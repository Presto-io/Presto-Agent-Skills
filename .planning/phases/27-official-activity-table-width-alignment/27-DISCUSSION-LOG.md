# Phase 27: Official Activity Table Width Alignment - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-14
**Phase:** 27-Official Activity Table Width Alignment
**Areas discussed:** Official algorithm basis, Local AWK mismatch, Regression verification and Phase 26 boundary

---

## Official Algorithm Basis

| Option | Description | Selected |
|--------|-------------|----------|
| Official reference parity | Port the behavior evidenced by `/private/tmp/presto-jiaoan-shicao-main.go` and official tests around `activityTableTotalWidthCM`, `sectionColumnSpecs`, `tableColumnWidthsCM`, and `columnPressures`. | ✓ |
| Visual tweak only | Adjust current column constants until the table looks acceptable. | |
| Runtime dependency on official Go | Call the official Go template implementation from this repository's script. | |

**User's choice:** Official reference parity.
**Notes:** The user explicitly supplied the official snapshots and required a discussion output that contrasts the official algorithm with the current AWK behavior. The phase is a repair, not a renderer replacement.

---

## Local AWK Mismatch

| Option | Description | Selected |
|--------|-------------|----------|
| Repair chapter-level grouping | Keep the shell/AWK renderer but compute activity-table columns per official-style chapter, sharing widths across same-chapter tables and recalculating after `{pagebreak}`. | ✓ |
| Keep per-task widths | Continue using `table_columns_for_task(i)` for all groups under one learning task. | |
| Rewrite all activity rendering | Replace activity parsing and table emission broadly. | |

**User's choice:** Repair chapter-level grouping.
**Notes:** Read-only comparison showed official `sectionColumnSpecs(section)` flushes on `PageBreak`, while local `table_columns_for_task(i)` computes one width spec per learning task. This is the core behavioral gap to hand to planning.

---

## Regression Verification and Phase 26 Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Verify direct and package paths | Cover standalone `jiaoan-shicao` and integrated package output, including total width, narrow `课时分配`, same-chapter shared columns, centered method cells, absolute `cm` columns, PDF status, and filled `起止日期`. | ✓ |
| Verify only standalone output | Limit checks to `jiaoan-shicao.sh render`. | |
| Verify only visual PDF output | Compile PDF and rely on manual inspection. | |

**User's choice:** Verify direct and package paths.
**Notes:** The user explicitly required Phase 26 date backfill not to regress and Phase 27 to generate Markdown, Typst, and PDF evidence where possible. Generated artifacts must not be staged or committed.

---

## Claude's Discretion

- Choose conservative AWK-side implementation details during planning/execution.
- Prefer black-box Typst assertions for layout invariants.
- If existing v1.10 fixture bytes must change because official alignment changes `columns: (...)`, require explicit verification evidence and rationale.

## Deferred Ideas

- Replacing the local shell/AWK renderer with the official Go executable.
- Broad renderer architecture refactoring.
- New package features unrelated to preserving Phase 26 date backfill and verifying package-path width behavior.
