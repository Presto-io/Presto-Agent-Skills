# Phase 48: 确定性定向渲染与干净批量交付 - Research

**Researched:** 2026-07-18
**Domain:** 离线事实定向、Markdown-first Typst/PDF 渲染、动态 managed-set 安全发布
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

## Implementation Decisions

### Deterministic Targeting
- **D-01:** 定向解析必须逐事实记录稳定 ID、所执行的动作（选择、排序、强调、排除或置顶）以及匹配理由，不能只输出最终顺序。
- **D-02:** 正式 Markdown YAML 保存简要追溯索引；逐事实的完整理由保存在授权的隐藏诊断/证据区域。Typst 与 PDF 不显示内部匹配理由。
- **D-03:** 个人信息、教育等核心事实始终保留；项目、技能、证书、实训和经历等非核心事实可按岗位相关性及冻结页数预算选择或省略。
- **D-04:** 用户可通过 CLI 按稳定事实 ID 显式保留、排除或置顶；覆盖参数必须冻结进该版本 metadata，不能回写 canonical 事实源或 target 招聘事实。

### Hard Requirement States
- **D-05:** 硬条件采用严格证据判定：只有已核实事实明确证明时才是“满足”；明确不符合为“缺口”；资料不足为“未知”；条件对该岗位实例不成立时才是“不适用”。不得用相似关键词推断满足。
- **D-06:** 每个存在缺口的目标必须单独显式允许继续生成；批量命令可以一次列出多个获准继续的目标 ID，但不能用长期全局开关绕过确认。
- **D-07:** “未知”默认允许生成并给出警告，不要求额外放行；正式简历和 metadata 均不得暗示未知条件已经满足。
- **D-08:** 预检在 CLI 中展示逐条件四态表格；完整条件矩阵写入隐藏 JSON 证据，正式 Markdown YAML 只保存四态汇总、证据摘要和是否经缺口放行。

### Version Matrix
- **D-09:** batch 默认生成一份通用版及全部已确认目标版；单份 render 用于明确选择一个通用版或目标版。
- **D-10:** 每个通用版和目标版都正式生成“保守稳妥 / 现代简洁 / 个性设计”三种主题，不采用“先预览一个、再只发布一个”的默认策略。离线 PDF 渲染不消耗 AI，因此三个主题均属于正式交付矩阵。
- **D-11:** 每个“版本 + 主题”只发布一个主页面版本。Phase 47 临界区或强制页数策略产生的另一页数版本只进入 preview/workdir，不占用正式 stem。
- **D-12:** 每份正式 Markdown 都是可独立审阅的最终定向文档，包含该版本实际采用的事实与顺序、主题、页数、照片模式、目标来源/日期和简要追溯索引；Typst 必须由这份最终 Markdown 派生，PDF 再由该 Typst 编译。

### Clean Batch Publication
- **D-13:** 投递根平铺全部正式三件套，不按单位或版本创建 current 子目录。根目录只允许当前 managed files 及约定的支持目录；诊断、缺口明细、照片规范化中间件、preview 和临时证据不得泄露到投递根。
- **D-14:** history 只归档实际更新或移除的版本，不复制本次未变化版本；但每个被归档版本必须保存完整 Markdown、Typst、PDF 三件套，不能只归档发生字节变化的单个文件。
- **D-15:** 所有定向版 stem 始终包含岗位，格式为“姓名简历-单位-岗位-主题”；通用版固定为“姓名简历-通用-主题”。姓名、单位、岗位和主题必须经过确定性安全规范化，且不得包含联系方式、身份证、原始 URL 等敏感信息。
- **D-16:** batch 的新版本矩阵是 current 的权威目标集合。目标减少时，预检必须明确列出拟移除版本；确认后先把这些版本的完整三件套归档，再从 current 删除。
- **D-17:** 单份与批量任务都必须先完成全部候选生成和完整预检。批量中任一目标、主题或三件套失败时，不得发布新增、更新或移除中的任何一项。
- **D-18:** no-op 以本次受影响版本的精确 managed path set 与逐文件 bytes 相等判定；完全相同的版本不发布、不归档，也不改变 current。
- **D-19:** 沿用 v1.18 的 candidate-first、handled error/INT/TERM rollback、held directory identity、unknown/symlink/partial/stale-work fail-closed 语义。单份更新不得破坏其他 current 版本，批量失败必须保持整个原 current 集合不变。

### the agent's Discretion
- 定向评分权重、同分稳定排序规则和模块相关性词表可由研究与规划阶段确定，但必须离线、确定、可解释，并受稳定 ID 追溯约束。
- CLI 参数的具体拼写、metadata 字段名、隐藏 JSON schema、终端表格样式和安全文件名规范化细节由后续规划决定。
- history 序号目录内如何区分多个同时更新的版本可由实现选择，只要每个归档版本保持完整三件套且 rollback 可确定恢复。

### Deferred Ideas (OUT OF SCOPE)
- 跨 runtime 安装验证、聚合故障注入、PDF 结构/布局验证和非开发环境字体 UAT 属于 Phase 49。
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TARGET-01 | CLI 能从同一份已核实资料生成一份通用版，以及每个“单位 + 岗位”一份独立定向版；定向只允许选择、排序和强调已核实事实。 | 采用不可变 `VersionProjection`、稳定事实 ID、整数相关性评分、显式覆盖和逐事实 trace；布局器只消费投影。 `[VERIFIED: 48-CONTEXT.md; graduate_resume_layout.py]` |
| TARGET-02 | CLI 对用户提供的岗位硬条件生成透明的满足、缺口、未知或不适用提示；有缺口时仍允许按用户决定生成定向版，但简历不得暗示已符合。 | 使用受控谓词 + 明确证据 ID 的四态解析；未知默认警告，缺口按 target ID 单次放行，完整矩阵留在隐藏 evidence。 `[VERIFIED: 48-CONTEXT.md; .planning/research/PITFALLS.md]` |
| TARGET-03 | 每个版本的 YAML 记录实际主题、页数、照片模式、目标单位和岗位，以及本次定向信息的来源/日期；招聘信息不由技能抓取、猜测或声称实时。 | 定义 `graduate-resume-delivery/v1` 最终 Markdown metadata，并绑定 canonical 输入 hash、target ID/source/as_of 与证据摘要。 `[VERIFIED: schema-and-review-contract.md; 48-CONTEXT.md]` |
| DELIVERY-01 | 每个成功版本同 stem 输出 Markdown、Typst、PDF 三件套，正式命名为 `某某某简历-某某单位-某某主题.md`、`.typ`、`.pdf`；通用版的单位段固定为 `通用`。 | 版本×三主题展开为每版本 9 个 managed files；最终 Markdown 重读后发射 Typst，Typst 固定时间戳编译 PDF。 `[VERIFIED: graduate_resume_typst.py; test_layout_fixtures.py; 48-CONTEXT.md]` |
| DELIVERY-02 | CLI 提供单份与批量命令，批量任务先完整预检，任何目标失败时不发布部分当前版本。 | 单份采用 patch 语义、批量采用 replace-authority 语义；两者都在同一 `.work/<run>/candidate` 完成所有候选与预检后才开发布事务。 `[VERIFIED: delivery_transaction.py analogs; 48-CONTEXT.md]` |
| DELIVERY-03 | 成功交付沿用 candidate-first、精确 path-set/bytes no-op、完整 bundle history、handled error/INT/TERM rollback 与 unknown/symlink fail-closed 语义；诊断、照片规范化中间件和缺口报告不泄露到投递根。 | 从现有 held-directory 事务抽取动态 bundle delta：unchanged/add/update/remove，history 只写 update/remove 的旧完整三件套。 `[VERIFIED: tiaokedan delivery_transaction.py; teaching-design-package delivery-transaction.js]` |
</phase_requirements>

## Summary

Phase 48 不需要引入新的外部框架；正确计划应围绕三个新的内部权威对象展开：`VersionProjection`（一个通用版或目标版实际采用的事实及逐事实 trace）、`FinalResumeDocument`（正式可重读 Markdown）和 `DeliveryMutationPlan`（按完整三件套分组的 add/update/remove/unchanged 事务计划）。现有 CLI 已有严格 schema/target 校验，布局器已有三主题、照片、1/2 页冻结计划，Typst emitter 已有候选文本转义；缺口是这些组件目前仍直接消费 canonical facts，且 `render`/`batch` 仍为 `NOT_IMPLEMENTED`。 `[VERIFIED: codebase grep]`

规划时最重要的边界是：相关性排序与硬条件证明必须分成两条管线。相关性可以使用离线、版本化、可解释的词表评分；硬条件只能由受控谓词对明确已核实字段求值，任何未识别自然语言都必须落为 `unknown`，不得借用关键词相似度得出 `meets`。 `[VERIFIED: 48-CONTEXT.md]` `[RECOMMENDATION]`

发布层不能直接复制现有“整套全量归档”实现。Teaching Design Package 已证明动态 expected set、candidate-first、held directory identity 与 root discovery 可行，但它会归档整个旧 managed set；Phase 48 必须进一步按 stem 分组计算 delta，只归档实际更新或移除的旧完整三件套，同时保持未变化 bundle 的 inode/mtime 不动。 `[VERIFIED: teaching-design-package/scripts/delivery-transaction.js; skills/tiaokedan/scripts/delivery_transaction.py]`

**Primary recommendation:** 按 roadmap 的 48-01/02/03 顺序实现“事实投影与四态 → 最终 Markdown 重读式渲染 → 动态 bundle-delta 安全事务”，不要把定向、渲染和发布揉进 CLI 单文件。 `[RECOMMENDATION]`

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| canonical 资料解析与验证 | CLI / Application Core | Local Storage | 已有 `load_resume`/`validate_document` 是唯一入口，文件仅作为本地受审输入。 `[VERIFIED: graduate_resume_cli.py]` |
| 定向事实选择与排序 | Application Core | — | 纯函数消费已验证事实、target 和 overrides，不应接触文件发布或 Typst。 `[RECOMMENDATION]` |
| 硬条件四态证据 | Application Core | Hidden Evidence Storage | 状态由受控 evaluator 产生，完整证据写授权 evidence，公开 YAML 只留摘要。 `[VERIFIED: 48-CONTEXT.md]` |
| 1/2 页与主题冻结 | Layout Domain | Typst Emitter | `FrozenResumePlan` 继续拥有页数、容器与主题；emitter 机械实现。 `[VERIFIED: graduate_resume_layout.py; graduate_resume_typst.py]` |
| 最终 Markdown | Application Core | Local Storage | 它是公开、可独立审阅且必须被重读的渲染检查点。 `[VERIFIED: 48-CONTEXT.md; PROJECT.md]` |
| Typst/PDF 生成 | Local Renderer | Typst CLI | Typst 从最终 Markdown 投影机械生成，PDF 由受控 Typst 0.15.0 编译。 `[VERIFIED: local CLI; Phase 47 code]` |
| 单份/批量发布 | Delivery Transaction | Local Filesystem | held directory + descriptor-relative mutation拥有 current/history/rollback 边界。 `[VERIFIED: v1.18 delivery implementations]` |

## Project Constraints (from AGENTS.md)

- 所有用户可见回复使用简体中文；文件格式必须使用其他语言时除外。 `[VERIFIED: AGENTS.md]`
- canonical `SKILL.md` 必须保持 runtime-neutral；runtime 私有语法只能进入 adapter notes。 `[VERIFIED: AGENTS.md]`
- 文档、模板应简洁、可复制、可审阅；复杂背景进入 `references/`，脚本进入 `scripts/`，模板进入 `templates/`。 `[VERIFIED: AGENTS.md]`
- 外部命令、网络、凭据或文件写入必须写明安全边界和验证步骤。 `[VERIFIED: AGENTS.md]`
- OpenClaw 与 Hermes Agent 必须保持一等 runtime，但跨 runtime 实际验收留给 Phase 49。 `[VERIFIED: AGENTS.md; 48-CONTEXT.md]`
- 本阶段不得修改 source implementation；本研究仅生成规划文档。 `[VERIFIED: parent task]`

## Standard Stack

### Core

| Library / Runtime | Version | Purpose | Why Standard |
|-------------------|---------|---------|--------------|
| Python | 3.14.6（当前环境） | CLI、解析、定向、事务与测试 | 当前 `graduate-resume` 和两个 Python clean-delivery analog 均使用 Python；当前环境 secure dir-fd 能力完整。 `[VERIFIED: local CLI; codebase grep]` |
| PyYAML | 6.0.3 | canonical 与 final Markdown frontmatter 解析 | 已是现有 CLI 依赖，当前安装版也是 PyPI 最新可见版。 `[VERIFIED: pip registry; graduate_resume_cli.py]` |
| Typst CLI | 0.15.0 | 受控字体下编译 PDF/PNG | Phase 47 已锁定该版本并使用 `--font-path --ignore-system-fonts --creation-timestamp 0`。 `[VERIFIED: local CLI; test_layout_fixtures.py]` |
| Python stdlib `hashlib`, `unicodedata`, `os`, `stat`, `signal`, `secrets` | Python 3.14 | hash 绑定、NFKC、安全文件系统与 rollback | 现有事务已经用这些原语实现 held identity、O_NOFOLLOW、fsync 和信号回滚。 `[VERIFIED: delivery_transaction.py]` |

### Supporting

| Library / Asset | Version | Purpose | When to Use |
|-----------------|---------|---------|-------------|
| skill-local Noto Sans Mono CJK SC | manifest/hash controlled | 中文字形与跨机排版稳定 | 每次正式 plan/render 前验证 manifest、hash 与 Typst 可见性。 `[VERIFIED: graduate_resume_layout.py]` |
| `unittest` | stdlib | 定向、渲染、事务回归 | Phase 48 skill-local 快速测试；Phase 49 再负责聚合与跨环境证明。 `[VERIFIED: existing tests; 48 boundary]` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| 版本化整数词表评分 | jieba/embedding/LLM | 会新增包、模型或不可解释分词；与离线、零 token、可追溯约束不匹配。 `[RECOMMENDATION]` |
| PyYAML | 自写 YAML/frontmatter parser | 会重复处理 YAML 边界和类型错误，且已有成熟依赖。 `[VERIFIED: current implementation]` |
| Typst CLI | 自写 PDF 生成器 | 会重建字体嵌入、页面布局和 PDF 编码；Phase 47 已有冻结 Typst contract。 `[VERIFIED: Phase 47 implementation]` |
| descriptor-relative transaction | 普通 `Path.rename`/`shutil` 流程 | 无法保留现有 held identity、no-follow、rollback 与 stale-work 防线。 `[VERIFIED: v1.18 tests]` |

**Installation:** 本阶段不应新增包；使用仓库已声明的 Python、PyYAML、Typst 与 skill-local 字体。 `[RECOMMENDATION]`

## Package Legitimacy Audit

本阶段没有新增外部包，因此不触发 package installation legitimacy gate。项目继续使用当前 Python 生态依赖 `PyYAML`，不新增其他解析包。 `[VERIFIED: pip registry; graduate_resume_cli.py]`

## Architecture Patterns

### System Architecture Diagram

```text
canonical graduate-resume/v2 + CLI overrides
                 |
                 v
      validate_document (fail closed)
                 |
        +--------+---------+
        |                  |
        v                  v
 generic projection   confirmed target projections
                           |
                           v
                  four-state condition matrix
                 /      |       |        \
              meets    gap   unknown     n/a
                        |        |
                per-target      warning
                allow gate
        +--------------------------+
        v
  VersionProjection (ordered facts + trace)
        |
        v
  3 ThemeSpecs x frozen 1/2-page plans
        |
        v
  final Markdown candidates (public semantic truth)
        |
      reparse
        v
  Typst candidates -> Typst 0.15.0 -> PDF candidates
        |
        v
 full candidate preflight + bundle delta
        |
   +----+-------------------------------+
   |                                    |
 render patch mode                 batch authority mode
 preserve unrelated               remove obsolete bundles
   |                                    |
   +----------------+-------------------+
                    v
      held-dir transaction + history + rollback
                    |
                    v
       flat current triples + support directories
```

该流程保持 canonical facts 不变、最终 Markdown 可审阅、Typst/PDF 机械派生，并把任何 current mutation 推迟到全候选成功之后。 `[VERIFIED: 48-CONTEXT.md]` `[RECOMMENDATION]`

### Recommended Project Structure

```text
skills/graduate-resume/
├── SKILL.md
├── references/
│   ├── schema-and-review-contract.md
│   ├── phase-46-baseline.md
│   └── targeted-render-delivery-contract.md   # Phase 48 长契约
├── templates/
│   ├── graduate-resume.md
│   ├── resume-themes.typ
│   ├── layout-measurement.json
│   └── targeting-policy.json                  # 版本化权重/词表/受控谓词
└── scripts/
    ├── graduate_resume_cli.py                 # 参数与稳定错误边界
    ├── graduate_resume_targeting.py           # VersionProjection + 四态
    ├── graduate_resume_final_markdown.py      # 写入并重读 final MD
    ├── graduate_resume_layout.py              # 继续拥有冻结布局
    ├── graduate_resume_typst.py               # 只消费 final MD projection
    ├── graduate_resume_render.py              # 候选三件套与矩阵协调
    ├── graduate_resume_delivery.py            # 动态 bundle delta 事务
    └── test_phase48_*.py
```

这是职责拆分建议，不要求改变现有公开 shell 命令名。 `[RECOMMENDATION]`

### Pattern 1: 不可变版本事实投影

**What:** 在布局前生成 `VersionProjection`，只含该版本最终采用的已核实事实、稳定顺序、强调标记、overrides 和逐事实 trace；canonical document 永不被修改。 `[RECOMMENDATION]`

**Rules:**
- `candidate/profile` 与 `education` 总是 selected；对它们执行 exclude 必须稳定失败。 `[VERIFIED: D-03]`
- `pin` 隐含 retain；同一事实同时 retain/exclude 或 pin/exclude 必须拒绝，而非定义隐式优先级。 `[RECOMMENDATION]`
- 非核心事实先按模块分组，再按整数 score 降序、稳定 ID 字典序排序；正文原始顺序不能作为 tie-break，因为 Phase 46 已声明正文顺序不构成事实语义。 `[VERIFIED: schema-and-review-contract.md]`
- 推荐评分使用版本化整数项：岗位 exact term `40`、岗位词表 expansion `20`、每个 requirement exact term `15`、求职方向 exact term `10`；分数只是选择/排序依据，不能作为硬条件证据。 `[RECOMMENDATION]`
- 模块展示顺序继续由 renderer 的受控简历阅读顺序决定；评分只改变模块内条目和可选条目的入选，不把个人信息移出首页。 `[VERIFIED: Phase 47 contract]`
- D-03 的冻结页数预算采用共享事实集反馈算法：resolver 先产生核心事实与按稳定优先级排列的非核心候选，再把同一 selected ID 集合交给 conservative/modern/expressive 三个 Phase 47 布局计划评估；任一主题超过请求的 `auto（最多 2 页）`、`1` 或 `2` 页预算时，只从全主题共享集合尾部移除一个最低优先级、非 core、非 retain、非 pin 的事实并重试。三主题不得各自删事实；只剩 core/retain/pin 仍溢出时稳定失败 `PAGE_BUDGET_UNSATISFIABLE`。最终 projection 冻结请求页数、三主题 fit/page-count 摘要、selected/elided IDs 与反馈 digest。 `[RESOLVED: D-03; Claude's Discretion]`

### Pattern 2: 四态硬条件采用受控谓词，不采用模糊匹配

**What:** 为每条 requirement 生成稳定 condition ID、原文、predicate、state、evidence fact IDs、reason code。 `[RECOMMENDATION]`

**Recommended resolution order:**
1. 对 requirement 做 Unicode NFKC 与空白/标点规范化，并以 `target_id + sha256(normalized_requirement)` 生成稳定 condition ID；重复归一化条件直接拒绝。 `[RECOMMENDATION]`
2. 若本次 CLI 显式声明该条件对岗位实例不适用，记录理由并得出 `not-applicable`；不得由关键词自动推断。 `[VERIFIED: D-05]` `[RECOMMENDATION]`
3. Phase 48 的 versioned predicate registry 只登记 `education_level`、`major_exact`、`certificate_exact`、`fresh_graduate_status` 四类；仅当规范化 requirement 能无歧义解析为其中之一并映射到已核实结构化字段时求值，明确通过为 `meets`，明确反例为 `gap`。年限、年龄、地域、技能熟练度及其他自然语言条件一律不扩展谓词。 `[RESOLVED: Claude's Discretion]`
4. 无受控谓词、字段缺失、日期不足、只能靠相似词或经验推断时一律 `unknown`。 `[VERIFIED: D-05/D-07]`

公开 CLI 唯一采用可重复三参数形式 `--not-applicable <target-id> <condition-id> <reason>`。两个 ID 必须原样满足现有稳定 ID grammar；reason 是一个经 shell 引号保护的 UTF-8 参数，trim 后 1..200 个 Unicode code points，禁止 NUL、CR/LF 和其他控制字符。相同 `(target-id, condition-id)` 重复出现（即使理由相同）、未知或未选 target、未知 condition、generic render 使用该参数都稳定报错；有效 override 只冻结到本次 metadata/evidence，不回写 canonical 或 target brief。 `[RESOLVED: D-05; Claude's Discretion]`

### Pattern 3: Final Markdown 是必须重读的编译检查点

**What:** renderer 先写完整 final Markdown candidate，然后重新调用专用 parser 得到 `FinalResumeDocument`；Typst emitter 只能消费该重读结果，不能继续消费写 Markdown 前的内存对象。 `[RECOMMENDATION]`

**Required YAML fields:**
- `schema: graduate-resume-delivery/v1`
- canonical input SHA-256、target policy/version hash、font manifest hash、measurement hash。 `[RECOMMENDATION]`
- version kind/id、company、role、source、as_of；通用版显式 `kind: generic`。 `[VERIFIED: D-12; TARGET-03]`
- theme key/label、page_count、photo_mode、ordered selected fact IDs。 `[VERIFIED: D-12]`
- override snapshot、trace 摘要、四态计数、evidence digest、gap allow 状态。 `[VERIFIED: D-02/D-04/D-08]`

不得写运行时间或随机 run ID 到正式三件套，否则同输入无法 byte-exact no-op。 target 的 `as_of` 是用户事实，可保留；PDF creation timestamp 固定为 `0`。 `[VERIFIED: D-18; Typst local CLI; test_layout_fixtures.py]`

### Pattern 4: 三主题正式矩阵与单一主页面

**What:** 一个“版本”固定展开 conservative/modern/expressive 三个正式主题，每主题一套 `.md/.typ/.pdf`，即每版本 9 个 managed files。 `[VERIFIED: D-09/D-10]`

- `render generic` 生成通用版的三个主题，不删除其他 current bundle。 `[VERIFIED: D-09/D-19]`
- `render --target <id>` 生成该目标版的三个主题，不删除其他 current bundle。 `[VERIFIED: D-09/D-19]`
- `batch` 生成 `generic + all confirmed targets` 的全部三个主题，并把该矩阵作为 current 权威集合。 `[VERIFIED: D-09/D-16]`
- 临界/强制页数的 comparison 版本必须完整生成和验证，但只能位于当前 run 的 preview/evidence 区，不能进入正式 stem 或 root。 `[VERIFIED: D-11/D-13]`

### Pattern 5: 动态 managed-set 的 bundle delta transaction

**What:** 文件级 expected set 先按 stem 分成严格三件套，再计算 `unchanged / added / updated / removed`。 `[RECOMMENDATION]`

| Class | Current | Candidate | Action |
|-------|---------|-----------|--------|
| unchanged | 完整 triple | 同 path set 且逐文件 bytes 相同 | 不 replace、不归档、不改 inode/mtime。 `[VERIFIED: D-18]` |
| added | 无 | 完整 triple | 发布 candidate；rollback 时删除新增 triple。 `[RECOMMENDATION]` |
| updated | 完整 triple | 同 stem 完整 triple，但任一 bytes 不同 | 先 snapshot/归档旧完整 triple，再 replace 新 triple。 `[VERIFIED: D-14]` |
| removed | 完整 triple | 无（仅 batch authority） | 先 snapshot/归档旧完整 triple，再删除 current。 `[VERIFIED: D-16]` |

一个发布序号目录可以平铺本次所有 updated/removed stem 的旧文件；因为 stem 唯一，三件套不会冲突，且 history 校验只需证明每个 stem 恰有 `.md/.typ/.pdf`。 `[RECOMMENDATION]`

### Pattern 6: 照片版三件套自包含

现有 emitter 把逻辑照片路径写入 `.typ`，若正式 delivery/history 只保存三件套，旧 Typst 会依赖外部照片路径。 `[VERIFIED: graduate_resume_typst.py]`

冻结实现为 skill-local Python 调用已锁定的 Typst 0.15.0，不新增图像库：对 Phase 47 已验证、no-follow bounded-read 得到的 JPEG/PNG bytes 生成只含 `image(bytes(...), fit: "contain")` 的临时 Typst 文档，以白色 `35mm × 49mm` 页面、零边距、居中、保持宽高比、允许等比放大但禁止裁切/拉伸，执行 `typst compile - normalized.png --format png --ppi 300 --creation-timestamp 0`。输出契约固定为 PNG、`413 × 579` 像素、300 PPI 栅格化基准；仅接受重新解码后 IHDR 尺寸匹配的输出。Typst 重编码移除输入 EXIF、源文件名和路径 metadata；规范化 PNG bytes 随后以 `image(bytes(...), format: "png")` 内嵌正式 `.typ`，中间 PNG 只留 owned workdir。 `[RESOLVED: Phase 47 slot; existing Typst dependency]`

Phase 48 测试必须用含 EXIF/方向信息的 JPEG 与 PNG fixture 断言：同一输入重复规范化得到逐字节相同 PNG 与 SHA-256；输出为 `413 × 579`、白底居中 contain 且无 EXIF/源路径文本；正式 `.md/.typ/.pdf` 不含原始绝对路径或 URL；移动 current triple、以及把旧 triple 归档到 history 后，均可在无原照片目录用受控字体独立重编译 `.typ`，且重复编译 bytes 稳定。 `[RESOLVED]`

### Anti-Patterns to Avoid

- **用同一关键词分数判定 hard requirement:** 相关不等于证明，必须落回受控谓词或 unknown。 `[VERIFIED: D-05]`
- **Typst 直接消费 canonical facts:** 会绕过 final Markdown 事实检查点。 `[VERIFIED: D-12]`
- **batch 边生成边发布:** 任一后续目标失败都会留下半批 current。 `[VERIFIED: D-17]`
- **每次归档整个 current:** 违反“更新谁、归档谁”，并制造无关历史副本。 `[VERIFIED: D-14]`
- **把 manifest/condition JSON 放在投递根:** 它们属于隐藏 evidence 或显式外部诊断目录。 `[VERIFIED: D-13]`
- **按连字符反向解析单位/岗位:** 安全规范化后字段可能含连接符；current 身份应以完整 expected stem 集合和安全前后缀 contract 判断。 `[RECOMMENDATION]`
- **发现 stem 冲突后静默覆盖:** 必须在预检阶段稳定失败，或使用 target ID 派生的非敏感短 hash 确定性消歧。 `[RECOMMENDATION]`

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML 解析 | 正则 frontmatter/YAML parser | PyYAML `safe_load` + 专用字段校验 | 当前实现已覆盖类型和未知字段边界。 `[VERIFIED: graduate_resume_cli.py]` |
| PDF 编码/字体嵌入 | 自写 PDF writer | Typst 0.15.0 + skill-local fonts | Phase 47 已冻结布局与字体 contract。 `[VERIFIED: Phase 47 code]` |
| 中文语义 AI 排序 | LLM、embedding 或联网职位分析 | 版本化整数词表 + exact term trace | 保持离线、零 token、可解释、byte deterministic。 `[VERIFIED: PROJECT.md]` `[RECOMMENDATION]` |
| 模糊资格推断 | 相似度阈值 | 受控 predicate registry + unknown fallback | 防止把相关词误报为满足。 `[VERIFIED: D-05]` |
| 普通路径事务 | `shutil.copytree`/裸 `rename` | 现有 O_NOFOLLOW、dir_fd、held identity 模式 | 已有故障、INT/TERM、symlink/stale-work 回归。 `[VERIFIED: v1.18 tests]` |
| 新的时间戳/manifest sidecar | 公开 run manifest | final Markdown YAML + hidden evidence JSON | 避免污染 delivery root 和破坏 no-op。 `[VERIFIED: D-02/D-13/D-18]` |

**Key insight:** 本阶段真正复杂的是“事实证明边界”和“多 bundle 状态迁移”，不是 Markdown 字符串拼接。复用现有 parser/layout/Typst/secure-fs 原语，把新代码集中在不可变投影、重读检查点和 bundle delta。 `[RECOMMENDATION]`

## Common Pitfalls

### Pitfall 1: canonical facts 与 target projection 共用可变 dict
**What goes wrong:** 一个目标的排序、排除或强调污染通用版或另一个目标。 `[VERIFIED: milestone PITFALLS]`
**Why it happens:** 当前布局器直接消费 `document.data`，若原地修改就会共享状态。 `[VERIFIED: graduate_resume_cli.py; graduate_resume_layout.py]`
**How to avoid:** 对每个版本构建冻结 projection；所有 target transform 都返回新对象并绑定 canonical hash。 `[RECOMMENDATION]`
**Warning signs:** 第二个 target 的 trace 出现第一个 target 的 override，或通用版 selected IDs 随 batch 顺序变化。 `[RECOMMENDATION]`

### Pitfall 2: requirement 文本未结构化却输出 meets
**What goes wrong:** “熟悉 PLC”被当成“持有低压电工证”或“本科”条件满足。 `[VERIFIED: D-05; PITFALLS.md]`
**Why it happens:** 把相关性词表复用于资格证明。 `[RECOMMENDATION]`
**How to avoid:** evaluator registry 只接受明确 predicate；不识别即 unknown，证据必须列稳定 fact IDs。 `[RECOMMENDATION]`
**Warning signs:** `meets` 没有 evidence IDs，或 reason 只有 shared keyword。 `[RECOMMENDATION]`

### Pitfall 3: final Markdown 写了但 Typst 仍绕过它
**What goes wrong:** Markdown 展示事实与 PDF 实际事实不一致，YAML metadata 变成装饰。 `[VERIFIED: D-12]`
**Why it happens:** emitter 继续拿写 Markdown 前的 Python model。 `[RECOMMENDATION]`
**How to avoid:** 写入 candidate Markdown后立即 reopen/reparse；emitter API 改为接收 `FinalResumeDocument`。 `[RECOMMENDATION]`
**Warning signs:** 删除/篡改 candidate Markdown 后 Typst bytes 不变。 `[RECOMMENDATION]`

### Pitfall 4: 动态 root discovery 把合法外观的私有文件当 managed
**What goes wrong:** 私人附件或旧残件被自动删除/归档。 `[VERIFIED: teaching-design-package dynamic tests]`
**Why it happens:** 只按扩展名或姓名前缀发现 current。 `[RECOMMENDATION]`
**How to avoid:** current 文件必须全部满足候选人前缀、已登记主题后缀、严格 triple grouping；任何额外文件、partial group、ambiguous group 都 fail closed。 `[RECOMMENDATION]`
**Warning signs:** 根目录出现单独 `.pdf` 仍能继续 batch。 `[RECOMMENDATION]`

### Pitfall 5: 单份 render 误用 batch replace 语义
**What goes wrong:** 更新一个目标时删除其他 current 目标。 `[VERIFIED: D-19]`
**Why it happens:** 两个命令共享一个“candidate 是全部 current”假设。 `[RECOMMENDATION]`
**How to avoid:** transaction 显式区分 `patch` 与 `authoritative_replace`；只有 batch 可产生 removals。 `[RECOMMENDATION]`
**Warning signs:** 单份 render 的 preflight 显示 unrelated removals。 `[RECOMMENDATION]`

### Pitfall 6: metadata 含当前时间或随机 ID
**What goes wrong:** 相同输入每次 Markdown/PDF bytes 都变化，永远无法 no-op。 `[VERIFIED: D-18]`
**Why it happens:** 把 run audit 字段放进公开 YAML/PDF metadata。 `[RECOMMENDATION]`
**How to avoid:** 随机 run ID 只在 `.work`；正式产物只含输入事实、版本化 policy/hash 与固定 creation timestamp。 `[RECOMMENDATION]`
**Warning signs:** 连续两次 batch 创建 history，或唯一 diff 是时间字段。 `[RECOMMENDATION]`

### Pitfall 7: 照片 `.typ` 依赖原始文件
**What goes wrong:** 三件套离开原机器或进入 history 后无法重编译，甚至泄露原始绝对路径/EXIF。 `[VERIFIED: current emitter behavior; D-13]`
**Why it happens:** `image("logical/path")` 仍指向 canonical asset。 `[VERIFIED: graduate_resume_typst.py]`
**How to avoid:** 在 workdir 归一化并嵌入 bytes；禁止正式产物出现源路径。 `[RECOMMENDATION]`
**Warning signs:** 把历史 triple 复制到临时目录后 `typst compile` 失败。 `[RECOMMENDATION]`

### Pitfall 8: history 只保存变化文件
**What goes wrong:** PDF 改变时只归档旧 PDF，旧 Markdown/Typst 无法形成可恢复版本。 `[VERIFIED: D-14]`
**Why it happens:** delta 在文件级而不是 bundle 级计算。 `[RECOMMENDATION]`
**How to avoid:** 先以 stem 分组，再把任一文件变化提升为整个 triple 的 updated。 `[RECOMMENDATION]`
**Warning signs:** 任一 history stem 缺 `.md`、`.typ` 或 `.pdf`。 `[RECOMMENDATION]`

## Code Examples

Verified patterns and recommended adaptations:

### Stable bundle classification

```python
# Source pattern: skills/tiaokedan/scripts/delivery_transaction.py
# Phase 48 adaptation: classify at complete-triple granularity.
def classify_bundles(current, candidate):
    current_stems = set(current)
    candidate_stems = set(candidate)
    unchanged = {
        stem for stem in current_stems & candidate_stems
        if current[stem].path_set == candidate[stem].path_set
        and current[stem].bytes_by_name == candidate[stem].bytes_by_name
    }
    updated = (current_stems & candidate_stems) - unchanged
    return {
        "unchanged": unchanged,
        "updated": updated,
        "added": candidate_stems - current_stems,
        "removed": current_stems - candidate_stems,
    }
```

该结构把 no-op 与 history 决策提升到完整 triple，符合 D-14/D-18。 `[RECOMMENDATION]`

### Strict hard-condition fallback

```python
# Source: Phase 48 locked decision D-05
def resolve_condition(condition, facts, explicit_not_applicable):
    if condition.id in explicit_not_applicable:
        return ConditionResult("not-applicable", (), "explicit-job-instance-override")
    predicate = PREDICATES.match(condition.normalized_text)
    if predicate is None:
        return ConditionResult("unknown", (), "no-controlled-predicate")
    result = predicate.evaluate(facts)
    if result.proven:
        return ConditionResult("meets", result.fact_ids, result.reason)
    if result.disproven:
        return ConditionResult("gap", result.fact_ids, result.reason)
    return ConditionResult("unknown", result.fact_ids, "insufficient-verified-evidence")
```

任何模糊或未覆盖条件都自然落入 unknown。 `[RECOMMENDATION]`

### Deterministic safe component

```python
# Source patterns: teaching-design-package delivery transaction and school-pptx stem validation
def safe_component(display: str) -> str:
    value = unicodedata.normalize("NFKC", display)
    value = CONTROL_OR_SEPARATOR.sub("-", value).strip(" .-")
    value = REPEATED_DASH.sub("-", value)
    if not value or value in {".", ".."} or len(value.encode("utf-8")) > MAX_BYTES:
        raise DeliveryError("UNSAFE_STEM", "输出名无法安全规范化。")
    return value
```

规范化必须先对全部版本完成，再检测 collision；碰撞时使用 target stable ID 的短 SHA-256 后缀确定性消歧，不能覆盖。 `[RECOMMENDATION]`

### Final Markdown reparse gate

```python
markdown_bytes = emit_final_markdown(version_projection, frozen_plan, metadata)
session.write_candidate(markdown_name, markdown_bytes)
final_document = load_final_resume(session.candidate_path(markdown_name))
typst_bytes = emit_typst_from_final(final_document)
session.write_candidate(typst_name, typst_bytes)
compile_pdf(session.candidate_path(typst_name), session.candidate_path(pdf_name))
```

测试应 mutation-check：如果 final Markdown 的 selected IDs 或主题被篡改，reparse/emit 必须失败或改变 Typst，不能静默使用旧内存状态。 `[RECOMMENDATION]`

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `render`/`batch` 返回 `NOT_IMPLEMENTED` | 实现 generic/target × 3 themes 正式矩阵 | Phase 48 | 公开命令名已冻结，可直接填充实现而无需兼容旧成功产物。 `[VERIFIED: graduate_resume_cli.py; phase-46-baseline.md]` |
| 布局器消费全部 canonical facts | 布局器消费不可变 `VersionProjection` | Phase 48 recommendation | 定向选择不污染唯一事实源。 `[RECOMMENDATION]` |
| Typst emitter 消费 facts + plan | emitter 消费重读后的 final Markdown projection | Phase 48 locked contract | Markdown 成为真实编译检查点。 `[VERIFIED: D-12]` |
| 固定 pair/triple 或整套 dynamic set history | 多 stem bundle delta history | Phase 48 locked contract | 未变化版本不归档，更新/移除版本完整归档。 `[VERIFIED: D-14/D-18]` |
| 外部 photo logical path | workdir 归一化后内嵌 photo bytes | Phase 48 recommendation | 三件套与 history 可独立移动/重编译。 `[RECOMMENDATION]` |

**Deprecated/outdated:**
- `command_reserved("render"/"batch")`：Phase 48 实现后应删除 reserved 分支，但保留公开子命令名与稳定 JSON 错误边界。 `[VERIFIED: graduate_resume_cli.py]`
- `emit_typst(plan, facts)`：应保留兼容测试入口或迁移测试，但正式 render 不应绕过 final Markdown。 `[RECOMMENDATION]`

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| — | 无。研究中的未锁定内容均明确标为 recommendation，不作为已验证事实。 | — | — |

## Open Questions (RESOLVED)

1. **硬条件受控谓词首批覆盖哪些字段？**
   - **RESOLVED:** 只覆盖 `education_level`、`major_exact`、`certificate_exact`、`fresh_graduate_status`。年限、地域、年龄、技能熟练度及其他未登记条件稳定输出 `unknown`；不得用相关性词表扩展资格证明。 `[RESOLVED: Claude's Discretion]`

2. **显式 not-applicable 的 CLI 形态如何表达理由？**
   - **RESOLVED:** 唯一公开形态为可重复 `--not-applicable <target-id> <condition-id> <reason>`。ID 使用现有稳定 ID grammar；reason 为单个 UTF-8 参数，trim 后 1..200 code points、禁止控制字符。同一 target/condition 重复、未知 target/condition、generic 使用均稳定报错。 `[RESOLVED: Claude's Discretion]`

3. **照片归一化的固定像素/PPI 是多少？**
   - **RESOLVED:** 用 Typst 0.15.0 在 `35mm × 49mm` 白底零边距页面以 contain 居中重编码为 PNG，固定 `413 × 579` 像素、300 PPI 栅格化基准；输出去 EXIF/源路径并内嵌 `.typ`。不得在 Phase 48 根据文件大小动态降到其他 PPI。 `[RESOLVED: existing dependency; Phase 47 slot]`

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python | CLI/targeting/delivery | ✓ | 3.14.6 | 项目 runtime 文档可声明受支持最低版本；本阶段不更换语言。 `[VERIFIED: local CLI]` |
| PyYAML | frontmatter | ✓ | 6.0.3 | 无；缺失时 fail closed。 `[VERIFIED: local CLI; pip registry]` |
| Typst | PDF/PNG | ✓ | 0.15.0 | 无；版本不符时 fail closed。 `[VERIFIED: local CLI]` |
| skill-local fonts | layout/render | ✓ | manifest/hash controlled | 无系统字体 fallback。 `[VERIFIED: Phase 47 verify passed]` |
| secure dir-fd primitives | delivery transaction | ✓ | `O_DIRECTORY`, `O_NOFOLLOW`, `dir_fd`, `os.replace` supported | 无；缺失时 fail closed。 `[VERIFIED: local capability probe]` |

**Missing dependencies with no fallback:** none in the current research environment. `[VERIFIED: environment probes]`

**Missing dependencies with fallback:** none. `[VERIFIED: environment probes]`

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | 纯本地 CLI，不提供身份认证面。 `[VERIFIED: codebase scope]` |
| V3 Session Management | no | 无会话或远程状态。 `[VERIFIED: codebase scope]` |
| V4 Access Control | limited | 只写用户授权 delivery/work/evidence 路径；不扩大到其他目录。 `[VERIFIED: AGENTS.md; delivery patterns]` |
| V5 Input Validation | yes | restricted YAML/Markdown schema、稳定 ID、safe component、exact set、regular-file/no-follow 校验。 `[VERIFIED: current code and ASVS project]` |
| V6 Cryptography | yes | 使用 stdlib SHA-256 绑定输入/config/assets；随机 run ID 使用 `secrets`，不自写算法。 `[VERIFIED: current repo patterns]` |

OWASP ASVS 是本节分类依据；本阶段重点落在输入验证、文件路径边界、完整性 hash 和敏感信息不泄露。 `[CITED: https://owasp.org/www-project-application-security-verification-standard/]`

### Known Threat Patterns for Python/Typst local rendering

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Markdown/Typst 内容注入 | Tampering / Elevation | 所有 candidate-controlled text 经 `typst_content` 转义；照片和 template import 不接受用户 Typst。 `[VERIFIED: graduate_resume_typst.py]` |
| path traversal / unsafe stem | Tampering | NFKC 后单组件校验、长度上限、禁止 separators/control/`.`/`..`，碰撞预检。 `[RECOMMENDATION]` |
| symlink / directory swap | Tampering / Elevation | `O_NOFOLLOW`、held `(dev, ino)` identity、descriptor-relative stat/replace/unlink。 `[VERIFIED: v1.18 delivery code]` |
| partial publish / interrupted mutation | Tampering | candidate-first、rollback snapshot、INT/TERM handler、post-publish exact set/bytes verify。 `[VERIFIED: v1.18 tests]` |
| contact/photo/source-path leakage | Information Disclosure | stem allowlist字段、hidden evidence、无原始路径、照片归一化后内嵌、root allowlist。 `[VERIFIED: D-13/D-15]` `[RECOMMENDATION]` |
| stale/ambiguous current discovery | Tampering | unknown/partial/ambiguous/stale-work fail closed；只有 batch 可删除 obsolete bundles。 `[VERIFIED: D-16/D-19]` |
| false qualification claim | Spoofing | controlled predicates、evidence IDs、unknown fallback、per-target gap allow。 `[VERIFIED: D-05..D-08]` |

## Validation Notes

`.planning/config.json` 将 `workflow.nyquist_validation` 明确设为 `false`，因此按 GSD 研究协议不生成正式 `## Validation Architecture` section。 `[VERIFIED: .planning/config.json]`

规划仍应在 Phase 48 各计划中安排窄回归：target resolver unit tests、final Markdown round-trip、三主题 candidate matrix、bundle delta/no-op/history/rollback/path safety；Phase 49 再建设聚合故障注入、PDF 结构/布局验证与跨 runtime/UAT。 `[VERIFIED: roadmap boundary]` `[RECOMMENDATION]`

## Research Verification Performed

- `skills/graduate-resume/scripts/graduate-resume.sh verify`：4 个 valid、6 个 invalid、5 个 layout fixture 全部符合预期。 `[VERIFIED: local test run 2026-07-18]`
- `python3 -m unittest` 运行 tiaokedan 与 end-of-term delivery tests：22 tests passed。 `[VERIFIED: local test run 2026-07-18]`
- secure I/O probe：两个 Python delivery analog 的 `_secure_io_capabilities()` 均返回空缺失列表。 `[VERIFIED: local probe]`
- Typst 0.15.0 `compile --help` 确认支持 stdin、`--root`、`--font-path`、`--ignore-system-fonts`、`--creation-timestamp`、`--ppi`。 `[VERIFIED: local CLI]`
- 临时目录实验确认 Typst 0.15.0 可用 `image(bytes((...)), format: "svg")` 编译内嵌图片 bytes。 `[VERIFIED: local experiment]`

## Sources

### Primary (HIGH confidence)
- `.planning/phases/48-deterministic-targeted-rendering-clean-batch-delivery/48-CONTEXT.md` — 全部锁定决策与 Phase 49 边界。
- `.planning/REQUIREMENTS.md` — TARGET-01..03、DELIVERY-01..03。
- `.planning/ROADMAP.md` — 48-01/02/03 计划方向与 success criteria。
- `skills/graduate-resume/scripts/graduate_resume_cli.py` — 当前命令、parser、validation、reserved render/batch。
- `skills/graduate-resume/scripts/graduate_resume_layout.py` — 三主题、照片、容器、冻结 1/2 页计划。
- `skills/graduate-resume/scripts/graduate_resume_typst.py` — Typst 机械发射、文本转义与当前照片路径行为。
- `skills/tiaokedan/scripts/delivery_transaction.py` — Python same-stem triple、exact no-op、history、rollback、held directory。
- `skills/teaching-design-package/scripts/delivery-transaction.js` — dynamic expected set、candidate validation、discovery contract 与 held transaction。
- Typst 0.15.0 local CLI help — compile/root/font/timestamp/PPI 能力。

### Secondary (MEDIUM confidence)
- `.planning/research/PITFALLS.md` — v1.19 定向、隐私、离线、batch 与验证风险。
- `https://owasp.org/www-project-application-security-verification-standard/` — ASVS 分类依据。

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — 没有新增包，版本由当前 registry/CLI 与已通过 Phase 47 实现确认。
- Architecture: HIGH — 直接受 48-CONTEXT 锁定，并有三个已交付 clean-delivery analog 支撑。
- Pitfalls: HIGH — 来自当前代码缺口、v1.19 PITFALLS 和已执行负向事务测试。

**Research date:** 2026-07-18
**Valid until:** 2026-08-17（核心架构稳定；若 Typst 或 schema 版本变化需提前重查）
