---
phase: 45-clean-delivery-standardization
plan: 05
subsystem: delivery
tags: [filesystem-safety, offline-html, rollback, managed-assets, evidence-isolation]

requires:
  - phase: 45-clean-delivery-standardization
    provides: explicit DeliverySpec, fixed fault registry, and clean-delivery state machine
provides:
  - Markdown plus offline HTML candidate-first delivery transaction
  - Exact no-op, whole-bundle history, managed asset reference preservation, and handled rollback
  - Manifest and verification evidence isolation from normal current delivery
  - Six-runtime school-presentation clean-delivery contract
affects: [45-08, 45-09, school-presentation]

tech-stack:
  added: []
  patterns: [dynamic-managed-assets, pair-transaction, external-evidence-guard, caller-owned-verify-workdir]

key-files:
  created:
    - skills/school-presentation/scripts/school_presentation/delivery.py
    - skills/school-presentation/scripts/school_presentation/test_delivery.py
  modified:
    - skills/school-presentation/scripts/school_presentation/_engine.py
    - skills/school-presentation/SKILL.md
    - skills/school-presentation/references/verification-contract.md
    - skills/school-presentation/references/authoring-and-layout.md

key-decisions:
  - "Normal current is exactly one reviewed Markdown plus offline HTML pair and its explicitly referenced managed assets; manifests and verification evidence remain external."
  - "A same-root input Markdown may seed first publication, but every handled failure restores its original bytes and never creates false history."
  - "Legacy media requires confirmation-based migration to assets; required missing assets fail before publication while existing optional fallback behavior remains evidence-only."

patterns-established:
  - "HTML candidate gate: UTF-8, non-empty, size, offline references, required DOM tokens, and exact asset references all pass before current mutation."
  - "Verification isolation: each deterministic render uses its own delivery subroot while manifests and aggregate evidence stay in the caller-owned workdir."

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

duration: 19 min
completed: 2026-07-16
---

# Phase 45 Plan 05: School Presentation HTML Pair Transaction Summary

**School Presentation 现以 reviewed Markdown、offline HTML 与明确 referenced assets 完成 candidate 验门、整包 history 和 handled rollback，并将 manifest/verify/PDF evidence 完全隔离于 normal current。**

## Performance

- **Duration:** 19 min
- **Started:** 2026-07-16T10:09:00+08:00
- **Completed:** 2026-07-16T10:28:00+08:00
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- 新增 skill-local `DeliverySession`，覆盖同根锁、owned `.work/<run-id>/{candidate,rollback,evidence}`、exact path-set+bytes no-op、max+1 history 和七 fault/INT/TERM rollback。
- `cmd_render()` 先在 candidate 中写 reviewed Markdown、offline HTML、ephemeral manifest 和 referenced assets，完成 size/offline/DOM/assets gate 后仅发布 current pair/assets。
- `--manifest` 只允许显式独立 evidence path；`verify --workdir` 使用四个独立 delivery 子目录并证明 normal root 无 manifest、verification-manifest、截图、diff、日志或 failed HTML。
- history 同 sequence 保存旧 pair 与旧 Markdown 所需 assets，归档引用可解析，未引用输入不复制，`sources/` 在成功、no-op 和失败路径保持不变。
- 同步 exact artifact、legacy media 确认迁移、浏览器/PDF 人工边界和六 runtime whole-folder/fallback/权限说明。

## Task Commits

1. **Task 1 RED: HTML delivery transaction tests** - `9b3b16b` (test)
2. **Task 1 GREEN: pair/assets transaction helper** - `145f330` (feat)
3. **Task 2 RED: render evidence isolation tests** - `cd302fd` (test)
4. **Task 2 GREEN: candidate-first render integration** - `77c5628` (feat)
5. **Task 3: artifact and six-runtime contract** - `40bfc6e` (docs)

## Files Created/Modified

- `skills/school-presentation/scripts/school_presentation/delivery.py` - Markdown/HTML/assets transaction、history、rollback、lock 和 owned cleanup。
- `skills/school-presentation/scripts/school_presentation/test_delivery.py` - helper 与真实 render 的 9 项回归。
- `skills/school-presentation/scripts/school_presentation/_engine.py` - candidate-first render、manifest guard、assets resolver 和 caller-owned verify roots。
- `skills/school-presentation/SKILL.md` - exact current、支持目录、evidence/PDF 边界和六 runtime notes。
- `skills/school-presentation/references/verification-contract.md` - publication gates、root pollution、history/assets 与 verify workdir 契约。
- `skills/school-presentation/references/authoring-and-layout.md` - persistent assets authoring 和 confirmed legacy migration 规则。

## Decisions Made

- `--html` 的 parent/stem 决定 stable current pair；当输入恰为同 stem/root Markdown 时，它只作为 first-publication seed，失败必须恢复原 bytes。
- external manifest 在 current mutation 前安全写入独立 evidence path；normal delivery root 及其支持目录内的 manifest target 一律拒绝。
- normal render 不解析或搬迁 legacy `media/`；confirmed assets 必须使用安全 `assets/...` 相对引用，missing required asset 阻断发布。
- HTML 自动 gate 不签署浏览器视觉或最终 PDF；一键 browser export 与 `bookmark-pdf` 仍是显式人工/postprocess 边界。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Made `_engine` import-safe for TDD and package reuse**
- **Found during:** Task 2 RED integration tests
- **Issue:** `_engine.py` unconditionally executed `main(sys.argv[2:])` on import, so direct module tests exited through argparse before exercising `cmd_render()`.
- **Fix:** Added the standard `if __name__ == "__main__"` guard and retained the existing CLI module invocation path.
- **Files modified:** `skills/school-presentation/scripts/school_presentation/_engine.py`
- **Verification:** 9/9 unittest tests, public shell `--help/info/render/verify`, and isolated whole-folder invocation all pass.
- **Committed in:** `77c5628`

---

**Total deviations:** 1 auto-fixed blocking issue. **Impact:** Improves import safety without changing public command names, flags, rendering content, or final artifacts.

## Issues Encountered

- 计划指定的中央命令 `python3 test/clean-delivery/verify_clean_delivery.py --skill school-presentation` 与 `--gate documentation_runtime_contract_gate` 当前不可用；45-01 foundation harness 仅暴露 `--self-test`。遵守 shared-file ownership，未修改中央 harness；真实 `--skill/--gate` 接线明确留给 45-09。

## User Setup Required

None - 未新增依赖或外部服务配置。浏览器 PDF export 与可选 `bookmark-pdf` 仍使用已有人工/`pypdf` 边界。

## Verification Evidence

- `python3 -m unittest skills/school-presentation/scripts/school_presentation/test_delivery.py -v` — PASS, 9 tests。
- `skills/school-presentation/scripts/school-presentation.sh verify --workdir <owned-mktemp>` — PASS，deterministic/interaction/print/offline/16:9/4:3 与 root pollution aggregate 全过。
- 真实 public CLI first/identical/changed + seven-fault matrix — PASS；每个 fault 非零、无 traceback、current/history/sources hashes 不变且 `.work` 收尾。
- 真实 history/reference matrix — PASS：`001/003 -> 004`、archived `assets/diagram.png` 可解析、unreferenced input 不复制、identical inode/mtime 不变。
- Whole-folder isolated copy — PASS：`--help`、`info`、真实 render 均不依赖 sibling skill 或仓库根 runtime helper。
- `python3 test/clean-delivery/verify_clean_delivery.py --self-test all` — PASS；中央 `--skill/--gate` route 预期返回 usage error，归属 45-09。
- Python `py_compile`、shell `bash -n`、production static import scan 与 `git diff --check` — PASS。

## Next Phase Readiness

- School Presentation adapter 已可进入 45-08 仓库级文档同步与 45-09 中央六技能 strict aggregate 接线。
- skill folder 内无剩余实现 blocker；browser/PDF visual UAT 保持为明确人工边界。

## Self-Check: PASSED

- 两个 created files 与四个 modified files 均存在。
- 五个 `45-05` task commits 均可由 git object database 验证。
- 所有任务 acceptance criteria 与计划级 verification 已由 unit、真实 public CLI、完整 verify 和 isolated installation 重跑通过。
- `REQUIREMENTS.md` 中本计划 11 个 requirement IDs 已保持 Complete；未越界改动 shared central harness。

---
*Phase: 45-clean-delivery-standardization*
*Completed: 2026-07-16*
