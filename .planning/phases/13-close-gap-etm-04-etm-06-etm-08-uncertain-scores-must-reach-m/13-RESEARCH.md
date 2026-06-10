---
phase: 13-close-gap-etm-04-etm-06-etm-08-uncertain-scores-must-reach-m
research_date: 2026-06-10
status: complete
requirements:
  - ETM-04
  - ETM-06
  - ETM-08
---

# Phase 13 Research: Uncertain Scores Must Reach Markdown Review

## RESEARCH COMPLETE

External research is intentionally skipped. The problem is an integration gap inside the existing `end-of-term-teaching-materials` skill, and the repository already contains the necessary contract, renderer, fixtures, audit evidence, and verification pattern.

## Key Finding

Phase 11 correctly defines uncertain score values such as `87?` as teacher-reviewable data that must be visible in the Markdown intermediate and mirrored in `## 复核标记`. Phase 12 implements the structured-data-to-Markdown pipeline, but `validate_source_data()` rejects any score containing `?` before `generate_markdown()` can emit the reviewable Markdown.

The closure phase should not redesign the data shape. It should preserve the inline `87?` marker and split validation into two explicit modes:

- `export_ready=false`: allow reviewable uncertainty so Markdown can be generated for teacher review.
- `export_ready=true`: block unresolved `?` score values and non-empty review markers before final export readiness.

## Canonical Inputs Read

- `.planning/phases/13-close-gap-etm-04-etm-06-etm-08-uncertain-scores-must-reach-m/13-CONTEXT.md`
- `.planning/v1.7-MILESTONE-AUDIT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/11-end-of-term-data-and-markdown-contract/11-CONTEXT.md`
- `.planning/phases/12-fixed-template-rendering-and-verification/12-CONTEXT.md`
- `.planning/phases/12-fixed-template-rendering-and-verification/12-01-SUMMARY.md`
- `skills/end-of-term-teaching-materials/SKILL.md`
- `skills/end-of-term-teaching-materials/references/data-contract.md`
- `skills/end-of-term-teaching-materials/references/rendering-style.md`
- `skills/end-of-term-teaching-materials/references/scorebook-template-notes.md`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`
- `skills/end-of-term-teaching-materials/scripts/render_package.py`
- `skills/end-of-term-teaching-materials/references/fixtures/end-of-term-source.json`

## Implementation Approach

1. Keep structured uncertain scores as strings such as `87?`; do not introduce nested score objects for this closure slice.
2. Teach source validation to distinguish review-generation mode from final-export mode.
3. Auto-create review markers during Markdown generation when uncertain source scores lack matching `review_markers`.
4. Keep blank score cells blank and do not treat them as automatic review markers.
5. Keep normal `validate`, `render`, and final readiness strict unless the operator chooses an explicit abnormal preview path.
6. Add abnormal preview output that is clearly marked as not final-ready and visually highlights unresolved uncertain cells.
7. Highlight derived `学期成绩` values below 60 in score-book workbook/PDF outputs where that derived field is shown.
8. Extend verification with positive and negative fixtures so the gap cannot regress.
9. Normalize missing GSD audit metadata called out by `.planning/v1.7-MILESTONE-AUDIT.md`.

## Files Likely To Change

- `skills/end-of-term-teaching-materials/scripts/render_package.py`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`
- `skills/end-of-term-teaching-materials/references/fixtures/end-of-term-source-uncertain.json`
- `skills/end-of-term-teaching-materials/SKILL.md`
- `skills/end-of-term-teaching-materials/references/data-contract.md`
- `skills/end-of-term-teaching-materials/references/rendering-style.md`
- `skills/end-of-term-teaching-materials/references/scorebook-template-notes.md`
- `.planning/phases/11-end-of-term-data-and-markdown-contract/11-VERIFICATION.md`
- `.planning/phases/12-fixed-template-rendering-and-verification/12-01-SUMMARY.md`
- `.planning/phases/13-close-gap-etm-04-etm-06-etm-08-uncertain-scores-must-reach-m/13-01-SUMMARY.md`
- `.planning/phases/13-close-gap-etm-04-etm-06-etm-08-uncertain-scores-must-reach-m/13-VERIFICATION.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`

## Risks

| Risk | Mitigation |
|------|------------|
| A review Markdown command becomes confused with final export readiness. | Use explicit validation modes and manifest fields such as `final_ready`, `review_cleared`, and `artifact_kind`. |
| Abnormal preview PDF is mistaken for a final submission package. | Require an explicit flag and record abnormal status in manifest and user-facing docs. |
| Auto-created review markers are too vague for the teacher to answer. | Include student, task/field, current value, and reason in every marker. |
| Red highlighting becomes nondeterministic or invisible to verification. | Emit deterministic manifest/table metadata in addition to workbook/PDF styling. |
| Audit metadata work expands into unrelated milestone cleanup. | Limit metadata cleanup to Phase 11 standalone verification, Phase 12 summary frontmatter, and Phase 13 verification. |
