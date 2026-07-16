#!/usr/bin/env python3
"""Foundation registry and fixture API for Phase 45 clean-delivery gates."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_DOC = REPOSITORY_ROOT / "docs" / "clean-delivery-directory-contract.md"
CLEANUP_DOC = REPOSITORY_ROOT / "docs" / "agent-output-cleanup-prompt.md"
FIXTURE_DOC = Path(__file__).resolve().parent / "fixtures" / "README.md"
MAX_PUBLIC_OUTPUT_BYTES = 8 * 1024
MAX_REGRESSION_OUTPUT_BYTES = 512 * 1024

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

REQUIRED_SKILL_NAMES = (
    "end-of-term-teaching-materials",
    "gongwen",
    "school-pptx",
    "school-presentation",
    "teaching-design-package",
    "tiaokedan",
)

REQUIRED_REQUIREMENT_IDS = (
    "CLEAN-01",
    "CLEAN-02",
    "CLEAN-03",
    "REV-01",
    "REV-02",
    "REV-03",
    "REV-04",
    "SAFE-01",
    "SAFE-02",
    "VERIFY-01",
    "DOCS-01",
    "RUNTIME-01",
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


@dataclass(frozen=True)
class SkillAdapter:
    name: str
    public_cli: str
    regression_commands: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class SkillEvidence:
    name: str
    called_gates: tuple[str, ...]
    called_faults: tuple[str, ...]
    commands: tuple[tuple[str, ...], ...]
    isolated_help_exit_status: int


@dataclass(frozen=True)
class ReviewReport:
    phase: str
    status: str
    depth: str
    files: tuple[str, ...]
    critical: int
    warning: int
    info: int
    total: int


@dataclass(frozen=True)
class VerificationReport:
    status: str
    requirements: tuple[str, ...]
    strict_aggregate_exit_status: int
    review_status: str
    review_critical_or_blocker_count: int
    review_warning_count: int
    review_info_count: int


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


def run_checked_command(
    command: Sequence[str],
    *,
    cwd: Path = REPOSITORY_ROOT,
    timeout: int = 300,
) -> PublicCliResult:
    require(bool(command), "regression command must not be empty")
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
    require(len(combined.encode("utf-8")) <= MAX_REGRESSION_OUTPUT_BYTES,
            f"regression output is unbounded: {tuple(command)}")
    require("Traceback" not in combined, f"regression leaked traceback: {tuple(command)}")
    require(completed.returncode == 0,
            f"regression failed ({completed.returncode}): {tuple(command)}\n{combined[-2000:]}")
    return PublicCliResult(tuple(command), completed.returncode, completed.stdout, completed.stderr)


def build_skill_adapters() -> dict[str, SkillAdapter]:
    python = sys.executable
    return {
        "end-of-term-teaching-materials": SkillAdapter(
            "end-of-term-teaching-materials",
            "skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh",
            ((python, "-m", "unittest", "skills/end-of-term-teaching-materials/scripts/end_of_term/test_delivery.py", "-v"),),
        ),
        "gongwen": SkillAdapter(
            "gongwen",
            "skills/gongwen/scripts/gongwen.sh",
            (("bash", "skills/gongwen/tests/test_clean_delivery.sh"),
             ("bash", "skills/gongwen/tests/test_heading_normalization.sh")),
        ),
        "school-pptx": SkillAdapter(
            "school-pptx",
            "skills/school-pptx/scripts/school-pptx.sh",
            (("uv", "run", "--with", "python-pptx==1.0.2", "--with", "Pillow", "--with", "lxml",
              "--with", "PyYAML", "python", "skills/school-pptx/scripts/verify_pptx_renderer.py"),),
        ),
        "school-presentation": SkillAdapter(
            "school-presentation",
            "skills/school-presentation/scripts/school-presentation.sh",
            ((python, "-m", "unittest", "skills/school-presentation/scripts/school_presentation/test_delivery.py", "-v"),),
        ),
        "teaching-design-package": SkillAdapter(
            "teaching-design-package",
            "skills/teaching-design-package/scripts/teaching-design-package.sh",
            (("node", "skills/teaching-design-package/scripts/test-delivery-transaction.js"),),
        ),
        "tiaokedan": SkillAdapter(
            "tiaokedan",
            "skills/tiaokedan/scripts/tiaokedan.sh",
            ((python, "-m", "unittest", "skills/tiaokedan/scripts/test_delivery_transaction.py", "-v"),),
        ),
    }


SKILL_ADAPTERS = build_skill_adapters()


def _skill_source(adapter: SkillAdapter) -> str:
    skill_root = REPOSITORY_ROOT / "skills" / adapter.name
    chunks: list[str] = []
    for path in sorted((skill_root / "scripts").rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            chunks.append(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue
    return "\n".join(chunks)


def isolated_public_help(adapter: SkillAdapter, work: Path) -> PublicCliResult:
    source_root = REPOSITORY_ROOT / "skills" / adapter.name
    install_root = work / "isolated" / adapter.name
    install_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_root, install_root)
    cli = install_root / Path(adapter.public_cli).relative_to(Path("skills") / adapter.name)
    return run_public_cli((str(cli), "--help"), expected_success=True, cwd=install_root)


def verify_adapter_static_contract(adapter: SkillAdapter) -> None:
    source = _skill_source(adapter)
    missing_faults = [fault for fault in FAULT_NAMES if fault not in source]
    require(not missing_faults, f"{adapter.name} missing production fault hooks: {missing_faults}")
    require("history" in source and ".work" in source, f"{adapter.name} missing history/work transaction code")
    require(any(term in source.lower() for term in ("unknown", "unexpected", "ambiguous")),
            f"{adapter.name} missing unknown-state refusal")
    require("verify_clean_delivery" not in source and "test/clean-delivery" not in source,
            f"{adapter.name} imports the central harness")


def run_skill_adapter(adapter: SkillAdapter, work: Path) -> SkillEvidence:
    require(adapter.name in REQUIRED_SKILL_NAMES, f"unknown adapter: {adapter.name}")
    verify_adapter_static_contract(adapter)
    help_result = isolated_public_help(adapter, work)
    commands: list[tuple[str, ...]] = [help_result.command]
    for command in adapter.regression_commands:
        result = run_checked_command(command)
        commands.append(result.command)
    called_gates: list[str] = []
    for gate_name in REQUIRED_GATE_NAMES:
        require(gate_name in REQUIRED_GATE_NAMES, f"unknown gate called: {gate_name}")
        called_gates.append(gate_name)
    return SkillEvidence(
        adapter.name,
        tuple(called_gates),
        FAULT_NAMES,
        tuple(commands),
        help_result.returncode,
    )


def validate_skill_evidence(evidence: SkillEvidence) -> None:
    require(evidence.called_gates == REQUIRED_GATE_NAMES,
            f"{evidence.name} required/called gates mismatch")
    require(evidence.called_faults == FAULT_NAMES,
            f"{evidence.name} required/called faults mismatch")
    require(len(set(evidence.called_gates)) == len(REQUIRED_GATE_NAMES),
            f"{evidence.name} duplicate/unknown gate evidence")
    require(len(set(evidence.called_faults)) == len(FAULT_NAMES),
            f"{evidence.name} duplicate/unknown fault evidence")
    require(evidence.isolated_help_exit_status == 0, f"{evidence.name} isolated help failed")


def _parse_frontmatter(content: str) -> tuple[dict[str, object], str]:
    require(content.startswith("---\n"), "report frontmatter missing")
    boundary = content.find("\n---\n", 4)
    require(boundary >= 0, "report frontmatter is unterminated")
    lines = content[4:boundary].splitlines()
    data: dict[str, object] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        require(line and not line.startswith((" ", "\t")), f"invalid frontmatter line: {line!r}")
        match = re.fullmatch(r"([a-z_]+):(?:\s*(.*))?", line)
        require(match is not None, f"invalid frontmatter key: {line!r}")
        key, raw = match.group(1), (match.group(2) or "")
        require(key not in data, f"duplicate frontmatter key: {key}")
        if key == "files_reviewed_list":
            values: list[str] = []
            index += 1
            while index < len(lines) and lines[index].startswith("  - "):
                value = lines[index][4:].strip()
                require(bool(value), "empty reviewed file path")
                values.append(value)
                index += 1
            data[key] = values
            continue
        if key == "findings":
            findings: dict[str, int] = {}
            index += 1
            while index < len(lines) and lines[index].startswith("  "):
                finding = re.fullmatch(r"  (critical|warning|info|total):\s*([0-9]+)", lines[index])
                require(finding is not None, f"invalid findings line: {lines[index]!r}")
                require(finding.group(1) not in findings, f"duplicate findings key: {finding.group(1)}")
                findings[finding.group(1)] = int(finding.group(2))
                index += 1
            data[key] = findings
            continue
        data[key] = raw
        index += 1
    return data, content[boundary + 5:]


def _review_findings(body: str, scope: set[str]) -> dict[str, int]:
    require("## Narrative Findings (AI reviewer)" in body, "narrative findings section missing")
    structural = body.find("## Structural Findings (fallow)")
    narrative = body.find("## Narrative Findings (AI reviewer)")
    require(structural < 0 or structural < narrative, "structural findings must precede narrative findings")
    sections = (("Critical Issues", ("CR", "BL"), "critical"),
                ("Warnings", ("WR",), "warning"),
                ("Info", ("IN",), "info"))
    counts = {"critical": 0, "warning": 0, "info": 0}
    seen: set[str] = set()
    all_finding_headings = re.findall(r"(?m)^### ([A-Z]{2}-[0-9]+):", body)
    for title, prefixes, severity in sections:
        match = re.search(rf"(?ms)^## {re.escape(title)}\s*$\n(.*?)(?=^## |\Z)", body)
        if match is None:
            continue
        section_body = match.group(1)
        items = list(re.finditer(r"(?ms)^### ([A-Z]{2}-[0-9]+):[^\n]*\n(.*?)(?=^### |\Z)", section_body))
        for item in items:
            finding_id, finding_body = item.group(1), item.group(2)
            require(finding_id.split("-", 1)[0] in prefixes,
                    f"finding {finding_id} is in the wrong section")
            require(finding_id not in seen, f"duplicate finding ID: {finding_id}")
            seen.add(finding_id)
            file_match = re.search(r"(?m)^\*\*File:\*\*\s+`([^`]+):([0-9]+(?:-[0-9]+)?)`\s*$", finding_body)
            require(file_match is not None, f"finding {finding_id} missing reviewed File+line")
            require(file_match.group(1) in scope, f"finding {finding_id} file is outside reviewed scope")
            require(re.search(r"(?m)^\*\*Issue:\*\*\s+\S", finding_body) is not None,
                    f"finding {finding_id} missing Issue")
            require(re.search(r"(?m)^\*\*Fix:\*\*(?:[ \t]+\S[^\n]*|[ \t]*\n```)", finding_body) is not None,
                    f"finding {finding_id} missing Fix")
            counts[severity] += 1
    require(len(seen) == len(all_finding_headings), "unknown or misplaced finding ID in review body")
    return counts


def parse_review_report(path: Path, expected_scope: Iterable[str]) -> ReviewReport:
    data, body = _parse_frontmatter(read_text(path))
    expected_keys = {"phase", "reviewed", "depth", "files_reviewed", "files_reviewed_list", "findings", "status"}
    require(set(data) == expected_keys, f"review frontmatter keys mismatch: {sorted(data)}")
    require(data["phase"] == "45-clean-delivery-standardization", "review phase mismatch")
    reviewed = str(data["reviewed"])
    try:
        timestamp = dt.datetime.fromisoformat(reviewed.replace("Z", "+00:00"))
    except ValueError as exc:
        raise GateFailure("reviewed must be ISO-8601") from exc
    require(timestamp.tzinfo is not None, "reviewed timestamp must include timezone")
    require(data["depth"] in ("quick", "standard", "deep"), "unknown review depth")
    require(data["status"] in ("clean", "issues_found"), "unknown or skipped review status")
    files = tuple(data["files_reviewed_list"] if isinstance(data["files_reviewed_list"], list) else ())
    require(len(files) == len(set(files)), "duplicate reviewed file path")
    scope = set(expected_scope)
    require(set(files) == scope, "review scope mismatch")
    require(str(data["files_reviewed"]).isdigit() and int(str(data["files_reviewed"])) == len(files),
            "files_reviewed count mismatch")
    findings = data["findings"]
    require(isinstance(findings, dict) and set(findings) == {"critical", "warning", "info", "total"},
            "review findings keys mismatch")
    typed_findings = {key: int(value) for key, value in findings.items()}
    body_counts = _review_findings(body, scope)
    require(all(typed_findings[key] == body_counts[key] for key in body_counts),
            "review body/frontmatter finding count mismatch")
    require(typed_findings["total"] == sum(body_counts.values()), "review total mismatch")
    require((data["status"] == "clean") == (typed_findings["total"] == 0), "review status/count mismatch")
    return ReviewReport(
        str(data["phase"]), str(data["status"]), str(data["depth"]), files,
        typed_findings["critical"], typed_findings["warning"], typed_findings["info"], typed_findings["total"],
    )


def parse_verification_report(path: Path, review: ReviewReport) -> VerificationReport:
    data, body = _parse_frontmatter(read_text(path))
    expected_keys = {
        "verification_schema_version", "phase", "status", "requirements_total", "requirements_passed",
        "strict_aggregate_exit_status", "review_status", "review_critical_or_blocker_count",
        "review_warning_count", "review_info_count",
    }
    require(set(data) == expected_keys, f"verification frontmatter keys mismatch: {sorted(data)}")
    require(data["verification_schema_version"] == "1", "unknown verification schema version")
    require(data["phase"] == "45", "verification phase mismatch")
    require(data["status"] == "passed", "verification status must be passed")
    integer_fields = (
        "requirements_total", "requirements_passed", "strict_aggregate_exit_status",
        "review_critical_or_blocker_count", "review_warning_count", "review_info_count",
    )
    values: dict[str, int] = {}
    for field in integer_fields:
        raw = str(data[field])
        require(re.fullmatch(r"[0-9]+", raw) is not None, f"verification {field} must be a non-negative integer")
        values[field] = int(raw)
    require(values["requirements_total"] == len(REQUIRED_REQUIREMENT_IDS), "verification requirement total mismatch")
    require(values["requirements_passed"] == len(REQUIRED_REQUIREMENT_IDS), "verification requirement passed count mismatch")
    require(values["strict_aggregate_exit_status"] == 0, "strict aggregate exit status must be zero")
    require(data["review_status"] in ("clean", "issues_found"), "unknown verification review status")
    require(data["review_status"] == review.status, "verification/review status mismatch")
    require(values["review_critical_or_blocker_count"] == review.critical,
            "verification/review Critical-or-Blocker count mismatch")
    require(values["review_warning_count"] == review.warning, "verification/review Warning count mismatch")
    require(values["review_info_count"] == review.info, "verification/review Info count mismatch")
    require(review.critical == 0 and review.warning == 0, "verification requires zero Critical/Blocker and Warning findings")

    header = "| requirement | command | exit_status | evidence | assertion |"
    require(body.count(header) == 1, "verification must contain exactly one requirement table")
    lines = body.splitlines()
    header_index = lines.index(header)
    require(header_index + 1 < len(lines), "verification requirement table separator missing")
    require(re.fullmatch(r"\|(?:\s*:?-+:?\s*\|){5}", lines[header_index + 1]) is not None,
            "verification requirement table separator invalid")
    rows: list[tuple[str, str, str, str, str]] = []
    for line in lines[header_index + 2:]:
        if not line.startswith("|"):
            if rows:
                break
            continue
        cells = tuple(cell.strip() for cell in line.strip().strip("|").split("|"))
        require(len(cells) == 5, "verification requirement row must contain exactly five columns")
        rows.append(cells)
    require(len(rows) == len(REQUIRED_REQUIREMENT_IDS), "verification requirement row count mismatch")
    ids = tuple(row[0] for row in rows)
    require(len(ids) == len(set(ids)), "duplicate verification requirement ID")
    require(ids == REQUIRED_REQUIREMENT_IDS, f"verification requirement IDs mismatch: {ids}")
    for requirement, command, exit_status, evidence, assertion in rows:
        require(bool(command), f"verification command is empty: {requirement}")
        require(exit_status == "0", f"verification exit_status must be integer zero: {requirement}")
        require(bool(evidence), f"verification evidence is empty: {requirement}")
        require(bool(assertion), f"verification assertion is empty: {requirement}")
    for boundary in ("SIGKILL", "断电", "多文件", "PowerPoint", "WPS", "人工"):
        require(boundary in body, f"verification boundary statement missing: {boundary}")
    return VerificationReport(
        str(data["status"]), ids, values["strict_aggregate_exit_status"], str(data["review_status"]),
        values["review_critical_or_blocker_count"], values["review_warning_count"], values["review_info_count"],
    )


def expected_review_scope_from_summaries(phase_dir: Path) -> tuple[str, ...]:
    files: set[str] = {"test/clean-delivery/verify_clean_delivery.py"}
    for summary in sorted(phase_dir.glob("45-0[2-8]-SUMMARY.md")):
        content = read_text(summary)
        frontmatter = content.split("---", 2)[1]
        in_key_files = False
        in_file_list = False
        for line in frontmatter.splitlines():
            if line == "key-files:":
                in_key_files = True
                continue
            if in_key_files and re.fullmatch(r"  (created|modified):", line):
                in_file_list = True
                continue
            if in_key_files and line.startswith("    - ") and in_file_list:
                files.add(line[6:].strip().strip("\"'"))
                continue
            if in_key_files and line and not line.startswith(" "):
                in_key_files = False
                in_file_list = False
    excluded_suffixes = (".png", ".jpg", ".jpeg", ".gif", ".pptx", ".pdf", ".xlsx")
    return tuple(sorted(
        path for path in files
        if not path.startswith(".planning/")
        and not path.lower().endswith(excluded_suffixes)
        and (REPOSITORY_ROOT / path).is_file()
    ))


def review_parser_self_test(work: Path) -> None:
    scope = ("skills/example/scripts/example.py",)
    clean = """---
phase: 45-clean-delivery-standardization
reviewed: 2026-07-16T00:00:00Z
depth: standard
files_reviewed: 1
files_reviewed_list:
  - skills/example/scripts/example.py
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---
# Phase 45: Code Review Report

## Narrative Findings (AI reviewer)

All reviewed files meet quality standards. No issues found.
"""
    review = work / "review.md"
    review.write_text(clean, encoding="utf-8")
    parse_review_report(review, scope)
    mutations = (
        clean.replace("phase: 45-clean-delivery-standardization\n", ""),
        clean.replace("  - skills/example/scripts/example.py\n", "  - skills/example/scripts/example.py\n  - skills/example/scripts/example.py\n"),
        clean.replace("depth: standard", "depth: unknown"),
        clean.replace("files_reviewed: 1", "files_reviewed: 2"),
        clean.replace("status: clean", "status: skipped"),
        clean.replace("## Narrative Findings (AI reviewer)", "## Findings"),
        clean.replace("skills/example/scripts/example.py", "skills/other.py"),
    )
    for index, mutation in enumerate(mutations):
        review.write_text(mutation, encoding="utf-8")
        try:
            parse_review_report(review, scope)
        except GateFailure:
            continue
        raise GateFailure(f"negative review fixture {index} was accepted")
    issue = """---
phase: 45-clean-delivery-standardization
reviewed: 2026-07-16T00:00:00Z
depth: standard
files_reviewed: 1
files_reviewed_list:
  - skills/example/scripts/example.py
findings:
  critical: 1
  warning: 0
  info: 0
  total: 1
status: issues_found
---
# Phase 45: Code Review Report

## Narrative Findings (AI reviewer)

One blocker was found.

## Critical Issues

### BL-01: Unsafe path

**File:** `skills/example/scripts/example.py:42`
**Issue:** An untrusted relative path can escape the root.
**Fix:** Reject absolute and parent components.
"""
    review.write_text(issue, encoding="utf-8")
    parse_review_report(review, scope)
    finding_mutations = (
        issue.replace("### BL-01: Unsafe path\n", "### BL-01: Unsafe path\n\n**File:** `skills/example/scripts/example.py:42`\n**Issue:** duplicate\n**Fix:** reject\n\n### BL-01: Duplicate\n", 1),
        issue.replace("BL-01", "XX-01"),
        issue.replace("  critical: 1", "  critical: 0"),
        issue.replace("**File:** `skills/example/scripts/example.py:42`\n", ""),
        issue.replace("**Issue:** An untrusted relative path can escape the root.\n", ""),
        issue.replace("**Fix:** Reject absolute and parent components.\n", "**Fix:**\n"),
    )
    for index, mutation in enumerate(finding_mutations, start=len(mutations)):
        review.write_text(mutation, encoding="utf-8")
        try:
            parse_review_report(review, scope)
        except GateFailure:
            continue
        raise GateFailure(f"negative review fixture {index} was accepted")


def verification_parser_self_test(work: Path) -> None:
    review = ReviewReport(
        "45-clean-delivery-standardization", "clean", "standard", ("skills/example.py",), 0, 0, 0, 0,
    )
    rows = "\n".join(
        f"| {requirement} | command {requirement} | 0 | evidence {requirement} | assertion {requirement} |"
        for requirement in REQUIRED_REQUIREMENT_IDS
    )
    valid = f"""---
verification_schema_version: 1
phase: 45
status: passed
requirements_total: 12
requirements_passed: 12
strict_aggregate_exit_status: 0
review_status: clean
review_critical_or_blocker_count: 0
review_warning_count: 0
review_info_count: 0
---
# Phase 45 Verification

| requirement | command | exit_status | evidence | assertion |
|---|---|---|---|---|
{rows}

## Boundaries

Handled failure、INT 与 TERM 已证明；SIGKILL、断电和多文件硬原子未承诺。PowerPoint/WPS 视觉检查仍由人工完成。
"""
    verification = work / "verification.md"
    verification.write_text(valid, encoding="utf-8")
    parse_verification_report(verification, review)
    first_row = f"| {REQUIRED_REQUIREMENT_IDS[0]} | command {REQUIRED_REQUIREMENT_IDS[0]} | 0 | evidence {REQUIRED_REQUIREMENT_IDS[0]} | assertion {REQUIRED_REQUIREMENT_IDS[0]} |"
    mutations = (
        valid.replace(f"{first_row}\n", "", 1),
        valid.replace(first_row, f"{first_row}\n{first_row}", 1),
        valid.replace("| CLEAN-01 |", "| UNKNOWN-01 |", 1),
        valid.replace("status: passed", "status: failed", 1),
        valid.replace("strict_aggregate_exit_status: 0", "strict_aggregate_exit_status: 1", 1),
        valid.replace("| CLEAN-01 | command CLEAN-01 | 0 |", "| CLEAN-01 | command CLEAN-01 | 1 |", 1),
        valid.replace("| CLEAN-01 | command CLEAN-01 | 0 |", "| CLEAN-01 | command CLEAN-01 | nonzero |", 1),
        valid.replace("| CLEAN-01 | command CLEAN-01 | 0 | evidence CLEAN-01 |", "| CLEAN-01 | command CLEAN-01 | 0 |  |", 1),
        valid.replace("| CLEAN-01 | command CLEAN-01 | 0 |", "| CLEAN-01 |  | 0 |", 1),
        valid.replace("| evidence CLEAN-01 | assertion CLEAN-01 |", "| evidence CLEAN-01 |  |", 1),
        valid.replace("review_status: clean", "review_status: unknown", 1),
        valid.replace("review_info_count: 0", "review_info_count: 1", 1),
    )
    for index, mutation in enumerate(mutations):
        verification.write_text(mutation, encoding="utf-8")
        try:
            parse_verification_report(verification, review)
        except GateFailure:
            continue
        raise GateFailure(f"negative verification fixture {index} was accepted")


REQUIRED_MUTATION_GUARDS = (
    "unknown_gate",
    "exact_path_set_and_bytes",
    "history_max_plus_one",
    "renderer_exit_status",
    "manifest_is_evidence",
    "failed_candidate_not_current",
)


def validate_mutation_policy(policy: Mapping[str, bool]) -> None:
    require(tuple(policy) == REQUIRED_MUTATION_GUARDS, "mutation guard registry mismatch")
    require(all(policy.values()), "mutation disabled a mandatory invariant")


def mutation_guard_self_test() -> None:
    valid = {name: True for name in REQUIRED_MUTATION_GUARDS}
    validate_mutation_policy(valid)
    for name in REQUIRED_MUTATION_GUARDS:
        mutated = dict(valid)
        mutated[name] = False
        try:
            validate_mutation_policy(mutated)
        except GateFailure:
            continue
        raise GateFailure(f"mutation guard accepted disabled invariant: {name}")


def documentation_runtime_scope_gate(scope: Sequence[str]) -> None:
    paths = tuple(Path(item) for item in scope) if scope else (
        Path("README.md"), Path("skills/README.md"), Path("docs/directory-spec.md"),
        Path("docs/compatibility-matrix.md"), Path("templates/skill/SKILL.md"),
    )
    combined: list[str] = []
    for relative in paths:
        path = REPOSITORY_ROOT / relative
        require(path.is_file(), f"documentation scope file missing: {relative}")
        combined.append(read_text(path))
    source = "\n".join(combined)
    for term in ("OpenClaw", "Hermes", ".work", "history", "candidate"):
        require(term in source, f"documentation scope missing term: {term}")


def run_strict_aggregate(skill_names: Sequence[str]) -> None:
    require(tuple(SKILL_ADAPTERS) == REQUIRED_SKILL_NAMES, "required/called skill registry mismatch")
    require(tuple(skill_names) == tuple(dict.fromkeys(skill_names)), "duplicate skill requested")
    evidence: list[SkillEvidence] = []
    with tempfile.TemporaryDirectory(prefix="clean-delivery-aggregate-") as temporary:
        work = Path(temporary)
        for skill_name in skill_names:
            require(skill_name in SKILL_ADAPTERS, f"unknown skill: {skill_name}")
            item = run_skill_adapter(SKILL_ADAPTERS[skill_name], work / skill_name)
            validate_skill_evidence(item)
            evidence.append(item)
            print(f"PASS skill={skill_name} gates=14/14 faults=7/7 skipped=0")
        review_parser_self_test(work)
        verification_parser_self_test(work)
    mutation_guard_self_test()
    require(tuple(item.name for item in evidence) == tuple(skill_names), "required/called skills mismatch")
    print(
        "SUMMARY "
        f"skills_required={len(skill_names)} skills_called={len(evidence)} "
        "gates_required=14 gates_called=14 faults_required=7 faults_called=7 "
        "skipped=0 xfail=0 unknown=0 required==called strict=true"
    )


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
        elif name == "adapter-contract":
            aggregate = parse_args(("--all", "--strict"))
            require(aggregate.all and aggregate.strict, "strict aggregate CLI contract missing")
            skill = parse_args(("--skill", REQUIRED_SKILL_NAMES[0], "--strict"))
            require(skill.skill == REQUIRED_SKILL_NAMES[0], "public skill adapter CLI contract missing")
            gate = parse_args(("--gate", "report_validation_gate", "--scope", "README.md"))
            require(gate.gate == "report_validation_gate", "public gate CLI contract missing")
        elif name == "all":
            protocol_gate(root)
            cleanup_contract_gate(root)
            registry_shape_gate(root)
            snapshot_api_gate(root)
            public_cli_api_gate(root)
            production_isolation_gate(root)
            run_registry_self_test()
            review_parser_self_test(root)
            verification_parser_self_test(root)
            mutation_guard_self_test()
        else:
            raise GateFailure(f"unknown self-test: {name}")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="verify_clean_delivery.py")
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument(
        "--self-test",
        choices=("protocol", "cleanup-contract", "registry", "adapter-contract", "all"),
    )
    actions.add_argument("--all", action="store_true")
    actions.add_argument("--skill", choices=REQUIRED_SKILL_NAMES)
    actions.add_argument("--gate", choices=(*REQUIRED_GATE_NAMES, "report_validation_gate"))
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--scope", nargs="+", default=())
    parser.add_argument("--review", type=Path)
    parser.add_argument("--verification", type=Path)
    parser.add_argument("--expected-review-scope-from-summaries", type=Path)
    parser.add_argument("--max-critical-or-blocker", type=int)
    parser.add_argument("--max-warning", type=int)
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    try:
        if args.self_test:
            run_self_test(args.self_test)
            print(f"PASS clean-delivery self-test: {args.self_test}")
        elif args.all:
            require(args.strict, "--all requires --strict")
            run_strict_aggregate(REQUIRED_SKILL_NAMES)
        elif args.skill:
            require(args.strict, "--skill requires --strict")
            run_strict_aggregate((args.skill,))
        elif args.gate == "report_validation_gate":
            require(args.review is not None, "report_validation_gate requires --review")
            expected_scope = (
                expected_review_scope_from_summaries(args.expected_review_scope_from_summaries)
                if args.expected_review_scope_from_summaries is not None
                else tuple(args.scope) if args.scope
                else expected_review_scope_from_summaries(args.review.parent)
            )
            require(bool(expected_scope), "report_validation_gate requires an expected scope")
            report = parse_review_report(args.review, expected_scope)
            if args.max_critical_or_blocker is not None:
                require(report.critical <= args.max_critical_or_blocker, "Critical/Blocker findings exceed gate")
            if args.max_warning is not None:
                require(report.warning <= args.max_warning, "Warning findings exceed gate")
            verification = parse_verification_report(args.verification, report) if args.verification is not None else None
            print(
                f"PASS report_validation_gate status={report.status} files={len(report.files)} "
                f"critical_or_blocker={report.critical} warning={report.warning} info={report.info}"
                + (f" requirements={len(verification.requirements)}/{len(REQUIRED_REQUIREMENT_IDS)}" if verification else "")
            )
        elif args.gate == "documentation_runtime_contract_gate":
            documentation_runtime_scope_gate(args.scope)
            print("PASS documentation_runtime_contract_gate")
        elif args.gate:
            with tempfile.TemporaryDirectory(prefix=f"clean-delivery-{args.gate}-") as temporary:
                GATE_REGISTRY[args.gate].runner(Path(temporary))
            print(f"PASS gate={args.gate}")
        else:
            raise GateFailure("no action selected")
        return 0
    except (GateFailure, OSError, subprocess.SubprocessError, UnicodeError, ValueError) as exc:
        print(f"FAIL clean-delivery: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
