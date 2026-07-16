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
4. 运行 `skills/gongwen/scripts/gongwen.sh render`：`--typ` 决定交付根和稳定 stem，`--pdf` 若提供必须同根同 stem。脚本先在 `.work/<run-id>/candidate/` 生成完整 pair/triple，expected 与 PDF gate 全部通过后才发布。
5. 若有参考 Typst，使用 `--expected-typ` 做 candidate 黑盒一致性验证；相同 exact set 是 no-op，发生变化时旧整套进入下一 `history/<sequence>/`。

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
| Codex | 整目录安装并读取本文件与 `references/`；自动发现不可用时显式执行 `scripts/gongwen.sh`。允许 Bash 与 Python 3 执行、技能目录读取和交付根/`.work` 写入；PDF 模式额外 allowlist `typst`，sandbox 不得把 `.work` 映射到不同设备。 |
| Claude Code | 将完整 skill folder 安装到技能路径；显式 fallback 仍是 `scripts/gongwen.sh`。授权 Bash、Python 3、读取模板/reference、写交付根与 `.work`；PDF 模式需可执行 `typst`，不得只复制 `SKILL.md`。 |
| Gemini CLI | 通过项目上下文发现完整目录；支持文件发现失败时显式调用脚本。需要 Bash、Python 3、文件读写和可选 `typst`；allowlist/sandbox 必须同时覆盖 delivery root 与同根 `.work`。 |
| OpenCode | 使用完整 canonical skill folder，Claude-compatible discovery 不可靠时走同一显式脚本。允许 Bash、Python 3、模板/reference 读取、delivery/`.work` 写入与可选 `typst`，保持 whole-folder 安装。 |
| OpenClaw | 安装时验证 whole-folder、frontmatter、reference/template/script 发现、Bash/Python 3/`cmp`、可选 `typst`、execute/read/write allowlist 及同根 delivery/`.work` sandbox；自动发现失败时使用显式 `gongwen.sh` fallback。 |
| Hermes Agent | 安装时验证项目级/全局 whole-folder 路径、support-file discovery、Bash/Python 3/`cmp`、可选 `typst`、工具权限及 delivery/`.work` 可写同设备；发现不确定时显式调用 `gongwen.sh`。 |

## Outputs

- 当前交付是 exact same-stem `标题.md + 标题.typ` pair；请求 `--pdf` 时是 exact `标题.md + 标题.typ + 标题.pdf` triple。PDF 的增加或移除都是整套变化。
- 根目录还只允许按需存在 `sources/`、`assets/`、`history/`、`.work/`；`.work` 仅属于一次运行并在成功或 handled failure 后清理。
- `history/<sequence>/` 保存被替换的完整旧 pair/triple；`sources/` 永不由普通 render 归档或修改，unknown/legacy 项必须先走确认式整理。
- manifest、log、diff、验证报告、staging、失败产物和任意平铺版本副本不得发布到根目录。

## Verification

- [ ] `skills/gongwen/scripts/gongwen.sh example --output <标题.md>` 能输出可审阅的最终 Markdown 结构。
- [ ] `skills/gongwen/scripts/gongwen.sh render --input <md> --typ <typ>` 能生成 Typst。
- [ ] `signature: true` 时正文末尾没有手写发文单位、日期或署名块；落款只由 `author` 和 `date` frontmatter 生成。
- [ ] 成功 current 是 exact pair 或 optional-PDF triple；完全相同运行不改 current inode/mtime、不创建 history。
- [ ] expected mismatch、Typst 缺失/编译失败、PDF header 失败和 handled fault 不改变 prior current/history/sources。
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
- 脚本只读取 reviewed Markdown；所有 candidate、rollback 和 evidence 只写本次 owned `.work/<run-id>/`，输出父目录必须已存在且为真实目录。
- 所有 mutation/cleanup 只使用验证后的 quoted fixed-name arrays 和本 run ownership；拒绝 unknown、legacy `media`/hidden diagnostics、symlink、path traversal、跨根/不同 stem 与 stale work，绝不自动整理用户文件。
- portable guarantee 仅覆盖逐路径 replace 与 handled error/INT/TERM rollback，不声称 SIGKILL、断电或多文件跨路径原子。
