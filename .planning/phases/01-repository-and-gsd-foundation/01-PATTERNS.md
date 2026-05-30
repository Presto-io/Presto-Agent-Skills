# Phase 1: Repository and GSD Foundation - Pattern Map

**Mapped:** 2026-05-30
**Files analyzed:** 10
**Analogs found:** 10 / 10

## File Classification

| New/Modified/Verified File | Role | Data Flow | Closest Analog | Match Quality |
|----------------------------|------|-----------|----------------|---------------|
| `README.md` | documentation/config | request-response | `README.md` | exact baseline |
| `docs/directory-spec.md` | documentation/config | transform | `docs/directory-spec.md` | exact baseline |
| `AGENTS.md` | config | request-response | `AGENTS.md` | exact baseline |
| `.planning/PROJECT.md` | config | batch | `.planning/PROJECT.md` | exact baseline |
| `.planning/REQUIREMENTS.md` | config | transform | `.planning/REQUIREMENTS.md` | exact baseline |
| `.planning/ROADMAP.md` | config | transform | `.planning/ROADMAP.md` | exact baseline |
| `.planning/STATE.md` | config | event-driven | `.planning/STATE.md` | exact baseline |
| `.planning/config.json` | config | batch | `.planning/config.json` | exact baseline |
| `.planning/phases/01-repository-and-gsd-foundation/01-SUMMARY.md` | documentation/config | batch | `.planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md` | role-match |
| `.planning/phases/01-repository-and-gsd-foundation/01-VERIFICATION.md` | test/documentation | batch | `.planning/phases/01-repository-and-gsd-foundation/01-RESEARCH.md` | role-match |

## Pattern Assignments

### `README.md` (documentation/config, request-response)

**Analog:** `README.md`

**Quick entry pattern** (lines 1-14):
```markdown
# Presto Agent Skills

Presto Agent Skills 是一个面向多类 AI agent 的技能仓库框架。目标是让一个技能先以统一的 canonical `SKILL.md` 写成，再通过 runtime adapter 说明适配到不同 agent。

首批支持目标：

- Codex
- Claude Code
- Gemini CLI
- OpenCode
- OpenClaw
- Hermes Agent

其中 OpenClaw 和 Hermes Agent 是 v1 必须支持的目标。
```

**Principles pattern** (lines 16-22):
```markdown
## 设计原则

1. **统一源文件优先**：每个技能先写 canonical `SKILL.md`，避免维护多份语义漂移的技能。
2. **适配层隔离差异**：各 agent 的路径、frontmatter、工具调用、子代理、用户问询等差异写进 adapter notes。
3. **渐进披露**：`description` 要短而准确，正文只写必要流程，大块参考资料放到 `references/`。
4. **安全默认**：技能可能改变 agent 的行为和可执行能力，第三方技能必须先审阅再启用。
5. **先文档契约，后自动化**：v1 先稳定目录、模板、示例和 GSD 规划，脚手架与校验器后续再加。
```

**Directory tree pattern** (lines 24-53):
````markdown
## 仓库结构

```text
.
├── AGENTS.md
├── README.md
├── adapters/
│   └── README.md
├── docs/
│   ├── compatibility-matrix.md
│   └── directory-spec.md
├── examples/
│   ├── README.md
│   └── portable-skill/
│       └── SKILL.md
├── skills/
│   └── README.md
├── templates/
│   ├── README.md
│   ├── adapter/
│   │   └── runtime-adapter.md
│   └── skill/
│       └── SKILL.md
└── .planning/
    ├── PROJECT.md
    ├── REQUIREMENTS.md
    ├── ROADMAP.md
    ├── STATE.md
    └── config.json
```
````

**Scope guard:** keep README two-layered: quick contributor entry first, then concise structure and current milestone detail. Do not expand into Phase 2 template internals or Phase 3 example completeness.

---

### `docs/directory-spec.md` (documentation/config, transform)

**Analog:** `docs/directory-spec.md`

**Purpose sentence pattern** (lines 1-3):
```markdown
# Directory Specification

本文档定义 Presto Agent Skills 的目录职责。新增文件时优先遵守这里的归属规则。
```

**Path/Purpose table pattern** (lines 7-12):
```markdown
| Path | Purpose |
|------|---------|
| `README.md` | 给人类贡献者看的项目入口 |
| `AGENTS.md` | 给 coding agents 看的仓库规则和语言约束 |
| `.planning/` | GSD 项目规划、需求、路线图和状态 |
```

**Boundary rule pattern** (lines 17-22):
```markdown
| `skills/<skill-name>/SKILL.md` | canonical 技能源文件 |
| `skills/<skill-name>/references/` | 可按需读取的长参考资料 |
| `skills/<skill-name>/scripts/` | 技能需要调用的辅助脚本 |
| `skills/<skill-name>/templates/` | 技能输出模板或文件模板 |

`skills/` 下的内容应该尽量 runtime-neutral。遇到 runtime 差异时，在技能内的 adapter section 或 `adapters/` 中记录，而不是复制出多份语义不同的技能。
```

**Template/example separation pattern** (lines 27-31, 45-48):
```markdown
| `templates/skill/SKILL.md` | 新技能的 canonical 模板 |
| `templates/adapter/runtime-adapter.md` | 单个 runtime 适配说明模板 |

模板必须保持占位符形式，不应包含真实项目的业务逻辑。

| `examples/<example-name>/SKILL.md` | 展示 canonical 模板的真实用法 |

示例必须可读、短小，并覆盖所有必选 runtime 的 adapter notes。
```

**Scope guard:** keep this as directory responsibilities plus boundary rules, not an operation manual.

---

### `AGENTS.md` (config, request-response)

**Analog:** `AGENTS.md`

**Language constraint pattern** (lines 3-5):
```markdown
## Language

始终使用简体中文回复用户，除非用户明确要求其他语言，或正在编辑的文件格式必须使用其他语言。
```

**Project purpose pattern** (lines 7-9):
```markdown
## Project Purpose

本仓库用于沉淀可跨多类 AI agent 使用的技能。核心策略是：一个 canonical `SKILL.md` 作为语义源文件，再用 runtime adapter 说明 Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw、Hermes Agent 的差异。
```

**Editing rules pattern** (lines 11-19):
```markdown
## Editing Rules

- 优先保持文档和模板简洁、可复制、可审阅。
- 不要把某个 agent 的私有语法写进 canonical 技能主体；放到 adapter notes。
- 新技能默认放在 `skills/<skill-name>/SKILL.md`。
- 示例技能放在 `examples/<example-name>/SKILL.md`。
- 模板只放在 `templates/`，不要把示例内容和模板混在一起。
- 更新目录约定时，同步更新 `README.md` 和 `docs/directory-spec.md`。
- 如果新增 runtime 支持，同步更新 `docs/compatibility-matrix.md`。
```

**Skill authoring rules pattern** (lines 21-27):
```markdown
## Skill Authoring Rules

- `description` 必须说明什么时候使用该技能，不要写营销句。
- 一个技能只服务一个明确工作流。
- 复杂背景材料放到 `references/`，脚本放到 `scripts/`，输出模板放到 `templates/`。
- 技能涉及外部命令、网络、凭据或文件写入时，必须写明安全边界和验证步骤。
- OpenClaw 与 Hermes Agent 是必须考虑的 runtime；新增技能不能只写 Claude/Codex 说明。
```

**Scope guard:** preserve AGENTS.md as a strong constraint file. Do not add long commit-process checklists or duplicate GSD execution minutiae.

---

### `.planning/PROJECT.md` (config, batch)

**Analog:** `.planning/PROJECT.md`

**Project identity pattern** (lines 3-11):
```markdown
## What This Is

Presto Agent Skills is a portable skill repository for authoring agent skills once and adapting them across multiple AI agent runtimes. The initial targets are Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent, with OpenClaw and Hermes Agent treated as mandatory first-class compatibility targets.

The repository starts as a documentation-first framework: canonical skill templates, runtime adapter guidance, example skills, and project instructions that different agents can read without guessing the repository contract.

## Core Value

A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.
```

**Active requirements pattern** (lines 19-26):
```markdown
### Active

- [ ] Define a clear repository structure for skills, templates, adapters, examples, and GSD planning files.
- [ ] Provide a canonical `SKILL.md` authoring template that can serve as the single source of truth.
- [ ] Document adapter expectations for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
- [ ] Treat OpenClaw and Hermes Agent as mandatory supported runtimes, not optional future targets.
- [ ] Include an example portable skill showing the intended authoring style and adapter notes.
- [ ] Add project-level agent instructions through `AGENTS.md`, including the Simplified Chinese response requirement.
```

**Constraint pattern** (lines 49-53):
```markdown
- **Runtime compatibility**: OpenClaw and Hermes Agent must be represented in v1 adapter docs - they are required targets.
- **Source of truth**: Prefer one canonical skill source plus runtime adapter notes or generated wrappers - this reduces drift across agents.
- **Scope discipline**: Keep v1 documentation-first; defer CLI tooling and validation until the shape is exercised.
- **Language**: Agent-facing responses in this repository should be Simplified Chinese unless a file format or downstream runtime requires otherwise.
- **Portability**: Avoid assuming one agent's proprietary tool syntax in the canonical skill body; isolate those differences in adapter sections.
```

**Planner use:** use PROJECT as the broad alignment source when checking whether README, AGENTS, and directory spec still describe the same repository.

---

### `.planning/REQUIREMENTS.md` (config, transform)

**Analog:** `.planning/REQUIREMENTS.md`

**Requirement grouping pattern** (lines 10-14):
```markdown
### Documentation

- [ ] **DOC-01**: A contributor can read the README and understand the repository purpose, target users, and top-level structure.
- [ ] **DOC-02**: A contributor can find a directory specification that explains where skills, templates, adapters, examples, and planning files live.
- [ ] **DOC-03**: An agent can read `AGENTS.md` and follow the repository's language, editing, and skill-authoring rules.
```

**Planning requirement pattern** (lines 32-34):
```markdown
### Planning

- [ ] **PLAN-01**: The repository is initialized as a GSD project with project context, config, requirements, roadmap, state, and project instructions.
```

**Out-of-scope guard pattern** (lines 59-64):
```markdown
| Feature | Reason |
|---------|--------|
| Scaffold CLI | Useful after the canonical structure stabilizes; premature for the first framework pass |
| Schema/lint enforcement | Requires finalizing required sections and adapter metadata first |
| Runtime execution harness | Needs real runtime installations and stable adapter contracts |
| Publishing pipeline | Distribution should follow after examples and compatibility docs are useful |
```

**Traceability pattern** (lines 66-80):
```markdown
## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DOC-01 | Phase 1 | Pending |
| DOC-02 | Phase 1 | Pending |
| DOC-03 | Phase 1 | Pending |
| PLAN-01 | Phase 1 | Pending |
```

**Planner use:** Phase 1 plans should explicitly map work and verification evidence to DOC-01, DOC-02, DOC-03, and PLAN-01.

---

### `.planning/ROADMAP.md` (config, transform)

**Analog:** `.planning/ROADMAP.md`

**Phase overview pattern** (lines 11-15):
```markdown
| Phase | Name | Goal | Requirements |
|-------|------|------|--------------|
| 1 | Repository and GSD Foundation | Create the base repository contract, project instructions, and planning structure | DOC-01, DOC-02, DOC-03, PLAN-01 |
| 2 | Canonical Skill Format and Runtime Adapters | Define the reusable skill source format and compatibility model for all target runtimes | TMPL-01, TMPL-02, RT-01, RT-02, RT-03 |
| 3 | Portable Example Skill | Add a concrete example that demonstrates the repository conventions across runtimes | EX-01, EX-02 |
```

**Phase success criteria pattern** (lines 20-30):
```markdown
### Phase 1: Repository and GSD Foundation

**Goal:** Create the base repository contract, project instructions, and planning structure.
**Mode:** mvp

**Requirements:** DOC-01, DOC-02, DOC-03, PLAN-01

**Success Criteria:**
1. `README.md` explains what the repository is for and how it is organized.
2. `docs/directory-spec.md` describes the intended folders and ownership of each artifact type.
3. `AGENTS.md` gives agents clear repository instructions, including Simplified Chinese response behavior.
4. `.planning/` contains project context, configuration, requirements, roadmap, and state files.
```

**Planner use:** use this file as the phase boundary. Template internals and example skill completion are Phase 2/3, not Phase 1.

---

### `.planning/STATE.md` (config, event-driven)

**Analog:** `.planning/STATE.md`

**State frontmatter pattern** (lines 1-12):
```markdown
---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: Phase 1 - Repository and GSD Foundation
status: Ready for phase execution
last_updated: "2026-05-30T08:30:23.549Z"
progress:
  total_phases: 3
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
---
```

**Workflow preferences pattern** (lines 29-38):
```markdown
## Workflow Preferences

- Mode: YOLO
- Granularity: Coarse
- Execution: Parallel
- Planning docs committed: Yes
- Research: Yes
- Plan Check: Yes
- Verifier: Yes
- AI Models: Balanced
```

**Supported runtime pattern** (lines 40-46):
```markdown
## Supported Runtime Targets

- Codex
- Claude Code
- Gemini CLI
- OpenCode
- OpenClaw
- Hermes Agent
```

**Planner use:** update state only through the normal GSD phase transition convention. For Phase 1 planning, verify current state and avoid ad hoc status churn unless execution explicitly requires it.

---

### `.planning/config.json` (config, batch)

**Analog:** `.planning/config.json`

**Workflow configuration pattern** (lines 1-24):
```json
{
  "model_profile": "balanced",
  "commit_docs": true,
  "parallelization": true,
  "search_gitignored": false,
  "brave_search": false,
  "firecrawl": false,
  "exa_search": false,
  "git": {
    "branching_strategy": "none",
    "phase_branch_template": "gsd/phase-{phase}-{slug}",
    "milestone_branch_template": "gsd/{milestone}-{slug}",
    "quick_branch_template": null
  },
  "workflow": {
    "research": true,
    "plan_check": true,
    "verifier": true,
    "nyquist_validation": false,
```

**Mode pattern** (lines 48-50):
```json
  "mode": "yolo",
  "granularity": "coarse",
```

**Planner use:** no validation architecture or schema tooling is required because `workflow.nyquist_validation` is false and v2 explicitly defers schema/lint enforcement.

---

### `.planning/phases/01-repository-and-gsd-foundation/01-SUMMARY.md` (documentation/config, batch)

**Analog:** `.planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md`

**Phase record heading pattern** (lines 1-4):
```markdown
# Phase 1: Repository and GSD Foundation - Context

**Gathered:** 2026-05-30
**Status:** Ready for planning
```

**Decision capture pattern** (lines 15-37):
```markdown
## Implementation Decisions

### Phase Completion Approach
- **D-01:** Treat the existing Phase 1 files as the baseline. The next plan should review them, patch gaps, and bring GSD records into alignment rather than starting from a blank slate.
- **D-02:** Existing documentation may be changed when review finds real gaps or inconsistencies, but large rewrites are not the default.
```

**Canonical reference pattern** (lines 39-59):
```markdown
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Planning
- `.planning/PROJECT.md` — Defines project purpose, active scope, constraints, and key decisions.
- `.planning/REQUIREMENTS.md` — Defines v1 requirements and explicitly deferred v2 scope.
- `.planning/ROADMAP.md` — Defines Phase 1 goals and success criteria.
- `.planning/STATE.md` — Records current workflow state and next-step expectations.
```

**Planner use:** execution summary should mirror this phase-record style: title, date/status, decisions or results, files changed/verified, and clear scope boundaries.

---

### `.planning/phases/01-repository-and-gsd-foundation/01-VERIFICATION.md` (test/documentation, batch)

**Analog:** `.planning/phases/01-repository-and-gsd-foundation/01-RESEARCH.md`

**Requirement-to-evidence pattern** (lines 42-47):
```markdown
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DOC-01 | A contributor can read the README and understand the repository purpose, target users, and top-level structure. [CITED: .planning/REQUIREMENTS.md] | Plan must review `README.md` for a quick entry plus repository structure and constraint details. [CITED: .planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md] |
| DOC-02 | A contributor can find a directory specification that explains where skills, templates, adapters, examples, and planning files live. [CITED: .planning/REQUIREMENTS.md] | Plan must review `docs/directory-spec.md` for folder responsibilities and boundary rules, especially template/example separation and adapter placement. [CITED: .planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md] |
```

**Verification command pattern** (lines 146-151, 231-238):
```bash
rg --files README.md AGENTS.md docs .planning | sort
rg -n "OpenClaw|Hermes|简体中文|canonical|templates|examples" README.md AGENTS.md docs/directory-spec.md .planning/*.md
```

```bash
rg --files README.md AGENTS.md docs .planning | sort

rg -n "DOC-01|DOC-02|DOC-03|PLAN-01|OpenClaw|Hermes|简体中文|canonical|adapter|templates|examples" README.md AGENTS.md docs/directory-spec.md .planning/*.md

rg --files .planning/phases/01-repository-and-gsd-foundation
```

**Planner use:** verification should be lightweight Markdown/file audit evidence, not a new validator, runtime harness, or scaffold CLI.

## Shared Patterns

### Baseline-First Review

**Source:** `.planning/phases/01-repository-and-gsd-foundation/01-CONTEXT.md` lines 17-19
**Apply to:** `README.md`, `AGENTS.md`, `docs/directory-spec.md`, `.planning/*`

```markdown
- **D-01:** Treat the existing Phase 1 files as the baseline. The next plan should review them, patch gaps, and bring GSD records into alignment rather than starting from a blank slate.
- **D-02:** Existing documentation may be changed when review finds real gaps or inconsistencies, but large rewrites are not the default.
```

### Synchronize Directory Contract

**Source:** `AGENTS.md` lines 13-18
**Apply to:** `README.md`, `docs/directory-spec.md`, `AGENTS.md`

```markdown
- 不要把某个 agent 的私有语法写进 canonical 技能主体；放到 adapter notes。
- 新技能默认放在 `skills/<skill-name>/SKILL.md`。
- 示例技能放在 `examples/<example-name>/SKILL.md`。
- 模板只放在 `templates/`，不要把示例内容和模板混在一起。
- 更新目录约定时，同步更新 `README.md` 和 `docs/directory-spec.md`。
```

### Canonical Source Plus Adapter Notes

**Source:** `docs/compatibility-matrix.md` lines 5-12
**Apply to:** README purpose text, directory spec boundary wording, AGENTS skill-authoring constraints

```markdown
## Recommended Pattern

最佳实践是 **canonical source + runtime adapters**：

1. 用一个 canonical `SKILL.md` 表达技能语义、触发条件、流程、输出和成功标准。
2. 在 adapter notes 里记录每个 runtime 的加载路径、frontmatter 限制、工具调用差异、用户问询差异和安全限制。
3. 只有当 runtime 需要不同文件布局时，才生成专用包装层；不要手写维护多份业务逻辑。
```

### Scope Control

**Source:** `.planning/REQUIREMENTS.md` lines 59-64 and `.planning/ROADMAP.md` lines 36-56
**Apply to:** all Phase 1 plans and execution records

```markdown
| Scaffold CLI | Useful after the canonical structure stabilizes; premature for the first framework pass |
| Schema/lint enforcement | Requires finalizing required sections and adapter metadata first |
| Runtime execution harness | Needs real runtime installations and stable adapter contracts |
| Publishing pipeline | Distribution should follow after examples and compatibility docs are useful |
```

### Lightweight Verification

**Source:** `.planning/phases/01-repository-and-gsd-foundation/01-RESEARCH.md` lines 231-238
**Apply to:** Phase 1 verification artifacts

```bash
rg --files README.md AGENTS.md docs .planning | sort
rg -n "DOC-01|DOC-02|DOC-03|PLAN-01|OpenClaw|Hermes|简体中文|canonical|adapter|templates|examples" README.md AGENTS.md docs/directory-spec.md .planning/*.md
rg --files .planning/phases/01-repository-and-gsd-foundation
```

## No Analog Found

No Phase 1 file lacks a usable analog. All target files are existing baseline documents or GSD records with direct local examples.

## Metadata

**Analog search scope:** repository root Markdown files, `docs/`, `adapters/`, `skills/`, `templates/`, `examples/`, `.planning/`, `.planning/phases/01-repository-and-gsd-foundation/`
**Files scanned:** 17 local Markdown/JSON artifacts plus phase directory inventory
**Project-local skills:** none found under `.codex/skills/` or `.agents/skills/`
**Pattern extraction date:** 2026-05-30
