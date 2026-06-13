---
name: "jiaoan-shicao"
description: "Use when writing, normalizing, or rendering hands-on lesson plans, practical training lesson plans, vocational education teaching activity designs, or project-based teaching units in the jiaoan-shicao Markdown-to-Typst workflow."
metadata:
  short-description: "实操教案 Markdown 到 Typst 工作流"
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

# Jiaoan Shicao

## Objective

把课程内容、实训安排、教学活动设计或项目化教学单元归一化为稳定的 `jiaoan-shicao-full.md` Markdown intermediate，再通过技能自带 shell 脚本生成可编译 Typst。

## Use When

- 用户明确使用触发词 `jiaoan-shicao`。
- 用户需要写实操教案、实训教案、职业教育教案、课程教案表、教学活动设计或项目化教学单元。
- 用户需要把已有课程材料整理成可直接对接 Typst 实操教案模板的 Markdown intermediate。

## Inputs

- `source_material`: 用户给出的课程资料、实训任务、教学目标、活动安排、评价要求或已有 Markdown。
- `output_markdown`: 持久化的 `jiaoan-shicao-full.md` 风格 Markdown intermediate，默认结构见 `templates/jiaoan-shicao-full.md`。
- `calendar_json`: 支持资源，默认见 `references/calendar.json`；用于核对授课日期、排课顺序或维护旧材料中的日历语义。
- `references/format-and-rendering.md`: frontmatter 字段、三段式正文结构、完整性规则、渲染约束和详细验证规则。

## Process

1. 按 `docs/markdown-normalization-contract.md` 把源材料归一化为 `YAML frontmatter + body` 的 Markdown intermediate。
2. 按 `references/format-and-rendering.md` 填写 frontmatter、学习任务分析、教学活动设计和学业评价结构。
3. 材料不足时仍输出完整骨架；不确定字段留空或就近标记复核，不要虚构。
4. 运行 `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render` 生成 `.typ`。
5. 若有参考 Typst，使用 `--expected-typ` 作为严格一致性 gate。

## Script Usage

```bash
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example \
  --output jiaoan-shicao-full.md \
  --calendar-output calendar.json

skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input jiaoan-shicao-full.md \
  --typ jiaoan-shicao-full.typ
```

带参考产物验证：

```bash
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input /path/to/jiaoan-shicao-full.md \
  --typ /path/to/jiaoan-shicao-full.typ \
  --expected-typ /path/to/reference.typ
```

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 读取本 `SKILL.md` 和 `references/format-and-rendering.md` 后执行流程；用 shell 调用 `scripts/jiaoan-shicao.sh`；写文件前确认目标路径；PDF 编译若需要，必须在脚本外单独执行。 |
| Claude Code | 可把同一目录安装到 `.claude/skills/jiaoan-shicao/`；frontmatter 的 `description` 是触发入口；脚本属于显式外部命令，执行前检查路径和权限。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向本 `SKILL.md`；若无法自动发现脚本，按 `Script Usage` 手动调用，并读取 `references/` 中的长规则。 |
| OpenCode | 使用可加载 `SKILL.md` 的 skill 路径；若走 Claude-compatible fallback，保持同一目录结构并验证 `references/`、脚本和 `calendar.json` 可读。 |
| OpenClaw | 作为 AgentSkills-compatible 目录使用；安装时验证 frontmatter 解析、技能根目录、脚本 allowlist、shell 脚本执行权限和 `calendar.json` 支持资源。 |
| Hermes Agent | 使用 `SKILL.md` skill folder；安装时验证项目级/全局技能路径、reference/script 发现行为、shell 脚本执行权限和支持资源。 |

## Outputs

- `jiaoan-shicao-full.md` 结构的 Markdown intermediate。
- 由 `scripts/jiaoan-shicao.sh` 内置 shell 渲染器生成的 `.typ` 文件。
- 可选复制出的 `calendar.json` 支持资源。

## Verification

- [ ] `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example --output <file>` 能输出可审阅的 `jiaoan-shicao-full.md` 结构。
- [ ] `--calendar-output <file>` 能复制随技能提供的 `calendar.json` 支持资源。
- [ ] `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --input <md> --typ <typ>` 能生成 Typst。
- [ ] 对 v1.10 给定教案 fixture 运行 `--expected-typ` 时，生成 Typst 与参考文件严格一致。
- [ ] OpenClaw 与 Hermes Agent 的运行时差异保留在 adapter notes 中，没有写入 canonical 主流程。

## Success Criteria

- 技能在触发词 `jiaoan-shicao` 下能指导 agent 产出完整实操教案 Markdown intermediate。
- 脚本能从 `jiaoan-shicao-full.md` 生成稳定 Typst。
- 长格式规则和 renderer notes 位于 `references/format-and-rendering.md`，入口保持清晰可读。
- 技能保持 canonical 单文件语义源，不引入 runtime-specific wrapper。

## Safety

- 不要静默删除源材料中不确定、缺失或无法表达的内容；必须就近标记复核或留空。
- 不要虚构学校名称、教师姓名、教学班级、教材版本、授课日期或用户没有暗示的评价结论。
- 脚本的 Markdown 到 Typst 转换不得调用外部模板二进制、PDF 编译器或任何其他外部可执行文件。
- 脚本的 v1.10 fixture-backed 路径只读取输入 Markdown 并写入用户指定的 Typst 输出；参考 `.typ` 只能由 `--expected-typ` 比较 gate 读取。
