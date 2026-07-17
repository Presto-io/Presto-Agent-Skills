# Phase 47: 受控主题、照片与冻结布局 - Research

**Researched:** 2026-07-18  
**Domain:** 离线 Python CLI、Typst A4 排版、受控字体、逻辑分页  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** 三种主题只允许是样式差异，不是内容差异。主题之间不得通过增删事实、改变模块语义或切换内容强调逻辑来制造差异。
- **D-02:** 三种主题允许有明显不同的页面构图，不要求“同骨架换皮”。后续实现可在单栏、双栏、信息区比例、装饰强度等方面形成清晰区分。
- **D-03:** 主题家族固定为 `保守稳妥 / 现代简洁 / 个性设计`，作为第一批正式主题边界。
- **D-04:** 主题需要像常见简历模板那样提供风格差异，但仍保持职业感、可打印、可投递，不走海报化路线。
- **D-05:** `graduate-resume.md` 是唯一可编辑事实源；1 页版、2 页版、主题版、照片版都必须从这份源文件派生，不维护独立事实 MD。
- **D-05a:** 事实源采用 v2 混合格式：首页信息栏 `profile`、可选本地 `photo` 路径与派生 `preferences` 位于 YAML frontmatter，教育、技能、证书、项目、实训、经历和目标位于 Markdown 正文；省略 `photo` 即无照片，正文顺序不构成事实语义。
- **D-06:** 用户后续修改资料时，应继续修改唯一事实源并重跑派生流程；如果修改的是页数、主题或照片偏好，则优先通过 frontmatter 偏好字段或 CLI 参数表达，而不是复制内容。
- **D-07:** 新增个性化模块时，默认由 agent 判断其容器归属，但允许用户显式覆盖。
- **D-08:** 页面系统采用两类通用容器承接模块：`fact-block` 用于个人信息、摘要、教育、技能等结构化信息块；`list-entry` 用于项目、实训、经历、证书、竞赛、活动等条目型模块。
- **D-09:** 容器是承载方式，不是抹平模块身份；教育、项目、证书等模块语义仍需保留，不能退化为匿名卡片流。
- **D-10:** 缺失模块直接不渲染，由其余容器自然补位；不保留假空白，不编造内容。
- **D-11:** 布局适配采用“标准模块集合 + 可选模块启用 + 受控顺序 + 自适应补位”，而不是为每个模块预留固定空槽。
- **D-12:** 照片是固定占位区域的可选元素，不是可自由摆放内容。
- **D-13:** 每个主题固定自己的照片位置，主题内不再派生额外的位置变体。
- **D-14:** 无照片时，照片及其装饰元素必须一起消失；只有左侧或上部照片这类会挤占主内容流的主题，正文才需要补齐移动。
- **D-15:** 对右侧、下部或其他对主内容骨架影响较小的照片位，无照片时可以基本保持整体布局不变。
- **D-16:** 照片形态和装饰语言允许由主题决定，例如边框、色块、条形等，但必须保持职业感。
- **D-17:** 照片适配默认优先不裁切、保持比例；必要时允许受控裁切，但默认不强制填满照片区域。
- **D-18:** 自动页数模式不采用“一页优先”或“两页优先”的硬编码，而是按内容量判断最合适页数。
- **D-19:** 自动模式采用三段式判断：`明显更适合 1 页 / 明显更适合 2 页 / 临界区`。
- **D-20:** 内容明显偏少时默认直接生成 1 页；内容明显偏多时默认直接生成 2 页；不为凑 2 页而扩页，也不为压成 1 页而过度收缩。
- **D-21:** 临界区时系统应给出建议页数，并同时生成两种页数版本；主产物采用建议页数，另一种页数版本作为对照产物。
- **D-22:** 自动模式尽量不失败；单页不合适就转双页，只有连双页也超边界时才失败关闭。
- **D-23:** 用户强制 1 页时允许激进压缩，但仍需明确提示更推荐 2 页，并同时产出推荐的 2 页版。
- **D-24:** 用户强制 2 页但内容不足时，应提示更适合 1 页，但仍按要求生成 2 页版。
- **D-25:** 分页的最小完整单元是“单个条目”，不是整个模块。
- **D-26:** 模块整体尽量不拆页；必要时允许模块跨页，但单个条目不可拆。
- **D-27:** `项目 / 实训 / 经历` 按单条严格不可拆处理。
- **D-28:** `证书` 允许整组跨页续下，但同一证书条目内部不可拆。
- **D-29:** `技能` 允许按组续页，但不得出现页尾只挂技能组标题、下一页才出现组内容的阅读障碍。
- **D-30:** `个人信息` 固定为首页首位锚点，不可下沉到中后段；`教育` 尽量保持在前部稳定区域。
- **D-31:** 布局允许做“受限重排”以改善分页和阅读顺序，但不能破坏正常简历阅读习惯，例如不得把个人信息挪到非首位。
- **D-32:** 当分页困难时，优先在允许范围内调整模块顺序，再做密度压缩。
- **D-33:** 系统不应让用户只看到单一主题，避免被首个模板限制选择空间。
- **D-34:** 当前阶段锁定“支持多主题预览”的产品原则，但预览产物格式、发布路径、是否输出 PDF/PNG/HTML 等工程细节延后到 Phase 48/49 再定。

### the agent's Discretion
- 具体三套主题的视觉语言、色彩强度、字体层级、单双栏构图和照片装饰细节由后续研究与实现阶段在上述边界内收敛。
- `fact-block` 与 `list-entry` 的字段映射细节可由 agent 默认判断，但需保留用户覆盖接口。

### Deferred Ideas (OUT OF SCOPE)
- 多主题预览的具体产物形态、路径、命名、是否输出 PDF/PNG/HTML、以及与正式交付的关系，延后到 Phase 48/49 讨论。
- 推荐排序、轻变体数量、是否先做 style pass 再做 final pass 等样式选择交互细节，延后到后续定向渲染与验证阶段细化。
- `⚠ Unpackaged spikes/sketches detected — run /gsd:spike --wrap-up or /gsd:sketch --wrap-up to make findings available.`
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|---|---|---|
| THEME-01 | 三个 YAML 可选主题且不改 schema | 主题注册表、中文别名解析、单一事实模型与主题纯视觉映射。 |
| THEME-02 | 每主题照片/无照片；无照片不留空位 | `resolve_photo_mode` 延展、受控照片槽位、无照片输入/计划/Typst 三层移除。 |
| THEME-03 | 自动或强制 1/2 页 A4，不能截断或有第 3 页 | 冻结计划、两次候选布局、密度阶梯和最终 Typst/PDF 页面数门禁。 |
| THEME-04 | 双页无孤立标题、无无标题续接、条目/职责/成果不拆 | 条目级原子块、页首锚点规则、编译后结构验证、失败关闭错误码。 |
| THEME-05 | 内容不足只重排或使用既有表达，不虚构 | 规划器只消费已验证字段；禁止摘要改写、补空白和主题专有事实。 |
</phase_requirements>

## Summary

本阶段应在现有 Python CLI 内增加一个纯确定性的布局规划层：先把已验证的 `ResumeDocument` 投影为语义容器与不可变 `FrozenResumePlan`，再由 Typst 发射器机械消费计划。[VERIFIED: `skills/graduate-resume/scripts/graduate_resume_cli.py:141-170,400-441`] 这满足“主题不改事实”的锁定边界，并避免流式模板在发射时自行移动条目。[CITED: `.planning/phases/47-controlled-themes-photo-frozen-layout/47-UI-SPEC.md`]

页面是否有效不能只由行数估算决定。规划器须使用冻结的字体、字号、列宽和间距做保守预算，依次尝试合法的 1 页和 2 页计划；Typst 编译后再以精确物理页数、A4 尺寸、页面起点与条目锚点复核。Typst 官方页面 API 支持 A4 页面尺寸和边距，`block` 支持可断页控制，CLI 支持 `--font-path`、`--ignore-system-fonts`、`--creation-timestamp` 与 PNG 多页导出命名。[CITED: https://typst.app/docs/reference/layout/page/] [CITED: https://typst.app/docs/reference/layout/block/] [CITED: https://typst.app/docs/reference/cli/]

**Primary recommendation:** 先交付受控字体 + 三主题注册表 + `FrozenResumePlan`/条目预算与 fixture 门禁，再让 `plan` 输出 Phase 47 计划摘要；本阶段不发布正式 Markdown/Typst/PDF bundle，也不实现 batch/history/跨 runtime 验收。[VERIFIED: `.planning/ROADMAP.md` Phase 47-49 边界]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|---|---|---|---|
| YAML 偏好、事实解析与校验 | API / Backend（本地 Python CLI） | — | 现有 CLI 在本地加载、解析并校验 Markdown/YAML。 [VERIFIED: `skills/graduate-resume/scripts/graduate_resume_cli.py:141-170,400-441`] |
| 主题选择和主题几何 | API / Backend（本地 Python CLI） | 静态模板 | 主题 key、色彩、字体和槽位是 renderer-owned 派生值。 [CITED: `47-UI-SPEC.md`] |
| 照片安全解析与模式决议 | API / Backend（本地 Python CLI） | 静态资源 | 照片必须是本地已提供路径；布局只接收已决议模式。 [VERIFIED: `graduate_resume_cli.py:371-385,501-509`] |
| 分页、重排、不可拆条目 | API / Backend（布局规划器） | Typst | 语义分页必须在发射前冻结，Typst 不得改写计划。 [CITED: `47-UI-SPEC.md`] |
| A4 PDF 版面发射 | 静态 / Typst | 本地 CLI | Typst 消费固定页面、字体和容器预算。 [CITED: https://typst.app/docs/reference/layout/page/] |
| PDF 结构与视觉验收 | API / Backend（本地 CLI） | Typst/PDF 工具 | Phase 47 建立布局 fixture；全量聚合与跨环境验收属于 Phase 49。 [VERIFIED: `.planning/ROADMAP.md` Phase 47/49 success criteria] |

## Project Constraints (from AGENTS.md)

- 文档与模板保持简洁、可复制、可审阅。 [VERIFIED: `AGENTS.md`]
- canonical `SKILL.md` 不得包含某个 runtime 的私有语法；runtime 差异只能位于 adapter notes。 [VERIFIED: `AGENTS.md`]
- 复杂背景材料放 `references/`，脚本放 `scripts/`，模板放 `templates/`。 [VERIFIED: `AGENTS.md`]
- 外部命令、网络、凭据或文件写入必须声明安全边界和验证步骤。 [VERIFIED: `AGENTS.md`]
- OpenClaw 与 Hermes Agent 必须被考虑；本阶段只保留可移植 CLI/文件结构，安装验证留给 Phase 49。 [VERIFIED: `AGENTS.md`; VERIFIED: `.planning/ROADMAP.md`]

## Standard Stack

### Core

| Component | Version | Purpose | Why Standard |
|---|---:|---|---|
| Python | 3.14.6 | 扩展现有离线 CLI、解析、冻结计划与 fixture runner | 仓库已有单文件 Python CLI，使用 `dataclass`、JSON 和 PyYAML。 [VERIFIED: `graduate_resume_cli.py`; VERIFIED: local `python3 --version`] |
| PyYAML | 6.0.3 | YAML frontmatter 解析 | 已被现有 CLI 直接导入，非本阶段新增依赖。 [VERIFIED: `graduate_resume_cli.py:14`; VERIFIED: local Phase 46 `verify`] |
| Typst | **0.15.0**（本阶段锁定） | 受控 A4 Typst/PDF/PNG 发射 | 本机可用版本为 0.15.0；其 CLI 明确支持隔离字体目录与固定创建时间。 [VERIFIED: local `typst --version`; VERIFIED: local `typst compile --help`] |
| Source Han Sans SC Regular 400 + Semibold 600 | 精确文件 SHA-256，而非浮动名称 | 中文/ASCII 的唯一生产字体 | UI 契约锁定该字族和两个字重；字体清单哈希进入冻结计划。 [CITED: `47-UI-SPEC.md`] |

### Supporting

| Component | Purpose | When to Use |
|---|---|---|
| `typst compile --font-path … --ignore-system-fonts --creation-timestamp 0` | 仅搜索 skill-local 字体并使可重复构建元数据稳定 | 所有 Phase 47 layout fixture 编译。 [VERIFIED: local `typst compile --help`] |
| `typst compile … page-{0p}-of-{t}.png` | 为每个物理页导出可人工检查的 PNG | 主题/照片/压力 fixture 的视觉门禁；正式预览发布仍延后。 [VERIFIED: local `typst compile --help`] |
| `pdfinfo` | 读取 PDF 物理页数与页面尺寸 | 当前环境已有可执行文件；在 fixture 验证中作结构证据。 [VERIFIED: local `command -v pdfinfo`] |

**Installation:** 本阶段不建议通过 npm/pip 安装新包；字体以已审阅、带许可证和 SHA-256 清单的 skill-local 文件加入版本库或明确的受控输入提供。[ASSUMED]

## Architecture Patterns

### System Architecture Diagram

```text
graduate-resume.md
        |
        v
现有 load_resume + validate_document
        |
        +--> 主题别名/偏好决议 ----> ThemeSpec（只含视觉与几何）
        |
        +--> 照片路径安全检查 ----> photo / no-photo
        |
        v
语义容器投影（保留 section、fact id、字段）
        |
        v
FrozenResumePlan 建模与分页
  | 1 页候选 | 2 页候选 | 强制页数/临界对照 |
        |
        +-- 不可满足 --> LAYOUT_UNSATISFIABLE（不发射、不发布）
        v
仅消费计划的 Typst 发射器
        |
        v
受控 Typst compile（固定版本/字体/时间）
        |
        v
结构门禁：A4、精确页数、页首锚点、条目完整、无第三页
```

### Recommended Project Structure

```text
skills/graduate-resume/
├── fonts/                              # Source Han Sans SC 两个受控字体 + manifest
├── fixtures/
│   ├── layout/                         # 短、标准、临界、压力、长字段、有/无照片资料
│   └── media/                          # 仅 fixture 可用、受控的本地测试照片
├── scripts/
│   ├── graduate_resume_cli.py          # CLI 参数、稳定错误码、plan/verify 入口
│   ├── graduate_resume_layout.py       # FrozenResumePlan、预算、分页、验证
│   └── graduate_resume_typst.py        # 纯计划 -> Typst 发射
└── templates/
    └── resume-themes.typ               # 主题 token、容器与照片槽位宏
```

### Pattern 1: 不可变计划先行

**What:** 使用 `@dataclass(frozen=True)` 的计划对象，并把 `theme`、`page_count`、`photo_mode`、字体清单哈希、页/栏/容器、`entry_budget`、重排理由和建议页数全部序列化为可审阅 JSON。发射器的输入只能是该计划与已验证事实视图。[CITED: `47-UI-SPEC.md`]

**When to use:** 每次 `plan`、布局 fixture 和后续 Phase 48 的 render 都必须先创建计划；禁止在 Typst 模板内根据剩余空间做语义重排。[CITED: `47-UI-SPEC.md`]

```python
@dataclass(frozen=True)
class FrozenResumePlan:
    theme: str
    page_count: int
    photo_mode: str
    font_manifest_hash: str
    pages: tuple[PagePlan, ...]
    containers: tuple[ContainerPlan, ...]
    recommendation: PageRecommendation

def emit_typst(plan: FrozenResumePlan, facts: ResumeFacts) -> str:
    # 不重新排序、不重新测量、不插入事实；违规即抛稳定错误码。
    return render_from_plan(plan, facts)
```

该数据模型是实现建议，尚未在仓库中存在；行高预算必须在最终 PDF 门禁前保守估计。[ASSUMED]

### Pattern 2: 条目原子化 + 模块可续接

**What:** `projects`、`training`、`experience`、单张证书和技能组都先转成含模块标题、标题、元数据、摘要、职责/成果的原子单位；每个单位以不可断页 Typst block 发射。模块可在两个原子单位之间续页，续页首必须重新带模块标题或合法的“续”标题。[CITED: `47-UI-SPEC.md`] Typst 的 block API 有 `breakable` 控制，适合承载该物理不可拆要求。[CITED: https://typst.app/docs/reference/layout/block/]

**When to use:** 任何两页候选；教育、个人信息和照片身份区为首屏锚点，不能通过普通排序器移动到后页。[CITED: `47-UI-SPEC.md`]

### Pattern 3: 三段式页数选择，不以缩字求通过

**What:** 在同一 `ThemeSpec` 下先求常规密度的 1 页、2 页候选；合法 1 页且占用低于“临界下界”时推荐 1 页，1 页非法或明显超预算时推荐 2 页，二者均合法且接近边界时标记临界并生成两份计划。强制模式仍编制推荐页数的对照计划。[CITED: `47-CONTEXT.md` D-18 至 D-24]

**How:** 密度阶梯只能是：跳过空字段 -> 允许的模块重排 -> 在 UI-SPEC 下限内降低模块/条目间距；禁止改写事实、删事实、增加字号/字距技巧或低于 9pt/规定行距。[CITED: `47-UI-SPEC.md`]

### Pattern 4: 主题注册表是纯数据

**What:** 用稳定内部 key `conservative`、`modern`、`expressive` 映射中文 YAML 值；每个 `ThemeSpec` 固定 A4 安全边距、栏比例、色板、四级字号、间距 token、照片槽位和允许的无照片补位策略，不保存候选人内容。[CITED: `47-UI-SPEC.md`]

**When to use:** 新主题加入前，必须使用同一 layout fixture 矩阵通过；主题不得影响模块语义、事实集合和目标强调逻辑。[CITED: `47-CONTEXT.md` D-01 至 D-04]

### Anti-Patterns to Avoid

- **在 Markdown 写原始 Typst、空行或手工 pagebreak：** 将版式反向写入事实源，破坏唯一事实源和主题无关性。 [CITED: `schema-and-review-contract.md`; CITED: `.planning/research/PITFALLS.md`]
- **仅靠 `pagebreak()` 修复分页：** 它只强制后续内容进入下一页，不能证明条目完整或页面有效。 [CITED: https://typst.app/docs/reference/layout/pagebreak/]
- **让 Typst 流式布局决定语义分页：** 编译成功仍可能产生孤立标题、无标题续接和第三页。 [CITED: `.planning/research/PITFALLS.md`]
- **照片仅在 PDF 中隐藏：** 无照片模式还必须清除计划、Typst 输入、缩略图、EXIF 与路径引用。 [CITED: `47-UI-SPEC.md`; CITED: `.planning/research/PITFALLS.md`]
- **依赖系统字体：** 系统字体差异会改变中文换行和页数；生产编译必须忽略系统字体。 [VERIFIED: local `typst compile --help`; CITED: `.planning/research/PITFALLS.md`]

## Existing Extension Points And Gaps

| Surface | Reuse / required change | Evidence |
|---|---|---|
| `preferences.theme`, `preferred_pages`, `photo_mode` | 已允许字段且 `plan` 已回显；增加主题别名决议、页数策略和 CLI 参数覆盖，但不得改 schema。 | [VERIFIED: `graduate_resume_cli.py:62-74,388-397,512-535`] |
| `resolve_photo_mode()` | 已能从资料和偏好决议 `photo`/`no-photo`；补齐显式 `photo` 且缺本地可读文件时的失败关闭。 | [VERIFIED: `graduate_resume_cli.py:371-385,501-509`] |
| `plan` 命令 | 当前仅输出 `phase: 46` baseline JSON；Phase 47 应替换/扩展为 FrozenResumePlan 摘要与稳定诊断。 | [VERIFIED: `graduate_resume_cli.py:512-536`] |
| `render` / `batch` | 当前明确返回 `NOT_IMPLEMENTED`；不要在 Phase 47 实现 Phase 48 的候选发布、三件套、history 或 batch 事务。 | [VERIFIED: `graduate_resume_cli.py:539-543,575-587`; VERIFIED: `.planning/ROADMAP.md`] |
| 现有 fixture | 有照片、无照片、通用、多目标和 6 类 schema 负例均可复用为基础；缺少布局压力、长字段、精确页数、实际图片、字体缺失与分页负例。 | [VERIFIED: `graduate_resume_cli.py:76-89`; VERIFIED: `skills/graduate-resume/fixtures/`] |
| 照片真实路径校验 | 当前只拒绝 URL，并未检查文件存在、相对根、symlink、MIME/可解码性；这是与 UI “已通过本地路径校验”前提的实际缺口。 | [VERIFIED: `graduate_resume_cli.py:371-385`; CITED: `47-UI-SPEC.md`] |
| 字体资产 | `skills/graduate-resume/fonts/` 当前不存在；以 `--ignore-system-fonts` 列举时只显示 Typst 内嵌拉丁字体，不能满足锁定的 Source Han Sans SC。 | [VERIFIED: local `find skills/graduate-resume …`; VERIFIED: local `typst fonts --font-path skills/graduate-resume/fonts --ignore-system-fonts`] |

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| PDF 排版引擎 | Python 手写 PDF 坐标排版 | Typst 固定版本 | A4、列、字体嵌入和 PDF 输出由成熟排版器处理。 [CITED: https://typst.app/docs/reference/layout/page/] |
| 图像拉伸/裁切算法 | 自定义像素处理或自动修图 | Typst 图像等比放置；受控槽位内仅允许显式裁切 | 照片契约要求不拉伸、不远程下载、不自动修图。 [CITED: `47-UI-SPEC.md`] |
| 字体发现 | 遍历或猜测系统字体 | `--font-path` + `--ignore-system-fonts` + manifest hash | CLI 已支持显式字体目录，能避免机器差异。 [VERIFIED: local `typst compile --help`] |
| 事实/主题合并 | 按主题维护三套 Markdown | 单一解析事实模型 + ThemeSpec | 三主题不得改变事实集合或模块语义。 [CITED: `47-CONTEXT.md` D-01, D-05]

**Key insight:** 自定义的部分应只限于“简历语义到冻结计划”的业务规则；排版、字体检索和 PDF 生成不应重造。[ASSUMED]

## Common Pitfalls

### Pitfall 1: 预估通过、最终 Typst 多出第 3 页
**What goes wrong:** 长中文名称、照片槽位或一条成果换行改变流式高度，令 PDF 不再符合计划。[CITED: `.planning/research/PITFALLS.md`]

**How to avoid:** 预算器只产生候选；受控 Typst 编译后的物理页数、A4 页面尺寸、条目 ID 与页首锚点是最终 gate。若与计划不一致，返回 `LAYOUT_RENDER_MISMATCH`，不将其视作可发布结果。[ASSUMED]

### Pitfall 2: 单页靠缩字“成功”
**How to avoid:** 把 9pt metadata、10.5pt body、14pt heading、22pt name 及对应行距设为 ThemeSpec 不变量；压缩只能走锁定密度阶梯。[CITED: `47-UI-SPEC.md`]

### Pitfall 3: 容器拆分丢失模块身份
**How to avoid:** 每个 `ContainerPlan` 同时记录 `kind` 与原始 `section`/`fact_id`；跨页续接前重新发射语义模块标题，禁止第二页以日期、bullet 或成果开头。[CITED: `47-UI-SPEC.md`]

### Pitfall 4: 无照片变体仍泄露照片引用
**How to avoid:** `no-photo` 分支在计划创建前就把照片字段排除；测试同时扫描计划 JSON、`.typ` 文本、PDF 依赖清单与 PNG 目录，不能只看视觉空位。[CITED: `47-UI-SPEC.md`; CITED: `.planning/research/PITFALLS.md`]

### Pitfall 5: 把 Phase 47 的布局证据混入 Phase 48 交付根
**How to avoid:** Phase 47 fixture 输出仅写调用方指定的临时 workdir；正式命名 Markdown/Typst/PDF 三件套、candidate-first、history/no-op/rollback 由 Phase 48 负责。[VERIFIED: `.planning/ROADMAP.md` Phase 47-49]

## State of the Art

| Old Approach | Current Approach | Impact |
|---|---|---|
| 依赖机器系统字体 | 显式 `--font-path` 加 `--ignore-system-fonts` | 字体来源能被锁定与验证，避免系统发现造成排版漂移。 [VERIFIED: local `typst compile --help`] |
| 编译后只看 PDF 是否存在 | 计划前冻结 + 编译后页数/锚点门禁 | “能生成”不等于“不截断且逻辑完整”。 [CITED: `.planning/research/PITFALLS.md`] |
| 主题复制内容 | 单一事实源 + 纯视觉 ThemeSpec | 三个主题可以有构图差异而不制造事实漂移。 [CITED: `47-CONTEXT.md` D-01, D-05]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---:|---|---|
| Python | CLI/布局规划器 | ✓ | 3.14.6 | — [VERIFIED: local `python3 --version`] |
| PyYAML | 现有 frontmatter 解析 | ✓ | 6.0.3 | — [VERIFIED: Phase 46 `verify`] |
| Typst | A4 Typst/PDF/PNG fixture 编译 | ✓ | 0.15.0 | —；本阶段锁定此版本 [VERIFIED: local `typst --version`] |
| `pdfinfo` | PDF 页数/尺寸 gate | ✓ | 路径可用 | 可由 Python PDF 解析器在后续阶段提供，但本阶段优先使用现有工具。 [VERIFIED: local `command -v pdfinfo`; ASSUMED] |
| Source Han Sans SC 400/600 | 生产布局与中文换行测量 | ✗ | — | 无安全 fallback；须先加入/提供受控字体并验证哈希。 [VERIFIED: local font inventory; CITED: `47-UI-SPEC.md`] |
| 有效 fixture 测试照片 | 照片版布局与无照片移除测试 | ✗ | — | 无；须提供非敏感、可版本控制的 fixture 图片。 [VERIFIED: `skills/graduate-resume/fixtures/` file inventory; VERIFIED: `valid-photo-single-target.md`] |

**Missing dependencies with no fallback:** 受控 Source Han Sans SC 两字重、可解析的 fixture 照片。它们是 Phase 47 实际 Typst 布局/照片测试的前置阻断项。[VERIFIED: local font/fixture inventory]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | 本地离线 CLI 不提供身份认证面。 [VERIFIED: `graduate_resume_cli.py`; ASSUMED] |
| V3 Session Management | no | 本地离线 CLI 不创建会话。 [VERIFIED: `graduate_resume_cli.py`; ASSUMED] |
| V4 Access Control | yes | 限制照片为受控输入根内的常规文件，拒绝绝对路径、父级逃逸和 symlink；此部分尚待实现。 [CITED: `.planning/research/PITFALLS.md`; ASSUMED] |
| V5 Input Validation | yes | 复用受限 schema 校验，并新增主题值、页数、照片路径/类型和容器覆盖白名单。 [VERIFIED: `graduate_resume_cli.py:297-441`; ASSUMED] |
| V6 Cryptography | no | 本阶段只计算完整性 hash，不自定义加密。 [ASSUMED] |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| 照片路径 traversal 或 symlink 读取 | Information Disclosure | 以资料根为基准 `resolve()`，拒绝逃逸、symlink、非普通文件与远程 URL；不在错误/计划中回显绝对路径。 [CITED: `.planning/research/PITFALLS.md`; ASSUMED] |
| 无照片版残留原图、EXIF 或路径 | Information Disclosure | 从布局计划、Typst、预览和任何中间可投递产物共同排除，并做递归负向扫描。 [CITED: `47-UI-SPEC.md`] |
| 超长文本造成排版耗尽/截断 | Denial of Service / Tampering | 限定解析字段与预算；2 页仍不满足即 `LAYOUT_UNSATISFIABLE`。 [VERIFIED: `graduate_resume_cli.py:291-441`; ASSUMED] |

## Planned File-Level Work

| File | Phase 47 responsibility |
|---|---|
| `skills/graduate-resume/scripts/graduate_resume_cli.py` | 增加主题/页数/照片 CLI 决议，升级 `plan`/`verify` 的 Phase 47 摘要和稳定失败码；保留 `render`/`batch` 的 Phase 48 发布边界。 [VERIFIED: current command surface] |
| `skills/graduate-resume/scripts/graduate_resume_layout.py` | 新建纯布局模块，承载 ThemeSpec、FrozenResumePlan、容器投影、预算、三段式页数决议、条目不可拆与计划验证。 [ASSUMED] |
| `skills/graduate-resume/scripts/graduate_resume_typst.py` | 新建只消费冻结计划的 Typst 文本发射器，并拒绝未冻结或不完整计划。 [ASSUMED] |
| `skills/graduate-resume/templates/resume-themes.typ` | 新建三主题的 A4 token、栏位、`block(breakable: false)` 条目宏与受控照片槽位；不含候选人事实。 [CITED: https://typst.app/docs/reference/layout/block/; ASSUMED] |
| `skills/graduate-resume/fonts/*` 与 `fonts/manifest.json` | 加入两个审阅后的字体文件、许可证/来源记录与 SHA-256 清单。 [CITED: `47-UI-SPEC.md`; ASSUMED] |
| `skills/graduate-resume/fixtures/layout/*` 与 `fixtures/media/*` | 新建短、标准、临界、压力、长字段、有/无照片以及失败关闭 fixture；照片为可公开的测试资产。 [CITED: `47-UI-SPEC.md`; ASSUMED] |
| `skills/graduate-resume/SKILL.md`、`references/phase-46-baseline.md` | 仅补充 Phase 47 的 layout plan、受控字体、验证命令与未实现发布边界；canonical 主体不得写 runtime 私有指令。 [VERIFIED: `AGENTS.md`; VERIFIED: `SKILL.md`] |

## Validation Evidence And Commands

Phase 配置显式关闭 `workflow.nyquist_validation`，因此不单列 Nyquist Validation Architecture；仍必须在计划中加入以下直接可执行的 fixture 验收。[VERIFIED: `.planning/config.json`]

```bash
# 保留 Phase 46 schema 基线，必须全绿。
skills/graduate-resume/scripts/graduate-resume.sh verify

# 逐个布局 fixture 生成可审阅冻结计划；实现后应非零失败关闭。
skills/graduate-resume/scripts/graduate-resume.sh plan --input <fixture.md>

# 固定字体和时间的 Typst 编译模式；仅在受控 workdir 中生成证据。
typst compile --font-path skills/graduate-resume/fonts --ignore-system-fonts \
  --creation-timestamp 0 <plan.typ> <workdir>/resume.pdf
pdfinfo <workdir>/resume.pdf
```

| Fixture / case | Required evidence | Requirement |
|---|---|---|
| 每个主题 x 有照片/无照片 | 主题 key、照片 mode、A4、1/2 页、照片槽位或完全移除 | THEME-01, THEME-02 |
| 短资料/内容不足 | 推荐 1 页或按强制 2 页，未添加事实、未制造假空白 | THEME-03, THEME-05 |
| 临界资料 | 主建议计划 + 另一页数对照计划，均有解释 | THEME-03 |
| 长姓名/机构/证书/成果压力资料 | 仅 1 或 2 页；不可拆条目和字号下限不破 | THEME-03, THEME-04 |
| 单页无法合法放入的资料 | 自动转 2 页；强制 1 页给出推荐 2 页对照或稳定失败 | THEME-03, THEME-04 |
| 两页仍无法容纳的资料 | `LAYOUT_UNSATISFIABLE`、原因摘要，未发射正式结果 | THEME-04 |
| 无照片负例 | 计划/Typst/依赖/产物文本中无图片路径、图片或 EXIF | THEME-02 |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | 用保守高度预算先建计划、再用最终 PDF 门禁闭环足以稳定当前简历字段。 | Architecture Patterns | 需要加入更精确的 Typst 测量或迭代策略。 |
| A2 | `graduate_resume_layout.py` 和 `graduate_resume_typst.py` 是比继续膨胀单文件 CLI 更清晰的本地结构。 | Planned File-Level Work | 实现计划可能改为同文件私有模块。 |
| A3 | `pdfinfo` 可作为当前机器的 PDF 元数据检查工具。 | Environment Availability | CI/其他 runtime 需在 Phase 49 选择替代验证器。 |
| A4 | 字体以许可证、哈希受控文件入库或显式提供的方式交付可行。 | Standard Stack | 字体体积/许可证可能要求不同的受控分发策略。 |

## Open Questions

1. **如何取得并审阅两个 Source Han Sans SC 字重？**
   - What we know: UI 契约要求该字体，当前 skill-local 字体目录和可用 fixture 媒体都不存在。 [VERIFIED: local inventory; CITED: `47-UI-SPEC.md`]
   - Recommendation: 将“字体文件、许可证/来源、SHA-256 manifest、`typst fonts --ignore-system-fonts` 检查”作为 47-01 的硬前置；未满足时布局命令失败。 [ASSUMED]

2. **临界区的定量阈值如何落地？**
   - What we know: 上游锁定了三段式策略和字号/间距边界，但没有指定“明显”的数值。 [CITED: `47-CONTEXT.md`; CITED: `47-UI-SPEC.md`]
   - Recommendation: 把阈值设为 ThemeSpec 的命名常量并由临界 fixture 校准；计划、日志和测试都断言该常量，而不是在模板里隐式猜测。 [ASSUMED]

3. **照片的真实文件验证应补到何处？**
   - What we know: Phase 46 的 `validate_photo` 不检查存在性或路径边界，虽然 Phase 47 UI 契约要求已通过本地路径校验。 [VERIFIED: `graduate_resume_cli.py:371-385`; CITED: `47-UI-SPEC.md`]
   - Recommendation: 在 Phase 47 的照片决议入口补强，保持 Phase 46 schema 不变；把隐私发布/root 管理留在 Phase 48。 [ASSUMED]

## Sources

### Primary (HIGH confidence)
- `47-CONTEXT.md` - 锁定主题、照片、页数、容器、分页和阶段边界。
- `47-UI-SPEC.md` - A4 几何、字体、主题 inventory、冻结计划字段、照片与验收契约。
- `.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md` - THEME-01..05 和 Phase 47/48/49 职责划分。
- `skills/graduate-resume/scripts/graduate_resume_cli.py` - 现有命令、schema、照片模式与 fixture 基线的直接实现证据。
- Typst official documentation: https://typst.app/docs/reference/layout/page/ 、https://typst.app/docs/reference/layout/block/ 、https://typst.app/docs/reference/layout/pagebreak/ 、https://typst.app/docs/reference/cli/ - 页面、不可拆 block、手工分页与 CLI 字体隔离能力。

### Secondary (MEDIUM confidence)
- `.planning/research/PITFALLS.md` - 本项目已经识别的分页、中文可读性、字体漂移、照片隐私与分层验证风险。

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - 当前 Typst/Python/PyYAML 实测，字体缺失已明确记录。
- Architecture: HIGH - 上游 UI/Context 冻结了计划先行、主题/分页与照片规则；具体模块拆分为 ASSUMED。
- Pitfalls: HIGH - 项目风险研究与当前代码缺口相互印证。

**Research date:** 2026-07-18  
**Valid until:** 2026-08-17（Typst 版本与字体资产发生变化时立即重做）

## RESEARCH COMPLETE

**Phase:** 47 - 受控主题、照片与冻结布局  
**Confidence:** HIGH

- 现有 CLI 可复用 schema、偏好和照片模式入口，但尚无真实布局或渲染实现。 [VERIFIED: `graduate_resume_cli.py`]
- `FrozenResumePlan` 必须在 Typst 发射前完成；条目原子化、A4/页数/锚点编译后门禁共同满足 THEME-03/04。 [CITED: `47-UI-SPEC.md`]
- 三主题应登记为纯 ThemeSpec，照片/无照片为主题内唯一固定槽位变体，且不改变事实集合。 [CITED: `47-CONTEXT.md`; CITED: `47-UI-SPEC.md`]
- 受控 Source Han Sans SC 与有效 fixture 照片当前缺失，是实际实施的首要阻断项。 [VERIFIED: local inventory]
- Phase 47 只建立布局、字体、fixture 和计划证据；正式三件套/批量发布属 Phase 48，聚合/跨 runtime 验收属 Phase 49。 [VERIFIED: `.planning/ROADMAP.md`]

**File created:** `.planning/phases/47-controlled-themes-photo-frozen-layout/47-RESEARCH.md`
