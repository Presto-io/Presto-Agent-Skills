---
phase: 02-canonical-skill-format-and-runtime-adapters
verified: 2026-05-30T15:33:44Z
status: passed
score: 5/5 requirements verified
requirements:
  - TMPL-01
  - TMPL-02
  - RT-01
  - RT-02
  - RT-03
superseded_artifacts:
  - "templates/adapter/runtime-adapter.md was removed by Phase 3 scope reconciliation; TMPL-02 is now verified through canonical SKILL.md Runtime Adapter Notes."
  - "adapters/README.md was removed by Phase 3 scope reconciliation; runtime guidance is verified through docs/compatibility-matrix.md and canonical SKILL.md notes."
human_verification:
  - test: "As a skill contributor, copy templates/skill/SKILL.md to skills/<skill-name>/SKILL.md, then fill metadata, workflow, runtime notes, outputs, verification, and safety sections."
    expected: "The contributor can author one portable skill source without needing separate adapter files."
    why_human: "Automated checks prove the required sections and runtime targets exist; contributor clarity remains qualitative."
---

# Phase 2: Canonical Skill Format and Runtime Notes Verification Report

**Phase Goal:** As a skill contributor, I want to use a reusable skill source format with embedded runtime notes, so that I can adapt one skill source across all supported runtimes.
**Verified:** 2026-05-30T15:33:44Z
**Status:** passed

## User Flow Coverage

| Step | Expected | Evidence in Codebase | Status |
|---|---|---|---|
| Start from canonical template | Contributor can copy `templates/skill/SKILL.md` as the portable skill source. | `README.md:51`, `templates/README.md:5`, `templates/skill/SKILL.md:1-15` | VERIFIED |
| Fill required skill sections | Template includes metadata, objective, usage triggers, inputs, process, outputs, verification, success criteria, and safety. | `templates/skill/SKILL.md:1-15`, `templates/skill/SKILL.md:19-75` | VERIFIED |
| Capture runtime differences inside the same file | Template includes `Runtime Adapter Notes` rather than requiring separate adapter logic. | `templates/skill/SKILL.md:42-53` | VERIFIED |
| Check runtime compatibility guidance | Compatibility matrix covers Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent. | `docs/compatibility-matrix.md:16-23`, `docs/compatibility-matrix.md:27-82` | VERIFIED |
| Preserve first-class OpenClaw and Hermes coverage | Docs keep OpenClaw and Hermes Agent as required targets with verification cautions. | `README.md:7-16`, `docs/compatibility-matrix.md:22-23`, `docs/compatibility-matrix.md:60-82` | VERIFIED |

## Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `templates/skill/SKILL.md` | Copyable canonical skill template | VERIFIED | Contains metadata, supported runtimes, workflow sections, runtime notes, outputs, verification, success criteria, and safety. |
| `docs/compatibility-matrix.md` | Six-runtime compatibility matrix and runtime notes | VERIFIED | Covers all required runtimes and records installation-time cautions for OpenClaw and Hermes Agent. |
| `README.md` | Contributor path for authoring one portable skill file | VERIFIED | Directs contributors to copy `templates/skill/SKILL.md` and fill runtime notes in the same file. |
| `docs/directory-spec.md` | Directory rules for skill sources, templates, and adapter notes | VERIFIED | Defines canonical skill source ownership and states v1 does not maintain standalone adapter files. |
| `templates/README.md` | Template index and copyability guidance | VERIFIED | Identifies `skill/SKILL.md` as the default portable skill source template. |

## Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `README.md` | `templates/skill/SKILL.md` | New-skill contributor flow | VERIFIED | `README.md:51-56` points to copying the template and filling runtime notes. |
| `templates/skill/SKILL.md` | `docs/compatibility-matrix.md` | Six runtime targets and adapter-note model | VERIFIED | Both files name Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent. |
| `docs/compatibility-matrix.md` | v1 requirements | TMPL/RT coverage | VERIFIED | Archived requirements mark TMPL-01, TMPL-02, RT-01, RT-02, and RT-03 complete. |

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| TMPL-01 | `02-01-PLAN.md` | Contributor can copy a canonical `SKILL.md` template with metadata, objective, usage, process, outputs, and success criteria. | SATISFIED | `templates/skill/SKILL.md:1-15`, `templates/skill/SKILL.md:19-75`; `README.md:51-56`; `templates/README.md:5-9`. |
| TMPL-02 | `02-01-PLAN.md` | Contributor can use canonical `Runtime Adapter Notes` for invocation, user-question handling, task/subagent handling, tool differences, and limitations without a separate adapter template. | SATISFIED | `templates/skill/SKILL.md:42-53`; `docs/compatibility-matrix.md:7-12`, `docs/compatibility-matrix.md:16-23`. |
| RT-01 | `02-01-PLAN.md` | Compatibility matrix covers Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent. | SATISFIED | `docs/compatibility-matrix.md:16-23`, `docs/compatibility-matrix.md:27-82`. |
| RT-02 | `02-01-PLAN.md` | OpenClaw and Hermes Agent are first-class required targets with runtime-note guidance and research notes. | SATISFIED | `README.md:7-16`; `docs/compatibility-matrix.md:22-23`, `docs/compatibility-matrix.md:60-82`; `AGENTS.md:27`. |
| RT-03 | `02-01-PLAN.md` | Docs explain canonical source first, embedded runtime-specific notes second. | SATISFIED | `README.md:18-24`, `README.md:49-56`; `docs/directory-spec.md:26`, `docs/directory-spec.md:42`; `docs/compatibility-matrix.md:5-12`. |

No orphaned Phase 2 requirements were found. The archived v1.0 requirements map TMPL-01, TMPL-02, RT-01, RT-02, and RT-03 to Phase 2, and all five appear in the Phase 2 summary frontmatter.

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Canonical template sections | `rg -n "metadata:\|Objective\|Use When\|Inputs\|Process\|Runtime Adapter Notes\|Outputs\|Verification\|Success Criteria\|Safety" templates/skill/SKILL.md` | All required sections matched. | PASS |
| Six runtimes in template | `rg -n "Codex\|Claude Code\|Gemini CLI\|OpenCode\|OpenClaw\|Hermes Agent" templates/skill/SKILL.md` | All six runtimes matched. | PASS |
| Compatibility matrix coverage | `rg -n "Codex\|Claude Code\|Gemini CLI\|OpenCode\|OpenClaw\|Hermes Agent" docs/compatibility-matrix.md` | Matrix and runtime notes cover all six targets. | PASS |
| Canonical-first docs | `rg -n "canonical\|SKILL\\.md\|Runtime Adapter Notes\|generated wrappers" README.md docs/directory-spec.md docs/compatibility-matrix.md templates/README.md` | Docs consistently describe one canonical skill source and deferred wrappers. | PASS |
| Standalone adapter cleanup compatibility | `test ! -e adapters && test ! -e templates/adapter/runtime-adapter.md` | Standalone adapter artifacts are absent after Phase 3; canonical notes remain the verified path. | PASS |

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---:|---|---|---|
| n/a | n/a | n/a | n/a | No blocking TODO/FIXME/TBD/stub markers were found in Phase 2 deliverables. Template placeholders are intentional and required for copyable templates. |

## Human Verification

### Contributor Template Walkthrough

**Test:** As a skill contributor, copy `templates/skill/SKILL.md` to `skills/<skill-name>/SKILL.md`, then fill metadata, workflow, runtime notes, outputs, verification, and safety sections.

**Expected:** The contributor can author one portable skill source and record runtime differences without needing separate adapter files.

**Why human:** Automated checks prove sections and runtime targets exist; a human walkthrough confirms the template is clear enough to use.

## Completion Summary

Phase 2 satisfies TMPL-01, TMPL-02, RT-01, RT-02, and RT-03 against the final v1.0 scope. Standalone adapter files from the original Phase 2 plan were superseded by Phase 3's scope reconciliation, and their removal is consistent with the archived v1.0 requirement that runtime differences live in canonical `SKILL.md` notes.

Overall status is `passed`.

---
_Verified: 2026-05-30T15:33:44Z_
_Verifier: Codex_
