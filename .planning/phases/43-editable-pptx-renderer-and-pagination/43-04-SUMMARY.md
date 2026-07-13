---
phase: 43-editable-pptx-renderer-and-pagination
plan: 04
subsystem: pptx-render-publication
tags: [pptx, cli, best-effort, atomic-replace, descriptor-safety, regression]

requires:
  - phase: 43-03
    provides: Frozen-plan native PPTX emission and staged package validation
provides:
  - Public render command with canonical in-process parsing and same-stem Markdown/PPTX delivery
  - Bounded success, best-effort non-zero, and unrecoverable failure states
  - Held-descriptor Markdown-first/PPTX-last publication with old-PPTX preservation
  - Fixed-order Phase 43 structural, security, determinism, and prior-phase regression aggregate
affects: [44-verification-runtime-uat, school-pptx-public-workflow]

tech-stack:
  added: []
  patterns: [canonical in-process parser, descriptor-confined publication, PPTX-last commit point, semantic package determinism]

key-files:
  created:
    - skills/school-pptx/scripts/pptx_render.py
  modified:
    - skills/school-pptx/scripts/school-pptx.sh
    - skills/school-pptx/scripts/verify_pptx_renderer.py

key-decisions:
  - "Render imports the canonical parse_document path in-process and never serializes a public logical-model sidecar."
  - "Both successful and structurally valid best-effort renders publish Markdown first and PPTX last; only PPTX is the deck-ready commit point."
  - "Best-effort output remains editable and visually unpolluted while the CLI exits non-zero and names affected logical slides."

patterns-established:
  - "Three-state render boundary: success publishes with exit 0, best-effort publishes with non-zero, unrecoverable failure preserves the old PPTX."
  - "Phase aggregate registry: fixed named gates cover contract, pagination, objects, public CLI, failure safety, determinism, and Phase 41/42 regression."

requirements-completed: [PPTX-01, PPTX-02, PPTX-13, VER-03, SKILL-03]

duration: 19 min
completed: 2026-07-14
---

# Phase 43 Plan 04: Safe Render CLI and Publication Summary

**Canonical Markdown now renders through a public three-state CLI into a validated same-stem Markdown/PPTX pair with bounded best-effort reporting and descriptor-confined PPTX-last publication.**

## Performance

- **Duration:** 19 min
- **Started:** 2026-07-13T22:58:19Z
- **Completed:** 2026-07-13T23:17:07Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Added the public `render --input --out-dir [--stem]` dispatcher while preserving the established validate, example, template-report, and info surfaces.
- Implemented canonical in-process parsing, immutable pagination/emission orchestration, byte-preserved Markdown staging, staged PPTX validation, and held-descriptor Markdown-first/PPTX-last publication.
- Added fixed-order gates for successful dual delivery, invalid/missing-media best effort, corruption and dependency failures, symlink/TOCTOU and collision safety, crash-window honesty, semantic determinism, and Phase 41/42 regression.

## Task Commits

Each task was committed atomically:

1. **Task 1: 修订双产物与异常公开契约** - `826d779` (feat)
2. **Task 2: 实现 render 状态机与描述符约束发布** - `152fd7a` (feat)
3. **Task 3: 关闭 Phase 43 结构、安全与回归门** - `b19fbf0` (test)

## Files Created/Modified

- `skills/school-pptx/scripts/pptx_render.py` - Owns the render state machine, canonical parser/paginator/emitter orchestration, bounded summaries, and safe pair publication.
- `skills/school-pptx/scripts/school-pptx.sh` - Exposes the thin public render usage and dispatch while preserving existing commands.
- `skills/school-pptx/scripts/verify_pptx_renderer.py` - Adds public CLI, best-effort, publication safety, determinism, Phase 41/42 regression, and fixed Phase 43 aggregate gates.

## Decisions Made

- Kept the caller's Markdown bytes as the authoritative public source artifact and avoided logical JSON, manifest copies, logs, evidence, or debug files in delivery roots.
- Treated each file replacement as independently atomic and made the observable Markdown-new/PPTX-old crash window an explicit tested contract.
- Compared immutable physical-plan projections and semantic PPTX inventories rather than requiring unstable ZIP-byte equality.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Derived affected logical-slide titles for opener-level parser errors**
- **Found during:** Task 3 (best-effort public regression gate)
- **Issue:** An unknown-layout diagnostic is emitted at the slide opener before the parser attaches the later `##` title, so the first best-effort summary reported the affected slide as `unknown`.
- **Fix:** Mapped source-located diagnostics back to the nearest canonical logical slide when the diagnostic lacks a slide title.
- **Files modified:** `skills/school-pptx/scripts/pptx_render.py`
- **Verification:** The `best-effort` gate now reports `受影响页` for invalid layout input and still publishes a structural non-zero PPTX pair.
- **Committed in:** `b19fbf0`

---

**Total deviations:** 1 auto-fixed (1 bug). **Impact:** The fix improves required public diagnostics without changing parsing, pagination, or publication semantics.

## Issues Encountered

The host Python lacks `python-pptx`; structural and aggregate verification used an isolated temporary Python environment with `python-pptx 1.0.2`, Pillow, and PyYAML. The public renderer itself does not install dependencies and returns the bounded `PPTX_DEPENDENCY_MISSING` state while preserving an existing PPTX.

## User Setup Required

None - no external service configuration required.

## Verification

- `python3 skills/school-pptx/scripts/verify_pptx_renderer.py phase-43` under the isolated dependency environment - PASS; all 14 internal/named gates ran in the fixed aggregate order.
- `cli-publication` - PASS; canonical fixture publishes exactly the command-owned `.md/.pptx` pair, preserves Markdown bytes, and reopens as 24 native-object slides.
- `best-effort` - PASS; missing media and invalid layout publish structural same-name pairs, exit non-zero, name affected slides, and add no warning slide/banner/watermark.
- `publication-safety` - PASS; staged corruption, missing dependencies, root exchange, final symlink/directory collision, traversal, identity collision, and the two-replace crash window fail closed.
- `determinism` and `phase_41_42_regression` - PASS; physical-plan projection hash and semantic package inventory repeat, while template-report and fixture-example remain green.

## Next Phase Readiness

- Phase 43 is complete and the public renderer is ready for Phase 44 dependency readiness, canonical `SKILL.md`, runtime adapters, repository discoverability, aggregate public `verify --workdir`, and manual PowerPoint/WPS UAT.
- Phase 44 visual acceptance remains required for actual CJK wrapping, visual balance, editable group behavior, and cross-viewer theme fidelity.

## Self-Check: PASSED

The created render module exists, all three task commits are present, every task and plan-level gate passes, the canonical dual-artifact contract remains aligned, and Phase 44-only scope remains unimplemented.

---
*Phase: 43-editable-pptx-renderer-and-pagination*
*Completed: 2026-07-14*
