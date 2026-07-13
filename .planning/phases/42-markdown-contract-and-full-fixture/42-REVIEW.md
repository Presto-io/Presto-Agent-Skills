---
phase: 42
status: issues_found
depth: standard
files_reviewed: 9
findings:
  critical: 0
  warning: 5
  info: 0
  total: 5
reviewed_at: 2026-07-14
---

# Phase 42 代码审查

## 结论

Phase 42 的权威门禁能够通过，fixture 与四个 PNG 也均有效，但独立负例发现 5 个真实问题：两个解析语义偏差、两个未封装异常路径，以及一个并发文件系统竞态。当前不建议把该逻辑模型直接作为 Phase 43 的唯一解析输入，至少应先修复 YAML 类型、fenced code 与表格结构三个问题。

## Findings

### W-01 — YAML 白名单值未限制为字符串，常见未加引号日期会让 JSON 输出崩溃

- **严重度：** Warning
- **位置：** `skills/school-pptx/scripts/markdown_contract.py:369`、`skills/school-pptx/scripts/markdown_contract.py:373`、`skills/school-pptx/scripts/markdown_contract.py:611`
- **证据：** `yaml.safe_load()` 会把 `date: 2026-07-13` 解码为 `datetime.date`，实现随后原样写入 `metadata`。同一输入不带 `--out-json` 时返回 0 并打印“校验通过”，带 `--out-json` 时 `json.dumps()` 抛出 `TypeError: Object of type date is not JSON serializable` 和完整 traceback。十个公开 formatter 字段也都没有标量字符串类型检查，列表、映射、布尔值和数字同样可能进入模型。
- **影响：** 同一份被声明为有效的 Markdown 会因是否请求 JSON 而产生不同结果；Phase 43 无法依赖“校验通过”的模型一定可序列化，且违反了内部失败不得泄露堆栈的约束。
- **建议：** 在 YAML compose/load 后要求十个公开字段均为字符串标量（或明确、统一地将允许的标量规范化为字符串），拒绝序列/映射及 PyYAML 隐式日期类型；在写文件前先完成 JSON 序列化，并将 `TypeError` 纳入有界诊断。新增未加引号日期、布尔值、列表和映射负例。

### W-02 — slide 外层扫描器不识别 fenced code 状态，代码中的独立 `:::` 会提前闭合 slide

- **严重度：** Warning
- **位置：** `skills/school-pptx/scripts/markdown_contract.py:423`、`skills/school-pptx/scripts/markdown_contract.py:436`、`skills/school-pptx/scripts/markdown_contract.py:444`
- **证据：** 外层 slide 收集循环在进入 `parse_blocks()` 前，把任何独立 `:::` 当作容器闭合符，且未跟踪 fence。最小合法 code slide 的 fenced code 中包含一行独立 `:::` 时，验证错误地返回 `CODE_UNCLOSED`，逻辑 JSON 只保留该行之前的代码。现有 `fence_gate()`（`verify_markdown_contract.py:248`）只测试 HTML/style 文本，没有测试 directive/闭合符文本。
- **影响：** 契约宣称 fenced code 完全不透明，但合法代码内容会改变 Markdown 容器结构、丢失代码并被拒绝；Phase 43 若直接消费该模型将得到截断内容。
- **建议：** 让 slide 收集状态机显式跟踪 fence marker，处于 fence 内时原样收集所有 `:::`、`::: notes` 和 `::: slide` 文本，直到匹配 fence 闭合。增加 fenced code 内独立 `:::`, `::: notes` 和 `::: slide` 的回归用例。

### W-03 — Markdown 表格分隔行与列宽未验证，非法 timeline 会被报告为通过

- **严重度：** Warning
- **位置：** `skills/school-pptx/scripts/markdown_contract.py:280`、`skills/school-pptx/scripts/markdown_contract.py:282`、`skills/school-pptx/scripts/markdown_contract.py:585`
- **证据：** 若第二行不是 `---` 分隔行，解析器只是把它降级为普通数据行；timeline 校验只比较第一行 headers。输入 `| 时间 | 标题 | 说明 |` 后接 `| broken | separator | row |` 再接数据行，公开 `validate` 返回 0、零错误。普通 table 同样不要求有效分隔行，也不检查每行列数与表头一致。
- **影响：** 非 Markdown 表格进入已验证逻辑模型，后续 renderer 可能把伪分隔行渲染成数据、产生错列或在 Phase 43 才失败；这违背“完整 Markdown 表格”和 timeline 唯一规范表头语义。
- **建议：** 要求至少两行、第二行每个 cell 均匹配 `TABLE_SEPARATOR_RE`、数据行列数严格等于表头列数，并为缺失分隔行和列数不一致提供可定位诊断。测试应覆盖 timeline 与普通 table 两类负例。

### W-04 — manifest 加载异常虽被捕获，随后仍引用未赋值变量并泄露 traceback

- **严重度：** Warning
- **位置：** `skills/school-pptx/scripts/markdown_contract.py:627`、`skills/school-pptx/scripts/markdown_contract.py:630`、`skills/school-pptx/scripts/markdown_contract.py:647`
- **证据：** `load_manifest()` 失败时 `except Exception` 构造了 `INTERNAL_ERROR`，但没有给 `manifest` 赋默认值；打印主题时访问 `manifest.get(...)`，触发 `UnboundLocalError`。使用不存在的 skill dir 直接调用脚本可稳定复现完整 traceback。
- **影响：** manifest 缺失、损坏或依赖读取失败时，原本设计的有界内部错误失效；命令输出实现路径和堆栈，且用户看不到可执行修复信息。
- **建议：** 在 try 前初始化安全 manifest 默认值，或在捕获后立即走统一失败输出；把 manifest 缺失、非法 YAML、非法根结构纳入公开 CLI 回归测试，并继续断言无 traceback。

### W-05 — example 的路径预检与实际替换分离，存在父目录 symlink 竞态

- **严重度：** Warning
- **位置：** `skills/school-pptx/scripts/markdown_contract.py:668`、`skills/school-pptx/scripts/markdown_contract.py:686`、`skills/school-pptx/scripts/markdown_contract.py:708`、`skills/school-pptx/scripts/markdown_contract.py:717`
- **证据：** `prepare_example_destinations()` 先检查完整路径树，之后 `replace_file_safely()` 才按路径名重新打开父目录并执行 `NamedTemporaryFile`/`os.replace`。两个阶段之间若另一进程把 `media/` 普通目录替换为指向外部的 symlink，后续临时文件创建和替换会跟随新链接。现有测试只覆盖静态 symlink，不覆盖检查后替换的 TOCTOU 情形。
- **影响：** 在共享或攻击者可写的输出父目录中，固定文件写入边界可能逸出 `--out-dir`，覆盖外部同名目标；这削弱了计划声明的固定所有权和 symlink escape 防护。
- **建议：** 使用已打开目录描述符逐级操作并启用 no-follow 语义（如 `dir_fd` + `O_NOFOLLOW`），在最终 `os.replace` 前基于同一目录句柄确认目标；若无法做到，应明确要求输出树不可被并发修改并在每次写入前重新验证父链。增加可控并发目录交换测试。

## 测试与资产检查

- `python3 skills/school-pptx/scripts/verify_markdown_contract.py fixture-example`：通过。
- 四个 PNG 均为有效的 `1200 × 675`、8-bit RGBA、非交错 PNG，文件哈希互不相同。
- canonical fixture 可由当前验证器通过并覆盖十个显式布局与一个隐式 closing；上述 findings 均来自现有门禁未覆盖的独立最小负例。
- 审查期间未修改源码、fixture 或媒体文件，未提交 Git commit。
