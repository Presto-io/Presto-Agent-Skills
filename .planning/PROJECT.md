# Presto Agent Skills

## Current State

**Latest shipped milestone:** v1.18 全技能干净交付目录标准化改造

**Shipped:** 2026-07-17

**Active milestone:** v1.19 毕业生高级简历生成器

**Status:** Phase 46 已完成；Phase 47 已具备执行上下文。

**Delivered in v1.18:**
- Standardized candidate-first clean delivery for all six current file-writing skills.
- Added byte-exact no-op detection, whole-bundle `history/`, handled rollback, managed assets, and fail-closed unknown/symlink boundaries.
- Added a strict six-skill 14-gate/7-fault aggregate, executable cleanup approval fixture, three-round code review closure, and 12/12 requirement evidence.

## Milestone History

v1.0 shipped on 2026-05-30. The repository now has a documentation-first portable skill framework: contributor entry docs, directory ownership rules, project agent instructions, a canonical `SKILL.md` template, runtime adapter notes inside that template, and a compatibility matrix covering Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.

v1.2 shipped the first real skill built on the document workflow pattern: normalize class-official-document content into Markdown first, then render through the Presto gongwen Typst template and verify output artifacts. v1.3 extends that pattern to `jiaoan-shicao`; v1.4 adds `jiaoan-jihua` for授课进度计划表. v1.5 shipped `school-presentation`, extending the Markdown-first control surface to school-style offline HTML presentations. v1.6 refined that HTML output with playback, preview, hierarchy, ordered reveals, emphasis animation, and answer masks. v1.7 returns to the document workflow family with `end-of-term-teaching-materials`: structured data, reviewable Markdown, fixed-template outputs, and strict final gates. v1.8-v1.16 expanded the teaching and presentation skill family while preserving Markdown-first, skill-local execution. v1.17 added `school-pptx`, a controlled-template editable PPTX workflow with deterministic pagination and hash-bound viewer UAT. v1.18 standardized clean delivery across all six writing skills with candidate-first publication, exact no-op detection, whole-bundle history, handled rollback, confirmation-gated cleanup, and evidence-bound central verification.

## What This Is

Presto Agent Skills is a portable skill repository for authoring agent skills once and adapting them across multiple AI agent runtimes. The initial targets are Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent, with OpenClaw and Hermes Agent treated as mandatory first-class compatibility targets.

The repository is currently a stable documentation-first framework. New skill work should begin from `templates/skill/SKILL.md`; runtime differences belong in that file's Runtime Adapter Notes unless a later milestone introduces generated wrappers or runtime-specific packaging.

## Core Value

A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## Current Focus

Define and build a portable graduate-resume skill while preserving the v1.18 clean-delivery contract and six-runtime compatibility.

## Current Milestone: v1.19 毕业生高级简历生成器

**Goal:** 为电气相关工科大专毕业生提供 Markdown-first 的高级简历技能，支持纯 CLI 批量生成主题化、定向且版式稳定的 Typst/PDF 简历。

**Target features:**
- 定义跨主题一致的简历混合 Markdown/YAML schema：YAML 保存信息栏、可选本地照片路径和派生偏好，Markdown 正文保存其余事实；用主题参数切换可扩展模板。
- 实现 `Markdown → Typst → PDF` 三件套、1/2 页 A4 收敛和双页逻辑分页保护。
- 支持通用版、多个单位/岗位定向版、照片/无照片版和硬性条件缺口提示。
- 将已标准化资料后的验证、定向、主题切换和批量渲染保持为零 token CLI 工作流，并将 AI 限定在可选资料整理模式。

## Latest Milestone: v1.18 全技能干净交付目录标准化改造

**Goal:** Apply the repository clean-delivery contract to every current file-writing skill so successful delivery roots stay reviewable, revisions are archived as complete sets, and failed runs never pollute the current successful version.

**Target features:**
- Define a root allowlist and explicit `sources/`, `assets/`, `history/`, and `.work/` boundaries for all six current skills.
- Generate and minimally verify complete candidate versions under `.work/<run-id>/` before publishing them as the current stable files.
- Archive replaced Markdown and all associated final artifacts together under zero-padded `history/<sequence>/` directories without creating duplicate history for unchanged output.
- Preserve the current successful delivery on failure and remove incomplete candidates, temporary evidence, and empty work directories.
- Update shared scripts, skill entries, artifact contracts, contributor documentation, directory guidance, and the six-runtime compatibility matrix.
- Provide a reusable, confirmation-gated workflow for organizing historical agent-created clutter without automatically moving or deleting unknown user files.

## Previous Milestone: v1.17 school-pptx

**Goal:** Build a school-template PPTX skill that converts structured Markdown logical slides into editable, layout-stable, template-consistent `.pptx` files.

**Target features:**
- Hand-normalize the supplied visual `.potx` sample into a skill-local, machine-mappable standard PPTX template before scripting.
- Define a YAML formatter plus explicit `::: slide {layout="..."}` Markdown contract, with `theme` as a controlled template identifier.
- Support fixed layout slots for cover, contents, section, title-content, two-column, image-text, table, timeline, gallery, code, and closing slides.
- Generate the contents slide automatically from every `##` heading while treating `#` only as a document-title fallback.
- Expand one Markdown logical slide into multiple editable physical PPTX slides when text, tables, timelines, or galleries exceed a layout budget.
- Preserve strict template consistency through fixed frame geometry, elastic text boxes with bounded font-size behavior, and no Markdown-level coordinates or styling overrides.
- Render editable PPTX objects for text, images/icons, tables, speaker notes, horizontal timelines, four-image galleries, and a basic non-highlighted code block.
- Keep animation scope minimal: no complex object animation; smooth 0.5s slide transition is allowed only if it can be implemented or preserved reliably.

## Latest Milestone: v1.16 调课单 Skill

**Goal:** Build a `调课单` skill that turns teacher-reviewed Markdown into a stable Typst/PDF adjustment form through skill-local scripts and clear clarification questions.

**Delivered features:**
- Hand-authored `调课单` Typst reference that captures the expected form layout before script automation.
- Teacher-readable Markdown contract and fixture that can express all required adjustment-form facts without raw Typst.
- Skill-local conversion script that may learn from existing implementations but does not depend on sibling skill scripts at runtime.
- PDF generation workflow, verification artifacts, runtime adapter notes, and a clear question list for missing source information.

## Previous Milestone: v1.15 teaching-design-package 模块化渲染与旧格式回归

**Goal:** Refactor `teaching-design-package` into an extensible all-in-one module renderer that derives formal teaching-plan and teaching-design PDFs from one unified Markdown source while preserving clean public delivery and hidden diagnostics.

**Delivered features:**
- Package-owned module registry and orchestration for the current two modules: 授课进度计划表 and 教学设计方案.
- Hidden module Markdown and Typst generation under `.teaching-design-package/work/`, with public delivery limited to course-name-prefixed `1 + 1 + N` artifacts.
- Migration of the accepted legacy `jiaoan-jihua` and `jiaoan-shicao` rendering rules into `teaching-design-package` internals without runtime sibling-skill dependency.
- A single scheduling model that derives calendar ranges, task/activity hours, academic year/semester, and cross-module validation evidence from `calendar.json`, `first_teaching_day`, and the teaching-plan rows.
- Strict PDF generation and merge semantics: all module PDFs must be real and non-empty before the combined `课程名教学资料.pdf` is created.

## Requirements

### Validated

- [x] Define a clear repository structure for skills, templates, runtime compatibility docs, optional examples, and GSD planning files. - v1.0
- [x] Provide a canonical `SKILL.md` authoring template that can serve as the single source of truth. - v1.0
- [x] Document adapter expectations for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent. - v1.0
- [x] Treat OpenClaw and Hermes Agent as mandatory supported runtimes, not optional future targets. - v1.0
- [x] Add project-level agent instructions through `AGENTS.md`, including the Simplified Chinese response requirement. - v1.0
- [x] Keep examples out of v1 unless a concrete contributor need appears. - v1.0
- [x] Define a Markdown-first normalization contract for arbitrary document input. - v1.1 Phase 4
- [x] Add the first concrete `gongwen` skill with trigger wording, canonical workflow, runtime notes, script code, and verification path. - v1.2 Phase 5
- [x] Add the second concrete `jiaoan-shicao` skill with trigger wording, canonical workflow, support resource, script code, and verification path. - v1.3 Phase 6
- [x] Add the `jiaoan-jihua` skill with trigger wording, canonical workflow, script code, and Typst/PDF verification path. - v1.4 Phase 7
- [x] Add the `school-presentation` skill with a Markdown logical-slide intermediate, school identity assets, offline HTML rendering, overflow splitting, and human-accepted visual output. - v1.5 Phase 8
- [x] Refine `school-presentation` playback with preview workspace, page hierarchy, ordered reveals, emphasis animation, and answer masks. - v1.6 Phases 9-10
- [x] Add the `end-of-term-teaching-materials` skill with structured data input, teacher-reviewable Markdown, fixed-template Typst/PDF rendering, deterministic table artifacts, workbook output, and strict review gates. - v1.7 Phases 11-13
- [x] Add presenter-facing marking tools to the `school-presentation` playback UI while keeping annotations separate from Markdown source content. - v1.8 Phase 14
- [x] Add deterministic classroom interaction extensions compatible with reveal/mask playback. - v1.8 Phase 15
- [x] Add structured layout helpers, print/export review behavior, and one-click final PDF export without breaking the offline single-file HTML model or fixed slide canvas constraints. - v1.8 Phases 15-16
- [x] Reduce the default reading weight of current `SKILL.md` files without losing trigger clarity, runtime adapter coverage, verification instructions, or safety boundaries. - v1.9 Phase 17
- [x] Split large helper scripts into smaller internal modules while preserving the current shell command surface and generated artifact contracts. - v1.9 Phase 18
- [x] Document the decomposition pattern in repository guidance so new skills do not accumulate heavy entry files or monolithic scripts. - v1.9 Phase 19
- [x] Review affected skills for stable public interfaces, discoverable artifact contracts, and clear post-split ownership before accepting the refactor. - v1.9 Phase 19
- [x] Support strict Markdown-to-Typst conversion for the v1.10 `jiaoan-shicao` 教案 fixture through skill-local scripts. - v1.10 Phase 20
- [x] Support strict Markdown-to-Typst conversion for the v1.10 `jiaoan-jihua` 授课计划 fixture through skill-local scripts. - v1.10 Phase 21
- [x] Verify both v1.10 jiaoan outputs with strict diff, SHA-256, anti-copy inspection, phase verification files, and passed milestone audit. - v1.10 Phases 20-21

### Validated in v1.11

- [x] Define a shared calendar/scheduling contract that can infer task, activity, and lesson-plan date ranges from calendar data, first teaching day, daily hours, task/activity hours, holiday lists, and makeup teaching days. - v1.11 Phase 22
- [x] Create a new orchestration skill plan for a teaching-design package without deleting or replacing `jiaoan-jihua` or `jiaoan-shicao`. - v1.11 Phase 23
- [x] Require a teacher-reviewable Markdown intermediate before Typst/PDF generation for the integrated teaching plan and lesson-plan package. - v1.11 Phase 23
- [x] Integrate the optional end-of-term package module using existing structured data, score calculation, deterministic table artifacts, workbook, manifest, and review-gate rules. - v1.11 Phase 24
- [x] Define package outputs including split PDFs where supported and a default combined `teaching-design-package.pdf` with explicit failure/status evidence. - v1.11 Phase 24
- [x] Verify public command regression, package manifest truthfulness, runtime adapter coverage, and documentation/index discoverability for `teaching-design-package`. - v1.11 Phase 25

### Validated in v1.12

- [x] Repair `teaching-design-package` so scheduling evidence flows into lesson-plan Markdown before `jiaoan-shicao` rendering. - v1.12 Phase 26
- [x] Preserve teacher-reviewable Markdown and explicit review markers while filling inferred `起止日期` values. - v1.12 Phase 26
- [x] Repair `jiaoan-shicao` teaching-activity table column widths using official-template evidence from the locally downloaded reference files. - v1.12 Phase 27
- [x] Verify generated Markdown, Typst, and PDF outputs for the integrated package and affected jiaoan skill, including filled date checks and official table-width invariants. - v1.12 Phases 26-27
- [x] Keep `teaching-design-package`, `jiaoan-shicao`, `jiaoan-jihua`, and `end-of-term-teaching-materials` public interfaces stable. - v1.12 Phases 26-27

### Validated in v1.13

- [x] Use `skills/teaching-design-package/templates/teaching-design-package-full.md` as the integrated package Markdown baseline while preserving its teacher-facing structure. - v1.13 Phase 28
- [x] Generate a copyable package Markdown artifact and package Typst artifact from that single Markdown source. - v1.13 Phase 28
- [x] Preserve the semantic split between授课进度计划 and教学设计方案 in the pre-v1.14 rendering path. - v1.13 Phase 28
- [x] Derive total hours, task hours, lesson-plan activity hours, task date ranges, and academic year/semester from baseline rows, `first_teaching_day`, built-in calendar/default contracts, and generated evidence. - v1.13 Phases 28-29
- [x] Generate the final three PDFs: combined teaching-design package, teaching-plan, and lesson-plan PDFs. - v1.13 Phase 29
- [x] Verify split package outputs against legacy standalone comparison evidence while preserving legacy public interfaces. - v1.13 Phase 29
- [x] Keep machine defaults and validation/output settings out of teacher-maintained package YAML. - v1.13 Phases 28-29

### Validated in v1.14

- [x] `teaching-design-package` can be installed and used as a single skill without requiring users to install sibling repository skills. - v1.14 Phase 30
- [x] Package capability is implemented through `teaching-design-package`'s own unified data model, Markdown contract, validation rules, and Typst/PDF rendering path. - v1.14 Phase 30
- [x] Runtime adapter notes for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent explain the standalone install/use boundary. - v1.14 Phase 30
- [x] The canonical skill entry describes the teacher's real interactive workflow: ingest many source materials, ask or clarify missing facts, organize content, and produce one editable full-package Markdown. - v1.14 Phase 31
- [x] `teaching-design-package-full.md` or a course-specific Markdown file is the human-editable source of truth before rendering. - v1.14 Phase 31
- [x] The script entry is a strict final-render gate that accepts finalized Markdown rather than acting as the teacher's interactive organization entry. - v1.14 Phase 31
- [x] Default delivery emits the clean 1+1+3 artifact set only: one unified Markdown, one unified Typst, and three PDFs. - v1.14 Phase 32
- [x] Package-owned diagnostics, manifests, logs, status sidecars, split render intermediates, and similar implementation artifacts stay out of the default delivery directory except in hidden work/debug locations or explicit failure diagnostics. - v1.14 Phase 32
- [x] Scheduling evidence remains derived and mutually verified across plan and lesson-plan data, including hours, academic year/semester, first teaching day, and real teaching-day date ranges. - v1.14 Phase 32
- [x] The unified package user experience does not regress into instructing users to run or mentally stitch together old standalone skills, while legacy standalone entries remain preserved only as external compatibility surfaces. - v1.14 Phase 31

### Validated in v1.15

- [x] `teaching-design-package` uses `skills/teaching-design-package/templates/teaching-design-package-full.md` as the single structured Markdown source for module extraction and final rendering. - v1.15 Phase 33
- [x] Package internals generate hidden module Markdown and Typst for `teaching-plan` and `teaching-design` through an extensible module registry. - v1.15 Phase 33
- [x] Public delivery follows the course-name-prefixed `1 + 1 + N` contract and does not expose `.typ`, module intermediates, status, model, diagnostics, logs, or calendar resources. - v1.15 Phase 36
- [x] The package owns migrated rendering rules equivalent to the accepted `jiaoan-jihua` and `jiaoan-shicao` formal outputs while preserving those legacy skills as standalone external surfaces. - v1.15 Phases 34-35
- [x] YAML conversion, scheduling, hour totals, activity mapping, date ranges, and validation failures are derived by one shared scheduling model and recorded in hidden evidence. - v1.15 Phases 33-35
- [x] Module PDFs and the merged package PDF are generated only from successful real module renders, with honest non-zero failures on missing/invalid inputs. - v1.15 Phase 36

### Validated in v1.16

- [x] Create the `调课单` skill as a Markdown-first document workflow with a canonical `SKILL.md`, support references, templates, scripts, and fixtures. - v1.16 Phases 37-40
- [x] Establish the final form appearance by hand-authoring a Typst reference before automating conversion. - v1.16 Phase 37
- [x] Establish a teacher-reviewable Markdown source that can be converted into the Typst reference without requiring users to edit Typst directly. - v1.16 Phase 38
- [x] Implement skill-local Markdown-to-Typst and PDF generation without runtime dependency on other skill scripts. - v1.16 Phases 39-40
- [x] Document the skill's missing-information questions so agents ask for required adjustment-form facts before rendering. - v1.16 Phase 40

### Validated in v1.17 (Phases 41-44)

- [x] Establish a standardized, machine-mappable PPTX template from the supplied human-friendly `.potx` visual sample before automating rendering. - v1.17 Phase 41
- [x] Establish the accepted Markdown formatter and slide-block contract before treating script output as final. - v1.17 Phase 42
- [x] Implement Markdown-to-PPTX generation with editable native objects, deterministic logical-slide pagination, speaker notes, and strict template-slot behavior. - v1.17 Phase 43
- [x] Verify fixed 8/6/21 registries, six-runtime documentation, and hash-bound WPS viewer UAT with 10/10 human checks passed. - v1.17 Phase 44

### Validated in v1.18 (Phase 45)

- [x] Standardize clean delivery-root contracts across all six current file-writing skills. - v1.18 Phase 45
- [x] Implement candidate staging, minimal verification, complete-set history archival, and handled failure cleanup without claiming multi-file hard atomicity. - v1.18 Phase 45
- [x] Preserve existing public commands, accepted source formats, and final artifact behavior while changing delivery-directory management. - v1.18 Phase 45
- [x] Document and verify the standardized contract across all six supported runtimes. - v1.18 Phase 45
- [x] Provide a confirmation-gated reusable workflow for organizing historical agent-created output clutter. - v1.18 Phase 45

### Active

- [ ] 新建面向电气、机电、智能制造、发电厂与新能源方向大专毕业生的高级简历生成技能。
- [ ] 建立主题无关的简历 Markdown schema、可扩展主题契约和纯 CLI 批量渲染接口。
- [ ] 生成可打印的 Markdown、Typst、PDF 三件套，并保证 1/2 页 A4 的可读性和分页完整性。
- [ ] 支持通用版、多个单位/岗位定向版、照片/无照片版与透明的资格缺口提示。

### Out of Scope

- Direct one-step source-to-target rendering without Markdown intermediate - it makes target output harder to reason about and verify.
- PPTX, Keynote, and fully editable PowerPoint export for the school presentation skill - prior attempts were too unstable, so v1.5 is HTML-first.
- Arbitrary PPT template marketplace support for `school-pptx` - v1.17 starts from a controlled standard template derived from the supplied school visual sample.
- Markdown-controlled coordinates, fonts, colors, and freeform styling for `school-pptx` - strict template consistency requires fixed slots and theme-controlled layout behavior.
- Complex object animation for `school-pptx` - v1.17 only allows no animation or a reliably preserved/generated 0.5s smooth slide transition.
- Whole-slide screenshot rendering as a PPTX shortcut - `school-pptx` must produce editable PowerPoint objects where supported.
- Hosted deployment, password-gated sharing, and multi-device synchronization - defer until the offline HTML deck and presenter-local tooling are stable.
- PPTX, Keynote, and fully editable PowerPoint export for the school presentation skill - prior attempts were too unstable, so the active presentation line remains HTML-first.
- Cropping user images to fill decorative frames - images should keep their original aspect ratio and use contain-style placement by default.
- OCR, handwriting interpretation, and arbitrary school-template marketplace support - not part of the first school-presentation slice.
- Arbitrary form discovery, OCR extraction, and uncontrolled spreadsheet scraping for the end-of-term skill - v1.7 starts from explicit structured data and fixed templates.
- Generic office-suite automation, freeform template marketplace support, and one-step data-to-PDF generation without a Markdown checkpoint - these would weaken the reviewable workflow.
- Example-heavy showcase expansions - still deferred; the canonical skill path stays primary until a concrete contributor need appears.

## Context

This is a greenfield repository initialized in `/Users/mrered/Developer/Presto-Agent-Skills`. The project is now ready to serve as a shared home for agent skills that can be consumed by different agent ecosystems without locking the author into one provider-specific syntax.

v1.0 shipped 3 phases and 3 plans:

- Phase 1 established the contributor-facing repository contract, directory responsibilities, agent rules, and GSD baseline.
- Phase 2 made `templates/skill/SKILL.md` the canonical copyable artifact and documented runtime compatibility for all six required runtimes.
- Phase 3 removed unused examples and standalone adapter files, keeping examples optional until they solve a real contributor need.

v1.2 adds the first concrete skill using that pattern: `skills/gongwen`, backed by a Presto gongwen renderer and Typst PDF verification. v1.3 adds the second concrete skill, `skills/jiaoan-shicao`, backed by a Presto jiaoan-shicao renderer, calendar support resource, and Typst PDF verification. v1.4 adds `skills/jiaoan-jihua`, backed by the Presto jiaoan-jihua renderer and Typst/PDF verification.

v1.5 added `skills/school-presentation`, backed by extracted official-school visual assets and a Markdown-to-HTML presentation renderer. The milestone deliberately avoids PPTX generation and treats HTML as the primary stable output. v1.6 added playback and classroom interaction controls to that HTML deck.

v1.7 shipped a concrete document workflow skill for end-of-term teaching-materials submission. It reuses the proven data/Markdown/Typst/PDF shape from `gongwen`, `jiaoan-shicao`, and `jiaoan-jihua`, but targets a package of fixed-template documents, deterministic tables, and workbook output rather than a single document type.

v1.8 completed the official-school presentation continuation path from v1.5 and v1.6. It closed the Phase 10 deferred scope through scoped Markdown/rendering/playback capabilities: playback-local presenter markup, peek and sorting exercises, restrained body animation, SmartArt/timeline/cards/gallery-style layout helpers, semantic icons, section controls, print/export review behavior, and one-click final PDF export. The milestone kept freeform HTML editing, hosted collaboration, and office-suite automation out of scope.

v1.9 shipped the first decomposition pass for the current skill system. Some entry files and scripts had grown too heavy for the progressive-disclosure model, so the milestone slimmed current entries, moved long support material into references, split `school-presentation.sh`, `end-of-term-teaching-materials/scripts/render_package.py`, and `gongwen.sh` behind stable public entry points, and updated repository guidance for future skill authors.

v1.10 shipped strict jiaoan fixture conversion. `skills/jiaoan-shicao` and `skills/jiaoan-jihua` now generate the two committed `test/1.10/` Typst targets from Markdown through skill-local script code only. Both flows preserve public commands, use the target Typst only for generated-output comparison, and record clean diff/hash evidence in phase verification artifacts plus the passed milestone audit.

v1.11 shipped the integrated teaching-design package line. Local research confirmed that the current `jiaoan-jihua` script already consumes `calendar.json`, `first_teaching_day`, `daily_hours`, and per-content hours to derive week numbers, weekdays, and hour consumption. The milestone turned that proven local behavior into a shared scheduling contract, added a `teaching-design-package` orchestration skill, and layered teaching-plan, practical lesson-plan, and optional end-of-term artifacts behind reviewable Markdown and deterministic output gates.

Phase 24 completed the optional end-of-term and package-output slice: `teaching-design-package` now delegates end-of-term module internals to `end-of-term-teaching-materials`, exposes module artifact pointers in the package manifest, preserves module-local review gates, and records split/combined PDF status truthfully.

v1.12 completed the post-close repair slice for the integrated teaching-design package. Phase 26 backfilled concrete package scheduling evidence into generated practical lesson-plan Markdown while preserving review-marker gates. Phase 27 aligned `jiaoan-shicao` activity-table widths with official-template evidence using chapter/pagebreak-scoped column grouping and verified the direct and package paths with Markdown, Typst, and PDF artifacts.

v1.13 shipped from the committed Markdown baseline `skills/teaching-design-package/templates/teaching-design-package-full.md` rather than a new Markdown schema. The reference Markdown format stays teacher-facing and copyable, while the pre-v1.14 package render path consumes that Markdown and produces split and combined outputs.

v1.17 starts a new PPTX skill line rather than reopening `school-presentation`. The new `school-pptx` milestone targets editable PowerPoint output from a fixed school template: first hand-normalize the supplied `.potx` visual sample into a standard template, then hand-author the Markdown fixture, then implement the renderer and verification gate. The Markdown surface is intentionally constrained to YAML metadata and explicit slide blocks so the template, not the input document, owns coordinates, typography, theme behavior, overflow rules, and layout consistency.

v1.14 shipped the corrected `teaching-design-package` boundary. The package now owns its normal rendering path instead of relying on sibling skills, the skill entry starts with teacher source-material organization before scripts, and the default successful output directory is exactly the public 1+1+3 set. Derived scheduling facts and PDF readiness are validated from evidence, while status/model/logs/split Typst and failure diagnostics stay hidden.

v1.15 tightened that package-owned output model. The unified Markdown remains teacher-readable and script-parseable, while the renderer now splits it into package-owned module intermediates, uses migrated formal jiaoan rendering rules inside `teaching-design-package`, derives all time and hour facts through one scheduling model, and publishes only course-name-prefixed Markdown/PDF deliverables.

v1.16 added the `调课单` skill to the document workflow family. It preserves the build order of accepted Typst surface first, teacher-readable Markdown second, and script automation after that contract is stable. The shipped skill is standalone inside `skills/tiaokedan/`, keeps diagnostics hidden from clean output, and asks concise clarification questions before final rendering when source facts are missing.

## Next Milestone Goals

v1.19 聚焦毕业生高级简历生成器；阶段编号从 Phase 46 继续。

## Constraints
- **Runtime compatibility**: OpenClaw and Hermes Agent must remain represented in skill authoring guidance - they are required targets.
- **Source of truth**: Prefer one canonical skill source plus embedded runtime adapter notes - this reduces drift across agents.
- **Scope discipline**: Keep the document workflow centered on a Markdown intermediate; add automation only after the contract is stable.
- **Presentation output discipline**: For v1.5, HTML is the primary output. PPTX and Keynote export are future options, not current acceptance criteria.
- **Layout discipline**: Markdown owns logical slide content; the renderer owns physical pagination, text fitting, and overflow handling.
- **Interaction discipline**: Markdown may describe interaction intent such as reveal order, emphasis, and answer masks, while the renderer owns the concrete playback state and animation timing.
- **Annotation discipline**: Presenter annotations should not mutate the Markdown intermediate, manifest hierarchy, or deterministic review output unless a future phase explicitly introduces saved markup artifacts.
- **Fixed-template discipline**: The end-of-term skill should implement named submission templates, not infer arbitrary form structures.
- **Data checkpoint discipline**: Structured data and Markdown must remain inspectable before Typst/PDF generation; avoid invisible one-step conversions.
- **Language**: Agent-facing responses in this repository should be Simplified Chinese unless a file format or downstream runtime requires otherwise.
- **Portability**: Avoid assuming one agent's proprietary tool syntax in the canonical skill body; isolate those differences in adapter sections.
- **Entry weight**: `SKILL.md` should remain the semantic entry point, not a full reference manual; move long format rules, examples, and renderer details into skill-local references.
- **Behavior compatibility**: Script decomposition must not rename existing commands, flags, output paths, manifest fields, or accepted input contracts unless a requirement explicitly says so.
- **Integrated package discipline**: The v1.11 package skill must compose existing teaching skills through stable contracts; it must not silently delete or replace their canonical entries.
- **Scheduling evidence discipline**: Inferred dates must be accompanied by reviewable inputs and hour-consumption evidence so teachers can audit why a task or activity received a date range.
- **Post-close repair discipline**: v1.12 may repair shipped behavior after v1.11, but must not reframe this as a new replacement skill or delete original teaching skills.
- **Official template evidence**: `jiaoan-shicao` table-width repair must cite or reproduce evidence from the downloaded official `jiaoan-shicao` reference files before claiming alignment.
- **Regression artifact discipline**: Post-close repair milestones are not done until generated Markdown, Typst, and PDF artifacts prove the repaired behavior and preserve public command compatibility.
- **Markdown baseline discipline**: v1.13 implementation must adapt rendering around `skills/teaching-design-package/templates/teaching-design-package-full.md`; it must not require changing the teacher-facing Markdown reference format to satisfy renderer internals.
- **Derived scheduling discipline**: v1.13 must calculate hours, lesson activity durations, date ranges, academic year/semester, and default rendering behavior from the baseline teaching-plan rows, `first_teaching_day`, built-in calendar/default contracts, and generated evidence rather than duplicating those facts in teacher-maintained YAML or body fields.
- **Standalone teaching-skill discipline**: Legacy teaching skills must stay usable on their own with stable public interfaces, but they are not `teaching-design-package` internals, package resources, acceptance baselines, or future implementation direction.
- **v1.14 standalone package discipline**: `teaching-design-package` must be installable and usable as one skill; users must not be required to install sibling repo directories, and required package capability must be rebuilt through the package's own unified model, Markdown contract, validation, and Typst/PDF rendering path.
- **v1.14 teacher workflow discipline**: The canonical skill body must implement the teacher-facing source-materials-to-full-Markdown workflow, not merely point users at a renderer script.
- **v1.14 script boundary discipline**: Scripts consume finalized `teaching-design-package-full.md` for contract validation and delivery generation only; they are not the interactive content-organization entry.
- **v1.14 delivery discipline**: Default output directories must contain only the 1+1+3 delivery set: unified Markdown, unified Typst, combined package PDF, teaching-plan PDF, and lesson-plan PDF.
- **v1.14 diagnostic discipline**: Package-owned manifests, stderr logs, status files, split render intermediates, and similar artifacts belong in hidden work directories, temporary directories, debug mode, or failure diagnostics, not the default delivery directory.
- **v1.15 public delivery discipline**: Successful package output directories must contain only course-name-prefixed public artifacts: `课程名教学资料.md`, `课程名教学资料.pdf`, `课程名授课进度计划表.pdf`, `课程名教学设计方案.pdf`, and future `课程名<模块名>.pdf` files.
- **v1.15 hidden module discipline**: Module Markdown, module Typst, scheduling model, status, diagnostics, logs, and calendar evidence belong under hidden `.teaching-design-package/` paths and must not leak into successful public delivery roots.
- **v1.15 legacy-format discipline**: Legacy `jiaoan-jihua` and `jiaoan-shicao` skills may be used as format baselines and test oracles, but the package must not depend on them at runtime.
- **v1.15 scheduling discipline**: Calendar, academic year/semester, course/task date ranges, week/day labels, daily hour consumption, total hours, and activity hours must come from one package-owned scheduling model using `calendar.json`, `first_teaching_day`, and teaching-plan rows.
- **v1.15 failure discipline**: Missing calendar dates, range gaps, hour mismatches, task/activity mapping mismatches, failed module renders, or failed PDF merges must produce non-zero failure and hidden diagnostics rather than partial success output.
- **v1.16 hand-authored baseline discipline**: The `调课单` milestone must establish the accepted Typst and Markdown fixtures before treating script output as final.
- **v1.16 independence discipline**: The `调课单` renderer may reuse implementation ideas from existing document skills, but runtime execution must remain inside `skills/tiaokedan/` and must not call sibling skill scripts.
- **v1.16 clarification discipline**: When required adjustment-form fields are missing, the skill must ask concise teacher-facing questions before generating final artifacts.
- **v1.17 template-first discipline**: The `school-pptx` milestone must establish the standardized PPTX template before treating Markdown parsing or script output as final.
- **v1.17 Markdown contract discipline**: The accepted Markdown fixture must define YAML metadata, automatic `##`-based contents, explicit slide blocks, and logical-slide pagination behavior before renderer implementation.
- **v1.17 editability discipline**: Generated PPTX output must favor editable PowerPoint objects and must not use whole-slide images as a shortcut for template fidelity.
- **v1.18 clean-delivery discipline**: File-writing skills must generate and minimally verify complete candidates before current mutation, compare exact path-set+bytes for no-op, archive replaced bundles together, and fail closed on unknown or symlink states.
- **v1.18 rollback boundary**: Portable guarantees cover tested handled failure, INT, and TERM rollback; they do not claim SIGKILL, power-loss, filesystem-corruption, or multi-file hard atomicity.
- **v1.18 evidence discipline**: Central milestone gates must derive counts from parsed skill-local regression evidence; a successful no-op command or missing gate marker must fail strict verification.
- **v1.19 shared-schema discipline**: 简历内容 schema 必须与主题、页面密度和照片位置解耦；新增模板不得要求重写学生资料 Markdown。
- **v1.19 CLI discipline**: 已标准化资料的验证、定向、批量生成与 PDF 渲染必须只依赖 CLI，不消耗 AI token；AI 仅可用于可选的资料整理模式。
- **v1.19 pagination discipline**: 两页简历不得出现孤立标题、被拆开的经历条目或无标题的续接内容；无法同时满足页面、可读性和模块完整性时必须失败关闭。

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use a canonical `SKILL.md` plus runtime adapter guidance | Best balance between portability and practical runtime differences; avoids maintaining six divergent skill definitions | Good - shipped in v1.0 |
| Support Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent from v1 | User explicitly requires broad agent compatibility and mandatory OpenClaw/Hermes support | Good - documented in v1.0 |
| Start with docs, templates, and planning first, without v1 examples | User wants the canonical skill contract first; example material is deferred until it has concrete contributor value | Good - v1.0 removed unused examples |
| Use Markdown as the canonical intermediate for document workflows | Gives the skill family one stable semantic layer before target output | Good - shipped in v1.1 and reused in v1.2/v1.3 |
| Keep v1.1 focused on the Markdown intermediate rather than output-specific phases | The user clarified that output-specific follow-up phases are not the right focus | Updated |
| Add `gongwen` as the first real skill | User provided a concrete Presto gongwen fixture and requested a trigger for similar official-document writing | Good - shipped in v1.2 Phase 5 |
| Add `jiaoan-shicao` as the second real skill | User provided a Presto jiaoan-shicao fixture, `calendar.json`, and requested the trigger word for practical lesson-plan writing | Good - shipped in v1.3 Phase 6 |
| Add `jiaoan-jihua` as a授课进度计划 skill | User provided a Presto jiaoan-jihua fixture, `calendar.json`, and requested the trigger word for teaching-schedule writing | Good - shipped in v1.4 Phase 7 |
| Add `school-presentation` as a school-style HTML presentation skill | User rejected unstable PPTX output and prefers Markdown-controlled, single-file HTML presentations with fixed layouts and school visual identity | Good - shipped in v1.5 Phase 8 |
| Treat logical slides and physical pages separately | Users should edit one Markdown logical slide while the renderer splits overflow into additional HTML pages automatically | Good - shipped in v1.5 Phase 8 |
| Defer marking and annotation tools from playback UX | The current milestone should focus on slide playback, preview, hierarchy, reveals, and answer masks before adding presenter markup controls | Good - shipped in v1.6 |
| Resume `school-presentation` with deferred interaction and delivery features in v1.8 | The Phase 10 deferred scope was the user's requested continuation path, and the v1.6 playback base had passed visual UAT | Good - shipped in v1.8 |
| Keep presenter markup playback-local | Saved annotations would mutate the Markdown source and deterministic review artifacts, while the accepted v1.8 scope was live delivery support | Good - shipped in v1.8 Phase 14 |
| Keep structured classroom syntax teacher-facing | `peek`, `timeline`, `cards`, `gallery`, and `smartart` are easier to edit and review than raw HTML or internal renderer names | Good - shipped in v1.8 Phase 15 |
| Add one-click final PDF export inside the generated deck | Browser print alone could not reliably produce the accepted final artifact with outline/bookmarks and agenda links | Good - shipped in v1.8 Phase 16 |
| Add an end-of-term teaching-materials skill | User requested a new skill for fixed-template teaching documents and tables submitted at semester end | Good - shipped in v1.7 |
| Use data to Markdown to Typst to PDF for v1.7 | This preserves the repository's reviewable Markdown-first document workflow while supporting fixed templates and verification | Good - shipped in v1.7 |
| Skip external research for v1.7 planning | The target follows already validated local document-skill patterns, so requirements can be defined from project context and the user's confirmed scope | Good - shipped in v1.7 |
| Keep uncertain scores reviewable before final export | The audit found that `87?` must reach Markdown review while final delivery stays strict | Good - closed in v1.7 Phase 13 |
| Start v1.9 as a structure milestone | Current skill entries and scripts are increasingly heavy, so the next value is lowering default reading and edit cost while keeping the skill interface stable | Good - shipped in v1.9 |
| Preserve command surfaces during decomposition | Users and future agents rely on the current commands, generated artifacts, and invocation patterns | Good - shipped in v1.9 |
| Keep decomposition support files discoverable | Progressive disclosure only works if contributors can reliably find templates, references, artifact contracts, and scripts from the entry docs | Good - shipped in v1.9 |
| Start v1.10 as a strict jiaoan Typst conversion milestone | User provided two concrete Markdown and Typst fixture pairs and requested script-only 1:1 conversion through the existing jiaoan skills | Good - shipped in v1.10 |
| Keep v1.10 conversion fixture-scoped and skill-local | The milestone acceptance was strict 1:1 fixture equivalence, not a shared jiaoan rendering framework | Good - shipped in v1.10 |
| Start v1.11 as a new orchestration skill milestone | User wants plan and lesson-plan integration plus optional end-of-term outputs, while preserving the original skills | Good - shipped across Phases 22-25 |
| Treat jiaoan-jihua scheduling as reusable evidence, not final shared API | Existing local code proves the derivation is feasible, but a package-level contract and fixtures are needed before broad reuse | Good - Phase 22 created the shared contract and fixture evidence |
| Keep the integrated package Markdown-first | Teachers need a reviewable intermediate before Typst/PDF and workbook generation across the combined workflow | Good - Phase 23 created the package checkpoint and Phase 24 preserved module review gates |
| Keep package final-ready status tied to actual artifact evidence | Split Typst output alone should not imply a complete combined PDF package | Good - Phase 24 and Phase 25 verified honest manifest behavior |
| Start v1.12 as a post-close repair milestone | The user reported two shipped-behavior bugs after v1.11: missing lesson-plan `起止日期` backfill and `jiaoan-shicao` activity-table width mismatch | Good - shipped in v1.12 |
| Keep date backfill package-local | The repair only needed concrete package scheduling evidence and review-marker gating, not a new shared scheduling library | Good - shipped in v1.12 Phase 26 |
| Use official `jiaoan-shicao` reference snapshots as layout evidence | The table-width bug depends on official template behavior, not a subjective visual tweak | Good - shipped in v1.12 Phase 27 |
| Treat activity-table widths as chapter/pagebreak-scoped | Official evidence showed shared same-chapter column specs and `{pagebreak}` as a recalculation boundary | Good - shipped in v1.12 Phase 27 |
| Start v1.13 from the committed full-package Markdown template | The user corrected scope so the Markdown reference format remains the baseline and implementation adapts around rendering it | Good - shipped in v1.13 Phase 28 |
| Keep old jiaoan skills standalone during the pre-v1.14 package line | The v1.13 work preserved their direct use and public command contracts while recording comparison evidence | Superseded by v1.14 package-owned boundary |
| Keep package PDF generation explicit | Typst generation alone should not be confused with final accepted PDFs | Good - v1.13 Phase 29 added `render-package --pdf` |
| Merge combined package PDFs from accepted split outputs | The combined package should be file-backed and ordered from the teaching-plan and lesson-plan PDFs | Good - v1.13 Phase 29 records `python_fitz` fallback evidence |
| Rebuild `teaching-design-package` as its own two-in-one skill | User clarified the package must not copy old templates, keep old internal Markdown files, or continue old handoff thinking under a new folder | Good - shipped in v1.14 |
| Keep the package workflow teacher-first and script-finalized | Teachers should organize source materials into one editable Markdown before strict validation/rendering runs | Good - shipped in v1.14 |
| Keep successful package delivery roots clean | Default output should contain only one Markdown, one Typst, and three PDFs, with diagnostics hidden for audit/debug/failure use | Good - shipped in v1.14 |
| Start v1.15 as modular package rendering with legacy formal-format regression | User confirmed the package must derive hidden module Markdown/Typst and formal module PDFs from one unified Markdown source | Good - shipped in v1.15 |
| Treat old jiaoan skills as format baselines, not runtime dependencies | Package rendering must be standalone while proving migrated rules match or are equivalent to accepted old outputs | Good - shipped in v1.15 |
| Start v1.16 as a new `调课单` skill milestone | User requested a new skill whose build order is hand-authored Typst, hand-authored Markdown, independent conversion script, then PDF workflow and clarification questions | Good - shipped in v1.16 |
| Use one scheduling model for both modules | Calendar and hour facts must not be calculated independently by the two modules | Good - shipped in v1.15 |
| Start v1.17 as `school-pptx` with template-first build order | User requested a school-template Markdown-to-PPTX skill and explicitly set the build order as standard template, standard Markdown, then script | Good - Phases 41-42 established the controlled template and accepted Markdown boundary |
| Treat `theme` as a controlled standard-template identifier | Future `.potx` templates may exist, but Markdown must not control styling or layout details directly | Good - `standard-school` is manifest-controlled and arbitrary styling is rejected |
| Keep `school-pptx` output editable instead of screenshot-based | The value of the skill is template-consistent PPTX that can still be edited in PowerPoint | Good - Phase 43 emits native editable text, tables, pictures, groups, and notes |
| Standardize all writing skills on explicit managed bundles | Root cleanliness, revision history, and failure safety need one semantic contract without creating cross-skill runtime dependencies | Good - v1.18 shipped skill-local candidate/no-op/history/rollback implementations for all six skills |
| Bind central verification to real regression evidence | Required/called counts are meaningful only when stable output markers and fault registries prove the underlying public CLI tests ran | Good - v1.18 audit gap closure rejects no-op replacement and deleted gate evidence |
| Keep historical cleanup confirmation-gated | Unknown files and user materials cannot be classified safely by normal render commands | Good - v1.18 provides snapshot-bound audit/approval semantics and a test-only executable protocol fixture |
| Build the graduate-resume skill as a shared-schema CLI renderer with optional AI intake | It enables zero-token batch generation while retaining a practical path from scattered student materials to standardized input | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

After each phase transition:
1. Requirements invalidated? Move to Out of Scope with reason.
2. Requirements validated? Move to Validated with phase reference.
3. New requirements emerged? Add to Active.
4. Decisions to log? Add to Key Decisions.
5. "What This Is" still accurate? Update if drifted.

After each milestone:
1. Full review of all sections.
2. Core Value check - still the right priority?
3. Audit Out of Scope - reasons still valid?
4. Update Context with current state.

---
*Last updated: 2026-07-17 after starting milestone v1.19*
