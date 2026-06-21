#!/usr/bin/env python3
"""Narrow Phase 39 renderer for the tiaokedan Markdown contract."""

from __future__ import annotations

import argparse
import difflib
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


FRONTMATTER_FIELDS = ("title", "recipient", "department", "date")
TABLE_HEADERS = [
    "序号",
    "班级",
    "课程",
    "原上课时间",
    "原授课教师",
    "调整后上课时间",
    "调整后上课教师",
    "备注",
]
REQUIRED_TABLE_HEADERS = TABLE_HEADERS[:-1]
RAW_TYPST_RE = re.compile(r"#(?:set|let|table|linebreak\s*\(\)|page|align|block|text|h\s*\(|v\s*\()", re.I)
HTML_TAG_RE = re.compile(r"<\s*/?\s*([A-Za-z][A-Za-z0-9-]*)\b[^>]*>")
REVIEW_MARKER_RE = re.compile(r"\{\{(待补充|AI草稿)\s*:[^}]*\}\}")


class ContractError(Exception):
    """Raised when Markdown violates the Phase 39 rendering contract."""


@dataclass
class TiaokedanDocument:
    title: str
    recipient: str
    reason: str
    rows: list[list[str]]
    department: str
    date: str


def fail(message: str) -> None:
    print(f"tiaokedan: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ContractError("missing YAML frontmatter")

    closing = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing = index
            break
    if closing is None:
        raise ContractError("malformed YAML frontmatter: missing closing delimiter")

    fields: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:closing], start=2):
        if not line.strip():
            continue
        if ":" not in line:
            raise ContractError(f"malformed YAML frontmatter line {line_number}: expected key: value")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ContractError(f"malformed YAML frontmatter line {line_number}: empty key")
        fields[key] = value

    for field in FRONTMATTER_FIELDS:
        if field not in fields:
            raise ContractError(f"missing required frontmatter field: {field}")
        validate_required_value(fields[field], f"frontmatter field: {field}")

    body = "\n".join(lines[closing + 1 :])
    return fields, body


def strip_blank(lines: list[str]) -> list[str]:
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def parse_table_row(line: str) -> list[str]:
    if not line.strip().startswith("|") or not line.strip().endswith("|"):
        raise ContractError("malformed adjustment table: row must start and end with |")
    return [cell.strip() for cell in line.strip()[1:-1].split("|")]


def is_separator_row(line: str) -> bool:
    cells = parse_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def validate_required_value(value: str, area: str) -> None:
    stripped = value.strip()
    if not stripped:
        raise ContractError(f"missing required value in {area}")
    marker = REVIEW_MARKER_RE.search(stripped)
    if marker:
        raise ContractError(f"unresolved required marker in {area}")
    validate_supported_syntax(stripped, area)


def validate_supported_syntax(value: str, area: str) -> None:
    for match in HTML_TAG_RE.finditer(value):
        tag = match.group(1).lower()
        if tag != "br":
            raise ContractError(f"unsupported inline HTML in {area}: <{tag}>")

    # Remove the sole supported HTML marker before raw-Typst scanning.
    raw_scan = re.sub(r"<\s*br\s*/?\s*>", "", value, flags=re.I)
    if RAW_TYPST_RE.search(raw_scan):
        raise ContractError(f"unsupported raw Typst in {area}")


def parse_body(body: str, frontmatter: dict[str, str]) -> TiaokedanDocument:
    lines = body.splitlines()
    if "## 调课说明" not in [line.strip() for line in lines]:
        raise ContractError("missing required section: ## 调课说明")

    section_start = next(index for index, line in enumerate(lines) if line.strip() == "## 调课说明")
    section_lines = strip_blank(lines[section_start + 1 :])
    if len(section_lines) < 5:
        raise ContractError("malformed 调课说明 section: expected recipient, paragraph, table, and closing")

    recipient_line = section_lines[0].strip()
    validate_required_value(recipient_line, "recipient line")
    if recipient_line != frontmatter["recipient"]:
        raise ContractError("recipient line does not match frontmatter field: recipient")

    table_start = None
    for index, line in enumerate(section_lines[1:], start=1):
        if line.strip().startswith("|"):
            table_start = index
            break
    if table_start is None:
        raise ContractError("missing adjustment table")

    paragraph_lines = strip_blank(section_lines[1:table_start])
    if len(paragraph_lines) != 1:
        raise ContractError("malformed 调课说明 paragraph: expected one explanatory paragraph")
    reason = paragraph_lines[0].strip()
    validate_required_value(reason, "说明段落")

    table_lines: list[str] = []
    after_table_index = table_start
    while after_table_index < len(section_lines) and section_lines[after_table_index].strip().startswith("|"):
        table_lines.append(section_lines[after_table_index])
        after_table_index += 1

    rows = parse_adjustment_table(table_lines)
    closing_lines = [line.strip() for line in section_lines[after_table_index:] if line.strip()]
    if len(closing_lines) != 2:
        raise ContractError("malformed closing: expected department and date lines")
    department = closing_lines[0].strip()
    date = closing_lines[1].strip()
    validate_required_value(department, "closing department")
    validate_required_value(date, "closing date")
    if department != frontmatter["department"]:
        raise ContractError("closing department does not match frontmatter field: department")
    if date != frontmatter["date"]:
        raise ContractError("closing date does not match frontmatter field: date")

    return TiaokedanDocument(
        title=frontmatter["title"],
        recipient=frontmatter["recipient"],
        reason=reason,
        rows=rows,
        department=department,
        date=date,
    )


def parse_adjustment_table(table_lines: list[str]) -> list[list[str]]:
    if len(table_lines) < 3:
        raise ContractError("malformed adjustment table: expected header, separator, and at least one row")

    headers = parse_table_row(table_lines[0])
    if len(headers) != len(TABLE_HEADERS):
        raise ContractError(f"malformed adjustment table: expected 8 columns, found {len(headers)}")
    if headers != TABLE_HEADERS:
        raise ContractError("malformed adjustment table: unexpected columns")

    if not is_separator_row(table_lines[1]):
        raise ContractError("malformed adjustment table: expected separator row")
    separator = parse_table_row(table_lines[1])
    if len(separator) != len(TABLE_HEADERS):
        raise ContractError(f"malformed adjustment table: expected 8 columns, found {len(separator)}")

    rows: list[list[str]] = []
    for markdown_row_index, line in enumerate(table_lines[2:], start=1):
        cells = parse_table_row(line)
        if len(cells) != len(TABLE_HEADERS):
            raise ContractError(
                f"malformed adjustment table: expected 8 columns in row {markdown_row_index}, found {len(cells)}"
            )
        for column_index, header in enumerate(REQUIRED_TABLE_HEADERS):
            validate_required_value(cells[column_index], f"row {markdown_row_index} {header}")
        remark = cells[-1].strip()
        if remark:
            validate_supported_syntax(remark, f"row {markdown_row_index} 备注")
            marker = REVIEW_MARKER_RE.search(remark)
            if marker:
                raise ContractError(f"unresolved required marker in row {markdown_row_index} 备注")
        rows.append(cells)

    return rows


def typst_cell(value: str) -> str:
    normalized = re.sub(r"<\s*br\s*/?\s*>", "#linebreak()", value.strip(), flags=re.I)
    return f"  tc[{normalized}],"


def render_typst(document: TiaokedanDocument) -> str:
    lines = [
        "// Phase 37 hand-authored Typst reference for 调课单.",
        "// This is the accepted surface before Markdown contracts or renderers exist.",
        "",
        "#let FONT_SONG = (",
        '  "Songti SC",',
        '  "STSong",',
        '  "SimSun",',
        '  "NSimSun",',
        '  "Noto Serif CJK SC",',
        '  "Source Han Serif SC",',
        ")",
        "#let FONT_FS = (",
        '  "FangSong",',
        '  "STFangsong",',
        '  "FangSong_GB2312",',
        '  "Fangsong SC",',
        ")",
        "",
        '#set page(paper: "a4", flipped: true)',
        '#set text(lang: "zh", font: FONT_FS, size: 14pt, hyphenate: false)',
        "#set par(justify: true, leading: 1.15em)",
        "",
        "#let para(body, indent: 2em) = block(width: 100%)[",
        "  #set text(font: FONT_FS, size: 14pt)",
        "  #set par(first-line-indent: indent, justify: true, leading: 1.15em)",
        "  #body",
        "]",
        "",
        "#let tc(body) = table.cell(",
        "  align: center + horizon,",
        "  inset: (x: 3pt, y: 5pt),",
        ")[",
        "  #set text(font: FONT_FS, size: 14pt)",
        "  #body",
        "]",
        "",
        "#align(center)[",
        f'  #text(font: FONT_SONG, size: 22pt, weight: "bold")[#strong[{document.title}]]',
        "]",
        "",
        "#v(1.2em)",
        "",
        f"#para(indent: 0pt)[{document.recipient}]",
        "",
        "#para[",
        f"  #h(2em){document.reason}",
        "]",
        "",
        "#v(0.8em)",
        "",
        "#block(width: 100%)[#table(",
        "  columns: (0.7fr, 1.25fr, 1.75fr, 1.75fr, 1fr, 1.85fr, 1.15fr, 0.7fr),",
        "  stroke: 0.75pt,",
        "  align: center + horizon,",
        "  table.header(",
    ]
    lines.extend(f"    tc[{header}]," for header in TABLE_HEADERS)
    lines.extend(
        [
            "  ),",
        ]
    )
    for row in document.rows:
        lines.extend(typst_cell(cell) for cell in row)
    lines.extend(
        [
            ")]",
            "",
            "#v(3.2em)",
            "",
            "#align(right)[",
            "  #block(width: 12em)[",
            "    #set text(font: FONT_FS, size: 14pt)",
            "    #set par(first-line-indent: 0pt, justify: false, leading: 1.15em)",
            f"    #align(center)[{document.department}]",
            "    #v(0.4em)",
            f"    #align(center)[{document.date}]",
            "  ]",
            "]",
        ]
    )
    return "\n".join(lines) + "\n"


def render_command(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    output_path = Path(args.typ)
    pdf_path = Path(args.pdf) if args.pdf else None
    expected_path = Path(args.expected_typ) if args.expected_typ else None

    if not input_path.is_file():
        fail(f"input file not found: {input_path}")
    if output_path.exists() and expected_path and output_path.resolve() == expected_path.resolve():
        fail("refusing to overwrite expected Typst reference")
    if pdf_path and pdf_path.exists():
        try:
            pdf_path.unlink()
        except OSError as error:
            fail(f"cannot remove stale PDF output: {pdf_path}: {error}")

    try:
        frontmatter, body = parse_frontmatter(input_path.read_text(encoding="utf-8"))
        document = parse_body(body, frontmatter)
        rendered = render_typst(document)
    except ContractError as error:
        fail(str(error))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")

    if expected_path:
        if not expected_path.is_file():
            fail(f"expected Typst file not found: {expected_path}")
        expected = expected_path.read_text(encoding="utf-8")
        if rendered != expected:
            diff = "".join(
                difflib.unified_diff(
                    expected.splitlines(keepends=True),
                    rendered.splitlines(keepends=True),
                    fromfile=str(expected_path),
                    tofile=str(output_path),
                )
            )
            print(diff, file=sys.stderr, end="")
            fail(f"generated Typst differs from expected file: {expected_path}")

    if pdf_path:
        compile_pdf(output_path, pdf_path)

    return 0


def compile_pdf(typ_path: Path, pdf_path: Path) -> None:
    typst = shutil.which("typst")
    if not typst:
        remove_if_present(pdf_path)
        fail("typst CLI not found; install typst before requesting --pdf")

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [typst, "compile", str(typ_path), str(pdf_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        remove_if_present(pdf_path)
        stderr = result.stderr.strip().splitlines()
        detail = f": {stderr[-1]}" if stderr else ""
        fail(f"typst compile failed with exit code {result.returncode}{detail}")

    if not pdf_path.is_file() or pdf_path.stat().st_size <= 0:
        remove_if_present(pdf_path)
        fail(f"typst compile produced empty PDF: {pdf_path}")


def remove_if_present(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tiaokedan_renderer.py")
    subparsers = parser.add_subparsers(dest="command", required=True)
    render = subparsers.add_parser("render")
    render.add_argument("--input", required=True)
    render.add_argument("--typ", required=True)
    render.add_argument("--pdf")
    render.add_argument("--expected-typ")
    render.set_defaults(func=render_command)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
