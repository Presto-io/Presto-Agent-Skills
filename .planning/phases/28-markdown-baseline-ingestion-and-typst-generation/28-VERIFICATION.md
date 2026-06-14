# Phase 28 Verification: Markdown Baseline Ingestion and Typst Generation

**Phase:** 28 - Markdown Baseline Ingestion and Typst Generation
**Plan:** 01 - markdown-baseline-ingestion-and-typst-generation
**Started:** 2026-06-14T19:28:56Z

## Pre-fix baseline and gap reproduction

### Baseline identity

- Baseline path: `skills/teaching-design-package/templates/teaching-design-package-full.md`
- Baseline SHA-256 before implementation: `fa4302a2d1e4554db72524f5a3a4829e7cc04ea21ca609a79a427cf850c2a1e8`
- Baseline teacher-facing structure: unchanged at pre-fix capture time.

### Baseline semantic shape

Command:

```bash
awk '
  /^# 授课进度计划$/ { plan=1; design=0; plan_anchor++; next }
  /^# 教学设计方案$/ { design=1; plan=0; design_anchor++; next }
  plan && /^## / { plan_tasks++ }
  design && /^## 学习任务分析$/ { analysis++ }
  design && /^## 教学活动设计——学习任务/ { activity++ }
  design && /^## 学业评价$/ { evaluation++ }
  END {
    printf "counts plan_anchor=%d design_anchor=%d plan_tasks=%d analysis=%d activity=%d evaluation=%d\n", plan_anchor+0, design_anchor+0, plan_tasks+0, analysis+0, activity+0, evaluation+0
  }
' skills/teaching-design-package/templates/teaching-design-package-full.md
```

Result:

```text
counts plan_anchor=1 design_anchor=1 plan_tasks=3 analysis=3 activity=3 evaluation=3
```

`# 授课进度计划` appears before `# 教学设计方案`. The baseline has three teaching-plan task headings, three `## 学习任务分析` blocks, three `## 教学活动设计——学习任务...` blocks, and three `## 学业评价` blocks.

### Baseline frontmatter and forbidden package YAML fields

- Frontmatter fields observed: `course_name`, `major_name`, `course_attribute`, `textbook_name`, `class_name`, `teachers`, `first_teaching_day`.
- YAML `teachers` list: `["张老师"]`.
- Intended generated scalar handoff value: `teacher_name: "张老师"`.
- Forbidden teacher-maintained package YAML fields absent: `total_hours`, `school_year`, `semester`, `daily_hours`, `hour_unit`, `date_display_format`, `date_locale`, `calendar_source`, `holidays`, `makeup_days`, `source_of_truth`, `outputs`, `validation`.

Command:

```bash
node - <<'NODE'
const fs = require('fs');
const md = fs.readFileSync('skills/teaching-design-package/templates/teaching-design-package-full.md','utf8');
const fm = md.match(/^---\n([\s\S]*?)\n---/)[1];
const forbidden = ['total_hours','school_year','semester','daily_hours','hour_unit','date_display_format','date_locale','calendar_source','holidays','makeup_days','source_of_truth','outputs','validation'];
const present = forbidden.filter(k => new RegExp(`^${k}:`, 'm').test(fm));
const teachers = [...fm.matchAll(/^  - "([^"]+)"/gm)].map(m => m[1]);
console.log(`teachers=${teachers.join('、')}`);
console.log(`forbidden=${present.length ? present.join(',') : 'none'}`);
NODE
```

Result:

```text
teachers=张老师
forbidden=none
```

### Derived hours and expected scheduling facts

Command:

```bash
awk '
  /^# 授课进度计划$/ { in_plan=1; task=""; next }
  /^# 教学设计方案$/ { in_plan=0; next }
  in_plan && /^## / { task=substr($0,4); tasks[++n]=task; total[task]=0; next }
  in_plan && match($0, /-([0-9]+)$/) { h=substr($0,RSTART+1,RLENGTH-1)+0; total[task]+=h; grand+=h }
  END {
    printf "hours total=%d %s=%d %s=%d %s=%d\n", grand+0, tasks[1], total[tasks[1]]+0, tasks[2], total[tasks[2]]+0, tasks[3], total[tasks[3]]+0
  }
' skills/teaching-design-package/templates/teaching-design-package-full.md
```

Result:

```text
hours total=160 CA6140卧式车床电气控制线路安装与调试=40 X62W万能铣床电气控制线路安装与调试=60 Z3040摇臂钻床电气控制线路安装与调试=60
```

Expected date ranges from `first_teaching_day: "2026-05-11"`, built-in calendar, and default `8` hours/day:

- `CA6140=5月11日——5月15日`
- `X62W=5月18日——5月27日`
- `Z3040=5月27日——6月5日`

Expected inferred term metadata:

- `2025-2026学年第二学期`

### Pre-fix package command gap

Command:

```bash
tmpdir=$(mktemp -d /tmp/tdp-phase28-prefix.XXXXXX)
baseline="skills/teaching-design-package/templates/teaching-design-package-full.md"
skills/teaching-design-package/scripts/teaching-design-package.sh plan-split \
  --input "$baseline" \
  --out-dir "$tmpdir/out" >"$tmpdir/plan-split.out" 2>"$tmpdir/plan-split.err"
```

Observed temp directory:

```text
/tmp/tdp-phase28-prefix.zf9pnz
```

Exit status:

```text
1
```

Stdout:

```text
```

Stderr:

```text
teaching-design-package.sh: missing required section: ## 课程与整包元数据
```

Conclusion: pre-fix `plan-split` rejects the corrected baseline because `validate_package()` still requires old package sections. It does not reach scaffold generation, so the old template-copy behavior remains a known implementation gap for later tasks.

Generated reproduction files were under `/tmp`; no `deliverables/` files were staged.

## Baseline unchanged check

Final verification temp directory: `/tmp/tdp-phase28-final.nrcOzZ`

Final verification log: `/tmp/tdp-phase28-final.nrcOzZ/final-verification.log`

Baseline hash before final verification:

```text
fa4302a2d1e4554db72524f5a3a4829e7cc04ea21ca609a79a427cf850c2a1e8
```

Baseline hash after final verification:

```text
fa4302a2d1e4554db72524f5a3a4829e7cc04ea21ca609a79a427cf850c2a1e8
```

Commands passed:

```bash
diff -u skills/teaching-design-package/templates/teaching-design-package-full.md \
  /tmp/tdp-phase28-final.nrcOzZ/teaching-design-package-full.md

git diff -- skills/teaching-design-package/templates/teaching-design-package-full.md --exit-code
```

Result: maintained baseline Markdown stayed byte-identical; the generated package Markdown artifact from `example` is byte-identical to the baseline.

## Baseline validator/parser check

Commands passed:

```bash
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh

skills/teaching-design-package/scripts/teaching-design-package.sh plan-split \
  --input /tmp/tdp-phase28-final.nrcOzZ/teaching-design-package-full.md \
  --out-dir /tmp/tdp-phase28-final.nrcOzZ/out
```

Parser count result:

```text
baseline_counts plan_anchor=1 design_anchor=1 plan_tasks=3 analysis=3 activity=3 evaluation=3
```

Negative validation passed:

```text
missing_plan_anchor=failed_expected: teaching-design-package.sh: expected one # 授课进度计划 anchor, found 0
missing_design_anchor=failed_expected: teaching-design-package.sh: expected one # 教学设计方案 anchor, found 0
```

## Derived hours check

Command output:

```text
derived_hours total=160 CA6140=40 X62W=60 Z3040=60
```

Generated handoff evidence:

```text
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:7:total_hours: "160H"
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:20:课时：40H
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:433:课时：60H
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:797:课时：60H
```

## Derived dates and term check

Generated handoff evidence:

```text
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:11:academic_term: "2025-2026学年第二学期"
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:21:起止日期：5月11日——5月15日
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:434:起止日期：5月18日——5月27日
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:798:起止日期：5月27日——6月5日
```

Generated package Typst evidence:

```text
/tmp/tdp-phase28-final.nrcOzZ/render/teaching-design-package.typ:8:// inferred_term: 2025-2026学年第二学期
/tmp/tdp-phase28-final.nrcOzZ/render/teaching-design-package.typ:10:// task_1: CA6140卧式车床电气控制线路安装与调试 40H 5月11日——5月15日
/tmp/tdp-phase28-final.nrcOzZ/render/teaching-design-package.typ:11:// task_2: X62W万能铣床电气控制线路安装与调试 60H 5月18日——5月27日
/tmp/tdp-phase28-final.nrcOzZ/render/teaching-design-package.typ:12:// task_3: Z3040摇臂钻床电气控制线路安装与调试 60H 5月27日——6月5日
```

## Forbidden YAML/default fields check

Command output:

```text
forbidden_package_yaml=none
```

The package baseline frontmatter remains limited to teacher-maintained fields and did not reintroduce `total_hours`, `school_year`, `semester`, `daily_hours`, `hour_unit`, `date_display_format`, `date_locale`, `calendar_source`, `holidays`, `makeup_days`, `source_of_truth`, `outputs`, or `validation`.

## Teacher metadata mapping

Generated handoff evidence:

```text
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-jihua-full.md:4:teacher_name: "张老师"
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:8:teacher_name: "张老师"
```

## Markdown handoff check

Generated `jiaoan-jihua-full.md` preserves the three plan task headings:

```text
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-jihua-full.md:11:## CA6140卧式车床电气控制线路安装与调试
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-jihua-full.md:54:## X62W万能铣床电气控制线路安装与调试
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-jihua-full.md:91:## Z3040摇臂钻床电气控制线路安装与调试
```

Generated `jiaoan-shicao-full.md` preserves three repeated lesson-plan groups:

```text
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:17:## 学习任务分析
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:70:## 教学活动设计——学习任务1：CA6140车床电气控制线路安装与调试（40H）
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:418:## 学业评价
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:430:## 学习任务分析
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:483:## 教学活动设计——学习任务2：X62W万能铣床电气控制线路安装与调试（60H）
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:780:## 学业评价
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:794:## 学习任务分析
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:847:## 教学活动设计——学习任务3：Z3040摇臂钻床电气控制线路安装与调试（60H）
/tmp/tdp-phase28-final.nrcOzZ/out/jiaoan-shicao-full.md:1144:## 学业评价
```

Activity hour handoff rows are generated as `##### xH`, and the handoff contains an `activity_hour_mapping` comment with same-name/same-order mapping evidence.

## Package Typst render check

Commands passed:

```bash
skills/teaching-design-package/scripts/teaching-design-package.sh render-split \
  --input /tmp/tdp-phase28-final.nrcOzZ/teaching-design-package-full.md \
  --out-dir /tmp/tdp-phase28-final.nrcOzZ/split-render

skills/teaching-design-package/scripts/teaching-design-package.sh render-package \
  --input /tmp/tdp-phase28-final.nrcOzZ/teaching-design-package-full.md \
  --out-dir /tmp/tdp-phase28-final.nrcOzZ/render
```

Outputs:

```text
/tmp/tdp-phase28-final.nrcOzZ/render/teaching-plan.typ
/tmp/tdp-phase28-final.nrcOzZ/render/lesson-plans.typ
/tmp/tdp-phase28-final.nrcOzZ/render/teaching-design-package.typ
```

Package Typst source-order evidence:

```text
/tmp/tdp-phase28-final.nrcOzZ/render/teaching-design-package.typ:19:= 授课进度计划
/tmp/tdp-phase28-final.nrcOzZ/render/teaching-design-package.typ:45:= 教学设计方案
```

## Provenance and manifest check

Manifest path: `/tmp/tdp-phase28-final.nrcOzZ/render/teaching-design-package-manifest.json`

Key evidence:

```text
generated_from_markdown=true
source_markdown=/tmp/tdp-phase28-final.nrcOzZ/teaching-design-package-full.md
section_anchors include # 授课进度计划 and # 教学设计方案
derived_hours total_hours=160H, task hours=40H/60H/60H
derived_dates include the three expected ranges
inferred_term=2025-2026学年第二学期
activity_hour_mapping=same-name or same-order from # 授课进度计划 rows
```

## Phase 29 PDF slots

Manifest evidence:

```text
teaching-plan.pdf status=not_run
lesson-plans.pdf status=not_run
teaching-design-package.pdf status=not_run
```

Phase 28 generated Typst and manifest slots only. It did not claim PDF parity or mark any Phase 29 PDF status as passed.

## Standalone compatibility

Commands passed:

```bash
skills/teaching-design-package/scripts/teaching-design-package.sh info
skills/teaching-design-package/scripts/teaching-design-package.sh version
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh info
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh version
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh manifest
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh info
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh version
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh manifest
```

`jiaoan-jihua` and `jiaoan-shicao` public scripts were not modified in Phase 28.

## Repository cleanliness

Commands passed during final verification:

```bash
git diff --check
git diff --cached --check
```

`git status --short` at the end of final verification showed only expected documentation edits to be committed for Task 06 after this file update.

## Requirement traceability

| Requirement | Evidence |
|-------------|----------|
| TDBR-01 | `example`, `plan-split`, `render-package`, and manifest consume `skills/teaching-design-package/templates/teaching-design-package-full.md` shape. |
| TDBR-02 | Baseline hash before/after stayed `fa4302a2d1e4554db72524f5a3a4829e7cc04ea21ca609a79a427cf850c2a1e8`; `git diff -- baseline --exit-code` passed. |
| TDBR-03 | `example` generated a byte-identical copyable Markdown artifact. |
| TDBR-04 | `render-package` produced `teaching-design-package.typ` from Markdown and manifest provenance records `generated_from_markdown: true`. |
| TDBR-05 | Generated Typst and manifest preserve `授课进度计划` before `教学设计方案`. |
| TDBR-12 | Derived total hours check produced `160`; package YAML has no `total_hours`. |
| TDBR-13 | Derived task hours check produced `CA6140=40`, `X62W=60`, `Z3040=60`. |
| TDBR-14 | Generated lesson-plan handoff inserts `##### xH` rows and records `activity_hour_mapping`; the script fails if a mapping cannot be produced. |
| TDBR-15 | Generated task ranges are `5月11日——5月15日`, `5月18日——5月27日`, and `5月27日——6月5日`. |
| TDBR-16 | Generated handoff, Typst, and manifest infer `2025-2026学年第二学期`; package YAML has no `school_year` or `semester`. |
| TDBR-17 | Package YAML forbidden-field check passed for rendering/default/output/validation knobs. |
