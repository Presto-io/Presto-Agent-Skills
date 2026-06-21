---
phase: 38-markdown-contract
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - skills/tiaokedan/templates/tiaokedan.md
  - skills/tiaokedan/references/markdown-contract.md
  - .planning/phases/38-markdown-contract/38-VERIFICATION.md
autonomous: true
requirements:
  - TKD-MD-01
  - TKD-MD-02
  - TKD-MD-03
must_haves:
  truths:
    - "D-01: Phase 38 creates a teacher-readable Markdown fixture using skill-local `YAML frontmatter + body`."
    - "D-02: Frontmatter owns document-level reviewable facts: `title`, `recipient`, `department`, `date`, with optional `status` or `review_notes` only when useful."
    - "D-03: The explanatory paragraph remains visible Markdown body text under `## 调课说明`, not a hidden renderer default."
    - "D-04: Adjustment rows are a normal Markdown table with exactly `序号`, `班级`, `课程`, `原上课时间`, `原授课教师`, `调整后上课时间`, `调整后上课教师`, `备注`."
    - "D-05: Row-1 time-cell line breaks are preserved with visible `<br>` inside the Markdown table cells."
    - "D-06: Teacher-maintained facts are title, recipient, explanatory reason text, table cell values, department/signature text, and date."
    - "D-07: Renderer-only defaults stay out of teacher Markdown: page setup, font fallbacks, point sizes, table ratios, padding, strokes, spacing, signature block width, Typst helper names, and PDF compile details."
    - "D-08: The contract may document renderer defaults for downstream implementers, but the fixture never requires raw Typst, CSS-like layout knobs, or font declarations."
    - "D-09: Phase 38 does not add approval grids, signature boxes, opinion columns, variants, batch fields, or renderer configuration switches."
    - "D-10: Required unknown facts use visible inline `{{待补充: 说明}}` markers."
    - "D-11: AI-drafted editable prose may use `{{AI草稿: 说明}}`; the accepted fixture prefers concrete Phase 37 facts."
    - "D-12: Later final rendering treats unresolved `{{待补充: ...}}` as non-final; Phase 39 implements non-zero validation failures."
    - "D-13: Genuinely blank optional `备注` cells may remain empty."
    - "D-14: The main fixture mirrors Phase 37 accepted facts: title `调课说明`, recipient `教务处：`, locked explanatory paragraph, exact 8-column table, two example rows, `电气工程系`, and `2026年6月21日`."
    - "D-15: The fixture is inspectable as plain Markdown before any Typst/PDF generation, without scripts, hidden generated JSON, or sibling skill resources."
    - "D-16: A skill-local reference may define field contract, required/optional fields, marker semantics, and renderer-default boundary, but not parsing or rendering."
  artifacts:
    - path: "skills/tiaokedan/templates/tiaokedan.md"
      provides: "teacher-readable Markdown fixture for the accepted `调课单` form"
      contains: "调课说明"
    - path: "skills/tiaokedan/references/markdown-contract.md"
      provides: "skill-local Markdown field contract, marker semantics, and renderer-default boundary"
      contains: "{{待补充: 说明}}"
    - path: ".planning/phases/38-markdown-contract/38-VERIFICATION.md"
      provides: "requirement coverage, source assertions, and Phase 38 scope-boundary evidence"
      contains: "TKD-MD-03"
  key_links:
    - from: "skills/tiaokedan/templates/tiaokedan-reference.typ"
      to: "skills/tiaokedan/templates/tiaokedan.md"
      via: "accepted visible facts from Phase 37 represented in teacher-editable Markdown"
      pattern: "调课说明|教务处：|电气工程系"
    - from: ".planning/phases/38-markdown-contract/38-CONTEXT.md"
      to: "skills/tiaokedan/references/markdown-contract.md"
      via: "D-01 through D-16 Markdown contract decisions"
      pattern: "D-01|D-16"
    - from: "skills/tiaokedan/references/markdown-contract.md"
      to: "skills/tiaokedan/templates/tiaokedan.md"
      via: "required fields, optional fields, marker semantics, and renderer-default exclusions"
      pattern: "{{待补充: 说明}}|renderer-only"
---

<objective>
Create the Phase 38 `调课单` Markdown contract plan so execution can add the teacher-reviewable Markdown fixture and contract reference without starting renderer or skill-entry work.

Purpose: make every accepted Phase 37 form fact editable and reviewable in Markdown, while preserving a clean boundary between teacher-maintained fields and future renderer defaults.
Output: `skills/tiaokedan/templates/tiaokedan.md`, `skills/tiaokedan/references/markdown-contract.md`, and `.planning/phases/38-markdown-contract/38-VERIFICATION.md`.
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
@.planning/phases/37-typst-baseline/37-VERIFICATION.md
@.planning/phases/38-markdown-contract/38-CONTEXT.md
@docs/directory-spec.md
@docs/markdown-normalization-contract.md
@skills/tiaokedan/templates/tiaokedan-reference.typ

<interfaces>
This phase creates Markdown-facing contract artifacts only. `skills/tiaokedan/templates/tiaokedan-reference.typ` is the accepted visual/source baseline from Phase 37. The Phase 38 Markdown fixture must express the same visible facts without raw Typst. Phase 39 will later implement parsing, validation, generated Typst, and deterministic comparison. Phase 40 will later create `skills/tiaokedan/SKILL.md`, runtime adapter notes, PDF workflow, clarification questions, and repository discoverability updates.
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Hand-author the teacher-readable Markdown fixture</name>
  <files>skills/tiaokedan/templates/tiaokedan.md</files>
  <read_first>
    AGENTS.md
    docs/directory-spec.md
    docs/markdown-normalization-contract.md
    .planning/ROADMAP.md
    .planning/REQUIREMENTS.md
    .planning/phases/37-typst-baseline/37-CONTEXT.md
    .planning/phases/37-typst-baseline/37-VERIFICATION.md
    .planning/phases/38-markdown-contract/38-CONTEXT.md
    skills/tiaokedan/templates/tiaokedan-reference.typ
    If `skills/tiaokedan/templates/tiaokedan.md` already exists at execution time, read it before editing and preserve any user-authored accepted facts unless they conflict with Phase 37 or Phase 38 locked decisions.
  </read_first>
  <action>
    Create `skills/tiaokedan/templates/tiaokedan.md` as the accepted Phase 38 teacher-readable Markdown fixture for TKD-MD-01. Use `YAML frontmatter + body`, with frontmatter fields exactly `title`, `recipient`, `department`, and `date`; optional draft state fields such as `status` or `review_notes` may be omitted from the accepted fixture unless execution needs them for a concrete review note. Set the accepted frontmatter values to `title: 调课说明`, `recipient: 教务处：`, `department: 电气工程系`, and `date: 2026年6月21日`.

    In the body, include a `## 调课说明` heading and keep the explanatory paragraph as visible Markdown text exactly `因我系专职教师周老师需要去企业调研，故需将其3月11日所承担实习课程调整为早班，同时涉及到孙老师老师，具体调整如下：`. Add one normal Markdown table with exactly these 8 headers in this order: `序号`, `班级`, `课程`, `原上课时间`, `原授课教师`, `调整后上课时间`, `调整后上课教师`, `备注`. Add exactly the two accepted rows from Phase 37. Row 1 time cells must preserve teacher-facing line breaks with visible `<br>`: `2026年3月11日<br>14:00-19:00（D104）` and `2026年3月11日<br>7:30-13:00（D104）`. Row 2 time cells remain single-line: `2026年3月11日7:30-13:00（D104）` and `2026年3月11日14:00-19:00（D104）`. Keep both accepted `备注` cells empty because they are genuinely blank optional facts, not missing required facts. Include the closing signature facts as visible Markdown after the table, using `电气工程系` and `2026年6月21日`.

    Do not put raw Typst, page setup, font fallback lists, point sizes, table width ratios, cell padding/strokes, right-aligned signature widths, Typst helper names, renderer configuration, PDF compile details, approval grids, signature boxes, opinion columns, variants, batch fields, or spreadsheet-import fields into `tiaokedan.md`.
  </action>
  <verify>
    <automated>test -s skills/tiaokedan/templates/tiaokedan.md</automated>
    <automated>head -1 skills/tiaokedan/templates/tiaokedan.md | rg '^---$' && rg '^title: 调课说明$|^recipient: 教务处：$|^department: 电气工程系$|^date: 2026年6月21日$' skills/tiaokedan/templates/tiaokedan.md</automated>
    <automated>rg -F '## 调课说明' skills/tiaokedan/templates/tiaokedan.md && rg -F '因我系专职教师周老师需要去企业调研，故需将其3月11日所承担实习课程调整为早班，同时涉及到孙老师老师，具体调整如下：' skills/tiaokedan/templates/tiaokedan.md</automated>
    <automated>rg -F '| 序号 | 班级 | 课程 | 原上课时间 | 原授课教师 | 调整后上课时间 | 调整后上课教师 | 备注 |' skills/tiaokedan/templates/tiaokedan.md</automated>
    <automated>for token in '27WG电气3班' '高压电器装配与调试' '2026年3月11日<br>14:00-19:00（D104）' '2026年3月11日<br>7:30-13:00（D104）' '2026年3月11日7:30-13:00（D104）' '2026年3月11日14:00-19:00（D104）' '周老师' '孙老师' '电气工程系' '2026年6月21日'; do rg -F "$token" skills/tiaokedan/templates/tiaokedan.md >/dev/null || exit 1; done</automated>
    <automated>! rg 'page\\(|#set|table\\(|columns:|FangSong|Songti|SimSun|STSong|typst compile|pdf|renderer|approval|审批|意见栏' skills/tiaokedan/templates/tiaokedan.md</automated>
  </verify>
  <acceptance_criteria>
    `skills/tiaokedan/templates/tiaokedan.md` is a plain Markdown file with YAML frontmatter and teacher-readable body. It contains all accepted Phase 37 visible facts, preserves row-1 time line breaks with `<br>`, keeps blank optional remarks empty, and contains no raw Typst or renderer-only defaults.
  </acceptance_criteria>
  <done>Accepted Markdown fixture exists with exact Phase 37 facts and no Phase 39/40 implementation content.</done>
</task>

<task type="auto">
  <name>Task 2: Write the skill-local Markdown contract reference</name>
  <files>skills/tiaokedan/references/markdown-contract.md</files>
  <read_first>
    AGENTS.md
    docs/directory-spec.md
    docs/markdown-normalization-contract.md
    .planning/REQUIREMENTS.md
    .planning/phases/38-markdown-contract/38-CONTEXT.md
    skills/tiaokedan/templates/tiaokedan-reference.typ
    skills/tiaokedan/templates/tiaokedan.md
    If `skills/tiaokedan/references/markdown-contract.md` already exists at execution time, read it before editing and preserve user-authored contract notes unless they conflict with D-01 through D-16.
  </read_first>
  <action>
    Create `skills/tiaokedan/references/markdown-contract.md` for TKD-MD-02 and TKD-MD-03. The reference must be skill-local, concise, and implementation-neutral: it defines the Markdown contract that Phase 39 may consume later, but it must not implement parsing, rendering, or validation code. Include sections for: fixture path, contract shape, frontmatter fields, body sections, adjustment table columns, required vs optional facts, unknown-value markers, renderer-owned defaults, and Phase 38 non-goals.

    Define required teacher-maintained facts as `title`, `recipient`, explanatory reason text, every non-optional table cell value in the 8 columns, `department`, and `date`. Define `备注` as optional per row when the accepted form fact is genuinely blank. Define the required unknown marker exactly as `{{待补充: 说明}}`, with a short example such as `{{待补充: 原上课地点}}`. Define AI-drafted editable prose marker exactly as `{{AI草稿: 说明}}` and state that the accepted fixture should prefer concrete Phase 37 facts unless intentionally demonstrating review behavior. State that later final rendering must treat unresolved `{{待补充: ...}}` markers as non-final, while Phase 39 will implement the non-zero validation failure.

    Explicitly list renderer-owned defaults that teachers do not maintain in Markdown: A4 landscape page setup, default page margins, font fallback lists, point sizes, table column width ratios, cell padding, strokes, vertical spacing, right-side signature block width, Typst helper names, generated Typst paths, PDF compile commands, comparison evidence, and debug diagnostics. State that `tiaokedan.md` must not contain raw Typst or these layout knobs.

    Explicitly state Phase 38 non-goals: no renderer/parser/CLI/scripts, no generated Typst, no PDF workflow, no canonical `skills/tiaokedan/SKILL.md`, no runtime adapter notes, no README/index/discoverability updates, no approval grids, no signature boxes, no opinion columns, no school-specific variants, no batch generation, and no spreadsheet import.
  </action>
  <verify>
    <automated>test -s skills/tiaokedan/references/markdown-contract.md</automated>
    <automated>rg -F 'skills/tiaokedan/templates/tiaokedan.md' skills/tiaokedan/references/markdown-contract.md && rg -F 'YAML frontmatter + body' skills/tiaokedan/references/markdown-contract.md</automated>
    <automated>for token in title recipient department date '序号' '班级' '课程' '原上课时间' '原授课教师' '调整后上课时间' '调整后上课教师' '备注'; do rg -F "$token" skills/tiaokedan/references/markdown-contract.md >/dev/null || exit 1; done</automated>
    <automated>rg -F '{{待补充: 说明}}' skills/tiaokedan/references/markdown-contract.md && rg -F '{{AI草稿: 说明}}' skills/tiaokedan/references/markdown-contract.md</automated>
    <automated>rg -F 'renderer-owned defaults' skills/tiaokedan/references/markdown-contract.md && rg -F 'A4 landscape' skills/tiaokedan/references/markdown-contract.md && rg -F 'Phase 38 non-goals' skills/tiaokedan/references/markdown-contract.md</automated>
    <automated>! rg 'def |function |class |#!/|import |require\\(|typst compile skills/tiaokedan/templates/tiaokedan.md' skills/tiaokedan/references/markdown-contract.md</automated>
  </verify>
  <acceptance_criteria>
    `skills/tiaokedan/references/markdown-contract.md` documents the skill-local field contract, required/optional facts, exact review markers, future validation expectation for unresolved `{{待补充: ...}}`, and renderer-default boundary. It does not contain executable parser/renderer code or Phase 39/40 deliverables.
  </acceptance_criteria>
  <done>Markdown contract reference exists with field, marker, renderer-default, and non-goal boundaries.</done>
</task>

<task type="auto">
  <name>Task 3: Record Phase 38 verification and scope evidence</name>
  <files>.planning/phases/38-markdown-contract/38-VERIFICATION.md</files>
  <read_first>
    .planning/ROADMAP.md
    .planning/REQUIREMENTS.md
    .planning/phases/38-markdown-contract/38-CONTEXT.md
    skills/tiaokedan/templates/tiaokedan-reference.typ
    skills/tiaokedan/templates/tiaokedan.md
    skills/tiaokedan/references/markdown-contract.md
    If `.planning/phases/38-markdown-contract/38-VERIFICATION.md` already exists at execution time, read it before editing and append/update Phase 38 evidence without deleting unrelated user notes.
  </read_first>
  <action>
    Create `.planning/phases/38-markdown-contract/38-VERIFICATION.md` as the execution evidence file for TKD-MD-01, TKD-MD-02, and TKD-MD-03. Include sections for source paths, requirement coverage, decision coverage D-01 through D-16, Markdown fixture assertions, contract-reference assertions, and explicit Phase 39/40 scope-boundary checks.

    The verification file must prove TKD-MD-01 by checking that `tiaokedan.md` exists, has YAML frontmatter, contains the accepted Phase 37 title/recipient/paragraph/table rows/signature facts, and is readable without any generated JSON/script. It must prove TKD-MD-02 by checking that the fixture does not contain raw Typst/layout knobs and the contract reference lists renderer-owned defaults outside teacher-maintained fields. It must prove TKD-MD-03 by checking that the contract reference defines `{{待补充: 说明}}`, `{{AI草稿: 说明}}`, non-final behavior for unresolved required markers, and the optional blank `备注` rule.

    Add negative scope checks proving execution did not create `skills/tiaokedan/scripts/`, generated Typst output, Markdown-to-Typst renderer code, `skills/tiaokedan/SKILL.md`, runtime adapter notes, README/index/discoverability updates, approval grids, signature boxes, opinion columns, variants, batch support, or spreadsheet import.
  </action>
  <verify>
    <automated>test -s .planning/phases/38-markdown-contract/38-VERIFICATION.md</automated>
    <automated>rg -F 'TKD-MD-01' .planning/phases/38-markdown-contract/38-VERIFICATION.md && rg -F 'TKD-MD-02' .planning/phases/38-markdown-contract/38-VERIFICATION.md && rg -F 'TKD-MD-03' .planning/phases/38-markdown-contract/38-VERIFICATION.md</automated>
    <automated>for token in D-01 D-02 D-03 D-04 D-05 D-06 D-07 D-08 D-09 D-10 D-11 D-12 D-13 D-14 D-15 D-16; do rg -F "$token" .planning/phases/38-markdown-contract/38-VERIFICATION.md >/dev/null || exit 1; done</automated>
    <automated>! test -e skills/tiaokedan/SKILL.md && ! test -d skills/tiaokedan/scripts</automated>
    <automated>! find skills/tiaokedan -maxdepth 3 -type f | rg 'generated|renderer|\\.py$|\\.js$|\\.ts$|\\.sh$'</automated>
    <automated>! git diff --name-only -- README.md docs/directory-spec.md docs/compatibility-matrix.md skills/README.md | rg .</automated>
  </verify>
  <acceptance_criteria>
    `38-VERIFICATION.md` records positive evidence for all three Phase 38 requirements, D-01 through D-16, source assertions for the fixture and contract reference, and negative scope checks for Phase 39/40 artifacts.
  </acceptance_criteria>
  <done>Phase 38 verification file proves Markdown fixture, contract boundary, marker semantics, and scope discipline.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Phase 37 Typst baseline -> Markdown fixture | Accepted visible facts move from Typst into teacher-editable Markdown; omissions or wording drift would break the contract. |
| Teacher-maintained Markdown -> future renderer defaults | Layout and PDF mechanics must stay out of teacher fields so the source remains reviewable and not raw Typst. |
| Required unknown markers -> final rendering | Required missing facts must remain visible now and become non-final validation failures in Phase 39. |
| Phase 38 scope -> Phase 39/40 scope | Planning and execution must not create renderer, PDF workflow, skill entry, adapters, or discoverability work early. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-38-01 | Tampering | `skills/tiaokedan/templates/tiaokedan.md` | mitigate | Use exact string/table assertions against Phase 37 facts, including row-1 `<br>` line breaks and blank optional remarks. |
| T-38-02 | Information Disclosure | teacher-maintained Markdown | mitigate | Keep renderer-only defaults, generated paths, compile details, and debug diagnostics out of `tiaokedan.md`; document them only as non-teacher-owned boundaries in the reference. |
| T-38-03 | Repudiation | unknown required values | mitigate | Define visible `{{待补充: 说明}}` markers and record that unresolved markers are non-final for later renderer validation. |
| T-38-04 | Tampering | Phase scope boundary | mitigate | Use negative file and diff checks to prove no scripts, generated Typst, `SKILL.md`, runtime adapter notes, README/index updates, or PDF workflow were created. |
| T-38-SC | Tampering | package installs and external services | mitigate | No package-manager installs, network calls, external services, or sibling skill scripts are allowed or needed in Phase 38. |
</threat_model>

<verification>
Overall phase checks:

1. `test -s skills/tiaokedan/templates/tiaokedan.md`
2. `head -1 skills/tiaokedan/templates/tiaokedan.md | rg '^---$'`
3. `rg '^title: 调课说明$|^recipient: 教务处：$|^department: 电气工程系$|^date: 2026年6月21日$' skills/tiaokedan/templates/tiaokedan.md`
4. `rg -F '因我系专职教师周老师需要去企业调研，故需将其3月11日所承担实习课程调整为早班，同时涉及到孙老师老师，具体调整如下：' skills/tiaokedan/templates/tiaokedan.md`
5. `rg -F '| 序号 | 班级 | 课程 | 原上课时间 | 原授课教师 | 调整后上课时间 | 调整后上课教师 | 备注 |' skills/tiaokedan/templates/tiaokedan.md`
6. `for token in '27WG电气3班' '高压电器装配与调试' '2026年3月11日<br>14:00-19:00（D104）' '2026年3月11日<br>7:30-13:00（D104）' '2026年3月11日7:30-13:00（D104）' '2026年3月11日14:00-19:00（D104）' '周老师' '孙老师' '电气工程系' '2026年6月21日'; do rg -F "$token" skills/tiaokedan/templates/tiaokedan.md >/dev/null || exit 1; done`
7. `! rg 'page\\(|#set|table\\(|columns:|FangSong|Songti|SimSun|STSong|typst compile|pdf|renderer|approval|审批|意见栏' skills/tiaokedan/templates/tiaokedan.md`
8. `test -s skills/tiaokedan/references/markdown-contract.md`
9. `rg -F '{{待补充: 说明}}' skills/tiaokedan/references/markdown-contract.md && rg -F '{{AI草稿: 说明}}' skills/tiaokedan/references/markdown-contract.md`
10. `rg -F 'renderer-owned defaults' skills/tiaokedan/references/markdown-contract.md && rg -F 'Phase 38 non-goals' skills/tiaokedan/references/markdown-contract.md`
11. `test -s .planning/phases/38-markdown-contract/38-VERIFICATION.md`
12. `rg -F 'TKD-MD-01' .planning/phases/38-markdown-contract/38-VERIFICATION.md && rg -F 'TKD-MD-02' .planning/phases/38-markdown-contract/38-VERIFICATION.md && rg -F 'TKD-MD-03' .planning/phases/38-markdown-contract/38-VERIFICATION.md`
13. `! test -e skills/tiaokedan/SKILL.md && ! test -d skills/tiaokedan/scripts`
14. `! find skills/tiaokedan -maxdepth 3 -type f | rg 'generated|renderer|\\.py$|\\.js$|\\.ts$|\\.sh$'`
15. `! git diff --name-only -- README.md docs/directory-spec.md docs/compatibility-matrix.md skills/README.md | rg .`
</verification>

<success_criteria>
- TKD-MD-01: `skills/tiaokedan/templates/tiaokedan.md` exists as a hand-authored, teacher-readable Markdown fixture with all facts needed by the Phase 37 Typst form.
- TKD-MD-02: `skills/tiaokedan/templates/tiaokedan.md` contains only teacher-maintained facts, while `skills/tiaokedan/references/markdown-contract.md` documents renderer-only defaults outside the fixture.
- TKD-MD-03: `skills/tiaokedan/references/markdown-contract.md` defines visible markers for required unknowns and AI-drafted editable prose, including the later non-final behavior for unresolved required markers.
- Scope boundary: Phase 39/40 artifacts remain absent.
</success_criteria>

<source_audit>
| SOURCE | ID | Feature/Requirement | Plan | Status | Notes |
|--------|----|---------------------|------|--------|-------|
| GOAL | — | Create the teacher-reviewable Markdown fixture and contract that can express every required form fact without raw Typst. | 38-01 | COVERED | Tasks 1 and 2 create Markdown fixture and contract reference only. |
| REQ | TKD-MD-01 | Hand-authored Markdown fixture is teacher-readable and contains all facts required by the Typst form. | 38-01 | COVERED | Task 1 creates `tiaokedan.md`; Task 3 verifies all accepted facts. |
| REQ | TKD-MD-02 | Markdown contract separates user-maintained form facts from renderer-only defaults. | 38-01 | COVERED | Task 2 documents teacher fields and renderer-owned defaults; Task 1 keeps defaults out of fixture. |
| REQ | TKD-MD-03 | Fixture/reference documentation define missing or unknown adjustment fact markers before final rendering. | 38-01 | COVERED | Task 2 defines `{{待补充: 说明}}`, `{{AI草稿: 说明}}`, and optional blank remarks. |
| CONTEXT | D-01 | Use YAML frontmatter + body. | 38-01 | COVERED | Task 1 fixture shape and Task 2 contract shape. |
| CONTEXT | D-02 | Frontmatter carries title, recipient, department, date, and optional status/review notes if useful. | 38-01 | COVERED | Task 1 exact frontmatter fields; optional fields may be omitted. |
| CONTEXT | D-03 | Explanatory paragraph is visible Markdown body text under a clear heading. | 38-01 | COVERED | Task 1 body. |
| CONTEXT | D-04 | Adjustment rows are a normal Markdown table with exactly Phase 37 visible columns. | 38-01 | COVERED | Task 1 table. |
| CONTEXT | D-05 | Preserve teacher-facing line breaks with visible `<br>` where baseline intentionally line-breaks values. | 38-01 | COVERED | Task 1 row-1 time cells. |
| CONTEXT | D-06 | Teacher facts include title, recipient, reason text, table cells, department/signature text, and date. | 38-01 | COVERED | Task 2 required facts. |
| CONTEXT | D-07 | Renderer-only defaults stay out of teacher-maintained Markdown fields. | 38-01 | COVERED | Task 1 exclusions and Task 2 defaults list. |
| CONTEXT | D-08 | Contract may document renderer defaults but fixture does not require raw Typst/layout knobs. | 38-01 | COVERED | Task 2 reference; Task 1 negative checks. |
| CONTEXT | D-09 | Do not add approval grids, signature boxes, opinion columns, variants, batch fields, or renderer switches. | 38-01 | COVERED | Task 1 and Task 3 scope checks. |
| CONTEXT | D-10 | Required unknown values use `{{待补充: 说明}}`. | 38-01 | COVERED | Task 2 marker definition. |
| CONTEXT | D-11 | AI-drafted editable prose may use `{{AI草稿: 说明}}`; accepted fixture should prefer concrete facts. | 38-01 | COVERED | Task 2 marker definition; Task 1 concrete facts. |
| CONTEXT | D-12 | Later final rendering treats unresolved `{{待补充: ...}}` as non-final; Phase 39 implements non-zero failures. | 38-01 | COVERED | Task 2 records future validation expectation. |
| CONTEXT | D-13 | Empty optional `备注` cells may remain empty when genuinely blank. | 38-01 | COVERED | Task 1 row remarks and Task 2 optional rule. |
| CONTEXT | D-14 | Fixture mirrors Phase 37 accepted facts. | 38-01 | COVERED | Task 1 exact strings/table rows/signature. |
| CONTEXT | D-15 | Fixture is inspectable as plain Markdown before Typst/PDF generation. | 38-01 | COVERED | Task 1 creates copyable Markdown with no scripts/generated JSON. |
| CONTEXT | D-16 | Longer reference may define field contract, required/optional fields, marker semantics, renderer-default boundary, but not parsing/rendering. | 38-01 | COVERED | Task 2. |
</source_audit>

<output>
Create `.planning/phases/38-markdown-contract/38-01-SUMMARY.md` when done.
</output>
