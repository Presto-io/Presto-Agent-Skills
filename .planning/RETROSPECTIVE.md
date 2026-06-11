# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 - MVP

**Shipped:** 2026-05-30
**Phases:** 3 | **Plans:** 3 | **Sessions:** 3

### What Was Built

- A contributor-facing repository contract across README, directory spec, AGENTS, and GSD planning records.
- A canonical `templates/skill/SKILL.md` authoring path with embedded runtime adapter notes.
- Runtime compatibility guidance for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
- A lean v1 scope that removed unused examples and standalone adapter artifacts.

### What Worked

- Keeping `SKILL.md` as the semantic source of truth reduced drift between runtime targets.
- Documentation-only phases stayed fast when verification used local Markdown checks and requirement traceability.
- Scope reconciliation in Phase 3 prevented optional examples from hardening into v1 obligations.

### What Was Inefficient

- The milestone close began without a dedicated milestone audit file, so the close notes now record that as a process gap for the next release.
- The pre-close artifact audit counted a resolved UAT record as open even though it had 0 pending scenarios; future audit tooling may need a stricter actionable-item filter.

### Patterns Established

- New skills should start from `templates/skill/SKILL.md`.
- Runtime differences should remain in Runtime Adapter Notes unless a later milestone creates generated wrappers.
- Optional examples should be created only for a concrete contributor workflow.

### Key Lessons

1. Treat examples as proof tools, not default repository furniture.
2. Run `/gsd:audit-milestone` before `/gsd:complete-milestone` so close-out has a durable passed or accepted audit record.
3. Keep OpenClaw and Hermes Agent in every compatibility change so they do not drift into informal future support.

### Cost Observations

- Model mix: balanced profile.
- Sessions: 3 phase sessions plus milestone close.
- Notable: Most work stayed in Markdown, so local `rg` verification and concise phase summaries were enough for v1 confidence.

---

## Milestone: v1.7 - End-of-Term Teaching Materials Skill

**Shipped:** 2026-06-10
**Phases:** 3 | **Plans:** 3 | **Sessions:** 3+

### What Was Built

- A canonical `end-of-term-teaching-materials` skill for semester-end submission packages.
- A structured data contract and single teacher-editable Markdown source of truth.
- Fixed-template Typst/PDF package rendering, deterministic JSON/CSV table artifacts, and workbook output.
- Verification for clean final packages, uncertain-score Markdown review, strict final-export blocking, abnormal preview artifacts, and runtime adapter notes.

### What Worked

- Reusing the proven Markdown-first document-skill pattern kept scope focused.
- Treating historical teaching materials as already-extracted data prevented OCR/template-discovery creep.
- A dedicated closure phase was the right size for the audit gap around `87?` review handling.

### What Was Inefficient

- The first milestone audit surfaced missing metadata conventions after the renderer was already built.
- `audit-open` still reports passed/resolved UAT records as close-time items even when there are 0 pending scenarios.
- `milestone.complete` counted older unarchived phases in v1.7 statistics, so the generated MILESTONES entry needed manual correction.

### Patterns Established

- End-of-term workflows should preserve one Markdown checkpoint before Typst/PDF, workbook, or table output.
- Uncertain values such as `87?` belong in teacher review artifacts, not in final export.
- Abnormal review artifacts must be explicitly labeled non-final and carry machine-readable manifest status.

### Key Lessons

1. Run milestone audit before close, and treat gaps as first-class closure phases when they affect the user-facing review path.
2. Keep fixed-template rendering resources skill-local so future school-specific packs can be added without weakening the canonical skill.
3. Use strict final gates and explicit abnormal preview modes instead of silently guessing around unresolved review data.

### Cost Observations

- Model mix: balanced profile.
- Notable: Most complexity was in deterministic document generation and verification rather than in the skill description itself.

---

## Milestone: v1.8 - School Presentation Continuation

**Shipped:** 2026-06-11
**Phases:** 3 | **Plans:** 3 | **Sessions:** 6+

### What Was Built

- Playback-local presenter markup tools with pointer, pen, highlighter, eraser, clear current page, page-scoped session state, and deterministic annotation exclusion.
- Classroom interaction and structured layout helpers for peek, sorting, restrained body-step animation, timeline, cards, gallery, SmartArt-like process layouts, semantic icons, and section controls.
- Print/export review behavior plus one-click final PDF export with expanded review states, reader outline/bookmarks, agenda links, section-page include/skip behavior, and v1.8 regression verification.

### What Worked

- Continuing from the Phase 10 deferred scope kept the milestone focused.
- Browser/manual UAT gates were useful for live playback and final PDF control polish where manifest checks alone were not enough.
- The existing `verify` command absorbed new regression checks without introducing a separate renderer or screenshot-first gate.

### What Was Inefficient

- The automatic `milestone.complete` summary under-counted v1.8 because the active roadmap had already been partially collapsed.
- The final PDF path needed an extra product pass after browser print proved too indirect for the desired one-click workflow.
- UI polish for the presenter and top controls needed manual visual acceptance, so code completion and phase close had to stay separate.

### Patterns Established

- Presenter annotations remain playback-local and page-scoped; authored Markdown, manifests, preview, overview, thumbnails, and deterministic review artifacts stay annotation-free.
- Teacher-facing structured presentation syntax should stay readable and deterministic rather than exposing raw HTML.
- Final PDF export can live inside the generated offline HTML deck while keeping PPTX/Keynote export out of scope.

### Key Lessons

1. Treat live UI phases as complete only after explicit human visual UAT.
2. Re-run closeout archive outputs against the known phase range before trusting generated milestone statistics.
3. Keep print/export review on the same offline HTML pipeline unless a future milestone explicitly changes the output contract.

### Cost Observations

- Model mix: balanced profile.
- Notable: Most work stayed in one renderer and one deterministic verification command, but UI/PDF acceptance required several manual review loops.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | 3 | 3 | Established canonical-template-first documentation and deferred unused examples. |
| v1.7 | 3+ | 3 | Added fixed-template document package generation with strict review gates and audit-driven closure. |
| v1.8 | 6+ | 3 | Extended the school-presentation renderer through live markup, classroom structures, and one-click PDF export while preserving HTML-first delivery. |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.0 | Local Markdown and artifact checks | 9/9 v1 requirements shipped | 0 runtime dependencies added |
| v1.7 | Script verifier, Typst/PDF compile when available, table/workbook repeatability, milestone audit | 8/8 ETM requirements shipped | Reused standard shell/Python workflow |
| v1.8 | Script verifier, manifest checks, browser/manual UAT, PDF artifact sanity, milestone audit | 11/11 SP requirements shipped | Reused the existing shell/Python/HTML renderer path |

### Top Lessons (Verified Across Milestones)

1. Canonical source first, runtime notes second.
2. Keep optional artifacts out until they have a real user.
3. Preserve a reviewable Markdown checkpoint before final document exports.
4. Keep live presentation UI closeout tied to explicit visual UAT, not only code or state-file completion.
