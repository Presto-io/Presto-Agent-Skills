---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
plan: 05
subsystem: graduate-resume-render-trust-boundary
tags: [python, typst, pymupdf, verified-facts, structured-content, photo-safety]

requires:
  - phase: 48-deterministic-targeted-rendering-clean-batch-delivery
    plan: 04
    provides: 离线 render/batch CLI、最终 Markdown 重读、三主题候选矩阵与 clean-delivery 事务
provides:
  - publication/final Markdown/Typst 三层 verified-only 与稳定事实 ID 防线
  - 受控结构化展示序列化、同源高度测量及真实 Typst/PDF 内容证明
  - plan/render/batch 共享的显式照片 fail-closed 与失败零投递变化
affects: [48-06-gap-closure, 49-runtime-acceptance, graduate-resume-rendering, graduate-resume-uat]

tech-stack:
  added: []
  patterns: [verified-publication-view, shared-stable-id-grammar, frozen-display-serialization, explicit-photo-fail-closed]

key-files:
  created: []
  modified:
    - skills/graduate-resume/scripts/graduate_resume_cli.py
    - skills/graduate-resume/scripts/graduate_resume_targeting.py
    - skills/graduate-resume/scripts/graduate_resume_final_markdown.py
    - skills/graduate-resume/scripts/graduate_resume_layout.py
    - skills/graduate-resume/scripts/graduate_resume_typst.py
    - skills/graduate-resume/scripts/test_render_contract.py
    - skills/graduate-resume/scripts/test_phase48_cli.py
    - skills/graduate-resume/templates/resume-themes.typ

key-decisions:
  - "canonical graduate-resume/v2 继续允许 declined 事实，但正式 publication 一旦包含任何非 verified 候选事实即固定失败；resolver 只消费隔离深拷贝。"
  - "事实 ID 使用单一 ASCII 稳定 grammar，profile 只允许固定 profile；canonical、resolver、final Markdown 与 Typst emitter 分层复验。"
  - "结构化字段按模块字面 allowlist、schema 顺序和中文标签冻结；高度测量与 Typst 只消费同一 ContainerPlan.fields 序列。"
  - "显式 photo 必须绑定 status=provided 的安全常规本地文件；只有 auto 可在没有 provided 资产时降级 no-photo。"

patterns-established:
  - "Publication trust boundary: validate canonical -> build isolated verified view -> resolve projection -> emit/reopen final Markdown -> validate/escape Typst。"
  - "Display data flow: allowlisted strings/mappings/lists -> contextualized frozen fields -> height/pagination -> line-for-line Typst/PDF emission。"

requirements-completed: [TARGET-01, TARGET-03, DELIVERY-01]

duration: 39min
completed: 2026-07-18
---

# Phase 48 Plan 05: 最终渲染可信事实与完整内容 Summary

**正式简历三件套现在只消费可证明为 verified 的稳定 ID 事实，并把联系方式、技能、项目成果和工具经同一冻结文本完整、安全地送入 Typst/PDF；显式照片缺资产会在投递前失败。**

## Performance

- **Duration:** 39 min
- **Started:** 2026-07-18T11:57:05Z
- **Completed:** 2026-07-18T12:36:22Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- canonical 仍可记录 declined，但 publication view、target resolver、最终 Markdown emit/load 和 Typst emitter 均拒绝非 verified、非法或重复事实 ID；恶意 ID 不会进入可执行 Typst 语境。
- profile contact、skills.items、projects.outcomes/tools 及其余登记字符串/列表字段按稳定 schema 顺序冻结，映射未知键、嵌套映射、非字符串列表项和控制字符全部 fail closed。
- `ContainerPlan.fields` 同时驱动高度、分页与 Typst 发射；真实 Typst 编译和 PyMuPDF 文本提取确认四类唯一标记同时存在于 `.typ` 与 `.pdf`。
- plan/render/batch 对 `--photo-mode photo` + no-photo/missing/symlink/伪 JPEG 均返回 `PHOTO_ASSET_INVALID`，并以递归 path/bytes snapshot 证明 current/history 不变。
- modern 照片主题网格按扣除 gutter 后的 `31fr/69fr` 分配，pressure fixture 的 block 开销和跨页字段上下文纳入冻结测量，三主题边界证据保持 1/2 页一致。

## Task Commits

1. **Task 1 RED：可信事实与 ID 负例** - `9473ecb` (test)
2. **Task 1 GREEN：verified-only publication 与共享 ID grammar** - `d8059d2` (feat)
3. **Task 2 RED：结构化内容 HOLLOW 与非法结构负例** - `fcfbec0` (test)
4. **Task 2 GREEN：受控展示序列化与真实 PDF 内容流** - `a9fdef3` (feat)
5. **Task 3 RED：显式照片缺资产端到端负例** - `61be2af` (test)
6. **Task 3 GREEN：显式照片 fail-closed** - `c007950` (feat)
7. **Task 2 回归修复：字段发射与测量逐行对齐** - `d21b748` (fix)
8. **Task 2 回归修复：冻结边界与 modern grid 校准** - `57421b0` (fix)

## Files Created/Modified

- `skills/graduate-resume/scripts/graduate_resume_cli.py` - 共享稳定事实 ID、canonical 校验和隔离 verified publication view。
- `skills/graduate-resume/scripts/graduate_resume_targeting.py` - resolver 再次要求 verified 候选与合法稳定事实 ID。
- `skills/graduate-resume/scripts/graduate_resume_final_markdown.py` - emit/load 两侧拒绝非 verified、非法和重复事实。
- `skills/graduate-resume/scripts/graduate_resume_layout.py` - 字段 allowlist、受控序列化、同源高度、上下文追溯与照片模式分支。
- `skills/graduate-resume/scripts/graduate_resume_typst.py` - Typst 标记字符转义、容器 ID 复验和逐冻结字段机械发射。
- `skills/graduate-resume/scripts/test_render_contract.py` - final/Typst 双重防线、非法结构、真实 Typst/PDF 四标记和重排同源回归。
- `skills/graduate-resume/scripts/test_phase48_cli.py` - publication 非 verified/恶意 ID、显式照片、资产安全与 delivery snapshot 回归。
- `skills/graduate-resume/templates/resume-themes.typ` - modern 照片网格使用扣除 gutter 后的比例轨道。

## Decisions Made

- publication 对任何非 verified 候选事实 fail closed，而不是静默生成删减后仍可能不完整的正式简历；这保留 canonical 编辑语义，同时满足公开 render/batch 的可信边界。
- 每个非 profile 展示字段携带条目首字段上下文，使重复短值跨页时仍能归属到稳定条目，并保持 PDF gate 的强跑页检测。
- `_height` 对每个容器计入 Typst block/heading 固定开销；字段值逐行发射，使测量模型、发射模型与实际 PDF 分页一致。
- 不公开 Python repr、恶意 payload、绝对资产路径或 traceback；所有失败继续走既有 bounded JSON `CliError` 边界。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] targeting resolver 复用共享稳定 ID grammar**
- **Found during:** Task 1（共享事实 ID 信任边界）
- **Issue:** Task 文件列表未声明 `graduate_resume_targeting.py`，但 resolver 的 `_facts_by_section` 仍接受任意非空 ID，会绕过 canonical/final 的统一契约。
- **Fix:** resolver 同时要求 candidate/entry 为 verified，并调用 canonical 同一 `is_stable_fact_id`。
- **Files modified:** `skills/graduate-resume/scripts/graduate_resume_targeting.py`
- **Verification:** declined/非法/duplicate/override 端到端负例与全量 targeting 测试通过。
- **Committed in:** `d8059d2`

**2. [Rule 1 - Bug] 结构化字段单段发射导致照片窄栏越界**
- **Found during:** 计划级全量验证
- **Issue:** 多个冻结字段以 ` · ` 拼成一个段落，modern 照片窄栏出现右边界外可见像素，测量与发射行模型不一致。
- **Fix:** 按冻结字段逐行发射；`typst_content` 继续逐字符转义，每个字段与 `_height` 的最小一行模型一致。
- **Files modified:** `skills/graduate-resume/scripts/graduate_resume_typst.py`
- **Verification:** render contract 9/9、standard-photo 三主题 PNG/PDF 边界通过。
- **Committed in:** `d21b748`

**3. [Rule 1 - Bug] block 开销与 modern percentage grid 破坏冻结页数/安全区**
- **Found during:** 计划级全量验证
- **Issue:** pressure fixture 的旧 6mm 容器开销低估 Typst heading/block 间距；modern 的 31%+69% 再加 6mm gutter 超过可用宽度。
- **Fix:** 将冻结容器固定开销校准为 19mm、给非 profile 字段加入条目上下文，并把 modern 网格改为 `31fr/69fr`。
- **Files modified:** `skills/graduate-resume/scripts/graduate_resume_layout.py`, `skills/graduate-resume/templates/resume-themes.typ`
- **Verification:** layout fixture 6/6、render contract 9/9、全量 62/62 通过。
- **Committed in:** `57421b0`

---

**Total deviations:** 3 auto-fixed（2 bugs，1 missing critical trust-boundary link）
**Impact on plan:** 三项均是实现既定安全、完整内容和冻结分页契约所必需；未新增产品功能或外部依赖。

## Issues Encountered

- 真实 PDF 首轮暴露邮箱 `@` 被 Typst 解释为标签引用；统一转义扩展到 `#[]<>@$*_` 等 Typst 标记字符后编译通过，包含在 `a9fdef3`。
- 一次组合 `unittest` 文件路径被解析为 `_FailedTest.py`；改用 `unittest discover` 精确 pattern 后相关 6 项 layout fixture 全部通过，这不是代码失败。

## Known Stubs

None. 扫描命中的空列表、空映射、空字符串和 `None` 均是受控解析/累积状态或测试环境，不流向正式 UI/交付内容，也不伪造通过结果。

## Threat Review

- 本计划未新增网络 endpoint、认证路径、凭据、远程媒体、数据库/schema 或新的投递写入机制。
- `T-48-G05-01/02` 由共享 ID grammar、verified publication view、final Markdown 重读和 Typst 二次转义闭环。
- `T-48-G05-03` 由字面字段 allowlist、受控 mapping/list 序列化和控制字符拒绝闭环。
- `T-48-G05-04/05` 由显式照片先分支、provided 安全常规文件/no-follow/root containment 检查和失败 snapshot 闭环。
- 未发现计划威胁模型之外的新 trust boundary。

## Verification

- `python3 -m unittest skills/graduate-resume/scripts/test_render_contract.py skills/graduate-resume/scripts/test_phase48_cli.py -v`：20/20 PASS，真实 Typst/PDF 与 PyMuPDF 断言包含在内。
- `python3 -m unittest discover -s skills/graduate-resume/scripts -p 'test_*.py' -v`：62/62 PASS，约 29 秒。
- `python3 -m unittest discover -s skills/graduate-resume/scripts -p 'test_layout_fixtures.py' -v`：6/6 PASS，三主题真实 PDF/PNG 边界通过。
- `python3 -m py_compile` 覆盖本计划五个实现模块：PASS。
- `git diff --check`：PASS。

## TDD Gate Compliance

- Task 1：RED `9473ecb` 先证明 declined/恶意 ID/declined override 穿透，GREEN `d8059d2` 后通过。
- Task 2：RED `fcfbec0` 先证明四类结构化内容 HOLLOW 且非法结构未拒绝，GREEN `a9fdef3` 后真实 Typst/PDF 通过；回归修复 `d21b748`、`57421b0` 保持 GREEN。
- Task 3：RED `61be2af` 先证明显式 photo 被 no-photo canonical 静默吞掉，GREEN `c007950` 后 plan/render/batch 通过。

## User Setup Required

None - no external service configuration required. 本地验证继续复用仓库已有 Typst 0.15.0、PyMuPDF、Pillow 与 skill-local fonts。

## Next Phase Readiness

- TARGET-01、TARGET-03、DELIVERY-01 的验证报告反例已转为自动回归，48-06 可继续处理其声明的剩余 gap closure。
- Phase 49 可在可信、内容完整且照片失败关闭的三件套基础上做六 runtime、字体与视觉 UAT。
- 无实现 blocker；`.planning/STATE.md` 的并行未提交变化在 SUMMARY 提交后由顺序 SDK 更新流程合并处理。

## Self-Check: PASSED

- 八个 key-files.modified 均存在；本计划未声明 created implementation file。
- `9473ecb`、`d8059d2`、`fcfbec0`、`a9fdef3`、`61be2af`、`c007950`、`d21b748`、`57421b0` 均存在于 git history。
- 专项 20/20、layout fixture 6/6、全量 62/62、py_compile 和 diff check 全部通过。

---
*Phase: 48-deterministic-targeted-rendering-clean-batch-delivery*
*Completed: 2026-07-18*
