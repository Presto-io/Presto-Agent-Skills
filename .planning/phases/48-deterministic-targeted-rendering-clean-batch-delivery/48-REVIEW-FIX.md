---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
fixed_at: 2026-07-18T19:32:07Z
review_path: .planning/phases/48-deterministic-targeted-rendering-clean-batch-delivery/48-REVIEW.md
iteration: 2
findings_in_scope: 4
fixed: 3
skipped: 1
status: partial
---

# Phase 48: Code Review Fix Report

**Fixed at:** 2026-07-18T19:32:07Z
**Source review:** `.planning/phases/48-deterministic-targeted-rendering-clean-batch-delivery/48-REVIEW.md`
**Iteration:** 2

**Summary:**
- Findings in scope: 4
- Fixed: 3
- Skipped: 1

## Fixed Issues

### CR-01: 裸域名招聘 URL 仍可写入正式 Markdown

**Files modified:** `skills/graduate-resume/scripts/graduate_resume_cli.py`, `skills/graduate-resume/scripts/graduate_resume_final_markdown.py`, `skills/graduate-resume/scripts/test_phase48_cli.py`
**Commit:** `91a63f4`
**Applied fix:** 将来源校验收紧为 scheme、`www.`、裸域名及路径/查询串均拒绝；最终 Markdown 投影再次断言该边界。

### CR-02: stem 敏感信息检测仍遗漏座机和旧版身份证号

**Files modified:** `skills/graduate-resume/scripts/graduate_resume_render.py`, `skills/graduate-resume/scripts/test_render_contract.py`
**Commit:** `91a63f4`
**Applied fix:** 文件名组件现在拒绝中国座机、带 `+` 的国际号码、15 位与 18 位身份证，并保留已有移动电话、邮箱和 URL 检测。

### CR-03: 证据持久化失败发生在 delivery 提交之后，无法回滚正式产物

**Files modified:** `skills/graduate-resume/scripts/graduate_resume_cli.py`, `skills/graduate-resume/scripts/graduate_resume_delivery.py`, `skills/graduate-resume/scripts/graduate_resume_render.py`, `skills/graduate-resume/scripts/test_phase48_cli.py`
**Commit:** `91a63f4`
**Applied fix:** 证据批量写入移入 `DeliverySession.publish()` 的事务边界；第二次写入失败时会清除本批新证据并回滚 current/history。回归测试覆盖第二个 target 失败后 delivery、history 和 evidence 均恢复原快照。

## Skipped Issues

### CR-04: Typst 快照仍存在校验到执行之间的可替换竞态

**File:** `skills/graduate-resume/scripts/graduate_resume_typst_runtime.py:123`
**Reason:** 当前 Darwin 25.5.0 / Python 3.14.6 不提供 `os.fexecve`，系统 libc 也不导出 `fexecve`；实测以 `pass_fds` 执行 `/dev/fd/<fd>` 返回 `EACCES`。在同 UID 攻击模型下，保留路径执行、用户可撤销的权限位或 `/dev/fd` 路径替代均无法消除 check-to-exec 替换窗口，故未降级安全边界。
**Original issue:** 快照在校验后仍按路径交给 `subprocess.run()`，可在 exec 前被同 UID 攻击者原地覆写。

安全替代方案：在提供真实 `fexecve`/等价内核 descriptor-exec 的受支持平台运行，或引入经系统安装、非当前用户可写的受控原生 helper，由该 helper 在不可篡改的权限域内完成校验与 descriptor exec；在具备其中一种能力前，不应声称此项已修复。

---

_Fixed: 2026-07-18T19:32:07Z_
_Fixer: gsd-code-fixer_
_Iteration: 2_
