#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$SCRIPT_DIR" == "${BASH_SOURCE[0]}" ]]; then
  SCRIPT_DIR="."
fi
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEMPLATE_MD="${SKILL_DIR}/templates/teaching-design-package-full.md"
CALENDAR_JSON="${SKILL_DIR}/references/calendar.json"
STATUS_NAME="status.json"
DEFAULT_DAILY_HOURS=8

usage() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'USAGE'
Usage:
  teaching-design-package.sh example --output <teaching-design-package-full.md>
  teaching-design-package.sh model --input <package.md> [--out-dir <dir>]
  teaching-design-package.sh render-package --input <package.md> --out-dir <dir>
  teaching-design-package.sh render-package --pdf --input <package.md> --out-dir <dir>
  teaching-design-package.sh manifest --input <package.md> --out-dir <dir>
  teaching-design-package.sh plan-split --input <package.md> --out-dir <dir>
  teaching-design-package.sh render-split --input <package.md> --out-dir <dir>
  teaching-design-package.sh info
  teaching-design-package.sh version

The normal path is unified Markdown -> package data model -> clean 1+1+3 delivery.
Diagnostics, status, stderr logs, split Typst files, and failure evidence stay under .teaching-design-package/.
render-package --pdf exits successfully only when all three PDF files exist and are non-empty.
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
  RENDER_PDF=false
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --pdf)
        RENDER_PDF=true
        shift
        ;;
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

json_escape() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  value="${value//$'\n'/\\n}"
  printf '%s' "$value"
}

package_model_json() {
  local input="$1"
  need_file "$input"
  need_file "$CALENDAR_JSON"
  node "${SCRIPT_DIR}/package-model.js" "$input" "$DEFAULT_DAILY_HOURS" "$CALENDAR_JSON"
}

cmd_example() {
  parse_io_args "$@"
  [[ -n "$OUTPUT" ]] || die "example requires --output"
  need_file "$TEMPLATE_MD"
  ensure_parent_dir "$OUTPUT"
  cp "$TEMPLATE_MD" "$OUTPUT"
}

write_failure_diagnostics() {
  local input="$1" out_dir="$2" stderr_path="$3"
  local diagnostics_path status_path
  diagnostics_path="${out_dir}/.teaching-design-package/diagnostics.json"
  status_path="${out_dir}/.teaching-design-package/${STATUS_NAME}"
  mkdir -p "${out_dir}/.teaching-design-package/failure-diagnostics"
  node - "$input" "$stderr_path" "$diagnostics_path" "$status_path" <<'NODE'
const fs = require('fs');
const input = process.argv[2];
const stderrPath = process.argv[3];
const diagnosticsPath = process.argv[4];
const statusPath = process.argv[5];
const stderr = fs.existsSync(stderrPath) ? fs.readFileSync(stderrPath, 'utf8') : '';
const diagnosticLine = stderr.split(/\n/).find((line) => line.startsWith('TDPKG_DIAGNOSTIC_JSON='));
let error = { code: 'unknown_failure', message: stderr.trim() || 'unknown failure' };
if (diagnosticLine) {
  try {
    error = JSON.parse(diagnosticLine.slice('TDPKG_DIAGNOSTIC_JSON='.length));
  } catch (_error) {
    error = { code: 'invalid_diagnostic_payload', message: stderr.trim() };
  }
}
const diagnostics = {
  status: 'failed',
  source_markdown: input,
  errors: [error],
  stderr_log: stderrPath,
  failure_classes: [
    'missing_section',
    'invalid_frontmatter',
    'forbidden_derived_frontmatter',
    'malformed_schedule_row',
    'missing_module_source',
    'missing_calendar_resource',
    'invalid_calendar_json',
    'first_day_not_found',
    'calendar_exhausted',
    'non_positive_hours',
    'teaching_design_hours_inconsistent',
    'hidden_artifact_write_failure',
    'public_root_leakage',
  ],
};
fs.writeFileSync(diagnosticsPath, JSON.stringify(diagnostics, null, 2));
fs.writeFileSync(statusPath, JSON.stringify({
  generated_from_markdown: false,
  status: 'failed',
  source_markdown: input,
  diagnostics: diagnosticsPath,
  errors: [error],
}, null, 2));
fs.copyFileSync(diagnosticsPath, diagnosticsPath.replace('/diagnostics.json', '/failure-diagnostics/diagnostics.json'));
fs.copyFileSync(statusPath, statusPath.replace('/status.json', '/failure-diagnostics/status.json'));
NODE
}

write_model_file() {
  local input="$1" out_dir="$2" model_path
  model_path="${out_dir}/.teaching-design-package/model.json"
  mkdir -p "${out_dir}/.teaching-design-package/work" "${out_dir}/.teaching-design-package/debug" "${out_dir}/.teaching-design-package/failure-diagnostics"
  if ! package_model_json "$input" > "$model_path" 2>"${out_dir}/.teaching-design-package/debug/model.stderr.log"; then
    write_failure_diagnostics "$input" "$out_dir" "${out_dir}/.teaching-design-package/debug/model.stderr.log"
    cat "${out_dir}/.teaching-design-package/debug/model.stderr.log" >&2
    return 1
  fi
  printf '%s\n' "$model_path"
}

write_unified_typst() {
  local model_path="$1" typ_path="$2"
  node - "$model_path" "$typ_path" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const typPath = process.argv[3];

function esc(value) {
  return String(value ?? '').replace(/\\/g, '\\\\').replace(/"/g, '\\"');
}

function plain(value) {
  return String(value ?? '').replace(/[\\#*_`<>\[\]]/g, ' ');
}

const lines = [
  '// Generated by teaching-design-package.sh render-package.',
  '// package_owned_model: true',
  `// source_markdown: ${model.source_markdown}`,
  `// total_hours: ${model.derived.total_hours_label}`,
  `// term: ${model.derived.term_label}`,
  '',
  '#set document(',
  `  title: "${esc(model.metadata.course_name)} 教学设计整包",`,
  `  author: "${esc(model.metadata.teacher_name)}",`,
  ')',
  '',
  '= 课程教学设计整包',
  '',
  `课程名称：${plain(model.metadata.course_name)}\\`,
  `专业名称：${plain(model.metadata.major_name)}\\`,
  `班级：${plain(model.metadata.class_name)}\\`,
  `教师：${plain(model.metadata.teacher_name)}\\`,
  `学期：${plain(model.derived.term_label)}\\`,
  `总课时：${plain(model.derived.total_hours_label)}\\`,
  `起止日期：${plain(model.derived.date_range)}`,
  '',
  '== 授课进度计划',
  '',
];

for (const [taskIndex, task] of model.schedule.tasks.entries()) {
  lines.push(`=== 学习任务${taskIndex + 1}：${plain(task.title)}`);
  lines.push('');
  lines.push(`课时：${task.total_hours}H\\`);
  lines.push(`起止日期：${plain(task.date_range)}`);
  lines.push('');
  for (const stage of task.stages) {
    lines.push(`==== ${plain(stage.title)}`);
    lines.push('');
    for (const row of stage.rows) {
      const evidence = row.consumption.map((item) => `${item.date} ${item.weekday} ${item.hours}H`).join('；');
      lines.push(`- ${plain(row.title)}：${row.hours}H（${plain(evidence)}）`);
    }
    lines.push('');
  }
}

lines.push('== 教学设计方案');
lines.push('');
for (const line of model.teaching_design.markdown.split(/\n/)) {
  if (line.startsWith('## ')) lines.push(`=== ${plain(line.slice(3))}`);
  else if (line.startsWith('### ')) lines.push(`==== ${plain(line.slice(4))}`);
  else if (line.startsWith('#### ')) lines.push(`===== ${plain(line.slice(5))}`);
  else if (line.trim() === '') lines.push('');
  else lines.push(plain(line));
}

fs.writeFileSync(typPath, lines.join('\n'));
NODE
}

write_module_markdown_files() {
  local model_path="$1" out_dir="$2"
  node - "$model_path" "$out_dir" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outDir = process.argv[3];

function yamlValue(value) {
  if (typeof value === 'number') return String(value);
  return `"${String(value ?? '').replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`;
}

function frontmatterYaml(frontmatter) {
  return [
    '---',
    ...Object.entries(frontmatter).map(([key, value]) => `${key}: ${yamlValue(value)}`),
    '---',
    '',
  ].join('\n');
}

function moduleById(id) {
  const found = model.modules.items.find((item) => item.id === id);
  if (!found) throw new Error(`missing module in model: ${id}`);
  return found;
}

const plan = moduleById('teaching-plan');
const design = moduleById('teaching-design');
const planLines = [
  frontmatterYaml(plan.frontmatter),
  '# 授课进度计划',
  '',
];
for (const task of model.schedule.tasks) {
  planLines.push(`## ${task.title}`, '');
  for (const stage of task.stages) {
    planLines.push(`### ${stage.title}`, '');
    for (const row of stage.rows) {
      planLines.push(`${row.title}-${row.assigned_hours}`);
    }
    planLines.push('');
  }
}

const designLines = [
  frontmatterYaml(design.frontmatter),
  '# 教学设计方案',
  '',
  model.teaching_design.markdown,
  '',
];

fs.writeFileSync(`${outDir}/${plan.work_markdown}`, planLines.join('\n'));
fs.writeFileSync(`${outDir}/${design.work_markdown}`, designLines.join('\n'));
NODE
}

write_placeholder_pdf_typst() {
  local model_path="$1" typ_path="$2" title="$3"
  node - "$model_path" "$typ_path" "$title" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const typPath = process.argv[3];
const title = process.argv[4];
const esc = (value) => String(value ?? '').replace(/\\/g, '\\\\').replace(/"/g, '\\"');
const lines = [
  '// Package-owned Phase 33 module Typst intermediate.',
  '// Pre-formal surface only; formal renderer migration is Phase 34/35 scope.',
  '// This file is generated from the shared package model.',
  `#set document(title: "${esc(title)}", author: "${esc(model.metadata.teacher_name)}")`,
  '',
  `= ${title}`,
  '',
  `课程：${model.metadata.course_name}`,
  '',
  `总课时：${model.derived.total_hours_label}`,
  '',
  `学期：${model.derived.term_label}`,
  '',
  'This file is generated from the unified package model.',
  '',
];
fs.writeFileSync(typPath, lines.join('\n'));
NODE
}

write_teaching_plan_typst() {
  local model_path="$1" typ_path="$2"
  node "${SCRIPT_DIR}/teaching-plan-renderer.js" "$model_path" "$typ_path"
}

compile_pdf() {
  local typ="$1" pdf="$2" log="$3"
  rm -f "$pdf" "$log"
  if ! command -v typst >/dev/null 2>&1; then
    return 20
  fi
  typst compile "$typ" "$pdf" 2>"$log"
}

write_status() {
  local model_path="$1" out_dir="$2" pdf_requested="$3" full_status="$4" plan_status="$5" design_status="$6"
  local status_path="${out_dir}/.teaching-design-package/${STATUS_NAME}"
  mkdir -p "${out_dir}/.teaching-design-package"
  node - "$model_path" "$status_path" "$out_dir" "$pdf_requested" "$full_status" "$plan_status" "$design_status" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const statusPath = process.argv[3];
const outDir = process.argv[4];
const pdfRequested = process.argv[5] === 'true';
const [fullStatus, planStatus, designStatus] = process.argv.slice(6, 9);
const publicOutputs = {
  unified_markdown: `${outDir}/teaching-design-package-full.md`,
  unified_typst: `${outDir}/teaching-design-package.typ`,
  full_package_pdf: `${outDir}/teaching-design-package.pdf`,
  teaching_plan_pdf: `${outDir}/teaching-plan.pdf`,
  teaching_design_pdf: `${outDir}/teaching-design.pdf`,
};
const status = {
  generated_from_markdown: true,
  package_owned_model: true,
  phase33_module_registry: true,
  source_markdown: model.source_markdown,
  hidden_model: `${outDir}/.teaching-design-package/model.json`,
  hidden_status: statusPath,
  hidden_work_dir: `${outDir}/.teaching-design-package/work`,
  hidden_debug_dir: `${outDir}/.teaching-design-package/debug`,
  hidden_failure_diagnostics_dir: `${outDir}/.teaching-design-package/failure-diagnostics`,
  derived: model.derived,
  scheduling: {
    calendar: model.scheduling.calendar,
    first_teaching_day: model.scheduling.first_teaching_day,
    daily_hours: model.scheduling.daily_hours,
    daily_hours_source: model.scheduling.daily_hours_source,
    term_week_start: model.scheduling.term_week_start,
    consumed_calendar_range: model.scheduling.consumed_calendar_range,
    total_hours: model.scheduling.total_hours,
    use_time: model.scheduling.course.use_time,
  },
  modules: {
    registry: model.modules.registry,
    generated_frontmatter: Object.fromEntries(model.modules.items.map((item) => [item.id, item.frontmatter])),
  },
  validation: model.validation,
  teaching_plan_formal_renderer: {
    status: 'passed',
    renderer: 'package-owned teaching-plan-renderer.js',
    legacy_surface: 'jiaoan-jihua official five-column table',
    source: 'shared_scheduling_model',
    total_hours_source: model.validation.total_hours_source,
    hidden_typst: `${outDir}/.teaching-design-package/work/teaching-plan.typ`,
    public_pdf: publicOutputs.teaching_plan_pdf,
    pdf_compile_status: planStatus,
  },
  public_outputs: publicOutputs,
  pdf_requested: pdfRequested,
  pdf_status: {
    full_package_pdf: fullStatus,
    teaching_plan_pdf: planStatus,
    teaching_design_pdf: designStatus,
  },
  review_markers: model.review_markers,
  final_ready: pdfRequested && fullStatus === 'passed' && planStatus === 'passed' && designStatus === 'passed' && model.review_markers.length === 0 && model.validation.errors.length === 0,
  notes: [
    'Default successful delivery root is exactly one unified Markdown, one unified Typst, and three PDFs.',
    'Diagnostics, status, stderr logs, split Typst, model JSON, and failure evidence stay under .teaching-design-package/.',
  ],
};
fs.writeFileSync(statusPath, JSON.stringify(status, null, 2));
NODE
}

write_diagnostics() {
  local model_path="$1" out_dir="$2" diagnostics_path
  diagnostics_path="${out_dir}/.teaching-design-package/diagnostics.json"
  mkdir -p "${out_dir}/.teaching-design-package"
  node - "$model_path" "$diagnostics_path" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const diagnosticsPath = process.argv[3];
const diagnostics = {
  status: 'passed',
  package_owned_model: true,
  phase33_module_registry: true,
  source_markdown: model.source_markdown,
  calendar: model.scheduling.calendar,
  first_teaching_day: model.scheduling.first_teaching_day,
  daily_hours: model.scheduling.daily_hours,
  daily_hours_source: model.scheduling.daily_hours_source,
  term_week_start: model.scheduling.term_week_start,
  consumed_calendar_range: model.scheduling.consumed_calendar_range,
  row_consumption_summary: model.scheduling.row_consumption_summary,
  task_totals: model.scheduling.tasks,
  total_hours: model.scheduling.total_hours,
  use_time: model.scheduling.course.use_time,
  strict_sum_evidence: model.validation.strict_sum_evidence,
  teaching_plan_formal_renderer: {
    status: 'passed',
    renderer: 'package-owned teaching-plan-renderer.js',
    legacy_surface: 'jiaoan-jihua official five-column table',
    scheduling_source: 'shared_scheduling_model',
    hidden_typst: model.modules.items.find((item) => item.id === 'teaching-plan').work_typst,
  },
  module_registry: model.modules.registry,
  generated_module_frontmatter: Object.fromEntries(model.modules.items.map((item) => [item.id, item.frontmatter])),
  calendar_policy: model.derived.calendar_policy,
  total_hours_source: model.validation.total_hours_source,
  teaching_design_activity_hours_source: model.validation.teaching_design_activity_hours_source,
  hours_cross_check: model.validation.hours_cross_check,
  review_markers_count: model.review_markers.length,
  failure_classes: [
    'missing_section',
    'invalid_frontmatter',
    'forbidden_derived_frontmatter',
    'malformed_schedule_row',
    'missing_module_source',
    'missing_calendar_resource',
    'invalid_calendar_json',
    'first_day_not_found',
    'calendar_exhausted',
    'non_positive_hours',
    'teaching_design_hours_inconsistent',
    'hidden_artifact_write_failure',
    'public_root_leakage',
  ],
};
fs.writeFileSync(diagnosticsPath, JSON.stringify(diagnostics, null, 2));
NODE
}

assert_no_public_leakage() {
  local out_dir="$1" leak
  leak="$(find "$out_dir" -maxdepth 1 -type f -print | rg 'teaching-plan[.]md|teaching-design[.]md|teaching-plan[.]typ|teaching-design[.]typ|calendar[.]json|model[.]json|status[.]json|diagnostics[.]json|log' || true)"
  if [[ -n "$leak" ]]; then
    printf 'teaching-design-package.sh: public_root_leakage: %s\n' "$leak" >&2
    return 1
  fi
}

pdf_nonempty() {
  [[ -s "$1" ]]
}

cmd_model() {
  parse_io_args "$@"
  [[ -n "$INPUT" ]] || die "model requires --input"
  if [[ -n "$OUT_DIR" ]]; then
    mkdir -p "$OUT_DIR"
    write_model_file "$INPUT" "$OUT_DIR" >/dev/null
  else
    package_model_json "$INPUT"
  fi
}

cmd_render_package() {
  parse_io_args "$@"
  [[ -n "$INPUT" ]] || die "render-package requires --input"
  [[ -n "$OUT_DIR" ]] || die "render-package requires --out-dir"
  need_file "$INPUT"
  mkdir -p "$OUT_DIR"
  local model_path full_status="not_run" plan_status="not_run" design_status="not_run"
  cp "$INPUT" "${OUT_DIR}/teaching-design-package-full.md"
  model_path="$(write_model_file "$INPUT" "$OUT_DIR")"
  write_unified_typst "$model_path" "${OUT_DIR}/teaching-design-package.typ"
  write_module_markdown_files "$model_path" "$OUT_DIR"
  write_teaching_plan_typst "$model_path" "${OUT_DIR}/.teaching-design-package/work/teaching-plan.typ"
  write_placeholder_pdf_typst "$model_path" "${OUT_DIR}/.teaching-design-package/work/teaching-design.typ" "教学设计方案"
  if [[ "$RENDER_PDF" == true ]]; then
    if compile_pdf "${OUT_DIR}/teaching-design-package.typ" "${OUT_DIR}/teaching-design-package.pdf" "${OUT_DIR}/.teaching-design-package/debug/full-pdf.stderr.log" && pdf_nonempty "${OUT_DIR}/teaching-design-package.pdf"; then
      full_status="passed"
    else
      full_status="missing_compiler_or_failed"
    fi
    if compile_pdf "${OUT_DIR}/.teaching-design-package/work/teaching-plan.typ" "${OUT_DIR}/teaching-plan.pdf" "${OUT_DIR}/.teaching-design-package/debug/plan-pdf.stderr.log" && pdf_nonempty "${OUT_DIR}/teaching-plan.pdf"; then
      plan_status="passed"
    else
      plan_status="missing_compiler_or_failed"
    fi
    if compile_pdf "${OUT_DIR}/.teaching-design-package/work/teaching-design.typ" "${OUT_DIR}/teaching-design.pdf" "${OUT_DIR}/.teaching-design-package/debug/design-pdf.stderr.log" && pdf_nonempty "${OUT_DIR}/teaching-design.pdf"; then
      design_status="passed"
    else
      design_status="missing_compiler_or_failed"
    fi
  fi
  write_status "$model_path" "$OUT_DIR" "$RENDER_PDF" "$full_status" "$plan_status" "$design_status"
  write_diagnostics "$model_path" "$OUT_DIR"
  if ! assert_no_public_leakage "$OUT_DIR"; then
    write_failure_diagnostics "$INPUT" "$OUT_DIR" "${OUT_DIR}/.teaching-design-package/debug/model.stderr.log"
    die "public root leaked hidden package artifacts; diagnostics are under ${OUT_DIR}/.teaching-design-package/"
  fi
  if [[ "$RENDER_PDF" == true ]]; then
    if [[ "$full_status" != "passed" || "$plan_status" != "passed" || "$design_status" != "passed" ]]; then
      cp "${OUT_DIR}/.teaching-design-package/${STATUS_NAME}" "${OUT_DIR}/.teaching-design-package/failure-diagnostics/${STATUS_NAME}"
      die "render-package --pdf did not produce all three non-empty PDF deliverables; diagnostics are under ${OUT_DIR}/.teaching-design-package/"
    fi
  fi
}

cmd_manifest() {
  parse_io_args "$@"
  [[ -n "$INPUT" ]] || die "manifest requires --input"
  [[ -n "$OUT_DIR" ]] || die "manifest requires --out-dir"
  mkdir -p "$OUT_DIR"
  local model_path
  model_path="$(write_model_file "$INPUT" "$OUT_DIR")"
  write_status "$model_path" "$OUT_DIR" "false" "not_run" "not_run" "not_run"
  printf '%s/.teaching-design-package/%s\n' "$OUT_DIR" "$STATUS_NAME"
}

cmd_compat_render() {
  parse_io_args "$@"
  [[ -n "$INPUT" ]] || die "command requires --input"
  [[ -n "$OUT_DIR" ]] || die "command requires --out-dir"
  cmd_render_package --input "$INPUT" --out-dir "$OUT_DIR"
}

cmd_info() {
  printf 'teaching-design-package: standalone unified Markdown to package-owned module registry and shared scheduling model.\n'
  printf 'Package checkpoint: templates/teaching-design-package-full.md\n'
  printf 'Reference: references/format-and-orchestration.md\n'
  printf 'Calendar: references/calendar.json\n'
  printf 'Normal rendering does not require repository sibling skill folders.\n'
}

cmd_version() {
  printf 'teaching-design-package.sh 0.4.0-phase33\n'
}

main() {
  local command="${1:-}"
  [[ -n "$command" ]] || { usage; exit 1; }
  shift || true
  case "$command" in
    example) cmd_example "$@" ;;
    model) cmd_model "$@" ;;
    render-package) cmd_render_package "$@" ;;
    manifest) cmd_manifest "$@" ;;
    plan-split|render-split) cmd_compat_render "$@" ;;
    plan-end-of-term|render-end-of-term) die "optional external modules are outside the Phase 30 normal path" ;;
    info) cmd_info ;;
    version) cmd_version ;;
    -h|--help|help) usage ;;
    *) die "unknown command: $command" ;;
  esac
}

main "$@"
