---
phase: 19
artifact: pre-audit-evidence
milestone: v1.9
requirements:
  - SD-09
  - SD-10
  - SD-11
  - SD-12
status: ready-for-formal-audit
created: 2026-06-13
---

# Phase 19 Pre-Audit Evidence: v1.9 Decomposition Guidance

This document is a pre-audit evidence pass for a later `/gsd:audit-milestone` run. It is not the formal milestone audit, is not a `/gsd:complete-milestone` result, and does not mark v1.9 shipped.

## Source Evidence

- `.planning/phases/17-skill-entry-and-reference-decomposition/17-01-SUMMARY.md`
- `.planning/phases/17-skill-entry-and-reference-decomposition/17-VERIFICATION.md`
- `.planning/phases/18-script-module-decomposition/18-01-SUMMARY.md`
- `.planning/phases/18-script-module-decomposition/18-VERIFICATION.md`
- `README.md`
- `skills/README.md`
- `docs/directory-spec.md`
- `docs/compatibility-matrix.md`
- `templates/skill/SKILL.md`

## Phase 17 Entry Slimming Evidence

Phase 17 moved long operational detail out of current skill entries while preserving each canonical `SKILL.md` as the semantic entry point.

Before/after facts from Phase 17:

- Five current `SKILL.md` entries were slimmed: `gongwen`, `jiaoan-shicao`, `jiaoan-jihua`, `end-of-term-teaching-materials`, and `school-presentation`.
- Seven skill-local reference files were created:
  - `skills/gongwen/references/format-and-rendering.md`
  - `skills/jiaoan-shicao/references/format-and-rendering.md`
  - `skills/jiaoan-jihua/references/format-and-rendering.md`
  - `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md`
  - `skills/school-presentation/references/authoring-and-layout.md`
  - `skills/school-presentation/references/playback-and-export.md`
  - `skills/school-presentation/references/verification-contract.md`
- Current skill entry line count changed from 611 lines to 514 lines.
- Runtime Adapter Notes, including OpenClaw and Hermes Agent coverage, remained visible in affected entries.
- Phase 17 did not edit script internals, public command names, flags, output filenames, manifest keys, or Markdown intermediate filenames.
- Phase 17 verification passed reference-link, runtime-adapter, entry-section, directory-guidance, shell syntax, and Python compile checks.

Relevant Phase 17 commits:

- `b4f54c6` created skill-local reference files.
- `cc8602c` slimmed current skill entries and linked references.
- `b8a745c` updated contributor guidance for the entry/reference/scripts/templates split.

## Phase 18 Script Split Evidence

Phase 18 split the largest script entry points behind stable public command surfaces.

Before/after facts from Phase 18:

- Primary split targets were:
  - `skills/school-presentation/scripts/school-presentation.sh`
  - `skills/end-of-term-teaching-materials/scripts/render_package.py`
  - `skills/gongwen/scripts/gongwen.sh`
- New skill-local module/helper directories were created:
  - `skills/school-presentation/scripts/school_presentation/`
  - `skills/end-of-term-teaching-materials/scripts/end_of_term/`
  - `skills/gongwen/scripts/gongwen_lib/`
- Stable public command surfaces were preserved:
  - `school-presentation.sh`
  - `end-of-term-teaching-materials.sh`
  - `render_package.py`
  - `gongwen.sh`
- Secondary `jiaoan-shicao.sh` and `jiaoan-jihua.sh` scripts were intentionally left untouched because shared extraction would broaden scope without a stable contract.
- No global shared script framework was introduced.
- No canonical `SKILL.md` files were edited in Phase 18.
- Phase 18 verification passed black-box public-command regression, syntax checks, Python compile checks, manifest-key checks, artifact-name checks, Markdown intermediate filename checks, offline HTML checks, table/workbook artifact checks, and runtime-neutral script search.

Relevant Phase 18 commits:

- `7ba995e` split `school-presentation.sh`.
- `148b4aa` split the end-of-term renderer.
- `d8dc43d` split `gongwen.sh`.

## Artifact Contract Discoverability

SD-11 requires affected skills to keep their Markdown intermediate and artifact contract discoverable after decomposition. The post-split lookup path is:

| Skill | Markdown intermediate | Discoverable contract |
|-------|-----------------------|-----------------------|
| `gongwen` | `skills/gongwen/templates/gongwen-full.md` | `skills/gongwen/SKILL.md`, `skills/gongwen/references/format-and-rendering.md` |
| `jiaoan-shicao` | `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md` | `skills/jiaoan-shicao/SKILL.md`, `skills/jiaoan-shicao/references/format-and-rendering.md` |
| `jiaoan-jihua` | `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md` | `skills/jiaoan-jihua/SKILL.md`, `skills/jiaoan-jihua/references/format-and-rendering.md`, `skills/jiaoan-jihua/references/calendar.json` |
| `end-of-term-teaching-materials` | `skills/end-of-term-teaching-materials/templates/end-of-term-full.md` | `skills/end-of-term-teaching-materials/SKILL.md`, `skills/end-of-term-teaching-materials/references/data-contract.md`, `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md` |
| `school-presentation` | `skills/school-presentation/templates/school-presentation-full.md` | `skills/school-presentation/SKILL.md`, `skills/school-presentation/references/authoring-and-layout.md`, `skills/school-presentation/references/playback-and-export.md`, `skills/school-presentation/references/verification-contract.md` |

Phase 19 also exposes this lookup path from `README.md` and `skills/README.md` so a reviewer does not need to read a monolithic skill entry to find the artifact contract.

## Guidance Updates

Phase 19 updated the contributor guidance set named by SD-09:

- `README.md` now documents the post-decomposition lookup path: entry -> templates -> references -> scripts.
- `skills/README.md` now states ownership for lightweight entries, progressive disclosure references, public helper commands/internal modules, templates, and the affected skill artifact contract map.
- `docs/directory-spec.md` now clarifies that large scripts may be split into skill-local modules by responsibility while preserving public commands, common flags, output filenames, manifest keys, and behavior contracts.
- `docs/compatibility-matrix.md` now makes support-file discovery an installation-time compatibility check for `references/`, `templates/`, and `scripts/`.
- `templates/skill/SKILL.md` now prompts new skills to link Markdown intermediates or artifact contracts, preserve progressive disclosure, and verify support-folder discovery for required runtimes.

These updates keep OpenClaw and Hermes Agent as required runtime targets.

## Scope Guard and Deferred Work

This evidence supports SD-12. v1.9 structure work did not add:

- no new end-user skill capability;
- no new output format;
- no generated runtime wrapper;
- no hosted workflow;
- no office-suite automation;
- no lint command;
- no scaffold generator;
- no public command rename;
- no common flag rename;
- no output filename rename;
- no manifest key rename.

Future linting, scaffolding, generated wrappers, hosted workflows, office-suite automation, and new output formats remain deferred unless a later requirement explicitly reopens them.

## Later Audit Notes

A later formal `/gsd:audit-milestone` should cite this file together with Phase 17 and Phase 18 verification files. The formal audit should still independently confirm the current working tree state, requirement statuses, and that v1.9 has not been marked shipped before `/gsd:complete-milestone`.
