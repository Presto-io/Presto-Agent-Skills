# jiaoan-shicao 黑盒验证记录

## 结论

PASS

本次黑盒生成结果与本技能生成产物完全一致：

- `blackbox.typ` 与 `../jiaoan-shicao-original/output.typ`：一致
- `blackbox.pdf` 与 `../jiaoan-shicao-original/output.pdf`：一致

## 反作弊规则遵守情况

- 黑盒 Typst 由模板可执行文件从同一份 Markdown `../jiaoan-shicao-original/source.md` 读取 stdin 后生成到 `blackbox.typ`。
- 黑盒 PDF 由 `typst compile blackbox.typ blackbox.pdf` 生成。
- 未复制、覆盖或用既有 `output.typ` / `output.pdf` 作为黑盒结果。
- 未修改黑盒模板目录。
- 写入范围限定在 `test/validation/blackbox-jiaoan-shicao/` 及配套验证产物目录。

## 环境与工具

模板可执行文件：

```bash
/Users/mrered/Library/Application Support/com.mrered.presto/templates/jiaoan-shicao/presto-template-jiaoan-shicao
```

Typst 版本：

```text
typst 0.14.2 (unknown hash)
```

## 执行命令

生成黑盒 Typst：

```bash
"/Users/mrered/Library/Application Support/com.mrered.presto/templates/jiaoan-shicao/presto-template-jiaoan-shicao" < test/validation/jiaoan-shicao-original/source.md > test/validation/blackbox-jiaoan-shicao/blackbox.typ
```

生成可复现黑盒 PDF：

```bash
env SOURCE_DATE_EPOCH=1780000000 typst compile test/validation/blackbox-jiaoan-shicao/blackbox.typ test/validation/blackbox-jiaoan-shicao/blackbox.pdf
```

保存 Typst diff：

```bash
diff -u test/validation/jiaoan-shicao-original/output.typ test/validation/blackbox-jiaoan-shicao/blackbox.typ > test/validation/blackbox-jiaoan-shicao/typ.diff
```

比对 Typst：

```bash
cmp -s test/validation/blackbox-jiaoan-shicao/blackbox.typ test/validation/jiaoan-shicao-original/output.typ
```

结果：exit code `0`，一致。

比对 PDF：

```bash
cmp -s test/validation/blackbox-jiaoan-shicao/blackbox.pdf test/validation/jiaoan-shicao-original/output.pdf
```

结果：exit code `0`，一致。

## 文件 SHA-256

```text
1ea7e970f1c0f73e59e82ff294b9cabd6be86153fc2997147531821e8cbb46ff  test/validation/jiaoan-shicao-original/source.md
4deee5293adc98fa9e9a9686b0ea4a7ee94156fb3146fe6c32f8e715292fc893  test/validation/jiaoan-shicao-original/output.typ
f2dea57586c64ab18314713d1e1ab7cfd0c7962dbad5314b4a44fccfc4a87fd1  test/validation/jiaoan-shicao-original/output.pdf
4deee5293adc98fa9e9a9686b0ea4a7ee94156fb3146fe6c32f8e715292fc893  test/validation/blackbox-jiaoan-shicao/blackbox.typ
f2dea57586c64ab18314713d1e1ab7cfd0c7962dbad5314b4a44fccfc4a87fd1  test/validation/blackbox-jiaoan-shicao/blackbox.pdf
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  test/validation/blackbox-jiaoan-shicao/typ.diff
7b8bd56baa69a5bb97cd68ce956f9bf3258261e99073368e66eca099d93f883b  /Users/mrered/Library/Application Support/com.mrered.presto/templates/jiaoan-shicao/presto-template-jiaoan-shicao
```

## 文件信息

```text
test/validation/jiaoan-shicao-original/output.pdf:   PDF document, version 1.7, 10 pages
test/validation/blackbox-jiaoan-shicao/blackbox.pdf: PDF document, version 1.7, 10 pages
test/validation/jiaoan-shicao-original/output.typ:   Objective-C source text, Unicode text, UTF-8 text, with very long lines (909)
test/validation/blackbox-jiaoan-shicao/blackbox.typ: Objective-C source text, Unicode text, UTF-8 text, with very long lines (909)
```

文件大小：

```text
33746  test/validation/jiaoan-shicao-original/output.typ
33746  test/validation/blackbox-jiaoan-shicao/blackbox.typ
288012 test/validation/jiaoan-shicao-original/output.pdf
288012 test/validation/blackbox-jiaoan-shicao/blackbox.pdf
0      test/validation/blackbox-jiaoan-shicao/typ.diff
```

## PDF 说明

Typst 默认会写入当前编译时间与 XMP `InstanceID`。本次使用 `SOURCE_DATE_EPOCH=1780000000` 重新编译双方 PDF，确保可复现字节比对。
