# Scheduling Contract Reference

This reference defines the shared scheduling contract for the future integrated teaching-design package. It is a package-level contract: the existing `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` scheduling logic is implementation evidence that the derivation is feasible, not the public package API.

## Requirement Traceability

- `TDP-01`: Accept calendar data, first teaching day, daily hours, item hours, holidays, and makeup teaching days.
- `TDP-02`: Output dates, term weeks, weekdays, assigned hours, and hour-consumption evidence for each scheduled item.
- `TDP-03`: Preserve uncertain, missing, or conflicting schedule inputs as teacher-review markers.
- `TDP-04`: Provide fixture evidence that hand-filled date ranges can be derived from auditable calendar and hour inputs.

## Contract Inputs

The scheduling consumer receives a normalized object with these fields:

- `calendar.dates`: ordered teaching-date entries in `YYYY-MM-DD` format. This list is the authoritative consumption order.
- `calendar.holidays`: excluded dates or named exclusions. Holidays are normalized before scheduling and must not silently remain in `calendar.dates` unless explicitly converted to makeup teaching days.
- `calendar.makeup_days`: included teaching dates that may fall outside normal weekdays, such as Saturday teaching days. Makeup days are normalized into `calendar.dates` with evidence.
- `first_teaching_day`: the first date that may consume teaching hours. It must exist in `calendar.dates`.
- `daily_hours`: positive integer teaching-hour capacity for each teaching date.
- `items[]`: source-order teaching items. Each item must include:
  - `source`: stable pointer such as `task:1/stage:5/row:3` or a lesson-fragment id.
  - `kind`: `学习任务`, `学习环节`, `教学内容`, or future lesson-fragment kind.
  - `title`: teacher-facing title or content text.
  - `hours`: positive integer `学时`.
  - optional parent pointers for task, stage, or lesson-plan grouping.

The contract consumes `items[]` exactly in source order. It does not sort by title, week, renderer table row, or later package output grouping unless a later phase explicitly defines another ordering rule.

## Derived Outputs

Each scheduled output item must preserve the source pointer and add deterministic scheduling evidence:

- `start_date`: first teaching date consumed by the item.
- `end_date`: last teaching date consumed by the item.
- `term_week` or `term_week_range`: `周次` derived from the first calendar teaching date's week start. These are not ISO week numbers.
- `weekday` or `weekday_range`: `星期` evidence from each consumed date.
- `assigned_hours`: total `学时` assigned to the item.
- `hour_consumption[]`: machine-readable date-level evidence. Each entry records `date`, `consumed_hours`, `remaining_daily_capacity`, and the item `source`.
- `review_markers[]`: local review markers for this item when input is uncertain, missing, conflicting, or exhausted.

Teacher-facing Markdown should show the same facts in readable Chinese terms: `学习任务`, `学习环节`, `教学内容`, `学时`, `周次`, `星期`, and `复核标记`.

## Week and Calendar Semantics

Term weeks are based on the first date in `calendar.dates`. The week start is derived from that first teaching date's calendar weekday, then every scheduled item computes its academic week relative to that term-week start. This intentionally avoids ISO week numbers because teaching calendars may begin mid-term or include makeup days.

Holidays and makeup teaching days are handled in the calendar/evidence layer:

- A holiday removed from teaching must be represented in `calendar.holidays` and absent from the consumable `calendar.dates`.
- A makeup teaching day must be represented in `calendar.makeup_days` and present in `calendar.dates`.
- If the same date is both an excluded holiday and a makeup day without a clear resolution, scheduling must add a `review_markers[]` entry instead of guessing.

## Review Behavior

Missing, uncertain, or conflicting schedule inputs must become nearby review evidence. A Markdown artifact must either place the marker near the affected item or summarize it under `## 复核标记`; structured output must mirror the issue in `review_markers[]`.

At minimum, these cases must fail deterministically or mark review-needed:

- `first_teaching_day` is missing.
- `first_teaching_day` is not present in `calendar.dates`.
- `daily_hours` is missing, non-integer, zero, or negative.
- an item has missing, non-integer, zero, or negative `hours`.
- source order is ambiguous.
- `calendar.dates` ends before all item hours are assigned.
- `calendar.holidays` conflicts with `calendar.makeup_days` or the normalized teaching-date list.

For final package exports, unresolved review markers should block final readiness. For teacher review, markers must remain explicit and auditable rather than being silently dropped.

## Fixture Expectation

The Phase 22 fixture uses the v1.10 `jiaoan-jihua` source shape: frontmatter with `first_teaching_day`, `daily_hours`, and ordered `##` tasks, `###` stages, and trailing integer hour markers. The expected schedule is derived from `calendar.dates` and item `hours`; it must not be copied from old target Typst output.

