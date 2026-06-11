# Requirements: Presto Agent Skills

**Defined:** 2026-06-11
**Milestone:** v1.8 School Presentation Continuation
**Core Value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## v1.8 Requirements

Requirements for continuing the official-school presentation skill from the previously deferred Phase 10 scope.

### Presenter Markup

- [x] **SP-17**: A presenter can enable playback-local marking tools, including pointer, pen, highlighter, eraser, and clear/reset controls.
- [x] **SP-18**: A presenter can mark over the current physical page without mutating the Markdown source, manifest hierarchy, preview workspace content, or deterministic review output.
- [x] **SP-19**: Annotation state is scoped to the active deck session and page, remains usable with keyboard/mouse/touch playback navigation, and can be safely cleared.
- [x] **SP-20**: The verification fixture demonstrates presenter marking controls without breaking playback navigation, ordered reveals, emphasis animation, or answer masks.

### Classroom Interaction Extensions

- [x] **SP-21**: A Markdown author can define hover/peek content for supplementary hints or explanations while keeping click-based reveal order deterministic.
- [x] **SP-22**: A Markdown author can define sorting or reordering classroom exercises with a stable initial state, answer state, and playback reveal behavior.
- [x] **SP-23**: A Markdown author can request restrained body-step animation for selected content blocks while keeping preview, static review, and print-friendly output readable.

### Structured Layout and Delivery

- [x] **SP-24**: A Markdown author can request structured school-style layout intents such as timeline, card grid, gallery/compare, or process/SmartArt-like sections without writing raw HTML.
- [x] **SP-25**: The renderer can apply optional semantic icons and section-divider or section-cover display controls while preserving the established school identity system.
- [ ] **SP-26**: A presenter can generate a print/export-friendly review view where reveal and mask states are inspectable and presenter-local annotations are excluded or flattened deterministically.
- [ ] **SP-27**: The verification path covers v1.8 markup, classroom interactions, structured layouts, print/export review behavior, offline single-file boundaries, and fixed `16:9`/`4:3` slide-canvas stability.

## Future Requirements

Deferred to a later milestone. Tracked but not in the current roadmap.

### Presentation Distribution

- **SP-FUTURE-02**: Add hosted or password-gated sharing after offline single-file behavior, export review, and presenter-local controls are stable.
- **SP-FUTURE-03**: Add multi-device synchronization, remote control, or audience participation after local playback and annotation behavior are verified.
- **SP-FUTURE-04**: Reconsider PPTX, Keynote, or fully editable PowerPoint export only after the HTML renderer has stable print/export review artifacts.

## Out of Scope

Explicitly excluded from v1.8. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Replacing Markdown with freeform HTML slide editing | The `school-presentation` source of truth remains Markdown logical slides. |
| Saving presenter annotations back into source Markdown | v1.8 treats annotations as playback-local delivery state, not authored content. |
| Hosted collaboration, remote control, or audience sync | Local offline playback needs stable markup and export behavior before distribution features. |
| PPTX, Keynote, or editable PowerPoint generation | The accepted school-presentation path is HTML-first because earlier PPTX output quality was unstable. |
| Arbitrary animation builder or game-like interaction engine | v1.8 only adds deterministic classroom interactions that can be represented, verified, and reviewed. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SP-17 | Phase 14 | Complete |
| SP-18 | Phase 14 | Complete |
| SP-19 | Phase 14 | Complete |
| SP-20 | Phase 14 | Complete |
| SP-21 | Phase 15 | Complete |
| SP-22 | Phase 15 | Complete |
| SP-23 | Phase 15 | Complete |
| SP-24 | Phase 15 | Complete |
| SP-25 | Phase 15 | Complete |
| SP-26 | Phase 16 | Pending |
| SP-27 | Phase 16 | Pending |

**Coverage:**
- v1.8 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0

---
*Requirements defined: 2026-06-11 for v1.8 school-presentation continuation*
