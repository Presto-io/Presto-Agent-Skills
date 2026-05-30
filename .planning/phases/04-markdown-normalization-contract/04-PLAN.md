---
phase: 04-markdown-normalization-contract
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - docs/markdown-normalization-contract.md
  - README.md
  - docs/directory-spec.md
  - templates/skill/SKILL.md
autonomous: true
requirements:
  - DWF-01
  - DWF-02
user_setup: []
must_haves:
  truths:
    - "文档工作流技能作者能在仓库文档中找到 Markdown normalization contract。"
    - "任意源材料必须先归一化为 YAML frontmatter + body 的持久 Markdown 中间态。"
    - "Markdown 中间态覆盖 headings, paragraphs, lists, tables, code blocks, links, figures, callouts, metadata。"
    - "ambiguous, unsupported, or lossy fragments 必须显式保留并标记，不能静默丢弃或猜测。"
    - "共享契约保持行为级别，不定义 universal frontmatter field list 或 universal marker taxonomy。"
  artifacts:
    - path: docs/markdown-normalization-contract.md
      provides: "共享 Markdown normalization contract"
      contains: "YAML frontmatter + body"
    - path: README.md
      provides: "贡献者入口中的契约发现路径"
      contains: "docs/markdown-normalization-contract.md"
    - path: docs/directory-spec.md
      provides: "docs/ 目录边界和 document workflow contract 归属"
      contains: "docs/markdown-normalization-contract.md"
    - path: templates/skill/SKILL.md
      provides: "文档工作流技能模板中的短指针"
      contains: "Markdown intermediate"
  key_links:
    - from: README.md
      to: docs/markdown-normalization-contract.md
      via: "repository tree or contributor workflow pointer"
      pattern: "docs/markdown-normalization-contract\\.md"
    - from: docs/directory-spec.md
      to: docs/markdown-normalization-contract.md
      via: "Document Workflow section"
      pattern: "Document Workflow"
    - from: templates/skill/SKILL.md
      to: docs/markdown-normalization-contract.md
      via: "Process section note"
      pattern: "docs/markdown-normalization-contract\\.md"
---

## Phase Goal

**As a** document workflow skill author, **I want to** a clear Markdown normalization contract, **so that** arbitrary source material can become one stable intermediate representation before any target-format rendering.

<objective>
Create the minimal shared Markdown normalization contract for document workflow skills.

Purpose: Phase 4 establishes Markdown as the durable, editable intermediate state before Typst, HTML, or later target generation, while preserving template and skill freedom.
Output: One concise docs page plus short contributor-facing pointers from the README, directory specification, and canonical skill template.
</objective>

<execution_context>
@/Users/mrered/.codex/get-shit-done/workflows/execute-plan.md
@/Users/mrered/.codex/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/STATE.md
@.planning/phases/04-markdown-normalization-contract/04-CONTEXT.md
@.planning/phases/04-markdown-normalization-contract/04-RESEARCH.md
@.planning/phases/04-markdown-normalization-contract/04-PATTERNS.md
@README.md
@docs/directory-spec.md
@docs/compatibility-matrix.md
@templates/skill/SKILL.md

<interfaces>
This phase is documentation-only. There are no code interfaces, package installs, external services, schemas, API endpoints, or runtime wrappers.
</interfaces>
</context>

<source_audit>
## Multi-Source Coverage Audit

| Source | Item | Coverage |
|--------|------|----------|
| GOAL | Clear Markdown normalization contract before target-format rendering | Covered by Task 1 main docs artifact and Tasks 2-3 discovery pointers |
| REQ | DWF-01 normalize arbitrary source content into clean Markdown intermediate preserving structure and intent | Covered by Task 1 required pattern, intermediate shape, and primitive table |
| REQ | DWF-02 ambiguous, unsupported, or lossy fragments explicitly flagged instead of silently guessed/dropped | Covered by Task 1 ambiguity/loss section and Task 3 negative-source verification |
| RESEARCH | Create concise `docs/markdown-normalization-contract.md` grounded in CommonMark/GFM-style primitives | Covered by Task 1 |
| RESEARCH | Keep contract behavioral, not a universal schema or parser implementation | Covered by Task 1 and negative verification in Task 3 |
| RESEARCH | Add short pointers from README, directory spec, and template only as needed | Covered by Tasks 2-3 |
| CONTEXT D-01 | Markdown intermediate state is `YAML frontmatter + body` | Covered by Task 1 |
| CONTEXT D-02 | All source input must become the persistent Markdown intermediate before target generation | Covered by Task 1 |
| CONTEXT D-03 | Intermediate Markdown is durable and editable by humans and agents | Covered by Task 1 |
| CONTEXT D-04 | Skill-owned scripts transform Markdown into target outputs with stable results | Covered by Task 1 |
| CONTEXT D-05 | No universal frontmatter field list | Covered by Task 1 and Task 3 negative verification |
| CONTEXT D-06 | No universal warning/ambiguity/lossy marker taxonomy | Covered by Task 1 and Task 3 negative verification |
| CONTEXT D-07 | Stability through common IR, not one rigid schema | Covered by Task 1 contract scope and Task 2 directory boundary |
| CONTEXT Deferred Ideas | None | No deferred ideas planned |
</source_audit>

<tasks>

<task type="auto">
  <name>Task 1: Create the Markdown normalization contract</name>
  <files>docs/markdown-normalization-contract.md</files>
  <read_first>
    - docs/markdown-normalization-contract.md (create if missing)
    - .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md
    - .planning/phases/04-markdown-normalization-contract/04-RESEARCH.md
    - .planning/phases/04-markdown-normalization-contract/04-PATTERNS.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
    - docs/compatibility-matrix.md
  </read_first>
  <action>Create `docs/markdown-normalization-contract.md` as the authoritative Phase 4 shared contract. Use the concise documentation style from `docs/compatibility-matrix.md`. The document must include exact sections named `# Markdown Normalization Contract`, `## Required Pattern`, `## Intermediate Shape`, `## Normalized Primitives`, `## Ambiguous Or Lossy Content`, and `## Out Of Scope`. In `## Required Pattern`, state D-01 through D-04 concretely: the common target is `YAML frontmatter + body`; every document workflow source normalizes into this persistent Markdown before any target generation; humans and agents may edit the intermediate; skill-owned scripts generate Typst, HTML, or later outputs from the same Markdown. In `## Intermediate Shape`, state per D-05 that the shared contract does not define a universal frontmatter field list. In `## Normalized Primitives`, include a compact table with rows for headings, paragraphs, lists, tables, code blocks, links, figures, callouts, and metadata. In `## Ambiguous Or Lossy Content`, require visible preservation and explicit review marking for ambiguous, unsupported, or lossy fragments, while stating per D-06 that each skill or template chooses its own marker syntax. In `## Out Of Scope`, exclude Typst rules, HTML rules, rendering styles, OCR/extraction, lint tooling, universal metadata fields, and a universal marker taxonomy.</action>
  <verify>
    <automated>test -f docs/markdown-normalization-contract.md</automated>
    <automated>rg -n '^# Markdown Normalization Contract|^## Required Pattern|^## Intermediate Shape|^## Normalized Primitives|^## Ambiguous Or Lossy Content|^## Out Of Scope' docs/markdown-normalization-contract.md</automated>
    <automated>rg -n 'YAML frontmatter \\+ body|persistent Markdown|skill-owned scripts|Typst|HTML' docs/markdown-normalization-contract.md</automated>
    <automated>rg -n 'headings|paragraphs|lists|tables|code blocks|links|figures|callouts|metadata' docs/markdown-normalization-contract.md</automated>
  </verify>
  <acceptance_criteria>
    - Source assertion: `docs/markdown-normalization-contract.md` has exactly one H1: `# Markdown Normalization Contract`.
    - Source assertion: the file contains the exact string `YAML frontmatter + body`.
    - Source assertion: the file states that source material is normalized to the Markdown intermediate before target generation.
    - Source assertion: the primitive table includes headings, paragraphs, lists, tables, code blocks, links, figures, callouts, and metadata.
    - Source assertion: the file says ambiguous, unsupported, or lossy fragments must remain visible and explicitly marked for review.
    - Source assertion: the file says the shared contract does not define a universal frontmatter field list or a universal marker taxonomy.
  </acceptance_criteria>
  <done>The new contract document satisfies D-01 through D-07 and covers DWF-01/DWF-02 without adding tooling, schemas, or output renderer rules.</done>
</task>

<task type="auto">
  <name>Task 2: Add contributor discovery pointers</name>
  <files>README.md, docs/directory-spec.md</files>
  <read_first>
    - README.md
    - docs/directory-spec.md
    - docs/markdown-normalization-contract.md
    - .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md
    - .planning/phases/04-markdown-normalization-contract/04-PATTERNS.md
  </read_first>
  <action>Update only short discovery pointers. In `README.md`, add `docs/markdown-normalization-contract.md` under the `docs/` tree, and add one concise contributor workflow sentence or numbered item saying document workflow skills must normalize source material into the Markdown intermediate before generating Typst, HTML, or other target outputs. Do not paste the contract details into README. In `docs/directory-spec.md`, update the `docs/` row to mention the Markdown normalization contract, then add a short `## Document Workflow` section with a one-row table for `docs/markdown-normalization-contract.md`. The section must state that template-specific metadata fields, warning marker syntax, scripts, and renderer rules remain in the owning skill/template or later target-specific docs, not in a universal shared schema.</action>
  <verify>
    <automated>rg -n 'markdown-normalization-contract\\.md|Markdown normalization|Markdown intermediate' README.md docs/directory-spec.md</automated>
    <automated>rg -n '^## Document Workflow|docs/markdown-normalization-contract\\.md' docs/directory-spec.md</automated>
    <automated>! rg -n 'universal frontmatter field list|universal marker taxonomy|required metadata fields' README.md docs/directory-spec.md</automated>
  </verify>
  <acceptance_criteria>
    - Source assertion: `README.md` repository tree lists `docs/markdown-normalization-contract.md`.
    - Source assertion: `README.md` has one short document-workflow pointer and does not include the full contract sections.
    - Source assertion: `docs/directory-spec.md` has a `## Document Workflow` section.
    - Source assertion: `docs/directory-spec.md` links `docs/markdown-normalization-contract.md` to its purpose.
    - Source assertion: `docs/directory-spec.md` keeps template-specific metadata fields, marker syntax, scripts, and renderer rules out of the shared contract.
  </acceptance_criteria>
  <done>Contributors can discover the Phase 4 contract from the README and directory spec without README or directory-spec becoming the contract itself.</done>
</task>

<task type="auto">
  <name>Task 3: Add the minimal template pointer and verify scope boundaries</name>
  <files>templates/skill/SKILL.md</files>
  <read_first>
    - templates/skill/SKILL.md
    - docs/markdown-normalization-contract.md
    - README.md
    - docs/directory-spec.md
    - .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md
    - .planning/REQUIREMENTS.md
  </read_first>
  <action>In `templates/skill/SKILL.md`, add only one concise note in the `## Process` section after the existing supporting-file guidance. The note must tell authors that document workflow skills should normalize source material into the Markdown intermediate described in `docs/markdown-normalization-contract.md` before generating Typst, HTML, or other target outputs. Do not add required frontmatter keys, document-specific metadata fields, warning marker syntax, Typst constraints, HTML semantic rules, runtime adapter changes, examples, scripts, or validation tooling.</action>
  <verify>
    <automated>rg -n 'docs/markdown-normalization-contract\\.md|Markdown intermediate|Typst, HTML, or other target outputs' templates/skill/SKILL.md</automated>
    <automated>rg -n 'docs/markdown-normalization-contract\\.md' README.md docs/directory-spec.md templates/skill/SKILL.md</automated>
    <automated>rg -n 'YAML frontmatter \\+ body|ambiguous|unsupported|lossy|figures|callouts|metadata' docs/markdown-normalization-contract.md</automated>
    <automated>! rg -n 'required fields|mandatory fields|universal frontmatter field|universal marker taxonomy|canonical marker taxonomy|Typst hard constraints|HTML semantic rules|page layout' docs/markdown-normalization-contract.md templates/skill/SKILL.md README.md docs/directory-spec.md</automated>
  </verify>
  <acceptance_criteria>
    - Source assertion: `templates/skill/SKILL.md` references `docs/markdown-normalization-contract.md` exactly once or in one concise local note.
    - Source assertion: `templates/skill/SKILL.md` does not add document workflow frontmatter keys or marker syntax.
    - CLI assertion: `rg -n 'docs/markdown-normalization-contract\\.md' README.md docs/directory-spec.md templates/skill/SKILL.md` returns matches in all three files.
    - CLI assertion: the negative `rg` command in `<verify>` exits successfully, proving the phase did not add forbidden universal schema, marker taxonomy, or target-renderer rules.
  </acceptance_criteria>
  <done>The canonical template points document workflow authors to the shared Markdown contract while preserving the runtime-neutral, placeholder-based template shape.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| arbitrary source material -> Markdown intermediate | Untrusted or messy source content crosses into a normalized, reviewable document state. |
| shared contract -> skill-owned scripts | Repository-level behavior rules influence later scripts without controlling implementation-specific metadata or rendering details. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-04-01 | Tampering | `docs/markdown-normalization-contract.md` ambiguity handling | mitigate | Require ambiguous, unsupported, or lossy fragments to remain visible and explicitly marked for review instead of being silently dropped or guessed. |
| T-04-02 | Repudiation | `docs/markdown-normalization-contract.md` metadata scope | mitigate | State that the shared contract is behavioral and does not define a universal frontmatter field list, preserving template-specific traceability. |
| T-04-03 | Tampering | Phase 4 target-rendering scope | mitigate | Keep Typst constraints, HTML semantic rules, rendering styles, and page layout rules out of Phase 4 and reserve them for later phases. |
| T-04-SC | Tampering | package installs | accept | No npm, pip, cargo, external service, or runtime install is planned for this documentation-only phase. |
</threat_model>

<dependency_graph>
Task 1 creates `docs/markdown-normalization-contract.md`.
Task 2 depends on Task 1 because README and directory spec point to the new artifact.
Task 3 depends on Tasks 1-2 because it verifies all discovery pointers and source-boundary assertions.
All tasks are in one Wave 1 plan because they share documentation intent and must be executed sequentially within the same small file set.
</dependency_graph>

<verification>
Run these local checks after all tasks complete:

<automated>test -f docs/markdown-normalization-contract.md</automated>
<automated>rg -n 'YAML frontmatter \\+ body|persistent Markdown|skill-owned scripts|ambiguous|unsupported|lossy' docs/markdown-normalization-contract.md</automated>
<automated>rg -n 'headings|paragraphs|lists|tables|code blocks|links|figures|callouts|metadata' docs/markdown-normalization-contract.md</automated>
<automated>rg -n 'docs/markdown-normalization-contract\\.md' README.md docs/directory-spec.md templates/skill/SKILL.md</automated>
<automated>! rg -n 'required fields|mandatory fields|universal frontmatter field|universal marker taxonomy|canonical marker taxonomy|Typst hard constraints|HTML semantic rules|page layout' docs/markdown-normalization-contract.md README.md docs/directory-spec.md templates/skill/SKILL.md</automated>
</verification>

<success_criteria>
1. The repository documents Markdown as the required intermediate representation for document workflow skills.
2. The normalization contract covers headings, paragraphs, lists, tables, code blocks, links, figures, callouts, and metadata.
3. Ambiguous, unsupported, or lossy source fragments have an explicit flagging requirement instead of being silently dropped or guessed.
4. The shared contract remains minimal and behavioral, with no universal frontmatter field list and no universal marker taxonomy.
5. README, directory spec, and skill template point to the contract without duplicating it.
</success_criteria>

<output>
Create `.planning/phases/04-markdown-normalization-contract/04-01-SUMMARY.md` when done.
</output>
