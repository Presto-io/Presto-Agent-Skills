# Directory Specification

本文档定义 Presto Agent Skills 的目录职责。新增文件时优先遵守这里的归属规则。

## Root

| Path | Purpose |
|------|---------|
| `README.md` | 给人类贡献者看的项目入口 |
| `AGENTS.md` | 给 coding agents 看的仓库规则和语言约束 |
| `docs/` | 持久化项目说明、兼容性矩阵、目录契约、干净交付约束、可复用操作提示词和 Markdown normalization contract |
| `examples/` | 可选参考示例目录；仅在确实需要示例时创建，不是 v1 必需交付 |
| `references/` | 跨技能或未来 orchestration skill 共享的长参考资料；例如 `references/scheduling-contract.md` |
| `skills/` | canonical 技能源文件 |
| `test/` | 版本化 fixture 和 deterministic evidence；例如 `test/1.11/scheduling-contract/` |
| `templates/` | 可复制的占位符模板 |
| `.planning/` | GSD 项目规划、需求、路线图和状态 |

## Skill Sources

| Path | Purpose |
|------|---------|
| `skills/<skill-name>/SKILL.md` | canonical 技能源文件 |
| `skills/<skill-name>/references/` | 可按需读取的长参考资料、支持文件和格式说明 |
| `skills/<skill-name>/scripts/` | 技能需要调用的辅助脚本 |
| `skills/<skill-name>/templates/` | 技能输出模板或文件模板 |
| `skills/school-pptx/fixtures/` | `school-pptx` skill-local canonical Markdown 与 companion media；由 public `example` 复制，不是通用模板目录 |

`skills/` 下的 `SKILL.md` 是 semantic source of truth。它应该保留触发意图、目标、输入、核心流程、脚本调用入口、输出概览、验证入口、安全边界和 `Runtime Adapter Notes`。长格式规则、完整字段表、示例、renderer notes、artifact 明细、UAT 清单和排障说明应放进同一技能的 `references/`，并从 `SKILL.md` 显式链接。技能正文应该尽量 runtime-neutral；遇到 runtime 差异时，写在同一个 `SKILL.md` 的 `Runtime Adapter Notes` 中。v1 不维护独立 adapter 文件，也不要复制出多份语义不同的技能。

`references/` 是 skill-local progressive disclosure 区域，不是新的 canonical skill body。引用文件可以很详细，但必须服务 owning skill 的 workflow；不要把某个模板的 metadata fields、renderer rules 或 fixture 细节提升为全仓库通用 schema。`scripts/` 只放可调用辅助命令或内部模块；大型脚本可以拆成 CLI dispatch、parsing、rendering、artifact writing、verification/reporting 等 skill-local modules，但外层公共命令、常用 flags、输出文件名、manifest keys 和行为契约必须保持稳定。`templates/` 只放生成输出时复制、渲染或填充的文件模板，不要把长说明文档混进模板目录。

这些路径描述的是 canonical repository ownership，不是用户 delivery root。安装技能时复制整个 `skills/<skill-name>/`，保留 `SKILL.md` 及实际存在的 `references/`、`scripts/`、`templates/` 和 skill-local fixture；不要为 Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw 或 Hermes Agent 创建 runtime-specific adapter folder，也不要复制分叉 workflow。

## User Delivery Roots

当前 clean-delivery coverage 是封闭六技能集合：`end-of-term-teaching-materials`、`gongwen`、`school-presentation`、`school-pptx`、`teaching-design-package`、`tiaokedan`。它们的用户交付根遵守 [canonical clean-delivery contract](clean-delivery-directory-contract.md)，但各自稳定 current 文件名和 optional/dynamic managed set 仍由 owning `SKILL.md` 与 artifact contract 声明。

```text
<authorized-delivery-root>/
├── <current-markdown>
├── <current-final-artifact(s)>
├── sources/   # optional；普通发布不修改
├── assets/    # optional；仅显式 managed、持续引用的内容随版归档
├── history/   # optional；完整旧 bundle 使用 max + 1 序号
└── .work/     # optional；仅 owned run 的 candidate/rollback/evidence
```

- current 是显式 managed relative-name set，不通过 glob、扩展名或“看起来像产物”猜测；optional artifact 的存在会改变 exact set。
- candidate 完整生成并通过最小 gate 后才可变更 current；exact path-set+bytes 相同是 no-op，changed 才创建 whole-bundle history。
- unknown、legacy hidden directory、legacy `media/`、symlink、partial 或 ambiguous group 必须在 mutation 前失败关闭，并按 [确认式 cleanup contract](agent-output-cleanup-prompt.md) 处理。
- normal render 不得持久化 manifest、status、model、log、diff、screenshot、staging、缓存、验证证据或 failed artifact 到成功根。空 support directory 不是必需 current；owned `.work` 在 success、no-op 或 handled failure 后应收尾。
- `verify --workdir <caller-evidence-root>` 一类路径由调用方拥有，用于持久 verification evidence；它不是 delivery root，也不得被普通 publisher 扫描、归档或清理。
- portable guarantee 仅包括 candidate isolation、单路径 replace 和 handled failure/`INT`/`TERM` rollback；不得写成 `SIGKILL`、断电或多文件跨路径硬原子。

## Templates

| Path | Purpose |
|------|---------|
| `templates/skill/SKILL.md` | 新技能的默认 canonical 模板，复制后即可作为 `skills/<skill-name>/SKILL.md` |

模板必须保持占位符形式，不应包含真实项目的业务逻辑。模板里的 `SKILL.md` 也应体现轻入口模式：正文只写 agent 必须先读的语义和检查点，较长的规则应以 `references/<name>.md` 占位符链接表达。

## Runtime Compatibility

| Path | Purpose |
|------|---------|
| `docs/compatibility-matrix.md` | 记录各 runtime 的加载路径、能力差异和注意事项 |

runtime 差异优先写进 canonical `SKILL.md` 的 `Runtime Adapter Notes`。如果未来某个 runtime 真的需要独立说明或生成式运行时 shim，必须先重新打开范围，记录生成规则、来源 `SKILL.md`、安全边界和验证步骤；v1 不保留独立 adapter 目录，也不默认实现 wrapper。

`school-pptx` 的 normalized `.pptx` 与 manifest 归 `skills/school-pptx/templates/`，canonical fixture 归 skill-local `fixtures/`。可复用 viewer checklist 归该 skill 的 `references/visual-uat.md`；具体里程碑的 tester、viewer、timestamp、artifact hash 和逐项结果只归 `.planning/phases/<phase>/`，不得进入公开 delivery、canonical reference 或 template。

## Document Workflow

| Path | Purpose |
|------|---------|
| `docs/markdown-normalization-contract.md` | 记录文档工作流技能共享的 Markdown intermediate 归一化契约 |
| `docs/clean-delivery-directory-contract.md` | 记录所有写文件技能共享的交付一级目录、多轮修改归档、最小验证和失败清理约束 |
| `docs/agent-output-cleanup-prompt.md` | 提供审计、整理和安全清理历史 agent 散乱产物的可复用提示词 |

模板特定的 metadata fields、warning marker syntax、scripts 和 renderer rules 属于拥有它们的 skill/template，或后续目标格式文档；不要把这些差异提升成 universal shared schema。

所有写文件的技能都必须遵守 `docs/clean-delivery-directory-contract.md`。技能可以收紧公开文件白名单，但不得把中间模型、验证证据、失败产物或平铺历史版本重新放回交付根目录。

## Shared References and Fixtures

| Path | Purpose |
|------|---------|
| `references/scheduling-contract.md` | v1.11 integrated teaching-design package 的共享排课合同，供后续 package skill 组合授课计划、教案和可选期末材料时引用 |
| `test/1.11/scheduling-contract/` | 排课合同 fixture evidence，包含可审阅 source、确定性 JSON 和 Markdown 调度证据 |
| `skills/teaching-design-package/SKILL.md` | 教学设计整包 skill 入口；它用 package-owned model、skill-local calendar 和包内 renderer 生成授课进度计划表、教学设计方案及可选整包交付，正常运行不依赖 sibling skill folders |
| `skills/teaching-design-package/references/format-and-orchestration.md` | 整包长规则、模块交接、manifest/status 和 TDP traceability |
| `skills/teaching-design-package/templates/teaching-design-package-full.md` | 整包 Markdown intermediate 模板 |
| `skills/teaching-design-package/scripts/teaching-design-package.sh` | 整包公开 helper command |
| `skills/tiaokedan/SKILL.md` | 调课单 skill 入口；从教师调课事实到 `tiaokedan.md`、Typst 和可选 PDF 的 Markdown-first 工作流 |
| `skills/tiaokedan/references/markdown-contract.md` | 调课单字段契约、必填/可选事实、复核标记和 renderer-owned defaults |
| `skills/tiaokedan/references/pdf-workflow.md` | 调课单 PDF gate、candidate/history/rollback、owned `.work` 和验证命令 |
| `skills/tiaokedan/templates/tiaokedan.md` | 调课单教师可审阅 Markdown intermediate 模板 |
| `skills/tiaokedan/scripts/tiaokedan.sh` | 调课单公开 helper command |

根目录 `references/` 只放确实跨技能或未来 orchestration skill 复用的长参考资料。单一技能专属规则仍放在 `skills/<skill-name>/references/`。`test/` 下的版本化 fixture 可以被脚本和计划验证读取；如果仓库 `.gitignore` 默认忽略测试产物，必须只强制纳入明确计划要求的 deterministic fixture 文件。

## Examples

| Path | Purpose |
|------|---------|
| `examples/<example-name>/SKILL.md` | 可选参考示例，帮助读者对照 canonical 模板 |

当前 v1 不保留示例文件。只有在确实有贡献者参考价值时，才创建 `examples/` 并补充短小、可审阅的示例；示例必须优先让读者看见 `templates/skill/SKILL.md`，而且不要把它写成 v1 的硬要求。
