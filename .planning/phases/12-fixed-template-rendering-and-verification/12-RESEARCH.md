# Phase 12 Research: Fixed-Template Rendering and Verification

**Milestone:** v1.7 End-of-Term Teaching Materials Skill
**Date:** 2026-06-09
**Status:** Research complete
**Scope:** Repository-internal research only; external research intentionally skipped per `.planning/STATE.md`.

## Question

What does Phase 12 need to plan well so the `end-of-term-teaching-materials` skill can render the Phase 11 Markdown contract into fixed-template Typst/PDF and deterministic table artifacts without expanding into OCR, arbitrary template discovery, or binary-only verification?

## Findings

- Phase 11 already created the durable input contract: `skills/end-of-term-teaching-materials/SKILL.md`, `references/data-contract.md`, and `templates/end-of-term-full.md`.
- Phase 12 must cover ETM-05 through ETM-08: fixed skill-local templates, script code for structured data -> Markdown -> Typst -> PDF, deterministic table artifacts, and runtime adapter verification.
- Existing document skills favor a skill-local shell entry point with explicit subcommands, predictable output paths, `manifest/info/version` support, and optional Typst PDF compilation.
- Workbook generation cannot be verified safely by binary equality alone. The plan should require deterministic companion CSV/JSON artifacts and workbook smoke checks, while treating the `.xlsx` output as a teacher-facing deliverable.
- `openpyxl` is not available in the default local Python environment, so the Phase 12 script plan should not require it as an unpinned ambient dependency. If workbook helper code uses Python, it should use the standard library or document a clear optional dependency and fallback.
- The primary PDF deliverable is one merged printable package controlled by Markdown `package` flags. Per-artifact Typst/PDF files may exist as intermediates, but verification should assert the merged package.
- `## 复核标记` remains a hard export gate. If the section is not exactly `无`, final export verification must fail before claiming readiness.
- Reusable fixtures must be sanitized. User-provided historical materials and desktop template paths are validation references, not raw repository fixtures.

## Decision

Plan Phase 12 as one executable rendering slice:

1. Add skill-local fixed-template references, Typst templates, and sanitized table/workbook fixtures.
2. Add one shell entry point plus helper code that can validate, generate Markdown from structured JSON, render Markdown to Typst, compile a merged PDF when `typst` is available, and emit table artifacts.
3. Emit deterministic review artifacts (`manifest.json`, table JSON, and CSV) alongside teacher-facing workbook/PDF outputs.
4. Update the canonical skill with script usage, dependencies, safety boundaries, runtime adapter notes, and verification.
5. Verify through content checks, fixture generation, repeatability checks, Typst/PDF compile smoke checks, table artifact checks, and adapter-note coverage.

## Implications

- Phase 12 should not add OCR/photo extraction, source-file scraping, arbitrary template packs, or source-to-PDF shortcuts.
- The executor should prefer standard-library helpers where practical; any optional dependency must be documented and must not be silently assumed.
- Workbook fixture verification should inspect required sheets, headers, blanks, formulas or derived fields where present, and companion JSON/CSV consistency.
- The plan must avoid brittle verification that fails simply because docs mention forbidden derived-field names. Checks should target generated Markdown/table artifacts rather than every explanatory document string.
- Human visual/format validation against historical course materials remains supported but not replaced by automated checks.

## Source Notes

- `.planning/phases/12-fixed-template-rendering-and-verification/12-CONTEXT.md`
- `.planning/phases/11-end-of-term-data-and-markdown-contract/11-01-SUMMARY.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `skills/end-of-term-teaching-materials/SKILL.md`
- `skills/end-of-term-teaching-materials/references/data-contract.md`
- `skills/end-of-term-teaching-materials/templates/end-of-term-full.md`
- `skills/gongwen/scripts/gongwen.sh`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
