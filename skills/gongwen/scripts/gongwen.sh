#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$SCRIPT_DIR" == "${BASH_SOURCE[0]}" ]]; then
  SCRIPT_DIR="."
fi
SKILL_DIR="${SCRIPT_DIR}/.."
TEMPLATE_MD="${SKILL_DIR}/templates/gongwen.md"

source "$SCRIPT_DIR/gongwen_lib/common.sh"
source "$SCRIPT_DIR/gongwen_lib/delivery.sh"
source "$SCRIPT_DIR/gongwen_lib/inline.sh"
source "$SCRIPT_DIR/gongwen_lib/frontmatter.sh"
source "$SCRIPT_DIR/gongwen_lib/typst_head.sh"
source "$SCRIPT_DIR/gongwen_lib/images.sh"
source "$SCRIPT_DIR/gongwen_lib/tables.sh"
source "$SCRIPT_DIR/gongwen_lib/body.sh"
source "$SCRIPT_DIR/gongwen_lib/commands.sh"

main() {
  local command="${1:-}"
  [[ $# -gt 0 ]] && shift
  case "$command" in
    example) cmd_example "$@" ;;
    render) cmd_render "$@" ;;
    info) cmd_info "$@" ;;
    version) cmd_version "$@" ;;
    -h|--help|"") usage ;;
    *) die "unknown command: $command" ;;
  esac
}

main "$@"
