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
- 只有源材料明确给出编号时才保留。
- 公文层级编号由模板根据标题层级自动生成，不要在标题文字里重复写 `一、`、`（一）`、`1.` 或 `（1）`。

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
