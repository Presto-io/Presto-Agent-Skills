# Phase 49: 聚合验证、跨 Runtime 与发布验收 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-18
**Phase:** 49-聚合验证、跨 Runtime 与发布验收
**Areas discussed:** 聚合证据权威、PDF/PNG 结构验收、六 Runtime 安装验证、非开发环境 UAT

---

## 聚合证据权威

| Option | Description | Selected |
|--------|-------------|----------|
| 固定 registry 与原始证据重算 | 字面 gate、required/called 精确相等、从原始产物重算 | ✓ |
| 动态发现测试 | 按环境发现并运行可用测试 | |
| 沿用子测试自报 | 直接聚合各生产者的 passed/count | |

**User's choice:** `--auto` 采用推荐默认：固定 registry 与原始证据重算。
**Notes:** 质量债务和安全债务不能被聚合 PASS 掩盖。

---

## PDF/PNG 结构验收

| Option | Description | Selected |
|--------|-------------|----------|
| 重开并验证结构、内容和布局 | 验证 A4、页数、主题、照片、模块、命名与 hash | ✓ |
| 只验证 PDF 元数据 | 检查页框与页数，不核对内容映射 | |
| 只验证文件非空 | 仅存在性与可打开检查 | |

**User's choice:** `--auto` 采用推荐默认：重开并验证结构、内容和布局。
**Notes:** 证据留在 caller-owned verify workdir，不能污染正式 triples。

---

## 六 Runtime 安装验证

| Option | Description | Selected |
|--------|-------------|----------|
| whole-folder + CLI fallback + 安装 fixture | 单一 canonical skill，逐 runtime 验证完整目录与显式入口 | ✓ |
| 维护六份技能 | 为每个 runtime 分叉技能主体 | |
| 仅文档声明支持 | 不运行安装或入口验证 | |

**User's choice:** `--auto` 采用推荐默认：whole-folder、显式 CLI fallback 和安装 fixture。
**Notes:** OpenClaw 与 Hermes Agent 不得动态跳过；未实测自动发现时只承诺显式 fallback。

---

## 非开发环境 UAT

| Option | Description | Selected |
|--------|-------------|----------|
| hash 绑定人工 UAT | 固定版本、字体、fixture、环境与 PDF/PNG hash | ✓ |
| 本机自动截图 | 仅开发机自动生成截图并自报通过 | |
| 仅记录环境版本 | 不绑定实际产物和人工观察 | |

**User's choice:** `--auto` 采用推荐默认：hash 绑定的非开发环境人工 UAT。
**Notes:** 自动化只能准备证据；没有人工结果时阶段保持 `human_needed`。

## Claude's Discretion

- 固定 gate 数量、稳定 ID、证据 schema、PDF/PNG 解析工具和非开发环境具体实现方式。

## Deferred Ideas

None.
