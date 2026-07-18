from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import graduate_resume_cli as cli
from graduate_resume_targeting import condition_id_for_requirement


SKILL_ROOT = Path(__file__).resolve().parent.parent
CLI = SKILL_ROOT / "scripts" / "graduate_resume_cli.py"
THEME_LABELS = ("保守稳妥", "现代简洁", "个性设计")


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *arguments],
        cwd=SKILL_ROOT.parent.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def parse_json(completed: subprocess.CompletedProcess[str]) -> dict[str, object]:
    stream = completed.stdout if completed.returncode == 0 else completed.stderr
    return json.loads(stream)


def public_files(root: Path) -> tuple[Path, ...]:
    return tuple(sorted(path for path in root.iterdir() if path.is_file())) if root.exists() else ()


class PublicCliContractTests(unittest.TestCase):
    def test_help_exposes_only_exact_not_applicable_contract(self) -> None:
        completed = run_cli("render", "--help")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--not-applicable TARGET_ID CONDITION_ID REASON", completed.stdout)
        self.assertIn("--allow-gap-target TARGET_ID", completed.stdout)
        self.assertNotIn("override-file", completed.stdout)
        self.assertNotIn("TARGET=JSON", completed.stdout)

    def test_generic_render_preflights_then_publishes_three_theme_triples_and_true_noop(self) -> None:
        source = SKILL_ROOT / "fixtures" / "valid-no-photo.md"
        with tempfile.TemporaryDirectory() as temporary:
            delivery = Path(temporary) / "delivery"
            base = (
                "render", "--input", str(source), "--generic",
                "--delivery-root", str(delivery), "--photo-mode", "no-photo",
            )
            preview = run_cli(*base)
            self.assertEqual(preview.returncode, 0, preview.stderr)
            payload = parse_json(preview)
            self.assertEqual(payload["status"], "preflight")
            self.assertEqual(payload["mode"], "patch")
            self.assertEqual(len(payload["stems"]), 3)
            self.assertEqual(public_files(delivery), ())

            published = run_cli(*base, "--confirm")
            self.assertEqual(published.returncode, 0, published.stderr)
            self.assertEqual(parse_json(published)["publication"], "first")
            files = public_files(delivery)
            self.assertEqual(len(files), 9)
            self.assertEqual({path.suffix for path in files}, {".md", ".typ", ".pdf"})
            before = {path.name: (path.stat().st_ino, path.stat().st_mtime_ns, hashlib.sha256(path.read_bytes()).hexdigest()) for path in files}

            identical = run_cli(*base, "--confirm")
            self.assertEqual(identical.returncode, 0, identical.stderr)
            self.assertEqual(parse_json(identical)["publication"], "identical")
            after = {path.name: (path.stat().st_ino, path.stat().st_mtime_ns, hashlib.sha256(path.read_bytes()).hexdigest()) for path in public_files(delivery)}
            self.assertEqual(after, before)
            self.assertFalse((delivery / "history").exists())

    def test_target_patch_preserves_generic_and_batch_expands_all_confirmed_targets(self) -> None:
        generic = SKILL_ROOT / "fixtures" / "valid-no-photo.md"
        targeted = SKILL_ROOT / "fixtures" / "valid-multi-target.md"
        with tempfile.TemporaryDirectory() as temporary:
            delivery = Path(temporary) / "delivery"
            first = run_cli(
                "render", "--input", str(generic), "--generic", "--delivery-root", str(delivery),
                "--photo-mode", "no-photo", "--confirm",
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            targeted_run = run_cli(
                "render", "--input", str(targeted), "--target", "target-robot-001",
                "--delivery-root", str(delivery), "--photo-mode", "no-photo", "--confirm",
            )
            self.assertEqual(targeted_run.returncode, 0, targeted_run.stderr)
            self.assertEqual(len(public_files(delivery)), 18)

            batch_root = Path(temporary) / "batch"
            batch = run_cli(
                "batch", "--input", str(targeted), "--delivery-root", str(batch_root),
                "--photo-mode", "no-photo", "--confirm",
            )
            self.assertEqual(batch.returncode, 0, batch.stderr)
            payload = parse_json(batch)
            self.assertEqual(payload["mode"], "authority")
            self.assertEqual(payload["versions"], ["generic", "target-robot-001", "target-energy-002"])
            self.assertEqual(len(public_files(batch_root)), 27)

    def test_batch_lists_and_confirms_removed_old_target_triples(self) -> None:
        source = SKILL_ROOT / "fixtures" / "valid-multi-target.md"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            delivery = root / "delivery"
            initial = run_cli(
                "batch", "--input", str(source), "--delivery-root", str(delivery),
                "--photo-mode", "no-photo", "--confirm",
            )
            self.assertEqual(initial.returncode, 0, initial.stderr)
            reduced = root / "reduced.md"
            text = source.read_text(encoding="utf-8")
            text = text.split("\n### 某储能公司\n", 1)[0].rstrip() + "\n"
            reduced.write_text(text, encoding="utf-8")

            preview = run_cli(
                "batch", "--input", str(reduced), "--delivery-root", str(delivery),
                "--photo-mode", "no-photo",
            )
            self.assertEqual(preview.returncode, 0, preview.stderr)
            payload = parse_json(preview)
            self.assertEqual(len(payload["removed"]), 3)
            self.assertEqual(len(public_files(delivery)), 27)

            confirmed = run_cli(
                "batch", "--input", str(reduced), "--delivery-root", str(delivery),
                "--photo-mode", "no-photo", "--confirm",
            )
            self.assertEqual(confirmed.returncode, 0, confirmed.stderr)
            self.assertEqual(len(public_files(delivery)), 18)
            archived = delivery / "history" / "001"
            self.assertTrue(archived.is_dir())
            self.assertEqual(len(tuple(archived.iterdir())), 3)

    def test_not_applicable_is_repeatable_three_argv_and_rejects_invalid_scope_or_reason(self) -> None:
        source = SKILL_ROOT / "fixtures" / "targeting" / "multi-state-targets.md"
        target_id = "target-robot-001"
        condition_id = condition_id_for_requirement(target_id, "具有2年设备经验")
        with tempfile.TemporaryDirectory() as temporary:
            delivery = str(Path(temporary) / "delivery")
            base = (
                "render", "--input", str(source), "--target", target_id,
                "--delivery-root", delivery, "--photo-mode", "no-photo",
            )
            valid = run_cli(*base, "--not-applicable", target_id, condition_id, "招聘方确认本批次不适用")
            self.assertEqual(valid.returncode, 0, valid.stderr)
            self.assertNotIn("招聘方确认本批次不适用", valid.stdout)
            self.assertEqual(parse_json(valid)["conditions"]["not-applicable"], 1)

            invalid_arguments = (
                ("--not-applicable", target_id, condition_id, " "),
                ("--not-applicable", target_id, condition_id, "x" * 201),
                ("--not-applicable", target_id, condition_id, "含\n换行"),
                ("--not-applicable", "target-missing", condition_id, "理由"),
                ("--not-applicable", target_id, "condition-missing", "理由"),
                ("--not-applicable", target_id, condition_id, "理由", "--not-applicable", target_id, condition_id, "理由"),
            )
            for arguments in invalid_arguments:
                with self.subTest(arguments=arguments):
                    completed = run_cli(*base, *arguments)
                    self.assertNotEqual(completed.returncode, 0)
                    self.assertNotIn("Traceback", completed.stderr)
                    self.assertLess(len(completed.stderr), 1600)
                    self.assertEqual(parse_json(completed)["code"], "TARGET_CONDITION_INVALID")

            generic = run_cli(
                "render", "--input", str(SKILL_ROOT / "fixtures" / "valid-no-photo.md"), "--generic",
                "--delivery-root", delivery, "--photo-mode", "no-photo",
                "--not-applicable", target_id, condition_id, "理由",
            )
            self.assertNotEqual(generic.returncode, 0)
            self.assertEqual(parse_json(generic)["code"], "TARGET_CONDITION_INVALID")


if __name__ == "__main__":
    unittest.main(verbosity=2)
