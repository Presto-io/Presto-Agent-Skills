---
phase: 33
plan: 01
type: execute
wave: 1
depends_on:
  - phase: 32
files_modified:
  - skills/teaching-design-package/scripts/teaching-design-package.sh
  - skills/teaching-design-package/references/calendar.json
  - skills/teaching-design-package/references/format-and-orchestration.md
autonomous: true
requirements: [TDPKG-MOD-01, TDPKG-MOD-02, TDPKG-MOD-03, TDPKG-MOD-04, TDPKG-MOD-05, TDPKG-MOD-06, TDPKG-MOD-07, TDPKG-YAML-01, TDPKG-YAML-02, TDPKG-YAML-03, TDPKG-YAML-04, TDPKG-SCHED-01, TDPKG-SCHED-02, TDPKG-SCHED-03, TDPKG-SCHED-04, TDPKG-SCHED-05]
requirements_addressed: [TDPKG-MOD-01, TDPKG-MOD-02, TDPKG-MOD-03, TDPKG-MOD-04, TDPKG-MOD-05, TDPKG-MOD-06, TDPKG-MOD-07, TDPKG-YAML-01, TDPKG-YAML-02, TDPKG-YAML-03, TDPKG-YAML-04, TDPKG-SCHED-01, TDPKG-SCHED-02, TDPKG-SCHED-03, TDPKG-SCHED-04, TDPKG-SCHED-05]
---

# Phase 33 Plan: Module Registry, Unified Extraction, and Scheduling Model

<objective>
建立 `teaching-design-package` 的 Phase 33 基础架构：保留现有公开命令面，从统一 Markdown 单一来源解析 `teaching-plan` 与 `teaching-design` 两个注册模块，添加 skill-local `calendar.json`，用真实教学日历替换自然日顺推，生成隐藏模块 Markdown/Typst，并输出一个两个模块共享的 scheduling model 与隐藏诊断证据。
</objective>

<scope_boundary>
## Phase 33 Only

- 本阶段只实现模块注册、统一 Markdown 提取、YAML 转换、skill-local calendar、共享 scheduling model、隐藏模块 Markdown/Typst 和诊断基础。
- 本阶段不迁移正式 `jiaoan-jihua` renderer；这是 Phase 34。
- 本阶段不迁移正式 `jiaoan-shicao` renderer，也不做严格活动映射校验；这是 Phase 35。
- 本阶段不生成最终公开 PDF，不收口课程名前缀公开 `1 + 1 + N` 交付，不做 PDF 合并；这是 Phase 36。
- 本阶段不得修改 `skills/jiaoan-jihua/`、`skills/jiaoan-shicao/` 或其他 legacy standalone skill。它们只能作为只读参考。
</scope_boundary>

<must_haves>
## Truths

- LT-01: `skills/teaching-design-package/templates/teaching-design-package-full.md` 形状继续是唯一结构化 Markdown 契约。
- LT-02: `# 授课进度计划` 是课时和排课的唯一原始来源；`##` 学习任务、`###` 学习环节、以 `-N` 结尾的内容行必须按源顺序解析，非法非空行必须失败。
- LT-03: `# 教学设计方案` 提供正文结构和文本；时间字段、任务日期、任务课时、`total_hours`、`use_time` 必须来自共享 scheduling model。
- LT-04: 公开 helper command surface 必须保留：`example`、`model`、`render-package`、`manifest`、`plan-split`、`render-split`、`info`、`version` 不能被删除或改名。
- LT-05: 新增 package-owned module registry，稳定注册 `teaching-plan` 与 `teaching-design`，并记录中文显示名、顺序、提取/生成入口、隐藏 Markdown 路径、隐藏 Typst 路径和后续 PDF metadata。
- LT-06: registry 顺序是后续模块编排和 PDF 合并顺序的唯一来源：先 `teaching-plan`，后 `teaching-design`。
- LT-07: 隐藏模块 Markdown 路径固定为 `.teaching-design-package/work/teaching-plan.md` 与 `.teaching-design-package/work/teaching-design.md`。
- LT-08: 隐藏模块 Typst 路径固定为 `.teaching-design-package/work/teaching-plan.typ` 与 `.teaching-design-package/work/teaching-design.typ`。
- LT-09: 统一 YAML 只接受 `course_name`、`major_name`、`course_attribute`、`textbook_name`、`class_name`、`teachers`、`first_teaching_day`。
- LT-10: `teachers` 按源顺序用 `、` 合并为 `teacher_name`。
- LT-11: 授课进度计划模块 frontmatter 必须生成 `major_name`、`course_name`、`teacher_name`、`class_name`、`first_teaching_day`、`daily_hours`、`template: "jiaoan-jihua"`。
- LT-12: 教学设计方案模块 frontmatter 必须生成 `template: "jiaoan-shicao"`、`course_name`、`course_attribute`、`textbook_name`、`class_name`、`total_hours`、`teacher_name`、`use_time`。
- LT-13: `daily_hours` 是 package-owned 默认/配置值；`total_hours` 严格由授课计划所有内容行课时求和；`use_time` 来自真实教学日历消耗得到的课程总起止日期。
- LT-14: 新增 `skills/teaching-design-package/references/calendar.json`，standalone copy 只包含 `teaching-design-package` folder 时仍能推导排课。
- LT-15: `calendar.json` 是权威有序教学日期来源；必须移除或禁用 `sequential_teaching_days_default` 自然日顺推作为有效 scheduling 行为。
- LT-16: `first_teaching_day` 必填且必须存在于 skill-local calendar；缺失、格式错误、不在 calendar、calendar 耗尽都必须 hard fail。
- LT-17: scheduling model 必须推导学年、学期、课程总起止日期、每个学习任务起止日期、每行起止日期、周次或周次范围、星期或星期范围、assigned hours、date-level hour consumption。
- LT-18: 两个模块必须消费同一个 scheduling model object；教学设计模块不能重新计算日期、周次、星期、任务课时或活动课时。
- LT-19: 隐藏证据必须记录 calendar path、calendar hash、first teaching day、daily hours、term-week start、consumed calendar range、per-row consumption summary、per-task totals、total hours、derived `use_time`、generated module frontmatter。
- LT-20: 失败必须非零退出，并尽可能写隐藏 diagnostics/status；不能留下看起来成功的公开目录。

## Truths Context Decision Coverage Map

- D-01: `skills/teaching-design-package/templates/teaching-design-package-full.md` 的形状继续作为唯一结构化 Markdown 契约。解析器必须把 frontmatter、`# 授课进度计划` 和 `# 教学设计方案` 作为唯一权威内容来源。 Covered by Tasks 1 and 6.
- D-02: `# 授课进度计划` 是课时与排课的唯一原始来源。`##` 学习任务、`###` 学习环节下以 `-N` 结尾的行按源顺序解析；非空但不合法的行必须失败，不能静默忽略。 Covered by Task 1.
- D-03: `# 教学设计方案` 提供教案正文结构和文本，但时间字段、任务日期、任务课时、`total_hours`、`use_time` 必须来自共享 scheduling model，不能由教学设计部分独立推导。 Covered by Tasks 1, 3, and 4.
- D-04: 统一 Markdown 既要可供教师阅读，也要可供脚本解析；但 Phase 33 不应把脚本路径退回成强制教师确认关卡。脚本只消费 finalized Markdown。 Covered by Tasks 1 and 6.
- D-05: 新增 package-owned module registry，当前注册稳定模块 id `teaching-plan` 与 `teaching-design`，并记录教师可见名称、输出顺序、提取/渲染准备入口、隐藏 Markdown 路径、隐藏 Typst 路径和后续 PDF 元数据。 Covered by Tasks 1 and 4.
- D-06: registry 顺序是模块编排与后续 PDF 合并顺序的唯一来源：先 `teaching-plan`，后 `teaching-design`。 Covered by Tasks 1 and 4.
- D-07: 隐藏模块 Markdown 路径固定为 `.teaching-design-package/work/teaching-plan.md` 与 `.teaching-design-package/work/teaching-design.md`。 Covered by Tasks 1 and 4.
- D-08: 隐藏模块 Typst 路径固定为 `.teaching-design-package/work/teaching-plan.typ` 与 `.teaching-design-package/work/teaching-design.typ`。 Covered by Tasks 1 and 4.
- D-09: 模块架构不能退化成单体脚本堆砌。后续规划应寻找 skill-local 的边界，例如 registry 数据、共享 extraction/scheduling 函数和模块生成函数，同时保持现有公开 helper command surface。 Covered by Tasks 1, 4, and 6.
- D-10: 成功公开输出不得暴露模块 Markdown、模块 Typst、model、status、diagnostics、log、calendar JSON 或 scheduling evidence。这些都属于 `.teaching-design-package/` 隐藏目录；Phase 36 再做最终公开交付收口。 Covered by Tasks 4 and 5.
- D-11: 统一 YAML 在本阶段只接受教师可直接核验的 package facts：`course_name`、`major_name`、`course_attribute`、`textbook_name`、`class_name`、`teachers`、`first_teaching_day`。 Covered by Task 3.
- D-12: `teachers` 必须按源顺序用 `、` 合并为模块级 `teacher_name`。 Covered by Task 3.
- D-13: 授课进度计划模块 frontmatter 由统一 YAML 与 package 默认/推导事实生成：`major_name`、`course_name`、`teacher_name`、`class_name`、`first_teaching_day`、`daily_hours`、`template: "jiaoan-jihua"`。 Covered by Tasks 3 and 4.
- D-14: 教学设计方案模块 frontmatter 由统一 YAML 与 scheduling evidence 生成：`template: "jiaoan-shicao"`、`course_name`、`course_attribute`、`textbook_name`、`class_name`、`total_hours`、`teacher_name`、`use_time`。 Covered by Tasks 3 and 4.
- D-15: `daily_hours` 是 package-owned 默认/配置值，不是教师维护的统一 YAML 字段。若实现暴露配置入口，也必须是 skill-local，并写入隐藏证据。 Covered by Tasks 3 and 5.
- D-16: `total_hours` 严格由授课计划所有行课时求和；`use_time` 是真实教学日历消耗得到的课程总起止日期。 Covered by Tasks 2, 3, and 5.
- D-17: 新增 `skills/teaching-design-package/references/calendar.json`，确保只复制 `teaching-design-package` skill folder 的 standalone 安装也能完成推导。 Covered by Tasks 2 and 6.
- D-18: `calendar.json` 是权威有序教学日期来源。Phase 33 必须停止把自然日顺推作为有效 scheduling 行为。 Covered by Task 2.
- D-19: `first_teaching_day` 必填，并且必须能在 skill-local calendar 中定位。缺失、格式错误或不在 calendar 中都必须 hard fail。 Covered by Tasks 2 and 5.
- D-20: scheduling 按授课计划行源顺序消耗课时。每行按 `daily_hours` 容量消费 `calendar.dates`，并记录行级每日课时消耗证据。 Covered by Tasks 2, 3, and 5.
- D-21: 推导事实必须包括学年、学期、课程总起止日期和显示范围、每个学习任务起止日期、每行起止日期、周次或周次范围、星期或星期范围、assigned hours、date-level hour consumption。 Covered by Tasks 2, 3, and 5.
- D-22: 周次语义沿用现有 scheduling contract：第 1 周由 `calendar.dates` 第一日所在周推导；不得把 ISO week 当作教学周次。 Covered by Task 2.
- D-23: 学年/学期从排课日期和既有 package 约定推导：春季日期为上一年-当年第二学期，秋季日期为当年-下一年第一学期；除非后续 skill-local calendar 明确携带 term metadata。 Covered by Task 3.
- D-24: calendar 范围不够必须 hard fail。模型不得越过 calendar 用自然日外推。 Covered by Tasks 2 and 5.
- D-25: 两个模块必须消费同一个 scheduling model object。教学设计模块不能自行重新计算日期、周次、星期、任务课时或活动课时。 Covered by Tasks 3 and 4.
- D-26: 跨模块时间源唯一性锁定：授课计划行 + skill-local calendar + `first_teaching_day` + `daily_hours` 生成 model；模块渲染器只读这个 model。 Covered by Tasks 2, 3, and 5.
- D-27: 隐藏证据必须记录 calendar path、calendar hash、first teaching day、daily hours、term-week start、consumed calendar range、per-row consumption summary、per-task totals、total hours、derived `use_time`、以及 YAML 转换生成的 module frontmatter。 Covered by Task 5.
- D-28: 失败诊断至少区分：缺少章节、frontmatter 无效、出现禁止的 derived YAML、授课计划行格式错误、模块源缺失、calendar 资源缺失、calendar JSON 无效、`first_teaching_day` 不在 calendar、calendar 耗尽、非正课时、教学设计活动/课时声明不一致、隐藏工件写入失败。 Covered by Task 5.
- D-29: 失败必须诚实：尽可能写隐藏 diagnostics/status，命令非零退出，且不能留下看起来成功的公开目录。 Covered by Task 5.
</must_haves>

<tasks>
## Task 1: Add package-owned module registry and strict unified Markdown extraction

<read_first>
- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/STATE.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-CONTEXT.md`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
</read_first>

<action>
Refactor the current inline model parser inside `skills/teaching-design-package/scripts/teaching-design-package.sh` so it builds an internal package model from one finalized unified Markdown source. Add a package-owned module registry data structure with exactly these current module entries:

- `id: "teaching-plan"`, `display_name: "授课进度计划表"`, `order: 1`, `work_markdown: ".teaching-design-package/work/teaching-plan.md"`, `work_typst: ".teaching-design-package/work/teaching-plan.typ"`;
- `id: "teaching-design"`, `display_name: "教学设计方案"`, `order: 2`, `work_markdown: ".teaching-design-package/work/teaching-design.md"`, `work_typst: ".teaching-design-package/work/teaching-design.typ"`.

Parse frontmatter plus the two top-level sections `# 授课进度计划` and `# 教学设计方案` from the unified Markdown. For `# 授课进度计划`, parse source-order `##` tasks, `###` stages, and non-empty row lines ending in `-N`; fail on any non-empty content row under a stage that does not match `text-N`, on empty titles, on missing tasks, on missing stages, or on missing rows. Preserve stable source pointers such as `task:1/stage:2/row:3`. For `# 教学设计方案`, preserve the original Markdown body for downstream module generation without deriving dates independently.
</action>

<acceptance_criteria>
- `scripts/teaching-design-package.sh model --input skills/teaching-design-package/templates/teaching-design-package-full.md` exits 0.
- The model JSON contains `modules.registry[0].id == "teaching-plan"` and `modules.registry[1].id == "teaching-design"`.
- The model JSON records hidden paths `.teaching-design-package/work/teaching-plan.md`, `.teaching-design-package/work/teaching-design.md`, `.teaching-design-package/work/teaching-plan.typ`, and `.teaching-design-package/work/teaching-design.typ`.
- The model JSON contains source pointers matching `task:1/stage:1/row:1` for parsed授课计划 rows.
- A temporary Markdown fixture with a non-empty malformed row under a `###` stage, for example `缺少课时后缀`, makes `model` fail non-zero and emits a precise malformed-row diagnostic.
- Existing public commands `example`, `model`, `render-package`, `manifest`, `plan-split`, `render-split`, `info`, and `version` remain accepted by `scripts/teaching-design-package.sh --help` or command smoke checks.
</acceptance_criteria>

## Task 2: Add skill-local calendar resource and replace natural-day scheduling

<read_first>
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `references/scheduling-contract.md`
- `scripts/derive-scheduling-fixture.py`
- `skills/jiaoan-jihua/references/calendar.json`
- `skills/jiaoan-shicao/references/calendar.json`
- `.planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-CONTEXT.md`
</read_first>

<action>
Create `skills/teaching-design-package/references/calendar.json` as the package-owned teaching-date resource. The runtime code must load this calendar through `SKILL_DIR`, not through repository sibling skill paths. Replace the current natural-day scheduling behavior in `teaching-design-package.sh` with real calendar consumption:

- load and validate `references/calendar.json`;
- require JSON to be a non-empty ordered array of `YYYY-MM-DD` teaching dates, or a package-owned schema that exposes an ordered teaching-date array;
- require `first_teaching_day` to match a date in that calendar;
- consume授课计划 rows in source order using `daily_hours`;
- advance only through calendar entries, never through `addDays(firstTeachingDay, n)` or natural-day extrapolation;
- compute term-week start from the first calendar teaching date as in `references/scheduling-contract.md`;
- fail when the calendar ends before all row hours are assigned.
</action>

<acceptance_criteria>
- `test -f skills/teaching-design-package/references/calendar.json` passes.
- A standalone copy containing only `skills/teaching-design-package/` can run `scripts/teaching-design-package.sh model --input <sample>` without reading `skills/jiaoan-jihua/` or `skills/jiaoan-shicao/`.
- The model JSON contains `scheduling.calendar.path` or equivalent pointing to `skills/teaching-design-package/references/calendar.json` within the copied skill folder.
- The model JSON contains a calendar hash field such as `scheduling.calendar.sha256`.
- The model JSON does not report `calendar_policy: "sequential_teaching_days_default"` as the active policy; it reports a real calendar policy such as `skill_local_calendar`.
- A fixture with `first_teaching_day: "2099-01-01"` fails with a `first_teaching_day not found in calendar` diagnostic.
- A truncated temporary copy of `references/calendar.json` that cannot cover all row hours makes `model` fail with a calendar exhaustion diagnostic.
- `rg 'addDays\\(|sequential_teaching_days_default|new Date\\(' skills/teaching-design-package/scripts/teaching-design-package.sh` finds no active natural-day scheduling path. If `new Date` remains only for date validation or weekday formatting, verification must document that it does not advance days outside calendar entries.
</acceptance_criteria>

## Task 3: Generate shared scheduling model and module frontmatter from unified YAML

<read_first>
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `references/scheduling-contract.md`
- `.planning/REQUIREMENTS.md`
</read_first>

<action>
Extend the package model so unified frontmatter accepts only teacher-verifiable package facts: `course_name`, `major_name`, `course_attribute`, `textbook_name`, `class_name`, `teachers`, and `first_teaching_day`. Reject derived or internal keys including `daily_hours`, `total_hours`, `school_year`, `semester`, `start_date`, `end_date`, `date_range`, `calendar_policy`, `calendar_source`, `outputs`, `validation`, `status`, `manifest`, `output_readiness`, `final_ready`, `pdf_ready`, and `typst_ready`.

Build one shared scheduling model object from授课计划 rows, skill-local calendar, `first_teaching_day`, and package-owned `daily_hours`. The model must include total hours, per-task totals, per-stage totals, per-row assigned hours, per-row date-level consumption, term-week or range, weekday or range, course start/end dates, course `use_time`, school year, semester, and term-week start. Generate module frontmatter from this shared model:

- teaching-plan module: `major_name`, `course_name`, `teacher_name`, `class_name`, `first_teaching_day`, `daily_hours`, `template: "jiaoan-jihua"`;
- teaching-design module: `template: "jiaoan-shicao"`, `course_name`, `course_attribute`, `textbook_name`, `class_name`, `total_hours`, `teacher_name`, `use_time`.
</action>

<acceptance_criteria>
- `model` output contains `metadata.teacher_name` equal to the `teachers` list joined by `、` in source order.
- `model` output contains one shared object such as `scheduling` and both `modules.items[].frontmatter` values are derived from it.
- `modules.items` or equivalent contains `teaching-plan.frontmatter.template == "jiaoan-jihua"` and `teaching-design.frontmatter.template == "jiaoan-shicao"`.
- `teaching-plan.frontmatter.daily_hours` is present and comes from package-owned default/config evidence, not unified YAML.
- `teaching-design.frontmatter.total_hours` equals the strict sum of all授课计划 row hours.
- `teaching-design.frontmatter.use_time` equals the scheduling model's derived course date range.
- A temporary Markdown fixture adding `daily_hours:` or `total_hours:` to unified YAML fails with a forbidden derived frontmatter diagnostic.
- The teaching-design module has no separate date/week/hour recomputation path; verification can show it reads `scheduling` or derived module frontmatter generated from `scheduling`.
</acceptance_criteria>

## Task 4: Write hidden module Markdown and Typst without changing public delivery semantics

<read_first>
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/jiaoan-jihua/references/format-and-rendering.md`
- `skills/jiaoan-shicao/references/format-and-rendering.md`
- `.planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-CONTEXT.md`
</read_first>

<action>
Make `render-package` and existing split-compatible commands generate hidden module Markdown and hidden module Typst under `.teaching-design-package/work/` using the module registry and shared model. The hidden Markdown should be valid standalone-style module Markdown for later renderer migration:

- `.teaching-design-package/work/teaching-plan.md` has frontmatter generated for `template: "jiaoan-jihua"` and body generated from parsed `# 授课进度计划`;
- `.teaching-design-package/work/teaching-design.md` has frontmatter generated for `template: "jiaoan-shicao"` and body generated from parsed `# 教学设计方案`, with derived `total_hours` and `use_time`;
- `.teaching-design-package/work/teaching-plan.typ` and `.teaching-design-package/work/teaching-design.typ` may remain placeholder/pre-formal Typst surfaces in Phase 33, but they must be generated from module model data and clearly marked as package-owned module intermediates, not final public PDFs.

Do not expose module Markdown or Typst in the successful public root. Do not generate or claim final public PDFs in Phase 33 beyond preserving existing command compatibility.
</action>

<acceptance_criteria>
- `render-package --input <sample> --out-dir <tmp>/out` exits 0 without requiring `--pdf`.
- `test -f <tmp>/out/.teaching-design-package/work/teaching-plan.md` passes.
- `test -f <tmp>/out/.teaching-design-package/work/teaching-design.md` passes.
- `test -f <tmp>/out/.teaching-design-package/work/teaching-plan.typ` passes.
- `test -f <tmp>/out/.teaching-design-package/work/teaching-design.typ` passes.
- The hidden `teaching-plan.md` contains `template: "jiaoan-jihua"` and not a teacher-maintained `total_hours`.
- The hidden `teaching-design.md` contains `template: "jiaoan-shicao"`, derived `total_hours`, and derived `use_time`.
- `find <tmp>/out -maxdepth 1 -type f | rg 'teaching-plan[.]md|teaching-design[.]md|teaching-plan[.]typ|teaching-design[.]typ|calendar[.]json|model[.]json|status[.]json|diagnostics[.]json'` has no matches.
- `render-package --pdf` behavior is not expanded to final Phase 36 semantics in this phase; any existing PDF behavior must remain honest and non-final unless all existing required outputs actually exist.
</acceptance_criteria>

## Task 5: Record hidden scheduling evidence and classified diagnostics

<read_first>
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `.planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-CONTEXT.md`
</read_first>

<action>
Extend hidden `model.json`, `status.json`, and `diagnostics.json` under `.teaching-design-package/` so Phase 33 infrastructure has auditable evidence and precise failure classes. At minimum, hidden evidence must record:

- calendar path and SHA-256 hash;
- first teaching day;
- daily hours and its source;
- term-week start;
- consumed calendar range;
- row-level hour consumption summary;
- task totals and stage totals;
- total hours;
- derived `use_time`;
- generated module frontmatter for both modules;
- module registry order and hidden output paths.

Classify failures with stable codes or machine-readable fields for missing sections, invalid frontmatter, forbidden derived YAML, malformed授课计划 row, missing module source, missing calendar resource, invalid calendar JSON, first teaching day not in calendar, calendar exhaustion, non-positive hours, teaching-design time/hour declarations inconsistent with Phase 33-supported checks, hidden artifact write failure, and public root leakage.
</action>

<acceptance_criteria>
- Successful `render-package` writes `<out>/.teaching-design-package/model.json`, `<out>/.teaching-design-package/status.json`, and `<out>/.teaching-design-package/diagnostics.json`.
- Hidden model/status/diagnostics include calendar path, calendar hash, first teaching day, daily hours, term-week start, consumed calendar range, total hours, derived `use_time`, module registry, and generated module frontmatter.
- Missing `# 授课进度计划` fails with a stable missing-section diagnostic.
- Invalid calendar JSON fails with a stable invalid-calendar diagnostic.
- `first_teaching_day` absent from calendar fails with a stable first-day-not-found diagnostic.
- Calendar exhaustion fails with a stable calendar-exhausted diagnostic.
- Hidden artifact write failures are surfaced as non-zero command failures rather than ignored.
- No successful default public root contains `calendar.json`, `model.json`, `status.json`, `diagnostics.json`, module Markdown, module Typst, logs, or scheduling evidence files.
</acceptance_criteria>

## Task 6: Update package reference docs and record Phase 33 verification

<read_first>
- `.planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-PLAN.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/SKILL.md`
</read_first>

<action>
Update `skills/teaching-design-package/references/format-and-orchestration.md` to describe the Phase 33 module registry, skill-local calendar resource, shared scheduling model, hidden module Markdown/Typst, YAML conversion boundary, and non-goals for Phase 34-36. Keep `SKILL.md` public workflow stable unless a minimal note is needed for the script boundary; do not turn module internals into teacher-facing instructions.

During execute-phase, create `33-SUMMARY.md` and `33-VERIFICATION.md` that record implementation commits, exact verification commands, hidden artifact listings, scheduling model assertions, standalone-copy checks, failure diagnostics checks, public command smoke checks, and Phase 33 scope exclusions.
</action>

<acceptance_criteria>
- `format-and-orchestration.md` names `teaching-plan` and `teaching-design` as package-owned registered modules and names their hidden work paths.
- `format-and-orchestration.md` states `calendar.json` lives at `skills/teaching-design-package/references/calendar.json` and is the active scheduling source.
- `format-and-orchestration.md` states natural-day sequential scheduling is not valid for Phase 33+ package scheduling.
- `format-and-orchestration.md` states Phase 33 does not migrate formal renderers, does not generate final public PDFs, and does not perform Phase 36 public delivery/PDF merge finalization.
- `33-VERIFICATION.md` records all commands from the verification block and marks status passed only if all Phase 33 requirements pass.
- `33-SUMMARY.md` lists `requirements-completed` exactly as `TDPKG-MOD-01..07`, `TDPKG-YAML-01..04`, and `TDPKG-SCHED-01..05` after successful execution verification.
</acceptance_criteria>
</tasks>

<verification>
Run these checks after implementation. Keep exact stdout/stderr evidence in `33-VERIFICATION.md`.

```bash
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh

skills/teaching-design-package/scripts/teaching-design-package.sh info
skills/teaching-design-package/scripts/teaching-design-package.sh version
skills/teaching-design-package/scripts/teaching-design-package.sh example --output /tmp/tdpkg-phase33-example.md
skills/teaching-design-package/scripts/teaching-design-package.sh model --input /tmp/tdpkg-phase33-example.md > /tmp/tdpkg-phase33-model.json

node -e '
const fs = require("fs");
const model = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
const registry = model.modules && (model.modules.registry || model.modules);
if (!Array.isArray(registry)) throw new Error("missing module registry");
if (registry[0].id !== "teaching-plan") throw new Error("bad first module");
if (registry[1].id !== "teaching-design") throw new Error("bad second module");
if (!JSON.stringify(model).includes(".teaching-design-package/work/teaching-plan.md")) throw new Error("missing teaching-plan hidden md");
if (!JSON.stringify(model).includes(".teaching-design-package/work/teaching-design.md")) throw new Error("missing teaching-design hidden md");
if (!JSON.stringify(model).includes(".teaching-design-package/work/teaching-plan.typ")) throw new Error("missing teaching-plan hidden typ");
if (!JSON.stringify(model).includes(".teaching-design-package/work/teaching-design.typ")) throw new Error("missing teaching-design hidden typ");
if (model.metadata.teacher_name !== "张老师") throw new Error(model.metadata.teacher_name);
if (!model.scheduling) throw new Error("missing shared scheduling model");
if (!model.scheduling.calendar || !model.scheduling.calendar.sha256) throw new Error("missing calendar hash");
if (String(model.scheduling.calendar.policy || model.derived?.calendar_policy).includes("sequential_teaching_days_default")) throw new Error("natural-day policy still active");
if (!model.scheduling.use_time && !model.derived?.date_range) throw new Error("missing derived use_time");
' /tmp/tdpkg-phase33-model.json

tmp_root="$(mktemp -d "${TMPDIR:-/tmp}/tdpkg-phase33.XXXXXX")"
skills/teaching-design-package/scripts/teaching-design-package.sh render-package \
  --input /tmp/tdpkg-phase33-example.md \
  --out-dir "$tmp_root/out"

test -f "$tmp_root/out/.teaching-design-package/model.json"
test -f "$tmp_root/out/.teaching-design-package/status.json"
test -f "$tmp_root/out/.teaching-design-package/diagnostics.json"
test -f "$tmp_root/out/.teaching-design-package/work/teaching-plan.md"
test -f "$tmp_root/out/.teaching-design-package/work/teaching-design.md"
test -f "$tmp_root/out/.teaching-design-package/work/teaching-plan.typ"
test -f "$tmp_root/out/.teaching-design-package/work/teaching-design.typ"

rg 'template: "jiaoan-jihua"' "$tmp_root/out/.teaching-design-package/work/teaching-plan.md"
rg 'template: "jiaoan-shicao"' "$tmp_root/out/.teaching-design-package/work/teaching-design.md"
rg 'total_hours:' "$tmp_root/out/.teaching-design-package/work/teaching-design.md"
rg 'use_time:' "$tmp_root/out/.teaching-design-package/work/teaching-design.md"

! find "$tmp_root/out" -maxdepth 1 -type f -print |
  rg 'teaching-plan[.]md|teaching-design[.]md|teaching-plan[.]typ|teaching-design[.]typ|calendar[.]json|model[.]json|status[.]json|diagnostics[.]json|log'

derived_fail="$tmp_root/derived-frontmatter.md"
cp /tmp/tdpkg-phase33-example.md "$derived_fail"
perl -0pi -e 's/^---\n/---\ndaily_hours: 8\ntotal_hours: 999\n/s' "$derived_fail"
! skills/teaching-design-package/scripts/teaching-design-package.sh model --input "$derived_fail"

bad_first_day="$tmp_root/bad-first-day.md"
cp /tmp/tdpkg-phase33-example.md "$bad_first_day"
perl -0pi -e 's/first_teaching_day: "2026-05-11"/first_teaching_day: "2099-01-01"/' "$bad_first_day"
! skills/teaching-design-package/scripts/teaching-design-package.sh model --input "$bad_first_day"

malformed_row="$tmp_root/malformed-row.md"
cp /tmp/tdpkg-phase33-example.md "$malformed_row"
perl -0pi -e 's/安技教育-1/安技教育/' "$malformed_row"
! skills/teaching-design-package/scripts/teaching-design-package.sh model --input "$malformed_row"

standalone_root="$(mktemp -d "${TMPDIR:-/tmp}/tdpkg-phase33-standalone.XXXXXX")"
mkdir -p "$standalone_root/skills"
cp -R skills/teaching-design-package "$standalone_root/skills/"
"$standalone_root/skills/teaching-design-package/scripts/teaching-design-package.sh" example \
  --output "$standalone_root/package.md"
"$standalone_root/skills/teaching-design-package/scripts/teaching-design-package.sh" model \
  --input "$standalone_root/package.md" \
  > "$standalone_root/model.json"
rg 'skills/teaching-design-package/references/calendar[.]json|references/calendar[.]json' "$standalone_root/model.json"
! rg 'skills/jiaoan-jihua|skills/jiaoan-shicao|sequential_teaching_days_default' "$standalone_root/model.json"

rg 'teaching-design-package/references/calendar[.]json|references/calendar[.]json' \
  skills/teaching-design-package/scripts/teaching-design-package.sh \
  skills/teaching-design-package/references/format-and-orchestration.md

! rg 'skills/jiaoan-jihua|skills/jiaoan-shicao' \
  skills/teaching-design-package/scripts/teaching-design-package.sh

git diff --name-only -- skills/jiaoan-jihua skills/jiaoan-shicao
git diff --check
git diff --cached --check
```

For `new Date` scans, do not fail merely because the script formats or validates dates. Fail only if code advances outside `calendar.dates` with natural-day arithmetic.
</verification>

<success_criteria>
- Phase 33 covers all mapped requirements: `TDPKG-MOD-01..07`, `TDPKG-YAML-01..04`, and `TDPKG-SCHED-01..05`.
- Unified Markdown remains the only content source and finalized script input.
- Existing public helper commands remain available.
- Package-owned module registry drives `teaching-plan` and `teaching-design` module order and hidden output paths.
- Hidden module Markdown and Typst are generated under `.teaching-design-package/work/`.
- `skills/teaching-design-package/references/calendar.json` exists and is used from standalone copies.
- Natural-day sequential scheduling is replaced by skill-local calendar consumption.
- A single scheduling model supplies dates, weeks, weekdays, hours, totals, `teacher_name`, `total_hours`, and `use_time` to both modules.
- Hidden diagnostics/status/model capture calendar hash, scheduling evidence, generated module frontmatter, and classified failures.
- The implementation does not migrate formal legacy renderers, generate final public PDFs, enforce Phase 36 delivery merge semantics, or modify legacy standalone skills.
</success_criteria>

<threat_model>
Phase 33 changes the package's internal source-of-truth and scheduling foundation.

- Public command regression: refactoring the script could break existing commands. Mitigation: smoke test every command name and keep aliases routed to package-owned internals.
- Hidden artifact leakage: module Markdown/Typst or calendar/model/status files could appear in the public root. Mitigation: root-level `find` and `rg` assertions block leakage.
- Scheduling drift: natural-day arithmetic could remain and silently skip holidays/makeup days. Mitigation: model policy/hash assertions and calendar-exhaustion tests require `calendar.dates` consumption.
- Cross-module divergence: teaching-design could recompute dates or totals separately. Mitigation: module frontmatter assertions require values derived from one shared `scheduling` object.
- Runtime dependency regression: code could read sibling `jiaoan-*` calendars or scripts. Mitigation: standalone-copy test and `rg` scans forbid sibling runtime paths.
- Scope creep: executor could start Phase 34-36 renderer/PDF work early. Mitigation: plan boundary and verification require only hidden module intermediates and no formal renderer/PDF migration.
</threat_model>
