# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Last updated:** 2026-06-15 after v1.15 milestone initialization
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
- **Shipped: v1.13 Teaching Design Package Markdown Baseline Rendering** - Phases 28-29, shipped 2026-06-14. Archives: `.planning/milestones/v1.13-ROADMAP.md`, `.planning/milestones/v1.13-REQUIREMENTS.md`, `.planning/milestones/v1.13-MILESTONE-AUDIT.md`
- **Shipped: v1.14 teaching-design-package 单技能独立交付与 1+1+3 输出契约** - Phases 30-32, shipped 2026-06-15. Archives: `.planning/milestones/v1.14-ROADMAP.md`, `.planning/milestones/v1.14-REQUIREMENTS.md`, `.planning/milestones/v1.14-MILESTONE-AUDIT.md`

## Active Milestone

**v1.15 teaching-design-package 模块化渲染与旧格式回归**

This milestone converts `teaching-design-package` into a package-owned all-in-one module renderer. The unified Markdown remains the only content source. The package must derive hidden module Markdown and Typst, migrate the accepted `jiaoan-jihua` and `jiaoan-shicao` formal rendering rules into package internals, generate real module PDFs, and merge the final course package PDF only after all modules succeed.

The successful public delivery surface is course-name-prefixed `1 + 1 + N`: the unified Markdown and final PDFs only. Module Markdown, module Typst, scheduling model, status, diagnostics, logs, and calendar evidence stay in hidden `.teaching-design-package/` paths.

## Phases

### Phase 33: Module Registry, Unified Extraction, and Scheduling Model

**Goal:** Establish the package-owned modular architecture that parses the unified Markdown, derives YAML/module inputs, and produces hidden module Markdown/Typst plus one shared scheduling model.
**Depends on:** Phase 32
**Plans:** 1/1 plans complete
**Requirements:** TDPKG-MOD-01, TDPKG-MOD-02, TDPKG-MOD-03, TDPKG-MOD-04, TDPKG-MOD-05, TDPKG-MOD-06, TDPKG-MOD-07, TDPKG-YAML-01, TDPKG-YAML-02, TDPKG-YAML-03, TDPKG-YAML-04, TDPKG-SCHED-01, TDPKG-SCHED-02, TDPKG-SCHED-03, TDPKG-SCHED-04, TDPKG-SCHED-05
**Status:** Complete

Success criteria:

1. `teaching-design-package-full.md` shaped input is parsed as the only content source and split into registered module data for `teaching-plan` and `teaching-design`.
2. Hidden module Markdown and Typst paths are produced under `.teaching-design-package/work/` without exposing them in the public delivery directory.
3. YAML conversion fills module-specific frontmatter from unified YAML and derived scheduling facts, including `teacher_name`, `daily_hours`, `total_hours`, and `use_time`.
4. `calendar.json` lives inside the `teaching-design-package` skill folder and is usable from a standalone copy of that folder.
5. A single scheduling model derives academic year, semester, total course date range, task date ranges, week/day labels, and daily hour consumption from real calendar data.

### Phase 34: Teaching Plan Formal Renderer Migration

**Goal:** Migrate the accepted `jiaoan-jihua` teaching-plan format rules into package-owned internals and prove the generated 授课进度计划表 module is formally equivalent to the legacy baseline.
**Depends on:** Phase 33
**Plans:** 1/1 plans complete
**Requirements:** TDPKG-LEGACY-01, TDPKG-LEGACY-03, TDPKG-LEGACY-04, TDPKG-VAL-01
**Status:** Complete

Success criteria:

1. The package generates `课程名授课进度计划表.pdf` using internal migrated rendering rules, without invoking the sibling `jiaoan-jihua` skill at runtime.
2. Fixture evidence demonstrates equality or accepted equivalence with the current standalone `jiaoan-jihua` output format.
3. The legacy `jiaoan-jihua` skill remains available with its public interface unchanged.
4. Teaching-plan row hours remain the only authoritative raw hour source, and task/course totals are strict sums from those rows.

### Phase 35: Teaching Design Formal Renderer and Cross-Module Validation

**Goal:** Migrate the accepted `jiaoan-shicao` teaching-design format rules into package-owned internals and enforce strict task/activity/hour/date consistency against the teaching-plan module.
**Depends on:** Phase 34
**Plans:** 1/1 plans complete
**Requirements:** TDPKG-LEGACY-02, TDPKG-VAL-02, TDPKG-VAL-03, TDPKG-VAL-04
**Status:** Complete

Success criteria:

1. The package generates `课程名教学设计方案.pdf` using internal migrated rendering rules, without invoking the sibling `jiaoan-shicao` skill at runtime.
2. Fixture evidence demonstrates equality or accepted equivalence with the current standalone `jiaoan-shicao` output format.
3. Lesson-plan task hours and activity `##### xH` values are derived from the teaching-plan scheduling model rather than independently calculated.
4. Mismatched task counts, link counts, activity counts, titles, hour totals, or date ranges fail with hidden diagnostics and no final success output.

### Phase 36: Public Delivery, PDF Merge, and Standalone Regression

**Goal:** Enforce the course-name-prefixed `1 + 1 + N` public delivery contract, honest PDF merge semantics, hidden diagnostics, and standalone-copy verification.
**Depends on:** Phase 35
**Plans:** 0/1 plans complete
**Requirements:** TDPKG-ART-01, TDPKG-ART-02, TDPKG-ART-03, TDPKG-PDF-01, TDPKG-PDF-02, TDPKG-PDF-03, TDPKG-PDF-04
**Status:** Pending

Success criteria:

1. Default output for the current template contains `电气设备控制线路安装与调试教学资料.md`, `电气设备控制线路安装与调试教学资料.pdf`, `电气设备控制线路安装与调试授课进度计划表.pdf`, and `电气设备控制线路安装与调试教学设计方案.pdf`.
2. Public output contains no `.typ`, status, manifest, model, diagnostics, log, calendar JSON, or module intermediate files.
3. Hidden `.teaching-design-package/` evidence includes module Markdown, module Typst, model, status, diagnostics, calendar path/hash, scheduling summary, and any failure evidence.
4. Combined PDF merge runs only after all registered module PDFs exist and are non-empty, using module registration order and honestly recorded merge tooling.
5. Any module render or merge failure exits non-zero and does not leave a public directory that appears successful.
6. A standalone-copy check proves the package works when only the `teaching-design-package` skill folder is installed.

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
| 28. Markdown Baseline Ingestion and Typst Generation | v1.13 | Complete | 2026-06-14 |
| 29. PDF Parity and Standalone Regression | v1.13 | Complete | 2026-06-14 |
| 30. Standalone Skill Boundary and Internalized Dependencies | v1.14 | Complete | 2026-06-15 |
| 31. Teacher-Facing Unified Markdown Workflow | v1.14 | Complete | 2026-06-15 |
| 32. Clean 1+1+3 Delivery and Scheduling Regression Gate | v1.14 | Complete | 2026-06-15 |

## Current Position

Phase 35 is complete. The package-owned formal `教学设计方案` renderer, hidden `teaching-design.typ`, real `teaching-design.pdf`, strict task/stage/activity/hour/date validation, hidden mismatch diagnostics, standalone-copy check, and legacy `jiaoan-shicao` preservation are ready for Phase 36 public delivery and merge semantics.

## Next Step

Run `/gsd:discuss-phase 36` to prepare course-name-prefixed public delivery, final PDF merge semantics, and standalone regression.

---
*Roadmap updated: 2026-06-15 after Phase 34 execution*
