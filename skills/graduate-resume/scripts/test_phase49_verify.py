#!/usr/bin/env python3
"""Phase 49 verifier contracts: fixed registry and caller-owned runs."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from graduate_resume_verify import (
    PHASE49_GATE_ORDER,
    VerifyFailure,
    prepare_active_run,
    validate_acceptance,
)


EXPECTED_GATE_ORDER = (
    "P49-G01-release-prerequisites", "P49-G02-schema-baseline", "P49-G03-normal-photo",
    "P49-G04-no-photo", "P49-G05-multi-target", "P49-G06-qualification-gap",
    "P49-G07-content-pressure", "P49-G08-publication-faults", "P49-G09-pdf-png-physical",
    "P49-G10-triple-metadata-name", "P49-G11-six-runtime-install", "P49-G12-canonical-docs",
    "P49-G13-human-uat", "P49-G14-evidence-mutation-guards",
)


class Phase49VerifierTests(unittest.TestCase):
    def test_gate_order_is_literal_and_complete(self) -> None:
        self.assertEqual(PHASE49_GATE_ORDER, EXPECTED_GATE_ORDER)
        self.assertEqual(len(PHASE49_GATE_ORDER), len(set(PHASE49_GATE_ORDER)))

    def test_active_run_requires_exact_resume_after_first_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "verify"
            first = prepare_active_run(root, None)
            locator = json.loads((root / "active-run.json").read_text(encoding="utf-8"))
            self.assertEqual(locator["active_run_id"], first.active_run_id)
            with self.assertRaisesRegex(VerifyFailure, "ACTIVE_RUN_REQUIRED"):
                prepare_active_run(root, None)
            with self.assertRaisesRegex(VerifyFailure, "ACTIVE_RUN_MISMATCH"):
                prepare_active_run(root, "0" * 32)
            resumed = prepare_active_run(root, first.active_run_id)
            self.assertEqual(resumed.run_dir, first.run_dir)

    def test_candidate_rejects_duplicate_or_forged_registry(self) -> None:
        gates = {gate: {"status": "passed"} for gate in PHASE49_GATE_ORDER}
        candidate = {
            "active_run_id": "a" * 32,
            "registry": {"required": list(PHASE49_GATE_ORDER), "called": list(PHASE49_GATE_ORDER), "dynamic_skips": []},
            "gates": gates,
            "status": "passed",
        }
        validate_acceptance(candidate)
        candidate["registry"]["called"][2] = candidate["registry"]["called"][1]
        with self.assertRaisesRegex(VerifyFailure, "VERIFY_EVIDENCE_INVALID"):
            validate_acceptance(candidate)
        candidate["registry"]["called"] = list(PHASE49_GATE_ORDER)
        candidate["gates"][PHASE49_GATE_ORDER[0]]["status"] = "failed"
        with self.assertRaisesRegex(VerifyFailure, "VERIFY_EVIDENCE_INVALID"):
            validate_acceptance(candidate)


if __name__ == "__main__":
    unittest.main()
