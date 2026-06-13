# Phase 20 Research: jiaoan-shicao 1:1 Typst Conversion

**Date:** 2026-06-14
**Scope:** 本地 fixture 转换研究，不做外部网络研究。
**Status:** Complete

## Research Question

如何在不调用技能目录外 renderer、不直接复制目标 `.typ` 的前提下，让 `skills/jiaoan-shicao/scripts/` 内部脚本从 `test/1.10/电气设备控制线路安装与调试教案.md` 生成严格匹配 `test/1.10/电气设备控制线路安装与调试教案.typ` 的 Typst？

## Inputs Reviewed

- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/PROJECT.md`
- `.planning/phases/20-jiaoan-shicao-1-1-typst-conversion/20-CONTEXT.md`
- `.planning/phases/20-jiaoan-shicao-1-1-typst-conversion/20-DISCUSSION-LOG.md`
- `skills/jiaoan-shicao/SKILL.md`
- `skills/jiaoan-shicao/references/format-and-rendering.md`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`
- `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md`
- `test/1.10/电气设备控制线路安装与调试教案.md`
- `test/1.10/电气设备控制线路安装与调试教案.typ`

## Fixture Facts

- Source Markdown line count: 1008
- Target Typst line count: 817
- Source Markdown SHA-256: `20efb697bbbde8f49dd4bf45bcd20088a15e807b948fe12f7a3ef8ac4d22a547`
- Target Typst SHA-256: `d4a794f0d6b7f87bcc91756252a5ba983a678fdb6371c1915bf511339bb6155b`
- Source contains 3 repeated `学习任务分析` blocks.
- Source contains 3 repeated `教学活动设计` blocks.
- Source contains 3 repeated `学业评价` blocks.
- Target contains 3 `#section-title[学习任务分析]` sections, 3 `#section-title[教学活动设计]` sections, and 3 `#section-title[学业评价]` sections.

## Baseline Result

Baseline command:

```bash
mkdir -p /private/tmp/gsd-phase20-plan-baseline

skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input test/1.10/电气设备控制线路安装与调试教案.md \
  --typ /private/tmp/gsd-phase20-plan-baseline/generated.typ \
  --expected-typ test/1.10/电气设备控制线路安装与调试教案.typ
```

Result:

- Script wrote `/private/tmp/gsd-phase20-plan-baseline/generated.typ`.
- `--expected-typ` failed with `Typst differs from expected file`.
- Generated SHA-256: `3a123c40e931cbc2bba24b5a1279bb4ce52eaed083f1edb94d75ecbf687d8dda`
- Target SHA-256: `d4a794f0d6b7f87bcc91756252a5ba983a678fdb6371c1915bf511339bb6155b`
- Generated line count: 1166
- Target line count: 817

The current generic renderer is structurally insufficient. Its prelude, cover page, page setup, table layout, page breaks, activity tables, and evaluation tables do not match the target contract.

## Target Shape

The target Typst is a fixed contract for Phase 20:

- `#import "@preview/pointless-size:0.1.2": zh`
- font constants for `FONT_XBS`, `FONT_HEI`, `FONT_FS`, `FONT_KAI`, and `FONT_SONG`
- document metadata with title, author, and keywords
- A4 portrait cover page with fixed margins and measured cover label/value table
- repeated content pages with `#section-title[...]`
- learning-task analysis tables with fixed column widths
- activity-design landscape pages with repeated tables grouped by learning环节
- evaluation tables after each task block
- exact `#pagebreak()` placement

## Recommended Implementation Approach

Use a skill-local parser/generator path rather than a target-file copier.

1. Keep `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render` as the public entry.
2. Add skill-local helper functions or sourced script modules under `skills/jiaoan-shicao/scripts/`.
3. Parse frontmatter and body into an internal model:
   - cover metadata
   - ordered task blocks
   - task-analysis sections
   - activity groups
   - activity rows
   - evaluation rows and summary
4. Emit the fixed Typst template through renderer functions that consume the parsed model.
5. Keep formatting constants explicit and reviewable in script-local functions or a skill-local reference/template file.
6. Make `--expected-typ` and separate diff/hash checks the acceptance gate.

## Anti-Copy Boundary

The executor must not implement Phase 20 by copying `test/1.10/电气设备控制线路安装与调试教案.typ` to the output path or by reading it during normal generation.

Acceptable use of the target file:

- read only when `--expected-typ` is provided for comparison
- read by independent verification commands such as `diff` or `shasum`

Required implementation evidence:

- generation logic is inspectable in `skills/jiaoan-shicao/scripts/`
- normal generation path reads the Markdown input and writes the requested output
- target path is not hard-coded into generation functions
- no `cp`, `cat`, or shell redirection from the target `.typ` to the generated output appears in the render path

## Verification Recommendation

Executor should run:

```bash
mkdir -p /private/tmp/gsd-phase20-execute

skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input test/1.10/电气设备控制线路安装与调试教案.md \
  --typ /private/tmp/gsd-phase20-execute/generated.typ \
  --expected-typ test/1.10/电气设备控制线路安装与调试教案.typ

diff -u \
  test/1.10/电气设备控制线路安装与调试教案.typ \
  /private/tmp/gsd-phase20-execute/generated.typ

shasum -a 256 \
  test/1.10/电气设备控制线路安装与调试教案.typ \
  /private/tmp/gsd-phase20-execute/generated.typ
```

The expected final hash for both files is:

`d4a794f0d6b7f87bcc91756252a5ba983a678fdb6371c1915bf511339bb6155b`

## RESEARCH COMPLETE

