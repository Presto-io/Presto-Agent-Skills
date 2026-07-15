# Phase 44: Verification Gate, Runtime Notes, and UAT - Context

**Gathered:** 2026-07-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 44 turns the completed `school-pptx` renderer into a discoverable, portable, and acceptance-gated skill. It owns the public `verify --workdir` workflow, dependency and structural evidence, the required negative cases, a concise canonical `SKILL.md` with deeper references, repository discoverability, six-runtime adapter notes, and persisted human PowerPoint/WPS visual UAT evidence. It does not reopen template geometry, Markdown syntax, pagination decisions, renderer object design, new layouts, animation, PDF export, or template marketplace support.

</domain>

<decisions>
## Implementation Decisions

### Public Verification Evidence Contract
- **D-01:** `school-pptx.sh verify --workdir <dir>` is the single public verification entry. It must run dependency readiness, deterministic example generation, template validation, canonical rendering, structural PPTX inspection, the Phase 43 regression aggregate, and Phase 44 negative cases.
- **D-02:** Verification writes only beneath the caller-provided workdir. Keep the rendered same-stem Markdown/PPTX in a clearly separated delivery area; keep JSON, Markdown evidence, diagnostics, mutated fixtures, and temporary files in a verification-owned evidence/work area. Never pollute the user's normal delivery root or repository source directories.
- **D-03:** Produce bounded machine-readable evidence plus a concise human-readable summary from the same observed operands. Evidence uses relative artifact names, hashes, counts, stable codes, gate order, and pass/fail status; it must not embed PPTX bytes, unbounded user text, tracebacks, secrets, or absolute user paths.
- **D-04:** The aggregate uses a fixed, ordered, unique registry with exact required/called equality and zero dynamic skips. Any required gate failure, missing evidence field, registry drift, or unexpected negative-case success makes the command exit non-zero.
- **D-05:** A successful verification is rerunnable in a fresh workdir and must not treat stale evidence as current. Failed runs remain inspectable inside the workdir but cannot be confused with accepted delivery.

### Dependencies, Negative Cases, and Transition Truth
- **D-06:** Dependency readiness reports the actual Python executable/version and import readiness for `python-pptx`, Pillow, lxml, and PyYAML. Pandoc is recorded as optional and does not fail verification unless a future exercised path actually uses it.
- **D-07:** Verification never installs packages, downloads fonts/media/templates, or mutates the user's environment. Missing required dependencies fail with stable bounded diagnostics and remediation text; optional dependency absence is recorded honestly.
- **D-08:** A fixed negative registry covers unknown theme, unknown layout, missing media, unsupported styling, unresolved review markers, and template/manifest mismatch. Each case asserts non-zero exit, expected stable diagnostic code, bounded output, no traceback, no unrelated file damage, and no false success wording.
- **D-09:** Template/manifest mismatch and other destructive fixtures operate only on isolated copies inside the workdir. The committed normalized template, manifest, fixture, and user input are never mutated by verification.
- **D-10:** Transition mode remains an observed enum (`none`, `preserved`, or `generated`). The current renderer records `none`; absence of transitions is valid and must not be upgraded into a warning or failure.

### Canonical Skill and Six Runtime Notes
- **D-11:** Create one concise `skills/school-pptx/SKILL.md` as the semantic source of truth. It contains trigger wording, required inputs, clarification questions, review-before-render workflow, public commands, clean outputs, safety boundaries, verification entry, and links to deeper references.
- **D-12:** Long Markdown rules, template ownership, renderer/pagination behavior, verification evidence fields, negative cases, UAT checklist, and troubleshooting live in `skills/school-pptx/references/`. The canonical entry must remain short enough to review and copy.
- **D-13:** Runtime differences stay only in the canonical `Runtime Adapter Notes`; do not create separate runtime-specific skill copies or inject private runtime syntax into the canonical workflow.
- **D-14:** Adapter notes explicitly cover Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent. Every row states skill-folder/support-file discovery, explicit script invocation fallback, Python/package prerequisites, external command behavior, executable/read/write permissions, sandbox/allowlist concerns, and verification workdir boundaries.
- **D-15:** OpenClaw and Hermes Agent are first-class required rows. Their exact loading path or automatic script discovery must be described conservatively and verified at installation rather than assumed.
- **D-16:** Update `README.md`, `skills/README.md`, and `docs/compatibility-matrix.md` for discoverability. Update `docs/directory-spec.md` only where the existing directory contract needs a school-pptx-specific clarification; preserve the repository rule that runtime notes live in canonical skills.
- **D-17:** Clarification questions cover missing school/course title, subtitle/term/author metadata, controlled theme, required media paths, unresolved review markers, and whether the Markdown has been finalized. Rendering does not begin while required facts or media remain unresolved.

### Manual Viewer UAT and Milestone Acceptance
- **D-18:** Automated OOXML reopen is necessary but cannot approve visual UAT. Before milestone acceptance, a human must open the canonical full fixture PPTX in at least one real compatible viewer: Microsoft PowerPoint or WPS Presentation.
- **D-19:** Persist UAT evidence with viewer name/version, operating system, fixture Markdown hash, PPTX hash, timestamp, tester, and per-check result. The planning artifact is milestone evidence; the skill reference provides a reusable checklist without shipping project-specific pass claims.
- **D-20:** The minimum checklist covers Chinese wrapping/orphans/overflow, contents and timeline balance, theme fonts/colors/decor/footer fidelity, bold/highlight rendering, contain images and editable missing-media placeholders, notes visibility, table/code editability, and group move/ungroup/edit behavior.
- **D-21:** A failed or blocked UAT item prevents milestone acceptance and becomes an explicit gap. Auto mode cannot approve, synthesize, or infer a human PASS. A second viewer is useful comparative evidence but not required by VER-10.

### Claude's Discretion
- Exact evidence filenames and the internal Python module split may follow existing repository patterns, provided the public command, fixed registry, bounded evidence, and workdir separation above remain stable.
- The human summary may be Markdown or another directly reviewable text format alongside JSON; prefer Markdown to match existing repository evidence.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Acceptance
- `.planning/ROADMAP.md` — Phase 44 goal, success criteria, and boundary.
- `.planning/REQUIREMENTS.md` — VER-04..VER-10 and SKILL-01, SKILL-02, SKILL-04..SKILL-06.
- `.planning/phases/43-editable-pptx-renderer-and-pagination/43-VERIFICATION.md` — verified renderer baseline, 21-gate evidence, residual viewer risks, and Phase 44 handoff.
- `.planning/phases/43-editable-pptx-renderer-and-pagination/43-UI-SPEC.md` § Visual acceptance handoff — mandatory manual viewer checks.

### Skill and Renderer Contracts
- `skills/school-pptx/references/markdown-contract.md` — accepted source syntax, validation, notes, media, and review-marker behavior.
- `skills/school-pptx/references/template-contract.md` — controlled theme, layouts, slots, and template-owned geometry/style contract.
- `skills/school-pptx/references/template-editing.md` — safe normalized-template editing and revalidation workflow.
- `skills/school-pptx/scripts/verify_pptx_renderer.py` — existing Phase 43 fixed aggregate and observed structural evidence.
- `skills/school-presentation/references/verification-contract.md` — repository precedent for a public `verify --workdir` workflow.

### Repository Portability Contract
- `AGENTS.md` — canonical skill authoring, safety, verification, and mandatory OpenClaw/Hermes coverage rules.
- `docs/directory-spec.md` — semantic source of truth and progressive-disclosure directory responsibilities.
- `docs/compatibility-matrix.md` — six-runtime constraints and conservative OpenClaw/Hermes guidance.
- `skills/tiaokedan/SKILL.md` — concise canonical workflow and six-runtime adapter-note precedent.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/school-pptx/scripts/school-pptx.sh`: stable public dispatcher already owns `example`, `validate`, `template-report`, and `render`; Phase 44 adds `verify` without changing existing command contracts.
- `skills/school-pptx/scripts/verify_pptx_renderer.py`: fixed 21-gate Phase 43 aggregate, OOXML/package inspection helpers, deterministic inventory, negative fault injection, raw evidence recomputation, and bounded error assertions.
- `skills/school-pptx/scripts/verify_template_manifest.py` and `template_report.py`: reusable template/manifest readiness checks.
- `skills/school-pptx/fixtures/school-pptx-full.md` and fixture media: canonical end-to-end input for example, render, structure, and UAT evidence.
- `skills/school-pptx/templates/standard-school.manifest.yaml` and `.pptx`: controlled theme pair; mismatch tests must use workdir copies.

### Established Patterns
- Public successful render roots contain exactly one same-stem Markdown/PPTX pair; verification artifacts belong outside delivery.
- Held no-follow descriptors, bounded ZIP/XML/media reads, stable allowlisted codes, no traceback, and old-target preservation are existing security boundaries.
- Pagination and typography are frozen before emission; Phase 44 verifies rather than reselects layout, geometry, fonts, or page counts.
- The repository keeps runtime-neutral semantics in one canonical `SKILL.md` and places runtime differences in its adapter-note section.

### Integration Points
- Add `verify` dispatch and help text to `school-pptx.sh`, with Phase 44 verification code remaining skill-local under `scripts/`.
- Add verification/UAT references and link them from the new canonical `SKILL.md`.
- Update repository indexes and compatibility documentation without adding runtime-specific adapter directories.
- Store manual acceptance evidence in the Phase 44 planning directory; do not publish it as part of user delivery.

</code_context>

<specifics>
## Specific Ideas

- Use the Phase 43 21-gate aggregate as a required structural layer rather than duplicating its assertions in prose.
- Preserve a visible, reviewable mapping from each Phase 44 requirement to an actually called gate or human UAT item.
- Treat real-viewer observations as human evidence with hashes and environment identity, not as a screenshot-only or agent-generated PASS.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within Phase 44 scope.

</deferred>

---

*Phase: 44-verification-gate-runtime-notes-and-uat*
*Context gathered: 2026-07-15*
