# Phase 22: Scheduling Contract and Fixture - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-14
**Phase:** 22-Scheduling Contract and Fixture
**Areas discussed:** Scheduling Contract Shape, Derived Outputs and Evidence, Conflict and Review Behavior, Fixture Scope

---

## Scheduling Contract Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse `jiaoan-jihua` renderer internals as the shared API | Fastest path, but exposes renderer-specific shell behavior as package contract. | |
| Define a package-level scheduling contract informed by `jiaoan-jihua` evidence | Keeps the shared API portable and lets future package orchestration consume stable inputs/outputs. | ✓ |
| Defer scheduling contract until the package skill exists | Avoids early contract work, but blocks Phase 23 orchestration from having a stable scheduling boundary. | |

**User's choice:** `[auto]` Selected package-level scheduling contract.
**Notes:** Local research and requirements say `jiaoan-jihua` proves feasibility but should not become the final shared API.

---

## Derived Outputs and Evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Output only rendered table cells | Minimal output, but weak auditability for teachers and downstream tests. | |
| Output dates, weeks, weekdays, assigned hours, and hour-consumption evidence | Matches TDP-02 and makes the inferred date range reviewable. | ✓ |
| Output only machine-readable JSON | Easy to test, but misses the Markdown-first review discipline. | |

**User's choice:** `[auto]` Selected auditable derived outputs with both teacher-readable and machine-readable evidence.
**Notes:** The existing renderer already derives weeks/weekdays and consumes hours; Phase 22 should make that evidence explicit.

---

## Conflict and Review Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Guess defaults when inputs are missing | Keeps output flowing, but violates TDP-03 and the project's review discipline. | |
| Preserve missing, uncertain, or conflicting inputs as review markers | Makes problems visible and lets teachers resolve them before final output. | ✓ |
| Fail immediately for every ambiguity | Clear but too rigid for teacher-facing document workflows where review markers are already accepted. | |

**User's choice:** `[auto]` Selected review markers for uncertain or conflicting schedule inputs, with hard failures for invalid structural inputs.
**Notes:** This follows the end-of-term review-marker pattern while keeping non-recoverable scheduling errors explicit.

---

## Fixture Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse the v1.10 `jiaoan-jihua` fixture source as the scheduling fixture basis | Existing source has first teaching day, daily hours, ordered tasks/stages/content, and hour suffixes. | ✓ |
| Invent a new synthetic package fixture first | More flexible, but risks drifting away from proven local evidence. | |
| Wait until Phase 23 to define fixtures | Keeps Phase 22 abstract, but misses TDP-04. | |

**User's choice:** `[auto]` Selected v1.10 teaching-plan source as the minimum fixture basis.
**Notes:** The fixture should prove inferred date ranges and evidence, not just repeat Typst generation.

---

## Claude's Discretion

- Exact schema filenames and fixture artifact placement are left to planning, as long as they follow repository conventions and preserve traceability.
- Because this was invoked with `--auto`, no interactive user prompts were used. Choices are conservative defaults from `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/research/SUMMARY.md`, and code evidence.

## Deferred Ideas

- Full `teaching-design-package` skill entry and orchestration.
- Split/combined PDF outputs.
- Optional end-of-term module integration.
- Cross-skill regression and documentation index verification.
