#!/usr/bin/env python3
"""Narrow OOXML compatibility helpers for controlled PPTX emission."""

from __future__ import annotations

from typing import Any


def remove_seed_slides(presentation: Any) -> tuple[int, int]:
    """Remove every template seed slide and its presentation relationship."""
    removed = 0
    notes_relationships = 0
    slide_ids = presentation.slides._sldIdLst
    for slide_id in list(slide_ids):
        slide = presentation.part.related_part(slide_id.rId)
        notes_relationships += int(any(
            relationship.reltype
            == "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide"
            for relationship in slide.part.rels.values()
        ))
        presentation.part.drop_rel(slide_id.rId)
        slide_ids.remove(slide_id)
        removed += 1
    if len(presentation.slides) != 0:
        raise ValueError("PPTX_TEMPLATE_SEED_REMOVAL_FAILED")
    return removed, notes_relationships


def set_run_highlight(run: Any, scheme_color: str) -> None:
    """Set one theme-scheme run highlight without disturbing other run properties."""
    from pptx.oxml.xmlchemy import OxmlElement

    run_properties = run._r.get_or_add_rPr()
    for existing in list(run_properties):
        if existing.tag.endswith("}highlight"):
            run_properties.remove(existing)
    highlight = OxmlElement("a:highlight")
    color = OxmlElement("a:schemeClr")
    color.set("val", scheme_color)
    highlight.append(color)
    run_properties.insert_element_before(
        highlight,
        "a:uLnTx", "a:uLn", "a:uFillTx", "a:uFill", "a:latin", "a:ea", "a:cs", "a:sym",
        "a:hlinkClick", "a:hlinkMouseOver", "a:rtl", "a:extLst",
    )
