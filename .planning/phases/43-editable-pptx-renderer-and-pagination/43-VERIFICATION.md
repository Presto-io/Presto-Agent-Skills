---
phase: 43-editable-pptx-renderer-and-pagination
status: passed
score: "15/15"
verified_at: 2026-07-15T10:40:48+08:00
---

# Phase 43 验证报告

## 验证结论

Phase 43 阶段目标已经达成。最终版 canonical Markdown 可通过公开 CLI 渲染为非空、可重开、可编辑的 PPTX，逻辑页到物理页的展开遵守 normalized manifest 预算。新鲜验证将 13 个逻辑页展开为 32 个物理页，并关闭了旧报告中的目录容量、mixed heading、dedicated-code 字号及 aggregate 假阳性缺口。

最终状态为 `passed`，Phase 43 的 15 项 requirements 全部满足。Phase 44 仍负责公开 `verify --workdir`、六 runtime 说明、仓库可发现性及 PowerPoint/WPS 人工 viewer UAT；这些有意后置的交付不是 Phase 43 gap。

## Must-Haves 证据

| Must-have / success criterion | 状态 | 新鲜证据 |
|---|---|---|
| 可重复公开 render 生成非空 PPTX，非法输入非零退出 | PASS | `school-pptx.sh render` 对 canonical fixture 返回 0并生成 446,805-byte PPTX；非法输入返回 1，输出 bounded diagnostics 和结构可编辑的 best-effort 双产物。 |
| 适用内容保持可编辑，禁止整页截图捷径 | PASS | Aggregate 重开确认 native text/code runs、2 个 native table slides、18 个 editable groups、10 个 picture objects 和 9 个 notes slides；`code-literal-roundtrip` 以 Consolas 逐字符保留 123 字符；gate 明确拒绝宽高等于整页的 picture。 |
| 长文本、表格、时间线、图集、目录和代码按 manifest 预算扩展 | PASS | Canonical fixture 从 13 logical 扩展到 32 physical；分页证据包含 5 个目录页 `[2,3,3,3,3]`、2 个表格页、2 个时间线页、最多 9 图的 gallery vectors、mixed-fragment 扩页及重开 full-frame 容量重算。 |
| 续页语义正确 | PASS | Structured pagination 重复表头，只有已有表名添加 `（续）`；其他续页标题不增加可见续页标记；header-only table 保持一行 native table。 |
| 标准成功交付严格包含同 stem Markdown 和 PPTX | PASS | Public publication gate 仅写入 `course-deck.md` 与 `course-deck.pptx`，保留 caller-owned 文件，不发布 logical JSON、manifest、diagnostics、logs 或临时 debris；Markdown 输入 bytes 保持，PPTX 最后发布。 |

## Gap Closure

Plan 43-11 已关闭旧验证报告中的四项缺口：

| 旧 gap | 状态 | 证据 |
|---|---|---|
| R43-C04：目录测量与发射 typography 不一致 | CLOSED | 目录分页和发射统一使用 frozen 26pt、1.2 行距、2pt 段后距；5 项目录自动扩为多页，aggregate 使用重开段落和实际 geometry 独立重测。 |
| R43-C05：容量计算遗漏 fragment heading | CLOSED | `fragment_paragraph_sequence()` 按发射顺序投影 heading、paragraph、每个 list item 与 code；`frame-capacity-consistency` 比较 frozen plan/reopen sequence，并阻断 full height 超过 effective height。 |
| R43-W04：dedicated code 规划与发射字号不同 | CLOSED | Dedicated code 冻结 14pt typography；缺失 frozen font/typography 分别以 `PPTX_PLAN_FONT_MISSING`、`PPTX_PLAN_TYPOGRAPHY_MISSING` fail closed；重开 code 与多行 heading runs 均为 14pt。 |
| R43-W05：aggregate 可接受 producer 常量证据 | CLOSED | Aggregate 从 raw plan/reopen hashes、段落序列、geometry、media hashes 及前后 snapshot 重算；producer 级 AST mutation guards 拒绝硬编码成功布尔、expected media hash、派生容量字段及固定 fail-closed code。 |

超长 dedicated-code heading 负例也进入规定的 bounded overflow 路径：public exit 1、`TEXT_BLOCK_OVERFLOW`、无 traceback、输出小于 8 KiB，且 heading/code geometry 均为正并严格合计为 frozen slot height。

## Requirements Traceability

| Requirement | 状态 | 证据 |
|---|---|---|
| PPTX-01 | SATISFIED | Canonical render 生成非空、可重开的 32-slide PPTX。 |
| PPTX-02 | SATISFIED | 使用 native text、table、picture 和 group；明确拒绝整页尺寸 picture。 |
| PPTX-03 | SATISFIED | Text、rich runs、code、timeline labels 与 gallery captions 均为 editable objects。 |
| PPTX-04 | SATISFIED | Table 重开为 native `<a:tbl>`，带 frozen row heights，并覆盖 header-only 输入。 |
| PPTX-05 | SATISFIED | 图片使用 contain placement、zero crop 的 picture objects；validated descriptor bytes 与 embedded hashes 一致。 |
| PPTX-06 | SATISFIED | Gallery 每物理页最多 4 图，并覆盖 5/6/8/9 图自动分页。 |
| PPTX-07 | SATISFIED | Horizontal timeline 保序并将 canonical 12 项自动拆分到多个物理页。 |
| PPTX-08 | SATISFIED | Text、contents、table、timeline、gallery、mixed fragments 与 dedicated code 均由固定 pagination/capacity gates 覆盖；canonical 输出 32 个物理页。 |
| PPTX-09 | SATISFIED | 表格续页重复 header，只有已有表名添加 `（续）`。 |
| PPTX-10 | SATISFIED | Code 可编辑、literal、monospace；dedicated code 冻结 14pt；parser/plan/PPTX 逐字符一致，soft wrap 不注入 authored newline。 |
| PPTX-11 | SATISFIED | Authored notes 传播到全部派生页；canonical 有 9 个 notes slides，无 notes 页不产生 accidental notes。 |
| PPTX-12 | SATISFIED | Transition mode 如实记录为 `none`，符合 v1.17 契约。 |
| PPTX-13 | SATISFIED | 成功公开输出严格为同 stem Markdown/PPTX；sidecar 与验证产物留在 delivery 外。 |
| VER-03 | SATISFIED | 公开 `render --input --out-dir [--stem]` 可重复；合法输入成功，非法或 runtime failure 非零且输出 bounded。 |
| SKILL-03 | SATISFIED | Runtime 实现全部位于 `skills/school-pptx/scripts/`；Phase 41/42 regression 同时核实 skill-local runtime files。 |

`.planning/REQUIREMENTS.md` 仍沿用旧 14/15 验证，将 `PPTX-08` 显示为 unchecked/Blocked。该跟踪字段相对 Plan 43-11、clean review、当前源码和新鲜门禁已经滞后。本 verifier 被明确限制为只覆盖本报告，因此仅记录差异，不修改 REQUIREMENTS、ROADMAP 或 STATE。

## 自动化验证

环境：

```bash
PYTHONPATH=$HOME/.cache/uv/archive-v0/I2PFDpRQMCS91p6l
SCHOOL_PPTX_PYTHON=$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
PYTHONPYCACHEPREFIX=/tmp/presto-pycache
```

命令与结果：

```bash
$SCHOOL_PPTX_PYTHON skills/school-pptx/scripts/verify_pptx_renderer.py phase-43
# PASS, exit 0（连续运行两次）

skills/school-pptx/scripts/school-pptx.sh render \
  --input skills/school-pptx/fixtures/school-pptx-full.md \
  --out-dir <isolated-workdir> --stem canonical
# PASS, exit 0；logical 13，physical 32；Markdown 8,881 bytes；PPTX 446,805 bytes

skills/school-pptx/scripts/school-pptx.sh render \
  --input <invalid-markdown> --out-dir <isolated-workdir> --stem invalid
# 预期失败，exit 1；bounded diagnostics 和同 stem editable best-effort pair

git diff --check -- <Phase-43 implementation/review/summary files>
# PASS
```

Aggregate 实际执行以下固定 21 门；`required == called`、顺序完全一致、元素唯一、`dynamic_skips=0`：

`contract-model`、`pagination`、`frozen-slot-content`、`frozen-numbering-row-heights`、`ooxml-bootstrap`、`editable-objects`、`code-literal-roundtrip`、`mixed-fragment-capacity`、`frame-capacity-consistency`、`emit-structure`、`frozen-plan-emission`、`cli-publication`、`best-effort`、`publication-safety`、`publication-descriptor-race`、`table-header-only`、`object-error-bounded`、`media-descriptor-binding`、`template-reader-security`、`determinism`、`phase_41_42_regression`。

Canonical 关键证据：32 slides、133 ZIP entries、146 relationships、10 image relationships、2 native table slides、18 groups、9 notes slides、2 gallery slides、2 timeline slides、transition mode `none`，physical-plan hash 稳定。Phase 41/42 regression 报告 11 个 template layouts 以及 fixture/example PASS。

## Code Review

最新 `43-REVIEW.md` 状态为 `clean`，blocker、critical、warning、info 均为 0。`43-REVIEW-FIX.md` 记录最终超长 dedicated-code heading 修复，并确认 `frame-capacity-consistency`、`publication-safety` 和完整 21-gate aggregate 通过。本次新鲜验证在当前未提交 workspace implementation 上复现了这些结果。

## 残余风险与 Phase 44 边界

- PowerPoint/WPS 的字体 fallback、中文实际换行观感、grouped-object 编辑便利性和视觉均衡仍需 Phase 44 viewer UAT。结构可编辑性与 bounded geometry 已自动证明，因此这不是 Phase 43 gap。
- Phase 44 需增加公开 `verify --workdir`、dependency readiness、negative-case packaging、六 runtime adapter notes、repository discoverability 及持久化 manual UAT evidence。
- 成功双产物有意不宣称跨文件事务。Markdown 先原子替换、PPTX 后替换；两次 replace 之间中断可能暂时形成新 Markdown + 旧 PPTX，CLI 已如实报告该恢复边界。
- 当前 Phase 43 implementation 与 closeout artifacts 尚未提交。这是管理状态而非 renderer 目标失败；主 orchestrator 应有意保留并提交已经验证的文件集。

## Verification Complete

Phase 43 验证通过，score 为 15/15。最终 Markdown 到 editable PPTX 的 renderer、normalized-budget pagination、native object editability、notes/media 行为、bounded overflow、固定 21-gate aggregate、Phase 41/42 regression 及干净双产物发布边界均已验证；Phase 44 viewer UAT 与 runtime/documentation 工作保持正确后置。
