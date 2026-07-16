#!/usr/bin/env python3
from __future__ import annotations

import os
import json
import stat
import sys
from pathlib import Path


def safe_component(value: str) -> str:
    if not value or value in {".", ".."} or Path(value).name != value or "/" in value or "\\" in value:
        raise RuntimeError("unsafe relative component")
    return value


def open_directory(name: str | os.PathLike[str], *, dir_fd: int | None = None) -> int:
    return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dir_fd)


def remove_tree(name: str, parent_fd: int) -> None:
    metadata = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise RuntimeError("owned cleanup target must be a real directory")
    descriptor = open_directory(name, dir_fd=parent_fd)
    try:
        held = os.fstat(descriptor)
        current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if (held.st_dev, held.st_ino) != (current.st_dev, current.st_ino):
            raise RuntimeError("owned cleanup target changed identity")
        for entry in os.listdir(descriptor):
            child = os.stat(entry, dir_fd=descriptor, follow_symlinks=False)
            if stat.S_ISDIR(child.st_mode) and not stat.S_ISLNK(child.st_mode):
                remove_tree(entry, descriptor)
            elif stat.S_ISREG(child.st_mode) or stat.S_ISLNK(child.st_mode):
                os.unlink(entry, dir_fd=descriptor)
            else:
                raise RuntimeError("owned cleanup contains a special path")
    finally:
        os.close(descriptor)
    os.rmdir(name, dir_fd=parent_fd)


def cleanup(root: str, run_id: str) -> None:
    root_fd = open_directory(os.path.abspath(root))
    try:
        try:
            work_fd = open_directory(".work", dir_fd=root_fd)
        except FileNotFoundError:
            return
        try:
            try:
                remove_tree(safe_component(run_id), work_fd)
            except FileNotFoundError:
                pass
            if not os.listdir(work_fd):
                os.rmdir(".work", dir_fd=root_fd)
        finally:
            os.close(work_fd)
    finally:
        os.close(root_fd)


def move_candidate(root: str, run_id: str, name: str) -> None:
    root_fd = open_directory(os.path.abspath(root))
    descriptors = [root_fd]
    try:
        work_fd = open_directory(".work", dir_fd=root_fd)
        descriptors.append(work_fd)
        run_fd = open_directory(safe_component(run_id), dir_fd=work_fd)
        descriptors.append(run_fd)
        candidate_fd = open_directory("candidate", dir_fd=run_fd)
        descriptors.append(candidate_fd)
        filename = safe_component(name)
        source = os.stat(filename, dir_fd=candidate_fd, follow_symlinks=False)
        if not stat.S_ISREG(source.st_mode):
            raise RuntimeError("candidate artifact must be a regular file")
        os.replace(filename, filename, src_dir_fd=candidate_fd, dst_dir_fd=root_fd)
        os.fsync(root_fd)
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def assert_held_child(parent_fd: int, name: str, held_fd: int) -> None:
    current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    held = os.fstat(held_fd)
    if not stat.S_ISDIR(current.st_mode) or (current.st_dev, current.st_ino) != (held.st_dev, held.st_ino):
        raise RuntimeError(f"held directory identity changed: {name}")


def open_run_directory(work_fd: int, run_id: str) -> int:
    return open_directory(safe_component(run_id), dir_fd=work_fd)


def copy_regular(source_name: str, source_fd: int, destination_name: str, destination_fd: int) -> None:
    source = os.stat(source_name, dir_fd=source_fd, follow_symlinks=False)
    if not stat.S_ISREG(source.st_mode) or source.st_size <= 0:
        raise RuntimeError("copy source must be a non-empty regular file")
    source_descriptor = os.open(source_name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=source_fd)
    try:
        destination_descriptor = os.open(
            destination_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=destination_fd,
        )
        try:
            while True:
                block = os.read(source_descriptor, 64 * 1024)
                if not block:
                    break
                view = memoryview(block)
                while view:
                    written = os.write(destination_descriptor, view)
                    view = view[written:]
            os.fsync(destination_descriptor)
        finally:
            os.close(destination_descriptor)
    finally:
        os.close(source_descriptor)


def unlink_regular_if_present(parent_fd: int, name: str) -> None:
    try:
        metadata = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if not stat.S_ISREG(metadata.st_mode):
        raise RuntimeError(f"managed root entry is not a regular file: {name}")
    os.unlink(name, dir_fd=parent_fd)


def held_command(command: str, run_id: str, rest: list[str]) -> None:
    root_fd = os.dup(3)
    work_fd = os.dup(4)
    history_fd = os.dup(5) if len(rest) > 0 and rest[0] == "with-history" else None
    if history_fd is not None:
        rest = rest[1:]
    try:
        assert_held_child(root_fd, ".work", work_fd)
        if history_fd is not None:
            assert_held_child(root_fd, "history", history_fd)
        if command == "acquire-lock" and not rest:
            os.mkdir(".delivery-lock", dir_fd=work_fd)
            os.fsync(work_fd)
        elif command == "prepare-rollback" and not rest:
            run_fd = open_run_directory(work_fd, run_id)
            try:
                os.mkdir("rollback", dir_fd=run_fd)
                os.fsync(run_fd)
            finally:
                os.close(run_fd)
        elif command == "snapshot" and len(rest) == 1:
            run_fd = open_run_directory(work_fd, run_id)
            rollback_fd = open_directory("rollback", dir_fd=run_fd)
            try:
                filename = safe_component(rest[0])
                copy_regular(filename, root_fd, filename, rollback_fd)
                os.fsync(rollback_fd)
            finally:
                os.close(rollback_fd)
                os.close(run_fd)
        elif command == "ensure-history" and not rest:
            try:
                os.mkdir("history", dir_fd=root_fd)
            except FileExistsError:
                metadata = os.stat("history", dir_fd=root_fd, follow_symlinks=False)
                if not stat.S_ISDIR(metadata.st_mode):
                    raise RuntimeError("history must be a real directory")
            os.fsync(root_fd)
        elif command == "reserve-history" and history_fd is not None and len(rest) == 1:
            os.mkdir(safe_component(rest[0]), dir_fd=history_fd)
            os.fsync(history_fd)
        elif command == "archive" and history_fd is not None and len(rest) == 2:
            sequence = safe_component(rest[0])
            filename = safe_component(rest[1])
            run_fd = open_run_directory(work_fd, run_id)
            rollback_fd = open_directory("rollback", dir_fd=run_fd)
            sequence_fd = open_directory(sequence, dir_fd=history_fd)
            try:
                copy_regular(filename, rollback_fd, filename, sequence_fd)
                os.fsync(sequence_fd)
            finally:
                os.close(sequence_fd)
                os.close(rollback_fd)
                os.close(run_fd)
        elif command == "move" and len(rest) == 1:
            filename = safe_component(rest[0])
            run_fd = open_run_directory(work_fd, run_id)
            candidate_fd = open_directory("candidate", dir_fd=run_fd)
            try:
                source = os.stat(filename, dir_fd=candidate_fd, follow_symlinks=False)
                if not stat.S_ISREG(source.st_mode):
                    raise RuntimeError("candidate artifact must be a regular file")
                os.replace(filename, filename, src_dir_fd=candidate_fd, dst_dir_fd=root_fd)
                os.fsync(root_fd)
            finally:
                os.close(candidate_fd)
                os.close(run_fd)
        elif command == "unlink-root" and len(rest) == 1:
            unlink_regular_if_present(root_fd, safe_component(rest[0]))
            os.fsync(root_fd)
        elif command == "rollback" and len(rest) == 3:
            expected_names = json.loads(rest[0])
            old_names = json.loads(rest[1])
            sequence = rest[2]
            for name in dict.fromkeys(expected_names + old_names):
                unlink_regular_if_present(root_fd, safe_component(name))
            run_fd = open_run_directory(work_fd, run_id)
            rollback_fd = open_directory("rollback", dir_fd=run_fd)
            try:
                for name in old_names:
                    filename = safe_component(name)
                    copy_regular(filename, rollback_fd, filename, root_fd)
            finally:
                os.close(rollback_fd)
                os.close(run_fd)
            if sequence:
                if history_fd is None:
                    raise RuntimeError("history descriptor required for rollback")
                remove_tree(safe_component(sequence), history_fd)
                os.fsync(history_fd)
            os.fsync(root_fd)
        elif command == "cleanup" and not rest:
            try:
                remove_tree(safe_component(run_id), work_fd)
            except FileNotFoundError:
                pass
            try:
                remove_tree(".delivery-lock", work_fd)
            except FileNotFoundError:
                pass
            if not os.listdir(work_fd):
                os.rmdir(".work", dir_fd=root_fd)
            else:
                os.fsync(work_fd)
            os.fsync(root_fd)
        else:
            raise RuntimeError("invalid held delivery-safe-fs command")
    finally:
        if history_fd is not None:
            os.close(history_fd)
        os.close(work_fd)
        os.close(root_fd)


def main() -> None:
    if len(sys.argv) < 4:
        raise SystemExit("usage: delivery-safe-fs.py cleanup ROOT RUN_ID | move ROOT RUN_ID NAME")
    command, root, run_id, *rest = sys.argv[1:]
    if command == "held":
        held_command(root, run_id, rest)
    elif command == "cleanup" and not rest:
        cleanup(root, run_id)
    elif command == "move" and len(rest) == 1:
        move_candidate(root, run_id, rest[0])
    else:
        raise SystemExit("invalid delivery-safe-fs command")


if __name__ == "__main__":
    main()
