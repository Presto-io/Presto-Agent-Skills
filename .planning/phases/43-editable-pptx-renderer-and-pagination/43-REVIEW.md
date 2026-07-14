---
status: issues_found
phase: 43-editable-pptx-renderer-and-pagination
depth: standard
files_reviewed: 10
findings:
  critical: 2
  warning: 1
  info: 0
  total: 3
---

# Phase 43 代码审查

## Critical

### [C-01] literal code 修复只覆盖 `code` 布局，aggregate 会对其他合法代码块假绿

- 定位：`skills/school-pptx/scripts/pptx_emit.py:148`
- 相关：`skills/school-pptx/scripts/pptx_emit.py:193`、`skills/school-pptx/scripts/pptx_objects.py:105`、`skills/school-pptx/scripts/verify_pptx_renderer.py:735`
- 问题：专用 `add_literal_text()` 分支仅在 `physical.layout == "code"` 时使用。契约允许 `title-content` 和 `two-column` 包含有序 fenced-code block，这些 fragment 落入通用分支，经 `add_plain_lines()` -> `add_rich_text()` -> `inline_spans()` 重新解释 Markdown delimiter。公开 CLI 对合法 `title-content` 输入 `if a == b\nreturn **value**` 返回成功，但重开 PPTX 的正文变成 `if a == b\nreturn value`，静默删除星号并改变样式。
- 影响：C-02/D-03 声明的“任何代码路径逐字符保真”仍未成立，PPTX-03/PPTX-10 可发生静默内容损坏。`code-literal-roundtrip` 只构造 `layout="code"`，因此当前 17-gate aggregate 全绿也不能发现该回归。
- 建议：按 fragment kind 而非 physical layout 选择 literal emitter，或在契约验证层明确禁止专用 `code` 布局之外的 fenced code；新增 `title-content`、`two-column` 的 parser-plan-PPTX 逐字符重开向量，并让 gap gate 覆盖这些合法路径。

### [C-02] 合法的仅表头 Markdown 表格触发未捕获除零异常

- 定位：`skills/school-pptx/scripts/pptx_paginate.py:548`
- 相关：`skills/school-pptx/scripts/pptx_paginate.py:551`、`skills/school-pptx/scripts/pptx_render.py:390`
- 问题：Markdown parser 接受“表头 + 分隔行、零数据行”的标准表格且不产生诊断。此时 `data_heights` 为空，`ordered_contiguous_partition()` 返回空 ranges，随后 `loads=[]`，`sum(loads) / len(loads)` 直接抛出 `ZeroDivisionError`。顶层状态机未捕获该异常，公开命令输出完整 traceback。
- 影响：有效输入无法渲染，表头内容丢失，同时破坏 VER-03 的有界失败边界。canonical 表格均含数据行，因此 `pagination-structured`、`frozen-numbering-row-heights` 和 aggregate 均未覆盖此边界。
- 建议：要么把 header-only 表格规划为包含唯一 header row 的 native table fragment，要么在契约层以可定位诊断明确要求至少一条数据行；补充 public CLI、冻结 row-height vector 和重开 native table 回归。

## Warning

### [W-01] Pillow 的 `DecompressionBombError` 绕过对象错误映射并泄漏 traceback

- 定位：`skills/school-pptx/scripts/pptx_objects.py:162`
- 相关：`skills/school-pptx/scripts/pptx_emit.py:228`、`skills/school-pptx/scripts/verify_pptx_renderer.py:1422`
- 问题：`Image.open()` 会在读取超大尺寸图片头时先抛出 `PIL.Image.DecompressionBombError`，早于自定义 `width * height > MAX_MEDIA_PIXELS` 检查。该异常不是 `PptxObjectError`，不会被 emitter 映射，也不在 render 的通用捕获集合中。用 20000x10000 PNG 头即可让公开 CLI 输出包含仓库、缓存和临时目录绝对路径的 traceback。
- 影响：Pillow 会阻止实际解压炸弹，但 W-01 所要求的稳定、bounded、无内部路径公开错误仍可被绕过。现有 `object-error-bounded` 只覆盖自定义格式/像素错误，没有覆盖 Pillow 自身的 bomb exception。
- 建议：在 `_safe_image_size()` 边界捕获 Pillow 的识别、解压炸弹及解码异常并映射为稳定 `PptxObjectError`；增加低字节、高声明尺寸图片的黑盒 public gate。

## 验证记录

- 使用 skill-local 缓存依赖运行 `python3 skills/school-pptx/scripts/verify_pptx_renderer.py phase-43`：17 个顶层 gate 全部 PASS，确认上述 C-01/C-02/W-01 均属于现有 aggregate 未覆盖路径。
- 定向复现：合法 `title-content` fenced code 公开渲染成功但重开文本被改写；合法 header-only table 在 paginator 抛出 `ZeroDivisionError`；20000x10000 PNG 触发未捕获 `PIL.Image.DecompressionBombError`。
- 未修改任何生产源码，未提交。
