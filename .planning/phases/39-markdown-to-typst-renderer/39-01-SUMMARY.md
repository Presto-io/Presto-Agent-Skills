---
phase: 39-markdown-to-typst-renderer
plan: 01
subsystem: docs
tags: [tiaokedan, markdown, typst, renderer, deterministic-comparison]

requires:
  - phase: 37-typst-baseline
    provides: accepted 调课单 Typst/PDF visible baseline
  - phase: 38-markdown-contract
    provides: teacher-readable 调课单 Markdown fixture and contract
provides:
  - skill-local 调课单 Markdown-to-Typst renderer command
  - byte-for-byte generated Typst comparison evidence
  - negative fixtures for missing, malformed, and unsupported finalized Markdown
  - Phase 39 verification evidence for TKD-RENDER-01 through TKD-RENDER-04
affects: [tiaokedan, phase-40-skill-workflow]

tech-stack:
  added: [python-stdlib, bash]
  patterns: [skill-local renderer, byte-for-byte reference comparison, phase-local negative fixtures]

key-files:
  created:
    - skills/tiaokedan/scripts/tiaokedan.sh
    - skills/tiaokedan/scripts/tiaokedan_renderer.py
    - .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ
    - .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-missing-field.md
    - .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-table.md
    - .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-unsupported.md
    - .planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md
  modified: []

key-decisions:
  - "The Phase 39 renderer is intentionally narrow: it parses only the Phase 38 调课单 Markdown contract and emits the accepted Phase 37 Typst structure."
  - "Generated Typst matches `tiaokedan-reference.typ` byte-for-byte; no normalized-equivalent comparison rule is used."
  - "Runtime independence is enforced through skill-local Bash/Python, sibling skill path scans, and a copied `skills/tiaokedan/`-only render check."

patterns-established:
  - "Document renderer phases can commit generated deterministic Typst evidence when the generated directory is otherwise ignored."
  - "Negative finalized-Markdown fixtures stay phase-local rather than becoming teacher-facing templates."

requirements-completed:
  - TKD-RENDER-01
  - TKD-RENDER-02
  - TKD-RENDER-03
  - TKD-RENDER-04

duration: 20 min
completed: 2026-06-21
---

# Phase 39 Plan 01: 调课单 Markdown-to-Typst Renderer Summary

**Skill-local 调课单 renderer converts the accepted Markdown fixture into byte-for-byte matching Typst and rejects non-final Markdown failures**

## Performance

- **Duration:** 20 min
- **Started:** 2026-06-21T16:31:56Z
- **Completed:** 2026-06-21T16:50:24Z
- **Tasks:** 3
- **Files modified:** 11

## Accomplishments

- Added `skills/tiaokedan/scripts/tiaokedan.sh render --input --typ [--expected-typ]` and a Python stdlib renderer that validates Phase 38 frontmatter, section shape, table columns, required values, final markers, `<br>` line breaks, and unsupported raw Typst/HTML.
- Generated `.planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ` from `skills/tiaokedan/templates/tiaokedan.md` and verified it matches `skills/tiaokedan/templates/tiaokedan-reference.typ` byte-for-byte.
- Added three phase-local negative fixtures and stderr evidence covering unresolved required markers, malformed table columns, and unsupported raw Typst.
- Recorded `.planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md` with TKD-RENDER-01 through TKD-RENDER-04, D-01 through D-19, deterministic comparison, runtime independence, and Phase 40 boundary evidence.

## Task Commits

1. **Task 1: Add the skill-local renderer command and parser** - `1310cdc` (feat)
2. **Task 2: Add negative fixtures and non-zero failure checks** - `aa7a65c` (test)
3. **Task 3: Record deterministic comparison and independence evidence** - `bb64f8e` (docs)

## Files Created/Modified

- `skills/tiaokedan/scripts/tiaokedan.sh` - Public skill-local wrapper for `render`.
- `skills/tiaokedan/scripts/tiaokedan_renderer.py` - Contract parser, validator, deterministic Typst renderer, and expected-reference comparator.
- `.planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ` - Generated Typst evidence matching the accepted reference byte-for-byte.
- `.planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-missing-field.md` - Negative fixture for unresolved required marker.
- `.planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-table.md` - Negative fixture for malformed table columns.
- `.planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-unsupported.md` - Negative fixture for unsupported raw Typst.
- `.planning/phases/39-markdown-to-typst-renderer/generated/invalid-missing-field.stderr` - Captured stderr for missing/unresolved marker failure.
- `.planning/phases/39-markdown-to-typst-renderer/generated/invalid-table.stderr` - Captured stderr for malformed table failure.
- `.planning/phases/39-markdown-to-typst-renderer/generated/invalid-unsupported.stderr` - Captured stderr for unsupported syntax failure.
- `.planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md` - Phase 39 requirement, decision, comparison, negative, independence, and scope-boundary evidence.

## Decisions Made

- Kept comparison strict and byte-for-byte because the renderer can reproduce the accepted Phase 37 source exactly.
- Treated `{{AI草稿: ...}}` in required output facts as non-final for Phase 39, matching the finalized-Markdown gate.
- Allowed blank `备注` cells while validating every other table column as required.
- Kept all Phase 40 work out of scope: no canonical `SKILL.md`, PDF workflow, runtime adapters, README/index updates, clean delivery directory, manifest/info command, or missing-question guidance.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Initial positive run failed because closing parsing expected two adjacent closing lines, while the accepted Markdown fixture keeps a blank line between department and date. The renderer now ignores blank lines in the closing area while still requiring exactly two non-empty facts.
- `.planning/phases/39-markdown-to-typst-renderer/generated/` is ignored by default. The required deterministic Typst and stderr evidence files were added explicitly with `git add -f`.
- `git diff --cached --check` caught trailing whitespace in `39-VERIFICATION.md`; it was removed before the verification commit.

## Verification

All Phase 39 plan checks passed:

- `test -x skills/tiaokedan/scripts/tiaokedan.sh`
- `test -s skills/tiaokedan/scripts/tiaokedan_renderer.py`
- `python3 -m py_compile skills/tiaokedan/scripts/tiaokedan_renderer.py`
- `skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ --expected-typ skills/tiaokedan/templates/tiaokedan-reference.typ`
- `diff -u skills/tiaokedan/templates/tiaokedan-reference.typ .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ`
- `shasum -a 256 skills/tiaokedan/templates/tiaokedan-reference.typ .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ`
- negative render commands for `invalid-missing-field.md`, `invalid-table.md`, and `invalid-unsupported.md` all exited non-zero with expected stderr.
- `! rg 'skills/(gongwen|teaching-design-package|jiaoan-|end-of-term|school-presentation)' skills/tiaokedan/scripts`
- copied-only `/tmp/tiaokedan-phase39-only/skills/tiaokedan` positive render check passed.
- scope check confirmed no README/index/compatibility/`skills/tiaokedan/SKILL.md` changes.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 39 is complete. Phase 40 can now package the canonical `tiaokedan` skill workflow, PDF gate, runtime adapter notes, missing-information questions, clean delivery boundary, and repository discoverability without changing the accepted renderer evidence.

## Self-Check: PASSED

- Key created files exist on disk.
- `git log --oneline --grep="39-01"` returns the three task commits.
- All plan-level verification commands passed.
- Generated Typst comparison is byte-for-byte with no normalization rule.

---
*Phase: 39-markdown-to-typst-renderer*
*Completed: 2026-06-21*
