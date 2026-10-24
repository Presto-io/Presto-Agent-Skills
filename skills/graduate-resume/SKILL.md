---
name: "graduate-resume"
description: "Use when collecting, reviewing, validating, and preparing a verified Chinese graduate resume source package for offline generic or targeted resume generation with optional photo and deterministic Markdown/Typst/PDF outputs."
metadata:
  short-description: "毕业生简历资料契约与离线生成工作流"
  version: "0.3.2"
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
- `references/targeted-render-delivery-contract.md`: 目标投影、四态条件、三主题最终 Markdown、自包含照片与 patch/authority 干净投递契约。
- `references/phase-46-baseline.md`: Phase 46 骨架、夹具基线、CLI 边界和字体/依赖要求。
- `references/repository-publication.md`: 技能提交前的学生资料隔离、合成夹具与暂存区审查边界。
- `fixtures/`: 有照片、无照片、通用版、多目标和错误样例。
- `scripts/graduate-resume.sh`: 离线公开 CLI 入口。

## Canonical Workflow

资料整理和文案优化先阅读 `references/job-focused-writing.md`，以 HR 能快速识别的岗位匹配证据为目标：明确求职方向，突出相关技术、本人行动与真实成果；教育经历分开呈现学业表现和相关课程，相关课程优先，优秀成绩有据才强调。原始事实与熟练程度必须保留。离线渲染器按已确认岗位/招聘要求或通用求职方向自动排序课程并对正文匹配词组加粗，每段最多 3 处；测量和正式渲染共用强调结果，不能仅在导出的 PDF 中临时加粗。

1. 收集候选人的个人资料、教育、技能、证书、项目、实训、经历、目标岗位和照片情况。
2. 对缺失且影响可信度的资料执行一次追问，不循环追问。
3. 生成或更新 `graduate-resume.md`：把首页信息栏所需的 `profile`、可选本地 `photo` 路径和派生偏好写入 YAML frontmatter；把教育、技能、证书、项目、实训、经历和目标写入 Markdown 正文。
4. 运行 `validate` 检查 schema、必填、稳定 ID、待确认事实、照片状态和 target 完整度。
5. 资料通过 `validate` 后，使用 `render --generic` 或 `render --target <stable-id>` 预检单份版本；使用 `batch` 预检 generic 与全部 confirmed targets。两个命令都固定生成保守稳妥、现代简洁、个性设计三个主题。
6. 检查预检中的版本矩阵、逐条件四态、gap allow、完整 stems 和 `added/updated/unchanged/removed`。没有确认时不改变 current/history；确认无误后用完全相同参数追加 `--confirm`。
7. 逐页查看三种主题的 PDF 栅格预览，检查左右栏顶端、窄栏换行、联系方式、模块间距、裁切和续页。单页与双页都检查逐栏铺满，不能只检查“放得下”。布局计划冻结模块分配、栏宽、明细间距与逐栏弹性间隙；逐页 `fill_satisfied` 为 false 时说明留白原因，不能声称满足铺满。正常内容优先单页；自动双页必须两页均达标，强制双页内容不足时显示警告。联系方式从 `profile.contact` 展示，不要重复写进摘要。
8. 失败时按稳定错误码修正事实、覆盖冲突、gap、照片、字体、命名碰撞或投递根异常，再重新预检。不要手工发布 partial triple 或绕过 `.work`/history 审计。
9. 使用 `verify --workdir <临时证据目录>` 运行完整技能验收。其发布、跨运行环境和人工 UAT 证据缺失应如实说明，不能替代本次产物的 PDF 页数、内容与视觉检查。排版回归入口见 `references/targeted-render-delivery-contract.md`。

## One-Time Questions

- 缺 target 时：询问一次是否提供单位/岗位；用户明确不提供后，继续生成通用版。
- 照片可选：询问一次是否提供本地照片；用户没有照片或选择无照片时省略 `photo` 字段并继续。
- 缺核心事实时：只问缺失的真实资料，不询问主题配色、Typst 细节、字体或布局坐标。

照片默认策略：`photo` 存在时必须是学生明确提供的本地路径；字段不存在即走无照片版。

## Finalized Markdown / CLI Entry

```bash
skills/graduate-resume/scripts/graduate-resume.sh validate \
  --input skills/graduate-resume/templates/graduate-resume.md

skills/graduate-resume/scripts/graduate-resume.sh target \
  --input skills/graduate-resume/templates/graduate-resume.md

skills/graduate-resume/scripts/graduate-resume.sh plan \
  --input skills/graduate-resume/templates/graduate-resume.md \
  --theme <conservative|modern|expressive>

skills/graduate-resume/scripts/graduate-resume.sh render \
  --input graduate-resume.md \
  --generic \
  --delivery-root delivery

skills/graduate-resume/scripts/graduate-resume.sh render \
  --input graduate-resume.md \
  --target target-grid-001 \
  --not-applicable target-grid-001 condition-0123456789abcdefabcd "招聘方确认本批次不适用" \
  --delivery-root delivery

skills/graduate-resume/scripts/graduate-resume.sh batch \
  --input graduate-resume.md \
  --allow-gap-target target-grid-001 \
  --delivery-root delivery

skills/graduate-resume/scripts/graduate-resume.sh verify \
  --workdir <临时证据目录>
```

`render` 在 `--generic` 与 `--target` 中二选一，固定采用 patch 语义；`batch` 默认展开 generic + all confirmed targets，固定采用 authority 语义。`--retain`、`--exclude`、`--pin`、`--allow-gap-target` 可重复；不适用覆盖只有 `--not-applicable <target-id> <condition-id> <reason>` 这一种公开三参数语法。先运行上述命令查看预检，再追加 `--confirm` 发布。

## Runtime Adapter Notes

有照片的信息栏必须在整组文字与照片布局底部保留至少 3 mm 的实体内边距，使分割线与正文侧栏底色分离。不得依赖照片比文字高时自然产生的留白，或会在布局边界折叠的块间距；测量与正式渲染必须使用同一结构，并检查文字高于照片、照片高于文字两种情况。

现代简洁、个性设计是强制左右双栏主题，每一页左右两栏都必须有真实正文，禁止回落单栏，也不能用空白栏冒充双栏。现代简洁主题的浅色侧栏允许 60、70、80、88 mm 候选宽度，逐栏测量后选择完整且铺满的双栏组合；资料没有证书或独立项目时，也应评估“技能＋实训”侧栏和其他合理的模块分配。优先保持模块完整；长模块必要时可按完整条目跨栏，并在两栏分别重复模块标题，不拆开单条经历。无法保持指定结构、完整内容与可读边界时返回 `LAYOUT_UNSATISFIABLE`，不得发布结构降级产物。单页/双页铺满约束继续执行；保守稳妥保持单栏。

来源明确列出出生日期、籍贯、民族和政治面貌但未列性别时，可使用 `出生日期：…；籍贯：…；民族：…；政治面貌：…` 的概述格式，渲染器将其拆为独立信息栏字段；不得根据照片推断性别。其他未匹配的概述保持完整。

头像规范化时以透明像素补齐隐形尺寸槽位，禁止添加白色底框，保持 contain 等比显示。正文说明段落（概述、课程、技能、资格说明、项目/实训/经历说明及备注）整体向内缩进一字符，首行与续行保持同一起点；标题、条目名称、日期角色等元信息与信息栏保持各自对齐。成果项目符号使用一字符宽的独立标记列，圆点在该列与第一行字符高度内居中，正文及续行从一字符处开始，与普通说明段落对齐；禁止用空格凑缩进。独立说明段落统一以中文句号结束，已有问号或叹号保留，不将分号、逗号留在段尾；标题、日期、角色和信息栏不加句号。仅在展示层规范标点，不修改原始事实。排版变化后重新测量并验证逐页逐栏铺满。

信息栏采用对齐的两列网格，列间距 8 mm、行间距 2.5 mm，每个单元格为 15 mm 固定宽度标签与字段值，标签和内容之间留白，不加冒号、分隔点、逗号或句号。电话与邮箱排首行；标准四段个人资料严格匹配后拆为性别、出生日期、民族、籍贯，随后展示现居地等其余联系方式。标签用主题适配的次要颜色，字段值保持清晰。仅移除该标准句式的语法标点和“出生”“籍贯”等已由标签表达的字词；原始资料保持不变，其他自然语言概述保持完整，不猜测字段。三主题及有照、无照版本均用实际布局重新测量，检查邮箱换行、标签列对齐、逐项只出现一次和单页/双页铺满。

模块标题统一使用本地 Lucide 0.468.0 线性 SVG：教育 graduation-cap、技能 wrench、证书 badge-check、项目 folder-kanban、实训 flask-conical、经历 briefcase-business，预留基本信息 user-round 与概述 file-text。原始 SVG 与 ISC 许可位于 `assets/icons/lucide/`，来源为 https://github.com/lucide-icons/lucide/tree/0.468.0/icons 。生产模板内嵌 SVG 字符串以保持交付 Typst 自包含；更新图形时同步原始 SVG 与模板映射。

图标按主题 accent 着色，尺寸 4.2 mm，作为标题行内字符占位，使用 box 的 14% 基线对齐，图标与标题文字间距 1 mm。图标从原标题起点开始，标题文字自然向右移动 5.2 mm；不使用悬挂、负缩进、绝对定位或逐图标偏移。浅色侧栏保持原始底色边界。正文横向起点、栏宽和段落间距保持不变，标题行高度由行内排版自然计算并重新检查分页。基本信息头部没有模块标题时不额外添加图标。视觉检查须放大检查图标与文字的行内对齐、底色边界及裁切；模块图标可见图形中心与标题字框中心的纵向偏差不超过 0.5 pt。单页与双页铺满检查照常执行。

Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw 与 Hermes Agent 都应保留完整 skill folder，并通过同一个 `scripts/graduate-resume.sh` 执行上述 runtime-neutral 工作流。运行环境只需允许离线 shell、读取用户授权的输入/本地照片，以及写入用户授权的 workdir 和 delivery root。跨 runtime 的安装与发现验收属于 Phase 49，本技能不在 Phase 48 声称已经完成。

## Outputs

- `graduate-resume.md`: 候选人可审阅的 canonical 资料源文件。YAML 只保存信息栏和派生偏好；正文按语义模块保存其余事实，正文顺序不是事实语义。
- `validate` diagnostics: 仅用于说明为什么当前资料不能进入 final render。
- target brief summary / frozen plan: 输出不含候选人事实、照片路径或 EXIF 的 JSON 摘要。
- layout evidence: `verify` 仅在调用方临时 workdir 中生成受控 Typst/PDF/PNG 样张证据。
- render/batch preflight: 只显示有界版本矩阵、四态、digest、stems 和 delta，不显示完整理由、联系方式、照片路径或绝对路径。
- current: 平铺的正式 Markdown/Typst/PDF triples；不包含 manifest sidecar、完整 evidence、preview、照片中间件或日志。
- history: 只归档 updated/removed 的旧完整 triples；精确 no-op 不创建 history、不改变 inode/mtime。

## Verification

- [x] `scripts/graduate-resume.sh --help` 暴露 `validate`、`target`、`plan`、`render`、`batch`、`verify`。
- [x] 模板可表达 candidate、education、skills、certificates、projects、training、experience、targets、photo、preferences。
- [x] fixture 至少覆盖：有照片、无照片、通用版、多目标、未知字段、重复 ID、待确认核心事实、非法照片路径。
- [x] canonical 主流程不包含 runtime 私有语法。
- [x] `validate`、`target`、`plan`、`render`、`batch`、`verify` 被定义为离线、零 token 边界。
- [x] `plan --theme <conservative|modern|expressive>` 可冻结主题、页数和照片模式；每个主题均进入实际 Typst 布局，`verify` 对固定有照/无照、短内容、临界和压力样张逐页检查 A4、页数、锚点与条目归属。
- [x] `render` 以 patch 发布一个 generic/target 三主题矩阵并保留其他 current；`batch` 以 authority 发布 generic + all confirmed targets，并在确认前显示 removals。
- [x] gap allow 逐 target 生效；unknown 只警告；`--not-applicable TARGET_ID CONDITION_ID "REASON"` 是唯一公开覆盖入口。
- [x] 任一候选或事务失败不改变 current/history；相同输入为 true no-op。
- [x] 不可满足的强制页数经公开 shell CLI 以非零退出和稳定 JSON `LAYOUT_UNSATISFIABLE` 失败，不输出 traceback、部分 Typst、PDF 或 PNG。
- [x] 受控编译锁定 Typst 0.15.0、skill-local 字体和 `--ignore-system-fonts`；照片槽位不超过 35 mm x 49 mm，默认 contain 等比、禁止拉伸，只有主题显式许可时才可受控裁切。

## Safety

- 严禁将任何真实学生的简历源资料、联系方式、照片、预览、Markdown/Typst/PDF 成品或含个人信息的日志提交到技能仓库。真实资料和制作 workdir 必须位于仓库外；仓库 fixtures 只能使用完全虚构资料，照片测试仅使用无身份信息的合成像素。维护或提交技能前阅读 `references/repository-publication.md`。
- 不要把 target 关键词、主题偏好或照片布局回写为基础事实。
- 不要把未确认、过期或推断出的资料当作 final render 事实。
- 不要为照片生成、猜测或写入远程 URL；无照片时省略 `photo` 字段。
- 不要把主题、页数或照片布局回写为 `graduate-resume/v2` 的基础事实；照片必须是显式本地文件，且无照片输出不得保留图像、路径、EXIF 或照片装饰。
- 不要把电话、邮箱、身份证、原始招聘 URL 写入输出 stem 或 history 路径。
- 不要把完整 condition reason/evidence、preview、normalized photo 或 manifest sidecar 放入 delivery root。
- 不要在未检查权威目标矩阵和 removals 时追加 `--confirm`。
- 不要把 Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw 或 Hermes Agent 的私有语法写入 canonical 主流程。
