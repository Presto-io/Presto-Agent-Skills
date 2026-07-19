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
- `references/targeted-render-delivery-contract.md`: 目标投影、四态条件、三主题最终 Markdown、自包含照片与 patch/authority 干净投递契约。
- `references/phase-46-baseline.md`: Phase 46 骨架、夹具基线、CLI 边界和字体/依赖要求。
- `fixtures/`: 有照片、无照片、通用版、多目标和错误样例。
- `scripts/graduate-resume.sh`: 离线公开 CLI 入口。

## Canonical Workflow

1. 收集候选人的个人资料、教育、技能、证书、项目、实训、经历、目标岗位和照片情况。
2. 对缺失且影响可信度的资料执行一次追问，不循环追问。
3. 生成或更新 `graduate-resume.md`：把首页信息栏所需的 `profile`、可选本地 `photo` 路径和派生偏好写入 YAML frontmatter；把教育、技能、证书、项目、实训、经历和目标写入 Markdown 正文。
4. 运行 `validate` 检查 schema、必填、稳定 ID、待确认事实、照片状态和 target 完整度。
5. 资料通过 `validate` 后，使用 `render --generic` 或 `render --target <stable-id>` 预检单份版本；使用 `batch` 预检 generic 与全部 confirmed targets。两个命令都固定生成保守稳妥、现代简洁、个性设计三个主题。
6. 检查预检中的版本矩阵、逐条件四态、gap allow、完整 stems 和 `added/updated/unchanged/removed`。没有确认时不改变 current/history；确认无误后用完全相同参数追加 `--confirm`。
7. 失败时按稳定错误码修正事实、覆盖冲突、gap、照片、字体、命名碰撞或投递根异常，再重新预检。不要手工发布 partial triple 或绕过 `.work`/history 审计。
8. 使用 `verify` 运行 schema fixture 和固定布局样张；这些证据只进入调用方临时 workdir，不是正式投递产物。

## 受控 Typst 执行域

`plan`、`render` 与 `batch` 在启动 Typst 前必须取得本机受控执行 helper。未安装 helper，或 helper、`/usr`、`/usr/local`、`/usr/local/libexec` 任一对象不是 `root:wheel`、mode 可写、或 Darwin ACL/扩展权限不能证明真实调用者不可写时，三条入口均以 `TYPST_RUNTIME_INVALID` fail closed；不会创建 candidate、current 或 history。私有临时快照、单次 hash、`/dev/fd` 路径和 chmod 都不能替代该能力。

管理员须先审阅 `scripts/graduate_resume_typst_exec_helper.c` 并记录固定 SHA-256，再在已明确授权的管理员 shell 中显式运行下列命令。安装脚本不会自行调用 `sudo`：

```sh
shasum -a 256 scripts/graduate_resume_typst_exec_helper.c
scripts/install_typst_exec_helper.sh scripts/graduate_resume_typst_exec_helper.c <上述 SHA-256>
```

安装程序从同一 held source descriptor 冻结 root-owned staging，以受信的绝对 `/usr/bin/cc` 和 `env -i` 构建。source、compiler、环境、staging、编译或权限核验任一步失败都会保留旧 helper。安装后管理员必须核验 helper 为 `root:wheel`、mode `4755`，并核验完整父目录链和 Darwin ACL 对真实调用用户不可写；ACL API 或语义无法证明时即安装失败。出现 `TYPST_RUNTIME_INVALID` 后，先修复受控执行域，再用完全相同参数重跑不含 `--confirm` 的预检，成功后才追加 `--confirm`。这不构成 Phase 49 的跨 runtime 安装验收。

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

skills/graduate-resume/scripts/graduate-resume.sh verify
```

`render` 在 `--generic` 与 `--target` 中二选一，固定采用 patch 语义；`batch` 默认展开 generic + all confirmed targets，固定采用 authority 语义。`--retain`、`--exclude`、`--pin`、`--allow-gap-target` 可重复；不适用覆盖只有 `--not-applicable <target-id> <condition-id> <reason>` 这一种公开三参数语法。先运行上述命令查看预检，再追加 `--confirm` 发布。

## Runtime Adapter Notes

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

- 不要把 target 关键词、主题偏好或照片布局回写为基础事实。
- 不要把未确认、过期或推断出的资料当作 final render 事实。
- 不要为照片生成、猜测或写入远程 URL；无照片时省略 `photo` 字段。
- 不要把主题、页数或照片布局回写为 `graduate-resume/v2` 的基础事实；照片必须是显式本地文件，且无照片输出不得保留图像、路径、EXIF 或照片装饰。
- 不要把电话、邮箱、身份证、原始招聘 URL 写入输出 stem 或 history 路径。
- 不要把完整 condition reason/evidence、preview、normalized photo 或 manifest sidecar 放入 delivery root。
- 不要在未检查权威目标矩阵和 removals 时追加 `--confirm`。
- 不要把 Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw 或 Hermes Agent 的私有语法写入 canonical 主流程。
