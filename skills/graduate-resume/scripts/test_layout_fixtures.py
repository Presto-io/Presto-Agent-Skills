#!/usr/bin/env python3
"""固定 Phase 47 样张矩阵的红绿回归。"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

import graduate_resume_cli as cli
from graduate_resume_layout import LAYOUT_UNSATISFIABLE, THEME_SPECS, build_frozen_resume_plan, resolve_layout_photo
from graduate_resume_pdf_gate import verify_rendered_layout


LAYOUT_FIXTURES = (
    "short-no-photo.md",
    "standard-photo.md",
    "boundary-content.md",
    "pressure-two-pages.md",
    "error-unsatisfiable-two-pages.md",
)
THEME_KEYS = ("conservative", "modern", "expressive")
PHOTO_SUBJECT_SAFE_AREA = (0, 0, 1, 1)


def compile_controlled(plan, document) -> None:
    """Compile one fixture only under a disposable evidence root."""
    from graduate_resume_typst import emit_typst
    with tempfile.TemporaryDirectory() as temporary:
        workdir = Path(temporary)
        shutil.copy2(SKILL_ROOT / "templates" / "resume-themes.typ", workdir / "resume-themes.typ")
        if plan.photo is not None:
            (workdir / "media").mkdir()
            shutil.copy2(SKILL_ROOT / "fixtures" / "layout" / plan.photo.logical_path, workdir / plan.photo.logical_path)
        typst_path = workdir / "resume.typ"
        typst_path.write_text(emit_typst(plan, {"__verified__": True, **document.data}), encoding="utf-8")
        pdf_path = workdir / "resume.pdf"
        common = ["typst", "compile", "--font-path", str(SKILL_ROOT / "fonts"), "--ignore-system-fonts", "--creation-timestamp", "0", str(typst_path)]
        completed = subprocess.run([*common, str(pdf_path)], cwd=workdir, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if completed.returncode:
            raise AssertionError(completed.stderr)
        png_template = workdir / "page-{0p}.png"
        completed = subprocess.run([*common, str(png_template)], cwd=workdir, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if completed.returncode:
            raise AssertionError(completed.stderr)
        info = subprocess.run(["pdfinfo", str(pdf_path)], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if info.returncode or not re.search(rf"^Pages:\s+{plan.page_count}$", info.stdout, re.MULTILINE) or "A4" not in info.stdout:
            raise AssertionError("PDF 不是冻结的 A4 页数")
        verify_rendered_layout(plan, document.data, pdf_path, sorted(workdir.glob("page-*.png")))


def run_layout_fixture_matrix() -> None:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(LayoutFixtureTests)
    result = unittest.TextTestRunner(stream=open("/dev/null", "w", encoding="utf-8"), verbosity=0).run(suite)
    if not result.wasSuccessful():
        raise cli.CliError("LAYOUT_RENDER_MISMATCH", "固定布局样张验证失败。")


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

    def test_shell_cli_normalizes_unsatisfiable_layout_errors(self) -> None:
        fixture = self.root / "error-unsatisfiable-two-pages.md"
        shell = SCRIPT_DIR / "graduate-resume.sh"
        for key in THEME_KEYS:
            completed = subprocess.run(
                [str(shell), "plan", "--input", str(fixture), "--theme", key, "--pages", "2"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertNotIn("Traceback", completed.stderr)
            payload = json.loads(completed.stderr)
            self.assertEqual(payload["status"], "failed")
            self.assertEqual(payload["code"], LAYOUT_UNSATISFIABLE)

    def test_each_theme_compiles_controlled_photo_and_no_photo_evidence(self) -> None:
        photo_document = self.load("standard-photo.md")
        no_photo_document = self.load("short-no-photo.md")
        photo = resolve_layout_photo(photo_document.path, self.root, photo_document.data["photo"], photo_document.data["preferences"])
        for key in THEME_KEYS:
            compile_controlled(build_frozen_resume_plan(photo_document.data, THEME_SPECS[key], "photo", photo, self.font_hash, "auto"), photo_document)
            compile_controlled(build_frozen_resume_plan(no_photo_document.data, THEME_SPECS[key], "no-photo", None, self.font_hash, "2"), no_photo_document)

    def test_boundary_and_pressure_fixtures_compile_for_every_theme(self) -> None:
        boundary = self.load("boundary-content.md")
        pressure = self.load("pressure-two-pages.md")
        for key in THEME_KEYS:
            boundary_plan = build_frozen_resume_plan(boundary.data, THEME_SPECS[key], "no-photo", None, self.font_hash, "auto")
            pressure_plan = build_frozen_resume_plan(pressure.data, THEME_SPECS[key], "no-photo", None, self.font_hash, "2")
            self.assertIn(boundary_plan.page_count, (1, 2))
            self.assertEqual(pressure_plan.page_count, 2)
            self.assertEqual(len(pressure_plan.pages), 2)
            self.assertTrue(pressure_plan.pages[1].anchors)
            compile_controlled(boundary_plan, boundary)
            compile_controlled(pressure_plan, pressure)


if __name__ == "__main__":
    unittest.main(verbosity=2)
