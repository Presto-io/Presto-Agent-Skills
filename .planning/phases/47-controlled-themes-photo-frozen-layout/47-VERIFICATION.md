---
phase: 47-controlled-themes-photo-frozen-layout
verified: 2026-07-18T03:28:38Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 2/5
  gaps_closed:
    - "三个主题未进入实际 Typst 布局"
    - "不可满足的强制两页经 shell CLI 输出 traceback"
    - "临界与压力样张未经过真实 PDF/PNG 门禁"
  gaps_remaining: []
  regressions: []
---

# Phase 47: 受控主题、照片与冻结布局验证报告

**Phase Goal:** 用户能用同一已核实资料选择主题和照片模式，获得不虚构、不截断、逻辑完整的 1 页或 2 页 A4 布局。
**Verified:** 2026-07-18T03:28:38Z
**Status:** passed
**Re-verification:** 是，缺口关闭后复核

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | 用户可用 YAML 主题参数切换保守稳妥、现代简洁和个性设计，且无需改写资料 schema。 | ✓ VERIFIED | `ThemeSpec` 保持纯视觉注册表；`emit_typst()` 逐页调用 `resume.theme-layout(plan.theme_key, ...)`。对同一无照片资料，conservative、modern、expressive 的 Typst SHA-256 分别为 `394269...409a34`、`8c015c...4992f0`、`dccd55...713376`。 |
| 2 | 照片版只使用用户明确提供的本地照片；无照片版移除照片区域而不保留空位。 | ✓ VERIFIED | `resolve_layout_photo()` 仍拒绝路径逃逸、symlink、非普通文件和非图片；无照片计划的 `photo`、`photo_slot` 均为 `None`。无照片发射不含 `image(`，且三主题无照片 PDF/PNG 门禁通过。 |
| 3 | CLI 可自动或按用户强制选择 1 页或 2 页 A4，结果不低于可读性阈值、不截断且不产生第三页。 | ✓ VERIFIED | `build_frozen_resume_plan()` 保持测量阈值和精确 1/2 页选择；每主题的短、临界、压力样张均经实际 Typst/PDF/PNG 验证。不可满足强制两页返回非零和稳定 JSON `LAYOUT_UNSATISFIABLE`。 |
| 4 | 两页输出没有孤立标题、无标题续接或拆开的项目、实训、经历、职责及成果；不能满足时失败关闭并说明原因。 | ✓ VERIFIED | `list-entry` 仍不可拆；发射器在每个新 section 生成标题。三主题压力两页样张全部经过 PDF 文字页归属、第二页锚点、A4 页数和 PNG 安全区门禁；不可满足样张稳定失败。 |
| 5 | 内容不足时仅重排或扩展既有材料可支撑的表达，不会虚构事实。 | ✓ VERIFIED | 容器字段与 `source_fact_ids` 只来自 `validate_document()` 后的原始资料，`FrozenResumePlan.validate()` 逐项核验；未发现生成、补造或改写候选人事实的代码路径。 |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `graduate_resume_layout.py` | 主题、照片、冻结分页与失败关闭 | ✓ VERIFIED | 主题/照片策略、源事实容器、条目原子分页和受控字体数据流均由真实 CLI 与测试覆盖。 |
| `resume-themes.typ` | 三个实际 A4 视觉主题及宏 | ✓ VERIFIED | `theme-layout()` 现由生产发射器调用；三主题有不同的有照/无照布局分支，`list-entry` 保持 `breakable: false`。 |
| `graduate_resume_typst.py` | 仅消费冻结计划的发射器 | ✓ VERIFIED | 只消费已验证计划和事实；逐页传入冻结主题与仅首页可用的照片，不重算分页或解析路径。 |
| `test_layout_fixtures.py` | 固定样张及 PDF/PNG 实物门禁 | ✓ VERIFIED | 固定列表覆盖短无照、标准有照、临界、压力及失败样张；临界/压力现对三主题调用 `compile_controlled()`。 |
| `fonts/manifest.json` | skill-local 字体身份、哈希与许可 | ✓ VERIFIED | 400/600 语义字体记录的 SHA-256 与磁盘一致，`typst fonts --ignore-system-fonts` 可见。 |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| CLI `plan` | 冻结布局 | `build_frozen_resume_plan()` | ✓ WIRED | 正常路径构建冻结计划；带 `code/message` 的布局异常在公共 CLI 边界规范化为 JSON。 |
| 冻结主题 | Typst 主题布局 | `ThemeSpec.key` -> `theme-layout()` | ✓ WIRED | `graduate_resume_typst.py:59` 每页调用主题布局；主题差异性测试和实际编译均通过。 |
| 固定矩阵 | Typst/PDF/PNG 门禁 | `compile_controlled()` -> `verify_rendered_layout()` | ✓ WIRED | 有照、无照、临界和压力样张均使用受控字体编译、检查真实 A4/PDF/PNG。 |
| PDF 门禁 | FrozenResumePlan | 页数、文字、锚点和 PNG 安全区 | ✓ WIRED | `graduate_resume_pdf_gate.py` 对实际 PDF 文本和逐页 PNG 与冻结计划交叉核验。 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `graduate_resume_layout.py` | containers / source_fact_ids | 已验证 Markdown facts | 只投影实际字段和 ID | ✓ FLOWING |
| `graduate_resume_typst.py` | 页面正文与主题 | `FrozenResumePlan.pages` / `theme_key` | 真实冻结计划逐页驱动发射 | ✓ FLOWING |
| `test_layout_fixtures.py` | PDF/PNG evidence | 字面固定 fixtures | 每个规定成功样张均有临时实物产物并由门禁读取 | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| 主题、布局和样张回归 | `python3 -m unittest ... -v` | 19/19 通过，23.948s | ✓ PASS |
| skill-local 聚合验证 | `skills/graduate-resume/scripts/graduate-resume.sh verify` | schema 与 5 个固定 layout fixture 全部通过 | ✓ PASS |
| 不可满足强制双页 | `graduate-resume.sh plan ...error-unsatisfiable-two-pages.md --pages 2` | 非零退出，stderr JSON 为 `LAYOUT_UNSATISFIABLE`，无 traceback | ✓ PASS |
| 无照主题实际差异 | 直接调用 `emit_typst()` 比较 SHA-256 | 三主题均调用 `theme-layout` 且三个 hash 不同 | ✓ PASS |
| 字体门禁 | `typst fonts --font-path ... --ignore-system-fonts --variants` | 两个受控 Noto 静态字体可见，manifest 哈希匹配 | ✓ PASS |

### Probe Execution

Step 7c: SKIPPED。阶段计划、总结与仓库均未声明或提供 `probe-*.sh`。

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| THEME-01 | 47-01, 47-03 | 三主题 YAML 选择 | ✓ SATISFIED | 三个 key/别名进入实际不同主题布局，且主题对象不含事实字段。 |
| THEME-02 | 47-01, 47-03 | 本地照片与无照片布局 | ✓ SATISFIED | 受限本地解析、无照片移除及有照/无照实物门禁均通过。 |
| THEME-03 | 47-02, 47-03 | 自动/强制 1/2 页 A4 | ✓ SATISFIED | 冻结计划、实际 A4 PDF/PNG 矩阵及稳定失败契约均通过。 |
| THEME-04 | 47-02, 47-03 | 原子条目和双页逻辑 | ✓ SATISFIED | 不可拆条目、标题页首和压力双页的真实 PDF/PNG 门禁通过。 |
| THEME-05 | 47-02, 47-03 | 不虚构事实 | ✓ SATISFIED | 计划及发射只使用已验证来源字段/ID。 |

所有属于 Phase 47 的需求均被计划声明；未发现孤儿需求。

### Anti-Patterns Found

未发现本阶段生产文件中的未关联 `TBD`、`FIXME` 或 `XXX` 债务标记、空实现或硬编码空数据。`render`/`batch` 的 `NOT_IMPLEMENTED` 是路线图明确留给 Phase 48 的正式交付边界，不影响本阶段目标。

### Gaps Summary

初次验证的三项阻断缺口均已关闭，且未发现回归。Phase 48 的正式三件套发布与 Phase 49 的跨 runtime、跨环境人工验收仍按路线图边界保留，未被误计为本阶段交付。

---

_Verified: 2026-07-18T03:28:38Z_
_Verifier: the agent (gsd-verifier)_
