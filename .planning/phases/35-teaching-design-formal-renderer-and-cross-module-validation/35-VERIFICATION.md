---
phase: 35
plan: 01
status: passed
verified_at: "2026-06-15T08:37:16Z"
commits: [6feef9d, 87d4b05, 61f18f2]
requirements: [TDPKG-LEGACY-02, TDPKG-VAL-02, TDPKG-VAL-03, TDPKG-VAL-04]
---

# Phase 35 Verification

## Result

Passed. `teaching-design-package` now generates a package-owned formal hidden
`teaching-design.typ` and real `teaching-design.pdf` from the unified Markdown
and shared scheduling model. Cross-module validation fails hard on task, stage,
activity, title, hour, and date mismatches with hidden diagnostics.

Recovery update: the GSD execution-state check was refreshed after the plan
summary existed on disk. Current `gsd-sdk query init.execute-phase 35` reports
`incomplete_count: 0` and `incomplete_plans: []`.

Verification root:

```text
/var/folders/kh/3z1m41y56mgd98lxmb9zjjsw0000gn/T/tdpkg-phase35-verify.XXXXXX.Xl1m7JJHzz
```

## Syntax Checks

```bash
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh
node --check skills/teaching-design-package/scripts/package-model.js
node --check skills/teaching-design-package/scripts/teaching-plan-renderer.js
node --check skills/teaching-design-package/scripts/teaching-design-renderer.js
typst --version
```

Observed:

```text
typst 0.14.2 (unknown hash)
```

## Structured Mapping And PDF

```bash
skills/teaching-design-package/scripts/teaching-design-package.sh example --output "$verify_root/package.md"
skills/teaching-design-package/scripts/teaching-design-package.sh model --input "$verify_root/package.md" > "$verify_root/model.json"
skills/teaching-design-package/scripts/teaching-design-package.sh render-package --pdf --input "$verify_root/package.md" --out-dir "$verify_root/out"
test -s "$verify_root/out/teaching-design.pdf"
test -s "$verify_root/out/teaching-plan.pdf"
test -s "$verify_root/out/teaching-design-package.pdf"
```

Model assertions passed:

```text
structured_mapping_ok tasks=3 stages=19 activities=54
```

Verified:

- every `teaching_design.tasks[].derived_total_hours` equals `schedule.tasks[].total_hours`;
- every mapped activity `derived_hours` equals `schedule.tasks[].stages[].rows[].hours`;
- hidden `teaching-design.typ` contains no `Pre-formal surface only` or Phase 33 placeholder text;
- formal surface markers exist: `教学设计方案（二）`, `学习任务分析`, `教学活动设计`, `学业评价`, `25.04cm`, `课时分配`, `course_attribute`, `total_hours`, `use_time`;
- `status.json` records `teaching_design_formal_renderer.status: passed`, `cross_module_validation: passed`, and `teaching_design_pdf: passed`.

## Negative Mismatch Fixtures

Each fixture exited non-zero and wrote hidden diagnostics with calendar path/hash,
model version, source Markdown, expected/actual values, and source pointers.

```text
teaching_design_task_count_mismatch: ok
teaching_design_stage_count_mismatch: ok
teaching_design_activity_count_mismatch: ok
teaching_design_task_title_mismatch: ok
teaching_design_stage_title_mismatch: ok
teaching_design_activity_title_mismatch: ok
teaching_design_task_hours_mismatch: ok
teaching_design_activity_hours_mismatch: ok
teaching_design_task_date_range_mismatch: ok
```

## Legacy Equivalence

Raw `test/1.10/电气设备控制线路安装与调试教案.md` is not directly acceptable as a
Phase 35 package input because its task/activity titles drift from the schedule
oracle. The package correctly rejects it:

```text
legacy_raw_rejected=teaching_design_task_title_mismatch
```

For documented acceptable equivalence, the verification built a fixture-equivalent
package input from:

- `test/1.10/电气设备控制线路安装与调试授课计划.md`;
- `test/1.10/电气设备控制线路安装与调试教案.md`;
- title corrections that make the teaching-design section match schedule row
  titles exactly;
- package frontmatter using the same course, class, teacher, textbook, and first
  teaching day facts.

The package-owned formal renderer passed:

```text
legacy_equivalent_ok activities=54 use_time=5月11日--6月5日
```

Hashes and sizes:

```text
d4a794f0d6b7f87bcc91756252a5ba983a678fdb6371c1915bf511339bb6155b  test/1.10/电气设备控制线路安装与调试教案.typ
a59e82a700e6fec0a1046a12532dd7c35b38f5db4a8738cb8033ae87ae1d0b24  test/1.10/电气设备控制线路安装与调试教案.pdf
93b51b35996b8dc69f82551bd3d9f981da2fa92fb3b9185ea6f83798f2c4ba2a  generated package teaching-design.typ
288f83baee623b9173902d9cb2649e10d814e02308d2fe04d8305ae8bf94ad2e  generated package teaching-design.pdf

67916  test/1.10/电气设备控制线路安装与调试教案.typ
553111 test/1.10/电气设备控制线路安装与调试教案.pdf
65583  generated package teaching-design.typ
531689 generated package teaching-design.pdf
```

Allowed differences:

- package provenance and scheduling evidence comments;
- task dates and `use_time` derived from the shared scheduling model;
- task/activity hours derived from `# 授课进度计划` rows;
- title corrections required by strict Phase 35 cross-module validation.

These differences do not weaken the legacy surface check: the formal cover,
learning-task analysis, landscape activity tables, evaluation pages, table width,
activity order, and representative body text are present.

## Standalone Copy

```bash
mkdir -p "$verify_root/standalone/skills"
cp -R skills/teaching-design-package "$verify_root/standalone/skills/"
"$verify_root/standalone/skills/teaching-design-package/scripts/teaching-design-package.sh" example --output "$verify_root/standalone/package.md"
"$verify_root/standalone/skills/teaching-design-package/scripts/teaching-design-package.sh" model --input "$verify_root/standalone/package.md" > "$verify_root/standalone/model.json"
"$verify_root/standalone/skills/teaching-design-package/scripts/teaching-design-package.sh" render-package --pdf --input "$verify_root/standalone/package.md" --out-dir "$verify_root/standalone/out"
test -s "$verify_root/standalone/out/teaching-design.pdf"
! rg 'Pre-formal surface only|Phase 33 module Typst intermediate|skills/jiaoan-shicao|skills/jiaoan-jihua' \
  "$verify_root/standalone/out/.teaching-design-package/work/teaching-design.typ" \
  "$verify_root/standalone/out/.teaching-design-package/model.json" \
  "$verify_root/standalone/out/.teaching-design-package/status.json" \
  "$verify_root/standalone/out/.teaching-design-package/diagnostics.json" \
  "$verify_root/standalone/model.json"
```

Passed. The copied package used its own `references/calendar.json` and did not
need sibling skill folders.

## Public Root Leakage

```bash
! find "$verify_root/out" -maxdepth 1 -type f -print | \
  rg 'teaching-plan[.]md|teaching-design[.]md|teaching-plan[.]typ|teaching-design[.]typ|calendar[.]json|model[.]json|status[.]json|diagnostics[.]json|log'
```

Passed. The public root contains only:

```text
teaching-design-package-full.md
teaching-design-package.typ
teaching-design-package.pdf
teaching-plan.pdf
teaching-design.pdf
```

## Legacy Skill Preservation

```bash
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example --output "$verify_root/jiaoan-smoke.md"
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input test/1.10/电气设备控制线路安装与调试教案.md \
  --typ "$verify_root/jiaoan-smoke.typ"
test -s "$verify_root/jiaoan-smoke.typ"
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input test/1.10/电气设备控制线路安装与调试教案.md \
  --typ "$verify_root/jiaoan-smoke-expected.typ" \
  --expected-typ test/1.10/电气设备控制线路安装与调试教案.typ
test -z "$(git diff --name-only -- skills/jiaoan-shicao)"
! rg 'skills/jiaoan-shicao|jiaoan-shicao[.]sh|skills/jiaoan-shicao/references/calendar[.]json|test/1[.]10/.+教案[.]typ' \
  skills/teaching-design-package/scripts
```

Observed:

```text
wrote .../jiaoan-smoke.md
wrote .../jiaoan-smoke.typ
legacy_example_rc=0
legacy_render_rc=0
legacy_expected_typ_rc=1
ordinary_typ_nonempty_rc=0
```

`git diff --name-only -- skills/jiaoan-shicao` printed nothing.

The legacy `--expected-typ` oracle currently returns `1` in the unmodified old
skill:

```text
b6518d6e824c525935dce44e78802bd5ec0a2030d2ea99b002b7f36e56ca5c66  generated legacy Typst
d4a794f0d6b7f87bcc91756252a5ba983a678fdb6371c1915bf511339bb6155b  test/1.10/电气设备控制线路安装与调试教案.typ
67916 generated legacy Typst
67916 test/1.10/电气设备控制线路安装与调试教案.typ
```

Diff inspection shows the failure is not a command-argument issue: the old script
generates a non-empty Typst file, but its current output differs from the committed
expected oracle in rendered task-hour text and table column calculations. This is
a Phase 35 plan deviation / residual legacy evidence item, not an inline fix,
because Phase 35 forbids modifying `skills/jiaoan-shicao/`. The ordinary legacy
`example` and `render` paths remain runnable, `git diff --name-only -- skills/jiaoan-shicao`
is empty, and the package uses the old skill only as a read-only reference/oracle,
not as runtime dependency.

## GSD And Git Checks

```bash
gsd-sdk query init.execute-phase 35
git diff --check
git diff --cached --check
```

Observed:

```text
phase_found=true
plans=["35-PLAN.md"]
summaries=["35-SUMMARY.md"]
incomplete_plans=[]
plan_count=1
incomplete_count=0
```

Both git whitespace checks passed.
