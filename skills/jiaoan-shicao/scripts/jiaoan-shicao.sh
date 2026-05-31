#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_MD="$SKILL_DIR/templates/jiaoan-shicao-full.md"
CALENDAR_JSON="$SKILL_DIR/references/calendar.json"
DEFAULT_TEMPLATE_BINARY="/Users/mrered/Library/Application Support/com.mrered.presto/templates/jiaoan-shicao/presto-template-jiaoan-shicao"

usage() {
  cat <<'USAGE'
Usage:
  jiaoan-shicao.sh example --output <jiaoan-shicao-full.md> [--calendar-output <calendar.json>]
  jiaoan-shicao.sh render --input <input.md> [--typ <output.typ>] [--pdf <output.pdf>]
                          [--template <presto-template-jiaoan-shicao>]
                          [--expected-typ <reference.typ>] [--expected-pdf <reference.pdf>]
  jiaoan-shicao.sh manifest [--template <presto-template-jiaoan-shicao>]
  jiaoan-shicao.sh info [--template <presto-template-jiaoan-shicao>]
  jiaoan-shicao.sh version [--template <presto-template-jiaoan-shicao>]

Environment:
  JIAOAN_SHICAO_TEMPLATE_BINARY  Override the default Presto jiaoan-shicao template binary.
USAGE
}

die() {
  printf 'jiaoan-shicao.sh: %s\n' "$*" >&2
  exit 1
}

need_file() {
  local path="$1"
  [[ -f "$path" ]] || die "file not found: $path"
}

need_executable() {
  local path="$1"
  [[ -x "$path" ]] || die "executable not found or not executable: $path"
}

template_binary() {
  local explicit="${1:-}"
  if [[ -n "$explicit" ]]; then
    printf '%s\n' "$explicit"
  elif [[ -n "${JIAOAN_SHICAO_TEMPLATE_BINARY:-}" ]]; then
    printf '%s\n' "$JIAOAN_SHICAO_TEMPLATE_BINARY"
  else
    printf '%s\n' "$DEFAULT_TEMPLATE_BINARY"
  fi
}

mkdir_parent() {
  local path="$1"
  local parent
  parent="$(dirname -- "$path")"
  mkdir -p "$parent"
}

file_size() {
  wc -c < "$1" | tr -d '[:space:]'
}

pdf_page_count() {
  grep -ao '/Type /Page' "$1" | wc -l | tr -d '[:space:]'
}

verify_pdf_reference() {
  local expected="$1"
  local actual="$2"

  if cmp -s "$expected" "$actual"; then
    printf 'verified PDF byte-identical with %s\n' "$expected"
    return
  fi

  local expected_size actual_size expected_pages actual_pages
  expected_size="$(file_size "$expected")"
  actual_size="$(file_size "$actual")"
  expected_pages="$(pdf_page_count "$expected")"
  actual_pages="$(pdf_page_count "$actual")"

  if [[ "$expected_size" == "$actual_size" && "$expected_pages" == "$actual_pages" ]]; then
    printf 'verified PDF shape matches %s (size=%s, page-markers=%s; bytes differ, likely metadata)\n' "$expected" "$actual_size" "$actual_pages"
    return
  fi

  die "PDF differs from expected file: $expected (expected size/pages $expected_size/$expected_pages, got $actual_size/$actual_pages)"
}

cmd_example() {
  local output=""
  local calendar_output=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --output)
        output="${2:-}"
        shift 2
        ;;
      --calendar-output)
        calendar_output="${2:-}"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        die "unknown argument for example: $1"
        ;;
    esac
  done

  [[ -n "$output" ]] || die "example requires --output"
  need_file "$TEMPLATE_MD"
  mkdir_parent "$output"
  cp "$TEMPLATE_MD" "$output"
  printf 'wrote %s\n' "$output"

  if [[ -n "$calendar_output" ]]; then
    need_file "$CALENDAR_JSON"
    mkdir_parent "$calendar_output"
    cp "$CALENDAR_JSON" "$calendar_output"
    printf 'wrote %s\n' "$calendar_output"
  fi
}

cmd_render() {
  local input=""
  local typ=""
  local pdf=""
  local template_arg=""
  local expected_typ=""
  local expected_pdf=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --input)
        input="${2:-}"
        shift 2
        ;;
      --typ)
        typ="${2:-}"
        shift 2
        ;;
      --pdf)
        pdf="${2:-}"
        shift 2
        ;;
      --template)
        template_arg="${2:-}"
        shift 2
        ;;
      --expected-typ)
        expected_typ="${2:-}"
        shift 2
        ;;
      --expected-pdf)
        expected_pdf="${2:-}"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        die "unknown argument for render: $1"
        ;;
    esac
  done

  [[ -n "$input" ]] || die "render requires --input"
  need_file "$input"

  if [[ -z "$typ" ]]; then
    typ="${input%.*}.typ"
  fi

  if [[ -n "$expected_pdf" && -z "$pdf" ]]; then
    pdf="${typ%.*}.pdf"
  fi

  local renderer
  renderer="$(template_binary "$template_arg")"
  need_executable "$renderer"

  mkdir_parent "$typ"
  local tmp_typ
  tmp_typ="$(mktemp)"
  "$renderer" < "$input" > "$tmp_typ"
  mv "$tmp_typ" "$typ"
  printf 'wrote %s\n' "$typ"

  if [[ -n "$expected_typ" ]]; then
    need_file "$expected_typ"
    diff -u "$expected_typ" "$typ"
    printf 'verified Typst matches %s\n' "$expected_typ"
  fi

  if [[ -n "$pdf" ]]; then
    command -v typst >/dev/null 2>&1 || die "typst command not found"
    mkdir_parent "$pdf"
    typst compile "$typ" "$pdf"
    printf 'wrote %s\n' "$pdf"
  fi

  if [[ -n "$expected_pdf" ]]; then
    need_file "$expected_pdf"
    [[ -n "$pdf" ]] || die "--expected-pdf requires --pdf or an inferred pdf output"
    verify_pdf_reference "$expected_pdf" "$pdf"
  fi
}

cmd_passthrough() {
  local flag="$1"
  shift
  local template_arg=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --template)
        template_arg="${2:-}"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        die "unknown argument: $1"
        ;;
    esac
  done

  local renderer
  renderer="$(template_binary "$template_arg")"
  need_executable "$renderer"
  "$renderer" "$flag"
}

main() {
  local command="${1:-}"
  if [[ $# -gt 0 ]]; then
    shift
  fi

  case "$command" in
    example)
      cmd_example "$@"
      ;;
    render)
      cmd_render "$@"
      ;;
    manifest)
      cmd_passthrough -manifest "$@"
      ;;
    info)
      cmd_passthrough -info "$@"
      ;;
    version)
      cmd_passthrough -version "$@"
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
