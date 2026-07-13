# Phase 42: Markdown Contract and Full Fixture - Pattern Map

**Mapped:** 2026-07-13
**Scope:** `school-pptx` Markdown contract、逻辑解析/验证、full fixture、配套媒体与 `example` 命令
**Primary analogs:** Phase 41 `school-pptx` 产物、`tiaokedan` Markdown 契约、`school-presentation` authoring/full-fixture/parser/CLI

## File Classification

| Expected File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `skills/school-pptx/references/markdown-contract.md` | canonical reference | human authoring -> parser contract | `skills/tiaokedan/references/markdown-contract.md` + `skills/school-pptx/references/template-contract.md` | role-match |
| `skills/school-pptx/scripts/markdown_contract.py` | parser/validator/fixture copier | Markdown + manifest -> logical JSON + diagnostics / copied example | `skills/school-presentation/scripts/school_presentation/_engine.py` + `skills/school-pptx/scripts/template_report.py` | composite |
| `skills/school-pptx/scripts/school-pptx.sh` | skill-local CLI dispatcher | argv -> Python command | existing file + `skills/school-presentation/scripts/school-presentation.sh` | exact |
| `skills/school-pptx/fixtures/school-pptx-full.md` | canonical full fixture | reviewed source -> validator -> Phase 43 logical model | `skills/school-presentation/templates/school-presentation-full.md` | role-match |
| `skills/school-pptx/fixtures/media/*` | self-contained companion media | relative image references -> resolved media metadata | `skills/school-presentation/references/identity/images/*` | role-match |
| `skills/school-pptx/templates/standard-school.manifest.yaml` | read-only source of truth | layouts/themes/budgets -> validation and overflow evidence | Phase 41 manifest | exact dependency; no Phase 42 edit expected |

## Data Flow Map

```text
school-pptx.sh validate --input deck.md [--out-json model.json]
  -> markdown_contract.py
     -> read standard-school.manifest.yaml
     -> parse YAML + slide/notes containers + top-level blocks
     -> resolve media from deck.md parent
     -> validate layout-specific semantics and forbidden controls
     -> aggregate source-located diagnostics
     -> optionally write deterministic logical-document JSON
     -> exit 0 only when errors == []

school-pptx.sh example --out-dir DIR
  -> markdown_contract.py
     -> copy fixed fixture Markdown and fixed media set only
     -> validate DIR/school-pptx-full.md through the same parser
     -> print fixed coverage/overwrite summary
     -> preserve every unrelated file under DIR
```

Phase 43 should consume the Phase 42 logical model rather than reparsing Markdown. The hand-off unit is one logical document containing metadata, ordered logical slides, typed blocks, notes, media metadata, source locations, one implicit closing entry, and aggregated diagnostics.

## Pattern Assignments

### `references/markdown-contract.md` — semantic contract, not runtime-private syntax

**Closest analog:** `skills/tiaokedan/references/markdown-contract.md` establishes the useful structure: contract shape, frontmatter field table, body grammar, required/optional facts, renderer-owned defaults, and non-goals. `skills/school-pptx/references/template-contract.md` supplies the ownership fence and exact 11-layout vocabulary.

**Reuse these patterns:**

- Start with the accepted source shape and a complete copyable example, then define fields and blocks in review order.
- Put author-owned semantics in the contract; keep geometry, fonts, colors, crop, footer, decorative assets, and bounded text behavior template-owned.
- Use tables for strict field/layout matrices and explicit allow/deny lists for errors.
- Link the runtime manifest as the machine source of truth instead of duplicating geometry or slot budgets.
- End with scope fences: Phase 42 defines logical semantics and validation; Phase 43 owns PPTX objects and physical pagination; Phase 44 owns runtime adapters and final UAT.

**Contract sections to mirror:**

1. Source shape and generated canonical example.
2. Strict frontmatter whitelist in generated order.
3. Slide/notes container grammar and exactly-one-`##` rules.
4. Top-level block model, including `###` binding and empty `###` boundary.
5. Layout-by-layout semantic matrix for ten authorable layouts plus implicit `closing`.
6. Inline `**bold**` and `==highlight==` semantics.
7. Media resolution/caption/contain rules and missing-media truthfulness.
8. Diagnostics, forbidden controls, example overwrite boundary, and Phase 43 hand-off model.

**Do not reuse:**

- Do not copy `school-presentation`'s `## Section:` / `### Slide:` headings, HTML comment metadata, `layout: auto`, reveal/mask/animation directives, semantic icon attributes, or authored `closing`; these are a different public grammar.
- Do not copy `tiaokedan`'s tolerated `<br>` exception. Phase 42 requires unsupported raw HTML to fail outside fenced code.
- Do not expose raw manifest placeholder names, geometry, text sizes, or continuation tuning as Markdown controls.

### `scripts/markdown_contract.py` — line-aware state machine and shared command core

**Closest analogs:**

- `school-presentation/_engine.py:75-91` for extracting frontmatter without converting the whole document to HTML.
- `school-presentation/_engine.py:279-384` for the sequential block scanner that distinguishes fenced code, tables, lists, media, headings, and paragraphs.
- `tiaokedan_renderer.py:58-101` for preserving frontmatter line numbers and rejecting malformed input at the contract boundary.
- `template_report.py:41-50`, `102-205`, and `279-305` for skill-local YAML loading, accumulated failures/warnings, deterministic evidence objects, explicit output paths, and non-zero failure.

**Recommended internal shape:**

```python
@dataclass
class SourceLocation:
    line: int
    column: int = 1

@dataclass
class Diagnostic:
    code: str
    message: str
    location: SourceLocation
    slide: str | None
    layout: str | None
    fix: str

def load_manifest(skill_dir: Path) -> dict[str, object]: ...
def parse_document(input_path: Path, manifest: dict[str, object]) -> dict[str, object]: ...
def validate_document(document: dict[str, object], manifest: dict[str, object]) -> list[Diagnostic]: ...
def validate_command(args: argparse.Namespace) -> int: ...
def example_command(args: argparse.Namespace) -> int: ...
```

The exact class split is discretionary, but parsing and validation must be reusable functions rather than logic embedded only in CLI branches.

**State-machine pattern:**

- Iterate over `text.splitlines()` with 1-based source line tracking.
- Maintain explicit state for frontmatter, slide container, nested notes container, fenced code, pending `###`, and current top-level block.
- Treat fenced code as opaque until its matching fence; raw HTML/style words inside it are data, not author controls.
- Emit a complete list/table/fence/image/paragraph as one block. Attach a pending `###` only when the next complete block closes.
- Preserve raw payload plus parsed structure where Phase 43 benefits: list items, table headers/rows, code language/text, image original path/resolved path/caption, inline emphasis spans, notes Markdown.
- Continue after locatable structural errors whenever container recovery is unambiguous; sort diagnostics by `(line, column, code)` before printing or serializing.

**Manifest reading pattern:**

Use the existing Phase 41 approach, resolved from the skill directory rather than the current working directory:

```python
manifest_path = skill_dir / "templates" / "standard-school.manifest.yaml"
data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
available_themes = data.get("available_themes") or []
layouts = data.get("layouts") or {}
```

Derive authorable layouts from manifest entries whose `markdown_controllable` is not `false` and which are not fixed template pages. Validate the requested theme against `available_themes`. Read slot `kind`, `text_budget`, and `continuation` when producing overflow evidence; do not repeat layout lists or budget constants as a second source of truth. It is acceptable to keep contract-specific field names and diagnostic codes as module constants because those are not manifest-owned.

**Logical model pattern:**

```json
{
  "metadata": {},
  "document_title": "...",
  "contents_entries": ["..."],
  "logical_slides": [
    {
      "layout": "title-content",
      "title": "...",
      "source_line": 12,
      "blocks": [],
      "notes": null,
      "overflow_evidence": []
    }
  ],
  "implicit_slides": [{"layout": "closing", "position": "end_of_deck"}],
  "coverage": {"explicit_layouts": [], "implicit_layouts": ["closing"]},
  "errors": [],
  "warnings": []
}
```

Use stable, semantic keys similar to the Phase 41 report evidence and `school-presentation` manifest (`logical_slides`, `layouts_used`, `media_warnings`). Do not add `generated_at`, absolute fixture paths, random ids, or other nondeterministic values to the public example or deterministic JSON evidence.

**Media path pattern:**

The required rule is simpler than `school-presentation/_engine.py:52-72`: an absolute path resolves as itself; a relative path resolves from `input_path.parent`. Preserve both the authored path and normalized resolved path. Validate existence as a file and report the original authored path. Do not fall back to sibling skills, repository `test/`, the current working directory, or network fetching.

**Diagnostic/exit pattern:**

- Follow UI-SPEC's stable shape: `path:line:column [CODE] message`, then slide/layout/fix detail.
- Print all errors before warnings and order each group by source position.
- `validate` returns `0` only if no errors exist; missing media is an error even if the logical model carries placeholder metadata.
- `--out-json` may be written for diagnostics even on validation failure, but the exit code must remain non-zero and `errors` must remain populated.
- Unexpected internal failures should be summarized without a default stack trace.

**Do not reuse:**

- Do not use `school-presentation`'s regex-only hierarchy extraction or `extract_admonitions()` removal; it loses nested-container position and cannot enforce notes-last.
- Do not use `school-presentation`'s silent unknown metadata/layout fallback or `tiaokedan`'s fail-fast `ContractError` as-is; Phase 42 requires aggregate locatable diagnostics.
- Do not transform Markdown to HTML before validation; that loses exact source boundaries and invites raw-HTML ambiguity.
- Do not introduce Pandoc/Node Markdown dependencies; PyYAML is already established by Phase 41.
- Do not put Phase 43 physical pagination into this module. Record ordered blocks and overflow evidence only.

### `scripts/school-pptx.sh` — extend the existing dispatcher

**Exact analog:** current `school-pptx.sh` already establishes `set -euo pipefail`, `SCRIPT_DIR`, `SKILL_DIR`, literal heredoc usage, environment-selectable Python, command shifting, and unknown-command failure. `school-presentation.sh:29-41` shows grouping several Python-backed commands behind one helper.

**Apply:**

```bash
markdown_contract() {
  "${SCHOOL_PPTX_PYTHON:-python3}" "$SCRIPT_DIR/markdown_contract.py" "$SKILL_DIR" "$@"
}

case "$command" in
  validate|example)
    markdown_contract "$command" "$@"
    ;;
  template-report)
    "${SCHOOL_PPTX_PYTHON:-python3}" "$SCRIPT_DIR/template_report.py" "$SKILL_DIR" "$@"
    ;;
  ...
esac
```

Update the literal usage text with exactly:

```text
school-pptx.sh validate --input <deck.md> [--out-json <logical-document.json>]
school-pptx.sh example --out-dir <dir>
```

Preserve `template-report` and `info` behavior. Do not fork parsing or example-copy logic into Bash; the wrapper should only dispatch and report unknown commands.

### `fixtures/school-pptx-full.md` — realistic narrative and machine-checkable coverage

**Closest analog:** `school-presentation-full.md` demonstrates a coherent intelligent-manufacturing story, ordinary Markdown content, tables, code, notes, multiple media shapes, and long review cases. Its main reusable property is narrative completeness, not its syntax.

**Required fixture order/pattern:**

- Strict YAML frontmatter in the UI-SPEC field order, with `theme: "standard-school"`.
- Explicit empty `cover` and `contents` blocks.
- A realistic sequence of section/content slides covering every authorable layout at least once.
- No explicit `closing`; the logical model supplies the eleventh layout implicitly.
- Contents derived from valid ordinary-slide `##` titles in source order, excluding cover/contents and document `#` fallback semantics as defined by the contract.
- Notes at the end of selected owning slides; at least one slide that will later expand shares notes in the logical model.
- Normal relative media syntax only, including captioned and empty-alt images.
- Long text/list, long table, timeline rows beyond the slot budget/capacity, more than four gallery images, code beyond 22 lines or manifest budget, multiple `image-text` images, and odd-count `two-column` blocks.
- Both visible `###` binding and empty `###` forced boundary.
- Natural use of `**bold**` and `==highlight==` without test-matrix prose.

**Layout semantics to assert during fixture validation:**

| Layout | Fixture/parser expectation |
|---|---|
| `cover` | empty authored block; metadata provides content |
| `contents` | empty authored block; entries are derived |
| `section` | exactly one `##`, no body blocks |
| `title-content` | one `##`, ordered blocks, overflow evidence |
| `two-column` | ordered block pairing; fixture includes final unpaired block |
| `image-text` | one stable body block followed by multiple image blocks |
| `table` | one table; optional attached `###` becomes table title |
| `timeline` | one table with exact `时间 | 标题 | 说明` headers |
| `gallery` | consecutive image blocks; more than four proves pagination input |
| `code` | one fenced code block; HTML/CSS-like code text proves fence-safe scanning |
| `closing` | absent from source; exactly one implicit logical entry |

**Do not reuse:**

- Do not store this fixture under `templates/`; Phase 42 explicitly owns `fixtures/`.
- Do not visibly label slides as layout tests or include unresolved missing media in the positive fixture.
- Do not reference `school-presentation` media, repository test artifacts, user desktop paths, or remote URLs.
- Do not include timestamps, random ids, explicit `id`, raw coordinates/styles, fonts/colors, HTML, or explicit closing syntax.

### `fixtures/media/*` — deterministic, skill-local companion assets

**Closest analog:** `school-presentation/references/identity/images/*` demonstrates committed runtime-local assets, but Phase 42 fixture media should be owned by `school-pptx/fixtures/media/` and directly referenced by the fixture.

**Apply:**

- Prefer a small documented fixed set of simple SVG/PNG assets representing equipment, curriculum modules, workflow, workshop, or icons. SVG is well suited to text-authored deterministic fixtures if Phase 43's media pipeline accepts it; otherwise commit small PNGs and compare bytes.
- Use stable ASCII or concise Chinese filenames consistently in fixture, copier, and validation expectations.
- Keep provenance/source clarity in the contract or a compact fixture note; do not add machine-specific source paths.
- Include enough distinct files to exercise multiple `image-text` pages and a gallery over four items. Reusing one asset is allowed only when the narrative meaning remains credible; a fixture should not depend on a single decorative image for all media cases.
- The positive fixture must contain every referenced file. Missing-media behavior belongs in temporary negative validation cases, not committed canonical source.

**Example-copy ownership:** define one fixed manifest in code, for example the Markdown filename plus exact relative media filenames. Copy/write only these paths. If a required destination path is an existing directory, fail without deleting it. Never call `rmtree(out_dir)`, glob-delete, or replace unrelated files.

## Verification Patterns

No dedicated Phase 42 test framework exists in `school-pptx`; use command-level checks and temporary negative fixtures, matching Phase 41's verification style.

### Positive contract and logical model

```bash
skills/school-pptx/scripts/school-pptx.sh validate \
  --input skills/school-pptx/fixtures/school-pptx-full.md \
  --out-json /tmp/school-pptx-phase42/logical-document.json
```

Assert with a short inline reader or `jq` when available:

- exit status `0`, `errors == []`;
- controlled theme `standard-school`;
- all ten explicit authorable layouts occur and one implicit `closing` occurs;
- contents order matches eligible `##` source order;
- notes are absent from visible blocks and retained with source lines;
- media authored/resolved paths and captions are present;
- overflow evidence exists for long text, table, timeline, gallery, code, image-text, and odd two-column cases.

### Aggregate negative validation

Create temporary Markdown under `/tmp`, not committed fixture/test directories, combining unknown YAML, missing/unknown/explicit-closing layouts, unknown slide attributes, invalid heading count, misplaced notes, raw HTML, style/coordinate/font/color controls, malformed timeline headers, and missing media. Verify:

- exit status is non-zero;
- all independently locatable errors appear, in source order;
- each line uses 1-based line/column plus code, slide, layout, and fix;
- fenced code containing `<div style="color:red">` does not trigger raw HTML/style errors;
- `--out-json` still truthfully contains errors when requested.

### Example determinism and overwrite safety

```bash
rm -rf /tmp/school-pptx-phase42-example
mkdir -p /tmp/school-pptx-phase42-example
printf 'keep\n' > /tmp/school-pptx-phase42-example/unrelated.txt
skills/school-pptx/scripts/school-pptx.sh example --out-dir /tmp/school-pptx-phase42-example
find /tmp/school-pptx-phase42-example -type f -exec shasum -a 256 {} \; | sort > /tmp/example-first.sha
skills/school-pptx/scripts/school-pptx.sh example --out-dir /tmp/school-pptx-phase42-example
find /tmp/school-pptx-phase42-example -type f -exec shasum -a 256 {} \; | sort > /tmp/example-second.sha
cmp /tmp/example-first.sha /tmp/example-second.sha
test "$(cat /tmp/school-pptx-phase42-example/unrelated.txt)" = keep
```

Also validate the copied Markdown explicitly. Test failure when a command-owned file path is occupied by a directory and confirm unrelated paths remain untouched.

### Regression checks

```bash
skills/school-pptx/scripts/school-pptx.sh template-report \
  --theme standard-school \
  --out-md /tmp/school-pptx-phase42/template-report.md \
  --out-json /tmp/school-pptx-phase42/template-report.json
skills/school-pptx/scripts/school-pptx.sh info
```

These checks prove the dispatcher extension did not break Phase 41 commands.

## Cross-Cutting Anti-Patterns

1. **Duplicate layout truth:** hard-coding the 11 layouts and slot budgets in parser logic instead of reading the manifest.
2. **Second parser in Phase 43:** validating one interpretation now and rendering another later.
3. **Regex-only nested parsing:** removing `::: notes` or splitting slides without a container/fence state loses source location and notes-last semantics.
4. **Fail-fast validation:** reporting only the first unsupported field/layout/media when other source-locatable errors can be collected.
5. **False best-effort success:** substituting a placeholder and returning success for invalid input.
6. **Fence-blind forbidden-syntax scanning:** rejecting HTML/CSS-like code inside fenced examples.
7. **Unsafe example replacement:** deleting or recursively replacing the caller's output directory.
8. **Non-portable fixture media:** relying on sibling skills, `test/`, absolute local paths, network assets, or user-specific files.
9. **Nondeterministic evidence:** timestamps, random ids, unstable absolute paths, or unordered sets in copied examples/JSON.
10. **Premature pagination:** generating physical-slide splits, continuation titles, or PPTX coordinates in Phase 42.

## Planning Guidance

The repository patterns support two dependency-ordered plans:

1. Contract document plus manifest-driven parser/validator and `validate` dispatcher, closed by positive/aggregate-negative command checks.
2. Canonical fixture plus skill-local media and safe deterministic `example`, closed by coverage, byte-stability, overwrite-safety, and Phase 41 regression checks.

The second plan should depend on the first because copied fixture validation must use the same canonical parser and logical model that Phase 43 will consume.

## PATTERN MAPPING COMPLETE
