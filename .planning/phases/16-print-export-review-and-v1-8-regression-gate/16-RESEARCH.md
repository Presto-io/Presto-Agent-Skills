# Phase 16 Research: Print Export Review and v1.8 Regression Gate

**Milestone:** v1.8 School Presentation Continuation
**Date:** 2026-06-11
**Status:** Research complete
**Scope:** Repository-internal research; no external dependency research needed for this planning slice.

## Question

What should Phase 16 implement so the generated `school-presentation` offline HTML deck has a print/export-friendly review state, while preserving the existing Markdown source of truth, offline single-file output, fixed slide canvas, Phase 14 presenter-markup boundary, Phase 15 classroom/structure behavior, and deterministic verification gate?

## Findings

- Phase 16 has a complete context file with locked decisions: review/print behavior belongs inside the same offline HTML deck, browser PDF is the human UAT artifact, reveal/mask/emphasis/sort should be expanded into inspectable final review state, section title pages are visible by default during live playback, and presenter annotations are excluded by default.
- `skills/school-presentation/scripts/school-presentation.sh` already contains a usable print base:
  - `@media print` hides app chrome, thumbnail rail, overview, playback, and `.page-source`, then prints preview-stage slides.
  - Section divider records already carry `data-print-optional`, `print_optional`, `skip-section-dividers`, `hide-section-dividers`, and `section-divider-toggle` hooks.
  - Preview-stage rendering already tends toward final/show-all content, which is the right semantic base for a review/print state.
- Phase 16 should formalize the existing print path into an explicit review mode rather than introducing a parallel PDF renderer, office export path, or browser automation dependency.
- Sorting output already has `sort-rank` and `sort-final` reveal kinds plus `is-sorted` class behavior in playback. Print/review should deterministically expose the final sorted order, not the initial candidate state or an intermediate rank-only state.
- Gallery CSS already uses `break-inside: avoid` / `page-break-inside: avoid` on `.gallery-compare .gallery-item`, but Phase 16 needs stronger contract-level hooks and verification so gallery card-level pagination is not merely incidental.
- `cmd_verify()` already proves repeatable HTML hashes, manifest hierarchy, reveal kinds, workspace/playback/overview hooks, presenter markup, classroom structure, thumbnail ratio, flat compatibility, and runtime-state non-leakage. Phase 16 should extend this gate with print/review-specific booleans and rendered-token checks.
- `skills/school-presentation/templates/school-presentation-full.md` already exercises reveal, mask, emphasis, sort, gallery, section dividers, inserted physical pages, structured layouts, presenter markup, and fixed canvas behavior. It should be extended only where necessary to expose print/PDF risks such as gallery page breaks and section divider inclusion/exclusion.
- `skills/school-presentation/SKILL.md` currently defers export/print capability. Phase 16 should replace that deferred wording with runtime-neutral review/print behavior, manual PDF UAT steps, and OpenClaw/Hermes-compatible safety boundaries.

## Decision

Plan Phase 16 as a review/print formalization and regression-gate slice:

1. Add a discoverable review/print mode or print-control entry in the existing generated offline HTML.
2. Ensure print/review output expands reveal blocks, shows masks, preserves visible emphasis underlines, prints sorting exercises in final order, and excludes presenter annotations.
3. Keep section title pages visible by default in playback/workspace, while providing generated-deck controls for including or excluding section title pages in print/PDF review.
4. Strengthen print CSS and DOM hooks for inserted physical pages and gallery card-level pagination.
5. Extend `cmd_verify()` with `print_review_verified` and v1.8 regression checks while preserving the existing deterministic gate.
6. Update the fixture and canonical skill docs so future agents can execute Phase 16 without adding runtime-specific wrapper syntax or reopening PPTX/Keynote/export scope.

## Implications

- No separate PDF renderer, Playwright screenshot gate, automated browser-PDF default gate, PPTX, Keynote, hosted sharing, or annotation flattening is needed for Phase 16.
- Review/print behavior must be derived from rendered deck state and generated UI controls, not from new raw HTML authoring in Markdown.
- Manifest and deterministic artifacts must remain free of `annotationState`, stroke data, markup palette state, pinned peek state, hover state, and other runtime-only UI state.
- Manual UAT remains required after script verification because CSS pagination can pass token checks while still looking wrong in browser print/PDF output.

## Source Notes

- `.planning/phases/16-print-export-review-and-v1-8-regression-gate/16-CONTEXT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/14-presenter-markup-tools/14-CONTEXT.md`
- `.planning/phases/15-classroom-interaction-and-structured-layout-extensions/15-CONTEXT.md`
- `.planning/phases/15-classroom-interaction-and-structured-layout-extensions/15-01-SUMMARY.md`
- `.planning/milestones/v1.6-ROADMAP.md`
- `.planning/milestones/v1.6-REQUIREMENTS.md`
- `skills/school-presentation/SKILL.md`
- `skills/school-presentation/templates/school-presentation-full.md`
- `skills/school-presentation/scripts/school-presentation.sh`
