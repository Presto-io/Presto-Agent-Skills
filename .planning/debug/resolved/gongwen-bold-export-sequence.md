---
status: resolved
trigger: "当前 gongwen 模板无法正确处理加粗内容的渲染和导出；gongwen 技能会生成项目序号；参考但不要照搬 /Users/mrered/Developer/Presto-io/presto-official-templates/gongwen"
created: 2026-06-04
updated: 2026-06-04
---

# Debug Session: gongwen-bold-export-sequence

## Symptoms

- expected_behavior: "gongwen 技能生成的 Markdown/Typst/PDF 应正确保留加粗内容，导出结果应与官方模板语义一致；技能不应凭空生成项目序号。"
- actual_behavior: "加粗内容渲染和导出不正确；技能会生成项目序号。"
- error_messages: "未报告具体错误消息。"
- timeline: "用户在 2026-06-04 报告，当前行为异常。"
- reproduction: "运行 skills/gongwen 的生成/渲染链路，并参考 /Users/mrered/Developer/Presto-io/presto-official-templates/gongwen 对照模板契约。"

## Current Focus

- hypothesis: "gongwen 技能的 Markdown 规范或示例生成规则与官方模板对加粗和项目序号的解析契约不一致。"
- test: "检查 skills/gongwen 的 SKILL、scripts、fixtures，并用包含加粗与项目序号风险的样例跑 renderer。"
- expecting: "定位到是技能提示层、fixture、转换脚本或模板二进制调用参数中的具体差异。"
- next_action: "gather initial evidence"
- reasoning_checkpoint: ""
- tdd_checkpoint: ""

## Evidence

- timestamp: 2026-06-04
  observation: "参考 gongwen 模板源码中 `ast.KindEmphasis` 的二级强调会输出 `#strong[...]`，说明 `**...**` 是正确的 Markdown 加粗入口。"
  implication: "本仓库 shell renderer 应显式保留 strong 语义，并确保 PDF 字体环境中加粗可见。"
- timestamp: 2026-06-04
  observation: "本仓库 `skills/gongwen/scripts/gongwen.sh render` 可输出 `#strong[...]`，但原脚本没有 PDF 导出入口，技能文档也写着 PDF 编译在脚本外。"
  implication: "用户报告的导出问题至少包含工作流缺口：生成 Typst 后没有技能内可验证的 PDF 导出路径。"
- timestamp: 2026-06-04
  observation: "`skills/gongwen/templates/gongwen-full.md` 的示例默认包含有序列表和 `序号 | 项目 | 检查要点` 长表。"
  implication: "示例会诱导 agent 在源材料未要求编号时生成项目序号、序号列或编号化项目清单。"
- timestamp: 2026-06-04
  observation: "验证命令 `bash skills/gongwen/scripts/gongwen.sh render --input <sample.md> --typ <out.typ> --pdf <out.pdf>` 成功，Typst 中包含 `#show strong` 和 `#strong[...]`，PDF size=27847。"
  implication: "加粗 Typst 生成和 PDF 导出路径已可自动验证。"

## Eliminated

- hypothesis: "必须照搬 Presto-io gongwen 实现才能修复。"
  reason: "只需对照官方模板语义即可；本次修复保持 shell-owned renderer，没有迁移 Go 实现。"
- hypothesis: "用户必须手动在脚本外运行 typst 才能导出 PDF。"
  reason: "新增 `--pdf` 后，技能脚本可在 typst CLI 存在时直接导出 PDF。"

## Resolution

- root_cause: "shell-only gongwen 技能缺少显式 PDF 导出入口和强制可见的 strong 展示规则；示例模板和技能说明又默认展示有序列表/序号项目表，诱导 agent 凭空生成项目序号。"
- fix: "为 renderer 增加 `#show strong` 和 `render --pdf`；收紧 SKILL 规则，要求仅保留源材料明确给出的编号；去掉示例模板里的默认有序列表和 `序号/项目` 表格列。"
- verification: "`bash -n skills/gongwen/scripts/gongwen.sh`; `render --input <sample.md> --typ <out.typ> --pdf <out.pdf>`; `render --expected-typ`; `example` + `render` 完整模板；扫描示例输出无默认 ordered list 或 `序号/项目` 表格列。"
- files_changed: "skills/gongwen/SKILL.md; skills/gongwen/scripts/gongwen.sh; skills/gongwen/templates/gongwen-full.md; .planning/debug/gongwen-bold-export-sequence.md"
