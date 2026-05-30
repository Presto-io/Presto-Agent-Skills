# Walking Skeleton — Presto Agent Skills

**Phase:** 1
**Generated:** 2026-05-30

## Capability Proven End-to-End

A contributor or agent can understand the repository purpose, find the directory contract, follow the agent rules, and locate the GSD planning baseline for authoring portable skills.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Repository form | Documentation-first skill repository | Phase 1 proves the authoring contract before adding automation, validators, or runtime harnesses. |
| Source model | Canonical `SKILL.md` plus runtime adapter notes | One semantic source reduces drift while still allowing Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent differences to be documented. |
| Contributor entry | `README.md` | Human contributors need a quick purpose statement, supported runtime list, and top-level structure before deeper docs. |
| Directory contract | `docs/directory-spec.md` | File placement rules need one durable reference covering skills, templates, adapters, examples, references, scripts, and GSD planning files. |
| Agent constraints | `AGENTS.md` | Coding agents need a strong local rule file for Simplified Chinese behavior, runtime-neutral canonical skills, and synchronization requirements. |
| Planning baseline | `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/config.json` | GSD records connect project purpose, requirements, phases, workflow state, and execution preferences. |
| Verification method | Local Markdown and file audits | Phase 1 is documentation-foundation work; network access, package installs, schema/lint tooling, runtime harnesses, UI, API, database, and deployment layers are outside the skeleton. |

## Stack Touched in Phase 1

- [x] Contributor entry — `README.md`
- [x] Directory responsibilities and boundary rules — `docs/directory-spec.md`
- [x] Agent rule surface — `AGENTS.md`
- [x] GSD project context and workflow records — `.planning/`
- [x] Local verification approach — `rg` source assertions and file presence checks

## Out of Scope (Deferred to Later Slices)

- Canonical skill template redesign or completion beyond repository-foundation alignment.
- Runtime adapter template redesign.
- Compatibility matrix completion or runtime-specific execution proof.
- Portable example skill completeness.
- Scaffold CLI, schema/lint enforcement, publishing pipeline, or runtime execution harness.
- Product-app layers such as UI routes, APIs, databases, auth, or deployment targets.

## Subsequent Slice Plan

Each later phase adds one repository capability on top of this skeleton without renegotiating the Phase 1 authoring contract:

- Phase 2: Define the reusable canonical skill format and runtime adapter compatibility model.
- Phase 3: Add a portable example skill that demonstrates the repository conventions across supported runtimes.
