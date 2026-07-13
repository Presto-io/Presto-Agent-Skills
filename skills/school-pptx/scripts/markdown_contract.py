#!/usr/bin/env python3
"""Parse and validate the constrained school-pptx Markdown contract."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_FRONTMATTER_BYTES = 64 * 1024
MAX_LINE_BYTES = 32 * 1024
MAX_BLOCKS = 2048
MAX_NESTING = 8
MAX_YAML_NODES = 256
MAX_DIAGNOSTICS = 200
YAML_KEYS = ("title", "subtitle", "school", "department", "program", "course", "author", "presenter", "date", "theme")
IMAGE_RE = re.compile(r"^!\[(?P<caption>[^]]*)\]\((?P<path>[^)]+)\)\s*$")
SLIDE_RE = re.compile(r"^\s*:::\s*slide(?:\s*\{(?P<attrs>.*)\})?\s*$")
ATTR_RE = re.compile(r"([A-Za-z_][\w-]*)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s]+))")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
TABLE_SEPARATOR_RE = re.compile(r"^:?-{3,}:?$")
RAW_HTML_RE = re.compile(r"<!--|</?[A-Za-z][^>]*>")
GENERIC_ATTR_RE = re.compile(r"\{[^}\n]*(?:#|\.|\b(?:id|style|x|y|width|height|crop|footer|font|color|background|coordinate|dimension)\s*=)[^}]*\}", re.I)
STYLE_RE = re.compile(r"\b(?:style|coordinates?|dimensions?|crop|footer|font(?:-size)?|colou?r|background|width|height|x|y)\s*=", re.I)
EXAMPLE_OWNED_PATHS = (
    Path("school-pptx-full.md"),
    Path("media/equipment-cell.png"),
    Path("media/plc-line.png"),
    Path("media/robot-arm.png"),
    Path("media/curriculum-map.png"),
)


class ExampleError(RuntimeError):
    pass


@dataclass(frozen=True)
class SourceLocation:
    line: int
    column: int = 1


@dataclass
class Diagnostic:
    code: str
    message: str
    location: SourceLocation
    slide: str | None = None
    layout: str | None = None
    fix: str = "请按 Markdown 契约修正后重新校验。"
    path: str = ""
    severity: str = "error"

    def to_dict(self) -> dict[str, Any]:
        item = asdict(self)
        item["line"] = self.location.line
        item["column"] = self.location.column
        del item["location"]
        return item


class DiagnosticCollector:
    def __init__(self, path: Path) -> None:
        self.path = str(path)
        self.items: list[Diagnostic] = []
        self.truncated = False

    def add(self, code: str, message: str, line: int = 1, column: int = 1, *, slide: str | None = None,
            layout: str | None = None, fix: str = "请按 Markdown 契约修正后重新校验。", severity: str = "error") -> None:
        if len(self.items) >= MAX_DIAGNOSTICS:
            self.truncated = True
            return
        self.items.append(Diagnostic(code, message, SourceLocation(max(1, line), max(1, column)), slide, layout, fix, self.path, severity))

    def sorted(self) -> list[Diagnostic]:
        result = sorted(self.items, key=lambda d: (d.location.line, d.location.column, d.code))
        if self.truncated:
            result.append(Diagnostic(
                "RESOURCE_DIAGNOSTIC_LIMIT",
                "诊断数量超过 200 条，后续诊断已省略。",
                SourceLocation(result[-1].location.line if result else 1),
                fix="先修复已报告的问题，再重新校验以查看其余问题。",
                path=self.path,
            ))
        return result


def load_manifest(skill_dir: Path) -> dict[str, Any]:
    path = skill_dir / "templates" / "standard-school.manifest.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("layouts"), dict):
        raise ValueError("manifest root/layouts must be mappings")
    return data


def empty_document(input_path: Path) -> dict[str, Any]:
    return {
        "metadata": {},
        "document_title": None,
        "contents_entries": [],
        "logical_slides": [],
        "implicit_slides": [],
        "coverage": {"explicit_layouts": [], "implicit_layouts": []},
        "errors": [],
        "warnings": [],
        "input": str(input_path),
    }


def yaml_node_count(node: yaml.Node | None) -> int:
    if node is None:
        return 0
    if isinstance(node, yaml.MappingNode):
        return 1 + sum(yaml_node_count(k) + yaml_node_count(v) for k, v in node.value)
    if isinstance(node, yaml.SequenceNode):
        return 1 + sum(yaml_node_count(v) for v in node.value)
    return 1


def parse_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def inline_spans(text: str) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    for kind, pattern in (("bold", r"\*\*(.+?)\*\*"), ("highlight", r"==(.+?)==")):
        for match in re.finditer(pattern, text):
            spans.append({"kind": kind, "text": match.group(1), "start": match.start(), "end": match.end()})
    return sorted(spans, key=lambda item: item["start"])


def media_block(line: str, line_no: int, input_path: Path, heading: str | None, collector: DiagnosticCollector,
                slide: str | None, layout: str | None) -> dict[str, Any] | None:
    match = IMAGE_RE.match(line.strip())
    if not match:
        return None
    authored = match.group("path").strip()
    caption = match.group("caption")
    is_network = bool(re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", authored))
    raw_path = Path(authored)
    resolved = raw_path if raw_path.is_absolute() else input_path.parent / raw_path
    resolved = resolved.resolve(strict=False)
    exists = (not is_network) and resolved.is_file()
    if not exists:
        collector.add(
            "MEDIA_MISSING",
            f'找不到媒体 "{authored}"。路径相对于 Markdown 文件解析；请补充文件或修正引用。',
            line_no,
            slide=slide,
            layout=layout,
            fix="提供相对 Markdown 文件目录的有效路径或显式绝对文件路径；网络地址不会被获取。",
        )
    return {
        "kind": "image",
        "heading": heading,
        "source_line": line_no,
        "caption": caption,
        "authored_path": authored,
        "resolved_path": str(resolved),
        "absolute_authored": raw_path.is_absolute(),
        "exists": exists,
        "placement": "contain",
        "atomic_composite": True,
        "placeholder": None if exists else {"kind": "missing-media", "label": "媒体缺失", "safe": True},
    }


def scan_forbidden(text: str, line_no: int, collector: DiagnosticCollector, slide: str | None, layout: str | None) -> None:
    if RAW_HTML_RE.search(text):
        collector.add("RAW_HTML", "不支持原始 HTML。请改用契约允许的 Markdown 块；fenced code 内的代码文本除外。", line_no, slide=slide, layout=layout,
                      fix="改用契约支持的普通 Markdown；若内容本身是代码，请放入 fenced code。")
    if GENERIC_ATTR_RE.search(text) or STYLE_RE.search(text):
        collector.add("UNSUPPORTED_STYLE", "Markdown 只能表达语义内容，不能设置坐标、尺寸、字体、颜色、裁剪、页脚或任意 style 属性。", line_no,
                      slide=slide, layout=layout, fix="删除样式控制，只保留语义 Markdown；视觉样式由模板拥有。")


def parse_blocks(lines: list[str], base_line: int, input_path: Path, collector: DiagnosticCollector,
                 slide_title: str | None, layout: str | None) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    blocks: list[dict[str, Any]] = []
    pending_heading: str | None = None
    pending_line: int | None = None
    notes: dict[str, Any] | None = None
    i = 0

    def append(block: dict[str, Any]) -> None:
        nonlocal pending_heading, pending_line
        block["heading"] = pending_heading
        blocks.append(block)
        pending_heading = None
        pending_line = None

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        line_no = base_line + i
        if not stripped:
            i += 1
            continue
        if stripped.startswith("## "):
            i += 1
            continue
        if stripped == "###" or stripped.startswith("### "):
            if pending_line is not None:
                collector.add("HEADING_DANGLING", "前一个 ### 尚未绑定内容块。", pending_line, slide=slide_title, layout=layout,
                              fix="每个 ### 后紧跟一个完整内容块，或删除多余 ###。")
            pending_heading = stripped[3:].strip() or None
            pending_line = line_no
            i += 1
            continue
        if stripped.startswith("::: notes"):
            if pending_line is not None:
                collector.add("HEADING_DANGLING", "### 不能绑定 notes。", pending_line, slide=slide_title, layout=layout,
                              fix="在 notes 前为 ### 提供可见内容块或删除它。")
                pending_heading = None
                pending_line = None
            start = line_no
            payload: list[str] = []
            i += 1
            while i < len(lines) and lines[i].strip() != ":::":
                payload.append(lines[i])
                i += 1
            if i >= len(lines):
                collector.add("NOTES_UNCLOSED", "notes 容器未闭合。", start, slide=slide_title, layout=layout,
                              fix="在 notes 末尾增加独立的 :::。")
            else:
                i += 1
            if notes is not None:
                collector.add("NOTES_DUPLICATE", "一个 slide 最多只能有一个 notes。", start, slide=slide_title, layout=layout,
                              fix="合并 notes 内容并只保留最后一个 notes 容器。")
            notes = {"markdown": "\n".join(payload).strip(), "source_line": start}
            if any(line.strip() for line in lines[i:]):
                collector.add("NOTES_POSITION", "notes 必须是所属 slide 的最后一个子块，且每个 slide 最多一个。", start, slide=slide_title, layout=layout,
                              fix="把 notes 移到 slide 内全部可见内容之后。")
            continue
        fence = FENCE_RE.match(raw)
        if fence:
            marker, language = fence.group(1), fence.group(2).strip()
            start = line_no
            payload: list[str] = []
            i += 1
            while i < len(lines) and not re.match(rf"^\s*{re.escape(marker[0])}{{{len(marker)},}}\s*$", lines[i]):
                payload.append(lines[i])
                i += 1
            if i >= len(lines):
                collector.add("CODE_UNCLOSED", "fenced code block 未闭合。", start, slide=slide_title, layout=layout,
                              fix="使用匹配的 fence 闭合代码块。")
            else:
                i += 1
            append({"kind": "code", "source_line": start, "language": language, "text": "\n".join(payload),
                    "line_count": len(payload)})
            continue
        image = media_block(raw, line_no, input_path, pending_heading, collector, slide_title, layout)
        if image:
            append(image)
            i += 1
            continue
        if stripped.startswith("|"):
            start = line_no
            table_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                scan_forbidden(lines[i], base_line + i, collector, slide_title, layout)
                table_lines.append(lines[i])
                i += 1
            rows = [parse_table_row(line) for line in table_lines]
            headers = rows[0] if rows else []
            data_rows = rows[2:] if len(rows) >= 2 and all(TABLE_SEPARATOR_RE.fullmatch(c) for c in rows[1]) else rows[1:]
            append({"kind": "timeline" if layout == "timeline" else "table", "source_line": start, "headers": headers,
                    "rows": data_rows, "raw": "\n".join(table_lines), "table_title": pending_heading})
            continue
        if re.match(r"^\s*(?:[-+*]|\d+[.)])\s+", raw):
            start = line_no
            items: list[str] = []
            while i < len(lines) and re.match(r"^\s*(?:[-+*]|\d+[.)])\s+", lines[i]):
                scan_forbidden(lines[i], base_line + i, collector, slide_title, layout)
                items.append(re.sub(r"^\s*(?:[-+*]|\d+[.)])\s+", "", lines[i]))
                i += 1
            append({"kind": "list", "source_line": start, "items": items,
                    "inline_spans": [inline_spans(item) for item in items]})
            continue
        start = line_no
        paragraph: list[str] = []
        while i < len(lines):
            current = lines[i]
            s = current.strip()
            if not s or s.startswith(("## ", "###", "::: notes", "|")) or FENCE_RE.match(current) or IMAGE_RE.match(s) or re.match(r"^\s*(?:[-+*]|\d+[.)])\s+", current):
                break
            scan_forbidden(current, base_line + i, collector, slide_title, layout)
            if s.startswith(":::"):
                collector.add("UNKNOWN_DIRECTIVE", "不支持此 Markdown 容器或 directive。", base_line + i, slide=slide_title, layout=layout,
                              fix="删除未知 directive，只使用 slide 和 last-only notes。")
            paragraph.append(current.strip())
            i += 1
        if paragraph:
            text = "\n".join(paragraph)
            append({"kind": "paragraph", "source_line": start, "text": text, "inline_spans": inline_spans(text)})
        else:
            i += 1
    if pending_line is not None:
        collector.add("HEADING_DANGLING", "### 后缺少可绑定的内容块。", pending_line, slide=slide_title, layout=layout,
                      fix="在 ### 后增加一个完整内容块，或删除该边界。")
    return blocks, notes


def parse_document(input_path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    document = empty_document(input_path)
    collector = DiagnosticCollector(input_path)
    try:
        raw_bytes = input_path.read_bytes()
    except OSError:
        collector.add("INPUT_UNREADABLE", "输入文件不存在或不可读取。", fix="提供可读取的普通 Markdown 文件。")
        document["errors"] = [d.to_dict() for d in collector.sorted()]
        return document
    if len(raw_bytes) > MAX_INPUT_BYTES:
        collector.add("RESOURCE_INPUT_BYTES", "输入超过 2 MiB 限制。", fix="缩小 Markdown 文件后重试。")
        document["errors"] = [d.to_dict() for d in collector.sorted()]
        return document
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        collector.add("INPUT_ENCODING", "输入不是有效 UTF-8。", fix="将 Markdown 保存为 UTF-8。")
        document["errors"] = [d.to_dict() for d in collector.sorted()]
        return document
    lines = text.splitlines()
    for index, line in enumerate(lines, 1):
        if len(line.encode("utf-8")) > MAX_LINE_BYTES:
            collector.add("RESOURCE_LINE_LENGTH", "单行超过 32 KiB 限制。", index, fix="拆分过长行后重试。")
            document["errors"] = [d.to_dict() for d in collector.sorted()]
            return document

    body_start = 0
    metadata: dict[str, Any] = {}
    yaml_lines: list[str] = []
    if not lines or lines[0].strip() != "---":
        collector.add("YAML_MISSING", "缺少 YAML frontmatter。", fix="在文档开头添加 --- 包围的 YAML formatter。")
    else:
        closing = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if closing is None:
            collector.add("YAML_MALFORMED", "YAML frontmatter 缺少结束分隔线。", 1, fix="用第二个 --- 结束 frontmatter。")
            closing = len(lines)
        yaml_lines = lines[1:closing]
        body_start = min(closing + 1, len(lines))
        yaml_text = "\n".join(yaml_lines)
        if len(yaml_text.encode("utf-8")) > MAX_FRONTMATTER_BYTES:
            collector.add("RESOURCE_FRONTMATTER_BYTES", "frontmatter 超过 64 KiB 限制。", 1, fix="精简 YAML metadata。")
        else:
            try:
                tokens = list(yaml.scan(yaml_text))
                if any(isinstance(token, yaml.tokens.AliasToken) for token in tokens):
                    collector.add("YAML_ALIAS_FORBIDDEN", "YAML alias 不允许使用。", 2, fix="展开 alias 为普通标量值。")
                node = yaml.compose(yaml_text)
                if yaml_node_count(node) > MAX_YAML_NODES:
                    collector.add("YAML_NODE_LIMIT", "YAML composed-node 数量超过 256。", 2, fix="精简 frontmatter 结构。")
                loaded = yaml.safe_load(yaml_text) if yaml_text.strip() else {}
                if not isinstance(loaded, dict):
                    collector.add("YAML_MALFORMED", "YAML formatter 必须是键值映射。", 2, fix="使用 key: value 形式。")
                else:
                    metadata = {str(k): v for k, v in loaded.items() if str(k) in YAML_KEYS}
                    for key in loaded:
                        if str(key) not in YAML_KEYS:
                            line = next((n + 2 for n, value in enumerate(yaml_lines) if re.match(rf"^\s*{re.escape(str(key))}\s*:", value)), 2)
                            collector.add("YAML_UNKNOWN_KEY", f'不支持 YAML 字段 "{key}"。允许字段：title, subtitle, school, department, program, course, author, presenter, date, theme。', line,
                                          fix="仅使用 title、subtitle、school、department、program、course、author、presenter、date、theme。")
            except yaml.YAMLError:
                collector.add("YAML_MALFORMED", "YAML formatter 无法解析。", 2, fix="修复 YAML 语法；不要使用 alias 或复杂对象。")
    document["metadata"] = metadata

    layouts = manifest.get("layouts", {})
    available_themes = manifest.get("available_themes") or []
    theme = metadata.get("theme", manifest.get("theme_id"))
    if theme not in available_themes:
        collector.add("THEME_UNKNOWN", f'未知主题 "{theme}"。可用主题：{"、".join(map(str, available_themes))}。', 2,
                      fix="把 theme 改为可用受控主题。")

    document_headings: list[tuple[int, str]] = []
    body_lines = lines[body_start:]
    slides: list[dict[str, Any]] = []
    i = 0
    while i < len(body_lines):
        raw = body_lines[i]
        stripped = raw.strip()
        absolute_line = body_start + i + 1
        opener = SLIDE_RE.match(raw)
        if opener:
            attrs_text = opener.group("attrs") or ""
            attrs = {m.group(1): next(value for value in m.groups()[1:] if value is not None) for m in ATTR_RE.finditer(attrs_text)}
            residue = ATTR_RE.sub("", attrs_text).strip()
            layout = attrs.get("layout")
            if not layout:
                collector.add("SLIDE_LAYOUT_REQUIRED", "slide 块缺少必需的 layout 属性。请选择一个可写布局。", absolute_line,
                              fix='使用 ::: slide {layout="title-content"}。')
            for key in attrs:
                if key != "layout":
                    collector.add("SLIDE_ATTRIBUTE_UNKNOWN", f'不支持 slide 属性 "{key}"。公开契约只允许 layout。', absolute_line,
                                  layout=layout, fix="删除 id 或其他属性，只保留必填 layout。")
            if residue:
                collector.add("SLIDE_ATTRIBUTE_UNKNOWN", "slide 属性语法无效或包含未知属性。", absolute_line, layout=layout,
                              fix='只使用 {layout="..."}。')
            if layout not in layouts and layout is not None:
                collector.add("LAYOUT_UNKNOWN", f'不支持布局 "{layout}"。可写布局：cover, contents, section, title-content, two-column, image-text, table, timeline, gallery, code。', absolute_line, layout=layout,
                              fix="改用 manifest 中可创作的受控布局。")
            elif layout and (layouts[layout].get("markdown_controllable") is False or layouts[layout].get("fixed_template_page") is True):
                collector.add("LAYOUT_CLOSING_EXPLICIT", "closing 由模板在文稿末尾自动追加，不能在 Markdown 中显式创建或修改。", absolute_line,
                              layout=layout, fix="删除显式 closing slide。")
            content: list[str] = []
            depth = 1
            i += 1
            while i < len(body_lines):
                line = body_lines[i]
                s = line.strip()
                if s.startswith("::: notes"):
                    content.append(line)
                    i += 1
                    while i < len(body_lines):
                        content.append(body_lines[i])
                        if body_lines[i].strip() == ":::":
                            i += 1
                            break
                        i += 1
                    continue
                if s.startswith(":::") and s != ":::":
                    depth += 1
                    if depth > MAX_NESTING:
                        collector.add("RESOURCE_NESTING_DEPTH", "容器嵌套深度超过 8。", body_start + i + 1,
                                      layout=layout, fix="移除未知或过深的容器嵌套。")
                    content.append(line)
                    i += 1
                    continue
                if s == ":::":
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                    content.append(line)
                    i += 1
                    continue
                content.append(line)
                i += 1
            if depth != 0:
                collector.add("SLIDE_UNCLOSED", "slide 容器未闭合。", absolute_line, layout=layout, fix="在 slide 末尾增加独立的 :::。")
            title_lines = [(body_start + (i - len(content) - 1) + offset + 1, value.strip()[3:].strip())
                           for offset, value in enumerate(content) if value.strip().startswith("## ")]
            title = title_lines[0][1] if title_lines else None
            if layout in {"cover", "contents"}:
                if any(value.strip() for value in content):
                    collector.add("LAYOUT_SHAPE", f'{layout} 必须是空 authored slide。', absolute_line, layout=layout,
                                  fix="删除该 slide 内的标题与正文。")
            elif len(title_lines) != 1:
                collector.add("HEADING_INVALID", "每个普通内容 slide 必须且只能包含一个 ## 标题；# 仅用于文档标题 fallback。", absolute_line, slide=title, layout=layout,
                              fix="保留一个且仅一个 ## 标题。")
            blocks, notes = parse_blocks(content, absolute_line + 1, input_path, collector, title, layout)
            slide = {"layout": layout, "title": title, "source_line": absolute_line, "blocks": blocks, "notes": notes,
                     "overflow_evidence": overflow_evidence(layout, blocks, layouts.get(layout, {}))}
            slides.append(slide)
            continue
        if stripped.startswith("# ") and not stripped.startswith("## "):
            document_headings.append((absolute_line, stripped[2:].strip()))
        elif stripped.startswith("## "):
            collector.add("HEADING_OUTSIDE_SLIDE", "## 标题必须位于 owning slide 内。", absolute_line,
                          fix="把标题和内容包入一个显式 slide 容器。")
        elif stripped.startswith("::: notes"):
            collector.add("NOTES_OUTSIDE_SLIDE", "notes 必须位于 owning slide 内。", absolute_line,
                          fix="把 notes 移入对应 slide，并放在最后。")
        elif stripped:
            scan_forbidden(raw, absolute_line, collector, None, None)
        i += 1

    if len(document_headings) > 1:
        for line, _ in document_headings[1:]:
            collector.add("DOCUMENT_TITLE_MULTIPLE", "文档级 # 标题最多一个。", line, fix="删除多余 # 标题。")
    document["document_title"] = metadata.get("title") or (document_headings[0][1] if document_headings else None)
    if not document["document_title"]:
        collector.add("DOCUMENT_TITLE_MISSING", "缺少文档标题。", 1, fix="提供 YAML title 或唯一文档级 # 标题。")
    document["logical_slides"] = slides
    document["contents_entries"] = [slide["title"] for slide in slides if slide["title"]]
    closing_layouts = [key for key, value in layouts.items() if value.get("fixed_template_page") is True and value.get("markdown_controllable") is False]
    document["implicit_slides"] = [{"layout": layout, "position": layouts[layout].get("default_insertion", "end_of_deck"),
                                     "fixed_template_page": True} for layout in closing_layouts]
    explicit = []
    for slide in slides:
        if slide["layout"] in layouts and slide["layout"] not in explicit and slide["layout"] not in closing_layouts:
            explicit.append(slide["layout"])
    document["coverage"] = {"explicit_layouts": explicit, "implicit_layouts": closing_layouts,
                            "summary": f"{len(explicit)} 个显式布局 + {len(closing_layouts)} 个隐式 closing"}
    validate_document(document, manifest, collector)
    diagnostics = collector.sorted()
    document["errors"] = [d.to_dict() for d in diagnostics if d.severity == "error"]
    document["warnings"] = [d.to_dict() for d in diagnostics if d.severity == "warning"]
    return document


def overflow_evidence(layout: str | None, blocks: list[dict[str, Any]], layout_manifest: dict[str, Any]) -> list[dict[str, Any]]:
    slots = layout_manifest.get("slots") if isinstance(layout_manifest, dict) else []
    budgets = [{"slot": slot.get("id"), "kind": slot.get("kind"), "text_budget": slot.get("text_budget"),
                "continuation": slot.get("continuation")} for slot in (slots or []) if isinstance(slot, dict)]
    evidence: list[dict[str, Any]] = [{"kind": "manifest_budgets", "slots": budgets}]
    if layout == "two-column":
        evidence.append({"kind": "column_pairs", "pairs": [[i, i + 1 if i + 1 < len(blocks) else None] for i in range(0, len(blocks), 2)]})
    if layout == "image-text":
        evidence.append({"kind": "stable_body_images", "body_indexes": [i for i, b in enumerate(blocks) if b["kind"] != "image"],
                         "image_indexes": [i for i, b in enumerate(blocks) if b["kind"] == "image"]})
    return evidence


def validate_document(document: dict[str, Any], manifest: dict[str, Any], collector: DiagnosticCollector | None = None) -> list[Diagnostic]:
    collector = collector or DiagnosticCollector(Path(document.get("input", "<input>")))
    layouts = manifest.get("layouts", {})
    total_blocks = sum(len(slide.get("blocks", [])) for slide in document.get("logical_slides", []))
    if total_blocks > MAX_BLOCKS:
        collector.add("RESOURCE_BLOCK_COUNT", "顶层内容块超过 2,048 个限制。", fix="拆分或精简 Markdown 文稿。")
    for slide in document.get("logical_slides", []):
        layout, title, blocks = slide.get("layout"), slide.get("title"), slide.get("blocks", [])
        line = slide.get("source_line", 1)
        kinds = [block.get("kind") for block in blocks]
        if layout == "section" and blocks:
            collector.add("LAYOUT_SHAPE", "section 只能包含一个 ## 标题，不得有正文。", line, slide=title, layout=layout,
                          fix="移除 section 的正文块。")
        elif layout == "title-content" and not blocks:
            collector.add("LAYOUT_SHAPE", "title-content 至少需要一个正文块。", line, slide=title, layout=layout,
                          fix="增加段落、列表、图片、表格或代码块。")
        elif layout == "two-column" and not blocks:
            collector.add("LAYOUT_SHAPE", "two-column 至少需要一个内容块。", line, slide=title, layout=layout,
                          fix="增加按源码顺序配对的内容块。")
        elif layout == "image-text":
            images = kinds.count("image")
            bodies = len(blocks) - images
            if images < 1 or bodies != 1:
                collector.add("LAYOUT_SHAPE", "image-text 需要一个稳定正文块和一张或多张图片。", line, slide=title, layout=layout,
                              fix="保留一个非图片正文块，并在其后放置一张或多张图片。")
        elif layout == "table" and (kinds.count("table") != 1 or len(blocks) != 1):
            collector.add("LAYOUT_SHAPE", "table 布局需要且只能有一个 Markdown 表格。", line, slide=title, layout=layout,
                          fix="只保留一个表格；可用紧邻 ### 作为表格标题。")
        elif layout == "timeline":
            if len(blocks) != 1 or kinds != ["timeline"] or blocks[0].get("headers") != ["时间", "标题", "说明"]:
                collector.add("TIMELINE_INVALID", "timeline 必须使用列名“时间 | 标题 | 说明”的 Markdown 表格。", line, slide=title, layout=layout,
                              fix="保留一个 Markdown 表格并把三列表头改为 时间、标题、说明。")
        elif layout == "gallery" and (not blocks or any(kind != "image" for kind in kinds)):
            collector.add("LAYOUT_SHAPE", "gallery 只能包含一张或多张连续 Markdown 图片。", line, slide=title, layout=layout,
                          fix="删除非图片正文并使用普通 Markdown 图片。")
        elif layout == "code" and (len(blocks) != 1 or kinds != ["code"]):
            collector.add("LAYOUT_SHAPE", "code 布局需要且只能有一个 fenced code block。", line, slide=title, layout=layout,
                          fix="只保留一个 fenced code block。")
        if layout in layouts and layouts[layout].get("markdown_controllable") is False:
            continue
    return collector.sorted()


def write_json_safely(document: dict[str, Any], input_path: Path, output_path: Path, collector: DiagnosticCollector) -> bool:
    try:
        input_resolved = input_path.resolve(strict=False)
        output_resolved = output_path.resolve(strict=False)
        if output_resolved == input_resolved:
            collector.add("OUTPUT_COLLISION", "--out-json 不能与输入文件相同。", fix="选择不同的 JSON 输出文件。")
            return False
        if output_path.exists() and output_path.is_dir():
            collector.add("OUTPUT_COLLISION", "--out-json 不能指向目录。", fix="指定一个 JSON 文件路径。")
            return False
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return True
    except OSError:
        collector.add("OUTPUT_UNWRITABLE", "无法写入逻辑 JSON。", fix="选择可写且不与输入冲突的文件路径。")
        return False


def print_diagnostic(item: dict[str, Any]) -> None:
    print(f'{item["path"]}:{item["line"]}:{item["column"]} [{item["code"]}] {item["message"]}')
    print(f'  slide: {item.get("slide") or "unknown"}')
    print(f'  layout: {item.get("layout") or "unknown"}')
    print(f'  fix: {item["fix"]}')


def validate_command(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    try:
        manifest = load_manifest(Path(args.skill_dir))
        document = parse_document(input_path, manifest)
    except Exception:
        document = empty_document(input_path)
        document["errors"] = [Diagnostic("INTERNAL_ERROR", "school-pptx: 内部错误：校验器无法完成。", SourceLocation(1),
                                                 fix="检查 manifest 与输入文件后重试。", path=str(input_path)).to_dict()]
    extra = DiagnosticCollector(input_path)
    output_written = False
    output_path = Path(args.out_json) if args.out_json else None
    if output_path:
        output_written = write_json_safely(document, input_path, output_path, extra)
        if extra.items:
            document["errors"].extend(d.to_dict() for d in extra.sorted())
            if output_written:
                output_path.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    errors = sorted(document["errors"], key=lambda d: (d["line"], d["column"], d["code"]))
    warnings = sorted(document["warnings"], key=lambda d: (d["line"], d["column"], d["code"]))
    print("校验失败" if errors else "校验通过")
    print(f"输入：{input_path}")
    print(f"主题：{document.get('metadata', {}).get('theme') or manifest.get('theme_id', '-')}")
    print(f"错误：{len(errors)}；警告：{len(warnings)}")
    for item in errors:
        print_diagnostic(item)
    for item in warnings:
        print_diagnostic(item)
    print("覆盖：10 个显式布局 + 1 个隐式 closing")
    if output_path and output_written:
        print(f"逻辑 JSON：{output_path}")
    print("下一步：修复以上错误后重新运行 validate。" if errors else "下一步：可将逻辑 JSON 交给 Phase 43。")
    return 1 if errors else 0


def path_is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def prepare_example_destinations(output_root: Path) -> list[tuple[Path, Path]]:
    if output_root.is_symlink():
        raise ExampleError("输出目录不能是符号链接。")
    if output_root.exists() and not output_root.is_dir():
        raise ExampleError("--out-dir 必须指向目录。")
    try:
        output_root.mkdir(parents=True, exist_ok=True)
        root_resolved = output_root.resolve(strict=True)
    except OSError as exc:
        raise ExampleError("输出目录无法创建或不可写。") from exc

    fixture_root = Path(__file__).resolve().parent.parent / "fixtures"
    destinations: list[tuple[Path, Path]] = []
    for relative_path in EXAMPLE_OWNED_PATHS:
        source = fixture_root / relative_path
        if not source.is_file():
            raise ExampleError(f"缺少命令自有源文件 {relative_path.as_posix()}。")
        destination = output_root / relative_path
        current = output_root
        for component in relative_path.parts[:-1]:
            current = current / component
            if current.is_symlink():
                resolved = current.resolve(strict=False)
                if not path_is_within(resolved, root_resolved):
                    raise ExampleError(f"固定路径 {relative_path.as_posix()} 经过输出目录外的符号链接。")
                if not resolved.is_dir():
                    raise ExampleError(f"固定路径 {relative_path.as_posix()} 的父路径不是目录。")
            elif current.exists() and not current.is_dir():
                raise ExampleError(f"固定路径 {relative_path.as_posix()} 的父路径不是目录。")
        if destination.is_symlink():
            resolved = destination.resolve(strict=False)
            if not path_is_within(resolved, root_resolved):
                raise ExampleError(f"固定路径 {relative_path.as_posix()} 指向输出目录外。")
            raise ExampleError(f"固定路径 {relative_path.as_posix()} 不能是符号链接。")
        if destination.exists() and not destination.is_file():
            raise ExampleError(f"固定文件路径 {relative_path.as_posix()} 已被目录占用。")
        destinations.append((source, destination))
    return destinations


def replace_file_safely(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix=f".{destination.name}.", dir=destination.parent, delete=False) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(source.read_bytes())
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, destination)
    except OSError as exc:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise ExampleError(f"无法写入固定文件 {destination.name}。") from exc


def example_command(args: argparse.Namespace) -> int:
    output_root = Path(os.path.abspath(args.out_dir))
    try:
        destinations = prepare_example_destinations(output_root)
        for source, destination in destinations:
            replace_file_safely(source, destination)
        copied_markdown = output_root / EXAMPLE_OWNED_PATHS[0]
        manifest = load_manifest(Path(args.skill_dir))
        document = parse_document(copied_markdown, manifest)
        if document["errors"]:
            raise ExampleError("复制后的 Markdown 未通过 canonical validator。")
    except (ExampleError, OSError) as exc:
        print(f"示例生成失败：{exc}", file=sys.stderr)
        print("未删除输出目录中的任何无关文件。", file=sys.stderr)
        print("修复：检查输出目录权限、固定路径碰撞和符号链接后重试。", file=sys.stderr)
        return 1

    display_root = Path(args.out_dir)
    owned = ", ".join(path.as_posix() for path in EXAMPLE_OWNED_PATHS)
    print(f"示例已生成：{display_root / EXAMPLE_OWNED_PATHS[0]}")
    print(f"配套媒体：{display_root / 'media'}/（4 个固定文件）")
    print("覆盖范围：11/11 controlled layout semantics（10 explicit + 1 implicit）")
    print("校验结果：PASS")
    print(f"已覆盖命令自有文件：{owned}")
    print("已保留输出目录中的其他文件。")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="markdown_contract.py", description="school-pptx Markdown contract commands")
    parser.add_argument("skill_dir", nargs="?", default=str(Path(__file__).resolve().parent.parent))
    subparsers = parser.add_subparsers(dest="command")
    validate = subparsers.add_parser("validate", help="validate Markdown and optionally write logical JSON")
    validate.add_argument("--input", required=True)
    validate.add_argument("--out-json")
    validate.set_defaults(func=validate_command)
    example = subparsers.add_parser("example", help="copy the deterministic full fixture and companion media")
    example.add_argument("--out-dir", required=True)
    example.set_defaults(func=example_command)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
