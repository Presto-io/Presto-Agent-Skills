# 理论卷交付契约

## DeliverySpec

生成前确定授权 `delivery_root` 与精确成员集合：每套 `<stem>.md`、`<stem>-理论试卷.docx`、`<stem>-理论答案与评分.docx`；需要 PDF 时加入对应同名 PDF。多套集合按显式套号合并，拒绝重复名和路径穿越。只在长期引用时登记 managed `assets/`，输入原件及题库只读。

支持目录仅 sources/assets/history/.work；不修改 sources、不自动清理历史。最小 gate 检查成员 regular/non-symlink、非空、Markdown UTF-8、DOCX ZIP 必需部件、PDF 可重开、资源引用、题量分值与答案映射及考生卷答案隔离、逐页视觉。

## 候选与发布

本技能不带自动 publisher。Agent 在授权根排他锁内建立 owned `.work/<run-id>/candidate`，完整生成并通过 gate 后检查现有根。unknown、symlink、特殊文件、partial/重复组和编辑器占用先拒绝，不擅自搬移。

exact relative path-set + bytes 相同即 no-op，不动 current/history。changed 先备份并复验旧完整组，含 managed assets 的旧组同版进入 history 的 max+1 序号，再逐路径替换、复核。handled error/INT/TERM 恢复旧组、移除本次新增文件和未提交 history，清理本次 owned work 并释放锁；不保证断电/SIGKILL/跨文件原子。历史不自动删除。

模型、manifest、截图和日志只在 owned work 或显式 verification workdir。无法落实发布/回滚流程时仅交候选并注明未发布；未实现自动回归，不登记进已有六技能自动干净交付覆盖。
