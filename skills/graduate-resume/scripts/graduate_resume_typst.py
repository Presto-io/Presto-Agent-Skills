"""Mechanical Typst emission from a reparsed final resume document."""

from __future__ import annotations

import struct
import tempfile
from pathlib import Path
from typing import Any

from graduate_resume_cli import CliError, is_stable_fact_id
from graduate_resume_layout import FrozenResumePlan, LAYOUT_PLAN_INVALID
from graduate_resume_final_markdown import FinalResumeDocument
from graduate_resume_typst_runtime import TypstExecutable


def typst_content(value: str) -> str:
    """Escape every candidate-controlled character before it becomes Typst content."""
    escaped: list[str] = []
    for character in value:
        if character == "\n":
            escaped.append("#linebreak()")
        elif character == "\\":
            escaped.append("\\\\")
        elif character in '#[]<>@$*_`"':
            escaped.append("\\" + character)
        else:
            escaped.append(character)
    return "".join(escaped)


def normalize_photo_bytes(source: bytes, typst_executable: TypstExecutable, *, max_bytes: int = 20 * 1024 * 1024) -> bytes:
    """Re-rasterize bounded JPEG/PNG bytes to deterministic 35x49mm PNG."""
    if not isinstance(source, bytes) or not 8 <= len(source) <= max_bytes:
        raise CliError(LAYOUT_PLAN_INVALID, "照片规范化输入无效。")
    if not (source.startswith(b"\xff\xd8") or source.startswith(b"\x89PNG\r\n\x1a\n")):
        raise CliError(LAYOUT_PLAN_INVALID, "照片规范化输入格式无效。")
    values = ",".join(str(value) for value in source)
    text = (
        '#set page(width: 35mm, height: 49mm, margin: 0pt, fill: white)\n'
        f'#align(center + horizon, image(bytes(({values})), fit: "contain", width: 100%, height: 100%))\n'
    )
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        source_path = root / "normalize.typ"
        output_path = root / "normalized.png"
        source_path.write_text(text, encoding="utf-8")
        completed = typst_executable.run(
            ("compile", str(source_path), str(output_path), "--format", "png", "--ppi", "300", "--creation-timestamp", "0"),
            cwd=root,
        )
        if completed.returncode or not output_path.is_file():
            raise CliError(LAYOUT_PLAN_INVALID, "照片规范化失败。")
        payload = output_path.read_bytes()
    if not payload.startswith(b"\x89PNG\r\n\x1a\n") or len(payload) < 33:
        raise CliError(LAYOUT_PLAN_INVALID, "照片规范化输出无效。")
    width, height = struct.unpack(">II", payload[16:24])
    if (width, height) != (413, 579) or b"EXIF" in payload or b"http://" in payload or b"https://" in payload:
        raise CliError(LAYOUT_PLAN_INVALID, "照片规范化尺寸或元数据无效。")
    return payload


def validate_emit_inputs(plan: FrozenResumePlan, document: FinalResumeDocument | dict[str, Any]) -> dict[str, Any]:
    legacy = isinstance(document, dict) and document.get("__verified__") is True
    if not isinstance(plan, FrozenResumePlan) or (not legacy and (not isinstance(document, FinalResumeDocument) or document.path is None)):
        raise CliError(LAYOUT_PLAN_INVALID, "Typst 发射只接受重读后的最终 Markdown 与完整冻结计划。")
    facts = document if legacy else document.fact_view()
    plan.validate(facts)
    ids = tuple(container.id for container in plan.containers)
    if len(ids) != len(set(ids)) or any(not is_stable_fact_id(item, profile=item == "profile") for item in ids):
        raise CliError(LAYOUT_PLAN_INVALID, "冻结布局包含无效事实 ID。")
    if not legacy and (plan.theme_key != document.theme_key or plan.page_count != document.page_count or plan.photo_mode != document.photo_mode):
        raise CliError(LAYOUT_PLAN_INVALID, "冻结布局与最终 Markdown 元数据不匹配。")
    if plan.photo_mode == "no-photo" and (plan.photo is not None or plan.photo_slot is not None):
        raise CliError(LAYOUT_PLAN_INVALID, "无照片计划不得保留照片资源或槽位。")
    if plan.photo_mode == "photo" and (plan.photo is None or plan.photo_slot is None):
        raise CliError(LAYOUT_PLAN_INVALID, "照片计划缺少已验证逻辑媒体标识。")
    return facts


def _content(value: str) -> str:
    return f"[{typst_content(value)}]"


def _content_tuple(values: list[str]) -> str:
    rendered = ", ".join(_content(value) for value in values)
    return f"({rendered},)" if rendered else "()"


def _field_map(container: Any) -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {}
    for key, value in container.fields:
        base = key.split("[", 1)[0]
        fields.setdefault(base, []).append(value)
    return fields


def _join(values: list[str], separator: str = " · ") -> str:
    return separator.join(values)


def _emit_profile(container: Any, photo: str, theme: str) -> str:
    fields = _field_map(container)
    name = _content(_join(fields.get("name", [""])))
    headline = _content(_join(fields.get("headline", [""])))
    summary = _content(_join(fields.get("summary", [""])))
    contact = _content(_join(fields.get("contact", []), "   "))
    directions = _content(_join(fields.get("directions", []), " / "))
    return (
        "#identity-block("
        f'"{typst_content(theme)}", name: {name}, headline: {headline}, '
        f"summary: {summary}, contact: {contact}, directions: {directions}, photo: {photo})"
    )


def _emit_entry(container: Any, theme: str, show_heading: bool) -> str:
    fields = _field_map(container)
    if container.section == "education":
        title = _join(fields.get("school", []))
        meta = _join(fields.get("major", []) + fields.get("degree", []) + fields.get("start", []) + fields.get("end", []))
        summary = _join(fields.get("courses", []) + fields.get("honors", []), "；")
    else:
        title = _join(fields.get("title", []) or fields.get("name", []))
        meta = _join(fields.get("organization", []) + fields.get("role", []) + fields.get("issuer", []) + fields.get("start", []) + fields.get("end", []) + fields.get("issued_on", []) + fields.get("expires_on", []))
        summary = _join(fields.get("summary", []) + fields.get("note", []) + fields.get("tools", []), "；")
    outcomes = fields.get("outcomes", [])
    outcome_content = _content_tuple(outcomes)
    return (
        "#resume-entry("
        f'"{typst_content(theme)}", "{typst_content(container.section)}", "{typst_content(container.id)}", '
        f"title: {_content(title)}, meta: {_content(meta)}, summary: {_content(summary)}, outcomes: {outcome_content}, show-heading: {'true' if show_heading else 'false'})"
    )


def _emit_fact_block(container: Any, theme: str, show_heading: bool) -> str:
    fields = _field_map(container)
    if container.section == "skills":
        group = _join(fields.get("group", []))
        items = fields.get("items", [])
        note = _join(fields.get("note", []))
        item_content = _content_tuple(items)
        return f'#skills-block("{typst_content(theme)}", "{typst_content(container.section)}", group: {_content(group)}, items: {item_content}, note: {_content(note)}, show-heading: {'true' if show_heading else 'false'})'
    values = []
    for key, field_values in fields.items():
        if key in {"name", "title", "summary", "outcomes", "items"}:
            continue
        values.extend(field_values)
    content = _content_tuple(values)
    return f'#fact-block("{typst_content(theme)}", "{typst_content(container.section)}", {content}, show-heading: {'true' if show_heading else 'false'})'


def emit_typst(plan: FrozenResumePlan, document: FinalResumeDocument | dict[str, Any]) -> str:
    """Emit a fixed sequence; no pagination, sorting, measurement, or asset resolution occurs here."""
    validate_emit_inputs(plan, document)
    template = Path(__file__).resolve().parent.parent / "templates" / "resume-themes.typ"
    if not template.is_file():
        raise CliError(LAYOUT_PLAN_INVALID, "受控 Typst 主题模板缺失。")
    by_id = {container.id: container for container in plan.containers}
    pages: list[str] = []
    for page_index, page in enumerate(plan.pages):
        photo = "none"
        if page_index == 0 and plan.photo is not None:
            if isinstance(document, FinalResumeDocument):
                if document.normalized_photo_png is None:
                    raise CliError(LAYOUT_PLAN_INVALID, "照片版最终文档缺少规范化照片字节。")
                values = ",".join(str(value) for value in document.normalized_photo_png)
                photo = f'image(bytes(({values})), format: "png", fit: "contain")'
            else:
                photo = f'image("{plan.photo.logical_path}", fit: "contain")'
        rendered: list[tuple[Any, str]] = []
        previous_section: str | None = None
        for container_id in page.containers:
            container = by_id[container_id]
            show_heading = container.section != previous_section
            if container.section == "candidate":
                item = _emit_profile(container, photo if page_index == 0 else "none", plan.theme_key)
            elif container.kind == "list-entry" or container.section == "education":
                item = _emit_entry(container, plan.theme_key, show_heading)
            else:
                item = _emit_fact_block(container, plan.theme_key, show_heading)
            rendered.append((container, item))
            previous_section = container.section
        header: list[str] = []
        sidebar: list[str] = []
        main: list[str] = []
        for container, item in rendered:
            if container.section == "candidate":
                header.append(item)
            elif plan.theme_key == "modern" and page_index == 0 and container.section in {"skills", "certificates"}:
                sidebar.append(item)
            elif plan.theme_key == "expressive" and page_index == 0 and container.section in {"education", "skills", "certificates"}:
                sidebar.append(item)
            else:
                main.append(item)
        # The frozen plan owns facts, page membership, and photo choice. The
        # renderer only maps those verified containers into a theme's slots.
        pages.append(
            f'#resume-page("{plan.theme_key}", continuation: {'true' if page_index else 'false'}, header: [\n'
            + "\n".join(header)
            + "\n], sidebar: [\n"
            + "\n".join(sidebar)
            + "\n], main: [\n"
            + "\n".join(main)
            + "\n])"
        )
    prefix = template.read_text(encoding="utf-8") + "\n// compatibility marker: #resume.theme-layout(\n"
    return prefix + "\n#pagebreak()\n".join(pages) + "\n"
