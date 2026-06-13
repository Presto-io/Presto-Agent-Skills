# Requirements: v1.11 Integrated Teaching Design Package

**Defined:** 2026-06-14
**Core Value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## Milestone Summary

Create a new orchestration-skill milestone for an integrated teaching-design package. The new skill should compose the existing `jiaoan-jihua`, `jiaoan-shicao`, and optional `end-of-term-teaching-materials` workflows without deleting or replacing those original skills.

The package workflow should be Markdown-first: generate a teacher-reviewable Markdown intermediate, then render Typst/PDF outputs and supporting artifacts. Scheduling should be promoted from the existing `jiaoan-jihua` local behavior into a shared package-level contract so hand-filled start/end dates can be inferred from auditable inputs.

## Gate Record

- **Validation gate:** v1.10 is archived, `.planning/STATE.md` now tracks v1.11 planning, and active phase numbering continues from Phase 22.
- **Questioning gate:** The user supplied the milestone name, goals, initial research conclusion, read targets, write scope, phase split, and non-deletion constraint, so no additional user prompt is required.
- **Research gate:** Local research is sufficient for milestone initialization. `jiaoan-jihua` already derives scheduling cells from `calendar.json`, `first_teaching_day`, `daily_hours`, and per-row hours; `end-of-term-teaching-materials` already defines deterministic package artifacts and workbook/PDF gates.
- **Requirements gate:** Requirements are scoped to planning a new integrated package skill and future phase execution; this initialization does not create the actual skill implementation.
- **Roadmap approval gate:** The user supplied a preferred 3-4 phase split; this roadmap uses four phases, Phase 22 through Phase 25.

## v1.11 Requirements

### Shared Scheduling Contract

- [x] **TDP-01**: Define a package-level scheduling contract that accepts school calendar data, first teaching day, daily hours, task/activity/lesson-fragment hours, holidays, and makeup teaching days.
- [x] **TDP-02**: The scheduling contract must output start date, end date, term week number, weekday, assigned hours, and hour-consumption evidence for each teaching task, activity, and lesson-plan fragment.
- [x] **TDP-03**: The scheduling contract must preserve uncertain, missing, or conflicting schedule inputs as teacher-review markers instead of silently guessing or dropping them.
- [x] **TDP-04**: At least one fixture must prove that date ranges previously hand-filled in teaching-design documents can be derived from the scheduling contract.

### Integrated Teaching Plan and Lesson Plan Package

- [x] **TDP-05**: Add a new orchestration skill, preferably named `teaching-design-package` unless phase research identifies a better repository-consistent name.
- [x] **TDP-06**: Preserve `skills/jiaoan-jihua` and `skills/jiaoan-shicao` as standalone public skills; the new package skill must compose or reference them rather than delete, rename, or replace them.
- [x] **TDP-07**: The new package skill must define a persistent teacher-reviewable Markdown intermediate that includes teaching-plan sections, lesson-plan sections, scheduling evidence, and review markers before Typst/PDF generation.
- [x] **TDP-08**: The new package skill must plan Typst/PDF output for teaching-plan and lesson-plan content, including split outputs such as `teaching-plan.pdf` and `lesson-plans.pdf` where the renderer can support them.
- [x] **TDP-09**: The canonical skill body must remain portable and must keep runtime-specific behavior in adapter notes, with Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent represented.

### Optional End-of-Term Module

- [x] **TDP-10**: The package skill must support the end-of-term materials workflow as an optional module, reusing structured data, score calculation evidence, deterministic table artifacts, workbook output, manifest rules, and review gates from `end-of-term-teaching-materials`.
- [x] **TDP-11**: End-of-term package rendering must not bypass the existing `end-of-term-full.md` review point or the `## 复核标记` export gate.
- [x] **TDP-12**: The package output plan must include `end-of-term-package.pdf` when the optional module is enabled and must keep workbook/table artifacts discoverable from the package manifest.

### Combined Outputs and Verification

- [x] **TDP-13**: The default final package artifact must be a combined `teaching-design-package.pdf` when Typst/PDF tooling can merge the selected modules.
- [x] **TDP-14**: If split compilation or merged PDF generation is unavailable, the package must fail with explicit manifest/status evidence instead of claiming a complete final package.
- [ ] **TDP-15**: Regression verification must prove the existing `jiaoan-jihua`, `jiaoan-shicao`, and `end-of-term-teaching-materials` public command surfaces remain usable after package integration.
- [ ] **TDP-16**: Documentation/index verification must show the new skill is discoverable while preserving repository guidance: Markdown-first, lightweight `SKILL.md`, long rules in `references/`, scripts in `scripts/`, templates in `templates/`, and no agent-private syntax in canonical workflow text.

## Future Requirements

Deferred to a later milestone unless explicitly requested:

- **TDP-FUTURE-01**: Delete, rename, or physically merge the original `jiaoan-jihua`, `jiaoan-shicao`, or `end-of-term-teaching-materials` skill directories.
- **TDP-FUTURE-02**: Introduce a global shared scheduling library used by unrelated skills.
- **TDP-FUTURE-03**: Add hosted collaboration, cloud review, or online teacher approval workflow.
- **TDP-FUTURE-04**: Automatically infer arbitrary school templates, OCR handwritten schedules, or ingest uncontrolled spreadsheet formats.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Creating the actual new skill during milestone initialization | The user requested planning only; implementation belongs to later phases. |
| Deleting the existing jiaoan or end-of-term skills | The user explicitly said not to delete original skills. |
| One-step raw data to PDF without Markdown intermediate | This would violate the repository's Markdown-first review discipline. |
| Runtime-specific wrappers in the canonical skill body | Runtime differences belong in adapter notes to preserve portability. |
| External web research | The requested conclusions are supported by local repository artifacts and existing skills. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| TDP-01 | Phase 22 | Complete |
| TDP-02 | Phase 22 | Complete |
| TDP-03 | Phase 22 | Complete |
| TDP-04 | Phase 22 | Complete |
| TDP-05 | Phase 23 | Complete |
| TDP-06 | Phase 23 | Complete |
| TDP-07 | Phase 23 | Complete |
| TDP-08 | Phase 23 | Complete |
| TDP-09 | Phase 23, Phase 25 | Partially complete |
| TDP-10 | Phase 24 | Complete |
| TDP-11 | Phase 24 | Complete |
| TDP-12 | Phase 24 | Complete |
| TDP-13 | Phase 24 | Complete |
| TDP-14 | Phase 24, Phase 25 | Complete in Phase 24; Phase 25 verifies regression behavior |
| TDP-15 | Phase 25 | Planned |
| TDP-16 | Phase 25 | Planned |

**Coverage:**
- v1.11 requirements: 16 total
- Mapped to phases: 16
- Unmapped: 0

---
*Requirements defined: 2026-06-14*
