# Requirements: Presto Agent Skills v1.17 school-pptx

**Defined:** 2026-07-13
**Core Value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## v1.17 Requirements

### Template

- [x] **TPL-01**: The `school-pptx` skill includes a normalized, skill-local `.pptx` template derived from the supplied school visual `.potx` sample.
- [x] **TPL-02**: The original `.potx` sample is treated as visual source evidence, not as the renderer's direct runtime template input.
- [x] **TPL-03**: The normalized template exposes a committed manifest or slot map that defines supported themes, layouts, slots, placeholder identity, geometry, and text budgets.
- [x] **TPL-04**: The first supported `theme` is a controlled identifier for the normalized default school template, and unknown themes fail with a clear available-theme message.
- [x] **TPL-05**: The template contract covers exactly these v1.17 layouts: `cover`, `contents`, `section`, `title-content`, `two-column`, `image-text`, `table`, `timeline`, `gallery`, `code`, and `closing`.
- [x] **TPL-06**: Template-owned geometry, fonts, colors, decorative assets, and optional footer behavior cannot be overridden from Markdown.
- [x] **TPL-07**: Template text slots use fixed frame geometry with bounded elastic text behavior: text may shrink within the slot's allowed font-size range, but must not overflow visible frames.

### Markdown Contract

- [x] **MD-01**: The skill defines a teacher-reviewable Markdown source contract using YAML formatter fields plus explicit `::: slide {layout="..."}` blocks.
- [x] **MD-02**: The YAML formatter supports only these v1.17 fields: `title`, `subtitle`, `school`, `department`, `program`, `course`, `author`, `presenter`, `date`, and `theme`.
- [x] **MD-03**: Missing optional cover metadata is omitted without moving or resizing other cover elements; if `title` is missing, the first `#` heading is used as the document title fallback.
- [x] **MD-04**: The generated contents slide is derived from every `##` heading in Markdown order; `#` headings do not enter the contents list.
- [x] **MD-05**: Every rendered slide block must declare a supported `layout`; unsupported layouts, raw coordinate styling, arbitrary font/color overrides, and unsupported raw HTML fail validation.
- [x] **MD-06**: The Markdown fixture covers all 11 supported layouts plus speaker notes, images/icons, tables, timeline, gallery, code, and overflow/pagination cases.
- [x] **MD-07**: Speaker notes are expressed in Markdown separately from slide canvas content and must render into PPTX notes rather than visible slide text.
- [x] **MD-08**: Image and icon references use normal Markdown image semantics and resolve relative to the Markdown file unless an explicit absolute path is provided.

### PPTX Rendering

- [x] **PPTX-01**: The renderer generates a non-empty `.pptx` from the accepted Markdown fixture using the normalized template and controlled theme.
- [x] **PPTX-02**: Generated slide content is editable PowerPoint content where applicable; whole-slide screenshot rendering is forbidden.
- [x] **PPTX-03**: Text, code, timeline labels, gallery captions, and ordinary body content are emitted as editable text shapes.
- [x] **PPTX-04**: Tables are emitted as editable PPTX table objects or documented editable table primitives, with predictable column and row behavior.
- [x] **PPTX-05**: Images and icons are emitted as picture objects with contain-style placement that preserves aspect ratio and avoids default cropping.
- [x] **PPTX-06**: Gallery layout places up to four images per physical slide and automatically creates additional physical slides when a logical gallery contains more than four images.
- [x] **PPTX-07**: Timeline layout is horizontal and automatically splits long timelines into additional physical slides instead of compressing items into unreadable slots.
- [ ] **PPTX-08**: Long text, long tables, long timelines, and long galleries expand one Markdown logical slide into multiple PPTX physical slides according to template budgets.
- [x] **PPTX-09**: Table pagination repeats the table header and automatically adds a continuation marker to table continuation titles; other continuation slides do not add a visible "续" marker.
- [x] **PPTX-10**: Code blocks render as editable monospace text with stable background/spacing; syntax highlighting is not required in v1.17.
- [x] **PPTX-11**: Slides with Markdown speaker notes contain corresponding PPTX notes, and slides without notes do not gain accidental notes content.
- [x] **PPTX-12**: Slide transition behavior is optional: the renderer may preserve or generate a reliable 0.5s smooth transition, but no-transition output remains valid if transition support is unstable.
- [x] **PPTX-13**: Standard successful public output always contains exactly two same-stem artifacts, the reviewed Markdown source with its input bytes preserved and the rendered PPTX (`.pptx`); manifests, logical JSON, diagnostics, logs, debug files, verification evidence, and temporary files stay hidden or in verification workdirs.

### Verification

- [x] **VER-01**: The skill provides a repeatable `example` command that writes the full Markdown fixture.
- [x] **VER-02**: The skill provides a repeatable `template-report` or equivalent command that validates template layouts, slots, placeholders, and manifest consistency.
- [x] **VER-03**: The skill provides a repeatable `render` command that turns finalized Markdown into PPTX and fails non-zero on invalid input.
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
- [x] **SKILL-03**: Script implementation is skill-local under `skills/school-pptx/scripts/` and does not call sibling skill scripts at runtime.
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
| TPL-01 | Phase 41 | Complete |
| TPL-02 | Phase 41 | Complete |
| TPL-03 | Phase 41 | Complete |
| TPL-04 | Phase 41 | Complete |
| TPL-05 | Phase 41 | Complete |
| TPL-06 | Phase 41 | Complete |
| TPL-07 | Phase 41 | Complete |
| MD-01 | Phase 42 | Complete |
| MD-02 | Phase 42 | Complete |
| MD-03 | Phase 42 | Complete |
| MD-04 | Phase 42 | Complete |
| MD-05 | Phase 42 | Complete |
| MD-06 | Phase 42 | Complete |
| MD-07 | Phase 42 | Complete |
| MD-08 | Phase 42 | Complete |
| PPTX-01 | Phase 43 | Complete |
| PPTX-02 | Phase 43 | Complete |
| PPTX-03 | Phase 43 | Complete |
| PPTX-04 | Phase 43 | Complete |
| PPTX-05 | Phase 43 | Complete |
| PPTX-06 | Phase 43 | Complete |
| PPTX-07 | Phase 43 | Complete |
| PPTX-08 | Phase 43 | Blocked |
| PPTX-09 | Phase 43 | Complete |
| PPTX-10 | Phase 43 | Complete |
| PPTX-11 | Phase 43 | Complete |
| PPTX-12 | Phase 43 | Complete |
| PPTX-13 | Phase 43 | Complete |
| VER-01 | Phase 42 | Complete |
| VER-02 | Phase 41 | Complete |
| VER-03 | Phase 43 | Complete |
| VER-04 | Phase 44 | Pending |
| VER-05 | Phase 44 | Pending |
| VER-06 | Phase 44 | Pending |
| VER-07 | Phase 44 | Pending |
| VER-08 | Phase 44 | Pending |
| VER-09 | Phase 44 | Pending |
| VER-10 | Phase 44 | Pending |
| SKILL-01 | Phase 44 | Pending |
| SKILL-02 | Phase 44 | Pending |
| SKILL-03 | Phase 43 | Complete |
| SKILL-04 | Phase 44 | Pending |
| SKILL-05 | Phase 44 | Pending |
| SKILL-06 | Phase 44 | Pending |

**Coverage:**
- v1.17 requirements: 44 total
- Mapped to phases: 44
- Unmapped: 0

---
*Requirements defined: 2026-07-13*
*Last updated: 2026-07-14 after Phase 43 post-execution verification found four remaining gaps*
