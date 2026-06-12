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
- `references/authoring-and-layout.md`: frontmatter、章节/逻辑页结构、封面规则、结构化版式、固定画布和 Markdown authoring 规则。
- `references/playback-and-export.md`: preview workspace、playback、presenter markup 和最终 PDF export 行为。
- `references/verification-contract.md`: verify command、manifest booleans、HTML/PDF verification coverage 和 UAT 检查点。

## Process

1. 按 `docs/markdown-normalization-contract.md` 把源材料归一化为 `YAML frontmatter + body` 的 Markdown intermediate。
2. 按 `references/authoring-and-layout.md` 写 deck metadata、章节、逻辑页、slide 注释、版式语法、封面和固定画布内容。
3. 保持页面层级模型为 `sections -> logical_slides -> physical_pages -> reveal_steps`；逻辑页过长时由渲染器拆为多个物理页。
4. 课堂揭示、答案遮罩、正确项强调、peek、排序、timeline、cards、gallery、smartart、语义图标和 section divider 使用 reference 中的 Markdown-first 语法，不写 raw HTML。
5. 运行 `skills/school-presentation/scripts/school-presentation.sh render` 输出离线 HTML；生成 deck 的 preview/playback/export 行为见 `references/playback-and-export.md`。
6. 运行 `verify --workdir <dir>`，并按 `references/verification-contract.md` 检查 manifest、固定比例、单文件边界、结构化语义和 PDF/export tokens。
7. 对来源不确定、素材缺失、视频过大或内容无法稳定呈现的片段，就近写入合适级别的强调块或渲染 manifest，不要静默删除。

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
| Codex | 读取本 `SKILL.md` 和 `references/authoring-and-layout.md`、`references/playback-and-export.md`、`references/verification-contract.md` 后执行流程；用 shell 调用 `scripts/school-presentation.sh`；写文件前确认目标路径，验证时运行 `verify` 并检查 manifest。 |
| Claude Code | 可把同一目录安装到 `.claude/skills/school-presentation/`；frontmatter 的 `description` 是触发入口；脚本属于显式外部命令，执行前检查路径和权限。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向本 `SKILL.md`；若无法自动发现脚本，按 `Script Usage` 手动调用，并读取 `references/` 中的长规则。 |
| OpenCode | 使用可加载 `SKILL.md` 的 skill 路径；若走 Claude-compatible fallback，保持同一目录结构并验证 `references/`、identity assets、脚本和媒体路径可读。 |
| OpenClaw | 作为 AgentSkills-compatible 目录使用；安装时验证 frontmatter 解析、技能根目录、reference 读取、脚本 allowlist、sandbox 对 `references/identity/` 和媒体路径的访问。 |
| Hermes Agent | 使用 `SKILL.md` skill folder；安装时验证项目级/全局技能路径、reference/script 发现行为，以及是否允许读取 skill-local assets 和用户媒体。 |

## Outputs

- `school-presentation-full.md` 结构的 Markdown logical-slide intermediate。
- 单文件优先的离线 `.html` 演示文稿，默认进入 preview workspace，并内置 playback 与 overview。
- 可选 `manifest.json`，记录章节、逻辑页、物理页、reveal steps、HTML hash、产物大小、尺寸门禁和媒体 fallback。
- 一键最终 PDF export 行为、outline/link 规则和 runtime-state 排除规则见 `references/playback-and-export.md`。

## Verification

- [ ] `skills/school-presentation/scripts/school-presentation.sh example --output <file>` 能输出可审阅的逻辑页 Markdown。
- [ ] `render --input <md> --html <html>` 能生成离线 HTML，并内嵌学校 logo、slogan、CSS、图表和可内嵌资产。
- [ ] `verify --workdir <dir>` 能重复渲染同一 Markdown，并证明 HTML hash 一致。
- [ ] Manifest、preview/playback/overview、reveal/mask/emphasis、structured layout、presenter markup、print/export、fixed ratio 和 offline single-file 检查符合 `references/verification-contract.md`。
- [ ] OpenClaw 与 Hermes Agent 的运行时差异保留在 adapter notes 中，没有写入 canonical 主流程。

## Success Criteria

- 技能在触发词 `school-presentation` 下能指导 agent 产出学校风格演示文稿 Markdown intermediate。
- 脚本能从 Markdown 生成稳定、离线、蓝绿色学校视觉识别明确的 HTML deck。
- 渲染器保持图片等比 contain 放置，并能按 frontmatter 中的 `page_ratio` 把过长逻辑页拆成多个等尺寸物理 HTML 页。
- 输出 deck 能在同一个离线 HTML 中完成 preview workspace、playback、overview 导航、playback-local presenter markup 和一键最终 PDF 导出，并暴露章节、逻辑页、物理页和真实 reveal-step 层级。
- 长 authoring、layout、playback/export 和 verification 细节位于 `references/`，入口保持清晰可读。
- 技能保持 canonical 单文件语义源，不引入 runtime-specific wrapper。

## Deferred Scope

PPTX、Keynote、可编辑 PowerPoint、系统打印生产回路、自动浏览器截图 gate、托管分享、多人同步、远程互动、拖拽排序、持久保存标注和 annotation flattening 不属于当前交付；后续如需要，应单独规划需求、模板 fixture 和黑盒验证。

## Safety

- 不要静默丢弃源材料中不确定、缺失或无法表达的内容；必须就近标记复核。
- 不要虚构学校名称、校徽、教师姓名、作者、日期或用户没有暗示的事实。
- 不要把用户的大视频强行 base64 内嵌到 HTML；超过尺寸门禁时保留路径和 fallback 提示。
- 脚本只读取输入 Markdown、skill-local identity assets 和用户显式引用的相对或绝对媒体路径，并只写入用户指定的输出路径。
