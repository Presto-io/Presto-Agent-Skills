---
phase: 45-clean-delivery-standardization
plan: 07
subsystem: delivery
tags: [node, bash, filesystem-safety, dynamic-bundle, rollback, typst, pdf-merge]

requires:
  - phase: 45-clean-delivery-standardization
    provides: explicit DeliverySpec, fixed fault registry, and candidate-first state machine
provides:
  - Model-driven dynamic 1+1+N Node delivery transaction
  - Owned .work run orchestration for module, merge, status, and debug evidence
  - Exact no-op, course-prefix whole history, seven-fault and signal rollback
  - Six-runtime teaching-design-package clean-delivery contract
affects: [45-08, 45-09, teaching-design-package]

tech-stack:
  added: []
  patterns: [model-derived-managed-set, single-complete-group-discovery, owned-run-evidence, completed-name-rollback]

key-files:
  created:
    - skills/teaching-design-package/scripts/delivery-transaction.js
    - skills/teaching-design-package/scripts/test-delivery-transaction.js
  modified:
    - skills/teaching-design-package/scripts/package-model.js
    - skills/teaching-design-package/scripts/teaching-design-package.sh
    - skills/teaching-design-package/SKILL.md
    - skills/teaching-design-package/references/format-and-orchestration.md

key-decisions:
  - "public_delivery.expected_public_filenames is the sole dynamic mutation authority; current discovery accepts zero or one complete old prefix group and fails closed on ambiguity."
  - "Model, status, module, merge, and debug data remain evidence under an owned .work run or an explicit diagnostic workdir and never become current."
  - "Portable guarantees cover exact candidate isolation and handled error/INT/TERM rollback, not SIGKILL, power loss, or multi-path hard atomicity."

patterns-established:
  - "Dynamic group transaction: exact relative path-set plus bytes, max-plus-one whole history, and completed-name rollback."
  - "One publication call: the shell completes every module/merge/final-ready gate before invoking the model-driven Node publisher once."

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

duration: 10h 41m
completed: 2026-07-16
---

# Phase 45 Plan 07: Teaching Design Package Dynamic Bundle Transaction Summary

**Teaching Design Package 现以 model-derived exact `1+1+N` candidate 完成模块/merge 验门、课程前缀整组 history、no-op 与 handled rollback，并彻底移除生成前和失败时 public-root 清空。**

## Performance

- **Duration:** 10h 41m
- **Started:** 2026-07-16T03:07:41Z
- **Completed:** 2026-07-16T13:48:28Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- 新增 self-contained Node publisher，消费 validated `expected_public_filenames`，覆盖 held dev/ino、no-follow inspection、same-root lock、exact path-set+bytes、max+1 history、explicit replace/fsync 和 completed-name rollback。
- current discovery 只接受零套或唯一完整旧 course-prefix group；prefix change 成套归档，多 prefix、partial、unknown、legacy hidden、media、symlink、traversal 和 stale work 均在 mutation 前失败关闭。
- `render-package --pdf` 把 model、模块 Markdown/Typst/PDF、status、debug、merge plan/log 全部映射到 `.work/<run-id>/evidence/`，完整 public candidate 后只调用 publisher 一次。
- 删除生成前、failure path 和 final-ready failure 的 destructive cleanup，以及逐文件 final-root copy；真实 module/merge/final validation failure 保持 current/history/sources 不变。
- 同步 dynamic artifact、diagnostic workdir、history/rollback/ambiguity 和六 runtime whole-folder、fallback、依赖、权限与 sandbox/allowlist 契约。

## Task Commits

1. **Task 1 RED: dynamic bundle transaction matrix** - `7b8be4e` (test)
2. **Task 1 GREEN: model-driven Node publisher** - `76c4b1e` (feat)
3. **Task 2 RED: real render-package isolation regression** - `ee756f6` (test)
4. **Task 2 GREEN: owned run and single publisher integration** - `dd1a707` (feat)
5. **Task 3: dynamic artifact and six-runtime contract** - `ede93a3` (docs)
6. **Acceptance audit: dynamic N=3 and stale-work boundaries** - `fb79ea9` (test)

## Files Created/Modified

- `skills/teaching-design-package/scripts/delivery-transaction.js` - dynamic exact-set publisher、history、rollback、锁、identity 和 owned cleanup。
- `skills/teaching-design-package/scripts/test-delivery-transaction.js` - helper、真实 public CLI、module/merge/fault/signal/unknown/work 矩阵。
- `skills/teaching-design-package/scripts/package-model.js` - run-relative evidence paths、work layout 和 explicit public filename authority。
- `skills/teaching-design-package/scripts/teaching-design-package.sh` - owned run producer、module/merge gates、diagnostic workdir 和 single publisher call。
- `skills/teaching-design-package/SKILL.md` - exact current/support/history/failure/runtime 安全入口。
- `skills/teaching-design-package/references/format-and-orchestration.md` - candidate、registry、merge、ambiguity、history、rollback 和 portability 细节。

## Decisions Made

- model filename prefix 与 `expected_public_filenames` 同时定义 candidate 和旧组 suffix discovery；publisher 不硬编码当前四文件组，也不按 mtime 选旧组。
- `model`、`manifest`、non-PDF `render-package`、`plan-split` 和 `render-split` 的 `--out-dir` 是显式 diagnostic workdir，不是 final delivery root。
- 无 sibling skill 或仓库根 runtime dependency；Bash/Node/Typst 与 `pdfunite`、`qpdf`、Python PyMuPDF merge fallback 均保持现有公开命令/flags。

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- 计划指定的中央 `python3 test/clean-delivery/verify_clean_delivery.py --skill teaching-design-package` 与 `--gate documentation_runtime_contract_gate` 路由尚不存在；45-01 foundation harness 仅支持 `--self-test`，45-09 明确拥有六技能接线。未越界修改 shared harness，以 skill-local 8 组真实矩阵、foundation self-test、机械文档断言和本机真实 Typst/PyMuPDF merge 提供等价证据。
- 首次 production 静态扫描命中测试文件中用于禁止模式 mutation guard 的字面量；将 production scan 限定到生产源码后通过，测试断言本身保留。

## User Setup Required

None - 未新增依赖或外部服务。Final PDF 继续要求 Typst 和一个 PDF merge path；本机验证使用 Typst + Python PyMuPDF fallback。

## Verification Evidence

- `node skills/teaching-design-package/scripts/test-delivery-transaction.js` — PASS：8/8 groups、7/7 faults、SIGINT/SIGTERM、dynamic N=3、first/same/change、001/003→004、module/merge/final-validation failures、unknown/symlink/lock/stale work。
- `bash -n`、四个 Node `--check` 与 `git diff --check` — PASS。
- 本机真实 Typst + Python PyMuPDF merge + public `render-package --pdf` — PASS：exact model-derived 四文件，无 `.work` 或 legacy hidden sidecar。
- `model`、`manifest`、non-PDF `render-package`、`plan-split`、`render-split` 显式 diagnostic workdir — PASS，公开名称和 flags 保持。
- `python3 test/clean-delivery/verify_clean_delivery.py --self-test all` — PASS。
- 六 runtime documentation equivalent assertions — PASS；中央 `--skill/--gate` route 的预期 usage error 归属 45-09。
- Production mutation guard — PASS：无 `cleanup_public_root`、legacy hidden work/staging/debug、root find-delete、direct sequential final copy 或 hardcoded current group。

## Next Phase Readiness

- Teaching Design Package adapter 已可进入 45-08 仓库级文档同步与 45-09 中央六技能 strict aggregate 接线。
- Skill folder 内无剩余 blocker；中央 `--skill teaching-design-package` route 仍由 45-09 owning plan 完成。

## Self-Check: PASSED

- 两个 created files 与四个 modified files 均存在。
- 六个 `45-07` production/task commits 均可由 git object database 验证。
- 所有任务 acceptance criteria 与计划级 success criteria 已由 Node、真实 shell/public CLI、真实 Typst/merge、fault/signal 和文档断言重跑覆盖。

---
*Phase: 45-clean-delivery-standardization*
*Completed: 2026-07-16*
