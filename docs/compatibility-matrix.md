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

## Covered Skill Dependencies

当前矩阵只为以下六个写文件技能声明 clean-delivery coverage。所有技能必须整体安装；public script 的精确命令以 owning `SKILL.md` 为准。

| Skill | External command/package boundary | Current and evidence boundary |
|-------|-----------------------------------|-------------------------------|
| `end-of-term-teaching-materials` | Bash、Python、Typst；XLSX 由 skill-local Python writer 生成。 | 固定 Markdown/Typst/PDF/XLSX current；model、manifest、score evidence 仅在 owned work/evidence。 |
| `gongwen` | Bash、Python 3 skill-local 安全发布 helper、Typst。 | Markdown/Typst/PDF 同 stem current；expected diff、logs 和 failure candidate 不发布。 |
| `school-presentation` | Bash、Python；public verify 可使用安装环境提供的 browser。 | Markdown+offline HTML+显式引用 assets；manifest 和 caller `verify --workdir` evidence 不属于 delivery。 |
| `school-pptx` | Bash、Python、python-pptx、Pillow、lxml、PyYAML；Pandoc optional。 | reviewed Markdown+validated PPTX+confirmed referenced assets；best-effort 与 verify evidence 不发布，PowerPoint/WPS UAT 由人类完成。 |
| `teaching-design-package` | Bash、Node、Typst，以及 `pdfunite`、`qpdf` 或 Python PyMuPDF merge fallback。 | model-derived dynamic `1+1+N` current；model/status/module/merge/staging 只在 owned `.work` 或 caller diagnostic workdir。 |
| `tiaokedan` | Bash、Python；PDF 请求另需 Typst。 | Markdown+Typst 或 optional PDF exact set；diff/log/status/failure evidence 不发布。 |

六者都遵守 [clean-delivery contract](clean-delivery-directory-contract.md)：完整 candidate 和最小 gate 先于 current mutation，path-set+bytes identical 是 no-op，changed 使用 `history/<max+1>/` 整包归档，handled failure/`INT`/`TERM` 回滚。`sources/` 不由普通发布修改，只有显式 managed 且持续引用的 assets 随版归档；unknown、legacy、partial、ambiguous 或 symlink 状态必须先走 [audit → confirm → execute](agent-output-cleanup-prompt.md)。不承诺 `SIGKILL`、断电或多文件跨路径原子，也不自动删除 history。

`graduate-resume` 已完成 Phase 46 canonical 基线，但当前不属于已验收的 clean-delivery coverage 集合。它现已冻结 whole-folder 安装、资料 schema、fixtures 和离线 `validate` / `target` / `plan` / `verify` CLI；最终 Markdown/Typst/PDF 事务发布与验证 gate 以后续 phase 验收为准。

## Runtime Notes

### Teaching Design Package

- `teaching-design-package` 是整包编排 skill：运行时必须能保留 `references/format-and-orchestration.md`、`references/calendar.json`、`templates/teaching-design-package-full.md`、`scripts/teaching-design-package.sh` 以及 package-owned renderer scripts；旧授课计划和实操教案版式规则已迁入本 skill folder，正常运行不得要求读取 sibling skill 支持文件。
- PDF status 只有在显式 PDF 编译命令成功且输出文件存在时才能标记为 passed；只生成 Typst 不能声称最终 PDF 完成。

### Graduate Resume

- `graduate-resume` 必须 whole-folder 安装，保留 canonical `skills/graduate-resume/SKILL.md`、`references/`、`templates/`、`fixtures/` 和 `scripts/`；只复制入口会丢失 schema、照片/target 约束和 Phase 46 fixture 基线。
- 当前 public fallback 是 `skills/graduate-resume/scripts/graduate-resume.sh <command>`；Phase 46 已实现 `validate`、`target`、`plan`、`verify`，并继续冻结 `render`、`batch` 的离线零 token 边界，不声称已完成最终渲染。
- 所有命令都以离线、零 token 为前提；OpenClaw 与 Hermes Agent 的 whole-folder discovery、frontmatter、权限和 workdir 行为仍需 installation-time verification。

### Tiaokedan

- `tiaokedan` 是单张 `调课单` Markdown-first 文档 skill：运行时必须 whole-folder installation，保留 `SKILL.md`、`references/markdown-contract.md`、`references/pdf-workflow.md`、`templates/tiaokedan.md` 和 `scripts/tiaokedan.sh`。
- renderer 兼容省略 `title`、`recipient`、表格 `序号` 列和表格后的落款行；生成 Typst 时使用默认标题/收文对象、自动序号、frontmatter 落款，以及 `Songti SC` 优先的标题 `weight: 700`。
- 渲染依赖 `python3` 和 skill-local renderer；PDF gate 额外依赖 `typst` CLI，只有 `typst compile` 成功且 PDF 非空才能声称 final PDF passed。
- 成功路径只发布显式 pair/triple；logs、diffs、status、debug JSON 和 failure diagnostics 只存在于 owned `.work` 或调用方 evidence root，不得混入教师公开输出根目录。

### School PPTX

- `school-pptx` 必须 whole-folder 安装，保留 canonical `skills/school-pptx/SKILL.md`、`references/`、`scripts/`、`templates/` 和 `fixtures/`；只复制入口会丢失 Markdown/template contract、normalized PPTX/manifest、canonical fixture、verification 与 UAT 规则。
- required prerequisites 是 Python、python-pptx、Pillow、lxml、PyYAML；Pandoc 当前为 optional。runtime 不得联网或自动安装依赖，shell/Python external command 的 execute 权限、support/media read 权限、delivery/workdir write 权限和 sandbox/allowlist 必须在安装时核验。
- 自动脚本发现不可用时，统一 explicit invocation fallback 是 `skills/school-pptx/scripts/school-pptx.sh <command>`；`verify --workdir <caller-workdir>` 只可在调用方 root 下写 delivery/evidence/work，不能污染普通交付或仓库 source。
- 六 runtime 的具体路径/发现差异只保留在 canonical `Runtime Adapter Notes`。OpenClaw 与 Hermes Agent 的 exact path、frontmatter/support-file discovery、automatic script discovery 和 workdir boundary 必须 installation-time verification，不声明未实测支持；真实 PowerPoint/WPS UAT 也不能由 runtime 自动 PASS。

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
