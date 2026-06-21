# Phase 37: 调课单 Typst Baseline - Research

**Researched:** 2026-06-21
**Domain:** Typst document baseline / skill scaffold
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
## Implementation Decisions

### Page And Typography
- **D-01:** The baseline form uses A4 landscape orientation with default page margins.
- **D-02:** The title text is `调课说明`, centered, SimSun/宋体, 二号, bold.
- **D-03:** Body paragraphs use FangSong/仿宋, 四号, distributed alignment.
- **D-04:** The first recipient line has no first-line indent and reads `教务处：`.
- **D-05:** The explanatory paragraph uses the same FangSong 四号 distributed style, with first-line indent.

### Body Copy
- **D-06:** The explanatory paragraph content is locked as:

  `因我系专职教师周老师需要去企业调研，故需将其3月11日所承担实习课程调整为早班，同时涉及到孙老师老师，具体调整如下：`

### Adjustment Table
- **D-07:** The form contains one table spanning the full text block/page body width.
- **D-08:** The table has 8 columns, multiple rows, FangSong 四号 text, and all cell content is horizontally and vertically centered.
- **D-09:** Column headers are:

  | 序号 | 班级 | 课程 | 原上课时间 | 原授课教师 | 调整后上课时间 | 调整后上课教师 | 备注 |
  |------|------|------|------------|------------|----------------|----------------|------|

- **D-10:** The hand-authored Typst baseline should include these example rows:

  | 序号 | 班级 | 课程 | 原上课时间 | 原授课教师 | 调整后上课时间 | 调整后上课教师 | 备注 |
  |------|------|------|------------|------------|----------------|----------------|------|
  | 1 | 27WG电气3班 | 高压电器装配与调试 | 2026年3月11日<br>14:00-19:00（D104） | 周老师 | 2026年3月11日<br>7:30-13:00（D104） | 周老师 |  |
  | 2 | 27WG电气3班 | 高压电器装配与调试 | 2026年3月11日7:30-13:00（D104） | 孙老师 | 2026年3月11日14:00-19:00（D104） | 孙老师 |  |

### Closing Signature
- **D-11:** Below the table, leave a public-document-style blank distance before the closing signature.
- **D-12:** The closing signature uses FangSong 四号 and contains:

  `电气工程系`

  `2026年6月21日`

- **D-13:** The closing signature should sit in the traditional right-side closing area under the table, visually similar to official-document formatting.

### Claude's Discretion
- Translate the user-facing font sizes into Typst-friendly point sizes during planning/implementation, while preserving the Chinese typography intent.
- Choose exact table column widths, row heights, line spacing, and blank distance under the table as long as the rendered PDF matches the described A4 landscape official-form feel.

### the agent's Discretion
No separate `## the agent's Discretion` section exists in CONTEXT.md. The discretion items above are copied from `### Claude's Discretion`.

### Deferred Ideas (OUT OF SCOPE)
## Deferred Ideas

- Markdown field schema, missing-field markers, and teacher-editable source contract belong to Phase 38.
- Markdown-to-Typst conversion, deterministic generated-vs-reference verification, and non-zero missing-field failures belong to Phase 39.
- Canonical `SKILL.md`, runtime adapter notes, clean output/diagnostic boundary, and final missing-information question list belong to Phase 40.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TKD-TYP-01 | The `调课单` skill includes a hand-authored Typst reference file that captures the accepted adjustment-form layout before automation. | Use a skill-local reference fixture under `skills/tiaokedan/templates/`, not generated Typst. |
| TKD-TYP-02 | The Typst reference records the required visible fields, labels, table structure, signature/approval areas, and typography decisions needed for PDF output. | Field/table/signature checks are explicit verification items; no approval grid is added unless later required. |
| TKD-TYP-03 | The Typst reference can be compiled to a non-empty PDF with the repository's local Typst workflow when required fonts and tools are available. | Compile with local `typst compile`; record PDF size on success or exact stderr/blocker on failure. |
</phase_requirements>

## Summary

Phase 37 is a baseline-capture phase, not an automation phase. The planner should create the `skills/tiaokedan/` ownership boundary and a hand-authored Typst reference form that captures the accepted A4 landscape `调课单` surface before any Markdown contract or renderer exists. [VERIFIED: .planning/phases/37-typst-baseline/37-CONTEXT.md] The key planning risk is scope creep: a complete `SKILL.md`, runtime adapter notes, Markdown schema, script CLI, generated-vs-reference diffing, and final PDF gate are explicitly deferred to Phases 38-40. [VERIFIED: .planning/phases/37-typst-baseline/37-CONTEXT.md]

Local implementation can rely on Typst primitives already used in this repository: page setup, font fallback lists, paragraph settings, table cells, and optional PDF compilation. Existing document skills prove the repo pattern of skill-local templates/scripts, no sibling runtime dependency, and honest PDF status only after non-empty compiled artifacts exist. [VERIFIED: codebase grep] Current local environment has `typst 0.15.0` at `/opt/homebrew/bin/typst`, and `typst fonts` lists `SimSun`, `NSimSun`, `Songti SC`, `STSong`, `FangSong`, `FangSong_GB2312`, and `STFangsong`. [VERIFIED: local CLI]

**Primary recommendation:** implement the smallest reviewable baseline: `skills/tiaokedan/templates/tiaokedan-reference.typ`, optional compiled `tiaokedan-reference.pdf` or compile-blocker text, and phase verification evidence; avoid renderer/SKILL entry work until later phases.

## Phase Boundary and Non-Goals

| In Scope | Out of Scope |
|----------|--------------|
| Create `skills/tiaokedan/` scaffold directories as needed. [VERIFIED: AGENTS.md] | Do not implement Markdown field schema or teacher-editable Markdown fixture. [VERIFIED: .planning/phases/37-typst-baseline/37-CONTEXT.md] |
| Hand-author one Typst reference fixture for the locked visible form. [VERIFIED: .planning/REQUIREMENTS.md] | Do not implement Markdown-to-Typst renderer, parser, CLI, deterministic generated-vs-reference verification, or missing-field failures. [VERIFIED: .planning/REQUIREMENTS.md] |
| Compile to non-empty PDF if local Typst dependencies work; otherwise record exact blocker. [VERIFIED: .planning/ROADMAP.md] | Do not write complete canonical `SKILL.md`, runtime adapter notes, final PDF workflow, README/index discoverability, or missing-information question guide. [VERIFIED: .planning/phases/37-typst-baseline/37-CONTEXT.md] |
| Record evidence that visible fields, table, typography intent, and signature match locked decisions. [VERIFIED: .planning/phases/37-typst-baseline/37-CONTEXT.md] | Do not add approval/signature grids beyond the provided closing signature. [VERIFIED: .planning/phases/37-typst-baseline/37-DISCUSSION-LOG.md] |

## Project Constraints (from AGENTS.md)

- Always respond in Simplified Chinese unless a file format requires another language. [VERIFIED: AGENTS.md]
- Keep documents/templates concise, copyable, and reviewable. [VERIFIED: AGENTS.md]
- Do not put one agent's private syntax into canonical skill content; runtime differences belong in adapter notes. [VERIFIED: AGENTS.md]
- New skills default to `skills/<skill-name>/SKILL.md`, but Phase 37 should not complete the skill entry because that is Phase 40 scope. [VERIFIED: AGENTS.md] [VERIFIED: .planning/phases/37-typst-baseline/37-CONTEXT.md]
- Templates belong under `templates/`; examples and templates must not be mixed. [VERIFIED: AGENTS.md]
- If adding runtime support later, update `docs/compatibility-matrix.md`; Phase 37 should not do that unless scope is explicitly widened. [VERIFIED: AGENTS.md] [VERIFIED: .planning/phases/37-typst-baseline/37-CONTEXT.md]
- Skills involving external commands or file writes must state safety boundaries and verification steps; Phase 37 verification should capture the exact Typst compile command and result. [VERIFIED: AGENTS.md]
- OpenClaw and Hermes Agent must be considered later, but Phase 37 should avoid runtime adapter notes except minimal placeholders if absolutely needed. [VERIFIED: AGENTS.md] [VERIFIED: .planning/phases/37-typst-baseline/37-CONTEXT.md]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Hand-authored form baseline | Static skill template | Planning evidence | The accepted target is a committed Typst fixture, not runtime-generated output. |
| PDF compile proof | Local CLI/tooling | Phase verification docs | Typst compilation is an environment-dependent verification step; source remains the `.typ` fixture. |
| Typography/layout decisions | Typst document layer | Phase context | Fonts, table widths, line breaks, and signature placement are rendered in Typst from locked visual decisions. |
| Future Markdown/renderer workflow | Deferred skill runtime | — | Phase 38-40 own Markdown contract, parser, script command, PDF gate, and adapter notes. |

## Existing Repo Patterns Relevant to Planning

| Pattern | Evidence | Phase 37 Application |
|---------|----------|----------------------|
| Skill-local ownership | New skills live under `skills/<skill-name>/`; long rules in `references/`, scripts in `scripts/`, templates in `templates/`. [VERIFIED: docs/directory-spec.md] | Put the Typst baseline in `skills/tiaokedan/templates/`; create `references/` or `scripts/` only if the plan has a concrete Phase 37 use. |
| Compact entry, detailed support files | `gongwen` keeps workflow in `SKILL.md` and long rendering rules in `references/`. [VERIFIED: skills/gongwen/SKILL.md] | Do not author a full entry yet; if a placeholder is unavoidable, keep it minimal and mark Phase 40 ownership. |
| Optional PDF compile via Typst | `gongwen.sh` only compiles PDF when `--pdf` is provided and requires installed Typst. [VERIFIED: skills/gongwen/scripts/gongwen_lib/commands.sh] | Phase 37 can compile the hand-authored `.typ` directly; PDF success is optional but must be real and non-empty. |
| Honest compile status | `end-of-term` returns `skipped` when Typst is missing and captures stderr on failure. [VERIFIED: skills/end-of-term-teaching-materials/scripts/end_of_term/_engine.py] | Verification should record `compiled`, `failed`, or `skipped` with exact command/stderr, not infer readiness from `.typ` existence. |
| Non-empty PDF gate | `teaching-design-package` checks generated PDFs exist and `size > 0` before marking module/merge status passed. [VERIFIED: skills/teaching-design-package/scripts/teaching-design-package.sh] | If PDF compiles, record byte size and fail verification if size is 0. |
| Font fallback by type | `gongwen` defines separate fallback lists for 仿宋 and 宋体. [VERIFIED: skills/gongwen/scripts/gongwen_lib/typst_head.sh] | Use separate `FONT_SONG` and `FONT_FS` lists; do not mix 黑体/sans into 宋体/仿宋 fallback. |

## Recommended Target File Layout for Phase 37 Only

```text
skills/tiaokedan/
└── templates/
    ├── tiaokedan-reference.typ       # hand-authored accepted Typst baseline
    └── tiaokedan-reference.pdf       # optional; include only if local compile succeeds and repo policy accepts generated evidence

.planning/phases/37-typst-baseline/
├── 37-RESEARCH.md
└── 37-VERIFICATION.md               # later execution evidence: paths, checks, compile command, PDF size or blocker
```

Avoid creating `skills/tiaokedan/scripts/` in Phase 37 unless the plan needs a tiny verification helper; the renderer is Phase 39. Avoid creating a complete `skills/tiaokedan/SKILL.md`; the canonical entry is Phase 40. [VERIFIED: .planning/phases/37-typst-baseline/37-CONTEXT.md]

## Standard Stack

### Core

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Typst CLI | `0.15.0` locally | Compile `.typ` to PDF for baseline evidence | Existing repo document skills use `typst compile` for PDF proof. [VERIFIED: local CLI] [VERIFIED: codebase grep] |
| Typst source file | N/A | Hand-authored A4 landscape reference fixture | Phase 37 requires target surface before automation. [VERIFIED: .planning/REQUIREMENTS.md] |

### Supporting

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `rg` | local CLI available by repo convention | Verify locked strings and file layout | Use for content checks in verification. [VERIFIED: developer instructions] |
| `wc -c` / file stat | system tool | Verify PDF is non-empty | Use after successful Typst compile. [VERIFIED: codebase grep] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Hand-authored Typst | Markdown-to-Typst script | Out of scope until Phase 39; would undermine the accepted baseline. |
| Direct PDF-only artifact | Typst source plus optional PDF | PDF alone is not reviewable enough for future deterministic renderer work. |
| Sibling skill script reuse | `gongwen.sh` or `teaching-design-package.sh` | Explicitly forbidden as runtime dependency for `tiaokedan`; use as implementation inspiration only. |

**Installation:** No package install is required for Phase 37.

## Package Legitimacy Audit

No external packages should be installed in Phase 37. `ctx7` was not installed locally, so Context7 CLI fallback could not be used; Typst claims are based on official Typst docs and local CLI help instead. [VERIFIED: local CLI] [CITED: https://typst.app/docs/]

## Typst Implementation Considerations

| Concern | Recommendation |
|---------|----------------|
| A4 landscape | Use Typst page setup with A4 dimensions and landscape orientation, preferably `#set page(paper: "a4", flipped: true, margin: auto/default)` or explicit A4 landscape dimensions if default margin behavior needs visual control. Typst page supports `paper`, `flipped`, and `margin`. [CITED: https://typst.app/docs/reference/layout/page/] |
| Chinese font fallback | Define `FONT_SONG = ("SimSun", "NSimSun", "Songti SC", "STSong")` and `FONT_FS = ("FangSong", "STFangsong", "FangSong_GB2312", "Fangsong SC")`; this matches existing same-font-family fallback practice. [VERIFIED: skills/gongwen/scripts/gongwen_lib/typst_head.sh] Local fonts include SimSun/FangSong candidates. [VERIFIED: local CLI] |
| 二号/四号 mapping | Use `22pt` for 二号 and `14pt` for 四号 unless the planner chooses the repo's `@preview/pointless-size` `zh(2)`/`zh(4)` pattern. The point mapping is conventional Chinese print typography and should be treated as `[ASSUMED]` unless implementation verifies through a local package or typography reference. |
| Title | `调课说明` should be centered,宋体 fallback, `22pt`, bold. Existing Typst examples use `#align(center)[#text(...)]`. [VERIFIED: codebase grep] |
| Body paragraphs | Use 仿宋 fallback, `14pt`, paragraph justification, and first-line indent only on the explanatory paragraph. Typst paragraph settings include `justify` and `first-line-indent`. [CITED: https://typst.app/docs/reference/model/par/] |
| Distributed alignment | Typst `justify: true` gives paragraph justification; exact Chinese "分散对齐" for short lines may not be visually identical to word-processor distributed alignment. For Phase 37, use justified paragraph settings for normal paragraph text and, if short-label distribution is needed, use a small helper based on fixed-width `box/grid` spacing. [CITED: https://typst.app/docs/reference/model/par/] [ASSUMED] |
| Table full width | Use `#table(columns: (...), width: 100%)` or explicit column widths summing to the text block width. Typst table supports `columns`, `rows`, `stroke`, `inset`, and cell-level alignment. [CITED: https://typst.app/docs/reference/model/table/] |
| 8-column widths | Give more width to course and time columns. Start with approximate proportions: `0.9cm, 2.2cm, 4.4cm, 4.2cm, 1.7cm, 4.4cm, 1.9cm, 1.2cm`, then adjust against A4 landscape text block. [ASSUMED] |
| Table cells | Define helpers like `#let c(body) = table.cell(align: center + horizon, inset: 3pt)[#set par(first-line-indent: 0pt, justify: false) #body]`. The `center + horizon` pattern is already used in repository Typst renderers. [VERIFIED: codebase grep] |
| Row line breaks | Preserve row 1 time-cell line breaks with explicit `#linebreak(justify: false)` or separate stacked lines inside the cell; Typst has a `linebreak` function. [CITED: https://typst.app/docs/reference/text/linebreak/] |
| Signature placement | Put a vertical blank after the table, then right-align a fixed-width block containing `电气工程系` and `2026年6月21日`; use 仿宋四号. Do not add approval grids. [VERIFIED: .planning/phases/37-typst-baseline/37-CONTEXT.md] |
| Compile root | Compile from repo root or pass a stable root if assets are later introduced. Phase 37 should avoid assets, so plain `typst compile skills/tiaokedan/templates/tiaokedan-reference.typ <pdf>` is enough. [VERIFIED: local CLI help] |

## Architecture Patterns

### System Architecture Diagram

```text
Locked Phase 37 decisions
  -> hand-authored Typst reference fixture
  -> verification checks:
       - file/path exists
       - locked Chinese strings present
       - table headers and row facts present
       - typography/layout declarations present
       - no Markdown/schema/renderer scope creep
  -> optional Typst compile
       -> if success: record non-empty PDF path and byte size
       -> if failure/missing tool: record exact blocker/stderr
```

### Recommended Project Structure

```text
skills/
└── tiaokedan/
    └── templates/
        └── tiaokedan-reference.typ
```

### Pattern 1: Skill-Local Reference Fixture

**What:** Store the accepted `.typ` target inside the owning skill directory, not under another skill or global template folder.

**When to use:** Phase 37 establishes the future renderer target before Phase 38/39 build Markdown and conversion.

**Example:**

```typst
// Source: https://typst.app/docs/reference/layout/page/
#set page(paper: "a4", flipped: true)
#set text(lang: "zh", font: ("FangSong", "STFangsong"), size: 14pt)
```

### Pattern 2: Compile Evidence Is Separate From Source Truth

**What:** The `.typ` fixture is source truth; PDF is proof if it compiles locally.

**When to use:** Any environment-dependent PDF run.

**Example:**

```bash
typst compile skills/tiaokedan/templates/tiaokedan-reference.typ /tmp/tiaokedan-reference.pdf
wc -c /tmp/tiaokedan-reference.pdf
```

### Anti-Patterns to Avoid

- **Renderer-first implementation:** Do not parse Markdown or generate Typst in Phase 37; it destroys the intended accepted-target-first order.
- **Sibling script dependency:** Do not call `skills/gongwen/scripts/gongwen.sh` or `skills/teaching-design-package/scripts/teaching-design-package.sh`; borrow patterns only.
- **False PDF readiness:** Do not mark PDF complete because a `.typ` exists; require actual compile result and non-empty PDF.
- **Adding fields not requested:** Do not add approval columns, signature grids, or opinion areas beyond the locked closing signature.
- **Runtime adapter churn:** Do not update compatibility docs or six-runtime notes in Phase 37 unless the plan explicitly scopes a placeholder.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PDF compilation | Custom PDF writer or manual PDF bytes | Typst CLI `typst compile` | Existing repo workflow uses Typst; custom PDF output is unnecessary and risky. |
| Font discovery | Hardcoded local font path scanner | Typst font fallback lists and `typst fonts` verification | Typst already resolves installed fonts; repo already uses fallback lists. |
| Markdown parsing | Ad hoc parser or schema | Nothing in Phase 37 | Markdown contract is Phase 38; renderer is Phase 39. |
| Layout proof | Screenshot-only subjective check | String/layout declaration checks plus compile result | Planner needs deterministic evidence even if visual review happens later. |

**Key insight:** Phase 37 should make the future renderer target stable; every extra automation layer added now increases the chance that later phases chase the wrong baseline.

## Common Pitfalls

### Pitfall 1: Phase Creep Into Complete Skill
**What goes wrong:** Planner adds `SKILL.md`, runtime adapter notes, scripts, Markdown fixture, or README updates.
**Why it happens:** New skill scaffold normally includes all directories and entry docs.
**How to avoid:** Treat Phase 37 as an accepted target fixture phase only.
**Warning signs:** New `scripts/tiaokedan.sh`, Markdown schema docs, or six-runtime tables appear in the plan.

### Pitfall 2: Typography Name vs Installed Font Mismatch
**What goes wrong:** Typst compiles with fallback fonts that do not visually match 宋体/仿宋.
**Why it happens:** Font family names differ across macOS/Windows/Linux.
**How to avoid:** Use ordered fallback tuples and record `typst fonts` evidence. Current local machine has SimSun and FangSong candidates. [VERIFIED: local CLI]
**Warning signs:** Compile warnings about missing fonts or visibly sans-serif output.

### Pitfall 3: Distributed Alignment Overclaim
**What goes wrong:** Research/verification claims exact word-processor distributed alignment when Typst only used paragraph justification.
**Why it happens:** Chinese "分散对齐" can mean several visual behaviors.
**How to avoid:** Record the implementation as `justify: true` plus visual review; only add fixed-width spacing helpers if a short line needs distribution.
**Warning signs:** `教务处：` or signature gets stretched awkwardly.

### Pitfall 4: Table Overflow on A4 Landscape
**What goes wrong:** 8 columns overflow, wrap too aggressively, or compress names/time ranges.
**Why it happens:** Time columns and course title need most of the available width.
**How to avoid:** Allocate explicit widths, keep time line breaks in row 1, and verify the PDF compiles without layout spill.
**Warning signs:** Row 1 time line break missing, table extends past page body, or `备注` consumes too much width.

### Pitfall 5: Generated PDF Committed Without Source Evidence
**What goes wrong:** A PDF exists but planner/verifier cannot prove it matches locked content.
**Why it happens:** Binary artifacts are hard to review.
**How to avoid:** Verify `.typ` contains locked strings, headers, row facts, font declarations, page orientation, and signature; record PDF byte size as compile evidence only.
**Warning signs:** Verification only says "PDF generated."

## Code Examples

Verified patterns from official/local sources:

### A4 Landscape Page Setup

```typst
// Source: https://typst.app/docs/reference/layout/page/
#set page(paper: "a4", flipped: true)
```

### Font Fallback and Paragraph Style

```typst
// Source: skills/gongwen/scripts/gongwen_lib/typst_head.sh and Typst text/par docs
#let FONT_SONG = ("SimSun", "NSimSun", "Songti SC", "STSong")
#let FONT_FS = ("FangSong", "STFangsong", "FangSong_GB2312", "Fangsong SC")
#set text(lang: "zh", font: FONT_FS, size: 14pt)
#set par(justify: true, first-line-indent: (amount: 2em, all: true))
```

### Centered Table Cell

```typst
// Source: https://typst.app/docs/reference/model/table/ and local teaching renderers
#let cell(body) = table.cell(align: center + horizon, inset: 3pt)[
  #set par(first-line-indent: 0pt, justify: false)
  #body
]
```

### Explicit Line Break in Time Cell

```typst
// Source: https://typst.app/docs/reference/text/linebreak/
2026年3月11日#linebreak(justify: false)14:00-19:00（D104）
```

## Verification Strategy

| Check | Method | Pass Condition |
|-------|--------|----------------|
| Scaffold exists | `test -d skills/tiaokedan/templates` | Directory exists; no unnecessary renderer directories unless justified. |
| Reference file exists | `test -s skills/tiaokedan/templates/tiaokedan-reference.typ` | File exists and is non-empty. |
| Locked title/body/signature | `rg -F` for `调课说明`, `教务处：`, locked paragraph, `电气工程系`, `2026年6月21日` | All strings found in `.typ`. |
| Table structure | `rg -F` for 8 headers and row facts including teacher names, class, course, room/time strings | All required headers and rows present; row 1 preserves explicit line break in both time cells. |
| Typography declarations | `rg` for `SimSun|Songti|STSong`, `FangSong|STFangsong`, `22pt|zh\\(2\\)`, `14pt|zh\\(4\\)`, `justify`, `first-line-indent`, `center + horizon` | Typst records page/font/table intent. |
| Scope boundary | `find skills/tiaokedan -maxdepth 2 -type f` plus `rg` for Markdown/renderer terms if files exist | No Phase 38-40 artifacts are introduced. |
| Typst compile | `typst compile skills/tiaokedan/templates/tiaokedan-reference.typ /tmp/tiaokedan-reference.pdf 2>/tmp/tiaokedan-typst.stderr` | If Typst/fonts work: command exits 0 and PDF exists with byte size > 0. |
| Exact blocker | Capture `command -v typst`, `typst --version`, stderr, missing font/tool notes | If compile fails or tool missing: verification records the exact blocker and does not claim PDF success. |

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Typst CLI | Optional PDF compile for TKD-TYP-03 | Yes | `typst 0.15.0` at `/opt/homebrew/bin/typst` | If missing/failing in another environment, record exact blocker and keep `.typ` baseline. |
| Chinese fonts | Visual fidelity for 宋体/仿宋 | Yes locally | SimSun, NSimSun, Songti SC, STSong, FangSong, FangSong_GB2312, STFangsong visible in `typst fonts` | Use fallback tuples; record compile/font warning if absent elsewhere. |
| Context7 CLI | Documentation lookup fallback | No | `ctx7` not found | Used official Typst docs directly. |

**Missing dependencies with no fallback:** None for planning; PDF compilation can be blocked and recorded per roadmap.

**Missing dependencies with fallback:**
- Context7 CLI missing; official Typst docs and local CLI help provide sufficient Phase 37 evidence.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Planner overbuilds complete skill | Phase 37 becomes unreviewable and conflicts with Phase 38-40 | Plan only Typst fixture, optional PDF/blocker evidence, and verification. |
| PDF compiles with wrong visual font | Baseline may not match Chinese official-document intent | Use font fallback by family and record `typst fonts`; keep PDF visual review as execution evidence. |
| Table width needs adjustment | A4 landscape table may overflow or look cramped | Use explicit column widths, prioritize course/time columns, and preserve row 1 line breaks. |
| Ambiguity in `default page margins` | Different Typst defaults may not match expected official-form margins | Prefer Typst defaults first; if visual result is poor, planner can allow explicit margins while recording the reason. |
| Binary PDF evidence pollutes repo | Committed generated PDFs can bloat or drift | Planner should decide whether PDF belongs in `skills/tiaokedan/templates/` or only in phase verification/temp evidence; `.typ` is mandatory source truth. |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| One-step source-to-PDF document generation | Persistent Markdown intermediate before target rendering | v1.1 project decision | Phase 37 is the exception only because it establishes the target before Phase 38 Markdown contract. [VERIFIED: docs/markdown-normalization-contract.md] |
| Runtime dependency on sibling skills | Skill-local ownership and no sibling script calls | v1.14-v1.16 project decisions | `tiaokedan` may borrow patterns but must own future renderer code. [VERIFIED: .planning/PROJECT.md] |
| Treat generated Typst as enough for PDF readiness | Require real non-empty PDF evidence or exact blocker | Existing `teaching-design-package` and roadmap criteria | Verification must distinguish `.typ` existence from PDF success. [VERIFIED: codebase grep] |

**Deprecated/outdated:**
- Calling existing sibling renderers for a new document workflow: forbidden for `tiaokedan` runtime. [VERIFIED: .planning/REQUIREMENTS.md]
- Adding universal Markdown schema fields from the shared contract: the contract explicitly avoids universal metadata/schema. [VERIFIED: docs/markdown-normalization-contract.md]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | 二号 maps to `22pt` and 四号 maps to `14pt`. | Typst Implementation Considerations | Font sizes could be slightly off; planner should accept visual fidelity or verify against a typography reference/package. |
| A2 | `justify: true` is an acceptable Typst approximation for the requested Chinese distributed paragraph alignment. | Typst Implementation Considerations | Visual output may not match a word-processor's distributed alignment; execution may need a fixed-width helper for short lines. |
| A3 | The suggested 8-column width proportions will fit the accepted A4 landscape page body. | Typst Implementation Considerations | Implementation may need width tuning after first compile/visual review. |

## Open Questions (RESOLVED)

1. **Should the compiled PDF be committed or recorded only as phase evidence? — RESOLVED**
   - What we know: success criteria require non-empty PDF when dependencies are available.
   - What's unclear: repository policy for committing this specific generated PDF artifact is not explicitly stated.
   - Recommendation: plan PDF generation and byte-size evidence; commit the PDF only if the implementation plan treats it as the reference fixture, otherwise store evidence in phase verification.
   - Resolution: Phase 37 treats `skills/tiaokedan/templates/tiaokedan-reference.pdf` as optional compile evidence paired with the hand-authored `.typ` reference. If local Typst compilation succeeds and the PDF is non-empty, it may be kept under `skills/tiaokedan/templates/` and recorded with byte size in `37-VERIFICATION.md`; if compilation fails, no PDF success is claimed and the exact blocker is recorded.

2. **How exact must "distributed alignment" be? — RESOLVED**
   - What we know: locked decision requires 仿宋四号 distributed alignment for body paragraphs.
   - What's unclear: whether Typst paragraph justification alone is visually accepted.
   - Recommendation: start with `justify: true`; execution verification should include visual inspection and only add spacing helpers if required.
   - Resolution: Phase 37 baseline uses Typst paragraph justification (`justify: true`) as the accepted implementation of the requested body-paragraph distributed alignment unless the user later rejects the visual output. Short lines such as `教务处：` and the signature must not be stretched.

## Validation Architecture

Skipped: `.planning/config.json` sets `workflow.nyquist_validation` to `false`. [VERIFIED: .planning/config.json]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | No authentication surface in Phase 37. |
| V3 Session Management | no | No session state. |
| V4 Access Control | no | Local repo file changes only. |
| V5 Input Validation | yes | Verify locked strings and file scope; no untrusted runtime parser yet. |
| V6 Cryptography | no | No cryptographic operations. |

### Known Threat Patterns for This Phase

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Unreviewed external package install | Tampering | Install no packages; use local Typst CLI only. |
| Path confusion or sibling dependency | Tampering | Keep files under `skills/tiaokedan/`; do not call sibling scripts. |
| False artifact readiness | Repudiation | Record exact command, stderr/blocker, and PDF byte size if compiled. |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/37-typst-baseline/37-CONTEXT.md` - locked phase boundary, fields, typography, table rows, signature, non-goals.
- `.planning/REQUIREMENTS.md` - TKD-TYP-01/02/03 and future phase split.
- `.planning/ROADMAP.md` - Phase 37 goal and success criteria.
- `AGENTS.md` - language, directory, skill authoring, runtime constraints.
- `README.md` and `docs/directory-spec.md` - skill folder ownership and document workflow conventions.
- `docs/markdown-normalization-contract.md` - Markdown-first discipline and why Phase 37 is target-first only.
- `skills/gongwen/SKILL.md`, `skills/gongwen/scripts/gongwen.sh`, `skills/gongwen/scripts/gongwen_lib/*` - compact entry, font fallback, optional PDF compile pattern.
- `skills/teaching-design-package/scripts/teaching-design-package.sh` - non-empty PDF/status evidence pattern.
- `skills/end-of-term-teaching-materials/templates/typst/end-of-term-package.typ` and `scripts/end_of_term/_engine.py` - skill-local Typst template and compile blocker capture pattern.
- Local CLI probes: `typst --version`, `typst fonts`, `typst help compile`.

### Secondary (MEDIUM confidence)

- Typst official docs:
  - https://typst.app/docs/reference/layout/page/ - page paper/flipped/margin.
  - https://typst.app/docs/reference/model/table/ - table columns/cells/alignment.
  - https://typst.app/docs/reference/model/par/ - paragraph justification and first-line indent.
  - https://typst.app/docs/reference/text/text/ - text font/size/weight.
  - https://typst.app/docs/reference/text/linebreak/ - explicit line breaks.

### Tertiary (LOW confidence)

- Conventional Chinese字号 to point mapping: 二号≈22pt, 四号≈14pt. Marked `[ASSUMED]` pending implementation confirmation.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no new packages; local Typst 0.15.0 and repo patterns verified.
- Architecture: HIGH - phase boundary and non-goals are locked in CONTEXT/ROADMAP/REQUIREMENTS.
- Typst layout details: MEDIUM - Typst capabilities verified, but exact distributed alignment and column widths need visual tuning.
- Pitfalls: HIGH - derived from explicit phase boundaries and recent repo document workflow patterns.

**Research date:** 2026-06-21
**Valid until:** 2026-07-21 for repo phase planning; re-check Typst version/fonts if executed on another machine.
