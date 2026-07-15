# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Last updated:** 2026-07-16 after completing Phase 44 Plan 44-04 human viewer UAT
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
- **Shipped: v1.16 调课单 Skill** - Phases 37-40, shipped 2026-06-21. Archives: `.planning/milestones/v1.16-ROADMAP.md`, `.planning/milestones/v1.16-REQUIREMENTS.md`, `.planning/milestones/v1.16-MILESTONE-AUDIT.md`
- **Active: v1.17 school-pptx** - Phases 41-44, planning started 2026-07-13.

## Active Milestone

### v1.17 school-pptx

**Milestone Goal:** Build a `school-pptx` skill that converts structured Markdown logical slides into editable, layout-stable, template-consistent `.pptx` files.

**Delivery order:** Normalize the standard template and manifest first, lock the Markdown fixture and contract second, implement editable PPTX rendering and pagination third, then close with verification, runtime notes, and manual UAT evidence.

## Phases

- [x] **Phase 41: Standard Template and Manifest** - Normalize the school visual sample into a skill-local PPTX template with a committed slot manifest and template validation command. (completed 2026-07-13)
- [x] **Phase 42: Markdown Contract and Full Fixture** - Define the constrained YAML plus slide-block Markdown contract and produce a full fixture covering all supported layouts and edge cases. (completed 2026-07-13)
- [x] **Phase 43: Editable PPTX Renderer and Pagination** - Render accepted Markdown into editable PPTX objects with logical-to-physical pagination, notes, media handling, and clean public output. (completed 2026-07-15)
- [x] **Phase 44: Verification Gate, Runtime Notes, and UAT** - Add repeatable structural verification, negative cases, six-runtime guidance, repository discoverability, and manual visual acceptance evidence. (completed 2026-07-16)

## Phase Details

### Phase 41: Standard Template and Manifest
**Goal**: The renderer has a controlled, skill-local school PPTX template contract before any Markdown or rendering automation depends on it.
**Depends on**: Phase 40
**Requirements**: TPL-01, TPL-02, TPL-03, TPL-04, TPL-05, TPL-06, TPL-07, VER-02
**Success Criteria** (what must be TRUE):
  1. User can inspect a normalized `school-pptx` `.pptx` template that is derived from the supplied `.potx` visual sample but used as the runtime template.
  2. User can inspect a committed manifest or slot map that names the default theme, all 11 supported layouts, each slot identity, geometry, placeholder mapping, and text budget.
  3. User receives a clear validation failure when an unknown theme is requested, including the available controlled theme identifier.
  4. User can run a repeatable template validation/report command that checks template layouts, slots, placeholders, and manifest consistency.
  5. User cannot override template-owned geometry, fonts, colors, decorative assets, footer behavior, or bounded text behavior from Markdown.
**Plans**: 1/1 plans complete
Plans:
- [x] 41-01-PLAN.md — Normalize the controlled school PPTX template, author the full manifest, and add template-report validation.
**UI hint**: yes

### Phase 42: Markdown Contract and Full Fixture
**Goal**: Teachers and agents have one reviewable Markdown contract that expresses a complete logical deck without exposing PPTX coordinates or styling.
**Depends on**: Phase 41
**Requirements**: MD-01, MD-02, MD-03, MD-04, MD-05, MD-06, MD-07, MD-08, VER-01
**Success Criteria** (what must be TRUE):
  1. User can read the `school-pptx` Markdown contract and see the exact allowed YAML fields and explicit `::: slide {layout="..."}` syntax.
  2. User can generate or inspect a full Markdown fixture that covers all 11 layouts plus notes, images/icons, tables, timeline, gallery, code, and overflow cases.
  3. User sees contents derived from `##` headings in document order while `#` is used only as a title fallback when YAML `title` is absent.
  4. User receives locatable validation errors for unsupported layout names, raw coordinate styling, arbitrary font/color overrides, unsupported raw HTML, and missing media.
  5. User can express speaker notes and normal Markdown images in the source without those notes appearing as visible slide canvas text.
**Plans**: 3/3 plans complete
Plans:
**Wave 1**
- [x] 42-01-PLAN.md — Define the Markdown contract, logical model, manifest-driven validation, and `validate` CLI.

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 42-02-PLAN.md — Add the full fixture, skill-local media, deterministic `example` command, and coverage verification.

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 42-03-PLAN.md — Close the five reproduced contract and secure example-write gaps with task-local and aggregate regression gates.
**UI hint**: yes

### Phase 43: Editable PPTX Renderer and Pagination
**Goal**: Finalized Markdown renders to a non-empty editable PPTX whose physical slides follow the normalized template budgets.
**Depends on**: Phase 42
**Requirements**: PPTX-01, PPTX-02, PPTX-03, PPTX-04, PPTX-05, PPTX-06, PPTX-07, PPTX-08, PPTX-09, PPTX-10, PPTX-11, PPTX-12, PPTX-13, VER-03, SKILL-03
**Success Criteria** (what must be TRUE):
  1. User can run a repeatable render command that turns finalized Markdown into a non-empty `.pptx` and fails non-zero on invalid input.
  2. User can open the generated deck and edit text, code, table content, timeline labels, gallery captions, images/icons, and speaker notes where PPTX supports those objects.
  3. User sees long text, tables, timelines, and galleries split into additional physical slides according to template budgets instead of overflowing or shrinking into unreadable content.
  4. User sees table continuation slides repeat the header and add a continuation marker to table continuation titles, while other continuation slides avoid visible "续" markers.
  5. Standard successful delivery always contains exactly two same-stem public artifacts: the reviewed Markdown source and the rendered PPTX (`.pptx`); manifests, logical JSON, diagnostics, logs, debug files, verification evidence, and temporary files stay hidden or in verification workdirs.
**Plans**: 11/11 plans complete
Plans:
**Wave 1**
- [x] 43-01-PLAN.md — Establish manifest-owned renderer geometry, frozen physical models, CJK measurement, and contract gates.

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 43-02-PLAN.md — Implement deterministic semantic pagination, global balancing, notes propagation, and closing mapping.

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 43-03-PLAN.md — Emit native editable PPTX objects and validate staged package structure.

**Wave 4** *(blocked on Wave 3 completion)*
- [x] 43-04-PLAN.md — Add the public render state machine, safe dual-artifact publication, and Phase 43 aggregate gate.

**Wave 5** *(blocked on Wave 4 completion)*
- [x] 43-05-PLAN.md — Close descriptor-bound PPTX publication and bounded public object-error handling gaps.

**Wave 6** *(blocked on Wave 5 completion)*
- [x] 43-06-PLAN.md — Preserve authored code text byte-for-byte through native editable PPTX emission.

**Wave 7** *(blocked on Wave 6 completion)*
- [x] 43-07-PLAN.md — Freeze two-column, cover, contents, and table geometry decisions into the physical plan.

**Wave 8** *(blocked on Wave 7 completion)*
- [x] 43-08-PLAN.md — Bound production template parsing and aggregate all Phase 43 gap regressions.

**Wave 9** *(blocked on Wave 8 completion)*
- [x] 43-09-PLAN.md — Close non-code fenced-code fidelity, header-only native tables, and bounded Pillow media errors.

**Wave 10** *(blocked on Wave 9 completion)*
- [x] 43-10-PLAN.md — Close mixed-fragment capacity, evidence-derived aggregate auditing, and descriptor-bound media race gaps.

**Wave 11** *(blocked on Wave 10 completion)*
- [x] 43-11-PLAN.md — Close contents and fragment-heading capacity, freeze dedicated-code typography, and harden aggregate evidence against false-green results.
**UI hint**: yes

### Phase 44: Verification Gate, Runtime Notes, and UAT
**Goal**: The `school-pptx` skill is discoverable, portable across required runtimes, and accepted only after repeatable structural verification plus manual visual evidence.
**Depends on**: Phase 43
**Requirements**: VER-04, VER-05, VER-06, VER-07, VER-08, VER-09, VER-10, SKILL-01, SKILL-02, SKILL-04, SKILL-05, SKILL-06
**Success Criteria** (what must be TRUE):
  1. User can run `verify --workdir <dir>` or an equivalent command that exercises example generation, template validation, rendering, and structural PPTX inspection.
  2. User can review verification evidence for dependency readiness, slide count, layout mapping, logical-to-physical pagination, contents entries, notes, media relationships, tables, code text editability, and absence of whole-slide screenshots.
  3. User sees negative cases fail non-zero for unknown theme, unknown layout, missing media, unsupported styling, unresolved review markers, and template/manifest mismatch.
  4. User can read a concise canonical `SKILL.md` plus deeper `references/` docs that cover workflow, inputs, outputs, safety boundaries, clarification questions, and verification without bloating the entry file.
  5. User can verify repository discoverability and six-runtime adapter notes for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent, including dependencies, support files, external commands, and write boundaries.
**Plans**: 4/4 plans complete
Plans:
**Wave 1**
- [x] 44-01-PLAN.md — Establish the public verify command, isolated workdir lifecycle, bounded evidence, and dependency readiness gate.

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 44-02-PLAN.md — Add fresh structural verification, the Phase 43 21-gate regression, and the fixed six-case negative registry.

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 44-03-PLAN.md — Publish the concise canonical skill, deep references, six-runtime adapter notes, and repository indexes.

**Wave 4** *(blocked on Wave 3 completion; human checkpoint)*
- [x] 44-04-PLAN.md — Record hash-bound PowerPoint/WPS viewer UAT and accept only complete human PASS evidence.
**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 41 -> 42 -> 43 -> 44

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 41. Standard Template and Manifest | v1.17 | 1/1 | Complete | 2026-07-13 |
| 42. Markdown Contract and Full Fixture | v1.17 | 3/3 | Complete    | 2026-07-13 |
| 43. Editable PPTX Renderer and Pagination | v1.17 | 11/11 | Complete | 2026-07-15 |
| 44. Verification Gate, Runtime Notes, and UAT | v1.17 | 4/4 | Complete | 2026-07-16 |

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
| 38. 调课单 Markdown Contract | v1.16 | Complete | 2026-06-21 |
| 39. 调课单 Markdown-to-Typst Renderer | v1.16 | Complete | 2026-06-21 |
| 40. 调课单 Skill Workflow and PDF Gate | v1.16 | Complete | 2026-06-22 |

## Current Position

Phases 41-44 are complete. Phase 44 Plan 44-04 is backed by hash-bound WPS Presentation UAT evidence with 10/10 human checks passed.

## Next Step

Run the v1.17 milestone audit before archive/release; the milestone is not yet marked shipped.

## Backlog

### Phase 999.1: 全技能干净交付目录标准化改造 (BACKLOG)

**Goal:** 在 v1.17 结束后，依据 `docs/clean-delivery-directory-contract.md` 完整改造当前全部技能，统一交付一级目录、支持资料分组、多轮修改成套归档、最小验证和失败清理行为，并为历史 agent 散乱产物整理提供可复用流程。
**Requirements:** TBD
**Plans:** 0 plans

Plans:
- [ ] 盘点全部技能的输入、Markdown、最终产物、历史版本、中间文件和失败输出边界
- [ ] 为每个技能补齐根目录白名单、`sources/`、`assets/`、`history/`、`.work/` 和版本发布规则
- [ ] 改造公共脚本，使候选版本先进入 `.work/`，成功后成套归档旧版本并原子发布新版本
- [ ] 删除非必要持久验证产物，并验证失败运行不会污染当前成功交付
- [ ] 更新 README、目录规范、兼容性矩阵、技能入口和 artifact contract
- [ ] 使用 `$gsd-review-backlog` 在 v1.17 结束后晋升并正式规划

---
*Roadmap updated: 2026-07-14 after Phase 42 verification*
