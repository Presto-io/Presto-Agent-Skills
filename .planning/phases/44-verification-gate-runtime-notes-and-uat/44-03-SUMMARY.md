---
phase: 44-verification-gate-runtime-notes-and-uat
plan: 03
subsystem: documentation
tags: [school-pptx, canonical-skill, portability, runtime-adapters, visual-uat]
requires:
  - phase: 44-verification-gate-runtime-notes-and-uat
    provides: fixed public 8/6/21 verification authority and fresh evidence
provides:
  - Concise runtime-neutral canonical school-pptx workflow
  - Renderer, verification, and real-viewer UAT progressive references
  - Six-runtime portability notes with conservative OpenClaw/Hermes installation checks
  - Repository discovery indexes and public documentation-integrity enforcement
affects: [44-04, VER-10, school-pptx, compatibility-matrix, repository-discovery]
tech-stack:
  added: []
  patterns: [canonical semantic entry, progressive disclosure, installation-time runtime verification, documentation integrity gate]
key-files:
  created:
    - skills/school-pptx/SKILL.md
    - skills/school-pptx/references/renderer-and-pagination.md
    - skills/school-pptx/references/verification-contract.md
    - skills/school-pptx/references/visual-uat.md
    - .planning/phases/44-verification-gate-runtime-notes-and-uat/44-03-SUMMARY.md
  modified:
    - skills/school-pptx/scripts/verify_school_pptx.py
    - README.md
    - skills/README.md
    - docs/compatibility-matrix.md
    - docs/directory-spec.md
key-decisions:
  - "The canonical workflow remains runtime-neutral; all runtime paths and discovery caveats live only in one six-row Runtime Adapter Notes table."
  - "Documentation integrity is enforced inside the existing evidence-integrity gate so the fixed top-level eight-gate authority does not drift."
  - "The reusable UAT reference contains only a checklist and acceptance rules; project-specific tester identity, hashes, timestamps, and PASS belong exclusively to planning evidence."
patterns-established:
  - "Long renderer, evidence, negative-case, and UAT contracts are linked from the concise entry rather than duplicated."
  - "OpenClaw and Hermes Agent use installation-time verification language plus an explicit public-script fallback."
requirements-completed: [SKILL-01, SKILL-02, SKILL-04, SKILL-05, SKILL-06]
duration: 17min
completed: 2026-07-15
---

# Phase 44 Plan 03: Canonical Skill and Portability Summary

**A concise review-before-render `school-pptx` entry now links complete renderer/verification/UAT contracts, carries one six-runtime adapter table, and is guarded by the passing public documentation-integrity gate.**

## Performance

- **Duration:** 17 min
- **Started:** 2026-07-15T04:44:16Z
- **Completed:** 2026-07-15T05:01:38Z
- **Tasks:** 3
- **Files modified:** 9 implementation/documentation files

## Accomplishments

- Added the only canonical `school-pptx/SKILL.md` with precise use-when wording, review-before-render, D-17 clarification questions, five literal public commands, clean dual-output rules, safety boundaries, and progressive links.
- Documented frozen editable-object/pagination behavior, exact 8/6/21 verification registries and bounded workdir evidence, plus a reusable 10-item real PowerPoint/WPS UAT checklist that contains no project PASS.
- Covered Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent across whole-folder discovery, explicit fallback, dependencies, external commands, permissions, sandbox/allowlist, and caller workdir ownership.
- Updated root/skill indexes, compatibility guidance, and the minimal fixture/template/planning-UAT ownership gap in the directory specification.
- Wired documentation checks into public `evidence-integrity`; a fresh public verify passed with exact 8/8 registry, zero dynamic skips, and `documentation_integrity: passed`.

## Task Commits

Git metadata is read-only in this environment. Every normal task commit attempt failed while creating `.git/index.lock`; no hash was fabricated and `--no-verify` was not used.

1. **Task 1: Canonical skill and review gate** — `not committed: .git read-only`
2. **Task 2: Verification/UAT references and runtime notes** — `not committed: .git read-only`
3. **Task 3: Repository discovery and documentation integrity** — `not committed: .git read-only`

**Plan metadata:** `not committed: .git read-only`

## Files Created/Modified

- `skills/school-pptx/SKILL.md` - Concise canonical workflow and sole six-runtime adapter notes.
- `skills/school-pptx/references/renderer-and-pagination.md` - Frozen logical-to-physical and editable-object behavior.
- `skills/school-pptx/references/verification-contract.md` - Public workdir, exact registries, bounded evidence, dependencies, freshness, and troubleshooting.
- `skills/school-pptx/references/visual-uat.md` - Real-viewer identity, 10-item checklist, automation prohibition, gap, and sign-off contract.
- `skills/school-pptx/scripts/verify_school_pptx.py` - `docs-entry`/`docs-portability` self-tests and public documentation-integrity enforcement.
- `README.md`, `skills/README.md`, `docs/compatibility-matrix.md` - Canonical discovery and portability indexes.
- `docs/directory-spec.md` - Minimal school-pptx fixture/template and planning-only UAT ownership clarification.

## Decisions Made

- Kept the canonical entry at 102 lines and excluded layout schemas, geometry, fixed registry tables, evidence fields, and UAT item details from its main workflow.
- Reused the existing eighth `evidence-integrity` gate for documentation integrity rather than changing the frozen top-level registry.
- Updated `docs/directory-spec.md` only because its generic rules did not establish ownership for skill-local fixtures or project-specific human UAT evidence.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added missing documentation self-test modes during Task 1**
- **Found during:** Task 1 canonical entry verification
- **Issue:** The plan required `--self-test docs-entry` and `docs-portability`, but the existing verifier exposed neither mode.
- **Fix:** Added focused self-tests, then connected the same contract to public evidence integrity in Task 3.
- **Files modified:** `skills/school-pptx/scripts/verify_school_pptx.py`
- **Verification:** Both self-tests and fresh public verify pass.
- **Committed in:** Not committed (`.git` read-only)

---

**Total deviations:** 1 auto-fixed (1 blocking verification gap).
**Impact on plan:** The fix implements the explicitly planned documentation gate without changing the fixed 8/6/21 registry or renderer behavior.

## Issues Encountered

- `.git/index.lock` cannot be created under the managed read-only Git metadata policy. All work remains unstaged and uncommitted; existing user changes were preserved without reset, checkout, or stash.

## User Setup Required

None - no external service configuration required. Runtime installations must independently verify local dependencies, permissions, and discovery as documented.

## Verification

- `--self-test docs-entry`: PASS
- `--self-test docs-portability`: PASS
- Python `py_compile`: PASS
- Fresh public `verify --workdir`: PASS; 8/8 exact order, zero dynamic skips, documentation integrity PASS
- Repository discovery `rg`: PASS
- `git diff --check`: PASS

## Next Phase Readiness

- Plan 44-04 may prepare hash-bound UAT evidence and must stop for a real Microsoft PowerPoint or WPS Presentation tester.
- No automation has filled viewer identity, timestamp, observations, or PASS; VER-10 and Phase 44 remain pending.

## Self-Check: PASSED

- All three tasks and five listed requirements are complete.
- Canonical/reference/index links exist and public verification consumes their integrity.
- ROADMAP is 3/4 and STATE points to the human-only 44-04 checkpoint.

---
*Phase: 44-verification-gate-runtime-notes-and-uat*
*Completed: 2026-07-15*
