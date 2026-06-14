# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Last updated:** 2026-06-14 after Phase 26 execution closeout
**Granularity:** Coarse
**Project Mode:** MVP

## Milestones

- **Shipped: v1.0 MVP** - Phases 1-3, shipped 2026-05-30. Archives: `.planning/milestones/v1.0-ROADMAP.md`, `.planning/milestones/v1.0-REQUIREMENTS.md`
- **Shipped: v1.1 Document Workflow** - Phase 4, shipped 2026-05-31. Archives: `.planning/milestones/v1.1-ROADMAP.md`, `.planning/milestones/v1.1-REQUIREMENTS.md`
- **Shipped: v1.2 Gongwen Skill** - Phase 5, shipped 2026-05-31. Archives: `.planning/milestones/v1.2-ROADMAP.md`, `.planning/milestones/v1.2-REQUIREMENTS.md`
- **Shipped: v1.3 Jiaoan Shicao Skill** - Phase 6, shipped 2026-05-31. Archives: `.planning/milestones/v1.3-ROADMAP.md`, `.planning/milestones/v1.3-REQUIREMENTS.md`
- **Shipped: v1.4 Jiaoan Jihua Skill** - Phase 7, shipped 2026-05-31. Archives: `.planning/milestones/v1.4-ROADMAP.md`, `.planning/milestones/v1.4-REQUIREMENTS.md`
- **Shipped: v1.5 School Presentation Skill** - Phase 8, shipped 2026-06-01. Archives: `.planning/milestones/v1.5-ROADMAP.md`, `.planning/milestones/v1.5-REQUIREMENTS.md`
- **Shipped: v1.6 School Presentation Playback UX** - Phases 9-10, automated verification passed 2026-06-03; Phase 10 visual UAT passed 2026-06-11. Archives: `.planning/milestones/v1.6-ROADMAP.md`, `.planning/milestones/v1.6-REQUIREMENTS.md`, `.planning/milestones/v1.6-MILESTONE-AUDIT.md`
- **Shipped: v1.7 End-of-Term Teaching Materials Skill** - Phases 11-13, shipped 2026-06-10. Archives: `.planning/milestones/v1.7-ROADMAP.md`, `.planning/milestones/v1.7-REQUIREMENTS.md`, `.planning/milestones/v1.7-MILESTONE-AUDIT.md`
- **Shipped: v1.8 School Presentation Continuation** - Phases 14-16, shipped 2026-06-11. Archives: `.planning/milestones/v1.8-ROADMAP.md`, `.planning/milestones/v1.8-REQUIREMENTS.md`, `.planning/milestones/v1.8-MILESTONE-AUDIT.md`
- **Shipped: v1.9 Skill Decomposition and Entry Slimming** - Phases 17-19, shipped 2026-06-13. Archives: `.planning/milestones/v1.9-ROADMAP.md`, `.planning/milestones/v1.9-REQUIREMENTS.md`, `.planning/milestones/v1.9-MILESTONE-AUDIT.md`
- **Shipped: v1.10 Jiaoan Typst 1:1 Conversion** - Phases 20-21, shipped 2026-06-13. Archives: `.planning/milestones/v1.10-ROADMAP.md`, `.planning/milestones/v1.10-REQUIREMENTS.md`, `.planning/milestones/v1.10-MILESTONE-AUDIT.md`
- **Shipped: v1.11 Integrated Teaching Design Package** - Phases 22-25, shipped 2026-06-14. Archives: `.planning/milestones/v1.11-ROADMAP.md`, `.planning/milestones/v1.11-REQUIREMENTS.md`, `.planning/milestones/v1.11-MILESTONE-AUDIT.md`

## Active Milestone

**v1.12 Teaching Design Package Post-Close Repair**

This is a v1.11 post-close bugfix milestone. It keeps the original `teaching-design-package`, `jiaoan-shicao`, `jiaoan-jihua`, and `end-of-term-teaching-materials` skills intact, and scopes work to two reported regressions:

- `teaching-design-package` derives scheduling evidence but fails to backfill inferred `起止日期` into generated practical lesson-plan Markdown (`jiaoan-shicao-full.md`).
- `jiaoan-shicao` `教学活动设计` table widths need to match the official `presto-official-templates/jiaoan-shicao` behavior, using the local official-reference snapshots in `/private/tmp/presto-jiaoan-shicao-main.go`, `/private/tmp/presto-jiaoan-shicao-main_test.go`, and `/private/tmp/presto-jiaoan-shicao-example.md`.

## Phases

### Phase 26: Package Date Backfill Repair

**Goal:** Repair `teaching-design-package` so inferred scheduling evidence is written into the generated practical lesson-plan Markdown before `jiaoan-shicao` rendering.
**Depends on:** Phase 25
**Plans:** 1 plan
**Requirements:** TDPR-01, TDPR-02, TDPR-03, TDPR-06
**Status:** Complete
**Completed:** 2026-06-14

Success criteria:

1. Package generation produces `jiaoan-shicao-full.md` with concrete `起止日期` values derived from package scheduling evidence when source lesson-plan dates are missing.
2. The generated Markdown still preserves teacher-reviewable scheduling evidence and review markers for uncertain, conflicting, or incomplete scheduling inputs.
3. Public command surfaces for `teaching-design-package`, `jiaoan-jihua`, and `jiaoan-shicao` remain stable.
4. Regression verification generates Markdown, Typst, and PDF evidence for the affected package path and explicitly checks that `起止日期` is filled.

### Phase 27: Official Activity Table Width Alignment

**Goal:** Repair `jiaoan-shicao` `教学活动设计` table-width behavior using the official template algorithm and regression tests as evidence.
**Depends on:** Phase 26
**Plans:** 1 plan
**Requirements:** TDPR-04, TDPR-05, TDPR-06, TDPR-07
**Status:** Pending

Success criteria:

1. The `教学活动设计` width strategy is aligned with official-template behavior around `tableColumnWidthsCM`, `sectionColumnSpecs`, `columnPressures`, and `activityTableTotalWidthCM`.
2. Verification proves total activity-table width matches the official total, the `课时分配` column remains narrower than main text columns, and multiple activity tables in the same chapter share one column specification.
3. Regression verification generates Markdown, Typst, and PDF outputs for `jiaoan-shicao` and the integrated package path.
4. Phase evidence records the official-template basis or a clear local reproduction of it before claiming alignment.

## Completed Phase Archive

Detailed phase goals, requirements, success criteria, and verification evidence are preserved in the milestone archives and phase summary files.

| Phase | Milestone | Status | Completed |
|-------|-----------|--------|-----------|
| 1. Repository and GSD Foundation | v1.0 | Complete | 2026-05-30 |
| 2. Canonical Skill Format and Runtime Notes | v1.0 | Complete | 2026-05-30 |
| 3. Portable Example Scope Reconciliation | v1.0 | Complete | 2026-05-30 |
| 4. Markdown Normalization Contract | v1.1 | Complete | 2026-05-31 |
| 5. Gongwen Skill | v1.2 | Complete | 2026-05-31 |
| 6. Jiaoan Shicao Skill | v1.3 | Complete | 2026-05-31 |
| 7. Jiaoan Jihua Skill | v1.4 | Complete | 2026-05-31 |
| 8. School Presentation Skill | v1.5 | Complete | 2026-06-01 |
| 9. Playback Workspace and Page Hierarchy | v1.6 | Complete | 2026-06-01 |
| 10. Ordered Reveals and Classroom Answer Masks | v1.6 | Complete | 2026-06-03 |
| 11. End-of-Term Data and Markdown Contract | v1.7 | Complete | 2026-06-09 |
| 12. Fixed-Template Rendering and Verification | v1.7 | Complete | 2026-06-09 |
| 13. Close gap: uncertain scores reach Markdown review | v1.7 | Complete | 2026-06-10 |
| 14. Presenter Markup Tools | v1.8 | Complete | 2026-06-11 |
| 15. Classroom Interaction and Structured Layout Extensions | v1.8 | Complete | 2026-06-11 |
| 16. Print Export Review and v1.8 Regression Gate | v1.8 | Complete | 2026-06-11 |
| 17. Skill Entry and Reference Decomposition | v1.9 | Complete | 2026-06-13 |
| 18. Script Module Decomposition | v1.9 | Complete | 2026-06-13 |
| 19. Decomposition Guidance and Milestone Review | v1.9 | Complete | 2026-06-13 |
| 20. Jiaoan Shicao 教案 1:1 Typst Conversion | v1.10 | Complete | 2026-06-13 |
| 21. Jiaoan Jihua 授课计划 1:1 Typst Conversion | v1.10 | Complete | 2026-06-13 |
| 22. Scheduling Contract and Fixture | v1.11 | Complete | 2026-06-13 |
| 23. Integrated Skill Entry and Jiaoan Orchestration | v1.11 | Complete | 2026-06-13 |
| 24. Optional End-of-Term Module and Package Outputs | v1.11 | Complete | 2026-06-14 |
| 25. Regression Verification and Documentation Index | v1.11 | Complete | 2026-06-14 |
| 26. Package Date Backfill Repair | v1.12 | Complete | 2026-06-14 |

## Current Position

Phase 26 is complete. Phase 27 is next and remains unplanned.

## Next Step

Run `/gsd:discuss-phase 27` to gather implementation context for the official activity-table width alignment repair.

---
*Roadmap updated: 2026-06-14 after Phase 26 execution closeout*
