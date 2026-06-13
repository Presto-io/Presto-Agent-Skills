# Phase 24 Research: Optional End-of-Term Module and Package Outputs

**Phase:** 24 - Optional End-of-Term Module and Package Outputs
**Date:** 2026-06-14
**Mode:** local repository research for `/gsd:plan-phase 24 --auto`

## Research Question

What does the executor need to know to plan Phase 24 well without reimplementing the existing `end-of-term-teaching-materials` skill or breaking the Phase 23 `teaching-design-package` contract?

## Sources Read

- `.planning/phases/24-optional-end-of-term-module-and-package-outputs/24-CONTEXT.md`
- `.planning/phases/22-scheduling-contract-and-fixture/22-SUMMARY.md`
- `.planning/phases/22-scheduling-contract-and-fixture/22-VERIFICATION.md`
- `.planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-SUMMARY.md`
- `.planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-VERIFICATION.md`
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/end-of-term-teaching-materials/SKILL.md`
- `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md`
- `skills/end-of-term-teaching-materials/references/data-contract.md`
- `skills/end-of-term-teaching-materials/references/rendering-style.md`
- `skills/end-of-term-teaching-materials/references/cover-template-notes.md`
- `skills/end-of-term-teaching-materials/references/scorebook-template-notes.md`
- `skills/end-of-term-teaching-materials/templates/end-of-term-full.md`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`
- `skills/end-of-term-teaching-materials/scripts/render_package.py`
- `skills/end-of-term-teaching-materials/scripts/end_of_term/_engine.py`
- `test/1.11/teaching-design-package/expected-manifest.json`
- `test/1.11/teaching-design-package/expected-review.md`

## Existing Package Contract

Phase 23 created `skills/teaching-design-package` as a portable orchestration skill. It currently owns:

- A concise canonical `SKILL.md`.
- `references/format-and-orchestration.md` for long package rules.
- `templates/teaching-design-package-full.md` as the teacher-reviewable package checkpoint.
- `scripts/teaching-design-package.sh` with `example`, `plan-split`, `render-split`, `manifest`, `info`, and `version`.
- Manifest keys for `teaching_plan_typ`, `lesson_plans_typ`, `teaching_plan_pdf`, `lesson_plans_pdf`, `review_markers`, and `final_ready`.

The helper already records Phase 24 as deferred for optional end-of-term module behavior, `end-of-term-package.pdf`, and combined `teaching-design-package.pdf`. Phase 24 should replace that deferral with explicit optional-module status and output behavior while preserving the existing command surface.

## Existing End-of-Term Contract

`end-of-term-teaching-materials` already owns the module internals:

- Structured data contract in `references/data-contract.md`.
- Markdown checkpoint `end-of-term-full.md`.
- Public commands: `example`, `validate`, `markdown`, `render`, `verify`, `manifest`, `info`, and `version`.
- Normal final export requires `## 复核标记` to be exactly `无`.
- `render --abnormal-review` is inspection-only and must keep `artifact_kind: abnormal_review`, `final_ready: false`, and `review_cleared: false`.
- Output artifacts include `end-of-term-package.typ`, `end-of-term-package.pdf`, module `manifest.json`, deterministic `tables/*` evidence, `score-list.xlsx`, and `scorebook.xlsx`.

The package skill must orchestrate or point to these outputs. It must not copy score calculation, workbook generation, review-marker resolution, or Typst rendering logic into `teaching-design-package`.

## Planning Implications

1. Add optional-module documentation and manifest fields to the package contract.
2. Add template fields/sections that make `end-of-term-full.md` discoverable without duplicating the full end-of-term template.
3. Extend the package helper with optional end-of-term orchestration and honest combined-output status.
4. Add deterministic fixture expectations for enabled, disabled, blocked-review, split-only, and merge-unavailable behavior.
5. Keep broad regression of all public skills and documentation indexes for Phase 25, except for narrow smoke checks needed to prove Phase 24 behavior.

## Status Vocabulary

The plan should prefer explicit status values:

- `disabled`
- `planned`
- `not_run`
- `passed`
- `failed`
- `missing_compiler`
- `merge_unavailable`
- `blocked_review`

`final_ready` should be derived from selected modules and actual artifacts, not manually asserted.

## Risks

- False success: claiming `teaching-design-package.pdf` exists because Typst outputs exist.
- Logic duplication: reimplementing score or workbook behavior in the package helper.
- Gate bypass: clearing package-level review markers while the module-local `end-of-term-full.md` still blocks export.
- Runtime drift: relying on hidden script discovery, implicit writable directories, or agent-private syntax.
- Scope creep: moving Phase 25 public-command regression or documentation-index verification into Phase 24.

## Research Complete

Phase 24 can be planned as one executable plan with four implementation tasks and one verification/documentation boundary task. No external web research is needed; the required behavior is locked by local phase evidence and existing skill contracts.
