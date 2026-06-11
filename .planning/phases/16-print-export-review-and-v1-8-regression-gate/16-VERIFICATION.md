# Phase 16 Verification: Print Export Review and v1.8 Regression Gate

**Date:** 2026-06-11
**Status:** Passed
**Scope:** SP-26, SP-27

## Automated Gate

Command:

```bash
skills/school-presentation/scripts/school-presentation.sh verify --workdir /tmp/school-presentation-phase16-verify
```

Result: passed.

Verification manifest:

- Path: `/tmp/school-presentation-phase16-verify/verification-manifest.json`
- `status`: `passed`
- `repeatable_html`: `true`
- `presenter_markup_verified`: `true`
- `classroom_structure_verified`: `true`
- `print_review_verified`: `true`
- `ratio_4x3_verified`: `true`
- `offline_single_file_verified`: `true`
- `thumbnail_ratio_verified`: `true`
- `flat_slide_compat_verified`: `true`
- `physical_pages`: `51`
- `sections`: `5`

## PDF Review Artifact

Command:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-sandbox --print-to-pdf=/tmp/school-presentation-phase16-verify/school-presentation-review.pdf file:///tmp/school-presentation-phase16-verify/school-presentation-first.html
```

Artifact evidence:

- PDF: `/tmp/school-presentation-phase16-verify/school-presentation-review.pdf`
- PNG sanity render: `/tmp/school-presentation-phase16-verify/school-presentation-review-page1.png`
- PDF SHA-256: `9761c12f4fd4024dc1576e59d8c70250c614cd7d8a157823ce8b60d0a7ac4ce7`
- PNG SHA-256: `309d5dbb821f50d1c76a94e6f0b04148392dbb32b967eb3a9a785d252243d8f1`
- PDF page tree final `/Count`: `51`
- File type: PDF document, version 1.4
- First-page PNG visual sanity: nonblank, 16:9 canvas fills the PDF page, school cover text and identity assets visible.

## Manual PDF UAT Checklist

The generated PDF artifact is ready for human visual review. The following checks are the required manual scope:

- Reveal content is opened in the PDF.
- Masked answers are visible in the PDF.
- Emphasis/correct-answer marks remain visibly underlined.
- Sorting exercises appear in correct final order.
- Section title pages are visible by default during live playback.
- PDF review can include or exclude section title pages through generated deck controls.
- Automatically inserted agenda pages and overflow split pages appear in manifest order.
- Gallery cards paginate without clipping individual cards.
- Presenter annotations are not present in print/PDF review output by default.
- `16:9` and `4:3` generated samples keep stable slide-canvas proportions.

## Notes

- The default script gate remains deterministic and does not require Playwright, screenshot checks, or PDF generation.
- The PDF artifact was generated separately as manual UAT evidence using the already rendered offline HTML deck.
- The first PDF export attempt exposed default browser portrait/letter whitespace. Phase 16 fixed this by generating ratio-specific `@page` sizes: `16in 9in` for `16:9` and `12in 9in` for `4:3`.
