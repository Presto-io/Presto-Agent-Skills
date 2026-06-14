# Teaching Design Package Format and Orchestration

This reference owns the detailed package contract for the `teaching-design-package` skill. Keep `SKILL.md` concise and point here for field rules, module handoff, split output status, optional end-of-term integration, review gates, and combined package output semantics.

## Requirement Traceability

- `TDP-05`: Add a new orchestration skill named `teaching-design-package`.
- `TDP-06`: Preserve `jiaoan-jihua` and `jiaoan-shicao` as standalone public skills.
- `TDP-07`: Define a persistent teacher-reviewable Markdown intermediate before Typst/PDF generation.
- `TDP-08`: Plan split teaching-plan and lesson-plan Typst/PDF output status.
- `TDP-09`: Keep the canonical skill portable and represent Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent in adapter notes.
- `TDP-10`: Support the end-of-term materials workflow as an optional module while reusing `end-of-term-teaching-materials` data, scoring evidence, table artifacts, workbook output, manifest rules, and review gates.
- `TDP-11`: Do not bypass the module-local `end-of-term-full.md` review point or its `## 复核标记` export gate.
- `TDP-12`: Include `end-of-term-package.pdf` when the optional module is enabled and keep workbook/table artifacts discoverable from the package manifest.
- `TDP-13`: Use `teaching-design-package.pdf` as the default combined final artifact when selected PDFs exist and merge/compile tooling succeeds.
- `TDP-14`: If split compilation or merged PDF generation is unavailable, fail with explicit manifest/status evidence instead of claiming a complete final package.

## Package Markdown Intermediate

The package checkpoint is `teaching-design-package-full.md`. It is the semantic handoff point for teacher review and downstream rendering. A package is not final-ready until this Markdown exists and all unresolved review markers have been addressed.

The maintained v1.13 baseline is the teacher-facing reference document at `templates/teaching-design-package-full.md`. Its teacher-visible format must not be changed to satisfy parser internals. The renderer adapts around the baseline shape and writes machine status, provenance, defaults, and derived evidence to generated handoffs, Typst comments, or manifest fields.

Required v1.13 baseline body anchors:

- `# 授课进度计划`
- `# 教学设计方案`

Required v1.13 baseline frontmatter fields:

- `course_name`
- `major_name`
- `course_attribute`
- `textbook_name`
- `class_name`
- `teachers`
- `first_teaching_day`

The package YAML must not contain teacher-maintained derived/default/output/validation fields:

- `total_hours`
- `school_year`
- `semester`
- `daily_hours`
- `hour_unit`
- `date_display_format`
- `date_locale`
- `calendar_source`
- `holidays`
- `makeup_days`
- `source_of_truth`
- `outputs`
- `validation`

Legacy package drafts may still contain the old orchestration sections, but the corrected baseline does not require or inject them:

- `## 课程与整包元数据`
- `## 调度输入`
- `## 调度证据`
- `## 授课计划`
- `## 实操教案`
- `## 输出清单`
- `## 复核标记`

The package-level Markdown is the normalized source of truth. Module-specific overrides are allowed only when the source material explicitly requires them, and the override must be visible in generated handoff/provenance evidence rather than hidden in Typst.

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

## Optional End-of-Term Module Behavior

The end-of-term module is optional package behavior. The frontmatter field `modules.end_of_term.enabled` decides whether package readiness depends on module artifacts.

When disabled:

- manifest `end_of_term.status` is `disabled`
- missing `end-of-term-full.md`, module manifest, tables, workbooks, `end-of-term-package.typ`, or `end-of-term-package.pdf` is not a package failure
- `final_ready` is derived from selected non-end-of-term outputs and package-level review markers

When enabled:

- `end-of-term-full.md` is the module handoff and persistent review checkpoint
- `end-of-term-source.json` is the explicit source-data path expected by the package helper unless the user supplies another path
- `end-of-term-output/manifest.json` is the module manifest path expected by package-level discovery
- the package helper may call or reference `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh validate`, `markdown`, `render`, `verify`, and `manifest`
- score calculation, deterministic tables, workbook generation, and review-marker resolution remain owned by `skills/end-of-term-teaching-materials`
- final package readiness is blocked when module-local `## 复核标记` is not exactly `无` or the module manifest has `review_cleared: false`
- `render --abnormal-review` remains non-final inspection behavior; its `artifact_kind: abnormal_review`, `final_ready: false`, and `review_cleared: false` values must be preserved in package status

The package skill must not silently correct uncertain scores such as `87?`, missing fields, or AI-drafted analysis text. Those items continue through the end-of-term module's one-item-at-a-time teacher review pattern.

## End-of-Term Artifact Pointers

Package manifests should expose pointers, not flatten module evidence. The `end_of_term` object should make these paths/statuses discoverable when the module is enabled:

- `end-of-term-full.md`
- `end-of-term-output/end-of-term-package.typ`
- `end-of-term-output/end-of-term-package.pdf`
- `end-of-term-output/manifest.json`
- `end-of-term-output/tables/score-data.json`
- `end-of-term-output/tables/calculated-score-data.json`
- `end-of-term-output/tables/score-summary.json`
- `end-of-term-output/tables/highlight-evidence.json`
- `end-of-term-output/tables/score-list.md`
- `end-of-term-output/tables/score-list.xlsx`
- `end-of-term-output/tables/scorebook.xlsx`

The package manifest may summarize module booleans such as `review_cleared`, `calculated_scores_verified`, `table_artifacts_verified`, and `workbook_verified`, but detailed score rows, formulas, highlight evidence, and workbook content stay in the end-of-term module artifacts.

## Jiaoan Module Handoff

The package skill composes existing skills through module-local Markdown intermediates.

For v1.13 baseline mode, the package helper maps the YAML `teachers` list into legacy scalar handoff metadata:

- one teacher becomes that exact `teacher_name`
- multiple teachers join with `、`
- an empty or missing list leaves `teacher_name` blank and records a provenance warning

The helper derives scheduling fields from `# 授课进度计划`, not from package YAML defaults. The current baseline must derive:

- package total: `160H`
- task totals: `CA6140=40H`, `X62W=60H`, `Z3040=60H`
- task ranges: `5月11日——5月15日`, `5月18日——5月27日`, `5月27日——6月5日`
- academic term: `2025-2026学年第二学期`

The term is inferred from `first_teaching_day`; first-half dates infer previous-year/current-year second semester, and autumn dates infer current-year/next-year first semester.

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

For v1.13 baseline mode, lesson-plan activity `##### xH` rows are render handoff data only. They are mapped from same-name teaching-plan rows when possible, otherwise from same-order rows inside the same learning task. If an activity cannot be mapped, the package command must fail or record explicit non-final/review-needed status; it must not guess a duration.

## Split Output Status

The package plans split outputs first:

- `teaching-design-package.typ`: package Typst generated from the single baseline Markdown source
- `teaching-plan.typ`: Typst generated from `jiaoan-jihua-full.md`
- `lesson-plans.typ`: Typst generated from `jiaoan-shicao-full.md`
- `end-of-term-package.typ`: Typst generated by the optional end-of-term module when enabled
- `teaching-plan.pdf`: PDF status for the teaching-plan Typst file
- `lesson-plans.pdf`: PDF status for the lesson-plan Typst file
- `end-of-term-package.pdf`: PDF status for the optional end-of-term module when enabled

The manifest must preserve these split-output keys or equivalent entries under `split_outputs`:

- `teaching_plan_typ`
- `lesson_plans_typ`
- `end_of_term_typ`
- `teaching_plan_pdf`
- `lesson_plans_pdf`
- `end_of_term_pdf`
- `review_markers`
- `final_ready`

For v1.13 baseline mode, the manifest also records provenance:

- `generated_from_markdown: true`
- `source_markdown`
- `generated_package_markdown`
- `package_typ`
- `teaching_plan_handoff`
- `lesson_plan_handoff`
- `section_anchors`
- `derived_hours`
- `derived_dates`
- `inferred_term`
- `activity_hour_mapping`
- `phase29_pdf_slots`

Status semantics:

- Typst status may be `planned`, `passed`, or `failed`.
- PDF status may be `not_run`, `missing_compiler`, `passed`, or `failed`.
- PDF status must not be `passed` unless an explicit PDF command ran and the expected PDF file exists.
- If a renderer or compiler is unavailable, record partial Typst/status evidence instead of claiming completion.

## Combined Package Output Behavior

The default final artifact is `teaching-design-package.pdf`. It is package-level output, separate from module-local PDFs.

Combined status is `passed` only when all selected split PDFs exist and an explicit merge or compile step leaves an actual `teaching-design-package.pdf` file on disk. Typst generation, module manifests, or planned split outputs are not sufficient evidence.

If only split artifacts are available, preserve successful split-output evidence and set `combined_output.status` to `merge_unavailable`, `missing_compiler`, or `failed` with a clear reason. Do not set package `final_ready` to `true` for selected combined delivery unless the combined PDF exists or a later approved workflow explicitly accepts split-only delivery.

Phase 29 owns the final PDF parity gates for:

- `teaching-plan.pdf`
- `lesson-plans.pdf`
- `teaching-design-package.pdf`

Phase 28 may create Typst and planned PDF slots, but those PDF slots stay non-passed unless an explicit PDF command creates real files.

## Failure and Status Semantics

Use explicit status values:

- `disabled`: optional module is intentionally off and missing module artifacts are not failures
- `planned`: an artifact or module step is expected but not executed yet
- `not_run`: a compile, render, verify, or merge step was not executed
- `passed`: an explicit command ran and required output/evidence exists
- `failed`: an explicit command ran and failed or expected output is absent
- `missing_compiler`: Typst or another required compiler is unavailable
- `merge_unavailable`: split PDFs may exist but no local PDF merge/compile path was available
- `blocked_review`: package-level or enabled module-level review markers are unresolved

`final_ready` is derived from package review markers, selected split outputs, enabled module statuses, module `review_cleared`, `calculated_scores_verified`, `table_artifacts_verified`, `workbook_verified`, selected PDF status, and combined output status. Do not let a clean `jiaoan` split override a blocked enabled end-of-term module.

## Runtime Portability

Canonical process text should describe files, contracts, and verification. Runtime-private syntax belongs only in `SKILL.md` adapter notes. OpenClaw and Hermes Agent coverage must mention skill-folder discovery, support-file availability, script execution permissions, and calendar/support resources.

## Verification Detail

Use lightweight checks for this phase:

```bash
rg "TDP-05|TDP-06|TDP-07|TDP-08|TDP-09" \
  skills/teaching-design-package/SKILL.md \
  skills/teaching-design-package/references/format-and-orchestration.md

rg "TDP-10|TDP-11|TDP-12|TDP-13|TDP-14" \
  skills/teaching-design-package/SKILL.md \
  skills/teaching-design-package/references/format-and-orchestration.md

rg "Codex|Claude Code|Gemini CLI|OpenCode|OpenClaw|Hermes Agent" \
  skills/teaching-design-package/SKILL.md

bash -n skills/teaching-design-package/scripts/teaching-design-package.sh

skills/teaching-design-package/scripts/teaching-design-package.sh example --output /tmp/tdp-example.md

skills/teaching-design-package/scripts/teaching-design-package.sh plan-split \
  --input /tmp/tdp-example.md \
  --out-dir /tmp/tdp-split

skills/teaching-design-package/scripts/teaching-design-package.sh manifest \
  --input /tmp/tdp-example.md \
  --out-dir /tmp/tdp-split
```

The existing `jiaoan-jihua` and `jiaoan-shicao` public command surfaces should remain unchanged.
