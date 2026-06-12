---
phase: 18
status: completed
researched_at: 2026-06-13
requirements:
  - SD-05
  - SD-06
  - SD-07
  - SD-08
---

# Phase 18 Research: Script Module Decomposition

## Research Question

What does the executor need to know to plan Phase 18 well, while preserving public command names, common flags, output contracts, Markdown intermediates, and runtime neutrality?

## Inputs Read

- `AGENTS.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/18-script-module-decomposition/18-CONTEXT.md`
- `.planning/phases/17-skill-entry-and-reference-decomposition/17-CONTEXT.md`
- `.planning/phases/17-skill-entry-and-reference-decomposition/17-01-SUMMARY.md`
- `.planning/phases/17-skill-entry-and-reference-decomposition/17-VERIFICATION.md`
- `skills/school-presentation/scripts/school-presentation.sh`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`
- `skills/end-of-term-teaching-materials/scripts/render_package.py`
- `skills/gongwen/scripts/gongwen.sh`
- `skills/school-presentation/references/verification-contract.md`
- `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md`
- `skills/gongwen/references/format-and-rendering.md`

## Phase Boundary Findings

- Phase 18 covers only SD-05 through SD-08.
- Phase 17 explicitly did not edit script internals and verified existing script syntax.
- Phase 19 remains documentation, compatibility guidance, before/after evidence, milestone audit, and milestone closeout. Phase 18 may create narrow discoverability notes only when required by a changed script layout, but should not perform Phase 19's broader review.
- There are no project-local `.agents/skills` or `.claude/skills` directories to add extra planning constraints.

## Target Inventory

| Target | Lines | Public surface | Decomposition risk |
|--------|------:|----------------|--------------------|
| `skills/school-presentation/scripts/school-presentation.sh` | 4940 | `example`, `render`, `verify`, `bookmark-pdf`, `info`; `--input`, `--html`, `--manifest`, `--max-size-mb`, `--workdir`, `--pdf`, `--output` | Highest. Bash wraps a large Python heredoc, which also embeds offline HTML/CSS/JavaScript and verification logic. |
| `skills/end-of-term-teaching-materials/scripts/render_package.py` | 1971 | Internal Python helper invoked by stable shell wrapper; subcommands `example`, `validate`, `markdown`, `render`, `verify`, `manifest`, `info`, `version` | Medium. It is already Python with clear function clusters and an argparse boundary. |
| `skills/gongwen/scripts/gongwen.sh` | 1251 | `example`, `render`, `manifest`, `info`, `version`; `--input`, `--typ`, `--pdf`, `--expected-typ` | Medium-high. Bash-only rendering is a documented skill contract; extraction must stay Bash-based. |
| `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` | 462 | Secondary script entry point | Low. Only touch if exact shared Bash helper extraction is justified. |
| `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` | 447 | Secondary script entry point | Low. Only touch if exact shared Bash helper extraction is justified. |

## Contract Findings

### School Presentation

- `school-presentation.sh` must remain the public file users run.
- `render --input <md> --html <html> --manifest <json> --max-size-mb <mb>` must preserve generated HTML, manifest keys, size-cap behavior, and status lines such as `wrote <path>`.
- `verify --workdir <dir>` must continue to generate examples, repeat renders, compare stability, inspect HTML tokens, and write `verification-manifest.json`.
- The verification manifest must keep booleans such as `presenter_markup_verified`, `classroom_structure_verified`, `full_page_image_verified`, `print_review_verified`, `ratio_4x3_verified`, and `offline_single_file_verified`.
- Manifest runtime-state exclusions remain important: annotation state, markup palette state, pinned peek state, hover peek state, and print control runtime state must not leak into manifests.
- Offline single-file HTML is a hard contract; extracted CSS/JS support files must be embedded at render time or imported as local Python package data, not linked as external browser assets.

### End-of-Term Teaching Materials

- `end-of-term-teaching-materials.sh` is already a stable public wrapper and should remain unchanged except for the Python helper path if needed.
- The fixed workflow remains `structured data -> Markdown -> Typst/PDF + deterministic table artifacts`.
- `render_package.py` owns source validation, Markdown generation/parsing, Typst rendering, deterministic table artifacts, workbook writing, PDF compile, and verification.
- Output filenames are contract-bearing: `end-of-term-full.md`, `end-of-term-package.typ`, `end-of-term-package.pdf`, `manifest.json`, and the `tables/*` artifacts listed in the reference.
- Review gates for unresolved uncertain values such as `87?` must remain strict. Normal render must fail when `## 复核标记` is not exactly `无`; only `--abnormal-review` may produce inspection artifacts.

### Gongwen

- `gongwen.sh` is intentionally Bash-only. Do not convert the public implementation to Python, Node, Pandoc, or an external Markdown converter.
- `render --input <md> --typ <typ> --pdf <pdf> --expected-typ <fixture>` must remain black-box compatible.
- The script contains separable Bash clusters: common helpers, frontmatter parsing, inline/text escaping, Typst document head emission, Markdown body rendering, images, tables, signature placement, file copy helpers, and command dispatch.
- Any sourced helper files must be skill-local and loaded relative to `SCRIPT_DIR`, so runtime invocation still works from arbitrary current directories.

## Suggested Module Boundaries

### `school-presentation`

- Keep `skills/school-presentation/scripts/school-presentation.sh` as a thin Bash wrapper.
- Create a skill-local Python package under `skills/school-presentation/scripts/school_presentation/`.
- Recommended modules:
  - `cli.py`: argparse setup, subcommand dispatch, public status lines.
  - `io.py`: text read/write, asset resolution, data URI, path validation.
  - `markdown.py`: frontmatter, sections, logical slides, directive/block parsing.
  - `render.py`: page construction, manifest construction, high-level `render_deck`.
  - `html_assets.py`: CSS/JavaScript template strings and embedded playback/export assets.
  - `verify.py`: representative fixture generation, repeatability checks, HTML/manifest token checks.
  - `pdf.py`: bookmark/link injection for `bookmark-pdf`.
- The wrapper should call Python through the same environment knob, `SCHOOL_PRESENTATION_PYTHON`, and pass `SKILL_DIR` explicitly.

### `end-of-term-teaching-materials`

- Keep `end-of-term-teaching-materials.sh` as the public wrapper.
- Keep `render_package.py` as a stable Python CLI entry shim, because the wrapper already invokes that filename.
- Create `skills/end-of-term-teaching-materials/scripts/end_of_term/`.
- Recommended modules:
  - `cli.py`: argparse, command dispatch, `RenderError` handling.
  - `io.py`: text/json IO and stable JSON helpers.
  - `source_data.py`: source score validation, uncertain marker generation, review marker merging.
  - `markdown_contract.py`: Markdown generation, frontmatter parsing, section/table parsing, Markdown validation.
  - `typst_render.py`: Typst escaping, page helpers, fixed-template page generation.
  - `tables.py`: deterministic table rows, CSV/Markdown/XLSX writing, workbook logic.
  - `verify.py`: repeatability hashes, table/workbook/calculated-score verification.
- `render_package.py` should remain executable with `python3 .../render_package.py <command> --skill-dir ...`.

### `gongwen`

- Keep `skills/gongwen/scripts/gongwen.sh` as the public command and Bash dispatcher.
- Create skill-local sourced files under `skills/gongwen/scripts/gongwen_lib/`.
- Recommended files:
  - `common.sh`: `die`, `need_file`, `ensure_parent_dir`, trim/quote helpers, date helper.
  - `frontmatter.sh`: `parse_input`.
  - `inline.sh`: escaping, punctuation conversion, inline rendering.
  - `typst_head.sh`: `emit_template_head`, metadata emission.
  - `body.sh`: paragraphs, headings, code blocks, signature placement, body traversal.
  - `images.sh`: image and multi-image emitters.
  - `tables.sh`: table splitting, alignment, measurement, and emission.
  - `commands.sh`: `cmd_example`, `cmd_render`, `cmd_manifest`, `cmd_info`, `cmd_version`.
- Use `source "$SCRIPT_DIR/gongwen_lib/<file>.sh"` from `gongwen.sh`; avoid non-Bash runtime dependencies.

## Shared Helper Findings

- There are repeated Bash helper ideas across current skills, especially `die`, `need_file`, and parent-directory checks.
- The safe Phase 18 default is skill-local extraction first. A repository-global shell framework would be premature and would increase review scope.
- Shared behavior is acceptable only if the executor can prove exact duplication or a stable contract. Candidate scope is a very small `skills/_shared/scripts/bash-common.sh` or skill-local sourcing copied into secondary scripts, but only after reading `jiaoan-shicao.sh` and `jiaoan-jihua.sh`.
- If shared extraction would force broad edits to secondary scripts, leave secondary scripts untouched and document the reason in the execution summary later.

## Validation Architecture

Phase 18 verification should be black-box first:

1. Pre-change baseline:
   - Capture `--help`/usage text for public scripts.
   - Generate representative outputs for each primary target through public commands.
   - Capture manifest keys and artifact filenames before moving internals.
2. Structural checks:
   - `bash -n` on all touched shell scripts and sourced helper files.
   - `python3 -m py_compile` on all new Python modules and shims.
3. Public command regression:
   - Run school-presentation `example`, `render`, `verify`, and `bookmark-pdf` checks where fixtures exist.
   - Run end-of-term `example`, `markdown`, `validate`, `render`, `verify`, `manifest`, `info`, and `version` through the wrapper.
   - Run gongwen `example`, `render`, `manifest`, `info`, and `version`; include `--expected-typ` if a fixture exists.
4. Contract comparison:
   - Compare public usage text before/after for common command names and flags.
   - Compare generated manifest key sets before/after.
   - Confirm output filenames and default paths remain stable.
   - Confirm Markdown intermediates remain `school-presentation-full.md`, `end-of-term-full.md`, and `gongwen-full.md`.

## Planning Implications

- Use one sequential plan. The targets are large and compatibility-sensitive; parallel edits would increase conflict and review risk.
- Begin implementation with baseline capture, not code movement.
- Split `school-presentation.sh` first because it has the largest risk surface and the most embedded responsibility clusters.
- Split `render_package.py` second because it is the cleanest Python extraction and can reuse lessons from the presentation split.
- Split `gongwen.sh` third, preserving Bash-only semantics.
- End with a shared-helper audit and full public-command regression gate.

## Research Complete

The phase can be planned as one structural refactor plan covering SD-05, SD-06, SD-07, and SD-08.
