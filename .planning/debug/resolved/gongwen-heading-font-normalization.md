---
status: resolved
trigger: "gongwen 技能会用错：多级标题序号和系统自带序号重复，字体错误。需要同时适应没有多级标题序号和有标题序号的情况；处理方式是直接忽视用户手动输入的多级标题序号。字体需适应更多同类字体，但不能改变字体类型，例如黑体必须保持黑体或思源黑体等同类黑体，不能变成其它字体。"
created: "2026-06-13T00:00:00+08:00"
updated: "2026-06-13T22:21:07+08:00"
---

# Debug Session: gongwen-heading-font-normalization

## Symptoms

- expected_behavior: gongwen 技能转换/渲染时，无论源内容标题是否带用户手写多级序号，都只产生一套模板标题序号；源内容中的手写多级标题序号应被忽略。
- actual_behavior: 标题序号会和模板/系统自动序号重复，导致多级标题序号错误。
- error_messages: 无明确报错；表现为输出格式错误。
- timeline: 用户报告当前一直发生。
- reproduction: 使用 gongwen/presto-gongwen 技能处理带手写多级标题序号或不带序号的公文内容，并检查输出标题序号和字体。
- expected_font_behavior: 字体判断应支持同类型字体等价族，例如黑体、SimHei、STHeiti、Noto Sans CJK SC、Source Han Sans SC、思源黑体可作为黑体类；宋体、SimSun、STSong、Noto Serif CJK SC、Source Han Serif SC、思源宋体可作为宋体类。允许同类型 fallback，不允许黑体变宋体或宋体变黑体。

## Current Focus

- hypothesis: gongwen 技能/脚本对标题序号归一化和字体族选择缺少明确规则或实现，导致手写序号被保留并与模板自动编号重复，同时字体 fallback 过窄或跨类型。
- test: Inspect gongwen skill docs/scripts and fixtures for heading normalization, auto numbering, and font fallback behavior.
- expecting: Find either missing guidance in canonical skill docs, missing shell/script normalization logic, or hard-coded font names that should become typed fallback lists.
- next_action: gather initial evidence
- reasoning_checkpoint:
- tdd_checkpoint:

## Evidence

- timestamp: "2026-06-13T22:21:07+08:00"
  finding: "skills/gongwen/scripts/gongwen_lib/body.sh 的 emit_heading/emit_runin_heading 只剥离尾部控制 marker，不剥离标题开头的 一、/（一）/1./（1） 等手写层级序号；之后 Typst 模板 custom-heading 会再按标题级别自动插入同类编号。"
  supports: "手写标题序号被原样保留并与模板自动编号重复。"
- timestamp: "2026-06-13T22:21:07+08:00"
  finding: "skills/gongwen/scripts/gongwen_lib/typst_head.sh 原本将 FONT_HEI/FONT_SONG/FONT_FS/FONT_KAI 等定义为单个硬编码字体名，缺少同字体类型 fallback 列表和不跨字体类型的实现约束。"
  supports: "字体 fallback 过窄，且规则层无法防止黑体/宋体等跨类型替代。"
- timestamp: "2026-06-13T22:21:07+08:00"
  finding: "新增 fixtures heading-normalization-clean.md 和 heading-normalization-numbered.md；新增 test_heading_normalization.sh 验证带手写标题序号和不带序号的等价输入渲染为完全相同 Typst，并检查黑体/宋体 fallback 列表不跨类型。"
  supports: "bug 已被回归测试覆盖。"
- timestamp: "2026-06-13T22:31:00+08:00"
  finding: "复核后追加覆盖 `1.1`、`2．` 等数字多级/全角标题序号，并移除小标宋 fallback 中的普通宋体类字体。"
  supports: "修复满足手写多级标题序号整体忽略，以及不同字体类型不得互相替代的要求。"

## Eliminated

- 不是外部 Typst/PDF 编译器问题：重复编号在 shell 渲染生成的 Typst 阶段已经可见。
- 不是 Markdown 正文列表编号问题：修复只作用于 Markdown heading 文本，不改普通段落、列表或表格中的业务编号。

## Resolution

- root_cause: gongwen shell 渲染器没有在标题路径剥离用户手写的公文层级序号，导致输入标题中的 `一、`、`（一）`、`1.`、`（1）` 与 Typst 模板自动编号重复；字体常量同时缺少按类型组织的 fallback 列表。
- fix: 在 `body.sh` 增加 `normalize_heading_text`，并在块标题与随文标题渲染前统一剥离中文、阿拉伯数字和数字多级层级序号；在 `typst_head.sh` 将小标宋、黑体、仿宋、楷体、宋体、等宽字体改成同类 fallback tuple，且小标宋不降级为普通宋体；更新 gongwen 规则文档与版本号；添加编号归一化 fixtures 和测试脚本。
- verification: `bash skills/gongwen/tests/test_heading_normalization.sh`; `for file in skills/gongwen/scripts/gongwen.sh skills/gongwen/scripts/gongwen_lib/*.sh skills/gongwen/tests/test_heading_normalization.sh; do bash -n "$file" || exit 1; done`; `mkdir -p /private/tmp/gongwen-debug && skills/gongwen/scripts/gongwen.sh example --output /private/tmp/gongwen-debug/example.md && skills/gongwen/scripts/gongwen.sh render --input /private/tmp/gongwen-debug/example.md --typ /private/tmp/gongwen-debug/example.typ`; `skills/gongwen/scripts/gongwen.sh version`; `skills/gongwen/scripts/gongwen.sh manifest`.
- files_changed: `skills/gongwen/scripts/gongwen_lib/body.sh`; `skills/gongwen/scripts/gongwen_lib/typst_head.sh`; `skills/gongwen/scripts/gongwen_lib/commands.sh`; `skills/gongwen/SKILL.md`; `skills/gongwen/references/format-and-rendering.md`; `skills/gongwen/references/fixtures/heading-normalization-clean.md`; `skills/gongwen/references/fixtures/heading-normalization-numbered.md`; `skills/gongwen/tests/test_heading_normalization.sh`.
