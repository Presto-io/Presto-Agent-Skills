---
status: resolved
trigger: "v1.6 school-presentation Phase 10 generated HTML has visual bugs in agenda alignment/pagination, broken media placeholders, alert icons, spacing, list pagination, and playback overflow."
created: "2026-06-10"
updated: "2026-06-11"
---

# Debug Session: school-presentation-v16-visual-bugs

## Symptoms

- expected_behavior: "The v1.6 school-presentation HTML should render cleanly in playback and preview: cover content constrained to title/subtitle/info bar, agenda content aligned and paginated, broken media shown with a media-broken glyph, alert icons centered and semantically correct, block spacing preserved, long lists split naturally, and media-center slides staying within the visible area."
- actual_behavior: "Agents can overfill the cover by adding extra subtitle-like content or arbitrary cover info fields; the agenda title, route decoration, and agenda items are vertically misaligned; agendas with more than five entries overflow instead of splitting; agenda item numbers are not vertically centered; missing images/videos use an unsuitable icon; media playback failures should look like broken media; alert icons are off-center or wrong for error; adjacent tables/callouts and charts/text have no gap; long unordered lists create an excessive blank gap after five items; slide 2.6.1 overflows during playback."
- error_messages: "No runtime error; visual layout defects in /tmp/school-presentation-v16-phase10.html."
- timeline: "Reported during v1.6 milestone development/visual review on 2026-06-10."
- reproduction: "Render or open the v1.6 Phase 10 school-presentation HTML, then inspect agenda pages, slide 2.6.1, slide 3.4.1, media fallback pages, chart/text spacing, table/callout spacing, and long unordered-list split pages."

## Current Focus

- hypothesis: "The defects are mostly renderer CSS/layout, cover contract, and chunking behavior in skills/school-presentation/scripts/school-presentation.sh/SKILL.md, with planning state also incorrectly marking v1.6 as accepted."
- test: "Patch source renderer, regenerate the fixture, verify manifests, and inspect representative DOM/layout metrics for agenda, media-center, alert icons, spacing, and overflow."
- expecting: "Generated HTML has paginated agenda pages, centered agenda number badges, broken-media icons, centered alert icon marks, consistent block gaps, no artificial list gap, and no playback overflow on 2.6.1."
- next_action: "Resolved; Phase 10 human visual UAT passed on 2026-06-11, and v1.6 is ready for milestone closeout."

## Evidence

- timestamp: "2026-06-10"
  checked: "git status --short"
  observation: "Existing uncommitted planning edits mark v1.6 Phase 10 human UAT as passed, which conflicts with the user's correction that v1.6 is not finished."
- timestamp: "2026-06-10"
  checked: "skills/school-presentation/scripts/school-presentation.sh"
  observation: "The renderer owns agenda HTML/CSS, media fallback glyphs, alert icon CSS, block chunking, and playback scaling behavior."
- timestamp: "2026-06-10"
  checked: "skills/school-presentation/SKILL.md and cover renderer"
  observation: "The skill allowed arbitrary `cover_*` fields and the renderer included cover body blocks, which can create multiple subtitle-like regions and overflow the cover."
- timestamp: "2026-06-10"
  checked: "/tmp/school-presentation-cover-contract.md rendered to /tmp/school-presentation-cover-contract.html"
  observation: "A fixture containing cover body text, warning/notes, `cover_topic`, `cover_class`, and legacy `cover_location` rendered a cover with only title, one subtitle, and the fixed info-bar fields; forbidden extra cover strings were absent."
- timestamp: "2026-06-10"
  checked: "/tmp/school-presentation-agenda-contract.md rendered to /tmp/school-presentation-agenda-contract.html and manifest"
  observation: "Seven sections produced two agenda physical pages with 5 and 2 entries, page hints `1 / 2` and `2 / 2`, and manifest page labels `目录 1` and `目录 2`."
- timestamp: "2026-06-10"
  checked: "/tmp/school-presentation-v16-visual-verify3/verification-manifest.json"
  observation: "Skill verification passed with repeatable HTML, hierarchy, reveal, workspace, thumbnail ratio, and flat-slide compatibility checks all true."
- timestamp: "2026-06-10"
  checked: "npx -y playwright screenshot file:///tmp/school-presentation-cover-contract.html /tmp/school-presentation-cover-contract.png"
  observation: "Screenshot verification could not run because the local Playwright Chromium headless shell is not installed; installing it requires downloading browser binaries."
- timestamp: "2026-06-11"
  checked: ".planning/phases/10-ordered-reveals-and-classroom-answer-masks/10-HUMAN-UAT.md"
  observation: "User confirmed Phase 10 manual visual acceptance passed after the v1.6 visual-fix pass."

## Eliminated

- hypothesis: "This is a v1.7 post-close debug."
  reason: "User clarified the symptoms belong to unfinished v1.6 milestone work."

## Resolution

- root_cause: "Phase 10 renderer and skill contract were too permissive for cover metadata/content, used single-page agenda assumptions, had underspecified media fallback/error handling, and had CSS/chunking values that caused icon, spacing, list, and media-center overflow defects."
- fix: "Constrained the cover to title/subtitle/fixed info bar; made cover title render as at most two lines with at most ten visible characters per line; capped cover subtitle display at 24 visible characters; changed cover info bar to optional `unit`, person value, and date value only; placed unit below person/date without a label and lowered info-bar opacity; ignored cover body content; removed arbitrary `cover_*` info rendering; paginated agenda entries in groups of five; centered agenda layout and numeric badges; replaced missing-media glyphs with broken-media icons; added runtime broken media replacement; corrected warning/error/info/tip icon semantics and centering; restored table/chart/media fallback spacing; relaxed unordered-list splitting; tightened media-center image height."
- verification: "Ran `bash -n skills/school-presentation/scripts/school-presentation.sh`; ran `git diff --check`; rendered targeted cover long/short fixtures; ran `skills/school-presentation/scripts/school-presentation.sh verify --workdir /tmp/school-presentation-v16-debug-final`, which produced `status: passed`; after user-confirmed visual acceptance, ran `skills/school-presentation/scripts/school-presentation.sh verify --workdir /tmp/school-presentation-v16-audit-final`, which also produced `status: passed`."
- files_changed: "skills/school-presentation/scripts/school-presentation.sh; skills/school-presentation/SKILL.md; skills/school-presentation/templates/school-presentation-full.md; .planning/ROADMAP.md; .planning/STATE.md; .planning/milestones/v1.6-ROADMAP.md; .planning/phases/10-ordered-reveals-and-classroom-answer-masks/10-01-SUMMARY.md"
