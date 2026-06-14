# Phase 28: Markdown Baseline Ingestion and Typst Generation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-15
**Phase:** 28-Markdown Baseline Ingestion and Typst Generation
**Areas discussed:** Scope boundary, baseline semantic recognition, parser adaptation, package Typst and Phase 29 interface, risks and evidence

---

## Scope Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Adapt renderer to corrected Markdown baseline | Consume `skills/teaching-design-package/templates/teaching-design-package-full.md` without changing teacher-facing Markdown. | ✓ |
| Change the Markdown to match the old package parser | Would satisfy existing `validate_package()` shape but violates the user's explicit correction. | |
| Do PDF parity now | Would cross into Phase 29 scope. | |

**User's choice:** Adapt renderer to corrected Markdown baseline.
**Notes:** The user explicitly said this command is only `/gsd:discuss-phase 28`, must not implement code, and must focus on renderer ingestion and Typst generation while preserving the Markdown reference document.

---

## Baseline Semantic Recognition

| Option | Description | Selected |
|--------|-------------|----------|
| Heading-based section slicing | Use existing `# 授课进度计划`, `# 教学设计方案`, `## 学习任务分析`, `## 教学活动设计...`, and `## 学业评价` headings. | ✓ |
| Add hidden machine markers to Markdown | Easier parser anchors, but changes the teacher-facing reference shape. | |
| Treat only first lesson task as package source | Simpler, but drops content and breaks milestone acceptance. | |

**User's choice:** Heading-based section slicing.
**Notes:** Discussion identified the five requested content classes: teaching plan, teaching design plan, learning-task analysis, teaching-activity design, and academic evaluation.

---

## Parser Adaptation

| Option | Description | Selected |
|--------|-------------|----------|
| Section-slicer/internal model | Parse the baseline and generate temporary handoffs or package Typst without mutating the source Markdown. | ✓ |
| Rewrite baseline into old package sections before render | Would create a machine-friendly intermediate but risks making the wrong artifact the maintained source. | |
| Preserve old validation only | Current validation expects old `##` package sections and will likely reject the corrected baseline. | |

**User's choice:** Section-slicer/internal model.
**Notes:** Machine status should move to generated manifest or sidecar evidence, not into the baseline Markdown. Current `validate_package()` is a known risk because it requires old package sections.

---

## Package Typst and Phase 29 Interface

| Option | Description | Selected |
|--------|-------------|----------|
| Generate one package Typst from baseline Markdown and expose split slots | Satisfies Phase 28 while leaving `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf` for Phase 29. | ✓ |
| Maintain Typst manually | Violates the requirement that Typst be generated through the render path. | |
| Claim PDF success from Typst output | Violates existing manifest truthfulness and Phase 29 parity requirements. | |

**User's choice:** Generate one package Typst from baseline Markdown and expose split slots.
**Notes:** The output evidence should connect one Markdown source to one generated Typst and planned PDF slots without pretending PDFs are complete.

---

## Risks and Evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Record risks and verification hooks now | Downstream research/planning can resolve parser shape, command naming, YAML list handling, and Typst composition. | ✓ |
| Decide all implementation mechanics during discussion | Too much implementation detail for discuss-phase and risks premature design. | |
| Ignore old package contract | Would lose useful status/manifest semantics from v1.11-v1.12. | |

**User's choice:** Record risks and verification hooks now.
**Notes:** Recommended evidence includes baseline unchanged check, heading count assertions, generated Typst provenance, split handoff slots, and honest PDF statuses.

---

## Claude's Discretion

- Planner may choose whether to upgrade `render-split`, add a new package Typst command, or introduce an internal helper, as long as public contracts remain clear and the baseline Markdown is unchanged.
- Planner may choose whether combined package Typst wraps split Typst bodies or directly renders from the parsed baseline, as long as Markdown provenance is explicit.

## Deferred Ideas

- Three-PDF generation and standalone parity are deferred to Phase 29.
- Markdown schema redesign, package-only replacement of old jiaoan skills, OCR/import/cloud workflows, and unrelated document families remain out of scope.
