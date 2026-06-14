---
phase: 27
plan: 01
name: official-activity-table-width-alignment
type: execute
wave: 1
depends_on:
  - phase: 26
    provides: "package-side inferred `起止日期` backfill into generated `jiaoan-shicao-full.md`"
files_modified:
  - skills/jiaoan-shicao/scripts/render_v110_typst.awk
  - skills/jiaoan-shicao/references/format-and-rendering.md
  - test/1.10/电气设备控制线路安装与调试教案.typ
  - .planning/phases/27-official-activity-table-width-alignment/27-VERIFICATION.md
autonomous: true
requirements:
  - TDPR-04
  - TDPR-05
  - TDPR-06
  - TDPR-07
must_haves:
  truths:
    - D-01 use `/private/tmp/presto-jiaoan-shicao-main.go` as the canonical algorithm reference for `activityTableTotalWidthCM`, `sectionColumnSpecs`, `tableColumnWidthsCM`, and `columnPressures`.
    - D-02 preserve `activityTableTotalWidthCM = 25.04`; generated activity-table columns must sum to `25.04cm` within a small rounding tolerance.
    - D-03 preserve official header minimum widths from `headerMinWidthCM(metric, bias)` for `教学活动`, `学习内容`, `学生活动`, `教师活动`, `教学方法与手段`, and `课时分配`.
    - D-04 preserve the official weight shape: base weights `0.5, 1.8, 1.6, 1.6, 0.18, 0.06`; pressure scales `0.22, 1.0, 0.95, 0.95, 0.18, 0.05`; initial pressures `1, 1, 1, 1, 0.5, 0.25`.
    - D-05 keep `课时分配` narrower than `学习内容`, `学生活动`, and `教师活动`.
    - D-06 repair the grouping mismatch: official `sectionColumnSpecs(section)` groups tables by chapter/pagebreak, while current AWK `table_columns_for_task(i)` groups by learning task.
    - D-07 tables before the same `{pagebreak}` must share identical `columns: (...)`; tables after a `{pagebreak}` may recalculate.
    - D-08 keep the current `emit_activity_group(i, g)` per-group table emission shape unless a narrower AWK change cannot satisfy official invariants.
    - D-09 record `{pagebreak}` boundaries while parsing activity mode instead of dropping them as ordinary content.
    - D-10 do not use the official Go renderer as a runtime dependency; it is evidence and test-oracle material only.
    - D-11 preserve `jiaoan-shicao.sh` public commands and flags: `example`, `render`, `manifest`, `info`, `version`, and `--expected-typ`.
    - D-12 preserve existing Markdown authoring syntax: `## 教学活动设计`, `### 学习环节——学习单元`, `#### 活动名称`, `##### 课时`, and `{pagebreak}`.
    - D-13 if the v1.10 strict fixture output changes only because official width alignment changes `columns: (...)`, record that reason and update expected evidence deliberately.
    - D-14 preserve Phase 26 date backfill; package-path verification must still prove generated `jiaoan-shicao-full.md` contains filled `起止日期：` values.
    - D-15 do not stage or commit generated `deliverables/` artifacts; use `/tmp` and phase evidence docs for generated verification artifacts.
    - D-16 local width reproduction must verify total width, narrow `课时分配`, same-chapter shared columns, centered teaching-method cells, and absolute `cm` widths.
    - D-17 direct `jiaoan-shicao` verification must generate Markdown, Typst, inspect `columns: (...)`, and compile PDF if Typst is available.
    - D-18 integrated package verification must generate package outputs, check filled `起止日期`, inspect width invariants, and compile PDF if Typst is available.
    - D-19 PDF success requires a real output file; otherwise record `missing_compiler`, `not_run`, or `failed`.
    - D-20 run script syntax/smoke checks and `git diff --check`; use `git diff --cached --check` before any commit.
---

<objective>
Repair the standalone `jiaoan-shicao` `教学活动设计` table-width calculation so generated Typst follows the official template algorithm: `25.04cm` total activity-table width, official header/pressure weighting, identical column specifications within each chapter, recalculation after `{pagebreak}`, and no regression to Phase 26 integrated-package date backfill.
</objective>

<threat_model>
Primary risks are false visual alignment, public command regression, accidental loss of Phase 26 package date backfill, fixture drift without evidence, and false PDF readiness. Block false alignment with black-box Typst assertions that parse `columns: (...)` and verify official invariants. Block command regression with `jiaoan-shicao.sh` public command smoke checks and by leaving `jiaoan-shicao.sh` flags unchanged. Block Phase 26 regression with an integrated package path run that checks filled `起止日期：` before rendering. Block fixture drift by documenting any intentional `columns` changes in `27-VERIFICATION.md`. Block false PDF readiness by reporting success only when `typst compile` exits 0 and the PDF file exists.
</threat_model>

<tasks>

<task id="01" type="execute">
<title>Record official width evidence and reproduce the local AWK grouping gap</title>
<read_first>
- AGENTS.md
- .planning/ROADMAP.md
- .planning/REQUIREMENTS.md
- .planning/STATE.md
- .planning/phases/27-official-activity-table-width-alignment/27-CONTEXT.md
- .planning/phases/27-official-activity-table-width-alignment/27-RESEARCH.md
- /private/tmp/presto-jiaoan-shicao-main.go
- /private/tmp/presto-jiaoan-shicao-main_test.go
- /private/tmp/presto-jiaoan-shicao-example.md
- skills/jiaoan-shicao/scripts/render_v110_typst.awk
- skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
</read_first>
<action>
Create `.planning/phases/27-official-activity-table-width-alignment/27-VERIFICATION.md` during execution and record the official evidence before implementation. Cite the local official references for `activityTableTotalWidthCM = 25.04`, `renderActivitySection`, `sectionColumnSpecs(section)`, `tableColumnWidthsCM(tables)`, `columnPressures(tables)`, `headerMinWidthCM(metric, bias)`, and the tests `TestTableColumnWidthsPreserveHeaderRow`, `TestGenerateTypstCentersTeachingMethodAndRemovesTableGap`, and `TestGenerateTypstUsesSameColumnWidthsWithinChapter`. Then generate a pre-fix direct `jiaoan-shicao` Typst output in `/tmp`, extract all activity-table `columns: (...)` lines, and record that current AWK uses `table_columns_for_task(i)` from `emit_activity_group(i, g)` rather than chapter/pagebreak-scoped specs.
</action>
<acceptance_criteria>
- `27-VERIFICATION.md` contains an `Official algorithm evidence` section naming `/private/tmp/presto-jiaoan-shicao-main.go` and `/private/tmp/presto-jiaoan-shicao-main_test.go`.
- The evidence section records the exact constants/identifiers `activityTableTotalWidthCM = 25.04`, `sectionColumnSpecs`, `tableColumnWidthsCM`, `columnPressures`, and `headerMinWidthCM`.
- The pre-fix section records commands that run `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example --output "$tmpdir/jiaoan-shicao-full.md"` and `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --input "$tmpdir/jiaoan-shicao-full.md" --typ "$tmpdir/jiaoan-shicao.typ"`.
- The pre-fix section records at least one `columns: (...)` line from `$tmpdir/jiaoan-shicao.typ`.
- The pre-fix section explicitly states that current AWK `emit_activity_group(i, g)` calls `table_columns_for_task(i)`, so width calculation is learning-task-scoped instead of chapter/pagebreak-scoped.
- Generated reproduction files are under `/tmp` and no `deliverables/` files are staged.
</acceptance_criteria>
</task>

<task id="02" type="execute">
<title>Port official chapter/pagebreak width grouping into the AWK renderer</title>
<read_first>
- /private/tmp/presto-jiaoan-shicao-main.go
- /private/tmp/presto-jiaoan-shicao-main_test.go
- .planning/phases/27-official-activity-table-width-alignment/27-RESEARCH.md
- skills/jiaoan-shicao/scripts/render_v110_typst.awk
- skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
- skills/jiaoan-shicao/references/format-and-rendering.md
- test/1.10/电气设备控制线路安装与调试教案.md
- test/1.10/电气设备控制线路安装与调试教案.typ
</read_first>
<action>
Update `skills/jiaoan-shicao/scripts/render_v110_typst.awk` only as much as needed to reproduce official chapter grouping. Preserve the existing total-width formula and official weight values already present in `table_columns_for_task(i)`, but replace task-level grouping with chapter-level grouping derived from activity `{pagebreak}` markers. Add parser state that records each activity group as `GROUP_CHAPTER[task, group]`, increments the chapter only after a literal `{pagebreak}` in activity mode, and avoids emitting a row for that marker. Add a chapter-scoped column function such as `table_columns_for_chapter(i, chapter)` that aggregates only groups in that chapter, using the same six columns, `25.04`, header minimums, initial pressures, base weights, and pressure scales. Change `emit_activity_group(i, g)` so its `columns: (...)` argument uses the group chapter spec instead of `table_columns_for_task(i)`. Keep `jiaoan-shicao.sh` public commands and flags unchanged.
</action>
<acceptance_criteria>
- `render_v110_typst.awk` records `{pagebreak}` while `mode == "activity"` and does not append `{pagebreak}` to any activity content cell.
- `render_v110_typst.awk` contains a chapter/group mapping such as `GROUP_CHAPTER[task_count, group_count]` or an equivalent explicit data structure.
- The activity width calculation aggregates `GROUP_STAGE`, `GROUP_UNIT`, `ACT_TITLE`, `ACT_LEARN`, `ACT_STUDENT`, `ACT_TEACHER`, `ACT_METHOD`, and `ACT_HOURS` only for groups in the requested chapter.
- Generated activity columns still use the official total width literal `25.04`, initial pressures `1, 1, 1, 1, 0.5, 0.25`, base weights `0.5, 1.8, 1.6, 1.6, 0.18, 0.06`, and pressure scales `0.22, 1.0, 0.95, 0.95, 0.18, 0.05`.
- `emit_activity_group(i, g)` no longer calls `table_columns_for_task(i)` for every group unless `table_columns_for_task` itself has been redefined to accept chapter scope.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` commands and flags remain textually stable in `usage()`.
- `bash -n skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` exits 0.
</acceptance_criteria>
</task>

<task id="03" type="execute">
<title>Document the official activity-table width contract and manage fixture drift deliberately</title>
<read_first>
- skills/jiaoan-shicao/references/format-and-rendering.md
- skills/jiaoan-shicao/SKILL.md
- skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
- skills/jiaoan-shicao/scripts/render_v110_typst.awk
- test/1.10/电气设备控制线路安装与调试教案.md
- test/1.10/电气设备控制线路安装与调试教案.typ
- .planning/phases/27-official-activity-table-width-alignment/27-CONTEXT.md
- .planning/phases/27-official-activity-table-width-alignment/27-RESEARCH.md
</read_first>
<action>
Update `skills/jiaoan-shicao/references/format-and-rendering.md` with a concise renderer note: `教学活动设计` uses official-style absolute `cm` widths, the total width is `25.04cm`, multiple tables in the same chapter share the same `columns: (...)`, and `{pagebreak}` starts a new chapter that may recalculate widths. Keep `SKILL.md` concise; edit it only if it currently contradicts the new renderer contract. If the v1.10 strict target `test/1.10/电气设备控制线路安装与调试教案.typ` changes because the official table-width algorithm changes only `columns: (...)`, update it deliberately during execution and record the before/after rationale in `27-VERIFICATION.md`. Do not use the official Go renderer as a runtime dependency.
</action>
<acceptance_criteria>
- `format-and-rendering.md` contains the strings `25.04cm`, `columns: (...)`, and `{pagebreak}` in the `教学活动设计` or renderer-note context.
- The documentation says same-chapter activity tables share one column specification and pagebreak starts a new chapter for recalculation.
- `SKILL.md` is unchanged unless a concrete contradiction is found and fixed.
- If `test/1.10/电气设备控制线路安装与调试教案.typ` changes, `27-VERIFICATION.md` records that the change is limited to official-template width alignment or lists any additional intentional differences.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --input test/1.10/电气设备控制线路安装与调试教案.md --typ "$tmpdir/v110.typ"` exits 0 under the verified locale.
- If `--expected-typ test/1.10/电气设备控制线路安装与调试教案.typ` is used after updating the target, the comparison exits 0.
</acceptance_criteria>
</task>

<task id="04" type="execute">
<title>Verify direct `jiaoan-shicao` Markdown, Typst, width invariants, and PDF output</title>
<read_first>
- skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
- skills/jiaoan-shicao/scripts/render_v110_typst.awk
- skills/jiaoan-shicao/templates/jiaoan-shicao-full.md
- /private/tmp/presto-jiaoan-shicao-main_test.go
- /private/tmp/presto-jiaoan-shicao-example.md
- .planning/phases/27-official-activity-table-width-alignment/27-VERIFICATION.md
</read_first>
<action>
Run direct `jiaoan-shicao` black-box verification in a temporary directory. Generate Markdown with `example`, render Typst, parse activity-table `columns: (...)` lines, and assert official invariants: every activity table uses six absolute `cm` widths; each width list sums to `25.04` within `0.02`; column 6 is narrower than columns 2, 3, and 4; two tables before the first `{pagebreak}` share identical columns; a post-pagebreak table is allowed to differ; `align(center + horizon)` remains present for teaching-method cells. Compile a direct PDF with `typst compile` if available, and record `missing_compiler` or `failed` honestly otherwise.
</action>
<acceptance_criteria>
- `jiaoan-shicao.sh example --output "$tmpdir/jiaoan-shicao-full.md"` exits 0.
- `jiaoan-shicao.sh render --input "$tmpdir/jiaoan-shicao-full.md" --typ "$tmpdir/jiaoan-shicao.typ"` exits 0.
- `$tmpdir/jiaoan-shicao.typ` exists and contains activity-table `columns: (` lines with `cm` units.
- A recorded parser/assertion proves every checked activity width list has exactly six values and total width between `25.02` and `25.06`.
- A recorded parser/assertion proves column 6 is less than columns 2, 3, and 4 for each checked activity table.
- A recorded assertion proves at least two same-chapter activity tables have identical `columns: (...)`.
- `rg -n "align\\(center \\+ horizon\\)" "$tmpdir/jiaoan-shicao.typ"` exits 0.
- If `command -v typst` succeeds, `typst compile "$tmpdir/jiaoan-shicao.typ" "$tmpdir/jiaoan-shicao.pdf"` exits 0 and `$tmpdir/jiaoan-shicao.pdf` exists before PDF status is recorded as passed.
- If PDF compilation is unavailable or fails, `27-VERIFICATION.md` records `missing_compiler` or `failed` with the real command result.
</acceptance_criteria>
</task>

<task id="05" type="execute">
<title>Verify integrated package regression path and finish Phase 27 evidence</title>
<read_first>
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
- skills/jiaoan-shicao/scripts/render_v110_typst.awk
- .planning/phases/26-package-date-backfill-repair/26-VERIFICATION.md
- .planning/phases/27-official-activity-table-width-alignment/27-VERIFICATION.md
- .planning/REQUIREMENTS.md
</read_first>
<action>
Run the integrated package path after the AWK repair: generate `package.md`, run `plan-split`, assert generated `jiaoan-shicao-full.md` still has filled `起止日期：YYYY-MM-DD - YYYY-MM-DD` values and no blank `起止日期：` lines, run `render-split`, assert `lesson-plans.typ` contains official activity-table width invariants, and compile `lesson-plans.pdf` plus `teaching-plan.pdf` if Typst is available. Record public command smoke checks for `jiaoan-shicao.sh` and package commands, repository cleanliness, generated-artifact discipline, and TDPR-04/TDPR-05/TDPR-06/TDPR-07 traceability in `27-VERIFICATION.md`.
</action>
<acceptance_criteria>
- `skills/teaching-design-package/scripts/teaching-design-package.sh example --output "$tmpdir/package.md"` exits 0.
- `skills/teaching-design-package/scripts/teaching-design-package.sh plan-split --input "$tmpdir/package.md" --out-dir "$tmpdir/out"` exits 0.
- An assertion equivalent to `awk '/^起止日期：/{ if ($0 ~ /^起止日期：[[:space:]]*$/) empty++; else if ($0 ~ /^起止日期：[[:space:]]*[0-9]{4}-[0-9]{2}-[0-9]{2} - [0-9]{4}-[0-9]{2}-[0-9]{2}[[:space:]]*$/) filled++; } END { exit !(filled >= 1 && empty == 0) }' "$tmpdir/out/jiaoan-shicao-full.md"` exits 0.
- `skills/teaching-design-package/scripts/teaching-design-package.sh render-split --input "$tmpdir/package.md" --out-dir "$tmpdir/render"` exits 0.
- `$tmpdir/render/lesson-plans.typ` and `$tmpdir/render/teaching-plan.typ` exist.
- The same width-invariant parser used for direct `jiaoan-shicao` verification passes against `$tmpdir/render/lesson-plans.typ`.
- If `command -v typst` succeeds, `typst compile "$tmpdir/render/lesson-plans.typ" "$tmpdir/render/lesson-plans.pdf"` and `typst compile "$tmpdir/render/teaching-plan.typ" "$tmpdir/render/teaching-plan.pdf"` exit 0 and both PDF files exist before PDF status is recorded as passed.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh info`, `version`, and `manifest` exit 0.
- `skills/teaching-design-package/scripts/teaching-design-package.sh info` and `version` exit 0.
- `git diff --check` exits 0, and `git diff --cached --check` exits 0 before any commit.
- `git status --short` shows no staged generated `deliverables/` artifacts.
- `27-VERIFICATION.md` maps TDPR-04, TDPR-05, TDPR-06, and TDPR-07 to passing evidence or honest failure status.
</acceptance_criteria>
</task>

</tasks>

<verification>
At minimum, execute Phase 27 with these verification commands and record outcomes in `.planning/phases/27-official-activity-table-width-alignment/27-VERIFICATION.md`. Use `LC_ALL=C` for the shell/AWK render path if the environment reproduces the known locale-sensitive task-count issue from Phase 26.

```bash
bash -n skills/jiaoan-shicao/scripts/jiaoan-shicao.sh

tmpdir="$(mktemp -d /tmp/jiaoan-shicao-phase27.XXXXXX)"
LC_ALL=C skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example --output "$tmpdir/jiaoan-shicao-full.md"
LC_ALL=C skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --input "$tmpdir/jiaoan-shicao-full.md" --typ "$tmpdir/jiaoan-shicao.typ"
test -f "$tmpdir/jiaoan-shicao.typ"
rg -n "columns: \\(|align\\(center \\+ horizon\\)" "$tmpdir/jiaoan-shicao.typ"

awk '
  /columns: \(/ && $0 ~ /cm/ {
    line=$0
    gsub(/^.*columns: \(/, "", line)
    gsub(/\).*$/, "", line)
    n=split(line, parts, ",")
    if (n == 6) {
      total=0
      for (i=1; i<=6; i++) {
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", parts[i])
        gsub(/cm$/, "", parts[i])
        w[i]=parts[i]+0
        total+=w[i]
      }
      checked++
      if (total < 25.02 || total > 25.06) bad_total++
      if (!(w[6] < w[2] && w[6] < w[3] && w[6] < w[4])) bad_hours++
      spec=sprintf("%.2f,%.2f,%.2f,%.2f,%.2f,%.2f", w[1], w[2], w[3], w[4], w[5], w[6])
      if (checked == 1) first=spec
      if (checked == 2) second=spec
    }
  }
  END {
    printf "width_assertion checked=%d bad_total=%d bad_hours=%d same_first_two=%s\n", checked, bad_total+0, bad_hours+0, (first == second ? "yes" : "no")
    exit !(checked >= 2 && bad_total == 0 && bad_hours == 0 && first == second)
  }
' "$tmpdir/jiaoan-shicao.typ"

if command -v typst >/dev/null 2>&1; then
  typst compile "$tmpdir/jiaoan-shicao.typ" "$tmpdir/jiaoan-shicao.pdf"
  test -f "$tmpdir/jiaoan-shicao.pdf"
else
  printf 'direct PDF status: missing_compiler (typst not found)\n'
fi

pkgdir="$(mktemp -d /tmp/tdp-phase27.XXXXXX)"
LC_ALL=C skills/teaching-design-package/scripts/teaching-design-package.sh example --output "$pkgdir/package.md"
LC_ALL=C skills/teaching-design-package/scripts/teaching-design-package.sh plan-split --input "$pkgdir/package.md" --out-dir "$pkgdir/out"
awk '/^起止日期：/{
  if ($0 ~ /^起止日期：[[:space:]]*$/) empty++;
  else if ($0 ~ /^起止日期：[[:space:]]*[0-9]{4}-[0-9]{2}-[0-9]{2} - [0-9]{4}-[0-9]{2}-[0-9]{2}[[:space:]]*$/) filled++;
}
END {
  printf "date_assertion filled=%d empty=%d\n", filled+0, empty+0;
  exit !(filled >= 1 && empty == 0)
}' "$pkgdir/out/jiaoan-shicao-full.md"

LC_ALL=C skills/teaching-design-package/scripts/teaching-design-package.sh render-split --input "$pkgdir/package.md" --out-dir "$pkgdir/render"
test -f "$pkgdir/render/lesson-plans.typ"
test -f "$pkgdir/render/teaching-plan.typ"

if command -v typst >/dev/null 2>&1; then
  typst compile "$pkgdir/render/lesson-plans.typ" "$pkgdir/render/lesson-plans.pdf"
  test -f "$pkgdir/render/lesson-plans.pdf"
  typst compile "$pkgdir/render/teaching-plan.typ" "$pkgdir/render/teaching-plan.pdf"
  test -f "$pkgdir/render/teaching-plan.pdf"
else
  printf 'package PDF status: missing_compiler (typst not found)\n'
fi

skills/jiaoan-shicao/scripts/jiaoan-shicao.sh info
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh version
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh manifest
skills/teaching-design-package/scripts/teaching-design-package.sh info
skills/teaching-design-package/scripts/teaching-design-package.sh version
git diff --check
git diff --cached --check
git status --short
```

The width assertion must be run against both the direct `jiaoan-shicao.typ` and the integrated package `lesson-plans.typ`, adapting only the input path. The PDF checks may report `missing_compiler` or `failed`, but must not report success unless the real PDF file exists.
</verification>

<success_criteria>
- `render_v110_typst.awk` computes `教学活动设计` columns from official-style chapter/pagebreak groups rather than whole learning tasks.
- Generated activity-table width lists use six absolute `cm` widths that sum to `25.04cm` within tolerance.
- Same-chapter activity tables share identical `columns: (...)`, and `{pagebreak}` starts a recalculation boundary.
- The `课时分配` column remains narrower than `学习内容`, `学生活动`, and `教师活动`.
- `jiaoan-shicao.sh` public commands and flags remain stable.
- Phase 26 package date backfill is preserved in the integrated package path.
- Markdown, Typst, and honest PDF evidence are recorded for direct `jiaoan-shicao` and integrated package paths.
- No generated `deliverables/` artifacts are staged or committed.
</success_criteria>
