---
phase: 34
plan: 01
type: execute
wave: 1
depends_on:
  - phase: 33
files_modified:
  - skills/teaching-design-package/scripts/teaching-design-package.sh
  - skills/teaching-design-package/scripts/package-model.js
  - skills/teaching-design-package/references/format-and-orchestration.md
  - .planning/phases/34-teaching-plan-formal-renderer-migration/34-VERIFICATION.md
autonomous: true
requirements:
  - TDPKG-LEGACY-01
  - TDPKG-LEGACY-03
  - TDPKG-LEGACY-04
  - TDPKG-VAL-01
requirements_addressed:
  - TDPKG-LEGACY-01
  - TDPKG-LEGACY-03
  - TDPKG-LEGACY-04
  - TDPKG-VAL-01
must_haves:
  - "D-01: Package-owned teaching-plan formal renderer replaces the Phase 33 placeholder Typst."
  - "D-02: Legacy skills/jiaoan-jihua is read-only reference/oracle and not a runtime dependency."
  - "D-03: Accepted jiaoan-jihua official five-column table rules migrate into package internals, not old handoff architecture."
  - "D-04: Old script rules may guide implementation, but target Typst fixture is generation-after oracle only."
  - "D-05: Hidden teaching-plan.typ becomes formal授课进度计划表 Typst with no pre-formal placeholder semantics."
  - "D-06: Official title, course info grid, five-column table, signature grid, A4, STSong, cuti, and provenance are generated."
  - "D-07: Official columns are exactly (3.15cm, 8.51cm, 1.12cm, 1.29cm, 1.27cm)."
  - "D-08: Task, stage, and content row order comes from unified # 授课进度计划 source order through the Phase 33 model."
  - "D-09: Row hours, task totals, and stage rowspans come from row suffixes and row counts."
  - "D-10: Shared scheduling model is the only source for academic term, week, weekday, row hours, task totals, and course total."
  - "D-11: Unified Markdown remains the only content source and teaching-design cannot rewrite teaching-plan hours or dates."
  - "D-12: Runtime calendar remains skills/teaching-design-package/references/calendar.json, not legacy calendars."
  - "D-13: Skill-local calendar, first_teaching_day, and teaching-plan row hours drive all date/week/hour derivation."
  - "D-14: daily_hours remains package-owned default/config evidence, not unified YAML."
  - "D-15: TDPKG-VAL-01 strict row-hour sum evidence is recorded in hidden diagnostics/status/model."
  - "D-16: Equivalence evidence includes Typst text/structure proof and PDF non-empty proof."
  - "D-17: Fixture evidence covers v1.10 legacy Markdown/Typst/PDF and package-template generated module evidence."
  - "D-18: Accepted equivalence allows only provenance/source/timestamp/output-name differences, not formal table/content drift."
  - "D-19: Legacy jiaoan-jihua public interface remains runnable and skills/jiaoan-jihua has no diff."
  - "D-20: Standalone copy works with only skills/teaching-design-package and contains no runtime dependency on skills/jiaoan-jihua."
  - "D-21: Phase 34 may prove existing teaching-plan.pdf or course-name target without breaking Phase 36 1 + 1 + N."
  - "D-22: Successful public root does not leak hidden module Typst, module Markdown, model/status/diagnostics/log/calendar files."
  - "D-23: render-package --pdf failures are honest non-zero failures with hidden diagnostics and no false public success."
---

# Phase 34 Plan: Teaching Plan Formal Renderer Migration

<objective>
把旧 `jiaoan-jihua` 已接受的正式 `授课进度计划表` 渲染规则迁移到 `teaching-design-package` 内部：`teaching-design-package` 从统一 Markdown 和 Phase 33 共享 scheduling model 生成正式 hidden `teaching-plan.typ` 与真实 `teaching-plan.pdf`/课程名授课进度计划表 PDF，证明其与 legacy fixture 格式一致或可接受等价，同时保持旧 `skills/jiaoan-jihua` 完全未改且不可作为 package runtime dependency。
</objective>

<scope_boundary>
## Phase 34 Only

- 本阶段只迁移 `teaching-plan` / `授课进度计划表` formal renderer。
- 本阶段不得迁移 `jiaoan-shicao` / `教学设计方案` formal renderer；那是 Phase 35。
- 本阶段不得完成最终课程名前缀公开 `1 + 1 + N` 收口或整包 PDF merge；那是 Phase 36。
- 本阶段不得修改 `skills/jiaoan-jihua/`。旧 skill 只能作为只读格式参考、fixture oracle 和兼容性验证对象。
- package runtime 不得调用 `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`，不得读取 `skills/jiaoan-jihua/references/calendar.json`，不得要求 standalone copy 安装 sibling skill。
- 旧目标 Typst/PDF fixture 只能用于生成后 diff/hash/结构断言/PDF smoke evidence，不能作为生成源拼接或复制。
</scope_boundary>

<must_haves>
## Truths

- LT-01: `teaching-design-package` 必须拥有 package-owned `teaching-plan` formal renderer，正常 `render-package` / `render-package --pdf` 路径会调用它。
- LT-02: Phase 33 的 hidden `.teaching-design-package/work/teaching-plan.typ` 不能继续带有 `Pre-formal surface only` 或等价占位语义；它必须变成正式授课进度计划表 Typst。
- LT-03: 旧 `skills/jiaoan-jihua` 只读参考且运行时不可依赖；`git diff --name-only -- skills/jiaoan-jihua` 必须为空。
- LT-04: 正式 Typst 必须包含旧 `jiaoan-jihua` 当前可接受的官方五列表格结构：标题、课程信息 grid、五列表格、签字 grid、A4 页面、`STSong` 字体、`@preview/cuti:0.2.1` fake-bold import/show rule、以及 `// jiaoan-jihua official template` 或等价 package provenance 注释。
- LT-05: 表格列宽固定为 `(3.15cm, 8.51cm, 1.12cm, 1.29cm, 1.27cm)`，列语义固定为学习环节、教学内容、周次、星期、学时。
- LT-06: 课程信息区必须保留专业名称、课程名称、授课教师、授课班级；签字区必须保留系主任、教研室主任、制表/教师签字语义。
- LT-07: 学习任务标题、学习环节标题、教学内容行顺序必须来自统一 Markdown 的 `# 授课进度计划` 经 Phase 33 model 传递后的源顺序，不得按标题、日期、周次或任务名重排。
- LT-08: `TDPKG-VAL-01` 必须关闭：授课进度计划每一行 `内容-N` 是唯一原始课时来源；学习环节、学习任务和课程总课时均严格由这些行求和。
- LT-09: 每个内容行的 `学时` 单元格显示该行原始课时；学习任务总学时显示该任务行课时严格求和；学习环节 `rowspan` 由该环节内容行数决定。
- LT-10: 学年、学期、标题周次范围、每行周次、星期、学时消耗必须来自 package shared scheduling model；formal renderer 不得重新跑 calendar 推导。
- LT-11: `calendar.json` 继续使用 `skills/teaching-design-package/references/calendar.json`；不得恢复读取 legacy calendar。
- LT-12: hidden diagnostics/status/model 必须可审计：记录 teaching-plan formal renderer 状态、TDPKG-VAL-01 strict sum evidence、calendar hash、row totals、task totals、course total、fixture/equivalence evidence pointer、standalone runtime independence evidence。
- LT-13: fixture evidence 至少覆盖 legacy `test/1.10/电气设备控制线路安装与调试授课计划.md/.typ/.pdf`，以及 `skills/teaching-design-package/templates/teaching-design-package-full.md` 经 package path 生成的 teaching-plan evidence。
- LT-14: 可接受等价允许 provenance 注释、source path、generated timestamp 或 output filename 不同；不允许列宽、标题层级、课程信息字段、任务/环节/内容顺序、周次/星期/学时、签字 grid 或正文内容实质漂移。
- LT-15: standalone copy 只包含 `skills/teaching-design-package` 时必须能生成 formal teaching-plan Typst/PDF；生成的 hidden model/status/diagnostics 不得出现 `skills/jiaoan-jihua` runtime path。
- LT-16: 成功输出的 public root 不得泄漏 `teaching-plan.typ`、module Markdown、model、status、diagnostics、calendar JSON、log 或其他中间件。
- LT-17: 若 teaching-plan formal render、Typst compile 或 PDF 非空检查失败，命令必须非零退出并写 hidden diagnostics，不能留下看似成功的 public delivery root。

## Context Decision Coverage Map

- D-01: package-owned `teaching-plan` formal renderer in `skills/teaching-design-package/` and normal command routing. Covered by Tasks 1, 3, and 6.
- D-02: legacy `skills/jiaoan-jihua` is read-only reference/oracle, not a package runtime dependency. Covered by Tasks 1, 5, and verification.
- D-03: migrate accepted official five-column table rules into package internals, not old handoff architecture. Covered by Tasks 1 and 4.
- D-04: old script rules may guide implementation, but target Typst fixture is generation-after oracle only. Covered by Tasks 1 and 4.
- D-05: replace Phase 33 placeholder `teaching-plan.typ` with formal授课进度计划表 Typst. Covered by Task 1.
- D-06: formal renderer emits official title, course info grid, five-column table, signature grid, A4, `STSong`, `cuti`, and provenance. Covered by Tasks 1 and 4.
- D-07: official column widths are `(3.15cm, 8.51cm, 1.12cm, 1.29cm, 1.27cm)` with fixed column semantics. Covered by Tasks 1 and 4.
- D-08: task/stage/content source order comes from unified `# 授课进度计划` through Phase 33 model and is not reordered. Covered by Tasks 1 and 2.
- D-09: task totals, stage rowspans, and row hour cells come from row suffixes and row counts. Covered by Tasks 1 and 2.
- D-10: academic term, title week range, row week, row weekday, and hour cells come from the shared scheduling model. Covered by Tasks 1, 2, and 3.
- D-11: unified Markdown remains the only content source and `# 教学设计方案` cannot rewrite teaching-plan hours/dates. Covered by Task 2.
- D-12: runtime calendar remains `skills/teaching-design-package/references/calendar.json`, not legacy calendars. Covered by Tasks 1 and 5.
- D-13: date/week/hour derivation comes from skill-local calendar, `first_teaching_day`, and teaching-plan row hours; renderer-local recalculation is forbidden. Covered by Tasks 1, 2, and 5.
- D-14: `daily_hours` stays package-owned default/config evidence, not unified YAML. Covered by Task 2.
- D-15: `TDPKG-VAL-01` strict task/course hour sums are closed with hidden diagnostics/status evidence. Covered by Task 2 and verification.
- D-16: equivalence evidence has Typst structure/text layer and PDF non-empty layer. Covered by Tasks 3 and 4.
- D-17: baseline fixtures include v1.10 legacy Markdown/Typst/PDF plus package-template generated module evidence. Covered by Task 4.
- D-18: acceptable equivalence allows only provenance/source/timestamp/output-name differences, not formal table/content drift. Covered by Task 4.
- D-19: old `jiaoan-jihua` public interface remains runnable and `git diff --name-only -- skills/jiaoan-jihua` is empty. Covered by Task 5.
- D-20: standalone copy with only `teaching-design-package` generates formal teaching-plan evidence with no legacy runtime paths. Covered by Task 5.
- D-21: Phase 34 may prove existing `teaching-plan.pdf` or course-name target, but must not break Phase 36 `1 + 1 + N`. Covered by Task 3.
- D-22: hidden artifacts stay under `.teaching-design-package/`; public root does not leak Typst, model, status, diagnostics, calendar, or logs. Covered by Tasks 3 and 5.
- D-23: `render-package --pdf` failure remains honest: non-zero exit, hidden diagnostics, no false public success. Covered by Task 3.
</must_haves>

<tasks>
## Task 1: Replace the teaching-plan placeholder with a package-owned formal renderer

<read_first>
- `AGENTS.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-CONTEXT.md`
- `.planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-SUMMARY.md`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/scripts/package-model.js`
- `skills/jiaoan-jihua/references/format-and-rendering.md`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
</read_first>

<action>
Add a package-owned formal renderer for module id `teaching-plan` under `skills/teaching-design-package/`. It may be a Node helper, a Bash helper, or an internal function, but it must be owned by the package and invoked by `teaching-design-package.sh` normal rendering. Replace only the `teaching-plan` call to `write_placeholder_pdf_typst`; leave `teaching-design` formal migration for Phase 35.

The renderer must read the package model produced by `package-model.js`, not legacy Markdown or legacy scripts at runtime. It must emit `.teaching-design-package/work/teaching-plan.typ` with:

- official provenance comment, using `// jiaoan-jihua official template` plus package-owned migration context or an explicitly documented equivalent;
- `@preview/cuti:0.2.1` import and `#show: show-cn-fakebold`;
- A4 page setup and `STSong` text settings matching the accepted baseline;
- centered academic year/semester/week-range title from the shared scheduling model;
- centered `工学一体化课程/基本技能课程授课进度计划表` title;
- course information grid containing `major_name`, `course_name`, `teacher_name`, `class_name`;
- official five-column table with `(3.15cm, 8.51cm, 1.12cm, 1.29cm, 1.27cm)`;
- learning task total-hour rows, table header row, stage rowspans, content rows, week cells, weekday cells, hour cells;
- signature grid containing 系主任、教研室主任、制表/teacher.

Do not read, source, execute, or shell out to `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`. Do not read `test/1.10/...typ` while emitting the output. The old script may be read by the executor as human/code reference only.
</action>

<acceptance_criteria>
- `render-package --input <sample> --out-dir <tmp>/out` writes `<tmp>/out/.teaching-design-package/work/teaching-plan.typ`.
- The generated `teaching-plan.typ` contains no `Pre-formal surface only` placeholder text.
- The generated `teaching-plan.typ` contains `@preview/cuti:0.2.1`, `STSong`, A4 page setup, the official table comment/provenance, the course info grid, the signature grid, and the five-column table.
- `rg 'columns: \\(3[.]15cm, 8[.]51cm, 1[.]12cm, 1[.]29cm, 1[.]27cm\\)' <generated-teaching-plan.typ>` passes.
- `rg 'skills/jiaoan-jihua|jiaoan-jihua[.]sh|test/1[.]10/.+[.]typ' skills/teaching-design-package/scripts` does not reveal runtime generation dependencies. If a test-only path is added, it must live only in verification fixtures or planning evidence and be documented as non-runtime.
- `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh` and `node --check skills/teaching-design-package/scripts/package-model.js` pass. If a new JS helper is added, `node --check` must cover it too.
</acceptance_criteria>

## Task 2: Close TDPKG-VAL-01 with strict row-hour sum evidence

<read_first>
- `skills/teaching-design-package/scripts/package-model.js`
- `references/scheduling-contract.md`
- `.planning/REQUIREMENTS.md`
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-CONTEXT.md`
</read_first>

<action>
Make the package model and hidden diagnostics explicitly prove that all teaching-plan hour totals come from授课计划 row suffixes only. Add or harden evidence fields so executors and verifiers can assert:

- every parsed row has a stable source pointer, raw title, raw row hour, assigned hour, term week, weekday, and date-level consumption;
- each stage total is `sum(stage.rows[].hours)`;
- each task total is `sum(task.stages[].rows[].hours)`;
- course total is `sum(all rows[].hours)`;
- renderer uses `row.hours` for the `学时` cell and `task.total_hours` for each task total row;
- no value from `# 教学设计方案`, YAML `total_hours`, handwritten date fields, or renderer-local recalculation can override teaching-plan totals.

Reject any attempt to put `total_hours`, `daily_hours`, `school_year`, `semester`, `start_date`, `end_date`, `date_range`, `validation`, `status`, or output readiness into unified YAML, preserving Phase 33's forbidden derived frontmatter behavior. If any row has zero, negative, decimal, missing, or non-integer hours, fail with hidden diagnostics and no final success.
</action>

<acceptance_criteria>
- Hidden `model.json` or `diagnostics.json` includes `total_hours_source: "teaching_plan_rows"` or equivalent.
- Hidden evidence includes row totals, stage totals, task totals, and course total.
- A verification script can recompute the course total from `model.schedule.tasks[].stages[].rows[].hours` and match `model.scheduling.total_hours` and `model.derived.total_hours`.
- A verification script can recompute each task total from its row hours and match both model evidence and rendered task total rows.
- A fixture adding `total_hours:` or `daily_hours:` to unified YAML fails with `forbidden_derived_frontmatter`.
- A fixture changing a row suffix to `-0`, `--1`, `-1.5`, or removing the suffix fails non-zero with a stable malformed/non-positive hour diagnostic.
- `TDPKG-VAL-01` is listed as completed in `34-SUMMARY.md` only after these assertions pass.
</acceptance_criteria>

## Task 3: Integrate formal teaching-plan PDF generation while preserving hidden/public surfaces

<read_first>
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `.planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-VERIFICATION.md`
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-CONTEXT.md`
</read_first>

<action>
Wire `render-package --pdf` so the teaching-plan PDF is compiled from the new formal hidden Typst. Preserve Phase 34 scope:

- `teaching-plan.typ` remains hidden under `.teaching-design-package/work/`;
- successful public root may continue using the existing `teaching-plan.pdf` name unless the executor safely adds the Phase 36 target course-name alias without breaking the future `1 + 1 + N` contract;
- `teaching-design.typ` may remain Phase 33/35 pre-formal until Phase 35;
- full package PDF merge semantics remain Phase 36 scope.

If Typst compile fails, the PDF is empty, or the formal renderer fails before compile, write hidden status/diagnostics/failure evidence and exit non-zero. Do not create root-level status/model/diagnostics/log files. Do not expose hidden Typst or module Markdown in the public root.
</action>

<acceptance_criteria>
- `render-package --pdf --input <sample> --out-dir <tmp>/out` attempts to compile `.teaching-design-package/work/teaching-plan.typ` into the teaching-plan public PDF target.
- On a machine with `typst`, the teaching-plan PDF exists and is non-empty when the renderer succeeds.
- Hidden status records teaching-plan formal renderer state, source Typst path, public PDF target, and compile result.
- If `typst` is unavailable or compilation fails, the command exits non-zero and records hidden failure diagnostics rather than claiming final success.
- `find <tmp>/out -maxdepth 1 -type f` does not list `teaching-plan.typ`, module Markdown, `model.json`, `status.json`, `diagnostics.json`, `calendar.json`, or logs.
- Hidden `.teaching-design-package/work/teaching-plan.typ` exists for evidence, while public root contains only allowed public outputs for the current phase behavior.
</acceptance_criteria>

## Task 4: Prove legacy fixture equivalence or documented acceptable equivalence

<read_first>
- `test/1.10/电气设备控制线路安装与调试授课计划.md`
- `test/1.10/电气设备控制线路安装与调试授课计划.typ`
- `test/1.10/电气设备控制线路安装与调试授课计划.pdf`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `skills/jiaoan-jihua/references/format-and-rendering.md`
- `test/validation/jiaoan-jihua-original/VERIFY.md`
- `test/validation/blackbox-jiaoan-jihua/VERIFY.md`
</read_first>

<action>
Add Phase 34 verification evidence proving formal compatibility in two layers:

1. Legacy fixture layer: generate package-owned teaching-plan Typst/PDF for the v1.10 teaching-plan fixture shape. If the unified package input cannot directly be the old fixture, create a temporary verification fixture that embeds the same course metadata and `# 授课进度计划` rows into the teaching-design-package unified shape, then compare the generated formal teaching-plan Typst against `test/1.10/电气设备控制线路安装与调试授课计划.typ`.
2. Package template layer: generate from `skills/teaching-design-package/templates/teaching-design-package-full.md` and assert it has the official formal table surface, scheduling-derived week/day/hour cells, strict totals, and non-empty teaching-plan PDF.

Use strict `diff -u` where possible. If exact Typst diff cannot be byte-for-byte because of package provenance comments, source paths, output filenames, or generated timestamps, add a normalized comparison script or command that strips only those documented fields. The normalized comparison must still fail on column widths, table title hierarchy, course info fields, task/stage/content order, row weeks, row weekdays, row hours, task totals, signature grid, or body text drift.
</action>

<acceptance_criteria>
- `34-VERIFICATION.md` records exact commands for generating package teaching-plan Typst and PDF from the legacy fixture-equivalent input.
- `34-VERIFICATION.md` records either `diff -u` success against `test/1.10/电气设备控制线路安装与调试授课计划.typ` or a normalized diff with an explicit allowed-differences list.
- The allowed-differences list is limited to provenance comments, source path, generated timestamp, or output filename.
- Structural assertions grep the generated Typst for official title, `@preview/cuti:0.2.1`, `STSong`, the five fixed column widths, course info labels, task total rows, stage rowspans, week/day/hour cells, and signature grid.
- `typst compile <generated-teaching-plan.typ> <generated-teaching-plan.pdf>` succeeds when Typst is available, and the PDF is non-empty.
- Package template verification proves the generated teaching-plan output is formal, not a flattened unified document or placeholder.
- `34-VERIFICATION.md` records SHA-256 hashes and file sizes for generated Typst/PDF and baseline Typst/PDF where relevant.
</acceptance_criteria>

## Task 5: Verify standalone runtime independence and legacy skill preservation

<read_first>
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/jiaoan-jihua/SKILL.md`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
- `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md`
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-CONTEXT.md`
</read_first>

<action>
Add verification that the package works as a standalone copied skill and that legacy `jiaoan-jihua` remains unchanged:

- copy only `skills/teaching-design-package` into a fresh temporary skill root;
- run `scripts/teaching-design-package.sh example`, `model`, `render-package`, and, when Typst exists, `render-package --pdf`;
- assert the copied package uses its own `references/calendar.json` and produces formal teaching-plan Typst/PDF without sibling skill folders;
- scan generated model/status/diagnostics/logs and source scripts for runtime path references to `skills/jiaoan-jihua`;
- run legacy `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh example` and `render` smoke checks;
- prove `git diff --name-only -- skills/jiaoan-jihua` is empty.
</action>

<acceptance_criteria>
- Standalone copy test passes with only `skills/teaching-design-package` copied.
- Standalone hidden `.teaching-design-package/work/teaching-plan.typ` is formal and contains no placeholder text.
- Standalone hidden model/status/diagnostics do not contain `skills/jiaoan-jihua` or `skills/jiaoan-shicao` runtime paths.
- Legacy `jiaoan-jihua.sh example --output <tmp>` succeeds.
- Legacy `jiaoan-jihua.sh render --input test/1.10/电气设备控制线路安装与调试授课计划.md --typ <tmp>` succeeds.
- `git diff --name-only -- skills/jiaoan-jihua` prints nothing.
- `34-VERIFICATION.md` records all standalone and legacy preservation commands with observed results.
</acceptance_criteria>

## Task 6: Update package docs and Phase 34 verification artifacts

<read_first>
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-PLAN.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/SKILL.md`
</read_first>

<action>
Update package reference documentation to describe the migrated package-owned teaching-plan formal renderer without turning internal module mechanics into teacher-facing workflow. Keep `SKILL.md` concise; only update it if the public delivery/status description is now inaccurate.

During execution, create `34-VERIFICATION.md` and `34-SUMMARY.md`. `34-VERIFICATION.md` must include exact commands and observed results for syntax checks, model strict-sum checks, formal Typst/PDF generation, fixture equivalence, public-root leakage, hidden diagnostics, standalone copy, legacy skill preservation, and no sibling runtime dependency. `34-SUMMARY.md` must list implementation commits and `requirements-completed: [TDPKG-LEGACY-01, TDPKG-LEGACY-03, TDPKG-LEGACY-04, TDPKG-VAL-01]` only after verification passes.
</action>

<acceptance_criteria>
- `format-and-orchestration.md` states `teaching-plan` formal rendering is package-owned and no longer Phase 33 placeholder output.
- Docs state legacy `jiaoan-jihua` remains an external compatibility surface and is not a package runtime dependency.
- Docs state teaching-plan formal renderer reads the shared scheduling model for weeks/weekdays/hours.
- Docs state hidden module Typst and diagnostics stay under `.teaching-design-package/` and do not belong in public root.
- `34-VERIFICATION.md` frontmatter has `status: passed` only if every verification command passes.
- `34-SUMMARY.md` records files changed, commits, deviations, and self-check.
</acceptance_criteria>
</tasks>

<verification>
Run these checks during execute-phase and record exact output highlights in `34-VERIFICATION.md`.

```bash
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh
node --check skills/teaching-design-package/scripts/package-model.js
test ! -f skills/teaching-design-package/scripts/teaching-plan-renderer.js || node --check skills/teaching-design-package/scripts/teaching-plan-renderer.js

tmp_root="$(mktemp -d "${TMPDIR:-/tmp}/tdpkg-phase34.XXXXXX")"
skills/teaching-design-package/scripts/teaching-design-package.sh example \
  --output "$tmp_root/package.md"
skills/teaching-design-package/scripts/teaching-design-package.sh model \
  --input "$tmp_root/package.md" \
  > "$tmp_root/model.json"
skills/teaching-design-package/scripts/teaching-design-package.sh render-package \
  --input "$tmp_root/package.md" \
  --out-dir "$tmp_root/out"

test -f "$tmp_root/out/.teaching-design-package/work/teaching-plan.typ"
! rg 'Pre-formal surface only|Phase 33 module Typst intermediate' "$tmp_root/out/.teaching-design-package/work/teaching-plan.typ"
rg '@preview/cuti:0[.]2[.]1' "$tmp_root/out/.teaching-design-package/work/teaching-plan.typ"
rg 'STSong' "$tmp_root/out/.teaching-design-package/work/teaching-plan.typ"
rg '工学一体化课程/基本技能课程授课进度计划表' "$tmp_root/out/.teaching-design-package/work/teaching-plan.typ"
rg 'columns: \\(3[.]15cm, 8[.]51cm, 1[.]12cm, 1[.]29cm, 1[.]27cm\\)' "$tmp_root/out/.teaching-design-package/work/teaching-plan.typ"
rg '专业名称|课程名称|授课教师|授课班级|系主任|教研室主任|制表' "$tmp_root/out/.teaching-design-package/work/teaching-plan.typ"

node - "$tmp_root/model.json" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const tasks = model.schedule.tasks;
const rowTotal = tasks.flatMap(t => t.stages.flatMap(s => s.rows)).reduce((sum, row) => sum + row.hours, 0);
if (rowTotal !== model.scheduling.total_hours) throw new Error(`course total mismatch: ${rowTotal} vs ${model.scheduling.total_hours}`);
for (const task of tasks) {
  const taskRows = task.stages.flatMap(s => s.rows);
  const taskTotal = taskRows.reduce((sum, row) => sum + row.hours, 0);
  if (taskTotal !== task.total_hours) throw new Error(`task total mismatch: ${task.title}`);
  for (const stage of task.stages) {
    const stageTotal = stage.rows.reduce((sum, row) => sum + row.hours, 0);
    if (stageTotal !== stage.total_hours) throw new Error(`stage total mismatch: ${stage.title}`);
  }
}
if (model.validation.total_hours_source !== 'teaching_plan_rows') throw new Error('total hours source is not teaching_plan_rows');
NODE

for bad in total_hours daily_hours; do
  cp "$tmp_root/package.md" "$tmp_root/bad-$bad.md"
  perl -0pi -e "s/^---\\n/---\\n$bad: 999\\n/s" "$tmp_root/bad-$bad.md"
  ! skills/teaching-design-package/scripts/teaching-design-package.sh model --input "$tmp_root/bad-$bad.md"
done

bad_row="$tmp_root/bad-row.md"
cp "$tmp_root/package.md" "$bad_row"
perl -0pi -e 's/安技教育-1/安技教育/' "$bad_row"
! skills/teaching-design-package/scripts/teaching-design-package.sh model --input "$bad_row"

! find "$tmp_root/out" -maxdepth 1 -type f -print |
  rg 'teaching-plan[.]typ|teaching-plan[.]md|model[.]json|status[.]json|diagnostics[.]json|calendar[.]json|log'

if command -v typst >/dev/null 2>&1; then
  typst compile "$tmp_root/out/.teaching-design-package/work/teaching-plan.typ" "$tmp_root/generated-teaching-plan.pdf"
  test -s "$tmp_root/generated-teaching-plan.pdf"
  skills/teaching-design-package/scripts/teaching-design-package.sh render-package \
    --pdf \
    --input "$tmp_root/package.md" \
    --out-dir "$tmp_root/out-pdf" || true
  test -s "$tmp_root/out-pdf/teaching-plan.pdf"
fi

# Legacy fixture/equivalence evidence. The executor may replace this with
# a stricter helper, but allowed normalized differences must stay documented.
legacy_tmp="$(mktemp -d "${TMPDIR:-/tmp}/tdpkg-phase34-legacy.XXXXXX")"
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render \
  --input test/1.10/电气设备控制线路安装与调试授课计划.md \
  --typ "$legacy_tmp/legacy-generated.typ" \
  --expected-typ test/1.10/电气设备控制线路安装与调试授课计划.typ

# Standalone-copy check.
standalone_root="$(mktemp -d "${TMPDIR:-/tmp}/tdpkg-phase34-standalone.XXXXXX")"
mkdir -p "$standalone_root/skills"
cp -R skills/teaching-design-package "$standalone_root/skills/"
"$standalone_root/skills/teaching-design-package/scripts/teaching-design-package.sh" example \
  --output "$standalone_root/package.md"
"$standalone_root/skills/teaching-design-package/scripts/teaching-design-package.sh" render-package \
  --input "$standalone_root/package.md" \
  --out-dir "$standalone_root/out"
test -f "$standalone_root/out/.teaching-design-package/work/teaching-plan.typ"
! rg 'Pre-formal surface only|skills/jiaoan-jihua|skills/jiaoan-shicao' "$standalone_root/out/.teaching-design-package"

# Legacy skill preservation.
legacy_smoke="$(mktemp -d "${TMPDIR:-/tmp}/tdpkg-phase34-jihua.XXXXXX")"
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh example --output "$legacy_smoke/jiaoan-jihua-full.md"
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render \
  --input test/1.10/电气设备控制线路安装与调试授课计划.md \
  --typ "$legacy_smoke/jiaoan-jihua.typ"
git diff --name-only -- skills/jiaoan-jihua

! rg 'skills/jiaoan-jihua|jiaoan-jihua[.]sh|skills/jiaoan-jihua/references/calendar[.]json' \
  skills/teaching-design-package/scripts

git diff --check
git diff --cached --check
```

For the fixture equivalence block, the executor must add concrete package-generated Typst comparison commands before marking verification passed. Exact diff is preferred. Normalized diff is acceptable only when the verification file states the allowed stripped fields and preserves strict checks for formal table structure and row content.
</verification>

<success_criteria>
- `teaching-design-package` generates a package-owned formal `授课进度计划表` Typst/PDF through the normal package path.
- The generated teaching-plan formal surface matches the accepted `jiaoan-jihua` official five-column table contract, including column widths, course info area, row/task/hour semantics, and signature grid.
- Week, weekday, academic term, task/course ranges, and hour cells come from the shared Phase 33 scheduling model and skill-local calendar.
- `TDPKG-VAL-01` is proven by machine-readable strict sum evidence.
- Legacy fixture comparison proves equality or explicitly documented acceptable equivalence.
- Standalone copy with only `skills/teaching-design-package` can generate formal teaching-plan evidence.
- Successful public root does not leak hidden module Typst, module Markdown, model/status/diagnostics/log/calendar files.
- `skills/jiaoan-jihua` remains unchanged and its public smoke path still runs.
- Phase 34 does not migrate teaching-design formal rendering, does not finalize course-name public delivery, and does not merge the final package PDF.
</success_criteria>

<threat_model>
Phase 34 touches document rendering and verification, so the main risks are false parity, hidden dependency regression, and public artifact leakage.

- False fixture parity: byte-for-byte PDF equality can be unstable and weak structural greps can miss real format drift. Mitigation: prefer strict Typst diff, allow normalized diff only for documented metadata fields, and keep structural assertions for every official table invariant.
- Runtime dependency regression: copying or invoking `skills/jiaoan-jihua` would pass in-repo but fail standalone. Mitigation: source scans, standalone-copy render, and generated evidence scans forbid sibling runtime paths.
- Scheduling divergence: renderer-local calendar assignment could drift from Phase 33 model. Mitigation: renderer must consume model row/week/day/hour evidence, and verification recomputes totals from model row data.
- Public-root leakage: formal hidden Typst or diagnostics could appear as public files. Mitigation: `find`/`rg` leakage assertions block success.
- Legacy breakage: editing old `jiaoan-jihua` to make tests pass would violate compatibility. Mitigation: `git diff --name-only -- skills/jiaoan-jihua` and legacy smoke checks are required.
- Scope creep: implementing teaching-design formal renderer or final merge now could destabilize later phases. Mitigation: plan boundary leaves Phase 35 and Phase 36 concerns out of acceptance.
</threat_model>
