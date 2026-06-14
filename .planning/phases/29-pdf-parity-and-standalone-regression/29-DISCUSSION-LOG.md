# Phase 29: PDF Parity and Standalone Regression - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-15
**Phase:** 29-pdf-parity-and-standalone-regression
**Areas discussed:** PDF generation path, standalone parity definition, combined PDF verification, derived fact evidence, tool failure handling, artifact staging

---

## PDF Generation Path

| Option | Description | Selected |
|--------|-------------|----------|
| Extend existing package render path | Use Phase 28 `render-package` output, compile split Typst files, then merge accepted PDFs through existing package manifest/merge support. | ✓ |
| Add a separate PDF-only framework | Create a new orchestration layer outside existing package commands. | |
| Treat Typst success as PDF success | Keep PDF slots as status text without compiling files. | |

**User's choice:** The user required real `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf` artifacts.
**Notes:** Phase 29 should prefer the existing public package command surface and honest file-backed manifest statuses.

---

## Standalone Parity Definition

| Option | Description | Selected |
|--------|-------------|----------|
| Compare against standalone render from same generated handoff | Use package-generated `jiaoan-jihua-full.md` and `jiaoan-shicao-full.md` as the same source scope, render them independently through old standalone skills, and compare. | ✓ |
| Compare against unrelated historical fixtures only | Use `test/1.10` as the main parity target even though the source scope differs from the package baseline. | |
| Manual visual inspection only | Open PDFs and rely on human judgment without deterministic evidence. | |

**User's choice:** The user required the plan/lesson PDFs to match old standalone `jiaoan-jihua` and `jiaoan-shicao` outputs for the same source scope, allowing timestamp differences.
**Notes:** Typst diff after volatile-line normalization is the strongest deterministic layer; PDF compile and text/page checks should follow.

---

## Combined PDF Verification

| Option | Description | Selected |
|--------|-------------|----------|
| Merge accepted split PDFs in order | Build `teaching-design-package.pdf` from `teaching-plan.pdf` followed by `lesson-plans.pdf`, then verify content anchors and page-count evidence where possible. | ✓ |
| Generate a separate combined PDF from unrelated source | Compile `teaching-design-package.typ` alone without proving it preserves accepted split outputs. | |
| Placeholder combined status | Mark combined PDF passed when split outputs exist. | |

**User's choice:** The user required a real combined PDF that contains the original teaching-plan and lesson-plan outputs as one merged package.
**Notes:** Existing `pdfunite`/`qpdf` fallback logic is the natural implementation point; missing merge tools must be reported honestly.

---

## Derived Fact Evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Verify facts through provenance, Typst, and PDF text when available | Reconfirm `160H`, `40/60/60H`, three date ranges, and `2025-2026学年第二学期` through Phase 28 provenance and generated outputs. | ✓ |
| Trust Phase 28 only | Do not re-check that facts reached the final PDFs. | |
| Reintroduce facts into package YAML | Add duplicate YAML fields so checks are easier. | |

**User's choice:** The user explicitly listed the Phase 28 derived facts that must appear in PDF evidence.
**Notes:** The package baseline must remain free of forbidden derived/default YAML fields.

---

## Tool Failure Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Fail or mark unavailable with exact evidence | Missing Typst, merge, or PDF inspection tools produce explicit statuses such as `missing_compiler`, `merge_unavailable`, or `failed`. | ✓ |
| Silently skip unavailable tooling | Continue and imply success from partial outputs. | |
| Change templates or retry network automatically | Work around compile failures without user approval. | |

**User's choice:** The user asked how missing tools should fail rather than produce false claims.
**Notes:** Prior repo memory shows Typst preview package downloads may fail offline; exact errors should be reported and not papered over.

---

## Artifact Staging

| Option | Description | Selected |
|--------|-------------|----------|
| Keep generated artifacts in `/tmp` or evidence text | Record commands, paths, hashes/status, and verification excerpts without committing generated PDFs. | ✓ |
| Commit generated deliverables | Stage PDFs and smoke outputs as repository source. | |
| Leave untracked generated files in repo | Generate in `deliverables/` or similar and leave cleanup to later. | |

**User's choice:** The user required only this command's GSD discussion artifacts to be staged/committed.
**Notes:** This discuss command should commit only `29-CONTEXT.md`, `29-DISCUSSION-LOG.md`, and the GSD state session update if produced.

## Claude's Discretion

- Choose exact optional PDF inspection tools during planning based on local availability.
- Prefer `/tmp/tdp-phase29.*` verification layouts.
- Prefer extending existing package commands before adding new public commands.

## Deferred Ideas

- Markdown baseline redesign.
- Replacing standalone `jiaoan-jihua` or `jiaoan-shicao`.
- OCR, arbitrary external import, hosted review, cloud approval, or unrelated document-family expansion.
