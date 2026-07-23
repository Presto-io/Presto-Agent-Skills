# Phase 50: 受控视觉合同与模板预设 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-23
**Phase:** 50-受控视觉合同与模板预设
**Areas discussed:** 新布局语义与 Markdown 选择、媒体与图注、测试 Demo、溢出与 fixture、人工审阅和仓库操作

---

## 新布局语义与 Markdown 选择

| Option | Description | Selected |
|--------|-------------|----------|
| 首发四种布局 | `hero-evidence`、`annotated-image`、`process-overlay`、`kpi-evidence` 同时进入首发范围。 | ✓ |
| 缩小首发范围 | 将存在语义歧义的布局留待以后。 | |
| 自由视觉属性 | 为标注或构图允许作者提供坐标、样式或裁切。 | |

**User's choice:** 四种布局全部首发；继续使用既有唯一 `layout` 选择方式，每页只有一个布局。
**Notes:** `annotated-image` 使用 Markdown 编号清单，编号映射 manifest 固定插槽；3--5 个编号短标签，禁止自由段落或作者坐标。`hero-evidence` 支持一张主图和 2--3 个 KPI；`process-overlay` 可无图并使用原生流程预设；`kpi-evidence` 固定 2/3/4 项，首发没有趋势、图表或 SVG。

---

## 媒体、图注与测试 Demo

| Option | Description | Selected |
|--------|-------------|----------|
| 本地受控媒体 | 用户提供工程内图片或直接交给 AI，沿用本地媒体安全契约。 | ✓ |
| 联网补全媒体 | 渲染期搜索、下载或生成图片。 | |
| 提交临时 Demo 素材 | 将可替换试验图作为公开 fixture 资产提交。 | |

**User's choice:** 先做可替换图片的测试 Demo；临时资产仅在仓库已有 ignore 目录中活动。
**Notes:** 每张图片必须有非空图注，必要时以文件名替代。缺失或非法媒体沿用现有非成功、局部 placeholder 契约；临时 Demo 不进入公开交付或提交历史。

---

## 溢出、fixture 与人工审阅

| Option | Description | Selected |
|--------|-------------|----------|
| 稳定分页优先 | 超量内容由固定规则分页，能力外输入返回定位错误。 | ✓ |
| 渲染期自动压缩 | 由 emitter 临时缩字、换布局或重排。 | |
| 多个完整 fixture | 将旧布局和新布局拆分为并列的完整来源。 | |

**User's choice:** 超长标题与图注优先稳定分页，超出能力可定位报错；保留唯一完整 Markdown fixture。
**Notes:** 开发完成到用户可亲自 WPS 审阅为止；不把人工 UAT 记为自动 PASS，也不声称已完成真人审阅。

---

## 仓库操作

| Option | Description | Selected |
|--------|-------------|----------|
| main 单人开发 | 直接在 `main` 按 commander 流程推进，不 push。 | ✓ |
| 独立功能分支 | 建分支后再合并。 | |

**User's choice:** 直接在 `main`，授权 commander 流程，不 push。
**Notes:** 后续每条 GSD 命令由独立子代理完成；本讨论命令只创建讨论产物。

---

## Claude's Discretion

- 在既有 ignore 目录内选择临时测试 Demo 的具体组织和可替换图片，不得提交为公开资产。

## Deferred Ideas

- 冻结物理计划、原生对象发射、完整验证及真人 UAT 签署按路线图移交 Phase 51--53。
