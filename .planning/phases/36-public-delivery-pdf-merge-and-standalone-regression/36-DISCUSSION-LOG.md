# Phase 36: Public Delivery, PDF Merge, and Standalone Regression - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-15
**Phase:** 36-Public Delivery, PDF Merge, and Standalone Regression
**Areas discussed:** Public delivery surface, PDF merge semantics, hidden evidence and failure behavior, standalone regression

---

## Public Delivery Surface

| Option | Description | Selected |
|--------|-------------|----------|
| Course-name `1 + 1 + N` | Public root contains only course-name-prefixed Markdown and PDFs; current N=2 gives four files. | ✓ |
| Keep v1.14 English filenames | Continue `teaching-design-package-full.md`, `.typ`, `teaching-design-package.pdf`, `teaching-plan.pdf`, `teaching-design.pdf` in public root. | |
| Dual public names | Emit both English and course-name filenames for compatibility. | |

**User's choice:** Course-name `1 + 1 + N`.
**Notes:** User explicitly locked the final public root to `课程名教学资料.md`, `课程名教学资料.pdf`, `课程名授课进度计划表.pdf`, and `课程名教学设计方案.pdf`; `.typ`, status, manifest, model, diagnostics, logs, calendar JSON, and module intermediates must not be public.

---

## PDF Merge Semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Merge only after all registered module PDFs pass | Check every registry module PDF exists and is non-empty, then merge in registry order. | ✓ |
| Compile unified Typst as final PDF | Treat a directly compiled unified Typst/PDF as the full package PDF. | |
| Merge whatever files exist | Best-effort merge available PDFs and record partial status. | |

**User's choice:** Merge only after all registered module PDFs pass.
**Notes:** User explicitly required all registered module PDFs to truly exist and be non-empty before `课程名教学资料.pdf` is created. Merge order is module registry order, currently `teaching-plan` then `teaching-design`.

---

## Hidden Evidence And Tool Honesty

| Option | Description | Selected |
|--------|-------------|----------|
| Record actual merge tool and hidden evidence | Status names the real tool (`pdfunite`, `qpdf`, or PyMuPDF fallback), inputs, order, and result. | ✓ |
| Abstract merge as passed/failed only | Status records only final boolean readiness. | |
| Expose status/manifest publicly | Put diagnostic status in public root for easier inspection. | |

**User's choice:** Record actual merge tool and hidden evidence.
**Notes:** User called out `pdfunite`、`qpdf`、`PyMuPDF` specifically and required status to be honest about which tool actually ran. All diagnostics/status/log/model/calendar evidence stays hidden.

---

## Failure Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Non-zero and no apparent public success | Any module or merge failure exits non-zero and cannot leave a successful-looking public directory. | ✓ |
| Preserve partial public files | Leave whatever generated successfully in public root and rely on status to explain failure. | |
| Exit zero with warnings | Treat missing merge or partial PDFs as warning-only when split PDFs exist. | |

**User's choice:** Non-zero and no apparent public success.
**Notes:** User explicitly required any module failure or merge failure to exit non-zero and not leave a public directory that appears successful. Context recommends staging/atomic publish or cleanup of expected public outputs before each run.

---

## Standalone Regression

| Option | Description | Selected |
|--------|-------------|----------|
| Copy only `teaching-design-package` skill folder | Verify normal render works from a standalone copy with skill-local calendar and no sibling skill dependency. | ✓ |
| Verify inside repository only | Run regression from the main repo workspace where sibling skills and tests are present. | |
| Depend on old jiaoan skills | Use `jiaoan-jihua` and `jiaoan-shicao` as runtime helpers. | |

**User's choice:** Copy only `teaching-design-package` skill folder.
**Notes:** Phase 33/34/35 completion facts are carried forward: shared scheduling model and calendar are skill-local; old `jiaoan-jihua` and `jiaoan-shicao` are not runtime dependencies.

---

## Claude's Discretion

- Planner may choose staging directory naming and exact atomic publish mechanism.
- Planner may choose merge tool priority among `pdfunite`, `qpdf`, and PyMuPDF fallback, as long as status records the actual tool.
- Planner may keep hidden unified Typst/PDF debug evidence if useful, but `.typ` and debug evidence cannot appear in successful public root.

## Deferred Ideas

- Future module expansion for N>2 belongs to a later phase or future requirement.
- A cross-skill PDF merge helper belongs later, after this package-specific contract is stable.
