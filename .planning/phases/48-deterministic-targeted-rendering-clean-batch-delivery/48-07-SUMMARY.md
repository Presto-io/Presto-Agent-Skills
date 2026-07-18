---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
plan: 07
subsystem: graduate-resume-canonical-input-security
tags: [python, metadata, no-follow, snapshot, sha256, tdd]

requires:
  - phase: 48-deterministic-targeted-rendering-clean-batch-delivery
    plan: 06
    provides: verified-only publication、final Markdown hash 与 reviewed approval digest 链路
provides:
  - 非 target id/status 与 target id 的严格唯一 metadata authority
  - canonical Markdown 的有界 no-follow 单次 descriptor snapshot
  - final Markdown、evidence 与 approval payload 共享的 source SHA-256
affects: [48-09-verification, graduate-resume-targeting, graduate-resume-publication]

tech-stack:
  added: []
  patterns: [exact-metadata-field-set, bounded-no-follow-snapshot, frozen-source-hash]

key-files:
  created: []
  modified:
    - skills/graduate-resume/scripts/graduate_resume_cli.py
    - skills/graduate-resume/scripts/test_phase48_cli.py

key-decisions:
  - "非 target 注释只接受精确 id/status，target 注释只接受精确 id；重复、空值、缺失和额外字段在事实投影前统一失败。"
  - "canonical 输入上限固定为 4 MiB，并以 O_NOFOLLOW 普通文件 descriptor 循环读取后冻结 bytes 与 SHA-256。"
  - "canonical path 仅保留定位和默认 assets-root 语义；正式渲染与审批不得再次从该路径读取事实或 hash。"

patterns-established:
  - "Metadata authority: 标题建立 pending entry，恰好一个 exact resume comment 消费它，条目切换或结束前未消费即失败。"
  - "Canonical snapshot: resolved parent + no-follow leaf -> fstat -> bounded loop -> identity/size recheck -> immutable bytes/hash。"

requirements-completed: [TARGET-01, TARGET-02, TARGET-03, DELIVERY-02]

duration: 14min
completed: 2026-07-18
---

# Phase 48 Plan 07: 严格 Metadata 与 Canonical 单快照 Summary

**正式发布现在只消费显式 verified 的严格 Markdown metadata，并让事实解析、final Markdown 和 reviewed approval 共同绑定同一次 no-follow canonical bytes 快照。**

## Performance

- **Duration:** 14 min
- **Started:** 2026-07-18T15:01:23Z
- **Completed:** 2026-07-18T15:15:29Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- `parse_metadata` 在构造映射前拒绝非法 token、空 key/value 和重复 key；非 target 只允许且必须含 `id/status`，target 只允许且必须含 `id`。
- 每个 Markdown 条目必须恰好消费一个 resume comment；缺失、第二个 comment、拼错/额外字段均在事实投影和投递 mutation 前稳定失败，删除了 verified 缺省提升。
- `ResumeDocument` 冻结保存 `source_bytes/source_sha256`；canonical leaf 通过 `O_NOFOLLOW`、普通文件 `fstat`、4 MiB 上限和短读循环只读取一次。
- load 后 canonical 被换 bytes、inode 或 symlink 时，本次 final Markdown 与 `DeliverySpec.canonical_hash` 仍绑定原始 snapshot；下一独立确认重新加载后会拒绝旧 digest。

## Task Commits

1. **Task 1 RED：严格 metadata authority 负例** - `37983f8` (test)
2. **Task 1 GREEN：精确字段集与单注释消费** - `23493db` (fix)
3. **Task 2 RED：canonical no-follow/size/swap 负例** - `1b0527f` (test)
4. **Task 2 GREEN：冻结 canonical descriptor snapshot** - `d222d7a` (fix)

## Files Created/Modified

- `skills/graduate-resume/scripts/graduate_resume_cli.py` - 严格 metadata parser、唯一条目 metadata 消费状态、冻结 canonical bytes/hash 及 publication 复用。
- `skills/graduate-resume/scripts/test_phase48_cli.py` - metadata 状态提升、重复键、symlink/特殊文件/超限/UTF-8/短读和 load 后 swap 回归。

## Decisions Made

- 统一以 `CANONICAL_INPUT_INVALID` 表达 canonical symlink、特殊文件、超限、读取变化和无效 UTF-8，公开错误不携带候选内容或绝对路径。
- 使用解析父目录后拼接未解析 leaf 的路径，允许正常系统父级 symlink，同时确保 canonical leaf 本身由 `O_NOFOLLOW` 拒绝。
- descriptor 读取前后比较 device、inode、size、mtime 和 ctime，并要求读取字节数等于初始 size；读取中变化失败关闭。

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- 全量 unittest 由工具返回持续会话；收取剩余输出后确认 75/75 PASS，无测试中断或遗漏。

## Known Stubs

None. 修改文件中没有流向正式输出的 placeholder、TODO、FIXME、硬编码空值或未接通 mock。

## Threat Review

- `T-48-G07-01`：exact field set、重复 token/comment 拒绝和无 verified 缺省关闭 metadata spoofing。
- `T-48-G07-02/04`：no-follow regular descriptor、4 MiB 上限、短读循环和读取前后 identity 复验关闭 canonical tampering/DoS。
- `T-48-G07-03`：final Markdown、condition evidence 和 approval payload 复用 `source_sha256`，不再按 canonical path 二次读取。
- 未新增网络 endpoint、认证路径、凭据、数据库/schema 或计划威胁模型之外的 trust boundary。

## Verification

- `python3 -m unittest skills/graduate-resume/scripts/test_phase48_cli.py -v`：19/19 PASS。
- `python3 -m unittest discover -s skills/graduate-resume/scripts -p 'test_*.py' -v`：75/75 PASS，40.712 秒。
- `python3 skills/graduate-resume/scripts/graduate_resume_cli.py verify`：15 个 fixture/layout 结果 PASS。
- `python3 -m py_compile skills/graduate-resume/scripts/graduate_resume_cli.py skills/graduate-resume/scripts/test_phase48_cli.py`：PASS。
- `git diff --check cc6f09e..HEAD`：PASS。
- 静态检查确认生产代码不存在 `metadata.get("status", "verified")`、`document.path.read_bytes()` 或等价 canonical 二次 hash。

## TDD Gate Compliance

- Task 1：RED `37983f8` 先复现缺失 status 被提升、重复键覆盖和重复 comment 可通过；GREEN `23493db` 后专项及 fixture 验证通过。
- Task 2：RED `1b0527f` 先复现 leaf symlink 跟随、超限输入被接受、UTF-8 内部错误和旧事实绑定新 hash；GREEN `d222d7a` 后专项通过。
- 两个 RED 均因目标行为缺失而失败，不是导入、语法或测试环境错误；GREEN 后再通过完整 75-test 套件。

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- CR-01 metadata 状态提升与 CR-03 canonical hash 错绑均已转为公开 CLI 自动回归，可由 48-09 聚合验证消费。
- Phase 48 仍需 48-08 关闭照片 descriptor snapshot、投递 support 目录污染和 Typst 版本门禁；本计划未触碰其所有权文件。

## Self-Check: PASSED

- 两个 key-files.modified 与本 SUMMARY 均存在。
- `37983f8`、`23493db`、`1b0527f`、`d222d7a` 均存在于 git history，且 RED 均先于对应 GREEN。
- CLI 19/19、graduate-resume 全量 75/75、fixture verify、py_compile 和 diff check 全部通过。

---
*Phase: 48-deterministic-targeted-rendering-clean-batch-delivery*
*Completed: 2026-07-18*
