---
phase: 29-pdf-parity-and-standalone-regression
plan: 01
subsystem: teaching-design-package
tags: [pdf, typst, parity, jiaoan, manifest]

requires:
  - phase: 28-markdown-baseline-ingestion-and-typst-generation
    provides: baseline Markdown ingestion, generated jiaoan handoffs, split Typst, package Typst, and derived scheduling provenance
provides:
  - Real `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf` generation through `render-package --pdf`
  - File-backed PDF statuses and same-run stale-file guards in package manifests
  - Same-handoff standalone Typst/PDF parity evidence for `jiaoan-jihua` and `jiaoan-shicao`
  - Derived hour, date, and term evidence in handoffs, Typst, manifest, and PDF text extraction
  - Standalone public interface regression evidence
affects: [teaching-design-package, jiaoan-jihua, jiaoan-shicao, milestone-v1.13]

tech-stack:
  added: []
  patterns: [explicit PDF mode, file-backed manifest statuses, same-handoff parity, PyMuPDF merge fallback]

key-files:
  created:
    - .planning/phases/29-pdf-parity-and-standalone-regression/29-VERIFICATION.md
  modified:
    - skills/teaching-design-package/scripts/teaching-design-package.sh
    - skills/teaching-design-package/SKILL.md
    - skills/teaching-design-package/references/format-and-orchestration.md
    - skills/jiaoan-shicao/scripts/render_v110_typst.awk

key-decisions:
  - "Phase 29 keeps Typst-only rendering as the default and requires explicit `render-package --pdf` for real PDF outputs."
  - "Combined package PDF is built from accepted split PDFs in source order; when `pdfunite` and `qpdf` are unavailable, an installed PyMuPDF merge fallback provides a real merged PDF and records `python_fitz` in the manifest."
  - "Parity is proven against standalone renders from the same generated handoff Markdown, not unrelated fixtures."

patterns-established:
  - "PDF manifest statuses are read from same-run sidecars and only pass when the expected file exists."
  - "Final PDF verification combines Typst parity, PDF file existence, page/text checks, manifest status checks, and forbidden package YAML checks."

requirements-completed: [TDBR-06, TDBR-07, TDBR-08, TDBR-09, TDBR-10, TDBR-11, TDBR-12, TDBR-13, TDBR-14, TDBR-15, TDBR-16, TDBR-17]

duration: 23min
completed: 2026-06-14T20:48:40Z
---

# Phase 29 Plan 01: PDF Parity and Standalone Regression Summary

**Real split and combined teaching-design PDFs with same-handoff standalone parity and derived scheduling evidence**

## Performance

- **Duration:** 23 min
- **Started:** 2026-06-14T20:25:15Z
- **Completed:** 2026-06-14T20:48:40Z
- **Tasks:** 7
- **Files modified:** 5

## Accomplishments

- Added `render-package --pdf` to compile `teaching-plan.pdf` and `lesson-plans.pdf` with Typst and produce `teaching-design-package.pdf` from the accepted split PDFs.
- Made PDF manifest statuses file-backed and same-run, including explicit `missing_compiler`, `failed`, `merge_unavailable`, and tool/reason fields.
- Verified split Typst and PDFs against standalone `jiaoan-jihua` and `jiaoan-shicao` renders from the same generated handoffs.
- Proved the combined PDF contains both halves, has page count `27 = 2 + 25`, and carries required anchors plus derived facts.
- Preserved standalone public command surfaces and kept derived/default values out of package YAML.

## Task Commits

1. **Task 1: Record Phase 29 preflight, local PDF tools, and current gaps** - `d344806` (docs)
2. **Tasks 2-3: Add explicit PDF compilation and combined PDF generation** - `509abc6` (feat)
3. **Tasks 4-5: Verify standalone parity, PDF content, page counts, derived facts, and YAML boundaries** - `48f072d` (fix)
4. **Task 6: Document PDF workflow and preserve standalone public interfaces** - `af3d33d` (docs)
5. **Task 7: Run final Phase 29 verification and close evidence** - `8886ace` (docs)

## Files Created/Modified

- `.planning/phases/29-pdf-parity-and-standalone-regression/29-VERIFICATION.md` - preflight, final PDF/parity evidence, tool availability, derived facts, and requirement traceability.
- `skills/teaching-design-package/scripts/teaching-design-package.sh` - `render-package --pdf`, split PDF compilation, real PDF merge fallback, sidecar-backed manifest status, and stale-file guards.
- `skills/teaching-design-package/SKILL.md` - concise PDF workflow, verification, and safety guidance.
- `skills/teaching-design-package/references/format-and-orchestration.md` - detailed PDF command, tooling, missing-tool, merge, and same-handoff parity semantics.
- `skills/jiaoan-shicao/scripts/render_v110_typst.awk` - task-specific `学习任务分析` hour rendering fix.

## Decisions Made

- Kept `render-package --input --out-dir` as Typst-only behavior and made final PDF generation opt-in with `--pdf`.
- Used installed Python/PyMuPDF only after `pdfunite` and `qpdf` were missing; the manifest records this as `combined_output.reason=python_fitz`.
- Treated PyMuPDF extraction as the PDF inspection path because `pdftotext` and `pdfinfo` were unavailable.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added local PyMuPDF merge fallback**
- **Found during:** Tasks 2-3
- **Issue:** `pdfunite` and `qpdf` were both missing, which would have made the combined PDF acceptance fail despite successful split PDFs.
- **Fix:** Added a no-install fallback that uses the already available `python3` + `fitz` module to insert `teaching-plan.pdf` then `lesson-plans.pdf` into `teaching-design-package.pdf`.
- **Files modified:** `skills/teaching-design-package/scripts/teaching-design-package.sh`, docs, verification.
- **Verification:** Final manifest records `combined_output.status=passed`, `reason=python_fitz`; combined page count is `27 = 2 + 25`.
- **Committed in:** `509abc6`

**2. [Rule 1 - Bug] Fixed lesson-plan task-hour rendering**
- **Found during:** Task 5
- **Issue:** `jiaoan-shicao` rendered each `学习任务分析` table's `课时` cell from total hours `160` instead of per-task `40H/60H/60H`.
- **Fix:** Rendered `TASK_HOURS[i]` in `skills/jiaoan-shicao/scripts/render_v110_typst.awk`.
- **Files modified:** `skills/jiaoan-shicao/scripts/render_v110_typst.awk`
- **Verification:** Post-fix `lesson-plans.typ` has `40H`, `60H`, `60H`; package and standalone lesson PDFs have matching page counts and text hashes.
- **Committed in:** `48f072d`

**Total deviations:** 2 auto-fixed issues.
**Impact on plan:** Both were required to satisfy final PDF acceptance. No package YAML fields were added, no standalone command surface changed, and no generated artifacts were committed.

## Issues Encountered

- `pdftotext` and `pdfinfo` were missing. Verification used PyMuPDF for page counts and text extraction, while explicitly recording missing tool states.
- PDF text extraction inserts spaces inside some Chinese date/term strings. Verification records both exact Typst/manifest/handoff evidence and PDF extracted anchors with normalized spacing.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

v1.13 Phase 29 acceptance is complete: the package renderer produces all three real PDFs, proves same-handoff standalone parity, and records derived scheduling facts without reintroducing defaults into package YAML. The milestone is ready for audit/closeout by the permitted GSD workflow owner.

## Known Stubs

None blocking. `not_run`, `missing_compiler`, `merge_unavailable`, and `failed` strings in source/docs are status vocabulary and preflight evidence, not unimplemented stubs.

## Threat Flags

None. The new PDF merge path only reads same-run local PDF outputs in the requested output directory and writes the combined PDF there.

## Self-Check: PASSED

- Created file exists: `.planning/phases/29-pdf-parity-and-standalone-regression/29-01-SUMMARY.md`
- Commit hashes found: `d344806`, `509abc6`, `48f072d`, `af3d33d`, `8886ace`
- Final artifact paths recorded under `/tmp/tdp-phase29-final.HlT7QC/package/`
- `git diff --check` passed for the summary

---
*Phase: 29-pdf-parity-and-standalone-regression*
*Completed: 2026-06-14T20:48:40Z*
