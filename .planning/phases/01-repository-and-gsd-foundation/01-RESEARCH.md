# Phase 1: Repository and GSD Foundation - Research

**Researched:** 2026-05-30 [VERIFIED: init.phase-op]
**Domain:** 文档型仓库基础契约与 GSD 规划记录 [CITED: .planning/ROADMAP.md]
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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

### the agent's Discretion
Planner and executor may choose the exact patch shape, review checklist, and verification commands as long as they respect the decisions above and the v1 scope in `.planning/REQUIREMENTS.md`.

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DOC-01 | A contributor can read the README and understand the repository purpose, target users, and top-level structure. [CITED: .planning/REQUIREMENTS.md] | Plan must review `README.md` for a quick entry plus repository structure and constraint details. [CITED: .planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md] |
| DOC-02 | A contributor can find a directory specification that explains where skills, templates, adapters, examples, and planning files live. [CITED: .planning/REQUIREMENTS.md] | Plan must review `docs/directory-spec.md` for folder responsibilities and boundary rules, especially template/example separation and adapter placement. [CITED: .planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md] |
| DOC-03 | An agent can read `AGENTS.md` and follow the repository's language, editing, and skill-authoring rules. [CITED: .planning/REQUIREMENTS.md] | Plan must preserve Simplified Chinese behavior, runtime-neutral canonical skills, OpenClaw/Hermes consideration, and synchronized doc updates. [CITED: AGENTS.md] |
| PLAN-01 | The repository is initialized as a GSD project with project context, config, requirements, roadmap, state, and project instructions. [CITED: .planning/REQUIREMENTS.md] | Plan must verify `.planning/PROJECT.md`, `.planning/config.json`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, and `AGENTS.md` are present and aligned. [VERIFIED: init.phase-op] |
</phase_requirements>

## Summary

Phase 1 should be planned as a documentation-foundation review, not a greenfield build. The repository already contains `README.md`, `AGENTS.md`, `docs/directory-spec.md`, and the required `.planning/` files; the plan should inspect those files, patch specific gaps, and produce normal GSD execution/verification records. [VERIFIED: codebase grep] [CITED: .planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md]

The highest-risk planning mistake is scope creep into Phase 2 or Phase 3 artifacts. Templates, adapter templates, compatibility matrix details, and example skill completeness already exist as adjacent files, but Phase 1 owns only the repository contract and GSD foundation alignment. [CITED: .planning/ROADMAP.md] [VERIFIED: codebase grep]

**Primary recommendation:** Plan a short audit-and-patch wave across `README.md`, `docs/directory-spec.md`, `AGENTS.md`, and `.planning/`, followed by evidence capture that maps DOC-01, DOC-02, DOC-03, and PLAN-01 to the edited or verified files. [CITED: .planning/REQUIREMENTS.md]

## Project Constraints (from AGENTS.md)

- Respond to users in Simplified Chinese unless the user explicitly asks otherwise or the edited file format requires another language. [CITED: AGENTS.md]
- Keep documentation and templates concise, copyable, and reviewable. [CITED: AGENTS.md]
- Keep agent-specific private syntax out of canonical skill bodies; put runtime-specific differences in adapter notes. [CITED: AGENTS.md]
- Put new skills at `skills/<skill-name>/SKILL.md`, examples at `examples/<example-name>/SKILL.md`, and templates only under `templates/`. [CITED: AGENTS.md]
- When directory conventions change, update both `README.md` and `docs/directory-spec.md`. [CITED: AGENTS.md]
- When runtime support changes, update `docs/compatibility-matrix.md`. [CITED: AGENTS.md]
- Skill `description` fields must explain when to use the skill and avoid marketing copy. [CITED: AGENTS.md]
- A skill should serve one clear workflow; long background goes in `references/`, scripts in `scripts/`, and output templates in `templates/`. [CITED: AGENTS.md]
- Skills involving external commands, network, credentials, or file writes must state safety boundaries and verification steps. [CITED: AGENTS.md]
- OpenClaw and Hermes Agent must be considered for new skills, not treated as optional afterthoughts. [CITED: AGENTS.md]
- Before executing a new phase, read `.planning/ROADMAP.md` and `.planning/STATE.md`. [CITED: AGENTS.md]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Human-facing repository entry | Documentation | GSD planning | `README.md` is the contributor entry point and should align with roadmap scope. [CITED: README.md] [CITED: .planning/ROADMAP.md] |
| Directory ownership contract | Documentation | Repository filesystem | `docs/directory-spec.md` defines where artifacts belong and what must not be mixed. [CITED: docs/directory-spec.md] |
| Agent behavior constraints | Agent instruction layer | Documentation | `AGENTS.md` is the authoritative project rule file for agent language, edits, and skill authoring. [CITED: AGENTS.md] |
| GSD project state | GSD planning layer | Documentation | `.planning/` owns requirements, roadmap, state, config, and phase records. [CITED: .planning/PROJECT.md] [VERIFIED: init.phase-op] |

## Standard Stack

### Core

| Tool / Format | Version | Purpose | Why Standard |
|---------------|---------|---------|--------------|
| Markdown | n/a | Repository documentation, planning records, templates, and skills. [VERIFIED: codebase grep] | Existing project artifacts are Markdown-first and Phase 1 success criteria are documentation files. [CITED: .planning/ROADMAP.md] |
| GSD planning files | n/a | Track project purpose, requirements, roadmap, state, phase context, and phase research. [VERIFIED: init.phase-op] | PLAN-01 explicitly requires GSD project initialization with these planning records. [CITED: .planning/REQUIREMENTS.md] |
| Plain filesystem directories | n/a | Encode ownership for `skills/`, `examples/`, `templates/`, `adapters/`, `docs/`, and `.planning/`. [VERIFIED: codebase grep] | The directory contract is a central deliverable of DOC-02. [CITED: .planning/REQUIREMENTS.md] |

### Supporting

| Tool / Format | Version | Purpose | When to Use |
|---------------|---------|---------|-------------|
| `rg` | local CLI | Fast verification of file presence and text consistency. [VERIFIED: local command] | Use during planning/execution verification to confirm required files and scoped terms. [ASSUMED] |
| `sed` / Markdown read commands | local CLI | Inspect existing docs without modifying them. [VERIFIED: local command] | Use for review evidence before patching. [ASSUMED] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Manual Markdown review | Schema/lint tooling | Schema/lint tooling is explicitly deferred from v1, so Phase 1 should not add it. [CITED: .planning/REQUIREMENTS.md] |
| Existing GSD files | New planning system | PLAN-01 requires GSD project context/config/requirements/roadmap/state, so another planning system would duplicate scope. [CITED: .planning/REQUIREMENTS.md] |

**Installation:** No package installation is required for this phase. [VERIFIED: codebase grep]

## Architecture Patterns

### System Architecture Diagram

```text
Contributor or Agent
        |
        v
README.md ---------------> docs/directory-spec.md
        |                         |
        v                         v
AGENTS.md ----------------> repository file placement
        |                         |
        v                         v
.planning/PROJECT.md -> REQUIREMENTS.md -> ROADMAP.md -> STATE.md
        |
        v
Phase records: CONTEXT.md -> RESEARCH.md -> PLAN/verification artifacts
```

The planner should trace Phase 1 from requirements to files: DOC-01 maps to `README.md`, DOC-02 maps to `docs/directory-spec.md`, DOC-03 maps to `AGENTS.md`, and PLAN-01 maps to `.planning/` plus project instructions. [CITED: .planning/REQUIREMENTS.md]

### Recommended Project Structure

```text
.
├── README.md                 # contributor entry [CITED: README.md]
├── AGENTS.md                 # agent rules [CITED: AGENTS.md]
├── adapters/                 # runtime adapter guidance [CITED: docs/directory-spec.md]
├── docs/                     # durable repository docs [CITED: docs/directory-spec.md]
├── examples/                 # example skills [CITED: docs/directory-spec.md]
├── skills/                   # canonical skill sources [CITED: docs/directory-spec.md]
├── templates/                # copyable templates [CITED: docs/directory-spec.md]
└── .planning/                # GSD project records [CITED: AGENTS.md]
```

### Pattern 1: Audit Existing Baseline Before Editing

**What:** Treat current Phase 1 files as the source baseline, then patch only confirmed gaps. [CITED: .planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md]
**When to use:** Use this for every Phase 1 task because the required artifacts already exist. [VERIFIED: codebase grep]
**Example:**

```bash
rg --files README.md AGENTS.md docs .planning | sort
rg -n "OpenClaw|Hermes|简体中文|canonical|templates|examples" README.md AGENTS.md docs/directory-spec.md .planning/*.md
```

### Pattern 2: Keep Canonical Contract and Adapter Notes Separate

**What:** Keep shared skill meaning in canonical `SKILL.md` and isolate runtime differences in adapter notes or adapter docs. [CITED: AGENTS.md] [CITED: docs/compatibility-matrix.md]
**When to use:** Apply when Phase 1 wording explains repository purpose or directory boundaries. [CITED: docs/directory-spec.md]
**Example:**

```markdown
`skills/<skill-name>/SKILL.md` owns portable skill semantics.
Runtime-specific path, frontmatter, and tool differences belong in adapter notes or `adapters/`.
```

### Anti-Patterns to Avoid

- **Starting from a blank README or AGENTS.md:** Existing files are the approved baseline, and large rewrites are not the default. [CITED: .planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md]
- **Expanding into Phase 2 templates or Phase 3 examples:** Template design, compatibility matrix completion, and example skill completeness are assigned to later phases. [CITED: .planning/ROADMAP.md]
- **Mixing examples into templates:** `docs/directory-spec.md` states templates must remain placeholders and examples belong under `examples/`. [CITED: docs/directory-spec.md]
- **Putting runtime-private syntax into canonical skills:** `AGENTS.md` requires runtime-specific differences to live in adapter notes. [CITED: AGENTS.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Phase 1 verification | New schema validator or lint CLI | Manual Markdown/file audit plus GSD verification evidence | Schema/lint enforcement is v2 out of scope. [CITED: .planning/REQUIREMENTS.md] |
| Runtime compatibility proof | Runtime execution harness | Scope note pointing to Phase 2/3 docs | Runtime execution harness is deferred from v1. [CITED: .planning/REQUIREMENTS.md] |
| Alternate planning records | New tracker format | Existing `.planning/` GSD files | PLAN-01 requires GSD project context, config, requirements, roadmap, state, and instructions. [CITED: .planning/REQUIREMENTS.md] |

**Key insight:** Phase 1 succeeds by making the human and agent contracts coherent; it does not need executable tooling. [CITED: .planning/ROADMAP.md]

## Existing State Inventory

| Item | Status | Planning Implication |
|------|--------|----------------------|
| `README.md` | Present. [VERIFIED: codebase grep] | Review for two-layer contributor entry and clear top-level structure. [CITED: .planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md] |
| `docs/directory-spec.md` | Present. [VERIFIED: codebase grep] | Review for directory responsibilities, boundary rules, and common misplacements. [CITED: .planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md] |
| `AGENTS.md` | Present. [VERIFIED: codebase grep] | Preserve strong constraints and Simplified Chinese language behavior. [CITED: AGENTS.md] |
| `.planning/PROJECT.md` | Present. [VERIFIED: init.phase-op] | Ensure project purpose and constraints align with Phase 1 docs. [CITED: .planning/PROJECT.md] |
| `.planning/REQUIREMENTS.md` | Present. [VERIFIED: init.phase-op] | Use DOC-01, DOC-02, DOC-03, and PLAN-01 as acceptance anchors. [CITED: .planning/REQUIREMENTS.md] |
| `.planning/ROADMAP.md` | Present. [VERIFIED: init.phase-op] | Use Phase 1 success criteria as completion checklist. [CITED: .planning/ROADMAP.md] |
| `.planning/STATE.md` | Present. [VERIFIED: init.phase-op] | Update only if phase execution changes status through normal GSD flow. [CITED: .planning/STATE.md] |
| `.planning/config.json` | Present. [VERIFIED: init.phase-op] | `nyquist_validation` is explicitly false, so no Validation Architecture section is needed. [CITED: .planning/config.json] |
| `CLAUDE.md` | Not present. [VERIFIED: codebase grep] | No Claude-specific project instruction file needs Phase 1 alignment. [VERIFIED: codebase grep] |
| `.claude/skills/` and `.agents/skills/` | Not present in this repo. [VERIFIED: codebase grep] | No project-local skill rules need to be loaded for Phase 1. [VERIFIED: codebase grep] |
| `.planning/graphs/graph.json` | Not present. [VERIFIED: codebase grep] | No graph context is available for this phase. [VERIFIED: codebase grep] |

## Common Pitfalls

### Pitfall 1: Treating Baseline Files as Empty Work

**What goes wrong:** The plan creates wholesale replacements instead of targeted patches. [CITED: .planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md]
**Why it happens:** Phase 1 sounds foundational, but the required files already exist. [VERIFIED: codebase grep]
**How to avoid:** Start with a read-and-diff task for each required artifact before proposing edits. [ASSUMED]
**Warning signs:** A plan task says "create README" without first saying "review current README". [ASSUMED]

### Pitfall 2: Expanding Into Later Phase Scope

**What goes wrong:** The plan redesigns templates, adapter matrices, or example skills during Phase 1. [CITED: .planning/ROADMAP.md]
**Why it happens:** Related files are adjacent and already present. [VERIFIED: codebase grep]
**How to avoid:** Limit Phase 1 tasks to repository contract consistency and GSD record alignment. [CITED: .planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md]
**Warning signs:** Tasks mention scaffold CLI, schema linting, runtime execution harnesses, or publishing. [CITED: .planning/REQUIREMENTS.md]

### Pitfall 3: Letting AGENTS.md Become Too Procedural

**What goes wrong:** Agent rules turn into a long process checklist instead of a durable constraint file. [CITED: .planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md]
**Why it happens:** It is tempting to move GSD process details into project instructions. [ASSUMED]
**How to avoid:** Keep `AGENTS.md` focused on language, editing, skill authoring, runtime compatibility, and synchronization rules. [CITED: AGENTS.md]
**Warning signs:** `AGENTS.md` duplicates commit workflow or phase execution minutiae. [CITED: .planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md]

## Code Examples

Verified local commands for planner/executor tasks:

### File Presence Audit

```bash
rg --files README.md AGENTS.md docs .planning | sort
```

### Requirement Keyword Audit

```bash
rg -n "DOC-01|DOC-02|DOC-03|PLAN-01|OpenClaw|Hermes|简体中文|canonical|adapter|templates|examples" README.md AGENTS.md docs/directory-spec.md .planning/*.md
```

### Phase Output Audit

```bash
rg --files .planning/phases/01-repository-and-gsd-foundation
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Runtime-specific skill copies | Canonical `SKILL.md` plus runtime adapter guidance | v1 project initialization on 2026-05-30. [CITED: .planning/PROJECT.md] | Phase 1 docs must reinforce portability and avoid vendor-specific canonical content. [CITED: AGENTS.md] |
| Automation-first repository setup | Documentation-first repository contract | v1 project initialization on 2026-05-30. [CITED: .planning/PROJECT.md] | Phase 1 should not add scaffold CLI, schema linting, or runtime harnesses. [CITED: .planning/REQUIREMENTS.md] |

**Deprecated/outdated:** No deprecated local implementation pattern was found for Phase 1. [VERIFIED: codebase grep]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `rg`, `sed`, and manual Markdown inspection are sufficient verification tools for this documentation-only phase. [ASSUMED] | Standard Stack, Common Pitfalls | Planner may under-specify verification if stricter project tooling is later introduced. |
| A2 | A warning sign for poor planning is a task that creates files without reviewing existing files first. [ASSUMED] | Common Pitfalls | Planner may treat this as a hard rule rather than a planning heuristic. |

## Open Questions (RESOLVED)

1. **Should Phase 1 update `.planning/STATE.md` during execution?**
   - What we know: `.planning/STATE.md` currently says Phase 1 is ready for execution. [CITED: .planning/STATE.md]
   - Resolution: Do not manually change `.planning/STATE.md` unless execution evidence shows a concrete alignment issue or the normal GSD workflow transition updates it. [RESOLVED]
   - Plan impact: Phase 1 execution should audit `.planning/STATE.md` for PLAN-01 presence/alignment, but should preserve its workflow status until normal GSD execution or transition records the next state. [RESOLVED]

## Environment Availability

No external dependency is required beyond local file reads/writes and shell inspection for this documentation-foundation phase. [VERIFIED: codebase grep]

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `gsd-sdk` | Phase context initialization and optional commit helper | yes [VERIFIED: local command] | not captured [ASSUMED] | Manual file writing and git commands |
| `rg` | Fast file/text audit | yes [VERIFIED: local command] | not captured [ASSUMED] | `find` and shell text reads |

**Missing dependencies with no fallback:** None found. [VERIFIED: local command]

**Missing dependencies with fallback:** None found. [VERIFIED: local command]

## Validation Architecture

Skipped because `.planning/config.json` sets `workflow.nyquist_validation` to `false`. [CITED: .planning/config.json]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | Phase 1 has no authentication surface. [CITED: .planning/ROADMAP.md] |
| V3 Session Management | no | Phase 1 has no session surface. [CITED: .planning/ROADMAP.md] |
| V4 Access Control | no | Phase 1 has no runtime access-control implementation. [CITED: .planning/ROADMAP.md] |
| V5 Input Validation | yes | Review Markdown content for scope and path correctness; no executable input parser is added. [CITED: .planning/ROADMAP.md] |
| V6 Cryptography | no | Phase 1 has no cryptographic implementation. [CITED: .planning/ROADMAP.md] |

### Known Threat Patterns for Documentation-Only Repository Setup

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Instruction drift in agent rules | Tampering | Keep `AGENTS.md` explicit and aligned with README/directory spec. [CITED: AGENTS.md] |
| Unsafe skill guidance copied into canonical templates | Elevation of Privilege | Keep safety boundaries and runtime-specific permissions in skill/adapter documentation. [CITED: AGENTS.md] |
| Scope creep into executable tooling | Tampering | Keep scaffold CLI, schema linting, and runtime harnesses deferred. [CITED: .planning/REQUIREMENTS.md] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md` — locked decisions, discretion, deferred scope, and baseline strategy.
- `.planning/REQUIREMENTS.md` — DOC-01, DOC-02, DOC-03, PLAN-01, v1/v2 scope split.
- `.planning/ROADMAP.md` — Phase 1 goal, mode, requirements, success criteria, and later-phase boundaries.
- `.planning/PROJECT.md` — project purpose, constraints, current context, and key decisions.
- `.planning/STATE.md` — current phase and workflow preferences.
- `.planning/config.json` — workflow settings, including `nyquist_validation: false`.
- `AGENTS.md` — project language, editing, skill-authoring, synchronization, and GSD workflow rules.
- `README.md` — current repository entry and structure overview.
- `docs/directory-spec.md` — current directory ownership contract.
- Local file audit via `rg --files`, `find`, and `init.phase-op` — artifact presence, missing `CLAUDE.md`, missing project-local skill directories, missing graph file.

### Secondary (MEDIUM confidence)

- `docs/compatibility-matrix.md` — adjacent Phase 2 scope awareness and canonical-source-plus-adapters consistency check.
- `adapters/README.md`, `templates/skill/SKILL.md`, `templates/adapter/runtime-adapter.md`, `examples/portable-skill/SKILL.md` — adjacent files used only to prevent Phase 1 scope bleed.

### Tertiary (LOW confidence)

- None. No network research was used because the user requested local repository review unless required.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no external package stack; all required artifacts were verified locally. [VERIFIED: codebase grep]
- Architecture: HIGH — ownership is directly stated by requirements, roadmap, AGENTS.md, and directory spec. [CITED: .planning/REQUIREMENTS.md] [CITED: docs/directory-spec.md]
- Pitfalls: MEDIUM — scope pitfalls are documented in the phase context and requirements, while some warning signs are planning heuristics. [CITED: .planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md] [ASSUMED]

**Research date:** 2026-05-30
**Valid until:** 2026-06-29 for this documentation-foundation phase, unless Phase 2 changes directory or runtime support conventions first. [ASSUMED]
