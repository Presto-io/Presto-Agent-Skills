---
phase: 24
plan: 01
name: optional-end-of-term-module-and-package-outputs
type: execute
wave: 1
depends_on:
  - phase: 22
    provides: "package-level scheduling contract and fixture evidence"
  - phase: 23
    provides: "teaching-design-package skill entry, package checkpoint, split jiaoan outputs, and honest manifest status"
files_modified:
  - skills/teaching-design-package/SKILL.md
  - skills/teaching-design-package/references/format-and-orchestration.md
  - skills/teaching-design-package/templates/teaching-design-package-full.md
  - skills/teaching-design-package/scripts/teaching-design-package.sh
  - test/1.11/teaching-design-package/fixture-source.md
  - test/1.11/teaching-design-package/expected-manifest.json
  - test/1.11/teaching-design-package/expected-review.md
  - test/1.11/teaching-design-package/expected-end-of-term-disabled-manifest.json
  - test/1.11/teaching-design-package/expected-end-of-term-enabled-manifest.json
  - test/1.11/teaching-design-package/expected-end-of-term-blocked-review-manifest.json
  - test/1.11/teaching-design-package/expected-combined-merge-unavailable-manifest.json
autonomous: true
requirements:
  - TDP-10
  - TDP-11
  - TDP-12
  - TDP-13
  - TDP-14
must_haves:
  truths:
    - D-01 model end-of-term materials as an optional module inside teaching-design-package, with an explicit enabled switch and manifest status.
    - D-02 reuse skills/end-of-term-teaching-materials public commands instead of copying score, table, workbook, or review logic into the package skill.
    - D-03 keep end-of-term-full.md as the module handoff and review checkpoint.
    - D-04 disabled end-of-term module must be explicit in the package manifest and must not make missing end-of-term artifacts fail the package.
    - D-05 preserve the module-local hard export rule that ## 复核标记 in end-of-term-full.md must be exactly 无 before final export.
    - D-06 uncertain scores, missing fields, and AI-drafted analysis content must keep the existing one-item-at-a-time teacher-review pattern.
    - D-07 render --abnormal-review remains non-final and must preserve artifact_kind abnormal_review, final_ready false, and review_cleared false.
    - D-08 final readiness requires package-level and enabled module-level review markers to be clear.
    - D-09 package manifest includes enabled end-of-term paths and statuses for end-of-term-full.md, end-of-term-package.typ, end-of-term-package.pdf, module manifest, tables, calculated score evidence, and workbooks.
    - D-10 keep table and workbook evidence owned by the end-of-term module and expose package-level pointers instead of flattening all data.
    - D-11 derive package final_ready from selected outputs and module manifest flags including review_cleared, calculated_scores_verified, table_artifacts_verified, workbook_verified, and PDF status.
    - D-12 prefer explicit statuses disabled, planned, not_run, passed, failed, missing_compiler, merge_unavailable, and blocked_review.
    - D-13 enabled and cleared end-of-term module should produce split end-of-term-package.pdf alongside teaching-plan.pdf and lesson-plans.pdf.
    - D-14 default final artifact is teaching-design-package.pdf when all selected module PDFs exist and merge or compile tooling succeeds.
    - D-15 combined PDF status is passed only when teaching-design-package.pdf exists after an explicit merge or compile step.
    - D-16 split-only success should be preserved while combined output is marked unavailable or failed with evidence.
    - D-17 missing Typst/PDF tooling, unavailable merge tooling, module validation failure, unresolved review markers, and absent PDFs produce explicit manifest evidence.
    - D-18 keep broad public-command regression for jiaoan-jihua, jiaoan-shicao, and end-of-term-teaching-materials in Phase 25 except narrow Phase 24 safety checks.
    - D-19 keep OpenClaw and Hermes Agent compatible by avoiding hidden script discovery, implicit writable directories, and agent-private syntax.
    - D-20 preserve existing teaching-design-package.sh commands example, plan-split, render-split, manifest, info, and version.
    - D-21 keep end-of-term-teaching-materials as the canonical renderer for this module.
    - D-22 combined PDF behavior can start with conservative status semantics and honest tool availability checks.
    - D-23 new package command or flag names must be discoverable from SKILL.md, format-and-orchestration.md, and script help text.
    - D-24 optional ## 期末材料 template section must be concise and point to end-of-term-full.md rather than duplicating the module template.
    - D-25 SDK phase lookup mismatch is recorded context and should not block Phase 24 execution.
---

<objective>
Implement Phase 24 for `teaching-design-package`: integrate `end-of-term-teaching-materials` as an optional module, expose deterministic module artifact pointers and review-gate status in the package manifest, plan split `end-of-term-package.pdf`, and add honest default combined `teaching-design-package.pdf` status behavior. Preserve the existing end-of-term module as the source of truth and do not execute broad Phase 25 regression.
</objective>

<threat_model>
This phase primarily risks false readiness, review-gate bypass, and contract drift. Block false readiness by requiring actual file-existence evidence before `passed` PDF statuses, including `teaching-design-package.pdf`. Block review-gate bypass by checking both package-level `## 复核标记` and enabled module-local `end-of-term-full.md` / module manifest review state. Block contract drift by using public `end-of-term-teaching-materials` commands and stable module paths instead of duplicating score calculation, table generation, workbook generation, or Typst rendering internals. No credentials, network calls, or destructive git operations are required.
</threat_model>

<tasks>

<task id="01" type="execute">
<title>Update the package contract for optional end-of-term module ownership</title>
<read_first>
- skills/teaching-design-package/SKILL.md
- skills/teaching-design-package/references/format-and-orchestration.md
- skills/end-of-term-teaching-materials/SKILL.md
- skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md
- skills/end-of-term-teaching-materials/references/data-contract.md
- skills/end-of-term-teaching-materials/references/rendering-style.md
- .planning/phases/24-optional-end-of-term-module-and-package-outputs/24-CONTEXT.md
- .planning/phases/24-optional-end-of-term-module-and-package-outputs/24-RESEARCH.md
</read_first>
<action>
Revise `skills/teaching-design-package/SKILL.md` and `skills/teaching-design-package/references/format-and-orchestration.md` so the package contract explicitly supports an optional `end_of_term` module. The contract must name `end-of-term-full.md` as the module handoff, state that the package calls or references public `end-of-term-teaching-materials` commands, and document status semantics for disabled, planned, blocked_review, missing_compiler, merge_unavailable, failed, and passed. Add TDP-10 through TDP-14 traceability to the reference. Keep SKILL.md concise and keep long artifact lists, manifest details, and failure semantics in the reference.
</action>
<acceptance_criteria>
- `skills/teaching-design-package/SKILL.md` contains `end-of-term-teaching-materials`, `end-of-term-full.md`, `end-of-term-package.pdf`, and `teaching-design-package.pdf`.
- `skills/teaching-design-package/references/format-and-orchestration.md` contains `TDP-10`, `TDP-11`, `TDP-12`, `TDP-13`, and `TDP-14`.
- `skills/teaching-design-package/references/format-and-orchestration.md` contains headings or sections for optional end-of-term module behavior, end-of-term artifact pointers, combined package output behavior, and failure/status semantics.
- The reference states that score calculation, deterministic tables, workbook generation, and review-marker resolution remain owned by `skills/end-of-term-teaching-materials`.
- The reference states that disabled end-of-term module status does not fail the package due to missing end-of-term artifacts.
- The reference states that enabled module readiness is blocked when module-local `## 复核标记` is not exactly `无` or module manifest `review_cleared` is false.
</acceptance_criteria>
</task>

<task id="02" type="execute">
<title>Extend the package checkpoint template with a concise end-of-term handoff</title>
<read_first>
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/teaching-design-package/references/format-and-orchestration.md
- skills/end-of-term-teaching-materials/templates/end-of-term-full.md
- skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md
- skills/end-of-term-teaching-materials/references/data-contract.md
- .planning/phases/24-optional-end-of-term-module-and-package-outputs/24-CONTEXT.md
</read_first>
<action>
Update `skills/teaching-design-package/templates/teaching-design-package-full.md` so frontmatter `modules.end_of_term` is no longer a Phase 24 placeholder. Add explicit fields for `enabled`, `handoff`, `source_data`, `workdir`, and expected module manifest path using concrete names `end-of-term-full.md`, `end-of-term-source.json`, `end-of-term-output`, and `manifest.json`. Add a concise `## 期末材料` section or equivalent output-list block that points to the module handoff and selected artifacts without copying the full end-of-term template. Update `## 输出清单` to include `end-of-term-package.typ`, `end-of-term-package.pdf`, `tables/score-data.json`, `tables/calculated-score-data.json`, `tables/score-summary.json`, `tables/highlight-evidence.json`, `tables/score-list.md`, `tables/score-list.xlsx`, `tables/scorebook.xlsx`, and `teaching-design-package.pdf` with planned or not_run style statuses.
</action>
<acceptance_criteria>
- `skills/teaching-design-package/templates/teaching-design-package-full.md` contains `end_of_term:` with `enabled`, `handoff`, `source_data`, `workdir`, and `manifest`.
- The template contains `end-of-term-full.md`, `end-of-term-source.json`, `end-of-term-output`, and `manifest.json`.
- The template contains `## 期末材料` or a clearly labeled end-of-term block in `## 输出清单`.
- The template names `end-of-term-package.pdf`, `teaching-design-package.pdf`, `tables/score-list.xlsx`, and `tables/scorebook.xlsx`.
- The template does not duplicate the full body of `skills/end-of-term-teaching-materials/templates/end-of-term-full.md`.
- The template keeps `## 复核标记` and does not state that package-level clearance overrides module-local clearance.
</acceptance_criteria>
</task>

<task id="03" type="execute">
<title>Extend the package helper with optional module orchestration and honest combined output status</title>
<read_first>
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/teaching-design-package/references/format-and-orchestration.md
- skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh
- skills/end-of-term-teaching-materials/scripts/render_package.py
- skills/end-of-term-teaching-materials/scripts/end_of_term/_engine.py
- test/1.11/teaching-design-package/expected-manifest.json
- .planning/phases/24-optional-end-of-term-module-and-package-outputs/24-CONTEXT.md
</read_first>
<action>
Extend `skills/teaching-design-package/scripts/teaching-design-package.sh` without breaking existing commands. Preserve `example`, `plan-split`, `render-split`, `manifest`, `info`, and `version`. Add discoverable optional-module behavior through conservative commands or flags such as `plan-end-of-term`, `render-end-of-term`, `render-package`, or equivalent names chosen by the executor. The helper must read explicit `--input` and `--out-dir` or `--workdir` paths, create or point to `end-of-term-full.md`, call `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh validate`, `markdown`, `render`, `verify`, or `manifest` as appropriate, and write package manifest fields for `end_of_term`, `split_outputs`, `combined_output`, `review_markers`, and `final_ready`. Add combined output logic that marks `teaching-design-package.pdf` as `passed` only when the file exists after an explicit merge or compile command; if merge tooling is unavailable, preserve successful split output evidence and set combined status to `merge_unavailable`.
</action>
<acceptance_criteria>
- `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh` exits 0.
- The script help text still lists `example`, `plan-split`, `render-split`, `manifest`, `info`, and `version`.
- The script help text or SKILL.md documents the new optional end-of-term and combined-output commands or flags.
- Existing `skills/teaching-design-package/scripts/teaching-design-package.sh example --output /tmp/tdp-example.md` exits 0.
- Existing `skills/teaching-design-package/scripts/teaching-design-package.sh plan-split --input /tmp/tdp-example.md --out-dir /tmp/tdp-split` exits 0 and writes `jiaoan-jihua-full.md` plus `jiaoan-shicao-full.md`.
- A disabled-module manifest path marks `end_of_term.status` as `disabled` and keeps missing end-of-term artifacts non-failing.
- An enabled-module blocked-review path marks package `final_ready` false and records `blocked_review` evidence.
- The helper writes or preserves pointers to `end-of-term-package.typ`, `end-of-term-package.pdf`, module `manifest.json`, `tables/calculated-score-data.json`, `tables/score-list.xlsx`, and `tables/scorebook.xlsx`.
- The helper never marks `teaching-design-package.pdf` as `passed` unless an actual file exists at that path.
- The helper does not implement score calculation, deterministic table generation, workbook generation, or review-marker resolution itself.
</acceptance_criteria>
</task>

<task id="04" type="execute">
<title>Add Phase 24 deterministic fixture expectations for enabled, disabled, blocked, and merge-unavailable paths</title>
<read_first>
- test/1.11/teaching-design-package/fixture-source.md
- test/1.11/teaching-design-package/expected-manifest.json
- test/1.11/teaching-design-package/expected-review.md
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/end-of-term-teaching-materials/references/fixtures/end-of-term-source.json
- skills/end-of-term-teaching-materials/references/fixtures/end-of-term-source-uncertain.json
- skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md
- .planning/phases/24-optional-end-of-term-module-and-package-outputs/24-CONTEXT.md
</read_first>
<action>
Update or add deterministic test fixtures under `test/1.11/teaching-design-package/` that describe Phase 24 behavior. Keep existing Phase 23 split-output evidence valid. Add JSON expected manifests for disabled end-of-term module, enabled successful module pointers, blocked-review module behavior, and combined-output merge-unavailable behavior. Each expected manifest must include `end_of_term`, `split_outputs`, `combined_output`, `review_markers`, and `final_ready`. Use the existing sanitized end-of-term fixture sources from `skills/end-of-term-teaching-materials/references/fixtures/`; do not add real student data or private paths.
</action>
<acceptance_criteria>
- `python3 -m json.tool test/1.11/teaching-design-package/expected-end-of-term-disabled-manifest.json` exits 0.
- `python3 -m json.tool test/1.11/teaching-design-package/expected-end-of-term-enabled-manifest.json` exits 0.
- `python3 -m json.tool test/1.11/teaching-design-package/expected-end-of-term-blocked-review-manifest.json` exits 0.
- `python3 -m json.tool test/1.11/teaching-design-package/expected-combined-merge-unavailable-manifest.json` exits 0.
- Each new expected manifest contains `end_of_term`, `split_outputs`, `combined_output`, `review_markers`, and `final_ready`.
- The blocked-review fixture or expected manifest contains `blocked_review`, `review_cleared`, and `final_ready`.
- The merge-unavailable fixture or expected manifest contains `merge_unavailable` and does not claim `teaching-design-package.pdf` passed.
- `rg "真实|身份证|手机号|私有路径|/Users/.*/Desktop" test/1.11/teaching-design-package` exits 1 or finds only explanatory negative text, not fixture data.
</acceptance_criteria>
</task>

<task id="05" type="execute">
<title>Run narrow Phase 24 verification and preserve Phase 25 boundary</title>
<read_first>
- README.md
- skills/README.md
- docs/compatibility-matrix.md
- skills/teaching-design-package/SKILL.md
- skills/teaching-design-package/references/format-and-orchestration.md
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/end-of-term-teaching-materials/SKILL.md
- skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md
- .planning/REQUIREMENTS.md
- .planning/phases/24-optional-end-of-term-module-and-package-outputs/24-CONTEXT.md
</read_first>
<action>
Run verification commands that prove TDP-10 through TDP-14 and the Phase 24 decisions are represented in source, templates, helper behavior, and deterministic fixture expectations. Keep broad regression for `jiaoan-jihua`, `jiaoan-shicao`, and public documentation indexes out of scope unless a narrow smoke check is needed to prove existing `teaching-design-package` commands still work. If docs are touched due to changed artifact contracts, keep updates minimal and record that Phase 25 still owns full discoverability and public-command regression.
</action>
<acceptance_criteria>
- `rg "TDP-10|TDP-11|TDP-12|TDP-13|TDP-14" skills/teaching-design-package/SKILL.md skills/teaching-design-package/references/format-and-orchestration.md` finds all five requirement IDs.
- `rg "end-of-term-teaching-materials|end-of-term-full.md|end-of-term-package.pdf|teaching-design-package.pdf" skills/teaching-design-package/SKILL.md skills/teaching-design-package/references/format-and-orchestration.md skills/teaching-design-package/templates/teaching-design-package-full.md` exits 0.
- `rg "blocked_review|merge_unavailable|missing_compiler|disabled|not_run|passed|failed" skills/teaching-design-package/references/format-and-orchestration.md skills/teaching-design-package/scripts/teaching-design-package.sh` exits 0.
- `rg "calculated-score-data.json|score-list.xlsx|scorebook.xlsx|highlight-evidence.json" skills/teaching-design-package/references/format-and-orchestration.md skills/teaching-design-package/templates/teaching-design-package-full.md skills/teaching-design-package/scripts/teaching-design-package.sh` exits 0.
- `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh` exits 0.
- `skills/teaching-design-package/scripts/teaching-design-package.sh example --output /tmp/tdp24-example.md` exits 0.
- `skills/teaching-design-package/scripts/teaching-design-package.sh plan-split --input /tmp/tdp24-example.md --out-dir /tmp/tdp24-split` exits 0.
- `git diff -- skills/jiaoan-jihua/SKILL.md skills/jiaoan-shicao/SKILL.md skills/end-of-term-teaching-materials/SKILL.md` is empty unless the executor records a deliberate docs-only cross-reference.
- `git diff --check` exits 0.
</acceptance_criteria>
</task>

</tasks>

<verification>
Run these checks after completing the Phase 24 tasks:

```bash
rg "TDP-10|TDP-11|TDP-12|TDP-13|TDP-14" skills/teaching-design-package/SKILL.md skills/teaching-design-package/references/format-and-orchestration.md
rg "end-of-term-teaching-materials|end-of-term-full.md|end-of-term-package.pdf|teaching-design-package.pdf" skills/teaching-design-package/SKILL.md skills/teaching-design-package/references/format-and-orchestration.md skills/teaching-design-package/templates/teaching-design-package-full.md
rg "blocked_review|merge_unavailable|missing_compiler|disabled|not_run|passed|failed" skills/teaching-design-package/references/format-and-orchestration.md skills/teaching-design-package/scripts/teaching-design-package.sh
rg "calculated-score-data.json|score-list.xlsx|scorebook.xlsx|highlight-evidence.json" skills/teaching-design-package/references/format-and-orchestration.md skills/teaching-design-package/templates/teaching-design-package-full.md skills/teaching-design-package/scripts/teaching-design-package.sh
python3 -m json.tool test/1.11/teaching-design-package/expected-end-of-term-disabled-manifest.json >/tmp/phase24-disabled-manifest.json
python3 -m json.tool test/1.11/teaching-design-package/expected-end-of-term-enabled-manifest.json >/tmp/phase24-enabled-manifest.json
python3 -m json.tool test/1.11/teaching-design-package/expected-end-of-term-blocked-review-manifest.json >/tmp/phase24-blocked-manifest.json
python3 -m json.tool test/1.11/teaching-design-package/expected-combined-merge-unavailable-manifest.json >/tmp/phase24-merge-unavailable-manifest.json
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh
skills/teaching-design-package/scripts/teaching-design-package.sh example --output /tmp/tdp24-example.md
skills/teaching-design-package/scripts/teaching-design-package.sh plan-split --input /tmp/tdp24-example.md --out-dir /tmp/tdp24-split
test -f /tmp/tdp24-split/jiaoan-jihua-full.md
test -f /tmp/tdp24-split/jiaoan-shicao-full.md
git diff -- skills/jiaoan-jihua/SKILL.md skills/jiaoan-shicao/SKILL.md skills/end-of-term-teaching-materials/SKILL.md
git diff --check
```

Do not run `/gsd:execute-phase 24` from this plan-phase command. Execution belongs to the next GSD command.
</verification>

<success_criteria>
- TDP-10 through TDP-14 are covered by the plan's task scope and verification commands.
- The package skill supports the end-of-term workflow as an optional module while keeping the standalone end-of-term skill canonical.
- The existing `end-of-term-full.md` review checkpoint and `## 复核标记` export gate remain mandatory for enabled module final readiness.
- The package manifest makes deterministic end-of-term table, workbook, module manifest, split PDF, and combined PDF statuses discoverable.
- `end-of-term-package.pdf` and `teaching-design-package.pdf` are honest outputs: neither is marked passed without actual file evidence.
- OpenClaw and Hermes Agent constraints are preserved through explicit files, commands, statuses, and no runtime-private canonical syntax.
- Phase 25 remains responsible for broad regression and documentation-index verification.
</success_criteria>
