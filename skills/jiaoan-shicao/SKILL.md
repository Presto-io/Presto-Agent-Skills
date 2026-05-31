---
name: "jiaoan-shicao"
description: "Use when writing, normalizing, or rendering hands-on lesson plans, practical training lesson plans, vocational education teaching activity designs, project-based teaching units, or documents that must use the Presto jiaoan-shicao template."
metadata:
  short-description: "实操教案 Markdown 到 Typst/PDF 工作流"
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

# Jiaoan Shicao

## Objective

把课程内容、实训安排、教学活动设计或项目化教学单元归一化为稳定的 `jiaoan-shicao-full.md` 结构，再通过 Presto `jiaoan-shicao` 模板生成可编译的 Typst 文件和 PDF 验证产物。

## Use When

- 用户明确使用触发词 `jiaoan-shicao`。
- 用户需要写实操教案、实训教案、职业教育教案、课程教案表、教学活动设计或项目化教学单元。
- 用户需要把已有课程材料整理成可直接对接 Typst 实操教案模板的 Markdown intermediate。

## Inputs

- `source_material`: 用户给出的课程资料、实训任务、教学目标、活动安排、评价要求或已有 Markdown。
- `output_markdown`: 持久化的 `jiaoan-shicao-full.md` 风格 Markdown intermediate，默认结构见 `templates/jiaoan-shicao-full.md`。
- `calendar_json`: 支持资源，默认见 `references/calendar.json`；用于核对授课日期、排课顺序或维护旧材料中的日历语义。
- `template_binary`: Presto `jiaoan-shicao` 模板可执行文件，默认路径为 `/Users/mrered/Library/Application Support/com.mrered.presto/templates/jiaoan-shicao/presto-template-jiaoan-shicao`；可用 `JIAOAN_SHICAO_TEMPLATE_BINARY` 或脚本参数覆盖。

## Process

1. 先按 `docs/markdown-normalization-contract.md` 把源材料归一化为 `YAML frontmatter + body` 的 Markdown intermediate。
2. frontmatter 使用固定字段：
   - `template`: 固定为 `jiaoan-shicao`。
   - `course_name`: 课程名称。
   - `course_attribute`: 通常为 `基本技能课程` 或 `工学一体化课程`。
   - `textbook_name`: 教材名称；未知时留空。
   - `class_name`: 教学班级；未知时留空。
   - `total_hours`: 计划总课时；维护旧式完整样例时可保留。
   - `teacher_name`: 教师姓名；未知时留空。
   - `use_time`: 使用时间；维护旧式完整样例时可保留。
   - `first_teaching_day`: 课程排课起点；新文档若用户给出授课起点，优先用 `YYYY-MM-DD`。
3. 正文保持三大部分，顺序固定：
   - `## 学习任务分析`，包含 `学习任务：`、`课时：`、`起止日期：` 三个字段行，以及 `### 一、学习任务描述` 到 `### 五、学习资源` 五个分析块。
   - `## 教学活动设计——主题`，用 `### 学习环节——学习单元`、`#### 活动名称`、`##### 课时` 表达活动表。每个 `#####` 后按空行分隔四个内容块：学习内容、学生活动、教师活动、教学方法与手段。
   - `## 学业评价`，评价项使用 `1. 考核项目；考核细则；考核方式`，末尾保留 `小结：...`。
4. 材料不足时仍输出完整骨架；不确定的学校、教材版本、班级、教师、日期和评价结论留空或标记复核，不要虚构。
5. 生成 Markdown 后，运行 `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render` 生成 `.typ`，必要时同时生成 `.pdf`。
6. 若有参考 Typst 或 PDF，使用脚本的 `--expected-typ`、`--expected-pdf` 进行黑盒验证。Typst 必须逐字节一致；PDF 以成功编译为主，参考 PDF 校验允许 Typst 元数据造成的非内容字节差异。

## Script Usage

```bash
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example \
  --output jiaoan-shicao-full.md \
  --calendar-output calendar.json

skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input jiaoan-shicao-full.md \
  --typ jiaoan-shicao-full.typ \
  --pdf jiaoan-shicao-full.pdf
```

带参考产物验证：

```bash
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input /path/to/jiaoan-shicao-full.md \
  --typ /path/to/jiaoan-shicao-full.typ \
  --pdf /path/to/jiaoan-shicao-full.pdf \
  --expected-typ /path/to/reference.typ \
  --expected-pdf /path/to/reference.pdf
```

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 读取本 `SKILL.md` 后执行流程；用 shell 调用 `scripts/jiaoan-shicao.sh`；写文件前确认目标路径，验证时运行 `typst compile`。 |
| Claude Code | 可把同一目录安装到 `.claude/skills/jiaoan-shicao/`；frontmatter 的 `description` 是触发入口；脚本属于显式外部命令，执行前检查路径和权限。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向本 `SKILL.md`；若无法自动发现脚本，按 `Script Usage` 手动调用。 |
| OpenCode | 使用可加载 `SKILL.md` 的 skill 路径；若走 Claude-compatible fallback，保持同一目录结构并验证脚本可执行。 |
| OpenClaw | 作为 AgentSkills-compatible 目录使用；安装时验证 frontmatter 解析、技能根目录、脚本 allowlist、sandbox 对外部模板路径和 `calendar.json` 支持资源的访问。 |
| Hermes Agent | 使用 `SKILL.md` skill folder；安装时验证项目级/全局技能路径、脚本发现行为，以及是否允许读取 Presto 模板可执行文件和支持资源。 |

## Outputs

- `jiaoan-shicao-full.md` 结构的 Markdown intermediate。
- 由 Presto `jiaoan-shicao` 模板生成的 `.typ` 文件。
- 由 Typst 编译生成的 `.pdf` 验证产物。

## Verification

- [ ] `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example --output <file>` 能输出可审阅的 `jiaoan-shicao-full.md` 结构。
- [ ] `--calendar-output <file>` 能复制随技能提供的 `calendar.json` 支持资源。
- [ ] `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --input <md> --typ <typ>` 能通过 Presto `jiaoan-shicao` 模板生成 Typst。
- [ ] `typst compile <typ> <pdf>` 能成功生成 PDF。
- [ ] 对给定 fixture 运行 `--expected-typ` 时，生成 Typst 与参考文件一致。
- [ ] OpenClaw 与 Hermes Agent 的运行时差异保留在 adapter notes 中，没有写入 canonical 主流程。

## Success Criteria

- 技能在触发词 `jiaoan-shicao` 下能指导 agent 产出完整实操教案 Markdown intermediate。
- 脚本能从 `jiaoan-shicao-full.md` 生成与 Presto 模板一致的 Typst，并编译出 PDF。
- 技能保持 canonical 单文件语义源，不引入 runtime-specific wrapper。

## Safety

- 不要静默删除源材料中不确定、缺失或无法表达的内容；必须就近标记复核或留空。
- 不要虚构学校名称、教师姓名、教学班级、教材版本、授课日期或用户没有暗示的评价结论。
- 默认模板路径是本机 Presto 安装路径；在其他机器上运行时必须显式验证路径存在且可执行。
- 脚本只读取输入 Markdown、模板可执行文件、随技能提供的 `calendar.json` 和 Typst 编译所需资源，并只写入用户指定的输出路径。
