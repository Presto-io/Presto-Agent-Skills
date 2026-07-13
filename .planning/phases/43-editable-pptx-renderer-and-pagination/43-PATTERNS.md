# Phase 43：实现模式映射

**映射日期：** 2026-07-14  
**范围：** Editable PPTX Renderer and Pagination  
**结论：** 当前仓库已经形成“canonical 核心模型 + 薄 CLI 分发 + 纯中间计划 + 原生对象发射 + 独立重复验证 + 描述符约束原子发布”的实现风格。Phase 43 应沿用该风格，不应另建 Markdown 解析器，也不应把分页、布局分支或发布逻辑堆入 shell/CLI。

## 1. 建议文件清单、角色与数据流

| 文件 | 角色 | 输入 | 输出 / 下游 | 最接近 analog |
|---|---|---|---|---|
| `skills/school-pptx/scripts/school-pptx.sh` | 公共薄分发器；只增加 `render` usage 与 dispatch | CLI argv、`SCHOOL_PPTX_PYTHON` | 调用 `pptx_render.py`；原样传播退出码 | 当前同文件的 `validate|example`、`template-report` 分发（L30-L53） |
| `skills/school-pptx/scripts/markdown_contract.py` | canonical 逻辑模型源；仅被 import，不复制解析规则 | Markdown bytes、manifest | `parse_document()` 返回 logical document、errors、warnings | 本文件 `parse_document()`（L370 起）、`DiagnosticCollector`（L84-L107） |
| `skills/school-pptx/scripts/pptx_render.py` | render CLI 编排、依赖检查、状态机、诊断摘要、发布顺序 | `--input`、`--out-dir`、可选 `--stem` | 调用 parser → paginator → emitter → package verifier → publisher；返回 0/非 0 | `markdown_contract.validate_command()`（L697-L730）+ end-of-term `main()` 的异常边界（`_engine.py` L1474-L1487） |
| `skills/school-pptx/scripts/pptx_model.py` | 纯数据结构：物理页计划、fragment、诊断、映射索引 | logical document、normalized manifest 的值类型 | 被 paginator 构造、emitter/validator 只读消费 | `Diagnostic` / `SourceLocation` dataclass（`markdown_contract.py` L59-L81） |
| `skills/school-pptx/scripts/pptx_paginate.py` | 纯、确定性分页；不得 import `python-pptx` | logical document + normalized manifest + `TextMeasure` | `PhysicalDeckPlan`，包含 logical→physical 映射、字号、fragment、notes、诊断 | Phase 42 logical model 的 source-located block；验证脚本的 deterministic equality gate（`verify_markdown_contract.py` L228-L230） |
| `skills/school-pptx/scripts/pptx_emit.py` | 模板 bootstrap、种子页移除、按 layout dispatch 发射 | template + manifest + frozen physical plan | staged PPTX package | `template_report.load_shape_index()` 按 OOXML part path 解析布局（L58-L96）；不要照搬数字索引 |
| `skills/school-pptx/scripts/pptx_objects.py` | 原生文本/run、表格、contain 图片、group、notes 的小型 helper | 单页 fragment + manifest slot | native editable shapes | `markdown_contract.media_block()` 已锁定 resolved path / contain / safe placeholder（L190-L216） |
| `skills/school-pptx/scripts/pptx_ooxml.py` | 极小兼容层，仅处理 public API 缺口 | python-pptx element | `<a:highlight>`、受控 seed slide removal/group compatibility | `template_report.py` 的 namespace + XML 结构检查（L22-L29、L58-L91） |
| `skills/school-pptx/scripts/verify_pptx_renderer.py` | Phase 43 独立回归门；从公共 CLI 黑盒调用，并可 import 纯模块白盒测试 | fixture、临时目录、故障注入 | PASS/AssertionError；不成为公开 `verify` 命令 | `verify_markdown_contract.py` 的 `run()`、临时目录、gate registry、结构/安全测试 |
| `skills/school-pptx/templates/standard-school.manifest.yaml` | 所有几何、预算、空槽、主题 token、分项 preset 的机器源 | 受控模板契约 | parser、paginator、emitter、template-report 共同消费 | 当前 manifest + `template_report.validate_manifest()` |
| `skills/school-pptx/templates/standard-school.pptx` | theme/master/layout/decorative assets 的唯一视觉基底 | emitter 打开 | staged/final PPTX | `template_report.load_shape_index()` 直接读取 ZIP/XML |
| `skills/school-pptx/references/template-contract.md` | 人类可审阅的模板 schema 与编辑边界 | manifest 变更 | 实现与维护约束 | 当前 Phase 41 contract；变更 manifest 时同步更新 |
| `skills/school-pptx/references/markdown-contract.md` | 公共 `render` 双产物与异常语义 | Phase 43 D-17～D-21 | CLI 用户/agent 契约 | 当前 validate/example 文档模式 |
| `skills/school-pptx/fixtures/school-pptx-full.md` | 完整正向、分页和 editability fixture | render CLI | `<stem>.md` + `<stem>.pptx` | Phase 42 `full_fixture_gate()`（L627-L670） |

建议数据流固定为：

```text
authored Markdown bytes
  -> markdown_contract.load_manifest()
  -> markdown_contract.parse_document()
  -> normalize manifest contract
  -> pptx_paginate.build_physical_plan()
  -> pptx_emit.emit_staged_presentation()
  -> verify staged ZIP/XML + python-pptx reopen
  -> publish Markdown sibling
  -> atomic os.replace(staged PPTX, final PPTX)
  -> print bounded success / best-effort / unrecoverable summary
```

关键边界：`pptx_emit.py` 不得重新决定分页；`pptx_render.py` 不得出现 layout-specific 几何；`school-pptx.sh` 不得包含业务条件；`pptx_paginate.py` 不得操作 PPTX 对象。

## 2. school-pptx 内部可直接继承的模式

### 2.1 薄 shell dispatcher

`school-pptx.sh` 已使用 skill-relative 路径和可覆盖 Python runtime：

```bash
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"

case "$command" in
  validate|example)
    "${SCHOOL_PPTX_PYTHON:-python3}" "$SCRIPT_DIR/markdown_contract.py" "$SKILL_DIR" "$command" "$@"
    ;;
esac
```

Phase 43 应增加单独分支：

```bash
render)
  "${SCHOOL_PPTX_PYTHON:-python3}" "$SCRIPT_DIR/pptx_render.py" "$SKILL_DIR" "$@"
  ;;
```

CLI 建议与 research 一致：

```bash
school-pptx.sh render --input <reviewed.md> --out-dir <delivery-dir> [--stem <name>]
```

这比 `--output` + `--copy-markdown` 更直接表达同 stem 双产物。shell 使用 `set -euo pipefail`，Python 的非零状态会自然传播；不要在 shell 捕获并改写 best-effort 状态。

### 2.2 canonical parser 必须 in-process 复用

`markdown_contract.parse_document(input_path, manifest)` 已返回 renderer 所需数据：

- `logical_slides`、`implicit_slides`、`contents_entries`；
- 每个 block 的 `kind`、`source_line`、`heading`、结构化表格/时间线/代码；
- notes 与 overflow evidence；
- image 的 `authored_path`、`resolved_path`、`exists`、`placement: contain`；
- source-located `errors` / `warnings`。

媒体缺失仍返回安全、可渲染元数据，而不是提前丢弃 block：

```python
return {
    "kind": "image",
    "caption": caption,
    "resolved_path": str(resolved),
    "exists": exists,
    "placement": "contain",
    "atomic_composite": True,
    "placeholder": None if exists else {
        "kind": "missing-media",
        "label": "媒体缺失",
        "safe": True,
    },
}
```

这正是 D-17 best-effort 所需入口。render 应保留 parser errors，继续构造能够安全表达的物理计划；最后根据“是否发布结构有效 PPTX”与“是否存在 errors”决定退出码。不要 subprocess 调 `validate --out-json` 再读 JSON：那会引入第三产物、重复序列化和模型漂移。

### 2.3 诊断结构和有界输出

现有 `Diagnostic` 包含 `code/message/location/slide/layout/fix/path/severity`，`DiagnosticCollector`：

- 最多 200 条；
- 按 `(line, column, code)` 稳定排序；
- 超限追加 `RESOURCE_DIAGNOSTIC_LIMIT`；
- `print_diagnostic()` 输出路径、slide、layout、fix。

Phase 43 新诊断（例如 `TIMELINE_BALANCE_INFEASIBLE`、`CODE_LINE_OVERFLOW`、`PPTX_DEPENDENCY_MISSING`、`PPTX_PACKAGE_INVALID`）应复用相同字段与排序，不另建不兼容的字符串错误体系。若 renderer 自有诊断需附加 physical slide，可在 `pptx_model.py` 中扩展可选 `logical_index/physical_index`，但最终打印仍沿用现有四行格式并增加受影响物理页。

状态摘要应仿 `validate_command()`：先打印明确状态，再列输入、主题、错误/警告数、逐项诊断、产物、下一步。必须有三个互斥结果：

1. 成功：PPTX 发布且无 errors，退出 0；
2. best-effort：PPTX 发布但有 errors，明确“异常 PPTX / 非成功渲染”，退出非 0；
3. 不可恢复：未替换旧 PPTX，退出非 0。

### 2.4 manifest 校验先于 emitter

`template_report.validate_manifest()` 已建立仓库惯例：

- layout id 必须完整且无额外项；
- slot id 唯一；
- placeholder 通过 `ppt/slideLayouts/slideLayoutN.xml` + shape id/name 匹配；
- manifest geometry 与 layout XML geometry 在 tolerance 内一致；
- 每个 slot 的 text budget 必须完整；
- `empty_slot`、`continuation` 只接受受控 enum；
- errors 聚合后统一非零返回，而不是遇到第一个 slot 立即退出。

Phase 43 第一批 contract 修改应扩展这里，而不是只改 YAML：

- `gallery.caption.empty_slot: preserve`；
- table 新增 `table_name` 空槽及 budget；
- gallery 1/2/3/4 item presets；
- timeline node subregions / deterministic subdivisions；
- `inline_styles.highlight.scheme_color`；
- closing 指向 `ppt/slideLayouts/slideLayout7.xml`；
- 新字段的类型、范围、引用完整性都加入 evidence JSON。

模板报告输出的 Markdown/JSON evidence 模式适合继续复用，但 `write_text()` 当前只是直接写文件，不适合作为最终 PPTX 发布实现。

### 2.5 描述符约束的安全原子发布

`SecureExampleDestination` 是仓库中最强、最接近 D-19 的 analog：

```python
temporary_fd = os.open(
    candidate,
    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
    0o600,
    dir_fd=parent_fd,
)
...
os.fsync(temporary_fd)
...
os.replace(
    temporary_name,
    destination_name,
    src_dir_fd=parent_fd,
    dst_dir_fd=parent_fd,
)
```

它还通过 `fstat` 记录 `(st_dev, st_ino)`，在 publish 前后调用 `assert_public_identities()`，防止 output root/media parent 在准备与替换之间被换成 symlink；`close()` 只删除命令自有临时文件。

Phase 43 应提炼同类 renderer-owned publisher，而不是直接复用 `SecureExampleDestination` 名称或 `EXAMPLE_OWNED_PATHS`。推荐约定：

- 输出目录只拥有 `<stem>.md`、`<stem>.pptx` 与固定前缀临时文件；
- staged PPTX 必须与 final PPTX 同目录；
- 完成 ZIP/XML + reopen 验证后才 `os.replace()`；
- unrecoverable failure 保留旧 PPTX；
- best-effort 只要 staged PPTX 结构有效，仍替换 final PPTX，随后非零退出；
- 启动清理只匹配本命令前缀、普通文件、当前 output dir 身份，不 glob 删除任意隐藏文件。

重要限制：两个独立文件不存在跨文件原子事务。D-19 只应声称 PPTX 单文件原子替换。双产物按固定 commit order 独立原子发布；建议先 Markdown、后 PPTX，以 PPTX 替换作为“deck ready”提交点，并在文档中明确 crash window。

### 2.6 独立 gate 脚本模式

`verify_markdown_contract.py` 是 Phase 43 verifier 的直接模板：

```python
def run(*args: str, expected: int | None = None):
    result = subprocess.run(
        [str(PUBLIC_CLI), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    ...
    require("Traceback" not in result.stdout + result.stderr, ...)
    return result
```

其验证模式值得照搬：

- 黑盒调用公共 CLI，而非只调内部函数；
- `tempfile.TemporaryDirectory(prefix=...)` 隔离全部证据；
- `file_hashes()` / `tree_snapshot()` 验证确定性和 caller-owned 文件未变；
- 首次/二次运行比较产物与 terminal summary；
- positive + aggregate-negative + collision + resource + regression；
- 用 hook 注入 publish 窗口故障；
- 失败输出上限与“No Traceback”断言；
- gate registry 固定名称、无重复、fixture command 必须实际调用。

Phase 43 不应把所有测试塞进一个函数。建议至少注册：

```text
pagination_unit_gate
manifest_renderer_contract_gate
full_fixture_structure_gate
best_effort_gate
publication_safety_gate
determinism_gate
phase_41_42_regression_gate
```

## 3. 分页器的仓库适配模式

仓库没有现成 PPTX 分页器，最接近的可复用“模式”是 Phase 42 模型的稳定、source-located、可序列化结构和 verifier 的确定性断言。因此 Phase 43 应把算法新复杂度关进纯模块。

### 3.1 物理计划应是 frozen data，而不是 shape side effect

建议最小类型：

```python
@dataclass(frozen=True)
class PhysicalSlide:
    logical_index: int
    physical_index: int
    layout: str
    title: str | None
    fragment_index: int
    fragments: tuple[BlockFragment, ...]
    notes_markdown: str | None
    source_line: int

@dataclass(frozen=True)
class PhysicalDeckPlan:
    slides: tuple[PhysicalSlide, ...]
    diagnostics: tuple[RenderDiagnostic, ...]
```

选择 frozen dataclass 与当前 `SourceLocation(frozen=True)` 一致，同时避免 emitter 回写分页决定。测试应把 plan 转成稳定 JSON-compatible dict，重复调用直接比较 equality；不要要求最终 PPTX ZIP bytes 完全一致，因为 Office package relationship id/metadata 可能随库版本变化，结构确定性应比二进制确定性更重要。

### 3.2 全局均衡用统一 contiguous partition primitive

目录和时间线共享“有序 items → 连续 k 分区 → lexicographic cost”模式，不要分别实现贪心尾页修补。统一 helper 应接收：

- item visual weights；
- page capacity；
- min items/page（timeline 通常 3；contents 由 orphan 规则决定）；
- cost tuple builder；
- stable tie-break（最早分割点）。

cost tuple 依照 UI/Research：

```text
capacity violations
-> forbidden orphan count
-> max item-count difference
-> visual-weight variance
-> total unused height
-> earliest stable split points
```

测试不能只覆盖最后两页，必须使用 3+ 页构造证明上上一页会同步调整，并断言每页 item count、weight、顺序与稳定 split points。

### 3.3 测量是保守估算器，不是 PowerPoint autofit

建议 `TextMeasure` 返回 `display_lines`、`height_emu`、`break_opportunities`。manifest 的 min/max font size 是硬边界。正文、列表、code、cell 共用测量 primitive，但分别提供拆分策略：

- paragraph：句末 → 弱标点 → grapheme-safe hard split；
- list：item boundary，单个超大 item 才进入 paragraph splitter；
- code：source line boundary，单行只计算 soft-wrap display lines；
- table：每行高度取 cells 最大值 + margins，并对整页/整表搜索字号；
- contents/timeline：item weight 用实际 wrapped height。

不要调用 `TextFrame.fit_text()` 作为分页权威；research 已确认其 whitespace tokenizer 不适合无空格中文，且统一 apply fit 会破坏 mixed bold/highlight run。

## 4. 发射器与可编辑对象模式

### 4.1 layout 解析按 OOXML part path

`template_report.load_shape_index()` 已展示 ZIP 中按 `ppt/slideLayouts/slideLayout*.xml` 建索引。emitter 应把 presentation 的 slide layout partname 映射为对象，再按 manifest `pptx_layout` 选择；禁止按本地化 layout name 或 `prs.slide_layouts[7]` 猜测。

模板有五张 seed slides，且两张已有 notes relationships。bootstrap 必须先受控移除全部 seed slides，再创建 plan slides；否则会污染 slide count、可见内容和 no-accidental-notes contract。

### 4.2 原生对象 helper 的职责应窄

`pptx_objects.py` 建议每个 helper 只做一个对象契约：

- `add_rich_text(...)`：同一 text frame 内写 plain/bold/highlight runs；
- `add_native_table(...)`：`slide.shapes.add_table()`，显式列宽/行高；
- `add_contained_picture(...)`：计算 contain box，`add_picture()`，crop 全 0；
- `add_gallery_group(...)`：picture + 永远存在的 caption text box；
- `add_timeline_node_group(...)`：marker/time/title/description group，axis 在组外；
- `set_notes_if_present(...)`：只有非空 notes 才访问 `slide.notes_slide`；
- `add_missing_media_placeholder(...)`：本地 native shapes，不联网、不读取未授权路径。

空 caption/table-name placeholder 必须拥有稳定 shape name（例如 `school-pptx:caption-placeholder`），文本为空，不写 UI prompt。结构 verifier 通过 shape name + object type 检查“空对象存在”，而不是只查可见文本。

### 4.3 OOXML helper 必须隔离和结构测试

run highlight 没有 `python-pptx 1.0.2` public API，`pptx_ooxml.py` 可写一个局部 helper，在 run properties 下添加标准 `<a:highlight>`，颜色引用 manifest theme scheme token。该模块不能顺便处理普通文本、颜色或几何。

每个 OOXML helper 都需要：

- 二次调用幂等；
- 保存后 ZIP/XML 存在目标节点；
- `python-pptx` 成功 reopen；
- 不删除 bold `b="1"` 或纯文本；
- 不硬编码 RGB；
- PowerPoint/WPS 视觉与编辑行为留给 Phase 44，不在 Phase 43 宣称完成。

## 5. 其他技能 analog：可借鉴与不可照搬

`end-of-term-teaching-materials/scripts/end_of_term/_engine.py` 的 `deliver()` 展示了另一种清晰的 pipeline：parse → validate → generate → verify calculated artifacts → compile → return stable artifact map；`main()` 只在顶层捕获 domain error，打印一行 bounded stderr 并返回 1。这支持 Phase 43 将编排放在 Python 顶层、helper 抛 domain exception 的做法。

但其发布实现不适合照搬：它在生成前直接 `unlink()` 已有 public files（L1381-L1385），随后直接写 Markdown/Typst/XLSX/PDF。若中途失败，旧产物会丢失，违反 D-19。Phase 43 只能借鉴 pipeline/exception boundary，必须使用 school-pptx 的 descriptor + staged replace 模式。

`school-presentation` 的 public `render.py` / `verify.py` 只是从单体 `_engine.py` re-export；这说明兼容 shim 可保持稳定 import surface，但其巨大 engine 结构不是 Phase 43 模板。Phase 43 research 已明确按 model/paginate/emit/objects/ooxml 拆分，更适合测试和风险隔离。

## 6. 验证矩阵与具体断言

### 6.1 纯分页 gate

- 完整 block 优先；只有单 block 超整页才 split；
- paragraph 先句末，再弱标点，最后 grapheme-safe；
- list 默认只在 item boundary；
- code 只在 source line boundary，原 text/newline round-trip；
- `###` 每 fragment 重复，无“续”；所有物理页复用原 `##`；
- table data row intact、header repeat、table name continuation 仅 authored name；
- table font search 可选择更大字号消除视觉孤行；
- timeline/contents 3+ 页 global balance，不只是末两页；
- gallery chunk：1/2/3/4/5/6/8/9；空 caption 仍有 slot metadata；
- image-text 多图和正文分页的组合关系稳定；
- notes 复制到所有派生页；无 notes 不产生 notes intent；
- repeated run 的 plan equality。

### 6.2 PPTX 结构 gate

同时用 `zipfile` 和 `python-pptx` reopen，断言：

- ZIP 非空、package 可重开；
- seed sample text 不存在，closing 恰好一次；
- slide layout relationship 与 manifest part path 一致；
- visible text 是 native text frames/runs；
- table page 有 `<a:tbl>`，行/列与 header/data 对应；
- media relationship 有效、picture crop 四向为 0；
- timeline/gallery 存在 `<p:grpSp>` 且 children 类型正确；
- 空 caption/table-name text box 依旧存在且 text 为空；
- highlight 使用 scheme color，bold run 保持；
- notes relationships 只出现在 plan 标注页；
- code exact text round-trip；
- 不存在 full-slide screenshot shortcut。

### 6.3 CLI 与发布 gate

- help literal 包含 `render --input ... --out-dir ... [--stem ...]`；
- 成功目录恰好 `<stem>.md`、`<stem>.pptx`，Markdown bytes 与输入完全相同；
- caller-owned 其他文件/目录 hash 不变；
- missing-media/invalid Markdown 仍发布结构有效同名 PPTX，但退出非 0，stdout/stderr 明确异常与受影响 slide；
- best-effort 结果不含 warning slide/banner/watermark；
- staged package corruption / dependency missing 不替换旧 PPTX；
- root exchange、destination symlink、directory collision、input/output identity 均 fail closed；
- 不遗留 `.tmp-*`、`.bak`、JSON、manifest copy、log、debug/evidence；
- 失败无 traceback，诊断有长度上限；
- Phase 41 `template-report` 与 Phase 42 `contract` / `fixture-example` 回归仍通过。

## 7. 主要风险与规划约束

| 风险 | 具体表现 | 应在计划中锁定的缓解 |
|---|---|---|
| manifest 与模板漂移 | 新增 `table_name`/gallery preset 后 YAML 可读但 shape 映射无效 | 先改 contract + template-report validator/evidence，再写 emitter；43-01 gate 阻断后续 |
| closing mapping 错误 | 当前 manifest 指向 cover layout，而实际 closing seed 使用 `slideLayout7.xml` | 关系级断言，不用 layout name/index；full fixture 查 closing 外观留 Phase 44 |
| seed slides/notes 泄漏 | 直接 append 导致 5 张样例页和 2 个 notes relationship 留在成品 | bootstrap 单测：初始 slide 全移除；无 notes 页不得访问 `notes_slide` |
| 中文测量漂移 | 无空格中文被当一词；PowerPoint/WPS 换行差异 | CJK-aware 保守 estimator、明确 font bounds、结构 gate + Phase 44 viewer UAT |
| mixed run 被破坏 | autofit 统一重写 bold/italic；highlight 丢失 | 不调用 `fit_text()`；先 plan 字号；OOXML round-trip 检查 bold/highlight |
| group 跨 viewer 差异 | group 可生成但 WPS 编辑体验不同 | Phase 43 只验证 native `<p:grpSp>` 结构与 reopen；PowerPoint/WPS 手测延期 Phase 44 |
| 表格孤行算法局部化 | 单 cell 后处理导致整表高度变化、跨页溢出 | 字号/行高候选以整张表、全部页面共同评分 |
| 全局均衡退化为尾页修补 | 目录/时间线出现长短页交替 | 统一 ordered DP；三页以上 fixture；cost tuple 与 tie-break 固定 |
| best-effort 被误报成功 | 文件存在导致 agent 只说“已生成” | CLI 状态枚举 + 非零码 + 固定异常摘要；测试明确禁止“渲染成功”文案 |
| 两文件伪原子承诺 | crash 位于 Markdown 与 PPTX 两次 replace 之间 | 文档声明 individually atomic；固定 commit order；旧 PPTX 只在 staged PPTX 验证后替换 |
| 直接复用 example publisher 过度耦合 | `EXAMPLE_OWNED_PATHS` 与 media 子目录规则不匹配 render | 抽取同模式 renderer publisher 或新建专用类；复用安全原则，不复用示例领域名称 |
| 最终 PPTX 二进制不稳定 | ZIP timestamps/relationship ids 影响 hash | plan equality + semantic package inventory 为确定性权威；仅在确认库输出稳定后比较 PPTX bytes |
| 依赖缺失 | 当前 host 未安装 `python-pptx` | render 启动时 bounded dependency diagnostic；不得 traceback；aggregate readiness 属于 Phase 44 |

## 8. 推荐实施顺序

1. **契约先行：** manifest、template-contract、template-report validator/evidence、closing mapping、依赖边界。
2. **纯模型与分页：** `pptx_model.py`、`pptx_paginate.py`、CJK measure、unit gates。
3. **原生对象发射：** bootstrap、layout mapping、objects、isolated OOXML、结构 gate。
4. **公共编排与发布：** `pptx_render.py`、shell dispatch、双产物、best-effort 状态、descriptor-safe staged replace。
5. **回归闭环：** full fixture、negative fixture、fault injection、public-root cleanliness、Phase 41/42 regression。

不得反转 1 与 3：在 manifest 尚未拥有空 caption/table-name、gallery/timeline geometry、highlight token 和正确 closing mapping 时，emitter 中任何临时硬编码都会形成第二套视觉契约。

## 9. 映射结论

Phase 43 的新增核心不是“如何从 Markdown 画 PPTX”，而是把已有 logical document 固化为一个可重复验证的 physical plan，再把该计划机械地发射成原生 PPTX 对象。仓库已经提供了四个关键先例：

1. `markdown_contract.py`：canonical、source-located、有界诊断模型；
2. `template_report.py`：manifest 与 OOXML part-path 的结构契约；
3. `verify_markdown_contract.py`：公共 CLI 黑盒、临时目录、确定性、安全故障注入 gate；
4. `SecureExampleDestination`：描述符约束、同目录临时文件、`fsync`、`os.replace` 和目标身份检查。

实现应组合这些模式，而不是从其他技能复制“先删除旧文件、再直接生成”的简化 deliver 流程。这样才能同时满足 editability、global pagination、best-effort 非零语义和旧 PPTX 保全。
