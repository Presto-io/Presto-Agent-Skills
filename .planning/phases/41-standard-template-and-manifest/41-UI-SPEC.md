---
phase: 41
slug: standard-template-and-manifest
status: approved
shadcn_initialized: false
preset: none
created: 2026-07-13
reviewed_at: 2026-07-13T07:10:31Z
---

# Phase 41 - UI Design Contract

> Visual and interaction contract for the `school-pptx` template, manifest, and template-report surfaces. Generated for GSD planning and verification.

---

## Scope

Phase 41 does not create an application screen. The user-facing surfaces are:

- The normalized skill-local `.pptx` template that humans inspect and adjust in PowerPoint or a compatible editor.
- The YAML manifest that reviewers and later scripts use as the slot contract.
- The `template-report` Markdown report and JSON evidence.
- CLI validation errors for unknown theme, missing layouts, missing slots, duplicate slots, lost placeholder mapping, geometry mismatch, and malformed text budgets.
- Manual editing guardrails that explain what can be changed in the PPTX template without breaking slot mapping.

Out of scope: Markdown authoring syntax, Markdown-to-PPTX rendering, pagination quality, runtime adapter docs, and final visual UAT.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | manual / none |
| Preset | not applicable |
| Component library | none |
| Icon library | none for runtime output; report status symbols may use plain text tokens only |
| Font | Template-owned PPTX fonts; reports use system sans-serif in Markdown viewers |

No React, shadcn, browser UI, or third-party component registry is part of this phase. The contract is implemented through stable document assets, YAML fields, and deterministic CLI report copy.

---

## Spacing Scale

Declared values (must be multiples of 4):

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Inline report metadata separators, compact YAML examples |
| sm | 8px | Report table cell padding expectation, compact note spacing |
| md | 16px | Default report section spacing, manifest example grouping |
| lg | 24px | PPTX slot gutters and report major subsection rhythm |
| xl | 32px | PPTX layout band spacing and large slot separation |
| 2xl | 48px | Template section breaks and cover/closing visual breathing room |
| 3xl | 64px | Major canvas regions and title-to-body separation |

Exceptions: none. PPTX geometry may be stored in EMU or inches, but any human-facing normalized measurements must round to this 4px-equivalent rhythm where practical.

---

## Typography

Reports and manifest documentation must use a constrained type scale. PPTX slide fonts are template-owned and recorded in the manifest, not controlled from Markdown.

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 16px | 400 | 1.5 |
| Label | 14px | 400 | 1.4 |
| Heading | 20px | 600 | 1.25 |
| Display | 28px | 600 | 1.2 |

Rules:

- Use exactly these four sizes for Markdown report examples and documentation snippets.
- Use only 400 and 600 weights in report styling guidance.
- Manifest text budgets must record `font_size_min`, `font_size_max`, `max_chars`, `max_lines`, and `overflow`.
- PPTX slot text may shrink only inside the manifest-defined font-size range; visible overflow is invalid.

---

## Color

The normalized template owns final PPTX colors. Reports and examples use a restrained review palette that does not compete with the school template.

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#FFFFFF` | PPTX/report background and report body surface |
| Secondary (30%) | `#F3F4F6` | Report tables, code blocks, neutral manifest examples |
| Accent (10%) | `#2563EB` | Available theme id, current layout id, report links, focus on the first failing item |
| Destructive | `#B91C1C` | Fatal validation failures only |

Accent reserved for: available controlled theme identifier, active/current layout id in reports, report links, and the first failing validation item. Accent must not mean "all interactive elements" and must not be used for decorative PPTX assets unless the source school template already owns that color.

Status colors:

- Pass: `#15803D`, only for successful validation rows.
- Warning: `#A16207`, only for non-fatal calibration notes.
- Fail: `#B91C1C`, only for validation errors that cause non-zero exit.

---

## Visual Hierarchy

Primary focal point: the controlled theme and 11-layout coverage summary at the top of the `template-report` Markdown output.

Hierarchy order:

1. Validation status and selected theme.
2. Missing or failing layouts/slots, if any.
3. Layout coverage table for `cover`, `contents`, `section`, `title-content`, `two-column`, `image-text`, `table`, `timeline`, `gallery`, `code`, and `closing`.
4. Slot-level detail: semantic slot id, placeholder mapping, geometry, text budget, empty-slot rule, and continuation behavior.
5. Manual edit guardrails and calibration notes.

The normalized `.pptx` template should make mapped content slots visually inspectable without exposing Markdown-controlled styling. Decorative elements, footer behavior, colors, and typography remain template-owned.

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Primary CTA | `生成模板报告` |
| Empty state heading | `未找到模板槽位` |
| Empty state body | `请检查规范化 PPTX 是否包含 manifest 中列出的语义槽位，然后重新运行 template-report。` |
| Error state | `模板校验未通过：{reason}。请修复 PPTX 模板或 YAML manifest 后重新运行 template-report。` |
| Destructive confirmation | No destructive action in Phase 41. Template normalization must not delete the supplied visual source automatically. |

Required error messages:

- Unknown theme: `未知主题 "{theme}"。可用主题：{available_theme_ids}。`
- Missing layout: `模板缺少布局 "{layout}"。Phase 41 必须覆盖 11 个受控布局。`
- Missing slot: `布局 "{layout}" 缺少槽位 "{slot}"。请恢复占位符映射或更新 manifest。`
- Duplicate slot: `布局 "{layout}" 存在重复槽位 "{slot}"。请保留唯一语义槽位 id。`
- Lost placeholder mapping: `槽位 "{layout}.{slot}" 找不到对应 PPTX 占位符。请勿删除或替换映射锚点。`
- Geometry mismatch: `槽位 "{layout}.{slot}" 的 PPTX 几何与 manifest 不一致。请同步 manifest 或重新调整模板。`
- Malformed budget: `槽位 "{layout}.{slot}" 的文本预算不完整。必须包含 max_chars、max_lines、font_size_min、font_size_max 和 overflow。`

Report section labels:

- `主题`
- `布局覆盖`
- `槽位映射`
- `文本预算`
- `手动编辑守则`
- `校验结果`

---

## Template Asset Contract

Normalized template:

- Runtime source is the skill-local normalized `.pptx`, not the original `.potx`.
- The original `.potx` is visual source evidence only and should not be a long-term runtime dependency.
- All 11 layouts must be inspectable in the normalized `.pptx` through either slide layouts, template slides, or another explicit PPTX mapping mechanism chosen during implementation.
- Each mapped slot needs a stable semantic id. Do not expose localized or unstable raw PowerPoint names as the public contract.

Template-owned behavior:

- Markdown cannot override geometry, fonts, colors, decorative assets, footer behavior, or bounded text behavior.
- Decorative shapes may exist, but must not be listed as Markdown-controllable slots.
- Footer behavior is controlled by the template/manifest and must be consistent across layouts.

Manual editing guardrails:

- Allowed: drag, resize, and refine mapped placeholders; add decorative template-owned shapes; adjust theme-owned visual polish.
- Not allowed: delete mapped placeholders, replace mapped placeholders with ordinary shapes, remove mapping anchors, duplicate slots without unique ids, or add content slots without manifest entries.
- After any manual edit, run `template-report` and inspect both Markdown report and JSON evidence.

---

## Manifest Review Contract

The YAML manifest must be reviewable by humans and machine-readable by validators.

Required top-level content:

- Controlled default theme identifier.
- Available theme list.
- Template file reference.
- Layout list containing exactly the 11 v1.17 layout ids.
- Slot map for every layout.
- Footer/decorative ownership rules.

Required slot content:

- `id`: stable semantic slot id.
- `purpose`: short human-readable purpose.
- `placeholder`: PPTX mapping metadata.
- `geometry`: x, y, width, height in normalized units.
- `text_budget`: `max_chars`, `max_lines`, `font_size_min`, `font_size_max`, `overflow`.
- `empty_slot`: hide, preserve, or fail.
- `continuation`: none, paginate, repeat_header, or layout-specific rule.

Slot ids should use common names such as `title`, `subtitle`, `body`, `media`, `caption`, and `footer`, plus layout-specific names such as `left_body`, `right_body`, `table`, `timeline_items`, `gallery_items`, and `code`.

---

## Template-Report Contract

`template-report` must produce:

- A human-readable Markdown report for Phase 41 evidence.
- Machine-readable JSON evidence for later structural verification.
- Non-zero exit for unknown theme, missing required layout, missing slot, duplicate slot, lost placeholder mapping, geometry mismatch, and missing or malformed budget fields.

Markdown report order:

1. Summary status.
2. Theme validation.
3. Layout coverage.
4. Slot mapping table per layout.
5. Text budget validation.
6. Manual edit guardrails.
7. JSON evidence path.

JSON evidence must include:

- `theme_id`
- `template_path`
- `manifest_path`
- `layouts`
- `slots`
- `failures`
- `warnings`
- `generated_at`

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| none | none | not applicable - no UI registry is used |

No third-party registry, shadcn block, remote component source, or network-fetched UI dependency is allowed in Phase 41.

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS
- [ ] Dimension 2 Visuals: PASS
- [ ] Dimension 3 Color: PASS
- [ ] Dimension 4 Typography: PASS
- [ ] Dimension 5 Spacing: PASS
- [ ] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-07-13
