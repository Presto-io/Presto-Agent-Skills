---
phase: 42-markdown-contract-and-full-fixture
plan: 01
subsystem: markdown-validation
tags: [markdown, yaml, parser, validation, diagnostics, school-pptx]

requires:
  - phase: 41-standard-template-and-manifest
    provides: Controlled standard-school PPTX template, manifest layouts, slots, and budgets
provides:
  - Teacher-reviewable school-pptx Markdown authoring contract
  - Manifest-driven source-located logical document parser and aggregate validator
  - Public validate command with deterministic diagnostic JSON
  - Repeatable positive, negative, resource, collision, fence, and Phase 41 regression gate
affects: [42-02-full-fixture, 43-editable-pptx-renderer, 44-verification-runtime-uat]

tech-stack:
  added: []
  patterns: [line-aware constrained Markdown state machine, manifest-owned layout truth, bounded aggregate diagnostics]

key-files:
  created:
    - skills/school-pptx/references/markdown-contract.md
    - skills/school-pptx/scripts/markdown_contract.py
    - skills/school-pptx/scripts/verify_markdown_contract.py
  modified:
    - skills/school-pptx/scripts/school-pptx.sh

key-decisions:
  - "The logical model records 10 authorable layouts and exactly one manifest-owned implicit closing; explicit closing remains invalid."
  - "Phase 43 consumes typed logical blocks, notes, media metadata, and overflow evidence rather than reparsing Markdown."
  - "All fixed resource limits and output collisions fail with bounded diagnostics and no stack trace or source dump."

patterns-established:
  - "Public Markdown parser: explicit frontmatter, slide, notes, fence, heading, and top-level block states with 1-based source locations."
  - "Validation gate: one standard-library harness invokes the public shell command and asserts JSON fields plus subprocess status directly."

requirements-completed: [MD-01, MD-02, MD-03, MD-04, MD-05, MD-07, MD-08]

duration: 47 min
completed: 2026-07-13
---

# Phase 42 Plan 01: Markdown Contract and Logical Validator Summary

**Strict teacher-reviewable Markdown with manifest-driven logical parsing, bounded aggregate diagnostics, and a repeatable public validation gate**

## Performance

- **Duration:** 47 min
- **Started:** 2026-07-13T15:00:05Z
- **Completed:** 2026-07-13T15:47:45Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- Defined the exact ten-field YAML surface, ten explicit layouts plus implicit closing, atomic blocks, notes, media, emphasis, diagnostics, and Phase 43/44 boundaries.
- Implemented a reusable line-aware parser that reads layouts and budgets from the Phase 41 manifest and emits deterministic logical JSON with typed blocks and source locations.
- Added `school-pptx.sh validate` and a single contract gate covering valid ten-layout input, aggregate invalid input, fenced code, collision safety, all resource limits, and Phase 41 regressions.

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the public Markdown and layout semantics contract** - `5c5c59d` (docs)
2. **Task 2: Implement the manifest-driven logical parser and aggregate validator** - `1d4048d` (feat)
3. **Task 3: Wire validate and prove positive, aggregate-negative, and regression behavior** - `a4b51b3` (test)
4. **Task 3 follow-up: Assert all ten explicit layouts in the positive gate** - `9c76b68` (test)

## Files Created/Modified

- `skills/school-pptx/references/markdown-contract.md` - Canonical public YAML, slide, block, layout, notes, media, emphasis, diagnostics, and scope contract.
- `skills/school-pptx/scripts/markdown_contract.py` - Manifest loader, constrained parser, validator, logical JSON serializer, diagnostics, limits, and validate command.
- `skills/school-pptx/scripts/verify_markdown_contract.py` - Standard-library command gate for contract, safety, limits, and Phase 41 regression behavior.
- `skills/school-pptx/scripts/school-pptx.sh` - Thin public validate dispatcher while preserving template-report, info, help, and unknown commands.

## Decisions Made

- Kept authorable layout and budget truth in `standard-school.manifest.yaml`; only contract-owned field names and stable diagnostic codes are constants in the parser.
- Preserved missing-media metadata for a later safe placeholder while retaining a non-zero invalid outcome.
- Kept fenced code opaque so HTML/CSS-like source is preserved without weakening outside-fence style and raw HTML rejection.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Positive harness initially covered only a subset of explicit layouts**
- **Found during:** Plan-level acceptance review after Task 3
- **Issue:** The positive case proved logical fields but did not directly assert all ten authorable layouts required by the acceptance criteria.
- **Fix:** Expanded the valid temporary source to cover cover, contents, section, title-content, two-column, image-text, table, timeline, gallery, and code, then asserted exact JSON coverage plus implicit closing.
- **Files modified:** `skills/school-pptx/scripts/verify_markdown_contract.py`
- **Verification:** `python3 skills/school-pptx/scripts/verify_markdown_contract.py contract`
- **Committed in:** `9c76b68`

---

**Total deviations:** 1 auto-fixed (1 missing critical verification assertion).
**Impact on plan:** Verification became stricter without changing the public contract or expanding into Phase 43/44 scope.

## Issues Encountered

- Execution was interrupted after Task 1; the committed boundary was verified and execution resumed from Task 2 without redoing or losing work.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 42-02 can build the canonical full fixture and deterministic example command on the same validated logical model.
- Phase 43 can consume `parse_document` output directly; no renderer, physical pagination, PPTX notes XML, or runtime adapter work entered this plan.
- No blockers remain.

## Self-Check: PASSED

- Key created files exist and all four `42-01` implementation/test commits are present.
- Every task acceptance gate and the authoritative contract command passed after the final change.
- Requirements copied from the plan frontmatter: MD-01, MD-02, MD-03, MD-04, MD-05, MD-07, MD-08.

---
*Phase: 42-markdown-contract-and-full-fixture*
*Completed: 2026-07-13*
