# Phase 18: Script Module Decomposition - Context

**Gathered:** 2026-06-13
**Status:** Ready for planning
**Source:** `gsd discuss phase 18` equivalent, executed inline in Codex runtime

<domain>
## Phase Boundary

Phase 18 decomposes the largest current script entry points into smaller internal modules or support scripts with clear ownership boundaries. The split should reduce maintenance and review cost for CLI dispatch, parsing, rendering, artifact writing, verification, and reporting helpers where appropriate.

This phase covers SD-05 through SD-08 only. It must preserve public command names, common flags, default output paths, manifest keys, Markdown intermediate contracts, generated artifact names, and user-facing invocation patterns. It does not perform Phase 19 contributor-documentation review, milestone audit, milestone closeout, or broad feature expansion.

</domain>

<decisions>
## Implementation Decisions

### Target Selection

- **D-01:** Prioritize the largest script entry points by current size and responsibility density: `skills/school-presentation/scripts/school-presentation.sh` (4940 lines), `skills/end-of-term-teaching-materials/scripts/render_package.py` (1971 lines), and `skills/gongwen/scripts/gongwen.sh` (1251 lines).
- **D-02:** Treat `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` and `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` as secondary. They may receive only low-risk shared-helper extraction if it follows naturally from real duplication; they are not the primary decomposition targets.
- **D-03:** Do not count ignored `__pycache__` artifacts as script targets. They are generated validation byproducts, not source modules.

### Public Interface Stability

- **D-04:** Preserve the existing shell entry-point filenames and command names. Downstream users should still call `school-presentation.sh`, `end-of-term-teaching-materials.sh`, and `gongwen.sh` with the same commands they use today.
- **D-05:** Preserve common flags and current defaults: examples include `school-presentation.sh render --input --html --manifest --max-size-mb`, `school-presentation.sh verify --workdir`, `school-presentation.sh bookmark-pdf --pdf --manifest --output`, `end-of-term-teaching-materials.sh render --input --workdir --pdf --abnormal-review`, and `gongwen.sh render --input --typ --pdf --expected-typ`.
- **D-06:** Preserve printed status lines and generated artifact contracts unless a plan explicitly proves a compatibility-neutral mechanical relocation. The expected result is smaller source files, not changed behavior.

### Module Boundaries

- **D-07:** Split by existing responsibility clusters rather than by arbitrary line count. Preferred boundaries are CLI dispatch, input/frontmatter parsing, Markdown block parsing, rendering, embedded playback/export JavaScript and CSS, artifact writing, verification/reporting, and optional PDF/bookmark helpers.
- **D-08:** For `school-presentation.sh`, keep the shell wrapper as the public command surface and move Python implementation into skill-local Python modules under `scripts/` only if the command still works through the existing shell file. The embedded browser JavaScript/CSS may be extracted only if rendering remains offline and deterministic.
- **D-09:** For `render_package.py`, prefer Python module extraction around data validation, Markdown conversion/parsing, Typst page generation, table/workbook artifact writing, and verification. Keep `end-of-term-teaching-materials.sh` as the stable wrapper.
- **D-10:** For `gongwen.sh`, use extra caution: it is Bash-only by design. Decomposition should not silently convert the public implementation to Python or require a new runtime. Bash helper sourcing or a skill-local support script is acceptable only if `gongwen.sh` remains the command users run.

### Shared Behavior

- **D-11:** Extract shared behavior only where there is real duplication or a stable contract, such as repeated Bash CLI helper functions, parent-directory checks, file-copy helpers, or renderer smoke-test utilities. Do not create a broad global framework for hypothetical future skills.
- **D-12:** Any shared support must remain runtime-neutral and repository-local. Do not introduce Codex-, Claude-, OpenClaw-, Hermes-, or other agent-private syntax into canonical skill bodies or script interfaces.

### Verification Expectations

- **D-13:** Planning should include before/after checks for command help, script syntax, representative render/verify commands, manifest key stability, and artifact filename stability for every decomposed target.
- **D-14:** Verification should compare behavior through public shell commands, not by importing private modules directly. Private-module tests are allowed as additional safety, but the public contract is the acceptance gate.

### Claude's Discretion

- Exact module filenames, Python package layout, and Bash helper-file boundaries are left to implementation judgment, provided they are skill-local, descriptive, and keep the current command surface stable.
- If a target proves too risky for full decomposition in one plan, prefer a smaller vertical split with strong compatibility evidence over a broad rewrite.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope

- `.planning/ROADMAP.md` — Phase 18 goal, success criteria, dependencies, and Phase 19 boundary.
- `.planning/REQUIREMENTS.md` — SD-05 through SD-08 and v1.9 out-of-scope rules.
- `.planning/STATE.md` — Current v1.9 position and accumulated decisions about command-surface preservation.
- `AGENTS.md` — Repository editing rules, language rule, directory conventions, and no private runtime syntax in canonical skills.

### Dependency Context

- `.planning/phases/17-skill-entry-and-reference-decomposition/17-CONTEXT.md` — Confirms Phase 17 stopped before script decomposition and preserved public script interfaces.
- `.planning/phases/17-skill-entry-and-reference-decomposition/17-01-SUMMARY.md` — Lists Phase 17 affected files and verifies no script internals were edited.
- `.planning/phases/17-skill-entry-and-reference-decomposition/17-VERIFICATION.md` — Confirms Phase 17 passed and explicitly left Phase 18 script work untouched.

### Script Targets

- `skills/school-presentation/scripts/school-presentation.sh` — Largest script target; public commands are `example`, `render`, `verify`, `bookmark-pdf`, and `info`.
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh` — Stable public wrapper for the end-of-term skill.
- `skills/end-of-term-teaching-materials/scripts/render_package.py` — Large Python implementation behind the end-of-term wrapper.
- `skills/gongwen/scripts/gongwen.sh` — Bash-only Markdown-to-Typst renderer and third largest current script target.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` — Smaller Bash renderer with repeated helper patterns; secondary target only.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh` — Smaller Bash renderer with repeated helper patterns; secondary target only.

### Artifact Contracts

- `skills/school-presentation/templates/school-presentation-full.md` — Representative presentation input used by `example` and `verify`.
- `skills/school-presentation/references/verification-contract.md` — Current presentation verification expectations and manifest behavior.
- `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md` — End-of-term workflow and generated artifact contract.
- `skills/gongwen/references/format-and-rendering.md` — Gongwen Markdown/Typst rendering expectations.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `skills/*/scripts/*.sh`: Existing public shell entry points provide the compatibility layer that should survive module extraction.
- `skills/end-of-term-teaching-materials/scripts/render_package.py`: Already has `argparse` command dispatch and many pure Python functions that can be grouped into modules.
- Existing skill-local `references/` files from Phase 17 document artifact contracts; use them to avoid rediscovering output expectations from code alone.

### Established Patterns

- Skills expose a small shell command surface even when implementation detail is large.
- Document workflow skills use Markdown as the reviewable intermediate before Typst/PDF or other artifacts.
- Verification currently runs through public commands such as `verify`, `render`, `manifest`, `info`, and `version`.
- Runtime adapter differences belong in `SKILL.md` adapter notes, not inside scripts or private command syntax.

### Integration Points

- `school-presentation.sh` embeds a large Python renderer inside a Bash heredoc, then embeds HTML/CSS/JavaScript inside the generated offline deck. Module extraction must preserve single-file HTML output and deterministic manifests.
- `end-of-term-teaching-materials.sh` delegates to `render_package.py`; this already creates a clean wrapper/implementation split that Phase 18 can deepen inside Python.
- `gongwen.sh` currently owns parsing, rendering, artifact writing, and command dispatch in Bash. Extraction should keep the Bash-only contract visible because the skill documentation presents that as intentional.

</code_context>

<specifics>
## Specific Ideas

- Keep Phase 18 as a structural refactor, not a behavior milestone.
- Prefer narrow, reviewable module moves with regression checks after each major target.
- Treat `school-presentation.sh` as the highest-risk target because it contains CLI dispatch, renderer logic, verification logic, and embedded playback/export UI in one file.
- Treat `render_package.py` as the most straightforward Python module split because it already has typed functions and clear clusters.
- Treat `gongwen.sh` as a compatibility-sensitive Bash split; preserving the Bash-only command contract matters more than making it look like the Python skills.

</specifics>

<deferred>
## Deferred Ideas

- README skills index, compatibility matrix review, before/after milestone evidence, and milestone audit are Phase 19 unless a narrow Phase 18 script-interface note is required to keep a changed module layout discoverable.
- New skill capabilities, new output formats, hosted presentation features, or office-suite automation are out of scope for v1.9 and should not be folded into this refactor.

</deferred>

---

*Phase: 18-Script Module Decomposition*
*Context gathered: 2026-06-13*
