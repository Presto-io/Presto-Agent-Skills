# Phase 19 Research: Decomposition Guidance and Milestone Review

**Researched:** 2026-06-13
**Question:** What do I need to know to plan Phase 19 well?
**Scope:** SD-09, SD-10, SD-11, SD-12 only

## Research Summary

Phase 19 should be planned as a focused documentation-and-evidence phase. Phase 17 already slimmed current skill entries and moved long operational detail into skill-local `references/`; Phase 18 already split the largest script targets behind stable public command surfaces. Phase 19 now needs to make that implemented pattern discoverable for future contributors and produce pre-audit evidence that a later milestone audit can cite.

The plan should not perform formal milestone audit or closeout. It should not implement new skill behavior, output formats, runtime wrappers, scaffold generators, or lint tooling. Those are explicitly outside v1.9 unless required to preserve the decomposition contract.

## Evidence Inputs

### Phase 17 Entry Decomposition

Read:

- `.planning/phases/17-skill-entry-and-reference-decomposition/17-01-SUMMARY.md`
- `.planning/phases/17-skill-entry-and-reference-decomposition/17-VERIFICATION.md`

Relevant facts for planning:

- Five current `SKILL.md` entries were slimmed.
- Seven skill-local reference files were created:
  - `skills/gongwen/references/format-and-rendering.md`
  - `skills/jiaoan-shicao/references/format-and-rendering.md`
  - `skills/jiaoan-jihua/references/format-and-rendering.md`
  - `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md`
  - `skills/school-presentation/references/authoring-and-layout.md`
  - `skills/school-presentation/references/playback-and-export.md`
  - `skills/school-presentation/references/verification-contract.md`
- Current skill entry line count changed from 611 lines to 514 lines.
- Runtime adapter notes, including OpenClaw and Hermes Agent, were preserved.
- Phase 17 did not edit script internals.
- Verification passed with checks for reference links, runtime adapter visibility, entry sections, directory guidance, script syntax, and Python compile where relevant.

### Phase 18 Script Decomposition

Read:

- `.planning/phases/18-script-module-decomposition/18-01-SUMMARY.md`
- `.planning/phases/18-script-module-decomposition/18-VERIFICATION.md`

Relevant facts for planning:

- Primary split targets were `skills/school-presentation/scripts/school-presentation.sh`, `skills/end-of-term-teaching-materials/scripts/render_package.py`, and `skills/gongwen/scripts/gongwen.sh`.
- New skill-local module/helper directories were created:
  - `skills/school-presentation/scripts/school_presentation/`
  - `skills/end-of-term-teaching-materials/scripts/end_of_term/`
  - `skills/gongwen/scripts/gongwen_lib/`
- Public command surfaces stayed stable:
  - `school-presentation.sh`
  - `end-of-term-teaching-materials.sh`
  - `render_package.py`
  - `gongwen.sh`
- Secondary `jiaoan-shicao.sh` and `jiaoan-jihua.sh` scripts were intentionally left untouched because shared extraction would broaden scope without a stable contract.
- No global shared framework was introduced.
- No canonical `SKILL.md` files were edited in Phase 18.
- Black-box public-command regression passed, including help text, syntax checks, Python compile, render/verify commands, manifest keys, artifact names, Markdown intermediate filenames, offline HTML checks, table/workbook artifacts, and runtime-neutral script search.

## Guidance Surfaces

Phase 19 should update exactly the contributor guidance surfaces named in the context unless execution finds a small link/guidance gap that must be fixed to satisfy SD-11:

- `README.md`
- `skills/README.md`
- `docs/directory-spec.md`
- `docs/compatibility-matrix.md`
- `templates/skill/SKILL.md`

The current state already contains much of the lightweight-entry guidance, especially in `README.md`, `docs/directory-spec.md`, `docs/compatibility-matrix.md`, and `templates/skill/SKILL.md`. `skills/README.md` is the lightest surface and should likely receive the most compact discoverability guidance: what `SKILL.md`, `references/`, `scripts/`, and `templates/` mean, and how to find artifact contracts after decomposition.

Guidance should stay compact. README and compatibility docs should not become long manuals; they should point contributors to skill-local references and templates.

## Artifact Contract Discoverability

The affected skills already expose Markdown intermediates and artifact contracts from entries and support files. Execution should verify and tighten links only where needed.

Expected discoverability map:

| Skill | Markdown intermediate | Entry/template/reference path |
|-------|-----------------------|-------------------------------|
| `gongwen` | `gongwen-full.md` | `skills/gongwen/SKILL.md`, `skills/gongwen/templates/gongwen-full.md`, `skills/gongwen/references/format-and-rendering.md` |
| `jiaoan-shicao` | `jiaoan-shicao-full.md` | `skills/jiaoan-shicao/SKILL.md`, `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md`, `skills/jiaoan-shicao/references/format-and-rendering.md` |
| `jiaoan-jihua` | `jiaoan-jihua-full.md` | `skills/jiaoan-jihua/SKILL.md`, `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md`, `skills/jiaoan-jihua/references/calendar.json`, `skills/jiaoan-jihua/references/format-and-rendering.md` |
| `end-of-term-teaching-materials` | `end-of-term-full.md` | `skills/end-of-term-teaching-materials/SKILL.md`, `skills/end-of-term-teaching-materials/templates/end-of-term-full.md`, `skills/end-of-term-teaching-materials/references/data-contract.md`, `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md` |
| `school-presentation` | `school-presentation-full.md` | `skills/school-presentation/SKILL.md`, `skills/school-presentation/templates/school-presentation-full.md`, `skills/school-presentation/references/authoring-and-layout.md`, `skills/school-presentation/references/playback-and-export.md`, `skills/school-presentation/references/verification-contract.md` |

The execution plan should verify this map with `rg` and `test -f` checks. If a link is missing, the executor should make the smallest documentation-only fix. It must not rename artifact filenames, manifest keys, render outputs, CLI flags, or skill behavior.

## Pre-Audit Evidence Document

Phase 19 should create a phase-local evidence file, recommended filename:

- `.planning/phases/19-decomposition-guidance-and-milestone-review/19-MILESTONE-REVIEW-EVIDENCE.md`

This file should be a pre-audit evidence pass, not a formal milestone audit. It should cite Phase 17 and Phase 18 summaries/verifications, record before/after facts, list preserved public interfaces and artifact contracts, and include an explicit scope guard for SD-12.

Recommended sections:

- Source Evidence
- Phase 17 Entry Slimming Evidence
- Phase 18 Script Split Evidence
- Artifact Contract Discoverability
- Guidance Updates
- Scope Guard and Deferred Work
- Later Audit Notes

## Planning Risks

| Risk | Mitigation |
|------|------------|
| Phase 19 becomes a milestone audit or closeout. | Plan explicitly forbids `/gsd:audit-milestone`, `/gsd:complete-milestone`, milestone archiving, shipped metadata updates, `SUMMARY.md`, and `VERIFICATION.md` during this command. |
| Guidance updates become broad rewrites. | Limit docs to the decomposition pattern and discoverability links required by SD-09 and SD-11. |
| Evidence invents new acceptance criteria instead of citing prior verification. | Base evidence on Phase 17/18 SUMMARY and VERIFICATION facts and commands. |
| Artifact contracts drift while documenting them. | Use link and filename checks; do not alter behavior, filenames, manifest keys, CLI flags, or outputs. |
| Future tooling sneaks into this phase. | Keep linting, scaffolding, generated wrappers, and new runtime packages deferred to SD-FUTURE requirements. |

## Recommended Plan Shape

Use one sequential plan:

1. Update contributor guidance surfaces for the lightweight-entry and script-module pattern.
2. Verify and tighten artifact contract discoverability from entries to templates/references.
3. Create the Phase 19 pre-audit evidence document from Phase 17/18 facts.
4. Run documentation, link, scope, and requirement-coverage checks.

This shape covers SD-09 through SD-12 without overlapping implementation from Phase 17/18 or later milestone audit/closeout.

## RESEARCH COMPLETE
