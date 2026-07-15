# Phase 45: 全技能干净交付目录标准化改造 - Context

**Gathered:** 2026-07-16
**Status:** Ready for planning

<domain>
## Phase Boundary

本阶段把 `docs/clean-delivery-directory-contract.md` 落实到当前六个会写文件的技能：`gongwen`、`tiaokedan`、`end-of-term-teaching-materials`、`teaching-design-package`、`school-presentation` 与 `school-pptx`。交付范围包括统一根目录白名单与支持目录语义、候选版本暂存和最小验证、旧成功版本成套归档、失败回滚与清理、既有公开命令和文档契约同步、六运行时兼容说明，以及历史 agent 散乱产物的确认式整理流程；不借此改变各技能的内容模型、版式、分页、评分、教学逻辑或最终产物格式。

</domain>

<decisions>
## Implementation Decisions

### 覆盖范围与交付边界
- 本阶段以仓库当前六个顶层技能目录为封闭改造清单；验收必须逐技能列出输入资料、当前 Markdown、最终产物、持续引用资源、旧成功版本、中间文件、验证证据和失败输出的归属，不能用抽样代表全量。
- 每个技能保留已交付的公开产物集合与稳定文件名语义：本阶段只改变这些文件如何候选、验证、归档和发布，不新增面向用户的 manifest、status、model、JSON、日志、截图或验证报告。
- `sources/` 仅保存用户明确要求长期保留的原始资料；`assets/` 保存当前 Markdown 或最终产物持续引用的资源，现有 `media/` 语义统一映射到 `assets/`，迁移文本引用时必须同步修正并验证，不能为方便复制全部输入。
- 现有 `.teaching-design-package/`、`.tiaokedan/` 等成功路径隐藏诊断不再作为交付根的长期例外；候选、中间模型、状态、stderr、验证证据和失败诊断统一进入本次 `.work/<run-id>/` 或系统临时目录，并在成功或失败收尾时清理。

### 候选发布与历史版本
- 每次会改变当前交付的运行都必须先在交付根内部的 `.work/<run-id>/` 生成完整候选集合；候选未完整生成并通过该技能的最小验证前，不得删除、覆盖、移动或截断根目录中的当前成功版本。
- 最小验证以现有技能 gate 为基础，并至少检查候选 Markdown 与声明的全部最终产物齐全、非空、格式可读以及持续资源引用有效；验证使用退出状态、内存或 `.work/<run-id>/` 内证据，不把证明性 sidecar 发布到根目录。
- 是否变化按“该技能声明的完整受管交付集合”逐文件内容比较，而不是只比较 Markdown、mtime 或文件名；候选与当前集合完全相同时不创建 `history/`，直接清理本次工作目录并保持当前文件不动。
- 内容变化时，在交付根内串行发布：取得同根临时锁，把上一套受管 Markdown 和全部最终产物整体移入下一个至少三位零填充的 `history/<sequence>/`，再发布完整候选；任一步失败都必须回滚到上一套成功版本，清理不完整候选，且绝不触碰白名单外或无法归属的现有文件。

### 脚本实现与仓库集成
- 保持六个技能现有 shell 公共入口、常用子命令和已发布参数可用；事务能力在各 skill folder 内自包含实现，不引入运行时 sibling skill 或仓库根脚本依赖，自动脚本发现不可用时继续提供显式调用 fallback。
- 共享的是一套可复验的发布协议和测试断言，而不是强迫所有 renderer 共用同一内部语言；各技能从既有 renderer 输出适配为“生成候选集合 → 验证 → 发布”，避免重写已稳定的内容生成逻辑。
- 验证矩阵必须覆盖六个技能的首次发布、发生变化的再次发布、完全相同的重复运行、生成失败、验证失败、发布中断、已有历史序号、根目录未知文件和空 `.work/` 清理；失败注入必须证明当前成功版本及既有历史哈希保持不变。
- 文档同步范围固定为根 `README.md`、`docs/directory-spec.md`、`docs/compatibility-matrix.md`、六个 canonical `SKILL.md` 及其实际 artifact contract reference，并同步更新新技能模板，使后续写文件技能默认继承同一边界。

### 历史整理与运行时安全
- 历史 agent 散乱产物整理保持“两阶段、确认门控”：第一阶段只读审计并给出安全移动、需确认归档、需明确批准删除三组计划；只有用户确认具体方案后才执行，不能被普通 render/deliver 命令自动触发。
- 整理和发布都必须拒绝越界路径、跨授权根符号链接、路径穿越和不受管文件覆盖；`.work/` 放在交付根内以保持同文件系统重命名条件，无法保证安全原子替换或回滚时应失败关闭。
- Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw 与 Hermes Agent 共用 canonical 工作流和交付语义；runtime notes 只说明发现、显式命令 fallback、依赖、allowlist/sandbox、写权限和安装时验证差异，OpenClaw 与 Hermes Agent 不得只写推测性支持声明。
- 对已存在的散乱文件、旧隐藏诊断目录或未知用户资料不做静默迁移和删除；本阶段自动化只管理由当前技能明确声明且由本次运行创建或识别为当前成功交付集合的文件，旧数据治理必须走确认式整理流程。

### Claude's Discretion
- `.work/<run-id>/` 的具体命名、同根锁文件布局、回滚日志的内存/临时表示以及 skill-local helper 的拆分方式可在规划时按可测试性决定，但不得扩大公开根白名单。
- 各格式“可读”的最小检查细节由实现根据既有 gate 决定；不得用昂贵的全量人工 UAT替代自动最小验证，也不得降低 `school-pptx` 等技能已有的最终人工验收要求。
- 历史序号超过三位、并发运行冲突提示和空 `sources/`、`assets/`、`history/`、`.work/` 的删除时机可采用保守标准做法；目录为空时不应为展示结构而预创建。

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/clean-delivery-directory-contract.md` 已定义根白名单、四个支持目录、版本归档顺序、失败不污染和未知文件保护，是本阶段共享语义源。
- `docs/agent-output-cleanup-prompt.md` 已提供历史散乱产物的两阶段审计/确认流程，可收敛为可复用且确认门控的正式工作流，而不需要重新发明清理策略。
- 六个技能均已有 canonical `SKILL.md`、skill-local shell 入口和 renderer/verification 资产；`school-pptx` 的 staged publish、`teaching-design-package` 的模块 staging/失败诊断、`school-presentation` 的 caller workdir 验证可作为迁移参考。

### Established Patterns
- 仓库坚持 Markdown-first、一个 canonical `SKILL.md`、长契约下沉到 skill-local `references/`、命令放在 `scripts/`，且 skill folder 必须可独立安装运行，不依赖 sibling skills。
- 现有技能已经普遍区分公开交付与验证/诊断，但实现不统一：有的直接写目标文件，有的写调用方 workdir，有的保留隐藏诊断目录；Phase 45 应统一生命周期而非抹平各自最终产物差异。
- 自动验证、结构检查和人工 UAT 是不同层级；尤其 `school-pptx` 的真实 PowerPoint/WPS 验收不能由代理或新的目录事务层自动签署。

### Integration Points
- 六个公共入口分别是 `skills/*/scripts/*.sh`；应在这些既有命令的交付路径接入候选生成、最小验证、差异判断、历史归档、发布和收尾，而不是绕过公共命令另建用户入口。
- 根 `README.md`、`docs/directory-spec.md`、`docs/compatibility-matrix.md` 与 `templates/skill/SKILL.md` 是仓库级发现和新技能继承点；技能级具体白名单和目录用途应留在各自 `SKILL.md`/artifact contract。
- 测试应复用各技能现有 fixture、模板和 verify 命令，并在测试专用临时目录中观察根目录、`history/` 与 `.work/` 状态，避免把测试证据写入普通交付目录。

</code_context>

<specifics>
## Specific Ideas

- 根目录中的稳定文件名始终代表当前最新版，明确禁止 `final-final`、`最终版2`、日期副本等平铺版本命名。
- 旧版本必须把 Markdown 与同次交付的所有最终产物放进同一个 `history/<sequence>/`，不能按文件类型或单个 artifact 分别编号。
- 历史整理优先复用现有“只读审计 → 用户确认 → 执行 → 最小收尾验证”提示词，并把未知文件零自动处置作为硬边界。

</specifics>

<deferred>
## Deferred Ideas

- 自动压缩、裁剪或删除 `history/`，以及为历史版本建立索引、manifest 或内容寻址存储。
- 自动判断并移动未知用户文件、扫描未授权目录，或在未经确认时治理里程碑之前产生的散乱文件。
- 新增 runtime-specific wrapper、独立 adapter 目录、托管发布服务或跨设备并发事务；本阶段只保证 canonical skill folder 内的本地交付工作流。

</deferred>
