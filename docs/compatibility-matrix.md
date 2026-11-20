# Compatibility Matrix

本矩阵记录 v1 必须考虑的 agent runtime。这里的目标不是伪装成所有平台都完全一致，而是把差异显式化。

## Recommended Pattern

最佳实践是 **one canonical `SKILL.md` first, support files by progressive disclosure, runtime notes second**：

1. 用一个 canonical `SKILL.md` 表达技能语义、触发条件、流程、输出、验证和安全边界。
2. 把长格式规则、examples、renderer notes、artifact contract、UAT 和 troubleshooting 放进 skill-local `references/`，把 helper commands 和 internal modules 放进 `scripts/`，把 Markdown intermediate 或输出 scaffolds 放进 `templates/`。
3. 在同一个 `SKILL.md` 的 adapter notes 中记录各 runtime 的加载路径、frontmatter 限制、工具调用、用户问询、任务/子代理和权限差异。
4. v1 不维护独立 adapter 文件；如果 notes 变长，先压缩成必要检查点并保留在 canonical 文件里。
5. 只有当 runtime 确实无法直接使用 canonical 文件时，才重新打开范围讨论生成式运行时 shim；v1 不实现 shim generation，也不维护多份技能逻辑。

## Installation Checks

每个 runtime 在标记支持前都要做安装期核验：

- `SKILL.md` frontmatter 可被解析，`description` 能触发正确技能。
- `references/`、`templates/` 和 `scripts/` 保持相对路径可读；runtime 不会只复制入口文件而丢失支持文件。
- `scripts/` 中的公共 helper command 在 sandbox/allowlist/write-permission 边界内可执行；未验证自动脚本发现时必须记录手动调用 fallback。
- Markdown intermediate 模板和 artifact contract reference 可从 `SKILL.md` 或技能索引中找到。
- 未在目标 runtime 上验证的行为必须明确标注为 installation-time check，不要声称完整支持。
- 写文件技能还必须运行一次 authorized delivery root 测试：whole-folder 支持文件可读、public script 可显式执行、外部依赖可用、input/support 可读、delivery root/同根 `.work` 可写，unknown 与 symlink 会在 mutation 前失败。

## Matrix

| Runtime | Whole-folder discovery and explicit fallback | Execute/read/write and sandbox boundary | Clean-delivery and verification boundary |
|---------|----------------------------------------------|-----------------------------------------|------------------------------------------|
| Codex | 用 `AGENTS.md` 或已安装版本的 local skill mechanism 指向完整 folder；若 discovery 或 script discovery 不可用，显式读取 canonical `SKILL.md` 并调用其中 public script。 | allowlist 仅开放技能声明的 Bash/Python/Node/Typst/PPTX/PDF/browser 命令；读取 input、`references/`、`templates/`、`fixtures/`，写 authorized delivery root、同根 `.work` 或调用方 verify workdir。 | publisher 只消费 explicit managed names；delivery root 与 verify evidence root 分离，unknown/symlink 失败关闭。 |
| Claude Code | 安装同一 folder 到目标版本可发现的 skill path，保留全部 support files；自动加载失败时显式 shell/script fallback。 | frontmatter/tool allowlist 覆盖实际依赖、input/support read 和 authorized root/`.work` write，不把项目外路径隐式加入权限。 | candidate-first、exact no-op、whole-bundle history、handled rollback 与 evidence 分离和 canonical 契约一致。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向完整 folder；support/script discovery 不可用时显式路径调用 public script。 | sandbox 允许所需外部命令、support/input read、delivery root/`.work` write；调用方 verify workdir 另行授权。 | 不用 runtime 自动整理 unknown/legacy；诊断与验证证据不得成为 current。 |
| OpenCode | 使用当前版本验证过的 native skill path；Claude-compatible 路径只能作为实测 install note，失败时保留显式 script fallback。 | allowlist 覆盖实际 Bash/Python/Node/Typst/PPTX/PDF/browser 依赖及 whole-folder read、authorized root/`.work` write。 | 保持一个 canonical workflow；不得因 runtime fallback 放宽 explicit set、history、rollback 或 cleanup confirmation。 |
| OpenClaw | 仅声明 installation-time verified：逐项验证 exact skill root、frontmatter parser、whole-folder/support/script discovery；任一项不确定时只使用显式 public script fallback，不声明自动发现。 | 安装时审阅第三方脚本并验证 allowlist、sandbox sync、实际外部依赖、input/support read、delivery root/`.work` 与 verify workdir write。 | 安装测试必须证明 candidate/no-op/history/rollback、unknown/symlink fail closed；不得推测跨版本路径或多文件原子能力。 |
| Hermes Agent | 仅声明 installation-time verified：核对 exact local/global path、project/global behavior、whole-folder/support/script discovery；自动发现不确定时显式调用 public script。 | 安装时验证 tool execute/read/write、实际依赖、support/input read、authorized delivery root/`.work` 与 verify workdir allowlist。 | 保留 canonical cleanup confirmation 与显式 fallback；不得声明未实测自动 discovery、wrapper 或硬原子支持。 |
| DeepSeek Harness（DSH） | `.dsh/skills`、`.agents/skills` 或 `customSkillDirs` 的直属完整 bundle；按精确名称用 `skill` 加载，资源相对返回的技能根读取；失败时显式读 canonical 文件/调用公开脚本。 | 安装时核验 provider/tool 插件、实际命令/包/字体、输入与支持读取、授权交付根/owned `.work`/独立核查目录写权限及 sandbox；不修改 profile 或读取凭据。 | 适配说明与复制助手已提供，源码核对及复制验证不等于 DSH 实机验收，不扩大六技能自动发布覆盖。 |

## Covered Skill Dependencies

当前矩阵只为以下六个写文件技能声明 clean-delivery coverage。所有技能必须整体安装；public script 的精确命令以 owning `SKILL.md` 为准。

| Skill | External command/package boundary | Current and evidence boundary |
|-------|-----------------------------------|-------------------------------|
| `end-of-term-teaching-materials` | Bash、Python、Typst；XLSX 由 skill-local Python writer 生成。 | 固定 Markdown/Typst/PDF/XLSX current；model、manifest、score evidence 仅在 owned work/evidence。 |
| `gongwen` | Bash、Python 3 skill-local 安全发布 helper、Typst。 | Markdown/Typst/PDF 同 stem current；expected diff、logs 和 failure candidate 不发布。 |
| `school-pptx` | Python、python-pptx、Pillow、lxml；预览需LibreOffice及PyMuPDF或Poppler。 | 原生可编辑PPTX及所需预览、源文件；结构、模板资产、渲染与PowerPoint/WPS实机检查分别报告。 |
| `teaching-design-package` | Bash、Node、Typst，以及 `pdfunite`、`qpdf` 或 Python PyMuPDF merge fallback。 | model-derived dynamic `1+1+N` current；model/status/module/merge/staging 只在 owned `.work` 或 caller diagnostic workdir。 |
| `tiaokedan` | Bash、Python；PDF 请求另需 Typst。 | Markdown+Typst 或 optional PDF exact set；diff/log/status/failure evidence 不发布。 |

六者都遵守 [clean-delivery contract](clean-delivery-directory-contract.md)：完整 candidate 和最小 gate 先于 current mutation，path-set+bytes identical 是 no-op，changed 使用 `history/<max+1>/` 整包归档，handled failure/`INT`/`TERM` 回滚。`sources/` 不由普通发布修改，只有显式 managed 且持续引用的 assets 随版归档；unknown、legacy、partial、ambiguous 或 symlink 状态必须先走 [audit → confirm → execute](agent-output-cleanup-prompt.md)。不承诺 `SIGKILL`、断电或多文件跨路径原子，也不自动删除 history。

`graduate-resume` 当前版本为 `0.3.2`，已实现离线 `validate` / `target` / `plan` / `render` / `batch` / `verify` CLI、三主题 Markdown/Typst/PDF 生成及 patch/authority 事务交付。当前还包含实际 Typst 排版测量、逐栏铺满检查、现代简洁与个性设计的强制双栏、网格信息栏、透明照片槽位、本地模块图标及岗位词组强调。功能实现和定向回归不等于完整发布验收：Phase 49 的发布前提、六 runtime 安装、人工 UAT 等证据尚未齐备，因此仍不纳入已验收的 clean-delivery coverage 集合，也不宣称六 runtime 均已实测通过。

## Runtime Notes

### Party Member Study Notes

- `party-member-study-notes-cn` 是无脚本的内容写作工作流，六种 runtime 均读取同一个 canonical `SKILL.md`；实际发现与输入读取权限仍需安装期核验。
- 默认优先依赖 `gongwen` 交付 PDF，另行核验其可发现性、依赖和授权目录，按其交付契约执行；不可用时以环境已有 PDF 工具兜底并验证中文与分页。文字起草无外部命令依赖，所有 PDF 能力不可用时如实交付 Markdown 并报告限制。该技能不新增自动 clean-delivery coverage。

### Teaching Design Package

- `teaching-design-package` 是整包编排 skill：运行时必须能保留 `references/format-and-orchestration.md`、`references/calendar.json`、`templates/teaching-design-package-full.md`、`scripts/teaching-design-package.sh` 以及 package-owned renderer scripts；旧授课计划和实操教案版式规则已迁入本 skill folder，正常运行不得要求读取 sibling skill 支持文件。
- PDF status 只有在显式 PDF 编译命令成功且输出文件存在时才能标记为 passed；只生成 Typst 不能声称最终 PDF 完成。

### Graduate Resume

- `graduate-resume` 必须 whole-folder 安装，保留 canonical `skills/graduate-resume/SKILL.md`、`references/`、`templates/`、`fixtures/`、`scripts/`、`fonts/` 和 `assets/`，包括字体清单及字体、图标许可；只复制入口会丢失校验、测量、渲染与验收所需文件。
- public fallback 是 `skills/graduate-resume/scripts/graduate-resume.sh <command>`，提供 `validate`、`target`、`plan`、`render`、`batch`、`verify`。`render` 与 `batch` 必须先预检，再以相同参数追加 `--confirm` 发布；`verify --workdir <caller-owned-dir>` 的验收证据不得混入正式交付根。
- 运行依赖 Bash、Python、PyYAML、PyMuPDF、Pillow、Poppler，以及严格锁定的 Typst `0.15.0`；编译使用 skill-local 字体和 `--ignore-system-fonts`。安装时核验依赖、输入及支持文件读取权限、shell 执行权限和 delivery/workdir 写入边界，不由离线 CLI 联网安装依赖。
- 所有命令都以离线、零 token 为前提；六 runtime 的 whole-folder discovery、frontmatter、权限和 workdir 行为仍需 installation-time verification，尤其不能假定 OpenClaw 与 Hermes Agent 的安装路径或自动脚本发现行为。完整验收规则见 `skills/graduate-resume/references/phase-49-verification-contract.md`；单次 PDF 生成成功或定向测试通过不能替代完整验收。
- whole-folder 安装不表示可以把学生工作目录复制到仓库。发布包仅保留通用代码、规则、模板、字体、图标和虚构夹具；真实学生简历、照片和产物不得提交。提交前运行 `test_publication_contract` 并审查暂存区，具体边界见 `skills/graduate-resume/references/repository-publication.md`。

### Tiaokedan

- `tiaokedan` 是单张 `调课单` Markdown-first 文档 skill：运行时必须 whole-folder installation，保留 `SKILL.md`、`references/markdown-contract.md`、`references/pdf-workflow.md`、`templates/tiaokedan.md` 和 `scripts/tiaokedan.sh`。
- renderer 兼容省略 `title`、`recipient`、表格 `序号` 列和表格后的落款行；生成 Typst 时使用默认标题/收文对象、自动序号、frontmatter 落款，以及 `Songti SC` 优先的标题 `weight: 700`。
- 渲染依赖 `python3` 和 skill-local renderer；PDF gate 额外依赖 `typst` CLI，只有 `typst compile` 成功且 PDF 非空才能声称 final PDF passed。
- 成功路径只发布显式 pair/triple；logs、diffs、status、debug JSON 和 failure diagnostics 只存在于 owned `.work` 或调用方 evidence root，不得混入教师公开输出根目录。

### School PPTX

- `school-pptx` 必须整目录安装，保留入口、`agents/`、`references/`、`scripts/`和`assets/`；默认模板只有一份`assets/school-template.pptx`。
- 使用同一Python核验python-pptx、Pillow、lxml；预览另需LibreOffice及PyMuPDF或Poppler。运行时不安装软件或联网下载模板。
- 公开命令为`school_pptx.py doctor/inspect/check/preview`，Shell入口转发相同命令；所有项目产物和检查证据写在项目目录。
- Hermes核实当前profile实际发现的技能根、读取与执行权限，并在宿主同步源码和安装；不能仅凭源码已更新声称安装生效。实机检查与自动检查分别报告。

### Codex

- Put persistent project instructions in `AGENTS.md`.
- Keep runtime-specific command mappings out of canonical skill bodies.
- When a skill references tools, document Codex equivalents in adapter notes.
- If a Codex installation cannot auto-discover `SKILL.md`, record the project-context bridge that tells Codex to read it.

Reference: [OpenAI Codex AGENTS.md docs](https://github.com/openai/codex/blob/main/docs/agents_md.md)

### Claude Code

- Prefer one skill directory per skill.
- Keep `name` and `description` precise because they drive skill selection.
- Place long reference material in supporting files and let the skill load it only when needed.

Reference: [Claude Code Skills docs](https://code.claude.com/docs/en/agent-sdk/skills)

### Gemini CLI

- Treat `GEMINI.md` as the official project-context bridge.
- If using SKILL.md with Gemini-based workflows, document exactly how the agent is instructed to discover and follow skills.
- Keep user-question and subagent behavior as explicit fallbacks when Gemini lacks an equivalent tool.

Reference: [Gemini CLI GEMINI.md docs](https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html)

### OpenCode

- Document both native OpenCode skill paths and Claude-compatible fallback paths.
- Keep the canonical file valid enough that OpenCode can load the same `SKILL.md` when possible.
- Verify skill discovery in the installed OpenCode version before marking a skill as supported.

Reference: [OpenCode skills docs](https://opencode.ubitools.com/skills/)

### OpenClaw

- Use AgentSkills-compatible folders with `SKILL.md`.
- Keep frontmatter conservative; OpenClaw documentation notes parser constraints for frontmatter keys.
- Treat third-party skills as untrusted code and review before enabling.
- Verify allowlist, skill root, and sandbox behavior during installation. Keep OpenClaw as a required v1 runtime.

References:

- [OpenClaw skills source docs](https://github.com/openclaw/openclaw/blob/main/docs/tools/skills.md)
- [OpenClaw skills overview](https://openclawcn.com/en/docs/agent/skills/)

### Hermes Agent

- Keep Hermes in v1 as a required runtime, but mark exact loading paths as implementation-validated rather than assumed.
- Adapter notes must record whether Hermes loads project-local skills, global skills, or both in the installed version.
- Avoid depending on automatic script discovery until it has been verified in the target Hermes installation.
- Do not claim generated-wrapper support unless the wrapper rule and verification checklist are documented.

References:

- [NousResearch Hermes Agent skills catalog](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/reference/skills-catalog.md)
- [Hermes Agent SKILL.md guide](https://www.agensi.io/learn/how-to-use-skill-md-with-hermes-agent)

# 职业技能等级认定技能安装说明

`vocational-practical-exam` 与 `vocational-theory-exam` 按完整目录独立发现；`vocational-exam-package` 需要同时解析两项技能依赖。三者的六 runtime 注释在各自 `SKILL.md`，OpenClaw/Hermes 的路径、自动发现与权限必须安装时实测。实操审计仅依赖 Python 标准库；文档生成及渲染按实际环境选用现有工具，未提供自动 renderer/publisher 或已实测的跨 runtime 发布保证。fallback 为显式读取入口与引用，实操只读检查使用 `python3 scripts/audit_docx.py`。

## DeepSeek Harness（DSH）

2026-11-13 对照 [官方仓库](https://github.com/deepseek-ai/deepseek-harness) 提交 `39163dd30f703a79079e2d2446545cff3c453738`（仓库版本 `0.2.2-rc.3`）的 [filesystem provider](https://github.com/deepseek-ai/deepseek-harness/blob/39163dd30f703a79079e2d2446545cff3c453738/packages/skill/skill-filesystem/README.zh.md)、[实现](https://github.com/deepseek-ai/deepseek-harness/blob/39163dd30f703a79079e2d2446545cff3c453738/packages/skill/skill-filesystem/src/index.ts)及 [skill 工具](https://github.com/deepseek-ai/deepseek-harness/blob/39163dd30f703a79079e2d2446545cff3c453738/packages/skill/tool-skill/README.zh.md)核对以下规则。这是源码与本地复制验证，不是 DSH 实机端到端验收；旧版及自定义 profile 须重新核对。

- DSH 使用 `@deepseek-ai/dsh-skill` 注册表、`@deepseek-ai/dsh-skill-filesystem` 本地提供方和 `@deepseek-ai/dsh-tool-skill` 模型加载工具。安装技能不会自动安装/启用这些插件，不应擅自修改用户 profile。
- 提供方只扫描 `<root>/<name>/SKILL.md` 或 `<root>/<name>.md`，不递归查找 `**/SKILL.md`。本仓库必须整目录复制所选 `skills/<name>/`，或将仓库的绝对 `skills/` 路径配置到已有 filesystem provider 的 `customSkillDirs`；不能只复制 `SKILL.md` 或把整个仓库当作单个技能 bundle。
- 默认优先级（小 rank 优先）：最近 `.git` 祖先项目的 `.dsh/skills`（100）、`.agents/skills`（200）、`customSkillDirs`（300）、DSH 用户根 `skills`（400）、共享 agents 根 `skills`（500）、bundled（600）。没有 `.git` 时以 cwd 为项目根。`includeDefaultRoots: false` 会关闭默认根。
- DSH 用户根取 `dshHome` 配置，否则 `$DSH_HOME` / `~/.dsh`；共享 agents 根取 `agentsHome` 配置，否则 `$DSH_AGENTS_HOME` / `~/.agents`。优先检查当前 profile 配置及重名遮蔽，不能仅因目录存在就声称可发现。
- canonical frontmatter 的 `name`（kebab-case）与 `description` 必填；附加数据放 `metadata`。DSH 特有调用键为 `disable-model-invocation` / `user-invocable`，默认均允许；不为适配而全局关闭自动调用，也不把 Codex 的 `agents/openai.yaml` 当作 DSH 配置。
- 通过 `skill` 工具按精确名称加载，返回的资源基目录用于解析 `references/`、`scripts/`、`templates/` 等相对路径；仅看目录摘要不等于已加载正文。用户已显式加载正文时不重复加载。显式文件读取/公开脚本调用仅是 fallback，不能声称修复了自动发现。
- 当前技能依赖仍由各技能声明，不能假设 DSH 插件已经提供 Python、Typst、Office/PDF、浏览器或全部外部包。命令、网络、输入/支持读与授权交付根/owned `.work`/独立核查目录写权限按会话实际工具与权限核验，不把本仓库写成可执行插件包。

安装助手 `scripts/install-dsh-skills.py` 默认只读检查，`--install` 才复制，已有不同目标须 `--replace` 并保留 `.presto-backups/` 回滚目录；复制后校验完整目录 SHA-256 清单，不改动 DSH profile 或凭据。该助手依赖 Python 3 + PyYAML，不负责依赖安装和 DSH 运行测试。

### 专业调研报告

`professional-research-report` 是可跨 runtime 的取证、原稿格式继承与交付工作流，附标准库只读 DOCX 审计；编辑、制图、PDF 渲染使用宿主已有能力。现有报告的人类验收不等于技能所有模板与 runtime 均通过实机验收。该技能不扩展既有六技能自动 clean-delivery 覆盖。

## 技能同步升级

`presto-toolchain-and-upgrade` 在七种 runtime 中使用相同 CLI；按私有配置登记目录和传输方式，不修改 runtime 启用策略。控制端需要 Python 3.9+、Git、推送权限；端点仅需 Python，触发端无需 GitHub 凭据。Hermes 只读技能挂载由 NAS 端点写宿主目录；普通容器进程不承担安装。macOS/Linux 的接入核验不能替代 Windows 或各 runtime 的实机发现验收。
