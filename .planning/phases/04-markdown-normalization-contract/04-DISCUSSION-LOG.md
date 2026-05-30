# Phase 4: Markdown Normalization Contract - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-31
**Phase:** 4-Markdown Normalization Contract
**Areas discussed:** Shared Markdown IR contract

---

## Shared Markdown IR Contract

| Option | Description | Selected |
|--------|-------------|----------|
| YAML frontmatter + body | Markdown intermediate state uses YAML metadata plus document body. | ✓ |
| Normalize all inputs first | Arbitrary source material becomes persistent Markdown before target generation. | ✓ |
| Generate outputs through scripts | Skill-owned scripts transform Markdown into stable Typst or HTML output. | ✓ |
| Add more global constraints | Require shared fields or markers beyond the three core rules. | |

**User's choice:** Lock only the first three shared rules. Leave all remaining metadata, template fields, warning markers, and rendering conventions free for each template or skill.
**Notes:** The user clarified that the goal is not to create a rigid Markdown schema. The goal is a stable, durable intermediate state that humans and AI agents can both modify, with deterministic script-based output generation afterward.

---

## Claude's Discretion

- Choose concise wording and document placement for the normalization contract.
- Keep the contract minimal and avoid imposing global field lists or template-specific constraints.

## Deferred Ideas

None.
