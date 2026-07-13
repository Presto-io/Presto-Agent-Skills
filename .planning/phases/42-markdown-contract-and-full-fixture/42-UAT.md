---
status: complete
phase: 42-markdown-contract-and-full-fixture
source: [42-01-SUMMARY.md, 42-02-SUMMARY.md, 42-03-SUMMARY.md]
started: 2026-07-13T18:44:18Z
updated: 2026-07-13T18:59:34Z
---

## Current Test

[testing complete]

## Tests

### 1. 阅读 Markdown 作者契约
expected: 打开 skills/school-pptx/references/markdown-contract.md 后，可以清楚看到仅允许的 10 个 YAML 字段、`::: slide {layout="..."}` 语法、10 个可写布局与 1 个隐式 closing；文档不向作者暴露 PPTX 坐标、字体、颜色或任意样式控制。
result: pass

### 2. 生成完整且可复核的示例
expected: 运行 `skills/school-pptx/scripts/school-pptx.sh example --out-dir <空目录>` 后，只生成 1 个 Markdown 和 4 个本地 PNG；Markdown 是连贯的智能制造课程演示，覆盖全部布局语义、notes、图片、表格、时间线、画廊、代码及溢出输入。
result: pass

### 3. 校验逻辑文档与内容顺序
expected: 对完整示例运行 `validate` 后返回成功且无错误；逻辑 JSON 显示 contents 仅由有效 `##` 按源码顺序生成，`#` 只在 YAML 缺少 title 时回退为文档标题，notes 不进入可见块，媒体保留标题与路径信息。
result: pass

### 4. 获得可定位的负例诊断
expected: 使用未知布局、原始坐标样式、任意字体或颜色、unsupported raw HTML、缺失媒体等无效输入时，`validate` 非零退出，并按源码顺序给出稳定错误代码、文件位置和行号，不输出 traceback 或虚假的 PASS。
result: pass

### 5. 严格处理 YAML、代码围栏与表格
expected: YAML 的日期、布尔、数字、列表或映射值不会被静默强制转换；围栏代码中的 directive-like 文本保持原样；缺少或错误分隔行、列数不等的 table/timeline 会在对应源码行明确失败。
result: pass

### 6. 安全且确定性地写出示例
expected: 对同一输出目录重复运行 `example` 时，5 个命令自有文件保持字节一致并保留无关文件；目录碰撞、符号链接交换或缺少安全 I/O 能力时会在边界外文件未被修改的情况下失败关闭。
result: pass

## Summary

total: 6
passed: 6
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none yet]
