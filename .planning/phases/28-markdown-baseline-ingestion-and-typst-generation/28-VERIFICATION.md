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
