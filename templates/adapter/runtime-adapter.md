# Runtime Adapter: <runtime-name>

This optional document records install/use compatibility notes for one runtime. It is not a second source of skill logic; the canonical workflow remains in `skills/<skill-name>/SKILL.md`.

## Status

- Support level: <required|experimental|planned>
- Last verified: <YYYY-MM-DD or not yet verified>
- Owner: <name or team>
- Canonical skill file: `skills/<skill-name>/SKILL.md`

## Loading / Install Path

```text
<Where this runtime expects skill files, or how it is pointed at the canonical SKILL.md>
```

## Required File Shape

- Skill file name:
- Required frontmatter:
- Optional frontmatter:
- Supporting folders:
- Wrapper required: <yes|no|unknown; if yes, describe the generation rule without duplicating skill logic>

## Invocation Model

Describe how the runtime decides to use the skill:

- automatic selection:
- explicit command:
- project instruction bridge:
- user-visible slash command:

## User Questions

- Native user-question/checkpoint support:
- Fallback when native questions are unavailable:
- Required wording for human approval or setup steps:

## Tasks and Subagents

- Native task/subagent support:
- Sequential fallback:
- Isolation or worktree behavior:
- Completion signal or handoff marker:

## Tool and Permission Differences

- Shell:
- Filesystem:
- Network:
- Browser:
- External commands:
- Credentials/secrets:

## Canonical Mapping

Explain how fields in the canonical `SKILL.md` map into this runtime.

| Canonical Section | Runtime Mapping |
|-------------------|-----------------|
| `description` |  |
| `Objective` |  |
| `Use When` |  |
| `Process` |  |
| `Runtime Adapter Notes` |  |
| `Outputs` |  |
| `Verification` |  |
| `Safety` |  |

## Known Limitations

- <Limitation 1>
- <Limitation 2>
- <Installation-time behavior that must be verified instead of assumed>

## Verification Checklist

- [ ] Runtime discovers the skill.
- [ ] Runtime selects the skill for the intended trigger.
- [ ] Runtime can access required supporting files.
- [ ] Runtime handles tool and permission requirements safely.
- [ ] Runtime handles user questions, checkpoints, tasks, or subagents as documented.
- [ ] Runtime produces the expected output shape.
- [ ] Any generated wrapper, if required, is traceable back to the canonical `SKILL.md`.
