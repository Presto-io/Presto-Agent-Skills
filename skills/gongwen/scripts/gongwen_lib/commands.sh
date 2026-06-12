usage() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'USAGE'
Usage:
  gongwen.sh example --output <gongwen-full.md>
  gongwen.sh render --input <input.md> [--typ <output.typ>]
                    [--pdf <output.pdf>]
                    [--expected-typ <reference.typ>]
  gongwen.sh manifest
  gongwen.sh info
  gongwen.sh version

The Markdown-to-Typst conversion is implemented by this Bash script itself. It
does not call the Presto template executable or any external Markdown parser.
PDF export is optional and uses the installed typst CLI only when --pdf is set.
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

cmd_render() {
  local input="" typ="" pdf="" expected_typ=""
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
  render_markdown_to_typst "$input" "$typ"
  printf 'wrote %s\n' "$typ"
  if [[ -n "$expected_typ" ]]; then
    need_file "$expected_typ"
    same_file_shell "$expected_typ" "$typ" || die "Typst differs from expected file: $expected_typ"
    printf 'verified Typst matches %s\n' "$expected_typ"
  fi
  if [[ -n "$pdf" ]]; then
    command -v typst >/dev/null 2>&1 || die "typst CLI not found; install typst or omit --pdf"
    ensure_parent_dir "$pdf"
    typst compile "$typ" "$pdf"
    printf 'wrote %s\n' "$pdf"
  fi
}

cmd_manifest() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'JSON'
{
  "name": "gongwen",
  "displayName": "类公文模板",
  "version": "0.2.1-shell-only",
  "description": "Bash-only Markdown-to-Typst renderer with optional Typst PDF export."
}
JSON
}

cmd_info() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'INFO'
gongwen shell-only renderer
- Markdown-to-Typst conversion is performed inside this Bash script.
- The script does not call external template binaries or Markdown converters.
- PDF compilation is optional via --pdf and requires an installed typst CLI.
INFO
}

cmd_version() {
  printf 'gongwen.sh 0.2.1-shell-only\n'
}
