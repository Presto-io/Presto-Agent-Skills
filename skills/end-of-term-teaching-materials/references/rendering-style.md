# End-of-Term Rendering Style Notes

本说明记录 `end-of-term-teaching-materials` 固定模板渲染规则。它是可复用、已脱敏的技能本地资源；用户桌面、历史课程文件和真实学生原始材料只能作为外部人工对照，不能进入 reusable fixture。

## Package Artifacts

- `成绩记分册` 是一个 bundle，覆盖重新设计的成绩记分册封面和成绩记分册正文，不拆成两个 package 开关。
- `成绩汇总表` 输出成绩汇总与任务映射，作为 PDF 页面和 deterministic table artifacts 的共同依据。
- `成绩分析表` 输出试卷分析、存在问题、今后改进措施和异常情况分析。
- `教学日志封面` 使用课程、班级、教师、学年、学期和日期元数据。
- `过程考核评价表封面` 使用课程、专业、班级、教师和任务信息。
- `交接班记录封面` 只有在 `handover_class_name` 和 `handover_teachers` 同时存在时输出；缺失时 renderer 必须跳过并在 manifest 中写出 warning。

## Page And Typography

- PDF package 使用 A4 纵向页面，页边距保持保守，便于学校归档打印。
- 中文字体优先使用 `Noto Serif CJK SC`、`Songti SC`、`STSong`，无可用字体时由 Typst 环境继续 fallback。
- 封面页使用居中标题、元数据块和适度留白；正文表格使用紧凑字号，优先保证内容完整可审阅。
- 自动化输出只是格式验证和提交前检查依据，不能替代教师对 PDF 和 workbook 的最终格式确认。

## Score Table Behavior

- `## 过程考核任务` 的顺序决定 `任务1..任务N` 列顺序。
- 声明过的任务列必须保留，即使整列为空。
- 空成绩单元格保持空白；不能写成 `0`、`-1`、`—` 或自动复核项。
- 带 `?` 的不确定成绩会阻断最终 export readiness，除非 `## 复核标记` 正文已经准确清除为 `无` 且表格值也已修正。

## Deterministic Artifacts

Renderer 必须在 `tables/` 下输出稳定的 `score-data.json`、`score-data.csv`、`task-map.json`、`score-summary.json` 和 `scorebook.xlsx`。JSON 使用固定缩进、稳定 key 顺序和 UTF-8；CSV 使用固定列顺序；workbook 保留同样的表头和公式占位列。
