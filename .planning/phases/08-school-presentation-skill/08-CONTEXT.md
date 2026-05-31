# Phase 8: School Presentation Skill - Context

**Gathered:** 2026-05-31
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers the first `school-presentation` skill. It should turn source materials, outlines, or loose notes into a persistent Markdown logical-slide intermediate, then render that intermediate into a blue-green school-style offline HTML presentation.

The phase is HTML-first and Markdown-first. It does not add PPTX, Keynote, hosted sharing, multi-device sync, annotation tools, OCR, handwriting recognition, or a school-template marketplace. Markdown owns logical slide content; the renderer owns fixed layout selection, physical page splitting, text fitting, media packaging, and repeatable output generation.

</domain>

<decisions>
## Implementation Decisions

### Markdown Logical-Slide Structure
- **D-01:** Planner and executor should design the first Markdown logical-slide structure. The user delegated the exact structure to Claude.
- **D-02:** The Markdown structure must stay persistent and human-editable, following the existing `YAML frontmatter + body` document workflow contract.
- **D-03:** The structure must support fixed layout intents, speaker notes, reviewable warnings, formulas, tables, charts, images, videos, and text blocks without bypassing the Markdown source of truth.
- **D-04:** Logical slides are not guaranteed to map one-to-one to physical HTML pages. Overflow splitting remains a renderer responsibility.

### Layout Selection
- **D-05:** The renderer should automatically choose layouts by default.
- **D-06:** Users must be able to override the automatic layout choice in Markdown when they need a specific layout.
- **D-07:** Use a small fixed layout library rather than cloning arbitrary original PPT layouts. The layout library should preserve school identity and keep output stable.

### School Identity Assets
- **D-08:** School identity elements should live under the `school-presentation` skill directory. Planner and executor may choose the exact subdirectory layout.
- **D-09:** Prefer skill-local storage such as `skills/school-presentation/references/` for extracted source/provenance notes and `skills/school-presentation/assets/` or a similarly clear skill-owned path for reusable renderer assets.
- **D-10:** The asset set should cover logo, slogan, blue-green palette, reusable decorative marks, and provenance from the provided PPTX/POTX materials when available.

### Offline Packaging And Size Limit
- **D-11:** Final presentation output should not exceed 50 MB.
- **D-12:** The renderer should package CSS, JavaScript, formulas, charts, images, and school assets into a self-contained offline HTML deck when the 50 MB cap permits.
- **D-13:** Large videos or other oversized media should use documented fallback behavior instead of inflating the HTML beyond 50 MB.
- **D-14:** Image placement should preserve original aspect ratios by default and use contain-style placement rather than cropping.

### Verification Direction
- **D-15:** The user will perform final human visual verification.
- **D-16:** Automated verification should focus on repeatability and template reasonableness: same Markdown input should produce consistent output, and Markdown controls should have clear, predictable effects on the generated HTML.
- **D-17:** The phase does not need heavy visual judgment automation. It should still provide enough deterministic artifacts or checks for downstream agents to confirm the renderer is stable.

### Claude's Discretion
The user explicitly delegated Markdown slide schema design and school asset directory design to Claude. Planner and executor should make conservative choices that match existing repository patterns: skill-specific files under `skills/school-presentation/`, concise canonical `SKILL.md`, reusable templates in `templates/`, references/provenance in `references/`, scripts in `scripts/`, and runtime differences only in adapter notes.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Planning
- `.planning/ROADMAP.md` — Defines Phase 8 goal, requirements, and success criteria for `school-presentation`.
- `.planning/REQUIREMENTS.md` — Defines SP-01 through SP-09 and v1.5 out-of-scope boundaries.
- `.planning/PROJECT.md` — Defines the v1.5 milestone purpose, HTML-first direction, and project constraints.
- `.planning/STATE.md` — Records current workflow state and prior v1.5 decisions.

### Prior Decisions
- `.planning/phases/04-markdown-normalization-contract/04-CONTEXT.md` — Locks the minimal `YAML frontmatter + body` Markdown intermediate contract and skill-owned target rendering.
- `.planning/phases/02-canonical-skill-format-and-runtime-adapters/02-CONTEXT.md` — Locks one canonical `SKILL.md` plus lightweight runtime adapter notes.
- `.planning/phases/03-portable-example-skill/03-CONTEXT.md` — Carries forward the lean, non-example-heavy repository direction.

### School Presentation Research
- `.planning/research/v1.5-school-presentation-stack.md` — Recommends Markdown logical slides plus a custom school-style HTML renderer; rejects PPTX as the v1.5 primary output.
- `.planning/spikes/001-html-first-markdown-presentation-stack/README.md` — Validated spike comparing Marp, Slidev, reveal.js, Pandoc, and Deckset; supports reveal.js-style HTML rendering with fixed layout families.

### Repository Contract
- `docs/markdown-normalization-contract.md` — Defines the shared Markdown intermediate contract for document workflow skills.
- `templates/skill/SKILL.md` — Canonical skill template and required sections for portable skills.
- `docs/directory-spec.md` — Directory ownership rules for skills, templates, references, scripts, and docs.
- `docs/compatibility-matrix.md` — Runtime compatibility expectations for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
- `skills/gongwen/SKILL.md` — Existing concrete skill pattern for a Markdown-first workflow with script usage, runtime adapter notes, verification, and safety boundaries.
- `skills/jiaoan-shicao/SKILL.md` — Existing concrete teaching-document skill pattern.
- `skills/jiaoan-jihua/SKILL.md` — Existing concrete teaching-schedule skill pattern with skill-local support resources.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `templates/skill/SKILL.md`: Provides the canonical structure for `school-presentation/SKILL.md`, including description, objective, process, outputs, verification, safety, and runtime adapter notes.
- `docs/markdown-normalization-contract.md`: Provides the shared normalization boundary that the presentation Markdown intermediate must follow without imposing universal fields.
- `skills/gongwen/SKILL.md`, `skills/jiaoan-shicao/SKILL.md`, and `skills/jiaoan-jihua/SKILL.md`: Provide the established concrete-skill style for trigger wording, Markdown intermediate guidance, script usage, adapter notes, outputs, verification, and safety.
- `skills/jiaoan-jihua/references/calendar.json`: Demonstrates that support resources can live under a skill-local `references/` directory.
- `.planning/research/v1.5-school-presentation-stack.md` and `.planning/spikes/001-html-first-markdown-presentation-stack/README.md`: Provide the already-validated HTML-first implementation direction.

### Established Patterns
- One canonical `SKILL.md` remains the semantic source of truth.
- Runtime-specific behavior belongs in Runtime Adapter Notes, not in duplicated per-runtime skill files.
- New skills live under `skills/<skill-name>/SKILL.md`.
- Skill templates live under `skills/<skill-name>/templates/`.
- Skill scripts live under `skills/<skill-name>/scripts/`.
- Skill support resources and provenance notes can live under `skills/<skill-name>/references/`.
- Existing concrete skills use shell scripts as stable entry points for example generation and rendering.

### Integration Points
- Add `skills/school-presentation/SKILL.md`.
- Add `skills/school-presentation/templates/school-presentation-full.md`.
- Add `skills/school-presentation/scripts/school-presentation.sh`.
- Add skill-local school identity resources and provenance notes under a clear `skills/school-presentation/` subdirectory chosen during planning.
- Update discovery pointers only if required by the repository contract; avoid broad example-heavy docs.

</code_context>

<specifics>
## Specific Ideas

- The user wants Claude to design the Markdown logical-slide structure.
- Layout should be automatic by default, while still allowing user override.
- School identity elements should be stored inside the skill directory; exact path is delegated.
- Output size must stay at or below 50 MB.
- Human visual verification is the final quality gate.
- Automated checks should emphasize deterministic output and a reasonable Markdown-to-template control design, not subjective visual scoring.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. PPTX/Keynote export, hosted delivery, OCR, multi-device sync, annotation tools, and broader template marketplaces remain outside v1.5.

</deferred>

---

*Phase: 8-School Presentation Skill*
*Context gathered: 2026-05-31*
