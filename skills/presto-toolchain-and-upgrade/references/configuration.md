# 各设备独立配置

各设备只与 GitHub 交换版本，不查询或安装其他设备。默认入口为 `~/.config/presto-skill-sync/config.json`；配置、凭据、状态和备份均放在技能发现根和公开仓库之外。

## 直接执行

```json
{
  "mode": "device",
  "device_id": "stable-device-name",
  "state_dir": "/private/sync/device-state",
  "repository": "https://github.com/Presto-io/Presto-Agent-Skills.git",
  "branch": "main",
  "author_name": "维护者",
  "author_email": "GitHub noreply email",
  "resolution_file": "/private/sync/resolutions.json",
  "installation": {
    "state_dir": "/private/sync/installation-state",
    "engine_path": "/private/sync/engine.py",
    "roots": [
      {"path": "/private/repo/skills", "install_missing": true},
      {"path": "/private/runtime/skills", "install_missing": true}
    ],
    "private_skills": ["uws-workspace"]
  },
  "validators": []
}
```

`device_id` 在同设备上保持稳定；每台设备独立保存基线、缓存、安装备份和凭据，不复制其他设备的私钥或 GitHub token。默认使用各设备独立的 GitHub HTTPS 登录和本地凭据助手，不复制其他设备的token。组织禁止部署密钥时保持该策略不变。若用户另有明确授权并已配置SSH，可设置受信任的 `ssh_command` 和SSH仓库URL。所有路径、命令和 validators 都是受信任运维配置，不从技能文件或外部资料推导。

同步缓存专用，不把用户维护仓作为合并工作区；用户维护仓 skills 仅作为本机来源和安装目标，不 reset 分支、不改索引。安装状态目录与目标在同一文件系统，以支持 rename 与异常回滚；同步状态目录与安装状态目录必须不同，以免锁递归。读取失败必须停止，不当成文件删除。

`validators` 示例：`{"skills":["a-skill"],"command":["python3","skills/a-skill/scripts/check.py"]}`。在候选仓运行，非零则不发布。新增公共技能和整技能退休采用单独审阅提交，不根据本机缺目录推断全局删除。

## 只读运行时的同宿主服务

macOS凭据只能由登录会话访问时，可把服务作为该设备自己的登录LaunchAgent运行；不访问其他设备。Hermes 等普通运行时无法写生产目录时，在同一 NAS/宿主机部署固定 `local_service.py`，仅接受 `sync` 与 `status`。服务持有本机 device 配置、独立 Git 凭据和安装权限；客户端配置只含：

```json
{"state_dir":"/private/client-state","local_service":"/private/runtime-socket/sync.sock","timeout":1800}
```

服务启动参数为 `--socket <绝对路径> --engine <固定引擎> --config <本机device配置> --allow-uid <运行时UID> --socket-gid <运行时GID>`。socket 父目录由服务账号持有，禁止普通运行时写入；socket 为0660，并检查允许的Linux调用UID。客户端不能指定命令、引擎、配置或安装根。服务脚本、配置和私钥位于普通运行时不可写目录，不挂载 Docker socket，也不提供NAS密码或SSH中继。

用容器提供 NAS 缺失的 Git/Python 时，仅挂载本机技能存储及私有服务状态，使用固定镜像版本和本地socket。NAS重启后服务可自动恢复；它仅监听本地调用，不定时同步。特权安装可为维护源配置 `owner: {"uid": 1000, "gid": 10}`，保留普通账号编辑能力。生产只读挂载和业务启用策略不变。

## 初始化、迁移与验收

首次只有与 GitHub 相等的副本能自动建立基线；已有差异先备份和审阅，不强行覆盖。迁移旧基线时仅保留当前设备已经核验的记录和原device_id，不能把其他设备的成功结果当成本机成功。旧中心控制器、跨设备触发密钥及中继在本机独立同步验证后停用。

`engine_path` 可在安装新引擎时自动刷新固定副本；若使用本地服务客户端，`local_client.py` 必须与固定引擎同目录，服务脚本由管理员维护。现有进程继续使用已加载代码完成本轮。

执行 `status` 只查本机上一轮结果，`sync` 执行本机完整流程。验收应包含：独立设备先后修改的三方合并、推送竞争、GitHub离线保留、冲突集中返回，以及其他设备不可达时本机仍可完成。Windows 核心可使用 Python/Git，但目录、权限、服务适配需另行实测。
