# Phase 39: 调课单 Markdown-to-Typst Renderer - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-22
**Phase:** 39-调课单 Markdown-to-Typst Renderer
**Areas discussed:** Public renderer surface, Markdown parsing and validation, Generated Typst comparison, Failure semantics, Runtime independence

---

## Public Renderer Surface

| Option | Description | Selected |
|--------|-------------|----------|
| Skill-local render command | Add `skills/tiaokedan/scripts/` command that converts finalized Markdown to Typst. | ✓ |
| Reuse sibling renderer command | Call an existing sibling skill script such as `gongwen` for conversion. | |
| Defer command shape | Leave command details entirely for planning. | |

**User's choice:** Inferred from user-provided Phase 39 boundary: implement an independent skill-local renderer, not sibling reuse.
**Notes:** The command should stay minimal for Phase 39: Markdown in, Typst out, optional expected-reference comparison. PDF and canonical skill workflow remain Phase 40.

---

## Markdown Parsing And Validation

| Option | Description | Selected |
|--------|-------------|----------|
| Parse Phase 38 contract narrowly | Support YAML frontmatter, `## 调课说明`, one locked 8-column table, and closing department/date. | ✓ |
| Accept broad Markdown heuristics | Try to infer arbitrary adjustment-form layouts from loose Markdown. | |
| Require raw Typst/layout controls | Ask teachers to include Typst or layout knobs in Markdown. | |

**User's choice:** Inferred from Phase 38 verification and `markdown-contract.md`: teacher-maintained facts only, no raw Typst, no broad form discovery.
**Notes:** The renderer should fail non-zero for missing or malformed required contract areas rather than guessing.

---

## Generated Typst Comparison

| Option | Description | Selected |
|--------|-------------|----------|
| Byte-for-byte reference comparison | Generate Typst that matches `tiaokedan-reference.typ` exactly when feasible. | ✓ |
| Narrow normalized-equivalent comparison | Allow only documented formatting normalization if byte-for-byte is not practical. | ✓ |
| PDF-only comparison | Compile PDF and treat non-empty output as the deterministic renderer check. | |

**User's choice:** Inferred from TKD-RENDER-03 and user boundary: deterministic generated-vs-reference comparison is required; PDF-only evidence is insufficient for Phase 39.
**Notes:** Byte-for-byte comparison is preferred. If normalization is used, Phase 39 verification must document exactly what is ignored.

---

## Failure Semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Strict non-zero failures | Missing required fields, malformed sections, and unsupported values fail with clear stderr. | ✓ |
| Soft warnings | Render partial Typst while warning about unresolved fields. | |
| Ask teacher questions in renderer | Turn missing values into an interactive question workflow. | |

**User's choice:** Explicit in TKD-RENDER-04 and user instruction: missing/malformed/unsupported cases must fail non-zero.
**Notes:** Question guidance belongs to Phase 40; Phase 39 should only enforce the finalized Markdown gate.

---

## Runtime Independence

| Option | Description | Selected |
|--------|-------------|----------|
| Skill-local implementation only | All parser, renderer, and comparison logic lives under `skills/tiaokedan/` or standard tools. | ✓ |
| Runtime dependency on sibling skills | Require sibling skill scripts/directories to be installed. | |
| Shared repo framework extraction | Create a new cross-skill renderer framework now. | |

**User's choice:** Explicit in v1.16 independence discipline and TKD-RENDER-02: no sibling runtime dependency.
**Notes:** Borrowing patterns from existing skills is allowed as implementation inspiration only. Phase 39 should include an independence assertion in verification.

---

## Claude's Discretion

- Planner may choose Bash, Node, or Python for the narrow skill-local renderer.
- Planner may choose the exact evidence output paths under `.planning/phases/39-markdown-to-typst-renderer/`.
- Planner may choose byte-for-byte comparison or a documented narrow normalization rule, preferring byte-for-byte if feasible.

## Deferred Ideas

- Phase 40: canonical `SKILL.md`, runtime adapter notes, PDF workflow, clean output/diagnostic boundary, missing-information question list, README/index updates.
- Future: school-specific variants, batch generation, spreadsheet import, OCR/photo extraction, approval grids, signature boxes, opinion columns, arbitrary form discovery.
