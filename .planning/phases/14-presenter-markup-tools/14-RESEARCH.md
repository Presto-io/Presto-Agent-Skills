# Phase 14 Research: Presenter Markup Tools

**Milestone:** v1.8 School Presentation Continuation
**Date:** 2026-06-11
**Status:** Research complete
**Scope:** Repository-internal research; no external dependency research needed for this planning slice.

## Question

What should Phase 14 implement so the existing `school-presentation` playback view gets presenter-local pointer, pen, highlighter, eraser, and clear/reset tools without changing authored Markdown, preview workspace content, manifest hierarchy, deterministic review output, or accepted Phase 9/10 playback behavior?

## Findings

- Phase 14 already has a complete context file with locked UX decisions: compact iPad-style floating palette, four edge/side placement families, optional follow/peek behavior, toggle-selected pen/highlighter tools, intentional eraser/clear controls, and page-scoped session persistence.
- The renderer currently builds playback pages by cloning `.page-source` into `#playback-stage` through `buildStageShell()` and `clonePageInto()`. This is the right integration point for a playback-only overlay because preview, overview, thumbnails, source Markdown, and manifest data are all generated elsewhere.
- The fixed canvas model is already centralized through `SLIDE_DESIGN_WIDTH`, `SLIDE_DESIGN_HEIGHT`, `stageScaleFor()`, `fitStage()`, and `.slide-scale-shell`. Annotation coordinates should be stored in slide design coordinates, then rendered through a layer that scales with the shell.
- Existing click-zone navigation uses fixed `.playback-zone` buttons. Drawing tools must temporarily disable those zones while keeping keyboard left/right and PageUp/PageDown navigation intact.
- Existing classroom interactions include reveal, mask, emphasis, peek/hover, and sort behaviors. Phase 14 should arbitrate pointer events so drawing gestures win only when a drawing or eraser tool is active; passive pointer and non-drawing tools must not break mask click reveal or peek behavior.
- A browser-native SVG annotation layer is a good fit for this phase: it is offline, deterministic, easy to scale in design coordinates, can render pen/highlighter strokes as paths, can keep pointer-events local to playback, and does not require any runtime dependency.
- The verification path should stay deterministic. It can prove that markup controls and script hooks are present, that manifest output still excludes annotation data, and that previous workspace/playback/reveal/mask tokens still pass. Manual or browser visual UAT remains useful after implementation because this is a live UI feature.

## Decision

Plan Phase 14 as a playback-overlay slice:

1. Add a session-local annotation state model keyed by physical `page_id`.
2. Render an SVG annotation layer as a playback-only sibling of the cloned slide inside `.slide-scale-shell`.
3. Add a compact floating markup palette in playback with pointer, pen, highlighter, eraser, clear current page, placement controls, and optional follow/edge behavior.
4. Add pointer/touch/mouse event arbitration so active drawing suppresses click-zone navigation while keyboard navigation remains available.
5. Extend `verify` with token and manifest checks that prove controls exist and Phase 9/10 behavior is still present.
6. Update the canonical skill and fixture text only to document/demo the playback-local capability, not to introduce annotation Markdown syntax.

## Implications

- Annotation state lives only in the rendered HTML session memory; reloads do not need to restore it in Phase 14.
- Page navigation must preserve annotations per physical page until explicit clear/reset.
- `showPlayback()`, `selectPage()`, and page transition code must not clear annotation state except through a deliberate presenter command.
- The annotation layer must be attached to the playback shell so page fade/swap animation includes visible annotations.
- The manifest should not gain authored annotation entries, and `page-source`, preview thumbnails, overview tiles, and static review behavior should stay annotation-free.
- Phase 16 can later decide whether print/export excludes or deterministically flattens annotations. Phase 14 should not pre-solve export semantics.

## Source Notes

- `.planning/phases/14-presenter-markup-tools/14-CONTEXT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/milestones/v1.6-ROADMAP.md`
- `.planning/milestones/v1.6-REQUIREMENTS.md`
- `skills/school-presentation/SKILL.md`
- `skills/school-presentation/templates/school-presentation-full.md`
- `skills/school-presentation/scripts/school-presentation.sh`
