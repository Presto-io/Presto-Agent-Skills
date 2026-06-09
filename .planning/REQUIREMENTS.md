# Requirements: Presto Agent Skills

**Defined:** 2026-05-31
**Core Value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## v1.1 Requirements

Requirements for the document workflow milestone. The workflow treats Markdown as the canonical intermediate representation before target-specific output.

### Markdown Normalization

- [x] **DWF-01**: A contributor can normalize arbitrary source content into a clean Markdown intermediate document that preserves document structure and intent.
- [x] **DWF-02**: Ambiguous, unsupported, or lossy input fragments are explicitly flagged during Markdown normalization instead of being silently guessed or dropped.

## v1.2 Requirements

Requirements for the first concrete document workflow skill.

### Gongwen Skill

- [x] **GW-01**: A user can invoke the `gongwen` skill when they need Chinese official-document style writing.
- [x] **GW-02**: The skill can produce a persistent `gongwen-full.md` style Markdown intermediate with frontmatter, headings, paragraphs, lists, tables, figures, page breaks, and local reviewable formatting controls.
- [x] **GW-03**: The skill includes script code that renders the Markdown intermediate through the Presto `presto-template-gongwen` black-box template into Typst.
- [x] **GW-04**: The script can compile the generated Typst into a PDF verification artifact with Typst.
- [x] **GW-05**: The provided `gongwen-full.md` fixture generates Typst and PDF artifacts matching the provided references.

## v1.3 Requirements

Requirements for the second concrete document workflow skill.

### Jiaoan Shicao Skill

- [x] **JS-01**: A user can invoke the `jiaoan-shicao` skill when they need 实操教案、实训教案、教学活动设计或项目化教学单元.
- [x] **JS-02**: The skill can produce a persistent `jiaoan-shicao-full.md` style Markdown intermediate with frontmatter, learning-task analysis, teaching-activity design, evaluation, and reviewable formatting controls.
- [x] **JS-03**: The skill includes script code that renders the Markdown intermediate through the Presto `presto-template-jiaoan-shicao` black-box template into Typst.
- [x] **JS-04**: The script can compile the generated Typst into a PDF verification artifact with Typst.
- [x] **JS-05**: The provided `jiaoan-shicao-full.md` fixture generates Typst matching the provided reference and a PDF verification artifact.

## v1.4 Requirements

Requirements for the teaching-schedule progress skill.

### Jiaoan Jihua Skill

- [x] **JH-01**: A user can invoke the `jiaoan-jihua` skill when they need 授课进度计划表、教学进度安排或课程实施进度表.
- [x] **JH-02**: The skill can produce a persistent `jiaoan-jihua-full.md` style Markdown intermediate with frontmatter, task headings, stage headings, hour suffixes, bundled `calendar.json`, and reviewable scheduling controls.
- [x] **JH-03**: The skill includes script code that renders the Markdown intermediate through the Presto `presto-template-jiaoan-jihua` black-box template into Typst.
- [x] **JH-04**: The script can compile the generated Typst into a PDF verification artifact with Typst.
- [x] **JH-05**: The provided `jiaoan-jihua-full.md` fixture generates Typst matching the provided reference and a PDF verification artifact.

## v1.5 Requirements

Requirements for the school-style HTML presentation skill.

### School Presentation Skill

- [x] **SP-01**: A user can invoke the `school-presentation` skill when they need a school-official-style presentation generated from source materials, outlines, or loose notes.
- [x] **SP-02**: The skill includes school identity references extracted from the provided PPTX/POTX materials, including logo, slogan, blue-green palette, and reusable decorative marks.
- [x] **SP-03**: The skill can produce a persistent Markdown intermediate whose body is organized as logical slides with fixed layout intents, speaker notes, and reviewable content warnings.
- [x] **SP-04**: Markdown logical slides can include formulas, tables, charts, images, videos, and text blocks without bypassing the Markdown source of truth.
- [x] **SP-05**: The renderer can map Markdown logical slides onto a small fixed layout library and preserve school visual identity without requiring the original PPT layout to be cloned.
- [x] **SP-06**: The renderer preserves image aspect ratios by default and uses contain-style placement instead of cropping user images.
- [x] **SP-07**: The renderer detects excessive content and automatically splits one Markdown logical slide into multiple physical HTML pages without requiring the Markdown author to manually move content between pages.
- [x] **SP-08**: The renderer packages CSS, JavaScript, formulas, charts, and school assets into an offline self-contained HTML presentation when media size permits, with documented behavior for large videos.
- [x] **SP-09**: The provided fixture generates a school-style HTML deck plus preview/verification artifacts that demonstrate formula, table, chart, image, video, and overflow handling without generic AI-looking visual patterns.

## v1.6 Requirements

Requirements for refining the school-style HTML presentation skill into an interactive playback and classroom preview experience.

### School Presentation Playback UX

- [x] **SP-10**: A presenter can play the generated HTML deck with mouse and keyboard navigation, including previous/next movement and a focused presentation view.
- [x] **SP-11**: A presenter can use a slide-software-style preview workspace with a left thumbnail rail and a synchronized large preview on the right.
- [x] **SP-12**: A presenter can switch to a tiled overview that shows the generated physical pages for rapid scanning and page selection.
- [x] **SP-13**: The Markdown intermediate can express page hierarchy for logical slides, physical pages, sections, and reveal steps, and the rendered UI exposes that hierarchy for navigation.
- [x] **SP-14**: A Markdown author can mark emphasized content and ordered reveal groups whose click order is explicit and does not have to follow visual top-to-bottom order.
- [x] **SP-15**: The renderer animates content emphasis and ordered reveals in a stable, classroom-appropriate way during playback.
- [x] **SP-16**: A Markdown author can define answer masks for classroom questions so selected answers remain covered until the presenter advances them step by step.

## v1.7 Requirements

Requirements for the end-of-term teaching-materials skill. The workflow starts from explicit structured teaching data, writes a reviewable Markdown intermediate, then renders fixed-template Typst/PDF and table artifacts for semester-end submission.

### End-of-Term Teaching Materials Skill

- [x] **ETM-01**: A user can invoke the end-of-term teaching-materials skill when they need to generate semester-end teaching submission documents and tables from course, class, semester, teaching-record, and assessment data.
- [x] **ETM-02**: The skill includes a documented structured data contract for required and optional fields, including course metadata, class metadata, teacher metadata, semester metadata, teaching-hour records, assessment records, and submission metadata.
- [x] **ETM-03**: The skill can produce a persistent Markdown intermediate that keeps each document and table section reviewable before rendering.
- [x] **ETM-04**: The Markdown intermediate explicitly flags missing, ambiguous, or lossy teaching data instead of guessing silently.
- [x] **ETM-05**: The skill includes fixed templates for the semester-end teaching-materials package and keeps template-specific rules inside the skill directory.
- [x] **ETM-06**: The skill includes script code that converts structured data to Markdown, renders Markdown to Typst, and compiles Typst to PDF.
- [x] **ETM-07**: The skill can emit required table artifacts in a deterministic reviewable format alongside the PDF package.
- [x] **ETM-08**: The skill defines verification steps for data validation, Markdown generation, Typst generation, PDF compilation, table output, and runtime adapter compatibility across Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.

## Deferred Requirements

Deferred to a later milestone. Tracked but not in the current roadmap.

### Additional Targets

- **DWF-FUTURE-01**: Add additional delivery targets beyond current concrete skills, such as DOCX, expanded PDF workflows, PPTX, Keynote, or deployable hosted pages, after the active Markdown-to-target path is stable.
- **DWF-FUTURE-02**: Add reusable page templates, typography presets, or publishing layouts after the core transformation rules are validated.
- **DWF-FUTURE-03**: Add automation or lint tooling after the rules have been exercised by real document workflow skills.
- **SP-FUTURE-01**: Add presenter marking, annotation, drawing, and in-class markup tools after playback, hierarchy, reveal, and masking behavior are stable.
- **ETM-FUTURE-01**: Add DOCX or spreadsheet-native exports after the fixed Markdown-to-Typst/PDF package is stable.
- **ETM-FUTURE-02**: Add additional school-specific template packs after the first fixed end-of-term package is verified.
- **ETM-FUTURE-03**: Add OCR or automatic extraction from unstructured files after the structured data contract is stable.

## Out of Scope

Explicitly excluded from current and prior milestones. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Direct source-to-target conversion without Markdown | The milestone is explicitly about a stable Markdown intermediate representation |
| OCR, handwriting recognition, or image-to-text extraction | Input extraction is a separate problem from document workflow transformation |
| General PDF rendering or visual publishing pipeline | v1.2 only validates the concrete Presto gongwen Typst/PDF path |
| Runtime-specific wrappers | v1.1 should stay focused on canonical skill behavior before generated runtime packaging |
| PPTX/Keynote generation for school presentations | v1.5 uses HTML as the primary stable output because prior PPTX generation quality was poor |
| Hosted deployment and password access | Offline single-file HTML packaging must work before any hosting adapter is added |
| Cropping images into decorative frames | School presentation images must preserve original aspect ratio by default |
| Marking and annotation tools | User explicitly deferred marker-style functionality to the next milestone |
| One-step data-to-PDF generation for end-of-term materials | v1.7 requires a persistent Markdown checkpoint before Typst/PDF rendering |
| Arbitrary template discovery or marketplace support | v1.7 targets fixed submission templates, not uncontrolled template inference |
| OCR or handwriting extraction for teaching records | v1.7 starts from explicit structured data; extraction is a separate future workflow |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DWF-01 | Phase 4 | Complete |
| DWF-02 | Phase 4 | Complete |
| GW-01 | Phase 5 | Complete |
| GW-02 | Phase 5 | Complete |
| GW-03 | Phase 5 | Complete |
| GW-04 | Phase 5 | Complete |
| GW-05 | Phase 5 | Complete |
| JS-01 | Phase 6 | Complete |
| JS-02 | Phase 6 | Complete |
| JS-03 | Phase 6 | Complete |
| JS-04 | Phase 6 | Complete |
| JS-05 | Phase 6 | Complete |
| JH-01 | Phase 7 | Complete |
| JH-02 | Phase 7 | Complete |
| JH-03 | Phase 7 | Complete |
| JH-04 | Phase 7 | Complete |
| JH-05 | Phase 7 | Complete |
| SP-01 | Phase 8 | Complete |
| SP-02 | Phase 8 | Complete |
| SP-03 | Phase 8 | Complete |
| SP-04 | Phase 8 | Complete |
| SP-05 | Phase 8 | Complete |
| SP-06 | Phase 8 | Complete |
| SP-07 | Phase 8 | Complete |
| SP-08 | Phase 8 | Complete |
| SP-09 | Phase 8 | Complete |
| SP-10 | Phase 9 | Complete |
| SP-11 | Phase 9 | Complete |
| SP-12 | Phase 9 | Complete |
| SP-13 | Phase 9 | Complete |
| SP-14 | Phase 10 | Complete |
| SP-15 | Phase 10 | Complete |
| SP-16 | Phase 10 | Complete |
| ETM-01 | Phase 11 | Complete |
| ETM-02 | Phase 11 | Complete |
| ETM-03 | Phase 11 | Complete |
| ETM-04 | Phase 11 | Complete |
| ETM-05 | Phase 12 | Complete |
| ETM-06 | Phase 12 | Complete |
| ETM-07 | Phase 12 | Complete |
| ETM-08 | Phase 12 | Complete |

**Coverage:**
- v1.1 requirements: 2 total
- v1.2 requirements: 5 total
- v1.3 requirements: 5 total
- v1.4 requirements: 5 total
- v1.5 requirements: 9 total
- v1.6 requirements: 7 total
- v1.7 requirements: 8 total
- Mapped to phases: 41
- Unmapped: 0

---
*Requirements updated: 2026-06-09 after Phase 12 rendering completion*
