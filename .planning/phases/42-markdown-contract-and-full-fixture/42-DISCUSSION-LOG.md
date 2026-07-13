# Phase 42: Markdown Contract and Full Fixture - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md; this log preserves the alternatives considered.

**Date:** 2026-07-13
**Phase:** 42-markdown-contract-and-full-fixture
**Areas discussed:** Markdown surface, content-to-slot mapping, notes/media/validation, full fixture strategy, automatic pagination, block boundaries/media expansion/emphasis

---

## Markdown Surface

| Decision | Alternatives considered | User's choice |
|----------|-------------------------|---------------|
| Slide declaration | Explicit slide blocks; heading-only splitting; mixed syntax | Explicit `::: slide {layout="..."}` blocks |
| YAML fields | Strict allowlist; ignore unknown fields; extension namespace | Strict MD-02 allowlist; unknown fields fail |
| Document title and contents | `#` fallback plus `##` contents; include both; explicit contents | `#` fallback only; contents from ordered `##` headings |
| Slide attributes | `layout` only; optional `id`; layout-specific attributes | Temporary optional `id` in development only; omit from public contract/output |

**Notes:** The user accepted `id` only because the project is currently in testing and development. It must not survive into the final authored example or PPTX.

---

## Content-to-Slot Mapping

| Decision | Alternatives considered | User's choice |
|----------|-------------------------|---------------|
| Two-column syntax | Explicit left/right blocks; ordered `###` sections; thematic break | Ordered content blocks with optional `###` labels |
| Missing column headings | Require visible headings; hidden markers; optional headings | Optional; content renders directly when no heading is present |
| No-heading column split | Thematic break; first two blocks; left only | Pair blocks in source order |
| Image-text mapping | First image to fixed media slot; require image first; Markdown controls side | Fixed template media slot; Markdown order does not control geometry |

**Notes:** A later left/right alternating image variant was requested but deferred. Generic mixed media belongs in `two-column`; `image-text` remains for a stable body paired with primary images.

---

## Notes, Media, and Validation

| Decision | Alternatives considered | User's choice |
|----------|-------------------------|---------------|
| Notes syntax | `::: notes`; HTML comments; blockquotes | `::: notes` inside the slide, last |
| Missing media | Stop; empty slot; placeholder | Continue best-effort generation with placeholder and explicit warning |
| Structural errors | Collect then stop; fail fast; continue best effort | Validation fails, but a clearly identified diagnostic artifact may still be emitted |
| Error detail | General message; first error only; locatable complete diagnostics | Include slide, source line, field/path, and collect relevant errors |

**Notes:** Best-effort output never changes failed validation into success and does not override Phase 43's non-zero invalid-input requirement.

---

## Full Fixture Strategy

| Decision | Alternatives considered | User's choice |
|----------|-------------------------|---------------|
| Fixture form | Real presentation; test matrix; valid plus invalid fixtures | One realistic readable presentation |
| Topic | Intelligent-manufacturing curriculum; annual report; campus activities | Vocational-college intelligent-manufacturing curriculum development |
| Overflow cases | Natural narrative; stress-test appendix; commented expansion | Natural long content in the narrative |
| Repeatability | Deterministic overwrite; stop if existing; timestamped copies | Deterministic overwrite at a fixed path |

---

## Automatic Pagination and Block Model

| Decision | Alternatives considered | User's choice |
|----------|-------------------------|---------------|
| Logical-to-physical expansion | Keep one slide; expand same layout | Expand `title-content` and `two-column` into same-layout physical slides |
| Two-column distribution | Adaptive geometry; explicit pages; ordered pairing | Pair blocks 1/2, 3/4, and so on; final unpaired block goes left |
| Physical slide titles | Add continuation marker; first page only; repeat unchanged | Repeat the logical slide title unchanged on every physical page |
| Notes after expansion | First page; last page; duplicate/share | All physical pages share the logical slide notes |

---

## Block Boundaries, Media Expansion, and Emphasis

| Decision | Alternatives considered | User's choice |
|----------|-------------------------|---------------|
| `###` behavior | Own all following content; bind next block; visual-only heading | Forced boundary binding only the immediately following block; empty `###` is a silent manual boundary |
| Image and caption | Separate blocks; crop-fill; atomic contain-fit | Atomic composite block, `contain`, no crop; alt is caption and may be empty |
| Multiple image-text images | Reject extras; treat extras as body; create successive slides | One physical slide per image with title/body repeated |
| Oversized blocks | Shrink only; fail; expand/split | Splittable blocks expand into physical blocks; image-caption remains atomic |
| Table continuation | Modify slide title; use separate table title | Keep slide title unchanged; table title and table form a separate composite block |
| Inline emphasis | Theme controls all; arbitrary styling; semantic constrained syntax | `**bold**` and `==highlight==`, with theme-owned visual mapping |

**Notes:** The table-title decision intentionally supersedes the current Phase 43 roadmap wording that adds a continuation marker to the slide title. Planning must reconcile that wording before implementation.

---

## Claude's Discretion

- Exact file names and concise prose for the contract and fixture.
- Standard placeholder artwork and diagnostic formatting, within the locked behavior.

## Deferred Ideas

- Left/right `image-text` variants with marker-controlled alternating placement.
- Progressive reveal for answers and keywords, preferably implemented through duplicate physical slides; native object animation is optional future work.
