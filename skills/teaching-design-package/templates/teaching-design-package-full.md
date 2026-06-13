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
  end_of_term:
    enabled: false
    handoff: "end-of-term-full.md"
    source_data: "end-of-term-source.json"
    workdir: "end-of-term-output"
    manifest: "end-of-term-output/manifest.json"
outputs:
  teaching_plan_typ: "teaching-plan.typ"
  lesson_plans_typ: "lesson-plans.typ"
  end_of_term_typ: "end-of-term-output/end-of-term-package.typ"
  teaching_plan_pdf: "not_run"
  lesson_plans_pdf: "not_run"
  end_of_term_pdf: "not_run"
  combined_pdf: "teaching-design-package.pdf"
---

# 教学设计整包

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

- 校历来源：`references/scheduling-contract.md` 约定的 `calendar.dates`、`calendar.holidays`、`calendar.makeup_days`。
- 排课起点：`first_teaching_day: 2026-05-11`。
- 学时容量：`daily_hours: 8`。
- 源顺序教学项示例：
  - `task:1/stage:1/row:1`：安技教育，1H。
  - `task:1/stage:3/row:2`：CA6140卧式车床电气元件布局图，接线图讲解，2H。
  - `lesson:1/activity:1`：安技教育活动片段，1H。

## 调度证据

| Source | 教学项 | 学时 | 起止日期 | 周次 | 星期 | 消耗证据 | 复核 |
|--------|--------|------|----------|------|------|----------|------|
| `task:1/stage:1/row:1` | 安技教育 | 1 | 2026-05-11 - 2026-05-11 | 11 | 1 | 2026-05-11: 1H, remaining 7H | 无 |
| `task:1/stage:1/row:2` | 讲解电工工作现场管理规范 | 1 | 2026-05-11 - 2026-05-11 | 11 | 1 | 2026-05-11: 1H, remaining 6H | 无 |
| `task:1/stage:3/row:2` | CA6140卧式车床电气元件布局图，接线图讲解 | 2 | 2026-05-12 - 2026-05-12 | 11 | 2 | 2026-05-12: 2H, remaining 6H | 无 |
| `lesson:1/activity:1` | 安技教育活动片段 | 1 | 2026-05-11 - 2026-05-11 | 11 | 1 | 继承授课计划同源排课证据 | 无 |

## 授课计划

模块 handoff：生成或维护 `jiaoan-jihua-full.md`，再交给 `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render`。

> 本节只保存整包级摘要和源指针，不复制 `jiaoan-jihua-full.md` 的完整模板。

### CA6140卧式车床电气控制线路安装与调试

- `task:1/stage:1/row:1` 安技教育-1
- `task:1/stage:1/row:2` 讲解电工工作现场管理规范-1
- `task:1/stage:3/row:2` CA6140卧式车床电气元件布局图，接线图讲解-2

## 实操教案

模块 handoff：生成或维护 `jiaoan-shicao-full.md`，再交给 `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render`。

> 本节只保存整包级摘要和源指针，不复制 `jiaoan-shicao-full.md` 的完整模板。

### 学习任务分析

- 学习任务：CA6140车床电气控制线路安装与调试。
- 课时：40H。
- 起止日期：由 `task:1/*` 调度证据推导，缺失时写入复核标记。

### 教学活动设计

- `lesson:1/activity:1` 安技教育：观看安全教育案例，讨论安全用电与触电急救要点。
- `lesson:1/activity:2` 低压电器元件回顾：复习元件符号、结构和检测方法。

### 学业评价

- 安全文明生产、图纸识读、线路安装、检测调试、过程记录和成果展示按教师给定评价细则填写。

## 期末材料

模块 handoff：当 `modules.end_of_term.enabled: true` 时，生成或维护 `end-of-term-full.md`，再交给 `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh` 的 `validate`、`markdown`、`render`、`verify`、`manifest` 公开命令。

> 本节只保存整包级摘要、源数据路径和 artifact 指针，不复制 `end-of-term-full.md` 的完整模板，也不覆盖模块本地 `## 复核标记`。

- source data：`end-of-term-source.json`
- workdir：`end-of-term-output`
- module manifest：`end-of-term-output/manifest.json`
- module review gate：`end-of-term-full.md` 中的 `## 复核标记` 必须为 `无`

## 输出清单

| Artifact | Source | Status | Evidence |
|----------|--------|--------|----------|
| `jiaoan-jihua-full.md` | `## 授课计划` | planned | 模块 handoff scaffold |
| `jiaoan-shicao-full.md` | `## 实操教案` | planned | 模块 handoff scaffold |
| `teaching-plan.typ` | `jiaoan-jihua-full.md` | planned | 等待 render-split |
| `lesson-plans.typ` | `jiaoan-shicao-full.md` | planned | 等待 render-split |
| `end-of-term-full.md` | `end-of-term-source.json` | disabled | `modules.end_of_term.enabled: false` 时不要求存在 |
| `end-of-term-output/end-of-term-package.typ` | `end-of-term-full.md` | not_run | 仅启用期末模块后由模块 renderer 生成 |
| `end-of-term-output/end-of-term-package.pdf` | `end-of-term-output/end-of-term-package.typ` | not_run | 仅显式 PDF 编译成功且文件存在后可改为 passed |
| `end-of-term-output/manifest.json` | end-of-term module | not_run | 记录 `review_cleared`、table/workbook/PDF 状态 |
| `end-of-term-output/tables/score-data.json` | end-of-term module | not_run | 模块 deterministic table artifact |
| `end-of-term-output/tables/calculated-score-data.json` | end-of-term module | not_run | 模块 calculated score evidence |
| `end-of-term-output/tables/score-summary.json` | end-of-term module | not_run | 模块 score summary evidence |
| `end-of-term-output/tables/highlight-evidence.json` | end-of-term module | not_run | 模块 review/highlight evidence |
| `end-of-term-output/tables/score-list.md` | end-of-term module | not_run | 模块 teacher-facing score list |
| `end-of-term-output/tables/score-list.xlsx` | end-of-term module | not_run | 模块 workbook artifact |
| `end-of-term-output/tables/scorebook.xlsx` | end-of-term module | not_run | 模块 scorebook workbook |
| `teaching-plan.pdf` | `teaching-plan.typ` | not_run | 仅显式 PDF 编译成功后可改为 passed |
| `lesson-plans.pdf` | `lesson-plans.typ` | not_run | 仅显式 PDF 编译成功后可改为 passed |
| `teaching-design-package.pdf` | selected split PDFs | not_run | 仅显式合并/编译成功且文件存在后可改为 passed |

## 复核标记

无

<!--
Package-level clearance never overrides enabled module-local clearance.
If `end-of-term-full.md` still has unresolved `## 复核标记`, package final_ready remains false.
-->
