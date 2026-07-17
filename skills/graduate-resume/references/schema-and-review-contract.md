# Graduate Resume Schema And Review Contract

本文档定义 `graduate-resume` 在 Phase 46 的基础资料契约。目标是把主题、定向、照片布局和最终渲染之前的“真实资料层”单独稳定下来。

## Top-Level Sections

- `candidate`: 候选人基本信息、求职方向、联系方式和摘要。
- `education`: 学历、院校、专业、时间、核心课程。
- `skills`: 技能分组、工具、设备、软件、语言能力。
- `certificates`: 证书、职业资格、培训结业。
- `projects`: 项目经历与成果。
- `training`: 实训、实习、校内综合实践。
- `experience`: 兼职、社团、竞赛组织、相关工作经历。
- `targets`: 一个或多个单位/岗位/招聘信息。
- `photo`: 照片状态与本地路径。
- `preferences`: 页数、主题、照片模式等非事实偏好。

## Stable ID Rules

- 所有可复用条目都必须带稳定 `id`。
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

字段建议：

- `photo.status`
- `photo.path`
- `photo.confirmed_by_user`
- `photo.note`

`photo.status` 在 Phase 46 支持：

- `provided`: 已提供本地照片，可供后续照片版布局消费。
- `pending`: 尚未提供，且用户还没有明确说没有。
- `declined`: 用户明确说没有照片或选择无照片版。

约束：

- 默认期待提供照片。
- 没有照片时先追问一次。
- 只有用户明确说没有后，才能写 `declined`。
- `provided` 必须指向本地路径；远程 URL 不能直接视为最终受信输入。

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
- 照片既未提供也未明确 `declined`。
- 最终定向前的 target 缺少 `source`、`as_of` 或 `confirmed`。

当前实现补充：

- `validate` 输出 JSON 摘要；失败时返回稳定错误码 `VALIDATION_FAILED`。
- `target` 只做已核实 target brief 的归一化摘要，不抓取或推断招聘信息。
- `plan` 只输出 Phase 46 baseline plan 和依赖/字体策略占位，不负责分页和主题布局。

## One-Time Question Policy

- 缺 target：问一次，用户明确不提供后继续通用版。
- 缺照片：问一次，用户明确没有后继续无照片版。
- 缺核心事实：只问一次当前缺项，不重复追问同一问题。

## Out Of Scope In Phase 46

- 主题字体、页面几何、照片裁切和双页分页。
- AI 自动生成正式自我评价或项目成果。
- 招聘网站抓取、OCR、远程照片下载。
- 最终 Markdown/Typst/PDF bundle 事务发布。
