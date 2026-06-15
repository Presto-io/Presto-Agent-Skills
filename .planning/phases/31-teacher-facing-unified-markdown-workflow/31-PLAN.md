---
phase: 31
plan: 01
type: execute
wave: 1
depends_on:
  - phase: 30
files_modified:
  - skills/teaching-design-package/SKILL.md
  - skills/teaching-design-package/references/format-and-orchestration.md
autonomous: true
requirements: [TDPKG-04, TDPKG-05, TDPKG-06, TDPKG-14]
requirements_addressed: [TDPKG-04, TDPKG-05, TDPKG-06, TDPKG-14]
---

# Phase 31 Plan: Teacher-Facing Unified Markdown Workflow

<objective>
Make `teaching-design-package` read like the teacher's actual workflow: ingest many source materials, ask only for missing or conflicting information, normalize everything into one reviewable full Markdown, let the teacher edit that Markdown as the source of truth, then use scripts only for strict finalized-Markdown validation and delivery rendering. Execution must not ask users to run or stitch old standalone skills, must not use old handoff filenames, must not copy old templates, and must not treat old skills as internal dependencies or parity baselines.
</objective>

<must_haves>
## Locked Truths

- D-01: The canonical `SKILL.md` primary entry is source materials -> clarification -> unified Markdown -> strict render.
- D-02: Script commands are not the main teacher UX; they are validation and delivery tools after the unified Markdown is finalized.
- D-03: The assistant must proactively ask for missing, ambiguous, or conflicting teacher-facing facts before declaring the Markdown ready.
- D-04: The assistant must not ask teachers to mentally run, sequence, or stitch separate old standalone skills.
- D-05: The package must not hide old standalone skill structure inside its internal workflow.
- D-06: Do not use old precise full handoff filenames in Phase 31 docs or teaching-design-package docs.
- D-07: Do not copy old templates into the package and do not use old templates as parity baselines.
- D-08: Do not modify script implementation in Phase 31 unless a later execute-phase explicitly chooses to, and this plan does not require script edits.
- D-09: The human-editable Markdown may be named `teaching-design-package-full.md` or a course-specific name such as `某某某课教学资料.md`.
- D-10: YAML frontmatter contains stable, teacher-verifiable facts only; derived scheduling/output facts remain out of YAML and are extracted or computed from body evidence.
- D-11: Body content is the primary place for teaching plan rows, teaching activities, resources, evaluation details, review markers, and source-derived facts.
- D-12: `references/format-and-orchestration.md` or a new reference must define the teacher-editable Markdown contract clearly enough for a human to review and safely edit it.
- D-13: Phase 32 still owns clean successful 1+1+3 delivery enforcement and deeper scheduling validation; Phase 31 must not absorb that implementation work.
</must_haves>

<tasks>
## Task 1: Rewrite `SKILL.md` around the teacher interaction entry

<read_first>
- `AGENTS.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/30-standalone-skill-boundary-and-internalized-dependencies/30-SUMMARY.md`
- `.planning/phases/30-standalone-skill-boundary-and-internalized-dependencies/30-VERIFICATION.md`
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
</read_first>

<action>
Update `skills/teaching-design-package/SKILL.md` so the first meaningful workflow a runtime sees is teacher-facing:

1. accept many source materials such as course standards, lesson topics, schedules, activities, textbooks, assessment notes, school format requirements, and teacher notes;
2. inspect and normalize those materials into package concepts;
3. ask targeted clarification questions for missing required facts, contradictions, uncertain dates/hours, duplicate course facts, unresolved review markers, or teacher choices;
4. organize the answer into one complete full-package Markdown;
5. pause for teacher review/editing of that Markdown;
6. only then run scripts for strict validation, Typst/PDF generation, and delivery evidence.

Move script examples below the teacher workflow and label them as finalized-Markdown validation/delivery commands. Keep runtime adapter notes, but adjust them so each runtime follows the teacher workflow first and uses scripts only after the Markdown checkpoint is ready.
</action>

<acceptance_criteria>
- `SKILL.md` begins its Process/Workflow with source-material ingestion and clarification before any script command block.
- `SKILL.md` explicitly names `teaching-design-package-full.md` and course-specific `某某某课教学资料.md` as acceptable human-editable Markdown source-of-truth filenames.
- `SKILL.md` tells agents to ask targeted clarification questions for missing, conflicting, uncertain, or teacher-choice-dependent facts.
- `SKILL.md` states scripts consume finalized Markdown for validation/rendering and are not the teacher's content-organization UX.
- `SKILL.md` does not instruct users to install, run, chain, or stitch old standalone skills.
</acceptance_criteria>

## Task 2: Define clarification and source-material normalization rules

<read_first>
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
</read_first>

<action>
Document a practical clarification strategy in the skill entry or reference:

- Ask only for facts needed to produce a credible full Markdown or resolve contradictions.
- Prefer extracting facts from source bodies before asking the teacher.
- Group questions by topic: course identity, class/teacher facts, schedule/time evidence, lesson/activity structure, resources, assessment, school-specific format constraints, and unresolved review markers.
- When multiple sources conflict, quote or summarize the conflict and ask the teacher to choose or confirm.
- When information is optional or can be safely marked for review, keep the Markdown editable with a clear review marker instead of blocking.
- Do not ask the teacher to supply derived facts such as total hours, school year, semester, output configuration, or internal validation flags when those can be derived from body evidence or belong to script/config boundaries.
</action>

<acceptance_criteria>
- Clarification guidance distinguishes required blockers, conflict resolution, safe review markers, and optional teacher preferences.
- Normalization guidance maps source materials into one course package without preserving source-file fragmentation.
- Guidance explicitly says body evidence should be used before asking for YAML-like facts.
- The plan avoids prescribing OCR or arbitrary binary extraction as required behavior; raw extraction remains future scope unless source text is already available.
</acceptance_criteria>

## Task 3: Make the Markdown contract teacher-editable and body-centered

<read_first>
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `.planning/REQUIREMENTS.md`
</read_first>

<action>
Update `references/format-and-orchestration.md`, or add a new directly linked reference if that keeps the file clearer, to define the teacher-editable Markdown contract:

- the full Markdown is the human-editable source of truth before rendering;
- frontmatter is minimal and limited to stable facts a teacher can verify directly;
- teaching schedule rows, activity hours, resources, assessment details, teaching-design body, review markers, and source-derived evidence belong in the Markdown body;
- derived fields such as total hours, date ranges, school year, semester, output readiness, status flags, and renderer diagnostics must not be manually maintained in YAML;
- the assistant may generate the initial Markdown from many source materials, but must preserve a structure a teacher can edit without understanding internal scripts;
- script validation may reject or mark non-final Markdown when body evidence is inconsistent.
</action>

<acceptance_criteria>
- A reference section titled around teacher-editable Markdown or source-material orchestration exists and is linked from `SKILL.md`.
- The reference covers YAML metadata boundaries, body extraction rules, review markers, and human editability.
- The reference keeps script entry boundaries explicit: scripts validate and render finalized Markdown; they do not replace teacher-agent clarification.
- The reference contains no old precise full handoff filenames and no instruction to copy old templates.
</acceptance_criteria>

## Task 4: Remove old-workflow leakage from package docs without changing scripts

<read_first>
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/scripts/teaching-design-package.sh` only for boundary awareness; do not edit unless execute-phase explicitly revises scope.
</read_first>

<action>
Clean package documentation so the public workflow cannot be read as a script-first or old-skill-stitching experience. Keep Phase 30's standalone package-owned rendering boundary. Do not alter the script implementation for Phase 31 unless execution discovers a hard contradiction that cannot be fixed in docs and stops for a new user decision before editing scripts.
</action>

<acceptance_criteria>
- `git diff --name-only` after execution contains no script path unless execution records an explicit scope change and user approval.
- `SKILL.md` and the selected reference do not use legacy standalone skills as internal dependencies, package resources, or parity baselines.
- Package docs do not contain old precise full handoff filenames.
- Package docs keep six-runtime portability notes consistent with the teacher-facing workflow.
</acceptance_criteria>

## Task 5: Verify Phase 31 documentation and planning boundaries

<read_first>
- `.planning/phases/31-teacher-facing-unified-markdown-workflow/31-PLAN.md`
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- Any new reference added by Task 3
</read_first>

<action>
Run documentation and boundary checks that prove the teacher-facing workflow is primary and old handoff/template/script-first regressions did not return. Record exact command outcomes in the Phase 31 summary during execute-phase.
</action>

<acceptance_criteria>
- A scan confirms `SKILL.md` contains the sequence concepts: source materials, clarification/questions, unified Markdown, teacher review/editing, finalized Markdown, script validation/rendering.
- A scan confirms the selected reference contains teacher-editable Markdown contract, YAML boundary, body extraction, and script boundary language.
- Old precise full handoff filename scan over `.planning/phases/31-teacher-facing-unified-markdown-workflow`, `skills/teaching-design-package/SKILL.md`, and package references returns no matches.
- `git diff --name-only -- skills/teaching-design-package/scripts` is empty for this phase.
- `git diff --cached --check` passes before commit.
</acceptance_criteria>
</tasks>

<verification>
Run these checks after implementation:

```bash
rg 'source materials|源材料|clarification|clarify|澄清|提问|unified Markdown|统一 Markdown|teacher review|教师.*审|finalized Markdown|审定.*Markdown|script.*validation|脚本.*验证|render' \
  skills/teaching-design-package/SKILL.md

rg 'teacher-editable|教师.*可编辑|YAML|frontmatter|正文|body|derived|派生|script.*boundary|脚本.*边界' \
  skills/teaching-design-package/references/format-and-orchestration.md

legacy_full_pattern="$(printf '%s|%s|%s|%s' \
  "$(printf '%s-%s-%s[.]%s' 'jiaoan' 'jihua' 'full' 'md')" \
  "$(printf '%s-%s-%s[.]%s' 'jiaoan' 'shicao' 'full' 'md')" \
  "$(printf '%s-%s-%s[.]%s' 'teaching' 'plan' 'full' 'md')" \
  "$(printf '%s-%s-%s[.]%s' 'lesson' 'plan' 'full' 'md')")"
! rg "$legacy_full_pattern" \
  .planning/phases/31-teacher-facing-unified-markdown-workflow \
  skills/teaching-design-package/SKILL.md \
  skills/teaching-design-package/references

git diff --name-only -- skills/teaching-design-package/scripts

git diff --check
git diff --cached --check
```

For `git diff --name-only -- skills/teaching-design-package/scripts`, the expected output is empty. For the legacy full-pattern scan, a non-zero `rg` exit is the desired result. The final `git diff --cached --check` must run after staging only the Phase 31 planning and documentation files selected for the execution commit.
</verification>

<success_criteria>
- `SKILL.md` makes the teacher-facing source-materials-to-full-Markdown workflow the main entry.
- The workflow includes targeted clarification before producing the unified Markdown.
- `teaching-design-package-full.md` or a course-specific teaching-materials Markdown is the human-editable source of truth.
- A package reference defines the teacher-editable Markdown contract, YAML boundary, body extraction rules, review markers, and script boundary.
- Scripts remain bounded to finalized-Markdown validation and delivery generation.
- Phase 31 docs and teaching-design-package docs contain no old precise full handoff filenames.
- No script implementation files are changed by Phase 31 unless a later execute-phase explicitly expands scope.
</success_criteria>

<threat_model>
This phase is documentation and skill-entry workflow work. The main risks are user-experience regression, provenance confusion, and scope creep.

- User-experience regression: the entry could still read as "run scripts first." Mitigation: make source-material ingestion and clarification the first workflow and push script commands below the Markdown checkpoint.
- Provenance confusion: agents could put derived facts in YAML because it is convenient. Mitigation: document the YAML/body boundary and require body evidence extraction before asking teachers for derived values.
- Old-workflow leakage: previous handoff/template names could return through examples or scans. Mitigation: run the old precise full handoff filename scan over Phase 31 docs and package docs.
- Scope creep: execution could start changing render scripts. Mitigation: plan verification requires an empty script diff and treats script edits as a stop-and-ask scope change.
</threat_model>
