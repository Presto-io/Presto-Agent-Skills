# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Last updated:** 2026-06-15 after v1.13 milestone initialization
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
- **Shipped: v1.12 Teaching Design Package Post-Close Repair** - Phases 26-27, shipped 2026-06-14. Archives: `.planning/milestones/v1.12-ROADMAP.md`, `.planning/milestones/v1.12-REQUIREMENTS.md`, `.planning/milestones/v1.12-MILESTONE-AUDIT.md`

## Active Milestone

**v1.13 Teaching Design Package Markdown Baseline Rendering**

This milestone makes `teaching-design-package` render from the committed teacher-facing Markdown baseline:

- Baseline file: `skills/teaching-design-package/templates/teaching-design-package-full.md`
- Baseline commit observed during initialization: `28932fd Revise teaching design package markdown`

The renderer must adapt to this Markdown shape. The Markdown reference format itself is not part of the implementation change. Acceptance requires one copyable Markdown artifact, one Typst artifact produced by rendering that Markdown, and three PDFs: combined package, teaching-plan, and lesson-plan PDFs. The old `jiaoan-jihua` and `jiaoan-shicao` skills must remain standalone.

The baseline also locks derived scheduling behavior. Course and task hours are calculated from `# 授课进度计划` rows, not maintained as package YAML. Lesson-plan activity hours, task date ranges, academic year/semester, and renderer defaults must be inferred from the baseline `first_teaching_day`, built-in teaching calendar, default daily capacity, and plan-row hours, with non-final status on mapping failure.

## Phases

### Phase 28: Markdown Baseline Ingestion and Typst Generation

**Goal:** Make the integrated package render path consume the committed full-package Markdown baseline without changing its teacher-facing structure.
**Depends on:** Phase 27
**Plans:** 1/1 plans complete
**Requirements:** TDBR-01, TDBR-02, TDBR-03, TDBR-04, TDBR-05, TDBR-12, TDBR-13, TDBR-14, TDBR-15, TDBR-16, TDBR-17
**Status:** Pending

Success criteria:

1. The package path accepts `skills/teaching-design-package/templates/teaching-design-package-full.md` as a baseline input without requiring Markdown format changes.
2. The output package Markdown remains copyable and teacher-reviewable in the same reference-document shape.
3. The renderer produces one Typst artifact from that Markdown through the render path.
4. Verification records how the single Markdown source is split semantically into授课进度计划 and教学设计方案 sections without making Typst the maintained source.
5. Verification proves plan-row hour parsing derives `160H` total and task totals `CA6140=40H`, `X62W=60H`, `Z3040=60H` from `# 授课进度计划`.
6. Generated lesson-plan handoffs derive activity `##### xH` values only by mapping to same-name or same-order plan rows; any unmapped activity fails or records non-final/review-needed status.
7. Generated `学习任务分析` fields derive date ranges from `first_teaching_day`, the built-in teaching-day calendar, default `8` daily hours, and parsed plan-row hours, with current baseline expectations `5月11日——5月15日`, `5月18日——5月27日`, and `5月27日——6月5日`.
8. Generated metadata infers `2025-2026学年第二学期` from `first_teaching_day: "2026-05-11"` and keeps `school_year`, `semester`, `total_hours`, `daily_hours`, calendar/default/output/validation knobs out of teacher-maintained package YAML.

### Phase 29: PDF Parity and Standalone Regression

**Goal:** Produce the three accepted PDFs and prove split outputs match the old standalone jiaoan skills while preserving their public interfaces.
**Depends on:** Phase 28
**Plans:** 1 plan
**Requirements:** TDBR-06, TDBR-07, TDBR-08, TDBR-09, TDBR-10, TDBR-11, TDBR-12, TDBR-13, TDBR-14, TDBR-15, TDBR-16, TDBR-17
**Status:** Pending

Success criteria:

1. The final package workflow generates three PDF artifacts: combined package PDF, teaching-plan PDF, and lesson-plan PDF.
2. The combined package PDF contains the original授课进度计划 and教案 outputs as one merged package without dropping required content.
3. The teaching-plan PDF matches standalone `jiaoan-jihua` content and format for the same source scope, allowing only timestamp differences.
4. The lesson-plan PDF matches standalone `jiaoan-shicao` content and format for the same source scope, allowing only timestamp differences.
5. Public command, input, output, and documentation contracts for standalone `jiaoan-jihua` and `jiaoan-shicao` remain stable.
6. PDF parity evidence proves the displayed total hours, per-task hours, lesson-plan activity hours, task date ranges, and inferred academic year/semester come from the Phase 28 derived scheduling contract rather than manual YAML or duplicated Markdown facts.
7. The final Markdown copied from the baseline remains teacher-facing and unchanged in structure; machine defaults and validation/output settings appear only in skill/script contracts, manifests, or sidecar evidence.

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
| 27. Official Activity Table Width Alignment | v1.12 | Complete | 2026-06-14 |
| 28. Markdown Baseline Ingestion and Typst Generation | 1/1 | Complete   | 2026-06-14 |
| 29. PDF Parity and Standalone Regression | v1.13 | Pending | — |

## Current Position

Phase 28 is ready to discuss and plan.

## Next Step

Run `/gsd:discuss-phase 28` to gather implementation context, or `/gsd:plan-phase 28` to plan directly.

---
*Roadmap updated: 2026-06-15 after v1.13 milestone initialization*
