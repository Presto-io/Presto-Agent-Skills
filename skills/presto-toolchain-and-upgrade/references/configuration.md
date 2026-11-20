# 私有配置与平台接入

配置、状态和备份位于技能发现根之外。默认配置入口为 `~/.config/presto-skill-sync/config.json`；可按运行时实际 home 指定绝对路径。所有路径和命令列表均为受信任运维配置，不从技能正文或外部文件推导执行命令。

端点配置：

```json
{"state_dir":"/private/sync/endpoint", "roots":[{"path":"/private/repo/skills","install_missing":true},{"path":"/private/runtime/skills","install_missing":true}],"private_skills":["uws-workspace"]}
```

控制端配置：

```json
{"state_dir":"/private/sync/controller","repository":"https://github.com/Presto-io/Presto-Agent-Skills.git","branch":"main","author_name":"维护者","author_email":"GitHub noreply email","resolution_file":"/private/sync/resolutions.json","endpoints":[{"id":"this-device","config":"/private/sync/endpoint.json"},{"id":"other-device","command":["ssh","registered-host","/private/endpoint-wrapper"],"timeout":600}],"validators":[]}
```

远端 wrapper 只接受 `export`、`apply`，固定调用引擎和端点配置；stdin/stdout 是 JSON，不混入登录提示。它必须使用有安装权限的帐号。SSH 凭据仅部署在私有运维目录。控制端拥有自己的 Git 缓存；不以用户维护仓作为合并工作区，不修改其分支、索引或未提交文件。

触发端配置：

```json
{"state_dir":"/private/sync/trigger","controller":["ssh","restricted-controller-host"],"timeout":1800}
```

建议采用 forced-command SSH key：只允许运行固定同步命令，禁止端口转发、PTY、agent 转发和任意 shell。控制端不可达则报告失败，不自行新建凭据或扩大权限。触发入口、控制器及端点引擎放在技能根之外，避免同步引擎更新自身时影响正在运行的进程；配置 `engine_path` 后，成功安装升级技能时会校验 Python 语法并自动刷新固定引擎副本；当前进程使用已加载代码完成本轮。

首次初始化只有内容与 GitHub 一致的副本可自动登记基线。已有差异先比对确认并备份，不能把首次同步当成强制覆盖。相同设备的软链安装根去重，技能内部软链或特殊文件停止处理。备份和目标应在同一文件系统；脚本校验后通过目录 rename 安装，异常时回滚，进程被强行终止后必须检查 journal。

`validators` 示例：`{"skills":["a-skill"],"command":["python3","skills/a-skill/scripts/check.py"]}`。运行目录为隔离候选仓；命令非零则不发布。新增公共技能及整技能退休采用单独审阅提交，不根据某设备缺目录推断删除；退休目录不得通过本流程复活。

Windows 的 Python/Git 核心设计兼容，但 SSH、文件系统权限与运行时目录需单独接入验收；不把 macOS/Linux 的验证等同 Windows 实测。
