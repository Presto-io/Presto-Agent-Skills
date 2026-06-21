---
phase: 39-markdown-to-typst-renderer
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - skills/tiaokedan/scripts/tiaokedan.sh
  - skills/tiaokedan/scripts/tiaokedan_renderer.py
  - .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-missing-field.md
  - .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-table.md
  - .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-unsupported.md
  - .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ
  - .planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md
autonomous: true
requirements:
  - TKD-RENDER-01
  - TKD-RENDER-02
  - TKD-RENDER-03
  - TKD-RENDER-04
must_haves:
  truths:
    - "D-01: Phase 39 creates a skill-local command surface under `skills/tiaokedan/scripts/`; all runtime code lives inside `skills/tiaokedan/`."
    - "D-02: The public command supports `render --input <tiaokedan.md> --typ <output.typ>` and may support `--expected-typ <reference.typ>` for deterministic comparison."
    - "D-03: Phase 39 does not add `--pdf`, clean delivery directories, runtime adapter explanations, manifest/info commands, canonical skill workflow text, or README/index/discoverability updates."
    - "D-04: Evidence fixture input is `skills/tiaokedan/templates/tiaokedan.md`; accepted comparison reference is `skills/tiaokedan/templates/tiaokedan-reference.typ`."
    - "D-05: The renderer parses only the Phase 38 contract shape: YAML frontmatter, `## 调课说明`, recipient line, explanatory paragraph, one 8-column adjustment table, and closing department/date text."
    - "D-06: Table columns must be exactly `序号`, `班级`, `课程`, `原上课时间`, `原授课教师`, `调整后上课时间`, `调整后上课教师`, `备注` in that order."
    - "D-07: Required facts defined in `skills/tiaokedan/references/markdown-contract.md` must be non-empty after trimming; blank `备注` cells remain valid optional facts."
    - "D-08: Unresolved `{{待补充: ...}}` markers in required facts and `{{AI草稿: ...}}` markers in required output facts fail before Typst is accepted."
    - "D-09: `<br>` is the only supported authoring-level line-break marker and renders to Typst `#linebreak()`; unsupported inline HTML, raw Typst, or layout directives fail clearly."
    - "D-10: Generated Typst is deterministic: stable declarations, whitespace, row order, and no timestamps, random IDs, absolute temp paths, or environment-dependent comments."
    - "D-11: Accepted fixture generation should match `skills/tiaokedan/templates/tiaokedan-reference.typ` byte-for-byte if feasible; otherwise verification must document the exact normalized-equivalent rule."
    - "D-12: Deterministic checks use committed files and strict evidence such as `diff -u`, `cmp`, or SHA-256; PDF compile success is not the Phase 39 gate."
    - "D-13: The renderer never overwrites `tiaokedan-reference.typ`; generated output goes to an explicit output or phase evidence path."
    - "D-14: Missing files, malformed frontmatter/sections/table syntax, wrong columns, empty required cells, unresolved required markers, unsupported raw Typst/layout directives, and unsupported inline HTML exit non-zero."
    - "D-15: Error messages name the failing contract area and teacher-facing field where possible."
    - "D-16: Negative tests cover at least one missing-field case, one malformed-section/table case, and one unsupported-value case."
    - "D-17: Runtime independence is a hard gate: no calls to sibling skill scripts, no imports from sibling skill directories, and no requirement that other skills be installed."
    - "D-18: Borrowed patterns are implementation inspiration only; actual parser, renderer, comparison helper, and tests are skill-local or standard platform tools."
    - "D-19: Verification includes an independence assertion, including sibling skill path scans and a copied `skills/tiaokedan/`-only run if execution can keep it small."
  artifacts:
    - path: "skills/tiaokedan/scripts/tiaokedan.sh"
      provides: "skill-local public command wrapper for `render --input --typ [--expected-typ]`"
      contains: "render"
    - path: "skills/tiaokedan/scripts/tiaokedan_renderer.py"
      provides: "skill-local Markdown parser, validation, deterministic Typst renderer, and comparison helper"
      contains: "expected-typ"
    - path: ".planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ"
      provides: "generated Typst evidence from the accepted Markdown fixture"
      contains: "调课说明"
    - path: ".planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md"
      provides: "Phase 39 requirement, deterministic comparison, negative failure, and independence evidence"
      contains: "TKD-RENDER-04"
  key_links:
    - from: "skills/tiaokedan/templates/tiaokedan.md"
      to: "skills/tiaokedan/templates/tiaokedan-reference.typ"
      via: "skill-local renderer output comparison"
      pattern: "调课说明|#linebreak\\(\\)|电气工程系"
    - from: "skills/tiaokedan/references/markdown-contract.md"
      to: "skills/tiaokedan/scripts/tiaokedan_renderer.py"
      via: "required fields, optional `备注`, marker semantics, table column order, and unsupported syntax rules"
      pattern: "{{待补充: 说明}}|{{AI草稿: 说明}}|renderer-owned defaults"
    - from: ".planning/phases/39-markdown-to-typst-renderer/39-CONTEXT.md"
      to: ".planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md"
      via: "D-01 through D-19 decision coverage and Phase 40 scope boundary"
      pattern: "D-01|D-19|Phase 40"
---

<objective>
Implement the Phase 39 `调课单` skill-local Markdown-to-Typst renderer plan.

Purpose: enable `/gsd:execute-phase 39` to build a narrow, deterministic renderer that converts finalized `skills/tiaokedan/templates/tiaokedan.md` into generated Typst, verifies the generated source against the accepted Phase 37 reference, and fails non-zero for missing, malformed, or unsupported Markdown facts.
Output: a skill-local `skills/tiaokedan/scripts/` command, deterministic generated Typst evidence, negative fixtures, and `.planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md`.
</objective>

<execution_context>
@/Users/mrered/.codex/get-shit-done/workflows/execute-plan.md
@/Users/mrered/.codex/get-shit-done/templates/summary.md
</execution_context>

<context>
@AGENTS.md
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/STATE.md
@.planning/phases/37-typst-baseline/37-CONTEXT.md
@.planning/phases/37-typst-baseline/37-VERIFICATION.md
@.planning/phases/38-markdown-contract/38-CONTEXT.md
@.planning/phases/38-markdown-contract/38-VERIFICATION.md
@.planning/phases/39-markdown-to-typst-renderer/39-CONTEXT.md
@docs/directory-spec.md
@docs/markdown-normalization-contract.md
@skills/tiaokedan/templates/tiaokedan-reference.typ
@skills/tiaokedan/templates/tiaokedan.md
@skills/tiaokedan/references/markdown-contract.md

<interfaces>
This phase owns only the narrow renderer gate. `skills/tiaokedan/templates/tiaokedan.md` is the teacher-reviewed input contract from Phase 38. `skills/tiaokedan/templates/tiaokedan-reference.typ` is the accepted hand-authored Typst baseline from Phase 37. Phase 39 may create `skills/tiaokedan/scripts/` and phase-local evidence files, but must not modify `skills/tiaokedan/SKILL.md`, README/index/discoverability docs, runtime adapter notes, PDF workflow, clean delivery directories, or Phase 40 missing-information question guidance.
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add the skill-local renderer command and parser</name>
  <files>skills/tiaokedan/scripts/tiaokedan.sh, skills/tiaokedan/scripts/tiaokedan_renderer.py</files>
  <read_first>
    AGENTS.md
    docs/directory-spec.md
    docs/markdown-normalization-contract.md
    .planning/ROADMAP.md
    .planning/REQUIREMENTS.md
    .planning/phases/39-markdown-to-typst-renderer/39-CONTEXT.md
    skills/tiaokedan/templates/tiaokedan.md
    skills/tiaokedan/templates/tiaokedan-reference.typ
    skills/tiaokedan/references/markdown-contract.md
    skills/gongwen/scripts/gongwen_lib/commands.sh
    skills/teaching-design-package/scripts/teaching-design-package.sh
    If `skills/tiaokedan/scripts/` or either target file already exists at execution time, read the existing files before editing and preserve user-authored behavior unless it conflicts with D-01 through D-19.
  </read_first>
  <action>
    Create `skills/tiaokedan/scripts/tiaokedan.sh` as the skill-local public command wrapper for TKD-RENDER-01. The wrapper must live under `skills/tiaokedan/scripts/`, use repository-relative paths only for its own directory discovery, and dispatch only the subcommand `render`. It must accept the exact public shape `render --input <tiaokedan.md> --typ <output.typ>` and an optional `--expected-typ <reference.typ>` comparison flag. It must reject unknown subcommands and unknown flags with concise stderr and non-zero exit. It must call only the sibling local module `skills/tiaokedan/scripts/tiaokedan_renderer.py` plus standard platform commands; it must not call `skills/gongwen/`, `skills/teaching-design-package/`, `skills/jiaoan-*`, or any other sibling skill path.

    Create `skills/tiaokedan/scripts/tiaokedan_renderer.py` as a narrow Phase 39 renderer for TKD-RENDER-01, TKD-RENDER-02, TKD-RENDER-03, and TKD-RENDER-04. Use only Python standard library modules. Implement `render` argument parsing for `--input`, `--typ`, and optional `--expected-typ`. Parse YAML frontmatter narrowly enough for the accepted fixture fields `title`, `recipient`, `department`, and `date`; reject missing frontmatter, malformed frontmatter delimiters, missing required fields, and empty required values. Parse the body shape required by Phase 38: `## 调课说明`, the visible recipient line, the explanatory paragraph, one Markdown adjustment table, and closing department/date text. Validate the adjustment table has exactly these headers in this order: `序号`, `班级`, `课程`, `原上课时间`, `原授课教师`, `调整后上课时间`, `调整后上课教师`, `备注`. Validate every required table cell is non-empty after trimming; allow blank `备注`.

    Implement final-Markdown marker validation: unresolved `{{待补充: ...}}` in required facts fails non-zero; `{{AI草稿: ...}}` in required output facts also fails non-zero for Phase 39. Implement unsupported-syntax validation for teacher-maintained fields: allow plain text and `<br>` only; reject other inline HTML tags, raw Typst markers such as `#set`, `#let`, `#table`, `#linebreak()`, `#page`, `#align`, and layout/config-like directives. Convert `<br>` in table cells to Typst `#linebreak()` in the generated Typst.

    Generate deterministic Typst by reproducing the stable structure of `skills/tiaokedan/templates/tiaokedan-reference.typ`: same helper declarations, A4 landscape page setup, font fallback declarations, body/table/signature structure, accepted strings, row order, whitespace policy, and no timestamps, random IDs, absolute paths, or environment-dependent comments. Do not overwrite `skills/tiaokedan/templates/tiaokedan-reference.typ`; write only to the explicit `--typ` path. If `--expected-typ` is provided, compare the generated Typst to that file byte-for-byte by default. If byte-for-byte is impossible during execution, implement a named narrow normalization function only if it is documented in `39-VERIFICATION.md` with the exact ignored differences; prefer byte-for-byte.
  </action>
  <verify>
    <automated>test -x skills/tiaokedan/scripts/tiaokedan.sh</automated>
    <automated>test -s skills/tiaokedan/scripts/tiaokedan_renderer.py</automated>
    <automated>python3 -m py_compile skills/tiaokedan/scripts/tiaokedan_renderer.py</automated>
    <automated>skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ --expected-typ skills/tiaokedan/templates/tiaokedan-reference.typ</automated>
    <automated>test -s .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ</automated>
    <automated>cmp -s .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ skills/tiaokedan/templates/tiaokedan-reference.typ</automated>
    <automated>rg -F '#linebreak()' .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ && rg -F '调课说明' .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ && rg -F '电气工程系' .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ</automated>
    <automated>! rg 'skills/(gongwen|teaching-design-package|jiaoan-|end-of-term|school-presentation)' skills/tiaokedan/scripts/tiaokedan.sh skills/tiaokedan/scripts/tiaokedan_renderer.py</automated>
  </verify>
  <acceptance_criteria>
    `skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ --expected-typ skills/tiaokedan/templates/tiaokedan-reference.typ` exits 0. The generated Typst is deterministic and byte-for-byte equal to the accepted reference unless `39-VERIFICATION.md` documents an explicitly narrower normalized-equivalent comparison. Renderer code is skill-local and has no sibling skill runtime references.
  </acceptance_criteria>
  <done>Skill-local render command converts the accepted Markdown fixture to deterministic Typst and optionally compares it against the accepted reference.</done>
</task>

<task type="auto">
  <name>Task 2: Add negative fixtures and non-zero failure checks</name>
  <files>.planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-missing-field.md, .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-table.md, .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-unsupported.md, .planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md</files>
  <read_first>
    .planning/phases/39-markdown-to-typst-renderer/39-CONTEXT.md
    skills/tiaokedan/templates/tiaokedan.md
    skills/tiaokedan/references/markdown-contract.md
    skills/tiaokedan/scripts/tiaokedan.sh
    skills/tiaokedan/scripts/tiaokedan_renderer.py
    If any `.planning/phases/39-markdown-to-typst-renderer/fixtures/*.md` fixture exists at execution time, read it before editing and preserve useful negative coverage unless it conflicts with D-14 through D-16.
  </read_first>
  <action>
    Create three phase-local negative fixtures for TKD-RENDER-04. Keep them under `.planning/phases/39-markdown-to-typst-renderer/fixtures/` so they do not become teacher-facing templates or Phase 40 delivery artifacts.

    Create `invalid-missing-field.md` by copying the accepted fixture shape but making one required field fail; prefer removing or blanking `department`, or replacing one required time cell with `{{待补充: 原上课时间}}`. The renderer must exit non-zero and stderr must name the required area, for example `missing required frontmatter field: department` or `unresolved required marker in row 1 原上课时间`.

    Create `invalid-table.md` by copying the accepted fixture shape but changing the adjustment table structure, such as removing `调整后上课教师` or reordering the locked 8-column header. The renderer must exit non-zero and stderr must name the malformed table area, for example `malformed adjustment table: expected 8 columns` or `malformed adjustment table: unexpected columns`.

    Create `invalid-unsupported.md` by copying the accepted fixture shape but adding unsupported teacher-maintained syntax, such as raw Typst `#linebreak()` in a table cell or unsupported inline HTML `<span>...</span>` in a required field. The renderer must exit non-zero and stderr must identify unsupported syntax or unsupported inline HTML. Do not add interactive questions; Phase 40 owns missing-information question guidance.

    In `39-VERIFICATION.md`, reserve a command-log section that records the negative commands, exit behavior, and stderr snippets for the three cases. The commands must use explicit output paths under `.planning/phases/39-markdown-to-typst-renderer/generated/` and must not overwrite the accepted reference.
  </action>
  <verify>
    <automated>test -s .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-missing-field.md</automated>
    <automated>test -s .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-table.md</automated>
    <automated>test -s .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-unsupported.md</automated>
    <automated>! skills/tiaokedan/scripts/tiaokedan.sh render --input .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-missing-field.md --typ .planning/phases/39-markdown-to-typst-renderer/generated/invalid-missing-field.typ 2>.planning/phases/39-markdown-to-typst-renderer/generated/invalid-missing-field.stderr</automated>
    <automated>! skills/tiaokedan/scripts/tiaokedan.sh render --input .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-table.md --typ .planning/phases/39-markdown-to-typst-renderer/generated/invalid-table.typ 2>.planning/phases/39-markdown-to-typst-renderer/generated/invalid-table.stderr</automated>
    <automated>! skills/tiaokedan/scripts/tiaokedan.sh render --input .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-unsupported.md --typ .planning/phases/39-markdown-to-typst-renderer/generated/invalid-unsupported.typ 2>.planning/phases/39-markdown-to-typst-renderer/generated/invalid-unsupported.stderr</automated>
    <automated>rg 'missing required|unresolved required marker' .planning/phases/39-markdown-to-typst-renderer/generated/invalid-missing-field.stderr</automated>
    <automated>rg 'malformed adjustment table|expected 8 columns|unexpected columns' .planning/phases/39-markdown-to-typst-renderer/generated/invalid-table.stderr</automated>
    <automated>rg 'unsupported inline HTML|unsupported raw Typst|unsupported syntax' .planning/phases/39-markdown-to-typst-renderer/generated/invalid-unsupported.stderr</automated>
  </verify>
  <acceptance_criteria>
    Phase-local negative fixtures prove the renderer exits non-zero for at least one missing-field or unresolved-marker case, one malformed table case, and one unsupported-value/syntax case. Each stderr message is concise and names the failing contract area or teacher-facing field where possible.
  </acceptance_criteria>
  <done>Negative fixtures and commands cover TKD-RENDER-04 without adding Phase 40 question guidance.</done>
</task>

<task type="auto">
  <name>Task 3: Record deterministic comparison and independence evidence</name>
  <files>.planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md, .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ</files>
  <read_first>
    .planning/ROADMAP.md
    .planning/REQUIREMENTS.md
    .planning/phases/39-markdown-to-typst-renderer/39-CONTEXT.md
    skills/tiaokedan/templates/tiaokedan.md
    skills/tiaokedan/templates/tiaokedan-reference.typ
    skills/tiaokedan/references/markdown-contract.md
    skills/tiaokedan/scripts/tiaokedan.sh
    skills/tiaokedan/scripts/tiaokedan_renderer.py
    All negative fixtures created in Task 2.
    If `.planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md` already exists at execution time, read it before editing and update Phase 39 evidence without deleting unrelated user notes.
  </read_first>
  <action>
    Create `.planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md` as the execution evidence file for TKD-RENDER-01, TKD-RENDER-02, TKD-RENDER-03, and TKD-RENDER-04. Include sections for source paths, requirement coverage, D-01 through D-19 decision coverage, public command evidence, deterministic comparison evidence, negative failure evidence, runtime independence evidence, and explicit Phase 40 non-goals.

    Run the positive render command and record the exact command, exit code, generated output path, and comparison method. Prefer byte-for-byte evidence with `cmp -s`, `diff -u skills/tiaokedan/templates/tiaokedan-reference.typ .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ`, and `shasum -a 256` for both files. If normalized comparison is used instead, document the normalization command or function name, exactly what it ignores, and why byte-for-byte could not be achieved. Do not treat Typst PDF compilation as the required Phase 39 gate.

    Run the three negative commands from Task 2 and record non-zero behavior plus stderr snippets. Run independence checks that prove runtime execution does not require sibling skills: scan `skills/tiaokedan/scripts/` for sibling skill path references, run the positive command from a temporary copied directory containing only `skills/tiaokedan/` and standard tools if this can be done without broad repo copying, and record the command/result. The copied-only check should create a temporary root under `/tmp` or `.planning/tmp/`, copy only `skills/tiaokedan/`, run `skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ /tmp/tiaokedan-only.generated.typ --expected-typ skills/tiaokedan/templates/tiaokedan-reference.typ`, and record success or the exact blocker.

    Add explicit negative scope evidence proving Phase 39 did not modify or create `skills/tiaokedan/SKILL.md`, README/index/discoverability docs, `docs/compatibility-matrix.md`, runtime adapter files, final PDF workflow, clean teacher-facing delivery directory, manifest/info commands, missing-information question docs, school-specific variants, batch generation, spreadsheet import, approval grids, signature boxes, or opinion columns.
  </action>
  <verify>
    <automated>test -s .planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md</automated>
    <automated>rg -F 'TKD-RENDER-01' .planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md && rg -F 'TKD-RENDER-02' .planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md && rg -F 'TKD-RENDER-03' .planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md && rg -F 'TKD-RENDER-04' .planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md</automated>
    <automated>for token in D-01 D-02 D-03 D-04 D-05 D-06 D-07 D-08 D-09 D-10 D-11 D-12 D-13 D-14 D-15 D-16 D-17 D-18 D-19; do rg -F "$token" .planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md >/dev/null || exit 1; done</automated>
    <automated>skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ --expected-typ skills/tiaokedan/templates/tiaokedan-reference.typ</automated>
    <automated>diff -u skills/tiaokedan/templates/tiaokedan-reference.typ .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ</automated>
    <automated>shasum -a 256 skills/tiaokedan/templates/tiaokedan-reference.typ .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ</automated>
    <automated>! rg 'skills/(gongwen|teaching-design-package|jiaoan-|end-of-term|school-presentation)' skills/tiaokedan/scripts .planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md</automated>
    <automated>! git diff --name-only -- README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md skills/tiaokedan/SKILL.md | rg .</automated>
  </verify>
  <acceptance_criteria>
    `39-VERIFICATION.md` proves all four Phase 39 requirements, covers D-01 through D-19, records positive deterministic comparison evidence, records three negative non-zero failure cases, and records runtime independence plus Phase 40 scope-boundary evidence. No Phase 40-owned file is modified.
  </acceptance_criteria>
  <done>Phase 39 evidence is complete enough for verify-work to confirm renderer behavior, deterministic comparison, failure semantics, and independence.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Teacher-reviewed Markdown -> renderer parser | The renderer consumes a human-maintained Markdown contract and must reject malformed, missing, or non-final facts instead of guessing. |
| Renderer output -> accepted Typst reference | Generated Typst must be deterministic and compared against the Phase 37 accepted baseline without overwriting it. |
| `tiaokedan` skill runtime -> sibling skill folders | Runtime code may borrow ideas from existing skills but must not call or import sibling skill scripts/directories. |
| Phase 39 scope -> Phase 40 scope | Renderer work must not leak into PDF workflow, canonical `SKILL.md`, runtime adapter notes, README/index, clean delivery, or question guidance. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-39-01 | Tampering | `skills/tiaokedan/templates/tiaokedan.md` input parsing | mitigate | Validate exact frontmatter, body sections, table columns, required values, and marker semantics before writing Typst. |
| T-39-02 | Tampering | generated Typst evidence | mitigate | Write only to explicit `--typ` paths, never overwrite `tiaokedan-reference.typ`, and compare with `cmp`/`diff`/SHA-256. |
| T-39-03 | Repudiation | deterministic comparison | mitigate | Record exact positive command, comparison method, hashes, and any normalization rule in `39-VERIFICATION.md`. |
| T-39-04 | Information Disclosure | diagnostics and temporary outputs | mitigate | Keep evidence and negative fixtures in `.planning/phases/39-markdown-to-typst-renderer/`; do not introduce public delivery directories or Phase 40 clean-output claims. |
| T-39-05 | Elevation of Privilege | sibling skill runtime dependency | mitigate | Scan renderer files for sibling skill path references and run a copied `skills/tiaokedan/`-only positive command where feasible. |
| T-39-06 | Denial of Service | malformed teacher input | mitigate | Fail fast with concise stderr for missing files, malformed frontmatter, malformed tables, unsupported inline HTML/raw Typst, and unresolved markers. |
| T-39-SC | Tampering | package installs, network calls, external services | mitigate | No package-manager installs, network calls, external services, PDF compilation requirement, or sibling skill scripts are needed or allowed for Phase 39. |
</threat_model>

<verification>
Overall phase checks:

1. `test -x skills/tiaokedan/scripts/tiaokedan.sh`
2. `test -s skills/tiaokedan/scripts/tiaokedan_renderer.py`
3. `python3 -m py_compile skills/tiaokedan/scripts/tiaokedan_renderer.py`
4. `skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ --expected-typ skills/tiaokedan/templates/tiaokedan-reference.typ`
5. `test -s .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ`
6. `diff -u skills/tiaokedan/templates/tiaokedan-reference.typ .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ`
7. `shasum -a 256 skills/tiaokedan/templates/tiaokedan-reference.typ .planning/phases/39-markdown-to-typst-renderer/generated/tiaokedan.generated.typ`
8. `test -s .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-missing-field.md`
9. `test -s .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-table.md`
10. `test -s .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-unsupported.md`
11. `! skills/tiaokedan/scripts/tiaokedan.sh render --input .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-missing-field.md --typ .planning/phases/39-markdown-to-typst-renderer/generated/invalid-missing-field.typ 2>.planning/phases/39-markdown-to-typst-renderer/generated/invalid-missing-field.stderr`
12. `! skills/tiaokedan/scripts/tiaokedan.sh render --input .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-table.md --typ .planning/phases/39-markdown-to-typst-renderer/generated/invalid-table.typ 2>.planning/phases/39-markdown-to-typst-renderer/generated/invalid-table.stderr`
13. `! skills/tiaokedan/scripts/tiaokedan.sh render --input .planning/phases/39-markdown-to-typst-renderer/fixtures/invalid-unsupported.md --typ .planning/phases/39-markdown-to-typst-renderer/generated/invalid-unsupported.typ 2>.planning/phases/39-markdown-to-typst-renderer/generated/invalid-unsupported.stderr`
14. `rg 'missing required|unresolved required marker' .planning/phases/39-markdown-to-typst-renderer/generated/invalid-missing-field.stderr`
15. `rg 'malformed adjustment table|expected 8 columns|unexpected columns' .planning/phases/39-markdown-to-typst-renderer/generated/invalid-table.stderr`
16. `rg 'unsupported inline HTML|unsupported raw Typst|unsupported syntax' .planning/phases/39-markdown-to-typst-renderer/generated/invalid-unsupported.stderr`
17. `test -s .planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md`
18. `for req in TKD-RENDER-01 TKD-RENDER-02 TKD-RENDER-03 TKD-RENDER-04; do rg -F "$req" .planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md >/dev/null || exit 1; done`
19. `for d in D-01 D-02 D-03 D-04 D-05 D-06 D-07 D-08 D-09 D-10 D-11 D-12 D-13 D-14 D-15 D-16 D-17 D-18 D-19; do rg -F "$d" .planning/phases/39-markdown-to-typst-renderer/39-VERIFICATION.md >/dev/null || exit 1; done`
20. `! rg 'skills/(gongwen|teaching-design-package|jiaoan-|end-of-term|school-presentation)' skills/tiaokedan/scripts`
21. `! git diff --name-only -- README.md skills/README.md docs/directory-spec.md docs/compatibility-matrix.md skills/tiaokedan/SKILL.md | rg .`
</verification>

<success_criteria>
- TKD-RENDER-01: `skills/tiaokedan/scripts/tiaokedan.sh render --input skills/tiaokedan/templates/tiaokedan.md --typ <output.typ>` converts finalized Markdown into generated Typst.
- TKD-RENDER-02: Runtime execution is independent and uses only `skills/tiaokedan/` code plus standard platform tools; no sibling skill script or directory is required.
- TKD-RENDER-03: Generated Typst is deterministically compared against `skills/tiaokedan/templates/tiaokedan-reference.typ` with byte-for-byte evidence or a documented narrow normalized-equivalent rule.
- TKD-RENDER-04: Missing required fields, malformed sections/tables, and unsupported values/syntax fail non-zero with clear stderr.
- Scope boundary: Phase 40-owned files and workflows remain untouched.
</success_criteria>

<source_audit>
| SOURCE | ID | Feature/Requirement | Plan | Status | Notes |
|--------|----|---------------------|------|--------|-------|
| GOAL | — | Convert finalized Markdown into the accepted Typst form using only skill-local runtime code. | 39-01 | COVERED | Tasks 1 and 3 create and verify the renderer/comparison path. |
| REQ | TKD-RENDER-01 | Skill-local command converts finalized Markdown into Typst. | 39-01 | COVERED | Task 1 creates `tiaokedan.sh render --input --typ`. |
| REQ | TKD-RENDER-02 | Renderer is runtime independent from sibling skills. | 39-01 | COVERED | Task 1 forbids sibling calls; Task 3 records scan and copied-only evidence. |
| REQ | TKD-RENDER-03 | Generated Typst verifies against the hand-authored reference through deterministic checks. | 39-01 | COVERED | Task 1 implements optional `--expected-typ`; Task 3 records `diff`/hash evidence. |
| REQ | TKD-RENDER-04 | Renderer reports clear non-zero failures for missing, malformed, or unsupported input. | 39-01 | COVERED | Task 2 creates and verifies three negative fixtures. |
| CONTEXT | D-01 | Create skill-local command surface under `skills/tiaokedan/scripts/`. | 39-01 | COVERED | Task 1. |
| CONTEXT | D-02 | Support `render --input <tiaokedan.md> --typ <output.typ>` and optional `--expected-typ`. | 39-01 | COVERED | Task 1. |
| CONTEXT | D-03 | Avoid `--pdf`, delivery dirs, adapters, manifest/info, and canonical workflow text. | 39-01 | COVERED | Task 3 negative scope checks. |
| CONTEXT | D-04 | Use accepted fixture and reference paths for evidence. | 39-01 | COVERED | Tasks 1 and 3. |
| CONTEXT | D-05 | Parse YAML frontmatter, `## 调课说明`, recipient, paragraph, table, closing department/date. | 39-01 | COVERED | Task 1. |
| CONTEXT | D-06 | Enforce fixed 8-column order. | 39-01 | COVERED | Task 1 and malformed-table fixture. |
| CONTEXT | D-07 | Enforce required facts; allow blank `备注`. | 39-01 | COVERED | Task 1. |
| CONTEXT | D-08 | Fail unresolved required markers and AI-draft markers in required facts. | 39-01 | COVERED | Task 1 and missing-field fixture. |
| CONTEXT | D-09 | Support only `<br>` as line-break marker; fail raw Typst/layout/unsupported HTML. | 39-01 | COVERED | Task 1 and unsupported fixture. |
| CONTEXT | D-10 | Generate deterministic Typst. | 39-01 | COVERED | Task 1 and hash/diff evidence. |
| CONTEXT | D-11 | Prefer byte-for-byte reference match; document normalization only if unavoidable. | 39-01 | COVERED | Task 3. |
| CONTEXT | D-12 | Use deterministic local source checks; PDF compile is not required gate. | 39-01 | COVERED | Task 3. |
| CONTEXT | D-13 | Never overwrite hand-authored reference. | 39-01 | COVERED | Task 1 and verification output paths. |
| CONTEXT | D-14 | Missing/malformed/unsupported cases exit non-zero. | 39-01 | COVERED | Task 2. |
| CONTEXT | D-15 | Error messages name failing contract area/field. | 39-01 | COVERED | Task 2 stderr checks. |
| CONTEXT | D-16 | Negative tests cover missing-field, malformed-table, and unsupported-value cases. | 39-01 | COVERED | Task 2. |
| CONTEXT | D-17 | Hard runtime independence gate. | 39-01 | COVERED | Task 3 independence checks. |
| CONTEXT | D-18 | Borrowed patterns are inspiration only; implementation is skill-local/standard tools. | 39-01 | COVERED | Task 1. |
| CONTEXT | D-19 | Verification includes sibling path scans and copied-only run when feasible. | 39-01 | COVERED | Task 3. |
</source_audit>

<output>
Create `.planning/phases/39-markdown-to-typst-renderer/39-01-SUMMARY.md` when done.
</output>
