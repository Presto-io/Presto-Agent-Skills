---
phase: 30
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - skills/teaching-design-package/SKILL.md
  - skills/teaching-design-package/references/format-and-orchestration.md
  - skills/teaching-design-package/scripts/teaching-design-package.sh
autonomous: true
requirements: [TDPKG-01, TDPKG-02, TDPKG-03, TDPKG-15]
requirements_addressed: [TDPKG-01, TDPKG-02, TDPKG-03, TDPKG-15]
---

# Phase 30 Plan: Standalone Package-Owned Contract Boundary

<objective>
Correct `teaching-design-package` so the normal package path is self-contained and package-owned: unified Markdown -> package data model -> unified Typst -> three PDFs. Execution must not copy old standalone skill Markdown templates, must not create old-name internal directories, must not preserve old handoff architecture, and must not depend on legacy standalone skill folders for the normal standalone install path.
</objective>

<must_haves>
## Truths

- D-01: Do not copy old standalone skill Markdown templates into the package.
- D-02: Do not add package-internal directories that mirror old standalone skill names or old handoff layouts.
- D-03: Do not use old standalone handoff filenames, handoff naming, or old split-template naming as the package strategy.
- D-04: The package is the replacement user-facing integrated workflow for this use case, not a wrapper around hidden old skills.
- D-05: A standalone copy containing only `skills/teaching-design-package/` must support the normal verification path.
- D-06: Inputs are unified package Markdown files, either `teaching-design-package-full.md` or course-specific teaching-materials Markdown using the same contract.
- D-07: The package script must derive a package-owned data model from unified Markdown.
- D-08: Typst generation must be implemented from package-owned model data and package-owned rendering rules.
- D-09: Calendar/scheduling defaults must be defined by the package's own contract or explicitly configured package resources, never by sibling skill paths or mirrored old structures.
- D-10: Legacy standalone skills remain external compatibility surfaces and must not be deleted or renamed.
- D-11: Documentation may mention legacy standalone skills only generically as external compatibility surfaces.
- D-12: Standalone verification must not copy or invoke legacy standalone skill folders.
- D-13: This phase prepares the standalone implementation and must not absorb all Phase 31/32 work.
- D-14: The target delivery direction remains one unified Markdown, one unified Typst, and three PDFs.
- D-15: Debug artifacts, if any, must be package-owned and must avoid old handoff names and old internal directory names.
- D-16: User correction is locked; no new question is needed.
- D-17: Failed execute residue is invalid and must not guide the new plan.
</must_haves>

<tasks>
## Task 1: Replace old-handoff architecture with package-owned docs

<read_first>
- `AGENTS.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/30-standalone-skill-boundary-and-internalized-dependencies/30-CONTEXT.md`
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
</read_first>

<action>
Update `SKILL.md` and `references/format-and-orchestration.md` so the normal workflow is described as unified source Markdown parsed into a package-owned model and rendered by package-owned Typst/PDF logic. Remove instructions that tell users or agents to install, call, wrap, copy, or mentally stitch together legacy standalone skills. If legacy standalone skills must be mentioned, use only generic compatibility wording and make clear they are outside the package's normal path. Do not add package docs built around copying old templates, old split Markdown layouts, or old handoff architecture.
</action>

<acceptance_criteria>
- The blocked-token scan described in the verification section has no current v1.14 positive-requirement matches after execution.
- `rg 'skills/[a-z-]*|../[a-z-]*|standalone skills.*install|copy.*legacy' skills/teaching-design-package/SKILL.md skills/teaching-design-package/references/format-and-orchestration.md` exits non-zero unless the match explicitly describes external compatibility only.
- `rg 'Codex|Claude Code|Gemini CLI|OpenCode|OpenClaw|Hermes Agent' skills/teaching-design-package/SKILL.md` reports all six runtime names.
- `rg 'unified Markdown|package-owned|data model|Typst|PDF' skills/teaching-design-package/SKILL.md skills/teaching-design-package/references/format-and-orchestration.md` exits 0.
</acceptance_criteria>

## Task 2: Build a package-owned model from unified Markdown

<read_first>
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
</read_first>

<action>
Refactor the script so the package normalizes finalized unified Markdown into one package-owned model containing course metadata, schedule rows, activity rows, resource rows, derived hours, date facts, review markers, and output readiness. Use this model as the source for validation and rendering. Remove normal-path generation of old split Markdown and remove fallback copies from sibling skill templates. Keep CLI commands teacher-safe: `example`, validation/model inspection if present, and package rendering must operate on unified Markdown and package-owned outputs.
</action>

<acceptance_criteria>
- `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh` exits 0.
- `skills/teaching-design-package/scripts/teaching-design-package.sh example --output <tmp>/teaching-design-package-full.md` exits 0.
- The package script contains a package-owned normalization/render path whose identifiers do not use old handoff filenames or old internal directory names.
- Running the normal model/render preparation on the example Markdown does not require any sibling skill folder.
- `rg 'SKILL_DIR}/../|REPO_ROOT=.*/../..|skills/jiaoan' skills/teaching-design-package/scripts/teaching-design-package.sh` exits non-zero for the normal path.
</acceptance_criteria>

## Task 3: Generate package-owned Typst and PDF outputs

<read_first>
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
</read_first>

<action>
Implement package-owned Typst generation from the derived model. The renderer must produce a unified package Typst artifact and support the three PDF outputs required by the milestone direction. If some PDF compilation tools are unavailable locally, record honest failure or not-run status without falling back to legacy skill renderers. Do not expose old split artifacts as successful default delivery outputs.
</action>

<acceptance_criteria>
- `scripts/teaching-design-package.sh render-package --input <tmp>/teaching-design-package-full.md --out-dir <tmp>/out` exits 0 and writes a unified package Typst artifact.
- If `--pdf` is requested and a local compiler/merge tool is missing, the command records an honest non-final status and does not invoke legacy standalone skill scripts.
- Generated public output names follow the package 1+1+3 direction and avoid old handoff filenames.
- A scan of generated public outputs for repo paths and legacy dependency paths reports no normal-path leak.
</acceptance_criteria>

## Task 4: Preserve legacy standalone skills as external compatibility only

<read_first>
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- Legacy standalone skill entries only if needed for unchanged-surface verification.
</read_first>

<action>
Do not modify legacy standalone skill folders as part of implementing the package normal path. If regression evidence is useful, verify their public command surfaces remain unchanged through `git diff` and existing command smoke tests, but do not make those checks part of package standalone installation and do not use them as package parity baselines. Package documentation must frame legacy standalone skills as external compatibility only.
</action>

<acceptance_criteria>
- `git diff -- <legacy-plan-skill-path> <legacy-design-skill-path>` is empty unless the executor records an explicit out-of-scope reason and stops for user review.
- Package docs do not instruct a normal user to install or run legacy standalone skills.
- Package script normal path does not call legacy standalone skill scripts.
</acceptance_criteria>

## Task 5: Verify standalone copy using only the package folder

<read_first>
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `.planning/phases/30-standalone-skill-boundary-and-internalized-dependencies/30-PLAN.md`
</read_first>

<action>
Create verification evidence by copying only `skills/teaching-design-package/` into a temporary skill root and running the package's unified Markdown path there. The verification must prove the copied folder has its own docs, template, script, model derivation, and render boundary. It must not copy legacy standalone skill folders and must not rely on repo sibling paths. Record exact command outcomes in the Phase 30 summary during execute-phase.
</action>

<acceptance_criteria>
- A standalone verification command copies only `skills/teaching-design-package/` to a temporary skill root.
- In the standalone copy, `example` succeeds and the generated Markdown is the unified package Markdown.
- In the standalone copy, package validation/model preparation and Typst generation succeed or produce honest non-final status without sibling-path failures.
- The blocked-token scan described in the verification section has no current v1.14 positive-requirement matches.
- Standalone verification records that legacy standalone folders were not copied.
</acceptance_criteria>
</tasks>

<verification>
Run these checks after implementation:

```bash
legacy_full_pattern="$(printf '%s|%s|%s|%s|%s' \
  "$(printf '%s-%s-%s[.]%s' 'jiaoan' 'jihua' 'full' 'md')" \
  "$(printf '%s-%s-%s[.]%s' 'jiaoan' 'shicao' 'full' 'md')" \
  'internal/jiaoan' \
  'vendored' \
  'vendor')"
rg "$legacy_full_pattern" .planning/REQUIREMENTS.md .planning/ROADMAP.md .planning/STATE.md .planning/PROJECT.md .planning/phases/30-standalone-skill-boundary-and-internalized-dependencies

bash -n skills/teaching-design-package/scripts/teaching-design-package.sh

tmp_root="$(mktemp -d "${TMPDIR:-/tmp}/tdpkg-standalone-root.XXXXXX")"
mkdir -p "$tmp_root/skills"
cp -R skills/teaching-design-package "$tmp_root/skills/"
"$tmp_root/skills/teaching-design-package/scripts/teaching-design-package.sh" example \
  --output "$tmp_root/teaching-design-package-full.md"
"$tmp_root/skills/teaching-design-package/scripts/teaching-design-package.sh" render-package \
  --input "$tmp_root/teaching-design-package-full.md" \
  --out-dir "$tmp_root/out"
rg '../jiaoan|skills/jiaoan|/Presto-Agent-Skills' "$tmp_root/out" "$tmp_root"/*.log

git diff -- <legacy-plan-skill-path> <legacy-design-skill-path>
```

For the first `rg` check above, matches should be limited to the check command itself and this explanatory note; no current v1.14 positive requirements or Phase 30 planning prose may contain those blocked strings. Prefer using Chinese wording such as "禁止复制旧模板" and "禁止内嵌旧技能结构" instead of ambiguous English copy terms. For the standalone path-leak `rg`, a non-zero exit is the desired result. If the log glob has no files, rerun the path-leak scan against generated stdout/stderr captures from the standalone verification command.
</verification>

<success_criteria>
- `teaching-design-package` has a plan for a verified normal path when only its own folder is installed.
- The package implementation target is unified Markdown to package-owned data model to package-owned Typst/PDF rendering.
- No old standalone Markdown template copying, old handoff naming, or old-name internal directory structure is required or allowed.
- Legacy standalone skills remain external compatibility surfaces only and are not package internals, package resources, parity baselines, or future implementation direction.
- Six runtime adapters document the standalone package boundary.
- Legacy standalone skills remain external compatibility surfaces and unchanged.
</success_criteria>

<threat_model>
This phase is local documentation and shell-script packaging work. Primary risks are path confusion and contract confusion.

- Path confusion: the package could silently use sibling skill scripts on the developer machine and fail after standalone installation. Mitigation: standalone-copy verification must copy only the package folder and scan generated outputs for repo-path leaks.
- Contract confusion: old split handoff concepts could be reintroduced as package internals. Mitigation: blocked-token scans must fail the plan if old handoff filenames or old-name internal directory paths appear.
- Legacy regression: external compatibility surfaces could be accidentally edited. Mitigation: `git diff -- <legacy-plan-skill-path> <legacy-design-skill-path>` must remain empty unless the executor stops for explicit user review.
</threat_model>
