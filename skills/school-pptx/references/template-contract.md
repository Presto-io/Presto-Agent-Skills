# school-pptx Template Contract

Phase 41 defines the controlled template contract for `school-pptx`. Runtime behavior depends on `skills/school-pptx/templates/standard-school.pptx` and `skills/school-pptx/templates/standard-school.manifest.yaml`; the supplied `test/学院PPT模板.potx` is visual source evidence only.

## Controlled Theme

- Theme id: `standard-school`
- Available themes: `standard-school`
- Runtime template: `standard-school.pptx`
- Manifest: `standard-school.manifest.yaml`
- Runtime template seed contract: 26 reviewed seventh-version slides and 26 notes relationships; bootstrap removes all seed slides before emission.
- 第七版人工母版只保留 8 个 physical slide layouts；11 个 semantic layout ids 可复用同一个 physical layout，由 manifest geometry 和 renderer-owned native shapes 区分。

Unknown theme validation must fail non-zero and print the available controlled theme id.

## Cover Subtitle Descriptor

The `cover.subtitle` slot owns a strict `max_chars: 96`, `max_lines: 3` display budget and renders as a centered three-line information bar: line one is the authored YAML `subtitle`; line two joins `school` and `department`; line three joins `course`, `author`, and `date`. Empty groups are omitted without introducing blank placeholder lines. The `program` and `presenter` fields never enter this slot. A complete descriptor that exceeds either limit fails with `COVER_METADATA_OVERFLOW`; the renderer does not truncate characters or silently drop fields.

## Layouts

The manifest covers exactly these 11 semantic layout ids, mapped onto 8 physical PPTX layouts:

1. `cover`
2. `contents`
3. `section`
4. `title-content`
5. `two-column`
6. `image-text`
7. `table`
8. `timeline`
9. `gallery`
10. `code`
11. `closing`

Each layout points to an inspectable PPTX slide-layout XML file. Content layouts define semantic slots, but masters and layouts intentionally contain no content placeholders. The renderer creates native editable objects from manifest-owned geometry. The `closing` layout is a fixed template-owned page with no Markdown-controllable `title` or `subtitle` slot and is appended automatically at the end of every deck. Slot ids are stable public identifiers such as `title`, `subtitle`, `body`, `media`, `caption`, `left_body`, `right_body`, `table`, `timeline_items`, `gallery_items`, and `code`.

## Manifest Schema

Top-level fields:

- `theme_id`
- `available_themes`
- `template`
- `ownership`
- `required_layouts`
- `layouts`

Each layout includes:

- `label`
- `purpose`
- `pptx_layout`
- `required_slots`
- `slots`

Fixed template-owned layouts may also include `fixed_template_page: true`, `default_insertion: end_of_deck`, and `markdown_controllable: false`. In Phase 41 this applies to `closing`, which is a dead/fixed final page rather than a Markdown-authored slide.

Each slot includes:

- `id`
- `purpose`
- `kind`
- `placeholder`
- `geometry`
- `text_budget`
- `empty_slot`
- `continuation`

Phase 43 的动态可编辑对象仍由 manifest 拥有视觉事实：

- `table.table.subregions.table_name` 定义表名文本框的 geometry、text budget 和 `empty_slot: preserve`；即使没有表名，也创建无提示文字的空编辑槽。
- `table` 绑定 `标题和内容` layout；`table_style` 定义蓝色表头/表体和文字颜色，renderer 固定所有 cell 水平、垂直居中。
- `gallery.gallery_items.item_presets` 分别定义 1、2、3、4 项时每张 card、picture 和 caption 的 geometry；每张图片和图注形成一个原生可编辑组。
- `timeline.timeline_items.subregions` 定义 axis 与 node band；axis gradient 从 `accent6` 绿到 `accent1` 蓝，`node_template` 定义 marker、time、title 和 description 的节点本地子区域、对齐和文字预算。
- `inline_styles.highlight.scheme_color` 只允许引用 PowerPoint theme scheme token；普通高亮 run 必须同时使用该主题蓝色背景、`FFFFFF` 白色字体和粗体。白字是高亮文字的受控前景色，不把主题高亮背景降级为任意 RGB。

这些动态文本框和组合对象不要求修改二进制模板中的占位符。它们必须从 manifest 子区域创建，不能在发射器中复制坐标、字号范围或颜色。空 caption 和空 table name 在放映时不显示提示文字，但仍保留为可选择、可编辑的对象。

Geometry is stored in EMU units. `template-report` compares manifest geometry against PPTX XML with the manifest tolerance, currently `2000` EMU, so normal Office serialization noise does not fail validation.

## Template-Owned Guardrails

Markdown cannot override geometry, fonts, colors, decorative assets, footer behavior, or bounded text behavior. Markdown in later phases may provide semantic slide content only; it must not expose coordinates, font families, theme colors, decorative assets, footer placement, crop behavior, or arbitrary frame sizing.

Text slots use fixed frame geometry with bounded elastic text behavior. A renderer may shrink text only within the slot's `font_size_min` and `font_size_max` range and must obey the slot's `overflow` policy.

`closing` 必须通过 OOXML part path `ppt/slideLayouts/slideLayout8.xml` 解析实际结束页布局，不能使用 cover layout、布局显示名或数字索引猜测。

人工修订基准冻结了以下模板视觉角色：封面标题/副标题为 60/20pt，章节标题为 66pt 且左下对齐，普通横排内容页顶部标题为两端对齐 48pt，时间线页标题和节点 time/title 居中、description 左对齐，竖排代码标题为左对齐 48pt，标题正文页普通正文为 28pt、密集列表页为 26pt；目录使用独立 `目录` layout 且正文垂直居中，正文、表格、时间线和 gallery 使用受控内容区域；图文图片、table body、timeline axis/node band 与 gallery presets 均由 manifest 明确拥有几何。

## Phase 41 Scope Fence

Phase 41 validates manifest completeness and structural consistency. It does not implement Markdown syntax, no Markdown-to-PPTX renderer, no logical-to-physical pagination, no speaker notes rendering, and no final runtime adapter documentation.

Manual template editing rules live in [template-editing.md](template-editing.md). After any manual PPTX edit, run:

```bash
skills/school-pptx/scripts/school-pptx.sh template-report \
  --theme standard-school \
  --out-md build/school-pptx/.school-pptx/template-report.md \
  --out-json build/school-pptx/.school-pptx/template-report.json
```
