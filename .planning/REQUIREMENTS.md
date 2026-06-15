# Requirements: v1.15 teaching-design-package 模块化渲染与旧格式回归

**Defined:** 2026-06-15
**Core Value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.

## Milestone Summary

把 `teaching-design-package` 从“统一 Markdown 直接平铺成 Typst/PDF”改成可扩展的 all-in-one 模块编排。统一 Markdown 是唯一内容源，脚本先生成隐藏模块 Markdown，再用 package 内部迁移后的旧格式渲染规则生成正式模块 PDF，最后按模块注册顺序合并成整包 PDF。

公开交付契约改为 `1 + 1 + N`，公开目录只放课程名前缀文件：

- `课程名教学资料.md`
- `课程名教学资料.pdf`
- `课程名授课进度计划表.pdf`
- `课程名教学设计方案.pdf`
- future: `课程名<模块名>.pdf`

模块 Markdown、模块 Typst、model、status、diagnostics、log、calendar 证据等均放隐藏目录。

## Gate Record

- **Validation gate:** v1.14 已归档，Phase 32 是上一里程碑最后 phase；v1.15 roadmap 必须从 Phase 33 开始。
- **Questioning gate:** 用户已直接确认里程碑名称、目标、公开契约、统一 Markdown 契约、模块架构、旧格式回归、YAML 转换、日历推导、课时校验、PDF 合并和验收建议。
- **Research gate:** 跳过外部研究。该里程碑是既有本地技能的架构和格式回归规划，不需要联网调研。
- **Requirements gate:** 本命令只初始化里程碑规划，不执行 phase、不修改 `skills/` 代码。
- **Roadmap gate:** 所有 v1.15 需求必须映射到 Phase 33 及之后的连续 phase。

## v1.15 Requirements

### Unified Markdown Source

- [x] **TDPKG-MOD-01**: `skills/teaching-design-package/templates/teaching-design-package-full.md` 形状继续作为统一 Markdown 契约，并作为后续模块提取和正式产物生成的唯一内容源。
- [x] **TDPKG-MOD-02**: 统一 Markdown 被明确为结构化中间文档，既可供老师之后阅读，也可供脚本解析生成正式产物，但不再作为强制教师确认关卡。
- [x] **TDPKG-MOD-03**: `# 授课进度计划` 是课时和排课的唯一原始内容来源；`# 教学设计方案` 提供教案正文结构，但其中所有时间和课时字段必须由授课计划和日历推导补齐。

### Module Architecture

- [x] **TDPKG-MOD-04**: `teaching-design-package` 新增 package-owned module renderer 编排，当前注册 `teaching-plan` 和 `teaching-design` 两个模块，并能通过模块注册或模块配置扩展未来模块。
- [x] **TDPKG-MOD-05**: 渲染流程生成隐藏模块 Markdown：`.teaching-design-package/work/teaching-plan.md` 和 `.teaching-design-package/work/teaching-design.md`。
- [x] **TDPKG-MOD-06**: 渲染流程生成隐藏模块 Typst：`.teaching-design-package/work/teaching-plan.typ` 和 `.teaching-design-package/work/teaching-design.typ`。
- [x] **TDPKG-MOD-07**: 模块编排不能退化成单体脚本堆砌；新增模块时应能沿用模块注册、模块配置和共享调度模型边界。

### Public and Hidden Artifacts

- [ ] **TDPKG-ART-01**: 默认公开目录只包含课程名前缀的 `1 + 1 + N` 文件，不公开 `.typ`、status、manifest、model、diagnostics、log、calendar JSON 或模块中间产物。
- [ ] **TDPKG-ART-02**: 当前 N=2 时，默认公开目录生成 `电气设备控制线路安装与调试教学资料.md`、`电气设备控制线路安装与调试教学资料.pdf`、`电气设备控制线路安装与调试授课进度计划表.pdf`、`电气设备控制线路安装与调试教学设计方案.pdf`。
- [ ] **TDPKG-ART-03**: 隐藏目录包含模块 Markdown、模块 Typst、统一 scheduling model、status、diagnostics、log、calendar 路径/hash 和推导摘要。

### Legacy Formal Format Migration

- [ ] **TDPKG-LEGACY-01**: `授课进度计划表.pdf` 回归旧 `jiaoan-jihua` 当前可接受产物格式，格式规则迁移到 `teaching-design-package` 内部。
- [ ] **TDPKG-LEGACY-02**: `教学设计方案.pdf` 回归旧 `jiaoan-shicao` 当前可接受产物格式，格式规则迁移到 `teaching-design-package` 内部。
- [ ] **TDPKG-LEGACY-03**: 旧 `jiaoan-jihua` 和 `jiaoan-shicao` 技能保持可用、不被删除，并且不作为 package 运行时依赖。
- [ ] **TDPKG-LEGACY-04**: 对 fixture 场景，验证迁移后的 package 内部渲染规则与旧技能输出一致或等价；对统一模板场景，验证生成的是旧正式格式 PDF，而不是平铺文档。

### YAML and Module Conversion

- [x] **TDPKG-YAML-01**: 统一 Markdown YAML 接受 `course_name`、`major_name`、`course_attribute`、`textbook_name`、`class_name`、`teachers`、`first_teaching_day`。
- [x] **TDPKG-YAML-02**: 生成授课进度计划模块 Markdown 时补齐 `major_name`、`course_name`、`teacher_name`、`class_name`、`first_teaching_day`、`daily_hours`、`template: "jiaoan-jihua"`。
- [x] **TDPKG-YAML-03**: 生成教学设计方案模块 Markdown 时补齐 `template: "jiaoan-shicao"`、`course_name`、`course_attribute`、`textbook_name`、`class_name`、`total_hours`、`teacher_name`、`use_time`。
- [x] **TDPKG-YAML-04**: `teachers` 列表合并为 `teacher_name`；`daily_hours` 来自技能自身日历或配置约定；`total_hours` 严格从授课进度计划逐行课时求和；`use_time` 使用推导出的课程总起止日期。

### Calendar and Scheduling Model

- [x] **TDPKG-SCHED-01**: `calendar.json` 放在 `teaching-design-package` 技能自身目录中，例如 `skills/teaching-design-package/references/calendar.json`，standalone copy 只包含该 skill folder 时仍可完成推导。
- [x] **TDPKG-SCHED-02**: `first_teaching_day` 必须存在并能在 `calendar.json` 中定位；日历范围不够或日期缺失必须失败。
- [x] **TDPKG-SCHED-03**: 学年、学期、课程总起止日期、每个学习任务起止日期、周次、星期、每日课时消耗均由 `calendar.json`、`first_teaching_day` 和授课计划逐行课时推导。
- [x] **TDPKG-SCHED-04**: 不能用自然日顺推代替真实日历；所有时间相关内容只能由统一 scheduling model 推导，两个模块不能各算各的。
- [x] **TDPKG-SCHED-05**: 隐藏诊断/status/model 记录 calendar 路径、hash、推导摘要和错误。

### Hours and Cross-Module Validation

- [ ] **TDPKG-VAL-01**: 授课进度计划每一行 `内容-N` 是唯一原始课时来源；每个学习任务总课时和课程总课时均严格求和。
- [ ] **TDPKG-VAL-02**: 教案中每个 `课时：xH` 必须来自对应学习任务总课时；教案活动中每个 `##### xH` 必须来自对应授课计划活动课时。
- [ ] **TDPKG-VAL-03**: 活动映射以“学习任务 + 学习环节 + 活动顺序”为主，标题相似度或归一化只作为校验辅助。
- [ ] **TDPKG-VAL-04**: 授课计划与教案的任务数量、环节数量、活动数量、标题对应、课时合计、起止日期任一不一致时，命令必须失败并写隐藏诊断，不能生成最终成功产物。

### PDF Generation and Merge

- [ ] **TDPKG-PDF-01**: 所有模块 PDF 都真实生成且非空后，才允许合并 `课程名教学资料.pdf`。
- [ ] **TDPKG-PDF-02**: 合并顺序由模块注册顺序决定，当前先 `授课进度计划表`，再 `教学设计方案`。
- [ ] **TDPKG-PDF-03**: PDF 合并可使用 `pdfunite`、`qpdf` 或 Python PyMuPDF fallback，但 status 必须诚实记录实际工具和结果。
- [ ] **TDPKG-PDF-04**: 任一模块 PDF 失败或合并失败时，最终命令必须非零退出，公开目录不能伪装成成功。

## Future Requirements

- **TDPKG-FUTURE-01**: 新增第三个或更多正式模块，例如成绩册、期末资料或其他教学资料。
- **TDPKG-FUTURE-02**: 将 package 模块注册能力抽象成跨技能通用框架。
- **TDPKG-FUTURE-03**: 发布外部 skill registry 或 installer 包。
- **TDPKG-FUTURE-04**: 重写旧 standalone `jiaoan-jihua` 或 `jiaoan-shicao` 的公开接口。

## Out of Scope

| Feature | Reason |
|---------|--------|
| 执行实现 phase | 用户明确要求本命令只创建 v1.15 新里程碑，不执行 phase、不修代码。 |
| 修改 `skills/` 代码 | 实现应由后续 `discuss/plan/execute phase` 命令处理。 |
| 删除旧 `jiaoan-jihua` 或 `jiaoan-shicao` 技能 | 旧技能是外部兼容面和测试 oracle，必须保持可用。 |
| 公开模块 Markdown 或模块 Typst | 这些属于内部中间产物，必须隐藏。 |
| 用自然日顺推替代真实日历 | 用户要求必须基于 `calendar.json` 推导，范围缺失必须失败。 |
| 部分成功输出整包 PDF | 任一模块失败或合并失败时，公开目录不能伪装成功。 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| TDPKG-MOD-01 | Phase 33 | Complete |
| TDPKG-MOD-02 | Phase 33 | Complete |
| TDPKG-MOD-03 | Phase 33 | Complete |
| TDPKG-MOD-04 | Phase 33 | Complete |
| TDPKG-MOD-05 | Phase 33 | Complete |
| TDPKG-MOD-06 | Phase 33 | Complete |
| TDPKG-MOD-07 | Phase 33 | Complete |
| TDPKG-YAML-01 | Phase 33 | Complete |
| TDPKG-YAML-02 | Phase 33 | Complete |
| TDPKG-YAML-03 | Phase 33 | Complete |
| TDPKG-YAML-04 | Phase 33 | Complete |
| TDPKG-SCHED-01 | Phase 33 | Complete |
| TDPKG-SCHED-02 | Phase 33 | Complete |
| TDPKG-SCHED-03 | Phase 33 | Complete |
| TDPKG-SCHED-04 | Phase 33 | Complete |
| TDPKG-SCHED-05 | Phase 33 | Complete |
| TDPKG-LEGACY-01 | Phase 34 | Pending |
| TDPKG-LEGACY-03 | Phase 34 | Pending |
| TDPKG-LEGACY-04 | Phase 34 | Pending |
| TDPKG-VAL-01 | Phase 34 | Pending |
| TDPKG-LEGACY-02 | Phase 35 | Pending |
| TDPKG-VAL-02 | Phase 35 | Pending |
| TDPKG-VAL-03 | Phase 35 | Pending |
| TDPKG-VAL-04 | Phase 35 | Pending |
| TDPKG-ART-01 | Phase 36 | Pending |
| TDPKG-ART-02 | Phase 36 | Pending |
| TDPKG-ART-03 | Phase 36 | Pending |
| TDPKG-PDF-01 | Phase 36 | Pending |
| TDPKG-PDF-02 | Phase 36 | Pending |
| TDPKG-PDF-03 | Phase 36 | Pending |
| TDPKG-PDF-04 | Phase 36 | Pending |

**Coverage:**
- v1.15 requirements: 31 total
- Mapped to phases: 31
- Unmapped: 0

---
*Requirements defined: 2026-06-15*
*Last updated: 2026-06-15 after v1.15 milestone initialization*
