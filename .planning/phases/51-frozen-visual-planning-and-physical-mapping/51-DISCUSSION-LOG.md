# Phase 51: 冻结视觉规划与物理映射 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-23
**Phase:** 51-冻结视觉规划与物理映射
**Areas discussed:** 计划层级与输入绑定、variant 与稳定分页、逻辑物理映射与 emitter 边界、阶段顺序与 UAT 边界

---

## 计划层级与输入绑定

| Option | Description | Selected |
|---|---|---|
| 只保存逻辑语义 | emitter 在发射时补选 variant、分页与媒体。 | |
| 两层冻结计划 | `VisualPlan` 绑定审阅输入，`PhysicalDeckPlan` 冻结全部物理决定与 hash。 | ✓ |

**User's choice:** 会议确认 manifest、媒体和 Markdown 必须 hash 绑定，并由不可变计划承接后续实现。
**Notes:** 计划还绑定 template hash 与单次安全读取的媒体身份，防止路径在计划后变化。

---

## Variant 与稳定分页

| Option | Description | Selected |
|---|---|---|
| emitter 自适应压缩 | 发射时根据对象数量、字体或图片临时选预设。 | |
| manifest 决定 variant | 只用 manifest 的固定容量，按稳定规则原子分页或定位失败。 | ✓ |

**User's choice:** 四布局首发，沿用唯一 `layout`；超量优先自动分页，能力外定位报错。
**Notes:** 标注、流程、KPI、媒体和图注的组合保持原子，分区以最少物理页和最长最早前缀作为固定 tie-break。

---

## 逻辑物理映射与 emitter 边界

| Option | Description | Selected |
|---|---|---|
| 只记录最终页数 | 不能反向追溯物理页来源或媒体身份。 | |
| 完整有序映射 | 每页冻结来源逻辑页、continuation、variant、角色、媒体 hash 与对象组。 | ✓ |

**User's choice:** 逻辑页到物理页映射必须完整；emitter 不能再选择布局、分页、裁切或字号。
**Notes:** hash 不一致、未知 variant、字段缺失或映射不完整必须失败关闭。

---

## 阶段顺序与 UAT 边界

| Option | Description | Selected |
|---|---|---|
| 在本阶段发射并完成验收 | 提前实现 PPTX 对象、完整验证或 WPS UAT。 | |
| 仅冻结规划 | 原生对象发射留给 Phase 52；完整验证与用户 WPS 审阅留给 Phase 53。 | ✓ |

**User's choice:** 用户亲自审阅；开发仅推进到可审阅状态。
**Notes:** Phase 50 当前仍等待 audit/complete。此次记录只保存后续决策，不修改 gate 或推进 Phase 51 实现。

---

## Claude's Discretion

- 在不改变已锁定字段、排序和失败关闭边界的前提下，后续代理可选择模型的具体模块拆分、函数命名、canonical JSON 编码和稳定错误码名称。

## Deferred Ideas

- PPTX 原生对象发射、完整 fixture/aggregate、runtime 文档和 WPS 真人 UAT 不属于 Phase 51，分别保留给 Phase 52/53。
