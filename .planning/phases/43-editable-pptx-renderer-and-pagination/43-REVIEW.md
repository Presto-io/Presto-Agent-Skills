---
status: issues_found
phase: 43-editable-pptx-renderer-and-pagination
depth: standard
diff_base: 1f36ad596bf872244d23b9d4924b23c45970052b
files_reviewed:
  - skills/school-pptx/references/template-contract.md
  - skills/school-pptx/scripts/pptx_emit.py
  - skills/school-pptx/scripts/pptx_model.py
  - skills/school-pptx/scripts/pptx_objects.py
  - skills/school-pptx/scripts/pptx_ooxml.py
  - skills/school-pptx/scripts/pptx_paginate.py
  - skills/school-pptx/scripts/pptx_render.py
  - skills/school-pptx/scripts/school-pptx.sh
  - skills/school-pptx/scripts/template_report.py
  - skills/school-pptx/scripts/verify_pptx_renderer.py
  - skills/school-pptx/templates/standard-school.manifest.yaml
findings:
  critical: 2
  warning: 6
  info: 0
  total: 8
---

# Phase 43 代码审查

## Critical

### [C-01] staged PPTX 关闭描述符后按路径写入，存在可利用的符号链接 TOCTOU

- 定位：`skills/school-pptx/scripts/pptx_render.py:186`
- 相关：`skills/school-pptx/scripts/pptx_render.py:327`
- 问题：`reserve_pptx()` 使用 `O_EXCL|O_NOFOLLOW` 创建文件后立即关闭描述符，只把路径交给 `presentation.save()`。从关闭描述符到实际打开路径之间，具有输出目录写权限的并发进程可以删除该临时文件并放入指向任意文件的符号链接；`presentation.save()` 会跟随该链接写入目标。后续 `assert_temporary()` 虽会发现 inode 改变，但外部目标已经被覆盖，无法回滚。
- 影响：违反 Plan 04 的 held-descriptor、symlink/TOCTOU 与“不可恢复失败不破坏无关文件”安全边界，可造成任意可写文件覆盖。
- 建议：让发射器写入始终持有且经 `fstat` 绑定的文件描述符，或先在不可被交换的私有目录生成并验证，再通过 descriptor-relative、no-follow 的安全复制/提交路径进入输出目录；增加“reserve 后、save 前交换为 symlink”的故障注入门。

### [C-02] 代码块被富文本解析器静默改写，无法保持源码文本

- 定位：`skills/school-pptx/scripts/pptx_objects.py:82`
- 相关：`skills/school-pptx/scripts/pptx_emit.py:158`
- 问题：代码页也通过 `add_plain_lines()` 调用 `add_rich_text()`，因此 `inline_spans()` 会把代码中的 `**...**` 和 `==...==` 当作 Markdown 样式并删除分隔符。最小复现 `if a == b == c:\nreturn **value**` 会变为可见文本 `if a  b  c:\nreturn value`，同时错误添加 highlight/bold。
- 影响：代码内容被静默篡改，直接违反 D-03 的源码文本往返、PPTX-10 的原始代码保真和“机械发射冻结计划”的核心契约。
- 建议：为代码建立不经过 `inline_spans()` 的纯文本发射路径，仅设置等宽字体并原样写入换行；回归门加入包含比较运算符、Markdown 分隔符字符串和连续星号的代码向量，并断言重开文本逐字符相同。

## Warning

### [W-01] 媒体与富文本对象错误未转换为 bounded domain error

- 定位：`skills/school-pptx/scripts/pptx_render.py:365`
- 相关：`skills/school-pptx/scripts/pptx_objects.py:129`
- 问题：`_safe_image_size()`、`normalize_rich_text()` 和 notes helper 会抛出 `PptxObjectError`，但 `emit_deck()` 没有包装它，`render_command()` 也不捕获该类型。超大图片、不允许的 GIF/WebP、像素超限或重叠 span 会越过三态状态机并输出 Python traceback。
- 影响：违反 D-17/D-19 的有界非成功输出及“无 traceback/无内部路径泄漏”要求；现有 publication gate 只覆盖缺依赖和 staged corruption，未覆盖对象层异常。
- 建议：在 emitter 边界统一把 `PptxObjectError` 映射成带稳定 code/message 的 `PptxEmitError`，并为格式、大小、像素和 span 错误添加黑盒 CLI 负例。

### [W-02] two-column 只规划和发射左栏，右栏从未使用

- 定位：`skills/school-pptx/scripts/pptx_paginate.py:321`
- 相关：`skills/school-pptx/scripts/pptx_emit.py:145`
- 问题：分页器对 `two-column` 固定选择 `left_body`，发射器又把所有 fragment 拼接到同一个左栏文本框；`right_body` 没有任何消费路径。canonical fixture 的五个块因此全部堆入左栏，而计划要求成对块分配两栏、奇数尾块留左栏。
- 影响：双栏布局语义和模板几何失效，并可能让左栏溢出、右栏空白；现有测试只检查 layout 名存在，没有检查左右栏内容归属。
- 建议：在物理模型中保留栏位归属或左右 fragment 集，按成对块分别测量/分页并机械发射到两个 slot；结构门应断言左右 textbox 的内容和奇数尾块规则。

### [W-03] cover 只发射标题，canonical subtitle 与封面元数据全部丢失

- 定位：`skills/school-pptx/scripts/pptx_emit.py:114`
- 问题：通用发射逻辑仅处理 `title` slot；封面的 `subtitle` 必需槽位以及 document metadata 中的 school、department、author、date 等没有进入冻结计划或 emitter。canonical fixture 即使提供 subtitle，也会生成空副标题封面。
- 影响：PPTX-03 的模板一致封面信息不完整，且属于静默内容丢失；现有 full-fixture 结构门没有验证封面可见文本。
- 建议：在物理计划中显式携带封面字段到 manifest-owned slot，并为所有受支持元数据定义确定的组合规则；重开门断言 title/subtitle 及约定元数据均存在且无硬编码坐标。

### [W-04] contents 的连续编号只存在 metadata，发射时被忽略

- 定位：`skills/school-pptx/scripts/pptx_paginate.py:577`
- 相关：`skills/school-pptx/scripts/pptx_emit.py:150`
- 问题：分页器写入 `number_start/number_end`，但 emitter 只把 `fragment.items` 原样追加到文本行，未使用起始编号。因此目录页可见内容没有 `1. / 2. / ...`，更谈不上跨物理页连续编号。
- 影响：D-10 的“编号连续”只在计划元数据中存在，没有落实到 PPTX；测试也只比较未编号的 item 顺序。
- 建议：由 paginator 生成明确、不可变的编号展示项，或由 emitter 严格按 `number_start` 格式化；增加多页目录重开文本断言。

### [W-05] 表格分页测得的逐行高度没有进入模型，emitter 改为平均行高

- 定位：`skills/school-pptx/scripts/pptx_objects.py:117`
- 相关：`skills/school-pptx/scripts/pptx_paginate.py:483`
- 问题：分页器按每个单元格换行结果计算不同 row height 并据此选字体和分页，但 `BlockFragment` 不携带选定行高；发射器把可用高度平均分给所有行。长文本行可能得到小于测量需求的高度，短行反而占用多余空间。
- 影响：即使纯分页 gate 判定“不溢出”，最终 native table 仍可能截断或产生不可读行，破坏 D-08 的全表搜索与 emitter 不改写分页决定契约。
- 建议：把 header/data row heights 作为冻结计划的一部分并在 `add_table()` 精确应用；结构测试应构造一长多短的不均匀行并核对 OOXML 行高与计划一致。

### [W-06] template-report 对可指定 PPTX 包执行无上限解压与 XML 解析

- 定位：`skills/school-pptx/scripts/template_report.py:62`
- 问题：`load_shape_index()` 直接遍历全部 ZIP 名并 `pptx.read(name)`，没有 entry 数、单项大小、总解压预算、重复路径或 XML 实体标记检查。命令公开支持 `--template <template.pptx>`，攻击者可提供压缩炸弹或超大 slideLayout XML 触发内存/CPU 耗尽。verifier 中的 `safe_package_entries()` 负例测试的是测试 helper，并未覆盖生产 `template_report.load_shape_index()`。
- 影响：与 Plan 01 声明的模板 ZIP/XML 资源上限不一致，恶意或损坏模板可使 agent 进程失去有界失败能力。
- 建议：让 template-report 复用生产级有界 ZIP/XML reader，先校验路径、重复 entry、解压预算和实体声明，再解析必要的 layout parts；负例必须黑盒调用 public `template-report --template`。

## 验证记录

- `python3 -m py_compile ...`：通过。
- `python3 skills/school-pptx/scripts/verify_pptx_renderer.py contract-model`：通过。
- `python3 skills/school-pptx/scripts/verify_pptx_renderer.py pagination`：通过。
- 当前系统 Python 缺少 `python-pptx`，未重复运行依赖该库的 emit/publication aggregate；以上对象发射与发布问题通过源码路径和最小纯 Python 复现确认。

