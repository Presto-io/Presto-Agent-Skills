# Phase 50: 受控视觉合同与模板预设 - Context

**Gathered:** 2026-07-23
**Status:** Ready for planning

<domain>
## Phase Boundary

为 `school-pptx` 锁定四种新增教学视觉构图及既有媒体页的受限 Markdown 语义、固定预设、容量与 `standard-school` manifest 所有权。该阶段只定义作者可表达的内容和模板拥有的视觉边界；不实现冻结物理计划、PPTX 发射、自动验证扩展或真人 UAT 签署。

</domain>

<decisions>
## Implementation Decisions

### 布局选择与模板所有权
- **D-01:** 首发必须同时支持 `hero-evidence`、`annotated-image`、`process-overlay`、`kpi-evidence` 四种布局；每一种都必须有可区分的教学语义和非空原生对象角色。
- **D-02:** 作者沿用既有 `::: slide {layout="..."}` 的唯一 `layout` 选择方式。每页只能有一个布局，不定义多布局匹配、自动推断或优先级。
- **D-03:** Markdown 仍只表达受限语义，不能提供坐标、尺寸、字体、颜色、背景、裁切、动画、raw OOXML 或其他样式覆盖；`standard-school` manifest/template 继续是主题、几何、裁切和视觉层级的唯一事实源。

### 新布局语义与容量
- **D-04:** `hero-evidence` 使用一张主图和 2--3 个 KPI。KPI 超量时不在 emitter 临时压缩；后续由 agent/skill 按冻结容量生成 Markdown 并稳定分页。
- **D-05:** `annotated-image` 使用 3--5 个标注；每个标注必须为“编号 + 短标签”，禁止自由段落。Markdown 使用编号清单，编号自动映射到 manifest 固定插槽，作者绝不提供坐标。
- **D-06:** `process-overlay` 的本地证据图可选。无图时使用纯原生流程预设；无论是否有图，流程文本都必须清楚关联真实教学场景。步骤超量后续按完整步骤原子稳定分页，不能靠缩字或渲染期重排。
- **D-07:** `kpi-evidence` 固定支持 2、3、4 项数据卡。每项为数值，单位、标签和短脚注可选；首发不提供趋势表达、图表或 SVG。超量卡由后续冻结计划稳定分页或定位报错。

### 媒体、图注与 Demo 边界
- **D-08:** `gallery` 与既有图文页面均使用 1--4 项 manifest 固定媒体预设；每张图片必须有非空图注，必要时可用文件名替代，不能接受空图注。
- **D-09:** 先生成可替换图片的测试版 Demo。临时 Demo 资产只允许在仓库已有的 ignore 目录中活动，不得提交、不得污染公开交付或变成 fixture 的正式媒体。
- **D-10:** 用户可以将图片放入工程目录或直接交给 AI；正式媒体仍遵循既有本地媒体、离线读取、hash 绑定、允许格式和受控 `contain` 契约。缺失或非法媒体沿用当前契约，允许局部可编辑 placeholder 时整体 render 仍为非零，绝不作为成功交付发布。

### 溢出、fixture 与人工审阅边界
- **D-11:** 超长标题、图注、标注、流程步骤或 KPI 优先按稳定规则分页；超出已定义能力时返回可定位的稳定错误，不能静默缩小到不可读或临时改变布局。
- **D-12:** 保留唯一完整 Markdown fixture，最终覆盖旧 11 种布局与四种新增布局；不拆成多个竞争性的完整来源。
- **D-13:** 本轮开发交付到用户可在 WPS 中亲自审阅的状态。真人 UAT 不是本轮自动完成门，任何自动验证或生成的表单都不能声称 UAT 已 PASS；后续不得将实际审阅责任推诿为发布完成的前置声明。
- **D-14:** 仓库为单人开发，直接在 `main` 按 commander 流程推进；本里程碑不 push。

### Claude's Discretion
- 临时 Demo 的具体文件名、ignore 目录内的组织方式，以及在既有媒体大小/格式安全边界内选择何种可替换测试图片，交由后续代理决定；不得扩大为可提交的公开资产或联网取图能力。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 里程碑范围与需求
- `.planning/ROADMAP.md` §Phase 50 — 锁定本阶段目标、VIS-01 至 VIS-03 和成功标准。
- `.planning/REQUIREMENTS.md` §受控视觉合同 — 受控 Markdown、四种布局与 1--4 项媒体预设的正式需求。
- `.planning/PROJECT.md` §Current Milestone: v1.20 School PPTX Visual Enrichment — 里程碑价值、主题和 Markdown-first 边界。
- `.planning/STATE.md` §Current Position — 当前阶段状态和工作流偏好。

### v1.20 调研结论
- `.planning/research/v1.20-SUMMARY.md` — 分期、范围排除和现有风险总览；其中旧的 `annotated-image` 暂缓建议已被本 CONTEXT 的 D-05 覆盖。
- `.planning/research/v1.20-visual-composition.md` — 四类构图的教学语义、受控视觉语言和样张边界。
- `.planning/research/v1.20-renderer-architecture.md` — manifest ownership、冻结计划和 emitter 不作布局决策的架构边界。
- `.planning/research/v1.20-visual-uat.md` — 自动验证与 hash-bound 真人 UAT 的证据分界；本轮仅交付至可审阅状态。

### 现有 school-pptx 合同与实现锚点
- `skills/school-pptx/references/markdown-contract.md` — 现有唯一 `layout` 属性、媒体语法、图注、禁止样式控制和 delivery 边界。
- `skills/school-pptx/templates/standard-school.manifest.yaml` — 现有 layouts、slot、文本预算、gallery 1--4 项预设和主题所有权的机器事实源。
- `skills/school-pptx/scripts/markdown_contract.py` — allowlist、Markdown 解析、媒体缺失和不支持样式的稳定诊断。
- `skills/school-pptx/scripts/template_report.py` — manifest/template 对照、renderer-owned region、非重叠和 gallery 预设验证模式。
- `skills/school-pptx/references/verification-contract.md` — 固定验证 registry、缺失媒体非成功语义和公开交付隔离。
- `skills/school-pptx/references/visual-uat.md` — 真实 viewer UAT 只能由真人填写的既有规则。
- `skills/school-pptx/fixtures/school-pptx-full.md` — 唯一完整 Markdown fixture 的现有基线。

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/school-pptx/references/markdown-contract.md`: 已有 `::: slide {layout="..."}` 单属性 DSL、图片 `![caption](path)` 语法以及非空图注的现有场景，可作为新增受限语义的外观基线。
- `skills/school-pptx/templates/standard-school.manifest.yaml`: 已有 `image-text` 槽位与 `gallery` 的 1/2/3/4 项 `item_presets`，可扩展为新增布局的固定 slot、容量和子区域事实源。
- `skills/school-pptx/scripts/markdown_contract.py`: 已有 manifest layout allowlist、来源行、媒体占位及 `UNSUPPORTED_STYLE`/`MEDIA_MISSING` 诊断模式。
- `skills/school-pptx/scripts/template_report.py`: 已有 renderer-owned native shape 映射、geometry containment/non-overlap、text budget 和 gallery preset 完整性校验。

### Established Patterns
- 公共 Markdown 只允许 `layout` 属性；所有未知属性与视觉控制面 fail closed。
- 图片路径相对 Markdown 解析，网络 URL 不获取；图片的既定 placement 是 `contain`。
- 预算、分页和物理映射属于后续 planner 的职责，PPTX emitter 只能消费已冻结计划。
- 成功公开交付只包含同 stem 的 Markdown 与 PPTX；diagnostic、verification 和临时预览属于 caller-owned workdir。

### Integration Points
- Phase 50 将接入 Markdown parser 的新布局语义、manifest 中的 layout/variant/slot/容量注册，以及 template-report 对新固定预设的结构校验。
- 现有完整 fixture 是后续扩展新布局覆盖的唯一入口，但本阶段不应直接将 ignore 目录中的临时 Demo 资产并入它。

</code_context>

<specifics>
## Specific Ideas

- Demo 采用智能制造教学语义，允许先使用可替换测试图片；正式素材由用户放入工程目录或直接提供给 AI 后，再依既有本地媒体契约处理。
- 标注图以固定编号插槽建立阅读路径，避免将 Markdown 演化为坐标 DSL。
- 流程图无图时仍应可表达工序、诊断或操作流程，且节点和连接线的可编辑性留给后续阶段实现。

</specifics>

<deferred>
## Deferred Ideas

- PPTX 发射前的冻结 variant、容量向量、逻辑到物理页映射和超量项分页实现属于 Phase 51。
- 原生标注、引线、流程节点、数据卡及媒体对象发射属于 Phase 52。
- 完整 fixture 扩充、固定自动验证 registry、runtime 文档和 hash-bound WPS 人工 UAT 表单/签署属于 Phase 53；本轮不将人工 UAT 标为 PASS。

</deferred>

---

*Phase: 50-受控视觉合同与模板预设*
*Context gathered: 2026-07-23*
