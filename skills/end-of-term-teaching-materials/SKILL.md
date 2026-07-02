---
name: "end-of-term-teaching-materials"
description: "Use when preparing semester-end teaching submission documents and tables from explicit course, class, roster, task, score, assessment, and submission data."
metadata:
  short-description: "期末教学材料固定模板渲染"
  version: "0.6.0"
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

把期末提交材料需要的课程、班级、教师、学期、过程考核、成绩、分析和交接信息整理成唯一可复核、可手工编辑的 `end-of-term-full.md`。教师和 agent 通过多轮沟通不断修正这份 Markdown；定稿后由 Markdown 直接生成 Typst、PDF 和一个 4 列成绩清单 workbook。

## Use When

- 用户需要生成或整理期末教学提交材料、成绩相关表格、教学日志封面、过程考核评价表封面或交接班记录封面。
- 用户上传了花名册、成绩表、过程考核照片/表格、平时表现、考试、分析文本和提交元数据，需要整理成一份可审阅 Markdown。
- 用户需要通过反复沟通修正 Markdown，并从定稿 Markdown 生成固定模板 Typst/PDF 和一个 4 列 Excel 成绩清单。

## Inputs

- `source_materials`: 用户上传或描述的原始资料；agent 负责整理进 Markdown，不要求用户维护 JSON/CSV。
- `output_markdown`: 唯一事实源 Markdown，默认结构见 `templates/end-of-term-full.md`。
- `review_answers`: 用户对 `## 复核标记` 中不确定成绩、缺失字段或 AI 草稿内容的逐项确认或修正。
- `out_dir`: 输出目录；成功交付根目录只包含 Markdown、Typst、PDF 和一个 4 列 Excel 成绩清单。
- `references/workflow-and-artifacts.md`: 复核链、导出闸门、score/template 规则和成功交付边界。
- `references/rendering-style.md`, `references/cover-template-notes.md`, `references/scorebook-template-notes.md`: 固定模板排版和封面/记分册说明。

## Script Usage

```bash
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh validate --input /tmp/end-of-term-full.md
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh deliver --input /tmp/end-of-term-full.md --out-dir /tmp/end-of-term-delivery
```

Additional commands:

- `deliver --input <markdown.md> --out-dir <dir>` is the normal final path. It writes only `end-of-term-full.md`, `end-of-term-package.typ`, `end-of-term-package.pdf`, and `score-list.xlsx`.
- `validate --input <markdown.md>` checks required metadata, task/score consistency, package flags, and export readiness.
- `info` prints a short workflow summary.
- `version` prints the script version.

The normal workflow does not expose JSON, CSV, manifest, task-map, score-summary, highlight-evidence, or extra workbook files as successful delivery outputs.

## Process

1. Read the uploaded source materials and organize them into `end-of-term-full.md`; do not make JSON/CSV the user-facing source of truth.
2. Keep all data diagnosis in the Markdown: missing facts and uncertain scores go under `## 复核标记`; analysis revisions go under `## 分析`.
3. Work with the teacher through multiple turns, editing the Markdown after each confirmation or correction.
4. Clear review markers one item at a time. Normal final export requires `## 复核标记` to be exactly `无`.
5. Render with `deliver` only after the review gate is clear. Preserve blank cells, declared task columns, package flags, and fixed-template scoring rules from `references/workflow-and-artifacts.md`.
6. Successful delivery must not leave JSON, CSV, manifest, task-map, score-summary, highlight-evidence, verification output, or extra workbook files in the public output directory.

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 读取本 `SKILL.md`、`references/data-contract.md`、`references/workflow-and-artifacts.md`、固定模板说明和脚本后执行；先把源资料整理成唯一 Markdown，反复沟通修正，再用 `deliver` 生成公开四件套。 |
| Claude Code | 可安装到 `.claude/skills/end-of-term-teaching-materials/`；frontmatter 的 `description` 是触发入口；复核项可用 AskUserQuestion 或普通对话逐项确认；脚本执行前仍要验证文件写入边界。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向本 `SKILL.md`；若缺少专用交互工具，用编号列表收集复核答案；执行脚本时显式传入 `--input` 和 `--out-dir`，不要依赖自动发现。 |
| OpenCode | 使用可加载 `SKILL.md` 的 skill 路径；若走 Claude-compatible fallback，保持同一目录结构；验证 `references/`、`templates/`、`scripts/` 可读，且脚本只写入允许目录。 |
| OpenClaw | 作为 AgentSkills-compatible 目录使用；安装时验证 frontmatter 解析、reference/template 读取、脚本执行权限、文件写入权限和用户复核退路；如果脚本未被自动发现，显式调用 `scripts/end-of-term-teaching-materials.sh`。 |
| Hermes Agent | 使用 `SKILL.md` skill folder；安装时验证项目级/全局技能路径、支持文件读取、脚本执行权限、可写输出目录和用户追问能力；不要假设自动脚本发现，必要时手动调用脚本。 |

## Outputs

- `end-of-term-full.md`: 唯一事实源和交付 Markdown。
- `end-of-term-package.typ`: 由 Markdown 生成的 Typst。
- `end-of-term-package.pdf`: Typst 编译出的 PDF。
- `score-list.xlsx`: 唯一 Excel，列为 `学号`、`姓名`、`平时成绩`、`期末成绩`，按学号递增排序。

## Verification

- [ ] `bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`
- [ ] `python3 -m py_compile skills/end-of-term-teaching-materials/scripts/render_package.py`
- [ ] `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh deliver --input <finalized-markdown> --out-dir <delivery-dir>`
- [ ] Successful delivery directory contains only `end-of-term-full.md`, `end-of-term-package.typ`, `end-of-term-package.pdf`, and `score-list.xlsx`.
- [ ] `score-list.xlsx` contains only `学号`、`姓名`、`平时成绩`、`期末成绩` and is sorted by ascending student ID.
- [ ] Runtime adapter notes mention Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.

## Success Criteria

- 技能能指导 agent 产出一份可审阅、可手工编辑、可后续渲染的期末教学材料 Markdown intermediate。
- 脚本能从定稿 Markdown 生成 Typst，并在 Typst 可用时编译 PDF package。
- Renderer 能稳定输出 4 列 `score-list.xlsx`，且内容来自 Markdown 计算结果并按学号递增排序。
- 复核未清除时不会声称最终导出、打印或提交材料已经完成。
- 长工作流和 scoring 细节位于 `references/workflow-and-artifacts.md`，入口保持清晰可读。
- OpenClaw 与 Hermes Agent 的脚本权限、写入权限和 fallback 行为有明确 adapter notes。

## Safety

- 不要把真实学生隐私、成绩原件、私有路径、凭据或隐藏 source list 写入可复用模板或 workbook。
- 不要把空成绩单元格改成 `0`、`-1` 或自动复核项；空白就是空白，除非用户另行说明。
- 不要根据“看起来合理”补齐缺失成绩、教师、班级、学期或交接信息；缺失项必须显式标记复核。
- 不要在 canonical 主流程写入某个 runtime 的私有语法；差异只放在 `Runtime Adapter Notes`。
- 不要把自动生成 PDF/workbook 说成替代人工格式验收；它们是从定稿 Markdown 生成的交付产物。
