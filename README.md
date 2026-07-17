# Presto Agent Skills

Presto Agent Skills 是一个面向多类 AI agent 的技能仓库框架。它让团队先用一个 canonical `SKILL.md` 编写技能，再用轻量 runtime adapter notes 说明不同 agent 的安装、调用和安全差异。

这个仓库面向编写、审阅和迁移 agent 技能的贡献者，也面向需要读取本地规则并保持 runtime-neutral 输出的 coding agents。

首批支持目标：

- Codex
- Claude Code
- Gemini CLI
- OpenCode
- OpenClaw
- Hermes Agent

其中 OpenClaw 和 Hermes Agent 是 v1 必须支持的目标。

`graduate-resume` 技能现已完成 Phase 46 基线：沉淀毕业生简历资料契约、照片/target 一次追问语义、fixture 基线，以及离线 `validate` / `target` / `plan` / `verify` CLI。

## 给 Agent 说的话

这个仓库是技能的 canonical source repository，不是一个可以忽略支持文件、只复制 `SKILL.md` 的提示词集合。无论你负责使用、安装还是修改技能，都应先确认目标 runtime 如何发现技能、允许哪些外部命令，以及哪些目录可读写。

### 开始前先做什么

1. 先读取仓库根目录的 `AGENTS.md`，进入子目录后继续检查是否存在更深层的 `AGENTS.md`。
2. 根据任务意图查找 `skills/<skill-name>/SKILL.md`，先读完整入口文件，再按入口链接读取必要的 `references/`、`templates/`、`fixtures/` 或 `scripts/`。
3. 区分“使用现有技能”和“修改技能”。使用时遵守技能的输入、输出、安全与验证契约；修改时还要同步检查 `skills/README.md`、`docs/directory-spec.md` 和 `docs/compatibility-matrix.md`。
4. 不要根据技能名称猜测行为。以 `description`、工作流、公开命令和 artifact contract 为准。

### 如何安装技能

安装时复制整个技能目录，而不是只复制入口文件：

```bash
cp -R skills/<skill-name> <runtime-skill-root>/<skill-name>
```

目标目录必须保留原有相对结构，包括技能实际使用的 `SKILL.md`、`references/`、`scripts/`、`templates/` 和 `fixtures/`。不同 runtime 的发现方式不同：

| Runtime | 安装或发现方式 |
|---------|----------------|
| Codex | 通过项目 `AGENTS.md` 或当前 Codex 环境支持的本地 skill 机制指向 canonical 技能；无法自动发现时，明确要求读取目标 `SKILL.md`。 |
| Claude Code | 可将完整技能目录安装到 `.claude/skills/<skill-name>/`，并确认支持文件未丢失。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向 canonical `SKILL.md`，同时说明支持文件位置和命令调用方式。 |
| OpenCode | 优先使用当前版本支持的 native skill path；如使用 Claude-compatible fallback，必须实际验证技能是否被发现。 |
| OpenClaw | 使用当前安装版本支持的 AgentSkills-compatible 目录，安装前审阅第三方脚本，并验证 frontmatter、allowlist、skill root 和 sandbox。 |
| Hermes Agent | 使用当前版本支持的 `SKILL.md` skill folder；项目级或全局路径必须在安装环境中实测，不能靠猜测。 |

准确的 runtime 差异以目标技能的 `Runtime Adapter Notes` 和 `docs/compatibility-matrix.md` 为准。除 Claude Code 示例外，本仓库不把尚未跨版本验证的路径写成固定事实。

### 如何使用技能

1. 用用户任务匹配 `SKILL.md` 的 `description`，不要仅凭关键词强行触发。
2. 按技能要求收集输入；关键事实、媒体、凭据或输出位置缺失时，先澄清，不要用占位内容伪装完成。
3. 文档类工作流优先保留可审阅的 Markdown intermediate，再生成 Typst、PDF、HTML、PPTX 或其他最终产物。
4. 优先调用技能公开的 `scripts/` 命令；如果 runtime 不支持自动脚本发现，使用 `SKILL.md` 中记录的显式命令 fallback。
5. 按技能规定执行验证。自动验证、结构检查、人工 UAT 和最终交付检查是不同层级，不能互相冒充。
6. 只把当前 Markdown 和最终交付物放在公开交付根目录；历史版本、诊断、日志和临时验证产物按 `docs/clean-delivery-directory-contract.md` 处理。

### 六技能干净交付边界

当前干净交付契约是封闭集合，只覆盖 `end-of-term-teaching-materials`、`gongwen`、`school-presentation`、`school-pptx`、`teaching-design-package` 和 `tiaokedan` 六个写文件技能，不把其他技能误计为已适配。每个技能都以自己声明的稳定 Markdown 名称、最终产物名称和可选产物开关构造 explicit managed set；完整候选先在 `.work/<run-id>/` 生成并通过最小可读性 gate，才允许变更 current。

- 首次发布只写显式受管集合；candidate 与 current 的相对路径集合和 bytes 全部相同时是 no-op，不创建 history，也不触碰 current。
- 内容变化时，上一版完整受管集合以 `max + 1` 的同一序号进入 `history/<sequence>/`；普通发布不自动删除 history。
- handled failure、`INT` 或 `TERM` 回滚旧 current，并只清理本次 owned run；不承诺 `SIGKILL`、断电或多文件跨路径原子。
- `sources/` 不由普通发布修改；只有技能明确声明、被当前 bundle 持续引用的 managed `assets/` 才随同版归档。
- unknown、legacy、symlink、partial 或 ambiguous 状态在 mutation 前失败关闭。历史散乱产物必须按 [确认式 cleanup contract](docs/agent-output-cleanup-prompt.md) 先只读审计，再绑定 snapshot 明确确认，不能由普通 render 自动整理。
- 成功交付根不得平铺 manifest、status、model、log、diff、screenshot、staging、验证证据或失败产物；调用方 `verify --workdir` 是独立 evidence root，不是 delivery root。

完整状态机、目录所有权和真实原子性边界以 [canonical clean-delivery contract](docs/clean-delivery-directory-contract.md) 为准；技能的稳定文件名与最小 gate 继续由各自 `SKILL.md` 和 artifact contract 拥有。

### 安全与验证注意事项

- 把第三方技能和脚本视为未受信任代码，启用前先审阅其命令、网络访问、凭据读取和写入范围。
- 不要擅自联网、安装依赖、上传文件、读取凭据或扩大 sandbox/allowlist；需要这些能力时，必须遵守目标技能的安全边界并取得用户授权。
- 安装后至少验证：frontmatter 可解析、`description` 可正确触发、支持文件可读、公开脚本可执行、输出目录可写、失败运行不会污染已有成功交付。
- OpenClaw 与 Hermes Agent 是必须考虑的 runtime，但 exact path、自动发现、脚本权限和 workdir 边界仍需 installation-time verification。
- 真实 Microsoft PowerPoint、WPS、浏览器或打印结果要求人工 UAT 时，Agent 只能准备证据和检查清单，不能代替人类签署通过。

## 设计原则

1. **统一源文件优先**：每个技能先写一个 canonical `SKILL.md`，它是技能语义、流程、输出和验证标准的唯一来源。
2. **适配注释隔离差异**：各 agent 的路径、frontmatter、工具调用、子代理、用户问询等差异先写进同一个 `SKILL.md` 的 runtime notes。
3. **渐进披露**：`description` 要短而准确，`SKILL.md` 保留语义入口、流程、输出、验证、安全和 runtime notes；长格式规则、示例、renderer notes 和操作细节放到 skill-local `references/`。
4. **安全默认**：技能可能改变 agent 的行为和可执行能力，第三方技能必须先审阅再启用。
5. **先稳定契约，后扩展自动化**：v1 先稳定目录、模板和兼容性说明；示例保持可选且精简，脚手架、校验器、runtime harness、runtime shim generation 和发布流程后续再加。

## 仓库结构

```text
.
├── AGENTS.md
├── README.md
├── docs/
│   ├── compatibility-matrix.md
│   ├── directory-spec.md
│   ├── clean-delivery-directory-contract.md
│   ├── agent-output-cleanup-prompt.md
│   └── markdown-normalization-contract.md
├── skills/
│   ├── README.md
│   ├── graduate-resume/
│   │   ├── SKILL.md
│   │   ├── fixtures/
│   │   ├── references/
│   │   ├── scripts/
│   │   └── templates/
│   ├── gongwen/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── scripts/
│   │   └── templates/
│   ├── tiaokedan/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── scripts/
│   │   └── templates/
│   ├── end-of-term-teaching-materials/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── scripts/
│   │   └── templates/
│   ├── teaching-design-package/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── scripts/
│   │   └── templates/
│   ├── school-presentation/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── scripts/
│   │   └── templates/
│   └── school-pptx/
│       ├── SKILL.md
│       ├── fixtures/
│       ├── references/
│       ├── scripts/
│       └── templates/
├── templates/
│   ├── README.md
│   └── skill/
│       └── SKILL.md
└── .planning/
    ├── PROJECT.md
    ├── REQUIREMENTS.md
    ├── ROADMAP.md
    ├── STATE.md
    └── config.json
```

## 如何添加新技能

1. 复制 `templates/skill/SKILL.md` 到 `skills/<skill-name>/SKILL.md`。
2. 填写 `name`、`description`、目标、触发条件、流程、输出和成功标准。
3. 在同一个 `SKILL.md` 的 `Runtime Adapter Notes` 中补齐 Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw 和 Hermes Agent 的最小兼容说明。
4. 保持 `SKILL.md` 是 semantic entry：入口里只写 agent 必须先读的 workflow map；完整字段表、格式规则、renderer notes、fixture 说明、长验证清单和排障内容放到 `skills/<skill-name>/references/`，并从入口显式链接。
5. 把可调用命令放到 `scripts/`；把输出 scaffold、完整 Markdown 样板或渲染模板放到 `templates/`。不要把示例正文和模板、长说明和脚本混在一起。
6. 文档工作流技能必须先按 `docs/markdown-normalization-contract.md` 把源材料归一化为 Markdown intermediate，再生成 Typst、HTML 或其他目标输出。
7. 所有写文件的技能必须遵守 `docs/clean-delivery-directory-contract.md`：交付一级目录只放当前 Markdown 和当前最终产物，多轮修改成套归档到 `history/`，临时验证不得散落。
8. 如果某个 runtime 的说明变长，先压缩成必要检查点；不要为 v1 新增独立 adapter 文件。
9. 如果确实需要给贡献者看一个参考样例，再创建 `examples/<example-name>/SKILL.md`，但不要把它当成 v1 依赖。
10. 更新 `docs/compatibility-matrix.md` 中相关 runtime 的支持状态；不要在未验证时声称完整支持。

## 分解后的查找路径

贡献者和 reviewer 应先读技能入口，再按需要打开支持文件：

1. `skills/<skill-name>/SKILL.md` 确认触发意图、Markdown intermediate、公开脚本入口、输出概览、验证入口、安全边界和 runtime adapter notes。
2. `skills/<skill-name>/templates/` 查找可复制的 Markdown intermediate 或输出 scaffold。
3. `skills/<skill-name>/references/` 查找 artifact contract、renderer notes、字段表、UAT 和排障细节。
4. `skills/<skill-name>/scripts/` 查找公开 helper command；脚本内部可以按职责拆成 skill-local modules，但不得改变公共命令、常用 flags、输出文件名或 manifest keys。

## 共享参考资料

- `docs/clean-delivery-directory-contract.md`：所有写文件技能的公共交付底线，约束一级目录、支持资料目录、多轮修改归档、最小验证和失败清理。
- `docs/agent-output-cleanup-prompt.md`：用于审计和整理历史 agent 散乱产物的两阶段安全提示词。
- `references/scheduling-contract.md`：v1.11 integrated teaching-design package 的共享排课合同，定义 `calendar.dates`、`first_teaching_day`、`daily_hours`、按源顺序消费的教学项、日期/周次/星期/学时派生证据和 `## 复核标记` 处理规则。
- `test/1.11/scheduling-contract/`：Phase 22 排课合同 fixture evidence，包含复用 v1.10 授课计划形状的 fixture source、确定性 `expected-schedule.json` 和教师可复核的 `expected-schedule.md`。

## 已有技能

- `end-of-term-teaching-materials`：用于整理期末教学提交材料和表格，先输出可复核 Markdown intermediate，再以固定四件套事务发布 Markdown、Typst、PDF 和 XLSX；model、manifest 与评分证据不属于 current。Artifact contract 见 `skills/end-of-term-teaching-materials/references/data-contract.md` 和 `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md`。
- `graduate-resume`：用于整理毕业生简历的主题无关 canonical 资料，先冻结个人资料、教育、技能、项目、实训、目标岗位和照片状态，再进入后续主题、定向和离线 Markdown/Typst/PDF 生成。Phase 46 当前提供 `SKILL.md`、模板、fixtures、schema/reference 文档，以及可执行的离线 `validate` / `target` / `plan` / `verify` CLI。
- `gongwen`：用于写作、归一化和验证类公文文体文档，最终交付目录为 `documents/YYYYMMDD 事项名称/`，只保留同级 `标题.md`、`标题.typ`、`标题.pdf`；署名和日期由 YAML frontmatter 自动落款。Artifact contract 见 `skills/gongwen/references/format-and-rendering.md`。
- `school-presentation`：用于整理学校正式汇报、课程展示、培训课件、招生宣讲或项目答辩材料，先输出 `school-presentation-full.md` 结构的 Markdown logical-slide intermediate，再生成带学校视觉识别的离线 HTML 演示文稿。生成的 deck 内置 preview workspace、overview、playback、presenter markup、课堂 reveal/mask/peek/排序/结构化版式，以及一键最终 PDF 导出；PDF 会展开揭示内容、保留答案/强调/排序最终态、支持目录链接和 reader outline，并按当前章节页预览状态包含或跳过章节分隔页。Authoring、export 和 verification contract 分别见 `skills/school-presentation/references/authoring-and-layout.md`、`skills/school-presentation/references/playback-and-export.md` 和 `skills/school-presentation/references/verification-contract.md`。
- `school-pptx`：把已审阅的 Markdown logical slides 通过受控 `standard-school` template 生成原生可编辑 PowerPoint；[canonical skill](skills/school-pptx/SKILL.md) 提供 review-before-render 和 public `verify --workdir` 入口，自动结构 PASS 之后仍须在真实 Microsoft PowerPoint 或 WPS Presentation 中完成人工 UAT，不能由代理自动批准。
- `teaching-design-package`：用于整合授课计划和实操教案，先输出统一 Markdown intermediate，再由 package-owned model 和 renderer 生成 model-derived dynamic `1 + 1 + N` current bundle；model、status、module、merge 和 staging 证据只存在于 owned `.work` 或调用方 diagnostic workdir。正常运行不依赖 sibling skill folders。入口见 `skills/teaching-design-package/SKILL.md`，Artifact contract 见 `skills/teaching-design-package/references/format-and-orchestration.md`。
- `tiaokedan`：用于生成 `调课单`/`调课说明`，先输出教师可审阅的 `templates/tiaokedan.md` 结构 Markdown intermediate，再由 skill-local renderer 生成 Typst，并在教师确认后可选生成 PDF。Markdown 可省略标题、收文对象、表格序号列和表格后落款行；renderer 会补默认标题/收文对象、自动序号、frontmatter 落款，并用 `Songti SC` 优先的宋体标题 `weight: 700`。入口见 `skills/tiaokedan/SKILL.md`，Artifact contract 见 `skills/tiaokedan/references/markdown-contract.md` 和 `skills/tiaokedan/references/pdf-workflow.md`，公开 helper 见 `skills/tiaokedan/scripts/tiaokedan.sh`。
