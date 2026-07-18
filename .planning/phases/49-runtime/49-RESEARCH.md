# Phase 49: 聚合验证、跨 Runtime 与发布验收 - Research

**Researched:** 2026-07-19
**Domain:** 离线 PDF/PNG 产物验收、固定聚合证据、六 Runtime 安装验证、hash 绑定人工 UAT
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

> 以下内容逐字复制自 `49-CONTEXT.md`，是规划必须遵守的锁定边界。 `[VERIFIED: 49-CONTEXT.md]`

### Locked Decisions

#### Aggregate Evidence Authority
- **D-01:** 对外聚合验收必须使用字面固定、顺序固定的 gate registry；`required` 与实际 `called` 必须精确相等，不允许动态发现、动态跳过或按环境减少 gate。
- **D-02:** 顶层结论必须从子测试原始输出、重开的产物和 hash 重新计算，不能直接信任生产者写入的 `passed`、计数或常量证据。
- **D-03:** 聚合命令覆盖正常、无照片、多目标、资格缺口、内容压力和故障注入 fixture，并同时证明 schema、定向、分页、发布与回滚边界。
- **D-04:** Phase 48 的 `48-REVIEW.md` 质量债务与缺失的安全执行报告属于发布前置条件；可以独立修复和复核，但最终发布验收不得在这些债务仍未处置时给出无条件 PASS。

#### PDF And PNG Acceptance
- **D-05:** `verify` 必须重新打开 PDF/PNG 观察产物，不以文件存在、非空或可打开作为充分条件。
- **D-06:** 每份证据至少验证真实 A4、仅 1 或 2 页、主题、照片模式、页数、模块边界、正式命名与目标 metadata 一致；结构声明要从 PDF/PNG 与对应最终 Markdown/Typst 交叉重算。
- **D-07:** 验收证据保存于调用方授权的 verify workdir，不进入正式 delivery root；证据 JSON/Markdown、PNG 和日志不得成为 current sidecar。
- **D-08:** 固定 fixture、Typst 0.15.0、受控 CJK 字体清单、字体 hash、PDF/PNG hash 和运行环境信息必须进入同一验收链，便于复现和人工比对。

#### Six Runtime Installation Verification
- **D-09:** 六个 runtime 共享唯一 canonical `skills/graduate-resume/SKILL.md`；不得为 Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw 或 Hermes Agent 维护六份分叉技能逻辑。
- **D-10:** 每个 runtime 的验收都必须证明完整 skill folder 可读、支持文件相对路径有效、public shell CLI 可显式调用、依赖可检查、授权 workdir/delivery root 可写；自动发现不是通过条件。
- **D-11:** runtime 自动 discovery 或脚本发现未实测时，只声明 installation-time verified 的显式 fallback，不把推测路径、wrapper 或 runtime 私有语法写入 canonical 主流程。
- **D-12:** OpenClaw 与 Hermes Agent 是强制验收行；不能以环境不方便为由动态跳过，也不能把仅有文档条目当成已安装可用证据。

#### Cross-Environment Human UAT
- **D-13:** 至少一个非开发环境必须对 hash 绑定的 PDF/PNG 做人工验收，记录 viewer、OS、Typst、字体清单与 fixture 身份。
- **D-14:** 人工 UAT 检查中文字体 fallback、1/2 页稳定性、模块边界、照片 contain/无照片重排、正式命名和可读性；自动化只能准备证据，不能自动批准人工项。
- **D-15:** 人工验收结果必须绑定确切 PDF/PNG SHA-256；产物变化后旧 UAT 自动失效，不能沿用旧结论。
- **D-16:** 若当前环境无法完成非开发环境 UAT，阶段状态应为 `human_needed`，并持久化待测清单，而不是降低验收标准或伪造 PASS。

### the agent's Discretion
- 固定 gate 的具体数量、稳定 gate ID、聚合 JSON/Markdown schema 和命令内部模块拆分由研究与规划决定，但必须满足字面 registry、原始证据重算和零动态跳过。
- 非开发环境可选真实 OpenClaw/Hermes 安装、独立干净 shell 或其他与开发 checkout 隔离的环境；最终选择必须真实执行 whole-folder 与 CLI fallback 验收并记录环境。
- PNG 生成工具和 PDF 结构解析库可复用现有依赖或选择本地可验证替代，但不得联网安装或把缺少可选工具当成成功。

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

## Summary

Phase 49 不需要引入新渲染器或新第三方包。现有代码已经具备最终 Markdown 的 tamper-evident parser、冻结布局计划、受控 Typst 0.15.0、skill-local CJK 字体、真实 PDF/PNG 重开检查和 Phase 48 固定 registry；本阶段的核心是把这些窄能力组合成一个**不信任生产者结论**的发布权威。 `[VERIFIED: codebase grep]`

推荐把公开入口收束为 `graduate-resume.sh verify --workdir <caller-owned-dir>`：在授权 workdir 内生成固定 fixture 的真实 triples、PNG、raw logs、runtime rows、UAT PENDING/record 和聚合 JSON/Markdown；delivery root 始终只保留正式 Markdown/Typst/PDF triples。聚合器必须逐 gate 观察 exit code、原始 stdout/stderr、重开产物并重新计算 hashes、页面结构和 metadata，最后验证 `required == called`、顺序相同、唯一且零动态跳过。 `[VERIFIED: 49-CONTEXT.md]` `[RECOMMENDATION]`

Phase 48 的 6 个 Blocker、3 个 Warning 和缺失 `48-SECURITY.md` 不能混入 Phase 49 产品范围，但必须成为固定发布前置 gate：先由独立 code-review fix / secure-phase 流程关闭，再由 Phase 49 重读修复后的 review/security 文件并拒绝未处置状态。只有自动门、Phase 48 前置和六 runtime 行均通过、唯一缺项是非开发环境人工 UAT 时，顶层状态才允许为 `human_needed`；其他缺项均为失败。 `[VERIFIED: 48-REVIEW.md]` `[VERIFIED: STATE.md]` `[RECOMMENDATION]`

**Primary recommendation:** 使用两计划结构：49-01 建立发布前置门、独立 PDF/PNG 验证器和固定聚合 authority；49-02 建立六 runtime 安装证据与 hash 绑定人工 UAT，并让同一聚合器给出 `passed | human_needed | failed`。 `[VERIFIED: ROADMAP.md]` `[RECOMMENDATION]`

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| 公共 `verify --workdir` | 本地 CLI / Application | 文件系统 | 入口解析授权路径、编排固定 gates，并输出有界状态；正式 delivery 不承担证据存储。 `[VERIFIED: graduate_resume_cli.py]` |
| PDF/PNG 深度验收 | Verification Domain | 文件系统 | 验证器重开不可变产物并从物理页面、像素和最终源交叉重算，不依赖 renderer 的 `passed`。 `[VERIFIED: graduate_resume_pdf_gate.py]` |
| 固定聚合 registry | Verification Domain | Test Harness | registry 是发布权威，必须固定顺序、观察 raw outcome、验证 required/called equality。 `[VERIFIED: test_phase48_cli.py]` |
| 六 runtime 安装验收 | Runtime Adapter / Installation | 本地 CLI | 每个 runtime 仅负责启动同一 whole-folder 与显式 shell fallback；canonical 流程不分叉。 `[VERIFIED: docs/compatibility-matrix.md]` |
| 人工 UAT | Human Review | Verification Domain | 自动化只准备和 lint 记录；人类在非开发环境观察 PDF/PNG 并签署 hash 绑定结果。 `[VERIFIED: school-pptx visual UAT pattern]` |
| 发布前债务门 | Release Governance | Security / Code Review | Phase 48 review/security 是发布前置证据，不属于简历功能实现。 `[VERIFIED: 49-CONTEXT.md]` |

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| VERIFY-01 | CLI 验证生成 PDF 为真实 1 或 2 页 A4，并验证主题、照片模式、页数、模块边界和命名契约；单纯 PDF 非空或可打开不能视为通过。 | 扩展现有 `graduate_resume_pdf_gate.py`，从最终 Markdown 重建冻结计划并独立重开 Markdown/Typst/PDF/PNG，核对 A4、页数、逐页事实、主题、照片、stem 和 target metadata。 `[VERIFIED: codebase grep]` |
| VERIFY-02 | 技能提供正常、无照片、多个目标、资格缺口、内容压力和故障注入 fixtures，以及聚合回归命令来证明 schema、定向、分页和发布边界。 | 使用下文固定 14-gate registry；六类 fixture 均为字面 gate，Phase 48 registry 只作为一个被重新观察的子 gate。 `[VERIFIED: 49-CONTEXT.md]` `[RECOMMENDATION]` |
| VERIFY-03 | `SKILL.md`、CLI fallback 与安装期验证覆盖 Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw 和 Hermes Agent，且不把运行时私有语法写入 canonical 主流程。 | 建立单一 runtime-install fixture runner，在六个真实环境分别执行 whole-folder manifest、相对路径、显式 CLI、依赖、授权写入和 fail-closed 检查。 `[VERIFIED: docs/compatibility-matrix.md]` `[RECOMMENDATION]` |
| VERIFY-04 | 通过受控 CJK 字体、固定前置版本与至少跨一个非开发环境的 PDF/PNG 人工验收，证明中文简历不会因字体 fallback 产生页数或分页漂移。 | 复用 Phase 44 的只读 UAT lint 范式：自动生成全 PENDING 模板，人类填写，lint 复算 artifact/font/environment hashes；缺人工结果时输出 `human_needed`。 `[VERIFIED: skills/school-pptx/scripts/verify_school_pptx.py]` |
</phase_requirements>

## Project Constraints (from AGENTS.md)

- 所有用户沟通与规划说明使用简体中文。 `[VERIFIED: AGENTS.md]`
- 保持一个 canonical `SKILL.md`；runtime 私有语法只能出现在 adapter notes，不能进入 canonical 主流程。 `[VERIFIED: AGENTS.md]`
- 复杂验收契约放 `references/`，脚本放 `scripts/`，输出模板放 `templates/`；文档和模板应简洁、可复制、可审阅。 `[VERIFIED: AGENTS.md]`
- 外部命令、凭据、网络或文件写入必须写明安全边界和验证步骤；OpenClaw 与 Hermes Agent 必须纳入。 `[VERIFIED: AGENTS.md]`
- 新增或改变 runtime 支持声明时同步 `docs/compatibility-matrix.md`；若目录约定变化才同步 `README.md` 和 `docs/directory-spec.md`。 `[VERIFIED: AGENTS.md]`
- 执行阶段前以 `.planning/ROADMAP.md` 和 `.planning/STATE.md` 为当前边界。 `[VERIFIED: AGENTS.md]`

## Standard Stack

### Core

| Library / Tool | Verified Version | Purpose | Why Standard |
|----------------|------------------|---------|--------------|
| Python | 3.14.6（当前机） | CLI、固定 registry、hash、文件系统与 UAT lint | 项目现有全部 graduate-resume 验证代码均为 Python；不引入新语言。 `[VERIFIED: local command]` |
| Typst | 0.15.0 | 固定版本 PDF/PNG 编译 | 运行时 resolver 已精确锁定 `0.15.0`，编译使用 skill-local fonts 与 `--ignore-system-fonts`。 `[VERIFIED: graduate_resume_typst_runtime.py]` |
| PyMuPDF (`fitz`) | 1.27.2.2（当前机） | 重开 PDF、读取页面矩形、文本、字体和 raster | 已是 `graduate_resume_pdf_gate.py` 与测试使用的解析库；官方 Page API 提供 `rect`、`get_text`、`get_fonts`、`get_pixmap`。 `[VERIFIED: local import]` `[CITED: https://pymupdf.readthedocs.io/en/latest/page.html]` |
| Pillow | 12.2.0（当前机） | 重开 PNG、像素边界和照片区域检查 | 现有 PDF gate 已使用 `Image.open()` 做像素级安全区观察。 `[VERIFIED: local import]` `[VERIFIED: graduate_resume_pdf_gate.py]` |
| PyYAML | 6.0.3（当前机） | 最终 Markdown metadata 与 UAT frontmatter 解析 | 最终 Markdown parser 和 Phase 44 UAT lint 已采用 safe YAML 解析。 `[VERIFIED: local import]` `[VERIFIED: codebase grep]` |
| SHA-256 (`hashlib`) | Python stdlib | artifact、font、raw log、registry evidence 与 UAT 绑定 | 项目现有 canonical、Typst runtime、delivery、final Markdown 均以 SHA-256 绑定。 `[VERIFIED: codebase grep]` |

### Supporting

| Tool | Verified Version | Purpose | When to Use |
|------|------------------|---------|-------------|
| `pdfinfo` | 26.05.0（当前机） | 独立 smoke cross-check A4/page count | 可作为辅助二次观察；最终权威仍由 PyMuPDF 重开与几何复算承担，不能仅 grep `pdfinfo` 文本。 `[VERIFIED: local command]` `[RECOMMENDATION]` |
| `pdftoppm` | 26.05.0（当前机） | 必要时独立 raster cross-check | 仅作可选诊断；缺少它不得动态删 gate，应使用已锁定 Typst PNG 输出或明确失败。 `[VERIFIED: local command]` `[RECOMMENDATION]` |
| skill-local Noto Sans Mono CJK SC | manifest 中 2 个 OTF，hash 已冻结 | 中文字体与跨环境稳定性 | 每次 acceptance 重新计算字体 bytes/hash 并记录 family、weight、bytes。 `[VERIFIED: fonts/manifest.json]` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| 复用 PyMuPDF + Pillow | 新增 qpdf/pdfcpu/ImageMagick | 新工具增加安装和跨 runtime 依赖，却不能替代逐页事实与 UAT；本阶段不安装。 `[VERIFIED: existing code]` `[RECOMMENDATION]` |
| 复用 Typst 直接输出 PNG | `pdftoppm` 从 PDF raster | `pdftoppm` 可作独立比对，但不是所有 runtime 已证明具备；主链应使用已冻结 Typst，辅助链可记录 Poppler 结果。 `[VERIFIED: local environment]` `[RECOMMENDATION]` |
| 复用 unittest 固定 ID | pytest 动态收集 | 动态收集与锁定的字面 registry 冲突；Phase 48 已证明 `loadTestsFromName()` 可逐项观察。 `[VERIFIED: test_phase48_cli.py]` |

**Installation:** 本阶段不新增或安装外部包；计划不得联网安装依赖。 `[VERIFIED: 49-CONTEXT.md]` `[RECOMMENDATION]`

## Package Legitimacy Audit

本阶段不安装外部包，因此 Package Legitimacy Gate 不触发。所有建议库已存在于当前实现/环境；若执行时缺失，状态必须失败或阻塞，不能临时联网安装。 `[VERIFIED: codebase and local environment]`

## Architecture Patterns

### System Architecture Diagram

```text
caller-owned verify workdir
        |
        v
public verify CLI --workdir
        |
        +--> release prerequisite gate ----> fixed Phase 48 review/security evidence
        |
        +--> literal 14-gate registry ------> raw stdout/stderr + exit codes
        |             |
        |             +--> fixture render/publish/fault runs
        |             +--> reopen Markdown/Typst/PDF/PNG
        |             +--> recompute hashes/geometry/text/fonts/stems/metadata
        |
        +--> six runtime records ----------> whole-folder + explicit CLI fallback evidence
        |
        +--> UAT record lint --------------> exact PDF/PNG/font/environment hashes
        |
        v
independent top-level recomputation
        |
        +--> passed       (all automated + six runtimes + human UAT)
        +--> human_needed (only human UAT remains)
        +--> failed       (any other missing/failed/stale/tampered evidence)
```

该流向把生产、观察和最终裁决分开；顶层裁决不读取子测试自报计数作为事实。 `[VERIFIED: 49-CONTEXT.md]` `[RECOMMENDATION]`

### Recommended Project Structure

```text
skills/graduate-resume/
├── SKILL.md
├── references/
│   ├── phase-49-verification-contract.md   # public schema、固定 gate、状态语义
│   └── cross-environment-uat.md            # 人工 checklist，不含真实签名
├── fixtures/
│   └── verification/                       # 字面 normal/no-photo/multi/gap/pressure/fault 输入
├── scripts/
│   ├── graduate_resume_cli.py              # --workdir public orchestration
│   ├── graduate_resume_verify.py           # 独立 artifact/runtime/UAT 验证域
│   ├── graduate_resume_pdf_gate.py         # 扩展物理 PDF/PNG 观察
│   ├── test_phase49_verify.py              # 固定 registry 与 mutation guards
│   └── runtime_install_fixture.py           # 六 runtime 共用 runner
└── templates/
    └── phase-49-uat.md                      # 自动仅生成 PENDING
```

新增文件名可调整，但应把独立验证域从大型 CLI 中拆出，避免继续放大 `graduate_resume_cli.py`。 `[VERIFIED: AGENTS.md]` `[RECOMMENDATION]`

### Pattern 1: Producer / Observer / Arbiter 三分离

**What:** producer 生成 fixture 产物；observer 从 raw files 重开并计算观察值；arbiter 只根据字面 registry 和观察值裁决。 `[VERIFIED: 49-CONTEXT.md]`

**When to use:** 所有 gate，尤其是 Phase 48 子 registry、PDF metadata、runtime record 与 UAT。 `[RECOMMENDATION]`

**Implementation rule:** gate result 至少保存 `id`、实际 command/fixture、exit code、stdout/stderr SHA-256、artifact path/hash、observer fields 和 failure code；arbiter 重算 `required/called/unique/dynamic_skips`，不得复制子结果的 `status`。 `[VERIFIED: school-pptx verification-contract.md]` `[RECOMMENDATION]`

### Pattern 2: Caller-Owned Evidence Tree

**What:** `verify --workdir` 必须显式给出，所有写入限定于该 held root 下。建议布局为 `runs/<run-id>/{raw,artifacts,runtime,uat}/`，最终 `acceptance.json` 与 `acceptance.md` 也位于同一 run。 `[VERIFIED: 49-CONTEXT.md]` `[RECOMMENDATION]`

**When to use:** fixture compilation、PNG、logs、runtime records、UAT pending/record；正式 delivery root 不接受任何 sidecar。 `[VERIFIED: graduate-resume SKILL.md]`

**Security boundary:** workdir 必须拒绝 repository source、delivery current、symlink、FIFO、unknown ownership 和越界 path；失败清理只能清理本 run owned path。 `[VERIFIED: graduate_resume_delivery.py patterns]` `[RECOMMENDATION]`

### Pattern 3: Independent Artifact Reconstruction

**What:** 从最终 `.md` 的 verified facts 与 metadata 重建主题、照片模式、页数和冻结计划；解析 `.typ` 的固定 theme/photo/pagebreak markers；用 PyMuPDF 重开 `.pdf`；用 Pillow 重开每页 `.png`；最后交叉比对而不是相信任一 sidecar。 `[VERIFIED: codebase grep]` `[RECOMMENDATION]`

**Required physical checks:**

- PDF page count 只能是 1 或 2，且每页矩形必须在小容差内等于 210 mm × 297 mm。 `[CITED: https://pymupdf.readthedocs.io/en/latest/page.html]` `[RECOMMENDATION]`
- 每个冻结 container 的文本只能出现在指定页；首页以 profile 锚点开始，第二页以合法模块标题开始。 `[VERIFIED: graduate_resume_pdf_gate.py]`
- PDF fonts 必须与受控 font manifest 相容，并记录观察到的字体集合；不允许把未识别字体当 warning 后继续 PASS。 `[CITED: https://pymupdf.readthedocs.io/en/latest/page.html]` `[RECOMMENDATION]`
- PNG 数量等于 PDF 页数，尺寸/背景/安全区重新观察；照片版核对照片槽位存在且 contain，无码版核对照片区域和装饰消失并发生重排。 `[VERIFIED: graduate_resume_pdf_gate.py]` `[RECOMMENDATION]`
- triple stem、theme label、generic/target company-role、page/photo metadata 必须从最终 Markdown 与 canonical naming function 的独立规则重算。 `[VERIFIED: graduate_resume_final_markdown.py]` `[RECOMMENDATION]`

### Pattern 4: Hash-Bound Read-Only UAT Lint

**What:** 自动化只生成 `status: pending` 且所有 checklist 行为 `PENDING` 的模板；人工填写 viewer/OS/Typst/font manifest/fixture/PDF/PNG hashes、tester、timestamp、逐项 observation 和 signoff；lint 函数不得包含写入、自动用户名、自动时间或结构测试代填。 `[VERIFIED: school-pptx/scripts/verify_school_pptx.py]` `[RECOMMENDATION]`

**Status rule:** UAT hash 与 current acceptance artifacts 任一不一致即 stale/blocked；artifact 变化后必须重新人工验收。 `[VERIFIED: 49-CONTEXT.md]`

### Recommended Fixed Gate Registry

| Order | Stable ID | Scope |
|------:|-----------|-------|
| 1 | `P49-G01-release-prerequisites` | Phase 48 review debt closed + `48-SECURITY.md` present and passing |
| 2 | `P49-G02-schema-baseline` | existing valid/invalid schema fixtures |
| 3 | `P49-G03-normal-photo` | normal photo render, triple, PDF/PNG deep check |
| 4 | `P49-G04-no-photo` | no-photo reflow and absence checks |
| 5 | `P49-G05-multi-target` | generic + all confirmed targets + three themes |
| 6 | `P49-G06-qualification-gap` | gap/unknown/not-applicable and bounded publication behavior |
| 7 | `P49-G07-content-pressure` | deterministic 2-page A4 and atomic module boundaries |
| 8 | `P49-G08-publication-faults` | candidate/no-op/history/unknown/symlink/fault/rollback authority |
| 9 | `P49-G09-pdf-png-physical` | independent A4/pages/text/fonts/pixels observation |
| 10 | `P49-G10-triple-metadata-name` | Markdown/Typst/PDF/hash/stem/target cross-binding |
| 11 | `P49-G11-six-runtime-install` | exactly six literal rows, including OpenClaw/Hermes |
| 12 | `P49-G12-canonical-docs` | one SKILL, explicit fallback, compatibility docs, no private syntax in main flow |
| 13 | `P49-G13-human-uat` | exact-hash record lint or explicit `human_needed` |
| 14 | `P49-G14-evidence-mutation-guards` | tampered count/status/hash/artifact/runtime/UAT must fail |

14 gates 是推荐的固定 authority；planner 可以改数量，但一旦计划锁定就必须在代码、reference 和测试中逐字一致。 `[RECOMMENDATION]`

### Anti-Patterns to Avoid

- **把 Phase 48 registry 当顶层 authority：** 它明确只证明 local development scope，Phase 49 只能把它作为一个被重新观察的子 gate。 `[VERIFIED: test_phase48_cli.py]`
- **信任 evidence JSON 的 `passed`：** 必须从 raw output、exit code、artifact reopen 和 hashes 重算。 `[VERIFIED: 49-CONTEXT.md]`
- **动态发现 fixture/runtime：** 缺 Gemini/OpenClaw/Hermes 不能 skip 或减少 denominator。 `[VERIFIED: 49-CONTEXT.md]`
- **自动填写人工字段：** 自动 tester/time/observation/PASS 会破坏 UAT 权威。 `[VERIFIED: school-pptx visual UAT pattern]`
- **把 PNG/log/JSON 发布为 current sidecar：** 这些只能留在 caller-owned verify workdir。 `[VERIFIED: graduate-resume SKILL.md]`
- **仅看 PDF 非空、magic bytes 或 `pdfinfo` 文本：** 不能证明主题、照片、模块归属、命名或 target metadata。 `[VERIFIED: REQUIREMENTS.md]`
- **Phase 49 顺手扩展主题/事实/在线功能：** 本阶段只做验收与发布门。 `[VERIFIED: 49-CONTEXT.md]`

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PDF parser | 正则扫描 PDF bytes | PyMuPDF Page API | PDF 对象、字体、页面和文本结构不能可靠靠字节正则解析。 `[CITED: https://pymupdf.readthedocs.io/en/latest/page.html]` |
| PNG decoder | 自写 PNG chunk/pixel decoder | Pillow | 现有代码已使用 Pillow 可靠重开和像素遍历。 `[VERIFIED: graduate_resume_pdf_gate.py]` |
| PDF/PNG producer | 新 renderer 或浏览器截图链 | 锁定 Typst 0.15.0 | 本阶段只验收已冻结 renderer，Typst 官方支持 PDF export，现有实现也能编译 PNG。 `[CITED: https://typst.app/docs/reference/pdf/]` `[VERIFIED: test_layout_fixtures.py]` |
| UAT approval bot | 根据自动截图自动 PASS | 人工 record + read-only lint | 锁定决策禁止自动批准人工项。 `[VERIFIED: 49-CONTEXT.md]` |
| 六份 runtime skill | runtime-specific SKILL/shim copies | one canonical folder + explicit shell fallback | 仓库策略和 D-09 均禁止分叉逻辑。 `[VERIFIED: AGENTS.md]` |
| 新 aggregate framework | 动态 plugin/test discovery | literal tuple + direct named invocation | 现有 Phase 48/44 模式已满足固定顺序和 observed evidence。 `[VERIFIED: test_phase48_cli.py]` |

**Key insight:** 本阶段难点不是“能不能打开文件”，而是建立一条生产者无法用自报状态欺骗、环境缺失无法用 skip 隐藏、人工未签字无法被自动替代的证据链。 `[VERIFIED: 49-CONTEXT.md]`

## Common Pitfalls

### Pitfall 1: 发布前置债务被 verifier 的历史 PASS 掩盖
**What goes wrong:** `48-VERIFICATION.md` 通过，但后续标准审查仍有 6 Blocker/3 Warning，且没有 `48-SECURITY.md`；若只读 verification 会错误放行。 `[VERIFIED: 48-VERIFICATION.md]` `[VERIFIED: 48-REVIEW.md]`
**How to avoid:** `P49-G01` 必须读取最新 review/security artifacts，要求 blocker 为 0、所有旧 finding 有处置/复核证据、安全报告为 pass；缺文件或 stale hash 均失败。 `[RECOMMENDATION]`

### Pitfall 2: 复用生产 parser 导致共同错误
**What goes wrong:** renderer 和 verifier 共享同一个错误字段或自报 metadata，双方一致但产物仍错。 `[ASSUMED]`
**How to avoid:** 可以复用安全的最终 Markdown parser，但物理 A4、页数、字体、逐页文本、PNG 像素、path stem 和 hashes 必须由 observer 独立读取原始文件；mutation guard 修改副本中的 producer status/count/hash 后仍应失败。 `[RECOMMENDATION]`

### Pitfall 3: UAT 状态语义过宽
**What goes wrong:** runtime 缺失、自动 gate 失败也被归为 `human_needed`，从而模糊真实失败。 `[ASSUMED]`
**How to avoid:** `human_needed` 仅允许在 G01-G12、G14 全通过且 G13 唯一处于合法 PENDING 时出现；任何 runtime row 缺失、hash stale、FAIL/BLOCKED 都是 `failed`。 `[RECOMMENDATION]`

### Pitfall 4: runtime 名称只是调用方自报
**What goes wrong:** 在一个 shell 连跑六次并改 `--runtime` 标签，会制造六行伪证据。 `[ASSUMED]`
**How to avoid:** 每行记录真实 executable/version、installation root manifest、operator/environment ID、raw command log 和 artifact hashes；实际由目标 runtime 发起同一 fallback，最后聚合只接受六个字面 runtime ID 各一次。无法证明实际运行就保持失败，不用文档行代替。 `[RECOMMENDATION]`

### Pitfall 5: workdir 污染 delivery 或 repository
**What goes wrong:** 固定探针写进模板目录、验证 PNG/日志成为 current sidecar，或 cleanup 删除调用方文件。 `[VERIFIED: 48-REVIEW.md WR-03]`
**How to avoid:** 所有 probe 使用 held caller workdir 的唯一 run 子目录；拒绝 source/delivery overlap、symlink/FIFO/unknown；cleanup 只删 owned run。 `[RECOMMENDATION]`

### Pitfall 6: PDF 字体“看起来正常”但环境发生 fallback
**What goes wrong:** 页数仍为 1/2，但 glyph metrics 或字体集合已变化，后续 viewer/环境出现漂移。 `[VERIFIED: research/PITFALLS.md]`
**How to avoid:** 记录 font manifest bytes/hash、Typst snapshot hash、PDF observed font names、PDF/PNG hashes；非开发环境逐页人工比较中文、分页和可读性。 `[RECOMMENDATION]`

## Code Examples

### 固定 Registry 与独立裁决骨架

```python
# Source: existing test_phase48_cli.py pattern, adapted for Phase 49
PHASE49_GATE_ORDER = (
    "P49-G01-release-prerequisites",
    "P49-G02-schema-baseline",
    # ... literal IDs only ...
    "P49-G14-evidence-mutation-guards",
)

called = []
raw_outcomes = []
for gate_id in PHASE49_GATE_ORDER:
    called.append(gate_id)
    raw_outcomes.append(run_and_observe(gate_id, workdir))

valid_registry = (
    tuple(called) == PHASE49_GATE_ORDER
    and len(called) == len(set(called))
)
status = recompute_status(raw_outcomes, valid_registry)
```

该模式来自现有 Phase 48 的字面 registry，但 Phase 49 的 `recompute_status()` 必须重开 raw artifacts，不复制子测试 `status`。 `[VERIFIED: test_phase48_cli.py]` `[RECOMMENDATION]`

### UAT 只读状态裁决

```python
# Source: existing school-pptx UAT lint pattern
if hashes_do_not_match_current_evidence(record, artifacts):
    return "failed"
if record.status == "pending" and all_rows_pending(record):
    return "human_needed"
if record.status == "passed" and all_rows_pass(record) and record.signoff:
    return "passed"
return "failed"
```

lint 函数不得生成 tester、timestamp、observation 或 PASS。 `[VERIFIED: skills/school-pptx/scripts/verify_school_pptx.py]`

### 物理 A4 与页数观察

```python
# Source: PyMuPDF official Page API + existing graduate_resume_pdf_gate.py
with fitz.open(pdf_path) as document:
    if len(document) not in (1, 2):
        fail("PDF_PAGE_COUNT_INVALID")
    for page in document:
        width_mm = page.rect.width * 25.4 / 72
        height_mm = page.rect.height * 25.4 / 72
        if not close_to_a4(width_mm, height_mm):
            fail("PDF_PAGE_SIZE_INVALID")
```

`close_to_a4` 应使用计划锁定的小容差并在 evidence 中保存实际 pt/mm，不要只保存布尔值。 `[CITED: https://pymupdf.readthedocs.io/en/latest/page.html]` `[RECOMMENDATION]`

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| 文件存在/非空即成功 | 重开 Markdown/Typst/PDF/PNG 并交叉重算 | Phase 49 锁定 | VERIFY-01 才能证明真实 A4、页数、模块和 metadata。 `[VERIFIED: REQUIREMENTS.md]` |
| Phase 48 local registry 自证 | Phase 49 顶层重新观察子 registry 与 raw artifacts | Phase 49 锁定 | 防止把 local narrow tests 冒充发布 authority。 `[VERIFIED: 49-CONTEXT.md]` |
| runtime 文档条目即“支持” | 六个真实 whole-folder + explicit CLI install records | Phase 49 锁定 | OpenClaw/Hermes 不可只靠文档或动态 skip。 `[VERIFIED: 49-CONTEXT.md]` |
| 自动结构 PASS 替代视觉签字 | hash-bound human UAT + read-only lint | Phase 44 已建立、Phase 49 复用 | 自动化准备证据，人类对确切 artifact 签署。 `[VERIFIED: school-pptx visual UAT pattern]` |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | producer 与 verifier 共享 parser 可能形成共同错误 | Common Pitfalls 2 | 若风险低估，会减少独立 reopen/mutation tests；仍建议保持独立物理观察。 |
| A2 | 宽泛使用 `human_needed` 会掩盖自动失败 | Common Pitfalls 3 | 状态语义若另有仓库标准，planner 需对齐；锁定 D-16 仍要求不能伪造 PASS。 |
| A3 | runtime 标签可能被单 shell 自报伪造 | Common Pitfalls 4 | 若已有更强 runtime attestation，可替换记录方式；不得降低 six-runtime 实测要求。 |

## Open Questions (RESOLVED)

以下三项已收束为计划必须实现的阻塞式检查点；它们是可执行门禁，不表示对应环境、报告或人工签署已经存在。 `[VERIFIED: plan-checker research resolution]`

1. **Phase 48 REVIEW/SECURITY 债务如何关闭？**
   - **Locked resolution:** 49-01 必须在任何聚合实现前设置阻塞式前置检查点。操作者先执行 `/gsd:code-review 48 --fix`，其后 `48-REVIEW.md` 必须为 clean 或明确 skipped；再执行 `/gsd:secure-phase 48`，生成与当前 Phase 48 source hashes 一致、结论为 PASS 的 hash-fresh `48-SECURITY.md`。任一报告缺失、stale、仍有未处置 finding 或非 PASS 时，49-01 不得继续。 `[VERIFIED: plan-checker research resolution]`
   - **Planner action:** 将该检查点放在 49-01 第一个实现任务之前；`P49-G01-release-prerequisites` 继续在最终 aggregate 中复验同一证据，不能因检查点曾人工确认就跳过机器复算。 `[RECOMMENDATION]`

2. **六 runtime 的实际执行环境如何提供？**
   - **Locked resolution:** 49-02 必须在生成任何真实 runtime record 前设置阻塞式环境确认检查点。操作者逐 runtime 提供真实入口、whole-folder 安装根、public CLI 显式调用方式和 caller-owned evidence 回传路径；Codex、Claude Code、OpenCode 也必须实际执行，不能用本机命令存在性代替验收。Gemini CLI、OpenClaw、Hermes Agent 缺少真实环境时不得模拟、代填、动态跳过或减少 denominator，计划保持在该 checkpoint。 `[VERIFIED: plan-checker research resolution]`
   - **Planner action:** 检查点确认六行执行入口后，才运行 `runtime_install_fixture.py` 并生成 exact-six raw records；每行仍由 `P49-G11-six-runtime-install` 重算 whole-folder、explicit CLI、依赖和授权写入证据。 `[RECOMMENDATION]`

3. **非开发环境 UAT 如何完成？**
   - **Locked resolution:** 49-02 使用 hash-bound `human-verify` checkpoint。操作者提供真实非开发环境、viewer、OS、Typst、字体清单以及逐项签署结果；只有与当前 acceptance run 的确切 PDF/PNG/font/fixture hashes 一致且 UAT 结论为 passed 时，Phase 49 才能完成。 `[VERIFIED: plan-checker research resolution]`
   - **Status rule:** 无法立即完成人工验收时，`human_needed` 是合法暂停而不是完成；人工结果为 failed 时返回实现/产物修复，生成新 artifact hashes 后重新执行 UAT，不得沿用旧签署。 `[VERIFIED: plan-checker research resolution]`

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python | public CLI / tests | ✓ | 3.14.6 | 无；缺失阻塞 `[VERIFIED: local command]` |
| Typst | PDF/PNG render | ✓ | 0.15.0 | 无；版本不符失败 `[VERIFIED: local command]` |
| PyMuPDF | PDF observer | ✓ | 1.27.2.2 | 不新增依赖；缺失阻塞 `[VERIFIED: local import]` |
| Pillow | PNG observer | ✓ | 12.2.0 | 不新增依赖；缺失阻塞 `[VERIFIED: local import]` |
| PyYAML | metadata/UAT parser | ✓ | 6.0.3 | 无；缺失阻塞 `[VERIFIED: local import]` |
| `pdfinfo` | optional cross-check | ✓ | 26.05.0 | PyMuPDF authoritative observer `[VERIFIED: local command]` |
| `pdftoppm` | optional raster cross-check | ✓ | 26.05.0 | Typst direct PNG `[VERIFIED: local command]` |
| Codex | runtime row | ✓ | 0.144.1 | explicit public CLI fallback `[VERIFIED: local command]` |
| Claude Code | runtime row | ✓ | 2.1.114 | explicit public CLI fallback `[VERIFIED: local command]` |
| Gemini CLI | runtime row | ✗ | — | 必须提供真实外部安装环境；不可 skip `[VERIFIED: local command]` |
| OpenCode | runtime row | ✓ | 1.1.35 | explicit public CLI fallback `[VERIFIED: local command]` |
| OpenClaw | runtime row | ✗ | — | 必须提供真实外部安装环境；不可 skip `[VERIFIED: local command]` |
| Hermes Agent | runtime row | ✗ | — | 必须提供真实外部安装环境；不可 skip `[VERIFIED: local command]` |

**Missing dependencies with no fallback:** 当前机缺 Gemini CLI、OpenClaw、Hermes Agent；它们阻止 six-runtime PASS，但不阻止先实现本地自动化。 `[VERIFIED: local command]`

**Missing dependencies with fallback:** `pdfinfo` / `pdftoppm` 即使在其他环境缺失，主链仍可用 PyMuPDF + Typst direct PNG；但固定 registry 不应动态删 gate，应让该 gate 按锁定策略使用主链或失败。 `[RECOMMENDATION]`

## Security Domain

`security_enforcement` 未显式关闭，因此 Phase 49 必须包含安全域，并把缺失的 `48-SECURITY.md` 作为发布前置而非可选文档。 `[VERIFIED: .planning/config.json]` `[VERIFIED: STATE.md]`

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | 本地离线 CLI 无认证主体；不新增身份系统。 `[VERIFIED: PROJECT.md]` |
| V3 Session Management | no | 无 session/cookie/token。 `[VERIFIED: codebase grep]` |
| V4 Access Control | yes（本地文件授权边界） | caller-owned workdir、held directory、no-follow、拒绝越界/unknown/symlink。 `[VERIFIED: graduate_resume_delivery.py]` |
| V5 Input Validation | yes | 受限 YAML/Markdown、stable IDs、enum、bounded paths、严格 UAT schema。 `[VERIFIED: graduate_resume_cli.py]` |
| V6 Cryptography | yes（完整性） | Python `hashlib.sha256`；不自制密码算法、不把 hash 当认证。 `[VERIFIED: codebase grep]` |
| V8 Data Protection | yes | 禁止电话/邮箱/身份证/招聘 URL 进入 stem/evidence public surface；review debt必须关闭。 `[VERIFIED: 48-REVIEW.md]` |
| V12 Files and Resources | yes | 限制 bytes/path/type，重开 PDF/PNG，workdir 与 delivery 分离，拒绝 symlink/FIFO。 `[VERIFIED: codebase grep]` |

ASVS 用作安全检查分类，不改变本地 CLI 的产品边界。 `[CITED: https://owasp.org/www-project-application-security-verification-standard/]`

### Known Threat Patterns for Local Verification Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| producer 伪造 `passed`/counts | Tampering | raw output capture、artifact reopen、independent recompute、mutation guards。 `[VERIFIED: 49-CONTEXT.md]` |
| symlink/path traversal 污染 source/current | Tampering / Elevation | held workdir、O_NOFOLLOW、relative bounded paths、overlap rejection。 `[VERIFIED: graduate_resume_delivery.py]` |
| PII 进入 stem/log/evidence | Information Disclosure | Phase 48 CR-01/CR-02 修复 + bounded public payload + evidence root separation。 `[VERIFIED: 48-REVIEW.md]` |
| Typst snapshot 原地替换 | Tampering / Elevation | Phase 48 CR-06 修复并加入负例；`P49-G01` 在未关闭前拒绝 PASS。 `[VERIFIED: 48-REVIEW.md]` |
| stale UAT 沿用 | Spoofing / Tampering | exact PDF/PNG/font/fixture hashes，任一变化即失效。 `[VERIFIED: 49-CONTEXT.md]` |
| runtime 文档冒充真实安装 | Spoofing | exactly-six raw installation records，OpenClaw/Hermes 强制且不可 skip。 `[VERIFIED: 49-CONTEXT.md]` |

## Plan Split Recommendation

### 49-01: 发布前置、PDF/PNG 验证与固定聚合

1. **发布前置证据 gate：** 定义 `P49-G01`，只消费独立修复后的 Phase 48 review/security artifacts；不要在本任务扩展简历能力。 `[RECOMMENDATION]`
2. **独立 verification domain：** 新建 `graduate_resume_verify.py`，扩展 PDF gate，重建 final plan、重开 quadruple、复算 A4/pages/fonts/text/pixels/stem/metadata/hash。 `[RECOMMENDATION]`
3. **caller-owned public entry：** `verify --workdir` 写入 owned run tree，更新 SKILL/reference；证据不进入 delivery。 `[VERIFIED: 49-CONTEXT.md]`
4. **固定 14-gate authority：** 覆盖六类 fixture、Phase 48 子 registry、publication faults、raw recompute 和 mutation guards。 `[RECOMMENDATION]`
5. **状态与证据 schema：** JSON/Markdown 从同一 observed model 生成，固定 `passed | human_needed | failed`，public 输出有界。 `[RECOMMENDATION]`

### 49-02: 六 Runtime、跨环境 UAT 与发布签署

1. **runtime install fixture runner：** whole-folder manifest、relative supports、explicit CLI、dependency probe、authorized work/delivery write、unknown/symlink failure。 `[VERIFIED: docs/compatibility-matrix.md]`
2. **六行实际执行：** Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw、Hermes Agent 各一次，exact IDs/order，无 skip；自动 discovery 只记录观察，不作为 pass 条件。 `[VERIFIED: 49-CONTEXT.md]`
3. **UAT template/reference/lint：** 自动生成 PENDING；人工在非开发环境检查固定清单并绑定 PDF/PNG/font/Typst/environment hashes。 `[VERIFIED: school-pptx visual UAT pattern]`
4. **最终 aggregate：** 重读六 runtime raw records、UAT record、Phase 48 prerequisites 和 49-01 artifacts；只有全满足才 PASS，只有 UAT 合法 pending 才 `human_needed`。 `[RECOMMENDATION]`
5. **同步文档：** 更新 canonical `SKILL.md` adapter notes、`docs/compatibility-matrix.md` 和 skill index 中 graduate-resume 的实际支持状态；不创建 runtime-specific skill copies。 `[VERIFIED: AGENTS.md]`

## Sources

### Primary (HIGH confidence)
- `.planning/phases/49-runtime/49-CONTEXT.md` — D-01..D-16、阶段边界、canonical refs。 `[VERIFIED: codebase read]`
- `.planning/REQUIREMENTS.md` / `.planning/ROADMAP.md` / `.planning/STATE.md` — VERIFY-01..04、两计划边界、Phase 48 债务。 `[VERIFIED: codebase read]`
- `skills/graduate-resume/scripts/graduate_resume_pdf_gate.py` — 现有 PDF/PNG reopen 与逐页事实检查。 `[VERIFIED: codebase read]`
- `skills/graduate-resume/scripts/test_phase48_cli.py` — 字面 registry 与 required/called 模式。 `[VERIFIED: codebase read]`
- `skills/school-pptx/scripts/verify_school_pptx.py` / `references/visual-uat.md` — hash-bound、read-only human UAT lint 范式。 `[VERIFIED: codebase read]`
- `https://pymupdf.readthedocs.io/en/latest/page.html` — Page rect/text/fonts/pixmap API。 `[CITED: https://pymupdf.readthedocs.io/en/latest/page.html]`
- `https://typst.app/docs/reference/pdf/` — Typst PDF export 官方说明。 `[CITED: https://typst.app/docs/reference/pdf/]`

### Secondary (MEDIUM confidence)
- `docs/compatibility-matrix.md` — 六 runtime installation-time 与 explicit fallback 契约。 `[VERIFIED: codebase read]`
- `.planning/phases/48-deterministic-targeted-rendering-clean-batch-delivery/48-REVIEW.md` — 6 Blocker/3 Warning 发布债务。 `[VERIFIED: codebase read]`
- `https://owasp.org/www-project-application-security-verification-standard/` — ASVS 分类参考。 `[CITED: https://owasp.org/www-project-application-security-verification-standard/]`

### Tertiary (LOW confidence)
- 无外部 WebSearch-only 结论。所有 `[ASSUMED]` 项已集中列入 Assumptions Log。 `[VERIFIED: research process]`

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — 全部复用现有代码与本机已验证版本，没有新包。 `[VERIFIED: local commands and codebase]`
- Architecture: HIGH — 锁定决策明确，且 Phase 48/44 已有 registry、artifact reopen、UAT lint 先例。 `[VERIFIED: codebase read]`
- Pitfalls: HIGH — 关键风险来自实际 review findings、现有代码边界和锁定负面要求；三项推断已标 `[ASSUMED]`。 `[VERIFIED: 48-REVIEW.md]`
- Six-runtime execution availability: MEDIUM — 本机只具备 Codex、Claude Code、OpenCode，其他三者需外部真实环境。 `[VERIFIED: local command]`
- Human UAT completion: LOW — 尚无非开发环境 tester/signoff，执行时可能合法停在 `human_needed`。 `[VERIFIED: phase directory inspection]`

**Research date:** 2026-07-19
**Valid until:** 2026-08-18（核心架构稳定；runtime 版本/安装路径在执行当天必须重新探测） `[RECOMMENDATION]`
