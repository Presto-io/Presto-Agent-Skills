---
phase: 44
slug: verification-gate-runtime-notes-and-uat
status: draft
surface: pptx-viewer-uat
created: 2026-07-15
---

# Phase 44 — PPTX Viewer UAT Design Contract

> 本阶段没有 Web UI。这里的 UI 是 canonical PPTX 在 Microsoft PowerPoint 或 WPS Presentation 中的幻灯片画布、备注界面和对象编辑体验。本文件定义验收契约，不记录或暗示任何实际人工测试结果。

## Scope

Phase 44 负责把 Phase 43 已通过结构验证的 PPTX 交给真实 viewer 做最终视觉与交互验收，并保存可追溯的人工证据。验收必须覆盖：

- 中文实际换行、孤行和可见溢出；
- 目录页与时间线页的跨页视觉平衡；
- 模板主题字体、颜色、装饰和页脚一致性；
- 粗体、高亮、contain 图片和缺失媒体占位符的显示；
- notes 在 viewer 中的可见性与画布隔离；
- table、code、timeline、gallery 等原生对象的编辑体验；
- 组合对象整体移动、取消组合和成员编辑。

本阶段不重新选择模板几何、字号、分页算法或对象实现，不以 PDF、截图、缩略图、OOXML 重开或自动视觉分析替代真实 viewer 操作。自动结构验证是进入人工 UAT 的前置条件，不是人工 PASS。

## Acceptance Surface

至少使用以下真实桌面 viewer 之一打开完整 canonical fixture 生成的 PPTX：

| Viewer | 最低要求 | 角色 |
|---|---|---|
| Microsoft PowerPoint | 可报告产品版本的桌面版 | 合格主验收 viewer |
| WPS Presentation | 可报告产品版本的桌面版 | 合格主验收 viewer |

至少一个 viewer 必须完成全部必测项。第二个 viewer 可作为比较证据，但不能用第二个 viewer 的 PASS 覆盖第一个 viewer 已观察到的 FAIL；两者差异必须记录为兼容性 gap。浏览器预览、文件管理器缩略图、在线只读预览和导出的 PDF 均不构成合格 viewer。

## Evidence Identity

人工 UAT 记录必须绑定到本次真实打开的准确输入和产物，而不是仅引用文件名。Phase 44 的 milestone evidence 至少记录：

| Field | Contract |
|---|---|
| `viewer` | `Microsoft PowerPoint` 或 `WPS Presentation`，不得只写“PPT 软件” |
| `viewer_version` | viewer 显示的完整可识别版本或构建号 |
| `operating_system` | OS 名称和可识别版本 |
| `fixture_sha256` | 被渲染 canonical Markdown 的 SHA-256 |
| `pptx_sha256` | 在 viewer 中打开的 PPTX 的 SHA-256 |
| `tested_at` | 带时区的 ISO 8601 时间戳 |
| `tester` | 实际执行查看和编辑操作的人类测试者标识 |
| `evidence_source` | Phase 44 verification evidence 的仓库相对路径或 workdir 相对引用 |

`fixture_sha256` 与 `pptx_sha256` 必须和公开 `verify --workdir <dir>` 当前运行产生的 canonical evidence 一致。哈希不一致、字段缺失或 evidence 指向旧运行时，UAT 结果为 `BLOCKED`，不能沿用旧 PASS。

截图只能作为可选辅助引用。截图无法证明 notes、原生 table/code 编辑或 group 操作，因此不能单独满足任何交互项。

## Result Vocabulary

每个必测项使用同一状态枚举：

| Status | Meaning |
|---|---|
| `PENDING` | 尚未由人类在合格 viewer 中执行；初始状态，不是通过 |
| `PASS` | 人类完成指定观察或操作，且所有判据均满足 |
| `FAIL` | 操作可执行，但至少一个可见或交互判据不满足 |
| `BLOCKED` | 因 viewer、文件、权限、字体、环境或证据身份问题无法完成判定 |

每项必须记录状态、简短人工观察、涉及的物理页或对象，以及可选证据引用。人工验收结束时，所有必测项必须从 `PENDING` 解析为 `PASS`、`FAIL` 或 `BLOCKED`；只有全部为 `PASS` 才可接受。

## UAT Procedure

1. 先确认公开 verification 当前运行通过，并记录其 fixture/PPTX 哈希；自动验证失败时不开始视觉验收。
2. 由人类在合格真实 viewer 中打开哈希匹配的 canonical full-fixture PPTX，记录 viewer、版本、OS、时间和测试者。
3. 以普通编辑模式逐页检查画布，实际进入备注面板、文本编辑、表格编辑和组合对象编辑；不能只播放幻灯片或浏览缩略图。
4. 对每个必测项分别记录 `PASS`、`FAIL` 或 `BLOCKED` 和观察，不允许用一个总评代替逐项结果。
5. 任一 `FAIL` 或 `BLOCKED` 立即形成明确 gap，并阻止 Phase 44 和 v1.17 milestone acceptance；修复后必须用新产物哈希重新验收受影响项及其回归范围。

## Required Visual Checks

### UAT-V01 — Chinese wrapping, orphans, and overflow

在正文、列表、长标题、表格单元格、目录、时间线标签、图注和代码小标题等包含中文长文本的页面逐页检查：

- 汉字和标点换行自然，没有字符被裁切、遮挡、越出文本框或落到画布外；
- 没有明显的页首/页尾孤行、单字孤行或标点悬挂造成的不可接受阅读断裂；
- 续页内容完整、顺序连续，没有重复、丢失或因 viewer 自动缩放而改变信息层级；
- 所有文本保持可读，没有低于模板预算的异常缩小或重叠。

任一可见裁切、溢出、重叠、内容缺失或明显孤行记为 `FAIL`。无法确认所需字体是否加载而导致版式不可判断时记为 `BLOCKED`，并记录实际 fallback 情况。

### UAT-V02 — Contents balance

对所有标题为“目录”的物理页连续比较：

- 编号与条目顺序连续，页面标题一致且没有多余“续”标记；
- 各页条目数量和换行后的视觉重量接近；
- 不出现明显过密页、大片异常留白页或末页孤项；
- 长标题换行后仍与编号对齐，且不侵占页脚或装饰区域。

结构计数正确但肉眼明显失衡仍记为 `FAIL`。

### UAT-V03 — Timeline balance

对所有时间线物理页连续比较：

- 水平阅读方向和时间顺序清晰；
- 各页节点数量、文字高度和留白总体平衡，不出现明显长页/短页交替或孤立末页节点；
- 节点标记、时间、标题、说明和主轴线对齐，不重叠、不越界；
- 续页保持相同视觉层级，没有被压缩到难以阅读。

### UAT-V04 — Theme fidelity

从封面、章节、正文、表格、时间线、图集、代码和结束页抽查主题表现：

- 标题使用模板主字体角色，正文使用模板正文字体角色，代码保持等宽字体；
- 主题色、高亮色、中性表面和文字对比符合 normalized template，不出现任意 RGB 漂移；
- 背景、装饰、母版元素和页脚在适用布局上存在且位置稳定；
- 页面之间没有意外字体替换、颜色变化、装饰丢失或页脚侵入内容。

仅因 viewer 环境缺少模板字体而无法形成有效判断时记为 `BLOCKED`，不能把 fallback 显示批准为模板 PASS。

### UAT-V05 — Bold and highlight

在同时含普通、粗体和高亮 run 的文本中检查：

- Markdown 分隔符不出现在可见文字中；
- 粗体仅作用于预期文本，高亮范围准确；
- 高亮颜色属于模板主题且文字仍清晰可读；
- 粗体与高亮共存时不破坏字符顺序、换行和连续编辑体验。

### UAT-V06 — Images and missing-media placeholders

检查正常图片以及专门生成的缺失媒体 best-effort PPTX：

- 正常图片以 contain 方式完整显示，保持宽高比，无默认裁切、拉伸或槽位外溢；
- 图集中的图片、图注和空图注槽位置稳定，图文页的图片与正文平衡；
- 缺失媒体显示为本地、模板风格、可编辑的安全占位符，不伪装成真实图片；
- 占位符不含水印、联网下载内容、绝对路径、traceback 或不受控诊断文本。

缺失媒体用例本身仍是非零失败路径；占位符显示正确不把该渲染改判为成功。

## Required Interaction Checks

### UAT-I01 — Notes visibility and isolation

在 viewer 的备注界面打开所有预期含 notes 的页面，并抽查无 notes 页面：

- 演讲者备注在 notes surface 可见、文本完整且可编辑；
- 同一逻辑页拆出的各物理页都带相同备注；
- 备注不出现在幻灯片画布、放映内容或普通文本对象中；
- 无备注页面不出现意外备注内容。

只检查 OOXML 中存在 notes part 不足以 PASS，必须在 viewer 中实际打开备注界面。

### UAT-I02 — Native table editability

在至少一张首表页和一张续表页中实际执行单元格编辑，并在不保存破坏 canonical 证据的副本上完成：

- 可直接选中单元格并修改文字，不是整页或整表图片；
- 行列和重复表头保持原生表格行为；
- 表名文本框可独立编辑，续表名规则正确；
- 编辑一个单元格不会导致无关对象整体失效或异常位移。

### UAT-I03 — Native code editability

在代码页中实际进入代码文本并修改一个字符，再撤销：

- 代码是连续可编辑的文本，不是图片；
- 等宽字体、空白、源码换行和长行内容可见且稳定；
- 软换行没有向源码文本注入额外换行；
- 可选代码小标题与代码正文是可分别编辑的预期对象。

### UAT-I04 — Group move, ungroup, and member edit

分别选择至少一个 timeline 节点组和一个 gallery 卡片组，在测试副本中执行：整体移动、取消组合、编辑组内文本/图片或图注；必要时重新组合。

- 初始状态下可将节点或卡片作为整体选择并移动，成员相对位置保持；
- viewer 支持取消组合，取消后可单独选择并编辑成员；
- timeline 主轴线保持独立于节点组；gallery 图片与图注均可独立替换/编辑；
- 操作过程中不存在整页截图、锁死对象、不可选透明覆盖层或明显对象损坏；
- 若 viewer 支持重新组合，重新组合后仍可整体移动；viewer 本身不提供该命令时须记录并判定为 `BLOCKED`，不能跳过。

## Required Evidence Table

实际 milestone UAT 记录必须至少包含以下逐项表格；本设计契约不预填状态或观察：

| ID | Check | Result | Physical slides / objects | Human observation | Evidence reference |
|---|---|---|---|---|---|
| UAT-V01 | 中文换行、孤行、溢出 | 待人工填写 | 待人工填写 | 待人工填写 | 可选 |
| UAT-V02 | 目录视觉平衡 | 待人工填写 | 待人工填写 | 待人工填写 | 可选 |
| UAT-V03 | 时间线视觉平衡 | 待人工填写 | 待人工填写 | 待人工填写 | 可选 |
| UAT-V04 | 字体、颜色、装饰、页脚 | 待人工填写 | 待人工填写 | 待人工填写 | 可选 |
| UAT-V05 | 粗体与高亮 | 待人工填写 | 待人工填写 | 待人工填写 | 可选 |
| UAT-V06 | contain 图片与缺失媒体占位 | 待人工填写 | 待人工填写 | 待人工填写 | 可选 |
| UAT-I01 | notes 可见性与画布隔离 | 待人工填写 | 待人工填写 | 待人工填写 | 可选 |
| UAT-I02 | table 原生编辑 | 待人工填写 | 待人工填写 | 待人工填写 | 可选 |
| UAT-I03 | code 原生编辑 | 待人工填写 | 待人工填写 | 待人工填写 | 可选 |
| UAT-I04 | group 移动、取消组合、成员编辑 | 待人工填写 | 待人工填写 | 待人工填写 | 可选 |

完成记录时，`Result` 只能填写 `PASS`、`FAIL` 或 `BLOCKED`。如果同一项在两个 viewer 中执行，应使用两张独立结果表或明确按 viewer 分列，不能合并成模糊总评。

## Automation Boundary

自动化允许：

- 生成 canonical fixture/PPTX 并计算 SHA-256；
- 检查 PPTX 可重开、结构、关系、对象类型和固定 gate registry；
- 创建空白或 `pending` 的 UAT 记录；
- 校验人工记录字段完整、哈希匹配、状态枚举合法以及不存在未解析项。

自动化禁止：

- 填写 tester、人工观察、viewer 中的操作结果或测试时间；
- 把 OOXML、截图、渲染预览或代码断言转换为人工 `PASS`；
- 在 YOLO/auto 模式下代替人类签署 UAT；
- 因 canonical verification 通过而推断视觉或编辑体验通过。

自动执行到该边界时必须报告 `UAT PENDING` 并停止 milestone acceptance。不得伪造 PowerPoint/WPS 版本、测试者身份或观察。

## Gap and Acceptance Rules

Phase 44 人工视觉验收通过的必要且充分条件是：

1. 至少一个合格真实 viewer 完成全部 10 个必测项；
2. viewer/version、OS、fixture/PPTX hash、timestamp、tester 和 evidence source 均非空且可核对；
3. 两个哈希与本次通过的 verification canonical artifacts 一致；
4. 每个必测项均有具体人工观察且状态为 `PASS`；
5. 没有 `PENDING`、`FAIL` 或 `BLOCKED`。

任何 `FAIL` 或 `BLOCKED` 都必须成为 `.planning/` 中可追踪的明确 gap，记录受影响的 requirement（至少 `VER-10`，必要时包含对应 PPTX requirement）、viewer 环境、产物哈希和复验条件。未关闭 gap 前不得把 Phase 44、VER-10 或 v1.17 milestone 标记为完成。

## Sign-Off Contract

最终人工签署必须由实际测试者完成，并明确声明：已在所记录的真实 viewer 中打开哈希匹配的 PPTX，执行了所有视觉与编辑操作，逐项结果均为 PASS。代理、自动 verifier、计划生成器或截图审查者均不能代表人类测试者签署。

**Current approval:** pending human viewer UAT
