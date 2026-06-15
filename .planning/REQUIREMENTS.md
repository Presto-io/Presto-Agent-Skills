# Requirements: v1.14 teaching-design-package 单技能独立交付与 1+1+3 输出契约

**Defined:** 2026-06-15
**Core Value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## Milestone Summary

Make `teaching-design-package` a true unified teaching-design package skill rather than a user-visible wrapper around sibling repo skills or copied legacy internals. The milestone corrects the v1.13 package line so teachers start from source materials, interactively clarify and organize them into one reviewable Markdown, and then render the finalized Markdown through `teaching-design-package`'s own validation and Typst/PDF delivery path.

The default delivery contract is 1+1+3:

- one unified Markdown: `teaching-design-package-full.md` or a course-specific name such as `某某某课教学资料.md`
- one unified Typst artifact
- three PDFs: full package PDF, teaching-plan PDF, and teaching-design/lesson-plan PDF

## Gate Record

- **Validation gate:** v1.13 is shipped and archived; current state frontmatter was switched to v1.14 via `gsd-sdk query state.milestone-switch`.
- **Questioning gate:** The user supplied the milestone name, target behavior, and seven mandatory correction constraints directly; no additional scope prompt is required.
- **Research gate:** External research is skipped. The scope is an internal contract and workflow correction for existing repository skills.
- **Requirements gate:** This command initializes the milestone only and must not implement code or modify `skills/teaching-design-package`, legacy standalone skill files, or existing dirty skill files.
- **Correction gate:** Current and future v1.14 work must not copy old standalone Markdown templates, keep old split handoff files inside the package, or treat legacy standalone skills as package internals, internal resources, parity baselines, or implementation direction.
- **Roadmap gate:** Phase numbering continues from the previous milestone, so this roadmap starts at Phase 30.

## v1.14 Requirements

### Standalone Skill Packaging

- [ ] **TDPKG-01**: `teaching-design-package` can be installed and used as a single skill without requiring users to install sibling repository skill directories.
- [ ] **TDPKG-02**: Required package capability is implemented through `teaching-design-package`'s own unified data model, Markdown contract, validation, and Typst/PDF rendering path; old standalone Markdown templates, old split Markdown layouts, and old handoff thinking are not copied into the package.
- [ ] **TDPKG-03**: Runtime adapter notes for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent explain the standalone install/use boundary without relying on repo-local sibling paths.

### Teacher Markdown Workflow

- [ ] **TDPKG-04**: The canonical `SKILL.md` presents the main workflow as a teacher interaction: ingest many source materials, ask or clarify missing facts, organize content, and produce one reviewable full-package Markdown.
- [ ] **TDPKG-05**: The workflow treats `teaching-design-package-full.md` or a course-specific `某某某课教学资料.md` as the human-editable source of truth before rendering.
- [ ] **TDPKG-06**: The skill makes clear that the script layer is not the teacher's interactive organizing entry; scripts only consume finalized Markdown for strict validation and delivery generation.

### Delivery Artifact Contract

- [ ] **TDPKG-07**: The default successful output directory contains exactly the 1+1+3 deliverables: unified Markdown, unified Typst, full package PDF, teaching-plan PDF, and teaching-design/lesson-plan PDF.
- [ ] **TDPKG-08**: Default output directories do not contain copied legacy Markdown, split Typst files, manifests, stderr logs, status sidecars, or other internal implementation artifacts.
- [ ] **TDPKG-09**: Package-owned diagnostics, manifests, stderr logs, state files, split render intermediates, and temporary files are written only to hidden work directories, temporary directories, debug mode locations, or explicit failure diagnostics.

### Scheduling and Validation Contract

- [ ] **TDPKG-10**: Total course hours are calculated from teaching-plan or activity data and are not accepted as a manually authoritative YAML field.
- [ ] **TDPKG-11**: Teaching-plan hours and lesson-plan activity hours are mutually verified; mismatches fail validation or produce a non-final review-needed status.
- [ ] **TDPKG-12**: `first_teaching_day` can infer `school_year` and `semester` without requiring teachers to hand-maintain those fields.
- [ ] **TDPKG-13**: Start and end dates are inferred from real teaching days, parsed hours, holidays/makeup days where available, and documented default calendar behavior.

### Legacy Skill Preservation

- [ ] **TDPKG-14**: The user-facing package workflow does not regress into asking users to run or mentally stitch together old standalone skills, and does not hide old skill structure inside the package.
- [ ] **TDPKG-15**: Existing legacy standalone skill entries, public commands, accepted inputs, and output contracts remain preserved as external compatibility surfaces unless a later explicit requirement changes them; they are not package internals or v1.14 acceptance baselines.

## Future Requirements

Deferred to a later milestone unless explicitly requested:

- **TDPKG-FUTURE-01**: Package and publish `teaching-design-package` to an external skill registry or installer outside this repository.
- **TDPKG-FUTURE-02**: Add OCR or arbitrary binary document extraction for raw source materials.
- **TDPKG-FUTURE-03**: Add hosted review, multi-user approval, or cloud synchronization around the teacher Markdown.
- **TDPKG-FUTURE-04**: Redesign legacy standalone public interfaces.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Implementing code during milestone initialization | The user requested only the `gsd-new-milestone` workflow command. |
| Modifying `skills/teaching-design-package` scripts during initialization | Implementation belongs to later phase plan/execute commands. |
| Modifying current dirty legacy standalone skill files | The user explicitly asked to avoid staging, committing, or changing those files. |
| Requiring sibling skill installation for package use | This is the primary bug this milestone is meant to correct. |
| Polluting default delivery directories with internal artifacts | The user requires a clean 1+1+3 default output contract. |
| Deleting legacy standalone teaching skills | The unified package is the new/current package UX, but legacy standalone entries remain preserved outside the package. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| TDPKG-01 | Phase 30 | Pending |
| TDPKG-02 | Phase 30 | Pending |
| TDPKG-03 | Phase 30 | Pending |
| TDPKG-04 | Phase 31 | Pending |
| TDPKG-05 | Phase 31 | Pending |
| TDPKG-06 | Phase 31 | Pending |
| TDPKG-07 | Phase 32 | Pending |
| TDPKG-08 | Phase 32 | Pending |
| TDPKG-09 | Phase 32 | Pending |
| TDPKG-10 | Phase 32 | Pending |
| TDPKG-11 | Phase 32 | Pending |
| TDPKG-12 | Phase 32 | Pending |
| TDPKG-13 | Phase 32 | Pending |
| TDPKG-14 | Phase 31 | Pending |
| TDPKG-15 | Phase 30 | Pending |

**Coverage:**
- v1.14 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0

---
*Requirements defined: 2026-06-15*
*Last updated: 2026-06-15 after v1.14 milestone initialization*
