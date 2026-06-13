---
gsd_state_version: 1.0
milestone: v1.10
milestone_name: "Jiaoan Typst 1:1 Conversion"
current_phase: 20
status: executing
stopped_at: Phase 21 context gathered
last_updated: "2026-06-13T16:59:19.722Z"
last_activity: 2026-06-14 -- Phase 21 planning complete
progress:
  total_phases: 2
  completed_phases: 0
  total_plans: 1
  completed_plans: 0
  percent: 0
---

# State: Presto Agent Skills

**Initialized:** 2026-05-30
**Current Phase:** 20
**Status:** Ready to execute

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-14)

**Core value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.
**Current focus:** v1.10 Jiaoan Typst 1:1 Conversion.

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

Start either parallel phase:

- Phase 20: Jiaoan Shicao 教案 1:1 Typst Conversion
- Phase 21: Jiaoan Jihua 授课计划 1:1 Typst Conversion

## Accumulated Context

### Roadmap Evolution

- Phase 13 completed: Close gap: ETM-04/ETM-06/ETM-08 — uncertain scores reach Markdown review while final export remains strict
- Milestone v1.8 started: Continue official-school presentation development from the Phase 10 deferred scope.
- Phase 14 completed: Playback-local presenter markup tools now cover pointer, pen, highlighter, eraser, clear current page, page-scoped session state, deterministic verification, and manual UAT without mutating authored artifacts.
- Phase 15 completed: Classroom interaction and structured layout extensions connect peek, sort, restrained body-step animation, timeline/cards/gallery/smartart directives, semantic icons, section-divider controls, and deterministic verification.
- Phase 16 planned: Print/export review will formalize same-HTML review mode, browser PDF UAT, section-title print controls, annotation exclusion, gallery pagination, and the full v1.8 regression gate.
- Phase 16 completed: The offline HTML deck now includes generated print review controls, full physical-page PDF review output, section-divider print inclusion/exclusion, expanded reveal/mask/emphasis/sort review semantics, annotation exclusion, gallery card pagination hooks, 16:9 and 4:3 ratio checks, deterministic `print_review_verified` regression evidence, one-click final PDF export, and the user-accepted floating capsule top/playback control design.
- Milestone v1.8 archived: ROADMAP, REQUIREMENTS, and passed milestone audit are preserved under `.planning/milestones/`.
- Phase 18 completed: `school-presentation.sh`, `render_package.py`, and `gongwen.sh` now use skill-local modules or sourced helpers while preserving public command surfaces, common flags, Markdown intermediates, manifest keys, and artifact contracts.
- Phase 19 completed: contributor guidance now documents the lightweight-entry and script-module decomposition pattern, affected skill artifact contracts are discoverable from README/skills index, and phase-local pre-audit evidence records Phase 17/18 before/after facts without marking v1.9 shipped.
- Milestone v1.9 archived: ROADMAP, REQUIREMENTS, and the passed milestone audit are preserved under `.planning/milestones/`; no next milestone has been started.
- Milestone v1.10 started: strict 1:1 Markdown-to-Typst conversion is scoped to the existing `jiaoan-shicao` and `jiaoan-jihua` skills, with separate parallel phases for the教案 and授课计划 fixture pairs under `test/1.10/`.

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
- [Phase 05]: The Presto `presto-template-gongwen` executable is treated as the Markdown-to-Typst renderer. — Skill scripts call it through stdin/stdout and use Typst for PDF verification.
- [Milestone v1.3]: `jiaoan-shicao` is the second concrete skill. — User provided a Presto jiaoan-shicao fixture, `calendar.json`, and requested the trigger word for practical lesson-plan writing.
- [Phase 06]: The Presto `presto-template-jiaoan-shicao` executable is treated as the Markdown-to-Typst renderer. — Skill scripts call it through stdin/stdout and use Typst for PDF verification.
- [Milestone v1.4]: `jiaoan-jihua` adds a teaching-schedule workflow. — User provided a Presto jiaoan-jihua fixture, `calendar.json`, and requested the trigger word for授课进度计划 writing.
- [Phase 07]: The Presto `presto-template-jiaoan-jihua` executable is treated as the Markdown-to-Typst renderer. — Skill scripts call it through stdin/stdout and use Typst for PDF verification.
- [Milestone v1.5]: `school-presentation` generates school-style HTML presentations. — User clarified that PPTX output was unstable and the preferred route is a Markdown intermediate rendered to an offline single-file HTML deck.
- [Milestone v1.5]: Markdown pages are logical slides, not necessarily physical pages. — If a logical slide contains too much content, the renderer should split it into multiple physical HTML pages while keeping the Markdown easy to edit.
- [Milestone v1.5]: User images should preserve their original aspect ratio. — Images should be scaled and placed without cropping by default.
- [Milestone v1.6]: Playback UX comes before marking tools. — User requested playback, thumbnail/preview/overview, hierarchy, ordered reveal, emphasis animation, and answer masks now; marking-style tools are deferred to the next milestone.
- [Milestone v1.6]: Phase 10 visual UAT passed. — User reported display defects on 2026-06-10; after the visual-fix pass, user confirmed Phase 10 manual visual acceptance passed on 2026-06-11.
- [Milestone v1.8]: The next `school-presentation` milestone resumes deferred presenter markup, classroom interaction extensions, structured layouts, and print/export review behavior. — User requested v1.8 continue official template presentation development and read previous undeveloped phases.
- [Milestone v1.7]: The end-of-term teaching-materials skill should use structured data -> Markdown -> Typst -> PDF. — User requested a fixed-template workflow for semester-end submission documents and tables.
- [Milestone v1.7]: Skip external research for this milestone. — The work follows already validated document-skill patterns in this repository.
- [Phase 11]: The end-of-term teaching-materials skill now has a contract-only slice. — Phase 11 added the canonical skill, data contract, and Markdown intermediate while leaving rendering scripts, Excel, Typst, PDF, and deterministic table artifacts to Phase 12.
- [Phase 12]: Fixed-template rendering is complete. — The skill now has skill-local templates, sanitized fixtures, script entry points, deterministic table artifacts, workbook output, Typst/PDF package generation, and verification while keeping OCR and arbitrary template discovery out of scope.
- [Phase 12]: Manual verification passed. — User confirmed the generated package is accepted against external reference materials on 2026-06-10.
- [Phase 13]: Uncertain-score review closure is complete. — Structured `87?` values can reach Markdown review with matching markers, normal final export remains strict, and explicit abnormal preview artifacts record non-final status plus red highlight evidence.
- [Phase 14]: Presenter markup is playback-local session state only. — Pointer, pen, highlighter, eraser, and clear current page live in the generated playback UI; Markdown, `.page-source`, preview workspace, overview, thumbnails, and manifests stay annotation-free.
- [Phase 15]: Classroom interaction and structured layout execution is complete. — The renderer connects teacher-facing Markdown directives to deterministic offline HTML, verifies real fixture rendering, preserves unknown directive content, and marks SP-21 through SP-25 complete.
- [Phase 18]: Shared Bash helper extraction stayed skill-local. — The secondary jiaoan scripts were left untouched because a broader shared framework was not justified by a stable Phase 18 contract.
- [Phase 19]: Decomposition guidance remains documentation/evidence-only. — Formal v1.9 audit, complete-milestone, milestone archive, generated wrappers, linting, scaffolding, hosted workflows, office-suite automation, and new output formats remain out of scope for this execute-phase run.
- [Milestone v1.10]: Keep fixture conversion inside each affected skill. — User required final conversion through skill-internal script code and strict generated-output verification against the two target `.typ` files.

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
| Phase 08 P01 | current session | 3 tasks | 8 files |
| Phase 09 P01 | current session | 4 tasks | 6 files |
| Phase 10 P01 | current session | 5 tasks | 7 files |
| Phase 11 P01 | current session | 6 tasks | 8 files |
| Phase 12 P01 | current session | 7 tasks | 15 files |
| Phase 14 P01 | current session | 6 tasks | 7 files |
| Phase 15 P01 | current session | 6 tasks | 6 files |
| Phase 18 P01 | current session | 5 tasks | 30 files |
| Phase 19 P01 | current session | 4 tasks | 10 files |

## Last Session

- **Completed:** Phase 16 implementation, deterministic verification, Chrome-generated PDF review artifact, final control visual UAT, and planning closeout
- **Stopped At:** Phase 21 context gathered
- **Resume File:** .planning/phases/21-jiaoan-jihua-1-1-typst-conversion/21-CONTEXT.md

## Close Notes

- v1.0 archived ROADMAP and REQUIREMENTS under `.planning/milestones/`.
- Pre-close artifact audit reported Phase 01 human UAT as `resolved` with 0 pending scenarios; no actionable UAT gap remains.
- No dedicated milestone audit file existed before close. Phase summaries and the requirements archive record the shipped v1.0 evidence; the next milestone should run `/gsd:audit-milestone` before `/gsd:complete-milestone`.
- v1.7 archived ROADMAP, REQUIREMENTS, and the passed milestone audit under `.planning/milestones/`.
- v1.7.1 records post-close debug fixes for uncertain-score calculation, score views/pagination, deterministic score-list artifacts, and fixed-template layout polish without reopening the v1.7 milestone.
- Pre-close artifact audit reported Phase 01/08/09 UAT records as `resolved` or `passed` with 0 pending scenarios; no actionable UAT gap remains.
- v1.6 Phase 10 visual UAT passed on 2026-06-11 and is recorded as shipped in `.planning/MILESTONES.md`.
- v1.8 starts from Phase 10 deferred scope rather than reopening completed playback/reveal work.
- v1.8 archived ROADMAP, REQUIREMENTS, and the passed milestone audit under `.planning/milestones/`.
- v1.9 archived ROADMAP, REQUIREMENTS, and the passed milestone audit under `.planning/milestones/`.

## Current Position

Phase: 20 / 21 ready for parallel planning
Plan: —
Status: Ready to execute
Last activity: 2026-06-14 -- Phase 21 planning complete

## Operator Next Steps

- `/gsd:discuss-phase 20 /Users/mrered/Developer/Presto-Agent-Skills`
- `/gsd:discuss-phase 21 /Users/mrered/Developer/Presto-Agent-Skills`

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260613-134 | school-presentation full_page_image 页面样式 | 2026-06-13 | eb27efb | [260613-134-school-presentation-full-page-image](./quick/260613-134-school-presentation-full-page-image/) |
