---
phase: 45-clean-delivery-standardization
plan: 06
subsystem: delivery
tags: [bash, typst, filesystem-safety, rollback, exact-managed-set]

requires:
  - phase: 45-clean-delivery-standardization
    provides: explicit DeliverySpec, fixed fault registry, and clean-delivery state machine
provides:
  - Bash-only same-stem Markdown and Typst pair transaction with optional PDF triple
  - Candidate-first expected/PDF gates, exact no-op, max-plus-one history, and handled rollback
  - Fixed-name cleanup, same-root lock, and unsafe path/root refusal
  - Six-runtime gongwen clean-delivery contract
affects: [45-08, 45-09, gongwen]

tech-stack:
  added: []
  patterns: [quoted-fixed-name-arrays, owned-shell-run, stdin-typst-candidate, exact-pair-triple]

key-files:
  created:
    - skills/gongwen/scripts/gongwen_lib/delivery.sh
    - skills/gongwen/tests/test_clean_delivery.sh
  modified:
    - skills/gongwen/scripts/gongwen_lib/commands.sh
    - skills/gongwen/scripts/gongwen.sh
    - skills/gongwen/SKILL.md
    - skills/gongwen/references/format-and-rendering.md
    - skills/gongwen/tests/test_heading_normalization.sh

key-decisions:
  - "The --typ real parent and stem own the delivery root; optional --pdf must use that exact root and stem and changes the managed path set."
  - "PDF compilation consumes candidate Typst bytes through stdin while the reviewed Markdown parent remains the Typst root for existing relative assets/... references."
  - "Shell cleanup mutates only validated fixed names recorded for this run; unknown, legacy, symlink, partial, stale-work, or unsafe path states fail before current mutation."

patterns-established:
  - "Bash transaction: same-root mkdir lock plus owned candidate/rollback/evidence directories and EXIT/INT/TERM rollback."
  - "Pair/triple equality: exact filename set and bytes; optional PDF addition or removal archives the complete prior bundle."

requirements-completed:
  - CLEAN-01
  - CLEAN-02
  - CLEAN-03
  - REV-01
  - REV-02
  - REV-03
  - REV-04
  - SAFE-01
  - VERIFY-01
  - DOCS-01
  - RUNTIME-01

duration: 21 min
completed: 2026-07-16
---

# Phase 45 Plan 06: Gongwen Bash Delivery Transaction Summary

**Gongwen 现以纯 Bash 将 reviewed Markdown、candidate Typst 和 optional PDF 作为 exact pair/triple 安全发布，并覆盖 no-op、whole-bundle history 与 handled rollback。**

## Performance

- **Duration:** 21 min
- **Started:** 2026-07-16T02:35:35Z
- **Completed:** 2026-07-16T02:56:35Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- 新增 self-contained `delivery.sh`，使用 same-root exclusive lock、owned `.work/<run-id>/{candidate,rollback,evidence}`、quoted fixed-name arrays、exact set+bytes no-op 和 `history/` max+1。
- `render` 先在 candidate 复制 reviewed Markdown、生成 Typst、执行 expected gate，再从 candidate Typst 编译和验证 `%PDF-`；全部通过后才发布。
- pair/triple 变化整体归档；PDF 增加或移除都保留旧完整 bundle，handled fault、`INT`、`TERM` 恢复 prior current/history/sources。
- 真实 public CLI 矩阵覆盖 seven faults、history gap、optional set、lock、stale work、unknown/legacy/symlink/traversal/cross-root/different-stem 和 owned cleanup。
- canonical skill 与 rendering reference 同步 exact artifacts、支持目录、原子性边界和六 runtime whole-folder/fallback/依赖/权限说明。

## Task Commits

1. **Task 1 RED: gongwen clean-delivery transaction matrix** - `403f371` (test)
2. **Task 1 GREEN: Bash-only explicit-set transaction** - `c89d568` (feat)
3. **Task 1 regression unblock: isolate heading comparison roots** - `541c405` (test)
4. **Task 2: public candidate gates and runtime contract** - `52e6205` (docs)

## Files Created/Modified

- `skills/gongwen/scripts/gongwen_lib/delivery.sh` - fixed-name Bash transaction、lock、history、no-op、rollback 和安全 root/path inspection。
- `skills/gongwen/tests/test_clean_delivery.sh` - deterministic fake Typst 与真实 public CLI transaction/fault matrix。
- `skills/gongwen/scripts/gongwen_lib/commands.sh` - candidate Markdown/Typst/PDF 生成、expected/PDF pre-publication gate 和 publisher 接线。
- `skills/gongwen/scripts/gongwen.sh` - 仅 source skill-local delivery library。
- `skills/gongwen/SKILL.md` - exact pair/triple、支持目录、failure 和六 runtime 契约。
- `skills/gongwen/references/format-and-rendering.md` - candidate、history、rollback、asset root 和 verification 细节。
- `skills/gongwen/tests/test_heading_normalization.sh` - 两个对比 fixture 使用各自 exact-stem owned root。

## Decisions Made

- `--typ` 的真实 parent/stem 是唯一 authority；`--pdf` 必须同根同 stem，pair 与 triple 是两个不同 exact sets。
- `example` 保持显式 authoring output，不调用 delivery transaction、不创建 history。
- `cmp -s` 优先，缺失时回退既有 `same_file_shell`；Markdown→Typst 转换仍不调用外部 converter。
- portable guarantee 只覆盖逐路径替换和 handled error/INT/TERM，不声称 SIGKILL、断电或多文件硬原子。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Existing heading regression used two stems in one exact delivery root**
- **Found during:** Task 2 renderer regression
- **Issue:** 旧测试先后向同一临时根发布 `clean.typ` 与 `numbered.typ`；新 single-stem root 必须把第二套视为 unknown，导致计划要求的既有回归无法运行。
- **Fix:** 经 orchestrator 明确授权，仅把两个 fixture 输出改到各自 owned 临时子根，再保持原 byte comparison 与字体断言不变。
- **Files modified:** `skills/gongwen/tests/test_heading_normalization.sh`
- **Verification:** `bash skills/gongwen/tests/test_heading_normalization.sh` PASS。
- **Committed in:** `541c405`

**2. [Rule 1 - Bug] Nested candidate Typst initially changed relative asset resolution**
- **Found during:** Task 2 real Typst regression
- **Issue:** 直接以 `.work/.../candidate/notice.typ` 路径编译会把 `assets/...` 相对路径错误解析到 candidate 子目录。
- **Fix:** Typst 从 stdin 读取 candidate Typst bytes，并以 reviewed Markdown parent 作为 `--root`；PDF 仍只由 candidate Typst 生成，既有 relative asset 语义保持。
- **Files modified:** `skills/gongwen/scripts/gongwen_lib/commands.sh`, `skills/gongwen/references/format-and-rendering.md`, `skills/gongwen/tests/test_clean_delivery.sh`
- **Verification:** fake Typst public matrix 与本机真实 Typst public triple 均 PASS。
- **Committed in:** `52e6205`

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 bug). **Impact:** 保持既有 renderer regression 和 asset 解析语义，无公开命令、参数或交付格式回退；仅一个经授权的测试文件超出原 `files_modified`。

## Issues Encountered

- 计划指定的中央命令 `python3 test/clean-delivery/verify_clean_delivery.py --skill gongwen` 当前不可用；45-01 foundation harness 只暴露 `--self-test`，真实 `--skill/--gate` 接线明确归属 45-09。未越界修改中央 harness，以 skill-local public CLI、真实 Typst 与 foundation self-test 提供当前证据。

## User Setup Required

None - 未新增依赖或外部服务。Optional PDF 继续要求已安装的 Typst CLI；纯 pair 模式只需要 Bash 和 `cmp`（缺失时使用 shell fallback）。

## Verification Evidence

- `bash skills/gongwen/tests/test_clean_delivery.sh` — PASS：7/7 faults、2/2 signals、pair/triple、PDF 增减、`001/003 -> 004`、lock、unsafe root/path 与 cleanup。
- `bash skills/gongwen/tests/test_heading_normalization.sh` — PASS：heading normalization 与字体 fallback 回归。
- `bash -n skills/gongwen/scripts/gongwen.sh skills/gongwen/scripts/gongwen_lib/*.sh` — PASS。
- 本机 `/opt/homebrew/bin/typst` + 真实 public CLI — PASS：生成 exact Markdown/Typst/PDF triple，PDF header 为 `%PDF-`。
- `python3 test/clean-delivery/verify_clean_delivery.py --self-test all` — PASS。
- 静态安全 scan — PASS：`delivery.sh` 无 root wildcard rm/find-delete、无 Python/Node 或 sibling/root runtime dependency。
- `git diff --check` — PASS。

## Next Phase Readiness

- Gongwen adapter 已可进入 45-08 仓库级文档同步和 45-09 中央六技能 strict aggregate 接线。
- skill folder 内无剩余 blocker；中央 `--skill gongwen` route 仍由 45-09 owning plan 完成。

## Self-Check: PASSED

- 两个 created files 与五个 modified files 均存在。
- 四个 `45-06` production/task commits 均可由 git object database 验证。
- 所有 acceptance criteria 与计划级 verification 已由 shell aggregate、真实 public CLI、真实 Typst、renderer regression 和 foundation self-test 重跑覆盖。

---
*Phase: 45-clean-delivery-standardization*
*Completed: 2026-07-16*
