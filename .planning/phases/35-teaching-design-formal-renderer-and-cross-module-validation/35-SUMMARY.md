---
phase: 35-teaching-design-formal-renderer-and-cross-module-validation
plan: 01
subsystem: teaching-design-package
tags: [formal-renderer, teaching-design, typst, cross-module-validation, scheduling-model]
requires:
  - phase: 34
    provides: package-owned teaching-plan formal renderer and strict row-hour evidence
provides:
  - package-owned formal teaching-design Typst renderer
  - real teaching-design PDF generation through render-package --pdf
  - strict task/stage/activity/hour/date cross-module validation
  - hidden mismatch diagnostics for TDPKG-VAL-02 through TDPKG-VAL-04
  - legacy jiaoan-shicao acceptable-equivalence evidence
affects: [phase-36, teaching-design-package, jiaoan-shicao-compatibility]
tech-stack:
  added: [node-helper, typst-0.14.2-verification]
  patterns: [package-owned-formal-renderer, structural-cross-module-validation, hidden-failure-diagnostics]
key-files:
  created:
    - skills/teaching-design-package/scripts/teaching-design-renderer.js
    - .planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/35-VERIFICATION.md
  modified:
    - skills/teaching-design-package/scripts/teaching-design-package.sh
    - skills/teaching-design-package/scripts/package-model.js
    - skills/teaching-design-package/templates/teaching-design-package-full.md
    - skills/teaching-design-package/references/format-and-orchestration.md
key-decisions:
  - "Use structural task/stage/activity order as the mapping key; normalized titles are diagnostics only and do not reorder content."
  - "Treat raw legacy jiaoan-shicao fixture drift as hard-fail evidence, then prove acceptable equivalence with schedule-aligned fixture input."
  - "Keep legacy skills/jiaoan-shicao unchanged and outside package runtime dependencies."
patterns-established:
  - "Formal teaching-design renderer consumes model.teaching_design.tasks and shared scheduling evidence only."
  - "Cross-module validation errors use mismatch classes plus plan/design source pointers in hidden diagnostics."
requirements-completed: [TDPKG-LEGACY-02, TDPKG-VAL-02, TDPKG-VAL-03, TDPKG-VAL-04]
duration: 42min
completed: 2026-06-15
---

# Phase 35 Plan 01: Teaching Design Formal Renderer and Cross-Module Validation Summary

**Package-owned 教学设计方案 formal renderer with strict task/stage/activity validation against 授课进度计划**

## Performance

- **Duration:** 42 min
- **Started:** 2026-06-15T07:54:59Z
- **Completed:** 2026-06-15T08:37:00Z
- **Tasks:** 7
- **Files modified:** 7

## Accomplishments

- Added `teaching-design-renderer.js`, a package-owned renderer that emits formal `教学设计方案` Typst with cover metadata, learning-task analysis, landscape activity tables, evaluation pages, and legacy width markers.
- Extended `package-model.js` from total-only design checks to per-task, per-stage, and per-activity mapping evidence against `schedule.tasks[]`.
- Replaced the `teaching-design.typ` placeholder route with formal hidden Typst generation and real `teaching-design.pdf` compilation.
- Added hidden hard-fail diagnostics for task count, stage count, activity count, title, hour, and date mismatches.
- Verified standalone-copy rendering and confirmed `skills/jiaoan-shicao/` remained unchanged.

## Task Commits

1. **Tasks 1-4: Formal renderer, cross-module model, diagnostics, and PDF routing** - `6feef9d` (feat)
2. **Task 7: Package docs and verification evidence** - `87d4b05` (docs)
3. **Task 1 cleanup: Remove obsolete placeholder helper** - `61f18f2` (refactor)

## Files Created/Modified

- `skills/teaching-design-package/scripts/teaching-design-renderer.js` - Emits formal teaching-design Typst from the package model and shared schedule evidence.
- `skills/teaching-design-package/scripts/package-model.js` - Parses teaching-design tasks/stages/activities/evaluations and enforces structural cross-module validation.
- `skills/teaching-design-package/scripts/teaching-design-package.sh` - Routes hidden `teaching-design.typ` through the formal renderer, records status/diagnostics, and compiles `teaching-design.pdf`.
- `skills/teaching-design-package/templates/teaching-design-package-full.md` - Aligns example teaching-design titles with schedule row authority so strict validation passes.
- `skills/teaching-design-package/references/format-and-orchestration.md` - Documents Phase 35 formal renderer ownership and hard-fail validation semantics.
- `.planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/35-VERIFICATION.md` - Records exact verification commands and observed results.

## Decisions Made

- Structural position is the source of truth for mapping. Title normalization is intentionally narrow and diagnostic only.
- Existing raw `test/1.10` teaching-design fixture is preserved as read-only evidence, but it is not directly accepted by Phase 35 because its titles drift from the schedule. The verifier uses a schedule-aligned equivalent fixture for renderer equivalence.
- The old `jiaoan-shicao` skill was not modified even though its `--expected-typ` path currently returns `1`; ordinary `example` and `render` still run.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Aligned package template titles with schedule authority**
- **Found during:** Task 2 structured mapping
- **Issue:** The package template had teaching-design activity titles that shortened schedule row titles, for example missing `万用表的使用方法回顾` and `完成通电试验过程`.
- **Fix:** Updated only `skills/teaching-design-package/templates/teaching-design-package-full.md` so task and activity titles match `# 授课进度计划` exactly.
- **Verification:** Positive model check passed with 3 tasks, 19 stages, 54 activities, and negative title fixtures still fail.
- **Committed in:** `6feef9d`

**2. [Rule 1 - Bug] Removed obsolete pre-formal placeholder helper**
- **Found during:** Stub scan before summary
- **Issue:** `write_placeholder_pdf_typst` remained as dead code and still contained Phase 33 placeholder strings.
- **Fix:** Deleted the unused helper so the package has no remaining teaching-design placeholder route.
- **Verification:** Shell syntax and render-package Typst generation passed; placeholder grep no longer finds runtime code.
- **Committed in:** `61f18f2`

**Total deviations:** 2 auto-fixed bugs.
**Impact on plan:** Both were necessary to satisfy strict Phase 35 correctness; no scope expansion beyond package-owned renderer and validation.

## Issues Encountered

- Raw `test/1.10/电气设备控制线路安装与调试教案.md` is not directly Phase 35-valid because titles drift from the schedule oracle. This is documented as acceptable equivalence evidence, not hidden.
- The unmodified legacy `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --expected-typ` exits `1` against the current oracle, while `example` and ordinary `render` still succeed. The plan forbids modifying `skills/jiaoan-shicao/`, so this remains documented evidence rather than an inline fix.

## Known Stubs

None. Stub scan found no active placeholder output after `61f18f2`.

## Threat Flags

None. This phase adds local Markdown/model/Typst/PDF generation only; it introduces no network endpoints, auth paths, or new trust-boundary persistence beyond existing output directories.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 36 can now enforce course-name-prefixed public `1 + 1 + N` delivery and final PDF merge semantics. Both registered modules have package-owned formal hidden Typst and real module PDF generation.

## Self-Check: PASSED

- Created files exist: `skills/teaching-design-package/scripts/teaching-design-renderer.js`, `35-VERIFICATION.md`, and `35-SUMMARY.md`.
- Commits `6feef9d`, `87d4b05`, and `61f18f2` exist in git history.
- Verification commands in `35-VERIFICATION.md` passed.
- `git diff --name-only -- skills/jiaoan-shicao` printed nothing.

---
*Phase: 35-teaching-design-formal-renderer-and-cross-module-validation*
*Completed: 2026-06-15*
