---
gsd_state_version: 1.0
milestone: v1.17
milestone_name: school-pptx
status: planning
stopped_at: Phase 42 context gathered
last_updated: "2026-07-13T11:03:12.094Z"
last_activity: 2026-07-13 - Completed Phase 41 controlled school-pptx template contract and template-report validation.
progress:
  total_phases: 4
  completed_phases: 1
  total_plans: 1
  completed_plans: 1
  percent: 100
---

# State: Presto Agent Skills

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-07-13 for v1.17 school-pptx)

**Core value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.
**Current focus:** Phase 42 - Markdown Contract and Full Fixture

## Current Position

Phase: 42 of 44 (Markdown Contract and Full Fixture)
Plan: TBD
Status: Ready to plan
Last activity: 2026-07-13 - Completed Phase 41 controlled school-pptx template contract and template-report validation.

Progress: [###-------] 25%

## Workflow Preferences

- Mode: YOLO
- Granularity: Coarse
- Execution: Parallel
- Research: Yes
- Plan Check: Yes
- Verifier: Yes
- UI phase hints: Yes

## Active Milestone Summary

v1.17 builds `school-pptx`, a Markdown-first skill that turns structured logical slides into editable, template-consistent `.pptx` output.

Phase order:

- Phase 41: Standard template and manifest
- Phase 42: Markdown contract and full fixture
- Phase 43: Editable PPTX renderer and pagination
- Phase 44: Verification gate, runtime notes, and UAT

## Accumulated Context

### Decisions

- [v1.17]: Phase numbering continues after v1.16; this milestone starts at Phase 41 and ends at Phase 44.
- [v1.17]: Requirements coverage is limited to current v1.17 requirements only.
- [v1.17]: Build order follows research: hand-normalized standard template, hand-authored Markdown fixture/contract, renderer, then verification/runtime/UAT gate.
- [v1.17]: `school-pptx` is a new PPTX skill line, not a reopening of `school-presentation` HTML output.
- [Phase 41]: `standard-school` is the first controlled PPTX theme and is backed by a skill-local `.pptx`, YAML manifest, and `template-report` evidence command.

### Pending Todos

None yet.

### Blockers/Concerns

- Phase 43 may need implementation spikes for `python-pptx` notes, table objects, placeholder behavior, text fitting, and image contain placement.
- Phase 44 requires manual visual UAT evidence in at least one compatible PPTX viewer before milestone acceptance.

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| quick_task | 260615-0853-correct-v114-doc-boundary | legacy `audit-open` reported missing; existing plan, summary, and verification files are present | v1.15 |

## Session Continuity

Last session: 2026-07-13T11:03:12.084Z
Stopped at: Phase 42 context gathered
Resume file: .planning/phases/42-markdown-contract-and-full-fixture/42-CONTEXT.md
