---
phase: 47-controlled-themes-photo-frozen-layout
plan: "02"
subsystem: graduate-resume layout
tags: [graduate-resume, frozen-layout, pagination, typst, privacy]
requires:
  - phase: 47-01
    provides: ThemeSpec, controlled font manifest, safe photo resolution
provides:
  - Immutable 1/2-page FrozenResumePlan with measured container assignments
  - Atomic entry pagination and fail-closed layout diagnostics
  - Typst emitter limited to verified frozen plans
affects: [47-03, phase-48-rendering, phase-49-verification]
tech-stack:
  added: []
  patterns: [frozen-slotted-dataclass, measurement-hash, deidentified-projection, mechanical-typst-emission]
key-files:
  created:
    - skills/graduate-resume/scripts/graduate_resume_typst.py
    - skills/graduate-resume/scripts/test_layout_contract.py
    - skills/graduate-resume/templates/layout-measurement.json
  modified:
    - skills/graduate-resume/scripts/graduate_resume_layout.py
    - skills/graduate-resume/scripts/graduate_resume_cli.py
key-decisions:
  - "页数门槛只读取版本化测量配置并将其 SHA-256 冻结在计划中。"
  - "强制双页不以最低利用率拒绝；推荐和对照只影响 advisory。"
  - "公共 plan 投影只公开布局元数据和字段名，不公开候选人事实或照片路径。"
requirements-completed: [THEME-03, THEME-04, THEME-05]
duration: 28min
completed: 2026-07-18
---

# Phase 47 Plan 02: 冻结布局计划、原子分页与 Typst 边界总结

**受控主题资料现在先收敛为带测量哈希、页锚点和条目归属的不可变 1/2 页计划，再由安全 Typst 发射器机械消费。**

## Performance

- **Duration:** 28 min
- **Started:** 2026-07-18T02:11:00Z
- **Completed:** 2026-07-18T02:39:28Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- 新增版本化布局测量配置、`ContainerPlan`、`EntryBudget`、`PagePlan`、`PageRecommendation` 与完整 `FrozenResumePlan`，自动和强制模式均明确记录推荐、对照和 advisory。
- 按完整事实条目分页，固定个人信息首页首位、教育前置，并对超出任一可读页预算的不可拆条目返回 `LAYOUT_UNSATISFIABLE`。
- 新增只接收已验证计划的 Typst 发射器，统一转义候选人文本、固定 `pagebreak()` 序列，且 no-photo 文本不携带图片、路径或 EXIF。
- `plan` 现在在资料、字体和照片门禁后输出脱敏冻结布局摘要；`render`、`batch` 继续返回 `NOT_IMPLEMENTED`。

## Task Commits

1. **Task 1: 不可变计划投影与三段式页数决议** - `bb0188b`, `c2bf170`
2. **Task 2: 只消费冻结计划的 Typst 发射器** - `a6d3835`, `97ce2d0`
3. **Task 3: CLI 冻结计划摘要** - `54303bd`, `46c02e4`, `80610a5`

## Files Created/Modified

- `skills/graduate-resume/templates/layout-measurement.json` - 三主题唯一的版本化页数阈值来源。
- `skills/graduate-resume/scripts/graduate_resume_layout.py` - 不可变布局计划、事实容器投影、分页与失败关闭。
- `skills/graduate-resume/scripts/graduate_resume_typst.py` - 已验证冻结计划的安全 Typst 文本发射。
- `skills/graduate-resume/scripts/graduate_resume_cli.py` - `plan` 的脱敏冻结计划 JSON。
- `skills/graduate-resume/scripts/test_layout_contract.py` - 页数、锚点、原子性、安全发射与 CLI 合同测试。

## Decisions Made

- 利用率固定使用 `(used_height_mm + epsilon_mm) / usable_height_mm`；所有阈值与 epsilon 均来自哈希绑定的配置。
- `two_page_min_page_utilization` 只服务自动模式的明显双页判断，强制双页仍可生成低利用率的精确两页计划。
- 发射器要求 `__verified__` 标记和计划的交叉验证，不能从普通事实映射直接生成 Typst。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - 信息披露] 收紧公共容器投影**
- **Found during:** Task 3
- **Issue:** 初始容器 JSON 投影会带出字段值，违反 plan JSON 的脱敏边界。
- **Fix:** 投影只保留字段名、事实 ID、布局高度和页面归属。
- **Files modified:** `skills/graduate-resume/scripts/graduate_resume_layout.py`
- **Verification:** CLI 回归断言输出不包含候选人姓名或 fixture 媒体路径。
- **Committed in:** `46c02e4`

---

**Total deviations:** 1 auto-fixed（Rule 2 信息披露）。
**Impact on plan:** 加固既定信任边界，没有扩展交付范围。

## Issues Encountered

无。TDD 红灯阶段确认了缺失的冻结错误码与 Typst 模块，随后由实现提交闭环。

## User Setup Required

无外部服务配置要求。

## Next Phase Readiness

- 47-03 可使用冻结计划检查一页、两页、照片与内容压力样张。
- Phase 48 可消费 `FrozenResumePlan` 与 `emit_typst()`，但正式三件套发布仍保持在其范围内。

## Self-Check: PASSED

- 已确认全部六个计划文件存在，且 `bb0188b`、`c2bf170`、`a6d3835`、`97ce2d0`、`54303bd`、`46c02e4`、`80610a5` 均可在 git 历史中找到。
- `python3 -m unittest skills/graduate-resume/scripts/test_layout_contract.py skills/graduate-resume/scripts/test_theme_contract.py -v` 通过 13 项测试。
