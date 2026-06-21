---
phase: 40-skill-workflow-and-pdf-gate
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - skills/tiaokedan/SKILL.md
  - skills/tiaokedan/scripts/tiaokedan.sh
  - skills/tiaokedan/scripts/tiaokedan_renderer.py
  - skills/tiaokedan/references/pdf-workflow.md
  - README.md
  - skills/README.md
  - docs/directory-spec.md
  - docs/compatibility-matrix.md
  - .planning/REQUIREMENTS.md
  - .planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md
autonomous: true
requirements:
  - TKD-PDF-01
  - TKD-PDF-02
  - TKD-PDF-03
  - TKD-PDF-04
  - TKD-PDF-05
must_haves:
  truths:
    - "D-01: Create `skills/tiaokedan/SKILL.md` as a concise semantic entry, not a long reference manual."
    - "D-02: `description` triggers only for 调课单/调课说明 adjustment-form work."
    - "D-03: Workflow starts from teacher facts, asks only for missing/conflicting required fields, produces/updates `tiaokedan.md`, pauses for teacher review, then runs scripts only after Markdown is finalized."
    - "D-04: `SKILL.md` links to `references/markdown-contract.md`, `templates/tiaokedan.md`, `templates/tiaokedan-reference.typ`, and `scripts/tiaokedan.sh`."
    - "D-05: Canonical body remains runtime-neutral; runtime differences stay in `Runtime Adapter Notes`."
    - "D-06: Extend the existing render surface with PDF behavior shaped as `scripts/tiaokedan.sh render --input <tiaokedan.md> --typ <output.typ> --pdf <output.pdf>`."
    - "D-07: PDF success requires installed `typst`, render validation success, generated Typst, `typst compile` exit 0, and a non-empty PDF."
    - "D-08: `--expected-typ` remains optional fixture/evidence validation; production teacher forms do not need comparison to the Phase 37 sample."
    - "D-09: Missing `typst` or compile failure exits non-zero with concise stderr and no successful public-output leakage."
    - "D-10: Script changes are limited to PDF gate, clean-output boundary, help text, and verification; no broader parsing beyond the Phase 38 contract."
    - "D-11: Successful default teacher-facing output is minimal: finalized Markdown source/copy, explicit generated `.typ`, and requested `.pdf`."
    - "D-12: Hidden/debug diagnostics use a skill-specific hidden path such as `.tiaokedan/`; success roots do not leak status, logs, diffs, temp files, or negative-test artifacts."
    - "D-13: Failure behavior is honest: avoid complete-looking public PDF outputs when validation or PDF compilation fails."
    - "D-14: Verification includes public-root leakage checks for success and failure-path diagnostic checks."
    - "D-15: Required facts before final render are title, recipient, reason paragraph, department, date, and per-row 序号/班级/课程/原上课时间/原授课教师/调整后上课时间/调整后上课教师."
    - "D-16: Missing-info questions use teacher language: 调课原因、涉及班级和课程、原上课安排、调整后安排、涉及教师、落款部门和日期、optional 备注."
    - "D-17: Blank `备注` is allowed and should not be asked unless teacher indicates it is needed."
    - "D-18: Draft Markdown may keep `{{待补充: ...}}` or `{{AI草稿: ...}}`; final Typst/PDF rendering blocks while unresolved markers remain in required facts."
    - "D-19: Do not ask teachers for renderer-owned defaults such as page size, fonts, widths, Typst helper names, diagnostics paths, or comparison commands."
    - "D-20: Runtime adapter notes cover Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent in the established table pattern."
    - "D-21: Every runtime note mentions preserving the whole skill folder: `SKILL.md`, `references/`, `templates/`, and `scripts/`."
    - "D-22: OpenClaw and Hermes Agent notes conservatively verify frontmatter parsing, support-file discovery, script permission, `python3`, `typst`, sandbox writes, and hidden diagnostics."
    - "D-23: No generated wrappers, runtime-private syntax in the canonical body, or independent adapter files."
    - "D-24: Update `README.md` and `skills/README.md` so `tiaokedan` is discoverable."
    - "D-25: Update `docs/directory-spec.md` and `docs/compatibility-matrix.md` only for repository guidance/discoverability needed by this skill."
    - "D-26: Mark TKD-PDF-01 through TKD-PDF-05 complete only after Phase 40 verification evidence exists."
    - "D-27: Keep Phase 40 to the current single accepted 调课单 form; variants, batch generation, spreadsheet import, OCR/photo extraction, approval grids, signature boxes, and opinion columns remain future scope."
  artifacts:
    - path: "skills/tiaokedan/SKILL.md"
      provides: "canonical 调课单 skill entry with Markdown-first workflow, PDF command, missing-info questions, safety, verification, and six runtime notes"
      contains: "Runtime Adapter Notes"
    - path: "skills/tiaokedan/scripts/tiaokedan.sh"
      provides: "public render command extended with optional `--pdf <output.pdf>` while preserving existing `--input`, `--typ`, and `--expected-typ`"
      contains: "--pdf"
    - path: "skills/tiaokedan/scripts/tiaokedan_renderer.py"
      provides: "skill-local PDF gate support and clean failure behavior without broadening the Phase 38 parser contract"
      contains: "typst"
    - path: "skills/tiaokedan/references/pdf-workflow.md"
      provides: "longer PDF workflow, clean-output, diagnostics, and verification details if keeping them in SKILL.md would make the entry too heavy"
      contains: ".tiaokedan"
    - path: ".planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md"
      provides: "Phase 40 command evidence, PDF success/failure evidence, public-root leakage checks, runtime adapter/doc coverage, and TKD-PDF traceability"
      contains: "TKD-PDF-05"
  key_links:
    - from: "skills/tiaokedan/templates/tiaokedan.md"
      to: "skills/tiaokedan/SKILL.md"
      via: "teacher-readable Markdown source of truth and workflow example"
      pattern: "tiaokedan.md|教师审阅|Markdown"
    - from: "skills/tiaokedan/references/markdown-contract.md"
      to: "skills/tiaokedan/SKILL.md"
      via: "required facts, marker semantics, optional 备注, and renderer-owned defaults"
      pattern: "{{待补充: 说明}}|{{AI草稿: 说明}}|Renderer-Owned Defaults"
    - from: "skills/tiaokedan/scripts/tiaokedan.sh"
      to: "skills/tiaokedan/SKILL.md"
      via: "finalized Markdown render command and optional PDF gate"
      pattern: "render --input|--typ|--pdf"
    - from: ".planning/phases/40-skill-workflow-and-pdf-gate/40-CONTEXT.md"
      to: ".planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md"
      via: "D-01 through D-27 decision coverage and TKD-PDF-01 through TKD-PDF-05 evidence"
      pattern: "D-01|D-27|TKD-PDF-01|TKD-PDF-05"
---

<objective>
Implement the Phase 40 `调课单` Skill Workflow and PDF Gate plan.

Purpose: enable `/gsd:execute-phase 40` to package the existing Phase 37/38/39 `tiaokedan` work into a complete portable skill. The phase must add the canonical skill entry, a real PDF generation gate, clean output and hidden diagnostics behavior, concise missing-information questions, six-runtime adapter notes, repository discoverability, and requirement traceability.
Output: `skills/tiaokedan/SKILL.md`, PDF-capable `scripts/tiaokedan.sh render`, optional PDF/output reference documentation, README/index/docs updates, and `.planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md`.
</objective>

<execution_context>
@/Users/mrered/.codex/get-shit-done/workflows/execute-plan.md
@/Users/mrered/.codex/get-shit-done/templates/summary.md
</execution_context>

<context>
@AGENTS.md
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/STATE.md
@.planning/phases/37-typst-baseline/37-CONTEXT.md
@.planning/phases/37-typst-baseline/37-VERIFICATION.md
@.planning/phases/38-markdown-contract/38-CONTEXT.md
@.planning/phases/38-markdown-contract/38-VERIFICATION.md
@.planning/phases/39-markdown-to-typst-renderer/39-CONTEXT.md
@.planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md
@.planning/phases/40-skill-workflow-and-pdf-gate/40-CONTEXT.md
@docs/directory-spec.md
@docs/compatibility-matrix.md
@docs/markdown-normalization-contract.md
@README.md
@skills/README.md
@skills/gongwen/SKILL.md
@skills/teaching-design-package/SKILL.md
@skills/teaching-design-package/references/format-and-orchestration.md
@skills/tiaokedan/templates/tiaokedan.md
@skills/tiaokedan/templates/tiaokedan-reference.typ
@skills/tiaokedan/templates/tiaokedan-reference.pdf
@skills/tiaokedan/references/markdown-contract.md
@skills/tiaokedan/scripts/tiaokedan.sh
@skills/tiaokedan/scripts/tiaokedan_renderer.py

<interfaces>
Phase 40 may create `skills/tiaokedan/SKILL.md`, add or update a skill-local PDF/output reference file, extend the existing `skills/tiaokedan/scripts/tiaokedan.sh render` surface with `--pdf`, update repository discovery docs, and update Phase 40 verification/requirement traceability. It must not redesign `templates/tiaokedan.md`, `templates/tiaokedan-reference.typ`, `templates/tiaokedan-reference.pdf`, or the Phase 38 Markdown contract. Script changes must preserve existing Phase 39 behavior for `--input`, `--typ`, and optional `--expected-typ`.
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add canonical skill entry and missing-information workflow</name>
  <files>skills/tiaokedan/SKILL.md, skills/tiaokedan/references/pdf-workflow.md</files>
  <read_first>
    AGENTS.md
    docs/directory-spec.md
    docs/markdown-normalization-contract.md
    docs/compatibility-matrix.md
    .planning/ROADMAP.md
    .planning/REQUIREMENTS.md
    .planning/phases/40-skill-workflow-and-pdf-gate/40-CONTEXT.md
    skills/gongwen/SKILL.md
    skills/teaching-design-package/SKILL.md
    skills/tiaokedan/templates/tiaokedan.md
    skills/tiaokedan/templates/tiaokedan-reference.typ
    skills/tiaokedan/references/markdown-contract.md
    skills/tiaokedan/scripts/tiaokedan.sh
    If `skills/tiaokedan/SKILL.md` or `skills/tiaokedan/references/pdf-workflow.md` already exists at execution time, read it before editing and preserve user-authored content unless it conflicts with D-01 through D-23.
  </read_first>
  <action>
    Create `skills/tiaokedan/SKILL.md` as the canonical skill entry for TKD-PDF-03 and TKD-PDF-04. Use the concise entry style from `skills/gongwen/SKILL.md` and the teacher-first workflow style from `skills/teaching-design-package/SKILL.md`. The frontmatter must include `name: "tiaokedan"`, a `description` that triggers only for `调课单` / `调课说明` adjustment-form work, `metadata.short-description`, `version`, `portability: "canonical"`, and supported runtimes Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.

    The body must define: Objective, Use When, Inputs, Teacher Workflow, Missing Information Questions, Finalized Markdown Render/PDF Commands, Runtime Adapter Notes, Outputs, Verification, and Safety. The workflow must start with teacher-provided facts, ask only about missing/conflicting required facts, produce or update `tiaokedan.md`, pause for teacher review, treat finalized Markdown as the source of truth, then run scripts. Link explicitly to `references/markdown-contract.md`, `templates/tiaokedan.md`, `templates/tiaokedan-reference.typ`, and `scripts/tiaokedan.sh`; if the PDF/output detail would make the entry heavy, create `skills/tiaokedan/references/pdf-workflow.md` and link to it.

    The missing-information questions must be concise and teacher-facing. Include the required question groups: 调课原因, 涉及班级和课程, 原上课安排, 调整后安排, 涉及教师, 落款部门和日期, and optional 备注. State that blank `备注` is allowed and should not be asked unless the teacher indicates a remark is needed. State that unresolved `{{待补充: ...}}` or `{{AI草稿: ...}}` markers may remain in drafting Markdown but must block final Typst/PDF rendering when they appear in required output facts. Do not ask for renderer-owned defaults such as page size, font fallback list, point sizes, table widths, Typst helper names, diagnostic paths, or comparison commands.

    Add a `Runtime Adapter Notes` table covering all six required runtimes. Every runtime row must mention preserving the whole skill folder: `SKILL.md`, `references/`, `templates/`, and `scripts/`. Codex notes must mention reading project `AGENTS.md`, support files, and shell script calls. Claude Code notes must mention installing the same folder under a Claude skill path and frontmatter-triggered use. Gemini CLI notes must mention project context or `GEMINI.md` discovery fallback. OpenCode notes must mention native skill path or Claude-compatible fallback and support-folder preservation. OpenClaw and Hermes Agent rows must conservatively require verifying frontmatter parsing, support-file discovery, script execution permission, `python3`, `typst`, sandbox/write permissions, and hidden `.tiaokedan/` diagnostic behavior. Do not add runtime-private syntax to the canonical workflow and do not create independent adapter files.
  </action>
  <verify>
    <automated>test -s skills/tiaokedan/SKILL.md</automated>
    <automated>rg -F 'description:' skills/tiaokedan/SKILL.md && rg -F '调课单' skills/tiaokedan/SKILL.md && rg -F 'tiaokedan.md' skills/tiaokedan/SKILL.md</automated>
    <automated>rg -F 'references/markdown-contract.md' skills/tiaokedan/SKILL.md && rg -F 'templates/tiaokedan.md' skills/tiaokedan/SKILL.md && rg -F 'templates/tiaokedan-reference.typ' skills/tiaokedan/SKILL.md && rg -F 'scripts/tiaokedan.sh' skills/tiaokedan/SKILL.md</automated>
    <automated>for runtime in Codex 'Claude Code' 'Gemini CLI' OpenCode OpenClaw 'Hermes Agent'; do rg -F "$runtime" skills/tiaokedan/SKILL.md >/dev/null || exit 1; done</automated>
    <automated>rg -F 'SKILL.md' skills/tiaokedan/SKILL.md && rg -F 'references/' skills/tiaokedan/SKILL.md && rg -F 'templates/' skills/tiaokedan/SKILL.md && rg -F 'scripts/' skills/tiaokedan/SKILL.md</automated>
    <automated>for token in '调课原因' '涉及班级和课程' '原上课安排' '调整后安排' '涉及教师' '落款部门和日期' '{{待补充:' '{{AI草稿:'; do rg -F "$token" skills/tiaokedan/SKILL.md >/dev/null || exit 1; done</automated>
    <automated>! rg 'Claude-only|Task\\(|AskUserQuestion|mcp__|vscode_askquestions' skills/tiaokedan/SKILL.md</automated>
  </verify>
  <acceptance_criteria>
    `skills/tiaokedan/SKILL.md` is a concise canonical entry that describes the Markdown-first teacher workflow, required missing-information questions, finalized Markdown rendering, PDF gate, safety boundary, and six runtime adapter notes. It links to the existing support files and does not introduce runtime-private syntax or independent adapter files.
  </acceptance_criteria>
  <done>Canonical `tiaokedan` skill entry exists and gives future agents enough guidance to gather facts, keep Markdown reviewable, and block final output until required facts are complete.</done>
</task>

<task type="auto">
  <name>Task 2: Extend the skill-local render command with a strict PDF gate and clean diagnostics</name>
  <files>skills/tiaokedan/scripts/tiaokedan.sh, skills/tiaokedan/scripts/tiaokedan_renderer.py, skills/tiaokedan/references/pdf-workflow.md</files>
  <read_first>
    AGENTS.md
    .planning/phases/39-markdown-to-typst-renderer/39-PLAN.md
    .planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md
    .planning/phases/40-skill-workflow-and-pdf-gate/40-CONTEXT.md
    skills/tiaokedan/scripts/tiaokedan.sh
    skills/tiaokedan/scripts/tiaokedan_renderer.py
    skills/tiaokedan/templates/tiaokedan.md
    skills/tiaokedan/templates/tiaokedan-reference.typ
    skills/tiaokedan/references/markdown-contract.md
    skills/gongwen/SKILL.md
    skills/gongwen/scripts/gongwen.sh
    skills/teaching-design-package/SKILL.md
    skills/teaching-design-package/references/format-and-orchestration.md
    If either script has uncommitted user changes at execution time, read the current diff first and preserve those changes unless they conflict with the PDF gate requirements.
  </read_first>
  <action>
    Extend `skills/tiaokedan/scripts/tiaokedan.sh render` and the Python renderer to accept optional `--pdf <output.pdf>` while preserving the existing successful Phase 39 surface: `render --input <tiaokedan.md> --typ <output.typ> [--expected-typ <reference.typ>]`. Update help text to show `--pdf`. Unknown flags and unknown subcommands must still exit non-zero with concise stderr.

    Implement the PDF gate for TKD-PDF-01. The command must first perform the same Markdown validation and Typst generation as Phase 39. If `--pdf` is supplied, it must then locate an installed `typst` CLI, run `typst compile <output.typ> <output.pdf>`, require exit code 0, and require the PDF path to exist with non-zero size. Typst generation alone must not be reported as final PDF success. `--expected-typ` remains optional evidence/fixture comparison; normal production rendering with custom forms must not require comparing to `templates/tiaokedan-reference.typ`.

    Implement clean output and diagnostics behavior for TKD-PDF-02. Successful default output must be minimal: write only the explicit `--typ` output and, if supplied, the explicit `--pdf` output. Do not create status files, logs, diffs, debug JSON, temp files, or negative fixtures beside public teacher-facing files during success. If richer diagnostics are needed, place them only under a hidden `.tiaokedan/` directory under the relevant output parent or only when an explicit debug/failure path is used. On validation failure, missing `typst`, compile failure, or empty PDF, exit non-zero with concise stderr and remove or avoid publishing a complete-looking PDF at the requested public path. Preserve the generated Typst only when validation succeeded and the user explicitly asked for `--typ`.

    If adding the clean-output contract to `SKILL.md` would make the entry too long, create or update `skills/tiaokedan/references/pdf-workflow.md`. It must document command shapes, PDF success criteria, hidden `.tiaokedan/` diagnostics, failure behavior, and verification commands. It must not duplicate the full Markdown field contract from `references/markdown-contract.md`.
  </action>
  <verify>
    <automated>python3 -m py_compile skills/tiaokedan/scripts/tiaokedan_renderer.py</automated>
    <automated>skills/tiaokedan/scripts/tiaokedan.sh --help | rg -F -- '--pdf'</automated>
    <automated>rm -rf .planning/phases/40-skill-workflow-and-pdf-gate/generated && mkdir -p .planning/phases/40-skill-workflow-and-pdf-gate/generated</automated>
    <automated>skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.typ --expected-typ skills/tiaokedan/templates/tiaokedan-reference.typ</automated>
    <automated>cmp -s .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.typ skills/tiaokedan/templates/tiaokedan-reference.typ</automated>
    <automated>skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf.typ --pdf .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf</automated>
    <automated>test -s .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf</automated>
    <automated>test "$(find .planning/phases/40-skill-workflow-and-pdf-gate/generated -maxdepth 1 -type f | wc -l | tr -d ' ')" = 3</automated>
    <automated>for file in tiaokedan.pdf tiaokedan.pdf.typ tiaokedan.typ; do test -f ".planning/phases/40-skill-workflow-and-pdf-gate/generated/$file" || exit 1; done</automated>
    <automated>! find .planning/phases/40-skill-workflow-and-pdf-gate/generated -maxdepth 1 -type f | rg 'status|manifest|log|stderr|stdout|diff|debug|json|tmp|diagnostic'</automated>
    <automated>! skills/tiaokedan/scripts/tiaokedan.sh render --input .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-missing-field.md --typ .planning/phases/40-skill-workflow-and-pdf-gate/generated/invalid.typ --pdf .planning/phases/40-skill-workflow-and-pdf-gate/generated/invalid.pdf 2>.planning/phases/40-skill-workflow-and-pdf-gate/generated/invalid.stderr</automated>
    <automated>test ! -e .planning/phases/40-skill-workflow-and-pdf-gate/generated/invalid.pdf</automated>
    <automated>rg 'unresolved required marker|missing required|tiaokedan:' .planning/phases/40-skill-workflow-and-pdf-gate/generated/invalid.stderr</automated>
    <automated>! rg 'skills/(gongwen|teaching-design-package|jiaoan-|end-of-term|school-presentation)' skills/tiaokedan/scripts</automated>
  </verify>
  <acceptance_criteria>
    The public command supports `--pdf` without regressing Phase 39 Typst rendering or optional expected-Typst comparison. PDF success requires real `typst compile` success and a non-empty PDF. Successful public output roots contain only the explicitly requested teacher-facing files, while failure paths do not leave complete-looking PDFs.
  </acceptance_criteria>
  <done>Finalized `tiaokedan.md` can generate Typst and a real PDF through the skill-local command with honest success/failure semantics.</done>
</task>

<task type="auto">
  <name>Task 3: Update repository discoverability and requirement traceability</name>
  <files>README.md, skills/README.md, docs/directory-spec.md, docs/compatibility-matrix.md, .planning/REQUIREMENTS.md</files>
  <read_first>
    AGENTS.md
    README.md
    skills/README.md
    docs/directory-spec.md
    docs/compatibility-matrix.md
    .planning/REQUIREMENTS.md
    .planning/ROADMAP.md
    .planning/phases/40-skill-workflow-and-pdf-gate/40-CONTEXT.md
    skills/tiaokedan/SKILL.md
    skills/tiaokedan/references/markdown-contract.md
    skills/tiaokedan/references/pdf-workflow.md if it exists
    skills/tiaokedan/scripts/tiaokedan.sh
  </read_first>
  <action>
    Update `README.md` so `tiaokedan` appears in the repository structure and existing-skills list. The entry must say it is a `调课单` Markdown-first document workflow that uses `templates/tiaokedan.md`, the skill-local renderer, and optional PDF generation after teacher review. Keep the wording short and consistent with existing skill entries.

    Update `skills/README.md` so `tiaokedan` appears in `Current skills` and the artifact contract discovery table. The Markdown intermediate must be `templates/tiaokedan.md`. The artifact contract must include `SKILL.md`, `references/markdown-contract.md`, `scripts/tiaokedan.sh`, and `references/pdf-workflow.md` if Task 2 created it.

    Update `docs/directory-spec.md` only where useful for repository guidance. Add `skills/tiaokedan/SKILL.md`, `skills/tiaokedan/references/markdown-contract.md`, `skills/tiaokedan/templates/tiaokedan.md`, and `skills/tiaokedan/scripts/tiaokedan.sh` to the shared references/fixtures or skill examples section. Do not change the general directory ownership contract.

    Update `docs/compatibility-matrix.md` with a concise runtime note for `tiaokedan`: whole-folder installation, Markdown-first source, `python3` renderer, optional `typst` PDF gate, and hidden `.tiaokedan/` diagnostics. Do not add separate adapter files or claim runtime-specific wrappers.

    Update `.planning/REQUIREMENTS.md` only after Tasks 1 and 2 have verification evidence. Mark TKD-PDF-01 through TKD-PDF-05 complete and update the Traceability table to point to `.planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md` plus the relevant skill/docs artifacts. Do not modify future requirements or out-of-scope items.
  </action>
  <verify>
    <automated>rg -F 'tiaokedan' README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md</automated>
    <automated>rg -F 'templates/tiaokedan.md' skills/README.md README.md</automated>
    <automated>rg -F 'references/markdown-contract.md' skills/README.md docs/directory-spec.md</automated>
    <automated>rg -F 'scripts/tiaokedan.sh' skills/README.md docs/directory-spec.md docs/compatibility-matrix.md</automated>
    <automated>rg -F '.tiaokedan' docs/compatibility-matrix.md skills/tiaokedan/SKILL.md</automated>
    <automated>for req in TKD-PDF-01 TKD-PDF-02 TKD-PDF-03 TKD-PDF-04 TKD-PDF-05; do rg "$req.*Complete|\\[x\\].*$req" .planning/REQUIREMENTS.md >/dev/null || exit 1; done</automated>
    <automated>rg -F '.planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md' .planning/REQUIREMENTS.md</automated>
    <automated>! rg 'generated wrapper|adapter file|Claude-only|OpenClaw.*optional|Hermes Agent.*optional' README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md skills/tiaokedan/SKILL.md</automated>
  </verify>
  <acceptance_criteria>
    Repository indexes and compatibility docs make `tiaokedan` findable and explain its whole-folder runtime boundary. TKD-PDF-01 through TKD-PDF-05 are marked complete only after verification evidence exists, and traceability points to Phase 40 evidence plus the implemented skill/docs artifacts.
  </acceptance_criteria>
  <done>`tiaokedan` is discoverable from top-level docs, skill index, directory guidance, compatibility notes, and requirements traceability.</done>
</task>

<task type="auto">
  <name>Task 4: Record Phase 40 verification evidence and guard against scope creep</name>
  <files>.planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md</files>
  <read_first>
    AGENTS.md
    .planning/ROADMAP.md
    .planning/REQUIREMENTS.md
    .planning/phases/40-skill-workflow-and-pdf-gate/40-CONTEXT.md
    .planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md
    skills/tiaokedan/SKILL.md
    skills/tiaokedan/references/markdown-contract.md
    skills/tiaokedan/references/pdf-workflow.md if it exists
    skills/tiaokedan/scripts/tiaokedan.sh
    skills/tiaokedan/scripts/tiaokedan_renderer.py
    README.md
    skills/README.md
    docs/directory-spec.md
    docs/compatibility-matrix.md
  </read_first>
  <action>
    Create `.planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md` as the Phase 40 evidence file. Include sections for status, source paths, requirement coverage, D-01 through D-27 decision coverage, canonical skill entry evidence, missing-information question evidence, runtime adapter coverage, PDF command evidence, clean-output leakage evidence, failure-path evidence, repository discoverability evidence, requirement traceability evidence, runtime independence evidence, and explicit deferred scope.

    Record exact commands and results for the finalized Markdown to Typst/PDF path. Required positive evidence: `python3 -m py_compile`, successful Typst-only render with `--expected-typ`, `cmp -s` against the Phase 37 reference, successful PDF render with `--pdf`, and `test -s` on the final PDF. Required clean-output evidence: list the successful output directory and prove it contains only explicitly requested public files. Required failure evidence: run at least one invalid Phase 39 fixture with `--pdf` and prove the command exits non-zero, stderr is concise, and no public invalid PDF remains.

    Record runtime adapter coverage by scanning `skills/tiaokedan/SKILL.md` for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, Hermes Agent, and whole-folder preservation tokens. Record repository discovery coverage by scanning `README.md`, `skills/README.md`, `docs/directory-spec.md`, and `docs/compatibility-matrix.md` for `tiaokedan` and key support files. Record traceability coverage by scanning `.planning/REQUIREMENTS.md` for TKD-PDF-01 through TKD-PDF-05 as complete with Phase 40 evidence.

    Record scope-guard evidence: no school-specific variants, batch generation, spreadsheet import, OCR/photo extraction, approval grids, signature boxes, opinion columns, generated wrappers, independent runtime adapter files, or sibling skill runtime dependencies were introduced. Include a sibling path scan for `skills/tiaokedan/scripts/` and a copied `skills/tiaokedan/`-only render/PDF run if it is feasible without copying broad repo state.
  </action>
  <verify>
    <automated>test -s .planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md</automated>
    <automated>for req in TKD-PDF-01 TKD-PDF-02 TKD-PDF-03 TKD-PDF-04 TKD-PDF-05; do rg -F "$req" .planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md >/dev/null || exit 1; done</automated>
    <automated>for token in D-01 D-02 D-03 D-04 D-05 D-06 D-07 D-08 D-09 D-10 D-11 D-12 D-13 D-14 D-15 D-16 D-17 D-18 D-19 D-20 D-21 D-22 D-23 D-24 D-25 D-26 D-27; do rg -F "$token" .planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md >/dev/null || exit 1; done</automated>
    <automated>rg -F 'skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md' .planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md</automated>
    <automated>rg -F '--pdf' .planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md && rg -F 'test -s' .planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md</automated>
    <automated>rg -F 'clean output' .planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md || rg -F 'public-root leakage' .planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md</automated>
    <automated>rg -F 'Phase 40 Scope Boundary' .planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md</automated>
  </verify>
  <acceptance_criteria>
    `40-VERIFICATION.md` proves all five TKD-PDF requirements, covers all D-01 through D-27 decisions, records real PDF and clean-output commands, records at least one failure-path proof, records discovery/traceability evidence, and explicitly preserves deferred scope.
  </acceptance_criteria>
  <done>Phase 40 evidence is complete enough for verify-work to confirm skill workflow, PDF gate, clean diagnostics, runtime adapters, discoverability, and traceability.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Teacher source facts -> `tiaokedan.md` | Agents must ask only for missing/conflicting required facts and keep uncertainty visible in Markdown until teacher review. |
| Finalized Markdown -> Typst/PDF command | The script must reject unresolved required markers, malformed tables, unsupported syntax, missing `typst`, compile failures, and empty PDFs before claiming final success. |
| Public output root -> hidden diagnostics | Teacher-facing success output must remain minimal; logs, diffs, temp files, status JSON, and diagnostics belong in hidden/debug paths only. |
| Canonical skill body -> runtime adapter notes | Runtime-private behavior must stay in adapter notes, not in the canonical workflow body. |
| `tiaokedan` skill folder -> sibling skills | Runtime must remain self-contained inside `skills/tiaokedan/` and standard platform tools. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-40-01 | Tampering | finalized Markdown facts | mitigate | Preserve Phase 39 validation and document required missing-information questions before final rendering. |
| T-40-02 | Repudiation | PDF success claim | mitigate | Record exact `typst compile` path through `--pdf`, exit code, and non-empty PDF evidence in `40-VERIFICATION.md`. |
| T-40-03 | Information Disclosure | public output root | mitigate | Verify success roots contain only explicit `.typ` and `.pdf` files; hide diagnostics under `.tiaokedan/` or failure-only paths. |
| T-40-04 | Denial of Service | missing Typst or compile failure | mitigate | Exit non-zero with concise stderr and avoid publishing complete-looking PDFs. |
| T-40-05 | Elevation of Privilege | runtime adapter drift | mitigate | Keep one canonical `SKILL.md`; no wrappers or runtime-private syntax; adapter table documents installation checks. |
| T-40-06 | Tampering | sibling skill dependency | mitigate | Scan `skills/tiaokedan/scripts/` and run copied-folder verification where feasible. |
| T-40-SC | Scope Creep | future forms/imports | mitigate | Keep variants, batch generation, spreadsheet import, OCR/photo extraction, approval grids, signature boxes, and opinion columns deferred. |
</threat_model>

<verification>
Overall phase checks:

1. `test -s skills/tiaokedan/SKILL.md`
2. `python3 -m py_compile skills/tiaokedan/scripts/tiaokedan_renderer.py`
3. `skills/tiaokedan/scripts/tiaokedan.sh --help | rg -F -- '--pdf'`
4. `skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.typ --expected-typ skills/tiaokedan/templates/tiaokedan-reference.typ`
5. `cmp -s .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.typ skills/tiaokedan/templates/tiaokedan-reference.typ`
6. `skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf.typ --pdf .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf`
7. `test -s .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf`
8. Public-root leakage check confirms only explicit success outputs are present and no status/log/diff/debug/json/tmp/diagnostic files appear in the public root.
9. Invalid fixture with `--pdf` exits non-zero and does not leave `invalid.pdf`.
10. Runtime adapter scan finds Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, Hermes Agent, and whole-folder support-file preservation.
11. README/index/docs scan finds `tiaokedan`, `templates/tiaokedan.md`, `references/markdown-contract.md`, and `scripts/tiaokedan.sh`.
12. `.planning/REQUIREMENTS.md` marks TKD-PDF-01 through TKD-PDF-05 complete only with Phase 40 verification evidence.
13. `40-VERIFICATION.md` covers TKD-PDF-01 through TKD-PDF-05 and D-01 through D-27.
</verification>

<success_criteria>
- Canonical `skills/tiaokedan/SKILL.md` exists, is concise, runtime-neutral, and covers Markdown-first workflow, missing-information questions, PDF gate, verification, safety, and six runtime adapter notes.
- `scripts/tiaokedan.sh render --input --typ --pdf` produces a real non-empty PDF only after Markdown validation, Typst generation, and `typst compile` success.
- Successful teacher-facing output stays clean; diagnostics, logs, diffs, temp files, status JSON, and failure evidence do not leak into the public output root.
- Repository discovery docs list the new `tiaokedan` skill and its artifact contract.
- TKD-PDF-01 through TKD-PDF-05 are completed in `.planning/REQUIREMENTS.md` with Phase 40 verification evidence.
- No Phase 40 implementation introduces sibling skill runtime dependencies, generated wrappers, runtime-specific adapter files, or deferred future-form/import features.
</success_criteria>
