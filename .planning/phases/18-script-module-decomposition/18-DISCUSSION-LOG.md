# Phase 18: Script Module Decomposition - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-13
**Phase:** 18-Script Module Decomposition
**Areas discussed:** Target selection, public interface stability, module boundaries, shared behavior, verification expectations

---

## Target Selection

| Option | Description | Selected |
|--------|-------------|----------|
| Largest scripts first | Focus on `school-presentation.sh`, `render_package.py`, and `gongwen.sh` because they carry the most code and responsibility density. | yes |
| All scripts evenly | Split every skill script regardless of current size. | |
| Presentation only | Spend the phase only on the largest presentation script. | |

**User's choice:** Use the Phase 18 scope and codebase scan to prioritize the largest script entry points.
**Notes:** The user explicitly scoped Phase 18 to Script Module Decomposition / SD-05 through SD-08. Line counts confirmed the three largest source scripts are `school-presentation.sh` (4940), `render_package.py` (1971), and `gongwen.sh` (1251).

---

## Public Interface Stability

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve shell entry points | Keep current command filenames, command names, common flags, outputs, and manifests stable while moving internals. | yes |
| Rename commands during cleanup | Use decomposition as a chance to simplify or rename commands and flags. | |
| Add compatibility aliases only | Add new names while leaving old ones temporarily supported. | |

**User's choice:** Preserve public command names, common flags, and output contracts.
**Notes:** This was explicitly required by the user and by SD-05. Phase 18 is a refactor phase, not a public CLI redesign.

---

## Module Boundaries

| Option | Description | Selected |
|--------|-------------|----------|
| Responsibility-based modules | Split around CLI dispatch, parsing, rendering, artifact writing, verification/reporting, and export helpers. | yes |
| Equal-size chunks | Split files into similarly sized chunks regardless of ownership. | |
| One shared renderer framework | Create a broad cross-skill framework for all scripts. | |

**User's choice:** Use responsibility-based module boundaries.
**Notes:** This directly maps to SD-06 and keeps the work reviewable. Arbitrary chunking would reduce line count without improving ownership.

---

## Shared Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Extract real duplication only | Share only helpers that already repeat or represent a stable public contract. | yes |
| Create global utilities broadly | Build reusable script infrastructure for future skills now. | |
| Avoid all sharing | Keep every helper skill-local even when identical. | |

**User's choice:** Extract shared behavior only when it reduces real duplication or clarifies a stable contract.
**Notes:** This follows SD-08 and avoids turning Phase 18 into a framework-design phase.

---

## Verification Expectations

| Option | Description | Selected |
|--------|-------------|----------|
| Public-command regression gates | Verify through existing public shell commands and compare artifact/manifest contract stability. | yes |
| Private module tests only | Test extracted internals without exercising public commands. | |
| Syntax checks only | Rely on `bash -n` and `py_compile` after file moves. | |

**User's choice:** Public-command regression gates are required.
**Notes:** Private module tests and syntax checks can supplement verification, but Phase 18 acceptance must prove current user-facing commands still work.

## Claude's Discretion

- Exact module names and package layout are left to the planner/executor.
- If full decomposition of a high-risk target is too broad, a smaller vertical extraction with strong compatibility evidence is preferred.
- Secondary scripts may remain untouched unless real duplication justifies shared helper extraction.

## Deferred Ideas

- Phase 19 documentation review, compatibility matrix review, before/after milestone evidence, milestone audit, and milestone closeout.
- Any new end-user feature, new output format, or command rename.
