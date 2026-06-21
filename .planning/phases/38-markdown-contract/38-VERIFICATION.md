# Phase 38 Verification: 调课单 Markdown Contract

**Status:** passed
**Verified:** 2026-06-21
**Phase:** 38 — 调课单 Markdown Contract

## Source Paths

| Artifact | Path | Status |
|----------|------|--------|
| Phase 37 accepted Typst baseline | `skills/tiaokedan/templates/tiaokedan-reference.typ` | present, read as source of visible facts |
| Teacher-readable Markdown fixture | `skills/tiaokedan/templates/tiaokedan.md` | present, non-empty |
| Skill-local Markdown contract | `skills/tiaokedan/references/markdown-contract.md` | present, non-empty |

## Requirement Coverage

| Requirement | Evidence | Status |
|-------------|----------|--------|
| TKD-MD-01 | `skills/tiaokedan/templates/tiaokedan.md` uses YAML frontmatter plus body, contains the accepted Phase 37 title, recipient, reason paragraph, 8-column table rows, department, and date. | passed |
| TKD-MD-02 | The fixture contains teacher-maintained facts only; renderer-owned layout defaults are documented in `skills/tiaokedan/references/markdown-contract.md` and excluded from the fixture. | passed |
| TKD-MD-03 | `skills/tiaokedan/references/markdown-contract.md` defines `{{待补充: 说明}}`, `{{AI草稿: 说明}}`, non-final behavior for unresolved required markers, and the optional blank `备注` rule. | passed |

## Decision Coverage

| Decision | Evidence | Status |
|----------|----------|--------|
| D-01 | `tiaokedan.md` uses `YAML frontmatter + body`. | passed |
| D-02 | Frontmatter fields are exactly `title`, `recipient`, `department`, and `date`. | passed |
| D-03 | The explanatory paragraph remains visible Markdown body text under `## 调课说明`. | passed |
| D-04 | Adjustment rows are a normal Markdown table with exactly the Phase 37 8-column header order. | passed |
| D-05 | Row 1 time cells preserve visible `<br>` line breaks. | passed |
| D-06 | The contract lists title, recipient, reason text, table cells, department, and date as teacher-maintained facts. | passed |
| D-07 | Renderer-only defaults are excluded from `tiaokedan.md`. | passed |
| D-08 | Renderer defaults are documented only in the skill-local reference, not required in the fixture. | passed |
| D-09 | No approval grids, signature boxes, opinion columns, variants, batch fields, or renderer switches were added. | passed |
| D-10 | Required unknown values use the visible inline marker `{{待补充: 说明}}`. | passed |
| D-11 | AI-drafted editable prose may use `{{AI草稿: 说明}}`; the accepted fixture uses concrete Phase 37 facts. | passed |
| D-12 | The contract records that unresolved `{{待补充: ...}}` markers are non-final and Phase 39 will implement non-zero validation failure. | passed |
| D-13 | Accepted blank `备注` cells remain empty because they are optional blank facts. | passed |
| D-14 | The fixture mirrors Phase 37 accepted facts: `调课说明`, `教务处：`, locked paragraph, exact table rows, `电气工程系`, and `2026年6月21日`. | passed |
| D-15 | The fixture is inspectable as plain Markdown without scripts, hidden generated JSON, or sibling skill resources. | passed |
| D-16 | The reference defines fields, required/optional facts, markers, renderer-default boundary, and non-goals without parsing or rendering code. | passed |

## Markdown Fixture Assertions

```text
test -s skills/tiaokedan/templates/tiaokedan.md
PASS

head -1 skills/tiaokedan/templates/tiaokedan.md | rg '^---$'
PASS

rg '^title: 调课说明$|^recipient: 教务处：$|^department: 电气工程系$|^date: 2026年6月21日$' skills/tiaokedan/templates/tiaokedan.md
PASS

rg -F '因我系专职教师周老师需要去企业调研，故需将其3月11日所承担实习课程调整为早班，同时涉及到孙老师老师，具体调整如下：' skills/tiaokedan/templates/tiaokedan.md
PASS

rg -F '| 序号 | 班级 | 课程 | 原上课时间 | 原授课教师 | 调整后上课时间 | 调整后上课教师 | 备注 |' skills/tiaokedan/templates/tiaokedan.md
PASS
```

The fixture is plain Markdown and contains no generated JSON/script dependency.

## Contract Reference Assertions

```text
test -s skills/tiaokedan/references/markdown-contract.md
PASS

rg -F '{{待补充: 说明}}' skills/tiaokedan/references/markdown-contract.md
PASS

rg -F '{{AI草稿: 说明}}' skills/tiaokedan/references/markdown-contract.md
PASS

rg -F 'renderer-owned defaults' skills/tiaokedan/references/markdown-contract.md
PASS

rg -F 'Phase 38 non-goals' skills/tiaokedan/references/markdown-contract.md
PASS
```

## Phase 39/40 Scope Boundary Checks

Phase 38 intentionally did not create renderer/parser/CLI/scripts, generated Typst output, PDF workflow, canonical `skills/tiaokedan/SKILL.md`, runtime adapter notes, README/index/discoverability updates, approval grids, signature boxes, opinion columns, school-specific variants, batch support, or spreadsheet import.

```text
! test -e skills/tiaokedan/SKILL.md
PASS

! test -d skills/tiaokedan/scripts
PASS

! find skills/tiaokedan -maxdepth 3 -type f | rg 'generated|renderer|\.py$|\.js$|\.ts$|\.sh$'
PASS

! git diff --name-only -- README.md docs/directory-spec.md docs/compatibility-matrix.md skills/README.md | rg .
PASS
```

## Notes

- `skills/tiaokedan/templates/tiaokedan.md` keeps `备注` cells blank because Phase 37 accepted facts show genuinely empty optional remarks.
- `skills/tiaokedan/references/markdown-contract.md` intentionally uses English labels `renderer-owned defaults` and `Phase 38 non-goals` for deterministic GSD assertions while keeping the substantive guidance in Chinese.
- Phase 39 remains responsible for implementing parser, renderer, generated Typst comparison, and non-zero missing-field failures.
