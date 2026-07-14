---
phase: 43-editable-pptx-renderer-and-pagination
verified: 2026-07-14T07:10:00+08:00
status: gaps_found
score: "17/21 must-have truth groups verified"
requirements:
  PPTX-01: satisfied
  PPTX-02: satisfied
  PPTX-03: blocked
  PPTX-04: blocked
  PPTX-05: satisfied
  PPTX-06: satisfied
  PPTX-07: satisfied
  PPTX-08: blocked
  PPTX-09: satisfied
  PPTX-10: blocked
  PPTX-11: satisfied
  PPTX-12: satisfied
  PPTX-13: satisfied
  VER-03: satisfied
  SKILL-03: satisfied
gaps:
  - id: C-01
    severity: critical
    affects: [D-19, Plan-04-publication-safety]
    summary: "staged PPTX 关闭受控描述符后按可交换路径保存，符号链接竞态可先覆盖外部文件，再被事后 inode 检查发现。"
  - id: C-02
    severity: critical
    affects: [D-03, PPTX-03, PPTX-10]
    summary: "代码页经过 Markdown 富文本归一化，静默删除代码中的 == 与 ** 分隔符并错误添加样式。"
  - id: W-01
    severity: warning
    affects: [D-17, D-19, Plan-04-bounded-errors]
    summary: "PptxObjectError 未映射为 bounded domain error；非法媒体可向公开 CLI 泄漏 traceback 和内部路径。"
  - id: W-02
    severity: warning
    affects: [PPTX-03, PPTX-08, two-column-must-have]
    summary: "two-column 只使用 left_body，右栏内容归属未进入计划或发射。"
  - id: W-03
    severity: warning
    affects: [PPTX-03, cover-content]
    summary: "cover 只发射 title；subtitle 及约定封面元数据未进入成品。"
  - id: W-04
    severity: warning
    affects: [D-10, PPTX-03, PPTX-08]
    summary: "contents 连续编号只存于 fragment metadata，成品目录可见文本没有编号。"
  - id: W-05
    severity: warning
    affects: [D-08, PPTX-04, PPTX-08]
    summary: "分页器测得的逐行表格高度未冻结到计划，发射器改用平均行高，可能重新引入截断或溢出。"
  - id: W-06
    severity: warning
    affects: [Plan-01-template-ZIP-XML-security]
    summary: "公开 template-report 对可指定 PPTX 直接无上限解压和 XML 解析，现有安全负例未覆盖生产 reader。"
human_verification:
  required: false
  deferred_to_phase: 44
  note: "PowerPoint/WPS 中的实际中文换行、视觉均衡、组合编辑与主题保真仍按边界留给 Phase 44；当前自动与源码证据已足以判定 gaps_found。"
---

# Phase 43 Verification Report

**Phase Goal:** Finalized Markdown renders to a non-empty editable PPTX whose physical slides follow the normalized template budgets.
**Status:** `gaps_found`

## Verification Outcome

Phase 43 尚未真正达到阶段目标。新鲜运行的权威 `phase-43` 聚合门全绿，证明 canonical fixture 能生成 24 张非空、可重开的物理页，并包含 native table、picture、group、notes、正确布局关系、零 seed 泄漏和唯一末页 closing；但该聚合门未覆盖 `43-REVIEW.md` 已指出的核心路径。

两个 Critical 均经独立行为复现确认：发布竞态会在命令最终报 `OUTPUT_TEMP_CHANGED` 前覆盖 caller-owned 外部文件；代码页会把 `if a == b == c` 和 `return **value**` 静默改成 `if a  b  c` 和 `return value`。这分别直接违反 D-19 与 D-03/PPTX-10，不能因现有测试通过而豁免。

## Fresh Gate Evidence

隔离依赖使用本机 uv cache 中现有 `python-pptx 1.0.2` 与 `lxml 6.1.1`，复用系统 Pillow/PyYAML；未联网安装依赖，也未在仓库创建虚拟环境。

| Gate / evidence | Result |
|---|---|
| `verify_pptx_renderer.py phase-43` | PASS；14 个内部/命名 gate 按固定顺序执行，无 skip。 |
| Contract/model | 11 layouts；closing=`slideLayout7.xml`；gallery presets 1..4；highlight=`accent6`；5 seed slides；模型 frozen/deterministic。 |
| Pagination | canonical 13 logical -> 24 physical；gallery 9 -> 4/4/1；table 2 页；timeline 3/3/3/3/3；contents 5/5/4。 |
| Emit/package | 24 slides；111 ZIP entries；121 relationships；10 image relationships；2 native table slides；18 groups；6 notes slides；transition=`none`。 |
| Publication | 成功目录为同 stem `.md/.pptx`；Markdown bytes 保留；best-effort 非零；旧 PPTX corruption/crash-window/root-exchange 既有负例通过。 |
| Determinism/regression | physical plan SHA-256 稳定；semantic inventory 重复一致；Phase 41 template-report 与 Phase 42 fixture-example 通过。 |

聚合门第一次在直接继承隔离 `PYTHONPATH` 时停在“dependency absence”测试，因为该负例错误继承了父进程依赖；使用验证专用临时调度器只让该负例回到无 `python-pptx` 的宿主解释器后，完整聚合通过。临时调度器已删除，仓库未被污染。

## Plan Must-Haves

| Plan | Verified | Gaps |
|---|---:|---|
| 43-01 | 5/5 | manifest 空槽、closing part path、gallery/timeline geometry、theme highlight、frozen model 均有新鲜 gate 证据；但其 threat model 的生产 template ZIP/XML 上限被 W-06 破坏。 |
| 43-02 | 2/5 | complete-block/grapheme 分割与 notes propagation 成立；代码往返（C-02）、table 测量到发射（W-05）、contents 可见连续编号（W-04）不成立。 |
| 43-03 | 6/6 | native table/group/run/notes、seed 清理、唯一 closing、transition none 的结构断言通过；不过 code 使用 rich-text helper 的跨层 wiring 使 PPTX-10 仍失败。 |
| 43-04 | 4/5 | 双产物、PPTX-last 诚实边界、canonical imports 与 skill-local runtime 成立；D-19 held-descriptor publication 被 C-01 直接否定。 |

**Score:** 17/21 PLAN frontmatter truth groups verified。该分数不将 threat-model 与 requirements 缺口伪装为通过。

## Requirement Coverage

| Requirement | Status | Evidence / blocker |
|---|---|---|
| PPTX-01 | SATISFIED | canonical fixture 生成非空、可重开 24-slide PPTX。 |
| PPTX-02 | SATISFIED | 文本、table、picture、group、notes 均为 native 对象，无整页截图。 |
| PPTX-03 | BLOCKED | code 文本被改写；cover subtitle/metadata 丢失；two-column 右栏未使用。 |
| PPTX-04 | BLOCKED | native `<a:tbl>` 存在，但逐行测量高度未进入模型，成品所有行被平均分高，不能证明 predictable row behavior/budget。 |
| PPTX-05 | SATISFIED | 10 个有效图片关系，contain placement，crop 四值为 0。 |
| PPTX-06 | SATISFIED | gallery 每页 <=4，9-item 向量为 4/4/1，card 为 native group。 |
| PPTX-07 | SATISFIED | timeline 水平且长序列分成额外物理页，node groups 与独立 axis 存在。 |
| PPTX-08 | BLOCKED | pure plan 会扩页，但 table 行高、two-column slot 和 contents 可见编号未机械落实，不能证明物理页都遵守预算。 |
| PPTX-09 | SATISFIED | table 续页重复 header；仅已有表名加 `（续）`；其他续页无可见 `续`。 |
| PPTX-10 | BLOCKED | monospace shape 存在，但源码 `==`/`**` 不能逐字符往返。 |
| PPTX-11 | SATISFIED | canonical 成品恰有 6 notes relationships；无 notes intent 不创建 notes part。 |
| PPTX-12 | SATISFIED | transition mode 明确为 `none`，无 transition XML。 |
| PPTX-13 | SATISFIED | 成功公开产物固定为同 stem Markdown + PPTX，Markdown bytes 不变，无公开 sidecar/debris。 |
| VER-03 | SATISFIED | public `render` 可重复；canonical 成功为 0，invalid/missing-media 为非零。bounded traceback 属额外安全 gap W-01。 |
| SKILL-03 | SATISFIED | 六个 `pptx_*.py` 均在 skill-local scripts，source audit 未发现 sibling skill runtime call。 |

**Requirements:** 11/15 satisfied，4/15 blocked。

## Review Findings Reverification

| Finding | Verdict | Fresh evidence |
|---|---|---|
| C-01 staged PPTX symlink TOCTOU | CONFIRMED, BLOCKING | `reserve_pptx()` 在 `pptx_render.py:186-189` 关闭 fd；`emit_deck()` 在 `pptx_emit.py:174` 按路径 save。故障注入在 save 前把 temp 换成指向 sentinel 的 symlink：命令返回 1/`OUTPUT_TEMP_CHANGED`，但 sentinel 已从 12 bytes 变为 432322-byte PPTX。 |
| C-02 code rich-text mutation | CONFIRMED, BLOCKING | `pptx_emit.py:158` 对 code 调 `add_plain_lines()`，后者在 `pptx_objects.py:82-90` 调 `add_rich_text()`/`inline_spans()`。黑盒成品不含源码向量，含删除运算符/分隔符后的 mutated vector。 |
| W-01 unbounded object errors | CONFIRMED | valid local GIF 触发 `PPTX_MEDIA_FORMAT_INVALID`，public CLI 退出 1 但输出 Python traceback 与绝对内部路径；`PptxObjectError` 未被 render 三态捕获。 |
| W-02 two-column left-only | CONFIRMED | canonical 可重开 PPTX 的双栏页只有 `school-pptx:left_body`，五个块全部在左栏，未出现 renderer-owned right-body shape。 |
| W-03 cover content loss | CONFIRMED | canonical 封面 renderer-owned shape 只有 title；模板 `Subtitle 2` 为空，YAML subtitle/school/department/author/date 均未发射。 |
| W-04 contents numbering ignored | CONFIRMED | plan 有 `number_start/number_end`，但 canonical contents 可见文本从“一、课程建设目标”开始，没有 `1.`；emitter 只拼接 `fragment.items`。 |
| W-05 table row heights discarded | CONFIRMED | paginator 在 `pptx_paginate.py:481-496` 测每行高度，但 fragment 不携带高度；canonical 两张 table 的每页所有 row height 分别统一为 617946/540703 EMU。 |
| W-06 template-report unbounded ZIP/XML | CONFIRMED | `template_report.py:62-95` 对 public `--template` 使用 `namelist()` + `read()` + `ET.fromstring()`，未检查 entry count、单项/总解压预算、重复路径或实体；verifier 的安全 helper 不是该生产函数。 |

## Goal-Level Gaps

1. **安全发布不成立（C-01）**：把 staged PPTX 全程绑定到 held descriptor，或使用不可交换私有目录和 descriptor-relative 安全复制；新增 reserve 后/save 前 symlink exchange 黑盒门，并断言外部 sentinel byte-identical。
2. **代码文本保真不成立（C-02）**：代码使用不调用 `inline_spans()` 的纯文本 emitter；加入 `==`、`**`、连续星号、原始换行/空白的 reopen 逐字符断言。
3. **物理页没有完全机械落实计划预算（W-02/W-04/W-05）**：模型必须携带左右栏归属、目录展示编号和逐行 table heights，emitter 只消费这些冻结决定。
4. **内容完整性不足（W-03）**：cover subtitle 与约定 metadata 必须有 manifest-owned slot/组合规则和 reopen 文本断言。
5. **失败与模板读取边界不完整（W-01/W-06）**：统一映射 `PptxObjectError` 为 bounded domain error；生产 template-report 使用有界 ZIP/XML reader，并由 public 命令负例覆盖。

## Commands Run

```bash
# 当前权威 Phase 43 aggregate；依赖来自已有本机 cache，无网络安装
PATH="<temporary-verifier-bin>:/usr/bin:/bin" \
PYTHONPATH="$HOME/.cache/uv/archive-v0/3UaCURZW721Q9fJj:$HOME/.cache/uv/archive-v0/g8iDxaNqOVKE-2u5" \
/opt/homebrew/bin/python3 \
  skills/school-pptx/scripts/verify_pptx_renderer.py phase-43

# 专项行为复现（TemporaryDirectory）
# 1. canonical public render + python-pptx reopen/object inventory
# 2. code `==`/`**` round-trip vector
# 3. reserve 后/save 前 symlink exchange + outside sentinel hash/size
# 4. local GIF object-error public CLI traceback

# 源码与适用规范核对
python3 -m py_compile skills/school-pptx/scripts/pptx_*.py
rg -n 'reserve_pptx|presentation.save|add_plain_lines|right_body|number_start|row.height|load_shape_index' \
  skills/school-pptx/scripts
```

## Phase Boundary

PowerPoint/WPS 人工视觉与交互 UAT 仍正确留在 Phase 44；本报告不把未执行的 viewer 检查伪称完成。当前 `gaps_found` 来自确定性源码、黑盒 CLI 和可重开 PPTX 证据，不依赖人工视觉判断。

## Verification Complete

Phase 43 自动聚合门通过，但阶段目标因 C-01、C-02 及六项已确认 Warning 未达成。应先形成 gap-closure plans，修复后重新运行 aggregate 与本报告列出的专项复现。

---
*Verified: 2026-07-14T07:10:00+08:00*
*Verifier: Codex gsd-verifier subagent*
