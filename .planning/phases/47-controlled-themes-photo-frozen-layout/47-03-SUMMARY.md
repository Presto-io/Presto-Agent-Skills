---
phase: 47-controlled-themes-photo-frozen-layout
plan: "03"
subsystem: graduate-resume layout verification
tags: [graduate-resume, typst, pdf, png, fixtures, privacy]
requires:
  - phase: 47-01
    provides: controlled fonts, themes, and safe local photo resolution
  - phase: 47-02
    provides: FrozenResumePlan and deterministic Typst emission
provides:
  - fixed three-theme layout fixture matrix
  - isolated Typst PDF/PNG evidence gate
  - canonical Phase 47 workflow and delivery boundaries
affects: [phase-48-rendering, phase-49-verification]
tech-stack:
  added: [PyMuPDF, Pillow]
  patterns: [literal-fixture-registry, disposable-render-evidence, PDF-page-plan-gate]
key-files:
  created:
    - skills/graduate-resume/scripts/graduate_resume_pdf_gate.py
    - skills/graduate-resume/scripts/test_layout_fixtures.py
    - skills/graduate-resume/fixtures/layout/short-no-photo.md
    - skills/graduate-resume/fixtures/layout/standard-photo.md
  modified:
    - skills/graduate-resume/scripts/graduate_resume_cli.py
    - skills/graduate-resume/scripts/graduate_resume_typst.py
    - skills/graduate-resume/SKILL.md
    - skills/graduate-resume/references/phase-46-baseline.md
key-decisions:
  - "布局回归使用字面固定 fixture/theme 注册表，禁止目录发现影响执行集合。"
  - "Typst 证据只在临时 workdir 生成，正式三件套和发布事务仍留给 Phase 48。"
  - "PDF 门禁以实际 PDF 文字和 PNG 边界与 FrozenResumePlan 对照，而非信任 Typst 源。"
requirements-completed: [THEME-01, THEME-02, THEME-03, THEME-04, THEME-05]
duration: 34min
completed: 2026-07-18
---

# Phase 47 Plan 03: 固定布局样张与受控渲染门禁总结

**三种受控主题现在由固定有照、无照、短内容、压力和失败关闭样张，以及隔离字体的 Typst/PDF/PNG 门禁共同锁定。**

## Performance

- **Duration:** 34 min
- **Started:** 2026-07-18T02:27:00Z
- **Completed:** 2026-07-18T03:00:59Z
- **Tasks:** 3
- **Files modified:** 12

## Accomplishments

- 新增五个固定 v2 layout fixture，覆盖无照片短内容、照片标准内容、临界内容、双页压力与不可满足条目；固定三主题注册表不依赖 glob。
- 为每个主题编译隔离字体的 Typst PDF/逐页 PNG，检查 `%PDF-`、A4 页数、计划页归属、文本事实、页面锚点和安全区像素。
- `verify` 先执行 Phase 46 schema fixture，再执行 Phase 47 布局矩阵；所有证据位于临时 workdir，不触及投递目录。
- canonical 文档明确三主题、35 mm x 49 mm 照片限制、contain/禁止拉伸、受控字体和 Phase 48/49 边界。

## Task Commits

1. **Task 1: 编写显式的主题、照片和页数 layout fixture 矩阵** - `11f1e64`, `34603c7`
2. **Task 2: 对样张执行受控 Typst 编译、逐页 PDF 语义与裁切门禁** - `6c5fcd2`
3. **Task 3: 更新 canonical 工作流说明并明确 Phase 47 证据边界** - `5018a33`

## Decisions Made

- 强制双页样张允许低利用率，但保留一页 recommendation、comparison 和 advisory。
- 本地照片解析拒绝中间 symlink、不可读对象和非普通文件，避免测试媒体越过 assets root。
- 无照片发射不会注入 `image()` 或逻辑媒体路径。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Security] 收紧照片路径的逐段 no-follow 检查**
- **Found during:** Task 1
- **Issue:** 原有解析只检查最终路径 symlink，无法在组成路径含 symlink 时明确失败。
- **Fix:** 对每一逻辑路径段执行 no-follow 检查，并拒绝不可读和非普通文件。
- **Files modified:** `skills/graduate-resume/scripts/graduate_resume_layout.py`
- **Verification:** 主题与布局回归全部通过。
- **Committed in:** `34603c7`

---

**Total deviations:** 1 auto-fixed (Rule 2 security)
**Impact on plan:** 加固既定媒体信任边界，未扩大交付范围。

## Known Stubs

无。测试照片是既有的非敏感单像素 fixture，仅用于 contain 策略和路径边界，不流入正式交付。

## Next Phase Readiness

Phase 48 可消费 `FrozenResumePlan`、Typst 发射器和受控证据边界来实现正式三件套及发布事务；Phase 49 仍负责跨 runtime 与跨环境验收。

## Self-Check: PASSED

- 已确认五个 layout fixture、PDF 门禁模块和 canonical 文档均存在。
- 已确认 `11f1e64`、`34603c7`、`6c5fcd2`、`5018a33` 均存在于 git 历史。
- `python3 -m unittest skills/graduate-resume/scripts/test_theme_contract.py skills/graduate-resume/scripts/test_layout_contract.py skills/graduate-resume/scripts/test_layout_fixtures.py -v` 通过 17 项。
- `skills/graduate-resume/scripts/graduate-resume.sh verify` 通过 schema 与固定 layout fixture 验证。
