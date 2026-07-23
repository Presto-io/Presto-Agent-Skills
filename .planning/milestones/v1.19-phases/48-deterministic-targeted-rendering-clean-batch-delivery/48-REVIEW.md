---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
reviewed: 2026-07-20T03:03:00Z
depth: standard
files_reviewed: 20
files_reviewed_list:
  - skills/graduate-resume/SKILL.md
  - skills/graduate-resume/fixtures/render/targeted-photo.md
  - skills/graduate-resume/fixtures/targeting/multi-state-targets.md
  - skills/graduate-resume/references/targeted-render-delivery-contract.md
  - skills/graduate-resume/scripts/graduate_resume_cli.py
  - skills/graduate-resume/scripts/graduate_resume_delivery.py
  - skills/graduate-resume/scripts/graduate_resume_final_markdown.py
  - skills/graduate-resume/scripts/graduate_resume_layout.py
  - skills/graduate-resume/scripts/graduate_resume_render.py
  - skills/graduate-resume/scripts/graduate_resume_targeting.py
  - skills/graduate-resume/scripts/graduate_resume_typst.py
  - skills/graduate-resume/scripts/test_delivery_transaction.py
  - skills/graduate-resume/scripts/test_phase48_cli.py
  - skills/graduate-resume/scripts/test_render_contract.py
  - skills/graduate-resume/scripts/test_targeting_contract.py
  - skills/graduate-resume/scripts/test_theme_contract.py
  - skills/graduate-resume/templates/graduate-resume.md
  - skills/graduate-resume/templates/resume-themes.typ
  - skills/graduate-resume/templates/targeting-policy.json
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Phase 48: Code Review Report

**Reviewed:** 2026-07-20T03:03:00Z
**Depth:** standard
**Files Reviewed:** 20
**Status:** clean

## Summary

审查覆盖定向投影、最终 Markdown/Typst/PDF 渲染、candidate-first 投递、隐藏证据和事务回滚。WR-01 已由 `eb61707` 修复，并由 `60f677c` 的修复报告和 20 项回归复核；用户于 2026-07-20 确认 Phase 48 通过。已接受的同 UID Typst 可执行文件替换竞态继续由 `AR-48-07` 记录。

## Closure

- WR-01：已修复。`load_final_resume()` 现复用 target 元数据完整性和 URL 拒绝校验；重算 binding 后的 URL、空字段和 ID 不匹配篡改回归均通过。
- 修复证据：`48-REVIEW-FIX.md` 为 `status: all_fixed`，关联提交 `eb61707` 和 `60f677c`。
- 当前复核源码 SHA-256：
  - `skills/graduate-resume/scripts/graduate_resume_final_markdown.py`: `8cd9558f939fe26e8d31ee8074fae04b3db4eb7b3e222ea0edf5851fa18cba5e`
  - `skills/graduate-resume/scripts/test_render_contract.py`: `9325a7d94cd74fd45c0889f5de2c5399ea26230765fdf485f9eca5deaba293cf`
  - `skills/graduate-resume/scripts/graduate_resume_cli.py`: `a047c7845c01bdcf9dc384fe7cbe70e970f80b0a867afe9f089c498de88483a2`
  - `skills/graduate-resume/scripts/graduate_resume_delivery.py`: `7f95c135c68f2fd6760b0b44e7c3829b549e04292580655f90a8ba15e48d710a`
  - `skills/graduate-resume/scripts/graduate_resume_render.py`: `49060f2d50471d0f2239f79357046da4583ec35550dacbf74a25e595f50f77a3`

## Narrative Findings (AI reviewer)

## Warnings

### WR-01: 重读最终 Markdown 时未复验 target 元数据语义

**Classification:** WARNING

**File:** `skills/graduate-resume/scripts/graduate_resume_final_markdown.py:217`

**Issue:** `load_final_resume()` 对 `version.kind == "target"` 只检查 `target` 的键集合，未检查 `id/company/role/source/as_of` 均为非空字符串，也未重用 emitter 在第 145 行执行的 URL 拒绝规则。绑定摘要不是签名；任何可写 candidate 的进程都能在改写 frontmatter 后重算 `binding_sha256`。可复现地将一个已生成的定向 Markdown 的 `target.source` 改为 `https://private.example.test/job`、重算 binding 后，`load_final_resume()` 成功返回该 URL，违反 D-12/最终 Markdown 不包含原始招聘 URL 的契约，也使“reopen → safe parse → validate binding”无法作为完整语义检查点。

**Fix:** 在第 219 行的 target 分支中校验所有字段的类型、非空性、`target.id == version.id`，并拒绝匹配 `_SOURCE_URL_RE` 的 `source`；同时添加篡改后重算 binding 仍必须被拒绝的回归测试。例如：

```python
if version["kind"] == "target":
    if not isinstance(target, dict) or set(target) != {"id", "company", "role", "source", "as_of"}:
        raise ValueError
    if any(not isinstance(target[key], str) or not target[key].strip() for key in target):
        raise ValueError
    if target["id"] != version["id"] or _SOURCE_URL_RE.match(target["source"].strip()):
        raise ValueError
```

---

_Reviewed: 2026-07-19T18:38:52Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
