---
phase: 22
plan: 01
name: scheduling-contract-and-fixture
type: execute
wave: 1
depends_on: []
files_modified:
  - references/scheduling-contract.md
  - test/1.11/scheduling-contract/fixture-source.md
  - test/1.11/scheduling-contract/expected-schedule.json
  - test/1.11/scheduling-contract/expected-schedule.md
  - scripts/derive-scheduling-fixture.py
  - README.md
  - docs/directory-spec.md
autonomous: true
requirements:
  - TDP-01
  - TDP-02
  - TDP-03
  - TDP-04
must_haves:
  truths:
    - D-01 shared scheduling contract is package-level and must not expose jiaoan-jihua renderer internals as the public API.
    - D-02 required inputs include school calendar dates, first teaching day, daily hours, item hours, holidays, and makeup teaching days.
    - D-03 ordered tasks, activities, and lesson fragments are consumed in source order.
    - D-04 each scheduled item outputs start date, end date, term week evidence, weekday evidence, assigned hours, and hour-consumption evidence.
    - D-05 evidence is both teacher-reviewable Markdown and deterministic structured fixture data.
    - D-06 term week semantics follow the first calendar teaching date's week start, not ISO week numbers.
    - D-07 uncertain scheduling inputs become explicit review markers near affected items.
    - D-08 invalid first_teaching_day, daily_hours, item hours, or insufficient calendar capacity must fail or mark review-needed.
    - D-09 holidays and makeup teaching days are normalized in the calendar/evidence layer.
    - D-10 the fixture reuses the v1.10 teaching-plan source shape where possible.
    - D-11 the fixture proves date-range derivation from contract data, not old renderer output.
    - D-12 full package Markdown, split PDFs, combined PDFs, and end-of-term outputs remain deferred.
---

<objective>
Define and verify a shared scheduling contract plus deterministic fixture evidence for Phase 22. The outcome should let Phase 23 compose scheduling behavior into a future integrated teaching-design package without changing existing `jiaoan-jihua` or `jiaoan-shicao` public command surfaces.
</objective>

<threat_model>
This phase does not process credentials, network requests, or production data. Main risks are integrity risks: silently inventing dates, copying fixture target output instead of deriving evidence, or changing existing public skill behavior while planning a shared contract. Block these by keeping fixture derivation local and deterministic, documenting review markers for uncertain inputs, and verifying that existing skill command surfaces remain unchanged.
</threat_model>

<tasks>

<task id="01" type="execute">
<title>Create the shared scheduling contract reference</title>
<read_first>
- references/scheduling-contract.md if it already exists
- .planning/phases/22-scheduling-contract-and-fixture/22-CONTEXT.md
- .planning/phases/22-scheduling-contract-and-fixture/22-RESEARCH.md
- .planning/REQUIREMENTS.md
- skills/jiaoan-jihua/references/format-and-rendering.md
- skills/jiaoan-jihua/scripts/jiaoan-jihua.sh
- skills/jiaoan-jihua/references/calendar.json
- skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md
</read_first>
<action>
Add `references/scheduling-contract.md` as the package-level scheduling contract. It must define contract inputs `calendar.dates`, `calendar.holidays`, `calendar.makeup_days`, `first_teaching_day`, `daily_hours`, and ordered `items[]` with `source`, `kind`, `title`, `hours`, and stable source pointers. It must define derived outputs `start_date`, `end_date`, `term_week` or `term_week_range`, `weekday` or `weekday_range`, `assigned_hours`, `hour_consumption[]`, and `review_markers[]`. It must explicitly state that source items are consumed in source order, term weeks are derived from the first calendar teaching date's week start, and holidays/makeup days are normalized into the calendar/evidence layer. Include Chinese review terms `学习任务`, `学习环节`, `教学内容`, `学时`, `周次`, `星期`, and `复核标记` where they clarify the teacher-facing Markdown evidence.
</action>
<acceptance_criteria>
- `references/scheduling-contract.md` contains `TDP-01`, `TDP-02`, `TDP-03`, and `TDP-04`.
- `references/scheduling-contract.md` contains the exact identifiers `calendar.dates`, `calendar.holidays`, `calendar.makeup_days`, `first_teaching_day`, `daily_hours`, `items[]`, `hour_consumption[]`, and `review_markers[]`.
- `references/scheduling-contract.md` states that term weeks are not ISO week numbers.
- `references/scheduling-contract.md` states that uncertain, missing, or conflicting schedule inputs become `## 复核标记` entries or item-local review markers.
- `references/scheduling-contract.md` states that existing `jiaoan-jihua` shell logic is implementation evidence, not the public package API.
</acceptance_criteria>
</task>

<task id="02" type="execute">
<title>Add a deterministic scheduling fixture source and expected evidence</title>
<read_first>
- test/1.10/电气设备控制线路安装与调试授课计划.md
- skills/jiaoan-jihua/references/calendar.json
- .planning/phases/22-scheduling-contract-and-fixture/22-CONTEXT.md
- references/scheduling-contract.md
- test/1.11/scheduling-contract/fixture-source.md if it already exists
- test/1.11/scheduling-contract/expected-schedule.json if it already exists
- test/1.11/scheduling-contract/expected-schedule.md if it already exists
</read_first>
<action>
Create `test/1.11/scheduling-contract/fixture-source.md` by reusing the v1.10 teaching-plan source shape with `first_teaching_day: "2026-05-11"` and `daily_hours: 8`, keeping ordered task/stage/content rows and trailing integer hour markers. Add `test/1.11/scheduling-contract/expected-schedule.json` with deterministic scheduled item evidence for at least the first learning task and enough subsequent rows to prove daily-capacity rollover. Add `test/1.11/scheduling-contract/expected-schedule.md` as teacher-reviewable Markdown showing derived start/end dates, term week, weekday, assigned hours, date-level hour consumption, and a `## 复核标记` section. The expected evidence must be derived from `calendar.json` and hour consumption, not from the v1.10 target Typst file.
</action>
<acceptance_criteria>
- `test/1.11/scheduling-contract/fixture-source.md` contains `first_teaching_day: "2026-05-11"` and `daily_hours: 8`.
- `test/1.11/scheduling-contract/expected-schedule.json` is valid JSON when checked with `python3 -m json.tool`.
- `test/1.11/scheduling-contract/expected-schedule.json` contains `hour_consumption`, `start_date`, `end_date`, `term_week`, `weekday`, and `assigned_hours`.
- `test/1.11/scheduling-contract/expected-schedule.md` contains `## 调度证据` and `## 复核标记`.
- At least one fixture item in `expected-schedule.json` has `hour_consumption` entries on more than one date, proving date-range derivation across daily capacity.
</acceptance_criteria>
</task>

<task id="03" type="execute">
<title>Add a fixture derivation verifier</title>
<read_first>
- scripts/derive-scheduling-fixture.py if it already exists
- skills/jiaoan-jihua/scripts/jiaoan-jihua.sh
- skills/jiaoan-jihua/references/calendar.json
- test/1.11/scheduling-contract/fixture-source.md
- test/1.11/scheduling-contract/expected-schedule.json
- test/1.11/scheduling-contract/expected-schedule.md
- references/scheduling-contract.md
</read_first>
<action>
Add `scripts/derive-scheduling-fixture.py` as a repository-local verifier for the Phase 22 fixture. It must parse YAML frontmatter enough to read `first_teaching_day` and `daily_hours`, parse ordered `##` tasks, `###` stages, and `text-N` rows, load the ordered teaching dates from `skills/jiaoan-jihua/references/calendar.json`, derive start/end dates, term week, weekday, assigned hours, and date-level hour consumption, and compare the derived output to `test/1.11/scheduling-contract/expected-schedule.json`. Include explicit failures for missing first teaching day, first teaching day not in calendar, non-positive or non-integer daily hours, malformed or non-positive row hours, and calendar exhaustion. Keep it independent of Typst rendering and do not read `test/1.10/*.typ`.
</action>
<acceptance_criteria>
- `python3 -m py_compile scripts/derive-scheduling-fixture.py` exits 0.
- `scripts/derive-scheduling-fixture.py --source test/1.11/scheduling-contract/fixture-source.md --calendar skills/jiaoan-jihua/references/calendar.json --expected test/1.11/scheduling-contract/expected-schedule.json` exits 0.
- `scripts/derive-scheduling-fixture.py` contains no reference to `.typ`.
- `scripts/derive-scheduling-fixture.py` reports a non-zero exit for an invalid `daily_hours: 0` fixture when tested with a temporary copy.
- The script documents or emits the phrase `calendar ended before all hours were assigned` for calendar exhaustion.
</acceptance_criteria>
</task>

<task id="04" type="execute">
<title>Wire documentation discoverability and preserve phase boundaries</title>
<read_first>
- README.md
- docs/directory-spec.md
- references/scheduling-contract.md
- .planning/ROADMAP.md
- .planning/REQUIREMENTS.md
- skills/jiaoan-jihua/SKILL.md
- skills/jiaoan-shicao/SKILL.md
</read_first>
<action>
Update the repository documentation only as needed so `references/scheduling-contract.md` and `test/1.11/scheduling-contract/` are discoverable. Do not add the future `teaching-design-package` skill, do not change `skills/jiaoan-jihua/SKILL.md` or `skills/jiaoan-shicao/SKILL.md` public command examples, and do not introduce package output promises such as `teaching-design-package.pdf` in Phase 22 documentation except as deferred Phase 24 context.
</action>
<acceptance_criteria>
- `README.md` or `docs/directory-spec.md` links to `references/scheduling-contract.md`.
- `README.md` or `docs/directory-spec.md` mentions `test/1.11/scheduling-contract/` as fixture evidence.
- `git diff -- skills/jiaoan-jihua/SKILL.md skills/jiaoan-shicao/SKILL.md` shows no public command-surface changes for this phase unless the executor documents an explicit no-op.
- New documentation does not claim that `teaching-design-package.pdf` is implemented in Phase 22.
</acceptance_criteria>
</task>

<task id="05" type="execute">
<title>Run Phase 22 verification and record evidence</title>
<read_first>
- references/scheduling-contract.md
- test/1.11/scheduling-contract/fixture-source.md
- test/1.11/scheduling-contract/expected-schedule.json
- test/1.11/scheduling-contract/expected-schedule.md
- scripts/derive-scheduling-fixture.py
- .planning/REQUIREMENTS.md
- .planning/phases/22-scheduling-contract-and-fixture/22-CONTEXT.md
</read_first>
<action>
Run deterministic verification for the contract and fixture. Required commands are `python3 -m py_compile scripts/derive-scheduling-fixture.py`, `python3 -m json.tool test/1.11/scheduling-contract/expected-schedule.json`, the `scripts/derive-scheduling-fixture.py --source ... --calendar ... --expected ...` command from task 03, and source assertions with `rg` for TDP IDs, required contract identifiers, `## 复核标记`, and the no-`.typ` verifier rule. Record the results in the Phase 22 execution summary when execute-phase runs.
</action>
<acceptance_criteria>
- `python3 -m py_compile scripts/derive-scheduling-fixture.py` exits 0.
- `python3 -m json.tool test/1.11/scheduling-contract/expected-schedule.json` exits 0.
- `scripts/derive-scheduling-fixture.py --source test/1.11/scheduling-contract/fixture-source.md --calendar skills/jiaoan-jihua/references/calendar.json --expected test/1.11/scheduling-contract/expected-schedule.json` exits 0.
- `rg "TDP-01|TDP-02|TDP-03|TDP-04" references/scheduling-contract.md` finds all four requirement IDs.
- `rg "\\.typ" scripts/derive-scheduling-fixture.py` exits 1.
</acceptance_criteria>
</task>

</tasks>

<verification>
Run these checks after completing the tasks:

```bash
python3 -m py_compile scripts/derive-scheduling-fixture.py
python3 -m json.tool test/1.11/scheduling-contract/expected-schedule.json >/tmp/phase22-expected-schedule.json
scripts/derive-scheduling-fixture.py --source test/1.11/scheduling-contract/fixture-source.md --calendar skills/jiaoan-jihua/references/calendar.json --expected test/1.11/scheduling-contract/expected-schedule.json
rg "TDP-01|TDP-02|TDP-03|TDP-04" references/scheduling-contract.md
rg "calendar\\.dates|calendar\\.holidays|calendar\\.makeup_days|first_teaching_day|daily_hours|items\\[\\]|hour_consumption\\[\\]|review_markers\\[\\]" references/scheduling-contract.md
rg "## 复核标记" test/1.11/scheduling-contract/expected-schedule.md references/scheduling-contract.md
rg "\\.typ" scripts/derive-scheduling-fixture.py
git diff --check
```

The final `rg "\\.typ"` command should exit 1 because the verifier must not depend on Typst target files.
</verification>

<success_criteria>
- TDP-01 through TDP-04 are represented in the Phase 22 plan and contract.
- The shared scheduling contract is documented in `references/scheduling-contract.md`.
- The fixture proves derived scheduling evidence from calendar and hour inputs.
- Invalid or uncertain scheduling data has a defined review-marker path.
- Existing `jiaoan-jihua` and `jiaoan-shicao` public behavior remains preserved.
- The phase remains bounded to scheduling contract and fixture work; Phase 23 and Phase 24 deliverables are not implemented.
</success_criteria>
