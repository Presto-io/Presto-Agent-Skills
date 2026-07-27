# Phase 53: 完整验证、Runtime 文档与真人 UAT - Context

**Gathered:** 2026-07-24
**Status:** Ready for planning

## Boundary

建立覆盖旧 11 个布局与四种新增构图的完整 fixture，固定公开 verification registry，补齐 canonical 技能及六 runtime adapter 文档，并为真实 WPS/PowerPoint 操作者生成 Markdown/PPTX SHA-256 绑定的 UAT 记录。

## Locked Decisions

- 自动验证必须固定注册表、零动态跳过，重开 PPTX 从 OOXML/native objects 复算结构、对象与媒体证据；截图和像素评分不构成通过证据。
- fixture 必须同时包含旧 11 个布局和 `hero-evidence`、`annotated-image`、`process-overlay`、`kpi-evidence`，使用受控本地媒体。
- 文档覆盖 canonical `SKILL.md`、Markdown contract、renderer/verification/UAT references 与六 runtime adapter；明确离线、安装验证和人工 UAT 不能由自动通过替代。
- UAT 是最终人机边界：至少一名真实 WPS/PowerPoint 操作者对本次 Markdown/PPTX SHA-256 绑定 artifact 检查主体样式、四构图可读、媒体无失真、信息层可编辑/移动/取消组合。
