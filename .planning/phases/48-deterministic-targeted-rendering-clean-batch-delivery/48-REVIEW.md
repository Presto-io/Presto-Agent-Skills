---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
reviewed: 2026-07-19T18:38:52Z
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
  warning: 1
  info: 0
  total: 1
status: issues_found
---

# Phase 48: Code Review Report

**Reviewed:** 2026-07-19T18:38:52Z
**Depth:** standard
**Files Reviewed:** 20
**Status:** issues_found

## Summary

审查覆盖定向投影、最终 Markdown/Typst/PDF 渲染、candidate-first 投递、隐藏证据和事务回滚。阶段定向回归通过，但最终 Markdown 的重读验证未完整执行其公开元数据契约。已接受的同 UID Typst 可执行文件替换竞态（AR-48-07）未重新报告。

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
