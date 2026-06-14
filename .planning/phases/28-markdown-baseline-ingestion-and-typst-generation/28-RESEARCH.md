# Phase 28 Research: Markdown Baseline Ingestion and Typst Generation

**Phase:** 28 - Markdown Baseline Ingestion and Typst Generation
**Command:** `/gsd:plan-phase 28`
**Researched:** 2026-06-15
**Status:** Complete

## Scope

Phase 28 is internal repository research for planning only. No external research is required because the work is constrained to existing Markdown, shell renderers, package manifests, and GSD phase context.

This phase covers TDBR-01 through TDBR-05 for Markdown ingestion and package Typst generation, plus TDBR-12 through TDBR-17 for derived hours, dates, term metadata, and default-value boundaries:

- consume `skills/teaching-design-package/templates/teaching-design-package-full.md`;
- preserve the baseline document's teacher-facing Markdown format;
- produce a copyable package Markdown artifact in the same shape;
- generate one package Typst artifact through the render path;
- preserve and record the semantic split between `# 授课进度计划` and `# 教学设计方案`.
- derive total/task hours, lesson activity hours, task date ranges, and academic year/semester without reintroducing those facts as teacher-maintained package YAML.

Three final PDFs and standalone parity are Phase 29 scope, but Phase 29 must consume the Phase 28 derived-data contract rather than reinterpret those values manually.

## Local Findings

### Baseline Markdown Shape

The baseline `skills/teaching-design-package/templates/teaching-design-package-full.md` starts with YAML frontmatter containing:

- `course_name`
- `major_name`
- `course_attribute`
- `textbook_name`
- `class_name`
- `teachers`
- `first_teaching_day`

The baseline frontmatter intentionally does not contain `total_hours`, `school_year`, `semester`, `daily_hours`, `hour_unit`, `date_display_format`, `date_locale`, `calendar_source`, `holidays`, `makeup_days`, `source_of_truth`, `outputs`, or `validation`. Those values are derived script/skill contract facts or generated evidence, not teacher-maintained package YAML.

The body has two top-level anchors:

- `# 授课进度计划`
- `# 教学设计方案`

Under `# 授课进度计划`, `##` headings are learning tasks, `###` headings are stages, and content lines end with integer hour markers such as `-2`. This matches the body contract expected by `jiaoan-jihua` once proper frontmatter is generated.

Under `# 教学设计方案`, the baseline repeats three lesson-plan groups. Each group follows this pattern:

- `## 学习任务分析`
- `## 教学活动设计——学习任务N：...`
- `## 学业评价`

The `教学活动设计` blocks use `###` stage headings and `####` activity headings. The existing `jiaoan-shicao` template additionally expects `##### <hours>H` lines before each activity content group, so Phase 28 execution must either infer those from the teaching-plan rows or record non-final gaps honestly if an activity cannot be mapped.

### Derived Baseline Expectations

From `# 授课进度计划`, every row ending in `-N` contributes `N` hours. The current baseline derives:

- total package hours: `160H`
- `CA6140`: `40H`
- `X62W`: `60H`
- `Z3040`: `60H`

Using `first_teaching_day: "2026-05-11"`, the existing built-in teaching-day calendar resource `skills/jiaoan-jihua/references/calendar.json`, and default `8` hours per teaching day, the current baseline derives:

- `CA6140`: `5月11日——5月15日`
- `X62W`: `5月18日——5月27日`
- `Z3040`: `5月27日——6月5日`

The same `first_teaching_day` derives academic metadata `2025-2026学年第二学期`. These values must be generated or recorded as evidence; they must not be added back to package YAML as manually maintained fields.

### Existing Package Script

`skills/teaching-design-package/scripts/teaching-design-package.sh` currently keeps the public command surface:

- `example`
- `plan-split`
- `render-split`
- `plan-end-of-term`
- `render-end-of-term`
- `render-package`
- `manifest`
- `info`
- `version`

Important implementation points:

- `validate_package()` currently requires old `## 课程与整包元数据`, `## 调度输入`, `## 调度证据`, `## 授课计划`, `## 实操教案`, `## 输出清单`, and `## 复核标记` sections. It will reject the corrected baseline unless baseline-mode validation is added.
- `frontmatter_value()` extracts scalar frontmatter only. It does not map YAML list fields such as `teachers`.
- `write_jihua_scaffold()` currently copies `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md` instead of slicing `# 授课进度计划`.
- `write_shicao_scaffold()` currently starts from the standalone template and only performs date backfill for the old package shape. It does not slice the repeated `# 教学设计方案` content from the baseline.
- `cmd_render_split()` already calls standalone `jiaoan-jihua.sh render` and `jiaoan-shicao.sh render`, which is useful for preserving the standalone public contracts.
- `write_manifest()` records split Typst/PDF statuses and combined output status, but does not yet record baseline provenance or a package Typst path.
- `cmd_render_package()` currently delegates to split rendering and manifest/merge behavior; it does not generate a single `teaching-design-package.typ` package artifact.

### Existing Standalone Contracts

`jiaoan-jihua` accepts:

- frontmatter with scalar `teacher_name`;
- ordered `##` tasks, `###` stages, and `text-N` rows;
- `first_teaching_day` and optional `daily_hours`.

`jiaoan-shicao` accepts:

- frontmatter with scalar `teacher_name`;
- repeated three-part body sections: `## 学习任务分析`, `## 教学活动设计`, and `## 学业评价`;
- `## 教学活动设计——主题`, `### 学习环节——学习单元`, `#### 活动名称`, and `##### 课时`.

The package implementation should generate module handoffs that conform to these existing contracts. It must not change public commands, accepted standalone inputs, or output paths for `jiaoan-jihua` and `jiaoan-shicao`.

## Planning Decisions

1. Use heading-based baseline mode instead of mutating the baseline Markdown.
2. Extend package validation to accept either the old package contract or the corrected baseline contract, but make the Phase 28 baseline path explicit in verification.
3. Map YAML `teachers` list deterministically to `teacher_name` for module handoffs:
   - if one teacher is present, use that value;
   - if multiple teachers are present, join with `、`;
   - if the list is absent or empty, leave `teacher_name` blank and record status in provenance evidence.
4. Generate or copy one teacher-reviewable package Markdown artifact from the baseline into the output directory without reformatting the maintained baseline.
5. Generate `jiaoan-jihua-full.md` from the `# 授课进度计划` section, not from the old standalone template body.
6. Generate `jiaoan-shicao-full.md` from the `# 教学设计方案` section while preserving repeated task blocks and existing heading text.
7. Derive package total hours and per-task hours from plan rows only; do not require or preserve package YAML `total_hours`.
8. Derive lesson-plan activity `##### xH` handoff rows from same-name or same-order plan activities only; fail or record non-final/review-needed status if mapping fails.
9. Derive task date ranges and academic year/semester from `first_teaching_day`, built-in teaching-day calendar support, default `8` hours/day, and parsed plan-row hours.
10. Keep defaults such as `hour_unit`, `daily_hours`, `date_display_format`, `date_locale`, `calendar_source`, `holidays`, `makeup_days`, `source_of_truth`, `outputs`, and `validation` in script/skill contracts or generated evidence, not package YAML.
11. Generate one package Typst artifact named `teaching-design-package.typ` through `teaching-design-package.sh render-package`.
12. Record provenance in manifest or sidecar evidence with at least:
   - `source_markdown`
   - `generated_package_markdown`
   - `package_typ`
   - `teaching_plan_handoff`
   - `lesson_plan_handoff`
   - derived total/task hours
   - derived date ranges and academic term metadata
   - semantic section anchors or line ranges
   - `generated_from_markdown: true`
13. Leave Phase 29 PDF slots explicit:
   - `teaching-plan.pdf`
   - `lesson-plans.pdf`
   - `teaching-design-package.pdf`
   Their Phase 28 statuses must be `not_run`, `planned`, `missing_compiler`, or `merge_unavailable`, never `passed` without actual files.

## Suggested Verification Shape

Phase 28 execution should verify the plan with black-box commands against the public package script:

```bash
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh

baseline="skills/teaching-design-package/templates/teaching-design-package-full.md"
before_hash="$(shasum -a 256 "$baseline" | awk '{print $1}')"
tmpdir="$(mktemp -d /tmp/tdp-phase28.XXXXXX)"

skills/teaching-design-package/scripts/teaching-design-package.sh example \
  --output "$tmpdir/teaching-design-package-full.md"

diff -u "$baseline" "$tmpdir/teaching-design-package-full.md"

skills/teaching-design-package/scripts/teaching-design-package.sh plan-split \
  --input "$tmpdir/teaching-design-package-full.md" \
  --out-dir "$tmpdir/out"

skills/teaching-design-package/scripts/teaching-design-package.sh render-package \
  --input "$tmpdir/teaching-design-package-full.md" \
  --out-dir "$tmpdir/render"

test -f "$tmpdir/render/teaching-design-package.typ"
test -f "$tmpdir/render/teaching-design-package-manifest.json"

after_hash="$(shasum -a 256 "$baseline" | awk '{print $1}')"
test "$before_hash" = "$after_hash"
git diff -- "$baseline" --exit-code
```

The executor should also assert the semantic counts from the baseline and generated handoffs:

- one `# 授课进度计划` before one `# 教学设计方案`;
- three teaching-plan `##` task headings under `# 授课进度计划`;
- three `## 学习任务分析` blocks;
- three `## 教学活动设计——学习任务...` blocks;
- three `## 学业评价` blocks;
- `teacher_name: "张老师"` appears in both module handoffs for the current baseline;
- derived hours are `total=160H`, `CA6140=40H`, `X62W=60H`, `Z3040=60H`;
- derived date ranges are `5月11日——5月15日`, `5月18日——5月27日`, and `5月27日——6月5日`;
- inferred academic metadata is `2025-2026学年第二学期`;
- package YAML does not contain manually maintained derived/default fields such as `total_hours`, `school_year`, `semester`, `daily_hours`, `hour_unit`, `date_display_format`, `date_locale`, `calendar_source`, `holidays`, `makeup_days`, `source_of_truth`, `outputs`, or `validation`;
- package manifest or provenance sidecar contains planned PDF slots with non-passed statuses.

## Risks for Execute Phase

- A naive parser can break paragraph grouping in `教学活动设计`; preserve blank-line grouping and the implicit four content blocks under each activity.
- The baseline activity blocks lack explicit `##### <hours>H` lines. The executor must map hours from the teaching-plan source or record a non-final, review-needed status rather than inventing.
- The baseline deliberately omits `total_hours`, `daily_hours`, term metadata, output lists, and validation settings from package YAML. Reintroducing these as teacher-maintained YAML fields would violate v1.13 even if rendering succeeds.
- `validate_package()` is shared by multiple package commands. Add baseline support without breaking the old package shape unless the implementation deliberately removes old mode with clear evidence.
- `render-package` must not report combined PDF success from Typst-only output.

## RESEARCH COMPLETE
