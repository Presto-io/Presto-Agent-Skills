---
phase: 25
plan: 01
name: regression-verification-and-documentation-index
type: execute
wave: 1
depends_on:
  - phase: 22
    provides: "package-level scheduling contract and deterministic fixture evidence"
  - phase: 23
    provides: "teaching-design-package entry, split jiaoan orchestration, and six-runtime adapter coverage"
  - phase: 24
    provides: "optional end-of-term composition, expected manifest states, and honest combined-output status"
files_modified:
  - .planning/phases/25-regression-verification-and-documentation-index/25-REGRESSION-CHECKS.md
  - .planning/phases/25-regression-verification-and-documentation-index/25-VERIFICATION.md
  - README.md
  - skills/README.md
  - docs/directory-spec.md
  - docs/compatibility-matrix.md
  - skills/teaching-design-package/SKILL.md
  - skills/jiaoan-jihua/SKILL.md
  - skills/jiaoan-shicao/SKILL.md
  - skills/end-of-term-teaching-materials/SKILL.md
autonomous: true
requirements:
  - TDP-09
  - TDP-14
  - TDP-15
  - TDP-16
must_haves:
  truths:
    - D-01 verify standalone public command contracts for jiaoan-jihua, jiaoan-shicao, and end-of-term-teaching-materials instead of relying only on documentation inspection.
    - D-02 use temporary output directories and explicit file paths; do not rely on hidden runtime discovery, current working directory side effects, or persistent generated artifacts.
    - D-03 include strict v1.10 --expected-typ checks for jiaoan-jihua and jiaoan-shicao where feasible.
    - D-04 verify teaching-design-package as a caller/composer of standalone skills, not as their replacement.
    - D-05 compare public command surfaces against script usage text and docs; record mismatches.
    - D-06 teaching-design-package.pdf may be passed only when an actual combined file exists after explicit merge or compile evidence.
    - D-07 missing selected split PDFs, missing merge tooling, missing end-of-term source data, unresolved review markers, and unavailable PDF compiler paths must produce explicit non-passed status evidence.
    - D-08 disabled optional end-of-term module is non-failing; enabled module blocks final readiness when review markers or module manifest review state are unresolved.
    - D-09 verify disabled, enabled, blocked-review, and merge-unavailable expected manifest states with JSON validation and targeted field checks.
    - D-10 unavailable local Typst/PDF tooling should produce explicit non-passed manifest status rather than silent success.
    - D-11 affected canonical skill entries must represent Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
    - D-12 OpenClaw and Hermes Agent coverage must include practical discovery, support-file, script-permission, writable-path, and fallback notes, not names only.
    - D-13 canonical workflow text must stay runtime-neutral; runtime-private syntax belongs only in adapter notes.
    - D-14 compatibility matrix should keep one canonical SKILL.md plus progressive disclosure as the recommended pattern and should not overstate unverified support.
    - D-15 teaching-design-package must be discoverable from README.md, skills/README.md, docs/directory-spec.md, and docs/compatibility-matrix.md.
    - D-16 documentation should preserve placement rules for SKILL.md, references, scripts, templates, shared references, and versioned test fixtures.
    - D-17 README and skills index should state that teaching-design-package composes jiaoan-jihua, jiaoan-shicao, and optional end-of-term-teaching-materials without replacing them.
    - D-18 documentation-index verification should include TDP-09, TDP-14, TDP-15, and TDP-16 traceability.
    - D-19 prefer a dedicated Phase 25 verification artifact that is easy to rerun and audit.
    - D-20 verification must leave no repository-dirty generated outputs.
    - D-21 execution evidence must show command exit status, files checked, manifest statuses asserted, runtime coverage checks, and documentation-index checks.
    - D-22 run whitespace and syntax safety checks before committing execution artifacts.
    - D-23 no external web research is needed.
    - D-24 record the SDK phase lookup mismatch if encountered; do not silently omit Phase 25.
    - D-25 if a regression check fails, do not opportunistically change unrelated skill behavior; record a verification gap or apply only explicitly planned narrow documentation-index corrections.
---

<objective>
Plan Phase 25 as the v1.11 regression verification and documentation-index gate. The execution phase must prove that `jiaoan-jihua`, `jiaoan-shicao`, and `end-of-term-teaching-materials` remain standalone public skills after `teaching-design-package` integration; verify package manifest/failure semantics remain honest; verify runtime adapter coverage for six supported runtimes; and ensure repository indexes make the package skill discoverable without weakening Markdown-first or directory-ownership guidance.
</objective>

<threat_model>
Primary risks are false readiness, public-command regressions, documentation drift, and runtime portability overclaiming. Block false readiness by asserting actual file evidence before any PDF `passed` status. Block command regressions with black-box public script checks and strict v1.10 fixture comparisons. Block documentation drift with explicit path and requirement traceability checks across README, skills index, directory spec, and compatibility matrix. Block portability overclaiming by requiring OpenClaw and Hermes Agent notes to mention discovery, support files, script permission, writable paths, and fallback behavior. No network, credentials, destructive git, or runtime wrapper generation is required.
</threat_model>

<tasks>

<task id="01" type="execute">
<title>Create the Phase 25 regression verification matrix artifact</title>
<read_first>
- .planning/phases/25-regression-verification-and-documentation-index/25-CONTEXT.md
- .planning/phases/25-regression-verification-and-documentation-index/25-RESEARCH.md
- .planning/ROADMAP.md
- .planning/REQUIREMENTS.md
- .planning/phases/22-scheduling-contract-and-fixture/22-VERIFICATION.md
- .planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-VERIFICATION.md
- .planning/phases/24-optional-end-of-term-module-and-package-outputs/24-VERIFICATION.md
</read_first>
<action>
Create `.planning/phases/25-regression-verification-and-documentation-index/25-REGRESSION-CHECKS.md` as the execution-owned verification matrix. It must group checks into `Standalone public commands`, `Package manifest semantics`, `Runtime adapter coverage`, `Documentation/index discoverability`, and `Repository cleanliness`. Include each command/check, expected exit status, expected output or status fields, temporary output location policy, and requirement/decision coverage. Do not implement a runnable script in plan-phase; execution may later convert this matrix into a phase-local script if useful.
</action>
<acceptance_criteria>
- `25-REGRESSION-CHECKS.md` exists in the Phase 25 directory.
- It contains headings for `Standalone public commands`, `Package manifest semantics`, `Runtime adapter coverage`, `Documentation/index discoverability`, and `Repository cleanliness`.
- It names TDP-09, TDP-14, TDP-15, and TDP-16.
- It states that generated outputs must use `mktemp -d` or explicit `/tmp` paths and must leave no repository-dirty generated artifacts.
- It records D-01 through D-25 coverage either directly or through a traceability table.
</acceptance_criteria>
</task>

<task id="02" type="execute">
<title>Verify standalone public command surfaces and v1.10 strict fixtures</title>
<read_first>
- skills/jiaoan-jihua/SKILL.md
- skills/jiaoan-jihua/references/format-and-rendering.md
- skills/jiaoan-jihua/scripts/jiaoan-jihua.sh
- skills/jiaoan-jihua/templates/jiaoan-jihua-full.md
- skills/jiaoan-shicao/SKILL.md
- skills/jiaoan-shicao/references/format-and-rendering.md
- skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
- skills/jiaoan-shicao/templates/jiaoan-shicao-full.md
- skills/end-of-term-teaching-materials/SKILL.md
- skills/end-of-term-teaching-materials/references/data-contract.md
- skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md
- skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh
- test/1.10/电气设备控制线路安装与调试授课计划.md
- test/1.10/电气设备控制线路安装与调试授课计划.typ
- test/1.10/电气设备控制线路安装与调试教案.md
- test/1.10/电气设备控制线路安装与调试教案.typ
</read_first>
<action>
Run black-box smoke checks for all documented standalone public commands. For `jiaoan-jihua`, verify `example`, `render`, `manifest`, `info`, and `version`; include strict `--expected-typ` rendering against `test/1.10/电气设备控制线路安装与调试授课计划.typ`. For `jiaoan-shicao`, verify `example`, `render`, `manifest`, `info`, and `version`; include strict `--expected-typ` rendering against `test/1.10/电气设备控制线路安装与调试教案.typ` and `--calendar-output` if using the example command. For `end-of-term-teaching-materials`, verify `example`, `validate`, `markdown`, `render`, `verify`, `manifest`, `info`, and `version` using existing sanitized fixture data and temporary workdirs. Compare command availability against each script's usage text and relevant SKILL.md script usage text. If a command fails, record the failed command, exit status, and exact artifact state in `25-VERIFICATION.md`; do not silently fix unrelated implementation behavior.
</action>
<acceptance_criteria>
- `bash -n skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` exits 0.
- `bash -n skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` exits 0.
- `bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh` exits 0.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh example --output <tmp>/jiaoan-jihua-full.md` exits 0.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render --input test/1.10/电气设备控制线路安装与调试授课计划.md --typ <tmp>/jiaoan-jihua.typ --expected-typ test/1.10/电气设备控制线路安装与调试授课计划.typ` exits 0.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh manifest`, `info`, and `version` each exit 0.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example --output <tmp>/jiaoan-shicao-full.md --calendar-output <tmp>/calendar.json` exits 0.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --input test/1.10/电气设备控制线路安装与调试教案.md --typ <tmp>/jiaoan-shicao.typ --expected-typ test/1.10/电气设备控制线路安装与调试教案.typ` exits 0.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh manifest`, `info`, and `version` each exit 0.
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh example --output <tmp>/end-of-term-source.json` exits 0.
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh validate --input <tmp>/end-of-term-source.json` exits 0.
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh markdown --input <tmp>/end-of-term-source.json --output <tmp>/end-of-term-full.md` exits 0.
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh render --input <tmp>/end-of-term-full.md --workdir <tmp>/end-of-term-output` exits 0.
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh verify --workdir <tmp>/end-of-term-output` exits 0 or records explicit expected non-final/PDF-tool status in `25-VERIFICATION.md`.
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh manifest`, `info`, and `version` each exit 0.
- `25-VERIFICATION.md` records every standalone command, exit status, and artifact path checked.
</acceptance_criteria>
</task>

<task id="03" type="execute">
<title>Verify teaching-design-package command composition and manifest failure semantics</title>
<read_first>
- skills/teaching-design-package/SKILL.md
- skills/teaching-design-package/references/format-and-orchestration.md
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/end-of-term-teaching-materials/references/fixtures/end-of-term-source.json
- skills/end-of-term-teaching-materials/references/fixtures/end-of-term-source-uncertain.json
- test/1.11/teaching-design-package/expected-manifest.json
- test/1.11/teaching-design-package/expected-end-of-term-disabled-manifest.json
- test/1.11/teaching-design-package/expected-end-of-term-enabled-manifest.json
- test/1.11/teaching-design-package/expected-end-of-term-blocked-review-manifest.json
- test/1.11/teaching-design-package/expected-combined-merge-unavailable-manifest.json
- .planning/phases/24-optional-end-of-term-module-and-package-outputs/24-VERIFICATION.md
</read_first>
<action>
Verify `teaching-design-package.sh` as a composer over the standalone skills. Run `example`, `plan-split`, `render-split`, `plan-end-of-term`, `render-end-of-term` where feasible without requiring external PDF tooling, `render-package`, `manifest`, `info`, and `version`. Validate all expected manifest fixture JSON files with `python3 -m json.tool`. Assert targeted status fields for disabled, enabled, blocked-review, and merge-unavailable paths. Confirm that `teaching-design-package.pdf` is never `passed` unless an actual combined PDF file exists. Confirm that enabled unresolved end-of-term review markers block final readiness and disabled end-of-term remains non-failing.
</action>
<acceptance_criteria>
- `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh` exits 0.
- `skills/teaching-design-package/scripts/teaching-design-package.sh example --output <tmp>/teaching-design-package-full.md` exits 0.
- `skills/teaching-design-package/scripts/teaching-design-package.sh plan-split --input <tmp>/teaching-design-package-full.md --out-dir <tmp>/tdp-split` exits 0 and writes `jiaoan-jihua-full.md` plus `jiaoan-shicao-full.md`.
- `skills/teaching-design-package/scripts/teaching-design-package.sh render-split --input <tmp>/teaching-design-package-full.md --out-dir <tmp>/tdp-render` exits 0 and writes `teaching-design-package-manifest.json`.
- `skills/teaching-design-package/scripts/teaching-design-package.sh manifest --input <tmp>/teaching-design-package-full.md --out-dir <tmp>/tdp-render` exits 0.
- `skills/teaching-design-package/scripts/teaching-design-package.sh info` exits 0.
- `skills/teaching-design-package/scripts/teaching-design-package.sh version` exits 0.
- `plan-end-of-term`, `render-end-of-term`, and `render-package` are each executed when local fixture prerequisites exist; if a command is expected to return non-passed status due to review markers, missing PDFs, missing compiler, or unavailable merge tooling, `25-VERIFICATION.md` records that expected status.
- `python3 -m json.tool` exits 0 for every `test/1.11/teaching-design-package/expected-*.json` file.
- Targeted checks find `disabled`, `blocked_review`, `merge_unavailable`, `final_ready`, and `combined_output` in expected manifests or generated manifests.
- No generated or expected manifest marks `combined_output.status` as `passed` unless `teaching-design-package.pdf` exists in the checked output directory.
</acceptance_criteria>
</task>

<task id="04" type="execute">
<title>Verify runtime adapter coverage and canonical portability boundaries</title>
<read_first>
- AGENTS.md
- docs/compatibility-matrix.md
- skills/teaching-design-package/SKILL.md
- skills/jiaoan-jihua/SKILL.md
- skills/jiaoan-shicao/SKILL.md
- skills/end-of-term-teaching-materials/SKILL.md
- docs/directory-spec.md
</read_first>
<action>
Check that affected skill entries represent Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent in supported-runtimes metadata or Runtime Adapter Notes. Verify OpenClaw and Hermes Agent notes mention practical support-file discovery, script execution permission, writable path or sandbox expectations, and fallback behavior when automatic script discovery is not verified. Scan canonical process sections for runtime-private syntax and move or flag any runtime-specific wording that belongs in adapter notes. If no fixes are required, record pass evidence in `25-VERIFICATION.md`.
</action>
<acceptance_criteria>
- `rg "Codex|Claude Code|Gemini CLI|OpenCode|OpenClaw|Hermes Agent" skills/teaching-design-package/SKILL.md skills/jiaoan-jihua/SKILL.md skills/jiaoan-shicao/SKILL.md skills/end-of-term-teaching-materials/SKILL.md` exits 0 and each file contains all six runtime names.
- `rg "OpenClaw|Hermes Agent|references/|templates/|scripts/|shell|permission|fallback|workdir|writable|sandbox|support" skills/teaching-design-package/SKILL.md skills/jiaoan-jihua/SKILL.md skills/jiaoan-shicao/SKILL.md skills/end-of-term-teaching-materials/SKILL.md` exits 0.
- Canonical `Process`, `Outputs`, `Verification`, and `Safety` sections in affected SKILL.md files do not require Claude-only, Codex-only, Gemini-only, OpenCode-only, OpenClaw-only, or Hermes-only private syntax outside Runtime Adapter Notes.
- `25-VERIFICATION.md` records any adapter wording updated or records `no changes required`.
</acceptance_criteria>
</task>

<task id="05" type="execute">
<title>Verify documentation/index discoverability and record Phase 25 evidence</title>
<read_first>
- README.md
- skills/README.md
- docs/directory-spec.md
- docs/compatibility-matrix.md
- docs/markdown-normalization-contract.md
- references/scheduling-contract.md
- .planning/REQUIREMENTS.md
- .planning/phases/25-regression-verification-and-documentation-index/25-REGRESSION-CHECKS.md
</read_first>
<action>
Verify that `teaching-design-package` is discoverable from `README.md`, `skills/README.md`, `docs/directory-spec.md`, and `docs/compatibility-matrix.md`, with paths or text that point to `skills/teaching-design-package/SKILL.md`, `references/format-and-orchestration.md`, `templates/teaching-design-package-full.md`, and `scripts/teaching-design-package.sh` where appropriate. Check that docs preserve Markdown-first, lightweight `SKILL.md`, long rules in `references/`, scripts in `scripts/`, templates in `templates/`, shared cross-skill contract in root `references/`, and deterministic fixture evidence under versioned `test/`. Add minimal index/documentation patches only if a discoverability or traceability gap is found. Write `.planning/phases/25-regression-verification-and-documentation-index/25-VERIFICATION.md` with command results, manifest status assertions, runtime coverage, documentation/index checks, repository cleanliness, and any recorded gaps.
</action>
<acceptance_criteria>
- `rg "teaching-design-package" README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md` exits 0.
- `rg "skills/teaching-design-package/SKILL.md|format-and-orchestration.md|teaching-design-package-full.md|teaching-design-package.sh" README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md skills/teaching-design-package/SKILL.md` exits 0.
- `rg "Markdown|SKILL.md|references/|scripts/|templates/|test/|references/scheduling-contract.md" README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md` exits 0.
- `25-VERIFICATION.md` exists in the Phase 25 directory.
- `25-VERIFICATION.md` contains sections for `Standalone command regression`, `Package manifest semantics`, `Runtime adapter coverage`, `Documentation/index discoverability`, `Repository cleanliness`, and `Gaps`.
- `git status --short` after deleting temporary workdirs shows only intentional Phase 25 execution artifacts and any explicit narrow documentation-index edits.
- `git diff --check` exits 0 before staging.
- `git diff --cached --check` exits 0 before committing.
</acceptance_criteria>
</task>

</tasks>

<verification>
At minimum, run these verification commands during Phase 25 execution and record outcomes in `25-VERIFICATION.md`:

```bash
bash -n skills/jiaoan-jihua/scripts/jiaoan-jihua.sh
bash -n skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh

tmpdir="$(mktemp -d)"
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh example --output "$tmpdir/jiaoan-jihua-full.md"
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render --input "test/1.10/电气设备控制线路安装与调试授课计划.md" --typ "$tmpdir/jiaoan-jihua.typ" --expected-typ "test/1.10/电气设备控制线路安装与调试授课计划.typ"
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh manifest
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh info
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh version

skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example --output "$tmpdir/jiaoan-shicao-full.md" --calendar-output "$tmpdir/calendar.json"
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --input "test/1.10/电气设备控制线路安装与调试教案.md" --typ "$tmpdir/jiaoan-shicao.typ" --expected-typ "test/1.10/电气设备控制线路安装与调试教案.typ"
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh manifest
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh info
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh version

skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh example --output "$tmpdir/end-of-term-source.json"
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh validate --input "$tmpdir/end-of-term-source.json"
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh markdown --input "$tmpdir/end-of-term-source.json" --output "$tmpdir/end-of-term-full.md"
mkdir -p "$tmpdir/end-of-term-output"
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh render --input "$tmpdir/end-of-term-full.md" --workdir "$tmpdir/end-of-term-output"
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh verify --workdir "$tmpdir/end-of-term-output"
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh manifest
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh info
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh version

skills/teaching-design-package/scripts/teaching-design-package.sh example --output "$tmpdir/teaching-design-package-full.md"
skills/teaching-design-package/scripts/teaching-design-package.sh plan-split --input "$tmpdir/teaching-design-package-full.md" --out-dir "$tmpdir/tdp-split"
skills/teaching-design-package/scripts/teaching-design-package.sh render-split --input "$tmpdir/teaching-design-package-full.md" --out-dir "$tmpdir/tdp-render"
skills/teaching-design-package/scripts/teaching-design-package.sh manifest --input "$tmpdir/teaching-design-package-full.md" --out-dir "$tmpdir/tdp-render"
skills/teaching-design-package/scripts/teaching-design-package.sh info
skills/teaching-design-package/scripts/teaching-design-package.sh version

python3 -m json.tool test/1.11/teaching-design-package/expected-manifest.json >/tmp/phase25-expected-manifest.json
python3 -m json.tool test/1.11/teaching-design-package/expected-end-of-term-disabled-manifest.json >/tmp/phase25-disabled-manifest.json
python3 -m json.tool test/1.11/teaching-design-package/expected-end-of-term-enabled-manifest.json >/tmp/phase25-enabled-manifest.json
python3 -m json.tool test/1.11/teaching-design-package/expected-end-of-term-blocked-review-manifest.json >/tmp/phase25-blocked-manifest.json
python3 -m json.tool test/1.11/teaching-design-package/expected-combined-merge-unavailable-manifest.json >/tmp/phase25-merge-unavailable-manifest.json

rg "Codex|Claude Code|Gemini CLI|OpenCode|OpenClaw|Hermes Agent" skills/teaching-design-package/SKILL.md skills/jiaoan-jihua/SKILL.md skills/jiaoan-shicao/SKILL.md skills/end-of-term-teaching-materials/SKILL.md
rg "teaching-design-package" README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md
rg "skills/teaching-design-package/SKILL.md|format-and-orchestration.md|teaching-design-package-full.md|teaching-design-package.sh" README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md skills/teaching-design-package/SKILL.md
git status --short
git diff --check
```

Before committing execution artifacts, stage only Phase 25 scope files and run:

```bash
git diff --cached --check
```

Do not run `/gsd:execute-phase 25` from this plan-phase command.
</verification>

<success_criteria>
- TDP-15 is proven by black-box public command checks for `jiaoan-jihua`, `jiaoan-shicao`, and `end-of-term-teaching-materials`.
- TDP-16 is proven by documentation/index discoverability checks for `teaching-design-package` and preserved directory guidance.
- TDP-09 remains protected by six-runtime adapter coverage and runtime-neutral canonical workflow text.
- TDP-14 remains protected by package manifest checks that reject false combined-PDF readiness.
- Phase 25 execution evidence is easy to rerun, records command results and status assertions, and leaves no untracked generated outputs in the repository.
</success_criteria>
