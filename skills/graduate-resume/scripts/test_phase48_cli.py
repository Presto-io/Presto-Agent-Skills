from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import graduate_resume_cli as cli
from graduate_resume_targeting import condition_id_for_requirement


SKILL_ROOT = Path(__file__).resolve().parent.parent
CLI = SKILL_ROOT / "scripts" / "graduate_resume_cli.py"
THEME_LABELS = ("保守稳妥", "现代简洁", "个性设计")
PHASE48_ACCEPTANCE_REGISTRY = (
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
    "test_phase48_cli.PublicCliContractTests.test_photo_triple_recompiles_after_move_without_source_photo",
    "test_phase48_cli.PublicCliContractTests.test_one_typst_runtime_context_is_shared_by_all_consumers",
    "test_phase48_cli.PublicCliContractTests.test_cleanup_failures_are_bounded_and_preserve_published_or_rolled_back_current",
)


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


def run_reviewed(*arguments: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    preview = run_cli(*arguments, env=env)
    if preview.returncode != 0:
        return preview
    digest = parse_json(preview)["approval_digest"]
    return run_cli(*arguments, "--confirm", "--approval-digest", str(digest), env=env)


def parse_json(completed: subprocess.CompletedProcess[str]) -> dict[str, object]:
    stream = completed.stdout if completed.returncode == 0 else completed.stderr
    return json.loads(stream)


def public_files(root: Path) -> tuple[Path, ...]:
    return tuple(sorted(path for path in root.iterdir() if path.is_file())) if root.exists() else ()


def recursive_snapshot(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def run_phase48_acceptance_registry() -> dict[str, object]:
    called: list[str] = []
    failures: list[str] = []
    for test_id in PHASE48_ACCEPTANCE_REGISTRY:
        called.append(test_id)
        suite = unittest.defaultTestLoader.loadTestsFromName(test_id)
        result = unittest.TestResult()
        suite.run(result)
        if result.failures or result.errors or result.skipped or result.unexpectedSuccesses:
            failures.append(test_id)
    return {
        "status": "passed" if not failures else "failed",
        "scope": "phase-48-local-development-only",
        "required": list(PHASE48_ACCEPTANCE_REGISTRY),
        "called": called,
        "failures": failures,
    }


class PublicCliContractTests(unittest.TestCase):
    @staticmethod
    def _publication_args(source: Path, delivery: Path, *, command: str = "render") -> argparse.Namespace:
        return argparse.Namespace(
            command=command,
            input=str(source),
            delivery_root=str(delivery),
            evidence_root=None,
            retain=[],
            exclude=[],
            pin=[],
            not_applicable=[],
            allow_gap_target=[],
            pages="auto",
            photo_mode="no-photo",
            assets_root=None,
            confirm=False,
            approval_digest=None,
            generic=True,
            target=None,
        )

    def test_validate_rejects_duplicate_fields_urls_and_unrenderable_nested_values(self) -> None:
        source = SKILL_ROOT / "fixtures" / "valid-photo-single-target.md"
        original = source.read_text(encoding="utf-8").replace(
            "  status: verified\n", "  status: verified\n  directions:\n    - 设备运维\n", 1,
        )
        cases = {
            "duplicate": original.replace("- 专业：机电一体化技术", "- 专业：机电一体化技术\n- 专业：工业机器人技术", 1),
            "source-url": original.replace("- 来源：校园宣讲会资料", "- 来源：https://jobs.example.test/private?id=123"),
            "requirements-missing": original.replace("- 招聘要求：持有低压电工证\n", ""),
            "nested-non-string": original.replace("  directions:\n    - 设备运维\n", "  directions: [123]\n"),
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, content in cases.items():
                with self.subTest(case=name):
                    path = root / f"{name}.md"
                    path.write_text(content, encoding="utf-8")
                    completed = run_cli("validate", "--input", str(path))
                    self.assertEqual(completed.returncode, 64 if name == "duplicate" else 2, completed.stderr)
                    payload = parse_json(completed)
                    self.assertEqual(payload["code"], "MARKDOWN_INVALID" if name == "duplicate" else "VALIDATION_FAILED")

    def test_targeted_photo_fixture_renders_from_its_controlled_asset_root(self) -> None:
        source = SKILL_ROOT / "fixtures" / "render" / "targeted-photo.md"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence = root / "evidence"
            evidence.mkdir()
            completed = run_reviewed(
                "render", "--input", str(source), "--target", "target-photo-001",
                "--delivery-root", str(root / "delivery"), "--evidence-root", str(evidence),
                "--assets-root", str(source.parent), "--photo-mode", "photo",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = parse_json(completed)
            self.assertEqual(payload["photo_mode"], "photo")
            self.assertEqual(len(public_files(root / "delivery")), 9)

    def test_one_typst_runtime_context_is_shared_by_all_consumers(self) -> None:
        import graduate_resume_typst_runtime as runtime

        source_fixture = SKILL_ROOT / "fixtures" / "valid-generic-no-target.md"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "photo.md"
            source.write_text(
                source_fixture.read_text(encoding="utf-8").replace(
                    "fixtures/media/student-photo.jpg",
                    "fixtures/layout/media/student-photo.jpg",
                ),
                encoding="utf-8",
            )
            original_resolve = runtime.resolve_typst_executable
            original_run = runtime.TypstExecutable.run
            resolve_calls: list[object] = []
            observations: list[tuple[int, str, int, int, str, tuple[str, ...]]] = []
            runtime_link = root / "typst"
            fake_runtime = root / "typst-fake"
            fake_runtime.write_text("#!/bin/sh\nprintf 'typst 9.9.0\\n'\n", encoding="utf-8")
            fake_runtime.chmod(0o755)

            def capture_resolve(*args: object, **kwargs: object):
                resolve_calls.append((args, kwargs))
                runtime_link.unlink(missing_ok=True)
                runtime_link.symlink_to(Path("/opt/homebrew/bin/typst"))

                def replace_source() -> None:
                    runtime_link.unlink()
                    runtime_link.symlink_to(fake_runtime)

                return original_resolve(runtime_link, _after_source_verified=replace_source)

            def capture_run(executable, arguments, **kwargs):
                observations.append((
                    id(executable),
                    str(executable.snapshot_path),
                    executable.snapshot_dev,
                    executable.snapshot_ino,
                    executable.snapshot_sha256,
                    tuple(arguments),
                ))
                return original_run(executable, arguments, **kwargs)

            args = self._publication_args(source, root / "delivery")
            args.photo_mode = "photo"
            args.assets_root = str(SKILL_ROOT)
            output = io.StringIO()
            with (
                mock.patch.object(runtime, "resolve_typst_executable", side_effect=capture_resolve),
                mock.patch.object(runtime.TypstExecutable, "run", autospec=True, side_effect=capture_run),
                contextlib.redirect_stdout(output),
            ):
                self.assertEqual(cli._command_publication(args, batch=False), 0)
            self.assertEqual(len(resolve_calls), 1)
            self.assertEqual(len({item[:5] for item in observations}), 1)
            commands = [item[-1] for item in observations]
            self.assertEqual(sum(command[:1] == ("--version",) for command in commands), 1)
            self.assertEqual(sum(command[:1] == ("fonts",) for command in commands), 1)
            self.assertEqual(sum(command[:1] == ("compile",) for command in commands), 4)

            plan_args = argparse.Namespace(
                input=str(source),
                theme=None,
                assets_root=str(SKILL_ROOT),
                photo_mode="photo",
                pages="auto",
            )
            resolve_calls.clear()
            with mock.patch.object(runtime, "resolve_typst_executable", side_effect=capture_resolve), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cli.command_plan(plan_args), 0)
            self.assertEqual(len(resolve_calls), 1)

            args.command = "batch"
            resolve_calls.clear()
            with mock.patch.object(runtime, "resolve_typst_executable", side_effect=capture_resolve), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cli._command_publication(args, batch=True), 0)
            self.assertEqual(len(resolve_calls), 1)

            resolve_calls.clear()
            with mock.patch.object(runtime, "resolve_typst_executable", side_effect=capture_resolve), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cli.command_validate(argparse.Namespace(input=str(source))), 0)
                self.assertEqual(cli.command_target(argparse.Namespace(input=str(source))), 0)
            self.assertEqual(resolve_calls, [])

    def test_cleanup_failures_are_bounded_and_preserve_published_or_rolled_back_current(self) -> None:
        import graduate_resume_delivery as delivery_module

        source_fixture = SKILL_ROOT / "fixtures" / "valid-no-photo.md"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "resume.md"
            source.write_bytes(source_fixture.read_bytes())
            delivery = root / "delivery"
            preview_args = self._publication_args(source, delivery)
            preview_output = io.StringIO()
            with contextlib.redirect_stdout(preview_output):
                self.assertEqual(cli._command_publication(preview_args, batch=False), 0)
            preview = json.loads(preview_output.getvalue())
            publish_args = self._publication_args(source, delivery)
            publish_args.confirm = True
            publish_args.approval_digest = preview["approval_digest"]
            original_close = delivery_module.DeliverySession.close

            def cleanup_fault(session) -> None:
                original_close(session)
                raise delivery_module.DeliveryError("cleanup failed: rmdir .work errno=5")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with (
                mock.patch.object(cli, "parse_args", return_value=publish_args),
                mock.patch.object(delivery_module.DeliverySession, "close", autospec=True, side_effect=cleanup_fault),
                contextlib.redirect_stdout(stdout),
                contextlib.redirect_stderr(stderr),
            ):
                self.assertNotEqual(cli.main(), 0)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(json.loads(stderr.getvalue())["code"], "DELIVERY_PREFLIGHT_FAILED")
            self.assertLess(len(stderr.getvalue()), 1600)
            self.assertEqual(len(public_files(delivery)), 9)

            source.write_bytes(source.read_bytes() + b"\n")
            update_args = self._publication_args(source, delivery)
            update_output = io.StringIO()
            with contextlib.redirect_stdout(update_output):
                self.assertEqual(cli._command_publication(update_args, batch=False), 0)
            update = json.loads(update_output.getvalue())
            update_args.confirm = True
            update_args.approval_digest = update["approval_digest"]
            before = recursive_snapshot(delivery)
            stdout = io.StringIO()
            stderr = io.StringIO()
            with (
                mock.patch.object(cli, "parse_args", return_value=update_args),
                mock.patch.object(delivery_module.DeliverySession, "close", autospec=True, side_effect=cleanup_fault),
                mock.patch.dict(os.environ, {delivery_module.FAULT_ENV: "after_publish_file_1"}),
                contextlib.redirect_stdout(stdout),
                contextlib.redirect_stderr(stderr),
            ):
                self.assertNotEqual(cli.main(), 0)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(json.loads(stderr.getvalue())["code"], "DELIVERY_PREFLIGHT_FAILED")
            self.assertEqual(recursive_snapshot(delivery), before)

    def test_publication_photo_consumes_resolver_snapshot_without_path_reopen(self) -> None:
        from graduate_resume_layout import ResolvedPhotoAsset

        document = cli.load_resume(str(SKILL_ROOT / "fixtures" / "valid-generic-no-target.md"))
        source = b"\xff\xd8descriptor-snapshot\xff\xd9"
        resolved = ResolvedPhotoAsset(
            "missing-after-resolve.jpg",
            source,
            hashlib.sha256(source).hexdigest(),
            11,
            22,
        )
        args = argparse.Namespace(photo_mode="photo", assets_root="/definitely/missing")
        with mock.patch("graduate_resume_layout.resolve_layout_photo", return_value=resolved), mock.patch(
            "graduate_resume_layout.validate_font_manifest", return_value="a" * 64
        ):
            photo_mode, photo_bytes, feedback_photo, font_hash = cli._resolve_publication_photo(args, document, object())
        self.assertEqual(photo_mode, "photo")
        self.assertEqual(photo_bytes, source)
        self.assertEqual(feedback_photo.logical_path, "embedded-normalized.png")
        self.assertEqual(font_hash, "a" * 64)

    def test_canonical_reader_rejects_unsafe_inputs_and_handles_short_reads(self) -> None:
        source = SKILL_ROOT / "fixtures" / "valid-no-photo.md"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            delivery = root / "delivery"
            delivery.mkdir()
            initial = recursive_snapshot(delivery)
            real = root / "real.md"
            real.write_bytes(source.read_bytes())
            linked = root / "linked.md"
            linked.symlink_to(real)
            directory = root / "directory.md"
            directory.mkdir()
            fifo = root / "fifo.md"
            os.mkfifo(fifo)
            oversized = root / "oversized.md"
            oversized.write_bytes(source.read_bytes() + b" " * (4 * 1024 * 1024))
            invalid_utf8 = root / "invalid-utf8.md"
            invalid_utf8.write_bytes(source.read_bytes() + b"\xff")

            for candidate in (linked, directory, fifo, oversized, invalid_utf8):
                with self.subTest(candidate=candidate.name):
                    completed = run_cli(
                        "render", "--input", str(candidate), "--generic",
                        "--delivery-root", str(delivery), "--photo-mode", "no-photo",
                    )
                    self.assertNotEqual(completed.returncode, 0)
                    self.assertEqual(parse_json(completed)["code"], "CANONICAL_INPUT_INVALID")
                    self.assertNotIn(str(candidate), completed.stderr)
                    self.assertNotIn("Traceback", completed.stderr)
                    self.assertLess(len(completed.stderr), 1600)
                    self.assertEqual(recursive_snapshot(delivery), initial)

            original_read = os.read

            def short_read(file_descriptor: int, size: int) -> bytes:
                return original_read(file_descriptor, min(size, 7))

            with mock.patch.object(cli.os, "read", side_effect=short_read) as read_spy:
                document = cli.load_resume(str(real))
            self.assertGreater(read_spy.call_count, 1)
            self.assertEqual(document.source_bytes, source.read_bytes())
            self.assertEqual(document.source_sha256, hashlib.sha256(document.source_bytes).hexdigest())

    def test_loaded_canonical_snapshot_survives_path_byte_and_symlink_swaps(self) -> None:
        import graduate_resume_delivery as delivery_module
        import graduate_resume_render as render_module
        from graduate_resume_final_markdown import load_final_resume

        source = SKILL_ROOT / "fixtures" / "valid-no-photo.md"
        for swap_kind in ("bytes", "symlink"):
            with self.subTest(swap_kind=swap_kind), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                canonical = root / "resume.md"
                original_bytes = source.read_bytes()
                canonical.write_bytes(original_bytes)
                replacement = root / "replacement.md"
                replacement.write_bytes(original_bytes.replace("王宁".encode(), "李明".encode()))
                expected_hash = hashlib.sha256(original_bytes).hexdigest()
                captured: dict[str, object] = {}
                original_publication_view = cli.publication_fact_view
                original_render = render_module.render_candidate_matrix
                original_spec = delivery_module.DeliverySpec
                original_path_read_bytes = Path.read_bytes

                def swap_after_load(data: dict[str, object]) -> dict[str, object]:
                    view = original_publication_view(data)
                    canonical.unlink()
                    if swap_kind == "bytes":
                        canonical.write_bytes(replacement.read_bytes())
                    else:
                        canonical.symlink_to(replacement)
                    return view

                def capture_render(*args: object, **kwargs: object) -> object:
                    captured["render_hash"] = kwargs["canonical_hash"]
                    result = original_render(*args, **kwargs)
                    markdown = next(result.candidate_root.glob("*.md"))
                    captured["final_hash"] = load_final_resume(markdown).canonical_hash
                    return result

                def capture_spec(*args: object, **kwargs: object) -> object:
                    spec = original_spec(*args, **kwargs)
                    captured["approval_hash"] = spec.canonical_hash
                    return spec

                def forbid_canonical_path_read(path: Path) -> bytes:
                    if path == canonical:
                        raise AssertionError("publication must not reread the canonical path")
                    return original_path_read_bytes(path)

                args = argparse.Namespace(
                    input=str(canonical), delivery_root=str(root / "delivery"), evidence_root=None,
                    retain=[], exclude=[], pin=[], not_applicable=[], allow_gap_target=[], pages="auto",
                    photo_mode="no-photo", assets_root=None, confirm=False, approval_digest=None,
                    generic=True, target=None,
                )
                output = io.StringIO()
                with (
                    mock.patch.object(cli, "publication_fact_view", side_effect=swap_after_load),
                    mock.patch.object(render_module, "render_candidate_matrix", side_effect=capture_render),
                    mock.patch.object(delivery_module, "DeliverySpec", side_effect=capture_spec),
                    mock.patch.object(Path, "read_bytes", forbid_canonical_path_read),
                    contextlib.redirect_stdout(output),
                ):
                    self.assertEqual(cli._command_publication(args, batch=False), 0)
                self.assertEqual(cli.load_resume(str(replacement)).data["candidate"]["name"], "李明")
                self.assertEqual(captured["render_hash"], expected_hash)
                self.assertEqual(captured["final_hash"], expected_hash)
                self.assertEqual(captured["approval_hash"], expected_hash)
                self.assertRegex(json.loads(output.getvalue())["approval_digest"], r"^[0-9a-f]{64}$")

    def test_metadata_contract_rejects_missing_unknown_empty_and_duplicate_fields(self) -> None:
        non_target_source = (SKILL_ROOT / "fixtures" / "valid-no-photo.md").read_text(encoding="utf-8")
        target_source = (SKILL_ROOT / "fixtures" / "valid-multi-target.md").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            delivery = root / "delivery"
            baseline = run_reviewed(
                "render", "--input", str(SKILL_ROOT / "fixtures" / "valid-no-photo.md"), "--generic",
                "--delivery-root", str(delivery), "--photo-mode", "no-photo",
            )
            self.assertEqual(baseline.returncode, 0, baseline.stderr)
            before = recursive_snapshot(delivery)

            cases = {
                "missing-id": non_target_source.replace(
                    "id=edu-001 status=verified", "status=verified",
                ),
                "missing-status": non_target_source.replace(
                    "id=edu-001 status=verified", "id=edu-001",
                ),
                "misspelled-status": non_target_source.replace(
                    "id=edu-001 status=verified", "id=edu-001 stats=verified",
                ),
                "extra-key": non_target_source.replace(
                    "id=edu-001 status=verified", "id=edu-001 status=verified note=reviewed",
                ),
                "empty-value": non_target_source.replace(
                    "id=edu-001 status=verified", "id=edu-001 status=",
                ),
                "duplicate-id": non_target_source.replace(
                    "id=edu-001 status=verified", "id=edu-001 id=edu-shadow status=verified",
                ),
                "duplicate-status": non_target_source.replace(
                    "id=edu-001 status=verified", "id=edu-001 status=pending status=verified",
                ),
                "duplicate-comment": non_target_source.replace(
                    "<!-- resume: id=edu-001 status=verified -->",
                    "<!-- resume: id=edu-001 status=verified -->\n<!-- resume: id=edu-shadow status=verified -->",
                ),
                "target-status": target_source.replace(
                    "id=target-robot-001", "id=target-robot-001 status=verified",
                ),
                "target-extra-key": target_source.replace(
                    "id=target-robot-001", "id=target-robot-001 note=reviewed",
                ),
                "target-duplicate-id": target_source.replace(
                    "id=target-robot-001", "id=target-robot-001 id=target-shadow-002",
                ),
            }
            for name, text in cases.items():
                with self.subTest(name=name):
                    candidate = root / f"{name}.md"
                    candidate.write_text(text, encoding="utf-8")
                    completed = run_cli(
                        "render", "--input", str(candidate), "--generic",
                        "--delivery-root", str(delivery), "--photo-mode", "no-photo",
                    )
                    self.assertNotEqual(completed.returncode, 0)
                    self.assertEqual(recursive_snapshot(delivery), before)
                    self.assertNotIn("Traceback", completed.stderr)
                    self.assertNotIn("王宁", completed.stderr)
                    self.assertNotIn("周凯", completed.stderr)
                    self.assertNotIn(str(candidate), completed.stderr)
                    self.assertLess(len(completed.stderr), 1600)

        production = CLI.read_text(encoding="utf-8")
        self.assertNotIn('metadata.get("status", "verified")', production)

    def test_cross_process_preflight_digest_is_required_for_confirm_and_stale_input_fails(self) -> None:
        source = SKILL_ROOT / "fixtures" / "valid-no-photo.md"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            canonical = root / "resume.md"
            canonical.write_bytes(source.read_bytes())
            delivery = root / "delivery"
            base = (
                "render", "--input", str(canonical), "--generic",
                "--delivery-root", str(delivery), "--photo-mode", "no-photo",
            )
            preview = run_cli(*base)
            self.assertEqual(preview.returncode, 0, preview.stderr)
            digest = parse_json(preview)["approval_digest"]
            self.assertRegex(digest, r"^[0-9a-f]{64}$")
            self.assertEqual(recursive_snapshot(delivery), {})

            missing = run_cli(*base, "--confirm")
            detached = run_cli(*base, "--approval-digest", digest)
            malformed = run_cli(*base, "--confirm", "--approval-digest", "A" * 64)
            for completed in (missing, detached, malformed):
                self.assertNotEqual(completed.returncode, 0)
                self.assertEqual(recursive_snapshot(delivery), {})

            changed_candidate = run_cli(
                *base, "--pages", "1", "--confirm", "--approval-digest", digest,
            )
            self.assertNotEqual(changed_candidate.returncode, 0)
            self.assertEqual(recursive_snapshot(delivery), {})
            original = canonical.read_bytes()
            canonical.write_bytes(original + b"\n")
            stale = run_cli(*base, "--confirm", "--approval-digest", digest)
            self.assertNotEqual(stale.returncode, 0)
            self.assertEqual(recursive_snapshot(delivery), {})
            canonical.write_bytes(original)

            confirmed = run_cli(*base, "--confirm", "--approval-digest", digest)
            self.assertEqual(confirmed.returncode, 0, confirmed.stderr)
            self.assertEqual(parse_json(confirmed)["approval_digest"], digest)

    def test_reviewed_digest_binds_delivery_and_evidence_root_path_and_identity(self) -> None:
        generic = SKILL_ROOT / "fixtures" / "valid-no-photo.md"
        targeted = SKILL_ROOT / "fixtures" / "targeting" / "multi-state-targets.md"
        for case in ("alternate", "inode-swap", "symlink-swap"):
            with self.subTest(root=case), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                delivery = root / "delivery"
                base = (
                    "render", "--input", str(generic), "--generic",
                    "--delivery-root", str(delivery), "--photo-mode", "no-photo",
                )
                preview = run_cli(*base)
                self.assertEqual(preview.returncode, 0, preview.stderr)
                digest = str(parse_json(preview)["approval_digest"])
                confirm_base = base
                displaced = root / "displaced"
                if case == "alternate":
                    confirm_base = (
                        "render", "--input", str(generic), "--generic",
                        "--delivery-root", str(root / "other-delivery"), "--photo-mode", "no-photo",
                    )
                else:
                    delivery.rename(displaced)
                    if case == "inode-swap":
                        delivery.mkdir()
                    else:
                        delivery.symlink_to(displaced, target_is_directory=True)
                completed = run_cli(
                    *confirm_base, "--confirm", "--approval-digest", digest,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertEqual(recursive_snapshot(displaced), {})
                if delivery.exists() and not delivery.is_symlink():
                    self.assertEqual(recursive_snapshot(delivery), {})

        for case in ("alternate", "inode-swap", "symlink-swap"):
            with self.subTest(evidence=case), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                delivery = root / "delivery"
                evidence = root / "evidence"
                base = (
                    "render", "--input", str(targeted), "--target", "target-robot-001",
                    "--delivery-root", str(delivery), "--evidence-root", str(evidence),
                    "--photo-mode", "no-photo",
                )
                preview = run_cli(*base)
                self.assertEqual(preview.returncode, 0, preview.stderr)
                digest = str(parse_json(preview)["approval_digest"])
                confirm_base = base
                displaced = root / "evidence-displaced"
                if case == "alternate":
                    confirm_base = (
                        "render", "--input", str(targeted), "--target", "target-robot-001",
                        "--delivery-root", str(delivery), "--evidence-root", str(root / "other-evidence"),
                        "--photo-mode", "no-photo",
                    )
                else:
                    evidence.rename(displaced)
                    if case == "inode-swap":
                        evidence.mkdir()
                    else:
                        evidence.symlink_to(displaced, target_is_directory=True)
                completed = run_cli(
                    *confirm_base, "--confirm", "--approval-digest", digest,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertEqual(recursive_snapshot(delivery), {})

    def test_reviewed_digest_rejects_photo_bytes_changed_after_preflight(self) -> None:
        from PIL import Image

        fixture = SKILL_ROOT / "fixtures" / "valid-generic-no-target.md"
        original_photo = SKILL_ROOT / "fixtures" / "layout" / "media" / "student-photo.jpg"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "resume.md"
            source.write_text(
                fixture.read_text(encoding="utf-8").replace(
                    "fixtures/media/student-photo.jpg", "photo.jpg",
                ),
                encoding="utf-8",
            )
            photo = root / "photo.jpg"
            photo.write_bytes(original_photo.read_bytes())
            delivery = root / "delivery"
            base = (
                "render", "--input", str(source), "--generic",
                "--delivery-root", str(delivery), "--assets-root", str(root),
                "--photo-mode", "photo",
            )
            preview = run_cli(*base)
            self.assertEqual(preview.returncode, 0, preview.stderr)
            digest = str(parse_json(preview)["approval_digest"])
            with Image.open(photo) as image:
                changed = image.convert("RGB")
                red, green, blue = changed.getpixel((0, 0))
                changed.putpixel((0, 0), ((red + 1) % 256, green, blue))
                changed.save(photo, format="JPEG", quality=95)
            completed = run_cli(
                *base, "--confirm", "--approval-digest", digest,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(recursive_snapshot(delivery), {})

    def test_render_and_batch_share_bounded_target_conditions_and_persist_private_evidence(self) -> None:
        source = SKILL_ROOT / "fixtures" / "targeting" / "multi-state-targets.md"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            render_evidence = root / "render-evidence"
            batch_evidence = root / "batch-evidence"
            render_evidence.mkdir()
            batch_evidence.mkdir()
            render_arguments = (
                "render", "--input", str(source), "--target", "target-robot-001",
                "--delivery-root", str(root / "render-delivery"),
                "--evidence-root", str(render_evidence), "--photo-mode", "no-photo",
            )
            preview = run_cli(*render_arguments)
            self.assertEqual(preview.returncode, 0, preview.stderr)
            self.assertFalse(tuple(render_evidence.iterdir()))
            rendered = run_reviewed(*render_arguments)
            batch_arguments = (
                "batch", "--input", str(source),
                "--delivery-root", str(root / "batch-delivery"),
                "--evidence-root", str(batch_evidence), "--photo-mode", "no-photo",
                "--allow-gap-target", "target-device-002",
            )
            batch_preview = run_cli(*batch_arguments)
            self.assertEqual(batch_preview.returncode, 0, batch_preview.stderr)
            self.assertFalse(tuple(batch_evidence.iterdir()))
            batched = run_reviewed(*batch_arguments)
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            self.assertEqual(batched.returncode, 0, batched.stderr)
            render_payload = parse_json(rendered)
            batch_payload = parse_json(batched)
            target_id = "target-robot-001"
            self.assertEqual(
                render_payload["target_conditions"][target_id],
                batch_payload["target_conditions"][target_id],
            )
            public_projection = render_payload["target_conditions"][target_id]
            self.assertEqual(
                set(public_projection),
                {"target_id", "conditions", "counts", "warning_count", "gap_allowed", "evidence_digest"},
            )
            self.assertTrue(public_projection["conditions"])
            self.assertTrue(all(
                set(row) == {"condition_id", "predicate", "state"}
                for row in public_projection["conditions"]
            ))
            self.assertNotIn("reason", rendered.stdout)
            self.assertNotIn("evidence_fact_ids", rendered.stdout)
            self.assertTrue(tuple(render_evidence.iterdir()))
            self.assertTrue(tuple(batch_evidence.iterdir()))
            self.assertEqual(parse_json(run_cli(
                "render", "--input", str(SKILL_ROOT / "fixtures" / "valid-no-photo.md"),
                "--generic", "--delivery-root", str(root / "generic-delivery"),
                "--photo-mode", "no-photo",
            ))["target_conditions"], {})

    def test_target_publication_requires_separate_non_symlink_evidence_root(self) -> None:
        source = SKILL_ROOT / "fixtures" / "valid-multi-target.md"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            delivery = root / "delivery"
            missing = run_cli(
                "render", "--input", str(source), "--target", "target-robot-001",
                "--delivery-root", str(delivery), "--photo-mode", "no-photo",
            )
            self.assertNotEqual(missing.returncode, 0)
            delivery.mkdir()
            (root / "evidence-link").symlink_to(root / "real-evidence", target_is_directory=True)
            for evidence in (delivery, delivery / "private", root / "evidence-link"):
                with self.subTest(evidence=evidence):
                    completed = run_cli(
                        "render", "--input", str(source), "--target", "target-robot-001",
                        "--delivery-root", str(delivery), "--evidence-root", str(evidence),
                        "--photo-mode", "no-photo",
                    )
                    self.assertNotEqual(completed.returncode, 0)
                    self.assertEqual(recursive_snapshot(delivery), {})

    def test_help_exposes_only_exact_not_applicable_contract(self) -> None:
        completed = run_cli("render", "--help")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--not-applicable TARGET_ID CONDITION_ID REASON", completed.stdout)
        self.assertIn("--allow-gap-target TARGET_ID", completed.stdout)
        self.assertNotIn("override-file", completed.stdout)
        self.assertNotIn("TARGET=JSON", completed.stdout)

    def test_publication_rejects_unverified_and_invalid_fact_ids_before_delivery(self) -> None:
        source = SKILL_ROOT / "fixtures" / "valid-no-photo.md"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            delivery = root / "delivery"
            baseline = run_reviewed(
                "render", "--input", str(source), "--generic",
                "--delivery-root", str(delivery), "--photo-mode", "no-photo",
            )
            self.assertEqual(baseline.returncode, 0, baseline.stderr)
            before = recursive_snapshot(delivery)

            cases = (
                ("declined", source.read_text(encoding="utf-8").replace("id=edu-001 status=verified", "id=edu-001 status=declined"), ()),
                ("pending", source.read_text(encoding="utf-8").replace("id=edu-001 status=verified", "id=edu-001 status=pending"), ()),
                ("invalid-id", source.read_text(encoding="utf-8").replace("edu-001", 'x\");#panic(\"injected\");#(\"'), ()),
                ("declined-override", source.read_text(encoding="utf-8").replace("id=edu-001 status=verified", "id=edu-001 status=declined"), ("--retain", "edu-001")),
            )
            for name, text, extra in cases:
                with self.subTest(name=name):
                    candidate = root / f"{name}.md"
                    candidate.write_text(text, encoding="utf-8")
                    completed = run_cli(
                        "render", "--input", str(candidate), "--generic",
                        "--delivery-root", str(delivery), "--photo-mode", "no-photo",
                        *extra,
                    )
                    self.assertNotEqual(completed.returncode, 0)
                    self.assertEqual(recursive_snapshot(delivery), before)
                    self.assertNotIn("Traceback", completed.stderr)
                    self.assertNotIn("#panic", completed.stderr)
                    self.assertNotIn(str(candidate), completed.stderr)
                    self.assertLess(len(completed.stderr), 1600)

    def test_generic_render_preflights_then_publishes_three_theme_triples_and_true_noop(self) -> None:
        source = SKILL_ROOT / "fixtures" / "valid-no-photo.md"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            delivery = root / "delivery"
            evidence = root / "evidence"
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

            published = run_cli(
                *base, "--confirm", "--approval-digest", str(payload["approval_digest"]),
            )
            self.assertEqual(published.returncode, 0, published.stderr)
            self.assertEqual(parse_json(published)["publication"], "first")
            files = public_files(delivery)
            self.assertEqual(len(files), 9)
            self.assertEqual({path.suffix for path in files}, {".md", ".typ", ".pdf"})
            before = {path.name: (path.stat().st_ino, path.stat().st_mtime_ns, hashlib.sha256(path.read_bytes()).hexdigest()) for path in files}

            identical = run_reviewed(*base)
            self.assertEqual(identical.returncode, 0, identical.stderr)
            self.assertEqual(parse_json(identical)["publication"], "identical")
            after = {path.name: (path.stat().st_ino, path.stat().st_mtime_ns, hashlib.sha256(path.read_bytes()).hexdigest()) for path in public_files(delivery)}
            self.assertEqual(after, before)
            self.assertFalse((delivery / "history").exists())

    def test_target_patch_preserves_generic_and_batch_expands_all_confirmed_targets(self) -> None:
        targeted = SKILL_ROOT / "fixtures" / "valid-multi-target.md"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            delivery = root / "delivery"
            evidence = root / "evidence"
            first = run_reviewed(
                "render", "--input", str(targeted), "--generic", "--delivery-root", str(delivery),
                "--photo-mode", "no-photo",
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            targeted_run = run_reviewed(
                "render", "--input", str(targeted), "--target", "target-robot-001",
                "--delivery-root", str(delivery), "--evidence-root", str(evidence),
                "--photo-mode", "no-photo",
            )
            self.assertEqual(targeted_run.returncode, 0, targeted_run.stderr)
            self.assertEqual(len(public_files(delivery)), 18)

            batch_root = Path(temporary) / "batch"
            batch = run_reviewed(
                "batch", "--input", str(targeted), "--delivery-root", str(batch_root),
                "--evidence-root", str(evidence), "--photo-mode", "no-photo",
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
            evidence = root / "evidence"
            initial = run_reviewed(
                "batch", "--input", str(source), "--delivery-root", str(delivery),
                "--evidence-root", str(evidence), "--photo-mode", "no-photo",
            )
            self.assertEqual(initial.returncode, 0, initial.stderr)
            reduced = root / "reduced.md"
            text = source.read_text(encoding="utf-8")
            text = text.split("\n### 某储能公司\n", 1)[0].rstrip() + "\n"
            reduced.write_text(text, encoding="utf-8")

            preview = run_cli(
                "batch", "--input", str(reduced), "--delivery-root", str(delivery),
                "--evidence-root", str(evidence), "--photo-mode", "no-photo",
            )
            self.assertEqual(preview.returncode, 0, preview.stderr)
            payload = parse_json(preview)
            self.assertEqual(len(payload["removed"]), 3)
            self.assertEqual(len(public_files(delivery)), 27)

            confirmed = run_cli(
                "batch", "--input", str(reduced), "--delivery-root", str(delivery),
                "--evidence-root", str(evidence), "--photo-mode", "no-photo",
                "--confirm", "--approval-digest", str(payload["approval_digest"]),
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
            root = Path(temporary)
            delivery = str(root / "delivery")
            evidence = str(root / "evidence")
            base = (
                "render", "--input", str(source), "--target", target_id,
                "--delivery-root", delivery, "--evidence-root", evidence,
                "--photo-mode", "no-photo",
            )
            valid = run_cli(*base, "--not-applicable", target_id, condition_id, "招聘方确认本批次不适用")
            self.assertEqual(valid.returncode, 0, valid.stderr)
            self.assertNotIn("招聘方确认本批次不适用", valid.stdout)
            self.assertEqual(
                parse_json(valid)["target_conditions"][target_id]["counts"]["not-applicable"],
                1,
            )

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
            root = Path(temporary)
            delivery = root / "delivery"
            evidence = root / "evidence"
            base = (
                "batch", "--input", str(source), "--delivery-root", str(delivery),
                "--evidence-root", str(evidence), "--photo-mode", "no-photo",
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
            failed = run_cli(
                *base, "--allow-gap-target", "target-device-002",
                "--confirm", "--approval-digest", str(payload["approval_digest"]), env=environment,
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertNotIn("Traceback", failed.stderr)
            self.assertNotIn(str(delivery), failed.stderr)
            self.assertLess(len(failed.stderr), 1600)
            self.assertEqual(parse_json(failed)["code"], "TYPST_RUNTIME_INVALID")
            self.assertEqual(public_files(delivery), ())

    def test_photo_triple_recompiles_after_move_without_source_photo(self) -> None:
        fixture = SKILL_ROOT / "fixtures" / "valid-generic-no-target.md"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "photo-source.md"
            source.write_text(
                fixture.read_text(encoding="utf-8").replace(
                    "photo: fixtures/media/student-photo.jpg",
                    "photo: fixtures/layout/media/student-photo.jpg",
                ),
                encoding="utf-8",
            )
            delivery = root / "delivery"
            completed = run_reviewed(
                "render", "--input", str(source), "--generic", "--delivery-root", str(delivery),
                "--assets-root", str(SKILL_ROOT), "--photo-mode", "photo",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            typst_source = next(delivery.glob("*保守稳妥.typ"))
            isolated = root / "isolated"
            isolated.mkdir()
            moved = isolated / typst_source.name
            moved.write_bytes(typst_source.read_bytes())
            first = isolated / "first.pdf"
            second = isolated / "second.pdf"
            command = [
                "typst", "compile", "--font-path", str(SKILL_ROOT / "fonts"),
                "--ignore-system-fonts", "--creation-timestamp", "0", str(moved),
            ]
            one = subprocess.run([*command, str(first)], cwd=isolated, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            two = subprocess.run([*command, str(second)], cwd=isolated, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            self.assertEqual((one.returncode, two.returncode), (0, 0), (one.stderr, two.stderr))
            self.assertEqual(first.read_bytes(), second.read_bytes())
            typst_text = moved.read_text(encoding="utf-8")
            self.assertNotIn(str(source), typst_text)
            self.assertNotIn("student-photo.jpg", typst_text)

    def test_explicit_photo_requires_safe_provided_asset_before_any_delivery_change(self) -> None:
        no_photo = SKILL_ROOT / "fixtures" / "valid-no-photo.md"
        photo_fixture = SKILL_ROOT / "fixtures" / "valid-generic-no-target.md"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            delivery = root / "delivery"
            baseline = run_reviewed(
                "render", "--input", str(no_photo), "--generic",
                "--delivery-root", str(delivery), "--photo-mode", "no-photo",
            )
            self.assertEqual(baseline.returncode, 0, baseline.stderr)
            before = recursive_snapshot(delivery)

            plan_failed = run_cli("plan", "--input", str(no_photo), "--photo-mode", "photo")
            render_failed = run_cli(
                "render", "--input", str(no_photo), "--generic",
                "--delivery-root", str(delivery), "--photo-mode", "photo",
            )
            batch_failed = run_cli(
                "batch", "--input", str(no_photo),
                "--delivery-root", str(delivery), "--photo-mode", "photo",
            )
            for completed in (plan_failed, render_failed, batch_failed):
                self.assertNotEqual(completed.returncode, 0)
                self.assertEqual(parse_json(completed)["code"], "PHOTO_ASSET_INVALID")
                self.assertNotIn("Traceback", completed.stderr)
                self.assertNotIn(str(no_photo), completed.stderr)
                self.assertEqual(recursive_snapshot(delivery), before)

            auto_plan = run_cli("plan", "--input", str(no_photo), "--photo-mode", "auto")
            self.assertEqual(auto_plan.returncode, 0, auto_plan.stderr)
            self.assertEqual(parse_json(auto_plan)["resolved_photo_mode"], "no-photo")
            for command in ("render", "batch"):
                selector = ("--generic",) if command == "render" else ()
                completed = run_cli(
                    command, "--input", str(no_photo), *selector,
                    "--delivery-root", str(delivery), "--photo-mode", "auto",
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(parse_json(completed)["photo_mode"], "no-photo")
                self.assertEqual(recursive_snapshot(delivery), before)

            ignored = run_cli(
                "plan", "--input", str(photo_fixture), "--photo-mode", "no-photo",
                "--assets-root", str(root / "does-not-exist"),
            )
            self.assertEqual(ignored.returncode, 0, ignored.stderr)
            self.assertEqual(parse_json(ignored)["resolved_photo_mode"], "no-photo")

            assets = root / "assets"
            assets.mkdir()
            real_photo = SKILL_ROOT / "fixtures" / "layout" / "media" / "student-photo.jpg"
            (assets / "linked.jpg").symlink_to(real_photo)
            (assets / "invalid.jpg").write_bytes(b"not-a-jpeg")
            source_text = photo_fixture.read_text(encoding="utf-8")
            for name in ("linked.jpg", "invalid.jpg", "missing.jpg"):
                source = root / f"{name}.md"
                source.write_text(
                    source_text.replace("fixtures/media/student-photo.jpg", name),
                    encoding="utf-8",
                )
                completed = run_cli(
                    "render", "--input", str(source), "--generic",
                    "--delivery-root", str(delivery), "--photo-mode", "photo",
                    "--assets-root", str(assets),
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertEqual(parse_json(completed)["code"], "PHOTO_ASSET_INVALID")
                self.assertNotIn(str(source), completed.stderr)
                self.assertEqual(recursive_snapshot(delivery), before)


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
            "test_phase48_cli.PublicCliContractTests.test_photo_triple_recompiles_after_move_without_source_photo",
            "test_phase48_cli.PublicCliContractTests.test_one_typst_runtime_context_is_shared_by_all_consumers",
            "test_phase48_cli.PublicCliContractTests.test_cleanup_failures_are_bounded_and_preserve_published_or_rolled_back_current",
        )
        self.assertEqual(PHASE48_ACCEPTANCE_REGISTRY, required)
        observed = run_phase48_acceptance_registry()
        self.assertEqual(observed["required"], list(required))
        self.assertEqual(observed["called"], list(required))
        self.assertEqual(observed["status"], "passed")
        self.assertNotIn("skip", json.dumps(observed).lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
