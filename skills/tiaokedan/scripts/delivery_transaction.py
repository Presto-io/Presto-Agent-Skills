from __future__ import annotations

import inspect
import os
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
MAX_PUBLIC_DIAGNOSTIC_BYTES = 4096


class DeliveryError(RuntimeError):
    pass


def _validate_output_path(path: Path, suffix: str, option: str) -> Path:
    raw = os.fspath(path)
    if not raw or "\x00" in raw or any(part == ".." for part in Path(raw).parts):
        raise DeliveryError(f"{option} contains an unsafe path component")
    candidate = Path(raw)
    if candidate.suffix != suffix:
        raise DeliveryError(f"{option} must end with {suffix}")
    stem = candidate.stem
    if not stem or stem in {".", ".."} or "/" in stem or "\\" in stem or Path(stem).name != stem:
        raise DeliveryError(f"{option} must use one safe filename stem")
    return Path(os.path.abspath(candidate))


@dataclass(frozen=True)
class DeliverySpec:
    delivery_root: Path
    stem: str
    current_names: tuple[str, ...]

    def __post_init__(self) -> None:
        expected = (f"{self.stem}.md", f"{self.stem}.typ")
        if self.current_names not in (expected, (*expected, f"{self.stem}.pdf")):
            raise DeliveryError("tiaokedan delivery must use the exact pair or optional-PDF triple")


def derive_delivery_spec(typ_path: Path, pdf_path: Path | None) -> DeliverySpec:
    typ = _validate_output_path(typ_path, ".typ", "--typ")
    names = (f"{typ.stem}.md", typ.name)
    if pdf_path is not None:
        pdf = _validate_output_path(pdf_path, ".pdf", "--pdf")
        if pdf.parent != typ.parent or pdf.stem != typ.stem:
            raise DeliveryError("--pdf must use the same delivery root and stem as --typ")
        names = (*names, pdf.name)
    return DeliverySpec(typ.parent, typ.stem, names)


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
        self._work_created = False
        self._history_sequence: str | None = None
        self._old_bytes: dict[str, bytes] = {}
        self._published: list[str] = []
        self._evidence_names: set[str] = set()

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
        if (not stat.S_ISDIR(current.st_mode)
                or (current.st_dev, current.st_ino) != self.root_identity
                or (held.st_dev, held.st_ino) != self.root_identity):
            raise DeliveryError("delivery root changed during publication")

    @staticmethod
    def _directory_entries(directory_fd: int) -> tuple[str, ...]:
        return tuple(sorted(entry.name for entry in os.scandir(directory_fd)))

    @staticmethod
    def _require_directory(name: str, *, directory_fd: int) -> None:
        metadata = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        if not stat.S_ISDIR(metadata.st_mode):
            raise DeliveryError(f"support entry must be a real directory: {name}")

    def _possible_current_names(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        pair = (f"{self.spec.stem}.md", f"{self.spec.stem}.typ")
        return pair, (*pair, f"{self.spec.stem}.pdf")

    def _discover_names(self, entries: tuple[str, ...]) -> tuple[str, ...]:
        pair, triple = self._possible_current_names()
        present = tuple(name for name in triple if name in entries)
        if not present:
            return ()
        if present not in (pair, triple):
            raise DeliveryError("current delivery is a partial tiaokedan bundle")
        return present

    def _inspect_current(self, *, allow_owned_work: bool) -> tuple[str, ...]:
        assert self.root_fd is not None
        self._assert_root_identity()
        entries = self._directory_entries(self.root_fd)
        pair, triple = self._possible_current_names()
        allowed = set(triple) | set(SUPPORT_DIRECTORIES)
        unknown = [name for name in entries if name not in allowed]
        if unknown:
            raise DeliveryError(f"unknown delivery-root entry: {unknown[0]}")
        current_names = self._discover_names(entries)
        for name in current_names:
            metadata = os.stat(name, dir_fd=self.root_fd, follow_symlinks=False)
            if not stat.S_ISREG(metadata.st_mode):
                raise DeliveryError(f"current artifact must be a regular file: {name}")
        for name in SUPPORT_DIRECTORIES:
            if name in entries:
                self._require_directory(name, directory_fd=self.root_fd)
        if ".work" in entries:
            work_fd = os.open(".work", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.root_fd)
            try:
                work_entries = self._directory_entries(work_fd)
                expected = {".lock", self.run_name} if allow_owned_work else set()
                if set(work_entries) != expected:
                    raise DeliveryError("stale or concurrent .work content requires audit")
            finally:
                os.close(work_fd)
        self._inspect_history(pair, triple)
        return current_names

    def _inspect_history(self, pair: tuple[str, ...], triple: tuple[str, ...]) -> None:
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
                    names = self._directory_entries(sequence_fd)
                    if names not in (tuple(sorted(pair)), tuple(sorted(triple))):
                        raise DeliveryError(f"history entry has an invalid managed set: {sequence}")
                    for name in names:
                        self._read_regular(name, directory_fd=sequence_fd)
                finally:
                    os.close(sequence_fd)
        finally:
            os.close(history_fd)

    def _open_work(self) -> None:
        assert self.root_fd is not None
        try:
            os.mkdir(".work", 0o700, dir_fd=self.root_fd)
            self._work_created = True
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
        if name not in self.spec.current_names:
            raise DeliveryError("candidate name is outside the explicit managed set")
        return self.run_root / "candidate" / name

    def evidence_path(self, name: str) -> Path:
        if not name or name in {".", ".."} or Path(name).name != name or "/" in name or "\\" in name:
            raise DeliveryError("invalid evidence filename")
        self._evidence_names.add(name)
        return self.run_root / "evidence" / name

    @staticmethod
    def _read_regular(name: str, *, directory_fd: int, require_nonempty: bool = True) -> bytes:
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd)
        try:
            metadata = os.fstat(descriptor)
            if not stat.S_ISREG(metadata.st_mode):
                raise DeliveryError(f"managed path is not a regular file: {name}")
            chunks: list[bytes] = []
            while chunk := os.read(descriptor, 1024 * 1024):
                chunks.append(chunk)
            payload = b"".join(chunks)
            if require_nonempty and not payload:
                raise DeliveryError(f"managed file is empty: {name}")
            return payload
        finally:
            os.close(descriptor)

    @staticmethod
    def _write_bytes(name: str, payload: bytes, *, directory_fd: int) -> None:
        descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory_fd)
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

    def _candidate_bytes(self) -> dict[str, bytes]:
        assert self.candidate_fd is not None
        if self._directory_entries(self.candidate_fd) != tuple(sorted(self.spec.current_names)):
            raise DeliveryError("candidate does not match the explicit managed set")
        return {name: self._read_regular(name, directory_fd=self.candidate_fd) for name in self.spec.current_names}

    def _current_bytes(self, names: tuple[str, ...]) -> dict[str, bytes]:
        assert self.root_fd is not None
        return {name: self._read_regular(name, directory_fd=self.root_fd) for name in names}

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
            return f"{max((int(name) for name in self._directory_entries(history_fd)), default=0) + 1:03d}"
        finally:
            os.close(history_fd)

    def _create_history(self) -> int:
        assert self.root_fd is not None
        try:
            os.mkdir("history", 0o700, dir_fd=self.root_fd)
        except FileExistsError:
            pass
        history_fd = os.open("history", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.root_fd)
        sequence = self._next_history_sequence()
        os.mkdir(sequence, 0o700, dir_fd=history_fd)
        self._history_sequence = sequence
        sequence_fd = os.open(sequence, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=history_fd)
        os.close(history_fd)
        return sequence_fd

    def _remove_history_sequence(self) -> None:
        if self._history_sequence is None or self.root_fd is None:
            return
        history_fd = -1
        try:
            history_fd = os.open("history", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.root_fd)
            sequence_fd = os.open(self._history_sequence, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=history_fd)
            try:
                for name in self._old_bytes:
                    try:
                        os.unlink(name, dir_fd=sequence_fd)
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

    def _rollback(self) -> None:
        if self.root_fd is None or self.rollback_fd is None:
            return
        possible = set().union(*map(set, self._possible_current_names()))
        for name in possible:
            try:
                os.unlink(name, dir_fd=self.root_fd)
            except FileNotFoundError:
                pass
        for name in self._old_bytes:
            os.replace(name, name, src_dir_fd=self.rollback_fd, dst_dir_fd=self.root_fd)
        self._remove_history_sequence()
        os.fsync(self.root_fd)
        restored_names = self._discover_names(self._directory_entries(self.root_fd))
        if self._current_bytes(restored_names) != self._old_bytes:
            raise DeliveryError("rollback verification failed")

    def publish(self, validator: Callable[[dict[str, bytes]], None] | None = None) -> str:
        assert self.root_fd is not None and self.candidate_fd is not None and self.rollback_fd is not None
        candidate = self._candidate_bytes()
        if validator is not None:
            validator(candidate)
        self._fault("after_candidate_validation")
        current_names = self._inspect_current(allow_owned_work=True)
        current = self._current_bytes(current_names)
        if current_names == self.spec.current_names and current == candidate:
            self._fault("before_work_cleanup")
            return "identical"
        self._old_bytes = current
        for name, payload in current.items():
            self._write_bytes(name, payload, directory_fd=self.rollback_fd)
        sequence_fd: int | None = None
        previous_handlers: dict[int, signal.Handlers] = {}

        def interrupt_handler(signum: int, _frame: object) -> None:
            raise DeliveryError(f"delivery interrupted by signal {signum}")

        try:
            for signum in (signal.SIGINT, signal.SIGTERM):
                previous_handlers[signum] = signal.signal(signum, interrupt_handler)
            if current:
                sequence_fd = self._create_history()
                self._fault("after_history_reservation")
                for name, payload in current.items():
                    self._write_bytes(name, payload, directory_fd=sequence_fd)
                os.fsync(sequence_fd)
                self._fault("after_archive_snapshot")
            for index, name in enumerate(self.spec.current_names, start=1):
                os.replace(name, name, src_dir_fd=self.candidate_fd, dst_dir_fd=self.root_fd)
                self._published.append(name)
                if index == 1:
                    self._fault("after_publish_file_1")
                if index == max(1, len(self.spec.current_names) // 2):
                    self._fault("after_publish_middle_file")
            for name in set(current_names) - set(self.spec.current_names):
                os.unlink(name, dir_fd=self.root_fd)
            os.fsync(self.root_fd)
            self._fault("before_post_publish_verify")
            observed_names = self._discover_names(self._directory_entries(self.root_fd))
            if observed_names != self.spec.current_names or self._current_bytes(observed_names) != candidate:
                raise DeliveryError("post-publish exact-set verification failed")
            self._fault("before_work_cleanup")
            return "changed" if current else "first"
        except BaseException:
            self._rollback()
            raise
        finally:
            if sequence_fd is not None:
                os.close(sequence_fd)
            for signum, handler in previous_handlers.items():
                signal.signal(signum, handler)

    def _close_fd(self, attribute: str) -> None:
        descriptor = getattr(self, attribute)
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
            setattr(self, attribute, None)

    def close(self) -> None:
        if self.candidate_fd is not None:
            for name in self.spec.current_names:
                try:
                    os.unlink(name, dir_fd=self.candidate_fd)
                except OSError:
                    pass
        if self.rollback_fd is not None:
            for name in self._old_bytes:
                try:
                    os.unlink(name, dir_fd=self.rollback_fd)
                except OSError:
                    pass
        if self.evidence_fd is not None:
            for name in self._evidence_names:
                try:
                    os.unlink(name, dir_fd=self.evidence_fd)
                except OSError:
                    pass
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
                work_fd = os.open(".work", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.root_fd)
            except OSError:
                work_fd = None
            if work_fd is not None:
                try:
                    if not self._directory_entries(work_fd):
                        os.rmdir(".work", dir_fd=self.root_fd)
                except OSError:
                    pass
                finally:
                    os.close(work_fd)
        self._close_fd("root_fd")

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()
