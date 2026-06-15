# Phase 36: Public Delivery, PDF Merge, and Standalone Regression - Context

**Gathered:** 2026-06-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 36 只收口 `teaching-design-package` 的最终公开交付、PDF 合并语义、隐藏诊断边界和 standalone-copy 回归。当前公开契约从 v1.14 的英文 1+1+3 过渡为课程名前缀 `1 + 1 + N`，当前 N=2：一个统一 Markdown、一个整包 PDF、两个注册模块 PDF。

本阶段继承 Phase 33/34/35 已完成事实：统一 Markdown 是唯一内容源；`teaching-plan` 与 `teaching-design` 已在 package-owned module registry 中注册；registry 顺序是模块编排和合并顺序；共享 scheduling model 与 `calendar.json` 位于 `skills/teaching-design-package/` 内；`teaching-plan` 和 `teaching-design` 已有 package-owned formal hidden Typst/PDF 路径；旧 `jiaoan-jihua` 与 `jiaoan-shicao` 只保留为外部兼容面和历史 oracle，不是 package runtime dependency。

本阶段不新增第三模块、不改变 teacher-facing unified Markdown 结构、不重新迁移旧 renderer、不修改旧 standalone jiaoan 技能、不实现跨技能通用 PDF framework。Phase 36 的完成标准是：成功 public root 只出现课程名前缀最终文件；隐藏 evidence 完整；整包 PDF 只在所有 registered module PDFs 真实存在且非空后按 registry 顺序合并；任一模块或合并失败都非零退出，且不能留下看似成功的 public directory。

</domain>

<decisions>
## Implementation Decisions

### Public Delivery Contract
- **D-01:** 成功公开目录必须严格采用课程名前缀 `1 + 1 + N`，当前 N=2。默认模板课程名为 `电气设备控制线路安装与调试`，成功 public root 只应包含：
  - `电气设备控制线路安装与调试教学资料.md`
  - `电气设备控制线路安装与调试教学资料.pdf`
  - `电气设备控制线路安装与调试授课进度计划表.pdf`
  - `电气设备控制线路安装与调试教学设计方案.pdf`
- **D-02:** 公开目录不再输出 `teaching-design-package-full.md`、`teaching-design-package.typ`、`teaching-design-package.pdf`、`teaching-plan.pdf`、`teaching-design.pdf` 作为默认成功交付文件名。英文稳定名可作为内部兼容变量、隐藏 work 文件或测试辅助，但不能成为 Phase 36 默认 public root surface。
- **D-03:** `.typ` 不属于 Phase 36 成功公开交付。统一 Typst、模块 Typst、status、manifest、model、diagnostics、log、calendar JSON、scheduling summary、module Markdown、module中间产物都必须留在 `.teaching-design-package/` 隐藏路径。
- **D-04:** 文件名从 `course_name` 派生，必须经过保守清理：去除路径分隔符、控制字符和明显不适合作为文件名的字符；若课程名缺失或清理后为空，命令必须失败并写隐藏诊断，而不是回退到英文默认名伪成功。
- **D-05:** 未来 N>2 时只允许通过 module registry 增加 `课程名<模块显示名>.pdf`。不得为每个新模块临时手写一套 public copy 规则，也不得公开模块 Markdown 或 Typst。

### Hidden Evidence And Status Truthfulness
- **D-06:** 隐藏 `.teaching-design-package/` 必须包含足够审计 Phase 36 的证据：模块 Markdown、模块 Typst、统一 scheduling model、status、diagnostics、stderr/debug logs、calendar path/hash、scheduling summary、module registry、module PDF status、merge status、merge tool、merge input order、merge input sizes、failure evidence。
- **D-07:** `status.json` 必须诚实记录实际工具和结果。若使用 `pdfunite`，记录 `merge_tool: "pdfunite"`；若使用 `qpdf`，记录 `merge_tool: "qpdf"`；若使用 Python PyMuPDF fallback，记录 `merge_tool: "python_fitz"` 或同等明确值；若没有执行合并，记录 `not_run` 或具体失败类别。
- **D-08:** `final_ready` 只能在以下条件同时满足时为 true：公开 Markdown 存在且非空；所有 registered module PDFs 已真实生成且非空；整包 PDF 已由实际 merge 工具生成且非空；hidden leakage 检查通过；review markers 与 validation errors 均为空。
- **D-09:** status 不能把“Typst 编译了一个统一平铺 PDF”伪装成整包 PDF 合并成功。`课程名教学资料.pdf` 必须由 registered module PDFs 合并得到；统一 Typst 如仍生成，只能作为隐藏/debug 或非公开辅助 evidence。

### PDF Generation And Merge Semantics
- **D-10:** Phase 36 的整包 PDF 合并必须晚于所有注册模块 PDF 生成。合并前逐一检查 registry 中每个模块的 public-module-PDF staging path 是否存在且非空；任何缺失、空文件或模块状态非 passed 都必须跳过合并并失败。
- **D-11:** 合并顺序唯一来自 module registry order，当前顺序为 `teaching-plan` -> `teaching-design`，对应公开模块 PDF 顺序为 `课程名授课进度计划表.pdf` -> `课程名教学设计方案.pdf`。不得按文件名、mtime、glob 顺序或硬编码另一路顺序合并。
- **D-12:** PDF 合并工具选择可以按本机可用性 fallback：优先 `pdfunite`、再 `qpdf`、再 Python PyMuPDF；planner 可调整优先级，但必须记录实际工具、命令/参数摘要、输入列表、输出路径、退出码和非空检查结果。
- **D-13:** 合并输出必须写入 staging/hidden 临时路径，验证非空且可被选定工具成功写出后，才发布为 `课程名教学资料.pdf`。不得先创建 public final PDF 再尝试补齐模块，避免失败后留下伪成功文件。
- **D-14:** 每个 module PDF 也应先在 staging/hidden 或临时路径中完成编译和非空验证，再发布为课程名前缀 public PDF。这样任一模块失败时 public root 不会看起来像完整交付。
- **D-15:** 如果 public root 已存在旧的成功文件，本阶段实现必须避免失败时混用旧文件形成伪成功。可选策略是先清理本次 expected public outputs，或使用 run-specific staging directory 完成后原子发布；无论选择哪种，失败后不能留下四个看似本次成功的 public files。

### Failure Semantics
- **D-16:** 任一模块 render、Typst compile、PDF 非空检查、public filename derivation、PDF merge、public-root hidden leakage、standalone-copy regression 失败，最终命令必须非零退出。
- **D-17:** 失败时允许保留隐藏 diagnostics/failure evidence，但 public root 不能包含完整的四件套，也不能包含 status、manifest、model、diagnostics、log、calendar JSON、Typst 或模块中间产物。
- **D-18:** 失败诊断至少覆盖：课程名文件名无效、模块 PDF 缺失、模块 PDF 为空、模块状态失败、merge input order mismatch、merge tool unavailable、merge tool failed、merged PDF empty、public root leakage、standalone copy failed。
- **D-19:** 如果 module registry 中未来新增模块，缺少该模块 PDF 必须让整包 PDF 合并失败；不得只合并前两个历史模块后仍宣称 final_ready。

### Standalone Regression
- **D-20:** Standalone-copy 验证必须只复制 `skills/teaching-design-package/` skill folder 到干净临时目录，并从 copied folder 运行 `scripts/teaching-design-package.sh`。验证不能依赖 repo sibling skills、旧 `jiaoan-jihua`、旧 `jiaoan-shicao`、repo-level `test/` oracle 或工作区绝对路径。
- **D-21:** Standalone-copy 验证必须证明：skill-local `references/calendar.json` 被使用；公开目录只有课程名前缀四件套；隐藏目录包含 model/status/diagnostics/work/debug/failure evidence；status 中没有 sibling skill runtime dependency。
- **D-22:** Phase 36 验收应包含负向 standalone 或 failure fixture：模拟模块 PDF 缺失、空 PDF 或 merge 工具失败时命令非零，并确认 public root 不呈现成功四件套。

### Compatibility And Documentation
- **D-23:** `skills/teaching-design-package/references/format-and-orchestration.md` 必须从 v1.14/Phase 35 的英文 public filenames 更新为课程名前缀 public contract，并保留 OpenClaw 与 Hermes Agent 需要的隐藏文件、脚本权限、sandbox/allowlist 和 fallback 说明。
- **D-24:** `SKILL.md` 的正常交付说明必须面向老师可理解的课程名文件，而不是要求用户理解内部 `teaching-plan` / `teaching-design` 文件名。Runtime adapter notes 可以说明隐藏 diagnostics 的位置，但不能把私有 runtime 语法写入 canonical 主体。
- **D-25:** 旧 `jiaoan-jihua` 和 `jiaoan-shicao` 技能不得被修改为 Phase 36 的 runtime dependency。验收应检查 package normal path 没有调用 sibling scripts。

### Claude's Discretion
- Planner 可自行决定 staging 目录命名、原子发布方式、PDF merge helper 的具体实现语言和工具优先级，但必须满足真实模块 PDF 后合并、registry 顺序、诚实 status、失败非零、public root 不伪成功。
- Planner 可自行决定是否保留隐藏统一 Typst/PDF 作为 debug evidence；但成功公开目录不得出现 `.typ`，且 `课程名教学资料.pdf` 的成功语义必须来自模块 PDF merge。
- Planner 可自行选择 verification artifact 的具体目录和文件名；但必须留下可审计命令、stdout/stderr 摘要、status excerpts、public root listing、hidden evidence listing、standalone-copy 结果和 negative failure 结果。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope
- `.planning/ROADMAP.md` — Phase 36 goal、dependencies、requirements、success criteria。
- `.planning/REQUIREMENTS.md` — `TDPKG-ART-01`、`TDPKG-ART-02`、`TDPKG-ART-03`、`TDPKG-PDF-01`、`TDPKG-PDF-02`、`TDPKG-PDF-03`、`TDPKG-PDF-04` 的 authoritative requirement text。
- `.planning/PROJECT.md` — v1.15 course-name-prefixed public delivery discipline, hidden module discipline, scheduling discipline, failure discipline。
- `.planning/STATE.md` — Phase 35 complete state and next-up context。
- `.planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-CONTEXT.md` — module registry order, hidden module artifact paths, shared scheduling model, skill-local calendar decisions。
- `.planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-SUMMARY.md` — Phase 33 delivered module registry and scheduling evidence。
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-CONTEXT.md` — package-owned `teaching-plan` renderer, registry-order merge precondition, old `jiaoan-jihua` boundary。
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-SUMMARY.md` — Phase 34 delivered formal teaching-plan Typst/PDF behavior and strict sum evidence。
- `.planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/35-CONTEXT.md` — package-owned `teaching-design` renderer, cross-module validation, hidden diagnostics, Phase 36 deferral。
- `.planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/35-SUMMARY.md` — Phase 35 delivered formal teaching-design Typst/PDF behavior and mismatch diagnostics。
- `.planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/35-VERIFICATION.md` — Phase 35 verified commands and evidence that Phase 36 should preserve.

### Package Internals
- `skills/teaching-design-package/SKILL.md` — canonical skill workflow and runtime adapter notes under standalone boundary。
- `skills/teaching-design-package/references/format-and-orchestration.md` — package artifact contract, module registry, scheduling rules, hidden diagnostics, current public filename text to update。
- `skills/teaching-design-package/templates/teaching-design-package-full.md` — unified Markdown source shape and default `course_name` fixture。
- `skills/teaching-design-package/scripts/teaching-design-package.sh` — current command surface, hidden workdir/status/diagnostics, public PDF compile logic, leakage check, status writer。
- `skills/teaching-design-package/scripts/package-model.js` — module registry metadata, display names, `course_name`, scheduling model, validation evidence。
- `skills/teaching-design-package/scripts/teaching-plan-renderer.js` — package-owned teaching-plan formal Typst renderer。
- `skills/teaching-design-package/scripts/teaching-design-renderer.js` — package-owned teaching-design formal Typst renderer。
- `skills/teaching-design-package/references/calendar.json` — package-owned calendar resource required for standalone scheduling。

### Scheduling And Prior Contracts
- `references/scheduling-contract.md` — calendar/hour/week/weekday consumption semantics that must remain the single scheduling authority。
- `scripts/derive-scheduling-fixture.py` — executable scheduling evidence from prior contract work, useful for regression expectations。

### External Compatibility References
- `skills/jiaoan-jihua/SKILL.md` — legacy standalone teaching-plan skill must remain external compatibility surface only。
- `skills/jiaoan-shicao/SKILL.md` — legacy standalone teaching-design skill must remain external compatibility surface only。

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/teaching-design-package/scripts/package-model.js`: already exposes `MODULE_REGISTRY` with order `teaching-plan` then `teaching-design`, module display names `授课进度计划表` and `教学设计方案`, and the course metadata needed for filename prefix derivation.
- `skills/teaching-design-package/scripts/teaching-design-package.sh`: already centralizes public output creation, hidden model/status/diagnostics, Typst compile calls, non-empty PDF checks, and public-root leakage checks. Phase 36 should evolve this boundary rather than create a second command surface.
- `write_status` in `teaching-design-package.sh`: already records public outputs and PDF statuses, but currently uses English filenames and treats `teaching-design-package.pdf` as directly compiled from unified Typst. Phase 36 must change this to course-name public files and real merge status.
- `compile_pdf` and `pdf_nonempty` in `teaching-design-package.sh`: existing non-empty checks can be reused for module PDFs before merge.
- `teaching-plan-renderer.js` and `teaching-design-renderer.js`: both formal renderers already consume the shared package model and write hidden Typst; Phase 36 should compile their PDFs and merge those registered module outputs.

### Established Patterns
- Hidden evidence belongs under `.teaching-design-package/`, especially `model.json`, `status.json`, `diagnostics.json`, `work/`, `debug/`, and `failure-diagnostics/`.
- Registry order is already documented as orchestration and future PDF merge order; Phase 36 should make it executable and tested.
- Package-owned standalone boundary is non-negotiable: normal render must work from only the copied `teaching-design-package` skill folder and its skill-local `calendar.json`.
- Prior phases already require old `jiaoan-jihua` and `jiaoan-shicao` to remain available but not package runtime dependencies.

### Integration Points
- Replace public copy targets in `cmd_render_package` from English names to derived course-name filenames.
- Move public publication behind staging so failures cannot leave a complete-looking public root.
- Replace direct compile of `teaching-design-package.typ` to `teaching-design-package.pdf` as final package success with a merge helper that consumes registry-ordered module PDFs.
- Extend `write_status`/`write_diagnostics` with merge tool, merge order, module PDF paths/sizes/statuses, public artifact list, and final readiness checks.
- Extend `assert_no_public_leakage` so it rejects `.typ`, status, manifest, model, diagnostics, logs, calendar JSON, hidden work artifacts, and old English successful filename surface in the public root.
- Add standalone-copy and negative failure verification around missing/empty module PDFs and merge failure.

</code_context>

<specifics>
## Specific Ideas

- Treat `课程名教学资料.pdf` as the final merged artifact only. If a unified Typst/PDF is still useful for debugging, keep it hidden and make status call it debug evidence, not final delivery.
- A robust publish sequence is: build hidden model/work Typst -> compile module PDFs to staging -> verify every registry module PDF exists/non-empty -> merge staging module PDFs in registry order -> verify merged PDF non-empty -> publish the four course-name public files -> run leakage check -> mark final_ready.
- Negative tests should list the public root after failure and assert the exact four successful public filenames are not all present.
- Status should include a `merge_inputs` array in the same order as `modules.registry`, with module id, display name, staging path, public path, byte size, status, and source hidden Typst.

</specifics>

<deferred>
## Deferred Ideas

- Future phase: add third or later modules by extending the module registry and automatically producing `课程名<模块显示名>.pdf`.
- Future phase: consider a shared PDF merge helper across document skills only after this package-specific merge contract is stable.

</deferred>

---

*Phase: 36-Public Delivery, PDF Merge, and Standalone Regression*
*Context gathered: 2026-06-15*
