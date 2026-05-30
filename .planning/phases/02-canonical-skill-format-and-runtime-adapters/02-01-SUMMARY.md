---
phase: 02-canonical-skill-format-and-runtime-adapters
plan: 01
subsystem: documentation
tags: [markdown, templates, runtime-compatibility, agent-skills]

requires: [01-repository-and-gsd-foundation]
provides:
  - "Copyable canonical SKILL.md template aligned to TMPL-01"
  - "Minimal runtime adapter note template aligned to TMPL-02"
  - "Six-runtime compatibility matrix aligned to RT-01, RT-02, and RT-03"
affects: [03-portable-example-skill]

tech-stack:
  added: []
  patterns:
    - "Keep one canonical SKILL.md as the semantic source of truth"
    - "Prefer embedded runtime adapter notes before separate adapter docs"
    - "Record installation-time verification when runtime behavior is not locally verified"

key-files:
  created:
    - ".planning/phases/02-canonical-skill-format-and-runtime-adapters/02-01-SUMMARY.md"
  modified:
    - "templates/skill/SKILL.md"
    - "templates/README.md"
    - "templates/adapter/runtime-adapter.md"
    - "adapters/README.md"
    - "docs/compatibility-matrix.md"
    - "README.md"
    - "docs/directory-spec.md"
    - ".planning/REQUIREMENTS.md"
    - ".planning/ROADMAP.md"
    - ".planning/STATE.md"

key-decisions:
  - "Preserved Phase 2 D-01 through D-08 by making templates/skill/SKILL.md the default copyable artifact."
  - "Preserved D-09 by keeping template and adapter wording direct, placeholder-based, and install-oriented."
  - "Preserved D-10 through D-12 by keeping Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent as required targets while marking unverified behavior as installation-time checks."

patterns-established:
  - "New skills start from one SKILL.md file with embedded runtime adapter notes for all six required runtimes."
  - "Separate adapter files are optional compatibility notes, not duplicated workflow logic."
  - "Generated wrappers remain an exception/deferred path that requires documented generation and verification."

requirements-completed: [TMPL-01, TMPL-02, RT-01, RT-02, RT-03]

duration: 18min
completed: 2026-05-30
---

# Phase 2 Plan 01: Canonical Skill Format and Runtime Adapters Summary

**Canonical skill templates and runtime compatibility docs now tell one single-file-first story.**

## Performance

- **Duration:** 18min
- **Completed:** 2026-05-30
- **Tasks:** 4
- **Files modified:** 11

## Accomplishments

- Updated `templates/skill/SKILL.md` as the primary copyable artifact for new portable skills.
- Added explicit placeholders for metadata, objective, usage triggers, inputs, process, runtime adapter notes, outputs, verification, success criteria, and safety boundaries.
- Reframed `templates/adapter/runtime-adapter.md` and `adapters/README.md` as optional compatibility notes, not parallel implementations.
- Updated `docs/compatibility-matrix.md` to cover Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent with same-file strategy and verification cautions.
- Aligned `README.md`, `docs/directory-spec.md`, and `templates/README.md` around the canonical `SKILL.md` contributor path.
- Updated GSD requirement and roadmap status for Phase 2 while leaving Phase 3 example requirements pending.

## Requirement Evidence

| Requirement | Evidence | Result |
|-------------|----------|--------|
| TMPL-01 | `templates/skill/SKILL.md` includes metadata, Objective, Use When, Inputs, Process, Runtime Adapter Notes, Outputs, Verification, Success Criteria, and Safety. | Passed |
| TMPL-02 | `templates/adapter/runtime-adapter.md` includes Loading / Install Path, Invocation Model, User Questions, Tasks and Subagents, Tool and Permission Differences, Canonical Mapping, Known Limitations, and Verification Checklist. | Passed |
| RT-01 | `docs/compatibility-matrix.md` has matrix rows and runtime notes for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent. | Passed |
| RT-02 | `docs/compatibility-matrix.md`, `README.md`, and `adapters/README.md` keep OpenClaw and Hermes Agent as first-class required targets with verification cautions. | Passed |
| RT-03 | `README.md`, `docs/directory-spec.md`, `docs/compatibility-matrix.md`, `templates/README.md`, and `adapters/README.md` describe canonical `SKILL.md` first, embedded adapter notes second, and generated wrappers only as an exception/deferred path. | Passed |

## Task Commits

1. **Task 1: Tighten the canonical skill template as the primary copyable artifact** - `34ecac8` (`docs`)
2. **Task 2: Reframe adapter material as minimal compatibility notes** - `5e916fe` (`docs`)
3. **Task 3: Align runtime compatibility and contributor-facing docs** - `f80c416` (`docs`)

## Files Created/Modified

- `templates/skill/SKILL.md` - Added supported runtime metadata, stronger copyable placeholders, success criteria, and safety verification prompts.
- `templates/README.md` - Pointed contributors to `templates/skill/SKILL.md` first and adapter template only when embedded notes are not enough.
- `templates/adapter/runtime-adapter.md` - Added optional compatibility-note framing plus install, question, task/subagent, tool, permission, limitation, and verification fields.
- `adapters/README.md` - Clarified adapters as optional notes and preserved OpenClaw/Hermes as required targets.
- `docs/compatibility-matrix.md` - Reworked the recommended pattern and matrix around one canonical skill file plus runtime notes.
- `README.md` - Updated contributor flow to use one `SKILL.md` first and defer separate adapter files.
- `docs/directory-spec.md` - Updated directory ownership rules for canonical skills, adapter notes, and deferred wrappers.
- `.planning/REQUIREMENTS.md` - Marked Phase 2 requirements complete.
- `.planning/ROADMAP.md` - Marked Phase 2 roadmap coverage complete.
- `.planning/STATE.md` - Advanced state toward Phase 3 planning readiness.
- `.planning/phases/02-canonical-skill-format-and-runtime-adapters/02-01-SUMMARY.md` - Created Phase 2 evidence and verification record.

## Local Verification

| Command | Outcome |
|---------|---------|
| `rg -n "metadata:\|Objective\|Use When\|Inputs\|Process\|Runtime Adapter Notes\|Outputs\|Verification\|Success Criteria\|Safety" templates/skill/SKILL.md` | Passed; all canonical template sections are present. |
| `rg -n "Codex\|Claude Code\|Gemini CLI\|OpenCode\|OpenClaw\|Hermes Agent" templates/skill/SKILL.md` | Passed; all six required runtimes are named in the canonical template. |
| `rg -n "templates/skill/SKILL.md\|templates/adapter/runtime-adapter.md\|canonical\|SKILL.md" templates/README.md` | Passed; template index points to the canonical skill template first. |
| `rg -n "Loading\|Install\|Invocation\|User Questions\|Tasks\|Subagents\|Tool\|Permission\|Canonical Mapping\|Known Limitations\|Verification" templates/adapter/runtime-adapter.md` | Passed; adapter template covers the required compatibility-note fields. |
| `rg -n "canonical\|SKILL.md\|adapter notes\|generated wrapper\|Codex\|Claude Code\|Gemini CLI\|OpenCode\|OpenClaw\|Hermes Agent" adapters/README.md` | Passed; adapter guidance is single-file-first and covers required runtimes. |
| `rg -n "Codex\|Claude Code\|Gemini CLI\|OpenCode\|OpenClaw\|Hermes Agent" docs/compatibility-matrix.md` | Passed; compatibility matrix covers all six runtimes. |
| `rg -n "canonical\|SKILL\\.md\|one canonical\|single\|adapter notes\|generated wrappers\|OpenClaw\|Hermes Agent" docs/compatibility-matrix.md README.md docs/directory-spec.md` | Passed; contributor-facing docs reinforce canonical source first and required OpenClaw/Hermes coverage. |

## Decisions Made

No new runtime architecture was added. Phase 2 followed the locked decision that one canonical `SKILL.md` is the main cross-agent artifact; adapter material remains install/use compatibility documentation.

## Deviations from Plan

None - plan executed within the documented Phase 2 scope.

## Issues Encountered

- This Codex runtime did not expose a GSD `Agent` tool, so the single Phase 2 plan was executed inline. The phase had one plan and documentation-only tasks, so the fallback did not change scope or outputs.
- Phase 2 plan and research files were already untracked at executor start. They were treated as relevant GSD metadata and included in the final metadata commit.

## Scope Exclusions Confirmed

No scaffold CLI, schema/lint enforcement, runtime harness, generated wrapper implementation, publishing workflow, package install, UI, API, database, or deployment work was added.

## Known Stubs

None beyond intentional template placeholders.

## Authentication Gates

None.

## User Setup Required

None.

## Next Phase Readiness

Phase 3 can now create `examples/portable-skill/SKILL.md` against the tightened canonical template and include runtime adapter notes for all six required targets.

## Self-Check: PASSED

- Created file exists: `.planning/phases/02-canonical-skill-format-and-runtime-adapters/02-01-SUMMARY.md`.
- Task commits exist: `34ecac8`, `5e916fe`, and `f80c416`.
- Requirement evidence covers TMPL-01, TMPL-02, RT-01, RT-02, and RT-03.
- Phase 3 requirements EX-01 and EX-02 remain pending.

---
*Phase: 02-canonical-skill-format-and-runtime-adapters*
*Completed: 2026-05-30*
