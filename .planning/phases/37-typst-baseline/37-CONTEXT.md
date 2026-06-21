# Phase 37: 调课单 Typst Baseline - Context

**Gathered:** 2026-06-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 37 delivers the accepted visual/form surface for the new `调课单` skill: create `skills/tiaokedan/` scaffold, hand-author a Typst reference fixture for the described A4 landscape adjustment form, and compile it to a non-empty PDF when local Typst dependencies are available. Markdown contract, Markdown-to-Typst automation, full skill entry, PDF delivery gates, and missing-information question guides remain Phase 38-40 scope.

</domain>

<decisions>
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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope
- `.planning/ROADMAP.md` — Phase 37 goal and success criteria.
- `.planning/REQUIREMENTS.md` — TKD-TYP-01, TKD-TYP-02, and TKD-TYP-03 requirements.
- `.planning/PROJECT.md` — v1.16 milestone purpose, constraints, and document-workflow discipline.

### Repository Contracts
- `AGENTS.md` — Simplified Chinese response rule and repository editing conventions.
- `README.md` — skill directory conventions and document workflow expectations.
- `docs/directory-spec.md` — ownership rules for `skills/<skill-name>/SKILL.md`, `references/`, `scripts/`, and `templates/`.
- `docs/markdown-normalization-contract.md` — project-wide Markdown-first discipline; Phase 37 creates the Typst target before Phase 38 creates the Markdown contract.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/gongwen/SKILL.md` and `skills/gongwen/scripts/gongwen.sh`: useful examples for a compact document-skill entry, Typst/PDF command surface, and optional reference comparison, but the new `tiaokedan` runtime must not call this script.
- `skills/teaching-design-package/scripts/teaching-design-package.sh`: includes a local `typst compile` pattern that records failure when Typst is unavailable and treats real PDFs as final evidence.
- `skills/end-of-term-teaching-materials/templates/typst/end-of-term-package.typ`: example of a skill-local Typst template, useful as layout inspiration only.

### Established Patterns
- New skills live under `skills/<skill-name>/` and keep long rules in `references/`, executable helpers in `scripts/`, and copyable or renderable scaffolds in `templates/`.
- PDF readiness is not inferred from Typst generation. A PDF is final only when explicitly compiled and non-empty; otherwise the exact blocker should be recorded.
- Existing teaching-document work keeps source-of-truth decisions visible and reviewable rather than hiding them in opaque renderer behavior.

### Integration Points
- Phase 37 should create the initial `skills/tiaokedan/` folder and a hand-authored Typst reference fixture that later Phase 38 and Phase 39 can target.
- Phase verification should record the Typst path, PDF path or precise compile blocker, and evidence that the visible fields/table/signature match this context.

</code_context>

<specifics>
## Specific Ideas

- The document should look like a concise official adjustment statement, not a multi-page report.
- The table is the central artifact and must span the available text block width in landscape orientation.
- Preserve the row-1 line break inside both time cells; row 2 may remain single-line in the provided example.
- The closing signature should read:

  `电气工程系`

  `2026年6月21日`

</specifics>

<deferred>
## Deferred Ideas

- Markdown field schema, missing-field markers, and teacher-editable source contract belong to Phase 38.
- Markdown-to-Typst conversion, deterministic generated-vs-reference verification, and non-zero missing-field failures belong to Phase 39.
- Canonical `SKILL.md`, runtime adapter notes, clean output/diagnostic boundary, and final missing-information question list belong to Phase 40.

</deferred>

---

*Phase: 37-调课单 Typst Baseline*
*Context gathered: 2026-06-21*
