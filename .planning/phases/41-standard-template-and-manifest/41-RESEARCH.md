# Phase 41: Standard Template and Manifest - Research

**Researched:** 2026-07-13
**Status:** Ready for planning

## Research Question

What do we need to know to plan Phase 41 well?

Phase 41 should establish the controlled `school-pptx` template contract before later Markdown parsing or PPTX rendering code depends on it. The plan needs to produce a normalized skill-local `.pptx`, a reviewable machine-readable YAML manifest, and a repeatable `template-report` command that validates the contract.

## Key Findings

### 1. Template normalization should be treated as a contract build, not a renderer build

The phase should create the runtime substrate for later work:

- `skills/school-pptx/templates/<theme>.pptx` as the normalized runtime template.
- `skills/school-pptx/templates/<theme>.manifest.yaml` as the authoritative slot contract.
- A small script command under `skills/school-pptx/scripts/` that validates the template/manifest pair and writes report evidence.

The original `.potx` is visual source evidence only. It should not become the runtime input or a required durable artifact in the skill folder.

Planning implication: split tasks so the template asset, manifest, validator, and evidence are distinct but mutually checked. Do not make Phase 41 implement Markdown parsing or full PPTX rendering.

### 2. `python-pptx` is the most practical local tool for Phase 41 inspection

For Phase 41, the required operations are template creation/inspection and structural validation. A Python script can:

- open a `.pptx`;
- inspect slides, shapes, placeholder metadata, names, alt text where available, and geometry;
- compare observed shape anchors against a YAML manifest;
- fail non-zero for missing/duplicate/malformed manifest entries;
- emit Markdown and JSON evidence.

`python-pptx` has limitations around true PowerPoint master/layout editing, speaker notes, and some advanced XML details. Those are mostly Phase 43 concerns. Phase 41 can avoid claiming a perfect PowerPoint master model by representing the 11 layouts as inspectable template slides or another explicit mapping mechanism, as allowed by the phase context.

Planning implication: the validator should use stable mapping anchors that are inspectable from generated `.pptx` files. If placeholder layout internals are unstable, use explicit shape naming/alt-text style anchors plus manifest geometry instead of relying only on localized placeholder names.

### 3. A template-slide mapping is likely lower risk than editing PowerPoint masters in code

Creating or modifying PowerPoint slide masters/layouts programmatically is fragile. A lower-risk Phase 41 strategy is:

- generate a normalized `.pptx` with one inspectable template slide per supported logical layout;
- place mapped text/media/table/code/gallery/timeline slots as shapes with stable semantic anchors;
- keep decorative assets template-owned and excluded from controllable slots;
- record each layout and slot in the manifest.

Later renderer code can copy or recreate from these template slides, but Phase 41 only needs the normalized template contract and validation report.

Planning implication: include an acceptance criterion that the normalized PPTX contains exactly the 11 required layout ids through the chosen mapping mechanism, not necessarily that they are native PowerPoint custom layouts.

### 4. The manifest must be full-fidelity enough for downstream rendering

The manifest should not be a lightweight index. Each layout should include:

- stable layout id;
- human label/purpose;
- template mapping reference;
- slots keyed by semantic id;
- slot purpose and allowed content kind;
- PPTX mapping metadata;
- normalized geometry;
- text budget;
- empty-slot behavior;
- continuation behavior;
- footer/decorative ownership notes.

For text slots, the minimum budget fields are:

- `max_chars`;
- `max_lines`;
- `font_size_min`;
- `font_size_max`;
- `overflow` with controlled values such as `shrink`, `paginate`, or `fail`.

Planning implication: include a manifest schema task before the command task, and make `template-report` reject missing or malformed budget fields.

### 5. Theme validation must be explicit and user-facing

Requirement TPL-04 and the UI-SPEC require a controlled default theme id and a clear unknown-theme error:

`未知主题 "{theme}"。可用主题：{available_theme_ids}。`

Planning implication: include a negative validation task for unknown theme and require the report command to print or return available theme ids.

### 6. Manual template editing is expected, so the plan needs guardrails

The user explicitly wants to be able to manually drag and resize the generated PPTX framework. The plan must make room for manual calibration without making the template unverifiable.

Allowed manual edits:

- move/resize mapped placeholders;
- add decorative template-owned shapes;
- refine template-owned typography, colors, and polish.

Forbidden edits:

- delete mapped placeholders;
- replace mapped placeholders with ordinary unmapped shapes;
- remove mapping anchors;
- duplicate mapped slots without unique ids;
- add content slots without manifest entries.

Planning implication: add a reference doc or manifest comments for manual editing rules, and make `template-report` detect missing slots, duplicates, lost mappings, and geometry drift.

### 7. Phase 41 validation should prove structure, not final visual pagination quality

Phase 41 can prove that slots and budgets exist and are internally consistent. It cannot prove final long-text pagination, gallery splitting, table continuation, or notes rendering because those belong to Phase 43.

The validation report should honestly mark budget calibration as a starting point. It should not claim final visual acceptance for all generated deck content.

Planning implication: acceptance criteria should state that `template-report` validates manifest completeness and template consistency, while full render/pagination quality remains downstream.

### 8. Existing repo patterns favor concise entries, hidden evidence, and script-local behavior

Relevant precedent:

- `school-presentation` keeps fixed-canvas and layout rules in `references/`, with repeatable verification commands and explicit manual visual UAT boundary.
- `tiaokedan` keeps the canonical skill entry concise, places deeper behavior in references/scripts/templates, and hides diagnostics from clean public output.
- The repository requires OpenClaw and Hermes Agent to be considered for new skills, but final runtime adapter docs are Phase 44.

Planning implication: Phase 41 may create early `skills/school-pptx/` folders and reference docs, but should not bloat `SKILL.md` or attempt final six-runtime documentation.

## Recommended File Targets

Likely Phase 41 write scope:

- `skills/school-pptx/templates/standard-school.pptx`
- `skills/school-pptx/templates/standard-school.manifest.yaml`
- `skills/school-pptx/scripts/school-pptx.sh`
- `skills/school-pptx/scripts/template_report.py`
- `skills/school-pptx/references/template-contract.md`
- `skills/school-pptx/references/template-editing.md`
- optional minimal `skills/school-pptx/SKILL.md` placeholder only if needed to establish the folder, with final entry work deferred to Phase 44

Avoid in Phase 41:

- Markdown fixture and Markdown parser;
- full Markdown-to-PPTX renderer;
- logical-to-physical pagination implementation;
- speaker notes rendering;
- final runtime adapter notes and repository discoverability updates unless needed for local command discovery.

## Validation Architecture

`template-report` should support at least:

```text
skills/school-pptx/scripts/school-pptx.sh template-report \
  --theme standard-school \
  --out-md <path> \
  --out-json <path>
```

Validation should fail non-zero for:

- unknown theme;
- missing required layout;
- extra or misspelled layout when the manifest claims the v1.17 controlled set;
- missing slot;
- duplicate slot id within a layout;
- lost placeholder or shape mapping;
- manifest/PPTX geometry mismatch outside an explicit tolerance;
- missing or malformed text budget fields;
- unsupported `overflow`, `empty_slot`, or `continuation` values.

Markdown evidence should include:

- summary status;
- selected theme and available themes;
- 11-layout coverage table;
- slot mapping tables;
- text budget validation;
- manual edit guardrails;
- JSON evidence path.

JSON evidence should include:

- `theme_id`;
- `template_path`;
- `manifest_path`;
- `layouts`;
- `slots`;
- `failures`;
- `warnings`;
- `generated_at`.

## Risks and Planning Notes

### Real `.potx` source may be missing

STATE.md records that Phase 41 needs the real supplied `.potx` visual sample or accepted local evidence before template normalization can be completed. If the sample is not present during execution, the plan should require either:

- locating the supplied sample in the workspace; or
- generating a clearly marked provisional normalized PPTX framework and recording that visual-source parity is not yet accepted.

This should be a blocker for final Phase 41 verification if the user expects derivation from the real sample.

### Native PowerPoint layout semantics may not be reliable

If native slide layout/master editing is unstable, the accepted mapping mechanism can be template slides plus manifest anchors. The plan should phrase success around inspectable, explicit mapping rather than requiring unsupported master editing.

### Geometry drift needs tolerance and clear repair path

PPTX geometry units can be EMU, inches, or points. The manifest should store normalized units, and the validator should define conversion/tolerance rules so manual editing does not fail due to rounding noise.

### Public output boundary must stay clean

Reports and JSON evidence are verification outputs. Later successful public renders must not leak manifests/logs/debug files, but Phase 41 may intentionally produce reports in a verification workdir as evidence.

## Suggested Plan Shape

1. Establish `school-pptx` template folder and minimal command surface.
2. Create or normalize the default school PPTX template with 11 inspectable layout mappings and stable slot anchors.
3. Author the YAML manifest with theme, layouts, slots, geometry, text budgets, and ownership rules.
4. Implement `template-report` validation and evidence emission.
5. Add manual editing/reference guidance and negative cases.
6. Run and record verification evidence for the default theme plus failure cases.

## Research Complete

This research is sufficient to plan Phase 41. The key planning constraint is to keep Phase 41 focused on a verifiable template contract while explicitly deferring Markdown contract, renderer, pagination, and final adapter documentation to later phases.

## RESEARCH COMPLETE
