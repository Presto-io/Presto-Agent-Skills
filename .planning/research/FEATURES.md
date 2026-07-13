# Feature Landscape: school-pptx

**Domain:** 学校固定模板 Markdown-to-PPTX 技能  
**Researched:** 2026-07-13  
**Overall confidence:** HIGH for project-scoped feature boundary; MEDIUM for PPTX implementation difficulty until renderer spike验证。  

## Research Basis

本研究基于当前 v1.17 `school-pptx` 里程碑边界、项目级 Markdown-first 技能约定、`school-presentation` 既有逻辑页经验，以及用户已确认的字段和版式范围。`school-presentation` 只作为 Markdown-first、逻辑页拆物理页、固定画布和验证经验来源；不能把它的 HTML 输出、playback、overview、课堂交互或单文件离线模型迁移为 `school-pptx` 的输出方案。

## Table Stakes

缺少这些功能时，`school-pptx` 会不像一个可交付的学校 PPTX 技能。

| Feature | Why Expected | Complexity | First Version | Notes |
|---------|--------------|------------|---------------|-------|
| `school-pptx` canonical skill entry | 仓库所有真实技能都需要可触发、可安装、可被多 runtime 读取的 `SKILL.md` | Low | Must | `description` 说明“什么时候使用”，不要写营销句；OpenClaw 与 Hermes Agent 必须出现在 adapter notes。 |
| Markdown-first 工作流 | 本仓库文档技能的稳定模式是先产出可审阅 Markdown，再进入最终渲染 | Med | Must | 用户交互应先整理/确认 `school-pptx-full.md`，脚本只消费已定稿 Markdown。 |
| YAML formatter 字段 | 用户需要通过顶层元数据表达学校、课程和作者等封面/模板信息 | Low | Must | 字段固定为 `title/subtitle/school/department/program/course/author/presenter/date/theme`；未知值不得虚构。 |
| 受控 `theme` | 固定学校模板需要机器可映射的主题标识 | Med | Must | 第一版应只接受已登记的模板标识；未知 theme 硬失败或明确要求用户选择。 |
| 显式 slide block | PPTX 版式需要可解析、可验证的布局选择 | Med | Must | 使用 `::: slide {layout="..."}`；不要靠标题文本或 Markdown 形状猜 layout。 |
| 支持 11 个固定 layout | 已确认范围要求覆盖学校汇报常见页面类型 | High | Must | `cover/contents/section/title-content/two-column/image-text/table/timeline/gallery/code/closing` 必须全部可生成示例。 |
| 封面 slot 固定行为 | 学校模板封面元素不能因缺字段发生漂移 | Med | Must | 缺失封面信息时留空或显示待补标记，不移动其他元素，不重排 logo/标题/装饰。 |
| 自动目录页 | 学校课件通常要求目录；用户已确认从所有 `##` 生成 | Med | Must | `#` 只作为文档标题 fallback；所有 `##` 进入 contents，顺序等于 Markdown 顺序。 |
| 逻辑页自动扩展为物理页 | Markdown 逻辑页应易写，超量内容由 renderer 分页 | High | Must | 文本、表格、timeline、gallery 超出预算时拆页；不能用缩到不可读字体来硬塞。 |
| 可编辑 PPTX 对象 | `school-pptx` 的核心价值是 PowerPoint 可继续编辑 | High | Must | 文本、表格、图片、代码、timeline 基本形状应是 PPTX 对象，不用整页截图冒充。 |
| 图片等比 contain 放置 | 既有学校 presentation 经验和当前项目 out-of-scope 均反对裁切用户图片 | Med | Must | image-text、gallery 等版式默认保留原始比例，允许留白，不做 fill crop。 |
| Gallery 每页 4 图 | 用户已确认固定行为 | Med | Must | 多于 4 张自动生成后续物理页；每页维持同一四宫格 slot。 |
| Timeline 横向布局 | 用户已确认固定行为 | High | Must | 长 timeline 自动分页或分段，不改成纵向列表。 |
| Table 可编辑和可分页 | 学校课件常见表格需要后续人工微调 | High | Must | 表格使用 PPTX table 或等价可编辑 shape；超长表分物理页，表头可重复。 |
| Code 可编辑、无高亮 | 第一版不追求高亮，但代码必须能在 PowerPoint 里改 | Med | Must | 使用等宽文本框；保留缩进；不要渲染为图片。 |
| Speaker notes | PPTX 常见演讲稿需求，且当前里程碑目标包含 speaker notes | Med | Must | Markdown 中应有稳定 notes 语法或约定；写入 PPTX notes，不出现在画面正文。 |
| 最小转场策略 | 用户已确认 0.5s 平滑可做则做，否则无动画 | Med | Must | 转场不应成为失败原因；不稳定时输出无动画 PPTX 并在 manifest/验证说明中记录。 |
| 重复可验证输出 | 既有 GSD 里程碑强调黑盒真值命令和证据矩阵 | Med | Must | 需要 example/render/verify 之类命令，验证 slide count、layout、notes、media、table、pagination、非空 PPTX。 |

## Differentiators

这些功能不是泛用 Markdown-to-PPTX 的最低要求，但会让该技能真正贴合“学校固定模板”。

| Feature | Value Proposition | Complexity | First Version | Notes |
|---------|-------------------|------------|---------------|-------|
| 从 `.potx` 视觉样例手工归一化为标准 PPTX 模板 | 降低脚本直接读人类模板时的不可控性 | High | Must | 先建立机器可映射 slot、placeholder、layout 名称和尺寸预算，再自动化。 |
| 固定 frame geometry | 学校模板一致性优先于 Markdown 自由排版 | High | Must | 每个 layout 有固定坐标、字体层级、图片槽和安全边距；Markdown 不暴露坐标。 |
| 有界弹性文本策略 | 内容稍多时还能稳，但不会无限缩小 | High | Must | 字号只在可读范围内变化；超出则拆物理页。 |
| 逻辑页到物理页映射 manifest | 让用户知道一页 Markdown 被拆成了哪些 PPTX 页 | Med | Must | 验证和后续调试都依赖该映射。 |
| 缺失信息就近可见 | 防止 agent 虚构学校/作者/日期 | Low | Must | Markdown review 阶段使用待补标记；最终 render 对关键缺失项应报错或保留空 slot，取决于字段性质。 |
| 模板一致性优先的 layout fallback | 用户写得不完美时也能得到可控输出 | Med | Should | 例如普通正文可进入 `title-content`，但未知 layout 不应猜成任意样式。 |
| Markdown fixture 覆盖所有 layout | 便于 roadmap 后续拆 phase 和做黑盒测试 | Low | Must | 第一版必须有一个 hand-authored 全功能 fixture，覆盖 11 个 layout、notes、media、分页。 |
| PowerPoint 可人工二次编辑 | 学校用户通常需要最终微调 | High | Must | 输出不能依赖 HTML、浏览器或运行时 JS 才呈现核心内容。 |
| 可解释的降级报告 | PPTX 能力不稳定时，用户要知道哪里降级 | Med | Should | 转场、代码高亮、复杂表格等降级写入 manifest 或控制台摘要。 |

## Anti-Features

这些功能会破坏第一版边界，应该明确不做。

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| 把 `school-presentation` HTML 渲染方案当 PPTX 输出方案 | v1.17 是新的 editable PPTX 技能线；HTML playback/export 不是 PowerPoint 可编辑对象 | 只借鉴 Markdown-first、逻辑页拆物理页和验证经验，另建 PPTX renderer。 |
| 整页截图式 PPTX | 会丢失可编辑性，违背 `school-pptx` 核心目标 | 使用 PPTX 文本框、表格、图片和形状对象；只有不可避免的小装饰可来自模板。 |
| Markdown 控制坐标/字体/颜色 | 会把固定学校模板变成自由排版系统，导致难验证 | 坐标、字体、颜色由 theme/template/layout slots 管理。 |
| 泛化支持任意 PPT 模板市场 | 模板差异太大，会拖垮第一版验证 | 只支持从已确认 `.potx` 样例归一化出的标准模板。 |
| 复杂对象动画 | 不稳定且不利于跨 PowerPoint/WPS/Keynote 兼容 | 第一版只支持无动画；0.5s 平滑切页能稳定生成/保留时再启用。 |
| 强加页脚 | 用户已确认不强加页脚；学校模板可能没有固定 footer | 只使用模板本身已有元素；必要信息由 layout slots 或 notes 承载。 |
| 自动裁切图片填满装饰框 | 会损坏教学图片、证书、截图等内容语义 | 默认 contain 等比缩放；如未来需要裁切，必须另设显式受控选项。 |
| 代码高亮作为第一版硬要求 | PPTX 中稳定、可编辑的 token 高亮会显著增加复杂度 | 第一版输出可编辑等宽代码块；高亮延后。 |
| 自动 OCR/旧 PPT 深度解析 | 会把技能变成输入理解项目，而不是固定模板渲染项目 | 第一版要求用户或 agent 先整理成 Markdown。 |
| 托管分享、同步、课堂互动 | 这是 `school-presentation` HTML line 的能力，不是 PPTX 生成第一版核心 | 保持本地 Markdown-to-PPTX 输出和验证。 |

## Markdown User Experience Recommendations

### Recommended Authoring Shape

第一版 Markdown 应保持“YAML + 明确 slide blocks”的低歧义结构：

```markdown
---
title: 项目建设汇报
subtitle: 阶段成果与后续计划
school: 示例学校
department: 信息工程系
program: 电气自动化技术
course: 电气设备控制线路安装与调试
author: 张三
presenter: 李四
date: 2026-07-13
theme: standard-school
---

# 项目建设汇报

## 建设背景

::: slide {layout="title-content"}
### 建设背景

- 背景要点一
- 背景要点二

::: notes
这里写演讲提示，不进入画面。
:::
:::
```

### UX Rules

| Recommendation | User-Visible Behavior | Acceptance Point |
|----------------|-----------------------|------------------|
| 顶层 YAML 字段固定，不扩展临时字段 | 用户知道哪些元数据会影响模板 | 示例 Markdown 只出现已确认 10 个字段；未知字段要么忽略并警告，要么验证失败。 |
| `#` 只作为文档标题 fallback | 不把文档标题误放入目录 | 有 `#` 和多个 `##` 的 fixture 中，contents 只含 `##`。 |
| `##` 是目录来源，不等于必须产生 section slide | 用户可以用 `##` 表达结构，而 slide block 表达页面 | contents 顺序匹配所有 `##`；section slide 由显式 `layout="section"` 控制。 |
| 每个 slide block 必须有 layout | 减少 renderer 猜测 | 缺 layout 的 block 在验证阶段报清晰错误，或由 authoring helper 补成 `title-content` 并标记。 |
| 缺失字段不导致视觉漂移 | 用户看到的是固定模板缺项，而不是整页重排 | 删除 subtitle/department 等字段后，封面其他元素坐标不变。 |
| 长内容由 renderer 拆页 | 用户不用手动平衡每页字数 | 生成 manifest 显示 logical slide -> physical slides；物理页可读。 |
| 图片路径相对 Markdown 文件解析 | 教师材料目录可整体移动 | fixture 使用相对图片路径并成功渲染。 |
| notes 与正文分离 | 演讲提示不会污染画面 | PowerPoint notes pane 有内容，slide canvas 无 notes 文本。 |
| 错误信息贴近 Markdown 行号或 slide 标识 | 用户能快速改源文件 | 无效 layout、缺图片、表格过宽等错误报告包含 slide heading/block index。 |

## First-Version Must Do

第一版必须交付以下功能，否则后续路线会缺少可验证地基：

| Capability | Required Behavior | Verification |
|------------|-------------------|--------------|
| 标准模板归一化 | 从提供的 `.potx` 视觉样例建立 skill-local 标准 PPTX 模板和 layout slot contract | 模板文件、slot 说明、layout 名称一致；脚本不直接依赖人类视觉猜测。 |
| 全 layout fixture | 一个 Markdown fixture 覆盖 YAML、11 个 layout、notes、图片、表格、timeline、gallery、code、分页 | `example` 或模板命令能生成该 fixture。 |
| Markdown parser/validator | 解析 YAML 和 slide blocks，验证字段、layout、media、表格、notes | 无效输入非零退出；错误信息可定位。 |
| PPTX renderer | 输出非空 `.pptx`，核心内容为可编辑 PPTX 对象 | 打开后文本/表格/代码可编辑；自动检查 ZIP structure 和 slide XML。 |
| 目录生成 | 从全部 `##` 自动生成 contents slide | fixture 目录项数量和文本可被验证。 |
| 逻辑页分页 | 文本、gallery、table、timeline 超预算时拆为多张物理页 | manifest 和 slide count 匹配预期。 |
| Gallery 4 图/页 | 图片超过 4 张时自动新增物理页 | 5 图 fixture 输出 2 张 gallery 物理页。 |
| 横向 timeline | timeline 使用横向排布，长 timeline 分页/分段 | 生成的 timeline 不是纵向列表。 |
| 封面缺项稳定 | 缺少非关键封面字段时 slot 留空，其他元素不移动 | 对比完整/缺项封面关键坐标一致。 |
| 无页脚强加 | 不向每页插入模板外 footer | Slide XML/截图检查没有新增统一页脚文本。 |
| 代码可编辑无高亮 | 保留缩进和等宽风格，允许无 syntax highlight | PowerPoint 中可编辑代码文本。 |
| 转场降级 | 能稳定生成 0.5s 平滑则启用，否则无动画且不失败 | 验证报告记录 transition mode。 |

## Can Degrade or Defer

这些功能可以降级或放到后续阶段，不应阻塞第一版。

| Capability | First-Version Degradation | Defer Until |
|------------|---------------------------|-------------|
| 代码语法高亮 | 等宽可编辑文本框，无 token 颜色 | PPTX rich text run 生成稳定且可验证后。 |
| 复杂对象动画 | 无动画；只保留稳定 slide transition | 有跨 PowerPoint/WPS 兼容验证后。 |
| 任意模板导入 | 只支持已归一化标准模板 | 多模板 slot contract 稳定后。 |
| 智能图表/SmartArt | 用固定形状和文字表达 timeline/gallery/table | 需要真实用户样例证明价值后。 |
| 自动内容改写 | agent 可在 Markdown 草稿阶段辅助整理，但 renderer 不改写语义 | 技能交互层另行规划。 |
| 高级表格样式 | 可编辑基础表格，必要时分页 | 官方模板表格视觉规则稳定后。 |
| 图片裁切/焦点控制 | contain 放置，留白可接受 | 明确设计需求和非破坏性语法出现后。 |
| PPTX 到 PDF/图片导出 | 第一版只保证 PPTX | 本机 office/libreoffice 导出链路稳定后。 |
| 课堂播放控件 | 不做 | 仍由 `school-presentation` HTML line 承担。 |

## Feature Dependencies

```text
标准 PPTX 模板归一化 -> layout slot contract -> Markdown fixture -> parser/validator -> renderer -> verification
YAML formatter -> cover/contents metadata behavior -> missing-field validation
## heading collection -> contents slide generation -> contents verification
slide block parser -> layout mapping -> pagination budgets -> logical-to-physical manifest
media path resolver -> image-text/gallery rendering -> gallery 4-per-page verification
table parser -> editable PPTX table renderer -> table pagination verification
notes parser -> PPTX notes writer -> notes verification
transition capability spike -> transition mode decision -> verification report
```

## MVP Recommendation

优先做：

1. 标准模板归一化和 slot contract：没有这个，所有布局和验证都会漂移。
2. Markdown contract 与全 layout fixture：先锁用户可见输入体验，再写 renderer。
3. Renderer 的可编辑对象最小集：文本、图片、表格、timeline、gallery、code、notes。
4. 自动目录和逻辑页分页：这是用户已确认且最影响使用体验的行为。
5. 黑盒验证命令：验证 slide count、layout mapping、目录、notes、media、分页、非空 PPTX、无整页截图捷径。

延后：

- 代码高亮：先保证可编辑和缩进稳定。
- 复杂动画：先选择无动画或稳定 0.5s slide transition。
- 任意模板导入：第一版只围绕一个标准学校模板。
- PPTX 导出 PDF：除非后续阶段明确把 PDF 当验收条件。

## Acceptance Checklist

| Area | Acceptance Point |
|------|------------------|
| Skill boundary | `school-pptx` 是新技能；不修改 `school-presentation` 的 HTML 输出定位。 |
| Markdown | 示例文件包含固定 YAML 字段和显式 `::: slide {layout="..."}`；没有坐标、字体、颜色控制。 |
| Layout coverage | 11 个 layout 都有 fixture、渲染结果和验证断言。 |
| Contents | contents slide 从所有 `##` 生成；`#` 只作标题 fallback。 |
| Pagination | 至少覆盖长正文、长表格、5 图 gallery、长 timeline 的逻辑页拆分。 |
| Editability | 生成 PPTX 中正文、表格、代码、timeline 文本可编辑；不使用整页截图。 |
| Cover stability | 删除可选封面字段不会移动其他封面元素。 |
| Footer | 没有 renderer 强加的全局页脚。 |
| Images | 图片 contain 放置，不裁切；缺图报错可定位。 |
| Code | 代码块可编辑、保留缩进；无高亮不算失败。 |
| Transition | 记录 transition mode；不稳定时无动画通过。 |
| Verification | `verify` 能在临时目录重复生成并检查 slide count、layout map、manifest、PPTX 非空、media、notes、分页。 |

## Sources

- `.planning/PROJECT.md` - v1.17 目标、确认范围、out-of-scope 和项目历史。Confidence: HIGH.
- `.planning/STATE.md` - 当前 GSD 状态、历史决策、Markdown-first 与 school-presentation 经验。Confidence: HIGH.
- `.planning/ROADMAP.md` - 当前路线状态和历史 phase 边界。Confidence: HIGH.
- `AGENTS.md` - 仓库编辑规则、skill authoring rules、runtime adapter 要求。Confidence: HIGH.
- `skills/school-presentation/SKILL.md` - Markdown-first presentation 经验和必须避免迁移的 HTML 输出边界。Confidence: HIGH.
- User-provided v1.17 confirmed scope in this research request. Confidence: HIGH.

## Open Questions for Later Phases

- PPTX 渲染库的选择、版本、notes 写入和转场 XML 支持需要在 STACK/ARCHITECTURE 或实现 spike 中验证。
- `.potx` 到标准 PPTX 模板的归一化方式需要拿到真实样例后决定，是手工改母版/布局还是生成一个受控 `.pptx` seed。
- 表格分页预算、中文字体 fallback、WPS/PowerPoint 兼容性需要真实输出验证，不宜只靠静态 XML 判断。
