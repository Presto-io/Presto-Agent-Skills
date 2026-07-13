# Phase 42: Markdown Contract and Full Fixture - Context

**Gathered:** 2026-07-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Define one constrained, teacher-reviewable Markdown contract for a complete logical school deck and provide a deterministic full fixture covering all 11 controlled layouts plus notes, media, tables, timeline, gallery, code, and overflow cases. This phase defines source semantics and representative pagination inputs; Phase 43 implements editable PPTX rendering and logical-to-physical pagination. Runtime adapter guidance and final UAT remain in Phase 44.

</domain>

<decisions>
## Implementation Decisions

### Markdown surface
- **D-01:** Slides use explicit `::: slide {layout="..."}` blocks. `layout` is required and must name one of the 11 controlled layouts.
- **D-02:** YAML frontmatter strictly allows only `title`, `subtitle`, `school`, `department`, `program`, `course`, `author`, `presenter`, `date`, and `theme`. Unknown fields fail validation.
- **D-03:** The first `#` is used only as the document-title fallback when YAML `title` is absent. Contents are derived only from `##` slide titles in source order.
- **D-04:** A slide `id` may exist as temporary development/test metadata for diagnostics, but it is not part of the final public authoring contract, generated example, or visible PPTX output.

### Content blocks and slots
- **D-05:** A Markdown paragraph, complete list, image, table, fenced code block, and similar top-level unit is one content block. A `###` line is a forced block boundary that binds only to the immediately following block and renders as that block's visible subheading. An empty `###` acts as a manual block boundary without a visible subheading.
- **D-06:** `two-column` consumes blocks in source order, pairing blocks 1/2 on the first physical page, 3/4 on the next, and so on. A final unpaired block occupies the left column and leaves the right column empty.
- **D-07:** `title-content` and `two-column` may expand one logical slide into multiple same-layout physical slides. Splittable oversized blocks expand into multiple physical blocks according to template budgets.
- **D-08:** Every physical slide title is identical to its logical `##` slide title; no continuation suffix or number is added to the slide title.
- **D-09:** `image-text` remains distinct from generic `two-column`: it expresses one stable body paired with one or more primary images. Multiple images produce successive physical slides with the same slide title and body while only the image and its caption change.
- **D-10:** A table may have its own visible table title, distinct from the `##` slide title. The table title and table form one composite block. Phase 43 planning must reconcile its current roadmap wording so continuation markers are not added to the slide title.

### Notes, media, and validation
- **D-11:** Speaker notes use a `::: notes` block inside the owning slide block and must appear last. Notes never become visible canvas text. If a logical slide expands, all generated physical slides share the same notes.
- **D-12:** Images and icons use normal Markdown image syntax. Relative paths resolve from the Markdown file; absolute paths are allowed. Each image is an atomic content block. Its alt text is the visible caption; empty alt means no caption.
- **D-13:** An image and its optional caption form an indivisible composite block and are fitted into the block container with `contain`: preserve aspect ratio, do not crop, and do not split the image from its caption.
- **D-14:** Missing media is recoverable for best-effort output: use a standard placeholder and report the logical slide, source line, and original path. Structural violations still make validation fail, but an agent may emit a clearly identified best-effort diagnostic artifact by applying safe fallbacks. Invalid input must never be reported as successful validation, and Phase 43's public render command must still satisfy its non-zero failure requirement.
- **D-15:** Unsupported layout names, unknown YAML fields, raw coordinate styling, arbitrary font/color overrides, and unsupported raw HTML are validation errors. Diagnostics should collect and report all locatable errors rather than hiding them.

### Inline emphasis
- **D-16:** Standard `**bold**` expresses bold emphasis. The constrained extension `==highlight==` expresses theme-controlled highlighting. Authors cannot select fonts, colors, or highlight colors; the template owns visual styling and Phase 43 implements the PPTX mapping.
- **D-17:** Native object animation and progressive reveal are not part of Phase 42. Static emphasis remains valid input without animation semantics.

### Full fixture and example command
- **D-18:** The full fixture is a realistic, readable presentation titled around vocational-college intelligent-manufacturing curriculum development, not a visible test matrix.
- **D-19:** The fixture naturally covers all 11 layouts and embeds long text, long tables, long timelines, long code, multi-image content, notes, icons, captions, and other overflow/pagination inputs in the narrative.
- **D-20:** The `example` command is idempotent: every run overwrites a fixed destination with deterministic Markdown and companion media.

### Claude's Discretion
- Choose exact file names and concise wording for the contract and fixture while preserving the locked syntax and semantics above.
- Choose the standard missing-media placeholder and diagnostic formatting, provided errors remain locatable and validation status is truthful.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project scope and requirements
- `.planning/PROJECT.md` — Project goals, portability boundaries, and canonical-skill strategy.
- `.planning/REQUIREMENTS.md` — Locked MD-01 through MD-08 and VER-01 requirements for this phase.
- `.planning/ROADMAP.md` — Phase 42 boundary and Phase 43/44 downstream ownership. Note that Phase 43's table-continuation title wording must be reconciled with D-08 and D-10.
- `.planning/STATE.md` — Current milestone and phase state.

### Prior template contract
- `.planning/phases/41-standard-template-and-manifest/41-CONTEXT.md` — Locked template ownership and the 11-layout boundary.
- `.planning/phases/41-standard-template-and-manifest/41-01-SUMMARY.md` — Implemented template, manifest, and validation entry points.
- `skills/school-pptx/references/template-contract.md` — Controlled theme, layout, slot, geometry, and ownership contract.
- `skills/school-pptx/references/template-editing.md` — Safe template editing and validation workflow.
- `skills/school-pptx/templates/standard-school.manifest.yaml` — Canonical 11-layout slot map and text budgets.
- `skills/school-pptx/scripts/school-pptx.sh` — Existing CLI dispatcher to extend with the repeatable `example` command.

### Markdown and fixture precedents
- `skills/tiaokedan/references/markdown-contract.md` — Existing constrained Markdown-contract precedent.
- `skills/school-presentation/references/authoring-and-layout.md` — Existing school-presentation authoring and layout guidance.
- `skills/school-presentation/templates/school-presentation-full.md` — Existing full presentation fixture precedent.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/school-pptx/templates/standard-school.manifest.yaml`: Reuse its exact layout identifiers, required slots, geometry, and budgets instead of duplicating layout truth in the parser.
- `skills/school-pptx/scripts/school-pptx.sh`: Add the `example` command to the existing skill-local command dispatcher.
- `skills/school-pptx/references/template-contract.md`: Reuse its template-owned styling boundary when documenting forbidden Markdown controls.

### Established Patterns
- The controlled runtime has one theme, `standard-school`, and exactly 11 layouts: `cover`, `contents`, `section`, `title-content`, `two-column`, `image-text`, `table`, `timeline`, `gallery`, `code`, and `closing`.
- Markdown expresses semantic content only. Geometry, fonts, colors, decorative assets, footer behavior, and bounded text behavior remain template-owned.
- Existing presentation references use Markdown-first authoring and can inform syntax, but the new contract must remain specific to `school-pptx` and its manifest.

### Integration Points
- Contract validation must resolve layout names and slot expectations against `standard-school.manifest.yaml`.
- The full fixture and companion assets should live under the `school-pptx` skill and be generated through `school-pptx.sh example` or an equivalent dispatched command.
- Phase 43 consumes the logical block stream, notes, media metadata, captions, and overflow cases defined here to implement editable PPTX output and pagination.

</code_context>

<specifics>
## Specific Ideas

- The fixture should read like a genuine vocational-college intelligent-manufacturing curriculum-development presentation while naturally exercising every layout.
- Images behave like text blocks in pagination. Image plus caption is one `contain`-fitted composite block.
- In `image-text`, successive primary images repeat the same title and body so slide transitions appear to change only the image.
- Validation and best-effort generation are separate outcomes: an artifact may be produced for diagnosis while the command still reports invalid input truthfully.

</specifics>

<deferred>
## Deferred Ideas

- Add left/right `image-text` variants and an explicit marker that begins alternating image placement across subsequent pages; default adjacent pages do not alternate.
- Add semantic progressive-reveal blocks for answers, keywords, and attention cues. Prefer deterministic duplicate physical slides with transitions; native PPT object animation may be an optional later enhancement.

</deferred>

---

*Phase: 42-markdown-contract-and-full-fixture*
*Context gathered: 2026-07-13*
