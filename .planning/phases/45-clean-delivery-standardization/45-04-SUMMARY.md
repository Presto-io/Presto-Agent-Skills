---
phase: 45-clean-delivery-standardization
plan: 04
subsystem: delivery
tags: [filesystem-safety, held-descriptor, rollback, pptx, managed-assets]

requires:
  - phase: 45-clean-delivery-standardization
    provides: explicit DeliverySpec, fixed fault registry, and clean-delivery state machine
provides:
  - Whole-bundle reviewed Markdown, validated PPTX, and managed referenced-assets transaction
  - Exact no-op detection, same-sequence history, and seven-fault handled rollback
  - Best-effort evidence isolation and immutable sources behavior
  - Six-runtime school-pptx clean-delivery contract
affects: [45-08, 45-09, school-pptx]

tech-stack:
  added: []
  patterns: [held-root-descriptor, dynamic-managed-set, same-sequence-assets, evidence-only-best-effort]

key-files:
  created:
    - skills/school-pptx/fixtures/clean-delivery/confirmed-assets.md
    - skills/school-pptx/fixtures/clean-delivery/assets/robot-arm.png
  modified:
    - skills/school-pptx/scripts/pptx_render.py
    - skills/school-pptx/scripts/verify_markdown_contract.py
    - skills/school-pptx/scripts/verify_pptx_renderer.py
    - skills/school-pptx/SKILL.md
    - skills/school-pptx/references/renderer-and-pagination.md
    - skills/school-pptx/references/verification-contract.md

key-decisions:
  - "DeliverySpec is the exact reviewed Markdown, validated PPTX, and confirmed assets/... paths that remain referenced by the delivered bundle."
  - "Structurally editable best-effort output remains owned work evidence and never becomes current when parser, planner, runtime, or validation diagnostics are non-zero."
  - "Normal publication never mutates sources/ and archives old pair plus managed assets under one sequence so archived Markdown references remain resolvable."

patterns-established:
  - "Dynamic managed bundle: equality checks both exact relative path set and bytes; identical publication preserves current inode and mtime."
  - "Descriptor-safe cleanup: an owned candidate root or temp replaced by a symlink is unlinked without following or traversing its external target."

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

duration: 38 min
completed: 2026-07-16
---

# Phase 45 Plan 04: School PPTX Whole-Bundle Delivery Summary

**School PPTX 现以 reviewed Markdown、validated PPTX 和按需 managed referenced assets 组成完整事务，并在 no-op、history、handled failure 与 best-effort 路径上保持整套一致。**

## Performance

- **Duration:** 38 min
- **Started:** 2026-07-16T09:15:10+08:00
- **Completed:** 2026-07-16T09:53:02+08:00
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments

- 扩展既有 held-descriptor publisher，加入 same-root lock、owned `.work/<run-id>/{candidate,rollback,evidence}`、exact path-set+bytes no-op、max+1 history 和完整 bundle rollback。
- changed 发布将旧 Markdown、PPTX 与全部旧 managed assets 放入同一 sequence；归档 Markdown 的 `assets/...` 引用可在该 sequence 内解析。
- parser、planner、runtime 或 validation 非零时，best-effort deck 只存在于 owned evidence 生命周期，不发布为 current。
- 真实 public render 回归覆盖 first、identical、changed、`001/003 -> 004`、七 fault、失败路径、unknown、legacy media、symlink、traversal、锁和 cleanup。
- 同步 current artifact、verify workdir、人工 UAT 与六 runtime 的安装、权限和 fallback 边界。

## Task Commits

1. **Task 1: whole-bundle PPTX delivery transaction** - `73149d9` (feat)
2. **Task 2: publication regression and runtime contract** - `8261341` (test)

## Files Created/Modified

- `skills/school-pptx/scripts/pptx_render.py` - whole-bundle DeliverySpec、history、rollback、best-effort 隔离和 descriptor-safe cleanup。
- `skills/school-pptx/scripts/verify_pptx_renderer.py` - 真实 public render transaction gate、七 fault registry 和跨目录快照断言。
- `skills/school-pptx/scripts/verify_markdown_contract.py` - clean-delivery fixture 与 confirmed asset 契约。
- `skills/school-pptx/fixtures/clean-delivery/confirmed-assets.md` - 持续引用 managed asset 的受控 Markdown fixture。
- `skills/school-pptx/fixtures/clean-delivery/assets/robot-arm.png` - 与既有 fixture 字节一致的 confirmed managed asset。
- `skills/school-pptx/SKILL.md` - exact current bundle、支持目录和 runtime 安全入口。
- `skills/school-pptx/references/renderer-and-pagination.md` - candidate-first render 与 best-effort evidence 边界。
- `skills/school-pptx/references/verification-contract.md` - publication gate、verify workdir、history/rollback 和人工 UAT 边界。

## Decisions Made

- managed asset 必须同时满足安全相对路径、已确认纳管和被交付 Markdown/PPTX 持续引用；未引用输入不会复制到 `assets/` 或 history。
- `sources/` 不属于普通发布 mutation/history list，在 first、change、no-op 和 failure 中保持 byte-identical。
- 自动目录与 OOXML gate 不签署 PowerPoint/WPS 视觉通过；真实 viewer UAT 仍由人工完成。
- portable guarantee 只覆盖逐路径 replace 与 handled failure/INT/TERM rollback，不声称 SIGKILL、断电或多路径硬原子。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Cleanup could follow a candidate root exchanged for a symlink**
- **Found during:** Task 2 descriptor-race regression
- **Issue:** 攻击者在 cleanup 前把 candidate root 或 owned temp 替换为 symlink 时，清理逻辑可能遍历外部目录，或把 symlink 当作普通 owned file 处理。
- **Fix:** cleanup 先做 no-follow identity/type 检查；symlink 仅解除自身，不遍历其目标，也不按普通 owned file 删除。
- **Files modified:** `skills/school-pptx/scripts/pptx_render.py`, `skills/school-pptx/scripts/verify_pptx_renderer.py`
- **Verification:** descriptor race gate 通过，外部 sentinel SHA-256 保持不变。
- **Committed in:** `8261341`

---

**Total deviations:** 1 auto-fixed bug. **Impact:** 收紧 owned cleanup 的安全边界，不改变公开 render 输出或 DeliverySpec。

## Issues Encountered

- 计划指定的中央命令 `python3 test/clean-delivery/verify_clean_delivery.py --skill school-pptx` 当前不可用；45-01 foundation harness 仅支持 `--self-test`。遵守 shared-file ownership，未越界修改中央 harness；真实 `--skill` 路由明确留给 45-09，当前以 skill-local aggregate、真实 public render 和 foundation self-test 提供等价证据。

## User Setup Required

None - 未新增依赖或外部服务配置。人工视觉验收仍需 PowerPoint 或 WPS Presentation。

## Verification Evidence

- `uv run --with 'python-pptx==1.0.2' --with Pillow --with lxml --with PyYAML python skills/school-pptx/scripts/verify_pptx_renderer.py --self-test delivery-transaction` - PASS。
- 同一 uv 环境运行 `verify_pptx_renderer.py` 无参数 aggregate - PASS：既有 Phase 43 固定 21 gate 与新 delivery transaction gate 全部通过。
- 21-gate registry - PASS：`required == called`、唯一、`dynamic_skips == 0`。
- Delivery fault registry - PASS：七个 required fault 全部调用，`dynamic_skips == 0`。
- first/identical/changed - PASS；existing `001/003` 产生 `004`，identical 保持 inode/mtime。
- history asset resolution、`sources_unchanged`、`unreferenced_not_copied` 与 `best_effort_published: false` - PASS。
- publication safety、descriptor race、object error bounded、media descriptor binding、template reader security、determinism、Phase 41/42 regression - PASS。
- whole-folder isolated copy - PASS：`--help` 与 Markdown contract 可运行，无 sibling/root runtime import。
- Python `py_compile` 与 `git diff --check` - PASS。

## Next Phase Readiness

- School PPTX adapter 已可进入 45-08 仓库级文档同步和 45-09 中央六技能 strict aggregate 接线。
- skill folder 内无剩余实现 blocker；人工 PowerPoint/WPS UAT 保持为明确人工边界。

## Self-Check: PASSED

- 两个 fixture created files 与六个 modified files 均存在。
- `73149d9` 与 `8261341` 可由 git object database 验证。
- 所有任务 acceptance criteria 已由真实 public render、固定 registry、fault matrix 和隔离安装证据覆盖。
- 中央 `--skill` harness 缺口已明确归属 45-09，未错误声明为通过。

---
*Phase: 45-clean-delivery-standardization*
*Completed: 2026-07-16*
