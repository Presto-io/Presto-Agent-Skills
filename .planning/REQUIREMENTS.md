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

## Deferred Requirements

Deferred to a later milestone. Tracked but not in the current roadmap.

### Additional Targets

- **DWF-FUTURE-01**: Add HTML delivery, Typst, DOCX, PDF, or other target formats after the Markdown normalization contract is stable and there is a concrete need.
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

**Coverage:**
- v1.1 requirements: 2 total
- v1.2 requirements: 5 total
- v1.3 requirements: 5 total
- v1.4 requirements: 5 total
- Mapped to phases: 17
- Unmapped: 0

---
*Requirements updated: 2026-05-31 after v1.4 jiaoan-jihua skill implementation*
