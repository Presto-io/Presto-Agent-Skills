# Presto Agent Skills

## Current Milestone: v1.1 Document Workflow

**Goal:** Define a markdown-first document workflow skill family that normalizes arbitrary source material into Markdown and then renders Typst or HTML with clear target-specific rules.

**Target features:**
- Markdown normalization as the shared intermediate representation
- Typst output with hard constraint handling and explicit rejection/rewrite rules
- Semantic HTML output and verification from the same Markdown source

## Current State

v1.0 shipped on 2026-05-30. The repository now has a documentation-first portable skill framework: contributor entry docs, directory ownership rules, project agent instructions, a canonical `SKILL.md` template, runtime adapter notes inside that template, and a compatibility matrix covering Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.

v1.1 is now being scoped around a document workflow pattern: normalize any input into Markdown first, then render to Typst or HTML from that shared intermediate.

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

### Active

- [ ] Define a Markdown-first normalization contract for arbitrary document input.
- [ ] Define hard Typst output constraints and the handling rules for unsupported constructs.
- [ ] Define semantic HTML output and verification rules from the shared Markdown source.

### Out of Scope

- Direct one-step source-to-target rendering without Markdown intermediate - it makes cross-format behavior harder to reason about and verify.
- PDF generation, page templating, and layout-polish automation - defer until the core Markdown/Typst/HTML contract is stable.
- OCR, image extraction, and handwriting interpretation - not part of the first document workflow slice.
- Example-heavy showcase expansions - still deferred; the canonical skill path stays primary until a concrete contributor need appears.

## Context

This is a greenfield repository initialized in `/Users/mrered/Developer/Presto-Agent-Skills`. The project is now ready to serve as a shared home for agent skills that can be consumed by different agent ecosystems without locking the author into one vendor's syntax.

v1.0 shipped 3 phases and 3 plans:

- Phase 1 established the contributor-facing repository contract, directory responsibilities, agent rules, and GSD baseline.
- Phase 2 made `templates/skill/SKILL.md` the canonical copyable artifact and documented runtime compatibility for all six required runtimes.
- Phase 3 removed unused examples and standalone adapter files, keeping examples optional until they solve a real contributor need.

v1.1 is expected to focus on document-workflow skills that treat Markdown as the canonical intermediate representation before Typst or HTML output.

## Next Milestone Goals

The next milestone should start with `/gsd:new-milestone` and a fresh requirements pass. The current focus is a markdown-first document workflow with strict Typst constraints and semantic HTML output, not scaffold tooling or example expansion.

## Constraints

- **Runtime compatibility**: OpenClaw and Hermes Agent must remain represented in skill authoring guidance - they are required targets.
- **Source of truth**: Prefer one canonical skill source plus embedded runtime adapter notes - this reduces drift across agents.
- **Scope discipline**: Keep the document workflow centered on a Markdown intermediate; add automation only after the transform contract is stable.
- **Typst safety**: Hard Typst constraints must be explicit, documented, and enforced in output rules rather than left to ad hoc judgment.
- **Language**: Agent-facing responses in this repository should be Simplified Chinese unless a file format or downstream runtime requires otherwise.
- **Portability**: Avoid assuming one agent's proprietary tool syntax in the canonical skill body; isolate those differences in adapter sections.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use a canonical `SKILL.md` plus runtime adapter guidance | Best balance between portability and practical runtime differences; avoids maintaining six divergent skill definitions | Good - shipped in v1.0 |
| Support Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent from v1 | User explicitly requires broad agent compatibility and mandatory OpenClaw/Hermes support | Good - documented in v1.0 |
| Start with docs, templates, and planning first, without v1 examples | User wants the canonical skill contract first; example material is deferred until it has concrete contributor value | Good - v1.0 removed unused examples |
| Use Markdown as the canonical intermediate for document workflows | Gives the skill family one stable semantic layer before Typst or HTML output | Pending |
| Treat Typst hard limits as explicit transformation rules | Prevents invalid Typst output and makes unsupported constructs visible early | Pending |

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
*Last updated: 2026-05-31 after v1.1 milestone definition*
