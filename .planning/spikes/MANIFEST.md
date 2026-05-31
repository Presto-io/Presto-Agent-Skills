# Spike Manifest

## Idea
Explore the shortest reliable path for a school-style presentation generator that starts from Markdown, uses fixed layout families, preserves school identity, and ships as a self-contained HTML deck without the instability of PPTX-first generation.

## Requirements

- HTML is the primary stable output for v1.5.
- Markdown remains the editable source of truth.
- Logical slides may overflow and be split into multiple physical HTML pages by the renderer.
- Images keep their original aspect ratio by default and are not cropped for fit.
- The deck must carry school identity through blue-green palette, logo, slogan, and decorative marks.
- Formula, table, chart, image, and video handling must be supported in the Markdown-to-HTML path.

## Spikes

| # | Name | Type | Validates | Verdict | Tags |
|---|------|------|-----------|---------|------|
| 001 | html-first-markdown-presentation-stack | standard | Given school presentation content in Markdown, when comparing Marp, Slidev, reveal.js, Pandoc, and Deckset, then the least-warping path to stable single-file HTML is identifiable | VALIDATED | markdown, html, presentation, research |
