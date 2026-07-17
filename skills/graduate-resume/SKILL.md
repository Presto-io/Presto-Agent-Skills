---
name: "graduate-resume"
description: "Use when collecting, reviewing, validating, and preparing a verified Chinese graduate resume source package for offline generic or targeted resume generation with optional photo and deterministic Markdown/Typst/PDF outputs."
metadata:
  short-description: "毕业生简历资料契约与离线生成工作流"
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

# Graduate Resume

## Objective

把毕业生提供的个人资料、教育、技能、项目、实训、经历、目标岗位和照片信息整理为一份可审阅、可验证、可离线消费的 `graduate-resume.md`。在资料通过校验后，再进入后续主题规划、定向选择和 Markdown/Typst/PDF 渲染流程。

## Use When

- 用户要整理一名电气、机电、智能制造、发电厂或新能源方向大专毕业生的真实简历资料。
- 用户需要先建立主题无关的 canonical 简历资料，再决定通用版、定向版、照片版或无照片版。
- 用户需要离线、零 token 的 `validate`、`target`、`plan`、`render`、`batch`、`verify` 工作流。

## Inputs

- `source_facts`: 候选人提供的已核实资料、待核实资料、目标单位/岗位信息和照片情况。
- `templates/graduate-resume.md`: canonical Markdown/YAML 资料模板。
- `references/schema-and-review-contract.md`: 字段职责、稳定 ID、复核状态、一次追问和阻断规则。
- `references/phase-46-baseline.md`: Phase 46 骨架、夹具基线、CLI 边界和字体/依赖要求。
- `fixtures/`: 正常、缺照片、无照片、多目标和错误样例。
- `scripts/graduate-resume.sh`: 公开 CLI 入口；Phase 46 已实现 `validate`、`target`、`plan`、`verify`。

## Canonical Workflow

1. 收集候选人的个人资料、教育、技能、证书、项目、实训、经历、目标岗位和照片情况。
2. 对缺失且影响可信度的资料执行一次追问，不循环追问。
3. 生成或更新 `graduate-resume.md`，把结构化事实写入 YAML frontmatter。
4. 运行 `validate` 检查 schema、必填、稳定 ID、待确认事实、照片状态和 target 完整度。
5. 只有资料通过 `validate` 后，才进入后续 `plan`、`render`、`batch` 或 `verify`。

## One-Time Questions

- 缺 target 时：询问一次是否提供单位/岗位；用户明确不提供后，继续生成通用版。
- 缺照片时：询问一次是否提供本地照片；用户明确没有后，记录为无照片并继续。
- 缺核心事实时：只问缺失的真实资料，不询问主题配色、Typst 细节、字体或布局坐标。

照片默认策略：

- 默认期待提供照片。
- 若当前资料没有照片，先追问一次。
- 用户明确说没有后，写为 `photo.status: declined`，后续走无照片版。

## Finalized Markdown / CLI Entry

```bash
skills/graduate-resume/scripts/graduate-resume.sh validate \
  --input skills/graduate-resume/templates/graduate-resume.md

skills/graduate-resume/scripts/graduate-resume.sh target \
  --input skills/graduate-resume/templates/graduate-resume.md

skills/graduate-resume/scripts/graduate-resume.sh plan \
  --input skills/graduate-resume/templates/graduate-resume.md
```

Phase 46 已落地资料校验、target 摘要、基线 plan 和 fixture verify；`render` 与 `batch` 仍只冻结离线、零 token 边界，不在 canonical 主体里承诺已完成最终渲染。

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 整体安装并读取 `SKILL.md`、`references/`、`templates/`、`fixtures/`、`scripts/`；显式 fallback 是执行 `scripts/graduate-resume.sh`。允许 Bash 执行、读取输入，并写授权 workdir 或 delivery root。 |
| Claude Code | 整体安装到可发现 skill path；若 discovery 不可用，显式执行 `scripts/graduate-resume.sh`。授予 Bash、输入读取、workdir 或 delivery root 写入权限。 |
| Gemini CLI | 由 `GEMINI.md` 或项目上下文指向完整 skill folder；显式 fallback 是 `scripts/graduate-resume.sh`。sandbox/allowlist 必须允许 Bash、输入读取与目标输出根写入。 |
| OpenCode | 使用 native skill path 并保留全部支持文件；无法自动发现时显式执行 `scripts/graduate-resume.sh`。allowlist 必须覆盖 Bash、输入读取与目标输出根写入。 |
| OpenClaw | whole-folder 支持、frontmatter、support-file discovery 和路径行为均须 installation-time verified；始终保留 `scripts/graduate-resume.sh` 显式 fallback，并验证离线 CLI、输入读取与目标输出根写入权限。 |
| Hermes Agent | whole-folder 项目/全局加载、support-file discovery 和权限模型均须 installation-time verified；始终保留 `scripts/graduate-resume.sh` 显式 fallback，并验证离线 CLI、输入读取与目标输出根写入权限。 |

## Outputs

- `graduate-resume.md`: 候选人可审阅的 canonical 资料源文件。
- `validate` diagnostics: 仅用于说明为什么当前资料不能进入 final render。
- target brief summary / baseline plan: Phase 46 已提供 JSON 摘要输出。
- render artifacts: 后续 phase 交付，不在 Phase 46 承诺为完成态。

## Verification

- [x] `scripts/graduate-resume.sh --help` 暴露 `validate`、`target`、`plan`、`render`、`batch`、`verify`。
- [x] 模板可表达 candidate、education、skills、certificates、projects、training、experience、targets、photo、preferences。
- [x] fixture 至少覆盖：有照片、明确无照片、通用版、多目标、未知字段、重复 ID、待确认核心事实、照片待补。
- [x] canonical 主流程不包含 runtime 私有语法。
- [x] `validate`、`target`、`plan`、`render`、`batch`、`verify` 被定义为离线、零 token 边界。

## Safety

- 不要把 target 关键词、主题偏好或照片布局回写为基础事实。
- 不要把未确认、过期或推断出的资料当作 final render 事实。
- 不要在缺照片且用户尚未明确拒绝时默认为无照片。
- 不要把电话、邮箱、身份证、原始招聘 URL 写入输出 stem 或 history 路径。
- 不要把 Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw 或 Hermes Agent 的私有语法写入 canonical 主流程。
