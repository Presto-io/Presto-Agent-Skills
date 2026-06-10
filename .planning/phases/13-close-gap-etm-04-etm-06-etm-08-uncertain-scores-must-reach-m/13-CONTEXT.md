# Phase 13: Close gap: ETM-04/ETM-06/ETM-08 - uncertain scores must reach Markdown review - Context

**Gathered:** 2026-06-10
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase closes the v1.7 audit gap where structured JSON containing uncertain score values such as `87?` fails before the user can see and review the Markdown intermediate. The phase should make uncertain scores reach `end-of-term-full.md` and `## 复核标记`, add verification for that flow, and keep final export readiness strict unless the user explicitly chooses an abnormal preview/export path.

This phase does not reopen the Phase 11 Markdown contract, does not add OCR or handwriting recognition, does not redesign the fixed templates, and does not replace the teacher review loop. It may update the renderer and verification where needed to show unresolved or failing scores with red highlighting in generated workbook/PDF artifacts.

</domain>

<decisions>
## Implementation Decisions

### Uncertain Score Data Shape
- **D-01:** Structured JSON should continue to represent uncertain recognized scores as inline strings such as `87?`.
- **D-02:** Do not replace the teacher-facing shape with nested score objects such as `{ value: 87, uncertain: true }` for this phase. The same `87?` marker should flow into the Markdown score table.
- **D-03:** Blank score cells remain blank and are not automatic review items.

### Markdown Generation Versus Export Readiness
- **D-04:** The `markdown` command should allow structured data containing `87?` so the generated `end-of-term-full.md` visibly contains the abnormal value and a matching `## 复核标记` row.
- **D-05:** `validate`, `render`, and normal final export readiness must remain strict: unresolved review markers or unresolved `?` score values cannot be treated as final-ready.
- **D-06:** Planner should separate "review Markdown generation" from "final export readiness" in validation modes. `export_ready=false` should allow reviewable uncertainty; `export_ready=true` should block unresolved uncertainty.

### Review Marker Handling
- **D-07:** If structured JSON contains a `?` score value but omits a matching `review_markers` entry, the script should automatically create the review marker rather than fail before Markdown generation.
- **D-08:** Auto-created review markers must include enough location detail for the agent to ask the teacher clearly: student, task or field, current value, and why confirmation is needed.
- **D-09:** The agent must still explain unresolved review items in conversation and ask one-by-one when clearing them.

### Abnormal PDF And Red Highlighting
- **D-10:** When unresolved review items or abnormal scores exist, the agent must tell the user clearly that problems remain and ask whether to generate a PDF anyway.
- **D-11:** If the user explicitly asks to generate anyway, the system may produce an abnormal review/preview PDF rather than a final-ready export.
- **D-12:** Abnormal PDF/workbook artifacts should highlight unresolved uncertain cells with red background or equivalent red warning styling so the teacher can inspect the problem directly.
- **D-13:** In the score book, generated `学期成绩` cells below 60 must also be highlighted red. This applies to the teacher-facing workbook and the PDF score-book representation where that derived field is shown.
- **D-14:** Manifest or verification output must distinguish abnormal review artifacts from final-ready artifacts. A generated abnormal PDF must not be reported as final submission-ready while `## 复核标记` is unresolved.

### Verification Scope
- **D-15:** Add a structured JSON uncertain-score fixture that proves `source.json` with `87?` can generate Markdown containing the inline value and matching `## 复核标记`.
- **D-16:** Add a negative final-export test showing the same unresolved Markdown blocks normal render/export readiness.
- **D-17:** Add a positive user-confirmed abnormal artifact path showing a red-highlighted abnormal PDF/workbook can be generated when explicitly requested.
- **D-18:** Verification should cover the below-60 `学期成绩` red-highlight rule for workbook and PDF-visible score-book output.

### Claude's Discretion
Planner and executor may choose the exact flag names, manifest schema fields, fixture filenames, and internal implementation for auto-created review markers and red highlighting, as long as they preserve the decisions above and keep normal final export readiness strict.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Planning
- `.planning/ROADMAP.md` - Defines Phase 13 insertion, dependency on Phase 12, and v1.7 active status.
- `.planning/REQUIREMENTS.md` - Defines ETM-04, ETM-06, and ETM-08 boundaries plus v1.7 out-of-scope OCR/template-marketplace constraints.
- `.planning/PROJECT.md` - Defines the v1.7 Markdown-first fixed-template workflow.
- `.planning/STATE.md` - Records current phase and the Phase 13 handoff.
- `.planning/v1.7-MILESTONE-AUDIT.md` - Records the blocker: structured JSON `87?` fails before Markdown review and recommends the closure phase.
- `.planning/phases/11-end-of-term-data-and-markdown-contract/11-CONTEXT.md` - Locks inline `87?`, `## 复核标记`, blank-score semantics, and one-by-one review behavior.
- `.planning/phases/12-fixed-template-rendering-and-verification/12-CONTEXT.md` - Locks fixed-template rendering, deterministic artifacts, workbook/PDF generation, and review-marker export blocking.
- `.planning/phases/12-fixed-template-rendering-and-verification/12-01-SUMMARY.md` - Summarizes current Phase 12 script commands and verification coverage.

### End-of-Term Skill
- `skills/end-of-term-teaching-materials/SKILL.md` - Current canonical skill workflow, runtime notes, export rule, and verification checklist.
- `skills/end-of-term-teaching-materials/references/data-contract.md` - Defines score data, uncertain values, and review marker shape.
- `skills/end-of-term-teaching-materials/references/rendering-style.md` - Defines fixed rendering rules and current review blocking expectations.
- `skills/end-of-term-teaching-materials/references/scorebook-template-notes.md` - Defines score-book workbook constraints and uncertainty handling.
- `skills/end-of-term-teaching-materials/templates/end-of-term-full.md` - Current Markdown intermediate template.
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh` - Shell command surface for example, validate, markdown, render, verify, manifest, info, and version.
- `skills/end-of-term-teaching-materials/scripts/render_package.py` - Current implementation where `validate_source_data()` rejects `?` before `generate_markdown()` can emit reviewable Markdown.
- `skills/end-of-term-teaching-materials/references/fixtures/end-of-term-source.json` - Clean source fixture to extend or pair with an uncertain-score fixture.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `render_package.py`: Already has separate `validate_source_data(data, export_ready=True)`, `generate_markdown(data)`, `validate_markdown(package, export_ready=True)`, `render()`, and `verify()` entry points. This makes it practical to split review-generation validation from final-export validation.
- `generate_markdown(data)`: Already writes `## 复核标记` rows from `review_markers`; it needs to allow `87?` and auto-create missing markers.
- `validate_markdown(package, export_ready=True)`: Already blocks unresolved `?` values and non-`无` review text for final readiness.
- `verify()`: Already builds an unresolved-review Markdown fixture to prove normal rendering blocks unresolved review; it can be extended with structured JSON uncertainty and abnormal artifact tests.
- Workbook/PDF generation code: Already writes deterministic table artifacts and `tables/scorebook.xlsx`; red highlighting should integrate here rather than create a separate workflow.

### Established Patterns
- Markdown remains the persistent reviewable source of truth before target outputs.
- Normal final export readiness is stricter than draft/review artifact generation.
- Manifest output is the right place to make warnings, review status, abnormal artifact status, and PDF compile state machine-readable.
- Skill-local fixtures and tests should be sanitized and deterministic.

### Integration Points
- Update `skills/end-of-term-teaching-materials/scripts/render_package.py`.
- Update `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh` only if a new abnormal-preview flag or command surface is needed.
- Update `skills/end-of-term-teaching-materials/SKILL.md` and references to document the abnormal PDF confirmation rule and red highlighting.
- Add or update fixtures under `skills/end-of-term-teaching-materials/references/fixtures/`.
- Update Phase 13 verification artifacts so the milestone audit can see ETM-04/ETM-06/ETM-08 closure evidence.

</code_context>

<specifics>
## Specific Ideas

- User explicitly chose `87?` as the structured and Markdown uncertainty marker.
- User explicitly wants the generated review product to show abnormal cells, not fail before the teacher sees them.
- User wants unresolved abnormal PDF generation to be allowed only after the agent tells the user the problems and asks whether to generate anyway.
- User added that score-book `学期成绩` cells below 60 should be highlighted red.

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within the Phase 13 closure scope.

</deferred>

---

*Phase: 13-Close gap: ETM-04/ETM-06/ETM-08 - uncertain scores must reach Markdown review*
*Context gathered: 2026-06-10*
