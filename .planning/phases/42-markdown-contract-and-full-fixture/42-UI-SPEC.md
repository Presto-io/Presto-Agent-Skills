---
phase: 42
slug: markdown-contract-and-full-fixture
status: approved
shadcn_initialized: false
preset: none
created: 2026-07-13
---

# Phase 42 - UI Design Contract

> Visual and interaction contract for the teacher-reviewable Markdown source, full fixture, and `validate` / `example` CLI surfaces.

---

## Scope

Phase 42 does not create a web application or style PPTX slides. Its user-facing interfaces are:

- The constrained YAML plus `::: slide {layout="..."}` Markdown source that teachers review and agents author.
- The realistic full fixture and skill-local companion media used to understand the complete contract.
- The `validate` command, including source-located aggregate diagnostics and optional logical-document JSON.
- The deterministic `example --out-dir <dir>` command, including its overwrite boundary and completion summary.
- The semantic experience of 11 controlled layouts: 10 explicit authorable layouts plus one implicit template-owned `closing` page.

Out of scope: PPTX coordinates, font choices, colors, decorative assets, arbitrary styling controls, physical-slide rendering, pagination implementation, PPTX notes XML, runtime adapter documentation, and final visual UAT.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | manual / none |
| Preset | not applicable |
| Component library | none |
| Icon library | none; CLI status uses plain text tokens |
| Font | Markdown viewer or terminal default; PPTX typography remains template-owned |

No React, shadcn, browser UI, third-party registry, or remote UI dependency is part of this phase. The interface consists of portable Markdown, deterministic files, stable command syntax, and plain-text diagnostics.

Authoring controls are semantic only. The public Markdown grammar must not expose coordinates, frame dimensions, fonts, colors, crop controls, footer placement, decorative assets, or arbitrary style attributes. The manifest remains the source of truth for theme and layout ownership, but raw manifest geometry is not repeated in the authoring contract or fixture.

---

## Spacing Scale

Declared values for rendered Markdown documentation and reports (multiples of 4):

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Inline code and compact diagnostic metadata |
| sm | 8px | Related syntax lines and diagnostic detail |
| md | 16px | Paragraph, list, and table rhythm |
| lg | 24px | Subsection separation |
| xl | 32px | Major contract sections |
| 2xl | 48px | Example and diagnostic groups |
| 3xl | 64px | Document-level separation only |

Exceptions: terminal output follows terminal line spacing; fenced code preserves source indentation. These values describe review surfaces only and never become Markdown-controlled PPTX geometry.

---

## Typography

Documentation and optional rendered reports use a constrained review scale. Source Markdown remains plain text, and PPTX typography remains template-owned.

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 16px | 400 | 1.5 |
| Label | 14px | 400 | 1.4 |
| Heading | 20px | 600 | 1.25 |
| Display | 28px | 600 | 1.2 |

Rules:

- Use exactly these four sizes and only weights 400 and 600 in rendered contract/report guidance.
- Syntax keywords, file paths, layout ids, field names, and commands use inline or fenced monospace presentation supplied by the Markdown viewer.
- Do not use typography to encode validation state; every state also has explicit text.
- No font family, font size, line height, or text box setting is authorable in presentation Markdown.

---

## Color

The Markdown source and CLI must remain understandable without color. The following palette applies only when a Markdown viewer renders contract or validation evidence; it does not control PPTX output.

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#FFFFFF` | Documentation and report background |
| Secondary (30%) | `#F3F4F6` | Code blocks, tables, neutral diagnostic groups |
| Accent (10%) | `#2563EB` | Command links, active source reference, controlled layout id |
| Destructive | `#B91C1C` | Validation errors and unsafe overwrite failures only |

Accent reserved for: command links, the currently referenced source location, and controlled layout ids in documentation. Pass and warning states may use `#15803D` and `#A16207` respectively, but must always include `PASS`, `警告`, or `错误` text.

Authors cannot select or override any PPTX color, highlight color, theme color, or background color. `==highlight==` is semantic emphasis whose visual mapping is template-owned.

---

## Information Hierarchy

### Markdown source

Review order must be stable and obvious:

1. YAML formatter metadata.
2. Optional single document `#` title fallback.
3. Explicit logical slide blocks in presentation order.
4. Exactly one `##` logical title inside each ordinary content slide.
5. Top-level content blocks, with optional `###` block subheadings.
6. Optional `::: notes` as the final child of its owning slide.
7. Implicit template-owned `closing`, documented but absent from authored source.

The fixture must read as a coherent vocational-college intelligent-manufacturing curriculum presentation. Layout coverage is supporting evidence, not visible test-matrix prose.

### Validation output

Output order:

1. Overall `校验通过` or `校验失败` summary.
2. Input path and controlled theme.
3. Error count and warning count.
4. Diagnostics in source order.
5. Coverage summary: `10 个显式布局 + 1 个隐式 closing`.
6. Optional logical-document JSON path when explicitly requested.
7. One concrete next action.

Errors appear before warnings. The terminal summary must remain useful when color and Unicode decoration are unavailable.

---

## Authoring Syntax Contract

### YAML formatter

The only public fields are, in this order in generated examples:

```yaml
---
title: "职业院校智能制造课程建设"
subtitle: "课程体系、实训条件与实施路径"
school: "示例职业技术学院"
department: "智能制造学院"
program: "机电一体化技术"
course: "智能产线安装与调试"
author: "课程建设团队"
presenter: "张老师"
date: "2026-07-13"
theme: "standard-school"
---
```

Optional values are omitted rather than left as empty placeholders. If `title` is absent, the first and only document-level `#` heading becomes the title fallback. A `#` heading never enters contents. Unknown YAML fields are errors, not warnings.

### Slide and notes blocks

Canonical source shape:

```markdown
::: slide {layout="title-content"}
## 建设目标

### 课程目标

围绕**岗位能力**组织课程内容，并用==真实任务==贯穿教学。

::: notes
先说明课程目标，再说明任务来源。
:::
:::
```

Contract rules:

- Public slide openers accept only `layout`; development-only `id` never appears in docs, fixtures, normal validation, or visible output.
- An ordinary authorable slide contains exactly one `##`; slide blocks outside the two generated special layouts cannot omit or repeat it.
- A `### 标题` binds only to the immediately following complete top-level block. Empty `###` creates a boundary without visible subheading.
- Paragraph, complete list, image, table, and fenced code are atomic top-level blocks for author review.
- `::: notes` is optional, appears at most once, and must be the final child. Notes are excluded from visible blocks and contents.
- Standard `**bold**` and constrained `==highlight==` are the only added emphasis semantics. Raw HTML and generic attribute lists are rejected outside fenced code.

---

## Layout Experience

The controlled template has 11 layouts. The public source authors exactly 10; `closing` is the implicit eleventh layout.

| Layout | Authoring experience | Required semantic content | Review and validation behavior |
|--------|----------------------|---------------------------|--------------------------------|
| `cover` | Explicit empty slide block | YAML/document title and optional cover metadata | No `##` or body; omitted metadata stays omitted without exposing layout controls |
| `contents` | Explicit empty slide block | Entries generated from later valid `##` headings | No authored list or `##`; never includes `#`, cover, or contents itself |
| `section` | Explicit block | One `##` title | Divider only; body content is rejected |
| `title-content` | Explicit block | One `##` plus one or more ordered blocks | Long/splittable input remains one logical slide for Phase 43 pagination |
| `two-column` | Explicit block | One `##` plus ordered blocks | Pair blocks 1/2, 3/4; final unpaired block is left-side semantic content with empty right side |
| `image-text` | Explicit block | One `##`, one stable body block, then one or more images | Each image/caption is atomic; successive images reuse title, body, and notes |
| `table` | Explicit block | One `##` and one Markdown table | Optional bound `###` is table title, distinct from slide title; long rows are pagination input |
| `timeline` | Explicit block | One `##` and one table with `时间 | 标题 | 说明` columns | Row order is timeline order; malformed or renamed required columns fail clearly |
| `gallery` | Explicit block | One `##` and consecutive Markdown images | Alt text is caption; more than four images is intentional pagination input |
| `code` | Explicit block | One `##` and one fenced code block | Language tag is preserved; code that contains HTML/CSS-like text is not treated as author styling |
| `closing` | Not authorable | Fixed template-owned final page | Validator rejects explicit `layout="closing"`; logical model records one implicit closing at deck end |

Canonical special-layout syntax:

```markdown
::: slide {layout="cover"}
:::

::: slide {layout="contents"}
:::
```

Coverage language must always say `11/11 controlled layout semantics: 10 explicit + 1 implicit`. It must never imply that `closing` can be authored or customized.

---

## Media and Notes Experience

- Images and icons use ordinary `![alt](path)` syntax. No private `icon=`, crop, position, or size directive is available.
- Relative paths resolve from the Markdown file directory; absolute paths are accepted but clearly reduce portability.
- Alt text is the visible caption; empty alt means no caption.
- Image and caption form one indivisible semantic block. Later rendering uses template-owned contain placement without exposing crop or geometry controls.
- Missing media is a validation error with source path, line, slide title when known, and original media path. A diagnostic model may carry safe placeholder metadata, but validation still returns non-zero.
- Notes retain their source line and Markdown text, but never appear in contents or visible slide blocks. A logical slide expanded later shares the same notes across its physical slides.

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Primary CTA | `校验演示文稿` |
| Secondary CTA | `生成完整示例` |
| Empty state heading | `未找到可写幻灯片` |
| Empty state body | `请添加 10 个可写布局之一的 ::: slide {layout="..."} 块，然后重新运行 validate。closing 由模板自动追加。` |
| Success state | `校验通过：10 个显式布局，1 个隐式 closing，未发现错误。` |
| Error state | `校验失败：发现 {error_count} 个错误和 {warning_count} 个警告。请按下列源位置修复后重新运行 validate。` |
| Destructive confirmation | No interactive confirmation. `example` may overwrite only its documented fixed Markdown and companion-media files; it must not delete or replace unrelated files. |

Command labels and usage:

```text
school-pptx.sh validate --input <deck.md> [--out-json <logical-document.json>]
school-pptx.sh example --out-dir <dir>
```

Successful `example` output:

```text
示例已生成：<dir>/school-pptx-full.md
配套媒体：<dir>/media/（{count} 个固定文件）
覆盖范围：11/11 controlled layout semantics（10 explicit + 1 implicit）
校验结果：PASS
```

Overwrite copy:

```text
已覆盖命令自有文件：<fixed-paths>
已保留输出目录中的其他文件。
```

---

## Diagnostic Contract

Every locatable diagnostic uses this plain-text shape:

```text
<path>:<line>:<column> [<CODE>] <message>
  slide: <logical title or "unknown">
  layout: <layout id or "unknown">
  fix: <one concrete corrective action>
```

Line and column numbers are 1-based. Diagnostics are aggregated where parsing can continue and sorted by source position. One bad input must never be reported as a successful validation.

Required messages:

- Unknown YAML field: `不支持 YAML 字段 "{field}"。允许字段：title, subtitle, school, department, program, course, author, presenter, date, theme。`
- Unknown theme: `未知主题 "{theme}"。可用主题：standard-school。`
- Missing layout: `slide 块缺少必需的 layout 属性。请选择一个可写布局。`
- Unknown layout: `不支持布局 "{layout}"。可写布局：cover, contents, section, title-content, two-column, image-text, table, timeline, gallery, code。`
- Explicit closing: `closing 由模板在文稿末尾自动追加，不能在 Markdown 中显式创建或修改。`
- Unknown slide attribute: `不支持 slide 属性 "{attribute}"。公开契约只允许 layout。`
- Unsupported styling: `Markdown 只能表达语义内容，不能设置坐标、尺寸、字体、颜色、裁剪、页脚或任意 style 属性。`
- Raw HTML: `不支持原始 HTML。请改用契约允许的 Markdown 块；fenced code 内的代码文本除外。`
- Missing media: `找不到媒体 "{original_path}"。路径相对于 Markdown 文件解析；请补充文件或修正引用。`
- Notes position: `notes 必须是所属 slide 的最后一个子块，且每个 slide 最多一个。`
- Invalid heading: `每个普通内容 slide 必须且只能包含一个 ## 标题；# 仅用于文档标题 fallback。`
- Invalid timeline: `timeline 必须使用列名“时间 | 标题 | 说明”的 Markdown 表格。`

Do not dump stack traces by default. Unexpected internal failures use `school-pptx: 内部错误：{summary}` and point to an explicit debug/evidence path only when one was requested or safely created under a hidden work directory.

---

## Full Fixture Contract

The canonical fixture must:

- Be stored under `skills/school-pptx/fixtures/`, not `templates/`.
- Tell a coherent story titled around vocational-college intelligent-manufacturing curriculum development.
- Use `theme: "standard-school"` and only the ten public authorable layouts.
- Demonstrate document title behavior, contents order from `##`, visible and empty `###` boundaries, bold, theme-controlled highlight, notes, relative images/icons, captions, and empty captions.
- Include reviewable overflow inputs: long text, long table, long timeline, more than four gallery images, long code, multiple `image-text` images, and both paired and final-unpaired `two-column` blocks.
- Keep all positive-fixture media present, skill-local, source-clear, and network-independent.
- Never show PPTX coordinates, fonts, colors, arbitrary style attributes, explicit closing syntax, unresolved review markers, or missing media as accepted source.

The fixture should make layout changes legible through semantic structure and headings, not through comments such as `layout test 1/11`.

---

## Example Command Safety

`example --out-dir <dir>` is deterministic and idempotent:

- Create missing parent directories.
- Write the fixed `school-pptx-full.md` path and a documented fixed set of companion media paths.
- Overwrite only those command-owned fixed paths.
- Preserve every unrelated file and directory under `<dir>`; never run recursive deletion on the output directory.
- Do not emit timestamps, random ids, machine-specific absolute paths, logs, manifests, or debug evidence into the public example directory.
- Validate the copied Markdown before reporting success.
- Return non-zero if the output path is unsafe, unwritable, collides with a directory where a file is required, or the copied fixture fails validation.
- Repeated successful runs must produce byte-for-byte identical Markdown and media.

Failure copy:

```text
示例生成失败：{reason}
未删除输出目录中的任何无关文件。
修复：{one concrete action}
```

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| none | none | not applicable - no UI registry is used |

No shadcn block, third-party component registry, network-fetched template, or remote media dependency is allowed in Phase 42.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved
