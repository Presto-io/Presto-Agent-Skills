# Presto Agent Skills

## Current State

**Latest shipped milestone:** v1.11 Integrated Teaching Design Package

**Shipped:** 2026-06-14

**Active milestone:** None

**Status:** v1.11 is complete and archived; the project is waiting for the next milestone definition.

**Delivered in v1.11:**
- `teaching-design-package` now has a portable orchestration skill entry, package Markdown checkpoint, scheduling evidence contract, jiaoan module handoff, optional end-of-term module pointers, and split/combined output status semantics.
- The original `jiaoan-jihua`, `jiaoan-shicao`, and `end-of-term-teaching-materials` skills remain standalone and callable.
- The milestone audit passed with 16/16 requirements covered across Phases 22-25.

## Milestone History

v1.0 shipped on 2026-05-30. The repository now has a documentation-first portable skill framework: contributor entry docs, directory ownership rules, project agent instructions, a canonical `SKILL.md` template, runtime adapter notes inside that template, and a compatibility matrix covering Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.

v1.2 shipped the first real skill built on the document workflow pattern: normalize class-official-document content into Markdown first, then render through the Presto gongwen Typst template and verify output artifacts. v1.3 extends that pattern to `jiaoan-shicao`; v1.4 adds `jiaoan-jihua` for授课进度计划表. v1.5 shipped `school-presentation`, extending the Markdown-first control surface to school-style offline HTML presentations. v1.6 refined that HTML output with playback, preview, hierarchy, ordered reveals, emphasis animation, and answer masks. v1.7 returns to the document workflow family with `end-of-term-teaching-materials`: structured teaching data, a reviewable Markdown checkpoint, fixed-template Typst/PDF rendering, deterministic table artifacts, workbook output, and strict final-export gates. v1.8 resumed the `school-presentation` line by implementing deferred presenter markup, classroom interaction extensions, structured layout helpers, print/export review behavior, and one-click final PDF export without reopening PPTX/Keynote output. v1.9 turned the accumulated skill system back toward progressive disclosure by slimming entries, splitting large scripts, and updating contributor guidance while preserving public behavior. v1.10 added strict, skill-local Markdown-to-Typst fixture conversion for the two jiaoan skills, with byte-for-byte verification against the committed `test/1.10/` targets. v1.11 added the integrated `teaching-design-package` orchestration path while preserving the original teaching skills and keeping package outputs honest through manifest evidence.

## What This Is

Presto Agent Skills is a portable skill repository for authoring agent skills once and adapting them across multiple AI agent runtimes. The initial targets are Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent, with OpenClaw and Hermes Agent treated as mandatory first-class compatibility targets.

The repository is currently a stable documentation-first framework. New skill work should begin from `templates/skill/SKILL.md`; runtime differences belong in that file's Runtime Adapter Notes unless a later milestone introduces generated wrappers or runtime-specific packaging.

## Core Value

A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## Current Milestone

No active milestone is currently open. Start the next milestone with `/gsd:new-milestone` when ready.

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

### Active

(None - define the next milestone before adding new active requirements.)

### Out of Scope

- Direct one-step source-to-target rendering without Markdown intermediate - it makes target output harder to reason about and verify.
- PPTX, Keynote, and fully editable PowerPoint export for the school presentation skill - prior attempts were too unstable, so v1.5 is HTML-first.
- Hosted deployment, password-gated sharing, and multi-device synchronization - defer until the offline HTML deck and presenter-local tooling are stable.
- PPTX, Keynote, and fully editable PowerPoint export for the school presentation skill - prior attempts were too unstable, so the active presentation line remains HTML-first.
- Cropping user images to fill decorative frames - images should keep their original aspect ratio and use contain-style placement by default.
- OCR, handwriting interpretation, and arbitrary school-template marketplace support - not part of the first school-presentation slice.
- Arbitrary form discovery, OCR extraction, and uncontrolled spreadsheet scraping for the end-of-term skill - v1.7 starts from explicit structured data and fixed templates.
- Generic office-suite automation, freeform template marketplace support, and one-step data-to-PDF generation without a Markdown checkpoint - these would weaken the reviewable workflow.
- Example-heavy showcase expansions - still deferred; the canonical skill path stays primary until a concrete contributor need appears.

## Context

This is a greenfield repository initialized in `/Users/mrered/Developer/Presto-Agent-Skills`. The project is now ready to serve as a shared home for agent skills that can be consumed by different agent ecosystems without locking the author into one vendor's syntax.

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

## Next Milestone Goals

No next milestone has been defined yet. The next milestone should start from the current validated baseline:

- `teaching-design-package` composes existing teaching skills rather than replacing them.
- Scheduling evidence, module handoffs, output manifests, and review markers are now explicit package concepts.
- Any future rendering work should keep the package Markdown checkpoint and honest final-ready status intact.
- Public skill interfaces should remain stable unless the next milestone explicitly authorizes a breaking change.

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
*Last updated: 2026-06-14 after v1.11 milestone close*
