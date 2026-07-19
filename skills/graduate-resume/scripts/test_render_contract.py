#!/usr/bin/env python3
"""Phase 48 final Markdown, embedded-photo and render-matrix contract."""

from __future__ import annotations

import hashlib
import json
import os
import contextlib
from dataclasses import replace
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

import graduate_resume_cli as cli
from graduate_resume_targeting import (
    LayoutFeedback,
    PageBudgetRequest,
    evaluate_hard_conditions,
    resolve_version_projection,
)


def _projection(document):
    return resolve_version_projection(
        document.data,
        None,
        PageBudgetRequest("auto"),
        lambda theme, selected, request: LayoutFeedback(theme, True, 1, ()),
    )


@contextlib.contextmanager
def _verified_typst_runtime():
    from graduate_resume_layout import validate_font_manifest
    from graduate_resume_typst_runtime import resolve_typst_executable

    with resolve_typst_executable() as executable:
        yield executable, validate_font_manifest(SKILL_ROOT / "fonts", executable)


class TypstRuntimeResolverTests(unittest.TestCase):
    @staticmethod
    def _fake_typst(path: Path, version: str = "typst 0.15.0") -> None:
        path.write_text(
            "#!/bin/sh\n"
            f"if [ \"$1\" = \"--version\" ]; then printf '%s\\n' '{version}'; exit 0; fi\n"
            "printf '%s\\n' \"$0|$*\"\n",
            encoding="utf-8",
        )
        path.chmod(0o755)

    def test_missing_controlled_helper_fails_closed_before_snapshot_execution(self) -> None:
        """A private same-user snapshot is not a descriptor-exec substitute."""
        from graduate_resume_typst_runtime import resolve_typst_executable

        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "typst"
            self._fake_typst(source)
            with mock.patch("graduate_resume_typst_runtime.HELPER_PATH", Path(temporary) / "missing-helper"):
                with self.assertRaises(cli.CliError) as raised:
                    resolve_typst_executable(source)
        self.assertEqual(raised.exception.code, "TYPST_RUNTIME_INVALID")

    def test_native_acl_probe_accepts_only_kernel_proven_absence(self) -> None:
        source = (SCRIPT_DIR / "graduate_resume_typst_exec_helper.c").read_text(encoding="utf-8")
        self.assertIn("return errno == ENOENT", source)
        self.assertIn("return count == 0", source)

    def test_installed_helper_executes_a_root_owned_copy_after_privilege_drop(self) -> None:
        from graduate_resume_typst_runtime import resolve_typst_executable

        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "typst"
            self._fake_typst(source)
            with resolve_typst_executable(source) as executable:
                completed = executable.run(("--version",), text=True)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "typst 0.15.0\n")

    def test_real_homebrew_symlink_uses_one_private_snapshot(self) -> None:
        from graduate_resume_typst_runtime import resolve_typst_executable

        candidate = Path("/opt/homebrew/bin/typst")
        self.assertTrue(candidate.is_symlink())
        with resolve_typst_executable(candidate) as executable:
            snapshot = executable.snapshot_path
            self.assertEqual(executable.version, "0.15.0")
            self.assertNotEqual(snapshot, candidate)
            self.assertNotEqual(snapshot, candidate.resolve())
            self.assertEqual(snapshot.stat().st_mode & 0o777, 0o500)
            self.assertEqual(snapshot.stat().st_dev, executable.snapshot_dev)
            self.assertEqual(snapshot.stat().st_ino, executable.snapshot_ino)
            self.assertEqual(hashlib.sha256(snapshot.read_bytes()).hexdigest(), executable.snapshot_sha256)
            completed = executable.run(("--version",), text=True)
            self.assertEqual(completed.stdout.strip(), "typst 0.15.0 (unknown commit)")
        self.assertFalse(snapshot.exists())

    def test_relative_and_absolute_multihop_chains_are_supported(self) -> None:
        from graduate_resume_typst_runtime import resolve_typst_executable

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "Cellar" / "typst" / "0.15.0" / "bin" / "typst"
            target.parent.mkdir(parents=True)
            self._fake_typst(target)
            relative = root / "bin" / "typst"
            relative.parent.mkdir()
            relative.symlink_to(Path("../Cellar/typst/0.15.0/bin/typst"))
            absolute = root / "typst-absolute"
            absolute.symlink_to(relative)
            with resolve_typst_executable(absolute) as executable:
                self.assertEqual(executable.version, "0.15.0")
                self.assertEqual(executable.run(("probe",), text=True).args[0], str(executable.snapshot_path))

    def test_invalid_chain_target_and_version_fail_closed(self) -> None:
        from graduate_resume_typst_runtime import resolve_typst_executable

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            dangling = root / "dangling"
            dangling.symlink_to("missing")
            cycle_a = root / "cycle-a"
            cycle_b = root / "cycle-b"
            cycle_a.symlink_to(cycle_b.name)
            cycle_b.symlink_to(cycle_a.name)
            directory = root / "directory"
            directory.mkdir()
            not_executable = root / "not-executable"
            not_executable.write_text("typst", encoding="utf-8")
            hop_paths = [root / f"hop-{index}" for index in range(18)]
            final = root / "final"
            self._fake_typst(final)
            for index, path in enumerate(hop_paths):
                path.symlink_to((hop_paths[index + 1] if index + 1 < len(hop_paths) else final).name)
            bad_versions = []
            for name, version in (("wrong", "typst 9.9.0"), ("multi", "typst 0.15.0\\nextra")):
                path = root / name
                self._fake_typst(path, version)
                bad_versions.append(path)
            nonzero = root / "nonzero"
            nonzero.write_text("#!/bin/sh\nexit 7\n", encoding="utf-8")
            nonzero.chmod(0o755)
            verbose = root / "verbose"
            verbose.write_text("#!/bin/sh\nyes x | head -c 70000\n", encoding="utf-8")
            verbose.chmod(0o755)
            for candidate in (dangling, cycle_a, directory, not_executable, hop_paths[0], *bad_versions, nonzero, verbose):
                with self.subTest(candidate=candidate.name):
                    with self.assertRaises(cli.CliError):
                        with resolve_typst_executable(candidate):
                            pass

    def test_source_replacement_after_copy_cannot_change_snapshot_execution(self) -> None:
        from graduate_resume_typst_runtime import resolve_typst_executable

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = root / "typst-original"
            fake = root / "typst-fake"
            link = root / "typst"
            self._fake_typst(original)
            self._fake_typst(fake, "typst 9.9.0")
            link.symlink_to(original.name)

            def replace_source() -> None:
                link.unlink()
                link.symlink_to(fake.name)
                replacement = root / "replacement"
                self._fake_typst(replacement, "typst 9.9.0")
                os.replace(replacement, original)

            with resolve_typst_executable(link, _after_source_verified=replace_source) as executable:
                self.assertEqual(executable.version, "0.15.0")
                self.assertIn(str(executable.snapshot_path), executable.run(("probe",), text=True).stdout)
                self.assertNotIn("9.9.0", executable.run(("--version",), text=True).stdout)

    def test_snapshot_in_place_overwrite_is_rejected_before_execution(self) -> None:
        from graduate_resume_typst_runtime import resolve_typst_executable

        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "typst"
            self._fake_typst(source)
            with resolve_typst_executable(source) as executable:
                original = executable.snapshot_path.read_bytes()
                executable.snapshot_path.chmod(0o700)
                executable.snapshot_path.write_bytes(original.replace(b"0.15.0", b"9.9.0 "))
                executable.snapshot_path.chmod(0o500)
                with self.assertRaises(cli.CliError):
                    executable.run(("--version",), text=True)

    def test_copy_time_source_change_is_rejected_and_snapshot_cleaned(self) -> None:
        from graduate_resume_typst_runtime import resolve_typst_executable

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "typst"
            self._fake_typst(source)

            def mutate_source(_copied: int) -> None:
                source.chmod(0o700)

            snapshot_roots: list[Path] = []
            original_mkdtemp = tempfile.mkdtemp

            def make_temp(*args, **kwargs) -> str:
                value = original_mkdtemp(*args, **kwargs)
                snapshot_roots.append(Path(value))
                return value

            with mock.patch("graduate_resume_typst_runtime.tempfile.mkdtemp", side_effect=make_temp):
                with self.assertRaises(cli.CliError):
                    with resolve_typst_executable(source, _copy_chunk_hook=mutate_source):
                        pass
                self.assertEqual(len(snapshot_roots), 1)
                self.assertFalse(snapshot_roots[0].exists())


class PhotoDescriptorSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = SKILL_ROOT / "fixtures" / "valid-generic-no-target.md"
        self.photo = SKILL_ROOT / "fixtures" / "layout" / "media" / "student-photo.jpg"

    def test_photo_bytes_hash_and_identity_come_from_one_descriptor(self) -> None:
        from graduate_resume_layout import resolve_layout_photo

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            assets = root / "assets"
            assets.mkdir()
            leaf = assets / "student.jpg"
            original = self.photo.read_bytes()
            leaf.write_bytes(original)
            replacement = b"\xff\xd8replacement\xff\xd9"

            def replace_leaf() -> None:
                alternate = assets / "alternate.jpg"
                alternate.write_bytes(replacement)
                os.replace(alternate, leaf)

            resolved = resolve_layout_photo(
                self.source,
                assets,
                {"status": "provided", "path": "student.jpg"},
                {"photo_mode": "photo"},
                _after_leaf_read=replace_leaf,
            )
            self.assertEqual(resolved.logical_path, "student.jpg")
            self.assertEqual(resolved.source_bytes, original)
            self.assertEqual(resolved.source_sha256, hashlib.sha256(original).hexdigest())
            self.assertNotEqual(resolved.source_bytes, leaf.read_bytes())
            self.assertGreater(resolved.st_dev, 0)
            self.assertGreater(resolved.st_ino, 0)

    def test_photo_root_components_leaf_type_size_and_format_fail_closed(self) -> None:
        from graduate_resume_layout import MAX_PHOTO_BYTES, resolve_layout_photo

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            real_assets = root / "real-assets"
            real_assets.mkdir()
            valid = real_assets / "valid.jpg"
            valid.write_bytes(self.photo.read_bytes())
            linked_root = root / "linked-assets"
            linked_root.symlink_to(real_assets, target_is_directory=True)
            middle = real_assets / "middle"
            middle.symlink_to(root, target_is_directory=True)
            linked_leaf = real_assets / "linked.jpg"
            linked_leaf.symlink_to(valid)
            directory_leaf = real_assets / "directory.jpg"
            directory_leaf.mkdir()
            fifo = real_assets / "fifo.jpg"
            os.mkfifo(fifo)
            oversized = real_assets / "oversized.jpg"
            with oversized.open("wb") as stream:
                stream.write(b"\xff\xd8")
                stream.seek(MAX_PHOTO_BYTES)
                stream.write(b"\xff\xd9")
            (real_assets / "truncated.jpg").write_bytes(b"\xff\xd8truncated")
            (real_assets / "truncated.png").write_bytes(b"\x89PNG\r\n\x1a\ntruncated")
            cases = (
                (linked_root, "valid.jpg"),
                (real_assets, "middle/valid.jpg"),
                (real_assets, "linked.jpg"),
                (real_assets, "directory.jpg"),
                (real_assets, "fifo.jpg"),
                (real_assets, "oversized.jpg"),
                (real_assets, "truncated.jpg"),
                (real_assets, "truncated.png"),
            )
            for assets_root, logical_path in cases:
                with self.subTest(logical_path=logical_path):
                    with self.assertRaises(cli.CliError):
                        resolve_layout_photo(
                            self.source,
                            assets_root,
                            {"status": "provided", "path": logical_path},
                            {"photo_mode": "photo"},
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

    def test_declined_fact_remains_canonical_but_cannot_cross_final_checkpoint(self) -> None:
        from graduate_resume_final_markdown import emit_final_markdown, load_final_resume

        declined = cli.load_resume(str(self.source))
        declined.data["education"][0]["status"] = "declined"
        self.assertEqual(cli.validate_document(declined)["status"], "passed")
        with self.assertRaises(cli.CliError):
            emit_final_markdown(
                declined.data,
                self.projection,
                canonical_hash=hashlib.sha256(self.source.read_bytes()).hexdigest(),
                theme_key="conservative",
                theme_label="保守稳妥",
                page_count=1,
                photo_mode="no-photo",
            )

        payload = emit_final_markdown(
            self.document.data,
            self.projection,
            canonical_hash=hashlib.sha256(self.source.read_bytes()).hexdigest(),
            theme_key="conservative",
            theme_label="保守稳妥",
            page_count=1,
            photo_mode="no-photo",
        ).replace(b'"status":"verified"', b'"status":"declined"', 1)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "resume.md"
            path.write_bytes(payload)
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
        with _verified_typst_runtime() as (executable, _font_hash):
            first = normalize_photo_bytes(source, executable)
            second = normalize_photo_bytes(source, executable)
        self.assertEqual(first, second)
        self.assertEqual(first[16:24], (413).to_bytes(4, "big") + (579).to_bytes(4, "big"))
        self.assertNotIn(b"EXIF", first)

    def test_typst_rejects_candidate_controlled_container_id(self) -> None:
        from graduate_resume_final_markdown import emit_final_markdown, load_final_resume
        from graduate_resume_layout import build_frozen_resume_plan, resolve_theme
        from graduate_resume_typst import emit_typst

        source = SKILL_ROOT / "fixtures" / "valid-no-photo.md"
        document = cli.load_resume(str(source))
        projection = _projection(document)
        payload = emit_final_markdown(
            document.data, projection,
            canonical_hash=hashlib.sha256(source.read_bytes()).hexdigest(),
            theme_key="modern", theme_label="现代简洁", page_count=1,
            photo_mode="no-photo",
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "resume.md"
            path.write_bytes(payload)
            final = load_final_resume(path)
            plan = build_frozen_resume_plan(
                final.fact_view(), resolve_theme("modern"), "no-photo", None,
                "a" * 64, "auto",
            )
            malicious = 'x");#panic("injected");#("'
            containers = (replace(plan.containers[0], id=malicious), *plan.containers[1:])
            pages = tuple(
                replace(page, containers=tuple(malicious if item == plan.containers[0].id else item for item in page.containers))
                for page in plan.pages
            )
            poisoned = replace(plan, containers=containers, pages=pages)
            with self.assertRaises(cli.CliError):
                emit_typst(poisoned, final)

    def test_structured_display_fields_reach_real_typst_and_pdf(self) -> None:
        import fitz

        from graduate_resume_final_markdown import emit_final_markdown, load_final_resume
        from graduate_resume_layout import _height, build_frozen_resume_plan, project_containers, resolve_theme
        from graduate_resume_typst import emit_typst

        source = SKILL_ROOT / "templates" / "graduate-resume.md"
        document = cli.load_resume(str(source))
        markers = (
            "CONTACT-MARKER-138",
            "SKILL-MARKER-PLC",
            "OUTCOME-MARKER-ALARM",
            "TOOL-MARKER-TIA",
        )
        document.data["candidate"]["contact"]["phone"] = markers[0]
        document.data["skills"][0]["items"] = [markers[1]]
        document.data["projects"][0]["outcomes"] = [markers[2]]
        document.data["projects"][0]["tools"] = [markers[3]]
        cli.validate_document(document)
        projection = _projection(document)
        payload = emit_final_markdown(
            document.data, projection,
            canonical_hash=hashlib.sha256(source.read_bytes()).hexdigest(),
            theme_key="modern", theme_label="现代简洁", page_count=1,
            photo_mode="no-photo",
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            markdown_path = root / "resume.md"
            markdown_path.write_bytes(payload)
            final = load_final_resume(markdown_path)
            plan = build_frozen_resume_plan(
                final.fact_view(), resolve_theme("modern"), "no-photo", None,
                "a" * 64, "1",
            )
            frozen_text = "\n".join(value for container in plan.containers for _, value in container.fields)
            for marker in markers:
                self.assertIn(marker, frozen_text)
            for container in plan.containers:
                self.assertEqual(
                    container.height_mm,
                    _height(tuple(value for _, value in container.fields)),
                )
            reordered = final.fact_view()
            reordered["candidate"] = dict(reversed(tuple(reordered["candidate"].items())))
            for section in ("education", "skills", "certificates", "projects", "training", "experience"):
                reordered[section] = [dict(reversed(tuple(item.items()))) for item in reordered[section]]
            self.assertEqual(
                tuple((item.id, item.fields, item.height_mm) for item in project_containers(reordered)),
                tuple((item.id, item.fields, item.height_mm) for item in project_containers(final.fact_view())),
            )
            typst = emit_typst(plan, final)
            typst_path = root / "resume.typ"
            pdf_path = root / "resume.pdf"
            typst_path.write_text(typst, encoding="utf-8")
            completed = subprocess.run(
                [
                    "typst", "compile", "--font-path", str(SKILL_ROOT / "fonts"),
                    "--ignore-system-fonts", "--creation-timestamp", "0",
                    str(typst_path), str(pdf_path),
                ],
                cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            with fitz.open(pdf_path) as pdf:
                pdf_text = "\n".join(page.get_text() for page in pdf)
            for marker in markers:
                self.assertIn(marker, typst)
                self.assertIn(marker, pdf_text)

    def test_structured_display_fields_reject_unregistered_or_unsafe_values(self) -> None:
        from graduate_resume_layout import project_containers

        source = SKILL_ROOT / "templates" / "graduate-resume.md"
        mutations = (
            lambda data: data["candidate"]["contact"].update({"unknown": "secret"}),
            lambda data: data["candidate"].update({"contact": {"phone": {"nested": "bad"}}}),
            lambda data: data["skills"][0].update({"items": ["PLC", 7]}),
            lambda data: data["projects"][0].update({"outcomes": ["normal", "bad\x00control"]}),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                document = cli.load_resume(str(source))
                mutation(document.data)
                with self.assertRaises(cli.CliError):
                    project_containers(document.data)


class RenderMatrixContractTests(unittest.TestCase):
    def test_evidence_root_rejects_unknown_nodes_and_identity_swap(self) -> None:
        from graduate_resume_render import EvidenceSink

        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            evidence = parent / "evidence"
            evidence.mkdir()
            (evidence / "unknown.txt").write_text("unknown", encoding="utf-8")
            with self.assertRaises(cli.CliError):
                with EvidenceSink(evidence):
                    pass
            (evidence / "unknown.txt").unlink()
            with EvidenceSink(evidence) as sink:
                original = parent / "evidence-original"
                evidence.rename(original)
                evidence.mkdir()
                with self.assertRaises(cli.CliError):
                    sink.assert_identity()

    def test_target_evidence_is_persisted_outside_candidate_and_digest_bound(self) -> None:
        from graduate_resume_layout import build_layout_feedback_adapter
        from graduate_resume_render import EvidenceSink, render_candidate_matrix

        source = SKILL_ROOT / "fixtures" / "valid-multi-target.md"
        document = cli.load_resume(str(source))
        cli.validate_document(document)
        target = document.data["targets"][0]
        feedback = build_layout_feedback_adapter(document.data, "no-photo", None, "a" * 64)
        projection = resolve_version_projection(
            document.data, target, PageBudgetRequest("auto"), feedback,
        )
        evaluation = evaluate_hard_conditions(document.data, target)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence_root = root / "private-evidence"
            with _verified_typst_runtime() as (executable, font_hash):
                result = render_candidate_matrix(
                    root / "work" / "candidate",
                    document.data,
                    projection,
                    canonical_hash=hashlib.sha256(source.read_bytes()).hexdigest(),
                    target=target,
                    typst_executable=executable,
                    font_manifest_hash=font_hash,
                    condition_evidence=evaluation.to_evidence_projection(),
                    evidence_root=evidence_root,
                )
            evidence_files = tuple(evidence_root.iterdir())
            self.assertEqual(len(evidence_files), 1)
            payload = json.loads(evidence_files[0].read_bytes())
            self.assertEqual(payload["canonical_hash"], hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual(payload["projection_digest"], projection.digest)
            self.assertEqual(payload["condition_digest"], projection.condition_digest)
            digest_payload = dict(payload["condition_evidence"])
            digest_payload.pop("evidence_digest")
            matrix_digest = hashlib.sha256(
                json.dumps(
                    digest_payload,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            self.assertEqual(matrix_digest, projection.condition_digest)
            self.assertFalse(any("evidence" in path.name for path in result.candidate_root.iterdir()))
            evidence_files[0].write_bytes(b"conflicting binding")
            with self.assertRaises(cli.CliError):
                with EvidenceSink(evidence_root) as sink:
                    sink.persist(
                        canonical_hash=hashlib.sha256(source.read_bytes()).hexdigest(),
                        projection=projection,
                        condition_evidence=evaluation.to_evidence_projection(),
                    )

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
            with _verified_typst_runtime() as (executable, font_hash):
                result = render_candidate_matrix(
                    Path(temporary) / "candidate", document.data, projection,
                    canonical_hash=hashlib.sha256(source.read_bytes()).hexdigest(),
                    typst_executable=executable, font_manifest_hash=font_hash,
                )
            self.assertTrue(result.publishable)
            names = sorted(path.name for path in result.candidate_root.iterdir())
            self.assertEqual(len(names), 9)
            for item in result.items:
                self.assertEqual({path.suffix for path in result.candidate_root.glob(item.stem + ".*")}, {".md", ".typ", ".pdf"})

    def test_safe_stem_normalizes_and_rejects_collision(self) -> None:
        from graduate_resume_render import RENDER_INPUT_INVALID, RENDER_MATRIX_FAILED, RENDER_STEM_COLLISION, build_render_matrix, build_stem, render_candidate_matrix, safe_component

        self.assertEqual(safe_component(" Ａ/Ｂ\x00 C "), "A-B-C")
        self.assertLessEqual(len(safe_component("张" * 40).encode("utf-8")), 48)
        for sensitive in (
            "张三13800000000", "张三010-12345678", "张三+1 202 555 0123",
            "张三110105491231002", "test@example.com", "11010519491231002X",
            "https://jobs.example.test/private",
        ):
            with self.subTest(sensitive=sensitive):
                with self.assertRaises(cli.CliError) as raised:
                    build_stem(sensitive, "conservative")
                self.assertEqual(raised.exception.code, RENDER_INPUT_INVALID)
        source = SKILL_ROOT / "fixtures" / "valid-generic-no-target.md"
        document = cli.load_resume(str(source))
        projection = _projection(document)
        with self.assertRaises(cli.CliError) as raised:
            build_render_matrix("甲", (projection, projection))
        self.assertEqual(raised.exception.code, RENDER_STEM_COLLISION)
        target_source = SKILL_ROOT / "fixtures" / "valid-multi-target.md"
        targeted = cli.load_resume(str(target_source))
        cli.validate_document(targeted)
        target = targeted.data["targets"][0]
        target_projection = resolve_version_projection(
            targeted.data, target, PageBudgetRequest("auto"),
            lambda theme, selected, request: LayoutFeedback(theme, True, 1, ()),
        )
        target_matrix = build_render_matrix(targeted.data["candidate"]["name"], target_projection, targets={target["id"]: target})
        self.assertTrue(all(safe_component(target["role"]) in item.stem for item in target_matrix.items))
        with tempfile.TemporaryDirectory() as temporary:
            candidate = Path(temporary) / "candidate"
            with _verified_typst_runtime() as (executable, font_hash), self.assertRaises(cli.CliError) as raised:
                render_candidate_matrix(
                    candidate, document.data, projection,
                    canonical_hash=hashlib.sha256(source.read_bytes()).hexdigest(),
                    typst_executable=executable, font_manifest_hash=font_hash,
                    fail_theme="modern",
                )
            self.assertEqual(raised.exception.code, RENDER_MATRIX_FAILED)
            self.assertFalse(candidate.exists() and any(candidate.iterdir()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
