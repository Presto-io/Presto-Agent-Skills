# Phase 35 Plan Check

**Plan:** `35-PLAN.md`
**Checked:** 2026-06-15
**Result:** PASSED

## Scope Gate

- Passed: The plan is limited to Phase 35 teaching-design formal renderer migration and cross-module validation.
- Passed: It explicitly excludes Phase 36 course-name-prefixed final delivery and final package PDF merge.
- Passed: It forbids implementation work during planning and leaves code changes for `/gsd:execute-phase 35`.
- Passed: It protects `skills/jiaoan-shicao/` as read-only legacy reference/oracle and forbids package runtime dependency on it.

## Requirement Coverage

| Requirement | Coverage |
|-------------|----------|
| TDPKG-LEGACY-02 | Package-owned formal teaching-design renderer, legacy surface migration, Typst/PDF generation, fixture equivalence |
| TDPKG-VAL-02 | Task `课时：xH` from `task.total_hours`; activity `##### xH` from schedule row hours |
| TDPKG-VAL-03 | Mapping by learning task + learning stage + activity order; normalized titles only as diagnostics |
| TDPKG-VAL-04 | Hard-fail hidden diagnostics for count/title/hour/date mismatches, non-zero exit, no false public success |

## Must-Have Checks

- Passed: The plan requires replacing the `teaching-design.typ` placeholder and forbids `Pre-formal surface only` semantics.
- Passed: The plan names a package-owned `teaching-design-renderer.js` implementation path while allowing the executor to keep it package-internal.
- Passed: The plan requires old `jiaoan-shicao` formal layout migration, including learning-task analysis, activity table, evaluation pages, and metadata.
- Passed: Activity-table rules include `25.04cm` total width, narrow `课时分配`, chapter/pagebreak-scoped columns, and landscape behavior.
- Passed: Every task-level `课时：xH` must derive from `schedule.tasks[].total_hours`.
- Passed: Every activity-level `##### xH` must derive from `schedule.tasks[].stages[].rows[].hours`.
- Passed: Task/stage/activity count, order, title, hour, and date mismatches fail non-zero with hidden diagnostics.
- Passed: Diagnostics require mismatch class, module id, source pointers, expected/actual values, calendar path/hash, model version, and source Markdown path.
- Passed: Public-root leakage, standalone-copy verification, and unchanged legacy `skills/jiaoan-shicao` are required.

## Verification Quality

- Passed: Syntax checks cover shell, package model, teaching-plan renderer, and planned teaching-design renderer.
- Passed: Positive verification includes hidden formal Typst generation, structural greps, model evidence recomputation, Typst compile, and PDF non-empty checks.
- Passed: Negative fixtures cover task count, stage count, activity count, task title, stage title, activity title, task hours, activity hours, and task date range.
- Passed: Verification explicitly guards public-root leakage and false public success on mismatch failures.
- Passed: Fixture equivalence uses `test/1.10/电气设备控制线路安装与调试教案.md/.typ/.pdf` as read-only oracle.
- Passed: Source scans forbid runtime references to `skills/jiaoan-shicao`, `jiaoan-shicao.sh`, and legacy calendar resources.
- Passed: Final checks include `git diff --check` and `git diff --cached --check`.

## Residual Risk

- The plan allows normalized fixture diff when exact Typst diff is blocked by package provenance or scheduling-model metadata. This is acceptable only because the plan constrains allowed differences and requires structural checks that fail on layout, order, hour, date, evaluation, and body-text drift.
- The plan references a possible `create-negative-fixture.js` verification helper but keeps it evidence-only and out of package runtime dependencies.
- The plan leaves final course-name public delivery and final merge to Phase 36, so Phase 35 success must not be interpreted as full v1.15 delivery completion.

## Conclusion

`35-PLAN.md` is executable and ready for `/gsd:execute-phase 35`.
