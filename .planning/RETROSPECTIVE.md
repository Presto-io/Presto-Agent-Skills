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

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | 3 | 3 | Established canonical-template-first documentation and deferred unused examples. |
| v1.7 | 3+ | 3 | Added fixed-template document package generation with strict review gates and audit-driven closure. |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.0 | Local Markdown and artifact checks | 9/9 v1 requirements shipped | 0 runtime dependencies added |
| v1.7 | Script verifier, Typst/PDF compile when available, table/workbook repeatability, milestone audit | 8/8 ETM requirements shipped | Reused standard shell/Python workflow |

### Top Lessons (Verified Across Milestones)

1. Canonical source first, runtime notes second.
2. Keep optional artifacts out until they have a real user.
3. Preserve a reviewable Markdown checkpoint before final document exports.
