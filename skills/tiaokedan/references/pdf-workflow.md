# 调课单 PDF Workflow

本文件补充 `tiaokedan` 的最终渲染边界。字段契约、必填项、`{{待补充: ...}}` 和 `{{AI草稿: ...}}` 规则见 `references/markdown-contract.md`；这里只记录 Typst/PDF 命令、干净输出和诊断约定。

## Command Shapes

只生成 Typst：

```bash
skills/tiaokedan/scripts/tiaokedan.sh render \
  --input skills/tiaokedan/templates/tiaokedan.md \
  --typ build/tiaokedan/tiaokedan.typ
```

生成 Typst 并编译 PDF：

```bash
skills/tiaokedan/scripts/tiaokedan.sh render \
  --input skills/tiaokedan/templates/tiaokedan.md \
  --typ build/tiaokedan/tiaokedan.typ \
  --pdf build/tiaokedan/tiaokedan.pdf
```

用于临时回归或阶段证据的参考 Typst 比对：

```bash
skills/tiaokedan/scripts/tiaokedan.sh render \
  --input skills/tiaokedan/templates/tiaokedan.md \
  --typ build/tiaokedan/tiaokedan.typ \
  --expected-typ /tmp/tiaokedan-expected.typ
```

`--expected-typ` 是证据/回归 gate；普通教师表单不需要和示例 Typst 逐字节一致，仓库也不要求保留 `.typ` fixture。

## PDF Success Criteria

PDF 只有在以下条件全部满足时才算成功：

1. Markdown 通过 `references/markdown-contract.md` 的 finalized render gate。
2. `.typ` 写入调用方显式指定的 `--typ` 路径。
3. 本机存在 `typst` CLI。
4. `typst compile <output.typ> <output.pdf>` 退出码为 0。
5. `--pdf` 路径存在且文件大小大于 0。

只生成 Typst 不能声称最终 PDF 已完成。`typst` 缺失、编译失败或 PDF 为空时，命令必须非零退出。

## Clean Output Boundary

成功时，公开输出目录只应包含调用方显式请求的教师可用文件：

- `--typ` 指定的 generated Typst。
- `--pdf` 指定的 final PDF。

成功路径不得在公开目录旁生成 status、manifest、log、stderr、stdout、diff、debug JSON、tmp、diagnostic 或 negative fixture 文件。

如果以后需要更丰富的诊断，使用输出目录下隐藏的 `.tiaokedan/` 目录，例如：

```text
build/tiaokedan/
├── tiaokedan.typ
├── tiaokedan.pdf
└── .tiaokedan/
    └── debug-or-failure-evidence
```

当前 Phase 40 默认成功命令不写 `.tiaokedan/`；该目录是 debug/failure-only 约定，不是教师交付内容。

## Failure Behavior

- Markdown 校验失败时，不写 PDF。
- `typst` 缺失时，stderr 输出简短 blocker：`tiaokedan: typst CLI not found...`。
- 编译失败或 PDF 为空时，删除请求路径上的不完整 PDF，避免公开目录留下看似完成的文件。
- 失败诊断默认走 stderr；若后续加入详细诊断，必须写到隐藏 `.tiaokedan/`。

## Verification Commands

```bash
python3 -m py_compile skills/tiaokedan/scripts/tiaokedan_renderer.py

skills/tiaokedan/scripts/tiaokedan.sh --help | rg -F -- '--pdf'

skills/tiaokedan/scripts/tiaokedan.sh render \
  --input skills/tiaokedan/templates/tiaokedan.md \
  --typ /tmp/tiaokedan-doc-check.typ

skills/tiaokedan/scripts/tiaokedan.sh render \
  --input skills/tiaokedan/templates/tiaokedan.md \
  --typ /tmp/tiaokedan-doc-check.pdf.typ \
  --pdf /tmp/tiaokedan-doc-check.pdf

test -s /tmp/tiaokedan-doc-check.pdf
```
