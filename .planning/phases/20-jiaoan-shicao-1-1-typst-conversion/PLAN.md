---
phase: 20
plan: 01
type: implementation
wave: 1
depends_on:
  - .planning/phases/20-jiaoan-shicao-1-1-typst-conversion/20-CONTEXT.md
  - .planning/phases/20-jiaoan-shicao-1-1-typst-conversion/RESEARCH.md
  - .planning/phases/20-jiaoan-shicao-1-1-typst-conversion/PATTERNS.md
files_modified:
  - skills/jiaoan-shicao/SKILL.md
  - skills/jiaoan-shicao/references/format-and-rendering.md
  - skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
  - skills/jiaoan-shicao/scripts/*
autonomous: true
requirements:
  - SHICAO-01
  - SHICAO-02
  - SHICAO-03
  - SHICAO-04
  - VERIFY-01
  - VERIFY-02
  - VERIFY-03
---

# Phase 20 Plan 01: jiaoan-shicao 教案 1:1 Typst Conversion

<objective>
Update only the `jiaoan-shicao` skill so `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render` converts `test/1.10/电气设备控制线路安装与调试教案.md` into Typst that strictly matches `test/1.10/电气设备控制线路安装与调试教案.typ`, while preserving the existing public command surface and proving the result through strict diff/hash evidence.
</objective>

<constraints>

- Do not execute Phase 21 and do not modify `skills/jiaoan-jihua/`.
- Do not modify target fixtures under `test/1.10/`.
- Do not call renderer code outside `skills/jiaoan-shicao/scripts/` for Markdown-to-Typst generation.
- Preserve `example`, `render`, `manifest`, `info`, `version`, `--input`, `--typ`, `--expected-typ`, and `--calendar-output`.
- Do not implement conversion by copying `test/1.10/电气设备控制线路安装与调试教案.typ`.
- Normal generation must read the Markdown input and write the requested output; the target `.typ` may only be read by comparison or independent verification commands.
- Keep `SKILL.md` concise; move long v1.10 fixture notes to `references/format-and-rendering.md` or skill-local script comments/helpers.

</constraints>

<tasks>

## Task 1: Build a skill-local parsed model for the v1.10教案 Markdown

**Type:** implementation

**Files:**

- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`
- optional new helper files under `skills/jiaoan-shicao/scripts/`

**Action:**

Replace or extend the current direct heading/paragraph streaming path with a fixture-aware parser that builds an internal model from the Markdown source:

- frontmatter fields: `course_name`, `course_attribute`, `textbook_name`, `class_name`, `total_hours`, `teacher_name`, `use_time`
- repeated task blocks keyed by `## 学习任务分析`
- task analysis fields: `学习任务`, `课时`, `起止日期`, `一、学习任务描述`, `二、学习目标`, `三、学习内容`, `四、学生情况分析`, `五、学习资源`
- activity design header from `## 教学活动设计——学习任务N：...（<hours>）`
- activity groups from `### 学习环节——学习单元`
- activity rows from `####`, `#####`, and the four content blocks that follow
- evaluation rows and summary from `## 学业评价`

Keep parsing logic shell-reviewable. If the executor splits the script, source only helper files from `skills/jiaoan-shicao/scripts/`.

**Verify:**

Run a temporary diagnostic or script-level check that proves the parser finds:

- 3 learning-task blocks
- 3 activity-design blocks
- 3 evaluation blocks
- the expected task titles for CA6140, X62W, and Z3040

Suggested commands:

```bash
awk 'BEGIN{n=0} /^## 学习任务分析$/{n++} END{print n}' \
  test/1.10/电气设备控制线路安装与调试教案.md

awk 'BEGIN{n=0} /^## 教学活动设计/{n++} END{print n}' \
  test/1.10/电气设备控制线路安装与调试教案.md

awk 'BEGIN{n=0} /^## 学业评价$/{n++} END{print n}' \
  test/1.10/电气设备控制线路安装与调试教案.md
```

**Acceptance Criteria:**

- Parser consumes the Markdown structure instead of reading or copying the target `.typ`.
- Parser preserves task order and activity order.
- Parser can feed the generator without hard-coded target fixture path.

## Task 2: Generate the fixed target Typst layout from parsed data

**Type:** implementation

**Files:**

- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`
- optional new helper files under `skills/jiaoan-shicao/scripts/`
- optional skill-local template/reference file if generated through script code

**Action:**

Implement explicit emitter functions for the target Typst contract:

- prelude with `pointless-size`, font constants, text settings, and `section-title`
- cover page with measured label/value widths
- portrait page setup for task analysis
- landscape page setup for activity design
- `学习任务分析` table per task
- `教学活动设计` tables grouped by learning环节
- `学业评价` table per task
- exact page breaks and section order

Normalize fixture-specific values where the target requires it:

- `course_attribute: 工学一体化课程` -> `□基本技能课程  ☑工学一体化课程`
- `total_hours: "160H"` -> cover value `160`
- `use_time: "2026年5月-2026年6月"` -> `2026年5月——2026年6月`
- task-analysis `课时` cells follow the committed target, not the generic Markdown heading renderer

**Verify:**

```bash
mkdir -p /private/tmp/gsd-phase20-execute

skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input test/1.10/电气设备控制线路安装与调试教案.md \
  --typ /private/tmp/gsd-phase20-execute/generated.typ

rg -n '#import "@preview/pointless-size:0.1.2": zh|#section-title\\[学习任务分析\\]|#section-title\\[教学活动设计\\]|#section-title\\[学业评价\\]' \
  /private/tmp/gsd-phase20-execute/generated.typ
```

**Acceptance Criteria:**

- Generated output has the target prelude and repeated section shape.
- Generation happens through script code under `skills/jiaoan-shicao/scripts/`.
- `render --input --typ` still works without `--expected-typ`.

## Task 3: Preserve public skill documentation and narrow fixture support notes

**Type:** documentation

**Files:**

- `skills/jiaoan-shicao/SKILL.md`
- `skills/jiaoan-shicao/references/format-and-rendering.md`

**Action:**

Update documentation only as needed:

- keep `SKILL.md` concise and preserve runtime adapter notes for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent
- document that v1.10 includes fixture-backed strict Typst generation for the provided教案 Markdown
- record that long layout details live in the reference or script helpers
- state that `--expected-typ` is the strict equivalence gate for fixture verification
- keep safety text that the script must not invoke external template binaries or renderer code

**Verify:**

```bash
rg -n "v1.10|expected-typ|OpenClaw|Hermes Agent|script|external" \
  skills/jiaoan-shicao/SKILL.md \
  skills/jiaoan-shicao/references/format-and-rendering.md
```

**Acceptance Criteria:**

- Documentation explains the fixture-scoped behavior without promising arbitrary教案 generalization.
- Runtime adapter notes remain present.
- No Phase 21 or `jiaoan-jihua` documentation is changed.

## Task 4: Prove strict output equivalence and anti-copy integrity

**Type:** verification

**Files:**

- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`
- generated output under `/private/tmp/gsd-phase20-execute/`
- phase summary or verification evidence produced during execute phase

**Action:**

Run final strict checks against an independent generated path:

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

Then inspect anti-copy boundaries:

```bash
rg -n "电气设备控制线路安装与调试教案\\.typ|test/1\\.10|cp |cat |copy_file_shell|same_file_shell|expected_typ" \
  skills/jiaoan-shicao/scripts
```

Expected final SHA-256 for both target and generated output:

`d4a794f0d6b7f87bcc91756252a5ba983a678fdb6371c1915bf511339bb6155b`

**Acceptance Criteria:**

- `--expected-typ` exits successfully.
- `diff -u` exits 0 with no output.
- `shasum -a 256` shows identical hashes for target and generated output.
- Inspection confirms target `.typ` is not copied or hard-coded into the generation path.
- Execute phase records the exact commands and results in its `SUMMARY.md` or `VERIFICATION.md`.

</tasks>

<verification>

The execute phase must not mark Phase 20 complete until all of the following pass:

1. `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --input test/1.10/电气设备控制线路安装与调试教案.md --typ /private/tmp/gsd-phase20-execute/generated.typ --expected-typ test/1.10/电气设备控制线路安装与调试教案.typ`
2. `diff -u test/1.10/电气设备控制线路安装与调试教案.typ /private/tmp/gsd-phase20-execute/generated.typ`
3. `shasum -a 256 test/1.10/电气设备控制线路安装与调试教案.typ /private/tmp/gsd-phase20-execute/generated.typ`
4. `rg -n "电气设备控制线路安装与调试教案\\.typ|test/1\\.10|cp |cat |copy_file_shell|same_file_shell|expected_typ" skills/jiaoan-shicao/scripts`
5. `git diff --name-only HEAD -- skills/jiaoan-jihua .planning/phases/21-jiaoan-jihua-1-1-typst-conversion` returns no Phase 21 changes.

</verification>

<success_criteria>

- SHICAO-01: `skills/jiaoan-shicao/SKILL.md` and skill-local references/scripts document and support the v1.10教案 conversion path.
- SHICAO-02: Markdown-to-Typst generation runs only through code under `skills/jiaoan-shicao/scripts/`.
- SHICAO-03: Generated教案 Typst strictly matches the target `.typ` by `--expected-typ`, `diff -u`, and SHA-256 evidence.
- SHICAO-04: Existing public `jiaoan-shicao` workflow remains compatible.
- VERIFY-01: Final commands generate output from the source `.md` through skill-internal scripts.
- VERIFY-02: Strict output evidence is recorded.
- VERIFY-03: Evidence is committed in phase execution summary or verification artifacts before milestone completion.

</success_criteria>

## PLANNING COMPLETE

