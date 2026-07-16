# Requirements: Presto Agent Skills v1.18 全技能干净交付目录标准化改造

**Defined:** 2026-07-16
**Core Value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## v1.18 Requirements

### Skill Coverage And Directory Contract

- [ ] **CLEAN-01**: `end-of-term-teaching-materials`、`gongwen`、`school-pptx`、`school-presentation`、`teaching-design-package` 和 `tiaokedan` 六个当前写文件技能都遵守 `docs/clean-delivery-directory-contract.md`，且既有成功交付能力不回退。
- [x] **CLEAN-02**: 每个技能都为交付根目录声明可核对的一级白名单，仅允许当前 Markdown、当前最终产物以及按需存在的 `sources/`、`assets/`、`history/`、`.work/`。
- [x] **CLEAN-03**: 每个技能都明确 `sources/`、`assets/`、`history/`、`.work/` 的所有权和生命周期；manifest、status、model、日志、diff、截图、缓存、验证证据、staging 和失败产物不得作为未声明文件平铺在成功交付根目录。

### Candidate Publication And Revision History

- [x] **REV-01**: 六个技能的修改流程都先在 `.work/<run-id>/` 生成一整套候选 Markdown 和最终产物，候选通过发布门前不得覆盖或移动根目录中的当前成功版本。
- [x] **REV-02**: 候选发布前只执行证明该技能交付可用所需的最小验证，包括声明产物齐全、非空且可读取；验证不得在成功交付根目录留下额外持久证据。
- [x] **REV-03**: 当候选受管文件与当前成功版本逐文件内容相同时，技能不创建新的 `history/<sequence>/`，并清理本次候选和临时证据。
- [x] **REV-04**: 当验证成功且内容发生变化时，技能先把上一版 Markdown 和与其同版的全部最终产物成套移入下一个零填充 `history/<sequence>/`，再以稳定文件名发布整套新版本；同一版不得拆分编号，也不得自动删除历史版本。

### Failure Safety And Historical Cleanup

- [x] **SAFE-01**: 生成、验证、归档或发布任一步失败时，根目录中的当前成功版本保持可用且内容不变；不完整候选、临时证据和空 `.work/` 被清理，失败产物不得伪装为当前交付。
- [x] **SAFE-02**: 散乱历史 agent 产物整理流程首次运行只做授权范围内的只读审计；任何未知文件或用户资料在移动、归档、重命名、隔离或删除前，都必须列出计划并取得用户明确确认。

### Verification, Documentation And Runtime Portability

- [x] **VERIFY-01**: 自动化回归覆盖六个技能的成功发布、变更后成套归档、内容相同不归档、失败不污染和工作目录收尾，并证明成功交付根目录符合各自白名单。
- [ ] **DOCS-01**: `SKILL.md`、artifact contract、相关模板和公共脚本对稳定文件名、目录用途、候选发布、成套归档、失败清理和最小验证的描述与行为一致；README 与目录规范同步反映统一契约和六技能覆盖范围。
- [ ] **RUNTIME-01**: Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw 和 Hermes Agent 的兼容性矩阵及六个技能 adapter notes 一致说明支持文件发现、外部命令、读写权限、sandbox/allowlist、显式调用 fallback 和干净交付边界。

## Out Of Scope

| Feature | Reason |
|---------|--------|
| 自动删除或压缩 `history/` 中的旧成功版本 | 历史保留策略必须由用户另行决定。 |
| 未经确认批量整理未知文件、用户原始资料或授权范围外目录 | v1.18 要求确认门和保守处理，不能把疑似散乱文件直接视为垃圾。 |
| 改变六个技能的内容模型、版式、渲染能力或公开交付格式 | 本里程碑只标准化交付目录和版本发布生命周期。 |
| 为不同 runtime 维护分叉的 canonical workflow | runtime 差异继续只放在 adapter notes 和兼容性说明。 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CLEAN-01 | Phase 45 | Pending |
| CLEAN-02 | Phase 45 | Complete |
| CLEAN-03 | Phase 45 | Complete |
| REV-01 | Phase 45 | Complete |
| REV-02 | Phase 45 | Complete |
| REV-03 | Phase 45 | Complete |
| REV-04 | Phase 45 | Complete |
| SAFE-01 | Phase 45 | Complete |
| SAFE-02 | Phase 45 | Complete |
| VERIFY-01 | Phase 45 | Complete |
| DOCS-01 | Phase 45 | Pending |
| RUNTIME-01 | Phase 45 | Pending |

**Coverage:**
- v1.18 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0

---
*Requirements defined: 2026-07-16*
