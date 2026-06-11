# Phase 16: Print Export Review and v1.8 Regression Gate - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-11
**Phase:** 16-Print Export Review and v1.8 Regression Gate
**Areas discussed:** Review view shape, Annotation export policy, Regression gate strength, Human UAT artifact

---

## Review View Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Same offline HTML review/print mode | Add or formalize a deterministic review/print mode in the generated single-file HTML, then print/export it to PDF through the browser. | ✓ |
| Basic `@media print` only | Keep relying on incidental preview print CSS without a distinct review contract. | |
| Separate deterministic review artifact | Generate a second HTML/PDF-like artifact outside the main deck. | |

**User's choice:** Same offline HTML review/print mode, with browser PDF as the human review artifact.
**Notes:** User clarified the review/PDF state must open reveal content, show masked answers, preserve underlined emphasis, put sorting exercises in correct final order, and paginate gallery content from cards. Section title pages should be shown by default during live presentation/playback, while print/PDF review should provide a button for whether section title pages are included. Section title pages, automatically inserted middle pages, and gallery page breaks need special attention.

---

## Annotation Export Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Exclude presenter annotations by default | Keep Phase 14 markup as playback-local session state and omit it from print/export review, manifest, and deterministic artifacts. | ✓ |
| Flatten annotations into review output | Capture live presenter marks as a flattened visual layer in print/PDF. | |
| Make annotation export configurable | Add controls for including/excluding annotations. | |

**User's choice:** Default exclude.
**Notes:** This preserves the Phase 14 boundary that annotations do not mutate Markdown, manifest hierarchy, preview workspace, overview, thumbnails, or deterministic review artifacts.

---

## Regression Gate Strength

| Option | Description | Selected |
|--------|-------------|----------|
| Extend existing `verify` gate | Keep deterministic script-based verification and add Phase 16 checks for review/print behavior. | ✓ |
| Add browser screenshot gate | Add a heavier visual regression dependency such as Playwright screenshots. | |
| Add automated PDF generation gate | Generate and inspect PDF as part of the default script gate. | |

**User's choice:** Continue using existing `verify`.
**Notes:** The gate should still prove repeatable output, manifest hierarchy, runtime-state non-leakage, presenter markup, classroom structure, offline single-file boundaries, and fixed canvas behavior. Phase 16 should extend it with deterministic review/print checks rather than adding a heavy default browser automation dependency.

---

## Human UAT Artifact

| Option | Description | Selected |
|--------|-------------|----------|
| PDF from review/print mode | Human reviewer exports/prints the offline HTML review state to PDF and inspects the resulting PDF. | ✓ |
| HTML-only manual review | Inspect the generated HTML in browser only. | |
| Office export review | Use PPTX, Keynote, or editable PowerPoint as the manual review surface. | |

**User's choice:** PDF.
**Notes:** User explicitly called out section title pages, middle inserted pages, and gallery page breaks as important. PDF UAT should inspect reveal opened, masks visible, underlined emphasis, final sorted order, section title page inclusion/exclusion behavior, card-level gallery pagination, and stable `16:9` / `4:3` canvas output.

---

## Claude's Discretion

- Choose the exact label and UI placement for review/print mode.
- Choose implementation details for print CSS and card-level gallery pagination, provided no gallery card is clipped.
- Choose deterministic verification token names, provided the checks prove rendered fixture behavior.

## Deferred Ideas

- Annotation flattening or saved annotation exports.
- Automated browser-PDF or screenshot regression as a default gate.
- PPTX, Keynote, editable PowerPoint, hosted sharing, remote control, and multi-device synchronization.
