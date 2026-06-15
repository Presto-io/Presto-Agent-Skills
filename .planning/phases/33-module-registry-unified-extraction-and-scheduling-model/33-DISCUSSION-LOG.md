# Phase 33: Module Registry, Unified Extraction, and Scheduling Model - Discussion Log

> **Audit trail only.** 不作为 planning、research 或 execution agents 的输入。
> 决策已写入 CONTEXT.md；本文件只保留讨论过的替代路径。

**Date:** 2026-06-15
**Phase:** 33-Module Registry, Unified Extraction, and Scheduling Model
**Areas discussed:** 统一 Markdown 解析, 模块注册与隐藏工件, YAML 转换, skill-local calendar.json, 共享 scheduling model, 跨模块时间源唯一性, 失败诊断

---

## 统一 Markdown 解析

| Option | Description | Selected |
|--------|-------------|----------|
| Unified Markdown as only source | 解析 `teaching-design-package-full.md` 形状，并从 frontmatter 与两个 body section 派生模块数据。 | ✓ |
| Module-authored sources | 让用户或 agent 维护分离模块 Markdown 作为源输入。 | |
| Legacy handoff files | 重新引入旧 package handoff 名称或 sibling skill 源文件。 | |

**User's choice:** Unified Markdown as only source.
**Notes:** 用户明确要求覆盖统一 Markdown 解析并聚焦 Phase 33；这也延续 v1.14 standalone package boundary。

---

## 模块注册与隐藏工件

| Option | Description | Selected |
|--------|-------------|----------|
| Package-owned registry | 注册 `teaching-plan` 与 `teaching-design`，包含顺序 metadata 和 hidden work outputs。 | ✓ |
| Flat renderer | 保留单个 package renderer，只写统一 Typst/PDF surface。 | |
| Runtime sibling orchestration | 把旧 standalone skills 当成 package internals 调用。 | |

**User's choice:** Package-owned registry.
**Notes:** Registry 必须支持未来模块扩展，同时避免 Phase 33 变成单体脚本堆砌。隐藏模块 Markdown/Typst 路径锁定在 `.teaching-design-package/work/`。

---

## YAML 转换

| Option | Description | Selected |
|--------|-------------|----------|
| Derived module frontmatter | 从统一 YAML 与 scheduling facts 生成 module YAML。 | ✓ |
| Teacher-maintained derived YAML | 让统一 Markdown frontmatter 维护 `total_hours`、日期、status 或模块渲染字段。 | |
| Independent module YAML | 保留分离模块 YAML 作为第二套 source of truth。 | |

**User's choice:** Derived module frontmatter.
**Notes:** `teachers` 生成 `teacher_name`；`daily_hours` 为 package-owned；`total_hours` 与 `use_time` 从授课计划行和真实 calendar consumption 派生。

---

## skill-local calendar.json

| Option | Description | Selected |
|--------|-------------|----------|
| Package-owned calendar resource | 新增 `skills/teaching-design-package/references/calendar.json`，并在 hidden evidence 中记录 hash。 | ✓ |
| Use sibling calendars at runtime | 运行时读取 `jiaoan-jihua` 或 `jiaoan-shicao` 的 sibling calendar。 | |
| Natural-day fallback | 不使用真实 calendar，直接按自然日顺推。 | |

**User's choice:** Package-owned calendar resource.
**Notes:** 可参考既有 sibling calendars，但 runtime scheduling 必须在只复制 `teaching-design-package` folder 的 standalone 情况下工作。

---

## 共享 scheduling model

| Option | Description | Selected |
|--------|-------------|----------|
| Real calendar consumption model | 使用 `calendar.json`、`first_teaching_day`、`daily_hours` 和源顺序行课时推导全部日期/周次/课时事实。 | ✓ |
| Natural-day sequential model | 继续当前 `sequential_teaching_days_default` 行为。 | |
| Per-module derivation | 让授课计划和教学设计两个模块分别计算日期。 | |

**User's choice:** Real calendar consumption model.
**Notes:** model 必须推导学年、学期、课程起止日期、任务起止日期、周次、星期、每日课时消耗，并在 calendar 缺失或耗尽时失败。

---

## 跨模块时间源唯一性

| Option | Description | Selected |
|--------|-------------|----------|
| Single source model | 两个模块读取同一个 package scheduling model。 | ✓ |
| Local recomputation | 每个模块从自身正文重新推导日期/课时。 | |
| Human override | 允许 module Markdown 覆盖生成的时间字段。 | |

**User's choice:** Single source model.
**Notes:** 教学设计时间字段和后续校验必须来自授课计划/calendar model，避免模块产物之间漂移。

---

## 失败诊断

| Option | Description | Selected |
|--------|-------------|----------|
| Hidden structured diagnostics | 在 `.teaching-design-package/` 下记录 calendar path/hash、推导摘要、generated module frontmatter 和分类失败。 | ✓ |
| Public diagnostic files | 把 status/model/log/calendar evidence 写入公开输出根目录。 | |
| Best-effort partial success | 能生成多少工件就生成多少，并 exit 0。 | |

**User's choice:** Hidden structured diagnostics.
**Notes:** 失败必须诚实且非零，尤其是缺少章节、禁止 derived YAML、calendar 无效/缺失、first day 不在 calendar、calendar 耗尽、行格式错误、时间证据不一致。

---

## Claude's Discretion

- 具体内部脚本拆分由 planner/executor 决定，但必须保留公开命令并保持 package-local ownership。
- Calendar schema 可参考既有 accepted calendars 或做 package-owned wrapper，但必须记录 path/hash 并使用真实可消费教学日期。

## Deferred Ideas

- Phase 34: 迁移 `jiaoan-jihua` formal renderer equivalence。
- Phase 35: 迁移 `jiaoan-shicao` formal renderer 与 strict activity validation。
- Phase 36: 强制 public course-name-prefixed delivery 与 final PDF merge。
