---
phase: 32
plan: 01
status: passed
verified: 2026-06-15T02:29:11Z
---

# Phase 32 Verification

## Result

PASSED. `teaching-design-package` now verifies from a standalone copy containing only `skills/teaching-design-package/`.

Standalone root:

```text
/private/tmp/tdpkg-phase32-standalone.boi89n
```

## Required Command Evidence

| Check | Result |
|-------|--------|
| `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh` | PASS |
| Copy only `skills/teaching-design-package/` to temporary standalone skill root | PASS |
| Standalone `example --output /private/tmp/tdpkg-phase32-standalone.boi89n/课程名教学资料.md` | PASS |
| Standalone `render-package --pdf --input ... --out-dir .../delivery` | PASS; all three PDFs exist and are non-empty |
| Public root exact five-file assertion | PASS |
| Public root pollution scan | PASS; no `status`, `manifest`, `stderr`, `log`, `model`, `split`, `teaching-plan.typ`, or `teaching-design.typ` root files |
| Hidden model/status/diagnostics checks | PASS |
| Derived JSON assertions | PASS |
| Derived frontmatter injection rejection | PASS |
| Autumn first teaching day inference | PASS |
| Activity-hour mismatch rejection | PASS |
| Dynamic old precise name scan | PASS |
| Legacy dependency scan | PASS |
| Legacy skill diff | PASS; empty |
| `git diff --check` and `git diff --cached --check` | PASS |

## Public Delivery Root

The successful delivery root contained exactly:

```text
teaching-design-package-full.md
teaching-design-package.pdf
teaching-design-package.typ
teaching-design.pdf
teaching-plan.pdf
```

The plan's GNU `find -printf` command was also attempted on this macOS host and failed with:

```text
find: -printf: unknown primary or operator
```

Because GNU `find`/`gfind` is not installed here, the actual assertion used the portable equivalent:

```bash
find "$delivery" -maxdepth 1 -type f -exec basename {} \; | sort
```

That portable list matched the required five-file set exactly.

## Hidden Diagnostics

Hidden files under `.teaching-design-package/`:

```text
debug/design-pdf.stderr.log
debug/full-pdf.stderr.log
debug/plan-pdf.stderr.log
diagnostics.json
model.json
status.json
work/teaching-design.typ
work/teaching-plan.typ
```

The public root contains none of these diagnostics.

## Scheduling Assertions

`model.json` derived:

```json
{
  "total_hours": 160,
  "total_hours_label": "160H",
  "daily_hours": 8,
  "calendar_policy": "sequential_teaching_days_default",
  "school_year": "2025-2026学年",
  "semester": "第二学期",
  "term_label": "2025-2026学年第二学期",
  "start_date": "2026-05-11",
  "end_date": "2026-05-30",
  "date_range": "5月11日--5月30日"
}
```

Derived frontmatter injection failed as required:

```text
teaching-design-package.sh: package frontmatter must not own derived fields: total_hours, school_year
```

Autumn first teaching day inference passed:

```text
2026-2027学年 第一学期
```

Teaching-plan/activity-hour mismatch failed as required:

```text
teaching-design-package.sh: teaching-plan total hours (160) and teaching-design activity hours (999) mismatch
```

## Legacy Boundary

Dynamic old precise full-name scan over `skills/teaching-design-package` and this Phase 32 directory returned no matches.

Legacy dependency scan over the standalone delivery and copied package script returned no normal-path matches.

Legacy skill diff command:

```bash
git diff --name-only -- skills/jiaoan-jihua skills/jiaoan-shicao skills/end-of-term-teaching-materials
```

Output was empty.

## Self-Check

All Phase 32 plan acceptance criteria were verified. No old standalone skill directory was modified, and no audit/complete/push workflow was run.
