# Technology Stack

**Project:** v1.19 `graduate-resume` / 毕业生高级简历生成器
**Researched:** 2026-07-17
**Scope:** 纯 CLI 的 Markdown -> Typst -> PDF 简历渲染；中文字体、照片、1/2 页 A4 收敛、PDF 证据和六 runtime 运行边界。
**Overall confidence:** HIGH（Typst、pypdf、Pillow 的公开能力和本机 CLI 均已核对）；MEDIUM（最终字体视觉效果仍需在受支持 OS 上以 fixture 验收）。

## Recommended Stack

### Core Runtime

| Technology | Version | Purpose | Why |
|---|---:|---|---|
| Python | 3.11+ | skill-local CLI、Markdown/YAML contract、定向规则、版面计划、候选发布和验证 | 与现有 Typst 文档技能一致；标准库足以负责路径、JSON、subprocess、哈希和事务，不需要 Node 或运行时网络。不要把开发机的 Python 3.14.6 作为最低要求。 |
| Typst CLI | `0.15.0`，固定为 tested 版本 | `candidate.typ -> candidate.pdf`、同源 PNG 审阅图、A4 排版 | 本机已验证 `typst 0.15.0`；CLI 提供 `--root`、`--font-path`、`--ignore-system-fonts`、`--creation-timestamp`、`--pdf-standard` 和 PNG 输出。它是唯一 PDF 生成器，版面完全由受控主题模板拥有。 |
| PyYAML | `6.0.3`（或锁定已验收版本） | 解析 Markdown front matter / YAML 定向清单 | schema 必须稳定而非依赖自然语言解析；仅接受安全加载后的受限字段。保留 Markdown 正文为可审阅内容，YAML 只承载结构元数据。 |
| Python stdlib | 随 Python | 文件交易、SHA-256、Unicode/path 验证、JSON evidence、子进程退出码 | 避免增添 orchestrator/数据库/服务依赖；已标准化资料后的流程完全离线、零 AI token。 |

### Chinese Fonts and Theme Assets

| Technology / asset | Version / policy | Purpose | Why |
|---|---|---|---|
| Noto Sans CJK SC / Source Han Sans CN font bundle | 固定、可再分发的字库快照；以许可证清单随 skill 交付 | 简体中文正文、标题、联系方式 | 不可使用 macOS 的苹方、Windows 的微软雅黑或开发机的思源字体作为隐式前提。不同 runtime/OS 的系统字库不一致，会改变换行、页数和 PDF 字形。选择可随 skill 安装、覆盖简中与常用 Latin 的开源 CJK 字体。 |
| 可选 Noto Serif CJK SC bundle | 同一受控快照 | 仅在某个主题确需衬线标题时使用 | 与无衬线正文字库同样显式提供；不得以系统宋体作为 fallback。v1 首选单一 Sans 主题，减少度量漂移。 |
| 模板自带 SVG/PNG 图标 | skill-local allowlist | 电话、邮箱、地址等固定图标 | 不拉取 icon CDN，也不让 Markdown 注入任意 SVG/URL；固定资源可审计且离线可用。 |
| Pillow | `12.3.0`（锁定已验收版本） | 照片解码、EXIF 方向归正、尺寸/格式/像素上限验证、生成受控 JPEG/PNG candidate asset | 官方 API 有 `ImageOps.exif_transpose` 与 `contain`/`fit`；在主题渲染之前标准化人像，消除手机拍照方向和超大图带来的不确定性。 |

### PDF and Evidence

| Technology | Version | Purpose | Why |
|---|---:|---|---|
| pypdf | `6.14.2` | 确认 PDF 可读取、页数、每页 `mediabox`、基础文本抽取与 metadata | 纯 Python，不依赖桌面 Office。A4 必须逐页为约 `595.28 x 841.89 pt`；页数只能是 1 或 2。它是结构 gate，不承担视觉排版判断。 |
| Typst PNG export | 与 Typst 同版本 | 在 `.work/<run-id>/evidence/` 生成每页审阅 PNG | 从与 PDF 相同的 candidate `.typ` 以固定 `--ppi 144` 生成，供 fixture 图像 diff / 人工 UAT 使用；不进入 public delivery。避免把本机 Poppler、Ghostscript 或浏览器当作必备依赖。 |
| `pdfinfo` | optional diagnostic only | 在存在时交叉记录 PDF page size / metadata | 本机有 Poppler `pdfinfo 26.05.0`，但不是六 runtime 的硬前置。其缺失不能改变核心 gate 的真值。 |

## Required Invocation Model

```bash
# prerequisites are verified, never installed automatically by the skill
python3 --version
typst --version
python3 -c 'import yaml, PIL, pypdf'

# deterministic render: custom fonts only, fixed project root and timestamp
SOURCE_DATE_EPOCH=0 typst compile \
  --root "$candidate_root" \
  --font-path "$skill_root/fonts" \
  --ignore-system-fonts \
  --creation-timestamp 0 \
  --pdf-standard 1.7 \
  "$candidate_root/resume.typ" "$candidate_root/resume.pdf"

# hidden, same-source visual evidence (one PNG per physical page)
typst compile --root "$candidate_root" --font-path "$skill_root/fonts" \
  --ignore-system-fonts --ppi 144 "$candidate_root/resume.typ" \
  "$work_root/evidence/resume-{0p}.png"
```

The actual wrapper must pass an absolute, validated project root; it must not trust the caller's current directory. Font names in `.typ` must be tested with `typst fonts --font-path "$skill_root/fonts" --ignore-system-fonts`, and the template must set `fallback: false` after selecting the bundled CJK family. A missing glyph then fails visibly during fixture testing rather than silently changing to a system font.

## Layout-Convergence Recommendation

Do **not** attempt to infer final page count from character counts or by shrinking every font until compilation succeeds. Use a bounded, deterministic planner before publication:

1. Validate schema and calculate semantic modules: header, summary, education, skills, projects, internships and awards. Each experience/project is a non-splittable item with an identifier.
2. Render a finite ordered density ladder for the selected theme, for example `regular`, `compact`, then `two-page`. Only theme-owned constants may change: spacing, heading rhythm, approved summary-line cap and item cap. The raw student Markdown never changes.
3. Compile each candidate, then use pypdf to measure 1/2 pages and A4 media boxes. A 1-page profile is accepted only when it fits intact. The two-page profile has an explicit semantic partition and explicit `pagebreak()` between sections.
4. Emit every experience/project in Typst `block(breakable: false, ...)`. The official Typst layout API confirms this prevents a block splitting across pages. If an item cannot fit on an otherwise valid page, fail with its identifier; do not create an orphan heading or unheaded continuation.
5. Accept the first profile satisfying all structural rules. If none does, fail closed with a short actionable overflow report. Never rasterize text, silently drop material, reduce text below theme accessibility minimum, or emit a third page.

The renderer can use Typst's automatic pagination inside an allowed section, but page 2 must be logically planned. It must reject: a heading as the final usable block on a page, a section with no following item, any split `experience_id`, an empty second page, or a nonempty third page. Template-level visual UAT is still required because PDF structural inspection cannot prove every line is aesthetically balanced.

## Photo Pipeline

1. `--photo` is optional. No-photo is a first-class layout variant; do not leave an empty photo frame or reflow arbitrary content.
2. Resolve only a regular local file below the allowed input/media root; reject symlinks, URLs, SVG/HTML/PDF masquerading as images, unsupported mode/format and excessive file/pixel dimensions.
3. Treat Pillow `DecompressionBombWarning` as an error and retain a finite `Image.MAX_IMAGE_PIXELS`; official Pillow security guidance explicitly warns against disabling this limit.
4. Decode, run `ImageOps.exif_transpose`, convert to sRGB RGB/RGBA, and generate a bounded JPEG or PNG into candidate-owned `assets/`. Record original hash, normalized hash, size and profile in hidden evidence, not in public resume content.
5. Let Typst use a theme-owned fixed photo frame with `fit: "cover"` only after the contract explicitly allows center crop. Do not permit user-controlled crop coordinates. For identification photos, `contain`/padding is the safer default if head cropping would be unacceptable.

## Cross-Runtime Dependency Boundary

The canonical `SKILL.md` must state the same runtime-neutral command path for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw and Hermes Agent. Runtime adapters may explain discovery and sandbox configuration, but must not fork renderer behavior.

| Boundary | Mandatory policy |
|---|---|
| Install unit | Install the complete `skills/graduate-resume/` folder: `SKILL.md`, `scripts/`, `templates/`, bundled `fonts/`, fixed icons, fixtures and references. A script may not call a sibling skill at runtime. |
| External prerequisites | Python 3.11+, Typst 0.15.0, PyYAML, Pillow and pypdf. `typst` must be on `PATH`; Python imports and exact/accepted version range must be checked before any current-delivery mutation. |
| No hidden provisioning | The skill never runs `pip install`, downloads Typst/fonts/icons, accesses an LLM API, invokes a browser, or calls a desktop application. Missing dependencies produce one non-zero, actionable prerequisite error. |
| Sandbox / allowlist | Grant execute for the wrapper and `typst`; read for the whole skill folder and approved input/photo roots; write only for the explicit delivery root and its owned `.work/`. No network permission is required. |
| OpenClaw / Hermes | Both require installation-time whole-folder discovery, explicit shell-wrapper fallback, prerequisite probe, and a small fixture render. Do not claim automatic script discovery unless that runtime has been tested. |
| Delivery | Reuse v1.18 candidate-first exact managed bundle, no-op and whole-bundle history rules. Candidate is Markdown + Typst + PDF + only explicitly managed normalized photo assets; logs, page PNGs, plan JSON and hashes stay under owned `.work/`. |

## Alternatives Considered

| Category | Recommended | Alternative | Why not |
|---|---|---|---|
| Typesetting | Typst CLI | LaTeX/XeLaTeX | CJK font setup, package installation and cross-machine reproducibility add operational burden without helping the short, controlled resume layout. |
| Typesetting | Typst CLI | Pandoc direct PDF | Pandoc does not own the theme-specific page planner, non-splitting item contract, or photo/layout details; adding it would create a second formatting authority. |
| PDF conversion | Typst direct PDF | LibreOffice headless / Word / WPS automation | Requires viewer installation and OS-specific typography; cannot provide a portable six-runtime contract. |
| PDF inspection | pypdf + Typst PNG evidence | Browser screenshots as the only verification | Browser availability and PDF rendering vary. Screenshots are supplementary visual evidence, not a structural source of truth. |
| Image processing | Pillow | ImageMagick | ImageMagick is a large external runtime and policy surface for the small, bounded photo-normalization job. |
| Fonts | bundled open CJK fonts | system font fallback | Font availability and metrics vary by OS; it directly breaks the 1/2-page guarantee. |
| Dynamic fitting | bounded semantic density ladder | arbitrary auto-shrink / CSS-like overflow hiding | It can meet page count by damaging readability or deleting semantics; it also makes results hard to audit. |
| Runtime orchestration | Python CLI | Node service / web UI / LLM invocation | Violates the zero-token, offline batch-render requirement and multiplies runtime compatibility work. |

## Implementation Preconditions

- Select and license-review the exact font files before writing the first visual fixture. Record their SHA-256 values and tested Typst family names in a font manifest.
- Establish two or more approved visual fixtures, including Chinese/Latin mixed text, dense two-page content, no-photo and portrait-photo variants. Acceptance needs PNG/PDF human review on at least macOS and one non-macOS supported environment before claiming stable cross-platform layout.
- Define an explicit schema field for every item that must not split (`experience_id`, `project_id`, `award_id`) and an ordered section policy for the two-page profile.
- Make all theme density constants data in a template manifest; source Markdown/YAML cannot set raw fonts, sizes, margins, page breaks, file paths or Typst expressions.
- Define exact public filenames and asset policy before coding publication. Unknown files, partial prior bundles, symlinks, failed font probes, invalid photos, page count outside 1/2, non-A4 pages, or structural pagination violations must fail before current mutation.
- Test the Typst lock/version with `SOURCE_DATE_EPOCH=0`; use byte equality only for identical inputs and pinned tool/font versions. Otherwise retain v1.18's no-op contract without promising PDF bytes are universally reproducible across unpinned hosts.

## Sources and Confidence

| Source | Confidence | What it establishes |
|---|---|---|
| Typst CLI local `typst 0.15.0`, `typst compile --help` | HIGH | `--root`, custom/isolated font paths, `SOURCE_DATE_EPOCH`, PDF standard, page-select and PNG export are current in the workspace. |
| Typst official CLI / layout / text / image docs: https://typst.app/docs/reference/cli/ , https://typst.app/docs/reference/layout/block/ , https://typst.app/docs/reference/text/text/ , https://typst.app/docs/reference/visualize/image/ | HIGH | Non-splitting blocks, font fallback controls and image fit policy. |
| Typst official release page: https://github.com/typst/typst/releases/tag/v0.15.0 | HIGH | Tested CLI release line. |
| pypdf official docs: https://pypdf.readthedocs.io/en/stable/ | HIGH | `PdfReader` page count and per-page `mediabox` structural checks. Local PyPI metadata reports `6.14.2`. |
| Pillow official docs/security: https://pillow.readthedocs.io/en/stable/reference/ImageOps.html , https://pillow.readthedocs.io/en/stable/reference/Image.html , https://pillow.readthedocs.io/en/stable/handbook/security.html | HIGH | EXIF transpose, bounded resize helpers and decompression-bomb handling. |
| Existing v1.18 clean-delivery contracts and Typst skill scripts in this repository | HIGH | Candidate-first publication, exact bundle/no-op/history/rollback boundary that v1.19 must reuse. |

## Roadmap Recommendation

1. **Stack and font baseline**: vendor/license fonts, lock Typst/Python package prerequisites, build the prerequisite probe and create visual Typst fixtures.
2. **Shared schema and theme contract**: parser/validator, controlled theme manifest, no-photo/photo variants and safe Pillow normalization. Keep all style and density controls out of student data.
3. **Renderer and bounded convergence**: Markdown -> Typst, semantic density ladder, one/two-page partition and non-splitting blocks.
4. **Evidence and six-runtime gate**: PDF page/A4/readability structure checks, PNG visual fixtures, candidate publication/rollback, and installation-time adapter verification including OpenClaw/Hermes.

Phase 1 must precede layout work: without pinned fonts, every page-budget result is provisional. Phase 3 must precede final publication mechanics: the delivery layer should publish only a renderer output already proven to satisfy page and structural constraints.
