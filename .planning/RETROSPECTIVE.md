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

## Milestone: v1.9 - Skill Decomposition and Entry Slimming

**Shipped:** 2026-06-13
**Phases:** 3 | **Plans:** 3 | **Sessions:** 4+

### What Was Built

- Lightweight `SKILL.md` entries for current skills, with long operational detail moved into skill-local references.
- Skill-local script modules for the largest current command surfaces while preserving public flags, artifact names, manifest keys, and Markdown intermediates.
- Contributor guidance and pre-audit evidence for the decomposition pattern across README, skills index, directory spec, compatibility matrix, and the skill template.

### What Worked

- Treating `SKILL.md -> templates -> references -> scripts` as a lookup path kept the work focused on discoverability instead of feature expansion.
- Phase 17 and Phase 18 summaries provided enough before/after evidence for a strict milestone audit.
- Public-command regression checks gave confidence that the refactor reduced maintenance weight without changing user-facing behavior.

### What Was Inefficient

- Audit metadata needed normalization for Phase 17 requirements after the implementation had already passed verification.
- The native `audit-open` query and the quick-task workflow disagreed on quick summary filenames, so closeout needed a compatibility summary for a completed quick task.
- The automatic `milestone.complete` output needed manual date, statistics, ROADMAP, PROJECT, STATE, and archive wording fixes.

### Patterns Established

- Long-form skill detail belongs in `references/` and should be linked from the entry, not embedded in the default skill read.
- Script splits should stay skill-local until there is stable cross-skill duplication worth a shared framework.
- Milestone archives need manual review after SDK generation, especially for dates, task counts, and active/shipped wording.

### Key Lessons

1. Normalize requirement metadata before audit when a phase summary body and frontmatter can drift.
2. Keep compatibility wrappers small and explicit when workflow tooling has legacy naming assumptions.
3. Use phase summaries, verification files, and audit evidence as the source of truth for milestone statistics instead of trusting generated counts blindly.

### Cost Observations

- Model mix: balanced profile.
- Notable: Most work was refactor and documentation review, with verification centered on public command compatibility rather than new feature behavior.

---

## Milestone: v1.10 - Jiaoan Typst 1:1 Conversion

**Shipped:** 2026-06-13
**Phases:** 2 | **Plans:** 2 | **Sessions:** 4+

### What Was Built

- A skill-local `jiaoan-shicao` renderer for the v1.10 教案 Markdown fixture.
- A Bash-only `jiaoan-jihua` parser and official five-column Typst emitter for the v1.10 授课计划 fixture.
- Strict generated-output verification for both fixture pairs with clean `diff -u`, matching SHA-256, and anti-copy inspection.
- A passed milestone audit covering all 11 v1.10 requirements across Phase 20 and Phase 21.

### What Worked

- Splitting the two jiaoan skills into parallel phases kept ownership clear and avoided premature shared infrastructure.
- Requiring `--expected-typ` only after generation made target files useful as oracles without allowing copy-through behavior.
- Standalone phase verification files gave the final audit enough durable evidence to pass without reopening implementation.

### What Was Inefficient

- Phase 20 needed a small follow-up evidence closure because its first summary did not fully expose requirement completion metadata.
- The SDK milestone close generated a partial MILESTONES accomplishment list and stale active-state wording, so closeout still needed manual review.

### Patterns Established

- Fixture-specific 1:1 conversion can live inside the affected skill directory while the public command surface remains stable.
- For byte-for-byte renderer milestones, verification should include render-with-expected, independent diff, hash comparison, and source anti-copy inspection.
- Phase directories can remain in `.planning/phases/` as raw evidence when milestone-level archives already preserve ROADMAP, REQUIREMENTS, and AUDIT.

### Key Lessons

1. Put requirement completion metadata in phase summaries before audit so closeout does not need evidence repair.
2. Treat target fixtures as verification oracles only after renderer execution.
3. Review generated milestone archives manually before committing closeout.

### Cost Observations

- Model mix: balanced profile.
- Notable: The highest-value verification was deterministic text comparison, not visual/PDF acceptance.

---

## Milestone: v1.11 - Integrated Teaching Design Package

**Shipped:** 2026-06-14
**Phases:** 4 | **Plans:** 4 | **Sessions:** 4+

### What Was Built

- A shared package-level scheduling contract with deterministic calendar/hour fixture evidence.
- A portable `teaching-design-package` orchestration skill entry with package Markdown checkpoint, jiaoan handoff files, and split Typst/PDF status semantics.
- Optional end-of-term module orchestration that delegates module internals to `end-of-term-teaching-materials` while exposing manifest pointers.
- Regression verification for existing teaching skills, package manifest truthfulness, runtime adapter coverage, and documentation/index discoverability.

### What Worked

- Promoting proven `jiaoan-jihua` scheduling behavior into a documented contract kept the milestone grounded in existing code instead of inventing a broad shared API too early.
- Keeping the package skill as an orchestrator preserved the standalone public interfaces for `jiaoan-jihua`, `jiaoan-shicao`, and `end-of-term-teaching-materials`.
- Explicit manifest status made missing merged PDFs an honest non-ready state rather than a false milestone success.

### What Was Inefficient

- Phase 23 needed recovery closeout after implementation commits landed without the expected summary, verification, and review artifacts.
- SDK roadmap analysis could not infer phase details from the already curated ROADMAP shape, so milestone closeout needed manual phase/stat review.
- Generated closeout text needed manual date and state corrections before commit.

### Patterns Established

- Orchestration skills should keep module ownership clear and expose handoff/status evidence instead of reimplementing module internals.
- Package-level final readiness should require actual final artifact evidence, not only successful intermediate generation.
- Root `references/` can hold shared contracts when the rule is broader than any one skill directory.

### Key Lessons

1. Keep phase summaries and verification files committed before milestone audit to avoid recovery work during closeout.
2. Treat combined package outputs as status-driven artifacts with explicit failure reasons.
3. Preserve standalone skill behavior first, then add package orchestration around stable handoff files.

### Cost Observations

- Model mix: balanced profile.
- Notable: Most work was contract and orchestration design; the highest-risk verification was regression and manifest truthfulness rather than PDF rendering.

---

## Milestone: v1.12 - Teaching Design Package Post-Close Repair

**Shipped:** 2026-06-14
**Phases:** 2 | **Plans:** 2 | **Sessions:** 2+

### What Was Built

- Package scheduling evidence now backfills concrete `起止日期` values into generated practical lesson-plan Markdown before `jiaoan-shicao` rendering.
- `jiaoan-shicao` activity tables now use official-style `25.04cm` chapter-scoped Typst column widths.
- Direct `jiaoan-shicao` and integrated package regression paths produce Markdown, Typst, and PDF evidence for the repaired behavior.
- The v1.12 milestone audit passed with TDPR-01 through TDPR-07 covered and no open gaps.

### What Worked

- Treating v1.12 as a post-close repair milestone kept the scope tight and avoided replacing existing teaching skills.
- Local official-template snapshots gave the width repair a concrete oracle instead of relying on subjective layout tuning.
- Phase 27 re-verified the Phase 26 date backfill through the integrated package path, which caught cross-repair compatibility rather than only direct script behavior.

### What Was Inefficient

- The default-locale AWK task-count issue required `LC_ALL=C` in the regression path.
- A prior executor timed out after implementation commits, so Phase 27 needed continuation work to finish verification and summary metadata.
- `milestone.complete` archived the core files but still needed manual ROADMAP, PROJECT, STATE, MILESTONES, and retrospective cleanup.

### Patterns Established

- Post-close bugfix milestones can stay small when they preserve the shipped skill topology and focus on concrete regression evidence.
- Package handoff fixes should keep standalone jiaoan skill behavior stable and prove preservation through command smoke checks.
- Layout repairs should parse generated Typst artifacts for invariants that the user actually receives.

### Key Lessons

1. Keep local official-reference evidence close to the phase verification before claiming visual or layout alignment.
2. Use integrated package regression after direct skill fixes so earlier package repairs do not silently regress.
3. Continue manually reviewing SDK-generated closeout text until active/shipped wording is consistently reliable.

### Cost Observations

- Model mix: balanced profile.
- Notable: The highest-value checks were generated Markdown assertions, Typst width parsing, real PDF compilation, and milestone audit cross-reference.

---

## Milestone: v1.14 - teaching-design-package 单技能独立交付与 1+1+3 输出契约

**Shipped:** 2026-06-15
**Phases:** 3 | **Plans:** 3 | **Sessions:** 3+

### What Was Built

- A standalone `teaching-design-package` normal path that runs from a copied-only skill folder without sibling skill calls.
- A teacher-facing source-materials-to-full-Markdown workflow in the canonical skill entry.
- A clean public 1+1+3 delivery root: one Markdown, one Typst, and three PDFs.
- Hidden diagnostics, strict PDF success semantics, derived scheduling facts, and activity-hour mismatch validation.

### What Worked

- Correcting the package boundary before close kept legacy standalone skills external instead of turning them into hidden internals.
- Standalone-copy verification gave high confidence that the package can be installed and used by itself.
- Treating scripts as finalized-Markdown validators kept the teacher workflow readable while preserving strict delivery automation.

### What Was Inefficient

- The quick-task closeout query still reported `260615-0853-correct-v114-doc-boundary` as missing even though its files and STATE record mark it verified.
- The SDK milestone close generated archive files and base state, but ROADMAP, PROJECT, MILESTONES, STATE, and retrospective still needed manual closeout review.
- Earlier package history used legacy standalone parity evidence, so v1.14 needed explicit language to supersede that direction.

### Patterns Established

- A package skill that claims standalone installability should be tested from a copied-only skill folder.
- Public delivery directories should expose only teacher-facing final artifacts; model, status, logs, split Typst, and failure evidence belong in hidden diagnostics.
- Derived scheduling fields should be computed from body evidence and `first_teaching_day`, not owned by teacher-maintained YAML.

### Key Lessons

1. Keep package-owned boundaries explicit when an integrated workflow grows out of earlier standalone skills.
2. Verify clean public output and hidden diagnostic retention together; either one alone is not enough.
3. Continue manually reviewing closeout output until audit-open and milestone-complete agree on quick-task artifact status.

### Cost Observations

- Model mix: balanced profile.
- Notable: The highest-value checks were standalone-copy execution, exact root-file assertions, hidden diagnostic assertions, and failure-mode validation.

---

## Milestone: v1.15 - teaching-design-package 模块化渲染与旧格式回归

**Shipped:** 2026-06-15
**Phases:** 4 | **Plans:** 4 | **Sessions:** 4+

### What Was Built

- A package-owned module registry that derives hidden `teaching-plan` and `teaching-design` Markdown/Typst intermediates from the unified package Markdown.
- Formal package-owned renderers for 授课进度计划表 and 教学设计方案, with legacy format equivalence evidence and no runtime sibling-skill dependency.
- One scheduling model that owns calendar, hour totals, task/activity mapping, date ranges, and cross-module validation.
- Course-name-prefixed public `1 + 1 + N` delivery, registry-order PDF merge, hidden diagnostics, and standalone success/failure regression evidence.

### What Worked

- Keeping the unified Markdown as the only content source made module extraction, validation, and public delivery traceable.
- Migrating legacy formal rendering rules into package internals closed the previous gap between standalone jiaoan outputs and package delivery.
- Forced failure checks for missing PDFs, empty PDFs, merge failure, empty merge output, public leakage, and standalone negative behavior kept success semantics honest.

### What Was Inefficient

- The first v1.15 audit failed because Phase 33 verification lacked requirement-ID traceability metadata, requiring a follow-up audit pass.
- `STATE.md` still carried the old audit blocker after the passed audit, so complete closeout needed manual state correction.
- `milestone.complete` archived core files but did not fully update ROADMAP, PROJECT, MILESTONES, or retrospective without manual review.

### Patterns Established

- Package modules should expose final public PDFs while keeping module Markdown, module Typst, status, diagnostics, logs, and calendar evidence hidden.
- Legacy skills can serve as format oracles during migration without becoming runtime dependencies.
- Public-root cleanliness and hidden diagnostic retention should be tested together for all successful and failed package runs.

### Key Lessons

1. Put requirement IDs directly into verification artifacts before milestone audit, especially for large phase requirement groups.
2. Treat `STATE.md` as a closeout target whenever audit artifacts supersede older blocker text.
3. Keep module registry order as the single source for final package merge order.

### Cost Observations

- Model mix: balanced profile.
- Notable: The highest-value checks were fresh black-box package render, module PDF size/status assertions, negative failure cases, and standalone-copy regression.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | 3 | 3 | Established canonical-template-first documentation and deferred unused examples. |
| v1.7 | 3+ | 3 | Added fixed-template document package generation with strict review gates and audit-driven closure. |
| v1.8 | 6+ | 3 | Extended the school-presentation renderer through live markup, classroom structures, and one-click PDF export while preserving HTML-first delivery. |
| v1.9 | 4+ | 3 | Reduced skill entry and script weight through progressive-disclosure references, skill-local modules, and contributor guidance. |
| v1.10 | 4+ | 2 | Added strict skill-local jiaoan Markdown-to-Typst fixture conversion with byte-for-byte verification. |
| v1.11 | 4+ | 4 | Added integrated teaching-design package orchestration with scheduling evidence, optional end-of-term module pointers, and honest manifest readiness. |
| v1.12 | 2+ | 2 | Repaired post-close teaching-design regressions for package date backfill and official activity-table width alignment. |
| v1.14 | 3+ | 3 | Corrected `teaching-design-package` into a standalone teacher-first package with clean 1+1+3 delivery and hidden diagnostics. |
| v1.15 | 4+ | 4 | Converted `teaching-design-package` into a modular all-in-one renderer with migrated formal outputs and strict PDF merge semantics. |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.0 | Local Markdown and artifact checks | 9/9 v1 requirements shipped | 0 runtime dependencies added |
| v1.7 | Script verifier, Typst/PDF compile when available, table/workbook repeatability, milestone audit | 8/8 ETM requirements shipped | Reused standard shell/Python workflow |
| v1.8 | Script verifier, manifest checks, browser/manual UAT, PDF artifact sanity, milestone audit | 11/11 SP requirements shipped | Reused the existing shell/Python/HTML renderer path |
| v1.9 | Public command regression, syntax/compile checks, documentation discovery checks, milestone audit | 12/12 SD requirements shipped | No new runtime dependencies added |
| v1.10 | Skill render commands, strict diff, SHA-256, anti-copy source inspection, milestone audit | 11/11 jiaoan requirements shipped | No new runtime dependencies added |
| v1.11 | Scheduling fixture derivation, public command regression, manifest truthfulness checks, documentation/runtime coverage, milestone audit | 16/16 TDP requirements shipped | No new runtime dependencies added |
| v1.12 | Markdown handoff assertions, Typst width parsing, direct/package PDF compilation, public command smoke checks, milestone audit | 7/7 TDPR requirements shipped | No new runtime dependencies added |
| v1.14 | Standalone-copy execution, exact public root assertions, hidden diagnostics checks, derived scheduling/failure gates, milestone audit | 15/15 TDPKG requirements shipped | No new runtime dependencies added |
| v1.15 | Fresh package render, module PDF/status checks, forced failure semantics, public leakage scan, standalone-copy regression, milestone audit | 31/31 TDPKG requirements shipped | No new runtime dependencies added |

### Top Lessons (Verified Across Milestones)

1. Canonical source first, runtime notes second.
2. Keep optional artifacts out until they have a real user.
3. Preserve a reviewable Markdown checkpoint before final document exports.
4. Keep live presentation UI closeout tied to explicit visual UAT, not only code or state-file completion.
5. Review generated milestone archives manually before committing closeout.
6. Make package final-ready status depend on actual final artifacts and explicit manifest reasons.
7. Verify post-close repairs through both direct skill paths and integrated package paths.
8. Test standalone package claims from a copied-only skill folder before shipping.
9. Require verification artifacts to carry requirement IDs before running a closeout audit.
