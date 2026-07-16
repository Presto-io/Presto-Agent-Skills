#!/usr/bin/env python3
"""Narrow Phase 39 renderer for the tiaokedan Markdown contract."""

from __future__ import annotations

import argparse
import difflib
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from delivery_transaction import DeliveryError, DeliverySession, derive_delivery_spec


FRONTMATTER_DEFAULTS = {
    "title": "调课说明",
    "recipient": "教务处：",
}
REQUIRED_FRONTMATTER_FIELDS = ("department", "date")
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
COMPACT_DATE_RE = re.compile(r"\b(\d{4})(\d{2})(\d{2})\b")
ISO_DATE_RE = re.compile(r"^['\"]?(\d{4})-(\d{1,2})-(\d{1,2})['\"]?$")


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
        value = unquote_yaml_scalar(value.strip())
        if not key:
            raise ContractError(f"malformed YAML frontmatter line {line_number}: empty key")
        fields[key] = value

    for field, default in FRONTMATTER_DEFAULTS.items():
        fields.setdefault(field, default)

    for field in REQUIRED_FRONTMATTER_FIELDS:
        if field not in fields:
            raise ContractError(f"missing required frontmatter field: {field}")
        fields[field] = normalize_scalar(fields[field])
        validate_required_value(fields[field], f"frontmatter field: {field}")

    fields["title"] = normalize_scalar(fields["title"])
    fields["recipient"] = normalize_scalar(fields["recipient"])
    fields["date"] = normalize_date(fields["date"])
    fields["department"] = normalize_scalar(fields["department"])
    validate_required_value(fields["title"], "frontmatter field: title")
    validate_required_value(fields["recipient"], "frontmatter field: recipient")

    body = "\n".join(lines[closing + 1 :])
    return fields, body


def unquote_yaml_scalar(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


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
    stripped_lines = [line.strip() for line in lines]
    if "## 调课说明" in stripped_lines:
        section_start = next(index for index, line in enumerate(lines) if line.strip() == "## 调课说明")
        section_lines = strip_blank(lines[section_start + 1 :])
    else:
        section_lines = strip_blank(lines[:])

    if len(section_lines) < 3:
        raise ContractError("malformed 调课说明 section: expected paragraph, table, and optional closing")

    recipient = frontmatter["recipient"]
    if section_lines and section_lines[0].strip() == recipient:
        recipient_line = normalize_scalar(section_lines.pop(0).strip())
        validate_required_value(recipient_line, "recipient line")
        if recipient_line != recipient:
            raise ContractError("recipient line does not match frontmatter field: recipient")

    table_start = None
    for index, line in enumerate(section_lines):
        if line.strip().startswith("|"):
            table_start = index
            break
    if table_start is None:
        raise ContractError("missing adjustment table")

    paragraph_lines = strip_blank(section_lines[:table_start])
    if len(paragraph_lines) != 1:
        raise ContractError("malformed 调课说明 paragraph: expected one explanatory paragraph")
    reason = normalize_scalar(paragraph_lines[0].strip())
    validate_required_value(reason, "说明段落")

    table_lines: list[str] = []
    after_table_index = table_start
    while after_table_index < len(section_lines) and section_lines[after_table_index].strip().startswith("|"):
        table_lines.append(section_lines[after_table_index])
        after_table_index += 1

    rows = parse_adjustment_table(table_lines)
    closing_lines = [line.strip() for line in section_lines[after_table_index:] if line.strip()]
    if closing_lines:
        if len(closing_lines) != 2:
            raise ContractError("malformed closing: expected department and date lines")
        department = normalize_scalar(closing_lines[0].strip())
        date = normalize_date(normalize_scalar(closing_lines[1].strip()))
    else:
        department = frontmatter["department"]
        date = frontmatter["date"]
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
    has_sequence_column = headers == TABLE_HEADERS
    has_implicit_sequence = headers == TABLE_HEADERS[1:]
    if not has_sequence_column and not has_implicit_sequence and len(headers) != len(TABLE_HEADERS):
        raise ContractError(f"malformed adjustment table: expected 8 columns, found {len(headers)}")
    if not has_sequence_column and not has_implicit_sequence:
        raise ContractError("malformed adjustment table: unexpected columns")

    if not is_separator_row(table_lines[1]):
        raise ContractError("malformed adjustment table: expected separator row")
    separator = parse_table_row(table_lines[1])
    expected_columns = len(TABLE_HEADERS) if has_sequence_column else len(TABLE_HEADERS) - 1
    if len(separator) != expected_columns:
        raise ContractError(f"malformed adjustment table: expected {expected_columns} columns, found {len(separator)}")

    rows: list[list[str]] = []
    for markdown_row_index, line in enumerate(table_lines[2:], start=1):
        cells = parse_table_row(line)
        if len(cells) != expected_columns:
            raise ContractError(
                f"malformed adjustment table: expected {expected_columns} columns in row {markdown_row_index}, found {len(cells)}"
            )
        if has_implicit_sequence:
            cells = [str(markdown_row_index), *cells]
        cells = normalize_table_cells(cells, markdown_row_index)
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


def normalize_table_cells(cells: list[str], row_index: int) -> list[str]:
    normalized = [normalize_scalar(cell) for cell in cells]
    for column_name in ("原上课时间", "调整后上课时间"):
        column_index = TABLE_HEADERS.index(column_name)
        normalized[column_index] = normalize_time_cell(normalized[column_index], row_index)
    return normalized


def normalize_scalar(value: str) -> str:
    normalized = value.strip()
    normalized = normalized.replace("孙老师老师", "孙老师")
    return normalize_inline_dates(normalized)


def normalize_inline_dates(value: str) -> str:
    return COMPACT_DATE_RE.sub(lambda match: format_chinese_date(*match.groups()), value)


def normalize_date(value: str) -> str:
    stripped = value.strip()
    iso_match = ISO_DATE_RE.fullmatch(stripped)
    if iso_match:
        return format_chinese_date(*iso_match.groups())
    compact_match = COMPACT_DATE_RE.fullmatch(stripped)
    if compact_match:
        return format_chinese_date(*compact_match.groups())
    return normalize_scalar(stripped)


def format_chinese_date(year: str, month: str, day: str) -> str:
    return f"{int(year)}年{int(month)}月{int(day)}日"


def normalize_time_cell(value: str, row_index: int) -> str:
    normalized = value.strip()
    if re.search(r"<\s*br\s*/?\s*>", normalized, flags=re.I):
        return normalized

    match = re.match(r"^(?P<date>\d{4}年\d{1,2}月\d{1,2}日)\s+(?P<time>.+)$", normalized)
    if not match:
        return normalized

    separator = "<br>" if row_index == 1 else ""
    return f"{match.group('date')}{separator}{match.group('time')}"


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
        "#let FONT_TITLE_SONG = (",
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
        f'  #text(font: FONT_TITLE_SONG, size: 22pt, weight: 700)[{document.title}]',
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
    pdf_path = Path(args.pdf) if args.pdf else None
    expected_path = Path(args.expected_typ) if args.expected_typ else None

    if not input_path.is_file():
        fail(f"input file not found: {input_path}")
    try:
        spec = derive_delivery_spec(Path(args.typ), pdf_path)
        output_path = spec.delivery_root / f"{spec.stem}.typ"
        if expected_path and Path(os.path.abspath(expected_path)) == output_path:
            raise DeliveryError("refusing to overwrite expected Typst reference")
        markdown_bytes = input_path.read_bytes()
        markdown_text = markdown_bytes.decode("utf-8")
        frontmatter, body = parse_frontmatter(markdown_text)
        document = parse_body(body, frontmatter)
        rendered = render_typst(document)
        rendered_bytes = rendered.encode("utf-8")
    except (ContractError, DeliveryError, OSError, UnicodeError) as error:
        fail(str(error))

    try:
        with DeliverySession(spec) as session:
            session.candidate_path(f"{spec.stem}.md").write_bytes(markdown_bytes)
            candidate_typ = session.candidate_path(f"{spec.stem}.typ")
            candidate_typ.write_bytes(rendered_bytes)

            if expected_path:
                if not expected_path.is_file():
                    raise DeliveryError(f"expected Typst file not found: {expected_path}")
                expected = expected_path.read_text(encoding="utf-8")
                if rendered != expected:
                    diff = "".join(
                        difflib.unified_diff(
                            expected.splitlines(keepends=True),
                            rendered.splitlines(keepends=True),
                            fromfile=str(expected_path),
                            tofile=str(candidate_typ),
                        )
                    )
                    session.evidence_path("expected-typ.diff").write_text(diff[:65536], encoding="utf-8")
                    public_diff = diff[:1024]
                    if public_diff:
                        print(public_diff, file=sys.stderr, end="" if public_diff.endswith("\n") else "\n")
                    raise DeliveryError(f"generated Typst differs from expected file: {expected_path}")

            if pdf_path:
                compile_pdf(candidate_typ, session.candidate_path(f"{spec.stem}.pdf"))

            publication = session.publish(validate_delivery_bundle)
    except (DeliveryError, OSError, UnicodeError) as error:
        fail(str(error))

    print(f"tiaokedan: publication {publication}")
    return 0


def validate_delivery_bundle(bundle: dict[str, bytes]) -> None:
    markdown_names = [name for name in bundle if name.endswith(".md")]
    typst_names = [name for name in bundle if name.endswith(".typ")]
    pdf_names = [name for name in bundle if name.endswith(".pdf")]
    if len(markdown_names) != 1 or len(typst_names) != 1 or len(pdf_names) not in (0, 1):
        raise DeliveryError("candidate has an invalid tiaokedan managed set")
    for name in (*markdown_names, *typst_names):
        payload = bundle[name]
        if not payload:
            raise DeliveryError(f"candidate text artifact is empty: {name}")
        try:
            payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise DeliveryError(f"candidate text artifact is not UTF-8: {name}") from error
    for name in pdf_names:
        if not bundle[name].startswith(b"%PDF-"):
            raise DeliveryError(f"candidate PDF has an invalid header: {name}")


def compile_pdf(typ_path: Path, pdf_path: Path) -> None:
    typst = shutil.which("typst")
    if not typst:
        raise DeliveryError("typst CLI not found; install typst before requesting --pdf")

    result = subprocess.run(
        [typst, "compile", str(typ_path), str(pdf_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip().splitlines()
        detail = f": {stderr[-1][-512:]}" if stderr else ""
        raise DeliveryError(f"typst compile failed with exit code {result.returncode}{detail}")

    try:
        payload = pdf_path.read_bytes()
    except OSError as error:
        raise DeliveryError(f"typst compile did not create a readable PDF: {pdf_path}") from error
    if not payload:
        raise DeliveryError(f"typst compile produced empty PDF: {pdf_path}")
    if not payload.startswith(b"%PDF-"):
        raise DeliveryError(f"typst compile produced an invalid PDF header: {pdf_path}")


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
