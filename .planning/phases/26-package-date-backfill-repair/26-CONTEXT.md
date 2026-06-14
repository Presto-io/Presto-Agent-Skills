# Phase 26: Package Date Backfill Repair - Context

**Gathered:** 2026-06-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 26 repairs the `teaching-design-package` package handoff so inferred scheduling evidence from the package Markdown is written into generated `jiaoan-shicao-full.md` before `jiaoan-shicao` rendering. The visible bug is that `## 调度证据` in the package Markdown already contains concrete `起止日期` values, but `skills/teaching-design-package/scripts/teaching-design-package.sh plan-split` currently scaffolds `jiaoan-shicao-full.md` by directly copying `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md`, leaving the lesson-plan `起止日期：` lines blank.

This phase is a post-close v1.11 repair. It must not delete, rename, replace, or broadly redesign `teaching-design-package`, `jiaoan-shicao`, `jiaoan-jihua`, or `end-of-term-teaching-materials`. It must preserve public command surfaces and Markdown-first teacher review, while adding enough regression evidence to prove the package date backfill works.

The user supplied the decisive discussion input before this command: the failure path, expected repair target, no implementation during discussion, no staging/committing untracked `deliverables/`, and the required handoff to planning. No additional product-direction questions remain open.

</domain>

<decisions>
## Implementation Decisions

### Date Backfill Source and Target

- **D-01:** Treat package-level `## 调度证据` as the primary source for backfilled `起止日期` values in `jiaoan-shicao-full.md`. The fix should consume already reviewable package evidence, not invent dates from scratch inside the lesson-plan renderer.
- **D-02:** The immediate target is the generated handoff file `jiaoan-shicao-full.md` under the package output directory. `jiaoan-shicao` should receive a filled Markdown intermediate before rendering; do not rely on Typst renderer-side patching as the main fix.
- **D-03:** Backfill should fill blank `起止日期：` fields when the package evidence can determine a concrete range. The example evidence shows `2026-05-11 - 2026-05-11` in package `## 调度证据` while generated handoff lines remain blank.
- **D-04:** The package helper should preserve the existing template structure and teacher-facing Chinese headings. It may post-process or generate the scaffold, but the resulting handoff must still be valid `jiaoan-shicao-full.md`.

### Reviewability and Ambiguous Evidence

- **D-05:** Backfilled values must remain auditable. Source scheduling rows, source pointers such as `task:...` or `lesson:...`, hour-consumption evidence, and review markers must stay visible in package Markdown or adjacent evidence artifacts.
- **D-06:** If scheduling input is missing, conflicting, uncertain, or exhausted, the implementation should not silently guess. It should keep the `起止日期：` field blank or marked as review-needed and mirror the issue in `## 复核标记` or manifest/status evidence.
- **D-07:** If both task-level and lesson-level evidence exist, planner/researcher should decide the exact precedence, but the safe default is to prefer the most direct lesson-plan source pointer for lesson fragments and fall back to task-level evidence only when the package `## 实操教案` explicitly says the date derives from `task:1/*`.
- **D-08:** Review markers are blocking evidence, not cosmetic text. A generated package must not become `final_ready: true` merely because a blank date was filled elsewhere while unresolved scheduling markers remain.

### Public Interface and Scope Boundaries

- **D-09:** Preserve existing public commands for `teaching-design-package.sh`: `example`, `plan-split`, `render-split`, `plan-end-of-term`, `render-end-of-term`, `render-package`, `manifest`, `info`, and `version`.
- **D-10:** Preserve standalone `jiaoan-shicao` and `jiaoan-jihua` behavior. Phase 26 should fix package orchestration/handoff behavior, not alter standalone renderer semantics unless planning finds a tiny compatibility guard is absolutely required.
- **D-11:** Do not introduce a broad global scheduling library in this repair. Reuse local package evidence and existing contracts first; a shared library belongs to a later milestone if it becomes justified.
- **D-12:** Do not stage or commit generated `deliverables/` artifacts. Verification artifacts may be generated in `/tmp` or phase-local planning evidence, but committed files for this discuss command are limited to Phase 26 discussion/context and necessary planning state.

### Regression Verification Expectations

- **D-13:** Verification must include a black-box package path: generate a package example, run `plan-split` or `render-split`, then assert the produced `jiaoan-shicao-full.md` contains a concrete non-empty `起止日期：...` value.
- **D-14:** Verification should preserve the failure reproduction: before the fix, `plan-split` generates `jiaoan-shicao-full.md` with blank `起止日期：` even though package `## 调度证据` contains concrete date ranges.
- **D-15:** Phase 26 acceptance requires Markdown, Typst, and PDF evidence for the affected package path where feasible. If PDF tooling is unavailable, the result must record explicit status such as `missing_compiler`, `not_run`, or `failed`; it must not claim PDF success without a file.
- **D-16:** Add a focused regression check for TDPR-01/TDPR-02/TDPR-03/TDPR-06 traceability. A simple grep-only check is not enough unless it proves the generated handoff file has filled dates and unresolved review markers are preserved.
- **D-17:** Run `bash -n` for edited shell scripts and run existing package/jiaoan smoke commands after implementation. Generated outputs should go to a temporary directory or a deliberate phase evidence path, not `deliverables/`.

### Claude's Discretion

- Prefer a small, transparent package-script repair over refactoring the renderers.
- Prefer parsing existing package Markdown tables conservatively rather than adding a new hidden data format in this repair.
- If exact multi-task date aggregation is ambiguous, keep the planner focused on the minimum concrete user bug first: package-derived dates must no longer be lost when producing the practical lesson-plan Markdown.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Requirements

- `.planning/ROADMAP.md` — Defines Phase 26 goal, dependencies, success criteria, and TDPR requirement mapping.
- `.planning/REQUIREMENTS.md` — Locks TDPR-01, TDPR-02, TDPR-03, and TDPR-06 for Phase 26; records out-of-scope items such as deleting original skills and staging generated `deliverables/`.
- `.planning/PROJECT.md` — Captures v1.12 post-close repair discipline, Markdown-first package discipline, and regression artifact expectations.
- `.planning/STATE.md` — Records Phase 26 as current position and `/gsd:discuss-phase 26` as next command.
- `AGENTS.md` — Repository language, editing, skill authoring, GSD workflow, and OpenClaw/Hermes requirements.

### Prior Phase Decisions

- `.planning/phases/22-scheduling-contract-and-fixture/22-CONTEXT.md` — Scheduling contract decisions and review-marker discipline.
- `.planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-CONTEXT.md` — Package skill, Markdown checkpoint, jiaoan composition, and split-output decisions.
- `.planning/phases/24-optional-end-of-term-module-and-package-outputs/24-CONTEXT.md` — Manifest truthfulness and final-readiness behavior that should not be regressed.
- `.planning/phases/25-regression-verification-and-documentation-index/25-CONTEXT.md` — Public-command regression and documentation-index expectations carried forward from v1.11.

### Affected Package and Jiaoan Files

- `skills/teaching-design-package/scripts/teaching-design-package.sh` — Current handoff scaffold copies both jiaoan templates; `write_shicao_scaffold` is the likely repair point.
- `skills/teaching-design-package/templates/teaching-design-package-full.md` — Example package Markdown with `## 调度证据` rows containing concrete date ranges and `## 实操教案` text saying dates derive from `task:1/*` evidence.
- `skills/teaching-design-package/references/format-and-orchestration.md` — Package contract for scheduling evidence, jiaoan module handoff, review gates, split outputs, status semantics, and verification details.
- `skills/teaching-design-package/SKILL.md` — Canonical skill entry, runtime adapter notes, safety boundaries, and package workflow.
- `references/scheduling-contract.md` — Shared scheduling model: source-order items, derived dates, hour-consumption evidence, and review marker requirements.
- `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md` — Handoff template currently copied unchanged; contains blank `起止日期：` lines.
- `skills/jiaoan-shicao/references/format-and-rendering.md` — Defines `起止日期：` as part of `## 学习任务分析` for the practical lesson-plan contract.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` — Existing renderer that should receive filled Markdown rather than owning package evidence inference.
- `skills/jiaoan-shicao/scripts/render_v110_typst.awk` — Reads `起止日期：` into `TASK_DATE`, proving that blank Markdown propagates into rendered output.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` — Existing teaching-plan renderer and scheduling evidence precedent; public behavior should remain stable.

### Fixtures and Evidence

- `test/1.11/teaching-design-package/fixture-source.md` — Package fixture with `## 调度证据` rows and `## 实操教案` date derivation text.
- `test/1.11/teaching-design-package/expected-review.md` — Existing v1.11 review expectations for package handoff and split/combined output status.
- `test/1.11/scheduling-contract/expected-schedule.md` — Teacher-facing scheduling evidence pattern with concrete date ranges.
- `test/1.11/scheduling-contract/expected-schedule.json` — Machine-readable scheduling fixture evidence for source pointers and hour consumption.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `write_shicao_scaffold()` in `skills/teaching-design-package/scripts/teaching-design-package.sh` is a narrow repair point. It currently receives both `package_md` and output path but ignores package contents aside from a no-op `frontmatter_value` call.
- `validate_package()` already guarantees `## 调度证据` and `## 实操教案` sections exist before planning split handoffs, so a package-side extractor can rely on those sections being present after validation.
- `review_marker_state()` and manifest review-marker handling already exist in the package script and can be reused or respected when preserving unresolved scheduling evidence.
- `skills/jiaoan-shicao/scripts/render_v110_typst.awk` already consumes `起止日期：` from Markdown. Filling the handoff file is sufficient for the existing renderer to carry dates forward.

### Established Patterns

- Markdown intermediates are the semantic checkpoint. Fixes should make `jiaoan-shicao-full.md` teacher-reviewable and correct before rendering.
- Public shell commands and output filenames are stable contracts; Phase 26 should extend internals without renaming commands, flags, or generated filenames.
- Review markers should be explicit and blocking when data is uncertain; the package should not convert uncertainty into silent success.
- Verification should prefer black-box command behavior from the public scripts over brittle internal-only assertions.

### Integration Points

- `cmd_plan_split` calls `write_shicao_scaffold "$INPUT" "${OUT_DIR}/jiaoan-shicao-full.md"` before writing the manifest. Any backfill should happen before manifest/render evidence is generated.
- `cmd_render_split` calls `cmd_plan_split` and then renders `lesson-plans.typ` from the generated handoff. Fixing `plan-split` automatically affects `render-split`.
- The package template and v1.11 fixture already show the intended date derivation wording, so implementation can add regression tests without inventing a new acceptance fixture.
- TDPR-06 requires package-path Markdown, Typst, and PDF evidence; the existing script can generate Markdown/Typst paths, while PDF status must remain honest if local compilation is unavailable.

</code_context>

<specifics>
## Specific Ideas

- Reproduction command used during discussion:

```bash
tmpdir=$(mktemp -d /tmp/tdp-phase26.XXXXXX)
skills/teaching-design-package/scripts/teaching-design-package.sh example --output "$tmpdir/package.md"
skills/teaching-design-package/scripts/teaching-design-package.sh plan-split --input "$tmpdir/package.md" --out-dir "$tmpdir/out"
rg -n "^起止日期：|调度证据|lesson:1/activity:1|2026-05-11" "$tmpdir/package.md" "$tmpdir/out/jiaoan-shicao-full.md"
```

- Observed result before implementation: package Markdown contains `2026-05-11 - 2026-05-11` rows under `## 调度证据`, while generated `out/jiaoan-shicao-full.md` has blank `起止日期：` lines at template positions.
- A focused acceptance assertion after implementation should fail if every generated `起止日期：` line is empty.
- If multiple learning tasks exist in one generated `jiaoan-shicao-full.md`, planning should decide whether to backfill each blank task date independently or only the package scaffold's first task in the minimum repair. The user-reported bug is satisfied only when relevant practical lesson-plan Markdown dates are no longer blank where package evidence exists.

</specifics>

<deferred>
## Deferred Ideas

- Phase 27 owns official `jiaoan-shicao` `教学活动设计` table-width alignment and official-template evidence.
- Broad scheduling-library extraction, arbitrary source parsing, cloud review workflows, OCR, and template discovery remain out of scope.
- Deleting, replacing, or physically merging original teaching skill directories remains future-only unless explicitly requested.

</deferred>

---

*Phase: 26-Package Date Backfill Repair*
*Context gathered: 2026-06-14*
