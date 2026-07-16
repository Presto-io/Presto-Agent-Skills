---
phase: 45-clean-delivery-standardization
plan: 08
subsystem: documentation
tags: [clean-delivery, runtime-portability, skill-authoring, directory-contract]

requires:
  - phase: 45-clean-delivery-standardization
    provides: six implemented skill-local delivery transactions from plans 45-02 through 45-07
provides:
  - Repository discovery and directory ownership aligned to the explicit six-skill clean-delivery set
  - Six-runtime dependency, permission, fallback, delivery, and verification boundary matrix
  - Safe default template for future file-writing skills
affects: [45-09, repository-discovery, compatibility-matrix, skill-authoring]

tech-stack:
  added: []
  patterns: [explicit-managed-set, whole-folder-installation, installation-time-runtime-verification, safe-authoring-defaults]

key-files:
  created: []
  modified:
    - README.md
    - skills/README.md
    - docs/directory-spec.md
    - docs/compatibility-matrix.md
    - templates/skill/SKILL.md

key-decisions:
  - "Repository documentation names exactly the six implemented writing skills; no seventh skill inherits clean-delivery status implicitly."
  - "Verification workdirs are caller-owned evidence roots, not delivery roots, and normal publication never persists diagnostic artifacts as current."
  - "OpenClaw and Hermes Agent support remains installation-time verified with explicit public-script fallback and no automatic-discovery claim."

patterns-established:
  - "Shared discovery pattern: explicit managed set, candidate-first gate, byte-identical no-op, whole-bundle max+1 history, handled rollback, and confirmation-bound unknown cleanup."
  - "Future authoring pattern: whole-folder installation plus real dependency, execute/read/write, sandbox/allowlist, delivery/.work, and verify-workdir declarations for all six runtimes."

requirements-completed:
  - CLEAN-01
  - CLEAN-02
  - CLEAN-03
  - SAFE-02
  - DOCS-01
  - RUNTIME-01

duration: 20 min
completed: 2026-07-16
---

# Phase 45 Plan 08: Shared Clean-Delivery Documentation Summary

**仓库入口、目录规范、六 runtime 矩阵与新技能模板现已共同表达六技能 explicit managed clean-delivery 契约**

## Performance

- **Duration:** 20 min
- **Started:** 2026-07-16T14:23:00Z
- **Completed:** 2026-07-16T14:43:34Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- README、skills index 与 directory spec 明确恰好六个已适配技能，并区分 canonical repository ownership、用户 delivery root 和调用方 verification evidence root。
- Compatibility matrix 统一六 runtime 的 whole-folder discovery、显式 fallback、真实依赖、execute/read/write、sandbox/allowlist、delivery `.work` 与 verify workdir 边界。
- 新技能模板默认要求 stable explicit set、optional set、sources/assets ownership、candidate minimal gate、byte-identical no-op、whole-bundle max+1 history、handled rollback 和 snapshot-bound unknown confirmation。
- 公共文档不再把 legacy hidden diagnostics、manifest/status/model/log/diff/screenshot/staging/failure artifacts 或空 support directory 写成 current，也不承诺自动 discovery、自动删 history 或多文件硬原子。

## Task Commits

Each task was committed atomically:

1. **Task 1: 同步 repository discovery 与 directory ownership** - `8be537e` (docs)
2. **Task 2: 更新六 runtime matrix 与新技能默认模板** - `7ed2262` (docs)

## Files Created/Modified

- `README.md` - 新增六技能共享交付边界、cleanup 链接并修正旧 evidence 表述。
- `skills/README.md` - 固化封闭覆盖集合、candidate/no-op/history/rollback 与 current/evidence 边界。
- `docs/directory-spec.md` - 分离 canonical skill folder、用户 delivery root 和 caller verification workdir ownership。
- `docs/compatibility-matrix.md` - 增加六 runtime 完整 portability dimensions 与六技能外部依赖矩阵。
- `templates/skill/SKILL.md` - 为未来写文件技能加入可执行的安全 authoring contract 和验证清单。

## Decisions Made

- 共享文档只描述六技能共同语义，不复制各技能的长文件名表；具体 stable names 和 minimal validators 继续由 owning skill contract 管理。
- OpenClaw/Hermes 的 exact path、frontmatter、support/script discovery 与权限均保持 installation-time verification，失败时走显式 public script，不推测自动发现。
- Portable publication guarantee 限定为 candidate isolation、单路径 replace 与 handled failure/INT/TERM rollback；SIGKILL、断电和多文件跨路径原子继续明确不保证。

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- 计划指定的 `python3 test/clean-delivery/verify_clean_delivery.py --gate documentation_runtime_contract_gate --scope ...` 尚未由中央 harness 实现；当前 parser 仅接受 `--self-test`，真实 `--gate/--scope` 路由属于后续 45-09 owning plan。未越界修改 shared harness；改用计划结构检查、五文档/六技能/六 runtime/本地链接机械断言、`--self-test all` 和 `git diff --check` 完成等价文档验证。

## User Setup Required

None - no external service configuration required.

## Verification Evidence

- `python3 test/clean-delivery/verify_clean_delivery.py --self-test all` — PASS。
- 45-08 PLAN frontmatter、两项 task 和 required XML sections structural gate — PASS。
- 五个 shared docs 的 canonical contract link、本地 Markdown link existence、封闭六技能覆盖 — PASS。
- 六个 current `SKILL.md` 的六 runtime rows、whole-folder/fallback/history/`.work` 与 skill-local unknown/symlink contract coverage — PASS。
- Task 1 repository discovery/ownership assertions与 Task 2 matrix/template required-term assertions — PASS。
- `git diff --check -- README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md templates/skill/SKILL.md` — PASS。

## Next Phase Readiness

- Shared documentation authorities are stable for 45-09 strict aggregate, code review, and final 12/12 milestone verification.
- The central harness still needs its planned `--gate/--scope` and six-skill aggregate wiring in 45-09; no 45-08 documentation blocker remains.

## Self-Check: PASSED

- 两个 task commits 均可由 `git log --grep=45-08` 检索，五个计划文件已提交且 worktree 中无未提交产品变更。
- 所有可在 45-08 ownership 内执行的 acceptance criteria 和计划级 verification 已重跑通过；未实现中央路由已明确留给 owning 45-09。

---
*Phase: 45-clean-delivery-standardization*
*Completed: 2026-07-16*
