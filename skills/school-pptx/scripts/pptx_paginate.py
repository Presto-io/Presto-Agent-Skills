#!/usr/bin/env python3
"""Pure, deterministic pagination measurement primitives for school-pptx."""

from __future__ import annotations

import json
import hashlib
import io
import math
import os
import re
import stat
import unicodedata
import warnings
from dataclasses import FrozenInstanceError, dataclass, replace
from pathlib import Path
from typing import Any, Iterator, Sequence

from markdown_contract import visual_semantics
from pptx_model import (
    BlockFragment, MediaBinding, PhysicalDeckPlan, PhysicalSlide, RenderDiagnostic, VisualPlan, VisualSlide,
    bind_physical_plan_integrity,
    canonical_json, fragment_paragraph_sequence,
)


MAX_TEXT_BYTES = 2 * 1024 * 1024
MAX_LOGICAL_LINES = 2048
MAX_BLOCKS = 2048
MAX_PARTITION_STATES = 200_000
MAX_MEDIA_BYTES = 16 * 1024 * 1024
MAX_MEDIA_PIXELS = 40_000_000
EMU_PER_POINT = 12700
NO_LINE_START = frozenset("，。！？；：、）》】」』〉…,.!?;:%)]}")
NO_LINE_END = frozenset("《（【「『〈([{“‘")
STRONG_BREAK = frozenset("。！？!?；;")
WEAK_BREAK = frozenset("，、：:,")
TRAILING_CLOSERS = frozenset('"\'”’）》】」』〉)]}')


def _stable_capacity(value: object) -> tuple[tuple[str, tuple[int, ...]], ...]:
    if not isinstance(value, dict):
        return ()
    result: list[tuple[str, tuple[int, ...]]] = []
    for name in sorted(value):
        raw = value[name]
        values = raw if isinstance(raw, (list, tuple)) else (raw,)
        try:
            result.append((str(name), tuple(int(item) for item in values)))
        except (TypeError, ValueError):
            result.append((str(name), ()))
    return tuple(result)


def _read_media_binding(reference: dict[str, Any]) -> MediaBinding:
    """Read an authored media file once through a no-follow descriptor."""
    logical_reference = str(reference.get("logical_reference", ""))
    caption = str(reference.get("caption", "")).strip()
    source_line = int(reference.get("source_line", 1))
    placement = str(reference.get("placement", "contain"))
    path = str(reference.get("resolved_path", ""))
    if not logical_reference or not path or not bool(reference.get("exists", False)):
        return MediaBinding(logical_reference, source_line, None, 0, None, placement, False, "MEDIA_MISSING")
    descriptor = -1
    descriptors: list[int] = []
    try:
        candidate = Path(path)
        if not candidate.is_absolute():
            return MediaBinding(logical_reference, source_line, None, 0, None, placement, False, "MEDIA_UNREADABLE")
        parts = tuple(part for part in candidate.parts if part != candidate.anchor)
        if not parts or any(part in {"", ".", ".."} for part in parts):
            return MediaBinding(logical_reference, source_line, None, 0, None, placement, False, "MEDIA_UNREADABLE")
        descriptors.append(os.open(candidate.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW))
        for component in parts[:-1]:
            descriptors.append(os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptors[-1],
            ))
        descriptor = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=descriptors[-1])
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size <= 0 or metadata.st_size > MAX_MEDIA_BYTES:
            return MediaBinding(logical_reference, source_line, None, 0, None, placement, False, "MEDIA_SIZE_INVALID")
        chunks: list[bytes] = []
        remaining = MAX_MEDIA_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) != metadata.st_size or len(payload) > MAX_MEDIA_BYTES:
            return MediaBinding(logical_reference, source_line, None, 0, None, placement, False, "MEDIA_READ_INVALID")
        media_format = "png" if payload.startswith(b"\x89PNG\r\n\x1a\n") else "jpeg" if payload.startswith(b"\xff\xd8\xff") else None
        if media_format is None:
            return MediaBinding(logical_reference, source_line, None, len(payload), None, placement, False, "MEDIA_FORMAT_INVALID")
        # The bound payload replaces the legacy emitter's path-based image
        # loader, so validate it to the same boundary before freezing it.
        try:
            from PIL import Image, UnidentifiedImageError
        except (ImportError, ModuleNotFoundError):
            return MediaBinding(
                logical_reference, source_line, None, len(payload), None, placement, False,
                "PPTX_DEPENDENCY_MISSING",
            )

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(payload)) as image:
                    expected_format = "PNG" if media_format == "png" else "JPEG"
                    if image.format != expected_format:
                        return MediaBinding(
                            logical_reference, source_line, None, len(payload), None, placement, False,
                            "MEDIA_FORMAT_INVALID",
                        )
                    width, height = image.size
                    if width <= 0 or height <= 0 or width * height > MAX_MEDIA_PIXELS:
                        return MediaBinding(
                            logical_reference, source_line, None, len(payload), None, placement, False,
                            "PPTX_MEDIA_PIXEL_LIMIT",
                        )
                    image.verify()
        except (Image.DecompressionBombError, Image.DecompressionBombWarning):
            return MediaBinding(
                logical_reference, source_line, None, len(payload), None, placement, False,
                "PPTX_MEDIA_PIXEL_LIMIT",
            )
        except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
            return MediaBinding(
                logical_reference, source_line, None, len(payload), None, placement, False,
                "MEDIA_FORMAT_INVALID",
            )
        return MediaBinding(
            logical_reference, source_line, hashlib.sha256(payload).hexdigest(), len(payload), media_format,
            placement, True, payload=payload, caption=caption,
        )
    except OSError:
        return MediaBinding(logical_reference, source_line, None, 0, None, placement, False, "MEDIA_UNREADABLE")
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        for open_descriptor in reversed(descriptors):
            os.close(open_descriptor)


def build_visual_plan(
    document: dict[str, Any], manifest: dict[str, Any], *, template_path: str | os.PathLike[str] | None = None,
    manifest_bytes: bytes | None = None,
) -> VisualPlan:
    """Freeze reviewed input identity and author-order visual semantics before pagination."""
    markdown_sha256 = document.get("markdown_sha256")
    if not isinstance(markdown_sha256, str) or len(markdown_sha256) != 64:
        raise ValueError("visual planning requires parse_document markdown_sha256")
    manifest_sha256 = hashlib.sha256(manifest_bytes if manifest_bytes is not None else canonical_json(manifest)).hexdigest()
    if template_path is None:
        raise ValueError("visual planning requires the controlled template path")
    descriptor = -1
    try:
        descriptor = os.open(template_path, os.O_RDONLY | os.O_NOFOLLOW)
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise OSError("template is not a regular file")
        digest = hashlib.sha256()
        while chunk := os.read(descriptor, 1024 * 1024):
            digest.update(chunk)
        template_sha256 = digest.hexdigest()
    except OSError as exc:
        raise ValueError("visual planning requires a readable controlled template") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    slides: list[VisualSlide] = []
    diagnostics: list[RenderDiagnostic] = []
    for semantic in visual_semantics(document):
        layout = semantic["layout"]
        layout_manifest = manifest.get("layouts", {}).get(layout, {})
        bindings = tuple(_read_media_binding(reference) for reference in semantic["media"])
        for binding in bindings:
            if not binding.confirmed:
                diagnostics.append(RenderDiagnostic(
                    code=binding.diagnostic_code or "MEDIA_INVALID", message="媒体未通过冻结计划安全校验。",
                    severity="error", source_line=binding.source_line,
                    logical_indices=(int(semantic["logical_index"]),),
                    fix="恢复受支持的本地 PNG 或 JPEG 媒体后重新规划。",
                ))
        semantics = (
            ("block_kinds", ",".join(semantic["block_kinds"])),
            ("media_count", str(len(bindings))),
        )
        slides.append(VisualSlide(
            logical_index=int(semantic["logical_index"]), source_line=int(semantic["source_line"]),
            layout=layout, title=semantic["title"], visual_semantics=semantics,
            candidate_capacity=_stable_capacity(layout_manifest.get("visual_capacity")),
            object_roles=tuple(str(role) for role in layout_manifest.get("object_roles", ())),
            media_bindings=bindings,
        ))
    return VisualPlan(markdown_sha256, manifest_sha256, template_sha256, tuple(slides), tuple(diagnostics))


_PRESET_LAYOUTS = frozenset({"hero-evidence", "annotated-image", "process-overlay", "kpi-evidence", "gallery", "image-text"})


def _visual_diagnostic(
    code: str, layout: str, logical_index: int, source_line: int, group_index: int, fix: str,
) -> RenderDiagnostic:
    """Create a stable, directly actionable visual-planning failure."""
    return RenderDiagnostic(
        code=code,
        message=(f"布局 {layout} 的原子组 {group_index} 无法映射到受控 manifest 预设。"),
        severity="error",
        source_line=source_line,
        logical_indices=(logical_index,),
        fix=fix,
    )


def _slot_by_id(layout_manifest: dict[str, Any], slot_id: str) -> dict[str, Any]:
    return next(
        (slot for slot in layout_manifest.get("slots", ()) if isinstance(slot, dict) and slot.get("id") == slot_id),
        {},
    )


def _freeze_emitter_font_sizes(layout_manifest: dict[str, Any]) -> tuple[tuple[str, float], ...]:
    """Freeze every manifest text budget consumed by the native emitter.

    The emitter may use manifest geometry and object presets, but its font choices
    are part of the reviewed physical projection.  Keep the key path literal so a
    later emitter call cannot silently introduce an unfrozen fallback.
    """
    fonts: list[tuple[str, float]] = []

    def visit(value: object, path: tuple[str, ...]) -> None:
        if not isinstance(value, dict):
            return
        budget = value.get("text_budget")
        if isinstance(budget, dict):
            for bound in ("min", "max"):
                raw = budget.get(f"font_size_{bound}")
                if isinstance(raw, (int, float)):
                    fonts.append((f"font.{'.'.join(path)}.{bound}", float(raw)))
        nested = value.get("subregions")
        if isinstance(nested, dict):
            for key, child in nested.items():
                visit(child, (*path, "subregions", str(key)))
        node_template = value.get("node_template")
        if isinstance(node_template, dict):
            visit(node_template, (*path, "node_template"))

    for slot in layout_manifest.get("slots", ()):
        if isinstance(slot, dict) and isinstance(slot.get("id"), str):
            visit(slot, (str(slot["id"]),))
    return tuple(fonts)


def _variant_counts(layout: str, layout_manifest: dict[str, Any]) -> tuple[int, ...]:
    """Return the manifest-owned item counts in canonical numeric order."""
    if layout == "hero-evidence":
        values = _slot_by_id(layout_manifest, "kpi_cards").get("item_presets", {})
    elif layout == "kpi-evidence":
        values = _slot_by_id(layout_manifest, "kpi_cards").get("item_presets", {})
    elif layout == "annotated-image":
        values = _slot_by_id(layout_manifest, "annotations").get("fixed_anchors", {})
    elif layout == "process-overlay":
        values = _slot_by_id(layout_manifest, "process_nodes").get("node_counts", ())
    elif layout == "gallery":
        values = _slot_by_id(layout_manifest, "gallery_items").get("item_presets", {})
    elif layout == "image-text":
        values = _slot_by_id(layout_manifest, "media").get("item_presets", {})
    else:
        return ()
    if isinstance(values, dict):
        values = values.keys()
    try:
        return tuple(sorted({int(value) for value in values if int(value) > 0}))
    except (TypeError, ValueError):
        return ()


def _atomic_group(
    kind: str, group_index: int, source_line: int, *values: str,
) -> tuple[str, ...]:
    """A compact immutable group identity; all payload remains in its frozen fragment."""
    return (f"id={group_index}", f"kind={kind}", f"source_line={source_line}", *values)


def _visual_atomic_groups(
    logical: dict[str, Any], visual_slide: VisualSlide,
) -> tuple[tuple[tuple[str, ...], ...], tuple[BlockFragment, ...]]:
    """Build indivisible source-order units for the controlled visual layouts."""
    layout = visual_slide.layout
    blocks = tuple(logical.get("blocks", ()))
    groups: list[tuple[str, ...]] = []
    fragments: list[BlockFragment] = []

    def add(kind: str, source_line: int, metadata: tuple[tuple[str, str], ...], *identity: str) -> None:
        group_index = len(groups)
        groups.append(_atomic_group(kind, group_index, source_line, *identity))
        fragments.append(BlockFragment(
            kind="visual-group", logical_index=visual_slide.logical_index, block_index=group_index,
            fragment_index=0, source_line=source_line, metadata=metadata,
        ))

    if layout in {"gallery", "image-text"}:
        for media_index, binding in enumerate(visual_slide.media_bindings):
            block = next((item for item in blocks if int(item.get("source_line", -1)) == binding.source_line and item.get("kind") == "image"), {})
            caption = str(block.get("caption", "")).strip()
            add(
                "media-caption", binding.source_line,
                (("media_index", str(media_index)), ("caption", caption), ("media_sha256", binding.sha256 or "")),
                f"media={media_index}", f"caption={caption}", f"sha256={binding.sha256 or ''}",
            )
    elif layout in {"hero-evidence", "kpi-evidence"}:
        table = next((item for item in blocks if item.get("kind") == "table"), {})
        for row_index, row in enumerate(table.get("rows", ())):
            values = tuple(str(value) for value in row)
            add("kpi-card", int(table.get("source_line", visual_slide.source_line)) + row_index + 2,
                (("row", "|".join(values)),), f"row={row_index}", f"value={'|'.join(values)}")
    elif layout == "annotated-image":
        labels = next((item for item in blocks if item.get("kind") == "list"), {})
        for label_index, label in enumerate(labels.get("items", ())):
            source_line = int(labels.get("source_line", visual_slide.source_line)) + label_index
            add("annotation", source_line, (("label", str(label)),),
                f"number={label_index + 1}", f"label={str(label)}", f"anchor={label_index + 1}", f"leader={label_index + 1}")
    elif layout == "process-overlay":
        table = next((item for item in blocks if item.get("kind") == "table"), {})
        for step_index, row in enumerate(table.get("rows", ())):
            values = tuple(str(value) for value in row)
            source_line = int(table.get("source_line", visual_slide.source_line)) + step_index + 2
            connector = "none" if step_index == 0 else f"{step_index - 1}->{step_index}"
            add("process-node", source_line, (("row", "|".join(values)), ("connector", connector)),
                f"step={step_index}", f"value={'|'.join(values)}", f"connector={connector}")
    return tuple(groups), tuple(fragments)


def _page_ranges(group_count: int, capacities: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    """Minimize pages, then greedily take the longest earliest prefix on every page."""
    if group_count <= 0 or not capacities:
        return ()
    maximum = max(capacities)
    result: list[tuple[int, int]] = []
    start = 0
    while start < group_count:
        end = min(group_count, start + maximum)
        remaining = group_count - end
        # A non-final page must leave an expressible non-empty remainder.
        if remaining and remaining < min(capacities):
            end -= min(capacities) - remaining
        if end <= start or end - start not in capacities:
            # All controlled manifests currently accept every count from 1 to max for media,
            # or only a single already-validated page for the other layouts.
            candidates = [count for count in capacities if count <= group_count - start]
            if not candidates:
                return ()
            end = start + max(candidates)
        result.append((start, end))
        start = end
    return tuple(result)


def build_physical_deck_plan(
    document: dict[str, Any], manifest: dict[str, Any], visual_plan: VisualPlan, *, include_implicit: bool = False,
) -> PhysicalDeckPlan:
    """Freeze manifest variants, atomic groups and physical mapping before any emission.

    This planner deliberately consumes parser output only.  It never measures text, searches
    for media again, or selects geometry outside the checked manifest preset set.
    """
    diagnostics: list[RenderDiagnostic] = list(visual_plan.diagnostics)
    slides: list[PhysicalSlide] = []
    mapping: list[tuple[int, tuple[int, ...]]] = []
    logical_slides = tuple(document.get("logical_slides", ()))
    if len(logical_slides) != len(visual_plan.slides):
        diagnostic = RenderDiagnostic("VISUAL_PLAN_MISMATCH", "VisualPlan 与已审阅逻辑页数量不一致。", "error", 1,
                                      fix="使用同一份已审阅 Markdown 重新构建 VisualPlan。")
        return bind_physical_plan_integrity(PhysicalDeckPlan(
            (), (*diagnostics, diagnostic), (), visual_plan.sha256,
            visual_plan.markdown_sha256, visual_plan.manifest_sha256, visual_plan.template_sha256,
        ))
    for logical, visual_slide in zip(logical_slides, visual_plan.slides):
        layout = visual_slide.layout
        logical_index = visual_slide.logical_index
        source_line = visual_slide.source_line
        if str(logical.get("layout", "")) != layout or int(logical.get("source_line", 1)) != source_line:
            diagnostics.append(RenderDiagnostic("VISUAL_PLAN_MISMATCH", "VisualPlan 与逻辑页来源不一致。", "error", source_line,
                                                (logical_index,), fix="使用同一份已审阅 Markdown 重新构建 VisualPlan。"))
            continue
        if any(not binding.confirmed for binding in visual_slide.media_bindings):
            diagnostics.append(_visual_diagnostic(
                "VISUAL_MEDIA_BINDING_INVALID", layout, logical_index, source_line, 0,
                "恢复通过安全校验的本地 PNG 或 JPEG 媒体后重新规划。",
            ))
            continue
        layout_manifest = manifest.get("layouts", {}).get(layout)
        if not isinstance(layout_manifest, dict):
            diagnostics.append(_visual_diagnostic("VISUAL_LAYOUT_UNKNOWN", layout, logical_index, source_line, 0,
                                                  "恢复 manifest 中受支持的布局后重新规划。"))
            continue
        if layout not in _PRESET_LAYOUTS:
            # Existing layouts retain their prior pagination contract; bind the resulting pages
            # to this VisualPlan without inventing a visual preset.
            legacy = build_deck_plan({**document, "logical_slides": (logical,), "implicit_slides": ()}, manifest)
            indices: list[int] = []
            for continuation, legacy_slide in enumerate(legacy.slides):
                physical_index = len(slides)
                indices.append(physical_index)
                rebound_fragments = tuple(replace(fragment, logical_index=logical_index) for fragment in legacy_slide.fragments)
                frozen_fonts = _freeze_emitter_font_sizes(layout_manifest)
                slides.append(replace(legacy_slide, logical_index=logical_index, physical_index=physical_index,
                                      fragments=rebound_fragments,
                                      continuation=continuation, affected_pages=(physical_index,),
                                      selected_font_sizes=(*legacy_slide.selected_font_sizes, *frozen_fonts),
                                      candidate_capacity=visual_slide.candidate_capacity,
                                      object_roles=visual_slide.object_roles,
                                      media_bindings=visual_slide.media_bindings))
            diagnostics.extend(legacy.diagnostics)
            mapping.append((logical_index, tuple(indices)))
            continue
        groups, fragments = _visual_atomic_groups(logical, visual_slide)
        capacities = _variant_counts(layout, layout_manifest)
        ranges = _page_ranges(len(groups), capacities)
        if not ranges:
            diagnostics.append(_visual_diagnostic("VISUAL_VARIANT_UNAVAILABLE", layout, logical_index, source_line, 0,
                                                  "将原子内容数量调整为 manifest 支持的固定预设容量。"))
            continue
        indices: list[int] = []
        for continuation, (start, end) in enumerate(ranges):
            count = end - start
            if count not in capacities:
                group_source_line = int(groups[start][2].split("=", 1)[1])
                diagnostics.append(_visual_diagnostic("VISUAL_VARIANT_UNAVAILABLE", layout, logical_index,
                                                      group_source_line, start,
                                                      "将原子内容数量调整为 manifest 支持的固定预设容量。"))
                continue
            physical_index = len(slides)
            indices.append(physical_index)
            preset_id = f"{layout}:{count}"
            slots = (("variant_count", str(count)), ("preset_id", preset_id))
            frozen_fonts = _freeze_emitter_font_sizes(layout_manifest)
            # image-text is a fixed media-preset layout, but its editable text
            # frame still consumes the legacy body typography path at emission.
            if layout == "image-text":
                body_typography = _selected_body_typography(_slot(layout_manifest, "body"))
                frozen_fonts = (("body", body_typography["font_size"]), *frozen_fonts)
                slots = (*slots, *_typography_slot_values("body", body_typography))
            slides.append(PhysicalSlide(
                logical_index=logical_index, physical_index=physical_index, layout=layout, title=visual_slide.title,
                fragment_index=continuation, source_line=source_line, fragments=fragments[start:end],
                continuation=continuation, variant=preset_id, preset_id=preset_id,
                candidate_capacity=visual_slide.candidate_capacity, object_roles=visual_slide.object_roles,
                atomic_groups=groups[start:end], media_bindings=visual_slide.media_bindings,
                affected_pages=(physical_index,), slot_values=slots,
                selected_font_sizes=frozen_fonts,
            ))
        if indices:
            mapping.append((logical_index, tuple(indices)))
    # The template-owned closing page is still part of the frozen physical deck.  It
    # has no authored visual choice, but must not be appended by the emitter.
    closing_specs = ([item for item in document.get("implicit_slides", ()) if item.get("layout") == "closing"]
                     if include_implicit else [])
    if closing_specs:
        physical_index = len(slides)
        closing_manifest = manifest.get("layouts", {}).get("closing", {})
        closing_fragment = BlockFragment(
            kind="closing", logical_index=len(logical_slides), block_index=0, fragment_index=0,
            source_line=1, metadata=(("pptx_layout", str(closing_manifest.get("pptx_layout", ""))),),
        )
        slides.append(PhysicalSlide(
            logical_index=len(logical_slides), physical_index=physical_index, layout="closing", title="",
            fragment_index=0, source_line=1, fragments=(closing_fragment,),
            notes_intent="总结本次汇报的核心内容，邀请听众提问并进入交流答疑。",
            affected_pages=(physical_index,),
        ))
    return bind_physical_plan_integrity(PhysicalDeckPlan(
        tuple(slides), tuple(diagnostics), tuple(mapping), visual_plan.sha256,
        visual_plan.markdown_sha256, visual_plan.manifest_sha256, visual_plan.template_sha256,
    ))


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


def _selected_body_typography(slot: dict[str, Any]) -> dict[str, float]:
    budget = slot["text_budget"]
    if budget.get("overflow") != "paginate":
        raise ValueError("body typography requires a paginate slot")
    return {
        "font_size": float(budget["font_size_max"]),
        "margin_left_points": 0.0,
        "margin_right_points": 0.0,
        "margin_top_points": 0.0,
        "margin_bottom_points": 0.0,
        "line_spacing": 1.2,
        "paragraph_spacing_points": 2.0,
    }


def _selected_code_typography(slot: dict[str, Any]) -> dict[str, float]:
    budget = slot["text_budget"]
    if budget.get("overflow") != "paginate":
        raise ValueError("code typography requires a paginate slot")
    return {
        "font_size": float(budget["font_size_max"]),
        "margin_left_points": 0.0,
        "margin_right_points": 0.0,
        "margin_top_points": 0.0,
        "margin_bottom_points": 0.0,
        "line_spacing": 1.2,
        "paragraph_spacing_points": 2.0,
    }


def _effective_geometry(slot: dict[str, Any], typography: dict[str, float]) -> tuple[int, float]:
    width_points = slot["geometry"]["width"] / EMU_PER_POINT
    width_points -= typography["margin_left_points"] + typography["margin_right_points"]
    height_points = slot["geometry"]["height"] / EMU_PER_POINT
    height_points -= typography["margin_top_points"] + typography["margin_bottom_points"]
    if width_points <= 0 or height_points <= 0:
        raise ValueError("effective body geometry must be positive")
    return max(1, int(round(width_points * EMU_PER_POINT))), height_points


def _typography_slot_values(slot_id: str, typography: dict[str, float]) -> tuple[tuple[str, str], ...]:
    return tuple(
        (f"typography.{slot_id}.{key}", str(value))
        for key, value in typography.items()
        if key != "font_size"
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


def _fragment_height(
    fragment: BlockFragment,
    measure: TextMeasure,
    slot: dict[str, Any],
    typography: dict[str, float],
) -> float:
    width, _ = _effective_geometry(slot, typography)
    return _measure_paragraph_sequence(fragment, width, typography)


def _measure_paragraph_sequence(
    fragment: BlockFragment, width: int, typography: dict[str, float]
) -> float:
    target_measure = TextMeasure(
        line_spacing=typography["line_spacing"],
        paragraph_spacing_points=typography["paragraph_spacing_points"],
    )
    total = 0.0
    for projection in fragment_paragraph_sequence(fragment):
        measurement = target_measure.measure(
            projection.visible_text,
            width_emu=width,
            font_size=typography["font_size"],
            font_size_min=typography["font_size"],
            font_size_max=typography["font_size"],
            kind="code" if projection.role == "code" else "paragraph",
        )
        total += measurement.display_lines * typography["font_size"] * typography["line_spacing"]
        total += typography["paragraph_spacing_points"]
    return round(total, 3)


def _code_heading_height_emu(
    fragments: Sequence[BlockFragment], slot: dict[str, Any], typography: dict[str, float]
) -> int:
    heading = next((fragment.heading for fragment in fragments if fragment.heading), None)
    if not heading:
        return 0
    heading_fragment = BlockFragment(
        kind="paragraph", logical_index=0, block_index=0, fragment_index=0,
        source_line=1, heading=heading,
    )
    width, _ = _effective_geometry(slot, typography)
    height_points = _measure_paragraph_sequence(heading_fragment, width, typography)
    measured_height = max(1, math.ceil(height_points * EMU_PER_POINT))
    minimum_code_height = max(1, math.ceil(
        (typography["font_size"] * typography["line_spacing"]
         + typography["paragraph_spacing_points"]) * EMU_PER_POINT
    ))
    safe_heading_height = max(1, int(slot["geometry"]["height"]) - minimum_code_height)
    return min(measured_height, safe_heading_height)


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
    block: dict[str, Any], logical_index: int, block_index: int, slot: dict[str, Any], measure: TextMeasure,
    typography: dict[str, float],
) -> tuple[tuple[BlockFragment, ...], tuple[RenderDiagnostic, ...]]:
    width, capacity = _effective_geometry(slot, typography)
    font = typography["font_size"]
    target_measure = TextMeasure(
        line_spacing=typography["line_spacing"],
        paragraph_spacing_points=typography["paragraph_spacing_points"],
    )
    lines = str(block.get("text", "")).split("\n")
    diagnostics: list[RenderDiagnostic] = []
    line_weights: list[float] = []
    for offset, line in enumerate(lines):
        line_measurement = target_measure.measure(
            line, width_emu=width, font_size=font,
            font_size_min=font, font_size_max=font, kind="code"
        )
        line_height = line_measurement.height_points
        line_weights.append(line_measurement.display_lines * font * typography["line_spacing"])
        if line_height > capacity:
            diagnostics.append(RenderDiagnostic(
                code="CODE_LINE_OVERFLOW", message="code source line exceeds one physical page", severity="error",
                source_line=int(block.get("source_line", 1)) + offset, logical_indices=(logical_index,),
                fix="shorten the source line without changing paginator wrapping",
            ))
    max_lines = max(1, int(slot["text_budget"]["max_lines"]))
    bounded_capacity = min(
        capacity,
        max_lines * font * typography["line_spacing"] + typography["paragraph_spacing_points"],
    )
    ranges = ordered_contiguous_partition(line_weights, bounded_capacity)
    groups = [lines[start:end] for start, end in ranges]
    fragments = tuple(BlockFragment(
        kind="code", logical_index=logical_index, block_index=block_index, fragment_index=i,
        source_line=int(block.get("source_line", 1)), heading=block.get("heading"), text="\n".join(group),
        metadata=(("display_lines", str(sum(target_measure.measure(
            line, width_emu=width, font_size=font,
            font_size_min=font, font_size_max=font, kind="code"
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
    typography = _selected_code_typography(slot) if layout == "code" else _selected_body_typography(slot)
    _, capacity = _effective_geometry(slot, typography)
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
            # A generic title-content image owns a continuation page. Counting
            # it as zero height places it over the preceding body text.
            height = capacity
            fragments = (fragment,)
        elif block["kind"] == "code":
            fragments, found = _code_fragments(block, logical_index, block_index, slot, measure, typography)
            diagnostics.extend(found)
            height = capacity + 1 if len(fragments) > 1 else _fragment_height(fragments[0], measure, slot, typography)
        else:
            fragments = _text_fragments(block, logical_index, block_index, slot, measure)
            unsplit = fragments[0]
            unsplit_height = _fragment_height(unsplit, measure, slot, typography)
            # A complete block that fits an empty page is never split.
            if len(fragments) > 1 and unsplit_height <= capacity:
                fragments = (replace(unsplit, text=block.get("text"), items=tuple(block.get("items", ()))),)
            if block["kind"] == "paragraph":
                fitted: list[BlockFragment] = []
                pending = [fragment.text or "" for fragment in fragments]
                while pending:
                    text = pending.pop(0)
                    candidate = replace(unsplit, text=text, items=(), fragment_index=len(fitted))
                    if _fragment_height(candidate, measure, slot, typography) <= capacity:
                        fitted.append(candidate)
                        continue
                    clusters = len(list(grapheme_clusters(text)))
                    if clusters <= 1:
                        fitted.append(candidate)
                        continue
                    parts = split_semantic_text(text, max(1, clusters // 2))
                    pending = [*parts, *pending]
                fragments = tuple(fitted)
            elif block["kind"] == "list":
                fitted_lists: list[BlockFragment] = []
                current_items: list[str] = []
                for item in block.get("items", ()):
                    candidate_items = (*current_items, str(item))
                    candidate = replace(unsplit, items=candidate_items, text=None,
                                        fragment_index=len(fitted_lists))
                    if current_items and _fragment_height(candidate, measure, slot, typography) > capacity:
                        fitted_lists.append(replace(unsplit, items=tuple(current_items), text=None,
                                                    fragment_index=len(fitted_lists)))
                        current_items = [str(item)]
                    else:
                        current_items.append(str(item))
                if current_items:
                    fitted_lists.append(replace(unsplit, items=tuple(current_items), text=None,
                                                fragment_index=len(fitted_lists)))
                fragments = tuple(fitted_lists)
            height = unsplit_height
        for fragment in fragments:
            fragment_height = _fragment_height(fragment, measure, slot, typography) if fragment.kind != "image" else height
            if fragment_height > capacity:
                diagnostics.append(RenderDiagnostic(
                    code="TEXT_BLOCK_OVERFLOW",
                    message="complete paragraph sequence exceeds one physical page",
                    severity="error",
                    source_line=fragment.source_line,
                    logical_indices=(logical_index,),
                    fix="shorten the semantic unit without changing source order",
                ))
            if pages[-1] and used + fragment_height > capacity:
                pages.append([]); used = 0.0
            pages[-1].append(fragment); used += fragment_height
            if fragment_height >= capacity and fragment is not fragments[-1]:
                pages.append([]); used = 0.0
    return [tuple(page) for page in pages if page or not pages[0]], diagnostics


def _two_column_fragments(
    slide: dict[str, Any], logical_index: int, layout_manifest: dict[str, Any], measure: TextMeasure
) -> tuple[list[tuple[BlockFragment, ...]], list[RenderDiagnostic]]:
    blocks = list(slide.get("blocks", ()))
    pages: list[tuple[BlockFragment, ...]] = []
    diagnostics: list[RenderDiagnostic] = []
    for pair_start in range(0, len(blocks), 2):
        side_pages: list[list[tuple[BlockFragment, ...]]] = []
        for offset, slot_id in enumerate(("left_body", "right_body")):
            if pair_start + offset >= len(blocks):
                side_pages.append([])
                continue
            slot = _slot(layout_manifest, slot_id)
            synthetic = {"slots": [{**slot, "id": "body"}]}
            found_pages, found = _simple_slide_fragments(
                {**slide, "layout": "title-content", "blocks": [blocks[pair_start + offset]]},
                logical_index,
                synthetic,
                measure,
            )
            diagnostics.extend(found)
            side_pages.append([
                tuple(replace(fragment, block_index=pair_start + offset, target_slot=slot_id) for fragment in page)
                for page in found_pages
            ])
        for page_index in range(max(1, *(len(side) for side in side_pages))):
            pages.append(tuple(
                fragment
                for side in side_pages
                for fragment in (side[page_index] if page_index < len(side) else ())
            ))
    return pages or [tuple()], diagnostics


def _cover_slot_values(document: dict[str, Any]) -> tuple[tuple[tuple[str, str], ...], RenderDiagnostic | None]:
    metadata = document.get("metadata", {})
    subtitle = str(metadata.get("subtitle") or "")
    institution = " · ".join(
        str(metadata.get(key)) for key in ("school", "department") if metadata.get(key)
    )
    delivery = " · ".join(
        str(metadata.get(key)) for key in ("course", "author", "date") if metadata.get(key)
    )
    complete = "\n".join(value for value in (subtitle, institution, delivery) if value)
    diagnostic = None
    if len(complete) > 96 or complete.count("\n") + 1 > 3:
        diagnostic = RenderDiagnostic(
            code="COVER_METADATA_OVERFLOW",
            message="complete cover subtitle descriptor exceeds the controlled 96-character/3-line budget",
            severity="error",
            source_line=1,
            fix="shorten subtitle or cover metadata without dropping descriptor fields",
        )
    return (("title", str(document.get("document_title") or "")), ("subtitle", complete)), diagnostic


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
    table_name_geometry = table_slot["subregions"]["table_name"]["geometry"]
    if any(table_name_geometry[key] != geometry[key] for key in ("x", "y", "width")):
        raise ValueError("table_name geometry must share table x/y/width")
    table_body_geometry = table_slot.get("subregions", {}).get("table_body", {}).get("geometry")
    content_budget_emu = int(
        table_body_geometry["height"] if table_body_geometry is not None
        else geometry["height"] - table_name_geometry["height"]
    )
    if content_budget_emu <= 0:
        raise ValueError("derived table content budget must be positive")
    preferred = float(budget["font_size_max"])
    candidates: list[tuple[tuple[float, ...], float, list[int], tuple[tuple[int, int], ...]]] = []
    all_rows = [tuple(map(str, block.get("headers", ()))), *[tuple(map(str, row)) for row in block.get("rows", ())]]
    for font in range(int(budget["font_size_min"]), int(budget["font_size_max"]) + 1):
        heights: list[int] = []
        orphan_count = 0
        for row in all_rows:
            measured = [_wrapped_cell(cell, cell_width, float(font), measure) for cell in row]
            measured_points = max((item[0] for item in measured), default=font * 1.2)
            heights.append(max(1, math.ceil(measured_points * EMU_PER_POINT)))
            orphan_count += sum(item[1] for item in measured)
        header_height, data_heights = heights[0], heights[1:]
        data_capacity = max(1, content_budget_emu - header_height)
        ranges = ((0, 0),) if not data_heights else ordered_contiguous_partition(data_heights, data_capacity)
        loads = [header_height + sum(data_heights[start:end]) for start, end in ranges]
        overflow = sum(load > content_budget_emu for load in loads)
        mean = sum(loads) / len(loads)
        variance = sum((load - mean) ** 2 for load in loads)
        cost = (float(overflow), float(orphan_count), float(len(ranges)), abs(font - preferred), variance, -float(font))
        candidates.append((cost, float(font), heights, ranges))
    cost, selected_font, measured_heights, ranges = min(candidates, key=lambda item: item[0])
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
        page_heights = _allocate_row_heights(
            (measured_heights[0], *measured_heights[start + 1:end + 1]), content_budget_emu,
            fixed_prefix=1,
        )
        fragment = BlockFragment(
            kind="table", logical_index=logical_index, block_index=0, fragment_index=page_index,
            source_line=int(block.get("source_line", 1)), heading=block.get("heading"), rows=(headers, *rows[start:end]),
            metadata=(("table_name", name), ("table_name_placeholder", "true"), ("repeat_header", "true")),
            row_heights_emu=page_heights,
        )
        pages.append((fragment,))
    return pages or [tuple()], diagnostics, selected_font


def _allocate_row_heights(
    measured: Sequence[int], content_budget_emu: int, *, fixed_prefix: int = 0
) -> tuple[int, ...]:
    heights = tuple(int(value) for value in measured)
    if not heights or any(value <= 0 for value in heights):
        raise ValueError("table row measurements must be positive integers")
    measured_total = sum(heights)
    if measured_total >= content_budget_emu:
        return heights
    adjustable = len(heights) - fixed_prefix
    if adjustable <= 0:
        return heights
    quotient, remainder = divmod(content_budget_emu - measured_total, adjustable)
    return tuple(
        value if index < fixed_prefix else value + quotient + (1 if index - fixed_prefix < remainder else 0)
        for index, value in enumerate(heights)
    )


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
    max_items = int(slot.get("max_items_per_page", 0))
    if max_items > 0:
        capped_ranges: list[tuple[int, int]] = []
        for start, end in ranges:
            count = end - start
            page_count = max(1, math.ceil(count / max_items))
            quotient, remainder = divmod(count, page_count)
            cursor = start
            for page_index in range(page_count):
                size = quotient + (1 if page_index < remainder else 0)
                capped_ranges.append((cursor, cursor + size))
                cursor += size
        ranges = tuple(capped_ranges)
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
    typography = _selected_body_typography(slot)
    width, capacity = _effective_geometry(slot, typography)
    weights = []
    for entry in entries:
        item = BlockFragment(kind="contents", logical_index=logical_index, block_index=0,
                             fragment_index=0, source_line=source_line,
                             items=(entry,))
        weights.append(_measure_paragraph_sequence(item, width, typography))
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
            source_line=source_line,
            items=tuple(entries[start:end]),
            metadata=(("entry_start", str(start)), ("entry_end", str(end))),
        ),
    ) for page_index, (start, end) in enumerate(ranges)]
    return pages or [tuple()], diagnostics


def _gallery_fragments(slide: dict[str, Any], logical_index: int) -> list[tuple[BlockFragment, ...]]:
    blocks = list(slide.get("blocks", ()))
    pages: list[tuple[BlockFragment, ...]] = []
    page_count = max(1, math.ceil(len(blocks) / 4))
    base_size, remainder = divmod(len(blocks), page_count)
    start = 0
    for page_index in range(page_count):
        chunk_size = base_size + (1 if page_index < remainder else 0)
        chunk = blocks[start:start + chunk_size]
        preset = len(chunk)
        fragments = tuple(BlockFragment(
            kind="image", logical_index=logical_index, block_index=start + item_index,
            fragment_index=item_index, source_line=int(block.get("source_line", 1)),
            heading=block.get("heading"), metadata=(
                ("authored_path", str(block.get("authored_path", ""))),
                ("caption", str(block.get("caption", ""))),
                ("caption_placeholder", "true"),
                ("gallery_preset", str(preset)),
                ("gallery_item_index", str(item_index)),
            ),
        ) for item_index, block in enumerate(chunk))
        pages.append(fragments)
        start += chunk_size
    return pages or [tuple()]


def _default_notes(
    logical: dict[str, Any], logical_index: int, logical_slides: Sequence[dict[str, Any]], document: dict[str, Any]
) -> str:
    layout = str(logical.get("layout", "title-content"))
    title = str(logical.get("title") or document.get("document_title") or "本页内容")
    if layout == "cover":
        return f"开场介绍《{title}》，说明汇报主题、适用专业和本次交流目标。"
    if layout == "contents":
        entries = "、".join(map(str, document.get("contents_entries", ())))
        return f"概览本次汇报结构：{entries}。说明各章节之间的逻辑关系。" if entries else "概览本次汇报结构和讲解顺序。"
    if layout == "section":
        following_titles: list[str] = []
        for following in logical_slides[logical_index + 1:]:
            if following.get("layout") == "section":
                break
            following_title = str(following.get("title") or "").strip()
            if following_title:
                following_titles.append(following_title)
        if following_titles:
            return f"本章内容概括：围绕“{title}”，依次介绍{'、'.join(following_titles)}。"
        return f"本章内容概括：说明“{title}”的核心目标、实施要点和预期成果。"
    layout_prompts = {
        "two-column": "对照左右两栏说明对应关系、差异和共同目标。",
        "image-text": "结合左侧说明与右侧图片，讲清场景、方法和实际作用。",
        "table": "按表头和关键行说明数据关系、验收标准和结论。",
        "timeline": "按时间顺序说明各阶段任务、衔接关系和阶段成果。",
        "gallery": "结合各图片说明资源用途、观察重点和证据价值。",
        "code": "说明结构化记录的字段、使用场景和审阅要求。",
    }
    prompt = layout_prompts.get(layout, "概括页面核心观点，并结合正文说明实施要求和预期成果。")
    return f"本页围绕“{title}”展开。{prompt}"


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
        frozen_typography: tuple[tuple[str, str], ...] = ()
        if layout == "cover":
            page_fragments, found = [tuple()], []
        elif layout == "two-column":
            page_fragments, found = _two_column_fragments(logical, logical_index, layout_manifest, measure)
            body_typographies = {
                slot_id: _selected_body_typography(_slot(layout_manifest, slot_id))
                for slot_id in ("left_body", "right_body")
            }
            selected_font_sizes = tuple(
                (slot_id, typography["font_size"]) for slot_id, typography in body_typographies.items()
            )
            frozen_typography = tuple(
                item
                for slot_id, typography in body_typographies.items()
                for item in _typography_slot_values(slot_id, typography)
            )
        elif layout == "image-text":
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
            page_fragments, found = _gallery_fragments(logical, logical_index), []
        else:
            page_fragments, found = _simple_slide_fragments(logical, logical_index, layout_manifest, measure)
        if layout == "code":
            code_typography = _selected_code_typography(_slot(layout_manifest, "code"))
            selected_font_sizes = (("code", code_typography["font_size"]),)
            frozen_typography = _typography_slot_values("code", code_typography)
        elif layout in {"contents", "title-content", "image-text"}:
            body_typography = _selected_body_typography(_slot(layout_manifest, "body"))
            selected_font_sizes = (("body", body_typography["font_size"]),)
            frozen_typography = _typography_slot_values("body", body_typography)
        diagnostics.extend(found)
        physical_indices: list[int] = []
        notes = logical.get("notes")
        notes_intent = (
            notes.get("markdown") if isinstance(notes, dict)
            else _default_notes(logical, logical_index, logical_slides, document)
        )
        slot_values: tuple[tuple[str, str], ...] = ()
        if layout == "cover":
            slot_values, cover_diagnostic = _cover_slot_values(document)
            if cover_diagnostic is not None:
                diagnostics.append(cover_diagnostic)
        for fragment_index, fragments in enumerate(page_fragments):
            physical_index = len(slides)
            physical_indices.append(physical_index)
            page_selected_font_sizes = selected_font_sizes
            page_frozen_typography = frozen_typography
            if layout == "title-content" and any(fragment.kind == "list" for fragment in fragments):
                dense_typography = {**body_typography, "font_size": 26.0}
                page_selected_font_sizes = (("body", dense_typography["font_size"]),)
                page_frozen_typography = _typography_slot_values("body", dense_typography)
            page_slot_values = (*slot_values, *page_frozen_typography)
            if layout == "code":
                heading_height = _code_heading_height_emu(
                    fragments, _slot(layout_manifest, "code"), code_typography
                )
                page_slot_values = (
                    *page_slot_values,
                    ("geometry.code.heading_height_emu", str(heading_height)),
                )
            slides.append(PhysicalSlide(
                logical_index=logical_index,
                physical_index=physical_index,
                layout=layout,
                title="目录" if layout == "contents" else str(logical.get("title") or document.get("document_title") or ""),
                fragment_index=fragment_index,
                source_line=int(logical.get("source_line", 1)),
                fragments=fragments,
                notes_intent=notes_intent,
                selected_font_sizes=page_selected_font_sizes,
                affected_pages=(physical_index,),
                slot_values=page_slot_values,
            ))
        mapping.append((logical_index, tuple(physical_indices)))
    closing_specs = [item for item in document.get("implicit_slides", ()) if item.get("layout") == "closing"]
    if closing_specs:
        physical_index = len(slides)
        closing_manifest = manifest["layouts"]["closing"]
        closing_fragment = BlockFragment(
            kind="closing", logical_index=len(logical_slides), block_index=0, fragment_index=0,
            source_line=1, metadata=(("pptx_layout", str(closing_manifest["pptx_layout"])),),
        )
        slides.append(PhysicalSlide(
            logical_index=len(logical_slides), physical_index=physical_index, layout="closing", title="",
            fragment_index=0, source_line=1, fragments=(closing_fragment,),
            notes_intent="总结本次汇报的核心内容，邀请听众提问并进入交流答疑。",
            affected_pages=(physical_index,),
        ))
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
