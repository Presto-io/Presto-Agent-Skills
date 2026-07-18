#!/usr/bin/env python3
"""Phase 48 final Markdown, embedded-photo and render-matrix contract."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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
        first = normalize_photo_bytes(source)
        second = normalize_photo_bytes(source)
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
        from graduate_resume_render import render_candidate_matrix

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
            result = render_candidate_matrix(
                root / "work" / "candidate",
                document.data,
                projection,
                canonical_hash=hashlib.sha256(source.read_bytes()).hexdigest(),
                target=target,
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
            result = render_candidate_matrix(
                Path(temporary) / "candidate", document.data, projection,
                canonical_hash=hashlib.sha256(source.read_bytes()).hexdigest(),
            )
            self.assertTrue(result.publishable)
            names = sorted(path.name for path in result.candidate_root.iterdir())
            self.assertEqual(len(names), 9)
            for item in result.items:
                self.assertEqual({path.suffix for path in result.candidate_root.glob(item.stem + ".*")}, {".md", ".typ", ".pdf"})

    def test_safe_stem_normalizes_and_rejects_collision(self) -> None:
        from graduate_resume_render import RENDER_MATRIX_FAILED, RENDER_STEM_COLLISION, build_render_matrix, render_candidate_matrix, safe_component

        self.assertEqual(safe_component(" Ａ/Ｂ\x00 C "), "A-B-C")
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
            with self.assertRaises(cli.CliError) as raised:
                render_candidate_matrix(
                    candidate, document.data, projection,
                    canonical_hash=hashlib.sha256(source.read_bytes()).hexdigest(), fail_theme="modern",
                )
            self.assertEqual(raised.exception.code, RENDER_MATRIX_FAILED)
            self.assertFalse(candidate.exists() and any(candidate.iterdir()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
