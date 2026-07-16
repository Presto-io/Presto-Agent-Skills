# School Presentation Authoring and Layout Reference

This reference holds Markdown authoring, page model, layout, and fixed-canvas rules for the `school-presentation` skill. Keep `SKILL.md` as the concise semantic entry point and update this file when long authoring behavior changes.

## Frontmatter

- `template`: 固定为 `school-presentation`。
- `title`: 演示文稿标题；封面渲染时每行最多 10 个可见字符、最多 2 行，生成时应优先提炼为 20 个中文字符以内。
- `subtitle`: 副标题；未知时留空，建议不超过 24 个中文字符，渲染器会按 24 个可见字符截断。
- `unit`: 可选单位字段；未知时留空，留空时封面信息栏不显示单位。不要把 `school`、`department` 或 `location` 当作封面信息栏字段。
- `author`、`presenter`、`reporter`、`date`: 可选封面信息栏字段；未知时留空或标记复核。`author`、`presenter`、`reporter` 只会归并为一个汇报人值，封面上不再显示“汇报人”标签；`date` 只显示日期值，不再显示“时间/日期”标签。
- `page_ratio`: 页面比例，只允许 `16:9` 或 `4:3`，默认 `16:9`；渲染器按该比例生成等尺寸物理页。
- `max_output_mb`: 默认 `50`，用于离线 HTML 产物尺寸门禁。

## Persistent Assets

- 当前版本持续引用的相对资源统一写为 `assets/<safe-relative-path>`，并与 reviewed Markdown + offline HTML 一起进入 candidate gate。
- 只复制 Markdown/HTML 仍明确引用的 confirmed assets；未引用输入不进入 current 或 history，`sources/` 永不由 normal render 改写或归档。
- legacy `media/` 不是 normal root 例外。迁移必须先只读审计并获得明确确认，再移动获批资源、同步把文本引用改成 `assets/`，最后重跑 render/reference gate；不得静默移动整个目录。
- 图片默认 contain、不裁切。缺少 required `assets/...` 会阻断 current 发布；绝对或非持久 optional media 的 fallback 仍须在 evidence 中留有 warning。

## Deck Structure

- 正文优先用 `## Section: 章节名` 表达章节边界。
- 章节下用 `### Slide: 标题` 表达一个逻辑页。
- 旧的平面 `## Slide: 标题` deck 仍然兼容，渲染器会把它们放入默认章节。
- 逻辑页下方可放一个 `<!-- slide ... -->` 元数据块。

## Slide Metadata

Supported `layout` values:

- `auto`
- `cover`
- `closing`
- `section`
- `content`
- `media-right`
- `media-left`
- `media-center`
- `media-compare`
- `media-chart`
- `full_page_image`
- `table`
- `chart`
- `quote`

Other metadata:

- `intent`: 该页的表达目的，供 agent 审阅和渲染器选择布局。
- `split`: 默认为 `auto`，过长内容可自动拆为多个物理 HTML 页。

## Cover Rules

- 封面只能由一个主标题、一个可省略副标题和一个固定信息栏构成。
- 主标题每行最多 10 个中文字符、最多 2 行。
- 副标题最多按 24 个中文字符设计。
- 固定信息栏只允许可选单位值、汇报人值、日期值。
- 单位字段默认不显示，只有用户填写 `unit` 时才显示，且封面不显示“单位”标签。
- 汇报地点不再使用。
- 不要根据用户需求额外发明“主题、班级、课程、项目背景、适用对象、指导思想、地点”等封面栏目。
- 不要在封面逻辑页正文中追加说明段落、第二副标题、口号、项目背景、更多信息卡片或自定义 `cover_*` 字段。
- 封面后的补充内容必须移动到第一个内容页。
- 渲染器会忽略封面正文块，只使用 frontmatter 的 `title`、`subtitle`、`unit`、汇报人和日期，防止首页内容溢出。

## Page Hierarchy

The fixed page model is:

```text
sections -> logical_slides -> physical_pages -> reveal_steps
```

- 渲染器会在封面后自动插入目录页。
- 目录只读取 `## Section:` 一级章节标题，不要求 Markdown 作者手写次级页标题。
- 目录每页最多显示 5 个章节，超过后自动拆成多个目录物理页。
- 一个逻辑页可以自动拆成多个物理页。
- 物理页标签使用逻辑页点号格式，例如 `3.1`、`3.2`。
- `reveal_steps` 记录当前物理页中的有序揭示、强调和答案遮罩步骤。

## Markdown Content

Logical slide content stays in ordinary Markdown:

- 标题
- 段落
- 列表
- 表格
- 代码块
- 公式
- 图片
- 视频占位
- 图表 fenced block
- 强调块
- speaker notes

Emphasis blocks:

- `::: info`
- `::: tip`
- `::: warning`
- `::: error`

GitHub alert compatibility:

- `> [!NOTE]`
- `> [!TIP]`
- `> [!IMPORTANT]`
- `> [!WARNING]`
- `> [!CAUTION]`

## Full Page Image Layout

`layout: full_page_image` is for workflows that already generated a complete page image.

- The logical slide still uses `### Slide: 标题` and slide metadata for directory, page number, and management semantics.
- The page body renders only the first Markdown image.
- It does not display title, page number, footer, caption text, speaker notes, or interactive elements.
- The image is centered in the full canvas with contain placement and no cropping.

## Classroom and Structured Layout Syntax

- Block reveal: `::: reveal order=1 ... :::`
- Answer mask: `::: mask order=1 ... :::` or inline `{{mask order=1}}答案{{/mask}}`
- Correct emphasis: `::: emphasis order=1 ... :::` or inline `{{emphasis order=1}}正确项{{/emphasis}}`
- Auto step animation: `animate: step` in slide metadata.
- Sort exercise: `::: sort final_order=4 ... :::` with item attributes such as `[order=1]`.
- Peek prompt: `::: peek title="教师提示" trigger=both target="查看教师提示" ... :::`
- Timeline: `::: timeline variant=vertical|horizontal ... :::`
- Cards: `::: cards columns=3 ... :::`
- Gallery: `::: gallery variant=compare|album|strip ... :::`
- SmartArt: `::: smartart type=process|cycle|hierarchy|pyramid ... :::`

Images collections should use `gallery`. Do not write raw HTML. Do not add `::: process :::`; process diagrams use `::: smartart type=process :::`.

## Semantic Icons

- Ordinary content pages default to `icon=auto`.
- The renderer chooses restrained school-identity CSS icons based on title, intent, and body.
- Slide metadata can set `icon=none` or one of `safety|risk|formula|chart|table|media|reveal|review|process|target`.
- Cover, closing, and section pages do not auto-add title icons.
- Structured items also support `icon=none`.

## Section Dividers

- The renderer creates optional section divider pages for each non-default section.
- The top `章节页` button controls whether preview includes section dividers.
- Final PDF export follows the current preview state.
- Do not use raw HTML in Markdown to control section divider inclusion.

## Fixed Canvas Rules

- Slide internals must keep fixed design canvas dimensions.
- Do not use viewport-dependent CSS inside slide content, fonts, image heights, or grids.
- Avoid `vh`, `vw`, and viewport-based `clamp()` inside slide layout.
- Across preview sizes and browser zoom levels, only the outer stage scale may change; slide internal relationships must scale like an image.
