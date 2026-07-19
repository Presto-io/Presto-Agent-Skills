---
phase: 49-runtime
plan: 01
subsystem: verification
tags: [graduate-resume, verification, pdf, png, evidence, active-run]
requires:
  - phase: 48-deterministic-targeted-rendering-clean-batch-delivery
    provides: deterministic Markdown/Typst/PDF triples and delivery transaction
provides:
  - Fixed 14-gate acceptance registry and caller-owned active-run transaction
  - Independent PDF/PNG reopening observer with A4, font, PNG and stem facts
  - Public verify workdir/resume contract and Phase 48 release prerequisite check
affects: [49-02-runtime-uat, graduate-resume]
tech-stack:
  added: []
  patterns: [literal-gate-registry, caller-owned-evidence-run, producer-observer-arbiter]
key-files:
  created:
    - skills/graduate-resume/scripts/graduate_resume_verify.py
    - skills/graduate-resume/references/phase-49-verification-contract.md
    - skills/graduate-resume/scripts/test_phase49_verify.py
  modified:
    - skills/graduate-resume/scripts/graduate_resume_pdf_gate.py
    - skills/graduate-resume/scripts/graduate_resume_cli.py
key-decisions:
  - "verify 不再使用临时隐式目录；首次运行创建 active-run，续跑必须精确指定 resume ID。"
  - "缺少 runtime/UAT 或其他 gate 证据必须形成失败行，不能减少固定分母或伪造 human_needed。"
  - "Phase 48 review/security 以当前源码 hash 复核，历史 VERIFICATION PASS 不能放行。"
patterns-established:
  - "Acceptance 记录以 required/called 的字面顺序、唯一性和零 dynamic skip 作为完整性条件。"
  - "PDF/PNG observer 只重开交付文件并记录相对文件名与 hash，不读取生产者自报状态。"
requirements-completed: [VERIFY-01, VERIFY-02]
duration: 35min
completed: 2026-07-20
---

# Phase 49 Plan 01: 固定验收注册表与独立产物观察 Summary

**为毕业生简历建立了固定 14-gate、caller-owned active-run 证据事务和重新打开 Markdown/Typst/PDF/PNG 的观察基础。**

## Performance

- **Duration:** 35 min
- **Started:** 2026-07-19T19:54:00Z
- **Completed:** 2026-07-19T20:29:34Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- `verify --workdir` 首次创建唯一 locator/run，之后强制精确 `--resume`，并把 acceptance、raw、artifacts、runtime 和 UAT 限定在 run 内。
- 14 个 gate 的 ID、顺序、called/required equality 和无动态 skip 已由实现、reference 与回归共同锁定；缺失 evidence 会失败关闭。
- 新 PDF/PNG observer 重开最终三件套，复算 A4 尺寸、页数、字体、PNG 边界、hash、主题/照片/target metadata 与正式 stem。
- `P49-G01` 会复核 Phase 48 review/security 状态和报告中登记的每一项源码 hash。

## Task Commits

1. **Task 1: 建立独立 PDF/PNG 重开观察与交叉重算** - `fbadd9f`、`23b6256`
2. **Task 2: 固定 14-gate 聚合、发布前置门与 caller-owned 证据事务** - `23b6256`

## Files Created/Modified

- `skills/graduate-resume/scripts/graduate_resume_verify.py` - 固定 registry、active-run 和 acceptance 结构校验。
- `skills/graduate-resume/scripts/graduate_resume_pdf_gate.py` - 最终交付物的 PDF/PNG 独立观察记录。
- `skills/graduate-resume/scripts/graduate_resume_cli.py` - 公开 `verify --workdir [--resume]` 入口。
- `skills/graduate-resume/scripts/test_phase49_verify.py` - registry、篡改和续跑回归。
- `skills/graduate-resume/references/phase-49-verification-contract.md` - 公开证据、状态和 gate 契约。

## Decisions Made

- 使用显式调用方 workdir，禁止 latest fallback 或跨 run 消费记录。
- 对尚未由 49-02 提供的 six-runtime/UAT evidence 保留失败 gate 行，而不是将其表示为 skip。
- Phase 49 修改了 Phase 48 security scope 内的 CLI，因此 G01 正确将旧 security source hash 视为 stale；最终整合后需重新执行安全核验。

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

Phase 48 现有 security 报告的 CLI hash 在本计划修改公开 verify 入口后必然过期；这是发布前置门正常的 fail-closed 结果，不是以旧报告放行的理由。

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

49-02 可在同一 active run 内写入六 runtime 与人工 UAT 记录，并接入固定 registry。Phase 49 完成后需以当前 source hashes 重新生成/复核 Phase 48 security evidence，才能使 G01 通过。

---
*Phase: 49-runtime*
*Completed: 2026-07-20*
