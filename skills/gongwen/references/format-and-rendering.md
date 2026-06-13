# Gongwen Format and Rendering Reference

This reference holds detailed authoring and renderer rules for the `gongwen` skill. Keep `SKILL.md` as the concise semantic entry point and update this file when long format behavior changes.

## Frontmatter

- `title`: 公文标题；如需标题中手动换行，用 `|` 标记断点。
- `author`: 发文单位；可为字符串或字符串数组。
- `date`: `YYYY-MM-DD` 格式日期。
- `signature`: 是否启用签名信息。
- `template`: 固定为 `gongwen`。

## Body Structure

- 正文使用可审阅的 Markdown 表达结构：标题、段落、有序/无序列表、表格、代码块、引用、图片和图组。
- 只有源材料明确要求顺序、步骤或编号时才使用有序列表。
- 不要为了套用模板而凭空添加项目序号、编号列或“序号/项目”字段。

## Gongwen Control Syntax

- `::: {.noindent}` 表示无首行缩进块。
- Markdown `**加粗内容**` 表示正文或标题内的行内加粗，渲染和 PDF 导出时应保留为加粗语义。
- `{.indent}`、`{.bold}` 表示局部排版属性。
- `{.br:N}` 表示插入 N 个换行。
- `{pagebreak}` 或 `{pagebreak:weak}` 表示分页。
- Markdown 表格后的 `: 表题` 表示表格题名。
- 同一段内多张图片且 alt 相同表示一组子图。

## Numbering Rules

- 不要为了“看起来规范”凭空增加项目序号、序号列、项目编号、有序列表或手写标题编号。
- 普通段落、列表、表格中的业务编号按源材料保留；本规则只归一化 Markdown 标题开头的层级序号。
- 无论源材料是否写了标题层级序号，Markdown intermediate 中的标题文字都不得保留该序号。
- 渲染器必须忽略标题开头的 `一、`、`（一）`、`1.`、`1.1`、`（1）` 及对应全角/半角变体，公文层级编号只由模板根据标题级别自动生成。
- 带手写标题序号和不带手写标题序号的等价输入，必须产生同一套模板自动编号，不能重复编号。

## Font Fallback Rules

- 字体 fallback 必须按字体类型分组，只能在同类型字体之间替代。
- 黑体类可使用 `SimHei`、`STHeiti`、`Heiti SC`、`Noto Sans CJK SC`、`Source Han Sans SC`、`思源黑体` 等无衬线黑体；不得 fallback 到宋体类。
- 宋体类可使用 `SimSun`、`NSimSun`、`Songti SC`、`STSong`、`Noto Serif CJK SC`、`Source Han Serif SC`、`思源宋体` 等衬线宋体；不得 fallback 到黑体类。
- 仿宋、楷体、小标宋和等宽代码字体也应分别使用同类 fallback，不能为了提高字体命中率跨类型混用；例如小标宋不得降级为普通宋体。

## Renderer Notes

- `skills/gongwen/scripts/gongwen.sh render` converts `gongwen-full.md` to Typst through built-in shell logic.
- Rendering must not depend on an external template binary, Pandoc, Python, Node, or another Markdown converter.
- PDF export is optional through `render --pdf <output.pdf>` and only calls the installed `typst` CLI on the generated `.typ`.
- `--expected-typ` performs black-box comparison against a reference Typst file.

## Verification Detail

- `skills/gongwen/scripts/gongwen.sh example --output <file>` must output a reviewable `gongwen-full.md` structure.
- `skills/gongwen/scripts/gongwen.sh render --input <md> --typ <typ>` must generate Typst without external converters.
- `skills/gongwen/scripts/gongwen.sh render --input <md> --typ <typ> --pdf <pdf>` must export PDF when `typst` is installed and preserve `**bold**` semantics.
- `--expected-typ` must match the generated Typst against a fixture when provided.
- `skills/gongwen/tests/test_heading_normalization.sh` must confirm numbered and unnumbered heading fixtures render identically and font fallback lists do not cross font types.
