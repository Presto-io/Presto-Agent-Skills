# 集中处理冲突

结果记录在本机 `state_dir/last-result.json`，冲突报告在其指向的 `runs/<run>/conflicts.json`。常规文件冲突包含技能、文件、设备、根目录、原因、唯一 id 和 base/local/github 的哈希；对应原始字节保存在 `versions` 目录。报告中的 github 是合并到该来源时的候选内容，可能已包含其他设备的非冲突修改。

集中展示冲突清单，先解释差异和已有用户约定，再让用户决定无法确定的事项。允许 agent 按当前已明确的要求整理候选，但不得把未经决定的同段修改静默丢弃。

在私有 `resolution_file` 中按冲突 id 填写：

```json
{"<报告中的id>":{"take":"local"},"<另一id>":{"path":"/private/review/resolved-file.md","mode":420}}
```

`take` 可为 `base`、`local`、`github`；自定义 path 是完整解决后的文件，mode 420=0644，493=0755。然后重新执行 sync，重新收集本机副本并校验。决定绑定具体内容哈希，任一来源内容改变后旧决定失效，重新报告；不会按文件名永久记住“某端优先”。删除文件也只可通过该冲突的明确选择决定。

“无可信基线”不是常规文件冲突，不能用上述 id 强行采纳。应先保留全部副本、审阅差异、完成一次明确的初始统一，再让相等内容登记；不得凭猜测制造基线。

安装失败时查看 pending 与端点外置 backups。`journal.json` 为 prepared 表示可能中断，先比较 before 清单、当前目标和 previous 备份，恢复原状态或确认全部新状态后记录处理结果，再把 journal 标为 recovered。不要盲删目标或备份。脚本的自动异常回滚不等同断电恢复。

新增文件或二进制变更的发布清单为 `publication-review.json`。逐项核实无业务资料、重复素材或凭据后，将其 `approval` 字符串放入本机 `approved_publication` 数组，再重试。审批绑定具体 SHA，文件改变后需重新审阅；这与合并冲突的 resolution_file 分开。
