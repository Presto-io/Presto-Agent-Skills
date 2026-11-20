---
name: presto-toolchain-and-upgrade
description: 在任一设备修改 Presto 技能后，将公开技能变更合并发布到 GitHub，再同步已登记平台；用于技能升级、跨设备同步和冲突处理。
metadata:
  version: "0.2.0"
  portability: canonical
  supported-runtimes: [Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, Hermes Agent, DeepSeek Harness]
---

# Presto 技能同步升级

用户要求升级、同步，或完成本次已授权的技能修改后，执行一次“收集各端修改 → 三方合并 → 校验 → 推送 GitHub main → 安装各端 → 哈希回读”。不作为公文、教学、PPT 等业务工作的前置技能，也不启动后台定时任务。

使用本机私有配置 `~/.config/presto-skill-sync/config.json`，运行本技能的 `scripts/skill_sync.py --config <配置绝对路径> sync`。配置为控制端时执行完整流程；配置为触发端时请求已登记控制端执行。首次配置及平台适配见 [references/configuration.md](references/configuration.md)。不得把真实设备配置、密钥、业务资料或同步状态放进公开仓库。

## 合并规则

- GitHub main 是共同发布源；本平台修改也必须先上传，不能简单拉取覆盖。比较每个安装副本的上次成功基线、当前内容、GitHub 内容。
- 同一改动去重，单边改动保留，不重叠的 UTF-8 文字由 Git 三方合并；不得以版本号、时间戳、设备地位决定覆盖。
- 同段文字、二进制双改、删除与修改冲突、首次无基线却内容不同，停止发布并保留现场。统一告诉用户技能名、文件、来源设备和冲突原因；处理方法见 [references/conflicts.md](references/conflicts.md)。不要逐个弹问，也不要猜测用户取舍。
- 新技能须先审阅可公开内容并纳入 GitHub main，才进入自动同步名单。`uws-workspace` 等私有技能不通过公开 GitHub 同步；按独立私有渠道维护。已封存技能不上传、不重新安装。
- 设备资料路径、凭据、权限与运行时开关保留在私有配置；不要把它们作为共同技能文本传播。不得为安装改变业务技能的启用/禁用状态。

## 执行与验收

执行前检查本次修改清单和发布内容，排除真实学生资料、照片、成品及凭据。脚本的凭据扫描只是辅助，不能代替内容审阅。为变更技能运行适当的入口校验、脚本测试或渲染验证，按需放进控制器的 validators。

离线端收集失败时停止本轮发布；发布后某端安装失败则记录 pending，保留备份及基线，修复后重试。遇到中断 journal 应先检查目标与外置备份，恢复完成才重试；不删除锁、不强推、不 reset 用户维护仓。不把 GitHub 推送成功说成全端已更新。

完成后简要报告提交 SHA、已确认设备、未完成设备；逐文件哈希一致才报告同步一致。运行时发现可按新进程加载技能核验；已有会话是否缓存由运行时决定。

## Runtime adapter notes

Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw、Hermes Agent、DSH 均使用相同 Python CLI 和私有配置。安装根由配置显式登记，不能因品牌名猜路径。仅为正在使用的运行时登记安装根；维护仓 skills 也登记，以便捕获其修改。Hermes 的公共及角色目录分别登记，保留其路径适配。只读容器通过受限运维端点安装，不能声称普通聊天进程可直接写入。需要 Python 3.9+；控制端另需 Git 和 GitHub 推送权限，触发端无需 GitHub 凭据。
