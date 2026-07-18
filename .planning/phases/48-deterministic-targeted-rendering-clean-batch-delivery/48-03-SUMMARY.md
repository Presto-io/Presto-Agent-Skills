---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
plan: 03
subsystem: graduate-resume-delivery
tags: [python, secure-filesystem, bundle-transaction, rollback, tdd]

requires:
  - phase: 45-clean-delivery-standardization
    provides: held-directory、candidate-first、history、no-op 与 handled rollback 基线
  - phase: 47-controlled-themes-photo-frozen-layout
    provides: conservative、modern、expressive 三个登记主题与安全 stem 边界
provides:
  - 显式 safe-stem registry 驱动的动态 Markdown/Typst/PDF triple discovery
  - 完整 triple 粒度的 unchanged/added/updated/removed 分类与批准摘要
  - patch 保留其他版本、authority 安全移除 obsolete stems 的事务发布
  - updated/removed 选择性完整历史、精确 no-op 与全 current handled rollback
affects: [48-02-final-markdown-rendering, 48-04-public-cli, graduate-resume-batch]

tech-stack:
  added: []
  patterns: [explicit-managed-registry, whole-triple-delta, approval-bound-authority, held-dir-fd-rollback]

key-files:
  created:
    - skills/graduate-resume/scripts/graduate_resume_delivery.py
    - skills/graduate-resume/scripts/test_delivery_transaction.py
  modified: []

key-decisions:
  - "current 身份只消费调用方显式 safe stem 与登记主题后缀，不通过连字符反向解析单位或岗位。"
  - "patch 只把 candidate stems 与同名 current 比较并保留其他版本；authority 才能产生 removed，且批准摘要绑定整个 no-follow current snapshot。"
  - "任一 managed 文件变化都把整个 stem 提升为 updated；history 只包含 updated/removed，但每个归档 stem 必须保存完整三件套。"
  - "handled rollback 预存整个原 current 集合，恢复保证 exact path set 与 bytes；inode/mtime 不作为失败恢复承诺，仅 exact no-op 保持不变。"

patterns-established:
  - "Preflight-before-mutation: candidate grouping、root allowlist、current/history validation 与 delta approval 全部先于 history/replace/unlink。"
  - "Selective archive, whole-set rollback: 历史按变化 stem 最小化，rollback 按原 current 全集合恢复。"

requirements-completed: [DELIVERY-02, DELIVERY-03]

duration: 11min
completed: 2026-07-18
---

# Phase 48 Plan 03: 动态多 stem 三件套干净投递 Summary

**以 held directory descriptor、完整 triple delta 和批准绑定快照实现 patch/authority 多版本发布，同时保留精确 no-op、选择性完整历史与 handled 全集合回滚。**

## Performance

- **Duration:** 11 min
- **Started:** 2026-07-18T06:19:24Z
- **Completed:** 2026-07-18T06:30:08Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- 新增 `DeliverySpec`、`BundleDelta`、`classify_bundle_delta`，以显式 safe stem 和主题后缀 registry 验证动态 `.md/.typ/.pdf` 完整集合。
- 新增 held-root `DeliverySession`，在 mutation 前拒绝 unknown、partial、symlink、目录、FIFO、stale `.work`、非法 history 和 root identity 变化。
- 新增 patch 与 authority 两种发布语义：patch 保留所有非 candidate current，authority 的 removals 必须使用绑定整个 current snapshot 的批准 digest。
- 新增选择性 history、精确 no-op、post-publication exact verification，以及普通异常、全部 fault hooks、SIGINT、SIGTERM 的全 current rollback。

## Task Commits

每个 TDD gate 均独立提交：

1. **Task 1 RED：动态 triple discovery 与 delta 失败契约** - `c1005f6` (test)
2. **Task 1 GREEN：显式 registry 与 fail-closed delta 预检** - `bcf36ec` (feat)
3. **Task 2 RED：多 bundle 发布、历史与 rollback 失败契约** - `19d816d` (test)
4. **Task 2 GREEN：原子 patch/authority 发布事务** - `a76acf1` (feat)

## Files Created/Modified

- `skills/graduate-resume/scripts/graduate_resume_delivery.py` - 动态 triple discovery、delta 分类、held-root 会话、批准快照、history、发布与 rollback。
- `skills/graduate-resume/scripts/test_delivery_transaction.py` - 11 项事务回归，覆盖 no-op、history、remove、patch、TOCTOU、路径攻击、fault 与 signal。

## Decisions Made

- stem 验证只确认安全组件和唯一登记主题后缀；单位、岗位及含连字符的显示信息保持 opaque，不参与反向解析。
- authority 批准 token 使用 delta 类别与整个 current 文件 SHA-256 快照派生；预检后任一 current 字节变化都会稳定使批准失效。
- rollback 保存整个原 current，而 history 只保存 updated/removed stems；两种集合刻意不同，以同时满足最小历史与全批恢复。
- SIGKILL、掉电和多路径硬原子性仍不属于本计划承诺范围。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] 在打开前拒绝 FIFO 等特殊 managed path**
- **Found during:** Task 1（动态 triple discovery 与 delta 分类）
- **Issue:** 仅依赖 `O_NOFOLLOW` 打开 FIFO 会阻塞预检，无法稳定 fail closed。
- **Fix:** 先执行 descriptor-relative、no-follow `stat` 并要求普通文件，再打开并读取非空 bytes。
- **Files modified:** `skills/graduate-resume/scripts/graduate_resume_delivery.py`
- **Verification:** FIFO、目录、symlink 子测试均立即失败且根目录 snapshot 不变。
- **Committed in:** `bcf36ec`

---

**Total deviations:** 1 auto-fixed（1 bug）
**Impact on plan:** 修复属于计划威胁模型要求的特殊文件拒绝，不增加产品范围。

## Issues Encountered

- 初版故障回滚测试把 inode/mtime 也纳入失败恢复 snapshot；计划只要求恢复完整 path set 与 bytes，只有 exact no-op 要求 inode/mtime 不变。测试已分离这两个合同，避免声明无法通过 replace 保证的 inode 恢复。

## Known Stubs

None. 内部空容器和可选 descriptor 状态只用于会话初始化，不流向正式交付或公开输出。

## Threat Review

- T-48-10/T-48-11：根目录、support/history、managed files 均通过 held descriptor、`O_NOFOLLOW`、普通文件/目录类型与显式 allowlist 校验。
- T-48-12：authority approval digest 绑定 delta 与整个 current bytes snapshot；history post-validate 每个 stem 的完整 triple。
- T-48-13：所有 fault hooks、SIGINT、SIGTERM 后重新验证原 current exact path set 与 bytes。
- T-48-14：candidate、rollback、evidence 只存在于 owned `.work/run-*`，正常收尾不泄露到投递根。
- 未发现计划威胁模型之外的新网络端点、认证路径、schema 或外部依赖。

## Verification

- `python3 -m unittest skills/graduate-resume/scripts/test_delivery_transaction.py -v`：11/11 PASS。
- `python3 -m unittest discover -s skills/graduate-resume/scripts -p 'test_*.py' -v`：42/42 PASS。
- `python3 -m py_compile skills/graduate-resume/scripts/graduate_resume_delivery.py skills/graduate-resume/scripts/test_delivery_transaction.py`：PASS。
- `git diff --check HEAD~4..HEAD`：PASS。

## TDD Gate Compliance

- RED：`c1005f6`、`19d816d` 均先于对应实现提交且测试稳定失败。
- GREEN：`bcf36ec`、`a76acf1` 均使对应专项测试与相邻 graduate-resume 全量测试通过。
- 无需额外 REFACTOR 提交。

## User Setup Required

None - no external service configuration or package installation required.

## Next Phase Readiness

- 48-02 可直接将完整候选三件套写入 `DeliverySession.candidate_path()`，再调用 `preflight()` 与 `publish()`。
- 48-04 可在公开 batch CLI 中展示 `BundleDelta.removed` 和 `approval_digest`，确认后执行 authority 发布；无阻塞项。

## Self-Check: PASSED

- 两个 key files 均存在。
- 四个 TDD commits 均可在 git history 中找到。
- 11 项专项和 42 项 graduate-resume 全量测试全部通过。
- Phase 47 既有脏文件未被修改、暂存或提交。

---
*Phase: 48-deterministic-targeted-rendering-clean-batch-delivery*
*Completed: 2026-07-18*
