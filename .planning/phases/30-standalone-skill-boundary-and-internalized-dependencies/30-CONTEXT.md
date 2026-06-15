# Phase 30: Standalone Skill Boundary and Internalized Dependencies - Context

**Gathered:** 2026-06-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 30 delivers the standalone installation and dependency boundary for `teaching-design-package`. The phase must make the skill understandable and usable as one self-contained skill folder, while preserving the existing standalone `jiaoan-jihua` and `jiaoan-shicao` skills and their public command contracts.

This phase is not a general renderer cleanup and must not implement Phase 31's full teacher-facing rewrite or Phase 32's clean delivery-directory enforcement. However, Phase 30 decisions must not contradict those later locked milestone constraints.

</domain>

<decisions>
## Implementation Decisions

### Standalone Skill Boundary

- **D-01:** `teaching-design-package` must be installable and usable as a single skill. Downstream agents must not plan a workflow that requires users to separately install repo sibling skill directories such as `skills/jiaoan-jihua/` or `skills/jiaoan-shicao/`.
- **D-02:** Canonical guidance must describe `teaching-design-package` as the user-facing integrated skill, not as a thin wrapper that asks teachers or agents to mentally stitch together sibling skills.
- **D-03:** Runtime adapter notes for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent must all state the standalone boundary in runtime-appropriate terms: install/copy the `teaching-design-package` skill folder and verify its own `references/`, `templates/`, `scripts/`, and any vendored/internal resources are discoverable from that folder.

### Internalized Dependency Strategy

- **D-04:** Any needed `jiaoan-jihua` or `jiaoan-shicao` behavior must be vendored, internalized, or discovered from self-contained `teaching-design-package` package resources. Hard-coded repo sibling paths are not acceptable for the standalone install path.
- **D-05:** The existing repo-local sibling skills may still be used as source references during implementation and parity testing, but the accepted Phase 30 product must have a runtime path that works after installing only `teaching-design-package`.
- **D-06:** Planners should prefer skill-local resources under `skills/teaching-design-package/` for portable behavior: for example vendored templates, skill-local adapters/helpers, or explicit self-contained discovery metadata. If a dependency remains external, the plan must explain how a standalone install can discover it without assuming the original repository layout.
- **D-07:** Calendar/scheduling support must follow the same self-contained rule. Current code points at `skills/jiaoan-jihua/references/calendar.json`; Phase 30 planning must move or expose required calendar/default resources through `teaching-design-package` itself, or define a self-contained lookup fallback.

### Legacy Skill Preservation

- **D-08:** `jiaoan-jihua` and `jiaoan-shicao` standalone skills must remain in place. Do not delete, rename, replace, or change their public commands, accepted inputs, output contracts, or standalone install expectations in this phase.
- **D-09:** Parity verification may compare against legacy standalone skills in the repository, but that comparison is a regression gate, not a user-facing dependency requirement.
- **D-10:** If internalized behavior is copied or adapted from the legacy skills, the plan must include checks that the legacy public command surfaces still behave as before.

### Teacher UX and Script Boundary

- **D-11:** Treat the following as locked milestone decisions, not open questions: the teacher's primary UX is source materials -> clarification/organization -> one editable full Markdown document, named `teaching-design-package-full.md` or a course-specific `某某某课教学资料.md`.
- **D-12:** Scripts are not the teacher interaction surface. Scripts consume finalized Markdown for strict input/output validation and 1+1+3 delivery generation only.
- **D-13:** Phase 30 should update standalone guidance and dependency boundaries in a way that prepares Phase 31, but should avoid doing Phase 31's broader teacher-workflow rewrite unless the planner finds a small wording change is required to remove sibling-install instructions from Phase 30 scope.

### Output and Diagnostics Boundary

- **D-14:** The later default successful delivery surface is locked as exactly 1+1+3: one unified Markdown, one unified Typst, and three PDFs. Phase 30 should not introduce new public default artifacts that conflict with that contract.
- **D-15:** Internal handoff Markdown, split Typst, manifests, stderr logs, status sidecars, temporary state, and sibling-parity artifacts should be treated as hidden work/debug/failure diagnostics for later Phase 32 enforcement, not as public default delivery promises.

### Auto-Discussion Selections

- **D-16:** `[auto]` selected all meaningful Phase 30 gray areas: standalone install boundary, internalized/vendored jiaoan behavior, runtime adapter wording, legacy public contract preservation, and self-contained scheduling/resource discovery.
- **D-17:** `[auto]` did not ask the user new questions because the user explicitly supplied four locked corrections for this command. Those corrections are captured above as decisions, not unresolved prompts.

### Claude's Discretion

Implementation details remain for the planner/researcher: exact folder names for vendored resources, whether to share code through a skill-local library or shell wrappers, and the minimum regression test set. These choices are flexible only if they satisfy D-01 through D-15.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### GSD Phase Scope

- `.planning/ROADMAP.md` — Defines Phase 30 goal, dependencies, requirements, and success criteria.
- `.planning/REQUIREMENTS.md` — Defines TDPKG-01, TDPKG-02, TDPKG-03, and TDPKG-15 for Phase 30, plus the locked milestone-wide teacher UX and 1+1+3 constraints.
- `.planning/STATE.md` — Records v1.14 decisions, including standalone package UX, script boundary, and clean delivery constraints.
- `.planning/PROJECT.md` — Captures project-level constraints, runtime targets, and v1.14 discipline statements.
- `AGENTS.md` — Repository editing and skill authoring rules, including OpenClaw/Hermes coverage and canonical-vs-adapter boundaries.

### Teaching Design Package

- `skills/teaching-design-package/SKILL.md` — Current canonical entry; contains existing sibling-skill Inputs and runtime notes that Phase 30 must correct toward standalone install/use.
- `skills/teaching-design-package/references/format-and-orchestration.md` — Current detailed orchestration contract, module handoff semantics, scheduling evidence, split output status, and parity rules.
- `skills/teaching-design-package/templates/teaching-design-package-full.md` — Teacher-facing full-package Markdown baseline that must remain the human-editable source of truth.
- `skills/teaching-design-package/scripts/teaching-design-package.sh` — Current implementation; contains hard-coded repo sibling paths and generated internal artifacts that planning must account for.

### Legacy Skills and Shared Evidence

- `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md` — Existing teaching-plan handoff shape used for parity and possible vendoring/internalization reference.
- `skills/jiaoan-jihua/references/calendar.json` — Current calendar dependency that cannot remain reachable only through a repo sibling path for standalone package use.
- `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md` — Existing practical lesson-plan handoff shape used for parity and possible vendoring/internalization reference.
- `skills/jiaoan-shicao/references/calendar.json` — Existing lesson-plan calendar reference; planners should verify whether it is needed for self-contained package behavior.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `skills/teaching-design-package/templates/teaching-design-package-full.md`: already provides the unified Markdown baseline and should remain the package source-of-truth example.
- `skills/teaching-design-package/references/format-and-orchestration.md`: already records the module handoff and parity behavior; Phase 30 can revise this into a standalone dependency contract instead of inventing a separate spec.
- `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md` and `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md`: useful as reference material for vendored/internal handoff generation, while preserving legacy public skills.

### Established Patterns

- Canonical `SKILL.md` remains the semantic entry; long rules belong in `references/`, scripts in `scripts/`, templates in `templates/`.
- Runtime-specific details belong in Runtime Adapter Notes; canonical body should not contain one runtime's private syntax.
- v1.13 established that package rendering adapts around `teaching-design-package-full.md` rather than changing teacher-facing Markdown to satisfy parser internals.
- v1.13 parity verifies split package output against standalone jiaoan output from the same generated handoffs. Phase 30 should preserve parity as a regression check while removing it as an installation dependency.

### Integration Points

- Current `SKILL.md` Inputs list `skills/jiaoan-jihua/`, `skills/jiaoan-shicao/`, and `skills/end-of-term-teaching-materials/`, which conflicts with standalone install guidance for Phase 30 unless rewritten as internal/vendored/self-contained resources or optional repo-development references.
- Current script derives `REPO_ROOT` from `SKILL_DIR/../..` and uses repo sibling paths for `END_OF_TERM_SCRIPT`, `CALENDAR_JSON`, `jiaoan-jihua.sh`, `jiaoan-shicao.sh`, and sibling templates. Planning must remove or guard these assumptions for standalone use.
- Current script writes `jiaoan-jihua-full.md`, `jiaoan-shicao-full.md`, `teaching-design-package-manifest.json`, and split Typst/PDF artifacts into the output directory. Phase 30 need not enforce delivery cleanup, but should avoid making those internal paths part of standalone public UX.

</code_context>

<specifics>
## Specific Ideas

- The standalone install artifact should be conceptually copyable as `skills/teaching-design-package/` alone.
- Self-contained discovery can mean vendored resources or package-local discovery metadata, but not an implicit requirement that `../jiaoan-jihua` and `../jiaoan-shicao` exist.
- Keep old `jiaoan-jihua` and `jiaoan-shicao` commands exactly as legacy standalone entries; the integrated package is an additional unified UX, not a replacement.

</specifics>

<deferred>
## Deferred Ideas

- Phase 31 should do the full canonical teacher workflow rewrite: source materials, clarification, organization, one full Markdown, then render.
- Phase 32 should enforce the clean default 1+1+3 delivery directory and hidden diagnostics behavior.
- External registry packaging or publishing is deferred by `TDPKG-FUTURE-01`.

</deferred>

---

*Phase: 30-Standalone Skill Boundary and Internalized Dependencies*
*Context gathered: 2026-06-15*
