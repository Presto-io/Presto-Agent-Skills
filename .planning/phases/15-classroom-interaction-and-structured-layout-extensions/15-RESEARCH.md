# Phase 15 Research: Classroom Interaction and Structured Layout Extensions

**Milestone:** v1.8 School Presentation Continuation
**Date:** 2026-06-11
**Status:** Research complete
**Scope:** Repository-internal research; no external dependency research needed for this planning slice.

## Question

What should Phase 15 implement so `school-presentation` authors can use teacher-editable Markdown for peek hints, sorting exercises, restrained body-step animation, structured school layouts, semantic icons, and section-divider controls while preserving the existing offline single-file deck, fixed canvas model, playback behavior, and Phase 14 presenter-markup boundaries?

## Findings

- Phase 15 has a complete context file with locked decisions: use teacher-facing block directives, keep `process` under `::: smartart type=process :::`, keep sorting's existing candidate/rank/final-order model, keep `animate: step` restrained, and verify with a strong fixture plus manifest/token checks.
- `skills/school-presentation/scripts/school-presentation.sh` already contains substantial dormant or partially connected helpers:
  - `render_peek_block()`, `render_inline_peek()`, `peekTriggerAtPoint()`, `openPeek()`, and `togglePinnedPeek()` cover the interaction path for hover/click peek.
  - `render_sort_block()` and reveal kinds `sort-rank` / `sort-final` already match the chosen sorting behavior.
  - `normalize_animation_mode()` and `render_auto_animated_block()` already support `animate: step`, but the Phase 15 contract should keep automatic animation to ordinary paragraphs, list items, and table rows rather than structured-layout internals.
  - `render_timeline_block()`, `render_cards_block()`, `render_gallery_block()`, and `render_smartart_block()` exist, and the CSS contains school-style structure classes, but `STRUCTURE_KINDS` currently only includes `sort`; parser/render routing must be connected for `peek`, `timeline`, `cards`, `gallery`, and `smartart`.
  - `semantic_icon_for_slide()`, `structure_icon_html()`, and `render_semantic_icon()` exist, but slide-title semantic icons are not yet wired into `render_page_section()`.
- Section divider rendering and controls already exist at the deck level through section-divider records, `data-print-optional`, `section-divider-toggle`, and hide/show state. Phase 15 should document and verify this behavior rather than replace it.
- Phase 14 presenter markup added event arbitration around active drawing tools. Phase 15 peek behavior must preserve that priority: pen/highlighter/eraser gestures suppress peek and click-zone behavior, while keyboard reveal/navigation remains available.
- The current fixture already demonstrates sort and `animate: step`; it needs additional realistic slides for `peek`, `timeline`, `cards`, `gallery`, `smartart`, semantic icon defaults/opt-out, and section-divider controls.
- `cmd_verify()` already checks repeatable HTML hashes, manifest hierarchy, reveal kinds, workspace/playback/overview hooks, presenter markup hooks, thumbnail ratio, and flat compatibility. Phase 15 should extend this same deterministic gate with explicit classroom/structure checks instead of adding a Playwright default dependency.

## Decision

Plan Phase 15 as a parser-routing, fixture, documentation, and verification slice over the existing renderer:

1. Connect the teacher-facing directives to the parser and `render_block()` path: `peek`, `timeline`, `cards`, `gallery`, and `smartart`.
2. Preserve sorting's existing Markdown-order candidate state, rank reveal, and final-order reveal; improve fixture/docs/verification rather than redesigning it.
3. Keep `animate: step` automatic behavior restrained to ordinary paragraphs, list items, and table rows; structured layouts remain static unless explicitly wrapped in a reveal block.
4. Wire slide-level semantic icons into ordinary content slides and structure items, with `icon=none` as the opt-out and no automatic icons on cover, closing, or section-divider pages.
5. Extend the verification fixture and `cmd_verify()` to prove real rendered output for peek, sort, animate, timeline, cards, gallery, smartart, icons, section dividers, presenter markup compatibility, offline single-file output, repeatability, and fixed canvas behavior.
6. Update the canonical skill docs to make Phase 15 syntax and boundaries clear for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent without adding runtime-specific authoring syntax.

## Implications

- Most Phase 15 implementation should be local to `skills/school-presentation/scripts/school-presentation.sh`, the canonical `SKILL.md`, and the verification fixture.
- No external icon library, JavaScript framework, CDN, or network fetch is needed.
- The output must remain deterministic; hover/click/pinned peek state is live playback state and must not enter Markdown, `.page-source`, thumbnails, overview, or manifest review data.
- Phase 16 remains responsible for print/export review behavior and the full v1.8 regression gate; Phase 15 only keeps print/static fallback readable enough that Phase 16 can formalize it.

## Source Notes

- `.planning/phases/15-classroom-interaction-and-structured-layout-extensions/15-CONTEXT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/14-presenter-markup-tools/14-CONTEXT.md`
- `.planning/milestones/v1.6-ROADMAP.md`
- `.planning/milestones/v1.6-REQUIREMENTS.md`
- `skills/school-presentation/SKILL.md`
- `skills/school-presentation/templates/school-presentation-full.md`
- `skills/school-presentation/scripts/school-presentation.sh`
