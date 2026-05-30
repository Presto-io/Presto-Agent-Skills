# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Granularity:** Coarse
**Project Mode:** MVP

## Overview

This roadmap establishes the repository as a portable agent skill framework before adding automation. The first milestone is complete when the repository structure and GSD planning files are initialized.

| Phase | Name | Goal | Requirements |
|-------|------|------|--------------|
| 1 | Repository and GSD Foundation | Create the base repository contract, project instructions, and planning structure | DOC-01, DOC-02, DOC-03, PLAN-01 |
| 2 | Canonical Skill Format and Runtime Adapters | Define the reusable skill source format and compatibility model for all target runtimes | TMPL-01, TMPL-02, RT-01, RT-02, RT-03 |
| 3 | Portable Example Skill | Add a concrete example that demonstrates the repository conventions across runtimes | EX-01, EX-02 |

## Phases

### Phase 1: Repository and GSD Foundation

**Goal:** Create the base repository contract, project instructions, and planning structure.
**Mode:** mvp

**Requirements:** DOC-01, DOC-02, DOC-03, PLAN-01

**Success Criteria:**
1. `README.md` explains what the repository is for and how it is organized.
2. `docs/directory-spec.md` describes the intended folders and ownership of each artifact type.
3. `AGENTS.md` gives agents clear repository instructions, including Simplified Chinese response behavior.
4. `.planning/` contains project context, configuration, requirements, roadmap, and state files.

### Phase 2: Canonical Skill Format and Runtime Adapters

**Goal:** Define the reusable skill source format and compatibility model for all target runtimes.
**Mode:** mvp

**Requirements:** TMPL-01, TMPL-02, RT-01, RT-02, RT-03

**Success Criteria:**
1. `templates/skill/SKILL.md` can be copied as the starting point for a new portable skill.
2. `templates/adapter/runtime-adapter.md` captures the differences each runtime adapter must document.
3. `docs/compatibility-matrix.md` covers Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
4. The docs state that OpenClaw and Hermes Agent are required compatibility targets.
5. The canonical-source-plus-adapters strategy is documented clearly enough for contributors to follow.

### Phase 3: Portable Example Skill

**Goal:** Add a concrete example that demonstrates the repository conventions across runtimes.
**Mode:** mvp

**Requirements:** EX-01, EX-02

**Success Criteria:**
1. `examples/portable-skill/SKILL.md` uses the canonical template rather than a runtime-specific one-off format.
2. The example includes adapter notes for all six target runtimes.
3. A contributor can compare the example against the templates and understand how to author the next skill.

## Requirement Coverage

| Requirement | Phase | Status |
|-------------|-------|--------|
| DOC-01 | Phase 1 | Pending |
| DOC-02 | Phase 1 | Pending |
| DOC-03 | Phase 1 | Pending |
| PLAN-01 | Phase 1 | Pending |
| TMPL-01 | Phase 2 | Pending |
| TMPL-02 | Phase 2 | Pending |
| RT-01 | Phase 2 | Pending |
| RT-02 | Phase 2 | Pending |
| RT-03 | Phase 2 | Pending |
| EX-01 | Phase 3 | Pending |
| EX-02 | Phase 3 | Pending |

**Coverage:** 11/11 v1 requirements mapped

---
*Roadmap created: 2026-05-30*
