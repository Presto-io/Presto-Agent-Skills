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
- `TDPKG-07`: A successful public delivery directory contains only course-name-prefixed `1 + 1 + N` files: one unified Markdown, one merged package PDF, and one PDF per registered module.
- `TDPKG-08`: Successful public delivery directories do not contain `.typ`, status, manifest, stderr log, model JSON, diagnostics JSON, calendar JSON, module Markdown/Typst, staging files, old English success filenames, or temporary state files.
- `TDPKG-09`: Package-owned diagnostics stay in an explicit diagnostic workdir or the owned `.work/<run-id>/evidence/` lifecycle and never become current.
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
- `modules.registry[]`: package-owned module metadata for `teaching-plan` and `teaching-design`, including display name, order, run-relative evidence Markdown/Typst paths, and PDF metadata.
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

| id | Display name | Order | Run-relative Markdown | Run-relative Typst |
|----|--------------|-------|-----------------|--------------|
| `teaching-plan` | `授课进度计划表` | 1 | `evidence/modules/teaching-plan.md` | `evidence/modules/teaching-plan.typ` |
| `teaching-design` | `教学设计方案` | 2 | `evidence/modules/teaching-design.md` | `evidence/modules/teaching-design.typ` |

Registry order is the orchestration order and the future PDF merge order. New modules should be added by extending registry metadata and module generation code rather than by creating a second source-of-truth Markdown workflow.

The module Markdown files are package internals. They are generated from the finalized unified Markdown and shared scheduling model under the current run evidence directory. They are not teacher-maintained source files and must not appear in the successful public output root.

The evidence-only `teaching-plan.typ` is a package-owned formal `授课进度计划表`
renderer output. It uses the migrated official `jiaoan-jihua` five-column table
surface, including the title block, course information grid, fixed columns
`(3.15cm, 8.51cm, 1.12cm, 1.29cm, 1.27cm)`, learning-task total rows, stage
rowspans, row week/weekday/hour cells, and signature grid. The renderer reads the
shared package model and scheduling evidence; it does not invoke the historical
standalone `jiaoan-jihua` skill or read sibling skill calendars at runtime.

The evidence-only `teaching-design.typ` is a package-owned formal `教学设计方案`
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
- The run-relative model records `calendar.policy: "skill_local_calendar"` and the SHA-256 hash of the calendar file.
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
The package model records `validation.total_hours_source:
"teaching_plan_rows"` and strict sum evidence for rows, stages, tasks, and the
course total.

For `TDPKG-VAL-02` through `TDPKG-VAL-04`, `# 授课进度计划` is also the
authority for the teaching-design module. The mapping key is structural:
`learning_task + learning_stage + activity_order`. Normalized titles are used
only to diagnose whether the same structural position drifted; the renderer must
not reorder or fuzzy-match activities. The package model records
`validation.cross_module_evidence` with per-task, per-stage, and per-activity
source pointers, expected/actual titles, hours, date ranges, and validation
status.

Any mismatch is a hard failure. Covered mismatch classes include task count,
stage count, activity count, task title, stage title, activity title, task
`课时：xH`, activity `##### xH`, task date range, missing analysis block, missing
activity block, missing evaluation block, formal render failure, PDF compile
failure, and final candidate validation failure. Final delivery diagnostics stay
under the owned `.work/<run-id>/evidence/` lifecycle and are removed after
handled failure; diagnostic commands write the same bounded evidence only to
their explicit `--out-dir`, with calendar path/hash, model version, source
Markdown, plan/design pointers, expected values, actual values, and concise messages.

## Script Boundary

Script boundary rule: scripts consume finalized Markdown for strict validation, data-model generation, Typst/PDF rendering, status evidence, and diagnostics.

Scripts do not:

- ask the teacher clarification questions
- organize raw source materials into a course package
- replace teacher review/editing
- require the teacher to maintain derived YAML fields
- fall back to external compatibility entries as package internals

Script validation may reject Markdown or mark it non-final when body evidence is inconsistent, review markers remain blocking, or derived schedule facts cannot be computed safely.

## Public Delivery Directory And Owned Work

The public delivery root contains only the exact model-derived current group and
the optional support directories `sources/`, `assets/`, `history/`, and `.work/`.
There is no persistent hidden diagnostic exception.

Default successful `render-package --pdf` uses course-name-prefixed public filenames. The current public contract is `1 + 1 + N`; N is the number of registered modules. Current N=2:

- `课程名教学资料.md` for the unified Markdown public copy.
- `课程名教学资料.pdf` for the full package PDF created by merging registered module PDFs.
- `课程名授课进度计划表.pdf` for the `teaching-plan` module PDF.
- `课程名教学设计方案.pdf` for the `teaching-design` module PDF.

For the default template, the public root contains exactly:

- `电气设备控制线路安装与调试教学资料.md`
- `电气设备控制线路安装与调试教学资料.pdf`
- `电气设备控制线路安装与调试授课进度计划表.pdf`
- `电气设备控制线路安装与调试教学设计方案.pdf`

The old English filenames `teaching-design-package-full.md`, `teaching-design-package.typ`, `teaching-design-package.pdf`, `teaching-plan.pdf`, and `teaching-design.pdf` are no longer successful public output names. English names may remain internal helper names, staging names, or compatibility command names, but they must not appear at the successful public root.

`public_delivery.expected_public_filenames` is the sole dynamic mutation
authority. The current value is one unified Markdown, one merged PDF, and one
PDF for each registry item. Model, status, diagnostics, module Markdown/Typst,
module PDFs before publication, merge plan/status/logs, and failure evidence live
under `.work/<run-id>/evidence/`; only the complete final set enters
`.work/<run-id>/candidate/`. The publisher creates `rollback/` only when needed.

Root-level `.typ`, status files, manifests, stderr logs, model JSON, diagnostics JSON, calendar JSON, module intermediates, staging files, old English success filenames, temporary state, and failure diagnostics indicate a bug in the delivery boundary.

## Rendering Rules

`render-package --pdf` performs these steps:

1. Create one owned `.work/<run-id>/{candidate,evidence}` without mutating current.
2. Write model, diagnostics, module Markdown/Typst and debug-only unified Typst to evidence.
3. Compile each registered module Typst to evidence and verify registry membership, order, regular/non-symlink type, non-empty bytes, and PDF header.
4. Merge module PDFs in registry order, record merge plan/status/log, and verify the merged PDF.
5. Copy only the model-derived exact `1 + 1 + N` set into candidate and pass final-ready validation.
6. Invoke the Node publisher once with `expected_public_filenames`; it holds root identity, acquires a same-root lock, rejects unknown/legacy/symlink/partial/ambiguous states, and compares exact path-set+bytes.
7. For identical bytes, preserve current inode/mtime and create no history. For changed bytes or course prefix, archive the one complete old group under `history/<max+1>/`, then replace the complete candidate.
8. Post-verify exact names and bytes, then remove this run, evidence, rollback, lock, and empty `.work`.

If more than one old course-prefix group exists, or a group is partial, the
publisher fails closed rather than choosing by mtime. Existing `001/003` yields
`004`; gaps are never reused. `sources/` and unrelated user entries are never
cleaned, moved, or inferred as current.

Typst-only rendering is the default. PDF status values are honest:

- `not_run`: PDF was not requested.
- `module_pdf_missing`: a registered module PDF was not produced before merge.
- `module_pdf_empty`: a registered module PDF exists but is empty.
- `merge_tool_unavailable`: no allowed merge tool was available.
- `merge_tool_failed`: the selected merge tool returned non-zero.
- `merged_pdf_empty`: the merge command returned but produced no non-empty output.
- `passed`: an explicit compile ran and the expected file exists.

`render-package --pdf` cannot report final success unless all registered module
PDFs and the merged PDF pass, review markers are empty, model validation has no
errors, the complete candidate matches `expected_public_filenames`, and the
publisher post-check passes. Generation, module, merge, final validation,
publication, handled `INT`, or handled `TERM` failure restores the prior current
and removes only this run/history reservation. The contract does not claim
SIGKILL, power-loss, or multi-path hard atomicity.

Allowed merge tools are selected by availability in this order:

1. `pdfunite`
2. `qpdf`
3. Python PyMuPDF fallback, recorded as `python_fitz`

`status.json` records `merge_tool`, `command_summary`, `merge_inputs`, module ids, display names, staging paths, public paths, source Typst paths, input byte sizes, output path, exit code, stderr log path, output byte size, and non-empty result. `final_ready` is true only when this merge status is `passed`.

Phase 34 migrates the formal `jiaoan-jihua` teaching-plan table rules into the
package-owned renderer. Phase 35 migrates the formal `jiaoan-shicao`
teaching-design rules into the package-owned renderer and adds strict
cross-module validation. Historical standalone skills remain external
compatibility surfaces and fixture oracles, not package runtime dependencies.
Phase 36 performs final public course-name-prefixed delivery and PDF merge
semantics. Historical standalone skills remain external compatibility surfaces
and are not runtime dependencies.

## Public Output Direction

The target delivery direction is course-name-prefixed `1 + 1 + N`:

- one unified Markdown
- one merged package PDF
- N registered module PDFs

Successful public roots must not contain `.typ`, status, manifest, stderr log, model JSON, diagnostics JSON, calendar JSON, module Markdown/Typst, staging files, old English success filenames, or temporary diagnostic files.

## Standalone Boundary

A valid standalone verification copies only the `teaching-design-package` skill folder into a fresh skill root. From inside that copied folder, run commands only after a full Markdown exists:

```text
scripts/teaching-design-package.sh example --output <tmp>/package.md
scripts/teaching-design-package.sh render-package --pdf --input <tmp>/package.md --out-dir <tmp>/out
```

This verification must succeed without repo sibling paths or external skill installation. The copied package must use its own `references/calendar.json`, produce exactly the course-name-prefixed public files, clean its owned `.work/<run-id>`, and avoid runtime references to sibling `jiaoan-jihua` or `jiaoan-shicao` skills.

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

All six runtimes install the whole skill folder and retain an explicit
`scripts/teaching-design-package.sh` fallback. Final delivery requires Bash,
Node.js, Typst, and one PDF merge path (`pdfunite`, `qpdf`, or Python PyMuPDF),
plus read access to finalized Markdown/template/reference files and execute/write
permission for the authorized delivery root and `.work`. OpenClaw and Hermes
Agent claims remain installation-time verified rather than assumed automatic discovery.

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
- the render command writes the public course-name-prefixed `1 + 1 + N` files when `--pdf` succeeds
- diagnostics, status, module Markdown/Typst, staging files, merge evidence, and stderr logs stay in the explicit diagnostic workdir or owned run evidence, never current
- successful, identical, and handled-failure final delivery leaves no legacy `.teaching-design-package/` and no current run under `.work/`
- no normal-path output contains repo sibling paths
