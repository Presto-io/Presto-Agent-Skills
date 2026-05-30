# Phase 2: Canonical Skill Format and Runtime Adapters - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-30
**Phase:** 2-Canonical Skill Format and Runtime Adapters
**Areas discussed:** Canonical template strictness, adapter information placement, compatibility matrix trust level, contributor path

---

## Canonical Template Strictness

| Option | Description | Selected |
|--------|-------------|----------|
| Single `SKILL.md` as main artifact | Keep one copyable skill file as the cross-agent source of truth. | yes |
| More structured adapter model | Add more explicit adapter layers or generated wrapper concepts. | |
| Broad compatibility documentation | Expand docs around many runtime-specific cases. | |

**User's choice:** "我只需要一个 skill.md 文件能够适配不同的 agent，其他设计都是多余的，只需保证该技能安装后能直接适配其 agent 主体"
**Notes:** User clarified that Phase 2 should not grow an extra adapter architecture. The goal is direct cross-agent usability from one skill file.

---

## Adapter Information Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal install/use notes | Keep only the runtime notes necessary for the same skill file to work after installation. | yes |
| Separate per-runtime adapter structure | Create explicit runtime adapter documents as a main design surface. | |
| Generated wrappers | Generate runtime-specific files from the canonical source. | |

**User's choice:** "我希望就跟大部分技能一样，能在不同的agent里直接使用，没有其他要求"
**Notes:** Any runtime differences should be framed as installation/loading compatibility notes, not as a new design layer.

---

## Compatibility Matrix Trust Level

| Option | Description | Selected |
|--------|-------------|----------|
| Required targets with practical notes | Preserve all six required runtimes and say what must be checked during installation. | yes |
| Claim full verified support everywhere | Present every runtime as fully verified even where local behavior is not tested. | |
| Expand into research-heavy runtime specs | Turn the matrix into detailed runtime research for each agent. | |

**User's choice:** Inferred from the single-file direction and "没有其他要求".
**Notes:** Documentation should avoid inventing extra requirements. When a runtime cannot be guaranteed locally, record the installation check without expanding scope.

---

## Contributor Path

| Option | Description | Selected |
|--------|-------------|----------|
| Copy one `SKILL.md` template | Contributor starts from `templates/skill/SKILL.md` and installs the resulting skill into target agents. | yes |
| Multi-document authoring workflow | Contributor must fill a skill template plus separate adapter documents. | |
| Tool-driven scaffold workflow | Contributor uses a CLI or generator to produce runtime-specific artifacts. | |

**User's choice:** Inferred from "一个 skill.md 文件" and "没有其他要求".
**Notes:** The contributor path should be simple and copyable. Tooling and generated wrappers remain out of scope.

## Claude's Discretion

- Exact wording and document organization may be chosen during planning/execution.
- Planner should avoid broadening Phase 2 into adapter architecture work.

## Deferred Ideas

- Scaffold CLI, validation tooling, generated wrappers, runtime harnesses, and publishing workflows remain deferred by v1 scope.
