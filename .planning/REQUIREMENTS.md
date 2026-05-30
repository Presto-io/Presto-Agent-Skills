# Requirements: Presto Agent Skills

**Defined:** 2026-05-30
**Core Value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## v1 Requirements

Requirements for the initial repository framework. Each maps to roadmap phases.

### Documentation

- [x] **DOC-01**: A contributor can read the README and understand the repository purpose, target users, and top-level structure.
- [x] **DOC-02**: A contributor can find a directory specification that explains where skills, templates, adapters, examples, and planning files live.
- [x] **DOC-03**: An agent can read `AGENTS.md` and follow the repository's language, editing, and skill-authoring rules.

### Templates

- [ ] **TMPL-01**: A contributor can copy a canonical `SKILL.md` template that includes metadata, objective, usage, process, outputs, and success criteria.
- [ ] **TMPL-02**: A contributor can copy a runtime adapter template that captures invocation, user-question handling, task/subagent handling, tool differences, and known limitations.

### Runtime Compatibility

- [ ] **RT-01**: A contributor can inspect a compatibility matrix covering Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
- [ ] **RT-02**: OpenClaw and Hermes Agent are documented as first-class required targets with adapter placeholders and research notes.
- [ ] **RT-03**: The docs explain the preferred strategy: canonical source first, runtime-specific adapter notes or generated wrappers second.

### Examples

- [ ] **EX-01**: The repository includes at least one portable example skill using the canonical template.
- [ ] **EX-02**: The example skill includes runtime adapter notes for all six target runtimes.

### Planning

- [x] **PLAN-01**: The repository is initialized as a GSD project with project context, config, requirements, roadmap, state, and project instructions.

## v2 Requirements

Deferred to future release. Tracked but not in the current roadmap.

### Tooling

- **TOOL-01**: A contributor can run a scaffold command to create a new skill from the canonical template.
- **TOOL-02**: A contributor can run schema or lint checks for required skill sections.
- **TOOL-03**: CI verifies examples and documentation links.

### Distribution

- **DIST-01**: The repository documents install/export workflows for each supported runtime.
- **DIST-02**: Runtime-specific generated packages can be created from canonical source files.

### Verification

- **VER-01**: Compatibility smoke tests verify that generated or adapted skill artifacts load in target runtimes where automation is available.

## Out of Scope

Explicitly excluded from v1. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Scaffold CLI | Useful after the canonical structure stabilizes; premature for the first framework pass |
| Schema/lint enforcement | Requires finalizing required sections and adapter metadata first |
| Runtime execution harness | Needs real runtime installations and stable adapter contracts |
| Publishing pipeline | Distribution should follow after examples and compatibility docs are useful |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DOC-01 | Phase 1 | Complete |
| DOC-02 | Phase 1 | Complete |
| DOC-03 | Phase 1 | Complete |
| PLAN-01 | Phase 1 | Complete |
| TMPL-01 | Phase 2 | Pending |
| TMPL-02 | Phase 2 | Pending |
| RT-01 | Phase 2 | Pending |
| RT-02 | Phase 2 | Pending |
| RT-03 | Phase 2 | Pending |
| EX-01 | Phase 3 | Pending |
| EX-02 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0

---
*Requirements defined: 2026-05-30*
*Last updated: 2026-05-30 after Phase 1 execution*
