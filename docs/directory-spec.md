# Directory Specification

本文档定义 Presto Agent Skills 的目录职责。新增文件时优先遵守这里的归属规则。

## Root

| Path | Purpose |
|------|---------|
| `README.md` | 给人类贡献者看的项目入口 |
| `AGENTS.md` | 给 coding agents 看的仓库规则和语言约束 |
| `adapters/` | runtime adapter 的说明和可扩展放置点 |
| `docs/` | 持久化项目说明、兼容性矩阵和目录契约 |
| `examples/` | 可选参考示例目录；仅在确实需要示例时创建，不是 v1 必需交付 |
| `skills/` | canonical 技能源文件 |
| `templates/` | 可复制的占位符模板 |
| `.planning/` | GSD 项目规划、需求、路线图和状态 |

## Skill Sources

| Path | Purpose |
|------|---------|
| `skills/<skill-name>/SKILL.md` | canonical 技能源文件 |
| `skills/<skill-name>/references/` | 可按需读取的长参考资料 |
| `skills/<skill-name>/scripts/` | 技能需要调用的辅助脚本 |
| `skills/<skill-name>/templates/` | 技能输出模板或文件模板 |

`skills/` 下的 `SKILL.md` 是 semantic source of truth。技能正文应该尽量 runtime-neutral；遇到 runtime 差异时，先写在同一个 `SKILL.md` 的 `Runtime Adapter Notes` 中。只有 notes 过长或安装步骤需要单独审阅时，才新增 `adapters/` 文档。不要复制出多份语义不同的技能。

## Templates

| Path | Purpose |
|------|---------|
| `templates/skill/SKILL.md` | 新技能的默认 canonical 模板，复制后即可作为 `skills/<skill-name>/SKILL.md` |
| `templates/adapter/runtime-adapter.md` | 可选的单个 runtime 兼容说明模板，用于补充过长的 adapter notes |

模板必须保持占位符形式，不应包含真实项目的业务逻辑。

## Runtime Adapters

| Path | Purpose |
|------|---------|
| `adapters/README.md` | 解释 adapter notes 的职责和最佳实践 |
| `docs/compatibility-matrix.md` | 记录各 runtime 的加载路径、能力差异和注意事项 |

后续如果某个 runtime 需要较复杂的安装说明，可以新增 `adapters/<runtime>/<skill-name>.md`。如果某个 runtime 真的需要 generated wrappers，必须先记录生成规则、来源 `SKILL.md`、安全边界和验证步骤；v1 不默认实现 wrapper。

## Examples

| Path | Purpose |
|------|---------|
| `examples/<example-name>/SKILL.md` | 可选参考示例，帮助读者对照 canonical 模板 |

当前 v1 不保留示例文件。只有在确实有贡献者参考价值时，才创建 `examples/` 并补充短小、可审阅的示例；示例必须优先让读者看见 `templates/skill/SKILL.md`，而且不要把它写成 v1 的硬要求。
