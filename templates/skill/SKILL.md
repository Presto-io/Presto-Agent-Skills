---
name: "<skill-name>"
description: "<When should an agent use this skill? Be specific and intent-based.>"
metadata:
  short-description: "<Short display description>"
  version: "0.1.0"
  portability: "canonical"
---

# <Skill Title>

## Objective

<State the outcome this skill helps the agent produce. Keep this focused on one repeatable workflow.>

## Use When

- <Trigger condition 1>
- <Trigger condition 2>
- <Trigger condition 3>

## Inputs

- `<input-name>`: <Expected input and constraints>

## Process

1. <Step one>
2. <Step two>
3. <Step three>

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | <How Codex should invoke or approximate this skill> |
| Claude Code | <Claude-specific path/frontmatter/tool notes> |
| Gemini CLI | <GEMINI.md or project-context bridge notes> |
| OpenCode | <OpenCode skill path and loading notes> |
| OpenClaw | <OpenClaw frontmatter, allowlist, and sandbox notes> |
| Hermes Agent | <Hermes path/loading/script-discovery notes to verify> |

## Outputs

- <Expected output artifact or response>

## Verification

- [ ] <Checkable success criterion>
- [ ] <Checkable success criterion>

## Safety

- <What the agent must avoid>
- <Any permission, credential, network, or filesystem boundary>
