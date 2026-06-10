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


INTERACTION_KINDS = {"reveal", "mask", "emphasis"}
STRUCTURE_KINDS: set[str] = set()


def parse_attrs(raw: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for key, double_quoted, single_quoted, bare in re.findall(r"([A-Za-z_-][A-Za-z0-9_-]*)=(?:\"([^\"]*)\"|'([^']*)'|([^ \t]+))", raw):
        attrs[key.strip()] = (double_quoted or single_quoted or bare or "").strip()
    return attrs


def normalize_order(raw: str | None, fallback: str = "1") -> str:
    value = (raw or fallback).strip()
    if not value:
        value = fallback
    try:
        number = float(value)
    except ValueError:
        number = float(fallback)
    text = f"{number:.6f}".rstrip("0").rstrip(".")
    return text or "0"


def order_sort_key(raw: str) -> tuple[float, str]:
    try:
        return (float(raw), raw)
    except ValueError:
        return (0.0, raw)


def order_number(raw: str) -> float | None:
    try:
        return float(raw)
    except ValueError:
        return None


def normalize_animation_mode(raw: str | None) -> str:
    value = (raw or "none").strip().lower()
    if value in {"off", "false", "no", "none"}:
        return "none"
    if value in {"all", "page", "full"}:
        return "all"
    if value in {"step", "steps", "paragraph", "paragraphs", "staged"}:
        return "step"
    return "none"


def reveal_orders_in_html(rendered: str) -> list[float]:
    orders: list[float] = []
    for match in re.finditer(r'data-reveal-order="([^"]+)"', rendered):
        number = order_number(html.unescape(match.group(1)))
        if number is not None:
            orders.append(number)
    return orders


def order_before_inner(rendered: str, fallback: str) -> str:
    orders = reveal_orders_in_html(rendered)
    if not orders:
        return fallback
    return normalize_order(str(min(orders) - 0.1), fallback)


def next_auto_order(animation_state: dict[str, float] | None) -> str:
    if animation_state is None:
        return "1"
    current = animation_state.get("next", 1.0)
    animation_state["next"] = current + 1.0
    return normalize_order(str(current))


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
        directive_match = re.match(r"^:::\s*([A-Za-z_-]+)(.*?)\s*$", line.strip())
        if directive_match:
            directive_name = directive_match.group(1).strip().lower()
            attrs = parse_attrs(directive_match.group(2))
            body = []
            i += 1
            while i < len(lines) and not re.match(r"^:::\s*$", lines[i].strip()):
                body.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            body_text = "\n".join(body).strip()
            if directive_name in INTERACTION_KINDS or directive_name in STRUCTURE_KINDS:
                block = {"type": directive_name, "text": body_text}
                block.update({f"attr_{key}": value for key, value in attrs.items()})
                blocks.append(block)
                continue
            alert_type = normalize_alert_type(directive_name)
            if alert_type:
                blocks.append({"type": "alert", "alert_type": alert_type, "text": body_text})
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
        return max(5, len(text.splitlines()) * 2)
    if kind == "media":
        return 11
    if kind == "fence":
        return 10 if block.get("lang") == "chart" else 6
    if kind == "math":
        return 5
    if kind in {"reveal", "mask", "emphasis", "animate"}:
        inner_score = sum(block_score(inner) for inner in split_blocks(text))
        return max(4, inner_score)
    if kind == "sort":
        return max(8, len([line for line in text.splitlines() if line.strip()]) * 2)
    if kind in STRUCTURE_KINDS:
        item_count = len([line for line in text.splitlines() if re.match(r"^\s*[-*]\s+", line)])
        if kind == "timeline":
            return max(12, item_count * 5)
        if kind == "gallery":
            return max(10, item_count * 4)
        if kind == "smartart":
            smart_type = (block.get("attr_type") or "").strip().lower()
            multiplier = 6 if smart_type == "picture" else 4
            return max(10, item_count * multiplier)
        return max(8, item_count * 3)
    return max(3, len(text) // 70 + 2)


def split_large_block(block: dict[str, str]) -> list[dict[str, str]]:
    kind = block["type"]
    text = block["text"]
    if kind == "list":
        lines = [line for line in text.splitlines() if re.match(r"^\s*[-*]\s+", line)]
        if len(lines) <= 8:
            return [block]
        return [{"type": "list", "text": "\n".join(lines[idx : idx + 8])} for idx in range(0, len(lines), 8)]
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


def render_inline_interaction(kind: str, attr_text: str, body: str) -> str:
    attrs = parse_attrs(attr_text)
    order = normalize_order(attrs.get("order"))
    label = attrs.get("label", "")
    class_name = f"reveal-target reveal-kind-{kind} inline-reveal"
    if kind == "emphasis":
        class_name += " emphasis-underline"
    mathish = "\\" in body or any(token in body for token in ["√", "×", "cos", "sin", "tan", "^", "_"])
    content = latex_to_html(body) if mathish else inline_markdown(body)
    label_attr = f' data-reveal-label="{html.escape(label, quote=True)}"' if label else ""
    return (
        f'<span class="{class_name}" data-reveal-order="{html.escape(order, quote=True)}" '
        f'data-reveal-kind="{html.escape(kind, quote=True)}"{label_attr}>'
        f'<span class="reveal-content">{content}</span></span>'
    )


def safe_trigger_mode(raw: str | None) -> str:
    value = (raw or "both").strip().lower()
    return value if value in {"hover", "click", "both"} else "both"


def render_inline_zoom(attr_text: str, body: str) -> str:
    attrs = parse_attrs(attr_text)
    scale = attrs.get("scale", "1.16")
    try:
        scale_value = max(1.04, min(1.32, float(scale)))
    except ValueError:
        scale_value = 1.16
    content = inline_markdown(body)
    return (
        f'<span class="hover-zoom" tabindex="0" style="--hover-zoom-scale:{scale_value:.2f}">'
        f'{content}</span>'
    )


def render_peek_template(attrs: dict[str, str], body_html: str = "", input_dir: Path | None = None, media_warnings: list[str] | None = None) -> tuple[str, bool]:
    title = attrs.get("title", "").strip()
    text = attrs.get("text", "").strip()
    image = (attrs.get("image") or attrs.get("media") or "").strip()
    video = attrs.get("video", "").strip()
    parts: list[str] = ['<div class="peek-panel']
    has_media = bool(image or video)
    if has_media:
        parts[0] += ' has-media'
    parts[0] += '">'
    if title:
        parts.append(f'<strong class="peek-title">{inline_markdown(title)}</strong>')
    if video:
        path = resolve_asset(video, input_dir) if input_dir else None
        if path is None:
            if media_warnings is not None:
                media_warnings.append(f"peek video missing: {video}")
            parts.append(
                '<figure class="peek-media media-broken">'
                '<div class="broken-media-icon broken-video" aria-hidden="true"></div>'
                f'<figcaption><code>{html.escape(video)}</code></figcaption></figure>'
            )
        else:
            parts.append(f'<video class="peek-media" controls muted playsinline loop src="{data_uri(path)}"></video>')
    elif image:
        path = resolve_asset(image, input_dir) if input_dir else None
        if path is None:
            if media_warnings is not None:
                media_warnings.append(f"peek image missing: {image}")
            parts.append(
                '<figure class="peek-media media-broken">'
                '<div class="broken-media-icon broken-image" aria-hidden="true"></div>'
                f'<figcaption><code>{html.escape(image)}</code></figcaption></figure>'
            )
        else:
            alt = title or image
            parts.append(f'<img class="peek-media" src="{data_uri(path)}" alt="{html.escape(alt)}">')
    body = text or body_html
    if body:
        if text:
            parts.append(f'<p class="peek-body">{inline_markdown(body)}</p>')
        else:
            parts.append(f'<div class="peek-body">{body}</div>')
    parts.append('</div>')
    return "".join(parts), has_media


def render_inline_peek(attr_text: str, body: str) -> str:
    attrs = parse_attrs(attr_text)
    mode = safe_trigger_mode(attrs.get("trigger"))
    label = inline_markdown(body)
    panel, has_media = render_peek_template(attrs)
    media_attr = ' data-peek-media="true"' if has_media else ""
    return (
        f'<span class="peek-trigger" tabindex="0" role="button" data-peek-trigger="{html.escape(mode, quote=True)}"{media_attr}>'
        f'{label}<template class="peek-template">{panel}</template></span>'
    )


def inline_markdown(text: str) -> str:
    pattern = re.compile(r"\{\{(mask|emphasis|reveal)([^}]*)\}\}(.*?)\{\{/\1\}\}", re.S)
    parts: list[str] = []
    cursor = 0
    for match in pattern.finditer(text):
        parts.append(html.escape(text[cursor:match.start()]))
        kind = match.group(1)
        parts.append(render_inline_interaction(kind, match.group(2), match.group(3)))
        cursor = match.end()
    parts.append(html.escape(text[cursor:]))
    escaped = "".join(parts)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    return escaped


def render_table(text: str, row_orders: list[str] | None = None) -> str:
    rows = [row.strip().strip("|").split("|") for row in text.splitlines() if row.strip()]
    if len(rows) >= 2 and all(set(cell.strip()) <= {"-", ":"} for cell in rows[1]):
        header, body = rows[0], rows[2:]
    else:
        header, body = rows[0], rows[1:]
    parts = ["<div class=\"table-wrap\"><table><thead><tr>"]
    for cell in header:
        parts.append(f"<th>{inline_markdown(cell.strip())}</th>")
    parts.append("</tr></thead><tbody>")
    for idx, row in enumerate(body):
        row_attr = ""
        if row_orders and idx < len(row_orders):
            order = html.escape(row_orders[idx], quote=True)
            row_attr = f' class="reveal-target reveal-kind-animate" data-reveal-order="{order}" data-reveal-kind="animate"'
        parts.append(f"<tr{row_attr}>")
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
            interaction_match = re.match(r"\{\{(mask|emphasis|reveal|animate)([^}]*)\}\}(.*?)\{\{/\1\}\}", value[i:], flags=re.S)
            if interaction_match:
                kind = interaction_match.group(1)
                attrs = parse_attrs(interaction_match.group(2))
                order = normalize_order(attrs.get("order"))
                class_name = f"reveal-target reveal-kind-{kind} inline-reveal"
                if kind == "emphasis":
                    class_name += " emphasis-underline"
                out.append(
                    f'<span class="{class_name}" data-reveal-order="{html.escape(order, quote=True)}" '
                    f'data-reveal-kind="{html.escape(kind, quote=True)}">'
                    f'<span class="reveal-content">{render_inner(interaction_match.group(3))}</span></span>'
                )
                i += len(interaction_match.group(0))
                continue
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
            return f"<figure class=\"video-fallback media-broken\"><div class=\"broken-media-icon broken-video\" aria-hidden=\"true\"></div><figcaption><code>{html.escape(raw_path)}</code></figcaption></figure>"
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 20:
            media_warnings.append(f"video fallback: {raw_path} is {size_mb:.2f} MB")
            return f"<figure class=\"video-fallback media-broken\"><div class=\"broken-media-icon broken-video\" aria-hidden=\"true\"></div><figcaption><a href=\"{html.escape(str(path))}\">{html.escape(raw_path)}</a></figcaption></figure>"
        return f"<video controls src=\"{data_uri(path)}\"></video><p class=\"caption\">{inline_markdown(label_text)}</p>"
    if path is None:
        media_warnings.append(f"image missing: {raw_path}")
        return f"<figure class=\"missing-media media-broken\"><div class=\"broken-media-icon broken-image\" aria-hidden=\"true\"></div><figcaption><code>{html.escape(raw_path)}</code></figcaption></figure>"
    return f"<figure><img src=\"{data_uri(path)}\" alt=\"{html.escape(label_text)}\"><figcaption>{inline_markdown(label_text)}</figcaption></figure>"


def render_alert(kind: str, text: str) -> str:
    alert_type = normalize_alert_type(kind) or "info"
    label = ALERT_LABELS[alert_type]
    body = inline_markdown(text.strip()) if text.strip() else ""
    icon = {"info": "review", "tip": "hint", "warning": "risk", "error": "error"}.get(alert_type, "review")
    return (
        f"<aside class=\"alert alert-{html.escape(alert_type)}\">"
        f"{render_semantic_icon(icon, 'mini')}"
        f"<div><strong>{html.escape(label)}</strong><p>{body}</p></div></aside>"
    )


def parse_structured_items(text: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = re.match(r"^[-*]\s*(?:\[([^\]]+)\]\s*)?(.*)$", line)
        if not match:
            continue
        attrs = parse_attrs(match.group(1) or "")
        body = match.group(2).strip()
        title = attrs.get("title") or attrs.get("label") or ""
        if not title and "：" in body:
            head, rest = body.split("：", 1)
            if 0 < len(head) <= 18:
                title, body = head.strip(), rest.strip()
        elif not title and ":" in body:
            head, rest = body.split(":", 1)
            if 0 < len(head) <= 18:
                title, body = head.strip(), rest.strip()
        items.append({"body": body, "title": title, **attrs})
    return items


def structure_icon_html(item: dict[str, str], fallback_text: str = "") -> str:
    raw_icon = item.get("icon")
    icon = normalize_icon_name(raw_icon)
    if icon == "":
        return ""
    if not raw_icon or icon == "auto":
        icon = semantic_icon_for_text(" ".join([item.get("title", ""), item.get("body", ""), fallback_text]), "target")
    return render_semantic_icon(icon or "target", "mini")


def structure_media_html(item: dict[str, str], input_dir: Path, media_warnings: list[str], label: str = "") -> str:
    raw_path = (item.get("image") or item.get("media") or "").strip()
    if not raw_path:
        return ""
    alt = label or item.get("title") or raw_path
    path = resolve_asset(raw_path, input_dir)
    if path is None:
        media_warnings.append(f"structure media missing: {raw_path}")
        return (
            '<figure class="structure-media media-broken">'
            '<div class="broken-media-icon broken-image" aria-hidden="true"></div>'
            f'<figcaption><code>{html.escape(raw_path)}</code></figcaption></figure>'
        )
    return f'<figure class="structure-media"><img src="{data_uri(path)}" alt="{html.escape(alt)}"></figure>'


def render_timeline_block(block: dict[str, str], input_dir: Path, media_warnings: list[str]) -> str:
    variant = html.escape((block.get("attr_variant") or "vertical").strip().lower())
    items = parse_structured_items(block["text"])
    rows = []
    feature_media = []
    has_media = False
    for idx, item in enumerate(items, start=1):
        title = item.get("title") or f"节点 {idx}"
        time_label = item.get("time") or item.get("date") or str(idx)
        media = structure_media_html(item, input_dir, media_warnings, title)
        icon = structure_icon_html(item, title)
        has_media = has_media or bool(media)
        item_class = " has-media" if media else ""
        media_class = " has-media" if media and variant != "horizontal" else ""
        card_media = media if variant != "horizontal" else ""
        if media and variant == "horizontal":
            feature_media.append(
                '<div class="timeline-feature-card">'
                f'{media}'
                '<div class="timeline-feature-caption">'
                f'<small>{html.escape(time_label)}</small>'
                f'<strong>{inline_markdown(title)}</strong>'
                f'<span>{inline_markdown(item.get("body", ""))}</span>'
                '</div></div>'
            )
        rows.append(
            f'<article class="timeline-item{item_class}">'
            f'<div class="timeline-point"><span>{html.escape(time_label)}</span>{icon}</div>'
            f'<div class="timeline-card{media_class}">{card_media}<div class="timeline-card-text"><h3>{inline_markdown(title)}</h3><p>{inline_markdown(item.get("body", ""))}</p></div></div>'
            '</article>'
        )
    block_class = f"structure-block timeline timeline-{variant}"
    if has_media:
        block_class += " timeline-with-media"
    if variant == "horizontal" and feature_media:
        return f'<div class="{block_class}"><div class="timeline-track">{"".join(rows)}</div><div class="timeline-feature-panel">{"".join(feature_media)}</div></div>'
    return f'<div class="{block_class}">{"".join(rows)}</div>'


def render_cards_block(block: dict[str, str]) -> str:
    variant = html.escape((block.get("attr_variant") or "kanban").strip().lower())
    columns = block.get("attr_columns") or "3"
    try:
        column_count = max(2, min(4, int(columns)))
    except ValueError:
        column_count = 3
    items = parse_structured_items(block["text"])
    cards = []
    for idx, item in enumerate(items, start=1):
        title = item.get("title") or f"卡片 {idx}"
        status = item.get("status") or item.get("tag") or ""
        status_html = f'<small>{inline_markdown(status)}</small>' if status else ""
        cards.append(
            '<article class="board-card">'
            f'{structure_icon_html(item, title)}<div><h3>{inline_markdown(title)}</h3>'
            f'{status_html}<p>{inline_markdown(item.get("body", ""))}</p></div></article>'
        )
    return f'<div class="structure-block card-board card-board-{variant}" style="--card-columns:{column_count}">{"".join(cards)}</div>'


def render_gallery_block(block: dict[str, str], input_dir: Path, media_warnings: list[str]) -> str:
    variant = html.escape((block.get("attr_variant") or "album").strip().lower())
    items = parse_structured_items(block["text"])
    cards = []
    for idx, item in enumerate(items, start=1):
        title = item.get("title") or f"画册 {idx}"
        media = structure_media_html(item, input_dir, media_warnings, title)
        if not media:
            media = f'<div class="gallery-icon-panel">{structure_icon_html(item, title)}</div>'
        cards.append(
            '<article class="gallery-item">'
            f'{media}<div class="gallery-copy"><h3>{inline_markdown(title)}</h3><p>{inline_markdown(item.get("body", ""))}</p></div></article>'
        )
    return f'<div class="structure-block gallery gallery-{variant}">{"".join(cards)}</div>'


def render_smartart_block(block: dict[str, str], input_dir: Path, media_warnings: list[str]) -> str:
    smart_type = html.escape((block.get("attr_type") or "process").strip().lower())
    variant = html.escape((block.get("attr_variant") or "steps").strip().lower())
    items = parse_structured_items(block["text"])
    parts = []
    for idx, item in enumerate(items, start=1):
        title = item.get("title") or f"项目 {idx}"
        media = structure_media_html(item, input_dir, media_warnings, title) if smart_type == "picture" else ""
        pyramid_width = min(94, 44 + idx * 12)
        layer_width = max(54, 100 - (idx - 1) * 8)
        style = f"--item-index:{idx};--item-count:{max(1, len(items))};--pyramid-width:{pyramid_width}%;--layer-width:{layer_width}%"
        parts.append(
            f'<article class="smartart-item" style="{style}">'
            f'<span class="smartart-index">{idx}</span>{media}{structure_icon_html(item, title)}'
            f'<div><h3>{inline_markdown(title)}</h3><p>{inline_markdown(item.get("body", ""))}</p></div></article>'
        )
    return f'<div class="structure-block smartart smartart-{smart_type} smartart-{smart_type}-{variant}">{"".join(parts)}</div>'


def render_peek_block(block: dict[str, str], input_dir: Path, media_warnings: list[str]) -> str:
    attrs = {
        key.removeprefix("attr_"): value
        for key, value in block.items()
        if key.startswith("attr_")
    }
    mode = safe_trigger_mode(attrs.get("trigger"))
    title = attrs.get("title", "").strip()
    target = attrs.get("target", "").strip() or title or "查看说明"
    body_html = "".join(render_block(inner, input_dir, media_warnings) for inner in split_blocks(block["text"]))
    panel, has_media = render_peek_template(attrs, body_html, input_dir, media_warnings)
    icon_hint = semantic_icon_for_text(" ".join([title, target, block["text"]]), "review")
    media_attr = ' data-peek-media="true"' if has_media else ""
    subtitle = title if title and title != target else "补充说明"
    return (
        f'<button class="peek-trigger-card" type="button" data-peek-trigger="{html.escape(mode, quote=True)}"{media_attr}>'
        f'{render_semantic_icon(icon_hint, "mini")}'
        f'<span><strong>{inline_markdown(target)}</strong>'
        f'<small>{inline_markdown(subtitle)}</small></span>'
        f'<template class="peek-template">{panel}</template>'
        f'</button>'
    )


def render_blocks(
    blocks: list[dict[str, str]],
    input_dir: Path,
    media_warnings: list[str],
    section_index: int | None = None,
    formula_counters: dict[int, int] | None = None,
    animation_mode: str = "none",
    animation_state: dict[str, float] | None = None,
) -> str:
    parts: list[str] = []
    for block in blocks:
        if animation_mode == "step" and block["type"] not in INTERACTION_KINDS:
            parts.append(render_auto_animated_block(block, input_dir, media_warnings, section_index, formula_counters, animation_state))
        else:
            parts.append(render_block(block, input_dir, media_warnings, section_index, formula_counters))
    return "".join(parts)


def wrap_animated_content(rendered: str, order: str, tag: str = "div") -> str:
    safe_order = html.escape(order, quote=True)
    return (
        f'<{tag} class="reveal-target reveal-kind-animate" '
        f'data-reveal-order="{safe_order}" data-reveal-kind="animate">'
        f'<div class="reveal-content">{rendered}</div></{tag}>'
    )


def render_auto_animated_block(
    block: dict[str, str],
    input_dir: Path,
    media_warnings: list[str],
    section_index: int | None = None,
    formula_counters: dict[int, int] | None = None,
    animation_state: dict[str, float] | None = None,
) -> str:
    kind = block["type"]
    text = block["text"]
    if kind == "list":
        items = [re.sub(r"^\s*[-*]\s+", "", line).strip() for line in text.splitlines()]
        rows = []
        for item in items:
            rendered = inline_markdown(item)
            order = order_before_inner(rendered, next_auto_order(animation_state))
            safe_order = html.escape(order, quote=True)
            rows.append(
                f'<li class="reveal-target reveal-kind-animate" '
                f'data-reveal-order="{safe_order}" data-reveal-kind="animate">'
                f'<span class="reveal-content">{rendered}</span></li>'
            )
        return "<ul>" + "".join(rows) + "</ul>"
    if kind == "table":
        rows = [row for row in text.splitlines() if row.strip()]
        body_rows = rows[2:] if len(rows) >= 2 and all(set(cell.strip()) <= {"-", ":"} for cell in rows[1].strip().strip("|").split("|")) else rows[1:]
        row_orders = [next_auto_order(animation_state) for _ in body_rows]
        return render_table(text, row_orders)
    rendered = render_block(block, input_dir, media_warnings, section_index, formula_counters)
    order = order_before_inner(rendered, next_auto_order(animation_state))
    return wrap_animated_content(rendered, order)


def render_interaction_block(
    kind: str,
    block: dict[str, str],
    input_dir: Path,
    media_warnings: list[str],
    section_index: int | None = None,
    formula_counters: dict[int, int] | None = None,
) -> str:
    order = normalize_order(block.get("attr_order"))
    label = block.get("attr_label", "")
    class_name = f"reveal-target reveal-kind-{kind}"
    if kind == "emphasis":
        class_name += " emphasis-underline"
    label_attr = f' data-reveal-label="{html.escape(label, quote=True)}"' if label else ""
    rendered = render_blocks(split_blocks(block["text"]), input_dir, media_warnings, section_index, formula_counters)
    return (
        f'<div class="{class_name}" data-reveal-order="{html.escape(order, quote=True)}" '
        f'data-reveal-kind="{html.escape(kind, quote=True)}"{label_attr}>'
        f'<div class="reveal-content">{rendered}</div></div>'
    )


def render_sort_block(block: dict[str, str]) -> str:
    items: list[dict[str, str]] = []
    for idx, raw_line in enumerate(block["text"].splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        match = re.match(r"^[-*]\s*\[([^\]]+)\]\s*(.+)$", line)
        if match:
            attrs = parse_attrs(match.group(1))
            body = match.group(2).strip()
        else:
            attrs = {"order": str(idx)}
            body = re.sub(r"^[-*]\s+", "", line)
        order = normalize_order(attrs.get("order"), str(idx))
        items.append({"order": order, "body": body})
    if not items:
        return ""
    unique_orders = sorted({item["order"] for item in items}, key=order_sort_key)
    rank_by_order = {order: str(idx) for idx, order in enumerate(unique_orders, start=1)}
    final_order = normalize_order(block.get("attr_final_order"), str(len(unique_orders) + 1))
    rows = []
    for item in items:
        rank = rank_by_order[item["order"]]
        rows.append(
            f'<div class="sort-item reveal-target reveal-kind-sort-rank" '
            f'data-reveal-order="{html.escape(item["order"], quote=True)}" data-reveal-kind="sort-rank" '
            f'style="--sort-order:{html.escape(rank)}">'
            f'<i>{html.escape(rank)}</i><span>{inline_markdown(item["body"])}</span></div>'
        )
    return (
        f'<div class="sort-list reveal-target reveal-kind-sort-final" '
        f'data-reveal-order="{html.escape(final_order, quote=True)}" data-reveal-kind="sort-final">'
        + "".join(rows)
        + "</div>"
    )


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
    if kind in {"reveal", "mask", "emphasis"}:
        return render_interaction_block(kind, block, input_dir, media_warnings, section_index, formula_counters)
    if kind == "sort":
        return render_sort_block(block)
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


ICON_ALIASES = {
    "auto": "auto",
    "none": "",
    "off": "",
    "false": "",
    "target": "target",
    "goal": "target",
    "objective": "target",
    "process": "process",
    "flow": "process",
    "step": "process",
    "safety": "safety",
    "safe": "safety",
    "risk": "risk",
    "warning": "risk",
    "error": "risk",
    "formula": "formula",
    "math": "formula",
    "table": "table",
    "matrix": "table",
    "chart": "chart",
    "data": "chart",
    "media": "media",
    "image": "media",
    "video": "media",
    "reveal": "reveal",
    "mask": "reveal",
    "answer": "reveal",
    "review": "review",
    "check": "review",
    "default": "target",
}

ICON_KEYWORDS: list[tuple[str, list[str]]] = [
    ("safety", ["安全", "急停", "接地", "绝缘", "通电", "断电", "保护", "故障", "短路", "排故"]),
    ("risk", ["风险", "警告", "错误", "异常", "缺失", "fallback", "不可", "过大"]),
    ("formula", ["公式", "计算", "电压", "电流", "功率", "阻值", "sqrt", "cos", "sin", "tan", "u =", "p ="]),
    ("chart", ["图表", "进度", "数据", "统计", "比例", "达成", "投入", "评分"]),
    ("table", ["表格", "矩阵", "清单", "验收", "责任", "检测点", "功能点", "模块"]),
    ("media", ["图片", "视频", "照片", "媒体", "横向", "竖向", "双图", "图右", "图左"]),
    ("reveal", ["揭示", "遮罩", "强调", "排序", "答案", "选择题", "填空", "判断", "动画", "order"]),
    ("review", ["审阅", "关注", "评价", "复盘", "验证", "检查", "看什么"]),
    ("process", ["流程", "步骤", "链路", "推进", "安装", "调试", "联调", "沉淀"]),
    ("target", ["目标", "建设", "任务", "内容", "资源", "课程", "背景"]),
]


def normalize_icon_name(raw: str | None) -> str | None:
    if raw is None:
        return "auto"
    value = raw.strip().lower()
    return ICON_ALIASES.get(value, value if value in {name for name, _ in ICON_KEYWORDS} else "auto")


def semantic_icon_for_text(text: str, fallback: str = "target") -> str:
    lowered = text.lower()
    scores: dict[str, int] = {}
    for icon, keywords in ICON_KEYWORDS:
        score = 0
        for keyword in keywords:
            if keyword.lower() in lowered:
                score += 1
        if score:
            scores[icon] = score
    if scores:
        return max(scores.items(), key=lambda item: (item[1], -[name for name, _ in ICON_KEYWORDS].index(item[0])))[0]
    return fallback


def semantic_icon_for_slide(slide: dict[str, object], layout: str, blocks: list[dict[str, str]]) -> str:
    meta = slide["meta"] if isinstance(slide.get("meta"), dict) else {}
    explicit = normalize_icon_name(meta.get("icon") if isinstance(meta, dict) else None)
    if explicit == "":
        return ""
    if explicit and explicit != "auto":
        return explicit
    if layout in {"cover", "closing", "section"}:
        return ""
    if layout == "table":
        return "table"
    if layout == "chart":
        return "chart"
    if layout.startswith("media"):
        return "media"
    text_parts = [str(slide.get("title", ""))]
    if isinstance(meta, dict):
        text_parts.append(str(meta.get("intent", "")))
    text_parts.extend(block.get("text", "") for block in blocks[:6])
    return semantic_icon_for_text("\n".join(text_parts))


def render_semantic_icon(icon: str, extra_class: str = "") -> str:
    if not icon:
        return ""
    class_attr = f"semantic-icon icon-{html.escape(icon)}"
    if extra_class:
        class_attr += f" {html.escape(extra_class)}"
    return f'<span class="{class_attr}" aria-hidden="true"></span>'


def display_char_count(text: str) -> int:
    return sum(1 for char in text.strip() if not char.isspace())


def clamp_display_chars(text: str, max_chars: int) -> str:
    count = 0
    output: list[str] = []
    for char in text.strip():
        if not char.isspace():
            count += 1
        if count > max_chars:
            return "".join(output).rstrip()
        output.append(char)
    return "".join(output).strip()


def split_display_lines(text: str, chars_per_line: int, max_lines: int) -> list[str]:
    total_count = display_char_count(text)
    if chars_per_line < total_count <= chars_per_line * max_lines:
        chars_per_line = max(1, (total_count + max_lines - 1) // max_lines)
    lines = [""]
    visible_count = 0
    for char in text.strip():
        if char.isspace():
            if lines[-1] and not lines[-1].endswith(" "):
                lines[-1] += char
            continue
        if visible_count >= chars_per_line:
            if len(lines) >= max_lines:
                break
            lines.append("")
            visible_count = 0
        lines[-1] += char
        visible_count += 1
    return [line.strip() for line in lines if line.strip()]


def render_cover_title(title: str) -> str:
    lines = split_display_lines(title, 10, 2) or [title.strip()]
    return "".join(f"<span>{html.escape(line)}</span>" for line in lines)


def cover_title_density_class(title: str) -> str:
    count = display_char_count(title)
    if count > 38:
        return " cover-title-compact"
    if count > 26:
        return " cover-title-long"
    return ""


def render_cover_details(meta: dict[str, str]) -> str:
    unit = meta.get("unit", "").strip()
    person = next((meta.get(key, "").strip() for key in ["presenter", "reporter", "author"] if meta.get(key, "").strip()), "")
    date = meta.get("date", "").strip()
    rows: list[str] = []
    if person:
        rows.append(f"<span class=\"cover-detail-person\"><em>{html.escape(person)}</em></span>")
    if date:
        rows.append(f"<span class=\"cover-detail-date\"><em>{html.escape(date)}</em></span>")
    if unit:
        rows.append(f"<span class=\"cover-detail-unit\"><em>{html.escape(unit)}</em></span>")
    if not rows:
        return ""
    items = "".join(rows)
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
    raw_page_title = str(slide["title"])
    page_title = html.escape(raw_page_title)
    slide_meta = slide["meta"] if isinstance(slide.get("meta"), dict) else {}
    animation_mode = normalize_animation_mode(slide_meta.get("animate") if isinstance(slide_meta, dict) else None)
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
        "data-body-animation": animation_mode,
    })
    classes = f"slide layout-{html.escape(layout)}"
    if animation_mode == "all":
        classes += " body-animate-page"
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
    if layout == "cover":
        raw_cover_title = deck_meta.get("title", "").strip() or raw_page_title
        cover_title_html = render_cover_title(raw_cover_title)
        subtitle = clamp_display_chars(deck_subtitle, 24)
        subtitle_html = f"<p class=\"cover-subtitle\">{html.escape(subtitle)}</p>" if subtitle else "<p class=\"cover-subtitle cover-subtitle-empty\" aria-hidden=\"true\"></p>"
        details = render_cover_details(deck_meta)
        title_class = cover_title_density_class(raw_cover_title)
        record["reveal_steps"] = []
        return (
            f"<section class=\"{classes}\" {attrs}>"
            f"<img class=\"brand-logo\" src=\"{cover_logo_uri}\" alt=\"school logo\">"
            f"<div class=\"cover-hero\">"
            f"<h1 class=\"cover-title{title_class}\">{cover_title_html}</h1>"
            f"{subtitle_html}"
            f"{details}"
            f"</div>"
            f"<img class=\"cover-slogan\" src=\"{cover_slogan_uri}\" alt=\"school slogan\">"
            f"</section>"
        )
    section_number = int(record["section_index"])
    animation_start = order_number(normalize_order(slide_meta.get("animate_order") if isinstance(slide_meta, dict) else None, "1")) or 1.0
    animation_state = {"next": animation_start}
    semantic_icon = ""
    rendered_blocks = render_blocks(
        chunk,
        input_dir,
        media_warnings,
        section_number,
        formula_counters,
        animation_mode=animation_mode,
        animation_state=animation_state,
    )
    record["reveal_steps"] = collect_reveal_steps(rendered_blocks)
    warnings = "".join(f"<aside class=\"warning\">{inline_markdown(w)}</aside>" for w in slide["warnings"])
    notes = "".join(f"<details class=\"notes\"><summary>Speaker notes</summary><p>{inline_markdown(n)}</p></details>" for n in slide["notes"])
    page_marker = f"<span class=\"page-marker\">{html.escape(str(record['page_label']))}</span>"
    title_lockup = f"<div class=\"title-lockup\"><h2>{page_title}</h2></div>"
    return (
        f"<section class=\"{classes}\" {attrs}>"
        f"<div class=\"slide-title\">{title_lockup}{page_marker}</div>"
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
    start_index: int = 1,
    page_number: int = 1,
    page_total: int = 1,
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
    for idx, section_title in enumerate(section_titles, start=start_index):
        items.append(
            f"<li data-agenda-section-index=\"{idx}\" role=\"button\" tabindex=\"0\" aria-label=\"跳转到第 {idx:02d} 章 {html.escape(section_title, quote=True)}\">"
            f"<span>{idx:02d}</span>"
            f"<strong>{html.escape(section_title)}</strong>"
            "</li>"
        )
    page_hint = f"<div class=\"agenda-page-hint\">{page_number} / {page_total}</div>" if page_total > 1 else ""
    return (
        f"<section class=\"slide layout-agenda\" {attrs}>"
        "<div class=\"agenda-kicker\">目录</div>"
        f"<ol class=\"agenda-list\">{''.join(items)}</ol>"
        f"{page_hint}"
        "<div class=\"agenda-route\" aria-hidden=\"true\"><i></i><i></i><i></i></div>"
        f"<footer class=\"slide-footer\" aria-hidden=\"true\">"
        f"<img class=\"footer-band\" src=\"{footer_uri}\" alt=\"\">"
        f"<img class=\"footer-logo\" src=\"{footer_logo_uri}\" alt=\"\">"
        f"</footer>"
        f"</section>"
    )


def render_section_divider_page_section(
    record: dict[str, object],
    section_slides: list[dict[str, object]],
    logo_uri: str,
    wave_top_uri: str,
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
        "data-layout": "section",
        "data-section-divider": "true",
        "data-print-optional": "section-divider",
    })
    section_title = html.escape(str(record["section_title"]))
    section_index = int(record["section_index"])
    return (
        f"<section class=\"slide layout-section\" {attrs}>"
        f"<img class=\"section-logo\" src=\"{logo_uri}\" alt=\"school logo\">"
        f"<img class=\"section-wave\" src=\"{wave_top_uri}\" alt=\"\" aria-hidden=\"true\">"
        f"<div class=\"section-hero\">"
        f"<span class=\"section-kicker\">第 {section_index:02d} 章</span>"
        f"<h1>{section_title}</h1>"
        f"<i aria-hidden=\"true\"></i>"
        f"</div>"
        f"</section>"
    )


def render_thumb_card(record: dict[str, object], attr_name: str, extra_class: str = "") -> str:
    layout = html.escape(str(record["layout"]))
    page_id = html.escape(str(record["page_id"]), quote=True)
    page_label = html.escape(str(record["page_label"]))
    logical_title = html.escape(str(record["logical_title"]))
    section_title = html.escape(str(record["section_title"]))
    label = f"{page_label} {logical_title}".strip()
    section_divider_attr = ' data-section-divider-entry="true"' if bool(record.get("is_section_divider")) else ""
    return (
        f"<button class=\"thumb-item {extra_class}\" {attr_name}=\"{page_id}\" data-page-index=\"{record['global_index']}\"{section_divider_attr} aria-current=\"false\" aria-label=\"{html.escape(label, quote=True)}\">"
        f"<span class=\"thumb-label\">{page_label}</span>"
        f"<div class=\"thumb-real\" aria-hidden=\"true\"></div>"
        f"<div class=\"thumb-card layout-{layout}\" aria-hidden=\"true\">"
        f"<span>{page_label}</span><strong>{logical_title}</strong><em>{section_title}</em><i></i>"
        f"</div>"
        f"</button>"
    )


def collect_reveal_steps(rendered_html: str) -> list[dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}
    for match in re.finditer(r'data-reveal-order="([^"]+)"\s+data-reveal-kind="([^"]+)"', rendered_html):
        order = html.unescape(match.group(1))
        kind = html.unescape(match.group(2))
        entry = grouped.setdefault(order, {"priority": order, "kinds": set(), "target_count": 0})
        kinds = entry["kinds"]
        if isinstance(kinds, set):
            kinds.add(kind)
        entry["target_count"] = int(entry["target_count"]) + 1
    steps: list[dict[str, object]] = []
    for idx, order in enumerate(sorted(grouped, key=order_sort_key), start=1):
        entry = grouped[order]
        kinds = entry["kinds"]
        steps.append({
            "step_index": idx,
            "priority": order,
            "kinds": sorted(kinds) if isinstance(kinds, set) else [],
            "target_count": entry["target_count"],
        })
    return steps


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
    formula_counters: dict[int, int] = {}
    layouts_used: list[str] = []
    agenda_inserted = False
    agenda_section_titles = [str(section["title"]) for section in hierarchy]
    for section_index, section in enumerate(hierarchy, start=1):
        section_title = str(section["title"])
        section_display_count = 0
        section_manifest: dict[str, object] = {
            "section_index": section_index,
            "section_title": section_title,
            "logical_slides": [],
        }
        slides = section["slides"] if isinstance(section["slides"], list) else []
        section_divider_inserted = True
        for slide in slides:
            if not isinstance(slide, dict):
                continue
            body_text = str(slide["body"])
            blocks = split_blocks(body_text)
            layout = choose_layout(slide, blocks, logical_count)
            layouts_used.append(layout)
            numbered_layout = layout not in {"cover", "closing"}
            logical_slides = section_manifest["logical_slides"]
            if numbered_layout and not section_divider_inserted and section_title != "默认章节":
                section_divider_inserted = True
                layouts_used.append("section")
                logical_count += 1
                global_index = len(page_records) + 1
                section_record: dict[str, object] = {
                    "page_id": f"p{global_index}",
                    "page_label": str(section_index),
                    "section_index": section_index,
                    "section_title": section_title,
                    "logical_index": logical_count,
                    "display_logical_index": str(section_index),
                    "logical_title": section_title,
                    "physical_index": 1,
                    "global_index": global_index,
                    "layout": "section",
                    "reveal_steps": [],
                    "is_section_divider": True,
                    "print_optional": "section-divider",
                }
                page_sections.append(render_section_divider_page_section(
                    section_record,
                    slides,
                    logo_uri,
                    wave_top_uri,
                ))
                page_records.append(section_record)
                if isinstance(logical_slides, list):
                    logical_slides.append({
                        "section_index": section_index,
                        "section_title": section_title,
                        "logical_index": logical_count,
                        "display_logical_index": str(section_index),
                        "logical_title": section_title,
                        "is_section_divider": True,
                        "print_optional": "section-divider",
                        "physical_pages": [dict(section_record)],
                        "reveal_steps": [],
                    })
            logical_count += 1
            if numbered_layout:
                section_display_count += 1
                display_logical_label = f"{section_index}.{section_display_count}"
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
                    page_label = f"{display_logical_label}.{page_idx}"
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
                reveal_steps = slide_manifest["reveal_steps"]
                if isinstance(reveal_steps, list):
                    reveal_steps.extend([
                        {
                            **step,
                            "page_id": record["page_id"],
                            "page_label": record["page_label"],
                        }
                        for step in record.get("reveal_steps", [])
                        if isinstance(step, dict)
                    ])
            if isinstance(logical_slides, list):
                logical_slides.append(slide_manifest)
                if layout == "cover" and not agenda_inserted:
                    agenda_inserted = True
                    logical_count += 1
                    agenda_physical_pages: list[dict[str, object]] = []
                    agenda_chunks = [
                        (idx, agenda_section_titles[idx : idx + 5])
                        for idx in range(0, len(agenda_section_titles), 5)
                    ] or [(0, [])]
                    for agenda_page_idx, (agenda_start, agenda_titles) in enumerate(agenda_chunks, start=1):
                        global_index = len(page_records) + 1
                        agenda_label = "目录" if len(agenda_chunks) == 1 else f"目录 {agenda_page_idx}"
                        agenda_record: dict[str, object] = {
                            "page_id": f"p{global_index}",
                            "page_label": agenda_label,
                            "section_index": section_index,
                            "section_title": section_title,
                            "logical_index": logical_count,
                            "display_logical_index": "目录",
                            "logical_title": "汇报路径",
                            "physical_index": agenda_page_idx,
                            "global_index": global_index,
                            "layout": "agenda",
                            "reveal_steps": [],
                        }
                        page_sections.append(render_agenda_page_section(
                            agenda_record,
                            agenda_titles,
                            footer_uri,
                            footer_logo_uri,
                            start_index=agenda_start + 1,
                            page_number=agenda_page_idx,
                            page_total=len(agenda_chunks),
                        ))
                        page_records.append(agenda_record)
                        agenda_physical_pages.append(dict(agenda_record))
                    logical_slides.append({
                        "section_index": section_index,
                        "section_title": section_title,
                        "logical_index": logical_count,
                        "display_logical_index": "目录",
                        "logical_title": "汇报路径",
                        "physical_pages": agenda_physical_pages,
                        "reveal_steps": [],
                    })
        manifest_sections.append(section_manifest)
    physical_count = len(page_records)
    css = """
:root{__RATIO_CSS__;--slide-design-width:1280px;--slide-design-height:calc(1280px / var(--slide-ratio));--slide-max-width:1280px;--rail-width:260px;--resizer-width:8px;--green:#579E40;--teal:#549183;--blue:#0084CC;--deep:#0E2841;--paper:#fff;--soft:#E8E8E8;--gold:#F2BA02;--line:#d8e6ec;--shadow:0 18px 42px rgba(14,40,65,.16)}
*{box-sizing:border-box}body{margin:0;background:#eef3f5;color:var(--deep);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans SC",Arial,sans-serif;letter-spacing:0;overflow:hidden;-webkit-text-size-adjust:100%;text-size-adjust:100%}
button{font:inherit;color:inherit}.app{height:100vh;display:grid;grid-template-rows:auto 1fr}.app[data-view="playback"]{display:block}.app[data-view="playback"] .app-top{display:none}.app-top{height:56px;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:0 18px;border-bottom:1px solid var(--line);background:rgba(255,255,255,.94);backdrop-filter:blur(10px);overflow:hidden}.brand-lockup{display:grid;grid-template-columns:42px minmax(0,1fr);align-items:center;gap:12px;min-width:0;max-width:min(620px,calc(100vw - 360px));height:100%}.brand-lockup img{width:42px;max-height:38px;object-fit:contain;box-shadow:none;border-radius:0;background:transparent}.brand-text{min-width:0;display:grid;gap:2px}.brand-title{display:block;color:#0056A8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.15;font-size:15px}.brand-context{display:block;min-width:0;font-size:11px;line-height:1.2;color:#58717c;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.top-actions{display:flex;align-items:center;gap:8px;flex:0 0 auto}.icon-btn{border:1px solid var(--line);background:#fff;border-radius:6px;padding:7px 12px;cursor:pointer}.icon-btn.primary{background:linear-gradient(90deg,var(--green),var(--blue));color:#fff;border:0}.icon-btn.print-toggle[aria-pressed="false"]{background:#f6fafb;color:#60757e}.current-page-chip{min-width:78px;text-align:center;color:#0056A8;font-weight:700}
.view{min-height:0}.view[hidden]{display:none!important}.workspace{display:grid;grid-template-columns:var(--rail-width) var(--resizer-width) minmax(0,1fr);height:calc(100vh - 56px);min-height:0}.thumbnail-rail{border-right:1px solid var(--line);background:#f8fbfc;overflow:auto;padding:12px}.rail-resizer{position:relative;border:0;border-left:1px solid var(--line);border-right:1px solid var(--line);background:linear-gradient(180deg,#f7fbfc,#edf4f6);cursor:col-resize;padding:0}.rail-resizer::before{content:"";position:absolute;left:50%;top:50%;width:3px;height:52px;border-radius:99px;background:linear-gradient(180deg,var(--green),var(--blue));transform:translate(-50%,-50%);opacity:.55}.rail-resizer:hover::before,.rail-resizer.is-dragging::before{opacity:1}.drawer-handle{display:none}.rail-section{margin:0 0 16px;min-width:0}.rail-section-title{margin:0 0 8px;font-size:12px;color:#0056A8;text-transform:none}.rail-logical-title{margin:10px 0 6px;font-size:13px;color:#466;font-weight:700}.rail-pages{display:grid;gap:10px;min-width:0}.thumb-item{position:relative;display:block;width:100%;min-width:0;max-width:100%;overflow:visible;border:0;background:transparent;border-radius:6px;padding:0;text-align:left;cursor:pointer}.thumb-item[aria-current="true"],.thumb-item.is-active{outline:2px solid var(--blue);outline-offset:2px;background:#fff;box-shadow:0 8px 20px rgba(0,132,204,.12)}html.hide-section-dividers [data-section-divider-entry="true"]{display:none!important}.thumb-label{position:absolute;left:5px;top:5px;z-index:4;min-width:42px;font-size:11px;font-weight:800;color:#fff;background:var(--green);border-radius:4px;text-align:center;padding:4px 6px;box-shadow:0 2px 6px rgba(14,40,65,.18)}.thumb-real{position:relative;display:grid;place-items:center;width:100%;min-width:0;max-width:100%;aspect-ratio:var(--slide-aspect);overflow:hidden;border:1px solid var(--line);border-radius:5px;background:#fff;pointer-events:none}.thumb-real .slide-scale-shell,.overview-tile .slide-scale-shell{max-width:100%;max-height:100%;overflow:hidden}.thumb-real .slide,.overview-tile .slide{overflow:hidden}.thumb-card{display:none;aspect-ratio:var(--slide-aspect);border:1px solid var(--line);border-radius:5px;background:linear-gradient(135deg,#fff,#edf7fb);padding:8px;overflow:hidden;pointer-events:none}.thumb-card span{display:inline-block;font-size:11px;font-weight:800;color:#fff;background:var(--blue);border-radius:3px;padding:2px 6px}.thumb-card strong{display:block;margin-top:8px;font-size:12px;line-height:1.22;color:#0056A8}.thumb-card em{display:block;margin-top:4px;font-style:normal;font-size:10px;color:#60757e}.thumb-card i{display:block;margin-top:8px;height:5px;background:linear-gradient(90deg,var(--green),var(--blue),var(--gold));border-radius:99px}.layout-cover.thumb-card,.layout-section.thumb-card{background:linear-gradient(135deg,var(--green),var(--blue));color:#fff}.layout-cover.thumb-card strong,.layout-cover.thumb-card em,.layout-section.thumb-card strong,.layout-section.thumb-card em{color:#fff}.layout-agenda.thumb-card{background:linear-gradient(135deg,#fff 0 68%,#edf8f6 68%);color:var(--deep);border-top:4px solid var(--blue)}.layout-agenda.thumb-card span{background:var(--green)}.layout-agenda.thumb-card strong{color:#0056A8}.layout-agenda.thumb-card em{color:#60757e}.layout-table.thumb-card{background:repeating-linear-gradient(180deg,#fff 0 17px,#e9f4f7 17px 18px)}.layout-chart.thumb-card i{height:22px;background:linear-gradient(90deg,var(--green) 68%,#e4f0f4 68%)}.layout-media-right.thumb-card,.layout-media-left.thumb-card{background:linear-gradient(90deg,#fff 0 54%,#dfeff4 54%)}.layout-quote.thumb-card{background:linear-gradient(135deg,#fff 0 76%,#f9e9a8 76%)}.layout-closing.thumb-card{background:linear-gradient(135deg,#fff 0 45%,var(--blue) 45%,var(--green) 72%,#fff 72%)}
.preview-pane{min-width:0;display:grid;grid-template-rows:1fr auto;padding:18px;gap:12px;overflow:hidden}.preview-stage{place-self:stretch;width:100%;height:100%;min-height:0;display:grid;place-items:center;overflow:hidden}.preview-stage,.playback-stage{position:relative}.slide-scale-shell{position:relative;width:var(--scaled-slide-width,var(--slide-design-width));height:var(--scaled-slide-height,var(--slide-design-height));overflow:hidden;background:#fff;contain:paint}.preview-stage .slide-scale-shell,.playback-stage .slide-scale-shell{box-shadow:var(--shadow);outline:1px solid rgba(14,40,65,.18);outline-offset:0}.thumb-real .slide-scale-shell{outline:0;box-shadow:none}.preview-stage.is-transitioning .slide-scale-shell,.playback-stage.is-transitioning .slide-scale-shell{transition:opacity .18s ease}.preview-stage.is-fade-out .slide-scale-shell,.playback-stage.is-fade-out .slide-scale-shell{opacity:.82}.preview-stage.is-fade-in .slide-scale-shell,.playback-stage.is-fade-in .slide-scale-shell{animation:stageFadeIn .18s ease both}@keyframes stageFadeIn{from{opacity:.82}to{opacity:1}}.slide-scale-shell .slide{position:absolute;left:0;top:0;width:var(--slide-design-width);height:var(--slide-design-height);max-width:none;transform:scale(var(--stage-scale,1));transform-origin:top left;pointer-events:none}.preview-meta{display:flex;align-items:center;justify-content:space-between;color:#4f6874;font-size:13px}.overview{height:calc(100vh - 56px);overflow:auto;padding:20px 24px;background:#f4f8fa}.overview-toolbar{display:flex;align-items:center;justify-content:space-between;margin:0 0 18px}.overview-grid{display:grid;gap:22px}.section-group{border-top:4px solid var(--blue);background:#fff;padding:14px;border-radius:8px;box-shadow:0 10px 28px rgba(14,40,65,.08)}.section-title{margin:0 0 12px;color:#0056A8}.overview-pages{display:grid;grid-template-columns:repeat(auto-fill,minmax(178px,1fr));gap:14px}.overview-tile{display:grid;grid-template-columns:1fr;grid-template-rows:auto auto auto;align-content:start;gap:7px;border:1px solid #d8e6ec;border-radius:8px;background:#fff;padding:10px;text-align:left;cursor:pointer;box-shadow:0 8px 20px rgba(14,40,65,.06)}.overview-tile.section-first{border-top:4px solid var(--green)}.overview-tile[aria-current="true"],.overview-tile.is-active{border-color:var(--blue);box-shadow:0 10px 28px rgba(0,132,204,.15)}.overview-tile>.thumb-label{display:none}.overview-tile .thumb-real{width:100%;border-radius:6px;border-color:#cfe2ea;background:#f8fbfc}.overview-tile b{display:block;min-width:0;margin-top:1px;font-size:13px;line-height:1.22;color:#0056A8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.overview-tile>span:not(.thumb-label){display:block;font-size:11px;line-height:1.15;color:#60757e}.playback{position:fixed;inset:0;z-index:50;height:100vh;background:#071923;display:grid;place-items:center;cursor:none}.playback-stage{width:100vw;height:100vh;display:grid;place-items:center;overflow:hidden;pointer-events:none}.progress{position:fixed;left:0;right:0;top:0;height:4px;background:rgba(255,255,255,.18);z-index:80}.progress i{display:block;width:0;height:100%;background:linear-gradient(90deg,var(--green),var(--blue));transition:width .2s}.playback-zone{position:fixed;top:0;bottom:0;border:0!important;outline:0!important;box-shadow:none!important;background:transparent!important;color:transparent!important;appearance:none;-webkit-appearance:none;-webkit-tap-highlight-color:transparent;cursor:pointer;z-index:60}.playback-zone:focus,.playback-zone:focus-visible,.playback-zone:active{border:0!important;outline:0!important;box-shadow:none!important;background:transparent!important;color:transparent!important}.playback-zone.prev{left:0;width:25vw}.playback-zone.center{left:25vw;width:50vw}.playback-zone.next{right:0;width:25vw}.playback-toolbar{position:fixed;left:50%;bottom:max(22px,env(safe-area-inset-bottom));transform:translate(-50%,10px) scale(.96);display:flex;align-items:center;gap:6px;padding:7px;border:1px solid rgba(255,255,255,.2);border-radius:999px;background:rgba(8,25,35,.72);backdrop-filter:blur(18px) saturate(140%);box-shadow:0 18px 48px rgba(0,0,0,.3),inset 0 1px 0 rgba(255,255,255,.18);opacity:0;pointer-events:none;transition:opacity .18s,transform .18s;z-index:85}.playback-control,.playback-exit,.playback-page-pill{height:38px;border:1px solid rgba(255,255,255,.16);border-radius:999px;background:rgba(255,255,255,.1);color:#fff;box-shadow:inset 0 1px 0 rgba(255,255,255,.14)}.playback-control{width:38px;display:grid;place-items:center;padding:0;font-size:24px;line-height:1;cursor:pointer}.playback-control:hover,.playback-exit:hover{background:rgba(255,255,255,.18)}.playback-page-pill{display:grid;place-items:center;min-width:64px;padding:0 14px;font-weight:800;color:#fff;background:linear-gradient(90deg,rgba(87,158,64,.86),rgba(0,132,204,.86));letter-spacing:0}.playback-exit{padding:0 14px;font-size:12px;font-weight:800;letter-spacing:.08em;cursor:pointer}.playback.show-ui{cursor:default}.playback.show-ui .playback-toolbar{opacity:1;pointer-events:auto;transform:translate(-50%,0) scale(1)}
.page-source{display:none}.deck{width:100%;display:grid;justify-items:center;gap:28px;padding:28px 0}.slide{position:relative;width:min(calc(100vw - 32px),calc((100vh - 56px) * var(--slide-ratio)),var(--slide-max-width));aspect-ratio:var(--slide-aspect);height:auto;padding:4.3% 6% 8.2%;display:grid;grid-template-rows:auto auto 1fr;overflow:hidden;isolation:isolate;background:linear-gradient(115deg,#ffffff 0%,#ffffff 58%,#edf7fb 100%);-webkit-text-size-adjust:100%;text-size-adjust:100%}
.slide::before{content:"";position:absolute;left:0;top:0;width:16px;height:100%;background:linear-gradient(180deg,var(--green),var(--blue));z-index:0}.slide::after{content:"";position:absolute;right:4%;top:2.8%;width:48%;height:8%;background:url("__WAVE_TOP__") right top/contain no-repeat;opacity:.22;z-index:0;pointer-events:none}.slide>*{position:relative;z-index:1}
.brand-logo{width:min(18%,180px);height:auto;object-fit:contain;align-self:flex-start;box-shadow:none;border-radius:0;background:transparent}.slide-title{position:relative;display:flex;align-items:end;justify-content:space-between;gap:24px;margin:1.5% 0 2%;border-bottom:3px solid var(--blue);padding-bottom:10px}
.slide-title::before{content:"";position:absolute;right:74px;bottom:-6px;width:118px;height:3px;background:linear-gradient(90deg,var(--green),var(--blue))}.slide-title::after{content:"";position:absolute;right:0;top:-9px;width:72px;height:10px;background:linear-gradient(90deg,var(--green) 0 24px,transparent 24px 31px,var(--blue) 31px 55px,transparent 55px 62px,var(--gold) 62px 72px);opacity:.9}
.title-lockup{display:flex;align-items:center;gap:14px;min-width:0}.slide-title h2{font-size:44px;line-height:1.08;margin:0;color:#0056A8;font-weight:800;min-width:0}.page-marker{font-size:16px;color:#fff;background:var(--green);padding:5px 10px;border-radius:4px;min-width:42px;text-align:center}
.semantic-icon{--icon-size:44px;position:relative;display:inline-grid;place-items:center;flex:0 0 var(--icon-size);width:var(--icon-size);height:var(--icon-size);border-radius:14px;background:linear-gradient(135deg,var(--green),var(--blue));box-shadow:0 8px 18px rgba(0,132,204,.18),inset 0 1px 0 rgba(255,255,255,.34);overflow:hidden}.semantic-icon::before,.semantic-icon::after{content:"";position:absolute;box-sizing:border-box}.semantic-icon.mini{--icon-size:30px;border-radius:9px;box-shadow:0 5px 12px rgba(0,132,204,.14)}.title-icon{margin-bottom:1px}.icon-target::before{width:25px;height:25px;border:3px solid rgba(255,255,255,.95);border-radius:50%;box-shadow:inset 0 0 0 5px rgba(255,255,255,.22)}.icon-target::after{width:7px;height:7px;border-radius:50%;background:#fff}.icon-process::before{left:12px;right:12px;top:21px;height:3px;border-radius:99px;background:#fff}.icon-process::after{left:11px;top:15px;width:8px;height:8px;border-radius:50%;background:#fff;box-shadow:11px 0 0 #fff,22px 0 0 #fff}.icon-safety::before{width:24px;height:28px;background:rgba(255,255,255,.96);clip-path:polygon(50% 0,86% 14%,80% 67%,50% 100%,20% 67%,14% 14%)}.icon-safety::after{left:14px;top:18px;width:13px;height:7px;border-left:3px solid var(--green);border-bottom:3px solid var(--green);transform:rotate(-45deg)}.icon-risk{background:linear-gradient(135deg,var(--gold),var(--blue))}.icon-risk::before{left:50%;top:6px;width:0;height:0;border-left:13px solid transparent;border-right:13px solid transparent;border-bottom:25px solid rgba(255,255,255,.96);transform:translateX(-50%)}.icon-risk::after{content:"!";left:0;right:0;top:14px;color:#0E2841;font-size:18px;font-weight:900;line-height:1;text-align:center}.icon-error{background:linear-gradient(135deg,#d9534f,var(--blue))}.icon-error::before,.icon-error::after{left:50%;top:50%;width:23px;height:4px;border-radius:99px;background:#fff;transform:translate(-50%,-50%) rotate(45deg)}.icon-error::after{transform:translate(-50%,-50%) rotate(-45deg)}.icon-formula::before{content:"fx";color:#fff;font:italic 900 20px Georgia,"Times New Roman",serif;letter-spacing:0}.icon-formula::after{right:8px;bottom:10px;width:16px;height:2px;background:rgba(255,255,255,.8);box-shadow:0 -7px 0 rgba(255,255,255,.52)}.icon-table::before{width:26px;height:22px;border:2px solid #fff;border-radius:3px;background:linear-gradient(90deg,transparent 31%,rgba(255,255,255,.85) 32% 36%,transparent 37% 64%,rgba(255,255,255,.85) 65% 69%,transparent 70%),linear-gradient(180deg,transparent 45%,rgba(255,255,255,.85) 46% 52%,transparent 53%)}.icon-chart::before{left:11px;bottom:11px;width:6px;height:13px;border-radius:2px;background:#fff;box-shadow:10px -7px 0 #fff,20px -13px 0 #fff}.icon-chart::after{left:9px;right:8px;bottom:9px;height:2px;background:rgba(255,255,255,.7)}.icon-media::before{width:27px;height:22px;border:2px solid #fff;border-radius:4px}.icon-media::after{left:12px;right:10px;bottom:12px;height:11px;background:linear-gradient(135deg,transparent 0 38%,#fff 39% 58%,transparent 59%),linear-gradient(45deg,transparent 0 34%,rgba(255,255,255,.72) 35% 58%,transparent 59%)}.icon-reveal::before{width:29px;height:18px;border:3px solid #fff;border-radius:50%;transform:rotate(-7deg)}.icon-reveal::after{width:9px;height:9px;border-radius:50%;background:#fff}.icon-review::before{width:24px;height:24px;border:3px solid #fff;border-radius:50%}.icon-review::after{left:15px;top:17px;width:12px;height:7px;border-left:3px solid #fff;border-bottom:3px solid #fff;transform:rotate(-45deg)}.semantic-icon.mini.icon-review::before{width:18px;height:18px;border-width:2px}.semantic-icon.mini.icon-review::after{left:10px;top:12px;width:9px;height:5px;border-left-width:2px;border-bottom-width:2px}.semantic-icon.mini.icon-risk::before{top:5px;border-left-width:10px;border-right-width:10px;border-bottom-width:19px}.semantic-icon.mini.icon-risk::after{top:11px;font-size:14px}.semantic-icon.mini.icon-error::before,.semantic-icon.mini.icon-error::after{width:17px;height:3px}
.icon-review::before,.icon-review::after,.icon-risk::before,.icon-risk::after,.icon-hint::before,.icon-hint::after{border:0;box-shadow:none;clip-path:none}.icon-review::before{left:50%;top:50%;width:25px;height:25px;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3E%3Cpath d='M7 15.5 12.5 21 23 9' fill='none' stroke='%23fff' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat;transform:translate(-50%,-50%)}.icon-review::after{display:none}.icon-hint::before{left:50%;top:50%;width:25px;height:25px;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3E%3Cpath d='M7 15h16M17 9l6 6-6 6' fill='none' stroke='%23fff' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat;transform:translate(-50%,-50%)}.icon-hint::after{display:none}.icon-risk{color:#fff}.icon-risk::before{left:50%;top:28%;width:4px;height:15px;border-radius:99px;background:#fff;color:#fff;transform:translateX(-50%)}.icon-risk::after{content:"";left:50%;top:72%;width:5px;height:5px;border-radius:50%;background:#fff;color:#fff;transform:translate(-50%,-50%)}.semantic-icon.mini.icon-review::before{left:50%;top:50%;width:19px;height:19px;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3E%3Cpath d='M7 15.5 12.5 21 23 9' fill='none' stroke='%23fff' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat;transform:translate(-50%,-50%)}.semantic-icon.mini.icon-review::after{display:none}.semantic-icon.mini.icon-hint::before{left:50%;top:50%;width:19px;height:19px;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3E%3Cpath d='M7 15h16M17 9l6 6-6 6' fill='none' stroke='%23fff' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat;transform:translate(-50%,-50%)}.semantic-icon.mini.icon-hint::after{display:none}.semantic-icon.mini.icon-risk::before{left:50%;top:24%;width:3px;height:10px;border-radius:99px;background:#fff;color:#fff;transform:translateX(-50%)}.semantic-icon.mini.icon-risk::after{left:50%;top:73%;width:4px;height:4px;border-radius:50%;background:#fff;color:#fff;transform:translate(-50%,-50%)}
main.slide-content,.slide main{min-height:0;overflow:hidden;font-size:28px;line-height:1.38;width:100%;max-width:none;justify-self:stretch}
.layout-cover{grid-template-rows:auto 1fr;padding:5.3% 7.2% 8.2%;color:#fff;background:radial-gradient(circle at 76% 20%,rgba(255,255,255,.2),transparent 28%),linear-gradient(115deg,rgba(87,158,64,.96),rgba(0,132,204,.96)),#0084CC}
.layout-cover::before{display:none}
.layout-cover::after{left:0;right:0;top:66.5%;bottom:auto;width:100%;height:10%;background-position:center;background-size:100% 100%;background-repeat:no-repeat;opacity:.23;filter:brightness(0) invert(1)}
.layout-cover .brand-logo{width:min(31%,310px);max-width:310px}
.cover-hero{position:absolute;left:7.2%;top:0;width:min(76%,900px);height:100%;margin:0;min-height:0}
.cover-subtitle{position:absolute;left:0;top:57%;width:82%;min-height:0;margin:0;color:rgba(255,255,255,.9);font-size:30px;font-weight:650;line-height:1.18;overflow:visible}
.cover-subtitle-empty{visibility:hidden}
.cover-hero h1{position:absolute;left:0;top:27%;width:82%;min-height:0;margin:0;color:#fff;font-size:76px;line-height:1.02;font-weight:850;letter-spacing:0;overflow:visible}.cover-hero h1 span{display:block;white-space:nowrap}
.cover-hero h1.cover-title-long{width:88%;font-size:70px;line-height:1.04}.cover-hero h1.cover-title-compact{width:92%;font-size:66px;line-height:1.05}
.cover-details{position:absolute;left:0;top:78%;display:grid;grid-template-columns:max-content max-content;align-content:start;align-items:baseline;gap:7px 28px;min-height:0;margin:0;padding-top:10px;width:min(64%,760px);overflow:visible;color:rgba(255,255,255,.68);font-size:18px}.cover-details span{min-width:0}.cover-detail-unit{grid-column:1 / -1;display:block;margin-top:1px}.cover-detail-person,.cover-detail-date{display:block}.cover-details b{font-weight:700;color:rgba(255,255,255,.5);white-space:nowrap}.cover-details em{font-style:normal;font-weight:600;color:rgba(255,255,255,.72);min-width:0}.cover-slogan{position:absolute;right:7%;bottom:7.6%;width:min(27%,330px);height:auto;max-height:122px;object-fit:contain;box-shadow:none;border-radius:0;background:transparent}.layout-cover .slide-footer{display:none}.layout-cover figure{margin:.8em 0 0}.layout-cover figure img{max-width:52%;max-height:216px;box-shadow:none;border-radius:4px}.layout-cover figcaption{display:none}
.layout-section{padding:0;background:#fff;color:#fff}.layout-section::before{left:0;right:0;top:25%;width:100%;height:75%;background:radial-gradient(circle at 76% 20%,rgba(255,255,255,.2),transparent 28%),linear-gradient(115deg,rgba(87,158,64,.96),rgba(0,132,204,.96)),#0084CC;-webkit-mask-image:linear-gradient(180deg,rgba(0,0,0,0) 0%,rgba(0,0,0,.68) 24%,rgba(0,0,0,1) 45%);mask-image:linear-gradient(180deg,rgba(0,0,0,0) 0%,rgba(0,0,0,.68) 24%,rgba(0,0,0,1) 45%);z-index:0}.layout-section::after{display:none}.section-logo{position:absolute;left:7%;top:8%;width:min(23%,230px);height:auto;box-shadow:none;border-radius:0;background:transparent}.section-wave{position:absolute;left:0;top:68%;z-index:1;width:100%;height:auto;max-width:none;max-height:none;object-fit:fill;border-radius:0;background:transparent;box-shadow:none;opacity:1;pointer-events:none}.section-hero{position:absolute;left:7%;right:8%;top:39%;display:grid;grid-template-columns:minmax(0,1fr);align-content:center;gap:18px;z-index:2}.section-kicker{display:inline-grid;justify-self:start;min-width:112px;padding:8px 17px;border-left:6px solid var(--gold);background:rgba(255,255,255,.15);color:rgba(255,255,255,.96);font-size:25px;font-weight:850;letter-spacing:0;box-shadow:inset 0 0 0 1px rgba(255,255,255,.12)}.section-hero h1{margin:0;color:#fff;font-size:84px;line-height:1.04;font-weight:850;letter-spacing:0;text-wrap:balance;text-shadow:0 12px 30px rgba(0,45,92,.3)}.section-hero i{display:block;width:min(42%,410px);height:7px;border-radius:99px;background:linear-gradient(90deg,var(--gold),rgba(255,255,255,.78),rgba(255,255,255,0))}
	.layout-agenda{padding:0;color:var(--deep);background:linear-gradient(115deg,#fff 0 62%,#edf8f6 100%)}.layout-agenda::before{left:0;top:0;width:16px;height:100%;background:linear-gradient(180deg,var(--green),var(--blue))}.layout-agenda::after{right:4%;top:3.5%;width:48%;height:8%;opacity:.2;filter:none}.agenda-kicker{position:absolute;left:20%;top:50%;transform:translate(-50%,-50%);display:block;color:#0056A8;font-size:72px;line-height:1.02;font-weight:850}.agenda-list{position:absolute;left:40%;right:7%;top:50%;height:min(548px,67%);transform:translateY(-50%);display:grid;grid-template-rows:repeat(5,minmax(0,1fr));align-content:center;gap:12px;margin:0;padding:0;list-style:none}.agenda-list li{display:grid;grid-template-columns:76px minmax(0,1fr);align-items:center;gap:20px;min-height:0;padding:10px 22px 10px 18px;border:1px solid #d8e6ec;border-left:7px solid rgba(0,132,204,.7);border-radius:8px;background:rgba(255,255,255,.88);box-shadow:0 10px 24px rgba(14,40,65,.08);cursor:pointer;pointer-events:auto;transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease}.agenda-list li:hover,.agenda-list li:focus-visible{transform:translateX(6px);border-color:rgba(0,132,204,.72);box-shadow:0 12px 28px rgba(0,132,204,.14);outline:none}.agenda-list span{display:grid;place-items:center;width:64px;height:52px;font-family:Georgia,"Times New Roman",serif;font-size:42px;line-height:1;color:var(--green);font-weight:700}.agenda-list strong{display:block;min-width:0;color:#0E2841;font-size:38px;line-height:1.12;font-weight:850}.agenda-route{position:absolute;left:36.8%;top:50%;height:min(504px,61%);width:2px;background:linear-gradient(180deg,rgba(87,158,64,.2),rgba(0,132,204,.72),rgba(242,186,2,.32));transform:translateY(-50%)}.agenda-route i{display:block;position:absolute;left:50%;width:16px;height:16px;border:4px solid var(--gold);border-radius:50%;background:#fff;box-shadow:0 0 0 7px rgba(242,186,2,.11);transform:translateX(-50%)}.agenda-route i:nth-child(1){top:0}.agenda-route i:nth-child(2){top:50%;transform:translate(-50%,-50%)}.agenda-route i:nth-child(3){bottom:0}.agenda-page-hint{position:absolute;right:7%;bottom:12.5%;color:#60757e;font-size:18px;font-weight:750}.layout-agenda .slide-footer::before{left:16px;background:linear-gradient(90deg,var(--green),rgba(0,132,204,.58),transparent)}
.layout-closing{padding:0;background:#fff}.layout-closing::before,.layout-closing::after,.layout-closing .slide-title,.layout-closing main,.layout-closing .slide-footer,.layout-closing .brand-logo{display:none}.layout-closing .closing-stage{position:absolute;inset:0;overflow:hidden;background:#fff}.layout-closing .closing-band{position:absolute;left:0;right:0;top:30%;height:31%;background:url("__CLOSING_BG__") center/cover no-repeat}.layout-closing .closing-slogan{position:absolute;left:53%;top:44%;width:min(27%,340px);transform:translate(-50%,-50%);height:auto;box-shadow:none;border-radius:0;background:transparent}.layout-closing .closing-ribbon{position:absolute;left:0;right:0;top:57%;width:100%;height:19%;object-fit:fill;box-shadow:none;border-radius:0;background:transparent}.layout-closing .closing-logo{position:absolute;left:50%;bottom:9%;width:min(30%,380px);transform:translateX(-50%);height:auto;box-shadow:none;border-radius:0;background:transparent}
.slide p{margin:0 0 28px}.slide ul{margin:6px 0 28px;padding-left:34px}.slide li{margin:8px 0}.slide h3{position:relative;margin:15px 0 13px;padding-left:18px;color:#0056A8}.slide h3::before{content:"";position:absolute;left:0;top:8px;width:8px;height:29px;background:linear-gradient(180deg,var(--green),var(--blue));border-radius:2px}.slide strong{color:#0056A8}.slide code{font-size:18px;line-height:1.25;background:#eef7fb;padding:2px 5px;border-radius:4px}
.table-wrap{position:relative;overflow:auto;margin:0 0 24px;border:1px solid #d8e6ec;border-radius:6px;background:#fff;box-shadow:0 12px 28px rgba(14,40,65,.08)}.table-wrap::before,.chart::before{content:"";position:absolute;right:0;top:0;width:74px;height:5px;background:linear-gradient(90deg,var(--green),var(--blue));z-index:2}table{width:100%;border-collapse:collapse;font-size:.84em}th{background:#0084CC;color:#fff}th,td{padding:13px 14px;border-bottom:1px solid #dfe9ee;text-align:left;vertical-align:top}tr:nth-child(even) td{background:#f7fbfc}
figure{margin:24px 0;max-width:100%;display:grid;justify-items:center;align-content:start}img,video{max-width:100%;max-height:346px;object-fit:contain;border-radius:6px;background:#fff;box-shadow:0 14px 32px rgba(14,40,65,.13)}figcaption,.caption{width:100%;font-size:21px;line-height:1.3;color:#4b6470;margin-top:8px;text-align:center}
.layout-media-right main,.layout-media-left main,.layout-media-center main,.layout-media-compare main,.layout-media-chart main{display:grid;gap:18px;align-content:start;min-width:0}.layout-media-right main,.layout-media-left main,.layout-media-chart main{justify-content:center}.layout-media-right main{grid-template-columns:minmax(440px,560px) minmax(240px,max-content);column-gap:52px;align-items:start}.layout-media-left main{grid-template-columns:minmax(240px,max-content) minmax(440px,560px);column-gap:52px;align-items:start}.layout-media-right main figure{grid-column:2;grid-row:1 / span 6;justify-self:center}.layout-media-right main > :not(figure){grid-column:1}.layout-media-left main figure{grid-column:1;grid-row:1 / span 6;justify-self:center}.layout-media-left main > :not(figure){grid-column:2}.layout-media-left main figure,.layout-media-right main figure{width:max-content;max-width:430px}.layout-media-left main img,.layout-media-right main img{max-width:430px;max-height:331px}.layout-media-center main{grid-template-columns:1fr;justify-items:center;text-align:center;align-content:start;gap:12px}.layout-media-center main figure{width:min(70%,720px)}.layout-media-center main figure img{max-height:330px}.layout-media-center main p{max-width:800px;margin-bottom:0}.layout-media-compare main{grid-template-columns:repeat(2,max-content);justify-content:center;column-gap:52px;row-gap:14px;align-content:start}.layout-media-compare main figure:nth-of-type(1){grid-column:1}.layout-media-compare main figure:nth-of-type(2){grid-column:2}.layout-media-compare main figure{width:max-content;max-width:380px;justify-self:center}.layout-media-compare main img{width:auto;max-width:380px;max-height:288px}.layout-media-compare main p,.layout-media-compare main ul,.layout-media-compare main ol,.layout-media-compare main .warning,.layout-media-compare main .notes{grid-column:1 / -1}.layout-media-chart main{grid-template-columns:minmax(260px,max-content) minmax(420px,560px);column-gap:52px;align-items:start}.layout-media-chart main .chart{grid-column:2;grid-row:1 / span 5}.layout-media-chart main figure{grid-column:1;grid-row:1 / span 5;width:max-content;max-width:430px;justify-self:center}.layout-media-chart main figure img{max-width:430px;max-height:331px}.layout-media-chart main p,.layout-media-chart main ul,.layout-media-chart main ol,.layout-media-chart main .warning,.layout-media-chart main .notes{grid-column:1 / -1}.layout-media-right main figure,.layout-media-left main figure,.layout-media-center main figure,.layout-media-compare main figure,.layout-media-chart main figure{margin:0}.layout-media-right main > :not(figure):not(.notes):not(.warning),.layout-media-left main > :not(figure):not(.notes):not(.warning),.layout-media-center main > :not(figure):not(.notes):not(.warning),.layout-media-compare main > :not(figure):not(.chart):not(.notes):not(.warning),.layout-media-chart main > :not(figure):not(.chart):not(.notes):not(.warning){min-width:0}
.layout-media-compare main p{font-size:.86em;line-height:1.34;margin-top:2px;text-align:center}
	.chart{position:relative;display:grid;gap:12px;margin:0 0 24px;background:#fff;border:1px solid #d8e6ec;border-radius:6px;padding:24px;box-shadow:0 12px 28px rgba(14,40,65,.08)}.chart-row{display:grid;grid-template-columns:190px 1fr 70px;gap:14px;align-items:center;font-size:.86em}.bar{height:24px;background:#e3eff3;border-radius:999px;overflow:hidden}.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--green),var(--blue))}
	.structure-block{width:100%;max-width:100%;margin:6px 0 22px;font-size:22px;line-height:1.32}.structure-block h3{margin:0 0 6px!important;padding:0!important;font-size:25px;line-height:1.12;color:#0056A8}.structure-block h3::before{display:none}.structure-block p{margin:0;color:#304d5a}.structure-media{margin:0!important;width:100%;min-width:0}.structure-media img{display:block;width:100%;height:100%;max-height:none;object-fit:contain;border-radius:6px;box-shadow:none;background:#f7fbfc}.structure-media.media-broken{min-height:118px;padding:12px}.timeline{display:grid;gap:13px}.timeline-item{position:relative;display:grid;grid-template-columns:126px minmax(0,1fr);gap:18px;align-items:stretch}.timeline-item::before{content:"";position:absolute;left:62px;top:46px;bottom:-18px;width:2px;background:linear-gradient(180deg,rgba(87,158,64,.65),rgba(0,132,204,.18))}.timeline-item:last-child::before{display:none}.timeline-point{display:grid;justify-items:center;align-content:start;gap:8px;color:#0056A8;font-weight:850}.timeline-point span{display:grid;place-items:center;min-width:82px;min-height:34px;padding:5px 9px;border-radius:4px;background:#eef8f5;border:1px solid rgba(87,158,64,.35);font-size:19px}.timeline-card{display:grid;grid-template-columns:minmax(0,1fr);gap:8px;min-height:86px;padding:14px 16px;border:1px solid var(--line);border-left:6px solid var(--blue);border-radius:6px;background:#fff;box-shadow:0 10px 24px rgba(14,40,65,.08)}.timeline-card-text{display:block;min-width:0}.timeline-card.has-media{grid-template-rows:112px auto;gap:11px;padding:12px 14px;overflow:hidden}.timeline-card .structure-media{height:112px;border-radius:6px;background:#eef7fb}.timeline-horizontal{grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.timeline-horizontal .timeline-item{grid-template-columns:1fr;gap:10px}.timeline-horizontal .timeline-item::before{left:50%;right:-56%;top:37px;bottom:auto;width:auto;height:2px}.timeline-horizontal .timeline-card{min-height:190px;border-left:1px solid var(--line);border-top:6px solid var(--blue)}.timeline-horizontal .timeline-card.has-media{min-height:226px}.timeline-horizontal .timeline-card.has-media h3{font-size:22px}.timeline-horizontal .timeline-card.has-media p{font-size:19px;line-height:1.24}.timeline-compact{grid-template-columns:repeat(2,minmax(0,1fr))}.timeline-compact .timeline-item{grid-template-columns:94px minmax(0,1fr);gap:12px}.timeline-compact .timeline-item::before{left:46px}.timeline-compact .timeline-card{min-height:74px;padding:12px 14px}.timeline:not(.timeline-horizontal) .timeline-card.has-media{grid-template-columns:174px minmax(0,1fr);grid-template-rows:auto}.timeline:not(.timeline-horizontal) .timeline-card.has-media .structure-media{height:118px}.card-board{display:grid;grid-template-columns:repeat(var(--card-columns),minmax(0,1fr));gap:14px}.board-card{display:grid;grid-template-columns:34px minmax(0,1fr);align-items:start;gap:12px;min-height:142px;padding:16px;border:1px solid var(--line);border-top:5px solid var(--green);border-radius:6px;background:linear-gradient(180deg,#fff,#f8fbfc);box-shadow:0 10px 24px rgba(14,40,65,.08)}.board-card small{display:inline-block;margin:0 0 7px;padding:3px 7px;border-radius:4px;background:#eef7fb;color:#0056A8;font-size:16px;font-weight:800}.card-board-metrics .board-card{grid-template-columns:1fr;min-height:112px;border-top-color:var(--blue)}.card-board-metrics .semantic-icon{margin-bottom:5px}.gallery{display:grid;gap:14px}.gallery-album{grid-template-columns:repeat(3,minmax(0,1fr))}.gallery-mosaic{grid-template-columns:1.2fr .8fr .8fr}.gallery-strip{grid-template-columns:repeat(4,minmax(0,1fr))}.gallery-item{overflow:hidden;border:1px solid var(--line);border-radius:6px;background:#fff;box-shadow:0 10px 24px rgba(14,40,65,.08)}.gallery-item .structure-media,.gallery-icon-panel{height:152px;background:#eef7fb}.gallery-mosaic .gallery-item:first-child{grid-row:span 2}.gallery-mosaic .gallery-item:first-child .structure-media{height:330px}.gallery-strip .gallery-item .structure-media,.gallery-strip .gallery-icon-panel{height:118px}.gallery-item div:last-child{padding:12px 14px}.gallery-icon-panel{display:grid;place-items:center}.smartart{display:grid;gap:13px}.smartart-item{position:relative;display:grid;grid-template-columns:38px 34px minmax(0,1fr);gap:10px;align-items:start;min-width:0;padding:14px 16px;border:1px solid var(--line);border-radius:6px;background:#fff;box-shadow:0 8px 20px rgba(14,40,65,.07)}.smartart-index{display:grid;place-items:center;width:32px;height:32px;border-radius:4px;background:linear-gradient(135deg,var(--green),var(--blue));color:#fff;font-size:17px;font-weight:900}.smartart-list-accent{grid-template-columns:repeat(2,minmax(0,1fr))}.smartart-list-stack{gap:10px}.smartart-list-columns{grid-template-columns:repeat(3,minmax(0,1fr))}.smartart-list-accent .smartart-item,.smartart-list-columns .smartart-item{grid-template-columns:34px 34px minmax(0,1fr);min-height:128px}.smartart-process{grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.smartart-process .smartart-item{grid-template-columns:1fr;min-height:166px;border-top:6px solid var(--blue)}.smartart-process-chevron .smartart-item::after,.smartart-process-ribbon .smartart-item::after{content:"";position:absolute;right:-12px;top:50%;width:22px;height:22px;border-top:4px solid rgba(0,132,204,.45);border-right:4px solid rgba(0,132,204,.45);transform:translateY(-50%) rotate(45deg);z-index:2}.smartart-process .smartart-item:last-child::after{display:none}.smartart-cycle{position:relative;grid-template-columns:repeat(4,minmax(0,1fr));padding:48px 14px}.smartart-cycle::before{content:"";position:absolute;left:25%;right:25%;top:50%;height:118px;border:5px solid rgba(0,132,204,.18);border-radius:999px;transform:translateY(-50%)}.smartart-cycle .smartart-item{grid-template-columns:1fr;min-height:132px;background:rgba(255,255,255,.96)}.smartart-cycle-segments .smartart-item{border-top:6px solid var(--green)}.smartart-hierarchy{grid-template-columns:repeat(4,minmax(0,1fr));align-items:start}.smartart-hierarchy .smartart-item:first-child{grid-column:1 / -1;justify-self:center;width:46%;border-top:6px solid var(--blue)}.smartart-hierarchy .smartart-item{grid-template-columns:34px 34px minmax(0,1fr);min-height:116px}.smartart-hierarchy-layers{grid-template-columns:1fr}.smartart-hierarchy-layers .smartart-item{width:var(--layer-width);justify-self:center}.smartart-matrix{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.smartart-matrix .smartart-item{grid-template-columns:34px 34px minmax(0,1fr);min-height:128px}.smartart-matrix-axis{padding:22px;border-left:4px solid var(--green);border-bottom:4px solid var(--blue);background:linear-gradient(135deg,rgba(87,158,64,.06),rgba(0,132,204,.05))}.smartart-matrix-grid .smartart-item:nth-child(odd){border-left:6px solid var(--green)}.smartart-matrix-grid .smartart-item:nth-child(even){border-left:6px solid var(--blue)}.smartart-pyramid{display:flex;flex-direction:column-reverse;align-items:center;gap:8px}.smartart-pyramid .smartart-item{grid-template-columns:42px 34px minmax(0,1fr);width:var(--pyramid-width);min-height:76px;text-align:center;background:linear-gradient(90deg,rgba(87,158,64,.08),rgba(0,132,204,.08),#fff)}.smartart-pyramid-inverted{flex-direction:column}.smartart-picture{grid-template-columns:repeat(3,minmax(0,1fr))}.smartart-picture .smartart-item{grid-template-columns:1fr;grid-template-rows:126px auto;gap:9px;min-height:0;padding:10px}.smartart-picture .smartart-index{position:absolute;left:10px;top:10px;z-index:3}.smartart-picture .semantic-icon{display:none}.smartart-picture .structure-media{height:126px;grid-row:1}.smartart-picture .smartart-item>div{grid-row:2;padding:0 4px}.smartart-picture .smartart-item h3{font-size:22px}.smartart-picture .smartart-item p{font-size:18px;line-height:1.24}.smartart-picture-strip{grid-template-columns:repeat(4,minmax(0,1fr))}.smartart-picture-strip .smartart-item{grid-template-rows:108px auto}.smartart-picture-strip .structure-media{height:108px}
.smartart-cycle{display:block;position:relative;min-height:360px;padding:10px 18px;margin-top:2px}.smartart-cycle::before{content:"";position:absolute;left:50%;top:50%;width:360px;height:224px;border:7px solid rgba(0,132,204,.2);border-top-color:rgba(87,158,64,.55);border-right-color:rgba(0,132,204,.48);border-bottom-color:rgba(242,186,2,.45);border-left-color:rgba(87,158,64,.42);border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.72) 0 54%,rgba(0,132,204,.05) 55% 100%);transform:translate(-50%,-50%)}.smartart-cycle::after{content:"";position:absolute;left:50%;top:50%;width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,rgba(87,158,64,.18),rgba(0,132,204,.16));box-shadow:inset 0 0 0 2px rgba(255,255,255,.8),0 0 0 10px rgba(255,255,255,.38);transform:translate(-50%,-50%)}.smartart-cycle .smartart-item{position:absolute;z-index:2;width:250px;min-height:92px;grid-template-columns:34px 34px minmax(0,1fr);gap:9px;align-items:start;border-left:6px solid var(--green);border-top:1px solid var(--line);background:rgba(255,255,255,.97)}.smartart-cycle .smartart-item h3{font-size:22px!important}.smartart-cycle .smartart-item p{font-size:18px;line-height:1.24}.smartart-cycle .smartart-item:nth-child(1){left:50%;top:0;transform:translateX(-50%)}.smartart-cycle .smartart-item:nth-child(2){right:18px;top:50%;transform:translateY(-50%);border-left-color:var(--blue)}.smartart-cycle .smartart-item:nth-child(3){left:50%;bottom:0;transform:translateX(-50%);border-left-color:var(--gold)}.smartart-cycle .smartart-item:nth-child(4){left:18px;top:50%;transform:translateY(-50%)}.smartart-cycle .smartart-item::after{content:"";position:absolute;z-index:3;width:34px;height:34px;border-top:5px solid rgba(0,132,204,.55);border-right:5px solid rgba(0,132,204,.55);border-radius:3px}.smartart-cycle .smartart-item:nth-child(1)::after{right:-54px;top:62px;transform:rotate(45deg)}.smartart-cycle .smartart-item:nth-child(2)::after{left:72px;bottom:-48px;transform:rotate(135deg)}.smartart-cycle .smartart-item:nth-child(3)::after{left:-54px;top:22px;transform:rotate(225deg)}.smartart-cycle .smartart-item:nth-child(4)::after{right:72px;top:-48px;transform:rotate(315deg)}.gallery{gap:16px;align-items:start}.gallery-album,.gallery-mosaic{grid-template-columns:repeat(3,minmax(0,1fr))}.gallery-item{display:grid;grid-template-rows:168px minmax(116px,auto);min-width:0;border-radius:7px}.gallery-mosaic .gallery-item:first-child{grid-row:auto}.gallery-item .structure-media,.gallery-icon-panel,.gallery-mosaic .gallery-item:first-child .structure-media{height:168px;background:#eef7fb;border-bottom:1px solid #dceaf0}.gallery-item .structure-media img{padding:0;object-fit:contain}.gallery-copy{display:grid;align-content:start;gap:7px;min-width:0;padding:13px 15px 15px;background:linear-gradient(180deg,#fff,#f8fbfc)}.gallery-copy h3{font-size:23px!important;line-height:1.12}.gallery-copy p{font-size:18px;line-height:1.28}.gallery-strip .gallery-item{grid-template-rows:118px minmax(96px,auto)}.gallery-strip .gallery-item .structure-media,.gallery-strip .gallery-icon-panel{height:118px}.gallery-strip .gallery-copy{padding:10px 12px}.gallery-strip .gallery-copy h3{font-size:20px!important}.gallery-strip .gallery-copy p{font-size:16px;line-height:1.22}
.gallery-item .structure-media{overflow:hidden;display:grid;place-items:center}.gallery-item .structure-media img{width:100%!important;height:100%!important;max-height:100%!important;object-fit:contain!important}
	.formula{position:relative;display:grid;gap:12px;margin:12px 0 24px;padding:18px 24px;background:#f7fbfc;border-radius:4px;font-family:Georgia,"Times New Roman",serif;font-size:1.16em;color:#0056A8}.formula-row{position:relative;display:flex;align-items:center;justify-content:center;min-height:1.55em;padding:0 6em}.formula-line{white-space:normal;line-height:1.5;text-align:center}.formula-number{position:absolute;right:0;top:50%;transform:translateY(-50%);font-family:"Noto Sans SC",Arial,sans-serif;font-size:.78em;color:#0E2841;white-space:nowrap}.formula-line var{font-style:italic}.math-fn{font-style:normal;font-family:Georgia,"Times New Roman",serif}.math-op{display:inline-block;margin:0 .18em}.math-sqrt{display:inline-flex;align-items:flex-start;vertical-align:-.18em;margin:0 .12em}.math-radical{font-size:1.22em;line-height:1.08;margin-right:-.04em}.math-radicand{display:inline-block;border-top:2px solid currentColor;padding:.04em .08em 0 .1em;line-height:1.05}.math-frac{display:inline-grid;grid-template-rows:auto auto;place-items:center;vertical-align:-.45em;margin:0 .14em}.math-frac span:first-child{border-bottom:1.5px solid currentColor;padding:0 .2em .05em}.math-frac span:last-child{padding:.05em .2em 0}
.alert{display:grid;grid-template-columns:30px minmax(0,1fr);align-items:start;gap:10px;margin:0 0 18px;padding:14px 16px;border-left:6px solid;border-radius:6px;background:#f7fbfc;font-size:25px;line-height:1.32;break-inside:avoid}.alert:last-child{margin-bottom:0}.alert strong{display:block;font-size:20px;line-height:1.1;letter-spacing:0;text-transform:none}.alert p{margin:4px 0 0;line-height:1.34}.alert-info{border-color:#5b9bd5;background:#eef7ff;color:#164a78}.alert-tip{border-color:#5cb85c;background:#eef9ef;color:#2a5d2a}.alert-warning{border-color:#F2BA02;background:#fff8df;color:#675100}.alert-error{border-color:#d9534f;background:#fff1f0;color:#8d1f1f}.hover-zoom,.peek-trigger{position:relative;display:inline-block;pointer-events:auto;cursor:zoom-in;border-radius:5px;transition:transform .2s ease,color .2s ease,background .2s ease;transform-origin:center;will-change:transform}.hover-zoom:hover,.hover-zoom:focus-visible{transform:scale(var(--hover-zoom-scale,1.16));background:rgba(0,132,204,.08);outline:none}.hover-zoom:hover+.hover-zoom,.hover-zoom:has(+ .hover-zoom:hover){transform:scale(1.07)}.peek-trigger{color:#0056A8;text-decoration:underline;text-decoration-thickness:3px;text-decoration-color:rgba(87,158,64,.45);text-underline-offset:5px}.peek-trigger:hover,.peek-trigger:focus-visible{background:rgba(87,158,64,.08);outline:none}.peek-template{display:none}.peek-trigger-card{position:relative;display:grid;grid-template-columns:34px minmax(0,1fr);align-items:center;gap:12px;width:min(100%,640px);margin:10px 0 18px;padding:14px 16px;border:1px solid rgba(0,132,204,.24);border-left:6px solid var(--green);border-radius:7px;background:linear-gradient(180deg,#fff,#f7fbfc);box-shadow:0 10px 24px rgba(14,40,65,.08);text-align:left;cursor:zoom-in;pointer-events:auto;transition:transform .2s ease,border-color .2s ease,box-shadow .2s ease}.peek-trigger-card:hover,.peek-trigger-card:focus-visible{transform:translateY(-2px);border-color:rgba(0,132,204,.58);box-shadow:0 14px 30px rgba(0,132,204,.14);outline:none}.peek-trigger-card strong{display:block;color:#0056A8;font-size:24px;line-height:1.16}.peek-trigger-card small{display:block;margin-top:3px;color:#60757e;font-size:17px;line-height:1.2}.playback .peek-trigger,.playback .peek-trigger-card,.playback .hover-zoom{z-index:70}.peek-popover{position:fixed;left:0;top:0;z-index:120;max-width:calc(100vw - 48px);max-height:calc(100vh - 48px);opacity:0;transform:translateY(8px) scale(.98);pointer-events:none;transition:opacity .18s ease,transform .18s ease}.peek-popover.is-open{opacity:1;transform:translateY(0) scale(1);pointer-events:auto}.peek-panel{display:grid;gap:12px;width:min(560px,calc(100vw - 48px));max-height:calc(100vh - 64px);overflow:auto;padding:18px 20px;border:1px solid rgba(0,132,204,.26);border-radius:8px;background:rgba(255,255,255,.97);box-shadow:0 24px 70px rgba(14,40,65,.24),inset 0 1px 0 rgba(255,255,255,.9);backdrop-filter:blur(14px) saturate(130%);color:var(--deep)}.peek-panel.has-media{width:min(820px,calc(100vw - 48px));min-width:min(640px,calc(100vw - 48px))}.peek-title{display:block;color:#0056A8;font-size:24px;line-height:1.18}.peek-body{margin:0;font-size:20px;line-height:1.45;color:#263f4d}.peek-body p{margin:0 0 .55em}.peek-body p:last-child{margin-bottom:0}.peek-media{display:block;width:100%;min-height:min(48vh,420px);max-height:calc(100vh - 210px);object-fit:contain;border-radius:6px;background:#eef6f8}.peek-media.media-broken{min-height:min(48vh,420px);align-content:center}.reveal-target{position:relative}.inline-reveal{display:inline-grid;vertical-align:baseline}.reveal-content{position:relative;z-index:1}.playback .reveal-kind-animate:not(.is-revealed){visibility:hidden}.playback .reveal-kind-reveal:not(.is-revealed){visibility:hidden}.playback .reveal-kind-reveal:not(.is-revealed)::after{content:"";visibility:visible;position:absolute;inset:-4px -7px;border-radius:6px;background:linear-gradient(90deg,#e8f2f5,#dbecef);border:1px solid rgba(0,132,204,.22)}.playback .reveal-kind-mask:not(.is-revealed)>.reveal-content{visibility:hidden}.playback .reveal-kind-mask:not(.is-revealed)::after{content:"";position:absolute;inset:-4px -7px;border-radius:6px;background:linear-gradient(90deg,#e8f2f5,#dbecef);border:1px solid rgba(0,132,204,.24);box-shadow:inset 0 0 0 1px rgba(255,255,255,.65);z-index:2}.playback .reveal-kind-mask.is-newly-revealed::after,.playback .reveal-kind-reveal.is-newly-revealed::after{content:"";position:absolute;inset:-4px -7px;border-radius:6px;background:linear-gradient(90deg,#e8f2f5,#dbecef);border:1px solid rgba(0,132,204,.22);z-index:2;pointer-events:none;animation:maskClear .24s ease both}.playback .reveal-kind-animate.is-newly-revealed,.playback .reveal-kind-mask.is-newly-revealed>.reveal-content,.playback .reveal-kind-reveal.is-newly-revealed>.reveal-content{animation:bodyEnter .22s ease both}.playback .body-animate-page main.slide-content>*{animation:bodyEnter .24s ease both}.reveal-kind-emphasis.is-revealed,.emphasis-underline.is-revealed{text-decoration:underline;text-decoration-thickness:5px;text-decoration-color:rgba(242,186,2,.88);text-underline-offset:7px;background:rgba(87,158,64,.08);border-radius:4px}.playback .reveal-kind-emphasis.is-newly-revealed{animation:emphasisSettle .22s ease both}@keyframes bodyEnter{from{opacity:.35;transform:translateY(7px)}to{opacity:1;transform:translateY(0)}}@keyframes maskClear{from{opacity:1;clip-path:inset(0 0 0 0)}to{opacity:0;clip-path:inset(0 0 0 100%)}}@keyframes emphasisSettle{from{opacity:.78;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}.sort-list{display:grid;gap:12px;margin:0 0 20px}.sort-item{display:grid;grid-template-columns:44px 1fr;align-items:center;gap:14px;border:1px solid var(--line);border-radius:6px;background:#fff;padding:10px 14px;transition:border-color .2s,background .2s}.sort-item i{display:grid;place-items:center;width:34px;height:34px;border-radius:6px;background:var(--blue);color:#fff;font-style:normal;font-weight:850;opacity:1;transform:scale(1);transition:opacity .2s,transform .2s}.playback .sort-item:not(.is-revealed) i{opacity:0;transform:scale(.88)}.sort-list.is-sorted .sort-item{order:var(--sort-order);background:#f4fbf2;border-color:rgba(87,158,64,.62)}.sort-list.is-sorting .sort-item{box-shadow:0 8px 18px rgba(0,132,204,.12)}@media(prefers-reduced-motion:reduce){.hover-zoom,.peek-trigger,.peek-trigger-card,.peek-popover,.playback .reveal-kind-animate.is-newly-revealed,.playback .reveal-kind-mask.is-newly-revealed>.reveal-content,.playback .reveal-kind-reveal.is-newly-revealed>.reveal-content,.playback .reveal-kind-mask.is-newly-revealed::after,.playback .reveal-kind-reveal.is-newly-revealed::after,.playback .reveal-kind-emphasis.is-newly-revealed,.playback .body-animate-page main.slide-content>*{animation:none;transition:none}.hover-zoom:hover,.hover-zoom:focus-visible,.hover-zoom:hover+.hover-zoom,.hover-zoom:has(+ .hover-zoom:hover),.peek-trigger-card:hover,.peek-trigger-card:focus-visible,.peek-popover{transform:none}.sort-item,.sort-item i{transition:none}}.notes{display:none}.video-fallback,.missing-media{display:grid;grid-template-rows:auto auto;align-content:center;justify-items:center;row-gap:9px;width:100%;min-height:150px;margin:0 0 24px;padding:16px 20px;border:1.5px dashed #9fb7c4;border-radius:6px;background:#f7fbfd;text-align:center}.media-broken figcaption{margin:0;font-size:0;line-height:1.1;color:#526a76}.media-broken code,.media-broken a{display:inline-block;max-width:100%;font-family:"SFMono-Regular",Consolas,monospace;font-size:16px;line-height:1.2;color:#526a76;text-decoration:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.broken-media-icon{position:relative;width:72px;height:58px;border:4px solid #8ea8b6;border-radius:6px;background:linear-gradient(135deg,#fff 0 47%,#eef5f7 48% 52%,#fff 53% 100%);box-shadow:inset 0 0 0 2px #f0f5f7}.broken-media-icon::before{content:"";position:absolute;left:31px;top:4px;width:8px;height:48px;background:#c05050;clip-path:polygon(38% 0,100% 0,64% 28%,100% 28%,55% 58%,88% 58%,28% 100%,0 100%,36% 66%,0 66%,45% 34%,12% 34%);transform:rotate(14deg);opacity:.92}.broken-media-icon::after{content:"";position:absolute;right:10px;top:9px;width:12px;height:12px;border-radius:50%;background:#9fb7c4}.broken-video{border-radius:8px}.broken-video::before{left:24px;right:auto;top:13px;bottom:auto;width:0;height:0;border-top:14px solid transparent;border-bottom:14px solid transparent;border-left:23px solid #8ea8b6;background:none;clip-path:none;transform:none}.broken-video::after{left:12px;right:12px;top:50%;width:auto;height:0;border-radius:0;border-top:4px solid #c05050;background:none;transform:rotate(-18deg)}
.smartart-picture{gap:16px}.smartart-picture .smartart-item{display:grid;grid-template-columns:1fr;grid-template-rows:158px minmax(96px,auto);gap:0;min-height:0;padding:0;overflow:hidden;border-radius:7px}.smartart-picture .smartart-index{left:10px;top:10px;z-index:4;box-shadow:0 4px 12px rgba(14,40,65,.18)}.smartart-picture .structure-media{position:relative;grid-row:1;height:158px;margin:0!important;overflow:hidden;border-bottom:1px solid #dceaf0;background:#eef7fb}.smartart-picture .structure-media img{position:absolute!important;inset:0!important;width:100%!important;height:100%!important;max-width:100%!important;max-height:100%!important;object-fit:contain!important;box-shadow:none}.smartart-picture .smartart-item>div{grid-row:2;padding:13px 15px 15px;background:linear-gradient(180deg,#fff,#f8fbfc)}.smartart-picture .smartart-item h3{font-size:23px!important;line-height:1.12}.smartart-picture .smartart-item p{font-size:18px;line-height:1.28}.smartart-picture-strip .smartart-item{grid-template-rows:118px minmax(88px,auto)}.smartart-picture-strip .structure-media{height:118px}.smartart-picture-strip .smartart-item>div{padding:10px 12px}.smartart-picture-strip .smartart-item h3{font-size:20px!important}.smartart-picture-strip .smartart-item p{font-size:16px;line-height:1.22}.gallery-item .structure-media{position:relative}.gallery-item .structure-media img{position:absolute!important;inset:0!important;width:100%!important;height:100%!important;max-width:100%!important;max-height:100%!important;object-fit:contain!important}
.playback .reveal-kind-mask:not(.inline-reveal):not(.is-revealed)::after,.playback .reveal-kind-reveal:not(.inline-reveal):not(.is-revealed)::after,.playback .reveal-kind-mask:not(.inline-reveal).is-newly-revealed::after,.playback .reveal-kind-reveal:not(.inline-reveal).is-newly-revealed::after{left:0;right:0;box-sizing:border-box}
.timeline-media{display:none}.timeline-horizontal.timeline-with-media{grid-template-columns:1fr;gap:12px}.timeline-horizontal.timeline-with-media .timeline-track{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.timeline-horizontal.timeline-with-media .timeline-item{grid-template-columns:1fr;gap:8px}.timeline-horizontal.timeline-with-media .timeline-item::before{left:50%;right:-56%;top:37px;bottom:auto;width:auto;height:2px}.timeline-horizontal.timeline-with-media .timeline-item:last-child::before{display:none}.timeline-horizontal.timeline-with-media .timeline-card{min-height:118px;padding:11px 14px;border-left:1px solid var(--line);border-top:6px solid var(--blue)}.timeline-horizontal.timeline-with-media .timeline-item.has-media .timeline-card{border-top-color:var(--green);background:linear-gradient(180deg,#fff,#f5fbf7)}.timeline-horizontal.timeline-with-media .timeline-card h3{font-size:22px!important;line-height:1.08;margin-bottom:4px!important}.timeline-horizontal.timeline-with-media .timeline-card p{font-size:17px;line-height:1.18}.timeline-feature-panel{display:grid;gap:12px;min-width:0}.timeline-feature-card{display:grid;grid-template-columns:minmax(260px,360px) minmax(0,1fr);gap:16px;align-items:stretch;min-height:300px;padding:12px;border:1px solid #d8e6ec;border-radius:7px;background:linear-gradient(180deg,#fff,#f7fbfc);box-shadow:0 10px 24px rgba(14,40,65,.08)}.timeline-feature-card .structure-media{position:relative;height:100%;min-height:276px;margin:0!important;overflow:hidden;border-radius:6px;background:#eef7fb;border:1px solid #dceaf0}.timeline-feature-card .structure-media img{position:absolute!important;inset:0!important;width:100%!important;height:100%!important;max-width:100%!important;max-height:100%!important;object-fit:contain!important;box-shadow:none}.timeline-feature-caption{display:grid;align-content:center;gap:8px;min-width:0;padding:14px 18px;border-left:5px solid var(--green);background:rgba(238,248,245,.72);border-radius:5px}.timeline-feature-caption small{color:var(--green);font-size:19px;line-height:1;font-weight:850}.timeline-feature-caption strong{color:#0056A8;font-size:30px;line-height:1.12}.timeline-feature-caption span{color:#304d5a;font-size:21px;line-height:1.32}.timeline:not(.timeline-horizontal) .timeline-card.has-media{grid-template-columns:174px minmax(0,1fr);grid-template-rows:auto}.timeline:not(.timeline-horizontal) .timeline-card.has-media .structure-media{height:118px}
.slide-footer{position:absolute;left:0;right:0;bottom:0;width:100%;z-index:2;pointer-events:none}.slide-footer::before{content:"";position:absolute;left:16px;right:0;top:-2px;height:2px;background:linear-gradient(90deg,rgba(87,158,64,.85),rgba(0,132,204,.45),transparent)}.footer-band{display:block;width:100%;height:auto;max-height:none;object-fit:fill;box-shadow:none;border-radius:0;background:transparent}.footer-logo{position:absolute;left:3.4%;bottom:12%;width:13.5%;min-width:118px;max-width:178px;height:auto;box-shadow:none;border-radius:0;background:transparent}
@media print{body{overflow:visible}.app-top,.thumbnail-rail,.rail-resizer,.drawer-handle,.preview-meta,.overview,.playback,.page-source{display:none!important}.workspace{display:block;height:auto}.preview-stage{width:100%;display:block}.slide-scale-shell{width:100%;height:auto}.slide-scale-shell .slide{position:relative;transform:none}.preview-stage .slide{page-break-after:always;width:100%;height:auto;box-shadow:none}html.skip-section-dividers .slide[data-section-divider="true"]{display:none!important}}@media(max-width:1040px){:root{--rail-width:230px}.preview-pane{padding:14px}.brand-lockup{max-width:calc(100vw - 230px);grid-template-columns:38px minmax(0,1fr)}.brand-lockup img{width:38px;max-height:34px}.brand-context{display:none}.top-actions .icon-btn{padding:7px 10px}.thumb-label{font-size:11px}}@media(max-width:680px){body{overflow:hidden}.app-top{position:sticky;top:0;z-index:40;padding:0 10px}.workspace{grid-template-columns:1fr;height:calc(100vh - 56px);overflow:hidden}.thumbnail-rail{position:fixed;left:0;top:56px;bottom:0;width:min(84vw,330px);max-width:calc(100vw - 44px);z-index:45;border-right:1px solid var(--line);border-bottom:0;box-shadow:18px 0 46px rgba(14,40,65,.22);transform:translateX(calc(-100% - 2px));transition:transform .24s cubic-bezier(.22,1,.36,1);max-height:none}.app.rail-open .thumbnail-rail{transform:translateX(0)}.rail-resizer{display:none}.drawer-handle{position:fixed;left:0;top:50%;z-index:46;display:grid;place-items:center;width:34px;height:76px;border:1px solid rgba(0,132,204,.28);border-left:0;border-radius:0 16px 16px 0;background:linear-gradient(180deg,var(--green),var(--blue));color:#fff;font-weight:850;box-shadow:0 10px 28px rgba(14,40,65,.24);transform:translateY(-50%);cursor:pointer}.drawer-handle::before{content:"☰";font-size:20px;line-height:1}.app.rail-open .drawer-handle{left:min(84vw,330px);transform:translate(-34px,-50%);border-radius:16px;background:rgba(14,40,65,.86);backdrop-filter:blur(12px)}.preview-pane{height:100%;min-height:0;padding:12px 10px 10px}.preview-meta{font-size:12px}.thumb-real{display:none}.thumb-card{display:block}.overview{height:auto}.brand-title{font-size:13px}.current-page-chip{min-width:46px}.top-actions{gap:5px}.top-actions .icon-btn{padding:7px 8px}}
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
            logical_heading = f"{display_logical_index} {logical['logical_title']}"
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
let currentRevealStep = 0;
let viewMode = 'workspace';
let toolbarTimer = null;
let transitionSerial = 0;
let manualRevealKeys = new Set();
let showSectionDividers = true;

function sourcePage(page) {{
  return document.querySelector('.page-source [data-page-id=\"' + page.page_id + '\"]');
}}

function maxRevealStep(page) {{
  return Array.isArray(page.reveal_steps) ? page.reveal_steps.length : 0;
}}

function isSectionDividerPage(page) {{
  return page?.is_section_divider === true || page?.print_optional === 'section-divider';
}}

function isPageVisibleInUi(page) {{
  return showSectionDividers || !isSectionDividerPage(page);
}}

function visiblePageIndexes() {{
  return pages.map((page, index) => isPageVisibleInUi(page) ? index : -1).filter((index) => index >= 0);
}}

function nearestVisiblePageIndex(index, direction = 1) {{
  if (!pages.length) return -1;
  const clamped = Math.max(0, Math.min(pages.length - 1, index));
  if (isPageVisibleInUi(pages[clamped])) return clamped;
  const primary = direction >= 0 ? 1 : -1;
  for (let i = clamped + primary; i >= 0 && i < pages.length; i += primary) {{
    if (isPageVisibleInUi(pages[i])) return i;
  }}
  for (let i = clamped - primary; i >= 0 && i < pages.length; i -= primary) {{
    if (isPageVisibleInUi(pages[i])) return i;
  }}
  return clamped;
}}

	function adjacentVisiblePageIndex(index, direction) {{
	  const step = direction >= 0 ? 1 : -1;
	  for (let i = index + step; i >= 0 && i < pages.length; i += step) {{
	    if (isPageVisibleInUi(pages[i])) return i;
	  }}
	  return -1;
	}}

	function agendaTargetPageIndex(sectionIndex) {{
	  const targetSection = Number(sectionIndex);
	  if (!Number.isFinite(targetSection)) return -1;
	  const sectionPages = pages
	    .map((page, index) => ({{page, index}}))
	    .filter((entry) => Number(entry.page.section_index) === targetSection);
	  if (!sectionPages.length) return -1;
	  const divider = sectionPages.find((entry) => isSectionDividerPage(entry.page) && isPageVisibleInUi(entry.page));
	  if (showSectionDividers && divider) return divider.index;
	  const firstContent = sectionPages.find((entry) => (
	    isPageVisibleInUi(entry.page)
	    && !isSectionDividerPage(entry.page)
	    && !['cover','agenda','closing'].includes(String(entry.page.layout || ''))
	  ));
	  if (firstContent) return firstContent.index;
	  const firstVisible = sectionPages.find((entry) => isPageVisibleInUi(entry.page));
	  return firstVisible ? firstVisible.index : -1;
	}}

	function navigateAgendaSection(sectionIndex) {{
	  const target = agendaTargetPageIndex(sectionIndex);
	  if (target < 0) return;
	  selectPage(target, {{animate:true, direction: target >= currentPageIndex ? 1 : -1}});
	  if (isMobileRailMode()) closeRailDrawer();
	}}

function visiblePriorities(page, stepIndex) {{
  const steps = Array.isArray(page.reveal_steps) ? page.reveal_steps : [];
  return new Set(steps.filter((step) => Number(step.step_index) <= stepIndex).map((step) => String(step.priority)));
}}

	function revealTargetKey(page, target, index) {{
	  return page.page_id + ':' + index + ':' + (target.dataset.revealKind || '') + ':' + (target.dataset.revealOrder || '');
	}}

	function stepSatisfiedBeforeAdvance(page, stepIndex, currentStep) {{
	  const step = Array.isArray(page.reveal_steps) ? page.reveal_steps.find((item) => Number(item.step_index) === stepIndex) : null;
	  if (!step) return false;
	  const order = String(step.priority);
	  const priorities = visiblePriorities(page, currentStep);
	  const stage = document.getElementById('playback-stage');
	  if (!stage) return false;
	  const targets = [...stage.querySelectorAll('[data-reveal-order]')];
	  const stepTargets = targets
	    .map((target, index) => ({{target, index}}))
	    .filter((entry) => String(entry.target.dataset.revealOrder) === order);
	  if (!stepTargets.length) return false;
	  return stepTargets.every((entry) => (
	    priorities.has(order) || manualRevealKeys.has(revealTargetKey(page, entry.target, entry.index))
	  ));
	}}

	function nextPendingRevealStep(page) {{
	  const maxStep = maxRevealStep(page);
	  for (let step = currentRevealStep + 1; step <= maxStep; step += 1) {{
	    if (!stepSatisfiedBeforeAdvance(page, step, currentRevealStep)) return step;
	  }}
	  return maxStep + 1;
	}}

function captureSortItemRects(list) {{
  return new Map([...list.querySelectorAll(':scope > .sort-item')].map((item) => [item, item.getBoundingClientRect()]));
}}

function stageScaleFor(element) {{
  const shell = element.closest('.slide-scale-shell');
  const raw = shell ? getComputedStyle(shell).getPropertyValue('--stage-scale') : '1';
  const scale = Number.parseFloat(raw);
  return Number.isFinite(scale) && scale > 0 ? scale : 1;
}}

function animateSortFinal(list, beforeRects) {{
  const items = [...list.querySelectorAll(':scope > .sort-item')];
  const moving = [];
  const scale = stageScaleFor(list);
  items.forEach((item) => {{
    const before = beforeRects.get(item);
    if (!before) return;
    const after = item.getBoundingClientRect();
    const dx = (before.left - after.left) / scale;
    const dy = (before.top - after.top) / scale;
    if (Math.abs(dx) < 0.5 && Math.abs(dy) < 0.5) return;
    item.style.transition = 'none';
    item.style.transform = 'translate(' + dx.toFixed(2) + 'px,' + dy.toFixed(2) + 'px)';
    item.style.zIndex = '3';
    moving.push(item);
  }});
  if (!moving.length) return;
  list.classList.add('is-sorting');
  list.getBoundingClientRect();
  requestAnimationFrame(() => {{
    moving.forEach((item) => {{
      item.style.transition = 'transform .28s ease, border-color .2s, background .2s';
      item.style.transform = 'translate(0,0)';
    }});
    window.setTimeout(() => {{
      list.classList.remove('is-sorting');
      moving.forEach((item) => {{
        item.style.transition = '';
        item.style.transform = '';
        item.style.zIndex = '';
      }});
    }}, 330);
  }});
}}

function applyRevealStateToRoot(root, page, stepIndex, showAll = false, options = {{}}) {{
  if (!root) return;
  const priorities = visiblePriorities(page, showAll ? maxRevealStep(page) : stepIndex);
  const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  const animateNew = options.animateNew === true && !showAll && !reduceMotion;
  const previousPriorities = animateNew ? visiblePriorities(page, Number(options.previousStep) || 0) : new Set();
  root.querySelectorAll('[data-reveal-order]').forEach((target, index) => {{
    target.classList.remove('is-newly-revealed');
    const order = String(target.dataset.revealOrder);
	    const manualVisible = manualRevealKeys.has(revealTargetKey(page, target, index));
	    const visible = showAll || priorities.has(String(target.dataset.revealOrder)) || manualVisible;
	    const animateSort = animateNew && visible && target.dataset.revealKind === 'sort-final' && priorities.has(order) && !previousPriorities.has(order);
	    const sortRects = animateSort ? captureSortItemRects(target) : null;
	    target.classList.toggle('is-revealed', visible);
	    const shouldAnimateTarget = animateNew && visible && priorities.has(order) && !previousPriorities.has(order) && !manualVisible;
    if (shouldAnimateTarget && ['animate','mask','reveal','emphasis'].includes(target.dataset.revealKind || '')) {{
      target.classList.add('is-newly-revealed');
      window.setTimeout(() => target.classList.remove('is-newly-revealed'), 320);
    }}
    if (target.dataset.revealKind === 'sort-final') {{
      target.classList.toggle('is-sorted', visible);
      if (sortRects) animateSortFinal(target, sortRects);
    }}
  }});
}}

function resetManualRevealState() {{
  manualRevealKeys = new Set();
}}

function buildStageShell(page, stepIndex = maxRevealStep(page), showAll = true, options = {{}}) {{
  const source = sourcePage(page);
  if (!source) return null;
  const shell = document.createElement('div');
  shell.className = 'slide-scale-shell';
  shell.appendChild(source.cloneNode(true));
  applyRevealStateToRoot(shell, page, stepIndex, showAll, options);
  return shell;
}}

function clearStageTransition(stage) {{
  if (!stage) return;
  const timers = stage._transitionTimers || [];
  timers.forEach((timer) => window.clearTimeout(timer));
  stage._transitionTimers = [];
  stage.classList.remove('is-transitioning','is-fade-out','is-fade-in');
}}

function clonePageInto(stageId, page, animate = false, options = {{}}) {{
  const stage = document.getElementById(stageId);
  const showAll = options.showAll ?? stageId !== 'playback-stage';
  const shell = buildStageShell(page, options.step ?? (showAll ? maxRevealStep(page) : 0), showAll, options);
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
	    applyRevealStateToRoot(shell, page, maxRevealStep(page), true);
	    target.replaceChildren(shell);
	    fitStage(target);
	  }});
	}}

function replaceBrokenMediaElement(element) {{
  if (!element || element.dataset.mediaBrokenHandled === 'true') return;
  if (!element.closest?.('.slide main,.peek-panel')) return;
  element.dataset.mediaBrokenHandled = 'true';
  const figure = document.createElement('figure');
  const isVideo = String(element.tagName || '').toLowerCase() === 'video';
  figure.className = (isVideo ? 'video-fallback' : 'missing-media') + ' media-broken';
  const icon = document.createElement('div');
  icon.className = 'broken-media-icon ' + (isVideo ? 'broken-video' : 'broken-image');
  icon.setAttribute('aria-hidden', 'true');
  const caption = document.createElement('figcaption');
  const code = document.createElement('code');
  code.textContent = element.getAttribute('src') || element.getAttribute('alt') || 'media unavailable';
  caption.appendChild(code);
  figure.append(icon, caption);
  if (element.parentElement?.tagName?.toLowerCase() === 'figure') {{
    element.parentElement.replaceWith(figure);
  }} else {{
    element.replaceWith(figure);
  }}
}}

document.addEventListener('error', (event) => {{
  const target = event.target;
  if (target instanceof HTMLImageElement || target instanceof HTMLVideoElement) replaceBrokenMediaElement(target);
}}, true);

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

function applyRevealState(stageId, page, stepIndex, options = {{}}) {{
  const stage = document.getElementById(stageId);
  if (!stage) return;
  const showAll = stageId === 'preview-stage';
  applyRevealStateToRoot(stage, page, showAll ? maxRevealStep(page) : stepIndex, showAll, options);
}}

function maskTargetAtPoint(clientX, clientY) {{
  const stage = document.getElementById('playback-stage');
  if (!stage) return null;
  const targets = [...stage.querySelectorAll('.reveal-kind-mask[data-reveal-order]:not(.is-revealed)')];
  return targets.find((target) => {{
    const rect = target.getBoundingClientRect();
    return clientX >= rect.left && clientX <= rect.right && clientY >= rect.top && clientY <= rect.bottom;
  }}) || null;
}}

function revealMaskAtPoint(event) {{
  if (viewMode !== 'playback') return false;
  const target = maskTargetAtPoint(event.clientX, event.clientY);
  if (!target) return false;
  const stage = document.getElementById('playback-stage');
  const page = pages[currentPageIndex];
  const index = [...stage.querySelectorAll('[data-reveal-order]')].indexOf(target);
  if (index < 0) return false;
  manualRevealKeys.add(revealTargetKey(page, target, index));
  applyRevealState('playback-stage', page, currentRevealStep);
  revealPlaybackToolbar();
  return true;
}}

let peekHoverTimer = null;
let peekLeaveTimer = null;
let activePeek = null;
let spaceHoldTimer = null;
let spaceHoldTrigger = null;
let spaceHoldOpened = false;
let playbackHoverTrigger = null;

function peekTriggerMode(trigger) {{
  return trigger?.dataset?.peekTrigger || 'both';
}}

function peekAllows(trigger, action) {{
  const mode = peekTriggerMode(trigger);
  return mode === 'both' || mode === action;
}}

function peekTriggerAtPoint(clientX, clientY) {{
  const stage = document.getElementById('playback-stage');
  if (!stage) return null;
  const triggers = [...stage.querySelectorAll('[data-peek-trigger]')];
  return triggers.find((trigger) => {{
    const rect = trigger.getBoundingClientRect();
    return clientX >= rect.left && clientX <= rect.right && clientY >= rect.top && clientY <= rect.bottom;
  }}) || null;
}}

function peekTriggerFromEvent(event) {{
  return event.target.closest?.('[data-peek-trigger]') || (viewMode === 'playback' ? peekTriggerAtPoint(event.clientX, event.clientY) : null);
}}

function ensurePeekPopover() {{
  let popover = document.getElementById('peek-popover');
  if (!popover) {{
    popover = document.createElement('div');
    popover.id = 'peek-popover';
    popover.className = 'peek-popover';
    popover.setAttribute('role', 'dialog');
    popover.setAttribute('aria-live', 'polite');
    document.body.appendChild(popover);
    popover.addEventListener('pointerenter', () => window.clearTimeout(peekLeaveTimer));
    popover.addEventListener('pointerleave', () => {{
      if (activePeek && !activePeek.pinned) closePeek();
    }});
  }}
  return popover;
}}

function positionPeek(trigger) {{
  const popover = document.getElementById('peek-popover');
  if (!popover || !trigger) return;
  const rect = trigger.getBoundingClientRect();
  const popRect = popover.getBoundingClientRect();
  const margin = 24;
  let left = rect.left + rect.width / 2 - popRect.width / 2;
  left = Math.max(margin, Math.min(left, window.innerWidth - popRect.width - margin));
  let top = rect.bottom + 14;
  if (top + popRect.height > window.innerHeight - margin) {{
    top = rect.top - popRect.height - 14;
  }}
  top = Math.max(margin, Math.min(top, window.innerHeight - popRect.height - margin));
  popover.style.left = left.toFixed(1) + 'px';
  popover.style.top = top.toFixed(1) + 'px';
}}

function openPeek(trigger, options = {{}}) {{
  if (!trigger) return;
  const template = trigger.querySelector(':scope > .peek-template');
  if (!template) return;
  const popover = ensurePeekPopover();
  const pinned = options.pinned === true;
  popover.replaceChildren(template.content.cloneNode(true));
  popover.classList.toggle('has-media', trigger.dataset.peekMedia === 'true');
  activePeek = {{trigger, pinned}};
  requestAnimationFrame(() => {{
    positionPeek(trigger);
    popover.classList.add('is-open');
    popover.querySelectorAll('video').forEach((video) => video.play?.().catch?.(() => {{}}));
  }});
}}

function closePeek() {{
  window.clearTimeout(peekHoverTimer);
  window.clearTimeout(peekLeaveTimer);
  const popover = document.getElementById('peek-popover');
  if (popover) {{
    popover.querySelectorAll('video').forEach((video) => {{
      video.pause?.();
      try {{ video.currentTime = 0; }} catch (error) {{}}
    }});
    popover.classList.remove('is-open','has-media');
  }}
  activePeek = null;
}}

function togglePinnedPeek(trigger) {{
  if (activePeek?.trigger === trigger && activePeek.pinned) {{
    closePeek();
    return;
  }}
  openPeek(trigger, {{pinned:true}});
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

function setPrintSectionDividers(include) {{
  document.documentElement.classList.toggle('skip-section-dividers', !include);
}}

function setSectionDividersVisible(visible, persist = true) {{
  showSectionDividers = visible;
  document.documentElement.classList.toggle('hide-section-dividers', !visible);
  const button = document.getElementById('section-divider-toggle');
  if (button) {{
    button.setAttribute('aria-pressed', visible ? 'true' : 'false');
    button.textContent = visible ? '隐藏章节页' : '显示章节页';
  }}
  if (persist) {{
    try {{ localStorage.setItem('school-presentation-section-dividers-visible', visible ? '1' : '0'); }} catch (error) {{}}
  }}
  if (!isPageVisibleInUi(pages[currentPageIndex])) {{
    const next = nearestVisiblePageIndex(currentPageIndex, 1);
    if (next >= 0) selectPage(next, {{animate:false}});
  }} else {{
    setActiveState(pages[currentPageIndex]);
    fitVisibleStages();
  }}
}}

function toggleSectionDividers() {{
  setSectionDividersVisible(!showSectionDividers);
}}

function initSectionDividerControls() {{
  let visible = true;
  try {{
    const stored = localStorage.getItem('school-presentation-section-dividers-visible');
    if (stored === '0') visible = false;
  }} catch (error) {{}}
  setSectionDividersVisible(visible, false);
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
  if (progress) {{
    const visibleIndexes = visiblePageIndexes();
    const visiblePosition = Math.max(0, visibleIndexes.indexOf(currentPageIndex));
    const visibleTotal = Math.max(1, visibleIndexes.length);
    const local = maxRevealStep(page) ? currentRevealStep / Math.max(1, maxRevealStep(page)) : 1;
    progress.style.width = (((visiblePosition + local) / visibleTotal) * 100).toFixed(2) + '%';
  }}
  const activeRail = document.querySelector('[data-thumb-page-id=\"' + page.page_id + '\"]');
  activeRail?.scrollIntoView({{block:'nearest', inline:'nearest'}});
}}

function syncHash(page) {{
  const nextHash = '#p=' + encodeURIComponent(page.page_id) + '&s=' + encodeURIComponent(String(currentRevealStep));
  if (window.location.hash !== nextHash) history.replaceState(null, '', nextHash);
}}

function selectPage(target, options = {{}}) {{
  let idx = typeof target === 'number' ? target : pages.findIndex((page) => page.page_id === target || String(page.global_index) === String(target));
  if (idx < 0 || idx >= pages.length) return;
  if (options.allowHidden !== true && !isPageVisibleInUi(pages[idx])) {{
    idx = nearestVisiblePageIndex(idx, options.direction ?? 1);
    if (idx < 0 || idx >= pages.length) return;
  }}
  const previousPageIndex = currentPageIndex;
  const previousRevealStep = currentRevealStep;
  const animate = options.animate !== false && idx !== currentPageIndex;
  const samePage = idx === previousPageIndex;
  if (idx !== previousPageIndex) closePeek();
  if (idx !== previousPageIndex || options.resetManualReveal === true) resetManualRevealState();
  currentPageIndex = idx;
  const page = pages[currentPageIndex];
  const requestedStep = options.step ?? (previousPageIndex === idx ? currentRevealStep : 0);
  currentRevealStep = Math.max(0, Math.min(maxRevealStep(page), Number(requestedStep) || 0));
  const animateRevealStep = options.animateStep === true && idx === previousPageIndex && currentRevealStep > previousRevealStep;
  const revealAnimationOptions = animateRevealStep ? {{animateNew:true, previousStep:previousRevealStep}} : {{}};
  const hasPreviewShell = !!document.querySelector('#preview-stage .slide-scale-shell');
  const hasPlaybackShell = !!document.querySelector('#playback-stage .slide-scale-shell');
  const canReuseShells = samePage && !animate && hasPreviewShell && hasPlaybackShell;
  if (!canReuseShells) {{
    clonePageInto('preview-stage', page, animate, {{step:maxRevealStep(page), showAll:true}});
    clonePageInto('playback-stage', page, animate, {{step:currentRevealStep, showAll:false, ...revealAnimationOptions}});
  }}
  if (!animate || canReuseShells) {{
    applyRevealState('preview-stage', page, maxRevealStep(page));
    applyRevealState('playback-stage', page, currentRevealStep, revealAnimationOptions);
  }}
  setActiveState(page);
  if (options.hash !== false) syncHash(page);
}}

function goToPage(deltaOrIndex, options = {{}}) {{
  const direction = deltaOrIndex >= 0 ? 1 : -1;
  const next = adjacentVisiblePageIndex(currentPageIndex, direction);
  if (next >= 0) selectPage(next, {{...options, direction}});
}}

function nextAction() {{
  if (viewMode !== 'playback') {{
    goToPage(1);
    return;
  }}
	  const page = pages[currentPageIndex];
	  const maxStep = maxRevealStep(page);
	  if (currentRevealStep < maxStep) {{
	    const nextStep = nextPendingRevealStep(page);
	    if (nextStep <= maxStep) {{
	      selectPage(currentPageIndex, {{step: nextStep, animate:false, animateStep:true}});
	      return;
	    }}
	    currentRevealStep = maxStep;
	  }}
  if (currentPageIndex >= pages.length - 1) {{
    showWorkspace();
    return;
  }}
  const next = adjacentVisiblePageIndex(currentPageIndex, 1);
  if (next >= 0) {{
    selectPage(next, {{step:0, direction:1}});
    return;
  }}
  showWorkspace();
}}

function previousAction() {{
  if (viewMode !== 'playback') {{
    goToPage(-1);
    return;
  }}
  if (currentRevealStep > 0) {{
    selectPage(currentPageIndex, {{step: currentRevealStep - 1, animate:false}});
    return;
  }}
  const previous = adjacentVisiblePageIndex(currentPageIndex, -1);
  if (previous >= 0) {{
    selectPage(previous, {{step:0, direction:-1}});
  }}
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
  resetManualRevealState();
  setView('playback');
  selectPage(currentPageIndex, {{animate:false, resetManualReveal:true}});
  revealPlaybackToolbar();
  fitVisibleStages();
}}

function showOverview() {{
  setView('overview');
  selectPage(currentPageIndex, {{animate:false}});
  requestAnimationFrame(() => fitVisibleStages());
}}

function selectFromHash() {{
  const raw = window.location.hash.replace(/^#/, '');
  if (!raw) return false;
  const params = new URLSearchParams(raw);
  const pageId = decodeURIComponent(params.get('p') || raw.replace(/^p=/, '').split('&')[0]);
  const step = Number(params.get('s') || 0);
  const idx = pages.findIndex((page) => page.page_id === pageId || String(page.global_index) === pageId);
  if (idx >= 0) {{
    selectPage(idx, {{hash:false, animate:false, step:Number.isFinite(step) ? step : 0}});
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

document.addEventListener('pointerover', (event) => {{
  const trigger = event.target.closest?.('[data-peek-trigger]');
  if (!trigger || !peekAllows(trigger, 'hover')) return;
  if (trigger.contains(event.relatedTarget)) return;
  window.clearTimeout(peekLeaveTimer);
  window.clearTimeout(peekHoverTimer);
  peekHoverTimer = window.setTimeout(() => openPeek(trigger, {{pinned:false}}), 320);
}});

document.addEventListener('pointermove', (event) => {{
  if (viewMode !== 'playback') return;
  const trigger = peekTriggerAtPoint(event.clientX, event.clientY);
  if (trigger === playbackHoverTrigger) return;
  window.clearTimeout(peekHoverTimer);
  if (activePeek?.trigger === playbackHoverTrigger && !activePeek.pinned) closePeek();
  playbackHoverTrigger = trigger;
  if (trigger && peekAllows(trigger, 'hover')) {{
    window.clearTimeout(peekLeaveTimer);
    peekHoverTimer = window.setTimeout(() => openPeek(trigger, {{pinned:false}}), 320);
  }}
}});

document.addEventListener('pointerout', (event) => {{
  const trigger = event.target.closest?.('[data-peek-trigger]');
  if (!trigger || !peekAllows(trigger, 'hover')) return;
  if (trigger.contains(event.relatedTarget)) return;
  window.clearTimeout(peekHoverTimer);
  if (activePeek?.trigger === trigger && !activePeek.pinned) {{
    peekLeaveTimer = window.setTimeout(() => closePeek(), 120);
  }}
}});

document.addEventListener('click', (event) => {{
  const trigger = peekTriggerFromEvent(event);
  if (trigger && peekAllows(trigger, 'click')) {{
    event.preventDefault();
    event.stopPropagation();
    togglePinnedPeek(trigger);
    return;
  }}
  const popover = document.getElementById('peek-popover');
  if (activePeek?.pinned && popover && !popover.contains(event.target)) {{
    closePeek();
  }}
}}, true);

document.addEventListener('click', (event) => {{
  if (revealMaskAtPoint(event)) {{
    event.preventDefault();
    event.stopPropagation();
    return;
  }}
}}, true);

	document.addEventListener('click', (event) => {{
	  const agenda = event.target.closest('[data-agenda-section-index]');
	  if (agenda) {{
	    event.preventDefault();
	    event.stopPropagation();
	    navigateAgendaSection(agenda.dataset.agendaSectionIndex);
	    return;
	  }}
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
	  const peekTrigger = event.target.closest?.('[data-peek-trigger]');
	  if (!peekTrigger) return;
	  if (event.key === 'Enter' && peekAllows(peekTrigger, 'click')) {{
	    event.preventDefault();
	    event.stopPropagation();
	    togglePinnedPeek(peekTrigger);
	    return;
	  }}
	  if (event.key !== ' ') return;
	  event.preventDefault();
	  event.stopPropagation();
	  if (event.repeat || spaceHoldTimer) return;
	  spaceHoldTrigger = peekTrigger;
	  spaceHoldOpened = false;
	  spaceHoldTimer = window.setTimeout(() => {{
	    spaceHoldOpened = true;
	    openPeek(spaceHoldTrigger, {{pinned:false}});
	  }}, 300);
	}}, true);

	document.addEventListener('keyup', (event) => {{
	  if (event.key !== ' ' || !spaceHoldTrigger) return;
	  event.preventDefault();
	  event.stopPropagation();
	  window.clearTimeout(spaceHoldTimer);
	  if (spaceHoldOpened) {{
	    closePeek();
	  }} else {{
	    togglePinnedPeek(spaceHoldTrigger);
	  }}
	  spaceHoldTimer = null;
	  spaceHoldTrigger = null;
	  spaceHoldOpened = false;
	}}, true);

	document.addEventListener('keydown', (event) => {{
	  const agenda = event.target.closest?.('[data-agenda-section-index]');
	  if (!agenda || (event.key !== 'Enter' && event.key !== ' ')) return;
	  event.preventDefault();
	  navigateAgendaSection(agenda.dataset.agendaSectionIndex);
	}});

	document.addEventListener('keydown', (event) => {{
	  if (event.target.closest?.('[data-peek-trigger]')) return;
	  if (event.target.closest?.('[data-agenda-section-index]')) return;
	  if (event.key === 'Escape' && viewMode === 'playback') {{ event.preventDefault(); showWorkspace(); return; }}
	  if (event.key === 'ArrowRight' || event.key === 'PageDown' || event.key === ' ') {{ event.preventDefault(); nextAction(); }}
	  if (event.key === 'ArrowLeft' || event.key === 'PageUp') {{ event.preventDefault(); previousAction(); }}
	}});

document.querySelector('.playback-zone.prev')?.addEventListener('click', previousAction);
document.querySelector('.playback-zone.center')?.addEventListener('click', nextAction);
document.querySelector('.playback-zone.next')?.addEventListener('click', nextAction);
document.getElementById('playback')?.addEventListener('mousemove', revealPlaybackToolbar);
document.getElementById('playback')?.addEventListener('touchstart', revealPlaybackToolbar, {{passive:true}});
let touchStartX = null;
document.getElementById('playback')?.addEventListener('touchstart', (event) => {{ touchStartX = event.changedTouches[0]?.clientX ?? null; }}, {{passive:true}});
document.getElementById('playback')?.addEventListener('touchend', (event) => {{
  if (touchStartX === null) return;
  const dx = (event.changedTouches[0]?.clientX ?? touchStartX) - touchStartX;
  if (Math.abs(dx) > 42) (dx < 0 ? nextAction : previousAction)();
  touchStartX = null;
}}, {{passive:true}});
window.addEventListener('hashchange', selectFromHash);

renderThumbnailClones();
initRailControls();
initSectionDividerControls();
window.addEventListener('resize', () => {{
  if (!isMobileRailMode()) closeRailDrawer();
  fitVisibleStages();
  if (activePeek) positionPeek(activePeek.trigger);
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
        "<div id=\"playback-stage\" class=\"playback-stage\"></div><div class=\"playback-toolbar\" aria-label=\"playback controls\"><button class=\"playback-control\" type=\"button\" onclick=\"previousAction()\" aria-label=\"上一步\"><span aria-hidden=\"true\">‹</span></button><span class=\"playback-page-pill\" data-current-page-label></span><button class=\"playback-control\" type=\"button\" onclick=\"nextAction()\" aria-label=\"下一步\"><span aria-hidden=\"true\">›</span></button><button class=\"playback-exit\" type=\"button\" onclick=\"showWorkspace()\" aria-label=\"退出播放\">Esc</button></div>"
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
    reveal_verified = False
    try:
        sections = m1.get("sections", [])
        pages = m1.get("pages", [])
        reveal_pages = [
            page for page in pages
            if isinstance(page, dict) and isinstance(page.get("reveal_steps"), list) and page.get("reveal_steps")
        ]
        reveal_kinds = {
            kind
            for page in reveal_pages
            for step in page.get("reveal_steps", [])
            if isinstance(step, dict)
            for kind in step.get("kinds", [])
        }
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
                and isinstance(page.get("reveal_steps"), list)
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
        reveal_verified = (
            len(reveal_pages) >= 4
            and {"mask", "emphasis", "reveal"}.issubset(reveal_kinds)
            and not {"animate", "sort-rank", "sort-final"}.intersection(reveal_kinds)
            and any(
                [step.get("target_count") for step in page.get("reveal_steps", []) if isinstance(step, dict)].count(2) >= 1
                for page in reveal_pages
            )
            and any(
                {"2.1", "2.55"}.issubset({
                    str(step.get("priority"))
                    for step in page.get("reveal_steps", [])
                    if isinstance(step, dict)
                })
                for page in reveal_pages
            )
        )
    except Exception:
        hierarchy_verified = False
        reveal_verified = False

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
        "data-reveal-order",
        "data-reveal-kind",
        "reveal-kind-mask",
        "reveal-kind-emphasis",
        "reveal-kind-reveal",
        "nextAction",
        "previousAction",
        "URLSearchParams",
    ]
    workspace_verified = all(token in first_html for token in required_html_tokens)
    thumbnail_ratio_verified = (
        ".thumb-item{position:relative;display:block;width:100%" in first_html
        and "aspect-ratio:var(--slide-aspect)" in first_html
        and ".thumb-real .slide-scale-shell,.overview-tile .slide-scale-shell" in first_html
        and "grid-template-columns:56px minmax(0,1fr)" not in first_html
        and "grid-template-columns:48px 1fr" not in first_html
    )

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
        and reveal_verified
        and workspace_verified
        and thumbnail_ratio_verified
        and flat_slide_compat_verified
    )
    verification = {
        "status": "passed" if passed else "failed",
        "repeatable_html": stable,
        "hierarchy_verified": hierarchy_verified,
        "reveal_verified": reveal_verified,
        "workspace_verified": workspace_verified,
        "thumbnail_ratio_verified": thumbnail_ratio_verified,
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
