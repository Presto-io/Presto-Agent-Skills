---
phase: 33-module-registry-unified-extraction-and-scheduling-model
plan: 01
subsystem: teaching-design-package
tags: [module-registry, markdown-extraction, calendar-scheduling, diagnostics, typst]
requires:
  - phase: 32
    provides: clean 1+1+3 delivery boundary and hidden diagnostics layout
provides:
  - package-owned module registry for teaching-plan and teaching-design
  - unified Markdown parser with strict schedule-row extraction
  - skill-local calendar resource and shared scheduling model
  - hidden module Markdown and Typst intermediates under .teaching-design-package/work
  - Phase 33 verification evidence
affects: [phase-34, phase-35, phase-36, teaching-design-package]
tech-stack:
  added: [node-helper, skill-local-calendar-json]
  patterns: [package-owned-module-registry, shared-scheduling-model, hidden-module-workdir]
key-files:
  created:
    - skills/teaching-design-package/scripts/package-model.js
    - skills/teaching-design-package/references/calendar.json
    - .planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-VERIFICATION.md
  modified:
    - skills/teaching-design-package/scripts/teaching-design-package.sh
    - skills/teaching-design-package/references/format-and-orchestration.md
key-decisions:
  - "Use skill-local calendar.json as the only scheduling date source for Phase 33+ package scheduling."
  - "Keep formal legacy renderer migration out of Phase 33; hidden Typst is pre-formal module evidence only."
patterns-established:
  - "Module registry entries define id, display name, order, hidden Markdown, hidden Typst, and future PDF metadata."
  - "Both modules consume one shared scheduling object instead of recomputing dates or hours."
requirements-completed: [TDPKG-MOD-01, TDPKG-MOD-02, TDPKG-MOD-03, TDPKG-MOD-04, TDPKG-MOD-05, TDPKG-MOD-06, TDPKG-MOD-07, TDPKG-YAML-01, TDPKG-YAML-02, TDPKG-YAML-03, TDPKG-YAML-04, TDPKG-SCHED-01, TDPKG-SCHED-02, TDPKG-SCHED-03, TDPKG-SCHED-04, TDPKG-SCHED-05]
duration: 19min
completed: 2026-06-15
---

# Phase 33 Plan 01: Module Registry, Unified Extraction, and Scheduling Model Summary

**Package-owned module registry with skill-local calendar scheduling and hidden module Markdown/Typst intermediates**

## Performance

- **Duration:** 19 min
- **Started:** 2026-06-15T06:02:21Z
- **Completed:** 2026-06-15T06:21:48Z
- **Tasks:** 6
- **Files modified:** 6

## Accomplishments

- Replaced the inline natural-day model path with `scripts/package-model.js`, a package-owned parser/scheduler that reads unified Markdown plus `references/calendar.json`.
- Added the registered `teaching-plan` and `teaching-design` modules with stable hidden Markdown/Typst paths and shared scheduling-derived frontmatter.
- Generated hidden `.teaching-design-package/work/` module Markdown and Phase 33 pre-formal Typst while keeping public roots free of model/status/diagnostic/module files.
- Recorded verification for success paths, malformed schedule rows, forbidden derived YAML, missing first teaching day, standalone-copy calendar use, and legacy-skill non-modification.

## Task Commits

1. **Tasks 1-5: Module registry, extraction, scheduling, hidden artifacts, diagnostics** - `541b74d` (feat)
2. **Task 6: Reference docs, verification, and summary** - committed with plan metadata

## Files Created/Modified

- `skills/teaching-design-package/scripts/package-model.js` - Strict unified Markdown parser, module registry, skill-local calendar scheduler, YAML conversion, and classified diagnostics.
- `skills/teaching-design-package/references/calendar.json` - Package-owned teaching-date resource used by standalone copies.
- `skills/teaching-design-package/scripts/teaching-design-package.sh` - Routes model generation through the helper, writes hidden module Markdown/Typst, and records Phase 33 status/diagnostics.
- `skills/teaching-design-package/references/format-and-orchestration.md` - Documents module registry, calendar source, hidden module artifacts, and Phase 34-36 non-goals.
- `.planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-VERIFICATION.md` - Exact verification commands and observed results.

## Decisions Made

- Kept `calendar.json` under `skills/teaching-design-package/references/` so standalone copies do not depend on sibling legacy skill folders.
- Moved the larger model parser into `scripts/package-model.js` to keep the shell entry as command routing and artifact orchestration rather than a growing monolith.
- Treated module Typst as pre-formal internal evidence only; formal renderer parity remains Phase 34 and Phase 35 scope.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed row range assignment order**
- **Found during:** Task 2/3 verification
- **Issue:** The first implementation tried to summarize a row date range before assigning its `start_date` and `end_date`, causing a `TypeError`.
- **Fix:** Added row-level `applyRangeFromConsumption()` and used it before stage/task aggregation.
- **Files modified:** `skills/teaching-design-package/scripts/package-model.js`
- **Verification:** `model --input skills/teaching-design-package/templates/teaching-design-package-full.md` passed and produced `task:1/stage:1/row:1` scheduling evidence.
- **Committed in:** `541b74d`

**Total deviations:** 1 auto-fixed bug.
**Impact on plan:** Correctness fix only; no scope expansion.

## Issues Encountered

- The first patch attempt against the large Bash heredoc did not apply cleanly. I switched to a skill-local Node helper, which matches the plan's module-boundary intent and keeps the shell command surface stable.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 34 can migrate the `授课进度计划表` formal renderer using the hidden `teaching-plan.md`, `teaching-plan.typ`, module registry order, and shared scheduling model now produced in Phase 33.

## Self-Check: PASSED

- Created files exist: `scripts/package-model.js`, `references/calendar.json`, and `33-VERIFICATION.md`.
- Commit `541b74d` exists in git history.
- Verification commands in `33-VERIFICATION.md` passed.
- No `skills/jiaoan-jihua/` or `skills/jiaoan-shicao/` files were modified.

---
*Phase: 33-module-registry-unified-extraction-and-scheduling-model*
*Completed: 2026-06-15*
