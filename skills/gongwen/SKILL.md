---
name: "gongwen"
description: "Use when writing, normalizing, or rendering Chinese gongwen-style official documents such as notices, reports, and formal work arrangements."
metadata:
  short-description: "类公文 Markdown 到 Typst 工作流"
  version: "0.2.2"
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

把需要呈现为类公文文体的内容归一化为最终交付 Markdown，再通过技能自带 shell 脚本在同一目录生成同名 `.typ` 和 `.pdf`。

## Use When

- 用户明确使用触发词 `gongwen`。
- 用户需要写类似公文文体的通知、报告、方案、工作安排、检查通报或整改要求。
- 用户需要把已有材料整理成可直接对接 Typst 公文模板的 Markdown。

## Inputs

- `source_material`: 用户给出的主题、要点、原始资料或已有 Markdown。
- `output_markdown`: 持久化的最终交付 Markdown，文件名使用文档标题，如 `关于开展专项检查的通知.md`；默认结构见 `templates/gongwen.md`。
- `assets/`: 图片等资源目录。Markdown 中的相对图片路径必须能从生成的 Typst 文件位置解析。
- `references/format-and-rendering.md`: frontmatter 字段、控制语法、编号规则、渲染约束和详细验证规则。

## Process

1. 按 `docs/markdown-normalization-contract.md` 把源材料归一化为 `YAML frontmatter + body` 的最终交付 Markdown。
2. 使用 `references/format-and-rendering.md` 中的 frontmatter、正文结构、控制语法和编号规则；归一化时删除标题文字开头的手写层级序号，编号只交给模板生成。
3. 生成或更新 `documents/YYYYMMDD 事项名称/标题.md`，并保持所有不确定或缺失内容可复核。
4. 运行 `skills/gongwen/scripts/gongwen.sh render` 生成同目录同名 `.typ` 和 `.pdf`；最终 `.typ` 必须保留，且是唯一允许的 Typst 产物。
5. 若有参考 Typst，使用 `--expected-typ` 做黑盒一致性验证。

## Script Usage

```bash
skills/gongwen/scripts/gongwen.sh example --output documents/20260703专项检查/关于开展专项检查的通知.md
skills/gongwen/scripts/gongwen.sh render --input documents/20260703专项检查/关于开展专项检查的通知.md --typ documents/20260703专项检查/关于开展专项检查的通知.typ
skills/gongwen/scripts/gongwen.sh render --input documents/20260703专项检查/关于开展专项检查的通知.md --typ documents/20260703专项检查/关于开展专项检查的通知.typ --pdf documents/20260703专项检查/关于开展专项检查的通知.pdf
```

带参考产物验证：

```bash
skills/gongwen/scripts/gongwen.sh render \
  --input /path/to/documents/YYYYMMDD事项/标题.md \
  --typ /path/to/documents/YYYYMMDD事项/标题.typ \
  --expected-typ /path/to/reference.typ
```

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 读取本 `SKILL.md` 和 `references/format-and-rendering.md` 后执行流程；用 shell 调用 `scripts/gongwen.sh`；写文件前确认目标路径；正式公文任务必须同时生成并保留同级 `.md`、`.typ`、`.pdf`。 |
| Claude Code | 可把同一目录安装到 `.claude/skills/gongwen/`；frontmatter 的 `description` 是触发入口；脚本属于显式外部命令，执行前检查路径和权限。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向本 `SKILL.md`；若无法自动发现脚本，按 `Script Usage` 手动调用，并读取 `references/` 中的长规则。 |
| OpenCode | 使用可加载 `SKILL.md` 的 skill 路径；若走 Claude-compatible fallback，保持同一目录结构并验证 `references/` 和脚本可读可执行。 |
| OpenClaw | 作为 AgentSkills-compatible 目录使用；安装时验证 frontmatter 解析、技能根目录、`references/` 可读性、脚本 allowlist 和 shell 脚本执行权限。 |
| Hermes Agent | 使用 `SKILL.md` skill folder；安装时验证项目级/全局技能路径、reference/script 发现行为和 shell 脚本执行权限。 |

## Outputs

- `documents/YYYYMMDD 事项名称/标题.md` 最终 Markdown。
- 同目录同名 `标题.typ`，这是必须保留且唯一的 Typst 产物。
- 同目录同名 `标题.pdf`，生成条件和限制见 `references/format-and-rendering.md`。
- 成功交付目录只保留 `标题.md`、`标题.typ`、`标题.pdf`；不得留下 source、output、manifest、log、验证文件、临时目录或缓存目录。

## Verification

- [ ] `skills/gongwen/scripts/gongwen.sh example --output <标题.md>` 能输出可审阅的最终 Markdown 结构。
- [ ] `skills/gongwen/scripts/gongwen.sh render --input <md> --typ <typ>` 能生成 Typst。
- [ ] `signature: true` 时正文末尾没有手写发文单位、日期或署名块；落款只由 `author` 和 `date` frontmatter 生成。
- [ ] 成功交付目录只包含 `标题.md`、`标题.typ`、`标题.pdf`，且最终 `.typ` 必须保留。
- [ ] 带手写标题序号与不带手写标题序号的等价输入生成相同 Typst 标题内容。
- [ ] 标题及正文使用同字体类型 fallback，不把黑体替换成宋体或把宋体替换成黑体。
- [ ] `render --pdf <pdf>` 在安装 `typst` CLI 的环境中可导出 PDF。
- [ ] 对给定 fixture 运行 `--expected-typ` 时，生成 Typst 与参考文件一致。
- [ ] OpenClaw 与 Hermes Agent 的运行时差异保留在 adapter notes 中，没有写入 canonical 主流程。

## Success Criteria

- 技能在触发词 `gongwen` 下能指导 agent 产出类公文最终 Markdown。
- 脚本能从最终 Markdown 生成稳定 Typst，且转换效果与参考黑盒 Typst 一致。
- 长格式规则和 renderer notes 位于 `references/format-and-rendering.md`，入口保持清晰可读。
- 技能保持 canonical 单文件语义源，不引入 runtime-specific wrapper。

## Safety

- 不要静默删除源材料中不确定、缺失或无法表达的内容；必须就近标记复核。
- 不要把凭据、私有路径或用户专属资源写入正文，除非用户明确要求。
- 脚本的 Markdown 到 Typst 转换不得调用外部模板二进制、Pandoc、Python、Node 或其他 Markdown 转换器。
- 脚本只读取输入 Markdown，并只写入用户指定的 Typst/PDF 输出路径；输出路径的父目录必须已存在。
- 不要在 documents 工作目录留下 source、output、manifest、log、验证文件、临时目录或缓存目录；调试与验证产物必须放在系统临时目录或测试专用临时目录。
