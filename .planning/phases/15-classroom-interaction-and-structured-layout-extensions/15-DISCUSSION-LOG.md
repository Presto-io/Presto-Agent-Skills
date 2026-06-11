# Phase 15: Classroom Interaction and Structured Layout Extensions - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-11
**Phase:** 15-Classroom Interaction and Structured Layout Extensions
**Areas discussed:** Markdown syntax boundary, Classroom interaction behavior, Structured layout priority, Semantic icons and school style, Verification and acceptance

---

## Markdown Syntax Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Unified block syntax with metadata only for page-level controls | Use `::: peek :::`, `::: timeline :::`, `::: cards :::`, `::: gallery :::`, and `::: smartart :::` for content structures; keep `layout`, `animate`, and `icon` in slide metadata. | Yes |
| Put most configuration into metadata | Keeps body Markdown cleaner but makes teacher editing of complex structures less direct. | |
| Claude decides | Let the implementer choose based on code and verification cost. | |

**User's choice:** Unified block syntax with metadata only for page-level controls.
**Notes:** This keeps structured content visible and reviewable in the Markdown body.

---

## Directive Naming

| Option | Description | Selected |
|--------|-------------|----------|
| Teacher-facing names | Use direct names such as `peek`, `timeline`, `cards`, `gallery`, and `smartart`. | Yes |
| Generic structure wrapper | Use a generic shape such as `::: structure type=timeline :::`. | |
| Claude decides | Let the implementer choose. | |

**User's choice:** Teacher-facing names.
**Notes:** The user chose intuitive authoring names over generic abstractions.

---

## Classroom Interaction Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Peek supports hover and click | Hover opens temporary content; click pins/unpins it. Drawing tools and keyboard navigation keep priority. | Yes |
| Click-only peek | More stable for touch projection but less fluid for quick explanation. | |
| Hover-only peek | Lightweight but less reliable on touch devices and live classroom interaction. | |
| Claude decides | Lock behavior based on classroom stability. | |

**User's choice:** Peek supports both hover and click.
**Notes:** Drawing tools from Phase 14 must suppress peek while active; keyboard reveal/navigation should not be stolen by peek.

---

## Sorting Exercise Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Keep existing implementation shape | Candidates follow Markdown order, `order` steps reveal rank numbers, and `final_order` reveals final sorting. | Yes |
| Redesign sorting model | Reconsider whether sorting should be rank-only, drag-based, or another interaction. | |

**User's choice:** Keep the existing implementation shape.
**Notes:** The user noted this appears already implemented. Phase 15 should document, fixture, and verify the existing behavior instead of redesigning it.

---

## Body-Step Animation

| Option | Description | Selected |
|--------|-------------|----------|
| Basic content only | Auto-step ordinary paragraphs, list items, and table rows. | Yes |
| Also animate structured-block items | Timeline/cards/gallery/smartart items would automatically step. | |
| Explicit reveal/order only | Authors manually mark every progressive reveal. | |
| Claude decides | Choose based on classroom readability and verification cost. | |

**User's choice:** Basic content only.
**Notes:** This keeps `animate: step` restrained and avoids turning Phase 15 into a general animation engine.

---

## Structured Layout Priority

| Option | Description | Selected |
|--------|-------------|----------|
| Deliver all four layout families | `timeline`, `cards`, `gallery`, and `smartart` all need examples, rendering, school-style CSS, and verification. | Yes |
| Timeline and cards first | Smaller scope but would under-deliver the roadmap. | |
| Timeline, cards, gallery first; defer smartart | Reduces SmartArt generality but leaves a roadmap item unfinished. | |
| Claude decides | Choose the scope that best balances completion and risk. | |

**User's choice:** Deliver all four layout families.
**Notes:** Existing helper functions must be fully connected and verified rather than left dormant.

---

## SmartArt Naming

| Option | Description | Selected |
|--------|-------------|----------|
| Use `smartart` with `type=` | Keep process/cycle/pyramid/picture under `::: smartart type=... :::`. | Yes |
| Add a separate `process` alias | More direct for teachers but adds parser/docs/verification surface. | |
| Claude decides | Choose based on maintainability. | |

**User's choice:** Use `smartart` with `type=`.
**Notes:** Do not add a separate `process` directive in Phase 15.

---

## Semantic Icons and School Style

| Option | Description | Selected |
|--------|-------------|----------|
| Default automatic icons, with `icon=none` opt-out | Ordinary slides and structured items get skill-local semantic icons by default. | Yes |
| Default off; explicit `icon=auto` only | More restrained but easier for agents to omit. | |
| Structure blocks only | Avoids title decoration while keeping structured pages richer. | |
| Claude decides | Choose based on school style and readability. | |

**User's choice:** Default automatic icons, with `icon=none` opt-out.
**Notes:** Icons must stay in the local blue-green school identity style, without external libraries or network dependencies.

---

## Verification and Acceptance

| Option | Description | Selected |
|--------|-------------|----------|
| Strong fixture plus manifest/token verification, no default browser screenshot gate | Fixture covers all new syntax; `verify` checks repeatability and interaction compatibility; user manually inspects output artifacts. | Yes |
| Add Playwright screenshot gate | Stronger visual signal but higher dependency and execution cost. | |
| Token-only checks | Fast but too weak for structure rendering correctness. | |
| Claude decides | Choose based on current GSD verification style. | |

**User's choice:** Strong fixture plus manifest/token verification, plus human artifact review.
**Notes:** The user explicitly wants to inspect the generated output artifacts manually.

---

## Claude's Discretion

- Exact structure CSS details, density, and token names are left to the planner/implementer as long as the result stays formal, classroom-readable, deterministic, and aligned with the existing school identity.

## Deferred Ideas

- Print/export review and full v1.8 regression packaging belong to Phase 16.
- Drag-and-drop sorting, hosted collaboration, remote control, audience sync, annotation persistence, PPTX export, Keynote export, and editable PowerPoint output stay out of Phase 15.
