# Phase 40: 调课单 Skill Workflow and PDF Gate - Context

**Gathered:** 2026-06-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 40 packages the existing `tiaokedan` work into a complete portable skill surface. It should add the canonical `skills/tiaokedan/SKILL.md`, document the finalized Markdown-first workflow, add the final PDF gate on top of the Phase 39 Typst renderer, keep successful teacher-facing output clean while diagnostics stay hidden or debug-only, define concise missing-information questions, cover all six required runtime adapter notes, and update repository indexes/discoverability and requirement traceability. It must not redesign the accepted form surface, change the Phase 38 Markdown contract, or replace the Phase 39 renderer boundary unless a small script extension is required to expose the PDF gate.

</domain>

<decisions>
## Implementation Decisions

### Canonical Skill Entry
- **D-01:** Create `skills/tiaokedan/SKILL.md` as the lightweight semantic entry for the skill. It should be concise like `skills/gongwen/SKILL.md`, not a long reference manual.
- **D-02:** The `description` must trigger only for 调课单/调课说明 style adjustment-form work: gathering adjustment facts, producing/reviewing `tiaokedan.md`, rendering Typst, and generating the final PDF.
- **D-03:** The entry workflow should start from teacher-provided facts, ask only for missing or conflicting required fields, produce or update the teacher-readable Markdown intermediate, pause for teacher review, then run scripts only after Markdown is finalized.
- **D-04:** The entry must explicitly link to `references/markdown-contract.md`, `templates/tiaokedan.md`, `templates/tiaokedan-reference.typ`, and `scripts/tiaokedan.sh`. Long field rules and marker semantics stay in the reference file.
- **D-05:** The canonical body must remain runtime-neutral. Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent differences belong only in `Runtime Adapter Notes`.

### PDF Workflow
- **D-06:** Phase 40 should add a documented PDF path from finalized Markdown to generated Typst to final PDF. The expected public command shape should extend the existing render surface rather than create a second workflow: `scripts/tiaokedan.sh render --input <tiaokedan.md> --typ <output.typ> --pdf <output.pdf>`.
- **D-07:** PDF success requires an installed `typst` CLI, render validation success, a generated Typst file, `typst compile` exit 0, and a non-empty PDF. Typst generation alone must not be described as final PDF success.
- **D-08:** The PDF command may keep `--expected-typ <reference.typ>` as an optional verification gate for fixtures/evidence, but production teacher workflow should not require comparing every custom form to the Phase 37 sample reference.
- **D-09:** If `typst` is unavailable or compilation fails, the script must exit non-zero with a concise stderr message and keep any diagnostics out of the successful public output root.
- **D-10:** Phase 40 may update `scripts/tiaokedan.sh` and `scripts/tiaokedan_renderer.py` only as needed for the PDF gate, clean-output boundary, help text, and verification. It should not broaden parsing beyond the accepted Phase 38 contract.

### Clean Output And Diagnostics
- **D-11:** Successful default teacher-facing output should be minimal: the finalized Markdown source or copy, the generated `.typ` if the command explicitly asks for it, and the final `.pdf` when `--pdf` is requested. Comparison evidence, stderr logs, temp files, debug JSON, and failure snapshots must not appear as normal teacher-facing files.
- **D-12:** Hidden/debug-only diagnostics should use a clearly hidden location, preferably a skill-specific hidden directory such as `.tiaokedan/` under the chosen output directory when diagnostics are needed. Successful public roots must not leak status files, logs, comparison diffs, temp files, or negative-test artifacts.
- **D-13:** Failure behavior should be honest: remove or avoid publishing complete-looking public PDF outputs when validation or PDF compilation fails; record only concise failure messages by default and richer evidence only in hidden/debug paths.
- **D-14:** Phase verification should include public-root leakage checks for a successful PDF run and at least one failure-path check that proves diagnostics remain hidden/debug-only.

### Missing-Information Questions
- **D-15:** `SKILL.md` should include a short question list for blockers before final rendering. Required facts are: title, recipient, reason paragraph, department, date, and for each adjustment row: 序号, 班级, 课程, 原上课时间, 原授课教师, 调整后上课时间, 调整后上课教师.
- **D-16:** Ask questions in teacher language, not schema language. Good question groups are: 调课原因, 涉及班级和课程, 原上课安排, 调整后安排, 涉及教师, 落款部门和日期, optional 备注.
- **D-17:** Blank `备注` remains allowed. Do not ask for 备注 if the teacher has not indicated it is needed.
- **D-18:** If a required fact is unknown, keep it visible in Markdown as `{{待补充: ...}}` during drafting. Final PDF rendering must block while unresolved `{{待补充: ...}}` or `{{AI草稿: ...}}` markers remain in required output facts.
- **D-19:** Do not ask teachers for renderer-owned defaults such as page size, font fallback list, point sizes, column widths, Typst helper names, diagnostic paths, or comparison commands.

### Runtime Adapter Notes
- **D-20:** Runtime adapter notes must cover Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent in the same table pattern used by existing skills.
- **D-21:** Every runtime note should mention whole-folder support-file preservation: `SKILL.md`, `references/`, `templates/`, and `scripts/` must be installed/read together.
- **D-22:** OpenClaw and Hermes Agent must stay first-class required targets. Their notes should be conservative: verify frontmatter parsing, support-file discovery, script execution permission, `python3`, `typst`, sandbox write permissions, and hidden diagnostic directory behavior during installation.
- **D-23:** Do not introduce generated wrappers, runtime-private syntax in the canonical body, or independent adapter files in Phase 40.

### README, Index, And Traceability
- **D-24:** Update `README.md` and `skills/README.md` so `tiaokedan` is discoverable alongside existing document workflow skills.
- **D-25:** If directory conventions or compatibility notes need a skill-specific entry, update `docs/directory-spec.md` and `docs/compatibility-matrix.md` without changing their general contract.
- **D-26:** Update `.planning/REQUIREMENTS.md` traceability for TKD-PDF-01 through TKD-PDF-05 only after implementation evidence exists in Phase 40 verification. During planning, keep these as pending.
- **D-27:** Keep Phase 40 focused on the current single accepted 调课单 form. Multiple school variants, batch generation, spreadsheet import, OCR/photo extraction, approval grids, signature boxes, and opinion columns remain future scope.

### Claude's Discretion
- The planner may decide whether to implement clean delivery as a direct `--typ/--pdf` pair or add an optional `--out-dir` helper, provided successful public output stays clean and the existing explicit render command remains usable.
- The planner may choose the exact hidden diagnostics directory shape and whether to write debug files only when a debug flag is passed or when failures occur.
- The planner may add a small reference file for PDF/output behavior if `SKILL.md` would become too long; otherwise the concise skill entry can carry the workflow directly.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope
- `.planning/ROADMAP.md` — Phase 40 goal and success criteria.
- `.planning/REQUIREMENTS.md` — TKD-PDF-01, TKD-PDF-02, TKD-PDF-03, TKD-PDF-04, and TKD-PDF-05.
- `.planning/PROJECT.md` — v1.16 milestone purpose, Markdown-first discipline, portability constraints, and required runtimes.
- `.planning/STATE.md` — current state and Phase 39 completion context.
- `AGENTS.md` — Simplified Chinese response rule, editing rules, and skill authoring constraints.

### Accepted 调课单 Inputs And Renderer
- `skills/tiaokedan/templates/tiaokedan-reference.typ` — accepted hand-authored Typst surface and PDF target layout.
- `skills/tiaokedan/templates/tiaokedan.md` — teacher-readable Markdown fixture and default example.
- `skills/tiaokedan/references/markdown-contract.md` — required/optional fields, review markers, renderer-owned defaults, and Phase 38 boundaries.
- `skills/tiaokedan/scripts/tiaokedan.sh` — existing Phase 39 public command surface.
- `skills/tiaokedan/scripts/tiaokedan_renderer.py` — existing skill-local parser/renderer that Phase 40 may extend only for the PDF gate.

### Prior Phase Evidence
- `.planning/phases/37-typst-baseline/37-CONTEXT.md` — locked visual/form decisions.
- `.planning/phases/37-typst-baseline/37-VERIFICATION.md` — verified non-empty reference PDF evidence.
- `.planning/phases/38-markdown-contract/38-CONTEXT.md` — Markdown contract and missing-marker decisions.
- `.planning/phases/38-markdown-contract/38-VERIFICATION.md` — verified Markdown fixture and contract evidence.
- `.planning/phases/39-markdown-to-typst-renderer/39-CONTEXT.md` — renderer boundary and Phase 40 deferred decisions.
- `.planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md` — byte-for-byte render evidence, negative fixtures, and runtime independence evidence.

### Repository Contracts
- `README.md` — top-level skill discovery and document workflow expectations.
- `skills/README.md` — skill index and artifact contract discovery table.
- `docs/directory-spec.md` — ownership rules for `SKILL.md`, `references/`, `scripts/`, and `templates/`.
- `docs/compatibility-matrix.md` — required runtime adapter expectations.
- `docs/markdown-normalization-contract.md` — shared Markdown intermediate discipline and visible uncertainty markers.

### Local Pattern References
- `skills/gongwen/SKILL.md` — concise document-skill entry with Markdown-to-Typst/PDF command examples and six-runtime notes.
- `skills/gongwen/references/format-and-rendering.md` — optional PDF export language for a document workflow skill.
- `skills/teaching-design-package/SKILL.md` — teacher workflow before scripts, clean public output, hidden diagnostics, and runtime adapter note style.
- `skills/teaching-design-package/references/format-and-orchestration.md` — stronger clean-output/hidden-diagnostics pattern; use as inspiration only, not as a runtime dependency.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/tiaokedan/scripts/tiaokedan.sh`: already dispatches `render` through skill-local Python and can be extended with help/PDF flags while preserving the public command.
- `skills/tiaokedan/scripts/tiaokedan_renderer.py`: already validates frontmatter, body section, fixed 8-column table, required markers, unsupported raw Typst/HTML, deterministic Typst generation, and optional expected-Typst comparison.
- `skills/tiaokedan/templates/tiaokedan.md`: accepted teacher-facing Markdown example for `SKILL.md` and README/index pointers.
- `skills/tiaokedan/templates/tiaokedan-reference.pdf`: proves local Typst can compile the accepted reference in the current environment; Phase 40 should re-run PDF generation through the public workflow rather than rely only on this artifact.

### Established Patterns
- Existing document skills keep `SKILL.md` short and move long field/renderer rules into skill-local `references/`.
- Runtime differences are captured inside one canonical `SKILL.md` table; v1 does not add standalone adapter files or generated wrappers.
- PDF readiness is explicit: a real compile command must succeed and produce a non-empty PDF before final success is claimed.
- Clean public output should be boring and teacher-facing; diagnostics, model/status data, logs, temp files, comparison artifacts, and failure evidence belong in hidden/debug-only locations.

### Integration Points
- Phase 40 implementation will likely touch `skills/tiaokedan/SKILL.md`, `skills/tiaokedan/scripts/tiaokedan.sh`, `skills/tiaokedan/scripts/tiaokedan_renderer.py`, README/index docs, compatibility/docs entries, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, and `.planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md`.
- Do not modify Phase 37/38/39 accepted templates or verification evidence unless a downstream phase explicitly opens a correction.
- Keep runtime independence checks: no sibling skill script calls, no imports from sibling directories, and copied `skills/tiaokedan/`-only verification should still pass.

</code_context>

<specifics>
## Specific Ideas

- Treat `tiaokedan.md` as the teacher-editable source of truth and the final PDF as a strict post-review artifact.
- Keep questions short and practical: ask what is missing for the form, not how to tune Typst.
- The public workflow should feel similar to existing document skills: inspect Markdown, render Typst, optionally compile PDF, verify outputs.
- The successful output boundary for `tiaokedan` can be simpler than `teaching-design-package`, but it should inherit the same honesty: no debug leakage into teacher-facing delivery.

</specifics>

<deferred>
## Deferred Ideas

- Multiple school-specific `调课单` variants remain TKD-FUT-01.
- Batch generation for many adjustment forms remains TKD-FUT-02.
- Spreadsheet import remains TKD-FUT-03.
- OCR/photo extraction, arbitrary form discovery, approval grids, signature boxes, opinion columns, and extra school approval workflows remain out of scope for v1.16 Phase 40.

</deferred>

---

*Phase: 40-调课单 Skill Workflow and PDF Gate*
*Context gathered: 2026-06-22*
