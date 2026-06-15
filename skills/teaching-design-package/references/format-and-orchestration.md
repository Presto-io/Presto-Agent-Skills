# Teaching Design Package Format and Orchestration

This reference defines the standalone package contract for `teaching-design-package`. The normal path is unified Markdown -> package-owned data model -> package-owned Typst/PDF rendering. The skill folder must remain usable when installed by itself.

## Requirement Traceability

- `TDPKG-01`: The package can be installed and used as one skill folder.
- `TDPKG-02`: Package capability is implemented through its own Markdown contract, data model, validation, Typst generation, and PDF status path.
- `TDPKG-03`: Runtime adapter notes cover Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent under the standalone boundary.
- `TDPKG-15`: Historical standalone entries remain external compatibility surfaces only. They are not package internals, resources, parity baselines, or future implementation direction.

## Unified Markdown Contract

The accepted input is a single Markdown document named `teaching-design-package-full.md` or a course-specific teaching-materials Markdown with the same shape.

Required frontmatter fields:

- `course_name`
- `major_name`
- `course_attribute`
- `textbook_name`
- `class_name`
- `teachers`
- `first_teaching_day`

Required body anchors:

- `# 授课进度计划`
- `# 教学设计方案`

The package Markdown must not ask teachers to maintain derived fields such as total hours, school year, semester, output configuration, validation configuration, or calendar internals. Those facts are derived by the package model from source rows and first teaching day.

## Package-Owned Data Model

`scripts/teaching-design-package.sh model` parses the unified Markdown into one JSON model. The model owns:

- `metadata`: course, major, attribute, textbook, class, teachers, teacher display name, first teaching day.
- `schedule.tasks[]`: learning task title, stages, rows, row hours, row date-consumption evidence, task total hours, task date range.
- `teaching_design`: original teaching-design Markdown content plus block counts.
- `resources`: resource snippets extracted from the teaching-design section.
- `derived`: total hours, daily-hour default, school year, semester, term label, start/end dates, package date range.
- `review_markers`: unresolved package-level review items.
- `output_readiness`: Typst/PDF/final status booleans.

The model is package-owned. It must not encode old split workflow names, old internal directory names, or external skill paths as its normal execution contract.

## Scheduling Rules

Phase 30 uses a deterministic package-local default:

- `first_teaching_day` starts the hour-consumption sequence.
- `DEFAULT_DAILY_HOURS=8` unless a later phase exposes a package-owned configuration surface.
- Each `授课进度计划` row ending in `-N` contributes `N` hours.
- Rows consume hours in source order.
- Dates advance by one calendar day whenever the day budget is exhausted.
- Spring dates infer previous-year/current-year second semester; autumn dates infer current-year/next-year first semester.

This is sufficient for the standalone model/render path. Later scheduling work can refine holidays and makeup days without depending on external sibling folders.

## Rendering Rules

`render-package` performs these steps:

1. Copy the unified Markdown into the output directory as the human-readable source artifact.
2. Write hidden diagnostics under `.teaching-design-package/`.
3. Generate `teaching-design-package.typ` from the package model.
4. Write `teaching-design-package-status.json`.
5. If `--pdf` is present, attempt package-owned PDF generation and record actual status.

Typst-only rendering is the default. PDF status values are honest:

- `not_run`: PDF was not requested.
- `missing_compiler_or_failed`: local compiler is missing or failed.
- `passed`: an explicit compile ran and the expected file exists.

Phase 30 may generate provisional PDF surfaces to prove the package-owned path. Full official layout, exact successful 1+1+3 delivery cleaning, and final delivery directory enforcement remain Phase 32 work.

## Public Output Direction

The target delivery direction remains 1+1+3:

- one unified Markdown
- one unified Typst
- three PDFs: full package, teaching-plan, teaching-design/lesson-plan

During Phase 30, `render-package` must at least create the unified Markdown copy, unified Typst, hidden model, and status JSON. If PDF compilation is unavailable, the status JSON must say so without falling back to external compatibility entries.

## Standalone Boundary

A valid standalone verification copies only the `teaching-design-package` skill folder into a fresh skill root. From inside that copied folder, run:

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

Do not add package docs or scripts that instruct users to install, invoke, wrap, 内嵌打包, mirror, or mentally stitch external compatibility entries for normal package use.

## Runtime Portability

Canonical instructions describe files, contracts, command behavior, and verification. Runtime-private details belong in `SKILL.md` adapter notes. OpenClaw and Hermes Agent coverage must explicitly mention skill-folder discovery, support-file availability, script execution permissions, sandbox/allowlist checks, and fallback behavior.

## Verification Detail

```bash
bash -n scripts/teaching-design-package.sh

scripts/teaching-design-package.sh example \
  --output /tmp/teaching-design-package-full.md

scripts/teaching-design-package.sh model \
  --input /tmp/teaching-design-package-full.md

scripts/teaching-design-package.sh render-package \
  --input /tmp/teaching-design-package-full.md \
  --out-dir /tmp/teaching-design-package-out
```

Expected results:

- the example command writes unified Markdown
- the model command emits JSON with `model_version: phase30.package-owned.v1`
- the render command writes `teaching-design-package.typ`
- diagnostics stay under `.teaching-design-package/`
- no normal-path output contains repo sibling paths
