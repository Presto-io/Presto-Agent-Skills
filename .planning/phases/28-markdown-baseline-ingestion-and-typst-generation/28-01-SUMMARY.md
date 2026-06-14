---
phase: 28-markdown-baseline-ingestion-and-typst-generation
plan: 01
subsystem: teaching-design-package
tags: [markdown, typst, baseline-ingestion, scheduling, jiaoan]

requires:
  - phase: 27-official-activity-table-width-alignment
    provides: current jiaoan-shicao renderer behavior and integrated-package date/table regression baseline
provides:
  - Baseline-mode validation for `# 授课进度计划` and `# 教学设计方案`
  - Markdown-derived `jiaoan-jihua-full.md` and `jiaoan-shicao-full.md` handoffs
  - Derived total/task/activity hours, task date ranges, and inferred term metadata
  - `teaching-design-package.typ` generation from package Markdown with manifest provenance
  - Phase 29 PDF slots with honest non-passed statuses
affects: [phase-29, teaching-design-package, jiaoan-jihua, jiaoan-shicao]

tech-stack:
  added: []
  patterns: [baseline heading slicer, generated handoff provenance, honest PDF slot status]

key-files:
  created:
    - .planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-VERIFICATION.md
  modified:
    - skills/teaching-design-package/scripts/teaching-design-package.sh
    - skills/teaching-design-package/SKILL.md
    - skills/teaching-design-package/references/format-and-orchestration.md

key-decisions:
  - "Phase 28 adapts renderer ingestion around the committed baseline Markdown instead of changing the teacher-facing reference file."
  - "Derived scheduling facts stay in generated handoffs, Typst comments, and manifest provenance, not package YAML."
  - "Phase 29 PDF files remain explicit slots with non-passed status until real PDF commands create files."

patterns-established:
  - "Baseline mode validates top-level Chinese anchors and rejects forbidden package YAML defaults."
  - "Package scripts compose existing standalone jiaoan renderers while preserving their public command surfaces."

requirements-completed: [TDBR-01, TDBR-02, TDBR-03, TDBR-04, TDBR-05, TDBR-12, TDBR-13, TDBR-14, TDBR-15, TDBR-16, TDBR-17]

duration: 24min
completed: 2026-06-14T19:52:47Z
---

# Phase 28 Plan 01: Markdown Baseline Ingestion and Typst Generation Summary

**Teacher-facing package Markdown now drives generated jiaoan handoffs, derived scheduling evidence, and package Typst without modifying the baseline reference.**

## Performance

- **Duration:** 24 min
- **Started:** 2026-06-14T19:28:56Z
- **Completed:** 2026-06-14T19:52:47Z
- **Tasks:** 6
- **Files modified:** 5

## Accomplishments

- Added baseline-mode validation for `# 授课进度计划` and `# 教学设计方案`, including negative checks for missing anchors and forbidden package YAML fields.
- Replaced package scaffold copies with baseline slicing that generates `jiaoan-jihua-full.md` and `jiaoan-shicao-full.md`, maps `teachers` to `teacher_name`, and derives `160H`, `40H/60H/60H`, the three expected date ranges, and `2025-2026学年第二学期`.
- Extended `render-package` to run split Typst generation and produce `teaching-design-package.typ` with Markdown provenance while keeping Phase 29 PDFs as `not_run` slots.

## Task Commits

1. **Task 1: Record baseline shape and reproduce validator gap** - `f18fb69`
2. **Tasks 2-4: Baseline validation, handoff slicing, package Typst generation** - `b8d6ec8`
3. **Task 5: Document baseline contract and Phase 29 slots** - `e024e3b`
4. **Task 6: Record final black-box verification evidence** - `817bbfd`

## Files Created/Modified

- `.planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-VERIFICATION.md` - pre-fix gap, final black-box command evidence, baseline hash/diff proof, and requirement traceability.
- `skills/teaching-design-package/scripts/teaching-design-package.sh` - baseline parser, derived scheduling model, generated handoffs, package Typst output, and manifest provenance.
- `skills/teaching-design-package/SKILL.md` - concise v1.13 baseline-mode workflow and safety notes.
- `skills/teaching-design-package/references/format-and-orchestration.md` - detailed v1.13 baseline contract, derived data rules, and Phase 29 PDF handoff boundaries.

## Decisions Made

- Used an embedded Node parser inside the existing shell script for robust Markdown/YAML slicing and JSON provenance, without adding a package dependency.
- Kept `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` and `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` unchanged; package render calls them with `LC_ALL=C` to avoid macOS awk Chinese string comparison issues.
- Treated `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf` as Phase 29 slots with `not_run` status in Phase 28.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed macOS awk locale behavior during package split rendering**
- **Found during:** Task 4
- **Issue:** The standalone `jiaoan-shicao` renderer miscounted Chinese headings under the default macOS awk locale, causing split render failure.
- **Fix:** Package-level calls to existing standalone renderers now set `LC_ALL=C`; standalone scripts and public commands were not modified.
- **Files modified:** `skills/teaching-design-package/scripts/teaching-design-package.sh`
- **Verification:** `render-split` and `render-package` both produced `teaching-plan.typ`, `lesson-plans.typ`, and `teaching-design-package.typ`.
- **Committed in:** `b8d6ec8`

**Total deviations:** 1 auto-fixed blocking issue.
**Impact on plan:** Required for planned split Typst generation; no scope expansion and no standalone public contract change.

## Known Stubs

None blocking. `not_run` PDF statuses are intentional Phase 29 handoff slots, not missing Phase 28 functionality.

## Issues Encountered

- Pre-fix `plan-split` rejected the baseline because old validation required `## 课程与整包元数据`; final validator now accepts the corrected baseline and fails with specific anchor errors when either top-level section is missing.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 29 can consume the generated Markdown handoffs, split Typst files, package Typst, and manifest provenance to implement the three PDF outputs and standalone parity checks. Baseline hash evidence proves `skills/teaching-design-package/templates/teaching-design-package-full.md` was not modified.

## Self-Check: PASSED

- Created file exists: `.planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-VERIFICATION.md`
- Commit hashes found: `f18fb69`, `b8d6ec8`, `e024e3b`, `817bbfd`
- Baseline diff check passed: `git diff -- skills/teaching-design-package/templates/teaching-design-package-full.md --exit-code`

---
*Phase: 28-markdown-baseline-ingestion-and-typst-generation*
*Completed: 2026-06-14T19:52:47Z*
