# Phase 26 Research: Package Date Backfill Repair

**Phase:** 26 - Package Date Backfill Repair
**Researched:** 2026-06-14
**Mode:** Local repository research for `/gsd:plan-phase 26`

## RESEARCH COMPLETE

Phase 26 should be planned as a narrow package-orchestration repair. No external web research is needed. The relevant behavior is locked by the Phase 26 context, v1.12 requirements, existing `teaching-design-package` script/template contracts, the shared scheduling contract, and the `jiaoan-shicao` Markdown-to-Typst handoff.

## Sources Read

- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/26-package-date-backfill-repair/26-CONTEXT.md`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `references/scheduling-contract.md`
- `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md`
- `skills/jiaoan-shicao/references/format-and-rendering.md`
- `skills/jiaoan-shicao/scripts/render_v110_typst.awk`
- `test/1.11/teaching-design-package/fixture-source.md`
- `test/1.11/teaching-design-package/expected-review.md`
- `.planning/phases/25-regression-verification-and-documentation-index/25-VERIFICATION.md`

## Current Failure Shape

`skills/teaching-design-package/scripts/teaching-design-package.sh` already validates that package Markdown contains `## 调度证据` and `## 实操教案`. However, `write_shicao_scaffold "$package_md" "$out"` currently copies `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md` unchanged. That template contains blank `起止日期：` lines, and `skills/jiaoan-shicao/scripts/render_v110_typst.awk` reads those lines directly into `TASK_DATE`.

The package template already has concrete evidence rows such as:

- `task:1/stage:1/row:1` with `2026-05-11 - 2026-05-11`
- `task:1/stage:1/row:2` with `2026-05-11 - 2026-05-11`
- `task:1/stage:3/row:2` with `2026-05-12 - 2026-05-12`
- `lesson:1/activity:1` with `2026-05-11 - 2026-05-11`

The package `## 实操教案` learning-task analysis also says `起止日期：由 \`task:1/*\` 调度证据推导，缺失时写入复核标记。`, which gives the package handoff a concrete and reviewable fallback source.

## Repair Point

The narrow repair point is `write_shicao_scaffold()` in `skills/teaching-design-package/scripts/teaching-design-package.sh`.

Recommended shape:

1. Keep copying or deriving from the existing `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md`.
2. Add package-local helper logic that isolates the `## 调度证据` table.
3. Extract only concrete ranges matching `YYYY-MM-DD - YYYY-MM-DD`.
4. Preserve source pointers such as `lesson:*` and `task:*` in the helper data flow or verification evidence.
5. Fill only blank lines that are exactly `起止日期：`.
6. Prefer direct `lesson:*` evidence when it can be tied to lesson activity pointers.
7. For the current package example, aggregate concrete `task:1/` rows into an earliest-start/latest-end range only because `## 实操教案` explicitly says the date derives from `task:1/*`.
8. Leave the field blank or review-needed when evidence is missing, non-concrete, conflicting, or blocked by unresolved review markers.

This keeps Phase 26 inside package orchestration and avoids changing standalone `jiaoan-shicao` or `jiaoan-jihua` command behavior.

## Review and Manifest Constraints

`review_marker_state()` already reads package-level `## 复核标记`, and `write_manifest()` derives `final_ready` from review markers plus actual PDF/combined output evidence. Phase 26 should preserve this behavior. Filling a date in `jiaoan-shicao-full.md` must not clear package or module review markers, and must not make `final_ready` true unless existing manifest gates already allow it.

`references/scheduling-contract.md` requires missing, uncertain, conflicting, or exhausted schedule inputs to become visible review evidence. The implementation should therefore reject loose date guesses and record unresolved cases rather than inventing dates.

## Verification Strategy

Use black-box package commands and temporary output directories:

- `example` to produce package Markdown.
- `plan-split` to produce `jiaoan-shicao-full.md`.
- an `awk` assertion proving at least one filled `起止日期：YYYY-MM-DD - YYYY-MM-DD` and no blank `起止日期：` lines in the generated handoff for the package example.
- `render-split` to prove `lesson-plans.typ` receives the date through the existing `jiaoan-shicao` renderer.
- `typst compile` only if available; otherwise record `missing_compiler`. PDF success must require actual PDF files.
- manifest and review-marker checks to prove unresolved review gates remain honest.

Generated outputs should stay in `/tmp` or explicit phase evidence. Do not stage or commit `deliverables/`.

## Planning Recommendation

Use one executable plan with five tasks:

1. Reproduce the blank-date handoff and record pre-fix evidence in `26-VERIFICATION.md`.
2. Add conservative package Markdown date extraction scoped to `## 调度证据`.
3. Backfill blank `起止日期：` in `jiaoan-shicao-full.md` without weakening review gates.
4. Verify package split/render through Markdown and Typst artifacts.
5. Compile PDF evidence honestly or record missing/failed compiler status, then finish TDPR traceability and cleanliness checks.

The plan should cover TDPR-01, TDPR-02, TDPR-03, and TDPR-06. Phase 27 remains responsible for official activity-table width alignment.
