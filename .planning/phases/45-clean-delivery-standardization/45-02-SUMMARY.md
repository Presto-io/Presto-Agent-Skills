---
phase: 45-clean-delivery-standardization
plan: 02
subsystem: delivery
tags: [filesystem-safety, candidate-first, rollback, typst, xlsx]

requires:
  - phase: 45-clean-delivery-standardization
    provides: explicit DeliverySpec, fixed fault registry, and clean-delivery state machine
provides:
  - Skill-local fixed four-file DeliverySession with held-root no-follow publication
  - Candidate-first end-of-term Markdown, Typst, PDF, and XLSX generation and validation
  - Exact no-op detection, whole-bundle history, seven-fault and signal rollback
  - Six-runtime end-of-term clean-delivery contract
affects: [45-08, 45-09, end-of-term-teaching-materials]

tech-stack:
  added: []
  patterns: [fixed-managed-set, descriptor-relative-replace, deterministic-pdf, whole-bundle-history]

key-files:
  created:
    - skills/end-of-term-teaching-materials/scripts/end_of_term/delivery.py
    - skills/end-of-term-teaching-materials/scripts/end_of_term/test_delivery.py
  modified:
    - skills/end-of-term-teaching-materials/scripts/end_of_term/_engine.py
    - skills/end-of-term-teaching-materials/SKILL.md
    - skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md

key-decisions:
  - "The end-of-term current delivery is always the exact fixed four-file set; normal publication never infers or mutates additional root files."
  - "Typst compilation sets a default SOURCE_DATE_EPOCH so byte-identical inputs produce byte-identical PDFs and true no-op delivery."
  - "OpenClaw and Hermes Agent support remains installation-time verified with an explicit shell fallback and no automatic-discovery claim."

patterns-established:
  - "Fixed bundle transaction: candidate validation precedes root inspection, exact equality preserves inode/mtime, and changed publication archives one verified prior bundle."
  - "Owned cleanup: only explicit four names, the current run tree, lock, and uncommitted history sequence may be removed."

requirements-completed:
  - CLEAN-01
  - CLEAN-02
  - CLEAN-03
  - REV-01
  - REV-02
  - REV-03
  - REV-04
  - SAFE-01
  - VERIFY-01
  - DOCS-01
  - RUNTIME-01

duration: 21 min
completed: 2026-07-16
---

# Phase 45 Plan 02: End-of-Term Fixed Bundle Transaction Summary

**期末教学材料四件套现已在 skill-local candidate 中完整生成和验门，并以 no-op、整包 history 与可验证回滚安全发布**

## Performance

- **Duration:** 21 min
- **Started:** 2026-07-16T00:06:27Z
- **Completed:** 2026-07-16T00:27:11Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- 新增 held-root、`O_NOFOLLOW`、显式四文件、same-root lock、max+1 history 和 owned cleanup 的 `DeliverySession`。
- 将公开 `deliver --input --out-dir` 改为 candidate-first，Markdown/Typst/PDF/XLSX 全部验证后才触碰 current。
- 真实公开 CLI 证明 first、identical、changed、history gap 和七个标准 fault；所有失败保持 current/history hashes 不变。
- 同步固定 artifact、支持目录生命周期、真实原子性边界和六 runtime 安装/权限/fallback 说明。

## Task Commits

1. **Task 1 RED: 固定四件套事务行为** - `cfbd426` (test)
2. **Task 1 GREEN: DeliverySession** - `a9795ff` (feat)
3. **Task 2 RED: candidate-first deliver 行为** - `0d48b3b` (test)
4. **Task 2 GREEN: 真实 deliver 与格式门** - `c74ea27` (feat)
5. **Task 3: artifact 与六 runtime 契约** - `d330cd1` (docs)

## Files Created/Modified

- `skills/end-of-term-teaching-materials/scripts/end_of_term/delivery.py` - 固定四件套事务、history、回滚、锁和 owned cleanup。
- `skills/end-of-term-teaching-materials/scripts/end_of_term/test_delivery.py` - 事务与真实 deliver 的 9 项回归。
- `skills/end-of-term-teaching-materials/scripts/end_of_term/_engine.py` - candidate producer、四格式 gate 与确定性 Typst PDF。
- `skills/end-of-term-teaching-materials/SKILL.md` - 简洁 current/support/runtime 安全入口。
- `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md` - 完整 artifact、history、rollback 和人工边界。

## Decisions Made

- 固定四文件名同时是 discovery 与 mutation authority；partial、unknown、symlink、legacy/stale work 均失败关闭。
- PDF bytes 纳入 exact bundle equality，因此使用 Typst 支持的 `SOURCE_DATE_EPOCH` 默认值消除编译元数据抖动，不改变页面内容或公开 CLI。
- 自动 gate 只证明 UTF-8、PDF header、OOXML/四列/排序等最小可读性，人工内容与版式验收仍由教师拥有。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Typst PDF metadata prevented identical no-op**
- **Found during:** Task 2 真实 public CLI regression
- **Issue:** 同一 Markdown 连续编译得到不同 PDF bytes，导致第二次运行错误创建 history 并替换全部 current inode。
- **Fix:** 为 `typst compile` 提供默认 `SOURCE_DATE_EPOCH=0`，同时保留调用方显式环境覆盖。
- **Files modified:** `skills/end-of-term-teaching-materials/scripts/end_of_term/_engine.py`
- **Verification:** 真实 public CLI 输出 `first identical changed`，identical 前后四文件 inode/mtime 完全一致且无 history。
- **Committed in:** `c74ea27`

---

**Total deviations:** 1 auto-fixed (1 bug). **Impact:** 修复是 exact-bytes no-op 正确性的必要条件，不改变内容模型、版式、评分或产物格式。

## Issues Encountered

- 计划指定的中央命令 `python3 test/clean-delivery/verify_clean_delivery.py --skill end-of-term-teaching-materials` 当前不可用；45-01 foundation harness 只暴露 `--self-test`，其 SUMMARY 明确六技能真实接线留到 45-09。为遵守本计划 files ownership，未越界修改 shared harness；改以复制后的完整 skill folder、真实 public CLI 七故障矩阵、skill-local 9 项测试和 foundation `--self-test all` 提供等价证据。

## User Setup Required

None - no new dependencies or external service configuration required. Existing final PDF delivery still requires the documented Typst CLI.

## Verification Evidence

- `python3 -m unittest skills/end-of-term-teaching-materials/scripts/end_of_term/test_delivery.py -v` — PASS, 9 tests.
- `python3 -m py_compile skills/end-of-term-teaching-materials/scripts/end_of_term/*.py` — PASS.
- `bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh` — PASS.
- Copied whole skill folder + real public CLI — PASS: `first identical changed`; existing `001/003` produced `004`.
- Real public CLI seven-fault matrix — PASS: every fault exited non-zero, current/history hashes matched, `.work` absent after cleanup.
- `python3 test/clean-delivery/verify_clean_delivery.py --self-test all` — PASS.
- Documentation runtime contract assertions — PASS for exact four names, four support dirs, exactly six runtime rows, OpenClaw/Hermes installation-time verification and explicit fallback.

## Next Phase Readiness

- End-of-term adapter is ready for repository-level documentation synchronization in 45-08 and central six-skill harness wiring in 45-09.
- No implementation blocker remains inside the skill folder.

## Self-Check: PASSED

- Both created files exist and all five `45-02` task commits are present.
- All owned acceptance criteria and plan success criteria passed through skill-local and real public CLI evidence.
- The unavailable shared `--skill` harness route is explicitly deferred to its owning 45-09 plan rather than silently reported as passing.

---
*Phase: 45-clean-delivery-standardization*
*Completed: 2026-07-16*
