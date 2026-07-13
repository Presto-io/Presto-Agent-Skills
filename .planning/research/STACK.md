# Technology Stack

**Project:** v1.17 `school-pptx`
**Researched:** 2026-07-13
**Scope:** 新增 `school-pptx` 技能的技术栈增量和实现边界
**Overall confidence:** HIGH for `python-pptx`/Pandoc documented capabilities; MEDIUM for Open XML transition post-processing because it requires fixture validation in PowerPoint/WPS/Keynote.

## Recommended Stack

### Core Runtime

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | 3.11+ recommended; current local `python3` is 3.14.6 | Skill-local renderer and verification scripts | 仓库现有技能已经偏向 Python/脚本化渲染；Python 标准库可处理 zip/XML/JSON/CLI orchestration，新增认知成本低。建议写 3.11+，避免把本机 3.14 作为用户环境硬要求。 |
| `python-pptx` | 1.0.2 | Primary PPTX object writer | 官方文档支持从模板打开/保存演示文稿，添加 slides、shapes、text frames、pictures、tables、speaker notes；当前 PyPI 可用最新版本为 1.0.2。本机尚未安装，需要作为新增轻量依赖。 |
| Pandoc CLI | 3.x; current local `pandoc` is 3.10 | Markdown parsing/normalization and optional reference conversion | 官方文档支持 Markdown 到 pptx、`reference.pptx`、slide-level、speaker notes div、PowerPoint layout 名称约定。对本技能更适合作为 Markdown AST/contract parser，而不是最终 PPTX writer。 |
| Python stdlib `zipfile` + `xml.etree` or `lxml` via `python-pptx` dependency | stdlib / transitive | Controlled Open XML inspection and small post-processing | PPTX 是 Open XML zip 包。`python-pptx` 没有覆盖所有 PresentationML 功能，transition、模板内部元数据、notes/shape 校验可通过受控 XML patch/inspection 完成。 |

### Template and Assets

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Standardized `.pptx` template derived from supplied `.potx` | Skill-local artifact | Canonical machine-mappable template | `.potx` 适合人工套用模板，但脚本最好从标准 `.pptx` 读取固定 slide layouts/placeholders。先手工规范化模板，比让脚本猜测人类视觉样张可靠。 |
| Template manifest JSON/YAML | Skill-local, generated/hand-reviewed | Layout id, slot names, frame geometry, text budgets, continuation rules | Markdown 不应控制坐标、字号、颜色。模板 manifest 把布局槽位、预算和 overflow 规则固定下来，方便 roadmap 拆成模板标准化、合同 fixture、渲染器、验证 gate。 |
| Image assets | PNG/JPEG/SVG converted if needed | School logo, icons, source images | `python-pptx` can add picture files. For editable PPTX stability, prefer PNG/JPEG for bitmap content; avoid SVG as a first-slice requirement unless fixture proves target Office stack renders it consistently. |

### Verification

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `python-pptx` reader | 1.0.2 | Verify slide count, layout use, shape presence, notes text, table dimensions, media references | Same object model can inspect generated PPTX enough for repeatable gates. |
| Open XML zip/XML inspection | stdlib + optional `lxml` | Verify raw package parts, transition XML, relationships, placeholder ids, hidden work artifacts | Some properties are not surfaced by `python-pptx`; XML-level checks prevent false green results. |
| Optional Pandoc AST snapshot | Pandoc 3.x JSON | Verify Markdown contract parsing before rendering | Keeps the teacher-reviewable Markdown contract separate from PPTX layout bugs. |

## Recommended Division of Labor

### `python-pptx`: Use as the primary generator

Best for:

- Opening the standardized `.pptx` template and adding slides from known layouts.
- Creating editable text boxes, runs, paragraphs, simple bullet/list text, and non-highlighted code text boxes.
- Adding pictures with calculated contain-style placement. Avoid picture placeholders for first slice because official behavior crops to fill the placeholder.
- Adding basic editable tables and setting row/column dimensions within fixed template budgets.
- Writing speaker notes through `slide.notes_slide.notes_text_frame`.
- Applying bounded text fitting through explicit font-size budgeting and `TextFrame.fit_text()`/word-wrap behavior where it proves stable with installed fonts.
- Reading back generated PPTX for smoke verification.

Not suitable for:

- Complex object animation.
- Reliable creation of slide transitions through public API.
- Automatic semantic pagination. The renderer must own page budgeting and continuation slide creation before writing shapes.
- Arbitrary `.potx` marketplace templates. Layout and placeholder names need a controlled standard.
- Pixel-perfect PowerPoint typography across platforms. Text fitting depends on available fonts and PowerPoint/WPS rendering differences, so budgets must be conservative.

### Pandoc: Use as parser and reference tool, not the final renderer

Best for:

- Parsing structured Markdown, fenced divs, tables, lists, code blocks, and notes into a consistent AST.
- Enforcing a `slide-level`/logical-slide contract during fixture development.
- Validating that speaker notes can be represented in Markdown using `notes` divs.
- Generating a quick reference `.pptx` only for comparison or debugging.

Not suitable for this skill's final output:

- Pandoc's PowerPoint writer chooses from predefined layout names and has limited control over school-specific slot geometry.
- Column width behavior is explicitly limited for PowerPoint output, which conflicts with fixed two-column and image-text layouts.
- It cannot own custom overflow splitting, elastic textbox budgets, four-image gallery packing, timeline subdivision, or template-specific continuation rules cleanly.
- It may silently fall back to default layouts if expected names are missing, which is too loose for a strict school template.

### Open XML post-processing: Keep small, audited, and fixture-gated

Use only for:

- Adding or preserving a simple slide transition if the standardized template or generated slides cannot handle it through `python-pptx`.
- Inspecting package relationships, notes parts, media parts, placeholder ids, and slide layout references.
- Repairing/normalizing narrow template metadata when it is deterministic and covered by fixtures.

Do not use for:

- General slide layout construction.
- Large-scale table/text/picture generation.
- Freeform animation authoring.
- Office-suite automation that requires PowerPoint, WPS, LibreOffice, or Keynote to be installed.

Transition recommendation: treat transition as optional and late. The roadmap should first prove the editable-object deck without transition. Then add a narrow Open XML experiment for a 0.5s smooth/fade-like slide transition and accept it only if generated XML round-trips in Microsoft PowerPoint and at least one common fallback viewer without corrupting the file. If not proven, preserve a transition already embedded in the template or omit transitions.

## Implementation Boundaries for Requirements and Roadmap

1. Start with template standardization, not script rendering.
   - Convert the supplied `.potx` visual sample into a skill-local `.pptx` template.
   - Name every supported layout and slot deterministically.
   - Create a template manifest with slide size, layout key, placeholder/shape name, frame geometry, default font, min/max font, and overflow budget.

2. Keep Markdown logical, not visual.
   - Accept YAML metadata plus explicit `::: slide {layout="..."}` blocks.
   - `theme` must be a controlled template identifier, not arbitrary style input.
   - Do not accept Markdown-level coordinates, colors, fonts, crop values, or PowerPoint XML snippets.

3. Build pagination before object writing.
   - One logical slide may emit multiple physical slides.
   - Text, tables, timelines, and galleries need budget estimators that choose continuation slides before writing PPTX.
   - The renderer should never rely on PowerPoint's visual overflow behavior as a success path.

4. Make editable objects the default.
   - Text -> PPTX text boxes/placeholders.
   - Tables -> editable PPTX tables, split by rows when budget exceeded.
   - Code -> monospaced editable text box without syntax highlighting in v1.17.
   - Images -> placed picture objects with contain-style geometry.
   - Timeline/gallery -> editable lines/shapes/text/pictures where feasible; otherwise defer complexity rather than rasterizing the whole slide.

5. Use speaker notes as a first-class contract.
   - Markdown `::: notes` maps to `slide.notes_slide.notes_text_frame`.
   - Verification should read notes back and fail if notes are missing from expected slides.

6. Keep verification artifact-driven.
   - Verify slide count, logical-to-physical slide mapping, layout names, shape names, notes text, table row/column counts, image relationships, code textbox presence, and non-empty PPTX package.
   - Add XML-level checks only for capabilities not surfaced by `python-pptx`, especially transitions and package relationships.

## Not Recommended Heavy Dependencies

| Dependency | Why Not |
|------------|---------|
| LibreOffice/headless office conversion | Too heavy and viewer-dependent; tends to produce unstable layout and is hard to make portable across Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent. |
| PowerPoint COM / AppleScript / Office automation | Requires installed desktop Office and OS-specific automation; violates portable skill boundary. |
| Node PPTX stacks such as PptxGenJS or pptx-automizer | Adds a second runtime and duplicates `python-pptx` responsibilities. Useful elsewhere, but not justified when the user explicitly allows `python-pptx` and wants no heavier dependencies. |
| Playwright/browser screenshot rendering | Produces raster slides or HTML-first workflows, which conflicts with editable PPTX objects. Keep this out of `school-pptx`; it belongs to `school-presentation`. |
| Marp/Slidev/reveal.js as core renderer | Strong Markdown presentation ecosystems, but their PPTX paths are not the controlled editable-object, fixed-template renderer required here. |
| Full Open XML SDK / Java/.NET stack | More powerful than needed and introduces a heavyweight runtime. Use raw zip/XML only for narrow post-processing. |
| ImageMagick-heavy pipelines | Avoid making image conversion a hard requirement. Use existing source images and Python/Pillow only where already pulled by `python-pptx`. |

## Installation

Recommended dependency expression for the skill-local renderer:

```bash
# Required Python dependency
python3 -m pip install "python-pptx==1.0.2"

# Required external CLI when using Pandoc AST parsing
pandoc --version
```

If the project later introduces a lockfile for skills, pin `python-pptx==1.0.2` and document Pandoc as an external CLI prerequisite rather than vendoring it into the repository.

## Sources and Confidence

| Source | Confidence | Notes |
|--------|------------|-------|
| `python-pptx` official docs: https://python-pptx.readthedocs.io/en/latest/ | HIGH | Confirms slides, shapes, pictures, tables, text frames, text fitting, and speaker notes APIs. |
| PyPI `python-pptx`: https://pypi.org/project/python-pptx/ | HIGH | Confirms current available package line; `pip index versions` found 1.0.2. |
| Pandoc manual: https://pandoc.org/MANUAL.html | HIGH | Confirms PowerPoint writer, `reference.pptx`, slide-level, speaker notes, and layout-name behavior. |
| Pandoc local CLI `pandoc 3.10` | HIGH for current workspace | Confirms the repository machine already has Pandoc with Lua support available. |
| Microsoft Open XML / PresentationML documentation | MEDIUM | Confirms the format layer exists for narrow zip/XML inspection and patching, but transition behavior still needs fixture validation in real viewers. |

## Roadmap Recommendation

Suggested phase split for `school-pptx`:

1. **Template normalization and manifest** - standard `.pptx`, named layouts/slots, fixture deck, manifest, and XML/readback inspection.
2. **Markdown contract and AST parser** - YAML, `::: slide`, `::: notes`, layout allowlist, table/code/image contracts, and parser diagnostics using Pandoc JSON.
3. **Editable PPTX renderer** - `python-pptx` object generation for text, notes, images, tables, code, timeline/gallery basics, and continuation slides.
4. **Overflow and verification gate** - budget estimators, logical-to-physical mapping, strict readback checks, XML package checks, and optional transition experiment.

Do not make transitions, arbitrary template import, syntax highlighting, complex animation, or Office-driven visual export part of the minimum accepted slice.
