---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
fixed_at: 2026-07-18T19:08:21Z
review_path: .planning/phases/48-deterministic-targeted-rendering-clean-batch-delivery/48-REVIEW.md
iteration: 1
findings_in_scope: 10
fixed: 10
skipped: 0
status: all_fixed
---

# Phase 48: Code Review Fix Report

**Fixed at:** 2026-07-18T19:08:21Z
**Source review:** `.planning/phases/48-deterministic-targeted-rendering-clean-batch-delivery/48-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 10
- Fixed: 10
- Skipped: 0

## Fixed Issues

### CR-01: 招聘来源 URL 被公开到预检与正式 Markdown

**Files modified:** `graduate_resume_cli.py`, `test_phase48_cli.py`
**Commit:** `5a880a1`
**Applied fix:** canonical 校验拒绝 URL 来源描述，并覆盖 CLI 负例。

### CR-02: 安全 stem 未检测电话、邮箱或身份证信息

**Files modified:** `graduate_resume_render.py`, `test_render_contract.py`
**Commit:** `f26100d`
**Applied fix:** stem 组件拒绝敏感标识，并以 UTF-8 字节预算截断 CJK 组件。

### CR-03: 重复 Markdown 字段静默覆盖已解析事实

**Files modified:** `graduate_resume_cli.py`, `test_phase48_cli.py`
**Commit:** `5a880a1`
**Applied fix:** 同一条目重复规范字段改为稳定 `MARKDOWN_INVALID` 失败。

### CR-04: `validate` 接受渲染器必然拒绝的嵌套值

**Files modified:** `graduate_resume_cli.py`, `test_phase48_cli.py`
**Commit:** `5a880a1`
**Applied fix:** 对 contact、可选列表和条目字段统一验证安全字符串类型。

### CR-05: 未确认预检会覆盖既有隐藏证据记录

**Files modified:** `graduate_resume_render.py`, `graduate_resume_cli.py`, `test_render_contract.py`, `test_phase48_cli.py`, `targeted-render-delivery-contract.md`
**Commit:** `1e17ee6`, `6b2462b`
**Applied fix:** 证据文件绑定 canonical/projection/condition 摘要且冲突 fail-closed；预检不写证据，确认发布后才持久化。

### CR-06: Typst 快照只校验 inode，版本门禁后仍可被原地篡改执行

**Files modified:** `graduate_resume_typst_runtime.py`, `test_render_contract.py`
**Commit:** `cc27cb1`
**Applied fix:** 每次执行前复验快照类型、身份、权限、大小和 SHA-256，并覆盖同 inode 原地覆写。

### WR-01: CJK 长度按字符截断却按字节拒绝

**Files modified:** `graduate_resume_render.py`, `test_render_contract.py`
**Commit:** `f26100d`
**Applied fix:** 组件截断改为 UTF-8 字节预算。

### WR-02: 定向照片 fixture 引用了不存在的资产

**Files modified:** `fixtures/render/media/source-photo.jpg`, `test_phase48_cli.py`
**Commit:** `19de15e`
**Applied fix:** 提供受控照片副本并执行真实定向照片渲染。

### WR-03: 主题测试在源码模板目录使用固定探针文件

**Files modified:** `test_theme_contract.py`
**Commit:** `f135174`
**Applied fix:** 探针与 PDF 均移动到 `TemporaryDirectory()`，模板副本在临时目录内编译。

### WR-04: 已确认 target 可绕过结构化招聘要求进入发布

**Files modified:** `graduate_resume_cli.py`, `test_phase48_cli.py`, `fixtures/*.md`
**Commit:** `5a880a1`
**Applied fix:** confirmed target 的 `requirements` 现在必须为非空安全字符串列表。

---

_Fixed: 2026-07-18T19:08:21Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_
