# Phase 14: Presenter Markup Tools - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-11
**Phase:** 14-Presenter Markup Tools
**Areas discussed:** Tool palette placement, Pointer and tool behavior, Page-scoped annotation state, Navigation and input arbitration, Transition behavior

---

## Tool Palette Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Existing playback toolbar extension | Add tools to the current bottom playback control strip. | |
| iPad-style floating palette | Compact markup palette that can follow the mouse/pointer or slide/peek from an edge. | ✓ |
| Static settings panel | Larger fixed panel with detailed settings. | |

**User's choice:** Tool palette should be similar to Apple's iPad markup toolbar.
**Notes:** The palette should support lower-left, lower-right, left-side, and right-side positions. It may follow the mouse/pointer or slide/peek in from an edge.

---

## Pointer and Tool Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| iPad-like pointer | Pointer imitates Apple iPad pointer behavior and stays presenter-local. | ✓ |
| Simple laser dot | Minimal pointer dot with no iPad-like interaction feel. | |
| Permanent pointer marks | Pointer traces become part of saved annotations. | |

**User's choice:** Pointer should imitate Apple's iPad pointer.
**Notes:** Pen/highlighter tool selection is toggle-based: clicking the pen selects it, clicking the active pen again disengages it.

---

## Page-Scoped Annotation State

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve on navigation | Keep each physical page's annotations when navigating away and back. | ✓ |
| Clear on navigation | Automatically clear annotations when leaving a page. | |
| Save to source | Persist annotations into Markdown or deterministic artifacts. | |

**User's choice:** Flip-page navigation preserves annotations unless the presenter explicitly clears handwriting.
**Notes:** This locks annotations as session/page-local playback state, not authored Markdown content.

---

## Navigation and Input Arbitration

| Option | Description | Selected |
|--------|-------------|----------|
| Drawing mode owns pointer input | Active drawing tools disable normal click-zone navigation; keyboard left/right still navigates. | ✓ |
| Click zones always active | Drawing gestures may also trigger previous/next zones. | |
| Disable all navigation while drawing | Presenter must leave drawing mode before any navigation. | |

**User's choice:** In drawing mode, normal slide-turning is disabled except left/right keyboard navigation.
**Notes:** This requires explicit event arbitration with playback zones, mask-click reveal, and hover/peek behavior.

---

## Transition Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Animate annotations with the page | Page transition animation carries the visible annotation layer along with the slide. | ✓ |
| Pop annotations after transition | Slide animates first, annotations appear after. | |
| No annotation transition handling | Annotation layer is independent of slide transitions. | |

**User's choice:** Page-turn animation should also apply to handwriting/annotations.
**Notes:** Implementation should attach the annotation layer to the scaled page shell or otherwise synchronize it with the page swap/fade lifecycle.

---

## Claude's Discretion

- Choose conservative default pen/highlighter colors and stroke widths.
- Choose the technical rendering layer that best preserves fixed-canvas coordinates, offline single-file output, and deterministic verification.

## Deferred Ideas

- None.
