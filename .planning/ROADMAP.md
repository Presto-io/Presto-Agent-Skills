# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Last updated:** 2026-05-31 after removing output-specific follow-up phases
**Granularity:** Coarse
**Project Mode:** MVP

## Milestones

- **Shipped: v1.0 MVP** - Phases 1-3, shipped 2026-05-30. Full archive: `.planning/milestones/v1.0-ROADMAP.md`
- **Planned: v1.1 Document Workflow** - Phase 4, started 2026-05-31. Requirements: `.planning/REQUIREMENTS.md`

## Phases

<details>
<summary>v1.0 MVP (Phases 1-3) - SHIPPED 2026-05-30</summary>

- [x] Phase 1: Repository and GSD Foundation (1/1 plans) - completed 2026-05-30
- [x] Phase 2: Canonical Skill Format and Runtime Notes (1/1 plans) - completed 2026-05-30
- [x] Phase 3: Portable Example Scope Reconciliation (1/1 plans) - completed 2026-05-30

</details>

### Phase 4: Markdown Normalization Contract

**Goal:** As a document workflow skill author, I want a clear Markdown normalization contract, so arbitrary source material can become one stable intermediate representation before any target-format rendering.
**Mode:** mvp

**Depends on:** None

**Requirements:** DWF-01, DWF-02

**Success Criteria:**
1. The repository documents Markdown as the required intermediate representation for document workflow skills.
2. The normalization contract covers common document primitives such as headings, paragraphs, lists, tables, code blocks, links, figures, callouts, and metadata.
3. Ambiguous, unsupported, or lossy source fragments have an explicit flagging convention instead of being silently dropped or guessed.

## Current Position

v1.0 is complete. v1.1 currently contains only the Markdown normalization contract from Phase 4. Output-specific follow-up phases have been removed from the current roadmap because they are not the right focus.

Phase 4 is complete. Reconfirm the next code direction before adding or planning any new phase.

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Repository and GSD Foundation | v1.0 | 1/1 | Complete | 2026-05-30 |
| 2. Canonical Skill Format and Runtime Notes | v1.0 | 1/1 | Complete | 2026-05-30 |
| 3. Portable Example Scope Reconciliation | v1.0 | 1/1 | Complete | 2026-05-30 |
| 4. Markdown Normalization Contract | v1.1 | 1/1 | Complete | 2026-05-31 |

## Requirement Coverage

v1.0 shipped 9 required items: DOC-01, DOC-02, DOC-03, PLAN-01, TMPL-01, TMPL-02, RT-01, RT-02, and RT-03.

v1.1 currently tracks 2 document workflow requirements: DWF-01 and DWF-02. Both are mapped to Phase 4 in `.planning/REQUIREMENTS.md` and are complete.

EX-01 and EX-02 were explicitly deferred as optional future example guidance, not v1 delivery requirements. See `.planning/milestones/v1.0-REQUIREMENTS.md` for the archived requirement record.

---
*Roadmap updated: 2026-05-31 after removing output-specific follow-up phases*
