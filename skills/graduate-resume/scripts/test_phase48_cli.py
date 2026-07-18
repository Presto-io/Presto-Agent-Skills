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


def run_cli(*arguments: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *arguments],
        cwd=SKILL_ROOT.parent.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
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
        targeted = SKILL_ROOT / "fixtures" / "valid-multi-target.md"
        with tempfile.TemporaryDirectory() as temporary:
            delivery = Path(temporary) / "delivery"
            first = run_cli(
                "render", "--input", str(targeted), "--generic", "--delivery-root", str(delivery),
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
            removed_archives = tuple(path for path in archived.iterdir() if "某储能公司" in path.name)
            self.assertEqual(len(removed_archives), 3)
            self.assertTrue(all(len(tuple(path.iterdir())) == 3 for path in removed_archives))

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

    def test_gap_allow_is_per_target_unknown_is_warning_and_runtime_failure_is_bounded(self) -> None:
        source = SKILL_ROOT / "fixtures" / "targeting" / "multi-state-targets.md"
        with tempfile.TemporaryDirectory() as temporary:
            delivery = Path(temporary) / "delivery"
            base = (
                "batch", "--input", str(source), "--delivery-root", str(delivery),
                "--photo-mode", "no-photo",
            )
            blocked = run_cli(*base)
            self.assertNotEqual(blocked.returncode, 0)
            self.assertEqual(parse_json(blocked)["code"], "TARGET_GAP_NOT_ALLOWED")
            self.assertEqual(public_files(delivery), ())

            allowed = run_cli(*base, "--allow-gap-target", "target-device-002")
            self.assertEqual(allowed.returncode, 0, allowed.stderr)
            payload = parse_json(allowed)
            conditions = payload["target_conditions"]
            self.assertTrue(conditions["target-device-002"]["gap_allowed"])
            self.assertFalse(conditions["target-robot-001"]["gap_allowed"])
            self.assertGreater(conditions["target-robot-001"]["warning_count"], 0)
            self.assertEqual(public_files(delivery), ())

            environment = dict(os.environ)
            environment["PATH"] = ""
            failed = run_cli(*base, "--allow-gap-target", "target-device-002", "--confirm", env=environment)
            self.assertNotEqual(failed.returncode, 0)
            self.assertNotIn("Traceback", failed.stderr)
            self.assertNotIn(str(delivery), failed.stderr)
            self.assertLess(len(failed.stderr), 1600)
            self.assertEqual(parse_json(failed)["code"], "FONT_MANIFEST_INVALID")
            self.assertEqual(public_files(delivery), ())


class DocumentationContractTests(unittest.TestCase):
    def test_canonical_workflow_reference_and_template_are_synchronized(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract = (SKILL_ROOT / "references" / "targeted-render-delivery-contract.md").read_text(encoding="utf-8")
        template = (SKILL_ROOT / "templates" / "graduate-resume.md").read_text(encoding="utf-8")

        for needle in (
            "render --generic", "render --target <stable-id>", "generic + all confirmed targets",
            "--not-applicable <target-id> <condition-id> <reason>", "--confirm",
            "added/updated/unchanged/removed", "失败不改变 current/history", "Phase 49",
        ):
            self.assertIn(needle, skill)
        for runtime in ("Codex", "Claude Code", "Gemini CLI", "OpenCode", "OpenClaw", "Hermes Agent"):
            self.assertIn(runtime, skill)
        self.assertNotIn("AskUserQuestion", skill)
        self.assertNotIn("tool_call", skill)

        for decision in range(1, 20):
            self.assertIn(f"D-{decision:02d}", contract)
        for needle in (
            "education_level", "major_exact", "certificate_exact", "fresh_graduate_status",
            "meets", "gap", "unknown", "not-applicable", "1..200 Unicode code points",
            "graduate-resume-delivery/v1", "conservative", "modern", "expressive",
            "Markdown/Typst/PDF", "mode=patch", "mode=authority", "true no-op",
            "updated/removed", "rollback", "owned hidden evidence", "413 × 579", "300 PPI",
            "EXIF", "内嵌 bytes", "history", "manifest sidecar", "Phase 49",
        ):
            self.assertIn(needle, contract)
        self.assertIn("--not-applicable <target-id> <condition-id> <reason>", contract)
        self.assertNotIn("override.json", contract)
        self.assertEqual(contract.count("TARGET=JSON"), 1)

        for needle in (
            "id=target-grid-001", "来源：校园招聘公告", "截至日期：2026-07-17",
            "已确认：是", "学历要求：大专", "专业要求：电气自动化技术",
            "证书要求：低压电工证", "应届毕业生",
        ):
            self.assertIn(needle, template)
        self.assertNotIn("status=pending", template)
        self.assertNotIn("gap_allowed", template)
        self.assertNotIn("not-applicable", template)


class Phase48AcceptanceRegistryTests(unittest.TestCase):
    def test_acceptance_registry_is_literal_complete_and_observed(self) -> None:
        required = (
            "test_targeting_contract.TargetingProjectionTests.test_projection_is_deterministic_reorder_safe_and_immutable",
            "test_targeting_contract.TargetingProjectionTests.test_invalid_overrides_and_unsatisfiable_budget_fail_closed",
            "test_targeting_contract.HardConditionTests.test_controlled_predicates_produce_four_states_without_similarity_claims",
            "test_render_contract.FinalMarkdownContractTests.test_round_trip_is_deterministic_and_tamper_evident",
            "test_render_contract.TypstConsumerContractTests.test_photo_normalization_is_deterministic_and_embedded",
            "test_render_contract.RenderMatrixContractTests.test_safe_stem_normalizes_and_rejects_collision",
            "test_delivery_transaction.DiscoveryFailClosedTests.test_unknown_partial_symlink_directory_fifo_and_stale_work_fail",
            "test_delivery_transaction.PublicationTransactionTests.test_authority_requires_unchanged_approval_and_patch_preserves_other_stems",
            "test_delivery_transaction.PublicationTransactionTests.test_identical_does_not_create_history_or_touch_inode_mtime",
            "test_delivery_transaction.PublicationTransactionTests.test_every_fault_and_handled_signal_restore_entire_current_set",
            "test_phase48_cli.PublicCliContractTests.test_gap_allow_is_per_target_unknown_is_warning_and_runtime_failure_is_bounded",
            "test_phase48_cli.PublicCliContractTests.test_batch_lists_and_confirms_removed_old_target_triples",
        )
        self.assertEqual(PHASE48_ACCEPTANCE_REGISTRY, required)
        observed = run_phase48_acceptance_registry()
        self.assertEqual(observed["required"], list(required))
        self.assertEqual(observed["called"], list(required))
        self.assertEqual(observed["status"], "passed")
        self.assertNotIn("skip", json.dumps(observed).lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
