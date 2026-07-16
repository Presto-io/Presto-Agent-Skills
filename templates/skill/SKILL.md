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
- `templates/<intermediate-or-output-template>.md`: <Copyable Markdown intermediate or output scaffold, if this workflow creates files>

## Process

1. <Step one>
2. <Step two>
3. <Step three>

Keep `SKILL.md` as the semantic entry point: trigger intent, objective, required inputs, high-level process, Markdown intermediate or artifact contract pointers, outputs, verification, safety, and runtime adapter notes must remain visible here. Put long examples, detailed format rules, renderer notes, troubleshooting, fixture explanations, UAT lists, and operational edge cases in `references/`. Put public helper commands and responsibility-based internal modules in `scripts/`. Put output scaffolds or copyable artifact templates in `templates/`.

For document workflow skills, normalize source material into the Markdown intermediate described in `docs/markdown-normalization-contract.md` before generating Typst, HTML, or other target outputs.

## Runtime Adapter Notes

Use this table for concise compatibility notes. Do not duplicate the skill process into runtime-specific files unless a runtime truly cannot consume this canonical `SKILL.md` directly.

| Runtime | Notes |
|---------|-------|
| Codex | <Whole-folder discovery or project bridge; explicit public script fallback; external commands; support/input read and authorized delivery root/.work/verify-workdir write permissions; sandbox/allowlist> |
| Claude Code | <Whole-folder skill path and frontmatter; explicit fallback; external commands; progressive support-file read and authorized write boundaries> |
| Gemini CLI | <GEMINI.md/project bridge for the whole folder; explicit fallback; unavailable tool mappings; sandbox/allowlist and read/write boundaries> |
| OpenCode | <Verified native path or install note; whole-folder preservation; explicit fallback; tool permissions and authorized write boundaries> |
| OpenClaw | <Installation-time verification of exact path, conservative frontmatter, whole-folder/support/script discovery, external commands, allowlist/sandbox and read/write boundaries; explicit script fallback when uncertain> |
| Hermes Agent | <Installation-time verification of exact local/global path, project/global behavior, whole-folder/support/script discovery, execute/read/write and allowlist; explicit script fallback when uncertain> |

## Outputs

- <Expected output artifact or response>
- <Any files created or modified>
- <If outputs have many fields or files, link to `references/<artifact-contract>.md` instead of listing every detail here>

## Delivery Directory

Follow `docs/clean-delivery-directory-contract.md` for every workflow that writes files. The delivery root keeps only the current Markdown and current final deliverables; supporting materials belong in named folders, previous successful versions move together into `history/<sequence>/`, and temporary verification stays in `.work/` only until cleanup.

```text
<delivery-root>/
├── <project-name>.md
├── <project-name>.<delivery-format>
├── sources/
├── assets/
├── history/
│   └── 001/
└── .work/
```

- Stable managed set: <List exact current Markdown and final deliverable relative names. State how every optional artifact changes the exact path set; never discover mutation targets by glob or extension.>
- Support ownership: <State that normal publication does not modify `sources/`; list only explicitly managed, persistently referenced `assets/` that participate in equality and same-version history.>
- Candidate and minimal gate: <Generate one complete bundle in `.work/<run-id>/candidate/`; verify explicit presence, regular/non-symlink type, non-empty/readable format, required references, and skill-specific minimum before current mutation.>
- No-op and revision behavior: <Compare exact relative path-set+bytes. Byte-identical candidate is a no-op that creates no history and does not touch current; changed content archives the whole old bundle under `history/<max+1>/` before publishing stable names. Never auto-delete history.>
- Failure cleanup: <On handled failure/INT/TERM, restore the exact old bundle, remove only this run's owned candidate/rollback/evidence and uncommitted history sequence, and verify current/history remain usable. Do not promise SIGKILL, power-loss, or multi-file cross-path atomicity.>
- Unknown confirmation: <Reject unknown, legacy, partial, ambiguous, traversal, special-file, and symlink states before mutation. Route historical cleanup through snapshot-bound audit → confirm → execute; do not silently migrate, quarantine, rename, archive, or delete user files.>
- Persistent verification artifacts: <Normally none in delivery root. Manifest/status/model/log/diff/screenshot/staging/cache/failure artifacts stay in owned `.work` until cleanup or an explicit caller-owned verification workdir, which is not the delivery root.>

## Verification

- [ ] <Checkable success criterion for the output>
- [ ] <Checkable success criterion for runtime compatibility notes>
- [ ] <Checkable success criterion for safety boundaries>
- [ ] Whole-folder copy can read required `references/`, `scripts/`, `templates/`, and fixtures without sibling-skill or repository-root runtime imports.
- [ ] First publish, changed whole-bundle history, byte-identical no-op, handled rollback, unknown/symlink refusal, and `.work` cleanup are exercised through the public command.
- [ ] Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent notes each name whole-folder discovery, explicit fallback, real dependencies, execute/read/write, sandbox/allowlist, delivery root/`.work`, and verify workdir boundaries; OpenClaw/Hermes claims are installation-time verified only.
- [ ] <If detailed verification is long, this entry links to the skill-local reference that owns it>

## Success Criteria

- <What must be true for this skill to count as complete>
- <What must remain out of scope or unchanged>

## Safety

- <What the agent must avoid>
- <Any permission, credential, network, external command, or filesystem boundary>
- <How to verify before writing files, running commands, or using credentials>
- Treat the delivery root as an explicit authorized capability. Validate names and no-follow directory/file types before mutation; never broaden cleanup from the managed set or follow a symlink to satisfy a write.
- State every external command, network, credential, package, input-read, support-read, delivery-write, `.work`-write, and verification-workdir permission. Installation or permission changes require user authorization and a post-install public-command check.
- Portable publication guarantees stop at candidate isolation, single-path replace, and tested handled rollback. Do not advertise automatic history deletion, inferred cleanup, unverified runtime discovery, or multi-file hard atomicity.
