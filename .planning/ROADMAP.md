# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Last updated:** 2026-06-14 after v1.10 milestone start
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
- **Active: v1.10 Jiaoan Typst 1:1 Conversion** - Phases 20-21, started 2026-06-14. Goal: strict script-only conversion for the two `test/1.10/` jiaoan fixture pairs.

## Active Milestone

**v1.10 Jiaoan Typst 1:1 Conversion**

Goal: Make the existing `jiaoan-shicao` and `jiaoan-jihua` skills convert two provided Markdown fixtures into their corresponding Typst targets with strict 1:1 equivalence, using only skill-internal script code.

| Phase | Name | Goal | Requirements | Can Parallelize |
|-------|------|------|--------------|-----------------|
| 20 | Jiaoan Shicao 教案 1:1 Typst Conversion | Update the `jiaoan-shicao` skill so `test/1.10/电气设备控制线路安装与调试教案.md` can generate Typst strictly matching `test/1.10/电气设备控制线路安装与调试教案.typ`. | SHICAO-01, SHICAO-02, SHICAO-03, SHICAO-04, VERIFY-01, VERIFY-02, VERIFY-03 | Yes, independent from Phase 21 |
| 21 | Jiaoan Jihua 授课计划 1:1 Typst Conversion | Update the `jiaoan-jihua` skill so `test/1.10/电气设备控制线路安装与调试授课计划.md` can generate Typst strictly matching `test/1.10/电气设备控制线路安装与调试授课计划.typ`. | JIHUA-01, JIHUA-02, JIHUA-03, JIHUA-04, VERIFY-01, VERIFY-02, VERIFY-03 | Yes, independent from Phase 20 |

### Phase 20: Jiaoan Shicao 教案 1:1 Typst Conversion

**Goal:** Keep all changes inside `skills/jiaoan-shicao/` and make the skill's script generate the target教案 Typst from the provided Markdown source.

**Success criteria:**
1. `skills/jiaoan-shicao/SKILL.md`, `references/`, and/or `scripts/` document and implement the fixture conversion path.
2. The final command invokes only `skills/jiaoan-shicao/scripts/` code for Markdown-to-Typst generation.
3. `test/1.10/电气设备控制线路安装与调试教案.md` generates a `.typ` result that strictly matches `test/1.10/电气设备控制线路安装与调试教案.typ`.
4. Verification evidence includes strict diff, hash, or documented equivalence for the generated教案 output.

**Suggested next command:** `/gsd:discuss-phase 20 /Users/mrered/Developer/Presto-Agent-Skills`

### Phase 21: Jiaoan Jihua 授课计划 1:1 Typst Conversion

**Goal:** Keep all changes inside `skills/jiaoan-jihua/` and make the skill's script generate the target授课计划 Typst from the provided Markdown source.

**Success criteria:**
1. `skills/jiaoan-jihua/SKILL.md`, `references/`, and/or `scripts/` document and implement the fixture conversion path.
2. The final command invokes only `skills/jiaoan-jihua/scripts/` code for Markdown-to-Typst generation.
3. `test/1.10/电气设备控制线路安装与调试授课计划.md` generates a `.typ` result that strictly matches `test/1.10/电气设备控制线路安装与调试授课计划.typ`.
4. Verification evidence includes strict diff, hash, or documented equivalence for the generated授课计划 output.

**Suggested next command:** `/gsd:discuss-phase 21 /Users/mrered/Developer/Presto-Agent-Skills`

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

## Current Position

v1.10 is active and ready for phase planning. Phase 20 and Phase 21 are intentionally parallelizable because they touch separate skill directories and fixture pairs.

## Next Step

Run `/gsd:discuss-phase 20 /Users/mrered/Developer/Presto-Agent-Skills` or `/gsd:discuss-phase 21 /Users/mrered/Developer/Presto-Agent-Skills` to start either parallel phase.

---
*Roadmap updated: 2026-06-14 after v1.10 milestone start*
