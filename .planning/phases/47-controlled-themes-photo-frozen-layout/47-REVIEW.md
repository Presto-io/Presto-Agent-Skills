---
phase: 47-controlled-themes-photo-frozen-layout
reviewed: 2026-07-19T04:22:58Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - skills/graduate-resume/SKILL.md
  - skills/graduate-resume/fixtures/layout/media/student-photo.jpg
  - skills/graduate-resume/fixtures/layout/short-no-photo.md
  - skills/graduate-resume/fixtures/layout/standard-photo.md
  - skills/graduate-resume/fonts/manifest.json
  - skills/graduate-resume/references/phase-46-baseline.md
  - skills/graduate-resume/scripts/graduate_resume_cli.py
  - skills/graduate-resume/scripts/graduate_resume_layout.py
  - skills/graduate-resume/scripts/graduate_resume_pdf_gate.py
  - skills/graduate-resume/scripts/graduate_resume_typst.py
  - skills/graduate-resume/scripts/test_layout_contract.py
  - skills/graduate-resume/scripts/test_layout_fixtures.py
  - skills/graduate-resume/scripts/test_theme_contract.py
  - skills/graduate-resume/templates/layout-measurement.json
  - skills/graduate-resume/templates/resume-themes.typ
findings:
  critical: 1
  warning: 2
  info: 0
  total: 3
status: findings_found
---

# Phase 47: Code Review Report

**Reviewed:** 2026-07-19T04:22:58Z
**Depth:** standard
**Files Reviewed:** 15
**Status:** findings_found

## Summary

审查覆盖第 47 阶段的主题、照片、冻结分页、Typst 发射、PDF 门禁和固定 fixture 回归路径。阶段测试与 skill-local `verify` 可以通过，但冻结计划的完整性校验没有保证“每个已验证容器恰好一次地进入页面”，导致下游发射器可在通过自身校验后静默删除简历事实。这违反本阶段“不得隐藏/删除事实凑版”的核心约束。

## Critical Issues

### CR-01: 冻结计划可在校验后静默遗漏或重复已验证事实

**Classification:** BLOCKER

**File:** `skills/graduate-resume/scripts/graduate_resume_layout.py:213`

**Issue:** `FrozenResumePlan.validate()` 只检查页面引用的容器 ID 是否存在，未检查所有 `self.containers` 是否被页面集合完整、唯一地覆盖，也未将 `ContainerPlan.page_number` 与实际页面绑定。`emit_typst()` 仅遍历 `page.containers`（`graduate_resume_typst.py:93-106`），因此一个被篡改或跨模块构造的计划可以通过 `validate()` 后直接遗漏事实，或者重复某一事实。已复现：从 `standard-photo.md` 构造双页计划后，将第一页容器改为仅 `profile`；`validate()` 成功，`emit_typst()` 仅发射 2 个容器，原计划的 4 个容器中 `edu-standard-001` 与 `skill-standard-001` 被静默丢弃。

**Fix:** 在 `FrozenResumePlan.validate()` 中建立按页展平的容器 ID 序列，并要求它与 `self.containers` 的 ID 序列一一对应、无重复；同时校验每个容器的 `page_number == page.number`。例如：

```python
planned_ids = tuple(container.id for page in self.pages for container in page.containers)
container_ids = tuple(container.id for container in self.containers)
if planned_ids != container_ids or len(planned_ids) != len(set(planned_ids)):
    raise CliError(LAYOUT_PLAN_INVALID, "冻结计划必须完整且唯一地分配每条事实。")
if any(
    containers[container_id].page_number != page.number
    for page in self.pages for container_id in page.containers
):
    raise CliError(LAYOUT_PLAN_INVALID, "容器页面归属与冻结计划不一致。")
```

新增回归：删除容器、重复容器、交换页面及伪造 `page_number` 均必须在 `emit_typst()` 前失败。

## Warnings

### WR-01: `photo_mode` 参数被忽略，可生成与请求相反的照片计划

**Classification:** WARNING

**File:** `skills/graduate-resume/scripts/graduate_resume_layout.py:362`

**Issue:** `build_frozen_resume_plan()` 接收 `photo_mode`，但没有校验或使用它；实际模式完全由 `photo is not None` 决定（第 396 行）。调用 `build_frozen_resume_plan(..., photo_mode="no-photo", photo=PhotoAsset(...))` 会成功生成 `photo_mode="photo"` 的计划。当前 CLI 恰好先通过 resolver 把 no-photo 转成 `None`，但这是跨模块公开布局接口，调用者一旦复用它就能绕过无照片语义。

**Fix:** 在函数入口要求 `photo_mode in {"photo", "no-photo"}` 且与 `photo` 严格一致，任何不一致返回 `LAYOUT_PLAN_INVALID`；随后从已校验的参数写入计划，而不是重新从对象真值推断。增加两种不匹配组合的回归测试。

### WR-02: 同一事实的首字段被拼入后续每行，违反无重复字段的展示契约

**Classification:** WARNING

**File:** `skills/graduate-resume/scripts/graduate_resume_layout.py:294`

**Issue:** `_display_fields()` 对所有非 `candidate` 容器把首字段文本作为 `context` 拼到每个后续字段。例如教育经历会输出“学校：甲校”“学校：甲校 · 专业：乙”“学校：甲校 · 学历：丙”。这会重复学校、项目标题或证书名称，既增加可见内容和估算高度，也直接违背阶段 D-05 的“不得重复学校、技能方向或证书名称”。现有测试只检查 PDF 包含期望文本，不检查重复字段。

**Fix:** 保持字段结构独立，由 Typst 模板按标题/元信息/概述/成果的语义接口排版；最低限度应删除第 294-296 行的 context 前缀重写，仅保留各字段自己的标签和值。补充教育、技能、证书、项目、实训和经历的发射快照断言，确保每个已验证值只出现一次。

## Scope And Test Gaps

- 已读取全部 `47-*-PLAN.md`、`47-*-SUMMARY.md`、`.planning/REQUIREMENTS.md` 与用户列出的审查范围，并以当前实现而非总结描述判定。
- 未发现受审 JPEG fixture 含 EXIF/GPS；字体、照片路径和 Typst 字符转义路径已作静态检查。
- 已运行 `python3 -m unittest skills/graduate-resume/scripts/test_theme_contract.py skills/graduate-resume/scripts/test_layout_contract.py skills/graduate-resume/scripts/test_layout_fixtures.py -v` 和 `skills/graduate-resume/scripts/graduate-resume.sh verify`，均通过。
- 现有回归未覆盖 CR-01 的容器覆盖/唯一性，也未覆盖 WR-01 的参数一致性与 WR-02 的单次事实展示；因此通过的固定 fixture 矩阵不能证明所有冻结计划都保留全部事实。

---

_Reviewed: 2026-07-19T04:22:58Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
