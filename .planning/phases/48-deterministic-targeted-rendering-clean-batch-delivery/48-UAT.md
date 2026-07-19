---
status: complete
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
source: 48-01-SUMMARY.md, 48-02-SUMMARY.md, 48-03-SUMMARY.md, 48-04-SUMMARY.md, 48-05-SUMMARY.md, 48-06-SUMMARY.md, 48-07-SUMMARY.md, 48-08-SUMMARY.md, 48-09-SUMMARY.md
started: 2026-07-19T18:57:28Z
updated: 2026-07-19T20:10:05Z
---

## Current Test

[testing complete]

## Tests

### 1. 生成通用版三主题简历
expected: 使用已验证的简历资料执行公开 render 工作流后，预检会列出三个通用主题的正式命名版本；确认后，投递目录中每个版本都含同 stem 的 Markdown、Typst、PDF 三件套，且不含预览、日志或其他中间文件。
result: pass

### 2. 生成一份可追溯的定向简历
expected: 为一个已确认的单位和岗位执行 render 后，公开预检显示硬条件的满足、缺口、未知或不适用状态；成功投递的 Markdown 记录主题、页数、照片模式、目标单位/岗位及招聘信息来源和日期，且简历只使用已核实事实。
result: pass

### 3. 批量投递前的显式确认
expected: 执行 batch 时，系统先列出通用版和所有已确认目标的 added、updated、unchanged、removed 结果及 approval digest；只有将该 digest 原样提交确认后，才会一次性发布完整三件套或归档被移除目标的旧三件套。
result: pass

### 4. 失败不会破坏当前交付
expected: 当输入、照片、投递根或确认摘要无效时，命令以简短的非零 JSON 错误结束，不输出候选人正文、联系方式、绝对路径或 traceback；已有正式三件套与 history 保持不变。
result: pass

### 5. 重复运行与历史可审计性
expected: 对完全相同的资料重复发布不会修改现有文件，也不会新增 history；当已发布版本更新或移除时，history 只保存相应旧版本完整的 Markdown、Typst、PDF 三件套。
result: pass

## Summary

total: 5
passed: 5
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none yet]
