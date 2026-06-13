# Phase 25 Research: Regression Verification and Documentation Index

**Phase:** 25 - Regression Verification and Documentation Index
**Researched:** 2026-06-14
**Mode:** Local repository research for `/gsd:plan-phase 25 --auto`

## RESEARCH COMPLETE

Phase 25 should be planned as a black-box regression and documentation-index gate for v1.11. No external web research is needed; the relevant facts are already in `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, Phase 22/23/24 summaries and verification, the affected skill folders, fixtures, and repository indexes.

## Sources Read

- `AGENTS.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/25-regression-verification-and-documentation-index/25-CONTEXT.md`
- `.planning/phases/22-scheduling-contract-and-fixture/22-SUMMARY.md`
- `.planning/phases/22-scheduling-contract-and-fixture/22-VERIFICATION.md`
- `.planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-SUMMARY.md`
- `.planning/phases/23-integrated-skill-entry-and-jiaoan-orchestration/23-VERIFICATION.md`
- `.planning/phases/24-optional-end-of-term-module-and-package-outputs/24-SUMMARY.md`
- `.planning/phases/24-optional-end-of-term-module-and-package-outputs/24-VERIFICATION.md`
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/jiaoan-jihua/SKILL.md`
- `skills/jiaoan-jihua/references/format-and-rendering.md`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
- `skills/jiaoan-shicao/SKILL.md`
- `skills/jiaoan-shicao/references/format-and-rendering.md`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`
- `skills/end-of-term-teaching-materials/SKILL.md`
- `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`
- `README.md`
- `skills/README.md`
- `docs/directory-spec.md`
- `docs/compatibility-matrix.md`

## Current State

- Phase 22 completed TDP-01 through TDP-04 with a shared scheduling contract, deterministic schedule fixture, and `scripts/derive-scheduling-fixture.py`.
- Phase 23 completed TDP-05 through TDP-09 for the initial `teaching-design-package` skill, split jiaoan module handoff, split Typst status, and six-runtime adapter coverage.
- Phase 24 completed TDP-10 through TDP-14 for optional `end-of-term-teaching-materials` composition, module-owned review gates, deterministic table/workbook pointers, and honest combined-output status.
- Phase 25 owns broad regression proof for TDP-15 and documentation/index proof for TDP-16, while also re-checking TDP-09 and TDP-14 as regression-sensitive contracts.

## Regression Surface

### Standalone Commands

Phase 25 should verify these existing public commands from the outside:

- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh example`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh manifest`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh info`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh version`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh manifest`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh info`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh version`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh example`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh validate`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh markdown`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh render`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh verify`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh manifest`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh info`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh version`

The v1.10 fixture-backed gates are high-value:

- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render --input test/1.10/电气设备控制线路安装与调试授课计划.md --typ <tmp> --expected-typ test/1.10/电气设备控制线路安装与调试授课计划.typ`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --input test/1.10/电气设备控制线路安装与调试教案.md --typ <tmp> --expected-typ test/1.10/电气设备控制线路安装与调试教案.typ`

### Package Commands

The integrated package helper should be verified as a composer, not as a replacement:

- `skills/teaching-design-package/scripts/teaching-design-package.sh example`
- `skills/teaching-design-package/scripts/teaching-design-package.sh plan-split`
- `skills/teaching-design-package/scripts/teaching-design-package.sh render-split`
- `skills/teaching-design-package/scripts/teaching-design-package.sh plan-end-of-term`
- `skills/teaching-design-package/scripts/teaching-design-package.sh render-end-of-term`
- `skills/teaching-design-package/scripts/teaching-design-package.sh render-package`
- `skills/teaching-design-package/scripts/teaching-design-package.sh manifest`
- `skills/teaching-design-package/scripts/teaching-design-package.sh info`
- `skills/teaching-design-package/scripts/teaching-design-package.sh version`

### Manifest Semantics

Phase 24 established that `teaching-design-package.pdf` may be `passed` only when the actual combined PDF exists after explicit merge/compile evidence. Phase 25 should assert:

- disabled optional end-of-term remains non-failing
- enabled module with unresolved review markers records `blocked_review` and `final_ready: false`
- missing selected split PDFs record `failed` or equivalent non-passed status
- unavailable merge tooling records `merge_unavailable`
- unavailable PDF compiler records `missing_compiler` or another explicit non-passed status
- Typst generation alone never implies final PDF readiness

Existing expected manifests under `test/1.11/teaching-design-package/expected-*.json` provide deterministic status targets.

## Documentation and Runtime Coverage

Affected skill entries:

- `skills/teaching-design-package/SKILL.md`
- `skills/jiaoan-jihua/SKILL.md`
- `skills/jiaoan-shicao/SKILL.md`
- `skills/end-of-term-teaching-materials/SKILL.md`

Every affected entry should keep Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent represented in metadata or `Runtime Adapter Notes`. OpenClaw and Hermes coverage should include more than names: support-file discovery, script execution permissions, writable path or sandbox expectations, and fallback behavior when automatic script discovery is not guaranteed.

Index and documentation targets:

- `README.md`
- `skills/README.md`
- `docs/directory-spec.md`
- `docs/compatibility-matrix.md`
- `docs/markdown-normalization-contract.md`
- `references/scheduling-contract.md`

The docs should make `teaching-design-package` discoverable while preserving these placement rules:

- lightweight `SKILL.md`
- long rules in `references/`
- helper commands in `scripts/`
- templates in `templates/`
- shared cross-skill contracts in root `references/`
- deterministic fixture evidence under versioned `test/`
- no agent-private syntax in canonical workflow text

## Planning Recommendation

Use one executable plan with five tasks:

1. Add or update a focused Phase 25 regression verification artifact.
2. Cover standalone public commands and v1.10 strict fixtures.
3. Cover `teaching-design-package` manifest/failure semantics and expected manifests.
4. Cover runtime adapter and canonical-text portability.
5. Cover documentation/index discoverability and record verification evidence.

The execution phase may create a phase-local verification script or checklist, but plan-phase must not implement it. Any regression discovered during execution should be recorded as a gap unless the plan explicitly scopes a narrow documentation-index correction.
