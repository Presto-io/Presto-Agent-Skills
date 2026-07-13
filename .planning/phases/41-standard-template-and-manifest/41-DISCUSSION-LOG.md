# Phase 41: Standard Template and Manifest - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-13
**Phase:** 41-Standard Template and Manifest
**Areas discussed:** Template source and runtime boundary, Manifest contract, Layout and slot model, Text budgets and manual adjustment, Template validation and evidence

---

## Template Source and Runtime Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve original `.potx` as evidence and use normalized `.pptx` at runtime | Best audit trail, but keeps the original visual sample in the repository. | |
| Commit only normalized `.pptx` | Cleaner repository; original `.potx` is transformed into the controlled runtime template. | Yes |
| Keep both `.potx` and `.pptx` in templates | Convenient discovery, but mixes evidence and runtime assets. | |

**User's choice:** Commit only normalized `.pptx`.
**Notes:** User clarified: "directly改造成pptx". The original `.potx` should not be a durable committed evidence artifact.

---

## Manifest Contract

| Option | Description | Selected |
|--------|-------------|----------|
| Full slot contract | Record theme, layouts, slot ids, placeholder mapping, geometry, text budgets, empty rules, continuation behavior, footer/decor ownership. | Yes |
| Medium manifest | Record theme, layouts, major slots, placeholder mapping, and geometry; leave budgets to renderer logic. | |
| Lightweight index | Record only theme, layout names, and placeholder names for human reference. | |

**User's choice:** Full slot contract.
**Notes:** Manifest must be a real downstream contract for renderer and validation.

---

## Manifest Format

| Option | Description | Selected |
|--------|-------------|----------|
| YAML | Human-reviewable and suitable for slot-map adjustment; parser dependency must be handled deliberately. | Yes |
| JSON | No parser dependency and machine-stable, but harder to review and annotate. | |
| Markdown tables plus snippets | Pleasant for humans but fragile for renderer/validator parsing. | |

**User's choice:** YAML.
**Notes:** Human reviewability matters for template normalization.

---

## Layout and Slot Model

| Option | Description | Selected |
|--------|-------------|----------|
| Unified core slot naming | Reuse stable semantic names across layouts and add specialized slots where needed. | Yes |
| PPTX placeholder names | Closest to file internals, but can inherit unstable names and localization. | |
| Layout-specific slot names only | Flexible but encourages drift across 11 layouts. | |

**User's choice:** Unified core slot naming with a minimum common foundation plus layout-specific extensions.
**Notes:** User clarified that the manifest should preserve minimum common base information while letting different slots extend with specialized fields.

---

## Text Budgets and Manual Calibration

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit per-slot budget fields | Record `max_chars`, `max_lines`, font-size range, and overflow behavior. | Yes |
| Font range only | Simpler manifest, but pagination depends more heavily on renderer estimates. | |
| Human description only | Easy to read, but weak for validation and future renderer behavior. | |

**User's choice:** Explicit per-slot budget fields, calibrated manually.
**Notes:** User clarified that values should be seeded first and adjusted through manual testing rather than treated as perfect upfront numbers.

---

## Manual PPTX Adjustment

| Option | Description | Selected |
|--------|-------------|----------|
| Generate an initial PPTX framework and let the user manually drag/resize | Works well if mapping anchors are preserved and validation catches drift. | Yes |
| Avoid manual PPTX editing | More deterministic, but less useful for visual layout refinement. | |

**User's choice:** Generate a PPTX framework, then support careful manual drag/resize.
**Notes:** Guardrails captured: preserve placeholders and mapping anchors, avoid replacing mapped placeholders with ordinary shapes, mark decorative elements as template-owned, update manifest when adding content slots, and run `template-report` after edits.

---

## Layout Coverage

| Option | Description | Selected |
|--------|-------------|----------|
| All 11 layouts exist in Phase 41 | Template and manifest cover every v1.17 layout before Markdown/renderer work. | Yes |
| Core layouts only first | Faster, but risks later template/schema churn. | |
| Few physical layouts with virtual manifest mapping | Simpler PPTX, but weaker inspectability. | |

**User's choice:** All 11 layouts must exist in Phase 41.
**Notes:** The normalized `.pptx` and YAML manifest must cover `cover`, `contents`, `section`, `title-content`, `two-column`, `image-text`, `table`, `timeline`, `gallery`, `code`, and `closing`.

---

## Template Validation and Evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Human-readable Markdown report plus machine JSON evidence | Supports manual review and later structural verification. | Yes |
| Terminal text only | Lightweight but weak as durable evidence. | |
| JSON only | Machine-friendly but uncomfortable for human template review. | |

**User's choice:** Markdown report plus JSON evidence.
**Notes:** Failures should be non-zero for unknown theme, missing layout, missing slot, duplicate slot, lost placeholder mapping, manifest/PPTX geometry mismatch, and malformed budget fields.

---

## Claude's Discretion

- Concrete file names and YAML schema details may be decided by downstream planning as long as they satisfy the captured constraints.
- The plan may decide whether layouts are implemented as slide layouts, template slides, or another inspectable mapping mechanism, provided `template-report` validates all 11 mappings.

## Deferred Ideas

None.
