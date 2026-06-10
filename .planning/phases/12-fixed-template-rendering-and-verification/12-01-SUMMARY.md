---
phase: 12-fixed-template-rendering-and-verification
plan: 01
status: complete
requirements-completed:
  - ETM-05
  - ETM-06
  - ETM-07
  - ETM-08
completed: 2026-06-10
---

# Phase 12 Plan 01 Summary: Fixed-Template Rendering and Verification

## Outcome

Completed Phase 12 as one executable rendering slice for `end-of-term-teaching-materials`.

The skill now supports:

- Skill-local fixed-template references and a Typst package template.
- Sanitized structured JSON fixture and sanitized workbook fixture.
- `example`, `validate`, `markdown`, `render`, `verify`, `manifest`, `info`, and `version` commands.
- Structured data -> Markdown -> Typst/PDF + deterministic table artifacts.
- `tables/score-data.json`, `tables/score-data.csv`, `tables/task-map.json`, `tables/score-summary.json`, and `tables/scorebook.xlsx`.
- Review-marker blocking when `## 复核标记` is not exactly `无`.
- Manifest warnings for skipped `交接班记录封面` when handover metadata is missing.
- Runtime adapter notes for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.

## Files Created

- `skills/end-of-term-teaching-materials/references/rendering-style.md`
- `skills/end-of-term-teaching-materials/references/cover-template-notes.md`
- `skills/end-of-term-teaching-materials/references/scorebook-template-notes.md`
- `skills/end-of-term-teaching-materials/references/fixtures/end-of-term-source.json`
- `skills/end-of-term-teaching-materials/references/fixtures/scorebook-template.xlsx`
- `skills/end-of-term-teaching-materials/templates/typst/end-of-term-package.typ`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`
- `skills/end-of-term-teaching-materials/scripts/render_package.py`
- `.planning/phases/12-fixed-template-rendering-and-verification/12-01-SUMMARY.md`

## Files Updated

- `skills/end-of-term-teaching-materials/SKILL.md`
- `skills/end-of-term-teaching-materials/templates/end-of-term-full.md`
- `README.md`
- `skills/README.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`

## Verification

Run locally:

```bash
bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh
python3 -m py_compile skills/end-of-term-teaching-materials/scripts/render_package.py
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh verify --workdir <tmpdir>
git diff --check
```

The black-box verifier covers data validation, Markdown generation, unresolved-review blocking, Typst generation, optional PDF compilation, deterministic JSON/CSV outputs, workbook smoke checks, and repeatability checks.

Human verification passed on 2026-06-10. The generated end-of-term package was manually accepted against the user's external reference materials.

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

All Phase 12 requirements ETM-05 through ETM-08 are marked complete, and the skill remains bounded to fixed templates with no OCR, arbitrary template discovery, or hidden source-to-PDF shortcut.
