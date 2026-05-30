# Compatibility Matrix

本矩阵记录 v1 必须考虑的 agent runtime。这里的目标不是伪装成所有平台都完全一致，而是把差异显式化。

## Recommended Pattern

最佳实践是 **canonical source + runtime adapters**：

1. 用一个 canonical `SKILL.md` 表达技能语义、触发条件、流程、输出和成功标准。
2. 在 adapter notes 里记录每个 runtime 的加载路径、frontmatter 限制、工具调用差异、用户问询差异和安全限制。
3. 只有当 runtime 需要不同文件布局时，才生成专用包装层；不要手写维护多份业务逻辑。

## Matrix

| Runtime | v1 Status | Expected Skill Shape | Notes |
|---------|-----------|----------------------|-------|
| Codex | Required | `AGENTS.md` + local skill instructions where available | Codex 以 `AGENTS.md` 作为项目级 agent 指令入口；技能适配需避免依赖不可用的 Claude-only 语法。 |
| Claude Code | Required | `.claude/skills/<name>/SKILL.md` | Claude Skills 使用 `SKILL.md` 与 YAML frontmatter；适合做 canonical 结构参考。 |
| Gemini CLI | Required | `GEMINI.md` context plus project skills adapter | Gemini CLI 官方上下文机制围绕 `GEMINI.md`；SKILL.md 兼容需通过项目规则或 adapter 桥接。 |
| OpenCode | Required | `.opencode/skill/<name>/SKILL.md` and Claude-compatible skill paths | OpenCode 文档显示其可发现 OpenCode 路径与 Claude-compatible 路径。 |
| OpenClaw | Required | AgentSkills-compatible folder with `SKILL.md` | 必须注意 frontmatter 兼容性、allowlist、skill roots、sandbox sync 和安全审阅。 |
| Hermes Agent | Required | `SKILL.md` skill folders, exact path to validate per installed runtime | 公开资料显示 Hermes Agent 采用 SKILL.md 风格技能；v1 需要保留适配占位并在安装后实测路径与加载行为。 |

## Runtime Notes

### Codex

- Put persistent project instructions in `AGENTS.md`.
- Keep runtime-specific command mappings out of canonical skill bodies.
- When a skill references tools, document Codex equivalents in adapter notes.

Reference: [OpenAI Codex AGENTS.md docs](https://github.com/openai/codex/blob/main/docs/agents_md.md)

### Claude Code

- Prefer one skill directory per skill.
- Keep `name` and `description` precise because they drive skill selection.
- Place long reference material in supporting files and let the skill load it only when needed.

Reference: [Claude Code Skills docs](https://code.claude.com/docs/en/agent-sdk/skills)

### Gemini CLI

- Treat `GEMINI.md` as the official project-context bridge.
- If using SKILL.md with Gemini-based workflows, document exactly how the agent is instructed to discover and follow skills.

Reference: [Gemini CLI GEMINI.md docs](https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html)

### OpenCode

- Document both native OpenCode skill paths and Claude-compatible fallback paths.
- Keep the canonical file valid enough that OpenCode can load the same `SKILL.md` when possible.

Reference: [OpenCode skills docs](https://opencode.ubitools.com/skills/)

### OpenClaw

- Use AgentSkills-compatible folders with `SKILL.md`.
- Keep frontmatter conservative; OpenClaw documentation notes parser constraints for frontmatter keys.
- Treat third-party skills as untrusted code and review before enabling.

References:

- [OpenClaw skills source docs](https://github.com/openclaw/openclaw/blob/main/docs/tools/skills.md)
- [OpenClaw skills overview](https://openclawcn.com/en/docs/agent/skills/)

### Hermes Agent

- Keep Hermes in v1 as a required runtime, but mark exact loading paths as implementation-validated rather than assumed.
- Adapter notes must record whether Hermes loads project-local skills, global skills, or both in the installed version.
- Avoid depending on automatic script discovery until it has been verified in the target Hermes installation.

References:

- [NousResearch Hermes Agent skills catalog](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/reference/skills-catalog.md)
- [Hermes Agent SKILL.md guide](https://www.agensi.io/learn/how-to-use-skill-md-with-hermes-agent)
