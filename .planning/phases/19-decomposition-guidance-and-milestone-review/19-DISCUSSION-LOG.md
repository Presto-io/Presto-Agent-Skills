# Phase 19: Decomposition Guidance and Milestone Review - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-13
**Phase:** 19-Decomposition Guidance and Milestone Review
**Areas discussed:** Guidance surfaces, review evidence, artifact contract discoverability, scope guard
**Source:** User provided explicit command boundary for `gsd discuss phase 19`; no additional interactive planning, execution, audit, or milestone closeout was performed.

---

## Guidance Surfaces

| Option | Description | Selected |
|--------|-------------|----------|
| Update only top-level README | Minimal touch, but risks leaving skills index, directory spec, and runtime guidance inconsistent. | |
| Update README, skills index, directory spec, and compatibility guidance | Matches SD-09 and AGENTS.md sync expectations; keeps contributor expectations aligned. | ✓ |
| Add a new long contributor manual | Would centralize guidance but conflicts with the lightweight-entry/progressive-disclosure direction. | |

**User's choice:** Cover README, skills index, directory specification, and compatibility guidance for SD-09 only.
**Notes:** Guidance should explain the decomposition pattern and review expectations without expanding the milestone into new features or a broad rewrite.

---

## Review Evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Create pre-audit evidence from Phase 17/18 summaries and verifications | Gives reviewers before/after facts without running formal milestone audit or archive. | ✓ |
| Run milestone audit now | Explicitly out of scope for this command. | |
| Re-run all implementation verification as Phase 19 execution | Belongs to a later plan/execute step if needed, not discuss. | |

**User's choice:** Record before/after evidence for reviewer use, based on Phase 17/18 SUMMARY and VERIFICATION files.
**Notes:** Evidence should include entry line-count reduction, created references, script module directories, preserved public commands/flags, and scope guards.

---

## Artifact Contract Discoverability

| Option | Description | Selected |
|--------|-------------|----------|
| Verify and tighten links to existing Markdown intermediates and artifact references | Satisfies SD-11 while preserving current contracts. | ✓ |
| Move artifact contracts into README | Would make README heavier and duplicate skill-local references. | |
| Redesign artifact names or manifest keys | Explicitly out of scope; would violate compatibility requirements. | |

**User's choice:** Confirm each affected skill keeps Markdown intermediate and artifact contract discoverable after the split.
**Notes:** The discoverability check should point from `SKILL.md` to `templates/` and `references/` rather than changing artifact behavior.

---

## Scope Guard

| Option | Description | Selected |
|--------|-------------|----------|
| Keep Phase 19 limited to SD-09 through SD-12 | Matches the user's command boundary and v1.9 roadmap. | ✓ |
| Fold in feature cleanup while touching docs | Would create unrelated review noise and violate SD-12. | |
| Complete/archive v1.9 during this command | Explicitly forbidden by the command boundary. | |

**User's choice:** Phase 19 covers guidance and milestone-review evidence only; no unrelated feature expansion, milestone audit, or archive.
**Notes:** Future linting, scaffolding, generated wrappers, and end-user capabilities remain future scope.

---

## Claude's Discretion

- Choose the exact Phase 19 evidence filename during planning/execution, provided it is easy for later audit to cite and remains under the Phase 19 planning directory.
- Make small wording/link fixes in guidance files only where needed to preserve decomposition discoverability.

## Deferred Ideas

- Formal milestone audit and milestone completion/archive.
- Automated lint/check command for decomposition rules.
- Optional scaffolding generator for `references/`, `scripts/`, and `templates/`.
- Runtime-specific generated wrappers.
