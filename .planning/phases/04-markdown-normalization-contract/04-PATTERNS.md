# Phase 4: Markdown Normalization Contract - Pattern Map

**Mapped:** 2026-05-31
**Files analyzed:** 4
**Analogs found:** 4 / 4

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `docs/markdown-normalization-contract.md` | documentation contract | transform | `docs/compatibility-matrix.md` | exact |
| `README.md` | contributor entry documentation | discovery | `README.md` | exact |
| `docs/directory-spec.md` | repository contract documentation | discovery | `docs/directory-spec.md` | exact |
| `templates/skill/SKILL.md` | skill template | transform | `templates/skill/SKILL.md` | exact |

## Pattern Assignments

### `docs/markdown-normalization-contract.md` (documentation contract, transform)

**Analog:** `docs/compatibility-matrix.md`

**Document title and scope pattern** (`docs/compatibility-matrix.md` lines 1-4):

```markdown
# Compatibility Matrix

本矩阵记录 v1 必须考虑的 agent runtime。这里的目标不是伪装成所有平台都完全一致，而是把差异显式化。
```

Copy this concise shape for the new contract: one H1, followed by a short paragraph that defines the purpose and explicitly avoids pretending all templates/renderers are identical.

**Recommended pattern section** (`docs/compatibility-matrix.md` lines 5-13):

```markdown
## Recommended Pattern

最佳实践是 **one canonical `SKILL.md` first, runtime notes second**：

1. 用一个 canonical `SKILL.md` 表达技能语义、触发条件、流程、输出、验证和安全边界。
2. 在同一个 `SKILL.md` 的 adapter notes 中记录各 runtime 的加载路径、frontmatter 限制、工具调用、用户问询、任务/子代理和权限差异。
3. v1 不维护独立 adapter 文件；如果 notes 变长，先压缩成必要检查点并保留在 canonical 文件里。
4. 只有当 runtime 确实无法直接使用 canonical 文件时，才重新打开范围讨论 generated wrappers；v1 不实现 wrapper 生成，也不维护多份技能逻辑。
```

Adapt this to a "Required Pattern" section for Markdown normalization:

- source material must become persistent Markdown first
- the Markdown intermediate is `YAML frontmatter + body`
- humans and agents may edit that same intermediate
- skill-owned scripts generate Typst, HTML, or later targets from it

**Matrix/table pattern** (`docs/compatibility-matrix.md` lines 14-23):

```markdown
## Matrix

| Runtime | v1 Status | Same-File Strategy | Adapter Notes Must Cover |
|---------|-----------|--------------------|--------------------------|
| Codex | Required | Keep canonical workflow in `SKILL.md`; expose persistent project guidance through `AGENTS.md` or the local skill mechanism available in the installed Codex environment. | Tool equivalents, unavailable Claude-only syntax, file-write safety, and how Codex is told to read the skill. |
| Claude Code | Required | Install the same `SKILL.md` in a Claude skill folder such as `.claude/skills/<name>/SKILL.md`. | Trigger-focused `description`, frontmatter/tool allowlist, progressive disclosure, and supporting file paths. |
```

Use the same compact table style for common Markdown primitives. Suggested columns: `Primitive`, `Normalize As`, `Notes`. Keep figures and callouts behavior-level, because Phase 4 must not define renderer-specific rules.

**Detailed notes pattern** (`docs/compatibility-matrix.md` lines 25-34):

```markdown
## Runtime Notes

### Codex

- Put persistent project instructions in `AGENTS.md`.
- Keep runtime-specific command mappings out of canonical skill bodies.
- When a skill references tools, document Codex equivalents in adapter notes.
- If a Codex installation cannot auto-discover `SKILL.md`, record the project-context bridge that tells Codex to read it.
```

Use short subsections for contract details such as `Intermediate Shape`, `Supported Primitives`, `Ambiguous or Lossy Content`, and `Out of Scope`. Keep each subsection actionable and brief.

**Boundary source:** `.planning/phases/04-markdown-normalization-contract/04-CONTEXT.md` decisions D-01 through D-07 require the contract to be minimal, persistent, and behavior-first. Do not introduce a universal frontmatter field list or a global marker taxonomy.

---

### `README.md` (contributor entry documentation, discovery)

**Analog:** `README.md`

**Design principles pattern** (`README.md` lines 18-25):

```markdown
## 设计原则

1. **统一源文件优先**：每个技能先写一个 canonical `SKILL.md`，它是技能语义、流程、输出和验证标准的唯一来源。
2. **适配注释隔离差异**：各 agent 的路径、frontmatter、工具调用、子代理、用户问询等差异先写进同一个 `SKILL.md` 的 runtime notes。
3. **渐进披露**：`description` 要短而准确，正文只写必要流程，大块参考资料放到 `references/`。
4. **安全默认**：技能可能改变 agent 的行为和可执行能力，第三方技能必须先审阅再启用。
5. **先稳定契约，后扩展自动化**：v1 先稳定目录、模板和兼容性说明；示例保持可选且精简，脚手架、校验器、runtime harness、generated wrappers 和发布流程后续再加。
```

Add a concise principle or update principle 5 to mention document workflow stability through Markdown first. Keep it one sentence; avoid turning README into the full normalization contract.

**Repository tree pattern** (`README.md` lines 26-47):

````markdown
## 仓库结构

```text
.
├── AGENTS.md
├── README.md
├── docs/
│   ├── compatibility-matrix.md
│   └── directory-spec.md
```
````

Update this tree by adding `docs/markdown-normalization-contract.md` under `docs/`. Match the existing concise tree format.

**Contributor workflow pattern** (`README.md` lines 49-56):

```markdown
## 如何添加新技能

1. 复制 `templates/skill/SKILL.md` 到 `skills/<skill-name>/SKILL.md`。
2. 填写 `name`、`description`、目标、触发条件、流程、输出和成功标准。
3. 在同一个 `SKILL.md` 的 `Runtime Adapter Notes` 中补齐 Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw 和 Hermes Agent 的最小兼容说明。
```

If README mentions document workflow skills, add one short step or note that such skills must normalize source material into the Markdown intermediate before generating Typst/HTML. Do not add a long how-to here.

---

### `docs/directory-spec.md` (repository contract documentation, discovery)

**Analog:** `docs/directory-spec.md`

**Root directory table pattern** (`docs/directory-spec.md` lines 5-15):

```markdown
## Root

| Path | Purpose |
|------|---------|
| `README.md` | 给人类贡献者看的项目入口 |
| `AGENTS.md` | 给 coding agents 看的仓库规则和语言约束 |
| `docs/` | 持久化项目说明、兼容性矩阵和目录契约 |
| `examples/` | 可选参考示例目录；仅在确实需要示例时创建，不是 v1 必需交付 |
| `skills/` | canonical 技能源文件 |
| `templates/` | 可复制的占位符模板 |
| `.planning/` | GSD 项目规划、需求、路线图和状态 |
```

Update the `docs/` purpose to include the Markdown normalization contract. Keep the row compact.

**Dedicated subsection pattern** (`docs/directory-spec.md` lines 36-42):

```markdown
## Runtime Compatibility

| Path | Purpose |
|------|---------|
| `docs/compatibility-matrix.md` | 记录各 runtime 的加载路径、能力差异和注意事项 |

runtime 差异优先写进 canonical `SKILL.md` 的 `Runtime Adapter Notes`。如果未来某个 runtime 真的需要独立说明或 generated wrapper，必须先重新打开范围，记录生成规则、来源 `SKILL.md`、安全边界和验证步骤；v1 不保留独立 adapter 目录，也不默认实现 wrapper。
```

Add a similar short section, for example `## Document Workflow`, with a one-row table for `docs/markdown-normalization-contract.md` and one paragraph stating that template-specific metadata and rendering rules stay in templates/skills or later docs.

**Boundary pattern** (`docs/directory-spec.md` lines 17-26):

```markdown
## Skill Sources

| Path | Purpose |
|------|---------|
| `skills/<skill-name>/SKILL.md` | canonical 技能源文件 |
| `skills/<skill-name>/references/` | 可按需读取的长参考资料 |
| `skills/<skill-name>/scripts/` | 技能需要调用的辅助脚本 |
| `skills/<skill-name>/templates/` | 技能输出模板或文件模板 |

`skills/` 下的 `SKILL.md` 是 semantic source of truth。技能正文应该尽量 runtime-neutral；遇到 runtime 差异时，写在同一个 `SKILL.md` 的 `Runtime Adapter Notes` 中。v1 不维护独立 adapter 文件，也不要复制出多份语义不同的技能。
```

Reuse this boundary style to say document workflow scripts and template-specific conventions belong under the owning skill/template, not in a universal shared schema.

---

### `templates/skill/SKILL.md` (skill template, transform)

**Analog:** `templates/skill/SKILL.md`

**Frontmatter pattern** (`templates/skill/SKILL.md` lines 1-15):

```markdown
---
name: "<skill-name>"
description: "<When should an agent use this skill? Be specific and intent-based.>"
metadata:
  short-description: "<Short display description>"
  version: "0.1.0"
  portability: "canonical"
  supported-runtimes:
    - Codex
    - Claude Code
    - Gemini CLI
    - OpenCode
    - OpenClaw
    - Hermes Agent
---
```

Do not add Markdown normalization-specific required frontmatter fields to the generic skill template. The phase explicitly rejects a universal field list.

**Process/supporting-file pattern** (`templates/skill/SKILL.md` lines 34-40):

```markdown
## Process

1. <Step one>
2. <Step two>
3. <Step three>

Keep shared workflow logic in this file. Put long background material in `references/`, helper scripts in `scripts/`, and output templates in `templates/` only when the skill needs them.
```

If the template gets a document-workflow note, put it here as one short sentence or placeholder step. It should point to the shared contract without hard-coding Typst, HTML, field names, or marker syntax.

**Runtime adapter boundary pattern** (`templates/skill/SKILL.md` lines 42-54):

```markdown
## Runtime Adapter Notes

Use this table for concise compatibility notes. Do not duplicate the skill process into runtime-specific files unless a runtime truly cannot consume this canonical `SKILL.md` directly.

| Runtime | Notes |
|---------|-------|
| Codex | <How Codex should discover, invoke, or approximate this skill; map unavailable tools to Codex equivalents> |
```

Keep this section unchanged unless the planner has a precise reason. Markdown normalization is a workflow contract, not a runtime adapter concern.

**Verification/safety pattern** (`templates/skill/SKILL.md` lines 60-75):

```markdown
## Verification

- [ ] <Checkable success criterion for the output>
- [ ] <Checkable success criterion for runtime compatibility notes>
- [ ] <Checkable success criterion for safety boundaries>

## Success Criteria

- <What must be true for this skill to count as complete>
- <What must remain out of scope or unchanged>

## Safety

- <What the agent must avoid>
- <Any permission, credential, network, external command, or filesystem boundary>
- <How to verify before writing files, running commands, or using credentials>
```

If adding a generic document-workflow hint, prefer a verification placeholder such as "source material is normalized to the shared Markdown intermediate before target output." Keep it placeholder-style.

## Shared Patterns

### Minimal Documentation-First Scope

**Source:** `.planning/phases/03-portable-example-skill/03-CONTEXT.md` lines 18-32

```markdown
- **D-01:** Do not add a new portable example skill for v1.
- **D-03:** Treat "少即是多" as the guiding preference for Phase 3: keep the repository lean and avoid artifacts whose primary purpose is demonstration for humans.
- **D-07:** AI agents can follow the canonical `SKILL.md` contract directly; avoid adding extra instructional examples unless they serve a concrete agent workflow need.
```

**Apply to:** `docs/markdown-normalization-contract.md`, `README.md`, `docs/directory-spec.md`, `templates/skill/SKILL.md`

Keep Phase 4 small. Avoid examples-heavy prose, scaffold tooling, validators, or renderer implementation details.

### One Canonical Source Plus Local Details

**Source:** `docs/compatibility-matrix.md` lines 5-13

```markdown
1. 用一个 canonical `SKILL.md` 表达技能语义、触发条件、流程、输出、验证和安全边界。
2. 在同一个 `SKILL.md` 的 adapter notes 中记录各 runtime 的加载路径、frontmatter 限制、工具调用、用户问询、任务/子代理和权限差异。
3. v1 不维护独立 adapter 文件；如果 notes 变长，先压缩成必要检查点并保留在 canonical 文件里。
```

**Apply to:** all Phase 4 files

Mirror this pattern as: one shared Markdown IR contract first, skill/template-specific metadata and rendering details second.

### Directory Ownership

**Source:** `docs/directory-spec.md` lines 7-15 and 19-24

```markdown
| Path | Purpose |
|------|---------|
| `docs/` | 持久化项目说明、兼容性矩阵和目录契约 |
| `skills/` | canonical 技能源文件 |
| `templates/` | 可复制的占位符模板 |
```

```markdown
| `skills/<skill-name>/references/` | 可按需读取的长参考资料 |
| `skills/<skill-name>/scripts/` | 技能需要调用的辅助脚本 |
| `skills/<skill-name>/templates/` | 技能输出模板或文件模板 |
```

**Apply to:** `docs/markdown-normalization-contract.md`, `docs/directory-spec.md`, `templates/skill/SKILL.md`

Shared contracts belong in `docs/`; long skill-specific notes belong in `references/`; transform scripts belong in `scripts/`; reusable output templates belong in `templates/`.

### Ambiguity and Loss Handling

**Source:** `.planning/REQUIREMENTS.md` lines 10-13

```markdown
### Markdown Normalization

- [ ] **DWF-01**: A contributor can normalize arbitrary source content into a clean Markdown intermediate document that preserves document structure and intent.
- [ ] **DWF-02**: Ambiguous, unsupported, or lossy input fragments are explicitly flagged during Markdown normalization instead of being silently guessed or dropped.
```

**Source:** `.planning/ROADMAP.md` lines 33-36

```markdown
**Success Criteria:**
1. The repository documents Markdown as the required intermediate representation for document workflow skills.
2. The normalization contract covers common document primitives such as headings, paragraphs, lists, tables, code blocks, links, figures, callouts, and metadata.
3. Ambiguous, unsupported, or lossy source fragments have an explicit flagging convention instead of being silently dropped or guessed.
```

**Apply to:** `docs/markdown-normalization-contract.md`, `templates/skill/SKILL.md`

The contract must require visible preservation and review of ambiguous/lossy source fragments, but should leave the exact marker syntax to the owning skill/template.

### Runtime-Neutral Canonical Skill Body

**Source:** `templates/skill/SKILL.md` lines 40-54

```markdown
Keep shared workflow logic in this file. Put long background material in `references/`, helper scripts in `scripts/`, and output templates in `templates/` only when the skill needs them.

## Runtime Adapter Notes

Use this table for concise compatibility notes. Do not duplicate the skill process into runtime-specific files unless a runtime truly cannot consume this canonical `SKILL.md` directly.
```

**Apply to:** `templates/skill/SKILL.md`

Any template mention of Markdown normalization should be runtime-neutral and brief. Do not introduce Codex/Claude/Gemini/OpenCode/OpenClaw/Hermes-specific Markdown normalization syntax.

## No Analog Found

None.

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|

## Metadata

**Analog search scope:** `README.md`, `docs/`, `templates/`, `skills/`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/PROJECT.md`, `.planning/STATE.md`, prior phase context files.
**Project-local skills:** none found under `.codex/skills/` or `.agents/skills/`.
**Files scanned:** 15
**Pattern extraction date:** 2026-05-31
