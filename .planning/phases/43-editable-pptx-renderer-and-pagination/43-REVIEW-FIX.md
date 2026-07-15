---
status: fixed
phase: 43
findings_in_scope: 1
fixed: 1
skipped: 0
iteration: 2
---

# Phase 43 第二轮代码审查修复记录

## 本轮修复

### W-01：超长 dedicated-code heading 进入 bounded overflow 路径

- `_code_heading_height_emu()` 不再因 heading 高度达到或超过 code slot 而裸抛 `ValueError`。
- `_simple_slide_fragments()` 仍按完整 heading + code paragraph sequence 计高，并保留既有 `TEXT_BLOCK_OVERFLOW` error diagnostic；该 diagnostic 继续阻断 public render 成功，因此没有放宽成功裁切门禁。
- 冻结 heading geometry 时，将超槽 heading 高度限制为“code slot 高度减去一个冻结 14pt code paragraph 的最小正高度”。这只为非零 best-effort PPTX 保留有效几何，不把 overflow 页面视为成功。
- emitter 仍机械消费冻结值；heading 与 code shape 高度均为正、上下连续且总和严格等于原 code slot，不会产生零或负 code geometry。

## 新增负例

`frame-capacity-consistency` 增加 1,400 个中文字符的 dedicated-code heading：

- 直接 `build_deck_plan()` 返回 `PhysicalDeckPlan`，包含 `TEXT_BLOCK_OVERFLOW`、`severity=error`、源码行与逻辑页定位，不再抛异常。
- public render 退出非零，输出包含 `TEXT_BLOCK_OVERFLOW`，不退化为 `PPTX_RENDER_FAILED`，无 traceback，输出小于 8 KiB。
- public delivery 保持同 stem `.md/.pptx` best-effort 文件对。
- 实际冻结 heading 高度为 5,573,078 EMU，剩余 code 高度为 238,760 EMU；二者均为正且总和等于 5,811,838 EMU code slot。
- aggregate 从实际 diagnostic、public exit、artifact names 与重开 geometry 阻断回归。

## 上一轮复核

上一轮 3 项 finding 保持关闭：

- 原 C-01：多行 dedicated-code heading 的 planner/emitter 高度同源，reopen 检查全文、14pt 字号、1.2 行距、shape 高度及剩余 geometry。
- 原 W-01：`ParagraphProjection` 同时保存 authored/visible text；measurement/reopen 使用 visible，rich-run emitter 使用 authored；bold/highlight heading、paragraph、list 向量继续通过。
- 原 W-02：frame producer 返回 bounded raw operands，aggregate 独立重算 hash、高度、capacity 与异常码；source/mutation guard 继续拒绝派生值和 expected 常量回填。

## 验证结果

- 5 个受审源文件 `py_compile`：PASS。
- `frame-capacity-consistency`：PASS。
- `publication-safety`：PASS。
- 完整 `phase-43`：PASS；21 门 `required == called`，顺序完全一致，元素唯一，`dynamic_skips=0`。
- `git diff --check`：PASS。

验证使用 Codex bundled Python 3.12，并使用工作区现有 PyYAML 路径；PPTX、Pillow 与 lxml 来自 bundled runtime 的匹配依赖。

## 提交状态

当前执行环境的 `.git` 为只读，本轮未尝试创建提交，也未撤销其他 43-11 改动。

建议提交信息：

`fix(43): bound oversized dedicated code headings`
