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
END_OF_TERM_SCRIPT="${REPO_ROOT}/skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh"

usage() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'USAGE'
Usage:
  teaching-design-package.sh example --output <teaching-design-package-full.md>
  teaching-design-package.sh plan-split --input <package.md> --out-dir <dir>
  teaching-design-package.sh render-split --input <package.md> --out-dir <dir>
  teaching-design-package.sh plan-end-of-term --input <package.md> --out-dir <dir>
  teaching-design-package.sh render-end-of-term --input <package.md> --out-dir <dir>
  teaching-design-package.sh render-package --input <package.md> --out-dir <dir>
  teaching-design-package.sh manifest --input <package.md> --out-dir <dir>
  teaching-design-package.sh info
  teaching-design-package.sh version

Optional end-of-term behavior delegates to skills/end-of-term-teaching-materials.
Combined teaching-design-package.pdf is passed only when the actual file exists.
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

end_of_term_enabled() {
  local input="$1"
  awk '
    BEGIN { in_fm=0; in_mod=0; in_eot=0 }
    NR == 1 && $0 == "---" { in_fm=1; next }
    in_fm && $0 == "---" { exit }
    !in_fm { next }
    /^modules:[[:space:]]*$/ { in_mod=1; next }
    in_mod && /^  [A-Za-z0-9_]+:[[:space:]]*$/ {
      in_eot=($1 == "end_of_term:")
      next
    }
    in_eot && /^    enabled:[[:space:]]*/ {
      value=$0
      sub(/^    enabled:[[:space:]]*/, "", value)
      gsub(/"/, "", value)
      print value
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

json_bool_from_manifest() {
  local manifest="$1" key="$2" default_value="${3:-false}"
  if [[ -f "$manifest" ]] && grep -q "\"${key}\"[[:space:]]*:[[:space:]]*true" "$manifest"; then
    printf 'true'
  elif [[ -f "$manifest" ]] && grep -q "\"${key}\"[[:space:]]*:[[:space:]]*false" "$manifest"; then
    printf 'false'
  else
    printf '%s' "$default_value"
  fi
}

end_of_term_review_markers() {
  local handoff="$1"
  if [[ -f "$handoff" ]]; then
    review_marker_state "$handoff"
  else
    printf '[]'
  fi
}

status_for_file() {
  local path="$1" planned_status="${2:-not_run}"
  if [[ -f "$path" ]]; then
    printf 'passed'
  else
    printf '%s' "$planned_status"
  fi
}

all_split_pdfs_exist() {
  local teaching_pdf="$1" lesson_pdf="$2" eot_enabled="$3" eot_pdf="$4"
  [[ -f "$teaching_pdf" && -f "$lesson_pdf" ]] || return 1
  if [[ "$eot_enabled" == "true" ]]; then
    [[ -f "$eot_pdf" ]] || return 1
  fi
}

merge_combined_pdf() {
  local out_dir="$1" eot_enabled="$2"
  local combined="${out_dir}/teaching-design-package.pdf"
  local teaching_pdf="${out_dir}/teaching-plan.pdf"
  local lesson_pdf="${out_dir}/lesson-plans.pdf"
  local eot_pdf="${out_dir}/end-of-term-output/end-of-term-package.pdf"
  [[ -f "$combined" ]] && { printf 'passed:existing_file'; return 0; }
  if ! all_split_pdfs_exist "$teaching_pdf" "$lesson_pdf" "$eot_enabled" "$eot_pdf"; then
    printf 'failed:missing_selected_split_pdfs'
    return 0
  fi
  if command -v pdfunite >/dev/null 2>&1; then
    if [[ "$eot_enabled" == "true" ]]; then
      pdfunite "$teaching_pdf" "$lesson_pdf" "$eot_pdf" "$combined" >/dev/null 2>&1 || {
        printf 'failed:pdfunite_failed'
        return 0
      }
    else
      pdfunite "$teaching_pdf" "$lesson_pdf" "$combined" >/dev/null 2>&1 || {
        printf 'failed:pdfunite_failed'
        return 0
      }
    fi
    [[ -f "$combined" ]] && printf 'passed:pdfunite' || printf 'failed:combined_pdf_missing_after_merge'
    return 0
  fi
  if command -v qpdf >/dev/null 2>&1; then
    if [[ "$eot_enabled" == "true" ]]; then
      qpdf --empty --pages "$teaching_pdf" "$lesson_pdf" "$eot_pdf" -- "$combined" >/dev/null 2>&1 || {
        printf 'failed:qpdf_failed'
        return 0
      }
    else
      qpdf --empty --pages "$teaching_pdf" "$lesson_pdf" -- "$combined" >/dev/null 2>&1 || {
        printf 'failed:qpdf_failed'
        return 0
      }
    fi
    [[ -f "$combined" ]] && printf 'passed:qpdf' || printf 'failed:combined_pdf_missing_after_merge'
    return 0
  fi
  printf 'merge_unavailable:no_pdf_merge_tool'
}

write_manifest() {
  local package_md="$1" out_dir="$2" teaching_typ_status="$3" lesson_typ_status="$4"
  local manifest review_markers final_ready teaching_pdf_status lesson_pdf_status
  local eot_enabled eot_status eot_handoff eot_source eot_workdir eot_manifest
  local eot_typ eot_pdf eot_typ_status eot_pdf_status eot_review_markers eot_review_cleared
  local calculated_scores_verified table_artifacts_verified workbook_verified
  local combined_pdf combined_status combined_reason merge_result
  mkdir -p "$out_dir"
  manifest="${out_dir}/${MANIFEST_NAME}"
  review_markers="$(review_marker_state "$package_md")"
  teaching_pdf_status="$(status_for_file "${out_dir}/teaching-plan.pdf" "not_run")"
  lesson_pdf_status="$(status_for_file "${out_dir}/lesson-plans.pdf" "not_run")"
  eot_enabled="$(end_of_term_enabled "$package_md")"
  [[ "$eot_enabled" == "true" ]] || eot_enabled="false"
  eot_handoff="${out_dir}/end-of-term-full.md"
  eot_source="${out_dir}/end-of-term-source.json"
  eot_workdir="${out_dir}/end-of-term-output"
  eot_manifest="${eot_workdir}/manifest.json"
  eot_typ="${eot_workdir}/end-of-term-package.typ"
  eot_pdf="${eot_workdir}/end-of-term-package.pdf"
  eot_typ_status="$(status_for_file "$eot_typ" "not_run")"
  eot_pdf_status="$(status_for_file "$eot_pdf" "not_run")"
  eot_review_markers="$(end_of_term_review_markers "$eot_handoff")"
  eot_review_cleared="$(json_bool_from_manifest "$eot_manifest" "review_cleared" "false")"
  calculated_scores_verified="$(json_bool_from_manifest "$eot_manifest" "calculated_scores_verified" "false")"
  table_artifacts_verified="$(json_bool_from_manifest "$eot_manifest" "table_artifacts_verified" "false")"
  workbook_verified="$(json_bool_from_manifest "$eot_manifest" "workbook_verified" "false")"
  if [[ "$eot_enabled" != "true" ]]; then
    eot_status="disabled"
    eot_review_cleared="true"
  elif [[ "$eot_review_markers" != "[]" || "$eot_review_cleared" != "true" ]]; then
    eot_status="blocked_review"
  elif [[ -f "$eot_manifest" && -f "$eot_typ" && -f "$eot_pdf" ]]; then
    eot_status="passed"
  elif [[ -f "$eot_manifest" || -f "$eot_handoff" ]]; then
    eot_status="not_run"
  else
    eot_status="planned"
  fi
  combined_pdf="${out_dir}/teaching-design-package.pdf"
  merge_result="$(merge_combined_pdf "$out_dir" "$eot_enabled")"
  combined_status="${merge_result%%:*}"
  combined_reason="${merge_result#*:}"
  if [[ "$combined_status" == "$combined_reason" ]]; then
    combined_reason=""
  fi
  if [[ "$review_markers" == "[]" && "$teaching_pdf_status" == "passed" && "$lesson_pdf_status" == "passed" && "$combined_status" == "passed" && "$eot_status" != "blocked_review" && "$eot_status" != "planned" && "$eot_status" != "not_run" ]]; then
    final_ready="true"
  else
    final_ready="false"
  fi
  {
    printf '{\n'
    printf '  "package_markdown": "%s",\n' "$(json_escape "$package_md")"
    printf '  "split_outputs": {\n'
    printf '    "teaching_plan_typ": {\n'
    printf '      "path": "%s",\n' "$(json_escape "${out_dir}/teaching-plan.typ")"
    printf '      "status": "%s"\n' "$teaching_typ_status"
    printf '    },\n'
    printf '    "lesson_plans_typ": {\n'
    printf '      "path": "%s",\n' "$(json_escape "${out_dir}/lesson-plans.typ")"
    printf '      "status": "%s"\n' "$lesson_typ_status"
    printf '    },\n'
    printf '    "teaching_plan_pdf": {\n'
    printf '      "path": "%s",\n' "$(json_escape "${out_dir}/teaching-plan.pdf")"
    printf '      "status": "%s"\n' "$teaching_pdf_status"
    printf '    },\n'
    printf '    "lesson_plans_pdf": {\n'
    printf '      "path": "%s",\n' "$(json_escape "${out_dir}/lesson-plans.pdf")"
    printf '      "status": "%s"\n' "$lesson_pdf_status"
    printf '    },\n'
    printf '    "end_of_term_typ": {\n'
    printf '      "path": "%s",\n' "$(json_escape "$eot_typ")"
    printf '      "status": "%s"\n' "$eot_typ_status"
    printf '    },\n'
    printf '    "end_of_term_pdf": {\n'
    printf '      "path": "%s",\n' "$(json_escape "$eot_pdf")"
    printf '      "status": "%s"\n' "$eot_pdf_status"
    printf '    }\n'
    printf '  },\n'
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
    printf '  "end_of_term": {\n'
    printf '    "enabled": %s,\n' "$eot_enabled"
    printf '    "status": "%s",\n' "$eot_status"
    printf '    "handoff": "%s",\n' "$(json_escape "$eot_handoff")"
    printf '    "source_data": "%s",\n' "$(json_escape "$eot_source")"
    printf '    "workdir": "%s",\n' "$(json_escape "$eot_workdir")"
    printf '    "manifest": "%s",\n' "$(json_escape "$eot_manifest")"
    printf '    "typ": "%s",\n' "$(json_escape "$eot_typ")"
    printf '    "pdf": "%s",\n' "$(json_escape "$eot_pdf")"
    printf '    "review_cleared": %s,\n' "$eot_review_cleared"
    printf '    "review_markers": %s,\n' "$eot_review_markers"
    printf '    "calculated_scores_verified": %s,\n' "$calculated_scores_verified"
    printf '    "table_artifacts_verified": %s,\n' "$table_artifacts_verified"
    printf '    "workbook_verified": %s,\n' "$workbook_verified"
    printf '    "tables": {\n'
    printf '      "score_data": "%s",\n' "$(json_escape "${eot_workdir}/tables/score-data.json")"
    printf '      "calculated_score_data": "%s",\n' "$(json_escape "${eot_workdir}/tables/calculated-score-data.json")"
    printf '      "score_summary": "%s",\n' "$(json_escape "${eot_workdir}/tables/score-summary.json")"
    printf '      "highlight_evidence": "%s",\n' "$(json_escape "${eot_workdir}/tables/highlight-evidence.json")"
    printf '      "score_list_md": "%s"\n' "$(json_escape "${eot_workdir}/tables/score-list.md")"
    printf '    },\n'
    printf '    "workbooks": {\n'
    printf '      "score_list_xlsx": "%s",\n' "$(json_escape "${eot_workdir}/tables/score-list.xlsx")"
    printf '      "scorebook_xlsx": "%s"\n' "$(json_escape "${eot_workdir}/tables/scorebook.xlsx")"
    printf '    }\n'
    printf '  },\n'
    printf '  "combined_output": {\n'
    printf '    "path": "%s",\n' "$(json_escape "$combined_pdf")"
    printf '    "status": "%s",\n' "$combined_status"
    printf '    "reason": "%s"\n' "$(json_escape "$combined_reason")"
    printf '  },\n'
    printf '  "review_markers": %s,\n' "$review_markers"
    printf '  "final_ready": %s\n' "$final_ready"
    printf '}\n'
  } > "$manifest"
  printf '%s\n' "$manifest"
}

write_jihua_scaffold() {
  local package_md="$1" out="$2"
  frontmatter_value "$package_md" course_name >/dev/null
  cp "${SKILL_DIR}/../jiaoan-jihua/templates/jiaoan-jihua-full.md" "$out"
}

shicao_schedule_evidence_rows() {
  local package_md="$1"
  awk '
    function trim(value) {
      sub(/^[[:space:]]+/, "", value)
      sub(/[[:space:]]+$/, "", value)
      return value
    }
    function unquote_source(value) {
      value = trim(value)
      gsub(/`/, "", value)
      return value
    }
    /^## 调度证据$/ { in_schedule=1; next }
    in_schedule && /^## / { exit }
    !in_schedule { next }
    /^\|/ {
      line=$0
      sub(/^\|/, "", line)
      sub(/\|[[:space:]]*$/, "", line)
      cols=split(line, cells, "[|]")
      for (i=1; i<=cols; i++) cells[i]=trim(cells[i])
      if (source_col == 0 && cells[1] == "Source") {
        source_col=1
        if (cells[4] == "起止日期") date_col=4
        next
      }
      if (source_col == 0 || date_col == 0) next
      if (cells[source_col] ~ /^-+$/) next
      source=unquote_source(cells[source_col])
      range=trim(cells[date_col])
      if (source == "") next
      if (range ~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] - [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$/) {
        print source "\t" range
      }
    }
  ' "$package_md"
}

shicao_declared_task_prefix() {
  local package_md="$1"
  awk '
    /^## 实操教案$/ { in_shicao=1; next }
    in_shicao && /^## / { exit }
    !in_shicao { next }
    /起止日期：由[[:space:]]*`task:[0-9][0-9]*\/\*`[[:space:]]*调度证据推导/ {
      line=$0
      if (match(line, /`task:[0-9][0-9]*\/\*`/)) {
        source=substr(line, RSTART + 1, RLENGTH - 2)
        sub(/\*$/, "", source)
        print source
      }
      exit
    }
  ' "$package_md"
}

aggregate_date_ranges_for_prefix() {
  local package_md="$1" prefix="$2"
  shicao_schedule_evidence_rows "$package_md" | awk -F '\t' -v prefix="$prefix" '
    index($1, prefix) == 1 {
      start=substr($2, 1, 10)
      end=substr($2, 14, 10)
      if (min == "" || start < min) min=start
      if (max == "" || end > max) max=end
    }
    END {
      if (min != "" && max != "") print min " - " max
    }
  '
}

shicao_lesson_sources() {
  local package_md="$1"
  awk '
    /^## 实操教案$/ { in_shicao=1; next }
    in_shicao && /^## / { exit }
    !in_shicao { next }
    {
      line=$0
      while (match(line, /`lesson:[^`]+`/)) {
        source=substr(line, RSTART + 1, RLENGTH - 2)
        if (!seen[source]++) print source
        line=substr(line, RSTART + RLENGTH)
      }
    }
  ' "$package_md"
}

aggregate_date_ranges_for_sources() {
  local package_md="$1"
  local sources=("$@")
  shicao_schedule_evidence_rows "$package_md" | awk -F '\t' -v source_list="$(printf '%s\n' "${sources[@]:1}")" '
    BEGIN {
      split(source_list, source_items, "\n")
      for (i in source_items) {
        if (source_items[i] != "") wanted[source_items[i]]=1
      }
    }
    wanted[$1] {
      start=substr($2, 1, 10)
      end=substr($2, 14, 10)
      if (min == "" || start < min) min=start
      if (max == "" || end > max) max=end
    }
    END {
      if (min != "" && max != "") print min " - " max
    }
  '
}

shicao_backfill_date_range() {
  local package_md="$1" task_prefix date_range
  local -a lesson_sources
  task_prefix="$(shicao_declared_task_prefix "$package_md")"
  if [[ -n "$task_prefix" ]]; then
    aggregate_date_ranges_for_prefix "$package_md" "$task_prefix"
    return 0
  fi
  mapfile -t lesson_sources < <(shicao_lesson_sources "$package_md")
  if [[ "${#lesson_sources[@]}" -gt 0 ]]; then
    date_range="$(aggregate_date_ranges_for_sources "$package_md" "${lesson_sources[@]}")"
    [[ -n "$date_range" ]] && printf '%s\n' "$date_range"
  fi
}

backfill_shicao_blank_dates() {
  local out="$1" date_range="$2" tmp
  [[ -n "$date_range" ]] || return 0
  tmp="${out}.tmp.$$"
  awk -v date_range="$date_range" '
    /^起止日期：[[:space:]]*$/ {
      print "起止日期：" date_range
      next
    }
    { print }
  ' "$out" > "$tmp"
  mv "$tmp" "$out"
}

write_shicao_scaffold() {
  local package_md="$1" out="$2" date_range
  frontmatter_value "$package_md" course_name >/dev/null
  cp "${SKILL_DIR}/../jiaoan-shicao/templates/jiaoan-shicao-full.md" "$out"
  if [[ "$(review_marker_state "$package_md")" != "[]" ]]; then
    return 0
  fi
  date_range="$(shicao_backfill_date_range "$package_md")"
  backfill_shicao_blank_dates "$out" "$date_range"
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

cmd_plan_end_of_term() {
  parse_io_args "$@"
  [[ -n "$INPUT" ]] || die "plan-end-of-term requires --input"
  [[ -n "$OUT_DIR" ]] || die "plan-end-of-term requires --out-dir"
  validate_package "$INPUT"
  mkdir -p "$OUT_DIR"
  local enabled source_json handoff
  enabled="$(end_of_term_enabled "$INPUT")"
  [[ "$enabled" == "true" ]] || {
    write_manifest "$INPUT" "$OUT_DIR" "planned" "planned" >/dev/null
    return 0
  }
  need_file "$END_OF_TERM_SCRIPT"
  source_json="${OUT_DIR}/end-of-term-source.json"
  handoff="${OUT_DIR}/end-of-term-full.md"
  [[ -f "$source_json" ]] || die "enabled end-of-term module requires source data: $source_json"
  "$END_OF_TERM_SCRIPT" markdown --input "$source_json" --output "$handoff"
  "$END_OF_TERM_SCRIPT" validate --input "$handoff" >/dev/null 2>&1 || true
  write_manifest "$INPUT" "$OUT_DIR" "planned" "planned" >/dev/null
}

cmd_render_end_of_term() {
  parse_io_args "$@"
  [[ -n "$INPUT" ]] || die "render-end-of-term requires --input"
  [[ -n "$OUT_DIR" ]] || die "render-end-of-term requires --out-dir"
  validate_package "$INPUT"
  mkdir -p "$OUT_DIR"
  local enabled handoff workdir
  enabled="$(end_of_term_enabled "$INPUT")"
  [[ "$enabled" == "true" ]] || {
    write_manifest "$INPUT" "$OUT_DIR" "planned" "planned" >/dev/null
    return 0
  }
  need_file "$END_OF_TERM_SCRIPT"
  handoff="${OUT_DIR}/end-of-term-full.md"
  workdir="${OUT_DIR}/end-of-term-output"
  [[ -f "$handoff" ]] || cmd_plan_end_of_term --input "$INPUT" --out-dir "$OUT_DIR"
  mkdir -p "$workdir"
  "$END_OF_TERM_SCRIPT" render --input "$handoff" --workdir "$workdir" --pdf
  "$END_OF_TERM_SCRIPT" verify --workdir "$workdir"
  "$END_OF_TERM_SCRIPT" manifest --workdir "$workdir" >/dev/null
  write_manifest "$INPUT" "$OUT_DIR" "planned" "planned" >/dev/null
}

cmd_render_package() {
  parse_io_args "$@"
  [[ -n "$INPUT" ]] || die "render-package requires --input"
  [[ -n "$OUT_DIR" ]] || die "render-package requires --out-dir"
  validate_package "$INPUT"
  mkdir -p "$OUT_DIR"
  local teaching_status="planned" lesson_status="planned"
  [[ -f "${OUT_DIR}/teaching-plan.typ" ]] && teaching_status="passed"
  [[ -f "${OUT_DIR}/lesson-plans.typ" ]] && lesson_status="passed"
  write_manifest "$INPUT" "$OUT_DIR" "$teaching_status" "$lesson_status" >/dev/null
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
  printf 'teaching-design-package: Markdown-first orchestration over jiaoan-jihua, jiaoan-shicao, and optional end-of-term-teaching-materials.\n'
  printf 'Package checkpoint: templates/teaching-design-package-full.md\n'
  printf 'Reference: references/format-and-orchestration.md\n'
  printf 'Optional module: end-of-term-full.md -> end-of-term-package.pdf via end-of-term-teaching-materials.\n'
  printf 'Combined output: teaching-design-package.pdf is passed only when the actual file exists after merge/compile.\n'
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
    plan-end-of-term) cmd_plan_end_of_term "$@" ;;
    render-end-of-term) cmd_render_end_of_term "$@" ;;
    render-package) cmd_render_package "$@" ;;
    manifest) cmd_manifest "$@" ;;
    info) cmd_info "$@" ;;
    version) cmd_version "$@" ;;
    -h|--help|help) usage ;;
    *) die "unknown command: $command" ;;
  esac
}

main "$@"
