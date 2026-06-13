# Teaching Design Package Fixture Review

## Scope

This fixture covers Phase 23 plus Phase 24 manifest extensions: integrated `teaching-design-package` Markdown checkpoint, `jiaoan-jihua` handoff, `jiaoan-shicao` handoff, optional end-of-term module pointers, and split/combined output status evidence.

## Expected Split Outputs

| Artifact | Expected status | Notes |
|----------|-----------------|-------|
| `teaching-plan.typ` | planned or generated | From `jiaoan-jihua-full.md` through the existing jiaoan-jihua renderer. |
| `lesson-plans.typ` | planned or generated | From `jiaoan-shicao-full.md` through the existing jiaoan-shicao renderer. |
| `teaching-plan.pdf` | PDF status: not_run | PDF compilation is explicit and not claimed by Phase 23 fixture setup. |
| `lesson-plans.pdf` | PDF status: not_run | PDF compilation is explicit and not claimed by Phase 23 fixture setup. |
| `end-of-term-package.pdf` | disabled or not_run | Only required when `modules.end_of_term.enabled: true`. |
| `teaching-design-package.pdf` | failed, merge_unavailable, or not_run | Never passed unless the actual combined PDF file exists after explicit merge/compile. |

## Optional End-of-Term Expectations

| Scenario | Expected status | Notes |
|----------|-----------------|-------|
| Disabled module | `end_of_term.status: disabled` | Missing end-of-term artifacts do not fail the package. |
| Enabled clean module | `end_of_term.status: passed` or `not_run` with artifact pointers | Table/workbook evidence remains in `end-of-term-output/manifest.json` and `tables/`. |
| Enabled unresolved review | `end_of_term.status: blocked_review` | Module-local `## 复核标记` blocks package `final_ready`. |
| Split PDFs without merge tool | `combined_output.status: merge_unavailable` | Successful split artifacts are preserved; `teaching-design-package.pdf` is not claimed passed. |

## Review Markers

Expected review markers: none.

## Boundary

No fixture claims a completed combined package PDF unless the actual `teaching-design-package.pdf` file exists.
