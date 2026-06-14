# Phase 26: Package Date Backfill Repair - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-14
**Phase:** 26-Package Date Backfill Repair
**Areas discussed:** Date backfill source and target, reviewability and ambiguous evidence, public interface and scope boundaries, regression verification expectations

---

## Date Backfill Source and Target

| Option | Description | Selected |
|--------|-------------|----------|
| Package evidence to handoff Markdown | Parse or reuse `## 调度证据` from package Markdown and write concrete dates into generated `jiaoan-shicao-full.md` before render. | ✓ |
| Renderer-side fallback | Leave handoff Markdown blank and patch `jiaoan-shicao` rendering to infer missing dates later. | |
| Manual teacher fill only | Keep generated dates blank and rely on teacher review to fill them. | |

**User's choice:** The user reported the bug specifically as package-derived `起止日期` not being written into generated `jiaoan-shicao-full.md`; Phase 26 should repair that handoff path.
**Notes:** Black-box reproduction confirmed the package example has concrete `## 调度证据` date rows while generated `jiaoan-shicao-full.md` leaves `起止日期：` blank.

---

## Reviewability and Ambiguous Evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Conservative backfill with visible evidence | Fill dates only when concrete package evidence exists; keep source evidence and review markers visible. | ✓ |
| Silent best guess | Fill missing dates using whatever nearby schedule text appears plausible, without explicit review evidence. | |
| Hard fail on any ambiguity | Stop package generation whenever any date cannot be determined. | |

**User's choice:** The milestone requirements require teacher-reviewable evidence and review markers for uncertain, conflicting, or incomplete scheduling inputs.
**Notes:** The correct repair must not weaken `## 复核标记` or manifest truthfulness. Ambiguous scheduling should remain visible instead of being silently normalized.

---

## Public Interface and Scope Boundaries

| Option | Description | Selected |
|--------|-------------|----------|
| Narrow package repair | Keep public commands and original skills stable; repair `teaching-design-package` handoff behavior. | ✓ |
| Shared scheduling refactor | Extract a broader global scheduling library and wire multiple skills through it. | |
| Replace jiaoan skill flow | Change standalone `jiaoan-shicao` or `jiaoan-jihua` interfaces to fit the package. | |

**User's choice:** The user explicitly scoped Phase 26 as a v1.12 post-close repair and prohibited direct implementation during discussion.
**Notes:** Do not stage/commit untracked `deliverables/`. Do not execute plan, execute, audit, or complete commands.

---

## Regression Verification Expectations

| Option | Description | Selected |
|--------|-------------|----------|
| Black-box package regression | Generate example package, run package split/render path, assert handoff Markdown has filled `起止日期`, and record Typst/PDF status honestly. | ✓ |
| Static grep only | Search script/template text for keywords without generating package outputs. | |
| Full milestone-wide regression | Re-run unrelated v1.11/v1.12 public command matrices during this phase. | |

**User's choice:** TDPR-06 requires Markdown, Typst, and PDF evidence for the affected package path, with explicit date-fill verification.
**Notes:** PDF success may only be claimed when a PDF file exists after explicit compilation/merge. Temporary outputs should go under `/tmp` or deliberate phase evidence paths, not committed `deliverables/`.

---

## Claude's Discretion

- Planner may choose the exact parser shape for extracting date ranges from package `## 调度证据`.
- Planner may decide whether the minimum Phase 26 repair fills only the primary scaffold task date or multiple task dates, as long as package-derived concrete dates are no longer lost in generated practical lesson-plan Markdown.
- Planner may decide the least invasive verification artifact shape, but it must prove generated handoff dates are filled.

## Deferred Ideas

- Phase 27 table-width repair remains separate.
- Broad scheduling-library extraction remains deferred.
- Original teaching skill deletion/replacement remains out of scope.
