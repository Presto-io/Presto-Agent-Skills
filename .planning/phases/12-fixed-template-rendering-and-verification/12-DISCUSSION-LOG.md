# Phase 12: Fixed-Template Rendering and Verification - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-09
**Phase:** 12-Fixed-Template Rendering and Verification
**Areas discussed:** Table artifact shape, PDF package shape, fixed template resources, verification and human format validation

---

## Table Artifact Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Workbook only | Fill the fixed `.xlsx` score-book template as the primary table output. | |
| Review artifacts only | Emit deterministic CSV/JSON-style tables for diff and verification, without emphasizing workbook output. | |
| Both workbook and deterministic review artifacts | Produce the fixed workbook for delivery and companion deterministic artifacts for review/verification. | yes |

**User's choice:** 都要。
**Notes:** Phase 12 should keep the workbook as the teacher-facing table deliverable while also emitting deterministic table artifacts suitable for automated checks and review.

---

## PDF Package Shape

| Option | Description | Selected |
|--------|-------------|----------|
| One merged complete package | Generate a single printable PDF package controlled by `package` flags. | yes |
| Separate per-artifact PDFs | Generate one PDF per enabled artifact and let the user combine or print separately. | |
| Both separate and merged | Generate per-artifact PDFs internally or optionally, plus a merged final package. | |

**User's choice:** 一个合并后的完整包。
**Notes:** Intermediate per-artifact files may exist for implementation convenience, but the primary deliverable is the merged complete package.

---

## Fixed Template Resources

| Option | Description | Selected |
|--------|-------------|----------|
| Typst templates only | Add the minimal Typst resources needed to compile the PDF package. | |
| Typst templates plus style docs | Add Typst templates and style references, but leave workbook/docx extraction details external. | |
| Typst templates, style references, xlsx fixture, and docx extraction notes | Keep all fixed-template resources and derivation notes skill-local. | yes |

**User's choice:** Typst 模板、样式参考、xlsx fixture、docx 封面参考的提取说明。
**Notes:** Repository resources should be sanitized and reusable. Real private course files can inform implementation and manual validation but should not be committed as raw sensitive fixtures.

---

## Verification And Human Format Validation

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal automated verification | Validate data, generate Markdown/Typst/PDF, emit tables, and check runtime notes. | |
| Strong automated verification | Add workbook/table smoke checks, deterministic companion artifact checks, PDF compile/package checks, and review-marker blocking. | |
| Automated support plus user format validation | Use automated checks for determinism and completeness, while the user validates final formatting with historical electronic course materials. | yes |

**User's choice:** 我给你以往课程资料，你进行产出，我进行格式验证（以往课程资料是电子版的，你就当作已经提取出来图片上的数据了）。
**Notes:** Historical materials are validation inputs, not an OCR requirement. Phase 12 should treat them as already-extracted structured data and produce artifacts for the user's final format review.

---

## Claude's Discretion

- Planner and executor may choose exact filenames, manifest schema, implementation language, helper libraries, and companion table artifact format, provided the decisions in `12-CONTEXT.md` are preserved.

## Deferred Ideas

- OCR, handwriting/photo recognition, arbitrary template discovery, template marketplace support, and broader export targets remain outside Phase 12.
