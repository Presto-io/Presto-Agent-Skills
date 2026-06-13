// 中文字号转换函数
#import "@preview/pointless-size:0.1.2": zh

// 定义常用字体名称
#let FONT_XBS = ("FZXiaoBiaoSong-B05") // 方正小标宋
#let FONT_HEI = ("STHeiti") // 黑体
#let FONT_FS = ("STFangsong") // 仿宋
#let FONT_KAI = ("STKaiti") // 楷体
#let FONT_SONG = "STSong" // 宋体

#set text(
  lang: "zh",
  font: FONT_SONG,
  size: zh(5),
  hyphenate: false,
  tracking: -0.3pt,
  cjk-latin-spacing: auto
)

#let section-title(body) = block(above: 0pt, below: 0pt, width: 100%)[
  #set text(font: FONT_SONG, size: zh(4))
  #align(center)[#body]
]

#set document(
  title: "工业传感器安装与信号检测",
  author: "Presto",
  keywords: "教案, 实操, 教学设计",
)
#set page(
  paper: "a4",
  flipped: false,
  margin: (top: 2.54cm, bottom: 2.54cm, left: 2.58cm, right: 2.08cm)
)

#v(3.20cm)
#align(center)[#text(font: FONT_SONG, size: 22pt, weight: "bold")[教学设计方案（二）]]
#v(5.25cm)
#context {
  let cover-label-width = calc.max(
    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[课程名称：]).width,
    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[课程属性：]).width,
    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[教材名称：]).width,
    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[教学班级：]).width,
    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[计划总课时：]).width,
    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[教师姓名：]).width,
    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[使用时间：]).width,
  )
  let cover-value-width = calc.max(
    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[工业传感器安装与信号检测]).width,
    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[□基本技能课程  ☑工学一体化课程]).width,
    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[]).width,
    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[]).width,
    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[12]).width,
    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[]).width,
    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[]).width,
  ) + 0.90cm

  align(center)[
    #table(
      columns: (cover-label-width, cover-value-width),
      stroke: none,
      align: bottom,
      inset: 0pt,
      // cover-label: 课程名称
      table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-label-width, height: 1.50cm, inset: (bottom: 0.16cm))[#align(bottom)[#box(width: cover-label-width)[#grid(columns: (auto, 1fr, auto, 1fr, auto, 1fr, auto, 1fr, auto), column-gutter: 0pt, [#text(font: FONT_SONG, size: zh(4), weight: "bold")[课]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[程]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[名]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[称]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[：]])]]]], table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-value-width, height: 1.50cm, stroke: (bottom: 0.5pt), inset: (bottom: 0.16cm))[#align(center + bottom)[#text(font: FONT_SONG, size: zh(4), weight: "bold")[工业传感器安装与信号检测]]]],
      // cover-label: 课程属性
      table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-label-width, height: 1.50cm, inset: (bottom: 0.16cm))[#align(bottom)[#box(width: cover-label-width)[#grid(columns: (auto, 1fr, auto, 1fr, auto, 1fr, auto, 1fr, auto), column-gutter: 0pt, [#text(font: FONT_SONG, size: zh(4), weight: "bold")[课]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[程]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[属]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[性]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[：]])]]]], table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-value-width, height: 1.50cm, stroke: (bottom: 0.5pt), inset: (bottom: 0.16cm))[#align(center + bottom)[#text(font: FONT_SONG, size: zh(4), weight: "bold")[□基本技能课程  ☑工学一体化课程]]]],
      // cover-label: 教材名称
      table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-label-width, height: 1.50cm, inset: (bottom: 0.16cm))[#align(bottom)[#box(width: cover-label-width)[#grid(columns: (auto, 1fr, auto, 1fr, auto, 1fr, auto, 1fr, auto), column-gutter: 0pt, [#text(font: FONT_SONG, size: zh(4), weight: "bold")[教]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[材]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[名]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[称]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[：]])]]]], table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-value-width, height: 1.50cm, stroke: (bottom: 0.5pt), inset: (bottom: 0.16cm))[#align(center + bottom)[#text(font: FONT_SONG, size: zh(4), weight: "bold")[]]]],
      // cover-label: 教学班级
      table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-label-width, height: 1.50cm, inset: (bottom: 0.16cm))[#align(bottom)[#box(width: cover-label-width)[#grid(columns: (auto, 1fr, auto, 1fr, auto, 1fr, auto, 1fr, auto), column-gutter: 0pt, [#text(font: FONT_SONG, size: zh(4), weight: "bold")[教]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[学]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[班]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[级]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[：]])]]]], table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-value-width, height: 1.50cm, stroke: (bottom: 0.5pt), inset: (bottom: 0.16cm))[#align(center + bottom)[#text(font: FONT_SONG, size: zh(4), weight: "bold")[]]]],
      // cover-label: 计划总课时
      table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-label-width, height: 1.50cm, inset: (bottom: 0.16cm))[#align(bottom)[#box(width: cover-label-width)[#grid(columns: (auto, 1fr, auto, 1fr, auto, 1fr, auto, 1fr, auto, 1fr, auto), column-gutter: 0pt, [#text(font: FONT_SONG, size: zh(4), weight: "bold")[计]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[划]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[总]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[课]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[时]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[：]])]]]], table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-value-width, height: 1.50cm, stroke: (bottom: 0.5pt), inset: (bottom: 0.16cm))[#align(center + bottom)[#text(font: FONT_SONG, size: zh(4), weight: "bold")[12]]]],
      // cover-label: 教师姓名
      table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-label-width, height: 1.50cm, inset: (bottom: 0.16cm))[#align(bottom)[#box(width: cover-label-width)[#grid(columns: (auto, 1fr, auto, 1fr, auto, 1fr, auto, 1fr, auto), column-gutter: 0pt, [#text(font: FONT_SONG, size: zh(4), weight: "bold")[教]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[师]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[姓]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[名]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[：]])]]]], table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-value-width, height: 1.50cm, stroke: (bottom: 0.5pt), inset: (bottom: 0.16cm))[#align(center + bottom)[#text(font: FONT_SONG, size: zh(4), weight: "bold")[]]]],
      // cover-label: 使用时间
      table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-label-width, height: 1.50cm, inset: (bottom: 0.16cm))[#align(bottom)[#box(width: cover-label-width)[#grid(columns: (auto, 1fr, auto, 1fr, auto, 1fr, auto, 1fr, auto), column-gutter: 0pt, [#text(font: FONT_SONG, size: zh(4), weight: "bold")[使]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[用]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[时]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[间]], [], [#text(font: FONT_SONG, size: zh(4), weight: "bold")[：]])]]]], table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-value-width, height: 1.50cm, stroke: (bottom: 0.5pt), inset: (bottom: 0.16cm))[#align(center + bottom)[#text(font: FONT_SONG, size: zh(4), weight: "bold")[]]]],
    )
  ]
}

#pagebreak()

#set page(
  paper: "a4",
  flipped: false,
  margin: (top: 2.54cm, bottom: 2.54cm, left: 2.58cm, right: 2.08cm)
)

#section-title[学习任务分析]
#v(10pt)
#align(center)[
  #table(
    columns: (2.2cm, 3.2cm, 2.2cm, 2.4cm, 3.1cm, 3.24cm),
    stroke: 0.5pt,
    align: center + horizon,
    [学习任务], table.cell(colspan: 5)[电感式接近开关安装与金属件检测],
    [课时], table.cell(colspan: 2)[12], [起止日期], table.cell(colspan: 2)[],
    table.cell(colspan: 6)[*一、学习任务描述*],
    table.cell(colspan: 6, align: left + horizon)[智能分拣实训单元需要识别输送线上是否有金属工件到达指定工位。学生以设备调试小组身份接收电感式接近开关安装任务，完成任务单解读、元件识别、支架安装、三线制接线、供电检测、输出信号验证和调试记录填写，确保金属工件经过检测位置时信号稳定切换。],
    table.cell(colspan: 6)[*二、学习目标*],
    table.cell(colspan: 6, align: left + horizon)[1. 能说明电感式接近开关的检测对象、安装位置、检测距离和验收要求

2. 能识读三线制传感器接线图，区分棕色电源正极、蓝色电源负极和黑色信号线

3. 能按图完成传感器支架固定、导线处理、端子压接和线号标识

4. 能使用万用表检测 24V 供电、信号输出电压和线路通断

5. 能根据检测距离和指示灯状态调整安装位置，并填写调试记录],
    table.cell(colspan: 6)[*三、学习内容*],
    table.cell(colspan: 6, align: left + horizon)[1. 任务认知与资料查阅：阅读智能分拣单元任务单，明确金属工件到位检测的工作场景、质量标准、安全要求和交付资料

2. 元件识别与参数确认：识别电感式接近开关外观、铭牌、检测距离、供电范围、输出方式和常开常闭状态

3. 图纸识读与接线准备：识读传感器供电回路、信号回路和端子分配表，确定导线颜色、端子编号和测量点

4. 安装接线与工艺实施：完成支架固定、检测面朝向调整、导线剥削、冷压端子压接、端子接线、线缆固定和标识粘贴

5. 检测调试与记录归档：完成断电自检、通电申请、供电测量、信号输出验证、距离微调、异常排查和调试记录填写],
    table.cell(colspan: 6)[*四、学生情况分析*],
    table.cell(colspan: 6, align: left + horizon)[专业能力基础：学生已学习直流电源、常用低压电器和万用表基本测量，能够在教师提示下完成简单端子接线。



专业能力不足：部分学生对三线制传感器线色功能和信号输出测量点不够熟悉，容易只观察指示灯而忽略电压证据。



通用能力基础：学生愿意参与设备实操，能按小组分工完成工具准备、材料领取和记录填写。



通用能力不足：少数学生在支架调整和线缆整理时耐心不足，需要通过互检表强化工艺意识。



学习态度与支持重点：本任务贴近自动化岗位现场，教学中应突出安全确认、测量证据、工艺细节和记录规范。],
    table.cell(colspan: 6)[*五、学习资源*],
    table.cell(colspan: 6, inset: 0pt, stroke: none)[#table(
      columns: (7.24cm, 3.66cm, 5.44cm),
      stroke: 0.5pt,
      align: left + horizon,
      inset: 5pt,
      [工量具、设备：智能分拣实训台、24V 直流电源、电感式接近开关、传感器支架、端子排、万用表、剥线钳、压线钳、螺丝刀。], [耗材：导线、冷压端子、线号管、扎带、标签纸、绝缘胶带。], [其它：任务单、接线图、端子分配表、传感器说明书、安全操作规程、调试记录单、评价量规。],
    )],
  )
]

#pagebreak()

#set page(
  paper: "a4",
  flipped: true,
  margin: (top: 2.54cm, bottom: 2.08cm, left: 2.58cm, right: 2.54cm)
)

#section-title[教学活动设计]
#v(10pt)
#block(above: 0pt, below: 0pt)[
  #align(center)[
    #table(
      columns: (2.44cm, 5.96cm, 5.71cm, 5.61cm, 3.33cm, 1.99cm),
      stroke: 0.5pt,
      align: center + horizon,
      [*学习环节*], [*明确任务*], [*学习单元*], table.cell(colspan: 3)[*金属件到位检测要求识读*],
      [教学活动], [学习内容], [学生活动], [教师活动], [教学方法与手段], [课时分配],
      table.cell(rowspan: 1)[1.活动一：任务导入与检测点确认],      align(left)[1. 智能分拣单元金属件到位检测场景；
2. 任务单中的检测对象、安装位置、信号要求和验收标准；],      align(left)[1. 观察设备运行过程，标出金属件到达检测点的位置；
2. 阅读任务单并提取本组安装调试要求；],      align(left)[1. 展示分拣单元工作流程，说明金属件检测信号的控制作用；
2. 引导学生把任务要求转化为可检查的操作清单；],      align(center + horizon)[情境教学法、任务驱动法],      [1H],
    )
  ]
]
#block(above: 0pt, below: 0pt)[
  #align(center)[
    #table(
      columns: (2.44cm, 5.96cm, 5.71cm, 5.61cm, 3.33cm, 1.99cm),
      stroke: 0.5pt,
      align: center + horizon,
      [*学习环节*], [*制定计划*], [*学习单元*], table.cell(colspan: 3)[*三线制接线与安装方案编制*],
      [教学活动], [学习内容], [学生活动], [教师活动], [教学方法与手段], [课时分配],
      table.cell(rowspan: 1)[1.活动二：元件识别与接线图分析],      align(left)[1. 电感式接近开关铭牌参数、检测距离和线色功能；
2. 供电端、信号端、输入端和公共端的连接关系；],      align(left)[1. 查阅传感器说明书，记录型号、供电范围、输出方式和检测距离；
2. 识读接线图，绘制本组端子连接草图；],      align(left)[1. 讲解三线制接近开关工作特点和接线逻辑；
2. 检查学生接线草图，提示线色混接和测量点错误风险；],      align(center + horizon)[讲授法、图纸识读法],      [1H],
    )
  ]
]
#block(above: 0pt, below: 0pt)[
  #align(center)[
    #table(
      columns: (2.44cm, 5.96cm, 5.71cm, 5.61cm, 3.33cm, 1.99cm),
      stroke: 0.5pt,
      align: center + horizon,
      [*学习环节*], [*任务实施*], [*学习单元*], table.cell(colspan: 3)[*安装接线与通电检测*],
      [教学活动], [学习内容], [学生活动], [教师活动], [教学方法与手段], [课时分配],
      table.cell(rowspan: 1)[1.活动三：安装接线与信号验证],      align(left)[1. 支架固定、检测距离预调、端子压接、线号标识和线缆固定；
2. 供电电压检测、金属工件接近时信号输出验证和记录填写；],      align(left)[1. 按方案安装接近开关并完成导线处理、端子接线和线缆整理；
2. 申请通电后测量供电和输出电压，调整检测距离并记录结果；],      align(left)[1. 示范支架安装、端子压接和断电自检方法；
2. 巡回指导通电检测，要求学生用数据说明信号状态；],      align(center + horizon)[实操训练法、巡回指导法],      [2H],
    )
  ]
]

#pagebreak()

#set page(
  paper: "a4",
  flipped: false,
  margin: (top: 2.54cm, bottom: 2.54cm, left: 2.58cm, right: 2.08cm)
)

#section-title[学业评价]
#v(10pt)
#align(center)[
  #table(
    columns: (1.2cm, 3.2cm, 8.6cm, 3.34cm),
    stroke: 0.5pt,
    align: center + horizon,
    [序号], [考核项目], [考核细则], [考核方式],
    [1], align(center + horizon)[安全准备], align(center + horizon)[能完成断电确认、防护检查、工具仪表准备和通电申请], [过程观察],
    [2], align(center + horizon)[图纸识读], align(center + horizon)[能说明三线制接近开关线色功能和端子连接关系], [口头问答],
    [3], align(center + horizon)[安装接线], align(center + horizon)[支架牢固，导线处理、端子压接、线号标识和线缆固定符合要求], [作品检查],
    [4], align(center + horizon)[信号检测], align(center + horizon)[能使用万用表检测供电和输出电压，并根据检测距离调整安装位置], [实操考核],
    [5], align(center + horizon)[记录归档], align(center + horizon)[调试记录包含测量数据、信号状态和处理结果], [学习记录评价],
    [小结], table.cell(colspan: 3, align: left + horizon)[学生能够在安全规范约束下完成电感式接近开关安装、接线、检测和记录，达到金属件到位检测的基础调试要求。],
  )
]

#pagebreak()


#section-title[学习任务分析]
#v(10pt)
#align(center)[
  #table(
    columns: (2.2cm, 3.2cm, 2.2cm, 2.4cm, 3.1cm, 3.24cm),
    stroke: 0.5pt,
    align: center + horizon,
    [学习任务], table.cell(colspan: 5)[光电传感器安装与物料通过检测],
    [课时], table.cell(colspan: 2)[12], [起止日期], table.cell(colspan: 2)[],
    table.cell(colspan: 6)[*一、学习任务描述*],
    table.cell(colspan: 6, align: left + horizon)[智能分拣实训单元需要判断非金属物料是否通过输送带入口。学生接收光电传感器安装与调试任务，完成检测方式选择、光轴对准、灵敏度调整、抗干扰检查、输出信号测量和功能验收，使不同颜色物料通过入口时检测信号可靠变化。],
    table.cell(colspan: 6)[*二、学习目标*],
    table.cell(colspan: 6, align: left + horizon)[1. 能说明对射式、反射式和漫反射式光电传感器的适用场景

2. 能根据物料颜色、表面状态和安装空间选择检测方式

3. 能完成光电传感器支架安装、光轴对准、灵敏度初调和线缆固定

4. 能用万用表验证供电电压、信号输出和遮挡状态变化

5. 能分析误检、漏检、光轴偏移和环境光干扰等常见问题],
    table.cell(colspan: 6)[*三、学习内容*],
    table.cell(colspan: 6, align: left + horizon)[1. 检测任务分析：根据输送带入口检测需求，明确物料材质、颜色差异、通过速度、安装空间和验收标准

2. 传感器选型比较：比较对射、反射和漫反射光电传感器的检测特点、接线要求、调试难点和适用条件

3. 安装定位与光轴调整：完成支架固定、发射端与接收端对准、反光板位置确认、检测距离和检测角度调整

4. 灵敏度调试与抗干扰处理：通过样件测试调整灵敏度，检查环境光、背景反射、线缆松动和遮挡不完全带来的影响

5. 功能验证与成果说明：完成多次通过测试、信号状态记录、异常现象处理、现场整理和验收展示],
    table.cell(colspan: 6)[*四、学生情况分析*],
    table.cell(colspan: 6, align: left + horizon)[专业能力基础：学生已具备接近开关接线和电压测量经验，能理解传感器信号进入控制端的基本过程。



专业能力不足：学生对光轴对准、灵敏度旋钮调整和不同物料表面反光差异认识不足，调试时容易缺少重复验证。



通用能力基础：学生能够进行小组讨论和分工操作，愿意通过实物测试寻找参数变化规律。



通用能力不足：部分学生记录不够细致，容易只写“正常”而没有保存遮挡前后电压和现象描述。



学习态度与支持重点：教学中应鼓励学生通过多样件测试建立证据链，形成先观察、再测量、后调整的调试习惯。],
    table.cell(colspan: 6)[*五、学习资源*],
    table.cell(colspan: 6, inset: 0pt, stroke: none)[#table(
      columns: (7.06cm, 4.02cm, 5.26cm),
      stroke: 0.5pt,
      align: left + horizon,
      inset: 5pt,
      [工量具、设备：输送带实训单元、24V 直流电源、光电传感器、反光板、传感器支架、端子排、万用表、螺丝刀、内六角扳手。], [耗材：不同颜色物料块、导线、冷压端子、扎带、线号管、标签纸。], [其它：光电传感器说明书、任务单、接线图、物料测试记录表、故障排查流程卡、评价量规。],
    )],
  )
]

#pagebreak()

#set page(
  paper: "a4",
  flipped: true,
  margin: (top: 2.54cm, bottom: 2.08cm, left: 2.58cm, right: 2.54cm)
)

#section-title[教学活动设计]
#v(10pt)
#block(above: 0pt, below: 0pt)[
  #align(center)[
    #table(
      columns: (2.46cm, 5.90cm, 5.62cm, 5.74cm, 3.33cm, 1.99cm),
      stroke: 0.5pt,
      align: center + horizon,
      [*学习环节*], [*明确任务*], [*学习单元*], table.cell(colspan: 3)[*物料通过检测方案选择*],
      [教学活动], [学习内容], [学生活动], [教师活动], [教学方法与手段], [课时分配],
      table.cell(rowspan: 1)[1.活动一：检测方式比较与选型],      align(left)[1. 输送带入口物料通过检测需求；
2. 对射式、反射式和漫反射式光电传感器特点；],      align(left)[1. 观察不同物料通过入口的状态，分析检测难点；
2. 比较三类光电传感器并选择本任务实施方案；],      align(left)[1. 提供不同物料样件，引导学生分析颜色和表面状态对检测的影响；
2. 讲解不同光电检测方式的优缺点和选型依据；],      align(center + horizon)[比较分析法、任务驱动法],      [1H],
    )
  ]
]
#block(above: 0pt, below: 0pt)[
  #align(center)[
    #table(
      columns: (2.46cm, 5.90cm, 5.62cm, 5.74cm, 3.33cm, 1.99cm),
      stroke: 0.5pt,
      align: center + horizon,
      [*学习环节*], [*工作准备*], [*学习单元*], table.cell(colspan: 3)[*接线图识读与安装基准确定*],
      [教学活动], [学习内容], [学生活动], [教师活动], [教学方法与手段], [课时分配],
      table.cell(rowspan: 1)[1.活动二：接线准备与光轴基准建立],      align(left)[1. 光电传感器供电、信号输出、反光板或接收端安装基准；
2. 光轴对准、支架紧固和线缆保护要求；],      align(left)[1. 识读接线图，确认供电端子、信号端子和测量点；
2. 确定传感器与反光板或接收端的安装位置；],      align(left)[1. 讲解光轴对准方法和安装基准选择要点；
2. 审核学生安装草图并提示支架松动和遮挡不足风险；],      align(center + horizon)[图纸识读法、演示法],      [1H],
    )
  ]
]
#block(above: 0pt, below: 0pt)[
  #align(center)[
    #table(
      columns: (2.46cm, 5.90cm, 5.62cm, 5.74cm, 3.33cm, 1.99cm),
      stroke: 0.5pt,
      align: center + horizon,
      [*学习环节*], [*任务实施*], [*学习单元*], table.cell(colspan: 3)[*调试验证与异常处理*],
      [教学活动], [学习内容], [学生活动], [教师活动], [教学方法与手段], [课时分配],
      table.cell(rowspan: 1)[1.活动三：安装调试与多样件测试],      align(left)[1. 支架安装、光轴对准、灵敏度调整、遮挡测试和抗干扰检查；
2. 误检、漏检、背景反射和环境光影响的排查方法；],      align(left)[1. 完成传感器安装接线，调整光轴和灵敏度；
2. 使用不同物料进行通过测试，记录遮挡前后信号状态；],      align(left)[1. 示范灵敏度调整和遮挡测试方法，强调多次验证；
2. 设置典型异常，引导学生按流程定位原因并修正；],      align(center + horizon)[实操训练法、问题导向法],      [2H],
    )
  ]
]

#pagebreak()

#set page(
  paper: "a4",
  flipped: false,
  margin: (top: 2.54cm, bottom: 2.54cm, left: 2.58cm, right: 2.08cm)
)

#section-title[学业评价]
#v(10pt)
#align(center)[
  #table(
    columns: (1.2cm, 3.2cm, 8.6cm, 3.34cm),
    stroke: 0.5pt,
    align: center + horizon,
    [序号], [考核项目], [考核细则], [考核方式],
    [1], align(center + horizon)[检测方案选择], align(center + horizon)[能根据物料和安装空间说明光电传感器选型依据], [方案审核],
    [2], align(center + horizon)[安装定位], align(center + horizon)[支架固定可靠，光轴对准准确，线缆保护和标识符合要求], [作品检查],
    [3], align(center + horizon)[接线检测], align(center + horizon)[能按图完成接线并测量供电电压和信号输出状态], [实操考核],
    [4], align(center + horizon)[参数调试], align(center + horizon)[能调整灵敏度并完成多样件通过测试，减少误检和漏检], [过程评价],
    [5], align(center + horizon)[异常处理], align(center + horizon)[能记录异常现象、测量数据、原因判断和修正措施], [学习记录评价],
    [小结], table.cell(colspan: 3, align: left + horizon)[学生能够根据物料通过检测需求完成光电传感器选型、安装、调试和异常处理，具备初步现场检测方案验证能力。],
  )
]

#pagebreak()


#section-title[学习任务分析]
#v(10pt)
#align(center)[
  #table(
    columns: (2.2cm, 3.2cm, 2.2cm, 2.4cm, 3.1cm, 3.24cm),
    stroke: 0.5pt,
    align: center + horizon,
    [学习任务], table.cell(colspan: 5)[磁性开关安装与气缸末端位置检测],
    [课时], table.cell(colspan: 2)[12], [起止日期], table.cell(colspan: 2)[],
    table.cell(colspan: 6)[*一、学习任务描述*],
    table.cell(colspan: 6, align: left + horizon)[智能分拣实训单元的推料气缸需要反馈伸出到位和缩回到位信号。学生接收磁性开关安装与气缸末端位置检测任务，完成气缸动作观察、磁性开关槽位安装、行程端点调整、信号输出检测、线缆固定、联动测试和验收说明，保证气缸动作位置反馈准确。],
    table.cell(colspan: 6)[*二、学习目标*],
    table.cell(colspan: 6, align: left + horizon)[1. 能说明气缸伸出到位、缩回到位检测在自动化控制中的作用

2. 能识别磁性开关安装槽、指示灯、线缆和固定螺钉

3. 能根据气缸动作端点调整磁性开关位置并完成固定

4. 能检测磁性开关供电和输出信号，判断末端位置反馈是否可靠

5. 能处理开关位置偏移、线缆受力、信号抖动和动作不到位等问题],
    table.cell(colspan: 6)[*三、学习内容*],
    table.cell(colspan: 6, align: left + horizon)[1. 气缸动作与反馈需求：观察推料机构动作过程，明确伸出到位、缩回到位信号与设备节拍、安全互锁和故障判断的关系

2. 磁性开关结构识别：认识磁性开关安装槽、固定方式、线缆引出方向、指示灯状态和常见型号参数

3. 安装调节与线缆保护：根据气缸端点位置移动磁性开关，完成初步定位、紧固、防拉扯处理和标识粘贴

4. 信号检测与联动测试：检测供电电压、输出状态和动作切换点，完成伸出、缩回多次循环测试

5. 复盘交付与职业素养：整理检测数据、说明调节依据、完善验收表、归还工具材料并完成现场 6S],
    table.cell(colspan: 6)[*四、学生情况分析*],
    table.cell(colspan: 6, align: left + horizon)[专业能力基础：学生已完成接近开关和光电传感器调试，掌握基本接线、测量和记录方法。



专业能力不足：学生对气缸动作端点与磁性开关响应位置之间的关系理解不够直观，容易固定过早或过晚导致信号不稳定。



通用能力基础：学生具备小组协作基础，能在分工中完成观察、操作、测量和记录。



通用能力不足：部分学生联动测试次数不足，遇到偶发信号抖动时容易忽视线缆受力和机械位置变化。



学习态度与支持重点：教学中应强化动作观察、重复测试、证据记录和成果说明，帮助学生把单点调试提升为稳定性验证。],
    table.cell(colspan: 6)[*五、学习资源*],
    table.cell(colspan: 6, inset: 0pt, stroke: none)[#table(
      columns: (6.88cm, 3.66cm, 5.80cm),
      stroke: 0.5pt,
      align: left + horizon,
      inset: 5pt,
      [工量具、设备：推料气缸实训模块、24V 直流电源、磁性开关、端子排、万用表、螺丝刀、内六角扳手、气源处理组件。], [耗材：导线、冷压端子、扎带、线号管、标签纸、保护套管。], [其它：气动回路示意图、磁性开关说明书、接线图、联动测试记录表、安全操作规程、成果验收表。],
    )],
  )
]

#pagebreak()

#set page(
  paper: "a4",
  flipped: true,
  margin: (top: 2.54cm, bottom: 2.08cm, left: 2.58cm, right: 2.54cm)
)

#section-title[教学活动设计]
#v(10pt)
#block(above: 0pt, below: 0pt)[
  #align(center)[
    #table(
      columns: (2.47cm, 5.98cm, 5.62cm, 5.66cm, 3.32cm, 1.99cm),
      stroke: 0.5pt,
      align: center + horizon,
      [*学习环节*], [*明确任务*], [*学习单元*], table.cell(colspan: 3)[*气缸末端反馈需求分析*],
      [教学活动], [学习内容], [学生活动], [教师活动], [教学方法与手段], [课时分配],
      table.cell(rowspan: 1)[1.活动一：动作观察与信号需求确认],      align(left)[1. 推料气缸伸出到位、缩回到位检测需求；
2. 末端位置反馈与设备节拍、互锁保护和故障判断的关系；],      align(left)[1. 观察气缸动作循环，记录伸出和缩回端点位置；
2. 结合任务单说明两个末端信号的控制作用；],      align(left)[1. 演示推料机构动作过程，提示观察端点和信号灯变化；
2. 引导学生把机械位置转化为电气检测需求；],      align(center + horizon)[情境教学法、观察法],      [1H],
    )
  ]
]
#block(above: 0pt, below: 0pt)[
  #align(center)[
    #table(
      columns: (2.47cm, 5.98cm, 5.62cm, 5.66cm, 3.32cm, 1.99cm),
      stroke: 0.5pt,
      align: center + horizon,
      [*学习环节*], [*工作准备*], [*学习单元*], table.cell(colspan: 3)[*磁性开关安装位置确定*],
      [教学活动], [学习内容], [学生活动], [教师活动], [教学方法与手段], [课时分配],
      table.cell(rowspan: 1)[1.活动二：结构识别与调节方案制定],      align(left)[1. 磁性开关安装槽、指示灯、固定螺钉和线缆引出方向；
2. 动作端点、初始定位、紧固要求和线缆防拉扯措施；],      align(left)[1. 识别磁性开关结构和气缸安装槽，确定初始安装位置；
2. 编制伸出到位和缩回到位两个开关的调节步骤；],      align(left)[1. 讲解磁性开关感应原理和安装注意事项；
2. 检查学生调节方案，提醒固定过紧、线缆受力和端点偏差风险；],      align(center + horizon)[讲授法、小组合作法],      [1H],
    )
  ]
]
#block(above: 0pt, below: 0pt)[
  #align(center)[
    #table(
      columns: (2.47cm, 5.98cm, 5.62cm, 5.66cm, 3.32cm, 1.99cm),
      stroke: 0.5pt,
      align: center + horizon,
      [*学习环节*], [*任务实施*], [*学习单元*], table.cell(colspan: 3)[*末端位置调试与联动验收*],
      [教学活动], [学习内容], [学生活动], [教师活动], [教学方法与手段], [课时分配],
      table.cell(rowspan: 1)[1.活动三：安装调节、循环测试与成果交付],      align(left)[1. 磁性开关安装固定、供电与输出检测、气缸端点位置微调；
2. 多次循环测试、信号抖动排查、验收表填写和现场整理；],      align(left)[1. 安装两个磁性开关并完成接线、固定和线缆保护；
2. 进行伸出缩回循环测试，记录信号切换位置和异常处理结果；],      align(left)[1. 示范开关位置微调和联动测试方法，强调重复验证；
2. 组织成果验收，点评信号稳定性、记录完整性和现场 6S；],      align(center + horizon)[实操训练法、评价反馈法],      [2H],
    )
  ]
]

#pagebreak()

#set page(
  paper: "a4",
  flipped: false,
  margin: (top: 2.54cm, bottom: 2.54cm, left: 2.58cm, right: 2.08cm)
)

#section-title[学业评价]
#v(10pt)
#align(center)[
  #table(
    columns: (1.2cm, 3.2cm, 8.6cm, 3.34cm),
    stroke: 0.5pt,
    align: center + horizon,
    [序号], [考核项目], [考核细则], [考核方式],
    [1], align(center + horizon)[任务理解], align(center + horizon)[能说明气缸末端反馈信号的用途和验收要求], [口头问答],
    [2], align(center + horizon)[安装调节], align(center + horizon)[磁性开关位置合理，固定可靠，线缆保护和标识规范], [作品检查],
    [3], align(center + horizon)[信号检测], align(center + horizon)[能检测供电和输出状态，判断伸出到位与缩回到位信号], [实操考核],
    [4], align(center + horizon)[稳定性验证], align(center + horizon)[能完成多次循环测试并处理位置偏移或信号抖动], [过程评价],
    [5], align(center + horizon)[成果交付], align(center + horizon)[验收表、测试数据、问题处理和现场整理符合任务要求], [学习记录评价],
    [小结], table.cell(colspan: 3, align: left + horizon)[学生能够完成磁性开关安装、末端位置调试和联动验收，形成以稳定性测试支撑设备交付的基本职业能力。],
  )
]
