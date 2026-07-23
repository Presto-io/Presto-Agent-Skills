# Phase 49: 聚合验证、跨 Runtime 与发布验收 - Context

**Gathered:** 2026-07-18
**Status:** Ready for planning

<domain>
## Phase Boundary

本阶段把已经完成的 graduate-resume 功能收束为可重复、可审计的发布验收：验证真实 1/2 页 A4 PDF 与 PNG 版式证据，提供覆盖完整工作流和故障场景的固定聚合回归，证明六个承诺 runtime 的 whole-folder 安装与显式 CLI fallback，并完成至少一个非开发环境中的字体固定人工 UAT。本阶段不新增简历事实能力、主题家族、在线编辑、抓取或 AI 渲染。

</domain>

<decisions>
## Implementation Decisions

### Aggregate Evidence Authority
- **D-01:** 对外聚合验收必须使用字面固定、顺序固定的 gate registry；`required` 与实际 `called` 必须精确相等，不允许动态发现、动态跳过或按环境减少 gate。
- **D-02:** 顶层结论必须从子测试原始输出、重开的产物和 hash 重新计算，不能直接信任生产者写入的 `passed`、计数或常量证据。
- **D-03:** 聚合命令覆盖正常、无照片、多目标、资格缺口、内容压力和故障注入 fixture，并同时证明 schema、定向、分页、发布与回滚边界。
- **D-04:** Phase 48 的 `48-REVIEW.md` 质量债务与缺失的安全执行报告属于发布前置条件；可以独立修复和复核，但最终发布验收不得在这些债务仍未处置时给出无条件 PASS。

### PDF And PNG Acceptance
- **D-05:** `verify` 必须重新打开 PDF/PNG 观察产物，不以文件存在、非空或可打开作为充分条件。
- **D-06:** 每份证据至少验证真实 A4、仅 1 或 2 页、主题、照片模式、页数、模块边界、正式命名与目标 metadata 一致；结构声明要从 PDF/PNG 与对应最终 Markdown/Typst 交叉重算。
- **D-07:** 验收证据保存于调用方授权的 verify workdir，不进入正式 delivery root；证据 JSON/Markdown、PNG 和日志不得成为 current sidecar。
- **D-08:** 固定 fixture、Typst 0.15.0、受控 CJK 字体清单、字体 hash、PDF/PNG hash 和运行环境信息必须进入同一验收链，便于复现和人工比对。

### Six Runtime Installation Verification
- **D-09:** 六个 runtime 共享唯一 canonical `skills/graduate-resume/SKILL.md`；不得为 Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw 或 Hermes Agent 维护六份分叉技能逻辑。
- **D-10:** 每个 runtime 的验收都必须证明完整 skill folder 可读、支持文件相对路径有效、public shell CLI 可显式调用、依赖可检查、授权 workdir/delivery root 可写；自动发现不是通过条件。
- **D-11:** runtime 自动 discovery 或脚本发现未实测时，只声明 installation-time verified 的显式 fallback，不把推测路径、wrapper 或 runtime 私有语法写入 canonical 主流程。
- **D-12:** OpenClaw 与 Hermes Agent 是强制验收行；不能以环境不方便为由动态跳过，也不能把仅有文档条目当成已安装可用证据。

### Cross-Environment Human UAT
- **D-13:** 至少一个非开发环境必须对 hash 绑定的 PDF/PNG 做人工验收，记录 viewer、OS、Typst、字体清单与 fixture 身份。
- **D-14:** 人工 UAT 检查中文字体 fallback、1/2 页稳定性、模块边界、照片 contain/无照片重排、正式命名和可读性；自动化只能准备证据，不能自动批准人工项。
- **D-15:** 人工验收结果必须绑定确切 PDF/PNG SHA-256；产物变化后旧 UAT 自动失效，不能沿用旧结论。
- **D-16:** 若当前环境无法完成非开发环境 UAT，阶段状态应为 `human_needed`，并持久化待测清单，而不是降低验收标准或伪造 PASS。

### Claude's Discretion
- 固定 gate 的具体数量、稳定 gate ID、聚合 JSON/Markdown schema 和命令内部模块拆分由研究与规划决定，但必须满足字面 registry、原始证据重算和零动态跳过。
- 非开发环境可选真实 OpenClaw/Hermes 安装、独立干净 shell 或其他与开发 checkout 隔离的环境；最终选择必须真实执行 whole-folder 与 CLI fallback 验收并记录环境。
- PNG 生成工具和 PDF 结构解析库可复用现有依赖或选择本地可验证替代，但不得联网安装或把缺少可选工具当成成功。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone Scope And Requirements
- `.planning/ROADMAP.md` — 定义 Phase 49 目标、四项成功标准与两计划边界。
- `.planning/REQUIREMENTS.md` — 定义 VERIFY-01..04 的真实 PDF、固定聚合、六 runtime 与跨环境 UAT 要求。
- `.planning/PROJECT.md` — 定义 v1.19 Markdown-first、离线零 token、1/2 页 A4 与六 runtime 总体边界。
- `.planning/STATE.md` — 记录 Phase 48 已完成、Phase 49 当前状态及仍需处置的发布前债务。

### Prior Phase Contracts And Evidence
- `.planning/phases/48-deterministic-targeted-rendering-clean-batch-delivery/48-CONTEXT.md` — 锁定定向、四态条件、三主题矩阵、正式 triples 与 clean publication 语义。
- `.planning/phases/48-deterministic-targeted-rendering-clean-batch-delivery/48-VERIFICATION.md` — Phase 48 功能目标验证与 6/6 requirement 追溯基线。
- `.planning/phases/48-deterministic-targeted-rendering-clean-batch-delivery/48-REVIEW.md` — 发布前必须处置或复核的质量债务清单。
- `.planning/phases/47-controlled-themes-photo-frozen-layout/47-CONTEXT.md` — 锁定三主题、照片、1/2 页与分页最小单元。
- `.planning/research/PITFALLS.md` — 记录分页、字体 fallback、照片与跨环境漂移风险。

### Graduate Resume Implementation And Runtime Surface
- `skills/graduate-resume/SKILL.md` — canonical runtime-neutral 工作流、安全边界、public CLI 与当前 adapter notes。
- `skills/graduate-resume/scripts/graduate-resume.sh` — 六 runtime 共用的显式 public CLI fallback。
- `skills/graduate-resume/scripts/graduate_resume_cli.py` — 当前 `verify` 命令与 Phase 49 聚合入口的集成点。
- `skills/graduate-resume/scripts/test_phase48_cli.py` — 可复用的字面 Phase 48 acceptance registry、真实 Typst 编译与 CLI 负例。
- `skills/graduate-resume/scripts/test_render_contract.py` — Markdown/Typst/PDF render 与 clean publication 验收基础。
- `skills/graduate-resume/scripts/test_theme_contract.py` — 主题、受控字体与固定布局矩阵验收基础。
- `skills/graduate-resume/references/phase-46-baseline.md` — 固定依赖、字体与基础 fixture 前置版本。
- `docs/compatibility-matrix.md` — 六 runtime 的 whole-folder、显式 fallback、权限与 installation-time 验证边界。

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `run_phase48_acceptance_registry()`：已有字面固定 registry 与观察式结果，可作为 Phase 49 顶层聚合的一个受控子 gate，而不是最终自证。
- `graduate_resume_cli.py verify`：已有 caller-owned workdir 和 JSON 输出边界，可扩展为真实 PDF/PNG 与聚合证据入口。
- `test_render_contract.py` / `test_theme_contract.py`：已有真实 Typst、受控字体、照片和布局 fixture，可组合成固定验收矩阵。
- `docs/compatibility-matrix.md`：已有六 runtime installation-time 规则，可转化为可执行安装 fixture 与文档完整性 gate。

### Established Patterns
- Phase 43/44 与 Phase 48 已采用固定 registry、required/called equality、零动态跳过、原始证据重算和 mutation guard；Phase 49 应沿用同一证据完整性模式。
- 正式 delivery root 只容纳 Markdown/Typst/PDF triples；验证 JSON、Markdown、PNG、日志和运行时证据属于 caller-owned verify workdir。
- Typst 0.15.0 与 skill-local CJK 字体已冻结；Phase 49 只能验证这条链，不能回退到系统字体或 PATH 漂移。

### Integration Points
- `skills/graduate-resume/scripts/graduate-resume.sh verify` 是用户与六 runtime 的统一入口。
- `skills/graduate-resume/SKILL.md`、`docs/compatibility-matrix.md` 和 skill-local references 需要与实际安装 fixture 同步更新。
- Phase 49 的人工 UAT 结果应写入 phase planning/evidence 范围并由 verifier 读取，不应修改 canonical 简历事实源或 delivery current。

</code_context>

<specifics>
## Specific Ideas

- Phase 49 必须把“真实可交付”与“测试函数返回成功”区分开：验收需要重开产物、观察结构并绑定 hash。
- 发布验收不能掩盖 Phase 48 代码审查债务或缺失安全报告；这些项目需要在最终 PASS 前有明确处理证据。
- 非开发环境 UAT 是硬条件，允许阶段停在 `human_needed`，不允许自动批准。

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 49-聚合验证、跨 Runtime 与发布验收*
*Context gathered: 2026-07-18*
