---
phase: 43-editable-pptx-renderer-and-pagination
verified: 2026-07-14T18:09:01+08:00
status: gaps_found
score: "32/37 PLAN must-have truth groups verified"
requirements:
  PPTX-01: satisfied
  PPTX-02: satisfied
  PPTX-03: satisfied
  PPTX-04: satisfied
  PPTX-05: satisfied
  PPTX-06: satisfied
  PPTX-07: satisfied
  PPTX-08: blocked
  PPTX-09: satisfied
  PPTX-10: satisfied
  PPTX-11: satisfied
  PPTX-12: satisfied
  PPTX-13: satisfied
  VER-03: blocked
  SKILL-03: satisfied
gaps:
  - id: R43-C03
    review_id: C-01
    severity: critical
    affects: [PPTX-08, Phase-Goal, Plan-01, Plan-02, Plan-03]
    summary: "mixed-fragment code 按 16pt 分页却在普通 body slot 以 24pt 发射；合法成功成品可在未扩页时静默裁切代码。"
    fix: "在 paginator 中冻结每个正文 target slot 的实际字号并让 emitter 只消费该值，或统一两端字号；加入字号、display height 与扩页 blocking 回归。"
  - id: R43-W02
    review_id: W-01
    severity: warning
    affects: [Plan-08, Plan-09, PPTX-08, VER-03]
    summary: "phase-43 aggregate 的 gap_outcome_audit 使用硬编码成功值，未从 gate evidence 推导，能把未验证属性报告为已验证。"
    fix: "让定向 gate 返回结构化 exit/output/path/height evidence，aggregate 从实际 evidence 校验并复制，不再写死布尔值或向量数。"
  - id: R43-W03
    review_id: W-02
    severity: warning
    affects: [VER-03, Plan-05, Plan-09]
    summary: "图片校验后 add_picture(path) 再次按路径打开文件；校验后替换可抛出未映射 Pillow 异常并绕过 bounded public error。"
    fix: "从同一持有 descriptor 或已验证 bytes 发射图片；至少封装 add_picture 的 Pillow 异常，并增加校验后替换故障注入 gate。"
human_verification:
  required: false
  deferred_to_phase: 44
  note: "PowerPoint/WPS 的中文换行、视觉均衡、组合编辑和主题保真属于 Phase 44；本报告的 gaps 均由确定性源码与自动反例确认。"
---

# Phase 43 Verification Report

**Phase Goal:** Finalized Markdown renders to a non-empty editable PPTX whose physical slides follow the normalized template budgets.

**Status:** `gaps_found`

## Verification Outcome

Phase 43 尚未真正达到最终目标。当前提交 `39568b3` 的权威 `phase-43` aggregate 退出 0，固定 18 个顶层 gate 全部执行、required/called 完全相等、无重复、`dynamic_skips=0`；canonical fixture 可生成可重开的 26 张 native-object PPTX，历史 delimiter、header-only table 和静态 Pillow 错误缺口已关闭。

但最新 `43-REVIEW.md` 的 1 个 Critical 与 2 个 Warning 均可独立确认。最关键的 mixed-code 反例在公开 render 退出 0 时产生超过槽高约 2 倍的代码文本；因此 aggregate PASS 不能证明 normalized template budget 被遵守，阶段目标与 PPTX-08 仍被阻断。

## Fresh Aggregate Evidence

运行环境：macOS，Python `3.14.6`；按 43-09 计划使用既有 uv cache 的离线 `PYTHONPATH`，依赖为 `python-pptx 1.0.2`、`Pillow 12.3.0`、`lxml 6.1.1`、`PyYAML 6.0.3`。未联网、未安装依赖、未创建仓库虚拟环境。

```bash
export PYTHONPATH="$HOME/.cache/uv/archive-v0/3UaCURZW721Q9fJj:$HOME/.cache/uv/archive-v0/V3BbfFztllgFv38f:$HOME/.cache/uv/archive-v0/g8iDxaNqOVKE-2u5:$HOME/.cache/uv/archive-v0/I2PFDpRQMCS91p6l"
python3 skills/school-pptx/scripts/verify_pptx_renderer.py phase-43
```

新鲜结果：退出 `0`；18 个顶层 gate、3 个 pagination 子 gate全部 PASS。canonical evidence 为 13 logical -> 26 physical、115 ZIP entries、125 relationships、10 pictures、2 native tables、18 groups、6 notes、唯一 closing、transition=`none`；公开成功目录只含同 stem Markdown/PPTX，Markdown bytes 保留。

定向历史 gap gates 也重新通过：

| Gate | Fresh result |
|---|---|
| `code-literal-roundtrip` | PASS；title-content/two-column 代码逐字符相等，单槽一个 textbox，monospace runs=2。 |
| `table-header-only` | PASS；public exit 0，1 个物理 table 页，1 行 native table，1 个正 row height。 |
| `object-error-bounded` | PASS；4 个静态向量返回稳定 code，输出 213-229 bytes，旧 PPTX 保留。 |

## Latest Review Reproduction

### R43-C03 / REVIEW C-01 - CONFIRMED CRITICAL

构造合法 `title-content`，正文 fenced code 为 4 行、每行 40 个中文字符，并经 public `school-pptx.sh render` 黑盒执行：

| Evidence | Result |
|---|---:|
| Public exit / summary | `0` / `渲染成功` |
| title-content physical pages | `1` |
| frozen `selected_font_sizes` | `{}` |
| paginator font / display lines | `16pt` / `4` |
| reopened code run font / display lines | `24pt` / `8` |
| emitted display height | `236.4pt` |
| body slot height | `118.125pt` |
| OOXML text equality | `true` |

源码原因明确：`pptx_paginate._fragment_height()` 与 `_code_fragments()` 使用 `font_size_min`；除 table 外，`build_deck_plan()` 不冻结字号；普通 mixed-fragment emitter 缺省回退到 `font_size_max`。文本仍存在于 OOXML 不代表放映可见，实际高度约为槽高的 2.00 倍，违反 D-03 与 PPTX-08 的“软换行计入分页、超量扩页而非溢出/裁切”。现有 gate 只核对字符、字体名和 shape 数，因此未拦截。

### R43-W02 / REVIEW W-01 - CONFIRMED WARNING

`run_phase_43()` 的 `called`/`gap_calls` 能证明 gate 被调用，但 `gap_outcome_audit` 的 `public_success`、`bounded_output` 与 `failure_vectors` 是常量，没有从 `evidence` 读取。实际 aggregate JSON 原样输出这些硬编码值。

这不会单独改变 PPTX，但会把“gate 存在”误报成“具体行为已验证”，并直接掩盖 R43-C03。Plan 09 Task 3 要求 aggregate 从三条 gap 的真实退出码、输出边界、路径与高度证据形成 blocking audit；当前只完成了注册/调用追踪，未完成 outcome audit。

### R43-W03 / REVIEW W-02 - CONFIRMED WARNING

故障注入先让 `_safe_image_size()` 成功校验 1x1 PNG，再在 `slide.shapes.add_picture(str(path), ...)` 前将同一路径替换为声明 `20000x10000` 的 PNG。第二次打开结果：

```text
exception_type: PIL.Image.DecompressionBombError
is_domain_error: false
message: Image size (200000000 pixels) exceeds limit ...
```

因此静态四向量虽通过，校验与发射之间仍存在路径替换窗口。并发可写媒体目录可绕过 `PptxObjectError` allowlist，向 public render 泄漏 Pillow 原文/traceback/绝对路径，阻断 Plan 05/09 的 bounded error 边界与 VER-03。

## Plan Must-Haves

| Plan | Score | Verdict |
|---|---:|---|
| 43-01 | 4/5 | manifest/model/closing 成立；“完整冻结分页决定”缺少正文实际字号。 |
| 43-02 | 4/5 | 常规语义/结构化分页成立；mixed code 的 soft-wrap 未按实际发射字号计入。 |
| 43-03 | 6/6 | native objects、notes、seed cleanup、closing、transition none 均有结构证据。 |
| 43-04 | 5/5 | public command、双产物、PPTX-last 与 canonical parser 边界成立。 |
| 43-05 | 1/2 | descriptor publication 成立；图片二次打开绕过 bounded object error。 |
| 43-06 | 2/2 | authored code 字符、空格、换行与 monospace editability 成立。 |
| 43-07 | 3/3 | target slot、cover values、contents numbering、table row heights 均冻结。 |
| 43-08 | 3/4 | bounded template reader 与 registry 成立；aggregate 未真正重验 PPTX-08 outcome。 |
| 43-09 | 4/5 | delimiter、header-only table、Phase 44 边界成立；媒体竞态仍绕过 W01。 |

**Score:** 32/37 PLAN must-have truth groups verified。

九份 SUMMARY 的实现清单和历史专项向量大体与当前代码一致；但 43-01/02/03 对 frozen-plan mechanical emission、43-05/09 对所有公开媒体错误 bounded、43-08/09 对 aggregate closure 的表述仍过宽。

## Requirement Coverage

| Requirement | Status | Evidence / blocker |
|---|---|---|
| PPTX-01 | SATISFIED | canonical fixture 生成非空、可重开 26-slide PPTX。 |
| PPTX-02 | SATISFIED | text/table/picture/group/notes 均为 native editable objects，无整页截图。 |
| PPTX-03 | SATISFIED | 普通文本、code、timeline labels、gallery captions 均为 editable text shapes。 |
| PPTX-04 | SATISFIED | 常规与 header-only table 均为 native table，row heights 冻结并可回读。 |
| PPTX-05 | SATISFIED | canonical 图片为 picture object、contain placement、crop=0；竞态归入 VER-03。 |
| PPTX-06 | SATISFIED | gallery 每页最多 4 图，9 图按 4/4/1 扩页。 |
| PPTX-07 | SATISFIED | horizontal timeline 全局分区并自动扩页。 |
| PPTX-08 | BLOCKED | mixed code 可按 16pt 规划、24pt 发射，成功成品未扩页且 display height 超槽约 2 倍。 |
| PPTX-09 | SATISFIED | table continuation 重复 header，仅既有表名添加 `（续）`。 |
| PPTX-10 | SATISFIED | code 字符逐字、native editable、monospace，soft wrap 不写回额外 newline；容量问题计入 PPTX-08。 |
| PPTX-11 | SATISFIED | authored notes 传播到派生页，无 notes 页不产生 accidental relationship。 |
| PPTX-12 | SATISFIED | transition mode 诚实为 `none`。 |
| PPTX-13 | SATISFIED | 成功仅发布同 stem Markdown/PPTX，无 sidecar/debris。 |
| VER-03 | BLOCKED | canonical/静态 invalid 行为可重复，但媒体校验后替换可抛未映射异常并破坏 bounded public failure contract。 |
| SKILL-03 | SATISFIED | runtime 源码均位于 `skills/school-pptx/scripts/`，未发现 sibling skill runtime call。 |

**Requirements:** 13/15 satisfied，2/15 blocked。

## Boundary Verification

- Phase 43 只要求确定性 renderer、pagination、native object 与 public render 边界；这些边界中的自动反例必须在本阶段关闭。
- Phase 44 才拥有 public `verify --workdir`、runtime adapters、仓库 discoverability 和 PowerPoint/WPS 人工视觉 UAT。本报告未提前要求或宣称这些工作。
- viewer 中的中文换行、视觉均衡、组合编辑和主题保真仍需 Phase 44 人工证据；R43-C03 不依赖 viewer 主观判断，因为相同测量器已证明发射高度超过冻结 geometry。

## Next Steps

1. 统一 paginator/emitter 的正文 target-slot 字号，冻结实际字号；新增 mixed `title-content`/`two-column` 容量边界向量，断言 reopened run size、display height 和物理扩页。
2. 让 aggregate 从 gate 返回值推导 outcome，删除硬编码 `gap_outcome_audit`，使字号/高度反例成为 blocking gate。
3. 图片读取改为 descriptor/bytes 单次绑定；增加“校验后替换”故障注入，断言 stable code、无 traceback/path/Pillow 原文且旧 PPTX 保留。
4. 修复后重新运行 43-09 四条权威命令与以上两条反证，再更新本报告。

## Verification Complete

Phase 43 的 canonical aggregate 与大部分 native/publication 契约通过，但最新审查的 1 个 Critical 和 2 个 Warning 均可复现。最终状态为 `gaps_found`，score 为 `32/37`，共有 3 个开放 gap。

---
*Verified: 2026-07-14T18:09:01+08:00*
*Verifier: Codex gsd-verifier subagent*
