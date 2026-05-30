# Templates

这里存放可复制的模板。

- `skill/SKILL.md`：默认入口。复制到 `skills/<skill-name>/SKILL.md`，作为一个 portable skill 的 canonical 源文件。
- `adapter/runtime-adapter.md`：可选补充。只有当 `SKILL.md` 内嵌的 runtime adapter notes 放不下时，才为单个 runtime 追加独立兼容说明。

模板中的占位符使用尖括号，例如 `<skill-name>`。复制后必须替换为真实内容。

优先保持一个 `SKILL.md` 可读、可复制、可安装。不要把同一套技能流程复制到多个 runtime 文件中；如果未来某个 runtime 必须生成 wrapper，先在 adapter notes 中说明生成规则和验证步骤。
