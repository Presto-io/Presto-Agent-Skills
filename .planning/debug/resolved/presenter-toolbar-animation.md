---
status: resolved
trigger: "在 /Users/mrered/Developer/Presto-Agent-Skills 中诊断 generated/phase14-presenter-markup-review/school-presentation-first.html 的 presenter 工具条和翻页动画问题。用户症状：1) 左右翻页没有表现为当前页滑出屏幕、新页从另一侧滑入；2) 工具条没有稳定缩成同一个圆形浮动泡泡；3) 偶发出现两个圆且不对齐。请只做诊断，不要改文件。重点检查 skills/school-presentation/scripts/school-presentation.sh 中 clonePageInto/selectPage 的动画和 markup-palette CSS/JS，给出根因与最小修复建议。注意当前主线程也在修改文件，不要 revert 任何改动。"
created: 2026-06-11T11:41:15+08:00
updated: 2026-06-11T12:04:55+08:00
---

## Current Focus
<!-- OVERWRITE on each update - reflects NOW -->

hypothesis: Resolved. Toolbar side switching was restarting the same target animation while pointermove events kept firing, and CSS transition was competing with WAAPI for `transform`.
test: Re-run generator verification and static checks against the refreshed Phase 14 review artifact; wait for user manual acceptance.
expecting: Refreshed HTML contains the target-placement lock and `is-switching` CSS guard; stale side-toolbar and drawer-shift code remains absent; user confirms the interaction is acceptable.
next_action: None. Debug session closed after user manual acceptance.

## Symptoms
<!-- Written during gathering, then IMMUTABLE -->

expected: 左右翻页表现为当前页滑出屏幕、新页从另一侧滑入；presenter 工具条稳定缩成同一个圆形浮动泡泡；不会出现两个圆或错位圆。
actual: 左右翻页没有表现为完整滑出/滑入；工具条没有稳定缩成同一个圆形浮动泡泡；偶发出现两个圆且不对齐。
errors: 无显式报错，表现为视觉/状态错误。
reproduction: 打开 generated/phase14-presenter-markup-review/school-presentation-first.html，使用 presenter 左右翻页与工具条折叠/展开交互观察。
started: Phase 14 presenter markup review artifact。

## Eliminated
<!-- APPEND only - prevents re-investigating -->

## Evidence
<!-- APPEND only - facts discovered -->

- timestamp: 2026-06-11T11:41:15+08:00
  checked: Memory and required debugger references.
  found: 记忆显示 school-presentation 已锁定 HTML-first playback 方向，Phase 14 presenter markup 目标是 iPad-style 紧凑浮动调色板；通用 bug pattern 中该症状优先匹配 State Management / Async-Timing / CSS transition 状态冲突。
  implication: 本次诊断应聚焦生成脚本与单文件 HTML 中页面状态、动画状态、折叠状态的双重来源或状态竞争。

- timestamp: 2026-06-11T11:46:30+08:00
  checked: git status and repeated reads of skills/school-presentation/scripts/school-presentation.sh.
  found: Worktree is dirty and the source script changed during investigation; generated HTML still contains older markup-palette collapsed CSS.
  implication: Diagnose the checked generated artifact separately from the current script; avoid assuming generated HTML reflects the latest source edits.

- timestamp: 2026-06-11T11:52:00+08:00
  checked: clonePageInto/selectPage in generated HTML and current script.
  found: selectPage passes page direction to clonePageInto on real page changes. clonePageInto uses Web Animations transforms with baseTransform translate(-50%,-50%) plus translateX offsets. This only works if transition shells are absolutely positioned at left:50%, top:50%.
  implication: Any generated artifact with the baseTransform JS but grid-area-only transition CSS, or with absolute CSS but no baseTransform, will produce incorrect slide movement.

- timestamp: 2026-06-11T11:56:00+08:00
  checked: markup palette collapse CSS and syncMarkupPaletteDrawerShift/setMarkupPalettePlacement/setMarkupPaletteCollapsed.
  found: The collapsed palette keeps the full toolbar DOM and translates direct children using --drawer-shift; inactive controls are hidden by opacity/pointer-events, not removed from layout. Placement changes call syncMarkupPaletteDrawerShift before updateMarkupPaletteState writes the new data-placement, so measurements can be taken against the old placement while target math uses the new placement.
  implication: Collapsed state can show two circular visual layers or stale child offsets, especially after placement changes, resize, hover/focus, or auto-hide.

- timestamp: 2026-06-11T12:00:00+08:00
  checked: placement support.
  found: Current placementFromPoint only returns lower-left/lower-right, and CSS only defines those two placements in the latest source snapshot even though Phase 14 context called for lower-left, lower-right, left-side, and right-side.
  implication: Side-edge interactions are collapsed into bottom placements, increasing unexpected movement and making toolbar behavior feel unstable.

- timestamp: 2026-06-11T12:02:24+08:00
  checked: Final source and regenerated Phase 14 review artifact.
  found: `markupPalettePlacementTarget` prevents repeated pointermove events from restarting the same lower-left/lower-right switch animation; `.markup-palette.is-switching` removes CSS `transform` transition while WAAPI owns the side-switch movement. Generated HTML no longer contains `drawer-shift`, `left-side`, `right-side`, `is-slide-page`, `is-entering`, or `is-exiting`.
  implication: The observed "jitter/parry" animation reset has a direct state-machine guard and the toolbar animation is isolated from slide transitions.

- timestamp: 2026-06-11T12:04:55+08:00
  checked: User manual acceptance in the in-app browser.
  found: 用户确认“人工验收通过” for `generated/phase14-presenter-markup-review/school-presentation-first.html`.
  implication: Phase 14 presenter toolbar debug can be closed as resolved.

## Resolution
<!-- OVERWRITE as understanding evolves -->

root_cause: The toolbar side-switch animation was not idempotent. During a lower-left/lower-right switch, `markupPalettePlacement` still held the old placement until the exit animation finished, so repeated pointermove events retriggered the same target placement, canceled the running animation, cleared inline `transform`, and restarted from zero. In addition, the palette's CSS transition still included `transform`, so CSS and WAAPI could both interpolate the same property.
fix: Add `markupPalettePlacementTarget` to ignore duplicate target-placement requests while a switch is running; add `.markup-palette.is-switching` so CSS temporarily leaves `transform` to the WAAPI side-switch animation. Keep slide/page transitions on the restored fade path.
verification: `bash -n skills/school-presentation/scripts/school-presentation.sh`; `git diff --check`; `skills/school-presentation/scripts/school-presentation.sh verify --workdir generated/phase14-presenter-markup-review`; Node parse of generated inline script; `rg` confirmed no stale `drawer-shift`, side-placement, or slide-swipe transition tokens remain. User manual acceptance passed on 2026-06-11.
files_changed:
  - skills/school-presentation/scripts/school-presentation.sh
