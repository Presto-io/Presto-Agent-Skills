# Phase 24: Optional End-of-Term Module and Package Outputs - Context

**Gathered:** 2026-06-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 24 defines how the existing optional `end-of-term-teaching-materials` workflow is attached to the `teaching-design-package` orchestration skill and how package outputs are represented. It covers TDP-10 through TDP-14: optional end-of-term module integration, inherited review gates, deterministic table/workbook/manifest discoverability, split `end-of-term-package.pdf`, default combined `teaching-design-package.pdf`, and explicit failure/status behavior when PDF compilation or merge output is unavailable.

This phase should extend the existing `skills/teaching-design-package` contract created in Phase 23. It should not plan a new standalone end-of-term skill, should not delete or replace `skills/end-of-term-teaching-materials`, and should not bypass the existing `end-of-term-full.md` Markdown review checkpoint or `## 复核标记` export gate. Phase 25 remains responsible for broader regression and documentation-index verification across all public command surfaces.

**Auto-mode note:** The user authorized `/gsd:discuss-phase 24 --auto` and explicitly requested no large-direction questions. All gray areas below were auto-selected and resolved conservatively from roadmap, requirement, Phase 22/23 evidence, and existing skill contracts.

**Tooling note:** `gsd-sdk query init.phase-op 24` returned `phase_found: false` in this session even though `.planning/ROADMAP.md` and `.planning/STATE.md` both identify Phase 24 as planned/ready. This context treats ROADMAP/STATE as authoritative and records the SDK mismatch for downstream awareness.

</domain>

<decisions>
## Implementation Decisions

### Optional End-of-Term Module Attachment

- **D-01:** Model end-of-term materials as an optional module inside `teaching-design-package`, not as a required package stage. The package frontmatter should keep an `end_of_term.enabled`-style switch and make the module status explicit in the package manifest.
- **D-02:** Reuse the existing `skills/end-of-term-teaching-materials` contract as the source of truth. Phase 24 should reference or call its public commands (`markdown`, `validate`, `render`, `verify`, `manifest`) rather than copying its scoring, table, workbook, or review logic into the package skill.
- **D-03:** The package handoff file for this module should remain `end-of-term-full.md`. The package may scaffold or point to it, but final rendering must flow through the end-of-term skill's own Markdown checkpoint.
- **D-04:** If the optional module is disabled, the package manifest should say so explicitly and should not report missing end-of-term artifacts as failures. If enabled, missing `end-of-term-full.md`, missing source data, failed validation, or unresolved review markers should block final package readiness.

### Review Gate Preservation

- **D-05:** Phase 24 must preserve the end-of-term hard export rule: `## 复核标记` in `end-of-term-full.md` must be exactly `无` before normal final export. The package-level `## 复核标记` can summarize the blockage, but cannot override or clear the module-local gate.
- **D-06:** Uncertain score values such as `87?`, missing fields, and AI-drafted analysis content should keep the existing one-item-at-a-time teacher-review pattern. The package orchestration must not silently correct, drop, or auto-approve these markers.
- **D-07:** `render --abnormal-review` stays non-final inspection behavior. If surfaced through the package helper, its manifest must preserve `artifact_kind: abnormal_review`, `final_ready: false`, and `review_cleared: false`; it must not contribute to a ready combined package.
- **D-08:** Final readiness should require both package-level review markers and enabled module-level review markers to be clear. A clean teaching-plan/lesson-plan split is not enough if the enabled end-of-term module is unresolved.

### Manifest, Table, and Workbook Discoverability

- **D-09:** The `teaching-design-package` manifest should include an end-of-term module block when enabled, with paths/statuses for `end-of-term-full.md`, `end-of-term-package.typ`, `end-of-term-package.pdf`, module `manifest.json`, deterministic table directory, calculated score evidence, and workbook artifacts.
- **D-10:** Do not flatten all end-of-term table/workbook evidence into top-level package fields. Keep module-local ownership and add discoverable pointers so downstream agents and teachers can locate `tables/score-data.json`, `tables/calculated-score-data.json`, `tables/score-summary.json`, `tables/highlight-evidence.json`, `tables/score-list.md`, `tables/score-list.xlsx`, and `tables/scorebook.xlsx`.
- **D-11:** Package-level `final_ready` should be derived from selected outputs and enabled module statuses, including the end-of-term module manifest's `review_cleared`, `calculated_scores_verified`, `table_artifacts_verified`, `workbook_verified`, and PDF status when that module is selected for final output.
- **D-12:** Manifest/status fields should remain stable and auditable. Prefer explicit status values such as `disabled`, `planned`, `not_run`, `passed`, `failed`, `missing_compiler`, `merge_unavailable`, and `blocked_review` over vague booleans.

### Split Outputs and Combined Package Behavior

- **D-13:** When the optional module is enabled and review passes, Phase 24 should plan `end-of-term-package.pdf` as a split output alongside Phase 23's `teaching-plan.pdf` and `lesson-plans.pdf`.
- **D-14:** The default final artifact should be `teaching-design-package.pdf` when all selected module PDFs exist and local tooling can merge or compile a combined PDF. This output is a package-level artifact, separate from module-local PDFs.
- **D-15:** Do not claim combined PDF success from Typst generation alone. The combined artifact status is `passed` only when the actual `teaching-design-package.pdf` file exists after an explicit merge/compile step.
- **D-16:** If only split artifacts can be produced, the manifest should preserve successful split outputs and mark the combined output as unavailable or failed with evidence. It should not claim the full package is complete unless the requirement-selected default combined artifact succeeded or the user explicitly accepts split-only delivery in a later phase.

### Failure Semantics and Phase 25 Boundary

- **D-17:** Missing Typst/PDF tooling, unavailable merge tooling, failed module validation, unresolved review markers, and absent expected PDFs must produce explicit manifest/status evidence instead of silent success.
- **D-18:** Phase 24 should add enough fixture or manifest evidence for optional-module and combined-output behavior to guide execution, but broad public command surface regression for `jiaoan-jihua`, `jiaoan-shicao`, and `end-of-term-teaching-materials` belongs to Phase 25 unless needed as a narrow safety check.
- **D-19:** Keep OpenClaw and Hermes Agent in mind when planning output behavior: do not rely on hidden automatic script discovery, implicit writable directories, or agent-private syntax. Use file paths, shell commands, and manifest evidence that are portable across the supported runtimes.
- **D-20:** Preserve the Phase 23 helper's honest status behavior. Extending `teaching-design-package.sh` is acceptable if it keeps existing commands stable and adds optional-module/combined-output commands or flags without breaking `example`, `plan-split`, `render-split`, `manifest`, `info`, or `version`.

### Assumptions and Open Points for Planning

- **D-21:** Assume `end-of-term-teaching-materials` remains the canonical renderer for its module. The package skill should orchestrate or point to its artifacts, not reimplement score calculation or workbook generation.
- **D-22:** Assume the combined PDF path can start with conservative status semantics even if actual merging requires local tool availability checks during execution.
- **D-23:** Planner should decide exact command/flag names for optional module rendering and combined output, but must keep them discoverable from `SKILL.md`, `references/format-and-orchestration.md`, and script help text.
- **D-24:** Planner should decide whether to update the package Markdown template with an explicit `## 期末材料` section or keep the module represented through frontmatter plus `## 输出清单`. If added, it should be a concise handoff section pointing to `end-of-term-full.md`, not a full duplicate of the end-of-term template.
- **D-25:** Planner should include verification for the SDK phase lookup mismatch if relevant, but should not let it block Phase 24 planning because ROADMAP/STATE are clear.

### Claude's Discretion

- Prefer minimal, explicit integration over broad refactors. Add module pointers, manifest/status fields, and helper behavior where they reduce ambiguity for downstream agents.
- Preserve module-local artifacts and names. The safest default names are `end-of-term-full.md`, `end-of-term-package.typ`, `end-of-term-package.pdf`, `manifest.json`, `tables/`, and package-level `teaching-design-package.pdf`.
- If a merge path is uncertain, implement honest failure evidence first; a truthful incomplete package is better than a false success.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Requirements

- `.planning/ROADMAP.md` — Defines Phase 24 as optional end-of-term module and package outputs for TDP-10 through TDP-14.
- `.planning/REQUIREMENTS.md` — Locks TDP-10 through TDP-14 and separates Phase 25 regression/documentation requirements.
- `.planning/PROJECT.md` — Captures the v1.11 goal: compose existing teaching skills through a Markdown-first integrated package, optional end-of-term module, split outputs, and default combined package output.
- `.planning/STATE.md` — Records current Phase 24 status, accumulated v1.11 decisions, and supported runtime targets.

### Prior Phase Evidence

- `.planning/phases/22-scheduling-contract-and-fixture/22-CONTEXT.md` — Carries forward scheduling evidence and review-marker discipline.
- `.planning/phases/22-scheduling-contract-and-fixture/22-SUMMARY.md` — Lists delivered scheduling contract and deterministic fixture evidence.
- `.planning/phases/22-scheduling-contract-and-fixture/22-VERIFICATION.md` — Passed traceability for TDP-01 through TDP-04.
- `.planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-CONTEXT.md` — Defines Phase 23 decisions for the package skill, Markdown checkpoint, split jiaoan outputs, and Phase 24 deferrals.
- `.planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-SUMMARY.md` — Lists existing `teaching-design-package` files and helper behavior that Phase 24 should extend.
- `.planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-VERIFICATION.md` — Passed traceability for TDP-05 through TDP-09.

### Teaching Design Package Skill

- `skills/teaching-design-package/SKILL.md` — Current package entry, process, script usage, runtime adapter notes, outputs, verification, and Phase 24 deferrals.
- `skills/teaching-design-package/references/format-and-orchestration.md` — Current package contract, module handoff, split output status, manifest keys, and deferred Phase 24 scope.
- `skills/teaching-design-package/templates/teaching-design-package-full.md` — Package Markdown checkpoint and existing end-of-term placeholder/frontmatter.
- `skills/teaching-design-package/scripts/teaching-design-package.sh` — Existing helper commands and manifest writer to extend without breaking Phase 23 behavior.
- `test/1.11/teaching-design-package/expected-manifest.json` — Phase 23 expected manifest with deferred Phase 24 fields.
- `test/1.11/teaching-design-package/expected-review.md` — Fixture statement that combined package and end-of-term PDFs were not claimed in Phase 23.

### End-of-Term Module Source of Truth

- `skills/end-of-term-teaching-materials/SKILL.md` — Existing optional module entry, workflow, public commands, outputs, verification, runtime adapter notes, and safety boundaries.
- `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md` — Review/export gates, deterministic table artifacts, calculated score evidence, workbook outputs, manifest requirements, and verification details.
- `skills/end-of-term-teaching-materials/references/data-contract.md` — Structured JSON contract for course, class, roster, scores, package flags, and review markers.
- `skills/end-of-term-teaching-materials/references/rendering-style.md` — Rendering and evidence rules for tables, calculated scores, workbook values, and highlight evidence.
- `skills/end-of-term-teaching-materials/references/cover-template-notes.md` — Fixed cover-template notes relevant to module output stability.
- `skills/end-of-term-teaching-materials/references/scorebook-template-notes.md` — Workbook/scorebook template notes relevant to discoverability.
- `skills/end-of-term-teaching-materials/templates/end-of-term-full.md` — Module Markdown checkpoint that must not be bypassed.
- `skills/end-of-term-teaching-materials/templates/typst/end-of-term-package.typ` — Module Typst package template.
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh` — Public command surface for example, validate, markdown, render, verify, manifest, info, and version.
- `skills/end-of-term-teaching-materials/scripts/render_package.py` — Script entry used by verification and rendering.
- `skills/end-of-term-teaching-materials/scripts/end_of_term/` — Skill-local modules that own scoring, table artifacts, workbook generation, PDF manifest, and verification behavior.

### Repository Conventions

- `AGENTS.md` — Simplified Chinese response rule, editing rules, skill authoring rules, and GSD workflow pointers.
- `README.md` — Repository discoverability for `end-of-term-teaching-materials` and `teaching-design-package`.
- `skills/README.md` — Skill index and artifact contract table.
- `docs/compatibility-matrix.md` — Runtime compatibility matrix with `teaching-design-package` coverage.
- `docs/directory-spec.md` — Directory placement rules for `references/`, `scripts/`, `templates/`, and versioned fixture evidence.
- `docs/markdown-normalization-contract.md` — Markdown-first workflow contract that applies to both package and module checkpoints.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `skills/teaching-design-package/scripts/teaching-design-package.sh`: Existing `example`, `plan-split`, `render-split`, `manifest`, `info`, and `version` commands; manifest currently records split jiaoan Typst/PDF fields, `review_markers`, `final_ready`, and `phase_24_deferred`.
- `skills/teaching-design-package/templates/teaching-design-package-full.md`: Existing frontmatter already contains `modules.end_of_term.enabled: false` and a Phase 24 placeholder, making optional-module extension a natural continuation.
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`: Existing public helper that owns module validation, Markdown generation, rendering, verification, and manifest output.
- `skills/end-of-term-teaching-materials/scripts/end_of_term/_engine.py`: Existing module internals already write `end-of-term-full.md`, `end-of-term-package.typ`, `end-of-term-package.pdf`, `manifest.json`, deterministic table artifacts, score-list workbook, scorebook workbook, highlight evidence, and verification cases.
- `skills/end-of-term-teaching-materials/references/fixtures/`: Existing normal and uncertain source fixtures can inform optional-module test coverage without inventing real student data.

### Established Patterns

- Markdown-first checkpoints are mandatory before rendering: `teaching-design-package-full.md` at package level and `end-of-term-full.md` at module level.
- Public command surfaces are stable contracts. New behavior should extend rather than rename existing commands, flags, output paths, or manifest keys.
- Review gates block final readiness. Existing `end-of-term-teaching-materials` requires `## 复核标记` to be exactly `无` for normal final export.
- Manifest/status truthfulness is already established in Phase 23: PDF status cannot be `passed` unless explicit PDF generation ran and output exists.
- Long output rules belong in `references/`; `SKILL.md` should remain concise and portable.

### Integration Points

- `skills/teaching-design-package/references/format-and-orchestration.md` should gain Phase 24 rules for optional end-of-term module handoff, module manifest pointers, split `end-of-term-package.pdf`, and combined `teaching-design-package.pdf`.
- `skills/teaching-design-package/templates/teaching-design-package-full.md` may gain explicit optional end-of-term output rows or a concise `## 期末材料` handoff section.
- `skills/teaching-design-package/scripts/teaching-design-package.sh` may extend manifest generation and output orchestration while preserving Phase 23 commands.
- `test/1.11/teaching-design-package/` can hold deterministic optional-module/combined-output fixture expectations if execution needs evidence.
- README/skills index/compatibility docs may need small discoverability updates if Phase 24 changes artifact contracts; broad documentation-index verification remains Phase 25.

</code_context>

<specifics>
## Specific Ideas

- The package manifest can expose an `end_of_term` object with `enabled`, `markdown`, `manifest`, `typ`, `pdf`, `tables`, `workbooks`, `review_cleared`, `final_ready`, and `status` fields while leaving detailed score evidence in the module manifest.
- Split outputs should be easy to inspect: `teaching-plan.pdf`, `lesson-plans.pdf`, and `end-of-term-package.pdf`.
- The combined default output should be named exactly `teaching-design-package.pdf` to match TDP-13 and Phase 23 deferred wording.
- If merge tooling is unavailable, a status like `merge_unavailable` plus the successful split artifact list is preferred over a vague failure.
- If review markers block the optional module, a status like `blocked_review` should point to both package-level `## 复核标记` and module-local `end-of-term-full.md`.

</specifics>

<deferred>
## Deferred Ideas

- Full regression verification that existing `jiaoan-jihua`, `jiaoan-shicao`, and `end-of-term-teaching-materials` public command surfaces remain usable is Phase 25, except for narrow checks needed by Phase 24 implementation.
- Documentation/index verification for the new package skill and all affected docs is Phase 25 unless Phase 24 changes artifact contracts enough to require immediate local updates.
- Deleting, renaming, or physically merging original skill directories remains out of scope.
- Hosted collaboration, cloud teacher review, arbitrary template discovery, OCR, and uncontrolled spreadsheet ingestion remain out of scope.

</deferred>

---

*Phase: 24-Optional End-of-Term Module and Package Outputs*
*Context gathered: 2026-06-14*
