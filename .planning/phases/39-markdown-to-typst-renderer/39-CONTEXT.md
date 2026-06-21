# Phase 39: 调课单 Markdown-to-Typst Renderer - Context

**Gathered:** 2026-06-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 39 delivers the first skill-local renderer for `tiaokedan`: a public command converts the finalized teacher-reviewed Markdown fixture into generated Typst, validates required contract facts, and deterministically compares that generated Typst against the accepted Phase 37 reference or a documented normalized equivalent. The renderer may borrow implementation ideas from existing repository skills, but runtime execution must stay inside `skills/tiaokedan/` and must not call sibling skill scripts or require sibling skill directories. Canonical `skills/tiaokedan/SKILL.md`, runtime adapter notes, final PDF workflow, clean public delivery directories, README/index/discoverability updates, and missing-information question documentation remain Phase 40 scope.

</domain>

<decisions>
## Implementation Decisions

### Public Renderer Surface
- **D-01:** Phase 39 should create a skill-local command surface under `skills/tiaokedan/scripts/`, with a simple render entry that accepts finalized Markdown and writes generated Typst. A shell wrapper plus a small local parser/renderer module is acceptable, but all code must live under `skills/tiaokedan/`.
- **D-02:** The public command should support the core shape `render --input <tiaokedan.md> --typ <output.typ>`. It may also support `--expected-typ <reference.typ>` for deterministic verification, following the local `gongwen` pattern, as long as the implementation is copied or rewritten locally rather than calling `gongwen`.
- **D-03:** Phase 39 should not add `--pdf`, clean delivery directories, runtime adapter explanations, `manifest`, `info`, or canonical skill workflow text unless the planner determines a minimal helper is unavoidable for the renderer test. PDF and packaging are Phase 40.
- **D-04:** The default fixture input for evidence is `skills/tiaokedan/templates/tiaokedan.md`; the accepted comparison reference is `skills/tiaokedan/templates/tiaokedan-reference.typ`.

### Markdown Parsing And Validation
- **D-05:** The renderer should parse the Phase 38 contract exactly enough to preserve teacher-facing facts: YAML frontmatter, `## 调课说明`, recipient line, explanatory paragraph, one Markdown adjustment table with the locked 8 columns, and closing department/date text.
- **D-06:** The accepted table column order is fixed: `序号`, `班级`, `课程`, `原上课时间`, `原授课教师`, `调整后上课时间`, `调整后上课教师`, `备注`. Reordered, missing, duplicated, or extra columns should be treated as malformed input and fail non-zero.
- **D-07:** Required facts from `skills/tiaokedan/references/markdown-contract.md` must be non-empty after trimming. Blank `备注` cells remain valid optional facts; blank required cells fail.
- **D-08:** Unresolved `{{待补充: ...}}` markers in required facts fail non-zero before final Typst is accepted. `{{AI草稿: ...}}` may also be treated as non-final for the renderer gate if it appears in required output facts, because Phase 39 is a finalized-Markdown render step.
- **D-09:** `<br>` in Markdown table cells is the only supported authoring-level line-break marker for this phase and should render to Typst `#linebreak()` in the corresponding table cell. Unsupported inline HTML, raw Typst, or layout directives in teacher-maintained fields should fail clearly rather than be passed through.

### Generated Typst And Deterministic Comparison
- **D-10:** Generated Typst should be deterministic for the same Markdown input: stable helper declarations, stable whitespace, stable row order, and no timestamps, random IDs, absolute temp paths, or environment-dependent comments.
- **D-11:** For the accepted fixture, generated Typst should match `skills/tiaokedan/templates/tiaokedan-reference.typ` byte-for-byte if feasible. If small source-format differences are unavoidable, Phase 39 must document a normalized-equivalent comparison rule in verification evidence and explain exactly what normalization ignores.
- **D-12:** The deterministic check should be runnable locally from committed files and record strict evidence such as `diff -u`, `cmp`, or SHA-256 comparisons. A passing compile/PDF check is not required in Phase 39 unless used only as extra evidence; generated Typst comparison is the required gate.
- **D-13:** The renderer must not overwrite the hand-authored reference. Generated output should go to an explicit output path or phase evidence path, keeping `tiaokedan-reference.typ` as the accepted baseline.

### Failure Semantics
- **D-14:** Missing required fields, missing required sections, malformed frontmatter, malformed table syntax, wrong column order, empty required cells, unresolved required markers, unsupported raw Typst/layout directives, unsupported inline HTML, and missing input files must exit non-zero with concise stderr messages.
- **D-15:** Error messages should name the failing contract area and the teacher-facing field where possible, for example `missing required frontmatter field: department`, `malformed adjustment table: expected 8 columns`, or `unresolved required marker in row 1 原上课时间`.
- **D-16:** Negative tests should cover at least one missing-field case, one malformed-section/table case, and one unsupported-value case to satisfy TKD-RENDER-04 without expanding into Phase 40 user-facing question guidance.

### Runtime Independence
- **D-17:** Runtime independence is a hard gate: no calls to sibling skill scripts, no imports from sibling skill directories, and no requirement that `gongwen`, `teaching-design-package`, `jiaoan-*`, or other skills be installed.
- **D-18:** Borrowed patterns should be noted as implementation inspiration only. The actual renderer, parser, comparison helper, and tests must be skill-local or use standard platform tools such as shell, Node/Python if already acceptable in the repo, `diff`, `cmp`, `sha256sum`/`shasum`, and optional `typst` when explicitly invoked.
- **D-19:** Verification should include an independence assertion, such as checking the new renderer files for sibling skill path references and running from a copied `skills/tiaokedan/`-only fixture location if the plan can keep that small.

### Claude's Discretion
- The planner may choose Bash, Node, or Python for the skill-local implementation based on the simplest maintainable fit with existing repository patterns.
- The planner may choose exact generated output/evidence paths under the Phase 39 directory, provided accepted templates remain hand-authored and no Phase 40 delivery structure is introduced.
- The planner may choose byte-for-byte comparison or a documented narrow normalization rule, but must prefer byte-for-byte if it can be achieved without contorting the renderer.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope
- `.planning/ROADMAP.md` — Phase 39 goal, success criteria, and Phase 40 boundary.
- `.planning/REQUIREMENTS.md` — TKD-RENDER-01, TKD-RENDER-02, TKD-RENDER-03, and TKD-RENDER-04.
- `.planning/PROJECT.md` — v1.16 milestone purpose, Markdown-first discipline, and independence constraints.
- `.planning/STATE.md` — current state and latest completed Phase 38 context.
- `AGENTS.md` — Simplified Chinese response rule, directory conventions, and skill authoring constraints.

### Accepted Inputs And Baselines
- `skills/tiaokedan/templates/tiaokedan-reference.typ` — accepted hand-authored Typst surface; Phase 39 generated Typst must target this.
- `skills/tiaokedan/templates/tiaokedan.md` — accepted teacher-readable Markdown fixture; primary renderer input for Phase 39 evidence.
- `skills/tiaokedan/references/markdown-contract.md` — required fields, optional `备注`, marker semantics, renderer-owned defaults, and Phase 38 non-goals.
- `.planning/phases/37-typst-baseline/37-VERIFICATION.md` — verified Typst/PDF baseline evidence and locked visual decisions.
- `.planning/phases/38-markdown-contract/38-VERIFICATION.md` — verified Markdown contract evidence and Phase 39/40 scope boundary checks.
- `.planning/phases/37-typst-baseline/37-CONTEXT.md` — visible form facts, typography intent, table shape, and deferred renderer scope.
- `.planning/phases/38-markdown-contract/38-CONTEXT.md` — Markdown shape, required/optional facts, marker behavior, and renderer-default boundary.

### Repository Contracts
- `docs/markdown-normalization-contract.md` — shared `YAML frontmatter + body` intermediate discipline and visible review-marker rule.
- `docs/directory-spec.md` — ownership rules for `skills/<skill-name>/scripts/`, `templates/`, and `references/`.

### Local Pattern References
- `skills/gongwen/scripts/gongwen_lib/commands.sh` — useful local pattern for `render --input --typ --expected-typ` and strict expected Typst comparison; do not call this script at runtime.
- `skills/teaching-design-package/scripts/teaching-design-package.sh` — useful pattern for hidden diagnostics, non-zero PDF/status semantics, and skill-owned helper boundaries; do not import or call it at runtime.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/tiaokedan/templates/tiaokedan-reference.typ`: authoritative Typst reference with helper declarations, table column widths, text styles, row content, line breaks, and closing signature placement.
- `skills/tiaokedan/templates/tiaokedan.md`: teacher-facing Markdown source that should round-trip into the accepted reference.
- `skills/tiaokedan/references/markdown-contract.md`: exact contract for required fields, optional blank remarks, markers, and renderer-owned defaults.

### Established Patterns
- Document workflow skills render from persistent Markdown intermediates rather than opaque one-step source-to-output conversions.
- Existing script entries use explicit `--input` and output flags, fail non-zero for invalid input, and keep comparison evidence deterministic.
- Long format and renderer rules belong in skill-local `references/`; executable helpers belong in skill-local `scripts/`; accepted templates stay in `templates/`.
- Runtime independence matters: previous package work allows borrowing format ideas from sibling skills but rejects runtime dependency on sibling skill scripts.

### Integration Points
- Phase 39 should add implementation files under `skills/tiaokedan/scripts/` and phase evidence under `.planning/phases/39-markdown-to-typst-renderer/`.
- Phase 39 should consume `skills/tiaokedan/templates/tiaokedan.md` and generate a Typst output that can be compared to `skills/tiaokedan/templates/tiaokedan-reference.typ`.
- Phase 40 will later summarize the command in `skills/tiaokedan/SKILL.md`, add PDF workflow, runtime adapter notes, question guidance, and repository discoverability.

</code_context>

<specifics>
## Specific Ideas

- Keep the first renderer intentionally narrow: one accepted form contract, one Markdown table shape, and one generated Typst target.
- Favor simple deterministic source generation over clever formatting. The comparison should be boring enough for future agents to trust.
- Do not hide teacher-facing uncertainty. Any unresolved `{{待补充: ...}}` should block final Typst generation rather than produce a plausible-looking form.
- Treat `备注` as the only accepted optional blank field in the current contract.

</specifics>

<deferred>
## Deferred Ideas

- Canonical `skills/tiaokedan/SKILL.md`, runtime adapter notes for Codex/Claude/Gemini/OpenCode/OpenClaw/Hermes, final PDF workflow, clean teacher-facing output directory, diagnostics visibility rules, missing-information question list, README/index/discoverability updates, and requirement traceability updates belong to Phase 40.
- Multiple school-specific `调课单` variants, batch generation, spreadsheet import, OCR/photo extraction, approval grids, signature boxes, opinion columns, and arbitrary form discovery remain future requirements.

</deferred>

---

*Phase: 39-调课单 Markdown-to-Typst Renderer*
*Context gathered: 2026-06-22*
