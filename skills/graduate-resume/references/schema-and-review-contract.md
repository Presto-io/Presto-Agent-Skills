# Graduate Resume Schema And Review Contract

本文档定义 `graduate-resume` 的基础资料契约。目标是把主题、定向、照片布局和最终渲染之前的“真实资料层”单独稳定下来，并让事实源保持可读、可审阅。

## Document Shape

`graduate-resume.md` 是唯一可编辑事实源，但不再把所有内容塞入 YAML。

- YAML frontmatter 只允许 `schema`、`profile`、可选 `photo` 和 `preferences`。
- `profile` 承担首页信息栏的姓名、状态、求职标题、概述、联系方式和求职方向。
- `photo` 存在时值为学生明确提供的本地照片路径；字段不存在即为无照片。
- `preferences` 只表达主题、页数和照片模式等派生偏好，不是事实。
- Markdown 正文承载教育、技能、证书、项目、实训、经历和目标；标题保留模块语义。
- 可复用正文条目的标题下使用 `<!-- resume: id=... status=... -->` 保存稳定 ID 与复核状态；target 仍以 `confirmed` 表达确认状态。

正文可按可读性书写或调整顺序。后续 `fact-block` / `list-entry` 容器由渲染器从模块语义派生，条目出现的位置、主题、页数和照片槽位都不是新的事实，也不能反向改写资料源。

## Top-Level Sections

- `candidate`（YAML 中的 `profile`）：候选人基本信息、求职方向、联系方式和摘要。
- `education`: 学历、院校、专业、时间、核心课程。
- `skills`: 技能分组、工具、设备、软件、语言能力。
- `certificates`: 证书、职业资格、培训结业。
- `projects`: 项目经历与成果。
- `training`: 实训、实习、校内综合实践。
- `experience`: 兼职、社团、竞赛组织、相关工作经历。
- `targets`: 一个或多个单位/岗位/招聘信息。
- `photo`（YAML 可选字段）：学生明确提供的本地照片路径；字段不存在表示无照片。
- `preferences`: 页数、主题、照片模式等非事实偏好。

## Stable ID Rules

- 所有可复用条目都必须带稳定 `id`；正文中写在紧邻条目标题的 `resume` 注释里。
- `projects`、`training`、`experience`、`certificates` 和需要单独引用的技能组不能只靠标题辨识。
- `id` 一旦进入审阅与后续生成流程，就不应因主题或 target 变化而重写。

推荐格式：

- `edu-001`
- `skill-automation`
- `cert-electrician-001`
- `project-plc-001`
- `training-substation-001`
- `exp-campus-001`
- `target-grid-001`

## Review Status

Phase 46 统一使用以下状态表达复核结果：

- `verified`: 已由用户确认，可进入后续 final render。
- `pending`: 仍待确认，只能停留在草稿或被 `validate` 拒绝。
- `declined`: 用户明确表示不存在、不提供或不适用。

## Photo Contract

照片是独立资料项，不是布局选项。

字段格式：`photo: sources/student-photo.jpg`。`photo` 不存在时不创建照片区域；远程 URL、空字符串或对象均不是受信输入。

## Target Contract

`targets` 只表达用户提供的岗位事实，不允许技能抓取、猜测或声称实时。

每个 target 建议至少包含：

- `id`
- `company`
- `role`
- `source`
- `as_of`
- `confirmed`
- `requirements`

其中：

- `source` 记录来源，例如招聘公告、聊天转述、老师推荐信息。
- `as_of` 记录用户确认该信息对应的日期。
- `confirmed` 表示用户是否确认这份 target brief 可用于本次定向。

## Validation Gates

以下情况在 Phase 46 应直接阻断 `validate` 通过：

- 出现未知字段。
- 出现重复事实 ID。
- 缺失必填核心资料。
- 核心事实仍为 `pending`。
- `photo` 存在但不是非空本地路径。
- 最终定向前的 target 缺少 `source`、`as_of` 或 `confirmed`。

当前实现补充：

- `validate` 输出 JSON 摘要；失败时返回稳定错误码 `VALIDATION_FAILED`。
- `target` 只做已核实 target brief 的归一化摘要，不抓取或推断招聘信息。
- `plan` 只输出 Phase 46 baseline plan 和依赖/字体策略占位，不负责分页和主题布局。

## One-Time Question Policy

- 缺 target：问一次，用户明确不提供后继续通用版。
- 照片可选：问一次，用户没有照片后省略 `photo` 字段并继续无照片版。
- 缺核心事实：只问一次当前缺项，不重复追问同一问题。

## Out Of Scope In Phase 46

- 主题字体、页面几何、照片裁切和双页分页。
- AI 自动生成正式自我评价或项目成果。
- 招聘网站抓取、OCR、远程照片下载。
- 最终 Markdown/Typst/PDF bundle 事务发布。
