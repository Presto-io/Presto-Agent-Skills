# Phase 29: PDF Parity and Standalone Regression - Context

**Gathered:** 2026-06-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 29 completes the v1.13 acceptance gate for `teaching-design-package` after Phase 28's Markdown baseline ingestion and Typst generation. This phase must turn the Phase 28 handoffs and Typst artifacts into three real PDF artifacts: `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf`.

The phase also proves that split package outputs match the old standalone `jiaoan-jihua` and `jiaoan-shicao` skills for the same source scope, allowing only timestamp differences. The combined package PDF must behave as the original teaching-plan PDF and lesson-plan PDF merged into one package, without dropping required content.

Phase 29 is an output and regression phase. It must not redesign the teacher-facing package Markdown baseline, must not move derived scheduling facts back into package YAML, and must not break or replace the standalone `jiaoan-jihua` and `jiaoan-shicao` public interfaces. It should use Phase 28's generated Markdown handoffs, split Typst files, package Typst, and manifest provenance as the starting point, then add honest PDF compilation, merge, and parity evidence.

</domain>

<decisions>
## Implementation Decisions

### PDF Generation Path

- **D-01:** Treat Phase 28 `render-package` output as the canonical package starting point. Phase 29 should call the public package path against `skills/teaching-design-package/templates/teaching-design-package-full.md`, then compile the generated split Typst files into `teaching-plan.pdf` and `lesson-plans.pdf`.
- **D-02:** Use Typst CLI compilation as the first-choice PDF path. If `typst` is missing, exits non-zero, or cannot download/import a required package such as `@preview/cuti:0.2.1`, the workflow must record `missing_compiler` or `failed` with exact stderr and must not claim PDF success.
- **D-03:** The accepted split PDF filenames are `teaching-plan.pdf` and `lesson-plans.pdf` in the same output directory as `teaching-plan.typ`, `lesson-plans.typ`, `teaching-design-package.typ`, and `teaching-design-package-manifest.json`.
- **D-04:** The combined PDF filename is `teaching-design-package.pdf`. It should be produced by merging the accepted split PDFs in source order: teaching plan first, lesson plans second. Optional end-of-term PDFs are not part of the current Phase 29 acceptance unless an existing command includes them without changing scope.
- **D-05:** Prefer existing merge support already present in `teaching-design-package.sh`: `pdfunite` first, then `qpdf`. If neither exists, record `merge_unavailable` and fail the combined-PDF acceptance honestly rather than writing a placeholder.
- **D-06:** Do not commit generated PDFs, Typst smoke outputs, or `deliverables/` artifacts as source. Phase 29 verification outputs should live under `/tmp` or in deliberate phase evidence text such as `29-VERIFICATION.md`. Commit source/docs/tests/evidence only.

### Standalone Parity Definition

- **D-07:** Define `teaching-plan.pdf` parity as: package-generated `jiaoan-jihua-full.md` rendered through the same standalone `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render` path yields Typst/PDF content and layout equivalent to invoking standalone `jiaoan-jihua` directly on that same generated handoff. Timestamp or generated-at metadata may differ; visible document content and format must not.
- **D-08:** Define `lesson-plans.pdf` parity as: package-generated `jiaoan-shicao-full.md` rendered through the same standalone `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render` path yields Typst/PDF content and layout equivalent to invoking standalone `jiaoan-shicao` directly on that same generated handoff. Timestamp or generated-at metadata may differ; visible document content and format must not.
- **D-09:** Parity should be proven at the strongest stable layer first. Compare package split Typst against standalone-generated Typst from the exact handoff files, normalizing only explicitly allowed volatile timestamp lines if they exist. If Typst is byte-identical after normalization, compile both sides and verify the PDFs exist.
- **D-10:** PDF parity evidence should not rely only on file existence. Use available local tools to add at least one content/layout check: PDF text extraction, page-count comparison, file metadata normalization, visual raster comparison, or deterministic structural checks. If those tools are missing, record the missing tool and keep the claim bounded to Typst parity plus successful PDF compilation.
- **D-11:** The phrase "same source scope" means the same Phase 28-generated handoff Markdown: `jiaoan-jihua-full.md` for the plan and `jiaoan-shicao-full.md` for lesson plans. Do not compare against unrelated old fixture Markdown unless it is explicitly used as a separate regression smoke check.
- **D-12:** Because package rendering composes the standalone skills, Phase 29 should prefer black-box command comparisons over inspecting internals. The package output and standalone output should be generated in separate temp directories from the same handoff inputs, then compared.

### Combined Package PDF Definition

- **D-13:** The combined package PDF passes only when an actual `teaching-design-package.pdf` file exists after an explicit merge/compile command and contains both accepted split outputs in order.
- **D-14:** Combined PDF verification should prove that required content from both halves is present. Minimum content anchors include `授课进度计划`, `教学设计方案`, the three task names, and representative lesson-plan section anchors such as `学习任务分析`, `教学活动设计`, and `学业评价`.
- **D-15:** Page count is a useful guard: the combined PDF page count should equal the sum of accepted split PDF page counts when the merge tool preserves pages. If page-count tooling is unavailable, record that gap and rely on content anchors plus merge status.
- **D-16:** Do not accept a combined PDF generated from stale split PDFs. The manifest/provenance should link `source_markdown`, split Typst, split PDFs, combined PDF, and command status from the same output directory.

### Derived Fact Verification in PDFs

- **D-17:** Phase 29 must verify the displayed PDF content still carries Phase 28 derived scheduling facts: `160H`, task totals `40H`, `60H`, `60H`, date ranges `5月11日——5月15日`, `5月18日——5月27日`, `5月27日——6月5日`, and `2025-2026学年第二学期`.
- **D-18:** These facts must be traced to Phase 28 provenance rather than manual package YAML. Verification should re-run or inspect the Phase 28 checks showing forbidden package YAML fields remain absent: `total_hours`, `school_year`, `semester`, `daily_hours`, `hour_unit`, `date_display_format`, `date_locale`, `calendar_source`, `holidays`, `makeup_days`, `source_of_truth`, `outputs`, and `validation`.
- **D-19:** If PDF text extraction cannot see a fact because of font encoding or extraction limitations, verification may use generated Typst plus successful PDF compilation as the trace, but it must say the PDF text extractor could not confirm the string. Do not silently downgrade the check.
- **D-20:** Activity-hour mapping evidence from Phase 28 must remain present in handoff/manifest/provenance. If any activity-hour mapping becomes non-final or review-needed, Phase 29 must fail final PDF acceptance or mark it non-final.

### Standalone Public Interface Regression

- **D-21:** Keep `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` public commands stable: `example`, `render`, `manifest`, `info`, and `version`, with the existing `--input`, `--typ`, and `--expected-typ` render behavior.
- **D-22:** Keep `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` public commands stable: `example`, `render`, `manifest`, `info`, and `version`, with the existing `--input`, `--typ`, and `--expected-typ` render behavior.
- **D-23:** Do not require standalone callers to pass `teaching-design-package` Markdown or package-specific flags. Any package-only orchestration should remain inside `skills/teaching-design-package/scripts/teaching-design-package.sh`.
- **D-24:** If Phase 29 adds package PDF commands or flags, document them in `skills/teaching-design-package/SKILL.md` and `skills/teaching-design-package/references/format-and-orchestration.md` while keeping canonical guidance portable across Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.

### Failure and Tooling Honesty

- **D-25:** Missing `typst`, `pdfunite`, `qpdf`, `pdftotext`, `pdfinfo`, ImageMagick, or other optional verification tools must be explicit evidence, not hidden assumptions. Only required tools for the chosen acceptance path may block; optional checks may be recorded as unavailable with residual risk.
- **D-26:** If Typst compilation requires network access for preview packages and the environment is offline, stop with exact error evidence. Do not vendor packages, change templates, or retry networking without explicit user approval.
- **D-27:** Manifest statuses must reflect real files: PDF `passed` only when the corresponding file exists after the command, `not_run` when not attempted, `missing_compiler` when the compiler is absent, `merge_unavailable` when no merge tool exists, and `failed` when a command ran but did not produce the expected file.
- **D-28:** Run `git diff --check` and `git diff --cached --check` before committing. Stage only Phase 29 discussion/planning/evidence/source files; never use `git add .`.

### Claude's Discretion

- Prefer a small extension to the existing package script over introducing a separate PDF orchestration framework.
- Prefer comparing generated Typst first because it is deterministic and closer to the standalone renderers; use PDF-level checks to prove compilation and merge integrity.
- Prefer temp directories under `/tmp/tdp-phase29.*` for black-box verification so generated artifacts do not pollute the repository.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Requirements

- `AGENTS.md` — Repository language, editing, skill authoring, GSD workflow, and OpenClaw/Hermes requirements.
- `.planning/PROJECT.md` — Captures active v1.13 scope, Markdown baseline discipline, derived scheduling discipline, and standalone teaching-skill discipline.
- `.planning/REQUIREMENTS.md` — Locks TDBR-06 through TDBR-11 for Phase 29 and carries TDBR-12 through TDBR-17 as required PDF evidence.
- `.planning/ROADMAP.md` — Defines Phase 29 goal, dependency on Phase 28, success criteria, and active milestone scope.
- `.planning/STATE.md` — Records Phase 28 completion and v1.13 state.

### Prior Phase Evidence

- `.planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-CONTEXT.md` — Phase 28 decisions for baseline slicing, derived scheduling facts, package Typst provenance, and Phase 29 PDF slots.
- `.planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-PLAN.md` — Phase 28 plan and verification command patterns that Phase 29 should extend rather than repeat blindly.
- `.planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-VERIFICATION.md` — Evidence that Phase 28 generated handoffs and Typst artifacts, kept the baseline unchanged, and left PDF slots as non-passed.
- `.planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-01-SUMMARY.md` — Summary of Phase 28 outputs, commits, and known intentional `not_run` PDF slots.
- `.planning/phases/27-official-activity-table-width-alignment/27-CONTEXT.md` — Official `jiaoan-shicao` table-width behavior and PDF/tooling honesty expectations.
- `.planning/phases/26-package-date-backfill-repair/26-CONTEXT.md` — Package handoff/date backfill decisions and generated artifact discipline.

### Package and Standalone Skill Contracts

- `skills/teaching-design-package/templates/teaching-design-package-full.md` — Maintained teacher-facing baseline Markdown; must remain unchanged in structure.
- `skills/teaching-design-package/scripts/teaching-design-package.sh` — Existing package command surface, manifest status logic, split Typst generation, and PDF merge helper candidates.
- `skills/teaching-design-package/SKILL.md` — Canonical package skill entry and runtime adapter notes.
- `skills/teaching-design-package/references/format-and-orchestration.md` — Detailed package contract, provenance/status semantics, and Phase 29 PDF slot boundaries.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` — Standalone teaching-plan renderer and public command surface.
- `skills/jiaoan-jihua/references/format-and-rendering.md` — Standalone teaching-plan format, Typst generation, and verification rules.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` — Standalone lesson-plan renderer and public command surface.
- `skills/jiaoan-shicao/scripts/render_v110_typst.awk` — Current lesson-plan Typst renderer, including Phase 27 table-width behavior.
- `skills/jiaoan-shicao/references/format-and-rendering.md` — Standalone lesson-plan format, renderer contract, activity table behavior, and verification rules.

### Shared Scheduling and Fixture Evidence

- `references/scheduling-contract.md` — Shared scheduling model and evidence expectations for derived dates and hour consumption.
- `skills/jiaoan-jihua/references/calendar.json` — Built-in teaching-day calendar used by the baseline date-range derivation.
- `test/1.10/电气设备控制线路安装与调试授课计划.md` — Existing standalone teaching-plan fixture source for optional regression smoke checks.
- `test/1.10/电气设备控制线路安装与调试授课计划.typ` — Existing standalone teaching-plan Typst oracle for optional regression smoke checks.
- `test/1.10/电气设备控制线路安装与调试教案.md` — Existing standalone lesson-plan fixture source for optional regression smoke checks.
- `test/1.10/电气设备控制线路安装与调试教案.typ` — Existing standalone lesson-plan Typst oracle for optional regression smoke checks.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `skills/teaching-design-package/scripts/teaching-design-package.sh` already has `render-package`, `render-split`, `manifest`, `write_manifest`, `status_for_file`, and `merge_combined_pdf` logic. Phase 29 should extend this surface instead of inventing a separate command family unless planning finds a hard ambiguity.
- `merge_combined_pdf()` already tries `pdfunite` and `qpdf`, and writes `merge_unavailable:no_pdf_merge_tool` when neither exists. This is the natural combined-PDF implementation point.
- `write_manifest()` already exposes `teaching_plan_pdf`, `lesson_plans_pdf`, and `teaching_design_package_pdf` slots. Phase 29 can upgrade statuses from `not_run` to real file-backed status.
- `jiaoan-jihua.sh render --expected-typ` and `jiaoan-shicao.sh render --expected-typ` already support black-box Typst equivalence checks. They are suitable for standalone parity verification.

### Established Patterns

- Markdown remains the teacher-reviewable source and Typst/PDF are generated artifacts.
- Public shell commands are stable contracts; package orchestration may compose standalone scripts but must not force standalone callers into package input format.
- Manifest/status values must be honest and file-backed.
- Generated outputs should go to `/tmp` or explicit verification evidence, not committed deliverables.
- OpenClaw and Hermes compatibility requires portable instructions, explicit command examples, safety boundaries, and verification steps rather than one runtime's private syntax.

### Integration Points

- `cmd_render_package` currently produces `teaching-plan.typ`, `lesson-plans.typ`, and `teaching-design-package.typ`, then calls `write_manifest`. Phase 29 likely extends this command or adds a narrow PDF flag/subcommand that compiles the three PDF outputs.
- `cmd_manifest` currently detects existing `.typ` files and PDF slots. It can be used after PDF commands to confirm final status.
- The standalone parity harness can be a script-local verification helper or a phase verification command sequence: package render to one temp dir, standalone render from package handoffs to another temp dir, normalize allowed volatile lines, then compare.
- PDF text/page checks should be optional-tool-aware. Useful command candidates are `typst compile`, `pdfunite`, `qpdf`, `pdftotext`, `pdfinfo`, and visual raster tools if already installed.

</code_context>

<specifics>
## Specific Ideas

- Suggested temp layout for verification:
  - `/tmp/tdp-phase29.XXXXXX/package/` for package `render-package` and PDF outputs.
  - `/tmp/tdp-phase29.XXXXXX/standalone-plan/` for standalone `jiaoan-jihua` Typst/PDF from `package/jiaoan-jihua-full.md`.
  - `/tmp/tdp-phase29.XXXXXX/standalone-lessons/` for standalone `jiaoan-shicao` Typst/PDF from `package/jiaoan-shicao-full.md`.
- Suggested parity flow:
  1. Generate package outputs from `skills/teaching-design-package/templates/teaching-design-package-full.md`.
  2. Render standalone Typst from the generated handoffs in separate directories.
  3. Normalize only allowed volatile timestamp lines if present.
  4. `diff -u` normalized package split Typst vs standalone Typst.
  5. Compile both package split Typst files and standalone Typst files to PDF.
  6. Compare page counts and extracted text when tools are available.
  7. Merge accepted package split PDFs into `teaching-design-package.pdf`.
  8. Verify manifest statuses and content anchors.
- Required visible facts to search in generated Typst and, when extraction permits, PDFs: `160H`, `40H`, `60H`, `5月11日——5月15日`, `5月18日——5月27日`, `5月27日——6月5日`, `2025-2026学年第二学期`, `授课进度计划`, `教学设计方案`, `学习任务分析`, `教学活动设计`, and `学业评价`.
- If Typst package import fails because the environment is offline, use the exact error as verification evidence and stop. This project has prior evidence that `@preview/cuti:0.2.1` can require network on first compile.
- A useful `29-VERIFICATION.md` should include sections for PDF tool availability, split PDF compile, standalone Typst parity, standalone PDF parity, combined PDF merge, derived fact evidence, standalone public interface regression, generated artifact location, repository cleanliness, and requirement traceability.

</specifics>

<deferred>
## Deferred Ideas

- Redesigning the teacher-facing Markdown baseline remains out of scope.
- Replacing `jiaoan-jihua` or `jiaoan-shicao` with package-only entry points remains out of scope.
- Adding OCR, arbitrary external document import, hosted review, cloud approval, or unrelated document families remains future-only.

</deferred>

---

*Phase: 29-PDF Parity and Standalone Regression*
*Context gathered: 2026-06-15*
