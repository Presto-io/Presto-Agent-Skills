---
status: resolved
trigger: "异常预览里 87? 仍是未复核数据，此时先使用这个数据进行计算，但是输出的 87？ 仍要保留"
created: 2026-06-10
updated: 2026-06-10
---

# Debug Session: end-of-term-uncertain-score-calc

## Symptoms

- expected_behavior: "abnormal review preview 中，原始成绩单元格继续显示 `87?`，同时派生的 `平时分`、`学期成绩` 临时按数值部分 `87` 计算；最终导出仍被未复核数据阻断。"
- actual_behavior: "异常预览已经保留 `87?`，但计算函数把带 `?` 的值排除，导致 `学生乙` 的 `平时分` 和 `学期成绩` 没有按 87 参与计算。"
- error_messages: "无报错；表现为 PDF/workbook/calculated score evidence 中派生成绩值不符合异常预览语义。"
- timeline: "2026-06-10 在检查红色异常预览 PDF 和 calculated score evidence 时确认。"
- reproduction: "用 `generated/end-of-term-red-preview/end-of-term-full.md` 执行 `render --pdf --abnormal-review`，检查 `学生乙` 的 `任务1=87?`、`平时分` 和 `学期成绩`。"

## Current Focus

- hypothesis: "`score_number()` 和 `numeric_average()` 将 `87?` 视为不可计算值，导致异常预览没有按数值部分临时计算。"
- test: "修改 score parsing，让 `87?` 的可计算部分为 87，同时原始单元格仍保留 `87?`；重新生成 abnormal review PDF 并检查 Typst 源和 calculated-score-data。"
- expecting: "`任务1` 原始显示为 `87?`；`平时分` 为 `74`；`学期成绩` 为 `66`；manifest 仍为 `final_ready=false` 且 `calculated_scores_verified=true`。"
- next_action: "resolved"
- reasoning_checkpoint: ""
- tdd_checkpoint: ""

## Evidence

- timestamp: 2026-06-10
  observation: "`score_number()` 原先遇到以 `?` 结尾的值直接返回 `None`，`numeric_average()` 原先直接 `float(value)` 并忽略 `ValueError`。"
  implication: "`87?` 在异常预览中只作为显示值存在，没有参与 `平时分` 与 `学期成绩` 计算。"
- timestamp: 2026-06-10
  observation: "修复后 `score_number()` 会剥离结尾 `?` 再解析数值，`numeric_average()` 和 `semester_score()` 统一通过 `score_number()` 计算。"
  implication: "`87?` 的显示语义和计算语义被分离：显示保留问号，计算临时使用 87。"
- timestamp: 2026-06-10
  observation: "重新执行 `render --pdf --abnormal-review` 后，`generated/end-of-term-red-preview/tables/calculated-score-data.json` 中 `学生乙` 为 `任务1=87?`、`平时分=74`、`学期成绩=66`。"
  implication: "异常预览计算结果符合用户要求。"
- timestamp: 2026-06-10
  observation: "`generated/end-of-term-red-preview/end-of-term-package.typ` 同时包含 `学生乙`、`[87?]`、`[74]`、`[66]`，并保留 highlight evidence。"
  implication: "PDF 源会继续展示未复核原始值，同时展示临时派生成绩。"
- timestamp: 2026-06-10
  observation: "`skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh verify --workdir generated/end-of-term-calc-verify` 通过，正常最终包与异常预览包均记录 `calculated_scores_verified: true`。"
  implication: "修复没有破坏正常最终导出、异常预览、计算一致性或确定性验证。"

## Eliminated

- hypothesis: "异常预览应把 `87?` 清洗成 `87` 再输出。"
  reason: "用户明确要求输出仍保留 `87?`，否则教师无法看到该值仍需复核。"
- hypothesis: "带 `?` 的值不应参与任何计算。"
  reason: "用户明确要求异常预览阶段先使用该数据进行计算，以便检查受影响的派生成绩。"

## Resolution

- root_cause: "计算路径把带 `?` 的 review value 当作完全不可计算值处理，和 abnormal review preview 的教师检查语义不一致。"
- fix: "将 score parsing 收敛到 `score_number()`：原始单元格保留 `87?`，派生成绩计算使用数值部分 `87`；同时更新 skill 和 rendering notes，明确 abnormal review 的显示/计算规则。"
- verification: "`bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`; `python3 -m py_compile skills/end-of-term-teaching-materials/scripts/render_package.py`; `render --pdf --abnormal-review`; `verify --workdir generated/end-of-term-calc-verify`; `git diff --check`。"
- files_changed:
  - `skills/end-of-term-teaching-materials/scripts/render_package.py`
  - `skills/end-of-term-teaching-materials/SKILL.md`
  - `skills/end-of-term-teaching-materials/references/rendering-style.md`
  - `skills/end-of-term-teaching-materials/references/scorebook-template-notes.md`
  - `.planning/debug/resolved/end-of-term-uncertain-score-calc.md`

## Specialist Review

- specialist_hint: general
- result: not invoked; the bug was localized to score parsing and renderer verification, and local black-box verification passed.
