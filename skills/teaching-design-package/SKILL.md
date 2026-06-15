---
name: "teaching-design-package"
description: "Use when creating one standalone teaching-design package from finalized unified Markdown into package-owned Typst/PDF outputs."
metadata:
  short-description: "教学设计整包统一 Markdown 渲染工作流"
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

# Teaching Design Package

## Objective

把已经审定的教学设计整包 Markdown 解析为 package-owned data model，并由本技能自己的渲染规则生成 unified Typst 与 PDF 状态。正常使用路径只需要安装 `teaching-design-package` 这一整个 skill folder，不要求额外安装同仓库的其他技能目录。

Phase 30 的边界是先建立独立包内路径：unified Markdown -> package-owned data model -> package-owned Typst/PDF rendering。完整教师交互文案与最终清洁 1+1+3 交付目录会在后续阶段继续收束。

## Use When

- 用户已经有 `teaching-design-package-full.md`，或有同一合同形状的课程教学资料 Markdown。
- 用户需要从一份统一 Markdown 派生课程元数据、授课进度、教学活动、资源、课时、日期、学期和输出状态。
- 用户需要验证 standalone 安装边界：只复制本 skill folder 后，仍能运行 example、model、render-package。
- 用户要生成整包 Typst，或在本地工具可用时尝试 PDF，并要求缺失工具时诚实记录非最终状态。

## Inputs

- `source_material`: 教师提供的课程说明、授课进度、教学活动、资源、评价要求和补充事实。
- `templates/teaching-design-package-full.md`: 统一 Markdown 示例，也是包内 parser 的基线合同。
- `references/format-and-orchestration.md`: 统一 Markdown、data model、渲染状态、standalone 边界与安全规则。
- `scripts/teaching-design-package.sh`: 包内脚本，只读取本 skill folder 与调用方传入的 Markdown/output path。

## Process

1. 先把源材料整理为一份可审阅 unified Markdown。Phase 30 脚本只消费 finalized Markdown，不负责代替教师互动整理材料。
2. 运行 `example` 生成包内示例，或使用课程自己的整包 Markdown。
3. 运行 `model` 检查 package-owned data model。模型会派生课程元数据、授课进度行、教学活动块、资源片段、总课时、日期范围、学年学期、复核标记和输出 readiness。
4. 运行 `render-package` 从同一个模型生成 `teaching-design-package.typ`，并把内部模型写到隐藏诊断目录。
5. 需要 PDF 时显式加 `--pdf`。如果本地缺少 Typst 或编译失败，脚本写入诚实状态，不回退到外部技能或旧渲染路径。
6. 旧的独立技能只作为仓库外部兼容入口继续存在；它们不是本技能正常路径、内部资源、验收基准或后续实现方向。

## Script Usage

```bash
scripts/teaching-design-package.sh example \
  --output teaching-design-package-full.md

scripts/teaching-design-package.sh model \
  --input teaching-design-package-full.md

scripts/teaching-design-package.sh render-package \
  --input teaching-design-package-full.md \
  --out-dir build/teaching-design-package

scripts/teaching-design-package.sh render-package \
  --pdf \
  --input teaching-design-package-full.md \
  --out-dir build/teaching-design-package

scripts/teaching-design-package.sh manifest \
  --input teaching-design-package-full.md \
  --out-dir build/teaching-design-package
```

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 读取本入口、reference、template 和 script；在 shell 中显式运行包内脚本；只把用户指定 Markdown 和输出目录传给脚本；PDF 成功必须由实际文件和状态 JSON 证明。 |
| Claude Code | 可把本 skill folder 安装到 `.claude/skills/teaching-design-package/`；frontmatter `description` 触发后按渐进披露读取 reference/template/script；不要补读仓库外部技能作为正常执行条件。 |
| Gemini CLI | 在 `GEMINI.md` 或项目上下文中指向本 `SKILL.md`；自动技能加载不可用时按 `Script Usage` 手动执行；交互确认用普通文本完成。 |
| OpenCode | 使用 OpenCode 可发现的 skill path；如果走 Claude-compatible fallback，保持 `references/`、`templates/`、`scripts/` 同步复制并验证当前选中的是本技能。 |
| OpenClaw | 作为 AgentSkills-compatible skill folder 使用；安装时验证 skill root、frontmatter、sandbox/allowlist、support files 和 shell 脚本权限；正常路径不要求同仓库其他技能目录存在。 |
| Hermes Agent | 使用 Hermes Agent 可发现的 `SKILL.md` skill folder；安装时验证 project/global 路径、reference/template/script 可读性、脚本执行权限和失败时人工 fallback；不要把外部兼容入口当包内依赖。 |

## Outputs

默认 Typst-only 成功路径会写出：

- `teaching-design-package-full.md`：复制到输出目录的 unified Markdown。
- `teaching-design-package.typ`：由 package-owned data model 生成的 unified Typst。
- `.teaching-design-package/model.json`：隐藏诊断模型。
- `teaching-design-package-status.json`：输出状态与 readiness。

显式 `--pdf` 时还会尝试：

- `teaching-design-package.pdf`
- `teaching-plan.pdf`
- `teaching-design.pdf`

Phase 30 可以诚实记录 PDF `not_run`、`missing_compiler_or_failed` 或 `passed`。完整 1+1+3 最终交付清洁化由后续阶段完成。

## Verification

- [ ] `Codex`、`Claude Code`、`Gemini CLI`、`OpenCode`、`OpenClaw`、`Hermes Agent` 均出现在 Runtime Adapter Notes。
- [ ] `scripts/teaching-design-package.sh example --output <file>` 生成 unified Markdown。
- [ ] `scripts/teaching-design-package.sh model --input <file>` 输出 package-owned data model。
- [ ] `scripts/teaching-design-package.sh render-package --input <file> --out-dir <dir>` 输出 unified Typst 与状态 JSON。
- [ ] standalone 验证只复制本 skill folder，并能运行 example 与 render-package。

## Safety

- 不要把外部兼容入口改造成本包内部依赖。
- 不要新增旧式内部目录或旧式拆分交接结构。
- 不要从 unified Markdown 一跳声称 PDF 最终通过；只有显式 `--pdf` 且实际文件存在时才记录 `passed`。
- 不要把脚本诊断文件混入教师默认交付说明；Phase 32 会继续收束清洁输出目录。
