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


class TypstConsumerContractTests(unittest.TestCase):
    def test_layout_and_typst_consume_only_reopened_selected_facts(self) -> None:
        from graduate_resume_final_markdown import emit_final_markdown, load_final_resume
        from graduate_resume_layout import build_frozen_resume_plan, resolve_theme
        from graduate_resume_typst import emit_typst

        source = SKILL_ROOT / "fixtures" / "valid-generic-no-target.md"
        document = cli.load_resume(str(source))
        cli.validate_document(document)
        projection = resolve_version_projection(
            document.data, None, PageBudgetRequest("auto"),
            lambda theme, selected, request: LayoutFeedback(theme, True, 1, ()),
            overrides={"exclude": [document.data["skills"][0]["id"]]},
        )
        payload = emit_final_markdown(
            document.data, projection, canonical_hash=hashlib.sha256(source.read_bytes()).hexdigest(),
            theme_key="modern", theme_label="现代简洁", page_count=1, photo_mode="no-photo",
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "resume.md"
            path.write_bytes(payload)
            final = load_final_resume(path)
            plan = build_frozen_resume_plan(final.fact_view(), resolve_theme("modern"), "no-photo", None, "a" * 64, "auto")
            typst = emit_typst(plan, final)
        self.assertNotIn(document.data["skills"][0]["id"], typst)
        self.assertIn("theme-layout", typst)
        with self.assertRaises(cli.CliError):
            emit_typst(plan, document.data)

    def test_photo_normalization_is_deterministic_and_embedded(self) -> None:
        from graduate_resume_typst import normalize_photo_bytes

        source = (SKILL_ROOT / "fixtures" / "layout" / "media" / "student-photo.jpg").read_bytes()
        first = normalize_photo_bytes(source)
        second = normalize_photo_bytes(source)
        self.assertEqual(first, second)
        self.assertEqual(first[16:24], (413).to_bytes(4, "big") + (579).to_bytes(4, "big"))
        self.assertNotIn(b"EXIF", first)


class RenderMatrixContractTests(unittest.TestCase):
    def test_generic_matrix_has_three_complete_safe_triples(self) -> None:
        from graduate_resume_layout import build_layout_feedback_adapter
        from graduate_resume_render import build_render_matrix, render_candidate_matrix

        source = SKILL_ROOT / "fixtures" / "valid-generic-no-target.md"
        document = cli.load_resume(str(source))
        cli.validate_document(document)
        feedback = build_layout_feedback_adapter(document.data, "no-photo", None, "a" * 64)
        projection = resolve_version_projection(document.data, None, PageBudgetRequest("auto"), feedback)
        matrix = build_render_matrix(document.data["candidate"]["name"], projection)
        self.assertEqual(tuple(item.theme_key for item in matrix.items), ("conservative", "modern", "expressive"))
        self.assertTrue(all("-通用-" in item.stem for item in matrix.items))
        with tempfile.TemporaryDirectory() as temporary:
            result = render_candidate_matrix(
                Path(temporary) / "candidate", document.data, projection,
                canonical_hash=hashlib.sha256(source.read_bytes()).hexdigest(),
            )
            self.assertTrue(result.publishable)
            names = sorted(path.name for path in result.candidate_root.iterdir())
            self.assertEqual(len(names), 9)
            for item in result.items:
                self.assertEqual({path.suffix for path in result.candidate_root.glob(item.stem + ".*")}, {".md", ".typ", ".pdf"})

    def test_safe_stem_normalizes_and_rejects_collision(self) -> None:
        from graduate_resume_render import RENDER_STEM_COLLISION, build_render_matrix, safe_component

        self.assertEqual(safe_component(" Ａ/Ｂ\x00 C "), "A-B-C")
        source = SKILL_ROOT / "fixtures" / "valid-generic-no-target.md"
        document = cli.load_resume(str(source))
        projection = _projection(document)
        with self.assertRaises(cli.CliError) as raised:
            build_render_matrix("甲", (projection, projection))
        self.assertEqual(raised.exception.code, RENDER_STEM_COLLISION)


if __name__ == "__main__":
    unittest.main(verbosity=2)
