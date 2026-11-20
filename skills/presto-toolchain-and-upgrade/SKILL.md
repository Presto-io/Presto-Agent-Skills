---
name: presto-toolchain-and-upgrade
description: 各设备独立将本机公开技能修改合并发布到 GitHub，并更新本机安装；用于技能升级、跨设备同步和冲突处理。
metadata:
  version: "0.3.0"
  portability: canonical
  supported-runtimes: [Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, Hermes Agent, DeepSeek Harness]
---

# Presto 技能同步升级

用户要求升级、同步，或完成本次已授权的技能修改后，在当前设备执行一次“收集本机副本 → 与 GitHub 三方合并 → 校验 → 推送 GitHub main → 安装本机 → 哈希回读”。各设备仅通过 GitHub 交换版本，其他设备离线不影响本机。其他设备在各自下次执行时更新，不声称一次调用会即时更新所有离线设备。不作为公文、教学、PPT 等业务工作的前置技能，也不启动后台定时任务。

使用本机私有配置 `~/.config/presto-skill-sync/config.json`，运行本技能的 `scripts/skill_sync.py --config <配置绝对路径> sync`。使用 `mode: device`、本机 `installation` 和本机独立基线/缓存；不登记其他设备，不使用远程控制器、跳板或中继。只读运行时可通过同一宿主机 Unix socket 请求本地安装服务。首次配置及平台适配见 [references/configuration.md](references/configuration.md)。不得把真实设备配置、密钥、业务资料或同步状态放进公开仓库。

## 合并规则

- GitHub main 是共同发布源；本平台修改也必须先上传，不能简单拉取覆盖。比较每个安装副本的上次成功基线、当前内容、GitHub 内容。
- 同一改动去重，单边改动保留，不重叠的 UTF-8 文字由 Git 三方合并；不得以版本号、时间戳、设备地位决定覆盖。
- 同段文字、二进制双改、删除与修改冲突、首次无基线却内容不同，停止发布并保留现场。统一告诉用户技能名、文件、来源设备和冲突原因；处理方法见 [references/conflicts.md](references/conflicts.md)。不要逐个弹问，也不要猜测用户取舍。
- 新技能须先审阅可公开内容并纳入 GitHub main，才进入自动同步名单。`uws-workspace` 等私有技能不通过公开 GitHub 同步；按独立私有渠道维护。已封存技能不上传、不重新安装。
- 设备资料路径、凭据、权限与运行时开关保留在私有配置；不要把它们作为共同技能文本传播。不得为安装改变业务技能的启用/禁用状态。

## 执行与验收

执行前检查本次修改清单和发布内容，排除真实学生资料、照片、成品及凭据。新增文件及二进制变更会生成集中发布审阅清单；核实可公开后，把清单内绑定 SHA 的 approval 填入私有配置 `approved_publication` 再执行。已有明确授权且内容可确定时由 agent 完成审阅，不重复请求许可。脚本的凭据扫描只是辅助，不能代替内容审阅。为变更技能运行适当的入口校验、脚本测试或渲染验证，按需放进控制器的 validators。

GitHub 不可达或本机副本读取失败时保留修改并停止；发布后本机安装失败则记录 pending，保留备份及基线，修复后重试。推送遇到并发更新时重新取得 GitHub 最新内容，最多合并重试3轮，不能强推。遇到中断 journal 应先检查目标与外置备份，恢复完成才重试；不删除锁、不强推、不 reset 用户维护仓。不把 GitHub 推送成功说成全端已更新。

完成后报告提交 SHA、本机设备及安装结果；逐文件哈希一致才报告本机同步成功，不推断其他设备状态。运行时发现可按新进程加载技能核验；已有会话是否缓存由运行时决定。

## Runtime adapter notes

Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw、Hermes Agent、DSH 均使用相同 Python CLI 和私有配置。安装根由配置显式登记，不能因品牌名猜路径。仅为正在使用的运行时登记安装根；维护仓 skills 也登记，以便捕获其修改。Hermes 的公共及角色目录在 NAS 本机登记，保留其路径适配；只读容器通过同宿主安装服务完成同步，服务不依赖用户电脑、不开放任意命令。每台实际同步设备需要 Python 3.9+、Git 和独立 GitHub 仓库读写凭据；普通运行时可只访问本地服务，不接触其凭据。
