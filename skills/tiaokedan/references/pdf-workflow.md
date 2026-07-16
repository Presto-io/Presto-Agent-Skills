# 调课单 PDF Workflow

本文件补充 `tiaokedan` 的最终交付边界。字段契约与复核标记见 `references/markdown-contract.md`；这里只记录 exact bundle、candidate、PDF、history 与失败恢复。

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

`--typ` 的父目录是授权 delivery root，basename 决定稳定 stem。`--pdf` 必须同 root、同 stem 且使用 `.pdf` 后缀；跨 root、不同 stem、`..`、分隔符或 NUL 在 mutation 前失败。

## Exact Managed Sets

- 不带 `--pdf`：`<stem>.md`、`<stem>.typ`。
- 带 `--pdf`：`<stem>.md`、`<stem>.typ`、`<stem>.pdf`。

optional PDF 的增加或移除会改变 path set，因此属于 changed publication。根目录可按需保留 `sources/`、`assets/`、`history/`、`.work/`；normal render 不修改 `sources/`，当前 Markdown 没有 managed asset 引用时也不推断或复制 `assets/`。

## PDF Success Criteria

PDF 只有在以下条件全部满足时才算成功：

1. Markdown 通过 `references/markdown-contract.md` 的 finalized render gate。
2. Markdown、Typst 和 optional PDF 全部先写入同根 `.work/<run-id>/candidate/`。
3. 本机存在 `typst` CLI。
4. `typst compile <candidate.typ> <candidate.pdf>` 退出码为 0。
5. candidate PDF 是 regular、non-empty 且以 `%PDF-` 开头。

只生成 Typst 不能声称最终 PDF 已完成。`typst` 缺失、编译失败或 PDF 为空时，命令必须非零退出。

## Clean Output Boundary

候选验证完成后才检查 current。exact path set 与逐文件 bytes 都相同时返回 identical，不建 history 且不触碰 current。changed 时先把完整旧 2/3 件套复制并复验到 rollback，再写入同一个下一序号 `history/<sequence>/`，最后逐文件发布新 exact set。已有 `001/`、`003/` 时下一序号是 `004/`，不复用 gap。

成功根目录不得平铺 status、manifest、log、diff、debug JSON、tmp、diagnostic 或 negative fixture。临时结构只存在于当前命令拥有的：

```text
build/tiaokedan/
└── .work/
    └── <run-id>/
        ├── candidate/
        ├── rollback/
        └── evidence/
```

owned `.work` 在成功或 handled failure 后收尾；无关 stale run 不得删除。legacy `.tiaokedan/`、legacy `media/`、unknown、symlink、partial bundle 或歧义 stem 均在 current mutation 前失败，只能进入 snapshot-bound 审计与明确确认流程。

## Failure Behavior

- Markdown、expected 或 PDF gate 失败时不改变旧 current/history。
- `typst` 缺失时，stderr 输出简短 blocker：`tiaokedan: typst CLI not found...`。
- expected mismatch 的公开 diff 有界，详细 diff 只在 owned evidence 生命周期内存在。
- publish 中捕获的普通错误、INT 或 TERM 会恢复旧 exact set、移除本次新 history 并清理本次 run；不承诺 SIGKILL、断电或多文件跨路径原子。

## Verification Commands

```bash
python3 -m py_compile skills/tiaokedan/scripts/*.py
python3 -m unittest skills/tiaokedan/scripts/test_delivery_transaction.py -v

skills/tiaokedan/scripts/tiaokedan.sh --help | rg -F -- '--pdf'

skills/tiaokedan/scripts/tiaokedan.sh render \
  --input skills/tiaokedan/templates/tiaokedan.md \
  --typ /tmp/tiaokedan-doc-check.typ

skills/tiaokedan/scripts/tiaokedan.sh render \
  --input skills/tiaokedan/templates/tiaokedan.md \
  --typ /tmp/tiaokedan-doc-check.pdf.typ \
  --pdf /tmp/tiaokedan-doc-check.pdf

test -s /tmp/tiaokedan-doc-check.pdf
head -c 5 /tmp/tiaokedan-doc-check.pdf | rg -F '%PDF-'
```

自动 gate 证明格式与事务边界，不替代教师对事实、版式和最终 PDF 视觉效果的人工验收。
