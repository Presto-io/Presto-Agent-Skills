# End-of-Term Rendering Style Notes

本说明记录 `end-of-term-teaching-materials` 固定模板渲染规则。它是可复用、已脱敏的技能本地资源；用户桌面、历史课程文件和真实学生原始材料只能作为外部人工对照，不能进入 reusable fixture。

## Package Artifacts

- `成绩记分册` 是一个 bundle，覆盖重新设计的成绩记分册封面和成绩记分册正文，不拆成两个 package 开关。
- `成绩汇总表` 输出成绩汇总与任务映射，作为 PDF 页面和 deterministic table artifacts 的共同依据。
- `成绩分析表` 输出试卷分析、存在问题、今后改进措施和异常情况分析正文表，不额外生成封面。
- `教学日志封面` 使用参考封面的标题、留白和三行下划线信息栏，只展示科目、班级和教师。
- `过程考核评价表封面` 使用参考封面的标题、留白和三行下划线信息栏，只展示科目、班级和教师。
- `交接班记录封面` 只展示当前班级/教师和交接班级/教师两行；只有在 `handover_class_name` 和 `handover_teachers` 同时存在时输出，缺失时 renderer 必须跳过并在 manifest 中写出 warning。

## Page And Typography

- PDF package 使用 A4 纵向页面，页边距保持保守，便于学校归档打印。
- 中文字体优先使用 `Noto Serif CJK SC`、`Songti SC`、`STSong`，无可用字体时由 Typst 环境继续 fallback。
- 封面页参考学校样张：大号居中标题、充分上部留白、底部下划线式信息栏；正文表格使用紧凑字号，优先保证内容完整可审阅。
- 自动化输出只是格式验证和提交前检查依据，不能替代教师对 PDF 和 workbook 的最终格式确认。

## Score Table Behavior

- `成绩记分册正文` 按源 Excel 的 A:O 列比例、前两行组合表头、固定行高节奏和细边框网格渲染；左上角使用斜线表头表达 `学号 / 姓名`。
- `成绩汇总表` 按源 Excel 的 A:K 列比例、标题行、元数据行、任务权重区和 `学生姓名 / 考核成绩` 斜线表头渲染。
- `成绩分析表` 按源 Excel 的 A:I 列比例、合并单元格、统计区和四个分析大文本区渲染。
- `## 过程考核任务` 的顺序决定 `任务1..任务N` 列顺序。
- 声明过的任务列必须保留，即使整列为空。
- 空成绩单元格保持空白；不能写成 `0`、`-1`、`—` 或自动复核项。
- 带 `?` 的不确定成绩会阻断最终 export readiness，除非 `## 复核标记` 正文已经准确清除为 `无` 且表格值也已修正。
- 如果用户明确要求检查未清除复核项，可使用 abnormal review preview 路径生成非最终件。manifest 必须写出 `artifact_kind: abnormal_review`、`final_ready: false`、`review_cleared: false` 和 warnings，普通 `render` 仍必须阻断。
- Abnormal review 输出中，未解决的不确定成绩单元格使用 red warning fill。`成绩记分册` 和 `成绩汇总表` 中显示的衍生 `学期成绩` 如果低于 60，也使用 red warning fill，便于教师检查。

## Deterministic Artifacts

Renderer 必须在 `tables/` 下输出稳定的 `score-data.json`、`score-data.csv`、`task-map.json`、`score-summary.json` 和 `scorebook.xlsx`。JSON 使用固定缩进、稳定 key 顺序和 UTF-8；CSV 使用固定列顺序；workbook 保留同样的表头和公式占位列。
红色高亮不能只依赖人工看 PDF/workbook；renderer 还必须输出 `tables/highlight-evidence.json`，并在 manifest 中嵌入同一份 highlight evidence，用于验证 unresolved uncertain cells 和 below-60 `学期成绩`。
