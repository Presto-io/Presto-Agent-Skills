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
from dataclasses import replace
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

import graduate_resume_cli as cli
from graduate_resume_layout import LAYOUT_PLAN_INVALID, LAYOUT_UNSATISFIABLE, THEME_SPECS, build_frozen_resume_plan, resolve_layout_photo
from graduate_resume_pdf_gate import _compact, verify_rendered_layout


LAYOUT_FIXTURES = (
    "short-no-photo.md",
    "standard-photo.md",
    "boundary-content.md",
    "pressure-two-pages.md",
    "error-unsatisfiable-two-pages.md",
)
THEME_KEYS = ("conservative", "modern", "expressive")
PHOTO_SUBJECT_SAFE_AREA = (0, 0, 1, 1)


def compile_controlled(plan, document, check=None) -> None:
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
        png_paths = sorted(workdir.glob("page-*.png"))
        verify_rendered_layout(plan, document.data, pdf_path, png_paths)
        if check is not None:
            check(pdf_path, png_paths)


def tampered_topologies(plan):
    """Return the four page-assignment attacks against a successful two-page plan."""
    first_page, second_page = plan.pages
    moved_id = second_page.containers[0]
    return {
        "removed": replace(plan, pages=(replace(first_page, containers=first_page.containers[:-1]), second_page)),
        "duplicated": replace(plan, pages=(replace(first_page, containers=first_page.containers + (first_page.containers[-1],)), second_page)),
        "moved": replace(plan, pages=(replace(first_page, containers=first_page.containers + (moved_id,)), replace(second_page, containers=second_page.containers[1:]))),
        "forged-page": replace(plan, containers=tuple(
            replace(container, page_number=1) if container.id == moved_id else container
            for container in plan.containers
        )),
    }


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
            self.assertEqual(auto.page_count, 1)
            if key != "conservative":
                self.assertTrue(auto.pages[0].composition.sidebar_sections)
                with self.assertRaises(cli.CliError) as raised:
                    build_frozen_resume_plan(document.data, THEME_SPECS[key], "no-photo", None, self.font_hash, "2")
                self.assertEqual(raised.exception.code, LAYOUT_UNSATISFIABLE)
                continue
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
        no_photo_document = self.load("pressure-two-pages.md")
        photo = resolve_layout_photo(photo_document.path, self.root, photo_document.data["photo"], photo_document.data["preferences"])
        for key in THEME_KEYS:
            compile_controlled(build_frozen_resume_plan(photo_document.data, THEME_SPECS[key], "photo", photo, self.font_hash, "auto"), photo_document)
            compile_controlled(build_frozen_resume_plan(no_photo_document.data, THEME_SPECS[key], "no-photo", None, self.font_hash, "2"), no_photo_document)

    def test_sidebar_resume_fits_one_page_and_keeps_contacts_visible(self) -> None:
        import fitz

        document = self.load("pressure-two-pages.md")
        document.data["candidate"]["contact"] = {"phone": "13812345678", "email": "student@example.com", "city": "陕西西安"}
        document.data["skills"][0]["items"] = [
            "熟悉电气原理图绘制，掌握继电器、接触器、断路器等元件选型与接线。",
            "掌握西门子PLC梯形图编程，能完成程序编写、下载、在线调试与故障排查。",
            "熟悉变频器参数设置与多段速控制，了解触摸屏画面组态及生产线日常维护。",
            "熟练使用办公软件进行宣传物料设计与文档处理。",
        ]
        for key in THEME_KEYS:
            plan = build_frozen_resume_plan(document.data, THEME_SPECS[key], "no-photo", None, self.font_hash, "auto")
            self.assertEqual(plan.page_count, 1)

            def check(pdf_path, png_paths):
                with fitz.open(pdf_path) as pdf:
                    page = pdf[0]
                    text = _compact(page.get_text())
                    self.assertEqual(text.count("13812345678"), 1)
                    self.assertEqual(text.count("student@example.com"), 1)
                    for block in page.get_text("dict")["blocks"]:
                        for line in block.get("lines", []):
                            bounds = fitz.Rect(line["bbox"])
                            self.assertGreaterEqual(bounds.x0, 42)
                            self.assertLessEqual(bounds.x1, 554)
                            self.assertGreaterEqual(bounds.y0, 35)
                            self.assertLessEqual(bounds.y1, 803)
                    if plan.pages[0].composition.sidebar_sections:
                        skills = page.search_for("专业技能")[0]
                        projects = page.search_for("项目经历")[0]
                        self.assertGreater(projects.x0 - skills.x0, 120)
                        self.assertLess(abs(skills.y0 - projects.y0), 190)

            compile_controlled(plan, document, check)

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

    def test_dense_two_pages_fill_each_page_and_sparse_request_warns(self) -> None:
        document = self.load("pressure-two-pages.md")
        for index in range(5):
            document.data["projects"].append({
                "id": f"project-dense-{index}", "status": "verified",
                "title": f"综合设备调试项目{index}",
                "summary": "依据电气图纸完成接线与检查，使用仪表核对供电和信号，记录设备运行状态并分析异常原因。" * 3,
                "outcomes": ["完成接线复核与试运行记录。"],
            })
        for key in THEME_KEYS:
            if key == "modern":
                for index in range(5, 11):
                    document.data["projects"].append({
                        "id": f"project-dense-{index}", "status": "verified",
                        "title": f"综合设备调试项目{index}",
                        "summary": "依据电气图纸完成接线与检查，使用仪表核对供电和信号，记录设备运行状态并分析异常原因。" * 3,
                        "outcomes": ["完成接线复核与试运行记录。"],
                    })
            plan = build_frozen_resume_plan(document.data, THEME_SPECS[key], "no-photo", None, self.font_hash, "2")
            self.assertEqual(plan.page_count, 2)
            for page in plan.pages:
                if key != "conservative":
                    self.assertTrue(page.composition.sidebar_sections)
                    self.assertGreater(page.composition.sidebar_width_mm, 0)
                self.assertTrue(page.composition.fill_satisfied)
                self.assertGreaterEqual(page.used_height_mm, 240)
                self.assertLessEqual(page.used_height_mm, 265)
                self.assertLessEqual(page.elastic_gap_mm, 10)
            compile_controlled(plan, document)
        sparse = self.load("short-no-photo.md")
        forced = build_frozen_resume_plan(sparse.data, THEME_SPECS["conservative"], "no-photo", None, self.font_hash, "2")
        self.assertIn("强制双页", forced.recommendation.advisory)

    def test_pressure_evidence_rejects_tampered_topologies_and_displays_each_field_once(self) -> None:
        from graduate_resume_typst import emit_typst

        pressure = self.load("pressure-two-pages.md")
        # The source fixture has deliberately short Chinese values such as “设备维护”
        # that also occur inside longer titles.  Use non-overlapping verified values
        # so this D-05 probe measures duplicate emission rather than substring overlap.
        pressure.data["education"][0]["courses"] = ["课程甲唯一值", "课程乙唯一值", "课程丙唯一值", "课程丁唯一值"]
        pressure.data["skills"][0]["items"] = ["技能甲唯一值", "技能乙唯一值", "技能丙唯一值", "技能丁唯一值", "技能戊唯一值", "技能己唯一值"]
        pressure.data["projects"][0]["role"] = "控制柜装配执行者"
        pressure.data["projects"][1]["role"] = "独立巡检执行者"
        cli.validate_document(pressure)
        for key in THEME_KEYS:
            plan = build_frozen_resume_plan(pressure.data, THEME_SPECS[key], "no-photo", None, self.font_hash, "2")
            facts = {"__verified__": True, **pressure.data}
            variants = tampered_topologies(plan)
            for name, tampered in variants.items():
                with self.subTest(theme=key, tampering=name):
                    with self.assertRaises(cli.CliError) as raised:
                        emit_typst(tampered, facts)
                    self.assertEqual(raised.exception.code, LAYOUT_PLAN_INVALID)

            def check(pdf_path, png_paths):
                for name, tampered in variants.items():
                    with self.subTest(theme=key, gate_tampering=name):
                        with self.assertRaises(cli.CliError) as raised:
                            verify_rendered_layout(tampered, pressure.data, pdf_path, png_paths)
                        self.assertEqual(raised.exception.code, LAYOUT_PLAN_INVALID)
                import fitz
                with fitz.open(pdf_path) as pdf:
                    rendered = _compact("".join(page.get_text() for page in pdf))
                for container in plan.containers:
                    if container.section not in {"education", "skills", "certificates", "projects", "training", "experience"}:
                        continue
                    for field_key, value in container.fields:
                        with self.subTest(theme=key, container=container.id, field=field_key):
                            self.assertEqual(rendered.count(_compact(value)), 1)

            compile_controlled(plan, pressure, check)


if __name__ == "__main__":
    unittest.main(verbosity=2)
