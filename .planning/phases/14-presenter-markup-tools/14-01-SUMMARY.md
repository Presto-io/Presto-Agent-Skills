# Phase 14 Plan 01 Summary: Presenter Markup Tools

## Result

Complete. Phase 14 adds playback-local presenter markup tools to `school-presentation` without introducing authored annotation syntax or mutating deterministic review artifacts.

## Delivered

- Added a playback-only floating `markup-palette` with pointer, pen, highlighter, eraser, clear current page, and placement controls.
- Added `annotationState` session memory keyed by physical `page_id`.
- Rendered annotations through a playback-only SVG `annotation-layer` in slide design coordinates, scaled with `.slide-scale-shell`.
- Implemented Pointer Events for pen, highlighter, eraser, and live pointer behavior.
- Preserved page annotations across navigation until explicit current-page clear.
- Suppressed click-zone navigation while drawing or erasing, while keeping keyboard navigation available.
- Kept preview workspace, overview, thumbnails, `.page-source`, Markdown source, and manifest output annotation-free.
- Updated `SKILL.md` and `school-presentation-full.md` to document/demo playback-local markup without adding Markdown annotation directives.
- Extended `verify` with `presenter_markup_verified`.

## Files Changed

- `skills/school-presentation/scripts/school-presentation.sh`
- `skills/school-presentation/SKILL.md`
- `skills/school-presentation/templates/school-presentation-full.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/14-presenter-markup-tools/14-01-SUMMARY.md`

## Verification

Passed:

```bash
skills/school-presentation/scripts/school-presentation.sh verify --workdir /tmp/school-presentation-phase14-verify
rg -n '"status": "passed"|"presenter_markup_verified": true' /tmp/school-presentation-phase14-verify/verification-manifest.json
if rg -n "annotationState|annotation-layer|markup-palette" /tmp/school-presentation-phase14-verify/school-presentation-first.manifest.json; then exit 1; fi
for term in pointer pen highlighter eraser "clear/reset" "page-scoped"; do rg -n "$term" skills/school-presentation/SKILL.md; done
git diff --check
```

Browser smoke check passed with headless Google Chrome against `/tmp/school-presentation-phase14-verify/school-presentation-first.html`:

- Entered playback.
- Selected pen and drew one stroke.
- Confirmed drawing did not advance the deck.
- Confirmed ArrowRight advanced while pen was active.
- Returned to the annotated page and confirmed the stroke persisted.
- Cleared current page and confirmed the stroke count returned to zero.
- Left pen mode and confirmed normal keyboard navigation still advanced.

Smoke result:

```json
{
  "strokeCount": 1,
  "restoredStrokes": 1,
  "clearedStrokes": 0,
  "beforeIndex": 0,
  "nextIndex": 1,
  "returnedIndex": 0,
  "normalAdvanceIndex": 1
}
```

## Deviations from Plan

Two interaction defects were found during browser smoke testing and fixed before closeout:

- Keyboard navigation was initially blocked while focus remained on the active markup tool button. Fixed by allowing Arrow/Page navigation from toolbar focus while preserving Space/Enter button activation.
- Clear current page was initially intercepted by the active drawing handler when the palette overlapped the slide shell. Fixed by exempting markup and playback controls from stroke capture.

Post-smoke manual review found presenter-toolbar animation defects and they were fixed before final acceptance:

- Restored slide/page transitions to the original fade behavior after a toolbar-side-switch request was accidentally applied to page transitions.
- Reworked the collapsed toolbar into a true single circular bubble instead of a shifted expanded toolbar.
- Restricted presenter palette placement to lower-left/lower-right and removed side-toolbar/drawer-shift leftovers from the generated review artifact.
- Fixed lower-left/lower-right switching so the toolbar slides out through the current screen edge and enters from the opposite edge.
- Fixed the switch-animation restart jitter by locking the current target placement and letting WAAPI own `transform` while the switch is running.

**Total deviations:** 7 auto-fixed. **Impact:** Positive; fixes directly strengthen SP-17/SP-20 presenter usability while keeping annotations playback-local.

## Human UAT

Passed on 2026-06-11 in the in-app browser against:

```text
generated/phase14-presenter-markup-review/school-presentation-first.html
```

Final user acceptance note: "人工验收通过".

## Requirement Status

- SP-17: Complete
- SP-18: Complete
- SP-19: Complete
- SP-20: Complete

## Self-Check: PASSED
