#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"

usage() {
  cat <<'USAGE'
Usage:
  school-presentation.sh example --output <school-presentation-full.md>
  school-presentation.sh render --input <input.md> [--html <output.html>]
                                [--manifest <manifest.json>]
                                [--max-size-mb <mb>]
  school-presentation.sh bookmark-pdf --pdf <printed.pdf> --manifest <manifest.json>
                                      [--output <bookmarked.pdf>]
  school-presentation.sh verify --workdir <dir> [--max-size-mb <mb>]
  school-presentation.sh info

Environment:
  SCHOOL_PRESENTATION_MAX_MB  Override the default 50 MB output cap.
USAGE
}

die() {
  printf 'school-presentation.sh: %s\n' "$*" >&2
  exit 1
}

python_renderer() {
  PYTHONPATH="$SCRIPT_DIR${PYTHONPATH:+:$PYTHONPATH}" "${SCHOOL_PRESENTATION_PYTHON:-python3}" -m school_presentation.cli "$SKILL_DIR" "$@"
}

main() {
  local command="${1:-}"
  if [[ $# -gt 0 ]]; then
    shift
  fi

  case "$command" in
    example|render|verify|bookmark-pdf|info)
      python_renderer "$command" "$@"
      ;;
    -h|--help|"")
      usage
      ;;
    *)
      die "unknown command: $command"
      ;;
  esac
}

main "$@"
