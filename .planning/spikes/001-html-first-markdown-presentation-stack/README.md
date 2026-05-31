---
spike: 001
name: html-first-markdown-presentation-stack
type: standard
validates: "Given school presentation content in Markdown, when comparing Marp, Slidev, reveal.js, Pandoc, and Deckset, then the least-warping path to stable single-file HTML is identifiable"
verdict: VALIDATED
related: []
tags: [markdown, html, presentation, research]
---

# Spike 001: HTML-First Markdown Presentation Stack

## What This Validates

Markdown-first school presentations are best served by an HTML-first renderer with fixed layout families, not by a PPTX-first export path.

## Research

### Approach Comparison

| Approach | Tool/Library | Pros | Cons | Status |
|----------|-------------|------|------|--------|
| Markdown -> HTML/PDF/PPTX | Marp | Simple Markdown story, static HTML output, direct PDF and PPTX export | PPTX is still a conversion path, not the core design target | Strong baseline |
| Markdown -> web slides -> export | Slidev | Modern authoring, good export support, rich web-native presentation model | PPTX export rasterizes slides, so editable text is lost | Good for web delivery, weak for PPTX fidelity |
| Markdown -> HTML slides | reveal.js | Native HTML presentation framework, Markdown supported, suited for offline single-file decks | More assembly work for theming and fixed layout discipline | Best fit for HTML-first |
| Markdown -> PPTX | Pandoc | Mature Markdown-to-PPTX support, reference.pptx layout mapping | Pulls the project back into PPTX instability and layout drift | Not preferred |
| Markdown -> styled slides | Deckset | Strong slide aesthetics, image/text fit controls, presenter notes | macOS-only commercial app, not a portable skill/runtime base | Useful aesthetic reference only |

### Chosen Path

Use reveal.js-style HTML presentation rendering as the base, with Marp/Deckset ideas for Markdown ergonomics and visual discipline.

### Key Findings

- Marp is the cleanest Markdown presentation converter, but its own docs still frame it as a converter that can also export PPTX.
- Slidev is strong for Markdown-authoring plus web interactivity, but its PPTX export is image-based, which is a bad fit for editable or semantically rich PowerPoint output.
- reveal.js is an HTML presentation framework first, which matches the user's preference for a single-file HTML deliverable.
- Pandoc's PPTX path depends on reference layouts and is better for document conversion than for a school-identity presentation system with careful visual control.
- Deckset is the strongest aesthetic benchmark in this set, especially for fitting text, formulas, footers, notes, and backgrounds, but it is not the right runtime base.

## How To Run

Not applicable yet. This spike is a research synthesis, not a runnable implementation.

## What To Expect

A clear recommendation for the v1.5 implementation route: Markdown logical slides, fixed HTML layout families, offline packaging, and no PPTX-first dependency.

## Investigation Trail

- Compared official documentation for Marp, Slidev, reveal.js, Pandoc, and Deckset.
- Checked how each stack handles Markdown, export targets, and presentation fidelity.
- Rejected PPTX-first as the main path because it is the least stable way to preserve the school look without drift.
- Kept image-aspect preservation, logical-slide overflow splitting, and offline single-file packaging as hard design constraints.

## Results

VALIDATED. The shortest and least-warping route is Markdown-first with an HTML presentation engine, fixed layout families, and offline packaging. PPTX should remain a future compatibility target, not the core v1.5 path.
