---
phase: 13-close-gap-etm-04-etm-06-etm-08-uncertain-scores-must-reach-m
plan: 01
status: complete
requirements-completed:
  - ETM-04
  - ETM-06
  - ETM-08
completed: 2026-06-10
---

# Phase 13 Plan 01 Summary: Uncertain Scores Must Reach Markdown Review

## Outcome

Completed the v1.7 audit closure for uncertain score handling.

The `end-of-term-teaching-materials` skill now allows structured JSON values such as `87?` to generate reviewable Markdown with matching `## 复核标记` rows, while normal final export readiness remains strict. An explicit abnormal review preview path can produce non-final artifacts for teacher inspection with red warning evidence.

## Files Created

- `skills/end-of-term-teaching-materials/references/fixtures/end-of-term-source-uncertain.json`
- `.planning/phases/11-end-of-term-data-and-markdown-contract/11-VERIFICATION.md`
- `.planning/phases/13-close-gap-etm-04-etm-06-etm-08-uncertain-scores-must-reach-m/13-01-SUMMARY.md`
- `.planning/phases/13-close-gap-etm-04-etm-06-etm-08-uncertain-scores-must-reach-m/13-VERIFICATION.md`

## Files Updated

- `skills/end-of-term-teaching-materials/scripts/render_package.py`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`
- `skills/end-of-term-teaching-materials/SKILL.md`
- `skills/end-of-term-teaching-materials/references/data-contract.md`
- `skills/end-of-term-teaching-materials/references/rendering-style.md`
- `skills/end-of-term-teaching-materials/references/scorebook-template-notes.md`
- `.planning/phases/12-fixed-template-rendering-and-verification/12-01-SUMMARY.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`

## Verification

Passed:

```bash
bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh
python3 -m py_compile skills/end-of-term-teaching-materials/scripts/render_package.py
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh markdown --input skills/end-of-term-teaching-materials/references/fixtures/end-of-term-source-uncertain.json --output <tmpdir>/end-of-term-full.md
rg -n "87\?|## 复核标记|需复核" <tmpdir>/end-of-term-full.md
skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh verify --workdir <tmpdir>
```

The verifier covers clean fixture rendering, uncertain-source Markdown generation, final-export blocking, explicit abnormal review rendering, red highlight evidence for unresolved uncertainty, red highlight evidence for below-60 `学期成绩`, deterministic table artifacts, workbook output, and Typst/PDF compilation when Typst is available.

## Deviations

None.

## Self-Check: PASSED

ETM-04, ETM-06, and ETM-08 closure evidence is recorded in Phase 13 verification. Phase 11 and Phase 12 audit metadata gaps are normalized without expanding into OCR, arbitrary template discovery, hidden source-to-PDF output, or private data fixtures.
