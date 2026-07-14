#!/usr/bin/env python3
"""Native editable PPTX object helpers driven only by manifest geometry."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Iterable

from markdown_contract import inline_spans
from pptx_ooxml import set_run_highlight


MAX_MEDIA_BYTES = 16 * 1024 * 1024
MAX_MEDIA_PIXELS = 40_000_000
ALLOWED_MEDIA_FORMATS = {"JPEG", "PNG"}


class PptxObjectError(RuntimeError):
    pass


def normalize_rich_text(authored: str) -> tuple[tuple[str, str], ...]:
    """Remove inline delimiters once and preserve authored visible-text order."""
    spans = inline_spans(authored)
    segments: list[tuple[str, str]] = []
    cursor = 0
    for span in spans:
        start, end = int(span["start"]), int(span["end"])
        if start < cursor:
            raise PptxObjectError("PPTX_INLINE_SPAN_OVERLAP")
        if start > cursor:
            segments.append(("plain", authored[cursor:start]))
        segments.append((str(span["kind"]), str(span["text"])))
        cursor = end
    if cursor < len(authored):
        segments.append(("plain", authored[cursor:]))
    return tuple(segment for segment in segments if segment[1]) or (("plain", ""),)


def _geometry(value: dict[str, int]) -> tuple[int, int, int, int]:
    return value["x"], value["y"], value["width"], value["height"]


def _configure_text_frame(
    text_frame: Any,
    *,
    margin_left_points: float = 0.0,
    margin_right_points: float = 0.0,
    margin_top_points: float = 0.0,
    margin_bottom_points: float = 0.0,
) -> None:
    from pptx.enum.text import MSO_AUTO_SIZE
    from pptx.util import Pt

    text_frame.clear()
    text_frame.word_wrap = True
    text_frame.auto_size = MSO_AUTO_SIZE.NONE
    text_frame.margin_left = Pt(margin_left_points)
    text_frame.margin_right = Pt(margin_right_points)
    text_frame.margin_top = Pt(margin_top_points)
    text_frame.margin_bottom = Pt(margin_bottom_points)


def add_rich_text(
    slide: Any,
    geometry: dict[str, int],
    authored: str,
    *,
    font_size: float,
    highlight_scheme: str,
    name: str,
    monospace: bool = False,
) -> Any:
    from pptx.util import Pt

    shape = slide.shapes.add_textbox(*_geometry(geometry))
    shape.name = name
    text_frame = shape.text_frame
    _configure_text_frame(text_frame)
    paragraph = text_frame.paragraphs[0]
    for kind, text in normalize_rich_text(authored):
        run = paragraph.add_run()
        run.text = text
        run.font.size = Pt(font_size)
        if monospace:
            run.font.name = "Consolas"
        if kind == "bold":
            run.font.bold = True
        elif kind == "highlight":
            set_run_highlight(run, highlight_scheme)
    return shape


def add_literal_text(
    slide: Any,
    geometry: dict[str, int],
    text: str,
    *,
    font_size: float,
    name: str,
    font_name: str = "Consolas",
) -> Any:
    from pptx.util import Pt

    shape = slide.shapes.add_textbox(*_geometry(geometry))
    shape.name = name
    text_frame = shape.text_frame
    _configure_text_frame(text_frame)
    paragraph = text_frame.paragraphs[0]
    run = paragraph.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.name = font_name
    return shape


def add_fragment_text_frame(
    slide: Any,
    geometry: dict[str, int],
    fragments: Iterable[Any],
    *,
    font_size: float,
    highlight_scheme: str,
    name: str,
    margin_left_points: float,
    margin_right_points: float,
    margin_top_points: float,
    margin_bottom_points: float,
    line_spacing: float,
    paragraph_spacing_points: float,
    code_font_name: str = "Consolas",
) -> Any:
    from pptx.util import Pt

    shape = slide.shapes.add_textbox(*_geometry(geometry))
    shape.name = name
    text_frame = shape.text_frame
    _configure_text_frame(
        text_frame,
        margin_left_points=margin_left_points,
        margin_right_points=margin_right_points,
        margin_top_points=margin_top_points,
        margin_bottom_points=margin_bottom_points,
    )
    first_paragraph = True

    def append_rich_paragraph(authored: str) -> None:
        nonlocal first_paragraph
        paragraph = text_frame.paragraphs[0] if first_paragraph else text_frame.add_paragraph()
        first_paragraph = False
        paragraph.line_spacing = line_spacing
        paragraph.space_after = Pt(paragraph_spacing_points)
        for kind, text in normalize_rich_text(authored):
            run = paragraph.add_run()
            run.text = text
            run.font.size = Pt(font_size)
            if kind == "bold":
                run.font.bold = True
            elif kind == "highlight":
                set_run_highlight(run, highlight_scheme)

    for fragment in fragments:
        if fragment.heading:
            append_rich_paragraph(fragment.heading)
        if fragment.kind == "code":
            paragraph = text_frame.paragraphs[0] if first_paragraph else text_frame.add_paragraph()
            first_paragraph = False
            paragraph.line_spacing = line_spacing
            paragraph.space_after = Pt(paragraph_spacing_points)
            run = paragraph.add_run()
            run.text = fragment.text
            run.font.size = Pt(font_size)
            run.font.name = code_font_name
        elif fragment.items:
            for item in fragment.items:
                append_rich_paragraph(item)
        elif fragment.text is not None:
            append_rich_paragraph(fragment.text)
    return shape


def add_plain_lines(
    slide: Any, geometry: dict[str, int], lines: Iterable[str], *, font_size: float,
    highlight_scheme: str, name: str, monospace: bool = False
) -> Any:
    return add_rich_text(
        slide, geometry, "\n".join(lines), font_size=font_size, highlight_scheme=highlight_scheme,
        name=name, monospace=monospace,
    )


def add_table(
    slide: Any, slot: dict[str, Any], fragment: Any, *, font_size: float,
    row_heights_emu: tuple[int, ...],
) -> tuple[Any, Any]:
    from pptx.util import Pt

    geometry = slot["geometry"]
    table_name_geometry = slot["subregions"]["table_name"]["geometry"]
    table_name = dict(fragment.metadata).get("table_name", "")
    name_shape = slide.shapes.add_textbox(*_geometry(table_name_geometry))
    name_shape.name = "school-pptx:table-name"
    _configure_text_frame(name_shape.text_frame)
    name_shape.text_frame.paragraphs[0].text = table_name
    if name_shape.text_frame.paragraphs[0].runs:
        name_shape.text_frame.paragraphs[0].runs[0].font.size = Pt(
            slot["subregions"]["table_name"]["text_budget"]["font_size_max"]
        )

    rows = fragment.rows or (("",),)
    if len(row_heights_emu) != len(rows) or any(not isinstance(value, int) or value <= 0 for value in row_heights_emu):
        raise PptxObjectError("PPTX_TABLE_ROW_HEIGHT_MISMATCH")
    columns = max(1, max(len(row) for row in rows))
    table_y = table_name_geometry["y"] + table_name_geometry["height"]
    table_height = geometry["y"] + geometry["height"] - table_y
    graphic = slide.shapes.add_table(len(rows), columns, geometry["x"], table_y, geometry["width"], table_height)
    graphic.name = "school-pptx:native-table"
    table = graphic.table
    for column in table.columns:
        column.width = int(geometry["width"] / columns)
    for row, height in zip(table.rows, row_heights_emu):
        row.height = height
    for row_index, values in enumerate(rows):
        for column_index in range(columns):
            cell = table.cell(row_index, column_index)
            cell.text = values[column_index] if column_index < len(values) else ""
            for paragraph in cell.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(font_size)
                    run.font.bold = row_index == 0
    return name_shape, graphic


def _safe_image_size(path: Path) -> tuple[int, int]:
    from PIL import Image, UnidentifiedImageError

    if path.stat().st_size > MAX_MEDIA_BYTES:
        raise PptxObjectError("PPTX_MEDIA_SIZE_LIMIT")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as image:
                if image.format not in ALLOWED_MEDIA_FORMATS:
                    raise PptxObjectError("PPTX_MEDIA_FORMAT_INVALID")
                width, height = image.size
                if width <= 0 or height <= 0 or width * height > MAX_MEDIA_PIXELS:
                    raise PptxObjectError("PPTX_MEDIA_PIXEL_LIMIT")
                image.verify()
    except PptxObjectError:
        raise
    except (Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise PptxObjectError("PPTX_MEDIA_PIXEL_LIMIT") from None
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
        raise PptxObjectError("PPTX_MEDIA_FORMAT_INVALID") from None
    return width, height


def add_contain_picture(slide: Any, path: Path | None, geometry: dict[str, int], *, name: str) -> Any:
    if path is None or not path.is_file():
        from pptx.enum.shapes import MSO_SHAPE

        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, *_geometry(geometry))
        shape.name = name.replace("picture", "missing-media")
        shape.text = "媒体缺失"
        return shape
    width, height = _safe_image_size(path)
    scale = min(geometry["width"] / width, geometry["height"] / height)
    target_width, target_height = int(width * scale), int(height * scale)
    left = geometry["x"] + int((geometry["width"] - target_width) / 2)
    top = geometry["y"] + int((geometry["height"] - target_height) / 2)
    picture = slide.shapes.add_picture(str(path), left, top, target_width, target_height)
    picture.name = name
    picture.crop_left = picture.crop_top = picture.crop_right = picture.crop_bottom = 0
    return picture


def add_gallery_card(
    slide: Any, preset: dict[str, Any], path: Path | None, caption: str, *, index: int,
    highlight_scheme: str, font_size: float
) -> Any:
    picture = add_contain_picture(slide, path, preset["picture"], name=f"school-pptx:gallery-picture:{index}")
    caption_shape = add_rich_text(
        slide, preset["caption"], caption, font_size=font_size, highlight_scheme=highlight_scheme,
        name=f"school-pptx:gallery-caption:{index}",
    )
    group = slide.shapes.add_group_shape((picture, caption_shape))
    group.name = f"school-pptx:gallery-card:{index}"
    return group


def add_timeline(slide: Any, slot: dict[str, Any], rows: tuple[tuple[str, ...], ...], *, highlight_scheme: str) -> list[Any]:
    from pptx.enum.shapes import MSO_SHAPE

    axis_geometry = slot["subregions"]["axis"]["geometry"]
    axis = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, *_geometry(axis_geometry))
    axis.name = "school-pptx:timeline-axis"
    results: list[Any] = [axis]
    node_band = slot["subregions"]["node_band"]["geometry"]
    template = slot["node_template"]
    count = max(1, len(rows))
    node_width = int(node_band["width"] / count)
    for index, row in enumerate(rows):
        base_x = node_band["x"] + index * node_width
        shapes: list[Any] = []
        for role, value in zip(("time", "title", "description"), (*row, "", "")[:3]):
            local = template["subregions"][role]["geometry"]
            geometry = {
                "x": base_x + int(local["x"] * node_width / template["geometry"]["width"]),
                "y": node_band["y"] + local["y"],
                "width": max(1, int(local["width"] * node_width / template["geometry"]["width"])),
                "height": local["height"],
            }
            budget = template["subregions"][role]["text_budget"]
            shapes.append(add_rich_text(
                slide, geometry, value, font_size=budget["font_size_min"], highlight_scheme=highlight_scheme,
                name=f"school-pptx:timeline-{role}:{index}",
            ))
        marker_local = template["subregions"]["marker"]["geometry"]
        marker = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            base_x + int(marker_local["x"] * node_width / template["geometry"]["width"]),
            node_band["y"] + marker_local["y"],
            marker_local["width"], marker_local["height"],
        )
        marker.name = f"school-pptx:timeline-marker:{index}"
        shapes.append(marker)
        group = slide.shapes.add_group_shape(shapes)
        group.name = f"school-pptx:timeline-node:{index}"
        results.append(group)
    return results


def set_notes(slide: Any, notes: str | None) -> None:
    if notes is None:
        return
    text_frame = slide.notes_slide.notes_text_frame
    if text_frame is None:
        raise PptxObjectError("PPTX_NOTES_FRAME_MISSING")
    text_frame.text = notes
