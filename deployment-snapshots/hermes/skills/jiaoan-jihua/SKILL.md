---
name: "jiaoan-jihua"
description: "Use when creating Chinese teaching-schedule or lesson-plan progress tables in the jiaoan-jihua Markdown-to-Typst workflow."
metadata:
  short-description: "教案/授课进度计划 Markdown 到 Typst 工作流"
  version: "0.2.0"
  portability: "canonical"
  supported-runtimes:
    - Codex
    - Claude Code
    - Gemini CLI
    - OpenCode
    - OpenClaw
    - Hermes Agent
---

# Jiaoan Jihua

## Objective

把需要呈现为授课进度计划表的内容归一化为稳定的 `jiaoan-jihua-full.md` 结构，再通过技能自带 shell 脚本生成可编译的 Typst 文件。

## Use When

- 用户明确使用触发词 `jiaoan-jihua`。
- 用户需要写授课进度计划、教学安排、课程实施进度表或类似工学一体化课程进度安排。
- 用户给出课程元数据、学习任务、学习环节、学时分配、周次或校历，需要整理成可直接对接 Typst 的 Markdown intermediate。

## Inputs

- `source_material`: 用户给出的课程信息、任务结构、教学内容、周次安排或已有 Markdown。
- `references/calendar.json`: 教学日历/校历支持资源；当源材料依赖日期、周次或节假日排布时，先用它对齐教学进度，再写入 Markdown。
- `output_markdown`: 持久化的 jiaoan-jihua Markdown intermediate，默认结构见 `templates/jiaoan-jihua-full.md`。

## Process

1. 先按 `docs/markdown-normalization-contract.md` 把源材料归一化为 `YAML frontmatter + body` 的 Markdown intermediate。
2. 使用以下 frontmatter 字段：
   - `major_name`: 专业名称。
   - `course_name`: 课程名称。
   - `teacher_name`: 授课教师。
   - `class_name`: 授课班级。
   - `first_teaching_day`: `YYYY-MM-DD` 格式的首个授课日。
   - `daily_hours`: 可选；如果源材料明确给出每日学时，保留它。
   - `template`: 固定为 `jiaoan-jihua`。
3. 正文使用可审阅的 Markdown 表达结构：
   - `##` 作为学习任务标题。
   - `###` 作为学习环节标题，例如安技教育及旧知识回顾、明确任务、制定计划、工作准备、任务实施、成果展示、总结评价。
   - 每一行教学内容用 `-N` 结尾保留学时，便于模板映射到表格列。
4. 当源材料只给出日期、周次或总学时，而没有现成的任务分段时，先参考 `references/calendar.json` 还原教学日历，再写入 `jiaoan-jihua-full.md` 结构。
5. 生成 Markdown 后，运行 `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render` 生成 `.typ`；该转换必须由脚本内置 shell 逻辑完成，严禁调用外部可执行文件。
6. 若有参考 Typst，使用脚本的 `--expected-typ` 验证一致性。

## Script Usage

```bash
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh example --output jiaoan-jihua-full.md

skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render \
  --input jiaoan-jihua-full.md \
  --typ jiaoan-jihua-full.typ
```

带参考产物验证：

```bash
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render \
  --input /path/to/jiaoan-jihua-full.md \
  --typ /path/to/jiaoan-jihua-full.typ \
  --expected-typ /path/to/reference.typ
```

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 读取本 `SKILL.md` 后执行流程；用 shell 调用 `scripts/jiaoan-jihua.sh`；写文件前确认目标路径；PDF 编译若需要，必须在脚本外单独执行。 |
| Claude Code | 可把同一目录安装到 `.claude/skills/jiaoan-jihua/`；frontmatter 的 `description` 是触发入口；脚本属于显式外部命令，执行前检查路径和权限。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向本 `SKILL.md`；若无法自动发现脚本，按 `Script Usage` 手动调用。 |
| OpenCode | 使用可加载 `SKILL.md` 的 skill 路径；若走 Claude-compatible fallback，保持同一目录结构并验证脚本可执行。 |
| OpenClaw | 作为 AgentSkills-compatible 目录使用；安装时验证 frontmatter 解析、技能根目录、脚本 allowlist 和 shell 脚本执行权限。 |
| Hermes Agent | 使用 `SKILL.md` skill folder；安装时验证项目级/全局技能路径、脚本发现行为和 shell 脚本执行权限。 |

## Outputs

- `jiaoan-jihua-full.md` 结构的 Markdown intermediate。
- 由 `scripts/jiaoan-jihua.sh` 内置 shell 渲染器生成的 `.typ` 文件。

## Verification

- [ ] `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh example --output <file>` 能输出可审阅的 `jiaoan-jihua-full.md` 结构。
- [ ] `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render --input <md> --typ <typ>` 能不依赖任何外部可执行文件生成 Typst。
- [ ] 对给定 fixture 运行 `--expected-typ` 时，生成 Typst 与参考文件一致。
- [ ] OpenClaw 与 Hermes Agent 的运行时差异保留在 adapter notes 中，没有写入 canonical 主流程。

## Success Criteria

- 技能在触发词 `jiaoan-jihua` 下能指导 agent 产出授课进度计划 Markdown intermediate。
- 脚本能从 `jiaoan-jihua-full.md` 生成稳定 Typst。
- 技能保持 canonical 单文件语义源，不引入 runtime-specific wrapper。

## Safety

- 不要静默删除源材料中不确定、缺失或无法表达的周次、学时或任务分段；必须就近标记复核。
- 不要把凭据、私有路径或用户专属资源写入正文，除非用户明确要求。
- 脚本的 Markdown 到 Typst 转换不得调用外部模板二进制、PDF 编译器或任何其他外部可执行文件。
- 脚本只读取输入 Markdown，并只写入用户指定的 Typst 输出路径；输出路径的父目录必须已存在。
