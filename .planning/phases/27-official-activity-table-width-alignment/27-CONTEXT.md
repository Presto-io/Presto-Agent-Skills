# Phase 27: Official Activity Table Width Alignment - Context

**Gathered:** 2026-06-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 27 repairs the standalone `jiaoan-shicao` `教学活动设计` table-width behavior so it follows the official `presto-official-templates/jiaoan-shicao` reference. The bug is layout-specific: generated activity tables currently use the local AWK renderer's per-learning-task width calculation, while the official renderer calculates column specifications per activity-section chapter, where chapters are split by `{pagebreak}` markers.

This phase is a v1.12 post-close repair. It must keep the existing `jiaoan-shicao` public command surface stable, preserve the Markdown-first workflow, and avoid deleting or replacing `teaching-design-package`, `jiaoan-shicao`, `jiaoan-jihua`, or `end-of-term-teaching-materials`. It must also preserve Phase 26's completed package date backfill: generated package `jiaoan-shicao-full.md` must continue to receive concrete `起止日期` values before `jiaoan-shicao` rendering.

The user supplied the decisive discussion input before this command: use the official local snapshots as evidence, compare official Go behavior with current AWK behavior, do not implement during discussion, and carry the resulting context into planning. No additional product-direction questions remain open.

</domain>

<decisions>
## Implementation Decisions

### Official Algorithm Basis

- **D-01:** Treat `/private/tmp/presto-jiaoan-shicao-main.go` as the canonical algorithm reference for Phase 27. Downstream work should reproduce the behavior around `activityTableTotalWidthCM`, `sectionColumnSpecs`, `tableColumnWidthsCM`, and `columnPressures`, rather than inventing a subjective visual tweak.
- **D-02:** Preserve the official activity-table total width of `25.04cm`. Verification must prove generated activity-table column widths sum to `25.04cm` within a small rounding tolerance.
- **D-03:** Preserve the official minimum-width baseline derived from headers with `headerMinWidthCM(metric, bias)`, including the header set `教学活动`, `学习内容`, `学生活动`, `教师活动`, `教学方法与手段`, and `课时分配`.
- **D-04:** Preserve the official pressure weighting shape unless planning finds an exact portability issue in AWK: base weights `0.5, 1.8, 1.6, 1.6, 0.18, 0.06`; pressure scales `0.22, 1.0, 0.95, 0.95, 0.18, 0.05`; initial pressures `1, 1, 1, 1, 0.5, 0.25`.
- **D-05:** The narrow `课时分配` behavior is locked. That column must remain narrower than the main text columns `学习内容`, `学生活动`, and `教师活动`.

### Current AWK Difference to Repair

- **D-06:** The main behavioral mismatch is grouping scope. Official `sectionColumnSpecs(section)` accumulates all tables in a chapter and flushes a shared column spec when a `PageBreak` appears. Current AWK `table_columns_for_task(i)` calculates one spec for the entire learning task and reuses it for every group in that task.
- **D-07:** In official behavior, multiple teaching-activity tables in the same chapter share identical `columns: (...)`. A `{pagebreak}` starts a new chapter and permits recalculation for following tables. Phase 27 should reproduce that chapter-level sharing.
- **D-08:** Current AWK emits each `### 学习环节——学习单元` as a separate Typst table via `emit_activity_group(i, g)`. The repair may keep that table emission shape, but its `columns` argument must come from official-style chapter specs, not from the whole-task calculation.
- **D-09:** Current AWK parser currently skips `{pagebreak}` as ordinary content in activity mode rather than recording a chapter boundary for width calculation. Planning should add a way to track pagebreak/chapter boundaries for activity groups without changing the public Markdown syntax.
- **D-10:** Do not use official Go output as a runtime dependency. The repository requirement remains skill-local shell/AWK rendering; official files are reference evidence and test-oracle material only.

### Scope and Compatibility Boundaries

- **D-11:** Preserve `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` commands and flags: `example`, `render`, `manifest`, `info`, `version`, including existing `--expected-typ` comparison behavior.
- **D-12:** Preserve existing Markdown authoring syntax in `skills/jiaoan-shicao/references/format-and-rendering.md`: `## 教学活动设计`, `### 学习环节——学习单元`, `#### 活动名称`, `##### 课时`, and `{pagebreak}` markers.
- **D-13:** Do not regress the v1.10 fixture-backed strict conversion path. If exact byte-for-byte output changes are unavoidable because the intended layout changes `columns: (...)`, update expected evidence only through the planned execution path and record why the official-template repair supersedes the prior fixture width.
- **D-14:** Preserve Phase 26 date backfill. Any package-path regression run for Phase 27 must verify that generated `jiaoan-shicao-full.md` still contains filled `起止日期：` values where package scheduling evidence is concrete.
- **D-15:** Do not stage or commit generated `deliverables/` artifacts. Verification outputs should go to `/tmp` or deliberate phase evidence files, with only planning/evidence docs and necessary source/test changes committed during later commands.

### Verification Expectations

- **D-16:** Add or record a local reproduction of official width invariants before claiming alignment: total width equals `activityTableTotalWidthCM`, `课时分配` is narrower than main text columns, same-chapter tables share identical columns, teaching method cells are centered, and emitted columns use absolute `cm` widths.
- **D-17:** Verification should include a direct `jiaoan-shicao` path: generate Markdown with `jiaoan-shicao.sh example`, render Typst, inspect `columns: (...)`, and compile PDF if local Typst is available.
- **D-18:** Verification should include the integrated package path after Phase 26: generate package output, confirm filled `起止日期`, render lesson-plan Typst, inspect official width invariants, and compile PDF if local Typst is available.
- **D-19:** If PDF tooling is unavailable, record explicit status such as `missing_compiler`, `not_run`, or `failed`; do not claim PDF success without a real PDF file.
- **D-20:** Run syntax and safety checks for edited scripts, including at least `bash -n skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` and an AWK/render smoke test. Use `git diff --cached --check` before any commit.

### Claude's Discretion

- Prefer a small AWK-side repair that ports the official chapter grouping and width functions over broad renderer replacement.
- Prefer black-box generated Typst assertions for width behavior, because future agents and users observe `columns: (...)` and PDFs rather than internal arrays.
- If the planner must choose between preserving old fixture bytes and official layout behavior, prioritize the Phase 27 official-template requirement and make the fixture update explicit.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Requirements

- `AGENTS.md` — Repository language, editing, skill authoring, GSD workflow, and OpenClaw/Hermes requirements.
- `.planning/PROJECT.md` — Captures v1.12 post-close repair discipline, official-template evidence requirement, and regression artifact expectations.
- `.planning/REQUIREMENTS.md` — Locks TDPR-04, TDPR-05, TDPR-06, and TDPR-07 for Phase 27.
- `.planning/ROADMAP.md` — Defines Phase 27 goal, dependency on Phase 26, success criteria, and active milestone scope.
- `.planning/STATE.md` — Records Phase 27 as ready after Phase 26 completion.
- `.planning/phases/26-package-date-backfill-repair/26-SUMMARY.md` — Confirms date backfill is complete, gives commits/evidence, and records the package-path behavior that Phase 27 must not regress.

### Official Reference Snapshots

- `/private/tmp/presto-jiaoan-shicao-main.go` — Official algorithm reference. Key items: `activityTableTotalWidthCM = 25.04`, `renderActivitySection`, `sectionColumnSpecs`, `tableColumnWidthsCM`, `columnPressures`, `headerMinWidthCM`, `contentPressure`, and centered teaching-method cell behavior.
- `/private/tmp/presto-jiaoan-shicao-main_test.go` — Official invariant tests. Key tests: `TestTableColumnWidthsPreserveHeaderRow`, `TestGenerateTypstCentersTeachingMethodAndRemovesTableGap`, and `TestGenerateTypstUsesSameColumnWidthsWithinChapter`.
- `/private/tmp/presto-jiaoan-shicao-example.md` — Official example Markdown useful for local reproduction and black-box comparison.

### Affected Local Files

- `skills/jiaoan-shicao/scripts/render_v110_typst.awk` — Current Markdown-to-Typst renderer and likely repair point. Existing `table_columns_for_task(i)` computes whole-task widths; `emit_activity_group(i, g)` emits per-group tables; parser handles activity groups but not pagebreak chapters for width sharing.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` — Public command wrapper that must remain stable.
- `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md` — Standalone example Markdown containing multiple `教学活动设计` sections and activity groups.
- `skills/jiaoan-shicao/references/format-and-rendering.md` — Markdown syntax and renderer contract; should document official width behavior if implementation changes the contract.
- `skills/jiaoan-shicao/SKILL.md` — Canonical skill entry and runtime adapter notes; should remain concise and portable.

### Package Regression References

- `skills/teaching-design-package/scripts/teaching-design-package.sh` — Phase 26 backfill source and package orchestration path that should remain compatible with the repaired `jiaoan-shicao` renderer.
- `skills/teaching-design-package/templates/teaching-design-package-full.md` — Package example with scheduling evidence feeding `jiaoan-shicao-full.md`.
- `skills/teaching-design-package/references/format-and-orchestration.md` — Package review gates, split output, manifest, and regression semantics.
- `.planning/phases/26-package-date-backfill-repair/26-VERIFICATION.md` — Date backfill verification evidence to preserve during Phase 27.

### Fixture and Prior Verification Context

- `test/1.10/电气设备控制线路安装与调试教案.md` — Existing strict jiaoan-shicao fixture source.
- `test/1.10/电气设备控制线路安装与调试教案.typ` — Existing strict target that may need careful treatment if official width alignment intentionally changes Typst output.
- `.planning/phases/25-regression-verification-and-documentation-index/25-CONTEXT.md` — Public command regression and documentation-index expectations.
- `.planning/phases/26-package-date-backfill-repair/26-CONTEXT.md` — Phase 26 decisions around preserving package handoff and generated artifact discipline.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `display_width`, `content_pressure`, `header_min_width_cm`, and the existing AWK weight distribution in `render_v110_typst.awk` already closely mirror the official Go logic for per-column pressure. This lowers implementation risk: the main missing piece is chapter grouping, not a total rewrite.
- `emit_activity_group(i, g)` already emits teaching-method cells with `align(center + horizon)`, matching the official invariant for the `教学方法与手段` column.
- `jiaoan-shicao.sh render --expected-typ` already supports black-box Typst comparison when a fixture target is intended.
- Phase 26 package scripts already produce filled `jiaoan-shicao-full.md`; Phase 27 can reuse those outputs as a package-path regression fixture.

### Established Patterns

- Markdown remains the reviewable semantic checkpoint before Typst/PDF output.
- Public shell commands are stable contracts; repairs should be internal and black-box verifiable.
- Official template evidence is required before claiming layout alignment.
- Generated artifacts should be temporary or phase evidence, not committed deliverables.
- OpenClaw and Hermes compatibility means canonical skill docs should avoid one-agent private syntax and keep script invocation explicit.

### Integration Points

- The likely implementation point is `skills/jiaoan-shicao/scripts/render_v110_typst.awk`, especially parsing `{pagebreak}` in activity mode, computing chapter-level specs, and using the appropriate spec in `emit_activity_group`.
- `skills/jiaoan-shicao/references/format-and-rendering.md` may need a concise renderer note explaining that activity-table columns use official-style absolute `cm` widths and chapter-level sharing.
- Any changed fixture expectation should be paired with `27-VERIFICATION.md` evidence showing why the official reference requires the new output.
- Package-path verification should connect `teaching-design-package.sh render-split` output to the repaired `jiaoan-shicao` renderer and to Phase 26 filled-date evidence.

</code_context>

<specifics>
## Specific Ideas

- A high-signal local test input should have two activity groups before `{pagebreak}` and one after. The first two generated `columns: (...)` lines should match exactly; the post-pagebreak line may differ.
- A simple parser for generated Typst can extract activity-table `columns: (...)`, parse `N.NNcm` values, sum them, and compare column 6 against columns 2, 3, and 4.
- The planner should consider extracting AWK helpers for chapter IDs such as `GROUP_CHAPTER[task, group]`, then computing `CHAPTER_COLUMNS[task, chapter]` before emission.
- Official reference facts already verified during discussion:
  - `activityTableTotalWidthCM` is `25.04`.
  - Official `sectionColumnSpecs` flushes shared specs on `PageBreak`.
  - Official `tableColumnWidthsCM` uses header minimums plus weighted remaining width.
  - Official `columnPressures` uses content pressure from table titles, activity titles, four content blocks, and hours.
  - Official tests assert same-chapter shared columns, narrow `课时分配`, centered teaching method cells, and absolute `cm` columns.

</specifics>

<deferred>
## Deferred Ideas

- Replacing the shell/AWK renderer with the official Go executable remains out of scope.
- Broad jiaoan renderer architecture refactoring remains out of scope unless the planned repair cannot be made safely in AWK.
- New package capabilities beyond preserving Phase 26 date backfill and verifying package-path width behavior remain out of scope.

</deferred>

---

*Phase: 27-Official Activity Table Width Alignment*
*Context gathered: 2026-06-14*
