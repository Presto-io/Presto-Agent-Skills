# Milestones

## v1.17 school-pptx (Shipped: 2026-07-16)

**Delivered:** A Markdown-first `school-pptx` skill that renders controlled, editable school-template PPTX files with deterministic pagination, structural verification, and hash-bound human UAT.

**Phases completed:** 4 phases, 19 plans, 51 tasks

**Key accomplishments:**

- Added a controlled `standard-school` template, 11-layout manifest, and repeatable template validation.
- Defined a teacher-reviewable YAML plus slide-block Markdown contract with deterministic fixture generation and bounded diagnostics.
- Rendered native editable text, tables, pictures, groups, code, and speaker notes with logical-to-physical pagination.
- Added the fixed public 8-gate, 6-negative, and Phase 43 21-gate verification chain with six-runtime documentation.
- Passed 44/44 requirements, 10/10 integration checks, 4/4 E2E flows, and hash-bound WPS human UAT 10/10.

**Archives:**

- Roadmap: `.planning/milestones/v1.17-ROADMAP.md`
- Requirements: `.planning/milestones/v1.17-REQUIREMENTS.md`
- Audit: `.planning/milestones/v1.17-MILESTONE-AUDIT.md`

**What's next:** Promote backlog Phase 999.1「全技能干净交付目录标准化改造」into the next milestone.

---

## v1.16 调课单 Skill (Shipped: 2026-06-21)

**Phases completed:** 4 phases, 4 plans, 22 tasks

**Key accomplishments:**

- Hand-authored A4 landscape `调课单` Typst reference with non-empty PDF baseline evidence
- Teacher-readable 调课单 Markdown source and skill-local field contract for the accepted Phase 37 form facts
- Skill-local 调课单 renderer converts the accepted Markdown fixture into byte-for-byte matching Typst and rejects non-final Markdown failures
- `tiaokedan` now has a portable Markdown-first skill entry, strict Typst/PDF final gate, clean output contract, missing-information guide, and repository discoverability.

**Archives:**

- Roadmap: `.planning/milestones/v1.16-ROADMAP.md`
- Requirements: `.planning/milestones/v1.16-REQUIREMENTS.md`
- Audit: `.planning/milestones/v1.16-MILESTONE-AUDIT.md`

**Closeout notes:** v1.16 audit passed with non-blocking metadata tech debt; closeout corrected the stale Phase 37 and Phase 40 summary commit labels before archive commit.

---

## v1.15 teaching-design-package 模块化渲染与旧格式回归 (Shipped: 2026-06-15)

**Phases completed:** 4 phases, 4 plans, 26 tasks

**Key accomplishments:**

- Package-owned module registry with skill-local calendar scheduling and hidden module Markdown/Typst intermediates
- Package-owned 授课进度计划表 formal renderer with strict row-hour evidence and legacy fixture equivalence
- Package-owned 教学设计方案 formal renderer with strict task/stage/activity validation against 授课进度计划
- Course-name-prefixed teaching-design package delivery with registry-order module PDF merge and standalone failure regression

**Archives:**

- Roadmap: `.planning/milestones/v1.15-ROADMAP.md`
- Requirements: `.planning/milestones/v1.15-REQUIREMENTS.md`
- Audit: `.planning/milestones/v1.15-MILESTONE-AUDIT.md`

**Known deferred items at close:** 1 legacy audit-open quick-task compatibility item recorded in `.planning/STATE.md` Deferred Items.

---

## v1.15.1 Teaching Design Cover Hour Format Patch (Resolved: 2026-06-15)

**Patch scope:** post-close formatting fix after v1.15 milestone archive

**Key fixes:**

- Preserved `H` in `教学设计方案` cover `计划总课时` and task-analysis `课时` values.
- Aligned cover labels so four-character and five-character labels share the same width and colon column.
- Kept the fix inside the package-owned `teaching-design-package` renderer without modifying legacy `jiaoan-shicao`.
- Regenerated and user-accepted a clean delivery artifact set under `generated/teaching-design-package-acceptance-20260615-195318/`.

**Record:**

- Patch notes: `.planning/milestones/v1.15.1-POST-CLOSE-PATCH.md`
- Debug: `.planning/debug/resolved/teaching-design-cover-hours.md`

---

## v1.14 teaching-design-package 单技能独立交付与 1+1+3 输出契约 (Shipped: 2026-06-15)

**Phases completed:** 3 phases, 3 plans, 16 tasks

**Key accomplishments:**

- Standalone teaching-design-package now renders unified Markdown through a package-owned model and Typst/PDF status path without sibling skill calls.
- `teaching-design-package` now reads as a teacher source-materials-to-full-Markdown workflow before it reads as a renderer.
- `teaching-design-package` now enforces a clean public 1+1+3 delivery root and hidden diagnostics boundary, with derived scheduling validation.

**Archives:**

- Roadmap: `.planning/milestones/v1.14-ROADMAP.md`
- Requirements: `.planning/milestones/v1.14-REQUIREMENTS.md`
- Audit: `.planning/milestones/v1.14-MILESTONE-AUDIT.md`

**Known deferred items at close:** 1 audit-open quick-task compatibility item recorded in `.planning/STATE.md` Deferred Items.

---

## v1.13 Teaching Design Package Markdown Baseline Rendering (Shipped: 2026-06-14)

**Phases completed:** 2 phases, 2 plans, 13 tasks

**Key accomplishments:**

- Teacher-facing package Markdown now drives generated jiaoan handoffs, derived scheduling evidence, and package Typst without modifying the baseline reference.
- Real split and combined teaching-design PDFs with same-handoff standalone parity and derived scheduling evidence

**Archives:**

- Roadmap: `.planning/milestones/v1.13-ROADMAP.md`
- Requirements: `.planning/milestones/v1.13-REQUIREMENTS.md`
- Audit: `.planning/milestones/v1.13-MILESTONE-AUDIT.md`

---

## v1.12 Teaching Design Package Post-Close Repair (Shipped: 2026-06-14)

**Phases completed:** 2 phases, 2 plans, 10 tasks

**Key accomplishments:**

- Package scheduling evidence now backfills concrete `起止日期` values into generated practical lesson-plan Markdown before `jiaoan-shicao` rendering.
- `jiaoan-shicao` activity tables now use official-style `25.04cm` chapter-scoped Typst column widths, with package regression PDFs verified.

**Archives:**

- Roadmap: `.planning/milestones/v1.12-ROADMAP.md`
- Requirements: `.planning/milestones/v1.12-REQUIREMENTS.md`
- Audit: `.planning/milestones/v1.12-MILESTONE-AUDIT.md`

---

## v1.11 Integrated Teaching Design Package (Shipped: 2026-06-14)

**Phases completed:** 4 phases, 4 plans, 20 tasks, automated audit passed

**Key accomplishments:**

- Package-level scheduling contract with deterministic calendar/hour fixture evidence for future teaching-design package composition.
- Portable `teaching-design-package` orchestration skill with package Markdown checkpoint, jiaoan module handoff, split Typst status, and six-runtime adapter coverage.
- Optional end-of-term package orchestration with module-owned evidence pointers and honest combined PDF status.
- Black-box public command regression and documentation-index verification for the v1.11 teaching-design-package integration.

**Archives:**

- Roadmap: `.planning/milestones/v1.11-ROADMAP.md`
- Requirements: `.planning/milestones/v1.11-REQUIREMENTS.md`
- Audit: `.planning/milestones/v1.11-MILESTONE-AUDIT.md`

---

## v1.10 Jiaoan Typst 1:1 Conversion (Shipped: 2026-06-13)

**Phases completed:** 2 phases, 2 plans, 8 tasks, automated audit passed

**Key accomplishments:**

- Added a skill-local `jiaoan-shicao` fixture renderer that generates the v1.10 教案 Typst byte-for-byte from Markdown.
- Added a Bash-only `jiaoan-jihua` parser and official five-column Typst emitter with byte-for-byte fixture verification.
- Recorded strict `diff -u`, SHA-256, and anti-copy evidence for both fixture pairs.
- Passed the v1.10 milestone audit for SHICAO-01 through SHICAO-04, JIHUA-01 through JIHUA-04, and VERIFY-01 through VERIFY-03.

**Archives:**

- Roadmap: `.planning/milestones/v1.10-ROADMAP.md`
- Requirements: `.planning/milestones/v1.10-REQUIREMENTS.md`
- Audit: `.planning/milestones/v1.10-MILESTONE-AUDIT.md`

---

## v1.10.1 Jiaoan Shicao Black-Box Layout Patch (Resolved: 2026-06-14)

**Patch scope:** post-close visual and black-box validation fix after v1.10 milestone archive

**Key fixes:**

- Aligned `jiaoan-shicao` `学习资源` table column widths with the official Presto black-box template.
- Aligned `教学活动设计` table column widths with the official content-pressure distribution.
- Matched official empty-teacher author fallback to `Presto`.
- Verified skill-local Typst and PDF outputs byte-for-byte against the black-box template for the same original Markdown.

**Record:**

- Patch notes: `.planning/milestones/v1.10.1-POST-CLOSE-PATCH.md`

---

## v1.9 Skill Decomposition and Entry Slimming (Shipped: 2026-06-13)

**Phases completed:** 3 phases, 3 plans, 12 tasks, automated audit passed

**Key accomplishments:**

- Slimmed current canonical `SKILL.md` entries by moving long examples, renderer notes, artifact details, and operational guidance into skill-local `references/`.
- Split the largest script entry points behind stable public command surfaces while preserving common flags, generated artifacts, manifest keys, and Markdown intermediate contracts.
- Updated README, skills index, directory specification, compatibility matrix, and skill template so future skills follow the lightweight-entry and skill-local module pattern.
- Passed the v1.9 milestone audit for SD-01 through SD-12 across Phases 17-19.

**Archives:**

- Roadmap: `.planning/milestones/v1.9-ROADMAP.md`
- Requirements: `.planning/milestones/v1.9-REQUIREMENTS.md`
- Audit: `.planning/milestones/v1.9-MILESTONE-AUDIT.md`

---

## v1.8 School Presentation Continuation (Shipped: 2026-06-11)

**Phases completed:** 3 phases, 3 plans, automated audit passed

**Key accomplishments:**

- Added playback-local presenter markup tools: pointer, pen, highlighter, eraser, clear current page, and page-scoped session annotations that do not mutate Markdown, manifests, preview, or review artifacts.
- Added deterministic classroom interaction and structured layout authoring for peek hints, sorting/reordering, restrained body-step animation, timelines, cards, galleries, SmartArt-like process layouts, semantic icons, and section controls.
- Added print/export review behavior plus one-click final PDF export with expanded reveal/mask/emphasis/sort states, reader outline/bookmarks, agenda links, section-page include/skip behavior, and annotation exclusion.
- Passed the v1.8 milestone audit for SP-17 through SP-27 across Phases 14-16.

**Archives:**

- Roadmap: `.planning/milestones/v1.8-ROADMAP.md`
- Requirements: `.planning/milestones/v1.8-REQUIREMENTS.md`
- Audit: `.planning/milestones/v1.8-MILESTONE-AUDIT.md`

---

## v1.7.1 End-of-Term Teaching Materials Post-Close Patch (Resolved: 2026-06-10)

**Patch scope:** bug fixes after v1.7 milestone archive

**Key fixes:**

- Preserved uncertain score markers such as `87?` in abnormal review while using their numeric value for provisional derived-score calculation.
- Corrected score-book and score-summary views, owned-student pagination, placeholder task display, and deterministic score-list artifacts.
- Polished fixed-template package layout after visual review, including cover spacing, warning fills, analysis page layout, and handoff divider placement.

**Record:**

- Patch notes: `.planning/milestones/v1.7.1-POST-CLOSE-PATCH.md`

---

## v1.7 End-of-Term Teaching Materials Skill (Shipped: 2026-06-10)

**Phases completed:** 3 phases, 3 plans, automated audit passed

**Key accomplishments:**

- Added `end-of-term-teaching-materials`, with a structured teaching-data contract and one teacher-editable Markdown source of truth.
- Implemented fixed-template Typst/PDF package rendering, deterministic JSON/CSV table artifacts, and `scorebook.xlsx` output.
- Closed the uncertain-score review gap: values such as `87?` now reach Markdown review with explicit markers, while normal final export remains strict.
- Passed milestone audit for ETM-01 through ETM-08 across Phases 11-13.

**Archives:**

- Roadmap: `.planning/milestones/v1.7-ROADMAP.md`
- Requirements: `.planning/milestones/v1.7-REQUIREMENTS.md`
- Audit: `.planning/milestones/v1.7-MILESTONE-AUDIT.md`

---

## v1.6 School Presentation Playback UX (Shipped: 2026-06-11)

**Phases completed:** 2 phases, 2 plans, automated verification passed, human visual UAT passed

**Key accomplishments:**

- Added playback mode, thumbnail rail, large preview, and tiled overview for generated `school-presentation` HTML decks.
- Documented and rendered page hierarchy across logical slides, physical pages, sections, and reveal steps.
- Added ordered reveals, restrained emphasis animation, and classroom answer masks controlled from Markdown.
- Closed the Phase 10 visual UAT gate after agenda, cover, media fallback, alert icon, spacing, list pagination, and playback fit fixes.

**Archives:**

- Roadmap: `.planning/milestones/v1.6-ROADMAP.md`
- Requirements: `.planning/milestones/v1.6-REQUIREMENTS.md`
- Audit: `.planning/milestones/v1.6-MILESTONE-AUDIT.md`

---

## v1.5 School Presentation Skill (Shipped: 2026-06-01)

**Phases completed:** 1 phase, 1 plan, 3 tasks

**Key accomplishments:**

- Added `school-presentation`, with a reusable Markdown logical-slide intermediate and an offline self-contained HTML deck renderer.
- Extracted school identity assets and applied blue-green school-style layouts, footer branding, formula/table/chart/media rendering, overflow splitting, and a closing page.
- Passed deterministic render verification and user-confirmed visual UAT.

**Archives:**

- Roadmap: `.planning/milestones/v1.5-ROADMAP.md`
- Requirements: `.planning/milestones/v1.5-REQUIREMENTS.md`

---

## v1.4 Jiaoan Jihua Skill (Shipped: 2026-05-31)

**Phases completed:** 1 phase, 1 plan, 3 tasks

**Key accomplishments:**

- Added `jiaoan-jihua`, with a reusable授课进度计划 Markdown intermediate and verified Typst/PDF render path

**Archives:**

- Roadmap: `.planning/milestones/v1.4-ROADMAP.md`
- Requirements: `.planning/milestones/v1.4-REQUIREMENTS.md`

---

## v1.3 Jiaoan Shicao Skill (Shipped: 2026-05-31)

**Phases completed:** 1 phase, 1 plan, 3 tasks

**Key accomplishments:**

- Second concrete skill in the repository: `jiaoan-shicao`, with a reusable Markdown intermediate, bundled calendar support resource, and verified Typst/PDF render path

**Archives:**

- Roadmap: `.planning/milestones/v1.3-ROADMAP.md`
- Requirements: `.planning/milestones/v1.3-REQUIREMENTS.md`

---

## v1.2 Gongwen Skill (Shipped: 2026-05-31)

**Phases completed:** 1 phase, 1 plan, 3 tasks

**Key accomplishments:**

- First concrete skill in the repository: `gongwen`, with a reusable Markdown intermediate and verified Typst/PDF render path

**Archives:**

- Roadmap: `.planning/milestones/v1.2-ROADMAP.md`
- Requirements: `.planning/milestones/v1.2-REQUIREMENTS.md`

---

## v1.1 v1.1 (Shipped: 2026-05-31)

**Phases completed:** 1 phases, 1 plans, 3 tasks

**Key accomplishments:**

- Markdown-first document workflow contract with visible review handling for ambiguous or lossy source material

---

## v1.0 MVP (Shipped: 2026-05-30)

**Phases completed:** 3 phases, 3 plans, 10 tasks

**Key accomplishments:**

- Repository documentation contract aligned across contributor entry, directory boundaries, agent rules, and GSD planning records
- Canonical skill templates and runtime compatibility docs now tell one single-file-first story.
- EX-01 and EX-02 reframed as deferred optional example guidance while the canonical SKILL.md path stays primary

**Archives:**

- Roadmap: `.planning/milestones/v1.0-ROADMAP.md`
- Requirements: `.planning/milestones/v1.0-REQUIREMENTS.md`

**Known deferred items at close:** EX-01 and EX-02 remain optional future example guidance, not v1 delivery gaps.

---
