# Phase 47: 受控主题、照片与冻结布局 - Pattern Map

**Mapped:** 2026-07-18  
**Files analyzed:** 8 个文件/目录面  
**Analogs found:** 6 / 8

## File Classification

| 新建/修改文件 | 角色 | 数据流 | 最近范例 | 匹配质量 |
|---|---|---|---|---|
| `scripts/graduate_resume_cli.py` | CLI/controller | request-response、batch fixture | 同文件 | exact |
| `scripts/graduate_resume_layout.py` | service/model | transform、分页规划 | `skills/school-pptx/scripts/pptx_model.py` + `pptx_paginate.py` | role-match |
| `scripts/graduate_resume_typst.py` | service/utility | transform、file-I/O | `skills/tiaokedan/scripts/tiaokedan_renderer.py` | role-match |
| `templates/resume-themes.typ` | template/config | transform、layout | `skills/end-of-term-teaching-materials/templates/typst/end-of-term-package.typ` | partial |
| `fonts/manifest.json` 与字体文件 | config/assets | file-I/O、integrity | `skills/school-presentation/references/identity/asset-manifest.json` | partial |
| `fixtures/layout/*`、`fixtures/media/*` | fixture/test data | batch、file-I/O | `skills/graduate-resume/fixtures/*.md` | role-match |
| `SKILL.md` | documentation/config | request-response | 同文件 | exact |
| `references/phase-46-baseline.md` | documentation | transform contract | 同文件 | exact |

## Pattern Assignments

### `skills/graduate-resume/scripts/graduate_resume_cli.py`（CLI，request-response）

**Analog:** 同文件；这是唯一现有的 `graduate-resume` 公共命令面，Phase 47 必须在此扩展，不能另造平行入口。

**子命令与参数注册**（`skills/graduate-resume/scripts/graduate_resume_cli.py:88-122`）：

```python
parser = argparse.ArgumentParser(prog="graduate-resume.sh")
subparsers = parser.add_subparsers(dest="command", required=True)

plan = subparsers.add_parser("plan", help="输出 Phase 46 基线计划与依赖探测。")
plan.add_argument("--input", required=True, help="输入 Markdown 路径。")
```

在既有 `plan` 上增加主题、页数和照片模式 override，仍先 `load_resume()`、`validate_document()`，再委托布局模块。`render`/`batch` 的保留边界不可提前移除。

**已验证事实进入派生计划的顺序**（同文件 `:512-536`）：

```python
document = load_resume(args.input)
validate_document(document)
data = document.data
photo = data.get("photo", {})
preferences = data.get("preferences", {})
```

**照片模式的优先级**（同文件 `:501-509`）：

```python
def resolve_photo_mode(photo: dict[str, Any], preferences: dict[str, Any]) -> str:
    declared = preferences.get("photo_mode")
    if declared == "no-photo":
        return "no-photo"
    if photo.get("status") == "no-photo":
        return "no-photo"
    if photo.get("status") == "provided":
        return "photo"
    return "auto"
```

Phase 47 在此决议点补真实本地路径、受限根、非 symlink、可读常规文件检查；不得把绝对照片路径写回 plan JSON 或 Typst。

**稳定错误与 JSON 边界**（同文件 `:539-594`）：

```python
raise CliError("NOT_IMPLEMENTED", message)
...
except CliError as exc:
    payload = {"status": "failed", "code": exc.code, "message": exc.message}
    if exc.details:
        payload["issues"] = exc.details
    print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
    return 2 if exc.code in {"VALIDATION_FAILED", "NOT_IMPLEMENTED"} else 64
```

新增 `LAYOUT_UNSATISFIABLE`、`LAYOUT_RENDER_MISMATCH`、字体/照片诊断时复用此边界；只暴露稳定代码、短消息与受限详情。

### `skills/graduate-resume/scripts/graduate_resume_layout.py`（布局 service/model，transform）

**Analog:** `skills/school-pptx/scripts/pptx_model.py` 与 `skills/school-pptx/scripts/pptx_paginate.py`。两者均将语义输入转为不可变物理计划，发射器不能改写计划。

**不可变嵌套计划与 JSON 投影**（`skills/school-pptx/scripts/pptx_model.py:77-153`）：

```python
@dataclass(frozen=True, slots=True)
class PhysicalSlide:
    logical_index: int
    physical_index: int
    fragments: tuple[BlockFragment, ...]

    def to_projection(self) -> dict[str, Any]:
        return {"fragments": [fragment.to_projection() for fragment in self.fragments]}

@dataclass(frozen=True, slots=True)
class PhysicalDeckPlan:
    slides: tuple[PhysicalSlide, ...]
```

按此形状建立 `ThemeSpec`、`ContainerPlan`、`EntryBudget`、`PagePlan`、`PageRecommendation`、`FrozenResumePlan`，全用 `@dataclass(frozen=True, slots=True)`、tuple 与 `to_projection()`。计划必须包含 UI-SPEC 锁定的 `theme`、精确 `page_count`、`photo_mode`、`font_manifest_hash`、`pages`、`containers`、`entry_budget`、`reorder_reason` 和 recommendation。

**纯规划器入口与有界失败**（`skills/school-pptx/scripts/pptx_paginate.py:881-997`）：

```python
def build_deck_plan(document: dict[str, Any], manifest: dict[str, Any]) -> PhysicalDeckPlan:
    if sum(len(slide.get("blocks", ())) for slide in logical_slides) > MAX_BLOCKS:
        diagnostic = RenderDiagnostic(code="PAGINATION_RESOURCE_LIMIT", ...)
        return PhysicalDeckPlan((), (diagnostic,), ())
    ...
    return PhysicalDeckPlan(tuple(slides), tuple(diagnostics), tuple(mapping))
```

布局模块保持无 CLI/stdout/Typst 编译 I/O 的纯函数边界。先投影保持 `section` 与事实 ID 的容器，再估算并尝试 1/2 页；项目、实训、经历、证书条目作为不可分割单元，技能组标题必须与至少一项内容一起放置。个人信息首页首位、教育前部是不可移动锚点。

**保守 CJK 测量与冻结字号**（同文件 `:87-161`）：

```python
class TextMeasure:
    """Conservative CJK-aware estimator with no file, font-search, or PPTX I/O."""
    def measure(self, text: str, *, width_emu: int, font_size: float,
                font_size_min: float, font_size_max: float, ...) -> TextMeasurement:
        selected_size = clamp_font_size(font_size, font_size_min, font_size_max)
```

复用“测量器不做文件/字体发现”的职责分离，但不沿用 PPTX 的 EMU 或自动 clamp 语义：本阶段字体、字号、行距下限已冻结，密度只可按 UI-SPEC 的空字段、省略允许重排、间距阶梯处理。

### `skills/graduate-resume/scripts/graduate_resume_typst.py`（Typst 发射 service，transform/file-I/O）

**Analog:** `skills/tiaokedan/scripts/tiaokedan_renderer.py`。

**用户事实转义**（`skills/tiaokedan/scripts/tiaokedan_renderer.py:301-311`）：

```python
def typst_content(value: str) -> str:
    parts = re.split(r"<\s*br\s*/?\s*>", value.strip(), flags=re.I)
    escaped = [part.replace("\\", "\\\\").replace("#", "\\#")
               .replace("[", "\\[").replace("]", "\\]") for part in parts]
    return "#linebreak()".join(escaped)
```

新发射器应有同类单一转义函数，所有事实文本都经它输出；不得把 Markdown 或照片路径当作原始 Typst 代码拼接。

**模板/数据分离的发射形式**（`skills/end-of-term-teaching-materials/scripts/end_of_term/_engine.py:1215-1240`）：

```python
template = read_text(template_path)
return (
    template.replace("{{DOCUMENT_TITLE}}", typst_string(document_title))
            .replace("{{DOCUMENT_AUTHOR}}", typst_string(document_author))
            .replace("{{PACKAGE_BODY}}", "\n#pagebreak()\n".join(body).strip() + "\n"),
    warnings,
    flags,
)
```

读取 skill-local `resume-themes.typ`，仅以冻结计划的页/栏/容器序列填充。发射前校验计划完备性；不得重新测量、排序、添删模块或根据剩余空间产生 `pagebreak()`。

**外部 Typst 调用的失败检查**（`skills/tiaokedan/scripts/tiaokedan_renderer.py:484-508`）：

```python
result = subprocess.run([typst, "compile", str(typ_path), str(pdf_path)],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
if result.returncode != 0:
    raise DeliveryError(f"typst compile failed with exit code {result.returncode}{detail}")
payload = pdf_path.read_bytes()
if not payload.startswith(b"%PDF-"):
    raise DeliveryError(f"typst compile produced an invalid PDF header: {pdf_path}")
```

Phase 47 fixture 编译扩展参数为受控 `--font-path`、`--ignore-system-fonts`、`--creation-timestamp 0`，输出仅进调用者临时 workdir。正式 bundle 发布仍属 Phase 48。

### `skills/graduate-resume/templates/resume-themes.typ`（模板/config，布局 transform）

**Analog:** `skills/end-of-term-teaching-materials/templates/typst/end-of-term-package.typ`，但其固定坐标版式只适合模板结构，不可复制其系统字体 fallback 或裁剪策略。

**模板的受控全局设置与宏**（该文件 `:5-28`）：

```typst
#set page(width: 595.3pt, height: 841.9pt, margin: 0pt)
#set text(lang: "zh", font: (...), size: 12pt)
#let ptext(x, y, w, h, size, body, pos: center + horizon, weight: "regular") = ...
{{PACKAGE_BODY}}
```

新模板将其替换为 A4、14/14/15/15 mm 安全边距、锁定 Source Han Sans SC 400/600、四级字号和 spacing token。定义纯视觉三主题 token、页栏、照片槽位和 `fact-block`/`list-entry` 宏；`list-entry` 必须以 `block(breakable: false)[...]` 输出。候选人事实只能来自发射器，不得硬编码进模板。

### `skills/graduate-resume/fonts/manifest.json` 与受控字体（config/assets，file-I/O）

**Analog:** `skills/school-presentation/references/identity/asset-manifest.json` 的“相对路径 + SHA-256”资产身份模式；该仓库没有可直接复制的字体 manifest，因此字体字段结构为新契约。

清单至少列出相对文件名、族名、weight（400/600）、SHA-256、许可证/来源记录。布局规划器先读取/验证清单、计算确定 `font_manifest_hash`，再允许构建 `FrozenResumePlan`；文件缺失、哈希不符或 Typst 在 `--ignore-system-fonts` 下不可见时失败关闭。不得扫描系统字体作为 fallback。

### `skills/graduate-resume/fixtures/layout/*`、`fixtures/media/*`（fixture，batch/file-I/O）

**Analog:** `skills/graduate-resume/fixtures/*.md` 与同文件的固定 fixture 注册表。

**固定正负例集合**（`skills/graduate-resume/scripts/graduate_resume_cli.py:76-89,546-572`）：

```python
VALID_FIXTURES = ("valid-photo-single-target.md", ...)
INVALID_FIXTURES = ("error-missing-required.md", ...)
...
for fixture_name in VALID_FIXTURES:
    summary = validate_document(load_resume(str(fixtures_root / fixture_name)))
...
else:
    raise CliError("VERIFY_FAILED", f"负例 fixture 意外通过: {fixture_name}")
```

新增布局 fixture 也应以显式、稳定的列表/矩阵注册，而非运行时发现目录。复用当前 Markdown v2 事实格式（例如 `valid-photo-single-target.md:1-33`），仅在 `fixtures/media/` 添加公开、非敏感的测试照片。覆盖短、标准、临界、压力、长字段、有/无照片、强制 1/2 页和两页不可满足；每例断言 plan projection、Typst 文本和 PDF 的页数/锚点/条目原子性，且无照片例负向扫描路径与图像引用。

### `skills/graduate-resume/SKILL.md` 与 `references/phase-46-baseline.md`（文档，契约说明）

**Analog:** 同文件已有的阶段边界文档；遵循 `AGENTS.md` 的 canonical 语言中立规则。

更新只写：唯一事实源仍为 `graduate-resume.md`、`plan` 产生冻结布局、受控字体/本地照片要求、可执行验证命令，以及 `render`/`batch` 仍是 Phase 48 范围。不要把 Codex、Claude 等 runtime 私有语法写入 canonical 主体；复杂布局细节留在 reference。

## Shared Patterns

### 输入校验与稳定错误
**Source:** `skills/graduate-resume/scripts/graduate_resume_cli.py:400-441,575-594`  
**Apply to:** CLI、照片解析、布局计划、fixture 验证。

先验证资料，再构造派生值；失败抛 `CliError`，顶层统一 JSON stderr。新错误码必须可机器判定，且不泄露绝对路径、EXIF 或未受信任文本。

### 冻结计划优先
**Source:** `skills/school-pptx/scripts/pptx_model.py:77-153`; `pptx_paginate.py:881-997`  
**Apply to:** `graduate_resume_layout.py`、`graduate_resume_typst.py`、plan fixture。

规划器产出 immutable projection，发射器只消费它。页数、条目页面归属、容器、照片模式、字体身份与重排理由都进入计划；任何渲染后不一致都必须失败，而不是由模板自行修补。

### Typst 文本安全与受控编译
**Source:** `skills/tiaokedan/scripts/tiaokedan_renderer.py:301-307,484-508`; `skills/end-of-term-teaching-materials/scripts/end_of_term/_engine.py:1361-1375`  
**Apply to:** Typst 发射、布局 fixture。

事实文本统一转义；编译检查退出码、可读文件和 PDF header。Phase 47 再叠加受控字体目录、忽略系统字体、固定时间戳、A4/精确页数和结构门禁。

### 显式 fixture 回归
**Source:** `skills/graduate-resume/scripts/graduate_resume_cli.py:76-89,546-572`  
**Apply to:** CLI `verify` 与新 `fixtures/layout/`。

fixture 集合固定且正负例均有预期结果；验证不得因目录中遗漏/新增文件而静默改变覆盖面。

## No Analog Found

| 文件/契约 | 角色 | 数据流 | 原因 |
|---|---|---|---|
| `graduate_resume_layout.py` 的三段式 1/2 页 recommendation 与受限重排 | service/model | transform | 仓库仅有 PPTX 多页分页，没有简历精确 1/2 页和双版本对照语义。 |
| `resume-themes.typ` 的三主题、固定照片槽与不可拆条目宏 | template | layout | 无既有 Typst 简历主题或同等照片/分页契约。 |
| `fonts/manifest.json` 的 Source Han Sans SC 许可证/双字重 hash 结构 | config/assets | file-I/O | 有资产 SHA-256 清单，但无受控字体清单。 |
| 布局 PDF 的 A4、页首锚点、无照片泄露和条目跨页结构 gate | test | batch | 当前 graduate-resume 仅有 schema fixture；完整 PDF 验证将由本阶段首次建立。 |

## Metadata

**Analog search scope:** `skills/graduate-resume/`、`skills/school-pptx/scripts/`、`skills/tiaokedan/scripts/`、`skills/end-of-term-teaching-materials/`  
**Files scanned:** 16  
**Pattern extraction date:** 2026-07-18
