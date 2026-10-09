---
name: vocational-practical-exam
description: "用于依据职业标准和考核条件编制职业技能等级认定实操试卷、评分表，或将已有实操试卷逐字重构到用户提供的 DOCX 模板副本。"
metadata:
  short-description: "职业技能等级认定实操出题与模板重构"
  version: "0.1.0"
  portability: "canonical"
  supported-runtimes: [Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, Hermes Agent]
---

# 职业技能等级认定实操试卷

## 目标与输入

生成可编辑、可评分、可追溯的实操试卷。先判定任务是新出题、已有题修订还是纯格式重构。输入包括职业及代码、等级、职业标准版本及适用依据、考核范围、套数、时间与分值、场地设备与安全条件、已有原卷、试卷和评分表模板、授权输出目录。优先从材料读取；缺少决定命题有效性的依据时集中询问，不能自行宣称符合认定要求。

## 流程

默认 DOCX 母版随技能携带：[实操默认母版](templates/practical-exam-template.docx)和[实操备选母版](templates/practical-exam-template-alternate.docx)。两份都是用户提供的完整“实操卷 + 评分表”原始母版，题目仅作结构样例，生成时须逐套全部替换。读取 [模板登记](references/docx-templates.md)，不得从空白文档重建。

1. 读取 [命题与版式契约](references/authoring-and-format.md)，核对依据、原卷与母版角色。模板用于版式，原卷或审定稿用于内容；模板中的题目不作为新套卷的事实来源。
2. 使用 [Markdown 模板](templates/practical-exam.md)建立持久、可审阅的 YAML + 正文中间稿。逐套记录任务、要求、评分标准和来源映射；复杂表格合并及图形不能无损表达时保留原件引用和就近复核说明。
3. 新出题先确定能力覆盖与权重，编写可观察的操作任务和逐项评分标准；已有题重构不改任何文字、数字、标点、空格，不扩写或省略。授权直接批量格式重构时不额外要求内容审批。
4. 默认复制技能内实操母版作为候选 DOCX；用户指定新母版时使用指定文件。再替换内容、按实际内容扩缩表格行和列表项；保留模板关系、页眉页脚、绘图、文本框与页面设置。备选母版是同角色变体，按用户选择使用，不强行生成两个版本。安装时模板缺失即报告安装不完整，禁止退回空白文档。
5. 按角色应用标题加粗、真实编号、评分区分页和表格几何；只在授权的评分表单元格内清理多余空行。使用包内只读审计命令辅助逐字和版心检查：

   ```bash
   python3 scripts/audit_docx.py --input candidate.docx --source original.docx
   ```

   `--source` 仅用于逐字重构，命题或批准改题后改与审定稿核对。该脚本不生成文档、不证明评分正确或模板视觉一致。
6. 使用可用 DOCX 渲染器检查全部页面，复核字体、边框、合并单元格、分页和图形。中文缺字的渲染不能作为中文视觉通过证据；报告限制并提供 WPS/Word 可审阅文件。结构检查不替代真实软件验收。
7. 按 [交付规则](references/delivery.md)发布完整候选组。

## 输出、验证与安全

默认每套交付审定 Markdown 和内置母版对应的实操试卷及评分表合并 DOCX；用户要求拆分时再登记独立实操卷和评分表 DOCX。PDF 仅在用户需要且实际渲染成功时加入。分值合计、权重、时间、题目与评分表对应、安全否决条件必须逐项复核。自动编号显示字符与文档文字节点分别验证，避免重复编号或漏编号。

输入原卷和母版只读；不覆盖 WPS/Word 占用文件。脚本仅使用 Python 标准库、读取显式本地文件，审计输出写到终端。生成可使用已可用的 Python/OOXML 库、Word/WPS 或 LibreOffice；安装、上传或扩权需另有授权。不得把此类文件读写任务扩展为真实高压、吊装或机组操作指令的现场执行。

## Runtime Adapter Notes

| Runtime | 发现、依赖与权限 |
|---|---|
| Codex | 整目录发现；失败时显式读取本文件、调用 Python 审计。允许支持文件/输入读、授权交付根和 owned `.work` 写、Python 与实际渲染器执行；遵守 sandbox。 |
| Claude Code | 安装整个技能目录；显式读取和脚本调用为 fallback。检查 Python/渲染器、支持文件读与交付根/`.work` 写权限及 allowlist。 |
| Gemini CLI | 项目上下文指向整目录；显式读取与 Python fallback。sandbox 放行输入/支持文件读、授权根/`.work` 写和渲染器执行。 |
| OpenCode | 验证当前 native skill discovery；保留整目录，失败时显式入口。allowlist 覆盖 Python/渲染器与授权读写。 |
| OpenClaw | 安装时实测整目录发现、Python/渲染器执行、支持文件读、授权根/`.work` 写及 sandbox/allowlist；路径和自动发现未实测不宣称支持，使用显式入口 fallback。 |
| Hermes Agent | 安装时核对 local/global 路径、整目录支持文件、Python/渲染器、execute/read/write 和 allowlist；显式入口与脚本 fallback 保持同一交付边界。 |

验证报告和截图仅写本次 owned `.work` 或显式 verification workdir；后者不属于交付根，不自动清理。
