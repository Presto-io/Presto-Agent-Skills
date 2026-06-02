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
   - `title`: 演示文稿标题。
   - `subtitle`: 副标题；未知时留空。
   - `school`: 学校或院系名称；默认使用 identity 资源中的学校识别。
   - `department`、`author`、`presenter`、`reporter`、`date`、`location`: 封面信息；未知时留空或标记复核。
   - `cover_*`: 其他封面选填项，例如 `cover_location`、`cover_topic`、`cover_class`；渲染器会自动放入封面信息区。
   - `page_ratio`: 页面比例，只允许 `16:9` 或 `4:3`，默认 `16:9`；渲染器按该比例生成等尺寸物理页。
   - `max_output_mb`: 默认 `50`，用于离线 HTML 产物尺寸门禁。
3. 正文优先用 `## Section: 章节名` 表达章节边界，并在章节下用 `### Slide: 标题` 表达一个逻辑页。旧的平面 `## Slide: 标题` deck 仍然兼容，渲染器会把它们放入默认章节。逻辑页下方可放一个 `<!-- slide ... -->` 元数据块：
   - `layout`: `auto`、`cover`、`closing`、`section`、`content`、`media-right`、`media-left`、`media-center`、`media-compare`、`media-chart`、`table`、`chart` 或 `quote`。
   - `intent`: 该页的表达目的，供 agent 审阅和渲染器选择布局。
   - `split`: 默认为 `auto`，过长内容可自动拆为多个物理 HTML 页。
4. 页面层级模型固定为 `sections -> logical_slides -> physical_pages -> reveal_steps`。渲染器会在封面后自动插入目录页，目录只读取 `## Section:` 一级章节标题，不要求 Markdown 作者手写次级页标题。一个逻辑页可以自动拆成多个物理页，物理页标签使用逻辑页点号格式，例如 `3.1`、`3.2`。Phase 9 中 `reveal_steps` 是稳定空数组占位，供 Phase 10 的有序揭示、强调动画和答案遮罩继续扩展。
5. 逻辑页内容保持普通 Markdown：标题、段落、列表、表格、代码块、公式、图片、视频占位、图表 fenced block、强调块和 speaker notes。强调块支持 `::: info`、`::: tip`、`::: warning`、`::: error`，并兼容 GitHub alert 写法 `> [!NOTE]`、`> [!TIP]`、`> [!IMPORTANT]`、`> [!WARNING]`、`> [!CAUTION]`。
6. 生成 Markdown 后，运行 `skills/school-presentation/scripts/school-presentation.sh render` 输出离线 HTML。生成结果默认打开 preview workspace：左侧 thumbnail rail 按章节和逻辑页分组，右侧 preview stage 显示当前物理页的真实 slide DOM；同一个单文件 HTML 内还包含 playback 和 overview。
7. slide 内部必须保持固定设计画布尺寸。不要在 slide 内容、字体、图片高度、图文栅格中使用 viewport-dependent CSS，例如 `vh`、`vw` 或基于视口的 `clamp()`；不同预览尺寸和浏览器缩放比例下，只允许外层 stage scale 改变，slide 内部元素相对关系必须像图片缩放一样保持不变。
8. playback 支持键盘方向键、Space、PageUp/PageDown、鼠标左/中/右点击区域、触摸滑动、`Esc` 返回 workspace、URL hash 当前页同步和顶部蓝绿色进度条。overview 是 section-aware tiled overview，可直接选择物理页并返回 workspace。
9. 运行 `verify` 可生成示例、重复渲染、比对稳定性、检查层级 manifest、workspace/playback/overview hook，并写出 verification manifest。
10. 对来源不确定、素材缺失、视频过大或内容无法稳定呈现的片段，就近写入合适级别的强调块或渲染 manifest，不要静默删除。

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
- 可选 `manifest.json`，记录章节、逻辑页、物理页、`sections -> logical_slides -> physical_pages -> reveal_steps` 层级、HTML hash、产物大小、尺寸门禁和媒体 fallback。

## Verification

- [ ] `skills/school-presentation/scripts/school-presentation.sh example --output <file>` 能输出可审阅的逻辑页 Markdown。
- [ ] `render --input <md> --html <html>` 能生成离线 HTML，并内嵌学校 logo、slogan、CSS、图表和可内嵌资产。
- [ ] `verify --workdir <dir>` 能重复渲染同一 Markdown，并证明 HTML hash 一致。
- [ ] manifest 包含 `sections -> logical_slides -> physical_pages -> reveal_steps` 层级，每个物理页带 `data-section-index`、`data-logical-index`、`data-physical-index`、`data-global-index` 和 `data-page-id` 对应信息。
- [ ] 输出 HTML 包含 preview workspace、thumbnail rail、preview stage、playback、overview、hash 同步、键盘/鼠标/触摸导航和当前页同步逻辑。
- [ ] manifest 显示 HTML 输出小于或等于 50 MB；若视频或媒体过大，记录 fallback 而不是强行内嵌。
- [ ] 输出 deck 覆盖固定 `16:9`/`4:3` 页面比例、封面后自动目录页、公式、表格、图表、图片、视频 fallback、speaker notes、四类强调块和自动物理页拆分。
- [ ] OpenClaw 与 Hermes Agent 的运行时差异保留在 adapter notes 中，没有写入 canonical 主流程。

## Success Criteria

- 技能在触发词 `school-presentation` 下能指导 agent 产出学校风格演示文稿 Markdown intermediate。
- 脚本能从 Markdown 生成稳定、离线、蓝绿色学校视觉识别明确的 HTML deck。
- 渲染器保持图片等比 contain 放置，并能按 frontmatter 中的 `page_ratio` 把过长逻辑页拆成多个等尺寸物理 HTML 页。
- 输出 deck 能在同一个离线 HTML 中完成 preview workspace、playback 和 overview 导航，并暴露章节、逻辑页、物理页和 reveal-step 占位层级。
- 技能保持 canonical 单文件语义源，不引入 runtime-specific wrapper。

## Phase 10 Boundary

有序 reveal、内容强调动画和课堂答案遮罩属于 Phase 10。Phase 9 只提供 `reveal_steps` 空数组占位和页面级导航；不要在 Phase 9 文档或实现中宣称这些课堂交互已经完成。

## Safety

- 不要静默丢弃源材料中不确定、缺失或无法表达的内容；必须就近标记复核。
- 不要虚构学校名称、校徽、教师姓名、作者、日期或用户没有暗示的事实。
- 不要把用户的大视频强行 base64 内嵌到 HTML；超过尺寸门禁时保留路径和 fallback 提示。
- 脚本只读取输入 Markdown、skill-local identity assets 和用户显式引用的相对或绝对媒体路径，并只写入用户指定的输出路径。
