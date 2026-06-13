---
phase: 20
plan: 01
subsystem: jiaoan-shicao
tags:
  - typst
  - fixture-conversion
  - skill-script
requires:
  - SHICAO-01
  - SHICAO-02
  - SHICAO-03
  - SHICAO-04
  - VERIFY-01
  - VERIFY-02
  - VERIFY-03
requirements-completed:
  - SHICAO-01
  - SHICAO-02
  - SHICAO-03
  - SHICAO-04
  - VERIFY-01
  - VERIFY-02
  - VERIFY-03
completion-evidence:
  SHICAO-01: skills/jiaoan-shicao/SKILL.md and skills/jiaoan-shicao/references/format-and-rendering.md updated for v1.10 fixture-scoped conversion.
  SHICAO-02: skills/jiaoan-shicao/scripts/jiaoan-shicao.sh renders through skill-local script code only.
  SHICAO-03: .planning/phases/20-jiaoan-shicao-1-1-typst-conversion/20-VERIFICATION.md records --expected-typ, clean diff, and matching SHA-256 evidence.
  SHICAO-04: Existing public commands example/render/manifest/info/version and render flags are preserved.
  VERIFY-01: .planning/phases/20-jiaoan-shicao-1-1-typst-conversion/20-VERIFICATION.md records generation from source Markdown through the skill-internal script.
  VERIFY-02: .planning/phases/20-jiaoan-shicao-1-1-typst-conversion/20-VERIFICATION.md records strict diff and SHA-256 output evidence.
  VERIFY-03: .planning/phases/20-jiaoan-shicao-1-1-typst-conversion/20-VERIFICATION.md is the committed standalone verification artifact for Phase 20.
provides:
  - strict v1.10 jiaoan-shicao Markdown-to-Typst generation
affects:
  - skills/jiaoan-shicao
tech_stack:
  added:
    - awk helper under skills/jiaoan-shicao/scripts
  patterns:
    - skill-local renderer helper
    - strict fixture equivalence gate
key_files:
  created:
    - skills/jiaoan-shicao/scripts/render_v110_typst.awk
    - .planning/phases/20-jiaoan-shicao-1-1-typst-conversion/20-VERIFICATION.md
  modified:
    - skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
    - skills/jiaoan-shicao/SKILL.md
    - skills/jiaoan-shicao/references/format-and-rendering.md
decisions:
  - Keep v1.10 conversion fixture-scoped and skill-local.
  - Use the target Typst only for --expected-typ comparison, diff, and hash verification.
metrics:
  duration: 8min continuation
  completed: 2026-06-13T17:33:00Z
---

# Phase 20 Plan 01: Jiaoan Shicao 教案 1:1 Typst Conversion Summary

## One-Liner

`jiaoan-shicao` now generates the v1.10 教案 Typst fixture byte-for-byte from Markdown through skill-local script code.

## What Changed

- Added `skills/jiaoan-shicao/scripts/render_v110_typst.awk`, a skill-local parser/emitter for the v1.10 教案 Markdown structure.
- Routed `jiaoan-shicao.sh render` through the v1.10 helper while preserving `example`, `render`, `manifest`, `info`, `version`, `--input`, `--typ`, `--expected-typ`, and `--calendar-output`.
- Updated skill documentation to describe fixture-scoped strict generation and the `--expected-typ` equivalence gate.

## Commits

- `095c12e` - `feat(20-01): implement jiaoan-shicao typst fixture renderer`

## Verification Evidence

Standalone verification artifact:

- `.planning/phases/20-jiaoan-shicao-1-1-typst-conversion/20-VERIFICATION.md`

## Requirement Completion Metadata

| Requirement | Status | Evidence |
|-------------|--------|----------|
| SHICAO-01 | Completed | `SKILL.md` and `references/format-and-rendering.md` document the v1.10 fixture-scoped conversion. |
| SHICAO-02 | Completed | `jiaoan-shicao.sh render` generates through `skills/jiaoan-shicao/scripts/` code. |
| SHICAO-03 | Completed | `20-VERIFICATION.md` records `--expected-typ`, clean `diff -u`, and matching SHA-256 evidence. |
| SHICAO-04 | Completed | Public workflow and command surface remain preserved. |
| VERIFY-01 | Completed | `20-VERIFICATION.md` records generation from source Markdown via the skill-internal script. |
| VERIFY-02 | Completed | `20-VERIFICATION.md` records strict diff and hash output evidence. |
| VERIFY-03 | Completed | Phase 20 standalone verification evidence is committed as `20-VERIFICATION.md`. |

Parser structure checks:

```bash
awk 'BEGIN{n=0} /^## 学习任务分析$/{n++} END{print n}' test/1.10/电气设备控制线路安装与调试教案.md
# 3

awk 'BEGIN{n=0} /^## 教学活动设计/{n++} END{print n}' test/1.10/电气设备控制线路安装与调试教案.md
# 3

awk 'BEGIN{n=0} /^## 学业评价$/{n++} END{print n}' test/1.10/电气设备控制线路安装与调试教案.md
# 3
```

Strict generation gate:

```bash
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input test/1.10/电气设备控制线路安装与调试教案.md \
  --typ /private/tmp/gsd-phase20-execute/generated.typ \
  --expected-typ test/1.10/电气设备控制线路安装与调试教案.typ
# wrote /private/tmp/gsd-phase20-execute/generated.typ
# verified Typst matches test/1.10/电气设备控制线路安装与调试教案.typ
```

Strict diff:

```bash
diff -u test/1.10/电气设备控制线路安装与调试教案.typ /private/tmp/gsd-phase20-execute/generated.typ
# no output; exit 0
```

SHA-256:

```bash
shasum -a 256 test/1.10/电气设备控制线路安装与调试教案.typ /private/tmp/gsd-phase20-execute/generated.typ
# d4a794f0d6b7f87bcc91756252a5ba983a678fdb6371c1915bf511339bb6155b  test/1.10/电气设备控制线路安装与调试教案.typ
# d4a794f0d6b7f87bcc91756252a5ba983a678fdb6371c1915bf511339bb6155b  /private/tmp/gsd-phase20-execute/generated.typ
```

Target shape check:

```bash
rg -n '#import "@preview/pointless-size:0.1.2": zh|#section-title\[学习任务分析\]|#section-title\[教学活动设计\]|#section-title\[学业评价\]' /private/tmp/gsd-phase20-execute/generated.typ
# found the import and all three repeated section-title groups
```

Anti-copy inspection:

```bash
rg -n "电气设备控制线路安装与调试教案\\.typ|test/1\\.10|cp |cat |copy_file_shell|same_file_shell|expected_typ" skills/jiaoan-shicao/scripts
# only matched the expected_typ comparison variable in jiaoan-shicao.sh
```

Phase 21 isolation:

```bash
git diff --name-only HEAD -- skills/jiaoan-jihua .planning/phases/21-jiaoan-jihua-1-1-typst-conversion
# no output
```

## Deviations from Plan

None - plan executed within the Phase 20 scope.

## Known Stubs

None.

## Threat Flags

None.

## Self-Check: PASSED

- Found `skills/jiaoan-shicao/scripts/render_v110_typst.awk`.
- Found `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`.
- Found `skills/jiaoan-shicao/SKILL.md`.
- Found `skills/jiaoan-shicao/references/format-and-rendering.md`.
- Found implementation commit `095c12e`.
