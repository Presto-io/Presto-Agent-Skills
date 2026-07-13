---
phase: 41-standard-template-and-manifest
plan: 1
subsystem: templates
tags: [school-pptx, pptx, manifest, template-report, yaml]

requires:
  - phase: 40-pdf-workflow-and-missing-information-guidance
    provides: prior milestone completion before v1.17 starts
provides:
  - Controlled `standard-school` PPTX runtime template
  - YAML slot manifest for 11 school-pptx layouts
  - `template-report` Markdown and JSON evidence command
  - Manual template editing guardrails
affects: [school-pptx, phase-42, phase-43, phase-44]

tech-stack:
  added: []
  patterns:
    - Skill-local PPTX template plus YAML manifest contract
    - ZIP/XML structural validation without package-manager installs
    - Hidden `.school-pptx` evidence workdir

key-files:
  created:
    - skills/school-pptx/templates/standard-school.pptx
    - skills/school-pptx/templates/standard-school.manifest.yaml
    - skills/school-pptx/scripts/school-pptx.sh
    - skills/school-pptx/scripts/template_report.py
    - skills/school-pptx/references/template-contract.md
    - skills/school-pptx/references/template-editing.md
  modified: []

key-decisions:
  - "Use the supplied POTX as visual source evidence, but normalize runtime behavior to skill-local `standard-school.pptx`."
  - "Bind the 11 logical layouts to inspectable PPTX slide-layout XML anchors and verify shape ids, names, geometry, and budgets."
  - "Keep Phase 41 scoped to template contract validation; Markdown contract and rendering remain Phase 42/43 work."

patterns-established:
  - "Template reports write human Markdown and machine JSON evidence to explicit or hidden verification paths."
  - "Manual template edits are allowed only when mapped placeholders and manifest anchors stay valid."

requirements-completed: [TPL-01, TPL-02, TPL-03, TPL-04, TPL-05, TPL-06, TPL-07, VER-02]

duration: 49min
completed: 2026-07-13
---

# Phase 41: Standard Template and Manifest Summary

**Controlled `standard-school` PPTX template, full 11-layout slot manifest, and repeatable template-report validation for `school-pptx`**

## Performance

- **Duration:** 49 min
- **Started:** 2026-07-13T08:22:00Z
- **Completed:** 2026-07-13T09:11:33Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- Normalized `test/学院PPT模板.potx` into the skill-local runtime template `skills/school-pptx/templates/standard-school.pptx`.
- Authored `standard-school.manifest.yaml` with theme, 11 layouts, semantic slots for content-controllable layouts, placeholder anchors, EMU geometry, text budgets, empty-slot rules, continuation rules, and template-owned boundaries.
- Added `template-report` validation that emits Markdown/JSON evidence and fails non-zero for unknown themes, missing layouts, missing slots, duplicate slots, lost anchors, geometry mismatch, and malformed budgets.
- Documented template contract and manual editing rules while explicitly fencing out Markdown syntax, rendering, pagination, notes, and final runtime adapter docs.

## Task Commits

1. **Task 1: Normalize runtime PPTX template and manifest** - `83f6d16` (`feat`)
2. **Task 2: Implement template-report validator** - `0cbf554` (`feat`)
3. **Task 3: Document manual editing guardrails** - `ddca630` (`docs`)

## Files Created/Modified

- `skills/school-pptx/templates/standard-school.pptx` - Normalized runtime PPTX template.
- `skills/school-pptx/templates/standard-school.manifest.yaml` - Controlled theme, layouts, slots, geometry, budgets, and ownership manifest.
- `skills/school-pptx/scripts/school-pptx.sh` - Skill-local CLI wrapper for `template-report` and `info`.
- `skills/school-pptx/scripts/template_report.py` - PPTX ZIP/XML plus YAML manifest validator.
- `skills/school-pptx/references/template-contract.md` - Human-readable template contract and Phase 41 scope fence.
- `skills/school-pptx/references/template-editing.md` - Manual edit allow/deny rules and validation command.

## Decisions Made

- Used native slide-layout XML as the Phase 41 inspectable mapping mechanism because the supplied POTX already contains 11 slide layouts.
- Stored geometry in EMU to compare directly against PPTX XML and avoid lossy unit conversion during validation.
- Kept copied negative-case manifests in `/tmp` during verification so failure artifacts do not enter public output.
- Kept `closing` as a fixed template-owned final page with no Markdown-controllable title/subtitle slots.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The first negative-case verification exposed that `--manifest /tmp/...` resolved the template path relative to `/tmp`. Fixed `template_report.py` so an overridden manifest still uses the skill-local template unless `--template` is explicitly supplied.

## Verification

Passed:

```bash
skills/school-pptx/scripts/school-pptx.sh template-report \
  --theme standard-school \
  --out-md build/school-pptx/.school-pptx/template-report.md \
  --out-json build/school-pptx/.school-pptx/template-report.json
```

Passed JSON checks: `theme_id == "standard-school"`, `failures == []`, and exactly 11 layouts.

Passed negative checks for unknown theme, missing layout, missing slot, duplicate slot, lost placeholder mapping, geometry mismatch, and malformed text budget. `find skills/school-pptx -name '*.potx' -print | wc -l` returned `0`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 42 can define the Markdown contract and full fixture against the controlled `standard-school` theme and the 11 manifest layout ids. Rendering, logical-to-physical pagination, speaker notes, final adapter notes, README updates, and compatibility-matrix updates remain intentionally deferred.

---
*Phase: 41-standard-template-and-manifest*
*Completed: 2026-07-13*
