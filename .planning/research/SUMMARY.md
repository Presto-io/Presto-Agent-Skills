# Project Research Summary

**Project:** Presto Agent Skills v1.19 `graduate-resume` / 毕业生高级简历生成器
**Domain:** 面向电气、机电、智能制造、发电厂与新能源方向大专毕业生的离线 Markdown-to-Typst/PDF 简历技能
**Researched:** 2026-07-17
**Confidence:** HIGH（产品边界、Typst、Python PDF/图片能力与现有交付纪律均有直接依据；视觉密度需样张验收）

## Executive Summary

v1.19 是一个离线、可审阅、面向投递的简历生成技能，不是招聘平台、在线编辑器或自动投递系统。专家实现应把学生已核实事实收敛为唯一的主题无关 Markdown/YAML schema；通用版、多个单位/岗位定向版、主题化、照片/无照片和 1/2 页变体都只能从该 schema 派生。可选 AI 仅能把零散材料整理成待审阅草稿；一旦进入 `validate`、`target`、`plan`、`render`、`batch`，必须是零 token、无网络、可重复的纯 CLI 路径。

推荐采用单技能目录内的 Python 3.11+ CLI、锁定 Typst 0.15.0、PyYAML、Pillow 与 pypdf：受控主题和随技能交付的中文字体拥有视觉与几何，Python 负责 schema、定向规则、冻结布局计划、验证和候选发布，Typst 是唯一 PDF 生成器。正确流水线是 `Markdown -> CanonicalResume -> TargetedResume -> ThemeSpec -> FrozenLayoutPlan -> Typst -> PDF -> 验证 -> 干净交付`；其中布局计划而不是 Typst 的临场溢出处理，是 1/2 页与双页完整性的唯一权威。

最大风险是用系统字体、任意 Markdown/Typst、自动缩字或部分批量发布换取“生成成功”，从而破坏中文换行、真实性、可读性、隐私和既有 v1.18 交付保证。以固定字体与资产、白名单主题、经历不可拆块、有限密度阶梯、PDF 结构与视觉双重证据、候选优先的整 bundle 发布及失败关闭来防护；条件缺口、待确认资料、无效照片、非 A4、非 1/2 页、孤立标题、拆分经历或未知交付文件均不得发布投递件。

## Key Findings

### Recommended Stack

保留轻量的 skill-local 运行时，不引入 Node、数据库、浏览器、Office 自动化、运行时下载或模型 API。所有前置依赖只探测、不自动安装；六个 runtime 都安装完整 `skills/graduate-resume/` 目录，OpenClaw 与 Hermes 还须完成 shell wrapper 回退、前置探测和小型 fixture 渲染。

**核心技术：**

- **Python 3.11+ 与标准库：** 实现 CLI、受限 Markdown/YAML contract、路径/哈希/事务、定向、布局与交付；避免服务端和运行时网络。
- **Typst CLI 0.15.0：** 唯一的 `.typ -> .pdf` 引擎；以 `--root`、`--font-path`、`--ignore-system-fonts`、固定时间戳和 PDF 标准获得受控 A4 输出及同源 PNG 证据。
- **PyYAML 6.0.3：** 安全解析 front matter、target 与 batch 清单；Markdown 保留可审阅经历正文，YAML 只承载结构化标量与选择。
- **Pillow 12.3.0：** 校验和规范化可选照片，执行 EXIF 方向修正、尺寸/像素限制、sRGB 转换和受控 JPEG/PNG 产物。
- **pypdf 6.14.2：** 验证真实 PDF、精确 1 或 2 页、逐页 A4 mediabox、基础文本和 metadata；不把“可打开”误作版式通过。
- **固定 Noto Sans CJK SC 或 Source Han Sans CN 字体包：** 字体、许可证清单、哈希和 Typst family name 随技能交付；禁止系统字体 fallback，v1 首选单一 Sans 主题以减少度量漂移。

### Expected Features

**v1 table stakes：**

- 主题无关且可审阅的统一 resume schema，含稳定事实 ID、源位置、资料完整性/占位符/日期/重复项校验。
- 无岗位信息的通用版，以及由独立 target 文件驱动的多单位/岗位定向版；定向只能选择、排序和追溯已核实事实。
- 硬条件的 `meets/gap/unknown/not-applicable` 报告；未知不等于满足，未满足的 required 条件默认不发布定向 PDF。
- 登记制主题与照片/无照片布局变体；主题拥有字号、边距、槽位、密度和分页预算，schema 不含颜色、坐标、字体或 Typst 表达式。
- 同源 `Markdown -> Typst -> PDF` 三件套，明确的一页优先/两页模式、A4 检查、标题与首条目绑定、经历/项目不可拆、无空白或无标题续页。
- 零 token CLI 的 `validate`、`target`、`plan`、`render`、`batch`、`verify`；可选 AI 整理与确定性 CLI 严格分层。
- candidate-first 的干净交付、全 bundle no-op/history/rollback 语义；批次默认先完成所有 job 验证再发布。

**v1 应包含的差异化能力：** 电气相关课程实训、PLC/配电/安全/证书等可检索证据槽；变体 identity 至少包含 `target_id/theme/photo_mode/page_mode`；隐藏 evidence 或控制台给出定向选择理由；内容预算预检只做预警，最终以 PDF/布局 gate 为准。

**明确排除/延后：** 任何自动投递、招聘网站抓取或 JD 猜测、OCR/证书真伪核验、ATS 分数或录用预测、在线协作/托管、自由模板市场、用户自定义 Typst/字体/坐标/配色、将 AI 调用嵌入 render/batch，以及为凑页数自动删事实、缩到低于可读下限或生成第三页。硬条件为 gap 时可产出单独诊断的策略可在用户决定后支持，但不得产出投递 PDF。

### Architecture Approach

技能必须独立放在 `skills/graduate-resume/`，拥有自己的 `SKILL.md`、模板、references、字体/图标、shell wrapper、Python 模块和 fixtures；只能复用 v1.18 的交付语义，不能运行时调用兄弟技能。流水线单向且边界明确：解析器保留源行号，validator 构建 `CanonicalResume`，target resolver 产生不可回写的 `TargetedResume` 和缺口报告，theme registry 选择白名单 `ThemeSpec`，planner 先冻结 `FrozenLayoutPlan`，emitter 机械发射 Typst，verifier 生成结构/视觉 evidence，publisher 仅发布已通过的完整候选 bundle。

**主要组件：**

1. **Markdown parser + schema validator：** 把受限 Markdown/YAML 转为有稳定 ID 的唯一事实模型，并对未知字段和 review marker 失败关闭。
2. **target resolver：** 根据已确认 target 规则计算 included/deprioritized/qualification gaps；不推断、补齐或篡改资格事实。
3. **theme registry + photo normalizer：** 从白名单主题读取 token、A4 预算与照片槽；照片必须是允许根内的普通本地文件，拒绝符号链接、伪装格式、超限尺寸和解压炸弹。
4. **layout planner：** 先一页、再预定义两页语义分区；预留标题与首项、完整经历块，输出可审计的 `FrozenLayoutPlan`，不以反复编译或缩字修补。
5. **Typst emitter + PDF verifier：** emitter 只执行计划，以 `block(breakable: false)` 与计划页间断作第二道防线；验证 schema、定向、主题、计划、Typst metadata、PDF A4/页数/文本/照片模式。
6. **delivery publisher + aggregate verify：** 候选目录完整生成，精确 managed path set、whole-bundle 比较、历史归档和可处理失败回滚；日志、缺口报告、布局 JSON、哈希与 PNG 只留在 `.work/`/外部 workdir。

### Critical Pitfalls

1. **把系统字体或 fallback 当作可用字体。** 中文字形与换行会改变页数；随技能锁定并校验字体包、family name、哈希和 Typst 版本，以 `--ignore-system-fonts` 编译。
2. **让主题、照片或定向污染基础资料。** 会产生多份事实真相和跨目标串味；只允许 `CanonicalResume` 派生不可覆盖视图，主题只映射标准字段，照片只是素材引用与 job 选择。
3. **在 Typst 渲染期自动缩字、删 bullet 或硬凑页数。** 会造成不可解释的低可读性或拆分经历；先冻结有限密度阶梯和 1/2 页计划，不能容纳即指出 entry 并非零失败。
4. **把 PDF 非空/能打开等同投递通过。** 无法发现非 A4、孤立标题、跨页经历或错误照片；要求语义、结构、PDF 内容/页面、PNG 视觉与人工 UAT 的分层 gate。
5. **批次部分成功或失败污染当前成果。** 会破坏可审阅版本集；默认全体 job 预检与候选验证通过后再发布，未知文件/符号链接/部分 bundle 均人工审计、失败关闭。

## Implications for Roadmap

### Phase 46: 资料契约、字体与可验证夹具

**Rationale:** schema、输入身份与字体是之后主题、定向和页数结论的共同前置，不能先写 renderer。
**Delivers:** 独立 skill 骨架、canonical `SKILL.md`/六 runtime 边界、锁定前置探测、字体/许可证/manifest、统一 Markdown/YAML schema、target/batch contract、稳定 ID、正常/缺口/待确认/有无照片 fixtures 与 validator。
**Addresses:** shared schema、真实性校验、通用/定向输入、零 token 边界、照片规则。
**Avoids:** schema 主题耦合、目标关键词回写、隐式系统字体、个人信息写入不安全路径。

### Phase 47: 受控主题、照片和 1/2 页冻结布局

**Rationale:** 先手工验收同一资料的一页、两页、无照片、照片参考面，才能将真实中文密度固化为可测试主题预算。
**Delivers:** `ThemeSpec` registry、首个受控主题及主题自检、Pillow 安全照片规范化、无照片重排、有限密度阶梯、`FrozenLayoutPlan`、标题/首项与经历不可拆规则、溢出诊断。
**Addresses:** 主题化、照片/无照片、1/2 页 A4、双页逻辑完整性。
**Avoids:** 任意样式输入、空照片框、自动裁剪/缩字、孤立标题、第三页和拆分经历。

### Phase 48: 确定性定向渲染与干净批量交付

**Rationale:** 只有 schema 与布局已闭合，target resolver 和三件套输出才不会把选择规则或发布失败混入内容层。
**Delivers:** target resolver 和资格四态/可追溯缺口报告、Typst emitter、Typst 编译、pypdf structure/content gate、单 job candidate 交付、默认全有或全无 batch transaction、exact-set/no-op/history/rollback。
**Addresses:** 多 target、定向选择、Markdown/Typst/PDF 三件套、零 token batch、失败隔离。
**Avoids:** AI in the loop、硬条件虚构、同 stem 覆盖、半批发布、日志/evidence 泄露至投递根。

### Phase 49: 证据回归、跨 runtime 与发布验收

**Rationale:** 文档和渲染命令完成不代表 PDF 可投递；必须独立复算所有 gate，并在非开发机字体环境验证。
**Delivers:** aggregate verify、正常与故障注入测试、同源 144 PPI PNG evidence、PDF/布局 metadata 检查、macOS 加至少一个非 macOS 的视觉 UAT、六 runtime adapter 的安装期 fixture 验证，特别是 OpenClaw/Hermes。
**Addresses:** 交付可信度、可重复性、跨 runtime 可用性。
**Avoids:** 仅测开发机、仅检查 PDF 存在、字体漂移、无证据的兼容性承诺。

### Phase Ordering Rationale

- 先锁 schema、资产和字体，避免后续主题容量、定向和 PDF 页数建立在不稳定输入上。
- 将布局作为独立于 Typst 与发布层的冻结计划，确保 1/2 页规则可解释、可回归，且不允许渲染器改写事实。
- 只有单 job 的内容、分页和 PDF gate 都闭合后，才把 v1.18 candidate-first 语义扩展到定向批量，避免用发布机制掩盖内容失败。
- 最后做跨运行时与视觉 UAT，因为这是依赖受控字体、主题样张和端到端产物的系统级验收，而不是文档检查。

### Research Flags

**规划时需深入研究：**

- **Phase 47：** 中文/Latin 混排的实际字号、行高、边距、主题容量、照片 crop/contain 策略和双页锚点都必须通过受控样张与人工 UAT 定稿。
- **Phase 48：** target 硬条件的最小表达式、默认阻断边界和 gap report 的公开位置需要落实为精确 schema/交付契约；PDF 文本/图像证据组合也须用真实与损坏 fixture 验证。
- **Phase 49：** 六 runtime 的 whole-folder 发现、路径权限、字体可见性和 OpenClaw/Hermes shell fallback 要在真实安装环境确认。

**可按成熟模式实施：**

- **Phase 46：** skill-local 目录、受限 YAML 校验、fixture 驱动和前置依赖 probe 与现有文档技能模式一致。
- **Phase 48 的候选发布子项：** 直接移植 v1.18 已验收的 exact-set、no-op、history、rollback 与 fail-closed 语义，并在本 skill 内重新实现测试。

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Typst 0.15.0、本地能力与官方文档；pypdf/Pillow 官方 API；现有 skill-local CLI 先例。 |
| Features | HIGH | 直接来自 v1.19 项目目标和明确的 shared schema、零 token CLI、分页纪律。 |
| Architecture | HIGH | 与仓库既有 Markdown-first/candidate-first 模式一致，且 Typst 不可拆 block/分页能力有官方依据。 |
| Pitfalls | HIGH | 基于已知字体、PDF、图片、批处理和 clean-delivery 失败模式；视觉阈值的具体值仍待样张验证。 |

**Overall confidence:** HIGH

### Gaps to Address

- **硬条件语言与阻断策略：** 用户需决定 v1 仅接受布尔/枚举/最小年限等受控规则，还是加入受控文本规则；建议 v1 限于前者，并将 `required.all` gap 默认阻断投递 PDF。
- **照片默认与授权：** 用户需确认默认无照片，以及照片是否由候选人、投递渠道或每个 target 显式授权；在决定前采用无照片默认和 `contain` 优先，避免头部裁切。
- **中文可读性与主题容量：** 需由代表性一页/密集两页 fixture 在 macOS 和至少一个非 macOS 环境执行 PNG/PDF 人工 UAT 后锁定最小字号、行高、边距与预算。
- **target 时效与报告可见性：** 用户需决定 brief 的 `as-of`/截止日期策略，以及缺口报告仅作为隐藏诊断还是允许单独公开；建议无日期/未人工确认的 target 不生成最终定向 PDF，报告不进入投递 bundle。
- **本地历史隐私：** 技能可限制路径和产物边界，但无法单独承诺 OS 级加密或访问控制；用户需按部署环境决定历史目录保留与保护策略。

## Sources

### Primary (HIGH confidence)

- [.planning/PROJECT.md](../PROJECT.md) — v1.19 范围、共享 schema、Markdown→Typst→PDF、零 token CLI、主题/照片、1/2 页和 clean-delivery 强制纪律。
- [STACK.md](STACK.md) — 固定版本、字体/照片/PDF 证据、六 runtime 前置和交付边界。
- [FEATURES.md](FEATURES.md) — table stakes、差异化能力、反功能、用户流程与验收点。
- [ARCHITECTURE.md](ARCHITECTURE.md) — 单向模型、组件边界、冻结布局、CLI 与 candidate publication。
- [PITFALLS.md](PITFALLS.md) — 字体、真实性、分页、隐私、批处理与跨 runtime 风险防护。
- Typst 官方文档：CLI、`block`、`pagebreak`、`text`、`image`、`query` — 受控编译、不可拆模块、分页与 metadata 验证依据。
- pypdf 与 Pillow 官方文档 — PDF 结构检查、EXIF 转置、图像尺寸与解压炸弹防护。

---
*Research completed: 2026-07-17*
*Ready for roadmap: yes*
