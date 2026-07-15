---
gsd_state_version: 1.0
milestone: v1.17
milestone_name: school-pptx
status: Awaiting next milestone
stopped_at: v1.17 shipped and archived; awaiting next milestone
last_updated: "2026-07-16T05:30:00+08:00"
last_activity: 2026-07-16 — Milestone v1.17 completed, archived, and prepared for tagging
progress:
  total_phases: 4
  completed_phases: 4
  total_plans: 19
  completed_plans: 19
  percent: 100
---

# State: Presto Agent Skills

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-07-16)

**Core value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.
**Current focus:** Promote backlog Phase 999.1 into the next milestone

## Current Position

Phase: Milestone v1.17 complete
Plan: —
Status: Awaiting next milestone
Last activity: 2026-07-16 — Milestone v1.17 completed and archived

## Workflow Preferences

- Mode: YOLO
- Granularity: Coarse
- Execution: Parallel
- Research: Yes
- Plan Check: Yes
- Verifier: Yes
- UI phase hints: Yes

## Latest Shipped Milestone

v1.17 shipped `school-pptx`, a Markdown-first skill that turns structured logical slides into editable, template-consistent `.pptx` output with automated verification and human UAT.

Phase order:

- Phase 41: Standard template and manifest
- Phase 42: Markdown contract and full fixture
- Phase 43: Editable PPTX renderer and pagination
- Phase 44: Verification gate, runtime notes, and UAT

## Accumulated Context

### Decisions

- [v1.17]: Phase numbering continues after v1.16; this milestone starts at Phase 41 and ends at Phase 44.
- [v1.17]: Requirements coverage is limited to current v1.17 requirements only.
- [v1.17]: Build order follows research: hand-normalized standard template, hand-authored Markdown fixture/contract, renderer, then verification/runtime/UAT gate.
- [v1.17]: `school-pptx` is a new PPTX skill line, not a reopening of `school-presentation` HTML output.
- [Phase 41]: `standard-school` is the first controlled PPTX theme and is backed by a skill-local `.pptx`, YAML manifest, and `template-report` evidence command.
- [Phase 42]: Public Markdown exposes 10 authorable layouts; the manifest-owned `closing` remains exactly one implicit final page.
- [Phase 42]: Phase 43 consumes the source-located logical document model instead of reparsing Markdown.
- [Phase 42]: Validation aggregates bounded diagnostics and remains non-zero when safe missing-media fallback metadata is retained.
- [Phase 42]: All ten YAML formatter values must resolve to string scalars before entering the logical model.
- [Phase 42]: Fixed example output is published only through held no-follow directory descriptors; missing capabilities fail closed.
- [Phase 42]: `fixture-example` owns an explicit five-gap registry plus the secure-I/O capability companion.
- [Phase 43]: Dynamic table, gallery, and timeline objects derive every geometry and text budget from manifest subregions and presets.
- [Phase 43]: Physical pagination decisions are frozen, JSON-projectable values that the later PPTX emitter cannot mutate.
- [Phase 43]: CJK measurement uses deterministic grapheme-aware East Asian width fallback without CWD font discovery or PowerPoint autofit.
- [Phase 43]: All semantic splitting and structured balancing complete before PPTX emission and produce immutable physical plans. — This keeps emitter behavior deterministic and prevents PPTX object creation from changing pagination.
- [Phase 43]: PPTX emission consumes only the frozen PhysicalDeckPlan and never reruns pagination. — This keeps object generation deterministic and preserves the reviewed physical mapping.
- [Phase 43]: Transition mode is explicitly none for v1.17 emission. — Unstable viewer-specific transitions remain out of scope and absence is a valid PPTX-12 outcome.
- [Phase 43]: Render imports canonical parse_document in-process and publishes only the reviewed Markdown plus validated PPTX. — Avoids parser drift and public logical-model sidecars.
- [Phase 43]: Markdown-first and PPTX-last are individually atomic publications; PPTX is the deck-ready commit point. — Two independent files cannot form one cross-file transaction, so the crash window stays explicit and tested.
- [Phase 43]: Structurally valid best-effort decks remain editable and visually unpolluted while render exits non-zero and names affected logical slides. — Artifact existence must not be confused with successful rendering.
- [Phase 43]: Staged PPTX save and validation remain bound to duplicated streams for one held O_RDWR inode; path names are used only for identity checks and descriptor-relative replace.
- [Phase 43]: Public object failures expose only allowlisted stable codes and generic remediation; unknown object errors collapse to PPTX_OBJECT_INVALID.
- [Phase 43]: Code body text uses a delimiter-agnostic one-run monospace helper; optional code subheadings remain separate rich-text shapes.
- [Phase 43]: Multiple frozen code fragments on one physical slide are reconstructed only at their existing source-line boundary before literal emission.
- [Phase 43]: Two-column target slots, cover slot values, visible contents numbering, and native table row heights are immutable plan fields consumed mechanically by the emitter.
- [Phase 43]: Table content height is derived only from `table.height - table_name.height`; measured rows use ceil-to-EMU bounds and repeated headers retain one frozen height.
- [Phase 43]: Public template-report preflights all ZIP metadata, then chunk-reads bounded XML before parsing or relationship use. — This closes production reader drift while keeping public failures stable and bounded.
- [Phase 43]: Every non-code body slot uses one mixed-fragment textbox; code fragments are direct monospace runs while ordinary fragments retain native rich-text styles.
- [Phase 43]: Header-only tables are valid one-page native tables with exactly one frozen row and positive row height.
- [Phase 43]: Pillow bomb and format/decode failures cross the public boundary only through precise allowlisted codes and bounded generic diagnostics.
- [Phase 43]: Phase 43 aggregate has a fixed 21-gate order with exact required/called equality, zero dynamic skips, raw-evidence recomputation, and AST mutation guards against false-green producer constants.
- [Phase 43]: Mixed body pagination and native emission share frozen 24pt/22pt target-slot typography and controlled spacing. — This prevents successful PPTX output from silently clipping code measured at a smaller size.
- [Phase 43]: Media validation and `add_picture` consume one bounded descriptor-read payload, closing the media TOCTOU window; the 21-gate aggregate verifies capacity vectors and source-derived producer evidence.
- [Phase 43]: Paginator and emitter consume one frozen paragraph sequence, so headings, paragraphs, list items, code runs, line spacing, and paragraph spacing share one full-frame capacity contract.
- [Phase 43]: Contents freeze 26pt typography and dedicated code freezes 14pt typography; both public render and reopened PPTX evidence block successful clipping or font drift.
- [Phase 43]: The fixed 21-gate aggregate recomputes equality from raw text/media/projection/target hashes and rejects constant producer evidence through AST mutation guards.
- [Phase 44]: Public verification owns one fixed eight-gate authority and publishes current JSON/Markdown evidence from the same bounded observed projection.
- [Phase 44]: Plan 44-01 reserves later gates as explicit `NOT_IMPLEMENTED` failures; foundation completion cannot produce a false public PASS.
- [Phase 44]: Required Python imports are observed fresh while Pandoc remains optional and never changes gate readiness while unused.
- [Phase 44]: Public verify executes exact fixed registries of 8 top-level gates, 6 negative cases, and the reused 21-gate Phase 43 authority with required/called equality and zero dynamic skips.
- [Phase 44]: Fresh canonical evidence is SHA-256-bound to the reopened 13-logical/32-physical delivery; structural claims are recomputed from OOXML and native editable objects.
- [Phase 44]: Negative mutations remain inside per-case copied trees and must fail non-zero with exact stable codes, bounded output, unchanged canonical hashes, and no false-success evidence.
- [Phase 44]: One concise canonical `school-pptx/SKILL.md` owns the runtime-neutral workflow; renderer, verification, and UAT detail remains in progressive references.
- [Phase 44]: Documentation integrity is part of the public evidence-integrity gate and checks the canonical entry, fixed 8/6/21 contracts, six runtime rows, and repository discovery links.
- [Phase 44]: OpenClaw and Hermes Agent support remains installation-time verified with explicit script fallback; no untested automatic discovery path is claimed.
- [Phase 44]: The final human acceptance is bound to canonical PPTX SHA-256 `ed99daa1b7a187a2adb57f9769c1ecf282bc48ad950309cfbef3805a8f9af963` and verification run `76d62c9155092a76`; Mrered passed all 10 checks in WPS Presentation 12.1.26035 on macOS 26.5.2.

### Pending Todos

None yet.

### Blockers/Concerns

None. v1.17 is shipped; Phase 999.1 is the next milestone candidate.

## Performance Metrics

| Phase-Plan | Duration | Tasks | Files |
|------------|----------|-------|-------|
| 42-01 | 47 min | 3 | 4 |
| Phase 42 P02 | 11min | 3 tasks | 8 files |
| 42-03 | 22 min | 3 | 3 |
| Phase 43 P01 | 6 min | 3 tasks | 6 files |
| Phase 43 P02 | 12 min | 3 tasks | 2 files |
| Phase 43 P03 | 14 min | 3 tasks | 4 files |
| Phase 43 P04 | 19 min | 3 tasks | 3 files |
| Phase 43 P05 | 20 min | 2 tasks | 3 files |
| Phase 43 P06 | 29 min | 2 tasks | 3 files |
| Phase 43 P07 | 16 min | 3 tasks | 8 files |
| Phase 43 P08 | 18 min | 2 tasks | 3 files |
| Phase 43 P09 | 27 min | 3 tasks | 4 files |
| Phase 43 P10 | 25 min | 3 tasks | 5 files |
| Phase 43 P11 | 55 min | 3 tasks | 5 files |
| Phase 44 P01 | 47 min | 3 tasks | 5 files |
| Phase 44 P02 | 37 min | 3 tasks | 6 files |
| Phase 44 P03 | 17 min | 3 tasks | 9 files |
| Phase 44 P04 | human UAT | 10 checks | 4 planning files |

## Deferred Items

None.

## Session Continuity

Last session: 2026-07-16T05:30:00+08:00
Stopped at: v1.17 shipped and archived; awaiting next milestone
Resume file: None

## Operator Next Steps

- Promote Phase 999.1 with `$gsd-review-backlog`.
- Start the resulting milestone with `/gsd:new-milestone`.
