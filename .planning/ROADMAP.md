# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Last updated:** 2026-06-21 after v1.16 milestone definition
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
- **Shipped: v1.15 teaching-design-package 模块化渲染与旧格式回归** - Phases 33-36, shipped 2026-06-15. Archives: `.planning/milestones/v1.15-ROADMAP.md`, `.planning/milestones/v1.15-REQUIREMENTS.md`, `.planning/milestones/v1.15-MILESTONE-AUDIT.md`
- **Active: v1.16 调课单 Skill** - Phases 37-40. Goal: build a Markdown-first `调课单` document workflow from hand-authored Typst/Markdown baselines through independent script rendering, PDF generation, and clarification guidance.

## Active Milestone

**v1.16 调课单 Skill**

Build a new `调课单` skill by first hand-authoring the target Typst form, then hand-authoring the teacher-editable Markdown source, then implementing a skill-local Markdown-to-Typst renderer and PDF workflow. The renderer may borrow implementation patterns from existing document skills, but must not depend on sibling skill scripts at runtime.

## Phases

| Phase | Name | Goal | Requirements |
|-------|------|------|--------------|
| 37 | 调课单 Typst Baseline | Capture the accepted `调课单` visual/form structure as a hand-authored Typst reference and compilable PDF baseline. | TKD-TYP-01, TKD-TYP-02, TKD-TYP-03 |
| 38 | 调课单 Markdown Contract | Create the teacher-reviewable Markdown fixture and contract that can express every required form fact without raw Typst. | TKD-MD-01, TKD-MD-02, TKD-MD-03 |
| 39 | 调课单 Markdown-to-Typst Renderer | Implement the independent skill-local script that converts finalized Markdown into Typst and verifies output against the baseline. | TKD-RENDER-01, TKD-RENDER-02, TKD-RENDER-03, TKD-RENDER-04 |
| 40 | 调课单 Skill Workflow and PDF Gate | Complete the canonical skill entry, PDF workflow, clean output/diagnostic boundary, runtime adapter notes, questions for missing information, and repository discoverability. | TKD-PDF-01, TKD-PDF-02, TKD-PDF-03, TKD-PDF-04, TKD-PDF-05 |

### Phase 37: 调课单 Typst Baseline

**Goal:** Capture the accepted adjustment-form surface before automation.

**Success criteria:**
1. A `skills/tiaokedan/` scaffold exists with a hand-authored Typst reference fixture for `调课单`.
2. The Typst reference reflects the user's described fields, labels, table shape, signature/approval areas, and typography choices.
3. The reference compiles to a non-empty PDF when local Typst dependencies are available, or records the exact blocking error if the environment cannot compile.

### Phase 38: 调课单 Markdown Contract

**Goal:** Make the same form facts editable and reviewable in Markdown.

**Success criteria:**
1. A hand-authored Markdown fixture expresses all facts needed by the Phase 37 Typst reference.
2. The contract keeps renderer defaults out of teacher-maintained fields and documents any required markers for unknown values.
3. The Markdown fixture can be inspected by a teacher before any Typst/PDF generation.

### Phase 39: 调课单 Markdown-to-Typst Renderer

**Goal:** Convert finalized Markdown into the accepted Typst form using only skill-local runtime code.

**Success criteria:**
1. The public command converts the fixture Markdown into generated Typst.
2. The generated Typst is deterministically compared against the accepted reference or a documented normalized equivalent.
3. The renderer fails non-zero with clear messages for missing required fields, malformed sections, or unsupported values.
4. Runtime execution does not call sibling skill scripts or require sibling skill directories.

### Phase 40: 调课单 Skill Workflow and PDF Gate

**Goal:** Package `调课单` as a complete portable skill with final PDF workflow and missing-information questions.

**Success criteria:**
1. The canonical `SKILL.md` explains when to use `调课单`, the Markdown-first workflow, safety boundaries, and verification steps.
2. Runtime adapter notes cover Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent without moving agent-private syntax into the canonical body.
3. The PDF workflow produces clean teacher-facing output while diagnostics and temporary evidence stay hidden or debug-only.
4. Documentation lists concise questions to ask when required form facts are missing.
5. README/index/discoverability updates make the skill findable and keep requirement traceability complete.

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
| 33. Module Registry, Unified Extraction, and Scheduling Model | v1.15 | Complete | 2026-06-15 |
| 34. Teaching Plan Formal Renderer Migration | v1.15 | Complete | 2026-06-15 |
| 35. Teaching Design Formal Renderer and Cross-Module Validation | v1.15 | Complete | 2026-06-15 |
| 36. Public Delivery, PDF Merge, and Standalone Regression | v1.15 | Complete | 2026-06-15 |
| 37. 调课单 Typst Baseline | v1.16 | Complete | 2026-06-21 |

## Current Position

Phase 37 completed the hand-authored `调课单` Typst baseline and non-empty PDF evidence. The next implementation step is Phase 38: create the teacher-reviewable Markdown fixture and contract that express the same form facts without raw Typst.

## Next Step

Start Phase 38 with `/gsd:discuss-phase 38` or `/gsd:plan-phase 38`.

---
*Roadmap updated: 2026-06-21 after Phase 37 completion*
