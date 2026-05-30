# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Granularity:** Coarse
**Project Mode:** MVP

## Overview

This roadmap establishes the repository as a portable agent skill framework before adding automation. The first milestone is complete when the repository structure and GSD planning files are initialized.

| Phase | Name | Goal | Requirements |
|-------|------|------|--------------|
| 1 | Repository and GSD Foundation | As a skill contributor, I want to use a clear repository foundation and GSD baseline, so that I can author portable skills consistently across runtimes. | DOC-01, DOC-02, DOC-03, PLAN-01 |
| 2 | Canonical Skill Format and Runtime Adapters | As a skill contributor, I want to use a reusable skill source format and runtime adapter model, so that I can adapt one skill source across all supported runtimes. | TMPL-01, TMPL-02, RT-01, RT-02, RT-03 |
| 3 | Portable Example Skill | As a skill contributor, I want to study a concrete example that demonstrates the repository conventions across runtimes, so that I can author the next portable skill with confidence. | EX-01, EX-02 |

## Phases

### Phase 1: Repository and GSD Foundation

**Goal:** As a skill contributor, I want to use a clear repository foundation and GSD baseline, so that I can author portable skills consistently across runtimes.
**Mode:** mvp

**Requirements:** DOC-01, DOC-02, DOC-03, PLAN-01

**Success Criteria:**
1. `README.md` explains what the repository is for and how it is organized.
2. `docs/directory-spec.md` describes the intended folders and ownership of each artifact type.
3. `AGENTS.md` gives agents clear repository instructions, including Simplified Chinese response behavior.
4. `.planning/` contains project context, configuration, requirements, roadmap, and state files.

### Phase 2: Canonical Skill Format and Runtime Adapters

**Goal:** As a skill contributor, I want to use a reusable skill source format and runtime adapter model, so that I can adapt one skill source across all supported runtimes.
**Mode:** mvp

**Requirements:** TMPL-01, TMPL-02, RT-01, RT-02, RT-03

**Success Criteria:**
1. `templates/skill/SKILL.md` can be copied as the starting point for a new portable skill.
2. `templates/adapter/runtime-adapter.md` captures the differences each runtime adapter must document.
3. `docs/compatibility-matrix.md` covers Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
4. The docs state that OpenClaw and Hermes Agent are required compatibility targets.
5. The canonical-source-plus-adapters strategy is documented clearly enough for contributors to follow.

### Phase 3: Portable Example Skill

**Goal:** As a skill contributor, I want to study a concrete example that demonstrates the repository conventions across runtimes, so that I can author the next portable skill with confidence.
**Mode:** mvp

**Requirements:** EX-01, EX-02

**Success Criteria:**
1. `examples/portable-skill/SKILL.md` uses the canonical template rather than a runtime-specific one-off format.
2. The example includes adapter notes for all six target runtimes.
3. A contributor can compare the example against the templates and understand how to author the next skill.

## Requirement Coverage

| Requirement | Phase | Status |
|-------------|-------|--------|
| DOC-01 | Phase 1 | Complete |
| DOC-02 | Phase 1 | Complete |
| DOC-03 | Phase 1 | Complete |
| PLAN-01 | Phase 1 | Complete |
| TMPL-01 | Phase 2 | Complete |
| TMPL-02 | Phase 2 | Complete |
| RT-01 | Phase 2 | Complete |
| RT-02 | Phase 2 | Complete |
| RT-03 | Phase 2 | Complete |
| EX-01 | Phase 3 | Pending |
| EX-02 | Phase 3 | Pending |

**Coverage:** 11/11 v1 requirements mapped

---
*Roadmap created: 2026-05-30*
