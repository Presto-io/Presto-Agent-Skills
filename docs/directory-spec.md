# Directory Specification

本文档定义 Presto Agent Skills 的目录职责。新增文件时优先遵守这里的归属规则。

## Root

| Path | Purpose |
|------|---------|
| `README.md` | 给人类贡献者看的项目入口 |
| `AGENTS.md` | 给 coding agents 看的仓库规则和语言约束 |
| `docs/` | 持久化项目说明、兼容性矩阵、目录契约和 Markdown normalization contract |
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

`skills/` 下的 `SKILL.md` 是 semantic source of truth。它应该保留触发意图、目标、输入、核心流程、脚本调用入口、输出概览、验证入口、安全边界和 `Runtime Adapter Notes`。长格式规则、完整字段表、示例、renderer notes、artifact 明细、UAT 清单和排障说明应放进同一技能的 `references/`，并从 `SKILL.md` 显式链接。技能正文应该尽量 runtime-neutral；遇到 runtime 差异时，写在同一个 `SKILL.md` 的 `Runtime Adapter Notes` 中。v1 不维护独立 adapter 文件，也不要复制出多份语义不同的技能。

`references/` 是 skill-local progressive disclosure 区域，不是新的 canonical skill body。引用文件可以很详细，但必须服务 owning skill 的 workflow；不要把某个模板的 metadata fields、renderer rules 或 fixture 细节提升为全仓库通用 schema。`scripts/` 只放可调用辅助命令或内部模块；大型脚本可以拆成 CLI dispatch、parsing、rendering、artifact writing、verification/reporting 等 skill-local modules，但外层公共命令、常用 flags、输出文件名、manifest keys 和行为契约必须保持稳定。`templates/` 只放生成输出时复制、渲染或填充的文件模板，不要把长说明文档混进模板目录。

## Templates

| Path | Purpose |
|------|---------|
| `templates/skill/SKILL.md` | 新技能的默认 canonical 模板，复制后即可作为 `skills/<skill-name>/SKILL.md` |

模板必须保持占位符形式，不应包含真实项目的业务逻辑。模板里的 `SKILL.md` 也应体现轻入口模式：正文只写 agent 必须先读的语义和检查点，较长的规则应以 `references/<name>.md` 占位符链接表达。

## Runtime Compatibility

| Path | Purpose |
|------|---------|
| `docs/compatibility-matrix.md` | 记录各 runtime 的加载路径、能力差异和注意事项 |

runtime 差异优先写进 canonical `SKILL.md` 的 `Runtime Adapter Notes`。如果未来某个 runtime 真的需要独立说明或 generated wrapper，必须先重新打开范围，记录生成规则、来源 `SKILL.md`、安全边界和验证步骤；v1 不保留独立 adapter 目录，也不默认实现 wrapper。

## Document Workflow

| Path | Purpose |
|------|---------|
| `docs/markdown-normalization-contract.md` | 记录文档工作流技能共享的 Markdown intermediate 归一化契约 |

模板特定的 metadata fields、warning marker syntax、scripts 和 renderer rules 属于拥有它们的 skill/template，或后续目标格式文档；不要把这些差异提升成 universal shared schema。

## Shared References and Fixtures

| Path | Purpose |
|------|---------|
| `references/scheduling-contract.md` | v1.11 integrated teaching-design package 的共享排课合同，供后续 package skill 组合授课计划、教案和可选期末材料时引用 |
| `test/1.11/scheduling-contract/` | 排课合同 fixture evidence，包含可审阅 source、确定性 JSON 和 Markdown 调度证据 |
| `skills/teaching-design-package/SKILL.md` | v1.11 教学设计整包 skill 入口；它组合 `jiaoan-jihua`、`jiaoan-shicao` 和可选 `end-of-term-teaching-materials`，不替换原技能 |
| `skills/teaching-design-package/references/format-and-orchestration.md` | 整包长规则、模块交接、manifest/status 和 TDP traceability |
| `skills/teaching-design-package/templates/teaching-design-package-full.md` | 整包 Markdown intermediate 模板 |
| `skills/teaching-design-package/scripts/teaching-design-package.sh` | 整包公开 helper command |

根目录 `references/` 只放确实跨技能或未来 orchestration skill 复用的长参考资料。单一技能专属规则仍放在 `skills/<skill-name>/references/`。`test/` 下的版本化 fixture 可以被脚本和计划验证读取；如果仓库 `.gitignore` 默认忽略测试产物，必须只强制纳入明确计划要求的 deterministic fixture 文件。

## Examples

| Path | Purpose |
|------|---------|
| `examples/<example-name>/SKILL.md` | 可选参考示例，帮助读者对照 canonical 模板 |

当前 v1 不保留示例文件。只有在确实有贡献者参考价值时，才创建 `examples/` 并补充短小、可审阅的示例；示例必须优先让读者看见 `templates/skill/SKILL.md`，而且不要把它写成 v1 的硬要求。
