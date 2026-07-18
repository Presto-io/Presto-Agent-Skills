---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
plan: 09
subsystem: graduate-resume-delivery-transaction
tags: [python, delivery-root, cleanup, rollback, no-follow, tdd]

requires:
  - phase: 48-deterministic-targeted-rendering-clean-batch-delivery
    plan: 06
    provides: reviewed approval digest、完整 triple 事务与 rollback 基线
provides:
  - 仅允许 managed triples、受校验 history 与当前 owned work 的精确投递根边界
  - unlink、rmdir 与 descriptor close 的尽力清理和有界聚合错误
  - 成功发布与回滚双故障下保持 current 正确状态的 cleanup 语义
affects: [48-08-cli-cleanup-fault-acceptance, graduate-resume-publication, clean-delivery]

tech-stack:
  added: []
  patterns: [exact-root-allowlist, aggregate-cleanup-failure, exception-cause-preservation]

key-files:
  created: []
  modified:
    - skills/graduate-resume/scripts/graduate_resume_delivery.py
    - skills/graduate-resume/scripts/test_delivery_transaction.py

key-decisions:
  - "Phase 48 投递根的 support allowlist 仅保留 history 与 .work；sources/assets 的任何文件系统形态都按 unknown fail closed。"
  - "close() 固定尽力执行全部 owned cleanup，再以 operation、相对 owned name 与 errno 聚合为一个 bounded DeliveryError。"
  - "cleanup 首次失败后 session 进入 closed 状态，重复 close 不重试不确定 syscall，也不产生新的错误。"

patterns-established:
  - "Root authority: managed_names + history + exact owned .work 是唯一合法根目录集合。"
  - "Cleanup result: absent 可幂等忽略，其他 unlink/rmdir/close OSError 全部记录并在末尾统一抛出。"

requirements-completed: [DELIVERY-02, DELIVERY-03]

duration: 12min
completed: 2026-07-18
---

# Phase 48 Plan 09: 精确投递根与可观测 Cleanup Summary

**毕业生简历投递事务现在拒绝任何 sources/assets 污染，并在完成全部 owned cleanup 尝试后以有界错误报告文件删除、目录删除或 descriptor 关闭故障。**

## Performance

- **Duration:** 12 min
- **Started:** 2026-07-18T15:21:24Z
- **Completed:** 2026-07-18T15:33:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- 投递根 allowlist 从 `sources/assets/history/.work` 收紧为 `history/.work`；八种 sources/assets 空目录、非空目录、普通文件和 symlink 污染均在 mutation 前稳定拒绝。
- 污染负例比较递归 path set、bytes、inode、mtime 和 mode，证明 current/history 与未知现场均不被自动清理或迁移。
- `close()` 覆盖 candidate、rollback、evidence、run、`.lock`、`.work` 和 root 的 unlink/rmdir/close，完整尝试后聚合稳定相对资源名与 errno。
- 成功 publication 遇到 cleanup failure 时保留已发布 triples 并留下可审计 stale work；publication failure 遇到 cleanup failure 时先完成 rollback，再通过异常链保留原始失败。

## Task Commits

1. **Task 1 RED：sources/assets 污染与完整状态快照负例** - `d30fe07` (test)
2. **Task 1 GREEN：收紧 Phase 48 根目录 allowlist** - `c32c2f7` (fix)
3. **Task 2 RED：全 owned cleanup syscall 故障负例** - `c6701b7` (test)
4. **Task 2 GREEN：聚合 cleanup failure 与异常因果** - `41d4f62` (fix)

## Files Created/Modified

- `skills/graduate-resume/scripts/graduate_resume_delivery.py` - 精确 support allowlist、幂等 close、完整 cleanup 尝试、稳定聚合错误与异常链。
- `skills/graduate-resume/scripts/test_delivery_transaction.py` - 八种根污染、14 个 cleanup 注入点、成功发布残留与 rollback 双故障回归。

## Decisions Made

- cleanup 错误只公开固定 operation、相对 owned name 与整数 errno，不包含候选 bytes、绝对路径或 traceback。
- 只有明确的 `FileNotFoundError` 作为重复清理的 absent 成功；权限、非空、I/O 和 bad descriptor 等首次 `OSError` 全部记录。
- `__enter__` 与 `__exit__` 在原始异常和 cleanup 异常同时存在时，以 cleanup `DeliveryError` 为外层结果并用 `raise ... from original` 保留因果。

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- cleanup RED 初稿把两条既有 signal rollback 循环误置入新测试类；在 GREEN 前恢复到原 `PublicationTransactionTests`，随后窄测试与全量测试全部通过。该调整仅修正测试组织，不改变计划范围或生产契约。

## Known Stubs

None. 修改文件中的空集合与 `None` 均为事务初始化或测试快照状态，没有流向正式渲染的 placeholder、TODO、FIXME 或未接通 mock。

## Threat Review

- `T-48-G09-01/02`：sources/assets 不再具有 support 身份，history 与 `.work` 继续沿用 held descriptor、no-follow 和 exact content 校验。
- `T-48-G09-03/04`：cleanup syscall failure 变为 bounded 非零结果，残留 work 保持可见并阻止下一 session 静默继续。
- `T-48-G09-05`：双故障先验证 rollback 后 current bytes，再用异常链保留 publication failure。
- 未新增网络 endpoint、认证路径、凭据、数据库/schema 或计划威胁模型之外的 trust boundary。

## Verification

- `python3 -m unittest skills/graduate-resume/scripts/test_delivery_transaction.py -v`：18/18 PASS。
- `python3 -m unittest skills/graduate-resume/scripts/test_phase48_cli.py -v`：19/19 PASS。
- `python3 -m unittest discover -s skills/graduate-resume/scripts -p 'test_*.py' -v`：79/79 PASS。
- `python3 skills/graduate-resume/scripts/graduate_resume_cli.py verify`：4 个 valid、6 个 invalid、5 个 layout fixture 全部符合预期。
- `python3 -m py_compile skills/graduate-resume/scripts/graduate_resume_delivery.py skills/graduate-resume/scripts/test_delivery_transaction.py`：PASS。
- 静态检查确认生产 allowlist 不含 `sources/assets`，`close/_close_fd` 不含无条件 `except OSError: pass`，`git diff --check 9c43c9a..HEAD` PASS。

## TDD Gate Compliance

- Task 1：RED `d30fe07` 的八个 subcase 因 sources/assets 被错误接受或仅按 support-directory 类型拒绝而失败；GREEN `c32c2f7` 后全部通过。
- Task 2：RED `c6701b7` 的 14 个 syscall 注入点、成功 publication cleanup failure 与 rollback 双故障均因错误被吞掉而失败；GREEN `41d4f62` 后全部通过。
- 两个任务均具备先 RED 后 GREEN 的独立提交，未跳过失败门禁。

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- WR-01 的 service-level cleanup contract 已完成；公开 CLI 的非零 bounded JSON、无 success payload 与 current 状态验收明确交由依赖本计划的 48-08 Task 3。
- 本计划未修改 `test_phase48_cli.py` 或其他 48-08 所有权文件，可继续串行执行 48-08 收束 Phase 48。

## Self-Check: PASSED

- 两个 key-files.modified 与本 SUMMARY 均存在。
- `d30fe07`、`c32c2f7`、`c6701b7`、`41d4f62` 均存在于 git history，且每个 RED 均先于对应 GREEN。
- 窄测试 18/18、CLI 19/19、全量 79/79、fixture verify、py_compile、静态反模式检查与 diff check 全部通过。

---
*Phase: 48-deterministic-targeted-rendering-clean-batch-delivery*
*Completed: 2026-07-18*
