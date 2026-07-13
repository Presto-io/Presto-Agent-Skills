# school-pptx Template Editing Rules

The normalized template is intentionally human-adjustable. You may open `skills/school-pptx/templates/standard-school.pptx` in PowerPoint or another compatible editor, refine the visual system, and then re-run validation.

## Allowed Edits

Allowed edits are exactly:

- drag and resize mapped placeholders
- add decorative template-owned shapes
- refine template-owned typography, colors, and polish

These edits keep Markdown limited to semantic content while allowing the template to mature visually.

## Forbidden Edits

Forbidden edits are exactly:

- delete mapped placeholders
- replace mapped placeholders with ordinary shapes
- remove mapping anchors
- duplicate slots without unique ids
- add content slots without manifest entries

If a new content slot is genuinely needed, update `standard-school.manifest.yaml` with a unique semantic slot id, placeholder mapping, geometry, text budget, `empty_slot`, and `continuation`, then validate the template again.

## Post-Edit Validation

Run this command after every manual edit:

```bash
skills/school-pptx/scripts/school-pptx.sh template-report \
  --theme standard-school \
  --out-md build/school-pptx/.school-pptx/template-report.md \
  --out-json build/school-pptx/.school-pptx/template-report.json
```

The report must pass before later Markdown contracts or renderers depend on the edited template. Positive evidence belongs under explicit report paths or hidden `.school-pptx` workdirs. Later successful public PPTX output must not receive manifests, logs, debug files, or temporary evidence by default.
