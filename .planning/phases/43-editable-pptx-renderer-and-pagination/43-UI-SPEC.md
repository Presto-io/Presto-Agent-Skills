---
phase: 43
slug: editable-pptx-renderer-and-pagination
status: draft
shadcn_initialized: false
preset: none
created: 2026-07-14
---

# Phase 43 — UI Design Contract

> 面向 PPTX 视觉呈现、编辑体验、分页与渲染状态的设计契约。此处的 UI 是 PowerPoint/WPS 中的幻灯片画布与对象，不是网页界面。

---

## Scope

Phase 43 将 Phase 42 的逻辑文档模型渲染为使用 `standard-school` 受控模板的可编辑物理幻灯片，并负责：

- 逻辑页到物理页的确定性分页；
- 正文、列表、代码、表格、时间线、目录、图集和图文页的视觉装填；
- 原生文本、表格、图片、组合对象与演讲者备注；
- 成功、best-effort 异常与不可恢复失败三种用户可感知状态；
- 同名 Markdown 与 PPTX 的标准双产物交付。

本阶段不增加布局，不允许 Markdown 控制坐标、字体、颜色、裁剪、装饰或动画，不实现复杂转场，不编写六 runtime adapter，不以 PDF 或截图替代 PPTX，也不承担 Phase 44 的跨 PowerPoint/WPS 手工视觉验收。

---

## Design System

| Property | Value |
|----------|-------|
| Tool | `python-pptx 1.0.2` 为主要对象生成器；只对 run 高亮和种子页移除使用隔离、可测试的 OOXML 辅助层 |
| Preset | `standard-school` |
| Component library | 无；使用原生 PPTX 文本、图片、表格和组合形状 |
| Icon library | 无；图标沿用普通 Markdown 图片语义并渲染为可替换图片对象 |
| Font | 模板主题主字体 `等线 Light`，正文字体 `等线`；代码使用 manifest/template 指定的等宽字体，不由 Markdown 指定 |
| Canvas | 继承 `standard-school.pptx` 的页面尺寸、母版、布局、页脚和装饰资源 |

设计系统来源优先级固定为：

1. `standard-school.pptx` 的 theme、master 和 slide layout；
2. `standard-school.manifest.yaml` 的布局映射、槽位几何、文字预算和空槽行为；
3. 本契约对分页、对象结构和异常状态的补充规则；
4. 渲染器不得另建一套视觉常量覆盖上述来源。

Phase 43 开始渲染前必须先修订并重新校验以下模板契约缺口：

- `gallery.caption.empty_slot` 从 `hide` 改为 `preserve`；
- 表格布局增加 manifest 所有的 `table_name` 空间和预算；
- 图集为 1、2、3、4 项定义 manifest 所有的卡片几何；
- 时间线定义节点子区域或确定性的 manifest 所有细分规则；
- run 级高亮增加 theme scheme token；
- `closing.pptx_layout` 校正到实际结束页使用的 `ppt/slideLayouts/slideLayout7.xml`。

任何缺口未完成时，渲染器不得在代码中临时硬编码几何或颜色绕过 manifest。

---

## Layout Ownership

受控布局仍为 11 个：`cover`、`contents`、`section`、`title-content`、`two-column`、`image-text`、`table`、`timeline`、`gallery`、`code`、`closing`。前 10 个来自 Phase 42 逻辑模型，`closing` 只在文稿末尾隐式追加一次。

| Ownership | Contract |
|-----------|----------|
| 模板拥有 | 页面尺寸、母版、布局 XML、槽位几何、背景、装饰、页脚、主题色、字体、字号上下限、文本框边距 |
| 逻辑模型拥有 | 标题、块顺序、正文、列表、代码、表格数据、时间线节点、媒体路径、图注、备注、粗体/高亮语义 |
| 分页器拥有 | 物理页数量、连续片段边界、页内字号选择、目录/时间线的全局分区、续页上下文复制 |
| 发射器拥有 | 将已决定的物理页计划转换为原生可编辑对象，不再改变分页 |

每个物理页必须使用 manifest 指向的 slide-layout XML 关系，不能按本地化布局名称或数字索引猜测。模板现有的五张种子页必须在发射前移除，不能泄漏到成品。

---

## Spacing Scale

基础审阅刻度仍遵循 4 的倍数；真实 PPTX 几何以 manifest 的 EMU 值为唯一执行依据。

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px equivalent | run 内部最小视觉间隔、紧凑元数据 |
| sm | 8px equivalent | 图注内部、表格单元格紧凑留白 |
| md | 16px equivalent | 段落、列表项、代码行组之间的默认节奏 |
| lg | 24px equivalent | 子标题与其内容块、时间线节点内部层级 |
| xl | 32px equivalent | 卡片间距、双栏间隔、表名与表格本体间隔 |
| 2xl | 48px equivalent | 标题区与主要内容区分隔 |
| 3xl | 64px equivalent | 封面、章节页和结束页的大块呼吸空间 |

例外：槽位实际位置、尺寸、边距和卡片分区只能读取 manifest/template，不将上述 px 值换算后写死在发射器中。页面视觉重量由内容实际换行高度、对象占用和留白共同计算，不仅比较字符数或条目数。

---

## Typography

### Theme typography

| Role | Theme/manifest source | Behavior |
|------|-----------------------|----------|
| Display / slide title | theme major font；简体中文为 `等线 Light` | 使用各 layout 的 `title` 预算，不越过 `font_size_min` / `font_size_max` |
| Body / labels | theme minor font；简体中文为 `等线` | 使用对应 body、caption、table、timeline 预算 |
| Code | manifest/template 指定的等宽字体 | 可编辑纯文本，不要求语法高亮 |
| Bold | 原生 run `bold` | 与普通文字保持同一文本框和连续编辑体验 |
| Highlight | manifest 指定的 theme scheme color + `<a:highlight>` | 不硬编码 RGB，不拆成底色形状和独立文本框 |

文字排版遵循以下硬规则：

- 发射前由分页器选择字号，发射后不得调用会破坏 run 样式的统一 `fit_text()`；
- 正文使用显式换行估算与 CJK 感知测量，不能用空格分词作为中文换行权威；
- `word_wrap` 开启，PowerPoint 自动缩放关闭，防止查看器再次改变分页结果；
- 字号调整始终在 manifest 范围内；视觉孤行可通过重新选择更大或更小字号消除，但不能截断文字；
- `**bold**` 与 `==highlight==` 的 Markdown 分隔符不进入可见文本，run 顺序和纯文本内容必须可往返验证。

---

## Color

PPTX 色彩完全继承模板的 `CEE配色` 主题，不提供 Markdown 颜色入口。

| Role | Theme value | Usage |
|------|-------------|-------|
| Dominant | `lt1 #FFFFFF` | 主要背景与浅色画布 |
| Text | `dk1 #000000`、`dk2 #0E2841` | 主题正文与深色层级文字 |
| Secondary | `lt2 #E8E8E8` | 中性底色与次级表面 |
| Accent 1 | `#579E40` | 模板既有绿色强调 |
| Accent 2 | `#5E9768` | 模板既有辅助绿色 |
| Accent 3 | `#549183` | 模板既有青绿色层级 |
| Accent 4 | `#498B9E` | 模板既有蓝绿色层级 |
| Accent 5 | `#3E85B9` | 模板既有蓝色层级 |
| Accent 6 | `#0084CC` | 模板既有高强调蓝色 |
| Hyperlink | `#467886` | 主题超链接 |
| Followed hyperlink | `#96607D` | 已访问超链接 |

Accent 的具体用途由现有 master/layout 和新增 manifest token 决定。渲染器不得凭内容类型重新分配主题色。高亮必须引用 theme scheme token；表格、时间线、代码背景和缺失媒体占位符也必须使用模板定义的颜色角色，而非发射器私有 RGB。

异常 best-effort PPTX 不添加红色边框、警告色横幅、水印或警告页；异常状态仅由 CLI 与调用 agent 明示。

---

## Information Hierarchy

每个物理页保持以下阅读顺序：

1. 原逻辑页 `##` 标题；
2. 与当前布局相关的可选块标题或表名；
3. 主内容对象；
4. 模板拥有的装饰和页脚；
5. 演讲者备注仅位于 notes，不进入画布。

除已有表名外，续页不显示“续”、页码后缀或新的视觉状态。被拆分的带 `###` 内容块在每个片段重复同一小标题，不追加“续”也不使用弱化样式。

---

## Physical Pagination Contract

### Shared rules

- 先按源码顺序将完整顶层块装入当前物理页；下一个完整块放不下时整体移到下一页。
- 只有单个块本身超过空白物理页预算时，才允许在块内拆分。
- 任何物理页都保留原 `##` 标题，且同一逻辑页派生的所有物理页复制相同演讲者备注。
- 分页结果必须由纯物理页计划先确定，再发射 PPTX；发射器不得边写对象边改变页界。
- 相同输入、模板和依赖版本必须得到相同的物理页计划与连续分割点。

### Paragraphs and lists

段落拆分优先级固定为：

1. `。！？!?；;` 等句末边界及其尾随引号/括号；
2. `，、：:` 等弱标点或自然停顿；
3. 仅当单个句子仍超过整页时进行字素安全硬拆。

列表只在完整列表项之间拆分。单个列表项超过整页时，才在该项内部按段落优先级拆分，并在续页保留列表语义。不得在组合字符、变体选择符或 emoji 序列中间硬拆。

### Code

- 只在完整源码行之间分页；
- 超宽行在文本框中软换行，不向可编辑代码文本插入换行符；
- 页高预算按软换行后的显示行数计算；
- 每页使用一个连续、可编辑的等宽文本框，保持原始源码行与空白；
- 单行在最小字号下仍过高时，不截断；生成有界 best-effort 异常并非零退出。

### Tables

表格是“可缺省表名 + 表格本体”的复合块，表名与 `##` 标题无关。

- 数据本体必须是原生 `<a:tbl>`，每个物理页创建一张新原生表格；
- 表头在每张续页重复；数据行保持完整，不跨页、不截断；
- 有表名时，首张显示原表名，续页显示 `原表名（续）`；
- 无表名时，所有页保留空的可编辑表名文本框，不生成“表格（续）”或提示文案；
- 字号与行高选择以整张物理表格为单位搜索，不能只对单个单元格后处理；
- 视觉孤行指单元格排版后肉眼可见的孤立文本行，而非只剩一条数据记录；
- 优先在预算内调整字号和换行消除视觉孤行；若缩小仍产生孤行，允许增大字号诱导更均衡的多行重排；
- 不能仅因视觉孤行报错，也不能为消除孤行截断内容。

表格分页候选按以下优先级选择：无溢出/截断 → 无视觉孤行 → 页数更少 → 接近首选字号 → 各页实际高度更均衡。

### Timeline

- 时间线保持水平阅读方向与时间顺序；
- 每个节点是“标记 + 时间 + 标题 + 说明”的原生可编辑组合对象，主轴线独立于节点组合；
- 每页节点数量随文字高度弹性变化，不固定条数；
- 对整个逻辑时间线执行全局连续分区，不能只修补最后两页；
- 通常每个物理页至少 3 个节点；如果下一页只有 1 个节点，优先吸回上一页，否则从前页再移 2 个节点形成至少 3 个；
- 重新分配时必须同步考虑所有前页，使条目数和换行后的视觉重量整体接近，禁止明显长页/短页交替；
- 只有完整逻辑时间线本身少于 3 项时，才自然允许少于 3 项的页面；对于 3 项以上但因超高节点无法满足容量与最少 3 项的情况，生成最优 best-effort 分区、报告 `TIMELINE_BALANCE_INFEASIBLE` 并非零退出。

全局目标优先级：无容量违规 → 无孤项 → 节点数差异最小 → 视觉重量方差最小 → 总留白最少 → 稳定的最早分割点。

### Contents

- 所有物理页标题均严格为 `目录`，不追加“续”；
- 编号跨页连续，项目顺序与 Phase 42 的 `##` 顺序一致；
- 对所有目录页全局连续分区，先使条目数尽可能均衡，通常页间数量差不超过 1；
- 再依据长标题换行后的实际高度微调，使各页视觉重量相近；
- 只有为避免真实溢出时才允许更大的条目数差异；不得出现明显“多的多、少的少”或末页孤项。

### Gallery and image-text

- 图集每张物理页最多 4 项，按 manifest 的 1/2/3/4 项几何预设排布；
- 每项由可替换图片和可编辑图注文本框组成一个原生组合对象；
- 即使 alt 为空，也必须存在空图注文本框；空框无提示文字，放映时不可见，但在选择窗格中可选；
- 图文页中的每张主图片产生一张物理页，复用稳定的标题、正文和备注；正文自身需要分页时，必须先在物理计划中明确与多图片扩展的组合关系。

---

## Editable Object Contract

| Content | Required PPTX object | Forbidden substitute | Verification evidence |
|---------|----------------------|----------------------|-----------------------|
| 标题、正文、列表、代码、图注、表名 | 原生文本框/占位符与 run | 整页截图、栅格化文字 | `has_text_frame`、可回读文本与 run |
| 表格 | 原生 `<a:tbl>` | 文本框和矩形拼接矩阵 | 每个表格物理页存在一张 native table |
| 普通图片/图标 | 原生 picture | 画布截图、默认裁剪占位图 | 图片关系有效，四向 crop 为 0 |
| 时间线节点 | 原生 `<p:grpSp>` | SmartArt、合成图片 | 每组包含 marker/time/title/description，轴线在组外 |
| 图集卡片 | 原生 `<p:grpSp>` | 图片与图注无关联散落 | 每组包含 picture + caption text box |
| 粗体 | 同一文本框内 native bold run | 独立粗体文本框 | run `b=1` 且纯文本连续 |
| 高亮 | 同一文本框内 `<a:highlight>` run | 底色矩形 + 单独文本框 | 使用 manifest 指定 theme scheme color |
| 备注 | notes slide text frame | 可见画布文字 | 仅有备注的逻辑页及其全部物理页存在 notes relationship |

空图注和空表名不是“缺少对象”，而是编辑入口。形状名称必须稳定且可结构检查，例如 `school-pptx:caption-placeholder` 与 `school-pptx:table-name-placeholder`；文本内容为空，不写“单击添加……”等提示。

---

## Media Placement

图片和图标统一使用 contain：

- 以媒体固有宽高比为准，等比缩放到槽位内部；
- 水平、垂直居中；
- 不裁剪，不拉伸，不超出槽位；
- 使用原生 `add_picture()` 类对象，不使用会默认 fill/crop 的 picture placeholder 插入；
- 替换图片后，用户仍能单独选择图片；图集卡片可整体移动，进入组合后可分别编辑图注或替换图片。

缺失媒体只使用本地、安全、可编辑的模板风格占位形状；不得联网搜索、猜测路径或加载其他文件。该占位符是 best-effort 异常证据，但不能被视觉上伪装成真实图片。

---

## Notes Experience

- 有备注的逻辑页：每张派生物理页写入相同备注文本；
- 无备注的逻辑页：不得访问或创建 notes slide；
- 备注永不进入目录、可见文本统计或幻灯片画布；
- 结构验证必须证明“应有的都有、不应有的都没有”，而不只检查至少存在一个 notes part。

---

## Render States and Copywriting Contract

### Command surface

推荐公开命令形态：

```text
school-pptx.sh render --input <reviewed.md> --out-dir <delivery-dir> [--stem <name>]
```

标准成功产物固定为：

```text
<delivery-dir>/<stem>.md
<delivery-dir>/<stem>.pptx
```

Markdown 必须按作者输入字节保留；成功目录不出现 manifest、逻辑 JSON、日志、诊断、临时文件或备份。

| Element | Copy |
|---------|------|
| Primary CTA | `渲染可编辑 PPTX` |
| Success heading | `渲染成功` |
| Success body | `已生成可编辑 Markdown 与 PPTX：<stem>.md、<stem>.pptx。` |
| Best-effort heading | `渲染完成但输入存在异常` |
| Best-effort body | `已生成可编辑的异常 PPTX，但本次渲染不成功。请检查下列异常和受影响幻灯片；修正 Markdown 后重新渲染覆盖，或在自动工作流结束后手工修正 PPTX。` |
| Unrecoverable heading | `渲染失败` |
| Unrecoverable body | `未替换现有 PPTX：{reason}。请按提示修复后重新运行 render。` |
| Empty state heading | `没有可恢复的幻灯片内容` |
| Empty state body | `请修复 Markdown 结构后重新渲染；closing 仍由模板隐式追加。` |
| Destructive confirmation | 无交互确认；只原子替换同 stem 的命令自有目标，不创建 `.bak` |

成功摘要顺序：

1. `渲染成功`；
2. 输入 Markdown 与主题；
3. 逻辑页数、物理页数和分页摘要；
4. 两个公开产物路径；
5. `校验结果：PASS`。

best-effort 摘要顺序：

1. `渲染完成但输入存在异常`；
2. 明确语句 `本次渲染不成功，命令退出码非零`；
3. 错误数、警告数与受影响逻辑页；
4. 源位置诊断，沿用 Phase 42 的有界格式；
5. 已写入的 Markdown 与异常 PPTX 路径；
6. 修正后覆盖或工作流结束后手工修改的建议。

调用命令的 agent 必须在面向用户的最终回复中再次明确异常、受影响页面与非零状态；仅说“已生成文件”不合格。

---

## Failure and Publication Contract

区分三种结果：

1. **有效模型 + 有效 PPTX**：发布 Markdown 和 PPTX，退出 0；
2. **无效模型 + 结构有效的 best-effort PPTX**：发布同名 Markdown 和最终文件名 PPTX，退出非零；
3. **不可恢复的渲染/包错误**：不替换原有 PPTX，清理命令自有临时文件，退出非零。

best-effort PPTX：

- 使用用户请求的最终文件名；
- 不插入警告页、横幅、水印或异常主题；
- 保留所有可恢复内容、可编辑安全占位符与唯一隐式 closing；
- 不得被 CLI 或 agent 描述为成功渲染。

发布采用同目录暂存和校验后替换：

- Markdown 与 PPTX 均先暂存；
- PPTX 必须在 ZIP/XML 检查和 `python-pptx` 重开成功后才发布；
- Markdown 先原子替换，PPTX 最后原子替换并作为提交产物；
- 不宣称两个独立文件形成跨文件原子事务；
- PPTX 发布前崩溃或不可恢复失败时，旧 PPTX 保持不变；
- 不生成公开 `.bak`、日志、证据或随机临时文件。

本契约中的标准双产物有意修订 PPTX-13 的“仅显式请求 Markdown 副本”旧措辞；Phase 43 规划与实现必须同步更新面向需求的命令契约。

---

## Verification Contract

### Automated structural checks

- 成品是可重开的非空 PPTX ZIP；
- 物理页数与物理页计划一致，种子页文本不存在，closing 恰好一个且在末尾；
- 每页布局关系与 manifest XML 映射一致；
- 正文、代码、表格、时间线标签和图注不是整页截图；
- 表格页含原生表格，续页表头重复，数据行完整，表名规则正确；
- contents 与 timeline 的全局分区满足条目数和视觉重量目标或产生明确 infeasible 异常；
- gallery 每页最多 4 项，每项为 picture + caption 的组合对象，空图注仍存在；
- 每张表格页都有表名文本框，空表名仍存在；
- 图片关系有效、宽高比保持、crop 四值为 0；
- timeline 节点和 gallery 卡片可重开为原生 group，轴线独立；
- 粗体与高亮 run 同时存在时互不破坏，高亮引用 theme scheme；
- 备注只出现在应有的全部物理页；
- 源码文本、换行和长行内容可往返，不因软换行改变源代码；
- 成功交付根目录恰好只有 `<stem>.md` 与 `<stem>.pptx`；
- 缺失媒体场景发布无水印 best-effort PPTX 且退出非零；
- 不可恢复的暂存失败保留旧 PPTX。

### Visual acceptance handoff

Phase 43 自动验证只能证明结构和保守测量。Phase 44 必须在 PowerPoint 或 WPS 至少一个兼容查看器中人工确认：

- 中文实际换行与估算没有造成溢出或明显孤行；
- 目录和时间线各页视觉重量接近；
- 组合节点/卡片可整体移动并可进入组合编辑；
- 主题字体、颜色、装饰和页脚未漂移；
- 高亮、contain 图片和空编辑占位符按契约显示。

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| none | none | 不适用；Phase 43 不使用网页组件注册表、SmartArt 市场、远程模板或网络媒体 |

所有运行时资产必须 skill-local。不得从 sibling skill 调用脚本，不得在渲染时下载字体、图片、模板或图标。

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS
- [ ] Dimension 2 Visuals: PASS
- [ ] Dimension 3 Color: PASS
- [ ] Dimension 4 Typography: PASS
- [ ] Dimension 5 Spacing: PASS
- [ ] Dimension 6 Registry Safety: PASS

**Approval:** pending
