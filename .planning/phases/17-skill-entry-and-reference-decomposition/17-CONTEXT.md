# Phase 17: Skill Entry and Reference Decomposition - Context

**Gathered:** 2026-06-13
**Status:** Ready for planning
**Source:** `/gsd:discuss-phase 17 --auto` equivalent, executed inline in Codex runtime

<domain>
## Phase Boundary

Phase 17 slims the current canonical `SKILL.md` entries while preserving their role as semantic entry points. Long format rules, renderer behavior, examples, and detailed operational notes move into skill-local `references/` files. The public skill interface, script command surface, Markdown intermediate contracts, outputs, verification intent, safety boundaries, and runtime adapter notes remain discoverable.

This phase covers SD-01 through SD-04 only. It does not split script implementations, rename commands, change flags, alter output artifacts, or perform milestone-level audit/closeout.

</domain>

<decisions>
## Implementation Decisions

### Entry Shape

- **D-01:** Each affected `SKILL.md` remains the first file a runtime or contributor reads. It must retain frontmatter, objective, use cases, inputs, concise process, script usage, runtime adapter notes, outputs, verification, success criteria, and safety.
- **D-02:** Entry files should point to named skill-local references rather than inline large field lists, syntax catalogues, renderer details, or fixture-specific behavior.
- **D-03:** References must be explicit and local to each skill. Do not introduce a global shared schema or cross-skill reference manual during this phase.

### Runtime Compatibility

- **D-04:** OpenClaw and Hermes Agent stay visible in every affected `Runtime Adapter Notes` table. Their notes must mention reference/script/template discovery and permission checks where relevant.
- **D-05:** Runtime-private syntax remains out of canonical skill workflow prose. Differences stay in adapter notes only.

### Documentation Boundary

- **D-06:** `templates/skill/SKILL.md` should teach the lightweight-entry pattern directly: concise semantic entry in `SKILL.md`, long reference material in `references/`, helper commands in `scripts/`, and output scaffolds in `templates/`.
- **D-07:** Because the directory convention is clarified, update both `docs/directory-spec.md` and `README.md` so contributor guidance stays aligned with the template.

### Claude's Discretion

The exact file names inside each skill-local `references/` directory are left to implementation judgment, provided they are descriptive, linked from the owning `SKILL.md`, and keep the moved content easy to audit.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope

- `.planning/ROADMAP.md` — Phase 17 goal, success criteria, and explicit Phase 18/19 boundaries.
- `.planning/REQUIREMENTS.md` — SD-01 through SD-04 acceptance requirements and v1.9 out-of-scope rules.
- `.planning/STATE.md` — Current milestone state and accumulated runtime compatibility decisions.
- `AGENTS.md` — Repository editing rules, language rule, and directory sync obligations.

### Existing Guidance

- `README.md` — Contributor-facing structure and add-new-skill workflow.
- `docs/directory-spec.md` — Directory ownership contract to update for entry/reference boundaries.
- `templates/skill/SKILL.md` — Canonical template to update for future skills.
- `docs/markdown-normalization-contract.md` — Shared Markdown intermediate contract referenced by document/presentation skills.

### Affected Skill Entries

- `skills/gongwen/SKILL.md` — Current gongwen entry to slim.
- `skills/jiaoan-shicao/SKILL.md` — Current practical lesson-plan entry to slim.
- `skills/jiaoan-jihua/SKILL.md` — Current teaching-schedule entry to slim.
- `skills/end-of-term-teaching-materials/SKILL.md` — Current end-of-term fixed-template entry to slim.
- `skills/school-presentation/SKILL.md` — Current presentation entry to slim.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `skills/*/templates/*-full.md`: existing Markdown intermediate examples remain the output templates and should not be duplicated into references.
- `skills/*/scripts/*.sh`: command names and invocation examples remain stable; script internals are Phase 18 scope, not Phase 17.
- Existing `skills/end-of-term-teaching-materials/references/*.md`: shows the desired local-reference pattern already used by the heaviest document skill.

### Established Patterns

- All current skills use canonical frontmatter with the same supported runtime list: Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, Hermes Agent.
- Document workflow skills normalize to Markdown first, then render Typst/PDF or HTML through skill-local scripts.
- Runtime differences are recorded in `Runtime Adapter Notes`, not in separate adapter files.

### Integration Points

- New references must be linked from each owning `SKILL.md`.
- Documentation updates must align `README.md`, `docs/directory-spec.md`, and `templates/skill/SKILL.md`.

</code_context>

<specifics>
## Specific Ideas

- Keep the slimming mechanical and reviewable: move content, link it, and avoid behavior expansion.
- Prefer one concise reference file per smaller document skill; split the largest school-presentation details into multiple references if a single reference would become too dense.

</specifics>

<deferred>
## Deferred Ideas

- Script module decomposition is Phase 18.
- README skills index, compatibility matrix review, before/after milestone evidence, and milestone audit are Phase 19 unless a narrow Phase 17 directory-sync update requires a README touch.

</deferred>

---

*Phase: 17-Skill Entry and Reference Decomposition*
*Context gathered: 2026-06-13*
