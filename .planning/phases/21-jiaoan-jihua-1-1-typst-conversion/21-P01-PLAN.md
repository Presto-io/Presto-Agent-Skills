---
phase: 21
plan: P01
type: execute
wave: 1
depends_on: []
files_modified:
  - skills/jiaoan-jihua/SKILL.md
  - skills/jiaoan-jihua/references/format-and-rendering.md
  - skills/jiaoan-jihua/scripts/jiaoan-jihua.sh
  - skills/jiaoan-jihua/templates/jiaoan-jihua-full.md
autonomous: true
must_haves:
  truths:
    - "D-01: Implementation scope is limited to skills/jiaoan-jihua/SKILL.md, skills/jiaoan-jihua/references/, skills/jiaoan-jihua/scripts/, and skills/jiaoan-jihua/templates/."
    - "D-02: The final Markdown-to-Typst generation path must invoke code under skills/jiaoan-jihua/scripts/ and must not rely on renderer code outside the skill directory."
    - "D-03: Preserve example, render, manifest, info, and version as recognizable public commands."
    - "D-04: Do not introduce shared jiaoan infrastructure or modify skills/jiaoan-shicao/."
    - "D-05: Generated output must target the official table-style Typst fixture, not the current generic heading/paragraph renderer shape."
    - "D-06: Parse Markdown tasks, learning stages, content rows, and trailing hour markers, then emit the five-column table structure."
    - "D-07: Emit the official header, cuti fake-bold import/show rule, page/text/par settings, helper cells, metadata grid, table rows, and signature grid."
    - "D-08: Use first_teaching_day 2026-05-11, daily_hours 8, and references/calendar.json to derive week/day allocation."
    - "D-09: Source -N suffixes are lesson-hour counts and must drive row hours, task totals, rowspans, and multi-day/multi-week spans."
    - "D-10: Preserve source task order, stage order, and content row order."
    - "D-11: Acceptance requires strict evidence against test/1.10/电气设备控制线路安装与调试授课计划.typ using clean diff and matching SHA-256 hash."
    - "D-12: PDF visual acceptance is out of scope for Phase 21."
    - "D-13: Baseline current output is 204 lines with SHA-256 0e332451a2abeaa16c660f8de928d19176f444676a8b607fc3d9fd7d1348256d; target is 372 lines with SHA-256 0d681cca76cb7d6edaf7b0c76874f3f8a5b3f49ab5e00904caf9a106690e138b."
requirements:
  - JIHUA-01
  - JIHUA-02
  - JIHUA-03
  - JIHUA-04
  - VERIFY-01
  - VERIFY-02
  - VERIFY-03
requirements_addressed:
  - JIHUA-01
  - JIHUA-02
  - JIHUA-03
  - JIHUA-04
  - VERIFY-01
  - VERIFY-02
  - VERIFY-03
---

# Phase 21 P01: Skill-Local 授课计划 Official Typst Renderer

<objective>
Update only the `jiaoan-jihua` skill so `test/1.10/电气设备控制线路安装与调试授课计划.md` is converted by `skills/jiaoan-jihua/scripts/` code into Typst that strictly matches `test/1.10/电气设备控制线路安装与调试授课计划.typ`, while preserving the existing public workflow and leaving Phase 20 untouched.
</objective>

<must_haves>
<truth id="D-01">D-01: Implementation scope is limited to `skills/jiaoan-jihua/SKILL.md`, `skills/jiaoan-jihua/references/`, `skills/jiaoan-jihua/scripts/`, and `skills/jiaoan-jihua/templates/`.</truth>
<truth id="D-02">D-02: The final generation command must invoke `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render`; no renderer code outside `skills/jiaoan-jihua/scripts/` may be required.</truth>
<truth id="D-03">D-03: Keep `example`, `render`, `manifest`, `info`, and `version` recognizable.</truth>
<truth id="D-04">D-04: Do not introduce shared jiaoan infrastructure or modify `skills/jiaoan-shicao/`.</truth>
<truth id="D-05">D-05: Generated Typst must use the official table fixture shape rather than the current generic heading/paragraph shape.</truth>
<truth id="D-06">D-06: Parse Markdown tasks, stages, content rows, and trailing `-N` hour markers into table data.</truth>
<truth id="D-07">D-07: Emit the official header, cuti fake-bold import/show rule, page/text/par settings, helper cells, metadata grid, table rows, and signature grid.</truth>
<truth id="D-08">D-08: Use `first_teaching_day: "2026-05-11"`, `daily_hours: 8`, and `skills/jiaoan-jihua/references/calendar.json` for schedule allocation.</truth>
<truth id="D-09">D-09: Hour suffixes must drive row hours, task totals, rowspans, and multi-day/multi-week spans.</truth>
<truth id="D-10">D-10: Preserve source task, stage, and content row order.</truth>
<truth id="D-11">D-11: Verification must include clean `diff -u` evidence plus matching SHA-256 hashes against the target Typst.</truth>
<truth id="D-12">D-12: Do not include PDF visual acceptance in this phase.</truth>
<truth id="D-13">D-13: Baseline current output is 204 lines with SHA-256 `0e332451a2abeaa16c660f8de928d19176f444676a8b607fc3d9fd7d1348256d`; target output is 372 lines with SHA-256 `0d681cca76cb7d6edaf7b0c76874f3f8a5b3f49ab5e00904caf9a106690e138b`.</truth>
</must_haves>

<threat_model>
<threat severity="high" mitigation="Render without reading the target fixture, then use the target only in post-generation diff/hash verification. Require source assertions that the script does not contain the target fixture path or copy-from-expected branch.">Fake conversion by copying `test/1.10/电气设备控制线路安装与调试授课计划.typ` into the generated output.</threat>
<threat severity="medium" mitigation="Keep all modifications under `skills/jiaoan-jihua/` and verify `git diff --name-only` before commit.">Scope bleed into Phase 20 or unrelated skills.</threat>
<threat severity="medium" mitigation="Use fixture-specific assertions for known week/day/hour cells and a final byte-level diff/hash check.">Off-by-one scheduling from using ISO week numbers instead of teaching-term week allocation.</threat>
</threat_model>

<tasks>
<task id="T1" type="execute">
<title>Add a reviewable official-table parser and schedule model</title>
<read_first>
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
- `skills/jiaoan-jihua/references/format-and-rendering.md`
- `skills/jiaoan-jihua/references/calendar.json`
- `test/1.10/电气设备控制线路安装与调试授课计划.md`
- `test/1.10/电气设备控制线路安装与调试授课计划.typ`
- `.planning/phases/21-jiaoan-jihua-1-1-typst-conversion/21-CONTEXT.md`
- `.planning/phases/21-jiaoan-jihua-1-1-typst-conversion/21-RESEARCH.md`
- `.planning/phases/21-jiaoan-jihua-1-1-typst-conversion/21-PATTERNS.md`
</read_first>
<files>
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
</files>
<action>
Extend the Bash script with named helpers `load_calendar_dates`, `parse_official_jihua_body`, `assign_schedule_cells`, `term_week_for_date`, and `weekday_for_date`. Reuse the existing frontmatter parser for `major_name`, `course_name`, `teacher_name`, `class_name`, `first_teaching_day`, and `daily_hours`. Parse every `##` heading into a learning task, every `###` heading into a learning stage, and every non-empty stage body line matching `text-N` into a content row with integer hours. Reject malformed non-empty body lines under stages with a clear `jiaoan-jihua.sh:` error. Consume row hours sequentially from `first_teaching_day` across `calendar.json` with `daily_hours=8`, and store per-row teaching week cells, weekday cells, and hour cells. Keep this logic inside `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`; do not call external renderers, Typst, Python, Node, or shared jiaoan code.
</action>
<acceptance_criteria>
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` contains functions named `load_calendar_dates`, `parse_official_jihua_body`, `assign_schedule_cells`, `term_week_for_date`, and `weekday_for_date`.
- Running `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render --input test/1.10/电气设备控制线路安装与调试授课计划.md --typ /tmp/jiaoan-jihua-phase21-generated.typ` exits 0.
- Generated output contains `task-th[学习任务1名称：]`, `task-th[学习任务2名称：]`, and `task-th[学习任务3名称：]`.
- Generated output contains `body-cell[11]` with `body-cell[3 4]` for `巡回指导电气线路安装过程` in task 1, proving multi-day hour allocation is data-driven.
- `git diff --name-only` does not list `skills/jiaoan-shicao/` or any Phase 20 implementation file.
</acceptance_criteria>
</task>

<task id="T2" type="execute">
<title>Emit the official Typst table from parsed Markdown data</title>
<read_first>
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
- `test/1.10/电气设备控制线路安装与调试授课计划.typ`
- `.planning/phases/21-jiaoan-jihua-1-1-typst-conversion/21-CONTEXT.md`
</read_first>
<files>
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
</files>
<action>
Add `emit_official_jihua_head`, `emit_official_jihua_table`, and `emit_official_jihua_typst`, and call `emit_official_jihua_typst` from `render_markdown_to_typst` when frontmatter `template` is `jiaoan-jihua`. The emitted Typst must include exactly the official fixed header shape: `// jiaoan-jihua official template`, `#import "@preview/cuti:0.2.1": show-cn-fakebold`, `#show: show-cn-fakebold`, A4 page settings with margins `(top: 2.54cm, bottom: 2.54cm, left: 2.8cm, right: 2.8cm)`, `font: "STSong"`, `size: 10.5pt`, helper cell definitions, document metadata, centered title `2025-2026学年第二学期第11 - 14周`, metadata grid, five-column table `(3.15cm, 8.51cm, 1.12cm, 1.29cm, 1.27cm)`, stage rowspans, content cells, derived week/day/hour cells, and trailing signature grid with `制表：教师A`. Preserve existing `example`, `manifest`, `info`, and `version` commands.
</action>
<acceptance_criteria>
- Generated output starts with `// jiaoan-jihua official template`.
- Generated output contains `#import "@preview/cuti:0.2.1": show-cn-fakebold`, `font: "STSong"`, and `columns: (3.15cm, 8.51cm, 1.12cm, 1.29cm, 1.27cm)`.
- Generated output contains `#align(center)[#text(size: 14pt, weight: "bold")[2025-2026学年第二学期第11 - 14周]]`.
- Generated output contains `table.cell(rowspan: 6, align: center + horizon, inset: cell-pad)[学习环节4名称：任务实施]` for task 2 and `table.cell(rowspan: 2, align: center + horizon, inset: cell-pad)[学习环节6名称：总结评价]` for task 3.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh example --output /tmp/jiaoan-jihua-example.md`, `manifest`, `info`, and `version` still exit 0.
</acceptance_criteria>
</task>

<task id="T3" type="execute">
<title>Document the official-table workflow and anti-copy boundary</title>
<read_first>
- `skills/jiaoan-jihua/SKILL.md`
- `skills/jiaoan-jihua/references/format-and-rendering.md`
- `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md`
- `.planning/REQUIREMENTS.md`
- `.planning/phases/21-jiaoan-jihua-1-1-typst-conversion/21-CONTEXT.md`
</read_first>
<files>
- `skills/jiaoan-jihua/SKILL.md`
- `skills/jiaoan-jihua/references/format-and-rendering.md`
- `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md`
</files>
<action>
Update documentation only where needed. In `SKILL.md`, keep the entry concise and retain all runtime adapter notes for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent. In `references/format-and-rendering.md`, add the official table contract, hour suffix parsing rule, calendar scheduling rule, strict no-copy boundary, and verification commands. Ensure `templates/jiaoan-jihua-full.md` remains a valid reviewable Markdown intermediate with the same `template: "jiaoan-jihua"` frontmatter and task/stage/hour body structure.
</action>
<acceptance_criteria>
- `skills/jiaoan-jihua/references/format-and-rendering.md` documents that target Typst is used only after generation for strict verification.
- `skills/jiaoan-jihua/references/format-and-rendering.md` includes `diff -u` and `shasum -a 256` verification commands for the Phase 21 fixture pair.
- `skills/jiaoan-jihua/SKILL.md` still contains runtime adapter rows for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
- `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md` still contains `template: "jiaoan-jihua"` and at least one `##` task, one `###` stage, and one `-N` hour line.
</acceptance_criteria>
</task>

<task id="T4" type="execute">
<title>Prove strict generation without target-copy shortcuts</title>
<read_first>
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
- `test/1.10/电气设备控制线路安装与调试授课计划.md`
- `test/1.10/电气设备控制线路安装与调试授课计划.typ`
- `.planning/phases/21-jiaoan-jihua-1-1-typst-conversion/21-CONTEXT.md`
</read_first>
<files>
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
- `.planning/phases/21-jiaoan-jihua-1-1-typst-conversion/21-01-SUMMARY.md`
- `.planning/phases/21-jiaoan-jihua-1-1-typst-conversion/21-VERIFICATION.md`
</files>
<action>
Run generation once without `--expected-typ`, then compare the generated file to the target with strict diff and hash evidence. Also run the built-in `--expected-typ` verification as a convenience check. Record commands, exit statuses, and hash lines in the Phase 21 summary or verification artifact during execute-phase. Add a source assertion showing the script does not contain the target fixture path and does not copy `expected_typ` into the generated file.
</action>
<verify>
```bash
tmpdir="$(mktemp -d)"
generated="$tmpdir/jiaoan-jihua-generated.typ"
target="test/1.10/电气设备控制线路安装与调试授课计划.typ"
source="test/1.10/电气设备控制线路安装与调试授课计划.md"

skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render \
  --input "$source" \
  --typ "$generated"

diff -u "$target" "$generated"
shasum -a 256 "$target" "$generated"

skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render \
  --input "$source" \
  --typ "$tmpdir/jiaoan-jihua-generated-expected.typ" \
  --expected-typ "$target"

! rg -n '电气设备控制线路安装与调试授课计划\.typ|test/1\.10|copy_file_shell "\$expected_typ"|cp .*expected_typ|cat .*expected_typ' \
  skills/jiaoan-jihua/scripts/jiaoan-jihua.sh

git diff --name-only
```
</verify>
<acceptance_criteria>
- The first render command exits 0 without `--expected-typ`.
- `diff -u "$target" "$generated"` exits 0.
- `shasum -a 256 "$target" "$generated"` prints the same SHA-256 for both files; expected target hash is `0d681cca76cb7d6edaf7b0c76874f3f8a5b3f49ab5e00904caf9a106690e138b`.
- The built-in `--expected-typ` render exits 0 and prints `verified Typst matches`.
- The `rg` anti-copy assertion exits 1 because no forbidden target-copy pattern exists in the script.
- `git diff --name-only` lists only Phase 21 planning artifacts and `skills/jiaoan-jihua/` files during execute-phase; it must not list `skills/jiaoan-shicao/`.
</acceptance_criteria>
</task>
</tasks>

<verification>
Execute-phase must run the full verification block in task T4. Phase 21 is not complete until generated Typst has a clean strict diff against `test/1.10/电气设备控制线路安装与调试授课计划.typ`, matching SHA-256 evidence, and an anti-copy source assertion. PDF compilation or visual PDF review is explicitly out of scope.
</verification>

<success_criteria>
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render` generates the official table Typst from Markdown and calendar data.
- The generated file strictly matches `test/1.10/电气设备控制线路安装与调试授课计划.typ`.
- Verification evidence includes strict diff and SHA-256 hash lines.
- The implementation remains skill-local to `skills/jiaoan-jihua/`.
- Public skill workflow remains recognizable.
</success_criteria>

## PLANNING COMPLETE
