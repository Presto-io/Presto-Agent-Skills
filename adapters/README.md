# Runtime Adapters

Adapters describe how a canonical skill should be interpreted by a specific agent runtime.

Do not duplicate the full skill logic unless a runtime truly requires a generated wrapper. Prefer this order:

1. Keep shared workflow instructions in `skills/<skill-name>/SKILL.md`.
2. Add runtime-specific notes in the skill's adapter section.
3. If notes become too large, create `adapters/<runtime>/<skill-name>.md`.
4. If the runtime requires generated files, document the generation rule before adding output files.

Required v1 runtimes:

- Codex
- Claude Code
- Gemini CLI
- OpenCode
- OpenClaw
- Hermes Agent
