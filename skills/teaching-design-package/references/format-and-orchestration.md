# Teaching Design Package Format and Orchestration

This reference defines the teacher-facing source-material orchestration and standalone package contract for `teaching-design-package`. The normal path is:

```text
source materials -> clarification/questions -> teacher-editable unified Markdown -> finalized Markdown -> package-owned validation/rendering
```

The skill folder must remain usable when installed by itself. Script commands validate and render finalized Markdown; they do not replace teacher-agent clarification, teacher review, or content organization.

## Requirement Traceability

- `TDPKG-01`: The package can be installed and used as one skill folder.
- `TDPKG-02`: Package capability is implemented through its own Markdown contract, data model, validation, Typst generation, and PDF status path.
- `TDPKG-03`: Runtime adapter notes cover Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent under the standalone boundary.
- `TDPKG-04`: The canonical workflow starts from teacher source materials, clarification, organization, and one reviewable full-package Markdown.
- `TDPKG-05`: The unified Markdown is the human-editable source of truth before rendering.
- `TDPKG-06`: Scripts are finalized-Markdown validation and delivery tools, not the teacher's interactive organizing entry.
- `TDPKG-07`: A successful public delivery directory contains exactly one unified Markdown, one unified Typst, and three PDFs.
- `TDPKG-08`: Successful public delivery directories do not contain status, manifest, stderr log, model JSON, split Typst, or temporary state files.
- `TDPKG-09`: Package-owned diagnostics stay in hidden work/debug/failure paths.
- `TDPKG-10`: Total hours are derived from body schedule/activity evidence, not YAML.
- `TDPKG-11`: Teaching-plan hours and teaching-design activity hours are cross-checked when activity-hour evidence is declared.
- `TDPKG-12`: `first_teaching_day` derives school year and semester.
- `TDPKG-13`: Start/end dates are inferred from actual teaching-day hour consumption.
- `TDPKG-14`: The user-facing workflow does not ask teachers to mentally stitch other workflows together.
- `TDPKG-15`: Historical standalone entries remain external compatibility surfaces only. They are not package internals, resources, parity baselines, or future implementation direction.

## Teacher-Editable Markdown Contract

The accepted source of truth is one full Markdown document named `teaching-design-package-full.md` or a course-specific teaching-materials Markdown such as `某某某课教学资料.md`.

This Markdown must be readable and editable by a teacher without understanding package scripts. The assistant may generate the first draft from many source materials, but the teacher-facing structure must stay stable enough for direct review:

- one course identity area in frontmatter
- one `# 授课进度计划` body section
- one `# 教学设计方案` body section
- visible review markers for unresolved or teacher-choice-dependent facts
- source-derived facts placed near the schedule rows, activity text, resources, assessment details, or lesson design content they affect

The Markdown should merge source facts into a coherent course package. Do not preserve source-file fragmentation as separate mini-workflows.

## YAML / Frontmatter Boundary

Frontmatter is for stable facts a teacher can verify directly:

- `course_name`
- `major_name`
- `course_attribute`
- `textbook_name`
- `class_name`
- `teachers`
- `first_teaching_day`

Do not ask the teacher to maintain derived YAML values such as:

- total hours
- date ranges
- start dates
- end dates
- school year
- semester
- term labels
- output manifests
- output readiness
- validation flags
- renderer diagnostics
- internal calendar state

Those values are derived from the Markdown body, script configuration, or validation output. If a derived value is missing or inconsistent, fix the body evidence or mark the Markdown non-final instead of inventing YAML state.

The script rejects frontmatter keys that try to own derived or internal state, including `total_hours`, `school_year`, `semester`, `start_date`, `end_date`, `date_range`, `outputs`, `validation`, `status`, `manifest`, `output_readiness`, `final_ready`, and internal calendar/status fields.

## Body Extraction Rules

The Markdown body is the authority for teaching content and schedule evidence.

Use body content for:

- teaching schedule rows and hour-bearing activity lines
- learning tasks, stages, and lesson/activity structure
- resources, tools, equipment, worksheets, textbooks, and school-specific materials
- assessment rules, process evaluation, result evaluation, and evidence requirements
- teaching-design analysis, objectives, content, student analysis, methods, and activity steps
- review markers and source-derived evidence

The package model extracts schedule rows, activity hours, resources, teaching-design body, review markers, and source-derived facts from the body before validation/rendering. Body evidence should be used before asking the teacher for YAML-like facts.

## Source-Material Orchestration

When the teacher provides many materials, normalize them into one course package:

1. Read available text from course standards, lesson topics, schedule sheets, activity descriptions, textbooks, assessment notes, school format rules, and teacher notes.
2. Identify duplicate course facts and merge them into one canonical value when sources agree.
3. Detect conflicts in course identity, class/teacher facts, dates, hours, task order, resources, assessment requirements, and format constraints.
4. Ask targeted clarification questions only for blockers, conflicts, uncertainty, and teacher choices that affect the credibility of the full Markdown.
5. Group questions by topic: course identity, class/teacher facts, schedule/time evidence, lesson/activity structure, resources, assessment, school-specific format constraints, and unresolved review markers.
6. When a fact is optional or safe to defer, write a visible review marker in the Markdown body instead of blocking the whole workflow.

Raw OCR and arbitrary binary document extraction are future scope unless the runtime already has usable source text. This skill defines the organization contract, not a mandatory document-extraction engine.

## Review Markers

Review markers are teacher-facing, editable notes in the Markdown body. Use them for:

- missing facts that do not block a credible draft
- conflicts awaiting teacher choice
- uncertain dates, hours, or activity placement
- school-specific wording that needs local confirmation
- optional resource or assessment additions

Blocking markers must be resolved before the Markdown is treated as finalized. Non-blocking markers may remain only if the output is clearly non-final or review-needed.

## Package-Owned Data Model

After Markdown finalization, `scripts/teaching-design-package.sh model` parses the unified Markdown into one JSON model. The model owns:

- `metadata`: course, major, attribute, textbook, class, teachers, teacher display name, first teaching day.
- `schedule.tasks[]`: learning task title, stages, rows, row hours, row date-consumption evidence, task total hours, task date range.
- `modules.registry[]`: package-owned module metadata for `teaching-plan` and `teaching-design`, including display name, order, hidden Markdown path, hidden Typst path, and future PDF metadata.
- `modules.items[]`: module frontmatter generated from unified YAML and the shared scheduling model.
- `scheduling`: the single calendar-backed scheduling model consumed by all modules.
- `teaching_design`: original teaching-design Markdown content plus structured
  learning-task, stage, activity, and evaluation records aligned to
  `schedule.tasks[]`.
- `resources`: resource snippets extracted from the teaching-design section.
- `derived`: total hours, daily-hour default, school year, semester, term label, start/end dates, package date range.
- `review_markers`: unresolved package-level review items.
- `output_readiness`: Typst/PDF/final status booleans.

The model is package-owned. It must not encode external compatibility paths as its normal execution contract.

## Module Registry

Phase 33 introduces a package-owned module registry. Phase 34 migrates the
`teaching-plan` formal renderer into package internals. Phase 35 migrates the
`teaching-design` formal renderer into package internals. The current registered
modules are:

| id | Display name | Order | Hidden Markdown | Hidden Typst |
|----|--------------|-------|-----------------|--------------|
| `teaching-plan` | `授课进度计划表` | 1 | `.teaching-design-package/work/teaching-plan.md` | `.teaching-design-package/work/teaching-plan.typ` |
| `teaching-design` | `教学设计方案` | 2 | `.teaching-design-package/work/teaching-design.md` | `.teaching-design-package/work/teaching-design.typ` |

Registry order is the orchestration order and the future PDF merge order. New modules should be added by extending registry metadata and module generation code rather than by creating a second source-of-truth Markdown workflow.

The hidden module Markdown files are package internals. They are generated from the finalized unified Markdown and shared scheduling model, then stored under `.teaching-design-package/work/`. They are not teacher-maintained source files and must not appear in the successful public output root.

The hidden `teaching-plan.typ` is now a package-owned formal `授课进度计划表`
renderer output. It uses the migrated official `jiaoan-jihua` five-column table
surface, including the title block, course information grid, fixed columns
`(3.15cm, 8.51cm, 1.12cm, 1.29cm, 1.27cm)`, learning-task total rows, stage
rowspans, row week/weekday/hour cells, and signature grid. The renderer reads the
shared package model and scheduling evidence; it does not invoke the historical
standalone `jiaoan-jihua` skill or read sibling skill calendars at runtime.

The hidden `teaching-design.typ` is now a package-owned formal `教学设计方案`
renderer output. It uses the migrated `jiaoan-shicao` formal surface, including
cover metadata, `学习任务分析`, landscape `教学活动设计` tables, `学业评价`, task
hours, task date ranges, course `use_time`, total hours, teacher, class, and
textbook fields. The renderer reads the shared package model and scheduling
evidence; it does not invoke the historical standalone `jiaoan-shicao` skill or
read sibling skill calendars at runtime.

## Scheduling Rules

Phase 33 and later use a real package-owned teaching calendar:

- The active calendar resource is `skills/teaching-design-package/references/calendar.json`.
- `calendar.json` must be inside the `teaching-design-package` skill folder so a standalone copy of that folder can still derive schedule facts.
- The hidden model records `calendar.policy: "skill_local_calendar"` and the SHA-256 hash of the calendar file.
- `first_teaching_day` is required and must exist in `calendar.json`.
- `DEFAULT_DAILY_HOURS=8` unless a later package-owned configuration surface changes it.
- Each `授课进度计划` row ending in `-N` contributes `N` hours.
- Rows consume hours in source order, using only entries from `calendar.json`.
- Calendar exhaustion, malformed rows, non-positive hours, invalid calendar JSON, or a missing first teaching day is a hard failure.
- Natural-day sequential scheduling is not valid for Phase 33+ package scheduling. The renderer must not extrapolate with ordinary calendar-day increments when `calendar.json` does not contain enough teaching dates.
- Term weeks are derived from the first date in `calendar.json`, not ISO week numbers.
- Spring dates infer previous-year/current-year second semester; autumn dates infer current-year/next-year first semester unless a later package calendar explicitly carries term metadata.
- The `teaching-design` module reads dates, total hours, task hours, activity
  hours, and `use_time` from the shared scheduling model. It does not recompute
  date ranges, weeks, weekdays, task hours, or activity hours independently.
  Teacher-authored `课时：xH`, `##### xH`, or task date ranges are verification
  inputs only. When present, they must match `schedule.tasks[].total_hours`,
  `schedule.tasks[].stages[].rows[].hours`, and `schedule.tasks[].date_range`.

The `teaching-plan` formal renderer also reads term labels, title week ranges,
row weeks, row weekdays, row hours, task totals, and course totals from the same
shared scheduling model. It must not recalculate calendar consumption inside the
renderer.

For `TDPKG-VAL-01`, `# 授课进度计划` row suffixes are the only raw hour source.
The hidden model records `validation.total_hours_source:
"teaching_plan_rows"` and strict sum evidence for rows, stages, tasks, and the
course total.

For `TDPKG-VAL-02` through `TDPKG-VAL-04`, `# 授课进度计划` is also the
authority for the teaching-design module. The mapping key is structural:
`learning_task + learning_stage + activity_order`. Normalized titles are used
only to diagnose whether the same structural position drifted; the renderer must
not reorder or fuzzy-match activities. The hidden model records
`validation.cross_module_evidence` with per-task, per-stage, and per-activity
source pointers, expected/actual titles, hours, date ranges, and validation
status.

Any mismatch is a hard failure. Covered mismatch classes include task count,
stage count, activity count, task title, stage title, activity title, task
`课时：xH`, activity `##### xH`, task date range, missing analysis block, missing
activity block, missing evaluation block, formal render failure, PDF compile
failure, and public-root leakage. Failure diagnostics stay hidden under
`.teaching-design-package/diagnostics.json`, `.teaching-design-package/status.json`,
and `.teaching-design-package/failure-diagnostics/`, with calendar path/hash,
model version, source Markdown, plan/design pointers, expected values, actual
values, and concise messages.

## Script Boundary

Script boundary rule: scripts consume finalized Markdown for strict validation, data-model generation, Typst/PDF rendering, status evidence, and diagnostics.

Scripts do not:

- ask the teacher clarification questions
- organize raw source materials into a course package
- replace teacher review/editing
- require the teacher to maintain derived YAML fields
- fall back to external compatibility entries as package internals

Script validation may reject Markdown or mark it non-final when body evidence is inconsistent, review markers remain blocking, or derived schedule facts cannot be computed safely.

## Public Delivery Directory And Hidden Diagnostics

The output root has two surfaces:

1. **Public delivery directory**: only final teacher-facing files.
2. **Hidden internal directory**: `.teaching-design-package/`, with stable subdirectories for `work`, `debug`, and `failure-diagnostics`.

Default successful `render-package --pdf` uses stable English filenames for the public 1+1+3 set:

- `teaching-design-package-full.md` for the unified Markdown. The user may provide a course-specific input filename such as `某某某课教学资料.md`; the delivery root still receives the stable public copy.
- `teaching-design-package.typ` for the unified Typst.
- `teaching-design-package.pdf` for the full package PDF.
- `teaching-plan.pdf` for the 授课进度计划 PDF.
- `teaching-design.pdf` for the 教学设计方案 PDF.

Chinese teacher-facing names map to these stable script names:

| Teacher-facing deliverable | Default script filename |
|----------------------------|-------------------------|
| `某某某课教学资料.md` | `teaching-design-package-full.md` |
| `某某某课教学资料.typ` | `teaching-design-package.typ` |
| `某某某课教学资料.pdf` | `teaching-design-package.pdf` |
| `授课进度计划.pdf` | `teaching-plan.pdf` |
| `教学设计方案.pdf` | `teaching-design.pdf` |

Internal evidence is never a successful public-root file:

- `.teaching-design-package/model.json`
- `.teaching-design-package/status.json`
- `.teaching-design-package/work/` for split Typst and temporary render files
- `.teaching-design-package/debug/` for stderr logs
- `.teaching-design-package/failure-diagnostics/` for non-final status snapshots and failure evidence

Root-level status files, manifests, stderr logs, model JSON, split Typst, temporary state, and failure diagnostics indicate a bug in the delivery boundary.

## Rendering Rules

`render-package` performs these steps:

1. Copy the unified Markdown into the output directory as the human-readable source artifact.
2. Write hidden diagnostics under `.teaching-design-package/`.
3. Generate hidden module Markdown under `.teaching-design-package/work/`.
4. Generate formal hidden `teaching-plan.typ` from the package model and shared scheduling model.
5. Generate formal hidden `teaching-design.typ` from the package model and shared scheduling model.
6. Generate `teaching-design-package.typ` from the package model.
7. Write `.teaching-design-package/status.json`.
8. If `--pdf` is present, attempt package-owned PDF generation and record actual status.

Typst-only rendering is the default. PDF status values are honest:

- `not_run`: PDF was not requested.
- `missing_compiler_or_failed`: local compiler is missing or failed.
- `passed`: an explicit compile ran and the expected file exists.

`render-package --pdf` cannot report final success or exit 0 as a final delivery unless `teaching-design-package.pdf`, `teaching-plan.pdf`, and `teaching-design.pdf` all exist and are non-empty. If any PDF is missing or empty, the command exits non-zero, writes hidden status/failure diagnostics, and leaves enough evidence under `.teaching-design-package/` to troubleshoot without making the public root look complete.

Phase 34 migrates the formal `jiaoan-jihua` teaching-plan table rules into the
package-owned renderer. Phase 35 migrates the formal `jiaoan-shicao`
teaching-design rules into the package-owned renderer and adds strict
cross-module validation. Historical standalone skills remain external
compatibility surfaces and fixture oracles, not package runtime dependencies.
Phase 35 does not perform final public course-name-prefixed delivery and does
not finalize PDF merge semantics; that remains Phase 36 scope.
semantics. Those remain Phase 35 and Phase 36 scopes.

## Public Output Direction

The target delivery direction remains 1+1+3:

- one unified Markdown
- one unified Typst
- three PDFs: full package, teaching-plan, teaching-design/lesson-plan

Successful public roots must not contain status, manifest, stderr log, model JSON, split Typst, or temporary diagnostic files.

## Standalone Boundary

A valid standalone verification copies only the `teaching-design-package` skill folder into a fresh skill root. From inside that copied folder, run commands only after a full Markdown exists:

```text
scripts/teaching-design-package.sh example --output <tmp>/teaching-design-package-full.md
scripts/teaching-design-package.sh render-package --input <tmp>/teaching-design-package-full.md --out-dir <tmp>/out
```

This verification must succeed without repo sibling paths and without hidden external skill installation. Generated stdout, stderr, and output files must not leak the original repository path.

## External Compatibility Boundary

Historical standalone entries in the repository are allowed to remain available outside this package. Package documentation may mention them only generically as external compatibility surfaces. They are not:

- package internals
- package resources
- normal-path dependencies
- parity baselines
- future implementation direction

Do not add package docs or scripts that instruct users to install, invoke, wrap, embed, mirror, or mentally stitch external compatibility entries for normal package use.

## Runtime Portability

Canonical instructions describe files, contracts, command behavior, and verification. Runtime-private details belong in `SKILL.md` adapter notes. OpenClaw and Hermes Agent coverage must explicitly mention skill-folder discovery, support-file availability, script execution permissions, sandbox/allowlist checks, and fallback behavior.

## Verification Detail

```bash
bash -n scripts/teaching-design-package.sh

scripts/teaching-design-package.sh model \
  --input <finalized-markdown>

scripts/teaching-design-package.sh render-package \
  --input <finalized-markdown> \
  --out-dir /tmp/teaching-design-package-out
```

Expected results:

- the model command emits JSON with package-owned module and strict sum evidence
- the render command writes the public 1+1+3 files when `--pdf` succeeds
- diagnostics, status, split Typst, and stderr logs stay under `.teaching-design-package/`
- no normal-path output contains repo sibling paths
