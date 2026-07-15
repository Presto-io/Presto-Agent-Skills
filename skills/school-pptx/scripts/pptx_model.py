#!/usr/bin/env python3
"""Frozen renderer-plan models shared by pagination and PPTX emission."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from markdown_contract import inline_spans


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
        }


@dataclass(frozen=True, slots=True)
class PhysicalDeckPlan:
    slides: tuple[PhysicalSlide, ...]
    diagnostics: tuple[RenderDiagnostic, ...] = ()
    logical_to_physical: tuple[tuple[int, tuple[int, ...]], ...] = ()

    def to_projection(self) -> dict[str, Any]:
        return {
            "slides": [slide.to_projection() for slide in self.slides],
            "diagnostics": [diagnostic.to_projection() for diagnostic in self.diagnostics],
            "logical_to_physical": [
                {"logical_index": logical_index, "physical_indices": list(physical_indices)}
                for logical_index, physical_indices in self.logical_to_physical
            ],
        }
