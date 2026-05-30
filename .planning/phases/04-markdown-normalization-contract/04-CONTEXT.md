# Phase 4: Markdown Normalization Contract - Context

**Gathered:** 2026-05-31
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase defines the shared Markdown normalization contract for document workflow skills. The contract is intentionally small: arbitrary source material is normalized into a persistent Markdown intermediate state that humans and agents can both read and edit, then skill-owned scripts transform that intermediate state into target outputs such as Typst or HTML with stable results.

This phase does not prescribe template-specific metadata fields, document schemas, rendering styles, Typst rules, HTML rules, lint tooling, or automation beyond the shared intermediate-state contract. Those details remain free for each template, skill, or later phase.

</domain>

<decisions>
## Implementation Decisions

### Shared Markdown Intermediate State
- **D-01:** The Markdown intermediate state is `YAML frontmatter + body`. Phase 4 should document that shape as the common normalization target.
- **D-02:** All source input for document workflow skills must first become this persistent Markdown intermediate state before target-format generation.
- **D-03:** The intermediate Markdown is meant to be durable and editable by both humans and AI agents, not merely a temporary prompt artifact.
- **D-04:** Skills should use their own scripts to transform the Markdown intermediate into target outputs such as Typst or HTML, so the same Markdown produces consistent rendered output.

### Freedom Left To Templates And Skills
- **D-05:** Phase 4 must not impose a universal frontmatter field list. Each template or skill may define the metadata fields it needs.
- **D-06:** Phase 4 must not over-constrain warning, ambiguity, or lossy-content markers beyond the shared Markdown intermediate-state requirement. Template-specific needs can define their own conventions.
- **D-07:** The purpose of this phase is stability through a common intermediate representation, not reducing every document workflow to one rigid schema.

### Claude's Discretion
Planner and executor may choose the exact wording and document placement, but must keep the shared contract minimal. Favor documentation that says what must be stable across all document workflow skills, while explicitly leaving template-specific metadata, flags, and rendering details flexible.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Planning
- `.planning/ROADMAP.md` — Defines Phase 4 goal, requirements, and success criteria.
- `.planning/REQUIREMENTS.md` — Defines DWF-01 and DWF-02 for Markdown normalization.
- `.planning/PROJECT.md` — Defines the v1.1 document workflow milestone and project constraints.
- `.planning/STATE.md` — Records current workflow state, supported runtimes, and prior decisions.
- `.planning/phases/03-portable-example-skill/03-CONTEXT.md` — Carries forward the lean, non-example-driven project direction.
- `.planning/phases/02-canonical-skill-format-and-runtime-adapters/02-CONTEXT.md` — Locks the canonical `SKILL.md` and minimal runtime-notes strategy.

### Repository Contract
- `README.md` — Current contributor-facing overview and single-source-plus-adapter-notes strategy.
- `docs/directory-spec.md` — Defines where persistent docs, skills, templates, references, scripts, and optional examples belong.
- `docs/compatibility-matrix.md` — Defines runtime compatibility expectations for the required agent targets.
- `templates/skill/SKILL.md` — Current canonical skill template; useful for understanding how document workflow skills should remain runtime-neutral.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `templates/skill/SKILL.md`: Provides the canonical skill structure and already includes YAML frontmatter, process, outputs, verification, and safety sections.
- `README.md`: Establishes the contributor-facing contract that new guidance should stay concise and centered on canonical skill sources.
- `docs/directory-spec.md`: Provides the directory boundary rules for deciding whether the Markdown normalization contract belongs in `docs/`, `templates/`, or skill-local supporting files.

### Established Patterns
- The repository favors one canonical source file plus lightweight runtime notes instead of duplicated per-runtime logic.
- Long or reusable guidance belongs in `docs/` or skill-local `references/`, while copied starter material belongs in `templates/`.
- v1.1 should remain documentation-first and avoid adding tooling before the contract is stable.

### Integration Points
- If Phase 4 adds a new normalization contract document, update `README.md` and `docs/directory-spec.md` only as needed to point contributors to it.
- If the canonical skill template should mention document workflow normalization, keep it brief and avoid turning the generic skill template into a document-specific schema.

</code_context>

<specifics>
## Specific Ideas

- The user clarified that Markdown is a human- and machine-friendly intermediate state used to constrain agent output stability.
- The intended flow is: arbitrary input becomes persistent Markdown, humans or AI can modify that Markdown, and skill-owned scripts generate target artifacts.
- Determinism matters: fixed scripts should convert the same Markdown into consistent Typst-rendered PDFs or consistent HTML.
- The shared contract should lock only the three basics: `YAML frontmatter + body`, normalize all input into that intermediate state, and generate target outputs from it through skill scripts.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. Template-specific frontmatter fields, warning conventions, and rendering details are intentionally left to individual templates, skills, or later phases.

</deferred>

---

*Phase: 4-Markdown Normalization Contract*
*Context gathered: 2026-05-31*
