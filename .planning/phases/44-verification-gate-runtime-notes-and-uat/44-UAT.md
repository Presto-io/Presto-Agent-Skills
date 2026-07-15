---
status: passed
viewer: "WPS Presentation"
viewer_version: "12.1.26035"
operating_system: "macOS 26.5.2"
fixture_sha256: "2a6fcd2dccbba738a3e0ea6681ac4915f013db3d5150e5a151d5dde17a2d257f"
pptx_sha256: "ed99daa1b7a187a2adb57f9769c1ecf282bc48ad950309cfbef3805a8f9af963"
tested_at: "2026-07-16T04:10:28+08:00"
tester: "Mrered"
evidence_source: "test/school-pptx-uat-eighth/evidence/verification.json"
delivery_pptx: "test/canonical-待UAT-第八版.pptx"
signoff: "Mrered 确认 UAT-V01..V06 与 UAT-I01..I04 共 10 项全部通过。"
---

# Phase 44 Real-Viewer UAT

当前状态：`PASSED`。Mrered 已在 WPS Presentation 12.1.26035（macOS 26.5.2）中确认 10 项人工 UAT 全部通过；本记录绑定第八版 canonical Markdown/PPTX 哈希。

## 测试者填写规则

- `viewer` 只允许精确填写 `Microsoft PowerPoint` 或 `WPS Presentation`；同时填写完整 viewer version、OS/version、带时区 ISO 8601 `tested_at` 和实际人类 `tester`。
- 已核对 `test/canonical-待UAT-第八版.pptx` SHA-256 与 frontmatter `pptx_sha256` 完全一致。
- 在真实桌面 viewer 的编辑模式中逐项操作。表中 `Result` 只允许 `PENDING`、`PASS`、`FAIL`、`BLOCKED`。
- 每项必须填写具体 physical slides/objects 与 Human observation；Evidence reference 可选，但截图不能代替 notes、table/code 编辑或 group 操作。
- 编辑 table、code、timeline/gallery group 时使用测试副本，不得保存覆盖 canonical PPTX。
- 缺失媒体占位符辅助 deck 位于 `work/<verification run.id>/negatives/missing-media/delivery/negative.pptx`；从 current `evidence/verification.json` 读取 `run.id`，该路径仍是预期非零 negative case，不因占位符显示正确而变成自动成功。

## 必测项

| ID | Check | Result | Physical slides / objects | Human observation | Evidence reference |
|---|---|---|---|---|---|
| UAT-V01 | 中文换行、孤行、裁切、重叠、溢出与续页完整性 | PASS | 第 1–26 页，重点检查第 4–9、11–25 页续页 | Mrered 确认中文排版、裁切、重叠、溢出和续页完整性通过。 | 人工确认 2026-07-16 |
| UAT-V02 | contents 仅含无编号章节标题、换行、密度、留白与末页平衡 | PASS | 第 2 页目录正文 | Mrered 确认目录层级、编号、垂直居中、密度和留白通过。 | 人工确认 2026-07-16 |
| UAT-V03 | timeline 顺序、节点、文字高度、主轴对齐与跨页平衡 | PASS | 第 16–17 页时间轴节点与主轴 | Mrered 确认节点顺序、正圆 marker、文字、渐变主轴和跨页平衡通过。 | 人工确认 2026-07-16 |
| UAT-V04 | theme 字体、颜色、背景、装饰、母版与 footer fidelity | PASS | 第 1–26 页；目录、章节、内容、尾页版式 | Mrered 确认最新母版的字体、颜色、背景、装饰和 footer 呈现通过。 | 人工确认 2026-07-16 |
| UAT-V05 | bold/highlight 范围、颜色、delimiter 隐藏与连续编辑 | PASS | 正文 rich-text run 与蓝色 highlight | Mrered 确认粗体范围及蓝底白字粗体高亮显示和编辑通过。 | 人工确认 2026-07-16 |
| UAT-V06 | contain 图片、宽高比与 missing-media 可编辑安全占位符 | PASS | 第 11–13、18–19、25 页图片；missing-media 测试 deck | Mrered 确认图片比例、阴影、文字避让及缺图占位符通过。 | 人工确认 2026-07-16 |
| UAT-I01 | notes surface 可见、可编辑、拆页复制与画布隔离 | PASS | 第 1–26 页演讲者注释 | Mrered 确认全部页面 notes 可见、可编辑且未进入可见画布。 | 人工确认 2026-07-16 |
| UAT-I02 | 首表页/续表页 native cell 编辑与撤销 | PASS | 第 14–15 页原生表格 | Mrered 确认表格单元格编辑、撤销、居中和蓝色样式通过。 | 人工确认 2026-07-16 |
| UAT-I03 | native code 修改一个字符并撤销，空白/换行保持 | PASS | 第 21–22 页原生代码文本 | Mrered 确认代码字符编辑、撤销、空白和换行保持通过。 | 人工确认 2026-07-16 |
| UAT-I04 | timeline/gallery group 整体移动、ungroup、成员编辑及适用时 regroup | PASS | 第 16–19 页时间轴与图库组合对象 | Mrered 确认组合移动、取消组合、成员编辑及重新组合通过。 | 人工确认 2026-07-16 |

## 人工签署

只有实际测试者在记录的合格 viewer 中打开哈希匹配的 PPTX、完成全部 10 项且全部为 `PASS` 后，才可将 frontmatter `status` 改为 `passed` 并填写 `signoff`。任何 `PENDING`、`FAIL`、`BLOCKED`、缺字段或 hash mismatch 都继续阻止 Phase 44、VER-10 与 v1.17 milestone acceptance。

自动化不得填写 viewer、version、OS、tester、tested_at、Human observation、signoff 或任何人工 `PASS`，也不得把结构 gate、截图、预览或 OOXML 状态映射成人工结果。

## Gaps

旧 canonical PPTX（SHA-256 `a15ed198538a4ee589b43b905e36aadc603fdb7c3d6857b6f08b2d96ff8591bf`）收到用户提供的视觉修订基准 `test/人工修改.pptx`，暴露了 VER-10 / UAT-V01..V04、UAT-V06 的字体、字号、位置、尺寸、母版/layout 和页面平衡 gap。该旧 artifact 已 superseded，不能作为验收对象。

第一轮修复后 canonical PPTX（SHA-256 `f8ba3a5f5ee855074b4ca3202a530dea5fb46141d5c25bd67e0858360151b261`）曾将首轮人工规则写回模板、manifest、paginator 与 renderer，但随后被第二轮反馈取代。

第二轮人工反馈覆盖后的 canonical 已备份为 `test/canonical-人工二次修改.pptx`（SHA-256 `eb456465ef2b89d8324fbddc367ab608a6d814b0c2b9d82edca4ac4990f2fc99`）。该反馈指出目录层级/编号、章节与正文标题对齐、表格 layout/配色/对齐、timeline 字号/marker 形变、普通正文图片覆盖和新增 layout 装饰问题；该 artifact 同样已 superseded。

第三版 canonical PPTX（SHA-256 `0e197dad727d2c2fd6f1c61876871fc35424c2d4b7e14da99b1a0684ce3518a2`，verification run `f045c7776479348b`）只生成无编号 section 目录，统一内容页标题规则，使用蓝色居中 native table，冻结 timeline 字号/正圆 marker，并将 title-content 图片拆到独立续页；该 artifact 已被第四版取代。

第四版 canonical PPTX（SHA-256 `5be7d57a9540489c82e1091890fe20ee1ea611bcbb71c2cbfde295d1eecf53e8`，verification run `a6e0060a79fa249e`）吸收了 timeline 主轴、密集列表字号、gallery 分页与 code 分页修复，但仍错误沿用了带内容占位符的模板理解，现已被第五版取代。

第五至第七版继续吸收目录/标题/正文对齐、时间线渐变与 marker、图片阴影、高亮样式、notes、页面底部安全距离和人工母版更新；这些中间 artifact 均已被第八版取代。

最终验收对象为第八版 canonical PPTX（SHA-256 `ed99daa1b7a187a2adb57f9769c1ecf282bc48ad950309cfbef3805a8f9af963`，verification run `76d62c9155092a76`）。该版以用户最终修改的第七版母版为标准模板，public verify 的 8/8 顶层 gate、6/6 negative case 和 Phase 43 21/21 gate 均通过。Mrered 于 WPS Presentation 12.1.26035 / macOS 26.5.2 确认 UAT-V01..V06 与 UAT-I01..I04 全部通过，当前无未关闭 gap。
