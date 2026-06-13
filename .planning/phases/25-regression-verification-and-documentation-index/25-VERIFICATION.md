# Phase 25 Verification

**Phase:** 25 - Regression Verification and Documentation Index
**Date:** 2026-06-14

## Standalone command regression

Passed checks:
- `bash -n skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh example --output <tmp>/jiaoan-jihua-full.md`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render --input test/1.10/电气设备控制线路安装与调试授课计划.md --typ <tmp>/jiaoan-jihua.typ --expected-typ test/1.10/电气设备控制线路安装与调试授课计划.typ`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh manifest`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh info`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh version`
- `bash -n skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example --output <tmp>/jiaoan-shicao-full.md --calendar-output <tmp>/calendar.json`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --input test/1.10/电气设备控制线路安装与调试教案.md --typ <tmp>/jiaoan-shicao.typ --expected-typ test/1.10/电气设备控制线路安装与调试教案.typ`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh manifest`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh info`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh version`
- `bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh example --output <tmp>/end-of-term-source.json`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh validate --input <tmp>/end-of-term-source.json`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh markdown --input <tmp>/end-of-term-source.json --output <tmp>/end-of-term-full.md`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh render --input <tmp>/end-of-term-full.md --workdir <tmp>/end-of-term-output`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh verify --workdir <tmp>/end-of-term-output`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh manifest`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh info`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh version`
- `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/scripts/teaching-design-package.sh example --output <tmp>/teaching-design-package-full.md`
- `skills/teaching-design-package/scripts/teaching-design-package.sh plan-split --input <tmp>/teaching-design-package-full.md --out-dir <tmp>/tdp-split`
- `skills/teaching-design-package/scripts/teaching-design-package.sh render-split --input <tmp>/teaching-design-package-full.md --out-dir <tmp>/tdp-render`
- `skills/teaching-design-package/scripts/teaching-design-package.sh manifest --input <tmp>/teaching-design-package-full.md --out-dir <tmp>/tdp-render`
- `skills/teaching-design-package/scripts/teaching-design-package.sh info`
- `skills/teaching-design-package/scripts/teaching-design-package.sh version`

Results:
- `jiaoan-jihua` and `jiaoan-shicao` both passed strict v1.10 `--expected-typ` comparisons.
- `end-of-term-teaching-materials` returned explicit manifest evidence for `validation: ok`, `final_ready: true`, and abnormal-review behavior with `final_ready: false` plus unresolved-review evidence.
- `teaching-design-package` produced split Typst outputs and a manifest; `combined_output.status` was `failed` in the checked run because no actual `teaching-design-package.pdf` existed in the output directory.

## Package manifest semantics

Passed checks:
- `python3 -m json.tool test/1.11/teaching-design-package/expected-manifest.json`
- `python3 -m json.tool test/1.11/teaching-design-package/expected-end-of-term-disabled-manifest.json`
- `python3 -m json.tool test/1.11/teaching-design-package/expected-end-of-term-enabled-manifest.json`
- `python3 -m json.tool test/1.11/teaching-design-package/expected-end-of-term-blocked-review-manifest.json`
- `python3 -m json.tool test/1.11/teaching-design-package/expected-combined-merge-unavailable-manifest.json`

Status assertions observed:
- `expected-end-of-term-disabled-manifest.json` contains `disabled` and `final_ready` coverage.
- `expected-end-of-term-enabled-manifest.json` contains `final_ready` and `combined_output` coverage.
- `expected-end-of-term-blocked-review-manifest.json` contains `blocked_review` and `final_ready` coverage.
- `expected-combined-merge-unavailable-manifest.json` contains `merge_unavailable`, `final_ready`, and `combined_output` coverage.
- In the live run, `combined_output.status` was `failed` and `combined_pdf_exists` was `False`, which matches the rule that `passed` is only allowed when the actual combined PDF exists.

## Runtime adapter coverage

Passed checks:
- `rg "Codex|Claude Code|Gemini CLI|OpenCode|OpenClaw|Hermes Agent" skills/teaching-design-package/SKILL.md skills/jiaoan-jihua/SKILL.md skills/jiaoan-shicao/SKILL.md skills/end-of-term-teaching-materials/SKILL.md`
- `rg "OpenClaw|Hermes Agent|references/|templates/|scripts/|shell|permission|fallback|workdir|writable|sandbox|support" skills/teaching-design-package/SKILL.md skills/jiaoan-jihua/SKILL.md skills/jiaoan-shicao/SKILL.md skills/end-of-term-teaching-materials/SKILL.md`

Review result:
- A narrow wording gap was corrected in `skills/teaching-design-package/SKILL.md` script usage examples and in the discoverability docs.
- Canonical process text stays runtime-neutral; runtime-specific behavior remains in Runtime Adapter Notes.

## Documentation/index discoverability

Passed checks:
- `rg "teaching-design-package" README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md`
- `rg "skills/teaching-design-package/SKILL.md|format-and-orchestration.md|teaching-design-package-full.md|teaching-design-package.sh" README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md skills/teaching-design-package/SKILL.md`
- `rg "Markdown|SKILL.md|references/|scripts/|templates/|test/|references/scheduling-contract.md" README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md`

Edits made:
- `README.md` now explicitly points to `skills/teaching-design-package/SKILL.md`, `references/format-and-orchestration.md`, `templates/teaching-design-package-full.md`, and `scripts/teaching-design-package.sh`.
- `skills/README.md` now describes `teaching-design-package` as composing `jiaoan-jihua`, `jiaoan-shicao`, and optional `end-of-term-teaching-materials`.
- `docs/directory-spec.md` now lists the `teaching-design-package` entry, reference, template, and script under shared references and fixtures.

## Repository cleanliness

Observed:
- Temporary outputs were created under `mktemp -d` paths only.
- `git diff --check` passed before staging.
- `git status --short` showed only intentional Phase 25 edits and planning artifacts.

## Gaps

None.

## Verification summary

- TDP-15: passed
- TDP-16: passed
- TDP-09: passed
- TDP-14: passed
