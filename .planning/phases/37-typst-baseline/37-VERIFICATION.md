# Phase 37 Verification: 调课单 Typst Baseline

**Status:** passed-with-pdf  
**Verified:** 2026-06-21  
**Phase:** 37 — 调课单 Typst Baseline

## Source Paths

| Artifact | Path | Status |
|----------|------|--------|
| Hand-authored Typst reference | `skills/tiaokedan/templates/tiaokedan-reference.typ` | present, non-empty |
| Optional compiled PDF evidence | `skills/tiaokedan/templates/tiaokedan-reference.pdf` | present, non-empty |
| Compile stderr capture | `/tmp/tiaokedan-reference.typst.stderr` | present, contains fallback-font warnings only |

## Requirement Coverage

| Requirement | Evidence | Status |
|-------------|----------|--------|
| TKD-TYP-01 | `skills/tiaokedan/templates/tiaokedan-reference.typ` exists under the new `skills/tiaokedan/templates/` ownership boundary and is hand-authored, not generated. | passed |
| TKD-TYP-02 | The Typst source records the required visible fields, labels, 8-column table structure, two example rows, right-side signature area, and typography/layout declarations. | passed |
| TKD-TYP-03 | `typst compile skills/tiaokedan/templates/tiaokedan-reference.typ skills/tiaokedan/templates/tiaokedan-reference.pdf` exited 0 and produced a 27288-byte PDF. | passed |

## Locked Decision Coverage

| Decision | Evidence | Status |
|----------|----------|--------|
| D-01 | `#set page(paper: "a4", flipped: true)` declares A4 landscape with default page margins. | passed |
| D-02 | Title source is exactly `调课说明`, centered, `FONT_SONG`, `22pt`, `weight: "bold"`, and `#strong[...]`. | passed |
| D-03 | Body/table/signature text use `FONT_FS`, `14pt`, and paragraph justification via `justify: true`. | passed |
| D-04 | Recipient line source is exactly `教务处：` with `indent: 0pt`. | passed |
| D-05 | Explanatory paragraph starts with explicit `#h(2em)` before the locked reason text, producing the accepted two-character first-line visual indent. | passed |
| D-06 | Locked paragraph text appears exactly in the Typst source. | passed |
| D-07 | The table is wrapped in `#block(width: 100%)` to span the text block. | passed |
| D-08 | Table cells use `align: center + horizon`, visible stroke, `FONT_FS`, and `14pt`. | passed |
| D-09 | All 8 headers are present: `序号`, `班级`, `课程`, `原上课时间`, `原授课教师`, `调整后上课时间`, `调整后上课教师`, `备注`. | passed |
| D-10 | Both locked example rows are present; row 1 preserves explicit `#linebreak()` in both time cells. | passed |
| D-11 | A `#v(3.2em)` blank distance separates the table from the closing signature. | passed |
| D-12 | Closing signature source contains exactly `电气工程系` and `2026年6月21日` in `FONT_FS` `14pt`. | passed |
| D-13 | Closing signature is placed in a right-aligned fixed-width block under the table. | passed |

## Compile Evidence

```text
command -v typst
/opt/homebrew/bin/typst

typst --version
typst 0.15.0 (unknown commit)

typst compile skills/tiaokedan/templates/tiaokedan-reference.typ skills/tiaokedan/templates/tiaokedan-reference.pdf 2>/tmp/tiaokedan-reference.typst.stderr
exit code: 0

stat -f%z skills/tiaokedan/templates/tiaokedan-reference.pdf
27288

sed -n '1,220p' /tmp/tiaokedan-reference.typst.stderr
fallback-font warnings only; compile exit code remained 0
```

## Automated Source Assertions

```text
test -d skills/tiaokedan/templates && test -s skills/tiaokedan/templates/tiaokedan-reference.typ
PASS

rg -F '调课说明' skills/tiaokedan/templates/tiaokedan-reference.typ
PASS

rg -F '教务处：' skills/tiaokedan/templates/tiaokedan-reference.typ
PASS

rg -F '因我系专职教师周老师需要去企业调研，故需将其3月11日所承担实习课程调整为早班，同时涉及到孙老师老师，具体调整如下：' skills/tiaokedan/templates/tiaokedan-reference.typ
PASS

for token in 序号 班级 课程 原上课时间 原授课教师 调整后上课时间 调整后上课教师 备注 27WG电气3班 高压电器装配与调试 周老师 孙老师 '14:00-19:00（D104）' '7:30-13:00（D104）' 电气工程系 2026年6月21日; do rg -F "$token" skills/tiaokedan/templates/tiaokedan-reference.typ >/dev/null || exit 1; done
PASS

rg 'paper: *"a4"|flipped: *true|landscape' skills/tiaokedan/templates/tiaokedan-reference.typ
PASS

rg 'SimSun|NSimSun|Songti SC|STSong' skills/tiaokedan/templates/tiaokedan-reference.typ
PASS

rg 'FangSong|STFangsong|FangSong_GB2312|Fangsong SC' skills/tiaokedan/templates/tiaokedan-reference.typ
PASS

rg '22pt|zh\(2\)' skills/tiaokedan/templates/tiaokedan-reference.typ
PASS

rg '14pt|zh\(4\)' skills/tiaokedan/templates/tiaokedan-reference.typ
PASS

rg 'justify|first-line-indent|center \+ horizon' skills/tiaokedan/templates/tiaokedan-reference.typ
PASS

rg -F '#h(2em)因我系专职教师周老师' skills/tiaokedan/templates/tiaokedan-reference.typ
PASS

rg -F '#strong[调课说明]' skills/tiaokedan/templates/tiaokedan-reference.typ
PASS
```

## Scope Boundary Checks

Phase 37 intentionally did not create Markdown fixture/contract/schema/missing markers, Markdown-to-Typst renderer/parser/CLI/scripts, generated-vs-reference diffing, canonical `skills/tiaokedan/SKILL.md`, runtime adapter notes, README/index/discoverability updates, approval grids, signature boxes, opinion columns, or fields beyond the locked signature.

```text
find skills/tiaokedan -maxdepth 3 -type f | sort
skills/tiaokedan/templates/tiaokedan-reference.pdf
skills/tiaokedan/templates/tiaokedan-reference.typ

! test -e skills/tiaokedan/SKILL.md
PASS

! test -d skills/tiaokedan/scripts
PASS

! find skills/tiaokedan -maxdepth 3 -type f | rg '\.(md|py|js|ts|sh)$'
PASS
```

## Notes

- The first compile attempt exposed a Typst syntax issue: `table(width:)` is not valid in Typst 0.15.0. The baseline source was corrected to wrap the table in `#block(width: 100%)[#table(...)]`, preserving the full-width intent.
- After visual review, the explanatory paragraph was corrected from Typst paragraph-indent intent to an explicit `#h(2em)` first-line indent, because the previous source did not produce the required two-character visual indent.
- After visual review, the title was strengthened with `#strong[调课说明]` in addition to `weight: "bold"` and a `Songti SC`-first fallback order, because the previous fallback looked too light in the generated PDF.
- The captured final compile exited 0 and produced a non-empty PDF. Stderr contains only unavailable fallback-font warnings; the source still records same-family fallback intent for downstream portability.
