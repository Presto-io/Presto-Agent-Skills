# Phase 48: 确定性定向渲染与干净批量交付 - Pattern Map

**Mapped:** 2026-07-18
**Files analyzed:** 15 个建议创建/修改文件
**Analogs found:** 15 / 15

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `skills/graduate-resume/scripts/graduate_resume_cli.py` | controller / CLI | request-response | 同文件现有 `validate/target/plan/verify` | exact |
| `skills/graduate-resume/scripts/graduate_resume_targeting.py` | service / model | transform | `graduate_resume_layout.py` 的冻结 dataclass + 校验边界 | role-match |
| `skills/graduate-resume/scripts/graduate_resume_final_markdown.py` | service / parser | transform + file-I/O | `graduate_resume_cli.py` 的受限 frontmatter parser | role-match |
| `skills/graduate-resume/scripts/graduate_resume_render.py` | service / coordinator | batch + file-I/O | `school-pptx/scripts/pptx_render.py` 的 candidate-first render coordinator | role/data-flow match |
| `skills/graduate-resume/scripts/graduate_resume_delivery.py` | service / transaction | batch + file-I/O | `tiaokedan/scripts/delivery_transaction.py` + `school-pptx/scripts/pptx_render.py` | role/data-flow match |
| `skills/graduate-resume/scripts/graduate_resume_layout.py` | service / model | transform | 同文件现有 `FrozenResumePlan` | exact |
| `skills/graduate-resume/scripts/graduate_resume_typst.py` | service / emitter | transform | 同文件现有机械 emitter | exact |
| `skills/graduate-resume/templates/targeting-policy.json` | config | transform | `templates/layout-measurement.json` | exact role |
| `skills/graduate-resume/references/targeted-render-delivery-contract.md` | config / contract | request-response | `references/schema-and-review-contract.md` | exact role |
| `skills/graduate-resume/SKILL.md` | config / canonical workflow | request-response | 同文件 Phase 46/47 渐进披露结构 | exact |
| `skills/graduate-resume/scripts/test_phase48_targeting.py` | test | transform | `test_layout_contract.py` / `test_theme_contract.py` | role-match |
| `skills/graduate-resume/scripts/test_phase48_render.py` | test | batch + file-I/O | `test_layout_fixtures.py` | role/data-flow match |
| `skills/graduate-resume/scripts/test_phase48_delivery.py` | test | batch + file-I/O | `tiaokedan/scripts/test_delivery_transaction.py` | exact role/data-flow |
| `skills/graduate-resume/fixtures/phase48/*.md` | test fixture | transform | `fixtures/valid-multi-target.md` 与 `fixtures/layout/*.md` | exact role |
| `skills/graduate-resume/templates/graduate-resume.md` | template | CRUD / human review | 同文件现有稳定 ID、target、preferences 表达 | exact |

> 文件名来自 `48-RESEARCH.md` 的推荐结构；测试可按 planner 拆为 3 个文件或合并为一个 `test_phase48_contract.py`，但职责和覆盖矩阵不要合并丢失。

## Pattern Assignments

### `graduate_resume_cli.py`（CLI controller）

**Analog:** `skills/graduate-resume/scripts/graduate_resume_cli.py`

**稳定错误对象**（92-100）：

```python
class CliError(Exception):
    def __init__(self, code: str, message: str, details: list[str] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or []
```

**命令只负责解析与调度**（109-141、602-626）：保留现有 `argparse` 子命令；将 `render`、`batch` 从 reserved 分支替换为 `command_render`、`command_batch`，仍由 `main()` 统一把稳定错误转成 JSON 和非零退出，不让 traceback 穿过公开边界。

**加载顺序**（468-477、519-534）：每个公开命令先 `load_resume()`，再 `validate_document()`，之后才导入布局/渲染模块。Phase 48 应继续保持 `validate` 不依赖 Typst、delivery 或 render 环境。

**雷区：** 不要在 CLI 中实现评分、四态判定、文件命名或事务；CLI 只冻结参数、调用 service，并打印预检/结果。`render` 是 patch 语义，`batch` 是 authoritative replace 语义，必须在调用 delivery 时显式区分。

---

### `graduate_resume_targeting.py`（不可变投影 + 四态条件）

**Analog:** `skills/graduate-resume/scripts/graduate_resume_layout.py`

**冻结模型**（28-57、66-88、104-141）：

```python
@dataclass(frozen=True, slots=True)
class ThemeSpec:
    key: str
    label: str
    ...

@dataclass(frozen=True, slots=True)
class EntryBudget:
    container_id: str
    source_fact_id: str
    height_mm: float
```

照此定义 `VersionProjection`、`FactDecision`、`ConditionResult`、`OverrideSnapshot`；所有 tuple/digest/version 字段在构造时冻结，并提供 `to_projection()` 输出 JSON-safe 值。

**自校验模式**（143-171）：模型拥有 `validate(canonical_facts)`，验证 selected ID 全部来自已核实事实、核心事实未被排除、trace 覆盖每个候选事实、condition 的 `meets/gap` 带证据 ID、overrides 不冲突。

**稳定排序模式**（203-224）：先按受控模块顺序遍历，再把条目映射为新对象；不得原地修改 `document.data`。同分使用稳定事实 ID，而不是正文顺序。

**四态雷区：** 相关性评分只用于选择/排序；硬条件只有受控 predicate 可输出 `meets` 或 `gap`，否则必须 `unknown`。`not-applicable` 只能来自本次显式 condition override，且包含非空理由。

---

### `graduate_resume_final_markdown.py`（最终 Markdown 检查点）

**Analog:** `skills/graduate-resume/scripts/graduate_resume_cli.py`

**受限 frontmatter 解析**（148-177）：

```python
raw = path.read_text(encoding="utf-8")
if not raw.startswith("---\n"):
    raise CliError("FRONTMATTER_REQUIRED", "输入缺少 YAML frontmatter。")
parts = raw.split("\n---\n", 1)
parsed = yaml.safe_load(parts[0][4:]) or {}
if not isinstance(parsed, dict):
    raise CliError("YAML_ROOT_INVALID", "YAML frontmatter 顶层必须是映射对象。")
```

新模块应提供 `emit_final_markdown(...) -> bytes` 与 `load_final_resume(...) -> FinalResumeDocument`。写入 candidate 后必须重新打开并解析，校验 `graduate-resume-delivery/v1`、canonical hash、policy/hash、version、theme、page/photo、selected fact IDs、trace summary、condition counts/digest 和 gap allow snapshot。

**雷区：** 不要把完整逐事实理由、condition matrix、随机 run ID 或当前时间写入正式 YAML；完整理由进入 `.work/<run>/evidence/*.json`。Typst emitter 只能消费重读后的 `FinalResumeDocument`，不能继续消费写 Markdown 前的 Python 对象。

---

### `graduate_resume_layout.py`（消费投影的冻结布局）

**Analog:** 同文件现有实现。

**入口模式**（262-298）：`build_frozen_resume_plan()` 先验证参数、加载版本化测量配置、构造容器、分别尝试 1/2 页、选择主页面，再 `plan.validate(...)`。Phase 48 只把第一个参数从完整 canonical dict 收紧为 version projection 的已选事实视图。

**配置 hash**（227-238）：

```python
raw = path.read_bytes()
payload = json.loads(raw)
...
return values, version, hashlib.sha256(raw).hexdigest()
```

**雷区：** 不要在布局器里重新评分、重新判断 hard requirements 或补回被投影排除的事实；comparison page 只写 preview/evidence，不进入正式 stem。

---

### `graduate_resume_typst.py`（机械 Typst emitter）

**Analog:** 同文件现有实现。

**内容转义**（12-14）：

```python
return value.replace("\\", "\\\\").replace("#", "\\#").replace("[", "\\[").replace("]", "\\]").replace("\n", "#linebreak()")
```

**冻结消费**（32-64）：按 frozen pages/containers 固定顺序发射，不做 pagination、sorting、measurement 或 target resolution。

**必须替换的旧模式**（53-57）：当前 `image("logical/path")` 会让历史 triple 依赖原始照片。正式 emitter 应消费 final Markdown 中冻结的照片模式，并把 workdir 内规范化后的图像 bytes 嵌入 `.typ`；正式 `.typ` 不得含绝对路径、原始相对照片路径、URL 或 EXIF 文本。

---

### `graduate_resume_render.py`（版本×三主题候选协调）

**Analog:** `skills/school-pptx/scripts/pptx_render.py`

**先构造和验证、后发布**（772-839）：先读取输入、parse、build frozen plan、生成 candidate、校验 staged package；只有所有 diagnostics 为空才调用 `session.publish(...)`。失败的 best-effort 产物只留在 owned work evidence，不能成为 current。

**Phase 47 编译参数**（`test_layout_fixtures.py` 35-58）：

```python
common = [
    "typst", "compile",
    "--font-path", str(SKILL_ROOT / "fonts"),
    "--ignore-system-fonts",
    "--creation-timestamp", "0",
    str(typst_path),
]
```

协调器应：展开 generic/target versions；每个 version 固定展开 `conservative/modern/expressive`；生成 final Markdown；重读；生成 Typst；编译 PDF；验证每个 stem 恰有 `.md/.typ/.pdf`；最后一次性把完整 candidate matrix 交给 delivery。

**雷区：** batch 不得边生成边发布；任一 target、theme、gap gate、stem collision、Typst/PDF 或 candidate triple 失败都必须在打开 mutation 阶段前结束。正式产物不得包含 preview、diagnostic、condition JSON 或照片中间件。

---

### `graduate_resume_delivery.py`（动态多 bundle 事务）

**Primary analog:** `skills/tiaokedan/scripts/delivery_transaction.py`

**held-directory session**（82-118）：先探测 `O_DIRECTORY/O_NOFOLLOW/dir_fd/os.replace`，打开 delivery root 并冻结 `(st_dev, st_ino)`，检查 current，再创建 `.work/run-*/candidate|rollback|evidence`。

**根目录 allowlist / partial / stale fail-closed**（147-183）：只允许 managed names 与 `sources/assets/history/.work`；任何 unknown、非普通 current、partial bundle、symlink support dir 或 stale `.work` 立即失败。

**no-op、history、signal rollback**（361-409）：candidate 全量校验后读取 current；path set 与 bytes 完全相同直接返回 `identical`；变更前写 rollback 与 history；捕获 `SIGINT/SIGTERM`；发布后 exact-set/bytes 验证；任何异常执行 rollback。

**Dynamic-set adaptation analog:** `skills/school-pptx/scripts/pptx_render.py` 386-448：

```python
candidate_names = self.spec.current_names
candidate = self._bundle_bytes(self.candidate_root, candidate_names)
...
mutation_names = tuple(dict.fromkeys((*candidate_names, *old_names)))
for name in mutation_names:
    if name in candidate:
        os.replace(self.candidate_root / name, self.root / name)
    else:
        (self.root / name).unlink()
```

Phase 48 必须先按 stem 分组为完整 triple，再分类 `unchanged/added/updated/removed`：单份 render 禁止 removed；batch 才允许 removed。history 只写 updated/removed 的旧完整 triple，不能归档 unchanged，也不能只归档发生字节变化的单文件。

**雷区：** 不要靠拆连字符反向解析单位/岗位；current discovery 以候选人安全前缀、登记主题后缀和严格 triple grouping 判定。任何 partial/ambiguous group、stem collision、未知根文件或历史缺件都 fail closed。

---

### `targeting-policy.json`（版本化离线策略）

**Analog:** `skills/graduate-resume/templates/layout-measurement.json` 1-8。

保持小型、显式、带 `policy_version`，将整数 score、模块顺序、exact-term expansions、首批 controlled predicates 放在 JSON；加载时校验精确字段集并冻结 SHA-256。不要把 target/company 实例或用户 overrides 写回策略文件。

---

### `targeted-render-delivery-contract.md` 与 `SKILL.md`

**Analog:** `schema-and-review-contract.md` 5-16、61-90；`SKILL.md` 38-45、73-90。

长契约文档负责：投影/trace、四态条件、gap allow、final Markdown schema、正式命名、三主题矩阵、patch vs authority、history/no-op/rollback、隐藏 evidence 与照片自包含。

Canonical `SKILL.md` 只更新公开工作流、命令示例、输出与安全边界，并链接新 reference；继续把六 runtime 差异留在 adapter notes。不得把 Codex/Claude 私有命令或 Phase 49 跨 runtime 验收写进 canonical 主流程。

---

### Phase 48 tests 与 fixtures

**Transaction analog:** `skills/tiaokedan/scripts/test_delivery_transaction.py` 92-200、245-304。

必须复制的断言形态：

- identical 不创建 history，且 inode/mtime 不变（92-105）。
- 任一单文件 bytes 变化时归档旧完整 bundle（107-123）。
- 每个 fault point、`SIGINT`、`SIGTERM` 后 `snapshot(root)` 与运行前完全相同（124-160）。
- unknown、legacy、symlink、partial、lock、stale work 在 mutation 前失败并保留现场（162-200）。
- 编译/候选验证失败不改变 current/history（269-294）。

**Render matrix analog:** `test_layout_fixtures.py` 79-149。用字面 fixture/主题 registry，不动态发现用户文件；逐主题覆盖有照、无照、临界、压力与不可满足页数。

Phase 48 新增 fixture 至少覆盖：多 target 三主题；generic；hard requirement 的 meets/gap/unknown/not-applicable；按 target ID 放行 gap；retain/exclude/pin 冲突；核心事实 exclude；safe stem collision；目标减少；单份更新保留其他版本；照片 triple 移动后 `.typ` 可重编译。

## Shared Patterns

### Authentication / Network

不适用。该技能是纯本地 CLI；不得新增联网抓取、远程图片下载、凭据或 token 路径。

### Error Handling

**Source:** `graduate_resume_cli.py` 92-100、602-626。

所有新模块向上抛稳定 `CliError(code, message, details)`；公开 CLI 只输出 bounded JSON。底层未知异常不能伪装为业务成功，也不应泄露候选人事实、绝对路径、condition evidence 或 traceback。

### Candidate-First

**Source:** `school-pptx/scripts/pptx_render.py` 772-839；`tiaokedan/scripts/delivery_transaction.py` 361-409。

解析、投影、四态、gap gate、布局、Markdown round-trip、Typst/PDF、命名、完整 triple 与完整矩阵预检全部完成后，才允许读取并变更 current。

### Exact Managed Set

**Source:** `end-of-term-teaching-materials/scripts/end_of_term/delivery.py` 119-150、236-247。

候选与 current 都必须匹配声明的精确 managed path set；普通文件、非空、无 symlink。Phase 48 将固定四文件集扩展为“安全 stem -> 固定三件套”的动态映射。

### Determinism

- 正式 metadata 不含当前时间、随机 run ID 或机器路径。
- target `as_of` 是用户事实，可保留；PDF creation timestamp 固定 `0`。
- policy、font manifest、measurement、canonical input 均用 SHA-256 绑定。
- 同分排序按稳定 ID；文件名 NFKC 安全规范化后统一碰撞检测。

## No Analog Found

没有完全缺失的角色。`graduate_resume_targeting.py` 与 `graduate_resume_final_markdown.py` 没有同领域的完整实现，但现有冻结 dataclass、受限 Markdown parser、candidate-first renderer 足以提供结构样板；其中四态 predicate 与 final Markdown delivery schema 应以 `48-RESEARCH.md` 为语义来源，不要从相似代码臆造。

## Planner Landmines

1. 不要把 Phase 48 规划成一个巨大 CLI 文件；targeting、final Markdown、render、delivery 是不同失败边界。
2. 不要把“相关性”当“资格证明”；未命中 controlled predicate 必须是 `unknown`。
3. 不要让 Typst 绕过最终 Markdown；必须进行 write -> reopen -> parse -> emit。
4. 不要把单份 render 当 authoritative batch；单份不得删除其他 current stem。
5. 不要按文件级 delta 归档；任一文件变化提升为整个 triple 更新。
6. 不要归档 unchanged stem；精确 no-op 必须保持 inode/mtime。
7. 不要让照片 `.typ` 引用原始路径；历史 triple 必须可独立移动和重编译。
8. 不要把 evidence、preview、normalized photo 或 condition JSON 放进 delivery root。
9. 不要在本阶段承诺 Phase 49 的跨 runtime、聚合故障注入、PDF 结构/UAT。

## Metadata

**Analog search scope:** `skills/graduate-resume/`, `skills/tiaokedan/`, `skills/end-of-term-teaching-materials/`, `skills/school-pptx/`
**Primary files scanned:** 12
**Pattern extraction date:** 2026-07-18
**Repository pattern vintage:** 现有 analog 最近提交日期为 2026-07-18
