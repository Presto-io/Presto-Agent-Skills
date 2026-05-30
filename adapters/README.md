# Runtime Adapters

Adapters describe how a specific agent runtime loads and interprets the same canonical `SKILL.md`.

They are optional compatibility notes, not parallel implementations. The shared workflow, safety rules, verification steps, and output contract stay in `skills/<skill-name>/SKILL.md`.

Do not duplicate the full skill logic unless a runtime truly requires a generated wrapper. Prefer this order:

1. Keep shared workflow instructions in `skills/<skill-name>/SKILL.md`.
2. Add concise runtime-specific notes in the skill's `Runtime Adapter Notes` section.
3. If notes become too large, create `adapters/<runtime>/<skill-name>.md` from `templates/adapter/runtime-adapter.md`.
4. If the runtime requires a generated wrapper, document the generation rule and verification checklist before adding output files.

Required v1 runtimes:

- Codex
- Claude Code
- Gemini CLI
- OpenCode
- OpenClaw
- Hermes Agent

OpenClaw and Hermes Agent are first-class required targets. If exact loading behavior cannot be verified locally, record the installation-time check instead of claiming full support.
