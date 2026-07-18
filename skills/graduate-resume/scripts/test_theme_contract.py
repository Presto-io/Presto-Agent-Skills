#!/usr/bin/env python3
"""Phase 47 regression contract for controlled resume themes and local assets."""

from __future__ import annotations

import contextlib
import io
import json
import os
import stat
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
from graduate_resume_layout import (
    FONT_MANIFEST_INVALID,
    PHOTO_ASSET_INVALID,
    THEME_SPECS,
    FrozenResumePlan,
    build_frozen_plan,
    resolve_layout_photo,
    resolve_theme,
    validate_font_manifest,
)


class ThemeContractTests(unittest.TestCase):
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
            plan = build_frozen_plan(spec, "no-photo", None, "test-hash", "auto")
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
        self.assertEqual(len(validate_font_manifest(SKILL_ROOT / "fonts")), 64)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "manifest.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(cli.CliError) as raised:
                validate_font_manifest(root)
            self.assertEqual(raised.exception.code, FONT_MANIFEST_INVALID)

    def test_photo_resolution_rejects_untrusted_paths_without_absolute_leaks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media = root / "media"
            media.mkdir()
            image = media / "student.jpg"
            image.write_bytes(b"\xff\xd8\xff\xd9")
            (root / "plain.jpg").write_text("not an image", encoding="utf-8")
            (root / "folder").mkdir()
            fifo = root / "pipe.jpg"
            os.mkfifo(fifo)
            unreadable = root / "closed.jpg"
            unreadable.write_bytes(b"\xff\xd8\xff\xd9")
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
        self.assertNotIn("http", template)
        self.assertIn("if image_handle == none", template)
        self.assertIn("crop_policy == \"controlled\" and policy.allow_controlled_crop", template)
        probe = SKILL_ROOT / "templates" / ".theme-contract-probe.typ"
        pdf = probe.with_suffix(".pdf")
        try:
            probe.write_text('#import "resume-themes.typ" as resume\n#resume.fact-block("教育经历", [已核实资料])\n#resume.list-entry("项目经历", "project-001", [完整条目])\n', encoding="utf-8")
            completed = subprocess.run(["typst", "compile", str(probe), str(pdf), "--font-path", str(SKILL_ROOT / "fonts"), "--ignore-system-fonts"], cwd=probe.parent, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
        finally:
            probe.unlink(missing_ok=True)
            pdf.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
