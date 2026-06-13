# Phase 21 Pattern Map

**Date:** 2026-06-14
**Status:** Complete

## Files In Scope

| File | Role | Existing Pattern | Phase 21 Use |
|------|------|------------------|--------------|
| `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` | CLI, parser, renderer, comparison helper | Bash-only command dispatch, frontmatter parsing, escaping helpers, shell file comparison | Primary implementation file. Keep public commands and add official-table parser/emitter helpers. |
| `skills/jiaoan-jihua/SKILL.md` | Canonical skill entry | Concise workflow, runtime adapter notes, script usage | Update only if command behavior or strict verification instructions need a short note. |
| `skills/jiaoan-jihua/references/format-and-rendering.md` | Long-form format rules | Frontmatter/body/calendar/rendering/verification sections | Add official table rendering contract, anti-copy boundary, and strict diff/hash commands. |
| `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md` | Reviewable Markdown intermediate example | Same structure as fixture with sample teacher/class metadata | Keep or minimally update to remain a valid example for official-table rendering. |
| `skills/jiaoan-jihua/references/calendar.json` | Teaching date source | Ordered JSON array of teaching dates | Read for scheduling; do not mutate. |
| `test/1.10/电气设备控制线路安装与调试授课计划.md` | Source fixture | Regular frontmatter + task/stage/hour body | Use as source input for verification. |
| `test/1.10/电气设备控制线路安装与调试授课计划.typ` | Target fixture | Official Typst table | Use only as post-generation verification oracle. |

## Existing Script Patterns To Preserve

### Command Dispatch

`main()` dispatches `example`, `render`, `manifest`, `info`, and `version`. Preserve this public surface so existing workflow docs remain recognizable.

### Frontmatter Parsing

`parse_input()` and `set_meta_value()` already extract the frontmatter fields needed by the fixture. Reuse or extend them instead of adding a second incompatible parser.

### Typst Escaping

`escape_string`, `escape_content`, `render_plain_segment`, and `render_inline` already handle most text escaping. Reuse these helpers for content cells unless the official table needs stricter plain-cell behavior.

### Expected-File Comparison

`same_file_shell()` performs a line-by-line shell comparison. It can remain for `--expected-typ`, but strict execute-phase verification should also run external `diff -u` and `shasum -a 256` commands as required by Phase 21.

## New Helper Pattern

Use a small, named data pipeline inside `jiaoan-jihua.sh`:

1. `load_calendar_dates`: read `references/calendar.json` into an ordered Bash array.
2. `parse_official_jihua_body`: convert `BODY_LINES` into task/stage/content/hour records.
3. `assign_schedule_cells`: consume hours across calendar dates and attach week/day cells.
4. `emit_official_jihua_head`: emit fixed Typst imports, page/text/par settings, helper cell functions, document metadata, title, and metadata grid.
5. `emit_official_jihua_table`: emit task header rows, stage rowspans, content rows, scheduling cells, and signature grid.
6. `emit_official_jihua_typst`: orchestration wrapper called by `render_markdown_to_typst` when `template: jiaoan-jihua` is present.

## Source-Of-Truth Boundary

- Source data: Markdown fixture plus `calendar.json`.
- Target data: only for post-generation verification.
- Forbidden implementation shortcut: reading or copying `test/1.10/电气设备控制线路安装与调试授课计划.typ` during render.

## PATTERN MAPPING COMPLETE
