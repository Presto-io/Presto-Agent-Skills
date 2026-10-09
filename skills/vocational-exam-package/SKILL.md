---
name: vocational-exam-package
description: "用于编制完整职业技能等级认定试卷包，编排并复用 vocational-practical-exam 和 vocational-theory-exam，统一多套理论卷、实操卷、答案及评分表。"
metadata:
  short-description: "复用理论与实操技能的认定试卷包"
  version: "0.1.0"
  portability: "canonical"
  supported-runtimes: [Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, Hermes Agent]
---

# 职业技能等级认定试卷包

## 目标与依赖

统一职业、等级、依据、套号和版本，交付配套的理论与实操卷。本技能负责组织、对应和整包验收，命题与版式分别复用 `vocational-theory-exam` 和 `vocational-practical-exam`，不在本技能复制其出题实现。

安装时三个技能目录一起保留。先在当前 runtime 的技能清单或用户指定安装目录解析这两个依赖的实际入口，读取各自 `SKILL.md` 及所需支持文件。它们是显式工作流依赖，不通过 Python import 或固定 sibling 路径耦合。依赖缺失时报告确切名称，仍可整理包 Markdown 和材料映射，但不能宣称完整包生成。当前包不提供独立 renderer/publisher，不宣称单目录安装就能生成全部文件。

## 输入与流程

输入为职业/代码、等级、标准及方案、套数、理论/实操范围与分值时间、题库和设备条件、各角色模板及授权交付目录。

1. 使用 [包 Markdown 模板](templates/exam-package.md)保存唯一包级事实、套号配对表、覆盖矩阵和各角色模板路径；各套理论与实操审阅稿保留独立 Markdown，包级记录引用它们。
2. 复用理论技能生成候选理论卷和答案；复用实操技能生成候选实操卷和评分表。子工作流只写同一个 owned run 内对应候选子目录，不各自发布、不创建独立 history。
   母版由对应依赖技能的 `templates/` 提供，默认登记实操默认/备选母版、理论考生/答案母版的实际路径。安装预检必须确认四份 DOCX 可读；包技能不复制一套分叉模板，也不从空白文件生成。用户指定替代模板时逐角色覆盖映射。
3. 复核双方职业/等级/标准/套号/版本一致，答案与评分表严格绑定对应卷；理论和实操分值可独立，综合成绩仅按批准方案计算。
4. 检查每套蓝图覆盖、难度时间可比性、重题情况、答案隔离、安全条件和母版元素保留。子技能通过结构检查仍须整包文件对应检查及逐页视觉复核。
5. 所有成员通过后按 [整包交付契约](references/delivery.md)一次发布；任一成员未通过时保留旧整包，报告缺失成员和失败原因。

## 输出与验证

包级 `<package-stem>.md` 加显式成员表中的各套 Markdown、理论考生卷、理论答案评分、实操考生卷和评分表。批准合并的实操角色只登记一个 DOCX，不能再要求一个不存在的独立评分文件；PDF 按成员表明确登记，渲染失败不得放占位文件。包不默认生成 ZIP；需要时才增加 ZIP 并核对其内容集合，避免把答案一起打进仅给考生的包。

最终核对成员集合、可读性、来源映射、套号及角色；结构脚本、技术审题、真实 Word/WPS 验收分别报告，不互相替代。

## 安全与 Runtime Adapter Notes

原件和模板只读；子技能与主流程共享同一授权根，只有主流程发布完整 current。网络、安装、上传和扩权不由编排隐式授权。外部命令与依赖采用两项子技能声明的 Python/OOXML/渲染器环境。

| Runtime | 发现、依赖与权限 |
|---|---|
| Codex | 安装三个完整目录；从技能清单解析依赖。fallback 显式读取三个入口；sandbox 允许支持/输入读、授权根/owned `.work` 写与实际 Python/渲染器执行。 |
| Claude Code | 整目录发现及三个技能入口 fallback；核对 Python/渲染器和共享根的 execute/read/write、allowlist。 |
| Gemini CLI | 项目上下文登记三个目录，显式入口 fallback；sandbox 放行输入/支持读、共享 candidate/根写和实际命令执行。 |
| OpenCode | 验证三项技能 discovery，未发现时显式入口；依赖路径运行时解析，allowlist 覆盖共享授权根与实际命令。 |
| OpenClaw | 安装时验证三个目录、依赖解析、支持文件、Python/渲染器执行与共享根读写、sandbox/allowlist；未实测不声称自动发现。 |
| Hermes Agent | 安装时核对三项 local/global 路径和整目录支持文件、execute/read/write、共享根 allowlist；显式入口 fallback。 |

验证证据存本次 `.work` 或用户明确指定的 verification workdir，不进入公开成员集合。
