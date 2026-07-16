# Gongwen Format and Rendering Reference

This reference holds detailed authoring and renderer rules for the `gongwen` skill. Keep `SKILL.md` as the concise semantic entry point and update this file when long format behavior changes.

## Frontmatter

- `title`: 公文标题；如需标题中手动换行，用 `|` 标记断点。
- `author`: 发文单位；可为字符串或字符串数组。
- `date`: `YYYY-MM-DD` 格式日期。
- `signature`: 是否启用签名信息；使用 `true` 时，落款单位和日期只从 `author`、`date` 生成。
- `template`: 固定为 `gongwen`。

当 `signature: true` 时，正文严禁再手写落款、日期或署名块。严禁在新文档示例、默认模板、推荐写法或生成指令中展示旧式手工落款；旧 fenced div 只允许作为兼容解析能力存在，不能作为新文档的落款写法。

## Body Structure

- 正文使用可审阅的 Markdown 表达结构：标题、段落、有序/无序列表、表格、代码块、引用、图片和图组。
- 只有源材料明确要求顺序、步骤或编号时才使用有序列表。
- 不要为了套用模板而凭空添加项目序号、编号列或“序号/项目”字段。
- `signature: true` 时，正文不得手写落款、署名单位或日期块；不要在正文末尾写 `author`、`date` 的重复内容。
- “特此通知。”、“未尽事项由……解释。”等正文句子仍属于正文，不得被当作落款从正文中摘除。

## Gongwen Control Syntax

- 旧式无首行缩进 fenced div 只作为兼容解析保留；新文档使用段末 `{.noindent}` 标记无首行缩进段落。
- Markdown `**加粗内容**` 表示正文或标题内的行内加粗，渲染和 PDF 导出时应保留为加粗语义。
- `{.indent}`、`{.bold}` 表示局部排版属性。
- `{.br:N}` 表示插入 N 个换行。
- `{pagebreak}` 或 `{pagebreak:weak}` 表示分页。
- Markdown 表格后的 `: 表题` 表示表格题名。
- 同一段内多张图片且 alt 相同表示一组子图。

## Numbering Rules

- 不要为了“看起来规范”凭空增加项目序号、序号列、项目编号、有序列表或手写标题编号。
- 普通段落、列表、表格中的业务编号按源材料保留；本规则只归一化 Markdown 标题开头的层级序号。
- 无论源材料是否写了标题层级序号，最终 Markdown 中的标题文字都不得保留该序号。
- 渲染器必须忽略标题开头的 `一、`、`（一）`、`1.`、`1.1`、`（1）` 及对应全角/半角变体，公文层级编号只由模板根据标题级别自动生成。
- 带手写标题序号和不带手写标题序号的等价输入，必须产生同一套模板自动编号，不能重复编号。

## Font Fallback Rules

- 字体 fallback 必须按字体类型分组，只能在同类型字体之间替代。
- 黑体类可使用 `SimHei`、`STHeiti`、`Heiti SC`、`Noto Sans CJK SC`、`Source Han Sans SC`、`思源黑体` 等无衬线黑体；不得 fallback 到宋体类。
- 宋体类可使用 `SimSun`、`NSimSun`、`Songti SC`、`STSong`、`Noto Serif CJK SC`、`Source Han Serif SC`、`思源宋体` 等衬线宋体；不得 fallback 到黑体类。
- 仿宋、楷体、小标宋和等宽代码字体也应分别使用同类 fallback，不能为了提高字体命中率跨类型混用；例如小标宋不得降级为普通宋体。

## Renderer Notes

- `skills/gongwen/scripts/gongwen.sh render` converts the final Markdown file to same-title Typst through built-in shell logic.
- Markdown→Typst rendering must not depend on an external template binary, Pandoc, Python, Node, or another Markdown converter. The publication transaction uses the bundled Python 3 helper for descriptor-relative filesystem mutation.
- Final PDF export through `render --pdf <output.pdf>` only calls the installed `typst` CLI on the generated `.typ`; successful gongwen tasks must keep that `.typ` as the only Typst artifact.
- `--expected-typ` performs black-box comparison against a reference Typst file.
- The renderer requires `author`, `date`, `signature`, and `template: "gongwen"` in YAML frontmatter.
- `--typ` is authoritative for the delivery root and stable stem. Optional `--pdf` must resolve to that same real parent directory and stem.
- Reviewed Markdown, rendered Typst, and optional PDF are generated in one owned candidate. Expected comparison happens before publication; PDF compilation reads candidate Typst from standard input with the reviewed Markdown parent as the Typst root so existing relative `assets/...` references retain their meaning. The result must be regular, non-empty, and begin with `%PDF-`.

## Artifact Contract

- The working document path is `documents/YYYYMMDD 事项名称/标题.md`; it remains the reviewable source of truth and is copied byte-for-byte into the candidate.
- Without `--pdf`, current is exactly `标题.md + 标题.typ`; with `--pdf`, current is exactly `标题.md + 标题.typ + 标题.pdf`. Adding or removing PDF changes the managed path set and archives the previous whole bundle.
- Candidate validation precedes current mutation. Exact path-set+bytes equality is a no-op that preserves current inode/mtime and creates no history.
- A changed current pair/triple is copied as one verified bundle into the next `history/<sequence>/`; sequence is numeric `max + 1`, at least three digits, so existing `001/003` yields `004`.
- `sources/` is retained user material and never mutated by normal render; `assets/` is reserved for persistent referenced resources; `history/` owns old successful bundles; `.work/<run-id>/{candidate,rollback,evidence}` is run-owned and removed on success or handled failure.
- Root-level unknown files, legacy `media/` or hidden diagnostic directories, symlinks, partial bundles, stale `.work`, path traversal, different-stem or cross-root outputs fail before mutation and require the confirmation-based cleanup workflow.
- Do not publish `source/`, `output/`, manifests, logs, diffs, verification files, cache, staging, or failed artifacts. Diagnostics remain bounded on stderr or in owned evidence until cleanup.
- Publication uses fixed validated names under one same-root lock. Handled error, `INT`, and `TERM` restore prior current and remove only this run/history reservation; SIGKILL, power loss, and multi-file atomicity are outside the portable guarantee.

## Verification Detail

- `skills/gongwen/scripts/gongwen.sh example --output <标题.md>` must output a reviewable final Markdown structure.
- `skills/gongwen/scripts/gongwen.sh render --input <md> --typ <typ>` must generate Typst without external converters.
- `skills/gongwen/scripts/gongwen.sh render --input <md> --typ <typ> --pdf <pdf>` must export PDF when `typst` is installed and preserve `**bold**` semantics.
- `--expected-typ` must match the generated Typst against a fixture when provided.
- `skills/gongwen/tests/test_heading_normalization.sh` must confirm numbered and unnumbered heading fixtures render identically and font fallback lists do not cross font types.
- `skills/gongwen/tests/test_clean_delivery.sh` must cover pair/triple first-change-no-op, optional PDF set changes, history gap, seven standard faults, `INT`/`TERM`, lock conflict, expected/compile/PDF failures, unsafe paths/symlinks/unknowns and owned cleanup through the public CLI.
- Contract tests must also confirm `signature: true` rejects handwritten body author/date lines and that current contains the exact requested pair/triple with no evidence sidecars.
