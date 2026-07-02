# End-of-Term Teaching Materials Markdown Contract

本契约定义 `end-of-term-teaching-materials` 的唯一事实源 Markdown。用户可以上传 Excel、照片、截图、文字说明或历史文件，但这些都只是整理材料；最终维护、诊断、复核和渲染都围绕一份 `end-of-term-full.md` 进行。

## Top-Level Metadata

| Field | Required | Notes |
|-------|----------|-------|
| `template` | yes | 固定为 `end-of-term-teaching-materials`。 |
| `date` | yes | 材料日期，建议使用 `YYYY-MM-DD`。 |
| `school_year` | yes | 学年，例如 `2025-2026`。 |
| `semester` | yes | 学期，例如 `第二学期`。 |
| `major_name` | yes | 专业名称。 |
| `course_name` | yes | 课程名称。 |
| `course_type_label` | no | 支持 `一体化`、`基本技能`、`单技能`；缺失时默认 `基本技能`。 |
| `class_name` | yes | 当前教师所带班级短名称数组。 |
| `teachers` | yes | 任课教师有序数组。 |
| `handover_class_name` | no | 交接班短名称数组。 |
| `handover_teachers` | no | 交接班教师有序数组。 |

如果 `package` 请求 `交接班记录封面`，`handover_class_name` 和 `handover_teachers` 必须同时存在；缺失时回到 Markdown 复核修正，不生成最终交付。

## Package Flags

`package` 使用中文 artifact 名称作为 key。缺失的 key 默认视为 `true`。

| Key | Notes |
|-----|-------|
| `成绩记分册` | PDF 中的成绩记分册封面和正文。 |
| `成绩汇总表` | PDF 中的过程任务汇总页。 |
| `成绩分析表` | PDF 中的分析页。 |
| `教学日志封面` | PDF 中的教学日志封面。 |
| `过程考核评价表封面` | PDF 中的过程考核评价表封面。 |
| `交接班记录封面` | 仅在交接班级和交接教师均存在时允许输出。 |

## Required Sections

Markdown 正文必须包含：

- `## 我带的学生`
- `## 过程考核任务`
- `## 成绩数据`
- `## 分析`
- `## 复核标记`

## Student Roster

`## 我带的学生` 是教师可编辑名单。推荐每行使用：

```text
学号 姓名
```

存在重名、跨班或后续需要稳定排序时，必须保留学号。

## Task Records

`## 过程考核任务` 按顺序列出过程考核任务。每一项使用：

```text
1. 任务名称-课时
```

最后一个连字符后的数字是课时。任务顺序决定 `## 成绩数据` 中 `任务1..任务N` 的映射。声明过的任务列必须保留，即使整列为空。

## Score Table

`## 成绩数据` 是主成绩表。列为：

```text
学号 | 姓名 | 任务1..任务N | 考勤 | 作业 | 期末
```

规则：

- `任务1..任务N` 对应 `## 过程考核任务` 的顺序。
- `考勤`、`作业`、`期末` 是平时成绩计算来源，其中 `期末` 表示期末测试原始成绩。
- 空成绩单元格保持空白。空白不是 `0`、`-1` 或自动复核项。
- 不在 Markdown 中写课程总评、折算分、汇总分、平时分、期末分等衍生字段；这些由 renderer 从 Markdown 计算。

## Review Markers

形如 `87?` 的值表示 agent 识别出一个可能成绩，但需要教师确认。每个这类值必须同时出现在 `## 复核标记` 中。

复核项必须包含：

| Field | Meaning |
|-------|---------|
| `类型` | 例如 `需复核`。 |
| `位置` | 明确到章节、学生、任务或字段。 |
| `当前值` | 当前 Markdown 中的值，例如 `87?`。 |
| `说明` | 为什么需要复核。 |

复核必须逐项处理：agent 先说明一个学生、一个任务或字段、当前值和疑点，等待教师确认或修正，再编辑 Markdown。全部复核清除后，`## 复核标记` 的正文必须正好是 `无`。只要仍有 `?` 或非空复核标记，`validate` 和 `deliver` 必须失败。

## Analysis Sections

`## 分析` 包含以下子节：

- `### 试卷分析`
- `### 存在问题`
- `### 今后改进措施`
- `### 异常情况分析`

生成或更新这些子节时，agent 应先向教师追问必要背景，再结合 Markdown 中的成绩数据撰写。可追问的信息包括：本轮教学重点和难点、学生整体学习状态、低分或缺考原因、任务完成中的共性问题、异常成绩说明、后续教学改进措施。

如果没有源文本，agent 可以写 `{{AI草稿: ...}}` 提醒教师复核。AI 草稿是可编辑正文，不是隐藏 source。

## Delivery

定稿后运行 `deliver`。公开目录只包含：

- `end-of-term-full.md`
- `end-of-term-package.typ`
- `end-of-term-package.pdf`
- `score-list.xlsx`

`score-list.xlsx` 只有 `学号`、`姓名`、`平时成绩`、`期末成绩` 四列，并按学号递增排序。
