# Phase 43: Editable PPTX Renderer and Pagination - Research

**Researched:** 2026-07-14  
**Phase:** 43 — Editable PPTX Renderer and Pagination  
**Mode:** implementation / ecosystem  
**Overall confidence:** High for `python-pptx` object generation and package structure; Medium for visual line fitting across PowerPoint/WPS until Phase 44 manual UAT.

## Executive Summary

Phase 43 is feasible with `python-pptx 1.0.2`, but it should not be planned as one monolithic Markdown-to-PPTX function. The reliable architecture is:

1. call the existing Phase 42 parser in-process and consume its logical document directly;
2. reconcile the manifest gaps introduced by Phase 43 decisions before rendering;
3. paginate into a renderer-owned, deterministic physical-slide plan;
4. emit native editable objects from that plan;
5. inspect and reopen the staged PPTX before atomic publication;
6. publish the authored Markdown plus PPTX while keeping all evidence hidden.

The key capability findings are:

- `python-pptx 1.0.2` has supported APIs for speaker notes, native tables, pictures, and editable group shapes.
- Run-level highlight is represented by standard DrawingML `<a:highlight>` but has no public `Font.highlight_color` API. A tiny, isolated OOXML helper is required.
- `TextFrame.fit_text()` is unsuitable as the pagination authority for Chinese. Its current line fitter splits on whitespace, so a Chinese sentence without spaces is treated as one word; it also overwrites all run bold/italic settings when applying the fit.
- Picture placeholders crop by design. `contain` placement must use `add_picture()` with calculated dimensions and zero crop, not placeholder insertion.
- True atomic replacement of two independent files is not available on POSIX. D-19 can guarantee atomic PPTX replacement; the two-artifact delivery must use staged, individually atomic publication with a documented commit order, or the CLI must own and atomically replace a dedicated output directory.
- The current template manifest is not yet sufficient for D-14: `gallery.caption.empty_slot` is `hide`, there is no `table_name` slot, and the gallery/timeline per-item geometry is implicit. These must be reconciled before emitter implementation.

## Standard Stack

### Required runtime

| Component | Recommendation | Purpose | Confidence |
|---|---|---|---|
| Python | 3.10+ | Existing scripts use modern annotations and standard-library descriptor APIs | High |
| `python-pptx` | Pin/test against `1.0.2`; accept `>=1.0.2,<2` only after regression checks | PPTX package, layouts, shapes, tables, pictures, notes, groups | High |
| Pillow | Use the version installed transitively with `python-pptx`; declare it explicitly in readiness checks | Image dimensions and optional conservative font metrics | High |
| PyYAML | Existing project dependency | Canonical manifest loading through Phase 42 code | High |
| `zipfile` + `lxml`/ElementTree | Standard package inspection; use `python-pptx`'s lxml objects for local OOXML extension | Staged package validation and highlight XML | High |

The current host `python3` does not have `python-pptx` installed. An isolated probe installed the latest stable `python-pptx 1.0.2` and confirmed the APIs below. Phase 43 must therefore provide a bounded dependency error from `render`; Phase 44 will own the aggregate dependency-readiness command under VER-05.

### Confirmed `python-pptx 1.0.2` capabilities

| Contract | API / representation | Finding |
|---|---|---|
| Speaker notes | `slide.notes_slide.notes_text_frame` | Public supported API; accessing `notes_slide` creates one, so only access it when authored notes exist |
| No accidental notes | `slide.has_notes_slide` | Public read-only check; fresh generated slides remain without notes when `notes_slide` is never accessed |
| Native table | `slide.shapes.add_table(...)` | Produces editable `<a:tbl>` inside a graphic frame; row heights, column widths, cell margins, fills, and text are controllable |
| Editable group | `slide.shapes.add_group_shape(shapes)` and `group.shapes` | Public API; a probe round-tripped a picture and caption text box as one `<p:grpSp>` group |
| Picture object | `slide.shapes.add_picture(...)` | Produces replaceable picture objects; explicit width/height enables contain placement |
| Text fitting | `TextFrame.fit_text(...)` | Available but unsuitable as the canonical Chinese pagination engine and destructive to mixed bold styling |
| Run bold | `run.font.bold = True` | Public API |
| Run highlight | DrawingML `<a:highlight><a:schemeClr .../></a:highlight>` | Standard OOXML supported by PowerPoint; no public python-pptx property, so wrap one private-element operation |

Official references:

- `python-pptx` notes slides: <https://python-pptx.readthedocs.io/en/latest/user/notes.html>
- shape and group APIs: <https://python-pptx.readthedocs.io/en/latest/api/shapes.html>
- tables: <https://python-pptx.readthedocs.io/en/latest/user/table.html>
- source/version inspected locally: `python-pptx 1.0.2` installed under an isolated `/tmp` virtual environment.

## Required Contract Reconciliation Before Rendering

### 1. D-14 versus current manifest

The current manifest says:

```yaml
gallery:
  slots:
    - id: caption
      empty_slot: hide
```

D-14 supersedes this: every gallery card must retain an empty editable caption text box, and an absent table name must retain an empty editable table-name text box. Planning should make the reconciliation an explicit first task, not bury it inside rendering code.

Required changes:

- change the gallery empty-caption contract from `hide` to `preserve`;
- add a machine-owned `table_name` slot or a manifest-owned table-name subregion; do not invent its geometry in the emitter;
- define item-level gallery card geometry (picture region plus caption region) for one through four items;
- define timeline node geometry or a deterministic subdivision rule inside `timeline_items`;
- update `template-contract.md` and rerun `template-report` after controlled manifest/template changes.

An empty placeholder should be an empty native text box named predictably, such as `school-pptx:caption-placeholder`, with no prompt string. It is invisible in playback but remains selectable in the selection pane. For gallery, the picture and empty/non-empty caption text box are grouped together.

### 2. Closing layout mapping needs correction

The committed PPTX has five seed slides. Direct XML inspection shows the visually correct closing seed slide uses `ppt/slideLayouts/slideLayout7.xml` (the blank layout), while the manifest declares closing as `slideLayout1.xml` (the cover layout). Rendering both confirms slide 1 is the blue-green cover and slide 5 is the white/blue-green closing page.

The plan must resolve this before relying on manifest mapping. Recommended fix: point `closing.pptx_layout` to `slideLayout7.xml` and assert by relationship in `template-report`. Do not copy the existing seed closing slide unless a layout-only reconstruction proves visually different; adding a blank-layout slide currently inherits the closing design from the controlled master/layout.

### 3. Seed slides must not leak into output

`standard-school.pptx` currently contains five sample slides, and two already have notes-slide relationships. A renderer that merely opens the template and appends slides will violate slide-count, content, and no-accidental-notes requirements.

Use one encapsulated template-bootstrap helper that:

- opens the controlled template;
- resolves slide layouts by OOXML part path from the manifest, never by localized layout name or numeric index;
- removes all seed slide relationships before output generation;
- verifies the resulting presentation has zero physical slides before emit;
- appends exactly one implicit closing page at the end.

`python-pptx` has no public slide-delete API. Isolate the small private `_sldIdLst` / relationship operation in one module and cover it with a package-level regression test. Do not spread private calls throughout emitters.

### 4. D-20/D-21 versus PPTX-13

Phase 43 context intentionally revises PPTX-13. The successful standard output is always exactly:

```text
<stem>.md
<stem>.pptx
```

The Markdown bytes must be preserved as authored. The plan must update the public command contract and the requirement-facing reference so implementation and tests do not retain the older “Markdown only when explicitly requested” behavior.

Recommended CLI:

```bash
skills/school-pptx/scripts/school-pptx.sh render \
  --input <reviewed.md> \
  --out-dir <delivery-dir> \
  [--stem <name>]
```

Using `--out-dir` and one stem makes the two-artifact contract explicit and prevents ambiguous combinations of `--output`, `--copy-markdown`, and unrelated filenames. If backward-compatible `--output <file.pptx>` is preferred, derive the Markdown sibling unconditionally.

## Architecture Patterns

### Recommended module structure

All implementation remains skill-local for SKILL-03:

```text
skills/school-pptx/scripts/
├── school-pptx.sh                 # add render dispatch only
├── markdown_contract.py           # existing canonical parser; import, do not fork
├── pptx_render.py                 # CLI orchestration and status/diagnostics
├── pptx_model.py                  # physical-slide plan dataclasses / typed dicts
├── pptx_paginate.py               # pure deterministic pagination and balancing
├── pptx_emit.py                   # presentation bootstrap and layout dispatch
├── pptx_objects.py                # text, table, picture, group, notes helpers
├── pptx_ooxml.py                  # tiny highlight and slide-removal compatibility layer
└── verify_pptx_renderer.py        # Phase 43 task-local structural regression gate
```

Avoid a second Markdown parser and avoid placing layout-specific conditionals in the CLI. `pptx_paginate.py` should accept only the Phase 42 logical model plus normalized manifest data and return a physical plan that can be serialized in hidden work evidence during tests.

### Pipeline

```text
authored Markdown
    │
    ▼
Phase 42 parse_document() + diagnostics
    │
    ├── errors retained for final non-zero status
    ▼
normalized logical document
    │
    ▼
pure pagination / global balancing
    │
    ▼
physical-slide plan
    │
    ▼
template bootstrap + editable emitters
    │
    ▼
same-directory staged PPTX
    │
    ▼
ZIP/XML + python-pptx reopen validation
    │
    ▼
public Markdown + atomic PPTX replace
```

### Physical-slide plan

Use an explicit intermediate instead of emitting while deciding pagination. Each physical slide should carry at least:

```python
{
    "logical_index": 3,
    "physical_index": 7,
    "layout": "title-content",
    "title": "原 ## 标题",
    "fragment_index": 1,
    "fragments": [...],
    "notes": {...} | None,
    "source_line": 24,
}
```

This plan is essential for deterministic contents/timeline balancing, notes propagation, affected-slide diagnostics, and Phase 44 verification. It stays hidden and is not a third public artifact.

## Pagination Architecture

### Shared measurement model

Do not use character count alone and do not delegate pagination to PowerPoint autofit. Build a conservative `TextMeasure` abstraction that returns estimated display lines and height for a width, font size, and text.

Recommended rules:

- treat explicit newlines as hard line boundaries;
- measure CJK characters and punctuation individually using Pillow when a deterministic font file is available;
- keep a conservative East-Asian-width fallback so missing host fonts do not make rendering impossible;
- account for paragraph spacing, list bullet/hanging indent, subheading height, cell margins, and code indentation;
- use manifest min/max font sizes as hard bounds;
- set `word_wrap=True` and `auto_size=NONE` in emitted text frames so PowerPoint does not later choose a different shrink policy;
- use measurement to choose page fragments and font size, then structurally inspect for overflow proxies; Phase 44 visual UAT remains the final cross-viewer truth.

`TextFrame.fit_text()` must not be the authority because its current `_LineSource` uses `text.split()`. A long Chinese sentence without spaces is treated as a single token. Its `_apply_fit()` also applies one bold value to every run, which would destroy D-15 mixed bold semantics.

### Paragraphs and lists

Implement D-01 through D-05 as a two-stage operation:

1. greedily fill complete top-level blocks in source order;
2. only when one block cannot fit an empty page, split that block semantically.

Paragraph split priority:

1. sentence terminators `。！？!?；;` including trailing quotes/brackets;
2. weaker punctuation `，、：:` or natural pause;
3. grapheme-safe hard split only for a single overlong sentence.

List split priority:

- only between complete items;
- if one item exceeds a full page, apply the paragraph splitter inside that item while retaining bullet context;
- repeat the original visible `###` heading on every fragment without “续”.

Use a real grapheme iterator or at minimum avoid splitting before combining marks, variation selectors, and surrogate-equivalent emoji sequences. Do not use raw byte or arbitrary UTF-16 offsets.

### Code

Code pagination uses source lines as indivisible logical units. For each line, estimate its soft-wrapped display-line count at the selected monospace size. Break only between source lines. Preserve the original code text exactly; do not insert newlines to represent soft wraps.

If one source line alone exceeds the available physical height after soft wrapping, retain that complete line on one page at the minimum allowed size and emit a bounded best-effort diagnostic if it still cannot fit. Do not silently truncate.

The code emitter should use one editable text frame, a template-controlled monospace font, stable fill/background, explicit margins, `word_wrap=True`, and no syntax highlighting.

### Tables

For each candidate font size in the manifest range, estimate each row height as the maximum wrapped cell height plus cell margins. Keep rows intact. Page capacity includes:

- empty or authored table-name text box;
- repeated native table header;
- complete data rows only.

Choose the page/font combination with a lexicographic cost:

1. no overflow or truncation;
2. no visually isolated wrapped line;
3. fewest pages;
4. smallest deviation from preferred font size;
5. most even page heights.

This allows D-08's counterintuitive but intentional rule: if shrinking produces a single visible trailing line in a cell, a larger font can be selected to reflow the cell into a visually better multi-line block. The search must consider the entire table page, not mutate one cell independently after pagination.

Each physical page gets a new native table object. Continuations repeat the header. The slide `##` title never changes. If and only if the source table name exists, continuation table-name text becomes `原表名（续）`; an absent name leaves the preserved text box empty.

### Timelines and contents: global balancing

Do not greedily paginate and repair only the last two pages. Use contiguous-partition dynamic programming.

For each item, calculate a visual weight from wrapped line count/height. For a proposed page count `k`, partition the ordered sequence into `k` contiguous groups under page capacity. Minimize a deterministic lexicographic cost:

```text
capacity violations
→ forbidden orphan count
→ max item-count difference
→ variance from target visual weight
→ total unused height
→ earliest stable split points
```

Timeline constraints:

- normally every partition has at least three nodes;
- preserve chronological order;
- choose the fewest feasible pages at readable font sizes;
- if a valid `>=3` partition is mathematically impossible for a timeline of 3+ items, generate a best-effort partition, record a stable `TIMELINE_BALANCE_INFEASIBLE` error, and exit non-zero rather than hiding the violation.

That infeasibility case matters for 4–5 extremely tall nodes: any two-page partition necessarily leaves a page with fewer than three nodes, while one page may exceed capacity. The plan must define this behavior explicitly.

Contents constraints:

- retain continuous numbering across physical pages;
- every physical title is exactly `目录`;
- first minimize item-count imbalance (normally counts differ by at most one), then minimize wrapped-height imbalance;
- permit a larger count difference only when required to avoid actual overflow from a very long entry;
- never add a continuation suffix.

### Gallery and image-text

Gallery pagination is deterministic chunks of at most four images, but card geometry should depend on actual chunk size (1, 2, 3, or 4) through manifest-owned presets. Every card contains:

- one replaceable picture object;
- one editable caption text box, even when empty;
- one editable group containing both.

For `image-text`, each primary image produces one physical page with the same title, stable body, and notes. Body pagination, if independently required, must be resolved before multiplying across images; define the cartesian behavior in the physical plan rather than inside the emitter.

## Editable Object Emission

### Native text and inline runs

Create continuous text frames and runs. The logical model supplies authored text plus span offsets. Convert this to plain-text run segments once in a model-normalization helper; do not reparse the Markdown document.

Be careful: the current offsets include Markdown delimiters because `inline_spans()` records `match.start()` and `match.end()` over the authored string. The normalization helper must remove `**` and `==` delimiters while preserving the intended text. Add tests for adjacent and mixed bold/highlight spans. If nested/overlapping spans are not supported, reject them with a stable diagnostic rather than producing malformed run order.

Bold uses `run.font.bold = True`. Highlight should use one isolated helper similar to:

```python
def set_run_highlight(run, scheme_color: str) -> None:
    r_pr = run._r.get_or_add_rPr()
    highlight = OxmlElement("a:highlight")
    color = OxmlElement("a:schemeClr")
    color.set("val", scheme_color)
    highlight.append(color)
    r_pr.insert_element_before(
        highlight,
        "a:uLnTx", "a:uLn", "a:uFillTx", "a:uFill",
        "a:latin", "a:ea", "a:cs", "a:sym",
        "a:hlinkClick", "a:hlinkMouseOver", "a:rtl", "a:extLst",
    )
```

The exact scheme color must be template-owned. Add an explicit manifest theme token such as `inline_styles.highlight.scheme_color`, rather than hard-coding an RGB value in the renderer.

### Native table

Use `slide.shapes.add_table()` at manifest geometry and set explicit column widths and computed row heights. Keep headers/data in the table object's cell text frames. Decorative shapes may surround it, but never replace the `<a:tbl>` data structure.

Do not rely on a generic content placeholder's insertion API when its type is not a table placeholder; direct `add_table()` at the controlled slot geometry is predictable.

### Editable groups

Use public `add_group_shape()` for:

- each timeline node: marker, time, title, description;
- each gallery card: picture and caption text box.

Keep the timeline axis separate. A local capability probe created, saved, and reopened a picture-plus-caption group successfully; the reopened group retained two native children and the package contained `<p:grpSp>`. Cross-viewer movement/editing remains a Phase 44 PowerPoint/WPS UAT item.

### Speaker notes

For every physical slide derived from a logical slide with notes:

```python
text_frame = slide.notes_slide.notes_text_frame
if text_frame is None:
    # bounded package/template error
text_frame.text = notes_markdown
```

For a slide without notes, never access `slide.notes_slide`. This is the only reliable way to avoid creating accidental notes parts. After generation, assert that each expected slide has one notes relationship and every unexpected slide has none.

The template already includes a notes master, so newly created notes slides inherit the controlled notes-page structure.

### Contain images

Use intrinsic image pixels only for aspect ratio:

```python
scale = min(slot_width / image_width, slot_height / image_height)
width = image_width * scale
height = image_height * scale
left = slot_left + (slot_width - width) / 2
top = slot_top + (slot_height - height) / 2
picture = shapes.add_picture(path, left, top, width, height)
```

Do not use `PicturePlaceholder.insert_picture()`, which fills and crops. Assert `crop_left/right/top/bottom == 0` after reopen. Missing media uses a safe editable placeholder shape from the logical model; it must not trigger network access or path fallback.

## Failure and Publication Semantics

### Best-effort invalid input

Separate three outcomes:

1. **valid model + valid PPTX:** publish both artifacts, exit 0;
2. **invalid model but structurally valid best-effort PPTX:** publish authored Markdown and requested PPTX, print a prominent bounded summary with affected logical slides, exit non-zero;
3. **unrecoverable renderer/package failure:** do not replace the previous PPTX, clean same-directory temporary files, exit non-zero.

Missing media belongs to outcome 2 and should render an editable safe placeholder. Invalid syntax that leaves too little model data should still produce a non-empty template-based deck when safe, at minimum preserving recoverable slides and the implicit closing page. Never add warning slides, banners, or watermarks.

The CLI summary should begin with an unmistakable status such as `渲染完成但输入存在异常` and end with a direct statement that the artifact is not a successful render. Limit printed diagnostics using the Phase 42 bounded model, but include every affected slide identifier represented in the bounded set.

### Atomic replacement and two files

Use Phase 42's held no-follow directory-descriptor pattern for output safety. Prepare temporary Markdown and PPTX files in the destination directory, `fsync` files where supported, validate the staged PPTX, and publish with descriptor-relative `os.replace()`.

Important limitation: two independent `os.replace()` calls are not one atomic transaction. Recommended behavior for a normal existing directory:

1. stage and validate both files;
2. atomically replace Markdown first;
3. atomically replace PPTX last as the commit artifact;
4. on startup, clean only renderer-owned stale temp names after identity checks;
5. optionally embed the source SHA-256 in PPTX core/custom properties for mismatch diagnosis, while keeping it out of visible slides.

D-19's guarantee remains exact for PPTX: a build failure before PPTX publication preserves the old target. If the product requires genuinely atomic pair replacement, the command must own a dedicated delivery directory and atomically rename the entire directory; this cannot be promised for two files inside an arbitrary existing directory.

Do not emit `.bak`, logical JSON, manifest copies, logs, or evidence in the public delivery root. Hidden work paths are allowed for explicit verification only.

## Don't Hand-Roll

- Do not hand-build the OPC ZIP package, relationships, content types, slide layouts, native tables, notes parts, or group transforms. Use `python-pptx` and isolate only unsupported XML details.
- Do not build a second Markdown parser. Import the skill-local Phase 42 producer and consume its returned logical model.
- Do not use text-box matrices as tables. Use native `<a:tbl>` objects.
- Do not rasterize whole slides, timelines, tables, code, or captions.
- Do not use PowerPoint auto-fit as pagination. Decide pagination before emission.
- Do not use placeholder picture insertion for contain behavior.
- Do not greedily patch only the last timeline/contents page. Solve the ordered partition globally.
- Do not claim a two-file atomic transaction when using two file replacements.
- Do not create notes slides for slides with no authored notes.
- Do not hard-code localized layout names, layout indices, raw coordinates, fonts, or RGB highlight colors in emitters.

## Common Pitfalls

### Pitfall 1: fitting after runs are styled

`TextFrame.fit_text()` applies one family, size, bold, and italic value to every run. Calling it after constructing mixed bold text removes the intended run distinction. Choose the font size first, then emit runs.

### Pitfall 2: Chinese line measurement by whitespace

The library's current fitter uses `.split()`. Chinese text without spaces is one token, producing unreliable wrap/fit results. Use the renderer's CJK-aware estimator.

### Pitfall 3: template seed leakage

Appending to the committed template leaves five sample slides and two existing notes parts in output. Strip seed slides before emitting.

### Pitfall 4: wrong closing page

The current manifest points closing to the cover layout, while the actual closing seed uses the blank layout. Reconcile and test the relationship.

### Pitfall 5: invisible but absent placeholders

An empty caption/table name must exist as an editable text shape, not merely be omitted. Structural verification should count these shapes and inspect their names/text.

### Pitfall 6: grouping pictures without round-trip checks

Pictures carry slide relationships. Grouping works in `python-pptx 1.0.2`, but verify save/reopen and image relationships after moving shapes into groups.

### Pitfall 7: table pagination based on row count

Rows with wrapped Chinese text have different heights. Paginate using computed row heights, not `max_lines` as a row-count alias.

### Pitfall 8: invalid best-effort artifact reported as success

Artifact existence does not imply success. Exit non-zero whenever parser/render diagnostics contain errors, even when a usable PPTX was published.

### Pitfall 9: stale outputs after failed build

Never truncate the final PPTX path before the package is complete and reopened successfully. Build in the destination directory and replace only after validation.

### Pitfall 10: relying on PowerPoint-only visual behavior

Structural OOXML validity is not sufficient evidence of WPS editing, group movement, highlight display, or exact wrapping. Keep cross-viewer visual/manual checks in Phase 44.

## Verification Architecture

Phase 43 should add task-local automated verification without taking over Phase 44's public aggregate `verify` command or manual UAT.

### Unit-level pagination tests

- paragraph sentence splitting, punctuation fallback, and one-sentence hard split;
- list split only between items except one oversized item;
- code split only between source lines with soft-wrap accounting;
- table row-height estimation and header repetition;
- table name continuation only when authored;
- gallery chunks `1/2/3/4/5/6/8/9` with an empty caption placeholder case;
- timeline DP balance, one-item orphan avoidance, all-page rebalance, and infeasible 4/5-node tall-item case;
- contents count-first then visual-weight balance;
- deterministic plan equality across repeated runs.

### Structural PPTX tests

Open the generated file with both `zipfile` and `python-pptx` and assert:

- valid non-empty ZIP and successful reopen;
- expected physical slide count and exactly one closing slide;
- no seed sample text;
- each physical slide uses the manifest-mapped layout relationship;
- visible text is in text shapes/runs, including code and timeline labels;
- every table page contains one native `<a:tbl>`, repeated headers, and intact rows;
- media are picture objects with valid relationships and zero crop;
- gallery/timeline nodes contain `<p:grpSp>` with native children;
- every gallery item has a caption text box, including empty caption cases;
- every table page has a table-name text box, including empty-name cases;
- `<a:highlight>` uses a theme scheme color and bold runs retain `b="1"`;
- notes exist on all and only physical slides derived from noted logical slides;
- code text round-trips exactly, including source newlines and long-line content;
- there is no full-slide screenshot shortcut;
- public output root contains exactly `<stem>.md` and `<stem>.pptx` after success;
- invalid missing-media fixture publishes best-effort PPTX but exits non-zero;
- unrecoverable staged-PPTX failure preserves the previous target.

### Viewer smoke test boundary

Headless LibreOffice/PDF rendering can be used as an optional Phase 43 smoke test for gross corruption, but it must not become the visual acceptance oracle. Phase 44 owns PowerPoint/WPS editability and visual UAT evidence.

## Requirement Coverage and Planning Implications

| Requirement | Implementation implication | Primary verification |
|---|---|---|
| PPTX-01 | Open normalized template, strip seeds, emit all logical slides plus one closing | Non-empty valid PPTX, expected slide count |
| PPTX-02 | Native text, picture, table, and group objects only | XML object inventory; no full-slide image |
| PPTX-03 | Text frames for body, code, timeline labels, captions | Shape/run inspection and reopen |
| PPTX-04 | `add_table()` per physical table page | `<a:tbl>`, row/column structure |
| PPTX-05 | Manual contain calculation with `add_picture()` | Aspect ratio and zero crop |
| PPTX-06 | Gallery chunks of at most four, manifest-owned card presets | Pagination plan and group counts |
| PPTX-07 | Horizontal timeline groups and global DP pagination | Node order/count/weight assertions |
| PPTX-08 | Pure paginator for text/table/timeline/gallery/code | Logical-to-physical plan tests |
| PPTX-09 | Header repeat; only authored table name gets `（续）` | Continuation text/table assertions |
| PPTX-10 | One editable monospace text frame per code page | Exact code text and font/background properties |
| PPTX-11 | Conditional notes API access and propagation | Notes relationships exactly match plan |
| PPTX-12 | Choose `none` for v1.17 unless preservation is proven stable | Assert no generated transition and report mode internally as `none` |
| PPTX-13 | Reconcile to D-20/D-21: always two same-stem artifacts, no public evidence | Directory inventory and contract update |
| VER-03 | Add repeatable `render` dispatch; invalid input remains non-zero even with best-effort PPTX | Positive and negative CLI tests |
| SKILL-03 | All modules and helpers under `skills/school-pptx/scripts/`; no sibling runtime calls | Import/call graph audit |

## Recommended Plan Decomposition

### Plan 43-01 — Contracts, dependency boundary, and physical model

- reconcile manifest/template for D-14, table name, gallery/timeline geometry, highlight token, and closing mapping;
- add bounded dependency checks;
- define physical-slide plan and CJK-aware measurement primitives;
- add pure pagination unit tests.

### Plan 43-02 — Global pagination

- implement text/list/code splitters;
- implement native-table row sizing and pagination planning;
- implement global timeline/contents partitioning;
- implement gallery/image-text expansion and notes propagation in the plan.

### Plan 43-03 — Editable emitters

- bootstrap/strip template seed slides;
- emit native text/runs, tables, contain pictures, groups, code, and notes;
- add isolated OOXML highlight helper;
- stage and structurally validate a full fixture PPTX.

### Plan 43-04 — Render CLI, best-effort failure, and publication

- add `render` to `school-pptx.sh`;
- publish exactly Markdown + PPTX with secure staged replacement;
- implement non-zero best-effort diagnostics and affected-slide summary;
- run positive full fixture, missing-media negative, replacement-preservation, determinism, and public-directory cleanliness gates.

This four-plan split keeps contract changes ahead of emitters and keeps publication/failure semantics separate from pagination logic. With the repository's coarse granularity, 43-01 and 43-02 may be merged only if the manifest reconciliation is still completed before any emitter task begins.

## Open Risks for Planning

| Risk | Impact | Mitigation | Confidence |
|---|---|---|---|
| PowerPoint/WPS line wrapping differs from estimator | Visual orphan/overflow despite structural pass | Conservative budgets, explicit font sizes, Phase 44 UAT | Medium |
| Required CJK font absent on runtime | Measurement and appearance drift | Theme font discovery, deterministic fallback estimator, readiness warning | Medium |
| Private slide-removal API changes | Seed slides remain or package breaks | One compatibility helper, pin/test 1.0.2, ZIP assertions | High |
| Run highlight OOXML ordering/compatibility | Highlight lost or repaired by viewer | One helper using schema order, reopen/XML test, PowerPoint/WPS UAT | Medium-High |
| Group editing differs in WPS | User cannot conveniently move/edit node/card | Standard `<p:grpSp>`, structural round trip, Phase 44 WPS test | Medium |
| Timeline minimum-three rule infeasible | No partition satisfies D-09 | Explicit infeasible diagnostic + best-effort non-zero artifact | High |
| Two-file transaction interrupted between replaces | Markdown/PPTX stems can temporarily mismatch | PPTX-last commit order, source hash, or dedicated directory swap | High |
| Manifest geometry gaps remain implicit | Renderer hard-codes layout geometry | Make reconciliation a blocking first task | High |

## Final Prescriptive Guidance

Use `python-pptx 1.0.2` as the primary renderer, public APIs for notes/tables/groups/pictures, and one narrowly tested OOXML helper for run highlight. Put all pagination in a pure physical-plan stage and use global ordered partitioning for timeline and contents. Do not rely on PowerPoint autofit for Chinese. Reconcile D-14, the absent table-name slot, per-item geometry, the closing mapping, and D-20/D-21 before implementation. Treat invalid best-effort PPTX publication as a non-zero failure outcome, and state the limits of two-file atomicity honestly.

## RESEARCH COMPLETE
