# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Last updated:** 2026-06-13 for v1.9 milestone start
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
- **Active: v1.9 Skill Decomposition and Entry Slimming** - Phases 17-19.

## Current Milestone: v1.9 Skill Decomposition and Entry Slimming

**Goal:** Split heavy skill entry files and scripts into smaller, discoverable support files without changing the public skill interface or artifact contracts.

**Requirements:** SD-01 through SD-12

**Phases:** 3

## Phase 17: Skill Entry and Reference Decomposition

**Goal:** Slim the current canonical `SKILL.md` files so each remains a clear semantic entry point while long operational details move into skill-local `references/`.

**Depends on:** v1.9 requirements
**Plans:** 1 planned
**Requirements:** SD-01, SD-02, SD-03, SD-04
**Status:** Pending

**Success criteria:**

1. Each current skill entry keeps trigger intent, objective, inputs, process, outputs, verification, safety, and runtime adapter notes visible.
2. Long examples, format rules, renderer notes, and operational details are moved into named `references/` files and linked from the relevant `SKILL.md`.
3. OpenClaw and Hermes Agent notes remain present and easy to find in affected entries.
4. `templates/skill/SKILL.md` and `docs/directory-spec.md` clearly describe the split between entry, references, scripts, and templates.

## Phase 18: Script Module Decomposition

**Goal:** Split the largest script entry points into smaller internal modules with clear ownership while keeping current command names, common flags, and output contracts stable.

**Depends on:** Phase 17
**Plans:** 1 planned
**Requirements:** SD-05, SD-06, SD-07, SD-08
**Status:** Pending

**Success criteria:**

1. The largest script targets have smaller module boundaries for CLI dispatch, parsing, rendering, artifact writing, and reporting helpers where appropriate.
2. Public command names and common flags remain stable for current skills.
3. Extracted shared behavior is limited to real duplication or stable contracts.
4. Canonical skill bodies and script interfaces remain runtime-neutral.

## Phase 19: Decomposition Guidance and Milestone Review

**Goal:** Update contributor guidance and review evidence so future skills follow the lightweight-entry pattern without reintroducing oversized entry files or monolithic scripts.

**Depends on:** Phase 18
**Plans:** 1 planned
**Requirements:** SD-09, SD-10, SD-11, SD-12
**Status:** Pending

**Success criteria:**

1. README, skills index, directory specification, and compatibility guidance match the implemented decomposition pattern.
2. Before/after evidence records which entry files and scripts were slimmed or split.
3. Each affected skill still exposes its Markdown intermediate and artifact contract in a discoverable place.
4. The milestone review confirms no unrelated feature expansion was folded into the structure work.

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

## Current Position

v1.9 is defining and planning the skill decomposition path. Phase 17 is the next phase.

## Next Step

Start Phase 17 with `/gsd:discuss-phase 17` or `/gsd:plan-phase 17`.

---
*Roadmap updated: 2026-06-13 for v1.9 skill decomposition and entry slimming*
