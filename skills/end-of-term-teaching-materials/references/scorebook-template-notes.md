# Scorebook Template Notes

`scorebook-template.xlsx` 是脱敏、可复用的 workbook fixture，用于验证 `成绩记分册` 表头、sheet 结构和派生成绩输出位置，不包含真实学生原始记录。

## Workbook Expectations

- 必须包含 `成绩数据`、`任务映射`、`成绩汇总` 三个 worksheet。
- `成绩数据` sheet 的列顺序为 `学号`、`姓名`、`任务1..任务N`、`考勤`、`作业`、`期末`、`平时分`、`学期成绩`、`备注`。
- `任务映射` sheet 记录任务序号、任务名称和课时，顺序与 Markdown `## 过程考核任务` 完全一致。
- `成绩汇总` sheet 保留任务数、学生数、空白单元格数和计算说明。

## Score Cell Rules

- 空成绩单元格必须继续为空白。
- 任务列必须存在，即使所有学生在该任务下都为空。
- 不确定值不得被 workbook 自动清洗；普通 renderer 应在最终输出前用复核标记阻断。
- 只有用户明确要求 abnormal review preview 时，workbook 才能保留 `87?` 这类未解决值，并用 red warning fill 标出对应单元格。manifest 和 `tables/highlight-evidence.json` 必须记录这些 highlighted cells。
- workbook 中显示的衍生 `学期成绩` 低于 60 时也必须使用 red warning fill，并写入 highlight evidence。
- workbook、PDF 和 `tables/calculated-score-data.json` 必须使用同一套 renderer-calculated `平时分` 与 `学期成绩` 显示值；不要求 workbook 单元格保留 Excel 公式。

## Fixture Boundary

fixture 可以反映固定 score-book 样式和 sheet 结构，但不能包含真实姓名、真实学号、私有路径、凭据或未脱敏截图。用户桌面文件只允许作为人工外部验证参考。
