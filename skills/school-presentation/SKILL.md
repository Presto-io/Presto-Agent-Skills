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
- `output_markdown`: 持久化、已审阅的逻辑页 Markdown current，默认结构见 `templates/school-presentation-full.md`。
- `references/identity/`: 学校视觉识别资源，包括校名 logo、slogan、蓝绿色 palette、装饰条和来源说明。
- `assets/`: 当前 Markdown 持续引用且已确认纳管的图片或视频；只复制明确引用项。legacy `media/` 必须经过只读审计与明确确认，迁移时同步改写并验证引用，normal render 不静默移动。
- `references/authoring-and-layout.md`: frontmatter、章节/逻辑页结构、封面规则、结构化版式、固定画布和 Markdown authoring 规则。
- `references/playback-and-export.md`: preview workspace、playback、presenter markup 和最终 PDF export 行为。
- `references/verification-contract.md`: verify command、manifest booleans、HTML/PDF verification coverage 和 UAT 检查点。

## Process

1. 按 `docs/markdown-normalization-contract.md` 把源材料归一化为 `YAML frontmatter + body` 的 Markdown intermediate。
2. 按 `references/authoring-and-layout.md` 写 deck metadata、章节、逻辑页、slide 注释、版式语法、封面和固定画布内容。
3. 保持页面层级模型为 `sections -> logical_slides -> physical_pages -> reveal_steps`；逻辑页过长时由渲染器拆为多个物理页。
4. 课堂揭示、答案遮罩、正确项强调、peek、排序、timeline、cards、gallery、smartart、语义图标和 section divider 使用 reference 中的 Markdown-first 语法，不写 raw HTML。
5. 运行 `skills/school-presentation/scripts/school-presentation.sh render`；完整 Markdown+offline HTML 先在同根 `.work/<run-id>/candidate/` 通过 size/offline/DOM/assets gate，再发布为 current pair。
6. 运行 `verify --workdir <非交付目录>`，并按 `references/verification-contract.md` 检查 manifest、固定比例、单文件边界、结构化语义和 PDF/export tokens；manifest 与 verification evidence 不进入 delivery root。
7. 对来源不确定、素材缺失、视频过大或内容无法稳定呈现的片段，就近写入合适级别的强调块或渲染 manifest，不要静默删除。

## Script Usage

```bash
skills/school-presentation/scripts/school-presentation.sh example \
  --output school-presentation-full.md

skills/school-presentation/scripts/school-presentation.sh render \
  --input school-presentation-full.md \
  --html school-presentation-full.html \
  --manifest /tmp/school-presentation-evidence/manifest.json

skills/school-presentation/scripts/school-presentation.sh verify \
  --workdir /tmp/school-presentation-verify
```

## Runtime Adapter Notes

| Runtime | Whole-folder discovery 与显式 fallback | 外部命令、权限与边界 |
|---------|--------------------------------------|----------------------|
| Codex | 安装完整 skill folder；若自动发现不可用，显式 shell 调用 `scripts/school-presentation.sh` 并读取 `references/`、identity assets。 | 允许执行 Bash/Python、读取输入与 `assets/`、写 delivery root/`.work`；browser/PDF 命令只在人工 export 或 `bookmark-pdf` evidence 流程启用，verify 写独立 workdir。 |
| Claude Code | 安装完整目录到技能路径；保留同一显式 shell fallback，不复制单独 `SKILL.md`。 | 在 execute/read/write 与 sandbox/allowlist 中授权脚本、Python、identity assets、delivery root/`.work` 和独立 verify workdir；PDF postprocess 不扩展 current set。 |
| Gemini CLI | 由项目上下文发现完整目录；发现失败时按 `Script Usage` 显式调用 shell，并读取支持文件。 | 显式批准 Bash/Python 与可选 browser/PDF 外部命令；读输入/assets，写 delivery root/`.work` 与非交付 verify workdir。 |
| OpenCode | 使用可加载的完整 skill folder；Claude-compatible 路径只作发现 fallback，仍验证 scripts/references/assets identity。 | allowlist 必须覆盖 shell/Python execute、输入 read、delivery/.work write；manifest、浏览器导出和 bookmark evidence 只能写独立 workdir。 |
| OpenClaw | AgentSkills-compatible whole-folder 支持仅作 installation-time verified 声明；自动发现不确定时使用显式 shell fallback。 | 安装时验证 frontmatter、support discovery、Bash/Python execute、sandbox/allowlist 的 read/write；delivery root/.work 与 verify workdir 分权，browser/PDF 命令另行授权。 |
| Hermes Agent | 项目级/全局 whole-folder 路径与支持文件发现仅作 installation-time verified 声明；保留显式脚本 fallback。 | 安装时验证 shell/Python execute、输入/assets read、delivery/.work write、独立 verify workdir 和可选 browser/PDF 权限，不假定 runtime wrapper。 |

## Outputs

- Normal current 是同 stem 的 reviewed Markdown + 单文件 offline HTML pair；根一级仅允许该 pair 与按需 `sources/`、`assets/`、`history/`、`.work/`。
- `--manifest` 是显式独立 evidence，`verify --workdir` 是 caller-owned verification evidence；二者都不得位于 normal delivery root。
- HTML 内的一键 PDF export 与 `bookmark-pdf` 是浏览器/后处理边界，不把打印或 bookmarked PDF 默认加入 current。
- changed 发布把旧 pair 和旧 Markdown 所需 assets 归入同一 `history/<max+1>/`；identical 不 touch current、不建 history，handled failure/INT/TERM 回滚并清理 owned work。

## Verification

- [ ] `skills/school-presentation/scripts/school-presentation.sh example --output <file>` 能输出可审阅的逻辑页 Markdown。
- [ ] `render --input <md> --html <html>` 能生成离线 HTML，并内嵌学校 logo、slogan、CSS、图表和可内嵌资产。
- [ ] current root 没有 manifest、verification-manifest、截图、diff、日志、failed HTML 或 browser-printed PDF；history 内的旧 assets 引用仍可解析。
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
- 脚本只读取输入 Markdown、skill-local identity assets 和用户显式引用的 `assets/`/绝对可选媒体；normal render 不修改 `sources/`，不静默迁移 legacy `media/`。
- unknown、partial、symlink、manifest-in-root、legacy media 和 unrelated stale `.work` 在 mutation 前失败关闭，交由 snapshot-bound 确认式整理。
- `os.replace` 只提供单路径原子替换；保证范围是 candidate isolation 与 handled failure/INT/TERM rollback，不声称 SIGKILL、断电或跨文件硬原子。
