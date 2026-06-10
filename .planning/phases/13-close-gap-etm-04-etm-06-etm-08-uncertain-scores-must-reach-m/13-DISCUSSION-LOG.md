# Phase 13: Close gap: ETM-04/ETM-06/ETM-08 - uncertain scores must reach Markdown review - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-10
**Phase:** 13-close-gap-etm-04-etm-06-etm-08-uncertain-scores-must-reach-m
**Areas discussed:** uncertain score data shape, Markdown generation gate, review marker handling, abnormal PDF and red highlighting

---

## Uncertain Score Data Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Inline `87?` | Keep the existing Phase 11 teacher-facing uncertainty marker in structured JSON and Markdown. | yes |
| Nested object | Represent uncertainty as structured metadata such as `{ value: 87, uncertain: true }`. | |
| Planner discretion | Let planner choose a new representation. | |

**User's choice:** Use `87?`.
**Notes:** This preserves the Phase 11 contract and keeps the teacher-facing Markdown simple.

---

## Markdown Generation Gate

| Option | Description | Selected |
|--------|-------------|----------|
| Allow uncertain Markdown generation | Let `markdown` produce a visible review artifact containing abnormal values. | yes |
| Block before Markdown | Reject uncertain JSON before writing Markdown. | |
| Planner discretion | Let planner decide validation mode boundaries. | |

**User's choice:** Allow Markdown generation so the produced artifact can show the abnormal cells.
**Notes:** Normal final export readiness should still block unresolved uncertainty; the generated Markdown should make the abnormal data visible.

---

## Review Marker Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-create missing markers | If JSON has `?` values without markers, generate matching `## 复核标记` rows. | yes |
| Require explicit markers | Fail unless every uncertainty already has a marker. | |
| Planner discretion | Let planner choose. | |

**User's choice:** Automatically add missing review markers.
**Notes:** Auto-created markers must still be clear enough for agent/user dialogue: student, task or field, current value, and explanation.

---

## Abnormal PDF And Red Highlighting

| Option | Description | Selected |
|--------|-------------|----------|
| Allow abnormal preview PDF after confirmation | Agent explains unresolved problems and asks whether to generate anyway; if user says yes, generate red-highlighted abnormal PDF. | yes |
| Never generate PDF with unresolved review | Only allow PDF after all review markers are cleared. | |
| Generate with warning only | Produce PDF but rely on manifest text instead of visual highlighting. | |

**User's choice:** Allow a PDF with red-background abnormal cells when the user explicitly wants it.
**Notes:** The score book should also highlight `学期成绩` below 60 in red. The agent must say clearly that problems exist and ask whether to generate PDF anyway.

---

## Claude's Discretion

- Exact flag names, manifest fields, fixture names, and internal implementation details are left to planner/executor.

## Deferred Ideas

None.
