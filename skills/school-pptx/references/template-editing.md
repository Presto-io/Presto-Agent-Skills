# school-pptx Template Editing Rules

The normalized template is intentionally human-adjustable. You may open `skills/school-pptx/templates/standard-school.pptx` in PowerPoint or another compatible editor, refine the visual system, and then re-run validation.

## Renderer-Owned Slot Model

The controlled template uses `renderer-owned-native-shapes`. Slide masters and layouts intentionally contain no content placeholders. The renderer creates titles, body text, tables, media, timeline nodes, gallery cards, and code shapes from manifest-owned geometry on every generated slide.

## Allowed Edits

Allowed edits are exactly:

- add decorative template-owned shapes
- refine template-owned typography, colors, and polish
- delete content placeholders from masters and layouts
- adjust manifest geometry when the intended renderer-owned content region changes

These edits keep Markdown limited to semantic content while allowing the template to mature visually.

## Forbidden Edits

Forbidden edits are exactly:

- delete or rename a controlled slide-layout part
- duplicate slots without unique ids
- add content slots without manifest entries
- move manifest-owned content geometry outside the safe layout area or across the footer

If a new content slot is genuinely needed, update `standard-school.manifest.yaml` with a unique semantic slot id, geometry, text budget, `empty_slot`, and `continuation`, then validate the template again. Do not add a PowerPoint placeholder merely to carry renderer data.

## Post-Edit Validation

Run this command after every manual edit:

```bash
skills/school-pptx/scripts/school-pptx.sh template-report \
  --theme standard-school \
  --out-md build/school-pptx/.school-pptx/template-report.md \
  --out-json build/school-pptx/.school-pptx/template-report.json
```

The report must pass before later Markdown contracts or renderers depend on the edited template. Positive evidence belongs under explicit report paths or hidden `.school-pptx` workdirs. Later successful public PPTX output must not receive manifests, logs, debug files, or temporary evidence by default.
