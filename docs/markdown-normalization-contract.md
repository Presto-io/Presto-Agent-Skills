# Markdown Normalization Contract

本契约定义文档工作流技能的共享 Markdown 中间态。目标是让任意源材料先进入一个可审阅、可编辑、可复用的稳定表示，再由具体技能或模板生成目标格式；它不是通用文档 schema，也不是渲染规则集合。

## Required Pattern

文档工作流技能必须遵守以下模式：

1. 共同目标是 `YAML frontmatter + body`。
2. 每个源材料都必须先归一化为 persistent Markdown，再生成 Typst、HTML 或后续其他目标输出。
3. 这个 Markdown 中间态必须能被人类和 agent 直接阅读、审阅和修改，不能只是一次性的 prompt 临时文本。
4. skill-owned scripts 从同一份 Markdown 中间态生成目标输出，确保同样输入能得到稳定结果。

Source material is normalized to the Markdown intermediate before target generation.

## Intermediate Shape

Markdown 中间态由两个部分组成：

| Part | Requirement |
|------|-------------|
| YAML frontmatter | 保存该技能或模板需要的元数据。共享契约 does not define a universal frontmatter field list。 |
| Body | 保存归一化后的正文结构、内容、引用、说明和需要复核的片段。 |

每个技能或模板可以定义自己的 metadata 字段，但必须保持这些字段的含义可审阅，并避免让目标格式规则反向污染共享中间态。

## Normalized Primitives

| Primitive | Normalize As | Notes |
|-----------|--------------|-------|
| headings | Markdown heading levels | 保留层级和标题文本，避免用视觉样式替代结构。 |
| paragraphs | Plain Markdown paragraphs | 保留段落边界和语义顺序。 |
| lists | Ordered, unordered, or task lists | 保留嵌套关系；任务状态只在源材料明确表达时写入。 |
| tables | Markdown tables | 保留行列含义；复杂合并单元格需要显式复核标记。 |
| code blocks | Fenced code blocks | 保留语言标识；未知语言可以省略但不得改写内容。 |
| links | Markdown links | 保留可见文本和目标地址；缺失地址需要标记复核。 |
| figures | Image or figure-like blocks with nearby caption text | 保留图片引用、替代文本和标题说明；具体 figure 语法由技能或模板决定。 |
| callouts | Blockquote-style notes or skill-local callout syntax | 保留提示类型和正文；具体 marker syntax 由技能或模板决定。 |
| metadata | YAML frontmatter fields or visible body notes | 保存来源、标题、作者、日期、状态等需要追踪的信息；字段名不由共享契约统一规定。 |

## Ambiguous Or Lossy Content

归一化时遇到 ambiguous, unsupported, or lossy fragments，必须做到：

1. 原始信息或足够复核的信息仍然可见。
2. 片段被明确标记为需要 review，不能静默丢弃、猜测或改写成看似确定的内容。
3. 标记必须靠近相关片段，让后续人类、agent 或脚本能定位问题。
4. 共享契约 does not define a universal marker taxonomy；each skill or template chooses its own marker syntax。

Ambiguous, unsupported, or lossy fragments must remain visible and explicitly marked for review.

如果源材料不能完整表达为当前技能支持的 Markdown primitive，优先保留原文、截图引用、摘录、占位说明或局部结构，再用该技能自己的复核标记说明风险。

## Out Of Scope

以下内容不属于本共享契约：

- Typst rules
- HTML rules
- rendering styles
- OCR/extraction
- lint tooling
- universal metadata fields
- a universal marker taxonomy
