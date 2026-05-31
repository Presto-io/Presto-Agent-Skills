# Presto Agent Skills

Presto Agent Skills 是一个面向多类 AI agent 的技能仓库框架。它让团队先用一个 canonical `SKILL.md` 编写技能，再用轻量 runtime adapter notes 说明不同 agent 的安装、调用和安全差异。

这个仓库面向编写、审阅和迁移 agent 技能的贡献者，也面向需要读取本地规则并保持 runtime-neutral 输出的 coding agents。

首批支持目标：

- Codex
- Claude Code
- Gemini CLI
- OpenCode
- OpenClaw
- Hermes Agent

其中 OpenClaw 和 Hermes Agent 是 v1 必须支持的目标。

## 设计原则

1. **统一源文件优先**：每个技能先写一个 canonical `SKILL.md`，它是技能语义、流程、输出和验证标准的唯一来源。
2. **适配注释隔离差异**：各 agent 的路径、frontmatter、工具调用、子代理、用户问询等差异先写进同一个 `SKILL.md` 的 runtime notes。
3. **渐进披露**：`description` 要短而准确，正文只写必要流程，大块参考资料放到 `references/`。
4. **安全默认**：技能可能改变 agent 的行为和可执行能力，第三方技能必须先审阅再启用。
5. **先稳定契约，后扩展自动化**：v1 先稳定目录、模板和兼容性说明；示例保持可选且精简，脚手架、校验器、runtime harness、generated wrappers 和发布流程后续再加。

## 仓库结构

```text
.
├── AGENTS.md
├── README.md
├── docs/
│   ├── compatibility-matrix.md
│   ├── directory-spec.md
│   └── markdown-normalization-contract.md
├── skills/
│   ├── README.md
│   ├── gongwen/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   └── templates/
│   ├── jiaoan-jihua/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── scripts/
│   │   └── templates/
│   └── jiaoan-shicao/
│       ├── SKILL.md
│       ├── references/
│       ├── scripts/
│       └── templates/
├── templates/
│   ├── README.md
│   └── skill/
│       └── SKILL.md
└── .planning/
    ├── PROJECT.md
    ├── REQUIREMENTS.md
    ├── ROADMAP.md
    ├── STATE.md
    └── config.json
```

## 如何添加新技能

1. 复制 `templates/skill/SKILL.md` 到 `skills/<skill-name>/SKILL.md`。
2. 填写 `name`、`description`、目标、触发条件、流程、输出和成功标准。
3. 在同一个 `SKILL.md` 的 `Runtime Adapter Notes` 中补齐 Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw 和 Hermes Agent 的最小兼容说明。
4. 文档工作流技能必须先按 `docs/markdown-normalization-contract.md` 把源材料归一化为 Markdown intermediate，再生成 Typst、HTML 或其他目标输出。
5. 如果某个 runtime 的说明变长，先压缩成必要检查点；不要为 v1 新增独立 adapter 文件。
6. 如果确实需要给贡献者看一个参考样例，再创建 `examples/<example-name>/SKILL.md`，但不要把它当成 v1 依赖。
7. 更新 `docs/compatibility-matrix.md` 中相关 runtime 的支持状态；不要在未验证时声称完整 runtime 支持。

## 已有技能

- `gongwen`：用于写作、归一化和验证类公文文体文档，先输出 `gongwen-full.md` 结构的 Markdown intermediate，再通过 Presto gongwen 模板生成 Typst/PDF。
- `jiaoan-jihua`：用于写作、归一化和验证授课进度计划表，先输出 `jiaoan-jihua-full.md` 结构的 Markdown intermediate，再通过 Presto jiaoan-jihua 模板生成 Typst/PDF。
- `jiaoan-shicao`：用于写作、归一化和验证实操教案/实训教案文档，先输出 `jiaoan-shicao-full.md` 结构的 Markdown intermediate，再通过 Presto jiaoan-shicao 模板生成 Typst/PDF。
