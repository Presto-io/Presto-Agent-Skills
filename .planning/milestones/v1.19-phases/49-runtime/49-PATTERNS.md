# Phase 49: 聚合验证、跨 Runtime 与发布验收 - Pattern Map

**Mapped:** 2026-07-19
**Files analyzed:** 16 个预计新建或修改路径
**Analogs found:** 15 / 16（`runtime_install_fixture.py` 无现成可执行同类，仅有契约级 partial analog）

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `skills/graduate-resume/scripts/graduate_resume_cli.py` | controller / CLI | request-response + batch | 同文件现有 `command_verify()`；`skills/school-pptx/scripts/verify_school_pptx.py` public verify | exact（修改） |
| `skills/graduate-resume/scripts/graduate_resume_verify.py` | service / verification domain | batch + file-I/O + transform | `skills/school-pptx/scripts/verify_school_pptx.py` | exact |
| `skills/graduate-resume/scripts/graduate_resume_pdf_gate.py` | service / artifact observer | file-I/O + transform | 同文件现有 `verify_rendered_layout()` | exact（扩展） |
| `skills/graduate-resume/scripts/test_phase49_verify.py` | test | batch + fault-injection | `skills/graduate-resume/scripts/test_phase48_cli.py`；`skills/school-pptx/scripts/verify_school_pptx.py` mutation guards | exact |
| `skills/graduate-resume/scripts/runtime_install_fixture.py` | utility / installation verifier | batch + file-I/O + request-response | `docs/compatibility-matrix.md` Installation Checks | partial；无可执行 analog |
| `skills/graduate-resume/references/phase-49-verification-contract.md` | config / contract documentation | transform | `skills/school-pptx/references/verification-contract.md` | exact |
| `skills/graduate-resume/references/cross-environment-uat.md` | config / UAT documentation | human event-driven + file-I/O | `skills/school-pptx/references/visual-uat.md` | exact |
| `skills/graduate-resume/templates/phase-49-uat.md` | config / human record template | human event-driven + file-I/O | `skills/school-pptx/references/visual-uat.md` + `_validate_uat_record()` | role-match |
| `skills/graduate-resume/fixtures/verification/normal-photo.md` | test fixture | transform | `skills/graduate-resume/fixtures/layout/standard-photo.md` | exact |
| `skills/graduate-resume/fixtures/verification/no-photo.md` | test fixture | transform | `skills/graduate-resume/fixtures/valid-no-photo.md` | exact |
| `skills/graduate-resume/fixtures/verification/multi-target.md` | test fixture | transform + batch | `skills/graduate-resume/fixtures/valid-multi-target.md` | exact |
| `skills/graduate-resume/fixtures/verification/qualification-gap.md` | test fixture | transform | `skills/graduate-resume/fixtures/targeting/multi-state-targets.md` | exact |
| `skills/graduate-resume/fixtures/verification/content-pressure.md` | test fixture | transform | `skills/graduate-resume/fixtures/layout/pressure-two-pages.md` | exact |
| `skills/graduate-resume/SKILL.md` | config / canonical workflow | request-response | 同文件现有 Runtime Adapter Notes、Outputs、Verification | exact（修改） |
| `docs/compatibility-matrix.md` | config / runtime matrix | transform | 同文件 Installation Checks 与六 runtime rows | exact（修改） |
| `skills/README.md` | config / skill index | transform | 同文件现有 `graduate-resume` 索引行 | exact（修改） |

说明：研究建议把 publication fault 作为固定 gate 在隔离复制树中注入，而不是再维护一份会漂移的“故障 fixture”源文件。`graduate-resume.sh` 已是透明 shell dispatcher（第 1–5 行），预计无需修改即可承载 `verify --workdir`。

## Pattern Assignments

### `skills/graduate-resume/scripts/graduate_resume_cli.py`（controller，request-response + batch）

**Primary analog:** 同文件现有 public CLI，辅以 `skills/school-pptx/scripts/verify_school_pptx.py` 的 public verify 编排。

**子命令接入模式**（`graduate_resume_cli.py` lines 124-159）：

```python
subparsers = parser.add_subparsers(dest="command", required=True)
# ...
verify = subparsers.add_parser("verify", help="运行 Phase 46 fixture 回归与依赖探测。")
verify.add_argument(
    "--fixtures-root",
    default=str(default_skill_root() / "fixtures"),
    help="fixture 根目录，默认使用 skills/graduate-resume/fixtures。",
)
```

Phase 49 应沿用同一 argparse/main dispatch 形状，把 public contract 收束为显式 `--workdir`；不要让 CLI 动态发现 gate、fixture 或 runtime。

**现有 verify 边界**（lines 961-994）：

```python
def command_verify(args: argparse.Namespace) -> int:
    fixtures_root = Path(args.fixtures_root).expanduser().resolve()
    if not fixtures_root.is_dir():
        raise CliError("FIXTURES_NOT_FOUND", f"fixtures 目录不存在: {fixtures_root}")
    # fixed valid/invalid/layout fixtures
    payload = {
        "status": "passed",
        "results": results,
        "runtime_probe": runtime_probe(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0
```

保留稳定 JSON public boundary，但将生产、观察、最终裁决委派给独立 `graduate_resume_verify.py`。顶层不能继续硬编码 `"status": "passed"`，必须读取 observer model 后重算。

**稳定错误出口**（lines 997-1025）：

```python
except Exception as exc:
    if not isinstance(getattr(exc, "code", None), str) or not isinstance(getattr(exc, "message", None), str):
        payload = {"status": "failed", "code": "INTERNAL_ERROR", "message": "离线命令执行失败，正式投递未改变。"}
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 70
    payload = {"status": "failed", "code": exc.code, "message": exc.message}
    print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
```

Phase 49 新 verifier 的 domain errors 应继续穿过该出口，不泄露 traceback、绝对路径或原始简历事实。

---

### `skills/graduate-resume/scripts/graduate_resume_verify.py`（service，batch + file-I/O）

**Analog:** `skills/school-pptx/scripts/verify_school_pptx.py`

**固定 registry 常量模式**（lines 31-88）：

```python
VERIFY_GATE_ORDER = (
    "dependency-readiness",
    "example-generation",
    "template-validation",
    "canonical-render",
    "structural-inspection",
    "phase-43-regression",
    "negative-cases",
    "evidence-integrity",
)
VERIFY_REQUIRED_GATES = frozenset({...literal same IDs...})
NEGATIVE_CASE_ORDER = (...literal IDs...)
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
```

Phase 49 的 gate ID、顺序和 required set 同样必须是字面常量。不要从 test discovery、目录列表或当前环境构造 denominator。

**独立候选校验与裁决**（lines 439-466, 519-522）：

```python
required = tuple(registry.get("required", ()))
called = tuple(registry.get("called", ()))
if required != VERIFY_GATE_ORDER or len(required) != len(set(required)):
    raise VerifyFailure("VERIFY_EVIDENCE_INVALID")
if called != expected_called or len(called) != len(set(called)):
    raise VerifyFailure("VERIFY_EVIDENCE_INVALID")
if registry.get("dynamic_skips") != 0 or registry.get("unique") is not True:
    raise VerifyFailure("VERIFY_EVIDENCE_INVALID")
if include_integrity and candidate.get("status") != _aggregate_status(gates, list(called)):
    raise VerifyFailure("VERIFY_EVIDENCE_INVALID")

def _aggregate_status(gates, called):
    complete = tuple(called) == VERIFY_GATE_ORDER
    all_passed = complete and all(gates[name]["status"] == "passed" for name in VERIFY_GATE_ORDER)
    return "passed" if all_passed else "failed"
```

Phase 49 在此模式上增加三态：只有自动 gates、Phase 48 前置、六 runtime 与 mutation guard 全通过，且 UAT 是合法全 PENDING 时才能返回 `human_needed`；任一其他缺失、stale、FAIL/BLOCKED 均为 `failed`。

**顺序执行并保留失败行模式**（lines 952-1010）：

```python
called = []
gates = {}
dependency = dependency_gate()
gates["dependency-readiness"] = dependency
called.append("dependency-readiness")
if dependency.get("status") == "passed":
    # run literal gates and append each ID
else:
    for name in VERIFY_GATE_ORDER[1:-1]:
        gates[name] = blocked_result()
        called.append(name)
# integrity is always materialized
gates["evidence-integrity"] = integrity
called.append("evidence-integrity")
candidate["registry"]["called"] = list(called)
candidate["status"] = _aggregate_status(gates, called)
```

关键不是“遇错就少跑”，而是固定 registry 仍完整产生 observed/blocked outcome，保持 `required == called` 与零动态 skip。

**同源 JSON/Markdown + 原子 evidence 发布**（lines 525-595）：JSON 和 Markdown 从同一个 candidate 生成；发布前再次 `validate_candidate(..., include_integrity=True)`，再以 caller-owned evidence fd 原子替换。Phase 49 应保持 acceptance JSON/Markdown、PNG、raw logs、runtime rows、UAT 全部在 verify workdir，正式 delivery root 仍只保留 triples。

---

### `skills/graduate-resume/scripts/graduate_resume_pdf_gate.py`（artifact observer，file-I/O + transform）

**Analog:** 同文件现有实现。

**Imports 与错误归一化**（lines 5-19）：

```python
import fitz
from PIL import Image
from graduate_resume_cli import CliError

LAYOUT_RENDER_MISMATCH = "LAYOUT_RENDER_MISMATCH"

def _fail(message: str) -> None:
    raise CliError(LAYOUT_RENDER_MISMATCH, message)
```

继续复用 PyMuPDF/Pillow，不引入新 PDF/PNG parser。Phase 49 可细化 stable codes，但仍通过 `CliError` 进入 bounded public error boundary。

**真实 reopen 模式**（lines 26-58）：

```python
if not pdf_path.read_bytes().startswith(b"%PDF-"):
    _fail("受控产物不是 PDF。")
document = fitz.open(pdf_path)
page_texts = [page.get_text("text") for page in document]

with Image.open(png_path) as image:
    rgb = image.convert("RGB")
    width, height = rgb.size
    # derive background and inspect visible pixels against safe bounds
```

Phase 49 必须在 reopen 后新增实际 page rect/A4、字体集合、PNG 数量/尺寸/照片区域、每页 hashes 等观察值；不要把“magic bytes/可打开”当 gate 结论。

**冻结计划交叉检查**（lines 61-89）：

```python
plan.validate(facts)
page_texts = _page_texts(pdf_path)
if len(page_texts) != plan.page_count or len(page_texts) not in (1, 2) or len(png_paths) != plan.page_count:
    _fail("PDF/PNG 页数与冻结计划不一致。")
# first-page profile anchor, second-page module heading,
# every container fact on exactly its assigned page
```

扩展时保持“从 final Markdown/facts 重建 plan，再观察 PDF/PNG”的方向；不要信任 renderer 写入的页数、主题、照片模式或 producer `passed`。

---

### `skills/graduate-resume/scripts/test_phase49_verify.py`（test，batch + fault-injection）

**Primary analog:** `skills/graduate-resume/scripts/test_phase48_cli.py`

**字面 acceptance registry**（lines 22-41）：

```python
PHASE48_ACCEPTANCE_REGISTRY = (
    "test_targeting_contract...",
    "test_render_contract...",
    "test_delivery_transaction...",
    "test_phase48_cli...",
)
```

**逐项 named invocation 与观察**（lines 83-99）：

```python
called = []
failures = []
for test_id in PHASE48_ACCEPTANCE_REGISTRY:
    called.append(test_id)
    suite = unittest.defaultTestLoader.loadTestsFromName(test_id)
    result = unittest.TestResult()
    suite.run(result)
    if result.failures or result.errors or result.skipped or result.unexpectedSuccesses:
        failures.append(test_id)
```

Phase 49 可把 Phase 48 registry 作为一个 nested gate，但顶层 test 必须对 raw outcome、reopened artifacts、hashes 和 runtime/UAT records 再观察，不能复制 `run_phase48_acceptance_registry()["status"]`。

**registry 合同断言**（lines 1063-1087）：测试内再次写出完整 required tuple，断言生产常量、observed required、called 精确相等，并禁止任何 skip 字段。这是避免实现与测试共用同一个错误常量的现有做法。

**mutation guard analog**（`verify_school_pptx.py` lines 1060-1100）：

```python
missing = deep_copy(candidate); del missing["gates"]["canonical-render"]
duplicate = deep_copy(candidate); duplicate["registry"]["called"][2] = duplicate["registry"]["called"][1]
reordered = deep_copy(candidate); reordered["registry"]["called"][1:3] = reversed(...)
skipped = deep_copy(candidate); skipped["registry"]["called"].pop()
hardcoded_pass = deep_copy(candidate)
hardcoded_pass["gates"]["canonical-render"]["status"] = "failed"
hardcoded_pass["status"] = "passed"
for mutation in mutations:
    assert validate_candidate(mutation) raises VerifyFailure
```

Phase 49 的 mutation 集至少覆盖 count/status/hash/artifact/runtime row/UAT hash 与 producer constant tampering。

---

### `skills/graduate-resume/scripts/runtime_install_fixture.py`（utility，batch + file-I/O）

**Contract analog:** `docs/compatibility-matrix.md` lines 15-35。代码库没有真实“六 runtime 逐行安装执行”的 runner，因此此文件属于 **No executable analog**，不能把文档 integrity test 冒充安装实测。

必须从矩阵逐项转成观察字段：

```text
frontmatter 可解析
whole folder 与 references/templates/fixtures/scripts 相对路径可读
public shell CLI 可显式执行
依赖可检查（不联网安装）
authorized verify workdir、delivery root 与 .work 可写
unknown/symlink 在 mutation 前 fail closed
```

六个 runtime ID 和顺序必须字面固定：Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw、Hermes Agent。runner 应消费目标 runtime 实际写出的 raw record/executable/version/environment evidence；不得只接受调用者传入 `--runtime` 标签后在同一 shell 伪造六行。自动 discovery 不是 PASS 条件，显式 `scripts/graduate-resume.sh` fallback 才是共同可验入口。

---

### `skills/graduate-resume/references/phase-49-verification-contract.md`（config，transform）

**Analog:** `skills/school-pptx/references/verification-contract.md`

复制其文档结构，而非 PPTX 具体内容：

1. Public Entry and Workdir Ownership（lines 5-20）：唯一 `verify --workdir`、caller-owned tree、artifact paths 相对 workdir、delivery/evidence/work 分离。
2. Fixed Top-level Registry（lines 22-35）：按顺序逐字列出 gates，并声明 required/called、唯一性、零 skip。
3. Fixed Negative Registry（lines 37-48）：逐 case 列 stable expected code、隔离 copied tree、protected hashes 不变、bounded output。
4. Nested Authority（lines 56-82）：Phase 48 registry 是 nested regression，不替代 Phase 49 顶层 authority，不复制旧 JSON。
5. Bounded Evidence（lines 91-106）：列 schema 字段、hash/relative paths、禁止绝对路径与 unbounded raw content。
6. Freshness/Exit Rules（lines 108-118）：新失败必须覆盖 stale PASS；自动 PASS 不等于人工 UAT PASS。

---

### `skills/graduate-resume/references/cross-environment-uat.md` 与 `templates/phase-49-uat.md`

**Analog:** `skills/school-pptx/references/visual-uat.md` 与 `verify_school_pptx.py` UAT lint。

**人工与自动化边界**（`visual-uat.md` lines 3-18, 43-47）：自动验证、截图和结构分析不能代替真实 viewer；初始 `PENDING` 不是通过；自动化只生成 artifacts/hashes 和全 PENDING 表单，不能填写 tester/time/observation/PASS。

**严格行顺序和 enum**（`verify_school_pptx.py` lines 1431-1451）：

```python
rows = parse_markdown_table(body)
if tuple(row["id"] for row in rows) != UAT_ITEM_ORDER:
    raise UATLintFailure("UAT_INVALID")
if any(row["result"] not in UAT_RESULT_VALUES or not row["check"] for row in rows):
    raise UATLintFailure("UAT_INVALID")
```

**pending 与人工完成互斥**（lines 1490-1537）：pending 时 identity/signoff 必须为空、所有行恰为 PENDING、观察字段为空；非 pending 时 viewer/OS/time/tester/逐项 observation 必须完整，PENDING/FAIL/BLOCKED 各自 fail closed。

**hash 绑定**（lines 1540-1595）：lint 重读 current evidence 和 artifact bytes，复算 hash，再与 UAT frontmatter 比对。Phase 49 应绑定 fixture、每个 PDF、对应每页 PNG、font manifest、Typst/runtime/environment identity；任一变化旧 UAT 即 stale。

模板保持纯 Markdown/YAML、人类可编辑；真实 tester/signoff 不应提交到 reusable template。

---

### Verification fixtures（test fixture，transform）

这些新路径应优先复制现有 fixture 的 canonical `graduate-resume/v2` 形状，而不是重造 schema：

| New Fixture | Copy From | Concrete Pattern |
|---|---|---|
| `verification/normal-photo.md` | `fixtures/layout/standard-photo.md:1` | frontmatter `photo: media/student-photo.jpg` + verified education/skills/projects；照片资源使用 fixture-relative path。 |
| `verification/no-photo.md` | `fixtures/valid-no-photo.md:1` | 省略 `photo` 字段，`preferences.photo_mode: no-photo`，所有事实 ID/status 字面稳定。 |
| `verification/multi-target.md` | `fixtures/valid-multi-target.md:22` | 每个 target 有 stable ID、role/source/as_of/confirmed；用于 generic + all confirmed targets。 |
| `verification/qualification-gap.md` | `fixtures/targeting/multi-state-targets.md:28` | 同时包含可满足、gap、unknown/not-applicable 所需的招聘条件，仍只保存用户提供事实。 |
| `verification/content-pressure.md` | `fixtures/layout/pressure-two-pages.md:14` | 长标题、多模块、多条目，以稳定 verified facts 触发确定性 2 页和模块原子边界。 |

publication faults 不应写回这些 canonical fixtures；复制到每次 run 的 owned negative tree 后再做 missing/unknown/symlink/tamper/fault mutation，模式见 `verify_school_pptx.py` lines 876-948。

---

### `skills/graduate-resume/SKILL.md`（canonical config，request-response）

**Analog:** 同文件 lines 92-118。

- Runtime Adapter Notes 继续只说明六 runtime 使用同一完整 folder 和显式 `scripts/graduate-resume.sh`，不得把私有 runtime 语法写入主流程。
- Outputs 继续声明验证 JSON/Markdown/PNG/logs 属于 caller-owned verify workdir，current 只容纳 Markdown/Typst/PDF triples（lines 96-104）。
- Verification checklist 同步 Phase 49 实际完成状态，不得在六 runtime 或 human UAT 尚未实测时勾选/声称 PASS。
- 复杂 gate/schema/UAT 细节链接到新 references，保持 canonical `SKILL.md` 简洁。

---

### `docs/compatibility-matrix.md` 与 `skills/README.md`（config，transform）

**Analog:** 两个文件的现有 graduate-resume 条目。

`docs/compatibility-matrix.md` 应沿用：

- lines 15-24 的 installation checks；
- lines 28-35 的 exactly-six runtime rows；
- lines 61-65 的 Graduate Resume whole-folder/fallback notes。

更新时把“Phase 46/后续再验收”的旧状态改成 Phase 49 的真实观察结果；未完成的 runtime 只能保持 installation-time/human-needed，不得用文档存在替代实测。

`skills/README.md` 只更新技能摘要与 progressive files 索引，指向新增 verification/UAT references 和 public fallback；不要复制固定 gate 全文。

## Shared Patterns

### Fixed Registry Integrity

**Source:** `skills/school-pptx/scripts/verify_school_pptx.py:37`、`:439`、`:952`

**Apply to:** `graduate_resume_verify.py`、`test_phase49_verify.py`、runtime rows、negative cases。

字面 tuple 定义 required 顺序；执行时逐项 append called；被阻断的 gate 仍生成 explicit blocked outcome；最终检查顺序、唯一性、零 dynamic skip 和 gate key exact set。

### Producer / Observer / Arbiter Separation

**Source:** `skills/graduate-resume/scripts/graduate_resume_pdf_gate.py:26`、`skills/school-pptx/scripts/verify_school_pptx.py:439`

**Apply to:** 所有 artifact/runtime/UAT gates。

producer 只生成 raw outputs；observer 重开 Markdown/Typst/PDF/PNG 和 raw records；arbiter 从 observer fields 重算 status。生产者的 `passed`、count、hash、runtime label 都不是 authority。

### Caller-Owned Evidence and Clean Delivery

**Source:** `skills/school-pptx/references/verification-contract.md:5`、`skills/graduate-resume/SKILL.md:96`

**Apply to:** CLI、aggregate、runtime runner、UAT preparation。

验证证据仅写显式 verify workdir；正式 delivery root 只接受 same-stem Markdown/Typst/PDF triples。artifact paths 在 evidence 中使用 workdir-relative paths，拒绝 source/current overlap、symlink/FIFO/unknown。

### Bounded Stable Errors

**Source:** `skills/graduate-resume/scripts/graduate_resume_cli.py:997`、`skills/school-pptx/scripts/verify_school_pptx.py:606`

**Apply to:** 所有 public CLI 和 subprocess gates。

异常映射到稳定 code + 简短 message；stdout/stderr 截断并记录 exit code/hash/overflow；不输出 traceback、绝对用户路径、原始简历事实或 secret material。

### Hash Freshness

**Source:** `skills/school-pptx/scripts/verify_school_pptx.py:598`、`:1540`

**Apply to:** PDF/PNG、字体、raw logs、runtime records、UAT。

hash 从当前 bytes 分块重算；JSON 内自报 hash 只能作为待核对字段。artifact/font/environment 任一变化都使旧 UAT 与旧 acceptance stale。

### No Authentication Pattern

本阶段是离线本地 CLI，没有认证、session 或远端授权模式。安全边界是 caller-owned path、no-follow、bounded input/output 与 exact runtime/UAT evidence；不要引入无关 auth abstraction。

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `skills/graduate-resume/scripts/runtime_install_fixture.py` | utility | batch + file-I/O + request-response | 仓库只有六 runtime 安装契约、文档 integrity gate 和显式 fallback 说明，没有能证明六个真实 runtime whole-folder 执行的 runner。planner 应按 `49-RESEARCH.md` 和 `docs/compatibility-matrix.md:15` 定义记录 schema，不得把单 shell 六次改标签当 analog。 |

## Planner Notes

- `48-REVIEW.md` 债务关闭和缺失 `48-SECURITY.md` 是外部发布前置 evidence，不应混入 graduate-resume 功能模块；Phase 49 的固定 G01 只重读并 fail closed。
- 当前机缺 Gemini CLI、OpenClaw、Hermes Agent；这不妨碍先实现本地 gates，但阻止 six-runtime PASS。registry 不得因此减少三行。
- 人工 UAT 尚无非开发环境 tester/signoff；合法自动结果可以是 `human_needed`，但仅限 UAT 为唯一 pending。
- 固定 fixture 已有非常接近的 canonical sources。planner 可选择复用现有路径或复制到 `fixtures/verification/`；一旦 registry 锁定，路径和 hash 身份必须字面固定。
- `README.md` / `docs/directory-spec.md` 只有在 planner 判断公开项目状态或目录约定确实变化时才追加；本 pattern map 不把它们列为 Phase 49 必改文件。

## Metadata

**Analog search scope:** `skills/graduate-resume/`、`skills/school-pptx/`、`docs/`、`.planning/phases/48-*`、`.planning/STATE.md`

**Primary analogs read:**

1. `skills/graduate-resume/scripts/test_phase48_cli.py`
2. `skills/graduate-resume/scripts/graduate_resume_pdf_gate.py`
3. `skills/graduate-resume/scripts/graduate_resume_cli.py`
4. `skills/school-pptx/scripts/verify_school_pptx.py` 与其 verification/UAT references
5. `docs/compatibility-matrix.md`

**Pattern extraction date:** 2026-07-19
