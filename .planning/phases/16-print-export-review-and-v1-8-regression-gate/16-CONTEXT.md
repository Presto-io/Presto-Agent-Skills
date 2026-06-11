# Phase 16: Print Export Review and v1.8 Regression Gate - Context

**Gathered:** 2026-06-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 16 adds a print/export-friendly review surface and final v1.8 regression gate for the existing `school-presentation` offline HTML deck. It must let presenters or reviewers produce a PDF-oriented review output where reveal, mask, emphasis, sorting, inserted physical pages, section dividers, and gallery pagination can be inspected outside live playback.

This phase preserves the Markdown logical-slide source of truth, the offline single-file HTML primary output, fixed `16:9` / `4:3` slide-canvas behavior, Phase 14 playback-local presenter markup boundaries, and Phase 15 classroom/structured-layout authoring surface. It must not reopen PPTX, Keynote, editable PowerPoint export, hosted sharing, remote control, annotation persistence, or freeform HTML editing.

</domain>

<decisions>
## Implementation Decisions

### Review and Print/PDF Shape

- **D-01:** Phase 16 should add or formalize a review/print mode inside the same offline HTML deck, then use browser print/export to PDF as the human UAT artifact. Do not introduce a separate PDF renderer, PPTX/Keynote path, or office-suite automation for this phase.
- **D-02:** The print/PDF output is an expanded review state, not a live playback snapshot. It should show content in the state a teacher can inspect on paper or in a PDF viewer.
- **D-03:** Reveal content must be opened in the print/PDF review state.
- **D-04:** Masked answers must be visible in the print/PDF review state.
- **D-05:** Emphasis/correct-answer marks must remain visibly underlined in the print/PDF review state.
- **D-06:** Sorting exercises must print/export in the correct final order rather than the initial candidate order or an intermediate reveal state.

### Pagination and Gallery Review

- **D-07:** Automatically inserted physical pages, including overflow split pages and section or agenda-like inserted pages, must remain in the correct review/PDF page order.
- **D-08:** Gallery output must paginate from the card level. A gallery card must not be clipped by browser print pagination; if the gallery cannot fit on one printed page, it should break into readable card-level pages or card groups.
- **D-09:** Section title pages should be shown by default during live presentation/playback so the presenter can speak through chapter boundaries naturally.
- **D-10:** Print/PDF review must provide a visible control for whether section title pages are included. This choice belongs to the generated deck UI/review mode, not to raw Markdown authoring.
- **D-11:** Phase 16 verification and manual UAT must explicitly cover section title pages, middle inserted pages, and gallery page breaks, because these are the highest-risk visual review surfaces.

### Presenter Annotation Policy

- **D-12:** Presenter-local annotations are excluded by default from print/export review output.
- **D-13:** Phase 16 does not need annotation flattening. If flattening saved or live presenter marks ever becomes useful, treat it as a future capability with its own requirements because Phase 14 deliberately made markup playback-local session state.
- **D-14:** The review/PDF surface, manifest, and deterministic artifacts must not include `annotationState`, stroke data, markup palette state, pinned peek state, or other runtime-only UI state.

### Regression Gate

- **D-15:** Continue using the existing `skills/school-presentation/scripts/school-presentation.sh verify` gate and extend it for Phase 16. Do not make Playwright, screenshot checks, or automated browser-PDF generation part of the default gate.
- **D-16:** The extended `verify` gate should keep existing repeatable HTML hash checks, manifest hierarchy checks, workspace/playback/overview hooks, presenter markup verification, classroom structure verification, thumbnail ratio checks, flat-deck compatibility, size cap checks, and runtime-state leakage checks.
- **D-17:** Add deterministic checks for the print/review mode: review CSS or DOM hooks, expanded reveal/mask behavior, underlined emphasis visibility, sorted final-order print behavior, gallery card-level pagination hooks, section-title inclusion controls, section-divider/inserted-page print ordering, offline single-file boundaries, and fixed `16:9` / `4:3` canvas stability.

### Human Visual UAT

- **D-18:** The final manual review artifact is a PDF produced from the offline HTML deck's review/print mode.
- **D-19:** Manual UAT should explicitly inspect: reveal opened, masks visible, emphasis underlined, sort in correct order, section title page inclusion/exclusion behavior, gallery cards paginated without clipping, inserted middle pages present in order, and both fixed canvas ratios remaining stable.
- **D-20:** Human UAT is still required because Phase 16 changes printed/exported review surfaces, where CSS pagination can pass token checks while still looking wrong.

### Claude's Discretion

- The exact UI entry point and label for review/print mode may be chosen during planning and implementation as long as it is discoverable in the offline deck and does not add runtime-specific wrapper syntax.
- The exact CSS pagination mechanics for gallery cards and inserted pages may be chosen by the implementer, provided cards are not clipped and review pages remain readable.
- The exact verification token names may be chosen during implementation, provided they prove real rendered fixture behavior rather than dormant helper functions.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Active Phase Contract

- `.planning/ROADMAP.md` - Phase 16 goal, dependency on Phase 15, requirements SP-26 and SP-27, and success criteria for print/export review plus v1.8 regression.
- `.planning/REQUIREMENTS.md` - SP-26 and SP-27 define the pending print/export review and regression-gate requirements.
- `.planning/STATE.md` - Current milestone status, Phase 15 completion boundary, and Phase 16 ready-to-plan position.
- `.planning/PROJECT.md` - Project-wide constraints for Markdown source of truth, offline HTML-first presentation output, annotation discipline, and out-of-scope office exports.

### School Presentation Implementation

- `skills/school-presentation/SKILL.md` - Canonical skill behavior, Markdown contract, playback model, reveal/mask/emphasis rules, presenter markup boundary, verification expectations, runtime adapter notes, and current deferred print/export wording.
- `skills/school-presentation/scripts/school-presentation.sh` - Renderer, parser, fixed canvas CSS, preview/playback/overview state, current `@media print`, section divider print hooks, manifest output, and `cmd_verify()` regression gate.
- `skills/school-presentation/templates/school-presentation-full.md` - Full verification fixture that should be extended to prove Phase 16 review/print behavior across reveal, mask, emphasis, sort, gallery, inserted pages, and structured layouts.

### Prior Accepted v1.8 Phases

- `.planning/phases/14-presenter-markup-tools/14-CONTEXT.md` - Phase 14 decisions for playback-local markup, no mutation of authored/review artifacts, page-scoped annotation state, event priority, and fixed-canvas annotation alignment.
- `.planning/phases/15-classroom-interaction-and-structured-layout-extensions/15-CONTEXT.md` - Phase 15 decisions for peek, sort, animate step, timeline/cards/gallery/smartart, semantic icons, section dividers, and deterministic verification boundaries.
- `.planning/phases/15-classroom-interaction-and-structured-layout-extensions/15-01-SUMMARY.md` - Completed Phase 15 implementation summary, verification evidence, manual visual acceptance, and Phase 16 readiness notes.
- `.planning/phases/15-classroom-interaction-and-structured-layout-extensions/15-VERIFICATION.md` - Phase 15 automated and manual verification evidence that Phase 16 must preserve.
- `.planning/phases/15-classroom-interaction-and-structured-layout-extensions/15-REVIEW.md` - Clean-after-fix review record and unknown-directive safety note.

### Prior Presentation Baseline

- `.planning/milestones/v1.6-ROADMAP.md` - Accepted Phase 9/10 playback, preview, hierarchy, ordered reveal, emphasis, and answer-mask behavior.
- `.planning/milestones/v1.6-REQUIREMENTS.md` - Completed SP-10 through SP-16 requirements that Phase 16 must not regress.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `skills/school-presentation/scripts/school-presentation.sh`: existing `@media print` already hides app chrome, thumbnail rail, overview, playback, and `.page-source`, then prints preview-stage slides. Phase 16 should formalize this into review/print behavior instead of starting from scratch.
- `skills/school-presentation/scripts/school-presentation.sh`: section divider records already include `data-print-optional`, `print_optional`, `skip-section-dividers`, and `section-divider-toggle`; these are natural integration points for review print ordering and the user-controlled print inclusion policy for section title pages.
- `skills/school-presentation/scripts/school-presentation.sh`: preview-stage rendering already uses final/show-all reveal state, while playback owns progressive step state. Review/print should lean toward the preview/final state, with additional rules for masks, emphasis, sorting, and gallery pagination.
- `skills/school-presentation/scripts/school-presentation.sh`: `cmd_verify()` already writes a deterministic verification manifest and checks repeatability, hierarchy, reveal kinds, workspace/playback/overview hooks, presenter markup, classroom structure, thumbnail ratio, flat compatibility, and runtime-state leakage.
- `skills/school-presentation/templates/school-presentation-full.md`: current fixture already contains reveal, mask, emphasis, sort, gallery, structured layouts, section dividers, and review-focused slides that can be extended for print/PDF review coverage.

### Established Patterns

- Markdown remains the source of truth; generated review/print state must be derived from rendered deck behavior, not from authoring new raw HTML controls in Markdown.
- The renderer keeps `sections -> logical_slides -> physical_pages -> reveal_steps` as the manifest hierarchy. Review/PDF ordering must respect physical-page order, including automatically inserted and overflow-split pages.
- Preview workspace and overview are inspectable/static views; playback owns progressive reveal, mask clicks, peek hover/click, and presenter-local tools. Print review should be inspectable and deterministic, not interactive.
- Presenter markup is playback-local session state. It must not leak into Markdown, `.page-source`, manifest, preview, overview, thumbnails, review mode, or PDF output.
- The deck stays offline and single-file. Review/print mode should not require network dependencies or external services.

### Integration Points

- Extend render CSS/DOM around the existing print styles so print/PDF output has explicit review semantics rather than relying on incidental preview-state behavior.
- Add review/print hooks to the generated HTML so `verify` can prove that reveal, mask, emphasis, sorting, gallery pagination, section title page inclusion controls, and section/inserted-page ordering are covered.
- Extend `school-presentation-full.md` if necessary with gallery and inserted-page cases that expose browser pagination risks.
- Extend `cmd_verify()` with Phase 16 checks and write new booleans to `verification-manifest.json`, while preserving existing `presenter_markup_verified` and `classroom_structure_verified` gates.
- Update `skills/school-presentation/SKILL.md` with runtime-neutral Phase 16 behavior, PDF manual UAT instructions, and OpenClaw/Hermes-compatible safety boundaries.

</code_context>

<specifics>
## Specific Ideas

- User clarified the print/PDF review state should reveal all reveal blocks, show masked answers, preserve underlined emphasis marks, put sorting exercises in the correct final order, and paginate gallery content from cards rather than clipping cards.
- User wants section title pages shown by default during live presentation/playback, but print/PDF review should expose a button for whether section title pages are included.
- User wants the final human review artifact to be PDF, with special attention to section title pages, automatically inserted middle pages, and gallery page breaks.
- User chose to continue the existing `verify` path rather than adding a browser screenshot or Playwright default gate.
- User chose default exclusion of presenter annotations from print/export.

</specifics>

<deferred>
## Deferred Ideas

- Annotation flattening or saved presenter markup artifacts are deferred. Phase 16 excludes presenter annotations by default; any flattened annotation export should be its own future capability.
- Automated browser-PDF generation, Playwright screenshot gates, visual regression screenshots, PPTX export, Keynote export, editable PowerPoint output, hosted sharing, remote control, and multi-device synchronization remain out of scope for Phase 16.

</deferred>

---

*Phase: 16-Print Export Review and v1.8 Regression Gate*
*Context gathered: 2026-06-11*
