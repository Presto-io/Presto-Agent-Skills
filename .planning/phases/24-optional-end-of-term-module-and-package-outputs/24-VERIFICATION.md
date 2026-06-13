---
phase: 24-optional-end-of-term-module-and-package-outputs
status: passed
verified: 2026-06-14
requirements: [TDP-10, TDP-11, TDP-12, TDP-13, TDP-14]
automated_checks: 16
human_verification: []
---

# Phase 24 Verification: Optional End-of-Term Module and Package Outputs

## Verdict

Passed. Phase 24 implements optional end-of-term module integration for `teaching-design-package`, preserves the standalone `end-of-term-teaching-materials` source of truth, exposes deterministic table/workbook/manifest pointers, and keeps split/combined PDF readiness honest.

## Requirement Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| TDP-10 | passed | `SKILL.md`, reference rules, script manifest, and fixture expectations support optional `end_of_term` while delegating module internals. |
| TDP-11 | passed | Contract and template require `end-of-term-full.md` and preserve module-local `## 复核标记`; blocked-review smoke test kept `87?` and `final_ready: false`. |
| TDP-12 | passed | Manifest pointers include `end-of-term-package.pdf`, `manifest.json`, deterministic `tables/*`, `score-list.xlsx`, and `scorebook.xlsx`. |
| TDP-13 | passed | `combined_output.path` is `teaching-design-package.pdf`; script marks it `passed` only when the actual file exists after merge/compile. |
| TDP-14 | passed | Missing selected split PDFs and unavailable merge tooling are represented as explicit `failed` or `merge_unavailable` manifest status, not false success. |

## Must-Have Checks

- Optional module is controlled by `modules.end_of_term.enabled` and manifest `end_of_term.status`.
- Disabled end-of-term module does not fail the package due to missing module artifacts.
- Enabled module readiness is blocked when module-local review markers remain or manifest `review_cleared` is false.
- Score calculation, deterministic tables, workbook generation, and review-marker resolution remain owned by `skills/end-of-term-teaching-materials`.
- `render --abnormal-review` remains non-final by contract.
- `teaching-design-package.pdf` cannot be marked `passed` without a real file.
- OpenClaw and Hermes Agent portability is preserved through explicit files, commands, and status evidence.

## Verification Commands

```bash
rg "TDP-10|TDP-11|TDP-12|TDP-13|TDP-14" skills/teaching-design-package/SKILL.md skills/teaching-design-package/references/format-and-orchestration.md
rg "end-of-term-teaching-materials|end-of-term-full.md|end-of-term-package.pdf|teaching-design-package.pdf" skills/teaching-design-package/SKILL.md skills/teaching-design-package/references/format-and-orchestration.md skills/teaching-design-package/templates/teaching-design-package-full.md
rg "blocked_review|merge_unavailable|missing_compiler|disabled|not_run|passed|failed" skills/teaching-design-package/references/format-and-orchestration.md skills/teaching-design-package/scripts/teaching-design-package.sh
rg "calculated-score-data.json|score-list.xlsx|scorebook.xlsx|highlight-evidence.json" skills/teaching-design-package/references/format-and-orchestration.md skills/teaching-design-package/templates/teaching-design-package-full.md skills/teaching-design-package/scripts/teaching-design-package.sh
python3 -m json.tool test/1.11/teaching-design-package/expected-end-of-term-disabled-manifest.json >/tmp/phase24-disabled-manifest.json
python3 -m json.tool test/1.11/teaching-design-package/expected-end-of-term-enabled-manifest.json >/tmp/phase24-enabled-manifest.json
python3 -m json.tool test/1.11/teaching-design-package/expected-end-of-term-blocked-review-manifest.json >/tmp/phase24-blocked-manifest.json
python3 -m json.tool test/1.11/teaching-design-package/expected-combined-merge-unavailable-manifest.json >/tmp/phase24-merge-unavailable-manifest.json
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh
skills/teaching-design-package/scripts/teaching-design-package.sh example --output /tmp/tdp24-example.md
skills/teaching-design-package/scripts/teaching-design-package.sh plan-split --input /tmp/tdp24-example.md --out-dir /tmp/tdp24-split
test -f /tmp/tdp24-split/jiaoan-jihua-full.md
test -f /tmp/tdp24-split/jiaoan-shicao-full.md
skills/teaching-design-package/scripts/teaching-design-package.sh plan-end-of-term --input /tmp/tdp24-enabled-smoke.md --out-dir /tmp/tdp24-enabled-smoke
rg '"status": "blocked_review"|87\?|"final_ready": false' /tmp/tdp24-enabled-smoke/teaching-design-package-manifest.json /tmp/tdp24-enabled-smoke/end-of-term-full.md
git diff -- skills/jiaoan-jihua/SKILL.md skills/jiaoan-shicao/SKILL.md skills/end-of-term-teaching-materials/SKILL.md
git diff --check
gsd-sdk query verify.schema-drift 24
```

## Results

All commands exited 0 except the privacy scan command below, where exit 1 is the expected no-match result:

```bash
rg "真实|身份证|手机号|私有路径|/Users/.*/Desktop" test/1.11/teaching-design-package
```

The independent skill entries `skills/jiaoan-jihua/SKILL.md`, `skills/jiaoan-shicao/SKILL.md`, and `skills/end-of-term-teaching-materials/SKILL.md` have no diff.

## Non-Blocking Workflow Notes

- Code review gate was skipped because the current runtime exposes no `Skill(skill="gsd-code-review")` callable interface.
- Schema drift gate returned `drift_detected: false`.
- Phase 25 remains responsible for broad regression across `jiaoan-jihua`, `jiaoan-shicao`, `end-of-term-teaching-materials`, and documentation/index discoverability.

## Status

`passed`
