---
phase: 17
plan: 01
subsystem: skill-entry-decomposition
tags:
  - docs
  - skill-authoring
  - references
key-files:
  created:
    - skills/gongwen/references/format-and-rendering.md
    - skills/jiaoan-shicao/references/format-and-rendering.md
    - skills/jiaoan-jihua/references/format-and-rendering.md
    - skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md
    - skills/school-presentation/references/authoring-and-layout.md
    - skills/school-presentation/references/playback-and-export.md
    - skills/school-presentation/references/verification-contract.md
  modified:
    - skills/gongwen/SKILL.md
    - skills/jiaoan-shicao/SKILL.md
    - skills/jiaoan-jihua/SKILL.md
    - skills/end-of-term-teaching-materials/SKILL.md
    - skills/school-presentation/SKILL.md
    - templates/skill/SKILL.md
    - docs/directory-spec.md
    - README.md
metrics:
  tasks_completed: 3
  tasks_total: 3
  skill_entry_lines_before: 611
  skill_entry_lines_after: 514
requirements-completed:
  - SD-01
  - SD-02
  - SD-03
  - SD-04
---

# Plan 17-01 Summary: Slim Skill Entries and Move Detail into References

## Outcome

Phase 17 plan 01 is complete. Current canonical `SKILL.md` entries remain the semantic entry point while detailed authoring rules, renderer notes, artifact contracts, playback/export behavior, and verification details now live in skill-local `references/` files.

## Tasks Completed

| Task | Result | Commit |
|------|--------|--------|
| Create skill-local reference files | Added 7 reference files for gongwen, jiaoan-shicao, jiaoan-jihua, end-of-term, and school-presentation details. | `b4f54c6` |
| Slim current skill entries and link references | Rewrote 5 current skill entries to keep concise workflow maps, runtime adapter notes, outputs, verification, and safety while linking references. | `cc8602c` |
| Update contributor guidance | Updated the skill template, directory spec, and README to describe entry/reference/scripts/templates boundaries. | `b8a745c` |

Planning artifacts were created in commit `21ab1eb`.

## Requirement Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| SD-01 | Complete | Every current `SKILL.md` keeps trigger intent, objective, inputs, process, outputs, verification, safety, and runtime adapter notes visible. |
| SD-02 | Complete | Long rules moved into named skill-local `references/` files and linked from entries. |
| SD-03 | Complete | OpenClaw and Hermes Agent remain in every affected entry's supported runtime list and adapter table. |
| SD-04 | Complete | `templates/skill/SKILL.md`, `docs/directory-spec.md`, and `README.md` now describe the entry/reference/scripts/templates split. |

## Verification

Commands run:

```bash
test -f skills/gongwen/references/format-and-rendering.md
test -f skills/jiaoan-shicao/references/format-and-rendering.md
test -f skills/jiaoan-jihua/references/format-and-rendering.md
test -f skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md
test -f skills/school-presentation/references/authoring-and-layout.md
test -f skills/school-presentation/references/playback-and-export.md
test -f skills/school-presentation/references/verification-contract.md
rg -n "OpenClaw|Hermes Agent" skills/*/SKILL.md
rg -n "references/" skills/*/SKILL.md
wc -l skills/*/SKILL.md
rg -n "Runtime Adapter Notes|## Verification|## Safety" skills/*/SKILL.md
rg -n "semantic entry|references/|scripts/|templates/" templates/skill/SKILL.md docs/directory-spec.md README.md
rg -n "OpenClaw|Hermes Agent" templates/skill/SKILL.md README.md
git diff --check
bash -n skills/gongwen/scripts/gongwen.sh
bash -n skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
bash -n skills/jiaoan-jihua/scripts/jiaoan-jihua.sh
bash -n skills/school-presentation/scripts/school-presentation.sh
bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh
python3 -m py_compile skills/end-of-term-teaching-materials/scripts/render_package.py
```

Result: all commands passed. `python3 -m py_compile` produced ignored `__pycache__` files only; no validation artifact was committed.

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

- All three plan tasks completed.
- No script internals were edited.
- Public command names, flags, output paths, manifest fields, and Markdown intermediate filenames were preserved.
- Phase 18 script module decomposition was not performed.
- Phase 19 milestone audit/closeout was not performed.
