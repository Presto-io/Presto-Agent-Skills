#!/usr/bin/env python3
"""固定 Phase 47 样张矩阵的红绿回归。"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

import graduate_resume_cli as cli
from graduate_resume_layout import LAYOUT_UNSATISFIABLE, THEME_SPECS, build_frozen_resume_plan, resolve_layout_photo


LAYOUT_FIXTURES = (
    "short-no-photo.md",
    "standard-photo.md",
    "boundary-content.md",
    "pressure-two-pages.md",
    "error-unsatisfiable-two-pages.md",
)
THEME_KEYS = ("conservative", "modern", "expressive")
PHOTO_SUBJECT_SAFE_AREA = (0, 0, 1, 1)


class LayoutFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = SKILL_ROOT / "fixtures" / "layout"
        self.font_hash = "a" * 64
        self.measurement = json.loads((SKILL_ROOT / "templates" / "layout-measurement.json").read_text(encoding="utf-8"))

    def load(self, name: str):
        document = cli.load_resume(str(self.root / name))
        cli.validate_document(document)
        return document

    def test_matrix_is_literal_and_all_sources_validate(self) -> None:
        self.assertEqual(LAYOUT_FIXTURES, ("short-no-photo.md", "standard-photo.md", "boundary-content.md", "pressure-two-pages.md", "error-unsatisfiable-two-pages.md"))
        self.assertEqual(THEME_KEYS, ("conservative", "modern", "expressive"))
        for name in LAYOUT_FIXTURES:
            self.assertTrue((self.root / name).is_file())
            self.load(name)

    def test_short_no_photo_auto_and_forced_two_pages(self) -> None:
        document = self.load("short-no-photo.md")
        for key in THEME_KEYS:
            auto = build_frozen_resume_plan(document.data, THEME_SPECS[key], "no-photo", None, self.font_hash, "auto")
            forced = build_frozen_resume_plan(document.data, THEME_SPECS[key], "no-photo", None, self.font_hash, "2")
            self.assertEqual(auto.page_count, 1)
            self.assertEqual(forced.page_count, 2)
            self.assertEqual(forced.recommendation.recommended_pages, 1)
            self.assertEqual(forced.recommendation.comparison_pages, 1)
            self.assertTrue(forced.recommendation.advisory)
            self.assertTrue(any(page.utilization < 0.25 for page in forced.pages))

    def test_photo_slots_and_unsatisfiable_fixture(self) -> None:
        standard = self.load("standard-photo.md")
        failing = self.load("error-unsatisfiable-two-pages.md")
        photo = resolve_layout_photo(standard.path, self.root, standard.data["photo"], standard.data["preferences"])
        self.assertEqual(PHOTO_SUBJECT_SAFE_AREA, (0, 0, 1, 1))
        for key in THEME_KEYS:
            plan = build_frozen_resume_plan(standard.data, THEME_SPECS[key], "photo", photo, self.font_hash, "auto")
            self.assertEqual(plan.photo_fit, "contain")
            self.assertEqual(plan.crop_policy, "forbid")
            self.assertLessEqual(plan.photo_slot.width_mm, 35)
            self.assertLessEqual(plan.photo_slot.height_mm, 49)
            with self.assertRaises(cli.CliError) as raised:
                build_frozen_resume_plan(failing.data, THEME_SPECS[key], "no-photo", None, self.font_hash, "2")
            self.assertEqual(raised.exception.code, LAYOUT_UNSATISFIABLE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
