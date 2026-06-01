# Phase 9: Playback Workspace and Page Hierarchy - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-01
**Phase:** 9-Playback Workspace and Page Hierarchy
**Areas discussed:** 播放模式边界, 预览工作区布局, 总览视图选择, 层级模型写法

---

## 播放模式边界

| Question | Options Considered | User's Choice |
|----------|--------------------|---------------|
| 生成的 HTML 打开后默认进入哪里？ | 预览工作区优先; 播放模式优先; 保留滚动 deck 优先; 你来定 | 预览工作区优先 |
| 单文件 HTML 能否实现？ | 使用内嵌 CSS 和 vanilla JS 维护 view/current page/hash 状态 | 确认可以，且应保持单文件 HTML |
| 播放模式导航方式？ | 键盘+点击; 只用键盘; 显式按钮+键盘; 你来定 | 键盘上下左右和空格、左/中/右点击热区、触屏上下左右滑动 |
| 播放模式退出方式？ | Esc; 工具条; 双击/长按; 组合使用 | 组合使用 |
| 当前页状态是否写入 URL hash？ | 写入 hash; 只运行时状态; hash+localStorage; 你来定 | 写入 hash |
| 播放进度如何表达？ | 用户补充 | 细顶部进度条，使用学校蓝绿色条 |

**Notes:** 中区点击在 Phase 9 等同下一页，Phase 10 有 reveal 后优先推进 reveal step。工具条只保留返回工作区、打开总览、当前进度等必要动作。

---

## 预览工作区布局

| Question | Options Considered | User's Choice |
|----------|--------------------|---------------|
| 左侧 rail 展示什么层级？ | 按逻辑页分组展示物理页; 平铺所有物理页; 只显示逻辑页展开; 你来定 | 按逻辑页分组展示物理页 |
| 右侧大预览如何呈现当前物理页？ | 真实 slide DOM; 截图式缩略大图; 内容摘要; 你来定 | 真实 slide DOM |
| 缩略图 rail 怎么做？ | 缩放真实 DOM; 简化卡片; 混合方案; 你来定 | 混合方案 |
| 选中状态怎么同步？ | 三处强同步; 工作区内部同步; 只同步页码; 你来定 | 三处强同步 |

**Notes:** 宽 rail 使用真实 DOM 缩放；窄 rail 使用按 layout family 设计的简化卡片。简化卡片要对应常用版式，而不是通用摘要卡，避免缩放造成的锯齿感。

---

## 总览视图选择

| Question | Options Considered | User's Choice |
|----------|--------------------|---------------|
| 总览视图是什么？ | PPT/Keynote slide sorter/light table; 用户补充章节视觉线索 | 像 PPT 总览，但加章节分割和视觉线索 |
| 点击 overview tile 后回到哪里？ | 预览工作区; 播放模式; 根据入口返回; 你来定 | 预览工作区 |
| 章节来源从哪里来？ | Markdown 显式章节+自动兜底; 完全自动推断; 只认显式章节; 你来定 | Markdown 显式章节+自动兜底 |
| Overview tile 缩略方式？ | 复用 rail 响应式缩略体系; 永远简化卡片; 永远真实 DOM; 你来定 | 复用 rail 响应式缩略体系 |

**Notes:** 用户希望总览能看到章节边界，知道哪一页是章节第一页、哪一页是下一章节第一页。叠放卡片样式可作为候选，但最终以实用为准。

---

## 层级模型写法

| Question | Options Considered | User's Choice |
|----------|--------------------|---------------|
| Markdown 里章节怎么写？ | slide metadata section; `## Section:`; 两者都支持; Markdown 多级标题直接定义并解析 | Markdown 多级标题直接定义并解析，兼容旧 `## Slide:` |
| 物理页编号如何显示？ | 逻辑页.物理页编号; 全局物理页编号; 双编号; 你来定 | 逻辑页.物理页编号 |
| Manifest 是否输出完整层级树？ | 完整层级树; 计数+扁平 pages; 只写 DOM; 你来定 | 完整层级树 |
| DOM 暴露哪些属性？ | 完整 data 属性; 只保留 index; 只用 JS manifest; 你来定 | 完整 data 属性 |

**Notes:** 新模板建议使用 `## Section: Name` 和 `### Slide: Title`；旧模板的 `## Slide:` 继续兼容并落入默认章节。Manifest 树包含 `sections -> logical_slides -> physical_pages -> reveal_steps`，Phase 9 可将 `reveal_steps` 留空。

## Claude's Discretion

- 总览的具体章节视觉线索由 planner/executor 选最实用方案，可在章节分组网格、章节分隔带、章节首页强调、叠放卡片组之间权衡。

## Deferred Ideas

- Phase 10: ordered reveal execution, emphasis animation, and classroom answer masks.
- Later milestone: annotation, marking, drawing, and presenter markup tools.
