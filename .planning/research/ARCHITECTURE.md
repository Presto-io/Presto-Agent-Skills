# Architecture Patterns: 毕业生高级简历生成器

**Domain:** 面向电气、机电、智能制造、发电厂与新能源方向大专毕业生的离线简历生成
**Project:** Presto Agent Skills v1.19 `graduate-resume`
**Researched:** 2026-07-17
**Overall confidence:** HIGH（仓库边界和 Typst 能力均有直接依据；具体视觉主题仍须用本地样张验收）

## Recommended Architecture

新功能应是独立的 `skills/graduate-resume/`，不能把简历能力塞进既有任一文档 skill，也不能在运行时调用兄弟 skill 的脚本。采用不可逆的单向流水线：内容资料和定向规则先被解析为主题无关的规范模型，布局规划器在不接触文件系统发布逻辑的情况下冻结分页，Typst 发射器只消费冻结计划，PDF 验证通过后才由技能本地的干净交付事务发布三件套。

```text
reviewed resume.md + optional assets/photo
             |                     batch.yaml + targeting rules
             v                                  |
      schema parser + validator <----------------+
             |  CanonicalResume (theme-free, source-located)
             v
      target resolver ----> TargetedResume + qualification-gap report
             v
      theme registry ----> ThemeSpec (tokens, slots, page budget)
             v
      layout planner ----> FrozenLayoutPlan (1 or 2 A4 pages)
             v
      Typst emitter ----> candidate .typ ----> typst compile ----> candidate .pdf
             |                                                       |
             +------------ structural/PDF verifier <----------------+
                                      |
                                      v
                       clean-delivery publisher
                 current .md + .typ + .pdf / history/<seq>/
```

核心不变量：

- Markdown/YAML 表达候选人事实、可选素材和版本意图，不表达字号、坐标、颜色、照片位置或页面密度。
- 定向输出是从同一个 `CanonicalResume` 派生出的不可覆盖视图；不得把单位名称、岗位关键词或删改后的经历写回原始简历。
- 一个主题只能声明 `ThemeSpec` 和可验证的 A4 布局预算；主题不得重新解释简历字段。
- `FrozenLayoutPlan` 是分页唯一权威。Typst 发射器不得根据溢出再次拆分、缩字或换页。
- 发布层只接受通过所有验证的完整候选 bundle。失败、信号中断和未知/符号链接/部分现有 bundle 均不能触碰当前成功交付。

### Skill-Local Directory Structure

```text
skills/graduate-resume/
├── SKILL.md
├── templates/
│   ├── graduate-resume.md
│   ├── batch.yaml
│   └── themes/
│       ├── engineering-classic.yaml
│       └── engineering-compact.yaml
├── references/
│   ├── markdown-schema.md
│   ├── targeting-rules.md
│   ├── theme-contract.md
│   ├── layout-and-pagination.md
│   ├── pdf-verification.md
│   └── clean-delivery.md
├── scripts/
│   ├── graduate-resume.sh
│   └── graduate_resume/
│       ├── cli.py
│       ├── markdown_parser.py
│       ├── schema.py
│       ├── targeting.py
│       ├── themes.py
│       ├── layout_plan.py
│       ├── typst_emit.py
│       ├── pdf_verify.py
│       ├── delivery.py
│       └── verify.py
└── tests/
    ├── fixtures/
    └── test_*.py
```

主题 YAML 放在 `templates/themes/`，因为它们是受控且可复制的模板输入；schema、规则、验证细节留在 `references/`。不能新增仓库级 `shared/` 简历解析器，也不能依赖 `tiaokedan`、`gongwen` 或 `teaching-design-package` 的实现。可借鉴它们的候选目录、无变更检测和回滚语义，但须在本 skill 内实现和测试。

## Component Boundaries

| Component | Responsibility | Input / Output | Must Not Do |
|---|---|---|---|
| `SKILL.md` | 触发条件、资料整理可选模式、标准 CLI 流程、六 runtime adapter、边界声明 | 指向本 skill 的模板、参考和脚本 | 承载完整 schema、主题数值或 Python 实现 |
| Markdown parser | 解析 front matter、受限标题/列表/表格，保留源行号 | `.md` -> 语法树 | 猜测缺失事实、读取主题、输出 Typst |
| schema validator | 建立 `CanonicalResume`，验证必填字段、枚举、日期、URL、素材和 review marker | 语法树 -> 规范模型 / 稳定诊断 | 为特定公司润色或删经历 |
| target resolver | 根据明确规则筛选、排序和改写“展示文案”，生成资格缺口报告 | 规范模型 + target -> `TargetedResume` | 篡改资格事实、静默补齐硬性条件 |
| theme registry | 加载白名单主题、校验 token、页边距、槽位和预算 | theme id -> `ThemeSpec` | 从 Markdown 接受任意颜色/字体/坐标 |
| layout planner | 以 `TargetedResume + ThemeSpec` 选择模块、测量预算、冻结 1/2 页物理结构 | -> `FrozenLayoutPlan` | 写文件、动态试错 Typst、拆经历条目 |
| Typst emitter | 机械生成受控 `.typ`，将每个计划模块映射到 Typst block | 计划 -> `.typ` | 改变模块顺序或分页决策 |
| PDF verifier | 编译成功、页数、A4、文本/图像/结构证据和逻辑分页复核 | `.typ + .pdf + plan` -> evidence | 将“能打开 PDF”当成通过 |
| delivery publisher | 候选隔离、全 bundle 比较、历史归档、发布及处理 INT/TERM 回滚 | validated candidate -> current/history | 重新解析内容或重跑布局 |
| aggregate verify | 固定 gate 集、正常与故障夹具、证据重算 | skill fixtures -> pass/fail | 信任生产者自己写的 PASS 标记 |

## Shared Markdown/YAML Schema

推荐一个 Markdown 文档作为候选人事实的唯一可编辑源；YAML 只负责结构化标量、选择和引用，正文负责可读经历。YAML 不应复制正文中的项目细节。

```markdown
---
schema: graduate-resume/v1
name: 张三
headline: 电气自动化技术应届毕业生
contact:
  phone: "13800000000"
  email: "zhangsan@example.edu"
  city: 武汉
links:
  - label: GitHub
    url: https://github.com/example
education:
  school: 某职业技术学院
  major: 电气自动化技术
  degree: 大专
  graduation: 2026-06
facts:
  certifications: [低压电工作业证]
  hard_conditions: [可接受倒班]
assets:
  photo: assets/profile.jpg
---

## 求职意向

- 电气技术员
- 自动化设备维护

## 核心技能

- PLC: 西门子 S7-1200、梯形图、HMI 基础组态
- 电气: 低压配电、变频器、故障排查、安全规范

## 项目经历

### 自动化产线控制实训

2025-03 至 2025-06；组员

- 使用 S7-1200 完成输送、分拣与报警联锁控制。
- 编写调试记录并排查传感器、接线与参数问题。

## 实习经历

### 某设备公司 | 电气装配实习生

2025-07 至 2025-09

- 按图纸完成柜内元件安装、端子压接及通电前检查。
```

`CanonicalResume` 应具备稳定 ID（例如 `experience.project.automation-line-control`）和完整源位置。目标规则只引用这些 ID 或标准化 tags，不能用脆弱的字符串匹配标题。前端字段严格校验；未知字段默认失败，避免静默拼写错误。允许显式的可选值（如无照片）而不是空字符串隐式降级。

### Targeting Rule Input

每个单位/岗位放在单独、可审阅的 YAML 文件；批量清单仅引用它们。这既允许一个候选人生成多版，也让“为什么选中/省略某经历”可追溯。

```yaml
# targets/power-plant-operator.yaml
id: power-plant-operator
employer: 示例新能源电站
role: 运行值班员
required:
  all: [可接受倒班]
  any: [低压电工作业证, 高压电工作业证]
preferred_tags: [电气, 配电, 变频器, 故障排查, 安全]
section_order: [求职意向, 核心技能, 实习经历, 项目经历, 教育背景]
max_items:
  核心技能: 6
  项目经历: 2
disclose_gaps: true
```

规则引擎输出三类结果：`included`、`deprioritized`、`qualification_gaps`。`qualification_gaps` 必须显式列出未满足的硬性条件、其事实依据及“不要声称已满足”的处理。若 `required.all` 不满足，默认禁止发布该定向 PDF；可用一个显式 `--allow-gap-report-only` 只生成诊断，不生成投递件。绝不基于 AI 推断证书、设备经验或可倒班意愿。

### Theme Contract

主题是数据，不是新的 Markdown 方言。每个 `ThemeSpec` 至少固定：A4 尺寸、页边距、字体 fallback 列表、排版 token、照片槽策略、每个模块的最小/最大可容预算和允许的 1/2 页结构。示例：

```yaml
id: engineering-classic
schema_compatibility: graduate-resume/v1
page:
  size: a4
  margin_mm: {top: 13, right: 14, bottom: 13, left: 14}
  maximum_pages: 2
typography:
  body_pt: 9.3
  body_min_pt: 8.8
  heading_pt: 11.5
photo:
  mode: optional
  placement: header-right
  aspect_ratio: "3:4"
budgets:
  first_page_units: 100
  second_page_units: 104
rules:
  no_orphan_heading: true
  keep_experience_entry_together: true
```

主题新增通过 schema compatibility、主题自检、同一 canonical fixture 的回归 PDF 和布局快照验证。主题可改变呈现顺序的**槽位映射**，但不得改变定向规则的语义、字段必填性，或要求改写候选人 Markdown。

## CLI Surface and Batch Manifest

保留一个 shell wrapper，所有实际操作为零 token 的本地 CLI。AI 可选地协助把散乱材料整理到模板中，但绝不在 `validate`、`target`、`plan`、`render`、`batch` 或 `verify` 中被调用。

```bash
graduate-resume.sh example --output applicant/resume.md
graduate-resume.sh validate --input applicant/resume.md --assets applicant/assets
graduate-resume.sh target --input applicant/resume.md --target targets/power-plant-operator.yaml \
  --report build/power-plant-targeting.json
graduate-resume.sh plan --input applicant/resume.md --theme engineering-classic \
  --target targets/power-plant-operator.yaml --output build/plan.json
graduate-resume.sh render --input applicant/resume.md --theme engineering-classic \
  --target targets/power-plant-operator.yaml --out output/power-plant-operator
graduate-resume.sh batch --input applicant/resume.md --manifest batch.yaml --out output
graduate-resume.sh verify --workdir build/verify
```

```yaml
# batch.yaml
schema: graduate-resume-batch/v1
defaults:
  theme: engineering-classic
  photo: auto
jobs:
  - id: general
    target: null
    output_stem: 张三-通用简历
  - id: power-plant
    target: targets/power-plant-operator.yaml
    output_stem: 张三-新能源电站-运行值班员
    photo: none
```

批处理先验证整个 manifest、所有 target、所有主题和每个输出路径的唯一性，然后分别构建 job 的候选 bundle。默认全有或全无：任何 job 的资格、布局、Typst 或 PDF gate 失败，批次不发布任何 current 输出。若以后需要独立 job 发布，必须引入显式的 `--independent-jobs` 并为每个输出根隔离事务；v1 不应默认部分成功。

## Layout Planning and Typst Rendering

`layout_plan.py` 应生成 JSON 可投影的物理计划：每页模块顺序、各模块的条目集合、continuation 标记和测量证据。它先依据主题预算做离散选择，再用保守的中英文宽度/行数模型确认每一槽。布局不是“反复编译到看起来能放下”。

```text
Canonical sections
 -> target visibility/ranking
 -> immutable entries (heading + date/role + bullets)
 -> choose 1-page plan; otherwise choose 2-page plan
 -> reserve whole entry blocks and heading-with-first-entry pairs
 -> freeze PagePlan[1..2]
 -> emit Typst with plan page breaks and nonbreakable blocks
```

两页规则必须在 planner 和 Typst 两层同时受保护：

- 标题与其后第一个经历条目是一个不可拆单元；页末只剩标题时 planner 必须将整个单元移到下一页。
- 单个经历（机构、角色、日期、全部 bullets）是不可拆单元。它无法放进任何页面预算时，不得切开；应报告具体 entry 和建议（删减事实/选择更稀疏主题），然后非零失败。
- 允许在完整经历条目之间分页，但第二页不能从无标题的续接 body 开始。
- 先尝试 1 页；超过可读性阈值则按预定义两页分区重排，不能把正文缩到主题 `body_min_pt` 以下以伪装成一页。
- Typst 仅根据计划在模块边界插入 `pagebreak(weak: true)`，将经历外层发为 `block(breakable: false, ...)`。官方文档明确支持弱分页和不可分页 block；它们是防御层，而不是布局规划算法。

Typst 模板必须自带可查询的 metadata（schema、theme、plan hash、预计页数、每页 entry ID），以便 `typst eval` 从生成的 `.typ` 重算关键声明。编译固定使用受控 Typst 版本、受控字体目录/主题资产和可复现日期配置；不要依赖用户当前工作目录的字体发现。图片仅接受 candidate bundle 内受验证的普通文件，按主题槽位进行 contain/裁剪策略，且无照片模式需完全移除该槽，不留空白占位。

## PDF Verification and Clean Delivery

PDF 验证至少分为以下固定 gates：

| Gate | Evidence | Failure behavior |
|---|---|---|
| Schema | 规范模型和源位置诊断 | 不生成候选 Typst |
| Targeting | included/deprioritized/gaps JSON | 硬性缺口不发布定向件 |
| Theme | 主题 schema、资产和预算 | 不进入规划 |
| Plan | 1/2 页、每页完整模块、无 orphan/entry split | 不编译 |
| Typst | 非零退出、受控输入/资产、metadata query | 不发布 |
| PDF structure | 真 PDF、非空、A4、页数等于 plan | 不发布 |
| PDF content | 所有计划 entry ID/关键文字可提取，照片模式匹配 | 不发布 |
| Delivery | 精确 managed path set、字节级 no-op、history 和回滚故障夹具 | 不发布或回滚 |

对于每个 job，交付根只允许当前 `<stem>.md`、`<stem>.typ`、`<stem>.pdf` 与受控的 `sources/`、`assets/`、`history/`、`.work/`；是否需要公开 `assets/` 由 Markdown 引用决定。候选版本必须在 `.work/<run-id>/candidate/` 完整生成并最小验证。若当前 managed 相对路径集合与 candidate 相同且逐字节相同，返回成功但不创建 history。变更时将旧完整 bundle（包括仍由旧 Markdown 引用的受管资产）归档至 `history/<zero-padded-sequence>/`，再逐路径发布候选。

发布前后都 fail closed：未知文件、legacy 布局、部分 bundle、符号链接、陈旧/并发 `.work`、不安全输出 stem 都要求人工审计；不得“顺手清理”。仅承诺经测试的异常、INT、TERM 回滚，不承诺 SIGKILL、断电、文件系统损坏或跨文件强原子性。诊断、布局 JSON、target report、日志和 PDF 检查证据均留在 `.work/` 或调用方 `--workdir`，不得进入成功交付根。

## Build Order

1. **先冻结 schema 和 fixture。** 编写可读 resume Markdown、target YAML、无照片/有照片和硬性缺口夹具；验证器先于渲染器存在。
2. **建立主题契约和手工 Typst 样张。** 为第一个主题先制作可接受的 1 页和 2 页 A4 Typst/PDF 参考面，再把 token、槽位和预算固化到 `ThemeSpec`。
3. **实现 schema、target resolver 与报告。** 用稳定 ID 和源位置做 deterministic 资格检查；确保纯 CLI 可在没有网络/API key 下运行。
4. **实现冻结布局计划。** 以 fixture 验证全部无孤立标题、无拆经历、可读性下限、1/2 页边界和不可容纳失败。
5. **实现 Typst emitter 与 PDF gates。** emitter 只读计划；对 Typst metadata、PDF 页数/A4/文本和图片模式建立证据。
6. **接入候选发布、批处理和故障测试。** 将单 job 交付正确性闭合后再实现 atomic-by-default 批量预检和发布。
7. **压缩 canonical 文档并补齐六 runtime adapter。** 入口保持简洁，细节下沉 `references/`；OpenClaw 和 Hermes 必须有安装期脚本回退验证。

## Anti-Patterns to Avoid

### Theme-Specific Markdown

**What:** 在 Markdown 加 `photo-left`、`font-size`、`two-column`、x/y 坐标，或为每个主题复制一份资料。

**Why bad:** 新主题迫使重写候选人事实，直接违反 v1.19 shared-schema discipline。

**Instead:** content IDs + `ThemeSpec` 槽位与预算；照片仅是候选人素材引用和 job 选择。

### Render-Time Pagination

**What:** Typst emitter 发现溢出后自行缩字、删 bullet 或插入换页。

**Why bad:** 物理结果不可预测，且无法给出“哪条经历为何失败”的稳定诊断。

**Instead:** 先生成可审计 `FrozenLayoutPlan`；emitter 机械执行，PDF gate 检查是否偏离。

### Prompt-in-the-Loop Batch Generation

**What:** 每一公司版本都让模型重新选择经历、判断资格或生成文案。

**Why bad:** 不能零 token、不可复现，也容易凭空满足硬性条件。

**Instead:** 资料整理是明确可选的前置互动；一旦成为标准化 Markdown，target YAML 和 CLI 是唯一生成路径。

### Partial Success Delivery

**What:** 批量 5 个版本中 4 个发布，1 个失败却返回成功，或失败时覆盖旧 PDF。

**Why bad:** 投递集合无法审阅，且会污染上次已验证结果。

**Instead:** v1 预检全部 job 并默认 batch transaction；单 job 只在其完整 candidate 的验证通过后发布。

### Cross-Skill Runtime Reuse

**What:** `graduate-resume.sh` source/call 既有 skill 的 shell functions 或 Python modules。

**Why bad:** 安装一个目录不再可用，命令表面稳定但实际耦合，且 future clean-delivery 改动会跨 skill 回归。

**Instead:** 移植小而明确的思想和测试语义，保留 skill-local `delivery.py` / `delivery.sh`，只共享文档级约定。

## Scalability Considerations

| Concern | 100 candidates / local use | 10K candidates / batch service | 1M candidates / product scale |
|---|---|---|---|
| Parsing and targeting | 单进程 CLI、每份独立模型 | 并行 worker，锁定 schema/target/theme 版本 | 版本化规则服务和不可变输入存储 |
| Rendering | 本地 Typst 子进程、每 job 临时目录 | 受限 worker pool、字体/主题镜像固定 | 隔离渲染队列、资源配额、可观测性 |
| Assets | 本地 `assets/` 和 no-follow 校验 | 内容哈希缓存，仍复制进 candidate | 对象存储和签名/病毒扫描 |
| Delivery/history | 目录级 current/history | 每候选人输出根和保留策略 | 数据库版本索引 + 不可变 artifact store |

v1.19 只需第一列。不要为了未来服务化而引入数据库、HTTP API、任务队列或在线账户；这些都会破坏离线、单技能、可复制的目标。

## Sources

- [项目 v1.19 约束与目标](../PROJECT.md)（HIGH，仓库一手需求）：shared schema、纯 CLI、两页 fail-closed、clean delivery 边界。
- [Typst `pagebreak` 官方文档](https://typst.app/docs/reference/layout/pagebreak/)（HIGH）：`weak` 分页行为。
- [Typst `block` 官方文档](https://typst.app/docs/reference/layout/block/)（HIGH）：`breakable: false` 可防止模块跨页拆分。
- [Typst `layout` 官方文档](https://typst.app/docs/reference/layout/layout/)（HIGH）：可在 layout context 获取剩余空间；本设计选择先行规划而非把它当作动态溢出修补。
- [Typst `query` 官方文档](https://typst.app/docs/reference/introspection/query/)（HIGH）：`typst eval` 可提取 metadata，用于验证生成源的声明。
- [Typst CLI 变更记录](https://typst.app/docs/changelog/0.10.0/)（MEDIUM）：在手工设置文档日期时 PDF 可字节重现；实际锁定版本后需在 phase fixture 验证。

## Research Gaps

- 首个主题的中文/英文混排字体可用性、精确行高和视觉密度无法只靠文档推断，必须在 Phase 主题样张中以本机 Typst/PDF 人工验收和自动页数证据锁定。
- PDF 文本提取工具和图片检测的跨平台稳定组合尚未在仓库确认；Phase 验证需选择已安装工具并用真实/损坏 PDF 夹具证明其行为。
- “硬性条件”的默认阻断规则需由产品需求明确哪些条件属于 `required.all`、哪些仅提示；当前架构按安全默认阻断定向投递件设计。
