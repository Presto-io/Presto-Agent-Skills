# Runtime Adapter: <runtime-name>

## Status

- Support level: <required|experimental|planned>
- Last verified: <YYYY-MM-DD or not yet verified>
- Owner: <name or team>

## Loading Path

```text
<Where this runtime expects skill files>
```

## Required File Shape

- Skill file name:
- Required frontmatter:
- Optional frontmatter:
- Supporting folders:

## Invocation Model

Describe how the runtime decides to use the skill:

- automatic selection:
- explicit command:
- project instruction bridge:
- user-visible slash command:

## Tool and Permission Differences

- Shell:
- Filesystem:
- Network:
- Browser:
- Subagents/tasks:
- User questions:

## Canonical Mapping

Explain how fields in the canonical `SKILL.md` map into this runtime.

| Canonical Section | Runtime Mapping |
|-------------------|-----------------|
| `description` |  |
| `Process` |  |
| `Runtime Adapter Notes` |  |
| `Verification` |  |
| `Safety` |  |

## Known Limitations

- <Limitation 1>
- <Limitation 2>

## Verification Checklist

- [ ] Runtime discovers the skill.
- [ ] Runtime selects the skill for the intended trigger.
- [ ] Runtime can access required supporting files.
- [ ] Runtime handles tool and permission requirements safely.
- [ ] Runtime produces the expected output shape.
