# Requirements: Presto Agent Skills

**Defined:** 2026-06-13
**Milestone:** v1.9 Skill Decomposition and Entry Slimming
**Core Value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## v1.9 Requirements

Requirements for reducing the weight of current skill entry files and scripts while keeping the repository's new skill system coherent and easy to extend.

### Skill Entry Decomposition

- [ ] **SD-01**: A skill reader can understand each current skill's trigger, objective, inputs, process, outputs, verification, safety boundary, and runtime adapter notes from a concise `SKILL.md`.
- [ ] **SD-02**: Long format rules, examples, renderer details, and operational notes are moved from skill entry files into skill-local `references/` files with clear names and explicit links from `SKILL.md`.
- [ ] **SD-03**: OpenClaw and Hermes Agent remain first-class runtime targets in every affected `SKILL.md`, with adapter notes preserved during slimming.
- [ ] **SD-04**: The repository template and directory guidance describe when material belongs in `SKILL.md`, `references/`, `scripts/`, or `templates/`.

### Script Decomposition

- [x] **SD-05**: Large script entry points are split into smaller internal modules or support scripts while keeping the public command names and common flags stable.
- [x] **SD-06**: Script modules have clear ownership boundaries, such as CLI dispatch, parsing, rendering, artifact writing, and verification/reporting helpers.
- [x] **SD-07**: Decomposition avoids introducing runtime-specific private syntax into canonical skill bodies or script interfaces.
- [x] **SD-08**: Shared behavior created during decomposition is extracted only when it reduces real duplication or clarifies a stable contract.

### Compatibility and Documentation

- [x] **SD-09**: README, skills index, directory specification, and compatibility guidance are updated when the decomposition pattern changes contributor expectations.
- [x] **SD-10**: The v1.9 implementation records enough before/after evidence for reviewers to confirm that entry weight is lower and public interfaces are still stable.
- [x] **SD-11**: Each affected skill keeps its current Markdown intermediate and artifact contract discoverable after the split.
- [x] **SD-12**: The milestone leaves feature expansion out of scope unless required to preserve the decomposition contract.

## Future Requirements

Deferred to a later milestone. Tracked but not in the current roadmap.

### Tooling

- **SD-FUTURE-01**: Add an automated lint/check command that reports oversized skill entries, missing runtime adapter notes, and misplaced long-form content.
- **SD-FUTURE-02**: Add optional scaffolding that can create `references/`, `scripts/`, and `templates/` starter files from the canonical skill template.
- **SD-FUTURE-03**: Add generated runtime wrappers only if a supported runtime cannot consume the canonical `SKILL.md` plus adapter notes directly.

## Out of Scope

Explicitly excluded from v1.9. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Adding new end-user skill capabilities | v1.9 is a structure and maintainability milestone. |
| Replacing the canonical `SKILL.md` source-of-truth model | The repository's core value depends on one canonical semantic entry. |
| Creating separate runtime-specific skill bodies | Runtime differences stay in adapter notes unless a future milestone defines generated wrappers. |
| Renaming public commands or common flags as part of cleanup | The split should lower maintenance cost without changing how users invoke current skills. |
| Broad style rewrites unrelated to decomposition | Keep review focused on moved content, clearer module boundaries, and updated guidance. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SD-01 | Phase 17 | Pending |
| SD-02 | Phase 17 | Pending |
| SD-03 | Phase 17 | Pending |
| SD-04 | Phase 17 | Pending |
| SD-05 | Phase 18 | Complete |
| SD-06 | Phase 18 | Complete |
| SD-07 | Phase 18 | Complete |
| SD-08 | Phase 18 | Complete |
| SD-09 | Phase 19 | Complete |
| SD-10 | Phase 19 | Complete |
| SD-11 | Phase 19 | Complete |
| SD-12 | Phase 19 | Complete |

**Coverage:**
- v1.9 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0

---
*Requirements defined: 2026-06-13 for v1.9 skill decomposition and entry slimming*
