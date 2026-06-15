---
phase: 31
plan: 01
subsystem: skill-workflow
tags: [teaching-design-package, teacher-workflow, markdown, validation]
requires:
  - phase: 30
    provides: Standalone package-owned contract boundary
provides:
  - Teacher-facing source-materials-to-Markdown workflow
  - Teacher-editable Markdown contract
  - Finalized-Markdown script boundary
affects: [teaching-design-package, v1.14]
tech-stack:
  added: []
  patterns: [teacher-editable Markdown, body-centered evidence, finalized-Markdown validation boundary]
key-files:
  created:
    - .planning/phases/31-teacher-facing-unified-markdown-workflow/31-VERIFICATION.md
  modified:
    - skills/teaching-design-package/SKILL.md
    - skills/teaching-design-package/references/format-and-orchestration.md
key-decisions:
  - "The canonical skill entry now starts from teacher source materials and clarification before any script command."
  - "The unified Markdown is the teacher-editable source of truth before rendering."
  - "Scripts are documented as finalized-Markdown validation and delivery tools only."
requirements-completed: [TDPKG-04, TDPKG-05, TDPKG-06, TDPKG-14]
duration: current session
completed: 2026-06-15
---

# Phase 31 Plan 01: Teacher-Facing Unified Markdown Workflow Summary

**`teaching-design-package` now reads as a teacher source-materials-to-full-Markdown workflow before it reads as a renderer.**

## Performance

- **Duration:** current session
- **Started:** 2026-06-15T01:30:17Z
- **Completed:** 2026-06-15T01:50:56Z
- **Tasks:** 5/5
- **Files modified:** 4

## Accomplishments

- Rewrote `skills/teaching-design-package/SKILL.md` so the primary workflow is source materials, targeted clarification, unified Markdown, teacher review/editing, finalized Markdown, then script validation/rendering.
- Added a clarification strategy for required blockers, conflict resolution, review markers, optional preferences, and derived-fact boundaries.
- Reworked `references/format-and-orchestration.md` around teacher-editable Markdown, YAML/frontmatter limits, body extraction, review markers, source-material orchestration, and script boundaries.
- Preserved Phase 30's standalone package-owned boundary while removing script-first reading order from the public entry.
- Verified no script implementation files changed.

## Task Commits

1. **Tasks 1-5: teacher-facing Markdown workflow rewrite** - pending in execution commit.

## Files Created/Modified

- `skills/teaching-design-package/SKILL.md` - Teacher-facing source-materials-to-Markdown workflow, clarification strategy, runtime notes, and finalized-Markdown command boundary.
- `skills/teaching-design-package/references/format-and-orchestration.md` - Teacher-editable Markdown contract, YAML/body boundary, review markers, orchestration, and script boundary.
- `.planning/phases/31-teacher-facing-unified-markdown-workflow/31-VERIFICATION.md` - Verification evidence for Phase 31.
- `.planning/phases/31-teacher-facing-unified-markdown-workflow/31-SUMMARY.md` - This summary.

## Decisions Made

- Teachers interact with one reviewable Markdown, not with script commands as the main UX.
- `teaching-design-package-full.md` and course-specific `某某某课教学资料.md` are both accepted human-editable source-of-truth filenames.
- Derived facts such as total hours, school year, semester, date ranges, readiness, and diagnostics stay out of teacher-maintained YAML.
- Phase 32 still owns clean final 1+1+3 delivery enforcement and deeper scheduling validation.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None.

## Verification

See `31-VERIFICATION.md`. Required checks passed:

- `SKILL.md` teacher-workflow scan
- reference Markdown-contract scan
- dynamic precise legacy-name scan
- script diff empty check
- `git diff --check`
- `git diff --cached --check`

## Next Phase Readiness

Phase 32 can now enforce the clean 1+1+3 delivery directory and scheduling regression gates on top of a teacher-facing Markdown-first skill entry.

## Self-Check: PASSED

All Phase 31 plan tasks, acceptance criteria, and required verification commands were completed.

---
*Phase: 31-teacher-facing-unified-markdown-workflow*
*Completed: 2026-06-15*
