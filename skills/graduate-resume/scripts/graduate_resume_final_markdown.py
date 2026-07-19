"""Deterministic, reparsable final Markdown delivery checkpoint."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from graduate_resume_cli import CliError, is_stable_fact_id
from graduate_resume_targeting import VersionProjection

FINAL_MARKDOWN_INVALID = "FINAL_MARKDOWN_INVALID"
FINAL_SCHEMA = "graduate-resume-delivery/v1"
_THEMES = {"conservative": "保守稳妥", "modern": "现代简洁", "expressive": "个性设计"}
_FIELDS = (
    "schema", "canonical_hash", "targeting_policy", "version", "target", "theme",
    "page_count", "photo_mode", "selected_fact_ids", "overrides", "trace",
    "conditions", "body_sha256", "binding_sha256",
)
_SOURCE_URL_RE = re.compile(
    r"(?i)^(?:[a-z][a-z0-9+.-]*://|www\.|(?:[a-z0-9-]+\.)+[a-z]{2,}(?:[/?#].*)?$)"
)
_TARGET_FIELDS = {"id", "company", "role", "source", "as_of"}


@dataclass(frozen=True, slots=True)
class FinalResumeFact:
    fact_id: str
    section: str
    data: tuple[tuple[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return dict(self.data)


@dataclass(frozen=True, slots=True)
class FinalResumeDocument:
    path: Path | None
    canonical_hash: str
    policy_version: str
    policy_hash: str
    version_kind: str
    version_id: str
    target_id: str | None
    target_company: str | None
    target_role: str | None
    target_source: str | None
    target_as_of: str | None
    theme_key: str
    theme_label: str
    page_count: int
    photo_mode: str
    selected_fact_ids: tuple[str, ...]
    overrides: tuple[tuple[str, tuple[str, ...]], ...]
    trace_summary: tuple[tuple[str, int], ...]
    trace_digest: str
    condition_counts: tuple[tuple[str, int], ...]
    condition_digest: str | None
    gap_allowed: bool
    facts: tuple[FinalResumeFact, ...]
    body_sha256: str
    binding_sha256: str
    normalized_photo_png: bytes | None = None

    def fact_view(self) -> dict[str, Any]:
        result: dict[str, Any] = {key: [] for key in ("education", "skills", "certificates", "projects", "training", "experience")}
        for fact in self.facts:
            if fact.fact_id == "profile":
                result["candidate"] = fact.as_dict()
            else:
                result.setdefault(fact.section, []).append(fact.as_dict())
        return result


def _error() -> CliError:
    return CliError(FINAL_MARKDOWN_INVALID, "最终 Markdown 校验失败。")


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _all_facts(facts: Mapping[str, Any]) -> dict[str, tuple[str, Mapping[str, Any]]]:
    result: dict[str, tuple[str, Mapping[str, Any]]] = {}
    candidate = facts.get("candidate")
    if isinstance(candidate, Mapping) and candidate.get("status") == "verified":
        result["profile"] = ("candidate", candidate)
    for section in ("education", "skills", "certificates", "projects", "training", "experience"):
        for item in facts.get(section, ()) or ():
            if not isinstance(item, Mapping) or item.get("status") != "verified" or not is_stable_fact_id(item.get("id")):
                continue
            if item["id"] in result:
                raise _error()
            result[item["id"]] = (section, item)
    return result


def _body(selected: tuple[str, ...], facts: Mapping[str, Any]) -> bytes:
    known = _all_facts(facts)
    if len(selected) != len(set(selected)) or any(fact_id not in known for fact_id in selected):
        raise _error()
    lines = ["# 最终简历", ""]
    for fact_id in selected:
        section, item = known[fact_id]
        lines.extend((f"## {section}", f"<!-- final-resume-fact: {fact_id} -->", "```json", _json_bytes(item).decode("utf-8"), "```", ""))
    return ("\n".join(lines).rstrip() + "\n").encode("utf-8")


def _trace_summary(projection: VersionProjection) -> dict[str, int]:
    return {
        "selected": len(projection.selected_fact_ids),
        "elided": len(projection.elided_fact_ids),
        "retained": sum(item.retained for item in projection.fact_decisions),
        "pinned": sum(item.pinned for item in projection.fact_decisions),
    }


def _validate_target_metadata(
    target: Mapping[str, Any], version_id: Any, *, exact_fields: bool,
) -> None:
    if not isinstance(target, Mapping) or (exact_fields and set(target) != _TARGET_FIELDS):
        raise _error()
    if any(not isinstance(target.get(field), str) or not target[field].strip() for field in _TARGET_FIELDS):
        raise _error()
    if target["id"] != version_id or _SOURCE_URL_RE.match(target["source"].strip()):
        raise _error()


def emit_final_markdown(
    facts: Mapping[str, Any], projection: VersionProjection, *, canonical_hash: str,
    theme_key: str, theme_label: str | None = None, page_count: int,
    photo_mode: str, target: Mapping[str, Any] | None = None,
) -> bytes:
    if not isinstance(projection, VersionProjection) or not re.fullmatch(r"[0-9a-f]{64}", canonical_hash):
        raise _error()
    if theme_key not in _THEMES or page_count not in (1, 2) or photo_mode not in {"photo", "no-photo"}:
        raise _error()
    kind = "generic" if projection.target_id is None else "target"
    if kind == "generic":
        if target is not None or projection.target_source is not None or projection.target_as_of is not None:
            raise _error()
        target_data = None
    else:
        if not isinstance(target, Mapping) or target.get("id") != projection.target_id:
            raise _error()
        target_data = {
            "id": projection.target_id, "company": target.get("company"), "role": target.get("role"),
            "source": projection.target_source, "as_of": projection.target_as_of,
        }
        _validate_target_metadata(target_data, projection.version_id, exact_fields=True)
    body = _body(projection.selected_fact_ids, facts)
    metadata: dict[str, Any] = {
        "schema": FINAL_SCHEMA,
        "canonical_hash": canonical_hash,
        "targeting_policy": {"version": projection.policy_version, "sha256": projection.policy_hash},
        "version": {"kind": kind, "id": projection.version_id},
        "target": target_data,
        "theme": {"key": theme_key, "label": theme_label or _THEMES[theme_key]},
        "page_count": page_count,
        "photo_mode": photo_mode,
        "selected_fact_ids": list(projection.selected_fact_ids),
        "overrides": projection.overrides.to_projection(),
        "trace": {"summary": _trace_summary(projection), "digest": projection.digest},
        "conditions": {
            "counts": dict(projection.condition_summary), "evidence_digest": projection.condition_digest,
            "gap_allowed": projection.gap_allowed,
        },
        "body_sha256": hashlib.sha256(body).hexdigest(),
    }
    metadata["binding_sha256"] = hashlib.sha256(_json_bytes(metadata) + b"\0" + body).hexdigest()
    frontmatter = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, default_flow_style=False).encode("utf-8")
    return b"---\n" + frontmatter + b"---\n" + body


def _parse_body(body: bytes) -> tuple[FinalResumeFact, ...]:
    pattern = re.compile(rb"^## ([a-z-]+)\n<!-- final-resume-fact: ([^\n]+) -->\n```json\n([^\n]+)\n```$", re.MULTILINE)
    facts: list[FinalResumeFact] = []
    for match in pattern.finditer(body):
        try:
            section = match.group(1).decode("ascii")
            fact_id = match.group(2).decode("utf-8")
            data = json.loads(match.group(3))
            if (
                not isinstance(data, dict)
                or data.get("status") != "verified"
                or not is_stable_fact_id(fact_id, profile=fact_id == "profile")
                or (fact_id != "profile" and data.get("id") != fact_id)
            ):
                raise ValueError
            facts.append(FinalResumeFact(fact_id, section, tuple(data.items())))
        except (UnicodeError, ValueError, json.JSONDecodeError) as exc:
            raise _error() from exc
    expected = _body(tuple(item.fact_id for item in facts), {"candidate": facts[0].as_dict() if facts and facts[0].fact_id == "profile" else {}, **{section: [item.as_dict() for item in facts if item.section == section] for section in ("education", "skills", "certificates", "projects", "training", "experience")}})
    if body != expected:
        raise _error()
    return tuple(facts)


def load_final_resume(path: Path | str) -> FinalResumeDocument:
    actual_path = Path(path)
    try:
        raw = actual_path.read_bytes()
        if not raw.startswith(b"---\n"):
            raise ValueError
        frontmatter, body = raw[4:].split(b"---\n", 1)
        metadata = yaml.safe_load(frontmatter)
        if not isinstance(metadata, dict) or tuple(metadata) != _FIELDS:
            raise ValueError
        binding = metadata.pop("binding_sha256")
        expected_binding = hashlib.sha256(_json_bytes(metadata) + b"\0" + body).hexdigest()
        metadata["binding_sha256"] = binding
        if binding != expected_binding or metadata["schema"] != FINAL_SCHEMA or hashlib.sha256(body).hexdigest() != metadata["body_sha256"]:
            raise ValueError
        if not re.fullmatch(r"[0-9a-f]{64}", metadata["canonical_hash"]):
            raise ValueError
        policy, version, target, theme = metadata["targeting_policy"], metadata["version"], metadata["target"], metadata["theme"]
        if set(policy) != {"version", "sha256"} or not re.fullmatch(r"[0-9a-f]{64}", policy["sha256"]):
            raise ValueError
        if set(version) != {"kind", "id"} or version["kind"] not in {"generic", "target"}:
            raise ValueError
        if version["kind"] == "generic" and target is not None:
            raise ValueError
        if version["kind"] == "target":
            _validate_target_metadata(target, version["id"], exact_fields=True)
        if set(theme) != {"key", "label"} or theme["key"] not in _THEMES or theme["label"] != _THEMES[theme["key"]]:
            raise ValueError
        if metadata["page_count"] not in (1, 2) or metadata["photo_mode"] not in {"photo", "no-photo"}:
            raise ValueError
        facts = _parse_body(body)
        selected = tuple(metadata["selected_fact_ids"])
        if selected != tuple(item.fact_id for item in facts):
            raise ValueError
        conditions = metadata["conditions"]
        if set(conditions) != {"counts", "evidence_digest", "gap_allowed"} or set(conditions["counts"]) - {"meets", "gap", "unknown", "not-applicable"}:
            raise ValueError
        overrides = metadata["overrides"]
        if set(overrides) != {"retain_ids", "exclude_ids", "pin_ids"}:
            raise ValueError
        trace = metadata["trace"]
        if set(trace) != {"summary", "digest"} or not re.fullmatch(r"[0-9a-f]{64}", trace["digest"]):
            raise ValueError
        return FinalResumeDocument(
            actual_path, metadata["canonical_hash"], policy["version"], policy["sha256"],
            version["kind"], version["id"], None if target is None else target["id"],
            None if target is None else target["company"], None if target is None else target["role"],
            None if target is None else target["source"], None if target is None else target["as_of"],
            theme["key"], theme["label"], metadata["page_count"], metadata["photo_mode"], selected,
            tuple((key, tuple(value)) for key, value in overrides.items()), tuple(trace["summary"].items()),
            trace["digest"], tuple(conditions["counts"].items()), conditions["evidence_digest"],
            conditions["gap_allowed"], facts, metadata["body_sha256"], binding,
        )
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as exc:
        if isinstance(exc, CliError):
            raise
        raise _error() from exc


__all__ = ["FinalResumeDocument", "FinalResumeFact", "emit_final_markdown", "load_final_resume"]
