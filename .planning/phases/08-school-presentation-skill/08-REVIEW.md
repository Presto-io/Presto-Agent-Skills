---
phase: 08-school-presentation-skill
reviewed: 2026-05-31T16:02:58Z
depth: standard
files_reviewed: 1
files_reviewed_list:
  - skills/school-presentation/scripts/school-presentation.sh
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Phase 08: Code Review Report

**Reviewed:** 2026-05-31T16:02:58Z
**Depth:** standard
**Files Reviewed:** 1
**Status:** clean

## Summary

本次只重新审查 `skills/school-presentation/scripts/school-presentation.sh`，未读取或分析 `references/identity/images/*` 二进制内容。结论是前次指出的两个问题都已解决：媒体路径已收窄到允许范围，尺寸门禁也已改为优先读取 frontmatter 并记录来源。

All reviewed files meet quality standards. No issues found.

## Resolved Findings

### CR-01 resolved: 媒体路径不再可读取任意本地文件

**File:** `skills/school-presentation/scripts/school-presentation.sh:72`

**Resolved:** `resolve_asset()` 现在拒绝绝对路径和 `..`，删除了 `Path.cwd()` 兜底，并且只允许输入 Markdown 同目录下的 `media/` 与 `references/identity/images/` 下的 image/video MIME。该问题已关闭。

### WR-01 resolved: frontmatter 的 `max_output_mb` 现在参与门禁

**File:** `skills/school-presentation/scripts/school-presentation.sh:462`

**Resolved:** `--max-size-mb` 的默认值已改为 `None`，未显式传入 CLI 参数时会读取 frontmatter 的 `max_output_mb`，并在 manifest 中写入 `max_size_source`。这修复了 Markdown schema 与实际渲染行为不一致的问题。


---

_Reviewed: 2026-05-31T16:02:58Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
