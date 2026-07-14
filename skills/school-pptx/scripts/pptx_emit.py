#!/usr/bin/env python3
"""Mechanical emitter for immutable school-pptx physical deck plans."""

from __future__ import annotations

from importlib import import_module
import os
import posixpath
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Callable
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

from pptx_model import PhysicalDeckPlan
from pptx_objects import (
    PptxObjectError,
    add_contain_picture,
    add_gallery_card,
    add_plain_lines,
    add_rich_text,
    add_table,
    add_timeline,
    set_notes,
)
from pptx_ooxml import remove_seed_slides


class PptxEmitError(RuntimeError):
    """Bounded renderer-domain failure safe for CLI presentation."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


MAX_PACKAGE_ENTRIES = 512
MAX_PACKAGE_ENTRY_BYTES = 16 * 1024 * 1024
MAX_PACKAGE_TOTAL_BYTES = 96 * 1024 * 1024
MAX_PACKAGE_RELATIONSHIPS = 4096
FORBIDDEN_XML_MARKERS = (b"<!DOCTYPE", b"<!ENTITY")
REL_NS = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
OBJECT_ERROR_MESSAGES = {
    "PPTX_MEDIA_SIZE_LIMIT": "媒体文件大小超过安全上限。",
    "PPTX_MEDIA_FORMAT_INVALID": "媒体格式不受支持，请使用 JPEG 或 PNG。",
    "PPTX_MEDIA_PIXEL_LIMIT": "媒体像素数量超过安全上限。",
}


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
    plan: PhysicalDeckPlan, manifest: dict[str, Any], template_path: Path, output: Path | BinaryIO,
    *, media_root: Path | None = None,
) -> dict[str, Any]:
    """Emit only the frozen plan; pagination is intentionally absent from this module."""
    presentation, layouts, evidence = bootstrap_template(template_path, manifest)
    highlight = manifest["inline_styles"]["highlight"]["scheme_color"]
    try:
        for physical in plan.slides:
            slide = presentation.slides.add_slide(layouts[physical.layout])
            layout_manifest = manifest["layouts"][physical.layout]
            slots = {slot["id"]: slot for slot in layout_manifest.get("slots", ())}
            if "title" in slots:
                title_budget = slots["title"]["text_budget"]
                add_rich_text(
                    slide, slots["title"]["geometry"], physical.title,
                    font_size=title_budget["font_size_max"], highlight_scheme=highlight,
                    name="school-pptx:slide-title",
                )
            if physical.layout == "closing":
                set_notes(slide, physical.notes_intent)
                continue
            if physical.layout == "table" and physical.fragments:
                fragment = physical.fragments[0]
                add_table(
                    slide, slots["table"], fragment,
                    font_size=dict(physical.selected_font_sizes).get("table", slots["table"]["text_budget"]["font_size_min"]),
                )
            elif physical.layout == "timeline" and physical.fragments:
                add_timeline(slide, slots["timeline_items"], physical.fragments[0].rows, highlight_scheme=highlight)
            elif physical.layout == "gallery":
                gallery_slot = slots["gallery_items"]
                count = len(physical.fragments)
                presets = gallery_slot["item_presets"][count]
                for index, (fragment, preset) in enumerate(zip(physical.fragments, presets)):
                    metadata = dict(fragment.metadata)
                    path = _media_path(metadata.get("authored_path", ""), media_root)
                    add_gallery_card(
                        slide, preset, path, metadata.get("caption", ""), index=index,
                        highlight_scheme=highlight, font_size=slots["caption"]["text_budget"]["font_size_min"],
                    )
            else:
                body_slot_id = "code" if physical.layout == "code" else "body"
                if physical.layout == "two-column":
                    body_slot_id = "left_body"
                body_slot = slots.get(body_slot_id)
                text_fragments = [fragment for fragment in physical.fragments if fragment.kind != "image"]
                if body_slot is not None:
                    lines: list[str] = []
                    for fragment in text_fragments:
                        if fragment.heading:
                            lines.append(fragment.heading)
                        if fragment.text is not None:
                            lines.append(fragment.text)
                        lines.extend(fragment.items)
                    budget = body_slot["text_budget"]
                    add_plain_lines(
                        slide, body_slot["geometry"], lines,
                        font_size=budget["font_size_min"] if physical.layout == "code" else budget["font_size_max"],
                        highlight_scheme=highlight, name=f"school-pptx:{body_slot_id}",
                        monospace=physical.layout == "code",
                    )
                image_fragment = next((fragment for fragment in physical.fragments if fragment.kind == "image"), None)
                if image_fragment is not None and ("media" in slots or body_slot is not None):
                    metadata = dict(image_fragment.metadata)
                    media_geometry = slots["media"]["geometry"] if "media" in slots else body_slot["geometry"]
                    add_contain_picture(
                        slide, _media_path(metadata.get("authored_path", ""), media_root), media_geometry,
                        name="school-pptx:image-text-picture",
                    )
            set_notes(slide, physical.notes_intent)
    except PptxObjectError as exc:
        code = str(exc) if str(exc) in OBJECT_ERROR_MESSAGES else "PPTX_OBJECT_INVALID"
        message = OBJECT_ERROR_MESSAGES.get(code, "PPTX 对象内容无效。")
        raise PptxEmitError(code, message) from None
    try:
        if hasattr(output, "write"):
            output.seek(0)
            output.truncate(0)
            presentation.save(output)
            output.flush()
            os.fsync(output.fileno())
            output.seek(0)
        else:
            presentation.save(str(output))
    except (OSError, ValueError) as exc:
        raise PptxEmitError("PPTX_PACKAGE_INVALID", "无法保存 staged PPTX。") from exc
    package = validate_staged_package(output, expected_slides=len(plan.slides))
    return {
        **evidence,
        "physical_slides": len(plan.slides),
        "output": str(output) if isinstance(output, Path) else "<staged-stream>",
        "transition_mode": "none",
        "package": package,
    }


def _media_path(authored: str, media_root: Path | None) -> Path | None:
    if not authored:
        return None
    path = Path(authored)
    if path.is_absolute():
        return path
    if media_root is None:
        return None
    return (media_root / path).resolve(strict=False)


def _relationship_source(name: str) -> str:
    pure = PurePosixPath(name)
    if pure.name == ".rels":
        return ""
    source_name = pure.name.removesuffix(".rels")
    parent = pure.parent.parent
    return str(parent / source_name)


def _reader(source: Path | BinaryIO) -> tuple[BinaryIO | Path, Callable[[], None]]:
    if not hasattr(source, "read"):
        return source, lambda: None
    source.flush()
    duplicate = os.fdopen(os.dup(source.fileno()), "rb")
    duplicate.seek(0)
    return duplicate, duplicate.close


def validate_staged_package(source: Path | BinaryIO, *, expected_slides: int | None = None) -> dict[str, int]:
    """Apply bounded ZIP/XML/relationship checks before a staged file may be published."""
    dependencies = require_dependencies()
    try:
        zip_source, close_zip_source = _reader(source)
        with ZipFile(zip_source) as package:
            infos = package.infolist()
            if len(infos) > MAX_PACKAGE_ENTRIES:
                raise PptxEmitError("PPTX_PACKAGE_INVALID", "PPTX ZIP entry 数量超限。")
            names = {info.filename for info in infos}
            if len(names) != len(infos):
                raise PptxEmitError("PPTX_PACKAGE_INVALID", "PPTX ZIP 包含重复 entry。")
            required = {"[Content_Types].xml", "ppt/presentation.xml", "ppt/_rels/presentation.xml.rels"}
            if not required <= names:
                raise PptxEmitError("PPTX_PACKAGE_INVALID", "PPTX 缺少核心 content type 或 presentation part。")
            total = 0
            relationship_count = 0
            slide_count = sum(
                name.startswith("ppt/slides/slide") and name.endswith(".xml") and "/_rels/" not in name
                for name in names
            )
            for info in infos:
                pure = PurePosixPath(info.filename)
                if pure.is_absolute() or ".." in pure.parts or info.file_size > MAX_PACKAGE_ENTRY_BYTES:
                    raise PptxEmitError("PPTX_PACKAGE_INVALID", "PPTX ZIP 路径或 entry 大小无效。")
                total += info.file_size
                if total > MAX_PACKAGE_TOTAL_BYTES:
                    raise PptxEmitError("PPTX_PACKAGE_INVALID", "PPTX 解压总大小超限。")
                if not (info.filename.endswith(".xml") or info.filename.endswith(".rels")):
                    continue
                payload = package.read(info)
                upper = payload.upper()
                if any(marker in upper for marker in FORBIDDEN_XML_MARKERS):
                    raise PptxEmitError("PPTX_PACKAGE_INVALID", "PPTX XML 包含外部实体声明。")
                try:
                    root = ET.fromstring(payload)
                except ET.ParseError as exc:
                    raise PptxEmitError("PPTX_PACKAGE_INVALID", "PPTX XML 无法安全解析。") from exc
                if info.filename.endswith(".rels"):
                    relationships = root.findall("r:Relationship", REL_NS)
                    relationship_count += len(relationships)
                    if relationship_count > MAX_PACKAGE_RELATIONSHIPS:
                        raise PptxEmitError("PPTX_PACKAGE_INVALID", "PPTX relationship 数量超限。")
                    relationship_source = _relationship_source(info.filename)
                    source_dir = posixpath.dirname(relationship_source)
                    for relationship in relationships:
                        if relationship.get("TargetMode") == "External":
                            raise PptxEmitError("PPTX_PACKAGE_INVALID", "PPTX 禁止 external relationship。")
                        target = relationship.get("Target", "")
                        if not target or target.startswith("/"):
                            raise PptxEmitError("PPTX_PACKAGE_INVALID", "PPTX relationship target 无效。")
                        resolved = posixpath.normpath(posixpath.join(source_dir, target))
                        if resolved == ".." or resolved.startswith("../") or resolved not in names:
                            raise PptxEmitError("PPTX_PACKAGE_INVALID", "PPTX relationship target 越界或缺失。")
            if expected_slides is not None and slide_count != expected_slides:
                raise PptxEmitError("PPTX_PACKAGE_INVALID", "PPTX slide count 与冻结计划不一致。")
    except (BadZipFile, OSError) as exc:
        raise PptxEmitError("PPTX_PACKAGE_INVALID", "PPTX ZIP 无法读取。") from exc
    finally:
        if "close_zip_source" in locals():
            close_zip_source()
    try:
        reopen_source, close_reopen_source = _reader(source)
        reopened = dependencies["pptx"].Presentation(reopen_source)
    except (OSError, ValueError, KeyError) as exc:
        raise PptxEmitError("PPTX_PACKAGE_INVALID", "PPTX 无法由 python-pptx 重开。") from exc
    finally:
        if "close_reopen_source" in locals():
            close_reopen_source()
    if expected_slides is not None and len(reopened.slides) != expected_slides:
        raise PptxEmitError("PPTX_PACKAGE_INVALID", "重开后的 slide count 与冻结计划不一致。")
    return {
        "zip_entries": len(infos),
        "uncompressed_bytes": total,
        "relationships": relationship_count,
        "slides": slide_count,
    }
