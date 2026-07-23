---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
plan: 08
subsystem: graduate-resume-secure-render-runtime
tags: [python, typst, no-follow, executable-snapshot, photo-snapshot, cleanup, tdd]

requires:
  - phase: 48-deterministic-targeted-rendering-clean-batch-delivery
    plan: 07
    provides: canonical no-follow bytes snapshot 与严格 metadata authority
  - phase: 48-deterministic-targeted-rendering-clean-batch-delivery
    plan: 09
    provides: 聚合 cleanup failure、rollback 与精确 delivery root 契约
provides:
  - Homebrew-compatible、descriptor-copied immutable Typst 0.15.0 snapshot
  - 照片 no-follow 单 descriptor bytes/hash/identity 快照
  - plan/render/batch 单 runtime 编排及 cleanup CLI fail-closed 回归
affects: [49-verification-runtime-uat, graduate-resume-rendering, graduate-resume-clean-delivery]

tech-stack:
  added: []
  patterns: [descriptor-copied-executable, explicit-runtime-dependency, bounded-photo-snapshot]

key-files:
  created:
    - skills/graduate-resume/scripts/graduate_resume_typst_runtime.py
  modified:
    - skills/graduate-resume/scripts/graduate_resume_layout.py
    - skills/graduate-resume/scripts/graduate_resume_typst.py
    - skills/graduate-resume/scripts/graduate_resume_render.py
    - skills/graduate-resume/scripts/graduate_resume_cli.py
    - skills/graduate-resume/scripts/test_render_contract.py
    - skills/graduate-resume/scripts/test_phase48_cli.py
    - skills/graduate-resume/scripts/test_theme_contract.py

key-decisions:
  - "Typst 只通过 PATH 定位一次源候选，随后从 held descriptor 复制到 mode 0700 私有目录中的 mode 0500 snapshot；版本、字体、照片与 PDF 均不再执行原路径。"
  - "照片 leaf 在 held assets-root 下 descriptor-relative O_NOFOLLOW 打开一次，完整 bytes、格式、SHA-256 与规范化输入共享同一快照。"
  - "plan/render/batch 各自恰好持有一个 TypstExecutable context；validate/target 保持与渲染工具链解耦。"

patterns-established:
  - "Executable snapshot: bounded symlink resolution -> held source fd -> hash/fsync copy -> exact version gate -> explicit runner consumers。"
  - "Photo snapshot: held root fd -> no-follow components/leaf -> bounded read -> identity recheck -> frozen bytes/hash。"

requirements-completed: [TARGET-03, DELIVERY-01, DELIVERY-02, DELIVERY-03]

duration: 46min
completed: 2026-07-18
---

# Phase 48 Plan 08: Immutable Typst 与照片快照 Summary

**毕业生简历生产渲染现在把照片和 Typst 都绑定到一次验证后的不可变对象，并让公开 CLI 在 cleanup 双故障下保持非零、无成功载荷和正确 current。**

## Performance

- **Duration:** 46 min
- **Started:** 2026-07-18T15:46:19Z
- **Completed:** 2026-07-18T16:32:01Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- 新增 bounded/cycle-safe symlink resolver，兼容真实 `/opt/homebrew/bin/typst` 相对 Homebrew symlink，并从 held source descriptor 创建私有 immutable Typst 0.15.0 snapshot。
- `ResolvedPhotoAsset` 冻结同一 no-follow leaf descriptor 的 bytes、SHA-256、device 与 inode；CLI 删除按逻辑路径二次读取。
- `validate_font_manifest`、`normalize_photo_bytes` 与三主题 `_compile_typst` 全部显式消费同一个 `TypstExecutable`。
- Phase 48 固定 registry 增至 15 个 gate，加入共享工具链 identity 与 cleanup CLI 双故障验收；全量 89 tests 通过。

## Task Commits

1. **Task 1 RED：immutable Typst resolver 失败矩阵** - `f71ce2f` (test)
2. **Task 1 GREEN：冻结并验证 Typst 0.15.0 snapshot** - `d04e606` (feat)
3. **Task 2 RED：照片 descriptor/TOCTOU 负例** - `3b2b545` (test)
4. **Task 2 GREEN：照片单 descriptor 快照消费** - `72e3e7a` (fix)
5. **Task 3 RED：共享 runtime 与 cleanup CLI gate** - `39b7ca4` (test)
6. **Task 3 GREEN：全部 Typst 消费者显式迁移** - `e11ed48` (feat)

## Files Created/Modified

- `skills/graduate-resume/scripts/graduate_resume_typst_runtime.py` - 安全 symlink chain、descriptor copy、snapshot identity/hash/version 与 bounded runner。
- `skills/graduate-resume/scripts/graduate_resume_layout.py` - `ResolvedPhotoAsset`、held assets-root no-follow 读取及显式字体 runtime。
- `skills/graduate-resume/scripts/graduate_resume_typst.py` - 照片规范化只通过已验证 snapshot runner 编译。
- `skills/graduate-resume/scripts/graduate_resume_render.py` - 三主题 PDF 编译显式消费同一 runtime。
- `skills/graduate-resume/scripts/graduate_resume_cli.py` - plan/render/batch 单 resolver context 与 cleanup failure CLI 映射。
- `skills/graduate-resume/scripts/test_render_contract.py` - Homebrew、fake version、symlink/copy swap 与照片 descriptor 回归。
- `skills/graduate-resume/scripts/test_phase48_cli.py` - 单 runtime 编排、固定 15-gate registry 与 cleanup 双故障回归。
- `skills/graduate-resume/scripts/test_theme_contract.py` - 旧字体契约测试迁移到显式 runtime 签名。

## Decisions Made

- PATH 只负责发现源候选；相对/绝对 symlink chain 最多 16 hops，最终 target 以 `O_NOFOLLOW` 普通可执行文件 descriptor 打开。
- snapshot 限制 128 MiB，私有目录/文件分别固定 `0700/0500`，复制前后核对 source identity/size 并 fsync file/directory。
- 照片上限固定 20 MiB；JPEG/PNG 完整边界、大小、bytes 与 hash 在同一 descriptor 上验证，安全错误不降级为 no-photo。
- runtime version 错误在字体校验之前以 `TYPST_RUNTIME_INVALID` fail closed，取代旧 PATH 为空时的 `FONT_MANIFEST_INVALID`。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] 同步旧主题测试到显式 runtime 签名**
- **Found during:** Task 3（原子迁移全部 Typst 消费者）
- **Issue:** `test_theme_contract.py` 仍直接调用旧 `validate_font_manifest(fonts_root)`，会阻塞全量回归且保留半迁移测试契约。
- **Fix:** 测试通过 `resolve_typst_executable()` 获取已验证 runtime，再调用新强制签名；同时把过短伪 JPEG 调整为满足新完整边界检查的最小合法 bytes。
- **Files modified:** `skills/graduate-resume/scripts/test_theme_contract.py`
- **Verification:** theme contract 7/7 PASS，graduate-resume 全量 89/89 PASS。
- **Committed in:** `e11ed48`

---

**Total deviations:** 1 auto-fixed（1 Rule 3）。
**Impact on plan:** 仅同步直接受生产签名迁移影响的旧测试，没有扩展运行时或 Phase 49 范围。

## Issues Encountered

- cleanup fault 测试会关闭 unittest 进程的输出描述符，使工具提前显示 completed；改用临时日志与进程检查后确认 Phase 48 CLI 22/22、全量 89/89 均真实完成，遗留测试进程已安全终止。

## Known Stubs

None. 扫描到的空集合与 `None` 均为状态初始化或明确可选输入，没有流向正式渲染的 placeholder、TODO、FIXME 或未接通 mock。

## Threat Review

- `T-48-G08-01/04/05`：照片 root/component/leaf symlink、特殊文件、超限、截断格式与读取变化均在 candidate/delivery mutation 前失败；正式 Typst 只内嵌 normalized PNG bytes。
- `T-48-G08-02/03`：真实 Homebrew chain 通过；dangling/cycle/hop overflow/fake 9.9/copy identity change 失败；源 symlink/target 在 final check 后替换不改变 snapshot 消费。
- `T-48-G08-06`：成功 publication cleanup failure 保留新 current，rollback+cleanup 双故障保留开始快照，CLI 均无 success payload。
- 未新增网络 endpoint、认证路径、凭据、数据库/schema 或计划威胁模型之外的 trust boundary。

## Verification

- `python3 -m unittest skills/graduate-resume/scripts/test_render_contract.py -v`：18/18 PASS。
- `python3 -m unittest skills/graduate-resume/scripts/test_phase48_cli.py -v`：22/22 PASS，133.237 秒。
- `python3 -m unittest discover -s skills/graduate-resume/scripts -p 'test_*.py' -v`：89/89 PASS，121.885 秒。
- `python3 skills/graduate-resume/scripts/graduate_resume_cli.py verify`：4 valid、6 invalid、5 layout fixtures 全部符合预期。
- `python3 -m py_compile ...`、`git diff --check ca027d8..HEAD`：PASS。
- `gsd-sdk query verify.key-links .../48-08-PLAN.md`：4/4 VERIFIED，包括 `resolve_typst_executable` 与 `typst_executable` 两条新增链接。

## TDD Gate Compliance

- Task 1：RED `f71ce2f` 因 runtime 模块不存在而失败；GREEN `d04e606` 后 16/16 render contract 通过。
- Task 2：RED `3b2b545` 因缺少 `ResolvedPhotoAsset`、no-follow bounded reader 与 CLI snapshot 消费而失败；GREEN `72e3e7a` 后 38/38 窄回归通过。
- Task 3：RED `39b7ca4` 明确得到 resolver context 计数 `0 != 1`；GREEN `e11ed48` 后共享 runtime 与 cleanup 两项 2/2 通过。

## User Setup Required

None - no external service configuration required. 本机只需仓库既有、已锁定的 Typst 0.15.0。

## Next Phase Readiness

- Phase 48 五项生产阻断均已由 48-07、48-08、48-09 关闭；本计划 4/4 key-links 和全量回归通过。
- 可进入 Phase 49 的 PDF 结构验证、六 runtime 文档/聚合验证与跨环境字体 UAT；本计划未提前实现这些范围。

## Self-Check: PASSED

- 1 个 key-file.created、7 个计划 key-files.modified 及本 SUMMARY 均存在。
- `f71ce2f`、`d04e606`、`3b2b545`、`72e3e7a`、`39b7ca4`、`e11ed48` 均存在于 git history，三个 RED 均先于对应 GREEN。
- render contract 18/18、Phase 48 CLI 22/22、graduate-resume 全量 89/89、fixture verify、py_compile、diff check 与 key-links 4/4 全部通过。

---
*Phase: 48-deterministic-targeted-rendering-clean-batch-delivery*
*Completed: 2026-07-18*
