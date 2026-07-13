---
gsd_state_version: 1.0
milestone: v1.17
milestone_name: school-pptx
status: ready_to_plan
last_updated: "2026-07-13T00:00:00+08:00"
last_activity: 2026-07-13
progress:
  total_phases: 4
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# State: Presto Agent Skills

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-07-13 for v1.17 school-pptx)

**Core value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.
**Current focus:** Phase 41 - Standard Template and Manifest

## Current Position

Phase: 41 of 44 (Standard Template and Manifest)
Plan: TBD
Status: Ready to plan
Last activity: 2026-07-13 - Created v1.17 school-pptx roadmap and requirement traceability.

Progress: [----------] 0%

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

### Pending Todos

None yet.

### Blockers/Concerns

- Phase 41 needs the real supplied `.potx` visual sample or accepted local evidence before template normalization can be completed.
- Phase 43 may need implementation spikes for `python-pptx` notes, table objects, placeholder behavior, text fitting, and image contain placement.
- Phase 44 requires manual visual UAT evidence in at least one compatible PPTX viewer before milestone acceptance.

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| quick_task | 260615-0853-correct-v114-doc-boundary | legacy `audit-open` reported missing; existing plan, summary, and verification files are present | v1.15 |

## Session Continuity

Last session: 2026-07-13
Stopped at: v1.17 roadmap creation
Resume file: None
