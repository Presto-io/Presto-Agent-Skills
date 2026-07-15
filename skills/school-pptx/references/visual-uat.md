# school-pptx Visual UAT

本 reference 提供可复用人工 checklist，不记录任何项目的 tester、实际 timestamp/hash 或 PASS。自动验证、截图、PDF、缩略图、OOXML reopen 和自动视觉分析均不能代替真实 viewer 操作。

## Qualified Viewer and Identity

至少一名人类测试者必须在可报告版本的桌面版 **Microsoft PowerPoint** 或 **WPS Presentation** 中打开 canonical full-fixture PPTX，并完成全部 10 项。记录：

- `viewer`、`viewer_version`、`operating_system`
- `fixture_sha256`、`pptx_sha256`
- `tested_at`（带时区 ISO 8601）、`tester`
- `evidence_source`（repository/workdir relative reference）

两个 SHA-256 必须匹配同一次成功 public verification 的 canonical artifacts。字段缺失、hash 不匹配或指向 stale run 时记 `BLOCKED`，不能沿用旧结果。截图只可作辅助，不能证明 notes、table/code 编辑或 group 操作。

## Status and Procedure

每项只允许 `PENDING`、`PASS`、`FAIL`、`BLOCKED`。初始 `PENDING` 不是通过；执行后每项必须记录具体物理页/对象、简短人工 observation 和可选 evidence reference。

1. 确认 public verify 当前 PASS，并记录匹配的 fixture/PPTX hashes。
2. 在合格 viewer 编辑模式打开 PPTX，记录 viewer/environment/tester/time。
3. 逐页查看，并实际进入 notes、文本、table、code 和 group 编辑。
4. 对每项分别记录状态与观察，不以总评代替逐项结果。
5. 任一 `FAIL`/`BLOCKED` 形成明确 gap；修复后用新 hash 复验受影响项和回归范围。

## Required Checklist

| ID | Human check |
|---|---|
| `UAT-V01` | 检查正文、列表、长标题、表格、目录、时间线、图注和代码小标题的中文换行、标点/孤行、裁切、重叠、溢出、续页完整性与可读字号。 |
| `UAT-V02` | 确认目录只含无编号章节标题，不出现三级内容页标题；同时检查顺序、换行对齐、页间密度、留白与末页孤项。 |
| `UAT-V03` | 连续比较水平 timeline 的顺序、节点数量、文字高度、留白、主轴/marker/文字对齐及续页平衡。 |
| `UAT-V04` | 抽查封面、章节、正文、表格、timeline、gallery、code、closing 的字体角色、主题色、对比、背景、装饰、母版与 footer；缺字体无法判断时 BLOCKED。 |
| `UAT-V05` | 检查 bold/highlight 范围、主题高亮色、Markdown delimiter 隐藏、字符顺序、换行和连续编辑。 |
| `UAT-V06` | 检查正常图片 contain、宽高比、无裁剪/拉伸，以及 missing-media best-effort 的本地可编辑安全 placeholder；正确 placeholder 不改变非零失败语义。 |
| `UAT-I01` | 在 notes surface 检查有/无 notes 页、logical expansion 复制、完整可编辑性和画布隔离。 |
| `UAT-I02` | 在首表页和续表页副本中实际编辑 cell，确认 native rows/columns/repeated header/table name 和无关对象稳定。 |
| `UAT-I03` | 在 code 页修改并撤销一个字符，确认 native editable monospace text、空白/换行/长行稳定、soft wrap 不改源码、小标题可独立编辑。 |
| `UAT-I04` | 对 timeline node group 和 gallery card group 执行整体移动、ungroup、成员编辑/替换及适用时 regroup；锁死、透明覆盖或 viewer 无法操作均不得跳过。 |

实际 evidence table 每行至少有 `ID | Result | Physical slides / objects | Human observation | Evidence reference`。如果两个 viewer 都执行，应分表或清晰分列；第二个 viewer 的 PASS 不能覆盖第一个 viewer 的 FAIL。

## Automation Prohibition and Sign-off

自动化只可生成 artifacts/hashes、检查结构、创建 `PENDING` 表单，以及 lint 人工记录的字段、hash 和 enum；不得填写 tester、tested_at、viewer observation 或任何人工 `PASS`，也不得在 YOLO/auto 模式签署 UAT。

只有至少一个合格 viewer 的 10 项全部为 `PASS`，identity 字段完整且 hashes 匹配 current evidence，Phase 44 才可接受。任何 `PENDING`、`FAIL` 或 `BLOCKED` 都阻止接受；`FAIL`/`BLOCKED` 必须进入 `.planning/` gap，记录 requirement、环境、artifact hashes 和复验条件。最终 sign-off 只能由实际操作 viewer 的人类测试者完成。
