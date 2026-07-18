"""Deterministic, immutable targeting projections for verified resume facts."""

from __future__ import annotations

import hashlib
import json
import unicodedata
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from graduate_resume_cli import CliError

TARGETING_POLICY_INVALID = "TARGETING_POLICY_INVALID"
TARGETING_INPUT_INVALID = "TARGETING_INPUT_INVALID"
TARGETING_OVERRIDE_INVALID = "TARGETING_OVERRIDE_INVALID"
PAGE_BUDGET_UNSATISFIABLE = "PAGE_BUDGET_UNSATISFIABLE"
TARGETING_PROJECTION_INVALID = "TARGETING_PROJECTION_INVALID"

_POLICY_FIELDS = frozenset(
    ("policy_version", "module_order", "score_weights", "exact_term_expansions", "predicate_registry")
)
_SCORE_FIELDS = frozenset(("role_exact", "role_expansion", "requirement_exact", "direction_exact"))
_OVERRIDE_FIELDS = frozenset(("retain", "exclude", "pin"))
_CORE_SECTIONS = frozenset(("candidate", "education"))
_THEMES = ("conservative", "modern", "expressive")


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _normalized(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _flatten_text(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        normalized = _normalized(value)
        return (normalized,) if normalized else ()
    if isinstance(value, Mapping):
        return tuple(part for key, item in value.items() if key not in {"id", "status"} for part in _flatten_text(item))
    if isinstance(value, (list, tuple)):
        return tuple(part for item in value for part in _flatten_text(item))
    return ()


@dataclass(frozen=True, slots=True)
class TargetingPolicy:
    policy_version: str
    module_order: tuple[str, ...]
    score_weights: tuple[tuple[str, int], ...]
    exact_term_expansions: tuple[tuple[str, tuple[str, ...]], ...]
    predicate_registry: tuple[str, ...]
    sha256: str

    def to_projection(self) -> dict[str, Any]:
        return {
            "policy_version": self.policy_version,
            "module_order": list(self.module_order),
            "score_weights": dict(self.score_weights),
            "exact_term_expansions": {key: list(values) for key, values in self.exact_term_expansions},
            "predicate_registry": list(self.predicate_registry),
            "sha256": self.sha256,
        }


@dataclass(frozen=True, slots=True)
class FactDecision:
    fact_id: str
    section: str
    action: str
    score: int
    reason_codes: tuple[str, ...]
    core: bool
    retained: bool
    pinned: bool
    selected: bool

    def to_projection(self) -> dict[str, Any]:
        return {
            "fact_id": self.fact_id,
            "section": self.section,
            "action": self.action,
            "score": self.score,
            "reason_codes": list(self.reason_codes),
            "core": self.core,
            "retained": self.retained,
            "pinned": self.pinned,
            "selected": self.selected,
        }


@dataclass(frozen=True, slots=True)
class OverrideSnapshot:
    retain_ids: tuple[str, ...] = ()
    exclude_ids: tuple[str, ...] = ()
    pin_ids: tuple[str, ...] = ()

    def to_projection(self) -> dict[str, Any]:
        return {"retain_ids": list(self.retain_ids), "exclude_ids": list(self.exclude_ids), "pin_ids": list(self.pin_ids)}


@dataclass(frozen=True, slots=True)
class PageBudgetRequest:
    requested_pages: str = "auto"

    def __post_init__(self) -> None:
        if self.requested_pages not in {"auto", "1", "2"}:
            raise CliError(TARGETING_INPUT_INVALID, "页数预算必须是 auto、1 或 2。")

    def to_projection(self) -> dict[str, str]:
        return {"requested_pages": self.requested_pages}


@dataclass(frozen=True, slots=True)
class LayoutFeedback:
    theme_key: str
    fits: bool
    page_count: int
    overflow_container_ids: tuple[str, ...]

    def to_projection(self) -> dict[str, Any]:
        return {
            "theme_key": self.theme_key,
            "fits": self.fits,
            "page_count": self.page_count,
            "overflow_container_ids": list(self.overflow_container_ids),
        }


@dataclass(frozen=True, slots=True)
class VersionProjection:
    version_id: str
    target_id: str | None
    target_source: str | None
    target_as_of: str | None
    policy_version: str
    policy_hash: str
    requested_pages: str
    selected_fact_ids: tuple[str, ...]
    elided_fact_ids: tuple[str, ...]
    fact_decisions: tuple[FactDecision, ...]
    overrides: OverrideSnapshot
    layout_feedback: tuple[LayoutFeedback, ...]
    feedback_digest: str
    condition_summary: tuple[tuple[str, int], ...] = ()
    condition_digest: str | None = None
    gap_allowed: bool = False
    digest: str = ""

    def _payload(self) -> dict[str, Any]:
        return {
            "version_id": self.version_id,
            "target_id": self.target_id,
            "target_source": self.target_source,
            "target_as_of": self.target_as_of,
            "policy_version": self.policy_version,
            "policy_hash": self.policy_hash,
            "requested_pages": self.requested_pages,
            "selected_fact_ids": list(self.selected_fact_ids),
            "elided_fact_ids": list(self.elided_fact_ids),
            "fact_decisions": [item.to_projection() for item in self.fact_decisions],
            "overrides": self.overrides.to_projection(),
            "layout_feedback": [item.to_projection() for item in self.layout_feedback],
            "feedback_digest": self.feedback_digest,
            "condition_summary": dict(self.condition_summary),
            "condition_digest": self.condition_digest,
            "gap_allowed": self.gap_allowed,
        }

    def to_projection(self) -> dict[str, Any]:
        return {**self._payload(), "digest": self.digest}

    def validate(self, known_fact_ids: Iterable[str]) -> None:
        known = frozenset(known_fact_ids)
        if not self.policy_version or len(self.policy_hash) != 64 or len(self.feedback_digest) != 64:
            raise CliError(TARGETING_PROJECTION_INVALID, "目标投影缺少策略或反馈绑定。")
        if len(self.selected_fact_ids) != len(set(self.selected_fact_ids)) or any(item not in known for item in self.selected_fact_ids):
            raise CliError(TARGETING_PROJECTION_INVALID, "目标投影包含未知或重复事实。")
        decisions = {item.fact_id: item for item in self.fact_decisions}
        if set(decisions) != known or any(item.core and not item.selected for item in decisions.values()):
            raise CliError(TARGETING_PROJECTION_INVALID, "目标投影 trace 不完整或排除了核心事实。")
        if tuple(item.theme_key for item in self.layout_feedback) != _THEMES or not all(item.fits for item in self.layout_feedback):
            raise CliError(TARGETING_PROJECTION_INVALID, "三主题布局反馈无效。")
        expected = hashlib.sha256(_json_bytes(self._payload())).hexdigest()
        if self.digest != expected:
            raise CliError(TARGETING_PROJECTION_INVALID, "目标投影摘要无效。")


def load_targeting_policy(path: Path | None = None) -> TargetingPolicy:
    policy_path = path or Path(__file__).resolve().parent.parent / "templates" / "targeting-policy.json"
    try:
        raw = policy_path.read_bytes()
        payload = json.loads(raw)
        if not isinstance(payload, dict) or set(payload) != _POLICY_FIELDS:
            raise ValueError
        version = payload["policy_version"]
        module_order = payload["module_order"]
        weights = payload["score_weights"]
        expansions = payload["exact_term_expansions"]
        predicates = payload["predicate_registry"]
        if not isinstance(version, str) or not version or not isinstance(module_order, list) or len(module_order) != len(set(module_order)):
            raise ValueError
        if module_order[:2] != ["candidate", "education"] or set(module_order) != {"candidate", "education", "skills", "certificates", "projects", "training", "experience"}:
            raise ValueError
        if not isinstance(weights, dict) or set(weights) != _SCORE_FIELDS or any(type(value) is not int or value < 0 for value in weights.values()):
            raise ValueError
        if not isinstance(expansions, dict) or any(not isinstance(key, str) or not key or not isinstance(values, list) or not values or any(not isinstance(value, str) or not value for value in values) for key, values in expansions.items()):
            raise ValueError
        expected_predicates = ["education_level", "major_exact", "certificate_exact", "fresh_graduate_status"]
        if predicates != expected_predicates:
            raise ValueError
        return TargetingPolicy(
            version,
            tuple(module_order),
            tuple((key, weights[key]) for key in sorted(weights)),
            tuple((key, tuple(expansions[key])) for key in sorted(expansions)),
            tuple(predicates),
            hashlib.sha256(raw).hexdigest(),
        )
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise CliError(TARGETING_POLICY_INVALID, "离线定向策略无效。") from exc


def _facts_by_section(facts: Mapping[str, Any], module_order: tuple[str, ...]) -> tuple[tuple[str, str, Mapping[str, Any]], ...]:
    result: list[tuple[str, str, Mapping[str, Any]]] = []
    candidate = facts.get("candidate")
    if not isinstance(candidate, Mapping) or not candidate:
        raise CliError(TARGETING_INPUT_INVALID, "已核实资料缺少个人信息。")
    result.append(("candidate", "profile", candidate))
    seen = {"profile"}
    for section in module_order[1:]:
        raw_items = facts.get(section, ())
        if raw_items is None:
            raw_items = ()
        if not isinstance(raw_items, (list, tuple)):
            raise CliError(TARGETING_INPUT_INVALID, "已核实事实模块必须是条目列表。")
        for item in raw_items:
            if not isinstance(item, Mapping) or not isinstance(item.get("id"), str) or not item["id"]:
                raise CliError(TARGETING_INPUT_INVALID, "已核实事实缺少稳定 ID。")
            fact_id = item["id"]
            if fact_id in seen:
                raise CliError(TARGETING_INPUT_INVALID, "已核实事实 ID 重复。")
            seen.add(fact_id)
            result.append((section, fact_id, item))
    return tuple(result)


def _override_snapshot(overrides: Mapping[str, Any] | None, known_ids: frozenset[str], core_ids: frozenset[str]) -> OverrideSnapshot:
    raw = overrides or {}
    if not isinstance(raw, Mapping) or set(raw) - _OVERRIDE_FIELDS:
        raise CliError(TARGETING_OVERRIDE_INVALID, "事实覆盖字段无效。")

    def values(name: str) -> tuple[str, ...]:
        items = raw.get(name, ())
        if not isinstance(items, (list, tuple)) or any(not isinstance(item, str) or not item for item in items):
            raise CliError(TARGETING_OVERRIDE_INVALID, "事实覆盖必须使用稳定 ID 列表。")
        if len(items) != len(set(items)) or any(item not in known_ids for item in items):
            raise CliError(TARGETING_OVERRIDE_INVALID, "事实覆盖包含重复或未知 ID。")
        return tuple(sorted(items))

    retain = values("retain")
    exclude = values("exclude")
    pin = values("pin")
    if core_ids.intersection(exclude) or set(retain).intersection(exclude) or set(pin).intersection(exclude):
        raise CliError(TARGETING_OVERRIDE_INVALID, "事实覆盖冲突或试图排除核心事实。")
    return OverrideSnapshot(retain, exclude, pin)


def _score_fact(item: Mapping[str, Any], facts: Mapping[str, Any], target: Mapping[str, Any] | None, policy: TargetingPolicy) -> tuple[int, tuple[str, ...]]:
    if target is None:
        return 0, ("generic-version",)
    weights = dict(policy.score_weights)
    text = " ".join(_flatten_text(item))
    role = _normalized(target.get("role"))
    requirements = tuple(_normalized(value) for value in target.get("requirements", ()) if isinstance(value, str) and _normalized(value))
    directions = tuple(_normalized(value) for value in facts.get("candidate", {}).get("directions", ()) if isinstance(value, str) and _normalized(value))
    score = 0
    reasons: list[str] = []
    if role and role in text:
        score += weights["role_exact"]
        reasons.append("role-exact")
    expansions = dict(policy.exact_term_expansions)
    expanded_terms = {term for key, values in expansions.items() if _normalized(key) in role for term in values}
    if any(_normalized(term) in text for term in expanded_terms):
        score += weights["role_expansion"]
        reasons.append("role-expansion")
    for requirement in requirements:
        if requirement in text:
            score += weights["requirement_exact"]
            reasons.append("requirement-exact")
    for direction in directions:
        if direction in role and any(part and part in text for part in direction.split()):
            score += weights["direction_exact"]
            reasons.append("direction-exact")
    return score, tuple(dict.fromkeys(reasons)) or ("no-relevance-match",)


def _feedback_fits(item: LayoutFeedback, request: PageBudgetRequest) -> bool:
    if item.theme_key not in _THEMES or type(item.fits) is not bool or item.page_count not in (1, 2, 3):
        raise CliError(TARGETING_INPUT_INVALID, "布局反馈无效。")
    if request.requested_pages == "auto":
        return item.fits and item.page_count <= 2
    return item.fits and item.page_count == int(request.requested_pages)


LayoutFeedbackCallback = Callable[[str, tuple[str, ...], PageBudgetRequest], LayoutFeedback]


def resolve_version_projection(
    facts: Mapping[str, Any],
    target: Mapping[str, Any] | None,
    page_budget: PageBudgetRequest,
    layout_feedback_callback: LayoutFeedbackCallback,
    *,
    overrides: Mapping[str, Any] | None = None,
    policy_path: Path | None = None,
) -> VersionProjection:
    policy = load_targeting_policy(policy_path)
    if target is not None:
        required = ("id", "company", "role", "source", "as_of")
        if target.get("confirmed") is not True or any(not isinstance(target.get(key), str) or not target[key] for key in required):
            raise CliError(TARGETING_INPUT_INVALID, "目标岗位必须是已确认且来源完整的用户输入。")
    entries = _facts_by_section(facts, policy.module_order)
    known_ids = frozenset(fact_id for _, fact_id, _ in entries)
    core_ids = frozenset(fact_id for section, fact_id, _ in entries if section in _CORE_SECTIONS)
    snapshot = _override_snapshot(overrides, known_ids, core_ids)
    retain = frozenset(snapshot.retain_ids)
    excluded = frozenset(snapshot.exclude_ids)
    pinned = frozenset(snapshot.pin_ids)
    section_index = {section: index for index, section in enumerate(policy.module_order)}
    scored = []
    for section, fact_id, item in entries:
        score, reasons = _score_fact(item, facts, target, policy)
        scored.append((section, fact_id, score, reasons))
    ordered = sorted(scored, key=lambda value: (section_index[value[0]], 0 if value[1] in pinned else 1, -value[2], value[1]))
    selected = [fact_id for _, fact_id, _, _ in ordered if fact_id not in excluded]
    removed_for_budget: list[str] = []
    final_feedback: tuple[LayoutFeedback, ...] = ()
    while True:
        selected_ids = tuple(selected)
        current = tuple(layout_feedback_callback(theme, selected_ids, page_budget) for theme in _THEMES)
        if tuple(item.theme_key for item in current) != _THEMES:
            raise CliError(TARGETING_INPUT_INVALID, "布局反馈主题顺序无效。")
        if all(_feedback_fits(item, page_budget) for item in current):
            final_feedback = tuple(replace(item, fits=True) for item in current)
            break
        removable = next((fact_id for fact_id in reversed(selected) if fact_id not in core_ids | retain | pinned), None)
        if removable is None:
            raise CliError(PAGE_BUDGET_UNSATISFIABLE, "核心、保留和置顶事实无法在三主题共享页数预算内完整排入。")
        selected.remove(removable)
        removed_for_budget.append(removable)
    selected_set = frozenset(selected)
    decisions: list[FactDecision] = []
    score_by_id = {fact_id: (section, score, reasons) for section, fact_id, score, reasons in scored}
    for section, fact_id, _, _ in ordered:
        actual_section, score, reasons = score_by_id[fact_id]
        is_selected = fact_id in selected_set
        reason_codes = reasons
        if fact_id in excluded:
            action = "exclude"
            reason_codes = (*reason_codes, "override-exclude")
        elif fact_id in removed_for_budget:
            action = "exclude"
            reason_codes = (*reason_codes, "page-budget")
        elif fact_id in pinned:
            action = "pin"
            reason_codes = (*reason_codes, "override-pin")
        elif score > 0:
            action = "emphasize"
        else:
            action = "select"
        if fact_id in retain:
            reason_codes = (*reason_codes, "override-retain")
        decisions.append(FactDecision(fact_id, actual_section, action, score, tuple(dict.fromkeys(reason_codes)), fact_id in core_ids, fact_id in retain, fact_id in pinned, is_selected))
    feedback_digest = hashlib.sha256(_json_bytes([item.to_projection() for item in final_feedback])).hexdigest()
    elided = tuple(item.fact_id for item in decisions if not item.selected)
    draft = VersionProjection(
        "generic" if target is None else str(target["id"]),
        None if target is None else str(target["id"]),
        None if target is None else str(target["source"]),
        None if target is None else str(target["as_of"]),
        policy.policy_version,
        policy.sha256,
        page_budget.requested_pages,
        tuple(selected),
        elided,
        tuple(decisions),
        snapshot,
        final_feedback,
        feedback_digest,
    )
    projection = replace(draft, digest=hashlib.sha256(_json_bytes(draft._payload())).hexdigest())
    projection.validate(known_ids)
    return projection


__all__ = [
    "FactDecision",
    "LayoutFeedback",
    "OverrideSnapshot",
    "PageBudgetRequest",
    "TargetingPolicy",
    "VersionProjection",
    "load_targeting_policy",
    "resolve_version_projection",
]
