# Phase 32 Plan Check

**Checked:** 2026-06-15
**Plan:** `32-PLAN.md`
**Result:** Passed

## VERIFICATION PASSED

The Phase 32 plan is executable and matches the user's acceptance criteria:

- It defines a strict public delivery directory versus hidden package-owned work/debug/failure diagnostics.
- It requires default successful delivery to contain exactly 1+1+3 files: one unified Markdown, one unified Typst, and three PDFs.
- It moves status, manifest, stderr log, model, split Typst, temporary state, and failure evidence out of the public successful root.
- It makes failure semantics explicit: failed PDF generation must preserve diagnostics but cannot masquerade as successful final delivery.
- It requires derived scheduling validation for total hours, `school_year`, `semester`, start/end dates, and date range.
- It requires teaching-plan hours and lesson-plan activity hours to be cross-checked.
- It forbids old precise full handoff filenames and forbids using old standalone skills as package internals, implementation shortcuts, or parity baselines.
- It requires standalone-copy verification with only `skills/teaching-design-package/` installed.

## Coverage

| Requirement | Covered In |
|-------------|------------|
| TDPKG-07 | Tasks 1, 2, 5 |
| TDPKG-08 | Tasks 1, 2, 4, 5 |
| TDPKG-09 | Tasks 1, 2, 5 |
| TDPKG-10 | Task 3 |
| TDPKG-11 | Task 3 |
| TDPKG-12 | Task 3 |
| TDPKG-13 | Task 3 |

## Required Acceptance Coverage

1. Clean public delivery root: Tasks 1, 2, and 5 include exact `find`/`diff` assertions for the five public files.
2. Hidden diagnostics boundary: Tasks 1, 2, and 5 require status, model, stderr, split Typst, and failure diagnostics under `.teaching-design-package/`.
3. Failure/debug behavior: Tasks 1 and 2 require hidden failure evidence and non-final/non-zero behavior when PDFs cannot be fully produced.
4. Scheduling validation: Task 3 includes frontmatter rejection, derived JSON assertions, semester inference checks, date assertions, and mismatch behavior.
5. No legacy regression: Task 4 and verification scans forbid old precise names and normal-path legacy skill dependency matches.
6. Standalone copy: Task 5 requires copying only `skills/teaching-design-package/` and verifying the clean delivery directory from that copy.

## Checks Applied

- Frontmatter contains phase, plan, type, wave, depends_on, files_modified, autonomous, requirements, and requirements_addressed.
- Every task contains `read_first`, `action`, and `acceptance_criteria`.
- Actions use concrete file paths, command names, output filenames, and JSON fields.
- Verification includes public root file-list diff, root pollution scan, hidden diagnostics checks, derived scheduling JSON assertions, rejected derived frontmatter check, autumn semester inference, old-name scans, standalone-copy checks, legacy diff checks, and whitespace checks.
- Plan scope is limited to Phase 32 planning/execution readiness and explicitly excludes execute/audit/complete during this planning command.

## Residual Risk

Execution must adapt the current script carefully because the existing Phase 30/31 implementation still writes `teaching-design-package-status.json` in the public root and uses hidden split Typst files for PDF surfaces. The plan makes that known behavior an explicit implementation target and requires standalone-copy verification before Phase 32 can pass.
