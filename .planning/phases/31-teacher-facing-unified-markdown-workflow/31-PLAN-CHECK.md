# Phase 31 Plan Check

**Checked:** 2026-06-15
**Plan:** `31-PLAN.md`
**Result:** Passed

## VERIFICATION PASSED

The Phase 31 plan is executable and matches the user's correction:

- It makes `SKILL.md` start from many teacher source materials, targeted clarification, and one unified editable Markdown.
- It treats `teaching-design-package-full.md` or course-specific `某某某课教学资料.md` as the human-editable source of truth before rendering.
- It bounds scripts to finalized-Markdown validation and delivery rendering.
- It requires a package reference to document the teacher-editable Markdown contract, including YAML metadata boundaries and body-centered evidence extraction.
- It forbids old precise full handoff filenames, old template copying, old skill stitching, and old skills as internal dependencies or parity baselines.
- It explicitly keeps Phase 31 from changing script implementation unless a later execute-phase stops and obtains a scope decision.

## Coverage

| Requirement | Covered In |
|-------------|------------|
| TDPKG-04 | Tasks 1, 2 |
| TDPKG-05 | Tasks 1, 3 |
| TDPKG-06 | Tasks 1, 3, 4 |
| TDPKG-14 | Tasks 1, 4, 5 |

## Required Acceptance Coverage

1. `SKILL.md` main workflow from source materials to clarification to unified Markdown: Tasks 1 and 2.
2. `references/format-and-orchestration.md` or a new reference records the teacher-editable Markdown contract: Task 3.
3. Old precise full handoff filenames absent from Phase 31 docs and teaching-design-package docs: Tasks 3, 4, and 5 verification.
4. No script implementation changes in this phase unless execution later expands scope: Tasks 4 and 5.
5. `git diff --cached --check`: Task 5 verification.

## Checks Applied

- Frontmatter contains phase, plan, type, wave, depends_on, files_modified, autonomous, requirements, and requirements_addressed.
- Every task contains `read_first`, `action`, and `acceptance_criteria`.
- The plan names concrete package docs and avoids modifying `skills/` during this planning command.
- Verification includes teacher-workflow scans, Markdown-contract scans, old handoff filename scans, script-diff checks, and staged diff whitespace checks.
- Phase 32 clean delivery enforcement remains out of scope.

## Residual Risk

Execution still needs to rewrite the live package docs. The plan is intentionally documentation-first and does not require script changes; if execution discovers script behavior contradicts the teacher-facing contract, it must stop for a scope decision before editing scripts.
