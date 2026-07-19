# Phase 47: 受控主题、照片与冻结布局 - Context

**Gathered:** 2026-07-19
**Status:** Rework required before planning

<domain>
## Phase Boundary

本次 Phase 47 gap-closure 的目标不是让 PDF 可打开，而是让同一份已核实资料在三种主题下成为可直接投递的中文毕业生简历。本次只调整冻结布局、Typst 发射结构、三主题视觉 token 和视觉回归样张；不改变 canonical Markdown 事实、定向筛选规则、PDF 交付事务、主题名称或照片安全边界。

</domain>

<decisions>
## Implementation Decisions

### 统一中文信息结构
- **D-01:** 所有主题按固定中文栏目呈现：基本信息、教育经历、专业技能、证书与资格、项目经历、实训经历、相关经历。无内容模块不渲染，也不预留空槽。
- **D-02:** 姓名、求职标题、个人概述在页首形成清晰主次；栏目、字段标签和叙述均使用中文。英文只保留 PLC、AutoCAD 等必要技术名词。
- **D-03:** 保持 `graduate-resume.md` 为唯一可编辑事实源。主题、页数、照片版和无照片版均从同一事实源派生，不改变事实、模块语义、稳定 ID 或目标筛选结果。

### 条目视觉块与内容发射
- **D-04:** 每一条教育、项目、实训和经历必须发射为一个完整、不可跨页的视觉块：首行承载标题，必要时同行放置单位、角色或时间；后续行承载自然中文概述与紧凑成果项目符号。
- **D-05:** 旧的逐字段串接和连续重复前缀方案失效。不得将同一事实拆成“项目：标题”“项目：角色”“项目概述：……”等重复行，也不得重复学校、技能方向或证书名称。
- **D-06:** 模块标题、条目标题、角色/单位/时间、概述与成果必须由结构化 Typst 发射接口分别表达；不能靠把字段拼为一段纯文本再由模板猜测排版。
- **D-07:** 模块和条目视觉上均不可跨页。页面末尾允许合理留白，但不得产生大面积无内容空白、孤立标题、无标题续接、文字裁切或事实被隐藏/删除来凑版。

### 冻结分页与照片
- **D-08:** 1 页资料必须紧凑完整，不因模板预留造成大面积空白。完整压力样张固定为 2 页。
- **D-09:** 两页固定阅读顺序：第一页优先放基本信息、教育经历、专业技能、证书与资格；第二页放项目经历、实训经历和相关经历。分页器只能在不改变事实与模块语义的前提下进行受限重排。
- **D-10:** 照片继续使用既有受控本地资产、`contain`、禁止裁切/拉伸和最大普通 2 寸边界；有照片不得挤压姓名、求职标题或核心信息。
- **D-11:** 无照片时移除照片槽位及其装饰并自然重排，不得留下空白框；本次不改变现有照片解析、安全读取或路径边界。

### 三主题的可见定位
- **D-12:** `保守稳妥` 固定为单栏、黑灰主色、细分隔线和最高信息密度，面向国企、制造业和传统技术岗位；强调秩序、可扫描性和正式感。
- **D-13:** `现代简洁` 固定为单栏或弱双栏、深色正文与低饱和青绿色强调，克制而清晰的页首信息带，依靠间距和字号建立层级，不使用重边框；面向一般技术岗和校园招聘。
- **D-14:** `个性设计` 可使用更强的左侧信息栏或色块，但正文保持高可读性；强调色只服务标题、关键技能和页首，不覆盖正文阅读；面向展示型技术岗，不能像海报或作品集。
- **D-15:** 三主题必须在分栏、页首、标题体系、强调色和信息密度上有一眼可辨的差异；禁止只改色线、背景色或其他单一 token。

### 固定视觉回归
- **D-16:** `fixtures/layout/pressure-two-pages.md` 是完整两页固定视觉样张；三主题必须各生成真实 PDF 和 PNG。
- **D-17:** 人工和自动门禁必须证明：所有栏目为中文；无字段前缀重复；每条项目/经历完整成块；无异常大面积空白、孤立标题、跨页断裂或裁切；无中文字体 fallback/乱码；三主题事实完全一致但一眼可分辨；PDF 稳定为 A4 的 1/2 页规则。
- **D-18:** 不引入在线字体、网络素材、系统字体 fallback 或新的运行时依赖；不把 Phase 49 的聚合验证、跨 runtime 或 UAT 混入本次返工。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 范围与需求
- `.planning/ROADMAP.md` - Phase 47 的目标、THEME-01..05 成功标准，以及与 Phase 48/49 的边界。
- `.planning/REQUIREMENTS.md` - THEME-01..05 的正式需求映射。
- `.planning/PROJECT.md` - v1.19 的 Markdown-first、离线、可打印中文毕业生简历目标。
- `.planning/phases/47-controlled-themes-photo-frozen-layout/47-UI-SPEC.md` - 已有主题视觉 token、字体、照片和 A4 基线；与本次决定冲突时以本 CONTEXT.md 为准并在重规划中修订。

### 资料与渲染契约
- `skills/graduate-resume/SKILL.md` - canonical skill 及运行时中立工作流。
- `skills/graduate-resume/references/schema-and-review-contract.md` - 不可改动的唯一事实源、照片和 target contract。
- `skills/graduate-resume/scripts/graduate_resume_layout.py` - 当前冻结计划、容器投影和分页逻辑；返工需替换字段串接的视觉投影。
- `skills/graduate-resume/scripts/graduate_resume_typst.py` - 当前 Typst 发射结构；返工需以结构化模块/条目发射替代纯文本字段拼接。
- `skills/graduate-resume/templates/resume-themes.typ` - 三主题视觉模板与照片槽位；返工需实现可见主题差异。
- `skills/graduate-resume/scripts/graduate_resume_pdf_gate.py` - PDF/PNG 实物门禁，必须扩展为本次视觉结构的可验证断言。
- `skills/graduate-resume/scripts/test_layout_fixtures.py` - 固定样张矩阵与真实 Typst/PDF/PNG 回归入口。
- `skills/graduate-resume/fixtures/layout/pressure-two-pages.md` - 三主题完整两页视觉回归样张。

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `FrozenResumePlan`、`PagePlan`、安全照片 resolver、受控字体 manifest 与真实 PDF/PNG 编译路径已存在，必须保留并继续作为冻结计划和实物门禁的基础。
- `THEME_SPECS` 已固定三个 key、中文名称和照片策略；只可调整视觉 token 与布局实现，不能改变主题名称或照片安全策略。

### Established Patterns
- 当前 `project_containers()` 把字段预格式化为带标签文本，`graduate_resume_typst.py` 的 `_container_text()` 再拼接成纯文本。这正是重复前缀和条目结构缺失的根因，返工必须以保留字段语义的结构化视觉模型替代。
- 当前 `list-entry` 已以 `breakable: false` 保护条目原子性；返工必须保留该保护并将模块标题与条目块共同纳入冻结分页预算。

### Integration Points
- 返工后的冻结计划仍由 Phase 48 的 layout feedback 消费，因此不可改变 canonical facts、target selection、正式交付或命令行为。
- `test_layout_fixtures.py` 已对 `pressure-two-pages.md` 的三个主题生成真实 PDF/PNG，是扩展视觉回归的唯一 Phase 47 验收入口。

</code_context>

<specifics>
## Specific Ideas

- 目标是“可直接投递的中文毕业生简历”，不是仅语法正确或能打开的 PDF。
- 三主题要像不同、职业化的简历模板，而不是相同版式换颜色。
- 所有主题必须保留完全相同的事实和语义，差异只来自冻结布局与视觉 token。

</specifics>

<deferred>
## Deferred Ideas

- Phase 49 的聚合验证、六 runtime、跨环境字体 UAT 与人工发布验收保持在原阶段，不得迁入本次返工。
- canonical Markdown schema、目标定向、PDF 三件套发布事务和照片安全模型保持不变；任何需要修改这些面的工作属于其他阶段。

</deferred>

---

*Phase: 47-controlled-themes-photo-frozen-layout*
*Context gathered: 2026-07-19*
