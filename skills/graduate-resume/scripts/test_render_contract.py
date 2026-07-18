#!/usr/bin/env python3
"""Phase 48 final Markdown, embedded-photo and render-matrix contract."""

from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

import graduate_resume_cli as cli
from graduate_resume_targeting import LayoutFeedback, PageBudgetRequest, resolve_version_projection


def _projection(document):
    return resolve_version_projection(
        document.data,
        None,
        PageBudgetRequest("auto"),
        lambda theme, selected, request: LayoutFeedback(theme, True, 1, ()),
    )


class FinalMarkdownContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = SKILL_ROOT / "fixtures" / "valid-no-photo.md"
        self.document = cli.load_resume(str(self.source))
        cli.validate_document(self.document)
        self.projection = _projection(self.document)

    def test_round_trip_is_deterministic_and_tamper_evident(self) -> None:
        from graduate_resume_final_markdown import emit_final_markdown, load_final_resume

        canonical_hash = hashlib.sha256(self.source.read_bytes()).hexdigest()
        payload = emit_final_markdown(
            self.document.data,
            self.projection,
            canonical_hash=canonical_hash,
            theme_key="conservative",
            theme_label="保守稳妥",
            page_count=1,
            photo_mode="no-photo",
        )
        self.assertEqual(payload, emit_final_markdown(
            self.document.data, self.projection, canonical_hash=canonical_hash,
            theme_key="conservative", theme_label="保守稳妥", page_count=1,
            photo_mode="no-photo",
        ))
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "resume.md"
            path.write_bytes(payload)
            reopened = load_final_resume(path)
            self.assertEqual(reopened.selected_fact_ids, self.projection.selected_fact_ids)
            self.assertEqual(tuple(fact.fact_id for fact in reopened.facts), self.projection.selected_fact_ids)
            for needle in (b"reason_codes", b"layout_feedback", b"run_id", str(self.source).encode()):
                self.assertNotIn(needle, payload)
            for old, new in ((canonical_hash, "0" * 64), ("gap_allowed: false", "gap_allowed: true"), ("profile", "profile-x")):
                changed = payload.replace(old.encode(), new.encode(), 1)
                path.write_bytes(changed)
                with self.assertRaises(cli.CliError):
                    load_final_resume(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
