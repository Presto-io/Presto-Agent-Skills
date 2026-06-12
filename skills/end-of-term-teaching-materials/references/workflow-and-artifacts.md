# End-of-Term Workflow and Artifact Reference

This reference holds detailed workflow, artifact, scoring, and verification rules for the `end-of-term-teaching-materials` skill. Keep `SKILL.md` as the concise semantic entry point and update this file when long operational behavior changes.

## Fixed Workflow

The fixed workflow is:

```text
structured data -> Markdown -> Typst/PDF + table artifacts
```

Do not skip the persistent Markdown review point and export PDF directly from raw data.

## Markdown Review Sections

Generated or updated `end-of-term-full.md` must keep `YAML frontmatter + body` and these reviewable sections:

- `## 我带的学生`
- `## 过程考核任务`
- `## 成绩数据`
- `## 分析`
- `## 复核标记`

## Analysis Drafting

When `成绩分析表` or score-analysis-book content is enabled, do not rely only on generic AI prose. Ask the teacher for brief context such as:

- 教学重点和难点
- 学生整体表现
- 缺考或异常情况
- 需要强调的问题
- 后续改进措施

Combine those answers with score distribution, pass rate, below-60 cases, blank cells, and task-score patterns to draft `## 分析`.

## Review and Export Gates

- Uncertain values such as `87?` may be generated into `## 成绩数据` for teacher review.
- Every unresolved uncertain value must have a matching `## 复核标记` row.
- Ask one item at a time, edit the Markdown value after teacher confirmation or correction, and remove the matching marker.
- Hard export rule: `## 复核标记` must be exactly `无`.
- If `## 复核标记` is anything else, `validate`, `render`, and final export readiness must fail.
- If unresolved items remain and the user explicitly wants inspection artifacts, explain the unresolved items first, ask whether to generate an abnormal preview, then use `render --abnormal-review`.
- Abnormal review manifests must include `artifact_kind: abnormal_review`, `final_ready: false`, and `review_cleared: false`.

## Score and Template Rules

- Preserve blank score cells and declared task columns. Empty scores remain empty; declared tasks remain columns even when all cells are blank.
- Respect package flags.
- `成绩记分册` is one bundle covering the redesigned cover and score-book body.
- `交接班记录封面` requires both `handover_class_name` and `handover_teachers`; otherwise the renderer skips it and records a manifest warning.
- Support up to 8 process-assessment tasks. Markdown and deterministic artifacts must expand columns through `任务8`; the fixed `成绩汇总表` PDF grid renders at most 8 task columns.
- `成绩记分册` shows every score row and uses the Markdown `考勤`、`作业`、`期末` test columns as its source data.
- `平时分` uses `考勤 * 0.3 + 作业 * 0.4 + 期末测试 * 0.3` when the Markdown `期末` test column is present, otherwise `考勤 * 0.5 + 作业 * 0.5`.
- `成绩汇总表` only shows students listed under `## 我带的学生`, uses `任务1..任务N`, and its `总评成绩` equals `期末分`, where `期末分` is the task-hours weighted average.
- Preserve fixed-template merged cells in the `成绩分析表`; `全班人数` and `缺考人数` labels each span the upper two statistic rows and remain centered above their values.

## Outputs

- `end-of-term-full.md`: persistent Markdown intermediate.
- `end-of-term-package.typ`: generated Typst package using `templates/typst/end-of-term-package.typ`.
- `end-of-term-package.pdf`: merged PDF package when `typst compile` succeeds.
- `manifest.json`: package flags, warnings, PDF status, review status, repeatability and artifact verification flags.
- `tables/score-data.json`: deterministic score rows.
- `tables/score-data.csv`: deterministic score rows in fixed column order.
- `tables/task-map.json`: mapping from `任务1..任务N` to task names and hours.
- `tables/calculated-score-data.json`: deterministic raw score rows plus renderer-calculated `平时分`、`期末分` and `学期成绩`; PDF and workbook must use the same calculated values.
- `tables/score-summary.json`: summary evidence for `## 我带的学生` only, using `任务1..任务N` and `总评成绩 = 期末分`.
- `tables/highlight-evidence.json`: deterministic red-warning evidence for unresolved uncertain cells and below-60 `学期成绩` cells.
- `tables/score-list.md`: 4-column Markdown table sorted by ascending student ID: `姓名`、`学号`、`平时成绩`、`期末成绩`; values come from the score-book `平时分` and `期末分`.
- `tables/score-list.xlsx`: single-sheet workbook with the same 4-column sorted score list.
- `tables/scorebook.xlsx`: teacher-facing workbook with `成绩数据`、`任务映射`、`成绩汇总` sheets; `成绩数据` follows the score-book view and uses `考勤`、`作业`、`期末` plus derived scores.

PDF rendering uses the fixed Excel-style grid for the score book body, score summary, and analysis sheet: column proportions, row rhythm, thin borders, merged headers, merged statistic cells, and diagonal header cells are encoded in the skill-local renderer.

## Verification Detail

- `bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`
- `python3 -m py_compile skills/end-of-term-teaching-materials/scripts/render_package.py`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh verify --workdir <existing-dir>`
- `manifest.json` includes `"review_cleared": true`, `"repeatable": true`, `"calculated_scores_verified": true`, `"table_artifacts_verified": true`, and workbook verification.
- Uncertain fixture generation preserves `87?`, writes `## 复核标记`, blocks normal render, and allows only explicit `--abnormal-review` output with `"final_ready": false`.
- All deterministic table and workbook artifacts listed above exist.
