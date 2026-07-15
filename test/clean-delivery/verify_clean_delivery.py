#!/usr/bin/env python3
"""Foundation registry and fixture API for Phase 45 clean-delivery gates."""

from __future__ import annotations

import argparse
import hashlib
import os
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_DOC = REPOSITORY_ROOT / "docs" / "clean-delivery-directory-contract.md"
CLEANUP_DOC = REPOSITORY_ROOT / "docs" / "agent-output-cleanup-prompt.md"
FIXTURE_DOC = Path(__file__).resolve().parent / "fixtures" / "README.md"
MAX_PUBLIC_OUTPUT_BYTES = 8 * 1024

REQUIRED_GATE_NAMES = (
    "self_contained_installation_gate",
    "first_publish_gate",
    "changed_bundle_history_gate",
    "identical_noop_gate",
    "generation_failure_gate",
    "validation_failure_gate",
    "publish_rollback_gate",
    "history_sequence_gate",
    "unknown_and_symlink_gate",
    "work_cleanup_and_lock_gate",
    "assets_sources_history_reference_gate",
    "cleanup_audit_confirmation_gate",
    "documentation_runtime_contract_gate",
    "existing_renderer_regression_gate",
)

FAULT_NAMES = (
    "after_candidate_validation",
    "after_history_reservation",
    "after_archive_snapshot",
    "after_publish_file_1",
    "after_publish_middle_file",
    "before_post_publish_verify",
    "before_work_cleanup",
)

FAULT_BUNDLE_SIZES = {
    "after_candidate_validation": (2, 4),
    "after_history_reservation": (2, 4),
    "after_archive_snapshot": (2, 4),
    "after_publish_file_1": (2, 4),
    "after_publish_middle_file": (4,),
    "before_post_publish_verify": (2, 4),
    "before_work_cleanup": (2, 4),
}


class GateFailure(RuntimeError):
    """A bounded, expected self-test failure."""


@dataclass(frozen=True)
class SnapshotEntry:
    kind: str
    size: int
    sha256: str | None
    mode: int
    mtime_ns: int
    device: int
    inode: int
    symlink_target: str | None
    content: bytes | None


@dataclass(frozen=True)
class PublicCliResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class GateSpec:
    name: str
    runner: Callable[[Path], None]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise GateFailure(message)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_terms(path: Path, terms: Iterable[str]) -> None:
    source = read_text(path)
    missing = [term for term in terms if term not in source]
    require(not missing, f"{path.relative_to(REPOSITORY_ROOT)} missing terms: {missing}")


def tree_snapshot(root: Path) -> dict[str, SnapshotEntry]:
    """Capture a no-follow relative-path and byte snapshot of an explicit fixture root."""
    require(root.is_absolute(), "fixture root must be explicit and absolute")
    require(root.exists() and root.is_dir() and not root.is_symlink(), "fixture root must be a real directory")
    snapshot: dict[str, SnapshotEntry] = {}
    pending = [root]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in sorted(entries, key=lambda item: item.name):
                path = Path(entry.path)
                relative = path.relative_to(root).as_posix()
                metadata = entry.stat(follow_symlinks=False)
                common = {
                    "size": metadata.st_size,
                    "mode": metadata.st_mode,
                    "mtime_ns": metadata.st_mtime_ns,
                    "device": metadata.st_dev,
                    "inode": metadata.st_ino,
                }
                if stat.S_ISLNK(metadata.st_mode):
                    snapshot[relative] = SnapshotEntry(
                        kind="symlink", sha256=None, symlink_target=os.readlink(path), content=None, **common
                    )
                elif stat.S_ISDIR(metadata.st_mode):
                    snapshot[relative] = SnapshotEntry(
                        kind="directory", sha256=None, symlink_target=None, content=None, **common
                    )
                    pending.append(path)
                elif stat.S_ISREG(metadata.st_mode):
                    payload = path.read_bytes()
                    snapshot[relative] = SnapshotEntry(
                        kind="file",
                        sha256=hashlib.sha256(payload).hexdigest(),
                        symlink_target=None,
                        content=payload,
                        **common,
                    )
                else:
                    snapshot[relative] = SnapshotEntry(
                        kind="special", sha256=None, symlink_target=None, content=None, **common
                    )
    return dict(sorted(snapshot.items()))


def managed_bytes(snapshot: dict[str, SnapshotEntry]) -> dict[str, bytes]:
    return {
        relative: entry.content
        for relative, entry in snapshot.items()
        if entry.kind == "file" and entry.content is not None
    }


def run_public_cli(
    command: Sequence[str],
    *,
    expected_success: bool,
    cwd: Path | None = None,
    timeout: int = 30,
) -> PublicCliResult:
    """Invoke a real public CLI with bounded, traceback-free output."""
    require(bool(command), "public CLI command must not be empty")
    executable = Path(command[0])
    require(executable.is_file(), f"public CLI missing: {executable}")
    completed = subprocess.run(
        list(command),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    combined = completed.stdout + completed.stderr
    require(len(combined.encode("utf-8")) <= MAX_PUBLIC_OUTPUT_BYTES, "public CLI output is unbounded")
    require("Traceback" not in combined, "public CLI leaked traceback")
    if expected_success:
        require(completed.returncode == 0, f"public CLI failed: {tuple(command)}")
    else:
        require(completed.returncode != 0, f"public CLI produced false success: {tuple(command)}")
        lowered = combined.lower()
        require("校验通过" not in combined and "publish succeeded" not in lowered and "success" not in lowered,
                "failed public CLI printed false-success text")
    return PublicCliResult(tuple(command), completed.returncode, completed.stdout, completed.stderr)


def protocol_gate(_: Path) -> None:
    require_terms(PROTOCOL_DOC, (
        "DeliverySpec", "current_names", "managed_assets", "candidate", "rollback", "evidence",
        "same-root lock", "path-set+bytes", "max + 1", "unknown", "fail-closed", "owned",
        "^[0-9]{3,}$", "managed `assets/`", "`sources/`", "SIGKILL", "断电", "多文件原子发布",
        "find -delete", "broad glob",
    ))


def cleanup_contract_gate(_: Path) -> None:
    require_terms(CLEANUP_DOC, (
        "audit → confirm → execute", "lstat", "snapshot digest", "exact relative operations",
        "安全移动", "需确认归档", "需明确批准删除", "exact approved operations", "默认 --yes",
        "UNCONFIRMED_EXECUTION", "STALE_SNAPSHOT", "UNAUTHORIZED_ROOT", "SYMLINK_ESCAPE", "PLAN_MISMATCH",
        ".teaching-design-package/", ".tiaokedan/", "legacy `media/`", "零 mutation",
    ))
    require_terms(FIXTURE_DOC, (
        "unknown-user-file", "user-source", "referenced-asset", "symlink-escape", "stale-work",
        "changed-after-audit", "hash、inode", "零 mutation",
    ))


def registry_shape_gate(_: Path) -> None:
    require(tuple(GATE_REGISTRY) == REQUIRED_GATE_NAMES, "required/called gate registry mismatch")
    require(len(GATE_REGISTRY) == len(set(GATE_REGISTRY)), "gate registry contains duplicate names")
    require(tuple(FAULT_BUNDLE_SIZES) == FAULT_NAMES, "fault registry differs from the seven standard points")
    require(FAULT_BUNDLE_SIZES["after_publish_file_1"] == (2, 4), "file-1 fault lacks two/four bundle coverage")
    require(FAULT_BUNDLE_SIZES["after_publish_middle_file"] == (4,), "middle fault must target four-file bundles")


def snapshot_api_gate(work: Path) -> None:
    root = work / "snapshot-root"
    root.mkdir()
    (root / "two.md").write_bytes(b"markdown")
    (root / "two.pdf").write_bytes(b"%PDF-two")
    four = root / "four"
    four.mkdir()
    for index in range(4):
        (four / f"artifact-{index}").write_bytes(f"artifact-{index}".encode())
    outside = work / "outside.txt"
    outside.write_bytes(b"outside-sentinel")
    (root / "escape").symlink_to(outside)
    before = tree_snapshot(root)
    require(set(managed_bytes(before)) == {
        "four/artifact-0", "four/artifact-1", "four/artifact-2", "four/artifact-3", "two.md", "two.pdf"
    }, "snapshot path+bytes inventory changed")
    require(before["escape"].kind == "symlink" and before["escape"].content is None,
            "snapshot followed a symlink")
    require(outside.read_bytes() == b"outside-sentinel", "snapshot changed outside sentinel")


def public_cli_api_gate(_: Path) -> None:
    cli = REPOSITORY_ROOT / "skills" / "school-pptx" / "scripts" / "school-pptx.sh"
    result = run_public_cli((str(cli), "--help"), expected_success=True, cwd=REPOSITORY_ROOT)
    require("school-pptx" in result.stdout, "real public CLI help contract missing")


def production_isolation_gate(_: Path) -> None:
    needles = ("verify_clean_delivery", "test/clean-delivery", "test.clean-delivery")
    offenders: list[str] = []
    scripts_root = REPOSITORY_ROOT / "skills"
    for path in scripts_root.glob("*/scripts/**/*"):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if any(needle in source for needle in needles):
            offenders.append(path.relative_to(REPOSITORY_ROOT).as_posix())
    require(not offenders, f"production scripts import/call the repository harness: {offenders}")


def foundation_gate(_: Path) -> None:
    require(Path(tempfile.gettempdir()).is_absolute(), "TemporaryDirectory base must be absolute")


def build_gate_registry() -> dict[str, GateSpec]:
    runners = (
        foundation_gate,
        snapshot_api_gate,
        foundation_gate,
        foundation_gate,
        foundation_gate,
        foundation_gate,
        registry_shape_gate,
        foundation_gate,
        foundation_gate,
        foundation_gate,
        foundation_gate,
        cleanup_contract_gate,
        protocol_gate,
        public_cli_api_gate,
    )
    return {
        name: GateSpec(name, runner)
        for name, runner in zip(REQUIRED_GATE_NAMES, runners, strict=True)
    }


GATE_REGISTRY = build_gate_registry()


def validate_registry(registry: Sequence[GateSpec]) -> tuple[str, ...]:
    names = tuple(spec.name for spec in registry)
    require(names == REQUIRED_GATE_NAMES, f"required/called gate registry mismatch: {names}")
    require(len(names) == len(set(names)), "gate registry contains duplicate names")
    require(all(callable(spec.runner) for spec in registry), "gate registry contains non-callable runner")
    return names


def run_registry_self_test() -> None:
    specs = tuple(GATE_REGISTRY.values())
    validate_registry(specs)
    duplicate = (*specs[:-1], specs[0])
    try:
        validate_registry(duplicate)
    except GateFailure:
        pass
    else:
        raise GateFailure("duplicate gate mutation was accepted")
    called: list[str] = []
    with tempfile.TemporaryDirectory(prefix="clean-delivery-registry-") as temporary:
        root = Path(temporary)
        for spec in specs:
            gate_root = root / spec.name
            gate_root.mkdir()
            spec.runner(gate_root)
            called.append(spec.name)
    require(tuple(called) == REQUIRED_GATE_NAMES, "required/called gate registry execution mismatch")
    production_isolation_gate(root)


def run_self_test(name: str) -> None:
    with tempfile.TemporaryDirectory(prefix=f"clean-delivery-{name}-") as temporary:
        root = Path(temporary)
        if name == "protocol":
            protocol_gate(root)
        elif name == "cleanup-contract":
            cleanup_contract_gate(root)
        elif name == "registry":
            run_registry_self_test()
        elif name == "all":
            protocol_gate(root)
            cleanup_contract_gate(root)
            registry_shape_gate(root)
            snapshot_api_gate(root)
            public_cli_api_gate(root)
            production_isolation_gate(root)
            run_registry_self_test()
        else:
            raise GateFailure(f"unknown self-test: {name}")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="verify_clean_delivery.py")
    parser.add_argument("--self-test", required=True, choices=("protocol", "cleanup-contract", "registry", "all"))
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    try:
        run_self_test(args.self_test)
        print(f"PASS clean-delivery self-test: {args.self_test}")
        return 0
    except (GateFailure, OSError, subprocess.SubprocessError, UnicodeError) as exc:
        print(f"FAIL clean-delivery self-test {args.self_test}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
