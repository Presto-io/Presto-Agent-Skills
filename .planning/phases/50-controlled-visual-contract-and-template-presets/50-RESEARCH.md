# Phase 50: 受控视觉合同与模板预设 - Research

**Researched:** 2026-07-23
**Domain:** `school-pptx` 受限 Markdown、`standard-school` manifest 与模板合同校验
**Confidence:** HIGH

## 结论

Phase 50 应只把作者可写的四种视觉语义、各自容量、固定媒体预设和 manifest-owned 对象角色固化到 parser/contract/manifest/report。现有 `markdown_contract.py` 已经强制 `::: slide {layout="..."}` 是唯一 slide 属性，并能给每个块保留来源行；`template_report.py` 已经校验 renderer-owned geometry、文本预算、subregion 与 gallery 的 1--4 项 preset。因此本阶段无需也不得引入坐标 DSL、独立公开 JSON、PPTX 发射或视觉截图评估。

`annotated-image` 的稳定输入应是一个主图片块后紧随连续、从 1 开始的编号短标签列表；编号只作为 manifest 固定插槽的索引，绝不携带坐标。KPI 采用受限表格的数值层，避免从普通段落猜测单位或标签。流程同样采用固定列的 Markdown 表格，证据图为零或一张本地媒体。上述结构均可以由既有 block parser 以来源行进入后续 Phase 51 的冻结 planning。

## 已验证的扩展点

| Surface | 当前事实 | Phase 50 处理 |
|---|---|---|
| `markdown_contract.py` | layout 来自 manifest allowlist；只允许 `layout` 属性；`parse_blocks()` 已产出 image/list/table block 与来源行。 | 为四种新 layout 增加逐 layout 的 block-shape、数量、连续编号、非空图注与稳定诊断；不增加任意属性。 |
| `markdown-contract.md` | 定义 10 explicit + 1 implicit layout、图片/图注、禁止样式面。 | 将四种 layout、表格列、编号标注、容量和 1--4 媒体 preset 写成公开可审阅语法。 |
| `standard-school.manifest.yaml` | gallery 已有 1/2/3/4 item presets；所有 geometry/token 由 manifest 拥有。 | 为 image-text 和四种新 layout 注册静态 slot、subregion、容量和 object-role；只写模板拥有的 EMU/预算。 |
| `template_report.py` | `REQUIRED_LAYOUTS` 固定为 11，并专门检查 gallery preset。 | 扩展到 15 个 controlled layout，抽取可复用 1--4 preset 校验，并对四种新 layout 的专属 slot/角色/固定插槽失败关闭。 |
| `verify_markdown_contract.py` / `verify_template_manifest.py` | 已有真实 fixture、negative document 和 manifest mutation gate。 | 追加新 layout 正反例、样式越权、空图注、超量与 manifest drift gate；不触发 render。 |

## 锁定语义建议

| Layout | 受限 authored 结构 | 容量 | 后续原生对象角色 |
|---|---|---|---|
| `hero-evidence` | 1 张带图注主图 + `指标 | 数值 | 单位 | 短脚注` 表格 | 2--3 KPI | 主图、图注、KPI 卡、数值、可选单位/短脚注 |
| `annotated-image` | 1 张带图注主图 + 连续 `1.` 起的短标签列表 | 3--5 标注 | 主图、编号、标签、引线、固定锚区 |
| `process-overlay` | `步骤 | 说明` 表格 + 0 或 1 张带图注证据图 | 2--6 步 | 可选主图、节点、连接线、步骤编号/标签 |
| `kpi-evidence` | `指标 | 数值 | 单位 | 短脚注` 表格 | 2/3/4 KPI | 数据卡、数值、可选单位/标签/短脚注 |

每种表格的表头须完全匹配，数值列只接受受限数值字面量；不解析趋势箭头、图表、SVG 或自定义字段。图片一律沿用本地相对/显式绝对路径、`contain` 与现有缺失媒体 non-zero 契约。所有 gallery、image-text 和新 layout 媒体都必须有非空图注，允许以文件名作为正文图注。

## 执行边界

- 不实现 `VisualPlan`、冻结 variant、逻辑到物理页映射、分页、PPTX 对象、hash 绑定或 renderer 选择；这些属于 Phase 51/52。
- 不扩充唯一完整 fixture、固定 aggregate registry、六 runtime 文档或 WPS UAT。完整 fixture 和人工验收均为 Phase 53；不能把 UAT 写成 PASS。
- 临时 Demo 只可落在已有 ignore 目录，不能进入计划修改清单、正式 fixture 或 Git 提交。
- 不改 `standard-school.pptx`、主主题、封面/标题/页脚/closing 页、`contain` 策略、公开 delivery 文件集合或联网边界。

## 风险与对策

| 风险 | 对策 |
|---|---|
| 编号标注退化为隐蔽坐标 DSL | parser 只接受连续编号短标签；manifest 以编号绑定固定 slot；unknown attributes 和样式词继续 fail closed。 |
| 新 layout 只是旧图文页改名 | manifest 为每种 layout 声明不同的非空 `object_roles` 和专属 slots；template-report 断言完整性。 |
| `image-text` 多媒体仍退化为左图右文 | manifest 明确定义 1--4 张固定 item preset，并由 report 复用 gallery 同类完整性/无重叠检查。 |
| 超量内容在 emitter 临时压缩 | parser 只记录容量/来源 evidence；Phase 51 冻结分页，Phase 50 不写 emission 行为。 |
| 临时图片被误当正式证据 | Demo 路径维持 ignore-only；计划不得将其加入 fixture 或提交文件。 |

## 验证策略

执行 Phase 50 后，固定验证应至少覆盖：四种 layout 的合法结构；不存在多 layout/未知属性；空图注、错误列、非数值 KPI、非连续或过长标注、超量项目和缺失媒体的定位错误；style/coordinates/crop 仍被拒绝；manifest 的 15-layout allowlist、每种 object-role、固定锚区、gallery 与 image-text 的 1--4 preset、正尺寸/containment/non-overlap 均通过。不得以 PPTX 截图、像素评分或真人 UAT 宣称通过。
