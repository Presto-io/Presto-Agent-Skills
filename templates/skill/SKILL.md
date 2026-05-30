---
name: "<skill-name>"
description: "<When should an agent use this skill? Be specific and intent-based.>"
metadata:
  short-description: "<Short display description>"
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

# <Skill Title>

## Objective

<State the outcome this skill helps the agent produce. Keep this focused on one repeatable workflow.>

## Use When

- <Trigger condition 1>
- <Trigger condition 2>
- <Trigger condition 3>

## Inputs

- `<input-name>`: <Expected input, constraints, and default behavior>
- `<context-file-or-folder>`: <Optional supporting context the agent should read before acting>

## Process

1. <Step one>
2. <Step two>
3. <Step three>

Keep shared workflow logic in this file. Put long background material in `references/`, helper scripts in `scripts/`, and output templates in `templates/` only when the skill needs them.

## Runtime Adapter Notes

Use this table for concise compatibility notes. Do not duplicate the skill process into runtime-specific files unless a runtime truly cannot consume this canonical `SKILL.md` directly.

| Runtime | Notes |
|---------|-------|
| Codex | <How Codex should discover, invoke, or approximate this skill; map unavailable tools to Codex equivalents> |
| Claude Code | <Claude Code skill path, frontmatter, tool allowlist, and subagent notes> |
| Gemini CLI | <GEMINI.md or project-context bridge notes that tell Gemini how to find and follow this SKILL.md> |
| OpenCode | <OpenCode skill path/loading notes and any Claude-compatible fallback path> |
| OpenClaw | <OpenClaw path, conservative frontmatter, allowlist, sandbox, and security-review notes to verify> |
| Hermes Agent | <Hermes path/loading/script-discovery behavior to verify in the installed runtime> |

## Outputs

- <Expected output artifact or response>
- <Any files created or modified>

## Verification

- [ ] <Checkable success criterion for the output>
- [ ] <Checkable success criterion for runtime compatibility notes>
- [ ] <Checkable success criterion for safety boundaries>

## Success Criteria

- <What must be true for this skill to count as complete>
- <What must remain out of scope or unchanged>

## Safety

- <What the agent must avoid>
- <Any permission, credential, network, external command, or filesystem boundary>
- <How to verify before writing files, running commands, or using credentials>
