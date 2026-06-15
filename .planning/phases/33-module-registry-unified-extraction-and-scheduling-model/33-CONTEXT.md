# Phase 33: Module Registry, Unified Extraction, and Scheduling Model - Context

**Gathered:** 2026-06-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 33 建立 `teaching-design-package` 的 package-owned 模块化基础：把统一 Markdown 作为唯一内容源解析，为 `teaching-plan` 与 `teaching-design` 提取注册模块输入，生成隐藏模块 Markdown/Typst，把统一 YAML 转成模块 frontmatter，新增 skill-local `calendar.json`，并基于真实日历、`first_teaching_day` 和授课计划逐行课时推导一个共享 scheduling model。

本阶段不迁移完整旧正式渲染器、不生成最终公开 PDF、不完成公开交付命名收口；这些属于 Phase 34、35、36。Phase 33 的边界是先把模块注册、隐藏中间产物、YAML 转换和唯一时间模型做成后续阶段可依赖的基础。

</domain>

<decisions>
## Implementation Decisions

### 统一 Markdown 解析
- **D-01:** `skills/teaching-design-package/templates/teaching-design-package-full.md` 的形状继续作为唯一结构化 Markdown 契约。解析器必须把 frontmatter、`# 授课进度计划` 和 `# 教学设计方案` 作为唯一权威内容来源。
- **D-02:** `# 授课进度计划` 是课时与排课的唯一原始来源。`##` 学习任务、`###` 学习环节下以 `-N` 结尾的行按源顺序解析；非空但不合法的行必须失败，不能静默忽略。
- **D-03:** `# 教学设计方案` 提供教案正文结构和文本，但时间字段、任务日期、任务课时、`total_hours`、`use_time` 必须来自共享 scheduling model，不能由教学设计部分独立推导。
- **D-04:** 统一 Markdown 既要可供教师阅读，也要可供脚本解析；但 Phase 33 不应把脚本路径退回成强制教师确认关卡。脚本只消费 finalized Markdown。

### 模块注册与隐藏工件
- **D-05:** 新增 package-owned module registry，当前注册稳定模块 id `teaching-plan` 与 `teaching-design`，并记录教师可见名称、输出顺序、提取/渲染准备入口、隐藏 Markdown 路径、隐藏 Typst 路径和后续 PDF 元数据。
- **D-06:** registry 顺序是模块编排与后续 PDF 合并顺序的唯一来源：先 `teaching-plan`，后 `teaching-design`。
- **D-07:** 隐藏模块 Markdown 路径固定为 `.teaching-design-package/work/teaching-plan.md` 与 `.teaching-design-package/work/teaching-design.md`。
- **D-08:** 隐藏模块 Typst 路径固定为 `.teaching-design-package/work/teaching-plan.typ` 与 `.teaching-design-package/work/teaching-design.typ`。
- **D-09:** 模块架构不能退化成单体脚本堆砌。后续规划应寻找 skill-local 的边界，例如 registry 数据、共享 extraction/scheduling 函数和模块生成函数，同时保持现有公开 helper command surface。
- **D-10:** 成功公开输出不得暴露模块 Markdown、模块 Typst、model、status、diagnostics、log、calendar JSON 或 scheduling evidence。这些都属于 `.teaching-design-package/` 隐藏目录；Phase 36 再做最终公开交付收口。

### YAML 转换
- **D-11:** 统一 YAML 在本阶段只接受教师可直接核验的 package facts：`course_name`、`major_name`、`course_attribute`、`textbook_name`、`class_name`、`teachers`、`first_teaching_day`。
- **D-12:** `teachers` 必须按源顺序用 `、` 合并为模块级 `teacher_name`。
- **D-13:** 授课进度计划模块 frontmatter 由统一 YAML 与 package 默认/推导事实生成：`major_name`、`course_name`、`teacher_name`、`class_name`、`first_teaching_day`、`daily_hours`、`template: "jiaoan-jihua"`。
- **D-14:** 教学设计方案模块 frontmatter 由统一 YAML 与 scheduling evidence 生成：`template: "jiaoan-shicao"`、`course_name`、`course_attribute`、`textbook_name`、`class_name`、`total_hours`、`teacher_name`、`use_time`。
- **D-15:** `daily_hours` 是 package-owned 默认/配置值，不是教师维护的统一 YAML 字段。若实现暴露配置入口，也必须是 skill-local，并写入隐藏证据。
- **D-16:** `total_hours` 严格由授课计划所有行课时求和；`use_time` 是真实教学日历消耗得到的课程总起止日期。

### 共享 Scheduling Model
- **D-17:** 新增 `skills/teaching-design-package/references/calendar.json`，确保只复制 `teaching-design-package` skill folder 的 standalone 安装也能完成推导。
- **D-18:** `calendar.json` 是权威有序教学日期来源。Phase 33 必须停止把自然日顺推作为有效 scheduling 行为。
- **D-19:** `first_teaching_day` 必填，并且必须能在 skill-local calendar 中定位。缺失、格式错误或不在 calendar 中都必须 hard fail。
- **D-20:** scheduling 按授课计划行源顺序消耗课时。每行按 `daily_hours` 容量消费 `calendar.dates`，并记录行级每日课时消耗证据。
- **D-21:** 推导事实必须包括学年、学期、课程总起止日期和显示范围、每个学习任务起止日期、每行起止日期、周次或周次范围、星期或星期范围、assigned hours、date-level hour consumption。
- **D-22:** 周次语义沿用现有 scheduling contract：第 1 周由 `calendar.dates` 第一日所在周推导；不得把 ISO week 当作教学周次。
- **D-23:** 学年/学期从排课日期和既有 package 约定推导：春季日期为上一年-当年第二学期，秋季日期为当年-下一年第一学期；除非后续 skill-local calendar 明确携带 term metadata。
- **D-24:** calendar 范围不够必须 hard fail。模型不得越过 calendar 用自然日外推。
- **D-25:** 两个模块必须消费同一个 scheduling model object。教学设计模块不能自行重新计算日期、周次、星期、任务课时或活动课时。

### 跨模块时间源与失败诊断
- **D-26:** 跨模块时间源唯一性锁定：授课计划行 + skill-local calendar + `first_teaching_day` + `daily_hours` 生成 model；模块渲染器只读这个 model。
- **D-27:** 隐藏证据必须记录 calendar path、calendar hash、first teaching day、daily hours、term-week start、consumed calendar range、per-row consumption summary、per-task totals、total hours、derived `use_time`、以及 YAML 转换生成的 module frontmatter。
- **D-28:** 失败诊断至少区分：缺少章节、frontmatter 无效、出现禁止的 derived YAML、授课计划行格式错误、模块源缺失、calendar 资源缺失、calendar JSON 无效、`first_teaching_day` 不在 calendar、calendar 耗尽、非正课时、教学设计活动/课时声明不一致、隐藏工件写入失败。
- **D-29:** 失败必须诚实：尽可能写隐藏 diagnostics/status，命令非零退出，且不能留下看起来成功的公开目录。

### Claude's Discretion
- Planner 可自行选择 `skills/teaching-design-package/scripts/` 内部实现形状，但必须保留公开命令、保持资源 skill-local、避免 sibling runtime dependency。
- Planner 可决定 `calendar.json` 是从既有 accepted calendar 复制，还是规范化为 package-owned schema；但结果必须位于 `teaching-design-package` skill folder 内，并在隐藏证据中记录 path/hash。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope
- `.planning/ROADMAP.md` — Phase 33 goal、dependencies、requirements、success criteria。
- `.planning/REQUIREMENTS.md` — v1.15 active requirements，尤其是 `TDPKG-MOD-01..07`、`TDPKG-YAML-01..04`、`TDPKG-SCHED-01..05`。
- `.planning/PROJECT.md` — active milestone direction 与 standalone package boundary。
- `.planning/STATE.md` — 当前 GSD 位置和 resume context。

### Package Contract
- `skills/teaching-design-package/SKILL.md` — canonical skill workflow 与 runtime adapter notes。
- `skills/teaching-design-package/references/format-and-orchestration.md` — 既有 standalone package contract、YAML boundary、body extraction rules、hidden diagnostics、script boundary。
- `skills/teaching-design-package/templates/teaching-design-package-full.md` — Phase 33 必须解析的统一 Markdown source shape。
- `skills/teaching-design-package/scripts/teaching-design-package.sh` — 当前公开命令面与既有 inline model/render behavior，后续改造必须保守处理。

### Scheduling And Legacy Evidence
- `references/scheduling-contract.md` — calendar dates、first teaching day、daily hours、source-order items、term weeks、weekdays、hour consumption、review/failure behavior 的共享语义。
- `scripts/derive-scheduling-fixture.py` — 真实 calendar 源顺序课时消耗、term-week 计算和失败行为的既有可执行证据。
- `skills/jiaoan-jihua/references/calendar.json` — 创建 package-owned calendar 时可参考的既有 accepted calendar resource。
- `skills/jiaoan-shicao/references/calendar.json` — 创建 package-owned calendar 时可参考的既有 accepted calendar resource。
- `skills/jiaoan-jihua/references/format-and-rendering.md` — 生成授课计划模块 Markdown 时相关的 frontmatter 与官方授课进度解析期望。
- `skills/jiaoan-shicao/references/format-and-rendering.md` — 生成教学设计模块 Markdown 时相关的 frontmatter 与教学设计结构期望。

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/teaching-design-package/scripts/teaching-design-package.sh`: 当前公开 helper command 已支持 `example`、`model`、`render-package`、`manifest`、`plan-split`、`render-split`；Phase 33 应保留公开命令面，内部改造模型与模块生成。
- 当前 inline Node model parser：已解析 frontmatter、`# 授课进度计划`、`# 教学设计方案`、`teachers`、禁止 derived YAML、授课计划行、总课时、活动课时声明、隐藏 status/diagnostics；可作为行为起点，但其自然日顺推策略必须替换。
- `scripts/derive-scheduling-fixture.py`: 提供更接近目标的真实 calendar scheduling 算法形状，包括 `calendar.dates`、`first_teaching_day` membership、`daily_hours`、term-week start、source pointers、row-level consumption、calendar exhaustion failure。
- `jiaoan-jihua` 与 `jiaoan-shicao` 现有 `calendar.json`：可作为本地 accepted calendar 数据来源，但 Phase 33 必须在 `skills/teaching-design-package/references/` 中拥有自己的资源。

### Established Patterns
- Skill-local ownership 是仓库惯例：支持资源放 `references/`，helper commands 放 `scripts/`，模板放 `templates/`。
- `teaching-design-package` 必须保持 standalone：不能依赖 sibling skill 运行时，不能要求用户拼接旧技能，不能在公开目录泄露隐藏内部工件。
- 当前隐藏诊断布局使用 `.teaching-design-package/model.json`、`.teaching-design-package/status.json`、`.teaching-design-package/diagnostics.json`、`.teaching-design-package/work/`、`.teaching-design-package/debug/`、`.teaching-design-package/failure-diagnostics/`。
- 教师维护的统一 frontmatter 禁止 derived YAML；`total_hours`、`school_year`、`semester`、`date_range`、`daily_hours`、status、manifest、validation 等必须来自解析、配置或证据。

### Integration Points
- Module registry 应接入 `model` 与 `render-package` 路径，为 Phase 34/35 正式渲染迁移提供模块边界。
- 隐藏模块 Markdown/Typst 应写入既有 `.teaching-design-package/work/`。
- Scheduling evidence 应进入 package model，再由两个生成的模块 Markdown 共用。
- 后续阶段会迁移正式 Typst/PDF 规则，因此 Phase 33 不应硬编码会阻碍正式 renderer migration 的 placeholder 假设。

</code_context>

<specifics>
## Specific Ideas

- 模块 id 使用稳定英文内部 id，教师可见中文名称只作为标签和后续公开产物元数据。
- 隐藏生成的模块 Markdown 应像合法 standalone-style module Markdown，但它是 package 内部产物，不是公开用户工作流。
- scheduling model 应携带稳定 source pointers，例如 `task:1/stage:2/row:3`；这些 pointer 是后续授课计划行与教学设计活动块校验的桥。
- 失败诊断优先使用 machine-readable JSON 加简短 human-readable message，方便后续 executor 断言精确失败类别。

</specifics>

<deferred>
## Deferred Ideas

- Phase 34: 迁移 `jiaoan-jihua` 正式渲染等价性。
- Phase 35: 迁移 `jiaoan-shicao` 正式渲染与严格活动校验。
- Phase 36: 强制公开课程名前缀交付与最终 PDF 合并。

</deferred>

---

*Phase: 33-Module Registry, Unified Extraction, and Scheduling Model*
*Context gathered: 2026-06-15*
