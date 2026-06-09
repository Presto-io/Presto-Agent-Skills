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

VERSION = "0.2.0"
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


def list_value(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [scalar(item) for item in value]
    return [scalar(value)]


def package_flags(meta: dict[str, Any]) -> dict[str, bool]:
    raw = meta.get("package") or {}
    return {name: bool(raw.get(name, True)) for name in PACKAGE_ARTIFACTS}


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
        for value in list(row_tasks.values()) + [row.get("attendance"), row.get("homework"), row.get("final")]:
            if isinstance(value, str) and "?" in value:
                errors.append("uncertain score values must be reviewed before export")
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

    review_markers = data.get("review_markers") or []
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
    for row in package.score_rows:
        for header in package.score_headers:
            if "?" in row.get(header, ""):
                errors.append("uncertain score values must be reviewed before export")
    if export_ready and package.review_text != "无":
        errors.append("## 复核标记 must be exactly 无 before final export readiness")
    return errors


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


def final_score(row: dict[str, str]) -> str:
    task_values = [value for key, value in row.items() if key.startswith("任务")]
    process = numeric_average(task_values)
    final = row.get("期末", "")
    if not process and not final:
        return ""
    try:
        return str(round((float(process or 0) * 0.4) + (float(final or 0) * 0.6)))
    except ValueError:
        return ""


def excel_cover_page(package: MarkdownPackage) -> str:
    class_name = "、".join(list_value(package.meta.get("class_name")))
    teachers = "  ".join(list_value(package.meta.get("teachers")))
    rows = [
        '#align(center)[#text(size: 24pt, weight: "bold")[成  绩  记  分  册]]',
        "#v(46mm)",
        f'#align(center)[#text(size: 14pt)[{typst_escape(package.meta.get("school_year", ""))}{typst_escape(package.meta.get("semester", ""))}]]',
        "#v(10mm)",
        f'#align(center)[#text(size: 14pt)[班级  {typst_escape(class_name)}班]]',
        "#v(10mm)",
        f'#align(center)[#text(size: 14pt)[学科  {typst_escape(package.meta.get("course_name", ""))}]]',
        "#v(10mm)",
        f'#align(center)[#text(size: 14pt)[授课教师  {typst_escape(teachers)}]]',
        "#v(16mm)",
        f'#align(center)[#text(size: 13pt)[{typst_escape(package.meta.get("date", ""))}]]',
    ]
    return "#pagebreak(weak: true)\n" + "\n".join(rows)


def scorebook_body_page(package: MarkdownPackage) -> str:
    raw_widths = [11.140625, 5.640625, 13.0, 4.140625, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 11.0, 11.0, 11.0, 9.5]
    cols = excel_scaled_widths(raw_widths)
    data_row_count = max(54, len(package.score_rows))
    rows = [12.0, 8.8] + [7.3] * data_row_count + [8.4, 8.4, 8.4, 8.4]
    cells: list[str] = []
    diag_width = sum(cols[:3])
    diag_height = sum(rows[:2])
    cells.append(
        typst_table_cell(
            f'#excel-diag({typst_mm(diag_width)}, {typst_mm(diag_height)}, [学   号], [姓   名])',
            colspan=3,
            rowspan=2,
            inset="0pt",
            raw=True,
        )
    )
    cells.append(typst_table_cell("作 业 测 试 成 绩", colspan=8, align="center + horizon"))
    cells.extend(
        [
            typst_table_cell("平时\n成绩", rowspan=2),
            typst_table_cell("期末\n成绩", rowspan=2),
            typst_table_cell("学期\n成绩", rowspan=2),
            typst_table_cell("备注", rowspan=2),
        ]
    )
    for i in range(1, 9):
        cells.append(typst_table_cell(str(i)))
    for index in range(data_row_count):
        row = package.score_rows[index] if index < len(package.score_rows) else {}
        task_values = [score_value(row, f"任务{i}") for i in range(1, 9)]
        process = numeric_average([score_value(row, f"任务{i}") for i in range(1, len(package.tasks) + 1)])
        values = [
            row.get("学号", ""),
            row.get("姓名", ""),
            "",
            *task_values,
            process,
            row.get("期末", ""),
            final_score(row),
            "",
        ]
        cells.append(typst_table_cell(values[0], align="center + horizon"))
        cells.append(typst_table_cell(values[1], colspan=2, align="center + horizon"))
        for value in values[3:]:
            cells.append(typst_table_cell(value, align="center + horizon"))
    footer = [
        ("任课教师签名", 3, 1),
        ("", 2, 1),
        ("教研室审核", 3, 1),
        ("", 3, 1),
        ("系部审核", 2, 2),
        ("", 2, 2),
        ("日期", 3, 1),
        (package.meta.get("date", ""), 2, 1),
        ("", 6, 1),
        ("", 0, 0),
    ]
    cells.extend(
        [
            typst_table_cell("任课教师签名", colspan=3),
            typst_table_cell("", colspan=2),
            typst_table_cell("教研室审核", colspan=3),
            typst_table_cell("", colspan=3),
            typst_table_cell("系部审核", colspan=2, rowspan=2),
            typst_table_cell("", colspan=2, rowspan=2),
            typst_table_cell("日期", colspan=3),
            typst_table_cell(package.meta.get("date", ""), colspan=2),
            typst_table_cell("", colspan=6),
        ]
    )
    return "#pagebreak(weak: true)\n#text(size: 7.4pt)[\n" + typst_table(cols, rows, cells) + "\n]"


def score_summary_page(package: MarkdownPackage) -> str:
    raw_widths = [4.296875, 8.8515625, 7.03125, 13.0, 13.0, 13.0, 13.0, 13.0, 13.0, 13.0, 5.59375]
    cols = excel_scaled_widths(raw_widths)
    data_count = max(42, len(package.score_rows))
    rows = [10.5, 8.0, 7.0, 15.5, 12.0, 7.0] + [6.7] * data_count
    cells = [
        typst_table_cell("工学一体化课程/基本技能课程考核成绩汇总表", colspan=11, align="center + horizon", raw=False),
        typst_table_cell("专业：", colspan=2),
        typst_table_cell(package.meta.get("major_name", ""), colspan=3),
        typst_table_cell("班级："),
        typst_table_cell("、".join(list_value(package.meta.get("class_name"))), colspan=2),
        typst_table_cell(f"{package.meta.get('school_year', '')} {package.meta.get('semester', '')}", colspan=3),
        typst_table_cell("课程名称", colspan=2),
        typst_table_cell(package.meta.get("course_name", ""), colspan=3),
        typst_table_cell("课程类型", colspan=2),
        typst_table_cell("一体化课□  基本技能实训课√", colspan=4),
        typst_table_cell(""),
        typst_table_cell(
            f'#excel-diag({typst_mm(sum(cols[:2]))}, {typst_mm(rows[3] + rows[4] + rows[5])}, [学生\\n姓名], [考核\\n成绩])',
            colspan=2,
            rowspan=3,
            inset="0pt",
            raw=True,
        ),
    ]
    for i in range(8):
        task = package.tasks[i] if i < len(package.tasks) else {"task_name": "", "hours": ""}
        cells.append(typst_table_cell(f"{task['task_name']}\n{task['hours']}", rowspan=2))
    cells.append(typst_table_cell("总评成绩", rowspan=3))
    for i in range(8):
        task = package.tasks[i] if i < len(package.tasks) else {"hours": ""}
        cells.append(typst_table_cell(str(task.get("hours", ""))))
    for index in range(data_count):
        row = package.score_rows[index] if index < len(package.score_rows) else {}
        cells.append(typst_table_cell(str(index + 1) if row else ""))
        cells.append(typst_table_cell(row.get("姓名", "")))
        for i in range(1, 9):
            cells.append(typst_table_cell(row.get(f"任务{i}", "")))
        cells.append(typst_table_cell(final_score(row)))
    return "#pagebreak(weak: true)\n#text(size: 6.9pt)[\n" + typst_table(cols, rows, cells) + "\n]"


def analysis_page(package: MarkdownPackage) -> str:
    raw_widths = [8.7109375, 13.0, 13.0, 13.0, 13.0, 13.0, 13.0, 13.0, 15.75]
    cols = excel_scaled_widths(raw_widths)
    rows = [13.0, 11.0, 8.5, 9.0, 9.0, 9.0, 9.0, 8.5, 26.0, 26.0, 26.0, 26.0, 22.0]
    cells = [
        typst_table_cell("成   绩  分  析  表", colspan=9, align="center + horizon"),
        typst_table_cell(f"{package.meta.get('school_year', '')}{package.meta.get('semester', '')}", colspan=4),
        typst_table_cell("班级："),
        typst_table_cell("、".join(list_value(package.meta.get("class_name"))), colspan=2),
        typst_table_cell("时间："),
        typst_table_cell(package.meta.get("date", "")),
        typst_table_cell("课程名称", colspan=2),
        typst_table_cell(package.meta.get("course_name", ""), colspan=5),
        typst_table_cell("教师姓名"),
        typst_table_cell("、".join(list_value(package.meta.get("teachers")))),
        typst_table_cell("全班人数", rowspan=2),
        typst_table_cell("缺考人数", rowspan=2),
        typst_table_cell("考试成绩、分类、人数及百分比", colspan=6),
        typst_table_cell("最高分"),
        typst_table_cell("不及格"),
        typst_table_cell("及格"),
        typst_table_cell("80分以上"),
        typst_table_cell("90分以上"),
        typst_table_cell("平均成绩"),
        typst_table_cell("及格率"),
        typst_table_cell(summary_stat(package, "max")),
        typst_table_cell(str(len(package.score_rows)), rowspan=2),
        typst_table_cell("0", rowspan=2),
        typst_table_cell(summary_stat(package, "lt60"), rowspan=2),
        typst_table_cell(summary_stat(package, "gte60"), rowspan=2),
        typst_table_cell(summary_stat(package, "gte80lt90"), rowspan=2),
        typst_table_cell(summary_stat(package, "gte90"), rowspan=2),
        typst_table_cell(summary_stat(package, "avg"), rowspan=2),
        typst_table_cell(summary_stat(package, "pass_rate"), rowspan=2),
        typst_table_cell("最低分"),
        typst_table_cell(summary_stat(package, "min")),
        typst_table_cell("从学生掌握基本理论、基本概念、基本技能和重点难关等方面进行分析", colspan=9),
        typst_table_cell("试卷分析"),
        typst_table_cell(package.analysis.get("试卷分析", "无"), colspan=8, align="left + horizon"),
        typst_table_cell("存在问题"),
        typst_table_cell(package.analysis.get("存在问题", "无"), colspan=8, align="left + horizon"),
        typst_table_cell("今后改进措施"),
        typst_table_cell(package.analysis.get("今后改进措施", "无"), colspan=8, align="left + horizon"),
        typst_table_cell("异常情况分析"),
        typst_table_cell(package.analysis.get("异常情况分析", "无"), colspan=8, align="left + horizon"),
        typst_table_cell("教研室意见", colspan=5),
        typst_table_cell("系部意见", colspan=4),
    ]
    return "#pagebreak(weak: true)\n#text(size: 7.2pt)[\n" + typst_table(cols, rows, cells) + "\n]"


def summary_scores(package: MarkdownPackage) -> list[float]:
    values: list[float] = []
    for row in package.score_rows:
        score = final_score(row)
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
        return f"{sum(1 for score in scores if score >= 60) / len(scores):.0%}"
    return ""


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
        body.append(f'#cover("教学日志封面", "固定模板封面", [\n{meta_rows(package)}\n])')
    if flags["过程考核评价表封面"]:
        task_lines = "\\n".join(f"{i}. {task['task_name']}（{task['hours']}课时）" for i, task in enumerate(package.tasks, 1))
        body.append(f'#cover("过程考核评价表封面", "固定模板封面", [\n{meta_rows(package, {"过程考核任务": task_lines})}\n])')
    if flags["交接班记录封面"]:
        body.append(
            '#cover("交接班记录封面", "固定模板封面", [\n'
            + meta_rows(
                package,
                {
                    "交接班级": "、".join(list_value(package.meta.get("handover_class_name"))),
                    "交接教师": "、".join(list_value(package.meta.get("handover_teachers"))),
                },
            )
            + "\n])"
        )
    template = read_text(template_path)
    document_title = f"{package.meta.get('course_name', '')} 期末教学材料包"
    document_author = "、".join(list_value(package.meta.get("teachers")))
    return (
        template.replace("{{DOCUMENT_TITLE}}", typst_string(document_title))
        .replace("{{DOCUMENT_AUTHOR}}", typst_string(document_author))
        .replace("{{PACKAGE_BODY}}", "\n\n".join(body).strip() + "\n"),
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
        ["公式占位", "总评与折算分由教师-facing workbook 或学校模板公式处理"],
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
    return {
        "score_data": score_data,
        "task_map": task_map,
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


def worksheet_xml(rows: list[list[Any]]) -> str:
    body = []
    for r_index, row in enumerate(rows, start=1):
        cells = []
        for c_index, value in enumerate(row, start=1):
            ref = f"{column_name(c_index)}{r_index}"
            text = xml_escape(scalar(value))
            cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{text}</t></is></c>')
        body.append(f'<row r="{r_index}">{"".join(cells)}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(body)}</sheetData></worksheet>'
    )


def write_xlsx(path: Path, package: MarkdownPackage, artifacts: dict[str, Any]) -> None:
    score_rows = [package.score_headers + ["备注"]]
    score_rows.extend([[row.get(header, "") for header in package.score_headers] + [""] for row in package.score_rows])
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
            "</Relationships>"
        ),
        "xl/workbook.xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="成绩数据" sheetId="1" r:id="rId1"/>'
            '<sheet name="任务映射" sheetId="2" r:id="rId2"/>'
            '<sheet name="成绩汇总" sheetId="3" r:id="rId3"/></sheets></workbook>'
        ),
        "xl/worksheets/sheet1.xml": worksheet_xml(score_rows),
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


def render(markdown_path: Path, workdir: Path, skill_dir: Path, pdf: bool) -> dict[str, Any]:
    package = parse_markdown(markdown_path)
    errors = validate_markdown(package, export_ready=True)
    if errors:
        raise RenderError("; ".join(errors))

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
    write_text(tables_dir / "score-data.json", stable_json(artifacts["score_data"]))
    write_text(tables_dir / "task-map.json", stable_json(artifacts["task_map"]))
    write_text(tables_dir / "score-summary.json", stable_json(artifacts["score_summary"]))
    write_csv(tables_dir / "score-data.csv", package.score_headers, artifacts["score_data"])
    write_xlsx(tables_dir / "scorebook.xlsx", package, artifacts)

    pdf_status = "not_requested"
    pdf_message = ""
    if pdf:
        pdf_status, pdf_message = compile_pdf(typ_out, pdf_out)
    manifest = {
        "skill": "end-of-term-teaching-materials",
        "version": VERSION,
        "review_cleared": True,
        "enabled_packages": flags,
        "warnings": warnings,
        "markdown": str(md_out.name),
        "typst": str(typ_out.name),
        "pdf": {"status": pdf_status, "path": pdf_out.name if pdf_out.exists() else "", "message": pdf_message},
        "table_artifacts_verified": verify_table_artifacts(package, artifacts),
        "workbook_verified": (tables_dir / "scorebook.xlsx").exists(),
        "repeatable": False,
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
    return True


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repeatability_hashes(workdir: Path) -> dict[str, str]:
    paths = [
        workdir / "end-of-term-full.md",
        workdir / "end-of-term-package.typ",
        workdir / "tables/score-data.json",
        workdir / "tables/score-data.csv",
        workdir / "tables/task-map.json",
        workdir / "tables/score-summary.json",
        workdir / "tables/scorebook.xlsx",
    ]
    return {str(path.relative_to(workdir)): hash_file(path) for path in paths}


def verify(skill_dir: Path, workdir: Path) -> dict[str, Any]:
    fixture = skill_dir / "references/fixtures/end-of-term-source.json"
    source_out = workdir / "end-of-term-source.json"
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

    unresolved = workdir / "unresolved-review.md"
    unresolved_text = read_text(markdown_out).replace("\n## 复核标记\n\n无\n", "\n## 复核标记\n\n| 类型 | 位置 | 当前值 | 说明 |\n|------|------|--------|------|\n| 需复核 | 成绩数据 / 学生乙 / 任务1 | 87? | 验证阻断。 |\n").replace("| STU0002 | 学生乙 | 87 |", "| STU0002 | 学生乙 | 87? |")
    write_text(unresolved, unresolved_text)
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
    manifest = render(Path(args.input), Path(args.workdir), Path(args.skill_dir), bool(args.pdf))
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
                "commands": ["example", "validate", "markdown", "render", "verify", "manifest", "info", "version"],
                "outputs": [
                    "end-of-term-full.md",
                    "end-of-term-package.typ",
                    "end-of-term-package.pdf",
                    "manifest.json",
                    "tables/score-data.json",
                    "tables/score-data.csv",
                    "tables/task-map.json",
                    "tables/score-summary.json",
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
