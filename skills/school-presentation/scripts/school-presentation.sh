#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"

usage() {
  cat <<'USAGE'
Usage:
  school-presentation.sh example --output <school-presentation-full.md>
  school-presentation.sh render --input <input.md> [--html <output.html>]
                                [--manifest <manifest.json>]
                                [--max-size-mb <mb>]
  school-presentation.sh verify --workdir <dir> [--max-size-mb <mb>]
  school-presentation.sh info

Environment:
  SCHOOL_PRESENTATION_MAX_MB  Override the default 50 MB output cap.
USAGE
}

die() {
  printf 'school-presentation.sh: %s\n' "$*" >&2
  exit 1
}

python_renderer() {
  python3 - "$SKILL_DIR" "$@" <<'PY'
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import mimetypes
import re
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(sys.argv[1]).resolve()
TEMPLATE_MD = SKILL_DIR / "templates" / "school-presentation-full.md"
IDENTITY_DIR = SKILL_DIR / "references" / "identity"
IMAGE_DIR = IDENTITY_DIR / "images"
DEFAULT_MAX_MB = 50


def fail(message: str) -> None:
    print(f"school-presentation.sh: {message}", file=sys.stderr)
    sys.exit(1)


def read_text(path: Path) -> str:
    try:
      return path.read_text(encoding="utf-8")
    except FileNotFoundError:
      fail(f"file not found: {path}")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{payload}"


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_asset(raw: str, input_dir: Path) -> Path | None:
    raw_path = Path(raw)
    if raw_path.is_absolute():
        mime = mimetypes.guess_type(raw_path.name)[0] or ""
        if raw_path.is_file() and mime.startswith(("image/", "video/")):
            return raw_path
        return None
    if ".." in raw_path.parts:
        return None
    allowed_roots = [
        (input_dir / "media").resolve(),
        IMAGE_DIR.resolve(),
    ]
    candidates = []
    candidates.append((input_dir / raw_path).resolve())
    candidates.append((SKILL_DIR / raw_path).resolve())
    for candidate in candidates:
        mime = mimetypes.guess_type(candidate.name)[0] or ""
        if candidate.is_file() and mime.startswith(("image/", "video/")) and any(is_relative_to(candidate, root) for root in allowed_roots):
            return candidate
    return None


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.startswith(" "):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body


def parse_page_ratio(raw: str | None) -> tuple[str, int, int, float]:
    value = (raw or "16:9").strip().replace("/", ":")
    allowed = {"16:9": (16, 9), "4:3": (4, 3)}
    if value not in allowed:
        fail("page_ratio must be either 16:9 or 4:3")
    width, height = allowed[value]
    return value, width, height, width / height


ALERT_ALIASES = {
    "note": "info",
    "info": "info",
    "tip": "tip",
    "important": "tip",
    "warning": "warning",
    "warn": "warning",
    "caution": "error",
    "error": "error",
    "danger": "error",
}

ALERT_LABELS = {
    "info": "信息",
    "tip": "提示",
    "warning": "警告",
    "error": "错误",
}


def normalize_alert_type(raw: str) -> str | None:
    return ALERT_ALIASES.get(raw.strip().lower())


def parse_slide_meta(raw: str) -> tuple[dict[str, str], str]:
    raw = raw.lstrip()
    if not raw.startswith("<!--"):
        return {}, raw
    end = raw.find("-->")
    if end == -1:
        return {}, raw
    comment = raw[4:end]
    if not comment.strip().startswith("slide"):
        return {}, raw
    meta: dict[str, str] = {}
    for line in comment.splitlines()[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, raw[end + 3 :].lstrip()


def extract_admonitions(raw: str, name: str) -> tuple[list[str], str]:
    pattern = re.compile(rf"::: {re.escape(name)}\n(.*?)\n:::", re.S)
    values = [match.group(1).strip() for match in pattern.finditer(raw)]
    raw = pattern.sub("", raw)
    return values, raw


def new_section(title: str) -> dict[str, object]:
    return {"title": title, "slides": []}


def parse_hierarchy(body: str) -> list[dict[str, object]]:
    heading_re = re.compile(r"^(## Section:|### Slide:|## Slide:)\s*(.+?)\s*$", flags=re.M)
    matches = list(heading_re.finditer(body))
    sections: list[dict[str, object]] = []
    current_section: dict[str, object] | None = None

    def ensure_section(title: str = "默认章节") -> dict[str, object]:
        nonlocal current_section
        if current_section is None:
            current_section = new_section(title)
            sections.append(current_section)
        return current_section

    for idx, match in enumerate(matches):
        kind = match.group(1)
        title = match.group(2).strip()
        if kind == "## Section:":
            current_section = new_section(title)
            sections.append(current_section)
            continue
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
        raw = body[start:end].strip()
        meta, raw = parse_slide_meta(raw)
        notes, raw = extract_admonitions(raw, "notes")
        section = ensure_section()
        slides = section["slides"]
        if not isinstance(slides, list):
            fail("internal parser error: section slides is not a list")
        slides.append({
            "title": title,
            "meta": meta,
            "notes": notes,
            "warnings": [],
            "body": raw.strip(),
            "heading": kind,
        })

    return [section for section in sections if isinstance(section.get("slides"), list) and section["slides"]]


def parse_slides(body: str) -> list[dict[str, object]]:
    slides: list[dict[str, object]] = []
    for section in parse_hierarchy(body):
        for slide in section["slides"]:
            if isinstance(slide, dict):
                slides.append(slide)
    return slides


def split_blocks(raw: str) -> list[dict[str, str]]:
    lines = raw.splitlines()
    blocks: list[dict[str, str]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            lang = line.strip()[3:].strip()
            body = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1
            blocks.append({"type": "fence", "lang": lang, "text": "\n".join(body)})
            continue
        alert_match = re.match(r"^:::\s*([A-Za-z_-]+)\s*$", line.strip())
        if alert_match:
            alert_type = normalize_alert_type(alert_match.group(1))
            if alert_type:
                body = []
                i += 1
                while i < len(lines) and not re.match(r"^:::\s*$", lines[i].strip()):
                    body.append(lines[i])
                    i += 1
                if i < len(lines):
                    i += 1
                blocks.append({"type": "alert", "alert_type": alert_type, "text": "\n".join(body).strip()})
                continue
        github_alert_match = re.match(r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$", line.strip(), flags=re.I)
        if github_alert_match:
            alert_type = normalize_alert_type(github_alert_match.group(1))
            body = []
            i += 1
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                body.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            if alert_type:
                blocks.append({"type": "alert", "alert_type": alert_type, "text": "\n".join(body).strip()})
                continue
        if line.startswith("|"):
            body = [line]
            i += 1
            while i < len(lines) and lines[i].startswith("|"):
                body.append(lines[i])
                i += 1
            blocks.append({"type": "table", "text": "\n".join(body)})
            continue
        if re.match(r"^\s*[-*]\s+", line):
            body = [line]
            i += 1
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                body.append(lines[i])
                i += 1
            blocks.append({"type": "list", "text": "\n".join(body)})
            continue
        if line.startswith("$$"):
            if line.strip().endswith("$$") and len(line.strip()) > 4:
                blocks.append({"type": "math", "text": line.strip()})
                i += 1
                continue
            body = [line]
            i += 1
            while i < len(lines) and not lines[i].startswith("$$"):
                body.append(lines[i])
                i += 1
            if i < len(lines):
                body.append(lines[i])
                i += 1
            blocks.append({"type": "math", "text": "\n".join(body)})
            continue
        if re.match(r"^!\[[^\]]+\]\([^)]+\)", line.strip()):
            blocks.append({"type": "media", "text": line.strip()})
            i += 1
            continue
        if line.startswith("###"):
            blocks.append({"type": "heading", "text": line})
            i += 1
            continue
        body = [line]
        i += 1
        while i < len(lines) and lines[i].strip():
            if lines[i].startswith(("```", "|", "$$", "###")) or re.match(r"^\s*[-*]\s+", lines[i]) or re.match(r"^!\[[^\]]+\]\([^)]+\)", lines[i].strip()):
                break
            body.append(lines[i])
            i += 1
        blocks.append({"type": "paragraph", "text": "\n".join(body)})
    return blocks


def block_score(block: dict[str, str]) -> int:
    kind = block["type"]
    text = block["text"]
    if kind == "table":
        return max(12, len(text.splitlines()) * 3)
    if kind == "list":
        return max(5, len(text.splitlines()) * 3)
    if kind == "media":
        return 11
    if kind == "fence":
        return 10 if block.get("lang") == "chart" else 6
    if kind == "math":
        return 5
    return max(3, len(text) // 70 + 2)


def split_large_block(block: dict[str, str]) -> list[dict[str, str]]:
    kind = block["type"]
    text = block["text"]
    if kind == "list":
        lines = [line for line in text.splitlines() if re.match(r"^\s*[-*]\s+", line)]
        if len(lines) <= 5:
            return [block]
        return [{"type": "list", "text": "\n".join(lines[idx : idx + 5])} for idx in range(0, len(lines), 5)]
    if kind == "table":
        rows = [row for row in text.splitlines() if row.strip()]
        if len(rows) <= 6:
            return [block]
        header = rows[:2] if len(rows) >= 2 and all(set(cell.strip()) <= {"-", ":"} for cell in rows[1].strip().strip("|").split("|")) else rows[:1]
        body = rows[len(header):]
        chunks = []
        rows_per_page = 4
        for idx in range(0, len(body), rows_per_page):
            chunks.append({"type": "table", "text": "\n".join(header + body[idx : idx + rows_per_page])})
        return chunks or [block]
    if kind == "paragraph" and len(text) > 850:
        sentences = re.split(r"(?<=[。！？.!?])\s+", text)
        chunks: list[str] = []
        current = ""
        for sentence in sentences:
            if current and len(current) + len(sentence) > 520:
                chunks.append(current.strip())
                current = ""
            current = (current + " " + sentence).strip()
        if current:
            chunks.append(current.strip())
        if len(chunks) > 1:
            return [{"type": "paragraph", "text": chunk} for chunk in chunks]
    return [block]


def chunk_blocks(blocks: list[dict[str, str]], split_mode: str) -> list[list[dict[str, str]]]:
    if split_mode == "false":
        return [blocks]
    paged_blocks = [part for block in blocks for part in split_large_block(block)]
    pages: list[list[dict[str, str]]] = []
    current: list[dict[str, str]] = []
    score = 0
    limit = 22
    for block in paged_blocks:
        next_score = block_score(block)
        if current and score + next_score > limit:
            pages.append(current)
            current = []
            score = 0
        current.append(block)
        score += next_score
    if current:
        pages.append(current)
    return pages or [[]]


def inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    return escaped


def render_table(text: str) -> str:
    rows = [row.strip().strip("|").split("|") for row in text.splitlines() if row.strip()]
    if len(rows) >= 2 and all(set(cell.strip()) <= {"-", ":"} for cell in rows[1]):
        header, body = rows[0], rows[2:]
    else:
        header, body = rows[0], rows[1:]
    parts = ["<div class=\"table-wrap\"><table><thead><tr>"]
    for cell in header:
        parts.append(f"<th>{inline_markdown(cell.strip())}</th>")
    parts.append("</tr></thead><tbody>")
    for row in body:
        parts.append("<tr>")
        for cell in row:
            parts.append(f"<td>{inline_markdown(cell.strip())}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table></div>")
    return "".join(parts)


def render_chart(text: str) -> str:
    pairs = []
    for line in text.splitlines():
        if ":" not in line:
            continue
        label, value = line.split(":", 1)
        try:
            pairs.append((label.strip(), float(value.strip())))
        except ValueError:
            continue
    if not pairs:
        return "<div class=\"chart empty\">No chart data</div>"
    max_value = max(value for _, value in pairs) or 1
    bars = []
    for idx, (label, value) in enumerate(pairs):
        width = max(8, int(value / max_value * 100))
        bars.append(
            f"<div class=\"chart-row\"><span>{inline_markdown(label)}</span>"
            f"<div class=\"bar\"><i style=\"width:{width}%\"></i></div>"
            f"<strong>{value:g}</strong></div>"
        )
    return "<div class=\"chart\">" + "".join(bars) + "</div>"


def latex_to_html(expr: str) -> str:
    expr = expr.strip()
    functions = {"cos", "sin", "tan", "log", "ln", "max", "min"}
    greek = {
        "alpha": "α",
        "beta": "β",
        "gamma": "γ",
        "delta": "δ",
        "Delta": "Δ",
        "theta": "θ",
        "lambda": "λ",
        "mu": "μ",
        "pi": "π",
        "phi": "φ",
        "varphi": "φ",
        "omega": "ω",
        "Omega": "Ω",
    }
    symbols = {
        "times": "×",
        "cdot": "·",
        "leq": "≤",
        "geq": "≥",
        "neq": "≠",
        "approx": "≈",
        "pm": "±",
    }

    def read_group(value: str, start: int) -> tuple[str, int]:
        if start >= len(value) or value[start] != "{":
            return "", start
        depth = 1
        body: list[str] = []
        i = start + 1
        while i < len(value) and depth:
            char = value[i]
            if char == "{":
                depth += 1
                body.append(char)
            elif char == "}":
                depth -= 1
                if depth:
                    body.append(char)
            else:
                body.append(char)
            i += 1
        return "".join(body), i

    def read_script(value: str, start: int) -> tuple[str, int]:
        if start < len(value) and value[start] == "{":
            return read_group(value, start)
        if start < len(value):
            return value[start], start + 1
        return "", start

    def render_inner(value: str) -> str:
        out: list[str] = []
        i = 0
        while i < len(value):
            char = value[i]
            if char.isspace():
                out.append(" ")
                i += 1
                continue
            if char == "\\":
                match = re.match(r"\\([A-Za-z]+)", value[i:])
                if not match:
                    out.append(html.escape(char))
                    i += 1
                    continue
                name = match.group(1)
                i += len(match.group(0))
                if name == "sqrt":
                    body, i = read_group(value, i)
                    out.append(f"<span class=\"math-sqrt\"><span class=\"math-radical\">√</span><span class=\"math-radicand\">{render_inner(body)}</span></span>")
                elif name == "frac":
                    numerator, i = read_group(value, i)
                    denominator, i = read_group(value, i)
                    out.append(f"<span class=\"math-frac\"><span>{render_inner(numerator)}</span><span>{render_inner(denominator)}</span></span>")
                elif name in functions:
                    out.append(f"<span class=\"math-fn\">{html.escape(name)}</span>")
                elif name in greek:
                    out.append(f"<var>{html.escape(greek[name])}</var>")
                elif name in symbols:
                    out.append(f"<span class=\"math-op\">{html.escape(symbols[name])}</span>")
                else:
                    out.append(html.escape(name))
                continue
            if char in "^_":
                body, i = read_script(value, i + 1)
                tag = "sup" if char == "^" else "sub"
                out.append(f"<{tag}>{render_inner(body)}</{tag}>")
                continue
            if char.isalpha() or char in "αβγδθλμπφωΩΔ":
                out.append(f"<var>{html.escape(char)}</var>")
                i += 1
                continue
            if char in "=+-×·*/()[]{}":
                out.append(f"<span class=\"math-op\">{html.escape(char)}</span>" if char in "=+-×·*/" else html.escape(char))
                i += 1
                continue
            out.append(html.escape(char))
            i += 1
        return "".join(out)

    return render_inner(expr)


def render_formula(text: str, section_index: int | None = None, formula_counters: dict[int, int] | None = None) -> str:
    formulas: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4:
            formulas.append(stripped[2:-2].strip())
        else:
            stripped = stripped.replace("$$", "").strip()
            if stripped:
                formulas.append(stripped)
    if not formulas:
        return ""
    rows: list[str] = []
    for formula in formulas:
        number = ""
        if section_index is not None and formula_counters is not None:
            formula_counters[section_index] = formula_counters.get(section_index, 0) + 1
            number = f"（{section_index}-{formula_counters[section_index]}）"
        rows.append(
            f"<div class=\"formula-row\">"
            f"<div class=\"formula-line\">{latex_to_html(formula)}</div>"
            f"<div class=\"formula-number\">{html.escape(number)}</div>"
            f"</div>"
        )
    lines = "".join(rows)
    return f"<div class=\"formula\">{lines}</div>"


def render_media(line: str, input_dir: Path, media_warnings: list[str]) -> str:
    match = re.match(r"^!\[([^\]]+)\]\(([^)]+)\)", line)
    if not match:
        return f"<p>{inline_markdown(line)}</p>"
    label, raw_path = match.group(1), match.group(2)
    is_video = label.lower().startswith("video:")
    label_text = label.split(":", 1)[1] if is_video and ":" in label else label
    path = resolve_asset(raw_path, input_dir)
    if is_video:
        if path is None:
            media_warnings.append(f"video fallback: missing file {raw_path}")
            return f"<figure class=\"video-fallback\"><div>VIDEO</div><figcaption>{inline_markdown(label_text)}<br><code>{html.escape(raw_path)}</code></figcaption></figure>"
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 20:
            media_warnings.append(f"video fallback: {raw_path} is {size_mb:.2f} MB")
            return f"<figure class=\"video-fallback\"><div>VIDEO</div><figcaption>{inline_markdown(label_text)}<br><a href=\"{html.escape(str(path))}\">external media</a></figcaption></figure>"
        return f"<video controls src=\"{data_uri(path)}\"></video><p class=\"caption\">{inline_markdown(label_text)}</p>"
    if path is None:
        media_warnings.append(f"image missing: {raw_path}")
        return f"<figure class=\"missing-media\"><div>IMAGE MISSING</div><figcaption>{inline_markdown(label_text)}<br><code>{html.escape(raw_path)}</code></figcaption></figure>"
    return f"<figure><img src=\"{data_uri(path)}\" alt=\"{html.escape(label_text)}\"><figcaption>{inline_markdown(label_text)}</figcaption></figure>"


def render_alert(kind: str, text: str) -> str:
    alert_type = normalize_alert_type(kind) or "info"
    label = ALERT_LABELS[alert_type]
    body = inline_markdown(text.strip()) if text.strip() else ""
    return f"<aside class=\"alert alert-{html.escape(alert_type)}\"><strong>{html.escape(label)}</strong><p>{body}</p></aside>"


def render_block(
    block: dict[str, str],
    input_dir: Path,
    media_warnings: list[str],
    section_index: int | None = None,
    formula_counters: dict[int, int] | None = None,
) -> str:
    kind = block["type"]
    text = block["text"]
    if kind == "table":
        return render_table(text)
    if kind == "list":
        items = [re.sub(r"^\s*[-*]\s+", "", line).strip() for line in text.splitlines()]
        return "<ul>" + "".join(f"<li>{inline_markdown(item)}</li>" for item in items) + "</ul>"
    if kind == "fence":
        if block.get("lang") == "chart":
            return render_chart(text)
        return f"<pre><code>{html.escape(text)}</code></pre>"
    if kind == "alert":
        return render_alert(block.get("alert_type", "info"), text)
    if kind == "math":
        return render_formula(text, section_index, formula_counters)
    if kind == "media":
        return render_media(text, input_dir, media_warnings)
    if kind == "heading":
        return f"<h3>{inline_markdown(text.lstrip('#').strip())}</h3>"
    return f"<p>{inline_markdown(text)}</p>"


def choose_layout(slide: dict[str, object], blocks: list[dict[str, str]], index: int) -> str:
    meta = slide["meta"] if isinstance(slide["meta"], dict) else {}
    explicit = meta.get("layout", "auto")
    if explicit != "auto":
        return explicit
    if index == 0:
        return "cover"
    kinds = {block["type"] for block in blocks}
    if "table" in kinds:
        return "table"
    if any(block["type"] == "fence" and block.get("lang") == "chart" for block in blocks):
        return "chart"
    if "media" in kinds:
        return "media-right"
    return "content"


def html_attrs(values: dict[str, object]) -> str:
    parts = []
    for key, value in values.items():
        parts.append(f'{key}="{html.escape(str(value), quote=True)}"')
    return " ".join(parts)


def render_cover_details(meta: dict[str, str]) -> str:
    labels = {
        "school": "汇报单位",
        "department": "部门",
        "author": "汇报人",
        "presenter": "汇报人",
        "reporter": "汇报人",
        "date": "日期",
        "location": "地点",
    }
    ordered_keys = ["school", "department", "author", "presenter", "reporter", "date", "location"]
    rows: list[tuple[str, str]] = []
    used: set[str] = set()
    for key in ordered_keys:
        value = meta.get(key, "").strip()
        if value:
            rows.append((labels[key], value))
            used.add(key)
    for key, value in meta.items():
        if not key.startswith("cover_"):
            continue
        clean_key = key.removeprefix("cover_").strip()
        clean_value = value.strip()
        if not clean_key or not clean_value or key in used:
            continue
        label = labels.get(clean_key, clean_key.replace("_", " "))
        rows.append((label, clean_value))
    if not rows:
        return ""
    items = "".join(
        f"<span><b>{html.escape(label)}</b><em>{html.escape(value)}</em></span>"
        for label, value in rows
    )
    return f"<div class=\"cover-details\">{items}</div>"


def render_page_section(
    record: dict[str, object],
    slide: dict[str, object],
    layout: str,
    chunk: list[dict[str, str]],
    input_dir: Path,
    media_warnings: list[str],
    deck_meta: dict[str, str],
    deck_subtitle: str,
    cover_logo_uri: str,
    cover_slogan_uri: str,
    logo_uri: str,
    closing_slogan_uri: str,
    closing_ribbon_uri: str,
    footer_uri: str,
    footer_logo_uri: str,
    formula_counters: dict[int, int],
) -> str:
    page_title = html.escape(str(slide["title"]))
    attrs = html_attrs({
        "data-section-index": record["section_index"],
        "data-section-title": record["section_title"],
        "data-logical-index": record["logical_index"],
        "data-logical-title": record["logical_title"],
        "data-physical-index": record["physical_index"],
        "data-global-index": record["global_index"],
        "data-page-id": record["page_id"],
        "data-page-label": record["page_label"],
        "data-layout": layout,
    })
    classes = f"slide layout-{html.escape(layout)}"
    if layout == "closing":
        return (
            f"<section class=\"{classes}\" {attrs}>"
            f"<div class=\"closing-stage\">"
            f"<div class=\"closing-band\"><img class=\"closing-slogan\" src=\"{closing_slogan_uri}\" alt=\"school slogan\"></div>"
            f"<img class=\"closing-ribbon\" src=\"{closing_ribbon_uri}\" alt=\"\">"
            f"<img class=\"closing-logo\" src=\"{logo_uri}\" alt=\"school logo\">"
            f"</div>"
            f"</section>"
        )
    section_number = int(record["section_index"])
    rendered_blocks = "".join(
        render_block(block, input_dir, media_warnings, section_number, formula_counters)
        for block in chunk
    )
    warnings = "".join(f"<aside class=\"warning\">{inline_markdown(w)}</aside>" for w in slide["warnings"])
    notes = "".join(f"<details class=\"notes\"><summary>Speaker notes</summary><p>{inline_markdown(n)}</p></details>" for n in slide["notes"])
    if layout == "cover":
        subtitle = deck_subtitle.strip()
        subtitle_html = f"<p class=\"cover-subtitle\">{html.escape(subtitle)}</p>" if subtitle else ""
        details = render_cover_details(deck_meta)
        return (
            f"<section class=\"{classes}\" {attrs}>"
            f"<img class=\"brand-logo\" src=\"{cover_logo_uri}\" alt=\"school logo\">"
            f"<div class=\"cover-hero\">"
            f"{subtitle_html}"
            f"<h1>{page_title}</h1>"
            f"<main class=\"cover-summary\">{warnings}{rendered_blocks}{notes}</main>"
            f"{details}"
            f"</div>"
            f"<img class=\"cover-slogan\" src=\"{cover_slogan_uri}\" alt=\"school slogan\">"
            f"</section>"
        )
    page_marker = f"<span>{html.escape(str(record['page_label']))}</span>"
    return (
        f"<section class=\"{classes}\" {attrs}>"
        f"<div class=\"slide-title\"><h2>{page_title}</h2>{page_marker}</div>"
        f"<main>{warnings}{rendered_blocks}{notes}</main>"
        f"<footer class=\"slide-footer\" aria-hidden=\"true\">"
        f"<img class=\"footer-band\" src=\"{footer_uri}\" alt=\"\">"
        f"<img class=\"footer-logo\" src=\"{footer_logo_uri}\" alt=\"\">"
        f"</footer>"
        f"</section>"
    )


def render_agenda_page_section(
    record: dict[str, object],
    section_titles: list[str],
    footer_uri: str,
    footer_logo_uri: str,
) -> str:
    attrs = html_attrs({
        "data-section-index": record["section_index"],
        "data-section-title": record["section_title"],
        "data-logical-index": record["logical_index"],
        "data-logical-title": record["logical_title"],
        "data-physical-index": record["physical_index"],
        "data-global-index": record["global_index"],
        "data-page-id": record["page_id"],
        "data-page-label": record["page_label"],
        "data-layout": "agenda",
    })
    items = []
    for idx, section_title in enumerate(section_titles, start=1):
        items.append(
            "<li>"
            f"<span>{idx:02d}</span>"
            f"<strong>{html.escape(section_title)}</strong>"
            "</li>"
        )
    return (
        f"<section class=\"slide layout-agenda\" {attrs}>"
        "<div class=\"agenda-kicker\">目录</div>"
        "<div class=\"agenda-head\"><h2>汇报路径</h2><p>CONTENT</p></div>"
        f"<ol class=\"agenda-list\">{''.join(items)}</ol>"
        "<div class=\"agenda-route\" aria-hidden=\"true\"><i></i><i></i><i></i></div>"
        f"<footer class=\"slide-footer\" aria-hidden=\"true\">"
        f"<img class=\"footer-band\" src=\"{footer_uri}\" alt=\"\">"
        f"<img class=\"footer-logo\" src=\"{footer_logo_uri}\" alt=\"\">"
        f"</footer>"
        f"</section>"
    )


def render_thumb_card(record: dict[str, object], attr_name: str, extra_class: str = "") -> str:
    layout = html.escape(str(record["layout"]))
    page_id = html.escape(str(record["page_id"]), quote=True)
    page_label = html.escape(str(record["page_label"]))
    logical_title = html.escape(str(record["logical_title"]))
    section_title = html.escape(str(record["section_title"]))
    label = f"{page_label} {logical_title}".strip()
    return (
        f"<button class=\"thumb-item {extra_class}\" {attr_name}=\"{page_id}\" data-page-index=\"{record['global_index']}\" aria-current=\"false\" aria-label=\"{html.escape(label, quote=True)}\">"
        f"<span class=\"thumb-label\">{page_label}</span>"
        f"<div class=\"thumb-real\" aria-hidden=\"true\"></div>"
        f"<div class=\"thumb-card layout-{layout}\" aria-hidden=\"true\">"
        f"<span>{page_label}</span><strong>{logical_title}</strong><em>{section_title}</em><i></i>"
        f"</div>"
        f"</button>"
    )


def render_deck(input_path: Path, max_size_mb: int) -> tuple[str, dict[str, object]]:
    text = read_text(input_path)
    meta, body = parse_frontmatter(text)
    hierarchy = parse_hierarchy(body)
    if not hierarchy:
        fail("no logical slides found; use headings like '## Section:' + '### Slide:' or old '## Slide: Title'")
    page_ratio_label, page_ratio_width, page_ratio_height, page_ratio_value = parse_page_ratio(meta.get("page_ratio"))
    logo_uri = data_uri(IMAGE_DIR / "logo-combined.png")
    header_icon_uri = data_uri(IMAGE_DIR / "school-icon-color.png")
    cover_logo_uri = data_uri(IMAGE_DIR / "logo-white.png")
    closing_bg_uri = data_uri(IMAGE_DIR / "gradient-cover.png")
    closing_slogan_uri = data_uri(IMAGE_DIR / "slogan-white-script.png")
    closing_ribbon_uri = data_uri(IMAGE_DIR / "decorative-footer-band.png")
    footer_uri = data_uri(IMAGE_DIR / "body-page-footer.png")
    footer_logo_uri = data_uri(IMAGE_DIR / "logo-white.png")
    wave_top_uri = data_uri(IMAGE_DIR / "decorative-wave-top.png")
    title = meta.get("title") or "School Presentation"
    subtitle = meta.get("subtitle") or ""
    input_dir = input_path.parent.resolve()
    media_warnings: list[str] = []
    page_sections: list[str] = []
    page_records: list[dict[str, object]] = []
    manifest_sections: list[dict[str, object]] = []
    logical_count = 0
    display_logical_count = 0
    formula_counters: dict[int, int] = {}
    layouts_used: list[str] = []
    agenda_inserted = False
    agenda_section_titles = [str(section["title"]) for section in hierarchy]
    for section_index, section in enumerate(hierarchy, start=1):
        section_title = str(section["title"])
        section_manifest: dict[str, object] = {
            "section_index": section_index,
            "section_title": section_title,
            "logical_slides": [],
        }
        slides = section["slides"] if isinstance(section["slides"], list) else []
        for slide in slides:
            if not isinstance(slide, dict):
                continue
            logical_count += 1
            body_text = str(slide["body"])
            blocks = split_blocks(body_text)
            layout = choose_layout(slide, blocks, logical_count - 1)
            layouts_used.append(layout)
            numbered_layout = layout not in {"cover", "closing"}
            if numbered_layout:
                display_logical_count += 1
                display_logical_label = str(display_logical_count)
            elif layout == "closing":
                display_logical_label = "封底"
            else:
                display_logical_label = "封面"
            split_mode = "auto"
            if isinstance(slide["meta"], dict):
                split_mode = slide["meta"].get("split", "auto")
            chunks = chunk_blocks(blocks, split_mode)
            slide_manifest: dict[str, object] = {
                "section_index": section_index,
                "section_title": section_title,
                "logical_index": logical_count,
                "display_logical_index": display_logical_label,
                "logical_title": str(slide["title"]),
                "physical_pages": [],
                "reveal_steps": [],
            }
            for page_idx, chunk in enumerate(chunks, start=1):
                global_index = len(page_records) + 1
                if numbered_layout:
                    page_label = f"{display_logical_count}.{page_idx}"
                elif layout == "closing":
                    page_label = "封底"
                else:
                    page_label = "封面"
                record: dict[str, object] = {
                    "page_id": f"p{global_index}",
                    "page_label": page_label,
                    "section_index": section_index,
                    "section_title": section_title,
                    "logical_index": logical_count,
                    "display_logical_index": display_logical_label,
                    "logical_title": str(slide["title"]),
                    "physical_index": page_idx,
                    "global_index": global_index,
                    "layout": layout,
                    "reveal_steps": [],
                }
                page_sections.append(render_page_section(
                    record,
                    slide,
                    layout,
                    chunk,
                    input_dir,
                    media_warnings,
                    meta,
                    subtitle,
                    cover_logo_uri,
                    closing_slogan_uri,
                    logo_uri,
                    closing_slogan_uri,
                    closing_ribbon_uri,
                    footer_uri,
                    footer_logo_uri,
                    formula_counters,
                ))
                page_records.append(record)
                physical_pages = slide_manifest["physical_pages"]
                if isinstance(physical_pages, list):
                    physical_pages.append(dict(record))
            logical_slides = section_manifest["logical_slides"]
            if isinstance(logical_slides, list):
                logical_slides.append(slide_manifest)
                if layout == "cover" and not agenda_inserted:
                    agenda_inserted = True
                    logical_count += 1
                    global_index = len(page_records) + 1
                    agenda_record: dict[str, object] = {
                        "page_id": f"p{global_index}",
                        "page_label": "目录",
                        "section_index": section_index,
                        "section_title": section_title,
                        "logical_index": logical_count,
                        "display_logical_index": "目录",
                        "logical_title": "汇报路径",
                        "physical_index": 1,
                        "global_index": global_index,
                        "layout": "agenda",
                        "reveal_steps": [],
                    }
                    page_sections.append(render_agenda_page_section(
                        agenda_record,
                        agenda_section_titles,
                        footer_uri,
                        footer_logo_uri,
                    ))
                    page_records.append(agenda_record)
                    logical_slides.append({
                        "section_index": section_index,
                        "section_title": section_title,
                        "logical_index": logical_count,
                        "display_logical_index": "目录",
                        "logical_title": "汇报路径",
                        "physical_pages": [dict(agenda_record)],
                        "reveal_steps": [],
                    })
        manifest_sections.append(section_manifest)
    physical_count = len(page_records)
    css = """
:root{__RATIO_CSS__;--slide-design-width:1280px;--slide-design-height:calc(1280px / var(--slide-ratio));--slide-max-width:1280px;--rail-width:260px;--resizer-width:8px;--green:#579E40;--teal:#549183;--blue:#0084CC;--deep:#0E2841;--paper:#fff;--soft:#E8E8E8;--gold:#F2BA02;--line:#d8e6ec;--shadow:0 18px 42px rgba(14,40,65,.16)}
*{box-sizing:border-box}body{margin:0;background:#eef3f5;color:var(--deep);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans SC",Arial,sans-serif;letter-spacing:0;overflow:hidden;-webkit-text-size-adjust:100%;text-size-adjust:100%}
button{font:inherit;color:inherit}.app{height:100vh;display:grid;grid-template-rows:auto 1fr}.app[data-view="playback"]{display:block}.app[data-view="playback"] .app-top{display:none}.app-top{height:56px;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:0 18px;border-bottom:1px solid var(--line);background:rgba(255,255,255,.94);backdrop-filter:blur(10px);overflow:hidden}.brand-lockup{display:grid;grid-template-columns:42px minmax(0,1fr);align-items:center;gap:12px;min-width:0;max-width:min(620px,calc(100vw - 360px));height:100%}.brand-lockup img{width:42px;max-height:38px;object-fit:contain;box-shadow:none;border-radius:0;background:transparent}.brand-text{min-width:0;display:grid;gap:2px}.brand-title{display:block;color:#0056A8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.15;font-size:15px}.brand-context{display:block;min-width:0;font-size:11px;line-height:1.2;color:#58717c;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.top-actions{display:flex;align-items:center;gap:8px;flex:0 0 auto}.icon-btn{border:1px solid var(--line);background:#fff;border-radius:6px;padding:7px 12px;cursor:pointer}.icon-btn.primary{background:linear-gradient(90deg,var(--green),var(--blue));color:#fff;border:0}.current-page-chip{min-width:78px;text-align:center;color:#0056A8;font-weight:700}
.view{min-height:0}.view[hidden]{display:none!important}.workspace{display:grid;grid-template-columns:var(--rail-width) var(--resizer-width) minmax(0,1fr);height:calc(100vh - 56px);min-height:0}.thumbnail-rail{border-right:1px solid var(--line);background:#f8fbfc;overflow:auto;padding:12px}.rail-resizer{position:relative;border:0;border-left:1px solid var(--line);border-right:1px solid var(--line);background:linear-gradient(180deg,#f7fbfc,#edf4f6);cursor:col-resize;padding:0}.rail-resizer::before{content:"";position:absolute;left:50%;top:50%;width:3px;height:52px;border-radius:99px;background:linear-gradient(180deg,var(--green),var(--blue));transform:translate(-50%,-50%);opacity:.55}.rail-resizer:hover::before,.rail-resizer.is-dragging::before{opacity:1}.drawer-handle{display:none}.rail-section{margin:0 0 16px}.rail-section-title{margin:0 0 8px;font-size:12px;color:#0056A8;text-transform:none}.rail-logical-title{margin:10px 0 6px;font-size:13px;color:#466;font-weight:700}.rail-pages{display:grid;gap:8px}.thumb-item{position:relative;display:grid;grid-template-columns:42px 1fr;align-items:center;gap:8px;width:100%;border:1px solid transparent;background:transparent;border-radius:8px;padding:6px;text-align:left;cursor:pointer}.thumb-item[aria-current="true"],.thumb-item.is-active{border-color:var(--blue);background:#fff;box-shadow:0 8px 20px rgba(0,132,204,.12)}.thumb-label{font-size:12px;font-weight:800;color:#fff;background:var(--green);border-radius:4px;text-align:center;padding:4px 0}.thumb-real{position:relative;display:grid;place-items:center;aspect-ratio:var(--slide-aspect);overflow:hidden;border:1px solid var(--line);border-radius:5px;background:#fff;pointer-events:none}.thumb-card{display:none;aspect-ratio:var(--slide-aspect);border:1px solid var(--line);border-radius:5px;background:linear-gradient(135deg,#fff,#edf7fb);padding:8px;overflow:hidden;pointer-events:none}.thumb-card span{display:inline-block;font-size:11px;font-weight:800;color:#fff;background:var(--blue);border-radius:3px;padding:2px 6px}.thumb-card strong{display:block;margin-top:8px;font-size:12px;line-height:1.22;color:#0056A8}.thumb-card em{display:block;margin-top:4px;font-style:normal;font-size:10px;color:#60757e}.thumb-card i{display:block;margin-top:8px;height:5px;background:linear-gradient(90deg,var(--green),var(--blue),var(--gold));border-radius:99px}.layout-cover.thumb-card,.layout-section.thumb-card{background:linear-gradient(135deg,var(--green),var(--blue));color:#fff}.layout-cover.thumb-card strong,.layout-cover.thumb-card em,.layout-section.thumb-card strong,.layout-section.thumb-card em{color:#fff}.layout-agenda.thumb-card{background:linear-gradient(90deg,#fafdff 0 36%,var(--deep) 36%);color:#fff}.layout-agenda.thumb-card strong,.layout-agenda.thumb-card em{color:#fff}.layout-table.thumb-card{background:repeating-linear-gradient(180deg,#fff 0 17px,#e9f4f7 17px 18px)}.layout-chart.thumb-card i{height:22px;background:linear-gradient(90deg,var(--green) 68%,#e4f0f4 68%)}.layout-media-right.thumb-card,.layout-media-left.thumb-card{background:linear-gradient(90deg,#fff 0 54%,#dfeff4 54%)}.layout-quote.thumb-card{background:linear-gradient(135deg,#fff 0 76%,#f9e9a8 76%)}.layout-closing.thumb-card{background:linear-gradient(135deg,#fff 0 45%,var(--blue) 45%,var(--green) 72%,#fff 72%)}
.preview-pane{min-width:0;display:grid;grid-template-rows:1fr auto;padding:18px;gap:12px;overflow:hidden}.preview-stage{place-self:stretch;width:100%;height:100%;min-height:0;display:grid;place-items:center;overflow:hidden}.preview-stage,.playback-stage{position:relative}.slide-scale-shell{position:relative;width:var(--scaled-slide-width,var(--slide-design-width));height:var(--scaled-slide-height,var(--slide-design-height));overflow:hidden;background:#fff;contain:paint}.preview-stage .slide-scale-shell,.playback-stage .slide-scale-shell{box-shadow:var(--shadow);outline:1px solid rgba(14,40,65,.18);outline-offset:0}.thumb-real .slide-scale-shell{outline:0;box-shadow:none}.preview-stage.is-transitioning .slide-scale-shell,.playback-stage.is-transitioning .slide-scale-shell{transition:opacity .18s ease}.preview-stage.is-fade-out .slide-scale-shell,.playback-stage.is-fade-out .slide-scale-shell{opacity:.82}.preview-stage.is-fade-in .slide-scale-shell,.playback-stage.is-fade-in .slide-scale-shell{animation:stageFadeIn .18s ease both}@keyframes stageFadeIn{from{opacity:.82}to{opacity:1}}.slide-scale-shell .slide{position:absolute;left:0;top:0;width:var(--slide-design-width);height:var(--slide-design-height);max-width:none;transform:scale(var(--stage-scale,1));transform-origin:top left;pointer-events:none}.preview-meta{display:flex;align-items:center;justify-content:space-between;color:#4f6874;font-size:13px}.overview{height:calc(100vh - 56px);overflow:auto;padding:20px 24px;background:#f4f8fa}.overview-toolbar{display:flex;align-items:center;justify-content:space-between;margin:0 0 18px}.overview-grid{display:grid;gap:22px}.section-group{border-top:4px solid var(--blue);background:#fff;padding:14px;border-radius:8px;box-shadow:0 10px 28px rgba(14,40,65,.08)}.section-title{margin:0 0 12px;color:#0056A8}.overview-pages{display:grid;grid-template-columns:repeat(auto-fill,minmax(178px,1fr));gap:12px}.overview-tile{display:grid;gap:7px;border:1px solid var(--line);border-radius:8px;background:#fff;padding:8px;text-align:left;cursor:pointer}.overview-tile.section-first{border-top:5px solid var(--green)}.overview-tile[aria-current="true"],.overview-tile.is-active{border-color:var(--blue);box-shadow:0 10px 28px rgba(0,132,204,.15)}.overview-tile .thumb-real{width:100%}.overview-tile b{font-size:12px;color:#0056A8}.overview-tile span{font-size:11px;color:#60757e}.playback{position:fixed;inset:0;z-index:50;height:100vh;background:#071923;display:grid;place-items:center;cursor:none}.playback-stage{width:100vw;height:100vh;display:grid;place-items:center;overflow:hidden}.progress{position:fixed;left:0;right:0;top:0;height:4px;background:rgba(255,255,255,.18);z-index:80}.progress i{display:block;width:0;height:100%;background:linear-gradient(90deg,var(--green),var(--blue));transition:width .2s}.playback-zone{position:fixed;top:0;bottom:0;border:0;background:transparent;color:transparent;cursor:pointer;z-index:60}.playback-zone.prev{left:0;width:25vw}.playback-zone.center{left:25vw;width:50vw}.playback-zone.next{right:0;width:25vw}.playback-toolbar{position:fixed;left:50%;bottom:max(22px,env(safe-area-inset-bottom));transform:translate(-50%,10px) scale(.96);display:flex;align-items:center;gap:6px;padding:7px;border:1px solid rgba(255,255,255,.2);border-radius:999px;background:rgba(8,25,35,.72);backdrop-filter:blur(18px) saturate(140%);box-shadow:0 18px 48px rgba(0,0,0,.3),inset 0 1px 0 rgba(255,255,255,.18);opacity:0;pointer-events:none;transition:opacity .18s,transform .18s;z-index:85}.playback-control,.playback-exit,.playback-page-pill{height:38px;border:1px solid rgba(255,255,255,.16);border-radius:999px;background:rgba(255,255,255,.1);color:#fff;box-shadow:inset 0 1px 0 rgba(255,255,255,.14)}.playback-control{width:38px;display:grid;place-items:center;padding:0;font-size:24px;line-height:1;cursor:pointer}.playback-control:hover,.playback-exit:hover{background:rgba(255,255,255,.18)}.playback-page-pill{display:grid;place-items:center;min-width:64px;padding:0 14px;font-weight:800;color:#fff;background:linear-gradient(90deg,rgba(87,158,64,.86),rgba(0,132,204,.86));letter-spacing:0}.playback-exit{padding:0 14px;font-size:12px;font-weight:800;letter-spacing:.08em;cursor:pointer}.playback.show-ui{cursor:default}.playback.show-ui .playback-toolbar{opacity:1;pointer-events:auto;transform:translate(-50%,0) scale(1)}
.page-source{display:none}.deck{width:100%;display:grid;justify-items:center;gap:28px;padding:28px 0}.slide{position:relative;width:min(calc(100vw - 32px),calc((100vh - 56px) * var(--slide-ratio)),var(--slide-max-width));aspect-ratio:var(--slide-aspect);height:auto;padding:4.3% 6% 8.2%;display:grid;grid-template-rows:auto auto 1fr;overflow:hidden;isolation:isolate;background:linear-gradient(115deg,#ffffff 0%,#ffffff 58%,#edf7fb 100%);-webkit-text-size-adjust:100%;text-size-adjust:100%}
.slide::before{content:"";position:absolute;left:0;top:0;width:16px;height:100%;background:linear-gradient(180deg,var(--green),var(--blue));z-index:0}.slide::after{content:"";position:absolute;right:4%;top:2.8%;width:48%;height:8%;background:url("__WAVE_TOP__") right top/contain no-repeat;opacity:.22;z-index:0;pointer-events:none}.slide>*{position:relative;z-index:1}
.brand-logo{width:min(18%,180px);height:auto;object-fit:contain;align-self:flex-start;box-shadow:none;border-radius:0;background:transparent}.slide-title{position:relative;display:flex;align-items:end;justify-content:space-between;gap:24px;margin:1.5% 0 2%;border-bottom:3px solid var(--blue);padding-bottom:10px}
.slide-title::before{content:"";position:absolute;right:74px;bottom:-6px;width:118px;height:3px;background:linear-gradient(90deg,var(--green),var(--blue))}.slide-title::after{content:"";position:absolute;right:0;top:-9px;width:72px;height:10px;background:linear-gradient(90deg,var(--green) 0 24px,transparent 24px 31px,var(--blue) 31px 55px,transparent 55px 62px,var(--gold) 62px 72px);opacity:.9}
.slide-title h2{font-size:44px;line-height:1.08;margin:0;color:#0056A8;font-weight:800}.slide-title span{font-size:16px;color:#fff;background:var(--green);padding:5px 10px;border-radius:4px;min-width:42px;text-align:center}
main.slide-content,.slide main{min-height:0;overflow:hidden;font-size:28px;line-height:1.38;width:100%;max-width:none;justify-self:stretch}
.layout-cover{grid-template-rows:auto 1fr;padding:5.3% 7.2% 8.2%;color:#fff;background:radial-gradient(circle at 76% 20%,rgba(255,255,255,.2),transparent 28%),linear-gradient(115deg,rgba(87,158,64,.96),rgba(0,132,204,.96)),#0084CC}
.layout-cover::before{display:none}
.layout-cover::after{right:5.2%;top:auto;bottom:23%;width:54%;height:9%;opacity:.23;filter:brightness(0) invert(1)}
.layout-cover .brand-logo{width:min(31%,310px);max-width:310px}
.cover-hero{align-self:start;display:grid;gap:16px;width:min(76%,900px);margin-top:3.2%}
.cover-subtitle{margin:0;color:rgba(255,255,255,.9);font-size:30px;font-weight:650;line-height:1.18}
.cover-hero h1{margin:0;color:#fff;font-size:76px;line-height:1.02;font-weight:850;letter-spacing:0;text-wrap:balance}
.cover-summary{margin-top:12px;max-width:760px!important;color:rgba(255,255,255,.94);font-size:28px!important;line-height:1.42!important}
.cover-summary p{margin:0}.cover-details{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px 28px;margin-top:4px;padding-top:14px;width:min(70%,820px);border-top:1px solid rgba(255,255,255,.38);color:rgba(255,255,255,.95);font-size:18px}.cover-details span{display:grid;grid-template-columns:max-content minmax(0,1fr);align-items:baseline;gap:9px;min-width:0}.cover-details span:first-child{grid-column:1 / -1}.cover-details b{font-weight:700;color:rgba(255,255,255,.72);white-space:nowrap}.cover-details em{font-style:normal;font-weight:650;color:#fff;min-width:0}.cover-slogan{position:absolute;right:7%;bottom:7.6%;width:min(27%,330px);height:auto;max-height:122px;object-fit:contain;box-shadow:none;border-radius:0;background:transparent}.layout-cover .slide-footer{display:none}.layout-cover figure{margin:.8em 0 0}.layout-cover figure img{max-width:52%;max-height:216px;box-shadow:none;border-radius:4px}.layout-cover figcaption{display:none}
.layout-agenda{padding:0;color:#fff;background:linear-gradient(90deg,#fafdff 0 34%,#0e2841 34% 100%)}.layout-agenda::before{left:34%;top:0;width:2px;height:100%;background:linear-gradient(180deg,var(--green),var(--gold),var(--blue))}.layout-agenda::after{right:3.5%;top:6%;width:42%;height:9%;opacity:.16;filter:brightness(0) invert(1)}.agenda-kicker{position:absolute;left:7%;top:9%;display:inline-grid;place-items:center;width:104px;height:104px;border:2px solid rgba(0,132,204,.28);border-radius:50%;color:#0056A8;font-size:30px;font-weight:850}.agenda-head{position:absolute;left:7%;top:29%;width:23%;display:grid;gap:18px;color:#0056A8}.agenda-head h2{margin:0;font-size:58px;line-height:1.04;font-weight:850}.agenda-head p{margin:0;width:max-content;padding:8px 13px;background:#eaf5f8;color:#0E2841;border-left:7px solid var(--gold);font-size:18px;font-weight:850}.agenda-list{position:absolute;left:42%;right:7%;top:13%;bottom:18%;display:grid;align-content:center;gap:18px;margin:0;padding:0;list-style:none}.agenda-list li{display:grid;grid-template-columns:92px minmax(0,1fr);align-items:center;gap:24px;min-height:92px;border-bottom:1px solid rgba(255,255,255,.2)}.agenda-list li:first-child{border-top:1px solid rgba(255,255,255,.2)}.agenda-list span{font-family:Georgia,"Times New Roman",serif;font-size:54px;line-height:1;color:rgba(242,186,2,.94);font-weight:700}.agenda-list strong{display:block;min-width:0;color:#fff;font-size:50px;line-height:1.08;font-weight:850}.agenda-route{position:absolute;left:36.6%;top:17%;bottom:19%;display:grid;align-content:space-between}.agenda-route i{display:block;width:18px;height:18px;border:4px solid var(--gold);border-radius:50%;background:#0E2841;box-shadow:0 0 0 8px rgba(242,186,2,.12)}.layout-agenda .slide-footer::before{left:34%;background:linear-gradient(90deg,var(--gold),rgba(0,132,204,.58),transparent)}
.layout-closing{padding:0;background:#fff}.layout-closing::before,.layout-closing::after,.layout-closing .slide-title,.layout-closing main,.layout-closing .slide-footer,.layout-closing .brand-logo{display:none}.layout-closing .closing-stage{position:absolute;inset:0;overflow:hidden;background:#fff}.layout-closing .closing-band{position:absolute;left:0;right:0;top:30%;height:31%;background:url("__CLOSING_BG__") center/cover no-repeat}.layout-closing .closing-slogan{position:absolute;left:53%;top:44%;width:min(27%,340px);transform:translate(-50%,-50%);height:auto;box-shadow:none;border-radius:0;background:transparent}.layout-closing .closing-ribbon{position:absolute;left:0;right:0;top:57%;width:100%;height:19%;object-fit:fill;box-shadow:none;border-radius:0;background:transparent}.layout-closing .closing-logo{position:absolute;left:50%;bottom:9%;width:min(30%,380px);transform:translateX(-50%);height:auto;box-shadow:none;border-radius:0;background:transparent}
.slide p{margin:0 0 28px}.slide ul{margin:6px 0 28px;padding-left:34px}.slide li{margin:8px 0}.slide h3{position:relative;margin:15px 0 13px;padding-left:18px;color:#0056A8}.slide h3::before{content:"";position:absolute;left:0;top:8px;width:8px;height:29px;background:linear-gradient(180deg,var(--green),var(--blue));border-radius:2px}.slide strong{color:#0056A8}.slide code{font-size:18px;line-height:1.25;background:#eef7fb;padding:2px 5px;border-radius:4px}
.table-wrap{position:relative;overflow:auto;border:1px solid #d8e6ec;border-radius:6px;background:#fff;box-shadow:0 12px 28px rgba(14,40,65,.08)}.table-wrap::before,.chart::before{content:"";position:absolute;right:0;top:0;width:74px;height:5px;background:linear-gradient(90deg,var(--green),var(--blue));z-index:2}table{width:100%;border-collapse:collapse;font-size:.84em}th{background:#0084CC;color:#fff}th,td{padding:13px 14px;border-bottom:1px solid #dfe9ee;text-align:left;vertical-align:top}tr:nth-child(even) td{background:#f7fbfc}
figure{margin:24px 0;max-width:100%;display:grid;justify-items:center;align-content:start}img,video{max-width:100%;max-height:346px;object-fit:contain;border-radius:6px;background:#fff;box-shadow:0 14px 32px rgba(14,40,65,.13)}figcaption,.caption{width:100%;font-size:21px;line-height:1.3;color:#4b6470;margin-top:8px;text-align:center}
.layout-media-right main,.layout-media-left main,.layout-media-center main,.layout-media-compare main,.layout-media-chart main{display:grid;gap:18px;align-content:start;min-width:0}.layout-media-right main,.layout-media-left main,.layout-media-chart main{justify-content:center}.layout-media-right main{grid-template-columns:minmax(440px,560px) minmax(240px,max-content);column-gap:52px;align-items:start}.layout-media-left main{grid-template-columns:minmax(240px,max-content) minmax(440px,560px);column-gap:52px;align-items:start}.layout-media-right main figure{grid-column:2;grid-row:1 / span 6;justify-self:center}.layout-media-right main > :not(figure){grid-column:1}.layout-media-left main figure{grid-column:1;grid-row:1 / span 6;justify-self:center}.layout-media-left main > :not(figure){grid-column:2}.layout-media-left main figure,.layout-media-right main figure{width:max-content;max-width:430px}.layout-media-left main img,.layout-media-right main img{max-width:430px;max-height:331px}.layout-media-center main{grid-template-columns:1fr;justify-items:center;text-align:center}.layout-media-center main figure{width:min(76%,780px)}.layout-media-center main figure img{max-height:389px}.layout-media-compare main{grid-template-columns:repeat(2,max-content);justify-content:center;column-gap:52px;row-gap:14px;align-content:start}.layout-media-compare main figure:nth-of-type(1){grid-column:1}.layout-media-compare main figure:nth-of-type(2){grid-column:2}.layout-media-compare main figure{width:max-content;max-width:380px;justify-self:center}.layout-media-compare main img{width:auto;max-width:380px;max-height:288px}.layout-media-compare main p,.layout-media-compare main ul,.layout-media-compare main ol,.layout-media-compare main .warning,.layout-media-compare main .notes{grid-column:1 / -1}.layout-media-chart main{grid-template-columns:minmax(260px,max-content) minmax(420px,560px);column-gap:52px;align-items:start}.layout-media-chart main .chart{grid-column:2;grid-row:1 / span 5}.layout-media-chart main figure{grid-column:1;grid-row:1 / span 5;width:max-content;max-width:430px;justify-self:center}.layout-media-chart main figure img{max-width:430px;max-height:331px}.layout-media-chart main p,.layout-media-chart main ul,.layout-media-chart main ol,.layout-media-chart main .warning,.layout-media-chart main .notes{grid-column:1 / -1}.layout-media-right main figure,.layout-media-left main figure,.layout-media-center main figure,.layout-media-compare main figure,.layout-media-chart main figure{margin:0}.layout-media-right main > :not(figure):not(.notes):not(.warning),.layout-media-left main > :not(figure):not(.notes):not(.warning),.layout-media-center main > :not(figure):not(.notes):not(.warning),.layout-media-compare main > :not(figure):not(.chart):not(.notes):not(.warning),.layout-media-chart main > :not(figure):not(.chart):not(.notes):not(.warning){min-width:0}
.layout-media-compare main p{font-size:.86em;line-height:1.34;margin-top:2px;text-align:center}
.chart{position:relative;display:grid;gap:12px;background:#fff;border:1px solid #d8e6ec;border-radius:6px;padding:24px;box-shadow:0 12px 28px rgba(14,40,65,.08)}.chart-row{display:grid;grid-template-columns:190px 1fr 70px;gap:14px;align-items:center;font-size:.86em}.bar{height:24px;background:#e3eff3;border-radius:999px;overflow:hidden}.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--green),var(--blue))}
.formula{position:relative;display:grid;gap:12px;margin:12px 0 24px;padding:18px 24px;background:#f7fbfc;border-radius:4px;font-family:Georgia,"Times New Roman",serif;font-size:1.16em;color:#0056A8}.formula-row{position:relative;display:flex;align-items:center;justify-content:center;min-height:1.55em;padding:0 6em}.formula-line{white-space:normal;line-height:1.5;text-align:center}.formula-number{position:absolute;right:0;top:50%;transform:translateY(-50%);font-family:"Noto Sans SC",Arial,sans-serif;font-size:.78em;color:#0E2841;white-space:nowrap}.formula-line var{font-style:italic}.math-fn{font-style:normal;font-family:Georgia,"Times New Roman",serif}.math-op{display:inline-block;margin:0 .18em}.math-sqrt{display:inline-flex;align-items:flex-start;vertical-align:-.18em;margin:0 .12em}.math-radical{font-size:1.22em;line-height:1.08;margin-right:-.04em}.math-radicand{display:inline-block;border-top:2px solid currentColor;padding:.04em .08em 0 .1em;line-height:1.05}.math-frac{display:inline-grid;grid-template-rows:auto auto;place-items:center;vertical-align:-.45em;margin:0 .14em}.math-frac span:first-child{border-bottom:1.5px solid currentColor;padding:0 .2em .05em}.math-frac span:last-child{padding:.05em .2em 0}
.alert{display:grid;gap:8px;margin:0 0 18px;padding:14px 16px;border-left:6px solid;border-radius:6px;background:#f7fbfc;font-size:25px;line-height:1.32;break-inside:avoid}.alert:last-child{margin-bottom:0}.alert strong{font-size:20px;line-height:1.1;letter-spacing:0;text-transform:none}.alert p{margin:0;line-height:1.34}.alert-info{border-color:#5b9bd5;background:#eef7ff;color:#164a78}.alert-tip{border-color:#5cb85c;background:#eef9ef;color:#2a5d2a}.alert-warning{border-color:#F2BA02;background:#fff8df;color:#675100}.alert-error{border-color:#d9534f;background:#fff1f0;color:#8d1f1f}.notes{display:none}.video-fallback,.missing-media{display:grid;grid-template-rows:auto auto;align-content:center;justify-items:center;row-gap:8px;width:100%;min-height:180px;padding:16px 20px;border:2px dashed #8ab5c8;border-radius:6px;background:#f5fbfd;text-align:center}.video-fallback div,.missing-media div{font-size:46px;line-height:1;font-weight:800;color:#0084CC}.video-fallback figcaption,.missing-media figcaption{margin:0;font-size:21px;line-height:1.3}.video-fallback code,.missing-media code{display:inline-block;margin-top:4px;font-size:18px;line-height:1.25}
.slide-footer{position:absolute;left:0;right:0;bottom:0;width:100%;z-index:2;pointer-events:none}.slide-footer::before{content:"";position:absolute;left:16px;right:0;top:-2px;height:2px;background:linear-gradient(90deg,rgba(87,158,64,.85),rgba(0,132,204,.45),transparent)}.footer-band{display:block;width:100%;height:auto;max-height:none;object-fit:fill;box-shadow:none;border-radius:0;background:transparent}.footer-logo{position:absolute;left:3.4%;bottom:12%;width:13.5%;min-width:118px;max-width:178px;height:auto;box-shadow:none;border-radius:0;background:transparent}
@media print{body{overflow:visible}.app-top,.thumbnail-rail,.rail-resizer,.drawer-handle,.preview-meta,.overview,.playback,.page-source{display:none!important}.workspace{display:block;height:auto}.preview-stage{width:100%;display:block}.slide-scale-shell{width:100%;height:auto}.slide-scale-shell .slide{position:relative;transform:none}.preview-stage .slide{page-break-after:always;width:100%;height:auto;box-shadow:none}}@media(max-width:1040px){:root{--rail-width:230px}.preview-pane{padding:14px}.brand-lockup{max-width:calc(100vw - 230px);grid-template-columns:38px minmax(0,1fr)}.brand-lockup img{width:38px;max-height:34px}.brand-context{display:none}.top-actions .icon-btn{padding:7px 10px}.thumb-item{grid-template-columns:36px 1fr;gap:6px}.thumb-label{font-size:11px}}@media(max-width:680px){body{overflow:hidden}.app-top{position:sticky;top:0;z-index:40;padding:0 10px}.workspace{grid-template-columns:1fr;height:calc(100vh - 56px);overflow:hidden}.thumbnail-rail{position:fixed;left:0;top:56px;bottom:0;width:min(84vw,330px);max-width:calc(100vw - 44px);z-index:45;border-right:1px solid var(--line);border-bottom:0;box-shadow:18px 0 46px rgba(14,40,65,.22);transform:translateX(calc(-100% - 2px));transition:transform .24s cubic-bezier(.22,1,.36,1);max-height:none}.app.rail-open .thumbnail-rail{transform:translateX(0)}.rail-resizer{display:none}.drawer-handle{position:fixed;left:0;top:50%;z-index:46;display:grid;place-items:center;width:34px;height:76px;border:1px solid rgba(0,132,204,.28);border-left:0;border-radius:0 16px 16px 0;background:linear-gradient(180deg,var(--green),var(--blue));color:#fff;font-weight:850;box-shadow:0 10px 28px rgba(14,40,65,.24);transform:translateY(-50%);cursor:pointer}.drawer-handle::before{content:"☰";font-size:20px;line-height:1}.app.rail-open .drawer-handle{left:min(84vw,330px);transform:translate(-34px,-50%);border-radius:16px;background:rgba(14,40,65,.86);backdrop-filter:blur(12px)}.preview-pane{height:100%;min-height:0;padding:12px 10px 10px}.preview-meta{font-size:12px}.thumb-real{display:none}.thumb-card{display:block}.overview{height:auto}.brand-title{font-size:13px}.current-page-chip{min-width:46px}.top-actions{gap:5px}.top-actions .icon-btn{padding:7px 8px}}
"""
    css = css.replace("__RATIO_CSS__", f"--slide-aspect:{page_ratio_width} / {page_ratio_height};--slide-ratio:{page_ratio_value:.8f}")
    css = css.replace("__CLOSING_BG__", closing_bg_uri)
    css = css.replace("__WAVE_TOP__", wave_top_uri)
    rail_parts: list[str] = []
    overview_parts: list[str] = []
    first_global_by_section: dict[int, int] = {}
    for record in page_records:
        first_global_by_section.setdefault(int(record["section_index"]), int(record["global_index"]))
    for section in manifest_sections:
        section_title = html.escape(str(section["section_title"]))
        rail_parts.append(f"<div class=\"rail-section\"><h3 class=\"rail-section-title\">{section_title}</h3>")
        overview_parts.append(f"<section class=\"section-group\"><h2 class=\"section-title\">{section_title}</h2><div class=\"overview-pages\">")
        logical_slides = section["logical_slides"] if isinstance(section["logical_slides"], list) else []
        for logical in logical_slides:
            if not isinstance(logical, dict):
                continue
            display_logical_index = logical.get("display_logical_index", logical.get("logical_index"))
            logical_heading = f"{display_logical_index}. {logical['logical_title']}" if str(display_logical_index).isdigit() else f"{display_logical_index} {logical['logical_title']}"
            rail_parts.append(f"<h4 class=\"rail-logical-title\">{html.escape(str(logical_heading))}</h4><div class=\"rail-pages\">")
            physical_pages = logical["physical_pages"] if isinstance(logical["physical_pages"], list) else []
            for record in physical_pages:
                if not isinstance(record, dict):
                    continue
                rail_parts.append(render_thumb_card(record, "data-thumb-page-id"))
                extra = "section-first" if first_global_by_section.get(int(record["section_index"])) == int(record["global_index"]) else ""
                tile = render_thumb_card(record, "data-overview-page-id", f"overview-tile {extra}").replace("thumb-item", "overview-tile", 1)
                tile = tile.replace(
                    "</button>",
                    f"<b>{html.escape(str(record['logical_title']))}</b><span>{html.escape(str(record['page_label']))}</span></button>"
                )
                overview_parts.append(tile)
            rail_parts.append("</div>")
        rail_parts.append("</div>")
        overview_parts.append("</div></section>")
    pages_json = json.dumps(page_records, ensure_ascii=False).replace("</", "<\\/")
    js = f"""
const pages = {pages_json};
const SLIDE_DESIGN_WIDTH = 1280;
const SLIDE_RATIO = {page_ratio_value:.8f};
const SLIDE_DESIGN_HEIGHT = Math.round(SLIDE_DESIGN_WIDTH / SLIDE_RATIO);
let currentPageIndex = 0;
let viewMode = 'workspace';
let toolbarTimer = null;
let transitionSerial = 0;

function sourcePage(page) {{
  return document.querySelector('.page-source [data-page-id=\"' + page.page_id + '\"]');
}}

function buildStageShell(page) {{
  const source = sourcePage(page);
  if (!source) return null;
  const shell = document.createElement('div');
  shell.className = 'slide-scale-shell';
  shell.appendChild(source.cloneNode(true));
  return shell;
}}

function clearStageTransition(stage) {{
  if (!stage) return;
  const timers = stage._transitionTimers || [];
  timers.forEach((timer) => window.clearTimeout(timer));
  stage._transitionTimers = [];
  stage.classList.remove('is-transitioning','is-fade-out','is-fade-in');
}}

function clonePageInto(stageId, page, animate = false) {{
  const stage = document.getElementById(stageId);
  const shell = buildStageShell(page);
  if (!stage || !shell) return;
  const oldShells = [...stage.querySelectorAll('.slide-scale-shell')];
  const oldShell = oldShells.at(-1);
  oldShells.slice(0, -1).forEach((item) => item.remove());
  const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  if (!animate || !oldShell || reduceMotion) {{
    clearStageTransition(stage);
    stage.replaceChildren(shell);
    fitStage(stage);
    return;
  }}
  clearStageTransition(stage);
  const token = String(++transitionSerial);
  stage.dataset.transitionToken = token;
  stage.classList.add('is-transitioning','is-fade-out');
  fitStage(stage);
  const swapTimer = window.setTimeout(() => {{
    if (stage.dataset.transitionToken !== token) return;
    stage.replaceChildren(shell);
    fitStage(stage);
    stage.classList.remove('is-fade-out');
    stage.classList.add('is-fade-in');
    const doneTimer = window.setTimeout(() => {{
      if (stage.dataset.transitionToken !== token) return;
      stage.classList.remove('is-transitioning','is-fade-in');
      fitStage(stage);
    }}, 190);
    stage._transitionTimers = [doneTimer];
  }}, 110);
  stage._transitionTimers = [swapTimer];
}}

function renderThumbnailClones() {{
  document.querySelectorAll('[data-thumb-page-id] .thumb-real,[data-overview-page-id] .thumb-real').forEach((target) => {{
    const holder = target.closest('[data-thumb-page-id],[data-overview-page-id]');
    const pageId = holder?.dataset.thumbPageId || holder?.dataset.overviewPageId;
    const page = pages.find((item) => item.page_id === pageId);
    const source = page ? sourcePage(page) : null;
    if (!source) return;
    const shell = document.createElement('div');
    shell.className = 'slide-scale-shell';
    shell.appendChild(source.cloneNode(true));
    target.replaceChildren(shell);
    fitStage(target);
  }});
}}

function fitStage(stage) {{
  if (!stage) return;
  const shells = stage.querySelectorAll('.slide-scale-shell');
  if (!shells.length) return;
  const width = stage.clientWidth || stage.getBoundingClientRect().width || SLIDE_DESIGN_WIDTH;
  const height = stage.clientHeight || stage.getBoundingClientRect().height || SLIDE_DESIGN_HEIGHT;
  const scale = Math.min(width / SLIDE_DESIGN_WIDTH, height / SLIDE_DESIGN_HEIGHT);
  const safeScale = Math.max(0.1, scale);
  shells.forEach((shell) => {{
    shell.style.setProperty('--stage-scale', String(safeScale));
    shell.style.setProperty('--scaled-slide-width', (SLIDE_DESIGN_WIDTH * safeScale) + 'px');
    shell.style.setProperty('--scaled-slide-height', (SLIDE_DESIGN_HEIGHT * safeScale) + 'px');
  }});
}}

function fitVisibleStages() {{
  fitStage(document.getElementById('preview-stage'));
  fitStage(document.getElementById('playback-stage'));
  document.querySelectorAll('.thumb-real').forEach(fitStage);
}}

function isMobileRailMode() {{
  return window.matchMedia?.('(max-width: 680px)').matches;
}}

function clampRailWidth(value) {{
  const viewport = window.innerWidth || 1280;
  return Math.max(180, Math.min(Math.round(value), Math.min(420, viewport * .45)));
}}

function setRailWidth(value, persist = true) {{
  const width = clampRailWidth(value);
  document.documentElement.style.setProperty('--rail-width', width + 'px');
  if (persist) {{
    try {{ localStorage.setItem('school-presentation-rail-width', String(width)); }} catch (error) {{}}
  }}
  requestAnimationFrame(fitVisibleStages);
}}

function closeRailDrawer() {{
  document.querySelector('.app')?.classList.remove('rail-open');
}}

function toggleRailDrawer() {{
  document.querySelector('.app')?.classList.toggle('rail-open');
}}

function initRailControls() {{
  try {{
    const storedWidth = Number(localStorage.getItem('school-presentation-rail-width'));
    if (storedWidth) setRailWidth(storedWidth, false);
  }} catch (error) {{}}
  const resizer = document.getElementById('rail-resizer');
  resizer?.addEventListener('pointerdown', (event) => {{
    if (isMobileRailMode()) return;
    event.preventDefault();
    resizer.classList.add('is-dragging');
    document.body.style.cursor = 'col-resize';
    const onMove = (moveEvent) => setRailWidth(moveEvent.clientX);
    const onUp = () => {{
      resizer.classList.remove('is-dragging');
      document.body.style.cursor = '';
      window.removeEventListener('pointermove', onMove);
      window.removeEventListener('pointerup', onUp);
    }};
    window.addEventListener('pointermove', onMove);
    window.addEventListener('pointerup', onUp, {{once:true}});
  }});
  resizer?.addEventListener('keydown', (event) => {{
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    const current = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--rail-width')) || 260;
    setRailWidth(current + (event.key === 'ArrowRight' ? 18 : -18));
  }});
  document.getElementById('drawer-handle')?.addEventListener('click', toggleRailDrawer);
}}

function setActiveState(page) {{
  document.querySelectorAll('[data-thumb-page-id],[data-overview-page-id]').forEach((item) => {{
    const active = item.dataset.thumbPageId === page.page_id || item.dataset.overviewPageId === page.page_id;
    item.classList.toggle('is-active', active);
    item.setAttribute('aria-current', active ? 'true' : 'false');
  }});
  document.querySelectorAll('[data-current-page-label]').forEach((item) => item.textContent = page.page_label);
  document.querySelectorAll('[data-current-logical-title]').forEach((item) => item.textContent = page.logical_title);
  document.querySelectorAll('[data-current-section-title]').forEach((item) => item.textContent = page.section_title);
  const progress = document.getElementById('playback-progress');
  if (progress) progress.style.width = (((currentPageIndex + 1) / pages.length) * 100).toFixed(2) + '%';
  const activeRail = document.querySelector('[data-thumb-page-id=\"' + page.page_id + '\"]');
  activeRail?.scrollIntoView({{block:'nearest', inline:'nearest'}});
}}

function syncHash(page) {{
  const nextHash = '#p=' + encodeURIComponent(page.page_id);
  if (window.location.hash !== nextHash) history.replaceState(null, '', nextHash);
}}

function selectPage(target, options = {{}}) {{
  const idx = typeof target === 'number' ? target : pages.findIndex((page) => page.page_id === target || String(page.global_index) === String(target));
  if (idx < 0 || idx >= pages.length) return;
  const animate = options.animate !== false && idx !== currentPageIndex;
  currentPageIndex = idx;
  const page = pages[currentPageIndex];
  clonePageInto('preview-stage', page, animate);
  clonePageInto('playback-stage', page, animate);
  setActiveState(page);
  if (options.hash !== false) syncHash(page);
}}

function goToPage(deltaOrIndex) {{
  const next = Math.max(0, Math.min(pages.length - 1, currentPageIndex + deltaOrIndex));
  selectPage(next);
}}

function setView(mode) {{
  viewMode = mode;
  document.querySelector('.app')?.setAttribute('data-view', mode);
  document.getElementById('workspace').hidden = mode !== 'workspace';
  document.getElementById('overview').hidden = mode !== 'overview';
  document.getElementById('playback').hidden = mode !== 'playback';
}}

function showWorkspace() {{
  setView('workspace');
  selectPage(currentPageIndex, {{animate:false}});
  fitVisibleStages();
}}

function showPlayback() {{
  setView('playback');
  selectPage(currentPageIndex, {{animate:false}});
  revealPlaybackToolbar();
  fitVisibleStages();
}}

function showOverview() {{
  setView('overview');
  selectPage(currentPageIndex, {{animate:false}});
  requestAnimationFrame(() => fitVisibleStages());
}}

function selectFromHash() {{
  const raw = decodeURIComponent(window.location.hash.replace(/^#p=/, ''));
  if (!raw) return false;
  const idx = pages.findIndex((page) => page.page_id === raw || String(page.global_index) === raw);
  if (idx >= 0) {{
    selectPage(idx, {{hash:false, animate:false}});
    return true;
  }}
  return false;
}}

function revealPlaybackToolbar() {{
  const playback = document.getElementById('playback');
  playback?.classList.add('show-ui');
  clearTimeout(toolbarTimer);
  toolbarTimer = setTimeout(() => playback?.classList.remove('show-ui'), 1800);
}}

document.addEventListener('click', (event) => {{
  const rail = event.target.closest('[data-thumb-page-id]');
  if (rail) {{
    selectPage(rail.dataset.thumbPageId);
    if (isMobileRailMode()) closeRailDrawer();
  }}
  const overview = event.target.closest('[data-overview-page-id]');
  if (overview) {{
    selectPage(overview.dataset.overviewPageId);
    showWorkspace();
  }}
}});

document.addEventListener('keydown', (event) => {{
  if (event.key === 'Escape' && viewMode === 'playback') {{ event.preventDefault(); showWorkspace(); return; }}
  if (event.key === 'ArrowRight' || event.key === 'PageDown' || event.key === ' ') {{ event.preventDefault(); goToPage(1); }}
  if (event.key === 'ArrowLeft' || event.key === 'PageUp') {{ event.preventDefault(); goToPage(-1); }}
}});

document.querySelector('.playback-zone.prev')?.addEventListener('click', () => goToPage(-1));
document.querySelector('.playback-zone.center')?.addEventListener('click', () => goToPage(1)); // Phase 10 will prefer reveal steps before page advance.
document.querySelector('.playback-zone.next')?.addEventListener('click', () => goToPage(1));
document.getElementById('playback')?.addEventListener('mousemove', revealPlaybackToolbar);
document.getElementById('playback')?.addEventListener('touchstart', revealPlaybackToolbar, {{passive:true}});
let touchStartX = null;
document.getElementById('playback')?.addEventListener('touchstart', (event) => {{ touchStartX = event.changedTouches[0]?.clientX ?? null; }}, {{passive:true}});
document.getElementById('playback')?.addEventListener('touchend', (event) => {{
  if (touchStartX === null) return;
  const dx = (event.changedTouches[0]?.clientX ?? touchStartX) - touchStartX;
  if (Math.abs(dx) > 42) goToPage(dx < 0 ? 1 : -1);
  touchStartX = null;
}}, {{passive:true}});
window.addEventListener('hashchange', selectFromHash);

renderThumbnailClones();
initRailControls();
window.addEventListener('resize', () => {{
  if (!isMobileRailMode()) closeRailDrawer();
  fitVisibleStages();
}});
if (!selectFromHash()) selectPage(0);
fitVisibleStages();
"""
    html_doc = (
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{html.escape(title)}</title><style>{css}</style></head><body>"
        "<div class=\"app\" data-view=\"workspace\">"
        "<header class=\"app-top\">"
        f"<div class=\"brand-lockup\"><img src=\"{header_icon_uri}\" alt=\"school emblem\"><div class=\"brand-text\"><strong class=\"brand-title\">{html.escape(title)}</strong><span class=\"brand-context\"><span data-current-section-title></span> / <span data-current-logical-title></span></span></div></div>"
        "<div class=\"top-actions\"><span class=\"current-page-chip\" data-current-page-label></span>"
        "<button class=\"icon-btn\" type=\"button\" onclick=\"showOverview()\">预览</button>"
        "<button class=\"icon-btn primary\" type=\"button\" onclick=\"showPlayback()\">放映</button></div>"
        "</header>"
        "<main id=\"workspace\" class=\"workspace view\">"
        "<aside class=\"thumbnail-rail\" aria-label=\"thumbnail rail\">" + "".join(rail_parts) + "</aside>"
        "<button id=\"rail-resizer\" class=\"rail-resizer\" type=\"button\" aria-label=\"拖动调整缩略图栏宽度\"></button>"
        "<button id=\"drawer-handle\" class=\"drawer-handle\" type=\"button\" aria-label=\"打开或收起缩略图栏\"></button>"
        "<section class=\"preview-pane\"><div id=\"preview-stage\" class=\"preview-stage\" aria-live=\"polite\"></div><div class=\"preview-meta\"><span data-current-section-title></span><strong data-current-page-label></strong></div></section>"
        "</main>"
        "<section id=\"overview\" class=\"overview view\" hidden><div class=\"overview-toolbar\"><h1>预览</h1><button class=\"icon-btn\" type=\"button\" onclick=\"showWorkspace()\">返回</button></div><div class=\"overview-grid\">"
        + "".join(overview_parts) + "</div></section>"
        "<section id=\"playback\" class=\"playback view\" hidden>"
        "<div class=\"progress\" aria-hidden=\"true\"><i id=\"playback-progress\"></i></div>"
        "<button class=\"playback-zone prev\" type=\"button\" aria-label=\"previous page\"></button><button class=\"playback-zone center\" type=\"button\" aria-label=\"next page\"></button><button class=\"playback-zone next\" type=\"button\" aria-label=\"next page\"></button>"
        "<div id=\"playback-stage\" class=\"playback-stage\"></div><div class=\"playback-toolbar\" aria-label=\"playback controls\"><button class=\"playback-control\" type=\"button\" onclick=\"goToPage(-1)\" aria-label=\"上一页\"><span aria-hidden=\"true\">‹</span></button><span class=\"playback-page-pill\" data-current-page-label></span><button class=\"playback-control\" type=\"button\" onclick=\"goToPage(1)\" aria-label=\"下一页\"><span aria-hidden=\"true\">›</span></button><button class=\"playback-exit\" type=\"button\" onclick=\"showWorkspace()\" aria-label=\"退出播放\">Esc</button></div>"
        "</section>"
        "<div class=\"page-source\" hidden>" + "".join(page_sections) + "</div>"
        f"<script>{js}</script></div></body></html>"
    )
    sha = hashlib.sha256(html_doc.encode("utf-8")).hexdigest()
    manifest: dict[str, object] = {
        "input": str(input_path),
        "sections": manifest_sections,
        "logical_slides": logical_count,
        "physical_pages": physical_count,
        "pages": page_records,
        "page_ratio": page_ratio_label,
        "layouts_used": sorted(set(layouts_used)),
        "html_sha256": sha,
        "max_size_mb": max_size_mb,
        "media_warnings": sorted(set(media_warnings)),
    }
    return html_doc, manifest


def cmd_example(args: argparse.Namespace) -> None:
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(TEMPLATE_MD, output)
    print(f"wrote {output}")


def cmd_render(args: argparse.Namespace) -> dict[str, object]:
    input_path = Path(args.input).resolve()
    output = Path(args.html or input_path.with_suffix(".html"))
    meta, _ = parse_frontmatter(read_text(input_path))
    if args.max_size_mb is not None:
        max_size_mb = int(args.max_size_mb)
        max_size_source = "cli"
    else:
        max_size_mb = int(meta.get("max_output_mb") or DEFAULT_MAX_MB)
        max_size_source = "frontmatter" if meta.get("max_output_mb") else "default"
    html_doc, manifest = render_deck(input_path, max_size_mb)
    write_text(output, html_doc)
    size = output.stat().st_size
    manifest.update({
        "html": str(output),
        "size_bytes": size,
        "size_mb": round(size / (1024 * 1024), 4),
        "max_size_source": max_size_source,
        "under_size_cap": size <= max_size_mb * 1024 * 1024,
    })
    if args.manifest:
        write_text(Path(args.manifest), json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    if size > max_size_mb * 1024 * 1024:
        fail(f"HTML output exceeds {max_size_mb} MB: {output}")
    print(f"wrote {output}")
    if args.manifest:
        print(f"wrote {args.manifest}")
    return manifest


def cmd_verify(args: argparse.Namespace) -> None:
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    sample = workdir / "school-presentation-full.md"
    cmd_example(argparse.Namespace(output=str(sample)))
    media_dir = workdir / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    demo_media = {
        "风景.webp": Path("/Users/mrered/Developer/Code/GongWen-Tamplate-Lite/风景.webp"),
        "猫猫.png": Path("/Users/mrered/Developer/Code/GongWen-Tamplate-Lite/猫猫.png"),
        "AI人像.jpg": Path("/Users/mrered/Developer/Code/GongWen-Tamplate-Lite/AI人像.jpg"),
    }
    for name, source in demo_media.items():
        if source.is_file():
            shutil.copyfile(source, media_dir / name)
    first = workdir / "school-presentation-first.html"
    second = workdir / "school-presentation-second.html"
    first_manifest = workdir / "school-presentation-first.manifest.json"
    second_manifest = workdir / "school-presentation-second.manifest.json"
    m1 = cmd_render(argparse.Namespace(input=str(sample), html=str(first), manifest=str(first_manifest), max_size_mb=args.max_size_mb))
    m2 = cmd_render(argparse.Namespace(input=str(sample), html=str(second), manifest=str(second_manifest), max_size_mb=args.max_size_mb))
    stable = first.read_bytes() == second.read_bytes()
    first_html = first.read_text(encoding="utf-8")

    hierarchy_verified = False
    try:
        sections = m1.get("sections", [])
        pages = m1.get("pages", [])
        hierarchy_verified = (
            isinstance(sections, list)
            and len(sections) >= 1
            and any(
                len(slide.get("physical_pages", [])) > 1
                for section in sections
                if isinstance(section, dict)
                for slide in section.get("logical_slides", [])
                if isinstance(slide, dict)
            )
            and all(
                page.get("page_id")
                and page.get("page_label")
                and page.get("section_index") is not None
                and page.get("logical_index") is not None
                and page.get("physical_index") is not None
                and page.get("global_index") is not None
                and page.get("layout")
                and page.get("reveal_steps") == []
                for page in pages
                if isinstance(page, dict)
            )
            and all(
                "physical_pages" in slide and "reveal_steps" in slide
                for section in sections
                if isinstance(section, dict)
                for slide in section.get("logical_slides", [])
                if isinstance(slide, dict)
            )
        )
    except Exception:
        hierarchy_verified = False

    required_html_tokens = [
        "workspace",
        "thumbnail-rail",
        "rail-resizer",
        "drawer-handle",
        "preview-stage",
        "slide-scale-shell",
        "playback",
        "overview",
        "progress",
        "currentPageIndex",
        "selectPage",
        "showWorkspace",
        "showPlayback",
        "showOverview",
        "syncHash",
        "goToPage",
        "hashchange",
        "keydown",
        "playback-zone",
        "touchstart",
        "scrollIntoView",
        "fitStage",
        "setRailWidth",
        "toggleRailDrawer",
        "data-section-index",
        "data-logical-index",
        "data-physical-index",
        "data-global-index",
        "data-page-id",
        "data-thumb-page-id",
        "data-overview-page-id",
    ]
    workspace_verified = all(token in first_html for token in required_html_tokens)

    flat_sample = workdir / "flat-compat.md"
    flat_html = workdir / "flat-compat.html"
    flat_manifest_path = workdir / "flat-compat.manifest.json"
    write_text(flat_sample, """---
template: "school-presentation"
title: "Flat Compatibility"
page_ratio: "16:9"
max_output_mb: 50
---

## Slide: 平面旧页一

<!-- slide
layout: content
intent: flat compatibility one
split: auto
-->

旧格式仍然可以渲染。

## Slide: 平面旧页二

<!-- slide
layout: content
intent: flat compatibility two
split: auto
-->

- 第一条
- 第二条
""")
    flat_manifest = cmd_render(argparse.Namespace(input=str(flat_sample), html=str(flat_html), manifest=str(flat_manifest_path), max_size_mb=args.max_size_mb))
    flat_sections = flat_manifest.get("sections", [])
    flat_slide_compat_verified = (
        isinstance(flat_sections, list)
        and len(flat_sections) == 1
        and isinstance(flat_sections[0], dict)
        and flat_sections[0].get("section_title") == "默认章节"
        and len(flat_sections[0].get("logical_slides", [])) == 2
    )

    passed = (
        stable
        and bool(m1.get("under_size_cap"))
        and bool(m2.get("under_size_cap"))
        and hierarchy_verified
        and workspace_verified
        and flat_slide_compat_verified
    )
    verification = {
        "status": "passed" if passed else "failed",
        "repeatable_html": stable,
        "hierarchy_verified": hierarchy_verified,
        "workspace_verified": workspace_verified,
        "flat_slide_compat_verified": flat_slide_compat_verified,
        "first_sha256": m1.get("html_sha256"),
        "second_sha256": m2.get("html_sha256"),
        "logical_slides": m1.get("logical_slides"),
        "physical_pages": m1.get("physical_pages"),
        "sections": len(m1.get("sections", [])),
        "pages_verified": len(m1.get("pages", [])),
        "media_warnings": sorted(set(m1.get("media_warnings", []) + m2.get("media_warnings", []))),
        "artifacts": [
            str(sample),
            str(first),
            str(second),
            str(first_manifest),
            str(second_manifest),
            str(flat_sample),
            str(flat_html),
            str(flat_manifest_path),
        ],
    }
    write_text(workdir / "verification-manifest.json", json.dumps(verification, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {workdir / 'verification-manifest.json'}")
    if verification["status"] != "passed":
        fail("verification failed")


def cmd_info(_: argparse.Namespace) -> None:
    manifest_path = IDENTITY_DIR / "asset-manifest.json"
    print(read_text(manifest_path))


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="school-presentation.sh")
    sub = parser.add_subparsers(dest="command", required=True)
    p_example = sub.add_parser("example")
    p_example.add_argument("--output", required=True)
    p_render = sub.add_parser("render")
    p_render.add_argument("--input", required=True)
    p_render.add_argument("--html")
    p_render.add_argument("--manifest")
    p_render.add_argument("--max-size-mb")
    p_verify = sub.add_parser("verify")
    p_verify.add_argument("--workdir", required=True)
    p_verify.add_argument("--max-size-mb")
    sub.add_parser("info")
    args = parser.parse_args(argv)
    if args.command == "example":
        cmd_example(args)
    elif args.command == "render":
        cmd_render(args)
    elif args.command == "verify":
        cmd_verify(args)
    elif args.command == "info":
        cmd_info(args)


main(sys.argv[2:])
PY
}

main() {
  local command="${1:-}"
  if [[ $# -gt 0 ]]; then
    shift
  fi

  case "$command" in
    example|render|verify|info)
      python_renderer "$command" "$@"
      ;;
    -h|--help|"")
      usage
      ;;
    *)
      die "unknown command: $command"
      ;;
  esac
}

main "$@"
