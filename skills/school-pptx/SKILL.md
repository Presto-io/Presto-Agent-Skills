---
name: "school-pptx"
description: "Use when drafting, reviewing, validating, or rendering school or course presentation content from finalized Markdown logical slides into an editable, controlled-template PowerPoint deck."
metadata:
  short-description: "学校课程 Markdown 逻辑页到可编辑 PPTX 工作流"
  version: "0.1.0"
  portability: "canonical"
  supported-runtimes:
    - Codex
    - Claude Code
    - Gemini CLI
    - OpenCode
    - OpenClaw
    - Hermes Agent
---

# School PPTX

## Objective and Use When

把学校汇报、课程展示、培训课件或项目答辩内容整理成教师可审阅的 Markdown logical slides，再用受控 `standard-school` 模板生成原生可编辑 PPTX。Markdown 是内容 source of truth；模板和 renderer 拥有视觉、对象与分页规则。

当用户要新建、补全、审阅、验证或渲染学校/课程 PowerPoint，且需要固定学校模板、可编辑对象和可复验交付时使用本技能。需要离线 HTML 演示时应改用 `school-presentation`。

## Required Inputs and References

- 学校或课程标题，以及需要出现在封面的 subtitle、学期/日期、作者等 metadata。
- 唯一受控主题 `standard-school`。
- 已定稿或待审阅的 Markdown；公开写作规则见 `references/markdown-contract.md`。
- 所有 Markdown 引用的本地图片/图标路径。
- 模板所有权与人工编辑规则见 `references/template-contract.md` 和 `references/template-editing.md`。
- 可编辑对象、logical→physical 分页与 clean output 见 `references/renderer-and-pagination.md`。
- 自动验证、依赖、证据和排障见 `references/verification-contract.md`。
- PowerPoint/WPS 人工检查见 `references/visual-uat.md`。

## Review Before Render

1. 从用户材料中提取 metadata、逻辑页、notes、表格、代码和媒体引用；不要猜测缺失事实。
2. 运行 `example` 获取完整 fixture，或按 Markdown contract 编写/更新 source。
3. 只对缺失或冲突的必需信息集中提问，然后运行 `validate` 和 `template-report`。
4. 让用户审阅 Markdown；确认内容已 finalized，且不存在 `{{待补充:...}}`、`{{AI草稿:...}}` 或缺失媒体。
5. 只有 required facts、required media 和 review markers 全部解决后才运行 `render`。
6. 在调用方 workdir 运行 `verify --workdir`；自动 PASS 不能替代真实 PowerPoint/WPS viewer UAT。

## Missing Information Questions

只在对应信息缺失时询问：

- 学校/课程标题：学校名称、课程名称和主标题分别是什么？
- subtitle/term/author metadata：副标题、学期或日期、作者/汇报人哪些需要显示？
- controlled theme：是否确认使用唯一受控主题 `standard-school`？
- required media：每张必需图片或图标的可读本地路径是什么？
- unresolved review markers：`{{待补充:...}}` 与 `{{AI草稿:...}}` 应如何定稿？
- Markdown finalized state：当前 Markdown 是否已经完成内容审阅并允许渲染？

任一必需事实、媒体或 review marker 未解决时，禁止 render；不要用占位内容伪装最终成功。

## Public Commands

```bash
skills/school-pptx/scripts/school-pptx.sh example --out-dir <fixture-dir>

skills/school-pptx/scripts/school-pptx.sh validate \
  --input <reviewed.md>

skills/school-pptx/scripts/school-pptx.sh template-report \
  --theme standard-school \
  --out-md <workdir>/template-report.md \
  --out-json <workdir>/template-report.json

skills/school-pptx/scripts/school-pptx.sh render \
  --input <reviewed.md> \
  --out-dir <delivery-dir> \
  --stem <name>

skills/school-pptx/scripts/school-pptx.sh verify \
  --workdir <caller-workdir>
```

## Outputs and Verification

成功 render 的 current DeliverySpec 是同 stem、逐字节保留的 reviewed `.md`、通过 staged package gate 的原生可编辑 `.pptx`，以及两者持续引用且已确认纳管的 `assets/<safe-relative-path>`。`sources/` 永不由普通 render 修改；未引用输入不复制进 `assets/`。根目录只允许 current、`sources/`、`assets/`、`history/` 与本次运行期间的 `.work/`。

完整 candidate 先在 `.work/<run-id>/candidate/` 生成并验证。exact relative set 与 bytes 全部相同即 no-op，不改 current inode/mtime、不建 history；changed 时旧 pair 与全部旧 managed assets 进入同一个 `history/<max+1>/`，归档 Markdown 的 `assets/...` 引用必须在该 sequence 内解析。七类 handled fault 与 `INT`/`TERM` 会恢复旧完整 bundle 并清理本次 history/work；这不承诺 `SIGKILL`、断电或多个路径的硬原子性。parser、plan 或 runtime 非零时，结构有效的 best-effort deck 只在 owned work evidence 生命周期内存在，绝不发布为 current。

manifest、logical JSON、日志、诊断和 verification evidence 不进入公开 delivery；`verify --workdir` 只写调用方指定、且不同于普通 delivery root 的 workdir。自动目录/OOXML PASS 不等于 PowerPoint/WPS 人工 UAT PASS。

## Runtime Adapter Notes

以下是唯一 runtime-specific 区域；canonical workflow 不依赖这些私有路径或发现机制。

| Runtime | Discovery/support files | Explicit invocation fallback | Python/packages | External commands | Execute/read/write | Sandbox/allowlist | Delivery/verify roots |
|---|---|---|---|---|---|---|---|
| Codex | 通过项目 `AGENTS.md` 或已安装的本地 skill 机制发现，并保留整个 `school-pptx` folder、references/scripts/templates/fixtures。 | 自动脚本发现不可用时，显式调用 `scripts/school-pptx.sh`。 | 需要 Python、python-pptx、Pillow、lxml、PyYAML；Pandoc 可选。 | shell/Python 是外部命令；不联网、不自动安装。 | 安装时验证脚本可执行及支持文件可读，输出目录可写。 | 将脚本、模板、fixture、媒体与目标目录纳入 sandbox/allowlist。 | delivery root 允许受管 current/support，运行期写 `.work`；`verify --workdir` 使用另一调用方可写根。 |
| Claude Code | 适用版本可安装整个 folder 到 `.claude/skills/school-pptx/`；保留所有支持目录。 | 自动脚本发现不可用时，显式调用 `scripts/school-pptx.sh`。 | 需要 Python、python-pptx、Pillow、lxml、PyYAML；Pandoc 可选。 | shell/Python 是外部命令；不联网、不自动安装。 | 验证 execute/read/write 权限和相对支持路径。 | 在工具 allowlist/sandbox 中允许脚本、输入媒体和目标目录。 | delivery root 仅 current/support 与运行期 `.work`；verify 使用独立 caller workdir。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向整个 canonical folder，并确认支持文件随安装保留。 | 无自动发现时显式读取本文件并调用 `scripts/school-pptx.sh`。 | 需要 Python、python-pptx、Pillow、lxml、PyYAML；Pandoc 可选。 | shell/Python 是外部命令；不联网、不自动安装。 | 安装时验证脚本执行、支持文件读取和目标写入。 | 显式批准脚本、模板、fixture、媒体与输出的 sandbox/allowlist。 | delivery root 仅 current/support 与运行期 `.work`；`verify --workdir` 指向另一调用方根。 |
| OpenCode | 使用适用版本的 native skill path 或 Claude-compatible fallback，whole-folder 安装并验证支持文件。 | 自动脚本发现不可用时显式调用 `scripts/school-pptx.sh`。 | 需要 Python、python-pptx、Pillow、lxml、PyYAML；Pandoc 可选。 | shell/Python 是外部命令；不联网、不自动安装。 | 验证 execute/read/write 权限，不假定继承宿主权限。 | 配置 sandbox/allowlist 读取模板、fixture、媒体并写目标目录。 | delivery root 授权 current/support 与 `.work`；verify 只用明确 caller workdir。 |
| OpenClaw | 作为必需 runtime；exact skill root、frontmatter 解析、support-file discovery 和 whole-folder 完整性必须 installation-time verification。 | automatic script discovery 不作保证；安装时验证后仍保留显式 `scripts/school-pptx.sh` fallback。 | 安装时核验 Python、python-pptx、Pillow、lxml、PyYAML；Pandoc 可选。 | shell/Python 属外部命令；禁止联网与自动安装。 | installation-time verification 覆盖 execute/read/write 权限。 | 安装时核验脚本 allowlist、sandbox 对模板/fixture/媒体/目标的访问。 | installation-time 实测 delivery `.work` 收尾与独立 caller `verify --workdir` 边界。 |
| Hermes Agent | 作为必需 runtime；exact local/global path、frontmatter 和 support-file discovery 必须 installation-time verification。 | automatic script discovery 不作保证；明确保留 `scripts/school-pptx.sh` invocation fallback。 | 安装时核验 Python、python-pptx、Pillow、lxml、PyYAML；Pandoc 可选。 | shell/Python 属外部命令；禁止联网与自动安装。 | installation-time verification 覆盖 execute/read/write 权限。 | 安装时核验 allowlist/sandbox 对完整 folder、媒体和目标目录的访问。 | installation-time 实测 delivery `.work` 收尾、history 权限与独立 caller workdir。 |

## Safety

- 不联网、下载安装依赖、字体、模板或媒体；缺少 required dependency 时非零失败并给出 bounded remediation。
- 不把 `.potx` 视觉源样本当作直接 runtime template，不允许 Markdown 覆盖坐标、字体、颜色、裁剪或动画。
- 不调用 sibling skill scripts，不把整页截图作为 PPTX 内容，不把 best-effort 产物或自动结构检查描述为人工 UAT PASS。
- 写入前确认 delivery 与 verify workdir；render 的 best-effort evidence 只在 owned `.work` 生命周期，verify 证据只留 caller workdir。
