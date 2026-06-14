# Phase 27 Verification: Official Activity Table Width Alignment

**Phase:** 27 - Official Activity Table Width Alignment
**Plan:** 01 - official-activity-table-width-alignment
**Started:** 2026-06-14T08:57:49Z

## Official Algorithm Evidence

Local official reference snapshots:

- `/private/tmp/presto-jiaoan-shicao-main.go`
- `/private/tmp/presto-jiaoan-shicao-main_test.go`
- `/private/tmp/presto-jiaoan-shicao-example.md`

Official identifiers and invariants recorded before implementation:

- `activityTableTotalWidthCM = 25.04` is defined in `/private/tmp/presto-jiaoan-shicao-main.go`.
- `renderActivitySection` uses chapter-level column specs when emitting activity tables.
- `sectionColumnSpecs(section)` accumulates activity tables until a `PageBreak`, flushes one shared `columns: (...)` spec for that chapter, then starts a new chapter.
- `tableColumnWidthsCM(tables)` emits six absolute `cm` widths using `activityTableTotalWidthCM`.
- `columnPressures(tables)` derives weighted pressure from group titles, activity titles, learning content, student activity, teacher activity, teaching method, and hours.
- `headerMinWidthCM(metric, bias)` preserves minimum widths for `教学活动`, `学习内容`, `学生活动`, `教师活动`, `教学方法与手段`, and `课时分配`.

Official tests used as behavioral evidence:

- `TestTableColumnWidthsPreserveHeaderRow`
- `TestGenerateTypstCentersTeachingMethodAndRemovesTableGap`
- `TestGenerateTypstUsesSameColumnWidthsWithinChapter`

## Pre-Fix Reproduction

Temporary output directory: `/tmp/jiaoan-shicao-phase27-prefix.5urAny`

Commands:

```bash
tmpdir=$(mktemp -d /tmp/jiaoan-shicao-phase27-prefix.XXXXXX)
LC_ALL=C skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example --output "$tmpdir/jiaoan-shicao-full.md"
LC_ALL=C skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --input "$tmpdir/jiaoan-shicao-full.md" --typ "$tmpdir/jiaoan-shicao.typ"
test -f "$tmpdir/jiaoan-shicao.typ"
rg -n "columns: \(" "$tmpdir/jiaoan-shicao.typ" | head -12
rg -n "table_columns_for_task|emit_activity_group|activityTableTotalWidthCM|func sectionColumnSpecs|func tableColumnWidthsCM|func columnPressures|func headerMinWidthCM|TestTableColumnWidthsPreserveHeaderRow|TestGenerateTypstCentersTeachingMethodAndRemovesTableGap|TestGenerateTypstUsesSameColumnWidthsWithinChapter" \
  /private/tmp/presto-jiaoan-shicao-main.go \
  /private/tmp/presto-jiaoan-shicao-main_test.go \
  skills/jiaoan-shicao/scripts/render_v110_typst.awk
```

Results:

- `example` exit status: 0
- `render` exit status: 0
- Typst output exists: yes
- Generated files stayed under `/tmp` and were not staged.

Pre-fix generated activity-table column examples:

```text
/tmp/jiaoan-shicao-phase27-prefix.5urAny/jiaoan-shicao.typ:182:      columns: (4.84cm, 4.84cm, 4.84cm, 4.84cm, 8.12cm, 4.84cm),
/tmp/jiaoan-shicao-phase27-prefix.5urAny/jiaoan-shicao.typ:202:      columns: (4.84cm, 4.84cm, 4.84cm, 4.84cm, 8.12cm, 4.84cm),
```

Pre-fix local AWK gap:

- `skills/jiaoan-shicao/scripts/render_v110_typst.awk:257` defines `table_columns_for_task(i)`.
- `skills/jiaoan-shicao/scripts/render_v110_typst.awk:497` defines `emit_activity_group(i, g)`.
- `skills/jiaoan-shicao/scripts/render_v110_typst.awk:501` emits `columns: (` by calling `table_columns_for_task(i)`.
- This means the current local renderer calculates activity-table width by learning task instead of official chapter/pagebreak scope.
