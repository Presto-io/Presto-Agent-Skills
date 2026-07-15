# Phase 44: Verification Gate, Runtime Notes, and UAT - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-15
**Phase:** 44-verification-gate-runtime-notes-and-uat
**Areas discussed:** Public verification evidence contract, Negative cases and dependency readiness, Canonical skill and six-runtime guidance, Manual viewer UAT acceptance

---

## Public Verification Evidence Contract

| Option | Description | Selected |
|--------|-------------|----------|
| Caller workdir with separated delivery/evidence | Explicit workdir contains a clean delivery pair plus verification-owned evidence/work areas | ✓ |
| Repository build directory | Persist all evidence under a repository-controlled build path | |
| Public delivery root | Put evidence beside the user's final Markdown/PPTX | |

**User's choice:** Auto-selected the recommended caller-workdir boundary.
**Notes:** Evidence is bounded JSON plus human-readable Markdown derived from observed values; stale evidence cannot satisfy a fresh run.

---

## Negative Cases and Dependency Readiness

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed exact registry | Required and called gate/case order must match exactly; any unexpected success fails | ✓ |
| Dynamic discovery | Run whatever checks are currently registered | |
| Advisory checks | Report failures without failing the command | |

**User's choice:** Auto-selected the fixed exact registry.
**Notes:** Required dependencies are reported without auto-install; optional Pandoc is recorded honestly. All destructive negative fixtures use isolated copies.

---

## Canonical Skill and Six-Runtime Guidance

| Option | Description | Selected |
|--------|-------------|----------|
| Canonical adapter notes | One concise SKILL.md plus deeper references and one six-runtime table | ✓ |
| Separate adapter files | Create one file per runtime | |
| Runtime-specific skill copies | Duplicate the skill for each runtime | |

**User's choice:** Auto-selected the canonical semantic-source pattern already required by the repository.
**Notes:** Every runtime row covers discovery, support files, invocation fallback, dependencies, permissions, sandbox/allowlist, external commands, and write boundaries. OpenClaw and Hermes remain mandatory.

---

## Manual Viewer UAT Acceptance

| Option | Description | Selected |
|--------|-------------|----------|
| One real viewer minimum | PowerPoint or WPS with viewer/version/OS, hashes, tester, and checklist evidence | ✓ |
| Both viewers required | Require PowerPoint and WPS before acceptance | |
| Automated reopen only | Treat python-pptx/OOXML reopen as visual acceptance | |

**User's choice:** Auto-selected the roadmap minimum of at least one real compatible viewer.
**Notes:** UAT is blocking and cannot be auto-approved. Failures become explicit gaps; a second viewer is optional comparative evidence.

## Claude's Discretion

- Exact internal verification module names and evidence filenames.
- Markdown formatting of the human summary alongside required machine-readable evidence.

## Deferred Ideas

None.
