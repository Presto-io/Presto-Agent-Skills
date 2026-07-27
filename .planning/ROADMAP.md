# Roadmap: Presto Agent Skills

## Milestones

- **Shipped: v1.0-v1.18** - Historical archives are listed in `.planning/MILESTONES.md`.
- **Completed: v1.19 毕业生高级简历生成器** - Phases 46-49 已完成归档。Archives: `.planning/milestones/v1.19-ROADMAP.md`, `.planning/milestones/v1.19-REQUIREMENTS.md`, `.planning/milestones/v1.19-MILESTONE-AUDIT.md`.
- **Active: v1.20 School PPTX Visual Enrichment** - Phases 50-53.

## Overview

v1.20 为 `school-pptx` 增加受控的教学视觉表达，同时保持 `standard-school` 唯一主题、Markdown-first 边界、离线本地媒体和原生可编辑 PPTX 交付。实施从模板拥有的语义合同与固定预设开始，将视觉决策冻结到物理计划后再机械发射对象，最后以完整回归、固定自动验证和 hash-bound 真人 UAT 闭环。

## Phases

- [x] **Phase 50: 受控视觉合同与模板预设** - 锁定新增构图的语义、固定预设、容量与 manifest 所有权。
- [x] **Phase 51: 冻结视觉规划与物理映射** - 在发射前确定并可复算视觉 variant、分页、媒体和对象角色。
- [x] **Phase 52: 原生对象与受控媒体发射** - 从冻结计划生成可编辑信息层和受审计的本地媒体对象。
- [ ] **Phase 53: 完整验证、Runtime 文档与真人 UAT** - 用固定证据链证明新旧布局、离线边界与真实 viewer 可用性。

## Phase Details

### Phase 50: 受控视觉合同与模板预设
**Goal**: 作者可用受限 Markdown 语义选择多样的教学视觉构图，而学校主题、几何、裁切和视觉层级仍完全由模板拥有。
**Depends on**: v1.19 closeout complete; no implementation dependency
**Requirements**: VIS-01, VIS-02, VIS-03
**Success Criteria** (what must be TRUE):
  1. 作者可在不提供坐标、尺寸、字体、颜色、背景、裁切、动画或 raw OOXML 的前提下，为适配内容选择四种新增构图。
  2. 每种新增构图都具有明确的教学语义和非空、彼此可区分的原生对象角色，而非改名的普通图文页。
  3. 作者可为 `gallery` 和既有图文页面使用 1–4 项固定媒体预设及一致图注，页面不再一律退化为左右图文构图。
  4. 任何试图越过 `standard-school` manifest 覆盖主题、几何、样式或裁切的 Markdown 都收到清晰拒绝。
**Plans**: 2 plans
**UI hint**: yes

### Phase 51: 冻结视觉规划与物理映射
**Goal**: 已审阅的 Markdown、确认媒体和 manifest 在发射前形成唯一、不可变且可复算的视觉物理计划。
**Depends on**: Phase 50
**Requirements**: PLAN-01, PLAN-02
**Success Criteria** (what must be TRUE):
  1. 用户可获得一个在 PPTX 发射前已确定的物理计划，其中包含视觉意图、variant、容量、逻辑到物理页映射、媒体绑定和对象角色。
  2. 同一已审阅 Markdown、确认媒体和 manifest 重复处理时，用户得到相同的视觉 projection 和物理页映射。
  3. 超量标注、流程步骤或 KPI 卡始终按固定预算分页，或以稳定、可定位的诊断失败，绝不由发射器临时缩字或重排。
**Plans**: TBD

### Phase 52: 原生对象与受控媒体发射
**Goal**: 用户获得以冻结计划机械生成、可在 PowerPoint/WPS 中编辑的视觉信息层，并且新媒体保持离线、受验证和不失真的交付边界。
**Depends on**: Phase 51
**Requirements**: OBJ-01, MEDIA-01
**Success Criteria** (what must be TRUE):
  1. 用户可在生成的 PPTX 中直接编辑标题、图注、数字、单位、标注、引线、流程节点、数据卡和表格，而无需编辑图片像素。
  2. 用户可移动新增信息层对象，并对支持组合的对象执行取消组合；整页截图或把信息文字烘焙进位图会被拒绝。
  3. 新布局仅接受经过验证和 hash 绑定的本地媒体，沿用受限大小、允许格式、单次 descriptor-read 与 `contain` 放置策略。
  4. 缺失、非法或不安全的媒体不会触发联网搜索、下载图标/字体/模板，且不会被发布为成功交付。
**Plans**: TBD
**UI hint**: yes

### Phase 53: 完整验证、Runtime 文档与真人 UAT
**Goal**: 用户能以固定的自动证据和本次 artifact 绑定的真实 viewer 操作，确认视觉增强没有破坏既有可编辑、离线和模板一致性承诺。
**Depends on**: Phase 52
**Requirements**: VERIFY-01, VERIFY-02, UAT-01, DOC-01
**Success Criteria** (what must be TRUE):
  1. 一份完整 fixture 同时覆盖旧 11 个布局和四种新增构图，并可从 Markdown、冻结计划和重开 PPTX 三方核对结构、对象和媒体。
  2. 用户运行固定自动验证 registry 时，可看到样式越权、非法/极端媒体、超量视觉项、可编辑性、确定性、既有回归和 clean-delivery 的明确结果，且没有动态跳过或截图/像素评分冒充通过。
  3. 至少一位真实 PowerPoint 或 WPS 操作者可对本次 Markdown/PPTX SHA-256 绑定的 artifact 记录：主体样式稳定、四种构图可读、媒体无失真，以及信息层可编辑、移动和取消组合。
  4. 用户可从 canonical `SKILL.md`、Markdown contract、renderer/verification/UAT references 和六 runtime adapter 了解新增能力、离线限制、安装验证与人工 UAT 步骤。
**Plans**: TBD
**UI hint**: yes

## Progress

**Execution Order:** Phase 50 → Phase 51 → Phase 52 → Phase 53

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 50. 受控视觉合同与模板预设 | 2/2 | Completed | 2026-07-23 |
| 51. 冻结视觉规划与物理映射 | 3/3 | Completed | 2026-07-23 |
| 52. 原生对象与受控媒体发射 | 1/1 | Completed | 2026-07-24 |
| 53. 完整验证、Runtime 文档与真人 UAT | 2/2 | Awaiting human UAT | - |
