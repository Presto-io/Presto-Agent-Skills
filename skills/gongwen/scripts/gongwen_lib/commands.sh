usage() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'USAGE'
Usage:
  gongwen.sh example --output <标题.md>
  gongwen.sh render --input <input.md> [--typ <output.typ>]
                    [--pdf <output.pdf>]
                    [--expected-typ <reference.typ>]
  gongwen.sh info
  gongwen.sh version

The Markdown-to-Typst conversion is implemented by this Bash script itself. It
does not call the Presto template executable or any external Markdown parser.
PDF export is optional and uses the installed typst CLI only when --pdf is set.
The --typ path owns the delivery root and stem. When --pdf is set it must use
that same root and stem. Publication is candidate-first with exact-set no-op,
whole-bundle history, and handled-failure rollback.
USAGE
}

cmd_example() {
  local output=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --output) output="${2:-}"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) die "unknown argument for example: $1" ;;
    esac
  done
  [[ -n "$output" ]] || die "example requires --output"
  need_file "$TEMPLATE_MD"
  ensure_parent_dir "$output"
  copy_file_shell "$TEMPLATE_MD" "$output"
  printf 'wrote %s\n' "$output"
}

resolve_typst_bin() {
  local typst_bin=""
  if [[ -n "${TYPST_BIN:-}" ]]; then
    [[ -x "$TYPST_BIN" ]] || die "TYPST_BIN is not executable: $TYPST_BIN"
    typst_bin="$TYPST_BIN"
  elif typst_bin="$(command -v typst 2>/dev/null)"; then
    :
  elif [[ -x /opt/data/.bin/typst ]]; then
    typst_bin="/opt/data/.bin/typst"
  else
    die "typst CLI not found; set TYPST_BIN, install typst, or omit --pdf"
  fi
  printf '%s' "$typst_bin"
}

cmd_render() {
  local input="" typ="" pdf="" expected_typ="" input_parent typst_bin font_path=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --input) input="${2:-}"; shift 2 ;;
      --typ) typ="${2:-}"; shift 2 ;;
      --pdf) pdf="${2:-}"; shift 2 ;;
      --expected-typ) expected_typ="${2:-}"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) die "unknown argument for render: $1" ;;
    esac
  done
  [[ -n "$input" ]] || die "render requires --input"
  need_file "$input"
  [[ -n "$typ" ]] || typ="${input%.*}.typ"
  delivery_begin "$typ" "$pdf"
  cp -- "$input" "$DELIVERY_CANDIDATE/$DELIVERY_STEM.md"
  render_markdown_to_typst "$input" "$DELIVERY_CANDIDATE/$DELIVERY_STEM.typ"
  if [[ -n "$expected_typ" ]]; then
    need_file "$expected_typ"
    delivery_same_file "$expected_typ" "$DELIVERY_CANDIDATE/$DELIVERY_STEM.typ" || die "Typst differs from expected file: $expected_typ"
    printf 'verified Typst matches %s\n' "$expected_typ"
  fi
  if [[ -n "$pdf" ]]; then
    typst_bin="$(resolve_typst_bin)"
    input_parent="${input%/*}"
    [[ "$input_parent" != "$input" ]] || input_parent="."
    input_parent="$(cd "$input_parent" && pwd -P)"
    if [[ -n "${TYPST_FONT_PATH:-}" ]]; then
      [[ -d "$TYPST_FONT_PATH" ]] || die "TYPST_FONT_PATH is not a directory: $TYPST_FONT_PATH"
      font_path="$TYPST_FONT_PATH"
    elif [[ -d /opt/data/fonts ]]; then
      font_path="/opt/data/fonts"
    fi
    if [[ -n "$font_path" ]]; then
      "$typst_bin" compile --font-path "$font_path" --root "$input_parent" - "$DELIVERY_CANDIDATE/$DELIVERY_STEM.pdf" < "$DELIVERY_CANDIDATE/$DELIVERY_STEM.typ"
    else
      "$typst_bin" compile --root "$input_parent" - "$DELIVERY_CANDIDATE/$DELIVERY_STEM.pdf" < "$DELIVERY_CANDIDATE/$DELIVERY_STEM.typ"
    fi
    delivery_is_regular_nonempty "$DELIVERY_CANDIDATE/$DELIVERY_STEM.pdf" || die "typst did not produce a readable non-empty candidate PDF"
    [[ "$(head -c 5 "$DELIVERY_CANDIDATE/$DELIVERY_STEM.pdf")" == "%PDF-" ]] || die "typst produced a candidate with an invalid PDF header"
  fi
  delivery_publish
  printf '%s delivery: %s\n' "$DELIVERY_RESULT" "$DELIVERY_ROOT"
}

cmd_info() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'INFO'
gongwen shell-only renderer
- Markdown-to-Typst conversion is performed inside this Bash script.
- The script does not call external template binaries or Markdown converters.
- PDF compilation is optional via --pdf and requires an installed typst CLI.
- Current delivery is the exact same-stem Markdown+Typst pair, or that pair plus PDF.
- Candidate gates complete before publication; changed bundles archive together.
INFO
}

cmd_version() {
  printf 'gongwen.sh 0.2.2-shell-only\n'
}
