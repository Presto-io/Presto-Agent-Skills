# Templates

这里存放可复制的模板。

- `skill/SKILL.md`：默认入口。复制到 `skills/<skill-name>/SKILL.md`，作为一个 portable skill 的 canonical 源文件。

模板中的占位符使用尖括号，例如 `<skill-name>`。复制后必须替换为真实内容。

所有写文件的技能模板实例必须填写 `Delivery Directory`，并遵守 `docs/clean-delivery-directory-contract.md`。一级目录只保留当前 Markdown 和最终交付产物，多轮修改统一进入 `history/`，临时验证进入 `.work/` 并在收尾时清理。

优先保持一个 `SKILL.md` 可读、可复制、可安装。不要把同一套技能流程复制到多个 runtime 文件中；runtime 差异写在 `SKILL.md` 的 `Runtime Adapter Notes` 中。如果未来某个 runtime 必须生成 wrapper，先重新打开范围并说明生成规则、安全边界和验证步骤。
