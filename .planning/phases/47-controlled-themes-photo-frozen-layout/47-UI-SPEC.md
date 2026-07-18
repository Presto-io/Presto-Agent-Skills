---
phase: 47
slug: controlled-themes-photo-frozen-layout
status: draft
shadcn_initialized: false
preset: none
created: 2026-07-18
---

# Phase 47 — UI Design Contract

> 面向 `graduate-resume` 的打印型 A4 简历视觉与交互契约。主题、照片、分页和密度由 renderer 拥有；`graduate-resume.md` 只保留已核实事实与派生偏好。

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none；使用受控 Typst 页面主题，不引入网页组件系统 |
| Preset | not applicable |
| Component library | none |
| Icon library | none；不得以图标替代电话、邮箱、城市等必须可复制和可检索的文字 |
| Font | skill-local、版本锁定的 `Source Han Sans SC`；Regular 400 与 Semibold 600 两个字重。未找到或缺少所需字形时失败，不回退系统字体 |
| Render environment | 固定 Typst 版本，生产渲染使用受控字体目录和 `--ignore-system-fonts` |
| Source of truth | `graduate-resume.md`；主题、页数、照片模式、容器与分页均为派生值，禁止回写事实 Markdown |

本阶段不是 React/Next.js/Vite 工程，未发现 `components.json`、Tailwind、网页组件或前端样式文件；shadcn 初始化和第三方 registry 均不适用。

## Visual Principles

- 三个主题只改变页面构图、色彩、分隔方式和照片装饰，不改变事实集合、模块语义、条目顺序规则或定向强调逻辑。
- 输出始终为可打印、可投递的 A4 简历：白底、高对比、无海报式大色块、无渐变、无装饰性背景图、无圆角卡片流。
- 个人信息是首页首位锚点；教育保持在前部稳定区域。缺失模块不渲染，也不留下标题、槽位或假空白。
- `fact-block` 承载个人信息、摘要、教育、技能等结构化模块；`list-entry` 承载项目、实训、经历、证书、竞赛、活动等可重复条目。两者都必须保留原模块标题和条目身份。

## Theme Inventory

| Theme key / 名称 | 页面骨架 | 照片固定槽位 | 无照片行为 | 视觉语言 |
|-----------------|----------|--------------|------------|----------|
| `conservative` / 保守稳妥 | 单栏正文；顶部信息栏，下接全宽模块流 | 首页右上角姓名信息栏内，32 mm x 42 mm | 照片、细边框和相邻预留宽度一起移除；信息栏文字扩展至全宽 | 深蓝标题、细水平分隔线、最低装饰强度；适合正式投递 |
| `modern` / 现代简洁 | 左侧 31% 信息/技能栏，右侧 69% 教育与条目主栏 | 左栏顶部，28 mm x 36 mm | 左栏顶部内容上移并填补照片高度；主栏比例和阅读顺序不变 | 石墨文字、青绿色强调线、清晰栅格与留白 |
| `expressive` / 个性设计 | 顶部横向身份区；下方 38% 摘要/技能辅栏与 62% 条目主栏 | 顶部身份区右端，30 mm x 40 mm | 照片及对应强调条消失；姓名和联系信息占用完整横向身份区 | 墨绿标题、暖金小面积强调、模块首字母式细节；不得形成海报或插画风格 |

主题 key 为渲染器内部稳定值；YAML 可继续接受当前中文主题值并在解析时确定映射。首批三种主题必须完整可见和可选，但 ThemeRegistry 可在后续增加主题，不得改写 `graduate-resume/v2` 事实 schema。每个主题只有上述一个照片位置，禁止用户指定坐标、色值、字体或照片变体。
所有照片槽位均不得超过标准 2 寸照片的 `35 mm x 49 mm` 上限。

## Page Geometry And Density

| Item | Contract |
|------|----------|
| Page | A4 210 mm x 297 mm；只允许精确 1 页或精确 2 页 |
| Safe margins | 上 14 mm、下 14 mm、左 15 mm、右 15 mm；任何主题不得突破该安全区 |
| Columns | 双栏主题栏间距固定 6 mm；文字不得跨栏、压入照片槽位或溢出安全区 |
| Text measure | 正文主栏最大 32 个中文全角字符或等价宽度；左/辅栏最大 15 个中文全角字符或等价宽度。超出时在词/短语边界换行，不缩小字号 |
| Item gap | 同一 `list-entry` 内使用 `xs`；相邻条目使用 `sm`；模块间使用 `md`。空字段不占间距 |
| Density ladder | 常规密度先排版；分页困难时只允许依次：省略空字段、受限模块重排、在下表下限内压缩模块间距/条目间距。不得删减或改写事实，不得低于字号和行距下限 |
| Content shortage | 只可通过已有事实的自然重排、主题既定密度和已有摘要表达补位；不得虚构、添加装饰占位或为了凑两页扩大无意义空白 |

## Spacing Scale

声明值均为 4 的倍数。Typst 实现约定：内容间距只引用下列 token，并统一按 `1 px = 25.4 / 96 mm` 换算为物理长度（`xs = 1.058 mm`、`sm = 2.117 mm`、`md = 4.233 mm`、`lg = 6.350 mm`、`xl = 8.467 mm`、`2xl = 12.700 mm`、`3xl = 16.933 mm`）；不得为内容间距另行声明毫米值。

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | 标签与元数据内联间距、细分隔元素 |
| sm | 8px | 同一字段组、紧凑条目内间距 |
| md | 16px | 默认 `fact-block` 内边距与模块内容间距 |
| lg | 24px | 主栏/侧栏分组间距 |
| xl | 32px | 顶部身份区和主要模块组的视觉间距 |
| 2xl | 48px | 仅用于未放照片的顶部身份区，不用于正文空白填充 |
| 3xl | 64px | 不在单页正文使用；保留给样张或多主题预览画布 |

Exceptions: 只有印刷安全边距、栏间距、照片槽位和条目防拆测量可使用毫米/pt；它们是冻结几何，不是可配置间距。

## Typography

仅允许以下四个字号与两种字重。主题可以改变它们的色彩和位置，不能增加字号、字重或以缩放规避分页。

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Metadata | 9pt | 400 | 1.35 |
| Body | 10.5pt | 400 | 1.45 |
| Heading | 14pt | 600 | 1.20 |
| Display (candidate name) | 22pt | 600 | 1.10 |

标题之后必须紧跟至少一行所属内容；技能组标题必须与至少一项技能同页。正文、成果、职责和日期不能用小于 9pt 的脚注或压缩字距呈现。所有文本字距为 0。

## Color

每个主题遵守 60/30/10 的页面视觉占比：60% 主表面为白色和正文背景，30% 次表面为淡色信息区、细分隔或栏背景，10% 强调色仅用于下列指定元素。文本对比度保持适合黑白打印；强调色不能承担唯一信息表达。

| Theme | Dominant (60%) | Secondary (30%) | Accent (10%) | Destructive |
|-------|----------------|-----------------|--------------|-------------|
| 保守稳妥 | `#FFFFFF` | `#F2F4F7` | `#1F4E79` | `#B42318` |
| 现代简洁 | `#FFFFFF` | `#EFF5F4` | `#0F766E` | `#B42318` |
| 个性设计 | `#FFFEFA` | `#F3F1EA` | `#8A6A20` | `#B42318` |

Accent reserved for: 模块标题短线、姓名下的主题标识线、照片边框/强调条、已选主题标记和 CLI 摘要中的推荐页数；不得用于正文段落、大面积背景、所有链接或每个可点击元素。

## Frozen Layout And Pagination Contract

布局规划器必须在 Typst 对象/文本发射前生成不可变 `FrozenResumePlan`。渲染器只消费该计划，不能重新分页、调整模块顺序或改变任何文字预算。

| Plan field | Required contract |
|------------|-------------------|
| `theme`, `page_count`, `photo_mode`, `font_manifest_hash` | 记录实际主题、精确页数、照片模式和受控字体身份；缺失任何一项即拒绝渲染 |
| `pages[]` | 每页记录安全区、主题栏位、已占用高度、模块锚点与可见条目 ID；不得产生空白第 2/3 页 |
| `containers[]` | 记录 `fact-block` / `list-entry` 类型、原模块语义、源事实 ID、页面和几何预算；未知模块按默认映射或用户显式容器覆盖处理 |
| `entry_budget` | 每个项目、实训、经历、证书条目的完整高度预算；标题、元数据、职责和成果必须同页 |
| `reorder_reason` | 发生受限重排时记录允许的原因与前后模块顺序；个人信息不得离开首页首位，教育不得被移至后部 |
| `recommendation` | 自动/强制页数下记录建议页数、实际主产物页数、对照页数和提示文案；不包含新事实 |

分页规则：

- `项目 / 实训 / 经历` 的单个 `list-entry` 是严格不可拆最小单元；其职责与成果不得分至下一页。
- `证书` 可整组跨页，但同一证书条目不可拆；`技能` 可按组续页，但页尾不得只留技能组标题。
- 模块整体优先保持同页；空间不足时先移动完整条目，再允许模块在条目边界续页。第二页不能以无标题的续接正文、日期、职责或成果开头。
- 自动页数按“明显适合 1 页 / 明显适合 2 页 / 临界区”三段判定。临界区生成推荐主产物与另一页数对照版本；强制 1 页同时生成推荐 2 页对照，强制 2 页内容不足时保留 2 页并提示推荐 1 页。
- 自动模式先尝试 1 页和 2 页的合法计划；只有 2 页也无法满足安全区、字号、行距、完整条目和页面有效内容时才失败关闭。

## Photo Contract

- 只有 YAML `photo` 指向学生明确提供且通过既有本地路径校验的文件时，`photo_mode: auto/photo` 才能生成照片版；`no-photo` 或缺失 `photo` 一律生成无照片版。
- 图片先使用 contain 式等比放置；只有主题槽位明确允许且不伤害主体时才做受控裁切。不得拉伸、自动修图、生成替代照片或读取远程 URL。
- 无照片版必须从布局计划、Typst 输入、PDF、预览和中间可投递产物中同时移除照片、边框、强调条、缩略图、EXIF 和路径引用。
- 右上/左栏/顶部照片消失后的补位仅可按各主题上表执行；禁止创建第二照片位置或把图片插入正文。

## Interaction And Copywriting Contract

本阶段的交互面是离线 CLI 与其可审阅的计划摘要，不提供网页编辑器、自由拖拽、自由换色或手工分页。

| Element | Copy |
|---------|------|
| Primary CTA | `生成布局方案` |
| Theme choice | `主题：保守稳妥`、`主题：现代简洁`、`主题：个性设计`；展示全部三项，不以单一默认主题遮蔽其他选择 |
| Page choice | `页数：自动`、`页数：1 页`、`页数：2 页` |
| Photo choice | `照片：自动`、`照片：使用已提供照片`、`照片：不使用照片` |
| Empty state heading | `暂无可生成的已核实资料` |
| Empty state body | `请先完成资料校验，再生成主题与页数布局方案。` |
| Error state | `无法在可读性下限内收敛为 1 或 2 页。请精简已有摘要或成果表述，或补充缺失的真实资料后重试。` |
| Page recommendation | `建议使用 {N} 页；已同时生成 {otherN} 页对照方案。` |
| Forced-page advisory | `已按要求生成 {N} 页；基于当前内容更推荐 {recommendedN} 页。` |
| Destructive confirmation | none；本阶段不删除资料、照片或已发布产物。后续发布/清理操作必须另行确认 |

状态反馈必须清楚列出实际主题、页数、照片模式、是否使用对照方案、字体版本/哈希和任何失败关闭原因；不得在输出中暴露照片绝对路径、EXIF、电话、邮箱或完整源事实。

## Accessibility And Print Acceptance

- PDF 必须可复制/搜索中文正文；不得将文字栅格化或仅以图片表达联系方式、模块标题和条目内容。
- 信息不能只靠色彩区分；每个主题在灰度打印时仍能通过位置、标题、分隔和字重扫描。
- 任何主题必须通过短、标准、内容压力、长姓名、长单位名、长证书名、长成果、有照片和无照片样张。每份样张仅可为 1 或 2 页 A4。
- PDF 页面级验收要检查：首页个人信息锚点、教育前置、每个 `list-entry` 完整、第二页有合法模块开端、无孤立标题、无第三页、无裁切/重叠/溢出。

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not applicable；本阶段不是 shadcn/React UI |
| third-party | none | not applicable；不得引入模板市场、远程主题包或第三方 UI block |

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS
- [ ] Dimension 2 Visuals: PASS
- [ ] Dimension 3 Color: PASS
- [ ] Dimension 4 Typography: PASS
- [ ] Dimension 5 Spacing: PASS
- [ ] Dimension 6 Registry Safety: PASS

**Approval:** pending

## Decision Sources

| Source | Applied decisions |
|--------|-------------------|
| `47-CONTEXT.md` | 三主题边界、唯一事实源、容器、照片、页数策略、条目不可拆、受限重排、多主题可见原则 |
| `REQUIREMENTS.md` / `ROADMAP.md` | THEME-01..05、精确 1/2 页 A4、失败关闭、不虚构事实 |
| `phase-46-baseline.md` / `schema-and-review-contract.md` | YAML 偏好、照片本地性、受控 CJK 字体、renderer-owned 派生边界 |
| `.planning/research/PITFALLS.md` | 可读性下限、字体锁定、无照片产物边界、页面级验证 |
| Default (agent discretion) | 三套视觉语言、调色板、印刷字号、冻结字段、CLI 文案 |
