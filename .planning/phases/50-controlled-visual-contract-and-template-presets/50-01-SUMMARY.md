---
phase: 50-controlled-visual-contract-and-template-presets
plan: "01"
type: execute-summary
requirements: [VIS-01, VIS-02, VIS-03]
completed: 2026-07-23
---

# Phase 50 Plan 01: Markdown 受控视觉合同 Summary

四种新增布局已进入唯一 `layout` 选择面，并由 parser 转换为可定位的受限逻辑语义。

## 完成内容

- 新增 `hero-evidence`、`annotated-image`、`process-overlay`、`kpi-evidence` 的严格 block shape、容量和来源行语义。
- `annotated-image` 只接受连续 `1.` 起的 3--5 个短标签；KPI 只接受数值列；流程页可选零或一张本地证据图。
- `image-text`、`gallery` 和新增媒体布局的每张图片均要求非空图注；缺失媒体继续是非零、带安全 placeholder 的 best-effort 输入状态。
- 公开 Markdown contract 更新为 14 explicit + 1 implicit layout，并明确无坐标、样式、裁切或 raw OOXML authoring 面。
- 回归覆盖空图注、错误/超量结构、趋势/SVG KPI、非连续与自由段落标注、多图、超量流程、未知 layout/attribute、样式越权和缺失媒体。

## 验证

`python3 skills/school-pptx/scripts/verify_markdown_contract.py contract` 通过。

## 边界

未实现物理分页、冻结计划、PPTX 发射、完整 fixture 扩充或 WPS 人工 UAT；这些仍属于 Phase 51--53。
