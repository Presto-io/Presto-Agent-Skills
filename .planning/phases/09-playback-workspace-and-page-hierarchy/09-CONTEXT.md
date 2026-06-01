# Phase 9: Playback Workspace and Page Hierarchy - Context

**Gathered:** 2026-06-01
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase upgrades the existing `school-presentation` single-file HTML output from a scrollable deck into an offline playback and preview workspace. It adds slide-software-style playback, a left thumbnail rail with a synchronized right preview, a PPT-like overview view with section navigation cues, and a durable hierarchy model for deck, sections, logical slides, physical pages, and future reveal steps.

This phase does not implement ordered reveals, emphasis animation, answer masks, annotation tools, hosted sharing, multi-device sync, PPTX/Keynote export, or a presenter console. Phase 10 will use the hierarchy model created here for reveal steps and classroom answer masks.

</domain>

<decisions>
## Implementation Decisions

### Playback Mode Boundary
- **D-01:** The generated HTML should open to the preview workspace by default. Playback mode is a switchable view inside the same single-file HTML, not a separate hosted route or external app.
- **D-02:** Single-file HTML is acceptable and expected. Use embedded CSS and vanilla JavaScript to maintain `currentPageIndex`, view mode, URL hash, rail selection, preview selection, overview selection, and playback state. Do not require a server, bundler runtime, external framework, or remote assets.
- **D-03:** Playback navigation must support keyboard arrow keys, `Space`, left/center/right click zones, and touch swipes in all directions. Left-zone click means previous page; right-zone click means next page; center-zone click means next step/page.
- **D-04:** In Phase 9, center-zone click can behave as next physical page. In Phase 10, it should first advance a reveal step when a reveal step exists, then advance to the next physical page.
- **D-05:** `Esc` must return from playback mode to the preview workspace while preserving the current physical page. Mouse movement or a touch tap should reveal a lightweight playback toolbar with only essential actions such as return to workspace, open overview, and current progress.
- **D-06:** The current page must be reflected in the URL hash, such as `#p=7` or an equivalent stable page id, so refresh and direct opening preserve page location.
- **D-07:** Playback progress should use a very thin top progress bar. Its color should use the school blue-green identity gradient, staying visually restrained and not occupying meaningful slide space.

### Preview Workspace Layout
- **D-08:** The left thumbnail rail should be grouped by logical slide. Each group shows the logical slide title and the generated physical pages under it, such as `1.1` and `1.2`, so overflow splitting is visible.
- **D-09:** The right large preview should use the real slide DOM, sharing the same source as playback mode so the preview is a faithful view of the rendered physical page.
- **D-10:** Thumbnail rendering should be responsive. On desktop or wide rails, use scaled real slide DOM. On small or narrow rails, use simplified cards to avoid jagged or cramped scaled slides.
- **D-11:** Simplified cards must not be generic summaries. They should have layout-family-specific miniature styles for the existing fixed layouts such as `cover`, `content`, `table`, `chart`, `media-*`, `section`, and `closing`, using school blue-green visual identity plus page number, logical title, and physical page number.
- **D-12:** Thumbnail internals should not be interactive. The outer thumbnail item handles selection.
- **D-13:** State must be strongly synchronized across left rail, right preview, playback mode, overview, and URL hash. Selecting a page from any entry point updates all views and scrolls the rail to the current item.

### Overview View
- **D-14:** The overview view should feel like PPT/Keynote slide sorter or light-table mode: a broad grid for scanning all generated physical pages and jumping to one page.
- **D-15:** The overview must not be an undifferentiated flat grid. It must expose section boundaries with clear visual cues so users can quickly identify each section's first page and the next section's first page.
- **D-16:** Planner and executor may choose the most practical section cue design. Acceptable directions include section-grouped grids, section divider bands, emphasized section opener pages, or compact stacked-card groups. Use the option that best supports fast location, not visual novelty.
- **D-17:** Clicking an overview tile should return to the preview workspace and select that physical page. Rail, preview, and URL hash must update together.
- **D-18:** Section source should be Markdown explicit hierarchy with automatic fallback. If section information is missing, infer conservatively from `layout: section`, heading patterns, or page order. If inference fails, keep a default or ungrouped section instead of silently falling back to a structureless grid.
- **D-19:** Overview tiles should reuse the same responsive thumbnail system as the left rail: real DOM thumbnails when space permits, layout-family cards when space is constrained.

### Page Hierarchy Model
- **D-20:** Prefer Markdown heading hierarchy for authoring page hierarchy. New templates should use `## Section: Name` for section boundaries and `### Slide: Title` for logical slides inside sections.
- **D-21:** Preserve compatibility with the existing flat `## Slide: Title` structure. If no section headings exist, place those logical slides under a default section.
- **D-22:** Physical page labels should use logical-slide dot physical-page numbering such as `3.1` and `3.2`. This numbering should appear consistently in slide markers, rail items, overview tiles, and current-page state.
- **D-23:** The render manifest should output a complete hierarchy tree: `sections -> logical_slides -> physical_pages -> reveal_steps`. In Phase 9, `reveal_steps` may be an empty array or stable placeholder structure.
- **D-24:** Each physical page `<section>` should expose full hierarchy `data-*` attributes: `data-section-index`, `data-section-title`, `data-logical-index`, `data-logical-title`, `data-physical-index`, `data-global-index`, and `data-page-id`.

### Claude's Discretion
Planner and executor should choose the most practical section-overview visual treatment. The user mentioned stacked card groups as one possible direction, but explicitly left the exact visual form open. Favor readability, fast section lookup, and implementation reliability over novelty.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Planning
- `.planning/ROADMAP.md` — Defines Phase 9 goal, SP-10 through SP-13, and success criteria.
- `.planning/REQUIREMENTS.md` — Defines v1.6 playback requirements and separates Phase 9 from Phase 10 reveal/mask scope.
- `.planning/PROJECT.md` — Defines current milestone direction, HTML-first constraints, interaction discipline, and out-of-scope boundaries.
- `.planning/STATE.md` — Records current phase position and prior milestone decisions.

### Prior Decisions
- `.planning/phases/08-school-presentation-skill/08-CONTEXT.md` — Locks HTML-first, Markdown-first, logical-slide-to-physical-page splitting, school identity assets, 50 MB output cap, and deterministic verification direction.
- `.planning/phases/04-markdown-normalization-contract/04-CONTEXT.md` — Locks the shared Markdown intermediate as `YAML frontmatter + body` while leaving template-specific hierarchy fields to the skill.

### Existing School Presentation Implementation
- `skills/school-presentation/SKILL.md` — Current skill process, Markdown slide metadata, runtime adapter notes, safety boundaries, and verification checklist.
- `skills/school-presentation/templates/school-presentation-full.md` — Existing flat `## Slide:` template that Phase 9 must preserve or migrate compatibly.
- `skills/school-presentation/scripts/school-presentation.sh` — Existing renderer that parses slides, splits logical slides into physical pages, emits `<section>` elements, and outputs manifest data.
- `.planning/research/v1.5-school-presentation-stack.md` — Prior research confirming the custom Markdown-to-HTML renderer direction and reveal.js-style web-native runtime inspiration.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/school-presentation/scripts/school-presentation.sh`: Already parses Markdown into slides, chooses fixed layout families, splits content into physical pages, emits `data-logical` and `data-physical`, and writes a render manifest.
- `skills/school-presentation/templates/school-presentation-full.md`: Provides the current sample content and should be upgraded to demonstrate section hierarchy while keeping old flat slides compatible.
- `skills/school-presentation/references/identity/`: Provides the blue-green school identity assets and palette for progress bars, section cues, thumbnails, and overview styling.

### Established Patterns
- The deck remains offline and self-contained when possible.
- The renderer owns physical pagination, layout selection, preview/playback state, and interaction behavior.
- Markdown owns logical content and hierarchy intent.
- Existing fixed layout families should drive both full slide rendering and simplified thumbnail card styles.

### Integration Points
- Extend Markdown parsing to support `## Section:` and `### Slide:` while preserving `## Slide:`.
- Extend the manifest from counts into a hierarchy tree.
- Extend generated HTML with workspace, playback, and overview containers or view states.
- Add lightweight embedded JavaScript for current page state, navigation handlers, hash synchronization, and view switching.
- Add verification that confirms hierarchy counts, current-page synchronization hooks, section cues, thumbnails/overview tiles, and required DOM `data-*` attributes.

</code_context>

<specifics>
## Specific Ideas

- The default entry experience should feel like checking a deck in slide software before presenting.
- The top playback progress bar should be thin and use the school blue-green strip style.
- The overview should resemble slide sorter mode but add stronger section cues so a large deck does not become a disorienting wall of thumbnails.
- Stacked-card section groups are acceptable if they prove more practical, but they are not required.
- Responsive thumbnails should switch from real DOM scaling to layout-family cards on small or narrow surfaces to avoid jagged scaled slides.

</specifics>

<deferred>
## Deferred Ideas

- Ordered reveal execution, emphasis animation, and answer masks belong to Phase 10.
- Annotation, marking, drawing, and in-class markup tools remain deferred to a later milestone.

</deferred>

---

*Phase: 9-Playback Workspace and Page Hierarchy*
*Context gathered: 2026-06-01*
