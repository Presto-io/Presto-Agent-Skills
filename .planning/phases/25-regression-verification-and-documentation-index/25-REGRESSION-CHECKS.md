# Phase 25 Regression Checks

**Phase:** 25 - Regression Verification and Documentation Index
**Date:** 2026-06-14
**Scope:** TDP-09, TDP-14, TDP-15, TDP-16

This matrix is the Phase 25 execution-owned checklist. Generated outputs must use
`mktemp -d` or explicit `/tmp` paths and must leave no repository-dirty generated
artifacts after cleanup.

## Standalone Public Commands

| Check | Expected | Temporary output policy | Coverage |
|-------|----------|-------------------------|----------|
| `bash -n skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` | exit 0 | no output | TDP-15; D-01, D-20, D-22 |
| `jiaoan-jihua.sh example --output <tmp>/jiaoan-jihua-full.md` | exit 0; Markdown file exists | `<tmp>` from `mktemp -d` | TDP-15; D-01, D-02 |
| `jiaoan-jihua.sh render --input test/1.10/...授课计划.md --typ <tmp>/jiaoan-jihua.typ --expected-typ test/1.10/...授课计划.typ` | exit 0; strict expected Typst comparison passes | `<tmp>` from `mktemp -d` | TDP-15; D-01, D-03 |
| `jiaoan-jihua.sh manifest`, `info`, `version` | each exits 0 | no repository output | TDP-15; D-01, D-05 |
| `bash -n skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` | exit 0 | no output | TDP-15; D-01, D-20, D-22 |
| `jiaoan-shicao.sh example --output <tmp>/jiaoan-shicao-full.md --calendar-output <tmp>/calendar.json` | exit 0; Markdown and calendar files exist | `<tmp>` from `mktemp -d` | TDP-15; D-01, D-02 |
| `jiaoan-shicao.sh render --input test/1.10/...教案.md --typ <tmp>/jiaoan-shicao.typ --expected-typ test/1.10/...教案.typ` | exit 0; strict expected Typst comparison passes | `<tmp>` from `mktemp -d` | TDP-15; D-01, D-03 |
| `jiaoan-shicao.sh manifest`, `info`, `version` | each exits 0 | no repository output | TDP-15; D-01, D-05 |
| `bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh` | exit 0 | no output | TDP-15; D-01, D-20, D-22 |
| `end-of-term-teaching-materials.sh example`, `validate`, `markdown`, `render`, `verify`, `manifest`, `info`, `version` | commands exit 0 or record explicit non-final/tooling status where designed | `<tmp>` from `mktemp -d`; existing `--workdir` only | TDP-15; D-01, D-02, D-10 |

## Package Manifest Semantics

| Check | Expected | Temporary output policy | Coverage |
|-------|----------|-------------------------|----------|
| `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh` | exit 0 | no output | TDP-14; D-20, D-22 |
| `teaching-design-package.sh example --output <tmp>/teaching-design-package-full.md` | exit 0; package Markdown exists | `<tmp>` from `mktemp -d` | TDP-14; D-02, D-04 |
| `plan-split`, `render-split`, `manifest`, `info`, `version` | exit 0; split module files and manifest exist where expected | `<tmp>` from `mktemp -d` | TDP-14; D-04, D-06 |
| `plan-end-of-term`, `render-end-of-term`, `render-package` when fixture prerequisites exist | exit 0 or produce explicit `blocked_review`, `failed`, `not_run`, `missing_compiler`, or `merge_unavailable` status | `<tmp>` from `mktemp -d` | TDP-14; D-07, D-08, D-10 |
| `python3 -m json.tool test/1.11/teaching-design-package/expected-*.json` | exit 0 for every expected manifest | normalized output in `/tmp` only | TDP-14; D-09 |
| Targeted manifest field checks | `disabled`, `blocked_review`, `merge_unavailable`, `final_ready`, and `combined_output` are present as applicable | no repository output | TDP-14; D-06, D-07, D-08, D-09 |
| Combined PDF truthfulness | no checked manifest marks `combined_output.status` as `passed` unless `teaching-design-package.pdf` exists in the checked output directory | `<tmp>` from `mktemp -d` | TDP-14; D-06, D-25 |

## Runtime Adapter Coverage

| Check | Expected | Temporary output policy | Coverage |
|-------|----------|-------------------------|----------|
| Runtime-name scan across affected `SKILL.md` files | each file contains Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent | no output | TDP-09; D-11 |
| OpenClaw/Hermes practical-note scan | affected entries mention discovery, support files, scripts/shell permissions, writable path/sandbox, and fallback behavior | no output | TDP-09; D-12 |
| Canonical section review | runtime-private syntax stays in Runtime Adapter Notes, not canonical Process/Outputs/Verification/Safety | no output | TDP-09; D-13 |
| Compatibility matrix review | matrix preserves one canonical `SKILL.md` plus progressive disclosure and avoids overclaiming unverified support | no output | TDP-09; D-14 |

## Documentation/Index Discoverability

| Check | Expected | Temporary output policy | Coverage |
|-------|----------|-------------------------|----------|
| `rg "teaching-design-package" README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md` | exit 0 | no output | TDP-16; D-15 |
| `rg "skills/teaching-design-package/SKILL.md|format-and-orchestration.md|teaching-design-package-full.md|teaching-design-package.sh" README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md skills/teaching-design-package/SKILL.md` | exit 0 | no output | TDP-16; D-15 |
| Directory-guidance scan for `Markdown`, `SKILL.md`, `references/`, `scripts/`, `templates/`, `test/`, and `references/scheduling-contract.md` | exit 0 | no output | TDP-16; D-16 |
| README and skills index wording | state that `teaching-design-package` composes `jiaoan-jihua`, `jiaoan-shicao`, and optional `end-of-term-teaching-materials` without replacing them | no output | TDP-16; D-17 |
| Requirement traceability review | verification evidence maps checks to TDP-09, TDP-14, TDP-15, and TDP-16 | no output | TDP-16; D-18 |

## Repository Cleanliness

| Check | Expected | Temporary output policy | Coverage |
|-------|----------|-------------------------|----------|
| `git status --short` after temporary cleanup | only intentional Phase 25 artifacts and narrow documentation-index edits are present | no generated repo outputs | D-20, D-21 |
| `git diff --check` | exit 0 before staging | no output | D-22 |
| `git diff --cached --check` | exit 0 before committing | no output | D-22 |
| `gsd-sdk query init.execute-phase 25` after closeout | no incomplete plan remains, or actual fields are reported | no output | D-21, D-24 |

## Decision Traceability

| Decision | Covered by |
|----------|------------|
| D-01 | Standalone public command smoke checks |
| D-02 | `mktemp -d` and explicit output path policy |
| D-03 | v1.10 strict `--expected-typ` render checks |
| D-04 | package `plan-split`/`render-split` composition checks |
| D-05 | command availability, usage text, and skill script usage comparison |
| D-06 | combined PDF status and file-existence assertions |
| D-07 | missing split PDF, merge tool, source data, review, and compiler status assertions |
| D-08 | optional end-of-term disabled/enabled manifest state assertions |
| D-09 | expected manifest JSON validation and targeted field checks |
| D-10 | explicit non-passed status for unavailable local PDF/Typst tooling |
| D-11 | six-runtime scan across affected canonical skill entries |
| D-12 | OpenClaw/Hermes practical adapter note review |
| D-13 | runtime-neutral canonical section review |
| D-14 | compatibility matrix review |
| D-15 | repository index discoverability checks |
| D-16 | directory placement and Markdown-first guidance checks |
| D-17 | package-composes-standalone wording checks |
| D-18 | requirement traceability in this matrix and verification artifact |
| D-19 | this dedicated rerunnable/auditable matrix |
| D-20 | temp output cleanup and `git status --short` checks |
| D-21 | `25-VERIFICATION.md` evidence sections |
| D-22 | shell syntax, JSON syntax, whitespace, and cached diff checks |
| D-23 | local-only verification; no web research |
| D-24 | SDK phase lookup/result recorded in verification |
| D-25 | failed regression handling limited to recorded gaps or narrow planned docs fixes |
