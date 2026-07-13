# Phase 43: Editable PPTX Renderer and Pagination - Context

**Gathered:** 2026-07-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Render the validated Phase 42 logical document model into a non-empty, editable, template-consistent PPTX. This phase owns logical-to-physical pagination, editable text/media/table/timeline/gallery/code objects, speaker notes, the repeatable `render` command, and the clean two-artifact public delivery boundary. It does not add new layouts, arbitrary styling, complex animation, runtime adapter documentation, aggregate verification, or manual visual UAT; those remain out of scope or belong to Phase 44.

</domain>

<decisions>
## Implementation Decisions

### Text and code pagination
- **D-01:** Fill each physical slide with complete top-level blocks in source order. Move the next complete block to a new physical slide when it does not fit; split inside a block only when that single block exceeds a whole-slide budget.
- **D-02:** Split oversized paragraphs at sentence boundaries whenever possible. Split lists only between complete list items. A last-resort hard split may occur only when one sentence or list item cannot fit, and should prefer punctuation or a natural pause rather than an arbitrary character boundary.
- **D-03:** Split code only between complete source lines. An over-wide line uses text-frame soft wrapping without inserting a newline into the editable code text; pagination accounts for the resulting display lines.
- **D-04:** When a block with a visible `###` subheading spans physical slides, repeat that same subheading on every fragment without a continuation suffix or alternate continuation style.
- **D-05:** All physical slides derived from a logical slide retain its original `##` slide title. Except for an existing table name as defined below, continuation pages do not add visible continuation markers.

### Tables, timelines, and contents
- **D-06:** A table is one composite block with two independent parts: an optional table name and the editable table body. The table name is unrelated to the slide's `##` title.
- **D-07:** Table continuation pages repeat the table header. If the source table has a table name, continuation pages show `原表名（续）`; if it has no table name, they do not synthesize `表格（续）`. An empty editable table-name placeholder is still retained.
- **D-08:** Keep each table data row intact. Cell text may wrap. Control physical, visible orphan lines through bounded type-size and reflow adjustments: try fitting within the template range, and if shrinking still leaves a visually isolated line, increasing type size to induce a better multi-line wrap is allowed. Do not truncate content or fail solely because of a visual orphan line.
- **D-09:** Timeline pagination is elastic and globally balanced across all physical pages for that logical timeline, not patched only between adjacent pages. Preserve item order, normally keep at least three nodes on each physical page, absorb a one-item continuation into the previous page when it fits, or move two additional nodes forward so the continuation has at least three. Fewer than three is allowed only when the complete logical timeline itself has fewer than three nodes.
- **D-10:** Contents pagination is elastic, continuously numbered, and globally balanced across every contents page. All page titles remain `目录` without a continuation suffix. First make entry counts as even as possible, then adjust for wrapped-title height so pages carry similar visual weight; obvious many-versus-few page imbalance and orphan entries are forbidden.

### Editable object contract
- **D-11:** Table data must use native PPTX table objects. Decorative shapes may be layered around a table, but editable data may not be replaced by a matrix of text boxes and rectangles.
- **D-12:** Each timeline node is an editable group containing its marker, time, title, and description. The main timeline axis remains separate. Group contents must remain native editable objects, and PowerPoint/WPS behavior must be researched and verified.
- **D-13:** Each gallery image and its caption placeholder form one editable group. Images use contain placement and remain replaceable picture objects.
- **D-14:** Retain an empty editable caption placeholder even when image alt text is empty, and retain an empty editable table-name placeholder when no table name is authored. Empty placeholders must not show prompt text during playback. This supersedes the manifest's current `gallery.caption.empty_slot: hide` declaration and requires a controlled manifest/template-contract reconciliation.
- **D-15:** Preserve `**bold**` and `==highlight==` as native editable text runs inside a continuous text frame. Bold uses native run weight; highlight uses the theme-controlled run-level treatment. Do not break highlighted text into independently positioned text boxes and background shapes.
- **D-16:** Speaker notes from one logical slide are copied to every physical slide produced from it, while slides without notes do not gain accidental notes.

### Failure, replacement, and public output
- **D-17:** Invalid Markdown or missing media may still produce a best-effort PPTX at the requested public path. The command must exit non-zero, print a prominent bounded error summary, and require the calling agent to state the abnormalities and affected slides explicitly. The artifact must never be described as a successful render.
- **D-18:** The best-effort PPTX uses the requested final filename and contains no injected warning slide, banner, or watermark. After correcting Markdown, the user can rerender over it; the agent may also advise manual correction in the editable PPTX after the automated workflow ends.
- **D-19:** Replace an existing target atomically: build and validate a same-directory temporary PPTX, then replace the target in one operation. A crash or unrecoverable build failure before publication preserves the old target. Do not emit public backup files.
- **D-20:** The standard successful public delivery is exactly two files with the same filename stem: one editable Markdown source and one PPTX. Preserve Markdown content as authored. Manifests, logical JSON, diagnostics, logs, evidence, and temporary files stay hidden or in explicit verification workdirs.
- **D-21:** D-20 intentionally supersedes the prior default assumption in PPTX-13 that the Markdown copy is only emitted when explicitly requested. Phase planning must reconcile the requirement wording and command contract before implementation.

### Claude's Discretion
- Choose the concrete pagination cost function, sentence-boundary tokenizer, visual-weight estimator, and bounded font-adjustment sequence, provided they implement the semantic and global-balance rules above deterministically.
- Choose the implementation route for editable grouped shapes and run-level highlight after researching current `python-pptx` and OOXML support; the observable editable-object contract is locked.
- Choose exact CLI flag names and hidden workdir structure while preserving the two-file public output and non-zero best-effort failure semantics.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project scope and phase requirements
- `.planning/PROJECT.md` — v1.17 goal, editable-output value, and project-wide skill boundaries.
- `.planning/REQUIREMENTS.md` — PPTX-01 through PPTX-13, VER-03, and SKILL-03; reconcile PPTX-13 with D-20/D-21.
- `.planning/ROADMAP.md` — Phase 43 boundary, success criteria, and separation from Phase 44 verification/runtime/UAT work.
- `.planning/STATE.md` — Current position and known implementation concerns for notes, tables, placeholders, fitting, and media.

### Locked prior-phase contracts
- `.planning/phases/41-standard-template-and-manifest/41-CONTEXT.md` — Template ownership, slot mapping, manual calibration, and validation decisions.
- `.planning/phases/42-markdown-contract-and-full-fixture/42-CONTEXT.md` — Logical block semantics, notes propagation, media behavior, title rules, and Phase 43 handoff decisions.
- `.planning/phases/42-markdown-contract-and-full-fixture/42-03-SUMMARY.md` — Final parser and secure-I/O state handed to the renderer.
- `skills/school-pptx/references/template-contract.md` — Controlled layout/slot/budget contract; reconcile empty caption and table-name placeholders with D-14.
- `skills/school-pptx/references/markdown-contract.md` — Canonical authoring contract and exact logical-model handoff. Phase 43 must not reparse Markdown.

### Runtime assets and integration surfaces
- `skills/school-pptx/templates/standard-school.manifest.yaml` — Machine source for layout ids, placeholder mappings, geometry, and text budgets.
- `skills/school-pptx/templates/standard-school.pptx` — Controlled runtime template whose native slide layouts and decorative assets must be preserved.
- `skills/school-pptx/scripts/markdown_contract.py` — Existing validated logical-document producer and diagnostics model.
- `skills/school-pptx/scripts/school-pptx.sh` — Existing public dispatcher to extend with the repeatable `render` command.
- `skills/school-pptx/fixtures/school-pptx-full.md` — Canonical full-deck pagination and editability fixture.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/school-pptx/scripts/markdown_contract.py`: Reuse its source-located logical model, validated media descriptors, notes, block structure, contents entries, implicit closing slide, overflow evidence, and bounded diagnostics. Do not build a second parser.
- `skills/school-pptx/templates/standard-school.manifest.yaml`: Reuse semantic slot ids, native layout XML mappings, geometry, font bounds, overflow policy, and continuation metadata as the renderer's machine contract.
- `skills/school-pptx/templates/standard-school.pptx`: Use the controlled theme and native layouts as the object/rendering base instead of recreating visual styling in code.
- `skills/school-pptx/scripts/school-pptx.sh`: Add `render` without changing the established `validate`, `example`, `template-report`, and `info` surfaces.

### Established Patterns
- Public Markdown contains semantics only; all geometry, fonts, colors, decoration, footer behavior, and bounded type behavior remain template-owned.
- The logical model already contains ten explicit authorable layouts plus exactly one implicit closing slide, resolved media paths, captions, notes, tables, timeline rows, code, and overflow evidence.
- Existing commands aggregate locatable validation errors and fail non-zero while retaining safe diagnostic metadata.
- Fixed outputs are published atomically and safely; Phase 42's descriptor-confined example writer is a relevant precedent for target replacement and path-collision handling.

### Integration Points
- The new render path starts after canonical validation and consumes the returned logical model directly.
- Pagination must read per-slot budgets from the manifest, produce a deterministic logical-to-physical mapping internally, and feed editable object emitters for each layout.
- Notes and grouped editable objects may require targeted OOXML support beyond high-level `python-pptx`; research must confirm round-trip behavior before the plan locks implementation details.
- Public publication must coordinate the same-stem Markdown and PPTX pair while keeping logical JSON and renderer evidence out of the delivery root.

</code_context>

<specifics>
## Specific Ideas

- Pagination quality is judged visually, not only by character counts: directory pages and timeline pages should feel equally weighted, and visible orphan lines/items are unacceptable.
- When a timeline continuation would contain one node, rebalance the entire sequence rather than merely moving one item between the last two pages.
- Empty table-name and caption slots are intentional editing affordances even though they contain no visible authored text.
- Best-effort invalid output is deliberately editable and uses the final filename so the user can either rerender over it or finish corrections manually after the workflow.
- An unpackaged `.planning/spikes/MANIFEST.md` exists but was not treated as validated input; package it through the spike wrap-up workflow before relying on it in planning.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within Phase 43 scope.

</deferred>

---

*Phase: 43-editable-pptx-renderer-and-pagination*
*Context gathered: 2026-07-14*
