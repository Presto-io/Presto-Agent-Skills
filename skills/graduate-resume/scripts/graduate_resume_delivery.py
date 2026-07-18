from __future__ import annotations

import hashlib
import inspect
import json
import os
import secrets
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


TRIPLE_SUFFIXES = (".md", ".typ", ".pdf")
SUPPORT_DIRECTORIES = ("sources", "assets", "history", ".work")
PUBLICATION_MODES = ("patch", "authority")


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

    def __post_init__(self) -> None:
        if self.mode not in PUBLICATION_MODES:
            raise DeliveryError("publication mode must be patch or authority")
        if not self.safe_stems:
            raise DeliveryError("delivery requires at least one explicit safe stem")
        if len(set(self.safe_stems)) != len(self.safe_stems):
            raise DeliveryError("delivery contains a duplicate safe stem")
        if not self.theme_suffixes or len(set(self.theme_suffixes)) != len(self.theme_suffixes):
            raise DeliveryError("registered theme suffixes must be unique and non-empty")
        for theme in self.theme_suffixes:
            if not _safe_stem(theme) or "-" in theme:
                raise DeliveryError("registered theme suffix is unsafe")
        for stem in self.safe_stems:
            if not _safe_stem(stem):
                raise DeliveryError("delivery contains an unsafe stem")
            matching = tuple(theme for theme in self.theme_suffixes if stem.endswith(f"-{theme}"))
            embedded = tuple(theme for theme in self.theme_suffixes if f"-{theme}-" in stem)
            if len(matching) != 1 or embedded:
                raise DeliveryError(f"stem must have exactly one registered theme suffix: {stem}")

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
        self.root = Path(os.path.abspath(spec.delivery_root))
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
                        if stem not in self.spec.safe_stems:
                            raise DeliveryError(f"history contains an unknown stem: {stem}")
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

    def _close_fd(self, attribute: str) -> None:
        descriptor = getattr(self, attribute)
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
            setattr(self, attribute, None)

    def close(self) -> None:
        self._close_fd("candidate_fd")
        self._close_fd("rollback_fd")
        self._close_fd("evidence_fd")
        if self.run_fd is not None:
            for name in ("candidate", "rollback", "evidence"):
                try:
                    os.rmdir(name, dir_fd=self.run_fd)
                except OSError:
                    pass
        self._close_fd("run_fd")
        if self.work_fd is not None:
            try:
                os.rmdir(self.run_name, dir_fd=self.work_fd)
            except OSError:
                pass
            if self._lock_owned:
                try:
                    os.unlink(".lock", dir_fd=self.work_fd)
                except OSError:
                    pass
                self._lock_owned = False
        self._close_fd("work_fd")
        if self.root_fd is not None:
            try:
                os.rmdir(".work", dir_fd=self.root_fd)
            except OSError:
                pass
        self._close_fd("root_fd")

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()
