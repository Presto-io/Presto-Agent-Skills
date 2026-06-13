---
phase: 23
plan: 01
name: integrated-skill-entry-and-jiaoan-orchestration
type: execute
wave: 1
depends_on:
  - phase: 22
    provides: "package-level scheduling contract and fixture evidence"
files_modified:
  - skills/teaching-design-package/SKILL.md
  - skills/teaching-design-package/references/format-and-orchestration.md
  - skills/teaching-design-package/templates/teaching-design-package-full.md
  - skills/teaching-design-package/scripts/teaching-design-package.sh
  - test/1.11/teaching-design-package/fixture-source.md
  - test/1.11/teaching-design-package/expected-manifest.json
  - test/1.11/teaching-design-package/expected-review.md
  - README.md
  - skills/README.md
  - docs/compatibility-matrix.md
autonomous: true
requirements:
  - TDP-05
  - TDP-06
  - TDP-07
  - TDP-08
  - TDP-09
must_haves:
  truths:
    - D-01 use skills/teaching-design-package/ as the new skill directory and teaching-design-package as the trigger/name.
    - D-02 keep SKILL.md concise; long package rules belong in references, scripts belong in scripts, and templates belong in templates.
    - D-03 the new skill is an orchestrator over stable contracts, not a physical merge of existing jiaoan directories.
    - D-04 do not change existing public commands, flags, output paths, fixture comparison behavior, or runtime adapter notes in jiaoan-jihua or jiaoan-shicao unless only a minimal discoverability cross-reference is needed.
    - D-05 define a persistent package-level Markdown intermediate named teaching-design-package-full.md.
    - D-06 package Markdown includes metadata, scheduling inputs/evidence, teaching-plan section, lesson-plan section, output selection/status, and ## 复核标记.
    - D-07 scheduling evidence from references/scheduling-contract.md appears in teacher-readable form and remains traceable to source pointers.
    - D-08 unresolved review markers block final readiness and must not be silently dropped.
    - D-09 one-step source-to-PDF generation remains out of scope.
    - D-10 generate or extract module-local Markdown intermediates compatible with jiaoan-jihua-full.md and jiaoan-shicao-full.md, then invoke or reference existing render paths.
    - D-11 use Phase 22 source-order scheduling contract as the shared schedule layer; do not expose old jiaoan-jihua.sh parser as package API.
    - D-12 preserve jiaoan-jihua frontmatter/body contract.
    - D-13 preserve jiaoan-shicao three-part structure and avoid inventing missing fields.
    - D-14 package-level course metadata is the normalized source of truth, with explicit module-specific overrides only when needed.
    - D-15 plan split teaching-plan and lesson-plan outputs first.
    - D-16 leave default combined teaching-design-package.pdf and optional end-of-term-package.pdf behavior to Phase 24.
    - D-17 do not claim PDF success unless a PDF command has actually run and produced evidence.
    - D-18 record partial Typst/status evidence when renderer or compiler is unavailable.
    - D-19 represent Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent in Runtime Adapter Notes.
    - D-20 keep canonical workflow text portable; runtime-specific behavior belongs in adapter notes.
    - D-21 OpenClaw and Hermes Agent notes mention skill-folder discovery, support-file availability, shell-script execution permissions, and calendar/support resources.
    - D-22 verification includes adapter coverage grep and canonical text avoids runtime-private syntax outside notes.
    - D-23 implement a minimal viable orchestration entry sufficient for TDP-05 through TDP-09, not the full optional end-of-term package.
    - D-24 no external web research is required.
    - D-25 exact internal filenames may be decided by implementation, but must stay discoverable from SKILL.md and consistent with existing layout.
---

<objective>
Implement the Phase 23 minimal `teaching-design-package` orchestration slice: a new portable skill entry, package Markdown checkpoint, jiaoan module handoff/reference rules, split teaching-plan and lesson-plan Typst/PDF status planning, and runtime adapter coverage. Preserve `jiaoan-jihua` and `jiaoan-shicao` as standalone public skills and defer optional end-of-term and combined package behavior.
</objective>

<threat_model>
This phase does not process credentials, network requests, or production systems. Main risks are documentation/API integrity risks: accidentally changing existing jiaoan public behavior, claiming generated PDFs without evidence, burying runtime-private syntax in canonical workflow text, or silently dropping uncertain schedule/content inputs. Block these with read-first checks, unchanged public-command verification, explicit review-marker gates, split Typst/PDF status fields, and adapter coverage assertions.
</threat_model>

<tasks>

<task id="01" type="execute">
<title>Add the teaching-design-package skill entry and orchestration reference</title>
<read_first>
- skills/teaching-design-package/SKILL.md if it already exists
- skills/teaching-design-package/references/format-and-orchestration.md if it already exists
- templates/skill/SKILL.md
- AGENTS.md
- README.md
- skills/README.md
- docs/directory-spec.md
- docs/compatibility-matrix.md
- docs/markdown-normalization-contract.md
- references/scheduling-contract.md
- skills/jiaoan-jihua/SKILL.md
- skills/jiaoan-shicao/SKILL.md
- .planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-CONTEXT.md
- .planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-RESEARCH.md
</read_first>
<action>
Create `skills/teaching-design-package/SKILL.md` using the repository skill template pattern. Set `name: "teaching-design-package"`, a description that triggers only for integrated teaching-design packages, metadata version `0.1.0`, portability `canonical`, and supported runtimes `Codex`, `Claude Code`, `Gemini CLI`, `OpenCode`, `OpenClaw`, and `Hermes Agent`. The entry must state that the skill composes `jiaoan-jihua` and `jiaoan-shicao`, preserves them as standalone skills, normalizes source material to `templates/teaching-design-package-full.md`, consumes `references/scheduling-contract.md`, and points long rules to `references/format-and-orchestration.md`. Create `skills/teaching-design-package/references/format-and-orchestration.md` with package input fields, required review sections, module handoff rules for `jiaoan-jihua-full.md` and `jiaoan-shicao-full.md`, split output status semantics, Phase 24 deferrals, and review-marker blocking rules.
</action>
<acceptance_criteria>
- `skills/teaching-design-package/SKILL.md` contains `name: "teaching-design-package"`.
- `skills/teaching-design-package/SKILL.md` contains all six runtime names: `Codex`, `Claude Code`, `Gemini CLI`, `OpenCode`, `OpenClaw`, and `Hermes Agent`.
- `skills/teaching-design-package/SKILL.md` contains `references/format-and-orchestration.md`, `templates/teaching-design-package-full.md`, and `references/scheduling-contract.md`.
- `skills/teaching-design-package/SKILL.md` states that `jiaoan-jihua` and `jiaoan-shicao` remain standalone skills.
- `skills/teaching-design-package/references/format-and-orchestration.md` contains `TDP-05`, `TDP-06`, `TDP-07`, `TDP-08`, and `TDP-09`.
- `skills/teaching-design-package/references/format-and-orchestration.md` contains the headings `## Package Markdown Intermediate`, `## Jiaoan Module Handoff`, `## Split Output Status`, and `## Deferred to Phase 24`.
- `skills/teaching-design-package/references/format-and-orchestration.md` states that unresolved review markers block final readiness.
</acceptance_criteria>
</task>

<task id="02" type="execute">
<title>Add the package Markdown template and module handoff scaffold</title>
<read_first>
- skills/teaching-design-package/templates/teaching-design-package-full.md if it already exists
- skills/teaching-design-package/references/format-and-orchestration.md
- skills/jiaoan-jihua/templates/jiaoan-jihua-full.md
- skills/jiaoan-jihua/references/format-and-rendering.md
- skills/jiaoan-shicao/templates/jiaoan-shicao-full.md
- skills/jiaoan-shicao/references/format-and-rendering.md
- references/scheduling-contract.md
- test/1.11/scheduling-contract/expected-schedule.md
- .planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-CONTEXT.md
</read_first>
<action>
Create `skills/teaching-design-package/templates/teaching-design-package-full.md` as the persistent package checkpoint. Use YAML frontmatter with concrete placeholder fields `template: "teaching-design-package"`, `course_name`, `major_name`, `teacher_name`, `class_name`, `first_teaching_day`, `daily_hours`, `modules`, and `outputs`. The body must include Chinese teacher-facing sections `## 课程与整包元数据`, `## 调度输入`, `## 调度证据`, `## 授课计划`, `## 实操教案`, `## 输出清单`, and `## 复核标记`. Include source-pointer examples such as `task:1/stage:1/row:1` and lesson-fragment examples such as `lesson:1/activity:1`. Include module handoff comments or bullets that name `jiaoan-jihua-full.md` and `jiaoan-shicao-full.md` without duplicating their full templates.
</action>
<acceptance_criteria>
- `skills/teaching-design-package/templates/teaching-design-package-full.md` contains `template: "teaching-design-package"`.
- The template contains the exact headings `## 调度证据`, `## 授课计划`, `## 实操教案`, `## 输出清单`, and `## 复核标记`.
- The template contains `jiaoan-jihua-full.md` and `jiaoan-shicao-full.md`.
- The template contains source pointer examples `task:1/stage:1/row:1` and `lesson:1/activity:1`.
- The template keeps optional end-of-term material as an explicit Phase 24 placeholder or deferral, not as an implemented module.
</acceptance_criteria>
</task>

<task id="03" type="execute">
<title>Add the minimal package helper script for split module rendering and honest status</title>
<read_first>
- skills/teaching-design-package/scripts/teaching-design-package.sh if it already exists
- skills/teaching-design-package/SKILL.md
- skills/teaching-design-package/references/format-and-orchestration.md
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/jiaoan-jihua/scripts/jiaoan-jihua.sh
- skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
- references/scheduling-contract.md
- scripts/derive-scheduling-fixture.py
</read_first>
<action>
Create `skills/teaching-design-package/scripts/teaching-design-package.sh` with commands `example`, `plan-split`, `render-split`, `manifest`, `info`, and `version`. `example --output <file>` should copy or emit the package template. `plan-split --input <package-md> --out-dir <dir>` should validate the package checkpoint has required sections and write module-local scaffold files named `jiaoan-jihua-full.md` and `jiaoan-shicao-full.md` into the output directory. `render-split --input <package-md> --out-dir <dir>` should call the existing jiaoan render commands to produce `teaching-plan.typ` and `lesson-plans.typ` from those module-local files. The script must write or update a manifest containing `teaching_plan_typ`, `lesson_plans_typ`, `teaching_plan_pdf`, `lesson_plans_pdf`, `review_markers`, and `final_ready`. PDF fields must remain `not_run`, `missing_compiler`, or `passed`; they must not be marked `passed` unless explicit PDF compilation succeeds and output files exist. Do not implement `end-of-term-package.pdf` or combined `teaching-design-package.pdf` in this phase.
</action>
<acceptance_criteria>
- `skills/teaching-design-package/scripts/teaching-design-package.sh` contains `cmd_example`, `cmd_plan_split`, `cmd_render_split`, `cmd_manifest`, `cmd_info`, and `cmd_version`.
- `skills/teaching-design-package/scripts/teaching-design-package.sh example --output /tmp/tdp-example.md` exits 0 and writes a file containing `## 复核标记`.
- `skills/teaching-design-package/scripts/teaching-design-package.sh plan-split --input /tmp/tdp-example.md --out-dir /tmp/tdp-split` exits 0 and writes `/tmp/tdp-split/jiaoan-jihua-full.md` plus `/tmp/tdp-split/jiaoan-shicao-full.md`.
- The script contains `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render` and `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render`.
- The script contains manifest keys `teaching_plan_typ`, `lesson_plans_typ`, `teaching_plan_pdf`, `lesson_plans_pdf`, `review_markers`, and `final_ready`.
- The script does not contain `end-of-term-package.pdf` or `teaching-design-package.pdf` except in a help or deferral message that labels them Phase 24.
</acceptance_criteria>
</task>

<task id="04" type="execute">
<title>Add deterministic orchestration fixture and verification evidence</title>
<read_first>
- test/1.11/teaching-design-package/fixture-source.md if it already exists
- test/1.11/teaching-design-package/expected-manifest.json if it already exists
- test/1.11/teaching-design-package/expected-review.md if it already exists
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/teaching-design-package/scripts/teaching-design-package.sh
- test/1.11/scheduling-contract/expected-schedule.md
- test/1.11/scheduling-contract/expected-schedule.json
- references/scheduling-contract.md
- .planning/phases/22-scheduling-contract-and-fixture/22-VERIFICATION.md
</read_first>
<action>
Create `test/1.11/teaching-design-package/fixture-source.md` as a small package checkpoint using the same course context as the existing jiaoan fixtures. Include scheduling evidence copied or summarized from `test/1.11/scheduling-contract/expected-schedule.md`, a teaching-plan module block, a lesson-plan module block, an output selection/status block, and a `## 复核标记` section. Create `expected-manifest.json` with deterministic expected keys for split Typst outputs, PDF status, review markers, and `final_ready`. Create `expected-review.md` as a human-readable expected review summary. Keep fixture scope limited to the two jiaoan modules and split outputs.
</action>
<acceptance_criteria>
- `test/1.11/teaching-design-package/fixture-source.md` contains `## 调度证据`, `## 授课计划`, `## 实操教案`, `## 输出清单`, and `## 复核标记`.
- `test/1.11/teaching-design-package/expected-manifest.json` is valid JSON when checked with `python3 -m json.tool`.
- `test/1.11/teaching-design-package/expected-manifest.json` contains `teaching_plan_typ`, `lesson_plans_typ`, `teaching_plan_pdf`, `lesson_plans_pdf`, `review_markers`, and `final_ready`.
- `test/1.11/teaching-design-package/expected-review.md` contains `teaching-plan.typ`, `lesson-plans.typ`, and `PDF status`.
- No Phase 23 fixture claims a completed `teaching-design-package.pdf` or `end-of-term-package.pdf`.
</acceptance_criteria>
</task>

<task id="05" type="execute">
<title>Wire discoverability and run Phase 23 plan verification</title>
<read_first>
- README.md
- skills/README.md
- docs/compatibility-matrix.md
- docs/directory-spec.md
- skills/teaching-design-package/SKILL.md
- skills/teaching-design-package/references/format-and-orchestration.md
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/jiaoan-jihua/SKILL.md
- skills/jiaoan-shicao/SKILL.md
- .planning/REQUIREMENTS.md
- .planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-CONTEXT.md
</read_first>
<action>
Update `README.md` and `skills/README.md` so `teaching-design-package` is discoverable as an integrated package skill. Update `docs/compatibility-matrix.md` only if a new package-specific runtime caution is needed; otherwise rely on `SKILL.md` adapter notes. Run verification commands for source presence, adapter coverage, JSON syntax, script syntax, example/split smoke behavior, deferred Phase 24 boundary, unchanged existing jiaoan command surfaces, and whitespace checks. Record verification evidence in the Phase 23 summary during execute-phase.
</action>
<acceptance_criteria>
- `README.md` contains `teaching-design-package`.
- `skills/README.md` contains `teaching-design-package` and lists its Markdown intermediate as `templates/teaching-design-package-full.md`.
- `rg "Codex|Claude Code|Gemini CLI|OpenCode|OpenClaw|Hermes Agent" skills/teaching-design-package/SKILL.md` finds all six runtime names.
- `python3 -m json.tool test/1.11/teaching-design-package/expected-manifest.json` exits 0.
- `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh` exits 0.
- `skills/teaching-design-package/scripts/teaching-design-package.sh example --output /tmp/tdp-example.md` exits 0.
- `skills/teaching-design-package/scripts/teaching-design-package.sh plan-split --input /tmp/tdp-example.md --out-dir /tmp/tdp-split` exits 0.
- `git diff -- skills/jiaoan-jihua/SKILL.md skills/jiaoan-shicao/SKILL.md` shows no public command-surface change unless the executor records an explicit docs-only discoverability note.
- `rg "TDP-05|TDP-06|TDP-07|TDP-08|TDP-09" skills/teaching-design-package/SKILL.md skills/teaching-design-package/references/format-and-orchestration.md` finds all five requirement IDs.
- `git diff --check` exits 0.
</acceptance_criteria>
</task>

</tasks>

<verification>
Run these checks after completing the Phase 23 tasks:

```bash
rg "TDP-05|TDP-06|TDP-07|TDP-08|TDP-09" skills/teaching-design-package/SKILL.md skills/teaching-design-package/references/format-and-orchestration.md
rg "Codex|Claude Code|Gemini CLI|OpenCode|OpenClaw|Hermes Agent" skills/teaching-design-package/SKILL.md
rg "references/scheduling-contract.md|jiaoan-jihua|jiaoan-shicao|teaching-design-package-full.md" skills/teaching-design-package/SKILL.md skills/teaching-design-package/references/format-and-orchestration.md
rg "## 调度证据|## 授课计划|## 实操教案|## 输出清单|## 复核标记" skills/teaching-design-package/templates/teaching-design-package-full.md
python3 -m json.tool test/1.11/teaching-design-package/expected-manifest.json >/tmp/phase23-expected-manifest.json
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh
skills/teaching-design-package/scripts/teaching-design-package.sh example --output /tmp/tdp-example.md
skills/teaching-design-package/scripts/teaching-design-package.sh plan-split --input /tmp/tdp-example.md --out-dir /tmp/tdp-split
test -f /tmp/tdp-split/jiaoan-jihua-full.md
test -f /tmp/tdp-split/jiaoan-shicao-full.md
git diff -- skills/jiaoan-jihua/SKILL.md skills/jiaoan-shicao/SKILL.md
rg "teaching-design-package" README.md skills/README.md
git diff --check
```

The `git diff -- skills/jiaoan-jihua/SKILL.md skills/jiaoan-shicao/SKILL.md` command should be empty unless the executor documents a minimal docs-only cross-reference. The plan intentionally does not verify `teaching-design-package.pdf` or `end-of-term-package.pdf`; those are Phase 24 concerns.
</verification>

<success_criteria>
- TDP-05 through TDP-09 are covered by the new skill entry, orchestration reference, package Markdown template, split-output helper behavior, fixture evidence, and adapter coverage.
- Existing `jiaoan-jihua` and `jiaoan-shicao` skills remain standalone and callable.
- The package workflow has a persistent teacher-reviewable Markdown checkpoint before Typst/PDF generation.
- Scheduling evidence from Phase 22 is visible and traceable in the package contract.
- Split `teaching-plan` and `lesson-plans` Typst/PDF status is explicit and honest.
- Runtime adapter notes cover Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
- Optional end-of-term module, workbook/table package behavior, combined `teaching-design-package.pdf`, and full regression/documentation gates remain deferred to later phases.
</success_criteria>
