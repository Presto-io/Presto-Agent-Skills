---
status: resolved
trigger: "期末教学材料成绩渲染多轮反馈：成绩记分册与成绩汇总表取数口径混淆、缺少 4 列成绩清单、最多 8 个任务列扩展不完整、预留任务名称不应显示、成绩汇总表未显示第 21 个测试学生、作业测试成绩表头应显示 1..8。"
created: 2026-06-10T15:36:46+0800
updated: 2026-06-10T15:36:46+0800
---

# Debug Session: end-of-term-score-views-and-summary-pagination

## Symptoms

- expected_behavior: "`成绩记分册` 显示所有学生，来源为 Markdown `考勤`、`作业`、`期末` 测试列，并派生 `平时分`、`期末分`、`学期成绩`；`成绩汇总表` 只显示 `## 我带的学生`，来源为 `任务1..任务N`，`总评成绩 = 期末分`；过程考核任务最多 8 个，作业测试成绩表头显示 `1 2 3 4 5 6 7 8`；0 课时或 `预留任务*` 不显示任务名称；额外输出 4 列 `score-list.md` 和 `score-list.xlsx`，按学号递增。"
- actual_behavior: "原实现混用任务列、平时列和期末列口径；成绩清单缺失；`成绩汇总表` 固定只渲染第一页 20 行，导致第 21 个 `测试学生` 未显示；任务名区域扩展到 8 列后仍有预留任务名称/居中问题；截图显示 `作业测试成绩` 小表头仍是 `考勤 / 作业 / 期末`，而不是 `1..8`。"
- error_messages: "无运行时报错；表现为 PDF/Typst/workbook/Markdown artifact 的内容与教师模板语义不一致。"
- timeline: "2026-06-10，在 v1.7 `end-of-term-teaching-materials` 已完成后，基于用户提供的全功能验证数据和人工截图连续复核。"
- reproduction: "使用 `/private/tmp/presto-full-validation.4dPdrF/full-validation.md` 渲染 abnormal review 包；该数据包含 42 名学生、21 名我带学生、8 个任务列、后 3 个任务 0 课时、坏数据 `29WGCS101 测试学生` 的 `任务1=30?`。"

## Current Focus

- hypothesis: "渲染器缺少两个独立成绩视图：score-book view 和 score-summary view；同时固定 PDF grid 的分页、任务列、任务名显示和派生成绩口径没有随用户确认的模板规则一起收敛。"
- test: "把成绩记分册、成绩汇总表、成绩清单分别建模；重新渲染全功能数据；抽查 Typst 源、score-list Markdown/xlsx、manifest 和脚本验证输出。"
- expecting: "`作业测试成绩` 表头包含 `[1]..[8]`；`成绩汇总表` 第二页包含序号 `21`、`测试学生` 和 `30?`；Typst 源不包含 `预留任务`；4 列成绩清单末行按学号排序到 `29WGCS101 测试学生`；manifest 为 `artifact_kind=abnormal_review`、`final_ready=false` 且 evidence 指向坏数据。"
- next_action: "resolved"
- reasoning_checkpoint: ""
- tdd_checkpoint: ""

## Evidence

- timestamp: 2026-06-10T15:14:00+0800
  observation: "全功能验证数据中 `我所带班` 标记 1..21，第 21 名是 `29WGCS101 测试学生`，且 `任务1=30？` 被标准化为 `30?`。"
  implication: "如果 `成绩汇总表` 固定只渲染 20 行，坏数据会被截断，人工复核无法看到专门设置的异常样本。"
- timestamp: 2026-06-10T15:20:00+0800
  observation: "截图显示 `作业测试成绩` 小表头为 `考勤 / 作业 / 期末`，后 5 格为空。"
  implication: "表头语义和用户要求的任务编号展示不一致；虽然成绩记分册数据源是 `考勤 / 作业 / 期末`，视觉表头仍应按固定模板显示 1..8。"
- timestamp: 2026-06-10T15:24:00+0800
  observation: "`render_package.py` 新增并使用 `owned_score_rows()`，`score_summary_pages()` 将 `## 我带的学生` 按 20 行分页，第二页起始序号继续递增。"
  implication: "`成绩汇总表` 从全体成绩数据中筛选教师负责学生，并能显示第 21 名及后续学生，不再被第一页固定行数截断。"
- timestamp: 2026-06-10T15:24:30+0800
  observation: "`scorebook_score_page()` 的 `作业测试成绩` 小表头固定渲染 `1..8`，而行数据仍通过 `scorebook_source_values()` 显示 `考勤`、`作业`、`期末` 及空白格。"
  implication: "视觉模板与数据口径被分离：表头满足固定模板编号要求，计算仍使用用户确认的平时成绩来源。"
- timestamp: 2026-06-10T15:25:00+0800
  observation: "`task_display_name()` 对 0 课时或 `预留任务*` 返回空字符串，`task_name_cells()` 按单元格整体高度计算垂直居中。"
  implication: "0 课时预留列不会泄漏为可见任务名，真实任务名称在其所在单元格内水平、垂直居中。"
- timestamp: 2026-06-10T15:26:00+0800
  observation: "脚本引入 `MAX_TASKS = 8`、`SCORE_LIST_COLUMNS = [姓名, 学号, 平时成绩, 期末成绩]`、`score_list_rows()` 和单 sheet xlsx writer。"
  implication: "过程考核任务上限显式化，Markdown/xlsx 成绩清单成为可验证的确定性 artifact，并按学号递增排序。"
- timestamp: 2026-06-10T15:27:00+0800
  observation: "渲染 `/private/tmp/presto-full-validation.4dPdrF/full-validation.md` 后，manifest 为 `artifact_kind=abnormal_review`、`final_ready=false`、`score_list_verified=true`，highlight evidence 包含 `测试学生 / 任务1 / 30?` 和 `测试学生 / 学期成绩 / 45`。"
  implication: "坏数据没有被吞掉，异常预览语义保留：可生成教师检查用 PDF，但不会被当作最终提交包。"
- timestamp: 2026-06-10T15:28:00+0800
  observation: "`/private/tmp/presto-full-validation-final.DALCEq/end-of-term-package.typ` 包含 `作 业 测 试 成 绩` 下的 `[1]` 和 `[8]`；同一文件包含第二页 `测试学生`、`30?`，且 `rg 预留任务` 无匹配。"
  implication: "PDF 源层面已验证 8 列表头、坏数据可见性、预留任务隐藏和分页行为。"
- timestamp: 2026-06-10T15:29:00+0800
  observation: "`full-validation-score-list.md` 末行是 `测试学生 | 29WGCS101 | 50 | 42`；`full-validation-score-list.xlsx` 为 43 行、4 列，并包含 `测试学生` 与 `29WGCS101`。"
  implication: "4 列成绩清单按学号递增覆盖全体 42 名学生，坏数据样本没有在表格 artifact 中丢失。"
- timestamp: 2026-06-10T15:30:00+0800
  observation: "验证命令通过：`python3 -m py_compile skills/end-of-term-teaching-materials/scripts/render_package.py`、`bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`、`skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh verify --workdir /private/tmp/presto-full-validation-final.AxRMzi`、`git diff --check`。"
  implication: "修复没有引入 Python 语法、shell 语法、内置验证或 whitespace regressions。"

## Eliminated

- hypothesis: "`成绩记分册` 应继续直接显示 `任务1..任务N`。"
  reason: "用户明确纠正：成绩记分册里的数据来自 `考勤`、`作业`、`期末`，并显示所有学生；任务成绩属于成绩汇总表视图。"
- hypothesis: "`期末成绩` 等同 Markdown 的 `期末` 列。"
  reason: "用户明确区分：Markdown `期末` 是期末测试；派生 `期末分` 来自任务成绩按课时加权平均。"
- hypothesis: "`成绩汇总表` 可以只渲染第一页 20 行。"
  reason: "用户专门放入第 21 名 `测试学生` 作为坏数据，未显示即说明分页/筛选逻辑错误。"
- hypothesis: "0 课时任务可以显示为 `预留任务` 以保留占位含义。"
  reason: "用户明确要求不显示 `预留任务`；固定列可以保留空白，但名称不能显示。"
- hypothesis: "交付仍需要复制 `full-validation-scorebook`。"
  reason: "用户明确要求以后不需要生成或交付 `full-validation-scorebook`；最终整理只复制 PDF、4 列 Markdown 和 4 列 xlsx。"

## Resolution

- root_cause: "固定模板渲染器把多个成绩视图合并成一套近似逻辑：记分册、汇总表、派生成绩、任务列、分页和 deterministic artifacts 没有按用户确认的真实模板口径拆开，导致字段来源、显示范围、任务列数量和异常样本可见性同时偏离。"
- fix: "将渲染规则拆为独立视图：`成绩记分册` 使用全体成绩行和 `考勤/作业/期末` 测试列派生 `平时分/期末分/学期成绩`；`成绩汇总表` 使用 `owned_score_rows()` 只显示 `## 我带的学生`，按任务课时加权计算 `期末分`，并用 `score_summary_pages()` 分页；任务 grid 扩展到 8 列，表头显示 `1..8`，0 课时/预留任务隐藏名称并垂直居中；新增 `score-list.md` 和 `score-list.xlsx` 作为 4 列、按学号递增的成绩清单；同步更新 `SKILL.md`、rendering notes、scorebook notes 和 cover notes。"
- verification: "`python3 -m py_compile skills/end-of-term-teaching-materials/scripts/render_package.py`; `bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`; `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh render --input /private/tmp/presto-full-validation.4dPdrF/full-validation.md --workdir /private/tmp/presto-full-validation-final.DALCEq --pdf --abnormal-review`; Typst 源抽查 `作业测试成绩` `[1]..[8]`、`测试学生`、`30?`、无 `预留任务`; xlsx zip 抽查 43 行 4 列且包含测试学生；`skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh verify --workdir /private/tmp/presto-full-validation-final.AxRMzi`; `git diff --check`。"
- files_changed:
  - `skills/end-of-term-teaching-materials/scripts/render_package.py`
  - `skills/end-of-term-teaching-materials/SKILL.md`
  - `skills/end-of-term-teaching-materials/references/cover-template-notes.md`
  - `skills/end-of-term-teaching-materials/references/rendering-style.md`
  - `skills/end-of-term-teaching-materials/references/scorebook-template-notes.md`
  - `.planning/debug/resolved/end-of-term-score-views-and-summary-pagination.md`

## Artifacts

- abnormal_review_pdf: `/private/tmp/presto-full-validation-final.DALCEq/full-validation-abnormal-review.pdf`
- score_list_xlsx: `/private/tmp/presto-full-validation-final.DALCEq/full-validation-score-list.xlsx`
- score_list_markdown: `/private/tmp/presto-full-validation-final.DALCEq/full-validation-score-list.md`
- source_markdown: `/private/tmp/presto-full-validation.4dPdrF/full-validation.md`

## Specialist Review

- specialist_hint: general
- result: not invoked; the issue was localized to deterministic renderer behavior and fixed with local script/documentation changes plus black-box render verification.
