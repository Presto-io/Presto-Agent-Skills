# Phase 44: Verification Gate, Runtime Notes, and UAT - Research

**Researched:** 2026-07-15
**Mode:** implementation / ecosystem
**Confidence:** High for repository-local architecture; Medium for runtime installation-path details that must be checked in each installed runtime

## Research Summary

Phase 44 should be implemented as a thin public orchestration layer around the already verified Phase 41–43 commands and evidence, not as a second renderer. The stable public entry remains:

```bash
skills/school-pptx/scripts/school-pptx.sh verify --workdir <dir>
```

The implementation should add one skill-local verification orchestrator, preserve the Phase 43 fixed 21-gate aggregate as a called sub-gate, publish bounded JSON and Markdown from the same observations, add six isolated negative fixtures, and leave visual approval to a human PowerPoint/WPS checkpoint. Documentation work should create one concise canonical `SKILL.md`, move long rules into skill-local references, and add discoverability without creating runtime-specific skill copies.

The principal planning risk is false-green evidence. The verifier must prove its fixed registries were actually called in order, recompute its aggregate from raw outcomes, reject missing schema fields, and never infer a manual UAT PASS. Two concrete implementation gaps must be handled explicitly: unresolved review markers do not yet have a stable public validator code, and template/manifest mismatch currently surfaces report failures mainly as human text rather than one normalized negative-case code.

## Requirement-to-Implementation Map

| Requirement | Required implementation/evidence |
|---|---|
| VER-04 | Public `verify --workdir` dispatcher; fixed top-level registry; isolated example, template, render, structural, regression, and negative execution. |
| VER-05 | Dependency gate records sanitized executable identity, Python implementation/version, required import versions/readiness for `pptx` (python-pptx), `PIL` (Pillow), `lxml`, `yaml` (PyYAML), and optional Pandoc status; it never installs or downloads. |
| VER-06 | Canonical evidence includes logical and physical counts, ordered layout mapping, complete logical-to-physical mapping, contents source entries and reopened contents text/counts. |
| VER-07 | Structural evidence includes exact notes indices/count, media relationships and zero-crop/native picture observations, native table counts/header structure, editable code textbox/run text hashes, editable groups, and a full-slide-picture shortcut count of zero. |
| VER-08 | Fixed six-case negative registry with isolated copies, non-zero exits, exact stable codes, bounded output, no traceback/false success, and before/after unrelated-file hashes. |
| VER-09 | Evidence enum is exactly `none`, `preserved`, or `generated`; current canonical result is observed `none`, which passes. |
| VER-10 | Persist a human-owned Phase 44 UAT artifact with real viewer identity, hashes, environment, tester, timestamp, per-item observations, and explicit pending/blocked/passed state. Automated execution may prepare inputs or lint completeness but may not set PASS. |
| SKILL-01 | Add concise `skills/school-pptx/SKILL.md` containing trigger, inputs, review-before-render workflow, public commands, outputs, safety, verification, and links. |
| SKILL-02 | Add long verification/UAT and renderer/workflow references; link existing Markdown/template references rather than duplicating them. |
| SKILL-04 | One six-row `Runtime Adapter Notes` table in the canonical skill; every row covers whole-folder discovery, explicit script fallback, dependencies, external commands, permissions/sandbox, and workdir writes. |
| SKILL-05 | Add `school-pptx` to `README.md`, `skills/README.md`, and `docs/compatibility-matrix.md`; update `docs/directory-spec.md` only with a useful school-pptx ownership row, not a new general schema. |
| SKILL-06 | Canonical workflow asks only for missing school/course title, subtitle/term/author metadata, controlled theme, required media, unresolved review markers, and finalized-review state before rendering. |

## Standard Stack

Use the repository’s existing stack:

- Bash dispatcher: `skills/school-pptx/scripts/school-pptx.sh`.
- Python standard library for orchestration, subprocesses, hashing, JSON, bounded file handling, temporary/staging directories, and OOXML ZIP/XML inspection.
- Existing skill-local code: `markdown_contract.py`, `template_report.py`, `pptx_render.py`, `verify_pptx_renderer.py` and its safe package/inventory helpers.
- Runtime dependencies already exercised by the renderer: `python-pptx`, Pillow, lxml, and PyYAML. Pandoc is observational/optional because the current path does not exercise it.
- Markdown as the human-readable evidence and UAT medium; JSON as the machine-readable evidence.

Do not introduce a test framework, package installer, network client, runtime shim generator, second PPTX parser, or PDF/screenshot-based acceptance path. The repository already has sufficient structural primitives.

## Recommended File and Module Split

### Implementation

| File | Responsibility |
|---|---|
| `skills/school-pptx/scripts/school-pptx.sh` | Add literal `verify --workdir <dir>` help and dispatch; keep all existing command contracts unchanged. |
| `skills/school-pptx/scripts/verify_school_pptx.py` | New Phase 44 public orchestrator: argument validation, owned workdir layout, fixed registries, subprocess capture, evidence normalization, aggregate status, JSON/Markdown publication, bounded failures. |
| `skills/school-pptx/scripts/verify_pptx_renderer.py` | Remain the Phase 43 regression authority. Prefer importing/calling a stable `run_phase_43()` or invoking the script as a bounded subprocess; do not duplicate its 21 gate bodies. Small helper extraction is acceptable only if behavior stays covered. |
| `skills/school-pptx/scripts/markdown_contract.py` | Add stable unresolved-review-marker rejection used by both validate/render and the Phase 44 negative case. Recommended code: `REVIEW_MARKER_UNRESOLVED`. Recognize only the project’s documented markers, not arbitrary braces. |
| `skills/school-pptx/scripts/template_report.py` or the new verifier adapter | Normalize an isolated template/manifest mismatch to one stable negative-case code, recommended `TEMPLATE_MANIFEST_MISMATCH`, while retaining bounded details in evidence. Do not change canonical report success semantics. |

### Documentation

| File | Responsibility |
|---|---|
| `skills/school-pptx/SKILL.md` | Concise semantic entry and six-runtime notes. |
| `skills/school-pptx/references/verification-contract.md` | Public verify contract, workdir layout, gate/negative registries, evidence schema, status/exit rules, dependency behavior, troubleshooting. |
| `skills/school-pptx/references/renderer-and-pagination.md` | Concise long-form renderer behavior if existing Markdown/template references do not cover it; link Phase 41–43 contracts rather than copying implementation detail. |
| `skills/school-pptx/references/visual-uat.md` | Reusable viewer checklist and instructions; must not contain project-specific PASS claims. |
| `.planning/phases/44-verification-gate-runtime-notes-and-uat/44-UAT.md` | Milestone-specific human evidence, initially `pending`; only a real tester may enter observations and PASS. |
| `README.md`, `skills/README.md`, `docs/compatibility-matrix.md` | Discoverability and portability. |
| `docs/directory-spec.md` | Add ownership rows only if useful; no new runtime adapter folder or universal evidence schema. |

Do not place reusable docs in `templates/`; do not create six copies of the skill; do not publish planning UAT evidence inside user delivery.

## Architecture Patterns

### 1. Public verification is orchestration, not rendering logic

The top-level verifier should call the same public `example`, `template-report`, and `render` paths a user invokes, then inspect their outputs independently. Phase 43’s aggregate is a mandatory regression layer. This catches dispatcher/path/publication regressions that direct Python calls would miss.

### 2. Verification owns a namespaced work tree

Recommended caller workdir layout:

```text
<workdir>/
├── delivery/
│   ├── school-pptx-full.md
│   └── school-pptx-full.pptx
├── evidence/
│   ├── verification.json
│   ├── verification.md
│   └── runs/<run-id>/failure-summary.json   # only when retaining a failed run
└── work/
    └── <run-id>/
        ├── example/
        ├── template/
        ├── canonical/
        └── negatives/<case-id>/
```

All paths in evidence are relative to `<workdir>`. Build the current run in a unique command-owned staging directory, then publish current evidence atomically. A new run must overwrite/update the current status from new observations; it must not read an old `verification.json` as proof. Unrelated caller files are preserved and hashed sentinels should prove this. A failed run writes `status: failed` evidence and retains bounded diagnostics, so no earlier PASS can be mistaken for the current run.

If implementation chooses a smaller layout, it must still keep delivery separate from evidence/work, preserve caller files, and distinguish fresh current evidence from retained failures.

### 3. Fixed top-level gate registry

Use this exact conceptual order (names may be finalized once, then frozen):

1. `dependency-readiness`
2. `example-generation`
3. `template-validation`
4. `canonical-render`
5. `structural-inspection`
6. `phase-43-regression`
7. `negative-cases`
8. `evidence-integrity`

Keep both an ordered tuple and an independently declared required set. At completion assert:

- ordered tuple is unique;
- set(tuple) equals required set;
- `called` exactly equals ordered tuple;
- `dynamic_skips == 0`;
- every required gate has a result object and `status`;
- aggregate PASS is recomputed from gate outcomes, not accepted from a stored boolean.

`evidence-integrity` should validate the in-memory evidence candidate before publication: schema fields, bounded strings/lists/counts, relative paths, hashes, transition enum, registry equality, requirement coverage, and absence of traceback/absolute paths. It must not validate a stale evidence file.

### 4. Fixed negative registry

Use one ordered registry with exactly these six cases:

| Case ID | Mutation | Expected public code |
|---|---|---|
| `unknown-theme` | Copy canonical Markdown and replace controlled theme | `THEME_UNKNOWN` |
| `unknown-layout` | Copy canonical Markdown and use unsupported layout | `LAYOUT_UNKNOWN` |
| `missing-media` | Copy Markdown into an isolated directory without its referenced media, or alter one reference | `MEDIA_MISSING` |
| `unsupported-styling` | Add a forbidden style/font/color/coordinate attribute outside code fences | `UNSUPPORTED_STYLE` |
| `unresolved-review-marker` | Add a documented unresolved marker such as `{{待补充: ...}}` or `{{AI草稿: ...}}` | new stable `REVIEW_MARKER_UNRESOLVED` |
| `template-manifest-mismatch` | Copy template and manifest into the case directory, mutate one mapped geometry/placeholder fact, then run report against both copies | normalized `TEMPLATE_MANIFEST_MISMATCH` |

Each case records and asserts: `exit_code != 0`, exact expected/observed code equality, output byte count below a fixed bound (prefer the existing 8 KiB public-failure bound), `traceback_present == false`, `false_success_present == false`, unchanged sentinel hashes, and no writes outside its case directory. For render negatives, best-effort editable pair output is allowed where already contractual, but evidence must call it failed. Template mismatch must never touch committed template/manifest bytes.

Do not generate the registry dynamically from discovered files or skip a case because an optional dependency is absent. Missing required dependencies make verification fail before case execution; they do not create skips.

### 5. Evidence is an observed projection

Recommended bounded JSON shape:

```json
{
  "schema_version": 1,
  "status": "passed|failed",
  "run": {"id": "bounded-id", "started_at": "ISO-8601", "finished_at": "ISO-8601"},
  "registry": {"required": [], "called": [], "unique": true, "dynamic_skips": 0},
  "dependencies": {},
  "canonical": {
    "artifacts": [{"path": "delivery/name.pptx", "sha256": "...", "bytes": 1}],
    "logical_slides": 13,
    "physical_slides": 32,
    "layout_mapping": [],
    "logical_to_physical": [],
    "contents": {},
    "structure": {},
    "transition_mode": "none"
  },
  "phase_43": {"status": "passed", "registry": {}},
  "negatives": [],
  "requirements": {},
  "manual_uat": {"status": "pending", "evidence_path": "planning artifact, not auto-approved"},
  "diagnostics": []
}
```

The Markdown summary must be rendered from this in-memory object, not separately reasoned. Bound every diagnostic message and collection, and include only stable codes, counts, hashes, relative paths, and short remediation. Never embed PPTX bytes, raw unbounded Markdown, tracebacks, secrets, or absolute user paths.

For dependency evidence, reconcile “actual executable” with the no-absolute-path rule by recording a sanitized executable identity (basename or `<external>/python3`), Python implementation/version, and import/module versions. Record how it was selected (`SCHOOL_PPTX_PYTHON` or default) without recording a home-directory path. Pandoc should be `{required: false, available: bool, version: bounded|null}` and must not affect PASS while unused.

### 6. Structural inspection reuses and strengthens Phase 43 evidence

Phase 43 already proves the key baseline: 13 logical → 32 physical slides, 11 controlled layouts plus implicit closing behavior, native tables, editable groups, 10 image relationships, 9 notes slides, editable code, no whole-slide picture, and transition `none`. Phase 44 should expose these as public evidence and independently bind them to the freshly rendered `delivery/*.pptx` hash.

Minimum structural evidence:

- source Markdown SHA-256 and output PPTX SHA-256/size;
- logical count, physical count, ordered physical layout part mapping;
- complete logical index → physical indices mapping;
- source contents entries and reopened contents text/count;
- expected and observed notes slide indices;
- image relationship count, embedded media hashes if available, and zero-crop observations;
- native table page count, each table’s row/column/header evidence;
- code source/frozen/reopened hashes and native textbox/run properties;
- native group count and editable timeline/gallery object counts;
- `whole_slide_picture_count: 0` based on geometry, not filename;
- observed transition enum.

Do not merely copy the Phase 43 JSON. Bind all public claims to the fresh canonical artifact, and retain the 21-gate `required == called` evidence as a separate regression result.

## Validation Architecture

Validation should be layered so failures identify the contract boundary:

### Layer A — Static and CLI contract

- Python compile/import of the new verifier.
- `school-pptx.sh --help` contains the literal verify usage.
- Missing `--workdir`, non-directory collisions, symlink/path escapes, and unwritable workdirs fail bounded and non-zero.
- Dispatcher passes the selected Python interpreter without installing anything.

### Layer B — Dependency readiness

- Required imports: `pptx`, `PIL`, `lxml`, `yaml`; record versions and fail on any missing import with one stable code such as `VERIFY_DEPENDENCY_MISSING` plus bounded remediation.
- Python executable/version is observed and sanitized.
- Pandoc is observed with a short timeout and remains optional while unused.
- Add a fault-injection test proving a required import failure cannot be reported as PASS.

### Layer C — Fresh public happy path

- In a fresh temporary caller workdir, run the public verify command twice in separate fresh roots.
- Assert success, exact gate order, fixed registry equality, zero skips, bounded stdout/stderr, and no traceback.
- Assert delivery contains only the canonical same-stem Markdown/PPTX pair.
- Assert evidence/work stay outside delivery and all evidence paths are relative.
- Compare deterministic semantic fields and artifact hashes where the renderer is byte-stable; explicitly exclude run timestamps/ids from determinism comparisons.

### Layer D — Structural and evidence integrity

- Reopen the exact PPTX named and hashed by public evidence.
- Recompute critical counts/mappings/hashes independently and compare them to evidence.
- Assert transition enum membership and accept observed `none`.
- Assert JSON and Markdown status/gate counts agree because Markdown derives from JSON observations.
- Mutation tests must prove hardcoded `status: passed`, missing gate results, absolute paths, oversized diagnostics, reordered/duplicate registries, and constant structural counts fail the integrity gate.

### Layer E — Negative isolation

- Execute all six fixed cases, each in a dedicated copied fixture tree.
- Snapshot committed canonical assets and caller sentinel before/after.
- Assert exact stable codes, non-zero exits, output bound, no traceback, no success language, no out-of-case writes, and fixed registry equality.
- Run template mismatch only against copies and assert original template/manifest hashes remain unchanged.

### Layer F — Phase 43 regression

- Run the existing fixed 21-gate Phase 43 aggregate in the supported dependency environment.
- Assert its `required == called`, order, uniqueness, and `dynamic_skips=0` rather than accepting exit code alone.
- Preserve the existing 13 → 32 canonical baseline unless a future phase explicitly changes the fixture/contract.

### Layer G — Documentation and portability

- Check canonical `SKILL.md` frontmatter and trigger-oriented description.
- Check all linked references/scripts/templates exist.
- Check exactly six runtime rows and required coverage terms (support files, explicit invocation, Python/packages, external command behavior, execute/read/write, sandbox/allowlist, workdir).
- Check OpenClaw and Hermes rows use installation-time verification language for uncertain discovery paths.
- Check README/index/matrix entries point to the same canonical skill folder.
- Check runtime-private syntax occurs only in adapter notes, not the main workflow.

### Layer H — Manual viewer checkpoint

Automation prepares canonical fixture/PPTX hashes and a blank/pending UAT form. It may validate that a human-completed form has all required fields, but it must not fill viewer observations, tester identity, timestamp, or PASS. Execution stops at `UAT PENDING` until a person opens the hashed deck in PowerPoint or WPS and records results. Any failed/blocked item becomes a Phase 44 or milestone gap.

## Manual Viewer UAT Design

Create `.planning/phases/44-verification-gate-runtime-notes-and-uat/44-UAT.md` initially with frontmatter similar to:

```yaml
phase: 44-verification-gate-runtime-notes-and-uat
status: pending
viewer: ""
viewer_version: ""
operating_system: ""
fixture_sha256: ""
pptx_sha256: ""
tested_at: ""
tester: ""
```

The body should identify the exact relative evidence source and contain per-item `PENDING/PASS/FAIL/BLOCKED`, observation, and optional screenshot/reference columns. Required observations:

1. Chinese wrapping, orphan lines, and visible overflow across long-content pages.
2. Contents-page and timeline-page visual balance.
3. Theme fonts, colors, decorations, and footer fidelity.
4. Bold and highlight rendering.
5. Contain images plus editable missing-media placeholders.
6. Speaker notes visibility in the viewer’s notes surface and absence from slide canvas.
7. Native table and code text editability.
8. Timeline/gallery group move, ungroup, regroup, and member editing.

Acceptance rule: all required items PASS in at least Microsoft PowerPoint or WPS Presentation; viewer/version, OS, hashes, timestamp, and tester are non-empty; hashes match the verified canonical artifacts. A second viewer is optional comparative evidence. Screenshots alone are insufficient because edit/group/notes operations must be observed. Auto mode must report `UAT PENDING` and stop; it cannot convert structural evidence into a visual PASS.

## Runtime Adapter Notes Guidance

Use one compact table in `skills/school-pptx/SKILL.md`. Each row should cover the same seven dimensions: discovery/whole-folder install, support-file paths, explicit script fallback, Python/package prerequisites, external command execution, read/write/execute permissions and sandbox/allowlist, and `verify --workdir` ownership.

Prescriptive row content:

- **Codex:** point project context to canonical skill/`AGENTS.md` when auto-discovery is unavailable; preserve whole folder; explicitly invoke shell; verify shell/Python execution and caller workdir access.
- **Claude Code:** install whole folder under a supported Claude skill path such as `.claude/skills/school-pptx/`; preserve progressive disclosure; check tool allowlist and script execution.
- **Gemini CLI:** use `GEMINI.md`/project context as discovery bridge; explicitly read canonical skill and invoke script when no native auto-discovery; verify permissions.
- **OpenCode:** use the installed version’s native skill path or documented Claude-compatible fallback; test selection and whole-folder preservation before claiming support.
- **OpenClaw:** use an AgentSkills-compatible folder only when supported; installation-time check frontmatter parser, skill root, sandbox sync, third-party code review, support-file visibility, allowlist, Python packages, script executable bit, and workdir writes. Do not assume automatic script discovery.
- **Hermes Agent:** installation-time verify exact project/global loading path, whole-folder support-file discovery, Python/external command permissions, executable/read/write access, sandbox boundaries, and explicit invocation fallback. Do not claim an untested automatic discovery path.

Runtime-specific path/syntax belongs only in this adapter table. The main workflow must say simply to run the public command.

## Canonical Skill Content Budget

The entry should remain comparable in scale to `skills/tiaokedan/SKILL.md`, but can be shorter by linking references. Recommended sections:

1. frontmatter with precise “use when” description and six supported runtimes;
2. Objective / Use When;
3. Inputs and progressive-disclosure references;
4. Review-before-render workflow;
5. Missing Information Questions;
6. literal public commands (`example`, `validate`, `template-report`, `render`, `verify`);
7. Outputs and clean delivery boundary;
8. Runtime Adapter Notes;
9. short Verification and Safety sections.

Long syntax tables, 11-layout rules, template geometry, 21/8/6 gate registries, evidence fields, UAT procedure, and troubleshooting stay in references.

## Don't Hand-Roll

- Do not implement a second renderer or paginator in the verifier.
- Do not parse OOXML without the existing bounded ZIP/XML helpers and relationship limits.
- Do not use screenshots, PDF export, or visual AI as a substitute for PowerPoint/WPS UAT.
- Do not create runtime-specific copies, adapters directories, generated wrappers, or runtime-private syntax in the canonical body.
- Do not install packages, download media/fonts/templates, or modify environment configuration.
- Do not mutate committed template, manifest, fixture, or user input during negative testing.
- Do not use exit code alone as proof; validate called registries and raw evidence.
- Do not treat old evidence as current, and do not leave a prior PASS visible as the latest result after a failed rerun.
- Do not record absolute home paths, PPTX bytes, unbounded subprocess output, traceback, or full user content in evidence.

## Common Pitfalls

1. **Wrapping Phase 43 without binding fresh artifacts.** A passing 21-gate aggregate is necessary but does not prove the public verify-created PPTX is the inspected file. Bind paths and hashes.
2. **Dynamic negative discovery.** File-based discovery can silently skip a deleted fixture. Freeze registry names in code and prove exact called equality.
3. **Natural-language diagnostic assertions.** Template-report currently emits useful Chinese failures, but negative evidence needs a stable code independent of wording.
4. **Review marker false negative.** Existing validator coverage includes unsupported style/theme/layout/media but no documented stable unresolved-marker code; add it to the shared validate/render path, not only the test harness.
5. **Dependency import-name confusion.** The distributions and imports differ: python-pptx → `pptx`, Pillow → `PIL`, PyYAML → `yaml`. Record both logical package and actual imported version.
6. **Absolute-path leakage.** `sys.executable`, subprocess errors, and temp paths can reveal user home directories. Normalize before evidence publication.
7. **Stale PASS after failure.** Publish a current failed evidence record before returning non-zero, or atomically replace a current pointer/status so old success cannot be mistaken as current.
8. **Optional Pandoc becoming a gate.** It is informative while unused; absence must not fail v1.17.
9. **Transition absence treated as degradation.** `none` is a valid observed enum and current expected behavior.
10. **Auto-approved UAT.** OOXML reopen, screenshots, or code assertions do not establish real viewer wrapping, visual balance, or editing ergonomics.
11. **Bloated canonical entry.** Copying all authoring/verification/UAT rules into `SKILL.md` violates progressive disclosure and makes runtime portability harder to review.
12. **Unverified OpenClaw/Hermes claims.** State installation-time checks conservatively; exact paths and automatic script discovery vary by installed version.

## Suggested Plan Boundaries

For downstream planning, use dependency-ordered vertical slices rather than one documentation-only closeout:

1. **Public verifier foundation:** dispatcher, workdir ownership, dependency gate, fixed top-level registry, evidence schema/writers, fresh-run/stale-evidence safety.
2. **Canonical and negative verification:** public example/template/render, fresh structural inspection, Phase 43 aggregate integration, six fixed isolated negatives, review-marker and template-mismatch stable codes, mutation/fault tests.
3. **Canonical skill and portability docs:** concise `SKILL.md`, verification/renderer/UAT references, six runtime notes, README/index/matrix/directory discoverability checks.
4. **Human UAT checkpoint and closeout:** generate canonical evidence and pending UAT form; stop for a real PowerPoint/WPS tester; after human evidence is supplied, validate hashes/completeness, record failures as gaps, then perform final requirement traceability.

Plan 4 cannot be auto-completed merely because Plans 1–3 pass. If the execution environment has no human viewer interaction, the correct end state is implementation/automated verification complete with VER-10 and milestone acceptance pending.

## Code Examples

Fixed registry pattern:

```python
VERIFY_GATE_ORDER = (
    "dependency-readiness",
    "example-generation",
    "template-validation",
    "canonical-render",
    "structural-inspection",
    "phase-43-regression",
    "negative-cases",
    "evidence-integrity",
)
VERIFY_REQUIRED_GATES = frozenset(VERIFY_GATE_ORDER)

assert len(VERIFY_GATE_ORDER) == len(set(VERIFY_GATE_ORDER))
assert set(VERIFY_GATE_ORDER) == VERIFY_REQUIRED_GATES
# execute every item, append to called only after invocation
assert tuple(called) == VERIFY_GATE_ORDER
```

Aggregate status must be derived:

```python
status = "passed" if (
    tuple(called) == VERIFY_GATE_ORDER
    and all(results[name]["status"] == "passed" for name in VERIFY_GATE_ORDER[:-1])
    and all(case["status"] == "passed" for case in negatives)
) else "failed"
```

The real implementation should avoid self-reference when evaluating `evidence-integrity`: integrity validates the candidate’s prior observed gates and then contributes its own result before final status is recomputed.

## Open Questions Resolved for Planning

- **Must verify call render directly or through Python?** Through the public shell commands for public-contract gates; direct helpers are acceptable only for independent recomputation.
- **Can Phase 43’s aggregate be replaced?** No. Call it as a required regression layer and expose its registry evidence.
- **Does Pandoc absence fail?** No, while no exercised path uses it.
- **Does transition `none` fail?** No.
- **Can invalid render produce a PPTX?** Yes, the existing bounded editable best-effort pair is compatible, but the negative case remains failed and exits non-zero.
- **Can automation sign UAT?** No. It may prepare and lint evidence only.
- **Are OpenClaw/Hermes optional?** No. Both require full rows, with uncertain discovery/path behavior labeled for installation-time verification.

## Confidence Assessment

- **High:** public dispatcher integration, Phase 43 aggregate reuse, workdir/evidence boundaries, fixed registries, structural coverage, requirement mapping, documentation placement, and manual-UAT non-automation rule. These are directly supported by repository code and locked Phase 44 decisions.
- **High:** existing canonical baseline of 13 logical / 32 physical slides and 21 Phase 43 gates, based on the passed Phase 43 verification report and source registry.
- **Medium:** exact OpenClaw and Hermes skill loading paths or auto-discovery, intentionally because project policy requires installation-time validation rather than assumptions.
- **Medium:** final stable string chosen for template/manifest mismatch and review markers. The research recommends codes, but implementation must freeze and test them consistently before documenting them as public contract.

## Sources Consulted

- `.planning/phases/44-verification-gate-runtime-notes-and-uat/44-CONTEXT.md`
- `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `.planning/ROADMAP.md`
- `.planning/phases/43-editable-pptx-renderer-and-pagination/43-VERIFICATION.md`
- `.planning/phases/43-editable-pptx-renderer-and-pagination/43-UI-SPEC.md`
- `skills/school-pptx/scripts/school-pptx.sh`
- `skills/school-pptx/scripts/verify_pptx_renderer.py`
- `skills/school-presentation/references/verification-contract.md`
- `skills/school-pptx/scripts/markdown_contract.py`, `template_report.py`, and existing school-pptx references
- `docs/directory-spec.md`, `docs/compatibility-matrix.md`
- `skills/tiaokedan/SKILL.md`
- `README.md`, `skills/README.md`, `AGENTS.md`

---

*Research complete. This document informs planning only and does not claim manual viewer UAT completion.*
