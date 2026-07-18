#!/usr/bin/env python3
"""Phase 47 frozen layout and Typst emission contract."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

import graduate_resume_cli as cli
from graduate_resume_layout import (
    LAYOUT_PLAN_INVALID,
    LAYOUT_UNSATISFIABLE,
    THEME_SPECS,
    build_frozen_resume_plan,
    resolve_theme,
)
from graduate_resume_typst import emit_typst, typst_content


class LayoutContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = cli.load_resume(str(SKILL_ROOT / "fixtures" / "valid-no-photo.md"))
        cli.validate_document(self.document)
        self.font_hash = "a" * 64

    def test_measurement_and_short_auto_plan_are_frozen(self) -> None:
        measurement = SKILL_ROOT / "templates" / "layout-measurement.json"
        raw = measurement.read_bytes()
        config = json.loads(raw)
        self.assertTrue(config["measurement_version"])
        self.assertEqual(set(config["themes"]), set(THEME_SPECS))
        for values in config["themes"].values():
            self.assertEqual(values["one_page_clear_max"], 0.88)
            self.assertEqual(values["one_page_critical_max"], 0.94)
            self.assertEqual(values["two_page_min_page_utilization"], 0.25)
            self.assertEqual(values["epsilon_mm"], 0.1)
        plan = build_frozen_resume_plan(self.document.data, resolve_theme("conservative"), "no-photo", None, self.font_hash, "auto")
        self.assertEqual(plan.page_count, 1)
        self.assertEqual(plan.recommendation.recommended_pages, 1)
        self.assertEqual(plan.measurement_hash, hashlib.sha256(raw).hexdigest())
        self.assertEqual(plan.pages[0].utilization, (plan.pages[0].used_height_mm + 0.1) / plan.pages[0].usable_height_mm)
        self.assertEqual(plan.pages[0].containers[0], "profile")
        self.assertTrue(any(container.section == "education" for container in plan.containers))

    def test_forced_two_pages_can_be_sparse(self) -> None:
        plan = build_frozen_resume_plan(self.document.data, resolve_theme("modern"), "no-photo", None, self.font_hash, "2")
        self.assertEqual(plan.page_count, 2)
        self.assertEqual(plan.recommendation.recommended_pages, 1)
        self.assertEqual(plan.recommendation.comparison_pages, 1)
        self.assertTrue(plan.recommendation.advisory)
        self.assertEqual(len(plan.pages), 2)

    def test_theme_photo_policy_and_plan_tampering_fail_closed(self) -> None:
        for theme in THEME_SPECS.values():
            plan = build_frozen_resume_plan(self.document.data, theme, "no-photo", None, self.font_hash, "auto")
            self.assertEqual(plan.photo_fit, "contain")
            self.assertEqual(plan.crop_policy, "forbid")
            self.assertLessEqual(theme.photo_slot.width_mm, 35)
            self.assertLessEqual(theme.photo_slot.height_mm, 49)
        plan = build_frozen_resume_plan(self.document.data, resolve_theme("conservative"), "no-photo", None, self.font_hash, "auto")
        with self.assertRaises(cli.CliError) as raised:
            plan.validate({**self.document.data, "candidate": {}})
        self.assertEqual(raised.exception.code, LAYOUT_PLAN_INVALID)

    def test_typst_emitter_uses_only_verified_frozen_plan(self) -> None:
        plan = build_frozen_resume_plan(self.document.data, resolve_theme("conservative"), "no-photo", None, self.font_hash, "auto")
        facts = {"__verified__": True, **self.document.data}
        output = emit_typst(plan, facts)
        self.assertNotIn("image(", output)
        self.assertNotIn("student-photo.jpg", output)
        self.assertNotIn("EXIF", output)
        self.assertIn("#pagebreak()", emit_typst(build_frozen_resume_plan(self.document.data, resolve_theme("conservative"), "no-photo", None, self.font_hash, "2"), facts))
        self.assertEqual(typst_content("#[\\]" + "\n"), r"\#\[\\\]#linebreak()")
        with self.assertRaises(cli.CliError) as raised:
            emit_typst(plan, self.document.data)
        self.assertEqual(raised.exception.code, LAYOUT_PLAN_INVALID)

    def test_cli_plan_is_deidentified_frozen_summary(self) -> None:
        args = type("Args", (), {"input": str(SKILL_ROOT / "fixtures" / "valid-no-photo.md"), "assets_root": None, "theme": None, "pages": "2", "photo_mode": "auto"})()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(cli.command_plan(args), 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["plan_type"], "frozen-resume-layout")
        self.assertEqual(payload["frozen_layout"]["page_count"], 2)
        self.assertEqual(payload["frozen_layout"]["recommendation"]["recommended_pages"], 1)
        self.assertNotIn("王宁", output.getvalue())
        self.assertNotIn("fixtures/media", output.getvalue())

    def test_oversized_atomic_entry_fails_closed(self) -> None:
        facts = {
            "candidate": {"name": "甲"},
            "education": [{"id": "edu-1", "school": "学校", "major": "专业"}],
            "projects": [{"id": "project-1", "title": "完整项目", "summary": "中" * 2000}],
        }
        with self.assertRaises(cli.CliError) as raised:
            build_frozen_resume_plan(facts, resolve_theme("expressive"), "no-photo", None, self.font_hash, "auto")
        self.assertEqual(raised.exception.code, LAYOUT_UNSATISFIABLE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
