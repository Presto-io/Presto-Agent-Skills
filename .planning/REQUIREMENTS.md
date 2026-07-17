# Requirements: Presto Agent Skills v1.19

**Defined:** 2026-07-17
**Core Value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## v1.19 Requirements

### Resume Contract

- [ ] **SCHEMA-01**: 用户可用一份主题无关的 Markdown/YAML 简历资料表达电气、机电、智能制造、发电厂和新能源方向大专毕业生的已核实个人信息、教育、技能、证书、项目、实训和经历。
- [ ] **SCHEMA-02**: CLI 能校验受限 schema、稳定事实 ID、必填资料、待确认标记、未知字段和重复事实，并拒绝不可信的最终投递件。
- [ ] **SCHEMA-03**: 用户可在可选 AI 整理模式中从零散材料得到待审阅的标准资料草稿；`validate`、`target`、`plan`、`render`、`batch` 和 `verify` 全程不调用 AI、不联网且不消耗 token。
- [ ] **SCHEMA-04**: 用户可提供一个或多个单位、岗位及当次招聘信息；未提供时 CLI/skill 先询问一次，明确不提供后生成通用版。

### Themes And Layout

- [ ] **THEME-01**: CLI 支持技术技能型、项目实践型、稳健通用型三个初始主题，并允许通过 Markdown YAML 的主题参数在不改写资料 schema 的情况下切换主题。
- [ ] **THEME-02**: 每个主题可支持带照片与无照片布局；无照片时移除照片区域，不保留空占位，且只使用学生明确提供的本地照片。
- [ ] **THEME-03**: CLI 默认自动选择 1 页或 2 页 A4，也支持用户强制页数；输出必须在主题可读性阈值内收敛到指定页数，不能截断内容或产生第 3 页。
- [ ] **THEME-04**: 两页输出不出现孤立标题、无标题续接内容或被拆开的项目、实训、经历、职责和成果；无法满足布局与可读性约束时必须失败关闭并说明原因。
- [ ] **THEME-05**: 对内容不足的页面，CLI 只可重排或扩展已有材料可支撑的表达及主题密度，不能虚构经历、证书、成果或数据。

### Targeting And Delivery

- [ ] **TARGET-01**: CLI 能从同一份已核实资料生成一份通用版，以及每个“单位 + 岗位”一份独立定向版；定向只允许选择、排序和强调已核实事实。
- [ ] **TARGET-02**: CLI 对用户提供的岗位硬条件生成透明的满足、缺口、未知或不适用提示；有缺口时仍允许按用户决定生成定向版，但简历不得暗示已符合。
- [ ] **TARGET-03**: 每个版本的 YAML 记录实际主题、页数、照片模式、目标单位和岗位，以及本次定向信息的来源/日期；招聘信息不由技能抓取、猜测或声称实时。
- [ ] **DELIVERY-01**: 每个成功版本同 stem 输出 Markdown、Typst、PDF 三件套，正式命名为 `某某某简历-某某单位-某某主题.md`、`.typ`、`.pdf`；通用版的单位段固定为 `通用`。
- [ ] **DELIVERY-02**: CLI 提供单份与批量命令，批量任务先完整预检，任何目标失败时不发布部分当前版本。
- [ ] **DELIVERY-03**: 成功交付沿用 candidate-first、精确 path-set/bytes no-op、完整 bundle history、handled error/INT/TERM rollback 与 unknown/symlink fail-closed 语义；诊断、照片规范化中间件和缺口报告不泄露到投递根。

### Verification And Portability

- [ ] **VERIFY-01**: CLI 验证生成 PDF 为真实 1 或 2 页 A4，并验证主题、照片模式、页数、模块边界和命名契约；单纯 PDF 非空或可打开不能视为通过。
- [ ] **VERIFY-02**: 技能提供正常、无照片、多个目标、资格缺口、内容压力和故障注入 fixtures，以及聚合回归命令来证明 schema、定向、分页和发布边界。
- [ ] **VERIFY-03**: `SKILL.md`、CLI fallback 与安装期验证覆盖 Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw 和 Hermes Agent，且不把运行时私有语法写入 canonical 主流程。
- [ ] **VERIFY-04**: 通过受控 CJK 字体、固定前置版本与至少跨一个非开发环境的 PDF/PNG 人工验收，证明中文简历不会因字体 fallback 产生页数或分页漂移。

## Future Requirements

### Resume Enhancements

- **FUTURE-01**: 增加经过同一 schema 契约验证的新主题与行业专用变体。
- **FUTURE-02**: 在获得明确授权和独立安全设计后支持 OCR、招聘信息抓取或结构化导入。
- **FUTURE-03**: 提供网页预览、在线协作或可视化编辑界面。

## Out of Scope

| Feature | Reason |
|---------|--------|
| 自动投递、招聘网站抓取、JD 猜测、ATS 评分或录用预测 | 技能只整理用户提供的事实与当次目标信息，不对招聘时效、资格或录用作推断。 |
| 在 `render` 或 `batch` 中调用 AI | 已标准化资料后的批量路径必须零 token、离线且可重复。 |
| 任意用户自定义 Typst、字体、坐标、配色或模板市场 | 会破坏共享 schema、稳定分页和可验证主题契约。 |
| 自动生成、修图或替换学生照片 | 只允许学生明确提供的照片；无照片时使用无照片版式。 |
| 为凑页数删除事实、低于可读阈值缩字、制造第三页或拆分经历 | 违反真实性、可读性和双页逻辑分页契约。 |
| OS 级加密、访问控制或外部隐私合规承诺 | 技能能约束自身产物与路径，但不能替代部署环境的安全控制。 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SCHEMA-01 | Phase 46 | Complete |
| SCHEMA-02 | Phase 46 | Complete |
| SCHEMA-03 | Phase 46 | Complete |
| SCHEMA-04 | Phase 46 | Complete |
| THEME-01 | Phase 47 | Pending |
| THEME-02 | Phase 47 | Pending |
| THEME-03 | Phase 47 | Pending |
| THEME-04 | Phase 47 | Pending |
| THEME-05 | Phase 47 | Pending |
| TARGET-01 | Phase 48 | Pending |
| TARGET-02 | Phase 48 | Pending |
| TARGET-03 | Phase 48 | Pending |
| DELIVERY-01 | Phase 48 | Pending |
| DELIVERY-02 | Phase 48 | Pending |
| DELIVERY-03 | Phase 48 | Pending |
| VERIFY-01 | Phase 49 | Pending |
| VERIFY-02 | Phase 49 | Pending |
| VERIFY-03 | Phase 49 | Pending |
| VERIFY-04 | Phase 49 | Pending |

**Coverage:**
- v1.19 requirements: 19 total
- Mapped to phases: 19
- Unmapped: 0

---
*Requirements defined: 2026-07-17*
*Last updated: 2026-07-17 after v1.19 milestone definition*
