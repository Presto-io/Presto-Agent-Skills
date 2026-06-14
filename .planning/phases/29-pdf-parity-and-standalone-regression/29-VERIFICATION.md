# Phase 29 Verification: PDF Parity and Standalone Regression

**Phase:** 29 - PDF Parity and Standalone Regression
**Plan:** 01 - pdf-parity-and-standalone-regression
**Started:** 2026-06-14T20:25:15Z

## Preflight and tool availability

### Preflight command

Command:

```bash
tmpdir=$(mktemp -d /tmp/tdp-phase29-preflight.XXXXXX)
pkg="$tmpdir/package"
mkdir -p "$pkg"
baseline="skills/teaching-design-package/templates/teaching-design-package-full.md"

for tool in typst pdfunite qpdf pdftotext pdfinfo; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '%s=%s\n' "$tool" "$(command -v "$tool")"
  else
    printf '%s=missing\n' "$tool"
  fi
done

skills/teaching-design-package/scripts/teaching-design-package.sh render-package \
  --input "$baseline" \
  --out-dir "$pkg"
```

Observed temp directory:

```text
/tmp/tdp-phase29-preflight.59EVNT
```

### Local PDF tools

```text
typst=/opt/homebrew/bin/typst
pdfunite=missing
qpdf=missing
pdftotext=missing
pdfinfo=missing
```

Implications:

- `typst` is available, so split PDF compilation can be attempted and must be reported as `passed` only if real PDF files exist.
- `pdfunite` and `qpdf` are both missing, so a merge-tool-only combined-PDF path cannot pass on this machine. Combined PDF verification must either use another explicit real-PDF path or record `merge_unavailable`.
- `pdftotext` and `pdfinfo` are missing, so PDF text extraction and page-count checks cannot be claimed through those tools. If no alternate local inspection tool is used, verification must bound PDF-level evidence to real file existence plus Typst/manifest/handoff evidence.

### Current package render state before Phase 29 implementation

Output existence after the current Typst-only command:

```text
teaching-plan.typ=exists
lesson-plans.typ=exists
teaching-design-package.typ=exists
teaching-plan.pdf=missing
lesson-plans.pdf=missing
teaching-design-package.pdf=missing
teaching-design-package-manifest.json=exists
```

Manifest evidence:

```text
teaching-plan.pdf status=not_run
lesson-plans.pdf status=not_run
teaching-design-package.pdf status=not_run in provenance phase29_pdf_slots
combined_output.status=failed
combined_output.reason=missing_selected_split_pdfs
```

Conclusion: before Phase 29 implementation, the package path produces split Typst and package Typst only. It does not produce real `teaching-plan.pdf`, `lesson-plans.pdf`, or `teaching-design-package.pdf`, and no PDF acceptance is passed.

## Package PDF generation

Implemented command:

```bash
skills/teaching-design-package/scripts/teaching-design-package.sh render-package \
  --pdf \
  --input skills/teaching-design-package/templates/teaching-design-package-full.md \
  --out-dir /tmp/tdp-phase29-pdf2.HhIUyK/package
```

Verification command:

```bash
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh
```

Result:

```text
bash_syntax=passed
temp_dir=/tmp/tdp-phase29-pdf2.HhIUyK
teaching-plan.pdf=exists
lesson-plans.pdf=exists
teaching-design-package.pdf=exists
```

Generated PDF files:

```text
/tmp/tdp-phase29-pdf2.HhIUyK/package/teaching-plan.pdf
/tmp/tdp-phase29-pdf2.HhIUyK/package/lesson-plans.pdf
/tmp/tdp-phase29-pdf2.HhIUyK/package/teaching-design-package.pdf
```

Split PDF status sidecars:

```text
teaching-plan.pdf status=passed reason=typst_compile tool=/opt/homebrew/bin/typst
lesson-plans.pdf status=passed reason=typst_compile tool=/opt/homebrew/bin/typst
```

Manifest evidence:

```text
teaching_plan_pdf.status=passed
teaching_plan_pdf.reason=typst_compile
teaching_plan_pdf.tool=/opt/homebrew/bin/typst
lesson_plans_pdf.status=passed
lesson_plans_pdf.reason=typst_compile
lesson_plans_pdf.tool=/opt/homebrew/bin/typst
phase29_pdf_slots.teaching_plan_pdf.status=passed
phase29_pdf_slots.lesson_plans_pdf.status=passed
```

Typst-only regression:

```text
render-package --input <baseline> --out-dir <dir>
```

still exits 0, writes `teaching-plan.typ`, `lesson-plans.typ`, and `teaching-design-package.typ`, and leaves `teaching-plan.pdf` and `lesson-plans.pdf` as `not_run`.

## Combined PDF verification

The preferred merge tools from the plan were unavailable during implementation:

```text
pdfunite=missing
qpdf=missing
```

To avoid claiming a Typst-only package artifact as a merged PDF, the script uses a third local, explicit PDF merge path when available: `python3` with the already-installed `fitz` module. This inserts the accepted split PDFs in source order into `teaching-design-package.pdf`.

Combined PDF status sidecar:

```text
teaching-design-package.pdf status=passed reason=python_fitz tool=/opt/homebrew/bin/python3
```

Manifest evidence:

```text
combined_output.path=/tmp/tdp-phase29-pdf2.HhIUyK/package/teaching-design-package.pdf
combined_output.status=passed
combined_output.reason=python_fitz
combined_output.tool=/opt/homebrew/bin/python3
phase29_pdf_slots.teaching_design_package_pdf.status=passed
final_ready=true
```

Stale-file guard: PDF mode removes existing `teaching-plan.pdf`, `lesson-plans.pdf`, `teaching-design-package.pdf`, and their status sidecars before compiling or merging, so a previous combined PDF cannot satisfy the same-run manifest.

## Standalone Typst parity

Fresh parity temp directory:

```text
/tmp/tdp-phase29-parity2.PYLgJA
```

Commands:

```bash
skills/teaching-design-package/scripts/teaching-design-package.sh render-package \
  --pdf \
  --input skills/teaching-design-package/templates/teaching-design-package-full.md \
  --out-dir /tmp/tdp-phase29-parity2.PYLgJA/package

LC_ALL=C skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render \
  --input /tmp/tdp-phase29-parity2.PYLgJA/package/jiaoan-jihua-full.md \
  --typ /tmp/tdp-phase29-parity2.PYLgJA/standalone-plan/teaching-plan.typ \
  --expected-typ /tmp/tdp-phase29-parity2.PYLgJA/package/teaching-plan.typ

LC_ALL=C skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input /tmp/tdp-phase29-parity2.PYLgJA/package/jiaoan-shicao-full.md \
  --typ /tmp/tdp-phase29-parity2.PYLgJA/standalone-lessons/lesson-plans.typ \
  --expected-typ /tmp/tdp-phase29-parity2.PYLgJA/package/lesson-plans.typ
```

Result:

```text
teaching-plan.typ parity=passed
lesson-plans.typ parity=passed
normalizer=none; raw --expected-typ comparison passed
source_scope=generated handoffs from the same package run
```

The primary parity target is not `test/1.10`; it is the package-generated `jiaoan-jihua-full.md` and `jiaoan-shicao-full.md` rendered through the existing standalone scripts.

## Standalone PDF parity

Commands:

```bash
typst compile /tmp/tdp-phase29-parity2.PYLgJA/standalone-plan/teaching-plan.typ \
  /tmp/tdp-phase29-parity2.PYLgJA/standalone-plan/teaching-plan.pdf

typst compile /tmp/tdp-phase29-parity2.PYLgJA/standalone-lessons/lesson-plans.typ \
  /tmp/tdp-phase29-parity2.PYLgJA/standalone-lessons/lesson-plans.pdf
```

PDF inspection tool used:

```text
python3=/opt/homebrew/bin/python3
fitz=available (PyMuPDF 1.27.2.2)
pdfinfo=missing
pdftotext=missing
```

PDF text/page evidence:

```text
pkg_plan.pages=2
pkg_plan.sha_text=4e82213c706cc93dd1554811386fbededb16d3763232834bbc51c17d20c30ab8
standalone_plan.pages=2
standalone_plan.sha_text=4e82213c706cc93dd1554811386fbededb16d3763232834bbc51c17d20c30ab8
plan_text_equal=true

pkg_lessons.pages=25
pkg_lessons.sha_text=7d510056b4393d6b842e32df44de14d71cb1c536402b117dcb858e75598cd763
standalone_lessons.pages=25
standalone_lessons.sha_text=7d510056b4393d6b842e32df44de14d71cb1c536402b117dcb858e75598cd763
lessons_text_equal=true
```

Conclusion: package split PDFs and standalone PDFs generated from the same handoffs have matching page counts and extracted text hashes.

## Derived fact evidence

An implementation-time check found that `jiaoan-shicao` rendered each `学习任务分析` table's task-hour cell from `total_hours` (`160`) instead of per-task `TASK_HOURS[i]`. This would have made the lesson-plan PDF fail the Phase 29 derived fact requirement. Fixed under Rule 1 by changing `skills/jiaoan-shicao/scripts/render_v110_typst.awk` to render `TASK_HOURS[i]` in that table cell.

Post-fix Typst evidence:

```text
lesson-plans.typ:99: [课时], table.cell(colspan: 2)[40H], [起止日期], table.cell(colspan: 2)[5月11日——5月15日]
lesson-plans.typ:407: [课时], table.cell(colspan: 2)[60H], [起止日期], table.cell(colspan: 2)[5月18日——5月27日]
lesson-plans.typ:690: [课时], table.cell(colspan: 2)[60H], [起止日期], table.cell(colspan: 2)[5月27日——6月5日]
teaching-design-package.typ:7: // derived_total_hours: 160H
teaching-design-package.typ:8: // inferred_term: 2025-2026学年第二学期
teaching-design-package.typ:10: // task_1: CA6140卧式车床电气控制线路安装与调试 40H 5月11日——5月15日
teaching-design-package.typ:11: // task_2: X62W万能铣床电气控制线路安装与调试 60H 5月18日——5月27日
teaching-design-package.typ:12: // task_3: Z3040摇臂钻床电气控制线路安装与调试 60H 5月27日——6月5日
```

Generated handoff and manifest evidence:

```text
jiaoan-shicao-full.md:7: total_hours: "160H"
jiaoan-shicao-full.md:11: academic_term: "2025-2026学年第二学期"
jiaoan-shicao-full.md:21: 起止日期：5月11日——5月15日
jiaoan-shicao-full.md:434: 起止日期：5月18日——5月27日
jiaoan-shicao-full.md:798: 起止日期：5月27日——6月5日
jiaoan-shicao-full.md:1157: <!-- activity_hour_mapping
teaching-design-package-manifest.json:43: "total_hours": "160H"
teaching-design-package-manifest.json:47: "hours": "40H"
teaching-design-package-manifest.json:51: "hours": "60H"
teaching-design-package-manifest.json:55: "hours": "60H"
teaching-design-package-manifest.json:77: "range": "5月11日——5月15日"
teaching-design-package-manifest.json:81: "range": "5月18日——5月27日"
teaching-design-package-manifest.json:85: "range": "5月27日——6月5日"
teaching-design-package-manifest.json:88: "inferred_term": "2025-2026学年第二学期"
teaching-design-package-manifest.json:89: "activity_hour_mapping": "same-name or same-order from # 授课进度计划 rows"
```

Combined PDF text extraction via PyMuPDF found the required anchors and derived facts. Typst/PDF extraction normalizes CJK spacing, so date and term strings appear with inserted spaces:

```text
combined_anchor[授课进度计划]=true
combined_anchor[教学设计方案]=true
combined_anchor[学习任务分析]=true
combined_anchor[教学活动设计]=true
combined_anchor[学业评价]=true
combined_anchor[160]=true
combined_anchor[40H]=true
combined_anchor[60H]=true
combined_anchor[5 月11 日——5 月15 日]=true
combined_anchor[5 月18 日——5 月27 日]=true
combined_anchor[5 月27 日——6 月5 日]=true
combined_anchor[2025-2026 学年第二学期]=true
```

## Forbidden YAML/default fields

Command:

```bash
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
```

Result:

```text
forbidden_package_yaml=none
```

## Manifest status evidence

Final observed manifest state from `/tmp/tdp-phase29-parity2.PYLgJA/package/teaching-design-package-manifest.json`:

```text
teaching_plan_pdf.status=passed
teaching_plan_pdf.reason=typst_compile
teaching_plan_pdf.tool=/opt/homebrew/bin/typst
lesson_plans_pdf.status=passed
lesson_plans_pdf.reason=typst_compile
lesson_plans_pdf.tool=/opt/homebrew/bin/typst
combined_output.status=passed
combined_output.reason=python_fitz
combined_output.tool=/opt/homebrew/bin/python3
final_ready=true
```

The provenance `phase29_pdf_slots` mirrors the final file-backed statuses for `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf`.

## Standalone public interface regression

Commands:

```bash
skills/teaching-design-package/scripts/teaching-design-package.sh info
skills/teaching-design-package/scripts/teaching-design-package.sh version
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh info
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh version
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh manifest
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh info
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh version
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh manifest
```

Result:

```text
teaching-design-package info=passed
teaching-design-package version=passed
jiaoan-jihua info=passed
jiaoan-jihua version=passed
jiaoan-jihua manifest=passed
jiaoan-shicao info=passed
jiaoan-shicao version=passed
jiaoan-shicao manifest=passed
```

No standalone command names, required inputs, or output semantics were changed. `jiaoan-shicao` was modified only to render each task's own `课时` value in the `学习任务分析` table, preserving the existing public render command and correcting generated content.
