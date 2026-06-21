#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$SCRIPT_DIR" == "${BASH_SOURCE[0]}" ]]; then
  SCRIPT_DIR="."
fi

usage() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'USAGE'
Usage:
  tiaokedan.sh render --input <tiaokedan.md> --typ <output.typ>
                       [--pdf <output.pdf>]
                       [--expected-typ <reference.typ>]
USAGE
}

die() {
  printf 'tiaokedan.sh: %s\n' "$*" >&2
  exit 1
}

if [[ $# -lt 1 ]]; then
  usage >&2
  exit 1
fi

case "$1" in
  render)
    shift
    python3 "${SCRIPT_DIR}/tiaokedan_renderer.py" render "$@"
    ;;
  -h|--help)
    usage
    ;;
  *)
    die "unknown subcommand: $1"
    ;;
esac
