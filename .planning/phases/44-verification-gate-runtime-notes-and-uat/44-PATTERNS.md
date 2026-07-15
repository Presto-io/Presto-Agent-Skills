# Phase 44 Pattern Mapping

**Phase:** 44 - Verification Gate, Runtime Notes, and UAT
**Mapped:** 2026-07-15
**Scope:** 仅映射现有代码与文档 analog；不包含实现、不创建计划、不声明人工 UAT 已通过。

## 1. 拟创建或修改的文件

从 `44-CONTEXT.md` 与 `44-RESEARCH.md` 提取出的工作面如下。

| 文件 | 动作 | 角色 | 上游输入 | 下游输出/消费者 |
|---|---|---|---|---|
| `skills/school-pptx/scripts/school-pptx.sh` | 修改 | 公共 CLI dispatcher | 用户命令、`SCHOOL_PPTX_PYTHON` | `verify_school_pptx.py` |
| `skills/school-pptx/scripts/verify_school_pptx.py` | 创建 | Phase 44 验证编排与证据发布 | dispatcher、canonical fixture、模板/manifest、Phase 43 aggregate | caller workdir 下的 delivery/evidence/work，命令退出码 |
| `skills/school-pptx/scripts/verify_pptx_renderer.py` | 可能小改 | Phase 43 regression authority 与结构检查 helper 来源 | freshly rendered PPTX 或独立 Phase 43 fixture | 21-gate raw evidence 与 registry evidence |
| `skills/school-pptx/scripts/markdown_contract.py` | 修改 | 公共 Markdown 诊断源 | finalized Markdown | `REVIEW_MARKER_UNRESOLVED` 等稳定 code |
| `skills/school-pptx/scripts/template_report.py` | 可能修改 | 模板/manifest 验证与 mismatch 诊断源 | 隔离复制的 template/manifest | 稳定 mismatch code 或 verifier 规范化输入 |
| `skills/school-pptx/SKILL.md` | 创建 | canonical semantic entry | 仓库 authoring 约束、现有 references、公共命令 | 六 runtime 的同一语义源 |
| `skills/school-pptx/references/verification-contract.md` | 创建 | 长验证契约 | Phase 44 fixed registries/evidence schema | 实现者、reviewer、用户 |
| `skills/school-pptx/references/renderer-and-pagination.md` | 条件创建 | 长 renderer/pagination 说明 | Phase 41–43 已冻结行为 | canonical skill 的 progressive disclosure；若现有 references 足够则不创建 |
| `skills/school-pptx/references/visual-uat.md` | 创建 | 可复用真实 viewer UAT 清单 | Phase 43 UI handoff、VER-10 | 人工测试者；不得含本阶段 PASS 声明 |
| `.planning/phases/44-verification-gate-runtime-notes-and-uat/44-UAT.md` | 创建 | 里程碑专属人工证据 | public verify 生成的 fixture/PPTX hashes、真实 viewer 操作 | Phase 44/milestone acceptance；初始必须为 pending |
| `README.md` | 修改 | 人类入口索引 | canonical skill 路径与短描述 | 项目贡献者 |
| `skills/README.md` | 修改 | skills 目录与 artifact contract 索引 | skill entry/references/scripts | skill 使用者与 reviewer |
| `docs/compatibility-matrix.md` | 修改 | 跨 runtime 兼容索引 | canonical adapter notes | 六 runtime 安装期核验 |
| `docs/directory-spec.md` | 条件修改 | 文件归属契约 | school-pptx ownership 需求 | 贡献者；仅在确有专属澄清价值时更新 |

## 2. 总体数据流 analog

```text
school-pptx.sh verify --workdir <dir>
  -> verify_school_pptx.py
     -> dependency readiness
     -> public example
     -> public template-report
     -> public render
     -> freshly rendered PPTX structural inspection
     -> verify_pptx_renderer.run_phase_43() / bounded subprocess
     -> six isolated negative cases
     -> in-memory evidence-integrity
     -> <workdir>/delivery/* + <workdir>/evidence/{verification.json,verification.md}
     -> automated status + manual_uat: pending
  -> human opens exact hashed PPTX in PowerPoint/WPS
  -> planning-only 44-UAT.md
```

最接近的整体 analog 是 `school-presentation` 的 public `verify --workdir`，但 Phase 44 必须加强它：不能把所有产物平铺在 workdir，不能写绝对 artifact 路径，不能只凭最终布尔值，且必须保留固定 gate/negative registry 与人工 UAT pending 边界。

## 3. 公共 dispatcher：`school-pptx.sh`

### 最接近 analog

- `skills/school-presentation/scripts/school-presentation.sh`
  - `usage()` 明列 `school-presentation.sh verify --workdir <dir>`。
  - `main()` 的 `case` 将 `example|render|verify|bookmark-pdf|info` 统一交给 `python_renderer`。
  - `python_renderer()` 通过环境变量选择 Python，并保持 skill-local 模块路径。
- 当前 `skills/school-pptx/scripts/school-pptx.sh`
  - 已有稳定 `usage()`、`die()`、`main()` 和 literal case dispatch。
  - `validate|example`、`render`、`template-report` 分别映射到现有脚本；新增 `verify)` 应保持其余 case 不变。

### 可复用结构

- 在 `Usage:` 与 `Commands:` 同时增加 literal `verify --workdir <dir>`，便于静态 contract gate 检查。
- 延续 `"${SCHOOL_PPTX_PYTHON:-python3}" "$SCRIPT_DIR/<script>.py" "$SKILL_DIR" "$@"` 的解释器选择与参数透传模式。
- 继续使用 `set -euo pipefail`、绝对化 `SCRIPT_DIR`/`SKILL_DIR`、未知命令统一 `die`。

### 不应照搬

- `school-presentation` 的 verifier 直接在 workdir 根部写 sample、两次 HTML 和 manifests；Phase 44 要拆分 `delivery/`、`evidence/`、`work/<run-id>/`。
- dispatcher 不负责安装依赖、创建 runtime shim 或推断人工 UAT 状态。

## 4. Phase 44 verifier：`verify_school_pptx.py`

### 最接近 analog：public verify 生命周期

- `skills/school-presentation/scripts/school_presentation/_engine.py::cmd_verify`
  - `Path(args.workdir)` 建立 caller-owned root。
  - 调用同一实现的 example/render，重复渲染并比较输出。
  - 从观测值构造单一 `verification` 对象，再序列化 JSON。
  - 最终根据 `verification["status"]` 决定失败。
- 可复用要点：公共入口生成 fixture、执行真实渲染、从观测值构建 evidence、最后统一决定退出码。

### 最接近 analog：固定 registry 与 aggregate

- `skills/school-pptx/scripts/verify_pptx_renderer.py::run_phase_43`
  - 先断言 `PHASE_43_GATE_ORDER` 唯一。
  - 断言 `set(PHASE_43_GATE_ORDER) == PHASE_43_REQUIRED_GATES`。
  - 按 tuple 顺序逐 gate 调用 `run_named_gate()`，每 gate 使用隔离目录并追加 `called`。
  - 结束后断言 `tuple(called) == PHASE_43_GATE_ORDER`。
  - `evidence["registry"]` 同时记录 `required`、`called`、`unique`、`dynamic_skips`。
  - `GAP_COVERAGE` 与 `REQUIREMENT_COVERAGE` 均验证只引用实际 called gates。
- Phase 44 应复用同一形状建立固定 8-gate registry 与固定 6-case negative registry；aggregate 必须由各 gate raw status 重算，不能信任 producer 的预制 PASS。

### 最接近 analog：隔离与公共黑盒调用

- `verify_pptx_renderer.py::run_named_gate` 为每个 gate 接收独立 `workdir`。
- `verify_pptx_renderer.py::run_phase_43` 使用 `TemporaryDirectory` 隔离 21 个 gate。
- `verify_markdown_contract.py`、`verify_template_manifest.py` 广泛使用 `TemporaryDirectory` 执行 public CLI、collision、failure 与安全回归。
- Phase 44 的负例目录应固定为 `work/<run-id>/negatives/<case-id>/`，模板 mismatch 只操作复制件；caller sentinel 与 canonical source 在前后做 hash 对比。

### 最接近 analog：结构证据

- `skills/school-pptx/scripts/verify_pptx_renderer.py` 是本仓库最接近的结构检查来源：
  - `PUBLIC_CLI`、`FIXTURE_PATH` 绑定公共入口和 canonical fixture。
  - renderer gates 已重开 PPTX 并检查 native table、code textbox/runs、group shapes、notes、media relationships、whole-slide picture、layout/page mapping 与 transition。
  - `run_phase_43()` 已冻结 21-gate regression 与 13 logical → 32 physical baseline。
- 复用方式应是调用/提取稳定 helper 或 bounded subprocess，而不是复制 21 个 gate body。
- Phase 44 需要额外把结构观察绑定到本次 `delivery/*.pptx` 的 hash；不能仅转抄 Phase 43 自己 temporary fixture 的 JSON。

### 证据发布模式

- 借鉴 `_engine.py::write_text` 的“父目录创建 + UTF-8 写入”和从同一 `verification` dict 生成 JSON 的方式。
- 新 verifier 应先构建并校验内存 evidence，再由同一对象生成 JSON 与 Markdown，避免双轨推理。
- 所有 artifact path 使用 caller workdir 相对路径；`sys.executable` 仅记录 sanitized identity、implementation/version 和选择来源，不泄露 home path。
- 失败运行也应发布当前 `status: failed`，避免旧 PASS 被误认为最新状态；当前 evidence 可原子替换，历史失败放 `evidence/runs/<run-id>/`。

### 关键反模式

- `school-presentation::_engine.py::cmd_verify` 的 `artifacts` 使用 `str(Path)`，可产生绝对路径；Phase 44 不复用此字段表达。
- 不从目录动态发现 gate/negative fixture；固定 registry 丢一项即失败。
- 不用 exit code 代替 raw evidence，不用截图/OOXML reopen 代替真实 viewer UAT。
- 不把 optional Pandoc 缺失转成动态 skip 或失败；required Python imports 缺失则在 dependency gate 明确失败。

## 5. Phase 43 aggregate：`verify_pptx_renderer.py`

### 直接复用点

- `PHASE_43_GATE_ORDER`：有序 authority。
- `PHASE_43_REQUIRED_GATES`：独立 required set。
- `run_named_gate(name, workdir)`：统一 gate 调度。
- `run_phase_43()`：顺序、唯一性、required/called equality、gap/requirement coverage 和 `dynamic_skips=0` 的 aggregate authority。
- `phase_boundary`：当前明确 `public_verify_command: false`、`runtime_adapter_changes: false`、`manual_viewer_uat_claimed: false`；Phase 44 应消费这一边界，不应在 Phase 43 aggregate 内伪造新职责。

### 推荐衔接方式

- 优先调用稳定 `run_phase_43()`，或以 bounded subprocess 调用 `verify_pptx_renderer.py phase-43`；无论哪种方式，都解析并再次断言其 registry，而不只看进程 0。
- 若为公开 evidence 需要 helper extraction，应保持 `run_phase_43()` 的 21 gate、顺序、输出与 CLI contract 不变。
- Phase 44 的 `phase-43-regression` 是顶层 8 gates 之一，不把 21 gates 扁平复制进 Phase 44 registry。

## 6. 公共负例诊断

### `markdown_contract.py`

最接近的稳定 code 模式：

- `media_block()` 用 `collector.add("MEDIA_MISSING", ...)`，同时生成 safe editable placeholder 描述。
- `scan_forbidden()` 用 `collector.add("UNSUPPORTED_STYLE", ...)`。
- metadata validation 用 `THEME_UNKNOWN`。
- slide opener validation 用 `LAYOUT_UNKNOWN`。

新 unresolved-marker 规则应遵循同一 `DiagnosticCollector` 数据流：在共享 validate/render 路径识别文档约定的 `{{待补充: ...}}`、`{{AI草稿: ...}}`，产生固定 `REVIEW_MARKER_UNRESOLVED`，而不是只在 verifier fixture 中字符串匹配。扫描必须保持 fenced code opacity，不能把任意花括号视为 marker。

### `template_report.py`

最接近的模式：

- `validate_manifest(...)` 返回包含 `failures` 的 observed evidence。
- `main()` 对 package exception 与 evidence failures 都非零退出，并可写 Markdown/JSON report。
- `markdown_report(...)` 从 evidence 生成可审阅摘要。

当前不足是多数 mismatch 以人类文本表达。可选做法：

1. 在 report 层增加稳定 `TEMPLATE_MANIFEST_MISMATCH` code，同时保留 bounded failure details；或
2. 仅在 Phase 44 verifier adapter 中把“隔离复制件 report 非零 + expected mismatch evidence”规范化成该 code。

无论采用哪种方式，都不能改变 canonical template-report 成功语义，也不能对 committed template/manifest 做 mutation。

## 7. Canonical `SKILL.md` 与 Runtime Adapter Notes

### 最接近 canonical analog

- `skills/tiaokedan/SKILL.md`
  - frontmatter 的 `description` 是明确 “Use when” 触发句。
  - `metadata.supported-runtimes` 完整列出六 runtime。
  - 主体按 Objective、Use When、Inputs、Workflow、Missing Information Questions、Commands、Runtime Adapter Notes、Outputs、Verification、Safety 分层。
  - review markers 在定稿前可存在，final render 明确阻塞未解决 marker。
  - 长 Markdown/PDF 规则链接到 `references/`，入口不复制完整 schema。
- `skills/school-presentation/SKILL.md`
  - 与演示文稿领域最接近：logical slides、renderer-owned pagination、public `verify --workdir`、演示 UAT reference。
  - `Script Usage` 提供 literal example/render/verify 命令。
  - Runtime Adapter Notes 六行覆盖 discovery 与显式 shell fallback。

### 可复用文档结构

- frontmatter：精确 trigger-oriented `description`、`portability: canonical`、六 runtime 列表。
- 主流程保持 runtime-neutral，只描述 review-before-render、public commands、clean outputs、安全边界。
- Missing Information Questions 只覆盖 Context D-17 的事实：学校/课程标题、subtitle/term/author、受控 theme、媒体路径、review markers、Markdown 是否定稿。
- 长 Markdown、template、renderer/pagination、verification、UAT 与 troubleshooting 只做链接。
- Runtime Adapter Notes 保持一个六行表，不建 adapter 目录或六份 skill copy。

### 六 runtime 表的具体 analog

- `skills/tiaokedan/SKILL.md` 的表最完整地体现 whole-folder install、support files、shell invocation、外部依赖与写权限。
- `docs/compatibility-matrix.md::Installation Checks` 提供每行共同检查维度：frontmatter、support-file preservation、script execution/sandbox/allowlist、manual invocation fallback、未验证行为标为 installation-time check。
- OpenClaw analog：AgentSkills-compatible folder、frontmatter parser、skill root、sandbox sync、third-party review、allowlist、support-file visibility；不得假设自动 script discovery。
- Hermes analog：安装时验证 exact project/global loading path、whole-folder support discovery、外部命令/读写执行权限与显式 invocation fallback。

## 8. Verification 与 UAT references

### Verification reference analog

- `skills/school-presentation/references/verification-contract.md`
  - 开头声明本文件承载长验证期望，保持 `SKILL.md` 简洁。
  - 独立列出 Verify Command、Required Verification Coverage、manifest/evidence fields、entry-level checklist、Manual Review Notes。
- Phase 44 可复用该章节骨架，但内容必须替换为：caller workdir ownership、固定 8-gate registry、固定 6-negative registry、bounded JSON/Markdown schema、status/exit rules、dependency readiness、fresh-run/stale-evidence safety、相对路径与诊断边界。

### UAT reference analog

- `skills/school-presentation/references/verification-contract.md::Manual Review Notes` 证明仓库已有“自动结构验证不等于视觉 UAT”的边界表达。
- `.planning/phases/43-editable-pptx-renderer-and-pagination/43-UI-SPEC.md` 的 visual acceptance handoff 是 Phase 44 checklist 的领域 authority。
- 新 `skills/school-pptx/references/visual-uat.md` 应只放复用流程与检查项，不包含 tester、时间、hash 或 PASS。
- 新 `44-UAT.md` 才记录本里程碑的 viewer/version、OS、fixture/PPTX hash、timestamp、tester 和逐项状态；创建时必须 `status: pending`，自动执行最多校验表单完整度，不能填写 PASS。

## 9. README、skills index 与 compatibility index

### `README.md`

现有 analog：

- repo tree 显式列 skill folder。
- `## 已有技能` 每项用一段短说明并链接入口、artifact contract、template/helper。
- `## 如何添加新技能` 强调六 runtime notes、progressive disclosure 和 clean delivery。

school-pptx 应加入 tree 与已有技能清单，描述 Markdown logical source → editable PPTX、controlled template、public verify 和真实 viewer UAT 边界；避免把 21/8/6 gate 明细塞入根 README。

### `skills/README.md`

现有 analog：

- `Current skills` 一行短描述。
- `Artifact contract discovery` 表将 skill、Markdown intermediate、references 对齐。
- `Directory ownership` 明确 `SKILL.md`/`references`/`scripts`/`templates` 分工。

school-pptx 应新增 current-skill 行与 artifact contract 行，链接 `SKILL.md`、markdown/template/verification/UAT references 与 public helper；若没有 copyable Markdown template，不应伪造 `templates/*.md`，canonical fixture 可由 `example` 生成。

### `docs/compatibility-matrix.md`

现有 analog：

- Recommended Pattern 与 Installation Checks 是跨技能通用规则。
- Matrix 固定六 runtime。
- Runtime Notes 以具体 skill 小节记录 whole-folder assets、依赖、公开 helper 与 clean output 特性。

应新增 `School PPTX` runtime note，强调 whole-folder 安装、Python packages、shell execute/read/write、可选 Pandoc、模板/manifest/fixture/references 可见性，以及 `verify --workdir` 只写 caller root。不要改变六 runtime 通用 matrix，也不要宣称未安装验证的 OpenClaw/Hermes 自动发现路径。

### `docs/directory-spec.md`

现有规则已经覆盖 canonical entry、progressive disclosure、scripts 与 templates 归属。仅当需要解释 school-pptx 的 normalized PPTX template/manifest、fixture 与 planning-only UAT evidence 所有权时，增加小型 ownership row；否则保持不改，避免把单技能 schema 升格为全仓库规范。

## 10. 可复用模式与必须加强之处汇总

| 关注点 | 直接 analog | 可复用 | Phase 44 必须加强 |
|---|---|---|---|
| `verify --workdir` dispatch | `school-presentation.sh` | literal usage、case dispatch、env-selected Python | delivery/evidence/work 隔离，参数安全边界 |
| verifier lifecycle | `_engine.py::cmd_verify` | public example/render、同一 evidence object、status 驱动退出 | 固定 registry、相对路径、bounded output、fresh current evidence |
| aggregate truth | `verify_pptx_renderer.py::run_phase_43` | required/called/order/unique/dynamic_skips | Phase 44 8-gate 与 6-negative 双 registry，raw outcome 重算 |
| structural inspection | `verify_pptx_renderer.py` gates | OOXML reopen、native object/media/notes/group checks | 绑定 fresh delivery PPTX hash，不能只复制 Phase 43 evidence |
| stable diagnostics | `markdown_contract.py` collector | code + message + fix 的共享 validate/render 流 | 新 unresolved marker code，保持 fenced code opacity |
| template mismatch | `template_report.py` | observed failures、MD/JSON report、非零退出 | 固定 mismatch code、只 mutation workdir copies |
| canonical skill | `tiaokedan/SKILL.md`、`school-presentation/SKILL.md` | concise entry、review gate、commands、six runtimes | school-pptx 专属 facts 与 verification/UAT links |
| runtime portability | `docs/compatibility-matrix.md` | whole-folder、fallback、permissions、installation checks | OpenClaw/Hermes 保守措辞，workdir ownership |
| visual UAT | school-presentation manual notes、Phase 43 UI handoff | 自动与人工边界 | planning evidence 初始 pending；无人操作不得 PASS |
| discoverability | root/skills README 与 matrix | tree、short description、artifact links | 同步三处，directory spec 仅按需 |

## 11. 规划时应保持的依赖顺序

1. 先稳定公共 dispatcher、workdir ownership、dependency gate 与 evidence schema。
2. 再接入 fresh canonical public flow、结构检查、Phase 43 aggregate 和六负例。
3. 在命令与 evidence contract 稳定后撰写 canonical skill、references 和索引。
4. 最后生成 pending UAT artifact 并停在真实 PowerPoint/WPS 人工 checkpoint；任何 FAIL/BLOCKED 必须转成明确 gap。

该顺序用于模式映射，不构成 `PLAN.md`。自动 gate 全部通过仍不等于 VER-10 或 milestone acceptance 已完成。
