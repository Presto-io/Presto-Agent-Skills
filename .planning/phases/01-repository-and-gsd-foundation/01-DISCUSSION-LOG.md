# Phase 1: Repository and GSD Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-30
**Phase:** 1-Repository and GSD Foundation
**Areas discussed:** Phase completion approach, README structure, directory specification, agent instructions, GSD record alignment

---

## Phase Completion Approach

| Option | Description | Selected |
|--------|-------------|----------|
| Review and supplement existing baseline | Existing `README.md`, `AGENTS.md`, `docs/directory-spec.md`, and `.planning/` are already present; review them, patch gaps, and align records. | yes |
| Allow major rewrites | Planner may substantially rewrite key docs if it sees fit. | |
| Freeze content, only supplement records | Do not change docs unless there is a blocking error. | |

**User's choice:** Review and supplement existing baseline.
**Notes:** Phase 1 should not restart from scratch. Existing files are the baseline.

---

## README Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Quick entry | Optimize for immediate contributor orientation. | |
| Full specification entry | Put more of the repository contract directly into README. | |
| Two-layer structure | Start with quick orientation, then provide fuller structure and constraint references. | yes |

**User's choice:** Two-layer structure.
**Notes:** README should work for both first-time readers and contributors who need the repository contract.

---

## Directory Specification

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal responsibility table | Only say which directory stores which artifact. | |
| Responsibilities plus boundary rules | Define directory purposes and common boundaries, such as templates vs examples and canonical body vs adapter notes. | yes |
| Detailed operation manual | Include step-by-step procedures for adding skills, adapters, and examples. | |

**User's choice:** Responsibilities plus boundary rules.
**Notes:** The directory spec should be clear but not bloated.

---

## Agent Instructions

| Option | Description | Selected |
|--------|-------------|----------|
| Lightweight collaboration note | Mainly remind agents about language and basic layout. | |
| Strong constraint file | Explicitly enforce language, runtime-neutral canonical skills, mandatory OpenClaw/Hermes consideration, and synchronized doc updates. | yes |
| Strong constraints plus workflow details | Add detailed checklists, validation steps, and process rules. | |

**User's choice:** Strong constraint file.
**Notes:** Keep `AGENTS.md` authoritative without turning it into a long process manual.

---

## GSD Record Alignment

| Option | Description | Selected |
|--------|-------------|----------|
| Review and supplement records | Use existing files as input; patch gaps; write normal GSD summary and verification artifacts. | yes |
| Regenerate through the normal flow | Recreate or rewrite the files through Phase 1 execution. | |
| Only supplement GSD records | Create context, plan, and summary without changing source docs unless blocked. | |

**User's choice:** Review and supplement records.
**Notes:** The plan should explicitly reconcile existing Phase 1 artifacts with missing GSD plan/summary records.

## Claude's Discretion

- Planner and executor may choose the exact review checklist and verification commands.
- Minor documentation edits are allowed when needed to satisfy Phase 1 success criteria.

## Deferred Ideas

None.
