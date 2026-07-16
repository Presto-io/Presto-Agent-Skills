#!/usr/bin/env python3
from __future__ import annotations

import os
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


def main() -> None:
    if len(sys.argv) < 4:
        raise SystemExit("usage: delivery-safe-fs.py cleanup ROOT RUN_ID | move ROOT RUN_ID NAME")
    command, root, run_id, *rest = sys.argv[1:]
    if command == "cleanup" and not rest:
        cleanup(root, run_id)
    elif command == "move" and len(rest) == 1:
        move_candidate(root, run_id, rest[0])
    else:
        raise SystemExit("invalid delivery-safe-fs command")


if __name__ == "__main__":
    main()
