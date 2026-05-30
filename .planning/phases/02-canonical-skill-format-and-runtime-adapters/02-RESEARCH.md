# Phase 2: Canonical Skill Format and Runtime Adapters - Research

**Researched:** 2026-05-30 [VERIFIED: local-docs+web]
**Domain:** portable `SKILL.md` contract and runtime compatibility notes [CITED: .planning/ROADMAP.md]
**Confidence:** MEDIUM-HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

- Keep one canonical `SKILL.md` as the main cross-agent artifact.
- Do not design a heavy adapter architecture, generated wrapper system, scaffold CLI, schema/lint tooling, runtime execution harness, or publishing workflow in v1.
- Runtime-specific material should be limited to install, loading, invocation, tool, question, task/subagent, limitation, and verification notes needed for the same skill file to work after installation.
- Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent are all required v1 targets.
- OpenClaw and Hermes Agent must stay first-class required targets, but documentation must not invent unsupported behavior where local/runtime verification is unavailable.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TMPL-01 | A contributor can copy a canonical `SKILL.md` template with metadata, objective, usage, process, outputs, and success criteria. | Update `templates/skill/SKILL.md` as the central copyable artifact and keep placeholders concise. |
| TMPL-02 | A contributor can copy a runtime adapter template capturing invocation, user-question handling, task/subagent handling, tool differences, and limitations. | Keep `templates/adapter/runtime-adapter.md` as a minimal compatibility-note template, not a second source of skill logic. |
| RT-01 | Compatibility matrix covers Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent. | Keep all six runtimes in `docs/compatibility-matrix.md` and separate verified facts from installation checks. |
| RT-02 | OpenClaw and Hermes Agent are first-class required targets with adapter placeholders and research notes. | Preserve explicit rows/sections for OpenClaw and Hermes; mark exact paths or behaviors that require target-runtime validation. |
| RT-03 | Docs explain canonical source first, runtime-specific adapter notes or generated wrappers second. | Align README, adapter README, directory spec, template copy, and compatibility matrix around the single-file-first story. |
</phase_requirements>

## Runtime Research Summary

| Runtime | Planning Implication | Source |
|---------|----------------------|--------|
| Codex | Project-level rules are expressed through `AGENTS.md`; canonical skill docs should avoid Claude-only command assumptions and map unavailable tools in adapter notes. | https://github.com/openai/codex/blob/main/docs/agents_md.md |
| Claude Code | `SKILL.md` plus frontmatter is the strongest canonical reference shape; `description` should remain trigger-oriented and supporting content should be loaded progressively. | https://code.claude.com/docs/en/agent-sdk/skills |
| Gemini CLI | `GEMINI.md` is the official project-context bridge, so compatibility notes should say how the agent is instructed to discover/follow `SKILL.md`. | https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html |
| OpenCode | Document native skill path/loading notes and any Claude-compatible fallback as runtime compatibility, while keeping one semantic skill file. | https://opencode.ubitools.com/skills/ |
| OpenClaw | Treat OpenClaw as a required target with conservative frontmatter and security review notes; do not assume every Claude-specific field is accepted. | https://github.com/openclaw/openclaw/blob/main/docs/tools/skills.md |
| Hermes Agent | Keep Hermes as a required target, but require installation-time validation for exact local/global skill paths and script-discovery behavior. | https://github.com/NousResearch/hermes-agent/blob/main/website/docs/reference/skills-catalog.md |

## Existing State Inventory

| Artifact | Status | Planning Implication |
|----------|--------|----------------------|
| `templates/skill/SKILL.md` | Present and already includes objective, usage, process, runtime notes, outputs, verification, and safety. | Tighten wording so it reads as the primary single-file template, and make success criteria explicit. |
| `templates/adapter/runtime-adapter.md` | Present and useful, but currently reads like a full adapter document. | Reframe as optional/minimal install-use compatibility notes for cases where the embedded notes table is not enough. |
| `docs/compatibility-matrix.md` | Present and covers all six runtimes. | Align language with "same skill file first" and avoid claiming unverified full support. |
| `README.md` | Present and says canonical source plus runtime adapters. | Adjust contributor path so separate adapter docs are optional; the canonical `SKILL.md` remains the default unit. |
| `docs/directory-spec.md` | Present and explains artifact ownership. | Ensure adapter/wrapper language stays minimal and generated wrappers remain deferred. |
| `templates/README.md` | Present but minimal. | Point contributors to `templates/skill/SKILL.md` first and adapter template only when needed. |
| `adapters/README.md` | Present and lists all runtimes. | Simplify into lightweight compatibility-note guidance. |

## Recommended Planning Shape

Plan Phase 2 as a documentation/template alignment pass:

1. Make the canonical skill template copyable and self-contained.
2. Reframe the adapter template as minimal runtime compatibility notes.
3. Align compatibility and contributor docs around one semantic source file.
4. Capture summary evidence and update GSD state/requirement statuses after verification.

No new runtime harness, generator, schema validator, package install, or publishing flow is required.

## Verification Strategy

Use local Markdown/source assertions:

```bash
rg -n "metadata:|Objective|Use When|Process|Outputs|Verification|Safety|Runtime Adapter Notes" templates/skill/SKILL.md
rg -n "Invocation|User Questions|Tasks|Subagents|Tool|Permission|Known Limitations|Verification" templates/adapter/runtime-adapter.md
rg -n "Codex|Claude Code|Gemini CLI|OpenCode|OpenClaw|Hermes Agent|canonical|SKILL.md" docs/compatibility-matrix.md README.md docs/directory-spec.md adapters/README.md templates/README.md
rg -n "TMPL-01|TMPL-02|RT-01|RT-02|RT-03" .planning/REQUIREMENTS.md .planning/ROADMAP.md .planning/phases/02-canonical-skill-format-and-runtime-adapters/02-01-SUMMARY.md
```

## Common Pitfalls

- Treating adapter notes as a second source of skill logic.
- Requiring contributors to fill six separate runtime documents before a skill is useful.
- Claiming fully verified runtime support where only documentation-level guidance exists.
- Dropping OpenClaw or Hermes into "future/optional" status.
- Expanding v1 into scaffold CLI, generated wrappers, lint/schema enforcement, execution harnesses, or distribution tooling.

---

*Phase: 2-Canonical Skill Format and Runtime Adapters*
*Research completed: 2026-05-30*
