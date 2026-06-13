# Phase 20 Patterns: Existing jiaoan-shicao Script and Skill Structure

**Date:** 2026-06-14
**Status:** Complete

## Existing Public Interface

`skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` already exposes the public command surface required by Phase 20:

- `example --output <jiaoan-shicao-full.md> [--calendar-output <calendar.json>]`
- `render --input <input.md> [--typ <output.typ>] [--expected-typ <reference.typ>]`
- `manifest`
- `info`
- `version`

The Phase 20 implementation should preserve this surface. The final user-facing conversion should still be:

```bash
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input test/1.10/电气设备控制线路安装与调试教案.md \
  --typ <generated-output.typ> \
  --expected-typ test/1.10/电气设备控制线路安装与调试教案.typ
```

## Existing Script Capabilities

The current script has reusable low-level pieces:

- `need_file` validates inputs.
- `ensure_parent_dir` validates output parent directories.
- `trim` and `strip_quotes` normalize shell-parsed text.
- `parse_input` reads YAML frontmatter and body lines.
- `escape_string`, `escape_content`, `render_inline`, and `render_plain_segment` already handle basic Typst escaping.
- `same_file_shell` compares generated Typst against an expected file without invoking external diff tooling.
- `cmd_render` already wires `--input`, `--typ`, and `--expected-typ`.

These pieces should be reused or kept compatible instead of replacing the script with an unrelated entry point.

## Existing Gaps

The generic renderer currently emits:

- a generic Typst prelude
- simple metadata block
- Markdown headings as Typst headings
- simple lists and basic tables

The target requires:

- fixed official cover page
- specific Chinese font constants
- `pointless-size` import
- portrait and landscape page setup switches
- `section-title` helper
- structured table generation for task analysis, teaching activities, and evaluation
- exact blank-line and semicolon punctuation behavior inside table cells
- exact page-break positions

## Recommended File Ownership

Allowed Phase 20 files:

- `skills/jiaoan-shicao/SKILL.md`
- `skills/jiaoan-shicao/references/format-and-rendering.md`
- new or existing files under `skills/jiaoan-shicao/scripts/`
- new or existing files under `skills/jiaoan-shicao/templates/` if the executor chooses a skill-local template constant

Planning-only files:

- `.planning/phases/20-jiaoan-shicao-1-1-typst-conversion/RESEARCH.md`
- `.planning/phases/20-jiaoan-shicao-1-1-typst-conversion/PATTERNS.md`
- `.planning/phases/20-jiaoan-shicao-1-1-typst-conversion/PLAN.md`
- `.planning/phases/20-jiaoan-shicao-1-1-typst-conversion/PLAN-CHECK.md`

Forbidden in Phase 20:

- `skills/jiaoan-jihua/`
- `.planning/phases/21-jiaoan-jihua-1-1-typst-conversion/`
- any renderer code outside `skills/jiaoan-shicao/scripts/`
- modifications to committed target fixtures in `test/1.10/`

## Parser Pattern

The Markdown fixture has a stable nested shape:

1. YAML frontmatter.
2. `## 学习任务分析`.
3. `## 教学活动设计——学习任务N：...（<hours>）`.
4. Multiple `### 学习环节——学习单元` groups.
5. Repeated activity records:
   - `#### 活动名称`
   - `##### 课时`
   - learning content block
   - student activity block
   - teacher activity block
   - teaching method block
6. `## 学业评价`.
7. Three-item numbered evaluation list plus `小结：...`.

Executor should parse this into records rather than stream headings directly to Typst. A small internal model is enough:

- `cover`
- `tasks[]`
- `task.analysis`
- `task.activity_groups[]`
- `group.activities[]`
- `task.evaluation.items[]`
- `task.evaluation.summary`

## Generator Pattern

The Typst generator should be explicit and reviewable:

- emit a fixed prelude function
- emit a cover function from frontmatter values
- emit `学习任务分析` table per task
- emit `教学活动设计` landscape page per task
- emit each activity group as one Typst table
- emit `学业评价` table per task
- emit page breaks between target sections exactly as required

The generator may contain target-specific layout constants because Phase 20 is fixture-scoped, but those constants must be documented as v1.10 fixture support.

## Anti-Copy Review Pattern

Before accepting execution, reviewer should inspect:

```bash
rg -n "电气设备控制线路安装与调试教案\\.typ|test/1\\.10|cp |cat |copy_file_shell|same_file_shell|expected_typ" \
  skills/jiaoan-shicao/scripts
```

Expected result:

- `expected_typ` references are only in comparison logic.
- There is no target fixture path hard-coded in generation functions.
- Any copy helper remains limited to `example` and calendar support, not render output.
- No render path copies target `.typ` bytes into generated output.

## PATTERNS COMPLETE

