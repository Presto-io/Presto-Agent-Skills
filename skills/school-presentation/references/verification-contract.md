# School Presentation Verification Contract

This reference holds detailed verification expectations for the `school-presentation` skill. Keep `SKILL.md` as the concise semantic entry point and update this file when verification behavior changes.

## Verify Command

Run:

```bash
skills/school-presentation/scripts/school-presentation.sh verify --workdir <dir>
```

The command must generate examples, repeat renders, compare stability, inspect generated HTML, and write a verification manifest.

## Required Verification Coverage

The verification flow must cover:

- Layered manifest hierarchy.
- Preview workspace.
- Playback.
- Overview.
- Reveal hooks.
- Peek.
- Sorting.
- Structured layouts.
- Semantic icons.
- Section divider controls.
- `full_page_image` pages.
- Presenter markup controls.
- Annotation layer hooks.
- Print/export review tokens.
- Offline single-file boundary.
- `16:9` and `4:3` fixed-canvas examples.

## Required Manifest Booleans

The verification manifest must record:

- `presenter_markup_verified: true`
- `classroom_structure_verified: true`
- `full_page_image_verified: true`
- `print_review_verified: true`
- `ratio_4x3_verified: true`
- `offline_single_file_verified: true`

The manifest must not contain annotation state, markup palette, stroke data, pinned peek, hover peek, or print control runtime state.

## Entry-Level Verification Checklist

- `skills/school-presentation/scripts/school-presentation.sh example --output <file>` outputs reviewable logical-slide Markdown.
- `render --input <md> --html <html>` generates offline HTML and embeds school logo, slogan, CSS, charts, and embeddable assets.
- `verify --workdir <dir>` repeats render of the same Markdown and proves stable HTML hash.
- Manifest contains `sections -> logical_slides -> physical_pages -> reveal_steps` hierarchy.
- Every physical page has `data-section-index`, `data-logical-index`, `data-physical-index`, `data-global-index`, and `data-page-id` information.
- Output HTML contains preview workspace, thumbnail rail, preview stage, playback, overview, hash sync, keyboard/mouse/touch navigation, and current-page sync logic.
- Output HTML contains ordered reveal, answer masks, and correct-emphasis behavior.
- Preview shows full content and final reveal state; playback controls step visibility.
- Output HTML contains peek cards, sorting number/final reordering, `animate: step`, timeline, cards, gallery, smartart, semantic icons, and section divider controls.
- `layout: full_page_image` records hierarchy in manifest but renders only one full-canvas image and no reveal steps.
- Playback-local pointer, pen, highlighter, eraser, clear/reset controls, and page-scoped annotation layer are present.
- Manifest and Markdown source do not include annotation state.
- `导出最终PDF`, `预览`, and `章节页` bistable controls are present; controls do not use `是/否` text for state.
- One-click final PDF export downloads a PDF with outline/bookmarks and directory links, follows section-page preview state, expands reveal/mask/emphasis/sort, and excludes presenter annotations.
- Cover contains only constrained main title, optional subtitle, and fixed information bar.
- Formula content remains mathematical style, including masked or revealed formulas.
- Output HTML stays under `max_output_mb`; oversized media records fallback instead of forced embedding.
- Fixture deck covers fixed `16:9`/`4:3` ratios, auto directory pages, formulas, tables, charts, images, video fallback, speaker notes, emphasis blocks, auto physical page splitting, and PDF review samples.

## Manual Review Notes

Automated verification proves deterministic structure and token coverage. Browser/PDF visual UAT remains required when accepting a new presentation visual feature.
