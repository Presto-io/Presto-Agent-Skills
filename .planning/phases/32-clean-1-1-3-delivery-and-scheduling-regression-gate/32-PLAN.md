---
phase: 32
plan: 01
type: execute
wave: 1
depends_on:
  - phase: 31
files_modified:
  - skills/teaching-design-package/SKILL.md
  - skills/teaching-design-package/references/format-and-orchestration.md
  - skills/teaching-design-package/scripts/teaching-design-package.sh
autonomous: true
requirements: [TDPKG-07, TDPKG-08, TDPKG-09, TDPKG-10, TDPKG-11, TDPKG-12, TDPKG-13]
requirements_addressed: [TDPKG-07, TDPKG-08, TDPKG-09, TDPKG-10, TDPKG-11, TDPKG-12, TDPKG-13]
---

# Phase 32 Plan: Clean 1+1+3 Delivery and Scheduling Regression Gate

<objective>
Enforce the final successful `teaching-design-package` delivery contract: a default successful delivery directory contains exactly one unified Markdown, one unified Typst, and three PDFs, while all package-owned diagnostics, status, stderr logs, split Typst files, temporary state, and failure evidence stay in hidden work/debug/failure locations. The same execution must add hard scheduling validation so total hours, school year, semester, and start/end dates are derived from plan/activity/calendar evidence and cross-checked before an output can be final.
</objective>

<must_haves>
## Locked Truths

- D-01: Default successful delivery directory is public-facing and must contain only 1+1+3 deliverables.
- D-02: The public 1+1+3 filenames are `课程名教学资料.md` or `teaching-design-package-full.md`, `课程名教学资料.typ` or `teaching-design-package.typ`, `课程名教学资料.pdf` or `teaching-design-package.pdf`, `授课进度计划.pdf` or `teaching-plan.pdf`, and `教学设计方案.pdf` or `teaching-design.pdf`.
- D-03: Internal handoff, manifests, status sidecars, stderr logs, split Typst files, temporary state, model JSON, and failure diagnostics must not appear in the default successful delivery directory.
- D-04: Hidden work/debug/failure paths are allowed and required for troubleshooting, for example `.teaching-design-package/work`, `.teaching-design-package/debug`, and `.teaching-design-package/failure-diagnostics`.
- D-05: A failed render must preserve enough diagnostics in hidden/failure locations but must not leave the public directory looking like a successful final delivery.
- D-06: Total hours are computed from teaching-plan rows and/or lesson/activity hour data, never accepted as an authoritative YAML/frontmatter field.
- D-07: Teaching-plan hours and lesson-plan activity hours must mutually verify; mismatches fail validation or mark output non-final/review-needed.
- D-08: `first_teaching_day` derives `school_year` and `semester`; teachers must not maintain those values in YAML.
- D-09: Start and end dates are calculated from actual teaching-day consumption, parsed hours, and documented calendar/default behavior.
- D-10: Do not introduce or accept old precise full handoff filenames anywhere in package docs, scripts, or Phase 32 artifacts.
- D-11: Do not call, copy, install, or use legacy standalone skills as package internals, package resources, implementation shortcuts, or parity baselines.
- D-12: Verification must include a standalone copy containing only `skills/teaching-design-package/`; the default successful delivery directory in that copy must be clean.
- D-13: Phase 32 may modify package docs and package script implementation, but must not modify legacy standalone skill implementation files.
</must_haves>

<tasks>
## Task 1: Define the public delivery directory and hidden work/debug contract

<read_first>
- `AGENTS.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/30-standalone-skill-boundary-and-internalized-dependencies/30-SUMMARY.md`
- `.planning/phases/30-standalone-skill-boundary-and-internalized-dependencies/30-VERIFICATION.md`
- `.planning/phases/31-teacher-facing-unified-markdown-workflow/31-SUMMARY.md`
- `.planning/phases/31-teacher-facing-unified-markdown-workflow/31-VERIFICATION.md`
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
</read_first>

<action>
Update package docs and script behavior so the render contract has two explicit surfaces:

1. public delivery directory: final teacher-facing files only;
2. hidden internal directory under the output root, such as `.teaching-design-package/`, with stable subdirectories for `work`, `debug`, and `failure-diagnostics`.

Move or keep all non-delivery evidence there: `model.json`, status JSON, manifests, stderr logs, temporary Typst used for split PDFs, validator state, and failure diagnostics. Replace any wording that suggests `teaching-design-package-status.json` or split `.typ` files are successful public outputs. Keep status/manifest evidence available under the hidden directory and allow an explicit debug mode or failure path to reveal its location without polluting the public directory.
</action>

<acceptance_criteria>
- `references/format-and-orchestration.md` has a section that distinguishes "public delivery directory" from "hidden work/debug/failure diagnostics".
- `SKILL.md` outputs list describes only the 1+1+3 files as successful public delivery outputs.
- `scripts/teaching-design-package.sh render-package --pdf --input <md> --out-dir <dir>` writes diagnostics/status under `<dir>/.teaching-design-package/`, not as public root files.
- A successful public root `find <dir> -maxdepth 1 -type f -printf '%f\n' | sort` contains exactly five files for the default sample render.
- A successful public root scan finds no `status`, `manifest`, `stderr`, `log`, `model.json`, `split`, `teaching-plan.typ`, or `teaching-design.typ` files at maxdepth 1.
</acceptance_criteria>

## Task 2: Enforce the 1+1+3 naming and success/failure semantics

<read_first>
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
</read_first>

<action>
Make the default successful `render-package --pdf` path produce exactly:

- unified Markdown: `teaching-design-package-full.md` or a course-name mapped `课程名教学资料.md`;
- unified Typst: `teaching-design-package.typ` or a course-name mapped `课程名教学资料.typ`;
- full package PDF: `teaching-design-package.pdf` or `课程名教学资料.pdf`;
- teaching-plan PDF: `teaching-plan.pdf` or `授课进度计划.pdf`;
- teaching-design/lesson-plan PDF: `teaching-design.pdf` or `教学设计方案.pdf`.

If the current script keeps English filenames, document that mapping and make it deterministic. If course-name output is implemented, sanitize the course name once and use it consistently. The command must fail non-zero or write a hidden non-final status when any of the three PDFs cannot be produced; it must not present a public directory with partial root files as a successful delivery. Preserve hidden diagnostic evidence for failure.
</action>

<acceptance_criteria>
- The script has one deterministic output-name mapping for the five public deliverables.
- `render-package --pdf` cannot exit 0 as a final successful delivery unless all three expected PDF files exist and are non-empty.
- If PDF tooling fails, root-level public files do not masquerade as a complete final delivery; hidden status records the failure and the command exits non-zero or clearly marks non-final.
- Hidden split Typst files may exist only under `.teaching-design-package/work` or equivalent hidden subdirectory.
- Documentation names both the preferred Chinese teacher-facing names and the current English script filenames if the script keeps English defaults.
</acceptance_criteria>

## Task 3: Add strict derived scheduling validation

<read_first>
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `.planning/REQUIREMENTS.md`
</read_first>

<action>
Harden model validation around scheduling:

- reject frontmatter keys that try to own derived facts: `total_hours`, `school_year`, `semester`, `start_date`, `end_date`, `date_range`, `outputs`, `validation`, or internal calendar/status fields;
- compute total course hours from schedule/activity rows;
- parse lesson-plan activity hours from the teaching-design body when present, and compare them with teaching-plan row totals;
- fail validation or set hidden status to non-final/review-needed when teaching-plan hours and lesson/activity hours mismatch;
- infer `school_year` and `semester` from `first_teaching_day`;
- compute start/end dates from the real teaching-day consumption algorithm, parsed hours, and documented default calendar behavior.

If full holiday/makeup-day support is not implemented in this phase, document the default calendar behavior exactly and add a hidden model field that makes the default explicit, such as `calendar_policy: "sequential_teaching_days_default"` or equivalent. Do not rely on YAML-provided totals or dates.
</action>

<acceptance_criteria>
- `scripts/teaching-design-package.sh model --input <sample>` emits JSON where `.derived.total_hours`, `.derived.school_year`, `.derived.semester`, `.derived.start_date`, `.derived.end_date`, and `.derived.date_range` are computed.
- Adding `total_hours:` or `school_year:` to the sample frontmatter makes `model` fail with a message that derived frontmatter fields are not allowed.
- A fixture or temporary edited Markdown with mismatched teaching-plan hours versus teaching-design activity hours makes validation fail or produce hidden status with `final_ready: false` and a mismatch reason.
- A sample with `first_teaching_day: "2026-05-11"` derives `2025-2026学年` and `第二学期`.
- A sample with an autumn `first_teaching_day`, for example `2026-09-01`, derives `2026-2027学年` and `第一学期`.
- Start/end dates in the hidden model are derived from hour consumption, not copied from YAML.
</acceptance_criteria>

## Task 4: Remove old split compatibility leakage from successful defaults

<read_first>
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
</read_first>

<action>
Audit and revise package docs and normal script behavior so Phase 32 cannot regress into the pre-v1.14 split handoff strategy. Compatibility aliases such as `plan-split` or `render-split`, if kept, must route to the package-owned unified path and must not expose old handoff filenames, old package-internal skill names, or split artifacts in the successful default delivery root. Do not call or copy legacy standalone skill folders.
</action>

<acceptance_criteria>
- A dynamic old precise full handoff filename scan over `skills/teaching-design-package` and this Phase 32 directory returns no matches.
- A dynamic legacy standalone dependency scan over `skills/teaching-design-package/scripts/teaching-design-package.sh` returns no normal-path dependency matches.
- `git diff --name-only -- <legacy-plan-skill-path> <legacy-design-skill-path> <legacy-optional-module-path>` is empty after execution.
- No default successful public output root contains `teaching-plan.typ`, `teaching-design.typ`, old full Markdown names, `manifest`, `status`, `stderr`, or `log` root files.
</acceptance_criteria>

## Task 5: Build standalone-copy regression verification for clean delivery

<read_first>
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `.planning/phases/30-standalone-skill-boundary-and-internalized-dependencies/30-VERIFICATION.md`
- `.planning/phases/31-teacher-facing-unified-markdown-workflow/31-VERIFICATION.md`
</read_first>

<action>
Verify the final Phase 32 behavior from a standalone copy that installs only `teaching-design-package`. The verification must copy only `skills/teaching-design-package/` to a temporary skill root, run `example`, run `render-package --pdf`, assert the public directory is clean, inspect hidden diagnostics, assert derived scheduling fields, and scan for old precise handoff names and sibling-skill dependencies. Record exact command outputs and temp-root paths in `32-VERIFICATION.md` during execute-phase.
</action>

<acceptance_criteria>
- Standalone verification copies only `skills/teaching-design-package/` and does not copy any legacy standalone skill folder.
- In the standalone copy, `example --output <tmp>/课程名教学资料.md` or `example --output <tmp>/teaching-design-package-full.md` succeeds.
- In the standalone copy, `render-package --pdf --input <md> --out-dir <delivery>` succeeds only when all three PDFs are actually produced.
- `find <delivery> -maxdepth 1 -type f -printf '%f\n' | sort` matches the expected five-file list exactly.
- `find <delivery> -maxdepth 1 -type f | rg 'status|manifest|stderr|log|model|split|teaching-plan[.]typ|teaching-design[.]typ'` has no matches.
- `test -f <delivery>/.teaching-design-package/model.json` and hidden status/diagnostic checks pass.
- Derived scheduling JSON assertions pass for total hours, school year, semester, start date, end date, and date range.
</acceptance_criteria>

## Task 6: Record Phase 32 evidence and planning-state boundaries

<read_first>
- `.planning/phases/32-clean-1-1-3-delivery-and-scheduling-regression-gate/32-PLAN.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/REQUIREMENTS.md`
</read_first>

<action>
During execute-phase only, create `32-VERIFICATION.md` and `32-SUMMARY.md` that record implementation commits, exact verification commands, public directory file lists, hidden diagnostic file lists, scheduling assertion results, standalone-copy evidence, and legacy-boundary scans. Do not mark Phase 32 complete unless the verification proves TDPKG-07 through TDPKG-13. Do not audit or complete the milestone as part of Phase 32 execution unless the user separately requests that workflow.
</action>

<acceptance_criteria>
- `32-VERIFICATION.md` records the standalone-copy command sequence and marks status `passed` only if all required assertions pass.
- `32-SUMMARY.md` lists `requirements-completed: [TDPKG-07, TDPKG-08, TDPKG-09, TDPKG-10, TDPKG-11, TDPKG-12, TDPKG-13]` only after successful execution verification.
- Phase 32 execution does not modify legacy standalone skill folders.
- Phase 32 execution does not run `/gsd:audit-milestone` or `/gsd:complete-milestone`.
</acceptance_criteria>
</tasks>

<verification>
Run these checks after implementation. Keep exact stdout/stderr evidence in `32-VERIFICATION.md`.

```bash
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh

tmp_root="$(mktemp -d "${TMPDIR:-/tmp}/tdpkg-phase32-standalone.XXXXXX")"
mkdir -p "$tmp_root/skills"
cp -R skills/teaching-design-package "$tmp_root/skills/"

"$tmp_root/skills/teaching-design-package/scripts/teaching-design-package.sh" example \
  --output "$tmp_root/课程名教学资料.md"

"$tmp_root/skills/teaching-design-package/scripts/teaching-design-package.sh" render-package \
  --pdf \
  --input "$tmp_root/课程名教学资料.md" \
  --out-dir "$tmp_root/delivery"

find "$tmp_root/delivery" -maxdepth 1 -type f -printf '%f\n' | sort

expected_files="$tmp_root/expected-files.txt"
cat > "$expected_files" <<'EOF'
teaching-design-package-full.md
teaching-design-package.pdf
teaching-design-package.typ
teaching-design.pdf
teaching-plan.pdf
EOF
find "$tmp_root/delivery" -maxdepth 1 -type f -printf '%f\n' | sort | diff -u "$expected_files" -

! find "$tmp_root/delivery" -maxdepth 1 -type f -printf '%f\n' |
  rg 'status|manifest|stderr|log|model|split|teaching-plan[.]typ|teaching-design[.]typ'

test -f "$tmp_root/delivery/.teaching-design-package/model.json"
test -f "$tmp_root/delivery/.teaching-design-package/status.json"
find "$tmp_root/delivery/.teaching-design-package" -type f -printf '%P\n' | sort

node -e '
const fs = require("fs");
const model = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
if (model.derived.total_hours <= 0) throw new Error("total_hours not derived");
if (model.derived.school_year !== "2025-2026学年") throw new Error(model.derived.school_year);
if (model.derived.semester !== "第二学期") throw new Error(model.derived.semester);
if (!model.derived.start_date || !model.derived.end_date || !model.derived.date_range) throw new Error("missing derived dates");
' "$tmp_root/delivery/.teaching-design-package/model.json"

frontmatter_fail="$tmp_root/derived-frontmatter.md"
cp "$tmp_root/课程名教学资料.md" "$frontmatter_fail"
perl -0pi -e 's/^---\n/---\ntotal_hours: 999\nschool_year: "2099-2100学年"\n/s' "$frontmatter_fail"
! "$tmp_root/skills/teaching-design-package/scripts/teaching-design-package.sh" model \
  --input "$frontmatter_fail"

autumn_sample="$tmp_root/autumn.md"
cp "$tmp_root/课程名教学资料.md" "$autumn_sample"
perl -0pi -e 's/first_teaching_day: "2026-05-11"/first_teaching_day: "2026-09-01"/' "$autumn_sample"
"$tmp_root/skills/teaching-design-package/scripts/teaching-design-package.sh" model \
  --input "$autumn_sample" \
  --out-dir "$tmp_root/autumn-model"
node -e '
const fs = require("fs");
const model = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
if (model.derived.school_year !== "2026-2027学年") throw new Error(model.derived.school_year);
if (model.derived.semester !== "第一学期") throw new Error(model.derived.semester);
' "$tmp_root/autumn-model/.teaching-design-package/model.json"

old_full_pattern="$(printf '%s|%s|%s|%s' \
  "$(printf '%s-%s-%s[.]%s' 'jiaoan' 'jihua' 'full' 'md')" \
  "$(printf '%s-%s-%s[.]%s' 'jiaoan' 'shicao' 'full' 'md')" \
  "$(printf '%s-%s-%s[.]%s' 'teaching' 'plan' 'full' 'md')" \
  "$(printf '%s-%s-%s[.]%s' 'lesson' 'plan' 'full' 'md')")"
! rg "$old_full_pattern" \
  skills/teaching-design-package \
  .planning/phases/32-clean-1-1-3-delivery-and-scheduling-regression-gate

legacy_dependency_pattern="$(printf '%s|%s|%s|%s' \
  "$(printf '%s/%s' 'skills' 'jiaoan')" \
  "$(printf '%s%s/%s' '[.]' '[.]' 'jiaoan')" \
  "$(printf '%s-%s' 'jiaoan' 'jihua')" \
  "$(printf '%s-%s' 'jiaoan' 'shicao')")"
! rg "$legacy_dependency_pattern" \
  "$tmp_root/delivery" \
  "$tmp_root/skills/teaching-design-package/scripts/teaching-design-package.sh"

git diff --name-only -- <legacy-plan-skill-path> <legacy-design-skill-path> <legacy-optional-module-path>
git diff --check
git diff --cached --check
```

For the dynamic old precise handoff scan, the expected result is no matches. For the legacy diff check, substitute the three existing legacy skill paths and expect empty output.
</verification>

<success_criteria>
- Successful default delivery root contains exactly one unified Markdown, one unified Typst, and three PDFs.
- Status, manifest, model, stderr logs, split Typst files, temporary state, and failure diagnostics are hidden under package-owned work/debug/failure paths.
- Failures preserve diagnostics without pretending public delivery succeeded.
- Total hours, school year, semester, start date, end date, and date range are derived from schedule/activity evidence and `first_teaching_day`.
- Teaching-plan hours and lesson-plan activity hours are cross-checked, with mismatches failing validation or marking output non-final/review-needed.
- Old precise full handoff filenames and legacy standalone skill calls do not re-enter package docs, script normal paths, generated outputs, or Phase 32 evidence.
- A standalone copy containing only `teaching-design-package` verifies the clean delivery directory and scheduling assertions.
</success_criteria>

<threat_model>
This phase touches the package's user-facing delivery contract and validation behavior.

- Public artifact pollution: internal status/log/model files may remain in the public root. Mitigation: root-level `find`/`rg` assertions must fail if non-delivery files appear.
- False finality: a failed PDF compile could leave partial files and exit success. Mitigation: final success requires all three PDFs to exist and non-final/failure status must be hidden and explicit.
- Scheduling trust bug: YAML-provided totals or dates could override body evidence. Mitigation: derived frontmatter keys are rejected and model assertions check computed fields.
- Cross-document mismatch: teaching-plan hours and lesson-plan activity hours could diverge. Mitigation: validation must compare them and block final readiness on mismatch.
- Old workflow regression: old full handoff names or legacy skill calls could return through compatibility aliases. Mitigation: old-name scans and standalone-copy verification must pass, and legacy skill diffs must remain empty.
</threat_model>
