# jiaoan-shicao 黑盒差异 Debug 记录

## 结论

PASS

本技能脚本从同一份 Markdown 生成的 `output.typ` 已与黑盒模板生成的 `blackbox.typ` 字节一致；在固定 `SOURCE_DATE_EPOCH` 后，`output.pdf` 也与 `blackbox.pdf` 字节一致。

## 根因

差异来自本技能库 AWK 渲染器仍使用旧 fixture 的近似常量：

- `#set document author` 直接使用 `teacher_name`，当教师名为空时输出空字符串；官方实现会回退到 `Presto`。
- 学习资源表列宽按任务序号硬编码，未复刻官方 `resourceColumnWidthsCM` 的内容驱动算法。
- 教学活动设计表列宽按任务序号硬编码，未复刻官方 `tableColumnWidthsCM` 的 chapter 级共享列宽算法。
- AWK 环境下 `length()` 按 UTF-8 字节计数，直接用它计算中文宽度会把中文字符放大为字节宽度；修复时改用 `gsub` 的非 ASCII 匹配次数模拟官方 Go 的 rune 级 `displayWidth`。

## 官方依据

对照本地官方实现文件：

```text
/private/tmp/presto-jiaoan-shicao-main.go
```

关键实现：

- `generateTypstWithFrontMatter`：空 `TeacherName` 回退为 `Presto`。
- `resourceColumnWidthsCM`：`portraitTableTotalWidthCM = 16.34`，最小宽度 `{3.2, 2.6, 2.2}`，按 `sqrt(displayWidth(content))` 生成目标宽度，再用 `0.02cm` 步进枚举，以 `maxLoad`、`maxLines`、`totalLines`、`distance` 排序。
- `tableColumnWidthsCM`：`activityTableTotalWidthCM = 25.04`，使用 header 最小宽度、base weights、pressure scales 和内容 pressure 计算活动表列宽。
- `sectionColumnSpecs`：同一 chapter 内多个活动表共享同一组列宽。

## 修改点

修改文件：

```text
skills/jiaoan-shicao/scripts/render_v110_typst.awk
```

修改内容：

- 增加 `display_width` / `content_pressure` 等宽度度量函数。
- 增加学习资源表列宽枚举算法，替换旧的任务序号硬编码列宽。
- 增加教学活动表列宽压力分配算法，并让同一学习任务内多个活动表共享同一组列宽。
- 增加空教师名时的 `author: "Presto"` 回退。

重新生成文件：

```text
test/validation/jiaoan-shicao-original/output.typ
test/validation/jiaoan-shicao-original/output.pdf
test/validation/blackbox-jiaoan-shicao/blackbox.typ
test/validation/blackbox-jiaoan-shicao/blackbox.pdf
test/validation/blackbox-jiaoan-shicao/typ.diff
```

## 验证命令

生成本技能输出：

```bash
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input test/validation/jiaoan-shicao-original/source.md \
  --typ test/validation/jiaoan-shicao-original/output.typ
```

生成黑盒 Typst：

```bash
"/Users/mrered/Library/Application Support/com.mrered.presto/templates/jiaoan-shicao/presto-template-jiaoan-shicao" \
  < test/validation/jiaoan-shicao-original/source.md \
  > test/validation/blackbox-jiaoan-shicao/blackbox.typ
```

生成可复现 PDF：

```bash
env SOURCE_DATE_EPOCH=1780000000 typst compile \
  test/validation/jiaoan-shicao-original/output.typ \
  test/validation/jiaoan-shicao-original/output.pdf

env SOURCE_DATE_EPOCH=1780000000 typst compile \
  test/validation/blackbox-jiaoan-shicao/blackbox.typ \
  test/validation/blackbox-jiaoan-shicao/blackbox.pdf
```

保存 Typst diff：

```bash
diff -u \
  test/validation/jiaoan-shicao-original/output.typ \
  test/validation/blackbox-jiaoan-shicao/blackbox.typ \
  > test/validation/blackbox-jiaoan-shicao/typ.diff
```

严格比对：

```bash
cmp -s test/validation/jiaoan-shicao-original/output.typ \
  test/validation/blackbox-jiaoan-shicao/blackbox.typ

cmp -s test/validation/jiaoan-shicao-original/output.pdf \
  test/validation/blackbox-jiaoan-shicao/blackbox.pdf
```

## 验证结果

```text
typ_cmp=0
pdf_cmp=0
```

SHA-256：

```text
1ea7e970f1c0f73e59e82ff294b9cabd6be86153fc2997147531821e8cbb46ff  test/validation/jiaoan-shicao-original/source.md
4deee5293adc98fa9e9a9686b0ea4a7ee94156fb3146fe6c32f8e715292fc893  test/validation/jiaoan-shicao-original/output.typ
f2dea57586c64ab18314713d1e1ab7cfd0c7962dbad5314b4a44fccfc4a87fd1  test/validation/jiaoan-shicao-original/output.pdf
4deee5293adc98fa9e9a9686b0ea4a7ee94156fb3146fe6c32f8e715292fc893  test/validation/blackbox-jiaoan-shicao/blackbox.typ
f2dea57586c64ab18314713d1e1ab7cfd0c7962dbad5314b4a44fccfc4a87fd1  test/validation/blackbox-jiaoan-shicao/blackbox.pdf
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  test/validation/blackbox-jiaoan-shicao/typ.diff
```

文件大小：

```text
33746   test/validation/jiaoan-shicao-original/output.typ
33746   test/validation/blackbox-jiaoan-shicao/blackbox.typ
288012  test/validation/jiaoan-shicao-original/output.pdf
288012  test/validation/blackbox-jiaoan-shicao/blackbox.pdf
0       test/validation/blackbox-jiaoan-shicao/typ.diff
```

## PDF 说明

未固定 `SOURCE_DATE_EPOCH` 时，Typst 会写入当前编译时间和 XMP `InstanceID`，导致同一份 Typst 分两次编译出的 PDF 内容排版一致但字节不一致。固定 `SOURCE_DATE_EPOCH=1780000000` 后，两个 PDF 字节一致。
