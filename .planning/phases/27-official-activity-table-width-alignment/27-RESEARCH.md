# Phase 27 Research: Official Activity Table Width Alignment

**Phase:** 27 - Official Activity Table Width Alignment
**Date:** 2026-06-14
**Status:** Complete

## Research Question

What does Phase 27 need to know before planning a safe repair for `jiaoan-shicao` `教学活动设计` table widths?

## Sources Read

- `.planning/phases/27-official-activity-table-width-alignment/27-CONTEXT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/26-package-date-backfill-repair/26-SUMMARY.md`
- `.planning/phases/26-package-date-backfill-repair/26-VERIFICATION.md`
- `/private/tmp/presto-jiaoan-shicao-main.go`
- `/private/tmp/presto-jiaoan-shicao-main_test.go`
- `/private/tmp/presto-jiaoan-shicao-example.md`
- `skills/jiaoan-shicao/scripts/render_v110_typst.awk`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`
- `skills/jiaoan-shicao/references/format-and-rendering.md`

## Findings

### Official Algorithm Basis

- The official activity-table total width is `activityTableTotalWidthCM = 25.04`.
- Official rendering enters `renderActivitySection`, precomputes `chapterColumnSpecs := sectionColumnSpecs(section)`, and uses chapter specs while iterating section items.
- `sectionColumnSpecs(section)` accumulates tables until it sees a `PageBreak`, then flushes a shared `columns: (...)` spec for that chapter and starts a new chapter.
- `tableColumnWidthsCM(tables)` keeps six absolute `cm` columns and starts from header minimum widths via `headerMinWidthCM`.
- `columnPressures(tables)` uses title/content pressure from activity metadata and rows. The locked weight shape from context should be preserved in the AWK port.
- Official tests assert that header rows fit, teaching-method cells remain centered, activity widths total the official activity width, and multiple tables in the same chapter use identical widths.

### Local AWK Gap

- The current renderer already has useful helpers: `display_width`, `content_pressure`, `header_min_width_cm`, `table_columns_for_task`, and `emit_activity_group`.
- `table_columns_for_task(i)` currently aggregates all activity groups in a learning task. This is broader than official chapter scope.
- `emit_activity_group(i, g)` emits one Typst table per activity group and currently prints `columns: (` from `table_columns_for_task(i)`.
- `{pagebreak}` is emitted elsewhere, but activity-mode parsing does not currently preserve it as a width-group boundary for activity groups.
- Teaching-method cells already use `align(center + horizon)`, so the repair does not need a broad table-emission rewrite.

### Phase 26 Regression Boundary

- Phase 26 completed package-side date backfill in `teaching-design-package`.
- Phase 27 must not regress generated package `jiaoan-shicao-full.md` date filling.
- Package verification should assert at least one filled `起止日期：YYYY-MM-DD - YYYY-MM-DD` and zero blank `起止日期：` lines before claiming success.
- Generated verification artifacts should stay under `/tmp`; do not stage generated `deliverables/` artifacts.

## Planning Implications

- Prefer a focused AWK repair: record group chapter IDs while parsing activity groups, aggregate widths by `(task, chapter)`, and feed each emitted group the chapter-scoped spec.
- Keep the public `jiaoan-shicao.sh` commands and flags stable.
- Update renderer documentation so teachers and future agents know that same-chapter activity tables share official-style absolute `cm` widths and `{pagebreak}` starts a recalculation boundary.
- Treat any v1.10 fixture Typst drift as intentional only if it is limited to official activity-table `columns: (...)` behavior, and document the rationale in Phase 27 verification evidence.

## Verification Strategy

Direct `jiaoan-shicao` path:

1. Generate Markdown with `jiaoan-shicao.sh example`.
2. Render Typst with `jiaoan-shicao.sh render`.
3. Parse activity-table `columns: (...)` lists and assert:
   - six values with `cm` units;
   - total width between `25.02` and `25.06`;
   - column 6 is narrower than columns 2, 3, and 4;
   - at least two same-chapter tables share identical columns;
   - teaching-method cells still include `align(center + horizon)`.
4. Compile PDF only when `typst compile` exits 0 and the PDF file exists; otherwise record `missing_compiler` or `failed`.

Integrated package path:

1. Generate package Markdown with `teaching-design-package.sh example`.
2. Run `plan-split`.
3. Assert filled package handoff dates and no blank `起止日期：` lines.
4. Run `render-split`.
5. Apply the same activity-width parser to `lesson-plans.typ`.
6. Compile `lesson-plans.pdf` and `teaching-plan.pdf` only when real PDF files are produced.

## Risks

- **False alignment:** A plan that only changes constants could still miss chapter/pagebreak grouping. Block with same-chapter and post-pagebreak assertions.
- **Fixture drift without explanation:** If expected Typst changes, record before/after reason in `27-VERIFICATION.md`.
- **Phase 26 regression:** Always include the package handoff date assertion.
- **False PDF readiness:** Record PDF success only from actual compiler output and real files.

## RESEARCH COMPLETE

Phase 27 has enough local evidence to plan the repair without external web research. The official local snapshots are sufficient as algorithm and invariant references.
