# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Last updated:** 2026-05-31 after removing Typst constraint phase
**Granularity:** Coarse
**Project Mode:** MVP

## Milestones

- **Shipped: v1.0 MVP** - Phases 1-3, shipped 2026-05-30. Full archive: `.planning/milestones/v1.0-ROADMAP.md`
- **Planned: v1.1 Document Workflow** - Phases 4-5, started 2026-05-31. Requirements: `.planning/REQUIREMENTS.md`

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

### Phase 5: HTML Output and Verification

**Goal:** As a document workflow skill author, I want semantic Markdown-to-HTML rules and shared verification checks, so HTML output preserves document intent from the shared Markdown intermediate.
**Mode:** mvp

**Depends on:** Phase 4

**Requirements:** DWF-03, DWF-04

**Success Criteria:**
1. The repository documents semantic HTML output rules derived from the same Markdown intermediate.
2. Verification guidance checks Markdown normalization and HTML output structure.
3. The workflow explains how HTML generation preserves document structure without bypassing the Markdown intermediate.

## Current Position

v1.0 is complete. v1.1 is now scoped around a markdown-first document workflow: arbitrary input becomes Markdown first, then semantic HTML is generated from the shared intermediate. The dedicated Typst constraint phase was removed because it is not the current focus.

Reconfirm the Phase 5 code direction before planning with `/gsd:plan-phase 5`.

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Repository and GSD Foundation | v1.0 | 1/1 | Complete | 2026-05-30 |
| 2. Canonical Skill Format and Runtime Notes | v1.0 | 1/1 | Complete | 2026-05-30 |
| 3. Portable Example Scope Reconciliation | v1.0 | 1/1 | Complete | 2026-05-30 |
| 4. Markdown Normalization Contract | v1.1 | 1/1 | Complete | 2026-05-31 |
| 5. HTML Output and Verification | v1.1 | 0/1 | Not started | - |

## Requirement Coverage

v1.0 shipped 9 required items: DOC-01, DOC-02, DOC-03, PLAN-01, TMPL-01, TMPL-02, RT-01, RT-02, and RT-03.

v1.1 currently tracks 4 document workflow requirements: DWF-01, DWF-02, DWF-03, and DWF-04. All 4 are mapped to Phases 4-5 in `.planning/REQUIREMENTS.md`.

EX-01 and EX-02 were explicitly deferred as optional future example guidance, not v1 delivery requirements. See `.planning/milestones/v1.0-REQUIREMENTS.md` for the archived requirement record.

---
*Roadmap updated: 2026-05-31 after removing Typst constraint phase*
