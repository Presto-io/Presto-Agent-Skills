# Phase 22: Scheduling Contract and Fixture - Research

**Date:** 2026-06-14
**Command:** `/gsd:plan-phase 22 --auto`
**Question:** What do I need to know to plan this phase well?
**Status:** Research complete

## Scope

Phase 22 should formalize shared scheduling behavior for the future integrated teaching-design package. The deliverable is not the package skill itself and not a broad renderer refactor. It should create a portable contract, reviewable evidence shape, conflict/review semantics, and one deterministic fixture proving that date ranges can be derived from calendar and hour inputs.

## Required Local Evidence

### Existing scheduling implementation

`skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` already proves the narrow algorithm:

- `load_calendar_dates` reads `skills/jiaoan-jihua/references/calendar.json` into an ordered teaching-date list.
- `assign_schedule_cells` requires `first_teaching_day` and `daily_hours`.
- `assign_schedule_cells` validates that `daily_hours` is a positive integer.
- `assign_schedule_cells` finds `first_teaching_day` inside the calendar.
- `parse_official_jihua_body` preserves source order for learning tasks, stages, and content rows.
- Each body line must end in an integer hour marker (`text-N`); malformed lines fail rather than disappearing.
- The algorithm consumes row hours sequentially across calendar dates and daily capacity.
- For every row, it records term week and weekday values derived from consumed calendar dates.
- `term_week_for_date` derives the academic week from the first calendar date's teaching-week start, not from ISO week numbers.
- It fails when the calendar ends before all hours are assigned.

This implementation is a proof source, not the final public contract. Phase 22 should avoid exposing shell implementation internals as the package API.

### Existing authoring rules

`skills/jiaoan-jihua/references/format-and-rendering.md` locks several rules that should become contract-level language:

- `first_teaching_day` is the first date that consumes teaching hours and must exist in the calendar.
- `daily_hours` is the per-date capacity for consuming source-order content hours.
- Source task, stage, and content ordering is deterministic.
- Missing or unexpressible scheduling data must become nearby review markers rather than being silently dropped.
- Term week numbers come from the teaching calendar start, not ISO week numbers.

### Fixture source

`test/1.10/电气设备控制线路安装与调试授课计划.md` is a strong Phase 22 fixture input because it already contains:

- `first_teaching_day: "2026-05-11"`
- `daily_hours: 8`
- ordered learning tasks (`##`)
- ordered learning stages (`###`)
- ordered teaching-content rows with trailing hour markers

The fixture should not merely prove the old Typst renderer still works. It should demonstrate structured scheduling input, derived date/week/weekday/hour evidence, and at least one hand-filled-style date range derived from the contract.

## Contract Planning Implications

### Recommended contract files

Phase 22 should add a long-form reference rather than overloading a canonical `SKILL.md`:

- `references/scheduling-contract.md`

The contract should be reusable by Phase 23 without forcing the future `teaching-design-package` skill to import `jiaoan-jihua` shell internals.

### Recommended fixture files

Use deterministic fixture artifacts that can be reviewed without running a full package workflow:

- `test/1.11/scheduling-contract/fixture-source.md`
- `test/1.11/scheduling-contract/expected-schedule.json`
- `test/1.11/scheduling-contract/expected-schedule.md`

The JSON fixture should be machine-readable. The Markdown fixture should be teacher-reviewable and should show review markers and hour-consumption evidence in Chinese teaching-document terms.

### Recommended script placement

If implementation needs reusable derivation, keep it skill-local or repository-local rather than changing existing public skill commands:

- `scripts/derive-scheduling-fixture.py`

This script can parse the fixture source, calendar JSON, and output deterministic schedule evidence. It should not be wired into existing skills during Phase 22 unless the plan explicitly preserves public behavior.

## Contract Fields To Plan

Required inputs:

- `calendar.dates[]`: ordered teaching-date entries.
- `calendar.holidays[]`: excluded dates or named exclusions.
- `calendar.makeup_days[]`: included teaching dates that may fall outside normal weekdays.
- `first_teaching_day`: first date to consume source hours.
- `daily_hours`: positive integer teaching-hour capacity per teaching date.
- `items[]`: ordered tasks, activities, or lesson fragments.
- `items[].hours`: positive integer assigned hours.
- `items[].source`: source pointer such as task title, stage title, row index, or lesson-fragment id.

Derived outputs:

- `start_date`
- `end_date`
- `term_week` or `term_week_range`
- `weekday` or `weekday_range`
- `assigned_hours`
- `hour_consumption[]`, including date, consumed hours, remaining daily capacity after allocation, and source pointer
- `review_markers[]` when data is missing, ambiguous, conflicting, or exhausted

## Conflict And Review Cases

The plan must require explicit review markers for at least these cases:

- `first_teaching_day` is absent.
- `first_teaching_day` is not present in the calendar.
- `daily_hours` is missing, non-integer, zero, or negative.
- A task/activity/fragment has missing, zero, negative, or non-integer hours.
- Source item order is ambiguous.
- Calendar dates end before all hours are assigned.
- Holidays and makeup days conflict with the ordered teaching-date list.

Markers should be close to the affected item and also summarized under `## 复核标记` where a Markdown artifact is produced.

## Verification Strategy

Plan verification should check:

- The contract reference names TDP-01 through TDP-04.
- The contract explicitly cites `first_teaching_day`, `daily_hours`, calendar dates, holidays, makeup days, ordered items, derived dates, term weeks, weekdays, assigned hours, hour-consumption evidence, and review markers.
- Fixture JSON and Markdown are deterministic and contain evidence derived from the v1.10 source shape.
- At least one fixture row crosses or consumes calendar capacity in a way that proves derivation rather than copied hand-filled dates.
- Existing public skill commands for `jiaoan-jihua` and `jiaoan-shicao` remain unchanged in Phase 22.

## Risks

- Over-scoping into the full `teaching-design-package` orchestration would duplicate Phase 23.
- Editing `jiaoan-jihua` command behavior too early could create regression work that belongs in Phase 25.
- A prose-only contract without fixture evidence would not satisfy TDP-04.
- A fixture that only runs the old Typst renderer would not prove the new shared contract.

## Research Complete

Phase 22 can be planned as one implementation plan with three deliverable clusters: contract reference, deterministic fixture/evidence generator, and verification/documentation traceability.
