---
phase: 18
plan: 01
subsystem: script-module-decomposition
tags:
  - refactor
  - scripts
  - compatibility
key-files:
  created:
    - skills/school-presentation/scripts/school_presentation/
    - skills/end-of-term-teaching-materials/scripts/end_of_term/
    - skills/gongwen/scripts/gongwen_lib/
  modified:
    - skills/school-presentation/scripts/school-presentation.sh
    - skills/end-of-term-teaching-materials/scripts/render_package.py
    - skills/gongwen/scripts/gongwen.sh
metrics:
  tasks_completed: 5
  tasks_total: 5
  primary_targets_split: 3
  public_commands_preserved: 4
requirements-completed:
  - SD-05
  - SD-06
  - SD-07
  - SD-08
completed: 2026-06-12T18:45:45Z
---

# Phase 18 Plan 01: Decompose Large Script Entry Points Summary

## Outcome

Phase 18 plan 01 is complete. The largest current script entry points now delegate to skill-local modules or sourced helpers while preserving the existing public shell commands, common flags, generated artifact names, manifest key contracts, Markdown intermediate filenames, and runtime-neutral script interfaces.

## Tasks Completed

| Task | Result | Commit |
|------|--------|--------|
| Capture baseline public contracts | Captured help text, common flags, representative artifact names, manifest key sets, and status lines under `/tmp/phase18-baseline`; no tracked files changed. | N/A |
| Split `school-presentation.sh` | Kept `school-presentation.sh` as the public wrapper and moved the Python implementation behind `scripts/school_presentation/` modules for CLI, IO, parsing, rendering, assets, verification, and PDF helpers. | `7ba995e` |
| Split end-of-term renderer | Kept `render_package.py` as the stable executable shim and moved implementation behind `scripts/end_of_term/` modules for CLI, IO, source data, Markdown contract, Typst rendering, tables, and verification. | `148b4aa` |
| Split `gongwen.sh` | Kept `gongwen.sh` Bash-only and public; extracted sourced Bash modules under `gongwen_lib/` for common helpers, frontmatter, inline rendering, Typst head, body, images, tables, and commands. | `d8dc43d` |
| Shared-helper audit and regression | Left `jiaoan-shicao.sh` and `jiaoan-jihua.sh` untouched because shared extraction would broaden scope beyond proven stable contracts; ran full black-box regression through public commands. | N/A |

## Requirement Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| SD-05 | Complete | Primary large entry points were split while public command filenames and common flags stayed stable. |
| SD-06 | Complete | New module boundaries separate CLI dispatch, parsing, rendering, artifact writing, and verification/reporting helpers. |
| SD-07 | Complete | No runtime-specific private syntax was added to script interfaces; canonical skill bodies were not edited in this phase. |
| SD-08 | Complete | Shared behavior was limited to skill-local modules; no broad global framework was introduced. |

## Verification

Commands run:

```bash
git diff --check
bash -n skills/gongwen/scripts/gongwen.sh
bash -n skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
bash -n skills/jiaoan-jihua/scripts/jiaoan-jihua.sh
bash -n skills/school-presentation/scripts/school-presentation.sh
bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh
for file in skills/gongwen/scripts/gongwen_lib/*.sh; do bash -n "$file"; done
python3 -m py_compile skills/school-presentation/scripts/school_presentation/*.py skills/end-of-term-teaching-materials/scripts/render_package.py skills/end-of-term-teaching-materials/scripts/end_of_term/*.py
skills/school-presentation/scripts/school-presentation.sh verify --workdir /tmp/school-presentation-phase18-verify --max-size-mb 50
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh verify --workdir /tmp/end-of-term-phase18-verify
skills/gongwen/scripts/gongwen.sh render --input /tmp/gongwen-phase18-full.md --typ /tmp/gongwen-phase18.typ
```

Result: all commands passed. The final regression also confirmed baseline command names and common flags remain listed, school-presentation output remains offline single-file, generated Markdown intermediate filenames remain stable, baseline manifest key sets remain present, and `gongwen` generated Typst matches the baseline byte-for-byte.

## Deviations from Plan

None - plan executed within the Phase 18 scope. The only discretionary decision was to skip shared helper extraction for `jiaoan-shicao.sh` and `jiaoan-jihua.sh` because the repeated helpers were small, script-local, and not worth a new shared framework contract in this phase.

## Self-Check: PASSED

- All five plan tasks completed.
- `school-presentation.sh`, `end-of-term-teaching-materials.sh`, `render_package.py`, and `gongwen.sh` remain the public invocation surfaces.
- Phase 19 contributor documentation review, milestone audit, and milestone closeout were not performed.
- No new end-user feature behavior was added.
