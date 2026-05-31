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

- [ ] **SP-01**: A user can invoke the `school-presentation` skill when they need a school-official-style presentation generated from source materials, outlines, or loose notes.
- [ ] **SP-02**: The skill includes school identity references extracted from the provided PPTX/POTX materials, including logo, slogan, blue-green palette, and reusable decorative marks.
- [ ] **SP-03**: The skill can produce a persistent Markdown intermediate whose body is organized as logical slides with fixed layout intents, speaker notes, and reviewable content warnings.
- [ ] **SP-04**: Markdown logical slides can include formulas, tables, charts, images, videos, and text blocks without bypassing the Markdown source of truth.
- [ ] **SP-05**: The renderer can map Markdown logical slides onto a small fixed layout library and preserve school visual identity without requiring the original PPT layout to be cloned.
- [ ] **SP-06**: The renderer preserves image aspect ratios by default and uses contain-style placement instead of cropping user images.
- [ ] **SP-07**: The renderer detects excessive content and automatically splits one Markdown logical slide into multiple physical HTML pages without requiring the Markdown author to manually move content between pages.
- [ ] **SP-08**: The renderer packages CSS, JavaScript, formulas, charts, and school assets into an offline self-contained HTML presentation when media size permits, with documented behavior for large videos.
- [ ] **SP-09**: The provided fixture generates a school-style HTML deck plus preview/verification artifacts that demonstrate formula, table, chart, image, video, and overflow handling without generic AI-looking visual patterns.

## Deferred Requirements

Deferred to a later milestone. Tracked but not in the current roadmap.

### Additional Targets

- **DWF-FUTURE-01**: Add additional delivery targets beyond current concrete skills, such as DOCX, expanded PDF workflows, PPTX, Keynote, or deployable hosted pages, after the active Markdown-to-target path is stable.
- **DWF-FUTURE-02**: Add reusable page templates, typography presets, or publishing layouts after the core transformation rules are validated.
- **DWF-FUTURE-03**: Add automation or lint tooling after the rules have been exercised by real document workflow skills.

## Out of Scope

Explicitly excluded from v1.1. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Direct source-to-target conversion without Markdown | The milestone is explicitly about a stable Markdown intermediate representation |
| OCR, handwriting recognition, or image-to-text extraction | Input extraction is a separate problem from document workflow transformation |
| General PDF rendering or visual publishing pipeline | v1.2 only validates the concrete Presto gongwen Typst/PDF path |
| Runtime-specific wrappers | v1.1 should stay focused on canonical skill behavior before generated runtime packaging |
| PPTX/Keynote generation for school presentations | v1.5 uses HTML as the primary stable output because prior PPTX generation quality was poor |
| Hosted deployment and password access | Offline single-file HTML packaging must work before any hosting adapter is added |
| Cropping images into decorative frames | School presentation images must preserve original aspect ratio by default |

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
| SP-01 | Phase 8 | Planned |
| SP-02 | Phase 8 | Planned |
| SP-03 | Phase 8 | Planned |
| SP-04 | Phase 8 | Planned |
| SP-05 | Phase 8 | Planned |
| SP-06 | Phase 8 | Planned |
| SP-07 | Phase 8 | Planned |
| SP-08 | Phase 8 | Planned |
| SP-09 | Phase 8 | Planned |

**Coverage:**
- v1.1 requirements: 2 total
- v1.2 requirements: 5 total
- v1.3 requirements: 5 total
- v1.4 requirements: 5 total
- v1.5 requirements: 9 total
- Mapped to phases: 26
- Unmapped: 0

---
*Requirements updated: 2026-05-31 after v1.5 school-presentation milestone start*
