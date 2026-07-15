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

- `end-of-term-teaching-materials`：用于整理期末教学提交材料和表格，先输出 `end-of-term-full.md` 结构的可复核 Markdown intermediate，再生成固定模板 Typst/PDF、manifest、确定性表格产物、calculated score evidence 和 workbook。Artifact contract 见 `skills/end-of-term-teaching-materials/references/data-contract.md` 和 `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md`。
- `gongwen`：用于写作、归一化和验证类公文文体文档，最终交付目录为 `documents/YYYYMMDD 事项名称/`，只保留同级 `标题.md`、`标题.typ`、`标题.pdf`；署名和日期由 YAML frontmatter 自动落款。Artifact contract 见 `skills/gongwen/references/format-and-rendering.md`。
- `school-presentation`：用于整理学校正式汇报、课程展示、培训课件、招生宣讲或项目答辩材料，先输出 `school-presentation-full.md` 结构的 Markdown logical-slide intermediate，再生成带学校视觉识别的离线 HTML 演示文稿。生成的 deck 内置 preview workspace、overview、playback、presenter markup、课堂 reveal/mask/peek/排序/结构化版式，以及一键最终 PDF 导出；PDF 会展开揭示内容、保留答案/强调/排序最终态、支持目录链接和 reader outline，并按当前章节页预览状态包含或跳过章节分隔页。Authoring、export 和 verification contract 分别见 `skills/school-presentation/references/authoring-and-layout.md`、`skills/school-presentation/references/playback-and-export.md` 和 `skills/school-presentation/references/verification-contract.md`。
- `school-pptx`：把已审阅的 Markdown logical slides 通过受控 `standard-school` template 生成原生可编辑 PowerPoint；[canonical skill](skills/school-pptx/SKILL.md) 提供 review-before-render 和 public `verify --workdir` 入口，自动结构 PASS 之后仍须在真实 Microsoft PowerPoint 或 WPS Presentation 中完成人工 UAT，不能由代理自动批准。
- `teaching-design-package`：用于整合授课计划和实操教案，先输出 `teaching-design-package-full.md` 结构的整包 Markdown intermediate，再由 package-owned model、skill-local calendar、授课计划 renderer 和教学设计 renderer 生成课程名前缀公开交付文件；当前公开交付为主 Markdown、合并教学资料 PDF、授课进度计划表 PDF 和教学设计方案 PDF，诊断/model/work/staging 留在隐藏 `.teaching-design-package/`。授课进度计划和教学设计方案的旧版式规则已迁入 package-owned renderer，正常运行不依赖 sibling skill folders。入口见 `skills/teaching-design-package/SKILL.md`，Artifact contract 见 `skills/teaching-design-package/references/format-and-orchestration.md`，模板见 `skills/teaching-design-package/templates/teaching-design-package-full.md`，公开 helper 见 `skills/teaching-design-package/scripts/teaching-design-package.sh`。
- `tiaokedan`：用于生成 `调课单`/`调课说明`，先输出教师可审阅的 `templates/tiaokedan.md` 结构 Markdown intermediate，再由 skill-local renderer 生成 Typst，并在教师确认后可选生成 PDF。Markdown 可省略标题、收文对象、表格序号列和表格后落款行；renderer 会补默认标题/收文对象、自动序号、frontmatter 落款，并用 `Songti SC` 优先的宋体标题 `weight: 700`。入口见 `skills/tiaokedan/SKILL.md`，Artifact contract 见 `skills/tiaokedan/references/markdown-contract.md` 和 `skills/tiaokedan/references/pdf-workflow.md`，公开 helper 见 `skills/tiaokedan/scripts/tiaokedan.sh`。
