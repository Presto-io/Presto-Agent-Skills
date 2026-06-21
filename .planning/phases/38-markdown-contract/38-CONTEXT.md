# Phase 38: 调课单 Markdown Contract - Context

**Gathered:** 2026-06-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 38 delivers the teacher-reviewable Markdown contract for the accepted `调课单` form facts. It should create a hand-authored Markdown fixture and supporting contract decisions that express the same visible facts as the Phase 37 Typst baseline without raw Typst. Markdown-to-Typst renderer code, deterministic generated-output comparison, canonical `SKILL.md`, runtime adapter notes, PDF delivery gates, README/index updates, and broader form variants remain Phase 39-40 or future scope.

</domain>

<decisions>
## Implementation Decisions

### Markdown Shape
- **D-01:** The Phase 38 fixture should use `YAML frontmatter + body`, matching the repository-wide Markdown normalization discipline while keeping field names skill-local to `tiaokedan`.
- **D-02:** YAML frontmatter should carry document-level facts that a teacher can review directly: `title`, `recipient`, `department`, `date`, and optional `status` or `review_notes` if useful for marking draft state.
- **D-03:** The body should keep the explanatory paragraph as visible Markdown text under a clear heading such as `## 调课说明`, not as a renderer-generated hidden default.
- **D-04:** The adjustment rows should be represented as a normal Markdown table with exactly the Phase 37 visible columns: `序号`, `班级`, `课程`, `原上课时间`, `原授课教师`, `调整后上课时间`, `调整后上课教师`, `备注`.
- **D-05:** The fixture should preserve teacher-facing line breaks in time cells with simple Markdown-readable notation. Use visible `<br>` inside table cells only where the accepted baseline intentionally line-breaks a value, such as row 1 time cells.

### Teacher-Maintained Facts vs Renderer Defaults
- **D-06:** Teacher-maintained facts are the visible document title, recipient, explanatory reason text, all table cell values, department/signature text, and date.
- **D-07:** Renderer-only defaults must stay out of teacher-maintained Markdown fields: A4 landscape page setup, font fallback lists, point sizes, table column width ratios, cell padding, strokes, vertical spacing, right-aligned signature block width, Typst helper names, and PDF compile details.
- **D-08:** The contract may document those renderer defaults in prose for downstream implementers, but the Markdown fixture itself should not require teachers to write raw Typst, CSS-like layout knobs, or font declarations.
- **D-09:** Phase 38 should not add new approval grids, signature boxes, opinion columns, multiple-school variants, batch fields, or renderer configuration switches. Those would change the accepted Phase 37 form surface.

### Unknown And Missing Values
- **D-10:** Required unknown values should be marked inline and visibly with the skill-local marker `{{待补充: 说明}}`, close to the missing fact.
- **D-11:** AI-drafted but teacher-editable prose may use `{{AI草稿: 说明}}`, following the existing document-skill pattern, but the accepted Phase 38 fixture should prefer concrete facts from Phase 37 unless a field is intentionally demonstrating review behavior.
- **D-12:** Final rendering in later phases must treat unresolved `{{待补充: ...}}` markers as non-final. Phase 38 only defines the contract; Phase 39 will implement non-zero validation failures.
- **D-13:** Empty optional table cells, such as `备注`, may remain empty when the accepted form fact is genuinely blank. They should not be rewritten as `{{待补充}}` unless the teacher must provide a missing fact.

### Fixture Content
- **D-14:** The hand-authored fixture should mirror the Phase 37 accepted baseline facts: `调课说明`, `教务处：`, the locked explanatory paragraph, the two example adjustment rows, `电气工程系`, and `2026年6月21日`.
- **D-15:** The fixture should be inspectable as plain Markdown before any Typst/PDF generation. It should be copyable and reviewable without depending on a script, hidden generated JSON, or sibling skill resources.
- **D-16:** If Phase 38 creates a longer reference file in `skills/tiaokedan/references/`, it should define the field contract, required/optional fields, marker semantics, and renderer-default boundary. It should not implement parsing or rendering.

### Claude's Discretion
- Downstream planning may choose the exact filenames for the fixture and contract reference within `skills/tiaokedan/templates/` and `skills/tiaokedan/references/`, provided they follow repository directory ownership rules and are easy for teachers and later agents to find.
- Downstream planning may choose whether to include a minimal example of `{{待补充: ...}}` in a separate reference snippet rather than the main accepted fixture, as long as TKD-MD-03 is clearly documented.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope
- `.planning/ROADMAP.md` — Phase 38 goal and success criteria.
- `.planning/REQUIREMENTS.md` — TKD-MD-01, TKD-MD-02, and TKD-MD-03 requirements.
- `.planning/PROJECT.md` — v1.16 milestone purpose, constraints, and Markdown-first document workflow discipline.
- `.planning/STATE.md` — current phase and resume status.

### Accepted Form Baseline
- `.planning/phases/37-typst-baseline/37-CONTEXT.md` — locked visible form facts, typography intent, table shape, and scope boundaries carried into Markdown.
- `.planning/phases/37-typst-baseline/37-DISCUSSION-LOG.md` — audit trail showing why no approval grid or extra form fields were added.
- `.planning/phases/37-typst-baseline/37-VERIFICATION.md` — evidence that the hand-authored Typst reference and PDF passed.
- `skills/tiaokedan/templates/tiaokedan-reference.typ` — accepted hand-authored Typst surface that Phase 38 Markdown must be able to express.
- `skills/tiaokedan/templates/tiaokedan-reference.pdf` — non-empty PDF evidence for the accepted visual baseline.

### Repository Contracts
- `AGENTS.md` — Simplified Chinese response rule and repository editing conventions.
- `docs/markdown-normalization-contract.md` — shared `YAML frontmatter + body` intermediate discipline and review-marker expectations.
- `docs/directory-spec.md` — ownership rules for `skills/<skill-name>/templates/`, `references/`, `scripts/`, and `SKILL.md`.

### Local Pattern References
- `skills/end-of-term-teaching-materials/templates/end-of-term-full.md` — example of visible `{{AI草稿: ...}}` review markers in teacher-facing Markdown.
- `skills/teaching-design-package/templates/teaching-design-package-full.md` — example of a large teacher-reviewable Markdown source with frontmatter and body-owned facts.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/tiaokedan/templates/tiaokedan-reference.typ`: authoritative Phase 37 field list and example content for the Markdown fixture.
- `docs/markdown-normalization-contract.md`: establishes that each skill owns its own metadata fields and marker syntax; Phase 38 should not invent a universal schema.
- `skills/end-of-term-teaching-materials/templates/end-of-term-full.md`: shows the existing readable review-marker style that can inspire `{{待补充: ...}}` and `{{AI草稿: ...}}`.

### Established Patterns
- Document workflow skills keep a persistent Markdown intermediate before target generation.
- Renderer defaults and layout mechanics belong to skill-local code/templates/references, not teacher-maintained Markdown fields.
- Ambiguous or lossy content must remain visible and explicitly marked near the relevant fragment.
- Skill-local long rules belong under `skills/<skill-name>/references/`; templates should remain copyable or renderable artifacts, not long manuals.

### Integration Points
- Phase 38 should add Markdown-facing files under `skills/tiaokedan/templates/` and, if needed, `skills/tiaokedan/references/`.
- Phase 39 will consume this contract to implement parsing, validation, generated Typst output, and deterministic comparison against the Phase 37 baseline.
- Phase 40 will summarize this workflow in `skills/tiaokedan/SKILL.md` and connect runtime adapter notes plus repository discoverability.

</code_context>

<specifics>
## Specific Ideas

- The main fixture should read like a teacher-owned adjustment form source, not like a developer fixture packed with implementation comments.
- Keep the explanatory paragraph visible and editable because it is an actual form fact, not a computed renderer phrase.
- Preserve blank `备注` cells when the accepted baseline is blank.
- Use review markers only for uncertainty, not for fields that Phase 37 has already locked.

</specifics>

<deferred>
## Deferred Ideas

- Markdown-to-Typst conversion, parser implementation, generated Typst output, strict missing-field failures, and reference diffing belong to Phase 39.
- Canonical `skills/tiaokedan/SKILL.md`, runtime adapter notes, PDF workflow, clean output/diagnostic boundary, missing-information question list, README/index updates, and requirement traceability updates belong to Phase 40.
- Multiple school-specific `调课单` variants, batch generation, and spreadsheet import remain future requirements unless a later milestone explicitly scopes them.

</deferred>

---

*Phase: 38-调课单 Markdown Contract*
*Context gathered: 2026-06-21*
