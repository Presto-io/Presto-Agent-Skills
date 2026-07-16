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

`render-package --pdf` 是最终交付命令。它先在交付根的 `.work/<run-id>/` 内生成 model、模块 Markdown/Typst、模块 PDF、merge plan/status 和完整 public candidate；所有 registry/order、PDF header、non-empty、merge 和 final-ready gate 通过后，才由 `public_delivery.expected_public_filenames` 驱动的 publisher 一次发布 dynamic `1 + 1 + N`。失败只返回有界诊断并清理本次 owned run，旧 current、history 和 `sources/` 保持不变。

`model --out-dir`、`manifest --out-dir`、不带 `--pdf` 的 `render-package`、`plan-split` 和 `render-split` 是诊断/中间命令；其 `--out-dir` 是调用方显式 diagnostic workdir，不是成功交付根，也不产生 current 版本。

## Runtime Adapter Notes

| Runtime | Notes |
|---------|-------|
| Codex | 复制并读取整个 skill folder；自动发现不可用时显式执行 `scripts/teaching-design-package.sh`。允许 Bash/Node/Typst 以及 `pdfunite`、`qpdf` 或 Python PyMuPDF fallback，授予 template/reference/input 读权限和 delivery root/`.work` 写权限，并把这些命令加入 sandbox/allowlist。 |
| Claude Code | 安装整个 folder 到可发现 skill path；自动加载失败时显式 shell fallback。允许 Bash/Node/Typst/PDF merge，授予 finalized Markdown 读取与 delivery root、history、`.work` 写入权限；禁止把 model/status/debug/merge evidence 当作 current。 |
| Gemini CLI | 在 `GEMINI.md` 或项目上下文指向整个 folder；不能自动发现 support files 时显式调用脚本。sandbox 必须允许 Bash/Node/Typst/PDF merge、读取 reference/template/input，并写授权 delivery root 与 owned `.work`。 |
| OpenCode | 保持 `references/`、`templates/`、`scripts/` 整体安装；发现失败时使用显式 shell fallback。allowlist 覆盖 Bash/Node/Typst/PDF merge 和授权根读写，unknown/legacy/ambiguous root 仍失败关闭。 |
| OpenClaw | 仅声明 installation-time verified：安装时验证 whole-folder discovery、support-file 可读、脚本可执行、Bash/Node/Typst/PDF merge 可用、sandbox/allowlist 以及 delivery root/`.work` 写权限；验证失败时只使用显式脚本 fallback。 |
| Hermes Agent | 仅声明 installation-time verified：核对实际 local/global skill path、whole-folder support discovery、execute/read/write 权限、Bash/Node/Typst/PDF merge 和 delivery root/`.work` allowlist；自动发现不确定时显式调用脚本。 |

## Outputs

教师审阅阶段的核心输出：

- `teaching-design-package-full.md` 或 `某某某课教学资料.md`：统一、完整、教师可编辑的 Markdown source of truth。

默认成功交付目录只包含课程名前缀 `1 + 1 + N` 公开文件。当前 N=2 时为四个文件：

- `课程名教学资料.md`：统一 Markdown 的公开副本，例如 `电气设备控制线路安装与调试教学资料.md`。
- `课程名教学资料.pdf`：由所有注册模块 PDF 按 module registry 顺序合并得到的整包 PDF。
- `课程名授课进度计划表.pdf`：`teaching-plan` 注册模块的正式 PDF。
- `课程名教学设计方案.pdf`：`teaching-design` 注册模块的正式 PDF。

交付根按需允许 `sources/`、`assets/`、`history/`、`.work/`。当前实现不自动修改 `sources/`，也不自动治理 legacy hidden、`media/` 或 unknown 用户文件。`.work/<run-id>/candidate/` 只保存完整 public candidate，`evidence/` 保存 model/status/debug/module/merge 证据，publisher 按需创建 `rollback/`；成功、no-op 和 handled failure 后清理本次 run 与空 `.work/`。

`expected_public_filenames` 是唯一 dynamic mutation authority。相同 prefix 或 course-name 变化都按 exact path-set+bytes 比较：identical 不创建 history、不触碰 current；changed 把唯一完整旧 `1+1+N` group 放入下一个 `history/<max+1>/` 后发布新组。多个旧 prefix、partial group、unknown、legacy hidden、symlink 或 traversal 均在 mutation 前失败关闭。

`.typ`、status、manifest、stderr log、model JSON、diagnostics JSON、calendar JSON、模块 Markdown/Typst、merge plan/status、staging 文件、旧英文成功文件名和 failure diagnostics 都不是成功 current。

## Verification

- [ ] `SKILL.md` 的主流程从源材料、澄清/提问、统一 Markdown、教师审阅/编辑、定稿 Markdown 到脚本验证/渲染。
- [ ] `teaching-design-package-full.md` 和课程专属 `某某某课教学资料.md` 都被描述为教师可编辑 source of truth。
- [ ] `references/format-and-orchestration.md` 说明 teacher-editable Markdown、YAML/frontmatter 边界、正文/body 提取、派生事实、复核标记和 script boundary。
- [ ] `scripts/teaching-design-package.sh model --input <finalized-markdown>` 输出 package-owned data model。
- [ ] `scripts/teaching-design-package.sh render-package --pdf --input <finalized-markdown> --out-dir <dir>` 成功后，公开根目录只有 `课程名教学资料.md`、`课程名教学资料.pdf`、`课程名授课进度计划表.pdf`、`课程名教学设计方案.pdf`。
- [ ] 成功、identical 与 handled failure 后不保留 legacy `.teaching-design-package/` 或本次 `.work/<run-id>`；公开根没有 `.typ`、status、manifest、stderr log、model JSON、diagnostics JSON、calendar JSON、模块/merge 中间产物或旧英文成功文件名。
- [ ] changed 发布把完整旧 dynamic group 放入同一 next history；已有 `001/003` 时 next 为 `004`，course prefix 多组或 partial group 非零失败且零 mutation。

## Safety

- 不要把脚本命令放在教师内容组织之前。
- 不要要求用户安装、运行、排序或拼接其他独立技能来完成本包。
- 不要把外部兼容入口改造成本包内部依赖、资源、验收基准或实现方向。
- 不要把总课时、学年、学期、起止日期、输出 readiness、诊断状态等派生事实放进教师必须维护的 YAML。
- 不要从 unified Markdown 一跳声称 PDF 最终通过；`课程名教学资料.pdf` 必须由注册模块 PDF 真实合并得到。
- 不要把脚本诊断文件混入教师默认交付说明；成功交付根目录只允许课程名前缀 `1 + 1 + N` 公开文件。
- 不要在 candidate 完整验证前删除、覆盖、移动 current，也不要用 glob、find-delete、broad cleanup 或逐文件 final copy 绕过 publisher。
- 不要宣称 SIGKILL、断电或多文件跨路径硬原子；保证范围是 candidate isolation、逐路径 replace 与 handled error/INT/TERM rollback。
