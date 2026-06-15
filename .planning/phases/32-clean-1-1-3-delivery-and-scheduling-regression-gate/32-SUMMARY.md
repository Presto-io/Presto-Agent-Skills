---
phase: 32
plan: 01
subsystem: skill-delivery
tags: [teaching-design-package, delivery, scheduling, regression]
requires:
  - phase: 31
    provides: Teacher-facing unified Markdown workflow
provides:
  - Clean 1+1+3 public delivery contract
  - Hidden diagnostics/status/model boundary
  - Derived scheduling validation gate
  - Standalone-copy regression evidence
affects: [teaching-design-package, v1.14]
tech-stack:
  added: []
  patterns: [hidden diagnostics, clean delivery root, derived scheduling validation]
key-files:
  created:
    - .planning/phases/32-clean-1-1-3-delivery-and-scheduling-regression-gate/32-VERIFICATION.md
  modified:
    - skills/teaching-design-package/SKILL.md
    - skills/teaching-design-package/references/format-and-orchestration.md
    - skills/teaching-design-package/scripts/teaching-design-package.sh
key-decisions:
  - "Successful public delivery roots contain exactly the stable English 1+1+3 filenames."
  - "Status, model, diagnostics, stderr logs, split Typst, and failure evidence stay under .teaching-design-package/."
  - "Total hours, school year, semester, start date, end date, and date range are derived from body evidence and first_teaching_day."
requirements-completed: [TDPKG-07, TDPKG-08, TDPKG-09, TDPKG-10, TDPKG-11, TDPKG-12, TDPKG-13]
duration: current session
completed: 2026-06-15
---

# Phase 32 Plan 01: Clean 1+1+3 Delivery and Scheduling Regression Gate Summary

**`teaching-design-package` now enforces a clean public 1+1+3 delivery root and hidden diagnostics boundary, with derived scheduling validation.**

## Performance

- **Duration:** current session
- **Started:** 2026-06-15T02:19:12Z
- **Completed:** 2026-06-15T02:29:11Z
- **Tasks:** 6/6
- **Files modified:** 7

## Accomplishments

- Updated the canonical skill entry so successful script delivery lists only one Markdown, one Typst, and three PDFs.
- Added a reference section that separates the public delivery directory from hidden `.teaching-design-package/` work, debug, and failure diagnostics.
- Changed `render-package --pdf` so status, model JSON, stderr logs, split Typst files, diagnostics, and failure snapshots stay hidden.
- Enforced `render-package --pdf` success only when all three PDF deliverables exist and are non-empty.
- Rejected derived/internal frontmatter fields including total hours, school year, semester, start/end/date range, validation, manifest/status, and readiness fields.
- Derived total hours, school year, semester, start date, end date, date range, and calendar policy from body schedule evidence and `first_teaching_day`.
- Added teaching-design activity-hour cross-check behavior when activity-hour evidence is declared.
- Verified everything from a standalone copy containing only `skills/teaching-design-package/`.

## Task Commits

1. **Tasks 1-6: clean delivery and scheduling gate** - pending in execution commit.

## Files Created/Modified

- `skills/teaching-design-package/SKILL.md` - Clean 1+1+3 outputs and hidden diagnostics guidance.
- `skills/teaching-design-package/references/format-and-orchestration.md` - Public/hidden output contract, scheduling validation, and failure semantics.
- `skills/teaching-design-package/scripts/teaching-design-package.sh` - Hidden status/model/diagnostics, strict PDF success, derived field rejection, activity-hour cross-check.
- `.planning/phases/32-clean-1-1-3-delivery-and-scheduling-regression-gate/32-VERIFICATION.md` - Verification evidence.
- `.planning/phases/32-clean-1-1-3-delivery-and-scheduling-regression-gate/32-SUMMARY.md` - This summary.
- `.planning/REQUIREMENTS.md` - Marks TDPKG-07 through TDPKG-13 complete.
- `.planning/STATE.md` and `.planning/ROADMAP.md` - Phase execution state and progress.

## Decisions Made

- The script keeps stable English public filenames by default: `teaching-design-package-full.md`, `teaching-design-package.typ`, `teaching-design-package.pdf`, `teaching-plan.pdf`, and `teaching-design.pdf`.
- Course-specific Chinese input filenames remain accepted source Markdown names, but the default delivery root uses the stable five-file mapping.
- The default calendar policy is recorded as `sequential_teaching_days_default`.
- Teaching-design activity hours are optional body evidence; if declared, they must match the teaching-plan total.

## Deviations from Plan

- The required GNU `find -printf` assertion is not supported by the macOS `find` available in this environment, and GNU `gfind` is not installed. The command was attempted and recorded as unsupported; the same file-list assertion was performed with a portable `find ... -exec basename` equivalent and passed.

## Issues Encountered

None blocking.

## User Setup Required

None.

## Verification

See `32-VERIFICATION.md`. Required checks passed:

- shell syntax
- standalone copy only `teaching-design-package`
- standalone example and `render-package --pdf`
- exact public five-file root
- root pollution scan
- hidden model/status/diagnostics checks
- derived scheduling JSON assertions
- derived frontmatter rejection
- autumn semester inference
- activity-hour mismatch rejection
- old precise name scan
- legacy dependency scan
- legacy skill diff empty
- git diff whitespace checks

## Next Phase Readiness

Phase 32 is complete for execute-phase scope. No audit, complete, or push workflow was run.

## Self-Check: PASSED

All Phase 32 tasks, acceptance criteria, and required verification behaviors were completed.
