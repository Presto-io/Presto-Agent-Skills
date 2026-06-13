---
template: "teaching-design-package"
course_name: "电气设备控制线路安装与调试"
major_name: "电气自动化技术"
teacher_name: "张老师"
class_name: "示例电气2班"
first_teaching_day: "2026-05-11"
daily_hours: 8
modules:
  teaching_plan:
    enabled: true
    handoff: "jiaoan-jihua-full.md"
  lesson_plans:
    enabled: true
    handoff: "jiaoan-shicao-full.md"
outputs:
  teaching_plan_typ: "teaching-plan.typ"
  lesson_plans_typ: "lesson-plans.typ"
  teaching_plan_pdf: "not_run"
  lesson_plans_pdf: "not_run"
---

# 电气设备控制线路安装与调试教学设计整包

## 课程与整包元数据

| 字段 | 内容 |
|------|------|
| 专业名称 | 电气自动化技术 |
| 课程名称 | 电气设备控制线路安装与调试 |
| 授课教师 | 张老师 |
| 授课班级 | 示例电气2班 |
| 首次授课日 | 2026-05-11 |
| 每日学时 | 8 |

## 调度输入

- 校历来源：`skills/jiaoan-jihua/references/calendar.json`。
- 排课合同：`references/scheduling-contract.md`。
- 排课起点：2026-05-11。
- 每日学时：8。

## 调度证据

| Source | 学习任务 | 学习环节 | 教学内容 | 学时 | 起止日期 | 周次 | 星期 | 消耗证据 |
|--------|----------|----------|----------|------|----------|------|------|----------|
| `task:1/stage:1/row:1` | CA6140卧式车床电气控制线路安装与调试 | 安技教育及旧知识回顾 | 安技教育 | 1 | 2026-05-11 - 2026-05-11 | 11 | 1 | 2026-05-11: 1H, remaining 7H |
| `task:1/stage:1/row:2` | CA6140卧式车床电气控制线路安装与调试 | 安技教育及旧知识回顾 | 讲解电工工作现场管理规范 | 1 | 2026-05-11 - 2026-05-11 | 11 | 1 | 2026-05-11: 1H, remaining 6H |
| `task:1/stage:1/row:3` | CA6140卧式车床电气控制线路安装与调试 | 安技教育及旧知识回顾 | 常用低压电器元件知识回顾，万用表的使用方法回顾 | 1 | 2026-05-11 - 2026-05-11 | 11 | 1 | 2026-05-11: 1H, remaining 5H |
| `task:1/stage:3/row:2` | CA6140卧式车床电气控制线路安装与调试 | 制定计划 | CA6140卧式车床电气元件布局图，接线图讲解 | 2 | 2026-05-12 - 2026-05-12 | 11 | 2 | 2026-05-12: 2H, remaining 6H |

## 授课计划

模块 handoff：`jiaoan-jihua-full.md`。

### CA6140卧式车床电气控制线路安装与调试

- `task:1/stage:1/row:1` 安技教育-1
- `task:1/stage:1/row:2` 讲解电工工作现场管理规范-1
- `task:1/stage:1/row:3` 常用低压电器元件知识回顾，万用表的使用方法回顾-1
- `task:1/stage:3/row:2` CA6140卧式车床电气元件布局图，接线图讲解-2

## 实操教案

模块 handoff：`jiaoan-shicao-full.md`。

### 学习任务分析

- 学习任务：CA6140车床电气控制线路安装与调试。
- 课时：40H。
- 起止日期：由 `task:1/*` 调度证据推导。

### 教学活动设计

- `lesson:1/activity:1` 安技教育：观看安全教育案例，讨论安全用电与触电急救要点。
- `lesson:1/activity:2` 低压电器元件回顾：复习元件符号、结构和检测方法。

### 学业评价

- 安全文明生产、线路安装质量、检测调试记录和成果展示按教师给定细则评价。

## 输出清单

| Artifact | Status | Evidence |
|----------|--------|----------|
| `jiaoan-jihua-full.md` | planned | module handoff |
| `jiaoan-shicao-full.md` | planned | module handoff |
| `teaching-plan.typ` | planned | render-split |
| `lesson-plans.typ` | planned | render-split |
| `teaching-plan.pdf` | not_run | explicit PDF compile not executed |
| `lesson-plans.pdf` | not_run | explicit PDF compile not executed |

## 复核标记

无
