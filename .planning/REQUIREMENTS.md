# Requirements: Presto Agent Skills

**Defined:** 2026-05-31
**Core Value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## v1.1 Requirements

Requirements for the document workflow milestone. The workflow treats Markdown as the canonical intermediate representation before target-specific output.

### Markdown Normalization

- [x] **DWF-01**: A contributor can normalize arbitrary source content into a clean Markdown intermediate document that preserves document structure and intent.
- [x] **DWF-02**: Ambiguous, unsupported, or lossy input fragments are explicitly flagged during Markdown normalization instead of being silently guessed or dropped.

### HTML Output and Verification

- [ ] **DWF-03**: A contributor can transform the Markdown intermediate into semantic HTML that preserves structure and document intent.
- [ ] **DWF-04**: A contributor can validate the Markdown intermediate and HTML output before delivery.

## Deferred Requirements

Deferred to a later milestone. Tracked but not in the current roadmap.

### Additional Targets

- **DWF-FUTURE-01**: Add Typst, DOCX, PDF, or other target formats after the Markdown-to-HTML contract is stable and there is a concrete need.
- **DWF-FUTURE-02**: Add reusable page templates, typography presets, or publishing layouts after the core transformation rules are validated.
- **DWF-FUTURE-03**: Add automation or lint tooling after the rules have been exercised by real document workflow skills.

## Out of Scope

Explicitly excluded from v1.1. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Direct source-to-HTML conversion without Markdown | The milestone is explicitly about a stable Markdown intermediate representation |
| OCR, handwriting recognition, or image-to-text extraction | Input extraction is a separate problem from document workflow transformation |
| Full PDF rendering or visual publishing pipeline | The milestone defines transform rules, not final rendering infrastructure |
| Runtime-specific wrappers | v1.1 should stay focused on canonical skill behavior before generated runtime packaging |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DWF-01 | Phase 4 | Complete |
| DWF-02 | Phase 4 | Complete |
| DWF-03 | Phase 5 | Pending |
| DWF-04 | Phase 5 | Pending |

**Coverage:**
- v1.1 requirements: 4 total
- Mapped to phases: 4
- Unmapped: 0

---
*Requirements updated: 2026-05-31 after removing Typst constraint phase*
