# Domain Pitfalls: school-pptx

**Domain:** Markdown-first school-template PPTX generation skill  
**Project:** v1.17 school-pptx  
**Researched:** 2026-07-13  
**Overall confidence:** HIGH for python-pptx API boundaries verified from official docs/Context7; MEDIUM for runtime-specific OpenClaw/Hermes behavior because exact installed-runtime execution has not yet been validated.

## Executive Risk Position

`school-pptx` should be planned as a controlled-template renderer, not a general PPTX automation skill. The largest failure mode is accepting a human-composed `.potx`/PPTX visual sample as if it were already a machine-stable template. python-pptx can create and edit `.pptx` packages, fill placeholders, add tables/images/text, and write speaker notes, but it does not remove the need for a clean master/layout/placeholder contract. If template normalization is skipped, every later feature inherits dirty layout IDs, accidental direct formatting, inconsistent placeholder geometry, and unpredictable visual drift.

The first version should favor editable, template-consistent objects over fidelity tricks. Code highlighting, complex animation, arbitrary Markdown styling, freeform coordinates, and broad template marketplace support should be delayed. The renderer should make deterministic layout decisions from constrained Markdown blocks and template-owned slots, then verify the internal PPTX structure instead of only checking that a file exists.

Local environment note: `python3` currently does not have `pptx` installed in this workspace, so dependency installation and version pinning must be a Phase 41/43 gate. This research uses official python-pptx documentation and Context7 extracts rather than unverified local experiments.

## Risk Table

| Risk | Trigger Condition | Prevention Strategy | Phase to Handle |
|------|-------------------|---------------------|-----------------|
| Treating `.potx` as the runtime template input | The supplied school template arrives as `.potx` and scripts try to render directly from it | Normalize once into a skill-local standard `.pptx` template; document that `.potx` is visual source material, while renderer input is controlled `.pptx` | Phase 41: template normalization |
| Dirty slide masters/layouts from human-pasted pages | Template was assembled by copying pages, images, and text boxes rather than clean master layouts | Build a small named-layout catalog; delete unused layouts; assign stable placeholder names/types/idx; record expected placeholder map as fixture evidence | Phase 41 |
| Placeholder inheritance mismatch | Placeholders inherit position/formatting through master/layout/slide hierarchy; duplicate idx or direct overrides change effective geometry | Verify each supported layout has required placeholders by name/type/idx and expected EMU geometry before rendering | Phase 41, Phase 44 |
| Placeholder replacement surprises | `insert_table()` or picture placeholder insertion replaces the placeholder object with a graphic frame | Renderer must reacquire returned objects after insertion and avoid reusing stale placeholder handles | Phase 43 |
| Notes slide creation side effects | Accessing `slide.notes_slide` creates a notes slide that persists even if text is removed | Only create notes when Markdown has notes; verification must assert notes existence/content only on expected slides | Phase 43, Phase 44 |
| Notes placeholder missing or malformed | Notes master lacks a body placeholder or has been edited away | Template gate must verify notes master/body placeholder readiness; otherwise notes support is blocked rather than silently skipped | Phase 41 |
| Slide transitions/animations overpromised | Requirements mention smooth transition or object animation, but python-pptx has no stable public transition/animation authoring API in researched docs | First version allows no animation by default; 0.5s smooth transition only if preserved from normalized template and verified at package XML level | Requirements, Phase 41, Phase 44 |
| Autofit causes inconsistent typography | `fit_text()` changes all text in a frame to a computed font size based on available font metrics; runtime fonts differ | Use explicit per-layout content budgets and deterministic fallback font sizes; use fit only within bounded min/max rules with recorded font assumptions | Phase 42, Phase 43 |
| Text overflow hidden by PowerPoint behavior | A PPTX opens without errors but body text exceeds visible slot or shrinks below readable size | Renderer must paginate logical slides before writing when content exceeds budget; verification checks physical slide count, text presence, and min font size | Phase 42, Phase 44 |
| Markdown grammar too permissive | Authors use arbitrary Markdown features, raw HTML, inline styles, nested tables, or coordinates | Define strict YAML + `::: slide {layout="..."}` contract; reject unsupported syntax with actionable errors | Phase 42 |
| Theme/layout escape hatches break consistency | Markdown can specify colors, fonts, position, size, or arbitrary theme values | Allow `theme` only as controlled template identifier; coordinates/typography/colors are template-owned | Requirements, Phase 42 |
| Contents slide generated from wrong heading level | `#` title, `##` sections, logical slide titles, and physical continuation titles are mixed | Contract: `#` is document-title fallback only; every `##` becomes contents entry; continuations inherit section context but do not add duplicate contents items | Phase 42, Phase 43 |
| Logical-to-physical pagination breaks semantics | One logical slide expands to several physical PPTX slides and loses directory, title, notes, table headers, or continuation labels | Pagination model must track `logical_slide_id`, `physical_index`, `continuation_of`, title variant, notes placement, and repeated table headers | Phase 43 |
| Table continuation confusion | Long tables split across slides without repeated headers, column widths, or row grouping | Fixed table budgets per layout; repeat header rows; preserve column width map; add continuation labels owned by renderer | Phase 42, Phase 43 |
| Timeline/gallery overflow | Timelines or galleries exceed slot capacity and are squeezed into unreadable objects | Define item/image count budgets; paginate by item groups; image placement uses contain behavior and never crop by default | Phase 42, Phase 43 |
| Code block editability conflicts with highlighting | Syntax-highlighted code is easier as image/HTML rendering, but requirement says editable PPTX objects | First version uses editable monospace plain text, no syntax highlighting. Optional highlighting requires run-level text coloring and verification later | Phase 42, Phase 43 |
| Image shortcut undermines editability | Renderer screenshots whole slides or code blocks for fidelity | Requirement must ban whole-slide screenshot output; verification checks text/table/code are real PPTX editable objects, not image-only | Requirements, Phase 44 |
| File non-empty verification gives false success | A corrupted or visually wrong `.pptx` can still be non-zero bytes | Verify openability with python-pptx, slide count, layout IDs, placeholder fills, notes, media relationships, table dimensions, text extraction, and package XML invariants | Phase 44 |
| Package opens but template consistency regressed | Slide count and text pass, but layout mapping or theme assets drift | Verification must compare layout names, master/layout relationship IDs, expected media count, and absence of forbidden freeform coordinates from Markdown | Phase 44 |
| Dependency not installed or wrong version | Workspace/runtime lacks `python-pptx`, or version lacks needed notes/autofit behavior | Pin a supported version in docs/installer notes; `--help` and verification gates check import/version before claiming support | Phase 43, Phase 44 |
| OpenClaw/Hermes script execution assumptions | Runtime cannot discover scripts, cannot write target path, or does not preserve support files | Skill adapter notes must require whole-folder installation, explicit script allowlist, support-file discovery check, and sandbox write check | Phase 44 |
| Hidden diagnostics leak into teacher output | Renderer writes manifests/logs/status files beside public `.pptx` | Follow existing clean-output pattern: successful public output contains only requested `.md`/`.pptx` or named deliverables; manifests/evidence stay hidden or phase-local | Phase 43, Phase 44 |
| Sibling-skill dependency creep | New renderer imports `school-presentation` internals or old scripts for convenience | `school-pptx` must be skill-local. Existing school-presentation can inform design but must not be runtime dependency | Requirements, Phase 43 |
| Trying to support arbitrary PPT templates | Users provide random marketplace/company templates with unknown layouts | v1 supports only normalized controlled school templates; arbitrary template import is explicitly deferred | Requirements |

## Risks That Must Become Requirements

| Requirement Gate | Why It Must Be Required |
|------------------|-------------------------|
| The renderer consumes a normalized skill-local `.pptx` template, not raw `.potx` | Prevents template-source ambiguity and keeps python-pptx input within its documented `.pptx` workflow. |
| The normalized template has a committed layout/placeholder map | Without stable names/types/idx/geometry, Markdown-to-slot mapping cannot be verified. |
| Markdown uses a constrained YAML + slide-block contract | Prevents author-controlled layout/styling from breaking template consistency. |
| `theme` is a controlled identifier, not a style object | Keeps visual authority in the template and avoids template drift. |
| Logical slides may expand into multiple physical slides | Required for readable PPTX output when text/tables/timelines/galleries exceed slot budgets. |
| Editable PPTX objects are required for text, tables, notes, images, timelines, galleries, and basic code | Prevents screenshot-based shortcuts that defeat the skill goal. |
| Complex animation and object-level transitions are out of scope | Avoids building on unsupported or brittle python-pptx internals. |
| `school-pptx` is standalone and skill-local | Matches repository pattern from `tiaokedan` and `teaching-design-package`; avoids sibling runtime dependency. |
| OpenClaw and Hermes Agent adapter notes are mandatory | Repository compatibility matrix treats both as first-class required runtimes. |

## Risks That Must Become Verification Gates

| Verification Gate | Must Check |
|-------------------|------------|
| Dependency gate | `python3` can import `pptx`; version is recorded; script `--help` works in the target runtime. |
| Template gate | Normalized `.pptx` opens; required masters/layouts/placeholders exist; expected placeholder names/types/idx/EMU geometry match fixture evidence. |
| Markdown parser gate | Unsupported Markdown, raw HTML, freeform styles, unknown layouts, unknown theme IDs, and unresolved review markers fail non-zero. |
| Render gate | Generated PPTX opens with python-pptx; slide count equals expected physical pages; logical-to-physical mapping is recorded in hidden manifest/evidence. |
| Contents gate | Contents slide is generated from `##` headings only; `#` is not duplicated into contents except as fallback title behavior. |
| Notes gate | Slides with notes have expected notes text; slides without notes do not get accidental notes slides. |
| Object editability gate | Text/code are text shapes, tables are table objects, images are picture relationships, not whole-slide screenshots. |
| Pagination gate | Long text/table/timeline/gallery fixtures split predictably, repeat titles/table headers where required, and preserve notes/section context. |
| Code gate | Basic code fixture remains editable plain text; no claimed syntax highlighting unless run-level coloring is explicitly implemented and verified. |
| Clean output gate | Successful public output excludes logs, manifests, status sidecars, temp files, and debug JSON. |
| Runtime adapter gate | Codex/Claude/Gemini/OpenCode/OpenClaw/Hermes notes mention support-file discovery, script execution, write boundaries, and install-time checks. |
| Negative gate | Invalid template, invalid Markdown, missing media, missing required placeholders, unresolved markers, and unwritable output path fail honestly. |

## Requirements to Downgrade or Defer for v1

| Requirement | Recommendation | Reason |
|-------------|----------------|--------|
| Direct `.potx` rendering | Downgrade to one-time human/maintainer normalization into `.pptx` | Reduces library-format ambiguity and makes template fixture auditable. |
| Complex object animation | Defer | Not supported by stable python-pptx public docs; high brittleness for low first-version value. |
| Generated smooth transitions | Downgrade to "preserve normalized-template transition only if verifiable" or defer | Avoids custom XML mutation before the core renderer is stable. |
| Syntax-highlighted code | Downgrade to editable plain monospace code | Highlighting conflicts with editability and increases run-level formatting complexity. |
| Arbitrary Markdown styling | Defer/ban | Template consistency depends on renderer-owned slots and typography. |
| Arbitrary template marketplace support | Defer | Human-pasted templates require normalization; unknown templates cannot be made reliable in v1. |
| Automatic perfect autofit | Downgrade to budgeted pagination plus bounded font-size fallback | Font metrics and Office rendering vary by runtime and installed fonts. |
| Rich chart/SmartArt parity | Defer unless a controlled editable primitive is specified | Table/text/image/timeline/gallery/code are enough for the first school PPTX slice. |
| Whole-slide visual fidelity by screenshot | Ban | Violates editable-object requirement. |

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Phase 41: Template normalization | Treating visual sample as implementation-ready | Create standard `.pptx`, fixture map, and template validation command before renderer work. |
| Phase 42: Markdown contract | Letting Markdown express layout details | Keep contract semantic: layout IDs, content blocks, notes, media references, controlled theme only. |
| Phase 43: Renderer | Implementing too much fidelity at once | Start with fixed layouts and editable primitives; pagination and object identity matter more than animation. |
| Phase 44: Skill packaging and verification | Claiming success because `.pptx` exists | Require structural PPTX checks, negative tests, clean-output checks, and runtime adapter checks. |

## Source Notes

| Source | Confidence | Findings Used |
|--------|------------|---------------|
| python-pptx official ReadTheDocs, quickstart/API/user docs: https://python-pptx.readthedocs.io/ | HIGH | Library creates/updates `.pptx`; supports slides, text, pictures, tables, placeholders, and notes. |
| python-pptx notes docs: https://python-pptx.readthedocs.io/en/latest/user/notes.html | HIGH | Accessing `slide.notes_slide` creates a notes slide; each slide has at most one; notes placeholder can be missing. |
| python-pptx placeholder docs: https://python-pptx.readthedocs.io/en/latest/user/placeholders-understanding.html and https://python-pptx.readthedocs.io/en/latest/api/placeholders.html | HIGH | Placeholder behavior depends on master/layout/slide inheritance; table insertion uses placeholder geometry and replaces placeholder with returned object. |
| python-pptx text docs: https://python-pptx.readthedocs.io/en/latest/api/text.html | HIGH | `fit_text()` applies word wrap and computed font sizing within bounds; depends on font-family/font-file assumptions. |
| Context7 `/websites/python-pptx_readthedocs_io_en` and `/scanny/python-pptx` docs extracts | HIGH | Cross-checked notes, placeholders, tables, and autofit behavior from official docs/source snippets. |
| Local workspace import check, `python3 -c 'import pptx'` | HIGH | `python-pptx` is not currently installed in this workspace, so dependency gate is required before implementation verification. |
| `.planning/PROJECT.md`, `AGENTS.md`, `docs/compatibility-matrix.md`, `skills/school-presentation/SKILL.md`, `skills/tiaokedan/SKILL.md` | HIGH | Established repository constraints: Simplified Chinese, canonical `SKILL.md`, skill-local scripts, Markdown-first source, clean outputs, OpenClaw/Hermes support. |

## Open Questions for Phase Planning

- Which exact normalized template file should be committed as the machine-mappable source: `.pptx` only, or `.pptx` plus an extracted placeholder-map JSON fixture?
- Should transition preservation be attempted in Phase 41 by inspecting the normalized template XML, or deferred entirely until the core PPTX renderer is accepted?
- What minimum font family and fallback policy should be used for Chinese school PPTX rendering across macOS/Linux/OpenClaw/Hermes environments?
- Should verification use only python-pptx plus zip/XML inspection, or also include optional LibreOffice/PowerPoint manual UAT evidence when available?
