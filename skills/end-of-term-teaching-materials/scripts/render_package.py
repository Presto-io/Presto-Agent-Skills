#!/usr/bin/env python3
"""Render end-of-term teaching-materials fixtures without external packages."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape

VERSION = "0.5.0"
PACKAGE_ARTIFACTS = [
    "成绩记分册",
    "成绩汇总表",
    "成绩分析表",
    "教学日志封面",
    "过程考核评价表封面",
    "交接班记录封面",
]
BASE_SCORE_COLUMNS = ["学号", "姓名"]
TRAILING_SCORE_COLUMNS = ["考勤", "作业", "期末"]
DERIVED_SCORE_COLUMNS = ["平时分", "学期成绩"]
WARNING_FILL = "rgb(\"#ffe0e0\")"


class RenderError(RuntimeError):
    pass


@dataclass
class MarkdownPackage:
    meta: dict[str, Any]
    students: list[str]
    tasks: list[dict[str, Any]]
    score_headers: list[str]
    score_rows: list[dict[str, str]]
    analysis: dict[str, str]
    review_text: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8", newline="\n")


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise RenderError(f"invalid JSON: {path}: {exc}") from exc


def json_default(data: dict[str, Any], key: str, default: Any) -> Any:
    value = data.get(key, default)
    return default if value is None else value


def scalar(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def is_blank_score(value: Any) -> bool:
    return value in ("", None)


def score_number(value: Any) -> float | None:
    if isinstance(value, bool) or is_blank_score(value):
        return None
    text = scalar(value).strip()
    if text.endswith("?"):
        return None
    try:
        return float(text)
    except ValueError:
        return None


def validate_score_value(value: Any, *, allow_uncertain: bool, location: str) -> str | None:
    if is_blank_score(value):
        return None
    if isinstance(value, bool):
        return f"{location} must be a numeric score, blank, or review value like 87?"
    text = scalar(value).strip()
    uncertain = text.endswith("?")
    number_text = text[:-1] if uncertain else text
    if uncertain and not allow_uncertain:
        return "uncertain score values must be reviewed before export"
    if uncertain and not number_text:
        return f"{location} has malformed uncertain score: {text}"
    try:
        number = float(number_text)
    except ValueError:
        return f"{location} has malformed score: {text}"
    if number < 0 or number > 100:
        return f"{location} score out of range 0-100: {text}"
    if uncertain and not allow_uncertain:
        return "uncertain score values must be reviewed before export"
    return None


def list_value(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [scalar(item) for item in value]
    return [scalar(value)]


def package_flags(meta: dict[str, Any]) -> dict[str, bool]:
    raw = meta.get("package") or {}
    return {name: bool(raw.get(name, True)) for name in PACKAGE_ARTIFACTS}


def source_score_cells(data: dict[str, Any]) -> list[tuple[dict[str, Any], str, Any, str]]:
    tasks = data.get("tasks") or []
    task_names = [task.get("task_name") for task in tasks]
    cells: list[tuple[dict[str, Any], str, Any, str]] = []
    for row in data.get("scores") or []:
        row_tasks = row.get("tasks") or {}
        for index, task_name in enumerate(task_names, start=1):
            cells.append((row, f"任务{index}（{task_name}）", row_tasks.get(task_name, ""), f"task {index}"))
        for key, label in [("attendance", "考勤"), ("homework", "作业"), ("final", "期末")]:
            cells.append((row, label, row.get(key), key))
    return cells


def uncertain_source_markers(data: dict[str, Any]) -> list[dict[str, str]]:
    markers: list[dict[str, str]] = []
    for row, label, value, _source_key in source_score_cells(data):
        text = scalar(value).strip()
        if not text.endswith("?"):
            continue
        student = scalar(row.get("name")) or scalar(row.get("student_id")) or "<unknown>"
        markers.append(
            {
                "type": "需复核",
                "location": f"成绩数据 / {student} / {label}",
                "value": text,
                "note": f"{student} 的 {label} 当前为 {text}，需教师确认后删除复核标记。",
            }
        )
    return markers


def marker_matches(existing: dict[str, Any], generated: dict[str, str]) -> bool:
    return (
        scalar(existing.get("location")) == generated["location"]
        and scalar(existing.get("value")) == generated["value"]
    )


def merged_review_markers(data: dict[str, Any]) -> list[dict[str, Any]]:
    markers = list(data.get("review_markers") or [])
    for generated in uncertain_source_markers(data):
        if not any(marker_matches(existing, generated) for existing in markers):
            markers.append(generated)
    return markers


def validate_source_data(data: dict[str, Any], export_ready: bool = True) -> list[str]:
    errors: list[str] = []
    for key in [
        "template",
        "date",
        "school_year",
        "semester",
        "major_name",
        "course_name",
        "class_name",
        "teachers",
        "students",
        "tasks",
        "scores",
    ]:
        if key not in data or data[key] in ("", [], None):
            errors.append(f"missing required field: {key}")
    if data.get("template") != "end-of-term-teaching-materials":
        errors.append("template must be end-of-term-teaching-materials")
    tasks = data.get("tasks") or []
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks must be a non-empty array")
    for index, task in enumerate(tasks, start=1):
        if not task.get("task_name"):
            errors.append(f"task {index} missing task_name")
        if task.get("hours") in ("", None):
            errors.append(f"task {index} missing hours")
    students = data.get("students") or []
    scores = data.get("scores") or []
    if len(scores) != len(students):
        errors.append("scores length must match students length")
    task_names = [task.get("task_name") for task in tasks]
    for row in scores:
        row_tasks = row.get("tasks") or {}
        for task_name in task_names:
            if task_name not in row_tasks:
                errors.append(f"score row for {row.get('name', '<unknown>')} missing task: {task_name}")
    allow_uncertain = not export_ready
    for row, label, value, _source_key in source_score_cells(data):
        student = scalar(row.get("name")) or scalar(row.get("student_id")) or "<unknown>"
        error = validate_score_value(value, allow_uncertain=allow_uncertain, location=f"{student} {label}")
        if error:
            errors.append(error)
    if export_ready and data.get("review_markers"):
        errors.append("review_markers must be empty before export")
    return errors


def yaml_lines(meta: dict[str, Any]) -> list[str]:
    lines = ["---"]
    simple_keys = [
        "template",
        "date",
        "school_year",
        "semester",
        "major_name",
        "course_name",
        "course_type_label",
    ]
    for key in simple_keys:
        lines.append(f"{key}: {meta.get(key, '')}")
    for key in ["class_name", "teachers", "handover_class_name", "handover_teachers"]:
        values = list_value(meta.get(key))
        if values:
            lines.append(f"{key}:")
            for value in values:
                lines.append(f"  - {value}")
    flags = package_flags(meta)
    lines.append("package:")
    for name in PACKAGE_ARTIFACTS:
        lines.append(f"  {name}: {str(flags[name]).lower()}")
    lines.append("---")
    return lines


def generate_markdown(data: dict[str, Any]) -> str:
    errors = validate_source_data(data, export_ready=False)
    if errors:
        raise RenderError("; ".join(errors))
    lines = yaml_lines(data)
    lines.extend(["", "## 我带的学生", ""])
    for student in data["students"]:
        student_id = scalar(student.get("student_id"))
        name = scalar(student.get("name"))
        lines.append(f"{student_id} {name}".strip())

    lines.extend(["", "## 过程考核任务", ""])
    for index, task in enumerate(data["tasks"], start=1):
        lines.append(f"{index}. {task['task_name']}-{task['hours']}")

    task_count = len(data["tasks"])
    headers = BASE_SCORE_COLUMNS + [f"任务{i}" for i in range(1, task_count + 1)] + TRAILING_SCORE_COLUMNS
    aligns = ["---", "---"] + ["---:"] * (task_count + len(TRAILING_SCORE_COLUMNS))
    lines.extend(["", "## 成绩数据", "", "| " + " | ".join(headers) + " |", "| " + " | ".join(aligns) + " |"])
    task_names = [task["task_name"] for task in data["tasks"]]
    by_student = {scalar(row.get("student_id")) or scalar(row.get("name")): row for row in data["scores"]}
    for student in data["students"]:
        key = scalar(student.get("student_id")) or scalar(student.get("name"))
        row = by_student.get(key, {})
        row_tasks = row.get("tasks") or {}
        values = [scalar(student.get("student_id")), scalar(student.get("name"))]
        values.extend(scalar(row_tasks.get(task_name, "")) for task_name in task_names)
        values.extend([scalar(row.get("attendance")), scalar(row.get("homework")), scalar(row.get("final"))])
        lines.append("| " + " | ".join(values) + " |")

    analysis = data.get("analysis") or {}
    lines.extend(["", "## 分析", "", "### 试卷分析", "", scalar(analysis.get("exam", "无")) or "无"])
    lines.extend(["", "### 存在问题", "", scalar(analysis.get("issues", "无")) or "无"])
    lines.extend(["", "### 今后改进措施", "", scalar(analysis.get("improvements", "无")) or "无"])
    lines.extend(["", "### 异常情况分析", "", scalar(analysis.get("exceptions", "无")) or "无"])

    review_markers = merged_review_markers(data)
    lines.extend(["", "## 复核标记", ""])
    if review_markers:
        lines.extend([
            "| 类型 | 位置 | 当前值 | 说明 |",
            "|------|------|--------|------|",
        ])
        for marker in review_markers:
            lines.append(
                "| "
                + " | ".join(
                    [
                        scalar(marker.get("type", "需复核")),
                        scalar(marker.get("location")),
                        scalar(marker.get("value")),
                        scalar(marker.get("note")),
                    ]
                )
                + " |"
            )
    else:
        lines.append("无")
    return "\n".join(lines).rstrip() + "\n"


def split_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        raise RenderError("Markdown must start with YAML frontmatter")
    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        raise RenderError("Markdown frontmatter is not closed")
    return parse_simple_yaml(lines[1:end]), "\n".join(lines[end + 1 :]).strip() + "\n"


def parse_simple_yaml(lines: list[str]) -> dict[str, Any]:
    meta: dict[str, Any] = {}
    current_list: str | None = None
    current_map: str | None = None
    for raw in lines:
        if not raw.strip():
            continue
        if raw.startswith("  - ") and current_list:
            meta.setdefault(current_list, []).append(raw[4:].strip())
            continue
        if raw.startswith("  ") and current_map:
            key, _, value = raw.strip().partition(":")
            meta.setdefault(current_map, {})[key.strip()] = value.strip().lower() == "true"
            continue
        key, sep, value = raw.partition(":")
        if not sep:
            continue
        key = key.strip()
        value = value.strip()
        current_list = None
        current_map = None
        if value:
            meta[key] = value
        elif key == "package":
            meta[key] = {}
            current_map = key
        else:
            meta[key] = []
            current_list = key
    return meta


def section_map(body: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in body.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current:
            sections[current].append(line)
    return {key: "\n".join(value).strip() for key, value in sections.items()}


def parse_tasks(text: str) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if ". " in line:
            line = line.split(". ", 1)[1]
        name, dash, hours = line.rpartition("-")
        if not dash:
            raise RenderError(f"invalid task line: {line}")
        tasks.append({"task_name": name.strip(), "hours": hours.strip()})
    return tasks


def parse_table(text: str) -> tuple[list[str], list[dict[str, str]]]:
    rows = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    if len(rows) < 2:
        raise RenderError("missing Markdown table")
    headers = [cell.strip() for cell in rows[0].strip("|").split("|")]
    data_rows: list[dict[str, str]] = []
    for row in rows[2:]:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        cells.extend([""] * (len(headers) - len(cells)))
        data_rows.append(dict(zip(headers, cells[: len(headers)])))
    return headers, data_rows


def parse_analysis(text: str) -> dict[str, str]:
    result: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("### "):
            current = line[4:].strip()
            result[current] = []
        elif current:
            result[current].append(line)
    return {key: "\n".join(value).strip() or "无" for key, value in result.items()}


def parse_markdown(path: Path) -> MarkdownPackage:
    meta, body = split_frontmatter(read_text(path))
    sections = section_map(body)
    for required in ["我带的学生", "过程考核任务", "成绩数据", "分析", "复核标记"]:
        if required not in sections:
            raise RenderError(f"missing section: ## {required}")
    tasks = parse_tasks(sections["过程考核任务"])
    headers, rows = parse_table(sections["成绩数据"])
    return MarkdownPackage(
        meta=meta,
        students=[line.strip() for line in sections["我带的学生"].splitlines() if line.strip()],
        tasks=tasks,
        score_headers=headers,
        score_rows=rows,
        analysis=parse_analysis(sections["分析"]),
        review_text=sections["复核标记"].strip(),
    )


def validate_markdown(package: MarkdownPackage, export_ready: bool = True) -> list[str]:
    errors: list[str] = []
    for key in ["template", "date", "school_year", "semester", "major_name", "course_name", "class_name", "teachers"]:
        if package.meta.get(key) in ("", [], None):
            errors.append(f"missing required metadata: {key}")
    if package.meta.get("template") != "end-of-term-teaching-materials":
        errors.append("template must be end-of-term-teaching-materials")
    expected_task_headers = [f"任务{i}" for i in range(1, len(package.tasks) + 1)]
    expected_headers = BASE_SCORE_COLUMNS + expected_task_headers + TRAILING_SCORE_COLUMNS
    if package.score_headers != expected_headers:
        errors.append(f"score headers mismatch: expected {expected_headers}, got {package.score_headers}")
    allow_uncertain = not export_ready
    for row in package.score_rows:
        for header in package.score_headers:
            if header in BASE_SCORE_COLUMNS:
                continue
            error = validate_score_value(
                row.get(header, ""),
                allow_uncertain=allow_uncertain,
                location=f"{row.get('姓名', '<unknown>')} {header}",
            )
            if error:
                errors.append(error)
    if export_ready and package.review_text != "无":
        errors.append("## 复核标记 must be exactly 无 before final export readiness")
    return errors


def has_unresolved_review(package: MarkdownPackage) -> bool:
    if package.review_text != "无":
        return True
    return any("?" in row.get(header, "") for row in package.score_rows for header in package.score_headers[2:])


def typst_escape(value: Any) -> str:
    text = scalar(value)
    return (
        text.replace("\\", "\\\\")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("#", "\\#")
        .replace("$", "\\$")
        .replace("%", "\\%")
        .replace("&", "\\&")
    )


def typst_string(value: Any) -> str:
    return scalar(value).replace("\\", "\\\\").replace('"', '\\"')


def typst_cell(value: Any) -> str:
    return f"[{typst_escape(value)}]"


def typst_body(value: Any) -> str:
    return f"[{typst_escape(value)}]"


def pt(value: float) -> str:
    return f"{value:.2f}pt"


def ptext_abs(
    x: float,
    y: float,
    w: float,
    h: float,
    size: float,
    body: Any,
    *,
    pos: str = "center + horizon",
    weight: str = "regular",
    clip: bool = True,
) -> str:
    fn = "ptext" if clip else "ptext_nc"
    return (
        f"#{fn}({pt(x)}, {pt(y)}, {pt(w)}, {pt(h)}, {size:g}pt, "
        f"{typst_body(body)}, pos: {pos}, weight: \"{weight}\")"
    )


def ptitle_abs(
    x: float,
    y: float,
    w: float,
    h: float,
    size: float,
    body: Any,
    *,
    pos: str = "center + horizon",
) -> str:
    return f"#ptitle_nc({pt(x)}, {pt(y)}, {pt(w)}, {pt(h)}, {size:g}pt, {typst_body(body)}, pos: {pos})"


def hline_abs(x1: float, x2: float, y: float) -> str:
    return f"#hline({pt(x1)}, {pt(x2)}, {pt(y)}, s: 0.580pt)"


def hline_segment_abs(x1: float, x2: float, y: float, stroke: float = 0.58) -> str:
    return f"#hline({pt(x1)}, {pt(x2)}, {pt(y)}, s: {stroke:.3f}pt)"


def dashed_hline_abs(x1: float, x2: float, y: float, dash: float = 2.20, gap: float = 2.20, stroke: float = 0.58) -> list[str]:
    lines: list[str] = []
    x = x1
    while x < x2 - 0.01:
        lines.append(hline_segment_abs(x, min(x + dash, x2), y, stroke=stroke))
        x += dash + gap
    return lines


def vline_abs(x: float, y1: float, y2: float) -> str:
    return f"#vline({pt(x)}, {pt(y1)}, {pt(y2)}, s: 0.580pt)"


def diag_abs(x: float, y: float, length: float, deg: float) -> str:
    return f"#diag({pt(x)}, {pt(y)}, {pt(length)}, {deg:.2f}deg, s: 0.580pt)"


def warning_rect_abs(x: float, y: float, w: float, h: float) -> str:
    return f'#place(dx: {pt(x)}, dy: {pt(y)})[#rect(width: {pt(w)}, height: {pt(h)}, fill: {WARNING_FILL}, stroke: none)]'


def pagebox_abs(lines: list[str]) -> str:
    return "#pagebox[\n" + "\n".join(lines) + "\n]"


def school_year_label(package: MarkdownPackage) -> str:
    year = scalar(package.meta.get("school_year")).replace("-", "～")
    semester = scalar(package.meta.get("semester"))
    return f"{year}学年{semester}".strip()


def normalized_class_label(value: Any, spaced: bool = False) -> str:
    value = "、".join(list_value(value))
    if not value:
        return ""
    if value.endswith("班"):
        return value
    return f"{value} 班" if spaced else f"{value}班"


def class_label(package: MarkdownPackage, spaced: bool = False) -> str:
    return normalized_class_label(package.meta.get("class_name"), spaced=spaced)


def date_label(package: MarkdownPackage, spaced: bool = False) -> str:
    value = scalar(package.meta.get("date"))
    parts = value.split("-")
    if len(parts) == 3 and all(part.isdigit() for part in parts):
        year, month, day = parts[0], str(int(parts[1])), str(int(parts[2]))
        return f"{year} 年 {month} 月 {day} 日" if spaced else f"{year}年{month}月{day}日"
    return value


def teacher_label(package: MarkdownPackage, sep: str = "  ") -> str:
    return sep.join(list_value(package.meta.get("teachers")))


def course_type_label(package: MarkdownPackage) -> str:
    value = scalar(package.meta.get("course_type_label")).strip()
    if not value:
        value = "基本技能"
    if "√" in value or "□" in value:
        return value
    compact = value.replace(" ", "")
    if "一体化" in compact:
        return "一体化课√ 基本技能实训课□"
    if "基本技能" in compact or "单技能" in compact:
        return "一体化课□ 基本技能实训课√"
    return value


def wrap_cjk_label(value: Any, width: int = 4, max_lines: int = 8) -> list[str]:
    text = scalar(value).replace(" ", "")
    if not text:
        return []
    lines: list[str] = []
    current = ""
    for char in text:
        current += char
        if len(current) >= width:
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    return lines[:max_lines]


def task_score(row: dict[str, str], index: int) -> str:
    return row.get(f"任务{index}", "")


def process_score(row: dict[str, str], task_count: int) -> str:
    return numeric_average([row.get(f"任务{i}", "") for i in range(1, task_count + 1)])


def spaced_cover_title(title: str) -> str:
    raw = title.removesuffix("封面")
    overrides = {
        "成绩记分册": "成  绩  记  分  册",
        "成绩分析册": "成  绩  分  析  册",
        "教学日志": "教  学  日  志",
        "过程考核评价表": "过 程 考 核 评 价 表",
        "交接班记录": "交 接 班 记 录",
    }
    return overrides.get(raw, raw)


def cover_title_size(title: str) -> float:
    return 38.0


def cover_title_block(title: str, *, y: float = 202.00) -> list[str]:
    return [
        ptitle_abs(
            0.00,
            y,
            595.30,
            70.00,
            cover_title_size(title),
            spaced_cover_title(title),
        )
    ]


def cover_line_field(
    lines: list[str],
    y: float,
    label: str,
    value: Any,
    *,
    label_x: float = 158.00,
    label_w: float = 60.00,
    value_x: float = 218.00,
    value_w: float = 228.00,
    size: float = 16.2,
    label_text: str | None = None,
    line_offset: float = 27.00,
) -> None:
    line_y = y + line_offset
    lines.append(ptext_abs(label_x, y, label_w, 22.00, size, label_text or f"{label}：", pos="right + horizon", clip=False))
    lines.append(ptext_abs(value_x, y, value_w, 22.00, size, value, clip=False))
    lines.append(hline_abs(value_x, value_x + value_w, line_y))


def reference_cover_page(package: MarkdownPackage, title: str, *, fields: list[tuple[str, Any]] | None = None) -> str:
    lines = cover_title_block(title)
    cover_fields = fields or [
        ("科目", package.meta.get("course_name", "")),
        ("班级", class_label(package)),
        ("教师", teacher_label(package)),
    ]
    y = 522.00
    for label, value in cover_fields:
        cover_line_field(lines, y, label, value)
        y += 34.00
    return pagebox_abs(lines)


def cover_center_line(lines: list[str], y: float, value: Any, *, size: float = 16.2, underline: bool = False) -> None:
    x = 178.00
    w = 238.00
    lines.append(ptext_abs(x, y, w, 22.00, size, value, clip=False))
    if underline:
        lines.append(hline_abs(x, x + w, y + 27.00))


def scorebook_cover_page(package: MarkdownPackage) -> str:
    lines = cover_title_block("成绩记分册")
    cover_center_line(lines, 500.00, school_year_label(package), size=16.6)
    cover_center_line(lines, 542.00, class_label(package), size=16.6)
    cover_line_field(
        lines,
        584.00,
        "学科",
        package.meta.get("course_name", ""),
        label_x=126.00,
        label_w=92.00,
        value_x=218.00,
        value_w=228.00,
        label_text="学　　科：",
        line_offset=22.00,
    )
    cover_line_field(
        lines,
        626.00,
        "授课教师",
        teacher_label(package),
        label_x=126.00,
        label_w=92.00,
        value_x=218.00,
        value_w=228.00,
        line_offset=22.00,
    )
    cover_center_line(lines, 668.00, date_label(package, spaced=True), size=16.6)
    return pagebox_abs(lines)


def meta_rows(package: MarkdownPackage, extra: dict[str, Any] | None = None) -> str:
    fields: list[tuple[str, Any]] = [
        ("专业", package.meta.get("major_name", "")),
        ("课程", package.meta.get("course_name", "")),
        ("班级", "、".join(list_value(package.meta.get("class_name")))),
        ("任课教师", "、".join(list_value(package.meta.get("teachers")))),
        ("学年学期", f"{package.meta.get('school_year', '')} {package.meta.get('semester', '')}".strip()),
        ("日期", package.meta.get("date", "")),
    ]
    if extra:
        fields.extend(extra.items())
    return "\n".join(f'#meta-line("{typst_string(label)}", "{typst_string(value)}")' for label, value in fields)


def table_block(headers: list[str], rows: list[list[str]]) -> str:
    cells = [typst_cell(header) for header in headers]
    for row in rows:
        cells.extend(typst_cell(value) for value in row)
    joined = ",\n  ".join(cells)
    return f"#table(columns: {len(headers)}, inset: 3.5pt, stroke: 0.45pt,\n  {joined},\n)"


def typst_mm(value: float) -> str:
    return f"{value:.2f}mm"


def typst_table_cell(
    content: str,
    *,
    colspan: int = 1,
    rowspan: int = 1,
    align: str = "center + horizon",
    inset: str = "2pt",
    raw: bool = False,
    fill: str | None = None,
) -> str:
    args = []
    if colspan != 1:
        args.append(f"colspan: {colspan}")
    if rowspan != 1:
        args.append(f"rowspan: {rowspan}")
    args.append(f"align: {align}")
    args.append(f"inset: {inset}")
    if fill:
        args.append(f"fill: {fill}")
    body = content if raw else typst_escape(content)
    return f"table.cell({', '.join(args)})[{body}]"


def typst_table(columns: list[float], rows: list[float], cells: list[str]) -> str:
    col_spec = "(" + ", ".join(typst_mm(value) for value in columns) + ")"
    row_spec = "(" + ", ".join(typst_mm(value) for value in rows) + ")"
    return (
        f"#table(columns: {col_spec}, rows: {row_spec}, stroke: 0.45pt, inset: 2pt,\n  "
        + ",\n  ".join(cells)
        + ",\n)"
    )


def excel_scaled_widths(raw_widths: list[float], target_mm: float = 166.0) -> list[float]:
    total = sum(raw_widths)
    return [target_mm * value / total for value in raw_widths]


def score_value(row: dict[str, str], header: str) -> str:
    return row.get(header, "")


def numeric_average(values: list[str]) -> str:
    nums: list[float] = []
    for value in values:
        try:
            if value != "":
                nums.append(float(value))
        except ValueError:
            pass
    if not nums:
        return ""
    return str(round(sum(nums) / len(nums)))


def semester_score(process_score_value: str, final_exam_value: str) -> str:
    if not process_score_value and not final_exam_value:
        return ""
    try:
        return str(round((float(process_score_value or 0) * 0.4) + (float(final_exam_value or 0) * 0.6)))
    except ValueError:
        return ""


def derived_score_values(row: dict[str, str], task_count: int) -> dict[str, str]:
    process = process_score(row, task_count)
    final = row.get("期末", "")
    return {
        "平时分": process,
        "学期成绩": semester_score(process, final),
    }


def final_score(row: dict[str, str], task_count: int | None = None) -> str:
    if task_count is None:
        task_count = sum(1 for key in row if key.startswith("任务"))
    return derived_score_values(row, task_count)["学期成绩"]


def calculated_score_rows(package: MarkdownPackage) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    task_count = len(package.tasks)
    for row in package.score_rows:
        item = {header: row.get(header, "") for header in package.score_headers}
        item.update(derived_score_values(row, task_count))
        rows.append(item)
    return rows


def is_below_60(value: Any) -> bool:
    number = score_number(value)
    return number is not None and number < 60


def highlight_records(package: MarkdownPackage) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for row_index, row in enumerate(package.score_rows, start=1):
        student = row.get("姓名", "")
        student_id = row.get("学号", "")
        for header in package.score_headers[2:]:
            value = row.get(header, "")
            if "?" in value:
                records.append(
                    {
                        "kind": "unresolved_uncertain_score",
                        "student_id": student_id,
                        "student": student,
                        "field": header,
                        "value": value,
                        "markdown_location": f"成绩数据 / {student} / {header}",
                        "workbook_sheet": "成绩数据",
                        "workbook_cell": f"{column_name(package.score_headers.index(header) + 1)}{row_index + 1}",
                        "pdf_visible": "scorebook and score-summary cells use red warning fill in abnormal preview",
                    }
                )
        semester_score = final_score(row, len(package.tasks))
        if is_below_60(semester_score):
            records.append(
                {
                    "kind": "below_60_semester_score",
                    "student_id": student_id,
                    "student": student,
                    "field": "学期成绩",
                    "value": semester_score,
                    "markdown_location": f"成绩数据 / {student} / derived 学期成绩",
                    "workbook_sheet": "成绩数据",
                    "workbook_cell": f"{column_name(len(package.score_headers) + 2)}{row_index + 1}",
                    "pdf_visible": "scorebook and score-summary 学期成绩 cells use red warning fill",
                }
            )
    return records


def excel_cover_page(package: MarkdownPackage) -> str:
    return scorebook_cover_page(package)


def scorebook_body_page(package: MarkdownPackage) -> str:
    full_capacity = scorebook_row_capacity(769.17)
    stats_capacity = scorebook_row_capacity(662.06)
    rows = package.score_rows
    pages: list[str] = []
    while len(rows) > stats_capacity:
        pages.append(scorebook_score_page(package, rows[:full_capacity], bottom_y=769.17, include_stats=False))
        rows = rows[full_capacity:]
        if not rows:
            break
    pages.append(scorebook_score_page(package, rows, bottom_y=662.06, include_stats=True))
    return "\n#pagebreak()\n".join(pages)


def scorebook_row_lines(bottom_y: float) -> list[float]:
    row_lines = [72.26, 133.30]
    y = 155.52
    while y < bottom_y - 0.1:
        row_lines.append(round(y, 2))
        y += 21.98 if y != 133.30 else 22.22
    if bottom_y - row_lines[-1] <= 1.5:
        row_lines[-1] = bottom_y
    elif row_lines[-1] != bottom_y:
        row_lines.append(bottom_y)
    return row_lines


def scorebook_row_capacity(bottom_y: float) -> int:
    return len(scorebook_row_lines(bottom_y)[1:-1])


def scorebook_score_page(package: MarkdownPackage, rows: list[dict[str, str]], *, bottom_y: float, include_stats: bool) -> str:
    lines: list[str] = []
    for x in [52.88, 179.25, 371.59, 414.65, 457.71, 500.76, 541.95]:
        lines.append(vline_abs(x, 72.26, bottom_y))
    lines.append(vline_abs(115.13, 133.30, bottom_y))
    for x in [203.11, 227.45, 251.32, 275.65, 299.52, 323.39, 347.73]:
        lines.append(vline_abs(x, 107.58, bottom_y))
    row_lines = scorebook_row_lines(bottom_y)
    for y_value in row_lines:
        lines.append(hline_abs(52.88, 541.95, y_value))
    lines.append(hline_abs(179.25, 371.59, 107.58))
    for x in [203.11, 227.45, 251.32, 275.65, 299.52, 323.39, 347.73]:
        lines.append(vline_abs(x, 107.58, 133.30))
    lines.extend(
        [
            diag_abs(52.88, 72.26, 87.18, 44.44),
            diag_abs(52.88, 72.26, 140.34, 25.78),
            diag_abs(138.53, 72.26, 73.38, 56.29),
            ptext_abs(62.70, 115.80, 45.00, 17.00, 10.2, "学   号", clip=False),
            ptext_abs(111.00, 115.80, 43.00, 17.00, 10.2, "姓 名", clip=False),
            ptext_abs(111.00, 86.20, 43.00, 17.00, 10.2, "分 数", clip=False),
            ptext_abs(157.00, 77.50, 20.00, 12.00, 10.2, "种", clip=False),
            ptext_abs(157.00, 90.00, 20.00, 12.00, 10.2, "类", clip=False),
            ptext_abs(179.25, 72.26, 192.35, 35.32, 10.2, "作 业 测 试 成 绩", clip=False),
        ]
    )
    task_x = [179.25, 203.11, 227.45, 251.32, 275.65, 299.52, 323.39, 347.73]
    task_w = [23.87, 24.34, 23.87, 24.34, 23.87, 23.87, 24.34, 23.87]
    for i, (x, w) in enumerate(zip(task_x, task_w), start=1):
        lines.append(ptext_abs(x, 110.38, w, 20.11, 11, str(i)))
    for x, label in [(371.59, "平时"), (414.65, "期末"), (457.71, "学期")]:
        lines.append(ptext_abs(x, 91.00, 43.06, 12.00, 10.6, label, clip=False))
        lines.append(ptext_abs(x, 105.00, 43.06, 12.00, 10.6, "成绩", clip=False))
    lines.append(ptext_abs(500.76, 93.50, 41.18, 18.00, 11, "备注"))

    row_tops = row_lines[1:-1]
    task_count = len(package.tasks)
    for idx, top in enumerate(row_tops):
        row = rows[idx] if idx < len(rows) else {}
        y_text = top + 0.94
        h = max(12.0, row_lines[idx + 2] - top - 1.87)
        lines.append(ptext_abs(52.88, y_text, 62.24, h, 10.6, row.get("学号", "")))
        lines.append(ptext_abs(115.13, y_text, 64.12, h, 10.6, row.get("姓名", "")))
        for task_index, (x, w) in enumerate(zip(task_x, task_w), start=1):
            value = task_score(row, task_index)
            if "?" in value:
                lines.append(warning_rect_abs(x, y_text, w, h))
            lines.append(ptext_abs(x, y_text, w, h, 11.8, value))
        derived = derived_score_values(row, task_count)
        lines.append(ptext_abs(371.59, y_text, 43.06, h, 11.8, derived["平时分"]))
        final_exam = row.get("期末", "")
        if "?" in final_exam:
            lines.append(warning_rect_abs(414.65, y_text, 43.06, h))
        lines.append(ptext_abs(414.65, y_text, 43.06, h, 11.8, final_exam))
        semester_score = derived["学期成绩"]
        if is_below_60(semester_score):
            lines.append(warning_rect_abs(457.71, y_text, 43.06, h))
        lines.append(ptext_abs(457.71, y_text, 43.06, h, 11.8, semester_score))
    if include_stats:
        lines.extend(scorebook_stats_block(package))
    return pagebox_abs(lines)


def scorebook_stats_block(package: MarkdownPackage) -> list[str]:
    lines: list[str] = []
    xs = [52.88 + 54.34 * i for i in range(10)]
    for x in xs:
        lines.append(vline_abs(x, 697.84, 733.39))
    for y in [697.84, 715.15, 733.39]:
        lines.append(hline_abs(52.88, 541.95, y))
    lines.append("#hline(52.70pt, 542.15pt, 697.84pt, s: 0.760pt)")
    labels = ["分 数", "90 分以上", "80 分以上", "70 分以上", "60 分以上", "50 分以上", "40 分以上", "30 分以上", "不满 30 分"]
    values = score_distribution(package)
    for i, label in enumerate(labels):
        lines.append(ptext_abs(xs[i], 697.84, 54.34, 17.31, 10.8, label))
    lines.append(ptext_abs(xs[0], 715.15, 54.34, 18.24, 10.8, "人 数"))
    for i, value in enumerate(values, start=1):
        lines.append(ptext_abs(xs[i], 715.15, 54.34, 18.24, 10.8, value))
    lines.append(ptext_abs(0.00, 672.00, 595.30, 24.00, 16.8, "学 期 成 绩 统 计 表", weight="bold"))
    lines.append(ptext_abs(52.88, 748.36, 150.00, 14.97, 10.8, f"及格率：  {pass_rate(package)}", pos="left + horizon", clip=False))
    lines.append(ptext_abs(215.90, 748.36, 150.00, 14.97, 10.8, "任课教师：", pos="left + horizon", clip=False))
    lines.append(ptext_abs(378.93, 748.36, 150.00, 14.97, 10.8, "教研室主任：", pos="left + horizon", clip=False))
    return lines


def score_summary_page(package: MarkdownPackage) -> str:
    lines: list[str] = [
        ptext_abs(0.00, 89.50, 595.30, 21.04, 16.8, "工学一体化课程/基本技能课程考核成绩汇总表", weight="bold"),
        ptext_abs(55.69, 123.80, 160.68, 21.00, 11.6, f"专业：  {package.meta.get('major_name', '')}", clip=False),
        ptext_abs(216.37, 123.80, 160.68, 21.00, 11.6, f"班级：  {class_label(package, spaced=True)}", clip=False),
        ptext_abs(377.05, 123.80, 160.68, 21.00, 11.6, date_label(package, spaced=True), clip=False),
    ]
    for y in [142.19, 160.90, 326.00, 346.02, 366.04, 386.06, 406.08, 426.09, 446.11, 466.13, 486.15, 506.17, 526.19, 546.21, 566.22, 586.24, 606.26, 626.28, 646.30, 666.32, 686.34, 706.35, 726.37]:
        lines.append(hline_abs(55.69, 537.74, y))
    lines.append(hline_abs(140.40, 501.23, 305.89))
    for x in [55.69, 140.40, 276.12, 366.45, 537.74]:
        lines.append(vline_abs(x, 142.19, 160.90))
    for x in [55.69, 140.40, 185.80, 230.73, 276.12, 321.05, 366.45, 411.37, 456.30, 501.23, 537.74]:
        lines.append(vline_abs(x, 160.90, 326.00))
    for x in [55.69, 83.30, 140.40, 185.80, 230.73, 276.12, 321.05, 366.45, 411.37, 456.30, 501.23, 537.74]:
        lines.append(vline_abs(x, 326.00, 726.84))
    lines.extend(
        [
            diag_abs(55.69, 160.90, 172.40, 73.28),
            diag_abs(55.69, 160.90, 111.47, 40.54),
            ptext_abs(55.69, 142.19, 84.71, 18.71, 11.8, "课程名称"),
            ptext_abs(140.40, 142.19, 135.72, 18.71, 10.2, package.meta.get("course_name", "")),
            ptext_abs(276.12, 142.19, 90.32, 18.71, 11.8, "课程类型"),
            ptext_abs(366.45, 142.19, 171.29, 18.71, 11.8, course_type_label(package)),
            ptext_abs(90.00, 164.00, 49.00, 12.00, 10.5, "任务名称", pos="right + horizon", clip=False),
            ptext_abs(90.00, 178.00, 49.00, 12.00, 10.5, "考核权重", pos="right + horizon", clip=False),
            ptext_abs(55.00, 286.00, 42.00, 12.00, 10.5, "学生", clip=False),
            ptext_abs(55.00, 300.00, 42.00, 12.00, 10.5, "姓名", clip=False),
            ptext_abs(101.00, 264.00, 36.00, 12.00, 10.5, "考核", clip=False),
            ptext_abs(101.00, 278.00, 36.00, 12.00, 10.5, "成绩", clip=False),
            ptext_abs(501.23, 232.00, 36.50, 12.00, 10.5, "总评", clip=False),
            ptext_abs(501.23, 246.00, 36.50, 12.00, 10.5, "成绩", clip=False),
        ]
    )
    task_cols = [(140.40, 45.40), (185.80, 44.93), (230.73, 45.40), (276.12, 44.93), (321.05, 45.40)]
    weights = task_weights(package)
    for index, (x, w) in enumerate(task_cols, start=1):
        task = package.tasks[index - 1] if index <= len(package.tasks) else {"task_name": ""}
        task_lines = wrap_cjk_label(task.get("task_name", ""), width=4, max_lines=8)
        start_y = 192.00 if len(task_lines) <= 6 else 178.00
        for line_index, label in enumerate(task_lines):
            lines.append(ptext_abs(x, start_y + 14.00 * line_index, w, 13.00, 10.0 if len(task_lines) > 6 else 10.2, label, clip=False))
        lines.append(ptext_abs(x, 305.89, w, 20.11, 10.8, weights[index - 1] if index - 1 < len(weights) else ""))
    for index in range(20):
        row = package.score_rows[index] if index < len(package.score_rows) else {}
        top = 326.00 + 20.02 * index
        lines.append(ptext_abs(55.69, top, 27.61, 20.02, 10.8, str(index + 1) if row else ""))
        lines.append(ptext_abs(83.30, top, 57.10, 20.02, 10.8, row.get("姓名", "")))
        for task_index, (x, w) in enumerate(task_cols, start=1):
            value = task_score(row, task_index)
            if "?" in value:
                lines.append(warning_rect_abs(x, top, w, 20.02))
            lines.append(ptext_abs(x, top, w, 20.02, 10.8, value))
        semester_score = final_score(row, len(package.tasks))
        if is_below_60(semester_score):
            lines.append(warning_rect_abs(501.23, top, 36.50, 20.02))
        lines.append(ptext_abs(501.23, top, 36.50, 20.02, 10.8, semester_score))
    lines.append(ptext_abs(74.00, 758.00, 150.00, 14.00, 11.6, "教研室主任签字：", pos="left + horizon", clip=False))
    lines.append(ptext_abs(392.00, 758.00, 120.00, 14.00, 11.6, "教师签字：", pos="left + horizon", clip=False))
    return pagebox_abs(lines)


def analysis_page(package: MarkdownPackage) -> str:
    lines: list[str] = [
        ptext_abs(0.00, 102.00, 595.30, 25.00, 20.0, "成  绩  分  析  表"),
        ptext_abs(55.69, 142.66, 170.00, 16.84, 11.8, school_year_label(package), pos="left + horizon", clip=False),
        ptext_abs(250.00, 142.66, 120.00, 16.84, 11.8, f"班级：  {class_label(package, spaced=True)}", clip=False),
        ptext_abs(390.00, 142.66, 170.00, 16.84, 11.8, f"时间：  {date_label(package, spaced=True)}", clip=False),
    ]
    for y in [167.44, 192.70, 217.49, 242.75, 292.79, 317.58, 407.85, 498.12, 587.93, 678.20, 758.18]:
        lines.append(hline_abs(55.69, 537.74, y))
    for y in [267.77]:
        lines.append(hline_abs(448.35, 537.74, y))
    for x, y1, y2 in [
        (55.69, 167.44, 192.70), (153.97, 167.44, 192.70), (399.21, 167.44, 192.70),
        (448.35, 167.44, 192.70), (537.74, 167.44, 192.70),
        (55.69, 192.70, 217.49), (104.83, 192.70, 217.49), (153.97, 192.70, 217.49),
        (448.35, 192.70, 217.49), (537.74, 192.70, 217.49),
        (55.69, 217.49, 292.79), (104.83, 217.49, 292.79), (153.97, 217.49, 292.79),
        (203.11, 217.49, 292.79), (251.79, 217.49, 292.79), (300.93, 217.49, 292.79),
        (350.07, 217.49, 292.79), (399.21, 217.49, 292.79), (448.35, 217.49, 292.79),
        (537.74, 217.49, 292.79),
        (55.69, 292.79, 317.58), (537.74, 292.79, 317.58),
        (55.69, 317.58, 407.85), (104.83, 317.58, 407.85), (537.74, 317.58, 407.85),
        (55.69, 407.85, 498.12), (104.83, 407.85, 498.12), (537.74, 407.85, 498.12),
        (55.69, 498.12, 587.93), (104.83, 498.12, 587.93), (537.74, 498.12, 587.93),
        (55.69, 587.93, 678.20), (104.83, 587.93, 678.20), (537.74, 587.93, 678.20),
        (55.69, 678.20, 758.18), (300.93, 678.20, 758.18), (537.74, 678.20, 758.18),
    ]:
        lines.append(vline_abs(x, y1, y2))
    lines.extend(
        [
            ptext_abs(55.69, 167.44, 98.28, 25.26, 11.8, "课程名称"),
            ptext_abs(153.97, 167.44, 245.24, 25.26, 11.8, package.meta.get("course_name", "")),
            ptext_abs(399.21, 167.44, 49.14, 25.26, 11.8, "教师姓名"),
            ptext_abs(448.35, 167.44, 89.39, 25.26, 11.8, teacher_label(package, sep="  ")),
            ptext_abs(55.69, 192.70, 49.14, 24.79, 11.8, "全班人数"),
            ptext_abs(104.83, 192.70, 49.14, 24.79, 11.8, "缺考人数"),
            ptext_abs(153.97, 192.70, 294.38, 24.79, 11.8, "考试成绩、分类、人数及百分比"),
            ptext_abs(448.35, 192.70, 89.39, 24.79, 11.8, "最高分"),
            ptext_abs(153.97, 217.49, 49.14, 25.26, 11.6, "不及格"),
            ptext_abs(203.11, 217.49, 48.67, 25.26, 11.6, "及格"),
            ptext_abs(251.79, 217.49, 49.14, 25.26, 9.8, "80分以上", clip=False),
            ptext_abs(300.93, 217.49, 49.14, 25.26, 9.8, "90分以上", clip=False),
            ptext_abs(350.07, 217.49, 49.14, 25.26, 11.6, "平均成绩"),
            ptext_abs(399.21, 217.49, 49.14, 25.26, 11.6, "及格率"),
            ptext_abs(448.35, 217.49, 89.39, 25.26, 11.8, summary_stat(package, "max")),
            ptext_abs(55.69, 242.75, 49.14, 50.05, 10.8, str(len(package.score_rows))),
            ptext_abs(104.83, 242.75, 49.14, 50.05, 10.8, "0"),
            ptext_abs(153.97, 242.75, 49.14, 50.05, 10.8, summary_stat(package, "lt60")),
            ptext_abs(203.11, 242.75, 48.67, 50.05, 10.8, summary_stat(package, "gte60")),
            ptext_abs(251.79, 242.75, 49.14, 50.05, 10.8, summary_stat(package, "gte80lt90")),
            ptext_abs(300.93, 242.75, 49.14, 50.05, 10.8, summary_stat(package, "gte90")),
            ptext_abs(350.07, 242.75, 49.14, 50.05, 10.8, summary_stat(package, "avg")),
            ptext_abs(399.21, 242.75, 49.14, 50.05, 10.8, summary_stat(package, "pass_rate")),
            ptext_abs(448.35, 242.75, 89.39, 24.79, 11.8, "最低分"),
            ptext_abs(448.35, 267.77, 89.39, 24.79, 11.8, summary_stat(package, "min")),
            ptext_abs(55.69, 292.79, 482.04, 24.79, 11.8, "从学生掌握基本理论、基本概念、基本技能和重点难关等方面进行分析"),
        ]
    )
    analysis_rows = [
        ("试卷分析", package.analysis.get("试卷分析", "无"), 317.58, 407.85, 1),
        ("存在问题", package.analysis.get("存在问题", "无"), 407.85, 498.12, 1),
        ("今后改进\n措施", package.analysis.get("今后改进措施", "无"), 498.12, 587.93, 2),
        ("异常情况\n分析", package.analysis.get("异常情况分析", "无"), 587.93, 678.20, 2),
    ]
    for label, text, top, bottom, label_lines in analysis_rows:
        label_parts = label.split("\n")
        label_y = (top + bottom) / 2 - (14.0 * len(label_parts)) / 2
        for i, part in enumerate(label_parts):
            lines.append(ptext_abs(55.69, label_y + 14.0 * i, 49.14, 14.00, 11.6, part))
        if scalar(text) == "无":
            lines.append(ptext_abs(104.83, top, 432.90, bottom - top, 11.6, "无"))
        else:
            wrapped = wrap_analysis_text(text, max_chars=35, max_lines=4)
            body_y = (top + bottom) / 2 - 7.0 * len(wrapped)
            for i, part in enumerate(wrapped):
                prefix = "　　" if i == 0 else ""
                lines.append(ptext_abs(112.00, body_y + 14.0 * i, 420.00, 14.00, 11.2, prefix + part, pos="left + horizon", clip=False))
    lines.append(ptext_abs(55.69, 685.20, 245.23, 24.00, 11.6, "教研室意见", pos="left + top", clip=False))
    lines.append(ptext_abs(300.93, 685.20, 236.81, 24.00, 11.6, "系部意见", pos="left + top", clip=False))
    return pagebox_abs(lines)


def simple_cover_page(package: MarkdownPackage, title: str) -> str:
    if title == "交接班记录封面":
        lines = cover_title_block(title)
        left_x = 154.00
        right_x = 312.00
        block_w = 126.00
        top_y = 590.00
        bottom_y = 624.00
        lines.append(ptext_abs(left_x, top_y, block_w, 24.00, 16.0, class_label(package), clip=False))
        lines.append(ptext_abs(right_x, top_y, block_w, 24.00, 16.0, teacher_label(package), clip=False))
        lines.extend(dashed_hline_abs(150.00, 444.00, 621.00, dash=2.00, gap=2.00, stroke=0.58))
        lines.append(ptext_abs(left_x, bottom_y, block_w, 24.00, 16.0, normalized_class_label(package.meta.get("handover_class_name")), clip=False))
        lines.append(ptext_abs(right_x, bottom_y, block_w, 24.00, 16.0, "  ".join(list_value(package.meta.get("handover_teachers"))), clip=False))
        return pagebox_abs(lines)
    return reference_cover_page(package, title)


def summary_scores(package: MarkdownPackage) -> list[float]:
    values: list[float] = []
    for row in package.score_rows:
        score = final_score(row, len(package.tasks))
        try:
            if score != "":
                values.append(float(score))
        except ValueError:
            pass
    return values


def summary_stat(package: MarkdownPackage, kind: str) -> str:
    scores = summary_scores(package)
    if not scores:
        return ""
    if kind == "max":
        return str(round(max(scores)))
    if kind == "min":
        return str(round(min(scores)))
    if kind == "avg":
        return f"{sum(scores) / len(scores):.2f}"
    if kind == "lt60":
        return str(sum(1 for score in scores if score < 60))
    if kind == "gte60":
        return str(sum(1 for score in scores if score >= 60))
    if kind == "gte80lt90":
        return str(sum(1 for score in scores if 80 <= score < 90))
    if kind == "gte90":
        return str(sum(1 for score in scores if score >= 90))
    if kind == "pass_rate":
        return f"{sum(1 for score in scores if score >= 60) / len(scores) * 100:.2f}%"
    return ""


def pass_rate(package: MarkdownPackage) -> str:
    return summary_stat(package, "pass_rate") or ""


def score_distribution(package: MarkdownPackage) -> list[str]:
    scores = summary_scores(package)
    bins = [
        sum(1 for score in scores if score >= 90),
        sum(1 for score in scores if 80 <= score < 90),
        sum(1 for score in scores if 70 <= score < 80),
        sum(1 for score in scores if 60 <= score < 70),
        sum(1 for score in scores if 50 <= score < 60),
        sum(1 for score in scores if 40 <= score < 50),
        sum(1 for score in scores if 30 <= score < 40),
        sum(1 for score in scores if score < 30),
    ]
    return [str(value) for value in bins]


def task_weights(package: MarkdownPackage) -> list[str]:
    hours: list[float] = []
    for task in package.tasks:
        try:
            hours.append(float(task.get("hours", 0)))
        except (TypeError, ValueError):
            hours.append(0.0)
    total = sum(hours)
    if total <= 0:
        return [scalar(task.get("hours", "")) for task in package.tasks]
    return [f"{round(value / total * 100):g}%" if value else "" for value in hours]


def wrap_analysis_text(value: Any, max_chars: int, max_lines: int) -> list[str]:
    text = scalar(value).replace("\n", " ").strip()
    if not text:
        return ["无"]
    lines: list[str] = []
    current = ""
    for char in text:
        current += char
        if len(current) >= max_chars:
            lines.append(current)
            current = ""
            if len(lines) >= max_lines:
                break
    if current and len(lines) < max_lines:
        lines.append(current)
    return lines or ["无"]


def enabled_packages(package: MarkdownPackage) -> tuple[dict[str, bool], list[str]]:
    flags = package_flags(package.meta)
    warnings: list[str] = []
    handover_ready = bool(package.meta.get("handover_class_name")) and bool(package.meta.get("handover_teachers"))
    if flags["交接班记录封面"] and not handover_ready:
        flags["交接班记录封面"] = False
        warnings.append("交接班记录封面 skipped: handover_class_name and handover_teachers are required")
    return flags, warnings


def generate_typst(package: MarkdownPackage, template_path: Path) -> tuple[str, list[str], dict[str, bool]]:
    flags, warnings = enabled_packages(package)
    body: list[str] = []
    if flags["成绩记分册"]:
        body.append(excel_cover_page(package))
        body.append(scorebook_body_page(package))
    if flags["成绩汇总表"]:
        body.append(score_summary_page(package))
    if flags["成绩分析表"]:
        body.append(analysis_page(package))
    if flags["教学日志封面"]:
        body.append(simple_cover_page(package, "教学日志封面"))
    if flags["过程考核评价表封面"]:
        body.append(simple_cover_page(package, "过程考核评价表封面"))
    if flags["交接班记录封面"]:
        body.append(simple_cover_page(package, "交接班记录封面"))
    template = read_text(template_path)
    document_title = f"{package.meta.get('course_name', '')} 期末教学材料包"
    document_author = "、".join(list_value(package.meta.get("teachers")))
    return (
        template.replace("{{DOCUMENT_TITLE}}", typst_string(document_title))
        .replace("{{DOCUMENT_AUTHOR}}", typst_string(document_author))
        .replace("{{PACKAGE_BODY}}", "\n#pagebreak()\n".join(body).strip() + "\n"),
        warnings,
        flags,
    )


def score_summary_rows(package: MarkdownPackage) -> list[list[str]]:
    blank_cells = 0
    numeric_values: list[float] = []
    for row in package.score_rows:
        for header in package.score_headers[2:]:
            value = row.get(header, "")
            if value == "":
                blank_cells += 1
            else:
                try:
                    numeric_values.append(float(value))
                except ValueError:
                    pass
    average = "" if not numeric_values else f"{sum(numeric_values) / len(numeric_values):.2f}"
    return [
        ["学生数", str(len(package.score_rows))],
        ["过程考核任务数", str(len(package.tasks))],
        ["空白成绩单元格数", str(blank_cells)],
        ["已填成绩均值", average],
        ["计算说明", "PDF、workbook 和 calculated-score-data.json 使用同一套派生成绩结果"],
    ]


def build_table_artifacts(package: MarkdownPackage) -> dict[str, Any]:
    task_headers = [f"任务{i}" for i in range(1, len(package.tasks) + 1)]
    task_map = [
        {"column": f"任务{i}", "task_name": task["task_name"], "hours": scalar(task["hours"])}
        for i, task in enumerate(package.tasks, start=1)
    ]
    score_data = []
    for row in package.score_rows:
        item = {header: row.get(header, "") for header in package.score_headers}
        score_data.append(item)
    calculated_score_data = calculated_score_rows(package)
    return {
        "score_data": score_data,
        "calculated_score_data": calculated_score_data,
        "task_map": task_map,
        "highlight_evidence": highlight_records(package),
        "score_summary": {
            "student_count": len(package.score_rows),
            "task_count": len(task_headers),
            "blank_score_cells": sum(1 for row in package.score_rows for header in package.score_headers[2:] if row.get(header, "") == ""),
            "summary_rows": score_summary_rows(package),
        },
    }


def write_csv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({header: row.get(header, "") for header in headers})


def column_name(index: int) -> str:
    name = ""
    while index:
        index, rem = divmod(index - 1, 26)
        name = chr(65 + rem) + name
    return name


def worksheet_xml(rows: list[list[Any]], highlighted_cells: set[tuple[int, int]] | None = None) -> str:
    highlighted_cells = highlighted_cells or set()
    body = []
    for r_index, row in enumerate(rows, start=1):
        cells = []
        for c_index, value in enumerate(row, start=1):
            ref = f"{column_name(c_index)}{r_index}"
            text = xml_escape(scalar(value))
            style = ' s="1"' if (r_index, c_index) in highlighted_cells else ""
            cells.append(f'<c r="{ref}"{style} t="inlineStr"><is><t>{text}</t></is></c>')
        body.append(f'<row r="{r_index}">{"".join(cells)}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(body)}</sheetData></worksheet>'
    )


def write_xlsx(path: Path, package: MarkdownPackage, artifacts: dict[str, Any]) -> None:
    score_headers = package.score_headers + DERIVED_SCORE_COLUMNS + ["备注"]
    score_rows = [score_headers]
    highlighted_cells: set[tuple[int, int]] = set()
    for row_index, row in enumerate(package.score_rows, start=2):
        calculated = artifacts["calculated_score_data"][row_index - 2]
        values = [calculated.get(header, "") for header in package.score_headers + DERIVED_SCORE_COLUMNS]
        values.append("")
        score_rows.append(values)
        for col_index, header in enumerate(package.score_headers, start=1):
            if "?" in row.get(header, ""):
                highlighted_cells.add((row_index, col_index))
        semester_score_col = len(package.score_headers) + 2
        if is_below_60(calculated.get("学期成绩", "")):
            highlighted_cells.add((row_index, semester_score_col))
    task_rows = [["任务列", "任务名称", "课时"]]
    task_rows.extend([[item["column"], item["task_name"], item["hours"]] for item in artifacts["task_map"]])
    summary_rows = [["项目", "值"]]
    summary_rows.extend(artifacts["score_summary"]["summary_rows"])

    files = {
        "[Content_Types].xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '<Override PartName="/xl/worksheets/sheet3.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            "</Types>"
        ),
        "_rels/.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            "</Relationships>"
        ),
        "xl/_rels/workbook.xml.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet3.xml"/>'
            '<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
            "</Relationships>"
        ),
        "xl/styles.xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>'
            '<fill><patternFill patternType="solid"><fgColor rgb="FFFFE0E0"/><bgColor indexed="64"/></patternFill></fill></fills>'
            '<fonts count="1"><font><sz val="11"/><name val="SimSun"/></font></fonts>'
            '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
            '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
            '<cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
            '<xf numFmtId="0" fontId="0" fillId="2" borderId="0" xfId="0" applyFill="1"/></cellXfs>'
            '</styleSheet>'
        ),
        "xl/workbook.xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="成绩数据" sheetId="1" r:id="rId1"/>'
            '<sheet name="任务映射" sheetId="2" r:id="rId2"/>'
            '<sheet name="成绩汇总" sheetId="3" r:id="rId3"/></sheets></workbook>'
        ),
        "xl/worksheets/sheet1.xml": worksheet_xml(score_rows, highlighted_cells),
        "xl/worksheets/sheet2.xml": worksheet_xml(task_rows),
        "xl/worksheets/sheet3.xml": worksheet_xml(summary_rows),
    }
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo(name)
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, files[name])


def compile_pdf(typ_path: Path, pdf_path: Path) -> tuple[str, str]:
    typst = shutil.which("typst")
    if not typst:
        return "skipped", "typst CLI not found"
    result = subprocess.run([typst, "compile", str(typ_path), str(pdf_path)], text=True, capture_output=True)
    if result.returncode != 0:
        return "failed", (result.stderr or result.stdout).strip()
    return "compiled", str(pdf_path)


def render(markdown_path: Path, workdir: Path, skill_dir: Path, pdf: bool, abnormal_review: bool = False) -> dict[str, Any]:
    package = parse_markdown(markdown_path)
    errors = validate_markdown(package, export_ready=not abnormal_review)
    if errors:
        raise RenderError("; ".join(errors))
    unresolved_review = has_unresolved_review(package)
    if abnormal_review and not unresolved_review:
        raise RenderError("abnormal review rendering requires unresolved ? values or non-empty ## 复核标记")

    tables_dir = workdir / "tables"
    tables_dir.mkdir(exist_ok=True)
    md_out = workdir / "end-of-term-full.md"
    typ_out = workdir / "end-of-term-package.typ"
    pdf_out = workdir / "end-of-term-package.pdf"
    if markdown_path.resolve() != md_out.resolve():
        write_text(md_out, read_text(markdown_path))
    typst_text, warnings, flags = generate_typst(package, skill_dir / "templates/typst/end-of-term-package.typ")
    write_text(typ_out, typst_text)

    artifacts = build_table_artifacts(package)
    calculated_scores_verified = verify_calculated_scores(package, artifacts, typst_text)
    if not calculated_scores_verified:
        raise RenderError("calculated score verification failed")
    write_text(tables_dir / "score-data.json", stable_json(artifacts["score_data"]))
    write_text(tables_dir / "calculated-score-data.json", stable_json(artifacts["calculated_score_data"]))
    write_text(tables_dir / "task-map.json", stable_json(artifacts["task_map"]))
    write_text(tables_dir / "score-summary.json", stable_json(artifacts["score_summary"]))
    write_text(tables_dir / "highlight-evidence.json", stable_json(artifacts["highlight_evidence"]))
    write_csv(tables_dir / "score-data.csv", package.score_headers, artifacts["score_data"])
    write_xlsx(tables_dir / "scorebook.xlsx", package, artifacts)

    pdf_status = "not_requested"
    pdf_message = ""
    if pdf:
        pdf_status, pdf_message = compile_pdf(typ_out, pdf_out)
    manifest = {
        "skill": "end-of-term-teaching-materials",
        "version": VERSION,
        "artifact_kind": "abnormal_review" if abnormal_review else "final_package",
        "final_ready": not abnormal_review and not unresolved_review,
        "review_cleared": not unresolved_review,
        "enabled_packages": flags,
        "warnings": warnings
        + (
            ["abnormal review artifact: unresolved review items remain; do not submit as final package"]
            if abnormal_review
            else []
        ),
        "markdown": str(md_out.name),
        "typst": str(typ_out.name),
        "pdf": {"status": pdf_status, "path": pdf_out.name if pdf_out.exists() else "", "message": pdf_message},
        "highlight_evidence": artifacts["highlight_evidence"],
        "calculated_scores_verified": calculated_scores_verified,
        "table_artifacts_verified": verify_table_artifacts(package, artifacts),
        "workbook_verified": (tables_dir / "scorebook.xlsx").exists(),
        "repeatable": "not_checked",
    }
    write_text(workdir / "manifest.json", stable_json(manifest))
    return manifest


def verify_table_artifacts(package: MarkdownPackage, artifacts: dict[str, Any]) -> bool:
    task_columns = [item["column"] for item in artifacts["task_map"]]
    expected_task_columns = [f"任务{i}" for i in range(1, len(package.tasks) + 1)]
    if task_columns != expected_task_columns:
        return False
    for source, emitted in zip(package.score_rows, artifacts["score_data"]):
        for header in package.score_headers:
            if source.get(header, "") != emitted.get(header, ""):
                return False
    for source, emitted in zip(calculated_score_rows(package), artifacts["calculated_score_data"]):
        for header in package.score_headers + DERIVED_SCORE_COLUMNS:
            if source.get(header, "") != emitted.get(header, ""):
                return False
    return True


def verify_calculated_scores(package: MarkdownPackage, artifacts: dict[str, Any], typst_text: str) -> bool:
    expected = calculated_score_rows(package)
    emitted = artifacts.get("calculated_score_data") or []
    if expected != emitted:
        return False
    for row in expected:
        student_name = row.get("姓名", "")
        if student_name and typst_string(student_name) not in typst_text:
            return False
        for header in DERIVED_SCORE_COLUMNS:
            value = row.get(header, "")
            if value and typst_string(value) not in typst_text:
                return False
    return True


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repeatability_hashes(workdir: Path) -> dict[str, str]:
    paths = [
        workdir / "end-of-term-full.md",
        workdir / "end-of-term-package.typ",
        workdir / "tables/score-data.json",
        workdir / "tables/calculated-score-data.json",
        workdir / "tables/score-data.csv",
        workdir / "tables/task-map.json",
        workdir / "tables/score-summary.json",
        workdir / "tables/highlight-evidence.json",
        workdir / "tables/scorebook.xlsx",
    ]
    return {str(path.relative_to(workdir)): hash_file(path) for path in paths}


def verify(skill_dir: Path, workdir: Path) -> dict[str, Any]:
    fixture = skill_dir / "references/fixtures/end-of-term-source.json"
    uncertain_fixture = skill_dir / "references/fixtures/end-of-term-source-uncertain.json"
    source_out = workdir / "end-of-term-source.json"
    uncertain_source_out = workdir / "end-of-term-source-uncertain.json"
    markdown_out = workdir / "end-of-term-full.md"
    shutil.copyfile(fixture, source_out)
    data = load_json(source_out)
    source_errors = validate_source_data(data)
    if source_errors:
        raise RenderError("; ".join(source_errors))
    write_text(markdown_out, generate_markdown(data))
    markdown_package = parse_markdown(markdown_out)
    markdown_errors = validate_markdown(markdown_package)
    if markdown_errors:
        raise RenderError("; ".join(markdown_errors))

    shutil.copyfile(uncertain_fixture, uncertain_source_out)
    uncertain_data = load_json(uncertain_source_out)
    review_mode_errors = validate_source_data(uncertain_data, export_ready=False)
    if review_mode_errors:
        raise RenderError("; ".join(review_mode_errors))
    export_mode_errors = validate_source_data(uncertain_data, export_ready=True)
    if not export_mode_errors:
        raise RenderError("uncertain source fixture did not fail final export validation")
    uncertain_markdown = workdir / "end-of-term-full-uncertain.md"
    write_text(uncertain_markdown, generate_markdown(uncertain_data))
    uncertain_text = read_text(uncertain_markdown)
    if "87?" not in uncertain_text or "## 复核标记" not in uncertain_text or "需复核" not in uncertain_text:
        raise RenderError("uncertain source fixture did not generate reviewable Markdown markers")

    unresolved = workdir / "unresolved-review.md"
    write_text(unresolved, uncertain_text)
    try:
        render(unresolved, workdir / "_blocked", skill_dir, pdf=False)
        raise RenderError("unresolved review fixture did not block rendering")
    except FileNotFoundError:
        (workdir / "_blocked").mkdir(exist_ok=True)
        try:
            render(unresolved, workdir / "_blocked", skill_dir, pdf=False)
            raise RenderError("unresolved review fixture did not block rendering")
        except RenderError:
            pass
    except RenderError:
        pass

    abnormal_dir = workdir / "_abnormal-review"
    abnormal_dir.mkdir(exist_ok=True)
    abnormal_manifest = render(unresolved, abnormal_dir, skill_dir, pdf=True, abnormal_review=True)
    if abnormal_manifest.get("final_ready") is not False or abnormal_manifest.get("artifact_kind") != "abnormal_review":
        raise RenderError("abnormal review manifest did not record non-final status")
    highlights = abnormal_manifest.get("highlight_evidence") or []
    if not any(item.get("kind") == "unresolved_uncertain_score" for item in highlights):
        raise RenderError("abnormal review manifest missing unresolved-cell highlight evidence")
    if not any(item.get("kind") == "below_60_semester_score" for item in highlights):
        raise RenderError("abnormal review manifest missing below-60 highlight evidence")

    manifest = render(markdown_out, workdir, skill_dir, pdf=True)
    first_hashes = repeatability_hashes(workdir)
    repeat_dir = workdir / "_repeat"
    repeat_dir.mkdir(exist_ok=True)
    render(markdown_out, repeat_dir, skill_dir, pdf=False)
    second_hashes = repeatability_hashes(repeat_dir)
    repeatable = first_hashes == second_hashes
    if not repeatable:
        raise RenderError("deterministic artifact repeatability check failed")
    manifest["repeatable"] = True
    manifest["repeatability_hashes"] = first_hashes
    manifest["verification_cases"] = {
        "uncertain_markdown_generated": True,
        "normal_render_blocked_unresolved_review": True,
        "abnormal_review": abnormal_manifest,
        "final_export_validation_errors": export_mode_errors,
    }
    write_text(workdir / "manifest.json", stable_json(manifest))
    return manifest


def cmd_example(args: argparse.Namespace) -> None:
    shutil.copyfile(Path(args.skill_dir) / "references/fixtures/end-of-term-source.json", Path(args.output))


def cmd_validate(args: argparse.Namespace) -> None:
    path = Path(args.input)
    if path.suffix.lower() == ".json":
        errors = validate_source_data(load_json(path))
    else:
        errors = validate_markdown(parse_markdown(path))
    if errors:
        raise RenderError("; ".join(errors))
    print("validation: ok")


def cmd_markdown(args: argparse.Namespace) -> None:
    write_text(Path(args.output), generate_markdown(load_json(Path(args.input))))


def cmd_render(args: argparse.Namespace) -> None:
    manifest = render(Path(args.input), Path(args.workdir), Path(args.skill_dir), bool(args.pdf), bool(args.abnormal_review))
    print(stable_json(manifest), end="")


def cmd_verify(args: argparse.Namespace) -> None:
    manifest = verify(Path(args.skill_dir), Path(args.workdir))
    print(stable_json(manifest), end="")


def cmd_manifest(args: argparse.Namespace) -> None:
    print(
        stable_json(
            {
                "skill": "end-of-term-teaching-materials",
                "version": VERSION,
                "commands": ["example", "validate", "markdown", "render --abnormal-review", "verify", "manifest", "info", "version"],
                "outputs": [
                    "end-of-term-full.md",
                    "end-of-term-package.typ",
                    "end-of-term-package.pdf",
                    "manifest.json",
                    "tables/score-data.json",
                    "tables/calculated-score-data.json",
                    "tables/score-data.csv",
                    "tables/task-map.json",
                    "tables/score-summary.json",
                    "tables/highlight-evidence.json",
                    "tables/scorebook.xlsx",
                ],
            }
        ),
        end="",
    )


def cmd_info(args: argparse.Namespace) -> None:
    print("end-of-term-teaching-materials: structured data -> Markdown -> Typst/PDF + deterministic table artifacts")


def cmd_version(args: argparse.Namespace) -> None:
    print(VERSION)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ["example", "validate", "markdown", "render", "verify", "manifest", "info", "version"]:
        cmd = sub.add_parser(command)
        cmd.add_argument("--skill-dir", required=True)
    sub.choices["example"].add_argument("--output", required=True)
    sub.choices["validate"].add_argument("--input", required=True)
    sub.choices["markdown"].add_argument("--input", required=True)
    sub.choices["markdown"].add_argument("--output", required=True)
    sub.choices["render"].add_argument("--input", required=True)
    sub.choices["render"].add_argument("--workdir", required=True)
    sub.choices["render"].add_argument("--pdf", action="store_true")
    sub.choices["render"].add_argument("--abnormal-review", action="store_true")
    sub.choices["verify"].add_argument("--workdir", required=True)
    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        {
            "example": cmd_example,
            "validate": cmd_validate,
            "markdown": cmd_markdown,
            "render": cmd_render,
            "verify": cmd_verify,
            "manifest": cmd_manifest,
            "info": cmd_info,
            "version": cmd_version,
        }[args.command](args)
    except RenderError as exc:
        print(f"render_package.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
