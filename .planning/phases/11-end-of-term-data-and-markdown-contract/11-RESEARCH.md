# Phase 11 Research: End-of-Term Data and Markdown Contract

**Milestone:** v1.7 End-of-Term Teaching Materials Skill
**Date:** 2026-06-09
**Status:** Research complete
**Scope:** Repository-internal research only; external research intentionally skipped per `.planning/STATE.md`.

## Question

What does Phase 11 need to plan well so the `end-of-term-teaching-materials` skill defines a stable structured-data and Markdown contract without pulling Phase 12 rendering work forward?

## Findings

- Phase 4 already locks the shared document-workflow shape as `YAML frontmatter + body`, with template-specific fields and review-marker syntax owned by each skill.
- Existing document skills keep one concise canonical `SKILL.md`, put reusable templates under `templates/`, and keep long support material under `references/`.
- Phase 11 should create the skill's authoring contract and template, not the renderer. Excel, Typst, PDF, workbook formulas, and deterministic table artifact emission belong to Phase 12.
- The teacher-facing Markdown must be a durable checkpoint: it should not keep hidden `sources` entries, derived grade fields, or renderer-only calculations.
- Review semantics are part of this phase's contract. Values like `87?` must be represented inline, mirrored in `## 复核标记`, and resolved before final export completion.
- The safest structured-data contract is explicit and narrow: course, class, teacher, semester, teaching-hour/task records, assessment records, submission metadata, package flags, and optional handover metadata.

## Decision

Plan Phase 11 as a contract-writing slice:

1. Add `skills/end-of-term-teaching-materials/SKILL.md`.
2. Add a skill-local structured data contract under `skills/end-of-term-teaching-materials/references/`.
3. Add `skills/end-of-term-teaching-materials/templates/end-of-term-full.md`.
4. Update repository skill listings only as needed.
5. Mark ETM-01 through ETM-04 complete only after the files verify against the locked contract.

## Implications

- Phase 11 verification should use file-content checks and Markdown inspection, not renderer output.
- The plan should explicitly block scripts, Excel export, Typst generation, PDF generation, OCR implementation, and source-to-target shortcuts.
- The template should demonstrate aligned Markdown tables and review markers while avoiding real private student data in reusable examples.
- Runtime adapter notes still need all required targets: Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.

## Source Notes

- `.planning/phases/11-end-of-term-data-and-markdown-contract/11-CONTEXT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/04-markdown-normalization-contract/04-CONTEXT.md`
- `docs/markdown-normalization-contract.md`
- `docs/directory-spec.md`
- `docs/compatibility-matrix.md`
- `templates/skill/SKILL.md`
- `skills/gongwen/SKILL.md`
- `skills/jiaoan-shicao/SKILL.md`
- `skills/jiaoan-jihua/SKILL.md`
