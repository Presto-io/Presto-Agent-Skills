---
phase: 40-skill-workflow-and-pdf-gate
plan: 01
subsystem: skill-workflow
tags: [tiaokedan, markdown, typst, pdf, runtime-adapters]

requires:
  - phase: 37-typst-baseline
    provides: accepted hand-authored Typst/PDF form surface
  - phase: 38-markdown-contract
    provides: teacher-readable Markdown contract and missing-marker semantics
  - phase: 39-markdown-to-typst-renderer
    provides: skill-local deterministic Markdown-to-Typst renderer
provides:
  - canonical tiaokedan skill entry with six runtime adapter notes
  - strict PDF gate on the skill-local render command
  - clean output and hidden diagnostics contract
  - missing-information question guide
  - repository discoverability and requirement traceability
affects: [tiaokedan, skills-index, compatibility-matrix, v1.16]

tech-stack:
  added: []
  patterns: [Markdown-first document workflow, skill-local PDF gate, hidden diagnostics]

key-files:
  created:
    - skills/tiaokedan/SKILL.md
    - skills/tiaokedan/references/pdf-workflow.md
    - .planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md
  modified:
    - skills/tiaokedan/scripts/tiaokedan.sh
    - skills/tiaokedan/scripts/tiaokedan_renderer.py
    - README.md
    - skills/README.md
    - docs/directory-spec.md
    - docs/compatibility-matrix.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "PDF success requires real typst compile success and a non-empty PDF."
  - "Production teacher forms do not require --expected-typ comparison to the Phase 37 sample."
  - "Successful public output remains limited to explicitly requested .typ and .pdf files."

patterns-established:
  - "Document skills expose PDF readiness as an explicit final gate after finalized Markdown review."
  - "Single-form workflow questions stay teacher-facing and avoid renderer-owned defaults."

requirements-completed:
  - TKD-PDF-01
  - TKD-PDF-02
  - TKD-PDF-03
  - TKD-PDF-04
  - TKD-PDF-05

duration: 55min
completed: 2026-06-22
---

# Phase 40: 调课单 Skill Workflow and PDF Gate Summary

**`tiaokedan` now has a portable Markdown-first skill entry, strict Typst/PDF final gate, clean output contract, missing-information guide, and repository discoverability.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-06-21T16:58:00Z
- **Completed:** 2026-06-21T17:53:02Z
- **Tasks:** 4
- **Files modified:** 10

## Accomplishments

- Added `skills/tiaokedan/SKILL.md` with teacher workflow, missing-information questions, finalized render/PDF commands, safety rules, and runtime notes for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
- Extended `scripts/tiaokedan.sh render` with `--pdf`, backed by real `typst compile` success and non-empty PDF checks.
- Added `references/pdf-workflow.md` and Phase 40 verification evidence covering clean output, hidden `.tiaokedan/` diagnostics, failure behavior, runtime independence, and traceability.
- Updated README/index/directory/compatibility docs and marked TKD-PDF-01 through TKD-PDF-05 complete.

## Task Commits

1. **Task 2: Extend render command with PDF gate** - `43eacf9` (feat)
2. **Task 1: Add canonical skill entry and PDF workflow reference** - `6b327e0` (docs)
3. **Task 3: Update repository discoverability and requirement traceability** - `25ef4cb` (docs)
4. **Task 4: Record Phase 40 verification evidence** - `eb0f7c9` (docs)

## Files Created/Modified

- `skills/tiaokedan/SKILL.md` - canonical skill entry for the `调课单` workflow.
- `skills/tiaokedan/references/pdf-workflow.md` - PDF gate, clean output, diagnostics, and verification reference.
- `skills/tiaokedan/scripts/tiaokedan.sh` - help text now exposes `--pdf`.
- `skills/tiaokedan/scripts/tiaokedan_renderer.py` - compiles requested PDF with `typst`, verifies non-empty output, and removes incomplete PDFs on failure.
- `README.md` - top-level skill list and structure include `tiaokedan`.
- `skills/README.md` - skill index and artifact contract table include `tiaokedan`.
- `docs/directory-spec.md` - shared references/fixtures section lists `tiaokedan` artifacts.
- `docs/compatibility-matrix.md` - runtime note covers whole-folder install, `python3`, `typst`, and hidden diagnostics.
- `.planning/REQUIREMENTS.md` - TKD-PDF requirements marked complete with Phase 40 traceability.
- `.planning/phases/40-skill-workflow-and-pdf-gate/40-VERIFICATION.md` - full command evidence and scope guard.

## Decisions Made

- Kept `--expected-typ` optional for fixture/evidence; normal teacher PDF generation only needs finalized Markdown, `--typ`, and `--pdf`.
- Documented `.tiaokedan/` as hidden/debug-only diagnostics without making successful default runs create that directory.
- Updated old generic docs wording that matched Phase 40 anti-pattern scans, without changing the underlying v1 no-adapter-files rule.

## Deviations from Plan

None - plan executed exactly as written.

**Total deviations:** 0 auto-fixed.
**Impact on plan:** No scope creep; Phase 37/38/39 accepted templates and contracts were preserved.

## Issues Encountered

- macOS `find` does not support GNU `-printf`; verification used `find ... -exec basename {} \;` instead.
- PDF hashes differed between compile locations, which is acceptable because Phase 40 gates PDF success on compile exit 0 plus non-empty output. Generated Typst remains byte-for-byte deterministic.

## Verification

Key commands passed:

- `python3 -m py_compile skills/tiaokedan/scripts/tiaokedan_renderer.py`
- `skills/tiaokedan/scripts/tiaokedan.sh --help | rg -F -- '--pdf'`
- `skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.typ --expected-typ skills/tiaokedan/templates/tiaokedan-reference.typ`
- `cmp -s .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.typ skills/tiaokedan/templates/tiaokedan-reference.typ`
- `skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf.typ --pdf .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf`
- `test -s .planning/phases/40-skill-workflow-and-pdf-gate/generated/tiaokedan.pdf`
- Success output root contained only `tiaokedan.typ`, `tiaokedan.pdf.typ`, and `tiaokedan.pdf` before failure evidence was generated.
- Invalid fixture with `--pdf` exited non-zero and left no `invalid.pdf`.
- Copied-only `skills/tiaokedan/` render/PDF run passed under `/tmp/tiaokedan-phase40-only`.

## User Setup Required

None - no external service configuration required. PDF generation requires a local `typst` CLI when users request `--pdf`.

## Next Phase Readiness

All Phase 40 requirements are implemented and verified. v1.16 has no remaining planned phases after Phase 40; next workflow should be milestone verification/audit or closeout, not additional Phase 40 implementation.

## Self-Check: PASSED

- `40-VERIFICATION.md` covers TKD-PDF-01 through TKD-PDF-05 and D-01 through D-27.
- Real PDF gate ran with local `typst 0.15.0` and produced a 27288-byte PDF.
- `gsd-sdk query init.execute-phase 40` should report no incomplete plans after this summary is committed.

---
*Phase: 40-skill-workflow-and-pdf-gate*
*Completed: 2026-06-22*
