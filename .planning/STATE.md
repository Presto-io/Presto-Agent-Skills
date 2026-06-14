---
gsd_state_version: 1.0
milestone: v1.14
milestone_name: teaching-design-package 单技能独立交付与 1+1+3 输出契约
status: planning
last_updated: "2026-06-14T23:39:49.058Z"
last_activity: 2026-06-15 — Milestone v1.14 started
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# State: Presto Agent Skills

**Initialized:** 2026-05-30
**Current Phase:** 30
**Status:** v1.14 milestone planning

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-15 after v1.14 milestone initialization)

**Core value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.
**Current focus:** v1.14 is initialized: `teaching-design-package` must become a standalone teacher-facing unified skill with a clean 1+1+3 delivery contract and hidden/internal diagnostics boundary.

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

Start the first v1.14 workflow step when ready:

- `/gsd:discuss-phase 30`
- `/gsd:plan-phase 30`

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
- Milestone v1.10 archived: ROADMAP, REQUIREMENTS, and the passed milestone audit are preserved under `.planning/milestones/`; Phase 20 and Phase 21 evidence directories remain in `.planning/phases/`.
- Milestone v1.11 started: create a new integrated teaching-design package skill plan that preserves existing jiaoan and end-of-term skills while adding shared scheduling evidence, a teacher-reviewable Markdown intermediate, optional end-of-term module integration, split/combined PDF outputs, and regression/documentation gates.
- Phase 23 completed: `teaching-design-package` now has a portable skill entry, teacher-reviewable package Markdown checkpoint, jiaoan module handoff rules, split Typst/PDF status helper, fixture evidence, and six-runtime adapter coverage.
- Phase 24 completed: `teaching-design-package` now supports optional end-of-term module handoff, module-owned review gates, deterministic table/workbook pointers, `end-of-term-package.pdf` split status, and honest `teaching-design-package.pdf` combined-output status evidence.
- Phase 25 completed: public command regression, package manifest truthfulness, six-runtime adapter coverage, OpenClaw/Hermes practical notes, and documentation/index discoverability are verified with no gaps.
- Milestone v1.11 archived: ROADMAP, REQUIREMENTS, and the passed milestone audit are preserved under `.planning/milestones/`; no next milestone has been started.
- Milestone v1.12 started: post-close repair for two v1.11 teaching-design bugs. Phase 26 will backfill inferred `起止日期` values into `jiaoan-shicao-full.md`; Phase 27 will align `jiaoan-shicao` `教学活动设计` table widths with official-template evidence.
- Phase 26 completed: `teaching-design-package` now backfills concrete package scheduling evidence into generated `jiaoan-shicao-full.md`, preserves review-marker gating, and records Markdown, Typst, and PDF verification evidence.
- Phase 27 completed: `jiaoan-shicao` now computes `教学活动设计` activity-table widths by official-style chapter/pagebreak grouping, verifies `25.04cm` total width and narrow `课时分配`, and preserves the Phase 26 package date backfill through integrated package PDF verification.
- Milestone v1.13 started: use the committed `skills/teaching-design-package/templates/teaching-design-package-full.md` Markdown template as the baseline, keep its teacher-facing structure unchanged, and plan renderer work around one Markdown, one Typst, and three PDF outputs.
- Milestone v1.14 started: correct `teaching-design-package` so it is a standalone, teacher-facing unified skill with a final-render script boundary, clean 1+1+3 delivery outputs, hidden diagnostics, and derived scheduling validation.

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
- [Phase 20]: jiaoan-shicao v1.10 conversion stays fixture-scoped and skill-local. — Phase 20 generated the 教案 Typst fixture byte-for-byte from Markdown via `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`.
- [Phase 20]: The target Typst is used only for `--expected-typ` comparison, strict `diff -u`, and SHA-256 verification. — Anti-copy inspection only matched the comparison variable in the script.
- [Phase 21]: jiaoan-jihua conversion stays skill-local and uses target Typst only for generated-output verification. — Phase 21 generated `test/1.10/电气设备控制线路安装与调试授课计划.typ` byte-for-byte from Markdown via `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`.
- [Milestone v1.11]: Start a new orchestration-skill milestone instead of deleting original skills. — User requested integration of teaching plan, lesson plan, and optional end-of-term materials while keeping `jiaoan-jihua`, `jiaoan-shicao`, and `end-of-term-teaching-materials` available.
- [Milestone v1.11]: Treat scheduling inference as auditable shared package behavior. — Existing `jiaoan-jihua` code proves `calendar.json`, `first_teaching_day`, `daily_hours`, and per-row hours can derive week, weekday, and hour consumption; v1.11 must formalize the broader contract before reuse.
- [Milestone v1.11]: Keep the integrated package Markdown-first. — Teachers must review a persistent Markdown intermediate before Typst/PDF, workbook, or combined package artifacts are claimed final.
- [Phase 23]: The integrated package skill composes the existing jiaoan skills rather than replacing them. — Phase 23 added `skills/teaching-design-package/` with module-local handoff files and kept `jiaoan-jihua` and `jiaoan-shicao` public skill entries unchanged.
- [Phase 23]: Split Typst/PDF status is honest and bounded. — The helper can render `teaching-plan.typ` and `lesson-plans.typ`, while PDF manifest fields remain `not_run` unless explicit PDF compilation succeeds.
- [Phase 24]: Optional end-of-term support delegates module internals to `end-of-term-teaching-materials`. — The package manifest exposes pointers and status evidence but does not reimplement score calculation, tables, workbooks, or module review resolution.
- [Phase 24]: Combined package readiness requires actual `teaching-design-package.pdf` file evidence. — Split output success is preserved separately, and missing merge tooling or PDFs records `merge_unavailable` or `failed` instead of false readiness.
- [Phase 27]: Activity-table widths are chapter/pagebreak-scoped, not learning-task-scoped. — The official local snapshots define `activityTableTotalWidthCM = 25.04` and same-chapter shared `columns: (...)`; `{pagebreak}` starts a recalculation boundary.
- [Milestone v1.13]: The full-package Markdown reference is the baseline contract. — The user corrected scope so implementation must adapt render ingestion around `skills/teaching-design-package/templates/teaching-design-package-full.md`, not change that Markdown's teacher-facing format.
- [Milestone v1.13]: Three PDF outputs are acceptance criteria. — The combined PDF must merge the original授课进度计划 and教案 outputs; the plan and lesson PDFs must match standalone `jiaoan-jihua` and `jiaoan-shicao` outputs except timestamps.
- [Phase 28]: Renderer ingestion adapts around the committed teacher-facing package baseline instead of changing the template. — Baseline hash/diff evidence proves skills/teaching-design-package/templates/teaching-design-package-full.md stayed byte-identical.
- [Phase 28]: Derived scheduling facts live in generated handoffs, Typst comments, and manifest provenance, not package YAML. — Phase 28 keeps total_hours, school_year, semester, daily_hours, and output/validation knobs out of package frontmatter.
- [Phase 28]: Phase 29 PDF outputs remain not_run slots until real PDF generation and parity verification run. — Phase 28 creates Typst and provenance only; it does not claim PDF parity.
- [Phase 29]: Final package PDF generation is explicit via `render-package --pdf`; Typst-only rendering remains the default. — This prevents callers from confusing Typst generation with accepted PDF output.
- [Phase 29]: Combined package PDF is merged from accepted split PDFs in source order. — When `pdfunite` and `qpdf` are unavailable, installed PyMuPDF provides a real local merge fallback recorded as `python_fitz`.
- [Phase 29]: Standalone parity is proven against the same generated handoff Markdown. — Package split Typst/PDF outputs match standalone `jiaoan-jihua` and `jiaoan-shicao` renders from `jiaoan-jihua-full.md` and `jiaoan-shicao-full.md`.
- [Milestone v1.14]: `teaching-design-package` is the unified user experience, not a requirement to install or stitch together sibling repo skills. — User clarified that any needed `jiaoan-jihua` or `jiaoan-shicao` capability must be vendored/internalized or discoverable from self-contained package resources.
- [Milestone v1.14]: The teacher workflow is source materials -> clarification/organization -> one editable full Markdown -> strict delivery render. — Scripts consume finalized Markdown for validation and output generation only.
- [Milestone v1.14]: Default delivery is exactly 1+1+3. — Internal handoffs, manifests, logs, status files, split Typst, and sidecars must stay hidden/debug/failure-only and out of successful delivery directories.

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
| Phase 20 P01 | 8min | 4 tasks | 5 files |
| Phase 21 P01 | 16min | 4 tasks | 4 files |
| Phase 22 P01 | 45min | 5 tasks | 8 files |
| Phase 23 P01 | recovery closeout | 5 tasks | 10 files |
| Phase 26 P01 | 27min | 5 tasks | 2 files |
| Phase 27 P01 | 20min | 5 tasks | 5 files |
| Phase 28 P01 | 24min | 6 tasks | 5 files |
| Phase 29 P01 | 23min | 7 tasks | 5 files |

## Last Session

- **Completed:** Phase 29 PDF parity and standalone regression
- **Stopped At:** Completed 29-PLAN.md
- **Resume File:** None

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
- v1.10 archived ROADMAP, REQUIREMENTS, and the passed milestone audit under `.planning/milestones/`.
- v1.10.1 records the post-close `jiaoan-shicao` black-box layout fix for learning-resource and teaching-activity table wrapping without reopening the v1.10 milestone.
- v1.11 records local initialization research in `.planning/research/SUMMARY.md` and scopes the milestone to planning/phase execution for a new integrated package skill.
- v1.11 archived ROADMAP, REQUIREMENTS, and the passed milestone audit under `.planning/milestones/`; phase evidence remains in `.planning/phases/`.

## Current Position

Phase: 30 - Standalone Skill Boundary and Internalized Dependencies
Plan: Not started
Status: Ready for phase discussion or planning
Last activity: 2026-06-15 — Milestone v1.14 initialized

## Operator Next Steps

- Run `/gsd:discuss-phase 30` to gather implementation context for standalone packaging.
- Or run `/gsd:plan-phase 30` to plan directly.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260613-134 | school-presentation full_page_image 页面样式 | 2026-06-13 | eb27efb | [260613-134-school-presentation-full-page-image](./quick/260613-134-school-presentation-full-page-image/) |
