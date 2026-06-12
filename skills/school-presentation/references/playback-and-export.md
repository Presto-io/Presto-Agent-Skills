# School Presentation Playback and Export Reference

This reference holds playback, preview workspace, presenter markup, and PDF export rules for the `school-presentation` skill. Keep `SKILL.md` as the concise semantic entry point and update this file when long interaction behavior changes.

## Rendered Deck Shell

`skills/school-presentation/scripts/school-presentation.sh render` outputs offline HTML. The generated result defaults to a preview workspace:

- Left thumbnail rail grouped by section and logical slide.
- Right preview stage showing the current physical page's real slide DOM.
- The same single-file HTML also contains playback and overview.
- Preview workspace shows full content and final reveal state.
- Playback controls reveal steps, masking, emphasis, and navigation state.

## Playback Navigation

Playback supports:

- Keyboard arrow keys
- Space
- PageUp/PageDown
- Mouse left/middle/right click regions
- Touch swipes
- `Esc` to return to workspace
- URL hash synchronization for current page and step
- Top blue-green progress bar

Forward navigation with right arrow, Space, or right/middle click first advances the current page reveal step; once complete, it turns the page. Backward navigation with left arrow or left click first reverses the current page step.

When crossing pages:

- The old page fades out according to its current revealed state.
- The newly entered page always starts from original step 0 masking state.
- Advancing beyond the last completed page exits playback mode.

## Reveal, Mask, Emphasis, and Peek Semantics

- `order` is playback priority and may be decimal for insertion.
- The renderer sorts by numeric priority and normalizes manifest values to continuous `step_index`.
- Elements with the same `order` appear simultaneously.
- Answer masks hide answers in playback without adding “click to reveal” prompt text.
- Emphasis defaults to underline, remains visible in print/static review, and only plays entrance animation the first time that step appears.
- Peek is supplementary information. It does not replace click-based reveal and does not write runtime pinned/hover state to manifest.

## Presenter Markup

Playback includes a presenter markup palette:

- Laser pointer
- Pen
- Highlighter
- Eraser
- Clear current page

Rules:

- Markup affects only the current browser playback session.
- The floating palette docks based on mouse or touch edge intent.
- Pen, highlighter, and eraser annotations are page-scoped session state by physical page.
- Returning to a page preserves its session annotations until the user clears that page.
- Laser pointer drag shows a temporary red trail; after release, it begins fading after about 2 seconds.
- Annotation layers attach only to the playback shell.
- Markup must not write back to Markdown, `.page-source`, preview workspace, overview, thumbnails, manifest, or deterministic review artifacts.
- Drawing and erasing suppress playback click regions while active.
- Keyboard navigation, reveal, mask, emphasis, and hover/peek continue under normal rules outside drawing state.

## Final PDF Export

Generated decks include a `导出最终PDF` control that directly generates and downloads the final PDF from the offline HTML.

- It does not depend on the system print dialog.
- It does not require a post-processing command.
- Export follows manifest physical page order.
- The PDF includes reader-readable outline/bookmarks.
- Directory pages get jump links.
- Reveal content is expanded.
- Mask answers are visible.
- Emphasis keeps underline.
- Sorting exercises use final order.
- Section divider inclusion follows the current `章节页` preview button state.
- If section dividers are skipped, PDF outline and directory links must point to the first visible content page for each section.
- PDF export state belongs to the generated deck UI and must not be written to Markdown or manifest.
- Presenter annotation layer, markup palette, laser trail, pinned peek, hover state, and other runtime state are excluded by default.
- For one-click closure and low-performance-device speed, final PDF pages use a fixed-canvas visual grid; text selectability/copyability is not promised.

## PDF UAT

PDF UAT should click `导出最终PDF` inside the offline HTML and confirm:

- The downloaded PDF opens in a PDF reader.
- Outline/bookmarks are readable.
- Directory page links jump.
- Page count matches manifest physical pages.
- Reveal content is expanded.
- Mask answers are visible.
- Emphasis underline is visible.
- Sorting uses final order.
- Section pages can be included or skipped without reordering later pages.
- Auto-inserted pages and split pages remain in correct order.
- Gallery cards are not truncated.
- Presenter annotations are excluded by default.
- `16:9` and `4:3` examples preserve fixed canvas ratios.
