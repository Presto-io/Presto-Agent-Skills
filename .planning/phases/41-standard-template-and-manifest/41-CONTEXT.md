# Phase 41: Standard Template and Manifest - Context

**Gathered:** 2026-07-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 41 establishes the controlled template contract for `school-pptx` before Markdown parsing or PPTX rendering depends on it. It delivers a normalized skill-local runtime `.pptx`, a committed YAML manifest/slot map for all 11 supported layouts, and a repeatable `template-report` validation command.

This phase does not define the Markdown contract, implement Markdown-to-PPTX rendering, build logical-to-physical pagination, or write the final skill entry/runtime adapter documentation beyond what is needed to support the template contract.

</domain>

<decisions>
## Implementation Decisions

### Template Source and Runtime Boundary
- **D-01:** Do not keep the original supplied `.potx` as a long-term committed evidence artifact. Convert it directly into the normalized skill-local runtime `.pptx`.
- **D-02:** Runtime behavior and validation must depend on the normalized `.pptx` plus manifest, not on the original `.potx`.
- **D-03:** Documentation may state that the normalized template is derived from the supplied school visual sample, but downstream agents should treat the skill-local `.pptx` as the controlled template source.

### Manifest Contract
- **D-04:** The manifest must be a full slot contract, not a lightweight index. It must cover theme, layouts, slots, placeholder mapping, geometry, text budgets, empty-slot rules, continuation behavior, and template-owned decorative/footer behavior.
- **D-05:** The manifest format is YAML, because the slot map must remain reviewable and adjustable by humans while still being machine-readable for validators and later renderers.
- **D-06:** The first controlled theme identifier must point to the normalized default school template. Unknown themes must fail clearly and include the available controlled theme identifier.

### Layout and Slot Model
- **D-07:** Phase 41 must include actual inspectable mappings for all 11 v1.17 layouts: `cover`, `contents`, `section`, `title-content`, `two-column`, `image-text`, `table`, `timeline`, `gallery`, `code`, and `closing`.
- **D-08:** Slot naming should use a minimum common foundation plus layout-specific extensions. Common slots should use stable semantic names such as `title`, `subtitle`, `body`, `media`, `caption`, and `footer`; specialized layouts can add slots such as `left_body`, `right_body`, `table`, `timeline_items`, `gallery_items`, and `code`.
- **D-09:** Slot names should not mirror raw PPTX placeholder names when those names are unstable, localized, or polluted by PowerPoint history. PPTX placeholder identity is recorded as mapping metadata, while the manifest exposes stable semantic slot ids.

### Text Budgets and Manual Calibration
- **D-10:** Each text slot should have explicit machine-readable budget fields such as `max_chars`, `max_lines`, `font_size_min`, `font_size_max`, and `overflow` (`shrink`, `paginate`, or `fail`).
- **D-11:** Initial text-budget values are calibration starting points, not proof that every visual boundary is perfect. The expected workflow is to set initial values, open the `.pptx`, test boundary content by hand, and adjust budgets as visual evidence improves.
- **D-12:** Phase 41 validation should verify that budget fields exist, are well-formed, and are reasonable enough for downstream use. It should not claim final pagination quality before Phase 43 rendering tests exist.

### Manual PPTX Adjustment Rules
- **D-13:** It is acceptable, and preferred, for Codex to generate an initial `.pptx` framework and for the user to manually drag, resize, and refine placeholders in PowerPoint or another compatible editor.
- **D-14:** Manual edits must preserve mapping anchors. Do not delete mapped placeholders, replace them with ordinary shapes, rename stable placeholder anchors, remove alt text/tags used for mapping, or duplicate placeholders without assigning distinct identifiers.
- **D-15:** New decorative elements are allowed if they are template-owned and excluded from Markdown-controllable slots. New content slots are allowed only when the manifest is updated with slot id, purpose, geometry, placeholder mapping, and budget.
- **D-16:** After manual template edits, `template-report` must be run to detect missing slots, duplicate slots, unknown placeholders, and manifest/PPTX geometry mismatch.

### Template Validation and Evidence
- **D-17:** The template validation command should be named `template-report` or an equivalent explicit template-reporting command.
- **D-18:** The command must produce both a human-readable Markdown report and machine-readable JSON evidence.
- **D-19:** At minimum, validation must fail non-zero for unknown theme, missing required layout, missing slot, duplicate slot, lost placeholder mapping, manifest/PPTX geometry mismatch, and missing or malformed budget fields.
- **D-20:** The Markdown report should be suitable as human Phase 41 verification evidence; the JSON evidence should be suitable for later structural verification and CI-style checks.

### Claude's Discretion
- Planner may choose concrete file names and internal YAML schema details as long as they satisfy the decisions above and remain consistent with repository conventions.
- Planner may decide whether the 11 layouts are represented as PowerPoint slide layouts, template slides, or another inspectable PPTX mapping mechanism, as long as all mappings are explicit and `template-report` can validate them.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope
- `.planning/ROADMAP.md` — Phase 41 goal, success criteria, phase order, and v1.17 delivery boundary.
- `.planning/REQUIREMENTS.md` — TPL-01 through TPL-07 and VER-02 requirements that Phase 41 must satisfy.
- `.planning/PROJECT.md` — v1.17 project context, active milestone constraints, and template-first discipline.
- `.planning/STATE.md` — current milestone state and known concern that Phase 41 needs a real supplied `.potx` sample or accepted local evidence before completion.

### Existing Skill Patterns
- `skills/school-presentation/references/authoring-and-layout.md` — prior school presentation fixed-canvas/layout discipline and template-owned visual behavior, used as conceptual precedent only.
- `skills/school-presentation/references/verification-contract.md` — precedent for repeatable verification/reporting expectations and human visual UAT boundary.
- `skills/tiaokedan/SKILL.md` — recent pattern for establishing a hand-reviewed baseline before automation and keeping runtime behavior skill-local.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/school-presentation/` provides school-presentation authoring, fixed-canvas, and verification language that can inform `school-pptx`, but the new skill must not become an extension of the HTML presentation line.
- `skills/tiaokedan/` provides a recent example of a compact canonical skill entry, skill-local script boundary, clear verification checklist, and hidden diagnostics discipline.

### Established Patterns
- New skills live under `skills/<skill-name>/` with concise `SKILL.md`, deeper `references/`, `templates/`, and `scripts/` as needed.
- Long rules belong in `references/`; the canonical skill entry should stay concise and runtime-portable.
- Successful public outputs should stay clean; manifests, logs, debug artifacts, and verification evidence belong in hidden workdirs or explicit verification workdirs.
- Runtime differences for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent belong in adapter notes, not in the canonical workflow body.

### Integration Points
- Expected new paths are likely under `skills/school-pptx/`, including `templates/` for the normalized `.pptx` and YAML manifest, `scripts/` for `template-report`, and `references/` for template-normalization and manual-editing rules.
- Repository discoverability updates are not part of Phase 41 unless needed by the plan, but later Phase 44 must cover `README.md`, `skills/README.md`, and `docs/compatibility-matrix.md`.

</code_context>

<specifics>
## Specific Ideas

- The user wants the `.potx` directly transformed into the normalized `.pptx` rather than committed separately as durable evidence.
- The user explicitly wants to be able to manually drag and resize the generated PPTX framework, with guardrails that prevent breaking slot mappings.
- Text budgets should be real manifest fields, but should be treated as values that are refined through manual testing rather than perfectly known upfront.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 41-Standard Template and Manifest*
*Context gathered: 2026-07-13*
