# Architecture Patterns

**Domain:** school-pptx editable school PowerPoint workflow  
**Project:** Presto Agent Skills v1.17 `school-pptx`  
**Researched:** 2026-07-13  
**Overall confidence:** HIGH for repository architecture and phase ordering; MEDIUM for exact PPTX library behavior until local fixture proof exists.

## Recommended Architecture

`school-pptx` should be a new standalone skill under `skills/school-pptx/`, not an extension of `school-presentation`. Reuse the proven repository pattern, but keep the output line separate:

```text
source materials / supplied POTX
  -> hand-normalized standard PPTX template + manifest
  -> teacher-reviewable Markdown logical deck
  -> skill-local Markdown parser and pagination model
  -> editable PPTX renderer
  -> hidden verification evidence + public PPTX output
```

The core rule is: **template owns geometry and style; Markdown owns logical content; renderer owns physical slide splitting and fitting.** This mirrors the accepted `school-presentation` model of logical pages becoming physical pages, and the `tiaokedan` discipline of locking a hand-authored target surface before scripting. It also prevents the new skill from reopening the unstable PPTX export scope of `school-presentation`.

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|----------------|-------------------|
| `SKILL.md` | Trigger, objective, high-level workflow, command pointers, runtime adapter notes, safety | `references/`, `templates/`, `scripts/` |
| `templates/school-pptx.md` | Copyable teacher-reviewable Markdown logical deck fixture | Markdown parser |
| `templates/school-standard.pptx` | Normalized machine-mappable PowerPoint template derived from the supplied `.potx` visual sample | Renderer, template validator |
| `references/markdown-contract.md` | YAML + `::: slide {layout="..."}` authoring contract, review markers, layout names, speaker-note syntax | `SKILL.md`, parser, validator |
| `references/template-normalization.md` | Human POTX -> standard PPTX process, placeholder naming, accepted layout inventory | Template authoring phase, validator |
| `references/template-manifest.yaml` | Machine-readable layout/slot/budget map for the standard template | Renderer, verifier |
| `references/rendering-and-pagination.md` | Logical-to-physical slide rules, overflow budgets, fixed/flexible slot behavior | Renderer, roadmap plans |
| `references/verification-contract.md` | Required checks, manifest booleans, artifact boundaries, UAT expectations | `verify` command |
| `scripts/school-pptx.sh` | Stable public command surface | Python modules |
| `scripts/school_pptx/` | Internal parser, template inspector, layout engine, PPTX writer, verifier | Shell wrapper only |
| `test/1.17/school-pptx/` | Versioned deterministic fixtures and expected verification evidence | Phase verification |

## Recommended Skill-Local Directory Structure

```text
skills/school-pptx/
├── SKILL.md
├── references/
│   ├── markdown-contract.md
│   ├── template-normalization.md
│   ├── template-manifest.yaml
│   ├── rendering-and-pagination.md
│   └── verification-contract.md
├── templates/
│   ├── school-pptx.md
│   └── school-standard.pptx
└── scripts/
    ├── school-pptx.sh
    └── school_pptx/
        ├── __init__.py
        ├── cli.py
        ├── markdown_parser.py
        ├── template_model.py
        ├── pagination.py
        ├── fit.py
        ├── pptx_writer.py
        ├── ooxml_inspector.py
        └── verify.py
```

Do not put the template manifest in a root-level shared schema. It is specific to this skill and to the normalized school PPTX template. The `.pptx` belongs in `templates/` because it is a runtime template copied/loaded for rendering. The manifest and slot map belong in `references/` because they are the skill-local rendering contract and validation source; scripts may read them, but they are not teacher-facing output templates.

## Recommended Command Surface

Use one stable shell wrapper, with Python internals hidden behind it:

```bash
skills/school-pptx/scripts/school-pptx.sh example \
  --output school-pptx-full.md

skills/school-pptx/scripts/school-pptx.sh template-report \
  --template skills/school-pptx/templates/school-standard.pptx \
  --manifest skills/school-pptx/references/template-manifest.yaml \
  --output build/school-pptx/template-report.json

skills/school-pptx/scripts/school-pptx.sh render \
  --input school-pptx-full.md \
  --pptx build/school-pptx/school-pptx-full.pptx \
  --manifest build/school-pptx/school-pptx-manifest.json

skills/school-pptx/scripts/school-pptx.sh verify \
  --workdir /tmp/school-pptx-verify
```

Optional phase-local commands can exist for authoring the standard template, but they should not become the normal teacher workflow:

```bash
skills/school-pptx/scripts/school-pptx.sh template-report \
  --template /path/to/supplied-human-sample.potx \
  --output /tmp/supplied-potx-inspection.json
```

Avoid `normalize-template` as an automatic promise unless the phase proves it can safely rewrite POTX files. The reliable architecture is human normalization first, script validation second.

## Markdown Contract Shape

The Markdown contract should be `YAML frontmatter + explicit slide blocks`:

```markdown
---
template: school-pptx
theme: school-standard
title: 示例课件标题
subtitle: 可选副标题
author: 张老师
date: 2026-07-13
---

# 示例课件标题

::: slide {layout="cover"}
:::

## 一、项目背景

::: slide {layout="title-content" notes="本页讲清背景。"}
### 背景与目标

- 要点一
- 要点二
:::
```

Rules:

- `theme` is a controlled template identifier, not arbitrary styling.
- `#` is only a document-title fallback.
- `##` headings define sections and feed the auto contents slide.
- `::: slide {layout="..."}` creates one logical slide.
- Markdown authors may choose allowed layout names but must not provide coordinates, font sizes, colors, placeholder ids, crop values, animation XML, or arbitrary PPTX styling.
- Speaker notes are Markdown-owned content, rendered into PPTX notes where supported and verified by OOXML inspection.

## Layout Inventory and Slot Map

v1.17 should start with this fixed layout set:

| Layout | Required Slots | Pagination Behavior |
|--------|----------------|---------------------|
| `cover` | `title`, `subtitle`, `meta` | No body overflow; cover body ignored or rejected |
| `contents` | `title`, `items` | Auto-generated from `##`; splits after item budget |
| `section` | `section_title`, `section_index` | One physical slide per section divider |
| `title-content` | `title`, `body` | Body chunks split by text budget |
| `two-column` | `title`, `left`, `right` | Split by paired column budget |
| `image-text` | `title`, `image`, `body`, `caption` | Image contain placement; body may split |
| `table` | `title`, `table`, `caption` | Split by row budget, repeat header |
| `timeline` | `title`, `timeline` | Split by event count, preserve order |
| `gallery` | `title`, `images`, `captions` | Four-image physical pages, overflow continues |
| `code` | `title`, `code`, `caption` | Plain code text, no syntax highlighting in v1.17 |
| `closing` | `title`, `subtitle`, `meta` | No overflow |

The manifest should map each layout to PowerPoint slide layout identity, placeholder ids, slot kinds, budgets, and overflow strategy. Example shape:

```yaml
theme: school-standard
page:
  width_in: 13.333
  height_in: 7.5
layouts:
  title-content:
    pptx_layout_name: "SP_TITLE_CONTENT"
    slots:
      title:
        placeholder_idx: 10
        kind: text
        required: true
        fit: fixed
      body:
        placeholder_idx: 11
        kind: rich_text
        required: true
        fit: elastic_text
        max_lines: 12
        min_font_pt: 18
        split: by_block
```

Use stable placeholder `idx` values and names in the normalized template. python-pptx documentation states placeholder lookup by `idx` is stable and not simply list position, which makes it suitable for this slot map. Picture placeholder insertion crops to fill, so the renderer should prefer explicit image placement for contain behavior unless crop semantics are intentionally configured.

## Human POTX to Machine-Mappable Template

The supplied `.potx` should be treated as visual evidence, not directly as the render contract. Recommended process:

1. Inspect the supplied POTX manually and with `template-report` to capture slide size, masters, layouts, placeholder names, and sample shapes.
2. Create `templates/school-standard.pptx` by hand in PowerPoint/WPS/Keynote-compatible PowerPoint export: one master, one slide layout per supported `layout`, placeholder names prefixed with stable slot ids, no duplicate ambiguous placeholders.
3. Assign explicit placeholder `idx` values for user-added placeholders where possible; keep names like `SP_SLOT_title`, `SP_SLOT_body`, `SP_SLOT_image`.
4. Write `references/template-manifest.yaml` against that normalized template, not against the raw POTX.
5. Run `template-report` and commit phase evidence showing every manifest slot maps to a real placeholder or declared shape frame.
6. Do not let Markdown select arbitrary layouts from the raw POTX or rely on visual shape order.

This gives humans a familiar PPTX template to edit while giving the renderer a deterministic slot API. If future users bring another school template, it should be a new controlled `theme` with its own normalized `.pptx` and manifest, not marketplace autodetection.

## Logical Slide to Physical Slide Pagination

Keep the hierarchy from `school-presentation`, adapted for PPTX:

```text
sections -> logical_slides -> physical_slides -> slots
```

Pagination should happen before writing PPTX. The parser creates logical slides; the layout engine calculates one or more physical slide payloads; the writer only fills a known layout payload.

Rules:

- Contents slides are generated from every `##` heading and split by manifest item budget.
- A logical slide never changes layout mid-stream; overflow creates continuation slides with the same layout plus continuation markers in the manifest.
- Text splits by Markdown block first, then list item, then sentence/line only as a last resort.
- Tables split by rows and repeat the header row on continuation slides.
- Timelines split by event count and preserve chronological order.
- Galleries split into four-image physical slides.
- Code blocks split by line count; v1.17 keeps non-highlighted editable text.
- Speaker notes should attach to the first physical slide by default, with optional continuation notes recording `continued_from`.

The output manifest should record:

```json
{
  "sections": [],
  "logical_slides": [],
  "physical_slides": [],
  "layout_usage": {},
  "pagination": {
    "logical_to_physical": {},
    "overflow_events": []
  },
  "template": {
    "theme": "school-standard",
    "template_sha256": "...",
    "manifest_sha256": "..."
  },
  "verification": {}
}
```

## Fixed Slots and Elastic Text Boxes

Use two categories, both renderer-owned:

| Slot Type | Behavior | Use For |
|-----------|----------|---------|
| Fixed slot | Position, size, font role, alignment, and object type are fixed by manifest/template. Content must fit or paginate. | cover meta, section title, image frame, gallery cells, table frame |
| Elastic text slot | Frame is fixed, but renderer may reduce font within a bounded range and adjust paragraph spacing before paginating. | body, two-column text, captions, code |

Recommended fitting order:

1. Fill slot with template role defaults.
2. Measure by conservative character/line budget from manifest.
3. If slightly over budget, reduce font size down to `min_font_pt`.
4. If still over budget, split into continuation physical slides.
5. If unsplittable content still cannot fit, fail non-zero and write hidden diagnostics.

Do not expose these knobs in Markdown. Do not implement freeform `x/y/w/h`, per-slide font sizes, or arbitrary color overrides. Template consistency depends on keeping layout knobs out of the teacher-maintained source.

## PPTX Writer Choice

Prefer Python for v1.17 because the repository already uses shell wrappers plus Python scripts for skill-local renderers, and this keeps runtime expectations close to existing skills. Use `python-pptx` as the first implementation candidate because its official documentation covers adding slides, placeholders, text, images, tables, charts, and notes slides, while also warning that the PPTX format has unsupported features. That means the renderer should pair high-level `python-pptx` writes with OOXML inspection for verification and avoid claiming support for transitions/animations until proven locally.

Important constraints from current docs:

- Placeholders can be located by stable `idx` keys.
- Picture placeholder insertion may crop to fill; contain-style image placement should be implemented explicitly rather than relying on `insert_picture` defaults.
- Notes slides are modeled and can hold notes text, but the first local fixture must verify PowerPoint/WPS/Keynote compatibility before notes are considered passed.
- Complex transitions and object animations should remain out of v1.17 unless a local OOXML fixture proves reliable preservation.

## Verification Artifacts

Successful public output should stay clean:

```text
build/school-pptx/
├── school-pptx-full.pptx
├── school-pptx-full.md          # optional copied source, only if explicitly requested
└── .school-pptx/
    ├── school-pptx-manifest.json
    ├── template-report.json
    ├── ooxml-inspection.json
    ├── media-report.json
    └── verification.json
```

For phase evidence, commit deterministic fixtures under `test/1.17/school-pptx/` only when they are small, sanitized, and explicitly needed for regression:

```text
test/1.17/school-pptx/
├── school-pptx-full.md
├── expected-template-report.json
├── expected-manifest.json
└── README.md
```

The verification command should check:

- `python3 -m py_compile` for all Python modules.
- `school-pptx.sh --help` exposes `example`, `template-report`, `render`, and `verify`.
- Example Markdown renders into non-empty PPTX.
- PPTX opens as a ZIP and contains expected slide XML count.
- Manifest `sections -> logical_slides -> physical_slides -> slots` is populated.
- Every physical slide maps to a known layout and every required slot is filled.
- Contents slide is generated from `##` headings, not hand-authored body text.
- Speaker notes XML exists when notes are present.
- Tables, images, galleries, timelines, and code produce editable PPTX objects where supported.
- Image placement preserves aspect ratio with contain behavior.
- Overflow creates continuation physical slides and records why.
- Public output root does not leak logs, debug JSON, temp files, status sidecars, or failure diagnostics.

Automated verification should be structural. Manual visual UAT remains required for accepting the first normalized template because PPTX rendering varies between PowerPoint, WPS, Keynote, and LibreOffice.

## Patterns to Follow

### Pattern 1: Hand Surface Before Script

**What:** First phase accepts `school-standard.pptx` and its manifest before renderer implementation.  
**When:** Template visual identity and slot geometry are not yet stable.  
**Why:** This follows `tiaokedan`: lock the target surface, then author Markdown, then automate.

### Pattern 2: Markdown Logical Deck as Source of Truth

**What:** Teacher edits `school-pptx.md`, not PPTX XML, Python config, or slot coordinates.  
**When:** Every normal workflow.  
**Why:** It preserves reviewability and matches the repository's Markdown-first document workflow.

### Pattern 3: Renderer-Owned Physical Pagination

**What:** Markdown declares logical slides; renderer produces physical slides using manifest budgets.  
**When:** Text, tables, timelines, galleries, or code exceed a layout budget.  
**Why:** This keeps authoring simple and matches the accepted `school-presentation` page hierarchy.

### Pattern 4: Whole-Folder Standalone Runtime

**What:** `school-pptx` must run from its own `SKILL.md`, `references/`, `templates/`, and `scripts/`, without sibling skill dependencies.  
**When:** Installation into Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, or Hermes Agent.  
**Why:** v1.14-v1.16 established that new skills must not hide runtime dependencies on sibling skill folders.

## Anti-Patterns to Avoid

### Anti-Pattern 1: Raw POTX Autodiscovery

**What:** Letting scripts infer arbitrary layouts from any user-supplied POTX.  
**Why bad:** Placeholder order, names, masters, and visual intent are not stable enough for deterministic rendering.  
**Instead:** Normalize one standard template and write an explicit manifest.

### Anti-Pattern 2: Markdown Coordinates and Styling

**What:** Allowing `x`, `y`, `w`, `h`, font size, color, crop, and animation controls in slide Markdown.  
**Why bad:** It breaks template consistency and moves design ownership to authors.  
**Instead:** Markdown selects approved layouts and supplies semantic content only.

### Anti-Pattern 3: Screenshot PPTX

**What:** Rendering each slide as a full-slide image.  
**Why bad:** It violates the editable PPTX goal and hides text, tables, notes, and media from verification.  
**Instead:** Use editable text boxes, tables, images, and shapes; reserve full-slide images only for an explicitly deferred layout.

### Anti-Pattern 4: False Animation Support

**What:** Claiming transitions or object animation because XML tokens exist.  
**Why bad:** Office compatibility is fragile and hard to verify across apps.  
**Instead:** v1.17 should support no animation by default; only add 0.5s smooth transition if a local fixture proves round-trip reliability.

## Scalability Considerations

| Concern | At 100 decks | At 10K decks | At 1M decks |
|---------|--------------|--------------|-------------|
| Template variants | One controlled `school-standard` template | Add versioned themes with separate manifests | Need registry and migration tooling, out of v1.17 scope |
| Rendering performance | Single-process Python is enough | Batch rendering needs cache for template inspection and media metadata | Queue/distributed rendering, out of repository skill scope |
| Verification | Local structural checks + manual UAT | Deterministic fixture suite across themes | Office-app compatibility lab, out of scope |
| Markdown contract | One template fixture | Contract versioning in frontmatter | Migration tooling required |

## Roadmap Phase Recommendation

1. **Phase A: Standard Template and Manifest**
   - Create `skills/school-pptx/` skeleton.
   - Hand-normalize supplied `.potx` into `templates/school-standard.pptx`.
   - Write `references/template-normalization.md` and `references/template-manifest.yaml`.
   - Add `template-report` validation and phase evidence.

2. **Phase B: Markdown Contract and Fixture**
   - Add `templates/school-pptx.md`.
   - Define frontmatter, `theme`, `::: slide {layout="..."}`, notes, review markers, allowed layouts, and anti-styling rules in `references/markdown-contract.md`.
   - Verify contents generation from `##` headings at parser/model level.

3. **Phase C: Renderer and Pagination**
   - Implement `render` from Markdown to editable PPTX.
   - Cover title-content, two-column, image-text, table, timeline, gallery, code, generated contents, section, cover, and closing.
   - Implement logical-to-physical split before PPTX writing.
   - Add hidden manifest and OOXML inspection evidence.

4. **Phase D: Skill Entry, Runtime Notes, and Regression Gate**
   - Finalize `SKILL.md`, README/index/docs references if required by phase scope.
   - Add `verify --workdir`.
   - Prove whole-folder standalone behavior and six-runtime adapter notes.
   - Run manual visual UAT against PowerPoint-compatible apps before milestone close.

Ordering rationale: template/manifest must precede Markdown finalization because layout names and slot budgets define what Markdown may express. Markdown must precede renderer implementation because parser and pagination need a stable semantic contract. Renderer must precede final skill docs because runtime notes and verification cannot be honest until local PPTX behavior is proven.

## Sources

- Local: `.planning/PROJECT.md` v1.17 scope and active requirements.
- Local: `AGENTS.md`, `docs/directory-spec.md`, `docs/compatibility-matrix.md` for canonical skill structure and runtime support.
- Local: `skills/tiaokedan/SKILL.md`, `skills/tiaokedan/references/markdown-contract.md`, `skills/tiaokedan/references/pdf-workflow.md` for hand-authored target -> Markdown -> script discipline and clean output boundary.
- Local: `skills/school-presentation/SKILL.md`, `skills/school-presentation/references/authoring-and-layout.md`, `skills/school-presentation/references/verification-contract.md` for logical/physical page hierarchy, fixed canvas, manifest verification, and deferred PPTX boundary.
- Official: python-pptx 1.0.0 documentation, feature overview and unsupported-feature warning: https://python-pptx.readthedocs.io/
- Official: python-pptx placeholders documentation, stable placeholder `idx` and insertion behavior: https://python-pptx.readthedocs.io/en/latest/user/placeholders-using.html
- Official: python-pptx notes slide documentation: https://python-pptx.readthedocs.io/en/latest/user/notes.html
