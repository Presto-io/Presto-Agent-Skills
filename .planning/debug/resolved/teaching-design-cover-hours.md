---
status: resolved
trigger: "teaching-design-package 教学设计方案渲染中，封面计划总课时和学习任务分析课时应保留 H；封面标签四个字和五个字应等宽，冒号对齐。用户提供截图示例。"
created: 2026-06-15
updated: 2026-06-15
---

# Debug Session: teaching-design-cover-hours

## Symptoms

- expected_behavior: "教学设计方案封面 `计划总课时` 显示为 `160H`；学习任务分析表中的 `课时` 显示为 `40H`、`60H` 等；封面标签四字项通过字间距撑到与五字项等宽，所有冒号对齐。"
- actual_behavior: "当前 package-owned teaching-design renderer 会把 `160H` 正规化为 `160`，学习任务分析表输出纯数字课时；封面标签按整段文字测量宽度，四字项没有按截图样式拉开字距。"
- error_messages: "无命令错误；属于渲染格式/版式回归。"
- timeline: "v1.15 package-owned teaching-design renderer 迁移后暴露；旧模板/旧 renderer 中已有类似 normalize_total_hours 和 cover label grid 行为。"
- reproduction: "运行 `skills/teaching-design-package/scripts/teaching-design-package.sh example` 后执行 `render-package --pdf`，检查隐藏 `.teaching-design-package/work/teaching-design.typ` 或输出 PDF 封面/学习任务分析。"
- user_artifact: "/var/folders/kh/3z1m41y56mgd98lxmb9zjjsw0000gn/T/codex-clipboard-190b00f5-2f5f-4fff-b1eb-02b49fc8c58b.png"

## Current Focus

- hypothesis: "`skills/teaching-design-package/scripts/teaching-design-renderer.js` 继承了旧 `normalizeTotalHours()` 去 H 行为，并在学习任务分析中直接输出 `task.derived_total_hours`；封面标签用整段文本测量宽度而不是逐字 grid，因此四字标签没有撑满到五字标签宽度。"
- test: "生成示例 model 和 hidden `teaching-design.typ`，检查 `计划总课时` 行、学习任务分析 `课时` 单元格以及 cover label Typst 结构。"
- expecting: "修复后 Typst 包含封面 `160H`、学习任务分析 `[40H]` 等，且封面标签通过逐字 grid 或等效结构保证冒号对齐。"
- next_action: "resolved; keep regression evidence with the renderer change."
- reasoning_checkpoint: "初步 rg 已定位到 package renderer；旧 jiaoan-shicao 脚本仅作为格式参考，不应改动或恢复为依赖。"
- tdd_checkpoint: "workflow.tdd_mode 未配置，按现有黑盒渲染验证补回归。"

## Evidence

- timestamp: 2026-06-15
  observation: "`rg` 显示 package renderer 中 `normalizeTotalHours()` 会移除 H；`emitTaskAnalysis()` 输出 `${task.derived_total_hours}`；`emitCover()` 用 `measure(text(...)[课程名称：]).width` 与普通文本 label。"
  implication: "三个症状都可由同一 renderer 文件解释。"
- timestamp: 2026-06-15
  observation: "旧 `skills/jiaoan-shicao/scripts/render_v110_typst.awk` 的 `emit_cover_label()` 对四字/五字标签使用逐字 `#grid(columns: (auto, 1fr, ...))`，可实现截图所示标签撑宽和冒号对齐。"
  implication: "修复可迁移这种纯 Typst 输出模式到 package-owned renderer，而不依赖旧脚本。"
- timestamp: 2026-06-15
  observation: "只读 `gsd-debugger` 复核确认根因在 package-owned renderer 输出层，不在 `package-model.js`；旧 `jiaoan-shicao` 只应作为版式参考，不应修改。"
  implication: "修复范围应限制在 `skills/teaching-design-package/scripts/teaching-design-renderer.js`。"
- timestamp: 2026-06-15
  observation: "修复后黑盒 `render-package --pdf` 生成 hidden Typst，grep 命中封面 `[160H]`、学习任务分析 `[40H]`/`[60H]`，并命中四字/五字封面标签逐字 `#grid(columns: (auto, 1fr, ...))`。"
  implication: "三个用户可见症状已在真实生成路径中闭环。"
- timestamp: 2026-06-15
  observation: "PyMuPDF 将 `电气设备控制线路安装与调试教学设计方案.pdf` 首页渲染为 `/private/tmp/tdpkg-cover-hours-cover-page.png`；视觉检查显示封面标签冒号对齐，`计划总课时` 为 `160H`。"
  implication: "源码和 PDF 视觉层均通过。"
- timestamp: 2026-06-15
  observation: "`node --check skills/teaching-design-package/scripts/teaching-design-renderer.js`、`bash -n skills/teaching-design-package/scripts/teaching-design-package.sh`、`git diff --check` 均通过；`git diff --name-only -- skills/jiaoan-shicao` 无输出。"
  implication: "修复没有破坏脚本语法、仓库空白检查或旧 `jiaoan-shicao` 边界。"

## Eliminated

- hypothesis: "PDF 合并或最终交付命名导致字段格式变化。"
  reason: "问题出现在 hidden `teaching-design.typ` 生成层，合并只消费模块 PDF。"

## Resolution

- root_cause: "`teaching-design-renderer.js` 在渲染层错误复用了去掉 `H` 的总课时格式化，并对学习任务课时直接输出数字；封面标签按整段文本输出，无法让四字标签拉伸到五字标签宽度。"
- fix: "用 `hourLabel()` 保留/补齐 `H`；封面 `计划总课时` 和学习任务分析 `课时` 都走该格式化；新增 `coverLabelCell()` 输出逐字 grid，使四字/五字标签共享 `cover-label-width` 并对齐冒号。"
- verification: "`node --check skills/teaching-design-package/scripts/teaching-design-renderer.js`; `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh`; `skills/teaching-design-package/scripts/teaching-design-package.sh example --output /private/tmp/tdpkg-cover-hours-verify.31868/package.md`; `skills/teaching-design-package/scripts/teaching-design-package.sh render-package --pdf --input /private/tmp/tdpkg-cover-hours-verify.31868/package.md --out-dir /private/tmp/tdpkg-cover-hours-verify.31868/out`; `rg` hidden Typst for `160H`, `40H`, `60H`, cover label grids; PyMuPDF rendered PDF first page to `/private/tmp/tdpkg-cover-hours-cover-page.png`; `git diff --check`; `git diff --name-only -- skills/jiaoan-shicao`."
- files_changed: "`skills/teaching-design-package/scripts/teaching-design-renderer.js`; `.planning/debug/resolved/teaching-design-cover-hours.md`."
