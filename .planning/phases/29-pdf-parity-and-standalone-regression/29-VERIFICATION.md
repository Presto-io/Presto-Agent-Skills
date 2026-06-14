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
