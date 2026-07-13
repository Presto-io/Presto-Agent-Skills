---
phase: 42-markdown-contract-and-full-fixture
plan: 03
subsystem: markdown-validation
tags: [markdown, yaml, parser, diagnostics, secure-io, symlink, regression]

requires:
  - phase: 42-markdown-contract-and-full-fixture
    provides: Public Markdown contract, logical validator, canonical full fixture, and deterministic example command from plans 42-01 and 42-02
provides:
  - JSON-safe string-only YAML formatter validation
  - Structurally opaque fenced code and strict complete table/timeline parsing
  - Bounded manifest failures and descriptor-relative no-follow example writes
  - Authoritative five-gap fixture-example registry with capability fail-closed coverage
affects: [43-editable-pptx-renderer, 44-verification-runtime-uat]

tech-stack:
  added: []
  patterns: [composed YAML node validation, fence-aware outer collection, descriptor-relative atomic publish, explicit regression gate registry]

key-files:
  created:
    - .planning/phases/42-markdown-contract-and-full-fixture/42-03-SUMMARY.md
  modified:
    - skills/school-pptx/references/markdown-contract.md
    - skills/school-pptx/scripts/markdown_contract.py
    - skills/school-pptx/scripts/verify_markdown_contract.py

key-decisions:
  - "All ten formatter values must resolve to YAML string scalar nodes before entering the logical model."
  - "The example writer fails closed unless all required no-follow and dir-fd primitives are available."
  - "The output root and media directory remain open by descriptor for the complete five-file operation, with public pathname identity checked before publication and PASS."
  - "fixture-example owns an exact five-gate registry and runs secure-I/O capability failure as a mandatory companion."

patterns-established:
  - "Bounded configuration failure: manifest read, parse, and root-shape failures map to stable diagnostics and parseable invalid JSON."
  - "Race-resistant fixed output: prepare same-directory temporary files and publish only through held no-follow parent descriptors."

requirements-completed: [MD-01, MD-02, MD-03, MD-04, MD-05, MD-06, MD-07, MD-08, VER-01]

duration: 22 min
completed: 2026-07-14
---

# Phase 42 Plan 03: Markdown Contract and Full Fixture Gap Closure Summary

**String-only formatter metadata, opaque code fences, complete tables, bounded manifest diagnostics, and descriptor-confined example publication close all five reproduced Phase 42 gaps.**

## Performance

- **Duration:** 22 min
- **Started:** 2026-07-13T17:54:20Z
- **Completed:** 2026-07-13T18:15:55Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Enforced YAML string-scalar semantics with JSON parity, preserved directive-like fenced code exactly, and rejected malformed or unequal-width table/timeline structures at source rows.
- Mapped missing, malformed, and root-invalid manifests to bounded diagnostics and replaced path-only example writes with capability-gated, descriptor-relative atomic publication.
- Registered all five reproduced gaps under `fixture-example`, retained the secure-I/O capability companion, and preserved every canonical, ownership, resource, collision, and Phase 41 regression.

## Task Commits

Each task was committed atomically:

1. **Task 1: Enforce JSON-safe YAML, opaque fences, and complete table structure** - `c6ae3fe` (fix)
2. **Task 2: Bound manifest failures and remove the example symlink race** - `078873b` (fix)
3. **Task 3: Audit gap-gate registration and run the full fixture-example aggregate** - `83472d7` (test)

## Files Created/Modified

- `skills/school-pptx/references/markdown-contract.md` - States string-only formatter values, opaque fence behavior, and complete equal-width table structure.
- `skills/school-pptx/scripts/markdown_contract.py` - Implements composed-node validation, fence-aware collection, strict tables, bounded manifests, and held-descriptor example publication.
- `skills/school-pptx/scripts/verify_markdown_contract.py` - Adds `gap-parser`, `gap-safety`, five named reproductions, capability failure, deterministic exchanges, and registry completeness auditing.

## Decisions Made

- Rejected implicit YAML types instead of coercing them so the authored contract and logical JSON remain identical and reviewable.
- Required every secure-I/O primitive before creating `--out-dir`; no path-only compatibility fallback is allowed.
- Coordinated exchange tests through an explicit pre-publish hook after temporary preparation, avoiding sleeps and scheduler-dependent races.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Avoided creating `media/` before detecting a root owned-path collision**
- **Found during:** Task 2 fixture-example regression
- **Issue:** The first descriptor-context implementation created an empty `media/` before checking whether `school-pptx-full.md` was occupied by a directory, changing the protected tree on failure.
- **Fix:** Moved repository-source and root-level destination checks ahead of media creation, then checked media destinations only after safely opening that parent.
- **Files modified:** `skills/school-pptx/scripts/markdown_contract.py`
- **Verification:** `gap-safety` and the existing `fixture-example` collision/preservation gate both pass.
- **Committed in:** `078873b`

---

**Total deviations:** 1 auto-fixed bug.
**Impact on plan:** The correction preserves the existing no-mutation-on-failure contract without expanding scope.

## Issues Encountered

- The new exchange gate and legacy example safety gate initially reused `outside-root` in one temporary directory. The registry now runs in an isolated `gap-gates/` subtree; no product behavior changed.

## User Setup Required

None - no external service configuration required.

## Verification

- `python3 -m py_compile skills/school-pptx/scripts/markdown_contract.py skills/school-pptx/scripts/verify_markdown_contract.py` - PASS
- `python3 skills/school-pptx/scripts/verify_markdown_contract.py gap-parser` - PASS
- `python3 skills/school-pptx/scripts/verify_markdown_contract.py gap-safety` - PASS
- `python3 skills/school-pptx/scripts/verify_markdown_contract.py fixture-example` - PASS, including all five gaps, capability fail-closed, both exchange cases, canonical fixture, five-file ownership, determinism, `template-report`, and `info`

## Next Phase Readiness

- Phase 42 plan work is complete and ready for orchestrator-owned phase verification.
- Phase 43 can consume the logical model after that verification; Phase 42 is not marked finally complete by this plan executor.

## Self-Check: PASSED

All key files exist, all three task commits are present, every task acceptance gate passes, and the authoritative aggregate passes.

---
*Phase: 42-markdown-contract-and-full-fixture*
*Completed: 2026-07-14*
