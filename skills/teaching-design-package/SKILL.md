---
name: "teaching-design-package"
description: "Use when creating an integrated teaching-design package that composes teaching-plan and practical lesson-plan materials before Typst/PDF output."
metadata:
  short-description: "教学设计整包 Markdown 编排工作流"
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

# Teaching Design Package

## Objective

把课程教学设计材料归一化为持久、可复核的 `teaching-design-package-full.md` Markdown intermediate，再把授课计划部分交给 `jiaoan-jihua` 契约、把实操教案部分交给 `jiaoan-shicao` 契约，并记录拆分 Typst/PDF 输出状态。

## Use When

- 用户需要一个整包教学设计，而不是单独的授课进度计划或单独的实操教案。
- 用户要求同时整理授课计划、实操教案、排课证据、输出清单或教师复核标记。
- 用户给出的源材料需要先形成可审阅 Markdown，再计划生成 `teaching-plan.typ`、`lesson-plans.typ` 或对应 PDF 状态。

## Inputs

- `source_material`: 课程元数据、教学任务、实操教案片段、排课依据、已有 Markdown 或教师补充说明。
- `templates/teaching-design-package-full.md`: 整包级 Markdown checkpoint。任何 Typst/PDF 生成前都先产出并复核它。
- `references/format-and-orchestration.md`: TDP-05 到 TDP-09 的长规则、字段、模块交接、输出状态和 Phase 24 边界。
- `references/scheduling-contract.md`: 共享排课合同；整包技能消费此合同，不把 `jiaoan-jihua.sh` 的旧解析器暴露为整包 API。
- `skills/jiaoan-jihua/`: 授课计划模块，继续保持 standalone skill。
- `skills/jiaoan-shicao/`: 实操教案模块，继续保持 standalone skill。

## Process

1. 按 `docs/markdown-normalization-contract.md` 把源材料整理为 `templates/teaching-design-package-full.md` 形状。
2. 在整包 Markdown 中保留课程元数据、调度输入、`## 调度证据`、`## 授课计划`、`## 实操教案`、`## 输出清单` 和 `## 复核标记`。
3. 按 `references/scheduling-contract.md` 记录 source-order 调度证据，保留 `task:...` 或 `lesson:...` 指针。
4. 为 `jiaoan-jihua` 生成或抽取 `jiaoan-jihua-full.md` 模块 intermediate，为 `jiaoan-shicao` 生成或抽取 `jiaoan-shicao-full.md` 模块 intermediate。
5. 使用 `scripts/teaching-design-package.sh plan-split` 或 `render-split` 规划/生成拆分输出，并在 manifest 中诚实记录 Typst 与 PDF 状态。
6. 若存在未解决 `## 复核标记`，不得把最终整包标记为 ready；缺失、冲突或不确定内容必须留在 Markdown 与 manifest 中。

## Script Usage

```bash
skills/teaching-design-package/scripts/teaching-design-package.sh example \
  --output teaching-design-package-full.md

skills/teaching-design-package/scripts/teaching-design-package.sh plan-split \
  --input teaching-design-package-full.md \
  --out-dir build/teaching-design-package

skills/teaching-design-package/scripts/teaching-design-package.sh render-split \
  --input teaching-design-package-full.md \
  --out-dir build/teaching-design-package

skills/teaching-design-package/scripts/teaching-design-package.sh manifest \
  --input teaching-design-package-full.md \
  --out-dir build/teaching-design-package
```

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 读取本入口、`references/format-and-orchestration.md`、模板和共享 `references/scheduling-contract.md`；用 shell 显式调用脚本；写文件前确认目标目录；PDF 编译必须单独验证，不能把 Typst 生成当成 PDF 成功。 |
| Claude Code | 可把同一 skill folder 安装到 `.claude/skills/teaching-design-package/`；frontmatter 的 `description` 是触发入口；按渐进披露读取 reference/template/script，脚本执行需检查 allowlist 和路径。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向本 `SKILL.md`；若技能不能自动加载，按 `Script Usage` 手动执行；用户问询和子代理能力缺失时使用普通文本确认。 |
| OpenCode | 使用可加载 `SKILL.md` 的 OpenCode skill 路径；若走 Claude-compatible fallback，保持 `references/`、`templates/`、`scripts/` 同步，并验证运行时实际选中本技能。 |
| OpenClaw | 作为 AgentSkills-compatible skill folder 使用；安装时验证 conservative frontmatter、skill root、sandbox/allowlist、`references/`、`templates/`、`scripts/`、校历/排课支持资源和 shell 脚本执行权限。 |
| Hermes Agent | 使用 Hermes Agent 可发现的 `SKILL.md` skill folder；安装时验证项目级/全局路径、reference/template/script 发现、shell 脚本执行权限、calendar/support resources 可读性和未验证行为的人工 fallback。 |

## Outputs

- `teaching-design-package-full.md` 结构的整包 Markdown intermediate。
- 模块交接文件：`jiaoan-jihua-full.md` 和 `jiaoan-shicao-full.md`。
- 拆分 Typst 输出状态：`teaching-plan.typ` 与 `lesson-plans.typ`。
- Manifest/status 字段：`teaching_plan_typ`、`lesson_plans_typ`、`teaching_plan_pdf`、`lesson_plans_pdf`、`review_markers`、`final_ready`。

## Verification

- [ ] `SKILL.md` 保持 portable canonical body，runtime-specific 行为只在 adapter notes 中。
- [ ] `Codex`、`Claude Code`、`Gemini CLI`、`OpenCode`、`OpenClaw`、`Hermes Agent` 均出现在 Runtime Adapter Notes。
- [ ] `references/format-and-orchestration.md` 覆盖 TDP-05、TDP-06、TDP-07、TDP-08 和 TDP-09。
- [ ] `scripts/teaching-design-package.sh example --output <file>` 输出包含 `## 复核标记` 的整包 Markdown。
- [ ] `scripts/teaching-design-package.sh plan-split --input <file> --out-dir <dir>` 输出两个模块 intermediate。

## Success Criteria

- TDP-05 到 TDP-09 的最小整包编排入口可被 agent 读取、执行和验证。
- `jiaoan-jihua` 与 `jiaoan-shicao` 仍是 standalone skills；本技能只组合、引用或调用它们。
- 所有最终输出声明都经过 Markdown checkpoint 和 manifest/status 证据。
- 默认合并 `teaching-design-package.pdf`、`end-of-term-package.pdf` 和可选期末材料模块保留到 Phase 24。

## Safety

- 不要删除、重命名、替换或改变 `skills/jiaoan-jihua` 与 `skills/jiaoan-shicao` 的公开命令。
- 不要一跳从源材料生成 PDF；必须先落地可审阅 Markdown intermediate。
- 不要静默丢弃缺失、冲突、耗尽或不确定的排课/内容输入；必须就近标记并汇总到 `## 复核标记`。
- 不要把 PDF 状态标记为 `passed`，除非显式 PDF 编译命令已运行且输出文件存在。
- 不要在 Phase 23 实现默认合并包或可选期末材料包；这些属于 Phase 24。
