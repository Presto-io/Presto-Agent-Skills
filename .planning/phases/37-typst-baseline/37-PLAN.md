---
phase: 37-typst-baseline
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - skills/tiaokedan/templates/tiaokedan-reference.typ
  - skills/tiaokedan/templates/tiaokedan-reference.pdf
  - .planning/phases/37-typst-baseline/37-VERIFICATION.md
autonomous: true
requirements:
  - TKD-TYP-01
  - TKD-TYP-02
  - TKD-TYP-03
must_haves:
  truths:
    - "仓库中存在 hand-authored `调课单` Typst reference，作为自动化前的 accepted surface。"
    - "`tiaokedan-reference.typ` 明确呈现标题、收文对象、说明段、8 列表头、两行示例数据、row-1 两个时间单元格换行、右侧落款。"
    - "`tiaokedan-reference.typ` 编码 A4 横向、宋体/SimSun-family 二号加粗标题、仿宋/FangSong-family 四号正文/表格/落款、首行缩进规则、全宽居中表格、右侧落款块。"
    - "执行期要么产生非空 PDF 证据，要么在 `37-VERIFICATION.md` 记录精确 Typst compile blocker。"
    - "Phase 37 不引入 Markdown fixture/schema、renderer/parser/CLI、完整 `SKILL.md`、runtime adapter notes、README/index 更新或额外审批字段。"
  artifacts:
    - path: "skills/tiaokedan/templates/tiaokedan-reference.typ"
      provides: "hand-authored Typst accepted baseline"
      contains: "调课说明"
    - path: "skills/tiaokedan/templates/tiaokedan-reference.pdf"
      provides: "optional non-empty local compile evidence when Typst succeeds"
      optional: true
    - path: ".planning/phases/37-typst-baseline/37-VERIFICATION.md"
      provides: "source assertions, compile result or blocker, and scope-boundary evidence"
      contains: "TKD-TYP-03"
  key_links:
    - from: ".planning/phases/37-typst-baseline/37-CONTEXT.md"
      to: "skills/tiaokedan/templates/tiaokedan-reference.typ"
      via: "D-01 through D-13 locked visible/layout decisions"
      pattern: "D-01|D-13"
    - from: "skills/tiaokedan/templates/tiaokedan-reference.typ"
      to: "skills/tiaokedan/templates/tiaokedan-reference.pdf"
      via: "typst compile"
      pattern: "typst compile skills/tiaokedan/templates/tiaokedan-reference.typ"
    - from: ".planning/phases/37-typst-baseline/37-VERIFICATION.md"
      to: "skills/tiaokedan/templates/tiaokedan-reference.typ"
      via: "locked string/layout assertions"
      pattern: "调课说明|教务处：|电气工程系"
---

<objective>
Create the Phase 37 `调课单` Typst baseline before any Markdown or renderer automation exists.

Purpose: establish the accepted A4 landscape adjustment-form surface so later phases can create a Markdown contract and renderer against a stable target.
Output: `skills/tiaokedan/templates/tiaokedan-reference.typ`, optional non-empty compiled PDF evidence, and `.planning/phases/37-typst-baseline/37-VERIFICATION.md`.
</objective>

<execution_context>
@/Users/mrered/.codex/get-shit-done/workflows/execute-plan.md
@/Users/mrered/.codex/get-shit-done/templates/summary.md
</execution_context>

<context>
@AGENTS.md
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/STATE.md
@.planning/phases/37-typst-baseline/37-CONTEXT.md
@.planning/phases/37-typst-baseline/37-RESEARCH.md
@.planning/phases/37-typst-baseline/37-PATTERNS.md
@docs/directory-spec.md
@docs/markdown-normalization-contract.md

<interfaces>
This plan creates a static Typst reference fixture only. There is no existing `skills/tiaokedan/` API, no renderer interface, and no canonical `SKILL.md` in Phase 37. Treat `skills/tiaokedan/templates/tiaokedan-reference.typ` as the only source artifact that downstream Phase 38/39 work may target.
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Hand-author the accepted Typst reference surface</name>
  <files>skills/tiaokedan/templates/tiaokedan-reference.typ</files>
  <read_first>
    AGENTS.md
    docs/directory-spec.md
    docs/markdown-normalization-contract.md
    .planning/ROADMAP.md
    .planning/REQUIREMENTS.md
    .planning/phases/37-typst-baseline/37-CONTEXT.md
    .planning/phases/37-typst-baseline/37-RESEARCH.md
    .planning/phases/37-typst-baseline/37-PATTERNS.md
    If `skills/tiaokedan/templates/tiaokedan-reference.typ` already exists at execution time, read it before editing and preserve any user-authored accepted content unless it conflicts with D-01 through D-13.
  </read_first>
  <action>
    Create `skills/tiaokedan/templates/` and hand-author `skills/tiaokedan/templates/tiaokedan-reference.typ` as the Phase 37 accepted baseline for TKD-TYP-01 and TKD-TYP-02. Use the skill-local Typst template style mapped from `skills/end-of-term-teaching-materials/templates/typst/end-of-term-package.typ`, but keep this document in normal flow layout with no renderer placeholders. Encode D-01 with A4 landscape Typst page setup and default page margins only; do not introduce custom non-default margins in Phase 37. Encode D-02 with centered title text exactly `调课说明`, SimSun/Songti/STSong-family fallback following the same-font-family fallback pattern mapped from `skills/gongwen/scripts/gongwen_lib/typst_head.sh`, approximately 二号 as `22pt`, and bold weight. Encode D-03 through D-06 with FangSong/STFangsong/FangSong_GB2312-family fallback, 四号 as `14pt`, justified/distributed paragraph intent via `justify: true`, `教务处：` on its own first recipient line with no first-line indent and no stretching, and the locked explanatory paragraph exactly `因我系专职教师周老师需要去企业调研，故需将其3月11日所承担实习课程调整为早班，同时涉及到孙老师老师，具体调整如下：` with first-line indent.

    Encode D-07 through D-10 with one full text-block-width table containing exactly 8 headers: `序号`, `班级`, `课程`, `原上课时间`, `原授课教师`, `调整后上课时间`, `调整后上课教师`, `备注`. Use FangSong-family 四号 table text and cell alignment equivalent to centered horizontal plus centered vertical, such as `center + horizon`. Include both locked example rows exactly: row 1 values `1`, `27WG电气3班`, `高压电器装配与调试`, `2026年3月11日` plus an explicit Typst line break plus `14:00-19:00（D104）`, `周老师`, `2026年3月11日` plus an explicit Typst line break plus `7:30-13:00（D104）`, `周老师`, blank remark; row 2 values `2`, `27WG电气3班`, `高压电器装配与调试`, `2026年3月11日7:30-13:00（D104）`, `孙老师`, `2026年3月11日14:00-19:00（D104）`, `孙老师`, blank remark. Encode D-11 through D-13 with official-document-style blank space after the table and a right-side FangSong 四号 signature block containing exactly `电气工程系` and `2026年6月21日`.

    Do not create Markdown fixtures/contracts, missing markers, parsers, renderers, CLIs, generated-vs-reference diffing, canonical `skills/tiaokedan/SKILL.md`, runtime adapter notes, README/index/discoverability updates, approval grids, signature boxes, opinion columns, or extra fields beyond the locked closing signature.
  </action>
  <verify>
    <automated>test -d skills/tiaokedan/templates && test -s skills/tiaokedan/templates/tiaokedan-reference.typ</automated>
    <automated>rg -F '调课说明' skills/tiaokedan/templates/tiaokedan-reference.typ && rg -F '教务处：' skills/tiaokedan/templates/tiaokedan-reference.typ && rg -F '因我系专职教师周老师需要去企业调研，故需将其3月11日所承担实习课程调整为早班，同时涉及到孙老师老师，具体调整如下：' skills/tiaokedan/templates/tiaokedan-reference.typ && rg -F '电气工程系' skills/tiaokedan/templates/tiaokedan-reference.typ && rg -F '2026年6月21日' skills/tiaokedan/templates/tiaokedan-reference.typ</automated>
    <automated>for token in 序号 班级 课程 原上课时间 原授课教师 调整后上课时间 调整后上课教师 备注 27WG电气3班 高压电器装配与调试 周老师 孙老师 '14:00-19:00（D104）' '7:30-13:00（D104）'; do rg -F "$token" skills/tiaokedan/templates/tiaokedan-reference.typ >/dev/null || exit 1; done</automated>
    <automated>rg 'paper: *"a4"|flipped: *true|landscape' skills/tiaokedan/templates/tiaokedan-reference.typ && rg 'SimSun|NSimSun|Songti SC|STSong' skills/tiaokedan/templates/tiaokedan-reference.typ && rg 'FangSong|STFangsong|FangSong_GB2312|Fangsong SC' skills/tiaokedan/templates/tiaokedan-reference.typ && rg '22pt|zh\\(2\\)' skills/tiaokedan/templates/tiaokedan-reference.typ && rg '14pt|zh\\(4\\)' skills/tiaokedan/templates/tiaokedan-reference.typ && rg 'justify|first-line-indent|center \\+ horizon' skills/tiaokedan/templates/tiaokedan-reference.typ</automated>
  </verify>
  <acceptance_criteria>
    `skills/tiaokedan/templates/tiaokedan-reference.typ` is non-empty, hand-authored, and contains every visible string locked in D-02, D-04, D-06, D-09, D-10, and D-12. The source declares the typography/layout intent from D-01, D-03, D-05, D-07, D-08, D-11, and D-13. Row 1 preserves separate explicit line breaks in both time cells. No Phase 38-40 artifact is created by this task.
  </acceptance_criteria>
  <done>Accepted Typst reference source exists with locked visible content, layout/typography declarations, row-1 time-cell line breaks, and no Phase 38-40 artifacts.</done>
</task>

<task type="auto">
  <name>Task 2: Compile the baseline or capture the exact blocker</name>
  <files>skills/tiaokedan/templates/tiaokedan-reference.typ, skills/tiaokedan/templates/tiaokedan-reference.pdf, .planning/phases/37-typst-baseline/37-VERIFICATION.md</files>
  <read_first>
    skills/tiaokedan/templates/tiaokedan-reference.typ
    .planning/phases/37-typst-baseline/37-RESEARCH.md
    .planning/phases/37-typst-baseline/37-PATTERNS.md
    If `.planning/phases/37-typst-baseline/37-VERIFICATION.md` already exists at execution time, read it before editing and append/update Phase 37 evidence without deleting unrelated user notes.
  </read_first>
  <action>
    Run local Typst compilation for TKD-TYP-03 from the repository root using the exact source path `skills/tiaokedan/templates/tiaokedan-reference.typ`, following the compile/status pattern mapped from `skills/teaching-design-package/scripts/teaching-design-package.sh`: command availability is checked before compile, stderr is captured, and PDF readiness is accepted only when the output exists with byte size greater than 0. If `command -v typst` succeeds, record `typst --version`, run `typst compile skills/tiaokedan/templates/tiaokedan-reference.typ skills/tiaokedan/templates/tiaokedan-reference.pdf 2>/tmp/tiaokedan-reference.typst.stderr`, and verify the PDF exists and has byte size greater than 0. If compilation succeeds, keep `skills/tiaokedan/templates/tiaokedan-reference.pdf` as the optional non-empty local baseline evidence and record its byte size in `37-VERIFICATION.md`.

    If `typst` is unavailable, compilation exits non-zero, fonts fail, or the PDF is missing/empty, do not claim PDF success. Instead, remove any empty/partial `skills/tiaokedan/templates/tiaokedan-reference.pdf` and record the exact blocker in `37-VERIFICATION.md`: `command -v typst` result, `typst --version` result if available, exact compile command, exit code, and stderr from `/tmp/tiaokedan-reference.typst.stderr`.
  </action>
  <verify>
    <automated>if command -v typst >/dev/null 2>&1; then typst --version; fi</automated>
    <automated>if command -v typst >/dev/null 2>&1; then typst compile skills/tiaokedan/templates/tiaokedan-reference.typ skills/tiaokedan/templates/tiaokedan-reference.pdf 2>/tmp/tiaokedan-reference.typst.stderr || test -s /tmp/tiaokedan-reference.typst.stderr; else true; fi</automated>
    <automated>if test -f skills/tiaokedan/templates/tiaokedan-reference.pdf; then test "$(stat -f%z skills/tiaokedan/templates/tiaokedan-reference.pdf)" -gt 0; else test -s /tmp/tiaokedan-reference.typst.stderr || ! command -v typst >/dev/null 2>&1; fi</automated>
  </verify>
  <acceptance_criteria>
    Execution produces one of two valid states: `skills/tiaokedan/templates/tiaokedan-reference.pdf` exists with byte size greater than 0 and `37-VERIFICATION.md` records the compile command/version/size, or no PDF success is claimed and `37-VERIFICATION.md` records the exact missing-tool or compile blocker. Empty PDFs are not accepted.
  </acceptance_criteria>
  <done>Compile evidence is honest: non-empty PDF plus recorded byte size, or exact compile blocker with no PDF success claim.</done>
</task>

<task type="auto">
  <name>Task 3: Record verification evidence and enforce Phase 37 boundaries</name>
  <files>.planning/phases/37-typst-baseline/37-VERIFICATION.md</files>
  <read_first>
    .planning/ROADMAP.md
    .planning/REQUIREMENTS.md
    .planning/phases/37-typst-baseline/37-CONTEXT.md
    .planning/phases/37-typst-baseline/37-RESEARCH.md
    .planning/phases/37-typst-baseline/37-PATTERNS.md
    skills/tiaokedan/templates/tiaokedan-reference.typ
    If `skills/tiaokedan/templates/tiaokedan-reference.pdf` exists, inspect its file size before writing evidence.
  </read_first>
  <action>
    Create `.planning/phases/37-typst-baseline/37-VERIFICATION.md` as the execution evidence file for TKD-TYP-01, TKD-TYP-02, and TKD-TYP-03. Include sections for source paths, locked-decision coverage D-01 through D-13, requirement coverage, automated command log, compile result or exact blocker, PDF byte size when present, and explicit scope-boundary checks. The scope-boundary section must state that Phase 37 intentionally did not create Markdown fixture/contract/schema/missing markers, Markdown-to-Typst renderer/parser/CLI/scripts, generated-vs-reference diffing, canonical `skills/tiaokedan/SKILL.md`, runtime adapter notes, README/index/discoverability updates, approval grids, signature boxes, opinion columns, or fields beyond the locked signature.

    Run source assertions after writing the verification file and paste or summarize the exact pass/fail result in `37-VERIFICATION.md`. Use `rg` checks for every locked visible string, headers, row facts, font/layout declarations, and `find` checks for file scope. The final status in `37-VERIFICATION.md` may be `passed-with-pdf` only if the PDF is non-empty; otherwise use `passed-source-blocked-pdf` with the exact blocker.
  </action>
  <verify>
    <automated>test -s .planning/phases/37-typst-baseline/37-VERIFICATION.md</automated>
    <automated>rg -F 'TKD-TYP-01' .planning/phases/37-typst-baseline/37-VERIFICATION.md && rg -F 'TKD-TYP-02' .planning/phases/37-typst-baseline/37-VERIFICATION.md && rg -F 'TKD-TYP-03' .planning/phases/37-typst-baseline/37-VERIFICATION.md</automated>
    <automated>for token in D-01 D-02 D-03 D-04 D-05 D-06 D-07 D-08 D-09 D-10 D-11 D-12 D-13; do rg -F "$token" .planning/phases/37-typst-baseline/37-VERIFICATION.md >/dev/null || exit 1; done</automated>
    <automated>! test -e skills/tiaokedan/SKILL.md && ! test -d skills/tiaokedan/scripts && ! find skills/tiaokedan -maxdepth 3 -type f | rg '\\.(md|py|js|ts|sh)$'</automated>
    <automated>find skills/tiaokedan -maxdepth 3 -type f | sort</automated>
  </verify>
  <acceptance_criteria>
    `37-VERIFICATION.md` proves all three Phase 37 requirements, all locked decisions D-01 through D-13, the Typst source assertions, the compile success or exact blocker, and the Phase 38-40 non-goals. The `skills/tiaokedan/` tree contains only the Phase 37 template artifacts allowed by this plan.
  </acceptance_criteria>
  <done>`37-VERIFICATION.md` contains requirement coverage, D-01 through D-13 evidence, compile/blocker evidence, and negative scope checks.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| planning decisions -> Typst source | Locked Phase 37 decisions become committed Typst source; omission or drift would create a false baseline. |
| local Typst CLI -> PDF evidence | Environment-dependent compilation creates binary evidence; success must not be inferred from source existence. |
| Phase 37 scope -> later phase scope | Markdown/renderer/skill-entry work is explicitly out of scope and must not leak into this plan. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-37-01 | Tampering | `skills/tiaokedan/templates/tiaokedan-reference.typ` | mitigate | Verify all D-01 through D-13 source strings/layout declarations with `rg` and record coverage in `37-VERIFICATION.md`. |
| T-37-02 | Repudiation | `skills/tiaokedan/templates/tiaokedan-reference.pdf` | mitigate | Record exact `typst compile` command, version, exit result, stderr/blocker, and PDF byte size; accept PDF success only when size is greater than 0. |
| T-37-03 | Tampering | Phase scope boundary | mitigate | Use `find`/negative checks to prove no Markdown contract, renderer, scripts, full `SKILL.md`, adapters, README/index updates, or extra approval fields were introduced. |
| T-37-SC | Tampering | npm/pip/cargo installs | mitigate | No package-manager installs are allowed or needed in Phase 37. |
</threat_model>

<verification>
Overall phase checks:

1. `test -s skills/tiaokedan/templates/tiaokedan-reference.typ`
2. `rg -F '调课说明' skills/tiaokedan/templates/tiaokedan-reference.typ`
3. `rg -F '教务处：' skills/tiaokedan/templates/tiaokedan-reference.typ`
4. `rg -F '因我系专职教师周老师需要去企业调研，故需将其3月11日所承担实习课程调整为早班，同时涉及到孙老师老师，具体调整如下：' skills/tiaokedan/templates/tiaokedan-reference.typ`
5. `for token in 序号 班级 课程 原上课时间 原授课教师 调整后上课时间 调整后上课教师 备注 27WG电气3班 高压电器装配与调试 周老师 孙老师 '14:00-19:00（D104）' '7:30-13:00（D104）' 电气工程系 2026年6月21日; do rg -F "$token" skills/tiaokedan/templates/tiaokedan-reference.typ >/dev/null || exit 1; done`
6. `rg 'paper: *"a4"|flipped: *true|landscape' skills/tiaokedan/templates/tiaokedan-reference.typ && rg 'SimSun|NSimSun|Songti SC|STSong' skills/tiaokedan/templates/tiaokedan-reference.typ && rg 'FangSong|STFangsong|FangSong_GB2312|Fangsong SC' skills/tiaokedan/templates/tiaokedan-reference.typ`
7. `test -s .planning/phases/37-typst-baseline/37-VERIFICATION.md`
8. `! test -e skills/tiaokedan/SKILL.md && ! test -d skills/tiaokedan/scripts && ! find skills/tiaokedan -maxdepth 3 -type f | rg '\\.(md|py|js|ts|sh)$'`
9. If `skills/tiaokedan/templates/tiaokedan-reference.pdf` exists: `test "$(stat -f%z skills/tiaokedan/templates/tiaokedan-reference.pdf)" -gt 0`; otherwise `37-VERIFICATION.md` must contain the exact compile blocker.
</verification>

<success_criteria>
- TKD-TYP-01: `skills/tiaokedan/templates/tiaokedan-reference.typ` exists as a hand-authored Typst reference under the owning skill template directory.
- TKD-TYP-02: The Typst reference includes all locked visible fields, labels, table structure, row facts, signature content, and typography/layout decisions from D-01 through D-13.
- TKD-TYP-03: Local Typst compilation either produces a non-empty `tiaokedan-reference.pdf` with byte-size evidence or records the exact compile blocker in `.planning/phases/37-typst-baseline/37-VERIFICATION.md`.
- Scope boundary: Phase 38-40 artifacts remain absent.
</success_criteria>

<source_audit>
| SOURCE | ID | Feature/Requirement | Plan | Status | Notes |
|--------|----|---------------------|------|--------|-------|
| GOAL | — | Capture the accepted adjustment-form surface before automation. | 37-01 | COVERED | Typst baseline, compile/blocker evidence, and verification file. |
| REQ | TKD-TYP-01 | Hand-authored Typst reference file captures accepted adjustment-form layout before automation. | 37-01 | COVERED | Task 1 creates `tiaokedan-reference.typ`. |
| REQ | TKD-TYP-02 | Typst reference records visible fields, labels, table structure, signature area, and typography decisions. | 37-01 | COVERED | Task 1 source assertions and Task 3 evidence. |
| REQ | TKD-TYP-03 | Typst reference compiles to non-empty PDF when local tools/fonts are available. | 37-01 | COVERED | Task 2 compiles or records exact blocker. |
| RESEARCH | — | Use skill-local template under `skills/tiaokedan/templates/`, not generated Typst. | 37-01 | COVERED | Task 1. |
| RESEARCH | — | Use local Typst CLI; record PDF byte size or exact stderr/blocker. | 37-01 | COVERED | Task 2 and Task 3. |
| RESEARCH | — | Do not install packages or call sibling skill scripts. | 37-01 | COVERED | Threat model and scope checks. |
| CONTEXT | D-01 | A4 landscape with default page margins. | 37-01 | COVERED | Task 1 action and verification. |
| CONTEXT | D-02 | Title `调课说明`, centered, 宋体/SimSun-family, 二号, bold. | 37-01 | COVERED | Task 1 action and verification. |
| CONTEXT | D-03 | Body paragraphs use 仿宋/FangSong-family 四号 distributed alignment. | 37-01 | COVERED | Task 1 action and verification. |
| CONTEXT | D-04 | First recipient line has no first-line indent and reads `教务处：`. | 37-01 | COVERED | Task 1 action and verification. |
| CONTEXT | D-05 | Explanatory paragraph has first-line indent. | 37-01 | COVERED | Task 1 action and verification. |
| CONTEXT | D-06 | Locked explanatory paragraph content. | 37-01 | COVERED | Task 1 exact string assertion. |
| CONTEXT | D-07 | One table spans full text block/page body width. | 37-01 | COVERED | Task 1 action and verification. |
| CONTEXT | D-08 | 8-column multi-row table, 仿宋四号, centered horizontal/vertical cells. | 37-01 | COVERED | Task 1 action and verification. |
| CONTEXT | D-09 | Exact 8 table headers. | 37-01 | COVERED | Task 1 exact header assertions. |
| CONTEXT | D-10 | Both example rows, including row-1 line breaks in both time cells. | 37-01 | COVERED | Task 1 action and verification. |
| CONTEXT | D-11 | Public-document-style blank distance before closing signature. | 37-01 | COVERED | Task 1 action and evidence. |
| CONTEXT | D-12 | Closing signature `电气工程系` and `2026年6月21日`, 仿宋四号. | 37-01 | COVERED | Task 1 exact string assertion. |
| CONTEXT | D-13 | Right-side traditional closing area under table. | 37-01 | COVERED | Task 1 action and evidence. |
</source_audit>

<output>
Create `.planning/phases/37-typst-baseline/37-01-SUMMARY.md` when done.
</output>
