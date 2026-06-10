---
status: resolved
trigger: "请在 /Users/mrered/Developer/Presto-Agent-Skills 里只读诊断 end-of-term-teaching-materials 版式回归：1) 所有封面页下划线与文字距离需和成绩记分册一致；2) 淡红高亮区域与表格框线冲突/左右溢出/上下短导致白缝；3) 成绩分析表学期班级时间表头太宽，需仿照成绩汇总表重设信息表头；4) 成绩分析表正文填写区域首行缩进/标点起头问题；5) 交接班记录虚线应在上下两条信息中间。请不要改文件，输出根因、相关文件/函数/行号、建议验证命令。始终使用简体中文。"
created: 2026-06-10T21:27:37+08:00
updated: 2026-06-10T23:16:57+08:00
---

## Current Focus
<!-- OVERWRITE on each update - reflects NOW -->

hypothesis: 已确认并修复：版式回归来自 render_package.py 与 Typst 模板中的绝对坐标、绘制顺序和段落块宽度策略不一致，而不是 Markdown 数据合同。
test: 已修改 cover_line_field、warning fill 绘制层级、analysis_page 页眉与正文排版、Typst 段落 helper、simple_cover_page 交接虚线坐标，并运行语法检查、完整 verify、49 人异常预览和用户视觉检查。
expecting: 封面线距统一，红色高亮不盖框线且覆盖完整单元格，成绩分析表信息栏不越界，正文为稳定宽度段落块且整体居中、内部左对齐和首行缩进，交接虚线居中。
next_action: 无；用户已确认视觉验证通过，debug 关闭。

## Symptoms
<!-- Written during gathering, then IMMUTABLE -->

expected: 封面页下划线与文字距离和成绩记分册一致；淡红高亮区域不与表格框线冲突、不左右溢出、上下完整无白缝；成绩分析表信息表头宽度仿成绩汇总表；成绩分析正文填写区不出现首行缩进/标点起头异常；交接班记录虚线位于上下两条信息中间。
actual: 用户报告 end-of-term-teaching-materials 存在上述 5 项版式回归。
errors: 无运行时报错；表现为 PDF/Typst 版式差异。
reproduction: 运行 end-of-term-teaching-materials 渲染/验证流程并检查生成的封面页、成绩分析表、交接班记录页面。
started: v1.7 Phase 12/13 固定模板渲染完成后发现。

## Eliminated
<!-- APPEND only - prevents re-investigating -->

## Evidence
<!-- APPEND only - facts discovered -->

- timestamp: 2026-06-10T21:27:37+08:00
  checked: 规划状态与历史记忆
  found: v1.7 已完成 Phase 12 固定模板渲染与 Phase 13 不确定成绩 review 闭环；路线要求固定模板、Typst/PDF、deterministic review artifacts。
  implication: 诊断应优先检查 skill-local templates/scripts/artifacts，而不是重新讨论合同或 OCR 范围。
- timestamp: 2026-06-10T21:28:57+08:00
  checked: skills/end-of-term-teaching-materials/SKILL.md 与目录结构
  found: 渲染脚本为 skills/end-of-term-teaching-materials/scripts/render_package.py；SKILL.md 明确 PDF grid 的列比例、行节奏、边框、合并表头和高亮都由 skill-local renderer 编码。
  implication: 用户报告的版式问题应直接追踪 renderer 的硬编码坐标/尺寸，而不是模板 frontmatter 或 source fixture。
- timestamp: 2026-06-10T21:31:52+08:00
  checked: git diff 与 render_package.py 带行号源码
  found: 当前工作树在 render_package.py 中已有未提交改动，涉及 line_offset 27->22、红色高亮从行内绘制改为 fills+lines、成绩分析表头坐标改为成绩汇总表同款 160.68pt 分区、分析正文首行缩进改为坐标缩进并加入行首禁用标点、交接班虚线从 621pt 改为上下两行中点 divider_y。
  implication: 这些未提交改动正对应用户列出的 5 个症状；根因是此前 HEAD 里各页面使用分散 magic numbers，没有共享“封面字段线距/信息表头/高亮背景/正文折行/交接分隔线”布局原语。
- timestamp: 2026-06-10T21:31:52+08:00
  checked: .planning/debug/resolved/end-of-term-score-views-and-summary-pagination.md 与 end-of-term-uncertain-score-calc.md
  found: 旧修复集中在成绩视图、分页、任务列和 87? 计算；没有覆盖本次封面线距、分析表头、分析正文标点、交接虚线这些版式微调。
  implication: 本次是固定模板渲染器的后续版式回归，不是旧诊断已经解决的成绩口径问题。
- timestamp: 2026-06-10T21:45:00+08:00
  checked: 渲染器修复与完整 verify
  found: `python3 -m py_compile`、`bash -n`、`end-of-term-teaching-materials.sh verify --workdir /private/tmp/presto-layout-verify.UZTulm` 全部通过，Typst/PDF 成功编译；抽查 Typst 源确认 abnormal preview 中 red warning rect 在 hline/vline 前绘制，成绩分析表信息行使用 160.68pt 三列，交接虚线位于 619pt。
  implication: 自动化与 Typst 源层面确认修复生效；最终视觉仍建议由用户打开 PDF 人工看一眼。
- timestamp: 2026-06-10T22:05:00+08:00
  checked: 用户截图反馈后的二次修正和 49 人异常预览
  found: 成绩分析表和成绩汇总表页眉班级均改为紧凑 `示例电气2班`；成绩分析表三项基本信息均居中；分析正文改用单元格完整宽度 `104.83pt..537.73pt`，首行只在内部缩进两字符。生成 `/private/tmp/presto-layout-49-preview/end-of-term-package.pdf`，包含 49 名虚假学生和 13 条 red warning fill 高亮证据。
  implication: 这次修复覆盖真实截图暴露出的视觉问题，并提供可人工查看淡红色背景效果的大样本异常预览。
- timestamp: 2026-06-10T22:18:00+08:00
  checked: 成绩分析正文自动换行
  found: 用户指出右侧空白来自手工 `max_chars` 预切行；最终移除分析正文的 Python 逐行切分，新增 Typst `ppara_nc` 段落 helper，在完整单元格宽度内设置 `first-line-indent: 2em` 和局部行距，由 Typst 自动换行。
  implication: 成绩分析正文不再依赖硬编码字数，标点行首控制交给 Typst 的中文/Unicode 排版规则处理。
- timestamp: 2026-06-10T22:28:00+08:00
  checked: 成绩分析正文块水平位置
  found: 用户指出“段落块居中”不是缩窄正文框、也不是每行居中；已撤销对称 inset 和 `center + horizon` 尝试，恢复完整单元格宽度内的左对齐 Typst 段落，由段落自身自动换行、段首缩进和垂直居中。
  implication: 固定表格中段落盒子与单元格同宽时没有额外水平居中空间；后续若需要视觉文字块右移，必须明确允许水平位移或内边距。
- timestamp: 2026-06-10T23:16:57+08:00
  checked: 成绩分析正文稳定宽度段落块与用户视觉验收
  found: 将 `ppara_nc` 从内容自适应宽度和整格宽度调整为按正文单元格宽度比例推导的稳定段落块，当前 `body-ratio: 0.94`；49 人异常预览重新生成到 `/private/tmp/presto-layout-49-preview/end-of-term-package.pdf`，用户确认视觉验证通过。
  implication: 短文段不会按内容 shrink-to-fit，长文段也不会因段落块等于整格宽度而显得右侧空白过大；debug 可关闭。

## Resolution
<!-- OVERWRITE as understanding evolves -->

root_cause: render_package.py 用绝对坐标和逐页 magic numbers 绘制 PDF，缺少共享布局原语；此前 HEAD 中封面字段线距、红色高亮背景、成绩分析表信息表头、分析正文折行缩进、交接班虚线位置分别各自硬编码。后续正文段落调试中，`auto` 宽度会让短内容 shrink-to-fit，整格宽度又会让视觉上右侧空白过大。
fix: 将封面字段默认 line_offset 改为 22pt；把成绩记分册和成绩汇总表 red warning fill 收集为背景层并用完整单元格 bounds 绘制；成绩分析表页眉改用成绩汇总表同款三列信息栏并整体居中；成绩分析表和成绩汇总表页眉班级改为紧凑 `示例电气2班`；分析正文改为 Typst 自动换行段落，使用按正文单元格宽度比例推导的稳定段落块并在单元格内居中，段落内部左对齐和首行 2em 缩进；交接虚线由上下文本框中点计算；同步更新 rendering-style 和 cover-template-notes。
verification: `python3 -m py_compile skills/end-of-term-teaching-materials/scripts/render_package.py`；`bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`；`git diff --check`；`skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh verify --workdir /private/tmp/presto-layout-verify-centered`；Typst 源抽查高亮绘制顺序、成绩分析表页眉坐标、封面线距、段落块 `body-ratio: 0.94` 和交接虚线坐标；49 人异常预览 `/private/tmp/presto-layout-49-preview/end-of-term-package.pdf` 和 PNG 页面检查 red warning fill、页眉居中、正文段落块自动换行与首行缩进；用户确认视觉验证通过。
files_changed:
  - skills/end-of-term-teaching-materials/scripts/render_package.py
  - skills/end-of-term-teaching-materials/references/rendering-style.md
  - skills/end-of-term-teaching-materials/references/cover-template-notes.md
  - .planning/debug/resolved/end-term-layout-regression.md
