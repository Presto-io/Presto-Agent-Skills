---
status: issues_found
phase: 43-editable-pptx-renderer-and-pagination
depth: standard
files_reviewed: 9
findings:
  critical: 1
  warning: 2
  info: 0
  total: 3
---

# Phase 43 代码审查

## Critical

### [C-01] mixed-fragment code 的冻结字号与实际发射字号不一致，可在成功成品中静默裁切代码

- 定位：`skills/school-pptx/scripts/pptx_emit.py:209`
- 相关：`skills/school-pptx/scripts/pptx_paginate.py:206`、`skills/school-pptx/scripts/pptx_paginate.py:274`、`skills/school-pptx/scripts/pptx_paginate.py:708`、`skills/school-pptx/scripts/verify_pptx_renderer.py:855`
- 问题：paginator 对正文和 fenced code 一律使用 slot 的 `font_size_min` 计算高度与 code display lines；除 table 外，`PhysicalSlide.selected_font_sizes` 保持为空。43-09 的通用 emitter 却在没有冻结字号时回退到 `budget["font_size_max"]`，并把这个最大字号同时用于普通段落和 code run。因而 plan 认为能放入一页的 code，在成品中可能以更大字号产生更多软换行并超过同一冻结 geometry。
- 复现：临时 `title-content` 向量包含 4 行、每行 40 个中文字符。冻结计划只生成 1 个物理页，按 16pt 估算为 4 个 display lines；重开成品的 code run 实际为 24pt，按同一测量器为 8 个 display lines、236.4pt 高，而 body slot 仅 118.12pt。公开 render 仍退出 0，文本虽留在 OOXML 中，但放映时会被 text frame 裁切。
- 影响：破坏 D-03/PPTX-08 的“soft wrap 计入分页”以及冻结 plan -> emitter 机械一致性；R43-C01 的逐字符回读门只检查 OOXML 文本、字体名和 shape 数，不检查实际字号或槽高度，因此完整 aggregate 当前仍会假绿。
- 建议：在 paginator 中为每个正文 target slot 冻结实际采用的字号，并让 emitter 只消费该值；或让 paginator 与 emitter 明确统一使用同一个 manifest 字号。为 mixed `title-content`/`two-column` 增加接近槽容量的多行 code 向量，断言冻结字号等于重开 run 字号、发射后的 display height 不超过 slot，必要时产生额外物理页而不是裁切。

## Warning

### [W-01] aggregate 的 gap outcome 是硬编码声明，未由 gate evidence 推导

- 定位：`skills/school-pptx/scripts/verify_pptx_renderer.py:1787`
- 相关：`skills/school-pptx/scripts/verify_pptx_renderer.py:1753`、`skills/school-pptx/scripts/verify_pptx_renderer.py:1767`、`skills/school-pptx/scripts/verify_pptx_renderer.py:835`、`skills/school-pptx/scripts/verify_pptx_renderer.py:1491`
- 问题：`called`/`gap_calls` 只能证明注册函数返回成功，`gap_outcome_audit` 中 `public_success`、`bounded_output` 和 `failure_vectors` 却直接写死为 `True`/`4`，没有读取各 gate 返回的真实 evidence。尤其 `table_header_only_gate()` 不审计成功输出的字节上限或内部路径，`code_literal_roundtrip_gate()` 也不审计输出长度；即使这些断言缺失或未来退化，aggregate 仍会输出 `bounded_output: true`。
- 影响：报告 JSON 会把未验证属性表示成已验证事实，削弱 43-09 用 aggregate 阻断 R43-C01/C02/W01 的目标，并掩盖 C-01 这类“gate 通过但冻结/发射不一致”的回归。
- 建议：让每个 gap gate 返回结构化 outcome（实际 exit、output bytes、路径审计、页数/高度等），aggregate 从 `evidence` 中校验并复制这些值；不要生成独立硬编码的成功布尔值。为 C-01 的字号/高度一致性增加 blocking assertion。

### [W-02] 受检媒体路径在校验后被再次打开，替换竞态仍可绕过 Pillow 错误映射

- 定位：`skills/school-pptx/scripts/pptx_objects.py:239`
- 相关：`skills/school-pptx/scripts/pptx_objects.py:207`、`skills/school-pptx/scripts/pptx_objects.py:244`、`skills/school-pptx/scripts/pptx_emit.py:225`、`skills/school-pptx/scripts/pptx_render.py:390`
- 问题：`_safe_image_size()` 已正确封装首次 `Image.open/size/verify` 的 bomb/identify/decode 异常，但返回后 `slide.shapes.add_picture(str(path), ...)` 会按路径再次打开文件。若媒体在两次打开之间被替换，第二次 Pillow `DecompressionBombError` 不在 `_safe_image_size()` 的 `try` 内，也不是 `PptxObjectError` 或 render 顶层捕获的异常类型。
- 复现：先让 `_safe_image_size()` 验证 1x1 PNG，随后在 `add_picture()` 前将同一路径替换为 20000x10000 PNG 头；第二次打开直接抛出未映射的 `PIL.Image.DecompressionBombError`，错误原文包含像素阈值。现有四向量都是静态文件，无法覆盖这个二次打开窗口。
- 影响：并发可写媒体目录中仍可能产生 traceback/Pillow 原文和绝对路径，绕过 R43-W01/VER-03 的 bounded public error 边界。旧 PPTX 因 PPTX-last 提交仍可保留，但公开诊断契约失守。
- 建议：校验后从同一已持有的只读 descriptor/内存 bytes 创建图片，避免按路径二次读取；至少把 `add_picture()` 的 Pillow bomb/format/decode 异常映射为相同 stable code，并增加“校验后替换”故障注入 gate。

## 已确认正常

- header-only table 会产生唯一 header fragment、唯一正整数 `row_heights_emu`，公开成品重开后是 1 行 native table，空 `school-pptx:table-name` placeholder 保留。
- 静态 Pillow bomb error/warning、无法识别图片和 verify/decode 失败均精确映射到 allowlist code，失败输出低于 8 KiB，旧 PPTX 不被替换。
- 同一 body slot 的普通 rich text 与 fenced code 由单一 textbox 按 fragment 顺序发射；code run 不经过 delimiter normalization，bold/highlight 普通 run 保持可编辑样式。

## 验证记录

- `python3 skills/school-pptx/scripts/verify_pptx_renderer.py code-literal-roundtrip`：PASS。
- `python3 skills/school-pptx/scripts/verify_pptx_renderer.py table-header-only`：PASS。
- `python3 skills/school-pptx/scripts/verify_pptx_renderer.py object-error-bounded`：PASS，4 个失败向量 code/退出码/旧目标保持均符合预期。
- `python3 skills/school-pptx/scripts/verify_pptx_renderer.py phase-43`：18 个固定顶层 gate 全部 PASS；同时额外向量确认 C-01 与 W-02 不在现有 aggregate 覆盖范围内。
- 未修改生产源码，未提交。
