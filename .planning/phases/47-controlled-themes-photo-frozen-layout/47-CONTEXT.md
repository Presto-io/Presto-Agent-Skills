# Phase 47: 受控主题、照片与冻结布局 - Context

**Gathered:** 2026-07-18
**Status:** Ready for planning

<domain>
## Phase Boundary

本阶段交付同一份已核实简历事实源在受控主题、照片模式与 1/2 页 A4 布局下的稳定呈现规则。重点是冻结主题家族、照片占位行为、页数决策、分页最小单元、模块容器与受限重排策略，为后续研究与实现提供明确的 renderer-owned contract。

</domain>

<decisions>
## Implementation Decisions

### Theme Families
- **D-01:** 三种主题只允许是样式差异，不是内容差异。主题之间不得通过增删事实、改变模块语义或切换内容强调逻辑来制造差异。
- **D-02:** 三种主题允许有明显不同的页面构图，不要求“同骨架换皮”。后续实现可在单栏、双栏、信息区比例、装饰强度等方面形成清晰区分。
- **D-03:** 主题家族固定为 `保守稳妥 / 现代简洁 / 个性设计`，作为第一批正式主题边界。
- **D-03a:** 首批三种主题必须完整可见和可选，但不是永久数量上限；主题通过 renderer-owned registry 扩展，后续新增主题不得改写 `graduate-resume/v2` 事实 schema 或改变已验证事实。
- **D-04:** 主题需要像常见简历模板那样提供风格差异，但仍保持职业感、可打印、可投递，不走海报化路线。

### Source Of Truth And Derivation
- **D-05:** `graduate-resume.md` 是唯一可编辑事实源；1 页版、2 页版、主题版、照片版都必须从这份源文件派生，不维护独立事实 MD。
- **D-05a:** 事实源采用 v2 混合格式：首页信息栏 `profile`、可选本地 `photo` 路径与派生 `preferences` 位于 YAML frontmatter，教育、技能、证书、项目、实训、经历和目标位于 Markdown 正文；省略 `photo` 即无照片，正文顺序不构成事实语义。
- **D-06:** 用户后续修改资料时，应继续修改唯一事实源并重跑派生流程；如果修改的是页数、主题或照片偏好，则优先通过 frontmatter 偏好字段或 CLI 参数表达，而不是复制内容。
- **D-07:** 新增个性化模块时，默认由 agent 判断其容器归属，但允许用户显式覆盖。

### Container Model And Missing Modules
- **D-08:** 页面系统采用两类通用容器承接模块：`fact-block` 用于个人信息、摘要、教育、技能等结构化信息块；`list-entry` 用于项目、实训、经历、证书、竞赛、活动等条目型模块。
- **D-09:** 容器是承载方式，不是抹平模块身份；教育、项目、证书等模块语义仍需保留，不能退化为匿名卡片流。
- **D-10:** 缺失模块直接不渲染，由其余容器自然补位；不保留假空白，不编造内容。
- **D-11:** 布局适配采用“标准模块集合 + 可选模块启用 + 受控顺序 + 自适应补位”，而不是为每个模块预留固定空槽。

### Photo Variants
- **D-12:** 照片是固定占位区域的可选元素，不是可自由摆放内容。
- **D-13:** 每个主题固定自己的照片位置，主题内不再派生额外的位置变体。
- **D-14:** 无照片时，照片及其装饰元素必须一起消失；只有左侧或上部照片这类会挤占主内容流的主题，正文才需要补齐移动。
- **D-15:** 对右侧、下部或其他对主内容骨架影响较小的照片位，无照片时可以基本保持整体布局不变。
- **D-16:** 照片形态和装饰语言允许由主题决定，例如边框、色块、条形等，但必须保持职业感。
- **D-17:** 照片适配默认优先不裁切、保持比例；必要时允许受控裁切，但默认不强制填满照片区域。
- **D-17a:** 照片槽位不得超过标准 2 寸照片尺寸 `35 mm x 49 mm`；在此上限内按主题固定槽位等比放置，禁止拉伸。

### Page Count Strategy
- **D-18:** 自动页数模式不采用“一页优先”或“两页优先”的硬编码，而是按内容量判断最合适页数。
- **D-19:** 自动模式采用三段式判断：`明显更适合 1 页 / 明显更适合 2 页 / 临界区`。
- **D-20:** 内容明显偏少时默认直接生成 1 页；内容明显偏多时默认直接生成 2 页；不为凑 2 页而扩页，也不为压成 1 页而过度收缩。
- **D-21:** 临界区时系统应给出建议页数，并同时生成两种页数版本；主产物采用建议页数，另一种页数版本作为对照产物。
- **D-22:** 自动模式尽量不失败；单页不合适就转双页，只有连双页也超边界时才失败关闭。
- **D-23:** 用户强制 1 页时允许激进压缩，但仍需明确提示更推荐 2 页，并同时产出推荐的 2 页版。
- **D-24:** 用户强制 2 页但内容不足时，应提示更适合 1 页，但仍按要求生成 2 页版。

### Pagination And Layout Freezing
- **D-25:** 分页的最小完整单元是“单个条目”，不是整个模块。
- **D-26:** 模块整体尽量不拆页；必要时允许模块跨页，但单个条目不可拆。
- **D-27:** `项目 / 实训 / 经历` 按单条严格不可拆处理。
- **D-28:** `证书` 允许整组跨页续下，但同一证书条目内部不可拆。
- **D-29:** `技能` 允许按组续页，但不得出现页尾只挂技能组标题、下一页才出现组内容的阅读障碍。
- **D-30:** `个人信息` 固定为首页首位锚点，不可下沉到中后段；`教育` 尽量保持在前部稳定区域。
- **D-31:** 布局允许做“受限重排”以改善分页和阅读顺序，但不能破坏正常简历阅读习惯，例如不得把个人信息挪到非首位。
- **D-32:** 当分页困难时，优先在允许范围内调整模块顺序，再做密度压缩。

### Theme Selection And Preview Strategy
- **D-33:** 系统不应让用户只看到单一主题，避免被首个模板限制选择空间。
- **D-34:** 当前阶段锁定“支持多主题预览”的产品原则，但预览产物格式、发布路径、是否输出 PDF/PNG/HTML 等工程细节延后到 Phase 48/49 再定。

### Claude's Discretion
- 具体三套主题的视觉语言、色彩强度、字体层级、单双栏构图和照片装饰细节由后续研究与实现阶段在上述边界内收敛。
- `fact-block` 与 `list-entry` 的字段映射细节可由 agent 默认判断，但需保留用户覆盖接口。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone Scope And Requirements
- `.planning/ROADMAP.md` — 定义 Phase 47 的目标、成功标准、三条计划拆分以及与 Phase 48/49 的边界。
- `.planning/REQUIREMENTS.md` — 定义 THEME-01..05 的正式要求，尤其是主题切换、照片模式、1/2 页收敛与失败关闭语义。
- `.planning/PROJECT.md` — 定义 v1.19 的总体目标、Markdown-first 和可打印 PDF 简历方向。
- `.planning/STATE.md` — 记录当前项目已完成 Phase 46、即将执行 Phase 47 的阶段状态。

### Graduate Resume Baseline
- `skills/graduate-resume/SKILL.md` — 定义 canonical skill 目标、现有 CLI 边界和不能把主题差异写成内容差异的工作流前提。
- `skills/graduate-resume/references/schema-and-review-contract.md` — 定义唯一事实源、照片 contract、target contract 与 Phase 46/47 边界。
- `skills/graduate-resume/references/phase-46-baseline.md` — 定义已冻结的 CLI、fixtures、受控字体与后续交接前提。
- `skills/graduate-resume/templates/graduate-resume.md` — 当前唯一事实源模板，后续 1 页/2 页和主题版本都必须从这里派生。

### Existing Implementation Surface
- `skills/graduate-resume/scripts/graduate_resume_cli.py` — 当前已实现的资料校验、照片模式解析、偏好字段和后续 phase 的 CLI 入口保留面。

### Research And Pitfalls
- `.planning/research/PITFALLS.md` — 记录本里程碑在分页、主题预算、照片敏感信息、双页逻辑分页与受控字体上的关键风险与防线。

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/graduate-resume/scripts/graduate_resume_cli.py`: 已有 `preferences.theme`、`preferences.preferred_pages`、`preferences.photo_mode` 校验与 `resolve_photo_mode()`，可作为 Phase 47 页数/照片策略的现有命令面。
- `skills/graduate-resume/templates/graduate-resume.md`: v2 模板将信息栏 `profile`、可选 `photo` 路径和派生 `preferences` 放在 YAML，教育、技能、证书、项目、实训、经历和 targets 放在 Markdown 正文；可直接映射到 `fact-block` / `list-entry` 容器。
- `skills/graduate-resume/references/schema-and-review-contract.md`: 已把照片与主题布局剥离为“后续 phase 决策”，说明 Phase 47 应保持 renderer-owned defaults，而不是回写 schema。

### Established Patterns
- 仓库当前技能普遍采用“唯一可审阅事实源 + 后续派生产物”的模式，已在教学文档、PPTX 和 clean-delivery 相关阶段中反复强化。
- renderer-owned contract 是既有仓库偏好：用户输入存语义内容，布局预算、字体、分页、照片槽位等由模板/渲染器控制，不暴露为自由排版旋钮。
- Phase 46 已明确 `render`、`batch` 为后续实现，说明 Phase 47 可以专注主题和布局 contract，而不必同时解决最终交付事务。

### Integration Points
- Phase 47 的决策会直接约束后续 `render` / `batch` 命令的主题参数、页数选择、双版本对照生成和照片变体行为。
- 通用容器模型将成为 Typst 模板和布局规划器的中间抽象，应在不改写事实 schema 的前提下完成映射。
- 多主题预览原则已被锁定，但具体预览产物格式要在 Phase 48/49 与交付和验证机制一起设计。

</code_context>

<specifics>
## Specific Ideas

- 用户希望三套主题像常见简历模板一样有明显风格差异，但不能让内容和模块语义随主题漂移。
- 用户特别强调 HR 不应为了看明白单个条目而来回翻页，因此分页规则需要围绕“条目完整阅读”设计。
- 用户提出通用容器方案来承接未来个性化模块，目标是减少因新增模块而重做版式系统的成本。
- 用户认可“多主题预览”的产品方向，但要求把预览产物形态留到后续阶段再定，避免当前阶段越界到交付细节。

</specifics>

<deferred>
## Deferred Ideas

- 多主题预览的具体产物形态、路径、命名、是否输出 PDF/PNG/HTML、以及与正式交付的关系，延后到 Phase 48/49 讨论。
- 推荐排序、轻变体数量、是否先做 style pass 再做 final pass 等样式选择交互细节，延后到后续定向渲染与验证阶段细化。
- `⚠ Unpackaged spikes/sketches detected — run /gsd:spike --wrap-up or /gsd:sketch --wrap-up to make findings available.`

</deferred>

---

*Phase: 47-受控主题、照片与冻结布局*
*Context gathered: 2026-07-18*
