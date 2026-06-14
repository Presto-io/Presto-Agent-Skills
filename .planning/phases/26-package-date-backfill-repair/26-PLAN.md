---
phase: 26
plan: 01
name: package-date-backfill-repair
type: execute
wave: 1
depends_on:
  - phase: 25
    provides: "v1.11 package command regression, manifest truthfulness, and documentation-index baseline"
files_modified:
  - skills/teaching-design-package/scripts/teaching-design-package.sh
  - .planning/phases/26-package-date-backfill-repair/26-VERIFICATION.md
autonomous: true
requirements:
  - TDPR-01
  - TDPR-02
  - TDPR-03
  - TDPR-06
must_haves:
  truths:
    - D-01 parse package-level `## 调度证据` as the source of concrete date evidence; do not invent dates inside `jiaoan-shicao`.
    - D-02 fill the generated package handoff file `jiaoan-shicao-full.md` before `jiaoan-shicao` rendering.
    - D-03 only fill blank `起止日期：` when a concrete `YYYY-MM-DD - YYYY-MM-DD` range can be traced to package scheduling evidence.
    - D-04 preserve the existing `jiaoan-shicao-full.md` template structure and teacher-facing Chinese headings.
    - D-05 keep package evidence, source pointers, hour-consumption evidence, and review markers visible in package Markdown or adjacent manifest/status evidence.
    - D-06 do not silently guess when scheduling evidence is missing, conflicting, uncertain, or exhausted; keep blank/review-needed output and record the issue.
    - D-07 prefer direct `lesson:*` evidence for lesson fragments, and use `task:1/*` task evidence only when `## 实操教案` explicitly says the date derives from that task pointer.
    - D-08 unresolved review markers must continue to block final readiness; filling a date must not make `final_ready` true by itself.
    - D-09 preserve public `teaching-design-package.sh` commands: `example`, `plan-split`, `render-split`, `plan-end-of-term`, `render-end-of-term`, `render-package`, `manifest`, `info`, and `version`.
    - D-10 preserve standalone `jiaoan-shicao` and `jiaoan-jihua` behavior; Phase 26 is a package handoff repair.
    - D-11 do not introduce a broad global scheduling library for this repair.
    - D-12 do not stage or commit generated `deliverables/` artifacts.
    - D-13 regression must run the package path: `example` -> `plan-split` or `render-split` -> inspect `jiaoan-shicao-full.md`.
    - D-14 keep the before-fix failure mode understandable in Phase 26 evidence: package evidence had concrete dates while handoff Markdown was blank.
    - D-15 Markdown, Typst, and PDF evidence must be recorded honestly; PDF success requires an actual successful compile and output file.
    - D-16 the date assertion must prove generated `起止日期：` is non-empty and review markers are not dropped.
    - D-17 use `/tmp` or phase-local evidence paths for generated artifacts, never committed `deliverables/`.
---

<objective>
Implement a narrow `teaching-design-package` package-side handoff fix: parse auditable date ranges from package Markdown `## 调度证据`, backfill blank `起止日期：` lines in generated `jiaoan-shicao-full.md`, preserve review markers and public command surfaces, and verify the affected package path through Markdown, Typst, and honest PDF compilation evidence.
</objective>

<threat_model>
Primary risks are silent date invention, review-marker loss, public command regression, and false PDF readiness. Block silent invention by accepting only explicit `YYYY-MM-DD - YYYY-MM-DD` ranges from `## 调度证据` rows tied to `lesson:*` or declared `task:*` source pointers. Block review-marker loss by leaving `## 复核标记`, manifest `review_markers`, and `final_ready` semantics intact. Block public-command regression with usage-surface checks and black-box package commands. Block false PDF readiness by recording `missing_compiler`, `failed`, or real compiler output when Typst/PDF compilation cannot produce a file.
</threat_model>

<tasks>

<task id="01" type="execute">
<title>Reproduce the blank-date package handoff and define the acceptance evidence</title>
<read_first>
- .planning/phases/26-package-date-backfill-repair/26-CONTEXT.md
- .planning/ROADMAP.md
- .planning/REQUIREMENTS.md
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/jiaoan-shicao/templates/jiaoan-shicao-full.md
</read_first>
<action>
Create `.planning/phases/26-package-date-backfill-repair/26-VERIFICATION.md` during execution and record the pre-fix reproduction: run `teaching-design-package.sh example`, run `plan-split`, and capture that the package Markdown `## 调度证据` contains concrete `YYYY-MM-DD - YYYY-MM-DD` rows while generated `jiaoan-shicao-full.md` has blank `起止日期：` lines. Use a `mktemp -d /tmp/tdp-phase26.XXXXXX` directory and keep generated files out of `deliverables/`.
</action>
<acceptance_criteria>
- `26-VERIFICATION.md` contains a `Pre-fix reproduction` section.
- The reproduction section records the exact `example` and `plan-split` commands, exit statuses, temporary output directory pattern, and checked files.
- The reproduction evidence includes at least one concrete package evidence date matching `[0-9]{4}-[0-9]{2}-[0-9]{2} - [0-9]{4}-[0-9]{2}-[0-9]{2}`.
- The reproduction evidence records the blank `^起止日期：$` state in generated `jiaoan-shicao-full.md` before implementation.
- `git status --short` may show pre-existing untracked `deliverables/`, but `git diff --cached --name-only` does not include `deliverables/`.
</acceptance_criteria>
</task>

<task id="02" type="execute">
<title>Add conservative package Markdown date extraction for shicao handoff</title>
<read_first>
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/teaching-design-package/references/format-and-orchestration.md
- references/scheduling-contract.md
- test/1.11/teaching-design-package/fixture-source.md
- test/1.11/teaching-design-package/expected-review.md
</read_first>
<action>
Update `skills/teaching-design-package/scripts/teaching-design-package.sh` near `write_shicao_scaffold` with package-local helper logic that reads the input package Markdown, isolates the `## 调度证据` table, and extracts rows with `Source` plus concrete `起止日期` values. Use structured `awk`/shell parsing scoped to this Markdown table rather than broad whole-file greps. The extractor must accept ranges formatted exactly like `2026-05-11 - 2026-05-11`, ignore rows whose date cell is blank or non-concrete, and preserve enough source-pointer information to trace back to `lesson:*` or `task:*` evidence. Do not change public command names, flags, output filenames, or standalone `jiaoan-shicao`/`jiaoan-jihua` scripts.
</action>
<acceptance_criteria>
- `skills/teaching-design-package/scripts/teaching-design-package.sh` still defines `write_shicao_scaffold()` and `cmd_plan_split()` with the same public call flow.
- The script contains helper logic that limits extraction to the `## 调度证据` section and table rows below it.
- The helper rejects non-concrete date cells and only emits values matching `YYYY-MM-DD - YYYY-MM-DD`.
- The helper preserves source pointers such as `` `lesson:1/activity:1` `` and `` `task:1/stage:1/row:1` `` for traceability.
- `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh` exits 0.
- `skills/teaching-design-package/scripts/teaching-design-package.sh info` and `version` still exit 0.
</acceptance_criteria>
</task>

<task id="03" type="execute">
<title>Backfill blank `起止日期：` in generated `jiaoan-shicao-full.md` without weakening review gates</title>
<read_first>
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/jiaoan-shicao/templates/jiaoan-shicao-full.md
- skills/jiaoan-shicao/references/format-and-rendering.md
- skills/jiaoan-shicao/scripts/render_v110_typst.awk
- skills/teaching-design-package/references/format-and-orchestration.md
- references/scheduling-contract.md
</read_first>
<action>
Change `write_shicao_scaffold "$package_md" "$out"` so it still starts from the existing `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md`, then fills blank lines that are exactly `起止日期：` only when package evidence resolves a concrete range. Prefer direct `lesson:*` rows referenced by `## 实操教案` teaching activity pointers; when the `## 实操教案` learning-task analysis explicitly says `起止日期：由 \`task:1/*\` 调度证据推导`, aggregate matching `task:1/` evidence into one range using the earliest start date and latest end date from concrete rows. If no concrete range is available or package review markers indicate unresolved scheduling uncertainty, leave the field blank or append a review-needed marker instead of guessing. Preserve `review_marker_state`, manifest `review_markers`, `combined_output`, and `final_ready` behavior.
</action>
<acceptance_criteria>
- `plan-split` writes `${OUT_DIR}/jiaoan-shicao-full.md` with at least one non-empty `起止日期：YYYY-MM-DD - YYYY-MM-DD` line for the package example.
- No generated `起止日期：` line is filled from a non-concrete or missing date cell.
- The implementation does not edit `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`, `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`, or their public command surfaces.
- `review_marker_state()` output and manifest `review_markers` semantics remain unchanged for existing package-level `## 复核标记`.
- If package `## 复核标记` contains unresolved text other than `无`, generated manifest `final_ready` remains `false`.
- The generated `jiaoan-shicao-full.md` keeps the `## 学习任务分析`, `## 教学活动设计`, and `## 学业评价` structure.
</acceptance_criteria>
</task>

<task id="04" type="execute">
<title>Verify package split/render path through Markdown and Typst artifacts</title>
<read_first>
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
- skills/jiaoan-shicao/scripts/render_v110_typst.awk
- skills/jiaoan-jihua/scripts/jiaoan-jihua.sh
- .planning/phases/26-package-date-backfill-repair/26-VERIFICATION.md
</read_first>
<action>
Run black-box package verification in a temporary directory: generate `package.md` with `example`, run `plan-split`, assert generated `jiaoan-shicao-full.md` has no blank `起止日期：` line and at least one concrete filled date, then run `render-split` and assert `teaching-plan.typ` and `lesson-plans.typ` exist. Record all commands, exit statuses, checked files, and date-check results in `26-VERIFICATION.md`.
</action>
<acceptance_criteria>
- `skills/teaching-design-package/scripts/teaching-design-package.sh example --output "$tmpdir/package.md"` exits 0.
- `skills/teaching-design-package/scripts/teaching-design-package.sh plan-split --input "$tmpdir/package.md" --out-dir "$tmpdir/out"` exits 0.
- An assertion equivalent to `awk '/^起止日期：/{ if ($0 ~ /^起止日期：[[:space:]]*$/) empty++; else filled++ } END { exit !(filled >= 1 && empty == 0) }' "$tmpdir/out/jiaoan-shicao-full.md"` exits 0.
- `skills/teaching-design-package/scripts/teaching-design-package.sh render-split --input "$tmpdir/package.md" --out-dir "$tmpdir/render"` exits 0.
- `$tmpdir/render/teaching-plan.typ` exists.
- `$tmpdir/render/lesson-plans.typ` exists.
- `rg -n "^起止日期：|2026-[0-9]{2}-[0-9]{2}" "$tmpdir/out/jiaoan-shicao-full.md" "$tmpdir/render/lesson-plans.typ"` exits 0 and is recorded.
</acceptance_criteria>
</task>

<task id="05" type="execute">
<title>Compile PDF evidence honestly and finish Phase 26 verification</title>
<read_first>
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/teaching-design-package/references/format-and-orchestration.md
- .planning/phases/26-package-date-backfill-repair/26-VERIFICATION.md
- .planning/REQUIREMENTS.md
</read_first>
<action>
Record PDF verification for the affected package path in `26-VERIFICATION.md`. If `typst` is available, compile at least `$tmpdir/render/lesson-plans.typ` to `$tmpdir/render/lesson-plans.pdf` and record the exact command, exit status, stderr/stdout summary, and file existence. Also compile `$tmpdir/render/teaching-plan.typ` when feasible. If `typst` is missing or compilation fails, record `missing_compiler` or `failed` with the real command result; do not mark PDF success. Finish with `git diff --check`, `git status --short`, and explicit TDPR-01/TDPR-02/TDPR-03/TDPR-06 traceability.
</action>
<acceptance_criteria>
- `26-VERIFICATION.md` contains sections for `Markdown handoff date check`, `Typst render check`, `PDF compile check`, `Review marker and manifest check`, `Public command stability`, `Repository cleanliness`, and `Requirement traceability`.
- If `command -v typst` succeeds, `typst compile "$tmpdir/render/lesson-plans.typ" "$tmpdir/render/lesson-plans.pdf"` is run and `lesson-plans.pdf` must exist before PDF status is recorded as passed.
- If PDF compilation fails, `26-VERIFICATION.md` records the actual failing command and status as `failed`; if `typst` is absent, it records `missing_compiler`.
- `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh` exits 0 after all edits.
- Public commands `example`, `plan-split`, `render-split`, `manifest`, `info`, and `version` for `teaching-design-package.sh` are smoke-checked without renamed flags or output filenames.
- `git diff --check` exits 0.
- `git status --short` shows only intentional source/planning changes plus any pre-existing untracked `deliverables/`; `deliverables/` is not staged.
- `26-VERIFICATION.md` maps TDPR-01, TDPR-02, TDPR-03, and TDPR-06 to passing or honestly failed evidence.
</acceptance_criteria>
</task>

</tasks>

<verification>
At minimum, execute Phase 26 with these verification commands and record outcomes in `.planning/phases/26-package-date-backfill-repair/26-VERIFICATION.md`:

```bash
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh

tmpdir="$(mktemp -d /tmp/tdp-phase26.XXXXXX)"
skills/teaching-design-package/scripts/teaching-design-package.sh example --output "$tmpdir/package.md"
skills/teaching-design-package/scripts/teaching-design-package.sh plan-split --input "$tmpdir/package.md" --out-dir "$tmpdir/out"

awk '/^起止日期：/{
  if ($0 ~ /^起止日期：[[:space:]]*$/) empty++;
  else if ($0 ~ /^起止日期：[[:space:]]*[0-9]{4}-[0-9]{2}-[0-9]{2} - [0-9]{4}-[0-9]{2}-[0-9]{2}[[:space:]]*$/) filled++;
}
END { exit !(filled >= 1 && empty == 0) }' "$tmpdir/out/jiaoan-shicao-full.md"

skills/teaching-design-package/scripts/teaching-design-package.sh render-split --input "$tmpdir/package.md" --out-dir "$tmpdir/render"
test -f "$tmpdir/render/teaching-plan.typ"
test -f "$tmpdir/render/lesson-plans.typ"
rg -n "^起止日期：|2026-[0-9]{2}-[0-9]{2}" "$tmpdir/out/jiaoan-shicao-full.md" "$tmpdir/render/lesson-plans.typ"

if command -v typst >/dev/null 2>&1; then
  typst compile "$tmpdir/render/lesson-plans.typ" "$tmpdir/render/lesson-plans.pdf"
  test -f "$tmpdir/render/lesson-plans.pdf"
  typst compile "$tmpdir/render/teaching-plan.typ" "$tmpdir/render/teaching-plan.pdf"
  test -f "$tmpdir/render/teaching-plan.pdf"
else
  printf 'PDF status: missing_compiler (typst not found)\n'
fi

skills/teaching-design-package/scripts/teaching-design-package.sh manifest --input "$tmpdir/package.md" --out-dir "$tmpdir/render"
skills/teaching-design-package/scripts/teaching-design-package.sh info
skills/teaching-design-package/scripts/teaching-design-package.sh version
git diff --check
git status --short
```

The PDF block is not allowed to report success unless each expected PDF file exists after `typst compile`. If a compile fails, preserve the real failure output in `26-VERIFICATION.md` and keep PDF status failed.
</verification>

<success_criteria>
- `teaching-design-package.sh plan-split` produces `jiaoan-shicao-full.md` with concrete package-derived `起止日期：YYYY-MM-DD - YYYY-MM-DD` values when source lesson-plan dates are blank and package scheduling evidence is concrete.
- The package Markdown and manifest/status evidence still expose scheduling source pointers, hour-consumption evidence, and unresolved review markers.
- Public commands, flags, and output filenames remain unchanged for `teaching-design-package`, `jiaoan-shicao`, and `jiaoan-jihua`.
- Phase 26 verification records Markdown, Typst, and PDF outcomes honestly, including real PDF compiler failures or `missing_compiler` if applicable.
- No generated `deliverables/` artifacts are staged or committed.
</success_criteria>
