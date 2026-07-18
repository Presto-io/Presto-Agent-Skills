# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Last updated:** 2026-07-18 for `graduate-resume/v2` source contract
**Granularity:** Coarse
**Project Mode:** MVP

## Milestones

- **Shipped: v1.0 MVP** - Phases 1-3, shipped 2026-05-30. Archives: `.planning/milestones/v1.0-ROADMAP.md`, `.planning/milestones/v1.0-REQUIREMENTS.md`
- **Shipped: v1.1 Document Workflow** - Phase 4, shipped 2026-05-31. Archives: `.planning/milestones/v1.1-ROADMAP.md`, `.planning/milestones/v1.1-REQUIREMENTS.md`
- **Shipped: v1.2 Gongwen Skill** - Phase 5, shipped 2026-05-31. Archives: `.planning/milestones/v1.2-ROADMAP.md`, `.planning/milestones/v1.2-REQUIREMENTS.md`
- **Shipped: v1.3 Jiaoan Shicao Skill** - Phase 6, shipped 2026-05-31. Archives: `.planning/milestones/v1.3-ROADMAP.md`, `.planning/milestones/v1.3-REQUIREMENTS.md`
- **Shipped: v1.4 Jiaoan Jihua Skill** - Phase 7, shipped 2026-05-31. Archives: `.planning/milestones/v1.4-ROADMAP.md`, `.planning/milestones/v1.4-REQUIREMENTS.md`
- **Shipped: v1.5 School Presentation Skill** - Phase 8, shipped 2026-06-01. Archives: `.planning/milestones/v1.5-ROADMAP.md`, `.planning/milestones/v1.5-REQUIREMENTS.md`
- **Shipped: v1.6 School Presentation Playback UX** - Phases 9-10, shipped 2026-06-11. Archives: `.planning/milestones/v1.6-ROADMAP.md`, `.planning/milestones/v1.6-REQUIREMENTS.md`, `.planning/milestones/v1.6-MILESTONE-AUDIT.md`
- **Shipped: v1.7 End-of-Term Teaching Materials Skill** - Phases 11-13, shipped 2026-06-10. Archives: `.planning/milestones/v1.7-ROADMAP.md`, `.planning/milestones/v1.7-REQUIREMENTS.md`, `.planning/milestones/v1.7-MILESTONE-AUDIT.md`
- **Shipped: v1.8 School Presentation Continuation** - Phases 14-16, shipped 2026-06-11. Archives: `.planning/milestones/v1.8-ROADMAP.md`, `.planning/milestones/v1.8-REQUIREMENTS.md`, `.planning/milestones/v1.8-MILESTONE-AUDIT.md`
- **Shipped: v1.9 Skill Decomposition and Entry Slimming** - Phases 17-19, shipped 2026-06-13. Archives: `.planning/milestones/v1.9-ROADMAP.md`, `.planning/milestones/v1.9-REQUIREMENTS.md`, `.planning/milestones/v1.9-MILESTONE-AUDIT.md`
- **Shipped: v1.10 Jiaoan Typst 1:1 Conversion** - Phases 20-21, shipped 2026-06-13. Archives: `.planning/milestones/v1.10-ROADMAP.md`, `.planning/milestones/v1.10-REQUIREMENTS.md`, `.planning/milestones/v1.10-MILESTONE-AUDIT.md`
- **Shipped: v1.11 Integrated Teaching Design Package** - Phases 22-25, shipped 2026-06-14. Archives: `.planning/milestones/v1.11-ROADMAP.md`, `.planning/milestones/v1.11-REQUIREMENTS.md`, `.planning/milestones/v1.11-MILESTONE-AUDIT.md`
- **Shipped: v1.12 Teaching Design Package Post-Close Repair** - Phases 26-27, shipped 2026-06-14. Archives: `.planning/milestones/v1.12-ROADMAP.md`, `.planning/milestones/v1.12-REQUIREMENTS.md`, `.planning/milestones/v1.12-MILESTONE-AUDIT.md`
- **Shipped: v1.13 Teaching Design Package Markdown Baseline Rendering** - Phases 28-29, shipped 2026-06-14. Archives: `.planning/milestones/v1.13-ROADMAP.md`, `.planning/milestones/v1.13-REQUIREMENTS.md`, `.planning/milestones/v1.13-MILESTONE-AUDIT.md`
- **Shipped: v1.14 teaching-design-package 单技能独立交付与 1+1+3 输出契约** - Phases 30-32, shipped 2026-06-15. Archives: `.planning/milestones/v1.14-ROADMAP.md`, `.planning/milestones/v1.14-REQUIREMENTS.md`, `.planning/milestones/v1.14-MILESTONE-AUDIT.md`
- **Shipped: v1.15 teaching-design-package 模块化渲染与旧格式回归** - Phases 33-36, shipped 2026-06-15. Archives: `.planning/milestones/v1.15-ROADMAP.md`, `.planning/milestones/v1.15-REQUIREMENTS.md`, `.planning/milestones/v1.15-MILESTONE-AUDIT.md`
- **Shipped: v1.16 调课单 Skill** - Phases 37-40, shipped 2026-06-21. Archives: `.planning/milestones/v1.16-ROADMAP.md`, `.planning/milestones/v1.16-REQUIREMENTS.md`, `.planning/milestones/v1.16-MILESTONE-AUDIT.md`
- **Shipped: v1.17 school-pptx** - Phases 41-44, shipped 2026-07-16. Archives: `.planning/milestones/v1.17-ROADMAP.md`, `.planning/milestones/v1.17-REQUIREMENTS.md`, `.planning/milestones/v1.17-MILESTONE-AUDIT.md`
- **Shipped: v1.18 全技能干净交付目录标准化改造** - Phase 45, shipped 2026-07-17. Archives: `.planning/milestones/v1.18-ROADMAP.md`, `.planning/milestones/v1.18-REQUIREMENTS.md`, `.planning/milestones/v1.18-MILESTONE-AUDIT.md`
- **Planned: v1.19 毕业生高级简历生成器** - Phases 46-49

## Overview

v1.19 为电气相关工科大专毕业生交付离线、Markdown-first 的 `graduate-resume` 技能：先固化可审阅资料、字体与夹具，再冻结 1/2 页 A4 主题布局，继而确定性生成通用与多目标定向三件套，最后以跨 runtime 和跨环境证据完成验收。

## Phases

- [x] **Phase 46: 资料契约、字体与可验证夹具** - 建立主题无关、可验证的简历资料与离线 CLI 基线。
- [x] **Phase 47: 受控主题、照片与冻结布局** - 让同一资料在三种主题下稳定收敛为 1/2 页 A4 简历。 (completed 2026-07-18)
- [ ] **Phase 48: 确定性定向渲染与干净批量交付** - 生成通用版和多目标定向 Markdown、Typst、PDF 三件套。
- [ ] **Phase 49: 聚合验证、跨 Runtime 与发布验收** - 通过故障注入、跨环境 UAT 和六 runtime 验证证明交付可信。

## Phase Details

### Phase 46: 资料契约、字体与可验证夹具
**Goal**: 用户能提供一份独立于主题和 AI、经验证后可供定向与渲染复用的毕业生简历资料。
**Depends on**: Phase 45
**Requirements**: SCHEMA-01, SCHEMA-02, SCHEMA-03, SCHEMA-04
**Success Criteria** (what must be TRUE):
  1. 用户可用一份主题无关的混合 Markdown/YAML 资料表达电气、机电、智能制造、发电厂和新能源方向毕业生的已核实资料：信息栏 `profile` 与可选本地 `photo` 路径位于 YAML，其余事实位于 Markdown 正文，并为可复用事实保留稳定 ID。
  2. `validate` 会拒绝未知字段、重复事实、缺失必填资料或待确认事实，并说明为何不能生成最终投递件。
  3. 可选 AI 整理只产生待审阅草稿；`validate`、`target`、`plan`、`render`、`batch`、`verify` 均离线、零 token。
  4. 用户可提供多个单位、岗位及招聘信息；明确不提供后，技能仅询问一次并继续生成通用版。
**Plans**: 3 plans

Plans:
- [x] 46-01: 定义 skill-local schema、稳定事实 ID 与受限校验规则。
- [x] 46-02: 建立离线 CLI 命令边界、目标资料输入、固定依赖和受控 CJK 字体。
- [x] 46-03: 建立正常、多目标与资料错误 fixtures，作为后续阶段基线。

### Phase 47: 受控主题、照片与冻结布局
**Goal**: 用户能用同一已核实资料选择主题和照片模式，获得不虚构、不截断、逻辑完整的 1 页或 2 页 A4 布局。
**Depends on**: Phase 46
**Requirements**: THEME-01, THEME-02, THEME-03, THEME-04, THEME-05
**Success Criteria** (what must be TRUE):
  1. 用户可用 YAML 主题参数切换保守稳妥、现代简洁和个性设计，且无需改写资料 schema。
  2. 照片版只使用用户明确提供的本地照片；无照片版移除照片区域而不保留空位。
  3. CLI 可自动或按用户强制选择 1 页或 2 页 A4，结果不低于可读性阈值、不截断且不产生第三页。
  4. 两页输出没有孤立标题、无标题续接或拆开的项目、实训、经历、职责及成果；不能满足时失败关闭并说明原因。
  5. 内容不足时仅重排或扩展既有材料可支撑的表达，不会虚构事实。
**Plans**: 3 plans
**UI hint**: yes

Plans:
**Wave 1**
- [x] 47-01: 定义三种受控主题与照片/无照片变体的可读性边界。

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 47-02: 建立冻结布局计划、模块不可拆规则与 1/2 页收敛/失败条件。

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 47-03: 用一页、两页、照片、无照片和内容压力样张锁定密度与双页锚点。

### Phase 48: 确定性定向渲染与干净批量交付
**Goal**: 用户能离线生成通用版及多个透明、可追溯的定向简历三件套，并在失败时保持当前成功交付。
**Depends on**: Phase 47
**Requirements**: TARGET-01, TARGET-02, TARGET-03, DELIVERY-01, DELIVERY-02, DELIVERY-03
**Success Criteria** (what must be TRUE):
  1. 用户可从同一已核实资料生成一份通用版及每个“单位 + 岗位”一份定向版，定向仅选择、排序或强调已核实事实。
  2. 用户可查看硬条件的满足、缺口、未知或不适用结果；存在缺口时可明确选择生成，但简历不暗示已符合。
  3. 每个版本资料记录实际主题、页数、照片模式、目标单位/岗位和当次招聘信息来源/日期，技能不抓取、猜测或声称招聘信息实时。
  4. 每个成功版本以同 stem 输出正式命名的 Markdown、Typst、PDF 三件套；通用版使用 `通用`，投递根不含诊断或中间件。
  5. 单份与批量任务均先完整预检；任一目标失败不发布部分版本，并保留 candidate-first、bytes no-op、完整 bundle history、rollback 与 unknown/symlink fail-closed 语义。
**Plans**: 3 plans

Plans:
- [ ] 48-01: 实现 target resolver、硬条件四态和可追溯版本 metadata。
- [ ] 48-02: 从冻结布局生成正式命名的 Markdown、Typst、PDF 三件套。
- [ ] 48-03: 实现单份/批量候选发布、完整预检、no-op、归档、rollback 和路径边界。

### Phase 49: 聚合验证、跨 Runtime 与发布验收
**Goal**: 用户能以重复的证据确认简历为真实、布局稳定、可在所有承诺 runtime 中离线交付的 1/2 页 A4 PDF。
**Depends on**: Phase 48
**Requirements**: VERIFY-01, VERIFY-02, VERIFY-03, VERIFY-04
**Success Criteria** (what must be TRUE):
  1. `verify` 确认 PDF 为真实 1 或 2 页 A4，并验证主题、照片模式、页数、模块边界和正式命名，而不只检查文件非空或可打开。
  2. 一条聚合回归命令覆盖正常、无照片、多个目标、资格缺口、内容压力和故障注入 fixtures，证明 schema、定向、分页和发布边界。
  3. Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw、Hermes Agent 均可按 canonical `SKILL.md`、CLI fallback 和安装期验证使用技能，主流程不含 runtime 私有语法。
  4. 在固定前置版本、受控 CJK 字体和至少一个非开发环境中，PDF/PNG 人工验收确认无字体 fallback 导致的页数或分页漂移。
**Plans**: 2 plans

Plans:
- [ ] 49-01: 建立 PDF 结构/内容/布局验证、聚合回归及故障注入证据。
- [ ] 49-02: 完成六 runtime adapter/安装 fixture 验证和跨环境字体固定 PDF/PNG UAT。

## Progress

**Execution Order:** Phase 46 -> Phase 47 -> Phase 48 -> Phase 49

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 46. 资料契约、字体与可验证夹具 | 3/3 | Completed | 2026-07-18 |
| 47. 受控主题、照片与冻结布局 | 3/3 | Complete   | 2026-07-18 |
| 48. 确定性定向渲染与干净批量交付 | 0/3 | Not started | - |
| 49. 聚合验证、跨 Runtime 与发布验收 | 0/2 | Not started | - |

## Traceability Coverage

| Requirement | Phase | Criterion |
|-------------|-------|-----------|
| SCHEMA-01 | Phase 46 | 1 |
| SCHEMA-02 | Phase 46 | 2 |
| SCHEMA-03 | Phase 46 | 3 |
| SCHEMA-04 | Phase 46 | 4 |
| THEME-01 | Phase 47 | 1 |
| THEME-02 | Phase 47 | 2 |
| THEME-03 | Phase 47 | 3 |
| THEME-04 | Phase 47 | 4 |
| THEME-05 | Phase 47 | 5 |
| TARGET-01 | Phase 48 | 1 |
| TARGET-02 | Phase 48 | 2 |
| TARGET-03 | Phase 48 | 3 |
| DELIVERY-01 | Phase 48 | 4 |
| DELIVERY-02 | Phase 48 | 5 |
| DELIVERY-03 | Phase 48 | 5 |
| VERIFY-01 | Phase 49 | 1 |
| VERIFY-02 | Phase 49 | 2 |
| VERIFY-03 | Phase 49 | 3 |
| VERIFY-04 | Phase 49 | 4 |

**Coverage:** 19/19 v1.19 requirements mapped exactly once; unmapped 0; duplicate mappings 0.

---
*Roadmap updated: 2026-07-18 for `graduate-resume/v2` source contract*
