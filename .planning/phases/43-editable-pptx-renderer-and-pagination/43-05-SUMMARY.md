---
phase: 43-editable-pptx-renderer-and-pagination
plan: 05
subsystem: pptx-render-publication
tags: [pptx, descriptors, symlink-race, bounded-errors, media-validation]

requires:
  - phase: 43-04
    provides: Public three-state render command and same-stem Markdown/PPTX publication
provides:
  - Descriptor-bound staged PPTX save, validation, reopen, and replacement lifecycle
  - Symlink-exchange regression proving caller-owned sentinel preservation
  - Allowlisted bounded public mapping for PPTX object and media errors
affects: [43-06-code-fidelity, 44-verification-runtime-uat, school-pptx-public-workflow]

tech-stack:
  added: []
  patterns: [held owner descriptor, duplicated binary stream, allowlisted domain errors]

key-files:
  created: []
  modified:
    - skills/school-pptx/scripts/pptx_render.py
    - skills/school-pptx/scripts/pptx_emit.py
    - skills/school-pptx/scripts/verify_pptx_renderer.py

key-decisions:
  - "PPTX staging keeps an O_RDWR owner descriptor open until the destination context closes; all save and validation reads use duplicated streams for the same inode."
  - "A replaced temporary directory entry is never followed or removed unless it is still the renderer-owned regular inode."
  - "Only allowlisted PptxObjectError codes cross the emitter boundary; all unknown object errors become PPTX_OBJECT_INVALID with generic text."

patterns-established:
  - "Descriptor-bound publication: staged path names are used only for identity checks and descriptor-relative replace, never for package writes or validation reopen."
  - "Bounded object errors: public output exposes stable codes and generic remediation without exception repr, traceback, or internal paths."

requirements-completed: [VER-03]

duration: 20 min
completed: 2026-07-14
---

# Phase 43 Plan 05: Descriptor Publication and Bounded Object Errors Summary

**Staged PPTX publication now remains bound to held file descriptors through save and validation, while malformed media returns short stable public errors without replacing prior output.**

## Performance

- **Duration:** 20 min
- **Started:** 2026-07-14T03:09:05Z
- **Completed:** 2026-07-14T03:28:52Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Kept PPTX owner descriptors open as `O_RDWR`, returned seekable duplicated `w+b` streams, and performed save, fsync, ZIP inspection, and python-pptx reopen without reopening the staged path.
- Added a precise reserve-before-save directory-entry exchange regression that returns `OUTPUT_TEMP_CHANGED`, preserves the external sentinel byte-for-byte, closes both descriptors, and leaves only the attacker-owned symlink.
- Mapped allowlisted media failures to bounded emitter-domain errors and verified GIF and oversized-pixel vectors through the public CLI with outputs below 8 KiB and unchanged prior PPTX bytes.

## Task Commits

Each task was committed atomically:

1. **Task 1: 让 staged PPTX 全生命周期绑定 held descriptor（C-01）** - `376b50d` (fix)
2. **Task 2: 将对象层失败映射为 bounded domain error（W-01）** - `0d635b9` (fix)

## Files Created/Modified

- `skills/school-pptx/scripts/pptx_render.py` - Holds renderer-owned temporary descriptors, duplicates the PPTX stream, verifies inode identity, and safely retains foreign exchanged entries.
- `skills/school-pptx/scripts/pptx_emit.py` - Saves and validates seekable streams and normalizes object errors at the emitter domain boundary.
- `skills/school-pptx/scripts/verify_pptx_renderer.py` - Adds descriptor-race, GIF, oversized-pixel, output-bound, old-target preservation, and publication regression evidence.

## Decisions Made

- Preserved path-based emitter compatibility for existing internal structure gates while requiring the public renderer to use only descriptor streams.
- Allowed an attacker-created replacement symlink to remain because it cannot be safely attributed to the renderer; cleanup only unlinks the original regular inode when its identity still matches.
- Kept public remediation generic and code-driven rather than forwarding media paths or Pillow exception text.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Avoided stream parameter shadowing during relationship validation**
- **Found during:** Task 1 descriptor-only python-pptx reopen gate
- **Issue:** The existing relationship loop reused the validator input name, replacing the binary stream reference with the last relationship source string before reopen.
- **Fix:** Renamed the loop-local relationship source and retained the original descriptor stream for python-pptx reopen.
- **Files modified:** `skills/school-pptx/scripts/pptx_emit.py`
- **Verification:** `publication-descriptor-race` completes descriptor-only save, ZIP validation, and python-pptx reopen.
- **Committed in:** `376b50d`

**2. [Rule 3 - Blocking] Isolated the dependency-absence regression from the positive verification environment**
- **Found during:** Task 2 publication-safety regression
- **Issue:** The existing dependency-negative subprocess inherited the positive `PYTHONPATH`, so it could no longer prove `PPTX_DEPENDENCY_MISSING` while the positive gates used cached local dependencies.
- **Fix:** Restricted that subprocess to the cached YAML-only path, keeping python-pptx absent without installing or downloading anything.
- **Files modified:** `skills/school-pptx/scripts/verify_pptx_renderer.py`
- **Verification:** `publication-safety` passes its dependency, corruption, exchange, collision, and crash-window vectors.
- **Committed in:** `0d635b9`

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking issue). **Impact:** Both fixes were required to exercise the planned descriptor and bounded-error guarantees; no runtime scope or public command surface expanded.

## Issues Encountered

The host Python does not include python-pptx. Verification reused already-present local uv cache packages through `PYTHONPATH`; no network access, package installation, repository virtual environment, or persistent test artifact was created.

## User Setup Required

None - no external service configuration required.

## Verification

- `publication-descriptor-race` - PASS; both descriptors are `O_RDWR` and point to one inode, descriptor-only ZIP/reopen succeeds, sentinel SHA-256 remains `82042068be4a76fb22390d2bd14e077aa738901375ab7b1d49700db09af16867`, and exchanged output returns `OUTPUT_TEMP_CHANGED`.
- `object-error-bounded` - PASS; GIF returns `PPTX_MEDIA_FORMAT_INVALID` in 229 bytes and oversized PNG returns `PPTX_MEDIA_PIXEL_LIMIT` in 213 bytes, without traceback, absolute workdir, Pillow detail, or target replacement.
- `publication-safety` - PASS; staged corruption, dependency absence, output-root exchange, collisions, traversal, identity collision, and Markdown-new/PPTX-old crash-window behavior remain green.
- `python3 -m py_compile skills/school-pptx/scripts/pptx_render.py skills/school-pptx/scripts/pptx_emit.py` - PASS.

## Next Phase Readiness

- C-01 and W-01 are mechanically closed, so Plan 43-06 can focus on authored code-text byte fidelity without reopening publication or public-error boundaries.
- Phase 44 still owns compatible-viewer visual UAT and dependency-readiness documentation.

## Self-Check: PASSED

All modified runtime files exist, both task commits are present, every task and plan-level gate passes, the external sentinel remains byte-identical, public media errors are bounded, and no test artifact persists outside temporary directories.

---
*Phase: 43-editable-pptx-renderer-and-pagination*
*Completed: 2026-07-14*
