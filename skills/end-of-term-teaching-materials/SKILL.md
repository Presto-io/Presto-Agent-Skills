---
name: "end-of-term-teaching-materials"
description: "Use when preparing semester-end teaching submission documents and tables from explicit course, class, roster, task, score, assessment, and submission data."
metadata:
  short-description: "期末教学材料 Markdown 契约"
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

# End-of-Term Teaching Materials

## Objective

把期末提交材料需要的课程、班级、教师、学期、过程考核、成绩、分析和交接信息整理成一份可复核、可手工编辑的 `end-of-term-full.md` Markdown intermediate，为后续固定模板渲染保留稳定数据入口。

## Use When

- 用户需要生成或整理期末教学提交材料、成绩相关表格、教学日志封面、过程考核评价表封面或交接班记录封面。
- 用户提供了明确结构化数据，或提供了可整理成结构化数据的花名册、过程考核任务、成绩、平时表现、考试、分析文本和提交元数据。
- 用户需要先检查一份 Markdown 源文件，再在后续步骤生成固定模板 Excel、Typst、PDF 或其他提交材料。

## Inputs

- `source_data`: 明确的结构化数据，至少覆盖课程、班级、教师、学期、过程考核任务、成绩或待提交材料开关。字段契约见 `references/data-contract.md`。
- `output_markdown`: 持久化 Markdown intermediate，默认结构见 `templates/end-of-term-full.md`。
- `review_answers`: 用户对 `## 复核标记` 中不确定成绩、缺失字段或 AI 草稿内容的逐项确认或修正。

## Process

1. 先按 `docs/markdown-normalization-contract.md` 把源材料归一化为 `YAML frontmatter + body` 的 Markdown intermediate。
2. 使用 `references/data-contract.md` 校验输入字段。必须显式处理 course、class、teacher、semester、teaching-hour/task、assessment 和 submission metadata；不能把未知字段藏入隐藏 source list。
3. 生成或更新 `end-of-term-full.md`，流程固定为 `structured data -> Markdown -> later fixed-template rendering`。Phase 11 只建立 Markdown 契约；不要在本技能阶段声称 Excel、Typst、PDF 或 deterministic table artifacts 已生成完成。
4. 最终 Markdown frontmatter 禁止包含 `sources` 字段，也不要在正文末尾追加隐藏来源清单。源材料可用于整理 Markdown，但教师复核的唯一持久源是这份 Markdown。
5. 在正文中保留可审阅章节，至少包含 `## 我带的学生`、`## 过程考核任务`、`## 成绩数据`、`## 分析` 和 `## 复核标记`。
6. 对缺失、歧义或有损识别的数据使用显式复核标记。手写或图片识别不确定的成绩写作 `87?` 这类内联值，并在 `## 复核标记` 中加入同一事项。
7. 逐项执行复核循环：每个问题必须说清学生、任务或字段、当前值，例如“学生乙「CA6140卧式车床控制线路安装与调试」成绩识别为 87，请确认。”用户确认或修正后，立即编辑 Markdown 中的值，并删除对应复核项。
8. 当 `## 复核标记` 还有任何内容不是 `无` 时，不要声明最终导出已就绪。全部复核清除后，该节正文必须正好是 `无`。
9. 结束时报告剩余复核项；如果没有剩余项，明确说明复核已清除。

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 读取本 `SKILL.md`、`references/data-contract.md` 和 `templates/end-of-term-full.md` 后执行；写 Markdown 前确认目标路径；没有独立问询工具时用简洁文本逐项询问复核项。 |
| Claude Code | 可把同一目录安装到 `.claude/skills/end-of-term-teaching-materials/`；frontmatter 的 `description` 是触发入口；复核项可用 AskUserQuestion 或普通对话逐项确认。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向本 `SKILL.md`；若缺少专用交互工具，用编号列表逐项收集复核答案，再回写 Markdown。 |
| OpenCode | 使用可加载 `SKILL.md` 的 skill 路径；若走 Claude-compatible fallback，保持同一目录结构，并验证 `references/` 与 `templates/` 可被读取。 |
| OpenClaw | 作为 AgentSkills-compatible 目录使用；安装时验证 frontmatter 解析、技能根目录、文件写入权限和复核问询退路，不把未验证的渲染命令加入 allowlist。 |
| Hermes Agent | 使用 `SKILL.md` skill folder；安装时验证项目级/全局技能路径、支持文件读取行为和用户追问能力；不要假设自动脚本发现，因为 Phase 11 不提供脚本。 |

## Outputs

- `end-of-term-full.md` 结构的 Markdown intermediate。
- 需要用户确认的复核项清单，或“复核已清除”的运行结果说明。

## Verification

- [ ] `end-of-term-full.md` 使用 `YAML frontmatter + body`，且不包含 `sources` frontmatter 或隐藏来源清单。
- [ ] Markdown 覆盖课程、班级、教师、学期、过程考核任务、成绩、分析和提交材料开关。
- [ ] `## 复核标记` 存在；只要内容不是 `无`，agent 不声明最终导出就绪。
- [ ] 不确定值如 `87?` 同时出现在成绩表和复核标记中。
- [ ] Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw、Hermes Agent 的差异只写在 adapter notes 中。

## Success Criteria

- 技能能指导 agent 产出一份可审阅、可手工编辑、可后续渲染的期末教学材料 Markdown intermediate。
- 所有缺失、歧义或有损数据都能通过内联标记和 `## 复核标记` 暴露给教师复核。
- 复核未清除时不会声称最终导出、打印或提交材料已经完成。
- Phase 11 不新增渲染脚本，不实现 OCR、Excel、Typst、PDF 或 deterministic table artifact 输出。

## Safety

- 不要把真实学生隐私、成绩原件、私有路径、凭据或隐藏 source list 写入可复用模板。
- 不要把空成绩单元格改成 `0`、`-1` 或自动复核项；空白就是空白，除非用户另行说明。
- 不要根据“看起来合理”补齐缺失成绩、教师、班级、学期或交接信息；缺失项必须显式标记复核。
- 不要在 canonical 主流程写入某个 runtime 的私有语法；差异只放在 `Runtime Adapter Notes`。
