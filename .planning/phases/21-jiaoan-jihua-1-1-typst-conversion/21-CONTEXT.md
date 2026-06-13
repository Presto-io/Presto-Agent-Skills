# Phase 21: Jiaoan Jihua 授课计划 1:1 Typst Conversion - Context

**Gathered:** 2026-06-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 21 updates only the existing `skills/jiaoan-jihua/` skill so the provided授课计划 Markdown fixture can be converted by skill-internal script code into Typst that strictly matches the committed target file at `test/1.10/电气设备控制线路安装与调试授课计划.typ`.

This phase is independent from Phase 20. Do not modify `skills/jiaoan-shicao/` or any Phase 20 implementation files.

</domain>

<decisions>
## Implementation Decisions

### Scope and Ownership
- **D-01:** Implementation scope is limited to `skills/jiaoan-jihua/SKILL.md`, `skills/jiaoan-jihua/references/`, `skills/jiaoan-jihua/scripts/`, and `skills/jiaoan-jihua/templates/` if needed.
- **D-02:** The final Markdown-to-Typst generation path must invoke code under `skills/jiaoan-jihua/scripts/`; it must not rely on renderer code outside the skill directory.
- **D-03:** Preserve the existing public workflow and command surface unless a narrow compatibility note is required. Existing commands such as `example`, `render`, `manifest`, `info`, and `version` should remain recognizable.
- **D-04:** Do not introduce shared jiaoan infrastructure in this phase. Cross-skill generalization is deferred by `JIAOAN-FUTURE-02`.

### Target Typst Shape
- **D-05:** Generated output must target the official table-style Typst fixture, not the current generic heading/paragraph renderer shape.
- **D-06:** The renderer needs to parse the existing Markdown structure into tasks, learning stages, content rows, and trailing hour markers, then emit the five-column table structure used by the target Typst.
- **D-07:** The target includes the official header, `cuti` fake-bold import/show rule, page/text/par settings, helper cell functions, metadata grid, table rows, and signature grid. Planning should treat these as required output details, not optional styling.

### Scheduling and Hours
- **D-08:** Use `first_teaching_day: "2026-05-11"`, `daily_hours: 8`, and `references/calendar.json` to derive the target week/day allocation.
- **D-09:** The source fixture's `-N` suffixes are lesson-hour counts and must drive row hours, task totals, rowspans, and multi-day/multi-week spans.
- **D-10:** Preserve source order: task order, stage order, and content row order should map directly into the target table.

### Verification
- **D-11:** Acceptance requires strict evidence against `test/1.10/电气设备控制线路安装与调试授课计划.typ`, preferably a clean `diff -u` plus a matching SHA-256 hash or equivalent byte-for-byte check.
- **D-12:** PDF visual acceptance is not part of Phase 21. It remains deferred until Typst strict equivalence is stable.
- **D-13:** Baseline evidence from discussion: current `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render` produces `/tmp/jiaoan-jihua-phase21-current.typ` with 204 lines and SHA-256 `0e332451a2abeaa16c660f8de928d19176f444676a8b607fc3d9fd7d1348256d`; target has 372 lines and SHA-256 `0d681cca76cb7d6edaf7b0c76874f3f8a5b3f49ab5e00904caf9a106690e138b`.

### Claude's Discretion
- The planner/executor may choose the exact internal parser and emitter organization inside `skills/jiaoan-jihua/scripts/`, as long as the public command surface, skill-local ownership, and strict target equivalence are preserved.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planning Scope
- `.planning/ROADMAP.md` — Phase 21 goal, success criteria, and Phase 20 independence.
- `.planning/REQUIREMENTS.md` — JIHUA-01 through JIHUA-04 and VERIFY-01 through VERIFY-03 acceptance requirements.
- `.planning/PROJECT.md` — Current milestone constraints and repository-level skill authoring expectations.
- `.planning/STATE.md` — Accumulated decisions, especially the v1.10 skill-internal conversion constraint.

### Existing Skill
- `skills/jiaoan-jihua/SKILL.md` — Public workflow, command examples, runtime adapter notes, outputs, verification, and safety boundaries.
- `skills/jiaoan-jihua/references/format-and-rendering.md` — Current frontmatter/body rules and renderer notes that should be updated if behavior changes.
- `skills/jiaoan-jihua/references/calendar.json` — Teaching calendar used to derive week/day scheduling from the fixture.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` — Current script entry point and Bash-only renderer.
- `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md` — Existing reviewable Markdown intermediate example.
- `docs/markdown-normalization-contract.md` — Repository-level Markdown intermediate contract for document workflow skills.

### Fixture Pair
- `test/1.10/电气设备控制线路安装与调试授课计划.md` — Source Markdown fixture for Phase 21.
- `test/1.10/电气设备控制线路安装与调试授课计划.typ` — Strict target Typst fixture for Phase 21.
- `test/1.10/电气设备控制线路安装与调试授课计划.pdf` — Reference PDF is available for context only; strict Typst equivalence is the Phase 21 gate.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`: Provides CLI parsing, frontmatter parsing, simple escaping helpers, `--expected-typ` comparison, and public commands. These are reusable but the renderer body is currently too generic for the official table fixture.
- `skills/jiaoan-jihua/references/calendar.json`: Contains ordered teaching dates including `2026-05-11` through the relevant weeks; use it to map daily hours into week/day values.
- `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md`: Mirrors the source fixture structure closely and can remain the example/update target for documentation.

### Established Patterns
- The skill follows the repository's Markdown-first document workflow: source material becomes a reviewable Markdown intermediate, then a skill-local script renders Typst.
- Long renderer details belong in `references/`; `SKILL.md` should stay concise and keep runtime adapter notes visible for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
- Current script comparison is black-box and line-based. Phase 21 should strengthen verification evidence with strict diff/hash commands in the plan/summary.

### Integration Points
- Primary implementation point: `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`.
- Documentation integration points: `skills/jiaoan-jihua/SKILL.md` and `skills/jiaoan-jihua/references/format-and-rendering.md` only if behavior or verification instructions change.
- Test/verification integration: generated output should be written to a temporary or phase-local path and compared with `test/1.10/电气设备控制线路安装与调试授课计划.typ`.

</code_context>

<specifics>
## Specific Ideas

- The target Typst begins with `// jiaoan-jihua official template`, imports `@preview/cuti:0.2.1`, and uses `STSong` at `10.5pt`; the generated file should match these bytes rather than approximate the visual layout.
- The target title line is `2025-2026学年第二学期第11 - 14周`, derived from the fixture's teaching calendar span.
- The target table uses columns `(3.15cm, 8.51cm, 1.12cm, 1.29cm, 1.27cm)` and helper cells `task-th`, `th`, `subth`, `body-cell`, and `content-cell`.
- Current baseline mismatch is structural: the existing renderer emits generic headings and paragraphs, while the target is one centered Typst table with rowspans and derived scheduling cells.

</specifics>

<deferred>
## Deferred Ideas

- Generalizing arbitrary third-party教案/授课计划 Markdown beyond this fixture remains deferred to `JIAOAN-FUTURE-01`.
- Shared rendering infrastructure across `jiaoan-shicao` and `jiaoan-jihua` remains deferred to `JIAOAN-FUTURE-02`.
- PDF visual acceptance for the v1.10 fixtures remains deferred to `JIAOAN-FUTURE-03`.

</deferred>

---

*Phase: 21-Jiaoan Jihua 授课计划 1:1 Typst Conversion*
*Context gathered: 2026-06-14*
