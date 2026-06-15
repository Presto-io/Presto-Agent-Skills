---
phase: 34
plan: 01
status: passed
verified_at: "2026-06-15T07:30:45Z"
commits: [b0840fa, 89cc2c9, 093ceb5]
requirements: [TDPKG-LEGACY-01, TDPKG-LEGACY-03, TDPKG-LEGACY-04, TDPKG-VAL-01]
---

# Phase 34 Verification

## Result

Passed. `teaching-design-package` now generates a package-owned formal hidden
`teaching-plan.typ` and real `teaching-plan.pdf` from the unified Markdown and
shared scheduling model. Legacy `skills/jiaoan-jihua/` remained unchanged and is
not a package runtime dependency.

Verification root:

```text
/var/folders/kh/3z1m41y56mgd98lxmb9zjjsw0000gn/T//tdpkg-phase34-verify.2TRWUr
```

## Syntax Checks

```bash
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh
node --check skills/teaching-design-package/scripts/package-model.js
node --check skills/teaching-design-package/scripts/teaching-plan-renderer.js
typst --version
```

Observed:

```text
typst 0.14.2 (unknown hash)
```

## Formal Typst Surface

```bash
skills/teaching-design-package/scripts/teaching-design-package.sh example --output "$verify_root/package.md"
skills/teaching-design-package/scripts/teaching-design-package.sh model --input "$verify_root/package.md" > "$verify_root/model.json"
skills/teaching-design-package/scripts/teaching-design-package.sh render-package --input "$verify_root/package.md" --out-dir "$verify_root/out"
test -f "$verify_root/out/.teaching-design-package/work/teaching-plan.typ"
! rg 'Pre-formal surface only|Phase 33 module Typst intermediate' "$verify_root/out/.teaching-design-package/work/teaching-plan.typ"
rg '@preview/cuti:0[.]2[.]1|STSong|工学一体化课程/基本技能课程授课进度计划表|columns: \(3[.]15cm, 8[.]51cm, 1[.]12cm, 1[.]29cm, 1[.]27cm\)|专业名称|课程名称|授课教师|授课班级|系主任|教研室主任|制表' "$verify_root/out/.teaching-design-package/work/teaching-plan.typ"
```

Observed highlights:

```text
#import "@preview/cuti:0.2.1": show-cn-fakebold
font: "STSong"
工学一体化课程/基本技能课程授课进度计划表
columns: (3.15cm, 8.51cm, 1.12cm, 1.29cm, 1.27cm)
专业名称 / 课程名称 / 授课教师 / 授课班级
系主任 / 教研室主任 / 制表
```

## Strict Sum Checks

```bash
node - "$verify_root/model.json" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const evidence = model.validation.strict_sum_evidence;
const tasks = model.schedule.tasks;
const rowTotal = tasks.flatMap(t => t.stages.flatMap(s => s.rows)).reduce((sum, row) => sum + row.hours, 0);
if (rowTotal !== model.scheduling.total_hours) throw new Error(`scheduling total mismatch ${rowTotal}`);
if (rowTotal !== model.derived.total_hours) throw new Error(`derived total mismatch ${rowTotal}`);
if (rowTotal !== evidence.course.total_hours) throw new Error(`evidence total mismatch ${rowTotal}`);
for (const task of tasks) {
  const taskTotal = task.stages.flatMap(s => s.rows).reduce((sum, row) => sum + row.hours, 0);
  const taskEvidence = evidence.tasks.find(item => item.source === task.source);
  if (taskTotal !== task.total_hours || !taskEvidence || taskEvidence.total_hours !== taskTotal) throw new Error(`task total mismatch: ${task.title}`);
  for (const stage of task.stages) {
    const stageTotal = stage.rows.reduce((sum, row) => sum + row.hours, 0);
    const stageEvidence = evidence.stages.find(item => item.source === stage.source);
    if (stageTotal !== stage.total_hours || !stageEvidence || stageEvidence.total_hours !== stageTotal) throw new Error(`stage total mismatch: ${stage.title}`);
  }
}
if (model.validation.total_hours_source !== 'teaching_plan_rows') throw new Error('bad total_hours_source');
if (evidence.total_hours_source !== 'teaching_plan_rows') throw new Error('bad evidence source');
console.log(`strict_sum_ok rows=${evidence.rows.length} stages=${evidence.stages.length} tasks=${evidence.tasks.length} total=${rowTotal}`);
NODE
```

Observed:

```text
strict_sum_ok rows=54 stages=19 tasks=3 total=160
```

Forbidden derived frontmatter checks passed for:

```text
total_hours daily_hours school_year semester start_date end_date date_range validation status
```

Malformed/non-positive row checks passed for:

```text
安技教育-0 -> non_positive_hours
安技教育-1.5 -> malformed_schedule_row
安技教育 with no suffix -> malformed_schedule_row
```

## PDF Checks

```bash
skills/teaching-design-package/scripts/teaching-design-package.sh render-package --pdf --input "$verify_root/package.md" --out-dir "$verify_root/out-pdf"
test -s "$verify_root/out-pdf/teaching-plan.pdf"
test -s "$verify_root/out-pdf/teaching-design.pdf"
test -s "$verify_root/out-pdf/teaching-design-package.pdf"
node - "$verify_root/out-pdf/.teaching-design-package/status.json" # asserts plan pdf and renderer status
! find "$verify_root/out-pdf" -maxdepth 1 -type f -print | rg 'teaching-plan[.]typ|teaching-plan[.]md|model[.]json|status[.]json|diagnostics[.]json|calendar[.]json|log'
```

Observed:

```text
pdf_status plan=passed full=passed design=passed
```

The public-root leakage assertion passed. Hidden `teaching-plan.typ` remained under
`.teaching-design-package/work/`.

## Legacy Fixture Equivalence

The legacy fixture-equivalent package input was generated from:

- `test/1.10/电气设备控制线路安装与调试授课计划.md`
- package-compatible YAML mapping for `course_name`, `major_name`, `class_name`, `teachers`, and `first_teaching_day`
- a minimal `# 教学设计方案` section with no activity-hour declaration

Commands:

```bash
skills/teaching-design-package/scripts/teaching-design-package.sh render-package \
  --input "$verify_root/package-legacy.md" \
  --out-dir "$verify_root/legacy-out"

sed '/^\/\/ package-owned teaching-design-package migration/d;/^\/\/ source_markdown:/d;/^\/\/ total_hours_source:/d' \
  "$verify_root/legacy-out/.teaching-design-package/work/teaching-plan.typ" \
  > "$verify_root/package-normalized.typ"

diff -u \
  test/1.10/电气设备控制线路安装与调试授课计划.typ \
  "$verify_root/package-normalized.typ"

typst compile \
  "$verify_root/legacy-out/.teaching-design-package/work/teaching-plan.typ" \
  "$verify_root/legacy-teaching-plan.pdf"
test -s "$verify_root/legacy-teaching-plan.pdf"
```

Result: normalized diff passed.

Allowed normalized differences:

- package-owned provenance comment
- generated source path comment
- `total_hours_source` evidence comment

These differences do not affect table structure, title hierarchy, course info
fields, task/stage/content order, row weeks, row weekdays, row hours, task totals,
signature grid, or body text.

Hashes:

```text
0d681cca76cb7d6edaf7b0c76874f3f8a5b3f49ab5e00904caf9a106690e138b  test/1.10/电气设备控制线路安装与调试授课计划.typ
5297902038358b113e210095e3932223b6f9e2050393fb8b76390117f8df3ca1  test/1.10/电气设备控制线路安装与调试授课计划.pdf
51958a89e8814063e23416c7a22228e9a0bf9506de39a7f2ece2c0765425ef31  generated package teaching-plan.typ
786724cc38d92be22007f3d613b6222bfa380b6c29c92cfcf8d4060e9fd24afe  generated package teaching-plan.pdf
```

## Standalone Copy

```bash
mkdir -p "$verify_root/standalone/skills"
cp -R skills/teaching-design-package "$verify_root/standalone/skills/"
"$verify_root/standalone/skills/teaching-design-package/scripts/teaching-design-package.sh" example --output "$verify_root/standalone/package.md"
"$verify_root/standalone/skills/teaching-design-package/scripts/teaching-design-package.sh" model --input "$verify_root/standalone/package.md" > "$verify_root/standalone/model.json"
"$verify_root/standalone/skills/teaching-design-package/scripts/teaching-design-package.sh" render-package --pdf --input "$verify_root/standalone/package.md" --out-dir "$verify_root/standalone/out"
test -s "$verify_root/standalone/out/teaching-plan.pdf"
test -f "$verify_root/standalone/out/.teaching-design-package/work/teaching-plan.typ"
! rg 'Pre-formal surface only|skills/jiaoan-jihua|skills/jiaoan-shicao' "$verify_root/standalone/out/.teaching-design-package/work/teaching-plan.typ" "$verify_root/standalone/out/.teaching-design-package/model.json" "$verify_root/standalone/out/.teaching-design-package/status.json" "$verify_root/standalone/out/.teaching-design-package/diagnostics.json" "$verify_root/standalone/model.json"
```

Passed. The copied package used its own `references/calendar.json` and did not
need sibling skill folders. `teaching-design.typ` remains pre-formal by design
until Phase 35, so placeholder scanning was scoped to `teaching-plan.typ` and
machine-readable package evidence.

## Legacy Skill Preservation

```bash
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh example --output "$verify_root/jihua-smoke/jiaoan-jihua-full.md"
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render \
  --input test/1.10/电气设备控制线路安装与调试授课计划.md \
  --typ "$verify_root/jihua-smoke/jiaoan-jihua.typ"
test -z "$(git diff --name-only -- skills/jiaoan-jihua)"
! rg 'skills/jiaoan-jihua|jiaoan-jihua[.]sh|skills/jiaoan-jihua/references/calendar[.]json' skills/teaching-design-package/scripts
```

Observed:

```text
wrote .../jihua-smoke/jiaoan-jihua-full.md
wrote .../jihua-smoke/jiaoan-jihua.typ
```

`git diff --name-only -- skills/jiaoan-jihua` printed nothing.

## Final Checks

```bash
git diff --check
git diff --cached --check
gsd-sdk query init.execute-phase 34
```

`git diff --check` and `git diff --cached --check` passed during the verification
run. `init.execute-phase 34` was run at executor start and returned Phase 34 with
one incomplete plan, requirements `TDPKG-LEGACY-01`, `TDPKG-LEGACY-03`,
`TDPKG-LEGACY-04`, and `TDPKG-VAL-01`.
