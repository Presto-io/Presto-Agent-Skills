---
name: "teaching-design-package"
description: "Use when turning teacher source materials into one reviewable teaching-design-package Markdown, then validating/rendering the finalized Markdown with package-owned tools."
metadata:
  short-description: "教师源材料到统一教学资料 Markdown 的整包工作流"
  version: "0.3.0"
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

把教师提供的课程标准、授课计划、学习任务、教材资源、评价要求、学校格式要求和零散说明整理成一份教师可审阅、可编辑的统一 Markdown；教师确认这份 Markdown 后，再用本技能自己的脚本做严格验证、Typst/PDF 渲染和交付证据记录。

正常使用路径只需要安装 `teaching-design-package` 这一整个 skill folder。脚本层消费审定后的 Markdown，不替代教师沟通、内容组织或审阅编辑。

## Use When

- 教师给出多份源材料，需要整理为一份完整教学资料包。
- 教师已经有 `teaching-design-package-full.md`，或课程专属文件名，例如 `某某某课教学资料.md`，并希望作为后续渲染的人工可编辑事实源。
- 用户需要先确认课程事实、授课进度、教学活动、资源、评价方式、复核标记和学校格式要求，再生成整包 Typst/PDF。
- 用户需要验证 standalone 安装边界：只复制本 skill folder 后，仍能在审定 Markdown 上运行 package-owned validation/rendering。

## Inputs

- `source_materials`: 教师提供的课程说明、课程标准、教材信息、授课进度、活动设计、工作页、考核要求、校内模板要求、教师备注和已有 Markdown 片段。
- `templates/teaching-design-package-full.md`: 可参考的统一 Markdown 形状。不要把它当成必须复制的旧模板；按教师材料组织课程自己的完整 Markdown。
- `references/format-and-orchestration.md`: 源材料编排、教师可编辑 Markdown 契约、YAML/正文边界、复核标记、脚本边界与验证规则。
- `scripts/teaching-design-package.sh`: 包内脚本，只在 Markdown 定稿后读取调用方传入的 Markdown/output path。

## Teacher Workflow

1. **收集源材料**：接收课程标准、教材、任务清单、进度安排、活动过程、评价要求、学校格式约束和教师补充说明。先把可读文本内容作为事实来源；OCR 或任意二进制提取不作为本技能必需能力。
2. **抽取并归一化**：把多份材料映射到一个课程资料包，合并重复事实，保留可追溯的正文证据，不按源文件碎片继续组织。
3. **澄清/提问**：先从正文证据里找答案；只对缺失、冲突、不确定或依赖教师选择的事实提问。问题按课程身份、班级/教师、时间课时、学习任务、活动设计、资源评价、学校格式和复核标记分组。
4. **生成统一 Markdown**：产出一份完整的 `teaching-design-package-full.md`，或使用课程专属文件名如 `某某某课教学资料.md`。这份 Markdown 是教师可编辑的 source of truth。
5. **教师审阅/编辑**：暂停让教师审阅、改写、补充或保留复核标记。不要要求教师运行、排序或拼接其他独立技能；不要把脚本状态当成内容审阅。
6. **定稿 Markdown**：只有当教师确认内容可进入交付，且阻塞性复核标记已解决或明确保留为非最终状态时，才把 Markdown 视为 finalized Markdown。
7. **脚本验证/渲染**：对定稿 Markdown 运行包内脚本，生成 package-owned data model、unified Typst、PDF 状态和交付证据。脚本只做 finalized Markdown validation/rendering，不承担教师互动和内容组织 UX。

## Clarification Strategy

- **必问阻塞项**：课程名称、专业/班级、教师、教材、首个授课日、学习任务结构、课时来源、关键评价要求、学校强制格式等缺失时，必须先问清。
- **冲突项**：当多个来源给出不同课程名、日期、课时、任务顺序或评价口径时，简要说明冲突来源和差异，请教师确认采用哪一项。
- **可复核项**：能安全进入草稿但尚未确认的内容，写入正文复核标记，让教师在 Markdown 中直接改。不要为可延后偏好反复打断。
- **可选偏好**：封面称谓、局部措辞、资源补充、展示顺序等可作为集中问题询问，也可先生成可编辑草稿。
- **不要索要派生事实**：总课时、学年、学期、起止日期、输出配置、内部验证开关和诊断状态应从正文证据、脚本配置或后续验证派生，不要求教师手工维护 YAML 值。

## Finalized Markdown Validation And Delivery Commands

在教师审阅并确认 Markdown 可进入交付后，才运行以下命令：

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

如果课程使用专属文件名，把 `--input teaching-design-package-full.md` 换成对应的 `某某某课教学资料.md` 路径。

`render-package --pdf` 是最终交付命令。它只有在所有注册模块 PDF 都真实生成且非空，并且整包 PDF 由这些模块 PDF 按 registry 顺序合并成功后才返回成功；否则命令非零退出，并把 status、stderr log、model JSON、模块 Markdown/Typst、staging 文件和失败诊断保存在输出目录内的隐藏 `.teaching-design-package/` 下。

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 先读取本入口、reference 和 template，按教师源材料完成澄清、统一 Markdown、教师审阅/编辑；仅在 Markdown 定稿后运行包内脚本。PDF 成功必须由课程名前缀公开文件、隐藏 status JSON 和 registry-order merge 证据证明。 |
| Claude Code | 可把本 skill folder 安装到 `.claude/skills/teaching-design-package/`；frontmatter `description` 触发后渐进读取 reference/template/script；先执行教师 workflow，再执行 finalized Markdown validation/rendering。 |
| Gemini CLI | 在 `GEMINI.md` 或项目上下文中指向本 `SKILL.md`；自动技能加载不可用时用普通文本完成澄清和教师确认；脚本命令只作为定稿后的交付步骤。 |
| OpenCode | 使用 OpenCode 可发现的 skill path；保持 `references/`、`templates/`、`scripts/` 同步复制；先确认教师可编辑 Markdown，再运行脚本验证。 |
| OpenClaw | 作为 AgentSkills-compatible skill folder 使用；安装时复制整个 `teaching-design-package` folder，验证 frontmatter、support files、脚本权限、Typst/Python merge fallback、sandbox/allowlist 和隐藏 `.teaching-design-package/` 可写性；教师确认 Markdown 前不要触发渲染交付。 |
| Hermes Agent | 使用 Hermes Agent 可发现的 `SKILL.md` skill folder；验证 reference/template/script 可读性、执行权限、PDF merge 工具 fallback 和隐藏诊断目录可写性；遇到材料冲突时走文本澄清，定稿后再运行包内脚本。 |

## Outputs

教师审阅阶段的核心输出：

- `teaching-design-package-full.md` 或 `某某某课教学资料.md`：统一、完整、教师可编辑的 Markdown source of truth。

默认成功交付目录只包含课程名前缀 `1 + 1 + N` 公开文件。当前 N=2 时为四个文件：

- `课程名教学资料.md`：统一 Markdown 的公开副本，例如 `电气设备控制线路安装与调试教学资料.md`。
- `课程名教学资料.pdf`：由所有注册模块 PDF 按 module registry 顺序合并得到的整包 PDF。
- `课程名授课进度计划表.pdf`：`teaching-plan` 注册模块的正式 PDF。
- `课程名教学设计方案.pdf`：`teaching-design` 注册模块的正式 PDF。

隐藏诊断目录：

- `.teaching-design-package/model.json`：派生模型和调度证据。
- `.teaching-design-package/status.json`：输出状态、PDF readiness 和 final_ready。
- `.teaching-design-package/work/`：模块 Markdown、模块 Typst 和 debug-only unified Typst 等内部中间文件。
- `.teaching-design-package/staging/`：模块 PDF 与整包合并 PDF 的发布前 staging 产物。
- `.teaching-design-package/debug/`：stderr log、merge status、merge stderr 等调试证据。
- `.teaching-design-package/failure-diagnostics/`：失败时保留的诊断快照。

`.typ`、status、manifest、stderr log、model JSON、diagnostics JSON、calendar JSON、模块 Markdown/Typst、staging 文件、旧英文成功文件名和 failure diagnostics 不属于成功交付根目录的公开文件。

## Verification

- [ ] `SKILL.md` 的主流程从源材料、澄清/提问、统一 Markdown、教师审阅/编辑、定稿 Markdown 到脚本验证/渲染。
- [ ] `teaching-design-package-full.md` 和课程专属 `某某某课教学资料.md` 都被描述为教师可编辑 source of truth。
- [ ] `references/format-and-orchestration.md` 说明 teacher-editable Markdown、YAML/frontmatter 边界、正文/body 提取、派生事实、复核标记和 script boundary。
- [ ] `scripts/teaching-design-package.sh model --input <finalized-markdown>` 输出 package-owned data model。
- [ ] `scripts/teaching-design-package.sh render-package --pdf --input <finalized-markdown> --out-dir <dir>` 成功后，公开根目录只有 `课程名教学资料.md`、`课程名教学资料.pdf`、`课程名授课进度计划表.pdf`、`课程名教学设计方案.pdf`。
- [ ] `.teaching-design-package/model.json` 和 `.teaching-design-package/status.json` 存在，且公开根目录没有 `.typ`、status、manifest、stderr log、model JSON、diagnostics JSON、calendar JSON、模块中间产物、staging 文件或旧英文成功文件名。

## Safety

- 不要把脚本命令放在教师内容组织之前。
- 不要要求用户安装、运行、排序或拼接其他独立技能来完成本包。
- 不要把外部兼容入口改造成本包内部依赖、资源、验收基准或实现方向。
- 不要把总课时、学年、学期、起止日期、输出 readiness、诊断状态等派生事实放进教师必须维护的 YAML。
- 不要从 unified Markdown 一跳声称 PDF 最终通过；`课程名教学资料.pdf` 必须由注册模块 PDF 真实合并得到。
- 不要把脚本诊断文件混入教师默认交付说明；成功交付根目录只允许课程名前缀 `1 + 1 + N` 公开文件。
