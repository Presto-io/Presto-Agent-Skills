---
phase: 47-controlled-themes-photo-frozen-layout
plan: "05"
subsystem: graduate-resume frozen layout verification
tags: [graduate-resume, frozen-layout, typst, pdf, png, regression]
requires:
  - phase: 47-01
    provides: controlled themes and photo safety policy
  - phase: 47-02
    provides: FrozenResumePlan and mechanical Typst emission
  - phase: 47-03
    provides: disposable PDF/PNG evidence gate
provides:
  - complete one-to-one frozen page/container topology validation
  - fail-closed photo mode consistency at the public layout boundary
  - real PDF/PNG adversarial topology regression across all themes
affects: [phase-48-rendering, phase-49-verification]
tech-stack:
  added: []
  patterns: [ordered-topology-invariant, verified-photo-mode, real-evidence-adversarial-test]
key-files:
  modified:
    - skills/graduate-resume/scripts/graduate_resume_layout.py
    - skills/graduate-resume/scripts/graduate_resume_pdf_gate.py
    - skills/graduate-resume/scripts/test_layout_contract.py
    - skills/graduate-resume/scripts/test_layout_fixtures.py
key-decisions:
  - "页面容器序列必须与冻结容器序列完全一致、无重复，且每个容器页码必须与所在 PagePlan 相同。"
  - "photo_mode 只能为 photo/no-photo，且必须与照片资源和槽位同时一致。"
  - "PDF 门禁仅忽略另一冻结页面也明确期望的同一可见字段值；未获该页计划授权的跨页文本仍失败。"
requirements-completed: [THEME-04, THEME-05]
completed: 2026-07-19
---

# Phase 47 Plan 05: 冻结布局完整性与 D-05 闭环总结

冻结布局现在将容器集合、顺序和页码归属作为同一不可变契约验证。删容器、重复容器、跨页移动和伪造容器页码都会在 Typst 发射和 PDF/PNG 门禁读取页面文本前以 `LAYOUT_PLAN_INVALID` 失败。

## Accomplishments

- `FrozenResumePlan.validate()` 验证页面扁平容器序列与 `containers` 完全一致，并同时拒绝任一侧重复和页码不一致。
- `build_frozen_resume_plan()` 及冻结计划验证共同收紧 `photo_mode`：只允许 `photo`/`no-photo`，并强制与照片对象、照片槽位一致。
- 移除非候选人字段的首字段上下文前缀；教育、技能、证书、项目、实训和经历字段各自保留独立标签和值。
- 三主题压力样张实际生成临时 Typst/PDF/PNG；同一份正常真实证据对四类篡改计划仍在 PDF 门禁前失败。D-05 逐字段计数使用测试内唯一化的已验证角色值，避免将源样张中两个合法相同的“角色：组员”混同。

## Verification

- `python3 -m unittest skills/graduate-resume/scripts/test_layout_contract.py -v`：8 项通过。
- `python3 -m unittest skills/graduate-resume/scripts/test_theme_contract.py skills/graduate-resume/scripts/test_layout_contract.py skills/graduate-resume/scripts/test_layout_fixtures.py -v`：22 项通过。
- `skills/graduate-resume/scripts/graduate-resume.sh verify`：通过；固定 layout fixture 三主题真实 PDF/PNG 矩阵保持在临时目录。
- `git diff --check -- skills/graduate-resume/scripts/graduate_resume_layout.py skills/graduate-resume/scripts/graduate_resume_pdf_gate.py skills/graduate-resume/scripts/test_layout_contract.py skills/graduate-resume/scripts/test_layout_fixtures.py`：通过。

## Task Commit

1. **冻结页面拓扑、照片模式与真实证据对抗回归** - `f74d487`

## Deviations From Plan

### 自动修正

**1. [Rule 1 - 回归修复] 让 PDF 门禁识别跨页合法同值字段**

- **发现于：** Task 2 的压力样张真实 PDF/PNG 回归。
- **问题：** 移除 D-05 首字段前缀后，源压力样张的两个项目均合法显示“角色：组员”；旧门禁会把另一页已被其自身冻结容器期望的同值误报为错页文本。
- **处理：** 门禁只在另一页冻结计划不包含该同一可见值时拒绝跨页文本。容器 ID、全量唯一页面归属、页码、PDF 页数和所有非授权文本检查均未放宽。
- **影响：** 这是让既有固定样张在 D-05 独立字段展示后继续真实验证的最小必要修复；未触及 Phase 48/49、canonical schema、target/delivery 或照片 resolver。
- **提交：** `f74d487`

## Self-Check: PASSED

- 未修改用户已有的 `47-VERIFICATION.md` 或未跟踪的 `47-REVIEW.md`。
- 未修改 47-01 至 47-04 的总结、主题模板、canonical schema、target/delivery 或正式交付路径。
