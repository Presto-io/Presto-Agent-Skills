# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Last updated:** 2026-06-11 after Phase 15 completion
**Granularity:** Coarse
**Project Mode:** MVP

## Milestones

- **Shipped: v1.0 MVP** - Phases 1-3, shipped 2026-05-30. Full archive: `.planning/milestones/v1.0-ROADMAP.md`
- **Completed: v1.1 Document Workflow** - Phase 4, completed 2026-05-31. Requirements archive: `.planning/milestones/v1.1-REQUIREMENTS.md`
- **Completed: v1.2 Gongwen Skill** - Phase 5, completed 2026-05-31. Requirements archive: `.planning/milestones/v1.2-REQUIREMENTS.md`
- **Completed: v1.3 Jiaoan Shicao Skill** - Phase 6, completed 2026-05-31. Requirements archive: `.planning/milestones/v1.3-REQUIREMENTS.md`
- **Completed: v1.4 Jiaoan Jihua Skill** - Phase 7, completed 2026-05-31. Requirements archive: `.planning/milestones/v1.4-REQUIREMENTS.md`
- **Completed: v1.5 School Presentation Skill** - Phase 8, completed 2026-06-01. Requirements archive: `.planning/milestones/v1.5-REQUIREMENTS.md`
- **Shipped: v1.6 School Presentation Playback UX** - Phases 9-10, automated verification passed 2026-06-03; Phase 10 visual UAT passed 2026-06-11. Requirements archive: `.planning/milestones/v1.6-REQUIREMENTS.md`
- **Shipped: v1.7 End-of-Term Teaching Materials Skill** - Phases 11-13, shipped 2026-06-10. Requirements archive: `.planning/milestones/v1.7-REQUIREMENTS.md`
- **Active: v1.8 School Presentation Continuation** - Phases 14-16, started 2026-06-11.

## Completed Phase Archive

Previous milestone summaries are preserved in `.planning/milestones/` and the repository history. The active phase directory is reserved for v1.8 planning and execution.

| Phase | Milestone | Status | Completed |
|-------|-----------|--------|-----------|
| 1. Repository and GSD Foundation | v1.0 | Complete | 2026-05-30 |
| 2. Canonical Skill Format and Runtime Notes | v1.0 | Complete | 2026-05-30 |
| 3. Portable Example Scope Reconciliation | v1.0 | Complete | 2026-05-30 |
| 4. Markdown Normalization Contract | v1.1 | Complete | 2026-05-31 |
| 5. Gongwen Skill | v1.2 | Complete | 2026-05-31 |
| 6. Jiaoan Shicao Skill | v1.3 | Complete | 2026-05-31 |
| 7. Jiaoan Jihua Skill | v1.4 | Complete | 2026-05-31 |
| 8. School Presentation Skill | v1.5 | Complete | 2026-06-01 |
| 9. Playback Workspace and Page Hierarchy | v1.6 | Complete | 2026-06-01 |
| 10. Ordered Reveals and Classroom Answer Masks | v1.6 | Complete | 2026-06-03 |
| 11. End-of-Term Data and Markdown Contract | v1.7 | Complete | 2026-06-09 |
| 12. Fixed-Template Rendering and Verification | v1.7 | Complete | 2026-06-09 |
| 13. Close gap: uncertain scores reach Markdown review | v1.7 | Complete | 2026-06-10 |
| 14. Presenter Markup Tools | v1.8 | Complete | 2026-06-11 |

## Active Phases

### Phase 14: Presenter Markup Tools

**Goal:** As a presenter, I want playback-local pointer, pen, highlighter, eraser, and clear/reset tools, so I can mark up a class presentation live without changing the Markdown source or deterministic deck review artifacts.
**Mode:** mvp
**Status:** Complete

**Depends on:** Phase 10

**Requirements:** SP-17, SP-18, SP-19, SP-20

**Success Criteria:**
1. The playback UI exposes presenter marking controls that work with mouse, keyboard, and touch where practical.
2. Pointer, pen, highlighter, eraser, and clear/reset behavior are scoped to the active session and physical page.
3. Annotation state does not mutate the Markdown source, manifest hierarchy, preview workspace content, or deterministic review output.
4. Existing navigation, ordered reveals, emphasis animation, and answer masks continue to work while marking tools are enabled.
5. The verification fixture and manifest checks prove marking controls are present and do not regress Phase 9/10 behavior.

### Phase 15: Classroom Interaction and Structured Layout Extensions

**Goal:** As a Markdown author, I want the Phase 10 deferred classroom interaction and structured layout helpers, so lessons can include hover/peek hints, sorting exercises, restrained body steps, timelines, cards, gallery/compare pages, and school-style process layouts without raw HTML.
**Mode:** mvp
**Status:** Complete

**Depends on:** Phase 14

**Requirements:** SP-21, SP-22, SP-23, SP-24, SP-25

**Success Criteria:**
1. Markdown can express hover/peek content without replacing deterministic click-based reveal order.
2. Markdown can express sorting or reordering exercises with stable initial and answer states.
3. Body-step animation remains restrained and has readable preview/static fallback behavior.
4. Structured layout intents for timeline, cards, gallery/compare, and process/SmartArt-like sections render in the existing school identity system.
5. Optional semantic icons and section-divider or section-cover controls are documented, rendered, and verified without introducing raw HTML authoring.

### Phase 16: Print Export Review and v1.8 Regression Gate

**Goal:** As a presenter or reviewer, I want a print/export-friendly deck review view and full regression gate, so v1.8 additions can be checked outside live playback while preserving offline single-file output and fixed slide-canvas stability.
**Mode:** mvp

**Depends on:** Phase 15

**Requirements:** SP-26, SP-27

**Success Criteria:**
1. The generated deck includes a print/export-friendly review mode or artifact where reveal and mask states are inspectable.
2. Presenter-local annotations are excluded or flattened deterministically in print/export review behavior.
3. Verification covers v1.8 markup tools, classroom interactions, structured layouts, print/export review, offline single-file boundaries, and fixed `16:9`/`4:3` canvas behavior.
4. The canonical `SKILL.md`, template fixture, and runtime adapter notes describe the v1.8 behavior without adding runtime-specific wrapper syntax.
5. Human visual UAT scope is recorded for the final deck because the milestone changes live playback and printed/exported review surfaces.

## Current Position

v1.8 is active and continues the `school-presentation` line. Phase 15 is complete; the next slice is Phase 16 print/export review and the v1.8 regression gate.

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 14. Presenter Markup Tools | v1.8 | 1/1 | Complete | 2026-06-11 |
| 15. Classroom Interaction and Structured Layout Extensions | v1.8 | 1/1 | Complete | 2026-06-11 |
| 16. Print Export Review and v1.8 Regression Gate | v1.8 | 0/1 | Not Started | - |

## Requirement Coverage

v1.8 tracks 11 school-presentation continuation requirements: SP-17 through SP-27.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SP-17 | Phase 14 | Complete |
| SP-18 | Phase 14 | Complete |
| SP-19 | Phase 14 | Complete |
| SP-20 | Phase 14 | Complete |
| SP-21 | Phase 15 | Complete |
| SP-22 | Phase 15 | Complete |
| SP-23 | Phase 15 | Complete |
| SP-24 | Phase 15 | Complete |
| SP-25 | Phase 15 | Complete |
| SP-26 | Phase 16 | Pending |
| SP-27 | Phase 16 | Pending |

**Coverage:**
- v1.8 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0

---
*Roadmap updated: 2026-06-11 after Phase 15 classroom interaction and structured layout completion*
