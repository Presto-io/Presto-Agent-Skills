# Phase 33 Plan Check

**Checked:** 2026-06-15
**Plan:** `33-PLAN.md`
**Result:** Passed

## VERIFICATION PASSED

The Phase 33 plan is executable and matches the scoped Phase 33 context:

- It covers only the mapped Phase 33 requirements: `TDPKG-MOD-01..07`, `TDPKG-YAML-01..04`, and `TDPKG-SCHED-01..05`.
- It explicitly keeps Phase 33 to infrastructure: module registry, unified extraction, YAML conversion, skill-local calendar, shared scheduling model, hidden module Markdown/Typst, and diagnostics.
- It preserves the existing public command surface instead of renaming or deleting `example`, `model`, `render-package`, `manifest`, `plan-split`, `render-split`, `info`, or `version`.
- It requires `skills/teaching-design-package/references/calendar.json` and standalone-copy scheduling without runtime dependency on sibling `jiaoan-jihua` or `jiaoan-shicao` folders.
- It replaces natural-day sequential scheduling with real calendar consumption and requires failure when `first_teaching_day` is missing, absent from the calendar, or the calendar is exhausted.
- It requires hidden module Markdown and Typst under `.teaching-design-package/work/`.
- It requires generated module frontmatter for both registered modules and one shared scheduling model consumed by both modules.
- It records hidden scheduling evidence and classified diagnostics.
- It explicitly excludes Phase 34 formal `jiaoan-jihua` migration, Phase 35 formal `jiaoan-shicao` migration/cross-module activity validation, and Phase 36 public final PDF delivery/merge work.

## Coverage

| Requirement | Covered In |
|-------------|------------|
| TDPKG-MOD-01 | Tasks 1, 6 |
| TDPKG-MOD-02 | Tasks 1, 6 |
| TDPKG-MOD-03 | Tasks 1, 3, 4 |
| TDPKG-MOD-04 | Tasks 1, 4, 6 |
| TDPKG-MOD-05 | Task 4 |
| TDPKG-MOD-06 | Task 4 |
| TDPKG-MOD-07 | Tasks 1, 4, 6 |
| TDPKG-YAML-01 | Task 3 |
| TDPKG-YAML-02 | Tasks 3, 4 |
| TDPKG-YAML-03 | Tasks 3, 4 |
| TDPKG-YAML-04 | Tasks 2, 3, 5 |
| TDPKG-SCHED-01 | Tasks 2, 6 |
| TDPKG-SCHED-02 | Tasks 2, 5 |
| TDPKG-SCHED-03 | Tasks 2, 3, 5 |
| TDPKG-SCHED-04 | Tasks 2, 3 |
| TDPKG-SCHED-05 | Tasks 2, 5 |

## Required Acceptance Coverage

1. Unified Markdown parsing: Task 1 requires frontmatter plus `# 授课进度计划` and `# 教学设计方案`, source-order schedule rows, source pointers, and malformed-row failure.
2. Module registry: Task 1 requires stable module ids, display names, order, hidden Markdown/Typst paths, and public command preservation.
3. YAML conversion: Task 3 requires accepted unified YAML keys, rejected derived/internal keys, `teacher_name`, module frontmatter, `daily_hours`, `total_hours`, and `use_time`.
4. Calendar scheduling: Task 2 requires skill-local `calendar.json`, standalone-copy access, calendar hash, calendar policy, first-day membership, calendar exhaustion failure, and no natural-day scheduling path.
5. Hidden module artifacts: Task 4 requires hidden module Markdown/Typst files and root-leakage checks.
6. Diagnostics and evidence: Task 5 requires hidden model/status/diagnostics with calendar path/hash, derivation summary, module frontmatter, and classified failures.
7. Scope exclusion: `scope_boundary`, Task 4, Task 6, verification, and success criteria all block Phase 34-36 work from being claimed in Phase 33.

## Checks Applied

- Frontmatter contains phase, plan, type, wave, depends_on, files_modified, autonomous, requirements, and requirements_addressed.
- Every task contains `read_first`, `action`, and `acceptance_criteria`.
- Actions use concrete file paths, command names, JSON fields, module ids, hidden work paths, and exact forbidden/success patterns.
- Verification includes shell syntax, command smoke checks, model JSON assertions, hidden artifact existence checks, public-root leakage scans, forbidden frontmatter checks, first-day failure, malformed-row failure, standalone-copy calendar checks, sibling dependency scans, legacy skill diff checks, and whitespace checks.
- Plan scope does not modify legacy standalone skill implementations and does not ask the executor to migrate formal renderers or produce final public PDFs.
- The plan includes `git diff --cached --check` in verification so the final plan-phase commit can be staged safely.

## Residual Risk

Execution will need careful script refactoring because the current script already generates hidden split Typst and model/status files, but still uses `sequential_teaching_days_default` natural-day scheduling. The plan makes that drift the central implementation target and requires standalone calendar evidence before Phase 33 can pass.
