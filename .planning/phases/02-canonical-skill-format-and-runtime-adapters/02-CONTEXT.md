# Phase 2: Canonical Skill Format and Runtime Adapters - Context

**Gathered:** 2026-05-30
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers the portable skill contract for v1: a contributor should be able to author one canonical `SKILL.md` file and install/use that same skill across the supported agent runtimes wherever the runtime can consume skill folders. The phase should keep adapter-related material minimal and practical: only document the compatibility notes needed for the skill to work after installation in each agent. It does not introduce a separate adapter architecture, generated wrappers, scaffold CLI, validation tooling, runtime execution harnesses, or publishing workflow.

</domain>

<decisions>
## Implementation Decisions

### Single-File Skill Contract
- **D-01:** The primary product of Phase 2 is a single portable `SKILL.md` format, not a multi-layer adapter system.
- **D-02:** The canonical `SKILL.md` should be written so that, like most skills, it can be directly installed and used by different agents with as little extra runtime-specific handling as possible.
- **D-03:** Runtime-specific material should be limited to necessary compatibility notes that help each agent load or interpret the same skill after installation.

### Adapter Scope
- **D-04:** Do not design extra adapter abstractions beyond what is necessary to document installation/use differences.
- **D-05:** If a runtime needs a different path or discovery mechanism, document that as an installation/loading note while preserving one source skill file.
- **D-06:** Avoid duplicating skill logic into per-runtime files. The `SKILL.md` remains the semantic source of truth.

### Template Direction
- **D-07:** `templates/skill/SKILL.md` should become the central artifact contributors copy from.
- **D-08:** Any adapter template or compatibility matrix updates should support the single-file story, not compete with it.
- **D-09:** Keep template and documentation language simple, direct, and install-oriented: "write this one skill file, install it into the agent's skill location, verify the agent can use it."

### Compatibility Expectations
- **D-10:** Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent remain required v1 targets.
- **D-11:** OpenClaw and Hermes Agent must still be considered first-class targets, but only through the same single-file compatibility framing.
- **D-12:** Where exact runtime behavior is not verified locally, documentation should say what must be checked during installation instead of inventing a richer adapter design.

### Claude's Discretion
Planner and executor may choose the exact wording and document patch shape, but must preserve the user's constraint: one `SKILL.md` should be the main cross-agent artifact, and other design should be minimized.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Planning
- `.planning/PROJECT.md` — Defines the project purpose, v1 scope, supported runtimes, and deferred automation/tooling.
- `.planning/REQUIREMENTS.md` — Defines Phase 2 requirements TMPL-01, TMPL-02, RT-01, RT-02, and RT-03.
- `.planning/ROADMAP.md` — Defines Phase 2 goal and success criteria.
- `.planning/STATE.md` — Records the current phase and workflow preferences.
- `.planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md` — Carries forward Phase 1 decisions about documentation-first scope, runtime-neutral canonical bodies, and concise repository contracts.

### Repository Contract
- `AGENTS.md` — Defines repository editing rules, skill authoring rules, and required consideration of OpenClaw and Hermes Agent.
- `README.md` — Current contributor entry point and single-source-plus-adapters overview.
- `docs/directory-spec.md` — Defines where skills, templates, adapters, examples, references, scripts, and templates belong.

### Phase 2 Artifacts
- `templates/skill/SKILL.md` — Primary template to update as the copyable single-file skill source.
- `templates/adapter/runtime-adapter.md` — Existing adapter template; update only insofar as it supports minimal install/use compatibility notes.
- `docs/compatibility-matrix.md` — Runtime compatibility document that should explain how the same `SKILL.md` is used across required runtimes.
- `adapters/README.md` — Adapter responsibility overview; may need simplification or rewording so it does not imply a heavy adapter architecture.
- `templates/README.md` — Template index; should point contributors toward the canonical `SKILL.md` as the main artifact.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `templates/skill/SKILL.md` already contains the expected canonical sections and runtime notes table; it can be tightened into the central single-file template.
- `templates/adapter/runtime-adapter.md` already captures loading path, invocation, tools, mapping, limitations, and verification; it may be too heavy for the user's desired v1 shape unless positioned as optional/minimal compatibility documentation.
- `docs/compatibility-matrix.md` already lists all six required runtimes and has references for each. It should be aligned to the simpler "same skill file, runtime install notes" story.

### Established Patterns
- Documentation is Markdown-first, concise, and intended to be easy to copy/review.
- v1 is documentation-first; scaffold CLI, schema/lint enforcement, execution harnesses, and publishing are explicitly deferred.
- Runtime-specific syntax should not leak into the canonical skill body unless it is clearly framed as compatibility guidance.

### Integration Points
- If Phase 2 changes template strategy, update `README.md`, `templates/README.md`, `docs/directory-spec.md`, `docs/compatibility-matrix.md`, and relevant files under `templates/`.
- If runtime support wording changes, preserve the required targets: Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.

</code_context>

<specifics>
## Specific Ideas

- The user explicitly wants one `SKILL.md` file that adapts to different agents.
- The user does not want extra adapter design beyond what is necessary.
- The intended experience is: after a skill is installed into an agent, the agent can directly use it like most skills.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. Automation, generated wrappers, validation tooling, runtime harnesses, and publishing remain deferred by project requirements.

</deferred>

---

*Phase: 2-Canonical Skill Format and Runtime Adapters*
*Context gathered: 2026-05-30*
