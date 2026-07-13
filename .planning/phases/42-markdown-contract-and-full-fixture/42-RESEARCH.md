# Phase 42: Markdown Contract and Full Fixture - Research

**Researched:** 2026-07-13
**Status:** Ready for planning

## Research Question

为了高质量规划 Phase 42，需要知道什么？

Phase 42 不能只交付一篇语法说明和一份看起来完整的 Markdown。它需要锁定一个可由教师直接审阅、可被机器无歧义解析、可向 Phase 43 传递带源码位置逻辑模型的契约；同时交付一套确定性 full fixture、配套媒体和可重复 `example`/验证入口，覆盖 MD-01 至 MD-08 与 VER-01。

## Executive Summary

建议将 Phase 42 规划为三个相互验证的交付面：

1. `references/markdown-contract.md`：规范公开语法、布局语义、内容块、notes、媒体、错误边界和自动关闭页行为。
2. `fixtures/`：保存真实、可读、覆盖全部受控布局语义及分页输入的 canonical full fixture 与自包含媒体；不要把 fixture 混进 `templates/`。
3. `scripts/markdown_contract.py` 加现有 `school-pptx.sh`：解析并验证契约、输出带行号的逻辑 AST/诊断，并提供确定性 `example` 命令。

最重要的架构选择是：Phase 42 就建立 Phase 43 将直接消费的逻辑文档模型，而不是让 Phase 43 再写一套 Markdown 解释器。否则 MD-05、notes、`###` 绑定、`two-column` 配对、`image-text` 多图扩展和错误定位都会在两个阶段之间漂移。

## Sources Inspected

必须阅读且已核对：

- `.planning/phases/42-markdown-contract-and-full-fixture/42-CONTEXT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/ROADMAP.md`
- `.planning/PROJECT.md`
- `AGENTS.md`
- `.planning/phases/41-standard-template-and-manifest/41-CONTEXT.md`
- `.planning/phases/41-standard-template-and-manifest/41-01-SUMMARY.md`
- `.planning/phases/41-standard-template-and-manifest/41-RESEARCH.md`
- `skills/school-pptx/references/template-contract.md`
- `skills/school-pptx/references/template-editing.md`
- `skills/school-pptx/templates/standard-school.manifest.yaml`
- `skills/school-pptx/scripts/school-pptx.sh`
- `skills/school-pptx/scripts/template_report.py`
- `skills/tiaokedan/references/markdown-contract.md`
- `skills/school-presentation/references/authoring-and-layout.md`
- `skills/school-presentation/templates/school-presentation-full.md`

仓库根目录不存在 `CLAUDE.md`；本阶段范围内也没有更深层 `AGENTS.md`。

## Key Findings

### 1. Phase 42 应产出可复用解析器，而非仅靠文档声明验证

ROADMAP 的 Phase 42 成功标准要求用户能获得可定位的 unsupported layout、raw coordinate styling、任意 font/color override、unsupported raw HTML 和 missing media 错误。仅写 `markdown-contract.md` 和 fixture 无法证明该标准。

现有 `school-pptx.sh` 只有 `template-report` 与 `info`；Phase 43 的 `render` 尚未存在。因此 Phase 42 应新增一个轻量 `validate` 命令及其解析模块，让本阶段就能证明 MD-01 至 MD-08，并让 Phase 43 直接复用。

推荐接口：

```text
skills/school-pptx/scripts/school-pptx.sh validate \
  --input <deck.md> \
  [--out-json <logical-document.json>]
```

验证成功返回 0；任何结构、样式或媒体错误返回非 0。`--out-json` 应用于显式验证/隐藏工作目录，不是默认公共交付物。即使验证失败，也可以写出带 `errors` 和安全 fallback 元数据的诊断模型，供 Phase 43 生成明确标识的 best-effort artifact；退出状态仍必须保持失败。

### 2. 解析器应是受限 Markdown 状态机，而不是通用 Markdown 渲染器

契约表面很小，但有嵌套容器、源码位置和布局相关规则：

- YAML frontmatter；
- `::: slide {layout="..."}`；
- slide 内最后一个 `::: notes`；
- `##` slide title；
- `###` 只绑定紧随其后的一个内容块；
- paragraph、完整 list、image、table、fenced code 等顶层 block；
- `==highlight==` 受限扩展；
- raw HTML 与任意样式控制必须拒绝。

最稳妥的实现是一个逐行、维护容器栈与 fenced-code 状态的解析器。它可以保留每个节点的 `source_line`，避免先经通用 Markdown 转 HTML 后丢失精确定位。YAML 可继续使用 Phase 41 已使用的 PyYAML；建议通过 `yaml.compose()` 的 node mark 或 frontmatter 行扫描为未知字段提供准确行号。

不要在 Phase 42 引入 Pandoc 或 Node Markdown 依赖。它们对这套自定义容器和逐项错误聚合没有明显收益，还会提前扩大 Phase 44 的依赖检查范围。

### 3. 逻辑 AST 是 Phase 42 与 Phase 43 的关键交接件

推荐逻辑模型至少包含：

```text
document
  metadata: allowed YAML fields only
  document_title: YAML title or first # fallback
  contents_entries: ordered ## titles
  logical_slides[]
    layout
    title
    source_line
    blocks[]
      kind
      heading (optional ###)
      source_line
      payload
      media_path / caption (when applicable)
    notes (optional, source line preserved)
  implicit_slides[]
    closing
  errors[] / warnings[]
```

Phase 42 不应实现 PPTX physical pagination，但必须把 Phase 43 需要的语义全部结构化：块边界、源序、表头/表行、timeline items、gallery images、code language/text、notes、媒体原始路径与解析后绝对路径、bold/highlight inline spans。

这样 Phase 43 只负责“逻辑模型到 PPTX 对象与物理页”，不再重新判断 Markdown 含义。

### 4. 公开 frontmatter 必须严格白名单，且 title fallback 规则要可验证

MD-02 与 CONTEXT D-02 已锁定唯一允许字段：

- `title`
- `subtitle`
- `school`
- `department`
- `program`
- `course`
- `author`
- `presenter`
- `date`
- `theme`

未知字段必须聚合为错误，不能静默忽略。`theme` 应读取 manifest 的 `available_themes`，而不是在解析器中重复一份主题真相。

`title` 缺失时只使用正文中第一个 `#` 作为 document title fallback；`#` 不进入 contents。若 YAML `title` 已存在，第一个 `#` 可用于可见审阅但不能覆盖 YAML title。需要在契约中明确多余 `#` 的处理；推荐只允许零个或一个 document-level `#`，多个视为结构错误，避免 fallback 歧义。

### 5. `##` 是 slide title 与 contents 的唯一来源，特殊布局需写清映射

CONTEXT D-03 和 D-08 要求 contents 按源码顺序来自 `##`，且扩展后的每个 physical slide 保持同一个逻辑 `##` 标题。Phase 42 应明确：

- 普通 authorable slide block 恰好包含一个 `##` title；
- contents entries 是全部合法 `##` title 的源码顺序列表，不从 `#` 推导；
- 不允许 slide block 外的 `##`；
- 一个 slide block 中出现多个 `##` 是错误，而不是隐式拆页。

`cover`、`contents` 和自动 `closing` 是特殊布局：cover 可从 frontmatter/document title 填充；contents 的条目由解析器生成；closing 不接受 Markdown 内容。契约必须为这些特例写出明确规则，不能让 renderer 猜测。

### 6. “11 个布局覆盖”与 Phase 41 的不可控 closing 存在表面冲突，计划必须显式调和

Phase 41 已锁定并实现：

- `closing.fixed_template_page: true`
- `closing.default_insertion: end_of_deck`
- `closing.markdown_controllable: false`
- `closing` 没有 slots

Phase 41 summary 也明确 closing 是“fixed template-owned final page with no Markdown-controllable title/subtitle slots”。但 MD-06/Phase 42 文案又要求 full fixture 覆盖全部 11 layouts，而 CONTEXT D-01 表述为 slide 使用显式 layout block。

高质量规划不应通过允许 `::: slide {layout="closing"}` 来回退 Phase 41 契约。推荐解释是：

- fixture 显式覆盖 10 个 authorable layouts；
- 第 11 个 `closing` 由逻辑模型标记为 implicit、由后续 renderer 自动追加；
- `validate` 对显式 author-authored `closing` block 报错；
- fixture/验证报告仍声明 11/11 controlled layout semantics covered，其中 10 explicit + 1 implicit；
- `markdown-contract.md` 清楚区分 `supported layouts` 与 `authorable layouts`。

这既满足 MD-06 的完整 deck 覆盖意图，又保持已完成 Phase 41 的固定关闭页契约。计划验收项必须直接检查该行为，否则执行者很容易误把 closing 暴露给作者。

### 7. 内容块模型应在 Phase 42 完整锁定

CONTEXT D-05 至 D-10 已足以定义稳定 block model：

- paragraph 是一个 block；连续段落按空行分隔；
- 一个完整有序/无序列表是一个 block；
- 一张 Markdown image 是一个 atomic block；alt text 是 caption，空 alt 表示无 caption；
- image + caption 是不可拆 composite block，后续按 contain 放置；
- Markdown table 是一个 block；可选 `###` table title 与 table 合成一个 composite block；
- fenced code 是一个 block；
- `### 标题` 强制开始新 block，只绑定紧随其后的一个 block；
- 空 `###` 只作为无可见标题的 manual block boundary；
- `###` 后没有 block、连续多个未消费 `###`、或 `###` 绑定 notes 都应报错。

`two-column` 不使用 left/right 私有语法。它按 block source order 配对：1/2、3/4……；最后一个未配对 block 进左栏，右栏为空。Phase 42 模型应记录有序 blocks，Phase 43 再应用 manifest budget 和物理分页。

`title-content` 同样只保留有序 blocks；本阶段不计算每页装多少，但 fixture 必须给出足够长且可拆的输入。

### 8. `image-text` 需要独立、可测试的槽位语义

`image-text` 不是 generic two-column：

- one stable body；
- one or more primary Markdown images；
- 每张图在 Phase 43 形成一个 successive physical slide；
- slide title、body、notes 保持相同，只替换 image 与 caption；
- Markdown 顺序不控制左右几何，模板的 `media`/`body` slots 决定位置。

解析器应将 images 和 stable body 分开建模，而不是简单保存混合 block 数组。应拒绝无法确定 stable body 的歧义输入，例如多个互相分离且没有契约定义的 body groups。

### 9. table、timeline、gallery、code 需要在文档中定义最小公开语法

CONTEXT 锁定了功能，却未完全锁定 timeline item 的具体 Markdown 形状。规划时应选择最小、教师可读、无需 raw HTML 的语法并在 fixture 中只使用这一种。

推荐：

- `table`：普通 Markdown table；可用紧邻的 `###` 作为可见 table title；
- `timeline`：受限 Markdown table，例如固定列 `时间 | 标题 | 说明`，解析为 ordered timeline items；
- `gallery`：连续普通 Markdown images，每张 alt 为 caption；超过 4 张作为 Phase 43 pagination 输入；
- `code`：一个 fenced code block，language tag 可保留但 v1.17 不要求 syntax highlighting；
- icons：同样使用普通 Markdown image syntax，不引入 `icon=` 私有指令。

固定 timeline 列名比再引入一套属性列表更容易审阅、定位和验证。若 planner 选择列表语法，也必须在契约、解析器和 fixture 中只保留一个 canonical form。

### 10. 样式边界必须以 allowlist 为核心，而非只匹配少数坏字符串

MD-05 要拒绝 unsupported layout、raw coordinate styling、arbitrary font/color overrides 和 unsupported raw HTML。推荐策略：

- slide opener 只允许公开属性 `layout`；临时 `id` 仅能通过内部开发开关接受，不出现在 public contract、fixture 或 normal CLI；
- layout 必须来自 `standard-school.manifest.yaml`，但 explicit `closing` 因不可控而拒绝；
- 拒绝所有 raw HTML tags/comments（fenced code 内除外）；
- 拒绝 generic attribute lists、`style=...`、坐标/尺寸/字体/颜色类属性；
- 仅解析标准 `**bold**` 与受限 `==highlight==`，作者不能携带颜色参数；
- fenced code 内的 HTML、CSS 字样是代码文本，不应误报。

与其不断增加 `x=`, `font=`, `color=` 正则，不如只允许契约列出的容器、属性和 inline forms；任何未知 directive/attribute 都带行号报错。

### 11. notes 必须是独立节点，且 last-only 约束应在解析时执行

`::: notes` 必须：

- 位于 owning slide block 内；
- 最多一个；
- 是 slide 中最后一个 child；
- 不进入 visible blocks 或 contents；
- 保留 Markdown 文本与 source line；
- 在 logical slide expansion 时由 Phase 43 复制到全部 physical slides。

notes 后出现可见内容、slide 外 notes、嵌套 notes、未闭合 notes 均应成为可定位结构错误。full fixture 应同时包含有 notes 与无 notes 的 slides，便于 Phase 43 验证“有则复制、无则不意外生成”。

### 12. missing media 是验证失败，但模型要保留可恢复信息

MD-08 与 CONTEXT D-12/D-14 的正确组合是：

- relative media path 以 Markdown 文件所在目录解析；
- absolute path 可接受；
- 原始 path 与 resolved path 都进入逻辑模型；
- 文件不存在时记录 slide、line、original path；
- `validate` 返回非 0，不能宣称验证成功；
- 模型可附加 standard placeholder descriptor，供 Phase 43 显式 best-effort 输出。

不要让 full fixture 自身包含缺失媒体；它应是 accepted positive fixture。missing media negative case应在临时 workdir 中由验证脚本动态构造，避免把一份真实演示变成可见测试矩阵。

### 13. full fixture 应放在 `fixtures/`，并自包含 companion media

根 `AGENTS.md` 要求 templates 只存模板，不要混入示例内容。`standard-school.pptx` 与 manifest 已占用 `templates/` 的正确职责；真实 full presentation 更适合：

```text
skills/school-pptx/fixtures/school-pptx-full.md
skills/school-pptx/fixtures/media/...
```

fixture 主题应按 D-18/D-19 写成“职业院校智能制造课程建设”的完整叙事，而不是“layout test 1/11”。它需要自然覆盖：

- cover、contents、section、title-content、two-column、image-text、table、timeline、gallery、code；
- implicit closing；
- 有/无 subtitle 等可选 cover metadata；
- notes；
- relative images 与 icons、含 caption/空 caption；
- image-text 多图；
- 长 text、长 table、长 timeline、超过 4 图 gallery、超过 code budget 的长 code；
- `two-column` 偶数配对和最后一个 unpaired left block；
- `###` 可见 subheading 与空 `###` boundary；
- `**bold**` 与 `==highlight==`；
- table title 与 slide title 分离。

companion media 应是 skill-local、可提交、来源明确且无需网络的 PNG/JPEG；不要让运行时引用 `skills/school-presentation` 或 `test/`。媒体内容应与智能制造课程叙事相符，避免复用现有猫图等仅适合旧测试的素材。

### 14. `example` 应采用安全、确定性的目录输出

推荐接口：

```text
skills/school-pptx/scripts/school-pptx.sh example --out-dir <dir>
```

每次固定写入：

```text
<dir>/school-pptx-full.md
<dir>/media/<known-files>
```

命令应：

- 创建缺失父目录；
- 覆盖自己拥有的固定文件；
- 不删除 `<dir>` 中无关文件；
- 不写 timestamp、随机 id 或机器绝对路径；
- 复制后用同一 validator 校验；
- 明确打印写入路径；
- 连续执行两次结果 byte-for-byte 相同。

这比无参数写入仓库或当前目录更安全，也比让用户逐个指定 Markdown/媒体目标更符合“fixed destination with deterministic Markdown and companion media”。

## Requirement Mapping

| Requirement | Planning implication | Verification evidence |
|---|---|---|
| MD-01 | 文档与解析器共同定义 YAML + explicit slide blocks | positive fixture validate PASS；AST 含 logical slides |
| MD-02 | frontmatter strict allowlist | 每个允许字段 positive；未知字段带行号 non-zero |
| MD-03 | optional cover metadata omission + first `#` fallback | 两个临时 positive variants；AST document title 检查 |
| MD-04 | contents 仅来自 ordered `##` | 检查 AST `contents_entries` 顺序且不含 `#` |
| MD-05 | manifest-driven layout + style/HTML allowlist | unknown layout/style/font/color/raw HTML negative cases |
| MD-06 | realistic fixture 覆盖 10 explicit + 1 implicit layouts 与 overflow inputs | fixture coverage assertion、block-kind counts、implicit closing |
| MD-07 | notes 独立且 last-only | AST notes 不在 visible blocks；非法位置 non-zero |
| MD-08 | standard Markdown images；relative-to-source/absolute resolution | relative/absolute positive 与 missing media negative |
| VER-01 | repeatable example command | 连跑两次 hash/diff 相同，Markdown 和媒体均覆盖 |

## Recommended File Targets

Phase 42 推荐写入范围：

- `skills/school-pptx/references/markdown-contract.md`
- `skills/school-pptx/fixtures/school-pptx-full.md`
- `skills/school-pptx/fixtures/media/<self-contained-assets>`
- `skills/school-pptx/scripts/markdown_contract.py`
- `skills/school-pptx/scripts/school-pptx.sh`

如需要保存固定验证入口，可增加一个 skill-local contract verification script；不要在本阶段创建最终 `SKILL.md`、runtime adapter notes 或 README/compatibility matrix 更新，这些属于 Phase 44。

不要在 Phase 42 修改：

- `standard-school.pptx` 的视觉内容；
- manifest 的布局/几何/slot/budget，除非执行时发现 Phase 41 的真实结构错误；
- PPTX renderer、physical pagination、PPTX notes XML；
- final verify/UAT/runtime 文档。

## Validation Architecture

### Positive path

1. `example --out-dir <tmp>` 写 Markdown 与 companion media。
2. `validate --input <tmp>/school-pptx-full.md --out-json <tmp>/.school-pptx/logical-document.json`。
3. 断言 validation PASS、无 errors。
4. 断言 YAML keys 是允许集合子集，theme 为 `standard-school`。
5. 断言 10 个 explicit authorable layouts 均出现，implicit closing 恰好一个。
6. 断言 ordered `contents_entries` 与 fixture 中 `##` 顺序一致，且 document `#` 不进入。
7. 断言 notes、images/icons、table、timeline、gallery、code 与 overflow inputs 都存在于 AST。
8. 断言所有 relative media resolve 到 fixture 相邻 `media/` 且文件存在。
9. 再运行一次 `example`，比较 Markdown 与全部媒体的 SHA-256/byte diff 完全相同。

### Negative path

在临时目录中由 accepted fixture 派生小型 case，不把错误示例放进公开 full fixture：

- unknown YAML field；
- unknown theme；
- missing layout attribute；
- unsupported layout；
- explicit `closing`；
- unknown slide attribute / temporary public `id`；
- raw coordinates；
- font/color override；
- raw HTML；
- slide 外 `##`；
- multiple `##` in one slide；
- notes not last / duplicate notes / unclosed block；
- dangling `###`；
- missing media；
- malformed table/timeline/gallery/code layout content。

每个 case 应检查 non-zero、诊断包含文件、行号、logical slide/title（可定位时）、field/path 与可操作原因。一次输入含多个独立错误时应尽可能聚合，证明 D-15，而不是只报第一个。

### Diagnostic model invariants

- `errors` 非空时 overall status 必须是 invalid；
- missing media 可带 placeholder metadata，但不能降级为 warning-only；
- notes 不进入 visible blocks；
- `closing` 是 implicit，不是 author block；
- parser 不复制 manifest 的布局真相，只按 manifest 查 theme/layout/slot ownership；
- 所有 source positions 使用 1-based line numbers。

## Risks and Planning Notes

### Risk 1: closing 覆盖语义被误实现

这是当前最明确的跨阶段冲突。若允许 Markdown 显式 author closing，会破坏 Phase 41 已锁定的 `markdown_controllable: false`。计划应把“10 explicit + 1 implicit”写进任务与验收，而非仅留在文档解释中。

### Risk 2: `##` 的特殊布局规则不清导致目录污染

若 cover、contents 自己也被要求写 `##`，contents 很可能包含封面/目录自身；若不要求，又需要为 D-08 定义例外。计划应要求 contract 中列出每个 layout 的 required/allowed content，并为 cover/contents/closing 加专门测试。

### Risk 3: timeline 公开语法尚未锁定

CONTEXT 锁定 timeline coverage，但没有给出唯一 item grammar。Planner 必须在计划里明确一个最小 canonical syntax；不要把这个决定拖到 renderer 实现时。

### Risk 4: validator 与 renderer 解析逻辑分叉

若 Phase 42 只做 regex validation、Phase 43 再做独立 parser，两者会对 block boundary、notes 和 media 得出不同结果。Phase 42 的 parser/AST 应成为 Phase 43 的唯一输入接口。

### Risk 5: 误报 fenced code 中的 HTML/CSS

style/raw HTML 检查必须理解 fenced code 边界。代码示例中出现 `<div>`、`color` 或坐标词不应被当成作者样式控制。

### Risk 6: fixture 资源依赖兄弟技能或测试目录

Phase 43/最终技能要求 skill-local runtime。Phase 42 就应复制或创建自有、来源明确的 companion media；不要在 fixture 中引用 `skills/school-presentation/...` 或 `test/...`。

### Risk 7: fixture 很完整但无法证明 pagination inputs

本阶段不分页，但 AST 验证应能证明长文本字符/行数、table rows、timeline item count、gallery image count、code lines 超过 manifest 对应 budget 或后续固定容量。否则“overflow cases”只是描述，没有机器证据。

### Risk 8: example 覆盖范围过宽

幂等覆盖只能触碰固定拥有的 Markdown 和 companion media。不要 `rm -rf --out-dir`；这会删除用户同目录文件并违反安全边界。

## Suggested Plan Shape

### Plan 42-01: Contract model and manifest-driven validator

1. 编写 `markdown-contract.md`，锁定 public grammar、layout-by-layout rules、content block model、notes/media/emphasis 与 forbidden controls。
2. 实现 `markdown_contract.py` 状态机、manifest-driven theme/layout validation、逻辑 AST 和聚合诊断。
3. 将 `validate` 接入 `school-pptx.sh`，保留现有 `template-report`/`info` 行为。
4. 用临时 positive/negative cases 验证 frontmatter、heading、slide/notes nesting、styles、HTML 和 media resolution。

### Plan 42-02: Full fixture, companion media, and example determinism

1. 在 `fixtures/` 编写真实智能制造课程建设 full deck，覆盖 10 explicit layouts、implicit closing 和全部 required blocks/overflow inputs。
2. 增加 self-contained companion media，全部使用相对 Markdown path。
3. 实现 `example --out-dir` 的安全确定性覆盖与复制后验证。
4. 连跑两次进行 byte-for-byte 验证，并检查 AST coverage、contents order、notes separation 和 overflow evidence。

两份 plan 可以按依赖顺序执行：42-02 依赖 42-01 的契约与 validator。粗粒度模式下也可合成一个 plan，但任务边界仍应按上述两个闭环组织。

## Planning Readiness

本地证据足以规划 Phase 42，不需要外部网络研究。PyYAML 已被 Phase 41 使用，现有 shell dispatcher 可直接扩展，manifest 已提供 11 layout ids、slot kinds 和 budgets。

规划前唯一必须显式写进 plan 的解释是：`closing` 以 implicit fixed page 覆盖，不暴露为 Markdown-authorable block。其余未锁定细节（尤其 timeline item grammar、fixture 文件名和媒体文件名）属于 Claude's Discretion，可由 planner 按上述最小语法方案确定。

## RESEARCH COMPLETE
