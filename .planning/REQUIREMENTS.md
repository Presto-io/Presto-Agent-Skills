# Requirements: v1.12 Teaching Design Package Post-Close Repair

**Defined:** 2026-06-14
**Core Value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## Milestone Summary

Repair two post-close bugs found after v1.11 shipped, without deleting or replacing the original teaching skills.

The milestone is scoped to shipped behavior repair:

- `teaching-design-package` must backfill inferred `起止日期` values from package scheduling evidence into generated practical lesson-plan Markdown before handing off to `jiaoan-shicao`.
- `jiaoan-shicao` must align the `教学活动设计` table-width strategy with the official `presto-official-templates/jiaoan-shicao` behavior.

## Gate Record

- **Validation gate:** v1.11 is archived; current state frontmatter tracks v1.12 planning; active phase numbering continues from Phase 26.
- **Questioning gate:** The user supplied the two bug reports, official-template research evidence, scope boundaries, required regression verification, and staging/commit constraints, so no additional user prompt is required.
- **Research gate:** External web research is not required for milestone initialization. The official-reference evidence is already available locally in `/private/tmp/presto-jiaoan-shicao-main.go`, `/private/tmp/presto-jiaoan-shicao-main_test.go`, and `/private/tmp/presto-jiaoan-shicao-example.md`.
- **Requirements gate:** Requirements are scoped to planning a post-close bugfix milestone only; this command does not implement the fixes.
- **Roadmap approval gate:** The roadmap uses two focused phases, Phase 26 for package date backfill and Phase 27 for official activity-table width alignment.

## v1.12 Requirements

### Package Scheduling Backfill

- [ ] **TDPR-01**: `teaching-design-package` must propagate inferred scheduling evidence into generated `jiaoan-shicao-full.md` so missing practical lesson-plan `起止日期` fields are filled before `jiaoan-shicao` rendering.
- [ ] **TDPR-02**: Date backfill must remain teacher-reviewable: source scheduling inputs, derived date ranges, and uncertain/conflicting/missing-input review markers must stay visible in Markdown or adjacent evidence artifacts.
- [ ] **TDPR-03**: Package date backfill must preserve existing public command surfaces, accepted input contracts, output filenames, manifest semantics, and standalone availability for `teaching-design-package`, `jiaoan-jihua`, and `jiaoan-shicao`.

### Official Activity Table Width Alignment

- [ ] **TDPR-04**: `jiaoan-shicao` `教学活动设计` table-width behavior must be aligned with the official template algorithm around `tableColumnWidthsCM`, `sectionColumnSpecs`, `columnPressures`, and `activityTableTotalWidthCM`.
- [ ] **TDPR-05**: Activity-table verification must cover the official invariants: total width equals `activityTableTotalWidthCM`, the `课时分配` column stays narrower than main text columns, and multiple teaching-activity tables in the same chapter share identical column widths.

### Regression Verification

- [ ] **TDPR-06**: Regression verification must generate Markdown, Typst, and PDF artifacts for the affected package path, and must explicitly verify that generated `jiaoan-shicao-full.md` contains filled `起止日期` values.
- [ ] **TDPR-07**: Regression verification must generate Markdown, Typst, and PDF artifacts for the affected `jiaoan-shicao` path, and must record official-template width evidence or a clear local reproduction before claiming alignment.

## Future Requirements

Deferred to a later milestone unless explicitly requested:

- **TDPR-FUTURE-01**: Delete, rename, or physically merge the original `teaching-design-package`, `jiaoan-shicao`, `jiaoan-jihua`, or `end-of-term-teaching-materials` skill directories.
- **TDPR-FUTURE-02**: Introduce a new global shared scheduling library used by unrelated skills.
- **TDPR-FUTURE-03**: Replace the current Markdown-first review flow with one-step raw data to PDF generation.
- **TDPR-FUTURE-04**: Add arbitrary school-template discovery, OCR, hosted review, or cloud approval workflow.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Deleting or replacing original teaching skills | The user explicitly requested a v1.11 post-close repair that keeps existing skills. |
| New integrated teaching-design feature expansion | This milestone fixes two shipped-behavior bugs; new feature design belongs in a later milestone. |
| Runtime-specific canonical skill syntax | Canonical skill bodies must stay portable, with runtime differences in adapter notes. |
| External official-template re-research during initialization | The required official evidence has already been identified locally for this milestone. |
| Staging or committing generated `deliverables/` artifacts during initialization | The user explicitly limited this command to GSD planning files and said not to stage existing untracked `deliverables/`. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| TDPR-01 | Phase 26 | Pending |
| TDPR-02 | Phase 26 | Pending |
| TDPR-03 | Phase 26 | Pending |
| TDPR-04 | Phase 27 | Pending |
| TDPR-05 | Phase 27 | Pending |
| TDPR-06 | Phase 26, Phase 27 | Pending |
| TDPR-07 | Phase 27 | Pending |

**Coverage:**
- v1.12 requirements: 7 total
- Mapped to phases: 7
- Unmapped: 0

---
*Requirements defined: 2026-06-14*
*Last updated: 2026-06-14 after v1.12 milestone initialization*
