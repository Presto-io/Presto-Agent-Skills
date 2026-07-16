# School Presentation Verification Contract

This reference holds detailed verification expectations for the `school-presentation` skill. Keep `SKILL.md` as the concise semantic entry point and update this file when verification behavior changes.

## Verify Command

Run:

```bash
skills/school-presentation/scripts/school-presentation.sh verify --workdir <dir>
```

`<dir>` 必须是 caller-owned、与 normal delivery root 分离的 evidence workdir。命令在其中生成样例、使用独立 delivery 子目录重复渲染、比较稳定性、检查 HTML，并把 manifests 与 `verification-manifest.json` 留在该 workdir；这些文件不是 current artifact。

## Publication Contract

- Normal current 固定为同 stem 的 reviewed Markdown + offline HTML；manifest、verification-manifest、截图、diff、日志、failed HTML 与 browser/PDF 输出不属于 pair。
- renderer 在 `.work/<run-id>/candidate/` 写完整 pair、ephemeral manifest 和明确 referenced `assets/`，再执行 UTF-8/non-empty、size、offline、required DOM token 与 asset resolution gate。
- `--manifest` 只允许显式独立 evidence path；指向 delivery root、`assets/`、`history/` 或 `.work/` 的路径在 current/history mutation 前拒绝。
- required `assets/...` 缺失会阻断发布；安全的 optional fallback 仍由既有 media warning contract 表达。legacy `media/` 不自动迁移，须确认后改写为 `assets/` 并复验。
- exact path-set+bytes 相同是 no-op，不修改 current inode/mtime、不创建 history。changed 将旧 pair 与旧引用 assets 放入同一 `history/<max+1>/`，历史引用必须在 sequence 内解析。
- handled failure、七个标准 fault、INT/TERM 会恢复旧 pair/assets、移除新 history 和 owned work；`sources/` 与 unrelated stale work 不变。SIGKILL/断电和跨文件硬原子不在保证范围。

## Required Verification Coverage

The verification flow must cover:

- Layered manifest hierarchy.
- Preview workspace.
- Playback.
- Overview.
- Reveal hooks.
- Peek.
- Sorting.
- Structured layouts.
- Semantic icons.
- Section divider controls.
- `full_page_image` pages.
- Presenter markup controls.
- Annotation layer hooks.
- Print/export review tokens.
- Offline single-file boundary.
- Delivery-root pollution absence and archived asset reference validity.
- `16:9` and `4:3` fixed-canvas examples.

## Required Manifest Booleans

The verification manifest must record:

- `presenter_markup_verified: true`
- `classroom_structure_verified: true`
- `full_page_image_verified: true`
- `print_review_verified: true`
- `ratio_4x3_verified: true`
- `offline_single_file_verified: true`
- `delivery_roots_clean: true`

The manifest must not contain annotation state, markup palette, stroke data, pinned peek, hover peek, or print control runtime state.

## Entry-Level Verification Checklist

- `skills/school-presentation/scripts/school-presentation.sh example --output <file>` outputs reviewable logical-slide Markdown.
- `render --input <md> --html <html>` generates offline HTML and embeds school logo, slogan, CSS, charts, and embeddable assets.
- `verify --workdir <dir>` repeats render of the same Markdown and proves stable HTML hash.
- Manifest contains `sections -> logical_slides -> physical_pages -> reveal_steps` hierarchy.
- Every physical page has `data-section-index`, `data-logical-index`, `data-physical-index`, `data-global-index`, and `data-page-id` information.
- Output HTML contains preview workspace, thumbnail rail, preview stage, playback, overview, hash sync, keyboard/mouse/touch navigation, and current-page sync logic.
- Output HTML contains ordered reveal, answer masks, and correct-emphasis behavior.
- Preview shows full content and final reveal state; playback controls step visibility.
- Output HTML contains peek cards, sorting number/final reordering, `animate: step`, timeline, cards, gallery, smartart, semantic icons, and section divider controls.
- `layout: full_page_image` records hierarchy in manifest but renders only one full-canvas image and no reveal steps.
- Playback-local pointer, pen, highlighter, eraser, clear/reset controls, and page-scoped annotation layer are present.
- Manifest and Markdown source do not include annotation state.
- `导出最终PDF`, `预览`, and `章节页` bistable controls are present; controls do not use `是/否` text for state.
- One-click final PDF export downloads a PDF with outline/bookmarks and directory links, follows section-page preview state, expands reveal/mask/emphasis/sort, and excludes presenter annotations.
- Cover contains only constrained main title, optional subtitle, and fixed information bar.
- Formula content remains mathematical style, including masked or revealed formulas.
- Output HTML stays under `max_output_mb`; oversized media records fallback instead of forced embedding.
- Oversize HTML、manifest write failure、online reference、required DOM token 缺失或 required asset 缺失均在 publish 前失败，prior current/history 保持不变。
- Fixture deck covers fixed `16:9`/`4:3` ratios, auto directory pages, formulas, tables, charts, images, video fallback, speaker notes, emphasis blocks, auto physical page splitting, and PDF review samples.

## Manual Review Notes

Automated verification proves deterministic structure, candidate publication gates and token coverage. Browser/PDF visual UAT remains required when accepting a new presentation visual feature；`bookmark-pdf` 仍是显式 postprocess helper，不代表自动最终 PDF current。
