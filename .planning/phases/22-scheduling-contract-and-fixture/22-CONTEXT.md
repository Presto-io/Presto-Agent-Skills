# Phase 22: Scheduling Contract and Fixture - Context

**Gathered:** 2026-06-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 22 defines the shared scheduling contract for the future integrated teaching-design package. It must turn proven `jiaoan-jihua` scheduling behavior into a package-level contract and fixture: inputs, derived outputs, hour-consumption evidence, conflict/review handling, and at least one fixture showing that previously hand-filled date ranges can be inferred from auditable calendar and hour data.

This phase does not create the full `teaching-design-package` orchestration skill, does not delete or replace existing skills, and does not implement optional end-of-term package outputs. Those remain Phase 23 and Phase 24 work.

**Auto-mode recovery note:** This context was reviewed during `/gsd:discuss-phase 22 --auto` recovery. `gsd-sdk query init.phase-op 22` now resolves Phase 22 with `phase_found: true`; existing decisions remain grounded in `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/research/SUMMARY.md`, and code evidence from `jiaoan-jihua`.

</domain>

<decisions>
## Implementation Decisions

### Scheduling Contract Shape
- **D-01:** Define a package-level scheduling contract instead of exposing the existing `jiaoan-jihua` renderer internals as the shared API. The existing shell script is evidence that the derivation is feasible, not the final public contract.
- **D-02:** Required scheduling inputs should include school calendar dates, first teaching day, daily hours, task/activity/lesson-fragment hour allocations, holiday exclusions, and makeup teaching days. If a value is absent or ambiguous, the contract should preserve a review marker rather than inventing a silent default.
- **D-03:** Keep ordering deterministic. The contract should consume tasks, activities, and lesson fragments in source order unless a later phase explicitly defines a different ordering rule.

### Derived Outputs and Evidence
- **D-04:** Each scheduled item should output start date, end date, term week number or range, weekday evidence, assigned hours, and hour-consumption evidence that shows which calendar dates consumed which hours.
- **D-05:** Evidence should be teacher-reviewable and machine-readable. Plan toward a Markdown-readable summary plus deterministic structured fixture data, so later phases can display the evidence in the integrated Markdown intermediate and verify it in tests.
- **D-06:** Term week semantics should follow the existing `jiaoan-jihua` behavior: derive the academic week from the first calendar teaching date's week start, not ISO week numbers.

### Conflict and Review Behavior
- **D-07:** Missing, uncertain, or conflicting schedule inputs must become explicit review markers near the affected task/activity/fragment. This carries forward the repository's Markdown-first review discipline and the end-of-term `## 复核标记` gate pattern.
- **D-08:** The contract should fail or mark review-needed when `first_teaching_day` is not in the calendar, daily hours are non-positive or non-integer, a row/fragment has missing or zero hours, or the calendar ends before all hours are assigned.
- **D-09:** Holidays and makeup teaching days should be normalized into the calendar/evidence layer rather than handled as ad hoc renderer exceptions.

### Fixture Scope
- **D-10:** The minimum Phase 22 fixture should reuse the v1.10 teaching-plan source shape where possible: `test/1.10/电气设备控制线路安装与调试授课计划.md` has `first_teaching_day: "2026-05-11"`, `daily_hours: 8`, and ordered content rows with trailing hour markers.
- **D-11:** The fixture should prove at least one hand-filled date-range style output can be derived from the shared contract, not merely that the old renderer still emits Typst.
- **D-12:** Keep the fixture focused on scheduling evidence. Full package Markdown, split PDFs, combined PDFs, and end-of-term artifacts are intentionally deferred.

### Claude's Discretion
- Use conservative names and file placement that fit existing repository conventions. Prefer `references/` for contract prose, `templates/` for reviewable intermediate shape, `scripts/` only when implementation is actually planned, and `test/` or phase-local verification files for fixture evidence.
- Planner may choose exact schema filenames, but must preserve full traceability from source calendar/hour inputs to derived dates and review markers.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Requirements
- `.planning/ROADMAP.md` — Defines v1.11 Phases 22-25 and scopes Phase 22 to scheduling contract, evidence, conflict handling, and fixture proof.
- `.planning/REQUIREMENTS.md` — Locks TDP-01 through TDP-04 for Phase 22 and records out-of-scope future work.
- `.planning/PROJECT.md` — Captures project-level v1.11 decisions, especially preserving existing skills and keeping scheduling evidence auditable.
- `.planning/STATE.md` — Records current milestone, Phase 22 focus, and active decisions carried into v1.11.
- `.planning/research/SUMMARY.md` — Summarizes local evidence that existing `jiaoan-jihua` scheduling can be generalized.

### Existing Scheduling Evidence
- `skills/jiaoan-jihua/SKILL.md` — Existing teaching-schedule skill contract and safety rules.
- `skills/jiaoan-jihua/references/format-and-rendering.md` — Detailed frontmatter, body, calendar, scheduling, and verification rules.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` — Current implementation evidence for calendar loading, term week derivation, weekday derivation, and sequential hour consumption.
- `skills/jiaoan-jihua/references/calendar.json` — Existing teaching date sequence used by the current renderer.
- `test/1.10/电气设备控制线路安装与调试授课计划.md` — Concrete fixture source with `first_teaching_day`, `daily_hours`, ordered tasks/stages/content rows, and hour suffixes.

### Related Review and Package Patterns
- `skills/jiaoan-shicao/SKILL.md` — Existing lesson-plan skill that the future package must preserve and compose.
- `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md` — Review-marker and deterministic artifact discipline that should inform conflict handling.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`: Contains proven shell logic for `date_to_serial`, `weekday_for_date`, `load_calendar_dates`, `term_week_for_date`, parsing `text-N` hour markers, and sequentially assigning calendar cells.
- `skills/jiaoan-jihua/references/calendar.json`: Existing ordered teaching-date list that already excludes non-teaching dates and includes makeup days such as Saturday teaching dates.
- `test/1.10/电气设备控制线路安装与调试授课计划.md`: Ready source material for a scheduling fixture because it already has ordered learning tasks, stages, content rows, `first_teaching_day`, and `daily_hours`.

### Established Patterns
- Markdown-first document workflows are the project norm. Scheduling evidence should be inspectable before Typst/PDF generation.
- Long rules belong in `references/`; canonical `SKILL.md` entries should stay concise.
- Public command surfaces and existing skills should be preserved unless a requirement explicitly authorizes a breaking change.
- Uncertain or unresolved data should be represented as reviewable markers, not silently dropped.

### Integration Points
- Phase 22 should provide the contract and fixture that Phase 23 can compose from the new `teaching-design-package` skill.
- Phase 23 will likely consume the contract in a teacher-reviewable Markdown intermediate covering both teaching-plan and lesson-plan sections.
- Phase 24 can later attach optional end-of-term artifacts using the same review and manifest discipline, but Phase 22 should not implement that package layer.

</code_context>

<specifics>
## Specific Ideas

- Treat the current `jiaoan-jihua` renderer as a black-box proof source: it already derives weeks and weekdays from a calendar sequence and consumes row hours across daily capacity.
- Make hour consumption evidence explicit enough for teachers to audit why a task/activity/fragment received a date range.
- Preserve Chinese teaching-document semantics where relevant: 学习任务, 学习环节, 教学内容, 学时, 周次, 星期, and 复核标记.

</specifics>

<deferred>
## Deferred Ideas

- Creating the actual `teaching-design-package` skill entry is Phase 23.
- Composing `jiaoan-jihua` and `jiaoan-shicao` outputs is Phase 23.
- Optional `end-of-term-teaching-materials` integration, workbook/table package discovery, split PDFs, and combined `teaching-design-package.pdf` outputs are Phase 24.
- Regression verification across existing public skill command surfaces and runtime adapter coverage is Phase 25.

</deferred>

---

*Phase: 22-Scheduling Contract and Fixture*
*Context gathered: 2026-06-14*
