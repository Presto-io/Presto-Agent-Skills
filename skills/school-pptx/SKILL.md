---
name: "school-pptx"
description: "Use when drafting, reviewing, validating, or rendering school or course presentation content from finalized Markdown logical slides into an editable, controlled-template PowerPoint deck."
metadata:
  short-description: "学校课程 Markdown 逻辑页到可编辑 PPTX 工作流"
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

# School PPTX

## Objective and Use When

把学校汇报、课程展示、培训课件或项目答辩从需求澄清、材料筛选、页面策划推进到教师可审阅的 Markdown logical slides，再用受控 `standard-school` 模板生成原生可编辑 PPTX。Markdown 是内容 source of truth；模板和 renderer 拥有视觉、对象与分页规则。除既有布局外，作者可用受限语义选择 `hero-evidence`、`annotated-image`、`process-overlay` 与 `kpi-evidence`；它们分别服务主证据、设备标注、流程闭环和定量证据，不接受作者坐标或样式覆盖。

当用户要新建、补全、审阅、验证或渲染学校/课程 PowerPoint，且需要固定学校模板、可编辑对象和可复验交付时使用本技能。需要离线 HTML 演示时应改用 `school-presentation`。

## Required Inputs and References

- 学校或课程标题，以及需要出现在封面的 subtitle、学期/日期、作者等 metadata。
- 唯一受控主题 `standard-school`。
- 已定稿或待审阅的 Markdown；公开写作规则见 `references/markdown-contract.md`，完整 fixture 覆盖既有 11 个受控布局与四种新增构图。
- 所有 Markdown 引用的本地图片/图标路径。
- 模板所有权与人工编辑规则见 `references/template-contract.md` 和 `references/template-editing.md`。
- 可编辑对象、logical→physical 分页与 clean output 见 `references/renderer-and-pagination.md`。
- 自动验证、依赖、证据和排障见 `references/verification-contract.md`。
- PowerPoint/WPS 人工检查见 `references/visual-uat.md`。

## 课堂课件的表述与逻辑

本节适用于面向学生的上课、实训和复习课件；教师培训、教学设计汇报等以教师为受众的材料按实际用途撰写。

- 可见标题和正文直接呈现知识、原理、案例、问题或学习任务。不要把“此处适合教学/复习”“教师可重点讲解”“教学重点是”“学生必须掌握”等备课评价、制作建议或教学安排写上投影页面；确有必要的教师提示放入 `::: notes`，与课堂讲述稿分开。
- 合理保留“想一想”“比较”“练一练”“课后任务”等学生可执行的活动，以及操作授权、教师监护和安全条件；不要因删除备课话语而删掉实际任务或安全要求。
- 先确定本节要回答的核心问题，再按受众的已有知识组织概念、结构/原理、应用、检查和练习。页面之间建立明确关系，解释新术语后再使用；避免突然援引未交代的其他课程、柜型或内部制作背景。顺序按内容需要调整，不强制套用固定模板。
- 标题说明本页具体问题或结论，正文提供对应解释、依据或步骤；不要用“正确口径”“底层逻辑”“必须掌握的动作”等空泛表述代替知识点。课堂口语应自然准确，避免连续口号和机械串词。
- 比较页使用一致维度并解释差异的实际影响；操作流程交代前提、步骤和异常处理；练习提出可回答的问题或可完成的任务。不要为凑 KPI 卡片把学习要求包装成无依据的量化成果。
- 渲染前逐页审阅可见文本并连读整套讲述：本页承接什么、回答什么、如何引出下一页；发现跳步、重复、标题正文不符或教师视角旁白时先改源稿，再生成 PPTX。语义审阅与结构验证分别完成，不能以自动验证通过代替课堂逻辑审阅。

改写示例：“GCS教学重点是抽屉和联锁”→“GCS抽屉有哪些工作位置？联锁如何限制误操作？”；“此页适合复习两类柜型”→“比较GCS与GGD的安装结构及检修方式”。改写后的问题须在正文中回答或给出明确讨论任务。

## Layout Selection

默认避免使用 `gallery` 图册布局。先确定讲述模块与页面关系，再选择布局；双栏不是默认容器，只有完整并列模块或同维度比较适合 `two-column`，顺序讲述优先 `title-content`。只有一张确有教学价值的图片时优先选用 `image-text`。仅当用户明确要求图册展示，且多张图片本身构成需要并列比较的完整内容时，才使用 `gallery`。

### 双栏的语义分页

所有新建、改写、直接生成和重新渲染课件均执行 [语义分页规则](references/semantic-pagination.md)，不能只在用户指出问题后补救。讲述完整性与比较关系优先于节省页数和填满左右框。

- 先判断左右栏关系。独立模块只有在双方均能完整呈现在同一物理页时才用双栏；放不下就改为各有明确标题的顺序逻辑页，先讲完一个模块再进入另一个。
- 真正的比较保持对比结构，按统一维度组织左右内容，或使用对比表。超长时在源稿中显式拆成多张逻辑页，每页仍包含双方在同一组维度上的完整内容，标题注明比较维度。禁止按对象分开而丢失对比特点，也禁止一侧续页仅剩一句、另一侧为空。
- 小标题及其解释、步骤或完整列表作为一个讲述模块。先精简重复表述，保留关键事实、安全前提和结论；仍放不下就按子主题拆页。不得突破模板字号、坐标和样式约束，或缩到难读的字号。
- 首轮 render 后检查实际物理页正文与 logical→physical mapping，尤其检查同标题的连续页。发现模块交错、孤立的最后一两条、比较两侧不同步时，返回源稿调整逻辑页后重渲染。每页须有完整讲述目标，不能仅凭结构验证通过就交付。
- 当前 renderer 会分别拆分左右栏再按页码拼接，并不理解比较关系和讲述顺序。完整模块与比较维度须在源稿中明确划分，不声称已有语义识别或弹性框高功能。

## Collaborative Project Workflow

### 1. 先建立项目边界，再处理材料

- 新建课件时，先在用户指定工作根目录创建 `YYYYMMDD项目名称/` 子目录；所有本次材料、源稿和交付均在该目录内处理。
- 用户可能将未整理的文件一并放入目录。先聊天确认培训对象、时长、任务目标、可讲深度、组织/保密边界、交付形式与可用外部资源；不要刚收到文件就直接生成 PPT。
- 对有明确受众差异的课程（例如非本专业新员工），先把难度、术语密度和案例深度降到受众能理解的水平；不能把专业资料原样堆到页面上。

### 2. 做素材台账，不删除用户材料

- 逐项阅读可读材料，并为每项标注：`直接事实依据`、`知识参考`、`可用图片/图表`、`视频/课堂活动`、`仅作制作策略参考` 或 `本次不用`，同时写明原因和可落入的页面。
- 未采用不等于无价值：所有原始材料必须保留原位，绝不因为“本次不用”而移动、重命名或删除。不能把参考别家单位的资料误写成当前单位事实。
- 将“材料中明确给出的事实”和“为帮助理解而设计的讲解”分开；缺少事实时提出问题或删去该点，不得补造公司、产线、岗位、安全事件或数据。

### 3. 先讲清结构，再做页级策划

- 先交付可讨论的大纲：每部分解决什么问题、服务哪类受众、预计时长与关键结论。长时培训应按实际教学节奏拆分（例如上午/下午、讲解/练习/休息），不要默认连续讲完。
- 用户确认结构后，再给出页级 storyboard：每页标题、核心结论、依据材料、配图/视频、课堂动作与演讲备注。目录应保留；编号按 `1. 2. 3.` 等用户要求呈现，不附带“第几小时”这类粘标题。
- 页级策划同时明确讲述模块、顺序/并列/比较关系和比较维度；先划定语义边界，再估算容量。超长模块在源稿中按子主题拆分，比较内容按维度成对拆分，不把讲述顺序交给左右栏独立自动分页。
- 需要播放完整视频时，把它安排在自然的课间、讨论或章节转换处；PPT 前后页提供播放目的与复盘要点。若当前 renderer 不支持原生视频嵌入，先明确说明限制和可审阅的插入点，不能悄悄把完整视频替换成无关链接或图片。

### 4. 按证据选择图片与视觉重点

- 每张图片先判断是否真正承担证据、设备认知、过程说明、情境导入或课堂节奏的作用；能用的本地素材优先使用，不能只做纯文字页。
- 用户授权外部检索时，仅在前期研究阶段搜索补足的通用图片；先核验来源、授权条件、与当前单位边界及事实表述，再下载为本地、可读、可追溯的媒体。渲染和验证阶段始终离线，不联网下载媒体。
- 图片不足、涉密、或无法确认可用时，直接列出所需图片的主题、画面、用途和优先级，请用户补充；不要杜撰厂内、公司或岗位场景。
- 正文使用少量而清晰的 `**关键词**` 或 `==提示词==` 强调关键概念、动作、风险和结论，避免把整段文字都加粗。依据语义分页规则选择双栏、顺序正文或比较表，单图内容用 `image-text`，继续避免滥用 `gallery`。

### 5. 形成可审阅的一版，再进入最终渲染

- 大纲、页级 storyboard、事实边界和媒体选择应依次获得用户确认；用户要求“先做一版看看”时，只用已确认事实和可用媒体生成可审阅 draft，不把未确认内容伪装为成品。
- 保存用户对目录、编号、关键词高亮、动画、视频插页等人工修改的意图；技能能直接完成的操作应固化为规则，当前 renderer 不能完成的操作要明确列为人工编辑步骤。

## Review Before Render

1. 先完成上述需求澄清、素材台账和大纲/页级 storyboard，再从用户材料中提取 metadata、逻辑页、notes、表格、代码和媒体引用；不要猜测缺失事实。
2. 运行 `example` 获取完整 fixture，或按 Markdown contract 编写/更新 source。
3. 只对缺失或冲突的必需信息集中提问，然后运行 `validate` 和 `template-report`。
4. 让用户审阅 Markdown；确认内容已 finalized，且不存在 `{{待补充:...}}`、`{{AI草稿:...}}` 或缺失媒体。
5. 只有 required facts、required media 和 review markers 全部解决后才运行 final `render`。
6. 在调用方 workdir 运行 `verify --workdir`，并运行 `verify_pptx_renderer.py phase-53` 的固定完整回归；两者都只证明自动结构和离线边界，不能替代真实 PowerPoint/WPS viewer UAT。
7. 重新打开本次 PPTX，按 `references/semantic-pagination.md` 检查实际物理页的讲述顺序、模块完整性和比较同步性。未通过时修改 source、重新 validate/render 并复查，不能将存在残句或交错模块的课件标为最终可上课版本。自动语义检查与真实 viewer 视觉 UAT 分别报告。

### Explicit Generate Requests

- 若用户已经给出明确的现成工作目录、主题/用途和“继续工作并生成 PPT”等直接执行指令，不要再次要求其确认已经明确的结构；将该指令视为对本轮课件生成的授权。
- 在这种直接执行模式下，仍须把可确认事实整理成 Markdown source，先 `validate`，再 `render`，最后用独立 caller workdir 执行 `verify`；不得以省略人工 storyboard 为理由跳过自动验证。
- 直接执行同样必须在生成前划分讲述模块、生成后检查实际语义分页；已有事实与结构足够时自行完成调整，不为常规分页修订追加用户确认环节。
- 若材料足以支撑课件，优先一次性产出可审阅成品；只在缺少标题、受众、日期、关键事实或必需媒体等会改变页面内容的字段时集中提问。没有图片不等于必须停工：可先生成清晰的文字型课件，但不得伪造图片证据。
- 交付时同时报告 source、PPTX 和验证结果；PPTX 文件必须实际存在、非空且可打开（至少通过 OOXML/PPTX 结构检查），不能只报告“已生成”。

## Missing Information Questions

只在对应信息缺失时询问：

- 学校/课程标题：学校名称、课程名称和主标题分别是什么？
- subtitle/term/author metadata：副标题、学期或日期、作者/汇报人哪些需要显示？
- controlled theme：是否确认使用唯一受控主题 `standard-school`？
- required media：每张必需图片或图标的可读本地路径是什么？
- unresolved review markers：`{{待补充:...}}` 与 `{{AI草稿:...}}` 应如何定稿？
- Markdown finalized state：当前 Markdown 是否已经完成内容审阅并允许渲染？

任一必需事实、媒体或 review marker 未解决时，禁止 render；不要用占位内容伪装最终成功。

## Public Commands

```bash
skills/school-pptx/scripts/school-pptx.sh example --out-dir <fixture-dir>

skills/school-pptx/scripts/school-pptx.sh validate \
  --input <reviewed.md>

skills/school-pptx/scripts/school-pptx.sh template-report \
  --theme standard-school \
  --out-md <workdir>/template-report.md \
  --out-json <workdir>/template-report.json

skills/school-pptx/scripts/school-pptx.sh render \
  --input <reviewed.md> \
  --out-dir <delivery-dir> \
  --stem <name>

skills/school-pptx/scripts/school-pptx.sh verify \
  --workdir <caller-workdir>

python3 skills/school-pptx/scripts/verify_pptx_renderer.py phase-53
```

## Outputs and Verification

成功 render 的 current DeliverySpec 是同 stem、逐字节保留的 reviewed `.md`、通过 staged package gate 的原生可编辑 `.pptx`，以及两者持续引用且已确认纳管的 `assets/<safe-relative-path>`。新增视觉布局只接受验证后 hash 绑定的本地媒体；描述符在受限大小、格式和安全路径检查中读取一次，发射器只消费该 payload 并以 `contain` 放置，不联网搜索或下载媒体、字体、图标或模板。`sources/` 永不由普通 render 修改；未引用输入不复制进 `assets/`。根目录只允许 current、`sources/`、`assets/`、`history/` 与本次运行期间的 `.work/`。

完整 candidate 先在 `.work/<run-id>/candidate/` 生成并验证。exact relative set 与 bytes 全部相同即 no-op，不改 current inode/mtime、不建 history；changed 时旧 pair 与全部旧 managed assets 进入同一个 `history/<max+1>/`，归档 Markdown 的 `assets/...` 引用必须在该 sequence 内解析。七类 handled fault 与 `INT`/`TERM` 会恢复旧完整 bundle 并清理本次 history/work；这不承诺 `SIGKILL`、断电或多个路径的硬原子性。parser、plan 或 runtime 非零时，结构有效的 best-effort deck 只在 owned work evidence 生命周期内存在，绝不发布为 current。

manifest、logical JSON、日志、诊断和 verification evidence 不进入公开 delivery；`verify --workdir` 只写调用方指定、且不同于普通 delivery root 的 workdir。自动目录/OOXML PASS 不等于 PowerPoint/WPS 人工 UAT PASS。

## Runtime Adapter Notes

以下是唯一 runtime-specific 区域；canonical workflow 不依赖这些私有路径或发现机制。

| Runtime | Discovery/support files | Explicit invocation fallback | Python/packages | External commands | Execute/read/write | Sandbox/allowlist | Delivery/verify roots |
|---|---|---|---|---|---|---|---|
| Codex | 通过项目 `AGENTS.md` 或已安装的本地 skill 机制发现，并保留整个 `school-pptx` folder、references/scripts/templates/fixtures。 | 自动脚本发现不可用时，显式调用 `scripts/school-pptx.sh`。 | 需要 Python、python-pptx、Pillow、lxml、PyYAML；Pandoc 可选。 | shell/Python 是外部命令；不联网、不自动安装。 | installation-time verification 要实测脚本执行、support 读取与 authorized root 写入。 | 将脚本、模板、fixture、媒体与目标目录纳入 sandbox/allowlist。 | delivery root 允许受管 current/support，运行期写 `.work`；`verify --workdir` 使用另一调用方可写根。 |
| Claude Code | 适用版本可安装整个 folder 到 `.claude/skills/school-pptx/`；保留所有支持目录。 | 自动脚本发现不可用时，显式调用 `scripts/school-pptx.sh`。 | 需要 Python、python-pptx、Pillow、lxml、PyYAML；Pandoc 可选。 | shell/Python 是外部命令；不联网、不自动安装。 | installation-time verification 要实测 execute/read/write 权限和相对支持路径。 | 在工具 allowlist/sandbox 中允许脚本、输入媒体和目标目录。 | delivery root 仅 current/support 与运行期 `.work`；verify 使用独立 caller workdir。 |
| Gemini CLI | 通过 `GEMINI.md` 或项目上下文指向整个 canonical folder，并确认支持文件随安装保留。 | 无自动发现时显式读取本文件并调用 `scripts/school-pptx.sh`。 | 需要 Python、python-pptx、Pillow、lxml、PyYAML；Pandoc 可选。 | shell/Python 是外部命令；不联网、不自动安装。 | installation-time verification 要实测脚本执行、支持文件读取和目标写入。 | 显式批准脚本、模板、fixture、媒体与输出的 sandbox/allowlist。 | delivery root 仅 current/support 与运行期 `.work`；`verify --workdir` 指向另一调用方根。 |
| OpenCode | 使用适用版本的 native skill path 或 Claude-compatible fallback，whole-folder 安装并验证支持文件。 | 自动脚本发现不可用时显式调用 `scripts/school-pptx.sh`。 | 需要 Python、python-pptx、Pillow、lxml、PyYAML；Pandoc 可选。 | shell/Python 是外部命令；不联网、不自动安装。 | installation-time verification 要实测 execute/read/write 权限，不假定继承宿主权限。 | 配置 sandbox/allowlist 读取模板、fixture、媒体并写目标目录。 | delivery root 授权 current/support 与 `.work`；verify 只用明确 caller workdir。 |
| OpenClaw | 作为必需 runtime；exact skill root、frontmatter 解析、support-file discovery 和 whole-folder 完整性必须 installation-time verification。 | automatic script discovery 不作保证；安装时验证后仍保留显式 `scripts/school-pptx.sh` fallback。 | 安装时核验 Python、python-pptx、Pillow、lxml、PyYAML；Pandoc 可选。 | shell/Python 属外部命令；禁止联网与自动安装。 | installation-time verification 覆盖 execute/read/write 权限。 | 安装时核验脚本 allowlist、sandbox 对模板/fixture/媒体/目标的访问。 | installation-time 实测 delivery `.work` 收尾与独立 caller `verify --workdir` 边界。 |
| Hermes Agent | 作为必需 runtime；先通过 `skills_list`/`skill_view` 确认实际生效的 profile-local root，禁止猜 shared 同名路径。必须核验 frontmatter、support-file discovery、whole-folder 完整性及读取权限。 | automatic script discovery 不作保证；保留 explicit invocation fallback。对每次执行显式设置 `SCHOOL_PPTX_PYTHON=<ready-venv>/bin/python` 后调用 `<effective-skill-root>/scripts/school-pptx.sh`；脚本也会继承已激活的 `VIRTUAL_ENV`。 | 先用同一个解释器执行 `import pptx, PIL, lxml, yaml`；缺任一项时停止并报告 interpreter 与缺失包，不能改用系统 `python3`，也不能在渲染过程中自动安装。 | shell/Python 属外部命令；禁止联网与自动安装。 | installation-time verification 覆盖 execute/read/write 权限；聊天中不得尝试 patch 已安装的只读技能。更新必须走已配置的 Presto 更新链路，然后重新发现 effective root。 | 安装时核验 allowlist/sandbox 对完整 folder、媒体和目标目录的访问。 | 先对同一解释器运行 `validate`，仅成功后 `render`；再用独立 caller workdir `verify`，并明确区分自动验证与 WPS/PowerPoint 人工 UAT。 |

Hermes 执行前的最小预检（路径以 `skills_list` 返回的 effective root 为准）：

```bash
HERMES_SKILL="<effective-skill-root>"
HERMES_PYTHON="<ready-venv>/bin/python"
test -x "$HERMES_PYTHON" && "$HERMES_PYTHON" -c 'import pptx, PIL, lxml, yaml'
SCHOOL_PPTX_PYTHON="$HERMES_PYTHON" "$HERMES_SKILL/scripts/school-pptx.sh" validate --input <reviewed.md>
```

若预检失败，先报告失败，不要在 shell 中另起一套手写 `python-pptx` 生成逻辑；若技能更新或同名副本造成路径不一致，先完成更新与重新发现，再从 `validate → render → verify` 执行。

## Safety

- render 和 verify 阶段不联网、下载安装依赖、字体、模板或媒体；前期外部图片研究仅在用户明确授权后进行，且结果必须本地化、可读、可追溯并经过事实与使用边界核验。缺少 required dependency 时非零失败并给出 bounded remediation。
- 不把 `.potx` 视觉源样本当作直接 runtime template，不允许 Markdown 覆盖坐标、字体、颜色、裁剪或动画。
- 不调用 sibling skill scripts，不把整页截图作为 PPTX 内容，不把 best-effort 产物或自动结构检查描述为人工 UAT PASS。
- 写入前确认 delivery 与 verify workdir；render 的 best-effort evidence 只在 owned `.work` 生命周期，verify 证据只留 caller workdir。
