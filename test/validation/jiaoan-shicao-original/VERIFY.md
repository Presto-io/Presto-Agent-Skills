# jiaoan-shicao 原创验证记录

## 验证对象

- 技能入口：`skills/jiaoan-shicao/SKILL.md`
- 格式参考：`skills/jiaoan-shicao/references/format-and-rendering.md`
- 验证目录：`test/validation/jiaoan-shicao-original/`

## 原创性说明

本次验证文档主题为“工业传感器安装与信号检测”，围绕智能分拣实训单元中的电感式接近开关、光电传感器和磁性开关安装调试展开。课程主题、学习任务、教学内容、活动安排、评价项均为本次新写内容。

未复制 `test/1.10/电气设备控制线路安装与调试教案.md` 或其他既有教案正文；仅参考 `jiaoan-shicao` 技能的字段结构、章节结构和渲染约束。

原创性关键词复核命令未命中 v1.10 样例特征词：

```bash
rg -n "CA6140|车床|电气设备控制线路|电工工艺学|顺序启动|逆序停止" \
  test/validation/jiaoan-shicao-original/source.md \
  test/validation/jiaoan-shicao-original/output.typ
```

## 执行命令

已执行：

```bash
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input test/validation/jiaoan-shicao-original/source.md \
  --typ test/validation/jiaoan-shicao-original/output.typ

env SOURCE_DATE_EPOCH=1780000000 typst compile \
  test/validation/jiaoan-shicao-original/output.typ \
  test/validation/jiaoan-shicao-original/output.pdf
```

命令结果：

- render：成功，输出 `wrote test/validation/jiaoan-shicao-original/output.typ`
- typst：成功，`typst 0.14.2 (unknown hash)`，编译命令退出码为 0

## 结果

- `source.md`：已生成原创 Markdown intermediate
- `output.typ`：已由技能内部脚本生成
- `output.pdf`：已由 `typst compile` 生成
- 原创性复核：已确认未复制既有 `test/1.10` 正文，且未命中样例主题特征词

## SHA-256

```text
1ea7e970f1c0f73e59e82ff294b9cabd6be86153fc2997147531821e8cbb46ff  test/validation/jiaoan-shicao-original/source.md
4deee5293adc98fa9e9a9686b0ea4a7ee94156fb3146fe6c32f8e715292fc893  test/validation/jiaoan-shicao-original/output.typ
f2dea57586c64ab18314713d1e1ab7cfd0c7962dbad5314b4a44fccfc4a87fd1  test/validation/jiaoan-shicao-original/output.pdf
```

## 备注

当前 `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render` 使用 v1.10 fixture-backed renderer，要求输入包含 3 个学习任务。首次单任务原创稿触发 `expected 3 learning tasks, found 1`，因此最终验证稿按同一原创课程拆分为 3 个独立学习任务，每个任务 4H，总课时 12H。
