# Jiaoan Shicao Format and Rendering Reference

This reference holds detailed authoring and renderer rules for the `jiaoan-shicao` skill. Keep `SKILL.md` as the concise semantic entry point and update this file when long format behavior changes.

## Frontmatter

- `template`: 固定为 `jiaoan-shicao`。
- `course_name`: 课程名称。
- `course_attribute`: 通常为 `基本技能课程` 或 `工学一体化课程`。
- `textbook_name`: 教材名称；未知时留空。
- `class_name`: 教学班级；未知时留空。
- `total_hours`: 计划总课时；维护旧式完整样例时可保留。
- `teacher_name`: 教师姓名；未知时留空。
- `use_time`: 使用时间；维护旧式完整样例时可保留。
- `first_teaching_day`: 课程排课起点；新文档若用户给出授课起点，优先用 `YYYY-MM-DD`。

## Body Structure

正文保持三大部分，顺序固定。

### 学习任务分析

`## 学习任务分析` 包含 `学习任务：`、`课时：`、`起止日期：` 三个字段行，以及以下五个分析块：

- `### 一、学习任务描述`
- `### 二、学情分析`
- `### 三、学习目标`
- `### 四、学习重难点`
- `### 五、学习资源`

### 教学活动设计

- `## 教学活动设计——主题` 表示教学活动表。
- `### 学习环节——学习单元` 表示学习环节和单元。
- `#### 活动名称` 表示具体活动。
- `##### 课时` 后按空行分隔四个内容块：学习内容、学生活动、教师活动、教学方法与手段。

### 学业评价

- `## 学业评价` 保存评价内容。
- 评价项使用 `1. 考核项目；考核细则；考核方式`。
- 末尾保留 `小结：...`。

## Completeness Rules

- 材料不足时仍输出完整骨架。
- 不确定的学校、教材版本、班级、教师、日期和评价结论留空或标记复核。
- 不要虚构用户未提供或未暗示的信息。

## Renderer Notes

- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render` converts `jiaoan-shicao-full.md` to Typst through built-in shell logic.
- The conversion must not call an external executable.
- `--calendar-output <file>` copies the skill-provided `references/calendar.json` support resource.
- `--expected-typ` performs black-box comparison against a reference Typst file.

## Verification Detail

- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example --output <file>` must output a reviewable `jiaoan-shicao-full.md` structure.
- `--calendar-output <file>` must copy `calendar.json`.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --input <md> --typ <typ>` must generate Typst without external executables.
- `--expected-typ` must match the generated Typst against a fixture when provided.
