from __future__ import annotations

import inspect
import os
import secrets
import signal
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


CURRENT_NAMES = (
    "end-of-term-full.md",
    "end-of-term-package.typ",
    "end-of-term-package.pdf",
    "score-list.xlsx",
)
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


class DeliveryError(RuntimeError):
    pass


@dataclass(frozen=True)
class DeliverySpec:
    delivery_root: Path
    current_names: tuple[str, ...] = CURRENT_NAMES

    def __post_init__(self) -> None:
        if self.current_names != CURRENT_NAMES:
            raise DeliveryError("end-of-term delivery must use the fixed four-file set")


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

    def _directory_entries(self, directory_fd: int) -> tuple[str, ...]:
        return tuple(sorted(entry.name for entry in os.scandir(directory_fd)))

    def _require_directory(self, name: str, *, directory_fd: int) -> None:
        metadata = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        if not stat.S_ISDIR(metadata.st_mode):
            raise DeliveryError(f"support entry must be a real directory: {name}")

    def _inspect_current(self, *, allow_owned_work: bool) -> bool:
        assert self.root_fd is not None
        self._assert_root_identity()
        entries = self._directory_entries(self.root_fd)
        allowed = set(CURRENT_NAMES) | set(SUPPORT_DIRECTORIES)
        unknown = [name for name in entries if name not in allowed]
        if unknown:
            raise DeliveryError(f"unknown delivery-root entry: {unknown[0]}")
        present: list[str] = []
        for name in CURRENT_NAMES:
            if name not in entries:
                continue
            metadata = os.stat(name, dir_fd=self.root_fd, follow_symlinks=False)
            if not stat.S_ISREG(metadata.st_mode):
                raise DeliveryError(f"current artifact must be a regular file: {name}")
            present.append(name)
        if present and tuple(present) != CURRENT_NAMES:
            raise DeliveryError("current delivery is a partial four-file bundle")
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
        self._inspect_history()
        return bool(present)

    def _inspect_history(self) -> None:
        assert self.root_fd is not None
        try:
            history_fd = os.open("history", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.root_fd)
        except FileNotFoundError:
            return
        try:
            for name in self._directory_entries(history_fd):
                if len(name) < 3 or not name.isdigit():
                    raise DeliveryError(f"invalid history entry: {name}")
                self._require_directory(name, directory_fd=history_fd)
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
            lock_fd = os.open(".lock", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                              0o600, dir_fd=self.work_fd)
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
        if name not in CURRENT_NAMES:
            raise DeliveryError("candidate name is outside the fixed managed set")
        return self.run_root / "candidate" / name

    def evidence_path(self, name: str) -> Path:
        if not name or name in {".", ".."} or Path(name).name != name or "/" in name or "\\" in name:
            raise DeliveryError("invalid evidence filename")
        return self.run_root / "evidence" / name

    def _read_regular(self, name: str, *, directory_fd: int, require_nonempty: bool = True) -> bytes:
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd)
        try:
            metadata = os.fstat(descriptor)
            if not stat.S_ISREG(metadata.st_mode):
                raise DeliveryError(f"managed path is not a regular file: {name}")
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            payload = b"".join(chunks)
            if require_nonempty and not payload:
                raise DeliveryError(f"managed file is empty: {name}")
            return payload
        finally:
            os.close(descriptor)

    def _write_bytes(self, name: str, payload: bytes, *, directory_fd: int) -> None:
        descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600, dir_fd=directory_fd)
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
        entries = self._directory_entries(self.candidate_fd)
        if entries != tuple(sorted(CURRENT_NAMES)):
            raise DeliveryError("candidate must contain exactly the fixed four-file set")
        return {name: self._read_regular(name, directory_fd=self.candidate_fd) for name in CURRENT_NAMES}

    def _current_bytes(self, exists: bool) -> dict[str, bytes]:
        assert self.root_fd is not None
        if not exists:
            return {}
        return {name: self._read_regular(name, directory_fd=self.root_fd) for name in CURRENT_NAMES}

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
            values = [int(name) for name in self._directory_entries(history_fd)]
            return f"{max(values, default=0) + 1:03d}"
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
        try:
            history_fd = os.open("history", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.root_fd)
        except FileNotFoundError:
            return
        try:
            sequence_fd = os.open(self._history_sequence, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                  dir_fd=history_fd)
            try:
                for name in CURRENT_NAMES:
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
        for name in CURRENT_NAMES:
            try:
                os.unlink(name, dir_fd=self.root_fd)
            except FileNotFoundError:
                pass
        if self._old_bytes:
            for name in CURRENT_NAMES:
                os.replace(name, name, src_dir_fd=self.rollback_fd, dst_dir_fd=self.root_fd)
        self._remove_history_sequence()
        os.fsync(self.root_fd)
        restored = self._current_bytes(bool(self._old_bytes))
        if restored != self._old_bytes:
            raise DeliveryError("rollback verification failed")

    def publish(self, validator: Callable[[dict[str, bytes]], None] | None = None) -> str:
        assert self.root_fd is not None and self.candidate_fd is not None and self.rollback_fd is not None
        candidate = self._candidate_bytes()
        if validator is not None:
            validator(candidate)
        self._fault("after_candidate_validation")
        current_exists = self._inspect_current(allow_owned_work=True)
        current = self._current_bytes(current_exists)
        if current == candidate:
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
            for index, name in enumerate(CURRENT_NAMES, start=1):
                os.replace(name, name, src_dir_fd=self.candidate_fd, dst_dir_fd=self.root_fd)
                if index == 1 and os.environ.get("PRESTO_CLEAN_DELIVERY_SIGNAL_BEFORE_RECORD"):
                    os.kill(os.getpid(), getattr(signal, os.environ["PRESTO_CLEAN_DELIVERY_SIGNAL_BEFORE_RECORD"]))
                self._published.append(name)
                if index == 1:
                    self._fault("after_publish_file_1")
                if index == len(CURRENT_NAMES) // 2:
                    self._fault("after_publish_middle_file")
            os.fsync(self.root_fd)
            self._fault("before_post_publish_verify")
            if self._current_bytes(True) != candidate:
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
            for name in CURRENT_NAMES:
                try:
                    os.unlink(name, dir_fd=self.candidate_fd)
                except FileNotFoundError:
                    pass
                except OSError:
                    pass
        if self.rollback_fd is not None:
            for name in CURRENT_NAMES:
                try:
                    os.unlink(name, dir_fd=self.rollback_fd)
                except FileNotFoundError:
                    pass
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
        if self.root_fd is not None and self._work_created:
            try:
                os.rmdir(".work", dir_fd=self.root_fd)
            except OSError:
                pass
        elif self.root_fd is not None:
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
