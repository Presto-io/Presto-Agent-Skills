# school-pptx Markdown 契约

本文档是 `school-pptx` v1.17 唯一公开的 Markdown 写作契约。Markdown 只描述逻辑内容；布局集合、槽位类型和文字预算以 `templates/standard-school.manifest.yaml` 为机器事实源。

## 可复制的最小示例

```markdown
---
title: "职业院校智能制造课程建设"
subtitle: "课程体系、实训条件与实施路径"
school: "示例职业技术学院"
department: "智能制造学院"
program: "机电一体化技术"
course: "智能产线安装与调试"
author: "课程建设团队"
presenter: "张老师"
date: "2026-07-13"
theme: "standard-school"
---

::: slide {layout="cover"}
:::

::: slide {layout="contents"}
:::

::: slide {layout="title-content"}
## 建设目标

### 课程目标

围绕**岗位能力**组织课程内容，并用==真实任务==贯穿教学。

::: notes
先说明课程目标，再说明任务来源。
:::
:::
```

## YAML formatter

公开 YAML 只允许以下十个键，生成示例也必须保持此顺序：

1. `title`
2. `subtitle`
3. `school`
4. `department`
5. `program`
6. `course`
7. `author`
8. `presenter`
9. `date`
10. `theme`

未知键是错误。可选值缺失时直接省略，不写空占位。`theme` 必须是 manifest 的 `available_themes` 之一。

D-02 锁定以上白名单。D-03 规定：YAML 未提供 `title` 时，正文中第一个且唯一的文档级 `#` 作为标题回退；YAML 已有 `title` 时它不覆盖 YAML。文档级 `#` 最多一个，且永不进入目录。目录只收集有效普通幻灯片内的 `##`，严格保持源码顺序。

## slide 与标题

公开容器必须写成 `::: slide {layout="..."}`。D-01 要求 `layout` 必填；公开属性只允许 `layout`。D-04 明确拒绝 `id` 以及任何其他属性。缺失、未知或不可由 Markdown 控制的布局均验证失败。

除 `cover`、`contents` 两个空容器外，每个可创作容器恰好包含一个普通 `##` 标题。slide 外的 `##`、重复 `##` 或其他无法归属的标题均为错误。

## 顶层内容块

D-05 定义完整段落、完整列表、单张图片、完整表格和 fenced code 为原子顶层块。空行结束段落；连续列表项组成一个块；表头、分隔行和全部数据行组成一个表格块。

`### 标题` 是强制块边界，只绑定紧随其后的一个完整块，并作为该块的可见小标题。空 `###` 只创建边界，不产生可见小标题。连续未消费的 `###`、`###` 后没有块或把 `###` 绑定到 notes 都是错误。

D-06 规定 `two-column` 按源码顺序配对块：1/2、3/4，依此类推；最后一个未配对块属于左栏，右栏为空。逻辑模型记录配对，不创建物理页。

D-07 规定 `title-content` 与 `two-column` 的块和 manifest 预算是后续展开输入。D-08 规定 Phase 43 生成的每张物理页都保留原逻辑 `##` 标题，不添加 continuation、序号或“续”后缀。

D-09 规定 `image-text` 是一个稳定正文块加一张或多张主图；每张图是后续一页的输入，标题、正文和 notes 保持不变。D-10 规定 `table` 的可选绑定 `###` 是表格标题，和表格构成不可拆复合块；它与幻灯片 `##` 标题是两个独立字段。

## 布局语义

本契约覆盖 `11/11 controlled layout semantics: 10 explicit + 1 implicit`。

| 布局 | 可创作内容 |
|---|---|
| `cover` | 显式空容器；内容来自 YAML 或文档标题 |
| `contents` | 显式空容器；条目由有效 `##` 自动生成 |
| `section` | 一个 `##`，不得有正文 |
| `title-content` | 一个 `##` 和一个或多个有序块 |
| `two-column` | 一个 `##` 和按源码顺序配对的块 |
| `image-text` | 一个 `##`、一个稳定正文块和一张或多张图片 |
| `table` | 一个 `##` 和一个 Markdown 表格，可带绑定的 `###` 表格标题 |
| `timeline` | 一个 `##` 和唯一规范表头 `时间 | 标题 | 说明` 的表格 |
| `gallery` | 一个 `##` 和连续图片块，不允许其他正文 |
| `code` | 一个 `##` 和一个 fenced code block，保留语言和代码文本 |
| `closing` | 不可创作；模板在文稿末尾隐式追加且只追加一次 |

显式 `layout="closing"` 无效。它必须产生：`closing 由模板在文稿末尾自动追加，不能在 Markdown 中显式创建或修改。`

## notes

D-11 使用 slide 内的 `::: notes` 表达演讲者备注。notes 可省略，最多一次，必须是 slide 的最后一个子节点；它不进入可见块和目录。逻辑 slide 后续扩展为多个物理页时，同一份 notes 复制到所有扩展页。

## 图片与图注

D-12 只允许普通 Markdown 图片 `![图注](path)`。相对路径只相对 Markdown 文件目录解析；显式绝对路径保持显式；禁止从当前目录、兄弟 skill、测试资源或网络回退。alt text 是可见图注，空 alt 表示无图注。

D-13 规定图片与可选图注是不可拆的复合块，后续使用 `contain` 语义：保持宽高比、不裁剪、不把图注拆到另一页。D-14 规定缺失或非文件媒体必须使验证失败，同时逻辑 JSON 可保留 authored path、resolved path、源码位置、`exists: false` 和清楚标识的安全 placeholder 描述符，绝不能把回退元数据报告为验证成功。

## 行内语义与禁用面

D-16 仅增加两种行内语义：标准 `**bold**` 和受控 `==highlight==`。高亮颜色由模板决定，作者不能带颜色参数。D-17 不提供 animation、reveal、逐项出现或原生对象动画语义。

D-15 采用允许列表：fenced code 外拒绝 raw HTML、HTML 注释、通用 attributes、`id`、coordinates、`x/y`、width/height/dimensions、crop、footer、font/font-size、color/background 和 style 控制。任何未知 `:::` directive 也属于错误。fenced code 内容完全不透明，其中的 HTML、CSS、坐标、字体或颜色字样仅是代码文本。

## 诊断与退出状态

`validate` 聚合所有可定位错误，错误在警告之前，每组按 `(line, column, code)` 排序。规范首行是：

```text
<path>:<line>:<column> [<CODE>] <message>
```

随后必须提供 `slide`、`layout` 和一个具体 `fix`。行列从 1 开始。未知 YAML、未知主题、缺失/未知布局、显式 closing、未知 slide 属性、禁用样式、raw HTML、缺失媒体、notes 位置、非法标题和非法 timeline 都必须给出稳定代码和可执行修复建议。任何 `errors` 都使命令非零退出；即使写出诊断 JSON 也不得删掉错误或宣称通过。

## 逻辑交接与范围

Phase 43 直接消费 `metadata`、`document_title`、`contents_entries`、`logical_slides`、`implicit_slides`、`coverage`、`errors` 和 `warnings`，以及块、位置、notes、媒体和 overflow evidence；不得重新解释 Markdown。

本契约不公开 PPTX geometry values、坐标、renderer 实现、physical pagination 实现、continuation title、notes XML、模板视觉修改或 package-manager 依赖。Phase 43 负责 PPTX 对象与物理分页；Phase 44 负责 runtime adapters、最终验证与 final UAT。本阶段不实现这些下游工作。
