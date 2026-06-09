# End-of-Term Teaching Materials Data Contract

本契约定义 `end-of-term-teaching-materials` 技能在 Phase 11 接受和生成 Markdown intermediate 时使用的结构化数据。它只约束数据和复核语义，不实现 OCR、Excel、Typst、PDF 或表格导出。

## Top-Level Metadata

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `template` | yes | string | 固定为 `end-of-term-teaching-materials`。 |
| `date` | yes | string | 材料日期，建议使用 `YYYY-MM-DD`。 |
| `school_year` | yes | string | 学年，例如 `2025-2026`。 |
| `semester` | yes | string | 学期，例如 `第二学期`。 |
| `major_name` | yes | string | 专业名称。 |
| `course_name` | yes | string | 课程名称。 |
| `course_type_label` | no | string | 成绩汇总表的课程类型显示文本，例如 `一体化课□ 基本技能实训课√`；缺失时 renderer 使用该默认文本。 |
| `class_name` | yes | string array | 当前教师所带班级短名称数组，例如 `示例电气2`；renderers 在目标模板需要时自行追加 `班`。 |
| `teachers` | yes | string array | 任课教师有序数组；输出顺序跟随数组顺序，不添加 `primary_teacher`。 |
| `handover_class_name` | no | string array | 交接班短名称数组；可表示一个或多个交接班级。 |
| `handover_teachers` | no | string array | 交接班教师有序数组。 |

`handover_class_name` 和 `handover_teachers` 缺失时，表示没有交接班记录；即使 `package` 请求 `交接班记录封面`，后续 renderer 也应跳过该输出或提示缺少交接元数据。

## Package Flags

`package` 使用中文 artifact 名称作为 key。缺失的 `package` key 默认视为 `true`，但交接班输出仍然要求存在交接班元数据。

| Key | Type | Default | Notes |
|-----|------|---------|-------|
| `成绩记分册` | boolean | `true` | 一个 bundle：同时表示重新设计的成绩记分册封面和记分册正文，不拆成 cover/body 两个开关。 |
| `成绩汇总表` | boolean | `true` | 后续 Phase 12 输出。 |
| `成绩分析表` | boolean | `true` | 后续 Phase 12 输出。 |
| `教学日志封面` | boolean | `true` | 后续 Phase 12 输出。 |
| `过程考核评价表封面` | boolean | `true` | 后续 Phase 12 输出。 |
| `交接班记录封面` | boolean | `true` | 仅在 `handover_class_name` 和 `handover_teachers` 存在时输出。 |

`false` 表示不导出该 artifact。Phase 11 只记录这些开关，不生成最终文件。

## Student Roster Entries

学生名单可在结构化数据中以数组表示，也可在 Markdown 的 `## 我带的学生` 中保留为教师可编辑列表。

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `student_id` | recommended | string | 学号。重复姓名或需要稳定匹配时必须提供。 |
| `name` | yes | string | 学生姓名。 |
| `class_name` | no | string | 学生所属短班级名；跨班合并材料时建议提供。 |

`## 我带的学生` 默认可只列姓名；存在重名时使用 `学号 姓名`。

## Task And Teaching-Hour Records

过程考核任务在 Markdown 的 `## 过程考核任务` 中按顺序列出。每一项使用 `任务名称-课时`，最后一个连字符后的数字是课时。

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `task_name` | yes | string | 过程考核任务名称。 |
| `hours` | yes | number | 任务课时。 |
| `order` | recommended | number | 任务顺序；Markdown 中的顺序决定 `任务1..任务N` 列。 |

声明过的任务列必须在 `## 成绩数据` 中保留，即使整列为空。

## Assessment And Score Data

`## 成绩数据` 是主成绩表。列为 `学号`、`姓名`、`任务1..任务N`、`考勤`、`作业`、`期末`。任务列按 `## 过程考核任务` 的顺序映射。

| Field Category | Markdown Column | Notes |
|----------------|-----------------|-------|
| roster identity | `学号`, `姓名` | 用于匹配学生和复核问题。 |
| task scores | `任务1..任务N` | 对应有序任务列表，不在列名中重复长任务名。 |
| attendance | `考勤` | 平时记录输入，不计算衍生成绩。 |
| homework | `作业` | 平时记录输入，不计算衍生成绩。 |
| final exam | `期末` | 期末原始成绩输入，不写衍生字段。 |

空成绩单元格保持空白。空白不是 `0`，不是 `-1`，也不是自动复核项。

不要在 Markdown 中写课程总评、折算分、汇总分等衍生计算字段。这些是后续 Excel 或模板公式职责。

## Uncertain Values

形如 `87?` 的值表示 agent 识别出一个可能成绩，但需要教师确认。每个这类值必须同时出现在 `## 复核标记` 中。

复核项必须包含：

| Field | Meaning |
|-------|---------|
| `类型` | 例如 `需复核`。 |
| `位置` | 明确到章节、学生、任务或字段。 |
| `当前值` | 当前 Markdown 中的值，例如 `87?`。 |
| `说明` | 为什么需要复核。 |

复核问题必须说清学生、任务或字段、当前值。用户确认或修正后，agent 立即编辑 Markdown 值，并删除对应复核项。全部复核清除后，`## 复核标记` 的正文必须正好是 `无`。

## Analysis Sections

`## 分析` 包含以下子节：

- `### 试卷分析`
- `### 存在问题`
- `### 今后改进措施`
- `### 异常情况分析`

如果没有源文本，agent 可以写 `{{AI草稿: ...}}` 提醒教师复核。AI 草稿是可编辑正文，不是隐藏 source。

## Submission Metadata

提交元数据由 top-level metadata 和 `package` 共同表达：日期、学年、学期、专业、课程、班级、任课教师、可选交接班级、可选交接教师，以及需要导出的 artifact 开关。

Phase 12 可以在这个契约之上补充固定模板所需的 renderer metadata，但不得反向要求 Phase 11 Markdown 保留隐藏来源或衍生成绩字段。
