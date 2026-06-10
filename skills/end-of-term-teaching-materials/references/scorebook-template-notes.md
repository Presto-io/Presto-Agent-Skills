# Scorebook Template Notes

`scorebook-template.xlsx` 是脱敏、可复用的 workbook fixture，用于验证 `成绩记分册` 表头、sheet 结构和派生成绩输出位置，不包含真实学生原始记录。

## Workbook Expectations

- 必须包含 `成绩数据`、`任务映射`、`成绩汇总` 三个 worksheet。
- `成绩数据` sheet 的列顺序为 `学号`、`姓名`、`考勤`、`作业`、`期末`、`平时分`、`期末分`、`学期成绩`、`备注`。其中 Markdown `期末` 列是期末测试，不是派生的期末成绩；该 sheet 显示所有学生。
- `任务映射` sheet 记录任务序号、任务名称和课时，顺序与 Markdown `## 过程考核任务` 完全一致。
- `成绩汇总` sheet 保留 `## 我带的学生` 的任务数、学生数、任务成绩空白单元格数和计算说明；总评成绩口径为 `期末分`。
- renderer 还必须输出 `score-list.md` 和 `score-list.xlsx`，两者只包含 `姓名`、`学号`、`平时成绩`、`期末成绩` 四列，并按学号递增排序。

## Score Cell Rules

- 空成绩单元格必须继续为空白。
- 任务列必须存在于 Markdown 和 `任务映射` 中，即使所有学生在该任务下都为空；`成绩汇总表` 使用这些任务列且最多渲染 `任务1..任务8`，`成绩记分册` 不直接显示这些任务列。
- 不确定值不得被 workbook 自动清洗；普通 renderer 应在最终输出前用复核标记阻断。
- 只有用户明确要求 abnormal review preview 时，workbook 才能保留 `87?` 这类未解决值，并用 red warning fill 标出对应单元格；派生成绩计算临时使用数值部分 `87`。manifest 和 `tables/highlight-evidence.json` 必须记录这些 highlighted cells。
- workbook 中显示的衍生 `学期成绩` 低于 60 时也必须使用 red warning fill，并写入 highlight evidence。
- `平时分` 计算规则：有 Markdown `期末` 测试值时，`考勤 * 0.3 + 作业 * 0.4 + 期末 * 0.3`；无 Markdown `期末` 测试值时，`考勤 * 0.5 + 作业 * 0.5`。
- `期末分` 计算规则：`任务1..任务N` 按 `任务映射` 中的课时数加权平均；空白任务成绩不参与分子和分母。
- workbook、PDF、`tables/calculated-score-data.json`、`score-list.md` 和 `score-list.xlsx` 必须使用同一套 renderer-calculated `平时分`、`期末分` 与 `学期成绩` 显示值；不要求 workbook 单元格保留 Excel 公式。

## Fixture Boundary

fixture 可以反映固定 score-book 样式和 sheet 结构，但不能包含真实姓名、真实学号、私有路径、凭据或未脱敏截图。用户桌面文件只允许作为人工外部验证参考。
