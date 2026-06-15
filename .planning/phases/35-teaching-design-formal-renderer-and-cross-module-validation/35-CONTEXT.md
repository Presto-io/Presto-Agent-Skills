# Phase 35: Teaching Design Formal Renderer and Cross-Module Validation - Context

**Gathered:** 2026-06-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 35 只迁移 `教学设计方案` formal renderer 并补齐严格跨模块校验：让 `teaching-design-package` 用 package-owned 内部规则生成正式 `课程名教学设计方案.pdf`，并强制教案任务、环节、活动、课时、日期与 Phase 33/34 已建立的 teaching-plan scheduling model 一致。

本阶段继承 Phase 33/34 已完成事实：统一 Markdown 是唯一内容源；`# 授课进度计划` 是课时和排课唯一原始来源；`teaching-plan` formal renderer 已 package-owned；`calendar.json` 位于 `skills/teaching-design-package/references/calendar.json`；旧 `skills/jiaoan-shicao` 只读参考，不得修改，也不得作为 package runtime dependency。

本阶段不做 Phase 36 的最终课程名前缀公开交付收口、不做最终整包 PDF merge 语义重写、不新增第三模块、不重构旧 standalone `jiaoan-shicao`。Phase 35 的完成标准是 `teaching-design` 模块正式渲染、旧格式等价证据、严格映射校验与隐藏失败诊断。

</domain>

<decisions>
## Implementation Decisions

### Formal Renderer Ownership
- **D-01:** Phase 35 的核心输出是 package-owned `teaching-design` formal renderer。实现必须位于 `skills/teaching-design-package/` 内部，并由 `teaching-design-package` 正常 `render-package` / `render-package --pdf` 路径调用。
- **D-02:** 旧 `skills/jiaoan-shicao` 只能作为只读格式参考和测试 oracle。不得修改旧 skill 文件，不得在 package runtime 中调用 `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`，不得要求 standalone package 安装 sibling skill。
- **D-03:** 迁移目标是把旧 `jiaoan-shicao` 当前可接受的正式教学设计方案格式规则迁入 package internals，包括封面/标题层级、学习任务分析、教学活动设计横向表、学业评价、官方表格宽度和 pagebreak/chapter 分组规则。
- **D-04:** 隐藏 `.teaching-design-package/work/teaching-design.md` 可作为 package 内部模块输入，但它不是 teacher-maintained source。正式 renderer 可从共享 model 或隐藏模块 Markdown 渲染，但时间、课时、任务总量和 activity mapping 必须来自同一个 scheduling model。
- **D-05:** Phase 35 必须替换 Phase 33/34 留下的 `teaching-design.typ` pre-formal placeholder；生成的 hidden `teaching-design.typ` 不得再带有 `Pre-formal surface only` 或等价占位语义。

### Scheduling Model Authority
- **D-06:** 统一 Markdown 仍是唯一内容源，其中 `# 授课进度计划` 是所有课时和排课事实的唯一原始来源。`# 教学设计方案` 提供教学设计正文结构和文本，但不能独立拥有任务课时、活动课时、起止日期或课程总时长。
- **D-07:** `calendar.json` 必须继续使用 `skills/teaching-design-package/references/calendar.json`，保持 standalone-copy 行为。Phase 35 不能读取 `skills/jiaoan-shicao/references/calendar.json` 作为 runtime resource。
- **D-08:** 教案中的每个 `课时：xH` 必须由对应学习任务在 scheduling model 中的 `task.total_hours` 填充或验证；教师正文中的同名字段若存在且不一致，必须失败。
- **D-09:** 教案活动 `##### xH` 必须由对应授课计划行的原始 row hours 派生或验证。活动课时不得由教学设计正文自行求和成为新的权威来源。
- **D-10:** 任务起止日期、课程 `use_time`、每个任务的 `起止日期` 均由 shared scheduling model 的真实 calendar consumption 派生。自然日顺推、renderer 内重复计算、手填 YAML、或从 teaching-design 正文反推日期都不接受。

### Task / Stage / Activity Mapping
- **D-11:** 映射主键顺序为“学习任务 + 学习环节 + 活动顺序”。标题归一化或相似度只能作为辅助校验和诊断信息，不能替代结构位置映射。
- **D-12:** `# 授课进度计划` 中每个 `##` 学习任务必须对应 `# 教学设计方案` 中一个学习任务分析块和一个或多个教学活动设计块；任务数量不一致必须 hard fail。
- **D-13:** 每个授课计划 `###` 学习环节必须在对应教案任务下有对应环节。环节数量、源顺序或标题对应不一致必须 hard fail，并写出 task/stage source pointer。
- **D-14:** 每个授课计划内容行 `task:i/stage:j/row:k` 必须映射到对应教案活动 `##### xH`。活动数量不一致、活动顺序漂移、活动课时不一致或无法定位对应活动都必须 hard fail。
- **D-15:** 标题对应应记录双重证据：source pointer 的结构位置是主判据；规范化标题比较用于发现“位置相同但标题不同”的漂移。标题不一致时失败，不应静默按相似标题重排。
- **D-16:** planner 应避免把旧 `活动课时：80` / `教学活动课时：80` 的总量校验当成最终校验。Phase 35 必须升级到 per-task、per-stage、per-activity 粒度；总量相等但局部错位也必须失败。

### Legacy Formal Format Contract
- **D-17:** Package formal renderer 必须生成旧 `jiaoan-shicao` 当前可接受的正式 Typst/PDF surface，而不是统一 Markdown 平铺文档。至少覆盖学习任务分析页、教学活动设计表、学业评价页、课程属性/总课时/use_time/教师/班级等字段。
- **D-18:** 活动设计表必须沿用旧 accepted official table behavior：横向页面、`25.04cm` 活动表总宽、窄 `课时分配` 列、chapter/pagebreak scoped columns、教学方法与手段逐行呈现。
- **D-19:** Fixture 等价验收至少使用 `test/1.10/电气设备控制线路安装与调试教案.md`、`.typ`、`.pdf` 作为只读 oracle；允许 package provenance/source 注释等非实质差异，不允许标题层级、表格宽度、任务/环节/活动顺序、课时、日期、评价结构或正文内容漂移。
- **D-20:** 验证必须证明旧 `jiaoan-shicao` public interface 未变：旧脚本仍可独立运行 example/render/expected-typ 路径，且 `git diff --name-only -- skills/jiaoan-shicao` 为空。

### Failure Diagnostics And Output Semantics
- **D-21:** 任一映射不一致必须非零退出，并写隐藏 diagnostics/status；不能生成最终成功产物，也不能让 public root 看起来成功。
- **D-22:** 隐藏诊断至少记录 mismatch class、module id、task/stage/row/activity source pointer、teaching-plan title/hour/date、teaching-design title/hour/date、expected vs actual、calendar path/hash、model version 和 source Markdown path。
- **D-23:** 失败类别需要覆盖：任务数量不一致、环节数量不一致、活动数量不一致、任务标题不一致、环节标题不一致、活动标题不一致、`课时：xH` 不一致、`##### xH` 不一致、任务起止日期不一致、缺少教学设计块、旧格式渲染失败、PDF 编译失败、public-root hidden leakage。
- **D-24:** 成功 public root 在 Phase 35 仍可沿用当前英文 filename surface；Phase 36 再收口为课程名前缀 `1 + 1 + N`。但 Phase 35 成功时 hidden `teaching-design.typ` 必须是 formal output，public root 不得泄漏 `teaching-design.typ`、module Markdown、model、status、diagnostics、calendar JSON 或 logs。
- **D-25:** `render-package --pdf` 的成功语义必须诚实：若 teaching-design formal render、Typst compile 或 PDF non-empty check 失败，则命令失败并保留 hidden evidence。

### Claude's Discretion
- Planner 可自行选择把 teaching-design renderer 做成 Node helper、Bash helper、AWK 迁移或 package-model renderer 子模块；但必须 package-owned、standalone、可测试，并避免扩大为通用 renderer framework。
- Planner 可自行选择 normalized diff、structural assertions、PDF smoke test、fixture hash evidence 的组合；但必须明确记录哪些差异允许、哪些差异失败。
- Planner 可决定如何把 unified `# 教学设计方案` 正文整理成旧 `jiaoan-shicao` 的任务分析/活动表/评价结构，只要不改变 teacher-facing unified Markdown contract，并且所有时间与课时来自 scheduling model。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope
- `.planning/ROADMAP.md` — Phase 35 goal、dependencies、requirements、success criteria。
- `.planning/REQUIREMENTS.md` — `TDPKG-LEGACY-02`、`TDPKG-VAL-02`、`TDPKG-VAL-03`、`TDPKG-VAL-04` 的 authoritative requirement text。
- `.planning/PROJECT.md` — v1.15 package-owned modular renderer direction and standalone boundary。
- `.planning/STATE.md` — 当前 GSD 位置与 Phase 34 completion context。
- `.planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-CONTEXT.md` — unified Markdown、module registry、shared scheduling model、hidden artifact decisions。
- `.planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-SUMMARY.md` — Phase 33 provided files and next-phase readiness。
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-CONTEXT.md` — teaching-plan formal renderer ownership, schedule/hour authority, hidden artifact decisions。
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-SUMMARY.md` — Phase 34 delivered renderer and strict sum evidence。
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-VERIFICATION.md` — Phase 34 verified commands, equivalence behavior, standalone-copy evidence。

### Package Internals
- `skills/teaching-design-package/SKILL.md` — canonical skill workflow and runtime adapter notes under standalone boundary。
- `skills/teaching-design-package/references/format-and-orchestration.md` — package Markdown contract, module registry, scheduling rules, hidden diagnostics, Phase 34/35 rendering semantics。
- `skills/teaching-design-package/templates/teaching-design-package-full.md` — unified Markdown source shape and package fixture input。
- `skills/teaching-design-package/scripts/package-model.js` — Phase 33/34 package-owned parser, module registry, scheduling model, validation evidence, current teaching-design block extraction。
- `skills/teaching-design-package/scripts/teaching-design-package.sh` — current command surface, hidden workdir/status/diagnostics, `teaching-design.typ` placeholder path to replace。
- `skills/teaching-design-package/scripts/teaching-plan-renderer.js` — Phase 34 pattern for package-owned formal renderer consuming shared model。
- `skills/teaching-design-package/references/calendar.json` — package-owned calendar resource required for standalone scheduling。

### Legacy Teaching-Design Reference
- `skills/jiaoan-shicao/references/format-and-rendering.md` — accepted `jiaoan-shicao` frontmatter/body/rendering/table-width contract。
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` — read-only implementation reference for legacy command surface and rendering behavior。
- `skills/jiaoan-shicao/scripts/render_v110_typst.awk` — read-only v1.10 strict fixture renderer reference if implementation needs detailed Typst emission behavior。
- `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md` — legacy standalone example shape, read-only reference。
- `skills/jiaoan-shicao/references/calendar.json` — read-only historical calendar reference; not a runtime package dependency。

### Scheduling And Fixtures
- `references/scheduling-contract.md` — authoritative calendar/hour/week/weekday consumption semantics。
- `scripts/derive-scheduling-fixture.py` — executable scheduling evidence from prior contract work。
- `test/1.10/电气设备控制线路安装与调试教案.md` — legacy teaching-design source fixture for equivalence tests。
- `test/1.10/电气设备控制线路安装与调试教案.typ` — accepted legacy Typst oracle for generated-output comparison。
- `test/1.10/电气设备控制线路安装与调试教案.pdf` — accepted legacy PDF baseline for smoke/equivalence checks。
- `test/validation/jiaoan-shicao-original/VERIFY.md` — standalone original jiaoan-shicao validation evidence and command shape, if present。
- `test/validation/blackbox-jiaoan-shicao/VERIFY.md` — black-box jiaoan-shicao validation evidence, if present。

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/teaching-design-package/scripts/package-model.js`: already builds `modules.registry`, `modules.items`, `schedule.tasks[]`, `scheduling`, `derived.total_hours/use_time`, `validation.strict_sum_evidence`, and basic `teaching_design.activity_hours` total check.
- `skills/teaching-design-package/scripts/teaching-design-package.sh`: already writes hidden module Markdown, public Typst/PDF files, hidden status/diagnostics, public-root leakage checks, and routes `teaching-plan.typ` through a formal renderer.
- `skills/teaching-design-package/scripts/teaching-plan-renderer.js`: provides a useful Phase 34 pattern for a package-owned formal renderer fed by the shared model and verified against a legacy fixture without runtime sibling dependency.
- `skills/jiaoan-shicao/references/format-and-rendering.md` and `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`: read-only source of accepted formal teaching-design structure, activity table widths, v1.10 fixture path, and public command compatibility.

### Established Patterns
- Package-owned standalone boundary is non-negotiable: normal package rendering must work from a copied `skills/teaching-design-package` folder only.
- Hidden diagnostics pattern is established under `.teaching-design-package/model.json`, `status.json`, `diagnostics.json`, `work/`, `debug/`, and `failure-diagnostics/`.
- Phase 34 established formal module renderer pattern: renderer consumes the shared package model, not a sibling skill, and normalized legacy equivalence allows only non-substantive provenance differences.
- Phase 34 also established strict raw-hour authority via `validation.strict_sum_evidence`; Phase 35 should extend that evidence from row/stage/task/course totals to per teaching-design task/stage/activity mapping.

### Integration Points
- Replace `write_placeholder_pdf_typst "$model_path" ... "教学设计方案"` in `teaching-design-package.sh` with a package-owned formal teaching-design renderer.
- Extend `package-model.js` to parse `# 教学设计方案` into task/stage/activity structures with source pointers aligned to `schedule.tasks[].stages[].rows[]`.
- Extend diagnostics/status to record `teaching_design_formal_renderer`, `cross_module_validation`, per-activity mapping evidence, mismatch classes, and legacy independence evidence.
- Add verification around `render-package --pdf`, fixture equivalence, standalone copy, no public-root hidden leakage, no sibling path references, old `skills/jiaoan-shicao` unchanged, and mismatch fixtures for task/stage/activity/hour/date failures.

</code_context>

<specifics>
## Specific Ideas

- Use stable pointers such as `task:1/stage:2/row:3` on the teaching-plan side and `task:1/stage:2/activity:3` on the teaching-design side; diagnostics should print both.
- Normalize titles only for comparison reporting, for example trimming whitespace and punctuation. Do not use fuzzy title matching to remap source order.
- Build negative fixtures that prove total hours can match while a single activity hour/title/order mismatch still fails.
- Preserve old official teaching-design activity table width behavior exactly enough that future visual/PDF checks can catch table regression, especially the `25.04cm` total width and narrow `课时分配` column.

</specifics>

<deferred>
## Deferred Ideas

- Phase 36: enforce course-name-prefixed public `1 + 1 + N` output contract and final PDF merge semantics.
- Future phase: consider a shared formal jiaoan renderer library only after package-owned `teaching-plan` and `teaching-design` migrations are stable and old standalone surfaces are protected.

</deferred>

---

*Phase: 35-Teaching Design Formal Renderer and Cross-Module Validation*
*Context gathered: 2026-06-15*
