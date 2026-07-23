# Phase 48: 确定性定向渲染与干净批量交付 - Context

**Gathered:** 2026-07-20
**Status:** Ready for planning

<domain>
## Phase Boundary

本阶段把 Phase 46 的已核实唯一事实源和 Phase 47 的冻结主题、照片及 1/2 页布局接成可离线执行的正式交付流程：生成一份通用版及全部已确认目标版，为每个版本正式生成三种受控主题的 Markdown、Typst、PDF 三件套，并以完整预检、candidate-first、精确 no-op、受控 history、rollback 和 fail-closed 路径语义发布到干净投递根。招聘信息抓取、跨 runtime 验收和聚合故障注入证明仍属于 Phase 49。

</domain>

<decisions>
## Implementation Decisions

### Deterministic Targeting
- **D-01:** 定向解析必须逐事实记录稳定 ID、所执行的动作（选择、排序、强调、排除或置顶）以及匹配理由，不能只输出最终顺序。
- **D-02:** 正式 Markdown YAML 保存简要追溯索引；逐事实的完整理由保存在授权的隐藏诊断/证据区域。Typst 与 PDF 不显示内部匹配理由。
- **D-03:** 个人信息、教育等核心事实始终保留；项目、技能、证书、实训和经历等非核心事实可按岗位相关性及冻结页数预算选择或省略。
- **D-04:** 用户可通过 CLI 按稳定事实 ID 显式保留、排除或置顶；覆盖参数必须冻结进该版本 metadata，不能回写 canonical 事实源或 target 招聘事实。

### Hard Requirement States
- **D-05:** 硬条件采用严格证据判定：只有已核实事实明确证明时才是“满足”；明确不符合为“缺口”；资料不足为“未知”；条件对该岗位实例不成立时才是“不适用”。不得用相似关键词推断满足。
- **D-06:** 每个存在缺口的目标必须单独显式允许继续生成；批量命令可以一次列出多个获准继续的目标 ID，但不能用长期全局开关绕过确认。
- **D-07:** “未知”默认允许生成并给出警告，不要求额外放行；正式简历和 metadata 均不得暗示未知条件已经满足。
- **D-08:** 预检在 CLI 中展示逐条件四态表格；完整条件矩阵写入隐藏 JSON 证据，正式 Markdown YAML 只保存四态汇总、证据摘要和是否经缺口放行。

### Version Matrix
- **D-09:** batch 默认生成一份通用版及全部已确认目标版；单份 render 用于明确选择一个通用版或目标版。
- **D-10:** 每个通用版和目标版都正式生成“保守稳妥 / 现代简洁 / 个性设计”三种主题，不采用“先预览一个、再只发布一个”的默认策略。离线 PDF 渲染不消耗 AI，因此三个主题均属于正式交付矩阵。
- **D-11:** 每个“版本 + 主题”只发布一个主页面版本。Phase 47 临界区或强制页数策略产生的另一页数版本只进入 preview/workdir，不占用正式 stem。
- **D-12:** 每份正式 Markdown 都是可独立审阅的最终定向文档，包含该版本实际采用的事实与顺序、主题、页数、照片模式、目标来源/日期和简要追溯索引；Typst 必须由这份最终 Markdown 派生，PDF 再由该 Typst 编译。

### Clean Batch Publication
- **D-13:** 投递根平铺全部正式三件套，不按单位或版本创建 current 子目录。根目录只允许当前 managed files 及约定的支持目录；诊断、缺口明细、照片规范化中间件、preview 和临时证据不得泄露到投递根。
- **D-14:** history 只归档实际更新或移除的版本，不复制本次未变化版本；但每个被归档版本必须保存完整 Markdown、Typst、PDF 三件套，不能只归档发生字节变化的单个文件。
- **D-15:** 所有定向版 stem 始终包含岗位，格式为“姓名简历-单位-岗位-主题”；通用版固定为“姓名简历-通用-主题”。姓名、单位、岗位和主题必须经过确定性安全规范化，且不得包含联系方式、身份证、原始 URL 等敏感信息。
- **D-16:** batch 的新版本矩阵是 current 的权威目标集合。目标减少时，预检必须明确列出拟移除版本；确认后先把这些版本的完整三件套归档，再从 current 删除。
- **D-17:** 单份与批量任务都必须先完成全部候选生成和完整预检。批量中任一目标、主题或三件套失败时，不得发布新增、更新或移除中的任何一项。
- **D-18:** no-op 以本次受影响版本的精确 managed path set 与逐文件 bytes 相等判定；完全相同的版本不发布、不归档，也不改变 current。
- **D-19:** 沿用 v1.18 的 candidate-first、handled error/INT/TERM rollback、held directory identity、unknown/symlink/partial/stale-work fail-closed 语义。单份更新不得破坏其他 current 版本，批量失败必须保持整个原 current 集合不变。

### Typst Local Threat Model
- **D-20:** Phase 48 不将“同一登录用户在本机校验后替换 Typst 快照”的 TOCTOU 视为必须缓解的攻击模型。保留冻结副本、运行前 identity/SHA-256、版本、输出上限与候选发布检查；Typst 通过已校验的快照路径以普通用户权限启动，不引入 setuid helper、系统安装或 ACL 前置条件。

### Claude's Discretion
- 定向评分权重、同分稳定排序规则和模块相关性词表可由研究与规划阶段确定，但必须离线、确定、可解释，并受稳定 ID 追溯约束。
- CLI 参数的具体拼写、metadata 字段名、隐藏 JSON schema、终端表格样式和安全文件名规范化细节由后续规划决定。
- history 序号目录内如何区分多个同时更新的版本可由实现选择，只要每个归档版本保持完整三件套且 rollback 可确定恢复。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone Scope And Locked Requirements
- .planning/ROADMAP.md — 定义 Phase 48 目标、成功标准、三条计划方向及 Phase 49 边界。
- .planning/REQUIREMENTS.md — 定义 TARGET-01..03 与 DELIVERY-01..03，尤其是四态硬条件、正式命名、批量完整预检和 clean-delivery 语义。
- .planning/PROJECT.md — 定义 v1.19 的 Markdown-first、离线零 token、多目标主题化简历目标。
- .planning/STATE.md — 记录 Phase 46/47 已完成及 v1.18 clean-delivery 决策的承接关系。

### Prior Phase Contracts
- .planning/phases/47-controlled-themes-photo-frozen-layout/47-CONTEXT.md — 锁定三主题、唯一事实源、照片模式、1/2 页决策、分页最小单元和多主题产品原则。
- skills/graduate-resume/references/schema-and-review-contract.md — 定义 graduate-resume/v2 事实源、稳定 ID、target 来源/日期/确认和一次追问边界。
- skills/graduate-resume/references/phase-46-baseline.md — 定义已实现 CLI、fixtures、受控字体和 Phase 48 交接前提。

### Graduate Resume Implementation Surface
- skills/graduate-resume/SKILL.md — canonical workflow、runtime-neutral 安全边界、正式三件套责任和当前命令面。
- skills/graduate-resume/templates/graduate-resume.md — 唯一可编辑事实源模板与当前 target 表达。
- skills/graduate-resume/scripts/graduate_resume_cli.py — 已有 validate/target/plan/verify 命令、target 归一化、照片解析及 render/batch 保留入口。
- skills/graduate-resume/scripts/graduate_resume_layout.py — 冻结容器、主题、照片、页数和安全本地资产解析。
- skills/graduate-resume/scripts/graduate_resume_typst.py — 现有 Typst 内容转义和冻结布局消费面。
- .planning/phases/48-deterministic-targeted-rendering-clean-batch-delivery/48-SECURITY.md — 记录 T-48-G08-03 的用户接受风险及本次重新审计结果。

### Reusable Clean Delivery Pattern
- skills/tiaokedan/scripts/delivery_transaction.py — 可复用的 descriptor-relative candidate、history、rollback、no-op、fault hook 和 fail-closed 事务模式。
- skills/end-of-term-teaching-materials/scripts/end_of_term/delivery.py — 固定 managed set 的完整候选校验、根目录 allowlist 和 handled rollback 参考。

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- graduate_resume_cli.py: 已有公开 shell/argparse 入口、稳定 JSON 错误边界、target 摘要和冻结 plan；Phase 48 可在保留现有命令兼容性的前提下实现 render/batch。
- graduate_resume_layout.py: 已生成不可变的主题、照片和页数计划，并持有稳定容器/条目 ID；target resolver 应在进入布局计划前产生版本化事实投影。
- graduate_resume_typst.py: 已有 candidate-controlled 文本转义，可用于从最终定向 Markdown 模型机械生成 Typst。
- delivery_transaction.py: 已实现安全目录描述符、候选树、完整候选校验、history、rollback、锁、故障注入点和字节 no-op，可抽取或适配为动态多 bundle 事务。

### Established Patterns
- canonical 事实源保持不变，所有目标、主题、页数和照片版本均是 renderer-owned 派生物。
- 正式 Markdown 是可审阅的语义交付物，后续 Typst/PDF 必须从它确定性派生。
- v1.18 clean delivery 使用显式 managed set、支持目录 allowlist、candidate-first publication、完整 bundle history 和 unknown/symlink fail-closed。
- 当前 render 与 batch 明确保留为后续实现，Phase 48 可以扩充参数而不需要兼容既有成功输出。

### Integration Points
- target resolver 位于 validate 后、frozen layout 前，消费稳定事实 ID 和 confirmed target brief，输出每个版本的最终事实投影及四态证据。
- render pipeline 消费一个版本投影和一个 ThemeSpec，生成最终 Markdown，再生成 Typst/PDF 候选三件套。
- batch coordinator 先展开“通用 + 全部 confirmed targets × 三主题”矩阵，完成全部条件判断、布局、编译、命名和候选验证后再进入统一发布事务。
- delivery transaction 需要从固定 stem 扩展为动态多 stem managed set，同时保留逐版本完整归档和全批失败不变语义。

</code_context>

<specifics>
## Specific Ideas

- 用户明确认为离线 PDF 渲染开销很小且不消耗 AI，因此不需要为了节省生成成本只发布一个主题；三种受控主题都应直接产生正式 PDF。
- 用户偏好“更新了谁，归档谁”，不希望每次单份修改都复制整个未变化投递集合。
- 定向版文件名无论是否冲突都应包含岗位，使投递文件离开目录上下文后仍可辨识目标岗位。

</specifics>

<deferred>
## Deferred Ideas

- 跨 runtime 安装验证、聚合故障注入、PDF 结构/布局验证和非开发环境字体 UAT 属于 Phase 49。

</deferred>

---

*Phase: 48-确定性定向渲染与干净批量交付*
*Context gathered: 2026-07-20*
