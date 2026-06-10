# Phase 14: Presenter Markup Tools - Context

**Gathered:** 2026-06-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 14 adds playback-local presenter markup tools to the existing `school-presentation` offline HTML deck. The feature covers pointer, pen, highlighter, eraser, and clear/reset controls during live playback only. It must not mutate the Markdown source, preview workspace content, hierarchy manifest, deterministic review artifacts, or prior Phase 9/10 playback/reveal/mask behavior.

</domain>

<decisions>
## Implementation Decisions

### Tool Palette Placement and Motion

- **D-01:** The markup toolbar should feel like the Apple iPad floating markup palette: compact, visual, and presenter-oriented rather than a heavy desktop settings panel.
- **D-02:** The palette must support four placement families: lower-left, lower-right, left side, and right side.
- **D-03:** The palette may either follow the mouse/pointer while active or slide/peek in from an edge. Planning should preserve both interaction styles if feasible, with edge placement and drag/follow behavior scoped to playback only.

### Pointer and Tool Behavior

- **D-04:** Pointer behavior should imitate the Apple iPad pointer feel. It should read as a live presenter pointer, not as permanent authored content.
- **D-05:** Pen/highlighter tools are toggle-selected: clicking the pen selects drawing mode; clicking the active pen again disengages it.
- **D-06:** Eraser and clear/reset are intentional presenter controls. Navigation must never implicitly erase annotations.

### Page-Scoped Annotation State

- **D-07:** Annotation state is scoped to the active session and physical page. When the presenter navigates away and later returns, that page's annotations remain visible.
- **D-08:** Annotations persist across page navigation until the presenter explicitly clears the handwriting/markup.
- **D-09:** At minimum, clear behavior must support clearing the current physical page's annotations. A broader "clear all session annotations" affordance may be considered only if it does not make current-page clearing ambiguous.

### Navigation and Input Arbitration

- **D-10:** While a drawing tool is active, normal playback-zone click navigation is disabled so drawing strokes do not accidentally advance or reverse slides.
- **D-11:** Keyboard left/right navigation remains available while drawing mode is active. This gives presenters a reliable escape hatch without leaving markup mode.
- **D-12:** Pointer, pen, highlighter, eraser, mask-click reveal, peek/hover, and playback-zone navigation need explicit event arbitration. Drawing gestures should win over click zones; non-drawing tools must not break existing reveal/mask navigation.

### Transitions and Visual Continuity

- **D-13:** Existing page transition animation should also apply to the annotation layer. If a physical page fades or swaps, its visible annotations should move/fade with that page instead of popping separately.
- **D-14:** Annotation rendering should respect the fixed slide canvas model. Strokes should align with slide coordinates under stage scaling, browser resizing, and `16:9`/`4:3` output.

### Claude's Discretion

- The exact default color/width presets for pen and highlighter are not locked. Use conservative school-presentation defaults that are readable over the current blue-green deck style.
- The exact implementation mechanism is not locked. Canvas, SVG, or another browser-native layer is acceptable if it preserves page-scoped state, stage scaling, and offline single-file output.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Active Phase Contract

- `.planning/ROADMAP.md` — Phase 14 goal, dependencies, and success criteria for Presenter Markup Tools.
- `.planning/REQUIREMENTS.md` — SP-17 through SP-20 define the required markup-tool behavior and regression boundary.

### Existing School Presentation Behavior

- `skills/school-presentation/SKILL.md` — canonical skill behavior, playback model, fixed canvas rule, verification expectations, runtime adapter notes, and deferred-scope history.
- `skills/school-presentation/templates/school-presentation-full.md` — fixture source that should be extended only as needed to demonstrate presenter markup controls without turning annotations into Markdown content.
- `skills/school-presentation/scripts/school-presentation.sh` — current renderer, playback UI, reveal/mask/emphasis state machine, stage scaling, navigation zones, touch handling, and verification manifest checks.

### Prior Accepted Milestones

- `.planning/milestones/v1.6-ROADMAP.md` — accepted Phase 9/10 playback, preview, hierarchy, ordered reveal, emphasis, and answer-mask behavior.
- `.planning/milestones/v1.6-REQUIREMENTS.md` — completed SP-10 through SP-16 requirements that Phase 14 must not regress.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `#playback-stage` and `.slide-scale-shell` in `skills/school-presentation/scripts/school-presentation.sh`: the annotation layer should attach to or travel with the current playback shell so strokes share page transition behavior.
- `stageScaleFor`, `fitStage`, and `SLIDE_DESIGN_WIDTH` / `SLIDE_DESIGN_HEIGHT`: use these fixed-canvas mechanics to convert pointer coordinates into stable slide coordinates.
- `.playback-toolbar`, `.playback-control`, and `.playback-page-pill`: existing playback control styling can guide the compact iPad-like palette without making a separate heavy UI system.
- `pages[currentPageIndex]` and each page's `page_id`: natural key for session-local, page-scoped annotation state.

### Established Patterns

- Playback uses transparent click zones for previous/next. Drawing mode must temporarily suppress those zone clicks while keeping left/right keyboard navigation working.
- Reveal/mask/emphasis state is managed in cloned slide DOM for playback and full-state clones for preview/overview. Markup must stay playback-local and must not appear in preview thumbnails, overview, source Markdown, or manifest review data.
- The deck is an offline single-file HTML artifact. Markup implementation should avoid network dependencies and should keep verification deterministic.

### Integration Points

- Add markup controls inside the playback view near the existing toolbar, with placement support for lower-left, lower-right, left side, and right side.
- Add event handling around playback pointer/touch/mouse input so active drawing tools win over playback zones, mask reveal clicks, and hover/peek behaviors.
- Extend `verify` with HTML/manifest checks that prove markup controls exist and existing workspace/playback/reveal/mask tokens still pass.

</code_context>

<specifics>
## Specific Ideas

- User specifically wants an Apple iPad-style markup toolbar.
- Toolbar should support following the mouse/pointer or sliding/peeking from an edge.
- Toolbar placement choices: lower-left, lower-right, left side, right side.
- Pointer should imitate Apple iPad pointer behavior.
- Page navigation should preserve annotations unless the presenter explicitly clears handwriting.
- Clicking pen selects drawing mode; clicking the active pen again exits drawing mode.
- Drawing mode blocks normal click-zone slide navigation, while left/right keyboard navigation remains active.
- Page transition animation should include the annotation layer.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within Phase 14 scope. Hosted collaboration, remote control, audience sync, and export/print review behavior remain outside Phase 14 and are already assigned to future/out-of-scope areas in v1.8 requirements.

</deferred>

---

*Phase: 14-Presenter Markup Tools*
*Context gathered: 2026-06-11*
