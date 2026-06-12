---
name: "end-of-term-teaching-materials"
description: "Use when preparing semester-end teaching submission documents and tables from explicit course, class, roster, task, score, assessment, and submission data."
metadata:
  short-description: "期末教学材料固定模板渲染"
  version: "0.5.3"
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

把期末提交材料需要的课程、班级、教师、学期、过程考核、成绩、分析和交接信息整理成一份可复核的 `end-of-term-full.md` Markdown intermediate，再通过固定 skill-local 模板生成 Typst/PDF、manifest、确定性表格产物、calculated score evidence 和 teacher-facing workbook。

## Use When

- 用户需要生成或整理期末教学提交材料、成绩相关表格、教学日志封面、过程考核评价表封面或交接班记录封面。
- 用户提供了明确结构化数据，或提供了可整理成结构化数据的花名册、过程考核任务、成绩、平时表现、考试、分析文本和提交元数据。
- 用户需要先检查一份 Markdown 源文件，再生成固定模板 Typst/PDF、deterministic table artifacts 和 scorebook workbook。

## Inputs

- `source_data`: 明确结构化 JSON，至少覆盖课程、班级、教师、学期、学生名单、过程考核任务、成绩和 package flags。字段契约见 `references/data-contract.md`。
- `output_markdown`: 持久化 Markdown intermediate，默认结构见 `templates/end-of-term-full.md`。
- `review_answers`: 用户对 `## 复核标记` 中不确定成绩、缺失字段或 AI 草稿内容的逐项确认或修正。
- `workdir`: 已存在的输出目录；脚本只写入该目录或显式 `--output` 路径。
- `references/workflow-and-artifacts.md`: 复核链、导出闸门、score/template 规则、artifact 列表和详细验证规则。
- `references/rendering-style.md`, `references/cover-template-notes.md`, `references/scorebook-template-notes.md`: 固定模板排版和封面/记分册说明。

## Script Usage

```bash
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh example --output /tmp/end-of-term-source.json
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh markdown --input /tmp/end-of-term-source.json --output /tmp/end-of-term-full.md
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh render --input /tmp/end-of-term-full.md --workdir /tmp/end-of-term-output --pdf
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh render --input /tmp/end-of-term-full.md --workdir /tmp/end-of-term-preview --pdf --abnormal-review
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh verify --workdir /tmp/end-of-term-verify
```

Additional commands:

- `validate --input <source.json|markdown.md>` checks required metadata, task/score consistency, package flags, and export readiness.
- `render --abnormal-review` is only for explicitly requested unresolved-review inspection artifacts; it keeps `final_ready=false` and must not be treated as a final submission package.
- `manifest` prints machine-readable command/output metadata.
- `info` prints a short workflow summary.
- `version` prints the script version.

Parent directories for `--output` must already exist. `--workdir` must already exist.

## Process

1. Normalize source material into explicit structured JSON following `references/data-contract.md`.
2. Generate or update `end-of-term-full.md`; keep the reviewable Markdown sections listed in `references/workflow-and-artifacts.md`.
3. Draft `## 分析` from teacher-provided context and score evidence; do not rely only on generic AI prose.
4. Clear review markers one item at a time with the teacher. Normal final export requires `## 复核标记` to be exactly `无`.
5. If unresolved items remain and the user explicitly wants inspection artifacts, explain the unresolved items first, ask whether to generate an abnormal preview, then use `render --abnormal-review`.
6. Render normally only after the review gate is clear. Preserve blank cells, declared task columns, package flags, and fixed-template scoring rules from `references/workflow-and-artifacts.md`.
7. Run `verify --workdir <dir>` before delivery. Missing Typst is reported explicitly in the manifest instead of silently passing as a PDF success.

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 读取本 `SKILL.md`、`references/data-contract.md`、`references/workflow-and-artifacts.md`、固定模板说明和脚本后执行；写入前确认 `--output` parent 和 `--workdir` 已存在；用 `bash -n`、`python3 -m py_compile` 和 `verify --workdir` 做本地黑盒验证。 |
| Claude Code | 可安装到 `.claude/skills/end-of-term-teaching-materials/`；frontmatter 的 `description` 是触发入口；复核项可用 AskUserQuestion 或普通对话逐项确认；脚本执行前仍要验证文件写入边界。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向本 `SKILL.md`；若缺少专用交互工具，用编号列表收集复核答案；执行脚本时显式传入 `--input`、`--output` 和 `--workdir`，不要依赖自动发现。 |
| OpenCode | 使用可加载 `SKILL.md` 的 skill 路径；若走 Claude-compatible fallback，保持同一目录结构；验证 `references/`、`templates/`、`scripts/` 可读，且脚本只写入允许目录。 |
| OpenClaw | 作为 AgentSkills-compatible 目录使用；安装时验证 frontmatter 解析、reference/template 读取、脚本执行权限、文件写入权限、fixture verification 和用户复核退路；如果脚本未被自动发现，显式调用 `scripts/end-of-term-teaching-materials.sh`。 |
| Hermes Agent | 使用 `SKILL.md` skill folder；安装时验证项目级/全局技能路径、支持文件读取、脚本执行权限、可写 workdir、fixture verification 和用户追问能力；不要假设自动脚本发现，必要时手动调用脚本并检查 manifest fallback。 |

## Outputs

- `end-of-term-full.md`: persistent Markdown intermediate。
- Typst/PDF package, `manifest.json`, deterministic table artifacts, calculated score evidence, score-list workbook, and teacher-facing scorebook workbook。
- Full artifact list and scoring evidence contract are maintained in `references/workflow-and-artifacts.md`。

## Verification

- [ ] `bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`
- [ ] `python3 -m py_compile skills/end-of-term-teaching-materials/scripts/render_package.py`
- [ ] `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh verify --workdir <existing-dir>`
- [ ] Manifest and deterministic table/workbook checks listed in `references/workflow-and-artifacts.md` pass.
- [ ] Runtime adapter notes mention Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.

## Success Criteria

- 技能能指导 agent 产出一份可审阅、可手工编辑、可后续渲染的期末教学材料 Markdown intermediate。
- 脚本能从结构化 JSON 生成 Markdown，从 Markdown 生成 Typst，并在 Typst 可用时编译 merged PDF package。
- Renderer 能稳定输出 deterministic table artifacts、calculated score evidence 和 teacher-facing workbook，且 PDF 显示值与 calculated score evidence 一致。
- 复核未清除时不会声称最终导出、打印或提交材料已经完成。
- 长工作流、artifact 和 scoring 细节位于 `references/workflow-and-artifacts.md`，入口保持清晰可读。
- OpenClaw 与 Hermes Agent 的脚本权限、写入权限、fixture verification 和 fallback 行为有明确 adapter notes。

## Safety

- 不要把真实学生隐私、成绩原件、私有路径、凭据或隐藏 source list 写入可复用模板、fixture、manifest 或 workbook。
- 不要把空成绩单元格改成 `0`、`-1` 或自动复核项；空白就是空白，除非用户另行说明。
- 不要根据“看起来合理”补齐缺失成绩、教师、班级、学期或交接信息；缺失项必须显式标记复核。
- 不要在 canonical 主流程写入某个 runtime 的私有语法；差异只放在 `Runtime Adapter Notes`。
- 不要把自动生成 PDF/workbook 说成替代人工格式验收；它们是提交前验证和人工复核的支持产物。
