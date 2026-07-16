from __future__ import annotations

import os
import re
import secrets
import signal
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


SUPPORT_DIRECTORIES = ("sources", "assets", "history", ".work")
FAULT_NAMES = (
    "after_candidate_validation",
    "after_history_reservation",
    "after_archive_snapshot",
    "after_publish_file_1",
    "after_publish_middle_file",
    "before_post_publish_verify",
    "before_work_cleanup",
)
FAULT_ENV = "PRESTO_CLEAN_DELIVERY_FAULT"
MARKDOWN_ASSET_REFERENCE = re.compile(
    r"!?\[[^\]]*\]\((?:<)?(assets/[^\s)>]+)(?:>)?(?:\s+[^)]*)?\)"
)
HTML_ASSET_REFERENCE = re.compile(r"(?:src|href)=[\"'](assets/[^\"'#?]+)", re.IGNORECASE)
ONLINE_REFERENCE = re.compile(r"(?:src|href)=[\"'](?:https?:)?//", re.IGNORECASE)
REQUIRED_HTML_TOKENS = (
    "<!doctype html>",
    "<html",
    "<style>",
    "<script>",
    'class="app"',
    "page-source",
)


class DeliveryError(RuntimeError):
    pass


def _safe_relative_asset(value: str) -> str:
    path = Path(value)
    parts = path.parts
    if (
        not parts
        or parts[0] != "assets"
        or path.is_absolute()
        or any(part in {"", ".", ".."} or "\x00" in part or "/" in part or "\\" in part for part in parts)
    ):
        raise DeliveryError("asset references must be safe relative paths below assets/")
    return Path(*parts).as_posix()


def managed_asset_references(markdown: bytes, html: bytes = b"") -> tuple[str, ...]:
    try:
        markdown_text = markdown.decode("utf-8")
        html_text = html.decode("utf-8") if html else ""
    except UnicodeDecodeError as exc:
        raise DeliveryError("Markdown and HTML must be UTF-8") from exc
    values = [match.group(1) for match in MARKDOWN_ASSET_REFERENCE.finditer(markdown_text)]
    values.extend(match.group(1) for match in HTML_ASSET_REFERENCE.finditer(html_text))
    return tuple(sorted({_safe_relative_asset(value) for value in values}))


@dataclass(frozen=True)
class DeliverySpec:
    delivery_root: Path
    stem: str
    managed_assets: tuple[str, ...]
    seed_markdown: Path | None = None

    def __post_init__(self) -> None:
        if (
            not self.stem
            or self.stem in {".", ".."}
            or Path(self.stem).name != self.stem
            or "/" in self.stem
            or "\\" in self.stem
            or "\x00" in self.stem
        ):
            raise DeliveryError("delivery stem must be one safe filename component")
        normalized = tuple(sorted({_safe_relative_asset(name) for name in self.managed_assets}))
        if normalized != self.managed_assets:
            raise DeliveryError("managed assets must be sorted and unique")

    @property
    def pair_names(self) -> tuple[str, str]:
        return (f"{self.stem}.md", f"{self.stem}.html")

    @property
    def current_names(self) -> tuple[str, ...]:
        return (*self.pair_names, *self.managed_assets)


def validate_html_candidate(bundle: dict[str, bytes], max_size_mb: float) -> None:
    markdown_names = [name for name in bundle if name.endswith(".md") and "/" not in name]
    html_names = [name for name in bundle if name.endswith(".html") and "/" not in name]
    if len(markdown_names) != 1 or len(html_names) != 1:
        raise DeliveryError("candidate must contain one root Markdown and one root HTML")
    markdown = bundle[markdown_names[0]]
    html_payload = bundle[html_names[0]]
    if not markdown or not html_payload:
        raise DeliveryError("candidate Markdown and HTML must be non-empty")
    try:
        markdown.decode("utf-8")
        html_text = html_payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DeliveryError("candidate Markdown and HTML must be UTF-8") from exc
    if max_size_mb <= 0 or len(html_payload) > max_size_mb * 1024 * 1024:
        raise DeliveryError(f"HTML output exceeds {max_size_mb:g} MB")
    lowered = html_text.lower()
    missing = [token for token in REQUIRED_HTML_TOKENS if token.lower() not in lowered]
    if missing:
        raise DeliveryError(f"HTML candidate is missing required DOM token: {missing[0]}")
    if ONLINE_REFERENCE.search(html_text):
        raise DeliveryError("HTML candidate contains an online src/href reference")
    references = managed_asset_references(markdown, html_payload)
    asset_names = tuple(sorted(name for name in bundle if name.startswith("assets/")))
    if references != asset_names:
        raise DeliveryError("candidate referenced assets do not match the explicit managed asset set")
    for name in asset_names:
        if not bundle[name]:
            raise DeliveryError(f"managed asset is empty: {name}")


class DeliverySession:
    def __init__(self, spec: DeliverySpec) -> None:
        self.spec = spec
        self.root = Path(os.path.abspath(spec.delivery_root))
        self.run_name = f"run-{secrets.token_hex(8)}"
        self.run_root = self.root / ".work" / self.run_name
        self.candidate_root = self.run_root / "candidate"
        self.rollback_root = self.run_root / "rollback"
        self.evidence_root = self.run_root / "evidence"
        self.root_fd: int | None = None
        self.root_identity: tuple[int, int] | None = None
        self.work_fd: int | None = None
        self._lock_owned = False
        self._history_sequence: str | None = None
        self._published: list[str] = []
        self._old_bytes: dict[str, bytes] = {}
        self._initial_state = "none"

    def __enter__(self) -> DeliverySession:
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            metadata = os.stat(self.root, follow_symlinks=False)
            if not stat.S_ISDIR(metadata.st_mode):
                raise DeliveryError("delivery root must be a real directory")
            self.root_fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            held = os.fstat(self.root_fd)
            self.root_identity = (held.st_dev, held.st_ino)
            self._assert_root_identity()
            self._initial_state = self._inspect_root(allow_owned_work=False)
            self._open_work()
            self._create_run_tree()
            return self
        except BaseException:
            self.close()
            raise

    def _assert_root_identity(self) -> None:
        if self.root_fd is None or self.root_identity is None:
            raise DeliveryError("delivery root is not held open")
        current = os.stat(self.root, follow_symlinks=False)
        held = os.fstat(self.root_fd)
        if (
            not stat.S_ISDIR(current.st_mode)
            or (current.st_dev, current.st_ino) != self.root_identity
            or (held.st_dev, held.st_ino) != self.root_identity
        ):
            raise DeliveryError("delivery root changed during publication")

    @staticmethod
    def _entries(path: Path) -> tuple[str, ...]:
        return tuple(sorted(entry.name for entry in os.scandir(path)))

    @staticmethod
    def _require_real_directory(path: Path) -> None:
        metadata = os.stat(path, follow_symlinks=False)
        if not stat.S_ISDIR(metadata.st_mode):
            raise DeliveryError(f"support entry must be a real directory: {path.name}")

    @staticmethod
    def _read_regular(path: Path, *, nonempty: bool = True) -> bytes:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            metadata = os.fstat(descriptor)
            if not stat.S_ISREG(metadata.st_mode):
                raise DeliveryError(f"managed path must be a regular file: {path.name}")
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            payload = b"".join(chunks)
            if nonempty and not payload:
                raise DeliveryError(f"managed file is empty: {path.name}")
            return payload
        finally:
            os.close(descriptor)

    @staticmethod
    def _write_exclusive(path: Path, payload: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try:
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:
                    raise OSError("short write")
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def _seed_allowed(self, markdown_path: Path) -> bool:
        if self.spec.seed_markdown is None:
            return False
        try:
            return os.path.samefile(markdown_path, self.spec.seed_markdown)
        except OSError:
            return False

    def _current_asset_names(self, markdown_path: Path) -> tuple[str, ...]:
        return managed_asset_references(self._read_regular(markdown_path))

    def _inspect_assets(self, expected: tuple[str, ...]) -> None:
        asset_root = self.root / "assets"
        if not asset_root.exists() and not asset_root.is_symlink():
            if expected:
                raise DeliveryError("current delivery is missing referenced assets")
            return
        self._require_real_directory(asset_root)
        actual: list[str] = []
        for path in asset_root.rglob("*"):
            metadata = os.stat(path, follow_symlinks=False)
            if stat.S_ISDIR(metadata.st_mode):
                continue
            if not stat.S_ISREG(metadata.st_mode):
                raise DeliveryError("assets contains a symlink or non-regular entry")
            actual.append(path.relative_to(self.root).as_posix())
        if tuple(sorted(actual)) != expected:
            raise DeliveryError("assets contains missing or unreferenced content; confirmation cleanup is required")

    def _inspect_history(self) -> None:
        history = self.root / "history"
        if not history.exists() and not history.is_symlink():
            return
        self._require_real_directory(history)
        for entry in history.iterdir():
            metadata = os.stat(entry, follow_symlinks=False)
            if not re.fullmatch(r"[0-9]{3,}", entry.name) or not stat.S_ISDIR(metadata.st_mode):
                raise DeliveryError(f"invalid history entry: {entry.name}")

    def _inspect_root(self, *, allow_owned_work: bool) -> str:
        self._assert_root_identity()
        entries = self._entries(self.root)
        allowed = set(self.spec.pair_names) | set(SUPPORT_DIRECTORIES)
        unknown = [name for name in entries if name not in allowed]
        if unknown:
            raise DeliveryError(f"unknown delivery-root entry: {unknown[0]}; run confirmation cleanup")
        for name in SUPPORT_DIRECTORIES:
            if name in entries:
                self._require_real_directory(self.root / name)
        markdown_name, html_name = self.spec.pair_names
        markdown_present = markdown_name in entries
        html_present = html_name in entries
        state = "none"
        if markdown_present and html_present:
            self._read_regular(self.root / markdown_name)
            self._read_regular(self.root / html_name)
            state = "complete"
        elif markdown_present and not html_present and self._seed_allowed(self.root / markdown_name):
            self._read_regular(self.root / markdown_name)
            state = "seed"
        elif markdown_present or html_present:
            raise DeliveryError("current delivery is a partial Markdown/HTML pair")
        expected_assets = self._current_asset_names(self.root / markdown_name) if markdown_present else ()
        self._inspect_assets(expected_assets)
        if ".work" in entries:
            work_entries = set(self._entries(self.root / ".work"))
            expected_work = {".lock", self.run_name} if allow_owned_work else set()
            if work_entries != expected_work:
                raise DeliveryError("stale or concurrent .work content requires audit")
        self._inspect_history()
        return state

    def _open_work(self) -> None:
        assert self.root_fd is not None
        try:
            os.mkdir(".work", 0o700, dir_fd=self.root_fd)
        except FileExistsError:
            pass
        self.work_fd = os.open(".work", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.root_fd)
        try:
            lock_fd = os.open(
                ".lock",
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o600,
                dir_fd=self.work_fd,
            )
        except FileExistsError as exc:
            raise DeliveryError("another delivery session holds the lock") from exc
        os.close(lock_fd)
        self._lock_owned = True

    def _create_run_tree(self) -> None:
        assert self.work_fd is not None
        os.mkdir(self.run_name, 0o700, dir_fd=self.work_fd)
        self.candidate_root.mkdir()
        self.rollback_root.mkdir()
        self.evidence_root.mkdir()

    def candidate_path(self, name: str) -> Path:
        if name not in self.spec.current_names:
            raise DeliveryError("candidate name is outside the explicit managed set")
        return self.candidate_root / name

    def evidence_path(self, name: str) -> Path:
        if not name or name in {".", ".."} or Path(name).name != name or "/" in name or "\\" in name:
            raise DeliveryError("invalid evidence filename")
        return self.evidence_root / name

    def stage_candidate(self, markdown: bytes, html: bytes, *, asset_root: Path) -> None:
        references = managed_asset_references(markdown, html)
        if references != self.spec.managed_assets:
            raise DeliveryError("candidate references do not match the explicit managed asset set")
        markdown_name, html_name = self.spec.pair_names
        self._write_exclusive(self.candidate_root / markdown_name, markdown)
        self._write_exclusive(self.candidate_root / html_name, html)
        for name in self.spec.managed_assets:
            try:
                payload = self._read_regular(asset_root / name)
            except OSError as exc:
                raise DeliveryError(f"required managed asset is missing or unreadable: {name}") from exc
            self._write_exclusive(self.candidate_root / name, payload)

    def _bundle_bytes(self, root: Path, names: tuple[str, ...]) -> dict[str, bytes]:
        return {name: self._read_regular(root / name) for name in names}

    def _candidate_bytes(self) -> dict[str, bytes]:
        actual = tuple(sorted(
            path.relative_to(self.candidate_root).as_posix()
            for path in self.candidate_root.rglob("*")
            if path.is_file() and not path.is_symlink()
        ))
        if actual != tuple(sorted(self.spec.current_names)):
            raise DeliveryError("candidate path set does not match the explicit managed set")
        return self._bundle_bytes(self.candidate_root, self.spec.current_names)

    def _fault(self, name: str) -> None:
        if name not in FAULT_NAMES:
            raise DeliveryError(f"invalid fault point: {name}")
        if os.environ.get(FAULT_ENV) == name:
            raise DeliveryError(f"injected delivery fault: {name}")

    def _next_history(self) -> str:
        history = self.root / "history"
        values = [int(entry.name) for entry in history.iterdir()] if history.exists() else []
        return f"{max(values, default=0) + 1:03d}"

    @staticmethod
    def _remove_empty_parents(path: Path, stop: Path) -> None:
        parent = path.parent
        while parent != stop and parent != parent.parent:
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent

    def _remove_names(self, root: Path, names: tuple[str, ...]) -> None:
        for name in sorted(names, key=lambda value: value.count("/"), reverse=True):
            path = root / name
            try:
                path.unlink()
            except FileNotFoundError:
                continue
            self._remove_empty_parents(path, root)

    def _restore(self, old_names: tuple[str, ...]) -> None:
        mutation_names = tuple(sorted(set(self._published) | set(old_names)))
        self._remove_names(self.root, mutation_names)
        for name in old_names:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(self.rollback_root / name, target)
        if self._history_sequence is not None:
            sequence = self.root / "history" / self._history_sequence
            self._remove_names(sequence, old_names)
            try:
                sequence.rmdir()
            except FileNotFoundError:
                pass
            try:
                (self.root / "history").rmdir()
            except OSError:
                pass
            self._history_sequence = None
        if self._bundle_bytes(self.root, old_names) != self._old_bytes:
            raise DeliveryError("rollback verification failed")

    def publish(self, validator: Callable[[dict[str, bytes]], None] | None = None) -> str:
        candidate = self._candidate_bytes()
        if validator is not None:
            validator(candidate)
        self._fault("after_candidate_validation")
        state = self._inspect_root(allow_owned_work=True)
        markdown_name, html_name = self.spec.pair_names
        old_assets = self._current_asset_names(self.root / markdown_name) if state in {"seed", "complete"} else ()
        old_names = (
            (markdown_name, *old_assets)
            if state == "seed"
            else (markdown_name, html_name, *old_assets)
            if state == "complete"
            else ()
        )
        current = self._bundle_bytes(self.root, old_names)
        if state == "complete" and set(old_names) == set(self.spec.current_names) and current == candidate:
            self._fault("before_work_cleanup")
            return "identical"
        self._old_bytes = current
        for name, payload in current.items():
            self._write_exclusive(self.rollback_root / name, payload)
        previous_handlers: dict[int, signal.Handlers] = {}
        history_entry: Path | None = None

        def interrupt(signum: int, _frame: object) -> None:
            raise DeliveryError(f"delivery interrupted by signal {signum}")

        try:
            for signum in (signal.SIGINT, signal.SIGTERM):
                previous_handlers[signum] = signal.signal(signum, interrupt)
            if state == "complete":
                (self.root / "history").mkdir(exist_ok=True)
                self._history_sequence = self._next_history()
                history_entry = self.root / "history" / self._history_sequence
                history_entry.mkdir()
                self._fault("after_history_reservation")
                for name, payload in current.items():
                    self._write_exclusive(history_entry / name, payload)
                self._fault("after_archive_snapshot")
            mutation_names = tuple(dict.fromkeys((*self.spec.current_names, *old_names)))
            for index, name in enumerate(mutation_names, start=1):
                target = self.root / name
                if name in candidate:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(self.candidate_root / name, target)
                else:
                    target.unlink()
                    self._remove_empty_parents(target, self.root)
                self._published.append(name)
                if index == 1:
                    self._fault("after_publish_file_1")
                if index == max(1, len(mutation_names) // 2):
                    self._fault("after_publish_middle_file")
            assert self.root_fd is not None
            os.fsync(self.root_fd)
            self._fault("before_post_publish_verify")
            if self._bundle_bytes(self.root, self.spec.current_names) != candidate:
                raise DeliveryError("post-publish exact bundle verification failed")
            self._inspect_assets(self.spec.managed_assets)
            if history_entry is not None and self._bundle_bytes(history_entry, old_names) != current:
                raise DeliveryError("history exact bundle verification failed")
            self._fault("before_work_cleanup")
            return "changed" if state == "complete" else "first"
        except BaseException:
            self._restore(old_names)
            raise
        finally:
            for signum, handler in previous_handlers.items():
                signal.signal(signum, handler)

    @classmethod
    def _remove_owned_tree(cls, path: Path) -> None:
        try:
            metadata = os.stat(path, follow_symlinks=False)
        except FileNotFoundError:
            return
        if not stat.S_ISDIR(metadata.st_mode):
            path.unlink()
            return
        for entry in os.scandir(path):
            cls._remove_owned_tree(Path(entry.path))
        path.rmdir()

    def close(self) -> None:
        for path in (self.candidate_root, self.rollback_root, self.evidence_root):
            try:
                self._remove_owned_tree(path)
            except OSError:
                pass
        try:
            self.run_root.rmdir()
        except OSError:
            pass
        if self.work_fd is not None and self._lock_owned:
            try:
                os.unlink(".lock", dir_fd=self.work_fd)
            except OSError:
                pass
            self._lock_owned = False
        if self.work_fd is not None:
            os.close(self.work_fd)
            self.work_fd = None
        if self.root_fd is not None:
            try:
                os.rmdir(".work", dir_fd=self.root_fd)
            except OSError:
                pass
            os.close(self.root_fd)
            self.root_fd = None

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()
