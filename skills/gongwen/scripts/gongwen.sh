#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${LC_ALL:-}" && -z "${LANG:-}" ]]; then
  for locale_name in C.UTF-8 C.utf8; do
    if locale -a 2>/dev/null | grep -Fxq "$locale_name"; then
      export LC_ALL="$locale_name"
      break
    fi
  done
fi

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
