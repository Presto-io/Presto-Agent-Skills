---
name: "skill-authoring-checklist"
description: "Use when reviewing or drafting a portable SKILL.md for multiple agent runtimes."
metadata:
  short-description: "Review portable agent skills"
  version: "0.1.0"
  portability: "canonical"
---

# Skill Authoring Checklist

## Objective

Help an agent review or draft a portable `SKILL.md` that can be adapted across Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.

## Use When

- The user asks to create a new agent skill.
- The user asks whether an existing `SKILL.md` is portable.
- The user asks how to adapt a skill for multiple agent runtimes.

## Inputs

- `skill_goal`: The workflow the skill should make repeatable.
- `target_runtimes`: The runtimes that must be supported.
- `existing_skill`: Optional existing `SKILL.md` content to review.

## Process

1. Identify the single repeatable workflow the skill should cover.
2. Check that `name` and `description` are short, accurate, and trigger-oriented.
3. Ensure the main body explains when to use the skill, the process, expected outputs, verification, and safety.
4. Move long background material into `references/` instead of bloating `SKILL.md`.
5. Add adapter notes for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
6. Call out any runtime behavior that still needs installation-time verification.

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | Use `AGENTS.md` for project-level rules; avoid Claude-only task syntax in canonical instructions. |
| Claude Code | Place as `.claude/skills/skill-authoring-checklist/SKILL.md` when using Claude's native skill loader. |
| Gemini CLI | Bridge through `GEMINI.md` or explicit project instructions until SKILL.md discovery is verified in the target setup. |
| OpenCode | Prefer `.opencode/skill/skill-authoring-checklist/SKILL.md`; Claude-compatible paths may also be supported depending on installation. |
| OpenClaw | Keep frontmatter simple and verify with OpenClaw skill checks; document allowlist or sandbox needs. |
| Hermes Agent | Verify the local/global skills path in the installed Hermes version before claiming full support. |

## Outputs

- A concise review of skill portability issues, or
- A draft `SKILL.md` following the canonical structure.

## Verification

- [ ] The skill has one clear job.
- [ ] The description explains when to use it.
- [ ] Runtime adapter notes cover all required runtimes.
- [ ] Safety and verification expectations are explicit.

## Safety

- Do not invent runtime capabilities that have not been verified.
- Do not include secrets, tokens, or machine-local credentials in a skill.
- Treat third-party skills as executable influence over the agent and review them before installation.
