#!/usr/bin/env python3
"""Pure, deterministic pagination measurement primitives for school-pptx."""

from __future__ import annotations

import json
import unicodedata
from dataclasses import FrozenInstanceError, dataclass
from typing import Iterator

from pptx_model import BlockFragment, PhysicalDeckPlan, PhysicalSlide, RenderDiagnostic


MAX_TEXT_BYTES = 2 * 1024 * 1024
MAX_LOGICAL_LINES = 2048
EMU_PER_POINT = 12700
NO_LINE_START = frozenset("，。！？；：、）》】」』〉…,.!?;:%)]}")
NO_LINE_END = frozenset("《（【「『〈([{“‘")


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
