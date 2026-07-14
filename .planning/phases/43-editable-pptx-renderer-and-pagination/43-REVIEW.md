---
status: issues_found
phase: 43-editable-pptx-renderer-and-pagination
plan: 43-10
depth: standard
files_reviewed: 5
findings:
  critical: 2
  warning: 2
  info: 0
  total: 4
---

# Phase 43 Plan 43-10 代码审查

## 审查范围

- 变更提交：`7e399f8`、`5a024e8`、`f9f335e`，并核对当前 `HEAD`。
- 源文件：`pptx_paginate.py`、`pptx_emit.py`、`pptx_objects.py`、`pptx_render.py`、`verify_pptx_renderer.py`。
- 重点：descriptor traversal、绝对/相对路径与 symlink、fd/bytes 上限、异常泄漏、分页/发射同源排版、runtime diagnostic、aggregate false-green、测试可信度与回归。

## Critical

### [C-01] `contents.body` 仍按 18pt 分页、按冻结的 26pt 发射，合法成功成品可静默裁切目录

- 定位：`skills/school-pptx/scripts/pptx_paginate.py:690`
- 相关：`skills/school-pptx/scripts/pptx_paginate.py:789`、`skills/school-pptx/scripts/pptx_emit.py:241`
- 问题：`build_deck_plan()` 为 `contents.body` 冻结 `font_size_max=26pt`，emitter 也机械消费该值；但 `_contents_fragments()` 仍独立读取 `font_size_min=18pt`，并按 18pt 的单项高度进行分区。该专用分页路径没有消费本计划新建的 frozen typography，也没有计入 emitter 对每个目录段落设置的 2pt `space_after`。
- 复现：合法 Markdown 含一个空 `contents` slide 和 5 个后续章节。公开 render 退出 `0` 并打印“渲染成功”，计划只生成 1 张目录物理页；重开后 5 个 26pt 段落按同一 `TextMeasure` 合计 `156.0pt`，而 body effective height 仅 `118.125pt`。
- 影响：重新制造了 Plan 43-10 要关闭的“规划字号小于发射字号”缺口，直接阻断 PPTX-08 与 Phase 43 目标。目录文本仍存在于 OOXML，但 viewer 中可能被 text frame 裁切。
- 建议：让 `_contents_fragments()` 接收并使用与 emitter 完全相同的 frozen font/margins/line spacing/paragraph spacing 与 effective geometry；增加 5 项临界目录黑盒向量，重开后按整帧所有段落重测并要求扩页。

### [C-02] fragment 子标题未计入分页高度，带 `###` 的 mixed code 仍可退出 0 且每页超槽

- 定位：`skills/school-pptx/scripts/pptx_paginate.py:239`
- 相关：`skills/school-pptx/scripts/pptx_objects.py:177`、`skills/school-pptx/scripts/verify_pptx_renderer.py:984`
- 问题：`_fragment_height()` 只测量 `fragment.text` 或 `fragment.items`，完全忽略 `fragment.heading`；但 `add_fragment_text_frame()` 会先把 heading 发射为一个独立的 24pt/22pt 段落，再发射正文或 code 段落。分页后的每个 code fragment 都保留同一个 heading，因此遗漏会在每张派生页重复发生。
- 复现：合法 `title-content` 仅包含 `### 源码` 和 4 行×40 个中文字符的 fenced code。公开 render 退出 `0`，生成 2 张正文物理页；每页 code 自身为 `117.2pt`，heading 另占 `28.8pt`，整帧合计 `146.0pt > 118.125pt`。
- 影响：R43-C03 声称的“任何物理页 display height 不超过 effective content height”不成立，且现有 aggregate 仍 PASS。普通 paragraph/list heading 也受同一遗漏影响。
- 建议：分页成本必须按 emitter 的真实段落序列计算，包括 heading、每个 list item、code 段落及各段 `space_after`；测试应重测完整 text frame，而不是只测 Consolas run 对应的 `fragment.text`。

## Warning

### [W-01] 通用 body typography helper 使专用 `code` 布局改为 14pt 规划、10pt 发射

- 定位：`skills/school-pptx/scripts/pptx_paginate.py:367`
- 相关：`skills/school-pptx/scripts/pptx_emit.py:179`
- 问题：`_simple_slide_fragments()` 对所有布局无条件调用 `_selected_body_typography()`，因此专用 `code` slot 使用 manifest `font_size_max=14pt` 分页；`build_deck_plan()` 却不冻结 `code` 字号，emitter 继续回退 `font_size_min=10pt`。43-10 之前两端均使用最小字号，本次重构引入新的规划—发射漂移。
- 影响：不会导致裁切，但会让合法专用 code deck 产生不必要的额外物理页，并违反计划中“专用 code/table 保留既有受控字号语义”的回归边界。
- 建议：body helper 只用于普通 body target；专用 code 明确冻结并共享其受控字号，或继续在两端统一使用 10pt。增加 dedicated-code frozen/reopen 字号与页数回归。

### [W-02] 新 gate 只重测 code run，aggregate 因窄向量与硬编码 evidence 再次 false-green

- 定位：`skills/school-pptx/scripts/verify_pptx_renderer.py:903`
- 相关：`skills/school-pptx/scripts/verify_pptx_renderer.py:1008`、`skills/school-pptx/scripts/verify_pptx_renderer.py:1038`、`skills/school-pptx/scripts/verify_pptx_renderer.py:1967`、`skills/school-pptx/scripts/verify_pptx_renderer.py:2154`
- 问题：`mixed_fragment_capacity_gate()` 的输入不含 `###` heading，且高度断言只测 `fragment.text` 对应的 code run，没有汇总同一 text frame 的所有段落；它也不覆盖被新冻结的 `contents.body`。此外 gate 返回中仍存在 `joined_equality: True`、`frozen_projection_equal: True`、`old_target_preserved: True`，媒体 `embedded_hash` 还回填为预期 `original_hash` 而不是实际 `embedded_hashes` 项；AST 审计只检查最终 `gap_outcome_audit` assignment，无法发现这些上游常量。
- 影响：本次官方 `mixed-fragment-capacity`、`media-descriptor-binding` 与 20-gate `phase-43` 全部 PASS，但 C-01/C-02 两个公开成功裁切反例同时成立，说明 R43-W02 的 aggregate false-green 只被表面关闭。
- 建议：gate 返回实际比较表达式和实际提取值；aggregate 校验整帧高度、所有 frozen body 布局以及 heading/list/code 组合。AST/source guard 应覆盖证据生产函数，或直接删除可由原始 evidence 重算的成功布尔字段。

## 安全审查结果

- 相对媒体从 Markdown 父目录、绝对媒体从 `/` 开始逐分量 `O_NOFOLLOW` 打开；中间目录和最终普通文件均经 descriptor 状态确认，已覆盖相对中间/最终 symlink 与绝对最终 symlink。
- 最终 fd 读取受 `MAX_MEDIA_BYTES + 1` 限制，所有成功/失败路径在 `finally` 逆序关闭；Pillow 校验与 `add_picture(BytesIO(payload))` 消费同一 immutable bytes，未发现二次路径打开。
- bomb、格式、decode、symlink 与未知第三方异常均收敛为 bounded domain code；公开故障输出未泄漏 traceback、Pillow 原文或绝对媒体路径。
- runtime `MEDIA_MISSING` 会生成可编辑占位符、合并结构化 error、发布同 stem best-effort 双产物并退出非零；未发现 frozen plan 被修改。

## 验证记录

- `python3 -m py_compile`（5 个受审文件）：PASS。
- `python3 skills/school-pptx/scripts/verify_pptx_renderer.py mixed-fragment-capacity`：PASS，但未覆盖 C-01/C-02。
- `python3 skills/school-pptx/scripts/verify_pptx_renderer.py media-descriptor-binding`：PASS。
- `python3 skills/school-pptx/scripts/verify_pptx_renderer.py phase-43`：20 个固定顶层 gate 全部 PASS，`required/called` 一致、`dynamic_skips=0`；仍被上述两个反例证明 false-green。
- 手工黑盒反例：带 heading 的 mixed code 为 `146.0pt > 118.125pt` 且公开退出 0；5 项 contents 为 `156.0pt > 118.125pt` 且公开退出 0。
- 未修改实现代码，未提交。
