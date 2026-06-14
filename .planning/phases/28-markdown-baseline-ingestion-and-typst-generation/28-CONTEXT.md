# Phase 28: Markdown Baseline Ingestion and Typst Generation - Context

**Gathered:** 2026-06-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 28 makes the `teaching-design-package` render path consume the committed full-package Markdown baseline at `skills/teaching-design-package/templates/teaching-design-package-full.md` without changing its teacher-facing structure. The phase delivers parser/ingestion behavior, split semantic handoff, and one package Typst artifact generated from that Markdown through the render path.

This phase covers TDBR-01 through TDBR-05 for Markdown ingestion/Typst generation and TDBR-12 through TDBR-17 for derived hours, dates, term metadata, and default-value boundaries. It must preserve one copyable, teacher-reviewable Markdown artifact in the same reference-document shape, identify the semantic split between `授课进度计划` and `教学设计方案`, generate one package Typst from the Markdown source rather than treating Typst as a maintained source file, and leave derived-data evidence that Phase 29 can render into PDFs.

Phase 28 does not own final PDF parity. The milestone acceptance eventually requires one Markdown, one Typst, and three PDFs, but the three real PDF outputs and standalone parity gates are Phase 29 scope. Phase 28 should leave explicit interfaces and evidence hooks so Phase 29 can compile or merge PDFs without reworking ingestion.

Phase 28 does own the derived-data contract that Phase 29 must render and parity-check. The plan parser must derive total hours, learning-task hours, lesson-plan activity hours, task date ranges, and academic year/semester from `# 授课进度计划`, `first_teaching_day`, built-in teaching-day calendar support, and script defaults. These facts must not move back into package YAML or become hand-maintained duplicate teacher-facing fields.

</domain>

<decisions>
## Implementation Decisions

### Scope Boundaries and Non-Goals

- **D-01:** Treat `skills/teaching-design-package/templates/teaching-design-package-full.md` as the source contract for Phase 28. Renderer ingestion must adapt around this file; do not rewrite headings, add machine-only wrapper sections, or force teachers to use the older package `## 授课计划` / `## 实操教案` section shape.
- **D-02:** Preserve the teacher-facing Markdown format exactly as the maintained reference. Any machine-readable state needed by the renderer should be inferred from existing frontmatter, heading hierarchy, line order, and section titles, or stored in generated sidecar evidence outside the baseline Markdown.
- **D-03:** Keep old standalone skills independent. Phase 28 may generate module-compatible handoff Markdown for `jiaoan-jihua` and `jiaoan-shicao`, but must not change their public commands, required input shapes, output paths, or documentation contracts.
- **D-04:** Do not implement Phase 29 acceptance inside Phase 28. Combined package PDF, teaching-plan PDF parity, lesson-plan PDF parity, and standalone regression verification are downstream work. Phase 28 only records the planned PDF slots/statuses and proves the Typst path is generated from baseline Markdown.
- **D-05:** Do not stage generated `deliverables/` artifacts. Generated Markdown/Typst/PDF smoke outputs should live under `/tmp` or deliberate phase verification evidence when later commands implement and verify.

### Baseline Markdown Semantic Recognition

- **D-06:** Identify the teaching-plan source by the top-level `# 授课进度计划` section. Everything from that heading until the next top-level `# 教学设计方案` belongs to the teaching-plan semantic source. Within it, `##` headings are learning tasks, `###` headings are stages, and content lines ending in an integer hour marker such as `-2` are teaching-plan rows compatible with `jiaoan-jihua`.
- **D-07:** Identify the lesson-plan source by the top-level `# 教学设计方案` section. This section contains repeating lesson-plan blocks, each beginning with `## 学习任务分析`, followed by one `## 教学活动设计——学习任务N：...`, and ending with `## 学业评价` before the next `## 学习任务分析` or end of document.
- **D-08:** Identify `学习任务分析` blocks by literal `## 学习任务分析`. The parser should preserve the existing subheadings `### 一、学习任务描述` through `### 五、学习资源`, including their natural-language paragraphs and numbered lists, without requiring new IDs.
- **D-09:** Identify `教学活动设计` blocks by headings matching `## 教学活动设计——学习任务N：<task title>`. Under each block, `### <stage>——<task title>` headings define stage/activity groups, and `#### <activity>` headings define individual activity rows. The following paragraphs keep the current implicit order: learning content, student activity, teacher activity, then method lines, matching the existing `jiaoan-shicao` activity-table source pattern.
- **D-10:** Identify `学业评价` blocks by literal `## 学业评价`. The numbered semicolon-separated lines are evaluation rows and the trailing `小结：...` paragraph is summary text. The parser should keep both, because Phase 29 parity will compare lesson-plan output against standalone `jiaoan-shicao` behavior.
- **D-11:** Preserve repeated task structure. The baseline has three lesson-plan blocks and one combined teaching-plan section; ingestion should not assume only the first task is present or flatten all lesson-plan analysis/evaluation text into a single block.

### Parser Adaptation Without Markdown Format Changes

- **D-12:** Prefer a section-slicer layer over Markdown mutation. The package renderer should parse the baseline into an internal model or generated temporary handoffs, leaving `teaching-design-package-full.md` copyable and unchanged.
- **D-13:** The package script's current `validate_package()` expects old `## 课程与整包元数据`, `## 调度输入`, `## 调度证据`, `## 授课计划`, `## 实操教案`, `## 输出清单`, and `## 复核标记` sections. Phase 28 should replace or extend validation so baseline mode accepts `# 授课进度计划` and `# 教学设计方案` as the required structural anchors while preserving old behavior only if planning explicitly chooses compatibility mode.
- **D-14:** Frontmatter parsing must support the current baseline fields: `course_name`, `major_name`, `course_attribute`, `textbook_name`, `class_name`, `teachers`, and `first_teaching_day`. The renderer should map `teachers` into module handoff teacher metadata without changing the YAML list shape in the reference Markdown.
- **D-15:** If package-level fields needed by old handoffs are absent, derive only from visible baseline content or keep explicit non-final status. Do not invent hidden school, semester, teacher, date, or evaluation facts to make a render pass green.
- **D-16:** Review markers in the older package contract are not present in the corrected Markdown baseline. Phase 28 should not force a `## 复核标记` section into the teacher-facing document; if unresolved data needs tracking, write manifest/status evidence or generated sidecar notes.

### Derived Hours, Dates, and Metadata

- **D-28:** Do not preserve or rely on package YAML `total_hours`. Total course hours must be calculated by summing every `活动名称-课时` row under `# 授课进度计划`; the current baseline must calculate to `160H`.
- **D-29:** Calculate each learning-task hour total from that task's own teaching-plan rows. The current baseline must calculate `CA6140=40H`, `X62W=60H`, and `Z3040=60H`.
- **D-30:** Lesson-plan activity `##### xH` rows, if needed for `jiaoan-shicao` handoff compatibility, are generated facts derived from same-name or same-order teaching-plan activities. They must not be treated as teacher-maintained source data in the package Markdown.
- **D-31:** If a lesson-plan activity cannot be mapped to a same-name or same-order teaching-plan activity, Phase 28 must fail the render path or write an explicit non-final/review-needed status. It must not silently assign a guessed duration.
- **D-32:** Infer each `学习任务分析` 起止日期 from `first_teaching_day`, the skill's built-in real teaching-day calendar text/resource, default `8` hours per teaching day, and the parsed row-hour sequence. The output format is `M月D日——M月D日` without year.
- **D-33:** The current baseline date expectations are `CA6140=5月11日——5月15日`, `X62W=5月18日——5月27日`, and `Z3040=5月27日——6月5日`, derived from `first_teaching_day: "2026-05-11"`, `skills/jiaoan-jihua/references/calendar.json`, and `8` daily hours.
- **D-34:** Infer `school_year` and `semester` from `first_teaching_day`, not package YAML. Spring/first-half dates map to previous-year/current-year academic year second semester; autumn/second-half dates map to current-year/next-year academic year first semester. The current baseline must infer `2025-2026学年第二学期`.
- **D-35:** Keep defaults such as `hour_unit`, `daily_hours`, `date_display_format`, `date_locale`, `calendar_source`, `holidays`, `makeup_days`, `source_of_truth`, `outputs`, and `validation` in script/skill contracts or generated manifest/evidence. They must not be reintroduced as package YAML fields.
- **D-36:** The generated package Markdown artifact must remain directly copyable from the baseline document shape. Machine fields may be reflected in handoffs, manifests, Typst provenance, or verification evidence only when needed for rendering.

### Package Typst Generation and Phase 29 Interface

- **D-17:** Add a package-level Typst generation path that consumes the baseline Markdown and produces one package Typst artifact, preferably `teaching-design-package.typ`, through public `teaching-design-package.sh` behavior or an explicitly documented new subcommand chosen during planning.
- **D-18:** The package Typst artifact should include both semantic parts in source order: the rendered teaching-plan content from `# 授课进度计划` and the rendered lesson-plan content from `# 教学设计方案`. It can initially compose generated module Typst or emit a combined Typst wrapper, but the provenance must show it came from the Markdown baseline.
- **D-19:** Preserve split handoff slots for Phase 29: `jiaoan-jihua-full.md`, `jiaoan-shicao-full.md`, `teaching-plan.typ`, `lesson-plans.typ`, `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf`. Phase 28 may leave PDF statuses as `not_run`, `planned`, `missing_compiler`, or `merge_unavailable`, but must not mark PDFs `passed` without files.
- **D-20:** Package manifest or verification evidence should link the single Markdown baseline to every generated artifact. A useful evidence shape is: `source_markdown`, `package_typ`, `teaching_plan_handoff`, `lesson_plan_handoff`, semantic section ranges or heading anchors, and explicit `generated_from_markdown: true`.
- **D-21:** The package Typst output should not become the source of truth. Any generated `.typ` file may be inspected and compiled, but future edits should continue to happen in Markdown.

### Risks and Open Questions for Planning

- **D-22:** Risk: existing `teaching-design-package.sh plan-split` currently copies standalone templates rather than extracting from the corrected package Markdown. Planning must decide whether to rewrite the scaffold functions to slice baseline sections, add a baseline-specific mode, or introduce a package renderer helper.
- **D-23:** Risk: the corrected Markdown has top-level `#` section anchors, while the previous package contract and validation were based on `##` package sections. A naive validator will reject the new baseline.
- **D-24:** Risk: activity rows in `教学活动设计` are paragraph blocks rather than explicit pipe tables. The parser must preserve paragraph order and blank-line grouping carefully; ad hoc line splitting could scramble learning content, student activity, teacher activity, and method fields.
- **D-25:** Risk: teacher names are stored as YAML list `teachers`, while older jiaoan handoffs expect scalar metadata such as `teacher_name`. Planning should choose a deterministic mapping and record it in generated handoff evidence.
- **D-26:** Open question for planner/researcher: should `teaching-design-package.sh render-split` be upgraded in place to accept the baseline, or should a new command such as `render-package-typ` be added while keeping legacy `plan-split` behavior? The decision should optimize for public contract clarity and minimal breakage.
- **D-27:** Open question for planner/researcher: whether combined package Typst should wrap the two generated split Typst bodies, invoke module renderers and concatenate selected body sections, or implement a direct package renderer. The chosen path must keep Markdown provenance clear and leave Phase 29 PDF parity testable.

### Claude's Discretion

- Prefer black-box verification from public shell commands over internal parser-only assertions.
- Prefer a narrow parser/slicer that recognizes the corrected heading structure over broad Markdown schema redesign.
- Prefer generated sidecar evidence and manifests for machine status instead of inserting non-teacher-facing markers into the baseline Markdown.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Requirements

- `AGENTS.md` — Repository language, editing, skill authoring, GSD workflow, and OpenClaw/Hermes requirements.
- `.planning/PROJECT.md` — Captures active v1.13 scope, Markdown baseline discipline, standalone teaching-skill discipline, and current project constraints.
- `.planning/REQUIREMENTS.md` — Locks TDBR-01 through TDBR-05 and TDBR-12 through TDBR-17 for Phase 28 planning, with TDBR-06 through TDBR-11 plus final parity coverage for Phase 29.
- `.planning/ROADMAP.md` — Defines Phase 28 goal, success criteria, dependency on Phase 27, and Phase 29 boundary.
- `.planning/STATE.md` — Records Phase 28 as current phase and v1.13 as active milestone.

### Baseline Markdown and Package Contract

- `skills/teaching-design-package/templates/teaching-design-package-full.md` — Corrected teacher-facing baseline Markdown. This is the source contract for Phase 28 and must not be reformatted to satisfy parser internals.
- `skills/teaching-design-package/SKILL.md` — Canonical package skill entry and runtime adapter notes that must remain portable.
- `skills/teaching-design-package/references/format-and-orchestration.md` — Previous package contract, split output status semantics, combined output semantics, and module handoff rules. Useful as existing behavior, but Phase 28 must adapt it to the corrected baseline.
- `skills/teaching-design-package/scripts/teaching-design-package.sh` — Current package script. Existing validation and scaffold functions are likely implementation points.

### Standalone Teaching Skill Contracts

- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` — Existing teaching-plan renderer and public command surface.
- `skills/jiaoan-jihua/references/format-and-rendering.md` — Teaching-plan Markdown shape, Typst generation behavior, and verification rules.
- `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md` — Standalone teaching-plan handoff shape that Phase 28 may need to generate from `# 授课进度计划`.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` — Existing lesson-plan renderer and public command surface.
- `skills/jiaoan-shicao/references/format-and-rendering.md` — Lesson-plan Markdown shape, renderer contract, activity table behavior, and verification rules.
- `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md` — Standalone lesson-plan handoff shape that Phase 28 may need to generate from `# 教学设计方案`.

### Prior Phase Context to Preserve

- `.planning/phases/25-regression-verification-and-documentation-index/25-CONTEXT.md` — Public command regression, manifest truthfulness, runtime adapter coverage, and documentation-index expectations.
- `.planning/phases/26-package-date-backfill-repair/26-CONTEXT.md` — Package handoff/date backfill decisions and generated artifact discipline.
- `.planning/phases/27-official-activity-table-width-alignment/27-CONTEXT.md` — Current `jiaoan-shicao` activity-table width behavior and package-path regression expectations.
- `references/scheduling-contract.md` — Shared scheduling evidence model. Use only when deriving handoff evidence; do not require new teacher-facing sections in the baseline Markdown.
- `skills/jiaoan-jihua/references/calendar.json` — Built-in teaching-day calendar support used by the current baseline date-range expectation.

### Fixtures and Expected Evidence

- `test/1.10/电气设备控制线路安装与调试授课计划.md` — Existing standalone teaching-plan strict fixture source.
- `test/1.10/电气设备控制线路安装与调试授课计划.typ` — Existing standalone teaching-plan strict Typst oracle.
- `test/1.10/电气设备控制线路安装与调试教案.md` — Existing standalone lesson-plan strict fixture source.
- `test/1.10/电气设备控制线路安装与调试教案.typ` — Existing standalone lesson-plan strict Typst oracle.
- `test/1.11/teaching-design-package/expected-*.json` — Existing package manifest status fixtures; useful when preserving status semantics, but not the corrected Markdown shape.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `frontmatter_value()` in `skills/teaching-design-package/scripts/teaching-design-package.sh` already extracts scalar YAML fields, but it does not currently handle YAML lists such as `teachers`.
- `write_jihua_scaffold()` and `write_shicao_scaffold()` are narrow handoff points. They currently copy standalone templates, so they are likely places to replace template-copy behavior with baseline slicing.
- `cmd_render_split()` already calls the standalone `jiaoan-jihua.sh render` and `jiaoan-shicao.sh render` commands explicitly, which is useful for preserving public standalone contracts while generating package artifacts.
- `write_manifest()` already records split Typst/PDF and combined-output statuses. Phase 28 can extend this evidence with baseline provenance without inventing a new status system.

### Established Patterns

- Markdown remains the teacher-reviewable semantic checkpoint before Typst/PDF output.
- Public shell scripts are stable black-box contracts; implementation should preserve commands or add clearly documented commands without breaking existing ones.
- Manifest/status values must be honest: Typst/PDF status should be `passed` only when files exist after explicit commands.
- OpenClaw and Hermes compatibility means canonical instructions should describe files, scripts, safety boundaries, and verification, not one runtime's private syntax.

### Integration Points

- Existing `validate_package()` will likely reject the corrected baseline because it requires old `##` package sections. Phase 28 planning should address validation first.
- Existing `has_section()` only checks `##` headings. Baseline ingestion needs top-level `#` section awareness.
- Existing `jiaoan-jihua` renderer can consume a generated handoff where the body follows ordered `##` task, `###` stage, and `text-hours` lines.
- Existing `jiaoan-shicao` renderer can consume a generated handoff with `## 学习任务分析`, `## 教学活动设计`, and `## 学业评价` sections. The corrected baseline already contains those structures after `# 教学设计方案`.
- Phase 27 changed `jiaoan-shicao` activity table behavior; any generated handoff should preserve `教学活动设计` heading/task grouping so those width rules remain testable.

</code_context>

<specifics>
## Specific Ideas

- A high-signal parser smoke test should read `skills/teaching-design-package/templates/teaching-design-package-full.md` and assert:
  - one `# 授课进度计划` section exists before one `# 教学设计方案` section;
  - three teaching-plan `##` task headings are found under `# 授课进度计划`;
  - three `## 学习任务分析` blocks, three `## 教学活动设计——学习任务...` blocks, and three `## 学业评价` blocks are found under `# 教学设计方案`;
  - no edits are made to the baseline Markdown.
- The same smoke test should assert derived hours from `# 授课进度计划`: `total=160H`, `CA6140=40H`, `X62W=60H`, `Z3040=60H`.
- Date-range verification should use `first_teaching_day: "2026-05-11"`, the built-in teaching-day calendar, and default `8` hours/day to assert `5月11日——5月15日`, `5月18日——5月27日`, and `5月27日——6月5日`.
- Metadata verification should assert `2025-2026学年第二学期` is inferred, and that package YAML does not contain `total_hours`, `school_year`, `semester`, `daily_hours`, `hour_unit`, `date_display_format`, `date_locale`, `calendar_source`, `holidays`, `makeup_days`, `source_of_truth`, `outputs`, or `validation`.
- A generated package Typst verification should include a marker/comment or manifest field showing `source_markdown: skills/teaching-design-package/templates/teaching-design-package-full.md` and the generated `.typ` path.
- The generated package Typst should be inspected for content from both halves, for example `授课进度计划`/task table content and `学习任务分析`/`教学活动设计` content.
- The plan should include `git diff -- skills/teaching-design-package/templates/teaching-design-package-full.md` or an equivalent hash check after implementation to prove the baseline reference file was not modified.
- Phase 29 should receive explicit slots for `teaching-plan.pdf`, `lesson-plans.pdf`, and `teaching-design-package.pdf`; Phase 28 should not fake those PDFs by status text alone.

</specifics>

<deferred>
## Deferred Ideas

- Producing and parity-checking the three final PDFs belongs to Phase 29.
- Redesigning the package Markdown into a new schema is out of scope and listed as TDBR-FUTURE-01.
- Replacing `jiaoan-jihua` or `jiaoan-shicao` with package-only entry points is out of scope and listed as TDBR-FUTURE-02.
- OCR, arbitrary external import, hosted review, cloud approval, and unrelated document families remain future-only.

</deferred>

---

*Phase: 28-Markdown Baseline Ingestion and Typst Generation*
*Context gathered: 2026-06-15*
