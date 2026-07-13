# school-pptx Template Contract

Phase 41 defines the controlled template contract for `school-pptx`. Runtime behavior depends on `skills/school-pptx/templates/standard-school.pptx` and `skills/school-pptx/templates/standard-school.manifest.yaml`; the supplied `test/学院PPT模板.potx` is visual source evidence only.

## Controlled Theme

- Theme id: `standard-school`
- Available themes: `standard-school`
- Runtime template: `standard-school.pptx`
- Manifest: `standard-school.manifest.yaml`

Unknown theme validation must fail non-zero and print the available controlled theme id.

## Layouts

The manifest covers exactly these 11 layout ids:

1. `cover`
2. `contents`
3. `section`
4. `title-content`
5. `two-column`
6. `image-text`
7. `table`
8. `timeline`
9. `gallery`
10. `code`
11. `closing`

Each layout points to an inspectable PPTX slide-layout XML file and defines one or more semantic slots. Slot ids are stable public identifiers such as `title`, `subtitle`, `body`, `media`, `caption`, `left_body`, `right_body`, `table`, `timeline_items`, `gallery_items`, and `code`; raw localized PowerPoint placeholder names stay inside placeholder mapping metadata.

## Manifest Schema

Top-level fields:

- `theme_id`
- `available_themes`
- `template`
- `ownership`
- `required_layouts`
- `layouts`

Each layout includes:

- `label`
- `purpose`
- `pptx_layout`
- `required_slots`
- `slots`

Each slot includes:

- `id`
- `purpose`
- `kind`
- `placeholder`
- `geometry`
- `text_budget`
- `empty_slot`
- `continuation`

Geometry is stored in EMU units. `template-report` compares manifest geometry against PPTX XML with the manifest tolerance, currently `2000` EMU, so normal Office serialization noise does not fail validation.

## Template-Owned Guardrails

Markdown cannot override geometry, fonts, colors, decorative assets, footer behavior, or bounded text behavior. Markdown in later phases may provide semantic slide content only; it must not expose coordinates, font families, theme colors, decorative assets, footer placement, crop behavior, or arbitrary frame sizing.

Text slots use fixed frame geometry with bounded elastic text behavior. A renderer may shrink text only within the slot's `font_size_min` and `font_size_max` range and must obey the slot's `overflow` policy.

## Phase 41 Scope Fence

Phase 41 validates manifest completeness and structural consistency. It does not implement Markdown syntax, no Markdown-to-PPTX renderer, no logical-to-physical pagination, no speaker notes rendering, and no final runtime adapter documentation.

Manual template editing rules live in [template-editing.md](template-editing.md). After any manual PPTX edit, run:

```bash
skills/school-pptx/scripts/school-pptx.sh template-report \
  --theme standard-school \
  --out-md build/school-pptx/.school-pptx/template-report.md \
  --out-json build/school-pptx/.school-pptx/template-report.json
```
