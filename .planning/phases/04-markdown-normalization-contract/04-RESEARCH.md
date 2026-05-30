# Phase 4: markdown-normalization-contract - Research

**Researched:** 2026-05-31  
**Domain:** Markdown normalization contract for document workflow skills [CITED: .planning/REQUIREMENTS.md; .planning/ROADMAP.md]  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** The Markdown intermediate state is `YAML frontmatter + body`. Phase 4 should document that shape as the common normalization target. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]
- **D-02:** All source input for document workflow skills must first become this persistent Markdown intermediate state before target-format generation. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]
- **D-03:** The intermediate Markdown is meant to be durable and editable by both humans and AI agents, not merely a temporary prompt artifact. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]
- **D-04:** Skills should use their own scripts to transform the Markdown intermediate into target outputs such as Typst or HTML, so the same Markdown produces consistent rendered output. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]

### the agent's Discretion
- **D-05:** Phase 4 must not impose a universal frontmatter field list. Each template or skill may define the metadata fields it needs. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]
- **D-06:** Phase 4 must not over-constrain warning, ambiguity, or lossy-content markers beyond the shared Markdown intermediate-state requirement. Template-specific needs can define their own conventions. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]
- **D-07:** The purpose of this phase is stability through a common intermediate representation, not reducing every document workflow to one rigid schema. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]

### Deferred Ideas (OUT OF SCOPE)
- None. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DWF-01 | A contributor can normalize arbitrary source content into a clean Markdown intermediate document that preserves document structure and intent. | Treat CommonMark + GFM as the syntax baseline for structural primitives, then document a repo-level normalization contract that preserves intent instead of forcing a universal field schema. [CITED: https://spec.commonmark.org/0.31.2/; https://github.github.com/gfm/; .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md] |
| DWF-02 | Ambiguous, unsupported, or lossy input fragments are explicitly flagged during Markdown normalization instead of being silently guessed or dropped. | Plan for one minimal shared rule: every uncertain fragment must stay visible in the intermediate Markdown and carry an explicit review/ambiguity marker, while leaving the exact marker syntax local to the skill/template. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md; https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax] |
</phase_requirements>

## Summary

Phase 4 should be planned as a documentation contract, not a parser or rendering implementation. The repository already says the shared document-workflow IR is `YAML frontmatter + body`, that all source input must normalize into that IR before target generation, and that target artifacts are produced by skill-owned scripts rather than by a shared rendering layer. The user also explicitly rejected a universal frontmatter field list and a universal warning taxonomy, so the planner should keep the shared contract behavioral and minimal rather than schema-heavy. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md; .planning/ROADMAP.md; .planning/PROJECT.md]

For the primitive coverage in the success criteria, the safest plan is to ground the shared contract in CommonMark and GFM, then describe project-level handling for anything those specs do not make universal. CommonMark 0.31.2 covers headings, paragraphs, lists, fenced code blocks, links, images, and thematic breaks; GFM adds tables, task list items, strikethrough, and autolinks. GitHub Docs also documents alert-style callouts as a blockquote-based extension with NOTE/TIP/IMPORTANT/WARNING/CAUTION variants. That gives the planner enough standard structure to define normalization rules without inventing a repo-specific Markdown dialect. [CITED: https://spec.commonmark.org/0.31.2/; https://github.github.com/gfm/; https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax]

The planning risk is over-constraining metadata and flags. The contract should require explicit marking of ambiguous, unsupported, or lossy fragments, but it should not freeze a global field inventory or a single canonical marker taxonomy across all skills. The best MVP shape is a small docs-only contract in `docs/`, plus short pointers from `README.md`, `docs/directory-spec.md`, and `templates/skill/SKILL.md` so contributors can find the contract without copying implementation rules into the canonical template. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md; README.md; docs/directory-spec.md; templates/skill/SKILL.md]

**Primary recommendation:** Add one concise repo-level contract doc in `docs/` that states the required Markdown IR shape, enumerates the supported structural primitives, and defines a minimal "flag, do not guess" rule for ambiguous content; keep template-specific metadata and marker syntax out of the shared contract. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md; .planning/ROADMAP.md]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Define the shared Markdown normalization contract | Docs/Planning | Repository docs | This phase is a documentation contract phase; the authoritative artifact belongs in planning/docs, not in runtime code. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md; .planning/ROADMAP.md] |
| Preserve document structure and intent during normalization | Docs/Planning | Skill-local scripts (later phases) | The planner must define the preservation rule now, while the actual transform scripts remain skill-owned and phase-local. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md] |
| Flag ambiguous, unsupported, or lossy fragments | Docs/Planning | Skill-local conventions | The shared contract needs a stable behavior rule, but the exact marker syntax is intentionally left flexible. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md] |
| Cover common Markdown primitives | Docs/Planning | CommonMark/GFM reference specs | The shared contract should be grounded in standard Markdown primitives rather than a bespoke dialect. [CITED: https://spec.commonmark.org/0.31.2/; https://github.github.com/gfm/] |

## Standard Stack

### Core
| Standard | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| CommonMark spec | 0.31.2 [CITED: https://spec.commonmark.org/0.31.2/] | Baseline Markdown block and inline syntax for headings, paragraphs, lists, code blocks, links, images, and thematic breaks. | It is the broadest stable baseline for portable Markdown semantics. |
| GitHub Flavored Markdown spec | Current online spec [CITED: https://github.github.com/gfm/] | Common extensions for tables, task list items, strikethrough, and autolinks. | It matches the shared repo context better than a custom Markdown dialect. |
| GitHub Docs alerts syntax | Current docs page [CITED: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax] | Alert/callout conventions based on blockquote syntax. | It is the clearest official reference for callout-style Markdown handling. |

### Supporting
| Standard | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Repo-level docs contract | N/A | Defines the required normalization behavior and the scope boundary for templates/skills. | Use for the Phase 4 artifact and for cross-linking from README/template docs. |
| YAML frontmatter + body | Project decision [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md] | Persistent Markdown IR envelope. | Use as the shared intermediate state, but do not freeze field names globally. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| One shared docs contract | Per-skill bespoke normalization notes | More flexibility, but far more drift and weaker planner guarantees. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md] |
| Explicit shared flagging behavior | Universal field list and marker taxonomy | Easier to describe mechanically, but it violates the user's minimal-contract decision. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md] |
| Custom Markdown dialect | CommonMark + GFM baseline | A custom dialect would fragment interoperability and weaken intent preservation. [CITED: https://spec.commonmark.org/0.31.2/; https://github.github.com/gfm/] |

**Installation:**
```bash
# No package installation is required for Phase 4 research/planning.
```

## Package Legitimacy Audit

Not applicable. Phase 4 does not recommend external package installation.

## Architecture Patterns

### System Architecture Diagram

```text
Arbitrary source material
  -> normalization rules in docs
  -> persistent Markdown IR (YAML frontmatter + body)
  -> human/AI edits to the same Markdown
  -> skill-owned scripts
  -> target renderers (Typst / HTML in later phases)

Ambiguous / unsupported / lossy fragment
  -> explicit flag in the Markdown IR
  -> human review or later rewrite
```

### Recommended Project Structure
```text
docs/
├── markdown-normalization-contract.md   # Concise repo-level contract for DWF-01/DWF-02
├── compatibility-matrix.md              # Existing runtime compatibility guidance
└── directory-spec.md                    # Where the contract belongs and where it does not
templates/
└── skill/SKILL.md                       # Brief pointer only; no schema inflation
skills/<skill-name>/references/          # Skill-local long-form notes when a skill needs them
```

### Pattern 1: Behavior-First Contract
**What:** State the required transformation behavior in prose and short examples instead of defining a rigid universal schema. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]

**When to use:** When the repo needs a shared intermediate representation but must leave template-specific metadata and marker syntax flexible. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]

**Example:**
```md
> [!NOTE]
> Keep this fragment visible for manual review.
```
[CITED: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax]

### Pattern 2: Standard-Primitives-First Normalization
**What:** Normalize headings, paragraphs, lists, tables, code blocks, links, images, and callouts before handling project-specific conventions like figures or metadata notes. [CITED: https://spec.commonmark.org/0.31.2/; https://github.github.com/gfm/; https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax]

**When to use:** When the source material is arbitrary and the output must stay stable across multiple render targets. [CITED: .planning/ROADMAP.md; .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]

**Example:**
```md
# Section Title

Paragraph text.

- Item 1
- Item 2

| A | B |
|---|---|
| 1 | 2 |
```
[CITED: https://spec.commonmark.org/0.31.2/; https://github.github.com/gfm/]

### Anti-Patterns to Avoid
- **Universal metadata schema:** freezes template-specific fields and contradicts the locked decisions. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]
- **Silent drop or guess:** loses intent and makes later Typst/HTML output untrustworthy. [CITED: .planning/REQUIREMENTS.md]
- **Parser-specific marker rules in the shared contract:** leaks implementation details into the repo-wide contract and makes later skills harder to tailor. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Shared normalization semantics | A bespoke per-skill schema or marker taxonomy | One concise repo-level Markdown contract in `docs/` | The planner needs one stable shared rule set, not many local dialects. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md; README.md; docs/directory-spec.md] |
| Lossy or ambiguous fragment handling | Silent deletion or guesswork | Explicit flagging plus preserved source text | That is the direct requirement in DWF-02 and the phase context. [CITED: .planning/REQUIREMENTS.md; .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md] |
| Markdown primitive support | Ad hoc regex rules that pretend every construct is equal | CommonMark/GFM-aligned handling for the shared primitives | The specs provide the stable baseline for portable Markdown behavior. [CITED: https://spec.commonmark.org/0.31.2/; https://github.github.com/gfm/] |

**Key insight:** The hard problem is not parsing Markdown syntax; it is preserving intent without freezing away template freedom. The shared contract should therefore describe invariants and review behavior, not a universal field catalog. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]

## Common Pitfalls

### Pitfall 1: Treating the contract as a schema
**What goes wrong:** The planner turns the phase into a field list exercise and accidentally standardizes template-specific metadata. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]

**Why it happens:** YAML frontmatter is easy to over-interpret as a fixed data model instead of a lightweight envelope. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]

**How to avoid:** Write the contract in terms of required behavior and explicit preservation rules, then leave field names and optional metadata to each skill/template. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]

**Warning signs:** The plan starts naming mandatory keys, global marker names, or a canonical lossiness taxonomy. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]

### Pitfall 2: Hiding unsupported content
**What goes wrong:** Source fragments vanish during normalization, and later Typst/HTML output becomes untraceable. [CITED: .planning/REQUIREMENTS.md]

**Why it happens:** Silent fallback feels cleaner than explicit review markers. [CITED: .planning/REQUIREMENTS.md]

**How to avoid:** Require a visible marker or note that keeps the original fragment in the Markdown IR until a human or script resolves it. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md; .planning/REQUIREMENTS.md]

**Warning signs:** The plan uses words like "drop", "ignore", or "assume" for unsupported fragments. [CITED: .planning/REQUIREMENTS.md]

### Pitfall 3: Mixing shared rules with renderer rules
**What goes wrong:** Phase 4 starts inheriting Typst- or HTML-specific behaviors before Phase 5/6 define them. [CITED: .planning/ROADMAP.md]

**Why it happens:** It is tempting to solve output concerns while defining the intermediate state. [CITED: .planning/ROADMAP.md]

**How to avoid:** Keep Phase 4 limited to Markdown normalization, shared primitives, and flagging behavior; leave output-specific handling to later phases. [CITED: .planning/ROADMAP.md]

**Warning signs:** The plan mentions page layout, Typst hard constraints, or HTML semantics as part of the Phase 4 contract. [CITED: .planning/ROADMAP.md]

## Code Examples

Verified patterns from official sources:

### CommonMark primitives
```md
# Heading

Paragraph text.

- Item 1
- Item 2

![Alt text](image.png)
```
[CITED: https://spec.commonmark.org/0.31.2/]

### GFM table shape
```md
| A | B |
|---|---|
| 1 | 2 |
```
[CITED: https://github.github.com/gfm/]

### GitHub alert / callout
```md
> [!WARNING]
> Needs manual review.
```
[CITED: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Per-skill ad hoc Markdown handling | Shared repo-level Markdown contract grounded in CommonMark + GFM | 2026-05-31 planning scope [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md; https://spec.commonmark.org/0.31.2/; https://github.github.com/gfm/] | The planner can specify one stable IR while keeping skill-specific metadata free. |
| Silent guess/drop of unsupported fragments | Explicit flagging plus preserved source text | 2026-05-31 requirement framing [CITED: .planning/REQUIREMENTS.md; .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md] | Normalization stays auditable and reversible enough for later output phases. |
| Template-specific schema rules in the shared contract | Behavioral contract only | 2026-05-31 user decision [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md] | The shared contract stays minimal and does not freeze unrelated metadata. |

**Deprecated/outdated:**
- Silent dropping or guessing of unsupported fragments: conflicts with DWF-02 and the locked decisions. [CITED: .planning/REQUIREMENTS.md; .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]
- Universal frontmatter field lists: conflicts with the user's minimal-contract decision. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]
- Treating figures as already-standardized Markdown syntax: the reviewed specs cover images and alerts, but figures still need a project convention. [ASSUMED]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Figures should be handled as a project-level convention layered on top of image/caption patterns, not as a core Markdown primitive. [ASSUMED] | Summary / Code Examples / State of the Art | The planner may under-specify figure handling if Phase 4 assumes a native figure syntax that the chosen Markdown baseline does not provide. |

## Open Questions (RESOLVED)

1. **RESOLVED: Where should the contract live exactly?**
   - What we know: `docs/` already owns persistent project documentation, while `templates/skill/SKILL.md` is the canonical copyable artifact. [CITED: docs/directory-spec.md; templates/skill/SKILL.md]
   - Decision: create one concise dedicated docs page at `docs/markdown-normalization-contract.md` and add only short pointers from README and template docs. [CITED: README.md; docs/directory-spec.md]

2. **RESOLVED: How explicit should the shared flagging convention be?**
   - What we know: the contract must forbid silent dropping/guessing, but the user also rejected a universal marker taxonomy. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md; .planning/REQUIREMENTS.md]
   - Decision: keep the contract at the behavioral level and let each skill/template choose the concrete marker syntax. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]

## Environment Availability

Step 2.6: SKIPPED. This phase is documentation-only and identified no external runtime/package/tool dependencies in scope. [CITED: .planning/ROADMAP.md; .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]

## Validation Architecture

Skipped because `.planning/config.json` sets `workflow.nyquist_validation` to `false`. [CITED: .planning/config.json]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | N/A; this phase does not add auth surfaces. [CITED: .planning/ROADMAP.md] |
| V3 Session Management | no | N/A; this phase does not add session surfaces. [CITED: .planning/ROADMAP.md] |
| V4 Access Control | no | N/A; this phase is documentation-only. [CITED: .planning/ROADMAP.md] |
| V5 Input Validation | yes | Use explicit normalization rules and preserve ambiguous/unsupported fragments instead of guessing or dropping them. [CITED: .planning/REQUIREMENTS.md; .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md] |
| V6 Cryptography | no | N/A; this phase does not define cryptographic behavior. [CITED: .planning/ROADMAP.md] |

### Known Threat Patterns for documentation-only Markdown normalization

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Silent content loss during normalization | Tampering | Require explicit review markers and preserve the original fragment in the Markdown IR. [CITED: .planning/REQUIREMENTS.md; .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md] |
| Over-constrained shared metadata | Repudiation | Keep universal rules behavioral, not a universal schema, so later template-specific choices remain traceable. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md] |
| Renderer-specific assumptions leaking into the IR contract | Tampering | Keep Typst/HTML rules out of Phase 4 and reserve them for later phases. [CITED: .planning/ROADMAP.md] |

## Sources

### Primary (HIGH confidence)
- `.planning/phases/04-markdown-normalization-contract/04-CONTEXT.md` - Locked decisions for the shared Markdown IR and the minimal-contract boundary. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md]
- `.planning/REQUIREMENTS.md` - DWF-01 and DWF-02 plus the v1.1 requirement framing. [CITED: .planning/REQUIREMENTS.md]
- `.planning/ROADMAP.md` - Phase 4 goal and success criteria. [CITED: .planning/ROADMAP.md]
- `.planning/PROJECT.md` - v1.1 milestone context and document-workflow scope. [CITED: .planning/PROJECT.md]
- `.planning/STATE.md` - Current milestone state and planning posture. [CITED: .planning/STATE.md]
- `README.md` - Contributor-facing canonical-template-first story. [CITED: README.md]
- `docs/directory-spec.md` - Directory boundary rules for docs, templates, and skills. [CITED: docs/directory-spec.md]
- `templates/skill/SKILL.md` - Canonical template shape and runtime-notes placement. [CITED: templates/skill/SKILL.md]
- CommonMark 0.31.2 - headings, paragraphs, lists, fenced code blocks, links, images, thematic breaks. [CITED: https://spec.commonmark.org/0.31.2/]
- GitHub Flavored Markdown Spec - tables, task list items, strikethrough, autolinks. [CITED: https://github.github.com/gfm/]
- GitHub Docs basic writing and formatting syntax - alerts/callouts. [CITED: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax]

### Secondary (MEDIUM confidence)
- None.

### Tertiary (LOW confidence)
- The figure-handling convention should be project-level rather than a native Markdown primitive. [ASSUMED]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - local repo decisions plus official Markdown/GFM docs define the stable baseline. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md; https://spec.commonmark.org/0.31.2/; https://github.github.com/gfm/]
- Architecture: HIGH - the repo already constrains Phase 4 to a minimal documentation contract, not a rendering implementation. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md; .planning/ROADMAP.md]
- Pitfalls: HIGH - the main risks are explicitly called out by the user decisions and by the requirement to preserve unsupported content visibly. [CITED: .planning/phases/04-markdown-normalization-contract/04-CONTEXT.md; .planning/REQUIREMENTS.md]

**Research date:** 2026-05-31
**Valid until:** 2026-06-30 [ASSUMED]
