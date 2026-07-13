# Requirements: Presto Agent Skills v1.17 school-pptx

**Defined:** 2026-07-13
**Core Value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## v1.17 Requirements

### Template

- [ ] **TPL-01**: The `school-pptx` skill includes a normalized, skill-local `.pptx` template derived from the supplied school visual `.potx` sample.
- [ ] **TPL-02**: The original `.potx` sample is treated as visual source evidence, not as the renderer's direct runtime template input.
- [ ] **TPL-03**: The normalized template exposes a committed manifest or slot map that defines supported themes, layouts, slots, placeholder identity, geometry, and text budgets.
- [ ] **TPL-04**: The first supported `theme` is a controlled identifier for the normalized default school template, and unknown themes fail with a clear available-theme message.
- [ ] **TPL-05**: The template contract covers exactly these v1.17 layouts: `cover`, `contents`, `section`, `title-content`, `two-column`, `image-text`, `table`, `timeline`, `gallery`, `code`, and `closing`.
- [ ] **TPL-06**: Template-owned geometry, fonts, colors, decorative assets, and optional footer behavior cannot be overridden from Markdown.
- [ ] **TPL-07**: Template text slots use fixed frame geometry with bounded elastic text behavior: text may shrink within the slot's allowed font-size range, but must not overflow visible frames.

### Markdown Contract

- [ ] **MD-01**: The skill defines a teacher-reviewable Markdown source contract using YAML formatter fields plus explicit `::: slide {layout="..."}` blocks.
- [ ] **MD-02**: The YAML formatter supports only these v1.17 fields: `title`, `subtitle`, `school`, `department`, `program`, `course`, `author`, `presenter`, `date`, and `theme`.
- [ ] **MD-03**: Missing optional cover metadata is omitted without moving or resizing other cover elements; if `title` is missing, the first `#` heading is used as the document title fallback.
- [ ] **MD-04**: The generated contents slide is derived from every `##` heading in Markdown order; `#` headings do not enter the contents list.
- [ ] **MD-05**: Every rendered slide block must declare a supported `layout`; unsupported layouts, raw coordinate styling, arbitrary font/color overrides, and unsupported raw HTML fail validation.
- [ ] **MD-06**: The Markdown fixture covers all 11 supported layouts plus speaker notes, images/icons, tables, timeline, gallery, code, and overflow/pagination cases.
- [ ] **MD-07**: Speaker notes are expressed in Markdown separately from slide canvas content and must render into PPTX notes rather than visible slide text.
- [ ] **MD-08**: Image and icon references use normal Markdown image semantics and resolve relative to the Markdown file unless an explicit absolute path is provided.

### PPTX Rendering

- [ ] **PPTX-01**: The renderer generates a non-empty `.pptx` from the accepted Markdown fixture using the normalized template and controlled theme.
- [ ] **PPTX-02**: Generated slide content is editable PowerPoint content where applicable; whole-slide screenshot rendering is forbidden.
- [ ] **PPTX-03**: Text, code, timeline labels, gallery captions, and ordinary body content are emitted as editable text shapes.
- [ ] **PPTX-04**: Tables are emitted as editable PPTX table objects or documented editable table primitives, with predictable column and row behavior.
- [ ] **PPTX-05**: Images and icons are emitted as picture objects with contain-style placement that preserves aspect ratio and avoids default cropping.
- [ ] **PPTX-06**: Gallery layout places up to four images per physical slide and automatically creates additional physical slides when a logical gallery contains more than four images.
- [ ] **PPTX-07**: Timeline layout is horizontal and automatically splits long timelines into additional physical slides instead of compressing items into unreadable slots.
- [ ] **PPTX-08**: Long text, long tables, long timelines, and long galleries expand one Markdown logical slide into multiple PPTX physical slides according to template budgets.
- [ ] **PPTX-09**: Table pagination repeats the table header and automatically adds a continuation marker to table continuation titles; other continuation slides do not add a visible "续" marker.
- [ ] **PPTX-10**: Code blocks render as editable monospace text with stable background/spacing; syntax highlighting is not required in v1.17.
- [ ] **PPTX-11**: Slides with Markdown speaker notes contain corresponding PPTX notes, and slides without notes do not gain accidental notes content.
- [ ] **PPTX-12**: Slide transition behavior is optional: the renderer may preserve or generate a reliable 0.5s smooth transition, but no-transition output remains valid if transition support is unstable.
- [ ] **PPTX-13**: Successful public output contains only the requested `.pptx` and any explicitly requested Markdown source copy; manifests, logs, debug files, and temporary evidence stay hidden or in verification workdirs.

### Verification

- [ ] **VER-01**: The skill provides a repeatable `example` command that writes the full Markdown fixture.
- [ ] **VER-02**: The skill provides a repeatable `template-report` or equivalent command that validates template layouts, slots, placeholders, and manifest consistency.
- [ ] **VER-03**: The skill provides a repeatable `render` command that turns finalized Markdown into PPTX and fails non-zero on invalid input.
- [ ] **VER-04**: The skill provides a repeatable `verify --workdir <dir>` command that exercises example generation, template validation, rendering, and structural PPTX inspection.
- [ ] **VER-05**: Verification checks dependency readiness, including Python, `python-pptx`, and optional Pandoc availability where used.
- [ ] **VER-06**: Verification checks generated slide count, layout mapping, logical-to-physical pagination mapping, and contents entries.
- [ ] **VER-07**: Verification checks notes, media relationships, table structure, code text editability, and absence of whole-slide screenshot shortcuts.
- [ ] **VER-08**: Verification includes negative cases for unknown theme, unknown layout, missing media, unsupported styling, unresolved review markers, and template/manifest mismatch.
- [ ] **VER-09**: Verification records transition mode honestly as `none`, `preserved`, or `generated`; transition absence must not fail v1.17.
- [ ] **VER-10**: Manual visual UAT evidence is recorded for the normalized template and at least one rendered full fixture PPTX before milestone acceptance.

### Skill Delivery

- [ ] **SKILL-01**: The repository adds `skills/school-pptx/SKILL.md` with a concise canonical workflow, trigger wording, inputs, outputs, safety boundaries, and verification instructions.
- [ ] **SKILL-02**: Long authoring rules, template normalization rules, renderer behavior, and verification details live in `skills/school-pptx/references/` rather than bloating the canonical entry.
- [ ] **SKILL-03**: Script implementation is skill-local under `skills/school-pptx/scripts/` and does not call sibling skill scripts at runtime.
- [ ] **SKILL-04**: Runtime adapter notes explicitly cover Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent, including support-file discovery, external command use, dependencies, and write boundaries.
- [ ] **SKILL-05**: Repository discoverability is updated for `README.md`, `skills/README.md`, `docs/directory-spec.md` if needed, and `docs/compatibility-matrix.md`.
- [ ] **SKILL-06**: The skill documents concise clarification questions for missing school/PPT metadata and missing media before final rendering.

## Future Requirements

### Template Expansion

- **FUT-TPL-01**: Support additional normalized school templates through additional controlled `theme` identifiers.
- **FUT-TPL-02**: Provide a guided normalization workflow for new human-friendly `.potx` samples.

### Advanced Rendering

- **FUT-PPTX-01**: Add editable syntax highlighting for code blocks through run-level formatting after plain editable code is stable.
- **FUT-PPTX-02**: Add richer table styling and controlled chart/SmartArt primitives after fixed layouts and editability gates are stable.
- **FUT-PPTX-03**: Add robust slide transitions or object animations only after fixture and cross-viewer compatibility evidence exists.
- **FUT-PPTX-04**: Add optional PPTX-to-PDF or preview image export if a stable local export chain is available.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Direct rendering from arbitrary `.potx` files | v1.17 requires a normalized, machine-mappable template before scripting. |
| Arbitrary PPT template marketplace support | Unknown templates cannot provide stable slot, geometry, and verification contracts in the first version. |
| Markdown-controlled coordinates, fonts, colors, crops, or animation XML | Strict school-template consistency requires template-owned visual decisions. |
| Whole-slide screenshot PPTX output | It destroys the editable-output value of `school-pptx`. |
| Complex object animation | It is unstable for the first version and not required for the accepted scope. |
| Syntax-highlighted code as a hard requirement | Plain editable code blocks are sufficient for v1.17; highlighting is deferred. |
| Hosted sharing, classroom playback controls, and browser-based presentation UX | Those belong to the existing `school-presentation` HTML line, not this PPTX generator. |
| OCR, old PPT deep extraction, or automatic content rewriting | v1.17 starts from reviewed Markdown and a fixed template contract. |
| Strongly enforced global footer insertion | The user confirmed footer behavior should follow the normalized template and not be imposed by the renderer. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| TPL-01 | TBD | Pending |
| TPL-02 | TBD | Pending |
| TPL-03 | TBD | Pending |
| TPL-04 | TBD | Pending |
| TPL-05 | TBD | Pending |
| TPL-06 | TBD | Pending |
| TPL-07 | TBD | Pending |
| MD-01 | TBD | Pending |
| MD-02 | TBD | Pending |
| MD-03 | TBD | Pending |
| MD-04 | TBD | Pending |
| MD-05 | TBD | Pending |
| MD-06 | TBD | Pending |
| MD-07 | TBD | Pending |
| MD-08 | TBD | Pending |
| PPTX-01 | TBD | Pending |
| PPTX-02 | TBD | Pending |
| PPTX-03 | TBD | Pending |
| PPTX-04 | TBD | Pending |
| PPTX-05 | TBD | Pending |
| PPTX-06 | TBD | Pending |
| PPTX-07 | TBD | Pending |
| PPTX-08 | TBD | Pending |
| PPTX-09 | TBD | Pending |
| PPTX-10 | TBD | Pending |
| PPTX-11 | TBD | Pending |
| PPTX-12 | TBD | Pending |
| PPTX-13 | TBD | Pending |
| VER-01 | TBD | Pending |
| VER-02 | TBD | Pending |
| VER-03 | TBD | Pending |
| VER-04 | TBD | Pending |
| VER-05 | TBD | Pending |
| VER-06 | TBD | Pending |
| VER-07 | TBD | Pending |
| VER-08 | TBD | Pending |
| VER-09 | TBD | Pending |
| VER-10 | TBD | Pending |
| SKILL-01 | TBD | Pending |
| SKILL-02 | TBD | Pending |
| SKILL-03 | TBD | Pending |
| SKILL-04 | TBD | Pending |
| SKILL-05 | TBD | Pending |
| SKILL-06 | TBD | Pending |

**Coverage:**
- v1.17 requirements: 44 total
- Mapped to phases: 0
- Unmapped: 44

---
*Requirements defined: 2026-07-13*
*Last updated: 2026-07-13 after v1.17 research synthesis*
