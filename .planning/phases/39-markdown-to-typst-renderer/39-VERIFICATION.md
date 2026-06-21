# Phase 39 Verification: 调课单 Markdown-to-Typst Renderer

**Status:** passed
**Verified:** 2026-06-21T16:45:59Z
**Phase:** 39 — 调课单 Markdown-to-Typst Renderer

## Source Paths

| Artifact | Path | Status |
|----------|------|--------|
| Skill-local command wrapper | `skills/tiaokedan/scripts/tiaokedan.sh` | present, executable |
| Skill-local renderer module | `skills/tiaokedan/scripts/tiaokedan_renderer.py` | present, Python stdlib only |
| Accepted Markdown fixture | `skills/tiaokedan/templates/tiaokedan.md` | render input |
| Accepted Typst reference | `skills/tiaokedan/templates/tiaokedan-reference.typ` | comparison target |
| Generated Typst evidence | `.planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ` | present, byte-for-byte match |
| Negative fixtures | `.planning/phases/39-markdown-to-typst-renderer/fixtures/*.md` | present |

## Requirement Coverage

| Requirement | Evidence | Status |
|-------------|----------|--------|
| TKD-RENDER-01 | `skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ` writes generated Typst. | passed |
| TKD-RENDER-02 | Runtime code lives under `skills/tiaokedan/scripts/`, imports only Python standard library modules, and passed sibling-path scan plus copied `skills/tiaokedan/`-only execution. | passed |
| TKD-RENDER-03 | `--expected-typ skills/tiaokedan/templates/tiaokedan-reference.typ`, `cmp`, `diff -u`, and matching SHA-256 prove deterministic byte-for-byte comparison. | passed |
| TKD-RENDER-04 | Three phase-local negative fixtures exit non-zero for unresolved required marker, malformed table columns, and unsupported raw Typst. | passed |

## Decision Coverage

| Decision | Evidence | Status |
|----------|----------|--------|
| D-01 | Created `skills/tiaokedan/scripts/tiaokedan.sh` and `skills/tiaokedan/scripts/tiaokedan_renderer.py`; runtime code stays inside `skills/tiaokedan/`. | passed |
| D-02 | Public command supports `render --input <tiaokedan.md> --typ <output.typ> [--expected-typ <reference.typ>]`. | passed |
| D-03 | No `--pdf`, delivery directory, adapter text, manifest/info command, canonical skill workflow text, README/index/discoverability update, or missing-question guidance was added. | passed |
| D-04 | Evidence command uses `skills/tiaokedan/templates/tiaokedan.md` and `skills/tiaokedan/templates/tiaokedan-reference.typ`. | passed |
| D-05 | Renderer validates YAML frontmatter, `## 调课说明`, recipient line, explanatory paragraph, one Markdown adjustment table, and closing department/date text. | passed |
| D-06 | Renderer enforces the locked 8-column order: `序号`, `班级`, `课程`, `原上课时间`, `原授课教师`, `调整后上课时间`, `调整后上课教师`, `备注`. | passed |
| D-07 | Required frontmatter/body/table facts must be non-empty; blank `备注` remains accepted. | passed |
| D-08 | `{{待补充: ...}}` and `{{AI草稿: ...}}` in required output facts fail as unresolved required markers. | passed |
| D-09 | `<br>` is the only allowed inline HTML marker and renders to `#linebreak()`; raw Typst and other HTML tags fail. | passed |
| D-10 | Generated Typst has stable helper declarations, whitespace, row order, and no timestamps, random IDs, absolute paths, or environment comments. | passed |
| D-11 | Accepted fixture matches the reference byte-for-byte; no normalization rule is used. | passed |
| D-12 | Deterministic checks use committed files with `diff -u`, `cmp`, and `shasum -a 256`; PDF compilation is not the Phase 39 gate. | passed |
| D-13 | Renderer refuses to overwrite `--expected-typ` and writes only to explicit `--typ` output paths. | passed |
| D-14 | Missing file/frontmatter/section/table/value markers/raw Typst/unsupported HTML paths produce non-zero errors. | passed |
| D-15 | Error messages name the failing contract area and teacher-facing field where available. | passed |
| D-16 | Negative tests cover missing/unresolved required fact, malformed table, and unsupported syntax. | passed |
| D-17 | Sibling skill path scan and copied-only execution prove no runtime dependency on sibling skill scripts or directories. | passed |
| D-18 | Implementation uses skill-local Bash/Python plus standard platform tools only. | passed |
| D-19 | Verification includes sibling path scan and a copied `skills/tiaokedan/`-only positive render check. | passed |

## Public Command Evidence

```text
test -x skills/tiaokedan/scripts/tiaokedan.sh
PASS

test -s skills/tiaokedan/scripts/tiaokedan_renderer.py
PASS

python3 -m py_compile skills/tiaokedan/scripts/tiaokedan_renderer.py
PASS

skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ --expected-typ skills/tiaokedan/templates/tiaokedan-reference.typ
PASS

test -s .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ
PASS
```

## Deterministic Comparison Evidence

Comparison method: byte-for-byte. No normalized-equivalent rule is used.

```text
cmp -s .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ skills/tiaokedan/templates/tiaokedan-reference.typ
PASS

diff -u skills/tiaokedan/templates/tiaokedan-reference.typ .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ
PASS (no output)

shasum -a 256 skills/tiaokedan/templates/tiaokedan-reference.typ .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ
5165f228124d82faee67471c855ca08242ccecd5728b9fe1c6f2aaf7ac213066  skills/tiaokedan/templates/tiaokedan-reference.typ
5165f228124d82faee67471c855ca08242ccecd5728b9fe1c6f2aaf7ac213066  .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ
```

Generated source assertions:

```text
rg -F '#linebreak()' .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ
PASS

rg -F '调课说明' .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ
PASS

rg -F '电气工程系' .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ
PASS
```

## Negative Failure Evidence

```text
! skills/tiaokedan/scripts/tiaokedan.sh render --input .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-missing-field.md --typ .planning/phases/39-markdown-to-typst-renderer/generated/invalid-missing-field.typ 2>.planning/phases/39-markdown-to-typst-renderer/generated/invalid-missing-field.stderr
PASS
stderr: tiaokedan: unresolved required marker in row 1 原上课时间

! skills/tiaokedan/scripts/tiaokedan.sh render --input .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-table.md --typ .planning/phases/39-markdown-to-typst-renderer/generated/invalid-table.typ 2>.planning/phases/39-markdown-to-typst-renderer/generated/invalid-table.stderr
PASS
stderr: tiaokedan: malformed adjustment table: expected 8 columns, found 7

! skills/tiaokedan/scripts/tiaokedan.sh render --input .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-unsupported.md --typ .planning/phases/39-markdown-to-typst-renderer/generated/invalid-unsupported.typ 2>.planning/phases/39-markdown-to-typst-renderer/generated/invalid-unsupported.stderr
PASS
stderr: tiaokedan: unsupported raw Typst in row 1 原上课时间
```

## Runtime Independence Evidence

```text
! rg 'skills/(gongwen|teaching-design-package|jiaoan-|end-of-term|school-presentation)' skills/tiaokedan/scripts
PASS

rm -rf /tmp/tiaokedan-phase39-only && mkdir -p /tmp/tiaokedan-phase39-only/skills && cp -R skills/tiaokedan /tmp/tiaokedan-phase39-only/skills/tiaokedan && cd /tmp/tiaokedan-phase39-only && skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ /tmp/tiaokedan-only.generated.typ --expected-typ skills/tiaokedan/templates/tiaokedan-reference.typ && test -s /tmp/tiaokedan-only.generated.typ
PASS
```

The copied-only check contains no sibling skill directories and still completes the positive render/comparison path.

## Phase 40 Scope Boundary

Phase 39 intentionally did not modify or create canonical skill entry, README/index/discoverability docs, runtime adapters, PDF workflow, clean delivery directories, manifest/info commands, missing-information question docs, school variants, batch generation, spreadsheet import, approval grids, signature boxes, or opinion columns.

```text
! git diff --name-only -- README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md skills/tiaokedan/SKILL.md | rg .
PASS
```

## Notes

- Byte-for-byte comparison was feasible and is the only accepted comparison mode recorded here.
- The generated Typst evidence is committed despite the phase `generated/` directory being ignored by default, because Phase 39 requires deterministic comparison evidence.
- PDF compilation remains Phase 40 scope and is not used as a Phase 39 completion gate.
