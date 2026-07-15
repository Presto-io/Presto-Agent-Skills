#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"

usage() {
  cat <<'USAGE'
Usage:
  school-pptx.sh validate --input <deck.md> [--out-json <logical-document.json>]
  school-pptx.sh example --out-dir <dir>
  school-pptx.sh render --input <reviewed.md> --out-dir <delivery-dir> [--stem <name>]
  school-pptx.sh verify --workdir <dir>
  school-pptx.sh template-report --theme <theme-id> --out-md <report.md> --out-json <report.json>
                                  [--manifest <manifest.yaml>] [--template <template.pptx>]
                                  [--geometry-tolerance-emu <integer>]
  school-pptx.sh info

Commands:
  validate         Validate Markdown and optionally write the logical document JSON.
  example          Generate the deterministic full fixture and four companion media files.
  render           Publish same-stem Markdown and editable PPTX artifacts.
  verify           Run isolated verification and publish bounded evidence under the caller workdir.
  template-report  Validate the controlled PPTX template and write Markdown/JSON evidence.
  info             Print the skill-local template and manifest paths.
USAGE
}

die() {
  printf 'school-pptx.sh: %s\n' "$*" >&2
  exit 1
}

main() {
  local command="${1:-}"
  if [[ $# -gt 0 ]]; then
    shift
  fi

  case "$command" in
    validate|example)
      "${SCHOOL_PPTX_PYTHON:-python3}" "$SCRIPT_DIR/markdown_contract.py" "$SKILL_DIR" "$command" "$@"
      ;;
    render)
      "${SCHOOL_PPTX_PYTHON:-python3}" "$SCRIPT_DIR/pptx_render.py" "$SKILL_DIR" "$@"
      ;;
    verify)
      "${SCHOOL_PPTX_PYTHON:-python3}" "$SCRIPT_DIR/verify_school_pptx.py" "$SKILL_DIR" "$@"
      ;;
    template-report)
      "${SCHOOL_PPTX_PYTHON:-python3}" "$SCRIPT_DIR/template_report.py" "$SKILL_DIR" "$@"
      ;;
    info)
      printf 'template: %s\n' "$SKILL_DIR/templates/standard-school.pptx"
      printf 'manifest: %s\n' "$SKILL_DIR/templates/standard-school.manifest.yaml"
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
