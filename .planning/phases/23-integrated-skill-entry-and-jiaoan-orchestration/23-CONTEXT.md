# Phase 23: Integrated Skill Entry and Jiaoan Orchestration - Context

**Gathered:** 2026-06-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 23 defines the implementation direction for the integrated `teaching-design-package` skill entry and the orchestration of the existing `jiaoan-jihua` and `jiaoan-shicao` skills. It covers the new skill's canonical entry shape, the persistent teacher-reviewable Markdown intermediate, composition of teaching-plan and lesson-plan material, split teaching-plan/lesson-plan Typst/PDF output planning, and runtime adapter coverage for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.

This phase must not delete, rename, or replace `skills/jiaoan-jihua` or `skills/jiaoan-shicao`. It must consume the Phase 22 scheduling contract rather than re-inventing scheduling behavior. Optional `end-of-term-teaching-materials` integration, default combined package output behavior, and full regression/documentation gates remain Phase 24 and Phase 25 work unless a small placeholder is needed to preserve the Phase 23 interface.

**Auto-mode note:** The user authorized `/gsd:discuss-phase 23 --auto` and explicitly requested no large-direction questions. All gray areas below were auto-selected and resolved conservatively from roadmap, requirement, Phase 22, and existing skill evidence.

</domain>

<decisions>
## Implementation Decisions

### New Skill Entry and Ownership

- **D-01:** Use `skills/teaching-design-package/` as the preferred new skill directory and `teaching-design-package` as the trigger/name. This follows TDP-05 and the repository's kebab-case skill naming pattern unless later implementation research finds a concrete conflict.
- **D-02:** Create a concise canonical `skills/teaching-design-package/SKILL.md` that describes orchestration behavior, inputs, outputs, safety boundaries, verification, and runtime adapter notes. Long package format rules should live in `skills/teaching-design-package/references/`, scripts in `skills/teaching-design-package/scripts/`, and output templates in `skills/teaching-design-package/templates/`.
- **D-03:** Treat the new skill as an orchestrator over stable contracts, not as a physical merge of existing skill directories. `jiaoan-jihua` remains the teaching-plan skill; `jiaoan-shicao` remains the practical lesson-plan skill.
- **D-04:** Do not change existing public commands, flags, output paths, fixture comparison behavior, or runtime adapter notes in `skills/jiaoan-jihua` and `skills/jiaoan-shicao` unless a minimal documentation cross-reference is required for discoverability.

### Markdown Intermediate Contract

- **D-05:** Define a persistent package-level Markdown intermediate, preferably `teaching-design-package-full.md`, before any Typst/PDF generation. It should be teacher-reviewable and remain the semantic checkpoint for the integrated package.
- **D-06:** The package Markdown should include at least these top-level sections: package/course metadata, scheduling inputs/evidence, teaching-plan section mapped to `jiaoan-jihua`, lesson-plan section mapped to `jiaoan-shicao`, output selection/status, and `## 复核标记`.
- **D-07:** Scheduling evidence from `references/scheduling-contract.md` must appear in the package intermediate in teacher-readable form and remain traceable to structured item sources such as task/stage/row or lesson-fragment pointers.
- **D-08:** Review markers must block final readiness. Missing, uncertain, conflicting, or exhausted schedule and content inputs should remain visible near the affected item and be summarized under `## 复核标记`; downstream render/export must not silently drop them.
- **D-09:** Keep package Markdown as the handoff point even when source material is already close to one of the existing jiaoan formats. One-step source-to-PDF generation remains out of scope.

### Jiaoan Composition Model

- **D-10:** Compose the existing skills by generating or extracting module-local Markdown intermediates compatible with `jiaoan-jihua-full.md` and `jiaoan-shicao-full.md`, then invoking or referencing their existing render paths. The package skill should not duplicate their full format manuals inside its entry file.
- **D-11:** Use Phase 22's source-order scheduling contract as the shared schedule layer. The package may map teaching-plan rows and lesson-plan fragments into that ordered item model, but should not expose the old `jiaoan-jihua.sh` parser as the package API.
- **D-12:** For `jiaoan-jihua`, preserve the known frontmatter/body contract: course metadata, `first_teaching_day`, optional `daily_hours`, ordered `##` tasks, `###` stages, and trailing integer hour markers.
- **D-13:** For `jiaoan-shicao`, preserve the three-part structure: `学习任务分析`, `教学活动设计`, and `学业评价`, with incomplete fields left blank or marked for review rather than invented.
- **D-14:** Where the same course metadata appears in both modules, the package intermediate should carry one normalized package-level source of truth and allow module-specific overrides only when needed and explicit.

### Typst/PDF Output Planning

- **D-15:** Plan split teaching-plan and lesson-plan outputs first: `teaching-plan.typ`/`teaching-plan.pdf` for `jiaoan-jihua` content and `lesson-plans.typ`/`lesson-plans.pdf` for `jiaoan-shicao` content where local tooling supports PDF compilation.
- **D-16:** Phase 23 may define manifest/status fields for split outputs but should leave default combined `teaching-design-package.pdf` and optional `end-of-term-package.pdf` behavior to Phase 24.
- **D-17:** PDF compilation should be explicit and verifiable. Existing jiaoan render scripts generate Typst; they do not compile PDF internally, so the new package plan must not claim PDF success unless the PDF command has actually run and produced evidence.
- **D-18:** If a renderer or compiler is unavailable, the package should record partial Typst/status evidence instead of claiming completed PDFs.

### Runtime Adapter Coverage

- **D-19:** The new skill's Runtime Adapter Notes must represent Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent from the first implementation slice.
- **D-20:** Canonical workflow text should stay portable. Runtime-specific behavior such as tool names, allowlists, install paths, shell execution cautions, and skill discovery differences belongs in adapter notes.
- **D-21:** OpenClaw and Hermes Agent must explicitly mention skill-folder discovery, reference/script availability, shell-script execution permissions, and support resources such as calendar data.
- **D-22:** Verification should include a lightweight adapter-coverage check, for example grepping the new `SKILL.md` for all six runtime names and checking that canonical sections avoid runtime-private syntax.

### Assumptions and Open Points for Planning

- **D-23:** Assume the new skill is implemented in Phase 23 as a minimal viable orchestration entry plus format/template/script plan sufficient to satisfy TDP-05 through TDP-09, not as the full optional end-of-term package.
- **D-24:** Assume no external web research is required for Phase 23; local repository artifacts provide the relevant contracts and patterns.
- **D-25:** Planner should decide the exact internal filenames for package reference/template/script files, but keep them discoverable from `SKILL.md` and consistent with existing skill layout.

### Claude's Discretion

- Use conservative file names and artifact shapes that mirror existing skills. Prefer concise entry text, a long `references/format-and-orchestration.md` or similarly named reference, a `templates/teaching-design-package-full.md` checkpoint, and only the smallest scripts needed to prove orchestration in this phase.
- If implementation risk is high, prioritize stable Markdown intermediate and manifest/status evidence over ambitious PDF merging.
- If a field cannot be mapped cleanly between teaching-plan and lesson-plan structures, mark it for teacher review instead of inventing or dropping it.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Requirements

- `.planning/ROADMAP.md` — Defines Phase 23 as the integrated skill entry and jiaoan orchestration slice for TDP-05 through TDP-09.
- `.planning/REQUIREMENTS.md` — Locks TDP-05 through TDP-09 and records Phase 24/25 boundaries.
- `.planning/PROJECT.md` — Captures v1.11 project-level decisions: new orchestration skill, Markdown-first package, preserved original skills, and runtime portability.
- `.planning/STATE.md` — Records current v1.11 status, accumulated decisions, and supported runtime targets.

### Phase 22 Scheduling Evidence

- `.planning/phases/22-scheduling-contract-and-fixture/22-CONTEXT.md` — Prior decisions D-01 through D-12 that Phase 23 should carry forward.
- `.planning/phases/22-scheduling-contract-and-fixture/22-SUMMARY.md` — Completed Phase 22 artifact list and verification summary.
- `.planning/phases/22-scheduling-contract-and-fixture/22-VERIFICATION.md` — Passed traceability for TDP-01 through TDP-04.
- `references/scheduling-contract.md` — Package-level scheduling contract that Phase 23 must consume.
- `test/1.11/scheduling-contract/expected-schedule.md` — Teacher-readable scheduling evidence pattern with `## 调度证据` and `## 复核标记`.
- `test/1.11/scheduling-contract/expected-schedule.json` — Machine-readable fixture evidence pattern for scheduling traceability.
- `scripts/derive-scheduling-fixture.py` — Local verifier demonstrating source-order calendar/hour derivation without reading Typst targets.

### Existing Jiaoan Skills

- `skills/jiaoan-jihua/SKILL.md` — Existing teaching-plan skill entry, public script usage, outputs, verification, safety, and adapter notes.
- `skills/jiaoan-jihua/references/format-and-rendering.md` — Teaching-plan Markdown, scheduling, renderer, and verification contract.
- `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md` — Existing teaching-plan Markdown intermediate template.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` — Existing public command surface and current render implementation.
- `skills/jiaoan-jihua/references/calendar.json` — Existing calendar support resource.
- `skills/jiaoan-shicao/SKILL.md` — Existing practical lesson-plan skill entry, public script usage, outputs, verification, safety, and adapter notes.
- `skills/jiaoan-shicao/references/format-and-rendering.md` — Practical lesson-plan Markdown, renderer, and verification contract.
- `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md` — Existing practical lesson-plan Markdown intermediate template.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` — Existing public command surface and current render implementation.
- `skills/jiaoan-shicao/references/calendar.json` — Existing calendar support resource and copy target.

### Repository Conventions

- `AGENTS.md` — Repository language, editing, skill authoring, runtime compatibility, and GSD workflow rules.
- `README.md` — Contributor-facing skill repository overview and discoverability index.
- `docs/directory-spec.md` — Directory placement rules for skills, references, scripts, templates, and test fixtures.
- `docs/markdown-normalization-contract.md` — Shared Markdown-first document workflow contract.
- `templates/skill/SKILL.md` — Canonical skill entry template and runtime adapter note pattern.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`: Existing public render command for `jiaoan-jihua-full.md` to Typst; also evidence for source-order hour consumption.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`: Existing public render command for `jiaoan-shicao-full.md` to Typst and optional calendar resource copy.
- `references/scheduling-contract.md`: Shared package-level scheduling contract created in Phase 22; Phase 23 should consume it instead of defining a parallel schedule model.
- `test/1.11/scheduling-contract/expected-schedule.md`: Ready pattern for teacher-readable schedule evidence inside the package intermediate.
- Existing `templates/*-full.md` files: Patterns for module-level reviewable Markdown checkpoints.

### Established Patterns

- Skills keep `SKILL.md` concise; long authoring/rendering rules belong in `references/`.
- Document workflows normalize to persistent Markdown before rendering to Typst/PDF or other final artifacts.
- Existing scripts preserve public command surfaces and use target Typst only as post-generation verification oracles.
- Unknown, missing, or uncertain teaching data is preserved as a review marker rather than silently guessed.
- Runtime adapter coverage is embedded in the canonical skill entry but runtime-private syntax is not placed in the canonical workflow body.

### Integration Points

- The new `skills/teaching-design-package/SKILL.md` should link to the existing jiaoan skills and the Phase 22 scheduling contract.
- The package intermediate should be able to emit or reference module-local intermediates compatible with `jiaoan-jihua` and `jiaoan-shicao`.
- Documentation discoverability likely requires README and directory-spec/index updates when the new skill is implemented.
- Phase 24 can attach optional end-of-term and combined-output behavior to the package manifest/status fields defined here.

</code_context>

<specifics>
## Specific Ideas

- Prefer `teaching-design-package-full.md` as the package Markdown checkpoint name because it matches existing `*-full.md` intermediate naming while clearly identifying the integrated package.
- Keep Chinese teacher-facing headings in the package intermediate: `## 调度证据`, `## 授课计划`, `## 实操教案`, `## 输出清单`, and `## 复核标记`.
- Use split output names that are easy to inspect: `teaching-plan.pdf` and `lesson-plans.pdf`; reserve `teaching-design-package.pdf` for Phase 24 combined output behavior.
- Keep the package skill honest about PDF status: Typst generation evidence is not the same as PDF generation evidence.

</specifics>

<deferred>
## Deferred Ideas

- Optional `end-of-term-teaching-materials` integration is Phase 24.
- `end-of-term-package.pdf`, workbook/table artifact discovery, package manifest rules for that module, and review gates are Phase 24.
- Default combined `teaching-design-package.pdf` behavior and failure semantics for merged output are Phase 24.
- Full regression verification across existing public command surfaces, documentation indexes, adapter coverage, and failure/manifest behavior is Phase 25.
- Deleting, renaming, or physically merging original jiaoan skill directories remains out of scope and future-only unless explicitly requested.

</deferred>

---

*Phase: 23-Integrated Skill Entry and Jiaoan Orchestration*
*Context gathered: 2026-06-14*
