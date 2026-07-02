# Scorebook Template Notes

本说明记录公开 Excel 的边界。期末材料 PDF 仍包含成绩记分册、成绩汇总表和成绩分析表页面；公开 workbook 只保留教师需要上报的 4 列成绩清单。

## Workbook Expectations

- 公开 workbook 文件名为 `score-list.xlsx`。
- workbook 只有一个 worksheet。
- 列顺序固定为 `学号`、`姓名`、`平时成绩`、`期末成绩`。
- 行按学号递增排序。
- 不输出 `成绩数据`、`任务映射`、`成绩汇总` 等多 sheet workbook。
- 不输出 `score-list.md`。

## Score Cell Rules

- 空成绩单元格必须继续为空白。
- 任务列必须存在于 Markdown 中，即使所有学生在该任务下都为空；`成绩汇总表` PDF 使用这些任务列且最多渲染 `任务1..任务8`，公开 workbook 不直接显示这些任务列。
- 不确定值不得被 workbook 自动清洗；最终交付前必须用复核标记阻断并回到 Markdown 修正。
- `平时分` 计算规则：有 Markdown `期末` 测试值时，`考勤 * 0.3 + 作业 * 0.4 + 期末 * 0.3`；无 Markdown `期末` 测试值时，`考勤 * 0.5 + 作业 * 0.5`。
- `期末分` 计算规则：`任务1..任务N` 按 `任务映射` 中的课时数加权平均；空白任务成绩不参与分子和分母。
- workbook 和 PDF 必须使用同一套 renderer-calculated `平时分` 与 `期末分` 显示值；不要求 workbook 单元格保留 Excel 公式。

## Reusable Boundary

可复用模板和说明不能包含真实姓名、真实学号、私有路径、凭据或未脱敏截图。用户桌面文件只允许作为人工外部参考。
