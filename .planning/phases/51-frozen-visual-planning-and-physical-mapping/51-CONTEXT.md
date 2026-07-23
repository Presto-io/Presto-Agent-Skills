# Phase 51: 冻结视觉规划与物理映射 - Context

**Gathered:** 2026-07-23
**Status:** Discussion captured; Phase 50 audit and completion remain required before Phase 51 planning

<domain>
## Phase Boundary

在任何 PPTX 原生对象发射前，把已审阅 Markdown、已确认本地媒体与 `standard-school` manifest 投影为唯一、不可变、可复算的视觉计划与物理页计划。该计划必须冻结视觉意图、variant、容量、逻辑到物理页映射、媒体绑定与对象角色；它不发射 PPTX、不完成完整 fixture/验收，也不执行 WPS 真人 UAT。

Phase 50 的自动合同验证已通过，但 `STATE.md` 仍正确标记为等待 audit/complete。本 Context 仅记录用户已给出的下一阶段设计决策，以免后续重复讨论；它不改变该 gate，也不授权 Phase 51 计划或实现越过该 gate。

</domain>

<decisions>
## Implementation Decisions

### 冻结层级与哈希绑定
- **D-01:** 规划分为两个不可变层级：`VisualPlan` 是输入绑定后、尚未展开物理页的语义视觉投影；`PhysicalDeckPlan` 是唯一可交给 emitter 的物理页投影。两者均须使用冻结数据结构，并公开稳定的 canonical JSON projection 以便复算与验收。
- **D-02:** `VisualPlan` 的不可变字段至少包括计划 schema 版本、`markdown_sha256`、`manifest_sha256`、`template_sha256`、按作者顺序的逻辑页标识/源行/layout/标题/视觉语义、每页候选容量与对象角色、以及每个已确认媒体的逻辑引用、单次安全读取所得 SHA-256、字节数、格式和 `contain` 策略。不得仅绑定路径，或在完成计划后按路径重新读取媒体。
- **D-03:** `PhysicalDeckPlan` 的不可变字段至少包括 schema 版本、`visual_plan_sha256`、完整输入 binding、按物理顺序的 `physical_index`、来源 `logical_index`、continuation 序号、唯一 layout/variant/preset ID、冻结容量、物理页对象角色、原子内容组、媒体 hash binding、稳定诊断，以及完整且有序的 `logical_to_physical` 映射。计划外字段不得在 emitter 中补推导。
- **D-04:** 计划生成只接受 hash 已确认、格式/边界已通过既有媒体契约的输入。缺失、非法或 hash 不匹配媒体继续沿用非零与安全 placeholder 的既有合同；其诊断、来源行和媒体身份必须被冻结，不能在发射时转为成功或替换为另一文件。

### Variant、容量与稳定分页
- **D-05:** variant 只可由已冻结的 manifest 预设选择，且由 `layout` 与当前物理页的原子对象数量唯一确定：`hero-evidence` 只选 2/3 KPI，`annotated-image` 只选 3/4/5 个编号锚区，`process-overlay` 只选 2--6 步，`kpi-evidence` 只选 2/3/4 张数据卡，`gallery` 与 `image-text` 只选 1--4 项媒体+非空图注预设。作者不写 variant、坐标、裁切或字号。
- **D-06:** 所有可拆分内容按 Markdown 源顺序形成连续分区；每个媒体+图注、KPI 数据卡、标注的编号+短标签+固定锚区+引线、流程节点+其连接关系均为不可拆的原子组。分页先最少化物理页数；若存在同页数方案，选择每一页尽量容纳更长的最早连续前缀的方案（按每页原子组数的降序向量作字典序 tie-break）。此规则不得依赖本机字体、运行时测量波动或迭代顺序。
- **D-07:** 若某个原子组在空白物理页上都没有合法 manifest variant，或需要的完整连续分区无法表达，则稳定非零失败。诊断必须包含固定错误码、layout、逻辑页索引、源行、原子组索引和修复建议；不得缩字、裁切、静默丢失、拆开原子组或临时替换布局。对 Markdown parser 已拒绝的超量/非法结构，保持其现有可定位诊断，不在规划器重新解释为成功输入。

### 逻辑到物理映射与 emitter 禁止事项
- **D-08:** 每个逻辑页都要产生按来源顺序的完整 `logical_to_physical` 条目；一个逻辑页可映射到一个或多个连续物理页，continuation 只是一项冻结元数据，不是 emitter 临时生成的内容。所有物理页必须可反向追溯到 Markdown 源行、manifest variant 和媒体 SHA-256。
- **D-09:** emitter 只能机械消费完整 `PhysicalDeckPlan`、同 hash 的 manifest/template/媒体输入，并按冻结对象角色创建后续原生对象。emitter 严禁重新选择 layout、variant、preset、分页、原子分区、裁切、字号、媒体或逻辑到物理映射；hash 不一致、字段缺失、未知 variant 或映射不全必须失败关闭。
- **D-10:** Phase 51 不触及 PPTX 原生对象发射、完整 fixture 扩充、固定 aggregate 验收、runtime 文档或 WPS 人工 UAT。用户会在后续交付可审阅后亲自进行 WPS 审阅；自动计划验证不得声称 UAT 通过。

### 承接已锁定的视觉合同
- **D-11:** 首发四种布局全部保留，页面通过既有唯一 `layout` 属性选择；`annotated-image` 使用连续编号清单映射 manifest 固定插槽，流程证据图可选，KPI 不引入趋势/图表/SVG，所有图片图注非空。媒体仍离线、本地、`contain` 且失败关闭；ignore 目录内的临时 Demo 不进入正式 fixture 或公开交付。

### Claude's Discretion
- 计划模型的模块拆分、类/函数名称、canonical JSON 的键排序实现、稳定错误码命名和验证脚本组织由后续代理依照既有 `pptx_model.py`、`pptx_paginate.py` 与 verifier 模式决定，但不得改变 D-01 至 D-11 的字段、排序、边界或阶段范围。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### v1.20 范围与 Phase 50 合同
- `.planning/ROADMAP.md` §Phase 51 — PLAN-01/PLAN-02 的目标、成功标准与阶段顺序。
- `.planning/REQUIREMENTS.md` §冻结计划与原生对象 — PLAN-01/PLAN-02 的可验收需求与范围围栏。
- `.planning/STATE.md` §Current Position and §Operator Next Steps — Phase 50 audit/complete gate 仍未解除。
- `.planning/phases/50-controlled-visual-contract-and-template-presets/50-CONTEXT.md` — 用户锁定的四布局、标注、KPI、流程、图注、Demo 与 UAT 边界。
- `.planning/phases/50-controlled-visual-contract-and-template-presets/50-RESEARCH.md` — Phase 50 的合同和 manifest 研究结论。
- `.planning/phases/50-controlled-visual-contract-and-template-presets/50-01-SUMMARY.md` — 已落地的 Markdown 受限语义与 parser 边界。
- `.planning/phases/50-controlled-visual-contract-and-template-presets/50-02-SUMMARY.md` — 已落地的 15-layout manifest、容量、角色和预设事实源。
- `.planning/phases/50-controlled-visual-contract-and-template-presets/50-VERIFICATION.md` — 仅 Phase 50 自动合同 PASS，明确未覆盖本阶段或 UAT。

### school-pptx 既有冻结计划与实现接口
- `skills/school-pptx/scripts/pptx_model.py` — 既有 immutable `PhysicalDeckPlan`、projection 与 logical-to-physical 数据模型。
- `skills/school-pptx/scripts/pptx_paginate.py` — 既有确定性分页、稳定诊断与物理页构造模式。
- `skills/school-pptx/scripts/pptx_emit.py` — emitter 只消费冻结计划、不得分页的现有边界。
- `skills/school-pptx/scripts/pptx_render.py` — parse → plan → projection → emit 的现有集成点。
- `skills/school-pptx/scripts/markdown_contract.py` — 已审阅 Markdown、媒体元数据与源行的唯一输入模型。
- `skills/school-pptx/templates/standard-school.manifest.yaml` — 15 种布局的唯一 geometry、角色、容量与 preset 事实源。
- `skills/school-pptx/scripts/template_report.py` — manifest 受控视觉合同的机器可读验证。
- `skills/school-pptx/references/markdown-contract.md` — 作者不可控制几何/样式与媒体语义的公开边界。
- `skills/school-pptx/references/renderer-and-pagination.md` — 已有 logical-to-physical 冻结、发射和可编辑性约束。
- `skills/school-pptx/references/verification-contract.md` — 证据、hash 与自动验证不得冒充真人 UAT 的边界。

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `pptx_model.py`: frozen dataclass、projection 和有序映射已是既有物理计划的可复用基线。
- `pptx_paginate.py`: 确定性分区、预算和 `RenderDiagnostic` 模式可承载新视觉内容的稳定分页。
- `markdown_contract.py`: 已提供受限视觉结构、来源行和本地媒体引用；不得再解析 Markdown。
- `template_report.py` 与 `standard-school.manifest.yaml`: 15-layout 的角色、容量、固定锚区和 1--4 预设可作为 variant 的唯一选择域。

### Established Patterns
- 语义拆分、容量决策与 logical-to-physical 映射在发射前冻结；`pptx_emit.py` 中明确没有 pagination。
- 验证使用固定注册表、稳定诊断和 mutation 负例，避免以常量或人工观察冒充可复算证据。
- 媒体读取与 hash 绑定需沿用既有 descriptor-read 边界，计划后不得路径二次读取。

### Integration Points
- Phase 51 应位于 `markdown_contract.py` 的 canonical document 与 `pptx_emit.py` 之间，扩展/适配 `pptx_model.py` 和 `pptx_paginate.py` 的规划投影。
- Phase 52 只能消费本阶段冻结并已验证的 `PhysicalDeckPlan`，不得接管 variant 或分页决定。

</code_context>

<specifics>
## Specific Ideas

- `annotated-image` 以固定编号插槽建立阅读路径，永不演化为 Markdown 坐标 DSL。
- 测试版 Demo 可在已忽略目录内使用可替换图片，但其产物不属于提交的 fixture 或正式交付。
- 交付目标是先达到可由用户亲自 WPS 审阅的状态；本阶段只提供其所需的可复算计划基础。

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within Phase 51 scope. PPTX 原生对象发射、完整验收、runtime 文档和 WPS 真人 UAT 分别留给 Phase 52/53。

</deferred>

---

*Phase: 51-冻结视觉规划与物理映射*
*Context gathered: 2026-07-23*
