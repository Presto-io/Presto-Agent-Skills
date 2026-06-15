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

The normal path is unified Markdown -> package data model -> course-prefixed 1+1+N delivery.
Diagnostics, status, stderr logs, split Typst files, and failure evidence stay under .teaching-design-package/.
render-package --pdf exits successfully only when all registered module PDFs and the merged package PDF exist and are non-empty.
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
  calendar: error.calendar || null,
  model_version: error.model_version || null,
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
    'teaching_design_task_count_mismatch',
    'teaching_design_stage_count_mismatch',
    'teaching_design_activity_count_mismatch',
    'teaching_design_task_title_mismatch',
    'teaching_design_stage_title_mismatch',
    'teaching_design_activity_title_mismatch',
    'teaching_design_task_hours_mismatch',
    'teaching_design_activity_hours_mismatch',
    'teaching_design_task_date_range_mismatch',
    'missing_teaching_design_analysis_block',
    'missing_teaching_design_activity_block',
    'missing_teaching_design_evaluation_block',
    'teaching_design_formal_render_failed',
    'teaching_design_pdf_compile_failed',
    'hidden_artifact_write_failure',
    'public_root_leakage',
    'invalid_course_name_for_filename',
    'module_pdf_missing',
    'module_pdf_empty',
    'module_status_failed',
    'merge_input_order_mismatch',
    'merge_tool_unavailable',
    'merge_tool_failed',
    'merged_pdf_empty',
    'standalone_copy_failed',
  ],
};
fs.writeFileSync(diagnosticsPath, JSON.stringify(diagnostics, null, 2));
let priorStatus = {};
if (fs.existsSync(statusPath)) {
  try {
    priorStatus = JSON.parse(fs.readFileSync(statusPath, 'utf8'));
  } catch (_error) {
    priorStatus = {};
  }
}
fs.writeFileSync(statusPath, JSON.stringify({
  ...priorStatus,
  generated_from_markdown: false,
  status: 'failed',
  final_ready: false,
  source_markdown: input,
  diagnostics: diagnosticsPath,
  errors: [error],
}, null, 2));
fs.copyFileSync(diagnosticsPath, diagnosticsPath.replace('/diagnostics.json', '/failure-diagnostics/diagnostics.json'));
fs.copyFileSync(statusPath, statusPath.replace('/status.json', '/failure-diagnostics/status.json'));
const safeCode = String(error.code || 'unknown_failure').replace(/[^A-Za-z0-9_.-]/g, '_');
fs.copyFileSync(diagnosticsPath, diagnosticsPath.replace('/diagnostics.json', `/failure-diagnostics/diagnostics-${safeCode}.json`));
fs.copyFileSync(statusPath, statusPath.replace('/status.json', `/failure-diagnostics/status-${safeCode}.json`));
NODE
}

cleanup_public_root() {
  local out_dir="$1"
  [[ -d "$out_dir" ]] || return 0
  find "$out_dir" -maxdepth 1 -type f \( \
    -name 'teaching-design-package-full.md' -o \
    -name 'teaching-design-package.typ' -o \
    -name 'teaching-design-package.pdf' -o \
    -name 'teaching-plan.pdf' -o \
    -name 'teaching-design.pdf' -o \
    -name 'status.json' -o \
    -name 'manifest.json' -o \
    -name 'model.json' -o \
    -name 'diagnostics.json' -o \
    -name 'calendar.json' -o \
    -name '*.log' -o \
    -name '*.typ' -o \
    -name '*教学资料.md' -o \
    -name '*教学资料.pdf' -o \
    -name '*授课进度计划表.pdf' -o \
    -name '*教学设计方案.pdf' \
  \) -exec rm -f {} +
}

record_failure() {
  local input="$1" out_dir="$2" code="$3" message="$4" log_path="$5"
  shift 5
  mkdir -p "${out_dir}/.teaching-design-package/debug"
  cleanup_public_root "$out_dir"
  {
    printf 'TDPKG_DIAGNOSTIC_JSON={"code":"%s","mismatch_class":"%s","message":"%s","source_markdown":"%s"' \
      "$(json_escape "$code")" "$(json_escape "$code")" "$(json_escape "$message")" "$(json_escape "$input")"
    while [[ $# -gt 1 ]]; do
      printf ',"%s":"%s"' "$(json_escape "$1")" "$(json_escape "$2")"
      shift 2
    done
    printf '}\n'
  } >>"$log_path"
  write_failure_diagnostics "$input" "$out_dir" "$log_path"
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

write_teaching_plan_typst() {
  local model_path="$1" typ_path="$2"
  node "${SCRIPT_DIR}/teaching-plan-renderer.js" "$model_path" "$typ_path"
}

write_teaching_design_typst() {
  local model_path="$1" typ_path="$2"
  node "${SCRIPT_DIR}/teaching-design-renderer.js" "$model_path" "$typ_path"
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
  local model_path="$1" out_dir="$2" pdf_requested="$3" module_status_json="$4" merge_status_json="$5" leakage_status="$6"
  local status_path="${out_dir}/.teaching-design-package/${STATUS_NAME}"
  mkdir -p "${out_dir}/.teaching-design-package"
  node - "$model_path" "$status_path" "$out_dir" "$pdf_requested" "$module_status_json" "$merge_status_json" "$leakage_status" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const statusPath = process.argv[3];
const outDir = process.argv[4];
const pdfRequested = process.argv[5] === 'true';
const modulePdfStatuses = JSON.parse(process.argv[6]);
const merge = JSON.parse(process.argv[7]);
const leakageStatus = process.argv[8];
const delivery = model.public_delivery;
const publicOutputs = {
  unified_markdown: `${outDir}/${delivery.public_markdown_filename}`,
  full_package_pdf: `${outDir}/${delivery.public_package_pdf_filename}`,
  module_pdfs: Object.fromEntries(delivery.module_pdfs.map((item) => [item.module_id, `${outDir}/${item.public_pdf_filename}`])),
};
const expectedPublicOutputs = delivery.expected_public_filenames.map((filename) => `${outDir}/${filename}`);
const markdownPassed = fs.existsSync(publicOutputs.unified_markdown) && fs.statSync(publicOutputs.unified_markdown).size > 0;
const mergedPassed = fs.existsSync(publicOutputs.full_package_pdf) && fs.statSync(publicOutputs.full_package_pdf).size > 0;
const allModulesPassed = modulePdfStatuses.length === model.modules.registry.length
  && modulePdfStatuses.every((item) => item.status === 'passed' && item.exists === true && item.nonempty === true && item.size > 0);
const status = {
  generated_from_markdown: true,
  package_owned_model: true,
  phase33_module_registry: true,
  phase36_public_delivery: true,
  source_markdown: model.source_markdown,
  hidden_model: `${outDir}/.teaching-design-package/model.json`,
  hidden_status: statusPath,
  hidden_work_dir: `${outDir}/.teaching-design-package/work`,
  hidden_staging_dir: `${outDir}/.teaching-design-package/staging`,
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
  public_delivery: delivery,
  validation: model.validation,
  teaching_plan_formal_renderer: {
    status: 'passed',
    renderer: 'package-owned teaching-plan-renderer.js',
    legacy_surface: 'jiaoan-jihua official five-column table',
    source: 'shared_scheduling_model',
    total_hours_source: model.validation.total_hours_source,
    hidden_typst: `${outDir}/.teaching-design-package/work/teaching-plan.typ`,
    public_pdf: publicOutputs.module_pdfs['teaching-plan'],
    pdf_compile_status: (modulePdfStatuses.find((item) => item.module_id === 'teaching-plan') || {}).status || 'not_run',
  },
  teaching_design_formal_renderer: {
    status: 'passed',
    renderer: 'package-owned teaching-design-renderer.js',
    legacy_surface: 'jiaoan-shicao formal teaching-design layout',
    source: 'shared_scheduling_model',
    total_hours_source: model.validation.total_hours_source,
    task_hours_source: 'schedule.tasks[].total_hours',
    activity_hours_source: 'schedule.tasks[].stages[].rows[].hours',
    cross_module_validation: 'passed',
    hidden_typst: `${outDir}/.teaching-design-package/work/teaching-design.typ`,
    public_pdf: publicOutputs.module_pdfs['teaching-design'],
    pdf_compile_status: (modulePdfStatuses.find((item) => item.module_id === 'teaching-design') || {}).status || 'not_run',
  },
  public_outputs: publicOutputs,
  expected_public_outputs: expectedPublicOutputs,
  pdf_requested: pdfRequested,
  module_pdf_statuses: modulePdfStatuses,
  merge,
  pdf_merge: merge,
  pdf_status: {
    full_package_pdf: merge.status || 'not_run',
    module_pdfs: Object.fromEntries(modulePdfStatuses.map((item) => [item.module_id, item.status])),
  },
  public_root_leakage_check: leakageStatus,
  review_markers: model.review_markers,
  final_ready: pdfRequested && markdownPassed && allModulesPassed && mergedPassed && merge.status === 'passed' && leakageStatus === 'passed' && model.review_markers.length === 0 && model.validation.errors.length === 0,
  notes: [
    'Default successful delivery root is exactly one course-name-prefixed unified Markdown, one merged package PDF, and one PDF per registered module.',
    'The merged package PDF is created from registered module PDFs in module registry order.',
    'Diagnostics, status, stderr logs, module Typst, module Markdown, model JSON, staging files, and failure evidence stay under .teaching-design-package/.',
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
  teaching_design_formal_renderer: {
    status: 'passed',
    renderer: 'package-owned teaching-design-renderer.js',
    legacy_surface: 'jiaoan-shicao formal teaching-design layout',
    scheduling_source: 'shared_scheduling_model',
    hidden_typst: model.modules.items.find((item) => item.id === 'teaching-design').work_typst,
  },
  cross_module_validation: model.validation.cross_module_evidence,
  module_registry: model.modules.registry,
  public_delivery: model.public_delivery,
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
    'teaching_design_task_count_mismatch',
    'teaching_design_stage_count_mismatch',
    'teaching_design_activity_count_mismatch',
    'teaching_design_task_title_mismatch',
    'teaching_design_stage_title_mismatch',
    'teaching_design_activity_title_mismatch',
    'teaching_design_task_hours_mismatch',
    'teaching_design_activity_hours_mismatch',
    'teaching_design_task_date_range_mismatch',
    'missing_teaching_design_analysis_block',
    'missing_teaching_design_activity_block',
    'missing_teaching_design_evaluation_block',
    'teaching_design_formal_render_failed',
    'teaching_design_pdf_compile_failed',
    'hidden_artifact_write_failure',
    'public_root_leakage',
    'invalid_course_name_for_filename',
    'module_pdf_missing',
    'module_pdf_empty',
    'module_status_failed',
    'merge_input_order_mismatch',
    'merge_tool_unavailable',
    'merge_tool_failed',
    'merged_pdf_empty',
    'standalone_copy_failed',
  ],
};
fs.writeFileSync(diagnosticsPath, JSON.stringify(diagnostics, null, 2));
NODE
}

assert_no_public_leakage() {
  local out_dir="$1" leak
  leak="$(find "$out_dir" -maxdepth 1 -type f -print | rg '[.]typ$|status[.]json$|manifest[.]json$|model[.]json$|diagnostics[.]json$|calendar[.]json$|[.]log$|teaching-plan[.]md$|teaching-design[.]md$|teaching-plan[.]typ$|teaching-design[.]typ$|teaching-design-package-full[.]md$|teaching-design-package[.]typ$|teaching-design-package[.]pdf$|teaching-plan[.]pdf$|teaching-design[.]pdf$' || true)"
  if [[ -n "$leak" ]]; then
    printf 'teaching-design-package.sh: public_root_leakage: %s\n' "$leak" >&2
    return 1
  fi
}

pdf_nonempty() {
  [[ -s "$1" ]]
}

module_status_json_not_run() {
  local model_path="$1" out_dir="$2"
  node - "$model_path" "$out_dir" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outDir = process.argv[3];
const values = model.modules.items.map((item) => ({
  module_id: item.id,
  display_name: item.display_name,
  order: item.order,
  status: 'not_run',
  hidden_typst: `${outDir}/${item.work_typst}`,
  staging_path: `${outDir}/.teaching-design-package/staging/${item.pdf_filename}`,
  public_path: `${outDir}/${item.public_pdf_filename}`,
  exists: false,
  nonempty: false,
  size: 0,
}));
process.stdout.write(JSON.stringify(values));
NODE
}

merge_status_not_run() {
  local model_path="$1" out_dir="$2"
  node - "$model_path" "$out_dir" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outDir = process.argv[3];
process.stdout.write(JSON.stringify({
  status: 'not_run',
  merge_tool: 'not_run',
  tool: 'not_run',
  inputs: [],
  merge_inputs: [],
  output_staging_path: `${outDir}/.teaching-design-package/staging/${model.public_delivery.public_package_pdf_filename}`,
  public_output_path: `${outDir}/${model.public_delivery.public_package_pdf_filename}`,
  exit_code: null,
  output_size: 0,
}));
NODE
}

compile_registered_module_pdfs() {
  local model_path="$1" out_dir="$2" staging_dir="$3"
  node - "$model_path" "$out_dir" "$staging_dir" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outDir = process.argv[3];
const stagingDir = process.argv[4];
for (const item of model.modules.items) {
  console.log([item.id, item.display_name, item.order, `${outDir}/${item.work_typst}`, `${stagingDir}/${item.pdf_filename}`, `${outDir}/${item.public_pdf_filename}`].join('\t'));
}
NODE
}

verify_module_pdf_statuses() {
  local model_path="$1" out_dir="$2" staging_dir="$3"
  node - "$model_path" "$out_dir" "$staging_dir" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outDir = process.argv[3];
const stagingDir = process.argv[4];
const values = model.modules.items.map((item) => {
  const stagingPath = `${stagingDir}/${item.pdf_filename}`;
  const exists = fs.existsSync(stagingPath);
  const size = exists ? fs.statSync(stagingPath).size : 0;
  return {
    module_id: item.id,
    display_name: item.display_name,
    order: item.order,
    status: exists && size > 0 ? 'passed' : exists ? 'module_pdf_empty' : 'module_pdf_missing',
    hidden_typst: `${outDir}/${item.work_typst}`,
    staging_path: stagingPath,
    public_path: `${outDir}/${item.public_pdf_filename}`,
    exists,
    nonempty: size > 0,
    size,
  };
});
process.stdout.write(JSON.stringify(values));
NODE
}

merge_registered_pdfs() {
  local model_path="$1" out_dir="$2" staging_dir="$3" status_path="$4" log_path="$5"
  node - "$model_path" "$out_dir" "$staging_dir" >"${staging_dir}/merge-plan.json" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outDir = process.argv[3];
const stagingDir = process.argv[4];
const inputs = model.modules.items
  .slice()
  .sort((a, b) => a.order - b.order)
  .map((item) => {
    const stagingPath = `${stagingDir}/${item.pdf_filename}`;
    const size = fs.existsSync(stagingPath) ? fs.statSync(stagingPath).size : 0;
    return {
      module_id: item.id,
      display_name: item.display_name,
      order: item.order,
      staging_path: stagingPath,
      public_path: `${outDir}/${item.public_pdf_filename}`,
      source_typst: `${outDir}/${item.work_typst}`,
      size,
    };
  });
process.stdout.write(JSON.stringify({
  inputs,
  output_staging_path: `${stagingDir}/${model.public_delivery.public_package_pdf_filename}`,
  public_output_path: `${outDir}/${model.public_delivery.public_package_pdf_filename}`,
}));
NODE
  local output_pdf
  output_pdf="$(node -e 'const fs=require("fs"); console.log(JSON.parse(fs.readFileSync(process.argv[1],"utf8")).output_staging_path)' "${staging_dir}/merge-plan.json")"
  rm -f "$output_pdf" "$log_path"

  if [[ "${TDPKG_FORCE_MERGE_FAILURE:-}" == "unavailable" ]]; then
    node - "${staging_dir}/merge-plan.json" "$status_path" merge_tool_unavailable not_run 127 0 <<'NODE'
const fs = require('fs');
const plan = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const statusPath = process.argv[3];
const status = process.argv[4];
const tool = process.argv[5];
const exitCode = Number(process.argv[6]);
const outputSize = Number(process.argv[7]);
fs.writeFileSync(statusPath, JSON.stringify({ status, merge_tool: tool, tool, inputs: plan.inputs, merge_inputs: plan.inputs, output_staging_path: plan.output_staging_path, public_output_path: plan.public_output_path, exit_code: exitCode, output_size: outputSize }, null, 2));
NODE
    return 1
  fi

  local tool="" exit_code=0
  local -a merge_inputs
  while IFS= read -r merge_input; do
    merge_inputs+=("$merge_input")
  done < <(node -e 'const fs=require("fs"); const p=JSON.parse(fs.readFileSync(process.argv[1],"utf8")); for (const item of p.inputs) console.log(item.staging_path)' "${staging_dir}/merge-plan.json")
  if [[ "${TDPKG_FORCE_MERGE_FAILURE:-}" == "failed" ]]; then
    tool="forced_failure"
    printf 'forced merge failure\n' >"$log_path"
    exit_code=99
  elif command -v pdfunite >/dev/null 2>&1; then
    tool="pdfunite"
    set +e
    pdfunite "${merge_inputs[@]}" "$output_pdf" >"$log_path" 2>&1
    exit_code=$?
    set -e
  elif command -v qpdf >/dev/null 2>&1; then
    tool="qpdf"
    set +e
    qpdf --empty --pages "${merge_inputs[@]}" -- "$output_pdf" >"$log_path" 2>&1
    exit_code=$?
    set -e
  else
    tool="python_fitz"
    set +e
    python3 - "${staging_dir}/merge-plan.json" "$output_pdf" >"$log_path" 2>&1 <<'PY'
import json
import sys

plan = json.load(open(sys.argv[1], encoding="utf-8"))
output = sys.argv[2]
try:
    import fitz
except Exception as exc:
    print(f"PyMuPDF unavailable: {exc}", file=sys.stderr)
    sys.exit(127)

merged = fitz.open()
try:
    for item in plan["inputs"]:
        with fitz.open(item["staging_path"]) as src:
            merged.insert_pdf(src)
    merged.save(output)
finally:
    merged.close()
PY
    exit_code=$?
    set -e
  fi

  if [[ "${TDPKG_FORCE_MERGE_FAILURE:-}" == "empty" ]]; then
    : >"$output_pdf"
  fi

  local output_size=0 status="passed"
  if [[ -f "$output_pdf" ]]; then
    output_size="$(wc -c <"$output_pdf" | tr -d ' ')"
  fi
  if [[ "$exit_code" -ne 0 ]]; then
    status="merge_tool_failed"
  elif [[ ! -s "$output_pdf" ]]; then
    status="merged_pdf_empty"
  fi
  node - "${staging_dir}/merge-plan.json" "$status_path" "$status" "$tool" "$exit_code" "$output_size" "$log_path" <<'NODE'
const fs = require('fs');
const plan = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const statusPath = process.argv[3];
const status = process.argv[4];
const tool = process.argv[5];
const exitCode = Number(process.argv[6]);
const outputSize = Number(process.argv[7]);
const logPath = process.argv[8];
fs.writeFileSync(statusPath, JSON.stringify({
  status,
  merge_tool: tool,
  tool,
  command_summary: tool === 'python_fitz' ? 'python3 PyMuPDF insert_pdf fallback' : tool,
  inputs: plan.inputs,
  merge_inputs: plan.inputs,
  output_staging_path: plan.output_staging_path,
  public_output_path: plan.public_output_path,
  exit_code: exitCode,
  stdout_stderr_log: logPath,
  output_size: outputSize,
  nonempty: outputSize > 0,
}, null, 2));
NODE
  [[ "$status" == "passed" ]]
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
  cleanup_public_root "$OUT_DIR"
  local model_path staging_dir module_statuses_json merge_status_json merge_status_path merge_log leakage_status="not_run"
  model_path="$(write_model_file "$INPUT" "$OUT_DIR")"
  staging_dir="${OUT_DIR}/.teaching-design-package/staging"
  mkdir -p "$staging_dir"
  find "$staging_dir" -mindepth 1 -maxdepth 1 -type f -exec rm -f {} +
  write_unified_typst "$model_path" "${OUT_DIR}/.teaching-design-package/work/teaching-design-package.typ"
  write_module_markdown_files "$model_path" "$OUT_DIR"
  write_teaching_plan_typst "$model_path" "${OUT_DIR}/.teaching-design-package/work/teaching-plan.typ"
  if ! write_teaching_design_typst "$model_path" "${OUT_DIR}/.teaching-design-package/work/teaching-design.typ" 2>"${OUT_DIR}/.teaching-design-package/debug/teaching-design-renderer.stderr.log"; then
    printf 'TDPKG_DIAGNOSTIC_JSON={"code":"teaching_design_formal_render_failed","mismatch_class":"teaching_design_formal_render_failed","module_id":"teaching-design","message":"package-owned teaching-design renderer failed","source_markdown":"%s"}\n' "$(json_escape "$INPUT")" >>"${OUT_DIR}/.teaching-design-package/debug/teaching-design-renderer.stderr.log"
    write_failure_diagnostics "$INPUT" "$OUT_DIR" "${OUT_DIR}/.teaching-design-package/debug/teaching-design-renderer.stderr.log"
    cat "${OUT_DIR}/.teaching-design-package/debug/teaching-design-renderer.stderr.log" >&2
    return 1
  fi
  module_statuses_json="$(module_status_json_not_run "$model_path" "$OUT_DIR")"
  merge_status_json="$(merge_status_not_run "$model_path" "$OUT_DIR")"
  if [[ "$RENDER_PDF" == true ]]; then
    while IFS=$'\t' read -r module_id display_name order hidden_typst staging_pdf public_pdf; do
      local compile_log="${OUT_DIR}/.teaching-design-package/debug/${module_id}-pdf.stderr.log"
      if ! compile_pdf "$hidden_typst" "$staging_pdf" "$compile_log"; then
        printf 'module %s PDF compile failed\n' "$module_id" >>"$compile_log"
      fi
    done < <(compile_registered_module_pdfs "$model_path" "$OUT_DIR" "$staging_dir")

    if [[ -n "${TDPKG_FORCE_MODULE_PDF_MISSING:-}" ]]; then
      node - "$model_path" "$staging_dir" "${TDPKG_FORCE_MODULE_PDF_MISSING}" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const stagingDir = process.argv[3];
const id = process.argv[4];
const item = model.modules.items.find((entry) => entry.id === id);
if (item) fs.rmSync(`${stagingDir}/${item.pdf_filename}`, { force: true });
NODE
    fi
    if [[ -n "${TDPKG_FORCE_MODULE_PDF_EMPTY:-}" ]]; then
      node - "$model_path" "$staging_dir" "${TDPKG_FORCE_MODULE_PDF_EMPTY}" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const stagingDir = process.argv[3];
const id = process.argv[4];
const item = model.modules.items.find((entry) => entry.id === id);
if (item) fs.writeFileSync(`${stagingDir}/${item.pdf_filename}`, '');
NODE
    fi

    module_statuses_json="$(verify_module_pdf_statuses "$model_path" "$OUT_DIR" "$staging_dir")"
    local failed_module_status
    failed_module_status="$(node -e 'const s=JSON.parse(process.argv[1]); const bad=s.find(i=>i.status!=="passed"); if (bad) console.log([bad.status,bad.module_id,bad.staging_path,bad.size].join("\t"));' "$module_statuses_json")"
    if [[ -n "$failed_module_status" ]]; then
      local fail_code fail_module fail_path fail_size
      IFS=$'\t' read -r fail_code fail_module fail_path fail_size <<<"$failed_module_status"
      merge_status_json="$(merge_status_not_run "$model_path" "$OUT_DIR")"
      write_status "$model_path" "$OUT_DIR" "$RENDER_PDF" "$module_statuses_json" "$merge_status_json" "not_run"
      record_failure "$INPUT" "$OUT_DIR" "$fail_code" "registered module PDF is not available for merge" "${OUT_DIR}/.teaching-design-package/debug/${fail_module}-pdf.stderr.log" \
        module_id "$fail_module" staging_path "$fail_path" actual_size "$fail_size" expected "non-empty module PDF"
      die "render-package --pdf failed before merge because module PDF ${fail_module} was not non-empty"
    fi

    merge_status_path="${OUT_DIR}/.teaching-design-package/debug/merge-status.json"
    merge_log="${OUT_DIR}/.teaching-design-package/debug/merge.stderr.log"
    if ! merge_registered_pdfs "$model_path" "$OUT_DIR" "$staging_dir" "$merge_status_path" "$merge_log"; then
      merge_status_json="$(tr -d '\n' <"$merge_status_path")"
      write_status "$model_path" "$OUT_DIR" "$RENDER_PDF" "$module_statuses_json" "$merge_status_json" "not_run"
      local merge_code
      merge_code="$(node -e 'const fs=require("fs"); const s=JSON.parse(fs.readFileSync(process.argv[1],"utf8")); console.log(s.status)' "$merge_status_path")"
      record_failure "$INPUT" "$OUT_DIR" "$merge_code" "registered module PDF merge failed" "$merge_log" merge_status "$merge_code"
      die "render-package --pdf failed during module PDF merge"
    fi
    merge_status_json="$(tr -d '\n' <"$merge_status_path")"

    node - "$model_path" "$OUT_DIR" "$staging_dir" "$INPUT" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outDir = process.argv[3];
const stagingDir = process.argv[4];
const input = process.argv[5];
const delivery = model.public_delivery;
fs.copyFileSync(input, `${outDir}/${delivery.public_markdown_filename}`);
for (const item of model.modules.items) {
  fs.copyFileSync(`${stagingDir}/${item.pdf_filename}`, `${outDir}/${item.public_pdf_filename}`);
}
fs.copyFileSync(`${stagingDir}/${delivery.public_package_pdf_filename}`, `${outDir}/${delivery.public_package_pdf_filename}`);
NODE
    if [[ "${TDPKG_FORCE_PUBLIC_LEAKAGE:-}" == "status" ]]; then
      printf '{}\n' >"${OUT_DIR}/status.json"
    elif [[ "${TDPKG_FORCE_PUBLIC_LEAKAGE:-}" == "typ" ]]; then
      printf 'leak\n' >"${OUT_DIR}/leaked.typ"
    elif [[ "${TDPKG_FORCE_PUBLIC_LEAKAGE:-}" == "calendar" ]]; then
      printf '{}\n' >"${OUT_DIR}/calendar.json"
    elif [[ "${TDPKG_FORCE_PUBLIC_LEAKAGE:-}" == "old_english" ]]; then
      printf 'leak\n' >"${OUT_DIR}/teaching-plan.pdf"
    fi
  else
    node - "$model_path" "$OUT_DIR" "$INPUT" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outDir = process.argv[3];
const input = process.argv[4];
fs.copyFileSync(input, `${outDir}/${model.public_delivery.public_markdown_filename}`);
NODE
  fi
  write_diagnostics "$model_path" "$OUT_DIR"
  if ! assert_no_public_leakage "$OUT_DIR"; then
    write_status "$model_path" "$OUT_DIR" "$RENDER_PDF" "$module_statuses_json" "$merge_status_json" "failed"
    record_failure "$INPUT" "$OUT_DIR" "public_root_leakage" "public root leaked hidden or obsolete artifacts" "${OUT_DIR}/.teaching-design-package/debug/public-root-leakage.stderr.log"
    die "public root leaked hidden package artifacts; diagnostics are under ${OUT_DIR}/.teaching-design-package/"
  fi
  leakage_status="passed"
  write_status "$model_path" "$OUT_DIR" "$RENDER_PDF" "$module_statuses_json" "$merge_status_json" "$leakage_status"
  if [[ "$RENDER_PDF" == true ]]; then
    local final_ready
    final_ready="$(node -e 'const fs=require("fs"); const s=JSON.parse(fs.readFileSync(process.argv[1],"utf8")); console.log(s.final_ready ? "true" : "false")' "${OUT_DIR}/.teaching-design-package/${STATUS_NAME}")"
    if [[ "$final_ready" != "true" ]]; then
      cp "${OUT_DIR}/.teaching-design-package/${STATUS_NAME}" "${OUT_DIR}/.teaching-design-package/failure-diagnostics/${STATUS_NAME}"
      cleanup_public_root "$OUT_DIR"
      die "render-package --pdf did not produce a final-ready course-prefixed delivery; diagnostics are under ${OUT_DIR}/.teaching-design-package/"
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
  write_status "$model_path" "$OUT_DIR" "false" "$(module_status_json_not_run "$model_path" "$OUT_DIR")" "$(merge_status_not_run "$model_path" "$OUT_DIR")" "not_run"
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
  printf 'teaching-design-package.sh 0.6.0-phase36\n'
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
