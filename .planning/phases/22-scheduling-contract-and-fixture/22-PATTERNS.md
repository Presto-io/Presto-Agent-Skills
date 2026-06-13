# Phase 22: Scheduling Contract and Fixture - Pattern Map

**Date:** 2026-06-14
**Status:** Pattern mapping complete

## Existing Analogs

| Planned File | Closest Existing Analog | Pattern To Reuse |
|--------------|-------------------------|------------------|
| `references/scheduling-contract.md` | `skills/jiaoan-jihua/references/format-and-rendering.md` | Long rules live in `references/`; canonical entries stay concise. |
| `test/1.11/scheduling-contract/fixture-source.md` | `test/1.10/电气设备控制线路安装与调试授课计划.md` | YAML frontmatter plus ordered `##` task, `###` stage, and trailing `-N` hour rows. |
| `test/1.11/scheduling-contract/expected-schedule.json` | `skills/end-of-term-teaching-materials` deterministic table artifacts | Machine-readable evidence should be deterministic and reviewable. |
| `test/1.11/scheduling-contract/expected-schedule.md` | `end-of-term-full.md` review discipline from `workflow-and-artifacts.md` | Markdown evidence should keep `## 复核标记` and block silent uncertainty. |
| `scripts/derive-scheduling-fixture.py` | `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` | Preserve source order, validate calendar/hour inputs, derive week/weekday/date evidence. |

## Source Order Pattern

`skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` parses the body in order:

- `##` starts a learning task.
- `###` starts a learning stage.
- `text-N` lines become ordered content rows with integer hours.
- Content before a task or stage fails.
- Malformed stage body lines fail.

Phase 22 should keep this source-order semantics in the shared contract and fixture. Future package behavior can map lesson fragments into the same ordered item model without adopting the shell parser as a public API.

## Scheduling Evidence Pattern

The existing shell script assigns schedule cells by:

- requiring a first teaching date;
- requiring positive integer daily capacity;
- finding the first teaching date in an ordered calendar;
- consuming item hours across dates and remaining daily capacity;
- appending term week and weekday evidence;
- failing if the calendar ends before all hours are assigned.

The Phase 22 contract should expand that into a visible `hour_consumption[]` record with date-level consumed hours rather than only final Typst table cells.

## Review Marker Pattern

`skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md` establishes a useful package rule:

- unresolved uncertainty appears in Markdown;
- unresolved uncertainty has matching `## 复核标记` rows;
- final export cannot claim success while markers remain.

Phase 22 should adopt the same review discipline for scheduling conflicts, while leaving final package export behavior to later phases.

## Non-Patterns

- Do not put a complete scheduling reference inside a canonical skill entry during Phase 22.
- Do not rename existing `jiaoan-jihua` or `jiaoan-shicao` command surfaces.
- Do not generate the future `teaching-design-package` skill in this phase.
- Do not use the v1.10 target Typst file as input to derive scheduling fixture evidence.

## Pattern Mapping Complete
