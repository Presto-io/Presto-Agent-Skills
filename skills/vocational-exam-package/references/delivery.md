# 整包交付契约

包级 Markdown 的公开成员表是唯一变更对象清单。`current_names` 为包级 Markdown 加所有显式套号的审阅稿和最终 DOCX；合并实操角色、可选 PDF/ZIP 均通过成员表确定精确集合。不能要求用户为此额外维护 JSON/CSV sidecar。依赖技能仅产候选，主流程拥有唯一发布事务。

`delivery_root` 必须为授权真实目录。仅允许 sources/assets/history/.work；sources 原件只读，managed assets 仅登记持续引用的资源。最小 gate 检查每个成员 regular/non-symlink、非空、可读，DOCX 必需部件、PDF 重开、ZIP 精确内容清单与资源引用；再检查全套题号/角色/标准/版本、答案评分配对、分值时间覆盖及每页视觉。

发布前取得同根排他锁，整包候选进入 owned `.work/<run-id>/candidate`。验证成功后检查零套或一套完整 current；unknown/partial/重复组、symlink、特殊文件、路径穿越和编辑器占用在变更前拒绝，不能自动整理。

路径集合和 bytes 全等为 no-op，不创建 history。changed 先备份完整旧组到 rollback 并复验，将整个旧包连同 managed assets 归档 `history/<max+1>`，逐路径替换候选并复验 current。任一成员失败不得发布部分新包；handled error/INT/TERM 恢复旧组，移除本次新引入文件和未提交 history，仅清理本次 owned work 并释放锁。历史不自动删除，不宣称 SIGKILL、断电或跨文件硬原子。

目前由 agent 按此合同组织可用工具，无内置已回归 publisher；不能声称已加入仓库六技能自动干净交付覆盖。无法完成发布保证时停在候选，说明实际状态。验证报告、日志、截图、模型不进入公开根；显式 verification workdir 不由发布流程扫描或清理。
