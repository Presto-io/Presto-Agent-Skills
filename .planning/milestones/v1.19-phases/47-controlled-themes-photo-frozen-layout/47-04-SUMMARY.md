---
phase: 47-controlled-themes-photo-frozen-layout
plan: "04"
subsystem: graduate-resume layout verification
tags: [graduate-resume, typst, pdf, png, cli, layout]
requires:
  - phase: 47-03
    provides: fixed fixtures and the initial PDF/PNG evidence gate
provides:
  - production theme-layout invocation for all three controlled themes
  - stable shell JSON normalization for layout failures
  - complete boundary and pressure PDF/PNG fixture coverage
affects: [phase-48-rendering, phase-49-verification]
tech-stack:
  added: []
  patterns: [frozen-theme-realization, stable-cli-error-boundary, all-fixture-render-gate]
key-files:
  created:
    - .planning/phases/47-controlled-themes-photo-frozen-layout/47-04-SUMMARY.md
  modified:
    - skills/graduate-resume/scripts/graduate_resume_typst.py
    - skills/graduate-resume/scripts/graduate_resume_cli.py
    - skills/graduate-resume/templates/resume-themes.typ
    - skills/graduate-resume/scripts/test_layout_contract.py
    - skills/graduate-resume/scripts/test_layout_fixtures.py
    - skills/graduate-resume/SKILL.md
key-decisions:
  - "Typst 发射器只将冻结的主题、首页面照片和分页容器交给 theme-layout，不重新选择布局。"
  - "公开 CLI 在入口处按稳定 code/message 结构归一化跨模块加载的布局错误。"
requirements-completed: [THEME-01, THEME-02, THEME-03, THEME-04, THEME-05]
duration: 17min
completed: 2026-07-18
---

# Phase 47 Plan 04: 验证缺口闭环总结

**三主题的冻结 Typst 布局、稳定失败 JSON 和完整临界/压力 PDF/PNG 逐页门禁已闭环。**

## Accomplishments

- `emit_typst()` 对每个冻结页面调用 `theme-layout`，并只在首页传入已验证的照片；conservative、modern、expressive 都有实际不同的 Typst 布局。
- shell CLI 将布局模块在 `__main__` 边界泄漏的稳定错误规范为 JSON；强制两页不可满足时返回 `LAYOUT_UNSATISFIABLE` 且不输出 traceback。
- 临界与压力 fixture 现在对每个主题实际编译 Typst、PDF 和逐页 PNG，门禁验证精确 1/2 页、无第三页、第二页模块锚点以及冻结条目事实归属。

## Verification

- `python3 -m unittest skills/graduate-resume/scripts/test_theme_contract.py skills/graduate-resume/scripts/test_layout_contract.py skills/graduate-resume/scripts/test_layout_fixtures.py -v`：19 项通过。
- `skills/graduate-resume/scripts/graduate-resume.sh verify`：通过；固定 5 个 layout fixture 均被记录，压力和临界样张使用真实受控 PDF/PNG 门禁。
- `graduate-resume.sh plan ...error-unsatisfiable-two-pages.md --pages 2`：非零退出并输出 JSON `LAYOUT_UNSATISFIABLE`。

## Decisions Made

- 列表条目的模块标题只在每个冻结页面的模块首条渲染，既保留第二页锚点，也不拆分原子条目。
- `list-entry` 的新标题开关是可选命名参数，保持既有三参数 Typst 模板调用兼容。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] 修复 Typst `body` content 参数调用与既有宏签名的兼容性**
- **Found during:** PDF/PNG 全矩阵编译。
- **Fix:** 使用 Typst trailing content 调用形式，并把列表标题开关设计为可选命名参数。
- **Verification:** 受控 Typst 编译、19 项回归与 skill-local `verify` 全部通过。

## Self-Check: PASSED

- 本总结列出的六个生产、测试和 canonical 文档文件均存在。
- 本次提交没有包含用户未提交的 `47-01-PLAN.md`、`47-UI-SPEC.md` 或 `47-VERIFICATION.md`。
