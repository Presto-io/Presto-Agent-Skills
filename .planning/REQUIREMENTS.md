# Requirements: Presto Agent Skills v1.16 调课单 Skill

**Defined:** 2026-06-21
**Core Value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## v1.16 Requirements

### Typst Baseline

- [x] **TKD-TYP-01**: The `调课单` skill includes a hand-authored Typst reference file that captures the accepted adjustment-form layout before automation. - v1.16 Phase 37
- [x] **TKD-TYP-02**: The Typst reference records the required visible fields, labels, table structure, signature/approval areas, and typography decisions needed for PDF output. - v1.16 Phase 37
- [x] **TKD-TYP-03**: The Typst reference can be compiled to a non-empty PDF with the repository's local Typst workflow when required fonts and tools are available. - v1.16 Phase 37

### Markdown Contract

- [x] **TKD-MD-01**: The `调课单` skill includes a hand-authored Markdown fixture that is teacher-readable and contains all facts required by the Typst form.
- [x] **TKD-MD-02**: The Markdown contract separates user-maintained form facts from renderer-only defaults, so teachers do not need to write raw Typst.
- [x] **TKD-MD-03**: The Markdown fixture and reference documentation define how missing or unknown adjustment facts should be marked before final rendering.

### Renderer Script

- [ ] **TKD-RENDER-01**: The `调课单` skill includes a skill-local command surface that converts finalized Markdown into Typst.
- [ ] **TKD-RENDER-02**: The renderer is independent at runtime: it may borrow patterns from existing skills, but it does not call sibling skill scripts or depend on sibling skill directories.
- [ ] **TKD-RENDER-03**: The renderer verifies generated Typst against the hand-authored reference through deterministic checks suitable for phase evidence.
- [ ] **TKD-RENDER-04**: The renderer reports clear non-zero failures for missing required fields, malformed Markdown sections, or unsupported values.

### PDF Workflow and Skill Entry

- [ ] **TKD-PDF-01**: The `调课单` skill provides a documented PDF generation workflow from finalized Markdown through generated Typst to final PDF.
- [ ] **TKD-PDF-02**: Successful default output is clean and teacher-facing, while diagnostics, comparison evidence, logs, and temporary files remain hidden or explicitly debug-only.
- [ ] **TKD-PDF-03**: The canonical `SKILL.md` describes when to use the skill, the Markdown-first workflow, safety boundaries, verification steps, and runtime adapter notes for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
- [ ] **TKD-PDF-04**: The skill documentation includes concise questions to ask when source information is insufficient before generating final Typst/PDF artifacts.
- [ ] **TKD-PDF-05**: Repository indexes and directory guidance make the new `调课单` skill discoverable without introducing agent-private syntax into the canonical skill body.

## Future Requirements

- **TKD-FUT-01**: Support multiple school-specific `调课单` variants if real accepted forms diverge.
- **TKD-FUT-02**: Add batch generation for many adjustment forms after the single-form workflow is stable.
- **TKD-FUT-03**: Add structured data import from spreadsheets if teachers later provide adjustment data in table form.

## Out of Scope

| Feature | Reason |
|---------|--------|
| OCR or photo-to-form extraction | The first milestone starts from user-provided facts and a reviewable Markdown source, not image recognition. |
| Runtime dependency on other skill scripts | The user explicitly requested borrowing implementation ideas without depending on other skills' scripts. |
| Freeform arbitrary form discovery | The milestone targets one concrete `调课单` form, with variants deferred until real accepted examples require them. |
| One-step source-to-PDF without Markdown review | This would violate the repository's Markdown-first document workflow discipline. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| TKD-TYP-01 | Phase 37 | Complete — `.planning/phases/37-typst-baseline/37-VERIFICATION.md` |
| TKD-TYP-02 | Phase 37 | Complete — `.planning/phases/37-typst-baseline/37-VERIFICATION.md` |
| TKD-TYP-03 | Phase 37 | Complete — non-empty `skills/tiaokedan/templates/tiaokedan-reference.pdf` |
| TKD-MD-01 | Phase 38 | Complete |
| TKD-MD-02 | Phase 38 | Complete |
| TKD-MD-03 | Phase 38 | Complete |
| TKD-RENDER-01 | Phase 39 | Pending |
| TKD-RENDER-02 | Phase 39 | Pending |
| TKD-RENDER-03 | Phase 39 | Pending |
| TKD-RENDER-04 | Phase 39 | Pending |
| TKD-PDF-01 | Phase 40 | Pending |
| TKD-PDF-02 | Phase 40 | Pending |
| TKD-PDF-03 | Phase 40 | Pending |
| TKD-PDF-04 | Phase 40 | Pending |
| TKD-PDF-05 | Phase 40 | Pending |

**Coverage:**
- v1.16 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0

---
*Requirements defined: 2026-06-21*
*Last updated: 2026-06-21 after milestone v1.16 definition*
