# Phase 20: Jiaoan Shicao 教案 1:1 Typst Conversion - Context

**Gathered:** 2026-06-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 20 updates only the `jiaoan-shicao` skill so `test/1.10/电气设备控制线路安装与调试教案.md` can be converted by code under `skills/jiaoan-shicao/scripts/` into Typst that strictly matches `test/1.10/电气设备控制线路安装与调试教案.typ`.

The phase is a brownfield, fixture-backed renderer upgrade. It does not modify `skills/jiaoan-jihua/`, does not plan or execute Phase 21, and does not generalize arbitrary教案 Markdown beyond what is necessary for the provided教案 fixture.

</domain>

<decisions>
## Implementation Decisions

### Conversion Scope
- **D-01:** The required output is the committed target `.typ`, not merely a visually similar or semantically close Typst file.
- **D-02:** The final generation command must invoke only code under `skills/jiaoan-shicao/scripts/`; no external Presto renderer, PDF compiler, template binary, or script from another skill may participate in Markdown-to-Typst generation.
- **D-03:** Fixture-specific parsing and formatting logic is acceptable for Phase 20 if it lives inside `skills/jiaoan-shicao/` and is documented as v1.10 fixture support rather than a broad new renderer promise.

### Public Workflow Compatibility
- **D-04:** Preserve the existing public command surface of `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`, especially `example`, `render`, `manifest`, `info`, `version`, `--input`, `--typ`, `--expected-typ`, and `--calendar-output`.
- **D-05:** If the implementation adds helper files or a fixture-aware mode, the default `render --input <md> --typ <typ>` path must still work for the v1.10教案 fixture without requiring callers to invoke non-skill scripts.
- **D-06:** `SKILL.md` should remain a concise semantic entry point. Longer fixture and rendering details should go into `references/` or script comments/helpers, consistent with v1.9 decomposition guidance.

### Target Typst Shape
- **D-07:** The planner should treat the target file as a fixed Typst contract: imports/font constants, cover page, page margins, `section-title`, task-analysis tables, teaching-activity tables, page breaks, and evaluation tables are all part of the expected generated output.
- **D-08:** The Markdown source contains three repeated learning-task blocks. The implementation must preserve the target ordering and mapping for each task: `学习任务分析`, `教学活动设计`, and `学业评价`.
- **D-09:** The current generic Markdown-to-Typst output is insufficient. A quick status check showed `render --expected-typ` fails, with major differences in document prelude, cover page, tables, page breaks, and section layout.

### Verification
- **D-10:** Phase 20 must record strict evidence for generated教案 output against `test/1.10/电气设备控制线路安装与调试教案.typ`; preferred evidence is `--expected-typ` success plus a strict `diff -u` or hash comparison.
- **D-11:** Verification should use a generated output path outside the committed target fixture, then compare that generated file to the target. Do not overwrite the target `.typ` as the only proof.
- **D-12:** It is acceptable to compile or visually inspect PDF only as supplemental evidence; Typst text equivalence is the acceptance gate for this phase.

### Claude's Discretion
- Planner and executor may choose whether to keep `jiaoan-shicao.sh` monolithic or split skill-local helpers under `skills/jiaoan-shicao/scripts/`, as long as the public command surface and script-only boundary remain intact.
- Planner and executor may decide whether fixture-specific constants belong in Bash functions, data tables, or skill-local reference/template files, provided the conversion path still runs through `skills/jiaoan-shicao/scripts/`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planning
- `.planning/ROADMAP.md` — Phase 20 goal, success criteria, and Phase 20/21 separation.
- `.planning/REQUIREMENTS.md` — SHICAO-01 through SHICAO-04 and VERIFY-01 through VERIFY-03.
- `.planning/STATE.md` — active v1.10 state and current phase position.
- `.planning/PROJECT.md` — repository constraints: Markdown-first workflows, skill-local support files, entry weight discipline, and fixture-specific conversion boundary.

### Skill Files
- `skills/jiaoan-shicao/SKILL.md` — current public workflow, runtime adapter notes, safety boundary, and verification wording.
- `skills/jiaoan-shicao/references/format-and-rendering.md` — existing long-form format and renderer rules to update if behavior changes.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` — current Bash-only renderer and public command surface.
- `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md` — existing example intermediate contract.
- `skills/jiaoan-shicao/references/calendar.json` — support resource that should remain unaffected unless explicitly needed.

### Fixture Contract
- `test/1.10/电气设备控制线路安装与调试教案.md` — Phase 20 source Markdown fixture.
- `test/1.10/电气设备控制线路安装与调试教案.typ` — strict target Typst fixture.
- `test/1.10/电气设备控制线路安装与调试教案.pdf` — supplemental visual reference only; Typst equivalence remains primary.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`: already provides argument parsing, input/output validation, shell-only file copying, Markdown parsing basics, Typst escaping helpers, and `--expected-typ` line-by-line comparison.
- `skills/jiaoan-shicao/SKILL.md`: already documents script-only rendering and runtime adapter notes for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
- `skills/jiaoan-shicao/references/format-and-rendering.md`: appropriate home for detailed v1.10 fixture notes if the entry would otherwise become too heavy.

### Established Patterns
- v1.9 established that `SKILL.md` entries should stay light while long renderer behavior moves into skill-local references.
- Existing document skills use a Markdown intermediate before target output; Phase 20 should keep that source-to-Typst story rather than bypassing the Markdown fixture.
- Public command names and flags are expected to remain stable unless requirements explicitly authorize a breaking change.

### Integration Points
- The final user-facing command should be based on:

```bash
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input test/1.10/电气设备控制线路安装与调试教案.md \
  --typ <generated-output.typ> \
  --expected-typ test/1.10/电气设备控制线路安装与调试教案.typ
```

- A current baseline run generated `/private/tmp/gsd-phase20/generated.typ` but failed `--expected-typ`, confirming that implementation work remains for the planner/executor.

</code_context>

<specifics>
## Specific Ideas

- The target `.typ` begins with `#import "@preview/pointless-size:0.1.2": zh`, font constants, A4 page settings, a fixed cover page, and repeated table-heavy sections. These are not produced by the current generic renderer.
- The source Markdown has frontmatter plus three task blocks, each with `学习任务分析`, `教学活动设计`, and `学业评价`; headings and `##### <hours>` markers encode activity rows that the target Typst represents as fixed tables.
- `total_hours: "160H"` in Markdown appears as cover value `160` and task-analysis row values in the target; planner should account for normalization decisions like removing `H` where the fixture requires it.

</specifics>

<deferred>
## Deferred Ideas

- Generalizing arbitrary third-party教案 Markdown into this exact Typst template belongs to a later milestone.
- Introducing shared jiaoan rendering infrastructure across `jiaoan-shicao` and `jiaoan-jihua` is explicitly deferred; Phase 20 and Phase 21 are independent.
- PDF visual acceptance is supplemental for v1.10 and can become a later milestone after strict Typst equivalence is stable.

</deferred>

---

*Phase: 20-Jiaoan Shicao 教案 1:1 Typst Conversion*
*Context gathered: 2026-06-14*
