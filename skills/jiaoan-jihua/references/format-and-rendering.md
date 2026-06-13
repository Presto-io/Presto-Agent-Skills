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
- 每一行教学内容必须用 `-N` 结尾保留整数学时；`N` 是该教学内容行的课时数。
- 渲染器按源文件顺序解析学习任务、学习环节和教学内容行，不重排任务、环节或内容。
- 非空学习环节正文如果不匹配 `text-N`，渲染器必须报错，不能静默丢弃。

## Calendar and Scheduling Rules

- 当源材料依赖日期、周次或节假日排布时，先使用 `references/calendar.json` 对齐教学进度。
- 当源材料只给出日期、周次或总学时，而没有现成任务分段时，先还原教学日历，再写入 `jiaoan-jihua-full.md` 结构。
- `first_teaching_day` 是第一条教学内容开始消耗课时的日期；该日期必须存在于 `references/calendar.json`。
- `daily_hours` 是每天可消耗的课时数。渲染器按教学内容行的 `-N` 课时顺序消耗校历日期，并为每一行生成周次、星期和学时单元格。
- 周次来自校历第一天所在教学周，不使用 ISO week 作为学期周次。
- 不要静默删除源材料中不确定、缺失或无法表达的周次、学时或任务分段；必须就近标记复核。

## Official Table Contract

- 当 frontmatter `template` 为 `jiaoan-jihua` 时，`scripts/jiaoan-jihua.sh render` 生成官方五列表格 Typst。
- 输出头部包含 `// jiaoan-jihua official template`、`@preview/cuti:0.2.1` fake-bold import/show rule、A4 页面设置、`STSong` 字体、helper cell 定义、文档 metadata、居中学期周次标题、课程信息 grid、五列表格和签字 grid。
- 表格列固定为 `(3.15cm, 8.51cm, 1.12cm, 1.29cm, 1.27cm)`，对应学习环节、教学内容、周次、星期、学时。
- 学习任务总学时由其所有内容行的 `-N` 求和得到；学习环节 `rowspan` 由该环节内容行数得到。
- 目标 Typst 文件只作为生成后的严格验证 oracle，不能在渲染过程中读取、复制或拼接进输出。

## Renderer Notes

- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render` converts `jiaoan-jihua-full.md` to Typst through built-in shell logic.
- The conversion must not call an external executable.
- `--expected-typ` performs black-box comparison against a reference Typst file after the output file has already been generated.

## Verification Detail

- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh example --output <file>` must output a reviewable `jiaoan-jihua-full.md` structure.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render --input <md> --typ <typ>` must generate Typst without external executables.
- `--expected-typ` must match the generated Typst against a fixture when provided.

Phase 21 strict fixture verification:

```bash
tmpdir="$(mktemp -d)"
generated="$tmpdir/jiaoan-jihua-generated.typ"
source="test/1.10/电气设备控制线路安装与调试授课计划.md"
target="test/1.10/电气设备控制线路安装与调试授课计划.typ"

skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render \
  --input "$source" \
  --typ "$generated"

diff -u "$target" "$generated"
shasum -a 256 "$target" "$generated"

skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render \
  --input "$source" \
  --typ "$tmpdir/jiaoan-jihua-generated-expected.typ" \
  --expected-typ "$target"
```
