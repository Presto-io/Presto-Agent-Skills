# Project Research Summary

**Project:** Presto Agent Skills v1.17 `school-pptx`
**Domain:** 学校固定模板 Markdown-to-editable-PPTX 技能
**Researched:** 2026-07-13
**Confidence:** HIGH for milestone scope, feature boundary, and documented `python-pptx`/Pandoc capabilities; MEDIUM for transition XML and cross-viewer PPTX behavior until fixture验证。

## Executive Summary

`school-pptx` 应作为一条新的可编辑 PPTX 技能线，而不是 `school-presentation` 的 HTML 导出扩展。专家做这类固定学校模板生成器时，不应让 Markdown 控制坐标、字体、颜色或任意 PPT XML；正确边界是模板拥有视觉和几何，Markdown 拥有逻辑内容，renderer 负责分页、适配和写入可编辑 PPTX 对象。

推荐路线是先把人类友好的 `.potx` 视觉样例手工归一化为 skill-local 标准 `.pptx` 模板，再用 manifest/slot map 固定 11 个 layout 的 placeholder、frame geometry、预算和 overflow 规则。随后定义 YAML + `::: slide {layout="..."}` Markdown contract，最后用 Python + `python-pptx` 生成文本、图片、表格、notes、timeline、gallery、code 等可编辑对象，并通过 OOXML/ZIP 结构检查做 verification gate。

主要风险是把原始 `.potx`、截图式高保真、复杂动画、自由 Markdown 样式或“文件非空”误当成功标准。缓解方式必须进入 requirements 和 verification：标准模板和 slot map 是硬前置；Markdown 必须受限；逻辑页可扩展为多张物理页；文本/表格/代码/notes 必须可验证为可编辑对象；转场仅在可靠保留或生成并通过 XML/Office 兼容验证时启用，否则无动画通过。

## Key Findings

### Recommended Stack

第一版应保持轻量、skill-local、可跨 Codex/Claude/Gemini/OpenCode/OpenClaw/Hermes Agent 安装。`python-pptx` 是主 PPTX writer；Pandoc 更适合做 Markdown AST/contract 辅助和参考转换，不应作为最终 PPTX renderer；OOXML 只用于小范围检查和受控后处理。

**Core technologies:**
- Python 3.11+：skill-local renderer、verifier、CLI orchestration；不要把本机 Python 3.14 作为用户硬要求。
- `python-pptx==1.0.2`：打开标准 `.pptx` 模板，写 slides、text、pictures、tables、speaker notes，并读回做 smoke verification。
- Pandoc 3.x CLI：解析/规范化 Markdown、辅助 AST fixture 和 notes/slide-level contract 验证；不负责最终版式。
- Python `zipfile` + XML inspection：检查 PPTX package、relationships、notes parts、media parts、layout references、transition XML。
- 标准 `.pptx` 模板 + `template-manifest.yaml`：作为 renderer 的 layout/slot/budget 真相源。

**Version requirements:**
- `python-pptx` 需固定到当前研究确认的 1.0.2 线，并在 `verify` 中记录 import/version。
- Pandoc 作为外部 CLI 前置项记录版本；本地已验证有 Pandoc 3.10，但技能不能假设所有 runtime 已安装。
- 转场/动画不得基于未验证的内部 API；任何 Open XML patch 都必须 fixture-gated。

### Expected Features

**Must have (table stakes):**
- 新建 `skills/school-pptx/` canonical `SKILL.md`，包含六 runtime adapter notes，OpenClaw/Hermes 是必需目标。
- Markdown-first 工作流：先形成教师可审阅 `school-pptx-full.md`，脚本只消费定稿 Markdown。
- 固定 YAML 字段：`title/subtitle/school/department/program/course/author/presenter/date/theme`；未知值不得虚构。
- 受控 `theme`，未知 theme 硬失败或要求用户选择。
- 显式 `::: slide {layout="..."}`，不靠标题或视觉猜 layout。
- 11 个固定 layout：`cover/contents/section/title-content/two-column/image-text/table/timeline/gallery/code/closing`。
- 自动 contents：从所有 `##` 生成，`#` 只作文档标题 fallback。
- 逻辑页自动扩展为物理页，覆盖长正文、长表格、timeline、gallery。
- 可编辑 PPTX 对象：文本、表格、图片、notes、timeline、gallery、plain code 都不能整页截图冒充。
- 图片 contain 等比放置；gallery 每页 4 图；timeline 横向；code 可编辑无高亮。
- 重复可验证输出：example/render/verify 能检查 slide count、layout mapping、manifest、notes、media、table、pagination、非空 PPTX。

**Differentiators:**
- 从 `.potx` 视觉样例手工归一化为标准 `.pptx`，避免脚本猜测人类模板。
- 固定 frame geometry 和 slot map，保证学校模板一致性。
- 有界弹性文本策略：字号只在可读范围内调整，超出即分页。
- logical-to-physical manifest，让用户和 verifier 知道一页 Markdown 拆成哪些 PPTX 页。
- 可解释降级报告：转场、代码高亮、复杂表格等不稳定能力要写入 manifest/控制台摘要。

**Deferred (v2+):**
- 代码语法高亮。
- 复杂对象动画。
- 任意模板导入或市场模板 autodetection。
- 智能图表/SmartArt。
- 自动内容改写。
- 高级表格样式。
- 图片裁切/焦点控制。
- PPTX 到 PDF/图片导出。

**Out of scope for v1.17:**
- 直接 source-to-target，无 Markdown intermediate。
- 把 `school-presentation` HTML renderer 当 PPTX 输出方案。
- Markdown 控制坐标、字体、颜色、crop、animation XML。
- 整页截图式 PPTX。
- 强加全局页脚。
- 复杂动画和未验证转场。
- 托管分享、课堂互动、浏览器播放控件。

### Architecture Approach

架构应采用 standalone skill folder：`SKILL.md` 是轻入口，长规则放 `references/`，教师模板放 `templates/`，脚本入口放 `scripts/school-pptx.sh`，Python internals 放 `scripts/school_pptx/`。核心数据流是：source materials / supplied POTX -> hand-normalized standard PPTX template + manifest -> teacher-reviewable Markdown logical deck -> parser/pagination model -> editable PPTX renderer -> hidden verification evidence + public PPTX output。

**Major components:**
1. `templates/school-standard.pptx`：归一化后的机器可映射模板，包含稳定 layout 和 placeholder。
2. `references/template-manifest.yaml`：layout id、slot name、placeholder idx/name、EMU geometry、字体预算、overflow 策略。
3. `references/markdown-contract.md`：YAML、`theme`、slide block、notes、layout allowlist、禁止 styling escape hatch。
4. `templates/school-pptx.md`：覆盖 11 个 layout、notes、media、pagination 的全功能 fixture。
5. `scripts/school-pptx.sh`：稳定命令面，至少提供 `example`、`template-report`、`render`、`verify`。
6. `scripts/school_pptx/markdown_parser.py`：解析 frontmatter、slide blocks、notes、media、tables、code。
7. `scripts/school_pptx/template_model.py`：读取 manifest，检查模板 layout/slot 映射。
8. `scripts/school_pptx/pagination.py` / `fit.py`：在写 PPTX 前完成 logical -> physical splitting 和预算判断。
9. `scripts/school_pptx/pptx_writer.py`：用 `python-pptx` 写可编辑对象。
10. `scripts/school_pptx/ooxml_inspector.py` / `verify.py`：结构化检查 PPTX package、notes、relationships、media、layout、object editability。

**Key architecture decisions:**
- 模板标准化先于 renderer：`.potx` 是视觉证据，不是运行时 contract。
- Manifest/slot map 是 renderer 的唯一几何和预算真相源。
- Markdown contract 只表达语义内容和允许的 layout，不表达视觉参数。
- Renderer 拥有分页、文本适配、continuation slide 和输出 manifest。
- OOXML verify 补足 `python-pptx` 读写 API 不覆盖的结构检查，尤其 notes、relationships、transitions、package invariants。

### Critical Pitfalls

1. **把 `.potx` 当运行时模板输入** — 先手工归一化为标准 `.pptx`，再用 `template-report` 验证 layouts/placeholders/geometry。
2. **Markdown grammar 太自由** — requirements 必须限制为 YAML + slide blocks + controlled theme，拒绝 raw HTML、坐标、字体、颜色、任意 styling。
3. **整页截图或图片捷径破坏可编辑性** — verification 必须检查文本/code 是 text shapes，表格是 table objects，图片是 picture relationships。
4. **PowerPoint 打开即误判成功** — gate 必须检查 slide count、layout IDs、placeholder fills、notes、media、table dimensions、manifest mapping、OOXML invariants。
5. **转场/动画过度承诺** — v1.17 默认无动画；0.5s smooth transition 仅在模板保留或 XML patch 经 fixture 证明后启用。
6. **字体和 autofit 不稳定** — 用 manifest 预算和有界字号 fallback，超出预算分页，不依赖 PowerPoint 视觉 overflow。
7. **OpenClaw/Hermes 运行假设未写清** — adapter notes 必须覆盖 whole-folder installation、support-file discovery、script allowlist、write boundary 和 dependency checks。

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 41: Standard Template and Manifest

**Rationale:** 模板和 slot map 是后续 Markdown、renderer、verify 的共同前置；没有稳定 template contract，所有后续工作都会漂移。
**Delivers:** `skills/school-pptx/` skeleton、`templates/school-standard.pptx`、`references/template-normalization.md`、`references/template-manifest.yaml`、`template-report` 初版和 fixture evidence。
**Addresses:** 标准模板归一化、固定 frame geometry、11 layout inventory、受控 theme。
**Avoids:** 原始 `.potx` autodiscovery、dirty master/layout、placeholder inheritance mismatch、转场误承诺。

### Phase 42: Markdown Contract and Full Fixture

**Rationale:** 用户可见输入面必须先稳定，renderer 才能按合同实现；这也继承仓库 Markdown-first 的既有成功模式。
**Delivers:** `references/markdown-contract.md`、`templates/school-pptx.md` 全 layout fixture、parser/model 层 validation、contents 从 `##` 生成的测试证据。
**Addresses:** YAML 字段、controlled `theme`、显式 slide blocks、notes 语法、table/code/image/timeline/gallery 合同、deferred/out-of-scope 边界。
**Avoids:** Markdown-level styling、目录 heading 混淆、未知 layout/theme 静默 fallback、未解决 review markers 进入渲染。

### Phase 43: Editable PPTX Renderer and Pagination

**Rationale:** 有模板 contract 和 Markdown contract 后，renderer 才能集中实现可编辑对象、contain 图片、逻辑页分页和输出 manifest。
**Delivers:** `render` 命令、`python-pptx` writer、logical-to-physical manifest、text/table/timeline/gallery/code pagination、notes 写入、media resolver、clean public output。
**Uses:** Python 3.11+、`python-pptx==1.0.2`、manifest/slot map、Pandoc AST 或结构化 Markdown parser。
**Implements:** parser、layout engine、pagination、fit、pptx_writer、hidden evidence。
**Avoids:** screenshot PPTX、PowerPoint visual overflow、placeholder stale handles、notes slide accidental creation、hidden diagnostics 泄漏。

### Phase 44: Verification Gate, Runtime Notes, and UAT Evidence

**Rationale:** PPTX 文件“存在”不是验收；必须把结构化验证、负例、runtime adapter、manual visual UAT 作为交付门槛。
**Delivers:** `verify --workdir`、dependency gate、template gate、parser negative tests、render/readback checks、OOXML inspection、clean-output check、six-runtime adapter notes、PowerPoint/WPS/Keynote 或 fallback viewer 手工 UAT 记录。
**Addresses:** slide count、layout map、notes、media、tables、code text、pagination、non-empty/openable PPTX、standalone skill install。
**Avoids:** false green、runtime discovery failure、OpenClaw/Hermes support drift、transition XML corruption。

### Phase Ordering Rationale

- Template/manifest first because layout names、slot geometry、placeholder ids 和预算定义了 Markdown 能表达什么。
- Markdown contract second because parser、fixture、contents、notes 和 unsupported syntax 必须在 renderer 前稳定。
- Renderer third because可编辑对象和 pagination 依赖已锁定的 template + Markdown contract。
- Verification last as milestone acceptance gate，但每个阶段都应带局部验证；最终 phase 聚合结构化 PPTX gate、负例和 runtime notes。

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 41:** 真实 `.potx` 到标准 `.pptx` 的归一化、placeholder idx/name/geometry、notes master 状态、转场保留策略需要样例级研究。
- **Phase 43:** `python-pptx` notes、table insertion、placeholder replacement、字体/autofit、图片 contain、editable timeline/gallery primitives 需要实现 spike。
- **Phase 44:** OOXML inspection、transition XML、PowerPoint/WPS/Keynote compatibility、OpenClaw/Hermes runtime install behavior 需要 fixture/UAT 研究。

Phases with standard patterns (skip research-phase unless new evidence appears):
- **Phase 42:** Markdown-first contract、显式 review markers、fixture-first、unsupported syntax hard fail 已有本仓库模式可复用。
- **Phase 44 adapter docs 部分:** 六 runtime adapter notes 的文档结构已有模板；重点是补本技能的 dependency/write-boundary 细节。

## Risks for Requirements and Verification Gates

**Must enter requirements:**
- Renderer consumes normalized skill-local `.pptx`, not raw `.potx`.
- Normalized template has committed layout/placeholder/slot map.
- Markdown contract is constrained to YAML + explicit slide blocks.
- `theme` is a controlled identifier, not a style object.
- Logical slides may expand into multiple physical slides.
- Text、tables、notes、images、timeline、gallery、code must be editable PPTX objects where applicable.
- Whole-slide screenshot PPTX is banned.
- Complex object animation is out of scope; transition is optional and gated.
- `school-pptx` is standalone and skill-local; no sibling skill runtime dependency.
- OpenClaw and Hermes Agent adapter notes are mandatory.

**Must enter verification gates:**
- Dependency gate: `python3` imports `pptx`; version recorded; wrapper `--help` works.
- Template gate: `.pptx` opens; masters/layouts/placeholders/names/types/idx/geometry match manifest.
- Markdown gate: invalid layout/theme, raw HTML, unsupported styling, missing media, unresolved markers fail non-zero with locatable errors.
- Render gate: PPTX opens; slide count and logical-to-physical mapping match manifest.
- Contents gate: generated from `##` only; `#` not duplicated into contents except title fallback.
- Notes gate: expected notes exist; slides without notes do not accidentally gain notes.
- Object editability gate: no full-slide screenshot shortcut; text/code/tables/images/timeline/gallery represented structurally.
- Pagination gate: long text/table/timeline/gallery fixtures split predictably; table headers repeat.
- Clean output gate: public output excludes manifests/logs/status/temp/debug JSON unless explicitly requested or failure diagnostics.
- Runtime adapter gate: Codex/Claude/Gemini/OpenCode/OpenClaw/Hermes notes cover support files, script execution, dependencies, and write boundaries.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH/MEDIUM | HIGH for `python-pptx` documented slides/shapes/tables/pictures/notes and Pandoc documented PPTX/AST behavior; MEDIUM for transition post-processing and cross-viewer compatibility. |
| Features | HIGH | Based on `.planning/PROJECT.md`, active v1.17 scope, existing Markdown-first skill family, and confirmed first-version boundaries. |
| Architecture | HIGH/MEDIUM | HIGH for repository structure、standalone skill pattern、Markdown logical deck pattern；MEDIUM for exact PPTX placeholder/notes behavior until fixture proof. |
| Pitfalls | HIGH/MEDIUM | HIGH for known python-pptx/template/Markdown risks from official docs and local project patterns；MEDIUM for OpenClaw/Hermes exact runtime execution until validated. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- Real `.potx` sample behavior: planning must decide exact normalization evidence and whether to commit `.pptx` plus extracted placeholder-map JSON.
- Font policy: choose minimum Chinese font/fallback strategy for macOS/Linux/OpenClaw/Hermes and avoid relying on unavailable metrics.
- Transition mode: decide whether to defer entirely or preserve template transition only; do not make it a success dependency.
- Parser implementation choice: Pandoc JSON vs Python Markdown parser needs a small spike focused on fenced div attributes and line-local diagnostics.
- Manual visual UAT: structural checks are necessary but not sufficient; first accepted template needs at least one PowerPoint-compatible visual review.

## Sources

### Primary (HIGH confidence)
- `.planning/PROJECT.md` — v1.17 goal, active requirements, out-of-scope, repository constraints, milestone history.
- `.planning/research/STACK.md` — recommended stack, dependency boundaries, `python-pptx`/Pandoc/OOXML division of labor.
- `.planning/research/FEATURES.md` — table stakes, differentiators, anti-features, MVP recommendation, acceptance checklist.
- `.planning/research/ARCHITECTURE.md` — component boundaries, directory structure, command surface, manifest/slot map, pagination model.
- `.planning/research/PITFALLS.md` — risks, required requirement gates, verification gates, phase warnings.
- `python-pptx` official documentation — slides, placeholders, pictures, tables, text frames, notes, unsupported feature boundaries.
- Pandoc manual — Markdown-to-PPTX, `reference.pptx`, slide-level, speaker notes, layout-name behavior.

### Secondary (MEDIUM confidence)
- Microsoft Open XML / PresentationML documentation — package structure and transition XML feasibility, still requiring fixture validation.
- Context7 python-pptx extracts cited by PITFALLS — cross-check for notes, placeholders, tables, autofit behavior.

### Tertiary (LOW confidence)
- None used as decision source.

---
*Research completed: 2026-07-13*
*Ready for roadmap: yes*
