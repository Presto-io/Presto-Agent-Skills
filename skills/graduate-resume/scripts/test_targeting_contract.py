#!/usr/bin/env python3
"""Phase 48 deterministic targeting and hard-condition contract."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

import graduate_resume_cli as cli
from graduate_resume_targeting import (
    PAGE_BUDGET_UNSATISFIABLE,
    TARGET_CONDITION_INVALID,
    TARGET_GAP_NOT_ALLOWED,
    TARGETING_OVERRIDE_INVALID,
    ConditionResult,
    LayoutFeedback,
    PageBudgetRequest,
    condition_id_for_requirement,
    evaluate_hard_conditions,
    load_targeting_policy,
    resolve_version_projection,
)


def _facts() -> dict[str, object]:
    return {
        "candidate": {
            "name": "周凯",
            "status": "verified",
            "directions": ["机器人调试", "设备运维"],
        },
        "education": [
            {
                "id": "edu-001",
                "status": "verified",
                "school": "某职业学院",
                "major": "智能制造装备技术",
                "degree": "大专",
            }
        ],
        "skills": [
            {"id": "skill-zeta", "status": "verified", "group": "设备", "items": ["巡检"]},
            {"id": "skill-alpha", "status": "verified", "group": "设备", "items": ["巡检"]},
            {"id": "skill-robot", "status": "verified", "group": "机器人", "items": ["示教器", "联调"]},
        ],
        "certificates": [
            {"id": "cert-electrician", "status": "verified", "name": "低压电工证"},
        ],
        "projects": [
            {"id": "project-robot", "status": "verified", "title": "机器人工作站联调", "tools": ["PLC"]},
            {"id": "project-energy", "status": "verified", "title": "储能设备巡检", "tools": ["万用表"]},
        ],
        "training": [],
        "experience": [],
        "targets": [],
    }


def _target() -> dict[str, object]:
    return {
        "id": "target-robot-001",
        "company": "某机器人公司",
        "role": "机器人调试技术员",
        "source": "校招海报",
        "as_of": "2026-07-18",
        "confirmed": True,
        "requirements": ["持有低压电工证"],
    }


class TargetingProjectionTests(unittest.TestCase):
    def test_policy_has_exact_schema_and_raw_bytes_hash(self) -> None:
        path = SKILL_ROOT / "templates" / "targeting-policy.json"
        policy = load_targeting_policy(path)
        self.assertEqual(
            set(policy.to_projection()),
            {"policy_version", "module_order", "score_weights", "exact_term_expansions", "predicate_registry", "sha256"},
        )
        self.assertEqual(policy.sha256, hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(
            policy.predicate_registry,
            ("education_level", "major_exact", "certificate_exact", "fresh_graduate_status"),
        )
        with tempfile.TemporaryDirectory() as temporary:
            bad = Path(temporary) / "policy.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["unexpected"] = True
            bad.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(cli.CliError) as raised:
                load_targeting_policy(bad)
            self.assertEqual(raised.exception.code, "TARGETING_POLICY_INVALID")

    def test_projection_is_deterministic_reorder_safe_and_immutable(self) -> None:
        facts = _facts()
        target = _target()
        before_facts = json.dumps(facts, ensure_ascii=False, sort_keys=True)
        before_target = json.dumps(target, ensure_ascii=False, sort_keys=True)
        calls: list[tuple[str, tuple[str, ...], str]] = []

        def feedback(theme_key: str, selected_ids: tuple[str, ...], request: PageBudgetRequest) -> LayoutFeedback:
            calls.append((theme_key, selected_ids, request.requested_pages))
            return LayoutFeedback(theme_key, True, 1, ())

        first = resolve_version_projection(facts, target, PageBudgetRequest("auto"), feedback)
        second = resolve_version_projection(copy.deepcopy(facts), copy.deepcopy(target), PageBudgetRequest("auto"), feedback)
        reordered = copy.deepcopy(facts)
        reordered["skills"] = list(reversed(reordered["skills"]))
        reordered["projects"] = list(reversed(reordered["projects"]))
        third = resolve_version_projection(reordered, copy.deepcopy(target), PageBudgetRequest("auto"), feedback)
        first_bytes = json.dumps(first.to_projection(), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(first_bytes, json.dumps(second.to_projection(), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
        self.assertEqual(first_bytes, json.dumps(third.to_projection(), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
        self.assertEqual(first.digest, second.digest)
        self.assertEqual(first.selected_fact_ids[:2], ("profile", "edu-001"))
        self.assertLess(first.selected_fact_ids.index("skill-alpha"), first.selected_fact_ids.index("skill-zeta"))
        self.assertEqual(json.dumps(facts, ensure_ascii=False, sort_keys=True), before_facts)
        self.assertEqual(json.dumps(target, ensure_ascii=False, sort_keys=True), before_target)
        self.assertEqual({call[0] for call in calls}, {"conservative", "modern", "expressive"})

    def test_shared_theme_budget_removes_one_lowest_optional_fact_per_round(self) -> None:
        calls: list[tuple[str, tuple[str, ...]]] = []

        def feedback(theme_key: str, selected_ids: tuple[str, ...], request: PageBudgetRequest) -> LayoutFeedback:
            calls.append((theme_key, selected_ids))
            fits = len(selected_ids) <= 6
            return LayoutFeedback(theme_key, fits, 2 if fits else 3, () if fits else (selected_ids[-1],))

        projection = resolve_version_projection(
            _facts(),
            _target(),
            PageBudgetRequest("2"),
            feedback,
            overrides={"retain": ["skill-zeta"], "pin": ["project-energy"]},
        )
        rounds = [calls[index : index + 3] for index in range(0, len(calls), 3)]
        self.assertGreater(len(rounds), 1)
        for round_calls in rounds:
            self.assertEqual([item[0] for item in round_calls], ["conservative", "modern", "expressive"])
            self.assertEqual(len({item[1] for item in round_calls}), 1)
        for previous, current in zip(rounds, rounds[1:]):
            self.assertEqual(len(previous[0][1]) - len(current[0][1]), 1)
        self.assertIn("profile", projection.selected_fact_ids)
        self.assertIn("edu-001", projection.selected_fact_ids)
        self.assertIn("skill-zeta", projection.selected_fact_ids)
        self.assertIn("project-energy", projection.selected_fact_ids)
        self.assertTrue(all(summary.page_count <= 2 for summary in projection.layout_feedback))
        self.assertEqual(projection.requested_pages, "2")

    def test_auto_one_two_page_requests_share_contract(self) -> None:
        for requested, expected_pages in (("auto", 2), ("1", 1), ("2", 2)):
            seen: list[str] = []

            def feedback(theme_key: str, selected_ids: tuple[str, ...], request: PageBudgetRequest) -> LayoutFeedback:
                seen.append(request.requested_pages)
                return LayoutFeedback(theme_key, True, expected_pages, ())

            projection = resolve_version_projection(_facts(), None, PageBudgetRequest(requested), feedback)
            self.assertEqual(projection.requested_pages, requested)
            self.assertEqual(seen, [requested, requested, requested])
            self.assertTrue(all(item.page_count == expected_pages for item in projection.layout_feedback))

    def test_invalid_overrides_and_unsatisfiable_budget_fail_closed(self) -> None:
        facts = _facts()
        target = _target()
        original = json.dumps((facts, target), ensure_ascii=False, sort_keys=True)

        def always_overflow(theme_key: str, selected_ids: tuple[str, ...], request: PageBudgetRequest) -> LayoutFeedback:
            return LayoutFeedback(theme_key, False, 3, selected_ids)

        invalid = (
            ({"exclude": ["profile"]}, TARGETING_OVERRIDE_INVALID),
            ({"exclude": ["edu-001"]}, TARGETING_OVERRIDE_INVALID),
            ({"exclude": ["missing"]}, TARGETING_OVERRIDE_INVALID),
            ({"retain": ["skill-alpha"], "exclude": ["skill-alpha"]}, TARGETING_OVERRIDE_INVALID),
            ({"pin": ["skill-alpha"], "exclude": ["skill-alpha"]}, TARGETING_OVERRIDE_INVALID),
        )
        for overrides, code in invalid:
            with self.subTest(overrides=overrides):
                with self.assertRaises(cli.CliError) as raised:
                    resolve_version_projection(facts, target, PageBudgetRequest("auto"), always_overflow, overrides=overrides)
                self.assertEqual(raised.exception.code, code)
        with self.assertRaises(cli.CliError) as raised:
            resolve_version_projection(
                facts,
                target,
                PageBudgetRequest("1"),
                always_overflow,
                overrides={"retain": ["skill-alpha", "skill-zeta", "skill-robot", "cert-electrician", "project-robot", "project-energy"]},
            )
        self.assertEqual(raised.exception.code, PAGE_BUDGET_UNSATISFIABLE)
        self.assertEqual(json.dumps((facts, target), ensure_ascii=False, sort_keys=True), original)


class HardConditionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.facts = _facts()
        self.facts["candidate"]["headline"] = "2026届应届毕业生"

    def _target(self, target_id: str, requirements: list[str]) -> dict[str, object]:
        return {
            "id": target_id,
            "company": "示例单位",
            "role": "设备技术员",
            "source": "用户提供的招聘简章",
            "as_of": "2026-07-18",
            "confirmed": True,
            "requirements": requirements,
        }

    def test_controlled_predicates_produce_four_states_without_similarity_claims(self) -> None:
        target = self._target(
            "target-four-state",
            [
                "学历要求：大专",
                "专业要求：智能制造装备技术",
                "证书要求：低压电工证",
                "应届毕业生",
                "具有2年设备经验",
                "了解低压电工安全知识",
            ],
        )
        evaluation = evaluate_hard_conditions(self.facts, target, allowed_gap_target_ids=())
        self.assertTrue(all(isinstance(item, ConditionResult) for item in evaluation.matrix))
        states = [item.state for item in evaluation.matrix]
        self.assertEqual(states, ["meets", "meets", "meets", "meets", "unknown", "unknown"])
        self.assertEqual(
            [item.predicate for item in evaluation.matrix[:4]],
            ["education_level", "major_exact", "certificate_exact", "fresh_graduate_status"],
        )
        self.assertTrue(evaluation.warnings)
        self.assertFalse(evaluation.gap_allowed)

    def test_explicit_verified_mismatch_is_gap_and_allow_is_per_target(self) -> None:
        target_a = self._target("target-a", ["学历要求：本科"])
        target_b = self._target("target-b", ["证书要求：特种作业操作证"])
        with self.assertRaises(cli.CliError) as raised:
            evaluate_hard_conditions(self.facts, target_a)
        self.assertEqual(raised.exception.code, TARGET_GAP_NOT_ALLOWED)
        allowed = evaluate_hard_conditions(self.facts, target_a, allowed_gap_target_ids=("target-a",))
        self.assertEqual(allowed.matrix[0].state, "gap")
        self.assertTrue(allowed.gap_allowed)
        with self.assertRaises(cli.CliError) as raised:
            evaluate_hard_conditions(self.facts, target_b, allowed_gap_target_ids=("target-a",))
        self.assertEqual(raised.exception.code, TARGET_GAP_NOT_ALLOWED)

    def test_not_applicable_requires_exact_current_override_and_safe_reason(self) -> None:
        target = self._target("target-na", ["学历要求：本科", "工作地点：本市"])
        condition_id = condition_id_for_requirement("target-na", "学历要求：本科")
        original = json.dumps(target, ensure_ascii=False, sort_keys=True)
        evaluation = evaluate_hard_conditions(
            self.facts,
            target,
            not_applicable_overrides=(("target-na", condition_id, "  招聘方确认该条不适用于本批次  "),),
        )
        self.assertEqual(evaluation.matrix[0].state, "not-applicable")
        self.assertEqual(evaluation.matrix[0].reason, "招聘方确认该条不适用于本批次")
        self.assertEqual(evaluation.matrix[1].state, "unknown")
        self.assertEqual(json.dumps(target, ensure_ascii=False, sort_keys=True), original)
        invalid_overrides = (
            (("target-na", condition_id, ""),),
            (("target-na", condition_id, "x" * 201),),
            (("target-na", condition_id, "包含\n换行"),),
            (("target-other", condition_id, "理由"),),
            (("target-na", "condition-missing", "理由"),),
            (("target-na", condition_id, "理由"), ("target-na", condition_id, "理由")),
        )
        for overrides in invalid_overrides:
            with self.subTest(overrides=overrides):
                with self.assertRaises(cli.CliError) as raised:
                    evaluate_hard_conditions(self.facts, target, not_applicable_overrides=overrides, allowed_gap_target_ids=("target-na",))
                self.assertEqual(raised.exception.code, TARGET_CONDITION_INVALID)

    def test_public_summary_is_bounded_and_hidden_matrix_is_digest_bound(self) -> None:
        target = self._target("target-public", ["学历要求：大专", "年龄不超过25岁", "工作地点：本市", "熟练掌握PLC"])
        evaluation = evaluate_hard_conditions(self.facts, target)
        public = evaluation.to_public_projection()
        hidden = evaluation.to_evidence_projection()
        public_text = json.dumps(public, ensure_ascii=False, sort_keys=True)
        hidden_text = json.dumps(hidden, ensure_ascii=False, sort_keys=True)
        self.assertEqual(public["counts"], {"meets": 1, "gap": 0, "unknown": 3, "not-applicable": 0})
        self.assertEqual(public["evidence_digest"], evaluation.evidence_digest)
        self.assertIn("condition_id", hidden_text)
        self.assertIn("evidence_fact_ids", hidden_text)
        for secret in ("周凯", "低压电工证", "/Users/", "招聘方确认"):
            self.assertNotIn(secret, public_text)
        self.assertNotIn("reason", public_text)

    def test_duplicate_normalized_conditions_and_unknown_allow_ids_fail(self) -> None:
        duplicate = self._target("target-duplicate", ["学历要求：大专", " 学历要求：大专 "])
        with self.assertRaises(cli.CliError) as raised:
            evaluate_hard_conditions(self.facts, duplicate)
        self.assertEqual(raised.exception.code, TARGET_CONDITION_INVALID)
        valid = self._target("target-valid", ["学历要求：大专"])
        with self.assertRaises(cli.CliError) as raised:
            evaluate_hard_conditions(self.facts, valid, allowed_gap_target_ids=("target-other",))
        self.assertEqual(raised.exception.code, TARGET_CONDITION_INVALID)

    def test_projection_freezes_condition_summary_digest_and_gap_allow(self) -> None:
        target = self._target("target-projection", ["学历要求：本科", "具有2年设备经验"])

        def feedback(theme_key: str, selected_ids: tuple[str, ...], request: PageBudgetRequest) -> LayoutFeedback:
            return LayoutFeedback(theme_key, True, 1, ())

        projection = resolve_version_projection(
            self.facts,
            target,
            PageBudgetRequest("auto"),
            feedback,
            allowed_gap_target_ids=("target-projection",),
        )
        self.assertEqual(dict(projection.condition_summary), {"meets": 0, "gap": 1, "unknown": 1, "not-applicable": 0})
        self.assertEqual(len(projection.condition_digest), 64)
        self.assertTrue(projection.gap_allowed)


class TargetingFixtureTests(unittest.TestCase):
    def test_literal_multi_state_fixture_is_valid(self) -> None:
        document = cli.load_resume(str(SKILL_ROOT / "fixtures" / "targeting" / "multi-state-targets.md"))
        summary = cli.validate_document(document)
        self.assertEqual(summary["target_count"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
