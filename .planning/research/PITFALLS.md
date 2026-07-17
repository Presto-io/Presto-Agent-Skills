# Domain Pitfalls: v1.19 毕业生高级简历生成器

**Domain:** 面向电气、机电、智能制造、发电厂与新能源方向大专毕业生的 Markdown-first 简历生成
**Project:** v1.19 毕业生高级简历生成器
**Researched:** 2026-07-17
**Overall confidence:** HIGH（项目既有 clean-delivery 约束与 Typst 官方文档）；MEDIUM（中文招聘信息源与跨平台字体实际覆盖需用阶段 fixture 验证）。

## Executive Risk Position

本技能不是“把一份 Markdown 排成 PDF”，而是受约束的求职材料发布器。它必须同时保证事实可审阅、目标岗位可追溯、页面可读、个人信息最小暴露，以及多版本批量运行不污染已确认交付。只检查 Typst 编译成功或 PDF 非空，无法证明它可投递。

最应前置的约束有三个。第一，页面数、最小字号、模块不可拆分、主题布局与照片位置必须由 renderer-owned contract 决定，而不是允许用户靠空行、手工分页或缩小字体“挤进去”。第二，岗位要求属于有时效的外部事实；CLI 可以在既有、已归档的岗位 brief 上做确定性匹配，但不能在零 token 模式中自行推断或声称“当前招聘要求”。第三，带照片、电话、邮箱、身份证明、住址或完整出生日期的源资料与中间件都应按敏感输出处理，不能进入公开 delivery、history 或普通诊断。

## Critical Pitfalls

### Pitfall 1: 以“能编译”为准，动态内容导致满页溢出或错误两页拆分

**What goes wrong:** 某个主题或目标版加入一行岗位名称、照片、联系方式或长项目 bullet 后，第一页出现孤立章节标题，经历条目跨页拆开，第二页以无标题续接，或渲染结果超过两页。反过来，粗暴插入分页会把大量空白推到前页。

**Why it happens:** 内容长度、中文字符宽度、主题参数和是否有照片共同影响流式排版；固定“每节 N 行”估算不能代替最终 PDF 的页面事实。Typst 提供 `pagebreak()`，但手动分页本身并不会保证模块完整或密度合理。

**Consequences:** 简历看起来未完成，关键经历脱离上下文，或违反 1/2 页承诺；不同定向版出现难以复现的视觉回归。

**Prevention:**

- schema 为每段经历定义不可拆分单元：段落标题、公司/学校元数据和至少一条 bullet 必须同页；职业经历/项目条目不得在条目内部拆页。
- 主题只声明可验证的页面预算、照片槽位和模块排序，禁止 Markdown 用空白行、原始 Typst 或自由 `pagebreak()` 操纵版式。
- renderer 先根据可收缩内容策略（去空字段、缩短受控摘要、移入第二页）排版；若仍无法同时满足 1/2 页、最小字号和模块完整性，非零失败，输出诊断到 owned work evidence，不发布 current。
- 以最终 PDF 页数和页面级文本/模块锚点为 gate：单页只能是 1 页；双页必须恰为 2 页，且每页都有有效内容和允许的模块起点。

**Detection:** PDF 页数为 0、超过请求值，或提取的页面文本显示标题在页尾、第二页起始为 bullet/日期而无上级标题；视觉 fixture 显示大片异常留白。

**Phase to handle:** Phase 47（Typst 模板、页面预算与逻辑分页）；Phase 49（PDF 结构与视觉回归验证）。

### Pitfall 2: 为塞入一页静默牺牲中文可读性

**What goes wrong:** renderer 通过把正文字号、行距、列表间距或联系方式无限压缩来满足页数，PDF 技术上正确但招聘者无法舒适阅读。

**Why it happens:** “一页优先”没有可测试下限，主题之间也没有一致排版预算；中文的字形密度与英文简历经验不能直接套用。

**Consequences:** 关键信息难扫描；不同主题的候选人材料形成不公平的阅读质量差异。

**Prevention:**

- 每种主题在 theme contract 中固定 A4 边距、正文字号下限、元数据字号下限、行距下限、最大行长和章节间距范围；将这些作为 renderer 常量，不进入用户 Markdown。
- 建立短/标准/边界三组中文 fixture，分别覆盖长姓名、长单位名、长证书名和长项目 bullet；任何主题必须通过最小字号与页数 gate。
- 内容超预算时，优先要求补充精炼事实或使用 2 页模式；不做自动改写、删减事实或低于下限的缩放。

**Detection:** 从生成的 Typst 或 PDF 可提取样式证据中发现低于主题下限的字体；边界 fixture 只能靠缩放通过；人工 UAT 在常用缩放比例下无法清晰阅读。

**Phase to handle:** Phase 47；Phase 49。

### Pitfall 3: 字体可用性与 PDF 跨机排版漂移

**What goes wrong:** macOS、Linux sandbox、OpenClaw/Hermes 环境安装的中文字体不同，fallback 改变字符宽度，导致换行、页数、粗体或符号表现不同；CI 与用户机器的 PDF 不一致。

**Why it happens:** Typst 会发现系统字体，而跨运行时的系统字体集合并不稳定。官方 CLI 近版还提供禁用系统字体以增强可复现性的能力，说明不能把系统字体当成固定依赖。

**Consequences:** 已验收的一页在另一运行时变两页；缺字、假粗体、联系方式图标变方框，导致定向批量输出不可信。

**Prevention:**

- 主题契约声明首选字体、按脚本可验证的 fallback 顺序及必须覆盖的中文/ASCII/符号字符集；生产 render 使用 skill-owned 或受控安装的字体目录，不依赖“机器上大概有某字体”。
- 记录并在 `doctor`/`verify` 检查 Typst CLI 版本、所选字体文件 hash/路径、主题版本；字体不可用或缺关键字形时失败，不静默换字体。
- 将 PDF 页数、页面尺寸、文本锚点和截图/栅格比较放到至少一个干净 Linux fixture 环境与开发环境运行；不要只 diff `.typ` 源码。

**Detection:** `doctor` 显示字体缺失/替代，跨环境 hash 或页面文本/页数不同，PDF 中出现 tofu 字符、替代字体或换行回归。

**Phase to handle:** Phase 47（受控主题与字体契约）；Phase 49（跨运行时回归、adapter 安装验证）。

### Pitfall 4: 照片与个人信息被复制到不该存在的位置

**What goes wrong:** 原始照片、身份证/完整住址/完整生日、联系方式或隐含个人信息被拷入 `.work`、diagnostic JSON、公开 `history/`、批量 manifest、文件名或日志；无照片版只隐藏 PDF 图像，却仍携带图片和 EXIF。

**Why it happens:** 把“资料收集”与“可投递材料”混为同一目录；history 默认整包归档时忽略了简历的敏感性；照片切换被实现为视觉隐藏而非产物集合变化。

**Consequences:** 隐私泄露、错误投递版本、清理困难；历史目录扩大暴露面。

**Prevention:**

- schema 将 `identity_contact` 与求职内容分层：只允许投递必需字段，明确禁止身份证号、精确住址、完整出生日期、家庭成员、健康等高风险字段进入 final Markdown/Typst/PDF；未知字段必须人工确认。
- `photo_mode` 是强类型的 `with-photo`/`without-photo`；无照片 candidate、current 与 history 均不得包含照片文件、照片引用、缩略图、EXIF 副本或文件名泄露。
- 照片仅可来自受控 `assets/` 相对路径，检测真实文件、扩展名、尺寸、路径 traversal 和可选 EXIF；拒绝 URL、绝对路径、symlink 以及把原始资料目录整体复制进 delivery。
- 默认隐藏诊断不得写入含联系方式、完整源数据或照片路径的 JSON；需要可审计证据时仅存字段存在性、匿名 run ID 和 hash，且证据目录不公开发布。
- 历史归档采取“完整可投递 bundle，但不归档源资料”的边界；变更前显示将归档的精确路径集，并对敏感 assets 实施与 current 同等访问边界。

**Detection:** 发布前扫描文件名、文本和元数据中的受禁字段/绝对路径；无照片 fixture 递归断言没有 image MIME、EXIF、图片 hash 或 Markdown/Typst 引用；history 与 `.work` cleanup fault fixture 也必须通过。

**Phase to handle:** Phase 46（schema、字段分类与照片 contract）；Phase 48（candidate-first 批量发布与历史）；Phase 49（安全/负向验证）。

### Pitfall 5: 将过期或不完整的招聘要求当成当前事实

**What goes wrong:** 针对某单位/岗位的版本依据旧网页、转发截图或未标注日期的描述，却在简历中删改重点、声称“符合要求”或生成不再适用的关键词。

**Why it happens:** 零 token CLI 被误解为可以离线“理解”外部招聘市场；岗位信息缺少来源 URL、抓取/确认时间、有效期、职位 ID 或人工确认状态。

**Consequences:** 定向材料误导求职者，错过硬性条件，批量生成陈旧版本；后续无法解释某关键词为何出现。

**Prevention:**

- 建立独立、可审阅的 `target brief`：单位、岗位、渠道/URL 或本地存档标识、获取日期、截止/有效期（未知则显式 unknown）、硬性条件、偏好条件、人工确认状态；它不是 renderer 自行抓取的事实。
- CLI 定向只消费已标准化 target brief，以确定性字段匹配规则生成“覆盖/缺口/未评估”矩阵；绝不联网抓取、调用 LLM 或从岗位名称臆测要求。
- `--as-of`/target brief 日期为必填发布元数据；超过项目定义有效期或无人工确认的 brief 阻止“定向最终版”，可最多生成标有草稿/待核实的 review Markdown，不能发布 PDF current。
- 每份定向 Markdown 附简短、非营销的 provenance 区块或隐藏证据：target ID、版本、as-of，不复制完整招聘网页或个人源资料。

**Detection:** 缺 URL/存档标识、日期、状态或要求字段时 CLI 非零；过期 fixture 不生成最终 PDF；生成版本中的目标 ID 无法回链到 brief。

**Phase to handle:** Phase 46（target brief/schema）；Phase 48（定向 CLI 与批量输入校验）；Phase 49（时效/溯源负向测试）。

### Pitfall 6: 把资格缺口包装成“已符合”或让它消失

**What goes wrong:** 学历层次、专业、证书、工作年限、地域、年龄或其他硬条件缺失时，定向版悄悄删除相关字段、使用含糊措辞，或把“学习中”写成“持有”。

**Why it happens:** 系统只优化关键词匹配，没有“事实、推断、缺口”三态；自然语言改写和事实校验没有分离。

**Consequences:** 对求职者和招聘方造成误导，损害可信度，且很难发现批量版本把原始事实改坏。

**Prevention:**

- 资格字段要求结构化状态：`verified`、`in-progress`、`not-held`、`unknown`，并保留来源/确认标记；最终模式拒绝 unresolved review marker。
- target matching 只输出事实矩阵：`meets`、`gap`、`unknown`、`not-applicable`，并给出字段级依据；禁止自动把 `gap` 改写为符合、禁止因 target 删除原有事实。
- 产品交付区分“投递简历”和“私有缺口报告”：缺口报告默认仅在 owned evidence 或显式授权的审阅输出中，绝不误混入对外 PDF；若硬性缺口存在，CLI 必须显式返回非零或要求 `--allow-known-gap` 这类人工确认开关后才渲染投递版。
- 将“已获得/通过/持有”设为受控措辞，只能映射 `verified`；`in-progress` 使用明确的预计/正在学习表述。

**Detection:** 用学历、证书与年限三类缺口 fixture 验证：默认不发布，显式确认后 PDF 的事实未被夸大；diff 检查任何定向版不能改写 candidate 的原始资格值。

**Phase to handle:** Phase 46；Phase 48；Phase 49。

### Pitfall 7: “纯 CLI 零 token”边界不清，批处理偷偷依赖 AI 或网络

**What goes wrong:** 资料标准化后，batch 命令仍隐式调用模型、联网查询岗位、依赖交互式 agent 决策，或每个岗位生成不同的不可解释文案。

**Why it happens:** 将可选 AI 资料整理与 deterministic renderer 放在同一命令或同一输入语义里；没有机器可验证的无网络/无模型边界。

**Consequences:** 违反成本和可复现性承诺；离线运行失败；相同输入出现不同结果，也无法做精确 no-op 与历史治理。

**Prevention:**

- 命令分层：可选 `normalize`/review 是 agent 协作步骤；`validate`、`target`、`render`、`batch` 只读取 finalized Markdown/YAML、本地主题和受控 assets。
- renderer/batch 不含 API key、HTTP client、shell 调用 agent、提示词或自动安装逻辑；`--offline` 为默认且不可关闭，`doctor` 明确列出实际二进制和版本。
- 为每个 batch 输入确定 target 列表、稳定排序、theme/photo mode、输出 stem；同样的输入字节和工具版本必须产生同一 candidate path set 与 bytes（PDF metadata 也需固定或排除导致漂移的时间字段）。
- 文档中只承诺“已标准化资料后的零 token”，不承诺从零散材料到最终简历的全流程零 token。

**Detection:** 在无网络、无凭据、无 agent binary 的环境运行 fixture；静态检查脚本不存在网络/API 依赖；重复 batch 的 path set、Markdown、Typst 与 PDF 可重复性证据一致。

**Phase to handle:** Phase 46（工作流边界）；Phase 48（CLI/batch 实现）；Phase 49（离线重复性验证）。

### Pitfall 8: 批量输出交叉污染 current、history 与目标版本

**What goes wrong:** 多单位/多岗位/照片变体共用 stem 或 assets，A 岗位的 PDF 覆盖 B 岗位；部分 batch 失败后已经发布一部分新版本；manifest、原始 brief、日志或临时文件泄漏到交付根；相同 batch 反复创建垃圾 history。

**Why it happens:** 将单文件 render 的成功语义直接套给 batch；输出身份不包含 target/theme/photo mode；未继承 v1.18 candidate-first、exact set、fail-closed 约束。

**Consequences:** 用户拿到错误投递件或敏感资料；历史不可审计；失败破坏已确认交付。

**Prevention:**

- 定义稳定的 delivery identity：`candidate-id + target-id + target-version + theme-id + photo-mode`，由安全 slug 映射到唯一 stem；拒绝重复、空值、path traversal、跨根、symlink 和未知顶层状态。
- batch 先在一个 owned `.work/<run-id>/candidate/` 构造并逐件验证所有 complete triples，再执行计划中的发布；任何 item 失败则整个 batch 不改变任何 current/history。不要声称 SIGKILL、断电或跨路径硬原子，仅保证 handled error/INT/TERM 回滚边界。
- 发布按 complete bundle 进行 exact path-set+bytes 比较：完全一致 no-op，不改 inode/mtime、不建 history；变更才将该 identity 的旧完整 bundle 和受管图片成套归档。`sources/` 永不由普通 render/history 修改。
- 公开根 allowlist 只包含请求的 Markdown/Typst/PDF、按需 `assets/`、`history/` 和运行期 `.work/`；target brief、manifest、匹配矩阵、日志、状态、diff、原图和诊断必须在公开根外或隐藏 evidence。

**Detection:** 两目标、两主题、两照片模式的组合 fixture 验证 8 个唯一输出；中途故障/INT/TERM、重复 no-op、partial legacy group、unknown file、symlink、重复 slug 与单 item 失败均须零错误发布和正确 cleanup。

**Phase to handle:** Phase 48（batch publisher、bundle/history、清理）；Phase 49（故障注入与公开根审计）。

### Pitfall 9: 验证只看 PDF header，漏掉事实、布局和安全回归

**What goes wrong:** `%PDF`、非空文件、甚至 Typst 无错误都通过，但输出的目标错位、第二页断条、无照片版仍有图片、缺口被隐藏、字体 fallback 或一条经历缺失。

**Why it happens:** 将渲染成功当成业务成功；没有分层证据，也没有覆盖最危险的边界 fixture。

**Consequences:** 把不适合投递的简历作为 current 归档和交付，问题只能在用户打开后暴露。

**Prevention:**

- 分层 gate：schema/事实完整性 → target 时效与资格矩阵 → Typst/字体 contract → PDF 文件与页面尺寸/页数 → 页面级文本与模块锚点 → 图片/敏感信息扫描 → 公开目录/历史/cleanup 审计 → 人工视觉 UAT。
- 每个主题、页面模式、photo mode、资格状态、目标状态至少有一个 fixture；专门维护最长中文字段、临界一页/两页、过期 brief、缺硬条件、无照片、缺字形、重复 batch 与故障中断样例。
- 截图或 PDF 栅格对比用于捕捉文本提取看不到的视觉问题，但不能单独取代结构校验；人工 UAT 对 1 页和 2 页各检查可读性、页首/页尾、照片槽位、联系方式与关键经历可扫描性。
- 验证 evidence 只允许写调用方给定且非 delivery root 的 workdir；成功交付不得混入 evidence。

**Detection:** gate 清单缺任一层即验证失败；引入已知恶意/边界 fixture 时必须被对应 gate 拦截，而不是仅产生警告。

**Phase to handle:** Phase 49（验证、回归与六运行时 adapter）。

## Moderate Pitfalls

### 主题契约反向绑定内容 schema

**What goes wrong:** 新主题要求改写资料字段、把照片位置或栏目名称写死在 Markdown，导致主题扩展时重做资料。

**Prevention:** schema 存语义内容与模块优先级；theme 只消费标准字段并负责视觉映射。新增主题先通过同一 fixture 集，再允许加入 registry。

**Phase to handle:** Phase 46、Phase 47。

### 目标关键词污染基础简历

**What goes wrong:** 定向关键词永久写回通用版，或针对一个单位的自述出现在另一个单位的版本。

**Prevention:** 通用 finalized Markdown 不可被 `target` 改写；target transform 输出单独 candidate，保留基准输入 hash 与 target brief ID，且只允许受控字段的可审计选择/排序。

**Phase to handle:** Phase 48。

### 文件名泄露姓名、电话或目标单位全称

**What goes wrong:** 输出 stem、history 路径或日志暴露过多个人信息或岗位信息。

**Prevention:** 使用稳定的 candidate/target slug 或显式安全显示名；禁止把电话、邮箱、身份证或原始 URL 放进文件名；验证扫描文件路径。

**Phase to handle:** Phase 46、Phase 48。

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Phase 46：资料、target brief 与 schema | 混合个人源资料、投递字段、目标事实与资格推断 | 先建立字段分类、review marker、资格四态、target provenance、照片模式与输出身份；未确认/过期数据不可 final render。 |
| Phase 47：主题、Typst 与分页 | 依赖系统字体或用缩放/硬分页掩盖 overflow | 先手工接受 1/2 页参考 surface，再编码主题预算、最小字号、不可拆分模块和受控字体；不满足即失败关闭。 |
| Phase 48：纯 CLI 定向与批量发布 | 隐式模型/网络、同 stem 覆盖、半批发布、history 污染 | 确定性 offline CLI；完整 batch candidate 通过所有 gates 后才 publish；继承 exact-set/no-op/history/rollback/unknown-symlink fail-closed 规则。 |
| Phase 49：验证与 runtime adapter | 把 PDF 存在当作可投递，或只在开发机验收 | 分层负向测试、跨字体环境、页面级锚点和视觉 UAT；OpenClaw/Hermes 安装时验证 whole-folder、Typst、字体、read/write/execute allowlist。 |

## Requirements That Must Be Explicit

| Requirement Gate | Why It Must Be Required |
|------------------|-------------------------|
| 1 页/2 页是精确 PDF 页面数，且有模块完整性规则 | `pagebreak()` 只能换页，不能证明没有孤立标题、拆分经历或空白页。 |
| 主题拥有字号、边距、行距、照片槽位和分页策略 | 防止 Markdown 为挤版式引入主题耦合和不可预测的空白/缩放。 |
| 每次 final render 检查受控字体及版本 | 字体 fallback 会直接改变中文换行、字形和页数。 |
| target brief 有来源标识、as-of、有效性和人工确认状态 | 零 token CLI 应处理已确认事实，不能伪装成实时招聘检索。 |
| 资格匹配为 `meets/gap/unknown/not-applicable`，不得自动美化 | 防止把缺证书、学历或年限写成已符合。 |
| 无照片版的完整产物集合不含照片和元数据 | 视觉隐藏不是隐私保护。 |
| validate/target/render/batch 默认离线、无模型调用 | 兑现已标准化资料后的纯 CLI 零 token 可复现性。 |
| batch 为全体 candidate 验证后再发布 | 防止部分成功污染 current/history。 |
| current、history、assets、sources、work/evidence 有明确边界 | 简历含个人信息，不能让日志、brief 或原始照片混入公开交付。 |
| 验证包含语义、结构、视觉与故障注入 | PDF header/非空只能证明文件存在。 |

## Sources

| Source | Confidence | Findings Used |
|--------|------------|---------------|
| `.planning/PROJECT.md`（2026-07-17） | HIGH | v1.19 的 shared-schema、纯 CLI 零 token、两页逻辑分页、candidate-first/clean-delivery 约束。 |
| Typst official docs, `pagebreak`: https://typst.app/docs/reference/layout/pagebreak/ | HIGH | 手工换页只能强制后续内容进入下一页，不能替代逻辑分页验证。 |
| Typst official docs, counter: https://typst.app/docs/reference/introspection/counter/ | HIGH | 页码在每个 page break 递增，可用于页数/分页语义理解。 |
| Typst 0.12 CLI changelog: https://typst.app/docs/changelog/0.12.0/ | HIGH | CLI 提供禁用系统字体以改善可复现性的能力；字体环境应被当作明确依赖。 |
| 既有 `skills/gongwen/SKILL.md`、`skills/tiaokedan/SKILL.md`、`skills/teaching-design-package/SKILL.md` | HIGH | 已接受的 Markdown-first、candidate-first、exact-set no-op、history、rollback、unknown/symlink fail-closed、隐藏诊断边界。 |

## Open Questions for Phase Planning

- 1 页和 2 页主题各自的正文字号、元数据字号、边距和最大行长具体下限应以哪套中文打印/屏读 UAT 标准定稿？这是 Phase 47 的手工参考 surface 前置决策。
- target brief 的时效窗口是统一固定天数，还是由来源中的截止日期优先、无截止日期时要求每次人工确认？在决定前，保守策略应是无日期即不产出 final targeted PDF。
- 照片模式是否默认无照片，以及“允许照片”应由候选人、投递渠道还是每个 target brief 显式授权？在明确前不应默认复制照片。
- 历史目录在本地离线交付中的访问控制/加密由哪个运行时承担？本技能可保证路径与内容边界，但不能单独承诺操作系统级机密性。
