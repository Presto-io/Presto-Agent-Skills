---
phase: 33
plan: 01
status: passed
verified_at: "2026-06-15T06:21:48Z"
commit: 541b74d
---

# Phase 33 Verification

## Result

Passed. Phase 33 implementation covers module registry, unified Markdown extraction, skill-local calendar scheduling, YAML conversion, hidden module Markdown/Typst, standalone-copy behavior, and classified diagnostics.

## Commands Run

```bash
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh
node --check skills/teaching-design-package/scripts/package-model.js

skills/teaching-design-package/scripts/teaching-design-package.sh info
skills/teaching-design-package/scripts/teaching-design-package.sh version
skills/teaching-design-package/scripts/teaching-design-package.sh example --output /tmp/tdpkg-phase33-example.md
skills/teaching-design-package/scripts/teaching-design-package.sh model --input /tmp/tdpkg-phase33-example.md > /tmp/tdpkg-phase33-model.json
```

Output highlights:

```text
teaching-design-package: standalone unified Markdown to package-owned module registry and shared scheduling model.
Calendar: references/calendar.json
teaching-design-package.sh 0.4.0-phase33
```

Model assertions passed:

```text
registry: teaching-plan, teaching-design
teacher_name: 张老师
calendar.policy: skill_local_calendar
calendar.sha256: 0bcb96b4ca7d452831cc20b56b4a82a60f239c5c75137b0f6f182ee8b79664bb
total_hours: 160
use_time: 5月11日--6月5日
first parsed row source: task:1/stage:1/row:1
```

## Hidden Artifact Checks

```bash
tmp_root="$(mktemp -d "${TMPDIR:-/tmp}/tdpkg-phase33.XXXXXX")"
skills/teaching-design-package/scripts/teaching-design-package.sh render-package \
  --input /tmp/tdpkg-phase33-example.md \
  --out-dir "$tmp_root/out"

test -f "$tmp_root/out/.teaching-design-package/model.json"
test -f "$tmp_root/out/.teaching-design-package/status.json"
test -f "$tmp_root/out/.teaching-design-package/diagnostics.json"
test -f "$tmp_root/out/.teaching-design-package/work/teaching-plan.md"
test -f "$tmp_root/out/.teaching-design-package/work/teaching-design.md"
test -f "$tmp_root/out/.teaching-design-package/work/teaching-plan.typ"
test -f "$tmp_root/out/.teaching-design-package/work/teaching-design.typ"

rg 'template: "jiaoan-jihua"' "$tmp_root/out/.teaching-design-package/work/teaching-plan.md"
rg 'template: "jiaoan-shicao"' "$tmp_root/out/.teaching-design-package/work/teaching-design.md"
rg 'total_hours:' "$tmp_root/out/.teaching-design-package/work/teaching-design.md"
rg 'use_time:' "$tmp_root/out/.teaching-design-package/work/teaching-design.md"

! find "$tmp_root/out" -maxdepth 1 -type f -print |
  rg 'teaching-plan[.]md|teaching-design[.]md|teaching-plan[.]typ|teaching-design[.]typ|calendar[.]json|model[.]json|status[.]json|diagnostics[.]json|log'
```

Observed hidden module frontmatter:

```text
template: "jiaoan-jihua"
template: "jiaoan-shicao"
total_hours: 160
use_time: "5月11日--6月5日"
```

The public-root leakage assertion passed.

## Failure Diagnostics Checks

```bash
derived_fail="$tmp_root/derived-frontmatter.md"
cp /tmp/tdpkg-phase33-example.md "$derived_fail"
perl -0pi -e 's/^---\n/---\ndaily_hours: 8\ntotal_hours: 999\n/s' "$derived_fail"
! skills/teaching-design-package/scripts/teaching-design-package.sh model --input "$derived_fail"
```

Observed diagnostic:

```text
forbidden_derived_frontmatter
```

```bash
bad_first_day="$tmp_root/bad-first-day.md"
cp /tmp/tdpkg-phase33-example.md "$bad_first_day"
perl -0pi -e 's/first_teaching_day: "2026-05-11"/first_teaching_day: "2099-01-01"/' "$bad_first_day"
! skills/teaching-design-package/scripts/teaching-design-package.sh model --input "$bad_first_day"
```

Observed diagnostic:

```text
first_day_not_found
first_teaching_day not found in calendar: 2099-01-01
```

```bash
malformed_row="$tmp_root/malformed-row.md"
cp /tmp/tdpkg-phase33-example.md "$malformed_row"
perl -0pi -e 's/安技教育-1/安技教育/' "$malformed_row"
! skills/teaching-design-package/scripts/teaching-design-package.sh model --input "$malformed_row"
```

Observed diagnostic:

```text
malformed_schedule_row
malformed row hours, expected text-N: 安技教育
```

## Standalone Copy Check

```bash
standalone_root="$(mktemp -d "${TMPDIR:-/tmp}/tdpkg-phase33-standalone.XXXXXX")"
mkdir -p "$standalone_root/skills"
cp -R skills/teaching-design-package "$standalone_root/skills/"
"$standalone_root/skills/teaching-design-package/scripts/teaching-design-package.sh" example \
  --output "$standalone_root/package.md"
"$standalone_root/skills/teaching-design-package/scripts/teaching-design-package.sh" model \
  --input "$standalone_root/package.md" \
  > "$standalone_root/model.json"
rg 'skills/teaching-design-package/references/calendar[.]json|references/calendar[.]json' "$standalone_root/model.json"
! rg 'skills/jiaoan-jihua|skills/jiaoan-shicao|sequential_teaching_days_default' "$standalone_root/model.json"
```

Passed. The copied skill used its own `references/calendar.json` and did not read sibling skill paths.

## Scope Exclusion Checks

```bash
rg 'teaching-design-package/references/calendar[.]json|references/calendar[.]json' \
  skills/teaching-design-package/scripts/teaching-design-package.sh \
  skills/teaching-design-package/scripts/package-model.js \
  skills/teaching-design-package/references/format-and-orchestration.md

! rg 'skills/jiaoan-jihua|skills/jiaoan-shicao' \
  skills/teaching-design-package/scripts/teaching-design-package.sh \
  skills/teaching-design-package/scripts/package-model.js

git diff --name-only -- skills/jiaoan-jihua skills/jiaoan-shicao
```

Passed. No `skills/jiaoan-jihua/` or `skills/jiaoan-shicao/` modifications were made.

## Whitespace Checks

```bash
git diff --check
git diff --cached --check
```

Passed.

## Phase 33 Scope Note

Phase 33 intentionally did not migrate the formal `jiaoan-jihua` renderer, did not migrate the formal `jiaoan-shicao` renderer, did not finalize course-name-prefixed public delivery, and did not implement final PDF merge semantics. Those remain Phase 34, Phase 35, and Phase 36 scope.
