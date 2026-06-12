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
- `references/<reference-name>.md`: <Long format rules, examples, renderer notes, or operational details to read only when needed>

## Process

1. <Step one>
2. <Step two>
3. <Step three>

Keep `SKILL.md` as the semantic entry point: trigger intent, objective, required inputs, high-level process, outputs, verification, safety, and runtime adapter notes must remain visible here. Put long examples, detailed format rules, renderer notes, troubleshooting, fixture explanations, and operational edge cases in `references/`. Put helper commands in `scripts/`. Put output scaffolds or copyable artifact templates in `templates/`.

For document workflow skills, normalize source material into the Markdown intermediate described in `docs/markdown-normalization-contract.md` before generating Typst, HTML, or other target outputs.

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
- <If outputs have many fields or files, link to `references/<artifact-contract>.md` instead of listing every detail here>

## Verification

- [ ] <Checkable success criterion for the output>
- [ ] <Checkable success criterion for runtime compatibility notes>
- [ ] <Checkable success criterion for safety boundaries>
- [ ] <If detailed verification is long, this entry links to the skill-local reference that owns it>

## Success Criteria

- <What must be true for this skill to count as complete>
- <What must remain out of scope or unchanged>

## Safety

- <What the agent must avoid>
- <Any permission, credential, network, external command, or filesystem boundary>
- <How to verify before writing files, running commands, or using credentials>
