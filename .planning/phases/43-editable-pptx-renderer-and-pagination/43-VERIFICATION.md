---
phase: 43-editable-pptx-renderer-and-pagination
verified: 2026-07-14T14:42:05+08:00
status: gaps_found
score: "28/32 PLAN must-have truth groups verified"
requirements:
  PPTX-01: satisfied
  PPTX-02: satisfied
  PPTX-03: blocked
  PPTX-04: blocked
  PPTX-05: satisfied
  PPTX-06: satisfied
  PPTX-07: satisfied
  PPTX-08: satisfied
  PPTX-09: satisfied
  PPTX-10: blocked
  PPTX-11: satisfied
  PPTX-12: satisfied
  PPTX-13: satisfied
  VER-03: blocked
  SKILL-03: satisfied
gaps:
  - id: R43-C01
    review_id: C-01
    severity: critical
    affects: [PPTX-03, PPTX-10, Plan-06, Plan-08]
    summary: "合法非 code 布局中的 fenced code 仍走富文本规范化，公开 render 成功但静默删除 authored Markdown delimiter。"
  - id: R43-C02
    review_id: C-02
    severity: critical
    affects: [PPTX-04, VER-03, Plan-02, Plan-08]
    summary: "合法仅表头 table 产生空分区，分页器未捕获 ZeroDivisionError，公开命令泄漏 traceback 与绝对路径。"
  - id: R43-W01
    review_id: W-01
    severity: warning
    affects: [VER-03, Plan-05, Plan-08]
    summary: "Pillow DecompressionBombError 在自定义像素检查之前抛出，绕过 PptxObjectError/domain mapping 并泄漏 traceback 与路径。"
human_verification:
  required: false
  deferred_to_phase: 44
  note: "PowerPoint/WPS 的中文换行、视觉均衡、组合编辑与主题保真仍属于 Phase 44；本次 gaps_found 来自确定性源码和黑盒行为，不依赖人工视觉判断。"
---

# Phase 43 Verification Report

**Phase Goal:** Finalized Markdown renders to a non-empty editable PPTX whose physical slides follow the normalized template budgets.

**Status:** `gaps_found`

## Verification Outcome

Phase 43 尚未真正达到最终目标。新鲜权威 `phase-43` aggregate 在当前提交 `bbf6a27` 上全绿，canonical fixture 可生成非空、可重开的 26 张 native-object PPTX，并证明公开双产物、frozen plan/emitter 边界、分页、notes、media、table、closing 与前序回归大体成立。

但 aggregate 未覆盖 `43-REVIEW.md` 的三条合法或可达公开路径。独立黑盒复现确认：非 `code` 布局 fenced code 被静默改写；合法仅表头 table 触发未捕获 `ZeroDivisionError`；高声明尺寸 PNG 触发未映射 `PIL.Image.DecompressionBombError`。因此不能把 aggregate PASS 当作阶段通过。

## Fresh Aggregate Evidence

运行环境：macOS 本机，Python `3.14.6`；依赖从既有 uv cache 通过 `PYTHONPATH` 离线加载：`python-pptx 1.0.2`、`Pillow 12.3.0`、`lxml 6.1.1`、`PyYAML 6.0.3`。未联网、未安装依赖、未创建仓库虚拟环境。

```bash
PYTHONPATH="$HOME/.cache/uv/archive-v0/3UaCURZW721Q9fJj:$HOME/.cache/uv/archive-v0/V3BbfFztllgFv38f:$HOME/.cache/uv/archive-v0/g8iDxaNqOVKE-2u5:$HOME/.cache/uv/archive-v0/I2PFDpRQMCS91p6l" \
python3 skills/school-pptx/scripts/verify_pptx_renderer.py phase-43
```

结果：退出 `0`；`PHASE_43_GATE_ORDER` 的 17 个顶层 gate 全部执行、顺序与 required/called 完全相同、`dynamic_skips=0`。其中 `pagination` 展开执行 3 个子 gate，aggregate 控制台共显示 21 条 PASS。

| Evidence | Fresh result |
|---|---|
| Contract/model | 11 layouts；closing=`slideLayout7.xml`；gallery presets 1..4；frozen/immutable model；5 seed slides。 |
| Pagination | canonical 13 logical -> 26 physical；gallery 9 -> 4/4/1；timeline 分页；table 2 页；目录连续编号。 |
| Native package | 26 slides；115 ZIP entries；125 relationships；10 pictures；2 native tables；18 groups；6 notes；transition=`none`。 |
| Frozen emission | 双栏目标槽为 `L/R/L/R/L`；cover descriptor 长 66；table content budget `4,325,625` EMU；row heights 与成品回读一致。 |
| Publication | 成功产物为同 stem `.md/.pptx`；Markdown bytes 保留；PPTX-last；成功目录无 manifest/log/debug/evidence sidecar。 |
| Security/regression | descriptor race、既有 object error vectors、bounded template reader、determinism、Phase 41/42 回归均通过。 |

## Independent Review Reproduction

三项均通过 public `school-pptx.sh render` 从隔离临时目录黑盒执行，随后按需用 `python-pptx` 重开成品。

### R43-C01 / REVIEW C-01 — CONFIRMED CRITICAL

输入为合法 `title-content` slide，正文只有：

```text
if a == b
return **value**
```

public render 退出 `0` 并打印“渲染成功”；重开 PPTX 后可见文本为 `if a == b\nreturn value`，两个 `**` 被静默删除。`pptx_emit.py` 仅在 `physical.layout == "code"` 时调用 `add_literal_text()`；其他布局中的 `fragment.kind == "code"` 进入 `add_plain_lines()` -> `add_rich_text()` -> delimiter normalization。

这直接违反 Plan 06 “任何代码路径不得调用 rich-text delimiter normalization”，并阻断 PPTX-03/PPTX-10。现有 `code-literal-roundtrip` 只构造 `layout="code"`，因此 aggregate 假绿。

### R43-C02 / REVIEW C-02 — CONFIRMED CRITICAL

输入为 parser 接受、无 validation diagnostic 的标准仅表头表格：

```markdown
| 字段 | 说明 |
|---|---|
```

public render 退出 `1`，但输出完整 traceback、仓库绝对路径和 `ZeroDivisionError: division by zero`。根因是 `data_heights=[]`，`ordered_contiguous_partition()` 返回空 ranges，随后 `loads=[]`，`sum(loads) / len(loads)` 除零。

这说明合法 table 无法渲染，阻断 PPTX-04 与 VER-03；同时 Plan 02 的 native table 数据语义和 Plan 08 的 requirement revalidation 对零数据行边界未成立。

### R43-W01 / REVIEW W-01 — CONFIRMED WARNING

使用低字节、IHDR 声明 `20000x10000` 的 PNG。public render 退出 `1`，输出完整 traceback、仓库/cache 路径和 `PIL.Image.DecompressionBombError`。异常在 `Image.open()` 内、读取 `image.size` 和自定义 `MAX_MEDIA_PIXELS` 判断之前抛出；它不是 `PptxObjectError`，不会被 emitter 或 render 状态机映射。

Pillow 阻止了解压炸弹，但 Plan 05 要求的稳定、bounded、无路径公开错误边界仍被绕过，VER-03 的公开失败行为因此不完整。现有 `object-error-bounded` 只覆盖自定义 format/pixel code，没有 Pillow 自身异常向量。

## Historical Gap Closure Audit

Plan 08 的 `GAP_COVERAGE` 使用了与最新 `43-REVIEW.md` 重名但语义不同的历史标签。以下结论按历史定义核对，不能替代上面的新审查缺口：

| Historical ID | Verdict | Evidence |
|---|---|---|
| C-01 descriptor race | CLOSED | held O_RDWR inode、duplicate fd、replace 前身份检查、sentinel hash 与 inode reclaim gate 通过。 |
| C-02 dedicated code-layout literal | PARTIALLY CLOSED | `layout="code"` 逐字符回读通过；非 code 布局合法 fenced code 未覆盖，故 requirement closure 不完整。 |
| W-01 custom object error mapping | PARTIALLY CLOSED | GIF/自定义 oversized pixel code bounded；Pillow bomb exception 可绕过。 |
| W-02 two-column frozen slots | CLOSED | plan/reopen 均验证 `L/R/L/R/L` 与三张双栏物理页。 |
| W-03 cover slot values | CLOSED | subtitle/metadata descriptor 长 66，低于 72 字符/2 行预算，成品回读一致。 |
| W-04 contents visible numbering | CLOSED | 11 项跨页连续编号，emitter 直接消费 frozen items。 |
| W-05 native table row heights | CLOSED FOR NONEMPTY TABLES | content budget 派生正确，逐行 EMU 高度冻结并回读一致；零数据行仍崩溃。 |
| W-06 template reader bounds | CLOSED | 7 类 public 恶意 package 与四项边界测试通过，canonical 11 layouts 回归通过。 |

## Plan Must-Haves

| Plan | Score | Claimed vs actual |
|---|---:|---|
| 43-01 | 5/5 | manifest-owned geometry、closing part path、frozen model 与 bounded template reader 均有实际证据。 |
| 43-02 | 4/5 | 常规分页、全局均衡、notes 成立；仅表头 table 破坏 D-06/D-07/D-08 的完整数据边界。 |
| 43-03 | 6/6 | native table/group/run/notes、seed 清理、唯一 closing、transition none 对已规划页面成立。 |
| 43-04 | 5/5 | canonical 三态入口、PPTX-last、同 stem 双产物、canonical parser 与 skill-local runtime 成立。 |
| 43-05 | 1/2 | descriptor publication 已关闭；Pillow bomb 绕过 W-01 bounded domain mapping。 |
| 43-06 | 1/2 | 专用 code layout 保真；“任何代码路径”声明被非 code 布局 fenced code 否定。 |
| 43-07 | 3/3 | slot values、visible numbering、非空 table row heights 均冻结并由 emitter 机械消费。 |
| 43-08 | 3/4 | 17-gate registry、debris 语义、Phase 44 边界成立；aggregate 未真正重验上述三条可达路径。 |

**Score:** 28/32 PLAN must-have truth groups verified。

八份 SUMMARY 对 canonical fixture、历史 gap 和各自专项向量的声明大多与实际一致；但 43-06 的“任何代码路径”、43-08 的“全部 gap/blocked requirement 闭环”属于过度声明，43-05 的 bounded object error 声明也只覆盖其既有测试向量。

## Requirement Coverage

| Requirement | Status | Evidence / blocker |
|---|---|---|
| PPTX-01 | SATISFIED | accepted canonical fixture 生成非空、可重开 26-slide PPTX。 |
| PPTX-02 | SATISFIED | 文本、tables、pictures、groups、notes 为 native/editable object；无整页截图。 |
| PPTX-03 | BLOCKED | 非 code 布局的合法 fenced code 文本被静默改写。 |
| PPTX-04 | BLOCKED | 非空表格为 native table 且 row behavior 可预测，但合法仅表头 table 无法规划或发射。 |
| PPTX-05 | SATISFIED | canonical pictures 为 contain placement，crop 为 0；bomb 错误泄漏归入公开错误边界。 |
| PPTX-06 | SATISFIED | gallery 每物理页最多 4 图，超量自动扩页。 |
| PPTX-07 | SATISFIED | horizontal timeline 按全局分区扩页。 |
| PPTX-08 | SATISFIED | canonical 长文本/table/timeline/gallery 按 manifest budget 扩为 26 物理页，frozen mapping 与成品一致。 |
| PPTX-09 | SATISFIED | table continuation 重复 header；仅既有表名添加 `（续）`。 |
| PPTX-10 | BLOCKED | 专用 code layout monospace/editable，但合法非 code 布局代码块不能逐字符保真。 |
| PPTX-11 | SATISFIED | authored notes 传播到派生页；canonical 恰有 6 notes relationships。 |
| PPTX-12 | SATISFIED | transition mode 诚实记录为 `none`。 |
| PPTX-13 | SATISFIED | 成功公开边界固定为同 stem Markdown + PPTX；Markdown bytes 保留，无 sidecar/debris。 |
| VER-03 | BLOCKED | canonical render 可重复且 invalid 非零，但合法仅表头输入崩溃，Pillow bomb 失败未映射为 bounded public domain error。 |
| SKILL-03 | SATISFIED | runtime 实现均位于 `skills/school-pptx/scripts/`，aggregate source audit 未发现 sibling skill call。 |

**Requirements:** 11/15 satisfied，4/15 blocked。

## Boundary Verification

- **公开双产物边界：** canonical success 与非 code fenced-code success 均只发布同 stem `.md/.pptx`；Markdown bytes 原样保留，PPTX 为最后提交点。未发现 public manifest、logical JSON、diagnostics、logs、debug 或 evidence sidecar。
- **Frozen plan/emitter 边界：** `pptx_paginate.py` 不导入 `python-pptx`；plan fields 包含 target slot、visible contents items、slot values、row heights；`pptx_emit.py` 不导入 paginator/measure，canonical 成品与 projection 回读一致。缺口来自 code fragment 路由条件和空 table 边界，不是 emitter 重新分页。
- **人工 UAT 边界：** PowerPoint/WPS 视觉与交互检查属于 Phase 44。本阶段既不要求完成，也未声称已经人工验证。

## Gap-Closure Direction

1. **R43-C01:** 按 `fragment.kind == "code"` 路由 literal emitter，而不是按 physical layout；为 `title-content`、`two-column` 加 parser -> frozen plan -> reopened PPTX 逐字符向量。
2. **R43-C02:** 明确 header-only table 语义：优先规划为仅含 header 的单页 native table；若产品契约选择禁止，则 parser 必须给出可定位、bounded validation diagnostic。两种方案都需 public CLI 与 row-height 回读回归。
3. **R43-W01:** 在 `_safe_image_size()` 捕获 Pillow identification/decompression-bomb/decode exceptions，统一映射稳定 `PptxObjectError`；新增低字节高声明尺寸 public 黑盒 gate，并断言无 traceback、绝对路径或 Pillow 内部信息。
4. 更新 `code-literal-roundtrip`、`object-error-bounded`、table structured gate 与 `GAP_COVERAGE`，使 aggregate 对以上路径真正 blocking，而不是只声明 requirement coverage。

## Verification Complete

Phase 43 的 canonical aggregate 与大部分 frozen/native/publication 契约通过，但 2 个 Critical 和 1 个 Warning 均独立复现，且分别破坏代码文本保真、合法 table 渲染和公开错误边界。最终状态为 `gaps_found`，score 为 `28/32`；修复后必须重新运行 aggregate 与三条定向黑盒复现。

---
*Verified: 2026-07-14T14:42:05+08:00*
*Verifier: Codex gsd-verifier subagent*
