---
phase: 04-markdown-normalization-contract
plan: 01
subsystem: documentation
tags: [documents, markdown, normalization, contracts]

requires: []
provides:
  - Shared Markdown normalization contract for document workflow skills
  - YAML frontmatter + body intermediate-state rule
  - Explicit review marking rule for ambiguous, unsupported, or lossy fragments
  - Contributor discovery pointers from README, directory spec, and skill template
affects: [v1.1, documents, markdown, templates]

tech-stack:
  added: []
  patterns:
    - markdown-first document workflow
    - behavior-level normalization contract
    - explicit preservation of lossy or ambiguous source fragments

key-files:
  created:
    - docs/markdown-normalization-contract.md
    - .planning/phases/04-markdown-normalization-contract/04-01-SUMMARY.md
  modified:
    - README.md
    - docs/directory-spec.md
    - templates/skill/SKILL.md

key-decisions:
  - "Document workflow skills normalize arbitrary source material into a persistent Markdown intermediate before target generation."
  - "The shared intermediate shape is YAML frontmatter + body, but the contract does not define a universal frontmatter field list."
  - "Ambiguous, unsupported, or lossy fragments must stay visible and be explicitly marked for review, while each skill or template chooses its own marker syntax."
  - "Typst rules, HTML rules, rendering styles, extraction, lint tooling, universal metadata fields, and a universal marker taxonomy remain out of scope for Phase 4."

patterns-established:
  - "Document workflow contracts live in docs/ and are linked from contributor entry points."
  - "Shared document workflow guidance stays behavioral; template-specific metadata, marker syntax, scripts, and renderer rules stay with the owning skill/template or later target-specific docs."

requirements-completed: [DWF-01, DWF-02]

duration: 21min
completed: 2026-05-31
---

# Phase 04 Plan 01: Markdown Normalization Contract Summary

**Markdown-first document workflow contract with visible review handling for ambiguous or lossy source material**

## Performance

- **Duration:** 21 min
- **Started:** 2026-05-30T18:20:00Z
- **Completed:** 2026-05-30T18:41:04Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- Added `docs/markdown-normalization-contract.md` as the shared Phase 4 contract.
- Documented `YAML frontmatter + body` as the common persistent Markdown intermediate before Typst, HTML, or later target generation.
- Covered headings, paragraphs, lists, tables, code blocks, links, figures, callouts, and metadata.
- Required ambiguous, unsupported, or lossy fragments to remain visible and explicitly marked for review.
- Added short discovery pointers in README, directory spec, and the canonical skill template without adding a universal field list, marker taxonomy, scripts, or renderer rules.

## Task Commits

Not committed during this execution because the working tree already contained pre-existing uncommitted v1.1 planning changes. The implementation changes were kept in the working tree and verified locally.

## Files Created/Modified

- `docs/markdown-normalization-contract.md` - Authoritative Markdown normalization contract for document workflow skills.
- `README.md` - Adds the contract to the repository tree and contributor workflow.
- `docs/directory-spec.md` - Defines where the document workflow contract belongs and where template-specific details remain.
- `templates/skill/SKILL.md` - Adds one concise document workflow pointer in the Process section.
- `.planning/phases/04-markdown-normalization-contract/04-01-SUMMARY.md` - Captures Phase 4 execution evidence.

## Decisions Made

- Kept the contract as a behavior-level docs artifact, not a schema, parser, or renderer specification.
- Preserved template freedom for metadata fields and marker syntax.
- Left Typst and HTML output-specific rules to later phases.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- README initially listed the new file in the tree without the full `docs/markdown-normalization-contract.md` path. Verification caught this, and the contributor workflow pointer was updated to include the full path.
- Commits were intentionally deferred because unrelated or pre-existing planning changes were already present in the working tree.

## Verification

Commands run locally:

- `test -f docs/markdown-normalization-contract.md`
  - PASS: contract file exists.
- `rg -n '^# Markdown Normalization Contract|^## Required Pattern|^## Intermediate Shape|^## Normalized Primitives|^## Ambiguous Or Lossy Content|^## Out Of Scope' docs/markdown-normalization-contract.md`
  - PASS: required sections are present with one H1.
- `rg -n 'YAML frontmatter \+ body|persistent Markdown|skill-owned scripts|ambiguous|unsupported|lossy' docs/markdown-normalization-contract.md`
  - PASS: required intermediate-state and ambiguity rules are present.
- `rg -n 'headings|paragraphs|lists|tables|code blocks|links|figures|callouts|metadata' docs/markdown-normalization-contract.md`
  - PASS: all required primitives are covered.
- `rg -n 'docs/markdown-normalization-contract\.md' README.md docs/directory-spec.md templates/skill/SKILL.md`
  - PASS: all contributor discovery pointers reference the contract.
- `rg -n 'does not define a universal frontmatter field list|does not define .*universal marker taxonomy|each skill or template chooses its own marker syntax' docs/markdown-normalization-contract.md`
  - PASS: scope boundaries are explicit.
- `! rg -n 'must use these fields|required metadata fields|mandatory metadata fields|canonical marker values|must use marker values|Typst hard constraints|HTML semantic rules|page layout' docs/markdown-normalization-contract.md templates/skill/SKILL.md README.md docs/directory-spec.md`
  - PASS: no universal field list, marker taxonomy, or target-renderer rule leakage was introduced.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 5 can now define Typst output constraints against a stable Markdown intermediate. No Phase 4 blocker remains.

## Self-Check: PASSED

- DWF-01 and DWF-02 are covered.
- The new contract is discoverable from README, directory spec, and the canonical skill template.
- The shared contract stays minimal and does not add tooling, schemas, runtime wrappers, or target renderer rules.

---
*Phase: 04-markdown-normalization-contract*
*Completed: 2026-05-31*
