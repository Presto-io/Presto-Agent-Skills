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

## Implementation Evidence

Implementation commits:

- `4240adf docs(27-01): record official width evidence`
- `a0aca60 fix(27-01): align activity columns by chapter`

The AWK renderer now records activity `{pagebreak}` boundaries as chapter transitions and maps each group to its chapter:

- `GROUP_CHAPTER[task_count, group_count] = activity_chapter`
- `table_columns_for_chapter(i, chapter)` aggregates only groups from the requested chapter.
- `emit_activity_group(i, g)` emits `columns: (` from `table_columns_for_chapter(i, GROUP_CHAPTER[i, g])`.

The v1.10 strict target Typst was updated deliberately because the official-template repair changes `教学活动设计` `columns: (...)` values from old task-wide widths to chapter/pagebreak-scoped widths. The verified differences are limited to official activity-table width alignment.

## Post-Fix Direct `jiaoan-shicao` Verification

Temporary output directory: `/tmp/jiaoan-shicao-phase27-direct.WVgrvq`

Commands:

```bash
bash -n skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
LC_ALL=C skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example --output "$tmpdir/jiaoan-shicao-full.md"
LC_ALL=C skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --input "$tmpdir/jiaoan-shicao-full.md" --typ "$tmpdir/jiaoan-shicao.typ"
test -f "$tmpdir/jiaoan-shicao.typ"
rg -n "columns: \(|align\(center \+ horizon\)" "$tmpdir/jiaoan-shicao.typ"
typst compile "$tmpdir/jiaoan-shicao.typ" "$tmpdir/jiaoan-shicao.pdf"
test -f "$tmpdir/jiaoan-shicao.pdf"
```

`LC_ALL=C` was used for shell/AWK render commands because Phase 26 exposed a locale-sensitive task-count path in the same renderer family under the default Chinese locale. The C locale keeps AWK character/count behavior deterministic for this regression run.

Results:

- `bash -n`: passed.
- `example`: passed and wrote `/tmp/jiaoan-shicao-phase27-direct.WVgrvq/jiaoan-shicao-full.md`.
- `render`: passed and wrote `/tmp/jiaoan-shicao-phase27-direct.WVgrvq/jiaoan-shicao.typ`.
- `align(center + horizon)`: present for teaching-method cells.
- PDF: passed; Typst compiler found at `/opt/homebrew/bin/typst` and produced `/tmp/jiaoan-shicao-phase27-direct.WVgrvq/jiaoan-shicao.pdf`.

Width parser result:

```text
activity_columns[1]=2.43,4.91,6.24,6.17,3.31,1.98 total=25.04
activity_columns[2]=2.43,4.91,6.24,6.17,3.31,1.98 total=25.04
activity_columns[3]=2.43,4.91,6.24,6.17,3.31,1.98 total=25.04
activity_columns[4]=2.43,4.91,6.24,6.17,3.31,1.98 total=25.04
activity_columns[5]=2.43,4.91,6.24,6.17,3.31,1.98 total=25.04
activity_columns[6]=2.43,4.91,6.24,6.17,3.31,1.98 total=25.04
activity_columns[7]=2.43,4.91,6.24,6.17,3.31,1.98 total=25.04
activity_columns[8]=2.46,5.01,6.16,6.11,3.31,1.98 total=25.03
activity_columns[9]=2.46,5.01,6.16,6.11,3.31,1.98 total=25.03
activity_columns[10]=2.46,5.01,6.16,6.11,3.31,1.98 total=25.03
activity_columns[11]=2.46,5.01,6.16,6.11,3.31,1.98 total=25.03
activity_columns[12]=2.46,5.01,6.16,6.11,3.31,1.98 total=25.03
activity_columns[13]=2.46,5.01,6.16,6.11,3.31,1.98 total=25.03
activity_columns[14]=2.44,4.92,6.21,6.17,3.32,1.98 total=25.04
activity_columns[15]=2.44,4.92,6.21,6.17,3.32,1.98 total=25.04
activity_columns[16]=2.44,4.92,6.21,6.17,3.32,1.98 total=25.04
activity_columns[17]=2.44,4.92,6.21,6.17,3.32,1.98 total=25.04
activity_columns[18]=2.44,4.92,6.21,6.17,3.32,1.98 total=25.04
activity_columns[19]=2.44,4.92,6.21,6.17,3.32,1.98 total=25.04
direct_width_assertion checked=19 bad_hours=0 same_first_two=yes
```

Assertions covered:

- Every checked activity table uses six absolute `cm` widths.
- Width totals are within `25.02` to `25.06`; observed totals are `25.03` or `25.04`.
- Column 6 (`课时分配`) is narrower than columns 2, 3, and 4 for every checked table.
- The first two same-chapter activity tables share identical `columns: (...)`.
- Later chapters after pagebreaks can recalculate widths; observed chapter specs differ after the first chapter.

## Post-Fix Integrated Package Verification

Temporary output directory: `/tmp/tdp-phase27.fN4RQk`

Commands:

```bash
LC_ALL=C skills/teaching-design-package/scripts/teaching-design-package.sh example --output "$pkgdir/package.md"
LC_ALL=C skills/teaching-design-package/scripts/teaching-design-package.sh plan-split --input "$pkgdir/package.md" --out-dir "$pkgdir/out"
awk '/^起止日期：/{ if ($0 ~ /^起止日期：[[:space:]]*$/) empty++; else if ($0 ~ /^起止日期：[[:space:]]*[0-9]{4}-[0-9]{2}-[0-9]{2} - [0-9]{4}-[0-9]{2}-[0-9]{2}[[:space:]]*$/) filled++; } END { printf "date_assertion filled=%d empty=%d\n", filled+0, empty+0; exit !(filled >= 1 && empty == 0) }' "$pkgdir/out/jiaoan-shicao-full.md"
LC_ALL=C skills/teaching-design-package/scripts/teaching-design-package.sh render-split --input "$pkgdir/package.md" --out-dir "$pkgdir/render"
test -f "$pkgdir/render/lesson-plans.typ"
test -f "$pkgdir/render/teaching-plan.typ"
typst compile "$pkgdir/render/lesson-plans.typ" "$pkgdir/render/lesson-plans.pdf"
typst compile "$pkgdir/render/teaching-plan.typ" "$pkgdir/render/teaching-plan.pdf"
test -f "$pkgdir/render/lesson-plans.pdf"
test -f "$pkgdir/render/teaching-plan.pdf"
```

Results:

- Package example: passed and wrote `/tmp/tdp-phase27.fN4RQk/package.md`.
- `plan-split`: passed.
- Date backfill assertion: `date_assertion filled=3 empty=0`.
- `render-split`: passed and wrote `teaching-plan.typ` and `lesson-plans.typ`.
- `align(center + horizon)`: present in `lesson-plans.typ`.
- PDF: passed; produced `/tmp/tdp-phase27.fN4RQk/render/lesson-plans.pdf` and `/tmp/tdp-phase27.fN4RQk/render/teaching-plan.pdf`.

Width parser result for integrated `lesson-plans.typ`:

```text
package_activity_columns[1]=2.43,4.91,6.24,6.17,3.31,1.98 total=25.04
package_activity_columns[2]=2.43,4.91,6.24,6.17,3.31,1.98 total=25.04
package_activity_columns[3]=2.43,4.91,6.24,6.17,3.31,1.98 total=25.04
package_activity_columns[4]=2.43,4.91,6.24,6.17,3.31,1.98 total=25.04
package_activity_columns[5]=2.43,4.91,6.24,6.17,3.31,1.98 total=25.04
package_activity_columns[6]=2.43,4.91,6.24,6.17,3.31,1.98 total=25.04
package_activity_columns[7]=2.43,4.91,6.24,6.17,3.31,1.98 total=25.04
package_activity_columns[8]=2.46,5.01,6.16,6.11,3.31,1.98 total=25.03
package_activity_columns[9]=2.46,5.01,6.16,6.11,3.31,1.98 total=25.03
package_activity_columns[10]=2.46,5.01,6.16,6.11,3.31,1.98 total=25.03
package_activity_columns[11]=2.46,5.01,6.16,6.11,3.31,1.98 total=25.03
package_activity_columns[12]=2.46,5.01,6.16,6.11,3.31,1.98 total=25.03
package_activity_columns[13]=2.46,5.01,6.16,6.11,3.31,1.98 total=25.03
package_activity_columns[14]=2.44,4.92,6.21,6.17,3.32,1.98 total=25.04
package_activity_columns[15]=2.44,4.92,6.21,6.17,3.32,1.98 total=25.04
package_activity_columns[16]=2.44,4.92,6.21,6.17,3.32,1.98 total=25.04
package_activity_columns[17]=2.44,4.92,6.21,6.17,3.32,1.98 total=25.04
package_activity_columns[18]=2.44,4.92,6.21,6.17,3.32,1.98 total=25.04
package_activity_columns[19]=2.44,4.92,6.21,6.17,3.32,1.98 total=25.04
package_width_assertion checked=19 bad_hours=0 same_first_two=yes
```

## Strict Fixture Verification

Command:

```bash
LC_ALL=C skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input test/1.10/电气设备控制线路安装与调试教案.md \
  --typ /tmp/phase27-v110.typ \
  --expected-typ test/1.10/电气设备控制线路安装与调试教案.typ
```

Result:

```text
wrote /tmp/phase27-v110.typ
verified Typst matches test/1.10/电气设备控制线路安装与调试教案.typ
```

## Public Command Smoke Checks

Commands:

```bash
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh info
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh version
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh manifest
skills/teaching-design-package/scripts/teaching-design-package.sh info
skills/teaching-design-package/scripts/teaching-design-package.sh version
```

Result: all commands exited 0.

## Repository Hygiene

- Generated Markdown, Typst, and PDF artifacts stayed under `/tmp`.
- No `deliverables/` files were staged or committed.
- `git diff --check`: passed.
- `git diff --cached --check`: run before final commit and passed.

## Requirement Traceability

| Requirement | Evidence | Status |
|-------------|----------|--------|
| TDPR-04 | AWK renderer now uses official-style chapter/pagebreak grouping and `25.04cm` activity-table total width. | Passed |
| TDPR-05 | Direct and package width parsers checked 19 activity tables each, narrow `课时分配`, and same-chapter shared specs. | Passed |
| TDPR-06 | Package path generated Markdown, Typst, lesson-plan PDF, teaching-plan PDF, and verified `起止日期` filled with `filled=3 empty=0`. | Passed |
| TDPR-07 | Direct path generated Markdown, Typst, PDF, and records official-template basis plus local reproduction evidence. | Passed |

## Phase 27 Verification Passed

Phase 27 execution satisfies the plan success criteria. The official activity-table width repair is verified for the standalone `jiaoan-shicao` path and the integrated `teaching-design-package` path.
