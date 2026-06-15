# Phase 35: Teaching Design Formal Renderer and Cross-Module Validation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-15
**Phase:** 35-Teaching Design Formal Renderer and Cross-Module Validation
**Areas discussed:** 旧格式迁移边界, 任务/环节/活动映射, 课时与日期权威来源, 失败诊断与输出语义

---

## 旧格式迁移边界

| Option | Description | Selected |
|--------|-------------|----------|
| Package-owned migration | 把旧 `jiaoan-shicao` 可接受正式格式迁入 `teaching-design-package` 内部，旧 skill 只读参考，不作为 runtime dependency。 | ✓ |
| Runtime delegation | package 渲染时调用旧 `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`。 | |
| Generic renderer refactor | 先抽一个跨 package/legacy skill 共用 renderer 框架。 | |

**User's choice:** Package-owned migration.
**Notes:** 用户明确要求旧 `skills/jiaoan-shicao` 只读参考、不可修改、不可作为 package runtime dependency。Phase 35 不 plan、不 execute，只锁定讨论上下文。

---

## 任务/环节/活动映射

| Option | Description | Selected |
|--------|-------------|----------|
| Source pointer first | 以“学习任务 + 学习环节 + 活动顺序”为主，标题归一化只作为校验辅助。 | ✓ |
| Fuzzy title matching | 主要依赖标题相似度，在结构顺序变化时自动重排。 | |
| Total-only validation | 只检查教学设计活动总课时是否等于授课计划总课时。 | |

**User's choice:** Source pointer first.
**Notes:** 用户特别要求澄清 `课时：xH`、活动 `##### xH`、任务起止日期、任务数量、环节数量、活动数量、标题对应如何从授课计划/scheduling model 严格映射。上下文锁定为任一数量、标题、顺序、课时或日期不一致都必须失败。

---

## 课时与日期权威来源

| Option | Description | Selected |
|--------|-------------|----------|
| Teaching-plan scheduling model | `# 授课进度计划` 行课时 + skill-local calendar + `first_teaching_day` 是唯一权威来源，teaching-design 只消费或验证。 | ✓ |
| Teaching-design body owns dates | 从教案正文中的 `课时：`、`#####`、`起止日期` 自行计算或覆盖 scheduling model。 | |
| Renderer recomputes dates | formal renderer 内部重新跑 calendar/date logic。 | |

**User's choice:** Teaching-plan scheduling model.
**Notes:** Phase 33/34 已完成事实被吸收：统一 Markdown 是唯一内容源；`# 授课进度计划` 是课时和排课唯一原始来源；`calendar.json` 在 package skill 自身目录；`teaching-plan` formal renderer 已 package-owned。

---

## 失败诊断与输出语义

| Option | Description | Selected |
|--------|-------------|----------|
| Hard fail with hidden diagnostics | 不一致时非零退出，写 `.teaching-design-package/` hidden diagnostics/status，不能生成最终成功产物。 | ✓ |
| Warn and continue | 记录 warning，但继续生成 PDF。 | |
| Public diagnostics | 把 mismatch 报告写到 public root 方便查看。 | |

**User's choice:** Hard fail with hidden diagnostics.
**Notes:** 用户明确要求不一致时必须失败并写隐藏诊断。成功 public root 不应泄漏 module Markdown/Typst/model/status/diagnostics/log/calendar JSON；Phase 36 再完成课程名前缀公开交付与 merge 收口。

---

## Claude's Discretion

- Renderer implementation shape may be Node helper, Bash helper, AWK migration, or package-model renderer module, as long as it stays package-owned and standalone.
- Equivalence verification may combine normalized Typst diff, structural assertions, PDF smoke checks, and hash evidence.

## Deferred Ideas

- Phase 36 owns course-name-prefixed public `1 + 1 + N` output contract and final PDF merge semantics.
- Shared formal jiaoan renderer extraction is future-only and should wait until package-owned migrations are stable.
