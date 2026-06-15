# Phase 30: Standalone Skill Boundary and Internalized Dependencies - Context

**Gathered:** 2026-06-15
**Status:** Ready for corrected planning
**Source:** Replan after failed execute attempt was cancelled

<domain>
## Phase Boundary

Phase 30 corrects the standalone boundary for `teaching-design-package`. The integrated skill must become a self-contained package workflow with its own data model, Markdown normalization, validation, Typst generation, and PDF delivery path. It must not preserve the old architecture by copying old skill Markdown templates, old handoff names, or old skill-internal directory structure into the package.

This phase may update planning and implementation guidance for `teaching-design-package`, but it must not execute the phase during this command. Existing legacy standalone skills remain available outside the package as historical compatibility surfaces. They are not package internals, not package dependencies, and not the target architecture for the new integrated skill.

</domain>

<decisions>
## Implementation Decisions

### Hard Correction From User

- **D-01:** Do not copy old standalone skill Markdown templates into `teaching-design-package`.
- **D-02:** Do not create or require package-internal directories that mirror old standalone skill names or handoff layouts.
- **D-03:** Do not use old standalone handoff filenames, handoff thinking, or old split-template naming as the package implementation strategy.
- **D-04:** The final target is a true two-in-one integrated skill that replaces old user-facing workflows for package use; it must not keep old skills hidden inside the package.

### Standalone Package Architecture

- **D-05:** `teaching-design-package` must be installable and usable as a single skill folder.
- **D-06:** The normal path starts from unified source Markdown: either `teaching-design-package-full.md` or a course-specific teaching-materials Markdown with the same package contract.
- **D-07:** The script layer consumes finalized unified Markdown and derives a package-owned intermediate data model. The derived model is the internal source for teaching schedule, teaching design, Typst, PDF, and manifest/status evidence.
- **D-08:** Typst generation must be package-owned. The package may learn from legacy behavior as historical reference, but execution must not invoke old standalone skill scripts or require old standalone skill folders for the normal path.
- **D-09:** Calendar, scheduling defaults, hour validation, and derived dates must be package-local or explicitly configured as package resources. They must not be borrowed through sibling skill paths.

### Legacy Boundary

- **D-10:** Legacy standalone skills may remain in this repository for backward compatibility and comparison outside the package. Phase 30 must not delete, rename, or rewrite their public command contracts.
- **D-11:** Documentation may mention legacy standalone skills only as external historical compatibility surfaces. It must not name old handoff files or present them as package internals.
- **D-12:** Regression checks may confirm legacy surfaces are untouched, but the package's standalone-copy verification must succeed without copying or invoking those legacy skill folders.

### Delivery Boundary

- **D-13:** Phase 30 prepares the standalone implementation path but does not perform Phase 31's full teacher-facing wording rewrite or Phase 32's complete delivery-directory cleanup.
- **D-14:** The plan must still point toward the locked final delivery contract: one unified Markdown, one unified Typst, and three PDFs.
- **D-15:** Debug artifacts are allowed only as package-owned diagnostics. They must not use old handoff filenames or old skill directory names.

### Auto-Discussion Selections

- **D-16:** No new user question is needed. The user's correction is a locked constraint.
- **D-17:** Previous failed execution output is invalid and must not be incorporated into the corrected plan.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### GSD Phase Scope

- `.planning/ROADMAP.md` - Phase 30 goal, dependencies, requirements, and success criteria.
- `.planning/REQUIREMENTS.md` - TDPKG-01, TDPKG-02, TDPKG-03, and TDPKG-15 plus milestone-wide teacher UX and 1+1+3 constraints.
- `.planning/STATE.md` - v1.14 decisions and the corrected boundary after the cancelled failed execute attempt.
- `.planning/PROJECT.md` - Project-level constraints and supported runtimes.
- `AGENTS.md` - Repository editing and skill authoring rules, including OpenClaw and Hermes Agent coverage.

### Teaching Design Package

- `skills/teaching-design-package/SKILL.md` - Current canonical entry to be corrected toward a standalone package-owned workflow.
- `skills/teaching-design-package/references/format-and-orchestration.md` - Current detailed contract to revise away from old handoff architecture and toward package-owned data/render contracts.
- `skills/teaching-design-package/templates/teaching-design-package-full.md` - Unified Markdown baseline and the human-editable package source of truth.
- `skills/teaching-design-package/scripts/teaching-design-package.sh` - Current implementation that must be moved away from sibling-path and old handoff assumptions during execution.

### Legacy Compatibility Boundary

- Legacy standalone skill folders in this repository are external historical compatibility surfaces only.
- They may be inspected to understand prior output expectations, but Phase 30 execution must not copy their full Markdown templates, create mirrored package internals, or require them for standalone package verification.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- The unified package Markdown template already exists and should remain the source contract for package parsing.
- The package script already contains parsing and scheduling logic that can be redirected into a package-owned model rather than old handoff generation.
- Current references already describe orchestration details; execution should revise them into a standalone package contract instead of adding old-template vendor docs.

### Conflict To Remove

- Current package docs and scripts still expose old split-handoff concepts as public workflow details.
- Current script has repo-sibling assumptions for calendar and render delegation.
- A failed execute attempt tried to add package-internal old-template files; those files must remain deleted and must not be reintroduced.

</code_context>

<specifics>
## Specific Ideas

- The package-owned model can normalize course metadata, schedule rows, teaching-design activities, resource rows, validation facts, and output status from the unified Markdown.
- The package renderer can generate schedule and teaching-design Typst sections directly from that model, then derive the full Typst and three PDFs from package-local rendering commands.
- Standalone verification must copy only `skills/teaching-design-package/` and prove the unified Markdown/script boundary works without legacy folders.

</specifics>

<deferred>
## Deferred Ideas

- Phase 31: full teacher-facing workflow rewrite and clarification flow.
- Phase 32: final clean 1+1+3 output directory enforcement and hidden diagnostics layout.
- External registry packaging remains future work.

</deferred>

---

*Phase: 30-Standalone Skill Boundary and Internalized Dependencies*
*Context corrected: 2026-06-15*
