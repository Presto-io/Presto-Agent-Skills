# Teaching Design Package Format and Orchestration

This reference owns the detailed package contract for the `teaching-design-package` skill. Keep `SKILL.md` concise and point here for field rules, module handoff, split output status, review gates, and Phase 24 deferrals.

## Requirement Traceability

- `TDP-05`: Add a new orchestration skill named `teaching-design-package`.
- `TDP-06`: Preserve `jiaoan-jihua` and `jiaoan-shicao` as standalone public skills.
- `TDP-07`: Define a persistent teacher-reviewable Markdown intermediate before Typst/PDF generation.
- `TDP-08`: Plan split teaching-plan and lesson-plan Typst/PDF output status.
- `TDP-09`: Keep the canonical skill portable and represent Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent in adapter notes.

## Package Markdown Intermediate

The package checkpoint is `teaching-design-package-full.md`. It is the semantic handoff point for teacher review and downstream rendering. A package is not final-ready until this Markdown exists and all unresolved review markers have been addressed.

Required top-level sections:

- `## 课程与整包元数据`
- `## 调度输入`
- `## 调度证据`
- `## 授课计划`
- `## 实操教案`
- `## 输出清单`
- `## 复核标记`

Required frontmatter fields:

- `template: "teaching-design-package"`
- `course_name`
- `major_name`
- `teacher_name`
- `class_name`
- `first_teaching_day`
- `daily_hours`
- `modules`
- `outputs`

The package-level metadata is the normalized source of truth. Module-specific overrides are allowed only when the source material explicitly requires them, and the override must be visible near the module handoff block.

## Scheduling Evidence

Scheduling evidence consumes the shared `references/scheduling-contract.md` model. The package contract uses source-order `items[]` with stable pointers and does not expose the old `jiaoan-jihua.sh` parser as the package API.

Teacher-facing evidence should show:

- source pointer such as `task:1/stage:1/row:1` or `lesson:1/activity:1`
- task/activity/lesson title
- assigned hours
- start and end date
- term week and weekday
- date-level hour-consumption evidence
- nearby review markers when data is missing, uncertain, conflicting, or exhausted

Unresolved review markers block final readiness. Downstream render/export must not silently drop them. The manifest must mirror unresolved markers in `review_markers` and set `final_ready` to `false`.

## Jiaoan Module Handoff

The package skill composes existing skills through module-local Markdown intermediates.

### Teaching Plan Module

The teaching-plan handoff file is `jiaoan-jihua-full.md`. It preserves the `jiaoan-jihua` contract:

- frontmatter: `major_name`, `course_name`, `teacher_name`, `class_name`, `first_teaching_day`, optional `daily_hours`, `template: "jiaoan-jihua"`
- body: ordered `##` learning tasks, `###` stages, and content lines ending with integer hour markers such as `-2`
- source order is stable and compatible with the Phase 22 scheduling contract

The package helper may scaffold this file from package sections, but it must not change `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` public behavior.

### Lesson Plan Module

The lesson-plan handoff file is `jiaoan-shicao-full.md`. It preserves the `jiaoan-shicao` three-part structure:

- `## 学习任务分析`
- `## 教学活动设计`
- `## 学业评价`

Unknown or incomplete lesson-plan fields should remain blank or be marked for review. The package helper may scaffold this file from package sections, but it must not invent school, class, teacher, textbook, date, or evaluation facts.

## Split Output Status

Phase 23 plans split outputs first:

- `teaching-plan.typ`: Typst generated from `jiaoan-jihua-full.md`
- `lesson-plans.typ`: Typst generated from `jiaoan-shicao-full.md`
- `teaching-plan.pdf`: PDF status for the teaching-plan Typst file
- `lesson-plans.pdf`: PDF status for the lesson-plan Typst file

The manifest must use these keys:

- `teaching_plan_typ`
- `lesson_plans_typ`
- `teaching_plan_pdf`
- `lesson_plans_pdf`
- `review_markers`
- `final_ready`

Status semantics:

- Typst status may be `planned`, `passed`, or `failed`.
- PDF status may be `not_run`, `missing_compiler`, `passed`, or `failed`.
- PDF status must not be `passed` unless an explicit PDF command ran and the expected PDF file exists.
- If a renderer or compiler is unavailable, record partial Typst/status evidence instead of claiming completion.

## Deferred to Phase 24

The following are intentionally not implemented in Phase 23:

- optional `end-of-term-teaching-materials` module integration
- workbook/table artifact discovery for the optional end-of-term module
- `end-of-term-package.pdf`
- default combined final package output
- merged PDF behavior and failure semantics for a combined final package

Phase 23 may mention these only as deferred fields, placeholders, or help text.

## Runtime Portability

Canonical process text should describe files, contracts, and verification. Runtime-private syntax belongs only in `SKILL.md` adapter notes. OpenClaw and Hermes Agent coverage must mention skill-folder discovery, support-file availability, script execution permissions, and calendar/support resources.

## Verification Detail

Use lightweight checks for this phase:

```bash
rg "TDP-05|TDP-06|TDP-07|TDP-08|TDP-09" \
  skills/teaching-design-package/SKILL.md \
  skills/teaching-design-package/references/format-and-orchestration.md

rg "Codex|Claude Code|Gemini CLI|OpenCode|OpenClaw|Hermes Agent" \
  skills/teaching-design-package/SKILL.md

bash -n skills/teaching-design-package/scripts/teaching-design-package.sh

skills/teaching-design-package/scripts/teaching-design-package.sh example --output /tmp/tdp-example.md

skills/teaching-design-package/scripts/teaching-design-package.sh plan-split \
  --input /tmp/tdp-example.md \
  --out-dir /tmp/tdp-split
```

The existing `jiaoan-jihua` and `jiaoan-shicao` public command surfaces should remain unchanged.
