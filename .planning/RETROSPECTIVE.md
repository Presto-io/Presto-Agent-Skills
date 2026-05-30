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

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | 3 | 3 | Established canonical-template-first documentation and deferred unused examples. |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.0 | Local Markdown and artifact checks | 9/9 v1 requirements shipped | 0 runtime dependencies added |

### Top Lessons (Verified Across Milestones)

1. Canonical source first, runtime notes second.
2. Keep optional artifacts out until they have a real user.
