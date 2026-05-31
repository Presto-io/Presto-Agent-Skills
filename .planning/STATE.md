---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: School Presentation Skill
current_phase: Not started (defining requirements)
status: Defining requirements
stopped_at: Phase 8 context gathered
last_updated: "2026-05-31T14:57:03.655Z"
last_activity: 2026-05-31 — Milestone v1.5 started
progress:
  total_phases: 5
  completed_phases: 4
  total_plans: 4
  completed_plans: 4
  percent: 100
---

# State: Presto Agent Skills

**Initialized:** 2026-05-30
**Current Phase:** Not started (defining requirements)
**Status:** Defining requirements

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-31)

**Core value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.
**Current focus:** v1.5 School Presentation Skill - Markdown-to-single-file-HTML school presentation workflow

## Workflow Preferences

- Mode: YOLO
- Granularity: Coarse
- Execution: Parallel
- Planning docs committed: Yes
- Research: Yes
- Plan Check: Yes
- Verifier: Yes
- AI Models: Balanced

## Supported Runtime Targets

- Codex
- Claude Code
- Gemini CLI
- OpenCode
- OpenClaw
- Hermes Agent

## Next Up

Plan Phase 8 for `school-presentation`: extract school identity assets, define Markdown logical-slide structure, implement fixed HTML layouts, and verify overflow-safe static output.

## Decisions

- Preserved Phase 1 as documentation-only: baseline audit plus minimal patches, no tooling/runtime expansion.
- README and directory spec are the contributor-facing contract; AGENTS remains the concise agent constraint surface.
- Phase 2 keeps one canonical `SKILL.md` as the primary cross-agent artifact, with runtime adapter notes as lightweight install/use compatibility guidance.
- OpenClaw and Hermes Agent remain first-class required v1 targets, with installation-time verification cautions where behavior is not locally verified.
- [Phase 03]: EX-01 and EX-02 are deferred as optional example guidance; v1 stays centered on the canonical SKILL.md contract. — User clarified that examples are human-facing and should not drive AI-skill development for v1.
- [Phase 03]: Removed unused examples directory from v1; examples will only be created later for a concrete contributor need. — The user clarified that unused files and directories should not remain just as optional placeholders.
- [Phase 03]: Removed standalone adapters and adapter-template directories from v1; runtime differences now live only in canonical SKILL.md Runtime Adapter Notes. — The directories were not runtime-loaded and acted as unused placeholders.
- [Milestone v1.1]: Document workflow skills use Markdown as the canonical intermediate representation. — User clarified that the milestone should stay centered on the shared intermediate, not output-specific phases.
- [Milestone v1.1]: Output-specific follow-up phases were removed from the current roadmap. — User clarified that they are not needed for the present direction.
- [Phase 04]: Document workflow skills normalize source material into a persistent Markdown intermediate before target generation. — Phase 4 created `docs/markdown-normalization-contract.md` and linked it from README, directory spec, and the skill template.
- [Phase 04]: The shared Markdown contract stays behavioral and does not define universal metadata fields or a universal marker taxonomy. — Template-specific metadata, marker syntax, scripts, and renderer rules remain owned by the relevant skill/template or later target-specific docs.
- [Milestone v1.2]: `gongwen` is the first concrete skill. — User provided a Presto gongwen fixture and requested the trigger word `gongwen` for similar official-document writing.
- [Phase 05]: The Presto `presto-template-gongwen` executable is treated as a black-box Markdown-to-Typst renderer. — Skill scripts call it through stdin/stdout and use Typst for PDF verification.
- [Milestone v1.3]: `jiaoan-shicao` is the second concrete skill. — User provided a Presto jiaoan-shicao fixture, `calendar.json`, and requested the trigger word for practical lesson-plan writing.
- [Phase 06]: The Presto `presto-template-jiaoan-shicao` executable is treated as a black-box Markdown-to-Typst renderer. — Skill scripts call it through stdin/stdout and use Typst for PDF verification.
- [Milestone v1.4]: `jiaoan-jihua` adds a teaching-schedule workflow. — User provided a Presto jiaoan-jihua fixture, `calendar.json`, and requested the trigger word for授课进度计划 writing.
- [Phase 07]: The Presto `presto-template-jiaoan-jihua` executable is treated as a black-box Markdown-to-Typst renderer. — Skill scripts call it through stdin/stdout and use Typst for PDF verification.
- [Milestone v1.5]: `school-presentation` will generate school-style HTML presentations. — User clarified that PPTX output was unstable and the preferred route is a Markdown intermediate rendered to an offline single-file HTML deck.
- [Milestone v1.5]: Markdown pages are logical slides, not necessarily physical pages. — If a logical slide contains too much content, the renderer should split it into multiple physical HTML pages while keeping the Markdown easy to edit.
- [Milestone v1.5]: User images should preserve their original aspect ratio. — Images should be scaled and placed without cropping by default.

## Performance Metrics

| Phase | Plan | Duration | Tasks | Files |
|-------|------|----------|-------|-------|
| 01-repository-and-gsd-foundation | 01 | 4min | 3 | 5 |
| 02-canonical-skill-format-and-runtime-adapters | 01 | 18min | 4 | 11 |
| Phase 03 P01 | 12min | 3 tasks | 7 files |
| Phase 04 P01 | 21min | 3 tasks | 4 files |
| Phase 05 P01 | current session | 3 tasks | 7 files |
| Phase 06 P01 | current session | 3 tasks | 8 files |
| Phase 07 P01 | current session | 3 tasks | 8 files |

## Last Session

- **Completed:** 07-01-PLAN.md
- **Stopped At:** Phase 8 context gathered
- **Resume File:** .planning/phases/08-school-presentation-skill/08-CONTEXT.md

## Close Notes

- v1.0 archived ROADMAP and REQUIREMENTS under `.planning/milestones/`.
- Pre-close artifact audit reported Phase 01 human UAT as `resolved` with 0 pending scenarios; no actionable UAT gap remains.
- No dedicated milestone audit file existed before close. Phase summaries and the requirements archive record the shipped v1.0 evidence; the next milestone should run `/gsd:audit-milestone` before `/gsd:complete-milestone`.

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-05-31 — Milestone v1.5 started

## Operator Next Steps

- Start the next milestone with /gsd-new-milestone
