---
phase: 24-optional-end-of-term-module-and-package-outputs
plan: 01
subsystem: docs-tooling
tags: [teaching-design-package, end-of-term, manifest, pdf-status, fixtures]
requires:
  - phase: 22
    provides: package-level scheduling contract and fixture evidence
  - phase: 23
    provides: teaching-design-package entry, package checkpoint, split jiaoan outputs, and honest manifest status
provides:
  - Optional end-of-term module ownership and review-gate contract for teaching-design-package
  - Package manifest fields for end_of_term, split_outputs, combined_output, review_markers, and final_ready
  - Helper commands for planning/rendering optional end-of-term module and refreshing combined package status
  - Deterministic fixture expectations for disabled, enabled, blocked-review, and merge-unavailable paths
affects: [phase-25-regression-verification, teaching-design-package, end-of-term-teaching-materials]
tech-stack:
  added: []
  patterns:
    - Optional module orchestration delegates to standalone skill public commands
    - PDF readiness requires actual file evidence
    - Package manifest points to module-owned table/workbook artifacts instead of flattening them
key-files:
  created:
    - test/1.11/teaching-design-package/expected-end-of-term-disabled-manifest.json
    - test/1.11/teaching-design-package/expected-end-of-term-enabled-manifest.json
    - test/1.11/teaching-design-package/expected-end-of-term-blocked-review-manifest.json
    - test/1.11/teaching-design-package/expected-combined-merge-unavailable-manifest.json
  modified:
    - skills/teaching-design-package/SKILL.md
    - skills/teaching-design-package/references/format-and-orchestration.md
    - skills/teaching-design-package/templates/teaching-design-package-full.md
    - skills/teaching-design-package/scripts/teaching-design-package.sh
    - test/1.11/teaching-design-package/expected-manifest.json
    - test/1.11/teaching-design-package/expected-review.md
key-decisions:
  - "Package-level end_of_term support delegates scoring, deterministic tables, workbooks, and module review resolution to end-of-term-teaching-materials."
  - "teaching-design-package.pdf is passed only when the actual combined PDF exists after an explicit merge or compile step."
  - "Enabled end-of-term module readiness is blocked by module-local review markers or review_cleared=false."
patterns-established:
  - "Manifest status vocabulary uses disabled, planned, not_run, passed, failed, missing_compiler, merge_unavailable, and blocked_review."
  - "Expected manifests document fixture states for optional module and combined-output behavior."
requirements-completed: [TDP-10, TDP-11, TDP-12, TDP-13, TDP-14]
duration: 28min
completed: 2026-06-14
---

# Phase 24 Plan 01: Optional End-of-Term Module and Package Outputs Summary

**Optional end-of-term package orchestration with module-owned evidence pointers and honest combined PDF status**

## Performance

- **Duration:** 28 min
- **Started:** 2026-06-13T22:21:00Z
- **Completed:** 2026-06-13T22:49:13Z
- **Tasks:** 5
- **Files modified:** 10

## Accomplishments

- Extended the `teaching-design-package` contract through TDP-14 with optional `end_of_term` behavior, module-owned review gates, table/workbook pointers, and combined output status semantics.
- Added a concise `## 期末材料` handoff and explicit frontmatter fields for `end-of-term-full.md`, `end-of-term-source.json`, `end-of-term-output`, and module `manifest.json`.
- Extended `teaching-design-package.sh` with `plan-end-of-term`, `render-end-of-term`, and `render-package` while preserving `example`, `plan-split`, `render-split`, `manifest`, `info`, and `version`.
- Added deterministic expected manifests for disabled, enabled, blocked-review, and merge-unavailable behavior.

## Task Commits

1. **Task 01: Update package contract** - `1be495d` (docs)
2. **Task 02: Extend checkpoint template** - `c6d43cc` (docs)
3. **Task 03: Extend helper orchestration** - `f7bfbe2` (feat)
4. **Task 04: Add fixture expectations** - `d44b18e` (test)
5. **Task 05: Verification and metadata** - included in plan metadata commit

## Files Created/Modified

- `skills/teaching-design-package/SKILL.md` - concise entry now names optional end-of-term module and combined output behavior.
- `skills/teaching-design-package/references/format-and-orchestration.md` - detailed TDP-10 through TDP-14 contract, artifact pointers, status vocabulary, and failure semantics.
- `skills/teaching-design-package/templates/teaching-design-package-full.md` - end-of-term handoff fields, `## 期末材料`, and output-list pointers.
- `skills/teaching-design-package/scripts/teaching-design-package.sh` - optional module orchestration and manifest status writer.
- `test/1.11/teaching-design-package/expected-*.json` - deterministic expected manifest states.
- `test/1.11/teaching-design-package/expected-review.md` - fixture review expectations updated for Phase 24.

## Decisions Made

- Kept `end-of-term-teaching-materials` as the canonical owner of score calculation, deterministic table artifacts, workbook generation, PDF rendering, and review-marker resolution.
- Treated disabled end-of-term module status as non-failing even when module artifacts are absent.
- Used explicit manifest status evidence instead of claiming readiness when split PDFs, merge tooling, or module review clearance is missing.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Direct `git add` inside sandbox could not create `.git/index.lock`; commits were completed with approved elevated git access.
- `plan-end-of-term` initially failed early on the uncertain-score fixture because the module validation correctly rejects unresolved review markers. The command was adjusted to generate the module Markdown first and record `blocked_review` in the package manifest instead of hiding the blockage.
- The GSD `Skill(...)` code-review and verifier subagent APIs are unavailable in this runtime, so code review was recorded as skipped/non-blocking and phase verification was created from deterministic local checks.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 25 can now verify broad public-command regression and documentation/index discoverability using explicit Phase 24 artifact contracts and fixture states.

---
*Phase: 24-optional-end-of-term-module-and-package-outputs*
*Completed: 2026-06-14*
