# Phase 11: End-of-Term Data and Markdown Contract - Context

**Gathered:** 2026-06-09
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase defines the data and Markdown contract for the `end-of-term-teaching-materials` skill. The skill should help a teacher turn score materials, roster data, regular-score data, class metadata, and optional handover information into one reviewable Markdown source file. That Markdown is the durable hand-editable source of truth before any Excel or PDF export.

Phase 11 does not implement the Excel/PDF renderer. It must, however, capture enough contract detail for Phase 12 to export an Excel workbook matching the provided score-book template style and a complete printable PDF package controlled by the Markdown `package` flags.

</domain>

<decisions>
## Implementation Decisions

### Markdown Source Shape
- **D-01:** The canonical intermediate is one file named like `end-of-term-full.md`; one Markdown file should generate one complete end-of-term materials package.
- **D-02:** The Markdown uses YAML frontmatter for package metadata and concise body sections for teacher-editable data and analysis text.
- **D-03:** The final Markdown must not include `sources` entries. Photo recognition, spreadsheet ingestion, and roster ingestion may be used to create the Markdown, but the teacher-facing artifact is the edited Markdown itself.
- **D-04:** Agent-generated Markdown tables must be fully padded and aligned so teachers can continue editing them without vertical columns drifting.

### YAML Metadata
- **D-05:** Required top-level metadata includes `template`, `date`, `school_year`, `semester`, `major_name`, `course_name`, `class_name`, and `teachers`.
- **D-06:** `class_name` is an array of short class names such as `示例电气2`; renderers add `班` where the target template requires it.
- **D-07:** `teachers` is an ordered array. Do not add `primary_teacher`; output should follow the `teachers` order.
- **D-08:** Optional handover metadata is represented as top-level `handover_class_name` and `handover_teachers`. If handover metadata is absent, there is no handover record and no handover cover is generated.
- **D-09:** `handover_class_name` also supports one or multiple short class names for combined-class handover cases.

### Package Flags
- **D-10:** `package` uses Chinese artifact names as keys.
- **D-11:** Missing `package` keys default to `true`, except handover output still requires handover metadata to exist.
- **D-12:** `false` means do not export that artifact.
- **D-13:** `成绩记分册: true` is a bundle: it generates both the redesigned score-book cover and the score-book body. Do not split it into separate cover/body switches.
- **D-14:** The supported package keys for this slice are `成绩记分册`, `成绩汇总表`, `成绩分析表`, `教学日志封面`, `过程考核评价表封面`, and `交接班记录封面`.

### Body Sections
- **D-15:** `## 我带的学生` lists the students taught by the current teacher. Default entries can be names; if duplicate names exist, use `学号 姓名`.
- **D-16:** `## 过程考核任务` is an ordered list. Each item has the form `任务名称-课时`, and the final hyphen-number suffix is the hours value.
- **D-17:** Declared task columns are always preserved in output even when an entire task score column is blank.
- **D-18:** `## 成绩数据` is the primary score table. Columns are `学号`, `姓名`, `任务1..任务N`, `考勤`, `作业`, and `期末`. Task columns map to the ordered tasks above.
- **D-19:** Do not put derived fields such as `平时分`, `期末分`, or `学期成绩` in Markdown. Calculations belong to the Excel/template renderer and should follow the existing Excel formula logic.
- **D-20:** A blank score cell means no score was filled and must remain blank. It is not `0`, not `-1`, and not automatically a review item.
- **D-21:** A value with `?`, such as `87?`, means the agent recognized a likely score but needs teacher confirmation.
- **D-22:** `## 分析` contains `### 试卷分析`, `### 存在问题`, `### 今后改进措施`, and `### 异常情况分析`. If source text is absent, the agent may write AI draft text for the teacher to review.
- **D-23:** `## 复核标记` is mandatory. When all review items are resolved, this section body is exactly `无`.

### Review Loop
- **D-24:** The skill must not enter final export completion while `## 复核标记` contains any item other than `无`.
- **D-25:** Uncertain photo/handwriting recognition is shown inline in `## 成绩数据` as values like `87?`, and each uncertainty is also listed in `## 复核标记`.
- **D-26:** The agent must ask the teacher about review items one by one until every item is resolved.
- **D-27:** Review questions must include the student name, the specific task name or field name, and the current value. Example: `学生乙「CA6140卧式车床控制线路安装与调试」成绩识别为 87，请确认。`
- **D-28:** After confirmation or correction, the agent edits the Markdown value, removes the corresponding review item, and continues until `## 复核标记` is `无`.
- **D-29:** At the end of a skill run, the agent must clearly tell the teacher which items still need review. If no review items remain, say that review is cleared.

### Export Expectations For Downstream Planning
- **D-30:** Phase 12 should export an Excel workbook matching the provided score-book template style. Prefer filling a fixed template while preserving layout, merged cells, formulas, and styles.
- **D-31:** The score-book cover should be redesigned as a Word/PDF-style cover similar to the provided `教学日志 过程考核评价表 封面` document, not dragged around inside an Excel cover sheet.
- **D-32:** Cover metadata needed by Excel should move into a safe metadata block in the `原始数据` sheet, without interfering with sorting or filtering score data.
- **D-33:** PDF export should produce a complete printable package using `package` flags, exporting only artifacts that are not `false` and have required data. The teacher should be able to print the resulting PDF set directly.

### Markdown Contract Example

```markdown
---
template: end-of-term-teaching-materials
date: 2026-06-05
school_year: 2025-2026
semester: 第二学期
major_name: 电气自动化技术
course_name: 电气设备控制线路安装与调试
class_name:
  - 示例电气2
teachers:
  - 张老师
  - 李老师
handover_class_name:
  - 示例电气1
handover_teachers:
  - 王老师

package:
  成绩记分册: true
  成绩汇总表: true
  成绩分析表: true
  教学日志封面: true
  过程考核评价表封面: true
  交接班记录封面: true
---

## 我带的学生

学生甲
学生乙

## 过程考核任务

1. CA6140卧式车床控制线路安装与调试-40
2. X62W万能铣床控制线路安装与调试-60
3. Z3040摇臂钻床控制线路安装与调试-60

## 成绩数据

| 学号 | 姓名 | 任务1 | 任务2 | 任务3 | 考勤 | 作业 | 期末 |
|---|---|---:|---:|---:|---:|---:|---:|
| XH000001 | 学生甲 | 80 | 64 |  | 100 | 100 | 63 |
| XH000002 | 学生乙 | 87? | 61 |  | 100 | 94 | 60 |

## 分析

### 试卷分析

{{AI草稿: 根据原始成绩、任务完成情况、缺失数据和课程特点生成，可人工修改。}}

### 存在问题

{{AI草稿: 根据成绩异常、低分项、缺失项和课程实施情况生成，可人工修改。}}

### 今后改进措施

{{AI草稿: 根据存在问题生成教学改进建议，可人工修改。}}

### 异常情况分析

无

## 复核标记

| 类型 | 位置 | 当前值 | 说明 |
|---|---|---|---|
| 需复核 | 成绩数据 / 学生乙 / CA6140卧式车床控制线路安装与调试 | 87? | 手写识别不确定，请确认。 |
```

### Claude's Discretion
Planner and executor may choose exact parser implementation, file names for generated artifacts, and internal data structures, but must preserve the teacher-facing Markdown shape above and the review-before-export behavior.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Planning
- `.planning/ROADMAP.md` — Defines Phase 11 goal, ETM-01 through ETM-04, and Phase 12 rendering dependency.
- `.planning/REQUIREMENTS.md` — Defines v1.7 end-of-term requirements and existing out-of-scope constraints that must be revisited if photo/OCR implementation is planned.
- `.planning/PROJECT.md` — Defines the v1.7 milestone goal and Markdown-first document workflow constraints.
- `.planning/STATE.md` — Records current workflow state and prior milestone decisions.
- `.planning/phases/04-markdown-normalization-contract/04-CONTEXT.md` — Locks `YAML frontmatter + body` as the shared document-workflow intermediate.

### Repository Contract
- `docs/markdown-normalization-contract.md` — Defines persistent reviewable Markdown and explicit review marking for ambiguous/lossy content.
- `docs/directory-spec.md` — Defines skill-local placement for `SKILL.md`, `templates/`, `scripts/`, and `references/`.
- `templates/skill/SKILL.md` — Canonical skill template and runtime adapter notes structure.
- `docs/compatibility-matrix.md` — Required runtime compatibility expectations.

### Existing Concrete Skills
- `skills/gongwen/SKILL.md` — Existing Markdown-to-rendered-document skill pattern.
- `skills/jiaoan-shicao/SKILL.md` — Existing teaching-document skill with skill-local templates/scripts.
- `skills/jiaoan-jihua/SKILL.md` — Existing teaching-schedule skill and calendar/resource pattern.

### User-Provided Template Materials
- `/Users/mrered/Desktop/教学/电气设备控制线路安装与调试/记分册 示例电气2.xlsx` — Provided score-book workbook template and data example.
- `/Users/mrered/Desktop/教学/电气设备控制线路安装与调试/教学日志 过程考核评价表 封面 示例电气2.docx` — Provided cover style reference; internal content type is macro-enabled Word document XML despite `.docx` extension.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `templates/skill/SKILL.md`: Provides the canonical structure for the new skill, including metadata, workflow, runtime adapter notes, verification, and safety.
- `docs/markdown-normalization-contract.md`: Provides the shared Markdown intermediate contract and explicit review-marker requirement.
- Existing document skills under `skills/gongwen/`, `skills/jiaoan-shicao/`, and `skills/jiaoan-jihua/`: Provide patterns for concise `SKILL.md`, skill-local `templates/`, skill-local `scripts/`, and runtime-neutral canonical processes.

### Established Patterns
- New skills live under `skills/<skill-name>/SKILL.md`.
- Long references and support resources belong under `skills/<skill-name>/references/`.
- Skill output templates belong under `skills/<skill-name>/templates/`.
- Runtime differences stay in `Runtime Adapter Notes`, not separate duplicated skill files.
- Markdown is reviewable source of truth; target outputs are generated from scripts/templates.

### Integration Points
- Add `skills/end-of-term-teaching-materials/SKILL.md`.
- Add `skills/end-of-term-teaching-materials/templates/end-of-term-full.md`.
- Plan parsing and validation behavior for the Markdown structure above.
- Phase 12 should add scripts/templates for Markdown-to-Excel and Markdown-to-PDF export while preserving the provided template style.

</code_context>

<specifics>
## Specific Ideas

- The teacher wants to photograph handwritten classroom score sheets, combine those results with regular-score data, student roster data, and metadata, then have the agent produce a Markdown file for review.
- The teacher will directly edit the final Markdown rather than maintain separate source references in the Markdown.
- Uncertain recognized scores should be represented as `87?` in the score table and explained in `## 复核标记`.
- The agent should keep asking the teacher about review items until `## 复核标记` becomes `无`.
- Blank score cells are legitimate and may indicate leave, suspension, or no participation; they must remain blank.
- Excel export should keep the user-provided score-book template style and formula logic.
- The score-book cover should be redesigned from the Word cover style rather than implemented as a pulled-around Excel sheet.
- The PDF package should be complete and immediately printable, with output controlled by `package`.

</specifics>

<deferred>
## Deferred Ideas

- Implementing handwriting/photo recognition is not part of Phase 11's contract-writing work. Phase 11 only defines how uncertain recognized values are represented and resolved in Markdown. If OCR/photo recognition is added to v1.7 implementation scope, update requirements/roadmap or explicitly plan it as a bounded input-normalization step.
- Implementing the Excel/PDF renderer belongs to Phase 12, using the contract captured here.

</deferred>

---

*Phase: 11-End-of-Term Data and Markdown Contract*
*Context gathered: 2026-06-09*
