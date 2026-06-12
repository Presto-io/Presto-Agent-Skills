# Phase 19: Decomposition Guidance and Milestone Review - Context

**Gathered:** 2026-06-13
**Status:** Ready for planning
**Source:** `gsd discuss phase 19` equivalent, executed inline in Codex runtime

<domain>
## Phase Boundary

Phase 19 updates contributor guidance and review evidence for the v1.9 decomposition milestone. It covers SD-09 through SD-12 only: README/skills index/directory/compatibility guidance, before/after evidence, discoverability of Markdown intermediate and artifact contracts, and a scope guard confirming that v1.9 stayed structural.

This phase must not perform formal milestone audit, milestone archive/complete, new feature development, new output format work, public command renaming, runtime-specific wrapper generation, or broad style rewrites unrelated to the decomposition contract.

</domain>

<decisions>
## Implementation Decisions

### Guidance Surfaces

- **D-01:** Treat `README.md`, `skills/README.md`, `docs/directory-spec.md`, and `docs/compatibility-matrix.md` as the contributor-facing guidance set for Phase 19. They should consistently describe the lightweight-entry pattern: concise `SKILL.md`, long material in skill-local `references/`, callable helpers or internal modules in `scripts/`, and copyable output scaffolds in `templates/`.
- **D-02:** Guidance updates should be compact and reviewable. Do not turn README or compatibility guidance into another long reference manual; point contributors to the owning skill's references and templates instead.
- **D-03:** Compatibility guidance must keep OpenClaw and Hermes Agent as required runtime targets and continue to emphasize installation-time checks for frontmatter parsing, reference/template/script discovery, sandbox/write permissions, and unverified runtime behavior.

### Review Evidence

- **D-04:** Phase 19 should create or update a milestone review evidence document that records Phase 17 and Phase 18 before/after facts without running the formal milestone audit workflow.
- **D-05:** Evidence should include Phase 17 entry slimming facts: five affected `SKILL.md` entries, seven new skill-local reference files, skill entry line count reduced from 611 to 514, runtime adapter notes preserved, and no script internals edited in Phase 17.
- **D-06:** Evidence should include Phase 18 script decomposition facts: `school-presentation.sh`, `render_package.py`, and `gongwen.sh` split behind stable public command surfaces; new skill-local module/helper directories `school_presentation/`, `end_of_term/`, and `gongwen_lib/`; secondary jiaoan scripts intentionally left untouched; no global shared framework introduced.
- **D-07:** Evidence should record black-box contract checks from Phase 17 and Phase 18 summaries/verifications rather than inventing new acceptance criteria. The review should point to the exact verification files and commands already run.

### Artifact Contract Discoverability

- **D-08:** Confirm each affected skill still exposes its Markdown intermediate from the entry and from either `templates/` or a skill-local reference:
  - `skills/gongwen/SKILL.md` -> `templates/gongwen-full.md` and `references/format-and-rendering.md`.
  - `skills/jiaoan-shicao/SKILL.md` -> `templates/jiaoan-shicao-full.md` and `references/format-and-rendering.md`.
  - `skills/jiaoan-jihua/SKILL.md` -> `templates/jiaoan-jihua-full.md`, `references/calendar.json`, and `references/format-and-rendering.md`.
  - `skills/end-of-term-teaching-materials/SKILL.md` -> `templates/end-of-term-full.md`, `references/data-contract.md`, and `references/workflow-and-artifacts.md`.
  - `skills/school-presentation/SKILL.md` -> `templates/school-presentation-full.md`, `references/authoring-and-layout.md`, `references/playback-and-export.md`, and `references/verification-contract.md`.
- **D-09:** If Phase 19 finds a discoverability gap, fix the smallest relevant guidance or link. Do not change artifact filenames, manifest keys, render outputs, CLI flags, or skill behavior as part of the fix.

### Scope Guard

- **D-10:** Phase 19 should explicitly state that v1.9 did not add end-user skill capabilities, office-suite automation, hosted workflows, new runtime wrappers, or new output formats. Any such ideas remain future scope unless they are required to preserve the decomposition contract.
- **D-11:** The Phase 19 review should be a pre-audit evidence pass, not the formal `/gsd:audit-milestone` result. Do not mark v1.9 shipped, archive roadmap/requirements, or update milestone completion metadata from this phase.

### Claude's Discretion

- Exact filename for the Phase 19 review evidence document is left to the planner/executor, but it should live under `.planning/phases/19-decomposition-guidance-and-milestone-review/` and be easy for a later milestone audit to cite.
- The implementation may update wording in guidance files where necessary, provided the changes stay focused on decomposition expectations and review evidence.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope

- `.planning/ROADMAP.md` — Phase 19 goal, success criteria, dependency on Phase 18, and instruction not to treat Phase 18 execution as audit/closeout.
- `.planning/REQUIREMENTS.md` — SD-09 through SD-12, v1.9 out-of-scope table, and traceability.
- `.planning/STATE.md` — Current v1.9 position, Phase 18 complete status, and accumulated decisions about preserving public interfaces.
- `.planning/PROJECT.md` — Current milestone description, active requirements, out-of-scope boundaries, constraints, and key decisions for v1.9.
- `AGENTS.md` — Repository editing rules, language rule, directory sync obligations, and canonical skill/runtime adapter constraints.

### Dependency Evidence

- `.planning/phases/17-skill-entry-and-reference-decomposition/17-CONTEXT.md` — Phase 17 boundary and decisions for lightweight skill entries.
- `.planning/phases/17-skill-entry-and-reference-decomposition/17-01-SUMMARY.md` — Phase 17 before/after evidence, affected files, commits, and requirement coverage.
- `.planning/phases/17-skill-entry-and-reference-decomposition/17-VERIFICATION.md` — Phase 17 passed checks and scope guard.
- `.planning/phases/18-script-module-decomposition/18-CONTEXT.md` — Phase 18 boundary and decisions for script module decomposition.
- `.planning/phases/18-script-module-decomposition/18-01-SUMMARY.md` — Phase 18 split targets, commits, preserved contracts, and requirement coverage.
- `.planning/phases/18-script-module-decomposition/18-VERIFICATION.md` — Phase 18 passed black-box command regression and scope guard.

### Contributor Guidance Targets

- `README.md` — Project overview, add-new-skill workflow, and current skills list.
- `skills/README.md` — Skills index and expected skill directory layout.
- `docs/directory-spec.md` — Directory ownership contract for `SKILL.md`, `references/`, `scripts/`, and `templates/`.
- `docs/compatibility-matrix.md` — Required runtime guidance and progressive-disclosure expectations.
- `templates/skill/SKILL.md` — Canonical new-skill template that should model the lightweight-entry pattern.
- `docs/markdown-normalization-contract.md` — Shared Markdown intermediate contract for document and presentation workflows.

### Affected Skill Contract Surfaces

- `skills/gongwen/SKILL.md` and `skills/gongwen/references/format-and-rendering.md` — Gongwen Markdown intermediate and Typst/PDF artifact contract.
- `skills/jiaoan-shicao/SKILL.md` and `skills/jiaoan-shicao/references/format-and-rendering.md` — Practical lesson-plan Markdown intermediate and Typst artifact contract.
- `skills/jiaoan-jihua/SKILL.md` and `skills/jiaoan-jihua/references/format-and-rendering.md` — Teaching-schedule Markdown intermediate, calendar support, and Typst artifact contract.
- `skills/end-of-term-teaching-materials/SKILL.md` and `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md` — End-of-term Markdown intermediate, fixed-template package, workbook, deterministic tables, and evidence artifacts.
- `skills/school-presentation/SKILL.md`, `skills/school-presentation/references/authoring-and-layout.md`, `skills/school-presentation/references/playback-and-export.md`, and `skills/school-presentation/references/verification-contract.md` — Presentation logical-slide Markdown intermediate, offline HTML deck, playback/export, and verification contract.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- Phase 17 summaries/verifications already provide the entry-slimming evidence needed for SD-10 and SD-11.
- Phase 18 summaries/verifications already provide the script-split evidence needed for SD-10 and SD-12.
- Existing skill entries already link most Markdown intermediate templates and artifact references; Phase 19 should verify and tighten discoverability rather than redesign contracts.

### Established Patterns

- The repository uses one canonical `SKILL.md` as semantic source of truth, with runtime differences isolated in `Runtime Adapter Notes`.
- Long field lists, renderer notes, verification detail, and artifact lists belong in skill-local `references/`.
- Public shell command surfaces and common flags are compatibility contracts; black-box verification should run through those public commands.
- Markdown remains the reviewable intermediate before Typst, PDF, HTML, workbook, or deterministic table artifacts.

### Integration Points

- Guidance changes should stay synchronized across `README.md`, `skills/README.md`, `docs/directory-spec.md`, `docs/compatibility-matrix.md`, and `templates/skill/SKILL.md` where the same contributor expectation is stated.
- Review evidence should be placed in the Phase 19 planning directory so later `/gsd:audit-milestone` can cite it without treating this phase as the audit itself.

</code_context>

<specifics>
## Specific Ideas

- Use Phase 19 to make the review path obvious: a contributor or reviewer should be able to start from README or `skills/README.md`, find the affected skill entry, then find the Markdown intermediate template and artifact reference without reading a monolithic `SKILL.md`.
- The before/after evidence should be factual and compact: line counts, created module/reference directories, preserved command names, preserved intermediate filenames, and links to verification outputs.
- Avoid abnormal expansion: no new features, no new runtime wrappers, no new output formats, no broad style cleanup.

</specifics>

<deferred>
## Deferred Ideas

- Formal `/gsd:audit-milestone v1.9` and `/gsd:complete-milestone v1.9` remain later commands after Phase 19 is planned, executed, summarized, and verified.
- Automated linting for oversized skill entries, missing runtime adapter notes, misplaced long content, or scaffolding generation remains SD-FUTURE scope.
- Runtime-specific generated wrappers remain future scope unless a later milestone proves a supported runtime cannot consume canonical `SKILL.md` plus adapter notes.

</deferred>

---

*Phase: 19-Decomposition Guidance and Milestone Review*
*Context gathered: 2026-06-13*
