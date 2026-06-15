---
phase: 33
plan: 01
status: passed
verified_at: "2026-06-15T06:21:48Z"
commit: 541b74d
requirements: [TDPKG-MOD-01, TDPKG-MOD-02, TDPKG-MOD-03, TDPKG-MOD-04, TDPKG-MOD-05, TDPKG-MOD-06, TDPKG-MOD-07, TDPKG-YAML-01, TDPKG-YAML-02, TDPKG-YAML-03, TDPKG-YAML-04, TDPKG-SCHED-01, TDPKG-SCHED-02, TDPKG-SCHED-03, TDPKG-SCHED-04, TDPKG-SCHED-05]
---

# Phase 33 Verification

## Result

Passed. Phase 33 implementation covers module registry, unified Markdown extraction, skill-local calendar scheduling, YAML conversion, hidden module Markdown/Typst, standalone-copy behavior, and classified diagnostics.

## Requirement Coverage

This table maps the Phase 33 requirement IDs to the existing verification evidence in this file. No new execution results are claimed here; each row references an already-recorded command, output highlight, or check section.

| Requirement | Evidence in this verification |
|-------------|-------------------------------|
| TDPKG-MOD-01 | `example --output /tmp/tdpkg-phase33-example.md` and `model --input /tmp/tdpkg-phase33-example.md` in Commands Run verify the unified Markdown template as the model input. |
| TDPKG-MOD-02 | Commands Run and Hidden Artifact Checks verify the unified Markdown is parsed into model data and hidden module artifacts without adding a teacher confirmation gate. |
| TDPKG-MOD-03 | Model assertions show `total_hours: 160`, `use_time: 5月11日--6月5日`, and `first parsed row source: task:1/stage:1/row:1`; failure diagnostics also reject malformed schedule rows. |
| TDPKG-MOD-04 | Model assertions show `registry: teaching-plan, teaching-design`, and Hidden Artifact Checks verify both registered modules are generated. |
| TDPKG-MOD-05 | Hidden Artifact Checks verify `.teaching-design-package/work/teaching-plan.md` and `.teaching-design-package/work/teaching-design.md`. |
| TDPKG-MOD-06 | Hidden Artifact Checks verify `.teaching-design-package/work/teaching-plan.typ` and `.teaching-design-package/work/teaching-design.typ`. |
| TDPKG-MOD-07 | Commands Run route through `scripts/package-model.js`, model assertions show registered module IDs, and Scope Exclusion Checks verify the package model boundary does not call legacy sibling skills. |
| TDPKG-YAML-01 | Commands Run generate the example package and model from unified Markdown YAML; model assertions verify accepted fields such as teacher, calendar policy, total hours, use time, and module IDs. |
| TDPKG-YAML-02 | Hidden Artifact Checks verify `teaching-plan.md` frontmatter includes `template: "jiaoan-jihua"` and shared schedule-derived fields. |
| TDPKG-YAML-03 | Hidden Artifact Checks verify `teaching-design.md` frontmatter includes `template: "jiaoan-shicao"`, `total_hours: 160`, and `use_time: "5月11日--6月5日"`. |
| TDPKG-YAML-04 | Model assertions verify teacher-name conversion and schedule-derived `total_hours`/`use_time`; hidden module frontmatter verifies those derived values are written to module Markdown. |
| TDPKG-SCHED-01 | Standalone Copy Check verifies a copied `skills/teaching-design-package` folder uses its own `references/calendar.json` and does not read sibling skill paths. |
| TDPKG-SCHED-02 | Failure Diagnostics Checks verify `first_day_not_found` and `calendar_exhausted` failures when the first teaching day or calendar range is invalid. |
| TDPKG-SCHED-03 | Model assertions verify the skill-local calendar hash, `total_hours`, `use_time`, and first parsed row source derived from schedule rows and calendar data. |
| TDPKG-SCHED-04 | Model assertions verify `calendar.policy: skill_local_calendar`; Scope Exclusion Checks verify the package uses `references/calendar.json` and does not depend on legacy sequential-day behavior. |
| TDPKG-SCHED-05 | Hidden Artifact Checks verify hidden `model.json`, `status.json`, and `diagnostics.json`; model assertions verify calendar hash and derived scheduling summary. |

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

Additional failure diagnostics were verified in a temporary standalone copy:

```bash
# Missing # 授课进度计划
! "$standalone/skills/teaching-design-package/scripts/teaching-design-package.sh" model --input "$missing_section"

# Invalid calendar JSON
printf '{bad json' > "$standalone/skills/teaching-design-package/references/calendar.json"
! "$standalone/skills/teaching-design-package/scripts/teaching-design-package.sh" model --input "$package"

# Calendar exhaustion
printf '["2026-05-11"]\n' > "$standalone/skills/teaching-design-package/references/calendar.json"
! "$standalone/skills/teaching-design-package/scripts/teaching-design-package.sh" model --input "$package"
```

Observed diagnostics:

```text
missing_section: missing # 授课进度计划
invalid_calendar_json: calendar is not valid JSON
calendar_exhausted: calendar ended before all row hours were assigned
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
