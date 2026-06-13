# Phase 23: Integrated Skill Entry and Jiaoan Orchestration - Pattern Map

**Date:** 2026-06-14
**Status:** Complete

## Purpose

This pattern map identifies the local files and behavior that the Phase 23 executor should reuse when implementing the future `teaching-design-package` skill. It is planning evidence only; no implementation files are created by this plan-phase run.

## Files to Reuse

| Target Concern | Existing Pattern | What to Reuse |
|----------------|------------------|---------------|
| New skill entry shape | `templates/skill/SKILL.md` | Frontmatter fields, concise Objective/Use When/Inputs/Process/Outputs/Verification/Safety sections, and six-runtime adapter table. |
| Skill index wording | `skills/README.md` | Short current-skill bullets and artifact contract discovery table. |
| Contributor-facing discovery | `README.md` | Existing skill list, shared reference section, and "如何添加新技能" guidance. |
| Directory placement | `docs/directory-spec.md` | `skills/<skill-name>/SKILL.md`, `references/`, `scripts/`, `templates/`, and root `references/` ownership rules. |
| Markdown-first contract | `docs/markdown-normalization-contract.md` | Persistent `YAML frontmatter + body` intermediate before target generation; ambiguous fragments stay visible. |
| Runtime coverage | `docs/compatibility-matrix.md` and existing jiaoan `SKILL.md` files | Required runtime set and adapter-note concerns for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, Hermes Agent. |
| Shared scheduling | `references/scheduling-contract.md` | Package-level inputs, derived outputs, source-order consumption, review-marker behavior, and teacher-readable evidence vocabulary. |
| Teaching-plan module | `skills/jiaoan-jihua/SKILL.md`, `references/format-and-rendering.md`, `templates/jiaoan-jihua-full.md`, `scripts/jiaoan-jihua.sh` | Teaching-plan Markdown shape, public render command, Typst-only generation, calendar support, and no target-copy rule. |
| Lesson-plan module | `skills/jiaoan-shicao/SKILL.md`, `references/format-and-rendering.md`, `templates/jiaoan-shicao-full.md`, `scripts/jiaoan-shicao.sh` | Practical lesson-plan Markdown shape, public render command, optional calendar output, and review-marker safety. |
| Scheduling fixture evidence | `test/1.11/scheduling-contract/expected-schedule.md` and `.json` | Teacher-readable `## 调度证据` plus `## 复核标记`; machine-readable `hour_consumption[]` style. |

## Proposed Package Data Flow

1. Source material is normalized to `teaching-design-package-full.md`.
2. Package-level metadata and scheduling inputs become the single source of truth.
3. The package intermediate stores `## 调度证据`, `## 授课计划`, `## 实操教案`, `## 输出清单`, and `## 复核标记`.
4. The package script materializes module-local intermediates:
   - `jiaoan-jihua-full.md` for teaching-plan content.
   - `jiaoan-shicao-full.md` for lesson-plan content.
5. The package script invokes existing render commands:
   - `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render --input <module-md> --typ <teaching-plan.typ>`
   - `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --input <module-md> --typ <lesson-plans.typ>`
6. The package records split-output status:
   - `teaching-plan.typ` and `lesson-plans.typ` are generated when render commands pass.
   - `teaching-plan.pdf` and `lesson-plans.pdf` are only marked passed if an explicit PDF compile command runs and produces files.
   - Combined `teaching-design-package.pdf` remains deferred to Phase 24.

## Executor Notes

- Keep original jiaoan skill directories standalone and callable.
- Do not move existing jiaoan format rules into the new skill entry.
- Prefer one long package reference, such as `skills/teaching-design-package/references/format-and-orchestration.md`.
- Prefer one copyable package template, `skills/teaching-design-package/templates/teaching-design-package-full.md`.
- If a script is added, keep it skill-local under `skills/teaching-design-package/scripts/` and make its help text explicit about review markers and partial output status.
