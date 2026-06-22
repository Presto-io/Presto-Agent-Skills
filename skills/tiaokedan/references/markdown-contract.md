# 调课单 Markdown Contract

本文件定义 `tiaokedan` 技能本地的 Markdown 契约，供 renderer 读取并生成 Typst/PDF。

## Fixture Path

接受的教师可读 Markdown fixture 位于：

`skills/tiaokedan/templates/tiaokedan.md`

## Contract Shape

`调课单` Markdown 使用 `YAML frontmatter + body`。frontmatter 保存教师可直接复核的必要文档事实，body 保存可见说明文字和调课明细表。

这份 Markdown 必须能直接被教师打开、复制、审阅和修改；不能依赖生成 JSON、隐藏脚本、兄弟技能目录或 Typst 源文件才能理解。

## Frontmatter Fields

| Field | Required | Owner | Meaning |
|-------|----------|-------|---------|
| `title` | no | renderer default | 文档标题。省略时 renderer 使用 `调课说明`。 |
| `recipient` | no | renderer default | 收文对象行。省略时 renderer 使用 `教务处：`。 |
| `department` | yes | teacher | 落款部门，当前接受值为 `电气工程系`。 |
| `date` | yes | teacher | 落款日期，可写 `2026年6月21日`、`2026-06-21` 或 `20260621`。 |

当前契约不使用 `status` 或 `review_notes`。如需草稿状态，应保持为教师可读事实，而不是 renderer 配置。

## Body Sections

body 可以包含 `## 调课说明` 标题，也可以直接从说明段落开始。说明段落是教师维护的表单事实，不是 renderer-owned defaults。

如果正文第一行是 `recipient`，renderer 会校验它与 frontmatter/default recipient 一致；如果省略，renderer 使用默认收文对象。

说明段落当前接受文本为：

`因我系专职教师周老师需要去企业调研，故需将其3月11日所承担实习课程调整为早班，同时涉及到孙老师老师，具体调整如下：`

落款事实可以以可见 Markdown 文本保存在表格后，也可以只保存在 frontmatter 中。两处都出现时必须一致：

- `电气工程系`
- `2026年6月21日`

## Adjustment Table Columns

调课明细使用普通 Markdown table。推荐教师维护 7 列表格，由 renderer 自动生成 `序号`：

| 班级 | 课程 | 原上课时间 | 原授课教师 | 调整后上课时间 | 调整后上课教师 | 备注 |
|------|------|------------|------------|----------------|----------------|------|

renderer 也兼容含 `序号` 的 8 列表格：

| 序号 | 班级 | 课程 | 原上课时间 | 原授课教师 | 调整后上课时间 | 调整后上课教师 | 备注 |
|------|------|------|------------|------------|----------------|----------------|------|

时间单元格可以写中文日期、紧凑日期或 ISO 日期。renderer 会把 `20260311 14:00-19:00（D104）` 规范为 `2026年3月11日 14:00-19:00（D104）`。需要保留教师可见换行时，可以使用 `<br>`。

## Required And Optional Facts

Required teacher-maintained facts:

- 说明段落文本
- 表格中每一行的 `班级`
- 表格中每一行的 `课程`
- 表格中每一行的 `原上课时间`
- 表格中每一行的 `原授课教师`
- 表格中每一行的 `调整后上课时间`
- 表格中每一行的 `调整后上课教师`
- `department`
- `date`

Optional teacher-maintained facts:

- `title` 可省略，renderer 默认 `调课说明`。
- `recipient` 可省略，renderer 默认 `教务处：`。
- `序号` 列可省略，renderer 按表格行序自动生成。
- 表格后的落款部门和日期可省略，renderer 使用 frontmatter 中的 `department` 和 `date`。
- `备注` 可按行留空，前提是接受表单事实本身确实为空。空备注不是缺失必填项。

## Unknown-Value Markers

必填事实未知时，必须在缺失位置附近使用可见内联标记：

`{{待补充: 说明}}`

示例：

`{{待补充: 原上课地点}}`

AI 起草但需要教师确认的可编辑文字可以使用：

`{{AI草稿: 说明}}`

接受 fixture 应优先使用 Phase 37 已锁定的具体事实，不为了演示而替换成 review marker。后续最终渲染必须把未解决的 `{{待补充: ...}}` 视为 non-final；Phase 39 将实现非零 validation failure。

## Renderer-Owned Defaults

以下属于 renderer-owned defaults，教师不需要也不应该在 Markdown 中维护：

- A4 landscape page setup
- default page margins
- font fallback lists
- title font family and weight
- point sizes
- table column width ratios
- cell padding
- strokes
- vertical spacing
- right-side signature block width
- Typst helper names
- generated Typst paths
- PDF compile commands
- comparison evidence
- debug diagnostics

`tiaokedan.md` 不得包含 raw Typst、CSS-like layout knobs、字体 fallback 列表、页面尺寸、表格宽度配置、PDF 命令或调试诊断字段。

## Phase 38 non-goals

Phase 38 明确不做：

- no renderer/parser/CLI/scripts
- no generated Typst
- no PDF workflow
- no canonical `skills/tiaokedan/SKILL.md`
- no runtime adapter notes
- no README/index/discoverability updates
- no approval grids
- no signature boxes
- no opinion columns
- no school-specific variants
- no batch generation
- no spreadsheet import
