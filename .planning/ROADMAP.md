# Roadmap: Presto Agent Skills

**Created:** 2026-05-30
**Last updated:** 2026-07-16 after defining v1.18 requirements and Phase 45 acceptance
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

## Next Milestone

### Phase 45: 全技能干净交付目录标准化改造

**Goal:** 在 v1.17 结束后，依据 `docs/clean-delivery-directory-contract.md` 完整改造当前全部技能，统一交付一级目录、支持资料分组、多轮修改成套归档、最小验证和失败清理行为，并为历史 agent 散乱产物整理提供可复用流程。
**Requirements:** CLEAN-01, CLEAN-02, CLEAN-03, REV-01, REV-02, REV-03, REV-04, SAFE-01, SAFE-02, VERIFY-01, DOCS-01, RUNTIME-01
**Depends on:** Phase 44
**Plans:** 0 plans

**Success Criteria** (what must be TRUE):
  1. 用户在六个写文件技能的成功交付根目录中只看到各技能声明的当前 Markdown、当前最终产物和按需存在的 `sources/`、`assets/`、`history/`、`.work/`，既有交付能力不回退。
  2. 用户修改任一技能交付时，完整候选先在 `.work/<run-id>/` 生成并通过该技能最小验证，验证证据、staging、日志和失败产物不会平铺到成功交付根目录。
  3. 用户发布内容发生变化的新版本时，上一版 Markdown 和全部同版最终产物进入同一个下一序号 `history/<sequence>/`，新版本以稳定文件名成套成为根目录当前版本。
  4. 用户提交与当前版本逐文件内容相同的候选时不会得到重复历史版本；任一步失败时当前成功版本保持不变，不完整候选和临时工作目录被清理。
  5. 用户可以运行覆盖六个技能的回归验证，证明成功发布、变更归档、相同内容不归档、失败不污染、根目录白名单和最小验证收尾均符合契约。
  6. 用户使用历史 agent 产物整理流程时，首次运行只收到授权范围内的审计与操作计划；未知文件和用户资料未经明确确认不会被移动、归档、重命名、隔离或删除。
  7. 用户可以从 README、目录规范、artifact contract、相关模板、六个 canonical `SKILL.md` 和兼容性矩阵读到一致规则，且 Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw、Hermes Agent 的 adapter notes 明确相同的写入安全边界与 fallback。

Plans:
- [ ] 盘点全部技能的输入、Markdown、最终产物、历史版本、中间文件和失败输出边界
- [ ] 为每个技能补齐根目录白名单、`sources/`、`assets/`、`history/`、`.work/` 和版本发布规则
- [ ] 改造公共脚本，使候选版本先进入 `.work/`，成功后成套归档旧版本并原子发布新版本
- [ ] 删除非必要持久验证产物，并验证失败运行不会污染当前成功交付
- [ ] 更新 README、目录规范、兼容性矩阵、技能入口和 artifact contract
- [ ] 补齐六技能成功、变更、相同内容、失败和未知文件确认门的端到端回归

---
*Roadmap updated: 2026-07-16 after defining v1.18 requirements and Phase 45 acceptance*
