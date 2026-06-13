# Phase 21 Research: Jiaoan Jihua 授课计划 1:1 Typst Conversion

**Date:** 2026-06-14
**Status:** Complete
**Scope:** local fixture conversion only; no external research required.

## Research Question

What does the executor need to know to plan and implement a strict, reviewable Markdown-to-Typst conversion for `skills/jiaoan-jihua/` without touching Phase 20 or copying the target fixture?

## Inputs Reviewed

- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/21-jiaoan-jihua-1-1-typst-conversion/21-CONTEXT.md`
- `.planning/phases/21-jiaoan-jihua-1-1-typst-conversion/21-DISCUSSION-LOG.md`
- `skills/jiaoan-jihua/SKILL.md`
- `skills/jiaoan-jihua/references/format-and-rendering.md`
- `skills/jiaoan-jihua/references/calendar.json`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
- `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md`
- `test/1.10/电气设备控制线路安装与调试授课计划.md`
- `test/1.10/电气设备控制线路安装与调试授课计划.typ`

## Findings

### Current Renderer Gap

The current `jiaoan-jihua.sh render` path is structurally generic: it parses frontmatter, emits a generic Typst document header, metadata block, headings, paragraphs, lists, and simple Markdown tables. Phase 21 requires an official table-style Typst fixture with:

- fixed `// jiaoan-jihua official template` header,
- `@preview/cuti:0.2.1` fake-bold import and show rule,
- fixed A4 margin/text/par settings,
- helper cell functions `task-th`, `th`, `subth`, `body-cell`, and `content-cell`,
- metadata grid,
- one centered five-column table,
- task rows, stage rowspans, content rows, week/day/hour cells,
- trailing signature grid.

The existing generic body renderer cannot be adjusted by styling alone; it needs a skill-local official-table parser and emitter path.

### Source Structure

The fixture Markdown is already highly regular:

- YAML frontmatter carries `major_name`, `course_name`, `teacher_name`, `class_name`, `first_teaching_day`, `daily_hours`, and `template`.
- `##` headings are learning task names.
- `###` headings are learning stage names.
- Non-empty body lines under stages use a final `-N` suffix, where `N` is the lesson-hour count.

This supports a reviewable parser without target-file copying. The executor should parse task/stage/content/hour records and derive table output from those records.

### Scheduling Model

Use `first_teaching_day: "2026-05-11"`, `daily_hours: 8`, and `skills/jiaoan-jihua/references/calendar.json`.

The target fixture assigns rows by consuming each content row's hour count sequentially across teaching days. A row's week/day cells are based on the teaching day or days occupied by that row. For example, after the first 16 hours of task 1 are consumed, the row `巡回指导电气线路安装过程-16` spans week 11, weekdays `3 4`, and 16 hours.

The executor should implement this as data logic:

1. Load ordered teaching dates from `calendar.json`.
2. Find `first_teaching_day`.
3. For every content row, consume `hours` against `daily_hours`.
4. Record every teaching date touched by the row.
5. Convert touched dates into teaching week and weekday cells.

For reviewability, use explicit helper names such as:

- `load_calendar_dates`
- `parse_official_jihua_body`
- `assign_schedule_cells`
- `term_week_for_date`
- `weekday_for_date`
- `emit_official_jihua_typst`

If Bash date arithmetic is needed, keep it inside the script using simple integer date helpers instead of shelling out to `date`, Python, Node, Typst, or external template executables.

### Anti-Fake-Conversion Boundary

The final renderer must not copy or splice `test/1.10/电气设备控制线路安装与调试授课计划.typ`.

The plan should require three kinds of evidence:

1. Source assertion: `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` must not contain the target fixture path or a copy-from-expected branch.
2. Generation assertion: render once without `--expected-typ`; only the Markdown fixture and calendar may be read for generation.
3. Equivalence assertion: after generation, compare the generated file to the target with `diff -u` and `shasum -a 256`.

`--expected-typ` may still exist as a verification convenience, but it must be used only after rendering has already written the generated output.

### Documentation Impact

`SKILL.md` should remain concise and preserve runtime adapter notes. `references/format-and-rendering.md` should carry the long-form official-table rules, anti-copy boundary, and strict verification commands. The example template can remain aligned with the fixture structure, but it should not include the target Typst.

## Risks

- A renderer that hard-codes the entire target Typst would pass diff but fail the requirement for reviewable Markdown-to-table conversion.
- Calendar/week logic can be off by one if week numbering is inferred from ISO week numbers rather than the teaching-term week used by the fixture.
- Updating shared jiaoan code or Phase 20 files would violate the parallel phase boundary.

## Recommendation

Use one execution plan with four tasks:

1. Add a skill-local official-table parser and scheduling model.
2. Replace the generic `jiaoan-jihua` render output for `template: jiaoan-jihua` with the official emitter.
3. Update concise skill and reference documentation.
4. Run strict no-copy, diff, and hash verification, then record evidence in the Phase 21 summary/verification artifacts during execute-phase.

## RESEARCH COMPLETE
