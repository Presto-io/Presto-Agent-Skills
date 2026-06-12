# Phase 18 Plan Check

**Checked:** 2026-06-13
**Status:** PASSED
**Checker:** `gsd plan phase 18` plan-check equivalent, executed inline in Codex runtime

## Scope Check

- Phase 18 maps to SD-05, SD-06, SD-07, and SD-08.
- The plan targets `school-presentation.sh`, `render_package.py`, and `gongwen.sh` as the primary large script entry points.
- Secondary scripts `jiaoan-shicao.sh` and `jiaoan-jihua.sh` are included only for a limited shared-helper audit.
- The plan does not implement Phase 19 contributor documentation review, milestone audit, milestone closeout, or before/after milestone report.
- The plan does not modify Phase 17 artifacts.

## Contract Check

- Public command names remain stable: `school-presentation.sh`, `end-of-term-teaching-materials.sh`, `render_package.py`, and `gongwen.sh` remain the invocation surfaces they are today.
- Common flags are explicitly protected: `--input`, `--html`, `--manifest`, `--max-size-mb`, `--workdir`, `--pdf`, `--abnormal-review`, `--typ`, `--expected-typ`, and `--output`.
- Output contracts are explicitly protected: Markdown intermediate filenames, generated HTML/Typst/PDF names, manifest keys, deterministic table/workbook artifacts, and verification manifests.
- Module boundaries are responsibility-based: CLI dispatch, IO/path guards, parsing, rendering, HTML/CSS/JS assets, artifact writing, PDF/bookmark handling, and verification/reporting.
- Gongwen remains Bash-only; no Python, Node, Pandoc, external Markdown converter, or runtime-specific private syntax is planned for the renderer.

## Requirement Coverage

| Requirement | Covered by plan | Evidence |
|-------------|-----------------|----------|
| SD-05 | Yes | Tasks 2, 3, and 4 split large entry points while preserving public commands and common flags. |
| SD-06 | Yes | Tasks define explicit module ownership boundaries for CLI, parsing, rendering, artifact writing, and verification/reporting. |
| SD-07 | Yes | Context, threat model, and tasks forbid runtime-specific private syntax in canonical skill bodies or script interfaces. |
| SD-08 | Yes | Task 5 permits shared behavior only for proven duplication or stable contracts and rejects a broad global framework. |

## Decision Coverage

| Decision | Covered |
|----------|---------|
| D-01 | Yes |
| D-02 | Yes |
| D-03 | Yes |
| D-04 | Yes |
| D-05 | Yes |
| D-06 | Yes |
| D-07 | Yes |
| D-08 | Yes |
| D-09 | Yes |
| D-10 | Yes |
| D-11 | Yes |
| D-12 | Yes |
| D-13 | Yes |
| D-14 | Yes |

## Risk Check

- **Risk:** Mechanical relocation changes public command behavior.
  **Mitigation:** Task 1 captures baseline public contracts and task 5 compares post-refactor behavior through public commands.
- **Risk:** `school-presentation.sh` loses offline single-file determinism after CSS/JS extraction.
  **Mitigation:** Task 2 requires embedded `<style>` and `<script>` output and rejects external HTTP/CDN references.
- **Risk:** End-of-term review gates regress during Python module extraction.
  **Mitigation:** Task 3 keeps `render_package.py` as the CLI shim and verifies review, repeatability, calculated scores, table artifacts, and workbook keys.
- **Risk:** Gongwen's Bash-only contract is weakened.
  **Mitigation:** Task 4 uses sourced Bash files only and explicitly forbids Python, Node, Pandoc, and external Markdown converters.
- **Risk:** Shared-helper extraction becomes a framework project.
  **Mitigation:** Task 5 limits sharing to proven duplication or stable contracts and allows leaving secondary scripts untouched.

## Structural Check

- `18-RESEARCH.md` exists and answers the planning research question.
- `18-PATTERNS.md` exists and records wrapper, package extraction, Bash-only renderer, and verification patterns.
- `18-01-PLAN.md` has frontmatter, objective, context, threat model, tasks, verification, success criteria, and must-haves.
- Every task includes `read_first`, concrete `action`, and command/source-based `acceptance_criteria`.
- The plan claims all Phase 18 requirements in frontmatter.

## Verdict

## VERIFICATION PASSED

Plan 18-01 is executable as a single sequential refactor plan. It covers SD-05 through SD-08 and preserves the required public command, flag, artifact, manifest, Markdown intermediate, and runtime-neutrality contracts.
