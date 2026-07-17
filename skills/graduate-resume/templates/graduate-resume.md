---
candidate:
  name: "张三"
  status: verified
  headline: "电气自动化技术应届毕业生"
  summary: "熟悉 PLC 接线与调试、低压配电基础、CAD 制图和常用办公软件，具备校内项目与实训经验。"
  contact:
    phone: "13800000000"
    email: "zhangsan@example.com"
    city: "江苏南京"
  directions:
    - "电气技术员"
    - "设备维护"
    - "新能源运维"
education:
  - id: edu-001
    status: verified
    school: "某职业技术学院"
    major: "电气自动化技术"
    degree: "大专"
    start: "2023-09"
    end: "2026-06"
skills:
  - id: skill-automation
    status: verified
    group: "自动化"
    items:
      - "PLC 基础编程"
      - "继电控制"
      - "电气识图"
certificates:
  - id: cert-electrician-001
    status: pending
    name: "低压电工证"
    note: "待补证书编号或取得状态"
projects:
  - id: project-plc-001
    status: verified
    title: "PLC 控制输送线实训项目"
    role: "接线与程序调试"
    outcomes:
      - "完成启停、急停和故障报警逻辑"
training:
  - id: training-substation-001
    status: verified
    title: "变配电综合实训"
    summary: "参与电气柜识图、元件识别和规范接线训练。"
experience: []
targets:
  - id: target-grid-001
    company: "某电力设备公司"
    role: "电气技术员"
    source: "校园招聘公告"
    as_of: "2026-07-17"
    confirmed: true
    requirements:
      - "接受应届毕业生"
photo:
  status: pending
  path: ""
  confirmed_by_user: false
preferences:
  theme: "稳健通用型"
  preferred_pages: auto
  photo_mode: auto
---

# 复核说明

- 这个模板默认是“待复核草稿”，因为示例里故意保留了 `pending` 证书和照片状态；直接运行 `validate` 预期不会通过。
- 先把所有 `pending` 条目标记清楚，再决定是否进入最终生成。
- 若暂时没有照片，请先向用户追问一次；只有用户明确没有时，才把 `photo.status` 改为 `declined`。
- 若不做定向，请在确认后清空 `targets` 并记录为通用版。
