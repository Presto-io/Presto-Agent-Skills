---
name: "tiaokedan"
description: "Use when gathering, drafting, reviewing, or rendering a Chinese 调课单/调课说明 adjustment form from teacher facts through tiaokedan.md, generated Typst, and optional final PDF."
metadata:
  short-description: "调课单 Markdown 到 Typst/PDF 工作流"
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

# Tiaokedan

## Objective

把教师提供的调课事实整理成可审阅的 `tiaokedan.md`，由教师确认后，再用本技能自己的脚本生成稳定 Typst，并在安装 `typst` CLI 时生成最终 PDF。

## Use When

- 用户要写、补全、审阅或生成 `调课单`、`调课说明`、课程调整说明等单张调课表单。
- 用户已经有调课事实，需要先生成教师可编辑 Markdown，再输出 Typst/PDF。
- 用户需要确认调课原因、原安排、调整后安排、涉及教师、落款部门和日期是否完整。

## Inputs

- `source_facts`: 教师给出的调课原因、班级、课程、原上课时间/教师、调整后时间/教师、部门、日期和可选备注。
- `templates/tiaokedan.md`: 教师可读 Markdown 样板，也是默认 fixture。
- `references/markdown-contract.md`: 必填字段、可选 `备注`、复核标记和 renderer-owned defaults。
- `references/pdf-workflow.md`: PDF gate、干净输出、隐藏 `.tiaokedan/` 诊断和验证命令。
- `scripts/tiaokedan.sh`: finalized Markdown 的 Typst/PDF 渲染命令。

## Teacher Workflow

1. 收集教师提供的调课事实，先从材料中抽取答案。
2. 只对缺失、冲突或会影响最终表单可信度的事实提问。
3. 生成或更新 `tiaokedan.md`，保持 `YAML frontmatter + body` 可直接审阅。
4. 暂停让教师审阅、改写、补充或确认；`tiaokedan.md` 是 source of truth。
5. 定稿前允许在 Markdown 中保留 `{{待补充: ...}}` 或 `{{AI草稿: ...}}` 标记。
6. 只有必填事实完整且教师确认后，才运行脚本生成 Typst/PDF。

`title`、`recipient`、表格 `序号` 列和表格后的落款行都可以省略；renderer 会使用默认标题 `调课说明`、默认收文对象 `教务处：`、自动序号，以及 frontmatter 中的 `department`/`date`。标题样式由 renderer 控制，当前生成 Typst 使用 `Songti SC` 优先的宋体族和 `weight: 700`，不要求教师在 Markdown 中维护字体。

## Missing Information Questions

按教师语言集中提问，不要求教师理解 renderer 配置：

- 调课原因：这次调课的原因和说明段落应如何表述？
- 涉及班级和课程：涉及哪些班级、课程和调课行？
- 原上课安排：每行原上课时间、地点和原授课教师是什么？
- 调整后安排：每行调整后的上课时间、地点和授课教师是什么？
- 涉及教师：原教师和调整后教师是否都已确认？
- 落款部门和日期：落款部门、落款日期分别是什么？
- 可选备注：只有教师表示需要备注时才询问；空白 `备注` 是允许的。

必填事实未知时，在草稿 Markdown 对应位置写 `{{待补充: 说明}}`。AI 起草但需要教师确认的正文可以写 `{{AI草稿: 说明}}`。最终 Typst/PDF 渲染会阻塞未解决的 `{{待补充: ...}}` 或 `{{AI草稿: ...}}` 标记。

不要向教师询问 A4 横向、标题宋体加粗、字体 fallback、字号、表格宽度、Typst helper、诊断目录、比较命令等 renderer-owned defaults。

## Finalized Markdown Render/PDF Commands

```bash
skills/tiaokedan/scripts/tiaokedan.sh render \
  --input skills/tiaokedan/templates/tiaokedan.md \
  --typ build/tiaokedan/tiaokedan.typ

skills/tiaokedan/scripts/tiaokedan.sh render \
  --input skills/tiaokedan/templates/tiaokedan.md \
  --typ build/tiaokedan/tiaokedan.typ \
  --pdf build/tiaokedan/tiaokedan.pdf
```

`--expected-typ` 仅用于临时回归或阶段证据；普通教师表单不需要和示例 Typst 逐字节一致，仓库也不要求保留 `.typ` fixture。

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 读取项目 `AGENTS.md`、本 `SKILL.md`、`references/`、`templates/` 和 `scripts/`；保持整个 skill folder 同步；教师确认 `tiaokedan.md` 后用 shell 调用 `scripts/tiaokedan.sh`，需要 PDF 时确认 `typst` 和写入权限。 |
| Claude Code | 可把同一整个 skill folder 安装到 `.claude/skills/tiaokedan/`，保留 `SKILL.md`、`references/`、`templates/` 和 `scripts/`；frontmatter `description` 触发后渐进读取支持文件，脚本执行前检查权限。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向本 `SKILL.md`；如果不能自动发现技能，显式读取整个 skill folder 的 `SKILL.md`、`references/`、`templates/` 和 `scripts/`，再按命令手动渲染。 |
| OpenCode | 使用可加载 `SKILL.md` 的 native skill path，或记录 Claude-compatible fallback；安装时保留整个 skill folder，并验证 `references/`、`templates/`、`scripts/` 可读且脚本可执行。 |
| OpenClaw | 作为 AgentSkills-compatible folder 使用；安装时验证 frontmatter 解析、support-file discovery、`SKILL.md`/`references/`/`templates/`/`scripts/` 完整性、脚本执行权限、`python3`、`typst`、sandbox 写权限和隐藏 `.tiaokedan/` 诊断目录行为。 |
| Hermes Agent | 使用 Hermes Agent 可发现的 `SKILL.md` skill folder；安装时验证项目/全局加载路径、support-file discovery、`SKILL.md`/`references/`/`templates/`/`scripts/` 完整性、执行权限、`python3`、`typst`、sandbox 写权限和隐藏 `.tiaokedan/` 诊断目录行为。 |

## Outputs

- `tiaokedan.md`: 教师可编辑的 Markdown source of truth。
- `tiaokedan.typ`: 脚本从 finalized Markdown 生成的 Typst。
- `tiaokedan.pdf`: 只有 `typst compile` 成功且 PDF 非空时才算最终 PDF。

成功路径只写调用方显式指定的 `.typ` 和 `.pdf`。debug 或 failure diagnostics 必须留在隐藏 `.tiaokedan/`，不得混入教师默认交付文件。

## Verification

- [ ] `python3 -m py_compile skills/tiaokedan/scripts/tiaokedan_renderer.py`
- [ ] `skills/tiaokedan/scripts/tiaokedan.sh --help` 显示 `--pdf`。
- [ ] `scripts/tiaokedan.sh render --input <md> --typ <typ>` 生成 Typst。
- [ ] `scripts/tiaokedan.sh render --input <md> --typ <typ> --pdf <pdf>` 在安装 `typst` 时生成非空 PDF。
- [ ] 成功公开目录不包含 status、manifest、log、diff、debug、json、tmp 或 diagnostic 文件。
- [ ] OpenClaw 与 Hermes Agent 的差异只在 adapter notes 中，没有进入 canonical 主流程。

## Safety

- 不要跳过教师审阅，直接从零散事实声称 PDF 最终通过。
- 不要在必填事实存在 `{{待补充: ...}}` 或 `{{AI草稿: ...}}` 时生成最终 Typst/PDF。
- 不要修改 Phase 37/38/39 已接受的 form surface、Markdown contract 或 renderer parsing scope，除非后续 phase 明确打开。
- 不要加入 school variants、batch generation、spreadsheet import、OCR/photo extraction、approval grids、signature boxes 或 opinion columns。
- 不要调用 sibling skill scripts；运行时只依赖本 `tiaokedan` skill folder、`python3` 和可选 `typst`。
