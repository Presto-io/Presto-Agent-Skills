#!/usr/bin/env python3
"""Phase 47 regression contract for controlled resume themes and local assets."""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import fitz
from dataclasses import replace
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

import graduate_resume_cli as cli
from graduate_resume_layout import (
    FONT_MANIFEST_INVALID,
    PHOTO_ASSET_INVALID,
    THEME_SPECS,
    FrozenResumePlan,
    build_frozen_resume_plan,
    resolve_layout_photo,
    resolve_theme,
    validate_font_manifest,
)
from graduate_resume_typst_runtime import resolve_typst_executable


class ThemeContractTests(unittest.TestCase):
    def test_two_column_template_rejects_empty_sidebar(self) -> None:
        template = (SKILL_ROOT / "templates" / "resume-themes.typ").read_text(encoding="utf-8")
        with resolve_typst_executable() as executable, tempfile.TemporaryDirectory() as temporary:
            for theme in ("modern", "expressive"):
                probe = Path(temporary) / f"empty-sidebar-{theme}.typ"
                probe.write_text(template + f'\n#resume-page("{theme}", main: [正文])', encoding="utf-8")
                result = subprocess.run([str(executable.snapshot_path), "compile", str(probe), "--font-path", str(SKILL_ROOT / "fonts"), "--ignore-system-fonts"], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("two-column themes require content in both columns", result.stderr)

    def test_modern_photo_header_keeps_sidebar_clear_of_divider(self) -> None:
        template = (SKILL_ROOT / "templates" / "resume-themes.typ").read_text(encoding="utf-8")
        with resolve_typst_executable() as executable, tempfile.TemporaryDirectory() as temporary:
            for row_count in (2, 8):
                with self.subTest(row_count=row_count):
                    probe = Path(temporary) / f"header-{row_count}.typ"
                    personal = "(" + "([字段], [内容])," * (row_count * 2) + ")"
                    header = '#identity-block("modern", name: [学生], headline: [电气自动化], personal: ' + personal + ', photo: rect(width: 28mm, height: 36mm, fill: black))'
                    probe.write_text(template + '\n#resume-page("modern", header: [' + header + '], sidebar: [#fact-block("modern", "skills", ([技能内容],))], main: [正文])', encoding="utf-8")
                    result = subprocess.run([str(executable.snapshot_path), "compile", str(probe), "--font-path", str(SKILL_ROOT / "fonts"), "--ignore-system-fonts"], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    with fitz.open(probe.with_suffix(".pdf")) as document:
                        self.assertEqual(len(document), 1)
                        drawings = document[0].get_drawings()
                        divider = next(drawing["rect"] for drawing in drawings if drawing["rect"].width > 300 and drawing["rect"].height < 1)
                        sidebar = next(drawing["rect"] for drawing in drawings if drawing.get("fill") is not None and 0.9 < drawing["fill"][0] < 0.95)
                        self.assertGreaterEqual(sidebar.y0 - divider.y1, 3 * 72 / 25.4 - 0.5)

    def test_paragraph_indents_and_bullet_column(self) -> None:
        template = (SKILL_ROOT / "templates" / "resume-themes.typ").read_text(encoding="utf-8")
        with resolve_typst_executable() as executable, tempfile.TemporaryDirectory() as temporary:
            probe = Path(temporary) / "paragraphs.typ"
            plain = "甲乙丙丁戊己庚辛壬癸" * 3
            outcome = "子丑寅卯辰巳午未申酉戌亥" * 3
            probe.write_text(template + '\n#set text(size: 10.2pt)\n#set par(leading: 0.95em, spacing: 0pt)\n#block(width: 70mm)[#body-paragraph([' + plain + '])#v(3mm)#outcome-paragraph("modern", [' + outcome + '])]', encoding="utf-8")
            result = subprocess.run([str(executable.snapshot_path), "compile", str(probe), "--font-path", str(SKILL_ROOT / "fonts"), "--ignore-system-fonts"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            with fitz.open(probe.with_suffix(".pdf")) as document:
                spans = [span for block in document[0].get_text("dict")["blocks"] for line in block.get("lines", []) for span in line["spans"]]
                plain_spans = [span for span in spans if span["text"].strip() and span["text"][0] in plain]
                bullet_spans = [span for span in spans if span["text"].strip() and span["text"][0] in outcome]
                left = 15 * 72 / 25.4
                for span in plain_spans:
                    self.assertAlmostEqual(span["bbox"][0] - left, 10.2, places=3)
                for span in bullet_spans:
                    self.assertAlmostEqual(span["bbox"][0] - left, 10.2, places=3)
                marker = next(span for span in spans if span["text"] == "•")
                self.assertAlmostEqual((marker["bbox"][0] + marker["bbox"][2]) / 2 - left, 5.1, places=3)
                self.assertAlmostEqual((marker["bbox"][1] + marker["bbox"][3]) / 2, (bullet_spans[0]["bbox"][1] + bullet_spans[0]["bbox"][3]) / 2, places=2)

    def test_inline_icons_stay_inside_sidebar_background(self) -> None:
        template = (SKILL_ROOT / "templates" / "resume-themes.typ").read_text(encoding="utf-8")
        sections = ("education", "skills", "certificates", "projects", "training", "experience")
        labels = ("教育经历", "专业技能", "证书与资格", "项目经历", "实训经历", "相关经历")
        with resolve_typst_executable() as executable, tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            probe = root / "icons.typ"
            body = "\n".join(f'#fact-block("modern", "{section}", ([已核实资料],))' for section in sections)
            probe.write_text(template + '\n#resume-page("modern", sidebar: [' + body + '], main: [正文])', encoding="utf-8")
            pdf = probe.with_suffix(".pdf")
            result = subprocess.run([str(executable.snapshot_path), "compile", str(probe), str(pdf), "--font-path", str(SKILL_ROOT / "fonts"), "--ignore-system-fonts"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            with fitz.open(pdf) as document:
                page = document[0]
                drawings = page.get_drawings()
                background = next(drawing["rect"] for drawing in drawings if drawing.get("fill") is not None and drawing.get("color") is None)
                for label in labels:
                    heading = page.search_for(label)[0]
                    shapes = [drawing["rect"] for drawing in drawings
                              if drawing.get("color") is not None
                              and heading.x0 - 16 < drawing["rect"].x0 < drawing["rect"].x1 < heading.x0
                              and heading.y0 - 1 < drawing["rect"].y0 < drawing["rect"].y1 < heading.y1 + 1]
                    self.assertTrue(shapes, label)
                    bounds = fitz.Rect(shapes[0])
                    for shape in shapes[1:]:
                        bounds |= shape
                    self.assertGreater(bounds.x0 - background.x0, 2.8, label)
                    self.assertLess(bounds.x1, heading.x0, label)
                    self.assertLess(abs((bounds.y0 + bounds.y1 - heading.y0 - heading.y1) / 2), 0.5, label)

    def test_inline_icons_shift_headings_and_preserve_body_alignment(self) -> None:
        template = (SKILL_ROOT / "templates" / "resume-themes.typ").read_text(encoding="utf-8")
        baseline = template.replace("#section-icon(theme, section)#h(1mm)", "")
        sections = ("education", "skills", "certificates", "projects", "training", "experience")
        with resolve_typst_executable() as executable, tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for theme in THEME_SPECS:
                body = "\n".join(f'#fact-block("{theme}", "{section}", ([已核实的专业资料与项目成果],))' for section in sections)
                for page_count in (1, 2):
                    sidebar = '' if theme == "conservative" else ', sidebar: [辅助资料]'
                    contents = "\n#pagebreak()\n".join(f'#resume-page("{theme}", main: [{body}]{sidebar})' for _ in range(page_count))
                    observations = []
                    for name, source in (("baseline", baseline), ("icons", template)):
                        probe = root / f"{theme}-{page_count}-{name}.typ"
                        probe.write_text(source + "\n" + contents, encoding="utf-8")
                        pdf = probe.with_suffix(".pdf")
                        result = subprocess.run([str(executable.snapshot_path), "compile", str(probe), str(pdf), "--font-path", str(SKILL_ROOT / "fonts"), "--ignore-system-fonts"], capture_output=True, text=True)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        with fitz.open(pdf) as document:
                            self.assertEqual(len(document), page_count)
                            observations.append(([
                                [(span["text"], tuple(round(value, 4) for value in span["bbox"]))
                                 for block in page.get_text("dict")["blocks"] for line in block.get("lines", []) for span in line["spans"]]
                                for page in document
                            ], [len(page.get_drawings()) for page in document]))
                    for old_page, new_page in zip(observations[0][0], observations[1][0]):
                        self.assertEqual(len(old_page), len(new_page))
                        for (old_text, old_box), (new_text, new_box) in zip(old_page, new_page):
                            self.assertEqual(old_text.strip(), new_text.strip())
                            shift = 5.2 * 72 / 25.4 if old_text.strip() in ("教育经历", "专业技能", "证书与资格", "项目经历", "实训经历", "相关经历") else 0
                            for index in (0, 2):
                                self.assertAlmostEqual(new_box[index], old_box[index] + shift, places=3)
                            self.assertAlmostEqual(new_box[3] - new_box[1], old_box[3] - old_box[1], places=3)
                    for old_count, new_count in zip(observations[0][1], observations[1][1]):
                        self.assertGreaterEqual(new_count - old_count, len(sections))

    def test_three_theme_aliases_and_photo_policy_are_frozen(self) -> None:
        expected = {"保守稳妥": "conservative", "现代简洁": "modern", "个性设计": "expressive"}
        self.assertEqual(set(THEME_SPECS), set(expected.values()))
        no_photo_behaviors = {
            "conservative": "remove-slot-and-decoration",
            "modern": "move-sidebar-content-up",
            "expressive": "expand-identity-bar",
        }
        for label, key in expected.items():
            spec = resolve_theme(label)
            self.assertEqual(spec.key, key)
            self.assertEqual(resolve_theme(key), spec)
            self.assertLessEqual(spec.photo_slot.width_mm, 35)
            self.assertLessEqual(spec.photo_slot.height_mm, 49)
            self.assertEqual(spec.photo_policy.photo_fit, "contain")
            self.assertEqual(spec.photo_policy.crop_policy, "forbid")
            self.assertTrue(spec.photo_policy.preserve_aspect_ratio)
            self.assertFalse(spec.photo_policy.allow_stretch)
            self.assertEqual(spec.no_photo_behavior, no_photo_behaviors[key])
            facts = cli.load_resume(str(SKILL_ROOT / "fixtures" / "valid-no-photo.md")).data
            plan = build_frozen_resume_plan(facts, spec, "no-photo", None, "a" * 64, "auto")
            self.assertIsInstance(plan, FrozenResumePlan)
            self.assertEqual(plan.photo_fit, "contain")
            self.assertEqual(plan.crop_policy, "forbid")
            self.assertIsNone(plan.photo)
        with self.assertRaises(cli.CliError) as raised:
            resolve_theme("unknown")
        self.assertEqual(raised.exception.code, "THEME_INVALID")

    def test_theme_is_visual_only_and_registry_is_additive(self) -> None:
        forbidden = {"candidate", "target", "facts", "body", "content", "entry_ids"}
        for spec in THEME_SPECS.values():
            self.assertFalse(forbidden.intersection(spec.__dataclass_fields__))
        document = cli.load_resume(str(SKILL_ROOT / "fixtures" / "valid-no-photo.md"))
        before = json.dumps(document.data, ensure_ascii=False, sort_keys=True)
        clone = replace(THEME_SPECS["conservative"], key="future-visual", label="未来视觉")
        expanded = {**THEME_SPECS, clone.key: clone}
        self.assertIn("future-visual", expanded)
        self.assertEqual(before, json.dumps(document.data, ensure_ascii=False, sort_keys=True))

    def test_font_manifest_rejects_tampering(self) -> None:
        with resolve_typst_executable() as executable:
            self.assertEqual(len(validate_font_manifest(SKILL_ROOT / "fonts", executable)), 64)
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                (root / "manifest.json").write_text("{}", encoding="utf-8")
                with self.assertRaises(cli.CliError) as raised:
                    validate_font_manifest(root, executable)
                self.assertEqual(raised.exception.code, FONT_MANIFEST_INVALID)

    def test_photo_resolution_rejects_untrusted_paths_without_absolute_leaks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media = root / "media"
            media.mkdir()
            image = media / "student.jpg"
            image.write_bytes(b"\xff\xd8safe\xff\xd9")
            (root / "plain.jpg").write_text("not an image", encoding="utf-8")
            (root / "folder").mkdir()
            fifo = root / "pipe.jpg"
            os.mkfifo(fifo)
            unreadable = root / "closed.jpg"
            unreadable.write_bytes(b"\xff\xd8safe\xff\xd9")
            unreadable.chmod(0)
            try:
                good = resolve_layout_photo(root, root, {"status": "provided", "path": "media/student.jpg"}, {})
                self.assertEqual(good.logical_path, "media/student.jpg")
                for bad in ("/tmp/a.jpg", "../a.jpg", "./media/student.jpg", "C:\\a.jpg", "\\\\server\\share\\a.jpg", "https://example.test/a.jpg", "folder", "pipe.jpg", "closed.jpg", "plain.jpg"):
                    with self.assertRaises(cli.CliError) as raised:
                        resolve_layout_photo(root, root, {"status": "provided", "path": bad}, {})
                    self.assertEqual(raised.exception.code, PHOTO_ASSET_INVALID)
                    self.assertNotIn(str(root), raised.exception.message)
                (root / "link.jpg").symlink_to(image)
                with self.assertRaises(cli.CliError) as raised:
                    resolve_layout_photo(root, root, {"status": "provided", "path": "link.jpg"}, {})
                self.assertEqual(raised.exception.code, PHOTO_ASSET_INVALID)
            finally:
                unreadable.chmod(stat.S_IRUSR | stat.S_IWUSR)

    def test_no_photo_never_retains_asset_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertIsNone(resolve_layout_photo(root, root, {"status": "no-photo"}, {"photo_mode": "no-photo"}))

    def test_plan_shows_all_themes_without_photo_path(self) -> None:
        args = type("Args", (), {"input": str(SKILL_ROOT / "fixtures" / "valid-no-photo.md"), "assets_root": None, "theme": None, "pages": "auto", "photo_mode": "auto"})()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(cli.command_plan(args), 0)
        payload = output.getvalue()
        for text in ("保守稳妥", "conservative", "现代简洁", "modern", "个性设计", "expressive", "--theme <key>"):
            self.assertIn(text, payload)
        self.assertNotIn("student-photo.jpg", payload)

    def test_typst_template_contains_only_visual_contract(self) -> None:
        template = (SKILL_ROOT / "templates" / "resume-themes.typ").read_text(encoding="utf-8")
        for token in ("conservative", "modern", "expressive", "block(breakable: false)", "Noto Sans Mono CJK SC", "paper: \"a4\"", "photo_fit: \"contain\"", "allow_controlled_crop"):
            self.assertIn(token, template)
        self.assertNotIn("student-photo.jpg", template)
        self.assertNotIn("https://", template)
        self.assertIn("if image_handle == none", template)
        self.assertIn("crop_policy == \"controlled\" and policy.allow_controlled_crop", template)
        with tempfile.TemporaryDirectory() as temporary:
            probe = Path(temporary) / "probe.typ"
            pdf = probe.with_suffix(".pdf")
            shutil.copy2(SKILL_ROOT / "templates" / "resume-themes.typ", probe.parent / "resume-themes.typ")
            probe.write_text('#import "resume-themes.typ" as resume\n#resume.theme-layout("conservative")[\n  #resume.fact-block("conservative", "education", ([已核实资料],))\n  #resume.resume-entry("conservative", "projects", "project-001", title: [完整条目])\n]\n', encoding="utf-8")
            completed = subprocess.run(["typst", "compile", str(probe), str(pdf), "--font-path", str(SKILL_ROOT / "fonts"), "--ignore-system-fonts"], cwd=probe.parent, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
