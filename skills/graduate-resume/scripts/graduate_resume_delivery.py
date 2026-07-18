from __future__ import annotations

import hashlib
import inspect
import json
import os
import secrets
import signal
import stat
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


TRIPLE_SUFFIXES = (".md", ".typ", ".pdf")
SUPPORT_DIRECTORIES = ("history", ".work")
PUBLICATION_MODES = ("patch", "authority")
_HISTORY_STEM_RE = re.compile(r"[\w\u3400-\u9fff-]+", re.UNICODE)
_HEX64_RE = re.compile(r"[0-9a-f]{64}")
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


class DeliveryError(RuntimeError):
    pass


def _safe_stem(stem: str) -> bool:
    return (
        bool(stem)
        and stem not in {".", ".."}
        and Path(stem).name == stem
        and "/" not in stem
        and "\\" not in stem
        and "\x00" not in stem
        and not stem.startswith(".")
        and len(stem.encode("utf-8")) <= 180
    )


def _triple_names(stem: str) -> tuple[str, str, str]:
    return tuple(f"{stem}{suffix}" for suffix in TRIPLE_SUFFIXES)  # type: ignore[return-value]


def _safe_owner_prefix(owner_prefix: str) -> bool:
    if not isinstance(owner_prefix, str) or unicodedata.normalize("NFKC", owner_prefix) != owner_prefix:
        return False
    if not owner_prefix.endswith("简历-") or len(owner_prefix.encode("utf-8")) > 96:
        return False
    owner = owner_prefix[: -len("简历-")]
    return bool(owner and _HISTORY_STEM_RE.fullmatch(owner))


def _safe_history_stem(stem: str, owner_prefix: str, theme_suffixes: tuple[str, ...]) -> bool:
    if (
        not _safe_owner_prefix(owner_prefix)
        or not isinstance(stem, str)
        or unicodedata.normalize("NFKC", stem) != stem
        or not _safe_stem(stem)
        or not _HISTORY_STEM_RE.fullmatch(stem)
        or not stem.startswith(owner_prefix)
    ):
        return False
    matching = tuple(theme for theme in theme_suffixes if stem.endswith(f"-{theme}"))
    embedded = tuple(theme for theme in theme_suffixes if f"-{theme}-" in stem)
    if len(matching) != 1 or embedded:
        return False
    body = stem[len(owner_prefix): -(len(matching[0]) + 1)]
    if body == "通用":
        return True
    components = body.split("-")
    return len(components) >= 2 and all(components)


def _validate_bundle_map(
    bundles: Mapping[str, Mapping[str, bytes]],
    *,
    label: str,
) -> dict[str, dict[str, bytes]]:
    validated: dict[str, dict[str, bytes]] = {}
    for stem, files in bundles.items():
        if not _safe_stem(stem):
            raise DeliveryError(f"{label} contains an unsafe stem")
        expected = set(_triple_names(stem))
        if set(files) != expected:
            raise DeliveryError(f"{label} stem must be one complete triple: {stem}")
        payloads: dict[str, bytes] = {}
        for name in sorted(expected):
            payload = files[name]
            if not isinstance(payload, bytes) or not payload:
                raise DeliveryError(f"{label} managed file must be non-empty bytes: {name}")
            payloads[name] = payload
        validated[stem] = payloads
    return validated


@dataclass(frozen=True, slots=True)
class DeliverySpec:
    delivery_root: Path
    safe_stems: tuple[str, ...]
    theme_suffixes: tuple[str, ...]
    mode: str
    owner_prefix: str
    canonical_hash: str = "0" * 64
    evidence_root_path: str | None = None
    evidence_root_identity: tuple[int, int] | None = None

    def __post_init__(self) -> None:
        if self.mode not in PUBLICATION_MODES:
            raise DeliveryError("publication mode must be patch or authority")
        if not self.safe_stems:
            raise DeliveryError("delivery requires at least one explicit safe stem")
        if len(set(self.safe_stems)) != len(self.safe_stems):
            raise DeliveryError("delivery contains a duplicate safe stem")
        if not self.theme_suffixes or len(set(self.theme_suffixes)) != len(self.theme_suffixes):
            raise DeliveryError("registered theme suffixes must be unique and non-empty")
        if not _safe_owner_prefix(self.owner_prefix):
            raise DeliveryError("delivery owner prefix is unsafe")
        if not isinstance(self.canonical_hash, str) or not _HEX64_RE.fullmatch(self.canonical_hash):
            raise DeliveryError("canonical input hash must be lowercase sha256")
        if (self.evidence_root_path is None) != (self.evidence_root_identity is None):
            raise DeliveryError("evidence root authorization is incomplete")
        if self.evidence_root_path is not None:
            if not os.path.isabs(self.evidence_root_path) or not isinstance(self.evidence_root_identity, tuple) or len(self.evidence_root_identity) != 2:
                raise DeliveryError("evidence root authorization is invalid")
            if any(type(value) is not int or value < 0 for value in self.evidence_root_identity):
                raise DeliveryError("evidence root identity is invalid")
        for theme in self.theme_suffixes:
            if not _safe_stem(theme) or "-" in theme:
                raise DeliveryError("registered theme suffix is unsafe")
        for stem in self.safe_stems:
            if not _safe_history_stem(stem, self.owner_prefix, self.theme_suffixes):
                raise DeliveryError(f"stem must match owner prefix and one registered theme suffix: {stem}")

    @property
    def managed_names(self) -> tuple[str, ...]:
        return tuple(name for stem in self.safe_stems for name in _triple_names(stem))


@dataclass(frozen=True, slots=True)
class BundleDelta:
    unchanged: tuple[str, ...]
    added: tuple[str, ...]
    updated: tuple[str, ...]
    removed: tuple[str, ...]
    approval_digest: str

    @property
    def changed(self) -> tuple[str, ...]:
        return (*self.added, *self.updated, *self.removed)


def classify_bundle_delta(
    candidate: Mapping[str, Mapping[str, bytes]],
    current: Mapping[str, Mapping[str, bytes]],
    *,
    mode: str,
) -> BundleDelta:
    if mode not in PUBLICATION_MODES:
        raise DeliveryError("publication mode must be patch or authority")
    candidate_bundles = _validate_bundle_map(candidate, label="candidate")
    current_bundles = _validate_bundle_map(current, label="current")
    candidate_stems = set(candidate_bundles)
    current_stems = set(current_bundles)
    unchanged = tuple(sorted(
        stem for stem in candidate_stems & current_stems
        if candidate_bundles[stem] == current_bundles[stem]
    ))
    updated = tuple(sorted((candidate_stems & current_stems) - set(unchanged)))
    added = tuple(sorted(candidate_stems - current_stems))
    removed = tuple(sorted(current_stems - candidate_stems))
    if mode == "patch" and removed:
        raise DeliveryError("patch publication cannot remove current stems")
    snapshot = {
        "mode": mode,
        "unchanged": unchanged,
        "added": added,
        "updated": updated,
        "removed": removed,
        "current": {
            stem: {
                name: hashlib.sha256(payload).hexdigest()
                for name, payload in sorted(current_bundles[stem].items())
            }
            for stem in sorted(current_bundles)
        },
    }
    digest = hashlib.sha256(
        json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return BundleDelta(unchanged, added, updated, removed, digest)


def _secure_io_capabilities() -> tuple[str, ...]:
    missing: list[str] = []
    for constant in ("O_DIRECTORY", "O_NOFOLLOW"):
        if not hasattr(os, constant):
            missing.append(f"os.{constant}")
    for function in (os.open, os.stat, os.unlink, os.mkdir, os.rmdir):
        if function not in os.supports_dir_fd:
            missing.append(f"{function.__name__}(dir_fd)")
    parameters = inspect.signature(os.replace).parameters
    for parameter in ("src_dir_fd", "dst_dir_fd"):
        if parameter not in parameters:
            missing.append(f"os.replace({parameter})")
    return tuple(missing)


class DeliverySession:
    def __init__(self, spec: DeliverySpec) -> None:
        self.spec = spec
        requested_root = Path(os.path.abspath(spec.delivery_root))
        try:
            self.root = requested_root.parent.resolve(strict=True) / requested_root.name
        except OSError as exc:
            raise DeliveryError("delivery root parent must be an existing real directory") from exc
        self.root_fd: int | None = None
        self.root_identity: tuple[int, int] | None = None
        self.work_fd: int | None = None
        self.run_fd: int | None = None
        self.candidate_fd: int | None = None
        self.rollback_fd: int | None = None
        self.evidence_fd: int | None = None
        self.run_name = f"run-{secrets.token_hex(8)}"
        self.run_root = self.root / ".work" / self.run_name
        self._lock_owned = False
        self._preflight_delta: BundleDelta | None = None
        self._candidate: dict[str, dict[str, bytes]] = {}
        self._current: dict[str, dict[str, bytes]] = {}
        self._old_bytes: dict[str, bytes] = {}
        self._history_sequence: str | None = None
        self._history_stems: tuple[str, ...] = ()
        self._mutation_started = False
        self._closed = False

    def __enter__(self) -> DeliverySession:
        missing = _secure_io_capabilities()
        if missing:
            raise DeliveryError(f"secure delivery unavailable: {', '.join(missing)}")
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            root_status = os.stat(self.root, follow_symlinks=False)
            if not stat.S_ISDIR(root_status.st_mode):
                raise DeliveryError("delivery root must be a real directory")
            self.root_fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            held = os.fstat(self.root_fd)
            self.root_identity = (held.st_dev, held.st_ino)
            self._assert_root_identity()
            self._inspect_current(allow_owned_work=False)
            self._open_work()
            self._create_run_tree()
            return self
        except BaseException as original:
            try:
                self.close()
            except DeliveryError as cleanup_error:
                raise cleanup_error from original
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

    def _assert_evidence_identity(self) -> None:
        if self.spec.evidence_root_path is None:
            return
        try:
            current = os.stat(self.spec.evidence_root_path, follow_symlinks=False)
        except OSError as exc:
            raise DeliveryError("evidence root changed during publication") from exc
        if (
            not stat.S_ISDIR(current.st_mode)
            or (current.st_dev, current.st_ino) != self.spec.evidence_root_identity
        ):
            raise DeliveryError("evidence root changed during publication")

    @staticmethod
    def _directory_entries(directory_fd: int) -> tuple[str, ...]:
        return tuple(sorted(entry.name for entry in os.scandir(directory_fd)))

    @staticmethod
    def _require_directory(name: str, *, directory_fd: int) -> None:
        metadata = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        if not stat.S_ISDIR(metadata.st_mode):
            raise DeliveryError(f"support entry must be a real directory: {name}")

    @staticmethod
    def _read_regular(name: str, *, directory_fd: int) -> bytes:
        path_metadata = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        if not stat.S_ISREG(path_metadata.st_mode):
            raise DeliveryError(f"managed path is not a regular file: {name}")
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd)
        try:
            metadata = os.fstat(descriptor)
            if not stat.S_ISREG(metadata.st_mode):
                raise DeliveryError(f"managed path is not a regular file: {name}")
            chunks: list[bytes] = []
            while chunk := os.read(descriptor, 1024 * 1024):
                chunks.append(chunk)
            payload = b"".join(chunks)
            if not payload:
                raise DeliveryError(f"managed file is empty: {name}")
            return payload
        finally:
            os.close(descriptor)

    def _inspect_history(self) -> None:
        assert self.root_fd is not None
        try:
            history_fd = os.open("history", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.root_fd)
        except FileNotFoundError:
            return
        try:
            for sequence in self._directory_entries(history_fd):
                if len(sequence) < 3 or not sequence.isdigit():
                    raise DeliveryError(f"invalid history entry: {sequence}")
                self._require_directory(sequence, directory_fd=history_fd)
                sequence_fd = os.open(sequence, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=history_fd)
                try:
                    for stem in self._directory_entries(sequence_fd):
                        if not _safe_history_stem(stem, self.spec.owner_prefix, self.spec.theme_suffixes):
                            raise DeliveryError(f"history contains an unsafe stem: {stem}")
                        self._require_directory(stem, directory_fd=sequence_fd)
                        stem_fd = os.open(stem, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=sequence_fd)
                        try:
                            if self._directory_entries(stem_fd) != tuple(sorted(_triple_names(stem))):
                                raise DeliveryError(f"history stem is not a complete triple: {stem}")
                            for name in _triple_names(stem):
                                self._read_regular(name, directory_fd=stem_fd)
                        finally:
                            os.close(stem_fd)
                finally:
                    os.close(sequence_fd)
        finally:
            os.close(history_fd)

    def _inspect_current(self, *, allow_owned_work: bool) -> dict[str, dict[str, bytes]]:
        assert self.root_fd is not None
        self._assert_root_identity()
        entries = self._directory_entries(self.root_fd)
        allowed = set(self.spec.managed_names) | set(SUPPORT_DIRECTORIES)
        unknown = [name for name in entries if name not in allowed]
        if unknown:
            raise DeliveryError(f"unknown delivery-root entry: {unknown[0]}")
        current: dict[str, dict[str, bytes]] = {}
        entry_set = set(entries)
        for stem in self.spec.safe_stems:
            names = _triple_names(stem)
            present = tuple(name for name in names if name in entry_set)
            if present and present != names:
                raise DeliveryError(f"current delivery contains a partial triple: {stem}")
            if present:
                current[stem] = {name: self._read_regular(name, directory_fd=self.root_fd) for name in names}
        for name in SUPPORT_DIRECTORIES:
            if name in entry_set:
                self._require_directory(name, directory_fd=self.root_fd)
        if ".work" in entry_set:
            work_fd = os.open(".work", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.root_fd)
            try:
                expected = {".lock", self.run_name} if allow_owned_work else set()
                if set(self._directory_entries(work_fd)) != expected:
                    raise DeliveryError("stale or concurrent .work content requires audit")
            finally:
                os.close(work_fd)
        self._inspect_history()
        return current

    def _open_work(self) -> None:
        assert self.root_fd is not None
        try:
            os.mkdir(".work", 0o700, dir_fd=self.root_fd)
        except FileExistsError:
            pass
        self.work_fd = os.open(".work", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.root_fd)
        try:
            lock_fd = os.open(".lock", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=self.work_fd)
        except FileExistsError as exc:
            raise DeliveryError("another delivery session holds the lock") from exc
        else:
            os.close(lock_fd)
            self._lock_owned = True

    def _create_run_tree(self) -> None:
        assert self.work_fd is not None
        os.mkdir(self.run_name, 0o700, dir_fd=self.work_fd)
        self.run_fd = os.open(self.run_name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.work_fd)
        for name in ("candidate", "rollback", "evidence"):
            os.mkdir(name, 0o700, dir_fd=self.run_fd)
        self.candidate_fd = os.open("candidate", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.run_fd)
        self.rollback_fd = os.open("rollback", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.run_fd)
        self.evidence_fd = os.open("evidence", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.run_fd)

    def candidate_path(self, name: str) -> Path:
        if name not in self.spec.managed_names:
            raise DeliveryError("candidate name is outside the explicit managed registry")
        return self.run_root / "candidate" / name

    def _candidate_bytes(self) -> dict[str, dict[str, bytes]]:
        assert self.candidate_fd is not None
        entries = self._directory_entries(self.candidate_fd)
        unknown = [name for name in entries if name not in self.spec.managed_names]
        if unknown:
            raise DeliveryError(f"unknown candidate entry: {unknown[0]}")
        entry_set = set(entries)
        candidate: dict[str, dict[str, bytes]] = {}
        for stem in self.spec.safe_stems:
            names = _triple_names(stem)
            present = tuple(name for name in names if name in entry_set)
            if present and present != names:
                raise DeliveryError(f"candidate stem must be one complete triple: {stem}")
            if present:
                candidate[stem] = {name: self._read_regular(name, directory_fd=self.candidate_fd) for name in names}
        if not candidate:
            raise DeliveryError("candidate requires at least one complete triple")
        return candidate

    def approval_payload(
        self,
        delta: BundleDelta,
        candidate: Mapping[str, Mapping[str, bytes]],
        current: Mapping[str, Mapping[str, bytes]],
    ) -> dict[str, object]:
        if self.root_identity is None:
            raise DeliveryError("delivery root identity is unavailable")
        snapshot: dict[str, object] = {
            "schema": "graduate-resume-approval/v1",
            "mode": self.spec.mode,
            "unchanged": delta.unchanged,
            "added": delta.added,
            "updated": delta.updated,
            "removed": delta.removed,
            "candidate": {
                stem: {name: payload.hex() for name, payload in sorted(files.items())}
                for stem, files in sorted(candidate.items())
            },
            "current": {
                stem: {name: payload.hex() for name, payload in sorted(files.items())}
                for stem, files in sorted(current.items())
            },
            "canonical_input_hash": self.spec.canonical_hash,
            "delivery_root": {
                "path": os.fspath(self.root),
                "st_dev": self.root_identity[0],
                "st_ino": self.root_identity[1],
            },
        }
        if self.spec.evidence_root_path is not None and self.spec.evidence_root_identity is not None:
            snapshot["evidence_root"] = {
                "path": self.spec.evidence_root_path,
                "st_dev": self.spec.evidence_root_identity[0],
                "st_ino": self.spec.evidence_root_identity[1],
            }
        return snapshot

    @staticmethod
    def approval_digest(payload: Mapping[str, object]) -> str:
        return hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

    def preflight(self) -> BundleDelta:
        self._assert_evidence_identity()
        candidate = self._candidate_bytes()
        current = self._inspect_current(allow_owned_work=True)
        comparison_current = current if self.spec.mode == "authority" else {
            stem: current[stem] for stem in candidate if stem in current
        }
        delta = classify_bundle_delta(candidate, comparison_current, mode=self.spec.mode)
        approval_digest = self.approval_digest(self.approval_payload(delta, candidate, current))
        delta = BundleDelta(delta.unchanged, delta.added, delta.updated, delta.removed, approval_digest)
        self._candidate = candidate
        self._current = current
        self._preflight_delta = delta
        return delta

    @staticmethod
    def _write_bytes(name: str, payload: bytes, *, directory_fd: int) -> None:
        descriptor = os.open(
            name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=directory_fd,
        )
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

    def _fault(self, name: str) -> None:
        if name not in FAULT_NAMES:
            raise DeliveryError(f"invalid fault point: {name}")
        if os.environ.get(FAULT_ENV) == name:
            raise DeliveryError(f"injected delivery fault: {name}")

    def _next_history_sequence(self) -> str:
        assert self.root_fd is not None
        try:
            history_fd = os.open("history", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.root_fd)
        except FileNotFoundError:
            return "001"
        try:
            values: list[int] = []
            for name in self._directory_entries(history_fd):
                if len(name) < 3 or not name.isdigit():
                    raise DeliveryError(f"invalid history entry: {name}")
                values.append(int(name))
            return f"{max(values, default=0) + 1:03d}"
        finally:
            os.close(history_fd)

    def _create_history(self, stems: tuple[str, ...]) -> None:
        assert self.root_fd is not None
        try:
            os.mkdir("history", 0o700, dir_fd=self.root_fd)
        except FileExistsError:
            pass
        history_fd = os.open("history", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.root_fd)
        try:
            sequence = self._next_history_sequence()
            os.mkdir(sequence, 0o700, dir_fd=history_fd)
            self._history_sequence = sequence
            self._history_stems = stems
            sequence_fd = os.open(sequence, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=history_fd)
            try:
                for stem in stems:
                    os.mkdir(stem, 0o700, dir_fd=sequence_fd)
                    stem_fd = os.open(stem, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=sequence_fd)
                    try:
                        for name, payload in self._current[stem].items():
                            self._write_bytes(name, payload, directory_fd=stem_fd)
                        os.fsync(stem_fd)
                    finally:
                        os.close(stem_fd)
                os.fsync(sequence_fd)
            finally:
                os.close(sequence_fd)
        finally:
            os.close(history_fd)

    def _remove_history_sequence(self) -> None:
        if self.root_fd is None or self._history_sequence is None:
            return
        try:
            history_fd = os.open("history", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.root_fd)
        except FileNotFoundError:
            self._history_sequence = None
            return
        try:
            sequence_fd = os.open(
                self._history_sequence,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=history_fd,
            )
            try:
                for stem in self._history_stems:
                    try:
                        stem_fd = os.open(stem, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=sequence_fd)
                    except FileNotFoundError:
                        continue
                    try:
                        for name in _triple_names(stem):
                            try:
                                os.unlink(name, dir_fd=stem_fd)
                            except FileNotFoundError:
                                pass
                    finally:
                        os.close(stem_fd)
                    try:
                        os.rmdir(stem, dir_fd=sequence_fd)
                    except FileNotFoundError:
                        pass
            finally:
                os.close(sequence_fd)
            os.rmdir(self._history_sequence, dir_fd=history_fd)
            if not self._directory_entries(history_fd):
                os.close(history_fd)
                history_fd = -1
                os.rmdir("history", dir_fd=self.root_fd)
        except FileNotFoundError:
            pass
        finally:
            if history_fd >= 0:
                os.close(history_fd)
        self._history_sequence = None
        self._history_stems = ()

    def _flatten(self, bundles: Mapping[str, Mapping[str, bytes]]) -> dict[str, bytes]:
        return {name: payload for files in bundles.values() for name, payload in files.items()}

    def _rollback(self) -> None:
        if not self._mutation_started or self.root_fd is None or self.rollback_fd is None:
            return
        self._assert_root_identity()
        for name in self.spec.managed_names:
            try:
                os.unlink(name, dir_fd=self.root_fd)
            except FileNotFoundError:
                pass
        for name in self._old_bytes:
            os.replace(name, name, src_dir_fd=self.rollback_fd, dst_dir_fd=self.root_fd)
        self._remove_history_sequence()
        os.fsync(self.root_fd)
        restored = self._inspect_current(allow_owned_work=True)
        if self._flatten(restored) != self._old_bytes:
            raise DeliveryError("rollback verification failed")
        self._mutation_started = False

    def publish(self, *, approval_digest: str | None = None) -> str:
        assert self.root_fd is not None and self.candidate_fd is not None and self.rollback_fd is not None
        delta = self.preflight()
        if approval_digest != delta.approval_digest:
            raise DeliveryError("publication requires an unchanged approval digest")
        self._fault("after_candidate_validation")
        if not delta.changed:
            self._fault("before_work_cleanup")
            return "identical"
        self._old_bytes = self._flatten(self._current)
        for name, payload in self._old_bytes.items():
            self._write_bytes(name, payload, directory_fd=self.rollback_fd)
        previous_handlers: dict[int, signal.Handlers] = {}

        def interrupt_handler(signum: int, _frame: object) -> None:
            raise DeliveryError(f"delivery interrupted by signal {signum}")

        try:
            for signum in (signal.SIGINT, signal.SIGTERM):
                previous_handlers[signum] = signal.signal(signum, interrupt_handler)
            self._mutation_started = True
            archived_stems = tuple(sorted((*delta.updated, *delta.removed)))
            if archived_stems:
                self._create_history(archived_stems)
                self._fault("after_history_reservation")
                self._inspect_history()
                self._fault("after_archive_snapshot")
            mutation_names = tuple(
                name
                for stem in (*delta.updated, *delta.added, *delta.removed)
                for name in _triple_names(stem)
            )
            candidate_flat = self._flatten(self._candidate)
            for index, name in enumerate(mutation_names, start=1):
                if name in candidate_flat:
                    os.replace(name, name, src_dir_fd=self.candidate_fd, dst_dir_fd=self.root_fd)
                else:
                    os.unlink(name, dir_fd=self.root_fd)
                if index == 1:
                    self._fault("after_publish_file_1")
                if index == max(1, len(mutation_names) // 2):
                    self._fault("after_publish_middle_file")
            os.fsync(self.root_fd)
            self._fault("before_post_publish_verify")
            observed = self._inspect_current(allow_owned_work=True)
            expected = dict(self._current)
            if self.spec.mode == "authority":
                expected = dict(self._candidate)
            else:
                expected.update(self._candidate)
            if observed != expected:
                raise DeliveryError("post-publish exact-set verification failed")
            self._fault("before_work_cleanup")
            self._mutation_started = False
            return "changed" if self._current else "first"
        except BaseException:
            self._rollback()
            raise
        finally:
            for signum, handler in previous_handlers.items():
                signal.signal(signum, handler)

    @staticmethod
    def _record_cleanup_failure(
        failures: list[str],
        operation: str,
        owned_name: str,
        error: OSError,
    ) -> None:
        error_number = error.errno if isinstance(error.errno, int) else 0
        failures.append(f"{operation} {owned_name} errno={error_number}")

    def _close_fd(
        self,
        attribute: str,
        owned_name: str,
        failures: list[str],
    ) -> None:
        descriptor = getattr(self, attribute)
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError as error:
                self._record_cleanup_failure(failures, "close", owned_name, error)
            setattr(self, attribute, None)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        failures: list[str] = []
        if self.candidate_fd is not None:
            for name in self.spec.managed_names:
                try:
                    os.unlink(name, dir_fd=self.candidate_fd)
                except FileNotFoundError:
                    continue
                except OSError as error:
                    self._record_cleanup_failure(
                        failures,
                        "unlink",
                        f"candidate/{name}",
                        error,
                    )
        if self.rollback_fd is not None:
            for name in self._old_bytes:
                try:
                    os.unlink(name, dir_fd=self.rollback_fd)
                except FileNotFoundError:
                    continue
                except OSError as error:
                    self._record_cleanup_failure(
                        failures,
                        "unlink",
                        f"rollback/{name}",
                        error,
                    )
        self._close_fd("candidate_fd", "candidate", failures)
        self._close_fd("rollback_fd", "rollback", failures)
        self._close_fd("evidence_fd", "evidence", failures)
        if self.run_fd is not None:
            for name in ("candidate", "rollback", "evidence"):
                try:
                    os.rmdir(name, dir_fd=self.run_fd)
                except FileNotFoundError:
                    continue
                except OSError as error:
                    self._record_cleanup_failure(failures, "rmdir", name, error)
        self._close_fd("run_fd", "run", failures)
        if self.work_fd is not None:
            try:
                os.rmdir(self.run_name, dir_fd=self.work_fd)
            except FileNotFoundError:
                pass
            except OSError as error:
                self._record_cleanup_failure(failures, "rmdir", "run", error)
            if self._lock_owned:
                try:
                    os.unlink(".lock", dir_fd=self.work_fd)
                except FileNotFoundError:
                    pass
                except OSError as error:
                    self._record_cleanup_failure(failures, "unlink", ".lock", error)
                self._lock_owned = False
        self._close_fd("work_fd", ".work", failures)
        if self.root_fd is not None:
            try:
                os.rmdir(".work", dir_fd=self.root_fd)
            except FileNotFoundError:
                pass
            except OSError as error:
                self._record_cleanup_failure(failures, "rmdir", ".work", error)
        self._close_fd("root_fd", ".", failures)
        if failures:
            raise DeliveryError(f"cleanup failed: {'; '.join(failures)}")

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        try:
            self.close()
        except DeliveryError as cleanup_error:
            if isinstance(exc, BaseException):
                raise cleanup_error from exc
            raise
