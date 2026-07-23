---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
plan: 01
subsystem: graduate-resume-targeting
tags: [python, deterministic-projection, hard-conditions, sha256, tdd]

requires:
  - phase: 46-graduate-resume-verified-source
    provides: graduate-resume/v2 已核实事实、稳定 ID 与 target brief
  - phase: 47-controlled-themes-photo-frozen-layout
    provides: 三主题冻结布局与一/两页反馈边界
provides:
  - 原始策略字节 SHA-256 绑定的不可变版本事实投影
  - 三主题共享事实集的确定性页数预算裁剪
  - 四态硬条件矩阵、逐目标 gap 放行与隐藏证据摘要
affects: [48-02-final-markdown-rendering, 48-03-bundle-delivery, graduate-resume-cli]

tech-stack:
  added: []
  patterns: [frozen-dataclass-projection, controlled-predicate-evaluation, public-summary-hidden-evidence]

key-files:
  created:
    - skills/graduate-resume/templates/targeting-policy.json
    - skills/graduate-resume/scripts/graduate_resume_targeting.py
    - skills/graduate-resume/scripts/test_targeting_contract.py
    - skills/graduate-resume/fixtures/targeting/multi-state-targets.md
  modified: []

key-decisions:
  - "事实排序固定为受控模块顺序、pin 优先、整数相关性降序、稳定事实 ID；正文出现顺序不参与决策。"
  - "三主题始终消费同一 selected_fact_ids；任一主题不满足预算时，每轮只移除一个最低优先级可省略事实。"
  - "只有 education_level、major_exact、certificate_exact、fresh_graduate_status 可产生 meets/gap；其他条件统一为 unknown。"
  - "完整条件理由和证据 ID 只进入隐藏矩阵，公开投影仅保留四态计数、warning 数、digest 与 gap_allowed。"

patterns-established:
  - "Policy-bound projection: 配置精确字段集与原始 bytes SHA-256 一起冻结进 VersionProjection。"
  - "Per-target qualification gate: gap 放行只检查当前 target ID，其他目标的 allow 不继承。"

requirements-completed: [TARGET-01, TARGET-02, TARGET-03]

duration: 11min
completed: 2026-07-18
---

# Phase 48 Plan 01: 确定性目标解析与四态条件 Summary

**以稳定事实 ID、离线策略哈希和受控谓词构建不可变目标投影，并用三主题共享预算与逐目标 gap 放行阻止资格暗示和内容漂移。**

## Performance

- **Duration:** 11 min
- **Started:** 2026-07-18T06:02:35Z
- **Completed:** 2026-07-18T06:13:51Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- 新增精确字段校验的 `graduate-resume-targeting/v1` 离线策略，并把原始字节 SHA-256 冻结进每个版本投影。
- 新增冻结 `VersionProjection`、`FactDecision`、`OverrideSnapshot`、`PageBudgetRequest`、`LayoutFeedback`，保证 core/retain/pin 不会被页数预算移除。
- 新增受控四态 evaluator、一次性 not-applicable 覆盖、逐目标 gap allow、隐藏 evidence matrix 与有界公开摘要。
- 新增真实 Markdown 多目标 fixture 与 12 项窄回归；相邻 graduate-resume 合同测试共 25 项通过。

## Task Commits

每个 TDD gate 均独立提交：

1. **Task 1 RED：定向投影失败契约** - `4f37873` (test)
2. **Task 1 GREEN：冻结确定性事实投影** - `54442e5` (feat)
3. **Task 2 RED：四态条件失败契约** - `e933041` (test)
4. **Task 2 GREEN：严格四态与逐目标放行** - `a5647cf` (feat)

## Files Created/Modified

- `skills/graduate-resume/templates/targeting-policy.json` - 版本化模块顺序、整数权重、exact-term expansions 与四谓词 registry。
- `skills/graduate-resume/scripts/graduate_resume_targeting.py` - 不可变投影、共享预算 resolver、四态条件 evaluator 与摘要绑定。
- `skills/graduate-resume/scripts/test_targeting_contract.py` - 确定性、覆盖冲突、页数预算、四态、gap gate 与隐私回归。
- `skills/graduate-resume/fixtures/targeting/multi-state-targets.md` - 两个目标、四谓词、gap 与 unsupported 条件的字面 fixture。

## Decisions Made

- `pin` 隐含预算保护但不越过核心模块；核心事实始终先于所有可选事实。
- 强制一页/两页要求反馈页数精确匹配，`auto` 只接受一页或两页；第三页反馈无论 `fits` 标志如何都触发继续裁剪或稳定失败。
- 受控谓词只读取已核实结构化字段；关键词相关性评分永不复用为资格证明。
- not-applicable 理由 trim 后限制为 1..200 Unicode code points，并拒绝所有 Unicode 控制字符。

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- 首轮跨目标 allow 校验过严，会把“allow A、评估 B”当作参数错误；在 GREEN 阶段收紧为只校验 ID 唯一且非空，并由当前 target 是否在集合中决定放行，符合不继承契约。

## Known Stubs

None. Dataclass 构造阶段的空 digest 默认值和函数内部空列表仅用于不可变对象最终化，不流向公开 UI 或正式交付。

## Threat Review

- T-48-01：只有四个受控谓词与明确 evidence 才能产生 meets/gap，相似词与不支持条件回退 unknown。
- T-48-02：策略精确字段集、原始 bytes hash、冻结 dataclass、核心事实保护与冲突覆盖 fail closed。
- T-48-03：公开摘要不含候选人正文、联系方式、绝对路径、完整理由或 evidence IDs。
- T-48-04：gap allow 绑定本次 target ID，不提供全局或持久化开关。
- 未发现计划威胁模型之外的新网络、认证、文件写入或 schema trust boundary。

## Verification

- `python3 -m unittest skills/graduate-resume/scripts/test_targeting_contract.py -v`：12/12 PASS。
- `python3 -m unittest discover -s skills/graduate-resume/scripts -p 'test_*contract.py' -v`：25/25 PASS。
- 重复解析同一 facts/target 得到完全相同 projection 与三个 SHA-256 digest。
- 策略和 resolver 扫描未发现网络 URL、当前时间、随机数、机器绝对路径或具体目标实例。

## TDD Gate Compliance

- RED：`4f37873`、`e933041` 均先于对应实现提交且测试稳定失败。
- GREEN：`54442e5`、`a5647cf` 均使对应测试与相邻合同测试通过。
- 无需额外 REFACTOR 提交。

## User Setup Required

None - no external service configuration or package installation required.

## Next Phase Readiness

- 48-02 可直接消费 `VersionProjection.selected_fact_ids`、逐事实 trace、policy/hash、condition counts/digest 与 gap allow snapshot。
- 真实 Phase 47 布局 adapter 尚由 48-02 接入；本计划已用纯 callback 锁定三主题共享裁剪算法和失败语义。

## Self-Check: PASSED

- 四个 key files 均存在。
- 四个 TDD commits 均可在 git history 中找到。
- 所有任务 acceptance criteria 与计划级 verification 已重新执行并通过。

---
*Phase: 48-deterministic-targeted-rendering-clean-batch-delivery*
*Completed: 2026-07-18*
