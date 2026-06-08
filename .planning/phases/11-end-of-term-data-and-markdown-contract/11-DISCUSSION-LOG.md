# Phase 11: End-of-Term Data and Markdown Contract - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-09
**Phase:** 11-End-of-Term Data and Markdown Contract
**Areas discussed:** source truth, Markdown structure, package flags, score entry shape, review loop, export expectations

---

## Source Truth

| Option | Description | Selected |
|--------|-------------|----------|
| Excel-like sheets | Mirror each workbook sheet as separate Markdown data blocks. | |
| Raw-data source | Treat raw score data as the only maintained score source. | ✓ |
| Hybrid source | Keep raw scores plus separate analysis/cover blocks. | |

**User's choice:** Score data should be maintained from raw values, not final sheet replicas.
**Notes:** The teacher-facing Markdown should not include formulas. Existing Excel formulas drive final calculations.

---

## Markdown Structure

| Option | Description | Selected |
|--------|-------------|----------|
| One Markdown file | One `end-of-term-full.md` generates the whole package. | ✓ |
| Multiple Markdown files | Split scores, covers, and analysis into separate files. | |
| Final-artifact Markdown | Mirror each final output as a separate Markdown source. | |

**User's choice:** One file generates a full package.
**Notes:** The user manually refined the structure toward compact YAML plus concise body sections.

---

## YAML And Package Flags

| Option | Description | Selected |
|--------|-------------|----------|
| English package keys | Use internal names such as `gradebook_cover`. | |
| Chinese package keys | Use final artifact names directly. | ✓ |
| Separate cover/body switches | Control score-book cover and body separately. | |

**User's choice:** Use Chinese artifact names. `成绩记分册` is one bundle and always includes cover plus body.
**Notes:** Missing package keys default to `true`; `false` disables export. Handover output also requires handover metadata.

---

## Score Entry Shape

| Option | Description | Selected |
|--------|-------------|----------|
| One section per task | Natural text blocks but too many lines. | |
| Markdown score table | One row per student, task columns added automatically. | ✓ |
| Plain text matrix | Compact but less readable as Markdown. | |

**User's choice:** Use a Markdown table and require agents to pad/align it when generating content.
**Notes:** Task definitions are an ordered list with `任务名称-课时`; score table columns are `任务1..任务N`.

---

## Missing And Uncertain Scores

| Option | Description | Selected |
|--------|-------------|----------|
| `-1` for missing scores | Explicit sentinel for missing values. | |
| Blank for missing scores | Leave empty cells blank. | ✓ |
| Inline `?` for uncertain scores | Use values such as `87?` for recognition uncertainty. | ✓ |

**User's choice:** Blank score cells stay blank. Uncertain recognized values use `?`.
**Notes:** Blank may mean leave, suspension, or no participation and should not become 0. Declared tasks are preserved even if their score column is blank.

---

## Review Loop

| Option | Description | Selected |
|--------|-------------|----------|
| Export with warnings | Allow export while review items remain. | |
| Block until reviewed | Keep asking until review markers are gone. | ✓ |

**User's choice:** The agent must ask the teacher one item at a time until `复核标记` is cleared.
**Notes:** Questions must include student name, specific task name or field name, and current value. Cleared state is `## 复核标记` followed by `无`.

---

## Export Expectations

| Option | Description | Selected |
|--------|-------------|----------|
| Excel from scratch | Build workbook layout manually. | |
| Template-preserving Excel | Fill the provided workbook style and formulas. | ✓ |
| Excel cover sheet | Keep score-book cover inside the workbook. | |
| Redesigned cover PDF | Redesign score-book cover using Word-like cover style. | ✓ |

**User's choice:** Export Excel matching the provided template and export a complete printable PDF package. Redesign the score-book cover separately instead of stretching an Excel cover sheet.
**Notes:** Cover metadata needed by Excel should move to a safe area in `原始数据` without affecting sorting/filtering.

---

## Claude's Discretion

- Planner and executor may choose exact parser internals and generated artifact names.
- Planner and executor may choose how to implement Markdown table alignment.
- Planner and executor may choose how to represent internal normalized data after parsing, as long as teacher-facing Markdown remains unchanged.

## Deferred Ideas

- Photo/handwriting recognition implementation is deferred from Phase 11 contract capture. The contract records how uncertain recognized scores are represented and resolved.
- Excel and PDF renderer implementation belongs to Phase 12.
