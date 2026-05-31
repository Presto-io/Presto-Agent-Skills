# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Last updated:** 2026-05-31 after v1.4 jiaoan-jihua skill implementation
**Granularity:** Coarse
**Project Mode:** MVP

## Milestones

- **Shipped: v1.0 MVP** - Phases 1-3, shipped 2026-05-30. Full archive: `.planning/milestones/v1.0-ROADMAP.md`
- **Completed: v1.1 Document Workflow** - Phase 4, completed 2026-05-31. Requirements: `.planning/REQUIREMENTS.md`
- **Completed: v1.2 Gongwen Skill** - Phase 5, completed 2026-05-31. Requirements: `.planning/REQUIREMENTS.md`
- **Completed: v1.3 Jiaoan Shicao Skill** - Phase 6, completed 2026-05-31. Requirements: `.planning/REQUIREMENTS.md`
- **Completed: v1.4 Jiaoan Jihua Skill** - Phase 7, completed 2026-05-31. Requirements: `.planning/REQUIREMENTS.md`

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

### Phase 5: Gongwen Skill

**Goal:** As a document workflow skill author, I want the first concrete `gongwen` skill to produce a stable Markdown intermediate and verified Typst/PDF artifacts, so class-official-document writing can be reused across supported agent runtimes.
**Mode:** mvp

**Depends on:** Phase 4

**Requirements:** GW-01, GW-02, GW-03, GW-04, GW-05

**Success Criteria:**
1. `skills/gongwen/SKILL.md` defines trigger wording, workflow, outputs, verification, safety boundaries, and adapter notes for all required runtimes.
2. `skills/gongwen/templates/gongwen-full.md` provides a reusable Markdown intermediate structure.
3. `skills/gongwen/scripts/gongwen.sh` renders Markdown through the Presto gongwen template and compiles/verifies Typst/PDF artifacts.
4. The provided fixture `gongwen-full.md` produces Typst and PDF output matching the provided references.

### Phase 6: Jiaoan Shicao Skill

**Goal:** As a document workflow skill author, I want the second concrete `jiaoan-shicao` skill to produce a stable Markdown intermediate and verified Typst/PDF artifacts, so practical lesson-plan writing can be reused across supported agent runtimes.
**Mode:** mvp

**Depends on:** Phase 4

**Requirements:** JS-01, JS-02, JS-03, JS-04, JS-05

**Success Criteria:**
1. `skills/jiaoan-shicao/SKILL.md` defines trigger wording, workflow, outputs, verification, safety boundaries, and adapter notes for all required runtimes.
2. `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md` provides a reusable Markdown intermediate structure.
3. `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` renders Markdown through the Presto `jiaoan-shicao` template and compiles/verifies Typst/PDF artifacts.
4. The provided fixture `jiaoan-shicao-full.md` produces Typst matching the provided reference and a compiled PDF verification artifact.

### Phase 7: Jiaoan Jihua Skill

**Goal:** As a document workflow skill author, I want the next concrete `jiaoan-jihua` skill to produce a stable Markdown intermediate and verified Typst/PDF artifacts, so授课进度计划 writing can be reused across supported agent runtimes.
**Mode:** mvp

**Depends on:** Phase 4

**Requirements:** JH-01, JH-02, JH-03, JH-04, JH-05

**Success Criteria:**
1. `skills/jiaoan-jihua/SKILL.md` defines trigger wording, workflow, outputs, verification, safety boundaries, and adapter notes for all required runtimes.
2. `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md` provides a reusable Markdown intermediate structure.
3. `skills/jiaoan-jihua/references/calendar.json` provides the bundled teaching-calendar support resource.
4. `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` renders Markdown through the Presto `jiaoan-jihua` template and compiles/verifies Typst/PDF artifacts.
5. The provided fixture `jiaoan-jihua-full.md` produces Typst matching the provided reference and a compiled PDF verification artifact.

## Current Position

v1.0 is complete. v1.1 contains the Markdown normalization contract from Phase 4. v1.2 adds the first concrete `gongwen` skill in Phase 5. v1.3 adds `jiaoan-shicao` as the second concrete skill in Phase 6. v1.4 adds `jiaoan-jihua` as the next concrete skill in Phase 7.

Phase 7 is complete. Reconfirm the next code direction before adding or planning any new phase.

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Repository and GSD Foundation | v1.0 | 1/1 | Complete | 2026-05-30 |
| 2. Canonical Skill Format and Runtime Notes | v1.0 | 1/1 | Complete | 2026-05-30 |
| 3. Portable Example Scope Reconciliation | v1.0 | 1/1 | Complete | 2026-05-30 |
| 4. Markdown Normalization Contract | v1.1 | 1/1 | Complete | 2026-05-31 |
| 5. Gongwen Skill | v1.2 | 1/1 | Complete | 2026-05-31 |
| 6. Jiaoan Shicao Skill | v1.3 | 1/1 | Complete | 2026-05-31 |
| 7. Jiaoan Jihua Skill | v1.4 | 1/1 | Complete | 2026-05-31 |

## Requirement Coverage

v1.0 shipped 9 required items: DOC-01, DOC-02, DOC-03, PLAN-01, TMPL-01, TMPL-02, RT-01, RT-02, and RT-03.

v1.1 tracks 2 document workflow requirements: DWF-01 and DWF-02. Both are mapped to Phase 4 in `.planning/REQUIREMENTS.md` and are complete.

v1.2 tracks 5 gongwen skill requirements: GW-01 through GW-05. All are mapped to Phase 5 and are complete.

v1.3 tracks 5 jiaoan-shicao skill requirements: JS-01 through JS-05. All are mapped to Phase 6 and are complete.

v1.4 tracks 5 jiaoan-jihua skill requirements: JH-01 through JH-05. All are mapped to Phase 7 and are complete.

EX-01 and EX-02 were explicitly deferred as optional future example guidance, not v1 delivery requirements. See `.planning/milestones/v1.0-REQUIREMENTS.md` for the archived requirement record.

---
*Roadmap updated: 2026-05-31 after v1.4 jiaoan-jihua skill implementation*
