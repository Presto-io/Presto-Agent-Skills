---
phase: 36-public-delivery-pdf-merge-and-standalone-regression
plan: 01
subsystem: document-rendering
tags: [teaching-design-package, pdf-merge, typst, pymupdf, standalone-regression]
requires:
  - phase: 35-teaching-design-formal-renderer-and-cross-module-validation
    provides: package-owned formal teaching-design module renderer and cross-module validation
provides:
  - course-name-prefixed 1+1+N public delivery
  - registry-order module PDF staging and merged package PDF generation
  - hidden merge/status/diagnostics evidence and failure semantics
  - standalone-copy success and negative regression evidence
affects: [teaching-design-package, public-delivery, pdf-generation, standalone-install]
tech-stack:
  added: []
  patterns:
    - hidden staging before public publication
    - registry-backed public module PDF filenames
    - honest PDF merge status with pdfunite/qpdf/python_fitz fallback
key-files:
  created:
    - .planning/phases/36-public-delivery-pdf-merge-and-standalone-regression/36-VERIFICATION.md
  modified:
    - skills/teaching-design-package/scripts/package-model.js
    - skills/teaching-design-package/scripts/teaching-design-package.sh
    - skills/teaching-design-package/SKILL.md
    - skills/teaching-design-package/references/format-and-orchestration.md
key-decisions:
  - "Phase 36 public delivery uses course-name-prefixed 1 + 1 + N files; current N=2 yields four public files."
  - "The full package PDF is created only by merging registered module PDFs in module registry order."
  - "Hidden staging and cleanup prevent failed runs from leaving a complete-looking public root."
patterns-established:
  - "Public filenames derive from model.public_delivery and registry metadata, not ad hoc copy branches."
  - "PDF merge status records actual tool, ordered inputs, sizes, output path, exit code, and non-empty result."
requirements-completed: [TDPKG-ART-01, TDPKG-ART-02, TDPKG-ART-03, TDPKG-PDF-01, TDPKG-PDF-02, TDPKG-PDF-03, TDPKG-PDF-04]
duration: 18min
completed: 2026-06-15
---

# Phase 36: Public Delivery, PDF Merge, and Standalone Regression Summary

**Course-name-prefixed teaching-design package delivery with registry-order module PDF merge and standalone failure regression**

## Performance

- **Duration:** 18 min
- **Started:** 2026-06-15T09:05:41Z
- **Completed:** 2026-06-15T09:23:40Z
- **Tasks:** 7
- **Files modified:** 6

## Accomplishments

- Public delivery now publishes exactly `课程名教学资料.md`, `课程名教学资料.pdf`, and one `课程名<模块显示名>.pdf` per registered module.
- `课程名教学资料.pdf` is generated from staged registered module PDFs in registry order: `teaching-plan` then `teaching-design`.
- Status/diagnostics now record module PDF staging paths, input sizes, actual merge tool, merge input order, output size, and failure classes.
- Failure paths for invalid course name, missing/empty module PDF, merge failure, empty merge output, and public leakage exit non-zero and leave no complete public four-file set.
- Standalone-copy verification passes with only `skills/teaching-design-package/`, and standalone negative merge failure exits non-zero.

## Task Commits

1. **Task 1: derive course-name public filenames** - `a4d2ebb`
2. **Tasks 2-5: staging, module PDF compile, merge, failure semantics** - `0b43dd1`
3. **Task 7 docs update** - `8c0814b`
4. **Rule 1 fix: missing course-name diagnostic class** - `ff2aada`
5. **Task 7 verification evidence** - `6086aa4`

## Files Created/Modified

- `skills/teaching-design-package/scripts/package-model.js` - Adds safe course-name filename validation and registry-backed public delivery metadata.
- `skills/teaching-design-package/scripts/teaching-design-package.sh` - Moves publication behind hidden staging, compiles registered module PDFs, merges via pdfunite/qpdf/python_fitz, and records honest status/failure evidence.
- `skills/teaching-design-package/SKILL.md` - Updates teacher-facing output contract to course-name-prefixed `1 + 1 + N`.
- `skills/teaching-design-package/references/format-and-orchestration.md` - Documents hidden artifacts, registry-order merge semantics, fallback merge tools, and standalone boundary.
- `.planning/phases/36-public-delivery-pdf-merge-and-standalone-regression/36-VERIFICATION.md` - Records syntax, success, hidden evidence, negative, standalone, and legacy-boundary verification.

## Decisions Made

- Public output names are derived from `model.metadata.course_name` and registry metadata. Missing, empty, path-like, traversal-like, control-character, and hostile-character course names fail before public success publication.
- The merged package PDF is never direct unified Typst output. Unified Typst remains hidden/debug-only under `.teaching-design-package/work/`.
- The merge fallback order is `pdfunite`, then `qpdf`, then Python PyMuPDF recorded as `python_fitz`.
- Public root cleanup removes expected course-name outputs, old English success filenames, `.typ`, status, manifest, model, diagnostics, calendar JSON, and logs before/after failure paths.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Missing `course_name` used the wrong failure class**
- **Found during:** Task 7 verification
- **Issue:** A missing `course_name` failed as generic `invalid_frontmatter`, but Phase 36 requires invalid filename derivation to report `invalid_course_name_for_filename`.
- **Fix:** Classified missing `course_name` as `invalid_course_name_for_filename` with `missing_course_name` reason.
- **Files modified:** `skills/teaching-design-package/scripts/package-model.js`
- **Verification:** All missing/empty/path/control invalid course-name cases now write `invalid_course_name_for_filename`.
- **Committed in:** `ff2aada`

---

**Total deviations:** 1 auto-fixed bug.
**Impact on plan:** The fix tightened planned failure semantics without expanding scope.

## Issues Encountered

- macOS Bash did not support `mapfile`; the merge helper was changed to a Bash 3-compatible `while read` array population.
- The local environment selected PyMuPDF fallback, so successful merge status records `merge_tool: "python_fitz"`.

## Known Stubs

None. Stub-pattern scan only matched Bash variable initializations and local default variables that do not flow to UI or public delivery output.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 36 closes v1.15 implementation requirements. The package is ready for milestone-level verification or audit, with public delivery, hidden evidence, merge semantics, failure behavior, and standalone-copy regression documented in `36-VERIFICATION.md`.

---
*Phase: 36-public-delivery-pdf-merge-and-standalone-regression*
*Completed: 2026-06-15*

## Self-Check: PASSED

Checked files:

- `skills/teaching-design-package/scripts/package-model.js`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `.planning/phases/36-public-delivery-pdf-merge-and-standalone-regression/36-VERIFICATION.md`
- `.planning/phases/36-public-delivery-pdf-merge-and-standalone-regression/36-SUMMARY.md`

Checked commits:

- `a4d2ebb`
- `0b43dd1`
- `8c0814b`
- `ff2aada`
- `6086aa4`
