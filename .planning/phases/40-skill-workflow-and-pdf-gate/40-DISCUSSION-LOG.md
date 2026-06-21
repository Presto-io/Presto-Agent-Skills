# Phase 40: 调课单 Skill Workflow and PDF Gate - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-22
**Phase:** 40-调课单 Skill Workflow and PDF Gate
**Areas discussed:** Canonical skill entry, PDF workflow, clean output and diagnostics, missing-information questions, runtime adapter notes, README/index/discoverability

---

## Invocation Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Run full interactive question loop | Ask the user to select gray areas and answer four questions per area. | |
| Use commander dispatch as locked discussion input | The user explicitly dispatched this one-shot subagent to run only `/gsd:discuss-phase 40` and named the required Phase 40 areas. | yes |
| Skip Phase 40 context | Leave Phase 40 untouched. | |

**User's choice:** Use commander dispatch as locked discussion input.
**Notes:** The user required covering canonical skill entry, PDF workflow, clean output/diagnostic boundary, missing-info questions, runtime adapters, README/index/discoverability, and TKD-PDF-01 through TKD-PDF-05. The user also prohibited implementation, planning, audit, complete, and direct edits to `skills/tiaokedan/SKILL.md`, README, docs, or PDF workflow files in this command.

---

## Canonical Skill Entry

| Option | Description | Selected |
|--------|-------------|----------|
| Short semantic entry with links | Keep `SKILL.md` concise and link to existing reference/template/script files. | yes |
| Full manual in `SKILL.md` | Duplicate all field contract, renderer details, and diagnostics guidance into the entry. | |
| Runtime-specific entries | Create separate instructions per runtime or wrapper. | |

**User's choice:** Short semantic entry with links.
**Notes:** This follows repository rules and existing `gongwen` / `teaching-design-package` patterns. Runtime-specific behavior belongs in adapter notes, not the canonical body.

---

## PDF Workflow

| Option | Description | Selected |
|--------|-------------|----------|
| Extend existing render command | Add final PDF behavior on top of `tiaokedan.sh render --input --typ`, likely with `--pdf <output.pdf>`. | yes |
| Separate PDF-only command | Add another workflow that bypasses the current Typst render command. | |
| Typst-only success | Treat generated Typst as enough for Phase 40. | |

**User's choice:** Extend existing render command.
**Notes:** Phase 39 already owns the Markdown-to-Typst renderer. Phase 40 should keep that command surface stable and add a strict PDF gate requiring `typst compile` success and a non-empty PDF.

---

## Clean Output And Diagnostics

| Option | Description | Selected |
|--------|-------------|----------|
| Clean public root with hidden/debug diagnostics | Keep successful teacher-facing outputs minimal and move logs/evidence/temp files to hidden or debug-only paths. | yes |
| Emit all evidence beside teacher files | Put diffs, logs, diagnostics, and temporary files in the same output root for transparency. | |
| No diagnostic guidance | Rely on ad hoc stderr only. | |

**User's choice:** Clean public root with hidden/debug diagnostics.
**Notes:** This is required by TKD-PDF-02 and matches the stronger `teaching-design-package` public-root discipline, scaled down for a single-document skill.

---

## Missing-Information Questions

| Option | Description | Selected |
|--------|-------------|----------|
| Concise teacher-language blockers | Ask only about missing required form facts and keep uncertainty visible in Markdown markers. | yes |
| Schema-heavy questionnaire | Ask users to fill all frontmatter/table fields as technical schema values. | |
| Ask renderer defaults too | Ask about fonts, page size, column widths, and diagnostic paths. | |

**User's choice:** Concise teacher-language blockers.
**Notes:** Required facts come from the Phase 38 contract. Blank `备注` is optional; unresolved `{{待补充: ...}}` and `{{AI草稿: ...}}` block final rendering when they appear in required output facts.

---

## Runtime Adapter Notes

| Option | Description | Selected |
|--------|-------------|----------|
| Six-runtime adapter table | Cover Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent in one canonical `SKILL.md` table. | yes |
| Only Codex/Claude notes | Document only the most common runtimes. | |
| Separate adapter files | Add independent runtime adapter files or generated wrappers. | |

**User's choice:** Six-runtime adapter table.
**Notes:** OpenClaw and Hermes Agent remain first-class required runtimes. Notes should emphasize whole-folder support-file preservation, script permissions, `python3`, `typst`, sandbox writes, and hidden diagnostic behavior.

---

## README, Index, And Traceability

| Option | Description | Selected |
|--------|-------------|----------|
| Update repo discovery and requirements traceability | Add `tiaokedan` to README/index docs and close TKD-PDF-01 through TKD-PDF-05 only with verification evidence. | yes |
| Skill-local files only | Leave top-level discovery unchanged. | |
| Mark requirements complete during discussion | Update requirement status before implementation evidence exists. | |

**User's choice:** Update repo discovery and requirements traceability.
**Notes:** README/docs edits are Phase 40 implementation scope, not this discuss command. Requirements should stay pending until the execute/verification phase proves them.

---

## Claude's Discretion

- The downstream planner may choose the exact hidden diagnostics directory shape.
- The downstream planner may decide whether to document PDF/output behavior in `SKILL.md` alone or add a small reference file if the entry would become too heavy.
- The downstream planner may choose direct `--typ/--pdf` output flags or an optional `--out-dir` helper, provided the explicit render command remains usable and public output stays clean.

## Deferred Ideas

- Multiple school-specific `调课单` variants.
- Batch generation.
- Spreadsheet import.
- OCR/photo extraction, arbitrary form discovery, approval grids, signature boxes, opinion columns, and additional approval workflows.
