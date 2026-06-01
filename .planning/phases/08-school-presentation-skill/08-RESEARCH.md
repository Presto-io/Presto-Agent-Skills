# Phase 08 Research: School Presentation Skill

**Milestone:** v1.5 School Presentation Skill
**Date:** 2026-05-31
**Status:** Research complete

## Question

What is the least-warping implementation route for a Markdown-first school presentation skill that needs formulas, tables, charts, images, videos, readable typography, automatic overflow pagination, and offline static delivery?

## Findings

- Markdown logical slides plus a custom HTML renderer is the best fit for v1.5.
- reveal.js-style HTML presentation concepts are useful, but the skill should keep its own renderer logic so fixed layout families and overflow splitting stay controllable.
- Marp and Deckset are good authoring and aesthetics references, but not the preferred runtime base.
- PPTX and Keynote should remain out of scope for the first school-presentation slice.
- Images should preserve aspect ratio and use contain-style placement by default.
- Large videos need documented fallback behavior so the HTML deck stays under the 50 MB cap.

## Decision

Use a persistent Markdown logical-slide intermediate and a skill-owned offline HTML renderer with a small fixed layout library. Keep the output self-contained when size permits, and externalize oversized media only when the 50 MB cap would otherwise be broken.

## Implications

- The skill needs a reusable logical-slide template rather than a one-off example deck.
- The renderer must make layout selection deterministic and allow explicit override.
- Verification should emphasize repeatable output, size limits, and predictable Markdown-to-HTML control behavior.
- School identity assets and provenance notes should live under the skill directory, with a clear skill-local subdirectory for extracted references.

## Source Notes

- `.planning/research/v1.5-school-presentation-stack.md`
- `.planning/spikes/001-html-first-markdown-presentation-stack/README.md`
