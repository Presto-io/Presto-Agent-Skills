# Requirements: Presto Agent Skills

**Defined:** 2026-05-31
**Core Value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## v1.1 Requirements

Requirements for the document workflow milestone. The workflow treats Markdown as the canonical intermediate representation before target-specific output.

### Markdown Normalization

- [x] **DWF-01**: A contributor can normalize arbitrary source content into a clean Markdown intermediate document that preserves document structure and intent.
- [x] **DWF-02**: Ambiguous, unsupported, or lossy input fragments are explicitly flagged during Markdown normalization instead of being silently guessed or dropped.

### Typst Output

- [ ] **DWF-03**: A contributor can transform the Markdown intermediate into Typst code that obeys the project's hard Typst constraints.
- [ ] **DWF-04**: Unsupported Markdown constructs have documented Typst handling rules: reject, rewrite, or isolate with an explicit note.

### HTML Output and Verification

- [ ] **DWF-05**: A contributor can transform the same Markdown intermediate into semantic HTML that preserves structure and document intent.
- [ ] **DWF-06**: A contributor can validate the Markdown intermediate and target output before delivery, including checks for Typst hard-constraint violations.

## Deferred Requirements

Deferred to a later milestone. Tracked but not in the current roadmap.

### Additional Targets

- **DWF-FUTURE-01**: Add DOCX, PDF, or other target formats after the Markdown-to-Typst/HTML contract is stable.
- **DWF-FUTURE-02**: Add reusable page templates, typography presets, or publishing layouts after the core transformation rules are validated.
- **DWF-FUTURE-03**: Add automation or lint tooling after the rules have been exercised by real document workflow skills.

## Out of Scope

Explicitly excluded from v1.1. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Direct source-to-Typst or source-to-HTML conversion without Markdown | The milestone is explicitly about a stable Markdown intermediate representation |
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
| DWF-05 | Phase 6 | Pending |
| DWF-06 | Phase 6 | Pending |

**Coverage:**
- v1.1 requirements: 6 total
- Mapped to phases: 6
- Unmapped: 0

---
*Requirements defined: 2026-05-31 after v1.1 milestone definition*
