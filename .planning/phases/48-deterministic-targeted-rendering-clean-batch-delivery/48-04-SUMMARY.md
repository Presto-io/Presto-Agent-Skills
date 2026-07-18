---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
plan: 04
subsystem: graduate-resume-public-workflow
tags: [python, cli, deterministic-rendering, clean-delivery, acceptance-registry, documentation]

requires:
  - phase: 48-deterministic-targeted-rendering-clean-batch-delivery
    plan: 01
    provides: 不可变目标投影、四态条件、逐目标 gap allow 与隐藏 evidence digest
  - phase: 48-deterministic-targeted-rendering-clean-batch-delivery
    plan: 02
    provides: final Markdown 重读检查点、三主题候选矩阵与自包含照片 Typst
  - phase: 48-deterministic-targeted-rendering-clean-batch-delivery
    plan: 03
    provides: patch/authority 动态 triple 事务、delta、history、no-op 与 rollback
provides:
  - 离线公开 render/batch CLI、精确 not-applicable 三参数契约与 bounded JSON 边界
  - generic/target 三主题 patch 与 generic+all confirmed targets authority 批量交付
  - D-01..D-19 canonical reference、runtime-neutral SKILL 流程和可验证 author template
  - 固定顺序、真实观察且无动态 skip 的 Phase 48 acceptance registry
affects: [49-runtime-acceptance, graduate-resume-verify, graduate-resume-uat]

tech-stack:
  added: []
  patterns: [preflight-confirm-publish, bounded-public-json, literal-observed-acceptance-registry, canonical-progressive-reference]

key-files:
  created:
    - skills/graduate-resume/scripts/test_phase48_cli.py
    - skills/graduate-resume/references/targeted-render-delivery-contract.md
  modified:
    - skills/graduate-resume/scripts/graduate_resume_cli.py
    - skills/graduate-resume/SKILL.md
    - skills/graduate-resume/templates/graduate-resume.md

key-decisions:
  - "render 只选择 generic 或一个稳定 target ID，并固定使用 patch；batch 默认 generic + all confirmed targets，并固定使用 authority。"
  - "--not-applicable 只有可重复三参数入口；reason trim 后限制 1..200 Unicode code points，重复 pair、未知或未选择 target/condition 均失败。"
  - "公开预检只显示逐条件四态、有界 digest、正式 stems 与 delta；完整 reason/evidence、preview 和照片中间件只留 owned 临时 evidence。"
  - "Phase 48 aggregate 使用字面固定 13 gate registry 观察四个窄测试模块，不动态发现、跳过或宣称 Phase 49 authority。"

patterns-established:
  - "CLI coordinator: load → validate → projection/four-state → complete candidate matrix → delivery preflight → explicit confirmation → publish。"
  - "Current-stem audit: 只识别同候选人安全前缀和登记主题后缀的完整/partial stem，让 authority 能列出旧目标 removals，同时 unknown 仍 fail closed。"

requirements-completed: [TARGET-01, TARGET-02, TARGET-03, DELIVERY-01, DELIVERY-02, DELIVERY-03]

duration: 23min
completed: 2026-07-18
---

# Phase 48 Plan 04: 确定性定向渲染与干净批量交付 Summary

**公开 CLI 已把稳定目标投影、三主题自包含候选和 patch/authority 事务串成完整离线工作流，并以唯一条件覆盖语法、确认绑定 delta 和固定验收矩阵锁定交付行为。**

## Performance

- **Duration:** 23 min
- **Started:** 2026-07-18T06:58:47Z
- **Completed:** 2026-07-18T07:21:53Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- `render` 支持 generic/单 target 二选一、retain/exclude/pin、逐目标 gap allow、精确三参数 not-applicable、页数/照片/资源/投递根和先预检后确认的三主题 patch 发布。
- `batch` 默认展开 generic 与全部 confirmed targets，在任何 mutation 前显示权威版本矩阵和 added/updated/unchanged/removed；确认后以 authority 一次性发布或安全移除旧 triple。
- 公开成功/失败 JSON 不输出完整理由、联系方式、绝对路径、候选正文或 traceback；相同输入保持 history、inode、mtime 不变。
- canonical `SKILL.md`、D-01..D-19 progressive reference 和通过 `graduate-resume/v2` validate 的 author template 已同步，未引入 runtime 私有语法或公开 sidecar。
- 固定 13 gate acceptance registry 覆盖四态、gap、override、safe stem、三主题、有照/无照、目标减少、patch、no-op、unknown/symlink/stale、rollback、partial publication 与照片 triple 移动重编译。

## Task Commits

1. **Task 1 RED：公开 CLI 失败契约** - `bfbc3de` (test)
2. **Task 1 GREEN：接通 render/batch 预检与发布** - `4d37555` (feat)
3. **Task 2：同步 canonical 工作流、模板与详细契约** - `84ea04a` (docs)
4. **Task 3 RED：固定验收 registry 失败 gate** - `de92984` (test)
5. **Task 3 GREEN：观察式 Phase 48 验收矩阵** - `d7c928a` (test)

## Files Created/Modified

- `skills/graduate-resume/scripts/graduate_resume_cli.py` - 公开参数、目标/条件请求冻结、照片与布局协调、完整候选暂存、事务预检/确认和 bounded JSON。
- `skills/graduate-resume/scripts/test_phase48_cli.py` - CLI/文件系统端到端回归、文档契约断言和字面固定 acceptance registry。
- `skills/graduate-resume/references/targeted-render-delivery-contract.md` - D-01..D-19、照片自包含、命名、history/no-op/rollback 与 Phase 49 边界。
- `skills/graduate-resume/SKILL.md` - runtime-neutral validate/render/batch 工作流、复制命令、错误恢复、输出和安全边界。
- `skills/graduate-resume/templates/graduate-resume.md` - 可直接填写稳定 target ID、source/as_of/confirmed 和四个受控谓词所需结构化招聘条件的通过版模板。

## Decisions Made

- 单份 patch 的 managed registry 同时包含 canonical 可推导 stems 与同候选人当前安全 stems，以保留其他版本；authority 使用同一 registry 把已从 canonical 删除的旧 target 明确分类为 removed。
- confirmation 不接受独立 token 文件；CLI 把本次 preflight 的 approval digest 原样交给同一 held-root session，publish 会重新预检并拒绝 snapshot 漂移。
- batch 中 generic projection 不继承 target gap allow；allow 只传给对应 target projection，避免通用版误触目标条件边界。
- Phase 49 的六 runtime 安装、聚合 fault-injection authority、PDF 结构/布局 gate 和非开发环境字体 UAT 只记录边界，不在本计划宣称完成。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] 修正 batch gap allow 误传给 generic projection**
- **Found during:** Task 1（gap allow 端到端回归）
- **Issue:** batch 同时包含 generic 与 targets，初版把 target allow tuple 传给 generic resolver，触发“通用版不得携带缺口放行”。
- **Fix:** generic projection 固定接收空 allow；每个 target projection 才接收本次逐目标 allow 集合。
- **Files modified:** `skills/graduate-resume/scripts/graduate_resume_cli.py`
- **Verification:** target-device 单目标 allow 成功、target-robot 不继承、generic 正常生成，专项 7 项通过。
- **Committed in:** `4d37555`

**2. [Rule 2 - Missing Critical] 统一未知内部异常为 bounded public failure**
- **Found during:** Task 1（失败不泄露验收）
- **Issue:** 既有 `main()` 仅规范化带 `code/message` 的异常，意外 I/O 或编程异常可能越过公开边界输出 traceback 和路径。
- **Fix:** 未知异常统一返回 `INTERNAL_ERROR` 与通用消息，不包含 traceback、绝对路径或候选事实。
- **Files modified:** `skills/graduate-resume/scripts/graduate_resume_cli.py`
- **Verification:** 移除 Typst PATH 的真实失败返回 bounded `FONT_MANIFEST_INVALID`；全部 CLI 失败回归检查无 traceback 且 current/history 不变。
- **Committed in:** `4d37555`

---

**Total deviations:** 2 auto-fixed（1 bug，1 missing critical public boundary）
**Impact on plan:** 两项均用于满足逐目标隔离和失败不泄露/不发布的既定正确性要求，无范围扩张。

## Issues Encountered

- 最初 patch 保留测试混用了不同候选人的 delivery root，正确触发 unknown-root fail closed；测试改为同一 canonical 候选人的 generic 与 target，验证真实 patch 语义。
- 目标减少会使 canonical hash 改变，因此 surviving generic/target 也分类为 updated；验收改为精确检查三个 removed 储能目标主题均完整归档，而不是假定 history 只有 removals。
- 仓库旧照片 fixture 的声明路径与实际媒体目录不同；照片可移动验收在临时 canonical 副本中改为真实受控媒体路径，未修改既有 fixture。

## Known Stubs

None. 扫描命中的空容器和 `None` 仅用于参数默认、解析状态与结果构建，不流向正式交付或伪造验收结果。

## Threat Review

- 新增文件写入面完全复用 48-03 held-directory/no-follow/explicit registry 事务；CLI 不新增网络、认证、凭据或远程媒体入口。
- 公开 condition matrix 只含 condition ID、predicate、state、计数与 digest；完整 reason/evidence 不进入 stdout 或 delivery root。
- 当前 stem discovery 只接受同候选人安全前缀、登记正式主题后缀和三种 managed suffix；unknown/partial/symlink/stale 状态仍由 DeliverySession 在 mutation 前拒绝。
- 未发现计划威胁模型之外的新 trust boundary。

## Verification

- `python3 -m unittest skills/graduate-resume/scripts/test_targeting_contract.py skills/graduate-resume/scripts/test_render_contract.py skills/graduate-resume/scripts/test_delivery_transaction.py skills/graduate-resume/scripts/test_phase48_cli.py -v`：37/37 PASS，约 7 秒。
- `python3 -m unittest discover -s skills/graduate-resume/scripts -p 'test_*.py' -v`：56/56 PASS，约 29 秒。
- `python3 skills/graduate-resume/scripts/graduate_resume_cli.py validate --input skills/graduate-resume/templates/graduate-resume.md`：PASS。
- `python3 -m py_compile skills/graduate-resume/scripts/graduate_resume_cli.py skills/graduate-resume/scripts/test_phase48_cli.py`：PASS。
- `git diff --check`：PASS；Phase 47 两个 modified 规划文件与一个 untracked verification 文件保持未暂存、未提交。

## TDD Gate Compliance

- Task 1 RED `bfbc3de` 先稳定失败，GREEN `4d37555` 后专项与相邻测试通过。
- Task 3 RED `de92984` 先因 registry 未定义稳定失败，GREEN `d7c928a` 后字面 required/called 精确相等且无 skip。
- 两个 TDD 任务均具备 test → implementation/fix 的提交顺序。

## User Setup Required

None - no external service configuration required. 本地正式渲染仍要求仓库锁定的 Typst 0.15.0 与 skill-local fonts。

## Next Phase Readiness

- TARGET-01..03 与 DELIVERY-01..03 已通过公开 CLI 和固定 acceptance registry 完整闭环，Phase 48 四个计划均具备 SUMMARY evidence。
- Phase 49 可在此基础上执行六 runtime 安装/发现验收、聚合故障注入 authority、PDF 结构/布局 gate 和非开发环境字体人工 UAT。
- 无实现 blocker；Phase 47 既有未提交规划/验证改动仍由其原所有者处理。

## Self-Check: PASSED

- 五个 plan-owned implementation/documentation files 均存在。
- `bfbc3de`、`4d37555`、`84ea04a`、`de92984`、`d7c928a` 均可在 git history 中找到。
- 37 项计划矩阵、56 项 graduate-resume 全量回归、模板 validate、py_compile 与 diff check 均通过。

---
*Phase: 48-deterministic-targeted-rendering-clean-batch-delivery*
*Completed: 2026-07-18*
