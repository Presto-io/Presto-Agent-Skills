"""Mechanical Typst emission from a reparsed final resume document."""

from __future__ import annotations

import struct
import tempfile
from pathlib import Path
from typing import Any

from graduate_resume_cli import CliError, is_stable_fact_id
from graduate_resume_layout import ColumnComposition, FrozenResumePlan, LAYOUT_PLAN_INVALID
from graduate_resume_final_markdown import FinalResumeDocument
from graduate_resume_typst_runtime import TypstExecutable
from graduate_resume_profile import personal_fields, paragraph_text
from graduate_resume_emphasis import emphasis_spans


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
        '#set page(width: 35mm, height: 49mm, margin: 0pt, fill: none)\n'
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


def _content(value: str, terms: tuple[str, ...] = (), *, academic: bool = False) -> str:
    pieces = []
    position = 0
    for start, end in emphasis_spans(value, terms, academic):
        pieces.append(typst_content(value[position:start]))
        pieces.append(f"#strong[{typst_content(value[start:end])}]")
        position = end
    pieces.append(typst_content(value[position:]))
    return "[" + "".join(pieces) + "]"


def _content_tuple(values: list[str], terms: tuple[str, ...] = ()) -> str:
    rendered = ", ".join(_content(value, terms) for value in values)
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
    summary_value = _join(fields.get("summary", [""]))
    personal_values = personal_fields(summary_value)
    summary = "[]" if personal_values else _content(paragraph_text(summary_value))
    def detail_pairs(values: Any) -> str:
        pairs = ", ".join(f"({_content(label)}, {_content(value)})" for label, value in values)
        return f"({pairs},)" if pairs else "()"
    personal = detail_pairs(personal_values)
    labels = {"phone": "电话", "email": "邮箱", "city": "现居地", "address": "地址", "website": "网站", "github": "GitHub", "wechat": "微信"}
    contact_values = [
        (labels[key.split('.', 1)[1]], value)
        for key, value in container.fields if key.startswith("contact.")
    ]
    contact = detail_pairs(contact_values)
    headline_values = fields.get("headline", [])
    directions = _content(_join([value for value in fields.get("directions", []) if value not in headline_values], " / "))
    return (
        "#identity-block("
        f'"{typst_content(theme)}", name: {name}, headline: {headline}, '
        f"summary: {summary}, contact: {contact}, personal: {personal}, directions: {directions}, photo: {photo})"
    )


def _emit_entry(container: Any, theme: str, show_heading: bool) -> str:
    fields = _field_map(container)
    terms = container.emphasis_terms
    if container.section == "education":
        title = _join(fields.get("school", []))
        meta = _join(fields.get("major", []) + fields.get("degree", []) + fields.get("start", []) + fields.get("end", []))
        academic_lines = []
        for key, label in (("honors", "成绩与荣誉"), ("courses", "相关课程")):
            if fields.get(key):
                academic_lines.append(_content(label + "：" + paragraph_text(_join(fields[key], "；")), terms, academic=True)[1:-1])
        summary_content = "[" + "#linebreak()".join(academic_lines) + "]"
    else:
        title = _join(fields.get("title", []) or fields.get("name", []))
        meta = _join(fields.get("organization", []) + fields.get("role", []) + fields.get("issuer", []) + fields.get("start", []) + fields.get("end", []) + fields.get("issued_on", []) + fields.get("expires_on", []))
        summary = _join(fields.get("summary", []) + fields.get("note", []) + fields.get("tools", []), "；")
        summary_content = _content(paragraph_text(summary), terms)
    outcomes = fields.get("outcomes", [])
    outcome_content = _content_tuple([paragraph_text(value) for value in outcomes], terms)
    return (
        "#resume-entry("
        f'"{typst_content(theme)}", "{typst_content(container.section)}", "{typst_content(container.id)}", '
        f"title: {_content(title)}, meta: {_content(meta)}, summary: {summary_content}, outcomes: {outcome_content}, show-heading: {'true' if show_heading else 'false'})"
    )


def _emit_fact_block(container: Any, theme: str, show_heading: bool) -> str:
    fields = _field_map(container)
    if container.section == "skills":
        group = _join(fields.get("group", []))
        items = fields.get("items", [])
        note = _join(fields.get("note", []))
        item_content = _content_tuple([paragraph_text(value) for value in items], container.emphasis_terms)
        return f'#skills-block("{typst_content(theme)}", "{typst_content(container.section)}", group: {_content(group)}, items: {item_content}, note: {_content(paragraph_text(note), container.emphasis_terms)}, show-heading: {'true' if show_heading else 'false'})'
    values = []
    for key, field_values in fields.items():
        if key in {"name", "title", "summary", "outcomes", "items"}:
            continue
        values.extend(paragraph_text(value) if key == "note" else value for value in field_values)
    content = _content_tuple(values, container.emphasis_terms)
    return f'#fact-block("{typst_content(theme)}", "{typst_content(container.section)}", {content}, show-heading: {'true' if show_heading else 'false'})'


def emit_page_body(containers: tuple[Any, ...], theme: str, photo: str = "none", continuation: bool = False, function: str = "resume-body", composition: ColumnComposition | None = None) -> str:
    slots: dict[str, list[str]] = {"header": [], "sidebar": [], "main": []}
    previous_sections: dict[str, str] = {}
    sidebar_sections = {"skills", "certificates"} if theme == "modern" else {"education", "skills", "certificates"} if theme == "expressive" else set()
    if composition is not None:
        sidebar_sections = set(composition.sidebar_sections)
    for container in containers:
        is_sidebar = container.section in sidebar_sections if composition is None else composition.is_sidebar(container)
        slot = "header" if container.section == "candidate" else "sidebar" if is_sidebar else "main"
        show_heading = container.section != previous_sections.get(slot)
        if container.section == "candidate":
            item = _emit_profile(container, photo, theme)
        elif container.kind == "list-entry" or container.section == "education":
            item = _emit_entry(container, theme, show_heading)
        else:
            item = _emit_fact_block(container, theme, show_heading)
        if composition is not None and container.section != "candidate":
            item = item[:-1] + f", detail-gap: {composition.detail_gap_mm}mm)"
        gap = 0.0 if composition is None else composition.sidebar_gap_mm if slot == "sidebar" else composition.main_gap_mm if slot == "main" else 0.0
        if slots[slot] and gap:
            slots[slot].append(f'#v({gap:.4f}mm, weak: false)')
        slots[slot].append(item)
        previous_sections[slot] = container.section
    arguments = ", ".join(f"{slot}: [\n" + "\n".join(items) + "\n]" for slot, items in slots.items())
    geometry = "" if composition is None else f", sidebar-width: {composition.sidebar_width_mm}mm, leading: {composition.leading_em}em"
    return f'#{function}("{theme}", continuation: {"true" if continuation else "false"}, {arguments}{geometry})'


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
                photo = f'image(bytes(({values})), format: "png", fit: "contain", width: 100%, height: 100%)'
            else:
                photo = f'image("{plan.photo.logical_path}", fit: "contain", width: 100%, height: 100%)'
        pages.append(emit_page_body(tuple(by_id[container_id] for container_id in page.containers), plan.theme_key, photo, bool(page_index), "resume-page", page.composition))
    prefix = template.read_text(encoding="utf-8") + "\n// compatibility marker: #resume.theme-layout(\n"
    return prefix + "\n#pagebreak()\n".join(pages) + "\n"
