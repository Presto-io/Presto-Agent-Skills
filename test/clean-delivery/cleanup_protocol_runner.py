#!/usr/bin/env python3
"""Test-only executable for the snapshot-bound cleanup approval protocol."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Sequence


@dataclass(frozen=True)
class SnapshotRecord:
    path: str
    kind: str
    size: int
    mtime_ns: int
    device: int
    inode: int
    sha256: str | None
    symlink_target: str | None


@dataclass(frozen=True)
class Operation:
    action: str
    source: str
    destination: str | None
    reason: str


@dataclass(frozen=True)
class Audit:
    root: str
    records: tuple[SnapshotRecord, ...]
    snapshot_digest: str
    operations: tuple[Operation, ...]
    plan_digest: str


@dataclass(frozen=True)
class ExecutionResult:
    code: str
    completed: tuple[Operation, ...] = ()


def _digest(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _real_root(root: Path) -> Path:
    absolute = root.absolute()
    metadata = absolute.lstat()
    if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
        raise ValueError("UNAUTHORIZED_ROOT")
    return absolute


def _relative_path(value: str) -> PurePosixPath:
    if not value or "\x00" in value or "\\" in value:
        raise ValueError("UNAUTHORIZED_ROOT")
    relative = PurePosixPath(value)
    if relative.is_absolute() or any(part in ("", ".", "..") for part in relative.parts):
        raise ValueError("UNAUTHORIZED_ROOT")
    return relative


def snapshot(root: Path) -> tuple[SnapshotRecord, ...]:
    root = _real_root(root)
    records: list[SnapshotRecord] = []
    pending = [root]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in sorted(entries, key=lambda item: item.name):
                path = Path(entry.path)
                metadata = entry.stat(follow_symlinks=False)
                relative = path.relative_to(root).as_posix()
                digest = None
                target = None
                if stat.S_ISLNK(metadata.st_mode):
                    kind = "symlink"
                    target = os.readlink(path)
                elif stat.S_ISDIR(metadata.st_mode):
                    kind = "directory"
                    pending.append(path)
                elif stat.S_ISREG(metadata.st_mode):
                    kind = "file"
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                else:
                    kind = "special"
                records.append(SnapshotRecord(
                    relative, kind, metadata.st_size, metadata.st_mtime_ns,
                    metadata.st_dev, metadata.st_ino, digest, target,
                ))
    return tuple(sorted(records, key=lambda item: item.path))


def _operation_payload(operations: Sequence[Operation]) -> list[dict[str, object]]:
    return [asdict(operation) for operation in operations]


def audit(root: Path, operations: Sequence[Operation]) -> Audit:
    root = _real_root(root)
    records = snapshot(root)
    operation_tuple = tuple(operations)
    for operation in operation_tuple:
        if operation.action not in ("move", "delete") or not operation.reason:
            raise ValueError("PLAN_MISMATCH")
        _relative_path(operation.source)
        if operation.action == "move":
            if operation.destination is None:
                raise ValueError("PLAN_MISMATCH")
            _relative_path(operation.destination)
        elif operation.destination is not None:
            raise ValueError("PLAN_MISMATCH")
    record_payload = [asdict(record) for record in records]
    return Audit(
        str(root), records, _digest(record_payload), operation_tuple,
        _digest(_operation_payload(operation_tuple)),
    )


def approval_token(report: Audit, approved: Sequence[Operation]) -> str:
    approved_tuple = tuple(approved)
    if any(operation not in report.operations for operation in approved_tuple):
        raise ValueError("PLAN_MISMATCH")
    return _digest({
        "snapshot_digest": report.snapshot_digest,
        "plan_digest": report.plan_digest,
        "approved": _operation_payload(approved_tuple),
    })


def _has_symlink_component(root: Path, relative: PurePosixPath, *, include_leaf: bool) -> bool:
    parts = relative.parts if include_leaf else relative.parts[:-1]
    current = root
    for part in parts:
        current = current / part
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(metadata.st_mode):
            return True
    return False


def execute(
    root: Path,
    report: Audit,
    approval: str | None,
    requested: Sequence[Operation],
) -> ExecutionResult:
    try:
        root = _real_root(root)
    except (OSError, ValueError):
        return ExecutionResult("UNAUTHORIZED_ROOT")
    requested_tuple = tuple(requested)
    if approval is None:
        return ExecutionResult("UNCONFIRMED_EXECUTION")
    if any(operation not in report.operations for operation in requested_tuple):
        return ExecutionResult("PLAN_MISMATCH")
    expected_approval = approval_token(report, requested_tuple)
    if approval != expected_approval:
        return ExecutionResult("PLAN_MISMATCH")
    if str(root) != report.root:
        return ExecutionResult("UNAUTHORIZED_ROOT")
    current = snapshot(root)
    if current != report.records or _digest([asdict(record) for record in current]) != report.snapshot_digest:
        return ExecutionResult("STALE_SNAPSHOT")

    prepared: list[tuple[Operation, Path, Path | None]] = []
    for operation in requested_tuple:
        try:
            source_relative = _relative_path(operation.source)
            destination_relative = (
                _relative_path(operation.destination) if operation.destination is not None else None
            )
        except ValueError:
            return ExecutionResult("UNAUTHORIZED_ROOT")
        source = root.joinpath(*source_relative.parts)
        if _has_symlink_component(root, source_relative, include_leaf=True):
            return ExecutionResult("SYMLINK_ESCAPE")
        try:
            source_metadata = source.lstat()
        except FileNotFoundError:
            return ExecutionResult("STALE_SNAPSHOT")
        if not stat.S_ISREG(source_metadata.st_mode):
            return ExecutionResult("PLAN_MISMATCH")
        destination = None
        if destination_relative is not None:
            if _has_symlink_component(root, destination_relative, include_leaf=False):
                return ExecutionResult("SYMLINK_ESCAPE")
            destination = root.joinpath(*destination_relative.parts)
            if destination.exists() or destination.is_symlink():
                return ExecutionResult("PLAN_MISMATCH")
            if not destination.parent.is_dir():
                return ExecutionResult("PLAN_MISMATCH")
        prepared.append((operation, source, destination))

    for operation, source, destination in prepared:
        if operation.action == "move" and destination is not None:
            os.replace(source, destination)
        else:
            source.unlink()
    return ExecutionResult("EXECUTED", requested_tuple)


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="cleanup-protocol-") as temporary:
        base = Path(temporary)
        root = base / "whole-folder-delivery"
        root.mkdir()
        (root / "current.md").write_text("![asset](assets/figure.png)\n", encoding="utf-8")
        (root / "current.pdf").write_bytes(b"%PDF-current")
        (root / "sources").mkdir()
        (root / "sources" / "original.md").write_text("source\n", encoding="utf-8")
        (root / "assets").mkdir()
        (root / "assets" / "figure.png").write_bytes(b"PNG")
        (root / "history" / "001").mkdir(parents=True)
        (root / "unknown-user-file.txt").write_text("private\n", encoding="utf-8")
        (root / "agent.log").write_text("evidence\n", encoding="utf-8")
        outside = base / "outside.txt"
        outside.write_text("sentinel\n", encoding="utf-8")
        (root / "escape").symlink_to(outside)

        move = Operation("move", "agent.log", "history/001/agent.log", "approved evidence archive")
        before_audit = snapshot(root)
        delete_unknown = Operation("delete", "unknown-user-file.txt", None, "unknown user file")
        delete_report = audit(root, (delete_unknown,))
        refusals = (
            (execute(root, delete_report, None, (delete_unknown,)), "UNCONFIRMED_EXECUTION"),
            (execute(root, delete_report, approval_token(delete_report, ()), (delete_unknown,)), "PLAN_MISMATCH"),
            (execute(root, delete_report, "approval-mismatch", (delete_unknown,)), "PLAN_MISMATCH"),
        )
        for result, expected in refusals:
            if result.code != expected or snapshot(root) != before_audit:
                raise AssertionError(f"{expected} refusal was not zero mutation")

        link_move = Operation("move", "escape", "history/001/escape", "archive symlink")
        link_report = audit(root, (link_move,))
        link_result = execute(root, link_report, approval_token(link_report, (link_move,)), (link_move,))
        if link_result.code != "SYMLINK_ESCAPE" or snapshot(root) != before_audit:
            raise AssertionError("symlink escape refusal was not zero mutation")

        stale_report = audit(root, (move,))
        (root / "agent.log").write_text("changed-after-audit\n", encoding="utf-8")
        stale_before = snapshot(root)
        stale_result = execute(root, stale_report, approval_token(stale_report, (move,)), (move,))
        if stale_result.code != "STALE_SNAPSHOT" or snapshot(root) != stale_before:
            raise AssertionError("stale snapshot refusal was not zero mutation")

        report = audit(root, (move,))
        if snapshot(root) != before_audit:
            # The stale-fixture byte edit is deliberate; audit itself must preserve that state.
            if snapshot(root) != stale_before:
                raise AssertionError("audit mutated fixture")
        result = execute(root, report, approval_token(report, (move,)), (move,))
        if result.code != "EXECUTED" or not (root / "history" / "001" / "agent.log").is_file():
            raise AssertionError("approved exact operation did not execute")
        if outside.read_text(encoding="utf-8") != "sentinel\n":
            raise AssertionError("whole-folder fixture touched symlink target")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true", required=True)
    parser.parse_args()
    try:
        self_test()
    except (AssertionError, OSError, ValueError) as exc:
        print(f"FAIL cleanup-protocol: {exc}")
        return 1
    print("PASS cleanup-protocol audit-confirm-execute whole-folder fixture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
