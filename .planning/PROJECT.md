# Presto Agent Skills

## What This Is

Presto Agent Skills is a portable skill repository for authoring agent skills once and adapting them across multiple AI agent runtimes. The initial targets are Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent, with OpenClaw and Hermes Agent treated as mandatory first-class compatibility targets.

The repository starts as a documentation-first framework: canonical skill templates, runtime adapter guidance, optional example references, and project instructions that different agents can read without guessing the repository contract.

## Core Value

A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## Requirements

### Validated

(None yet - ship to validate)

### Active

- [ ] Define a clear repository structure for skills, templates, adapters, examples, and GSD planning files.
- [ ] Provide a canonical `SKILL.md` authoring template that can serve as the single source of truth.
- [ ] Document adapter expectations for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
- [ ] Treat OpenClaw and Hermes Agent as mandatory supported runtimes, not optional future targets.
- [ ] Add project-level agent instructions through `AGENTS.md`, including the Simplified Chinese response requirement.
- [ ] Keep examples optional and brief so they support the canonical template without becoming a v1 requirement.

### Out of Scope

- Automated scaffold CLI - useful later, but v1 focuses on stable repository shape and human-readable contracts.
- Schema validation and lint scripts - deferred until the canonical format settles.
- Publishing or package-manager distribution - premature before the canonical contract and compatibility docs are proven useful.
- Full runtime execution test harnesses - requires per-runtime environments and should follow after the compatibility contract is stable.
- Example-heavy showcase expansions - deferred; v1 keeps `templates/skill/SKILL.md` as the primary authoring path.

## Context

This is a greenfield repository initialized in `/Users/mrered/Developer/Presto-Agent-Skills`. The project should become a shared home for agent skills that can be consumed by different agent ecosystems without locking the author into one vendor's syntax.

The user selected the lean v1 scope:

- Core goal: general skill specifications and templates that different agents can read and reuse.
- Supported runtime list: Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
- Initial framework: `README`, `AGENTS.md`, skill templates, directory specification, optional example references, and GSD planning.
- First milestone completion: repository structure and GSD planning files initialized.
- Workflow defaults: YOLO mode, coarse phases, parallel execution, planning docs committed, research/checking/verification enabled, balanced model profile.

## Constraints

- **Runtime compatibility**: OpenClaw and Hermes Agent must be represented in v1 adapter docs - they are required targets.
- **Source of truth**: Prefer one canonical skill source plus runtime adapter notes or generated wrappers - this reduces drift across agents.
- **Scope discipline**: Keep v1 documentation-first; defer CLI tooling and validation until the shape is exercised.
- **Language**: Agent-facing responses in this repository should be Simplified Chinese unless a file format or downstream runtime requires otherwise.
- **Portability**: Avoid assuming one agent's proprietary tool syntax in the canonical skill body; isolate those differences in adapter sections.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use a canonical `SKILL.md` plus runtime adapter guidance | Best balance between portability and practical runtime differences; avoids maintaining six divergent skill definitions | - Pending |
| Support Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent from v1 | User explicitly requires broad agent compatibility and mandatory OpenClaw/Hermes support | - Pending |
| Start with docs, templates, and planning first, with examples optional | User wants the canonical skill contract first; example material should stay lightweight and non-normative | - Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check - still the right priority?
3. Audit Out of Scope - reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-30 after initialization*
