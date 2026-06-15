# Phase 34: Teaching Plan Formal Renderer Migration - Context

**Gathered:** 2026-06-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 34 只迁移 `授课进度计划表` formal renderer：让 `teaching-design-package` 用 package-owned 内部规则生成正式 `课程名授课进度计划表.pdf`，并证明其格式与当前可接受的 `jiaoan-jihua` baseline 一致或可接受等价。

本阶段继承 Phase 33 已完成的统一 Markdown 解析、module registry、隐藏 `teaching-plan.md`、skill-local `calendar.json`、共享 scheduling model 和隐藏 diagnostics。Phase 34 不迁移 `jiaoan-shicao` 教学设计方案 renderer，不做最终公开课程名前缀交付收口，不做整包 PDF merge，也不修改旧 `skills/jiaoan-jihua`。这些分别属于 Phase 35、Phase 36 或外部兼容面维护。

</domain>

<decisions>
## Implementation Decisions

### Formal Renderer Ownership
- **D-01:** Phase 34 的核心输出是 package-owned `teaching-plan` formal renderer。实现必须位于 `skills/teaching-design-package/` 内部，并由 `teaching-design-package` 的正常命令路径调用。
- **D-02:** 旧 `skills/jiaoan-jihua` 只允许作为只读格式参考和测试 oracle。不得修改旧 skill 文件，不得在 package runtime 中调用 `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`，不得要求 standalone package 安装 sibling skill。
- **D-03:** 迁移目标不是复用旧 handoff 架构，而是把已接受的 `jiaoan-jihua` 官方五列表格格式规则迁入 package internals。隐藏 `teaching-plan.md` 可作为 package 内部模块输入，但它不是 teacher-maintained source。
- **D-04:** `teaching-design-package` 内部可借鉴旧脚本的解析和 Typst emission 规则，但 planner/executor 必须避免复制旧目标 Typst fixture 作为生成源。fixture 只用于生成后 diff/hash/PDF evidence。
- **D-05:** Phase 34 只需要 formalize `teaching-plan` module 的 Typst/PDF。Phase 33 生成的 placeholder module Typst 必须被替换为正式授课进度计划表 Typst，至少对 `teaching-plan` 不再带有 “Pre-formal surface only” 的占位语义。

### Legacy Table Contract
- **D-06:** Package 内部 formal renderer 必须生成旧 `jiaoan-jihua` 当前可接受的官方五列表格结构：标题、课程信息 grid、五列表格、签字 grid、A4 页面、`STSong` 字体、`@preview/cuti:0.2.1` fake-bold import/show rule、以及 `// jiaoan-jihua official template` 或等价 provenance 注释。
- **D-07:** 表格列宽沿用 accepted baseline：`(3.15cm, 8.51cm, 1.12cm, 1.29cm, 1.27cm)`，列语义为学习环节、教学内容、周次、星期、学时。
- **D-08:** 学习任务标题、学习环节标题、教学内容行顺序必须来自统一 Markdown 的 `# 授课进度计划` section，经 Phase 33 model/hidden module 传递后保持源顺序；renderer 不得按标题、日期、周次或任务名重排。
- **D-09:** 学习任务总学时由其所有授课计划内容行课时严格求和；学习环节 `rowspan` 由该环节内容行数决定；每个内容行的 `学时` 单元格显示该行原始课时。
- **D-10:** 旧格式中的学年/学期/周次范围标题、每行周次、星期和学时单元格必须来自 package shared scheduling model，而不是在 formal renderer 内重新跑一套 calendar 推导。

### Schedule And Hour Authority
- **D-11:** 统一 Markdown 仍是唯一内容源；`# 授课进度计划` 是课时唯一原始来源。`# 教学设计方案` 不得反向改写 teaching-plan 课时或日期。
- **D-12:** `calendar.json` 必须使用 `skills/teaching-design-package/references/calendar.json`，并保留 standalone-copy 行为。Phase 34 不能恢复读取 `skills/jiaoan-jihua/references/calendar.json` 的 runtime 依赖。
- **D-13:** 学年、学期、课程起止日期、任务起止日期、周次、星期、每日课时消耗必须由 skill-local calendar、`first_teaching_day` 和授课计划行课时严格推导。自然日顺推、手填 YAML、以及 renderer 内重复推导都不接受。
- **D-14:** `daily_hours` 在 Phase 34 继续沿用 package-owned 默认或 future skill-local config；它不是教师统一 YAML 字段。若实现为了验证暴露参数，也必须写入 hidden model/status/diagnostics。
- **D-15:** `TDPKG-VAL-01` 在本阶段必须关闭：每个学习任务总课时和课程总课时均为授课计划行课时严格求和，并在 hidden diagnostics/status 中可审计。

### Evidence And Equivalence
- **D-16:** 等价性验收分两层：Typst text/structure evidence 证明 package 生成的 teaching-plan Typst 与旧 accepted `jiaoan-jihua` formal surface 一致或可接受等价；PDF evidence 证明 `课程名授课进度计划表.pdf` 真实生成且非空。
- **D-17:** Fixture baseline 至少包括 `test/1.10/电气设备控制线路安装与调试授课计划.md`、`test/1.10/电气设备控制线路安装与调试授课计划.typ`、`test/1.10/电气设备控制线路安装与调试授课计划.pdf`，并补充从 `skills/teaching-design-package/templates/teaching-design-package-full.md` 经 package path 生成的 module evidence。
- **D-18:** 可接受等价允许 provenance 注释、source path、generated timestamp 或 output filename 不同；不允许表格列宽、标题层级、课程信息字段、任务/环节/内容顺序、周次/星期/学时、签字 grid 或正文内容发生实质漂移。
- **D-19:** 验证必须证明旧 `jiaoan-jihua` public interface 未变：旧脚本仍能运行其 example/render/expected-typ 路径，且 `git diff --name-only -- skills/jiaoan-jihua` 为空。
- **D-20:** 验证必须证明 runtime independence：standalone copy 只包含 `skills/teaching-design-package` 时仍能生成 formal teaching-plan Typst/PDF；生成的 hidden model/status/diagnostics 中不得出现 `skills/jiaoan-jihua` runtime path。

### Output Surface In Phase 34
- **D-21:** Phase 34 可先在 existing public naming surface 上证明 `teaching-plan.pdf` 或 course-name target 的正式内容；但最终 Phase 36 会收口为课程名前缀 `课程名授课进度计划表.pdf`。若 Phase 34 已实现课程名前缀输出，不得破坏 Phase 36 的 `1 + 1 + N` 公开契约。
- **D-22:** Hidden artifacts 仍应位于 `.teaching-design-package/work/`、`.teaching-design-package/debug/`、`.teaching-design-package/failure-diagnostics/`。正式 module Typst 应隐藏，public root 不应泄漏 `teaching-plan.typ`、model、status、diagnostics、calendar JSON 或 logs。
- **D-23:** `render-package --pdf` 的成功语义仍必须诚实。如果 teaching-plan formal render 失败、Typst compile 失败或 PDF 为空，应非零退出并写 hidden diagnostics；不能留下看似成功的 public delivery root。

### Claude's Discretion
- Planner 可自行决定把 teaching-plan formal renderer 做成 Node module、Bash helper、或 package-model 的 renderer 子模块；但必须保持 package-owned、standalone、可测试，并避免扩大为通用 renderer framework。
- Planner 可决定等价性比较采用 strict diff、normalized diff、structural grep/assertions、PDF text/render smoke test 或组合方式；但必须明确记录哪些差异被允许、哪些差异会 fail。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope
- `.planning/ROADMAP.md` — Phase 34 goal、dependencies、requirements、success criteria。
- `.planning/REQUIREMENTS.md` — `TDPKG-LEGACY-01`、`TDPKG-LEGACY-03`、`TDPKG-LEGACY-04`、`TDPKG-VAL-01` 的 authoritative requirement text。
- `.planning/PROJECT.md` — v1.15 package-owned modular renderer direction and standalone boundary。
- `.planning/STATE.md` — 当前 GSD 位置、Phase 33 completion context。
- `.planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-CONTEXT.md` — Phase 33 locked decisions for unified Markdown, module registry, scheduling, hidden artifacts。
- `.planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-SUMMARY.md` — Phase 33 provided files and next phase readiness。
- `.planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-VERIFICATION.md` — Phase 33 verified behaviors and known evidence commands。

### Package Internals
- `skills/teaching-design-package/SKILL.md` — canonical skill workflow and runtime adapter notes under standalone boundary。
- `skills/teaching-design-package/references/format-and-orchestration.md` — package Markdown contract, module registry, scheduling rules, public/hidden artifact boundaries, rendering semantics。
- `skills/teaching-design-package/templates/teaching-design-package-full.md` — unified Markdown source shape and package fixture input。
- `skills/teaching-design-package/scripts/package-model.js` — Phase 33 package-owned parser, scheduling model, module registry, frontmatter generation。
- `skills/teaching-design-package/scripts/teaching-design-package.sh` — current command surface, hidden workdir/status/diagnostics, placeholder module Typst path to replace for teaching-plan formal output。
- `skills/teaching-design-package/references/calendar.json` — package-owned calendar resource required for standalone scheduling。

### Legacy Teaching-Plan Reference
- `skills/jiaoan-jihua/references/format-and-rendering.md` — accepted `jiaoan-jihua` frontmatter/body/table/rendering contract。
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` — read-only implementation reference for official table emission and legacy verification path。
- `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md` — legacy standalone example shape, read-only reference。
- `skills/jiaoan-jihua/references/calendar.json` — read-only historical calendar reference; not a runtime package dependency。

### Scheduling And Fixtures
- `references/scheduling-contract.md` — authoritative calendar/hour/week/weekday consumption semantics。
- `scripts/derive-scheduling-fixture.py` — executable scheduling evidence from prior contract work。
- `test/1.10/电气设备控制线路安装与调试授课计划.md` — legacy teaching-plan source fixture for equivalence tests。
- `test/1.10/电气设备控制线路安装与调试授课计划.typ` — accepted legacy Typst oracle for generated-output comparison。
- `test/1.10/电气设备控制线路安装与调试授课计划.pdf` — accepted legacy PDF baseline for smoke/equivalence checks。
- `test/validation/jiaoan-jihua-original/VERIFY.md` — standalone original jiaoan-jihua validation evidence and command shape。
- `test/validation/blackbox-jiaoan-jihua/VERIFY.md` — black-box jiaoan-jihua validation evidence if planner needs broader oracle coverage。

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/teaching-design-package/scripts/package-model.js`: already parses unified frontmatter, extracts `# 授课进度计划`, builds `teaching-plan` module frontmatter, derives row/task/course scheduling evidence from skill-local calendar, and exposes `scheduling.row_consumption_summary` plus `schedule.tasks`.
- `skills/teaching-design-package/scripts/teaching-design-package.sh`: already writes hidden module Markdown, hidden placeholder module Typst, public PDF status, hidden diagnostics, failure diagnostics, and public-root leakage checks.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`: read-only source of accepted formal table emission details including `parse_official_jihua_body`, `assign_schedule_cells`, `emit_official_jihua_head`, `emit_official_jihua_table`, and `emit_official_signature_grid`.
- `skills/jiaoan-jihua/references/format-and-rendering.md`: concise rule source for official five-column table, column widths, task/stage row handling, source-order parsing, and fixture verification.

### Established Patterns
- Package-owned standalone boundary is non-negotiable: current `teaching-design-package` must not call sibling scripts at runtime and must work when only that skill folder is copied.
- Hidden diagnostics pattern is established: `.teaching-design-package/model.json`, `status.json`, `diagnostics.json`, `work/`, `debug/`, and `failure-diagnostics/`.
- Phase 33 intentionally left module Typst pre-formal. Phase 34 should replace only the `teaching-plan` side with formal renderer behavior and leave teaching-design formal migration to Phase 35.
- Current package scheduling model already uses skill-local `calendar.json`, not the old jiaoan calendar, and records path/hash/policy evidence.

### Integration Points
- Replace `write_placeholder_pdf_typst "$model_path" ... "授课进度计划"` with a formal teaching-plan Typst generator fed by the model's `schedule.tasks` and `scheduling` evidence.
- Keep `write_module_markdown_files` as hidden module Markdown generation; formal renderer may render from model directly or from hidden module Markdown, but scheduling facts must come from the shared model.
- Extend `write_status`/`write_diagnostics` to record teaching-plan formal renderer status, equivalence evidence pointers, calendar hash, row totals, and legacy runtime independence evidence if implementation needs new fields.
- Add verification around `render-package --pdf`, standalone copy, no public-root hidden leakage, no sibling path references, old skill unchanged, and legacy fixture equivalence.

</code_context>

<specifics>
## Specific Ideas

- Treat `# 授课进度计划` as both the visible teacher source and the sole source-order list for formal table rows.
- Use stable source pointers such as `task:1/stage:2/row:3` to connect model row evidence to formal table cells and diagnostics.
- Prefer machine-readable equivalence evidence under `.teaching-design-package/` or `.planning/phases/34-.../`, with a short human-readable summary in `34-VERIFICATION.md` during execute.
- Keep old `jiaoan-jihua` untouched even if duplicate code feels unattractive; Phase 34 is intentionally a package-internal migration, not a shared library refactor.

</specifics>

<deferred>
## Deferred Ideas

- Phase 35: migrate `jiaoan-shicao` teaching-design formal renderer and strict activity mapping/cross-module validation.
- Phase 36: enforce course-name-prefixed public `1 + 1 + N` output contract and final PDF merge semantics.
- Future phase: consider extracting a shared formal jiaoan renderer library only after package-owned migration is stable and both old standalone/public surfaces are protected.

</deferred>

---

*Phase: 34-Teaching Plan Formal Renderer Migration*
*Context gathered: 2026-06-15*
