# Compatibility Matrix

本矩阵记录 v1 必须考虑的 agent runtime。这里的目标不是伪装成所有平台都完全一致，而是把差异显式化。

## Recommended Pattern

最佳实践是 **one canonical `SKILL.md` first, runtime notes second**：

1. 用一个 canonical `SKILL.md` 表达技能语义、触发条件、流程、输出、验证和安全边界。
2. 在同一个 `SKILL.md` 的 adapter notes 中记录各 runtime 的加载路径、frontmatter 限制、工具调用、用户问询、任务/子代理和权限差异。
3. v1 不维护独立 adapter 文件；如果 notes 变长，先压缩成必要检查点并保留在 canonical 文件里。
4. 只有当 runtime 确实无法直接使用 canonical 文件时，才重新打开范围讨论 generated wrappers；v1 不实现 wrapper 生成，也不维护多份技能逻辑。

## Matrix

| Runtime | v1 Status | Same-File Strategy | Adapter Notes Must Cover |
|---------|-----------|--------------------|--------------------------|
| Codex | Required | Keep canonical workflow in `SKILL.md`; expose persistent project guidance through `AGENTS.md` or the local skill mechanism available in the installed Codex environment. | Tool equivalents, unavailable Claude-only syntax, file-write safety, and how Codex is told to read the skill. |
| Claude Code | Required | Install the same `SKILL.md` in a Claude skill folder such as `.claude/skills/<name>/SKILL.md`. | Trigger-focused `description`, frontmatter/tool allowlist, progressive disclosure, and supporting file paths. |
| Gemini CLI | Required | Use `GEMINI.md` or project context to point Gemini at the canonical `SKILL.md`. | Discovery bridge, invocation wording, unavailable tool mappings, and user-question fallback. |
| OpenCode | Required | Prefer an OpenCode skill path that can load the same `SKILL.md`; record any Claude-compatible fallback path as an install note. | Native path, fallback path, tool permission differences, and verification that the runtime selected the skill. |
| OpenClaw | Required | Treat OpenClaw as a first-class target using an AgentSkills-compatible `SKILL.md` folder when supported by the installed runtime. | Conservative frontmatter, allowlist, skill roots, sandbox sync, third-party skill review, and installation-time parser checks. |
| Hermes Agent | Required | Treat Hermes Agent as a first-class target with `SKILL.md` skill folders, but validate the exact local/global path in the installed runtime. | Loading path, project-vs-global behavior, script discovery, tool permissions, and verification cautions for untested behavior. |

## Runtime Notes

### Codex

- Put persistent project instructions in `AGENTS.md`.
- Keep runtime-specific command mappings out of canonical skill bodies.
- When a skill references tools, document Codex equivalents in adapter notes.
- If a Codex installation cannot auto-discover `SKILL.md`, record the project-context bridge that tells Codex to read it.

Reference: [OpenAI Codex AGENTS.md docs](https://github.com/openai/codex/blob/main/docs/agents_md.md)

### Claude Code

- Prefer one skill directory per skill.
- Keep `name` and `description` precise because they drive skill selection.
- Place long reference material in supporting files and let the skill load it only when needed.

Reference: [Claude Code Skills docs](https://code.claude.com/docs/en/agent-sdk/skills)

### Gemini CLI

- Treat `GEMINI.md` as the official project-context bridge.
- If using SKILL.md with Gemini-based workflows, document exactly how the agent is instructed to discover and follow skills.
- Keep user-question and subagent behavior as explicit fallbacks when Gemini lacks an equivalent tool.

Reference: [Gemini CLI GEMINI.md docs](https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html)

### OpenCode

- Document both native OpenCode skill paths and Claude-compatible fallback paths.
- Keep the canonical file valid enough that OpenCode can load the same `SKILL.md` when possible.
- Verify skill discovery in the installed OpenCode version before marking a skill as supported.

Reference: [OpenCode skills docs](https://opencode.ubitools.com/skills/)

### OpenClaw

- Use AgentSkills-compatible folders with `SKILL.md`.
- Keep frontmatter conservative; OpenClaw documentation notes parser constraints for frontmatter keys.
- Treat third-party skills as untrusted code and review before enabling.
- Verify allowlist, skill root, and sandbox behavior during installation. Do not move OpenClaw to optional/future status in v1 docs.

References:

- [OpenClaw skills source docs](https://github.com/openclaw/openclaw/blob/main/docs/tools/skills.md)
- [OpenClaw skills overview](https://openclawcn.com/en/docs/agent/skills/)

### Hermes Agent

- Keep Hermes in v1 as a required runtime, but mark exact loading paths as implementation-validated rather than assumed.
- Adapter notes must record whether Hermes loads project-local skills, global skills, or both in the installed version.
- Avoid depending on automatic script discovery until it has been verified in the target Hermes installation.
- Do not claim generated-wrapper support unless the wrapper rule and verification checklist are documented.

References:

- [NousResearch Hermes Agent skills catalog](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/reference/skills-catalog.md)
- [Hermes Agent SKILL.md guide](https://www.agensi.io/learn/how-to-use-skill-md-with-hermes-agent)
