#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$SCRIPT_DIR" == "${BASH_SOURCE[0]}" ]]; then
  SCRIPT_DIR="."
fi
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${SKILL_DIR}/../.." && pwd)"
TEMPLATE_MD="${SKILL_DIR}/templates/teaching-design-package-full.md"
MANIFEST_NAME="teaching-design-package-manifest.json"

usage() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'USAGE'
Usage:
  teaching-design-package.sh example --output <teaching-design-package-full.md>
  teaching-design-package.sh plan-split --input <package.md> --out-dir <dir>
  teaching-design-package.sh render-split --input <package.md> --out-dir <dir>
  teaching-design-package.sh manifest --input <package.md> --out-dir <dir>
  teaching-design-package.sh info
  teaching-design-package.sh version

Phase 23 supports split teaching-plan and lesson-plan outputs only.
Phase 24 owns optional end-of-term-package.pdf and combined teaching-design-package.pdf behavior.
USAGE
}

die() {
  printf 'teaching-design-package.sh: %s\n' "$*" >&2
  exit 1
}

need_file() {
  [[ -f "$1" ]] || die "file not found: $1"
}

ensure_parent_dir() {
  local path="$1" parent
  parent="${path%/*}"
  if [[ "$parent" != "$path" && -n "$parent" && ! -d "$parent" ]]; then
    die "parent directory does not exist: $parent"
  fi
}

parse_io_args() {
  INPUT=""
  OUT_DIR=""
  OUTPUT=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --input)
        [[ $# -ge 2 ]] || die "--input requires a path"
        INPUT="$2"
        shift 2
        ;;
      --out-dir)
        [[ $# -ge 2 ]] || die "--out-dir requires a path"
        OUT_DIR="$2"
        shift 2
        ;;
      --output)
        [[ $# -ge 2 ]] || die "--output requires a path"
        OUTPUT="$2"
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
}

frontmatter_value() {
  local input="$1" key="$2"
  awk -v key="$key" '
    BEGIN { in_fm=0 }
    NR == 1 && $0 == "---" { in_fm=1; next }
    in_fm && $0 == "---" { exit }
    in_fm && index($0, key ":") == 1 {
      sub("^[^:]+:[[:space:]]*", "")
      gsub(/^"|"$/, "")
      print
      exit
    }
  ' "$input"
}

json_escape() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  value="${value//$'\n'/\\n}"
  printf '%s' "$value"
}

has_section() {
  local input="$1" section="$2"
  grep -q "^## ${section}$" "$input"
}

validate_package() {
  local input="$1" section
  need_file "$input"
  for section in "课程与整包元数据" "调度输入" "调度证据" "授课计划" "实操教案" "输出清单" "复核标记"; do
    has_section "$input" "$section" || die "missing required section: ## ${section}"
  done
}

review_marker_state() {
  local input="$1"
  local in_section=false in_comment=false line trimmed markers=() escaped
  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" == "## 复核标记" ]]; then
      in_section=true
      continue
    fi
    if [[ "$in_section" == true && "$line" == "## "* ]]; then
      break
    fi
    [[ "$in_section" == true ]] || continue
    trimmed="${line#"${line%%[![:space:]-]*}"}"
    trimmed="${trimmed%"${trimmed##*[![:space:]]}"}"
    [[ -n "$trimmed" ]] || continue
    if [[ "$trimmed" == "<!--"* ]]; then
      in_comment=true
      [[ "$trimmed" == *"-->" ]] && in_comment=false
      continue
    fi
    if [[ "$in_comment" == true ]]; then
      [[ "$trimmed" == *"-->" ]] && in_comment=false
      continue
    fi
    [[ "$trimmed" == "无" ]] && continue
    markers+=("$trimmed")
  done < "$input"
  if [[ "${#markers[@]}" -eq 0 ]]; then
    printf '[]'
    return 0
  fi
  printf '['
  local i
  for i in "${!markers[@]}"; do
    escaped="$(json_escape "${markers[$i]}")"
    [[ "$i" -gt 0 ]] && printf ','
    printf '"%s"' "$escaped"
  done
  printf ']'
}

write_manifest() {
  local package_md="$1" out_dir="$2" teaching_typ_status="$3" lesson_typ_status="$4"
  local manifest review_markers final_ready teaching_pdf_status lesson_pdf_status
  mkdir -p "$out_dir"
  manifest="${out_dir}/${MANIFEST_NAME}"
  review_markers="$(review_marker_state "$package_md")"
  teaching_pdf_status="not_run"
  lesson_pdf_status="not_run"
  if [[ "$review_markers" == "[]" && "$teaching_typ_status" == "passed" && "$lesson_typ_status" == "passed" && "$teaching_pdf_status" == "passed" && "$lesson_pdf_status" == "passed" ]]; then
    final_ready="true"
  else
    final_ready="false"
  fi
  {
    printf '{\n'
    printf '  "package_markdown": "%s",\n' "$(json_escape "$package_md")"
    printf '  "teaching_plan_typ": {\n'
    printf '    "path": "%s",\n' "$(json_escape "${out_dir}/teaching-plan.typ")"
    printf '    "status": "%s"\n' "$teaching_typ_status"
    printf '  },\n'
    printf '  "lesson_plans_typ": {\n'
    printf '    "path": "%s",\n' "$(json_escape "${out_dir}/lesson-plans.typ")"
    printf '    "status": "%s"\n' "$lesson_typ_status"
    printf '  },\n'
    printf '  "teaching_plan_pdf": {\n'
    printf '    "path": "%s",\n' "$(json_escape "${out_dir}/teaching-plan.pdf")"
    printf '    "status": "%s"\n' "$teaching_pdf_status"
    printf '  },\n'
    printf '  "lesson_plans_pdf": {\n'
    printf '    "path": "%s",\n' "$(json_escape "${out_dir}/lesson-plans.pdf")"
    printf '    "status": "%s"\n' "$lesson_pdf_status"
    printf '  },\n'
    printf '  "review_markers": %s,\n' "$review_markers"
    printf '  "final_ready": %s,\n' "$final_ready"
    printf '  "phase_24_deferred": [\n'
    printf '    "optional end-of-term module",\n'
    printf '    "combined teaching-design-package.pdf",\n'
    printf '    "end-of-term-package.pdf"\n'
    printf '  ]\n'
    printf '}\n'
  } > "$manifest"
  printf '%s\n' "$manifest"
}

write_jihua_scaffold() {
  local package_md="$1" out="$2"
  frontmatter_value "$package_md" course_name >/dev/null
  cp "${SKILL_DIR}/../jiaoan-jihua/templates/jiaoan-jihua-full.md" "$out"
}

write_shicao_scaffold() {
  local package_md="$1" out="$2"
  frontmatter_value "$package_md" course_name >/dev/null
  cp "${SKILL_DIR}/../jiaoan-shicao/templates/jiaoan-shicao-full.md" "$out"
}

cmd_example() {
  parse_io_args "$@"
  [[ -n "$OUTPUT" ]] || die "example requires --output"
  need_file "$TEMPLATE_MD"
  ensure_parent_dir "$OUTPUT"
  cp "$TEMPLATE_MD" "$OUTPUT"
}

cmd_plan_split() {
  parse_io_args "$@"
  [[ -n "$INPUT" ]] || die "plan-split requires --input"
  [[ -n "$OUT_DIR" ]] || die "plan-split requires --out-dir"
  validate_package "$INPUT"
  mkdir -p "$OUT_DIR"
  write_jihua_scaffold "$INPUT" "${OUT_DIR}/jiaoan-jihua-full.md"
  write_shicao_scaffold "$INPUT" "${OUT_DIR}/jiaoan-shicao-full.md"
  write_manifest "$INPUT" "$OUT_DIR" "planned" "planned" >/dev/null
}

cmd_render_split() {
  parse_io_args "$@"
  [[ -n "$INPUT" ]] || die "render-split requires --input"
  [[ -n "$OUT_DIR" ]] || die "render-split requires --out-dir"
  cmd_plan_split --input "$INPUT" --out-dir "$OUT_DIR"
  # Existing render commands kept explicit for verification:
  # skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render
  # skills/jiaoan-shicao/scripts/jiaoan-shicao.sh render
  "${REPO_ROOT}/skills/jiaoan-jihua/scripts/jiaoan-jihua.sh" render \
    --input "${OUT_DIR}/jiaoan-jihua-full.md" \
    --typ "${OUT_DIR}/teaching-plan.typ"
  "${REPO_ROOT}/skills/jiaoan-shicao/scripts/jiaoan-shicao.sh" render \
    --input "${OUT_DIR}/jiaoan-shicao-full.md" \
    --typ "${OUT_DIR}/lesson-plans.typ"
  if [[ -f "${OUT_DIR}/teaching-plan.typ" && -f "${OUT_DIR}/lesson-plans.typ" ]]; then
    write_manifest "$INPUT" "$OUT_DIR" "passed" "passed" >/dev/null
  else
    write_manifest "$INPUT" "$OUT_DIR" "failed" "failed" >/dev/null
    die "split Typst render did not produce expected files"
  fi
}

cmd_manifest() {
  parse_io_args "$@"
  [[ -n "$INPUT" ]] || die "manifest requires --input"
  [[ -n "$OUT_DIR" ]] || die "manifest requires --out-dir"
  validate_package "$INPUT"
  local teaching_status="planned" lesson_status="planned"
  [[ -f "${OUT_DIR}/teaching-plan.typ" ]] && teaching_status="passed"
  [[ -f "${OUT_DIR}/lesson-plans.typ" ]] && lesson_status="passed"
  write_manifest "$INPUT" "$OUT_DIR" "$teaching_status" "$lesson_status"
}

cmd_info() {
  printf 'teaching-design-package: Markdown-first orchestration over jiaoan-jihua and jiaoan-shicao.\n'
  printf 'Package checkpoint: templates/teaching-design-package-full.md\n'
  printf 'Reference: references/format-and-orchestration.md\n'
  printf 'Phase 24 deferred: optional end-of-term-package.pdf and combined teaching-design-package.pdf.\n'
}

cmd_version() {
  printf 'teaching-design-package.sh 0.1.0\n'
}

main() {
  local command="${1:-}"
  [[ -n "$command" ]] || { usage; exit 1; }
  shift || true
  case "$command" in
    example) cmd_example "$@" ;;
    plan-split) cmd_plan_split "$@" ;;
    render-split) cmd_render_split "$@" ;;
    manifest) cmd_manifest "$@" ;;
    info) cmd_info "$@" ;;
    version) cmd_version "$@" ;;
    -h|--help|help) usage ;;
    *) die "unknown command: $command" ;;
  esac
}

main "$@"
