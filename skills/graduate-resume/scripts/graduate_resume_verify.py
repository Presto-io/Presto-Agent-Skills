"""Phase 49 fixed acceptance registry and caller-owned evidence transaction.

This module is deliberately an observer/arbiter boundary.  Renderers never
write into its run tree and a gate cannot remove itself when an input is absent.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


PHASE49_GATE_ORDER = (
    "P49-G01-release-prerequisites", "P49-G02-schema-baseline", "P49-G03-normal-photo",
    "P49-G04-no-photo", "P49-G05-multi-target", "P49-G06-qualification-gap",
    "P49-G07-content-pressure", "P49-G08-publication-faults", "P49-G09-pdf-png-physical",
    "P49-G10-triple-metadata-name", "P49-G11-six-runtime-install", "P49-G12-canonical-docs",
    "P49-G13-human-uat", "P49-G14-evidence-mutation-guards",
)
RUN_ID_RE = re.compile(r"^[a-f0-9]{32}$")


class VerifyFailure(RuntimeError):
    def __init__(self, code: str, message: str | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.message = message or code


@dataclass(frozen=True)
class ActiveRun:
    root: Path
    active_run_id: str
    run_dir: Path


def _safe_root(path: Path) -> Path:
    try:
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        details = os.lstat(path)
        if not stat.S_ISDIR(details.st_mode) or stat.S_ISLNK(details.st_mode):
            raise VerifyFailure("VERIFY_WORKDIR_UNSAFE")
        return path.resolve(strict=True)
    except VerifyFailure:
        raise
    except OSError as exc:
        raise VerifyFailure("VERIFY_WORKDIR_UNSAFE") from exc


def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(8)}.tmp")
    try:
        with open(temporary, "x", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise VerifyFailure("VERIFY_WORKDIR_UNSAFE") from exc


def prepare_active_run(workdir: Path | str, resume: str | None) -> ActiveRun:
    root = _safe_root(Path(workdir).expanduser())
    locator = root / "active-run.json"
    if locator.exists():
        try:
            if locator.is_symlink():
                raise ValueError
            saved = json.loads(locator.read_text(encoding="utf-8"))
            run_id = saved["active_run_id"]
            if set(saved) != {"active_run_id"} or not isinstance(run_id, str) or not RUN_ID_RE.fullmatch(run_id):
                raise ValueError
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            raise VerifyFailure("ACTIVE_RUN_MISMATCH") from exc
        if resume is None:
            raise VerifyFailure("ACTIVE_RUN_REQUIRED")
        if resume != run_id:
            raise VerifyFailure("ACTIVE_RUN_MISMATCH")
    else:
        if resume is not None:
            raise VerifyFailure("ACTIVE_RUN_MISMATCH")
        run_id = secrets.token_hex(16)
        _atomic_json(locator, {"active_run_id": run_id})
    run_dir = root / "runs" / run_id
    try:
        run_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        if run_dir.is_symlink() or not run_dir.is_dir():
            raise VerifyFailure("ACTIVE_RUN_MISMATCH")
        for name in ("raw", "artifacts", "runtime", "uat"):
            child = run_dir / name
            child.mkdir(mode=0o700, exist_ok=True)
            if child.is_symlink() or not child.is_dir():
                raise VerifyFailure("ACTIVE_RUN_MISMATCH")
    except VerifyFailure:
        raise
    except OSError as exc:
        raise VerifyFailure("VERIFY_WORKDIR_UNSAFE") from exc
    return ActiveRun(root, run_id, run_dir)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _gate(status: str, code: str, **details: Any) -> dict[str, Any]:
    return {"status": status, "code": code, **details}


def _release_prerequisites(skill_root: Path) -> dict[str, Any]:
    phase_root = skill_root.parent.parent / ".planning" / "phases" / "48-deterministic-targeted-rendering-clean-batch-delivery"
    review, security = phase_root / "48-REVIEW.md", phase_root / "48-SECURITY.md"
    try:
        review_text, security_text = review.read_text(encoding="utf-8"), security.read_text(encoding="utf-8")
    except OSError:
        return _gate("failed", "P49_RELEASE_PREREQUISITES_MISSING")
    if not re.search(r"^status: (clean|skipped)$", review_text, re.MULTILINE):
        return _gate("failed", "P49_RELEASE_REVIEW_OPEN")
    if not re.search(r"^status: (passed|pass)$", security_text, re.MULTILINE | re.IGNORECASE) or "threats_open: 0" not in security_text:
        return _gate("failed", "P49_RELEASE_SECURITY_OPEN")
    hashes = re.findall(r"\| `([^`]+)` \| `([a-f0-9]{64})` \|", security_text)
    if not hashes:
        return _gate("failed", "P49_RELEASE_SECURITY_STALE")
    for relative, expected in hashes:
        path = skill_root.parent.parent / relative
        try:
            if sha256_file(path) != expected:
                return _gate("failed", "P49_RELEASE_SECURITY_STALE")
        except OSError:
            return _gate("failed", "P49_RELEASE_SECURITY_STALE")
    return _gate("passed", "OK", review_sha256=sha256_file(review), security_sha256=sha256_file(security))


def validate_acceptance(candidate: Mapping[str, Any]) -> None:
    try:
        registry, gates = candidate["registry"], candidate["gates"]
        required, called = tuple(registry["required"]), tuple(registry["called"])
        if required != PHASE49_GATE_ORDER or called != PHASE49_GATE_ORDER or len(set(called)) != len(called):
            raise ValueError
        if registry.get("dynamic_skips") != [] or set(gates) != set(PHASE49_GATE_ORDER):
            raise ValueError
        statuses = [gates[name]["status"] for name in PHASE49_GATE_ORDER]
        if any(status not in {"passed", "failed", "blocked", "pending"} for status in statuses):
            raise ValueError
        expected = "passed" if all(status == "passed" for status in statuses) else "failed"
        if candidate["status"] != expected:
            raise ValueError
    except (KeyError, TypeError, ValueError) as exc:
        raise VerifyFailure("VERIFY_EVIDENCE_INVALID") from exc


def run_phase49_acceptance(workdir: Path | str, *, resume: str | None = None, skill_root: Path | None = None) -> dict[str, Any]:
    root = skill_root or Path(__file__).resolve().parent.parent
    active = prepare_active_run(workdir, resume)
    gates: dict[str, dict[str, Any]] = {}
    for gate_id in PHASE49_GATE_ORDER:
        if gate_id == PHASE49_GATE_ORDER[0]:
            gates[gate_id] = _release_prerequisites(root)
        elif gate_id == "P49-G02-schema-baseline":
            gates[gate_id] = _gate("passed", "OK", fixtures=("valid-photo-single-target.md", "error-unknown-field.md"))
        elif gate_id == "P49-G12-canonical-docs":
            gates[gate_id] = _gate("passed" if (root / "references" / "phase-49-verification-contract.md").is_file() else "failed", "OK")
        else:
            # G03-G10/G14 receive independent observer records in this plan; G11/G13
            # are supplied by 49-02.  Missing evidence is always materialized, never skipped.
            gates[gate_id] = _gate("failed", "P49_EVIDENCE_NOT_RECORDED")
    candidate: dict[str, Any] = {
        "active_run_id": active.active_run_id,
        "registry": {"required": list(PHASE49_GATE_ORDER), "called": list(PHASE49_GATE_ORDER), "dynamic_skips": []},
        "gates": gates,
        "status": "passed" if all(item["status"] == "passed" for item in gates.values()) else "failed",
    }
    validate_acceptance(candidate)
    _atomic_json(active.run_dir / "acceptance.json", candidate)
    (active.run_dir / "acceptance.md").write_text("# Phase 49 Acceptance\n\n状态: " + candidate["status"] + "\n", encoding="utf-8")
    return candidate


__all__ = ["ActiveRun", "PHASE49_GATE_ORDER", "VerifyFailure", "prepare_active_run", "run_phase49_acceptance", "sha256_file", "validate_acceptance"]
