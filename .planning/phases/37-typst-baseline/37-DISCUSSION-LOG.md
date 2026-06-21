# Phase 37: 调课单 Typst Baseline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-21
**Phase:** 37-调课单 Typst Baseline
**Areas discussed:** 表单字段范围, 版式结构, 审批与签字区, 视觉与字体口径

---

## 表单字段范围

| Option | Description | Selected |
|--------|-------------|----------|
| Free-form locked description | User provided the complete visible form content, including heading, recipient, explanatory paragraph, table headers, example rows, and closing signature. | ✓ |

**User's choice:** 用用户提供的具体文字和表格内容作为 Phase 37 hand-authored Typst baseline 的事实源。
**Notes:** 表格字段为序号、班级、课程、原上课时间、原授课教师、调整后上课时间、调整后上课教师、备注。

---

## 版式结构

| Option | Description | Selected |
|--------|-------------|----------|
| A4 landscape official form | A4 横版，页边距默认，标题、正文、全宽表格、落款依次排列。 | ✓ |
| Portrait form | Not selected. Would make the 8-column table tighter and less faithful to the described baseline. | |

**User's choice:** A4 横版，页边距默认；表格与版芯页面同宽，8 列多行。
**Notes:** 表格下方留类似公文格式的空白距离后放落款。

---

## 审批与签字区

| Option | Description | Selected |
|--------|-------------|----------|
| Closing signature only | Use the provided closing signature `电气工程系` and `2026年6月21日`; no extra approval grid is added in Phase 37. | ✓ |
| Multi-role approval grid | Not selected because the user did not request approval columns or signature boxes for this baseline. | |

**User's choice:** 表格下面放落款：`电气工程系` 和 `2026年6月21日`。
**Notes:** 下游不得擅自新增审批角色、签字格或意见栏；这些若需要应作为后续变体或新需求讨论。

---

## 视觉与字体口径

| Option | Description | Selected |
|--------|-------------|----------|
| Chinese official-document typography | Title uses 宋体二号加粗居中; body/table/signature use 仿宋四号; table cells centered both horizontally and vertically. | ✓ |

**User's choice:** 标题为宋体二号加粗居中；正文为仿宋四号分散对齐；表格为仿宋四号，单元格内容水平垂直居中；落款为仿宋四号。
**Notes:** 第一行 `教务处：` 无首行缩进；说明段首行缩进。

---

## Claude's Discretion

- Exact Typst point sizes, table column width distribution, row heights, line spacing, and blank distance may be chosen by the implementer to faithfully match the described A4 landscape official-form feel.

## Deferred Ideas

- Markdown contract and missing-field markers are Phase 38.
- Markdown-to-Typst renderer and generated-vs-reference verification are Phase 39.
- Complete skill entry, runtime adapter notes, PDF gate, and clarification questions are Phase 40.
