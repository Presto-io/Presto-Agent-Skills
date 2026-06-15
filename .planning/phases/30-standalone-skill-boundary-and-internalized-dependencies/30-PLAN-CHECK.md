# Phase 30 Plan Check

**Checked:** 2026-06-15
**Plan:** `30-PLAN.md`
**Result:** Passed after correction

## VERIFICATION PASSED

The corrected Phase 30 plan is executable and satisfies the user's hard boundary correction:

- It forbids copying old standalone Markdown templates into `teaching-design-package`.
- It forbids old-name package internals and old handoff naming.
- It changes the target architecture to unified Markdown -> package-owned data model -> package-owned Typst/PDF rendering.
- It keeps legacy standalone skills as external compatibility surfaces only.
- It requires standalone-copy verification that installs only `teaching-design-package`.

## Coverage

| Requirement | Covered In |
|-------------|------------|
| TDPKG-01 | Tasks 1, 2, 3, 5 |
| TDPKG-02 | Tasks 1, 2, 3, 5 |
| TDPKG-03 | Task 1 |
| TDPKG-15 | Task 4 |

## Decision Coverage

The plan references D-01 through D-17 in `must_haves.truths`, then maps them into documentation cleanup, package-owned model derivation, package-owned rendering, external legacy preservation, and standalone-copy verification.

## Checks Applied

- Frontmatter contains `phase`, `plan`, `type`, `wave`, `depends_on`, `files_modified`, `autonomous`, `requirements`, and `requirements_addressed`.
- Every task contains `read_first`, `action`, and `acceptance_criteria`.
- Actions name concrete files, commands, and target boundaries.
- Verification checks copy only `skills/teaching-design-package/`.
- Verification includes a blocked-token scan for old handoff filenames and old-name internal paths.
- The plan keeps Phase 31 teacher workflow rewrite and Phase 32 clean delivery enforcement out of Phase 30 scope while ensuring Phase 30 no longer points toward old-template vendoring.

## Residual Risk

Execution still needs to replace the current script's old split-handoff implementation. This plan intentionally does not perform that implementation; it only defines the corrected Phase 30 execution target.
