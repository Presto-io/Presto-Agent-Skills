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
    if raw_path.is_absolute() or ".." in raw_path.parts:
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


def parse_slides(body: str) -> list[dict[str, object]]:
    matches = list(re.finditer(r"^## Slide:\s*(.+?)\s*$", body, flags=re.M))
    slides: list[dict[str, object]] = []
    for idx, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
        raw = body[start:end].strip()
        meta, raw = parse_slide_meta(raw)
        notes, raw = extract_admonitions(raw, "notes")
        warnings, raw = extract_admonitions(raw, "warning")
        slides.append({
            "title": title,
            "meta": meta,
            "notes": notes,
            "warnings": warnings,
            "body": raw.strip(),
        })
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
        return max(6, len(text.splitlines()) * 2)
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
        if len(rows) <= 7:
            return [block]
        header = rows[:2] if len(rows) >= 2 and all(set(cell.strip()) <= {"-", ":"} for cell in rows[1].strip().strip("|").split("|")) else rows[:1]
        body = rows[len(header):]
        chunks = []
        for idx in range(0, len(body), 5):
            chunks.append({"type": "table", "text": "\n".join(header + body[idx : idx + 5])})
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
    expr = re.sub(r"\\sqrt\{([^{}]+)\}", r"√\1", expr)
    expr = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", expr)
    replacements = {
        r"\times": "×",
        r"\cdot": "·",
        r"\varphi": "φ",
        r"\phi": "φ",
        r"\cos": "cos",
        r"\sin": "sin",
        r"\tan": "tan",
        r"\sqrt": "√",
        r"\leq": "≤",
        r"\geq": "≥",
        r"\neq": "≠",
        r"\approx": "≈",
        r"\pm": "±",
        r"\alpha": "α",
        r"\beta": "β",
        r"\gamma": "γ",
        r"\Delta": "Δ",
        r"\Omega": "Ω",
    }
    for raw, rendered in replacements.items():
        expr = expr.replace(raw, rendered)
    expr = re.sub(r"\b(cos|sin|tan)(?=[A-Za-zα-ωΑ-Ω])", r"\1 ", expr)
    expr = re.sub(r"\s+", " ", expr).strip()
    escaped = html.escape(expr)
    escaped = re.sub(r"\^\\?\{([^{}]+)\}", r"<sup>\1</sup>", escaped)
    escaped = re.sub(r"_\\?\{([^{}]+)\}", r"<sub>\1</sub>", escaped)
    escaped = re.sub(r"\^([A-Za-z0-9+\-]+)", r"<sup>\1</sup>", escaped)
    escaped = re.sub(r"_([A-Za-z0-9+\-]+)", r"<sub>\1</sub>", escaped)
    return escaped


def render_formula(text: str) -> str:
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
    lines = "".join(f"<div class=\"formula-line\">{latex_to_html(formula)}</div>" for formula in formulas)
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


def render_block(block: dict[str, str], input_dir: Path, media_warnings: list[str]) -> str:
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
    if kind == "math":
        return render_formula(text)
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


def render_deck(input_path: Path, max_size_mb: int) -> tuple[str, dict[str, object]]:
    text = read_text(input_path)
    meta, body = parse_frontmatter(text)
    slides = parse_slides(body)
    if not slides:
        fail("no logical slides found; use headings like '## Slide: Title'")
    page_ratio_label, page_ratio_width, page_ratio_height, page_ratio_value = parse_page_ratio(meta.get("page_ratio"))
    logo_uri = data_uri(IMAGE_DIR / "logo-combined.png")
    cover_logo_uri = data_uri(IMAGE_DIR / "logo-white.png")
    slogan_uri = data_uri(IMAGE_DIR / "slogan-en.png")
    closing_bg_uri = data_uri(IMAGE_DIR / "gradient-cover.png")
    closing_slogan_uri = data_uri(IMAGE_DIR / "slogan-white-script.png")
    closing_ribbon_uri = data_uri(IMAGE_DIR / "decorative-footer-band.png")
    footer_uri = data_uri(IMAGE_DIR / "body-page-footer.png")
    footer_logo_uri = data_uri(IMAGE_DIR / "logo-white.png")
    wave_top_uri = data_uri(IMAGE_DIR / "decorative-wave-top.png")
    title = meta.get("title") or "School Presentation"
    input_dir = input_path.parent.resolve()
    media_warnings: list[str] = []
    sections: list[str] = []
    physical_count = 0
    layouts_used: list[str] = []
    for idx, slide in enumerate(slides):
        body_text = str(slide["body"])
        blocks = split_blocks(body_text)
        layout = choose_layout(slide, blocks, idx)
        layouts_used.append(layout)
        split_mode = "auto"
        if isinstance(slide["meta"], dict):
            split_mode = slide["meta"].get("split", "auto")
        chunks = chunk_blocks(blocks, split_mode)
        for page_idx, chunk in enumerate(chunks, start=1):
            physical_count += 1
            page_title = html.escape(str(slide["title"]))
            classes = f"slide layout-{html.escape(layout)}"
            rendered_blocks = "".join(render_block(block, input_dir, media_warnings) for block in chunk)
            warnings = "".join(f"<aside class=\"warning\">{inline_markdown(w)}</aside>" for w in slide["warnings"])
            notes = "".join(f"<details class=\"notes\"><summary>Speaker notes</summary><p>{inline_markdown(n)}</p></details>" for n in slide["notes"])
            page_marker = f"<span>{idx + 1}.{page_idx}</span>" if len(chunks) > 1 else f"<span>{idx + 1}</span>"
            if layout == "closing":
                sections.append(
                    f"<section class=\"{classes}\" data-logical=\"{idx + 1}\" data-physical=\"{page_idx}\">"
                    f"<div class=\"closing-stage\">"
                    f"<div class=\"closing-band\"><img class=\"closing-slogan\" src=\"{closing_slogan_uri}\" alt=\"school slogan\"></div>"
                    f"<img class=\"closing-ribbon\" src=\"{closing_ribbon_uri}\" alt=\"\">"
                    f"<img class=\"closing-logo\" src=\"{logo_uri}\" alt=\"school logo\">"
                    f"</div>"
                    f"</section>"
                )
                continue
            brand_logo = f"<img class=\"brand-logo\" src=\"{cover_logo_uri}\" alt=\"school logo\">" if layout == "cover" else ""
            sections.append(
                f"<section class=\"{classes}\" data-logical=\"{idx + 1}\" data-physical=\"{page_idx}\">"
                f"{brand_logo}"
                f"<div class=\"slide-title\"><h2>{page_title}</h2>{page_marker}</div>"
                f"<main>{warnings}{rendered_blocks}{notes}</main>"
                f"<footer class=\"slide-footer\" aria-hidden=\"true\">"
                f"<img class=\"footer-band\" src=\"{footer_uri}\" alt=\"\">"
                f"<img class=\"footer-logo\" src=\"{footer_logo_uri}\" alt=\"\">"
                f"</footer>"
                f"</section>"
            )
    css = """
:root{__RATIO_CSS__;--slide-max-width:1280px;--green:#579E40;--teal:#549183;--blue:#0084CC;--deep:#0E2841;--paper:#fff;--soft:#E8E8E8;--gold:#F2BA02}
*{box-sizing:border-box}body{margin:0;background:#eef3f5;color:var(--deep);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans SC",Arial,sans-serif;letter-spacing:0}
.deck{width:100%;display:grid;justify-items:center;gap:28px;padding:28px 0}.slide{position:relative;width:min(calc(100vw - 32px),calc((100vh - 56px) * var(--slide-ratio)),var(--slide-max-width));aspect-ratio:var(--slide-aspect);height:auto;padding:4.3% 6% 8.2%;display:grid;grid-template-rows:auto auto 1fr;overflow:hidden;isolation:isolate;background:linear-gradient(115deg,#ffffff 0%,#ffffff 58%,#edf7fb 100%)}
.slide::before{content:"";position:absolute;left:0;top:0;width:16px;height:100%;background:linear-gradient(180deg,var(--green),var(--blue));z-index:0}.slide::after{content:"";position:absolute;right:4%;top:2.8%;width:48%;height:8%;background:url("__WAVE_TOP__") right top/contain no-repeat;opacity:.22;z-index:0;pointer-events:none}.slide>*{position:relative;z-index:1}
.brand-logo{width:min(18%,180px);height:auto;object-fit:contain;align-self:flex-start;box-shadow:none;border-radius:0;background:transparent}.slide-title{position:relative;display:flex;align-items:end;justify-content:space-between;gap:24px;margin:1.5% 0 2%;border-bottom:3px solid var(--blue);padding-bottom:10px}
.slide-title::before{content:"";position:absolute;right:74px;bottom:-6px;width:118px;height:3px;background:linear-gradient(90deg,var(--green),var(--blue))}.slide-title::after{content:"";position:absolute;right:0;top:-9px;width:72px;height:10px;background:linear-gradient(90deg,var(--green) 0 24px,transparent 24px 31px,var(--blue) 31px 55px,transparent 55px 62px,var(--gold) 62px 72px);opacity:.9}
.slide-title h2{font-size:clamp(28px,5vh,48px);line-height:1.08;margin:0;color:#0056A8;font-weight:800}.slide-title span{font-size:16px;color:#fff;background:var(--green);padding:5px 10px;border-radius:4px;min-width:42px;text-align:center}
main{min-height:0;overflow:hidden;font-size:clamp(17px,2.45vh,24px);line-height:1.46;max-width:1040px}.layout-cover{color:#fff;background:linear-gradient(115deg,rgba(87,158,64,.95),rgba(0,132,204,.95)),#0084CC}.layout-cover::after{right:6%;top:16%;width:64%;height:11%;opacity:.28;filter:brightness(0) invert(1)}.layout-cover .slide-title{border-color:#fff}.layout-cover .slide-title::before{background:#fff}.layout-cover .slide-title::after{background:linear-gradient(90deg,#fff 0 24px,transparent 24px 31px,rgba(255,255,255,.72) 31px 55px,transparent 55px 62px,var(--gold) 62px 72px)}.layout-cover .slide-title h2,.layout-cover main{color:#fff}.layout-cover .brand-logo{width:min(34%,340px);max-width:340px}.layout-cover figure{margin:.8em 0 0}.layout-cover figure img{max-width:52%;max-height:30%;box-shadow:none;border-radius:4px}.layout-cover figcaption{display:none}.layout-closing{padding:0;background:#fff}.layout-closing::before,.layout-closing::after,.layout-closing .slide-title,.layout-closing main,.layout-closing .slide-footer,.layout-closing .brand-logo{display:none}.layout-closing .closing-stage{position:absolute;inset:0;overflow:hidden;background:#fff}.layout-closing .closing-band{position:absolute;left:0;right:0;top:30%;height:31%;background:url("__CLOSING_BG__") center/cover no-repeat}.layout-closing .closing-slogan{position:absolute;left:53%;top:44%;width:min(27%,340px);transform:translate(-50%,-50%);height:auto;box-shadow:none;border-radius:0;background:transparent}.layout-closing .closing-ribbon{position:absolute;left:0;right:0;top:57%;width:100%;height:19%;object-fit:fill;box-shadow:none;border-radius:0;background:transparent}.layout-closing .closing-logo{position:absolute;left:50%;bottom:9%;width:min(30%,380px);transform:translateX(-50%);height:auto;box-shadow:none;border-radius:0;background:transparent}
p{margin:0 0 1em}ul{margin:.2em 0 1em;padding-left:1.2em}li{margin:.28em 0}h3{position:relative;margin:.55em 0 .45em;padding-left:18px;color:#0056A8}h3::before{content:"";position:absolute;left:0;top:.28em;width:8px;height:1.05em;background:linear-gradient(180deg,var(--green),var(--blue));border-radius:2px}strong{color:#0056A8}code{font-size:.78em;background:#eef7fb;padding:2px 5px;border-radius:4px}
.table-wrap{position:relative;overflow:auto;border:1px solid #d8e6ec;border-radius:6px;background:#fff;box-shadow:0 12px 28px rgba(14,40,65,.08)}.table-wrap::before,.chart::before,.formula::before{content:"";position:absolute;right:0;top:0;width:74px;height:5px;background:linear-gradient(90deg,var(--green),var(--blue));z-index:2}table{width:100%;border-collapse:collapse;font-size:.72em}th{background:#0084CC;color:#fff}th,td{padding:12px 14px;border-bottom:1px solid #dfe9ee;text-align:left;vertical-align:top}tr:nth-child(even) td{background:#f7fbfc}
figure{margin:1em 0;max-width:100%}img,video{max-width:100%;max-height:48vh;object-fit:contain;border-radius:6px;background:#fff;box-shadow:0 14px 32px rgba(14,40,65,.13)}figcaption,.caption{font-size:.66em;color:#4b6470;margin-top:8px}
.chart{position:relative;display:grid;gap:12px;background:#fff;border:1px solid #d8e6ec;border-radius:6px;padding:22px;box-shadow:0 12px 28px rgba(14,40,65,.08)}.chart-row{display:grid;grid-template-columns:180px 1fr 64px;gap:14px;align-items:center;font-size:.76em}.bar{height:22px;background:#e3eff3;border-radius:999px;overflow:hidden}.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--green),var(--blue))}
.formula{position:relative;display:grid;gap:10px;margin:10px 0 22px;padding:16px 24px;border-left:6px solid var(--green);background:#f7fbfc;border-radius:4px;font-family:Georgia,"Times New Roman",serif;font-size:1.1em;color:#0056A8}.formula-line{white-space:normal;line-height:1.35}
.warning{margin:0 0 1em;padding:12px 16px;border-left:5px solid var(--gold);background:#fff8df;color:#675100;border-radius:4px;font-size:.8em}.notes{display:none}.video-fallback,.missing-media{display:grid;place-items:center;min-height:180px;border:2px dashed #8ab5c8;border-radius:6px;background:#f5fbfd;text-align:center}.video-fallback div,.missing-media div{font-size:42px;font-weight:800;color:#0084CC}
.slide-footer{position:absolute;left:0;right:0;bottom:0;width:100%;z-index:2;pointer-events:none}.slide-footer::before{content:"";position:absolute;left:16px;right:0;top:-2px;height:2px;background:linear-gradient(90deg,rgba(87,158,64,.85),rgba(0,132,204,.45),transparent)}.footer-band{display:block;width:100%;height:auto;max-height:none;object-fit:fill;box-shadow:none;border-radius:0;background:transparent}.footer-logo{position:absolute;left:3.4%;bottom:12%;width:13.5%;min-width:118px;max-width:178px;height:auto;box-shadow:none;border-radius:0;background:transparent}
.deck-cover{position:fixed;right:20px;top:16px;z-index:5;display:flex;gap:10px;align-items:center;font-size:12px;color:#466}.deck-cover img{width:94px;height:auto;box-shadow:none;border-radius:0;background:transparent}
@media print{.deck{padding:0;gap:0}.slide{page-break-after:always;width:100vw;max-width:none}.deck-cover{display:none}}@media(max-width:760px){.deck{gap:16px;padding:16px 0}.slide{width:calc(100vw - 20px);padding:4.5% 6% 8.5%}.brand-logo{width:34%;max-width:160px}.slide-title{align-items:start}.slide-title h2{font-size:26px}main{font-size:16px}.chart-row{grid-template-columns:1fr}.footer-logo{min-width:86px}}
"""
    css = css.replace("__RATIO_CSS__", f"--slide-aspect:{page_ratio_width} / {page_ratio_height};--slide-ratio:{page_ratio_value:.8f}")
    css = css.replace("__CLOSING_BG__", closing_bg_uri)
    css = css.replace("__WAVE_TOP__", wave_top_uri)
    html_doc = (
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{html.escape(title)}</title><style>{css}</style></head><body>"
        f"<div class=\"deck-cover\"><img src=\"{slogan_uri}\" alt=\"slogan\"><span>{len(slides)} logical / {physical_count} physical pages</span></div>"
        "<div class=\"deck\">" + "".join(sections) + "</div></body></html>"
    )
    sha = hashlib.sha256(html_doc.encode("utf-8")).hexdigest()
    manifest: dict[str, object] = {
        "input": str(input_path),
        "logical_slides": len(slides),
        "physical_pages": physical_count,
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
    first = workdir / "school-presentation-first.html"
    second = workdir / "school-presentation-second.html"
    first_manifest = workdir / "school-presentation-first.manifest.json"
    second_manifest = workdir / "school-presentation-second.manifest.json"
    m1 = cmd_render(argparse.Namespace(input=str(sample), html=str(first), manifest=str(first_manifest), max_size_mb=args.max_size_mb))
    m2 = cmd_render(argparse.Namespace(input=str(sample), html=str(second), manifest=str(second_manifest), max_size_mb=args.max_size_mb))
    stable = first.read_bytes() == second.read_bytes()
    verification = {
        "status": "passed" if stable and m1.get("under_size_cap") and m2.get("under_size_cap") else "failed",
        "repeatable_html": stable,
        "first_sha256": m1.get("html_sha256"),
        "second_sha256": m2.get("html_sha256"),
        "logical_slides": m1.get("logical_slides"),
        "physical_pages": m1.get("physical_pages"),
        "media_warnings": sorted(set(m1.get("media_warnings", []) + m2.get("media_warnings", []))),
        "artifacts": [str(sample), str(first), str(second), str(first_manifest), str(second_manifest)],
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
