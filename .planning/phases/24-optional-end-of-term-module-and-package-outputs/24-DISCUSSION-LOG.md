# Phase 24: Optional End-of-Term Module and Package Outputs - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-14
**Phase:** 24-Optional End-of-Term Module and Package Outputs
**Areas discussed:** Optional module attachment, Review gate preservation, Manifest/table/workbook discoverability, Split and combined outputs, Failure semantics and Phase 25 boundary

---

## Optional Module Attachment

| Option | Description | Selected |
|--------|-------------|----------|
| Optional module orchestrated through existing `end-of-term-teaching-materials` commands | Keep `end-of-term-teaching-materials` as source of truth; package points to `end-of-term-full.md` and module artifacts. | ✓ |
| Copy end-of-term scoring/table logic into `teaching-design-package` | Duplicates logic and risks drift from the existing skill. | |
| Make end-of-term required for every teaching-design package | Exceeds Phase 24 wording and blocks package use cases that only need jiaoan outputs. | |

**User's choice:** `[auto]` Selected optional module orchestrated through existing commands.
**Notes:** Conservatively preserves standalone skill ownership and stable public command surfaces.

---

## Review Gate Preservation

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve module-local `end-of-term-full.md` review gate and mirror status in package manifest | Keeps hard export rule `## 复核标记` exactly `无` before final output. | ✓ |
| Let the package-level review marker override module-local markers | Would bypass TDP-11 and weaken existing end-of-term safety. | |
| Treat abnormal review artifacts as acceptable final output | Conflicts with existing `artifact_kind: abnormal_review` and `final_ready: false` behavior. | |

**User's choice:** `[auto]` Selected preserve module-local review gate.
**Notes:** Normal final package readiness requires both package-level and enabled module-level gates to be clear.

---

## Manifest, Table, and Workbook Discoverability

| Option | Description | Selected |
|--------|-------------|----------|
| Add package manifest pointers to module-local manifest, table artifacts, calculated scores, and workbooks | Makes artifacts discoverable without flattening or re-owning module details. | ✓ |
| Copy all end-of-term artifact details into top-level package manifest | More verbose and likely to drift from module manifest fields. | |
| Only list `end-of-term-package.pdf` | Fails TDP-10/TDP-12 discoverability for deterministic tables and workbook output. | |

**User's choice:** `[auto]` Selected package manifest pointers to module-local evidence.
**Notes:** Required artifacts include score data, calculated score evidence, score summary, highlight evidence, score-list workbook, and scorebook workbook.

---

## Split and Combined Outputs

| Option | Description | Selected |
|--------|-------------|----------|
| Plan split module PDFs plus default combined `teaching-design-package.pdf` with explicit merge/compile evidence | Satisfies TDP-12/TDP-13 while preserving honest status behavior. | ✓ |
| Deliver split PDFs only by default | Does not satisfy TDP-13 unless later explicitly accepted. | |
| Claim combined output from Typst generation alone | Violates Phase 23 PDF-status precedent and TDP-14. | |

**User's choice:** `[auto]` Selected split module PDFs plus default combined output with explicit evidence.
**Notes:** `end-of-term-package.pdf` joins `teaching-plan.pdf` and `lesson-plans.pdf` when enabled; `teaching-design-package.pdf` is passed only if the file exists after an explicit merge/compile step.

---

## Failure Semantics and Phase 25 Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Record explicit package/module statuses for unavailable tooling, failed validation, unresolved review, and missing outputs | Produces auditable failure evidence without overstating readiness. | ✓ |
| Treat missing tooling as a warning while marking final package ready | Conflicts with TDP-14. | |
| Expand Phase 24 into full regression/documentation verification | Belongs to Phase 25 except for narrow checks needed by implementation. | |

**User's choice:** `[auto]` Selected explicit status evidence and Phase 25 boundary.
**Notes:** Suggested statuses include `disabled`, `planned`, `not_run`, `passed`, `failed`, `missing_compiler`, `merge_unavailable`, and `blocked_review`.

---

## Claude's Discretion

- Keep Phase 24 focused on optional-module integration and package-output semantics.
- Extend existing `teaching-design-package` files conservatively rather than refactoring existing end-of-term internals.
- Prefer truthfully incomplete manifest/status evidence over false final package success.
- Treat `.planning/ROADMAP.md` and `.planning/STATE.md` as authoritative for Phase 24 despite `gsd-sdk query init.phase-op 24` returning `phase_found: false` in this session.

## Deferred Ideas

- Phase 25 owns broad regression verification for existing public skill command surfaces.
- Phase 25 owns full documentation/index verification unless Phase 24 implementation requires targeted immediate doc updates.
- Hosted/cloud review, arbitrary template discovery, OCR, and uncontrolled spreadsheet ingestion remain out of scope.
