# Phase 52: 原生对象与受控媒体发射 - Context

**Gathered:** 2026-07-23
**Status:** Ready for planning

## Boundary

消费 Phase 51 已冻结且 hash-bound 的 `PhysicalDeckPlan`，为 `hero-evidence`、`annotated-image`、`process-overlay`、`kpi-evidence` 发射可编辑 PowerPoint/WPS 原生对象；复用已绑定媒体 payload 的 `contain` 放置。不得重新决定 variant、分页、裁切、字号或按路径重新读取媒体。

## Locked Decisions

- 标题、图注、数值、单位、标注、引线、流程节点、数据卡均为原生形状或文本框；信息文字不得烘焙进图片，禁止整页截图。
- 媒体只能来自 `MediaBinding.payload`，并在发射前复验 hash、大小、格式与 `contain`；不存在网络、字体、图标或模板下载后备路径。
- hero 发射主图与 2/3 KPI 卡；annotated-image 发射主图、编号锚区、标签与引线；process-overlay 发射 2--6 个流程节点、连接线与可选证据图；kpi-evidence 发射 2/3/4 个数据卡。
- 任何未知对象角色、几何、binding 或计划字段都 fail closed；不得将视觉页降级为旧布局成功产物。
- 本阶段不完成完整 fixture、runtime 文档或真人 WPS/PowerPoint UAT，均留给 Phase 53。
