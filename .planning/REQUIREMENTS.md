# Requirements: Presto Agent Skills

**Defined:** 2026-07-23
**Milestone:** v1.20 School PPTX Visual Enrichment
**Core Value:** 一个 canonical `SKILL.md` 可被多类 agent 理解、审阅和适配；对 `school-pptx` 而言，最终 PPTX 必须同时保持学校模板一致、可编辑与可复验。

## v1 Requirements

### 受控视觉合同

- [x] **VIS-01**: `standard-school` 继续作为唯一主题；所有新增视觉 token、geometry、裁切与层级均由 manifest/template 拥有，Markdown 不新增坐标、尺寸、字体、颜色、背景、裁切、动画或 raw OOXML 控制面。
- [x] **VIS-02**: 作者可通过受限语义为适配内容的页面使用 `hero-evidence`、`annotated-image`、`process-overlay`、`kpi-evidence` 四类新布局，且每类具有独有的非空原生对象角色集合。
- [x] **VIS-03**: `gallery` 和既有图文能力拥有 1–4 项的固定视觉预设与一致图注结构，避免所有媒体页退化为同一种左右图文构图。

### 冻结计划与原生对象

- [x] **PLAN-01**: 渲染器在发射 PPTX 前，将受限视觉意图、variant、容量、逻辑到物理映射、媒体绑定和对象角色冻结到不可变物理计划；emitter 不重新选择布局、分页、裁切或字号。
- [x] **PLAN-02**: 同一已审阅 Markdown、确认媒体与 manifest 输入可重复得到相同视觉 projection；任何超量标注、流程步骤或 KPI 卡按固定预算分页或以稳定诊断失败。
- [x] **OBJ-01**: 标题、图注、数字、单位、标注、引线、流程节点、数据卡和表格全部以原生可编辑 PowerPoint/WPS 对象生成；整页截图和包含信息层文字的位图为硬失败。
- [x] **MEDIA-01**: 新布局只消费已验证的本地媒体，沿用 bounded descriptor-read、允许格式、hash 绑定与 `contain` 策略；不得联网搜图、下载图标、生成图片或在运行期下载字体/模板。

### 验证与人工验收

- [x] **VERIFY-01**: 一份完整 fixture 覆盖旧 11 个布局和四种新布局，并通过 Markdown→frozen-plan→重开 PPTX 的结构/对象/媒体三向验证。
- [x] **VERIFY-02**: 固定自动验证 registry 覆盖样式越权、缺失/非法媒体、媒体极端比例、过量视觉项、对象可编辑性、determinism、既有回归和 clean-delivery；不得动态跳过或用截图/像素评分宣称通过。
- [ ] **UAT-01**: 对本次 artifact SHA-256 绑定的真实 PowerPoint 或 WPS UAT 确认主体样式稳定、四种构图可读、媒体无失真、信息层可编辑/移动/取消组合，且自动 PASS 不代替人工验收。
- [x] **DOC-01**: canonical `SKILL.md`、Markdown contract、renderer/verification/UAT references 和六 runtime adapter 准确说明新增受控能力、离线边界、安装验证与人工 UAT 步骤。

## Deferred Requirements

- **FUTURE-01**: 在先完成 `annotated-image` 稳定关联 grammar 后，再评估更复杂的多图拼贴或专题模板。
- **FUTURE-02**: 如未来要求 PowerPoint 与 WPS 双 viewer 支持，分别建立双矩阵人工 UAT，不以一个 viewer 的结果推断另一个。

## Out of Scope

| Feature | Reason |
|---|---|
| PPT Master 自由 SVG、OOXML 后处理或重排管线 | 会取代现有受控 renderer，破坏模板和确定性边界。 |
| 联网搜图、AI 生成图片、运行期图标/字体下载 | `school-pptx` 正式 render 必须离线、可复验且仅使用已审核的本地媒体。 |
| Markdown 坐标/样式 DSL 与任意裁切 | 几何和主题必须由 `standard-school` 模板拥有。 |
| 整页截图、信息文字烘焙进图片或像素评分验收 | 会损害原生可编辑性，且不能证明真实 viewer 体验。 |
| 动画、自由 path、SmartArt、复杂滤镜或玻璃拟态 | 超出学校模板稳定性与跨 viewer 可验证范围。 |
| 改变封面、标题、页脚、结束页或默认 `contain` 图片策略 | 本里程碑只丰富内容层，不改变主体学校样式。 |
| 重新开启 v1.19 Phase 49 | v1.19 已完整结束，不属于 v1.20 范围。 |

## Traceability

| Requirement | Phase | Status |
|---|---|---|
| VIS-01 | Phase 50 | Complete |
| VIS-02 | Phase 50 | Complete |
| VIS-03 | Phase 50 | Complete |
| PLAN-01 | Phase 51 | Complete |
| PLAN-02 | Phase 51 | Complete |
| OBJ-01 | Phase 52 | Complete |
| MEDIA-01 | Phase 52 | Complete |
| VERIFY-01 | Phase 53 | Complete |
| VERIFY-02 | Phase 53 | Complete |
| UAT-01 | Phase 53 | Pending |
| DOC-01 | Phase 53 | Complete |

**Coverage:**
- v1 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0

---
*Requirements defined: 2026-07-23*
*Last updated: 2026-07-23 after research synthesis*
