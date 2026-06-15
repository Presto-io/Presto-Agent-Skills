# Phase 30: Standalone Skill Boundary and Internalized Dependencies - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-15
**Phase:** 30-Standalone Skill Boundary and Internalized Dependencies
**Areas discussed:** Standalone install boundary, Internalized jiaoan behavior, Runtime adapter wording, Legacy contract preservation, Self-contained scheduling/resource discovery

---

## Standalone Install Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Require sibling repo skills | Keep using `../jiaoan-jihua` and `../jiaoan-shicao` as installed siblings. | |
| Single self-contained package | Make `teaching-design-package` installable/useable by copying only its own folder. | ✓ |
| Document manual stitching | Tell users to run separate skills and assemble outputs manually. | |

**User's choice:** Single self-contained package.
**Notes:** User explicitly corrected that `teaching-design-package` must not require extra installation of repo sibling skill directories.

---

## Internalized Jiaoan Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Vendor/internalize needed behavior | Copy/adapt the needed jiaoan behavior or resources into the package boundary. | ✓ |
| Keep hard-coded sibling paths | Continue resolving module behavior from repo-relative sibling paths. | |
| Remove jiaoan behavior | Drop teaching-plan or lesson-plan behavior from the package. | |

**User's choice:** Vendor/internalize needed behavior, or make it explicitly self-contained/discoverable.
**Notes:** Hard-coded repo sibling paths are not acceptable for the standalone path.

---

## Runtime Adapter Wording

| Option | Description | Selected |
|--------|-------------|----------|
| Explain standalone install per runtime | Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent notes all describe installing/using one skill folder and checking internal resources. | ✓ |
| Keep generic runtime notes | Preserve existing adapter wording without addressing sibling dependency risk. | |
| Split runtime-specific skill copies | Create divergent runtime bodies for this package. | |

**User's choice:** Explain standalone install per runtime.
**Notes:** This follows repository policy: canonical body plus adapter notes, not divergent runtime-specific skills.

---

## Legacy Contract Preservation

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve legacy public contracts | Leave `jiaoan-jihua` and `jiaoan-shicao` standalone entries and public commands unchanged. | ✓ |
| Replace legacy skills with package | Make the package the only supported path. | |
| Rename legacy commands | Change old commands to match integrated package naming. | |

**User's choice:** Preserve legacy public contracts.
**Notes:** User explicitly locked that old `jiaoan-jihua` and `jiaoan-shicao` skills must be retained and their public commands must not change.

---

## Self-Contained Scheduling/Resource Discovery

| Option | Description | Selected |
|--------|-------------|----------|
| Package-local resources or discovery | Move/expose needed calendars, templates, helpers, or discovery metadata through `teaching-design-package` itself. | ✓ |
| Repo-root discovery only | Resolve calendars/templates/scripts only through the original repository layout. | |
| Teacher-maintained YAML facts | Avoid resource dependency by asking teachers to fill derived scheduling fields manually. | |

**User's choice:** Package-local resources or discovery.
**Notes:** The current script points at `skills/jiaoan-jihua/references/calendar.json`; Phase 30 planning must remove that as a standalone-install assumption.

---

## Claude's Discretion

- Exact internal folder names and helper boundaries are left to planning, provided the final design satisfies the locked standalone boundary.
- Regression test granularity is left to planning, but must include checks that legacy jiaoan public contracts are not changed.

## Deferred Ideas

- Phase 31 owns the broader teacher-facing source-materials-to-full-Markdown rewrite.
- Phase 32 owns default output cleanup and hidden diagnostics enforcement.
