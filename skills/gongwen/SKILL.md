---
name: "gongwen"
description: "Use when writing, normalizing, or rendering Chinese gongwen-style official documents such as notices, reports, and formal work arrangements."
metadata:
  short-description: "类公文 Markdown 到 Typst 工作流"
  version: "0.2.0"
  portability: "canonical"
  supported-runtimes:
    - Codex
    - Claude Code
    - Gemini CLI
    - OpenCode
    - OpenClaw
    - Hermes Agent
---

# Gongwen

## Objective

把需要呈现为类公文文体的内容归一化为稳定的 `gongwen-full.md` 结构，再通过技能自带 shell 脚本生成可编译的 Typst 文件。

## Use When

- 用户明确使用触发词 `gongwen`。
- 用户需要写类似公文文体的通知、报告、方案、工作安排、检查通报或整改要求。
- 用户需要把已有材料整理成可直接对接 Typst 公文模板的 Markdown intermediate。

## Inputs

- `source_material`: 用户给出的主题、要点、原始资料或已有 Markdown。
- `output_markdown`: 持久化的 gongwen Markdown intermediate，默认结构见 `templates/gongwen-full.md`。
- `assets/`: 图片等资源目录。Markdown 中的相对图片路径必须能从生成的 Typst 文件位置解析。

## Process

1. 先按 `docs/markdown-normalization-contract.md` 把源材料归一化为 `YAML frontmatter + body` 的 Markdown intermediate。
2. 使用以下 frontmatter 字段：
   - `title`: 公文标题；如需标题中手动换行，用 `|` 标记断点。
   - `author`: 发文单位；可为字符串或字符串数组。
   - `date`: `YYYY-MM-DD` 格式日期。
   - `signature`: 是否启用签名信息。
   - `template`: 固定为 `gongwen`。
3. 正文使用可审阅的 Markdown 表达结构：标题、段落、有序/无序列表、表格、代码块、引用、图片和图组。
4. 对公文模板特有的控制语法保持显式、局部、可审阅：
   - `::: {.noindent}` 表示无首行缩进块。
   - `{.indent}`、`{.bold}` 表示局部排版属性。
   - `{.br:N}` 表示插入 N 个换行。
   - `{pagebreak}` 或 `{pagebreak:weak}` 表示分页。
   - Markdown 表格后的 `: 表题` 表示表格题名。
   - 同一段内多张图片且 alt 相同表示一组子图。
5. 生成 Markdown 后，运行 `skills/gongwen/scripts/gongwen.sh render` 生成 `.typ`；该 Markdown 到 Typst 转换由脚本内置 shell 逻辑完成，不依赖外部模板二进制、Pandoc、Python、Node、Typst 或其他转换器。
6. 若有参考 Typst，使用脚本的 `--expected-typ` 进行黑盒一致性验证。

## Script Usage

```bash
skills/gongwen/scripts/gongwen.sh example --output gongwen-full.md

skills/gongwen/scripts/gongwen.sh render \
  --input gongwen-full.md \
  --typ gongwen-full.typ
```

带参考产物验证：

```bash
skills/gongwen/scripts/gongwen.sh render \
  --input /path/to/gongwen-full.md \
  --typ /path/to/gongwen-full.typ \
  --expected-typ /path/to/reference.typ
```

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 读取本 `SKILL.md` 后执行流程；用 shell 调用 `scripts/gongwen.sh`；写文件前确认目标路径；PDF 编译若需要，必须在脚本外单独执行。 |
| Claude Code | 可把同一目录安装到 `.claude/skills/gongwen/`；frontmatter 的 `description` 是触发入口；脚本属于显式外部命令，执行前检查路径和权限。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向本 `SKILL.md`；若无法自动发现脚本，按 `Script Usage` 手动调用。 |
| OpenCode | 使用可加载 `SKILL.md` 的 skill 路径；若走 Claude-compatible fallback，保持同一目录结构并验证脚本可执行。 |
| OpenClaw | 作为 AgentSkills-compatible 目录使用；安装时验证 frontmatter 解析、技能根目录、脚本 allowlist 和 shell 脚本执行权限。 |
| Hermes Agent | 使用 `SKILL.md` skill folder；安装时验证项目级/全局技能路径、脚本发现行为和 shell 脚本执行权限。 |

## Outputs

- `gongwen-full.md` 结构的 Markdown intermediate。
- 由 `scripts/gongwen.sh` 内置 shell 渲染器生成的 `.typ` 文件。

## Verification

- [ ] `skills/gongwen/scripts/gongwen.sh example --output <file>` 能输出可审阅的 `gongwen-full.md` 结构。
- [ ] `skills/gongwen/scripts/gongwen.sh render --input <md> --typ <typ>` 能不依赖任何外部转换器生成 Typst。
- [ ] 对给定 fixture 运行 `--expected-typ` 时，生成 Typst 与参考文件一致。
- [ ] OpenClaw 与 Hermes Agent 的运行时差异保留在 adapter notes 中，没有写入 canonical 主流程。

## Success Criteria

- 技能在触发词 `gongwen` 下能指导 agent 产出类公文 Markdown intermediate。
- 脚本能从 `gongwen-full.md` 生成稳定 Typst，且转换效果与参考黑盒 Typst 一致。
- 技能保持 canonical 单文件语义源，不引入 runtime-specific wrapper。

## Safety

- 不要静默删除源材料中不确定、缺失或无法表达的内容；必须就近标记复核。
- 不要把凭据、私有路径或用户专属资源写入正文，除非用户明确要求。
- 脚本的 Markdown 到 Typst 转换不得调用外部模板二进制、Pandoc、Python、Node、Typst 或其他外部命令。
- 脚本只读取输入 Markdown，并只写入用户指定的 Typst 输出路径；输出路径的父目录必须已存在。
