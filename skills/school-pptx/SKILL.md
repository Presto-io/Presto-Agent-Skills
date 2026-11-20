---
name: school-pptx
description: Create, redesign, or edit editable school PowerPoint presentations using the current school template. Use for school reports, courseware, training, and defenses from documents, notes, photos, or an existing PPTX.
metadata:
  version: "2.1.0"
  short-description: "学校统一模板与原生可编辑课件制作"
---

# School PPTX

以本技能的学校模板制作可讲、可读、可编辑的演示文稿。默认学校为西安技师学院／西电机电学院；用户指定其他学校模板时，以该模板为准，不带入默认学校标识。

## 统一视觉

| 页面 | 固定规则 |
|---|---|
| 封面 | 居中布局；主标题60pt，副标题20pt；保留渐变、校徽、双校名、校训和书页线。 |
| 目录 | 左侧目录／CONTENTS与学校背景；右侧32pt条目整体垂直居中，每项前置蓝色矩形、白色序号。 |
| 章节 | 66pt章节标题左下对齐；保留校徽和渐变背景。 |
| 正文页页眉 | 顶部标题48pt，两端对齐；保留y=1.912英寸处的装饰分割线。 |
| 正文页内容 | 白底；根据内容设计文字分组、表格、图表、流程和步骤，原生可编辑；正文在y=2.15–6.10英寸内。 |
| 尾页 | 固定学校结束页；不添加结束语，必要说明写入备注。 |

默认画布16:9、13⅓×7½英寸。具体字体、色彩与安全区见 [学校视觉规范](references/school-visual.md)。只使用随本技能提供的`assets/school-template.pptx`作为默认模板。生产目录只维护当前模板、说明和工具；调试样稿、版本比较、开发记录和历史资产放在技能目录之外。

## 工作方式

- 学校视觉固定，正文构图按内容设计；不把每页套成相同卡片，也不为填版面制造数据。
- 以用户资料和已确认事实为依据；来源单位的成果不能写成本校成果。课堂页直接讲知识、问题和任务，制作建议写入备注。
- 原生标题、文字、表格、图表、箭头和标注保持可编辑。图片可用位图，整页截图不能代替课件对象。
- 用户要求直接制作或先做一版时，沿已有授权推进；仅对影响内容的关键缺项集中提问。不要重复要求确认已明确的信息。
- 新建课件或整体重做时，按 [设计与制作](references/design-workflow.md) 形成简短页级计划和项目设计规范。
- 修改现稿或仅改变视觉时，按 [编辑与验收](references/review-and-edit.md) 保留用户要求保留的页序、内容、对象和备注。

## 制作与验证

1. 建立项目目录，保留用户原件；明确受众、用途、事实依据和交付形式。
2. 阅读视觉规范，查看当前模板预览；按每页核心信息选择构图，记录`design_spec.md`。Markdown可作可审阅源稿，无需固定输入协议。
3. 使用 [原生制作接口](references/native-authoring.md) 的`SchoolDeck`或直接编辑模板副本。正文不能侵入页眉分割线或学校页脚。
4. 保存PPTX并检查结构、模板资产和内容；渲染全部页，检查联系表与长标题、密集文字、流程、图片和表格的大图，修复后复查。
5. 交付PPTX，以及所需PDF、预览和源文件。分别报告自动检查、渲染检查、PowerPoint/WPS实机检查；未实机打开不得声称通过。

```bash
python <skill-root>/scripts/school_pptx.py doctor
python <skill-root>/scripts/school_pptx.py inspect <deck.pptx> --out <inventory.json>
python <skill-root>/scripts/school_pptx.py check <deck.pptx> --school-template --out <check.json>
python <skill-root>/scripts/school_pptx.py preview <deck.pptx> --out-dir <empty-preview-dir>
```

优先用`scripts/school-pptx.sh`调用同一工具：解释器依次取`SCHOOL_PPTX_PYTHON`、已激活虚拟环境、安装时配置的`${XDG_CACHE_HOME:-$HOME/.cache}/presto/school-pptx/runtime/bin/python`，最后才取系统`python3`。依赖Python、python-pptx、Pillow、lxml；预览另需LibreOffice及PyMuPDF或Poppler。先在同一解释器核验依赖，缺项时报告具体缺项和解释器，不在渲染时安装软件。模板、媒体和字体均从已有本地资源读取。

安装时整目录发布。Hermes应核实当前profile实际发现的技能根，在宿主更新源仓库与活动安装，不在聊天运行时修改只读共享技能。项目产物和验证证据放在项目目录，不写入技能安装目录。
