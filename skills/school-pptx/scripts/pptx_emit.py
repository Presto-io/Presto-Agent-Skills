#!/usr/bin/env python3
"""Mechanical emitter for immutable school-pptx physical deck plans."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any, Callable

from pptx_model import PhysicalDeckPlan
from pptx_ooxml import remove_seed_slides


class PptxEmitError(RuntimeError):
    """Bounded renderer-domain failure safe for CLI presentation."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def require_dependencies(importer: Callable[[str], Any] = import_module) -> dict[str, Any]:
    try:
        pptx = importer("pptx")
        pillow = importer("PIL")
    except (ImportError, ModuleNotFoundError) as exc:
        raise PptxEmitError("PPTX_DEPENDENCY_MISSING", "需要 python-pptx 1.0.2+ 与 Pillow。") from exc
    try:
        version = tuple(int(item) for item in str(pptx.__version__).split(".")[:2])
    except (AttributeError, ValueError) as exc:
        raise PptxEmitError("PPTX_DEPENDENCY_MISSING", "无法确认 python-pptx 版本。") from exc
    if version < (1, 0) or version >= (2, 0):
        raise PptxEmitError("PPTX_DEPENDENCY_MISSING", "python-pptx 版本必须为 >=1.0.2,<2。")
    patch = int(str(pptx.__version__).split(".")[2].split("+")[0])
    if version == (1, 0) and patch < 2:
        raise PptxEmitError("PPTX_DEPENDENCY_MISSING", "python-pptx 版本必须为 >=1.0.2,<2。")
    return {"pptx": pptx, "PIL": pillow}


def layout_part_map(presentation: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for layout in presentation.slide_layouts:
        part_path = str(layout.part.partname).lstrip("/")
        if part_path in result:
            raise PptxEmitError("PPTX_TEMPLATE_LAYOUT_INVALID", "模板包含重复 layout part path。")
        result[part_path] = layout
    return result


def resolve_layouts(presentation: Any, manifest: dict[str, Any]) -> dict[str, Any]:
    by_part = layout_part_map(presentation)
    resolved: dict[str, Any] = {}
    for layout_id, specification in manifest.get("layouts", {}).items():
        part_path = specification.get("pptx_layout")
        if not isinstance(part_path, str) or part_path not in by_part:
            raise PptxEmitError(
                "PPTX_TEMPLATE_LAYOUT_INVALID", f'布局 "{layout_id}" 的 PPTX part path 不存在。'
            )
        resolved[str(layout_id)] = by_part[part_path]
    return resolved


def bootstrap_template(template_path: Path, manifest: dict[str, Any]) -> tuple[Any, dict[str, Any], dict[str, int]]:
    dependencies = require_dependencies()
    try:
        presentation = dependencies["pptx"].Presentation(str(template_path))
    except (OSError, ValueError) as exc:
        raise PptxEmitError("PPTX_TEMPLATE_INVALID", "无法打开受控 PPTX 模板。") from exc
    layouts = resolve_layouts(presentation, manifest)
    seed_count = len(presentation.slides)
    removed, notes_relationships = remove_seed_slides(presentation)
    if seed_count != 5 or removed != 5 or notes_relationships != 2:
        raise PptxEmitError("PPTX_TEMPLATE_SEED_INVALID", "受控模板必须包含 5 张 seed 与 2 个 notes relationships。")
    return presentation, layouts, {
        "seed_slides": seed_count,
        "removed_seed_slides": removed,
        "removed_seed_notes_relationships": notes_relationships,
    }


def emit_deck(
    plan: PhysicalDeckPlan, manifest: dict[str, Any], template_path: Path, output_path: Path
) -> dict[str, Any]:
    """Emit only the frozen plan; pagination is intentionally absent from this module."""
    presentation, layouts, evidence = bootstrap_template(template_path, manifest)
    for physical in plan.slides:
        presentation.slides.add_slide(layouts[physical.layout])
    try:
        presentation.save(str(output_path))
    except OSError as exc:
        raise PptxEmitError("PPTX_PACKAGE_INVALID", "无法保存 staged PPTX。") from exc
    return {**evidence, "physical_slides": len(plan.slides), "output": str(output_path)}
