---
phase: 37-typst-baseline
plan: 01
subsystem: document-workflow
tags: [tiaokedan, typst, pdf, baseline]

requires:
  - phase: 37-context
    provides: locked 调课单 layout, typography, table rows, and signature decisions
provides:
  - Hand-authored `调课单` Typst reference under `skills/tiaokedan/templates/`
  - Non-empty compiled PDF baseline evidence
  - Phase 37 verification evidence for TKD-TYP-01 through TKD-TYP-03
affects: [tiaokedan, phase-38-markdown-contract, phase-39-renderer]

tech-stack:
  added: []
  patterns: [skill-local Typst reference fixture, non-empty PDF evidence, scope-boundary verification]

key-files:
  created:
    - skills/tiaokedan/templates/tiaokedan-reference.typ
    - skills/tiaokedan/templates/tiaokedan-reference.pdf
    - .planning/phases/37-typst-baseline/37-VERIFICATION.md
  modified: []

key-decisions:
  - "Phase 37 stays target-first only: Typst reference, optional PDF evidence, and verification file."
  - "The table is full-width in A4 landscape and uses explicit Typst line breaks for the first row's two time cells."
  - "No Markdown contract, renderer, scripts, SKILL.md, runtime adapter notes, or README/index updates were introduced."

patterns-established:
  - "New document skills may start with a hand-authored accepted Typst target before automation when the milestone explicitly scopes that order."
  - "PDF readiness is accepted only after local Typst compile exits 0 and the PDF byte size is greater than 0."

requirements-completed:
  - TKD-TYP-01
  - TKD-TYP-02
  - TKD-TYP-03

duration: 49min
completed: 2026-06-21
---

# Phase 37: 调课单 Typst Baseline Summary

**Hand-authored A4 landscape `调课单` Typst reference with non-empty PDF baseline evidence**

## Performance

- **Duration:** 49 min
- **Started:** 2026-06-21T07:43:00Z
- **Completed:** 2026-06-21T08:32:00Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Created `skills/tiaokedan/templates/tiaokedan-reference.typ` as the accepted hand-authored target surface before Markdown or renderer automation.
- Captured the locked title, recipient line, explanatory paragraph, 8-column adjustment table, two example rows, row-1 time-cell line breaks, and right-side closing signature.
- Compiled `skills/tiaokedan/templates/tiaokedan-reference.pdf` successfully with Typst 0.15.0; the PDF is 29548 bytes.
- Recorded requirement, decision, command, compile, visual-preview, and negative scope evidence in `37-VERIFICATION.md`.

## Task Commits

1. **Task 1-3: Hand-author Typst baseline, compile PDF, and record verification evidence** - `ae67e62` (feat)

## Files Created/Modified

- `skills/tiaokedan/templates/tiaokedan-reference.typ` - hand-authored Phase 37 Typst baseline for the adjustment form.
- `skills/tiaokedan/templates/tiaokedan-reference.pdf` - non-empty PDF evidence compiled from the reference Typst file.
- `.planning/phases/37-typst-baseline/37-VERIFICATION.md` - evidence for TKD-TYP-01, TKD-TYP-02, TKD-TYP-03, D-01 through D-13, compile status, and scope boundaries.

## Decisions Made

- Used A4 landscape via `#set page(paper: "a4", flipped: true)` and kept default Typst page margins as planned.
- Used same-family Chinese font fallback declarations for Songti-style title and FangSong-style body/table/signature text.
- Accepted a successful compile with empty captured stderr; a direct earlier compile printed unavailable fallback-font warnings but still produced a valid PDF.
- Kept Phase 38-40 artifacts absent: no Markdown fixture, parser, renderer, scripts, canonical skill entry, runtime adapter notes, or README/index updates.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Correctness] Replaced invalid `table(width:)` Typst parameter**
- **Found during:** Task 2 (Compile the baseline or capture the exact blocker)
- **Issue:** Typst 0.15.0 rejected `table(width: 100%)` with `unexpected argument: width`.
- **Fix:** Wrapped the table in `#block(width: 100%)[#table(...)]`, preserving the full-width table intent.
- **Files modified:** `skills/tiaokedan/templates/tiaokedan-reference.typ`
- **Verification:** Re-ran source assertions and `typst compile`; compile exited 0 and produced a 29548-byte PDF.
- **Committed in:** `ae67e62`

---

**Total deviations:** 1 auto-fixed (Rule 2 correctness).  
**Impact on plan:** No scope expansion; the fix was required for the planned PDF compile evidence.

## Issues Encountered

- Sandboxed `qlmanage` thumbnail generation failed with a macOS Quick Look sandbox initialization error. It was rerun with escalation to produce `/private/tmp/tiaokedan-reference.pdf.png` for visual inspection only; no repository files were written by that command.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 38 can use `skills/tiaokedan/templates/tiaokedan-reference.typ` as the stable visual target for a teacher-readable Markdown fixture and contract. Phase 39 should continue to avoid sibling script runtime dependencies and later compare generated Typst against this accepted reference or a documented normalized equivalent.

---
*Phase: 37-typst-baseline*
*Completed: 2026-06-21*
