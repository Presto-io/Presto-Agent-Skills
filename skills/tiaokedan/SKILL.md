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
- `references/pdf-workflow.md`: exact bundle、candidate/PDF gate、history、rollback 和验证命令。
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

`--typ` 决定交付根和稳定 stem；`--pdf` 如存在，必须与 `--typ` 同 root、同 stem。只生成 Typst 时 current exact set 是 `<stem>.md + <stem>.typ`；请求 PDF 时是 `<stem>.md + <stem>.typ + <stem>.pdf`。

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 整体安装并读取 `SKILL.md`、`references/`、`templates/`、`scripts/`；显式 fallback 是执行 `scripts/tiaokedan.sh`。允许 Bash/Python 执行、读取输入，并写授权 delivery root 与同根 `.work`；PDF 另需 `typst`。 |
| Claude Code | 整体安装到可发现 skill path；若 discovery 不可用，显式执行 `scripts/tiaokedan.sh`。授予 Bash/Python、输入读取、delivery root/`.work` 写入权限，PDF 另需 `typst`。 |
| Gemini CLI | 由 `GEMINI.md` 或项目上下文指向完整 skill folder；显式 fallback 是 `scripts/tiaokedan.sh`。sandbox/allowlist 必须允许 Bash/Python、输入读取、delivery root/`.work` 写入，PDF 另需 `typst`。 |
| OpenCode | 使用 native skill path 并保留全部支持文件；无法自动发现时显式执行 `scripts/tiaokedan.sh`。allowlist 必须覆盖 Bash/Python、输入读取、delivery root/`.work` 写入，PDF 另需 `typst`。 |
| OpenClaw | whole-folder 支持、frontmatter、support-file discovery 和路径行为均须 installation-time verified；始终保留 `scripts/tiaokedan.sh` 显式 fallback，并验证 Bash/Python、可选 `typst`、sandbox/allowlist 与 delivery root/`.work` 权限。 |
| Hermes Agent | whole-folder 项目/全局加载、support-file discovery 和权限模型均须 installation-time verified；始终保留 `scripts/tiaokedan.sh` 显式 fallback，并验证 Bash/Python、可选 `typst`、输入读取及 delivery root/`.work` 写入。 |

## Outputs

- `<stem>.md`: 与本次 finalized 输入逐字节一致的当前 Markdown。
- `<stem>.typ`: 脚本从同一 candidate Markdown 生成的当前 Typst。
- `<stem>.pdf`: 仅在请求 PDF 且从同一 candidate Typst 编译、通过 PDF header gate 后存在。

根目录只允许 exact current set 与按需存在的 `sources/`、`assets/`、`history/`、`.work/`。候选、rollback 和有界 diff 位于 owned `.work/<run-id>/`，成功或 handled failure 后清理；legacy `.tiaokedan/`、`media/` 和 unknown 文件必须先审计并确认，普通 render 不自动迁移或删除。

## Verification

- [ ] `python3 -m py_compile skills/tiaokedan/scripts/tiaokedan_renderer.py`
- [ ] `skills/tiaokedan/scripts/tiaokedan.sh --help` 显示 `--pdf`。
- [ ] `scripts/tiaokedan.sh render --input <md> --typ <typ>` 生成 Typst。
- [ ] `scripts/tiaokedan.sh render --input <md> --typ <typ> --pdf <pdf>` 在安装 `typst` 时生成非空 PDF。
- [ ] identical candidate 不创建 history 且不改变 current inode/mtime；changed candidate 把旧 exact set 成套写入下一 `history/<sequence>/`。
- [ ] expected、生成、PDF 验证或 handled publish failure 后，旧 current/history 保持不变且 owned `.work` 收尾。
- [ ] 成功公开目录不包含 status、manifest、log、diff、debug、json、tmp 或 diagnostic 文件。
- [ ] OpenClaw 与 Hermes Agent 的差异只在 adapter notes 中，没有进入 canonical 主流程。

## Safety

- 不要跳过教师审阅，直接从零散事实声称 PDF 最终通过。
- 不要在必填事实存在 `{{待补充: ...}}` 或 `{{AI草稿: ...}}` 时生成最终 Typst/PDF。
- 不要修改 Phase 37/38/39 已接受的 form surface、Markdown contract 或 renderer parsing scope，除非后续 phase 明确打开。
- 不要加入 school variants、batch generation、spreadsheet import、OCR/photo extraction、approval grids、signature boxes 或 opinion columns。
- 不要调用 sibling skill scripts；运行时只依赖本 `tiaokedan` skill folder、`python3` 和可选 `typst`。
- 不要宣称多文件跨路径原子、SIGKILL 或断电恢复；保证范围是 candidate-first、单路径 replace 与 handled failure/INT/TERM 回滚。
