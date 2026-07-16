---
phase: 45-clean-delivery-standardization
plan: 03
subsystem: delivery
tags: [filesystem-safety, candidate-first, rollback, typst, pdf]

requires:
  - phase: 45-clean-delivery-standardization
    provides: explicit DeliverySpec, fixed fault registry, and clean-delivery state machine
provides:
  - Skill-local optional two/three-file DeliverySession with held-root publication
  - Candidate-first Markdown, Typst, expected comparison, and optional PDF validation
  - Exact no-op detection, whole-bundle history, seven-fault and signal rollback
  - Six-runtime tiaokedan clean-delivery contract
affects: [45-08, 45-09, tiaokedan]

tech-stack:
  added: []
  patterns: [optional-managed-set, same-root-same-stem, candidate-pdf-compile, whole-bundle-history]

key-files:
  created:
    - skills/tiaokedan/scripts/delivery_transaction.py
    - skills/tiaokedan/scripts/test_delivery_transaction.py
  modified:
    - skills/tiaokedan/scripts/tiaokedan_renderer.py
    - skills/tiaokedan/SKILL.md
    - skills/tiaokedan/references/pdf-workflow.md
    - skills/tiaokedan/references/markdown-contract.md

key-decisions:
  - "The --typ path owns the delivery root and stable stem; optional --pdf must use the same root and stem and changes the exact managed set."
  - "Expected comparison and Typst PDF compilation consume only the owned candidate, so their failures cannot mutate current delivery."
  - "Legacy .tiaokedan, media, unknown, symlink, partial, and stale-work states require audit instead of automatic migration or cleanup."

patterns-established:
  - "Optional bundle transaction: pair/triple path-set equality is checked alongside bytes, including PDF addition and removal."
  - "Bounded evidence: public expected mismatch output is capped while detailed diff remains only in the owned run lifecycle."

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

duration: 12 min
completed: 2026-07-16
---

# Phase 45 Plan 03: Tiaokedan Optional Bundle Transaction Summary

**调课单现以同 root/stem 的 Markdown+Typst 二件套或 optional PDF 三件套完成 candidate 验门、整包 history 与 handled failure 回滚**

## Performance

- **Duration:** 12 min
- **Started:** 2026-07-16T00:35:11Z
- **Completed:** 2026-07-16T00:47:11Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- 新增 held-root、`O_NOFOLLOW`、same-root lock、显式 pair/triple、max+1 history 和 owned cleanup 的 `DeliverySession`。
- 将公开 `render --input --typ [--pdf] [--expected-typ]` 改为 candidate-first，expected 与 PDF compile/format gate 均在 current mutation 前完成。
- 真实 public CLI 证明 first、identical、changed、optional PDF 增减、history gap、七 fault、generation/validation failure、unknown、symlink 与 path mismatch。
- 同步 exact artifact、支持目录生命周期、真实原子性边界和六 runtime 安装/权限/fallback 说明。

## Task Commits

1. **Task 1 RED: optional bundle 事务行为** - `049e637` (test)
2. **Task 1 GREEN: pair/triple DeliverySession** - `f5a4c30` (feat)
3. **Task 2 RED: candidate-first renderer 行为** - `8a357fd` (test)
4. **Task 2 GREEN: expected/PDF candidate 接线** - `fa88b3a` (feat)
5. **Task 3: artifact 与六 runtime 契约** - `e3f93ca` (docs)
6. **Acceptance audit: optional PDF 移除回归** - `d474836` (test)

## Files Created/Modified

- `skills/tiaokedan/scripts/delivery_transaction.py` - optional exact set、history、rollback、锁和 owned cleanup。
- `skills/tiaokedan/scripts/test_delivery_transaction.py` - 事务与真实 public CLI 的 11 项回归。
- `skills/tiaokedan/scripts/tiaokedan_renderer.py` - candidate Markdown/Typst/PDF、expected evidence 与格式 gate。
- `skills/tiaokedan/SKILL.md` - 简洁 current/support/runtime 安全入口。
- `skills/tiaokedan/references/pdf-workflow.md` - 完整 artifact、history、rollback 与人工边界。
- `skills/tiaokedan/references/markdown-contract.md` - finalized Markdown 到 candidate/current 的关系。

## Decisions Made

- `--typ` basename 是唯一 stem authority；`--pdf` 不允许跨 root、不同 stem 或不安全 component。
- pair 与 triple 是两个不同 exact path sets，PDF 增加或移除都归档完整旧 bundle；identical 必须 path set 和 bytes 同时相等。
- 自动 gate 只证明 Markdown/Typst UTF-8、PDF header、根白名单与事务恢复；教师仍负责事实、版式和最终 PDF 视觉验收。

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- 计划指定的中央命令 `python3 test/clean-delivery/verify_clean_delivery.py --skill tiaokedan` 与 `--gate documentation_runtime_contract_gate` 当前不可用；45-01 foundation harness 仅暴露 `--self-test`，真实技能路由明确留给 45-09。遵守 shared-file ownership，未越界修改中央 harness；改以 skill-local 11 项测试、真实 public CLI、真实 Typst 和机械文档断言提供等价证据。

## User Setup Required

None - no new dependencies or external service configuration required. Existing optional PDF delivery still requires the documented Typst CLI.

## Verification Evidence

- `python3 -m unittest skills/tiaokedan/scripts/test_delivery_transaction.py -v` — PASS, 11 tests。
- `bash -n skills/tiaokedan/scripts/tiaokedan.sh` — PASS。
- `python3 -m py_compile skills/tiaokedan/scripts/*.py` — PASS。
- 真实安装的 `typst` + public CLI — PASS：首次三件套发布，Markdown/Typst/PDF 非空且 PDF header 为 `%PDF-`。
- 真实 public CLI 七 fault 矩阵 — PASS：每项非零、有界诊断、current/history snapshot 不变且 owned `.work` 收尾。
- 真实 public CLI failure/no-op/history/unknown/symlink/path mismatch — PASS；existing `001/003` 产生 `004`，optional PDF 移除归档完整 triple。
- `python3 test/clean-delivery/verify_clean_delivery.py --self-test all` — PASS。
- 源码静态扫描 — PASS：生产模块无 sibling/root harness import，无 broad glob/rmtree 或提前删除 final PDF。
- 文档机械断言 — PASS：exact pair/triple、四支持目录、六 runtime、显式 fallback、OpenClaw/Hermes installation-time verification 与真实原子性边界均可找到。

## Next Phase Readiness

- Tiaokedan adapter 已可进入 45-08 仓库级文档同步与 45-09 中央六技能 harness 接线。
- skill folder 内无剩余实现 blocker；中央 `--skill/--gate` 路由仍由 45-09 owning plan 完成。

## Self-Check: PASSED

- 两个 created files 与四个 modified files 均存在。
- 六个 `45-03` production/task commits 均可由 git object database 验证。
- 所有任务 acceptance criteria 与计划级 verification 已通过 skill-local、真实 CLI 和等价 harness 证据重跑。

---
*Phase: 45-clean-delivery-standardization*
*Completed: 2026-07-16*
