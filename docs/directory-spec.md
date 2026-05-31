# Directory Specification

本文档定义 Presto Agent Skills 的目录职责。新增文件时优先遵守这里的归属规则。

## Root

| Path | Purpose |
|------|---------|
| `README.md` | 给人类贡献者看的项目入口 |
| `AGENTS.md` | 给 coding agents 看的仓库规则和语言约束 |
| `docs/` | 持久化项目说明、兼容性矩阵、目录契约和 Markdown normalization contract |
| `examples/` | 可选参考示例目录；仅在确实需要示例时创建，不是 v1 必需交付 |
| `skills/` | canonical 技能源文件 |
| `templates/` | 可复制的占位符模板 |
| `.planning/` | GSD 项目规划、需求、路线图和状态 |

## Skill Sources

| Path | Purpose |
|------|---------|
| `skills/<skill-name>/SKILL.md` | canonical 技能源文件 |
| `skills/<skill-name>/references/` | 可按需读取的长参考资料、支持文件和格式说明 |
| `skills/<skill-name>/scripts/` | 技能需要调用的辅助脚本 |
| `skills/<skill-name>/templates/` | 技能输出模板或文件模板 |

`skills/` 下的 `SKILL.md` 是 semantic source of truth。技能正文应该尽量 runtime-neutral；遇到 runtime 差异时，写在同一个 `SKILL.md` 的 `Runtime Adapter Notes` 中。v1 不维护独立 adapter 文件，也不要复制出多份语义不同的技能。

## Templates

| Path | Purpose |
|------|---------|
| `templates/skill/SKILL.md` | 新技能的默认 canonical 模板，复制后即可作为 `skills/<skill-name>/SKILL.md` |

模板必须保持占位符形式，不应包含真实项目的业务逻辑。

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

## Examples

| Path | Purpose |
|------|---------|
| `examples/<example-name>/SKILL.md` | 可选参考示例，帮助读者对照 canonical 模板 |

当前 v1 不保留示例文件。只有在确实有贡献者参考价值时，才创建 `examples/` 并补充短小、可审阅的示例；示例必须优先让读者看见 `templates/skill/SKILL.md`，而且不要把它写成 v1 的硬要求。
