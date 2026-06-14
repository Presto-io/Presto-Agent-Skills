# Requirements: v1.13 Teaching Design Package Markdown Baseline Rendering

**Defined:** 2026-06-15
**Core Value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## Milestone Summary

Make `teaching-design-package` render from the committed full-package Markdown baseline without changing the teacher-facing reference format.

The baseline is:

- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- Last relevant commit observed during initialization: `28932fd Revise teaching design package markdown`

The milestone is scoped to planning renderer behavior and output parity. It must not implement code during milestone initialization, and later implementation must adapt the renderer around the Markdown rather than rewriting the Markdown reference structure.

## Gate Record

- **Validation gate:** v1.12 is archived; current state frontmatter tracks v1.13 planning; phase numbering continues from Phase 28.
- **Questioning gate:** The user supplied the corrected scope and acceptance rules directly, so no additional user prompt is required.
- **Research gate:** External research is not required for milestone initialization. The scope is internal to existing package and jiaoan renderer behavior.
- **Requirements gate:** Requirements are scoped to establishing a new milestone only; this command does not implement rendering changes.
- **Roadmap approval gate:** The roadmap uses two focused phases: Phase 28 for Markdown baseline ingestion and Typst generation, Phase 29 for PDF parity and standalone regression.

## v1.13 Requirements

### Markdown Baseline Contract

- [ ] **TDBR-01**: `teaching-design-package` must use `skills/teaching-design-package/templates/teaching-design-package-full.md` as the baseline package Markdown input for the integrated teaching-design package.
- [ ] **TDBR-02**: The teacher-facing Markdown structure and format of the baseline reference document must remain unchanged; implementation must adapt renderer parsing around that Markdown shape.
- [ ] **TDBR-03**: The package workflow must produce one Markdown artifact that can be directly copied from the reference document shape and used as the teacher-reviewable package checkpoint.

### Derived Hours, Dates, and Metadata Contract

- [ ] **TDBR-12**: Total course hours must be derived from all `活动名称-课时` rows under `# 授课进度计划`; package YAML must not retain or depend on `total_hours`. The current baseline must calculate to `160H`.
- [ ] **TDBR-13**: Each learning-task hour total must be derived from its own teaching-plan rows, not from lesson-plan frontmatter or manually repeated fields. The current baseline must calculate `CA6140=40H`, `X62W=60H`, and `Z3040=60H`.
- [ ] **TDBR-14**: Lesson-plan activity hours must be mapped from same-name or same-order activities in `# 授课进度计划`; generated `##### xH` lines may only be derived render handoff data, not a maintained human fact source. If a lesson activity cannot be mapped, the package must fail or emit a non-final/review-needed status instead of inventing hours.
- [ ] **TDBR-15**: Each `学习任务分析` date range must be inferred from `first_teaching_day`, the skill's built-in real teaching-day calendar text/resource, the default `8` hours per teaching day, and automatically parsed plan-row hours. Output format is `M月D日——M月D日`, with no year. For the current baseline, the expected ranges are `CA6140=5月11日——5月15日`, `X62W=5月18日——5月27日`, and `Z3040=5月27日——6月5日`.
- [ ] **TDBR-16**: `school_year` and `semester` must be inferred from `first_teaching_day` and must not be manually maintained in package YAML. Spring/first-half dates infer the previous-year/current-year academic year second semester; autumn/second-half dates infer the current-year/next-year academic year first semester. The current baseline `2026-05-11` must infer `2025-2026学年第二学期`.
- [ ] **TDBR-17**: Default rendering and scheduling contract values such as `hour_unit`, `daily_hours`, `date_display_format`, `date_locale`, `calendar_source`, `holidays`, `makeup_days`, `source_of_truth`, `outputs`, and `validation` must stay in script/skill contracts or generated evidence. They must not be reintroduced as teacher-maintained package YAML fields.

### Markdown-to-Typst Rendering

- [ ] **TDBR-04**: Package rendering must consume the baseline Markdown and generate one Typst artifact from that Markdown, with evidence that the Typst was produced through the render path rather than manually maintained as the source.
- [ ] **TDBR-05**: The renderer must preserve the semantic split between the授课进度计划 section and the教学设计方案 section while using the single Markdown baseline as the source of truth.

### PDF Outputs and Parity

- [ ] **TDBR-06**: The final workflow must generate three PDF artifacts: one combined package PDF, one teaching-plan PDF, and one lesson-plan PDF.
- [ ] **TDBR-07**: The combined package PDF must behave like the original授课进度计划 and教案 outputs merged into one PDF, without dropping either document's required content.
- [ ] **TDBR-08**: The teaching-plan PDF must match the content and format produced by standalone `jiaoan-jihua` for the same source scope, allowing only timestamp differences.
- [ ] **TDBR-09**: The lesson-plan PDF must match the content and format produced by standalone `jiaoan-shicao` for the same source scope, allowing only timestamp differences.

### Standalone Compatibility

- [ ] **TDBR-10**: `jiaoan-jihua` and `jiaoan-shicao` must remain standalone skills with stable public commands, accepted inputs, output paths, and documented contracts.
- [ ] **TDBR-11**: Package-level changes must not silently require callers of standalone `jiaoan-jihua` or `jiaoan-shicao` to adopt `teaching-design-package` input format or orchestration.

## Future Requirements

Deferred to a later milestone unless explicitly requested:

- **TDBR-FUTURE-01**: Redesign the teacher-facing Markdown reference format into a new schema.
- **TDBR-FUTURE-02**: Replace the original `jiaoan-jihua` or `jiaoan-shicao` skills with package-only entry points.
- **TDBR-FUTURE-03**: Add arbitrary external document import, OCR, hosted review, or cloud approval workflow.
- **TDBR-FUTURE-04**: Extend the package to unrelated document families outside授课进度计划 and教学设计方案.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Modifying the Markdown reference format to satisfy renderer internals | The user explicitly corrected scope so the teaching Markdown remains teacher-facing and implementation adapts around render ingestion. |
| Implementing code during milestone initialization | This command is limited to `/gsd:new-milestone`; implementation belongs to later phase plan/execute commands. |
| Deleting, renaming, or replacing `jiaoan-jihua` and `jiaoan-shicao` | The user explicitly required both old skills to remain standalone. |
| Treating split Typst success as final PDF success | Acceptance requires actual three-PDF output evidence. |
| Accepting approximate plan/lesson PDF formatting | The split PDFs must match old standalone skill outputs except allowed timestamp differences. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| TDBR-01 | Phase 28 | Pending |
| TDBR-02 | Phase 28 | Pending |
| TDBR-03 | Phase 28 | Pending |
| TDBR-04 | Phase 28 | Pending |
| TDBR-05 | Phase 28 | Pending |
| TDBR-06 | Phase 29 | Pending |
| TDBR-07 | Phase 29 | Pending |
| TDBR-08 | Phase 29 | Pending |
| TDBR-09 | Phase 29 | Pending |
| TDBR-10 | Phase 29 | Pending |
| TDBR-11 | Phase 29 | Pending |
| TDBR-12 | Phase 28, Phase 29 | Pending |
| TDBR-13 | Phase 28, Phase 29 | Pending |
| TDBR-14 | Phase 28, Phase 29 | Pending |
| TDBR-15 | Phase 28, Phase 29 | Pending |
| TDBR-16 | Phase 28, Phase 29 | Pending |
| TDBR-17 | Phase 28, Phase 29 | Pending |

**Coverage:**
- v1.13 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0

---
*Requirements defined: 2026-06-15*
*Last updated: 2026-06-15 after v1.13 milestone initialization*
