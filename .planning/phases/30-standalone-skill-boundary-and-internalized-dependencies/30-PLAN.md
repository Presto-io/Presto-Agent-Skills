---
phase: 30
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - skills/teaching-design-package/SKILL.md
  - skills/teaching-design-package/references/format-and-orchestration.md
  - skills/teaching-design-package/references/standalone-install.md
  - skills/teaching-design-package/references/calendar.json
  - skills/teaching-design-package/internal/jiaoan-jihua/templates/jiaoan-jihua-full.md
  - skills/teaching-design-package/internal/jiaoan-shicao/templates/jiaoan-shicao-full.md
  - skills/teaching-design-package/internal/README.md
  - skills/teaching-design-package/scripts/teaching-design-package.sh
autonomous: true
requirements: [TDPKG-01, TDPKG-02, TDPKG-03, TDPKG-15]
requirements_addressed: [TDPKG-01, TDPKG-02, TDPKG-03, TDPKG-15]
---

# Phase 30 Plan: Standalone Skill Boundary and Internalized Dependencies

<objective>
Make `skills/teaching-design-package/` installable and verifiable as a single standalone skill folder. The execution must remove runtime assumptions that `../jiaoan-jihua`, `../jiaoan-shicao`, or repo-root calendars/scripts exist, while preserving the public legacy `jiaoan-jihua` and `jiaoan-shicao` skills unchanged.
</objective>

<must_haves>
## Truths

- D-01: `teaching-design-package` must have a normal runtime path after copying only `skills/teaching-design-package/` to a temporary skill root.
- D-02: The canonical entry must describe `teaching-design-package` as the integrated user-facing skill, not as a sibling-skill stitching instruction.
- D-03: Runtime adapter notes must cover Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent with standalone install/use guidance.
- D-04: Needed `jiaoan-jihua` and `jiaoan-shicao` behavior must be vendored, internalized, or discovered from self-contained package resources; hard-coded repo sibling paths are not accepted for the standalone path.
- D-05: Repo sibling skills may be read for implementation and parity verification only, not required by installed users.
- D-06: The accepted resource lookup must prefer files under `skills/teaching-design-package/`, including templates, scripts/helpers, metadata, and support resources.
- D-07: Calendar support must be skill-local or explicitly self-contained; `skills/jiaoan-jihua/references/calendar.json` cannot be the only runtime source.
- D-08: Do not delete, rename, replace, or change public legacy `jiaoan-jihua` and `jiaoan-shicao` entries, commands, accepted inputs, or output contracts.
- D-09: Legacy parity is a regression gate only.
- D-10: Copied or adapted internal behavior requires checks that legacy public command surfaces still behave as before.
- D-11: The locked teacher UX remains source materials -> clarification/organization -> one editable full Markdown document.
- D-12: Scripts remain finalized-Markdown validation/render tools, not the teacher interaction surface.
- D-13: Phase 30 may make wording changes needed for standalone boundaries but must not absorb the full Phase 31 workflow rewrite.
- D-14: Do not introduce public default artifacts that conflict with the later 1+1+3 delivery contract.
- D-15: Internal handoff Markdown, split Typst, manifests, stderr logs, status sidecars, temporary state, and parity artifacts are hidden work/debug/failure diagnostics, not public default delivery promises.
- D-16: The gray areas selected for Phase 30 are standalone install boundary, internalized jiaoan behavior, adapter wording, legacy public contract preservation, and self-contained scheduling/resource discovery.
- D-17: No new user question is needed; the corrections are locked decisions.
</must_haves>

<tasks>
## Task 1: Internalize package resources and remove sibling-path runtime assumptions

<read_first>
- `AGENTS.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/30-standalone-skill-boundary-and-internalized-dependencies/30-CONTEXT.md`
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md`
- `skills/jiaoan-jihua/references/calendar.json`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
- `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md`
- `skills/jiaoan-shicao/references/calendar.json`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`
</read_first>

<action>
Add skill-local resources so the script can run after only `skills/teaching-design-package/` is copied: create `references/calendar.json` from the currently used jiaoan calendar; create `internal/jiaoan-jihua/templates/jiaoan-jihua-full.md` and `internal/jiaoan-shicao/templates/jiaoan-shicao-full.md` from the legacy template shapes; add `internal/README.md` explaining that these are package-internal compatibility resources and not public skill commands. Update `scripts/teaching-design-package.sh` so `CALENDAR_JSON` points to `${SKILL_DIR}/references/calendar.json`, fallback scaffolds copy `${SKILL_DIR}/internal/jiaoan-jihua/templates/jiaoan-jihua-full.md` and `${SKILL_DIR}/internal/jiaoan-shicao/templates/jiaoan-shicao-full.md`, and normal `example`, `plan-split`, `manifest`, `info`, and baseline `render-package` no longer compute or require `REPO_ROOT` or `../jiaoan-*`.
</action>

<acceptance_criteria>
- `rg 'SKILL_DIR}/../jiaoan|skills/jiaoan-jihua/references/calendar.json|skills/jiaoan-shicao/templates' skills/teaching-design-package/scripts/teaching-design-package.sh` exits non-zero.
- `rg 'CALENDAR_JSON=.*skills/jiaoan|REPO_ROOT=.*/../..' skills/teaching-design-package/scripts/teaching-design-package.sh` exits non-zero for the standalone path.
- `test -f skills/teaching-design-package/references/calendar.json` exits 0.
- `test -f skills/teaching-design-package/internal/jiaoan-jihua/templates/jiaoan-jihua-full.md` exits 0.
- `test -f skills/teaching-design-package/internal/jiaoan-shicao/templates/jiaoan-shicao-full.md` exits 0.
- `bash -n skills/teaching-design-package/scripts/teaching-design-package.sh` exits 0.
</acceptance_criteria>

## Task 2: Define self-contained rendering boundaries for jiaoan and optional end-of-term behavior

<read_first>
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/references/scheduling-contract.md`
- `skills/end-of-term-teaching-materials/SKILL.md` if it exists
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh` if it exists
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`
</read_first>

<action>
Replace the runtime contract for split rendering with a package-local default path. The normal standalone path must support `example`, `plan-split`, `manifest`, and `render-package` from only package-local resources. If `render-split` or `render-package --pdf` still needs legacy jiaoan renderers for exact Typst/PDF parity, guard that branch behind explicit development/parity discovery such as `TDPKG_LEGACY_SKILL_ROOT` or a documented repo-development lookup, and fail with a clear non-final diagnostic when those optional external renderers are unavailable. Do the same for optional end-of-term commands: they may remain optional, but missing `end-of-term-teaching-materials` must not break the non-end-of-term standalone happy path.
</action>

<acceptance_criteria>
- In a standalone copy containing only `teaching-design-package`, `scripts/teaching-design-package.sh example --output <tmp>/teaching-design-package-full.md` exits 0.
- In that same standalone copy, `scripts/teaching-design-package.sh plan-split --input <tmp>/teaching-design-package-full.md --out-dir <tmp>/out` exits 0 and creates internal handoffs without reading `../jiaoan-jihua` or `../jiaoan-shicao`.
- In that same standalone copy, `scripts/teaching-design-package.sh manifest --input <tmp>/teaching-design-package-full.md --out-dir <tmp>/out` exits 0.
- If `render-split` or `render-package --pdf` cannot run without optional legacy renderers, the command fails or records status with text containing `legacy`, `optional`, `unavailable`, or `not installed`; it must not fail with `../jiaoan-jihua` or `../jiaoan-shicao` path errors.
- `scripts/teaching-design-package.sh info` describes `jiaoan-jihua` and `jiaoan-shicao` internals as package-local or optional parity/development resources, not required user installs.
</acceptance_criteria>

## Task 3: Correct standalone install/use documentation and six runtime adapter notes

<read_first>
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/references/scheduling-contract.md`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `AGENTS.md`
</read_first>

<action>
Update `SKILL.md` and references so Inputs no longer require installing `skills/jiaoan-jihua/`, `skills/jiaoan-shicao/`, or `skills/end-of-term-teaching-materials/` for the normal standalone package path. Add or update `references/standalone-install.md` and link it from `SKILL.md` and `format-and-orchestration.md`. Document that users install/copy only `skills/teaching-design-package/`, that `references/`, `templates/`, `scripts/`, `internal/`, and calendar support resources are part of the skill, and that legacy jiaoan skills remain public standalone commands in this repository. Runtime Adapter Notes for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent must each include standalone skill-root discovery, support-file availability, script execution permission, and optional legacy parity/development fallback wording.
</action>

<acceptance_criteria>
- `rg 'skills/jiaoan-jihua/|skills/jiaoan-shicao/|separately install|单独安装' skills/teaching-design-package/SKILL.md skills/teaching-design-package/references/format-and-orchestration.md skills/teaching-design-package/references/standalone-install.md` either exits non-zero or only matches statements that explicitly mark those paths as legacy repo-development/parity references.
- `rg 'Codex|Claude Code|Gemini CLI|OpenCode|OpenClaw|Hermes Agent' skills/teaching-design-package/SKILL.md` reports all six runtimes.
- `rg 'standalone|单技能|self-contained|skill root|support resources|calendar|internal' skills/teaching-design-package/SKILL.md skills/teaching-design-package/references/standalone-install.md` exits 0.
- `rg 'internal handoff|debug|failure diagnostics|public contract|1\\+1\\+3' skills/teaching-design-package/SKILL.md skills/teaching-design-package/references/format-and-orchestration.md skills/teaching-design-package/references/standalone-install.md` exits 0, proving Phase 30 did not expose Phase 32 internals as default public deliverables.
</acceptance_criteria>

## Task 4: Preserve legacy jiaoan public commands and add regression checks

<read_first>
- `skills/jiaoan-jihua/SKILL.md`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
- `skills/jiaoan-jihua/templates/jiaoan-jihua-full.md`
- `skills/jiaoan-shicao/SKILL.md`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`
- `skills/jiaoan-shicao/templates/jiaoan-shicao-full.md`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
</read_first>

<action>
Leave `skills/jiaoan-jihua/` and `skills/jiaoan-shicao/` public entries and commands unchanged unless a minimal test-only adjustment is absolutely required. Add regression evidence commands to the Phase 30 verification path: run each legacy `example` command into a temporary directory; run each legacy `render` command from that example Markdown to Typst; verify their `SKILL.md` trigger descriptions and `Script Usage` still mention the same public command names. If the package implementation needs a legacy parity comparison, make it an explicit repo-local regression check after the standalone check, not the normal standalone install path.
</action>

<acceptance_criteria>
- `git diff -- skills/jiaoan-jihua/SKILL.md skills/jiaoan-jihua/scripts/jiaoan-jihua.sh skills/jiaoan-shicao/SKILL.md skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` is empty unless the executor records an explicit reason in the Phase 30 summary.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh example --output <tmp>/legacy-jihua.md` exits 0.
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render --input <tmp>/legacy-jihua.md --typ <tmp>/legacy-jihua.typ` exits 0.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example --output <tmp>/legacy-shicao.md --calendar-output <tmp>/legacy-shicao-calendar.json` exits 0.
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render --input <tmp>/legacy-shicao.md --typ <tmp>/legacy-shicao.typ` exits 0.
- `rg 'jiaoan-jihua.sh example|jiaoan-jihua.sh render' skills/jiaoan-jihua/SKILL.md` exits 0 and `rg 'jiaoan-shicao.sh example|jiaoan-shicao.sh render' skills/jiaoan-shicao/SKILL.md` exits 0.
</acceptance_criteria>

## Task 5: Run standalone-copy verification before repo-local parity verification

<read_first>
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/references/standalone-install.md`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`
- `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`
</read_first>

<action>
Create a deterministic verification script sequence in the Phase 30 summary or verification evidence. First copy only `skills/teaching-design-package/` into a temporary standalone skill root such as `${TMPDIR}/tdpkg-standalone-root/skills/teaching-design-package`, run the normal happy path there, and scan outputs/errors to prove no repo sibling lookup is required. Then return to the repository and run legacy parity/public-command checks. Do not treat `jiaoan-jihua-full.md`, `jiaoan-shicao-full.md`, split Typst, manifests, logs, or sidecars as public output contracts; record them as internal/debug/failure evidence until Phase 32 enforces the default 1+1+3 delivery surface.
</action>

<acceptance_criteria>
- A standalone verification command copies only `skills/teaching-design-package/` to a temporary skill root and does not copy `skills/jiaoan-jihua/`, `skills/jiaoan-shicao/`, or `skills/end-of-term-teaching-materials/`.
- In the standalone copy, `example`, `plan-split`, and `manifest` complete successfully.
- A standalone hard-path scan such as `rg '../jiaoan|skills/jiaoan|/Presto-Agent-Skills' <standalone-out> <standalone-stderr>` reports no normal-path dependency leak, excluding documentation text that explicitly says legacy parity is optional.
- Repo-local regression then runs the legacy jiaoan public commands listed in Task 4.
- Phase 30 summary records both standalone-copy verification and legacy parity verification with exact commands and outcomes.
</acceptance_criteria>
</tasks>

<verification>
Run these checks after implementation:

```bash
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh

tmp_root="$(mktemp -d "${TMPDIR:-/tmp}/tdpkg-standalone-root.XXXXXX")"
mkdir -p "$tmp_root/skills"
cp -R skills/teaching-design-package "$tmp_root/skills/"
"$tmp_root/skills/teaching-design-package/scripts/teaching-design-package.sh" example \
  --output "$tmp_root/teaching-design-package-full.md"
"$tmp_root/skills/teaching-design-package/scripts/teaching-design-package.sh" plan-split \
  --input "$tmp_root/teaching-design-package-full.md" \
  --out-dir "$tmp_root/out"
"$tmp_root/skills/teaching-design-package/scripts/teaching-design-package.sh" manifest \
  --input "$tmp_root/teaching-design-package-full.md" \
  --out-dir "$tmp_root/out"
rg '../jiaoan|skills/jiaoan|/Presto-Agent-Skills' "$tmp_root/out" "$tmp_root"/*.log

legacy_tmp="$(mktemp -d "${TMPDIR:-/tmp}/tdpkg-legacy.XXXXXX")"
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh example --output "$legacy_tmp/jiaoan-jihua-full.md"
skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render \
  --input "$legacy_tmp/jiaoan-jihua-full.md" \
  --typ "$legacy_tmp/jiaoan-jihua-full.typ"
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh example \
  --output "$legacy_tmp/jiaoan-shicao-full.md" \
  --calendar-output "$legacy_tmp/calendar.json"
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render \
  --input "$legacy_tmp/jiaoan-shicao-full.md" \
  --typ "$legacy_tmp/jiaoan-shicao-full.typ"

rg 'Codex|Claude Code|Gemini CLI|OpenCode|OpenClaw|Hermes Agent' skills/teaching-design-package/SKILL.md
rg 'standalone|单技能|self-contained|support resources|internal' \
  skills/teaching-design-package/SKILL.md \
  skills/teaching-design-package/references/standalone-install.md
```

For the `rg '../jiaoan|skills/jiaoan|/Presto-Agent-Skills'` standalone scan, a non-zero exit is the desired normal-path result. If documentation files in the copied skill intentionally mention legacy repo paths, scan only generated outputs and command stderr/stdout for hard runtime leaks.
</verification>

<success_criteria>
- `teaching-design-package` has a verified normal path when only its own folder is installed.
- `jiaoan-jihua` and `jiaoan-shicao` behavior needed for package scaffolding/calendar support is internalized or made explicitly optional/self-contained.
- Six runtime adapters document standalone install/use boundaries.
- Legacy `jiaoan-jihua` and `jiaoan-shicao` public command surfaces remain unchanged and pass regression commands.
- The plan does not make Phase 32 internal artifacts a public default delivery contract.
</success_criteria>

<threat_model>
This phase is local documentation and shell-script packaging work. Primary risks are supply-chain-like path confusion and data leakage through absolute local paths in generated artifacts.

- Path confusion: a standalone install could accidentally run repo sibling scripts from a developer machine. Mitigation: default all normal paths to `${SKILL_DIR}` resources and reserve legacy discovery for explicit parity/development mode.
- Public contract leakage: internal handoff/status artifacts could become documented as required user deliverables. Mitigation: label them internal/debug/failure diagnostics and preserve Phase 32 as the clean delivery enforcement phase.
- Regression of legacy skills: copying internals could tempt changes to `skills/jiaoan-*`. Mitigation: do not modify legacy public commands and run legacy examples/renders after package standalone verification.
</threat_model>
