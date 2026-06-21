# Phase 37: 调课单 Typst Baseline - Pattern Map

**Mapped:** 2026-06-21
**Files analyzed:** 3
**Analogs found:** 3 / 3

## Scope Boundary

Phase 37 only maps patterns for the accepted Typst baseline surface, optional compile evidence, and phase verification. Do not add Markdown contract files, renderer CLI, canonical `SKILL.md`, runtime adapter notes, README/index updates, or Phase 38-40 files.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `skills/tiaokedan/templates/tiaokedan-reference.typ` | template | transform | `skills/end-of-term-teaching-materials/templates/typst/end-of-term-package.typ` + `skills/gongwen/scripts/gongwen_lib/typst_head.sh` | exact for Typst template conventions; role-match for official typography |
| `skills/tiaokedan/templates/tiaokedan-reference.pdf` | generated evidence | file-I/O | `skills/teaching-design-package/scripts/teaching-design-package.sh` | role-match |
| `.planning/phases/37-typst-baseline/37-VERIFICATION.md` | verification | file-I/O | `skills/teaching-design-package/scripts/teaching-design-package.sh` status/diagnostic pattern + Phase 37 research verification table | role-match |

## Pattern Assignments

### `skills/tiaokedan/templates/tiaokedan-reference.typ` (template, transform)

**Analog:** `skills/end-of-term-teaching-materials/templates/typst/end-of-term-package.typ`

**Skill-local Typst template pattern** (lines 1-7):

```typst
// Fixed absolute-position Typst package template for end-of-term teaching materials.
// The renderer replaces PACKAGE_BODY with generated page fragments.
// Coordinates follow the reference scorebook prototype and use A4 points.

#set page(width: 595.3pt, height: 841.9pt, margin: 0pt)
#set text(lang: "zh", font: ("SimSun", "NSimSun", "Songti SC", "STSong"), size: 12pt)
#set par(leading: 0.05em)
```

**Apply:** Keep the accepted baseline as a reviewable skill-local `.typ` under `skills/tiaokedan/templates/`. Unlike this fixed-position A4 portrait analog, Phase 37 should use A4 landscape (`paper: "a4", flipped: true`) and preserve default margins unless visual tuning is justified.

**Positioned text/helper pattern** (lines 9-20):

```typst
#let ptext(x, y, w, h, size, body, pos: center + horizon, weight: "regular") = place(dx: x, dy: y)[#box(width: w, height: h, clip: true, inset: 0pt)[
#align(pos)[#text(size: size, weight: weight)[#body]]]]
#let ppara_nc(x, y, w, h, size, body, first-indent: 0em, pos: center + horizon, body-ratio: 0.94) = place(dx: x, dy: y)[#box(width: w, height: h, clip: false, inset: 0pt)[
#align(pos)[#box(width: w * body-ratio)[#align(left)[
#set text(size: size)
#par(leading: 0.65em)[#box(width: first-indent)[]#body]
]]]
]]
#let ptitle_nc(x, y, w, h, size, body, pos: center + horizon) = place(dx: x, dy: y)[#box(width: w, height: h, clip: false, inset: 0pt)[
#align(pos)[#text(size: size, weight: "bold", font: ("FZXiaoBiaoSong-B05", "FZXiaoBiaoSong-B05S", "SimSun", "Songti SC"))[#body]]]]
```

**Apply:** For `tiaokedan-reference.typ`, prefer normal flow layout for title, paragraph, table, and right-side signature. Reuse the local convention of small named helpers and `center + horizon` for cell alignment, but do not introduce renderer replacement placeholders.

**Analog:** `skills/gongwen/scripts/gongwen_lib/typst_head.sh`

**Chinese font fallback pattern** (lines 18-24):

```typst
// 定义常用字体名称。同类字体可以 fallback，但不跨字体类型。
#let FONT_XBS = ("FZXiaoBiaoSong-B05", "FZXiaoBiaoSong-B05S", "FZXiaoBiaoSongS-B-GB", "方正小标宋简体", "方正小标宋_GBK") // 小标宋类
#let FONT_HEI = ("SimHei", "STHeiti", "Heiti SC", "Noto Sans CJK SC", "Source Han Sans SC", "思源黑体", "Microsoft YaHei") // 黑体类
#let FONT_FS = ("FangSong", "STFangsong", "FangSong_GB2312", "Fangsong SC") // 仿宋类
#let FONT_KAI = ("KaiTi", "STKaiti", "Kaiti SC", "KaiTi_GB2312") // 楷体类
#let FONT_SONG = ("SimSun", "NSimSun", "Songti SC", "STSong", "Noto Serif CJK SC", "Source Han Serif SC", "思源宋体") // 宋体类
#let FONT_CODE = ("Noto Sans Mono CJK SC", "Source Han Mono SC", "Sarasa Mono SC", "Menlo") // 等宽类
```

**Apply:** Define only the needed Phase 37 families, e.g. `FONT_SONG` for the centered bold `调课说明` title and `FONT_FS` for body/table/signature. Preserve the same "同类 fallback, 不跨字体类型" rule.

**Page and paragraph pattern** (lines 26-35, 54-72):

```typst
#set page(
  paper: "a4",
  margin: (
    inside: 28mm,
    outside: 26mm,
    top: 37mm,
    bottom: 35mm,
  ),
)

#set text(
  lang: "zh",
  font: FONT_FS,
  size: zh(3),
  hyphenate: false,
  cjk-latin-spacing: auto,
)

#set par(
  first-line-indent: (amount: 2em, all: true),
  justify: true,
  leading: 15.6pt,
  spacing: 15.6pt,
)
```

**Apply:** Use the same Typst-level declaration style, but adapt to Phase 37: A4 landscape, title `22pt`/宋体/bold, body `14pt`/仿宋/justified, `教务处：` without first-line indent, explanatory paragraph with first-line indent.

**Table pattern** from `skills/gongwen/scripts/gongwen_lib/tables.sh` (lines 146-157, 173-185):

```bash
printf '  columns: ('
for ((i = 0; i < max_cols; i++)); do
  (( i > 0 )) && printf ', '
  printf 'auto'
done
printf '),\n'
printf '  align: ('
for ((i = 0; i < max_cols; i++)); do
  (( i > 0 )) && printf ', '
  printf '%s' "${TABLE_ALIGNS[$i]:-left}"
done
printf '),\n'
printf '  stroke: none,\n'
printf '  table.hline(y: 1, stroke: 0.75pt),\n'
printf '  table.hline(y: 2, stroke: 0.5pt),\n'
printf '  table.hline(y: %s, stroke: 0.75pt),\n' "${#rows[@]}"

split_table_row "${rows[0]}"
if [[ "$keep" == true ]]; then
  if [[ -n "$caption" ]]; then
    printf '  table.cell(colspan: %s, align: center, stroke: none, inset: 0pt)[...'
  fi
  for cell in "${TABLE_CELLS[@]}"; do printf '  '; cell_content "$cell" true; printf ',\n'; done
fi
```

**Apply:** Hand-author the 8-column table directly in Typst. Use explicit widths rather than `auto` if needed, full text block width, centered horizontal/vertical cell alignment, visible strokes, locked headers, and row-1 explicit line breaks in both time cells.

### `skills/tiaokedan/templates/tiaokedan-reference.pdf` (generated evidence, file-I/O)

**Analog:** `skills/teaching-design-package/scripts/teaching-design-package.sh`

**Optional Typst compile pattern** (lines 396-403):

```bash
compile_pdf() {
  local typ="$1" pdf="$2" log="$3"
  rm -f "$pdf" "$log"
  if ! command -v typst >/dev/null 2>&1; then
    return 20
  fi
  typst compile "$typ" "$pdf" 2>"$log"
}
```

**Apply:** The executor may compile `skills/tiaokedan/templates/tiaokedan-reference.typ` directly with `typst compile`. If `typst` is unavailable or fonts fail, record the exact blocker instead of claiming PDF readiness.

**Non-empty PDF status pattern** (lines 662-687):

```javascript
const values = model.modules.items.map((item) => {
  const stagingPath = `${stagingDir}/${item.pdf_filename}`;
  const exists = fs.existsSync(stagingPath);
  const size = exists ? fs.statSync(stagingPath).size : 0;
  return {
    module_id: item.id,
    display_name: item.display_name,
    order: item.order,
    status: exists && size > 0 ? 'passed' : exists ? 'module_pdf_empty' : 'module_pdf_missing',
    hidden_typst: `${outDir}/${item.work_typst}`,
    staging_path: stagingPath,
    public_path: `${outDir}/${item.public_pdf_filename}`,
    exists,
    nonempty: size > 0,
    size,
  };
});
process.stdout.write(JSON.stringify(values));
```

**Apply:** If the PDF is created, verification must record `exists`, `nonempty`, and byte `size`. `size > 0` is required before treating the PDF as successful evidence.

**Final readiness gate pattern** (lines 953-960):

```bash
if [[ "$RENDER_PDF" == true ]]; then
  local final_ready
  final_ready="$(node -e 'const fs=require("fs"); const s=JSON.parse(fs.readFileSync(process.argv[1],"utf8")); console.log(s.final_ready ? "true" : "false")' "${OUT_DIR}/.teaching-design-package/${STATUS_NAME}")"
  if [[ "$final_ready" != "true" ]]; then
    cp "${OUT_DIR}/.teaching-design-package/${STATUS_NAME}" "${OUT_DIR}/.teaching-design-package/failure-diagnostics/${STATUS_NAME}"
    cleanup_public_root "$OUT_DIR"
    die "render-package --pdf did not produce a final-ready course-prefixed delivery; diagnostics are under ${OUT_DIR}/.teaching-design-package/"
  fi
fi
```

**Apply:** Phase 37 does not need this full delivery gate, but it should copy the same principle: PDF success is separate from Typst source existence and must be backed by a real compile result.

### `.planning/phases/37-typst-baseline/37-VERIFICATION.md` (verification, file-I/O)

**Analog:** `.planning/phases/37-typst-baseline/37-RESEARCH.md`

**Verification checklist pattern** (lines 328-339):

```markdown
| Check | Method | Pass Condition |
|-------|--------|----------------|
| Scaffold exists | `test -d skills/tiaokedan/templates` | Directory exists; no unnecessary renderer directories unless justified. |
| Reference file exists | `test -s skills/tiaokedan/templates/tiaokedan-reference.typ` | File exists and is non-empty. |
| Locked title/body/signature | `rg -F` for `调课说明`, `教务处：`, locked paragraph, `电气工程系`, `2026年6月21日` | All strings found in `.typ`. |
| Table structure | `rg -F` for 8 headers and row facts including teacher names, class, course, room/time strings | All required headers and rows present; row 1 preserves explicit line break in both time cells. |
| Typography declarations | `rg` for `SimSun|Songti|STSong`, `FangSong|STFangsong`, `22pt|zh\\(2\\)`, `14pt|zh\\(4\\)`, `justify`, `first-line-indent`, `center + horizon` | Typst records page/font/table intent. |
| Scope boundary | `find skills/tiaokedan -maxdepth 2 -type f` plus `rg` for Markdown/renderer terms if files exist | No Phase 38-40 artifacts are introduced. |
| Typst compile | `typst compile skills/tiaokedan/templates/tiaokedan-reference.typ /tmp/tiaokedan-reference.pdf 2>/tmp/tiaokedan-typst.stderr` | If Typst/fonts work: command exits 0 and PDF exists with byte size > 0. |
| Exact blocker | Capture `command -v typst`, `typst --version`, stderr, missing font/tool notes | If compile fails or tool missing: verification records the exact blocker and does not claim PDF success. |
```

**Apply:** The Phase 37 verification file should be evidence-first: paths, locked-string checks, table/header checks, typography/layout declarations, scope boundary check, and compile success or exact blocker.

**Analog:** `skills/teaching-design-package/scripts/teaching-design-package.sh`

**Diagnostic failure pattern** (lines 110-118, 132-141):

```bash
write_failure_diagnostics() {
  local input="$1" out_dir="$2" stderr_path="$3"
  local diagnostics_path status_path
  diagnostics_path="${out_dir}/.teaching-design-package/diagnostics.json"
  status_path="${out_dir}/.teaching-design-package/${STATUS_NAME}"
  mkdir -p "${out_dir}/.teaching-design-package/failure-diagnostics"
  node - "$input" "$stderr_path" "$diagnostics_path" "$status_path" <<'NODE'
const fs = require('fs');
const input = process.argv[2];
const stderrPath = process.argv[3];
...
const diagnostics = {
  status: 'failed',
  source_markdown: input,
  calendar: error.calendar || null,
  model_version: error.model_version || null,
  errors: [error],
  stderr_log: stderrPath,
  failure_classes: [
```

**Apply:** Do not create a full diagnostics subsystem for Phase 37, but record the same essentials in `37-VERIFICATION.md`: `status`, source Typst path, attempted command, stderr/blocker path or pasted error summary, and whether PDF evidence is non-empty.

## Shared Patterns

### Skill Directory Ownership

**Source:** `docs/directory-spec.md` lines 19-30

```markdown
| `skills/<skill-name>/SKILL.md` | canonical 技能源文件 |
| `skills/<skill-name>/references/` | 可按需读取的长参考资料、支持文件和格式说明 |
| `skills/<skill-name>/scripts/` | 技能需要调用的辅助脚本 |
| `skills/<skill-name>/templates/` | 技能输出模板或文件模板 |
```

**Apply to:** `skills/tiaokedan/templates/tiaokedan-reference.typ` and optional PDF evidence. Create only the `templates/` directory needed for this phase; avoid `scripts/`, `references/`, and `SKILL.md` unless the plan deliberately scopes a Phase 37 placeholder.

### Repository Editing Boundary

**Source:** `AGENTS.md` lines 11-19, 21-27

```markdown
- 优先保持文档和模板简洁、可复制、可审阅。
- 模板只放在 `templates/`，不要把示例内容和模板混在一起。
- 技能涉及外部命令、网络、凭据或文件写入时，必须写明安全边界和验证步骤。
```

**Apply to:** Keep the `.typ` concise and reviewable. Any `typst compile` evidence must state command, environment dependency, and result/blocker.

### Font Families

**Source:** `skills/gongwen/scripts/gongwen_lib/typst_head.sh` lines 18-24

```typst
#let FONT_FS = ("FangSong", "STFangsong", "FangSong_GB2312", "Fangsong SC") // 仿宋类
#let FONT_SONG = ("SimSun", "NSimSun", "Songti SC", "STSong", "Noto Serif CJK SC", "Source Han Serif SC", "思源宋体") // 宋体类
```

**Apply to:** Title uses `FONT_SONG`; body, table, and signature use `FONT_FS`. Do not borrow unrelated 黑体/楷体/sans families for Phase 37.

### PDF Evidence

**Source:** `skills/teaching-design-package/scripts/teaching-design-package.sh` lines 396-403 and 662-687

```bash
typst compile "$typ" "$pdf" 2>"$log"
```

```javascript
status: exists && size > 0 ? 'passed' : exists ? 'module_pdf_empty' : 'module_pdf_missing',
nonempty: size > 0,
size,
```

**Apply to:** Optional `tiaokedan-reference.pdf` and `37-VERIFICATION.md`. The PDF is successful only when the compile command exits 0 and the resulting PDF is non-empty.

## No Analog Found

None. Every Phase 37 file has a close enough in-repo analog. The analogs are intentionally pattern sources only; the new `tiaokedan` files must not call sibling skill scripts.

## Metadata

**Analog search scope:** `skills/**/*.typ`, `skills/**/*.sh`, `.planning/phases/**/*VERIFICATION.md`, required Phase 37 context/research files
**Files scanned:** 14 targeted files plus required Phase 37/project context
**Pattern extraction date:** 2026-06-21
