---
phase: 11-end-of-term-data-and-markdown-contract
plan: 01
subsystem: end-of-term-teaching-materials
tags:
  - skill
  - markdown-contract
  - teaching-materials
requires:
  - 04-markdown-normalization-contract
provides:
  - skills/end-of-term-teaching-materials/SKILL.md
  - skills/end-of-term-teaching-materials/references/data-contract.md
  - skills/end-of-term-teaching-materials/templates/end-of-term-full.md
affects:
  - README.md
  - skills/README.md
  - .planning/REQUIREMENTS.md
  - .planning/ROADMAP.md
  - .planning/STATE.md
tech-stack:
  added: []
  patterns:
    - canonical SKILL.md
    - YAML frontmatter + body Markdown intermediate
    - skill-local references and templates
key-files:
  created:
    - skills/end-of-term-teaching-materials/SKILL.md
    - skills/end-of-term-teaching-materials/references/data-contract.md
    - skills/end-of-term-teaching-materials/templates/end-of-term-full.md
  modified:
    - README.md
    - skills/README.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md
key-decisions:
  - Keep Phase 11 contract-only: no scripts, OCR, Excel, Typst, PDF, or deterministic table artifact implementation.
  - Treat `end-of-term-full.md` as the durable teacher-editable source of truth before rendering.
  - Use inline uncertainty values such as `87?` plus `## 复核标记` rows to block final export readiness until review is cleared.
requirements-completed:
  - ETM-01
  - ETM-02
  - ETM-03
  - ETM-04
duration: 24 min
completed: 2026-06-08T23:59:42Z
---

# Phase 11 Plan 01: End-of-Term Data and Markdown Contract Summary

Phase 11 added the contract layer for the `end-of-term-teaching-materials` skill: a canonical skill file, a structured data contract, and a reusable Markdown intermediate template.

## Execution

- Created `skills/end-of-term-teaching-materials/SKILL.md` with trigger conditions, source-data expectations, review-before-export behavior, verification, safety boundaries, and adapter notes for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
- Created `skills/end-of-term-teaching-materials/references/data-contract.md` covering required metadata, optional handover fields, package flags, roster entries, task/hour records, score data, uncertainty markers, analysis sections, and submission metadata.
- Created `skills/end-of-term-teaching-materials/templates/end-of-term-full.md` as one reviewable Markdown package with YAML frontmatter, task list, score table, analysis sections, an uncertain `87?` value, a blank score cell, and a matching review marker.
- Updated `README.md` and `skills/README.md` so contributors can discover the new skill without confusing Phase 11 contract work with Phase 12 rendering.
- Updated `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, and `.planning/STATE.md` to mark ETM-01 through ETM-04 complete and leave ETM-05 through ETM-08 planned for Phase 12.

## Commits

- `0238516 feat(11-01): add end-of-term contract skill`

## Verification

Passed:

```bash
test -f skills/end-of-term-teaching-materials/SKILL.md
test -f skills/end-of-term-teaching-materials/references/data-contract.md
test -f skills/end-of-term-teaching-materials/templates/end-of-term-full.md
for runtime in "Codex" "Claude Code" "Gemini CLI" "OpenCode" "OpenClaw" "Hermes Agent"; do rg -n "$runtime" skills/end-of-term-teaching-materials/SKILL.md; done
for field in template date school_year semester major_name course_name class_name teachers handover_class_name handover_teachers package; do rg -n "$field" skills/end-of-term-teaching-materials/references/data-contract.md; done
for artifact in 成绩记分册 成绩汇总表 成绩分析表 教学日志封面 过程考核评价表封面 交接班记录封面; do rg -n "$artifact" skills/end-of-term-teaching-materials/references/data-contract.md skills/end-of-term-teaching-materials/templates/end-of-term-full.md; done
for heading in "## 我带的学生" "## 过程考核任务" "## 成绩数据" "## 分析" "## 复核标记"; do rg -n "$heading" skills/end-of-term-teaching-materials/templates/end-of-term-full.md; done
for marker in "87\\?" "复核标记" "无"; do rg -n "$marker" skills/end-of-term-teaching-materials/SKILL.md skills/end-of-term-teaching-materials/references/data-contract.md skills/end-of-term-teaching-materials/templates/end-of-term-full.md; done
if rg -n "sources:|平时分|期末分|学期成绩" skills/end-of-term-teaching-materials; then echo "Unexpected source or derived field found" >&2; exit 1; fi
git diff --check
```

Manual review passed:

- Markdown tables in `end-of-term-full.md` are padded and aligned for teacher editing.
- The skill directory contains only `SKILL.md`, `references/data-contract.md`, and `templates/end-of-term-full.md`.
- Phase 11 does not provide render scripts or claim Excel, Typst, PDF, or deterministic table artifact output is complete.

## Deviations from Plan

**[Rule 2 - Verification conflict] Avoid literal forbidden derived-field names in data contract** — Found during: plan verification | Issue: the plan asked the data contract to document excluded derived score fields, while the final verification command rejected those literal field names anywhere under `skills/end-of-term-teaching-materials` | Fix: described them generically as derived calculation fields so the contract still blocks them and the final grep gate remains strict | Files modified: `skills/end-of-term-teaching-materials/references/data-contract.md` | Verification: final Phase 11 command suite passed | Commit hash: `0238516`.

**Total deviations:** 1 auto-fixed. **Impact:** No scope expansion; the stricter verification remains enforceable.

## Issues Encountered

None.

## Self-Check: PASSED

Key files exist, Phase 11 verification passed, ETM-01 through ETM-04 are complete, and Phase 12 remains responsible for rendering and deterministic output artifacts.

## Next

Phase complete, ready for Phase 12 planning.
