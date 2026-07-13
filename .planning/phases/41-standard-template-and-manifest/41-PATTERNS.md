# Phase 41: Standard Template and Manifest - Pattern Map

**Mapped:** 2026-07-13
**Files analyzed:** 7 source targets + 2 generated evidence outputs
**Analogs found:** 7 / 7 source targets

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `skills/school-pptx/templates/standard-school.pptx` | template asset | file-I/O | `skills/school-presentation/references/identity/images/*` + `asset-manifest.json` | role-match |
| `skills/school-pptx/templates/standard-school.manifest.yaml` | config/manifest | transform | `skills/school-presentation/references/identity/asset-manifest.json` | partial |
| `skills/school-pptx/scripts/school-pptx.sh` | script wrapper | request-response | `skills/school-presentation/scripts/school-presentation.sh` | exact |
| `skills/school-pptx/scripts/template_report.py` | utility/validator | file-I/O + transform | `skills/school-presentation/scripts/school_presentation/_engine.py` | role-match |
| `skills/school-pptx/references/template-contract.md` | reference doc | transform | `skills/school-presentation/references/authoring-and-layout.md` | role-match |
| `skills/school-pptx/references/template-editing.md` | reference doc | request-response | `skills/tiaokedan/references/pdf-workflow.md` + `school-presentation/references/verification-contract.md` | role-match |
| `skills/school-pptx/SKILL.md` | skill entry | request-response | `skills/tiaokedan/SKILL.md` | exact |
| `build/school-pptx/.school-pptx/template-report.md` or caller `--out-md` | generated evidence | file-I/O | `school-presentation` `verify --workdir` artifacts | generated |
| `build/school-pptx/.school-pptx/template-report.json` or caller `--out-json` | generated evidence | file-I/O | `verification-manifest.json` pattern | generated |

## Pattern Assignments

### `skills/school-pptx/templates/standard-school.pptx` (template asset, file-I/O)

**Analog:** `skills/school-presentation/references/identity/README.md` and `asset-manifest.json`

**Skill-local runtime asset pattern** (`identity/README.md` lines 43-47):

```markdown
## Provenance Rules

- 不把源 PPTX/POTX 作为技能运行时依赖；技能只依赖本目录中已提取的资源。
- 如需替换学校视觉，新增资源必须写入本目录并更新 `asset-manifest.json` 与本文件。
- 不得把用户没有提供的校名、校徽、题词或口号虚构为官方素材。
```

**Asset provenance structure** (`asset-manifest.json` lines 1-19):

```json
{
  "sources": [
    {
      "path": "/Users/mrered/Desktop/双校名ppt模板（通用）.pptx",
      "type": "pptx"
    },
    {
      "path": "/Users/mrered/Desktop/学院PPT模板.potx",
      "type": "potx"
    }
  ],
  "assets": [
    {
      "file": "images/logo-combined.png",
      "role": "school logo and bilingual school name",
      "source": "双校名ppt模板（通用）.pptx:ppt/media/image6.png",
      "width": 1589,
      "height": 485,
      "sha256": "6250b9a4c1f3beabef5c39664bad0397a091c34c54bc0417d204f8045ed57069"
    }
  ]
}
```

**Current Phase 41 source evidence:** `test/学院PPT模板.potx` exists in the repo workspace and should be treated as the supplied visual source evidence for normalization.

**Apply to Phase 41:** read `test/学院PPT模板.potx` during execution, normalize it into the committed runtime `skills/school-pptx/templates/standard-school.pptx`, and do not copy the original `.potx` into `skills/school-pptx/templates/` as a runtime dependency. Record derivation/provenance in the YAML manifest or `template-contract.md`.

---

### `skills/school-pptx/templates/standard-school.manifest.yaml` (config/manifest, transform)

**Analog:** no exact YAML manifest exists. Use `asset-manifest.json` for provenance shape and `_engine.py` generated manifest for structural keys.

**Theme/palette provenance pattern** (`palette.json` lines 1-13):

```json
{
  "source": "ppt/theme/theme1.xml from /Users/mrered/Desktop/学院PPT模板.potx",
  "colors": {
    "school-green": "#579E40",
    "soft-green": "#5E9768",
    "teal": "#549183",
    "blue-teal": "#498B9E",
    "school-blue": "#3E85B9",
    "bright-blue": "#0084CC",
    "ink": "#0E2841",
    "paper": "#FFFFFF",
    "soft-paper": "#E8E8E8"
  }
}
```

**Generated manifest key pattern** (`_engine.py` lines 4215-4226):

```python
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
```

**Directory/schema ownership pattern** (`docs/directory-spec.md` lines 28-30):

```markdown
`skills/` 下的 `SKILL.md` 是 semantic source of truth。它应该保留触发意图、目标、输入、核心流程、脚本调用入口、输出概览、验证入口、安全边界和 `Runtime Adapter Notes`。

`references/` 是 skill-local progressive disclosure 区域，不是新的 canonical skill body。引用文件可以很详细，但必须服务 owning skill 的 workflow；不要把某个模板的 metadata fields、renderer rules 或 fixture 细节提升为全仓库通用 schema。`scripts/` 只放可调用辅助命令或内部模块；大型脚本可以拆成 CLI dispatch、parsing、rendering、artifact writing、verification/reporting 等 skill-local modules，但外层公共命令、常用 flags、输出文件名、manifest keys 和行为契约必须保持稳定。
```

**Apply to Phase 41:** YAML should be skill-local and full-fidelity. Required top-level keys should include `theme_id`, `available_themes`, `template`, `layouts`, and `ownership`. Each layout should carry stable ids for the 11 layouts, slots keyed by semantic id, placeholder/anchor metadata, geometry, `text_budget`, `empty_slot`, and `continuation`.

---

### `skills/school-pptx/scripts/school-pptx.sh` (script wrapper, request-response)

**Analog:** `skills/school-presentation/scripts/school-presentation.sh`

**Shell wrapper pattern** (lines 1-6):

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
```

**Usage and subcommand pattern** (lines 7-21):

```bash
usage() {
  cat <<'USAGE'
Usage:
  school-presentation.sh example --output <school-presentation-full.md>
  school-presentation.sh render --input <input.md> [--html <output.html>]
                                [--manifest <manifest.json>]
                                [--max-size-mb <mb>]
  school-presentation.sh bookmark-pdf --pdf <printed.pdf> --manifest <manifest.json>
                                      [--output <bookmarked.pdf>]
  school-presentation.sh verify --workdir <dir> [--max-size-mb <mb>]
  school-presentation.sh info

Environment:
  SCHOOL_PRESENTATION_MAX_MB  Override the default 50 MB output cap.
USAGE
}
```

**Python module dispatch pattern** (lines 24-49):

```bash
die() {
  printf 'school-presentation.sh: %s\n' "$*" >&2
  exit 1
}

python_renderer() {
  PYTHONPATH="$SCRIPT_DIR${PYTHONPATH:+:$PYTHONPATH}" "${SCHOOL_PRESENTATION_PYTHON:-python3}" -m school_presentation.cli "$SKILL_DIR" "$@"
}

main() {
  local command="${1:-}"
  if [[ $# -gt 0 ]]; then
    shift
  fi

  case "$command" in
    example|render|verify|bookmark-pdf|info)
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
```

**Apply to Phase 41:** implement `school-pptx.sh template-report --theme <id> --out-md <path> --out-json <path>`. Keep wrapper thin; pass `SKILL_DIR` into Python so all asset paths are skill-local.

---

### `skills/school-pptx/scripts/template_report.py` (utility/validator, file-I/O + transform)

**Analog:** `skills/school-presentation/scripts/school_presentation/_engine.py`

**Imports/path/error helper pattern** (lines 1-35):

```python
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
```

**Layout decision/controlled value pattern** (lines 1190-1204):

```python
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
```

**Manifest hierarchy assembly pattern** (lines 1647-1662, 1725-1753):

```python
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
```

```python
slide_manifest: dict[str, object] = {
    "section_index": section_index,
    "section_title": section_title,
    "logical_index": logical_count,
    "display_logical_index": display_logical_label,
    "logical_title": str(slide["title"]),
    "physical_pages": [],
    "reveal_steps": [],
}
```

**Report/evidence write and failure pattern** (lines 4237-4264, 4680-4698):

```python
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
```

```python
write_text(workdir / "verification-manifest.json", json.dumps(verification, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {workdir / 'verification-manifest.json'}")
if verification["status"] != "passed":
    fail("verification failed")
```

**Argparse subcommand pattern** (lines 4856-4874):

```python
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
    p_bookmark_pdf = sub.add_parser("bookmark-pdf")
    p_bookmark_pdf.add_argument("--pdf", required=True)
    p_bookmark_pdf.add_argument("--manifest", required=True)
    p_bookmark_pdf.add_argument("--output")
    sub.add_parser("info")
    args = parser.parse_args(argv)
```

**Apply to Phase 41:** create one command module that loads YAML manifest and PPTX, validates:

- unknown theme with available ids;
- exact 11 required layouts;
- required slot ids per layout;
- duplicate semantic slot ids;
- missing/lost PPTX anchor mapping;
- geometry mismatch with a documented tolerance;
- malformed `text_budget`, `overflow`, `empty_slot`, and `continuation`.

It should always write both Markdown and JSON evidence when output paths are provided, and exit non-zero if `failures` is non-empty.

---

### `skills/school-pptx/references/template-contract.md` (reference doc, transform)

**Analog:** `skills/school-presentation/references/authoring-and-layout.md`

**Reference file purpose pattern** (lines 1-4):

```markdown
# School Presentation Authoring and Layout Reference

This reference holds Markdown authoring, page model, layout, and fixed-canvas rules for the `school-presentation` skill. Keep `SKILL.md` as the concise semantic entry point and update this file when long authoring behavior changes.
```

**Supported layout list pattern** (lines 22-40):

```markdown
## Slide Metadata

Supported `layout` values:

- `auto`
- `cover`
- `closing`
- `section`
- `content`
- `media-right`
- `media-left`
- `media-center`
- `media-compare`
- `media-chart`
- `full_page_image`
- `table`
- `chart`
- `quote`
```

**Fixed canvas rule pattern** (lines 144-149):

```markdown
## Fixed Canvas Rules

- Slide internals must keep fixed design canvas dimensions.
- Do not use viewport-dependent CSS inside slide content, fonts, image heights, or grids.
- Avoid `vh`, `vw`, and viewport-based `clamp()` inside slide layout.
- Across preview sizes and browser zoom levels, only the outer stage scale may change; slide internal relationships must scale like an image.
```

**Apply to Phase 41:** write the long template contract here, not in `SKILL.md`. Include the 11 layout ids, semantic slot naming rules, geometry units/tolerance, text budget fields, template-owned behavior, footer/decorative ownership, and the explicit Phase 41 limitation that budgets are initial calibration values.

---

### `skills/school-pptx/references/template-editing.md` (reference doc, request-response)

**Analog:** `skills/tiaokedan/references/pdf-workflow.md` and `skills/school-presentation/references/verification-contract.md`

**Command shape/reference pattern** (`tiaokedan/references/pdf-workflow.md` lines 5-33):

```markdown
## Command Shapes

只生成 Typst：

```bash
skills/tiaokedan/scripts/tiaokedan.sh render \
  --input skills/tiaokedan/templates/tiaokedan.md \
  --typ build/tiaokedan/tiaokedan.typ
```

生成 Typst 并编译 PDF：

```bash
skills/tiaokedan/scripts/tiaokedan.sh render \
  --input skills/tiaokedan/templates/tiaokedan.md \
  --typ build/tiaokedan/tiaokedan.typ \
  --pdf build/tiaokedan/tiaokedan.pdf
```

`--expected-typ` 是证据/回归 gate；普通教师表单不需要和示例 Typst 逐字节一致，仓库也不要求保留 `.typ` fixture。
```

**Clean output/hidden diagnostics pattern** (`tiaokedan/references/pdf-workflow.md` lines 47-67):

```markdown
## Clean Output Boundary

成功时，公开输出目录只应包含调用方显式请求的教师可用文件：

- `--typ` 指定的 generated Typst。
- `--pdf` 指定的 final PDF。

成功路径不得在公开目录旁生成 status、manifest、log、stderr、stdout、diff、debug JSON、tmp、diagnostic 或 negative fixture 文件。

如果以后需要更丰富的诊断，使用输出目录下隐藏的 `.tiaokedan/` 目录，例如：

```text
build/tiaokedan/
├── tiaokedan.typ
├── tiaokedan.pdf
└── .tiaokedan/
    └── debug-or-failure-evidence
```
```

**Verification command/report pattern** (`school-presentation/references/verification-contract.md` lines 5-14, 70-72):

```markdown
## Verify Command

Run:

```bash
skills/school-presentation/scripts/school-presentation.sh verify --workdir <dir>
```

The command must generate examples, repeat renders, compare stability, inspect generated HTML, and write a verification manifest.
```

```markdown
## Manual Review Notes

Automated verification proves deterministic structure and token coverage. Browser/PDF visual UAT remains required when accepting a new presentation visual feature.
```

**Apply to Phase 41:** document allowed manual edits (move/resize mapped placeholders, add decorative template-owned shapes) and forbidden edits (delete mapped placeholders, replace anchors, duplicate slot ids, add content slots without manifest). Point every manual edit back to `template-report`.

---

### `skills/school-pptx/SKILL.md` (skill entry, request-response)

**Analog:** `skills/tiaokedan/SKILL.md`

**Frontmatter and runtime list pattern** (lines 1-15):

```markdown
---
name: "tiaokedan"
description: "Use when gathering, drafting, reviewing, or rendering a Chinese 调课单/调课说明 adjustment form from teacher facts through tiaokedan.md, generated Typst, and optional final PDF."
metadata:
  short-description: "调课单 Markdown 到 Typst/PDF 工作流"
  version: "0.1.0"
  portability: "canonical"
  supported-runtimes:
    - Codex
    - Claude Code
    - Gemini CLI
    - OpenCode
    - OpenClaw
    - Hermes Agent
---
```

**Inputs/support files pattern** (lines 29-35):

```markdown
## Inputs

- `source_facts`: 教师给出的调课原因、班级、课程、原上课时间/教师、调整后时间/教师、部门、日期和可选备注。
- `templates/tiaokedan.md`: 教师可读 Markdown 样板，也是默认 fixture。
- `references/markdown-contract.md`: 必填字段、可选 `备注`、复核标记和 renderer-owned defaults。
- `references/pdf-workflow.md`: PDF gate、干净输出、隐藏 `.tiaokedan/` 诊断和验证命令。
- `scripts/tiaokedan.sh`: finalized Markdown 的 Typst/PDF 渲染命令。
```

**Command and clean output pattern** (lines 64-77, 90-96):

```markdown
## Finalized Markdown Render/PDF Commands

```bash
skills/tiaokedan/scripts/tiaokedan.sh render \
  --input skills/tiaokedan/templates/tiaokedan.md \
  --typ build/tiaokedan/tiaokedan.typ
```

`--expected-typ` 仅用于临时回归或阶段证据；普通教师表单不需要和示例 Typst 逐字节一致，仓库也不要求保留 `.typ` fixture。
```

```markdown
## Outputs

- `tiaokedan.md`: 教师可编辑的 Markdown source of truth。
- `tiaokedan.typ`: 脚本从 finalized Markdown 生成的 Typst。
- `tiaokedan.pdf`: 只有 `typst compile` 成功且 PDF 非空时才算最终 PDF。

成功路径只写调用方显式指定的 `.typ` 和 `.pdf`。debug 或 failure diagnostics 必须留在隐藏 `.tiaokedan/`，不得混入教师默认交付文件。
```

**Runtime adapter pattern** (lines 79-88):

```markdown
## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 读取项目 `AGENTS.md`、本 `SKILL.md`、`references/`、`templates/` 和 `scripts/`；保持整个 skill folder 同步；教师确认 `tiaokedan.md` 后用 shell 调用 `scripts/tiaokedan.sh`，需要 PDF 时确认 `typst` 和写入权限。 |
| Claude Code | 可把同一整个 skill folder 安装到 `.claude/skills/tiaokedan/`，保留 `SKILL.md`、`references/`、`templates/` 和 `scripts/`；frontmatter `description` 触发后渐进读取支持文件，脚本执行前检查权限。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向本 `SKILL.md`；如果不能自动发现技能，显式读取整个 skill folder 的 `SKILL.md`、`references/`、`templates/` 和 `scripts/`，再按命令手动渲染。 |
| OpenCode | 使用可加载 `SKILL.md` 的 native skill path，或记录 Claude-compatible fallback；安装时保留整个 skill folder，并验证 `references/`、`templates/`、`scripts/` 可读且脚本可执行。 |
| OpenClaw | 作为 AgentSkills-compatible folder 使用；安装时验证 frontmatter 解析、support-file discovery、`SKILL.md`/`references/`/`templates/`/`scripts/` 完整性、脚本执行权限、`python3`、`typst`、sandbox 写权限和隐藏 `.tiaokedan/` 诊断目录行为。 |
| Hermes Agent | 使用 Hermes Agent 可发现的 `SKILL.md` skill folder；安装时验证项目/全局加载路径、support-file discovery、`SKILL.md`/`references/`/`templates/`/`scripts/` 完整性、执行权限、`python3`、`typst`、sandbox 写权限和隐藏 `.tiaokedan/` 诊断目录行为。 |
```

**Apply to Phase 41:** if a minimal `SKILL.md` is created in this phase, keep it concise and defer final workflow/runtime polish to Phase 44. Mention only template contract inputs, `template-report`, outputs, safety boundaries, and whole-folder support-file discovery.

## Shared Patterns

### Skill Folder Shape

**Source:** `skills/README.md` lines 13-31

```markdown
Expected layout:

```text
skills/
└── <skill-name>/
    ├── SKILL.md
    ├── references/
    ├── scripts/
    └── templates/
```

Only `SKILL.md` is required. Add supporting folders only when the skill needs them.
```

Apply to all `skills/school-pptx/` additions.

### Runtime Portability

**Source:** `docs/compatibility-matrix.md` lines 5-13

```markdown
最佳实践是 **one canonical `SKILL.md` first, support files by progressive disclosure, runtime notes second**：

1. 用一个 canonical `SKILL.md` 表达技能语义、触发条件、流程、输出、验证和安全边界。
2. 把长格式规则、examples、renderer notes、artifact contract、UAT 和 troubleshooting 放进 skill-local `references/`，把 helper commands 和 internal modules 放进 `scripts/`，把 Markdown intermediate 或输出 scaffolds 放进 `templates/`。
3. 在同一个 `SKILL.md` 的 adapter notes 中记录各 runtime 的加载路径、frontmatter 限制、工具调用、用户问询、任务/子代理和权限差异。
```

Apply to `SKILL.md`, references, and command docs. Do not add separate runtime adapter files in Phase 41.

### Validation Evidence

**Source:** `school-presentation` verify command, `_engine.py` lines 4267-4299 and 4680-4698

```python
workdir = Path(args.workdir)
workdir.mkdir(parents=True, exist_ok=True)
sample = workdir / "school-presentation-full.md"
cmd_example(argparse.Namespace(output=str(sample)))
...
first_manifest = workdir / "school-presentation-first.manifest.json"
second_manifest = workdir / "school-presentation-second.manifest.json"
m1 = cmd_render(argparse.Namespace(input=str(sample), html=str(first), manifest=str(first_manifest), max_size_mb=args.max_size_mb))
m2 = cmd_render(argparse.Namespace(input=str(sample), html=str(second), manifest=str(second_manifest), max_size_mb=args.max_size_mb))
stable = first.read_bytes() == second.read_bytes()
```

```python
write_text(workdir / "verification-manifest.json", json.dumps(verification, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {workdir / 'verification-manifest.json'}")
if verification["status"] != "passed":
    fail("verification failed")
```

Apply to `template-report`: write Markdown + JSON evidence into explicit `--out-md`/`--out-json` paths or a hidden `.school-pptx/` diagnostics directory when invoked from a public output folder.

### Clean Public Output and Hidden Evidence

**Source:** `skills/tiaokedan/references/pdf-workflow.md` lines 47-67

```markdown
成功路径不得在公开目录旁生成 status、manifest、log、stderr、stdout、diff、debug JSON、tmp、diagnostic 或 negative fixture 文件。

如果以后需要更丰富的诊断，使用输出目录下隐藏的 `.tiaokedan/` 目录，例如：

```text
build/tiaokedan/
├── tiaokedan.typ
├── tiaokedan.pdf
└── .tiaokedan/
    └── debug-or-failure-evidence
```
```

Apply to Phase 41 verification outputs. Reports are explicit evidence outputs; later successful public PPTX rendering must not leak manifest/log/debug files.

### Manual UAT Boundary

**Source:** `skills/school-presentation/references/verification-contract.md` lines 70-72

```markdown
## Manual Review Notes

Automated verification proves deterministic structure and token coverage. Browser/PDF visual UAT remains required when accepting a new presentation visual feature.
```

Apply to template budgets and manual PPTX editing. `template-report` proves structure and mapping, not final pagination or visual perfection.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `skills/school-pptx/templates/standard-school.manifest.yaml` | config/manifest | transform | No existing YAML manifest or PPTX slot-map schema exists. Use Phase 41 research/UI spec for schema and copy provenance/reporting patterns from JSON analogs. |
| `skills/school-pptx/templates/standard-school.pptx` | template asset | file-I/O | Existing skill assets are extracted images and Markdown templates, not normalized PPTX template slides. Copy runtime-asset/provenance rules, not file format internals. |
| PPTX placeholder/alt-text anchor inspection code | utility | file-I/O | No existing `python-pptx` code in repo. Planner should use `python-pptx` research guidance and keep inspection isolated in `template_report.py`. |

## Metadata

**Analog search scope:** `skills/school-presentation/`, `skills/tiaokedan/`, `docs/`, `.planning/phases/41-standard-template-and-manifest/`
**Files scanned:** `rg --files skills`, targeted analog references/scripts, directory specs, compatibility matrix
**Known source evidence:** `test/学院PPT模板.potx`
**Pattern extraction date:** 2026-07-13
