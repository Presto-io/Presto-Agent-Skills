# Phase 21: Jiaoan Jihua 授课计划 1:1 Typst Conversion - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-14
**Phase:** 21-Jiaoan Jihua 授课计划 1:1 Typst Conversion
**Areas discussed:** Scope and ownership, Target Typst shape, Scheduling and hours, Verification

---

## Scope and Ownership

| Option | Description | Selected |
|--------|-------------|----------|
| Skill-local only | Update only `skills/jiaoan-jihua/` support files and scripts. | ✓ |
| Cross-skill shared renderer | Introduce shared jiaoan infrastructure used by Phase 20 and Phase 21. | |
| External renderer | Delegate Markdown-to-Typst conversion to renderer code outside the skill directory. | |

**User's choice:** Skill-local only, from the command boundary and v1.10 requirements.
**Notes:** The user explicitly said not to modify Phase 20's skill directory. Requirements also defer shared infrastructure and require skill-internal script code.

---

## Target Typst Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Exact official Typst fixture | Emit the official table template bytes required by `test/1.10/电气设备控制线路安装与调试授课计划.typ`. | ✓ |
| Generic semantic Typst | Preserve the current heading/paragraph renderer and accept semantic similarity. | |
| Visual-only approximation | Produce a visually similar PDF while allowing Typst source differences. | |

**User's choice:** Exact official Typst fixture.
**Notes:** Phase 21 says generated Typst must strictly match the target `.typ`; visual or semantic approximation is insufficient.

---

## Scheduling and Hours

| Option | Description | Selected |
|--------|-------------|----------|
| Derive from Markdown and calendar | Parse `-N` hour suffixes, `first_teaching_day`, `daily_hours`, and `calendar.json` to emit week/day/hour cells. | ✓ |
| Hard-code target rows | Special-case the fixture output without preserving a meaningful Markdown-to-table conversion path. | |
| Ask for manual schedule metadata | Require extra user input beyond the provided fixture. | |

**User's choice:** Derive from Markdown and calendar.
**Notes:** This keeps the existing skill contract meaningful while still targeting strict fixture equivalence.

---

## Verification

| Option | Description | Selected |
|--------|-------------|----------|
| Strict diff plus hash | Compare generated Typst against target with byte-level evidence. | ✓ |
| PDF visual review only | Compile/check PDF appearance but do not require Typst source equality. | |
| Script success only | Treat successful render command as enough. | |

**User's choice:** Strict diff plus hash.
**Notes:** Baseline discussion run showed current output differs: target SHA-256 `0d681cca76cb7d6edaf7b0c76874f3f8a5b3f49ab5e00904caf9a106690e138b`; current generated SHA-256 `0e332451a2abeaa16c660f8de928d19176f444676a8b607fc3d9fd7d1348256d`.

---

## Claude's Discretion

- Planner/executor may choose the exact internal parser/emitter structure inside `skills/jiaoan-jihua/scripts/`.
- Planner/executor may decide whether supporting documentation changes are necessary, provided `SKILL.md` stays concise and runtime adapter notes remain visible.

## Deferred Ideas

- Arbitrary third-party教案/授课计划 conversion beyond the supplied fixture.
- Shared jiaoan rendering infrastructure across both jiaoan skills.
- PDF visual acceptance after strict Typst equivalence is stable.
