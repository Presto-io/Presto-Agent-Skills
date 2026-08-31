#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf '%s\n' 'Usage: inspect-calendar-pdf.sh --input <school-calendar.pdf> --out-dir <diagnostic-dir>'
  printf '%s\n' 'Writes extracted layout text and one PNG per PDF page for calendar review.'
}

input=''
out_dir=''
while [[ $# -gt 0 ]]; do
  case "$1" in
    --input)
      [[ $# -ge 2 ]] || { usage >&2; exit 1; }
      input="$2"
      shift 2
      ;;
    --out-dir)
      [[ $# -ge 2 ]] || { usage >&2; exit 1; }
      out_dir="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'inspect-calendar-pdf.sh: unknown argument: %s\n' "$1" >&2
      exit 1
      ;;
  esac
done

[[ -f "$input" ]] || { printf 'inspect-calendar-pdf.sh: input PDF not found\n' >&2; exit 1; }
[[ -n "$out_dir" ]] || { usage >&2; exit 1; }
command -v pdftotext >/dev/null || { printf 'inspect-calendar-pdf.sh: pdftotext is required\n' >&2; exit 1; }
command -v pdftoppm >/dev/null || { printf 'inspect-calendar-pdf.sh: pdftoppm is required\n' >&2; exit 1; }

mkdir -p "$out_dir"
pdftotext -layout "$input" "$out_dir/calendar-layout.txt"
pdftoppm -png -r 200 "$input" "$out_dir/calendar-page"
printf '%s\n' "$out_dir"
