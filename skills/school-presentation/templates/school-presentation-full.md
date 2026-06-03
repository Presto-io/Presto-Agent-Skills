---
template: "school-presentation"
title: "智能制造实训基地建设汇报"
subtitle: ""
school: "西安技师学院 / 西电机电学院"
department: "电气工程系"
author: "课程建设团队"
date: "2026-05-31"
cover_location: "智能制造实训中心"
page_ratio: "16:9"
max_output_mb: 50
---

## Section: 建设背景

### Slide: 智能制造实训基地建设汇报

<!-- slide
layout: cover
intent: establish school identity and topic
split: auto
-->
面向工学一体化课程、竞赛训练和企业真实任务，建设可展示、可训练、可复盘的智能制造实训基地。

::: notes
开场页保留校徽、校名和蓝绿色视觉识别，避免泛化模板感。
:::

### Slide: 建设目标

<!-- slide
layout: auto
intent: summarize the core goals before details
split: auto
-->

::: warning
若源材料没有明确经费、工位数或设备型号，不要在正式汇报中补写具体数字。
:::

- 建成“课程教学、技能训练、竞赛备赛、企业服务”四位一体的实训空间。
- 形成从低压电器识别、控制线路安装到 PLC 联调的连续学习任务。
- 用过程数据支撑教学诊改，保留学生作品、评价记录和设备状态。
- 输出可复用课件、工作页、评价表和项目化案例。

## Section: 教学内容与资源

### Slide: 课程链路与公式

<!-- slide
layout: auto
intent: show technical teaching content with formulas
split: auto
-->

电气控制线路学习从元件识别进入控制逻辑，再进入故障排查。基础计算仍保留在逻辑页中，渲染器负责视觉呈现。

$$U = I \times R$$

$$P = \sqrt{3} \times U \times I \times \cos\varphi$$

#### 讲解重点

- 电压、电流、功率与安全载流量的关系。
- 主电路与控制电路的分工。
- 测量前先判断断电、验电和表笔档位。

### Slide: 建设任务表

<!-- slide
layout: table
intent: demonstrate table handling and readable typography
split: auto
-->

| 模块 | 建设内容 | 验收方式 | 责任主体 |
|---|---|---|---|
| 基础工位 | 低压电器识别、安装、检测 | 工位照片与点检表 | 教学团队 |
| 线路安装 | 点动、自锁、正反转、星三角 | 学生作品与通电记录 | 任课教师 |
| PLC 联调 | I/O 分配、程序下载、联机调试 | 运行视频与评分表 | 实训管理员 |
| 故障排查 | 断路、短路、互锁异常、元件失效 | 排故报告 | 学生小组 |
| 资源沉淀 | 工作页、微课、评价量表 | 资源包清单 | 课程负责人 |

### Slide: 进度与资源投入

<!-- slide
layout: chart
intent: demonstrate chart rendering from Markdown source
split: auto
-->

```chart
基础工位: 80
线路安装: 68
PLC 联调: 52
故障排查: 40
资源沉淀: 74
```

图表数据保留在 Markdown fenced block 中，便于 review 和版本比较。

### Slide: 图右文左示例

<!-- slide
layout: media-right
intent: demonstrate image on the right with explanatory text on the left
split: false
-->

图片默认按原始比例 contain 放置，不裁切用户照片。右侧图片保留完整画面，左侧文字用于说明场景、观察点和汇报结论。

![风景图：用于检验横向图片 contain 效果](media/风景.webp)

- 适合展示实训环境、校园空间或项目现场。
- 文字区保留足够宽度，便于放置三到五条讲解重点。

### Slide: 图左文右示例

<!-- slide
layout: media-left
intent: demonstrate image on the left with explanatory text on the right
split: false
-->

![猫猫图：用于检验方形或近方形图片效果](media/猫猫.png)

左侧图片承载视觉焦点，右侧用于放置结论、说明或评审意见。

- 适合人物、作品、设备局部或成果照片。
- 图片不会拉伸变形，说明文字与图片保持同屏阅读。

### Slide: 居中图片与底部说明

<!-- slide
layout: media-center
intent: demonstrate centered image with caption and bottom explanation
split: false
-->

![AI 人像：用于检验竖向图片居中展示效果](media/AI人像.jpg)

底部说明可以补充图片来源、使用边界、教学观察点或展示结论。

### Slide: 双图对比

<!-- slide
layout: media-compare
intent: demonstrate two image comparison
split: false
-->

![横向场景图](media/风景.webp)

![竖向人像图](media/AI人像.jpg)

### Slide: 图片与图表对比

<!-- slide
layout: media-chart
intent: compare visual evidence with chart data
split: false
-->

![猫猫图：左侧视觉材料](media/猫猫.png)

```chart
画面完整度: 92
主体清晰度: 88
色彩稳定性: 76
汇报适配度: 84
```

::: notes
本组页面用于验证不同图片比例与图文组合方式的视觉效果。
:::

## Section: 能力审阅

### Slide: 功能矩阵

<!-- slide
layout: table
intent: summarize what the renderer can do
split: auto
-->

| 功能点 | 当前表现 | 审阅关注 |
|---|---|---|
| 封面 | 标题、副标题、学校信息、汇报人、日期、可选字段 | 重点看封面排版是否拥挤 |
| 章节页 | 自动章节分组和逻辑页编号 | 看章节标题是否清楚 |
| 段落与列表 | 普通文本、加粗、项目符号 | 看字号和行距是否够远看 |
| 表格 | 表头、行斑马纹、长表拆页 | 看列宽与溢出是否稳定 |
| 图表 | Markdown fenced chart | 看比例条和数字对齐 |
| 公式 | `\sqrt{}`、`\times`、`\cos`、上下标 | 看根号、斜体、函数正体 |
| 图片 | contain 等比放置 | 看横图、竖图、方图是否都不变形 |
| 视频 | 超大或缺失时 fallback | 看 fallback 是否清楚提示 |
| 绝对路径媒体 | 支持存在的本地绝对路径 | 看路径解析是否稳定 |
| 缩略图 | 左侧 rail 与右侧预览一致 | 看缩略图是否乱掉 |
| 播放态 | 全屏播放、悬浮工具条、键盘导航 | 看控制条是否干净 |
| 预览 / 概览 | 工作区、概览、播放三态 | 看切换是否流畅 |
| 有序揭示 | `order` 优先级控制播放顺序 | 看非视觉顺序和同序号同时出现 |
| 答案遮罩 | 填空、判断、表格答案在播放态遮住 | 看遮罩是否不泄露提示文字 |
| 正确项强调 | 选择题选项常显，正确项用强调出现 | 看下划线在打印态是否仍可见 |

### Slide: 风险矩阵

<!-- slide
layout: table
intent: show likely bugs and review points
split: auto
-->

| 风险点 | 典型表现 | 你该看什么 |
|---|---|---|
| 公式过简 | 根号像普通字符、函数看着像文本 | 数学排版是否像真正公式 |
| 长表过密 | 表格列太窄、分页断裂不自然 | 是否需要再拆表或缩字 |
| 长文过长 | 一个逻辑页拆成多物理页 | 页码和内容顺序是否正确 |
| 图文拥挤 | 图片和说明抢空间 | 是否需要换版式 |
| 图像比例异常 | 竖图被压扁或横图显得过小 | contain 是否真的保比例 |
| 媒体缺失 | 只显示 fallback 卡片 | 缺失信息是否可读 |
| 视频过大 | fallback 而不是强塞进 HTML | 是否记录了外链或提示 |
| 小屏布局 | 侧栏太挤、正文太小 | 是否需要再调响应式字号 |
| 播放工具条 | 遮挡正文或看起来太重 | 浮窗是否轻一点 |
| 绝对路径媒体 | 路径不可移植 | 是否只在本机示例中使用 |

### Slide: 媒体 fallback 与错误输入

<!-- slide
layout: content
intent: show current fallback behavior for broken media
split: false
-->

下面这页故意放缺失媒体，用来观察 fallback 是否够明确。

![缺失图片示例](media/this-file-does-not-exist.png)

![video:缺失视频示例](media/this-video-does-not-exist.mp4)

### Slide: 强调块示例

<!-- slide
layout: content
intent: demonstrate GitHub-style alert blocks
split: false
-->

::: info
这是信息块，用于放背景说明或审阅提示。
:::

::: tip
这是提示块，用于放建议、做法或下一步动作。
:::

::: warning
这是警告块，用于放边界条件或需要注意的事项。
:::

::: error
这是错误块，用于放风险、异常或不应继续的情况。
:::

## Section: 课堂揭示与答案遮罩

### Slide: 填空题与公式答案遮罩

<!-- slide
layout: content
intent: demonstrate answer masks for blanks and formulas
split: auto
-->

三相功率计算公式为：

$$P = {{mask order=1}}\sqrt{3}{{/mask}} \times U \times I \times {{mask order=2}}\cos\varphi{{/mask}}$$

两个答案按 `order` 依次揭开。遮罩不显示“答案”“点击揭示”或“步骤 1/3”等提示文字。

::: mask order=3
$$P = \sqrt{3} \times U \times I \times \cos\varphi$$
:::

### Slide: 判断题答案与依据遮罩

<!-- slide
layout: content
intent: demonstrate judgement answer reveal
split: auto
-->

题干：通电前可以先试车，再检查保护接地。

::: mask order=1
判断：错误。
:::

::: mask order=2
依据：通电前必须先完成绝缘测试、保护接地检查和急停按钮测试。
:::

### Slide: 选择题正确项强调

<!-- slide
layout: content
intent: demonstrate visible options with emphasized correct answers
split: auto
-->

哪几项属于通电前检查？

- A. 作品拍照归档
- {{emphasis order=1}}B. 绝缘测试{{/emphasis}}
- {{emphasis order=1}}C. 保护接地检查{{/emphasis}}
- {{emphasis order=2}}D. 急停按钮测试{{/emphasis}}

选择题直接展示所有选项，不用遮罩；播放时只把正确项逐步变成强调状态。默认强调保留下划线，便于打印或静态审阅。

### Slide: Reveal 可以包住常见块

<!-- slide
layout: content
intent: demonstrate block reveal across common Markdown content
split: auto
-->

::: reveal order=1
- 先观察设备状态灯。
- 再检查 I/O 分配和端子对应关系。
:::

::: reveal order=2
$$U = I \times R$$
:::

::: reveal order=3
```chart
观察状态灯: 70
核对端子: 82
联机调试: 64
```
:::

::: reveal order=4
说明段落也可以作为一个整体 reveal；如果内容太多，渲染器继续按物理页拆分，不靠隐藏内容硬塞进一页。
:::

### Slide: 多个答案按 order 推进

<!-- slide
layout: table
intent: demonstrate multiple table answers by order
split: auto
-->

| 检测点 | 现象 | 答案 |
|---|---|---|
| 线圈 A1-A2 | 阻值无穷大 | {{mask order=1}}线圈断路{{/mask}} |
| 互锁触点 | 两路同时吸合 | {{mask order=2}}互锁失效{{/mask}} |
| 急停回路 | 按下后仍可启动 | {{mask order=2}}急停回路异常{{/mask}} |
| 保护接地 | 接地电阻异常 | {{mask order=3}}接地不可靠{{/mask}} |

### Slide: 非视觉顺序与小数优先级

<!-- slide
layout: content
intent: demonstrate non-visual order and decimal priorities
split: auto
-->

下面四个区域的播放顺序不按视觉位置，而按 `order` 数字。小数优先级会在 manifest 中归一成连续步骤。

::: mask order=3
左上：第三步显示。
:::

::: mask order=1
右上：第一步显示。
:::

::: mask order=2.1
右下：第二步后插入显示。
:::

::: mask order=2.55
左下：插入优先级会排在 2.1 和 3 之间。
:::

## Section: 推进与验收

### Slide: 过长内容自动拆页示例

<!-- slide
layout: content
intent: prove logical slide to physical page splitting
split: auto
-->

以下清单故意超过单页建议容量，用于验证一个 Markdown 逻辑页可以拆为多个 HTML 物理页。

- 入口处张贴安全告知和实训室管理制度。
- 每个工位配备工具清单、元件盒、线槽、号码管和端子标识。
- 学生先完成电路识读，再领取元件，最后进入接线操作。
- 接线前必须进行元件质量检测，记录常开、常闭和线圈阻值。
- 教师巡回检查端子压接、线号方向、导线弯曲半径和线槽余量。
- 通电前完成绝缘测试、保护接地检查和急停按钮测试。
- 通电后先空载试车，再进入带负载动作观察。
- 故障排查环节要求学生说明判断路径，而不是只给出故障点。
- 小组展示必须包含作品照片、问题清单、整改措施和复测结论。
- 课后归档保留工作页、评分表、设备点检表和过程照片。
- 课程团队每两周复盘一次典型错误，更新下一轮教学案例。
- 企业任务引入前必须完成风险评估和材料替换说明。
- 竞赛训练材料与常规教学材料分开归档，避免评价标准混用。
- 新设备上线必须同步补写操作说明、维护周期和常见故障库。

### Slide: 收束

<!-- slide
layout: closing
intent: close with action-oriented conclusion
split: auto
-->
