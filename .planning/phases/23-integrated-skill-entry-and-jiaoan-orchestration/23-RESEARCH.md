# Phase 23: Integrated Skill Entry and Jiaoan Orchestration - Research

**Date:** 2026-06-14
**Command:** `/gsd:plan-phase 23 --auto`
**Status:** Complete

## Research Question

What must be known to plan Phase 23 well, without implementing the new skill during planning?

Phase 23 should create the executable plan for a minimal `teaching-design-package` orchestration slice. The slice must introduce a new skill entry, preserve the existing `jiaoan-jihua` and `jiaoan-shicao` skills, define a persistent package Markdown checkpoint, compose module-local teaching-plan and lesson-plan intermediates, and plan split Typst/PDF output behavior while leaving optional end-of-term and combined-package work to later phases.

## Source Evidence Read

- `AGENTS.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/PROJECT.md`
- `.planning/STATE.md`
- `.planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-CONTEXT.md`
- `.planning/phases/22-scheduling-contract-and-fixture/22-CONTEXT.md`
- `.planning/phases/22-scheduling-contract-and-fixture/22-SUMMARY.md`
- `.planning/phases/22-scheduling-contract-and-fixture/22-VERIFICATION.md`
- `references/scheduling-contract.md`
- `docs/markdown-normalization-contract.md`
- `docs/directory-spec.md`
- `docs/compatibility-matrix.md`
- `templates/skill/SKILL.md`
- `skills/README.md`
- `skills/jiaoan-jihua/SKILL.md`
- `skills/jiaoan-jihua/references/format-and-rendering.md`
- `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
- `skills/jiaoan-shicao/SKILL.md`
- `skills/jiaoan-shicao/references/format-and-rendering.md`
- `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`

## Findings

### Phase Boundary

- Phase 23 maps to TDP-05 through TDP-09.
- Phase 23 should add the new `skills/teaching-design-package/` skill path, define the package Markdown intermediate, and prove orchestration with the two jiaoan modules.
- Phase 23 must not delete, rename, replace, or change public commands of `skills/jiaoan-jihua` or `skills/jiaoan-shicao`.
- Optional `end-of-term-teaching-materials`, default combined `teaching-design-package.pdf`, workbook/table package discovery, and full regression/documentation gates remain Phase 24 and Phase 25 work.

### Existing Skill Contracts

- `jiaoan-jihua` normalizes teaching-schedule content to `jiaoan-jihua-full.md`, then renders `.typ` through `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render`.
- `jiaoan-jihua` uses `first_teaching_day`, optional `daily_hours`, ordered `##` tasks, `###` stages, and `text-N` hour rows. Its renderer consumes rows in source order.
- `jiaoan-shicao` normalizes practical lesson-plan material to `jiaoan-shicao-full.md`, then renders `.typ` through `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render`.
- `jiaoan-shicao` preserves a fixed three-part structure: `学习任务分析`, `教学活动设计`, and `学业评价`. Missing or uncertain fields should remain blank or review-marked.
- Both existing skills already include runtime adapter notes for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.

### Scheduling Contract

- Phase 22 created `references/scheduling-contract.md` and deterministic fixture evidence under `test/1.11/scheduling-contract/`.
- The package should consume Phase 22's package-level scheduling model rather than exposing `jiaoan-jihua.sh` internals as its public API.
- Required schedule evidence includes `calendar.dates`, `calendar.holidays`, `calendar.makeup_days`, `first_teaching_day`, `daily_hours`, ordered `items[]`, derived start/end dates, term week, weekday, assigned hours, `hour_consumption[]`, and `review_markers[]`.
- Uncertain, missing, conflicting, or exhausted inputs must become teacher-reviewable markers near affected items and under `## 复核标记`.

### Repository Patterns

- `SKILL.md` should remain a concise semantic entry, with long rules in `references/`, scripts in `scripts/`, and copyable intermediates in `templates/`.
- Document workflows must normalize source material to persistent Markdown before rendering target artifacts.
- Runtime-specific behavior belongs in `Runtime Adapter Notes`, not in canonical workflow body text.
- New skill discovery should update `README.md`, `skills/README.md`, and possibly `docs/compatibility-matrix.md`; directory rules already support the intended layout.

## Recommended Plan Shape

Use one executable Phase 23 plan with five tasks:

1. Add the `teaching-design-package` skill entry and long orchestration reference.
2. Add the package Markdown template and define module handoff blocks.
3. Add a small skill-local script that can create/validate package artifacts, generate module-local intermediates, invoke existing jiaoan render paths for split Typst, and record honest PDF status.
4. Add deterministic fixture/verification evidence for orchestration without depending on end-of-term or combined PDF behavior.
5. Wire repository discoverability and run source/runtime/smoke verification.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| The new skill duplicates existing jiaoan manuals in its entry file. | Keep `SKILL.md` concise and link to `references/format-and-orchestration.md` plus existing jiaoan references. |
| The package claims PDF success when only `.typ` was generated. | Manifest/status must distinguish Typst generation from PDF compilation; PDF status only passes after an explicit compile command succeeds. |
| Existing public command surfaces drift. | Add verification that `skills/jiaoan-jihua/SKILL.md` and `skills/jiaoan-shicao/SKILL.md` remain unchanged unless a later executor records a deliberate docs-only cross-reference. |
| Runtime-private syntax enters the canonical workflow. | Adapter coverage grep should confirm all six runtime names appear; canonical process should avoid Claude/Codex-specific tool names outside notes. |
| End-of-term or combined package scope leaks into Phase 23. | The plan must explicitly defer `end-of-term-package.pdf`, workbook/table module integration, and combined `teaching-design-package.pdf` to Phase 24. |

## Research Complete

Local research is sufficient. No external web research is required because Phase 23 depends on local repository contracts, existing shipped jiaoan skills, and Phase 22 scheduling evidence.
