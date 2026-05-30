# Presto Agent Skills

Presto Agent Skills 是一个面向多类 AI agent 的技能仓库框架。目标是让一个技能先以统一的 canonical `SKILL.md` 写成，再通过 runtime adapter 说明适配到不同 agent。

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

1. **统一源文件优先**：每个技能先写 canonical `SKILL.md`，避免维护多份语义漂移的技能。
2. **适配层隔离差异**：各 agent 的路径、frontmatter、工具调用、子代理、用户问询等差异写进 adapter notes。
3. **渐进披露**：`description` 要短而准确，正文只写必要流程，大块参考资料放到 `references/`。
4. **安全默认**：技能可能改变 agent 的行为和可执行能力，第三方技能必须先审阅再启用。
5. **先文档契约，后自动化**：v1 先稳定目录、模板、示例和 GSD 规划，脚手架与校验器后续再加。

## 仓库结构

```text
.
├── AGENTS.md
├── README.md
├── adapters/
│   └── README.md
├── docs/
│   ├── compatibility-matrix.md
│   └── directory-spec.md
├── examples/
│   ├── README.md
│   └── portable-skill/
│       └── SKILL.md
├── skills/
│   └── README.md
├── templates/
│   ├── README.md
│   ├── adapter/
│   │   └── runtime-adapter.md
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
3. 用 `templates/adapter/runtime-adapter.md` 补齐每个 runtime 的适配说明。
4. 如果技能已经能代表最佳实践，把一个精简版放进 `examples/`。
5. 更新 `docs/compatibility-matrix.md` 中相关 runtime 的支持状态。

## 当前里程碑

当前 GSD 路线图的 Phase 1 是仓库与 GSD 基础结构。完成标准见 `.planning/ROADMAP.md`。

下一步建议：

```text
$gsd-discuss-phase 1
```
