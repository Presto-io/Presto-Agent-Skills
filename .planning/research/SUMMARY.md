# Research Summary: v1.11 Integrated Teaching Design Package

**Date:** 2026-06-14
**Scope:** Local repository research for the v1.11 milestone initialization.

## Question 1: Can hand-filled teaching-design start/end dates be inferred?

Yes. The existing `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` already implements a narrower version of this calculation:

- Reads `references/calendar.json` as the teaching-date sequence.
- Requires frontmatter `first_teaching_day` and `daily_hours`.
- Parses each teaching-content row's trailing integer hour marker.
- Consumes hours across the calendar sequence.
- Derives term week, weekday, row hours, task total hours, and min/max week evidence.

v1.11 should generalize this from the jiaoan-jihua table renderer into a package-level scheduling contract. The contract should accept calendar, first teaching day, daily hours, task/activity/fragment hours, holidays, and makeup teaching days; it should output start/end dates, term weeks, weekdays, assigned hours, and reviewable hour-consumption evidence.

## Question 2: Can teaching plan and lesson plan skills be combined?

Yes, but as a new orchestration skill rather than by deleting or replacing the existing skills.

Current local evidence:

- `skills/jiaoan-jihua/SKILL.md` already defines a teaching-schedule Markdown-to-Typst workflow.
- `skills/jiaoan-shicao/SKILL.md` already defines a practical lesson-plan Markdown-to-Typst workflow.
- Both skills preserve a Markdown intermediate and support Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent adapter notes.
- Both have v1.10 strict Typst conversion evidence in phase records.

v1.11 should create a `teaching-design-package`-style orchestration skill that generates one teacher-reviewable Markdown intermediate, then routes or composes teaching-plan and lesson-plan outputs. Existing skills must remain standalone.

## Question 3: Can end-of-term materials be merged into the same package?

Yes, as an optional module.

Current local evidence:

- `skills/end-of-term-teaching-materials/SKILL.md` defines structured data -> Markdown -> Typst/PDF, manifest, deterministic table artifacts, calculated score evidence, and workbook output.
- `references/workflow-and-artifacts.md` requires the persistent `end-of-term-full.md` review point and the `## 复核标记` export gate.
- It already defines split artifacts such as `end-of-term-package.pdf`, table JSON/CSV files, calculated score data, score summaries, score-list workbook, and teacher-facing scorebook workbook.

v1.11 should integrate this workflow only when requested or enabled by package flags. It must not bypass the end-of-term review gate, must keep workbook/table artifacts discoverable, and should include `end-of-term-package.pdf` plus a combined `teaching-design-package.pdf` when merged output is supported.

## Planning Implications

- Phase 22 should focus on scheduling contract and fixture evidence before broader package orchestration.
- Phase 23 should add the new skill entry, Markdown intermediate, and jiaoan orchestration.
- Phase 24 should attach optional end-of-term artifacts and combined/split package outputs.
- Phase 25 should run regression and documentation/index verification so existing public skill interfaces and runtime adapter coverage stay intact.
