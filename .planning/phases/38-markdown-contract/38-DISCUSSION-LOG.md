# Phase 38: 调课单 Markdown Contract - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-21
**Phase:** 38-调课单 Markdown Contract
**Areas discussed:** Markdown 形态, 教师字段边界, 未知值标记, fixture 内容范围

---

## Markdown 形态

| Option | Description | Selected |
|--------|-------------|----------|
| YAML frontmatter + readable body | Use repository document-workflow pattern; metadata carries document-level facts and body carries visible form text/table. | ✓ |
| Body-only Markdown | Simpler, but document-level fields such as title, recipient, department, and date become harder to validate consistently. | |
| Renderer-oriented schema | Easier for a future parser but less teacher-readable and risks leaking implementation details. | |

**User's choice:** Inferred from project contract and v1.16 requirements: keep Phase 38 Markdown teacher-readable and persistent.
**Notes:** The shared Markdown contract explicitly avoids universal metadata fields; `tiaokedan` owns its field list.

---

## 教师字段边界

| Option | Description | Selected |
|--------|-------------|----------|
| Visible facts only | Teachers maintain title, recipient, paragraph, table values, department, and date; renderer owns layout defaults. | ✓ |
| Expose layout controls | Would let users tweak page/table/font details, but violates the goal of no raw Typst and increases review burden. | |
| Hide paragraph/default facts | Would make the fixture shorter, but the explanatory paragraph is a real visible form fact and must be reviewed. | |

**User's choice:** Inferred from TKD-MD-02 and Phase 37 baseline: separate user-maintained facts from renderer-only defaults.
**Notes:** A reference file may describe renderer defaults for implementers, but the Markdown fixture should not require teachers to maintain them.

---

## 未知值标记

| Option | Description | Selected |
|--------|-------------|----------|
| `{{待补充: 说明}}` | Clear teacher-facing marker for required unknown facts; close to existing `{{AI草稿: ...}}` pattern. | ✓ |
| Empty required fields | Too easy to miss during review and ambiguous with accepted blank optional cells. | |
| HTML comments | Hidden from normal Markdown reading and therefore weaker for teacher review. | |

**User's choice:** Inferred from TKD-MD-03 and existing document-skill review-marker conventions.
**Notes:** Empty optional `备注` cells may remain empty; unresolved required markers become Phase 39 validation failures.

---

## fixture 内容范围

| Option | Description | Selected |
|--------|-------------|----------|
| Mirror Phase 37 accepted facts | The fixture contains the same title, recipient, paragraph, table rows, department, and date as the accepted Typst/PDF baseline. | ✓ |
| Demonstrate many variants | Useful later, but would exceed the single accepted form surface for Phase 38. | |
| Add approval/signature grid fields | Rejected by Phase 37 discussion; would change the visible form. | |

**User's choice:** Follow the accepted Phase 37 baseline exactly for the main fixture.
**Notes:** Missing-marker examples can live in contract documentation if needed; they should not dilute the accepted fixture.

---

## Claude's Discretion

- Downstream agents may choose exact fixture/reference filenames under `skills/tiaokedan/templates/` and `skills/tiaokedan/references/`.
- Downstream agents may decide whether the missing-marker example appears in the main contract reference or a short separate snippet, provided TKD-MD-03 is explicit.

## Deferred Ideas

- Renderer implementation and validation failures are Phase 39.
- Canonical skill entry, runtime adapters, PDF workflow, and discoverability are Phase 40.
- School-specific variants, batch generation, and spreadsheet import are future requirements.
