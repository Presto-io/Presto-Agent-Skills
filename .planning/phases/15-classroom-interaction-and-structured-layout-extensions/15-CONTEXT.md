# Phase 15: Classroom Interaction and Structured Layout Extensions - Context

**Gathered:** 2026-06-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 15 formalizes classroom-interaction and structured-layout authoring for the existing `school-presentation` Markdown-to-offline-HTML deck. It turns the deferred Phase 10 classroom features into teacher-editable Markdown capabilities: hover/peek hints, deterministic sorting exercises, restrained body-step animation, timeline/card/gallery/SmartArt-like structured blocks, semantic icons, and section-divider controls.

This phase must preserve the Markdown logical-slide source of truth, offline single-file HTML output, fixed slide-canvas model, existing preview/workspace/playback/overview behavior, Phase 9/10 reveal/mask/emphasis behavior, and Phase 14 playback-local presenter markup boundaries. Phase 16 owns print/export review and full v1.8 regression packaging.

</domain>

<decisions>
## Implementation Decisions

### Markdown Authoring Contract

- **D-01:** New classroom and layout capabilities should use block directives as the primary authoring surface. Slide metadata remains for page-level controls such as `layout`, `intent`, `split`, `animate`, and `icon`.
- **D-02:** Block directive names should favor teacher-facing classroom intuition over generic technical abstraction. Use `peek`, `timeline`, `cards`, `gallery`, and `smartart` directly instead of a generic `structure type=...` wrapper.
- **D-03:** Keep `process` and other diagram-like flows under `::: smartart type=process :::`; do not introduce a separate `::: process :::` directive in this phase.

### Classroom Interaction Behavior

- **D-04:** `peek` defaults to supporting both hover and click behavior. Hover opens temporary supplemental content; click pins/unpins it for live explanation.
- **D-05:** Keyboard navigation, reveal advancement, answer masks, and presenter markup must keep clear priority over peek. Active pen/highlighter/eraser drawing tools suppress peek and playback click-zone behavior; keyboard navigation remains available.
- **D-06:** Preview workspace and overview should expose peek entries in an inspectable way, but should not need to simulate hover behavior.
- **D-07:** Sorting exercises should preserve the existing implementation shape: candidates initially follow Markdown order, `order` steps reveal rank numbers, and `final_order` reveals the final sorted order. Phase 15 should document, fixture, and verify this behavior rather than redesign it.
- **D-08:** `animate: step` is intentionally restrained. It should auto-step ordinary paragraphs, list items, and table rows only. Structured blocks should not receive automatic per-item animation by default in this phase.

### Structured Layout Delivery

- **D-09:** Phase 15 should formally deliver all four structured layout families listed in the roadmap: `timeline`, `cards`, `gallery`, and `smartart`.
- **D-10:** Each delivered structured layout family needs a Markdown example, renderer path, school-identity CSS, and verification coverage. Existing dormant renderer helpers are not enough unless they are connected to parsing/rendering and proven by fixtures.
- **D-11:** Default intended uses are:
  - `timeline`: time lines, construction progress, course-development paths.
  - `cards`: task cards, competency points, resource lists, group activities.
  - `gallery`: image sets, works comparison, field evidence, before/after comparison.
  - `smartart`: process, cycle, hierarchy, pyramid, and picture-step diagrams.

### Semantic Icons and School Style

- **D-12:** Semantic icons are enabled by default for ordinary content slides and structured-layout items, with `icon=none` available to opt out.
- **D-13:** Icons must use the skill-local blue-green school identity system and browser-native HTML/CSS. Do not add external icon libraries, network dependencies, emoji-style decoration, or runtime-specific icon syntax.
- **D-14:** Cover, closing, and section-divider pages should not receive automatic semantic icons by default, to preserve the formal school-presentation tone.

### Verification and Acceptance

- **D-15:** Phase 15 verification should use a strong fixture plus manifest/token checks, not a token-only smoke test.
- **D-16:** The verification fixture must cover `peek`, `sort`, `animate: step`, `timeline`, `cards`, `gallery`, and `smartart`.
- **D-17:** `verify` must continue proving repeatable HTML hashes and must check that new classroom/structure features do not break workspace, playback, overview, reveal, mask, emphasis, sort, presenter markup, offline single-file output, or fixed `16:9`/`4:3` canvas behavior.
- **D-18:** Playwright/browser screenshot checks are not required as the default Phase 15 gate. Human visual acceptance remains explicit: the user will inspect generated output artifacts.

### Claude's Discretion

- Exact CSS details, layout density, and visual polish for each structure family may be chosen during planning/implementation as long as the output stays formal, readable from a classroom display, and consistent with the existing blue-green school identity.
- Exact verification token names may be chosen by the implementer, provided they prove real fixture rendering rather than merely checking for unused helper functions.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Active Phase Contract

- `.planning/ROADMAP.md` - Phase 15 goal, dependencies, requirements, and success criteria for classroom interaction and structured layout extensions.
- `.planning/REQUIREMENTS.md` - SP-21 through SP-25 define the active Phase 15 requirements.
- `.planning/STATE.md` - Current milestone status and Phase 14 completion boundary.

### Existing School Presentation Behavior

- `skills/school-presentation/SKILL.md` - Canonical skill behavior, Markdown contract, playback model, reveal/mask/emphasis model, presenter markup boundary, verification expectations, and runtime adapter notes.
- `skills/school-presentation/templates/school-presentation-full.md` - Current verification fixture source. It already demonstrates sort and `animate: step`; Phase 15 should extend it for peek and structured layouts.
- `skills/school-presentation/scripts/school-presentation.sh` - Renderer, parser, layout CSS, reveal state machine, peek/sort/animation hooks, semantic icon helpers, section divider controls, playback event arbitration, and verification checks.

### Prior Accepted Milestones

- `.planning/phases/14-presenter-markup-tools/14-CONTEXT.md` - Phase 14 decisions for playback-local markup, event priority, page-scoped annotation state, and no mutation of source/manifest/review artifacts.
- `.planning/milestones/v1.6-ROADMAP.md` - Accepted Phase 9/10 playback, preview, hierarchy, ordered reveal, emphasis, and answer-mask behavior.
- `.planning/milestones/v1.6-REQUIREMENTS.md` - Completed SP-10 through SP-16 requirements that Phase 15 must not regress.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `skills/school-presentation/scripts/school-presentation.sh`: `render_inline_peek`, `render_peek_block`, `peekTriggerAtPoint`, `openPeek`, `togglePinnedPeek`, and related JS/CSS already sketch the peek interaction path.
- `skills/school-presentation/scripts/school-presentation.sh`: `render_sort_block`, `sort-rank`, `sort-final`, `applyRevealState`, and verification reveal kinds already implement the chosen sorting behavior shape.
- `skills/school-presentation/scripts/school-presentation.sh`: `normalize_animation_mode`, `render_auto_animated_block`, and `animate: step` already support restrained paragraph/list/table animation.
- `skills/school-presentation/scripts/school-presentation.sh`: `render_timeline_block`, `render_cards_block`, `render_gallery_block`, and `render_smartart_block` exist as structured-layout helpers, but they still need full parser/render integration and fixture verification.
- `skills/school-presentation/scripts/school-presentation.sh`: `semantic_icon_for_text`, `semantic_icon_for_slide`, `structure_icon_html`, and `render_semantic_icon` can support default semantic icon behavior.

### Established Patterns

- The renderer keeps `sections -> logical_slides -> physical_pages -> reveal_steps` as the manifest hierarchy. New features should preserve this model and add reveal steps only where they participate in playback state.
- Preview workspace and overview show final/inspectable content; playback owns progressive reveal, masks, emphasis, peek interaction, and presenter-local tools.
- Markdown remains the source of truth. Runtime state such as pinned peek popovers, annotations, and reveal progress must not mutate Markdown, `.page-source`, thumbnails, overview, or manifest review data.
- The deck is an offline single-file HTML artifact. New interactions and icons must avoid network dependencies and must remain deterministic across repeated renders.

### Integration Points

- Add new directive names to the block parser structure allowlist and route them through `render_block`.
- Extend `school-presentation-full.md` so the verification fixture demonstrates each new authoring capability in realistic school-presentation content.
- Extend `verify` with checks for real rendered structure classes/hooks and interaction compatibility, while retaining existing repeatability, size, hierarchy, reveal, workspace, presenter markup, thumbnail ratio, and flat-compat checks.
- Update `SKILL.md` so the canonical authoring rules document Phase 15 syntax, defaults, and safety boundaries for all supported runtimes.

</code_context>

<specifics>
## Specific Ideas

- Use examples like:
  - `::: peek title="教师提示" trigger=both ... :::`
  - `::: timeline variant=vertical ... :::`
  - `::: cards columns=3 ... :::`
  - `::: gallery variant=compare ... :::`
  - `::: smartart type=process variant=steps ... :::`
- Default icon behavior should be useful but still formal: automatic blue-green semantic icons are allowed, while authors can write `icon=none` to remove them.
- User explicitly wants output artifacts available for manual visual review after script verification.

</specifics>

<deferred>
## Deferred Ideas

- Phase 16 owns print/export-friendly review behavior and the full v1.8 regression gate.
- Drag-and-drop sorting, hosted collaboration, remote control, audience synchronization, annotation persistence, PPTX export, Keynote export, and fully editable PowerPoint output remain outside Phase 15.

</deferred>

---

*Phase: 15-Classroom Interaction and Structured Layout Extensions*
*Context gathered: 2026-06-11*
