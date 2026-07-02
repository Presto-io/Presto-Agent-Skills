#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$SCRIPT_DIR" == "${BASH_SOURCE[0]}" ]]; then
  SCRIPT_DIR="."
fi
SKILL_DIR="${SCRIPT_DIR}/.."
PY_HELPER="${SCRIPT_DIR}/render_package.py"

usage() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'USAGE'
Usage:
  end-of-term-teaching-materials.sh validate --input <end-of-term-full.md>
  end-of-term-teaching-materials.sh deliver --input <end-of-term-full.md> --out-dir <dir>
  end-of-term-teaching-materials.sh info
  end-of-term-teaching-materials.sh version

The delivery path is reviewed Markdown -> Typst/PDF + one 4-column score-list
workbook. JSON/CSV/manifest/verification artifacts are not part of this skill
command surface.
USAGE
}

die() {
  printf 'end-of-term-teaching-materials.sh: %s\n' "$*" >&2
  exit 1
}

need_file() {
  [[ -f "$1" ]] || die "file not found: $1"
}

cmd="${1:-}"
if [[ -z "$cmd" || "$cmd" == "-h" || "$cmd" == "--help" ]]; then
  usage
  exit 0
fi
shift || true

case "$cmd" in
  validate)
    input=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --input) input="${2:-}"; shift 2 ;;
        *) die "unknown argument for validate: $1" ;;
      esac
    done
    [[ -n "$input" ]] || die "validate requires --input"
    need_file "$input"
    python3 "$PY_HELPER" validate --skill-dir "$SKILL_DIR" --input "$input"
    ;;
  deliver)
    input=""
    out_dir=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --input) input="${2:-}"; shift 2 ;;
        --out-dir) out_dir="${2:-}"; shift 2 ;;
        *) die "unknown argument for deliver: $1" ;;
      esac
    done
    [[ -n "$input" ]] || die "deliver requires --input"
    [[ -n "$out_dir" ]] || die "deliver requires --out-dir"
    need_file "$input"
    mkdir -p "$out_dir"
    args=(deliver --skill-dir "$SKILL_DIR" --input "$input" --out-dir "$out_dir")
    python3 "$PY_HELPER" "${args[@]}"
    ;;
  info|version)
    python3 "$PY_HELPER" "$cmd" --skill-dir "$SKILL_DIR"
    ;;
  *)
    usage >&2
    die "unknown command: $cmd"
    ;;
esac
