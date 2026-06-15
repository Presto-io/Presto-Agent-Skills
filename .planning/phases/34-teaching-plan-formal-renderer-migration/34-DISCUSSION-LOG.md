# Phase 34: Teaching Plan Formal Renderer Migration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-15
**Phase:** 34-Teaching Plan Formal Renderer Migration
**Areas discussed:** Formal renderer ownership, schedule/hour authority, equivalence evidence and legacy-skill protection

---

## Formal Renderer Ownership

| Option | Description | Selected |
|--------|-------------|----------|
| Package-owned migration | Move accepted `jiaoan-jihua` formal rules into `teaching-design-package` internals and call them from the package path. | ✓ |
| Runtime delegation to old skill | Invoke `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` from package rendering. | |
| Shared renderer refactor now | Create a shared library used by both old skill and package in this phase. | |

**User's choice:** Package-owned migration.
**Notes:** User explicitly required that old `skills/jiaoan-jihua` is read-only reference and not modified, and that package runtime must not depend on a sibling skill.

---

## Schedule And Hour Authority

| Option | Description | Selected |
|--------|-------------|----------|
| Shared package scheduling model | Use unified Markdown `# 授课进度计划`, package `calendar.json`, `first_teaching_day`, and row hours as the only derivation path. | ✓ |
| Renderer-local recalculation | Let the formal table renderer recompute week/day/hour cells independently. | |
| Hand-filled YAML/body dates | Accept manually maintained academic year, semester, date ranges, week, weekday, or totals. | |

**User's choice:** Shared package scheduling model.
**Notes:** User specified that unified Markdown is the only content source, `# 授课进度计划` is the only raw hour source, `calendar.json` lives in the teaching-design-package skill folder, and academic year/semester/date/week/day/hour consumption must be strictly derived.

---

## Equivalence Evidence And Legacy-Skill Protection

| Option | Description | Selected |
|--------|-------------|----------|
| Fixture equivalence with old skill unchanged | Compare generated formal output against accepted `jiaoan-jihua` fixtures/oracles and prove old skill files are unchanged. | ✓ |
| Visual smoke only | Generate a non-empty PDF and rely on visual/manual acceptance. | |
| Rewrite old skill alongside package | Change `skills/jiaoan-jihua` to make equivalence easier. | |

**User's choice:** Fixture equivalence with old skill unchanged.
**Notes:** Equivalence may allow non-semantic provenance/path differences, but not table structure, column widths, row order, week/day/hour facts, or signature/course-info drift.

---

## Claude's Discretion

- Planner may choose the internal implementation shape inside `skills/teaching-design-package/`, as long as it remains package-owned, standalone, testable, and scoped to teaching-plan formal renderer migration.
- Planner may choose strict diff, normalized diff, structural assertions, PDF smoke checks, or a combination for equivalence evidence, but must document allowed differences.

## Deferred Ideas

- Phase 35: `jiaoan-shicao` renderer migration and strict teaching-design activity validation.
- Phase 36: course-name-prefixed public output contract and final PDF merge.
- Future phase: possible shared renderer library after package-owned migration stabilizes.
