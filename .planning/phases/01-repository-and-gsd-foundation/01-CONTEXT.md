# Phase 1: Repository and GSD Foundation - Context

**Gathered:** 2026-05-30
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers the repository foundation contract: `README.md`, `AGENTS.md`, `docs/directory-spec.md`, and the existing `.planning/` project files should be reviewed as the baseline, corrected where needed, and brought into alignment with the GSD record. It does not add automation, schema validation, runtime test harnesses, publishing, or new skill authoring features beyond the foundation already scoped in the roadmap.

</domain>

<decisions>
## Implementation Decisions

### Phase Completion Approach
- **D-01:** Treat the existing Phase 1 files as the baseline. The next plan should review them, patch gaps, and bring GSD records into alignment rather than starting from a blank slate.
- **D-02:** Existing documentation may be changed when review finds real gaps or inconsistencies, but large rewrites are not the default.

### README Structure
- **D-03:** Use a two-layer README structure: a quick contributor entry at the top, followed by enough repository structure and constraint detail for contributors who need the fuller contract.

### Directory Specification
- **D-04:** `docs/directory-spec.md` should document directory responsibilities plus boundary rules. It should explain what belongs in `skills/`, `examples/`, `templates/`, adapter notes, `references/`, and `scripts/`, and call out common misplacements such as mixing examples into templates.
- **D-05:** Keep the directory spec concise enough to remain reviewable; it should not become a full operation manual.

### Agent Instructions
- **D-06:** `AGENTS.md` should be a strong constraint file, not a light reminder. It must preserve Simplified Chinese response behavior, require canonical skill bodies to stay runtime-neutral, require OpenClaw and Hermes Agent consideration, and require synchronized updates when directory conventions or runtime support change.
- **D-07:** Avoid overloading `AGENTS.md` with detailed execution checklists or commit-process minutiae.

### GSD Record Alignment
- **D-08:** Because Phase 1 artifacts already exist but Phase 1 lacks GSD plan/summary records, planning should explicitly account for review-and-record alignment: use current files as input, make needed fixes, then produce normal GSD summary and verification artifacts.

### Claude's Discretion
Planner and executor may choose the exact patch shape, review checklist, and verification commands as long as they respect the decisions above and the v1 scope in `.planning/REQUIREMENTS.md`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Planning
- `.planning/PROJECT.md` — Defines project purpose, active scope, constraints, and key decisions.
- `.planning/REQUIREMENTS.md` — Defines v1 requirements and explicitly deferred v2 scope.
- `.planning/ROADMAP.md` — Defines Phase 1 goals and success criteria.
- `.planning/STATE.md` — Records current workflow state and next-step expectations.

### Repository Contract
- `README.md` — Current human-facing repository entry and structure overview.
- `AGENTS.md` — Current agent-facing rules, language behavior, editing rules, and skill authoring constraints.
- `docs/directory-spec.md` — Current directory responsibility specification.

### Related Scope Awareness
- `docs/compatibility-matrix.md` — Phase 2-owned runtime compatibility document; useful only to avoid conflicting with already-written runtime support notes.
- `templates/skill/SKILL.md` — Phase 2-owned canonical skill template; do not expand Phase 1 scope into template redesign.
- `templates/adapter/runtime-adapter.md` — Phase 2-owned adapter template; do not expand Phase 1 scope into adapter redesign.
- `examples/portable-skill/SKILL.md` — Phase 3-owned example skill; do not expand Phase 1 scope into example redesign.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Existing documentation files already cover much of Phase 1: `README.md`, `AGENTS.md`, `docs/directory-spec.md`, and `.planning/` are present and should be reviewed before editing.

### Established Patterns
- Documentation is concise, Markdown-first, and Chinese-language by default.
- The repository uses a canonical-source-plus-adapters strategy: one canonical `SKILL.md` body with runtime-specific differences isolated into adapter notes.
- The project is documentation-first in v1; automation, validation, and distribution are deferred.

### Integration Points
- If directory rules change, update both `README.md` and `docs/directory-spec.md`.
- If runtime support expectations change, update `docs/compatibility-matrix.md`.
- If skill-authoring rules change, ensure `AGENTS.md` stays aligned with project purpose and requirements.

</code_context>

<specifics>
## Specific Ideas

- The user chose "review and supplement existing baseline" for Phase 1 completion.
- The user chose "two-layer structure" for README depth.
- The user chose "responsibilities plus boundary rules" for the directory specification.
- The user chose "strong constraint file" for `AGENTS.md`.
- The user chose "review and supplement GSD records" for Phase 1 record alignment.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 1-Repository and GSD Foundation*
*Context gathered: 2026-05-30*
