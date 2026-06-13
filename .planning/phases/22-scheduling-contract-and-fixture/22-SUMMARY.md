---
phase: 22-scheduling-contract-and-fixture
plan: 01
subsystem: documentation
tags: [scheduling, fixtures, teaching-design-package, jiaoan-jihua]
requires:
  - phase: 21
    provides: "jiaoan-jihua fixture-backed scheduling behavior"
provides:
  - "Package-level scheduling contract for v1.11"
  - "Deterministic scheduling fixture JSON and Markdown evidence"
  - "Repository-local fixture derivation verifier"
affects: [teaching-design-package, jiaoan-jihua, jiaoan-shicao]
tech-stack:
  added: []
  patterns: [Markdown-first contract reference, deterministic fixture evidence]
key-files:
  created:
    - references/scheduling-contract.md
    - test/1.11/scheduling-contract/fixture-source.md
    - test/1.11/scheduling-contract/expected-schedule.json
    - test/1.11/scheduling-contract/expected-schedule.md
    - scripts/derive-scheduling-fixture.py
  modified:
    - README.md
    - docs/directory-spec.md
key-decisions:
  - "Scheduling is documented as a package-level contract, not the jiaoan-jihua shell API."
  - "Fixture evidence is derived from calendar dates and source-order hour consumption."
  - "Phase 22 remains bounded to contract, fixture, verifier, and discoverability docs."
patterns-established:
  - "Shared orchestration references can live in root references/ when they are not owned by one existing skill."
  - "Versioned deterministic fixture evidence can live under test/<version>/<topic>/."
requirements-completed: [TDP-01, TDP-02, TDP-03, TDP-04]
duration: 45min
completed: 2026-06-13
---

# Phase 22 Plan 01: Scheduling Contract and Fixture Summary

**Package-level scheduling contract with deterministic calendar/hour fixture evidence for future teaching-design package composition**

## Performance

- **Duration:** 45 min
- **Started:** 2026-06-13T19:50:00Z
- **Completed:** 2026-06-13T20:34:37Z
- **Tasks:** 5
- **Files modified:** 8

## Accomplishments

- Added `references/scheduling-contract.md` covering TDP-01 through TDP-04, required inputs, derived outputs, source-order consumption, non-ISO term week semantics, and `## 复核标记` review behavior.
- Added a v1.11 scheduling fixture source plus deterministic JSON and teacher-reviewable Markdown evidence under `test/1.11/scheduling-contract/`.
- Added `scripts/derive-scheduling-fixture.py`, a local verifier that derives schedule evidence from frontmatter, ordered source rows, calendar dates, and hour consumption without reading Typst targets.
- Documented the shared contract and fixture evidence in README and the directory specification while preserving existing `jiaoan-jihua` and `jiaoan-shicao` public command surfaces.

## Task Commits

1. **Task 1: Create the shared scheduling contract reference** - `d874765`
2. **Task 2: Add deterministic fixture source and expected evidence** - `6da8e45`
3. **Task 3: Add fixture derivation verifier** - `8d07716`
4. **Task 4: Wire documentation discoverability** - `d401a52`
5. **Task 5: Run Phase 22 verification and record evidence** - recorded in this summary and metadata commit

## Files Created/Modified

- `references/scheduling-contract.md` - Shared scheduling contract, inputs, outputs, evidence semantics, and review-marker rules.
- `test/1.11/scheduling-contract/fixture-source.md` - Minimal v1.10-shaped scheduling fixture source.
- `test/1.11/scheduling-contract/expected-schedule.json` - Deterministic machine-readable derived schedule evidence.
- `test/1.11/scheduling-contract/expected-schedule.md` - Teacher-reviewable schedule evidence with `## 调度证据` and `## 复核标记`.
- `scripts/derive-scheduling-fixture.py` - Fixture derivation and comparison verifier.
- `README.md` - Shared reference and fixture discovery entry.
- `docs/directory-spec.md` - Root `references/` and versioned `test/` placement rules.

## Decisions Made

- The public scheduling contract is package-level. Existing `jiaoan-jihua` shell logic remains implementation evidence only.
- The fixture proves derivation by showing an item with `hour_consumption` over more than one date.
- Phase 22 does not add the future `teaching-design-package` skill or claim combined package PDFs.

## Deviations from Plan

None - plan executed exactly as written.

**Total deviations:** 0 auto-fixed.
**Impact on plan:** None.

## Issues Encountered

- `test/` is ignored by the repository `.gitignore`, so the planned deterministic fixture files were added with precise `git add -f` paths.
- `python3 -m py_compile` creates `scripts/__pycache__`; the generated cache was removed after verification and not committed.

## Verification

- `python3 -m py_compile scripts/derive-scheduling-fixture.py` - passed.
- `python3 -m json.tool test/1.11/scheduling-contract/expected-schedule.json >/tmp/phase22-expected-schedule.json` - passed.
- `scripts/derive-scheduling-fixture.py --source test/1.11/scheduling-contract/fixture-source.md --calendar skills/jiaoan-jihua/references/calendar.json --expected test/1.11/scheduling-contract/expected-schedule.json` - passed.
- `rg "TDP-01|TDP-02|TDP-03|TDP-04" references/scheduling-contract.md` - found all four IDs.
- `rg "calendar\\.dates|calendar\\.holidays|calendar\\.makeup_days|first_teaching_day|daily_hours|items\\[\\]|hour_consumption\\[\\]|review_markers\\[\\]" references/scheduling-contract.md` - found required identifiers.
- `rg "## 复核标记" test/1.11/scheduling-contract/expected-schedule.md references/scheduling-contract.md` - found both review-marker locations.
- `rg "\\.typ" scripts/derive-scheduling-fixture.py` - exited 1 as expected.
- Invalid `daily_hours: 0` temporary fixture - exited 1 with `daily_hours must be greater than zero`, as expected.
- `git diff -- skills/jiaoan-jihua/SKILL.md skills/jiaoan-shicao/SKILL.md` - empty.
- `git diff --check` - passed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 23 can consume `references/scheduling-contract.md` and `test/1.11/scheduling-contract/` when defining the future integrated `teaching-design-package` skill and its teacher-reviewable Markdown intermediate.

## Self-Check: PASSED

- All planned files exist.
- All required verification commands passed or returned the expected non-zero assertion.
- Existing standalone jiaoan skill command surfaces were not modified.

---
*Phase: 22-scheduling-contract-and-fixture*
*Completed: 2026-06-13*
