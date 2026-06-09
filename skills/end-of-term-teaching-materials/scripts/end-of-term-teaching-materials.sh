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
  end-of-term-teaching-materials.sh example --output <source.json>
  end-of-term-teaching-materials.sh validate --input <source.json|markdown.md>
  end-of-term-teaching-materials.sh markdown --input <source.json> --output <end-of-term-full.md>
  end-of-term-teaching-materials.sh render --input <end-of-term-full.md> --workdir <dir> [--pdf]
  end-of-term-teaching-materials.sh verify --workdir <dir>
  end-of-term-teaching-materials.sh manifest
  end-of-term-teaching-materials.sh info
  end-of-term-teaching-materials.sh version

The pipeline is structured data -> Markdown -> Typst/PDF + deterministic table
artifacts. Parent output directories and --workdir must already exist.
USAGE
}

die() {
  printf 'end-of-term-teaching-materials.sh: %s\n' "$*" >&2
  exit 1
}

ensure_parent_dir() {
  local path="$1" parent
  parent="${path%/*}"
  if [[ "$parent" != "$path" && -n "$parent" && ! -d "$parent" ]]; then
    die "parent directory does not exist: $parent"
  fi
}

need_file() {
  [[ -f "$1" ]] || die "file not found: $1"
}

need_workdir() {
  [[ -d "$1" ]] || die "workdir does not exist: $1"
}

cmd="${1:-}"
if [[ -z "$cmd" || "$cmd" == "-h" || "$cmd" == "--help" ]]; then
  usage
  exit 0
fi
shift || true

case "$cmd" in
  example)
    output=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --output) output="${2:-}"; shift 2 ;;
        *) die "unknown argument for example: $1" ;;
      esac
    done
    [[ -n "$output" ]] || die "example requires --output"
    ensure_parent_dir "$output"
    python3 "$PY_HELPER" example --skill-dir "$SKILL_DIR" --output "$output"
    ;;
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
  markdown)
    input=""
    output=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --input) input="${2:-}"; shift 2 ;;
        --output) output="${2:-}"; shift 2 ;;
        *) die "unknown argument for markdown: $1" ;;
      esac
    done
    [[ -n "$input" ]] || die "markdown requires --input"
    [[ -n "$output" ]] || die "markdown requires --output"
    need_file "$input"
    ensure_parent_dir "$output"
    python3 "$PY_HELPER" markdown --skill-dir "$SKILL_DIR" --input "$input" --output "$output"
    ;;
  render)
    input=""
    workdir=""
    pdf=false
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --input) input="${2:-}"; shift 2 ;;
        --workdir) workdir="${2:-}"; shift 2 ;;
        --pdf) pdf=true; shift ;;
        *) die "unknown argument for render: $1" ;;
      esac
    done
    [[ -n "$input" ]] || die "render requires --input"
    [[ -n "$workdir" ]] || die "render requires --workdir"
    need_file "$input"
    need_workdir "$workdir"
    if [[ "$pdf" == true ]]; then
      python3 "$PY_HELPER" render --skill-dir "$SKILL_DIR" --input "$input" --workdir "$workdir" --pdf
    else
      python3 "$PY_HELPER" render --skill-dir "$SKILL_DIR" --input "$input" --workdir "$workdir"
    fi
    ;;
  verify)
    workdir=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --workdir) workdir="${2:-}"; shift 2 ;;
        *) die "unknown argument for verify: $1" ;;
      esac
    done
    [[ -n "$workdir" ]] || die "verify requires --workdir"
    need_workdir "$workdir"
    python3 "$PY_HELPER" verify --skill-dir "$SKILL_DIR" --workdir "$workdir"
    ;;
  manifest|info|version)
    python3 "$PY_HELPER" "$cmd" --skill-dir "$SKILL_DIR"
    ;;
  *)
    usage >&2
    die "unknown command: $cmd"
    ;;
esac
