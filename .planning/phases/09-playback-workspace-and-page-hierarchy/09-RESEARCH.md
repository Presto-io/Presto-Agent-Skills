# Phase 09 Research: Playback Workspace and Page Hierarchy

**Milestone:** v1.6 School Presentation Playback UX
**Date:** 2026-06-01
**Status:** Research complete

## Question

What is the least-disruptive implementation route for upgrading the existing `school-presentation` offline HTML output into a slide-software-like playback and preview workspace while preserving Markdown-first authoring, deterministic rendering, and single-file delivery?

## Findings

- The existing renderer already has the right ownership boundary: Markdown parsing, layout selection, physical pagination, CSS, generated `<section>` elements, and manifest writing all live in `skills/school-presentation/scripts/school-presentation.sh`.
- Phase 9 should extend that renderer in place rather than introduce reveal.js, a bundler, an SPA framework, or a screenshot-generation dependency. The required state can be handled with embedded vanilla JavaScript: `currentPageIndex`, `viewMode`, hash synchronization, rail selection, preview selection, overview selection, playback toolbar visibility, keyboard handlers, click zones, and touch swipe handlers.
- The current `parse_slides` function only recognizes flat `## Slide:` headings. It should become a hierarchy parser that accepts new `## Section: Name` and `### Slide: Title` blocks while preserving old `## Slide:` decks by placing them under a default section.
- The existing physical-page loop should emit richer page records as it renders. Each record can carry section index/title, logical slide index/title, physical index within logical slide, global index, page id, layout, page label, and reveal-step placeholder data. The same records should drive DOM attributes, rail items, overview tiles, hash lookup, and manifest JSON.
- Thumbnails should not rely on raster screenshots. For desktop/wide containers, cloned or reused slide DOM can be scaled inside a fixed thumbnail viewport. For narrow contexts, layout-family cards are more reliable and less jagged, and they can still preserve school identity through palette, page label, layout accents, and title text.
- The preview workspace should be the default HTML entry point. It can keep all physical page DOM in the document while showing the selected page through a preview stage and hiding inactive views with CSS classes. Playback can reuse the same page DOM by moving or cloning selected page markup into a focused stage; the plan should require the executor to choose the simplest implementation that keeps preview and playback faithful.
- The tiled overview should be section-aware. Section-grouped grid bands are the most practical first implementation because they expose the first page of each section, support direct page selection, and do not require complex stacked-card geometry.
- Verification should be DOM/manifest oriented. The current repeat-render hash check should be preserved, then expanded to assert hierarchy presence, page labels, rail items, overview tiles, `data-*` attributes, hash/page synchronization hooks, and required interaction handlers in the generated HTML.

## Decision

Extend the existing skill-owned renderer in place. Add a Markdown hierarchy parser, a complete render manifest tree, and a single-file HTML workspace with embedded CSS and vanilla JavaScript. Keep Phase 9 centered on physical-page navigation, preview, overview, and hierarchy metadata; leave reveal execution, emphasis animation, and answer masks as stable placeholder fields for Phase 10.

## Implications

- `skills/school-presentation/templates/school-presentation-full.md` needs to demonstrate `## Section:` plus `### Slide:` while retaining compatibility with flat `## Slide:` inputs.
- `skills/school-presentation/SKILL.md` must describe the page hierarchy model, default preview workspace, playback controls, overview behavior, and Phase 10 reveal placeholder boundary.
- `skills/school-presentation/scripts/school-presentation.sh` remains the main implementation surface and should be updated carefully because it currently embeds Python, CSS, JavaScript, and manifest generation in one script.
- Phase 9 verification can remain local and deterministic: no browser server, package install, remote assets, or network fetch is required.
- Human visual review is still useful for the final school-style presentation feel, but automated verification should prove that navigation and hierarchy affordances exist and are synchronized.

## Source Notes

- `.planning/phases/09-playback-workspace-and-page-hierarchy/09-CONTEXT.md`
- `.planning/phases/08-school-presentation-skill/08-01-SUMMARY.md`
- `.planning/phases/08-school-presentation-skill/08-RESEARCH.md`
- `.planning/research/v1.5-school-presentation-stack.md`
- `skills/school-presentation/SKILL.md`
- `skills/school-presentation/templates/school-presentation-full.md`
- `skills/school-presentation/scripts/school-presentation.sh`
