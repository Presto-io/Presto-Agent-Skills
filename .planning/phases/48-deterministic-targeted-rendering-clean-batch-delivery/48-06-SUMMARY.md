---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
plan: 06
subsystem: graduate-resume-auditable-publication
tags: [python, condition-evidence, no-follow, history, approval-digest, toctou]

requires:
  - phase: 48-deterministic-targeted-rendering-clean-batch-delivery
    plan: 05
    provides: verified-only 完整三件套、结构化内容与显式照片 fail-closed
provides:
  - render/batch 共享的有界逐条件四态公开投影与独立持久隐藏证据
  - owner-prefix 绑定且不依赖当前 authority membership 的完整历史 triple 校验
  - 跨进程 reviewed approval digest 与 candidate/current/canonical/root identity TOCTOU 防线
affects: [49-runtime-acceptance, graduate-resume-delivery, graduate-resume-audit, graduate-resume-uat]

tech-stack:
  added: []
  patterns: [held-no-follow-evidence-sink, owner-bound-history-grammar, canonical-approval-payload, cross-process-reviewed-confirm]

key-files:
  created: []
  modified:
    - skills/graduate-resume/scripts/graduate_resume_cli.py
    - skills/graduate-resume/scripts/graduate_resume_render.py
    - skills/graduate-resume/scripts/graduate_resume_delivery.py
    - skills/graduate-resume/scripts/test_render_contract.py
    - skills/graduate-resume/scripts/test_delivery_transaction.py
    - skills/graduate-resume/scripts/test_phase48_cli.py

key-decisions:
  - "任何含 target 的正式 render/batch 都必须显式授权独立 evidence root；generic-only publication 公开空 target_conditions 且不创建隐藏证据。"
  - "历史 stem 以 canonical 候选人安全姓名生成的冻结 owner_prefix、独立命名结构和登记主题校验，不查询当前 authority safe_stems。"
  - "patch 与 authority 使用同一 reviewed approval gate；摘要绑定完整 candidate/current bytes、canonical hash 和 delivery/evidence root 规范路径及 inode。"

patterns-established:
  - "Condition evidence: bounded public rows -> canonical hidden projection -> digest recomputation -> held no-follow evidence root。"
  - "Publication review: process A preflight digest -> user review -> process B explicit digest -> service-layer canonical payload rebuild -> publish or zero mutation。"

requirements-completed: [TARGET-02, DELIVERY-02, DELIVERY-03]

duration: 37min
completed: 2026-07-18
---

# Phase 48 Plan 06: 可审计条件证据与跨进程确认 Summary

**render 与 batch 现在共享逐条件四态审阅面，完整理由持久化到 digest 绑定的独立隐藏根；历史可跨 authority 删除继续验证，正式发布必须提交上一进程审阅的完整事务摘要。**

## Performance

- **Duration:** 37 min
- **Started:** 2026-07-18T12:46:57Z
- **Completed:** 2026-07-18T13:24:17Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- 单 target render 与 batch 均输出同 schema 的 `target_conditions[target_id]`：只公开 condition ID、受控 predicate、四态 state、counts、warning count、gap allow 和 evidence digest；generic 固定为空映射。
- 完整 condition projection 以 canonical JSON 持久化到调用方授权的独立 evidence root，绑定 canonical hash、VersionProjection digest 和 condition digest；delivery root 仍只有正式 triples、history 与既有 support 目录。
- Evidence sink 逐级 `O_NOFOLLOW` 打开并持有目录身份，拒绝投递子树、symlink、unknown、非规范 JSON、stale 或 inode swap；正式 publish 前再次验证身份。
- `DeliverySpec.owner_prefix` 由 verified canonical 姓名的安全组件冻结；history 接受已退出当前 authority 的安全旧 stem，同时继续拒绝其他候选人、非法结构、未登记主题、partial/extra/symlink/目录/FIFO triple。
- patch 与 authority 均要求用户提交上一进程的 64 位小写 approval digest；服务层重建包含完整 candidate/current bytes、delta、canonical hash、delivery/evidence root path + `st_dev/st_ino` 的唯一 canonical payload。
- 两进程真实 CLI 回归证明 canonical、页数 candidate、照片 bytes、current、delivery/evidence 替代路径、inode 与 symlink 变化都会拒绝旧摘要且保持 current/history 不变。

## Task Commits

1. **Task 1 RED：逐条件公开投影与持久隐藏证据负例** - `319b5cf` (test)
2. **Task 1 GREEN：digest-bound 独立 evidence sink** - `3b6e577` (feat)
3. **Task 2 RED：目标删除后历史重开与连续 no-op 负例** - `d9ea1a8` (test)
4. **Task 2 GREEN：owner-prefix 独立 history grammar** - `cead524` (feat)
5. **Task 3 RED：patch/CLI 未绑定 reviewed digest 负例** - `c9e49ee` (test)
6. **Task 3 GREEN：跨进程 canonical approval payload** - `bdc500d` (feat)

## Files Created/Modified

- `skills/graduate-resume/scripts/graduate_resume_cli.py` - 统一公开条件 schema、`--evidence-root`、`--approval-digest` 参数组合与原样转交。
- `skills/graduate-resume/scripts/graduate_resume_render.py` - held/no-follow EvidenceSink、canonical evidence 验证和原子持久化。
- `skills/graduate-resume/scripts/graduate_resume_delivery.py` - 冻结 owner prefix、独立 history grammar、完整 approval payload 和双模式摘要门。
- `skills/graduate-resume/scripts/test_render_contract.py` - evidence digest 重算、根隔离、unknown 与 identity swap 回归。
- `skills/graduate-resume/scripts/test_delivery_transaction.py` - 历史连续性、owner-bound 完整 triple、patch 摘要门和 payload 重算回归。
- `skills/graduate-resume/scripts/test_phase48_cli.py` - 两进程确认、照片/canonical/candidate/root TOCTOU、连续删除/no-op 与公开四态端到端回归。

## Decisions Made

- evidence 文件使用 `<version-id>-<condition-digest>.json` 稳定命名；同一条件摘要对应的新 canonical/projection 以原子替换更新最新审计绑定，已有文件必须先通过完整 canonical schema 校验。
- approval payload 直接使用 candidate/current 完整 bytes 的十六进制投影，而不是只保存单文件哈希，使服务层的公开摘要可由同一生产 serializer 无歧义重算。
- delivery root 和 evidence root 都绑定规范绝对路径及 held identity；bytes 相同但换根、同路径换 inode 或换成 symlink 均不是同一次已审阅事务。
- history grammar 只把 owner prefix、通用/定向命名结构和登记主题视为持久 authority；当前目标集合只决定 current，不决定历史合法性。

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Evidence sink 首轮在 macOS `/var` 系统 symlink 上过度拒绝；改为解析已存在父目录、保留授权叶节点 no-follow 后，系统路径规范化与用户叶 symlink 拒绝同时成立。
- Evidence 文件不能仅因 canonical 删除了另一个 target 就永久冲突；保持稳定文件名并对已验证旧记录做原子替换后，缩减 authority 的预检/确认可连续运行。

## Known Stubs

None. 修改文件中未发现流向正式输出的 placeholder、TODO、FIXME、硬编码空数据或未接通 mock。

## Threat Review

- `T-48-G06-01/02` 由公开字段 allowlist、完整隐藏 projection、production canonical JSON 和 condition digest 重算闭环。
- `T-48-G06-03/04` 由 held/no-follow evidence root、冻结 owner prefix、独立 history grammar 和 exact non-empty regular triple 闭环。
- `T-48-G06-05/06` 由跨进程显式摘要、服务层双模式重算、完整 root identity 绑定和删除后连续 no-op 回归闭环。
- 未新增网络 endpoint、认证路径、凭据、数据库/schema 或计划威胁模型之外的 trust boundary。

## Verification

- `python3 -m unittest skills/graduate-resume/scripts/test_render_contract.py -v`：11/11 PASS。
- `python3 -m unittest skills/graduate-resume/scripts/test_delivery_transaction.py -v`：14/14 PASS。
- `python3 -m unittest skills/graduate-resume/scripts/test_phase48_cli.py -v`：16/16 PASS。
- `python3 -m unittest discover -s skills/graduate-resume/scripts -p 'test_*.py' -v`：72/72 PASS，约 36 秒。
- `python3 -m py_compile` 覆盖 CLI、render、delivery 三个实现模块：PASS。
- `git diff --check`：PASS。

## TDD Gate Compliance

- Task 1：RED `319b5cf` 先证明 render 丢失逐条件 rows、无持久 evidence 且不要求授权根；GREEN `3b6e577` 后专项通过。
- Task 2：RED `d9ea1a8` 先证明 `DeliverySpec` 无冻结 owner prefix、目标删除后的历史无法安全重开；GREEN `cead524` 后连续 no-op 与历史负例通过。
- Task 3：RED `c9e49ee` 先证明 patch 可无摘要发布、CLI confirm 自动采用新摘要；GREEN `bdc500d` 后真实两进程和 root/candidate TOCTOU 回归通过。

## User Setup Required

None - no external service configuration required. 本地验证继续使用仓库已有 Typst 0.15.0、Pillow、PyMuPDF 与 skill-local fonts。

## Next Phase Readiness

- TARGET-02、DELIVERY-02、DELIVERY-03 的 Phase 48 verifier 反例已全部变为自动化回归；Phase 48 六个实现计划均已有 summary，可进入后续 verifier。
- Phase 49 可基于完整可信三件套、持久条件证据、连续 history 和 reviewed digest 做六 runtime、聚合故障注入、PDF 结构/布局与字体 UAT。
- 无实现 blocker；是否把 Phase 48 标记 complete 仍由 execute-phase 后续 verifier 决定。

## Self-Check: PASSED

- 六个 key-files.modified 均存在；本计划未声明 created implementation file。
- `319b5cf`、`3b6e577`、`d9ea1a8`、`cead524`、`c9e49ee`、`bdc500d` 均存在于 git history。
- render 11/11、delivery 14/14、CLI 16/16、全量 72/72、py_compile 和 diff check 全部通过。

---
*Phase: 48-deterministic-targeted-rendering-clean-batch-delivery*
*Completed: 2026-07-18*
