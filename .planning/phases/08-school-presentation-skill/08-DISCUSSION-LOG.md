# Phase 8: School Presentation Skill - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-31
**Phase:** 8-School Presentation Skill
**Areas discussed:** Markdown slide structure, Layout selection, School identity assets, Media packaging, Verification direction

---

## Markdown Slide Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Claude designs it | Let planner/executor define the Markdown logical-slide schema within the existing Markdown normalization contract. | ✓ |
| User specifies it | User provides exact slide syntax and field structure before planning. | |

**User's choice:** "你来设计"
**Notes:** The schema must support fixed layout intents, speaker notes, review warnings, formulas, tables, charts, images, videos, and text blocks while keeping Markdown as source of truth.

---

## Layout Selection

| Option | Description | Selected |
|--------|-------------|----------|
| Automatic with override | Renderer chooses a layout by default; user can override when needed. | ✓ |
| Manual only | Every slide explicitly names its layout. | |
| Automatic only | Renderer always chooses; no user-level layout override. | |

**User's choice:** "自动选择，用户也可以改"
**Notes:** This locks default ergonomics while keeping author control for special slides.

---

## School Identity Assets

| Option | Description | Selected |
|--------|-------------|----------|
| Skill-local directory chosen by Claude | Store school elements inside the `school-presentation` skill directory; planner/executor decide exact subdirectory. | ✓ |
| User-defined path | User provides the exact storage layout before planning. | |

**User's choice:** "学校的元素放在技能的某个目录下，你来定"
**Notes:** Existing repository conventions suggest `references/` for extracted provenance and a clear skill-local asset directory for reusable renderer assets.

---

## Media Packaging

| Option | Description | Selected |
|--------|-------------|----------|
| 50 MB capped HTML package | Keep output at or below 50 MB; use documented fallback for oversized media. | ✓ |
| Embed everything regardless of size | Always inline all media into one HTML file. | |
| External assets by default | Always keep media outside the HTML deck. | |

**User's choice:** "产物体积不要超过50M"
**Notes:** This makes large-video behavior a required renderer and documentation decision.

---

## Verification Direction

| Option | Description | Selected |
|--------|-------------|----------|
| Human visual verification plus deterministic checks | User handles subjective review; automation checks repeatability and Markdown-to-output control behavior. | ✓ |
| Full visual automation | Add automated visual judgment as a primary gate. | |
| File-existence only | Only check that output files are created. | |

**User's choice:** "我来人工验证，你只需要保证每次输出的一致性和模板（markdown对产物的影响）设计的合理性即可"
**Notes:** Verification should prove stable output and reasonable template controls, not replace the user's final visual judgment.

---

## Claude's Discretion

- Design the Markdown logical-slide schema.
- Choose the exact skill-local directory structure for school identity assets.
- Choose the deterministic checks needed to prove output consistency and template-control reasonableness.

## Deferred Ideas

None.
