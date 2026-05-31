# Presto Agent Skills

## Current Milestone: v1.4 Jiaoan Jihua Skill

**Goal:** Create the next concrete document workflow skill, `jiaoan-jihua`, that produces a stable授课进度计划 Markdown intermediate and validates Typst/PDF output through the Presto jiaoan-jihua template.

**Target features:**
- `jiaoan-jihua` trigger for 授课进度计划表 writing
- `jiaoan-jihua-full.md` Markdown intermediate structure
- Scripted Markdown-to-Typst/PDF rendering, bundled calendar support resource usage, and reference artifact verification

## Current State

v1.0 shipped on 2026-05-30. The repository now has a documentation-first portable skill framework: contributor entry docs, directory ownership rules, project agent instructions, a canonical `SKILL.md` template, runtime adapter notes inside that template, and a compatibility matrix covering Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.

v1.2 shipped the first real skill built on the document workflow pattern: normalize class-official-document content into Markdown first, then render through the Presto gongwen Typst template and verify output artifacts. v1.3 extends that pattern to `jiaoan-shicao`; v1.4 now adds `jiaoan-jihua` for授课进度计划表.

## What This Is

Presto Agent Skills is a portable skill repository for authoring agent skills once and adapting them across multiple AI agent runtimes. The initial targets are Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent, with OpenClaw and Hermes Agent treated as mandatory first-class compatibility targets.

The repository is currently a stable documentation-first framework. New skill work should begin from `templates/skill/SKILL.md`; runtime differences belong in that file's Runtime Adapter Notes unless a later milestone introduces generated wrappers or runtime-specific packaging.

## Core Value

A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

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
- [x] Add the `jiaoan-jihua` skill with trigger wording, canonical workflow, script code, and black-box Typst/PDF verification path. - v1.4 Phase 7

### Active

No active follow-up phase is currently scoped. The next step is to audit or extend `jiaoan-jihua` only after a concrete new requirement appears.

### Out of Scope

- Direct one-step source-to-target rendering without Markdown intermediate - it makes target output harder to reason about and verify.
- Additional output formats beyond the Presto gongwen/jiaoan-shicao/jiaoan-jihua Typst/PDF paths - defer until a concrete new skill requires them.
- OCR, image extraction, and handwriting interpretation - not part of the first document workflow slice.
- Example-heavy showcase expansions - still deferred; the canonical skill path stays primary until a concrete contributor need appears.

## Context

This is a greenfield repository initialized in `/Users/mrered/Developer/Presto-Agent-Skills`. The project is now ready to serve as a shared home for agent skills that can be consumed by different agent ecosystems without locking the author into one vendor's syntax.

v1.0 shipped 3 phases and 3 plans:

- Phase 1 established the contributor-facing repository contract, directory responsibilities, agent rules, and GSD baseline.
- Phase 2 made `templates/skill/SKILL.md` the canonical copyable artifact and documented runtime compatibility for all six required runtimes.
- Phase 3 removed unused examples and standalone adapter files, keeping examples optional until they solve a real contributor need.

v1.2 adds the first concrete skill using that pattern: `skills/gongwen`, backed by a Presto gongwen black-box renderer and Typst PDF verification. v1.3 adds the second concrete skill, `skills/jiaoan-shicao`, backed by a Presto jiaoan-shicao black-box renderer, calendar support resource, and Typst PDF verification. v1.4 adds `skills/jiaoan-jihua`, backed by the Presto jiaoan-jihua black-box renderer and Typst/PDF verification.

## Next Milestone Goals

The next milestone should start with `/gsd:new-milestone` and a fresh requirements pass. The current skill is deliberately limited to jiaoan-jihua Markdown, Presto jiaoan-jihua Typst output, bundled calendar support resource usage, and PDF verification.

## Constraints

- **Runtime compatibility**: OpenClaw and Hermes Agent must remain represented in skill authoring guidance - they are required targets.
- **Source of truth**: Prefer one canonical skill source plus embedded runtime adapter notes - this reduces drift across agents.
- **Scope discipline**: Keep the document workflow centered on a Markdown intermediate; add automation only after the contract is stable.
- **Language**: Agent-facing responses in this repository should be Simplified Chinese unless a file format or downstream runtime requires otherwise.
- **Portability**: Avoid assuming one agent's proprietary tool syntax in the canonical skill body; isolate those differences in adapter sections.

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
*Last updated: 2026-05-31 after v1.4 jiaoan-jihua skill implementation*
