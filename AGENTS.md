# AGENTS.md

## Language

始终使用简体中文回复用户，除非用户明确要求其他语言，或正在编辑的文件格式必须使用其他语言。

## Project Purpose

本仓库用于沉淀可跨多类 AI agent 使用的技能。核心策略是：一个 canonical `SKILL.md` 作为语义源文件，再用 runtime adapter 说明 Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw、Hermes Agent 的差异。

## Editing Rules

- 优先保持文档和模板简洁、可复制、可审阅。
- 不要把某个 agent 的私有语法写进 canonical 技能主体；放到 adapter notes。
- 新技能默认放在 `skills/<skill-name>/SKILL.md`。
- 示例技能放在 `examples/<example-name>/SKILL.md`。
- 模板只放在 `templates/`，不要把示例内容和模板混在一起。
- 更新目录约定时，同步更新 `README.md` 和 `docs/directory-spec.md`。
- 如果新增 runtime 支持，同步更新 `docs/compatibility-matrix.md`。

## Skill Authoring Rules

- `description` 必须说明什么时候使用该技能，不要写营销句。
- 一个技能只服务一个明确工作流。
- 复杂背景材料放到 `references/`，脚本放到 `scripts/`，输出模板放到 `templates/`。
- 技能涉及外部命令、网络、凭据或文件写入时，必须写明安全边界和验证步骤。
- OpenClaw 与 Hermes Agent 是必须考虑的 runtime；新增技能不能只写 Claude/Codex 说明。

## GSD Workflow

本仓库已初始化为 GSD 项目。规划文件位于 `.planning/`：

- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/config.json`

执行新阶段前，优先阅读 `.planning/ROADMAP.md` 和 `.planning/STATE.md`。
