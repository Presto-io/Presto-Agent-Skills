# Phase 23: Integrated Skill Entry and Jiaoan Orchestration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-14
**Phase:** 23-integrated-skill-entry-and-jiaoan-orchestration
**Areas discussed:** New skill entry and ownership, Markdown intermediate contract, jiaoan composition model, Typst/PDF output planning, runtime adapter coverage

---

## Workflow Notes

- Invoked command: `/gsd:discuss-phase 23 --auto`.
- User explicitly authorized automatic conservative decisions and instructed this subagent not to execute any other GSD command.
- `gsd-sdk query init.phase-op 23` returned `phase_found: false`, while `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, and the user prompt all identify Phase 23 as the next planned phase. This log records the mismatch; the context was generated from the roadmap and requirement source of truth.
- `gsd-sdk query todo.match-phase 23` returned no matches.
- `workflow.max_discuss_passes` was not configured; the auto-mode default cap applies.
- Auto-mode normally chains to plan-phase after context capture, but this subagent did not run plan-phase because the user restricted the task to this single GSD command.

---

## New Skill Entry and Ownership

| Option | Description | Selected |
|--------|-------------|----------|
| Create `skills/teaching-design-package/` as a new orchestrator | Matches TDP-05 preferred name and keeps original jiaoan skills standalone. | yes |
| Extend only `jiaoan-jihua` or `jiaoan-shicao` | Would overload an existing standalone skill and blur ownership. | |
| Physically merge existing jiaoan skill directories | Violates TDP-06 and the user's non-deletion/non-replacement constraint. | |

**User's choice:** Auto-selected first option.
**Notes:** The new skill owns orchestration and package-level review flow; existing jiaoan skills keep their public interfaces.

---

## Markdown Intermediate Contract

| Option | Description | Selected |
|--------|-------------|----------|
| Persistent package-level `teaching-design-package-full.md` checkpoint | Keeps the integrated workflow Markdown-first and teacher-reviewable before rendering. | yes |
| Generate module Markdown only, without a package checkpoint | Easier initially but weakens package-level review and scheduling evidence. | |
| One-step source-to-PDF orchestration | Explicitly out of scope and conflicts with repository workflow discipline. | |

**User's choice:** Auto-selected first option.
**Notes:** The checkpoint should include package metadata, scheduling evidence, teaching-plan content, lesson-plan content, output status, and `## 复核标记`.

---

## Jiaoan Composition Model

| Option | Description | Selected |
|--------|-------------|----------|
| Compose via stable module intermediates and existing render paths | Preserves `jiaoan-jihua` and `jiaoan-shicao` while enabling package orchestration. | yes |
| Duplicate both jiaoan format manuals inside the package entry | Makes the new skill heavy and increases drift. | |
| Expose `jiaoan-jihua.sh` internals as the package scheduling API | Treats implementation evidence as public API and conflicts with Phase 22 decisions. | |

**User's choice:** Auto-selected first option.
**Notes:** Phase 23 should consume `references/scheduling-contract.md` for scheduling and use module-compatible Markdown for rendering.

---

## Typst/PDF Output Planning

| Option | Description | Selected |
|--------|-------------|----------|
| Plan split teaching-plan and lesson-plan outputs first | Fits Phase 23 scope and keeps combined package behavior for Phase 24. | yes |
| Implement default combined package PDF now | Belongs to Phase 24 with optional end-of-term and merge/failure semantics. | |
| Claim PDF output whenever Typst is generated | Misrepresents current script behavior and weakens verification. | |

**User's choice:** Auto-selected first option.
**Notes:** Use names such as `teaching-plan.pdf` and `lesson-plans.pdf` where PDF compilation is actually verified; otherwise record Typst/status evidence.

---

## Runtime Adapter Coverage

| Option | Description | Selected |
|--------|-------------|----------|
| Include all six runtime notes in the new canonical skill entry | Satisfies TDP-09 and existing repository policy. | yes |
| Cover only Codex/Claude initially | Faster but violates mandatory OpenClaw/Hermes coverage expectations. | |
| Move runtime behavior into separate wrappers | Not aligned with current canonical `SKILL.md` plus adapter notes model. | |

**User's choice:** Auto-selected first option.
**Notes:** OpenClaw and Hermes Agent notes should explicitly cover skill-folder discovery, references/scripts, shell permissions, and calendar/support resources.

---

## Claude's Discretion

- Choose exact package reference/template/script filenames during planning, keeping them discoverable and consistent with repository conventions.
- Prefer Markdown checkpoint and manifest/status evidence over broad PDF merging if implementation scope tightens.
- Mark ambiguous teaching-plan or lesson-plan mapping issues for teacher review instead of inventing data.

## Deferred Ideas

- Optional end-of-term module integration belongs to Phase 24.
- Combined `teaching-design-package.pdf` output behavior belongs to Phase 24.
- Full regression verification and documentation index checks belong to Phase 25.
