"""Descriptor-bound Typst 0.15.0 executable snapshots."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import stat
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Sequence

from graduate_resume_cli import CliError


TYPST_RUNTIME_INVALID = "TYPST_RUNTIME_INVALID"
EXPECTED_TYPST_VERSION = "0.15.0"
MAX_SYMLINK_HOPS = 16
MAX_EXECUTABLE_BYTES = 128 * 1024 * 1024
COPY_CHUNK_BYTES = 1024 * 1024
MAX_RUN_OUTPUT_BYTES = 1024 * 1024
MAX_VERSION_OUTPUT_BYTES = 4096
_VERSION_RE = re.compile(r"typst 0\.15\.0(?: \([^\r\n]*\))?\Z")


def _runtime_error() -> CliError:
    return CliError(TYPST_RUNTIME_INVALID, "受控 Typst 0.15.0 运行时无效。")


def _lexical_absolute(path: Path) -> Path:
    value = os.path.abspath(os.fspath(path))
    return Path(os.path.normpath(value))


def _resolve_symlink_chain(candidate: Path) -> Path:
    pending = list(_lexical_absolute(candidate).parts[1:])
    current = Path("/")
    seen: set[tuple[int, int, tuple[str, ...]]] = set()
    hops = 0
    while pending:
        current = current / pending.pop(0)
        try:
            metadata = os.lstat(current)
        except OSError as exc:
            raise _runtime_error() from exc
        if not stat.S_ISLNK(metadata.st_mode):
            continue
        identity = (metadata.st_dev, metadata.st_ino, tuple(pending))
        if identity in seen or hops >= MAX_SYMLINK_HOPS:
            raise _runtime_error()
        seen.add(identity)
        hops += 1
        try:
            target = Path(os.readlink(current))
        except OSError as exc:
            raise _runtime_error() from exc
        replacement = target if target.is_absolute() else current.parent / target
        replacement = _lexical_absolute(replacement)
        pending = list(replacement.parts[1:]) + pending
        current = Path("/")
    return current


def _source_identity(metadata: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_size,
        metadata.st_mode,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _snapshot_identity_and_digest(path: Path) -> tuple[os.stat_result, str]:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or not 0 < metadata.st_size <= MAX_EXECUTABLE_BYTES:
            raise _runtime_error()
        digest = hashlib.sha256()
        while True:
            chunk = os.read(descriptor, COPY_CHUNK_BYTES)
            if not chunk:
                break
            digest.update(chunk)
        return metadata, digest.hexdigest()
    finally:
        os.close(descriptor)


@dataclass(frozen=True)
class TypstExecutable:
    snapshot_path: Path
    snapshot_dev: int
    snapshot_ino: int
    snapshot_size: int
    snapshot_mode: int
    snapshot_sha256: str
    version: str
    _snapshot_root: Path = field(repr=False, compare=False)
    _closed: bool = field(default=False, init=False, repr=False, compare=False)

    def __enter__(self) -> "TypstExecutable":
        if self._closed:
            raise _runtime_error()
        return self

    def run(
        self,
        arguments: Sequence[str],
        *,
        cwd: Path | str | None = None,
        text: bool = False,
        timeout: float = 60,
    ) -> subprocess.CompletedProcess:
        if self._closed or not isinstance(arguments, (tuple, list)) or any(not isinstance(item, str) for item in arguments):
            raise _runtime_error()
        try:
            metadata, digest = _snapshot_identity_and_digest(self.snapshot_path)
            if (
                (metadata.st_dev, metadata.st_ino, metadata.st_size, stat.S_IMODE(metadata.st_mode))
                != (self.snapshot_dev, self.snapshot_ino, self.snapshot_size, self.snapshot_mode)
                or digest != self.snapshot_sha256
            ):
                raise _runtime_error()
            completed = subprocess.run(
                [str(self.snapshot_path), *arguments],
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=text,
                check=False,
                timeout=timeout,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise _runtime_error() from exc
        stdout_size = len(completed.stdout.encode("utf-8") if isinstance(completed.stdout, str) else completed.stdout)
        stderr_size = len(completed.stderr.encode("utf-8") if isinstance(completed.stderr, str) else completed.stderr)
        if stdout_size > MAX_RUN_OUTPUT_BYTES or stderr_size > MAX_RUN_OUTPUT_BYTES:
            raise _runtime_error()
        return completed

    def close(self) -> None:
        if self._closed:
            return
        object.__setattr__(self, "_closed", True)
        try:
            self.snapshot_path.unlink(missing_ok=True)
            self._snapshot_root.rmdir()
        except OSError as exc:
            raise _runtime_error() from exc

    def __exit__(self, exc_type, exc, traceback) -> bool:
        self.close()
        return False


def resolve_typst_executable(
    candidate: Path | str | None = None,
    *,
    _after_source_verified: Callable[[], None] | None = None,
    _copy_chunk_hook: Callable[[int], None] | None = None,
) -> TypstExecutable:
    """Freeze one executable candidate and verify the snapshot reports Typst 0.15.0."""
    if candidate is None:
        discovered = shutil.which("typst")
        if discovered is None:
            raise _runtime_error()
        raw_candidate = Path(discovered)
    else:
        raw_candidate = Path(candidate)
    target = _resolve_symlink_chain(raw_candidate)
    source_descriptor = -1
    snapshot_descriptor = -1
    snapshot_root: Path | None = None
    try:
        source_descriptor = os.open(target, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        before = os.fstat(source_descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_mode & 0o111 == 0 or not 0 < before.st_size <= MAX_EXECUTABLE_BYTES:
            raise _runtime_error()
        snapshot_root = Path(tempfile.mkdtemp(prefix="graduate-resume-typst-"))
        snapshot_root.chmod(0o700)
        snapshot_path = snapshot_root / "typst"
        snapshot_descriptor = os.open(
            snapshot_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o500,
        )
        digest = hashlib.sha256()
        copied = 0
        while True:
            chunk = os.read(source_descriptor, COPY_CHUNK_BYTES)
            if not chunk:
                break
            copied += len(chunk)
            if copied > MAX_EXECUTABLE_BYTES:
                raise _runtime_error()
            digest.update(chunk)
            view = memoryview(chunk)
            while view:
                written = os.write(snapshot_descriptor, view)
                if written <= 0:
                    raise _runtime_error()
                view = view[written:]
            if _copy_chunk_hook is not None:
                _copy_chunk_hook(copied)
        after = os.fstat(source_descriptor)
        if _source_identity(before) != _source_identity(after) or copied != before.st_size:
            raise _runtime_error()
        os.fsync(snapshot_descriptor)
        snapshot_metadata = os.fstat(snapshot_descriptor)
        if snapshot_metadata.st_size != copied or stat.S_IMODE(snapshot_metadata.st_mode) != 0o500:
            raise _runtime_error()
        os.close(snapshot_descriptor)
        snapshot_descriptor = -1
        directory_descriptor = os.open(snapshot_root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
        if _after_source_verified is not None:
            _after_source_verified()
        executable = TypstExecutable(
            snapshot_path=snapshot_path,
            snapshot_dev=snapshot_metadata.st_dev,
            snapshot_ino=snapshot_metadata.st_ino,
            snapshot_size=snapshot_metadata.st_size,
            snapshot_mode=stat.S_IMODE(snapshot_metadata.st_mode),
            snapshot_sha256=digest.hexdigest(),
            version=EXPECTED_TYPST_VERSION,
            _snapshot_root=snapshot_root,
        )
        completed = executable.run(("--version",), text=True)
        version_output = completed.stdout
        if (
            completed.returncode != 0
            or len(version_output.encode("utf-8")) > MAX_VERSION_OUTPUT_BYTES
            or _VERSION_RE.fullmatch(version_output.rstrip("\n")) is None
            or version_output.count("\n") != 1
        ):
            executable.close()
            raise _runtime_error()
        return executable
    except CliError:
        if snapshot_root is not None:
            try:
                (snapshot_root / "typst").unlink(missing_ok=True)
                snapshot_root.rmdir()
            except OSError:
                pass
        raise
    except OSError as exc:
        if snapshot_root is not None:
            try:
                (snapshot_root / "typst").unlink(missing_ok=True)
                snapshot_root.rmdir()
            except OSError:
                pass
        raise _runtime_error() from exc
    finally:
        if snapshot_descriptor >= 0:
            os.close(snapshot_descriptor)
        if source_descriptor >= 0:
            os.close(source_descriptor)


__all__ = ["TypstExecutable", "resolve_typst_executable"]
