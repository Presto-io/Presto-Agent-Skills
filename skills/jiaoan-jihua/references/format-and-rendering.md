# Jiaoan Jihua Format and Rendering Reference

This reference holds detailed authoring and renderer rules for the `jiaoan-jihua` skill. Keep `SKILL.md` as the concise semantic entry point and update this file when long format behavior changes.

## Frontmatter

- `major_name`: 专业名称。
- `course_name`: 课程名称。
- `teacher_name`: 授课教师。
- `class_name`: 授课班级。
- `first_teaching_day`: `YYYY-MM-DD` 格式的首个授课日。
- `daily_hours`: 可选；如果源材料明确给出每日学时，保留它。
- `template`: 固定为 `jiaoan-jihua`。

## Body Structure

- `##` 表示学习任务标题。
- `###` 表示学习环节标题，例如安技教育及旧知识回顾、明确任务、制定计划、工作准备、任务实施、成果展示、总结评价。
- 每一行教学内容用 `-N` 结尾保留学时，便于模板映射到表格列。

## Calendar and Scheduling Rules

- 当源材料依赖日期、周次或节假日排布时，先使用 `references/calendar.json` 对齐教学进度。
- 当源材料只给出日期、周次或总学时，而没有现成任务分段时，先还原教学日历，再写入 `jiaoan-jihua-full.md` 结构。
- 不要静默删除源材料中不确定、缺失或无法表达的周次、学时或任务分段；必须就近标记复核。

## Renderer Notes

- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render` converts `jiaoan-jihua-full.md` to Typst through built-in shell logic.
- The conversion must not call an external executable.
- `--expected-typ` performs black-box comparison against a reference Typst file.

## Verification Detail

- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh example --output <file>` must output a reviewable `jiaoan-jihua-full.md` structure.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render --input <md> --typ <typ>` must generate Typst without external executables.
- `--expected-typ` must match the generated Typst against a fixture when provided.
