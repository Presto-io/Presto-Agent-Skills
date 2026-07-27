#!/usr/bin/env python3
"""Frozen renderer-plan models shared by pagination and PPTX emission."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from typing import Any

from markdown_contract import inline_spans


VISUAL_PLAN_SCHEMA = "school-pptx/visual-plan/v1"
PHYSICAL_PLAN_SCHEMA = "school-pptx/physical-plan/v3"


def canonical_json(value: object) -> bytes:
    """Encode a projection once, with an explicit stable JSON contract."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def projection_sha256(value: object) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class MediaBinding:
    """Identity captured from one safe descriptor read, never a reusable path."""
    logical_reference: str
    source_line: int
    sha256: str | None
    byte_count: int
    media_format: str | None
    placement: str
    confirmed: bool
    diagnostic_code: str | None = None
    payload: bytes | None = None
    caption: str = ""

    def to_projection(self) -> dict[str, Any]:
        return {
            "logical_reference": self.logical_reference,
            "source_line": self.source_line,
            "sha256": self.sha256,
            "byte_count": self.byte_count,
            "media_format": self.media_format,
            "placement": self.placement,
            "confirmed": self.confirmed,
            "diagnostic_code": self.diagnostic_code,
            "caption": self.caption,
        }


@dataclass(frozen=True, slots=True)
class VisualSlide:
    logical_index: int
    source_line: int
    layout: str
    title: str
    visual_semantics: tuple[tuple[str, str], ...]
    candidate_capacity: tuple[tuple[str, tuple[int, ...]], ...]
    object_roles: tuple[str, ...]
    media_bindings: tuple[MediaBinding, ...] = ()

    def to_projection(self) -> dict[str, Any]:
        return {
            "logical_index": self.logical_index,
            "source_line": self.source_line,
            "layout": self.layout,
            "title": self.title,
            "visual_semantics": {key: value for key, value in self.visual_semantics},
            "candidate_capacity": [
                {"name": name, "values": list(values)} for name, values in self.candidate_capacity
            ],
            "object_roles": list(self.object_roles),
            "media_bindings": [binding.to_projection() for binding in self.media_bindings],
        }


@dataclass(frozen=True, slots=True)
class VisualPlan:
    markdown_sha256: str
    manifest_sha256: str
    template_sha256: str
    slides: tuple[VisualSlide, ...]
    diagnostics: tuple["RenderDiagnostic", ...] = ()
    schema_version: str = VISUAL_PLAN_SCHEMA

    def to_projection(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "markdown_sha256": self.markdown_sha256,
            "manifest_sha256": self.manifest_sha256,
            "template_sha256": self.template_sha256,
            "slides": [slide.to_projection() for slide in self.slides],
            "diagnostics": [diagnostic.to_projection() for diagnostic in self.diagnostics],
        }

    @property
    def sha256(self) -> str:
        return projection_sha256(self.to_projection())


@dataclass(frozen=True, slots=True)
class ParagraphProjection:
    role: str
    authored_text: str
    visible_text: str


def _visible_rich_text(authored: str) -> str:
    spans = inline_spans(authored)
    parts: list[str] = []
    cursor = 0
    for span in spans:
        start, end = int(span["start"]), int(span["end"])
        if start < cursor:
            raise ValueError("overlapping inline spans")
        parts.append(authored[cursor:start])
        parts.append(str(span["text"]))
        cursor = end
    parts.append(authored[cursor:])
    return "".join(parts)


def fragment_paragraph_sequence(fragment: "BlockFragment") -> tuple[ParagraphProjection, ...]:
    """Return authored and visible text for every emitted paragraph."""
    sequence: list[ParagraphProjection] = []

    def append(role: str, authored: str) -> None:
        visible = authored if role == "code" else _visible_rich_text(authored)
        sequence.append(ParagraphProjection(role, authored, visible))

    if fragment.heading:
        append("heading", fragment.heading)
    if fragment.kind == "code":
        if fragment.text is not None:
            append("code", fragment.text)
    elif fragment.items:
        for item in fragment.items:
            append("list", item)
    elif fragment.text:
        append("paragraph", fragment.text)
    return tuple(sequence)


@dataclass(frozen=True, slots=True)
class RenderDiagnostic:
    code: str
    message: str
    severity: str
    source_line: int
    logical_indices: tuple[int, ...] = ()
    physical_indices: tuple[int, ...] = ()
    fix: str = ""

    def to_projection(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "source_line": self.source_line,
            "logical_indices": list(self.logical_indices),
            "physical_indices": list(self.physical_indices),
            "fix": self.fix,
        }


@dataclass(frozen=True, slots=True)
class BlockFragment:
    kind: str
    logical_index: int
    block_index: int
    fragment_index: int
    source_line: int
    heading: str | None = None
    text: str | None = None
    items: tuple[str, ...] = ()
    rows: tuple[tuple[str, ...], ...] = ()
    metadata: tuple[tuple[str, str], ...] = ()
    target_slot: str | None = None
    row_heights_emu: tuple[int, ...] = ()

    def to_projection(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "logical_index": self.logical_index,
            "block_index": self.block_index,
            "fragment_index": self.fragment_index,
            "source_line": self.source_line,
            "heading": self.heading,
            "text": self.text,
            "items": list(self.items),
            "rows": [list(row) for row in self.rows],
            "metadata": {key: value for key, value in self.metadata},
            "target_slot": self.target_slot,
            "row_heights_emu": list(self.row_heights_emu),
        }


@dataclass(frozen=True, slots=True)
class PhysicalSlide:
    logical_index: int
    physical_index: int
    layout: str
    title: str
    fragment_index: int
    source_line: int
    fragments: tuple[BlockFragment, ...]
    notes_intent: str | None = None
    selected_font_sizes: tuple[tuple[str, float], ...] = ()
    affected_pages: tuple[int, ...] = ()
    slot_values: tuple[tuple[str, str], ...] = ()
    continuation: int = 0
    variant: str | None = None
    preset_id: str | None = None
    candidate_capacity: tuple[tuple[str, tuple[int, ...]], ...] = ()
    object_roles: tuple[str, ...] = ()
    atomic_groups: tuple[tuple[str, ...], ...] = ()
    media_bindings: tuple[MediaBinding, ...] = ()

    def to_projection(self) -> dict[str, Any]:
        return {
            "logical_index": self.logical_index,
            "physical_index": self.physical_index,
            "layout": self.layout,
            "title": self.title,
            "fragment_index": self.fragment_index,
            "source_line": self.source_line,
            "fragments": [fragment.to_projection() for fragment in self.fragments],
            "notes_intent": self.notes_intent,
            "selected_font_sizes": {key: value for key, value in self.selected_font_sizes},
            "affected_pages": list(self.affected_pages),
            "slot_values": {key: value for key, value in self.slot_values},
            "continuation": self.continuation,
            "variant": self.variant,
            "preset_id": self.preset_id,
            "candidate_capacity": [
                {"name": name, "values": list(values)} for name, values in self.candidate_capacity
            ],
            "object_roles": list(self.object_roles),
            "atomic_groups": [list(group) for group in self.atomic_groups],
            "media_bindings": [binding.to_projection() for binding in self.media_bindings],
        }


@dataclass(frozen=True, slots=True)
class PhysicalDeckPlan:
    slides: tuple[PhysicalSlide, ...]
    diagnostics: tuple[RenderDiagnostic, ...] = ()
    logical_to_physical: tuple[tuple[int, tuple[int, ...]], ...] = ()
    visual_plan_sha256: str | None = None
    markdown_sha256: str | None = None
    manifest_sha256: str | None = None
    template_sha256: str | None = None
    # Generated by the planner from ``integrity_projection``.  It is deliberately
    # excluded from that projection so a plan cannot validate itself by carrying a
    # self-referential hash.
    integrity_sha256: str | None = None
    schema_version: str = PHYSICAL_PLAN_SCHEMA

    def integrity_projection(self) -> dict[str, Any]:
        """Return every planner-owned decision that an emitter must not alter."""
        return {
            "schema_version": self.schema_version,
            "visual_plan_sha256": self.visual_plan_sha256,
            "markdown_sha256": self.markdown_sha256,
            "manifest_sha256": self.manifest_sha256,
            "template_sha256": self.template_sha256,
            "slides": [slide.to_projection() for slide in self.slides],
            "diagnostics": [diagnostic.to_projection() for diagnostic in self.diagnostics],
            "logical_to_physical": [
                {"logical_index": logical_index, "physical_indices": list(physical_indices)}
                for logical_index, physical_indices in self.logical_to_physical
            ],
        }

    def to_projection(self) -> dict[str, Any]:
        projection = self.integrity_projection()
        projection["integrity_sha256"] = self.integrity_sha256
        return projection

    @property
    def expected_integrity_sha256(self) -> str:
        return projection_sha256(self.integrity_projection())

    @property
    def sha256(self) -> str:
        return projection_sha256(self.to_projection())


def bind_physical_plan_integrity(plan: PhysicalDeckPlan) -> PhysicalDeckPlan:
    """Attach the planner-generated, non-self-referential physical-plan binding."""
    return replace(plan, integrity_sha256=plan.expected_integrity_sha256)
