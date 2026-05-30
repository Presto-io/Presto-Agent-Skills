# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Granularity:** Coarse
**Project Mode:** MVP

## Overview

This roadmap establishes the repository as a portable agent skill framework before adding automation. The first milestone is complete when the repository structure and GSD planning files are initialized.

| Phase | Name | Goal | Requirements |
|-------|------|------|--------------|
| 1 | Repository and GSD Foundation | As a skill contributor, I want to use a clear repository foundation and GSD baseline, so that I can author portable skills consistently across runtimes. | DOC-01, DOC-02, DOC-03, PLAN-01 |
| 2 | Canonical Skill Format and Runtime Notes | As a skill contributor, I want to use a reusable skill source format with embedded runtime notes, so that I can adapt one skill source across all supported runtimes. | TMPL-01, TMPL-02, RT-01, RT-02, RT-03 |
| 3 | Portable Example Scope Reconciliation | As a skill contributor, I want the repository to remove unused example artifacts from v1, so that the canonical skill template remains the primary authoring path. | EX-01, EX-02 (deferred) |

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

### Phase 2: Canonical Skill Format and Runtime Notes

**Goal:** As a skill contributor, I want to use a reusable skill source format with embedded runtime notes, so that I can adapt one skill source across all supported runtimes.
**Mode:** mvp

**Requirements:** TMPL-01, TMPL-02, RT-01, RT-02, RT-03

**Success Criteria:**
1. `templates/skill/SKILL.md` can be copied as the starting point for a new portable skill.
2. `templates/skill/SKILL.md` includes `Runtime Adapter Notes` for the differences each runtime must document.
3. `docs/compatibility-matrix.md` covers Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
4. The docs state that OpenClaw and Hermes Agent are required compatibility targets.
5. The canonical-source-plus-runtime-notes strategy is documented clearly enough for contributors to follow.

### Phase 3: Portable Example Scope Reconciliation

**Goal:** As a skill contributor, I want the repository to remove unused example artifacts from v1, so that the canonical skill template remains the primary authoring path.
**Mode:** mvp

**Requirements:** EX-01, EX-02 (deferred)

**Success Criteria:**
1. `README.md` and `docs/directory-spec.md` keep `templates/skill/SKILL.md` as the first/default authoring path.
2. The repository does not retain unused example files or directories in v1.
3. Phase 3 planning records explain that EX-01 and EX-02 are deferred rather than treated as hard v1 delivery promises.

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
| EX-01 | Phase 3 | Deferred |
| EX-02 | Phase 3 | Deferred |

**Coverage:** 9/9 v1 requirements mapped; 2 example items deferred

---
*Roadmap created: 2026-05-30*
