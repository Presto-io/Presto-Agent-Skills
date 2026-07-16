#!/usr/bin/env python3
from __future__ import annotations

import os
import signal
import stat
import sys
import time


class DeliveryFailure(RuntimeError):
    pass


def open_dir(name: str, parent: int | None = None) -> int:
    return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)


def read_file(name: str, parent: int) -> bytes:
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size <= 0:
            raise DeliveryFailure(f"managed artifact is not a non-empty regular file: {name}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
    finally:
        os.close(descriptor)


def write_file(name: str, payload: bytes, parent: int) -> None:
    descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
    try:
        view = memoryview(payload)
        while view:
            count = os.write(descriptor, view)
            view = view[count:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def entries(parent: int) -> tuple[str, ...]:
    return tuple(sorted(os.listdir(parent)))


def remove_tree(name: str, parent: int) -> None:
    metadata = os.stat(name, dir_fd=parent, follow_symlinks=False)
    if stat.S_ISDIR(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode):
        descriptor = open_dir(name, parent)
        try:
            for child in entries(descriptor):
                remove_tree(child, descriptor)
        finally:
            os.close(descriptor)
        os.rmdir(name, dir_fd=parent)
    elif stat.S_ISREG(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
        os.unlink(name, dir_fd=parent)
    else:
        raise DeliveryFailure("owned tree contains a special path")


def cleanup(root: str, run_name: str) -> None:
    root_fd = open_dir(os.path.abspath(root))
    try:
        try:
            work_fd = open_dir(".work", root_fd)
        except FileNotFoundError:
            return
        try:
            try:
                remove_tree(run_name, work_fd)
            except FileNotFoundError:
                pass
            try:
                remove_tree("lock", work_fd)
            except FileNotFoundError:
                pass
            if not entries(work_fd):
                os.rmdir(".work", dir_fd=root_fd)
        finally:
            os.close(work_fd)
    finally:
        os.close(root_fd)


def fault(point: str) -> None:
    if os.environ.get("PRESTO_CLEAN_DELIVERY_SIGNAL") and point == "after_publish_file_1":
        signum = signal.SIGINT if os.environ["PRESTO_CLEAN_DELIVERY_SIGNAL"] == "INT" else signal.SIGTERM
        os.kill(os.getpid(), signum)
    if os.environ.get("PRESTO_CLEAN_DELIVERY_FAULT") == point:
        raise DeliveryFailure(f"injected delivery fault: {point}")


def publish(root: str, stem: str, run_name: str, candidate_count: int) -> str:
    possible = (f"{stem}.md", f"{stem}.typ", f"{stem}.pdf")
    candidate_names = possible[:candidate_count]
    root_fd = open_dir(os.path.abspath(root))
    descriptors = [root_fd]
    history_fd: int | None = None
    sequence_fd: int | None = None
    sequence = ""
    old_names: tuple[str, ...] = ()
    mutation_started = False
    try:
        work_fd = open_dir(".work", root_fd); descriptors.append(work_fd)
        run_fd = open_dir(run_name, work_fd); descriptors.append(run_fd)
        candidate_fd = open_dir("candidate", run_fd); descriptors.append(candidate_fd)
        rollback_fd = open_dir("rollback", run_fd); descriptors.append(rollback_fd)
        if entries(candidate_fd) != tuple(sorted(candidate_names)):
            raise DeliveryFailure("candidate exact set changed before publication")
        candidate = {name: read_file(name, candidate_fd) for name in candidate_names}
        fault("after_candidate_validation")
        ready_file = os.environ.get("GONGWEN_DELIVERY_READY_FILE")
        if ready_file:
            with open(ready_file, "x", encoding="utf-8") as handle:
                handle.write("candidate-validated")
            time.sleep(float(os.environ.get("GONGWEN_DELIVERY_PAUSE_SECONDS", "1")))
        present = tuple(name for name in possible if name in entries(root_fd))
        if present not in ((), possible[:1], possible[:2], possible):
            raise DeliveryFailure("current delivery is a partial gongwen bundle")
        old_names = present
        current = {name: read_file(name, root_fd) for name in old_names}
        if old_names == candidate_names and current == candidate:
            fault("before_work_cleanup")
            return "identical"
        for name, payload in current.items():
            write_file(name, payload, rollback_fd)
        if len(old_names) >= 2:
            try:
                os.mkdir("history", 0o700, dir_fd=root_fd)
            except FileExistsError:
                pass
            history_fd = open_dir("history", root_fd)
            values = [int(name) for name in entries(history_fd)]
            sequence = f"{max(values, default=0) + 1:03d}"
            os.mkdir(sequence, 0o700, dir_fd=history_fd)
            sequence_fd = open_dir(sequence, history_fd)
            fault("after_history_reservation")
            for name, payload in current.items():
                write_file(name, payload, sequence_fd)
            os.fsync(sequence_fd)
            fault("after_archive_snapshot")
        mutation_started = True
        for index, name in enumerate(candidate_names, start=1):
            os.replace(name, name, src_dir_fd=candidate_fd, dst_dir_fd=root_fd)
            if index == 1:
                fault("after_publish_file_1")
            if len(candidate_names) >= 3 and index == 2:
                fault("after_publish_middle_file")
        if len(old_names) == 3 and len(candidate_names) == 2:
            os.unlink(possible[2], dir_fd=root_fd)
        os.fsync(root_fd)
        fault("before_post_publish_verify")
        if {name: read_file(name, root_fd) for name in candidate_names} != candidate:
            raise DeliveryFailure("published bundle verification failed")
        fault("before_work_cleanup")
        return "changed" if len(old_names) >= 2 else "first"
    except BaseException:
        if mutation_started:
            for name in possible:
                try:
                    os.unlink(name, dir_fd=root_fd)
                except FileNotFoundError:
                    pass
            rollback_fd = descriptors[-1]
            for name in old_names:
                os.replace(name, name, src_dir_fd=rollback_fd, dst_dir_fd=root_fd)
        if sequence_fd is not None and history_fd is not None:
            for name in old_names:
                try:
                    os.unlink(name, dir_fd=sequence_fd)
                except FileNotFoundError:
                    pass
            os.close(sequence_fd); sequence_fd = None
            os.rmdir(sequence, dir_fd=history_fd)
        raise
    finally:
        if sequence_fd is not None:
            os.close(sequence_fd)
        if history_fd is not None:
            try:
                if not entries(history_fd):
                    os.rmdir("history", dir_fd=root_fd)
            except OSError:
                pass
            os.close(history_fd)
        try:
            for descriptor in reversed(descriptors[2:]):
                os.close(descriptor)
            work_fd = descriptors[1]
            try:
                remove_tree(run_name, work_fd)
            except FileNotFoundError:
                pass
            try:
                remove_tree("lock", work_fd)
            except FileNotFoundError:
                pass
            empty_work = not entries(work_fd)
            os.close(work_fd)
            if empty_work:
                os.rmdir(".work", dir_fd=root_fd)
        finally:
            os.close(root_fd)


def main() -> None:
    def interrupted(signum: int, _frame: object) -> None:
        raise DeliveryFailure(f"delivery interrupted by signal {signum}")

    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    command, root, run_name, *args = sys.argv[1:]
    if command == "cleanup" and not args:
        cleanup(root, run_name)
    elif command == "publish" and len(args) == 2:
        print(publish(root, args[0], run_name, int(args[1])))
    else:
        raise SystemExit("invalid gongwen safe delivery command")


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        print(f"gongwen delivery: {exc}", file=sys.stderr)
        raise
