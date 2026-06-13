# Phase 25: Regression Verification and Documentation Index - Context

**Gathered:** 2026-06-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 25 is the v1.11 regression and documentation-index gate. It must verify that the new `teaching-design-package` integration did not break the existing standalone public command surfaces for `jiaoan-jihua`, `jiaoan-shicao`, or `end-of-term-teaching-materials`; that package failure and manifest behavior remains honest; that runtime adapter coverage still includes Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent; and that repository indexes make the new skill discoverable while preserving Markdown-first and directory-ownership guidance.

This phase must not implement feature fixes, change public interfaces, or add new package capabilities. If verification finds a regression, Phase 25 should record it as a gap for planning/execution rather than silently fixing it during discussion. The implementation phase may add regression tests, verification scripts, or documentation-index adjustments, but those choices belong to later `/gsd:plan-phase 25` and `/gsd:execute-phase 25` work.

**Auto-mode note:** The user authorized `/gsd:discuss-phase 25 --auto` and explicitly requested no large-direction questions. All gray areas were auto-selected and resolved conservatively from roadmap, requirements, Phase 22/23/24 artifacts, current skill entries, scripts, and documentation indexes.

**Tooling note:** `gsd-sdk query init.phase-op 25` returned `phase_found: false` even though `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, and `.planning/STATE.md` identify Phase 25 as planned/ready. This discussion treats ROADMAP/REQUIREMENTS/STATE as authoritative and records the SDK mismatch for downstream awareness.

</domain>

<decisions>
## Implementation Decisions

### Public Command Regression Scope

- **D-01:** Phase 25 should verify the existing standalone commands as public contracts, not merely inspect docs. Required coverage includes `jiaoan-jihua.sh example`, `jiaoan-jihua.sh render`, `jiaoan-jihua.sh manifest`, `jiaoan-jihua.sh info`, `jiaoan-jihua.sh version`; `jiaoan-shicao.sh example`, `jiaoan-shicao.sh render`, `jiaoan-shicao.sh manifest`, `jiaoan-shicao.sh info`, `jiaoan-shicao.sh version`; and `end-of-term-teaching-materials.sh example`, `validate`, `markdown`, `render`, `verify`, `manifest`, `info`, `version`.
- **D-02:** Regression checks should use temporary output directories and explicit file paths. Do not rely on hidden runtime discovery, current working directory side effects, or persistent build artifacts.
- **D-03:** Existing jiaoan v1.10 strict fixture behavior remains a high-value regression gate. Planner should include strict `--expected-typ` checks against the committed v1.10 fixtures if feasible within the execution budget.
- **D-04:** The integrated package helper should be verified as a caller/composer of standalone skills, not as a replacement. Required commands include `teaching-design-package.sh example`, `plan-split`, `render-split`, `plan-end-of-term`, `render-end-of-term` where feasible, `render-package`, `manifest`, `info`, and `version`.
- **D-05:** Public command surfaces should be compared against docs and script usage text. If a command exists in docs but not in the script, or vice versa, Phase 25 should capture that as a documentation/interface mismatch.

### Package Failure and Manifest Behavior

- **D-06:** Manifest truthfulness is the core TDP-14 regression. `teaching-design-package.pdf` may be marked `passed` only when the actual combined file exists after explicit merge/compile evidence; Typst output alone is not enough.
- **D-07:** Missing selected split PDFs, missing merge tooling, missing end-of-term source data, unresolved review markers, and unavailable PDF compiler paths should produce explicit manifest/status evidence such as `failed`, `merge_unavailable`, `planned`, `not_run`, `missing_compiler`, or `blocked_review`.
- **D-08:** Disabled optional end-of-term module must remain non-failing. Enabled end-of-term module must block final readiness when `end-of-term-full.md` contains unresolved `## 复核标记`, when module `manifest.json` has `review_cleared: false`, or when required module artifacts are absent.
- **D-09:** Phase 25 should verify the Phase 24 expected-manifest fixtures for disabled, enabled, blocked-review, and merge-unavailable states using JSON validation plus targeted status-field checks.
- **D-10:** If local Typst/PDF tooling is unavailable, the correct result is an explicit non-passed manifest status, not a skipped silent success. Verification should assert the status semantics rather than require PDF tool availability.

### Runtime Adapter Coverage

- **D-11:** Every affected canonical skill entry must keep Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent represented in `Runtime Adapter Notes` or supported-runtimes metadata. Affected entries are `skills/teaching-design-package/SKILL.md`, `skills/jiaoan-jihua/SKILL.md`, `skills/jiaoan-shicao/SKILL.md`, and `skills/end-of-term-teaching-materials/SKILL.md`.
- **D-12:** OpenClaw and Hermes Agent are mandatory runtime targets, so Phase 25 should verify they are not only present as names but also have practical notes for skill-folder discovery, support-file discovery, shell/script execution permission, writable path/sandbox expectations, and fallback behavior when automatic script discovery is not verified.
- **D-13:** Canonical workflow text should remain runtime-neutral. Runtime-private syntax, one-runtime-only tool names, or generated-wrapper assumptions should be treated as documentation defects unless confined to adapter notes.
- **D-14:** The compatibility matrix should continue to present one canonical `SKILL.md` plus progressive disclosure as the recommended pattern and should identify `teaching-design-package` runtime expectations without overstating unverified support.

### Documentation and Index Discoverability

- **D-15:** Phase 25 should verify that `teaching-design-package` is discoverable from `README.md`, `skills/README.md`, `docs/directory-spec.md`, and `docs/compatibility-matrix.md`. The docs should point readers to `skills/teaching-design-package/SKILL.md`, `references/format-and-orchestration.md`, `templates/teaching-design-package-full.md`, and `scripts/teaching-design-package.sh`.
- **D-16:** Documentation should preserve the repository placement rules: lightweight `SKILL.md`, long rules in `references/`, helper commands in `scripts/`, templates in `templates/`, shared cross-skill contract in root `references/`, and deterministic fixture evidence under versioned `test/`.
- **D-17:** README and skills index should make clear that `teaching-design-package` composes `jiaoan-jihua`, `jiaoan-shicao`, and optional `end-of-term-teaching-materials` without deleting, renaming, or replacing them.
- **D-18:** Documentation-index verification should include TDP-09/TDP-14/TDP-15/TDP-16 traceability, not only keyword presence. A future verifier should be able to see which requirement each check proves.

### Verification Artifact Shape

- **D-19:** Prefer a dedicated Phase 25 verification artifact that is easy to rerun and audit. Acceptable shapes include a focused shell script under a phase-appropriate location or a documented command matrix in `25-VERIFICATION.md`; planner should choose the least invasive option that fits repository conventions.
- **D-20:** Verification should leave no repository-dirty generated outputs. Temporary files should go under `/tmp` or another explicit temp directory, and generated caches should not be committed.
- **D-21:** Phase 25 execution should produce a summary and verification evidence showing command exit status, files checked, manifest statuses asserted, runtime coverage checks, and documentation-index checks.
- **D-22:** Run whitespace/syntax safety checks before committing execution artifacts. The discuss command itself must run `git diff --cached --check` before its context commit.

### Assumptions and Open Points for Planning

- **D-23:** Assume no external web research is needed. The phase is driven by local repo artifacts, public scripts, docs, and phase verification evidence.
- **D-24:** Because `gsd-sdk query init.phase-op 25` did not resolve Phase 25 in this session, planning should either verify the SDK mismatch or proceed from ROADMAP/REQUIREMENTS/STATE while recording the mismatch. It should not silently omit Phase 25.
- **D-25:** If a regression check fails during execution, the executor should not opportunistically change unrelated skill behavior. It should either implement the planned fix when the plan explicitly covers it or record a verification gap for a focused follow-up.

### Claude's Discretion

- Use conservative verification breadth: smoke public commands, strict fixtures where they already exist, targeted manifest status assertions, and documentation-index grep/structure checks.
- Prefer black-box command checks over internal rewrites. Phase 25 should prove the system still works from the outside.
- Keep any documentation edits small and index-focused. Do not rewrite long skill guidance unless verification shows a specific discoverability or traceability defect.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Requirements

- `.planning/ROADMAP.md` — Defines Phase 25 as regression verification and documentation index for TDP-09, TDP-14, TDP-15, and TDP-16.
- `.planning/REQUIREMENTS.md` — Locks the remaining active requirements and traceability for Phase 25.
- `.planning/PROJECT.md` — Captures v1.11 current state, active requirement, package discipline, runtime constraints, and milestone goals.
- `.planning/STATE.md` — Records Phase 25 as ready to discuss and lists accumulated v1.11 decisions.
- `AGENTS.md` — Repository language, editing, skill authoring, OpenClaw/Hermes, and GSD workflow rules.

### Prior Phase Evidence

- `.planning/phases/22-scheduling-contract-and-fixture/22-CONTEXT.md` — Locked scheduling contract and review-marker decisions.
- `.planning/phases/22-scheduling-contract-and-fixture/22-SUMMARY.md` — Delivered scheduling contract and fixture evidence.
- `.planning/phases/22-scheduling-contract-and-fixture/22-VERIFICATION.md` — Passed TDP-01 through TDP-04 checks.
- `.planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-CONTEXT.md` — Locked package entry, Markdown checkpoint, jiaoan composition, split output, and runtime-adapter decisions.
- `.planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-SUMMARY.md` — Delivered `teaching-design-package` files and Phase 23 verification commands.
- `.planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-VERIFICATION.md` — Passed TDP-05 through TDP-09 checks.
- `.planning/phases/24-optional-end-of-term-module-and-package-outputs/24-CONTEXT.md` — Locked optional end-of-term, combined-output, manifest, and failure-semantics decisions.
- `.planning/phases/24-optional-end-of-term-module-and-package-outputs/24-SUMMARY.md` — Delivered optional module and manifest fixture states.
- `.planning/phases/24-optional-end-of-term-module-and-package-outputs/24-VERIFICATION.md` — Passed TDP-10 through TDP-14 checks and explicitly deferred broad regression to Phase 25.

### Affected Skill Entries and Scripts

- `skills/teaching-design-package/SKILL.md` — Integrated package entry, adapter notes, outputs, verification, and safety boundaries.
- `skills/teaching-design-package/references/format-and-orchestration.md` — Long contract for package orchestration, optional end-of-term behavior, manifest/status semantics, and TDP traceability.
- `skills/teaching-design-package/templates/teaching-design-package-full.md` — Package Markdown checkpoint used by package helper commands.
- `skills/teaching-design-package/scripts/teaching-design-package.sh` — Public package helper commands and manifest writer.
- `skills/jiaoan-jihua/SKILL.md` — Standalone teaching-plan public skill contract and adapter notes.
- `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md` — Standalone teaching-plan Markdown intermediate.
- `skills/jiaoan-jihua/references/format-and-rendering.md` — Detailed teaching-plan format and verification rules.
- `skills/jiaoan-jihua/references/calendar.json` — Calendar support resource for scheduling-related verification.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` — Public command surface for example, render, manifest, info, and version.
- `skills/jiaoan-shicao/SKILL.md` — Standalone practical lesson-plan public skill contract and adapter notes.
- `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md` — Standalone practical lesson-plan Markdown intermediate.
- `skills/jiaoan-shicao/references/format-and-rendering.md` — Detailed practical lesson-plan format and verification rules.
- `skills/jiaoan-shicao/references/calendar.json` — Calendar support resource and copy target.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` — Public command surface for example, render, manifest, info, and version.
- `skills/end-of-term-teaching-materials/SKILL.md` — Standalone end-of-term module public skill contract and adapter notes.
- `skills/end-of-term-teaching-materials/references/data-contract.md` — Structured source-data contract.
- `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md` — Review gate, deterministic artifacts, workbook, manifest, and verification rules.
- `skills/end-of-term-teaching-materials/templates/end-of-term-full.md` — End-of-term Markdown checkpoint that must not be bypassed.
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh` — Public command surface for example, validate, markdown, render, verify, manifest, info, and version.
- `skills/end-of-term-teaching-materials/scripts/render_package.py` and `skills/end-of-term-teaching-materials/scripts/end_of_term/` — Module internals that own scoring, table artifacts, workbook generation, and verification.

### Fixtures and Expected Manifest States

- `test/1.10/电气设备控制线路安装与调试授课计划.md` — Existing jiaoan-jihua strict fixture source.
- `test/1.10/电气设备控制线路安装与调试授课计划.typ` — Existing jiaoan-jihua strict fixture target for post-generation comparison.
- `test/1.10/电气设备控制线路安装与调试教案.md` — Existing jiaoan-shicao strict fixture source.
- `test/1.10/电气设备控制线路安装与调试教案.typ` — Existing jiaoan-shicao strict fixture target for post-generation comparison.
- `test/1.11/teaching-design-package/expected-manifest.json` — Base package manifest expectation.
- `test/1.11/teaching-design-package/expected-end-of-term-disabled-manifest.json` — Optional module disabled state expectation.
- `test/1.11/teaching-design-package/expected-end-of-term-enabled-manifest.json` — Optional module enabled state expectation.
- `test/1.11/teaching-design-package/expected-end-of-term-blocked-review-manifest.json` — Blocked-review state expectation.
- `test/1.11/teaching-design-package/expected-combined-merge-unavailable-manifest.json` — Merge-unavailable combined-output expectation.
- `skills/end-of-term-teaching-materials/references/fixtures/end-of-term-source.json` — Normal end-of-term fixture source.
- `skills/end-of-term-teaching-materials/references/fixtures/end-of-term-source-uncertain.json` — Uncertain-score fixture source for blocked-review behavior.

### Documentation and Indexes

- `README.md` — Contributor-facing repository entry and existing skills index.
- `skills/README.md` — Skill index and artifact-contract discovery table.
- `docs/directory-spec.md` — Directory placement rules for skill entries, references, scripts, templates, shared references, and versioned fixtures.
- `docs/compatibility-matrix.md` — Runtime compatibility matrix and teaching-design-package runtime notes.
- `docs/markdown-normalization-contract.md` — Shared Markdown-first workflow contract that Phase 25 documentation checks should preserve.
- `references/scheduling-contract.md` — Shared v1.11 scheduling contract that package docs should keep discoverable.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `skills/teaching-design-package/scripts/teaching-design-package.sh`: Already exposes `example`, `plan-split`, `render-split`, `plan-end-of-term`, `render-end-of-term`, `render-package`, `manifest`, `info`, and `version`; it writes `teaching-design-package-manifest.json` with split output, end-of-term, combined output, review marker, and `final_ready` fields.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`: Existing shell-only public renderer for teaching-plan Markdown to Typst, with `--expected-typ` comparison support.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`: Existing shell-only public renderer for practical lesson-plan Markdown to Typst, with `--calendar-output` and `--expected-typ` support.
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`: Existing wrapper over Python module internals for structured data, Markdown, render, verify, and manifest behavior.
- `test/1.11/teaching-design-package/expected-*.json`: Existing deterministic manifest expectations that can anchor Phase 25 status assertions.

### Established Patterns

- Public scripts are the stable black-box surface. Phase 25 should test from the outside and avoid implementation-specific assumptions unless they are already documented as public contracts.
- Markdown-first checkpoints are mandatory before rendering or final output claims.
- Long workflow details live in `references/`; `SKILL.md` stays a concise semantic entry with runtime adapter notes.
- Runtime compatibility is documented as required support plus installation-time verification where behavior is not locally proven.
- Review markers and manifest fields are the honest-status mechanism; do not silently convert unresolved data into successful final readiness.

### Integration Points

- Phase 25 can connect prior phase verification evidence to a broader regression matrix covering standalone skills and the new package skill.
- Documentation-index checks should connect `README.md`, `skills/README.md`, `docs/directory-spec.md`, and `docs/compatibility-matrix.md` to the affected skill files and artifact contracts.
- If the planner chooses to add a reusable verification script, it should stay scoped to regression/documentation verification and avoid changing runtime behavior.

</code_context>

<specifics>
## Specific Ideas

- A useful Phase 25 verification matrix would have four groups: standalone command smoke, package manifest failure semantics, runtime adapter coverage, and documentation/index discoverability.
- The quickest high-signal command smoke should create example Markdown/JSON under `/tmp`, render generated Typst where scripts support it, validate JSON manifests with `python3 -m json.tool`, and assert expected status strings with `rg`.
- OpenClaw and Hermes checks should be specific enough to catch token-only coverage: look for support-file discovery and shell/script permission language, not just the runtime names.
- If `render-end-of-term` cannot produce a PDF because Typst is unavailable or review markers block export, the expected Phase 25 behavior is to verify the explicit blocked/missing status, not to require local PDF tooling.

</specifics>

<deferred>
## Deferred Ideas

- Implementing any newly discovered regression fix belongs to Phase 25 plan/execute, not this discuss command.
- Reworking `gsd-sdk query init.phase-op` phase lookup belongs to a separate GSD/tooling maintenance task unless Phase 25 planning explicitly includes a narrow documentation note.
- New runtime wrappers, generated adapters, hosted review workflows, OCR/template discovery, and cloud collaboration remain out of scope.

</deferred>

---

*Phase: 25-Regression Verification and Documentation Index*
*Context gathered: 2026-06-14*
