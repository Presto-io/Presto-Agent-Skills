# Phase 12: Fixed-Template Rendering and Verification - Context

**Gathered:** 2026-06-09
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase turns the Phase 11 `end-of-term-full.md` contract into fixed-template outputs for the `end-of-term-teaching-materials` skill. It adds skill-local Typst templates, fixed package resources, rendering scripts, deterministic table artifacts, PDF compilation, and verification.

Phase 12 does not redesign the Markdown contract, does not add OCR/photo extraction, does not infer arbitrary templates, and does not bypass the review loop. Historical course materials may be used as electronic validation input, but the phase should treat the data as already extracted and should not add image-recognition scope.

</domain>

<decisions>
## Implementation Decisions

### Table Artifact Shape
- **D-01:** Phase 12 should produce both delivery-oriented table artifacts and review/diff-oriented table artifacts. The score-book workbook remains the main teacher-facing table output, while deterministic companion artifacts such as CSV and/or JSON should be emitted for inspection and automated verification.
- **D-02:** The score-book workbook should prefer filling a fixed `.xlsx` template while preserving layout, merged cells, formulas, and styles from the provided score-book style.
- **D-03:** Deterministic companion table artifacts should make verification practical without depending only on binary workbook comparison. Planner and executor may choose the exact companion format mix, but the verification path must prove that generated table data matches the Markdown source.
- **D-04:** Blank score cells remain blank in all table artifacts. Declared task columns are preserved even when an entire task column is blank. Derived fields remain renderer/workbook formula responsibilities, not Markdown source fields.

### PDF Package Shape
- **D-05:** PDF output should be one merged complete printable package, not only separate per-artifact PDFs.
- **D-06:** The merged PDF package should respect `package` flags from Markdown. Artifacts set to `false` are omitted. `交接班记录封面` still requires handover metadata; if it is requested but handover metadata is absent, the renderer should skip it with a clear warning or manifest entry rather than guessing.
- **D-07:** Intermediate per-artifact Typst/PDF files may be generated internally if useful, but the primary user-facing PDF deliverable is the complete merged package.
- **D-08:** The PDF package should include the redesigned score-book cover, score-book body, score summary, score analysis, teaching-log cover, process-assessment cover, and handover cover only when enabled and data requirements are satisfied.

### Fixed Template Resources
- **D-09:** Phase 12 should add skill-local Typst templates under `skills/end-of-term-teaching-materials/`.
- **D-10:** Phase 12 should add style references that explain the fixed visual rules used by the generated package.
- **D-11:** Phase 12 should add an `.xlsx` fixture derived from the score-book template style so workbook generation and verification can be exercised in-repo.
- **D-12:** Phase 12 should add extracted notes for the `.docx` cover reference, describing the cover structure/style used by the Typst/PDF cover templates.
- **D-13:** Reusable fixtures and references must avoid committing private real-course paths, raw sensitive student data, credentials, or hidden source lists. If real historical course materials are used during manual validation, keep reusable repository fixtures sanitized.

### Validation And Human Format Check
- **D-14:** The user will provide historical electronic course materials for validation. Treat those inputs as already-extracted structured data, roster data, score data, and analysis text.
- **D-15:** The user will perform final format validation against those historical course materials. Automated checks should support that review by proving deterministic generation, artifact presence, source-data consistency, and compile success; they should not try to replace the user's visual/format judgment.
- **D-16:** The verification path should cover data validation, Markdown generation, review-marker blocking, Typst generation, PDF compilation, merged PDF package creation, table artifact generation, and required runtime adapter notes.
- **D-17:** Verification should also include workbook/table smoke checks where practical: required sheets or files exist, formulas or derived fields are preserved where expected, companion CSV/JSON matches Markdown rows, and generated outputs are deterministic for the same sanitized fixture.
- **D-18:** If `## 复核标记` is not exactly `无`, final export verification must fail or stop before claiming the package is ready.

### Script Entry Points
- **D-19:** The skill should expose a clear script entry point under `skills/end-of-term-teaching-materials/scripts/` that can validate input, generate Markdown from structured data, render Markdown to Typst, compile a merged PDF package, emit table artifacts, and run verification.
- **D-20:** Existing document skills use shell script entry points, but Phase 12 may choose the smallest reliable implementation language or helper stack needed for workbook handling. Any external command, dependency, or runtime requirement must be documented in `SKILL.md`, safety notes, and verification steps.
- **D-21:** Runtime adapter notes must be updated for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent. OpenClaw and Hermes Agent notes must explicitly mention script execution, file-write permissions, fixture verification, and fallback behavior when a runtime cannot automatically discover scripts.

### Claude's Discretion
Planner and executor may choose exact filenames, internal parser implementation, generated manifest schema, companion table format details, and whether to generate intermediate per-artifact files before merging. Those choices must preserve the decisions above and the Phase 11 Markdown contract.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Planning
- `.planning/ROADMAP.md` — Defines Phase 12 goal, ETM-05 through ETM-08, and success criteria.
- `.planning/REQUIREMENTS.md` — Defines v1.7 requirements, deferred requirements, and out-of-scope boundaries.
- `.planning/PROJECT.md` — Defines the v1.7 milestone purpose and Markdown-first document workflow constraints.
- `.planning/STATE.md` — Records current workflow state and the Phase 11-to-Phase 12 handoff.
- `.planning/phases/11-end-of-term-data-and-markdown-contract/11-CONTEXT.md` — Locks the `end-of-term-full.md` Markdown contract, package flags, review loop, Excel expectations, and PDF package expectations.
- `.planning/phases/04-markdown-normalization-contract/04-CONTEXT.md` — Locks `YAML frontmatter + body` as the shared document-workflow intermediate.

### Repository Contract
- `docs/markdown-normalization-contract.md` — Defines persistent reviewable Markdown and explicit review markers for ambiguous or lossy content.
- `docs/directory-spec.md` — Defines skill-local placement for `SKILL.md`, `templates/`, `scripts/`, and `references/`.
- `templates/skill/SKILL.md` — Canonical skill template and runtime adapter notes structure.
- `docs/compatibility-matrix.md` — Required runtime compatibility expectations.

### End-of-Term Skill
- `skills/end-of-term-teaching-materials/SKILL.md` — Current skill process, review-loop contract, runtime notes, verification, and safety boundaries.
- `skills/end-of-term-teaching-materials/references/data-contract.md` — Structured data and Markdown contract for metadata, package flags, roster, tasks, scores, analysis, and review markers.
- `skills/end-of-term-teaching-materials/templates/end-of-term-full.md` — Current Markdown intermediate fixture/template.

### Existing Concrete Skills
- `skills/gongwen/SKILL.md` — Existing Markdown-to-Typst/PDF skill pattern with script usage and runtime adapter notes.
- `skills/gongwen/scripts/gongwen.sh` — Existing shell renderer with optional Typst PDF compilation and fixture verification pattern.
- `skills/jiaoan-shicao/SKILL.md` — Existing teaching-document skill with skill-local templates/scripts.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` — Existing Markdown-to-Typst renderer pattern.
- `skills/jiaoan-jihua/SKILL.md` — Existing teaching-schedule skill and skill-local support-resource pattern.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` — Existing Markdown-to-Typst renderer pattern.

### User-Provided Template Materials
- `/Users/mrered/Desktop/教学/电气设备控制线路安装与调试/记分册 示例电气2.xlsx` — Provided score-book workbook template and data example; use as style/formula reference, not as a raw reusable repository fixture unless sanitized or derived.
- `/Users/mrered/Desktop/教学/电气设备控制线路安装与调试/教学日志 过程考核评价表 封面 示例电气2.docx` — Provided cover style reference; use extracted notes to guide Typst/PDF covers.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/end-of-term-teaching-materials/SKILL.md`: Current canonical skill body for Phase 11; Phase 12 should update it with rendering script usage, outputs, verification, and runtime adapter details.
- `skills/end-of-term-teaching-materials/references/data-contract.md`: Stable source contract for package flags, roster, tasks, score fields, analysis sections, and review markers.
- `skills/end-of-term-teaching-materials/templates/end-of-term-full.md`: Current Markdown fixture/template to drive rendering and verification.
- `skills/gongwen/scripts/gongwen.sh`: Demonstrates optional `--pdf` compilation, `--expected-typ` verification, manifest command, and Bash-style script ergonomics.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` and `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`: Demonstrate lightweight skill-local Markdown-to-Typst renderers.

### Established Patterns
- New skill code and resources stay under `skills/<skill-name>/`.
- Runtime-specific behavior belongs in `Runtime Adapter Notes`, not duplicated runtime-specific skill files.
- Markdown remains the persistent reviewable source of truth before rendering.
- Scripts should expose repeatable commands and verification steps, and should document external dependencies and file-write boundaries.
- Existing concrete skills favor deterministic fixtures and black-box command verification over subjective visual automation.

### Integration Points
- Add `skills/end-of-term-teaching-materials/scripts/`.
- Add skill-local Typst templates and style references under `skills/end-of-term-teaching-materials/`.
- Add sanitized workbook/table fixtures under `skills/end-of-term-teaching-materials/` in a clear subdirectory chosen during planning.
- Update `skills/end-of-term-teaching-materials/SKILL.md` with render/export/verify commands.
- Extend verification to cover Markdown, review blockers, Typst, merged PDF, deterministic table artifacts, workbook/table smoke checks, and runtime adapter notes.

</code_context>

<specifics>
## Specific Ideas

- The user wants both workbook-style table outputs and deterministic review artifacts.
- The primary PDF deliverable should be one merged complete printable package.
- Template resources should include Typst templates, style references, an `.xlsx` fixture, and extracted `.docx` cover-reference notes.
- The user will validate final formatting using historical electronic course materials; the implementation should treat the data as already extracted rather than implement OCR/photo parsing.
- Automated verification should support manual format validation without attempting to replace it.

</specifics>

<deferred>
## Deferred Ideas

- OCR, handwriting/photo recognition, and automatic extraction from images remain out of scope for Phase 12.
- Generic school template marketplaces and arbitrary form discovery remain deferred.
- DOCX or spreadsheet-native exports beyond the fixed workbook/table artifacts remain deferred unless required by the fixed package plan.

</deferred>

---

*Phase: 12-Fixed-Template Rendering and Verification*
*Context gathered: 2026-06-09*
