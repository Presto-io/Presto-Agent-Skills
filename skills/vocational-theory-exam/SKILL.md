---
name: vocational-theory-exam
description: "用于依据职业标准、题库或教材编制职业技能等级认定理论试卷、多套等值卷以及独立答案和评分说明。"
metadata:
  short-description: "职业技能等级认定理论试卷命题"
  version: "0.1.0"
  portability: "canonical"
  supported-runtimes: [Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, Hermes Agent]
---

# 职业技能等级认定理论试卷

## 目标与输入

形成考生卷和独立答案评分文件。输入包括职业/代码、等级、适用职业标准版本、知识范围及来源、题库/教材、题型数量与分值、总分时间、套数、难度要求、模板及授权交付目录。从材料推导已知事实，仅对影响正确性和认定适用性的缺失项提问。无适用依据时可做明确标记的草稿，不声称正式符合认定规范。

## 流程

随技能携带 [理论考生卷模板](templates/theory-paper-template.docx)与[理论答案模板](templates/theory-answer-template.docx)。读取 [模板说明](references/docx-templates.md)；生成须复制对应 DOCX 并填充，不从空白文档另起版式。

1. 读取 [理论命题契约](references/authoring.md)，提取知识域、认知层次、题型和权重蓝图。
2. 以 [Markdown 模板](templates/theory-exam.md)建立审阅稿；每题稳定 ID、题干、选项、答案、分值、解析与来源对应。Markdown 为可编辑事实源，不要求用户另维护 JSON/CSV。
3. 按蓝图出题或从授权题库选题，核查技术正确性、等级匹配、唯一答案、单位和条件完整性；多套等值性与跨套重复率按方案核查。
4. 根据用户授权进入定稿。把同一审定稿投影为考生卷、答案评分文件，考生卷不得包含答案、解析、答案批注、修订记录或隐藏答案文本。
5. 用户提供 DOCX 母版时优先使用指定副本，否则复制内置对应角色模板。题量随内容变化，保留页面元素、真实编号及批准加粗；模板缺失则报告安装不完整，不自动改用空白文档。多选、判断或简答的评分规则必须来自认定方案或明确批准，不自行设为通用标准。
6. 检查题号连续、选项唯一标签、答案映射、题型题量和总分；渲染全部页面检查题干/选项分页和答案泄露，按 [交付规则](references/delivery.md)发布。

## 输出与验证

默认 `<stem>.md`、`<stem>-理论试卷.docx`、`<stem>-理论答案与评分.docx`；需要 PDF 时加入同名 PDF，必须实际渲染成功。逐题对照审定稿验证答案与评分，自动总分检查不能替代技术审题；有争议题不得悄悄猜答案。

## 安全

只读原题库/标准/母版；只写用户授权交付目录及本次 owned `.work`。不上传题库、不读取凭据；网络资料仅在授权范围使用并记录来源。Python/OOXML 库及 Word/WPS/LibreOffice 等采用现有环境，安装或扩大权限另需授权。渲染缺字或缺软件时注明未完成的视觉验证，不能冒充 WPS 验收。

## Runtime Adapter Notes

| Runtime | 发现、依赖与权限 |
|---|---|
| Codex | 整目录发现；fallback 显式读取本文件与引用。允许输入/支持文件读、授权根/owned `.work` 写及现有 Python/渲染器执行，遵守 sandbox。 |
| Claude Code | 安装整个技能目录；fallback 显式入口。核对 Python/渲染器执行、支持文件读、授权根/`.work` 写和 allowlist。 |
| Gemini CLI | 项目上下文指向整目录；fallback 显式读取。sandbox 授权输入/支持文件读、交付根/`.work` 写和生成/渲染命令。 |
| OpenCode | 验证 native discovery，保留整个目录；显式入口 fallback，allowlist 覆盖 Python/渲染器及授权读写。 |
| OpenClaw | 安装时验证实际 skill path、整目录发现、依赖与 execute/read/write、sandbox/allowlist；未验证自动发现时显式入口。 |
| Hermes Agent | 安装时验证 local/global 路径、整目录支持文件、Python/渲染器与读写/执行权限；显式入口 fallback 不扩大授权范围。 |

验证证据只存本次 `.work` 或显式 verification workdir，不进入公开根目录。
