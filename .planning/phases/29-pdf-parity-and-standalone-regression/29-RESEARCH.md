# Phase 29 Research: PDF Parity and Standalone Regression

**Phase:** 29 - PDF Parity and Standalone Regression
**Command:** `/gsd:plan-phase 29`
**Researched:** 2026-06-15
**Status:** Complete

## Scope

Phase 29 is internal repository research for planning only. No external research is required because the work is constrained to existing package scripts, standalone jiaoan renderers, local PDF tooling, manifests, and Phase 28 evidence.

This phase covers the remaining v1.13 PDF and compatibility requirements:

- TDBR-06: generate `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf`;
- TDBR-07: prove the combined PDF is the accepted plan PDF followed by the accepted lesson PDF, without content loss;
- TDBR-08: prove the package teaching-plan PDF matches standalone `jiaoan-jihua` for the same handoff, allowing only timestamp differences;
- TDBR-09: prove the package lesson-plan PDF matches standalone `jiaoan-shicao` for the same handoff, allowing only timestamp differences;
- TDBR-10 and TDBR-11: keep the old standalone public interfaces stable;
- TDBR-12 through TDBR-17: carry the Phase 28 derived scheduling facts into Typst/PDF/manifest evidence without putting defaults back into package YAML.

## Local Findings

### Phase 28 Handoff State

Phase 28 already made `skills/teaching-design-package/templates/teaching-design-package-full.md` the baseline input and proved the baseline stays byte-identical. The current package script can generate:

- `jiaoan-jihua-full.md`;
- `jiaoan-shicao-full.md`;
- `teaching-plan.typ`;
- `lesson-plans.typ`;
- `teaching-design-package.typ`;
- `teaching-design-package-manifest.json`.

The manifest already contains PDF slots for `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf`, but Phase 28 intentionally leaves them non-passed until real PDF commands run.

### Existing Implementation Points

`skills/teaching-design-package/scripts/teaching-design-package.sh` already has useful hooks:

- `cmd_render_package()` produces split Typst and package Typst for baseline package Markdown.
- `write_manifest()` records Typst/PDF status and final readiness.
- `status_for_file()` marks a status as `passed` only when a file exists.
- `merge_combined_pdf()` already tries `pdfunite` first and `qpdf` second, then reports `merge_unavailable:no_pdf_merge_tool`.
- `write_baseline_provenance_json()` records source Markdown, generated handoffs, derived hours, dates, inferred term, and Phase 29 PDF slots.

The natural Phase 29 implementation is a small extension of the existing package command surface, not a separate PDF orchestration framework.

### Standalone Renderer Contracts

The standalone scripts keep these public commands:

- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`: `example`, `render`, `manifest`, `info`, `version`.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`: `example`, `render`, `manifest`, `info`, `version`.

Both `render` commands accept `--input`, `--typ`, and `--expected-typ`. The `--expected-typ` behavior is useful for black-box parity because the package split Typst can be compared against standalone-rendered Typst from the exact same generated handoff.

Phase 29 should not require standalone callers to pass package Markdown or package-only flags.

### Tooling Boundary

Required tools for a fully passing Phase 29 acceptance path:

- `typst` to compile `.typ` into real `.pdf`;
- `pdfunite` or `qpdf` to merge the accepted split PDFs into `teaching-design-package.pdf`;
- at least one PDF inspection path for content/page evidence, preferably `pdftotext` and `pdfinfo`.

Missing tools must be explicit evidence, not hidden assumptions:

- missing `typst`: record `missing_compiler` and do not claim split PDF success;
- Typst compile failure: record `failed` with exact stderr and expected output path;
- missing `pdfunite` and `qpdf`: record `merge_unavailable` and do not claim combined PDF success;
- missing `pdftotext` or `pdfinfo`: record unavailable checks and keep claims bounded to Typst parity, PDF file existence, and whichever other checks passed.

If Typst needs to download `@preview/cuti:0.2.1` or any other package and the environment is offline, the executor must record the exact failure and stop the final acceptance path. It must not vendor packages, edit templates, or retry network access without explicit user approval.

## Planning Decisions

1. Add explicit local tool probing before PDF work. Record tool paths or `missing` for `typst`, `pdfunite`, `qpdf`, `pdftotext`, and `pdfinfo`.
2. Extend the existing package path with an explicit PDF-producing mode, preferably `teaching-design-package.sh render-package --pdf --input <md> --out-dir <dir>`, while preserving the current Typst-only default behavior.
3. Compile `teaching-plan.typ` to `teaching-plan.pdf` and `lesson-plans.typ` to `lesson-plans.pdf` with `typst compile`.
4. Record split PDF statuses in the manifest as `passed`, `missing_compiler`, or `failed` based on actual files and command outcomes.
5. Merge only accepted split PDFs, in order: `teaching-plan.pdf` first, `lesson-plans.pdf` second.
6. Treat `teaching-design-package.pdf` as accepted only when the actual file exists after `pdfunite` or `qpdf`.
7. Build parity from the exact generated handoffs:
   - render `package/jiaoan-jihua-full.md` through standalone `jiaoan-jihua.sh render` into a separate temp directory;
   - render `package/jiaoan-shicao-full.md` through standalone `jiaoan-shicao.sh render` into a separate temp directory;
   - normalize only explicit volatile timestamp/generated-at lines if present;
   - compare normalized package split Typst against normalized standalone Typst;
   - compile both sides to PDF when `typst` is available.
8. Do not use unrelated `test/1.10` fixtures as the primary parity target. They may be an optional smoke regression only.
9. Verify derived facts in the strongest available layers:
   - generated handoffs and package Typst always;
   - manifest provenance always;
   - PDF text when `pdftotext` can extract the strings.
10. Verify combined PDF content with anchors from both halves and page count equality when tools are available.
11. Keep generated PDFs and temp artifacts under `/tmp/tdp-phase29.*`; commit only source/docs/tests and Phase 29 evidence text.
12. Finish `29-VERIFICATION.md` with honest status tables and exact commands, including missing-tool states if any tool is unavailable.

## Suggested Verification Shape

Phase 29 execution should use a temp directory similar to:

```bash
tmpdir="$(mktemp -d /tmp/tdp-phase29.XXXXXX)"
pkg="$tmpdir/package"
standalone_plan="$tmpdir/standalone-plan"
standalone_lessons="$tmpdir/standalone-lessons"
mkdir -p "$pkg" "$standalone_plan" "$standalone_lessons"
```

Primary package command:

```bash
skills/teaching-design-package/scripts/teaching-design-package.sh render-package \
  --pdf \
  --input skills/teaching-design-package/templates/teaching-design-package-full.md \
  --out-dir "$pkg"
```

Primary parity commands:

```bash
LC_ALL=C skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render \
  --input "$pkg/jiaoan-jihua-full.md" \
  --typ "$standalone_plan/teaching-plan.typ" \
  --expected-typ "$pkg/teaching-plan.typ"

LC_ALL=C skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input "$pkg/jiaoan-shicao-full.md" \
  --typ "$standalone_lessons/lesson-plans.typ" \
  --expected-typ "$pkg/lesson-plans.typ"
```

If `--expected-typ` does not normalize timestamp lines itself, the executor should add a small helper that strips only documented volatile generated-at/comment lines before running `diff -u`.

PDF inspection should prefer:

```bash
pdfinfo "$pkg/teaching-plan.pdf"
pdfinfo "$pkg/lesson-plans.pdf"
pdfinfo "$pkg/teaching-design-package.pdf"
pdftotext "$pkg/teaching-design-package.pdf" "$tmpdir/combined.txt"
```

When extraction works, required anchors include:

- `授课进度计划`;
- `教学设计方案`;
- `学习任务分析`;
- `教学活动设计`;
- `学业评价`;
- `160H`;
- `40H`;
- `60H`;
- `5月11日——5月15日`;
- `5月18日——5月27日`;
- `5月27日——6月5日`;
- `2025-2026学年第二学期`.

## Risks for Execute Phase

- Compiling split PDFs without updating manifest statuses can make files real but evidence stale.
- Merging stale PDFs from a previous run would create false combined evidence. The package command must generate Typst/PDF/manifest in one output directory and verify paths point to the same directory.
- PDF text extraction can fail because of fonts or encoding. That is a bounded verification gap, not permission to imply text-level PDF evidence.
- Adding a PDF flag must not break the existing `render-package --input --out-dir` Typst-only behavior.
- Changing standalone renderer public commands to make parity easier would violate Phase 29.
- Reintroducing `total_hours`, `daily_hours`, `school_year`, or `semester` into package YAML would violate v1.13 even if PDFs look right.

## RESEARCH COMPLETE
