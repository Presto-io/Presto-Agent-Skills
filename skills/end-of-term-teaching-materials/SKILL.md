---
name: "end-of-term-teaching-materials"
description: "Use when preparing semester-end teaching submission documents and tables from explicit course, class, roster, task, score, assessment, and submission data."
metadata:
  short-description: "期末教学材料固定模板渲染"
  version: "0.7.0"
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
- `out_dir`: 授权交付根；current 固定为 `end-of-term-full.md`、`end-of-term-package.typ`、`end-of-term-package.pdf`、`score-list.xlsx`，一级仅额外允许按需存在的 `sources/`、`assets/`、`history/`、`.work/`。
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
6. `deliver` 在 `.work/<run-id>/candidate/` 生成并验证完整四件套后才发布；逐文件 bytes 相同则保持 current inode/mtime 且不建 history，变化则把旧四件套整体归档到下一 `history/<sequence>/`。
7. Handled failure、`INT` 或 `TERM` 回滚旧四件套并清理本 run；unknown、partial、symlink、legacy hidden 或 stale `.work` 在 mutation 前失败关闭。成功根不得留下 JSON、CSV、manifest、status、model、日志、报告、staging 或失败产物。

## Runtime Adapter Notes

| Runtime | Whole-folder discovery | Explicit shell fallback | Dependencies | Execute/read/write | Sandbox/allowlist and delivery boundary |
|---------|------------------------|-------------------------|--------------|--------------------|-----------------------------------------|
| Codex | 通过项目指令或本地 skill 机制发现整个 folder，并保留 `references/`、`templates/`、`scripts/`。 | 自动脚本发现不可用时显式调用 `scripts/end-of-term-teaching-materials.sh`。 | 需要 Bash、Python 3、Typst；不联网、不自动安装。 | 验证脚本可执行、支持文件可读、授权根与 `.work` 可写。 | allowlist 覆盖完整 skill folder、输入和授权 delivery root；证据不得平铺到 root。 |
| Claude Code | 适用版本可 whole-folder 安装到 `.claude/skills/end-of-term-teaching-materials/`。 | 自动发现不可用时显式调用同一 shell 入口。 | 需要 Bash、Python 3、Typst；不联网、不自动安装。 | 验证 execute/read/write 与相对支持路径。 | sandbox 仅放行完整 skill folder、输入、delivery root 及其 `.work`。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向整个 canonical folder。 | 无自动发现时显式读取本文件并调用 shell 入口。 | 需要 Bash、Python 3、Typst；不联网、不自动安装。 | 安装后验证脚本执行、支持文件读取和目标写入。 | 明确批准输入、完整 folder、delivery root 与 `.work`，不扩大根白名单。 |
| OpenCode | 使用适用版本 native skill path 或 Claude-compatible fallback，保持 whole-folder 完整。 | 自动发现不可用时显式调用 shell 入口。 | 需要 Bash、Python 3、Typst；不联网、不自动安装。 | 验证 execute/read/write，不假定继承宿主权限。 | 配置 allowlist/sandbox 读取模板并仅写授权 root/`.work`。 |
| OpenClaw | exact skill root、frontmatter、support-file discovery 与 whole-folder 完整性必须 installation-time verification。 | automatic discovery 不作保证；installation-time verification 后仍保留显式 shell fallback。 | 安装时核验 Bash、Python 3、Typst；禁止联网与自动安装。 | installation-time verification 覆盖 execute/read/write。 | 安装时实测 allowlist/sandbox 只允许完整 folder、输入、delivery root 与 `.work`。 |
| Hermes Agent | exact local/global path、frontmatter、support-file discovery 与 whole-folder 完整性必须 installation-time verification。 | automatic discovery 不作保证；明确保留 shell invocation fallback。 | 安装时核验 Bash、Python 3、Typst；禁止联网与自动安装。 | installation-time verification 覆盖 execute/read/write。 | 安装时实测 allowlist/sandbox 和 delivery root/`.work` 写入边界。 |

## Outputs

- `end-of-term-full.md`: 唯一事实源和交付 Markdown。
- `end-of-term-package.typ`: 由 Markdown 生成的 Typst。
- `end-of-term-package.pdf`: Typst 编译出的 PDF。
- `score-list.xlsx`: 唯一 Excel，列为 `学号`、`姓名`、`平时成绩`、`期末成绩`，按学号递增排序。

四项 current 是不可拆分的固定 bundle；`sources/` 永不由普通发布变更，当前实现没有 managed assets，`history/` 不自动删除，`.work/` 仅承载本次 candidate/rollback/evidence 并在收尾清理。

## Verification

- [ ] `bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`
- [ ] `python3 -m py_compile skills/end-of-term-teaching-materials/scripts/render_package.py`
- [ ] `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh deliver --input <finalized-markdown> --out-dir <delivery-dir>`
- [ ] Successful delivery root contains the exact four current files plus only required support directories; identical rerun creates no history, changed rerun archives the whole prior bundle.
- [ ] `score-list.xlsx` contains only `学号`、`姓名`、`平时成绩`、`期末成绩` and is sorted by ascending student ID.
- [ ] Markdown/Typst are non-empty UTF-8, PDF starts with `%PDF-`, and XLSX reopens with required OOXML members; automated gates do not replace human content/layout review.
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
- 不承诺 SIGKILL、断电或四个路径的跨文件原子性；普通 `deliver` 不迁移 unknown/legacy 文件，也不自动删除 `history/`。
