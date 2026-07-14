---
phase: 43-editable-pptx-renderer-and-pagination
plan: 08
subsystem: pptx-security-aggregate
tags: [pptx, zip-security, xml-security, regression-gates, traceability]

requires:
  - phase: 43-07
    provides: frozen slots, cover metadata, visible numbering, and native table row heights
provides:
  - bounded production ZIP/XML/relationship reader for public template-report
  - seven public malicious-package regressions with stable bounded error codes
  - fixed-order Phase 43 aggregate covering C-01, C-02, and W-01 through W-06
affects: [phase-43-verification, phase-44-verification]

tech-stack:
  added: []
  patterns: [metadata-first ZIP preflight, chunked bounded XML reads, exact aggregate traceability]

key-files:
  created:
    - skills/school-pptx/scripts/verify_template_manifest.py
    - .planning/phases/43-editable-pptx-renderer-and-pagination/43-08-SUMMARY.md
  modified:
    - skills/school-pptx/scripts/template_report.py
    - skills/school-pptx/scripts/verify_pptx_renderer.py

key-decisions:
  - "Public template-report validates all ZIP metadata before payload use, then parses only chunk-read bounded XML after rejecting entity declarations."
  - "Phase 43 aggregate uses one immutable 17-gate order and exact C-01/C-02/W-01..W-06 plus blocked-requirement mappings."
  - "Canonical output is 26 physical slides because 43-07 freezes three ordered two-column pairs as three physical pages."

patterns-established:
  - "Template package failures expose only stable TEMPLATE_PACKAGE_* codes without payloads, tracebacks, or internal paths."
  - "Aggregate evidence records required order, actual called order, zero dynamic skips, gap coverage, and direct requirement coverage."

requirements-completed: [PPTX-03, PPTX-04, PPTX-08, PPTX-10, VER-03]

duration: 18 min
completed: 2026-07-14
---

# Phase 43 Plan 08: Template Reader Security and Aggregate Summary

**Public template-report 现已使用有界 ZIP/XML reader，Phase 43 的 8 个 gap 与 4 个 blocked PPTX requirements 可由固定顺序 aggregate 一次性机械重验。**

## Performance

- **Duration:** 18 min
- **Started:** 2026-07-14T05:06:00Z
- **Completed:** 2026-07-14T05:24:39Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- 对最多 512 entries、单项 16 MiB、总计 96 MiB 和 4096 relationships 执行 metadata-first 预检与 chunked actual-byte 读取。
- 通过 public `school-pptx.sh template-report` 阻断 entry count、声明/实际大小、重复名称、路径逃逸、DOCTYPE/ENTITY 和 External relationship 七类恶意包。
- 将 `publication-descriptor-race`、`code-literal-roundtrip`、`object-error-bounded`、四项 frozen-plan gate 和 `template-reader-security` 纳入 17 项固定顺序 aggregate。
- 精确输出 C-01、C-02、W-01..W-06 的 `gap_coverage`，以及 PPTX-03/04/08/10、VER-03 的 direct `requirement_coverage`。

## Task Commits

1. **Task 1: 为 public template-report 实现有界 ZIP/XML reader** - `4800386`
2. **Task 2: 将 8 个 gap 专项门纳入 Phase 43 aggregate** - `e245e4d`

## Files Created/Modified

- `skills/school-pptx/scripts/template_report.py` - 增加生产 ZIP metadata 预检、分块读取、XML/relationship 安全边界和稳定错误码。
- `skills/school-pptx/scripts/verify_template_manifest.py` - 在 `TemporaryDirectory` 中生成并黑盒调用七类恶意 package 向量及四项边界测试。
- `skills/school-pptx/scripts/verify_pptx_renderer.py` - 注册 W-06，固定 17-gate aggregate，增加 gap/requirement traceability 和 public cover overflow。

## Decisions Made

- canonical PPTX 固定期望更新为 26 页：43-07 将 canonical 五个双栏块冻结成三组 `L/R` 配对，较旧 24 页期望合法增加 2 页。
- C-01 cleanup evidence 按归属区分：攻击者交换 symlink 可保留，但 owner/duplicate fd 关闭、renderer-owned inode 回收且无普通 temp、`.bak`、JSON 或日志。
- Phase 44 的 public `verify`、runtime adapter、兼容矩阵和 viewer UAT 均未在本计划实现或宣称通过。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] 更新 editable-objects 手工表格夹具以遵守 frozen row-height contract**
- **Found during:** Task 2 aggregate 首次运行
- **Issue:** 旧手工 `BlockFragment` 未携带 43-07 要求的 `row_heights_emu`，生产 emitter 正确返回 `PPTX_TABLE_ROW_HEIGHT_MISMATCH`。
- **Fix:** 从 manifest 的 `table.height - table_name.height` 派生预算，为两行夹具提供确定 frozen heights。
- **Files modified:** `skills/school-pptx/scripts/verify_pptx_renderer.py`
- **Verification:** 完整 `phase-43` aggregate 中 `editable-objects` PASS。
- **Committed in:** `e245e4d`

**2. [Rule 1 - Regression expectation] 同步 canonical 26 页合法 frozen pagination**
- **Found during:** Task 2 aggregate 第二次运行
- **Issue:** public render 与 plan 均稳定生成 26 页，但旧 `cli-publication` 仍断言 24 页。
- **Fix:** 将固定期望设为 26，并在 evidence 中说明三组双栏配对带来的 +2 页。
- **Files modified:** `skills/school-pptx/scripts/verify_pptx_renderer.py`
- **Verification:** public canonical render 退出 0，26 页非空可重开，成功 root 仅含 caller sentinel 与 `.md/.pptx`。
- **Committed in:** `e245e4d`

---

**Total deviations:** 2 auto-fixed（1 blocking test fixture，1 stale regression expectation）。**Impact:** 仅同步验证夹具与 43-07 已冻结行为，未改变生产分页或发射逻辑。

## Issues Encountered

- 默认 Python 3.14 未安装 `python-pptx`；PPTX 门禁使用本机现有 uv package archive 通过 `PYTHONPATH` 离线运行，未联网、未安装依赖、未在仓库创建环境。

## Verification

- `python3 -m py_compile ...template_report.py ...verify_template_manifest.py` - PASS。
- `verify_pptx_renderer.py template-reader-security` - PASS；七类 public 恶意 package 精确返回稳定 code，输出均低于 8 KiB，canonical 11 layouts PASS。
- `verify_markdown_contract.py fixture-example` - PASS；Phase 41 template/manifest 与 Phase 42 fixture regression 保持通过。
- `verify_pptx_renderer.py phase-43`（离线依赖路径）- PASS；17 个 gate 按 required/called 完全相同顺序执行，zero skip。
- aggregate canonical evidence - 26 slides、115 ZIP entries、125 relationships、10 pictures、2 native tables、18 groups、6 notes、唯一 closing、transition `none`。
- aggregate security evidence - caller sentinel byte-identical，C-01 fds 关闭/inode 回收，W-01/W-06 无 traceback 或绝对 workdir 泄漏。

## Next Phase Readiness

- Phase 43 的 gap closure plans 已全部执行，具备交给 orchestrator final phase verifier 的完整机械证据。
- 本总结不宣称 Phase 43 已通过最终 verification；PowerPoint/WPS 人工视觉与编辑 UAT 继续留在 Phase 44。

## Self-Check: PASSED

全部关键文件存在，两个 task commit 可定位，Task 1/Task 2 automated gates 与完整 plan-level aggregate 均通过，requirements-completed 与 PLAN frontmatter 完全一致。

---
*Phase: 43-editable-pptx-renderer-and-pagination*
*Completed: 2026-07-14*
