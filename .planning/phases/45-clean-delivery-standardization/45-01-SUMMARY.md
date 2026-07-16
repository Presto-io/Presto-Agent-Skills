---
phase: 45-clean-delivery-standardization
plan: 01
subsystem: testing
tags: [filesystem-safety, delivery-contract, rollback, cleanup-audit, black-box-testing]

requires:
  - phase: 44-verification-gate-runtime-notes-and-uat
    provides: school-pptx fixed gate registry, bounded public CLI diagnostics, and renderer regression patterns
provides:
  - Machine-checkable DeliverySpec and candidate-first publication authority
  - Snapshot-bound audit-to-confirm historical cleanup contract
  - Fixed 14-gate and 7-fault cross-skill black-box harness foundation
affects: [45-02, 45-03, 45-04, 45-05, 45-06, 45-07, 45-08, 45-09]

tech-stack:
  added: []
  patterns: [explicit-managed-set, candidate-first, handled-failure-rollback, snapshot-bound-approval, fixed-gate-registry]

key-files:
  created:
    - test/clean-delivery/verify_clean_delivery.py
    - test/clean-delivery/fixtures/README.md
  modified:
    - docs/clean-delivery-directory-contract.md
    - docs/agent-output-cleanup-prompt.md

key-decisions:
  - "Delivery equality is exact relative path-set plus bytes, including explicitly managed assets."
  - "Portable guarantees stop at per-path replace and handled failure/INT/TERM rollback; SIGKILL, power loss, and cross-file atomicity are not claimed."
  - "Historical cleanup execution requires an exact approval bound to an unchanged no-follow snapshot."

patterns-established:
  - "Foundation-only gate registry: Phase 45 adapters target fixed names without claiming unconnected skill behavior passes."
  - "Owned cleanup: normal publication and cleanup execution mutate only explicit validated relative operations."

requirements-completed:
  - CLEAN-02
  - CLEAN-03
  - REV-01
  - REV-02
  - REV-03
  - REV-04
  - SAFE-01
  - SAFE-02
  - VERIFY-01

duration: 9 min
completed: 2026-07-15
---

# Phase 45 Plan 01: Clean Delivery Protocol Foundation Summary

**显式 DeliverySpec、snapshot-bound 整理确认门与固定 14-gate/7-fault harness 为六技能适配提供同一可复验目标**

## Performance

- **Duration:** 9 min
- **Started:** 2026-07-15T23:51:23Z
- **Completed:** 2026-07-15T23:59:55Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- 冻结显式受管集合、candidate-first、逐文件字节相等、history `max+1`、managed assets 归档与 sources 不变语义。
- 明确 handled failure/INT/TERM 回滚与单路径 replace 边界，不承诺 SIGKILL、断电或多文件跨路径原子。
- 将历史整理固化为 no-follow 只读 snapshot、三组 exact operations 和 snapshot-bound approval 两阶段协议。
- 建立固定 14-gate、7-fault、二/四文件 bundle、真实 public CLI subprocess 与 relative path+bytes snapshot 骨架。

## Task Commits

Each task was committed atomically:

1. **Task 1: 冻结可执行的交付状态机与真实原子性边界** - `fcdd747` (docs)
2. **Task 2: 固化只读审计与显式确认整理流程** - `97206f1` (docs)
3. **Task 3: 建立固定跨技能 gate 与故障注入注册表** - `a2fe1f6` (test)

## Files Created/Modified

- `docs/clean-delivery-directory-contract.md` - 定义 DeliverySpec、状态机、history、rollback 与真实原子性边界。
- `docs/agent-output-cleanup-prompt.md` - 定义授权 root、no-follow snapshot、exact approval 与拒绝结果。
- `test/clean-delivery/verify_clean_delivery.py` - 固定 gate/fault registry、snapshot API、public CLI wrapper 与 self-test。
- `test/clean-delivery/fixtures/README.md` - 定义 unknown、source、asset、symlink、stale work 与 stale snapshot fixtures。

## Decisions Made

- `DeliverySpec.current_names + managed_assets` 是唯一受管集合；相同候选要求相对路径集合和逐文件 bytes 同时相等。
- history 只扫描 `^[0-9]{3,}$` 真实目录并使用 `max+1`，archived Markdown 所需 managed assets 随同一版本归档，sources 永不由普通发布变更。
- harness 在本计划仅验证 registry、fixture API 与公共契约，不把尚未接线的六技能行为标为通过；真实技能矩阵留给 45-09。

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Task 1 和 Task 2 的计划内 self-test 依赖 Task 3 创建的 harness，首次按任务顺序运行时报告文件不存在；Task 3 完成后两项原命令与全量 self-test 均通过。

## User Setup Required

None - no external service configuration required.

## Verification Evidence

- `python3 test/clean-delivery/verify_clean_delivery.py --self-test protocol` — PASS
- `python3 test/clean-delivery/verify_clean_delivery.py --self-test cleanup-contract` — PASS
- `python3 test/clean-delivery/verify_clean_delivery.py --self-test all` — PASS
- `python3 -m py_compile test/clean-delivery/verify_clean_delivery.py` — PASS
- 未知 self-test 非零，重复 gate mutation 被 registry self-test 拒绝。
- 生产脚本静态扫描未发现对 `test/clean-delivery/verify_clean_delivery.py` 的 import/call。

## Next Phase Readiness

- 六个 skill-local 适配计划可共同引用固定 DeliverySpec、14-gate 与 7-fault authority。
- 后续实现必须保持 self-contained，中央 harness 的真实六技能接线由 45-09 统一完成。

## Self-Check: PASSED

- 关键 created files 存在。
- 三个 task commits 可由 `git log --grep=45-01` 检索。
- 所有任务 acceptance criteria 与计划级 verification 已重跑通过。

---
*Phase: 45-clean-delivery-standardization*
*Completed: 2026-07-15*
