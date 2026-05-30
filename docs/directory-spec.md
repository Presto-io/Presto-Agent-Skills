# Directory Specification

本文档定义 Presto Agent Skills 的目录职责。新增文件时优先遵守这里的归属规则。

## Root

| Path | Purpose |
|------|---------|
| `README.md` | 给人类贡献者看的项目入口 |
| `AGENTS.md` | 给 coding agents 看的仓库规则和语言约束 |
| `.planning/` | GSD 项目规划、需求、路线图和状态 |

## Skill Sources

| Path | Purpose |
|------|---------|
| `skills/<skill-name>/SKILL.md` | canonical 技能源文件 |
| `skills/<skill-name>/references/` | 可按需读取的长参考资料 |
| `skills/<skill-name>/scripts/` | 技能需要调用的辅助脚本 |
| `skills/<skill-name>/templates/` | 技能输出模板或文件模板 |

`skills/` 下的内容应该尽量 runtime-neutral。遇到 runtime 差异时，在技能内的 adapter section 或 `adapters/` 中记录，而不是复制出多份语义不同的技能。

## Templates

| Path | Purpose |
|------|---------|
| `templates/skill/SKILL.md` | 新技能的 canonical 模板 |
| `templates/adapter/runtime-adapter.md` | 单个 runtime 适配说明模板 |

模板必须保持占位符形式，不应包含真实项目的业务逻辑。

## Runtime Adapters

| Path | Purpose |
|------|---------|
| `adapters/README.md` | 解释 adapter 的职责和最佳实践 |
| `docs/compatibility-matrix.md` | 记录各 runtime 的加载路径、能力差异和注意事项 |

后续如果某个 runtime 需要较复杂的生成规则，可以新增 `adapters/<runtime>/README.md`。

## Examples

| Path | Purpose |
|------|---------|
| `examples/<example-name>/SKILL.md` | 展示 canonical 模板的真实用法 |

示例必须可读、短小，并覆盖所有必选 runtime 的 adapter notes。
