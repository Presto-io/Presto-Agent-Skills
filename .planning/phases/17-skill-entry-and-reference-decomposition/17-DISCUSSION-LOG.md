# Phase 17: Skill Entry and Reference Decomposition - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md; this log preserves the automatic discussion choices.

**Date:** 2026-06-13
**Phase:** 17-Skill Entry and Reference Decomposition
**Areas discussed:** Entry shape, reference ownership, runtime adapter preservation, documentation boundary

---

## Entry Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal entries only | Keep only trigger/objective and push most operational content out | |
| Semantic entries with reference links | Keep the full reader map in `SKILL.md`, move long details into named references | yes |
| Leave entries as-is | Avoid moving content until script decomposition | |

**User's choice:** Auto-selected semantic entries with reference links.
**Notes:** This best satisfies SD-01 and SD-02 because entries remain useful without becoming full reference manuals.

---

## Reference Ownership

| Option | Description | Selected |
|--------|-------------|----------|
| Skill-local references | Put long rules in each skill's own `references/` directory | yes |
| Global shared reference | Consolidate common rules into one repository-level document | |
| Template-only guidance | Only update future guidance, do not move current content | |

**User's choice:** Auto-selected skill-local references.
**Notes:** This follows AGENTS.md and avoids creating a universal schema outside Phase 17 scope.

---

## Runtime Adapter Preservation

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve all six runtime rows | Keep Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, Hermes Agent visible | yes |
| Move runtime notes to references | Slim entries further by relocating the table | |
| Preserve only verified runtimes | Remove less-tested runtimes from current entries | |

**User's choice:** Auto-selected preserve all six runtime rows.
**Notes:** OpenClaw and Hermes Agent are mandatory first-class runtime targets.

---

## Documentation Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Template and directory spec only | Update exactly the Phase 17 named docs | |
| Template, directory spec, and README | Also sync contributor-facing README because directory convention changes | yes |
| Defer docs to Phase 19 | Keep implementation only in Phase 17 | |

**User's choice:** Auto-selected template, directory spec, and README.
**Notes:** AGENTS.md requires README and directory spec to stay synchronized when directory conventions change.

## Claude's Discretion

- Choose exact reference file names and grouping by affected skill size.
- Keep verification focused on content presence, links, runtime rows, and script smoke checks.

## Deferred Ideas

- No script module split in this phase.
- No milestone audit or Phase 19 before/after report in this phase.
