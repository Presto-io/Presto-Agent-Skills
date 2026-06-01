---
template: "school-presentation"
title: "智能制造实训基地建设汇报"
subtitle: "Markdown 逻辑页到学校风格 HTML 演示文稿"
school: "西安技师学院 / 西电机电学院"
author: "电气工程系"
date: "2026-05-31"
page_ratio: "16:9"
max_output_mb: 50
---

## Slide: 智能制造实训基地建设汇报

<!-- slide
layout: cover
intent: establish school identity and topic
split: auto
-->
面向工学一体化课程、竞赛训练和企业真实任务，建设可展示、可训练、可复盘的智能制造实训基地。

::: notes
开场页保留校徽、校名和蓝绿色视觉识别，避免泛化模板感。
:::

## Slide: 建设目标

<!-- slide
layout: auto
intent: summarize the core goals before details
split: auto
-->

- 建成“课程教学、技能训练、竞赛备赛、企业服务”四位一体的实训空间。
- 形成从低压电器识别、控制线路安装到 PLC 联调的连续学习任务。
- 用过程数据支撑教学诊改，保留学生作品、评价记录和设备状态。
- 输出可复用课件、工作页、评价表和项目化案例。

::: warning
若源材料没有明确经费、工位数或设备型号，不要在正式汇报中补写具体数字。
:::

## Slide: 课程链路与公式

<!-- slide
layout: auto
intent: show technical teaching content with formulas
split: auto
-->

电气控制线路学习从元件识别进入控制逻辑，再进入故障排查。基础计算仍保留在逻辑页中，渲染器负责视觉呈现。

$$U = I \times R$$

$$P = \sqrt{3} \times U \times I \times \cos\varphi$$

### 讲解重点

- 电压、电流、功率与安全载流量的关系。
- 主电路与控制电路的分工。
- 测量前先判断断电、验电和表笔档位。

## Slide: 建设任务表

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

## Slide: 进度与资源投入

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

## Slide: 图片与视频材料

<!-- slide
layout: media-right
intent: demonstrate contain images and large-video fallback
split: auto
-->

图片默认按原始比例 contain 放置，不裁切用户照片。

![学校页脚横幅](references/identity/images/body-page-footer.png)

![video:设备联调演示](media/device-debug-demo.mp4)

::: notes
若视频不存在或会导致 HTML 超过 50 MB，渲染器输出 fallback 卡片并在 manifest 中记录。
:::

## Slide: 过长内容自动拆页示例

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

## Slide: 收束

<!-- slide
layout: closing
intent: close with action-oriented conclusion
split: auto
-->
