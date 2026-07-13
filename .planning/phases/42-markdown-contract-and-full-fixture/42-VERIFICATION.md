---
phase: 42-markdown-contract-and-full-fixture
verified: 2026-07-13T17:06:20Z
status: gaps_found
score: 9/14 must-haves verified
---

# Phase 42: Markdown Contract and Full Fixture Verification Report

**Phase Goal:** 教师与 agents 拥有一个可审阅的 Markdown 契约，能表达完整逻辑 deck 而不暴露 PPTX 坐标或样式。
**Verified:** 2026-07-13T17:06:20Z
**Status:** gaps_found

## Verification Outcome

Phase 42 的公开契约、canonical fixture、四个本地媒体、`validate`、`example`、`template-report` 与 `info` 主路径均存在且可运行；ROADMAP 的 5 条用户可观察成功标准也都有正向证据。然而，独立负例确认 `42-REVIEW.md` 的 5 个 warning 全部真实可复现，其中 W-01 至 W-04 直接违反 Phase 42 已锁定的解析、fenced-code、完整表格、确定性 JSON 和有界内部错误 must-haves，W-05 违反 `example` 的固定写入边界与 symlink escape 防护承诺。

因此不能仅凭权威门禁 PASS 宣称 Phase 42 已达到“Phase 43 可直接把该逻辑模型作为唯一输入”的完成条件。

## Goal Achievement

### ROADMAP Success Criteria

| # | Success criterion | Status | Evidence |
|---|---|---|---|
| 1 | 可读契约明确十个 YAML 字段与 `::: slide {layout="..."}` | ✓ VERIFIED | `references/markdown-contract.md` 列出唯一十字段白名单、只允许必填 `layout`，并拒绝公开 `id` 与显式 `closing`。 |
| 2 | 完整 fixture 覆盖 11 个布局语义、notes、媒体、表格、timeline、gallery、code 与 overflow | ✓ VERIFIED | canonical JSON 含 13 个逻辑 slide、10 个不同显式布局和 1 个 implicit closing；fixture 含 2 个 notes、10 个图片引用、长表格、12 项 timeline、6 图 gallery 和长 code。 |
| 3 | contents 由有效 `##` 按源码顺序生成，`#` 只作缺失 YAML title 时的 fallback | ✓ VERIFIED | canonical JSON 的 `document_title` 为 YAML title，`contents_entries` 为 11 个 `##` 标题且顺序与源码一致；契约和门禁覆盖 title fallback。 |
| 4 | unsupported layout、坐标样式、font/color、raw HTML、missing media 给出可定位错误 | ✓ VERIFIED | 独立聚合负例退出 1，并分别产生 `LAYOUT_UNKNOWN`、`UNSUPPORTED_STYLE`、`RAW_HTML`、`MEDIA_MISSING`；每项含 1-based 行列、slide、layout 和 fix。 |
| 5 | notes 与普通 Markdown 图片可表达，notes 不进入可见 slide blocks | ✓ VERIFIED | canonical JSON 将 notes 存为 slide 独立字段；对应 slide 的 visible `blocks` 不含 notes。图片均为普通 `![alt](path)`，相对 fixture 目录解析。 |

**ROADMAP success criteria:** 5/5 verified。

### Plan Must-Haves

两个计划 frontmatter 共 14 个 truth groups；其中 9 个完整成立，5 个因可复现缺口不能验证：

| Plan truth group | Status | Reason |
|---|---|---|
| 42-01 D-01/D-04 slide opener 与唯一 public layout 属性 | ✓ VERIFIED | public `id`、未知属性、缺失 layout、unknown layout、explicit closing 均失败。 |
| 42-01 D-02/D-03 YAML/title/contents | ✗ GAP | W-01：YAML 公共 formatter 值未限制或规范化为 JSON-safe string；未加引号日期可先“校验通过”，请求 JSON 时再 traceback。 |
| 42-01 D-05/D-06 完整顶层块与 two-column 配对 | ✗ GAP | W-03：没有合法 Markdown 分隔行的伪表格仍被接受；普通 table/timeline 也不校验行列宽一致，不能保证“完整表格块”。 |
| 42-01 D-07/D-08/D-09/D-10 expansion inputs | ✓ VERIFIED | 逻辑模型保留预算、长文本、column pairs、stable body/images、table title 和 overflow evidence，未生成物理页。 |
| 42-01 D-11/D-12/D-13/D-14 notes/media | ✓ VERIFIED | notes 独立且 last-only；媒体保留 authored/resolved path、caption、contain、existence 与安全 placeholder，缺失媒体非零。 |
| 42-01 D-15/D-16/D-17 聚合验证、fence opacity 与 emphasis | ✗ GAP | W-02：slide 外层收集器在 fenced code 中遇到独立 `:::` 会提前闭合容器并截断合法代码，违反“fenced code 内容完全不透明”。 |
| 42-01 manifest-driven 10 explicit + 1 implicit closing | ✓ VERIFIED | 布局来自 manifest；coverage 精确为 10 显式 + 1 implicit closing；显式 closing 被拒绝。 |
| 42-01 invalid input/JSON/internal failure truthfulness | ✗ GAP | W-01 与 W-04：JSON 序列化和 manifest 加载异常均泄露完整 traceback；前者还让同一输入随 `--out-json` 改变结果。 |
| 42-02 D-18 coherent curriculum narrative | ✓ VERIFIED | fixture 是完整的智能制造课程建设叙事，不是可见 layout test matrix。 |
| 42-02 D-19 full semantic/overflow coverage | ✓ VERIFIED | 长文本、奇数 two-column blocks、多图 image-text、长 table/timeline/code、>4 gallery、notes、caption 与空 caption 均存在。 |
| 42-02 D-20 deterministic fixed ownership | ✗ GAP | W-05：preflight 后交换 `media/` 为外部 symlink，再执行 replace，可在 `--out-dir` 外写入同名文件。 |
| 42-02 all media self-contained | ✓ VERIFIED | 4 个 PNG 均为有效 1200×675 RGBA，哈希各异；fixture 无网络、home、绝对或兄弟 skill 路径。 |
| 42-02 no authored closing / 11 semantics | ✓ VERIFIED | fixture 无 explicit closing；逻辑模型含唯一 end-of-deck implicit closing。 |
| 42-02 parser-verifiable order/notes/media/overflow | ✓ VERIFIED | canonical JSON 对 contents、notes、caption/path 和各类 overflow evidence 均可机器检查。 |

**Score:** 9/14 must-have truth groups verified。

## Required Artifacts

| Artifact | Status | Evidence |
|---|---|---|
| `skills/school-pptx/references/markdown-contract.md` | ✓ SUBSTANTIVE | 127 行；完整描述 YAML、slides、blocks、layouts、notes、media、diagnostics 和 Phase 43/44 边界。 |
| `skills/school-pptx/scripts/markdown_contract.py` | ⚠ EXISTS + GAPS | 776 行；提供 reusable parse/validate/model/example，但存在本报告 5 个可复现缺口。 |
| `skills/school-pptx/scripts/school-pptx.sh` | ✓ WIRED | 公开 dispatch `validate`、`example`，并保留 `template-report`、`info` 与 help。 |
| `skills/school-pptx/scripts/verify_markdown_contract.py` | ⚠ SUBSTANTIVE + INCOMPLETE | `fixture-example` 全套门禁通过，但未覆盖 YAML 隐式类型、fence 内 directive、非法表格结构、manifest failure 与 TOCTOU。 |
| `skills/school-pptx/fixtures/school-pptx-full.md` | ✓ SUBSTANTIVE | canonical fixture 可通过，含 10 authorable layouts 和完整叙事/overflow 输入。 |
| `skills/school-pptx/fixtures/media/` | ✓ VALID | 4 个有效本地 PNG，均为 1200×675、8-bit RGBA、non-interlaced。 |

## Key Links

| From | To | Status | Evidence |
|---|---|---|---|
| parser | `standard-school.manifest.yaml` | ✓ WIRED | `load_manifest()` 读取 theme/layout/slots/budgets；canonical JSON 带 manifest budget evidence。 |
| `school-pptx.sh` | parser | ✓ WIRED | public `validate` 与 `example` 都通过 shell wrapper 调用 `markdown_contract.py`。 |
| fixture | `fixtures/media/` | ✓ WIRED | 10 个普通 Markdown image 引用全部解析为存在的本地文件。 |
| verification harness | public commands | ⚠ WIRED BUT INCOMPLETE | subprocess 门禁确实调用公开命令，但未捕获本报告的 5 条回归路径。 |

## Requirements Coverage

| Requirement | Status | Notes |
|---|---|---|
| MD-01 | ✓ SATISFIED | 存在教师可审阅 YAML + explicit slide-block 契约。 |
| MD-02 | ✓ SATISFIED WITH MUST-HAVE GAP | 十个字段白名单准确；字段值类型和 JSON-safe 规范化缺失由 Gap 1 记录。 |
| MD-03 | ✓ SATISFIED | optional metadata 可省略，缺 title 时支持唯一 `#` fallback。 |
| MD-04 | ✓ SATISFIED | contents 由有效 `##` 按源码顺序生成。 |
| MD-05 | ✓ SATISFIED | 明列的 unsupported layout/style/font/color/raw HTML 负例均可定位且非零。 |
| MD-06 | ✓ SATISFIED | full fixture 覆盖 10 explicit + 1 implicit 及要求的所有对象/overflow 类型。 |
| MD-07 | ✓ SATISFIED | notes 使用独立 Markdown 容器并从 visible blocks 隔离。 |
| MD-08 | ✓ SATISFIED | 普通 Markdown media 以 Markdown parent 解析；absolute path 显式保留。 |
| VER-01 | ✓ SATISFIED WITH SAFETY GAP | repeatable `example` 命令存在且正常条件下 deterministic；并发 symlink 写边界缺口由 Gap 5 记录。 |

**Requirement text coverage:** 9/9；但 requirements 的实现质量仍受以下 must-have gaps 阻断。

## Reproduced Gaps

### Gap 1 — YAML 值可使已通过输入无法生成逻辑 JSON

- **Mapped truth:** 42-01 D-02/D-03；invalid YAML/JSON truthfulness；Phase 43 deterministic logical JSON hand-off。
- **Evidence:** `date: 2026-07-13` 不带 `--out-json` 时退出 0 并打印 `校验通过`；同一输入加 `--out-json` 时退出 1，泄露 `TypeError: Object of type date is not JSON serializable` 完整 traceback。
- **Why blocking:** Phase 43 不能假设 `validate` 通过的模型可序列化；输出选项不应改变输入有效性。
- **Suggested fix:** 要求十个 formatter 值均为字符串标量，或在 compose/load 后统一安全规范化；在宣布通过前先完成 JSON serialization；捕获 `TypeError` 并产生有界诊断。加入 date、bool、number、list、mapping 负例。

### Gap 2 — fenced code 内的 `:::` 会改变 slide 结构

- **Mapped truth:** D-05、D-15/D-16/D-17；契约“fenced code 内容完全不透明”。
- **Evidence:** 合法 code slide 的 fence 内仅含一行 `:::` 时，公开 validate 退出 1 并错误报告 `CODE_UNCLOSED`；代码内容被截断。
- **Why blocking:** 教师可表达的合法 code 无法可靠进入完整逻辑 deck；Phase 43 消费的是错误模型。
- **Suggested fix:** slide 收集状态机在解释任何 `:::`, `::: notes`, `::: slide` 前先追踪匹配 fence marker；fence 内逐行原样保留。增加三种 directive 文本回归。

### Gap 3 — 非 Markdown 表格与错列数据会被报告为有效

- **Mapped truth:** D-05 完整 table block；timeline 唯一 canonical Markdown table；D-10 table composite。
- **Evidence:** timeline 的第二行写成 `| broken | separator | row |` 而非 `|---|---|---|`，公开 validate 仍退出 0、错误数 0；实现把伪分隔行降级为数据行。
- **Why blocking:** logical model 不能保证 table/timeline 是契约声称的 Markdown 表格，错误会推迟到 renderer。
- **Suggested fix:** 要求至少 header + separator；每个 separator cell 匹配 `TABLE_SEPARATOR_RE`；所有 data rows 列数严格等于 header。普通 table 与 timeline 都加入缺 separator、错列数负例。

### Gap 4 — manifest 加载失败后仍泄露 traceback

- **Mapped truth:** internal failures bounded/no stack trace；manifest-driven validator key link。
- **Evidence:** 以不存在 skill dir 调用 parser 的 public validate entry point，先打印 `校验失败`，随后因 `manifest` 未赋值在主题输出处触发 `UnboundLocalError` traceback。
- **Why blocking:** 明确的安全/诊断 must-have 未成立，真实 manifest 缺失或损坏时用户得不到完整可执行诊断。
- **Suggested fix:** try 前初始化安全 manifest，或捕获后直接进入统一失败输出并返回；为 missing/malformed/root-invalid manifest 增加 no-traceback 回归。

### Gap 5 — `example` preflight 与 replace 之间存在 symlink TOCTOU

- **Mapped truth:** 42-02 D-20；fixed ownership、collision/escape safety。
- **Evidence:** 独立调用 `prepare_example_destinations(out)` 后，把已检查的 `out/media` 目录替换为指向 `outside` 的 symlink，再调用 `replace_file_safely()`；结果 `outside/equipment-cell.png` 被成功创建且字节与源文件一致。
- **Why blocking:** 在共享或攻击者可写输出树中，命令承诺的“只覆盖 command-owned files / 保留无关路径”并不成立。
- **Suggested fix:** 以已打开目录描述符逐级 no-follow 操作，并在同一目录句柄下创建临时文件与 replace；至少在每次写入前重新验证完整父链并清楚记录并发修改约束。加入受控目录交换测试。

## Positive and Negative Evidence

### Passed

- `python3 skills/school-pptx/scripts/verify_markdown_contract.py fixture-example`：两组 PASS。
- canonical `validate --out-json`：退出 0，0 errors / 0 warnings，10 explicit + 1 implicit。
- `example --out-dir <temp>`：退出 0，只产生 1 个 Markdown + 4 个 PNG。
- `template-report --theme standard-school`：退出 0。
- `info`：退出 0，打印 skill-local PPTX 与 manifest。
- 聚合必需负例：unknown YAML、unknown layout、public `id`、raw HTML、style/color、missing media 同时报告 6 个可定位错误并退出 1。

### Failed Expectations

- YAML implicit date：无 JSON 时误报通过；有 JSON 时 traceback。
- Fence 内独立 `:::`：合法 code 被误判 `CODE_UNCLOSED`。
- 缺 separator timeline：非法输入误报通过。
- Missing manifest：有界 `INTERNAL_ERROR` 后仍触发 `UnboundLocalError` traceback。
- Preflight 后 symlink swap：固定媒体写入逃逸输出目录。

## Human Verification Required

None。上述 gaps 均由确定性最小复现得到，不需要视觉判断。PPTX rendering、notes XML 与 final visual UAT 明确属于 Phase 43/44。

## Gaps Summary

**5 个 must-have gaps，均已独立复现。** 建议在 Phase 43 开始依赖该模型前修复 W-01 至 W-04；W-05 应在继续宣称 `example` 固定写边界前修复。修复后需把五种最小复现纳入 `verify_markdown_contract.py fixture-example` 并重新运行本阶段验证。

## Commands Run

```bash
python3 skills/school-pptx/scripts/verify_markdown_contract.py fixture-example
skills/school-pptx/scripts/school-pptx.sh validate \
  --input skills/school-pptx/fixtures/school-pptx-full.md \
  --out-json /tmp/phase42-canonical.json
skills/school-pptx/scripts/school-pptx.sh example --out-dir <temp>/example
skills/school-pptx/scripts/school-pptx.sh template-report --theme standard-school
skills/school-pptx/scripts/school-pptx.sh info
```

此外使用临时目录构造并运行：YAML implicit date（有/无 JSON）、fence 内 `:::`, malformed timeline、必需聚合负例、missing manifest，以及 preflight 后父目录 symlink swap。所有复现均未修改源码或 canonical fixture。

## Verification Metadata

**Verification approach:** goal-backward，逐项对照两个 PLAN 的 must_haves、Phase 42 五条 success criteria、MD-01..08、VER-01 与 `42-REVIEW.md`。
**Authoritative gate:** PASS，但被独立未覆盖负例推翻“完全完成”结论。
**Human checks required:** 0。
**Source changes:** none；仅新增本验证报告。

---
*Verified: 2026-07-13T17:06:20Z*
*Verifier: Codex gsd-verifier subagent*
