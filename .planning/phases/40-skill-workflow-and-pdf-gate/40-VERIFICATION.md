# Phase 40 Verification: 调课单 Skill Workflow and PDF Gate

**Status:** passed-with-pdf
**Verified:** 2026-06-22
**Phase:** 40 — 调课单 Skill Workflow and PDF Gate

## Source Paths

| Artifact | Path | Status |
|----------|------|--------|
| Canonical skill entry | `skills/tiaokedan/SKILL.md` | present, non-empty |
| Markdown contract | `skills/tiaokedan/references/markdown-contract.md` | present, reused from Phase 38 |
| PDF workflow reference | `skills/tiaokedan/references/pdf-workflow.md` | present, non-empty |
| Public render command | `skills/tiaokedan/scripts/tiaokedan.sh` | present, executable |
| Renderer module | `skills/tiaokedan/scripts/tiaokedan_renderer.py` | present, py_compile passed |
| Teacher Markdown fixture | `skills/tiaokedan/templates/tiaokedan.md` | present |
| Accepted Typst reference | `skills/tiaokedan/templates/tiaokedan-reference.typ` | present |
| Generated Phase 40 PDF evidence | `.planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf` | present, non-empty |

## Requirement Coverage

| Requirement | Evidence | Status |
|-------------|----------|--------|
| TKD-PDF-01 | `scripts/tiaokedan.sh render --input ... --typ ... --pdf ...` ran `typst compile` and produced a non-empty PDF. `references/pdf-workflow.md` documents the Markdown -> Typst -> PDF path. | passed |
| TKD-PDF-02 | Successful public output check confirmed only explicitly requested `.typ` and `.pdf` files before failure diagnostics were generated; failure path left no `invalid.pdf`. | passed |
| TKD-PDF-03 | `skills/tiaokedan/SKILL.md` contains Use When, Teacher Workflow, commands, Verification, Safety, and six Runtime Adapter Notes. | passed |
| TKD-PDF-04 | `skills/tiaokedan/SKILL.md` contains concise missing-information questions for 调课原因、涉及班级和课程、原上课安排、调整后安排、涉及教师、落款部门和日期, with optional 备注 handling. | passed |
| TKD-PDF-05 | `README.md`, `skills/README.md`, `docs/directory-spec.md`, `docs/compatibility-matrix.md`, and `.planning/REQUIREMENTS.md` make `tiaokedan` discoverable and traceable. | passed |

## Decision Coverage

| Decision | Evidence | Status |
|----------|----------|--------|
| D-01 | `skills/tiaokedan/SKILL.md` is the concise semantic entry; long PDF details moved to `references/pdf-workflow.md`. | passed |
| D-02 | `description` targets 调课单/调课说明 adjustment-form work only. | passed |
| D-03 | Teacher Workflow starts from facts, asks only missing/conflicting items, produces `tiaokedan.md`, pauses for review, then renders after finalization. | passed |
| D-04 | `SKILL.md` links `references/markdown-contract.md`, `templates/tiaokedan.md`, `templates/tiaokedan-reference.typ`, and `scripts/tiaokedan.sh`. | passed |
| D-05 | Canonical body is runtime-neutral; runtime differences stay in Runtime Adapter Notes. | passed |
| D-06 | Public command supports `scripts/tiaokedan.sh render --input <tiaokedan.md> --typ <output.typ> --pdf <output.pdf>`. | passed |
| D-07 | PDF success requires installed `typst`, valid generated Typst, compile exit 0, and non-empty PDF. | passed |
| D-08 | `--expected-typ` remains optional evidence/fixture validation; production PDF command did not require it. | passed |
| D-09 | Missing/failed PDF paths exit non-zero and avoid complete-looking public PDF output; invalid fixture left no `invalid.pdf`. | passed |
| D-10 | Script changes are limited to `--pdf`, help text, and PDF gate behavior; Phase 38 parsing was not broadened. | passed |
| D-11 | Successful public output is minimal: requested `.typ` and `.pdf` only. | passed |
| D-12 | `.tiaokedan/` is documented as hidden/debug-only diagnostics; successful default command does not create root diagnostics. | passed |
| D-13 | Failure path removes/avoids public PDF output when validation fails. | passed |
| D-14 | Verification includes success public-root leakage and invalid `--pdf` failure checks. | passed |
| D-15 | Required facts and per-row fields are listed in `SKILL.md` and preserved in `markdown-contract.md`. | passed |
| D-16 | Missing-information questions use teacher-facing groups. | passed |
| D-17 | Blank `备注` remains allowed and should not be asked unless needed. | passed |
| D-18 | `{{待补充: ...}}` and `{{AI草稿: ...}}` are allowed in drafts but block final Typst/PDF rendering. | passed |
| D-19 | `SKILL.md` says not to ask for renderer-owned defaults. | passed |
| D-20 | Runtime Adapter Notes cover Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent. | passed |
| D-21 | Every runtime row mentions preserving `SKILL.md`, `references/`, `templates/`, and `scripts/`, or the whole skill folder containing them. | passed |
| D-22 | OpenClaw and Hermes Agent notes require verifying frontmatter, support files, script permission, `python3`, `typst`, sandbox writes, and hidden `.tiaokedan/` diagnostics. | passed |
| D-23 | No generated wrappers, runtime-private canonical syntax, or independent adapter files were introduced. | passed |
| D-24 | `README.md` and `skills/README.md` list `tiaokedan`. | passed |
| D-25 | `docs/directory-spec.md` and `docs/compatibility-matrix.md` have concise skill-specific entries without changing the general contract. | passed |
| D-26 | `.planning/REQUIREMENTS.md` marks TKD-PDF-01 through TKD-PDF-05 complete with Phase 40 evidence paths. | passed |
| D-27 | Phase 40 stayed on the single accepted form; future scope remained deferred. | passed |

## Canonical Skill Entry Evidence

```text
test -s skills/tiaokedan/SKILL.md
PASS

rg -F 'description:' skills/tiaokedan/SKILL.md
PASS

rg -F 'references/markdown-contract.md' skills/tiaokedan/SKILL.md
PASS

rg -F 'templates/tiaokedan.md' skills/tiaokedan/SKILL.md
PASS

rg -F 'templates/tiaokedan-reference.typ' skills/tiaokedan/SKILL.md
PASS

rg -F 'scripts/tiaokedan.sh' skills/tiaokedan/SKILL.md
PASS

! rg 'Claude-only|Task\(|AskUserQuestion|mcp__|vscode_askquestions' skills/tiaokedan/SKILL.md
PASS
```

## Missing-Information Question Evidence

```text
for token in '调课原因' '涉及班级和课程' '原上课安排' '调整后安排' '涉及教师' '落款部门和日期' '{{待补充:' '{{AI草稿:'; do
  rg -F "$token" skills/tiaokedan/SKILL.md >/dev/null || exit 1
done
PASS
```

## Runtime Adapter Coverage

```text
for runtime in Codex 'Claude Code' 'Gemini CLI' OpenCode OpenClaw 'Hermes Agent'; do
  rg -F "$runtime" skills/tiaokedan/SKILL.md >/dev/null || exit 1
done
PASS

rg -F 'SKILL.md' skills/tiaokedan/SKILL.md
PASS

rg -F 'references/' skills/tiaokedan/SKILL.md
PASS

rg -F 'templates/' skills/tiaokedan/SKILL.md
PASS

rg -F 'scripts/' skills/tiaokedan/SKILL.md
PASS

rg -F '.tiaokedan' docs/compatibility-matrix.md skills/tiaokedan/SKILL.md
PASS
```

## PDF Command Evidence

```text
command -v typst
/opt/homebrew/bin/typst

typst --version
typst 0.15.0 (unknown commit)

python3 -m py_compile skills/tiaokedan/scripts/tiaokedan_renderer.py
PASS

skills/tiaokedan/scripts/tiaokedan.sh --help | rg -F -- '--pdf'
PASS

rm -rf .planning/phases/40-skill-workflow-and-pdf-gate/generated
mkdir -p .planning/phases/40-skill-workflow-and-pdf-gate/generated
PASS

skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.typ --expected-typ skills/tiaokedan/templates/tiaokedan-reference.typ
PASS

cmp -s .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.typ skills/tiaokedan/templates/tiaokedan-reference.typ
PASS

skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf.typ --pdf .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf
PASS

test -s .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf
PASS

stat -f '%N %z' .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf.typ .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.typ
.planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf 27288
.planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf.typ 2145
.planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.typ 2145
```

## Deterministic Typst Evidence

```text
shasum -a 256 skills/tiaokedan/templates/tiaokedan-reference.typ .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.typ .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf.typ
5165f228124d82faee67471c855ca08242ccecd5728b9fe1c6f2aaf7ac213066  skills/tiaokedan/templates/tiaokedan-reference.typ
5165f228124d82faee67471c855ca08242ccecd5728b9fe1c6f2aaf7ac213066  .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.typ
5165f228124d82faee67471c855ca08242ccecd5728b9fe1c6f2aaf7ac213066  .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf.typ
```

## Clean Output Evidence

The success output directory was checked before running the invalid fixture.

```text
find .planning/phases/40-skill-workflow-and-pdf-gate/generated -maxdepth 1 -type f -exec basename {} \; | sort
tiaokedan.pdf
tiaokedan.pdf.typ
tiaokedan.typ

test "$(find .planning/phases/40-skill-workflow-and-pdf-gate/generated -maxdepth 1 -type f | wc -l | tr -d ' ')" = 3
PASS

! find .planning/phases/40-skill-workflow-and-pdf-gate/generated -maxdepth 1 -type f | rg 'status|manifest|log|stderr|stdout|diff|debug|json|tmp|diagnostic'
PASS
```

## Failure-Path Evidence

```text
! skills/tiaokedan/scripts/tiaokedan.sh render --input .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-missing-field.md --typ .planning/phases/40-skill-workflow-and-pdf-gate/generated/invalid.typ --pdf .planning/phases/40-skill-workflow-and-pdf-gate/generated/invalid.pdf 2>.planning/phases/40-skill-workflow-and-pdf-gate/generated/invalid.stderr
PASS

test ! -e .planning/phases/40-skill-workflow-and-pdf-gate/generated/invalid.pdf
PASS

sed -n '1,20p' .planning/phases/40-skill-workflow-and-pdf-gate/generated/invalid.stderr
tiaokedan: unresolved required marker in row 1 原上课时间

rg 'unresolved required marker|missing required|tiaokedan:' .planning/phases/40-skill-workflow-and-pdf-gate/generated/invalid.stderr
PASS
```

## Repository Discoverability Evidence

```text
rg -F 'tiaokedan' README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md
PASS

rg -F 'templates/tiaokedan.md' skills/README.md README.md
PASS

rg -F 'references/markdown-contract.md' skills/README.md docs/directory-spec.md
PASS

rg -F 'scripts/tiaokedan.sh' skills/README.md docs/directory-spec.md docs/compatibility-matrix.md
PASS

! rg 'generated wrapper|adapter file|Claude-only|OpenClaw.*optional|Hermes Agent.*optional' README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md skills/tiaokedan/SKILL.md
PASS
```

## Requirement Traceability Evidence

```text
for req in TKD-PDF-01 TKD-PDF-02 TKD-PDF-03 TKD-PDF-04 TKD-PDF-05; do
  rg "$req.*Complete|\[x\].*$req" .planning/REQUIREMENTS.md >/dev/null || exit 1
done
PASS

rg -F '.planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md' .planning/REQUIREMENTS.md
PASS
```

## Runtime Independence Evidence

```text
! rg 'skills/(gongwen|teaching-design-package|jiaoan-|end-of-term|school-presentation)' skills/tiaokedan/scripts
PASS

rm -rf /tmp/tiaokedan-phase40-only
mkdir -p /tmp/tiaokedan-phase40-only/skills
cp -R skills/tiaokedan /tmp/tiaokedan-phase40-only/skills/tiaokedan
cd /tmp/tiaokedan-phase40-only
skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ /tmp/tiaokedan-phase40-only/tiaokedan-only.typ --pdf /tmp/tiaokedan-phase40-only/tiaokedan-only.pdf --expected-typ skills/tiaokedan/templates/tiaokedan-reference.typ
test -s /tmp/tiaokedan-phase40-only/tiaokedan-only.pdf
PASS

stat -f '%N %z' /tmp/tiaokedan-phase40-only/tiaokedan-only.typ /tmp/tiaokedan-phase40-only/tiaokedan-only.pdf
/tmp/tiaokedan-phase40-only/tiaokedan-only.typ 2145
/tmp/tiaokedan-phase40-only/tiaokedan-only.pdf 27288
```

The copied-only check contains only the `skills/tiaokedan/` folder and standard platform tools.

## Phase 40 Scope Boundary

No school-specific variants, batch generation, spreadsheet import, OCR/photo extraction, approval grids, signature boxes, opinion columns, generated wrappers, independent runtime adapter files, manifest/info commands, or sibling skill runtime dependencies were introduced.

Accepted Phase 37/38/39 templates and contracts were not redesigned:

- `skills/tiaokedan/templates/tiaokedan.md` unchanged.
- `skills/tiaokedan/templates/tiaokedan-reference.typ` unchanged.
- `skills/tiaokedan/templates/tiaokedan-reference.pdf` unchanged.
- `skills/tiaokedan/references/markdown-contract.md` unchanged.

```text
git diff --name-only -- skills/tiaokedan/templates/tiaokedan.md skills/tiaokedan/templates/tiaokedan-reference.typ skills/tiaokedan/templates/tiaokedan-reference.pdf skills/tiaokedan/references/markdown-contract.md
PASS (no output)
```

## Notes

- The Phase 40 PDF gate uses the installed local `typst` binary and produced a real non-empty PDF.
- PDF SHA-256 may vary between compile runs because the PDF format can include generated metadata; Phase 40 acceptance is compile exit 0 plus non-empty PDF, not byte-for-byte PDF equality.
- Typst source generation remains byte-for-byte deterministic against the Phase 37 reference.

---
*Phase: 40-skill-workflow-and-pdf-gate*
*Verified: 2026-06-22*
