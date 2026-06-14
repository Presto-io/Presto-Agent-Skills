---
phase: 28
plan: 01
name: markdown-baseline-ingestion-and-typst-generation
type: execute
wave: 1
depends_on:
  - phase: 27
    provides: "current jiaoan-shicao renderer behavior and integrated-package date/table regression baseline"
files_modified:
  - skills/teaching-design-package/scripts/teaching-design-package.sh
  - skills/teaching-design-package/references/format-and-orchestration.md
  - skills/teaching-design-package/SKILL.md
  - .planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-VERIFICATION.md
autonomous: true
requirements:
  - TDBR-01
  - TDBR-02
  - TDBR-03
  - TDBR-04
  - TDBR-05
  - TDBR-12
  - TDBR-13
  - TDBR-14
  - TDBR-15
  - TDBR-16
  - TDBR-17
must_haves:
  truths:
    - D-01 use `skills/teaching-design-package/templates/teaching-design-package-full.md` as the Phase 28 source contract.
    - D-02 do not change the baseline Markdown's teacher-facing format, headings, frontmatter shape, paragraph order, or visible review flow.
    - D-03 keep `jiaoan-jihua` and `jiaoan-shicao` standalone; do not change their public commands, accepted inputs, output paths, or documentation contracts.
    - D-04 do not implement Phase 29 final PDF parity; record PDF slots and honest non-passed status only.
    - D-05 do not stage generated `deliverables/` artifacts; use `/tmp` or phase-local evidence for generated smoke outputs.
    - D-06 accept `# 授课进度计划` as the teaching-plan source anchor.
    - D-07 accept `# 教学设计方案` as the lesson-plan source anchor.
    - D-08 preserve all three repeated `学习任务分析` blocks.
    - D-09 preserve all three `教学活动设计——学习任务N：...` blocks and their `###`/`####` grouping.
    - D-10 preserve all three `学业评价` blocks, numbered evaluation rows, and trailing `小结：...` text.
    - D-11 preserve repeated task structure; do not flatten the package into a single lesson block.
    - D-12 prefer section slicing/internal model over Markdown mutation.
    - D-13 replace or extend package validation so baseline mode accepts `# 授课进度计划` plus `# 教学设计方案`; keep old package mode only if it remains useful and verified.
    - D-14 parse YAML `teachers` list and map it to legacy scalar `teacher_name` handoff metadata deterministically.
    - D-15 derive only from visible baseline content; leave missing school, semester, teacher, date, or evaluation facts blank/non-final rather than inventing.
    - D-16 do not force a `## 复核标记` section into the teacher-facing baseline.
    - D-17 add package-level Typst generation from baseline Markdown.
    - D-18 include both semantic parts in `teaching-design-package.typ` in source order.
    - D-19 preserve split handoff and Phase 29 PDF slots: `jiaoan-jihua-full.md`, `jiaoan-shicao-full.md`, `teaching-plan.typ`, `lesson-plans.typ`, `teaching-plan.pdf`, `lesson-plans.pdf`, `teaching-design-package.pdf`.
    - D-20 record provenance from single Markdown baseline to generated package Markdown, module handoffs, package Typst, semantic anchors, and planned PDF slots.
    - D-21 keep generated Typst inspectable but not the source of truth; future edits remain in Markdown.
    - D-22 address current `plan-split` template-copy behavior so it slices baseline sections.
    - D-23 address old `##` validator mismatch with top-level `#` baseline anchors.
    - D-24 preserve paragraph order and blank-line grouping in activity blocks.
    - D-25 map `teachers` list to scalar handoff metadata and record mapping evidence.
    - D-26 choose a clear public command path for package Typst, preferably extending existing `render-package`.
    - D-27 choose a Typst composition path that keeps Markdown provenance clear and Phase 29 parity testable.
    - D-28 calculate package total hours from all `# 授课进度计划` rows; do not preserve or rely on package YAML `total_hours`; current baseline must be `160H`.
    - D-29 calculate task hours from each task's own plan rows; current baseline must be `CA6140=40H`, `X62W=60H`, `Z3040=60H`.
    - D-30 generate lesson-plan activity `##### xH` rows only from same-name or same-order plan activity mappings.
    - D-31 fail or record explicit non-final/review-needed status when activity-hour mapping fails; do not guess.
    - D-32 infer `学习任务分析` date ranges from `first_teaching_day`, built-in teaching-day calendar, default `8` hours/day, and parsed plan-row hours.
    - D-33 current baseline date expectations are `CA6140=5月11日——5月15日`, `X62W=5月18日——5月27日`, `Z3040=5月27日——6月5日`.
    - D-34 infer `school_year` and `semester` from `first_teaching_day`; current baseline must infer `2025-2026学年第二学期`.
    - D-35 keep `hour_unit`, `daily_hours`, `date_display_format`, `date_locale`, `calendar_source`, `holidays`, `makeup_days`, `source_of_truth`, `outputs`, and `validation` in script/skill contracts or generated evidence, not package YAML.
    - D-36 keep generated package Markdown directly copyable from the baseline document shape; put machine facts in handoffs, manifests, Typst provenance, or verification evidence only.
---

<objective>
Implement Phase 28 baseline ingestion for `teaching-design-package`: make the package render path consume the committed teacher-facing Markdown baseline unchanged, generate/copy one package Markdown artifact in the same shape, derive hours/date/term facts from the teaching-plan rows and scheduling contract instead of package YAML, create module-compatible handoffs for `jiaoan-jihua` and `jiaoan-shicao`, generate one `teaching-design-package.typ` from that Markdown through the public package render path, and record provenance plus Phase 29 PDF slots without claiming PDF parity.
</objective>

<threat_model>
Primary risks are mutating the teacher-facing baseline to satisfy parser internals, silently dropping repeated lesson-plan blocks, reintroducing derived/default facts into package YAML, duplicating or hand-maintaining total/task/activity hours, guessing date ranges, breaking standalone `jiaoan-jihua` or `jiaoan-shicao` contracts, treating Typst as the maintained source, and reporting PDF completion before Phase 29. Block these with baseline hash/diff checks, heading-count assertions, derived hour/date/term assertions, black-box package commands, scalar teacher metadata mapping evidence, manifest provenance, public-command smoke checks, and non-passed PDF statuses unless real PDF files exist.
</threat_model>

<tasks>

<task id="01" type="execute">
<title>Record baseline shape and reproduce the current validator/scaffold gap</title>
<read_first>
- AGENTS.md
- .planning/ROADMAP.md
- .planning/STATE.md
- .planning/REQUIREMENTS.md
- .planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-CONTEXT.md
- .planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-RESEARCH.md
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/teaching-design-package/references/format-and-orchestration.md
- skills/jiaoan-jihua/references/format-and-rendering.md
- skills/jiaoan-shicao/references/format-and-rendering.md
</read_first>
<action>
Create `.planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-VERIFICATION.md` during execution. Before editing implementation code, record the baseline hash, top-level section anchors, frontmatter fields, `teachers` list shape, semantic counts, absence of derived/default YAML fields, derived hour totals, expected task date ranges, and expected academic year/semester. Reproduce the current failure or mismatch by running the package script against `skills/teaching-design-package/templates/teaching-design-package-full.md` in a `/tmp/tdp-phase28.XXXXXX` directory. Capture whether `plan-split` rejects the baseline because `validate_package()` expects old `##` sections, or whether it still copies old standalone templates rather than slicing the baseline.
</action>
<acceptance_criteria>
- `28-VERIFICATION.md` contains a `Pre-fix baseline and gap reproduction` section.
- The section records the exact baseline path and SHA-256 hash before edits.
- The section records that `# 授课进度计划` appears before `# 教学设计方案`.
- The section records counts for three teaching-plan task `##` headings, three `## 学习任务分析` blocks, three `## 教学活动设计——学习任务` blocks, and three `## 学业评价` blocks.
- The section records the YAML `teachers` list and the intended scalar handoff value for the current baseline, `张老师`.
- The section records that package YAML does not contain `total_hours`, `school_year`, `semester`, `daily_hours`, `hour_unit`, `date_display_format`, `date_locale`, `calendar_source`, `holidays`, `makeup_days`, `source_of_truth`, `outputs`, or `validation`.
- The section records derived hours `total=160H`, `CA6140=40H`, `X62W=60H`, `Z3040=60H`.
- The section records expected date ranges `CA6140=5月11日——5月15日`, `X62W=5月18日——5月27日`, `Z3040=5月27日——6月5日`.
- The section records expected inferred term metadata `2025-2026学年第二学期`.
- The section records exact commands, exit statuses, and outputs for the pre-fix package run.
- Generated reproduction files live under `/tmp` and no `deliverables/` files are staged.
</acceptance_criteria>
</task>

<task id="02" type="execute">
<title>Add baseline-mode validation and provenance-aware Markdown artifact handling</title>
<read_first>
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/teaching-design-package/references/format-and-orchestration.md
- docs/markdown-normalization-contract.md
- references/scheduling-contract.md
- .planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-CONTEXT.md
</read_first>
<action>
Update `skills/teaching-design-package/scripts/teaching-design-package.sh` with a baseline-mode validator that accepts the corrected Markdown anchors `# 授课进度计划` and `# 教学设计方案`. Keep validation strict enough to fail if either anchor is missing, out of order, or duplicated unexpectedly. Preserve old package validation behavior only if it can coexist cleanly; otherwise document the baseline-mode switch in the reference. Ensure `example` still copies `skills/teaching-design-package/templates/teaching-design-package-full.md` byte-for-byte to the requested output. Ensure `plan-split`, `render-split`, `render-package`, and `manifest` use the same baseline-aware validation. Add manifest or sidecar provenance fields for `source_markdown`, `generated_package_markdown`, semantic anchors/ranges, derived total/task hours, derived date ranges, inferred term metadata, and `generated_from_markdown: true`.
</action>
<acceptance_criteria>
- `validate_package()` or its replacement accepts the baseline when both top-level anchors are present in source order.
- Validation fails when `# 授课进度计划` or `# 教学设计方案` is missing from a temporary edited copy.
- Validation does not require adding `## 课程与整包元数据`, `## 调度输入`, `## 调度证据`, `## 输出清单`, or `## 复核标记` to the baseline.
- Validation rejects or reports non-final status if package YAML reintroduces derived/default fields that v1.13 forbids as teacher-maintained inputs.
- `example --output "$tmpdir/teaching-design-package-full.md"` produces a file byte-identical to `skills/teaching-design-package/templates/teaching-design-package-full.md`.
- Manifest or provenance evidence contains `source_markdown`, `generated_package_markdown`, `section_anchors` or equivalent, derived hour/date/term fields, and `generated_from_markdown: true`.
- `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh` exits 0.
</acceptance_criteria>
</task>

<task id="03" type="execute">
<title>Slice baseline into module-compatible handoffs without changing standalone skills</title>
<read_first>
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/jiaoan-jihua/templates/jiaoan-jihua-full.md
- skills/jiaoan-jihua/references/format-and-rendering.md
- skills/jiaoan-jihua/scripts/jiaoan-jihua.sh
- skills/jiaoan-shicao/templates/jiaoan-shicao-full.md
- skills/jiaoan-shicao/references/format-and-rendering.md
- skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
- .planning/phases/27-official-activity-table-width-alignment/27-VERIFICATION.md
</read_first>
<action>
Replace template-copy scaffold behavior with baseline slicing for the corrected Markdown. Generate `jiaoan-jihua-full.md` by mapping package frontmatter into the legacy scalar fields and copying the body from `# 授课进度计划` up to `# 教学设计方案`. Generate `jiaoan-shicao-full.md` by mapping package frontmatter into the legacy scalar fields and copying the repeated blocks from `# 教学设计方案`. Preserve the `## 学习任务分析`, `## 教学活动设计——学习任务N：...`, and `## 学业评价` structures and all repeated task blocks. Map YAML `teachers` list to `teacher_name` deterministically: one teacher uses that name, multiple teachers join with `、`, no teachers leaves the scalar blank and records a provenance warning. Derive `total_hours`, task hours, activity `##### <hours>H` rows, `起止日期`, and academic year/semester for generated handoffs from `# 授课进度计划`, `first_teaching_day`, the built-in teaching-day calendar, and default `8` hours/day. Treat generated `##### xH` as handoff/render data only; if any activity cannot be mapped by same-name or same-order plan rows, fail the command or record non-final/review-needed status rather than inventing. Do not edit `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`, `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`, or their public contracts.
</action>
<acceptance_criteria>
- `plan-split --input "$tmpdir/teaching-design-package-full.md" --out-dir "$tmpdir/out"` exits 0.
- `$tmpdir/out/jiaoan-jihua-full.md` exists and contains frontmatter `template: "jiaoan-jihua"` plus `teacher_name: "张老师"` for the current baseline.
- `$tmpdir/out/jiaoan-jihua-full.md` contains the three baseline teaching-plan `##` task headings in source order.
- `$tmpdir/out/jiaoan-shicao-full.md` exists and contains frontmatter `template: "jiaoan-shicao"` plus `teacher_name: "张老师"` for the current baseline.
- `$tmpdir/out/jiaoan-shicao-full.md` contains derived `total_hours`/displayed total evidence equivalent to `160H` without requiring package YAML `total_hours`.
- `$tmpdir/out/jiaoan-shicao-full.md` contains derived learning-task hours `40H`, `60H`, and `60H`.
- `$tmpdir/out/jiaoan-shicao-full.md` contains derived task date ranges `5月11日——5月15日`, `5月18日——5月27日`, and `5月27日——6月5日` with no year in the teacher-facing value.
- `$tmpdir/out/jiaoan-shicao-full.md` contains or renders inferred term metadata `2025-2026学年第二学期` from `first_teaching_day`.
- `$tmpdir/out/jiaoan-shicao-full.md` contains three `## 学习任务分析` blocks, three `## 教学活动设计——学习任务` blocks, and three `## 学业评价` blocks.
- Activity `##### xH` rows in `$tmpdir/out/jiaoan-shicao-full.md` are derived from same-name or same-order `# 授课进度计划` rows, and verification records the mapping or non-final failure behavior.
- Paragraph order and blank-line grouping under `####` activity blocks are preserved or intentionally transformed only to satisfy the documented standalone `jiaoan-shicao` handoff contract.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` and `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` are unchanged unless the executor records an explicit, unavoidable reason and updates this plan's scope before proceeding.
- Public commands `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh info`, `version`, and `manifest` still exit 0 where supported by their usage contracts.
- Public commands `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh info`, `version`, and `manifest` still exit 0.
</acceptance_criteria>
</task>

<task id="04" type="execute">
<title>Generate one package Typst artifact from the baseline render path</title>
<read_first>
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/teaching-design-package/references/format-and-orchestration.md
- skills/teaching-design-package/SKILL.md
- skills/jiaoan-jihua/scripts/jiaoan-jihua.sh
- skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
- .planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-RESEARCH.md
</read_first>
<action>
Implement or extend the public package render path so `teaching-design-package.sh render-package --input <baseline-md> --out-dir <dir>` produces one package Typst artifact named `teaching-design-package.typ`. Prefer using the existing `render-package` command so the package public surface remains clear; add a new subcommand only if the existing command semantics cannot be extended without ambiguity, and then update usage/reference docs. The package Typst must be generated from the baseline Markdown through the script, include both semantic parts in source order, and include provenance in comments or manifest fields showing the baseline Markdown path and generated handoff paths. It must carry the derived total/task hours, generated lesson activity hours, task date ranges, and inferred term metadata from the Phase 28 contract. It may wrap generated `teaching-plan.typ` and `lesson-plans.typ` or directly render from the parsed model, but it must not make Typst the maintained source of truth. Preserve `teaching-plan.typ` and `lesson-plans.typ` split outputs as Phase 29 handoff artifacts.
</action>
<acceptance_criteria>
- `render-package --input "$tmpdir/teaching-design-package-full.md" --out-dir "$tmpdir/render"` exits 0.
- `$tmpdir/render/teaching-design-package.typ` exists.
- `$tmpdir/render/teaching-plan.typ` and `$tmpdir/render/lesson-plans.typ` exist or their nonexistence is documented as a deliberate command split with equivalent Phase 29 handoff paths in manifest; the preferred outcome is that both split Typst files exist.
- `teaching-design-package.typ` contains visible content or generated structure from both `授课进度计划` and `教学设计方案`.
- `teaching-design-package.typ` or its manifest/provenance shows derived `160H`, `40H`, `60H`, `60H`, `5月11日——5月15日`, `5月18日——5月27日`, `5月27日——6月5日`, and `2025-2026学年第二学期`.
- Manifest or provenance evidence links `teaching-design-package.typ` to the source Markdown and module handoffs.
- The generated package Typst is not committed as source; verification outputs remain under `/tmp` or phase evidence.
- `teaching-design-package.sh render-split` still works or the executor records an explicit compatibility decision and docs update.
</acceptance_criteria>
</task>

<task id="05" type="execute">
<title>Document baseline contract changes and Phase 29 PDF handoff slots</title>
<read_first>
- skills/teaching-design-package/SKILL.md
- skills/teaching-design-package/references/format-and-orchestration.md
- .planning/REQUIREMENTS.md
- .planning/ROADMAP.md
- .planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-CONTEXT.md
</read_first>
<action>
Update the package skill documentation only where it currently contradicts the corrected baseline contract. Keep `SKILL.md` concise and put detailed rules in `references/format-and-orchestration.md`. Document that the maintained baseline now uses frontmatter plus `# 授课进度计划` and `# 教学设计方案`, that `teachers` maps to legacy scalar `teacher_name` for generated handoffs, that total/task/activity hours and task date ranges are derived from plan rows plus scheduling defaults, that school year/semester are inferred from `first_teaching_day`, that renderer status/provenance lives in generated manifest or sidecar evidence rather than injected Markdown/YAML sections, and that Phase 29 owns the final `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf` parity gates. Preserve OpenClaw and Hermes Agent adapter notes and do not add runtime-private syntax to the canonical body.
</action>
<acceptance_criteria>
- `format-and-orchestration.md` describes the baseline frontmatter fields, top-level anchors, and generated provenance/status evidence.
- The docs explicitly say the baseline Markdown reference format must not be changed to satisfy parser internals.
- The docs describe `teachers` list to `teacher_name` mapping for generated `jiaoan-jihua-full.md` and `jiaoan-shicao-full.md`.
- The docs describe derived `160H` total, `40H/60H/60H` task totals, activity-hour mapping, task date inference, academic term inference, and non-final behavior on mapping failure.
- The docs explicitly say `total_hours`, `school_year`, `semester`, `daily_hours`, `hour_unit`, `date_display_format`, `date_locale`, `calendar_source`, `holidays`, `makeup_days`, `source_of_truth`, `outputs`, and `validation` do not belong in teacher-maintained package YAML.
- The docs preserve or restate standalone `jiaoan-jihua` and `jiaoan-shicao` compatibility.
- The docs list Phase 29 PDF slots: `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf`, with non-passed status in Phase 28 unless real files exist.
- `SKILL.md` remains portable and still mentions Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
</acceptance_criteria>
</task>

<task id="06" type="execute">
<title>Run Phase 28 black-box verification and finish evidence</title>
<read_first>
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/teaching-design-package/references/format-and-orchestration.md
- .planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-VERIFICATION.md
- .planning/REQUIREMENTS.md
</read_first>
<action>
Run final black-box verification in `/tmp`: syntax check the package script, copy the baseline with `example`, prove the copy is byte-identical to the maintained baseline, run `plan-split`, run `render-package`, inspect generated Markdown handoffs, inspect `teaching-design-package.typ`, inspect manifest/provenance, verify derived hour/date/term facts, verify forbidden YAML/default fields stayed out of the package baseline, verify baseline hash and `git diff -- skills/teaching-design-package/templates/teaching-design-package-full.md --exit-code`, smoke-check public command stability, and record repository cleanliness. Finish `28-VERIFICATION.md` with requirement traceability for TDBR-01 through TDBR-05 and TDBR-12 through TDBR-17, plus explicit Phase 29 PDF slot status. Do not compile or parity-check the three final PDFs unless the implementation incidentally supports local compilation; even then, Phase 28 must not claim Phase 29 parity acceptance.
</action>
<acceptance_criteria>
- `28-VERIFICATION.md` contains sections for `Baseline unchanged check`, `Baseline validator/parser check`, `Derived hours check`, `Derived dates and term check`, `Forbidden YAML/default fields check`, `Teacher metadata mapping`, `Markdown handoff check`, `Package Typst render check`, `Provenance and manifest check`, `Phase 29 PDF slots`, `Standalone compatibility`, `Repository cleanliness`, and `Requirement traceability`.
- `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh` exits 0.
- `example`, `plan-split`, `render-split` or equivalent split path, `render-package`, `manifest`, `info`, and `version` are smoke-checked and recorded.
- Baseline hash before and after implementation is identical.
- `git diff -- skills/teaching-design-package/templates/teaching-design-package-full.md --exit-code` exits 0.
- The generated package Markdown artifact is byte-identical to the baseline or, if intentionally copied to an output path with only path metadata outside the file, the file content diff is clean.
- Generated handoffs preserve the required semantic counts and teacher metadata.
- Generated handoffs and/or manifest prove `160H`, `40H`, `60H`, `60H`, `5月11日——5月15日`, `5月18日——5月27日`, `5月27日——6月5日`, and `2025-2026学年第二学期`.
- Package YAML remains free of forbidden derived/default fields.
- `teaching-design-package.typ` exists and contains content from both semantic halves.
- Manifest or sidecar provenance records `generated_from_markdown: true`.
- PDF slots for `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf` are present with honest non-passed statuses unless actual files exist after explicit commands.
- `git diff --check` exits 0.
- `git diff --cached --check` exits 0 before commit.
- No generated `deliverables/` artifacts are staged.
</acceptance_criteria>
</task>

</tasks>

<verification>
At minimum, execute Phase 28 with these commands and record outcomes in `.planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-VERIFICATION.md`:

```bash
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh

baseline="skills/teaching-design-package/templates/teaching-design-package-full.md"
before_hash="$(shasum -a 256 "$baseline" | awk '{print $1}')"
tmpdir="$(mktemp -d /tmp/tdp-phase28.XXXXXX)"

skills/teaching-design-package/scripts/teaching-design-package.sh example \
  --output "$tmpdir/teaching-design-package-full.md"

diff -u "$baseline" "$tmpdir/teaching-design-package-full.md"

awk '
  /^# 授课进度计划$/ { plan=1; design=0; plan_anchor++; next }
  /^# 教学设计方案$/ { design=1; plan=0; design_anchor++; next }
  plan && /^## / { plan_tasks++ }
  design && /^## 学习任务分析$/ { analysis++ }
  design && /^## 教学活动设计——学习任务/ { activity++ }
  design && /^## 学业评价$/ { evaluation++ }
  END {
    printf "baseline_counts plan_anchor=%d design_anchor=%d plan_tasks=%d analysis=%d activity=%d evaluation=%d\n", plan_anchor+0, design_anchor+0, plan_tasks+0, analysis+0, activity+0, evaluation+0
    exit !(plan_anchor == 1 && design_anchor == 1 && plan_tasks == 3 && analysis == 3 && activity == 3 && evaluation == 3)
  }
' "$baseline"

awk '
  /^# 授课进度计划$/ { in_plan=1; task=""; next }
  /^# 教学设计方案$/ { in_plan=0; next }
  in_plan && /^## / { task=substr($0,4); tasks[++n]=task; total[task]=0; next }
  in_plan && match($0, /-([0-9]+)$/) { h=substr($0,RSTART+1,RLENGTH-1)+0; total[task]+=h; grand+=h }
  END {
    printf "derived_hours total=%d CA6140=%d X62W=%d Z3040=%d\n", grand+0, total[tasks[1]]+0, total[tasks[2]]+0, total[tasks[3]]+0
    exit !(grand == 160 && total[tasks[1]] == 40 && total[tasks[2]] == 60 && total[tasks[3]] == 60)
  }
' "$baseline"

node - <<'NODE'
const fs = require('fs');
const baseline = 'skills/teaching-design-package/templates/teaching-design-package-full.md';
const md = fs.readFileSync(baseline, 'utf8');
const forbidden = ['total_hours','school_year','semester','daily_hours','hour_unit','date_display_format','date_locale','calendar_source','holidays','makeup_days','source_of_truth','outputs','validation'];
const fm = md.split('---')[1] || '';
const present = forbidden.filter((key) => new RegExp(`^${key}:`, 'm').test(fm));
if (present.length) {
  console.error(`forbidden_package_yaml=${present.join(',')}`);
  process.exit(1);
}
console.log('forbidden_package_yaml=none');
NODE

skills/teaching-design-package/scripts/teaching-design-package.sh plan-split \
  --input "$tmpdir/teaching-design-package-full.md" \
  --out-dir "$tmpdir/out"

test -f "$tmpdir/out/jiaoan-jihua-full.md"
test -f "$tmpdir/out/jiaoan-shicao-full.md"
rg -n '^teacher_name: "张老师"|^## CA6140|^## X62W|^## Z3040' "$tmpdir/out/jiaoan-jihua-full.md"
rg -n '^teacher_name: "张老师"|^## 学习任务分析$|^## 教学活动设计——学习任务|^## 学业评价$' "$tmpdir/out/jiaoan-shicao-full.md"
rg -n '160H|40H|60H|5月11日——5月15日|5月18日——5月27日|5月27日——6月5日|2025-2026学年第二学期|##### [0-9]+H' \
  "$tmpdir/out/jiaoan-shicao-full.md"

skills/teaching-design-package/scripts/teaching-design-package.sh render-package \
  --input "$tmpdir/teaching-design-package-full.md" \
  --out-dir "$tmpdir/render"

test -f "$tmpdir/render/teaching-design-package.typ"
rg -n '授课进度计划|教学设计方案|generated_from_markdown|source_markdown' \
  "$tmpdir/render/teaching-design-package.typ" \
  "$tmpdir/render/teaching-design-package-manifest.json"
rg -n '160H|40H|60H|5月11日——5月15日|5月18日——5月27日|5月27日——6月5日|2025-2026学年第二学期|activity_hour_mapping|derived_hours|derived_dates' \
  "$tmpdir/render/teaching-design-package.typ" \
  "$tmpdir/render/teaching-design-package-manifest.json"

skills/teaching-design-package/scripts/teaching-design-package.sh manifest \
  --input "$tmpdir/teaching-design-package-full.md" \
  --out-dir "$tmpdir/render"

rg -n 'teaching-plan.pdf|lesson-plans.pdf|teaching-design-package.pdf|not_run|planned|merge_unavailable|missing_compiler|generated_from_markdown' \
  "$tmpdir/render/teaching-design-package-manifest.json"

after_hash="$(shasum -a 256 "$baseline" | awk '{print $1}')"
test "$before_hash" = "$after_hash"
git diff -- "$baseline" --exit-code

skills/teaching-design-package/scripts/teaching-design-package.sh info
skills/teaching-design-package/scripts/teaching-design-package.sh version
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh info
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh version
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh info
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh version

git diff --check
git diff --cached --check
git status --short
```

If `render-package` also produces split PDFs or a combined PDF locally, record the exact command and file evidence, but keep Phase 29 parity status deferred unless Phase 29 explicitly verifies it.
</verification>

<success_criteria>
- `skills/teaching-design-package/templates/teaching-design-package-full.md` remains byte-identical before and after Phase 28 execution.
- The package path accepts the baseline Markdown with `# 授课进度计划` and `# 教学设计方案` without requiring teacher-facing format changes.
- The workflow produces a copyable package Markdown artifact in the same reference-document shape.
- Generated `jiaoan-jihua-full.md` and `jiaoan-shicao-full.md` are derived from the baseline and preserve semantic split, repeated task structure, and mapped teacher metadata.
- Total hours, task hours, lesson-plan activity hours, task date ranges, and academic year/semester are derived from plan rows, `first_teaching_day`, the built-in teaching-day calendar, and script defaults, with the current baseline values `160H`, `40H/60H/60H`, `5月11日——5月15日`, `5月18日——5月27日`, `5月27日——6月5日`, and `2025-2026学年第二学期`.
- Forbidden derived/default fields are not added to package YAML.
- `render-package` or the chosen public package render path produces `teaching-design-package.typ` from the baseline Markdown and records provenance.
- Manifest/provenance evidence preserves Phase 29 slots for `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf` with honest statuses.
- Standalone `jiaoan-jihua` and `jiaoan-shicao` public interfaces remain stable.
- No generated deliverables are staged or committed.
</success_criteria>
