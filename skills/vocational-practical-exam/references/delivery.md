# 交付契约

本技能由 agent 使用可用工具生成与发布，不提供已验证的自动 publisher。遵循下列流程；无法落实事务与回滚时只生成候选并报告未发布，不能声称实现了自动干净交付。

## DeliverySpec

- `delivery_root` 是用户授权的真实目录；当前文件名在生成前逐项列明。单套默认 `<stem>.md`、`<stem>-实操试卷.docx`、`<stem>-实操评分表.docx`；合并母版改为 `<stem>.md`、`<stem>-实操试卷及评分表.docx`。多套取明确套号成员的并集，不能按 glob 猜测变更对象。
- PDF 模式把对应同名 `.pdf` 加入集合。资源仅在明确持续引用时登记到 managed `assets/`；不默认复制题库或模板。
- 支持目录仅 `sources/`、`assets/`、`history/`、`.work/`。普通发布不修改 sources；不自动迁移旧散乱产物。
- 最小验证为所有成员存在、regular/non-symlink、非空、UTF-8 Markdown 可读、DOCX ZIP 可打开且含 document/styles/relationships、PDF 有效且可重开、引用可解析；加上逐字/分值/评分/分页/视觉检查。

## 发布

在授权根取得排他锁；所有候选先写 owned `.work/<run-id>/candidate/`，证据写 evidence。检查现有根目录只存在允许目录和零套或一套完整受管组，拒绝 unknown、partial、重复组、symlink、特殊文件、路径穿越或占用文件。

比较精确路径集合与 bytes：完全一致不改 current、不建 history。不同则先备份完整旧组到 rollback 并核对；将同版旧组及 managed assets 存入 `history/<max+1>/`，再逐路径替换候选。发布后复核完整集合与可读性。

捕获错误或 INT/TERM 时恢复旧组、移除本次新文件与未提交 history，仅清理本次 owned 路径并释放锁。不承诺 SIGKILL、断电或多文件硬原子。成功后清理本次 work；已有 history 不自动删除。报告/模型/日志/PNG 不是公开 current。

这是流程要求，尚无自动 publisher 回归证据；禁止把它登记为仓库既有六技能自动干净交付覆盖之一。
