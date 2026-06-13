# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Last updated:** 2026-06-14 after v1.11 milestone initialization
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

## Active Milestone

### v1.11 Integrated Teaching Design Package / 教学设计整包技能

**Status:** In progress
**Phases:** 22-25
**Goal:** Create a new orchestration-skill path that integrates teaching-plan, lesson-plan, and optional end-of-term teaching-material workflows while preserving the original skills and the repository's Markdown-first, portable-skill discipline.

| Phase | Name | Scope | Requirements |
|-------|------|-------|--------------|
| 22 | Scheduling Contract and Fixture | Complete 2026-06-13: shared calendar/scheduling inputs, derived outputs, evidence format, conflict handling, and deterministic fixture proof are now documented and verified. | TDP-01, TDP-02, TDP-03, TDP-04 |
| 23 | Integrated Skill Entry and Jiaoan Orchestration | Complete 2026-06-13: `teaching-design-package` now has a portable skill entry, teacher-reviewable package Markdown checkpoint, jiaoan module handoff rules, split Typst/PDF status helper, fixture evidence, and six-runtime adapter coverage. | TDP-05, TDP-06, TDP-07, TDP-08, TDP-09 |
| 24 | Optional End-of-Term Module and Package Outputs | Complete 2026-06-14: optional end-of-term module integration now has explicit package contract, module handoff fields, manifest pointers for table/workbook artifacts, split `end-of-term-package.pdf` status, blocked-review behavior, and honest `teaching-design-package.pdf` combined-output evidence. | TDP-10, TDP-11, TDP-12, TDP-13, TDP-14 |
| 25 | Regression Verification and Documentation Index | Verify existing public command surfaces, package failure/manifest behavior, runtime adapter coverage, OpenClaw/Hermes notes, and documentation/index discoverability. | TDP-09, TDP-14, TDP-15, TDP-16 |

**Acceptance direction:**

- The original `jiaoan-jihua`, `jiaoan-shicao`, and `end-of-term-teaching-materials` skills remain standalone and callable.
- The new package skill uses a persistent Markdown intermediate before rendering.
- Scheduling inference is auditable from calendar and hour-consumption evidence.
- Split outputs are planned where possible, and the default combined `teaching-design-package.pdf` is explicit.
- Runtime-specific behavior stays in adapter notes; OpenClaw and Hermes Agent remain mandatory compatibility targets.

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
| 25. Regression Verification and Documentation Index | v1.11 | Planned | — |

## Current Position

Phase 24 is complete and v1.11 is ready for Phase 25 discussion.

## Next Step

Run `/gsd:discuss-phase 25` to discuss the regression verification and documentation index slice.

---
*Roadmap updated: 2026-06-14 after Phase 24 execution*
