# Phase 17: Skill Entry and Reference Decomposition - Research

**Researched:** 2026-06-13
**Status:** Complete
**Source:** `/gsd:plan-phase 17` research step equivalent, executed inline in Codex runtime

## Question

What do we need to know to plan Phase 17 well?

## Current Entry Weight

Line counts before Phase 17 implementation:

| File | Lines | Notes |
|------|------:|-------|
| `skills/end-of-term-teaching-materials/SKILL.md` | 135 | Already has several references, but still includes long process/output/verification detail. |
| `skills/gongwen/SKILL.md` | 117 | Inline frontmatter fields, control syntax, numbering rules, script renderer constraints. |
| `skills/jiaoan-jihua/SKILL.md` | 107 | Inline frontmatter fields, body grammar, calendar/rendering rules. |
| `skills/jiaoan-shicao/SKILL.md` | 112 | Inline field list and full document section grammar. |
| `skills/school-presentation/SKILL.md` | 140 | Large renderer, playback, structured layout, presenter markup, PDF export, and verification detail. |
| `templates/skill/SKILL.md` | 77 | Needs stronger entry/reference/scripts/templates boundary guidance. |
| `docs/directory-spec.md` | 58 | Defines directories but does not clearly state entry vs reference content thresholds. |

## Existing Patterns

- Current skills share a canonical frontmatter pattern and six runtime targets.
- `skills/end-of-term-teaching-materials/references/` already holds detailed data and template notes, making it the clearest local precedent.
- `templates/<skill>/*-full.md` files are output templates, not references. They should stay under `templates/`.
- Script commands are already skill-local and should not be decomposed in Phase 17.

## Implementation Implications

1. Add skill-local reference files:
   - `skills/gongwen/references/format-and-rendering.md`
   - `skills/jiaoan-shicao/references/format-and-rendering.md`
   - `skills/jiaoan-jihua/references/format-and-rendering.md`
   - `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md`
   - `skills/school-presentation/references/authoring-and-layout.md`
   - `skills/school-presentation/references/playback-and-export.md`
   - `skills/school-presentation/references/verification-contract.md`
2. Update each affected `SKILL.md` to reference those files from `Inputs`, `Process`, `Outputs`, `Verification`, or `Safety`.
3. Keep OpenClaw and Hermes Agent adapter rows in the entry and update them to mention reference discovery when useful.
4. Update `templates/skill/SKILL.md`, `docs/directory-spec.md`, and `README.md` with the lightweight-entry pattern.

## Risks

- Moving text can accidentally drop behavior. Mitigation: preserve all detailed rules in references and run grep checks for key phrases.
- Runtime notes can become less visible. Mitigation: keep full runtime table in every entry.
- Phase 18 script work can creep in. Mitigation: do not edit script internals; only run existing scripts for smoke verification.

## Research Complete

The phase can be planned as one documentation/refactor plan with three implementation tasks: create references, slim entries, update contributor guidance.
