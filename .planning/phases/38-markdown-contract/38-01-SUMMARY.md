---
phase: 38-markdown-contract
plan: 01
subsystem: docs
tags: [tiaokedan, markdown, contract, fixture]

requires:
  - phase: 37-typst-baseline
    provides: accepted 调课单 Typst/PDF visible baseline
provides:
  - teacher-readable 调课单 Markdown fixture
  - skill-local Markdown contract reference
  - Phase 38 verification evidence for TKD-MD-01 through TKD-MD-03
affects: [tiaokedan, phase-39-renderer, phase-40-skill-workflow]

tech-stack:
  added: []
  patterns: [YAML frontmatter + body, teacher-owned Markdown facts, skill-local review markers]

key-files:
  created:
    - skills/tiaokedan/templates/tiaokedan.md
    - skills/tiaokedan/references/markdown-contract.md
    - .planning/phases/38-markdown-contract/38-VERIFICATION.md
  modified: []

key-decisions:
  - "The accepted 调课单 source is teacher-readable Markdown with exactly title, recipient, department, and date frontmatter."
  - "Required unknown values use {{待补充: 说明}}, while blank 备注 cells may remain empty when the accepted fact is genuinely blank."
  - "Renderer-owned layout defaults stay out of the teacher fixture and are documented only as boundaries for Phase 39."

patterns-established:
  - "调课单 fixture mirrors the accepted Phase 37 visible facts without raw Typst."
  - "Skill-local Markdown contracts define markers and renderer-default boundaries without implementing parser or renderer code."

requirements-completed: [TKD-MD-01, TKD-MD-02, TKD-MD-03]

duration: 9 min
completed: 2026-06-21
---

# Phase 38 Plan 01: 调课单 Markdown Contract Summary

**Teacher-readable 调课单 Markdown source and skill-local field contract for the accepted Phase 37 form facts**

## Performance

- **Duration:** 9 min
- **Started:** 2026-06-21T15:35:00Z
- **Completed:** 2026-06-21T15:43:42Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Created `skills/tiaokedan/templates/tiaokedan.md` as a plain Markdown fixture with YAML frontmatter, visible reason text, exact 8-column adjustment table, preserved row-1 `<br>` line breaks, blank optional remarks, and closing department/date facts.
- Added `skills/tiaokedan/references/markdown-contract.md` to define required/optional teacher facts, `{{待补充: 说明}}`, `{{AI草稿: 说明}}`, future non-final marker behavior, renderer-owned defaults, and Phase 38 non-goals.
- Recorded `.planning/phases/38-markdown-contract/38-VERIFICATION.md` with TKD-MD-01 through TKD-MD-03 evidence, D-01 through D-16 coverage, and explicit Phase 39/40 scope-boundary checks.

## Task Commits

1. **Task 1: Hand-author the teacher-readable Markdown fixture** - `d2ab1aa` (feat)
2. **Task 2: Write the skill-local Markdown contract reference** - `7ee4967` (feat)
3. **Task 3: Record Phase 38 verification and scope evidence** - `aef9385` (docs)

## Files Created/Modified

- `skills/tiaokedan/templates/tiaokedan.md` - Teacher-reviewable Markdown fixture mirroring the accepted 调课单 baseline facts.
- `skills/tiaokedan/references/markdown-contract.md` - Skill-local Markdown contract, marker semantics, renderer-default boundary, and Phase 38 non-goals.
- `.planning/phases/38-markdown-contract/38-VERIFICATION.md` - Requirement, decision, fixture, contract, and scope-boundary verification evidence.

## Decisions Made

- Used exactly four frontmatter fields in the accepted fixture: `title`, `recipient`, `department`, and `date`.
- Kept renderer-only defaults out of `tiaokedan.md`; the reference names them as downstream implementation boundaries only.
- Preserved empty `备注` cells as accepted optional blank facts rather than replacing them with missing-value markers.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `git diff --cached --check` caught trailing whitespace in the initial verification file. The whitespace was removed before committing.
- `gsd-sdk query roadmap.update-plan-progress 38` is incompatible with this milestone roadmap table shape and temporarily rewrote the Phase 38 row; the row was restored before metadata closeout.

## Verification

All Phase 38 plan checks passed:

- Markdown fixture existence, frontmatter, accepted paragraph, table header, locked row facts, blank remarks, and absence of raw Typst/layout tokens.
- Contract reference existence, fixture path, `YAML frontmatter + body`, all required fields/columns, `{{待补充: 说明}}`, `{{AI草稿: 说明}}`, `renderer-owned defaults`, `A4 landscape`, `Phase 38 non-goals`, and absence of executable parser/renderer snippets.
- Verification file existence, TKD-MD-01/TKD-MD-02/TKD-MD-03 coverage, D-01 through D-16 coverage, and Phase 39/40 artifact absence.
- Scope checks confirmed no `skills/tiaokedan/SKILL.md`, no `skills/tiaokedan/scripts/`, no generated/renderer/script files, and no README/index/compatibility changes.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 38 is complete and ready for verification. Phase 39 can consume `tiaokedan.md`, `markdown-contract.md`, and the Phase 37 Typst baseline to implement the independent Markdown-to-Typst renderer later; no Phase 39/40 files were created in this plan.

## Self-Check: PASSED

- Key created files exist on disk.
- `git log --oneline --grep="38-01"` returns the three task commits.
- All plan-level verification commands passed after the trailing-whitespace fix.

---
*Phase: 38-markdown-contract*
*Completed: 2026-06-21*
