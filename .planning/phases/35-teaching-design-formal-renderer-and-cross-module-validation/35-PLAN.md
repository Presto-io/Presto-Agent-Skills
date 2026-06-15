---
phase: 35
plan: 01
type: execute
wave: 1
depends_on:
  - phase: 34
files_modified:
  - skills/teaching-design-package/scripts/teaching-design-package.sh
  - skills/teaching-design-package/scripts/package-model.js
  - skills/teaching-design-package/scripts/teaching-design-renderer.js
  - skills/teaching-design-package/references/format-and-orchestration.md
  - .planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/35-VERIFICATION.md
autonomous: true
requirements:
  - TDPKG-LEGACY-02
  - TDPKG-VAL-02
  - TDPKG-VAL-03
  - TDPKG-VAL-04
requirements_addressed:
  - TDPKG-LEGACY-02
  - TDPKG-VAL-02
  - TDPKG-VAL-03
  - TDPKG-VAL-04
must_haves:
  - "D-01: Package-owned teaching-design formal renderer replaces the Phase 33/34 placeholder Typst."
  - "D-02: Legacy skills/jiaoan-shicao is read-only reference/oracle and not a package runtime dependency."
  - "D-03: Old jiaoan-shicao accepted 教学设计方案 format migrates into package internals."
  - "D-04: Hidden teaching-design.md is internal only; teacher-facing unified Markdown remains unchanged."
  - "D-05: Hidden teaching-design.typ contains no Pre-formal surface placeholder semantics."
  - "D-06: # 授课进度计划 remains the only raw source for hours and dates."
  - "D-07: Runtime calendar remains skills/teaching-design-package/references/calendar.json."
  - "D-08: Every task-level 课时：xH is derived from schedule task.total_hours."
  - "D-09: Every activity ##### xH is derived from the corresponding teaching-plan row hours."
  - "D-10: Task date ranges, course use_time, and task 起止日期 come from the shared scheduling model."
  - "D-11: Mapping key is learning task + learning stage + activity order; title normalization is diagnostic only."
  - "D-12: Task count, stage count, activity count, source order, and title correspondence must hard fail on mismatch."
  - "D-13: Total-hour equality alone is insufficient; per-task, per-stage, and per-activity drift must fail."
  - "D-14: Formal output covers learning-task analysis, activity table, evaluation page, metadata, hours, and dates."
  - "D-15: Activity table preserves legacy width/pagebreak/chapter rules, including 25.04cm total width and narrow 课时分配."
  - "D-16: Legacy fixture evidence uses test/1.10 教案 md/typ/pdf as read-only oracle."
  - "D-17: Mismatch diagnostics are hidden, classified, source-pointered, and command exits non-zero."
  - "D-18: No false public success and no public-root leakage of typ/md/model/status/diagnostics/log/calendar files."
  - "D-19: Standalone copy works with only skills/teaching-design-package."
  - "D-20: Old skills/jiaoan-shicao public interface remains runnable and its files are unchanged."
---

# Phase 35 Plan: Teaching Design Formal Renderer and Cross-Module Validation

<objective>
把旧 `jiaoan-shicao` 当前可接受的正式 `教学设计方案` 渲染规则迁移到 `teaching-design-package` 内部：package 正常 `render-package` / `render-package --pdf` 路径从统一 Markdown 和 Phase 33/34 共享 scheduling model 生成正式 hidden `teaching-design.typ` 与真实 `teaching-design.pdf`，并严格校验教学设计的任务、环节、活动、课时、日期与授课计划模型一致。旧 `skills/jiaoan-shicao` 只作为只读格式参考和测试 oracle，不得成为 runtime dependency。
</objective>

<scope_boundary>
## Phase 35 Only

- 本阶段只迁移 `teaching-design` / `教学设计方案` formal renderer，并补齐 teaching-plan 到 teaching-design 的 cross-module validation。
- 本阶段不得重写最终课程名前缀公开 `1 + 1 + N` 交付契约，不得完成最终整包 PDF merge；那是 Phase 36。
- 本阶段不得新增第三模块，不得抽象跨技能通用 renderer framework。
- 本阶段不得修改 `skills/jiaoan-shicao/`。旧 skill 只能作为只读格式参考、fixture oracle 和兼容性验证对象。
- package runtime 不得调用 `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`，不得读取 `skills/jiaoan-shicao/references/calendar.json`，不得要求 standalone copy 安装 sibling skill。
- `test/1.10/电气设备控制线路安装与调试教案.typ/.pdf` 只能在生成后作为 diff/hash/结构断言/PDF smoke oracle，不能作为生成源拼接或复制。
- 统一 Markdown 的 teacher-facing 结构不得为了迁移 renderer 而改变；需要的正式模块字段由 package model 派生。
</scope_boundary>

<must_haves>
## Truths

- LT-01: `teaching-design-package` 必须拥有 package-owned `teaching-design` formal renderer，建议新增 `skills/teaching-design-package/scripts/teaching-design-renderer.js` 并由 `teaching-design-package.sh` 正常渲染路径调用。
- LT-02: Phase 33/34 的 hidden `.teaching-design-package/work/teaching-design.typ` 不能继续带有 `Pre-formal surface only` 或等价占位语义；它必须变成正式 `教学设计方案` Typst。
- LT-03: 旧 `skills/jiaoan-shicao` 只读参考且运行时不可依赖；`git diff --name-only -- skills/jiaoan-shicao` 必须为空。
- LT-04: 正式 Typst/PDF 必须覆盖旧 `jiaoan-shicao` 当前可接受 surface：封面、标题层级、学习任务分析页、教学活动设计横向表、学业评价页、课程属性、总课时、`use_time`、教师、班级、教材等字段。
- LT-05: 活动设计表必须保持旧 official 行为：横向页面、活动表总宽 `25.04cm`、窄 `课时分配` 列、同一 chapter 内共享 `columns: (...)`、`{pagebreak}` 开启新 chapter 并允许重新计算列宽、教学方法与手段逐行呈现。
- LT-06: `# 授课进度计划` 是所有课时、日期、任务总量、活动时长的唯一原始来源；`# 教学设计方案` 只提供正文结构和文本。
- LT-07: 每个 `课时：xH` 必须由对应 `model.schedule.tasks[i].total_hours` 填充或验证；教师正文若已有不一致值必须 hard fail。
- LT-08: 每个活动 `##### xH` 必须由对应 `model.schedule.tasks[i].stages[j].rows[k].hours` 填充或验证；活动课时不得由教学设计正文自行求和成为权威来源。
- LT-09: 任务起止日期、课程 `use_time`、每个任务的 `起止日期` 必须来自 shared scheduling model；不得自然日顺推、renderer 内重复计算、手填 YAML、或从 teaching-design 正文反推。
- LT-10: 映射主键顺序为“学习任务 + 学习环节 + 活动顺序”。标题归一化只用于诊断，不得按相似标题重排。
- LT-11: `# 授课进度计划` 每个 `##` 学习任务必须对应 `# 教学设计方案` 中一个学习任务分析块、一个教学活动设计块和一个学业评价块；数量不一致必须 hard fail。
- LT-12: 每个授课计划 `###` 学习环节必须在对应教案任务下有对应环节；环节数量、顺序或标题对应不一致必须 hard fail。
- LT-13: 每个授课计划内容行 `task:i/stage:j/row:k` 必须映射到对应教案活动 `task:i/stage:j/activity:k`；活动数量、顺序、标题、课时或日期不一致必须 hard fail。
- LT-14: 总量相等但局部错位必须失败；不能只依赖旧 `活动课时` / `教学活动课时` 总量校验。
- LT-15: 隐藏 diagnostics/status/model 必须记录 cross-module validation evidence：mismatch class、module id、task/stage/row/activity source pointer、plan/design title、plan/design hour/date、expected vs actual、calendar path/hash、model version、source Markdown path。
- LT-16: 失败类别至少覆盖任务数量、环节数量、活动数量、任务标题、环节标题、活动标题、`课时：xH`、`##### xH`、任务起止日期、缺少教学设计块、旧格式渲染失败、PDF 编译失败、public-root hidden leakage。
- LT-17: 任一 mismatch 必须非零退出并写隐藏诊断；不能生成最终成功产物，不能让 public root 看起来成功。
- LT-18: 成功 public root 在 Phase 35 可沿用当前英文 filename surface，但不得泄漏 `teaching-design.typ`、module Markdown、model、status、diagnostics、calendar JSON 或 logs。
- LT-19: Standalone copy 只包含 `skills/teaching-design-package` 时必须能生成正式 teaching-design Typst/PDF，并且 generated evidence 不含 `skills/jiaoan-shicao` runtime path。
- LT-20: `skills/jiaoan-shicao` 旧脚本仍可独立运行 example/render/expected-typ smoke，且旧 skill 未改。

## Context Decision Coverage Map

- D-01: package-owned `teaching-design` formal renderer in `skills/teaching-design-package/` and normal command routing. Covered by Tasks 1, 4, and 7.
- D-02: legacy `skills/jiaoan-shicao` is read-only reference/oracle, not runtime dependency. Covered by Tasks 1, 6, and verification.
- D-03: migrate accepted formal surface: cover, hierarchy, task analysis, activity table, evaluation, official table behavior. Covered by Tasks 1 and 5.
- D-04: hidden teaching-design Markdown is internal and formal renderer may consume model or hidden module Markdown. Covered by Tasks 1 and 3.
- D-05: replace placeholder `teaching-design.typ`. Covered by Task 1.
- D-06: unified Markdown and `# 授课进度计划` remain authority for schedule facts. Covered by Tasks 2 and 3.
- D-07: package calendar remains skill-local. Covered by Tasks 2 and 6.
- D-08: task `课时：xH` comes from `task.total_hours`. Covered by Tasks 2, 3, and verification.
- D-09: activity `##### xH` comes from teaching-plan row hours. Covered by Tasks 2, 3, and verification.
- D-10: dates and `use_time` come from shared scheduling model. Covered by Tasks 2 and 3.
- D-11: mapping key is task + stage + activity order, with normalized titles as diagnostics only. Covered by Task 2.
- D-12: schedule tasks correspond to design task-analysis/activity/evaluation blocks. Covered by Task 2.
- D-13: stages correspond by count/order/title. Covered by Task 2.
- D-14: rows map to activities by position and source pointer. Covered by Task 2.
- D-15: title drift is recorded and fails; no silent fuzzy remap. Covered by Task 2.
- D-16: per-task/stage/activity validation replaces total-only validation. Covered by Task 2 and negative fixtures.
- D-17: formal surface is legacy `jiaoan-shicao`, not flattened unified document. Covered by Tasks 1 and 5.
- D-18: activity table width/pagebreak/chapter behavior preserved. Covered by Tasks 1, 5, and verification.
- D-19: fixture equivalence uses `test/1.10` 教案 oracle with strict allowed differences. Covered by Task 5.
- D-20: old `jiaoan-shicao` public interface unchanged. Covered by Task 6.
- D-21: mismatch non-zero with hidden diagnostics and no false public success. Covered by Tasks 3, 4, and verification.
- D-22: diagnostics include required pointer and expected/actual fields. Covered by Tasks 2 and 3.
- D-23: failure categories enumerated. Covered by Task 3.
- D-24: Phase 35 public root remains current surface but no hidden leakage. Covered by Task 4.
- D-25: `render-package --pdf` success semantics are honest for teaching-design formal render and PDF. Covered by Task 4.
</must_haves>

<tasks>
## Task 1: Replace the teaching-design placeholder with a package-owned formal renderer

<read_first>
- `AGENTS.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/35-CONTEXT.md`
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-SUMMARY.md`
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-VERIFICATION.md`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/scripts/package-model.js`
- `skills/teaching-design-package/scripts/teaching-plan-renderer.js`
- `skills/jiaoan-shicao/references/format-and-rendering.md`
- `skills/jiaoan-shicao/scripts/render_v110_typst.awk`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`
</read_first>

<action>
Add a package-owned formal renderer for module id `teaching-design` under `skills/teaching-design-package/`. The preferred shape is `scripts/teaching-design-renderer.js`, mirroring Phase 34's `teaching-plan-renderer.js`: consume the package model JSON and emit hidden `.teaching-design-package/work/teaching-design.typ`. Replace only the `teaching-design` call to `write_placeholder_pdf_typst`; keep `teaching-plan` formal routing unchanged.

The renderer must emit the old accepted `jiaoan-shicao` formal surface from model data and hidden module text, including cover/title metadata, learning-task analysis pages, landscape activity-table pages, evaluation pages, and official Typst setup. It must use `model.derived.total_hours`, `model.derived.use_time`, `model.metadata.teacher_name`, `model.metadata.class_name`, and `model.schedule.tasks[]` rather than YAML-derived or design-body-derived schedule facts.

Activity-table generation must preserve the legacy official behavior documented and implemented in `skills/jiaoan-shicao`: total table width `25.04cm`, narrow `课时分配` column, chapter/pagebreak-scoped shared `columns: (...)`, `{pagebreak}` as a recalculation boundary, and one-line-per-method rendering for `教学方法与手段`.

Do not read, source, execute, or shell out to `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` at runtime. Do not read `test/1.10/...教案.typ` while emitting output. The old script and Typst/PDF fixture may be read by the executor as reference/oracle only.
</action>

<acceptance_criteria>
- `render-package --input <sample> --out-dir <tmp>/out` writes `<tmp>/out/.teaching-design-package/work/teaching-design.typ`.
- Generated `teaching-design.typ` contains no `Pre-formal surface only` or `Phase 33 module Typst intermediate` placeholder text.
- Generated Typst contains formal `教学设计方案` surface markers for cover/title metadata, `学习任务分析`, `教学活动设计`, `学业评价`, `course_attribute`, `total_hours`, `use_time`, teacher, class, and textbook.
- Generated Typst contains activity-table evidence for `25.04cm`, `课时分配`, landscape/pagebreak behavior, and chapter-scoped `columns: (...)`.
- `rg 'skills/jiaoan-shicao|jiaoan-shicao[.]sh|skills/jiaoan-shicao/references/calendar[.]json|test/1[.]10/.+教案[.]typ' skills/teaching-design-package/scripts` does not reveal runtime generation dependencies. Any test-only fixture reference must live in verification docs/scripts only.
- `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh`, `node --check skills/teaching-design-package/scripts/package-model.js`, `node --check skills/teaching-design-package/scripts/teaching-plan-renderer.js`, and `node --check skills/teaching-design-package/scripts/teaching-design-renderer.js` pass.
</acceptance_criteria>

## Task 2: Build strict task/stage/activity mapping evidence from the shared scheduling model

<read_first>
- `skills/teaching-design-package/scripts/package-model.js`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `test/1.10/电气设备控制线路安装与调试教案.md`
- `.planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/35-CONTEXT.md`
- `.planning/REQUIREMENTS.md`
</read_first>

<action>
Extend `package-model.js` so `model.teaching_design` is no longer only a raw Markdown blob plus total activity-hours check. It must parse `# 教学设计方案` into structured task records aligned to `model.schedule.tasks[]`:

- task analysis block per schedule task;
- activity design block per schedule task;
- evaluation block per schedule task;
- stage groups inside each activity design block;
- activity rows under each stage, including title/text sections, raw `##### xH` if present, derived hour, source pointer, and optional `{pagebreak}` chapter boundary.

The mapping source of truth is structural position: `task:i/stage:j/row:k` from the schedule maps to `task:i/stage:j/activity:k` from the design. Normalize titles only for comparison reporting. Do not fuzzy-match or reorder by similar titles.

For each mapped task, set or verify:

- design task `课时：xH` equals `schedule.tasks[i].total_hours`;
- design task date range equals `schedule.tasks[i].date_range`;
- design activity `##### xH` equals `schedule.tasks[i].stages[j].rows[k].hours`;
- activity title corresponds to the schedule row title by source position plus normalized title equality;
- stage title corresponds to the schedule stage title by source position plus normalized title equality.

Record machine-readable evidence under `model.validation.cross_module_evidence` or equivalent, with `total_hours_source: "teaching_plan_rows"`, `task_hours_source: "schedule.tasks[].total_hours"`, `activity_hours_source: "schedule.tasks[].stages[].rows[].hours"`, and `mapping_key: "learning_task + learning_stage + activity_order"`.
</action>

<acceptance_criteria>
- `model.teaching_design.tasks.length === model.schedule.tasks.length`.
- Each design task records `source`, `schedule_source`, `title`, `normalized_title`, `task_total_hours`, `derived_total_hours`, `date_range`, `analysis_block`, `activity_block`, and `evaluation_block`.
- Each mapped stage records schedule/design source pointers, raw and normalized titles, row/activity counts, and derived total hours.
- Each mapped activity records `schedule_row_source`, `design_activity_source`, schedule title/hour/date, design title/hour/date if present, expected vs actual values, and validation result.
- A model recomputation script can prove every design task `derived_total_hours` equals its schedule task `total_hours`.
- A model recomputation script can prove every design activity `derived_hours` equals its schedule row `hours`.
- Total-only checks are not sufficient: model evidence retains per-task, per-stage, and per-activity granularity.
- No value from `# 教学设计方案`, YAML `total_hours`, handwritten dates, or renderer-local calculation can override schedule task/row hours or dates.
</acceptance_criteria>

## Task 3: Add hard-fail hidden diagnostics for all cross-module mismatches

<read_first>
- `skills/teaching-design-package/scripts/package-model.js`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `.planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/35-CONTEXT.md`
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-VERIFICATION.md`
</read_first>

<action>
Turn cross-module mismatches into classified failures before successful render output is claimed. Failure diagnostics must stay hidden under `.teaching-design-package/diagnostics.json`, `.teaching-design-package/status.json`, and `.teaching-design-package/failure-diagnostics/`.

At minimum, classify and test:

- `teaching_design_task_count_mismatch`;
- `teaching_design_stage_count_mismatch`;
- `teaching_design_activity_count_mismatch`;
- `teaching_design_task_title_mismatch`;
- `teaching_design_stage_title_mismatch`;
- `teaching_design_activity_title_mismatch`;
- `teaching_design_task_hours_mismatch`;
- `teaching_design_activity_hours_mismatch`;
- `teaching_design_task_date_range_mismatch`;
- `missing_teaching_design_analysis_block`;
- `missing_teaching_design_activity_block`;
- `missing_teaching_design_evaluation_block`;
- `teaching_design_formal_render_failed`;
- `teaching_design_pdf_compile_failed`;
- `public_root_leakage`.

Each diagnostic object must include module id, mismatch class, source Markdown path, calendar path/hash, model version, plan pointer (`task:i/stage:j/row:k` when available), design pointer (`task:i/stage:j/activity:k` when available), expected values, actual values, plan/design titles, plan/design hours, plan/design date range, and a concise message.

If a mismatch occurs, `render-package` and `render-package --pdf` must exit non-zero, preserve hidden failure evidence, and not leave a public root that appears successful.
</action>

<acceptance_criteria>
- Negative fixtures for task count, stage count, activity count, task title, stage title, activity title, task `课时：xH`, activity `##### xH`, and task date range each fail non-zero.
- Each negative fixture writes hidden diagnostics with the expected mismatch class and relevant source pointers.
- `render-package --pdf` fails non-zero on teaching-design formal renderer or PDF compile failure and copies status/diagnostics into `failure-diagnostics/`.
- Failure public root does not contain `teaching-design-package.pdf`, `teaching-design.pdf`, or other files that can be mistaken for final success when the design module failed. If existing code writes preliminary public files before failing, diagnostics must mark the delivery as failed and verification must assert no success marker/status leaks to public root.
- Hidden failure evidence includes `calendar.path`, `calendar.sha256`, `model_version`, and `source_markdown`.
</acceptance_criteria>

## Task 4: Integrate formal teaching-design PDF generation while preserving public/hidden surfaces

<read_first>
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `.planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/35-CONTEXT.md`
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-VERIFICATION.md`
</read_first>

<action>
Wire `render-package --pdf` so `teaching-design.pdf` is compiled from the new formal hidden `teaching-design.typ`. Preserve Phase 35 scope:

- `teaching-design.typ` remains hidden under `.teaching-design-package/work/`;
- successful public root may continue using the current English filename surface (`teaching-design.pdf`) until Phase 36;
- `teaching-plan` behavior from Phase 34 remains intact;
- final course-name-prefixed public `1 + 1 + N` and final PDF merge semantics remain Phase 36 scope.

Status and diagnostics must record `teaching_design_formal_renderer`, source Typst path, public PDF target, cross-module validation status, PDF compile status, and non-empty PDF check. If Typst compile fails, PDF is empty, or formal renderer fails before compile, command exits non-zero and writes hidden evidence.
</action>

<acceptance_criteria>
- `render-package --pdf --input <sample> --out-dir <tmp>/out` compiles `.teaching-design-package/work/teaching-design.typ` into the teaching-design public PDF target.
- On a machine with `typst`, `teaching-design.pdf` exists and is non-empty when the renderer succeeds.
- Hidden status records teaching-design formal renderer state, cross-module validation state, hidden Typst path, public PDF target, and compile result.
- `find <tmp>/out -maxdepth 1 -type f` does not list `teaching-design.typ`, module Markdown, `model.json`, `status.json`, `diagnostics.json`, `calendar.json`, or logs.
- Hidden `.teaching-design-package/work/teaching-design.typ` exists for evidence while public root contains only allowed public outputs for Phase 35 behavior.
- `render-package --pdf` exits non-zero if `full_status`, `plan_status`, or `design_status` is not passed; no false public success is reported.
</acceptance_criteria>

## Task 5: Prove legacy jiaoan-shicao fixture equivalence or documented acceptable equivalence

<read_first>
- `test/1.10/电气设备控制线路安装与调试教案.md`
- `test/1.10/电气设备控制线路安装与调试教案.typ`
- `test/1.10/电气设备控制线路安装与调试教案.pdf`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `skills/jiaoan-shicao/references/format-and-rendering.md`
- `skills/jiaoan-shicao/scripts/render_v110_typst.awk`
- `test/validation/jiaoan-shicao-original/VERIFY.md`
- `test/validation/blackbox-jiaoan-shicao/VERIFY.md`
</read_first>

<action>
Add Phase 35 verification evidence in two layers:

1. Legacy fixture layer: generate package-owned teaching-design Typst/PDF for a fixture-equivalent package input that embeds the same metadata, `# 授课进度计划`, and `# 教学设计方案` semantics as `test/1.10/电气设备控制线路安装与调试教案.md`. Compare generated hidden `teaching-design.typ` against `test/1.10/电气设备控制线路安装与调试教案.typ`.
2. Package template layer: generate from `skills/teaching-design-package/templates/teaching-design-package-full.md` and assert the output is formal `jiaoan-shicao` surface, not flattened unified document or placeholder.

Exact `diff -u` is preferred. If exact Typst diff cannot be byte-for-byte because package renderer derives hours/dates from the scheduling model or includes package provenance/source comments, add a normalized comparison that strips only documented non-substantive metadata. Normalized comparison must still fail on title hierarchy, cover/task/evaluation structure, activity table width, chapter/pagebreak behavior, task/stage/activity order, task hours, activity hours, dates, evaluation structure, and body text drift.
</action>

<acceptance_criteria>
- `35-VERIFICATION.md` records exact commands for generating package teaching-design Typst and PDF from fixture-equivalent input.
- `35-VERIFICATION.md` records either `diff -u` success against `test/1.10/电气设备控制线路安装与调试教案.typ` or a normalized diff with an explicit allowed-differences list.
- Allowed differences are limited to package provenance comments, source path, generated timestamp, output filename, and schedule-model-derived date/hour comments that do not change rendered meaning.
- Structural assertions grep generated Typst for formal title/cover markers, `学习任务分析`, `教学活动设计`, `学业评价`, `25.04cm`, `课时分配`, pagebreak/chapter evidence, `course_attribute`, `total_hours`, `use_time`, teacher/class/textbook labels, and representative task/activity text.
- `typst compile <generated-teaching-design.typ> <generated-teaching-design.pdf>` succeeds when Typst is available, and the PDF is non-empty.
- Package template verification proves hidden `teaching-design.typ` is formal and contains no placeholder text.
- `35-VERIFICATION.md` records SHA-256 hashes and file sizes for generated Typst/PDF and baseline Typst/PDF where relevant.
</acceptance_criteria>

## Task 6: Verify standalone runtime independence and legacy skill preservation

<read_first>
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/jiaoan-shicao/SKILL.md`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`
- `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md`
- `.planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/35-CONTEXT.md`
</read_first>

<action>
Add verification that package rendering works as a standalone copied skill and old `jiaoan-shicao` remains unchanged:

- copy only `skills/teaching-design-package` into a fresh temporary skill root;
- run copied `scripts/teaching-design-package.sh example`, `model`, `render-package`, and, when Typst exists, `render-package --pdf`;
- assert the copied package uses its own `references/calendar.json` and generates formal teaching-design Typst/PDF without sibling skill folders;
- scan generated model/status/diagnostics/logs and source scripts for runtime path references to `skills/jiaoan-shicao`;
- run legacy `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example` and `render --expected-typ` smoke checks;
- prove `git diff --name-only -- skills/jiaoan-shicao` is empty.
</action>

<acceptance_criteria>
- Standalone copy test passes with only `skills/teaching-design-package` copied.
- Standalone hidden `.teaching-design-package/work/teaching-design.typ` is formal and contains no placeholder text.
- Standalone hidden model/status/diagnostics do not contain `skills/jiaoan-shicao` or `skills/jiaoan-jihua` runtime paths.
- Legacy `jiaoan-shicao.sh example --output <tmp>` succeeds.
- Legacy `jiaoan-shicao.sh render --input test/1.10/电气设备控制线路安装与调试教案.md --typ <tmp> --expected-typ test/1.10/电气设备控制线路安装与调试教案.typ` succeeds.
- `git diff --name-only -- skills/jiaoan-shicao` prints nothing.
- `35-VERIFICATION.md` records all standalone and legacy preservation commands with observed results.
</acceptance_criteria>

## Task 7: Update package docs and Phase 35 verification artifacts

<read_first>
- `.planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/35-PLAN.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/SKILL.md`
</read_first>

<action>
Update package reference documentation to describe the migrated package-owned teaching-design formal renderer and cross-module validation without turning internal module mechanics into teacher-facing workflow. Keep `SKILL.md` concise; update it only if the public workflow/status description becomes inaccurate.

During execution, create `35-VERIFICATION.md` and `35-SUMMARY.md`. `35-VERIFICATION.md` must include exact commands and observed results for syntax checks, structured mapping checks, positive PDF generation, negative mismatch fixtures, legacy equivalence, public-root leakage, hidden diagnostics, standalone copy, legacy skill preservation, and no sibling runtime dependency. `35-SUMMARY.md` must list implementation commits and `requirements-completed: [TDPKG-LEGACY-02, TDPKG-VAL-02, TDPKG-VAL-03, TDPKG-VAL-04]` only after verification passes.
</action>

<acceptance_criteria>
- `format-and-orchestration.md` states `teaching-design` formal rendering is package-owned and no longer placeholder output.
- Docs state old `jiaoan-shicao` remains an external compatibility surface and is not a package runtime dependency.
- Docs state task hours, activity hours, and dates are derived from the shared scheduling model.
- Docs state mismatch diagnostics are hidden, source-pointered, non-zero, and public-root safe.
- Docs state final course-name public delivery and final package PDF merge remain Phase 36.
- `35-VERIFICATION.md` frontmatter has `status: passed` only if every verification command passes.
- `35-SUMMARY.md` records files changed, commits, deviations, and self-check.
</acceptance_criteria>
</tasks>

<verification>
Run these checks during execute-phase and record exact output highlights in `35-VERIFICATION.md`.

```bash
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh
node --check skills/teaching-design-package/scripts/package-model.js
node --check skills/teaching-design-package/scripts/teaching-plan-renderer.js
test ! -f skills/teaching-design-package/scripts/teaching-design-renderer.js || node --check skills/teaching-design-package/scripts/teaching-design-renderer.js

tmp_root="$(mktemp -d "${TMPDIR:-/tmp}/tdpkg-phase35.XXXXXX")"
skills/teaching-design-package/scripts/teaching-design-package.sh example \
  --output "$tmp_root/package.md"
skills/teaching-design-package/scripts/teaching-design-package.sh model \
  --input "$tmp_root/package.md" \
  > "$tmp_root/model.json"
skills/teaching-design-package/scripts/teaching-design-package.sh render-package \
  --input "$tmp_root/package.md" \
  --out-dir "$tmp_root/out"

test -f "$tmp_root/out/.teaching-design-package/work/teaching-design.typ"
! rg 'Pre-formal surface only|Phase 33 module Typst intermediate' "$tmp_root/out/.teaching-design-package/work/teaching-design.typ"
rg '教学设计方案|学习任务分析|教学活动设计|学业评价' "$tmp_root/out/.teaching-design-package/work/teaching-design.typ"
rg '25[.]04cm|课时分配|pagebreak|landscape|columns:' "$tmp_root/out/.teaching-design-package/work/teaching-design.typ"
rg '课程属性|总课时|起止日期|授课教师|授课班级|教材' "$tmp_root/out/.teaching-design-package/work/teaching-design.typ"

node - "$tmp_root/model.json" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
if (model.validation.total_hours_source !== 'teaching_plan_rows') throw new Error('bad total_hours_source');
const evidence = model.validation.cross_module_evidence || model.teaching_design.cross_module_evidence;
if (!evidence) throw new Error('missing cross-module evidence');
const scheduleTasks = model.schedule.tasks;
const designTasks = model.teaching_design.tasks;
if (!Array.isArray(designTasks) || designTasks.length !== scheduleTasks.length) throw new Error('task count mismatch in evidence');
for (const [taskIndex, task] of scheduleTasks.entries()) {
  const designTask = designTasks[taskIndex];
  if (designTask.schedule_source !== task.source) throw new Error(`bad task source ${task.source}`);
  if (designTask.derived_total_hours !== task.total_hours) throw new Error(`bad task hours ${task.source}`);
  if (designTask.date_range !== task.date_range) throw new Error(`bad task date range ${task.source}`);
  for (const [stageIndex, stage] of task.stages.entries()) {
    const designStage = designTask.stages[stageIndex];
    if (designStage.schedule_source !== stage.source) throw new Error(`bad stage source ${stage.source}`);
    if (designStage.activities.length !== stage.rows.length) throw new Error(`activity count mismatch ${stage.source}`);
    for (const [rowIndex, row] of stage.rows.entries()) {
      const activity = designStage.activities[rowIndex];
      if (activity.schedule_row_source !== row.source) throw new Error(`bad row source ${row.source}`);
      if (activity.derived_hours !== row.hours) throw new Error(`bad activity hours ${row.source}`);
    }
  }
}
console.log(`cross_module_ok tasks=${designTasks.length}`);
NODE

! find "$tmp_root/out" -maxdepth 1 -type f -print |
  rg 'teaching-design[.]typ|teaching-design[.]md|model[.]json|status[.]json|diagnostics[.]json|calendar[.]json|log'

if command -v typst >/dev/null 2>&1; then
  typst compile "$tmp_root/out/.teaching-design-package/work/teaching-design.typ" "$tmp_root/generated-teaching-design.pdf"
  test -s "$tmp_root/generated-teaching-design.pdf"
  skills/teaching-design-package/scripts/teaching-design-package.sh render-package \
    --pdf \
    --input "$tmp_root/package.md" \
    --out-dir "$tmp_root/out-pdf"
  test -s "$tmp_root/out-pdf/teaching-design.pdf"
fi

# Negative cross-module mismatch fixtures. The executor may implement helpers,
# but each fixture must exit non-zero and assert the expected hidden diagnostic class.
for case_name in \
  task-count \
  stage-count \
  activity-count \
  task-title \
  stage-title \
  activity-title \
  task-hours \
  activity-hours \
  task-date-range
do
  bad_input="$tmp_root/bad-$case_name.md"
  bad_out="$tmp_root/bad-$case_name-out"
  # Create the mutation with the phase verification helper or an inline script.
  # The helper must preserve the unified Markdown contract except for the targeted mismatch.
  node .planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/create-negative-fixture.js \
    "$case_name" "$tmp_root/package.md" "$bad_input"
  ! skills/teaching-design-package/scripts/teaching-design-package.sh render-package \
    --input "$bad_input" \
    --out-dir "$bad_out"
  test -f "$bad_out/.teaching-design-package/diagnostics.json"
  rg "teaching_design_.*mismatch|missing_teaching_design_" "$bad_out/.teaching-design-package/diagnostics.json"
done

# Legacy fixture/equivalence evidence. Prefer exact diff; normalized diff is
# acceptable only with explicitly documented non-substantive stripped fields.
legacy_root="$(mktemp -d "${TMPDIR:-/tmp}/tdpkg-phase35-legacy.XXXXXX")"
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input test/1.10/电气设备控制线路安装与调试教案.md \
  --typ "$legacy_root/legacy-generated.typ" \
  --expected-typ test/1.10/电气设备控制线路安装与调试教案.typ

# The executor must add concrete package fixture-equivalent generation here,
# then compare "$legacy_root/package-teaching-design.typ" with the oracle.
diff -u \
  test/1.10/电气设备控制线路安装与调试教案.typ \
  "$legacy_root/package-teaching-design-normalized.typ"

if command -v typst >/dev/null 2>&1; then
  typst compile "$legacy_root/package-teaching-design.typ" "$legacy_root/package-teaching-design.pdf"
  test -s "$legacy_root/package-teaching-design.pdf"
fi

# Standalone-copy check.
standalone_root="$(mktemp -d "${TMPDIR:-/tmp}/tdpkg-phase35-standalone.XXXXXX")"
mkdir -p "$standalone_root/skills"
cp -R skills/teaching-design-package "$standalone_root/skills/"
"$standalone_root/skills/teaching-design-package/scripts/teaching-design-package.sh" example \
  --output "$standalone_root/package.md"
"$standalone_root/skills/teaching-design-package/scripts/teaching-design-package.sh" model \
  --input "$standalone_root/package.md" \
  > "$standalone_root/model.json"
"$standalone_root/skills/teaching-design-package/scripts/teaching-design-package.sh" render-package \
  --input "$standalone_root/package.md" \
  --out-dir "$standalone_root/out"
test -f "$standalone_root/out/.teaching-design-package/work/teaching-design.typ"
! rg 'Pre-formal surface only|skills/jiaoan-shicao|skills/jiaoan-jihua' "$standalone_root/out/.teaching-design-package" "$standalone_root/model.json"

# Legacy skill preservation.
legacy_smoke="$(mktemp -d "${TMPDIR:-/tmp}/tdpkg-phase35-shicao.XXXXXX")"
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example --output "$legacy_smoke/jiaoan-shicao-full.md"
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input test/1.10/电气设备控制线路安装与调试教案.md \
  --typ "$legacy_smoke/jiaoan-shicao.typ" \
  --expected-typ test/1.10/电气设备控制线路安装与调试教案.typ
git diff --name-only -- skills/jiaoan-shicao

! rg 'skills/jiaoan-shicao|jiaoan-shicao[.]sh|skills/jiaoan-shicao/references/calendar[.]json' \
  skills/teaching-design-package/scripts

git diff --check
git diff --cached --check
```

If the negative-fixture helper is created for verification convenience, keep it under the Phase 35 planning directory or another test/evidence-only path. It must not become a package runtime dependency.
</verification>

<success_criteria>
- `teaching-design-package` generates a package-owned formal `教学设计方案` Typst/PDF through the normal package path.
- The generated teaching-design formal surface matches the accepted `jiaoan-shicao` contract, including learning-task analysis, activity table, evaluation structure, table widths, pagebreak/chapter behavior, metadata, hours, and dates.
- Every task `课时：xH` comes from `schedule.tasks[].total_hours`.
- Every activity `##### xH` comes from `schedule.tasks[].stages[].rows[].hours`.
- Mapping evidence proves task/stage/activity数量、顺序、标题、课时和日期 all correspond to the teaching-plan scheduling model.
- Negative fixtures prove mismatched counts, titles, hours, and dates fail non-zero with hidden diagnostics and no false public success.
- Legacy fixture comparison proves equality or explicitly documented acceptable equivalence.
- Standalone copy with only `skills/teaching-design-package` can generate formal teaching-design evidence.
- Successful public root does not leak hidden module Typst, module Markdown, model/status/diagnostics/log/calendar files.
- `skills/jiaoan-shicao` remains unchanged and its public smoke path still runs.
- Phase 35 does not finalize course-name public delivery, does not merge final package PDF, and does not modify old standalone `jiaoan-shicao`.
</success_criteria>

<threat_model>
Phase 35 touches document rendering and cross-module validation. Main risks:

- False schedule/design consistency: total hours may match while one task, stage, or activity is wrong. Mitigation: require source-pointered per-task/stage/activity evidence and negative fixtures for local drift.
- Runtime dependency regression: invoking `skills/jiaoan-shicao` would pass in-repo but fail standalone. Mitigation: source scans, standalone-copy render, generated evidence scans, and legacy skill diff checks.
- Renderer-local date/hour drift: a new renderer might recompute dates or accept handwritten design values. Mitigation: renderer consumes only model scheduling facts; verification recomputes design evidence from `model.schedule`.
- Formal-layout regression: rough Typst greps can miss table width/pagebreak/chapter drift. Mitigation: fixture diff or tightly constrained normalized diff plus structural assertions for `25.04cm`, `课时分配`, chapter/pagebreak behavior, and representative body text.
- Public false success: a mismatch could leave PDFs/status in public root that look successful. Mitigation: hard non-zero failures, hidden diagnostics, no public status/diagnostics, no hidden file leakage, and failure-output checks.
- Legacy breakage: editing old `jiaoan-shicao` to make tests pass violates compatibility. Mitigation: `git diff --name-only -- skills/jiaoan-shicao` and legacy example/render smoke are required.
- Scope creep: Phase 36 public naming and merge semantics could be pulled into this phase. Mitigation: explicitly keep course-name public delivery and final merge out of Phase 35 success criteria.
</threat_model>
