---
phase: 43-editable-pptx-renderer-and-pagination
verified: 2026-07-14T22:38:36+08:00
status: gaps_found
score: "14/15 phase requirements satisfied"
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
  VER-03: satisfied
  SKILL-03: satisfied
gaps:
  - id: R43-C04
    review_id: C-01
    severity: critical
    affects: [PPTX-08, Phase-Goal, Plan-02, Plan-07, Plan-10]
    summary: "contents.body 仍按 18pt 且不含 emitter paragraph spacing 分页，却冻结并以 26pt/每段 2pt space-after 发射；5 项合法目录只规划 1 页，成品整帧 156.0pt 超过 118.125pt 槽高且公开 render 退出 0。"
    fix: "让 contents 专用分页直接消费并冻结与 emitter 相同的 font、margins、line spacing、paragraph spacing 和 effective geometry；按整帧段落序列计高，加入 5 项临界目录 public render/reopen blocking 向量，要求自动扩页且每页总高度不超槽。"
  - id: R43-C05
    review_id: C-02
    severity: critical
    affects: [PPTX-08, Phase-Goal, Plan-02, Plan-09, Plan-10]
    summary: "_fragment_height() 完全忽略 fragment.heading；带 ### 源码的 4×40 中文 mixed code 公开退出 0并生成 2 个正文页，但每页完整 text frame 为 146.0pt，超过 118.125pt 槽高。"
    fix: "用与 add_fragment_text_frame 完全相同的段落序列计量 fragment：重复 heading、每个 list item、code/paragraph 正文及每段 spacing 全部入账；增加 heading+paragraph/list/code 三类整帧重开高度回归。"
  - id: R43-W04
    review_id: W-01
    severity: warning
    affects: [Phase-Goal, Plan-02, Plan-03, Plan-10]
    summary: "专用 code layout 通过通用 body helper 按 manifest max=14pt 规划，但 build_deck_plan 不冻结 code 字号，emitter 回退 min=10pt；独立 public 向量确认 selected_font_sizes 为空而重开 run 为 10pt。"
    fix: "为 dedicated code 明确一个受控字号并在计划中冻结，分页和 emitter 都只消费该值；加入 plan font、reopen font、物理页数与完整 text-frame capacity equality 回归。"
  - id: R43-W05
    review_id: W-02
    severity: warning
    affects: [Phase-Goal-Evidence, Plan-08, Plan-10]
    summary: "20-gate aggregate 仍会在 R43-C04/C05 确定性反例成立时整体 PASS；mixed gate 不含 heading/contents/dedicated-code，且 evidence producer 仍写死 joined_equality、embedded_hash、frozen_projection_equal、old_target_preserved，AST 仅审计最终 gap_outcome_audit assignment。"
    fix: "扩大 capacity gate 到 contents、heading+paragraph/list/code 与 dedicated code；所有 evidence 字段保存实际提取值或实际比较结果，aggregate 从原始值重算；AST/source guard 覆盖 evidence producer，禁止回填 expected hash/True。"
human_verification:
  required: false
  deferred_to_phase: 44
  note: "PowerPoint/WPS 的中文换行、视觉均衡、组合编辑和主题保真仍属于 Phase 44；本报告的阻断均由源码、public render、PPTX reopen 和同一确定性 TextMeasure 复现，不依赖 viewer 主观判断。"
---

# Phase 43 Verification Report

**Phase Goal:** Finalized Markdown renders to a non-empty editable PPTX whose physical slides follow the normalized template budgets.

**Status:** `gaps_found`

## Verification Outcome

Phase 43 尚未真正达到阶段目标。当前 `phase-43` aggregate 确实按固定顺序调用 20 个唯一 gate、`dynamic_skips=0` 并整体退出 0；canonical fixture 也可生成 27 张可重开、native/editable 的 PPTX。但独立 public 黑盒复现了两种“合法输入、退出 0、打印渲染成功、成品 text frame 超过模板槽高”的确定性反例，因此 aggregate 的 20/20 PASS 不能证明物理页遵守 normalized template budgets。

15 个 Phase 43 requirements 中 14 个满足，`PPTX-08` 被目录和 fragment-heading 两个裁切反例阻断。`VER-03` 现已满足：public `render` 可重复执行，canonical 成功，invalid/runtime-missing 非零，descriptor-bound media 错误保持 bounded；本报告不再沿用旧验证中由媒体 TOCTOU 导致的 `VER-03 blocked` 结论。

## Fresh Verification Evidence

环境：macOS、Python `3.14.6`、`python-pptx 1.0.2`、Pillow `12.3.0`、lxml `6.1.1`、PyYAML `6.0.3`；使用已有 uv cache 的离线 `PYTHONPATH`，未联网、未安装依赖、未创建仓库虚拟环境。

```bash
python3 skills/school-pptx/scripts/verify_pptx_renderer.py mixed-fragment-capacity
python3 skills/school-pptx/scripts/verify_pptx_renderer.py media-descriptor-binding
python3 skills/school-pptx/scripts/verify_pptx_renderer.py phase-43
```

新鲜结果：三条命令均退出 0；完整 aggregate 的 20 个 required/called gate 完全一致。canonical evidence 为 13 logical -> 27 physical、117 ZIP entries、127 relationships、10 pictures、2 native tables、18 groups、6 notes、唯一 closing、transition=`none`。

## Review Reproduction

### R43-C04 / REVIEW C-01 — CONFIRMED CRITICAL

源码中 `_contents_fragments()` 直接读取 `contents.body.font_size_min=18` 形成 weights；`build_deck_plan()` 随后却为相同 body 冻结 `font_size_max=26`，emitter 再机械使用 26pt 与每段 2pt `space_after`。

独立合法 Markdown 含一个空 authored contents slide 和 5 个后续 `##` 标题：

| Evidence | Result |
|---|---:|
| Public exit / summary | `0` / `渲染成功` |
| Contents entries / physical pages | `5` / `1` |
| Planning font / frozen+reopened font | `18pt` / `26pt` |
| Reopened full-frame height | `156.0pt` |
| `contents.body` slot height | `118.125pt` |

这不是 Phase 44 viewer 主观问题：同一个 `TextMeasure` 对实际发射的五个 26pt 段落重测已超过固定 geometry 约 `37.875pt`。

### R43-C05 / REVIEW C-02 — CONFIRMED CRITICAL

`_fragment_height()` 只测 `fragment.text/items`，不读取 `fragment.heading`；`add_fragment_text_frame()` 却会在每个派生 fragment 前追加 heading 段落，并为 heading、code 都设置相同 line/paragraph spacing。

独立合法 `title-content` 含 `### 源码` 与 4 行×40 个中文字符 fenced code：

| Evidence | Result |
|---|---:|
| Public exit / summary | `0` / `渲染成功` |
| Body physical pages | `2` |
| 每页 code height | `117.2pt` |
| 每页 heading + code full-frame height | `146.0pt` |
| Body slot height | `118.125pt` |

两张派生页都重复 `### 源码`，两页都超槽。现有 `mixed-fragment-capacity` gate 只重测 `Consolas` code run，因此其 `117.2 <= 118.125` 断言恰好漏掉 heading。

### R43-W04 / REVIEW W-01 — CONFIRMED WARNING

`_simple_slide_fragments()` 对 dedicated `code` slot 调 `_selected_body_typography()`，因此规划字号是 manifest `font_size_max=14`；但 `build_deck_plan()` 只为 contents/title-content/image-text、two-column、table 冻结字号，dedicated code 的 `selected_font_sizes` 仍为空。emitter 随后通过 `.get("code", font_size_min)` 以 10pt 发射。

独立 public dedicated-code 向量退出 0、计划一张 code 页、`selected_font_sizes={}`、重开 `school-pptx:code` run 为 10pt。该漂移当前偏向过度分页而非裁切，但违反“分页决定冻结、发射机械消费”的阶段目标。

### R43-W05 / REVIEW W-02 — CONFIRMED WARNING

完整 aggregate 在 R43-C04/C05 同时成立时仍 20/20 PASS，已直接证明 false-green。原因有两层：

1. coverage 只包含无 heading 的 mixed code，不包含 contents、fragment heading 或 dedicated code；
2. producer 仍回填常量：`joined_equality: True`、`embedded_hash: original_hash`、`frozen_projection_equal: True`、`old_target_preserved: True`。`_assert_gap_outcome_source_derived()` 只检查最终 `gap_outcome_audit` assignment，因此看不到上游常量。

这不会否定已由真实黑盒证据支持的媒体修复，但会否定“aggregate PASS 即 Phase 43 所有 budget 行为已关闭”的结论。

## Original 43-10 Gap Status

| Original gap | Verdict | Evidence |
|---|---|---|
| R43-C03 mixed code 字号漂移 | EXACT CASE CLOSED, BROADER PROPERTY BLOCKED | 无 heading 的 title-content/two-column 已分别统一为 24pt/22pt 并扩页；fragment heading 未计高形成 R43-C05。 |
| R43-W03 media descriptor race | CLOSED | 校验与 `add_picture` 消费同一 immutable bytes；替换后 embedded hash 仍等于 original、不等于 replacement；相对/绝对 symlink fail closed，runtime missing 非零并发布 editable placeholder pair。 |
| R43-W02 evidence-derived audit | NOT CLOSED | 最终 assignment 不再直接写成功常量，但 producer 仍回填 expected/True，且 aggregate 被 R43-C04/C05 证明 false-green；由 R43-W05 延续。 |

## Requirement Coverage

| Requirement | Status | Evidence / blocker |
|---|---|---|
| PPTX-01 | SATISFIED | canonical fixture 生成非空、可重开 27-slide PPTX。 |
| PPTX-02 | SATISFIED | 文本、table、picture、group、notes 均为 native editable objects，无整页截图。 |
| PPTX-03 | SATISFIED | ordinary text、code、timeline labels、gallery captions 均为 editable text objects；mixed code 字符逐字回读。 |
| PPTX-04 | SATISFIED | 常规与 header-only table 均为 native `<a:tbl>`，frozen row heights 可回读。 |
| PPTX-05 | SATISFIED | contain picture、crop=0；descriptor-bound validated bytes 与 embedded hash 一致，媒体竞态已关闭。 |
| PPTX-06 | SATISFIED | gallery 每页最多 4 图，canonical overflow 自动扩页。 |
| PPTX-07 | SATISFIED | horizontal timeline 保序、全局分区并自动扩页。 |
| PPTX-08 | BLOCKED | 5 项 contents 与带 `###` mixed code 均公开退出 0但完整 text frame 超过模板槽高。 |
| PPTX-09 | SATISFIED | table continuation 重复 header；仅既有表名加 `（续）`。 |
| PPTX-10 | SATISFIED | code native editable、monospace、逐字符保真，soft wrap 不写回 newline；dedicated code 字号漂移作为阶段目标 warning 单列。 |
| PPTX-11 | SATISFIED | authored notes 传播到全部派生页，无 notes 页不创建 accidental notes relationship。 |
| PPTX-12 | SATISFIED | transition mode 诚实记录为 `none`。 |
| PPTX-13 | SATISFIED | 成功目录仅有同 stem Markdown/PPTX，Markdown bytes 保留，无 sidecar/debris。 |
| VER-03 | SATISFIED | public render 可重复；valid 成功，invalid/runtime media missing 非零，unrecoverable failure 保留旧目标且输出 bounded。 |
| SKILL-03 | SATISFIED | runtime 实现均在 `skills/school-pptx/scripts/`，未调用 sibling skill runtime。 |

**Requirements:** 14/15 satisfied，1/15 blocked。

## Boundary Verification

- Phase 43 必须自动保证 frozen pagination 与 emitted geometry 一致；R43-C04/C05/W04 均属于本阶段，不可推迟给人工 viewer UAT。
- Phase 44 才拥有 public `verify --workdir`、六 runtime adapters、repository discoverability 和 PowerPoint/WPS 人工视觉证据。本报告没有提前要求这些交付。
- 中文实际 viewer 换行、视觉均衡、组合编辑与主题保真仍需 Phase 44；本报告的数值反例仅使用当前 renderer 自己的确定性 measurement contract。

## Next Gap Plan

1. 统一 contents 专用分页与发射 typography，增加 5 项目录整帧 capacity gate。
2. 将 heading 和所有 paragraph spacing 纳入 fragment/page 高度，覆盖 heading+paragraph/list/code。
3. 冻结 dedicated code 字号，让 planner/emitter 严格相等。
4. 删除 producer 中的 expected/True evidence 回填，并用以上三组反例扩展 aggregate。

## Verification Complete

Phase 43 的 native object、公开发布、媒体 descriptor race 和大部分分页契约已通过，但两个合法成功裁切反例与 dedicated code 字号漂移仍存在，20-gate aggregate 也被证明可 false-green。最终状态为 `gaps_found`，score 为 `14/15`，共有 4 个开放 gap。

---
*Verified: 2026-07-14T22:38:36+08:00*
*Verifier: Codex gsd-verifier subagent*
