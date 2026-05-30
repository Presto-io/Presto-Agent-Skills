# Phase 3: Portable Example Skill - Context

**Gathered:** 2026-05-30
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase was originally scoped to provide a concrete portable example skill. The user has now clarified that v1 should not add or expand example material: less is more, examples are human-facing documentation, and the repository should focus on AI skill development through the canonical `SKILL.md` contract rather than extra illustrative artifacts.

Planning should therefore treat Phase 3 as a scope-adjustment phase: reconcile the roadmap and requirements with the decision to avoid example-driven work. Do not add a larger example skill, extra example folders, or explanatory example documentation unless the user explicitly reopens that scope.

</domain>

<decisions>
## Implementation Decisions

### Example Scope
- **D-01:** Do not add a new portable example skill for v1.
- **D-02:** Do not expand the existing `examples/portable-skill/SKILL.md` into a fuller human-facing sample.
- **D-03:** Treat "少即是多" as the guiding preference for Phase 3: keep the repository lean and avoid artifacts whose primary purpose is demonstration for humans.

### Requirement Handling
- **D-04:** EX-01 and EX-02 should be reconsidered during planning because the user no longer wants example deliverables in v1.
- **D-05:** Downstream work should prefer updating planning and documentation records to reflect the reduced scope over producing an example just to satisfy the original roadmap.

### AI Skill Direction
- **D-06:** The repository's useful contract is the canonical skill format and runtime compatibility guidance already established in Phase 2.
- **D-07:** AI agents can follow the canonical `SKILL.md` contract directly; avoid adding extra instructional examples unless they serve a concrete agent workflow need.

### Claude's Discretion
Planner and executor may choose the exact minimal patch shape needed to reconcile requirements, roadmap, README/examples references, and state. They should not add new runtime adapter architecture, generated wrappers, scaffold tooling, validation tooling, or example-heavy explanations.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Planning
- `.planning/PROJECT.md` — Defines documentation-first v1 scope, supported runtimes, and deferred automation/tooling.
- `.planning/REQUIREMENTS.md` — Contains EX-01 and EX-02, which should be reconsidered based on this discussion.
- `.planning/ROADMAP.md` — Defines the original Phase 3 goal and success criteria that now conflict with the user's clarified preference.
- `.planning/STATE.md` — Records current workflow state and Phase 3 readiness.
- `.planning/phases/02-canonical-skill-format-and-runtime-adapters/02-CONTEXT.md` — Locks the single canonical `SKILL.md` strategy and minimal adapter-note approach.
- `.planning/phases/02-canonical-skill-format-and-runtime-adapters/02-01-SUMMARY.md` — Confirms Phase 2 already delivered the useful AI-facing skill contract.

### Repository Contract
- `templates/skill/SKILL.md` — Current canonical skill template; this remains the primary AI-facing authoring contract.
- `templates/adapter/runtime-adapter.md` — Optional compatibility-note template; do not expand it for Phase 3.
- `docs/compatibility-matrix.md` — Runtime compatibility guidance for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
- `README.md` — Contributor-facing overview that may need scope wording updates if example requirements are removed.
- `docs/directory-spec.md` — Directory contract that may need adjustment if examples are no longer part of v1 completion.
- `examples/README.md` — Existing example guidance; keep or simplify only if needed for consistency.
- `examples/portable-skill/SKILL.md` — Existing example file; do not expand unless the user reopens example scope.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `templates/skill/SKILL.md`: Already provides the canonical AI-facing structure for real skills.
- `docs/compatibility-matrix.md`: Already covers all six required runtimes, including OpenClaw and Hermes Agent.
- `examples/portable-skill/SKILL.md`: Already exists but should not become the center of v1 work.

### Established Patterns
- New skills should start from one canonical `SKILL.md`.
- Runtime differences belong in embedded adapter notes first.
- v1 remains documentation-first and avoids tooling, validation harnesses, generated wrappers, and publishing workflows.
- The user prefers minimalism over explanatory artifacts when the artifact does not help AI agents directly perform the work.

### Integration Points
- If EX-01 and EX-02 are removed, deferred, or reworded, update `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md`.
- If examples are no longer a v1 promise, check `README.md`, `docs/directory-spec.md`, and `examples/README.md` for wording that overstates their role.
- Use `gsd-sdk` for state changes rather than directly editing `.planning/STATE.md`.

</code_context>

<specifics>
## Specific Ideas

- User clarification: "不需要，少即是多，不需要示例，示例是给人看的，现在要你开发AI 技能，你是AI，你自己就知道该怎么干"
- The intended result is a leaner AI-skill framework, not a richer example library.

</specifics>

<deferred>
## Deferred Ideas

- Human-facing example skills can be revisited in a later phase only if there is a concrete contributor need.
- Scaffold CLI, validation tooling, generated wrappers, runtime harnesses, and publishing workflows remain deferred by v1 scope.

</deferred>

---

*Phase: 3-Portable Example Skill*
*Context gathered: 2026-05-30*
