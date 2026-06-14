---
phase: 29
plan: 01
name: pdf-parity-and-standalone-regression
type: execute
wave: 1
depends_on:
  - phase: 28
    provides: "baseline Markdown ingestion, generated jiaoan handoffs, split Typst, package Typst, and derived scheduling provenance"
files_modified:
  - skills/teaching-design-package/scripts/teaching-design-package.sh
  - skills/teaching-design-package/SKILL.md
  - skills/teaching-design-package/references/format-and-orchestration.md
  - .planning/phases/29-pdf-parity-and-standalone-regression/29-VERIFICATION.md
autonomous: true
requirements:
  - TDBR-06
  - TDBR-07
  - TDBR-08
  - TDBR-09
  - TDBR-10
  - TDBR-11
  - TDBR-12
  - TDBR-13
  - TDBR-14
  - TDBR-15
  - TDBR-16
  - TDBR-17
must_haves:
  truths:
    - D-01 treat Phase 28 `render-package` output as the canonical package starting point.
    - D-02 use Typst CLI as the first-choice PDF compiler and record `missing_compiler` or `failed` with exact stderr when it cannot produce PDFs.
    - D-03 accepted split PDF filenames are `teaching-plan.pdf` and `lesson-plans.pdf`.
    - D-04 accepted combined PDF filename is `teaching-design-package.pdf`.
    - D-05 prefer existing `pdfunite` then `qpdf` merge support; if neither exists, record `merge_unavailable`.
    - D-06 do not commit generated PDFs, Typst smoke outputs, or deliverable artifacts.
    - D-07 teaching-plan parity uses package-generated `jiaoan-jihua-full.md` rendered through standalone `jiaoan-jihua`.
    - D-08 lesson-plan parity uses package-generated `jiaoan-shicao-full.md` rendered through standalone `jiaoan-shicao`.
    - D-09 prove Typst parity after normalizing only documented volatile timestamp/generated-at lines if present.
    - D-10 PDF parity evidence must include PDF existence plus at least one content/layout check when local tools allow it.
    - D-11 same source scope means the Phase 28-generated handoff Markdown, not unrelated old fixtures.
    - D-12 generate package and standalone outputs in separate temp directories for black-box comparison.
    - D-13 combined PDF passes only when an actual `teaching-design-package.pdf` exists after explicit merge/compile command.
    - D-14 combined verification must prove anchors from both halves are present.
    - D-15 combined page count should equal split page-count sum when `pdfinfo` is available.
    - D-16 do not accept stale split PDFs; manifest/provenance must link same-run source, Typst, PDFs, and statuses.
    - D-17 verify final outputs carry `160H`, `40H`, `60H`, `60H`, the three date ranges, and `2025-2026学年第二学期`.
    - D-18 re-check forbidden package YAML fields remain absent.
    - D-19 if PDF text extraction cannot confirm a fact, state that limitation and use Typst/manifest evidence without silently downgrading.
    - D-20 non-final activity-hour mapping fails final PDF acceptance.
    - D-21 keep `jiaoan-jihua.sh` public commands stable.
    - D-22 keep `jiaoan-shicao.sh` public commands stable.
    - D-23 do not require standalone callers to pass package input or package flags.
    - D-24 document any package PDF commands or flags in portable package docs.
    - D-25 missing local tools are explicit evidence.
    - D-26 do not vendor packages, change templates, or retry network automatically after Typst package/network failure.
    - D-27 manifest statuses must reflect real files and exact command outcomes.
    - D-28 run `git diff --check` and `git diff --cached --check`; stage only Phase 29 scope.
---

<objective>
Implement Phase 29 PDF parity and standalone regression for `teaching-design-package`: generate real `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf` artifacts from the Phase 28 baseline render path; prove the split PDFs match standalone `jiaoan-jihua` and `jiaoan-shicao` outputs for the same generated handoffs, allowing only timestamp differences; prove the combined PDF is the accepted teaching-plan PDF followed by the accepted lesson-plan PDF without content loss; keep derived scheduling facts out of package YAML; and preserve the old standalone public interfaces.
</objective>

<threat_model>
Primary risks are false PDF success from Typst-only output, stale merged PDFs, hidden missing-tool failures, parity comparisons against the wrong source scope, over-normalizing differences beyond timestamps, breaking standalone jiaoan commands, losing content during merge, and reintroducing derived/default facts into package YAML. Block these with explicit tool probing, temp-directory isolation, real file-backed manifest statuses, same-handoff black-box standalone renders, strict normalized Typst diffs, PDF existence and page/text checks, combined anchor checks, forbidden-YAML assertions, and public-command regression smoke tests.
</threat_model>

<tasks>

<task id="01" type="execute">
<title>Record Phase 29 preflight, local PDF tools, and current gaps</title>
<read_first>
- AGENTS.md
- .planning/ROADMAP.md
- .planning/STATE.md
- .planning/REQUIREMENTS.md
- .planning/phases/29-pdf-parity-and-standalone-regression/29-CONTEXT.md
- .planning/phases/29-pdf-parity-and-standalone-regression/29-RESEARCH.md
- .planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-VERIFICATION.md
- .planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-01-SUMMARY.md
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/teaching-design-package/templates/teaching-design-package-full.md
</read_first>
<action>
Create `.planning/phases/29-pdf-parity-and-standalone-regression/29-VERIFICATION.md` before implementation edits. In a `/tmp/tdp-phase29.XXXXXX` directory, run the current package render path against `skills/teaching-design-package/templates/teaching-design-package-full.md` and record the pre-fix state: split Typst exists, PDF slots are non-passed, and the three accepted PDF files are not all produced. Probe local tools with `command -v typst`, `command -v pdfunite`, `command -v qpdf`, `command -v pdftotext`, and `command -v pdfinfo`. Record exact paths or `missing`. Do not treat missing optional PDF inspection tools as implementation failure at this task, but do mark which acceptance checks cannot pass until required tools exist.
</action>
<acceptance_criteria>
- `29-VERIFICATION.md` contains `Preflight and tool availability`.
- The section records a temp directory under `/tmp/tdp-phase29.*`.
- The section records exact tool availability for `typst`, `pdfunite`, `qpdf`, `pdftotext`, and `pdfinfo`.
- The section records the current package command used and whether `teaching-plan.typ`, `lesson-plans.typ`, and `teaching-design-package.typ` exist.
- The section records the current statuses for `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf` from `teaching-design-package-manifest.json`.
- If `typst` is missing, the section says split PDF acceptance cannot pass and future PDF statuses must be `missing_compiler`; the executor must still implement honest status handling if possible.
- If both `pdfunite` and `qpdf` are missing, the section says combined PDF acceptance cannot pass and future combined status must be `merge_unavailable`.
- No generated PDF or temp output is staged.
</acceptance_criteria>
</task>

<task id="02" type="execute">
<title>Add explicit PDF compilation and file-backed manifest statuses</title>
<read_first>
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/teaching-design-package/references/format-and-orchestration.md
- skills/teaching-design-package/SKILL.md
- .planning/phases/29-pdf-parity-and-standalone-regression/29-CONTEXT.md
- .planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-VERIFICATION.md
</read_first>
<action>
Extend the existing package render path with an explicit PDF-producing mode, preferably `teaching-design-package.sh render-package --pdf --input <package.md> --out-dir <dir>`, while preserving current `render-package --input <package.md> --out-dir <dir>` Typst-only behavior. Add narrow argument parsing for `--pdf`. After the existing split Typst and `teaching-design-package.typ` generation, compile `teaching-plan.typ` to `teaching-plan.pdf` and `lesson-plans.typ` to `lesson-plans.pdf` using `typst compile`. Use exact file paths in the same output directory. If `typst` is missing, record `missing_compiler` for both split PDFs, keep the command non-successful for final acceptance, and write exact evidence to stderr/manifest without producing placeholders. If a compile command runs but fails or the expected PDF file is missing, record `failed` and include stderr in a sidecar log or verification evidence. Update manifest writing so split PDF status is never `passed` unless the actual PDF exists after the command.
</action>
<acceptance_criteria>
- Existing Typst-only command `render-package --input "$baseline" --out-dir "$dir"` still exits 0 and produces Typst outputs when Phase 28 behavior is otherwise valid.
- New explicit PDF mode is documented in script usage.
- PDF mode attempts `typst compile "$out_dir/teaching-plan.typ" "$out_dir/teaching-plan.pdf"` and `typst compile "$out_dir/lesson-plans.typ" "$out_dir/lesson-plans.pdf"` or equivalent exact-path commands.
- When `typst` is available and compilation succeeds, `teaching-plan.pdf` and `lesson-plans.pdf` exist.
- When `typst` is missing, manifest split PDF statuses are `missing_compiler` and verification records the missing tool; no PDF success is claimed.
- When Typst exits non-zero, manifest split PDF statuses are `failed` and verification records exact stderr.
- Manifest split PDF statuses are `passed` only when the corresponding PDF file exists.
- The implementation does not change `skills/teaching-design-package/templates/teaching-design-package-full.md`.
- `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh` exits 0.
</acceptance_criteria>
</task>

<task id="03" type="execute">
<title>Merge accepted split PDFs into the combined package PDF</title>
<read_first>
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/teaching-design-package/references/format-and-orchestration.md
- .planning/phases/29-pdf-parity-and-standalone-regression/29-CONTEXT.md
</read_first>
<action>
Wire PDF mode to call the existing `merge_combined_pdf()` only after the split PDFs are generated in the same output directory. Keep source order fixed: `teaching-plan.pdf` first, `lesson-plans.pdf` second. Keep optional end-of-term PDFs out of the Phase 29 required merge unless the existing package command already enables them for the input without changing scope. Preserve the current fallback order: `pdfunite`, then `qpdf`. If neither merge tool exists, manifest `combined_output.status` must be `merge_unavailable` with reason `no_pdf_merge_tool`. If a merge tool fails or does not produce `teaching-design-package.pdf`, manifest status must be `failed`. `final_ready` must become true only when review markers are clear, both split PDFs pass, the combined PDF passes, and any existing optional module gate is not blocking.
</action>
<acceptance_criteria>
- PDF mode never merges unless `teaching-plan.pdf` and `lesson-plans.pdf` exist in the same output directory.
- `teaching-design-package.pdf` is produced by `pdfunite teaching-plan.pdf lesson-plans.pdf teaching-design-package.pdf` or `qpdf --empty --pages teaching-plan.pdf lesson-plans.pdf -- teaching-design-package.pdf`.
- Manifest `combined_output.path` points to the same output directory's `teaching-design-package.pdf`.
- Manifest `combined_output.status` is `passed` only when the combined PDF exists after the merge command.
- Manifest records `merge_unavailable` when neither `pdfunite` nor `qpdf` is available.
- Manifest records `failed` when merge command runs but fails or the combined PDF is missing.
- Verification records the merge tool used or the exact unavailable/failure reason.
- No stale pre-existing combined PDF is accepted without same-run split PDF evidence; if the script allows existing combined files, PDF mode must remove or overwrite them before same-run merge.
</acceptance_criteria>
</task>

<task id="04" type="execute">
<title>Build standalone parity harness from the same generated handoffs</title>
<read_first>
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/jiaoan-jihua/scripts/jiaoan-jihua.sh
- skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
- skills/jiaoan-jihua/references/format-and-rendering.md
- skills/jiaoan-shicao/references/format-and-rendering.md
- .planning/phases/29-pdf-parity-and-standalone-regression/29-CONTEXT.md
</read_first>
<action>
Add a deterministic verification harness as either a package script helper subcommand, a repository-local test script, or a documented command sequence in `29-VERIFICATION.md`; prefer the smallest implementation that the execute and verification agents can rerun. The harness must render package outputs to one temp directory, then render standalone outputs from the exact generated `jiaoan-jihua-full.md` and `jiaoan-shicao-full.md` into separate temp directories. Compare package `teaching-plan.typ` against standalone `teaching-plan.typ`, and package `lesson-plans.typ` against standalone `lesson-plans.typ`, using `--expected-typ` when it already performs strict comparison. If timestamp/generated-at lines differ, add an explicit normalizer that strips only those documented volatile lines before `diff -u`; do not normalize layout, content, widths, headings, or derived facts. When `typst` is available, compile the standalone Typst files to PDFs too so package and standalone PDF page/text checks can be compared.
</action>
<acceptance_criteria>
- Harness temp layout separates package output, standalone plan output, and standalone lesson output.
- Standalone plan render uses `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render --input "$pkg/jiaoan-jihua-full.md" --typ "$standalone_plan/teaching-plan.typ"`.
- Standalone lesson render uses `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --input "$pkg/jiaoan-shicao-full.md" --typ "$standalone_lessons/lesson-plans.typ"`.
- Package split Typst and standalone Typst compare equal after only documented volatile timestamp/generated-at normalization.
- Verification records the exact normalizer rule; if no volatile lines exist, it records that raw Typst diff passed or `--expected-typ` passed.
- The harness does not compare the package outputs against unrelated `test/1.10` fixtures as the primary parity target.
- If `typst` is available, standalone PDFs are compiled and exist for PDF-level parity checks.
- If `typst` is unavailable, verification records missing compiler and bounds parity to Typst comparison only.
- No changes are made to standalone script public command names, required inputs, or output semantics.
</acceptance_criteria>
</task>

<task id="05" type="execute">
<title>Verify PDF content, page counts, derived facts, and YAML boundaries</title>
<read_first>
- .planning/phases/28-markdown-baseline-ingestion-and-typst-generation/28-VERIFICATION.md
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/teaching-design-package/scripts/teaching-design-package.sh
- references/scheduling-contract.md
- skills/jiaoan-jihua/references/calendar.json
</read_first>
<action>
Add Phase 29 verification commands that inspect generated artifacts. Use `pdfinfo` when available to record page counts for package split PDFs, standalone split PDFs, and the combined PDF. The combined PDF page count must equal `teaching-plan.pdf` pages plus `lesson-plans.pdf` pages when page-count tooling is available. Use `pdftotext` when available to extract text from `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf`; verify anchors and derived facts in the extracted text when encoding permits. Always verify the same facts in generated handoffs, package Typst, and manifest provenance even if PDF text extraction fails. Re-check package baseline frontmatter to prove `total_hours`, `daily_hours`, `school_year`, `semester`, `hour_unit`, `date_display_format`, `date_locale`, `calendar_source`, `holidays`, `makeup_days`, `source_of_truth`, `outputs`, and `validation` are absent.
</action>
<acceptance_criteria>
- Verification records whether `pdfinfo` is available.
- When `pdfinfo` is available, verification records page counts for `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf`.
- When `pdfinfo` is available, combined page count equals split page-count sum.
- Verification records whether `pdftotext` is available.
- When `pdftotext` can extract text, combined PDF text contains `授课进度计划`, `教学设计方案`, `学习任务分析`, `教学活动设计`, and `学业评价`.
- When extraction can see derived facts, extracted PDF text contains `160H`, `40H`, `60H`, `5月11日——5月15日`, `5月18日——5月27日`, `5月27日——6月5日`, and `2025-2026学年第二学期`.
- If extraction cannot see one of those facts, verification says so explicitly and points to Typst/manifest/handoff evidence for that fact.
- Generated Typst or manifest contains `160H`, task hours `40H/60H/60H`, the three date ranges, `2025-2026学年第二学期`, and `activity_hour_mapping`.
- Package YAML forbidden fields remain absent from `skills/teaching-design-package/templates/teaching-design-package-full.md`.
- No package YAML field is added to make verification easier.
</acceptance_criteria>
</task>

<task id="06" type="execute">
<title>Document PDF workflow and preserve standalone public interfaces</title>
<read_first>
- skills/teaching-design-package/SKILL.md
- skills/teaching-design-package/references/format-and-orchestration.md
- skills/jiaoan-jihua/scripts/jiaoan-jihua.sh
- skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
- .planning/REQUIREMENTS.md
- .planning/phases/29-pdf-parity-and-standalone-regression/29-CONTEXT.md
</read_first>
<action>
Update package documentation for the final PDF-producing path, manifest statuses, local tool requirements, missing-tool behavior, and standalone parity verification. Keep the canonical skill body concise and put detailed commands/status semantics in `references/format-and-orchestration.md`. Preserve runtime portability for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent. Smoke-check old standalone public commands and record their output status in `29-VERIFICATION.md`. Do not require standalone `jiaoan-jihua` or `jiaoan-shicao` callers to use package Markdown, package flags, or package output directories.
</action>
<acceptance_criteria>
- Package docs mention the accepted three PDF outputs by exact filename.
- Package docs explain `typst`, `pdfunite`/`qpdf`, `pdftotext`, and `pdfinfo` roles and missing-tool statuses.
- Package docs describe `render-package --pdf` or the chosen PDF command exactly.
- Package docs state split PDF parity is checked against standalone renders from the same generated handoffs.
- Package docs state timestamp differences are the only allowed parity exception.
- Package docs preserve the rule that `total_hours`, `daily_hours`, `school_year`, `semester`, and other defaults do not belong in package YAML.
- Package docs remain portable and do not introduce runtime-private syntax into canonical guidance.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh info`, `version`, and `manifest` still exit according to existing usage contracts.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh info`, `version`, and `manifest` still exit according to existing usage contracts.
- If standalone scripts are modified at all, verification explains why and proves public command compatibility; preferred outcome is no standalone script changes.
</acceptance_criteria>
</task>

<task id="07" type="execute">
<title>Run final Phase 29 verification and close evidence</title>
<read_first>
- .planning/phases/29-pdf-parity-and-standalone-regression/29-VERIFICATION.md
- .planning/REQUIREMENTS.md
- skills/teaching-design-package/scripts/teaching-design-package.sh
- skills/teaching-design-package/templates/teaching-design-package-full.md
- skills/teaching-design-package/references/format-and-orchestration.md
- skills/teaching-design-package/SKILL.md
</read_first>
<action>
Run final black-box verification from a fresh `/tmp/tdp-phase29.XXXXXX` directory. Record exact commands, statuses, generated artifact paths, PDF tool availability, split PDF compile results, standalone Typst parity, standalone PDF parity where tools allow it, combined PDF merge result, derived fact checks, manifest status checks, standalone public interface regression, repository cleanliness, and requirement traceability. `29-VERIFICATION.md` must make it impossible to confuse missing tools with passed acceptance. If required tools are missing or Typst compilation fails, mark the relevant acceptance criteria not passed with exact evidence instead of claiming completion. If all required tools and checks pass, record the three real PDF artifact paths under `/tmp` and mark TDBR-06 through TDBR-17 satisfied.
</action>
<acceptance_criteria>
- `29-VERIFICATION.md` contains sections named `Preflight and tool availability`, `Package PDF generation`, `Standalone Typst parity`, `Standalone PDF parity`, `Combined PDF verification`, `Derived fact evidence`, `Forbidden YAML/default fields`, `Manifest status evidence`, `Standalone public interface regression`, `Generated artifact locations`, `Repository cleanliness`, and `Requirement traceability`.
- Final verification uses a fresh `/tmp/tdp-phase29.*` directory.
- `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh` exits 0.
- The package PDF command produces real `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf` when required tools are available.
- Manifest statuses for the three accepted PDFs are `passed` only when the files exist.
- Standalone Typst parity passes for plan and lesson outputs with only allowed volatile-line normalization if needed.
- Standalone PDF parity records file existence and page/text checks where local tools allow it.
- Combined PDF verification proves both halves are present and page count equals split sum when `pdfinfo` is available.
- Derived facts `160H`, `40H`, `60H`, `60H`, the three date ranges, and `2025-2026学年第二学期` are verified in Typst/manifest/handoff and in PDF text when extraction permits.
- Package YAML forbidden fields remain absent.
- Standalone public commands remain stable.
- `git diff --check` exits 0.
- `git diff --cached --check` exits 0 before commit.
- Only Phase 29 implementation, docs, and verification files are staged; no generated `/tmp`, PDF, or deliverable files are staged.
</acceptance_criteria>
</task>

</tasks>

<verification>
At minimum, execute Phase 29 with these commands and record outcomes in `.planning/phases/29-pdf-parity-and-standalone-regression/29-VERIFICATION.md`. Adapt only for exact implemented flag/subcommand names if the executor documents why a different package command is safer.

```bash
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh

baseline="skills/teaching-design-package/templates/teaching-design-package-full.md"
tmpdir="$(mktemp -d /tmp/tdp-phase29.XXXXXX)"
pkg="$tmpdir/package"
standalone_plan="$tmpdir/standalone-plan"
standalone_lessons="$tmpdir/standalone-lessons"
mkdir -p "$pkg" "$standalone_plan" "$standalone_lessons"

for tool in typst pdfunite qpdf pdftotext pdfinfo; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '%s=%s\n' "$tool" "$(command -v "$tool")"
  else
    printf '%s=missing\n' "$tool"
  fi
done

skills/teaching-design-package/scripts/teaching-design-package.sh render-package \
  --pdf \
  --input "$baseline" \
  --out-dir "$pkg"

test -f "$pkg/teaching-plan.typ"
test -f "$pkg/lesson-plans.typ"
test -f "$pkg/teaching-design-package.typ"
test -f "$pkg/teaching-design-package-manifest.json"

if command -v typst >/dev/null 2>&1; then
  test -f "$pkg/teaching-plan.pdf"
  test -f "$pkg/lesson-plans.pdf"
fi

if command -v typst >/dev/null 2>&1 && { command -v pdfunite >/dev/null 2>&1 || command -v qpdf >/dev/null 2>&1; }; then
  test -f "$pkg/teaching-design-package.pdf"
fi

LC_ALL=C skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render \
  --input "$pkg/jiaoan-jihua-full.md" \
  --typ "$standalone_plan/teaching-plan.typ" \
  --expected-typ "$pkg/teaching-plan.typ"

LC_ALL=C skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input "$pkg/jiaoan-shicao-full.md" \
  --typ "$standalone_lessons/lesson-plans.typ" \
  --expected-typ "$pkg/lesson-plans.typ"

if command -v typst >/dev/null 2>&1; then
  typst compile "$standalone_plan/teaching-plan.typ" "$standalone_plan/teaching-plan.pdf"
  typst compile "$standalone_lessons/lesson-plans.typ" "$standalone_lessons/lesson-plans.pdf"
fi

rg -n '160H|40H|60H|5月11日——5月15日|5月18日——5月27日|5月27日——6月5日|2025-2026学年第二学期|activity_hour_mapping|derived_hours|derived_dates' \
  "$pkg/jiaoan-jihua-full.md" \
  "$pkg/jiaoan-shicao-full.md" \
  "$pkg/teaching-design-package.typ" \
  "$pkg/teaching-design-package-manifest.json"

node - <<'NODE'
const fs = require('fs');
const baseline = 'skills/teaching-design-package/templates/teaching-design-package-full.md';
const md = fs.readFileSync(baseline, 'utf8');
const fm = (md.match(/^---\n([\s\S]*?)\n---/) || [,''])[1];
const forbidden = ['total_hours','school_year','semester','daily_hours','hour_unit','date_display_format','date_locale','calendar_source','holidays','makeup_days','source_of_truth','outputs','validation'];
const present = forbidden.filter((key) => new RegExp(`^${key}:`, 'm').test(fm));
if (present.length) {
  console.error(`forbidden_package_yaml=${present.join(',')}`);
  process.exit(1);
}
console.log('forbidden_package_yaml=none');
NODE

if command -v pdfinfo >/dev/null 2>&1 && test -f "$pkg/teaching-design-package.pdf"; then
  plan_pages="$(pdfinfo "$pkg/teaching-plan.pdf" | awk '/^Pages:/ {print $2}')"
  lesson_pages="$(pdfinfo "$pkg/lesson-plans.pdf" | awk '/^Pages:/ {print $2}')"
  combined_pages="$(pdfinfo "$pkg/teaching-design-package.pdf" | awk '/^Pages:/ {print $2}')"
  test "$combined_pages" -eq "$((plan_pages + lesson_pages))"
  printf 'pages teaching=%s lesson=%s combined=%s\n' "$plan_pages" "$lesson_pages" "$combined_pages"
fi

if command -v pdftotext >/dev/null 2>&1 && test -f "$pkg/teaching-design-package.pdf"; then
  pdftotext "$pkg/teaching-design-package.pdf" "$tmpdir/combined.txt"
  rg -n '授课进度计划|教学设计方案|学习任务分析|教学活动设计|学业评价' "$tmpdir/combined.txt"
  rg -n '160H|40H|60H|5月11日——5月15日|5月18日——5月27日|5月27日——6月5日|2025-2026学年第二学期' "$tmpdir/combined.txt" || true
fi

skills/teaching-design-package/scripts/teaching-design-package.sh manifest \
  --input "$baseline" \
  --out-dir "$pkg"

rg -n '"teaching_plan_pdf"|"lesson_plans_pdf"|"combined_output"|"status": "passed"|"missing_compiler"|"merge_unavailable"|"failed"' \
  "$pkg/teaching-design-package-manifest.json"

skills/teaching-design-package/scripts/teaching-design-package.sh info
skills/teaching-design-package/scripts/teaching-design-package.sh version
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh info
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh version
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh manifest
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh info
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh version
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh manifest

git diff --check
git diff --cached --check
git status --short
```

If the standalone `manifest` commands require arguments in the current scripts, record their usage output and then run the documented valid manifest invocation instead. Do not treat an argument-required usage exit as an interface regression unless the existing contract promised zero-argument manifest.
</verification>

<success_criteria>
- The package PDF path creates real `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf` artifacts when required local tools are available.
- The combined package PDF is produced from the accepted split PDFs in order and does not drop required content.
- Package `teaching-plan.pdf` matches standalone `jiaoan-jihua` output for the same generated `jiaoan-jihua-full.md`, allowing only timestamp differences.
- Package `lesson-plans.pdf` matches standalone `jiaoan-shicao` output for the same generated `jiaoan-shicao-full.md`, allowing only timestamp differences.
- PDF or Typst/manifest evidence preserves `160H`, `40H/60H/60H`, `5月11日——5月15日`, `5月18日——5月27日`, `5月27日——6月5日`, and `2025-2026学年第二学期`.
- Package YAML still does not contain `total_hours`, `daily_hours`, `school_year`, `semester`, or other derived/default/output/validation fields.
- Missing `typst`, merge tools, `pdftotext`, or `pdfinfo` are recorded explicitly and never reported as passing checks.
- Standalone `jiaoan-jihua` and `jiaoan-shicao` public interfaces remain stable.
- `29-VERIFICATION.md` records exact commands, artifact paths, tool statuses, manifest statuses, and requirement traceability.
- `git diff --check` and `git diff --cached --check` pass before commit.
</success_criteria>
