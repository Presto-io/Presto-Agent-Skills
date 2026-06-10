---
name: "school-presentation"
description: "Use when creating, normalizing, or rendering school-official-style presentations from source materials, outlines, loose notes, or an existing Markdown logical-slide deck."
metadata:
  short-description: "学校风格 Markdown 逻辑页到离线 HTML 演示文稿工作流"
  version: "0.1.0"
  portability: "canonical"
  supported-runtimes:
    - Codex
    - Claude Code
    - Gemini CLI
    - OpenCode
    - OpenClaw
    - Hermes Agent
---

# School Presentation

## Objective

把演示材料、提纲或零散内容归一化为稳定的 `school-presentation-full.md` 逻辑页 Markdown，再渲染为带学校蓝绿色视觉识别的离线 HTML 演示文稿。Markdown 是可审阅的源文件；渲染器负责布局选择、图片等比缩放、物理页拆分、资产内嵌、尺寸门禁，以及单文件 preview workspace / playback / overview 交互。

## Use When

- 用户明确使用触发词 `school-presentation`。
- 用户需要生成学校正式汇报、课程展示、培训课件、招生宣讲、项目答辩或类似学校场景的演示文稿。
- 用户给出源材料、提纲、旧 PPT 内容或已有 Markdown，需要整理成可版本化、可复核、可离线打开的 HTML deck。

## Inputs

- `source_material`: 用户给出的主题、文字材料、旧 PPT 摘要、课程内容、表格、图片、视频路径或已有 Markdown。
- `output_markdown`: 持久化的逻辑页 Markdown intermediate，默认结构见 `templates/school-presentation-full.md`。
- `references/identity/`: 学校视觉识别资源，包括校名 logo、slogan、蓝绿色 palette、装饰条和来源说明。
- `media/`: 用户提供的图片、视频或图表数据。图片默认按 contain 方式放置，不裁切；超过 50 MB 输出上限的视频走外链/旁路说明。

## Process

1. 先按 `docs/markdown-normalization-contract.md` 把源材料归一化为 `YAML frontmatter + body` 的 Markdown intermediate。
2. frontmatter 使用本技能自己的 deck 元数据：
   - `template`: 固定为 `school-presentation`。
   - `title`: 演示文稿标题；封面渲染时每行最多 10 个可见字符、最多 2 行，生成时应优先提炼为 20 个中文字符以内。
   - `subtitle`: 副标题；未知时留空，建议不超过 24 个中文字符，渲染器会按 24 个可见字符截断。
   - `unit`: 可选单位字段；未知时留空，留空时封面信息栏不显示单位。不要把 `school`、`department` 或 `location` 当作封面信息栏字段。
   - `author`、`presenter`、`reporter`、`date`: 可选封面信息栏字段；未知时留空或标记复核。`author`、`presenter`、`reporter` 只会归并为一个汇报人值，封面上不再显示“汇报人”标签；`date` 只显示日期值，不再显示“时间/日期”标签。
   - `page_ratio`: 页面比例，只允许 `16:9` 或 `4:3`，默认 `16:9`；渲染器按该比例生成等尺寸物理页。
   - `max_output_mb`: 默认 `50`，用于离线 HTML 产物尺寸门禁。
3. 正文优先用 `## Section: 章节名` 表达章节边界，并在章节下用 `### Slide: 标题` 表达一个逻辑页。旧的平面 `## Slide: 标题` deck 仍然兼容，渲染器会把它们放入默认章节。逻辑页下方可放一个 `<!-- slide ... -->` 元数据块：
   - `layout`: `auto`、`cover`、`closing`、`section`、`content`、`media-right`、`media-left`、`media-center`、`media-compare`、`media-chart`、`table`、`chart` 或 `quote`。
   - `intent`: 该页的表达目的，供 agent 审阅和渲染器选择布局。
   - `split`: 默认为 `auto`，过长内容可自动拆为多个物理 HTML 页。
4. 封面只能由一个主标题、一个可省略副标题和一个固定信息栏构成。主标题每行最多 10 个中文字符、最多 2 行；副标题最多按 24 个中文字符设计；固定信息栏只允许可选单位值、汇报人值、日期值，单位字段默认不显示，只有用户填写 `unit` 时才显示，且封面不显示“单位”标签；汇报地点不再使用。不要根据用户需求额外发明“主题、班级、课程、项目背景、适用对象、指导思想、地点”等封面栏目。不要在封面逻辑页正文中追加说明段落、第二副标题、口号、项目背景、更多信息卡片或自定义 `cover_*` 字段；这些内容必须移动到封面后的第一个内容页。渲染器会忽略封面正文块，只使用 frontmatter 的 `title`、`subtitle`、`unit`、汇报人和日期，防止首页内容溢出。
5. 页面层级模型固定为 `sections -> logical_slides -> physical_pages -> reveal_steps`。渲染器会在封面后自动插入目录页，目录只读取 `## Section:` 一级章节标题，不要求 Markdown 作者手写次级页标题。目录每页最多显示 5 个章节，超过后自动拆成多个目录物理页。一个逻辑页可以自动拆成多个物理页，物理页标签使用逻辑页点号格式，例如 `3.1`、`3.2`。`reveal_steps` 记录当前物理页中的有序揭示、强调和答案遮罩步骤。
6. 逻辑页内容保持普通 Markdown：标题、段落、列表、表格、代码块、公式、图片、视频占位、图表 fenced block、强调块和 speaker notes。强调块支持 `::: info`、`::: tip`、`::: warning`、`::: error`，并兼容 GitHub alert 写法 `> [!NOTE]`、`> [!TIP]`、`> [!IMPORTANT]`、`> [!WARNING]`、`> [!CAUTION]`。
7. 课堂揭示语法保持 Markdown-first：
   - 块级揭示：`::: reveal order=1 ... :::`，可包住列表、段落、公式、图表、图片等常见块。
   - 答案遮罩：`::: mask order=1 ... :::` 或行内 `{{mask order=1}}答案{{/mask}}`；播放态遮住答案但不显示“点击揭示”等提示文字。
   - 正确项强调：`::: emphasis order=1 ... :::` 或行内 `{{emphasis order=1}}正确项{{/emphasis}}`；选择题选项常显，正确项按 order 变成强调状态。默认强调包含下划线，打印或静态审阅时仍可见。强调入场动画只在该 step 首次出现时播放，已经强调过的内容保持静态高亮，不随后续 step 重播动画。
   - `order` 是播放优先级，允许小数插入；渲染器按数值排序并在 manifest 中归一成连续 `step_index`。相同 `order` 的元素同时出现。
8. 生成 Markdown 后，运行 `skills/school-presentation/scripts/school-presentation.sh render` 输出离线 HTML。生成结果默认打开 preview workspace：左侧 thumbnail rail 按章节和逻辑页分组，右侧 preview stage 显示当前物理页的真实 slide DOM；同一个单文件 HTML 内还包含 playback 和 overview。Preview workspace 显示全内容和最终揭示状态；playback 才按 reveal step 隐藏、遮罩或强调内容。
9. slide 内部必须保持固定设计画布尺寸。不要在 slide 内容、字体、图片高度、图文栅格中使用 viewport-dependent CSS，例如 `vh`、`vw` 或基于视口的 `clamp()`；不同预览尺寸和浏览器缩放比例下，只允许外层 stage scale 改变，slide 内部元素相对关系必须像图片缩放一样保持不变。
10. playback 支持键盘方向键、Space、PageUp/PageDown、鼠标左/中/右点击区域、触摸滑动、`Esc` 返回 workspace、URL hash 当前页与 step 同步和顶部蓝绿色进度条。右方向/Space/右侧或中部点击先推进当前页 reveal step，当前页完成后才翻页；左方向/左侧点击先撤回当前页上一步。跨页切换时，旧页按当前已揭示状态淡出，新切入页面一律从 step0 原始遮罩状态开始。最后一页全部完成后继续前进会退出放映模式。
11. 运行 `verify` 可生成示例、重复渲染、比对稳定性、检查层级 manifest、workspace/playback/overview/reveal hook，并写出 verification manifest。
12. 对来源不确定、素材缺失、视频过大或内容无法稳定呈现的片段，就近写入合适级别的强调块或渲染 manifest，不要静默删除。

## Script Usage

```bash
skills/school-presentation/scripts/school-presentation.sh example \
  --output school-presentation-full.md

skills/school-presentation/scripts/school-presentation.sh render \
  --input school-presentation-full.md \
  --html school-presentation-full.html \
  --manifest school-presentation-manifest.json

skills/school-presentation/scripts/school-presentation.sh verify \
  --workdir /tmp/school-presentation-verify
```

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 读取本 `SKILL.md` 后执行流程；用 shell 调用 `scripts/school-presentation.sh`；写文件前确认目标路径，验证时运行 `verify` 并检查 manifest。 |
| Claude Code | 可把同一目录安装到 `.claude/skills/school-presentation/`；frontmatter 的 `description` 是触发入口；脚本属于显式外部命令，执行前检查路径和权限。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向本 `SKILL.md`；若无法自动发现脚本，按 `Script Usage` 手动调用。 |
| OpenCode | 使用可加载 `SKILL.md` 的 skill 路径；若走 Claude-compatible fallback，保持同一目录结构并验证脚本可执行。 |
| OpenClaw | 作为 AgentSkills-compatible 目录使用；安装时验证 frontmatter 解析、技能根目录、脚本 allowlist、sandbox 对 `references/identity/` 和媒体路径的访问。 |
| Hermes Agent | 使用 `SKILL.md` skill folder；安装时验证项目级/全局技能路径、脚本发现行为，以及是否允许读取 skill-local assets 和用户媒体。 |

## Outputs

- `school-presentation-full.md` 结构的 Markdown logical-slide intermediate。
- 单文件优先的离线 `.html` 演示文稿，默认进入 preview workspace，并内置 playback 与 overview。
- 可选 `manifest.json`，记录章节、逻辑页、物理页、`sections -> logical_slides -> physical_pages -> reveal_steps` 层级、HTML hash、产物大小、尺寸门禁和媒体 fallback。`reveal_steps` 包含连续 `step_index`、原始优先级 `priority`、交互类型和目标数量。

## Verification

- [ ] `skills/school-presentation/scripts/school-presentation.sh example --output <file>` 能输出可审阅的逻辑页 Markdown。
- [ ] `render --input <md> --html <html>` 能生成离线 HTML，并内嵌学校 logo、slogan、CSS、图表和可内嵌资产。
- [ ] `verify --workdir <dir>` 能重复渲染同一 Markdown，并证明 HTML hash 一致。
- [ ] manifest 包含 `sections -> logical_slides -> physical_pages -> reveal_steps` 层级，每个物理页带 `data-section-index`、`data-logical-index`、`data-physical-index`、`data-global-index` 和 `data-page-id` 对应信息。
- [ ] 输出 HTML 包含 preview workspace、thumbnail rail、preview stage、playback、overview、hash 同步、键盘/鼠标/触摸导航和当前页同步逻辑。
- [ ] 输出 HTML 包含有序 reveal、答案遮罩和正确项强调；preview 显示全内容和最终揭示状态，playback 按 step 控制。
- [ ] 封面只包含每行最多 10 个中文字符且最多 2 行的主标题、最多 24 个中文字符的可选副标题和固定信息栏；信息栏只显示可选单位值、汇报人值和日期值，封面正文、额外副标题、自定义 `cover_*` 信息、地点或更多内容卡片不会进入首页。
- [ ] 公式内容必须保持数学公式样式；被遮罩或揭示的公式/公式片段不能降级为普通字符。
- [ ] manifest 显示 HTML 输出小于或等于 50 MB；若视频或媒体过大，记录 fallback 而不是强行内嵌。
- [ ] 输出 deck 覆盖固定 `16:9`/`4:3` 页面比例、封面后自动目录页、公式、表格、图表、图片、视频 fallback、speaker notes、四类强调块和自动物理页拆分。
- [ ] OpenClaw 与 Hermes Agent 的运行时差异保留在 adapter notes 中，没有写入 canonical 主流程。

## Success Criteria

- 技能在触发词 `school-presentation` 下能指导 agent 产出学校风格演示文稿 Markdown intermediate。
- 脚本能从 Markdown 生成稳定、离线、蓝绿色学校视觉识别明确的 HTML deck。
- 渲染器保持图片等比 contain 放置，并能按 frontmatter 中的 `page_ratio` 把过长逻辑页拆成多个等尺寸物理 HTML 页。
- 输出 deck 能在同一个离线 HTML 中完成 preview workspace、playback 和 overview 导航，并暴露章节、逻辑页、物理页和真实 reveal-step 层级。
- 技能保持 canonical 单文件语义源，不引入 runtime-specific wrapper。

## Deferred Scope

hover/peek 指针交互、SmartArt/时间轴/卡片等结构化版式、自动语义图标、排序题重排、正文逐段动画、章节封面显示开关和导出/打印专项能力不属于 Phase 10 的 SP-14/SP-15/SP-16 最小交付；后续如需要，应单独规划需求、模板 fixture 和黑盒验证。

## Safety

- 不要静默丢弃源材料中不确定、缺失或无法表达的内容；必须就近标记复核。
- 不要虚构学校名称、校徽、教师姓名、作者、日期或用户没有暗示的事实。
- 不要把用户的大视频强行 base64 内嵌到 HTML；超过尺寸门禁时保留路径和 fallback 提示。
- 脚本只读取输入 Markdown、skill-local identity assets 和用户显式引用的相对或绝对媒体路径，并只写入用户指定的输出路径。
