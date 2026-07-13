#!/usr/bin/env python3
"""Pure, deterministic pagination measurement primitives for school-pptx."""

from __future__ import annotations

import json
import math
import re
import unicodedata
from dataclasses import FrozenInstanceError, dataclass, replace
from typing import Any, Iterator, Sequence

from pptx_model import BlockFragment, PhysicalDeckPlan, PhysicalSlide, RenderDiagnostic


MAX_TEXT_BYTES = 2 * 1024 * 1024
MAX_LOGICAL_LINES = 2048
MAX_BLOCKS = 2048
MAX_PARTITION_STATES = 200_000
EMU_PER_POINT = 12700
NO_LINE_START = frozenset("，。！？；：、）》】」』〉…,.!?;:%)]}")
NO_LINE_END = frozenset("《（【「『〈([{“‘")
STRONG_BREAK = frozenset("。！？!?；;")
WEAK_BREAK = frozenset("，、：:,")
TRAILING_CLOSERS = frozenset('"\'”’）》】」』〉)]}')


@dataclass(frozen=True, slots=True)
class TextMeasurement:
    display_lines: int
    height_points: float
    break_opportunities: tuple[int, ...]
    font_size: float
    fallback_used: bool

    def to_projection(self) -> dict[str, object]:
        return {
            "display_lines": self.display_lines,
            "height_points": self.height_points,
            "break_opportunities": list(self.break_opportunities),
            "font_size": self.font_size,
            "fallback_used": self.fallback_used,
        }


def clamp_font_size(value: float, minimum: float, maximum: float) -> float:
    if minimum < 0 or maximum < minimum:
        raise ValueError("invalid manifest font-size bounds")
    return float(min(max(value, minimum), maximum))


def grapheme_clusters(text: str) -> Iterator[tuple[str, int]]:
    cluster = ""
    start = 0
    join_next = False
    for index, character in enumerate(text):
        combining = bool(unicodedata.combining(character))
        variation = character in {"\ufe0e", "\ufe0f"}
        if not cluster:
            cluster, start = character, index
        elif combining or variation or join_next or character == "\u200d":
            cluster += character
        else:
            yield cluster, start
            cluster, start = character, index
        join_next = character == "\u200d"
    if cluster:
        yield cluster, start


def cluster_width(cluster: str, *, code: bool = False) -> float:
    if cluster == "\t":
        return 4.0 if code else 2.0
    if cluster.isspace():
        return 0.55
    base = cluster[0]
    if code:
        return 1.0
    width = unicodedata.east_asian_width(base)
    if width in {"W", "F"}:
        return 1.0
    if unicodedata.category(base) == "So":
        return 1.0
    return 0.55


class TextMeasure:
    """Conservative CJK-aware estimator with no file, font-search, or PPTX I/O."""

    def __init__(self, *, line_spacing: float = 1.2, paragraph_spacing_points: float = 2.0) -> None:
        self.line_spacing = line_spacing
        self.paragraph_spacing_points = paragraph_spacing_points

    def measure(
        self,
        text: str,
        *,
        width_emu: int,
        font_size: float,
        font_size_min: float,
        font_size_max: float,
        kind: str = "paragraph",
        margin_left_points: float = 0.0,
        margin_right_points: float = 0.0,
        margin_top_points: float = 0.0,
        margin_bottom_points: float = 0.0,
    ) -> TextMeasurement:
        encoded_size = len(text.encode("utf-8"))
        if encoded_size > MAX_TEXT_BYTES or text.count("\n") + 1 > MAX_LOGICAL_LINES:
            raise ValueError("text exceeds bounded measurement input")
        selected_size = clamp_font_size(font_size, font_size_min, font_size_max)
        width_points = width_emu / EMU_PER_POINT - margin_left_points - margin_right_points
        if width_points <= 0 or selected_size <= 0:
            raise ValueError("measurement width and font size must be positive")
        capacity = max(1.0, width_points / selected_size)
        display_lines = 0
        opportunities: list[int] = []
        offset = 0
        code = kind == "code"

        hard_lines = text.split("\n")
        for hard_line_index, hard_line in enumerate(hard_lines):
            units = 0.0
            line_count = 1
            clusters = list(grapheme_clusters(hard_line))
            for cluster_index, (cluster, local_index) in enumerate(clusters):
                unit = cluster_width(cluster, code=code)
                if units and units + unit > capacity:
                    line_count += 1
                    units = 0.0
                units += unit
                following = clusters[cluster_index + 1][0] if cluster_index + 1 < len(clusters) else ""
                base = cluster[-1]
                if (
                    cluster.isspace()
                    or base in "，。！？；：、,.!?;:"
                    or (not code and unicodedata.east_asian_width(cluster[0]) in {"W", "F"})
                ) and base not in NO_LINE_END and (not following or following[0] not in NO_LINE_START):
                    opportunities.append(offset + local_index + len(cluster))
            display_lines += line_count
            offset += len(hard_line)
            if hard_line_index < len(hard_lines) - 1:
                opportunities.append(offset)
                offset += 1

        extra_spacing = max(0, len(hard_lines) - 1) * self.paragraph_spacing_points
        if kind == "list":
            extra_spacing += display_lines * 0.5
        height = (
            display_lines * selected_size * self.line_spacing
            + extra_spacing
            + margin_top_points
            + margin_bottom_points
        )
        return TextMeasurement(
            display_lines=display_lines,
            height_points=round(height, 3),
            break_opportunities=tuple(opportunities),
            font_size=selected_size,
            fallback_used=True,
        )


def _slot(layout: dict[str, Any], slot_id: str) -> dict[str, Any]:
    return next(slot for slot in layout.get("slots", ()) if slot.get("id") == slot_id)


def _budget_capacity(slot: dict[str, Any], *, role: str | None = None) -> tuple[int, float, float, float]:
    target = slot
    if role:
        target = slot.get("subregions", {}).get(role, slot)
    budget = target.get("text_budget", slot.get("text_budget", {}))
    height = target.get("geometry", slot["geometry"])["height"] / EMU_PER_POINT
    return (
        int(budget.get("max_lines", 1)),
        float(height),
        float(budget.get("font_size_min", 12)),
        float(budget.get("font_size_max", 18)),
    )


def split_semantic_text(text: str, max_clusters: int) -> tuple[str, ...]:
    """Split at sentence, weak punctuation, then grapheme boundaries."""
    if max_clusters < 1:
        raise ValueError("max_clusters must be positive")
    clusters = [cluster for cluster, _ in grapheme_clusters(text)]
    if len(clusters) <= max_clusters:
        return (text,)
    result: list[str] = []
    start = 0
    while start < len(clusters):
        limit = min(len(clusters), start + max_clusters)
        if limit == len(clusters):
            end = limit
        else:
            strong = [i + 1 for i in range(start, limit) if clusters[i][-1] in STRONG_BREAK]
            weak = [i + 1 for i in range(start, limit) if clusters[i][-1] in WEAK_BREAK]
            end = (strong or weak or [limit])[-1]
            while end < len(clusters) and clusters[end][0] in TRAILING_CLOSERS:
                end += 1
        result.append("".join(clusters[start:end]))
        start = end
    return tuple(result)


def _fragment_height(fragment: BlockFragment, measure: TextMeasure, slot: dict[str, Any]) -> float:
    budget = slot["text_budget"]
    width = slot["geometry"]["width"]
    font = float(budget["font_size_min"])
    if fragment.kind == "list":
        text = "\n".join(fragment.items)
        kind = "list"
    else:
        text = fragment.text or ""
        kind = "code" if fragment.kind == "code" else "paragraph"
    return measure.measure(
        text,
        width_emu=width,
        font_size=font,
        font_size_min=font,
        font_size_max=float(budget["font_size_max"]),
        kind=kind,
    ).height_points


def _text_fragments(
    block: dict[str, Any], logical_index: int, block_index: int, slot: dict[str, Any], measure: TextMeasure
) -> tuple[BlockFragment, ...]:
    kind = block["kind"]
    heading = block.get("heading")
    budget = slot["text_budget"]
    max_lines = max(1, int(budget["max_lines"]))
    max_chars = max(1, int(budget["max_chars"]))
    # Character cap is only a deterministic splitter bound; height is the final fit oracle.
    cluster_cap = max(1, max_chars // max(1, max_lines) * max_lines)
    base = dict(
        logical_index=logical_index,
        block_index=block_index,
        source_line=int(block.get("source_line", 1)),
        heading=heading,
    )
    if kind == "paragraph":
        parts = split_semantic_text(str(block.get("text", "")), cluster_cap)
        return tuple(BlockFragment(kind=kind, fragment_index=i, text=part, **base) for i, part in enumerate(parts))
    if kind == "list":
        groups: list[tuple[str, ...]] = []
        current: list[str] = []
        used = 0
        for item in block.get("items", ()):
            item_clusters = len(list(grapheme_clusters(item)))
            if item_clusters > cluster_cap:
                if current:
                    groups.append(tuple(current)); current, used = [], 0
                groups.extend((part,) for part in split_semantic_text(item, cluster_cap))
            elif current and used + item_clusters > cluster_cap:
                groups.append(tuple(current)); current, used = [item], item_clusters
            else:
                current.append(item); used += item_clusters
        if current or not groups:
            groups.append(tuple(current))
        return tuple(
            BlockFragment(
                kind=kind,
                fragment_index=i,
                items=items,
                metadata=(("bullet_continuation", "true" if i and len(items) == 1 else "false"),),
                **base,
            )
            for i, items in enumerate(groups)
        )
    raise ValueError(f"unsupported text block: {kind}")


def _code_fragments(
    block: dict[str, Any], logical_index: int, block_index: int, slot: dict[str, Any], measure: TextMeasure
) -> tuple[tuple[BlockFragment, ...], tuple[RenderDiagnostic, ...]]:
    budget = slot["text_budget"]
    minimum = float(budget["font_size_min"])
    maximum = float(budget["font_size_max"])
    max_display = max(1, int(budget["max_lines"]))
    lines = str(block.get("text", "")).split("\n")
    groups: list[list[str]] = []
    current: list[str] = []
    used = 0
    diagnostics: list[RenderDiagnostic] = []
    for offset, line in enumerate(lines):
        display = measure.measure(
            line, width_emu=slot["geometry"]["width"], font_size=minimum,
            font_size_min=minimum, font_size_max=maximum, kind="code"
        ).display_lines
        if display > max_display:
            diagnostics.append(RenderDiagnostic(
                code="CODE_LINE_OVERFLOW", message="code source line exceeds one physical page", severity="error",
                source_line=int(block.get("source_line", 1)) + offset, logical_indices=(logical_index,),
                fix="shorten the source line without changing paginator wrapping",
            ))
        if current and used + display > max_display:
            groups.append(current); current, used = [], 0
        current.append(line); used += display
    if current:
        groups.append(current)
    fragments = tuple(BlockFragment(
        kind="code", logical_index=logical_index, block_index=block_index, fragment_index=i,
        source_line=int(block.get("source_line", 1)), heading=block.get("heading"), text="\n".join(group),
        metadata=(("display_lines", str(sum(measure.measure(
            line, width_emu=slot["geometry"]["width"], font_size=minimum,
            font_size_min=minimum, font_size_max=maximum, kind="code"
        ).display_lines for line in group))), ("language", str(block.get("language", "")))),
    ) for i, group in enumerate(groups))
    return fragments, tuple(diagnostics)


def _simple_slide_fragments(
    slide: dict[str, Any], logical_index: int, layout_manifest: dict[str, Any], measure: TextMeasure
) -> tuple[list[tuple[BlockFragment, ...]], list[RenderDiagnostic]]:
    layout = slide["layout"]
    blocks = slide.get("blocks", ())
    diagnostics: list[RenderDiagnostic] = []
    if not blocks:
        return [tuple()], diagnostics
    slot_id = "code" if layout == "code" else "body"
    if layout == "two-column":
        slot_id = "left_body"
    slot = _slot(layout_manifest, slot_id)
    capacity = slot["geometry"]["height"] / EMU_PER_POINT
    pages: list[list[BlockFragment]] = [[]]
    used = 0.0
    for block_index, block in enumerate(blocks):
        if block["kind"] == "image":
            fragment = BlockFragment(
                kind="image", logical_index=logical_index, block_index=block_index, fragment_index=0,
                source_line=int(block.get("source_line", 1)), heading=block.get("heading"),
                metadata=(("authored_path", str(block.get("authored_path", ""))),
                          ("caption", str(block.get("caption", ""))),
                          ("caption_placeholder", "true")),
            )
            height = 0.0
            fragments = (fragment,)
        elif block["kind"] == "code":
            fragments, found = _code_fragments(block, logical_index, block_index, slot, measure)
            diagnostics.extend(found)
            height = capacity + 1 if len(fragments) > 1 else _fragment_height(fragments[0], measure, slot)
        else:
            fragments = _text_fragments(block, logical_index, block_index, slot, measure)
            unsplit = fragments[0]
            unsplit_height = _fragment_height(unsplit, measure, slot)
            # A complete block that fits an empty page is never split.
            if len(fragments) > 1 and unsplit_height <= capacity:
                fragments = (replace(unsplit, text=block.get("text"), items=tuple(block.get("items", ()))),)
            height = unsplit_height
        for fragment in fragments:
            fragment_height = min(capacity, _fragment_height(fragment, measure, slot)) if fragment.kind != "image" else height
            if pages[-1] and used + fragment_height > capacity:
                pages.append([]); used = 0.0
            pages[-1].append(fragment); used += fragment_height
            if fragment_height >= capacity and fragment is not fragments[-1]:
                pages.append([]); used = 0.0
    return [tuple(page) for page in pages if page or not pages[0]], diagnostics


def _image_text_fragments(
    slide: dict[str, Any], logical_index: int, layout_manifest: dict[str, Any], measure: TextMeasure
) -> tuple[list[tuple[BlockFragment, ...]], list[RenderDiagnostic]]:
    body_blocks = [block for block in slide.get("blocks", ()) if block.get("kind") != "image"]
    images = [block for block in slide.get("blocks", ()) if block.get("kind") == "image"]
    body_slide = {**slide, "blocks": body_blocks, "layout": "image-text"}
    body_pages, diagnostics = _simple_slide_fragments(body_slide, logical_index, layout_manifest, measure)
    result: list[tuple[BlockFragment, ...]] = []
    for body_page in body_pages:
        for image_index, image in enumerate(images):
            image_fragment = BlockFragment(
                kind="image", logical_index=logical_index, block_index=len(body_blocks) + image_index,
                fragment_index=image_index, source_line=int(image.get("source_line", 1)),
                heading=image.get("heading"), metadata=(
                    ("authored_path", str(image.get("authored_path", ""))),
                    ("caption", str(image.get("caption", ""))),
                    ("caption_placeholder", "true"),
                    ("cartesian_image_index", str(image_index)),
                ),
            )
            result.append((*body_page, image_fragment))
    return result or body_pages, diagnostics


def ordered_contiguous_partition(
    weights: Sequence[float], capacity: float, *, minimum_items: int = 1, count_first: bool = False
) -> tuple[tuple[int, int], ...]:
    """Return a deterministic globally-balanced contiguous partition."""
    count = len(weights)
    if count == 0:
        return ()
    if count > 256 or count * count * max(1, count // max(1, minimum_items)) > MAX_PARTITION_STATES:
        raise ValueError("partition state budget exceeded")
    prefix = [0.0]
    for weight in weights:
        prefix.append(prefix[-1] + weight)
    best: tuple[tuple[float, ...], tuple[tuple[int, int], ...]] | None = None
    minimum_pages = max(1, math.ceil(prefix[-1] / capacity))
    for pages in range(minimum_pages, count + 1):
        if minimum_items > 1 and count < pages * minimum_items:
            continue
        states: dict[tuple[int, int], tuple[tuple[float, ...], tuple[int, ...], tuple[float, ...]]] = {
            (0, 0): ((0.0,), (), ())
        }
        for page in range(pages):
            for (used_pages, start), (_, splits, loads) in list(states.items()):
                if used_pages != page:
                    continue
                remaining_pages = pages - page - 1
                lower = start + minimum_items
                upper = count - remaining_pages * minimum_items
                for end in range(lower, upper + 1):
                    load = prefix[end] - prefix[start]
                    candidate_loads = (*loads, load)
                    counts = tuple(b - a for a, b in zip((0, *splits), (*splits, end)))
                    violations = sum(value > capacity for value in candidate_loads)
                    imbalance = max(counts) - min(counts)
                    mean = sum(candidate_loads) / len(candidate_loads)
                    variance = sum((value - mean) ** 2 for value in candidate_loads)
                    unused = sum(max(0.0, capacity - value) for value in candidate_loads)
                    objective = (
                        float(violations),
                        float(imbalance if count_first else 0),
                        variance,
                        unused,
                        *map(float, (*splits, end)),
                    )
                    key = (page + 1, end)
                    current = states.get(key)
                    if current is None or objective < current[0]:
                        states[key] = (objective, (*splits, end), candidate_loads)
        final = states.get((pages, count))
        if final is None:
            continue
        objective, splits, loads = final
        counts = tuple(b - a for a, b in zip((0, *splits[:-1]), splits))
        violations = sum(value > capacity for value in loads)
        orphans = sum(value < minimum_items for value in counts)
        imbalance = max(counts) - min(counts)
        mean = sum(loads) / len(loads)
        variance = sum((value - mean) ** 2 for value in loads)
        cost = (float(violations), float(orphans), float(imbalance), variance, float(pages), *map(float, splits))
        ranges = tuple(zip((0, *splits[:-1]), splits))
        if best is None or cost < best[0]:
            best = cost, ranges
        if violations == 0 and orphans == 0:
            break
    if best is None:
        return ((0, count),)
    return best[1]


def _wrapped_cell(
    value: str, width: int, font: float, measure: TextMeasure
) -> tuple[float, bool]:
    result = measure.measure(
        value, width_emu=width, font_size=font, font_size_min=font, font_size_max=font,
        kind="cell", margin_left_points=4, margin_right_points=4, margin_top_points=2, margin_bottom_points=2,
    )
    clusters = len(list(grapheme_clusters(value)))
    approximate_capacity = max(1, int(width / EMU_PER_POINT / font / 0.7))
    visual_orphan = result.display_lines > 1 and clusters % approximate_capacity in {1, 2}
    return result.height_points, visual_orphan


def _table_fragments(
    slide: dict[str, Any], logical_index: int, layout_manifest: dict[str, Any], measure: TextMeasure
) -> tuple[list[tuple[BlockFragment, ...]], list[RenderDiagnostic], float]:
    block = slide["blocks"][0]
    table_slot = _slot(layout_manifest, "table")
    geometry = table_slot["geometry"]
    budget = table_slot["text_budget"]
    columns = max(1, len(block.get("headers", ())))
    cell_width = int(geometry["width"] / columns)
    table_name_height = table_slot["subregions"]["table_name"]["geometry"]["height"] / EMU_PER_POINT
    capacity = geometry["height"] / EMU_PER_POINT - table_name_height
    preferred = float(budget["font_size_max"])
    candidates: list[tuple[tuple[float, ...], float, list[float], tuple[tuple[int, int], ...]]] = []
    all_rows = [tuple(map(str, block.get("headers", ()))), *[tuple(map(str, row)) for row in block.get("rows", ())]]
    for font in range(int(budget["font_size_min"]), int(budget["font_size_max"]) + 1):
        heights: list[float] = []
        orphan_count = 0
        for row in all_rows:
            measured = [_wrapped_cell(cell, cell_width, float(font), measure) for cell in row]
            heights.append(max((item[0] for item in measured), default=font * 1.2))
            orphan_count += sum(item[1] for item in measured)
        header_height, data_heights = heights[0], heights[1:]
        data_capacity = max(1.0, capacity - header_height)
        ranges = ordered_contiguous_partition(data_heights, data_capacity)
        loads = [header_height + sum(data_heights[start:end]) for start, end in ranges]
        overflow = sum(load > capacity for load in loads)
        mean = sum(loads) / len(loads)
        variance = sum((load - mean) ** 2 for load in loads)
        cost = (float(overflow), float(orphan_count), float(len(ranges)), abs(font - preferred), variance, -float(font))
        candidates.append((cost, float(font), data_heights, ranges))
    cost, selected_font, _, ranges = min(candidates, key=lambda item: item[0])
    diagnostics: list[RenderDiagnostic] = []
    if cost[0]:
        diagnostics.append(RenderDiagnostic(
            code="TABLE_ROW_OVERFLOW", message="one or more complete table rows exceed page capacity",
            severity="error", source_line=int(block.get("source_line", 1)), logical_indices=(logical_index,),
            fix="shorten the affected table cells",
        ))
    table_name = str(block.get("table_title") or "")
    pages: list[tuple[BlockFragment, ...]] = []
    rows = [tuple(map(str, row)) for row in block.get("rows", ())]
    headers = tuple(map(str, block.get("headers", ())))
    for page_index, (start, end) in enumerate(ranges):
        name = f"{table_name}（续）" if table_name and page_index else table_name
        fragment = BlockFragment(
            kind="table", logical_index=logical_index, block_index=0, fragment_index=page_index,
            source_line=int(block.get("source_line", 1)), heading=block.get("heading"), rows=(headers, *rows[start:end]),
            metadata=(("table_name", name), ("table_name_placeholder", "true"), ("repeat_header", "true")),
        )
        pages.append((fragment,))
    return pages or [tuple()], diagnostics, selected_font


def _timeline_fragments(
    slide: dict[str, Any], logical_index: int, layout_manifest: dict[str, Any], measure: TextMeasure
) -> tuple[list[tuple[BlockFragment, ...]], list[RenderDiagnostic]]:
    block = slide["blocks"][0]
    slot = _slot(layout_manifest, "timeline_items")
    budget = slot["text_budget"]
    rows = [tuple(map(str, row)) for row in block.get("rows", ())]
    width = max(1, int(slot["subregions"]["node_band"]["geometry"]["width"] / 3))
    font = float(budget["font_size_min"])
    weights = [max(_wrapped_cell(cell, width, font, measure)[0] for cell in row) for row in rows]
    capacity = slot["geometry"]["height"] / EMU_PER_POINT
    diagnostics: list[RenderDiagnostic] = []
    try:
        ranges = ordered_contiguous_partition(weights, capacity, minimum_items=3 if len(rows) >= 3 else 1)
    except ValueError:
        ranges = ((0, len(rows)),)
        diagnostics.append(RenderDiagnostic(
            code="PAGINATION_RESOURCE_LIMIT", message="timeline partition exceeded bounded state budget",
            severity="error", source_line=int(block.get("source_line", 1)), logical_indices=(logical_index,),
            fix="split the timeline",
        ))
    if any(sum(weights[start:end]) > capacity or (len(rows) >= 3 and end - start < 3) for start, end in ranges):
        ranges = ordered_contiguous_partition(weights, capacity, minimum_items=1)
        diagnostics.append(RenderDiagnostic(
            code="TIMELINE_BALANCE_INFEASIBLE", message="timeline capacity cannot preserve three nodes per page",
            severity="error", source_line=int(block.get("source_line", 1)), logical_indices=(logical_index,),
            fix="shorten timeline descriptions or split the logical timeline",
        ))
    pages = [(
        BlockFragment(
            kind="timeline", logical_index=logical_index, block_index=0, fragment_index=page_index,
            source_line=int(block.get("source_line", 1)), heading=block.get("heading"), rows=tuple(rows[start:end]),
            metadata=(("start_item", str(start)), ("end_item", str(end))),
        ),
    ) for page_index, (start, end) in enumerate(ranges)]
    return pages or [tuple()], diagnostics


def _contents_fragments(
    entries: Sequence[str], logical_index: int, layout_manifest: dict[str, Any], measure: TextMeasure, source_line: int
) -> tuple[list[tuple[BlockFragment, ...]], list[RenderDiagnostic]]:
    slot = _slot(layout_manifest, "body")
    budget = slot["text_budget"]
    font = float(budget["font_size_min"])
    weights = [measure.measure(
        f"{index}. {entry}", width_emu=slot["geometry"]["width"], font_size=font,
        font_size_min=font, font_size_max=font,
    ).height_points for index, entry in enumerate(entries, 1)]
    capacity = slot["geometry"]["height"] / EMU_PER_POINT
    diagnostics: list[RenderDiagnostic] = []
    try:
        ranges = ordered_contiguous_partition(weights, capacity, count_first=True)
    except ValueError:
        ranges = ((0, len(entries)),)
        diagnostics.append(RenderDiagnostic(
            code="PAGINATION_RESOURCE_LIMIT", message="contents partition exceeded bounded state budget",
            severity="error", source_line=source_line, logical_indices=(logical_index,), fix="reduce contents entries",
        ))
    pages = [(
        BlockFragment(
            kind="contents", logical_index=logical_index, block_index=0, fragment_index=page_index,
            source_line=source_line, items=tuple(entries[start:end]),
            metadata=(("number_start", str(start + 1)), ("number_end", str(end))),
        ),
    ) for page_index, (start, end) in enumerate(ranges)]
    return pages or [tuple()], diagnostics


def build_deck_plan(document: dict[str, Any], manifest: dict[str, Any]) -> PhysicalDeckPlan:
    """Convert a canonical Phase 42 document into an immutable physical plan."""
    logical_slides = document.get("logical_slides", ())
    if sum(len(slide.get("blocks", ())) for slide in logical_slides) > MAX_BLOCKS:
        diagnostic = RenderDiagnostic(
            code="PAGINATION_RESOURCE_LIMIT", message="logical block count exceeds bounded pagination input",
            severity="error", source_line=1, fix="split the Markdown document",
        )
        return PhysicalDeckPlan((), (diagnostic,), ())
    measure = TextMeasure()
    slides: list[PhysicalSlide] = []
    diagnostics: list[RenderDiagnostic] = []
    mapping: list[tuple[int, tuple[int, ...]]] = []
    for logical_index, logical in enumerate(logical_slides):
        layout = str(logical.get("layout", "title-content"))
        layout_manifest = manifest["layouts"][layout]
        selected_font_sizes: tuple[tuple[str, float], ...] = ()
        if layout == "image-text":
            page_fragments, found = _image_text_fragments(logical, logical_index, layout_manifest, measure)
        elif layout == "table":
            page_fragments, found, selected_font = _table_fragments(logical, logical_index, layout_manifest, measure)
            selected_font_sizes = (("table", selected_font),)
        elif layout == "timeline":
            page_fragments, found = _timeline_fragments(logical, logical_index, layout_manifest, measure)
        elif layout == "contents":
            page_fragments, found = _contents_fragments(
                tuple(map(str, document.get("contents_entries", ()))), logical_index, layout_manifest, measure,
                int(logical.get("source_line", 1)),
            )
        elif layout == "gallery":
            page_fragments, found = [tuple()], []
        else:
            page_fragments, found = _simple_slide_fragments(logical, logical_index, layout_manifest, measure)
        diagnostics.extend(found)
        physical_indices: list[int] = []
        notes = logical.get("notes")
        notes_intent = notes.get("markdown") if isinstance(notes, dict) else None
        for fragment_index, fragments in enumerate(page_fragments):
            physical_index = len(slides)
            physical_indices.append(physical_index)
            slides.append(PhysicalSlide(
                logical_index=logical_index,
                physical_index=physical_index,
                layout=layout,
                title="目录" if layout == "contents" else str(logical.get("title") or document.get("document_title") or ""),
                fragment_index=fragment_index,
                source_line=int(logical.get("source_line", 1)),
                fragments=fragments,
                notes_intent=notes_intent,
                selected_font_sizes=selected_font_sizes,
                affected_pages=(physical_index,),
            ))
        mapping.append((logical_index, tuple(physical_indices)))
    return PhysicalDeckPlan(tuple(slides), tuple(diagnostics), tuple(mapping))


def run_contract_model_self_check() -> dict[str, object]:
    fragment = BlockFragment(
        kind="paragraph",
        logical_index=1,
        block_index=0,
        fragment_index=0,
        source_line=12,
        heading="目标",
        text="中文段落",
        metadata=(("role", "body"),),
    )
    slide = PhysicalSlide(
        logical_index=1,
        physical_index=2,
        layout="title-content",
        title="建设目标",
        fragment_index=0,
        source_line=10,
        fragments=(fragment,),
        notes_intent="先说明目标。",
        selected_font_sizes=(("body", 18.0),),
        affected_pages=(2,),
    )
    diagnostic = RenderDiagnostic(
        code="SELF_CHECK",
        message="deterministic",
        severity="info",
        source_line=10,
        logical_indices=(1,),
        physical_indices=(2,),
    )
    first = PhysicalDeckPlan((slide,), (diagnostic,), ((1, (2,)),))
    second = PhysicalDeckPlan((slide,), (diagnostic,), ((1, (2,)),))
    immutable = False
    try:
        fragment.text = "mutated"  # type: ignore[misc]
    except FrozenInstanceError:
        immutable = True
    assert first == second and immutable
    projection = first.to_projection()
    assert json.dumps(projection, ensure_ascii=False, sort_keys=True) == json.dumps(
        second.to_projection(), ensure_ascii=False, sort_keys=True
    )

    measure = TextMeasure()
    vectors = {
        "cjk_no_spaces": measure.measure(
            "职业院校智能制造课程建设需要稳定分页。" * 3,
            width_emu=2_540_000,
            font_size=18,
            font_size_min=14,
            font_size_max=22,
        ).to_projection(),
        "explicit_newline": measure.measure(
            "第一行\n第二行\n第三行",
            width_emu=5_080_000,
            font_size=18,
            font_size_min=14,
            font_size_max=22,
        ).to_projection(),
        "emoji_combining": measure.measure(
            "A\u0301 与 👩\u200d🏭 协同",
            width_emu=2_540_000,
            font_size=18,
            font_size_min=14,
            font_size_max=22,
        ).to_projection(),
        "code_indent": measure.measure(
            "def run():\n\treturn '完成'",
            width_emu=2_540_000,
            font_size=12,
            font_size_min=10,
            font_size_max=14,
            kind="code",
        ).to_projection(),
        "cell_margin": measure.measure(
            "设备状态与维护记录",
            width_emu=1_270_000,
            font_size=16,
            font_size_min=12,
            font_size_max=18,
            kind="cell",
            margin_left_points=8,
            margin_right_points=8,
            margin_top_points=4,
            margin_bottom_points=4,
        ).to_projection(),
        "font_clamp": measure.measure(
            "字号边界",
            width_emu=2_540_000,
            font_size=99,
            font_size_min=12,
            font_size_max=18,
        ).to_projection(),
    }
    assert vectors["explicit_newline"]["display_lines"] == 3
    assert vectors["font_clamp"]["font_size"] == 18.0
    return {
        "model_equal": first == second,
        "model_immutable": immutable,
        "projection": projection,
        "vectors": vectors,
    }


if __name__ == "__main__":
    print(json.dumps(run_contract_model_self_check(), ensure_ascii=False, indent=2, sort_keys=True))
