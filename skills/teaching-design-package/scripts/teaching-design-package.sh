#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$SCRIPT_DIR" == "${BASH_SOURCE[0]}" ]]; then
  SCRIPT_DIR="."
fi
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEMPLATE_MD="${SKILL_DIR}/templates/teaching-design-package-full.md"
MANIFEST_NAME="teaching-design-package-status.json"
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

The normal path is unified Markdown -> package data model -> package Typst/PDF status.
PDF files are produced only when local tools are available; otherwise status is honest and non-final.
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
  node - "$input" "$DEFAULT_DAILY_HOURS" <<'NODE'
const fs = require('fs');

const inputPath = process.argv[2];
const dailyHours = Number(process.argv[3] || 8);

function fail(message) {
  console.error(`teaching-design-package.sh: ${message}`);
  process.exit(1);
}

function splitFrontmatter(markdown) {
  const match = markdown.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!match) fail('frontmatter is required');
  return { frontmatter: match[1], body: markdown.slice(match[0].length) };
}

function scalar(frontmatter, key) {
  const match = frontmatter.match(new RegExp(`^${key}:\\s*(.*)$`, 'm'));
  if (!match) return '';
  return match[1].trim().replace(/^["']|["']$/g, '');
}

function list(frontmatter, key) {
  const lines = frontmatter.split(/\n/);
  const values = [];
  let inList = false;
  for (const line of lines) {
    if (line === `${key}:`) {
      inList = true;
      continue;
    }
    if (!inList) continue;
    const item = line.match(/^\s*-\s*(.*)$/);
    if (item) {
      values.push(item[1].trim().replace(/^["']|["']$/g, ''));
      continue;
    }
    if (/^[A-Za-z0-9_-]+:/.test(line)) break;
  }
  return values;
}

function addDays(date, days) {
  const value = new Date(`${date}T00:00:00Z`);
  value.setUTCDate(value.getUTCDate() + days);
  return value.toISOString().slice(0, 10);
}

function labelDate(date) {
  const match = date.match(/^[0-9]{4}-([0-9]{2})-([0-9]{2})$/);
  if (!match) return date;
  return `${Number(match[1])}月${Number(match[2])}日`;
}

function dateRangeLabel(start, end) {
  return `${labelDate(start)}--${labelDate(end)}`;
}

function weekdayName(date) {
  return ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][new Date(`${date}T00:00:00Z`).getUTCDay()];
}

function inferTerm(firstTeachingDay) {
  const match = firstTeachingDay.match(/^([0-9]{4})-([0-9]{2})-[0-9]{2}$/);
  if (!match) fail(`invalid first_teaching_day: ${firstTeachingDay}`);
  const year = Number(match[1]);
  const month = Number(match[2]);
  if (month >= 9) return { school_year: `${year}-${year + 1}学年`, semester: '第一学期' };
  return { school_year: `${year - 1}-${year}学年`, semester: '第二学期' };
}

function extractSection(markdown, heading, nextHeading) {
  const start = markdown.match(new RegExp(`^# ${heading}$`, 'm'));
  if (!start) fail(`missing # ${heading}`);
  const startIndex = start.index + start[0].length;
  const rest = markdown.slice(startIndex);
  const end = nextHeading ? rest.match(new RegExp(`\\n# ${nextHeading}$`, 'm')) : null;
  return (end ? rest.slice(0, end.index) : rest).replace(/^\n+|\n+$/g, '');
}

function parsePlanRows(planText) {
  const tasks = [];
  let currentTask = null;
  let currentStage = null;
  for (const line of planText.split(/\n/)) {
    const taskMatch = line.match(/^##\s+(.+)$/);
    if (taskMatch) {
      currentTask = { title: taskMatch[1], stages: [], rows: [], total_hours: 0 };
      tasks.push(currentTask);
      currentStage = null;
      continue;
    }
    const stageMatch = line.match(/^###\s+(.+)$/);
    if (stageMatch) {
      currentStage = { title: stageMatch[1], rows: [], total_hours: 0 };
      if (currentTask) currentTask.stages.push(currentStage);
      continue;
    }
    const rowMatch = line.match(/^(.+)-([0-9]+)$/);
    if (currentTask && currentStage && rowMatch) {
      const row = {
        title: rowMatch[1].trim(),
        hours: Number(rowMatch[2]),
        task_title: currentTask.title,
        stage_title: currentStage.title,
      };
      currentStage.rows.push(row);
      currentStage.total_hours += row.hours;
      currentTask.rows.push(row);
      currentTask.total_hours += row.hours;
    }
  }
  if (!tasks.length) fail('no schedule tasks found');
  for (const task of tasks) {
    if (!task.rows.length) fail(`schedule task has no hour rows: ${task.title}`);
  }
  return tasks;
}

function assignDates(tasks, firstTeachingDay) {
  let currentDate = firstTeachingDay;
  let remaining = dailyHours;
  let consumedDays = 0;
  for (const task of tasks) {
    let start = '';
    let end = '';
    for (const row of task.rows) {
      let left = row.hours;
      row.consumption = [];
      while (left > 0) {
        if (!start) start = currentDate;
        end = currentDate;
        const take = Math.min(left, remaining);
        row.consumption.push({ date: currentDate, weekday: weekdayName(currentDate), hours: take });
        left -= take;
        remaining -= take;
        if (remaining === 0) {
          consumedDays += 1;
          currentDate = addDays(firstTeachingDay, consumedDays);
          remaining = dailyHours;
        }
      }
    }
    task.start_date = start;
    task.end_date = end;
    task.date_range = dateRangeLabel(start, end);
  }
}

function reviewMarkers(markdown) {
  const match = markdown.match(/^## 复核标记\n([\s\S]*?)(?:\n## |\n# |$)/m);
  if (!match) return [];
  return match[1].split(/\n/).map((line) => line.trim()).filter((line) => line && line !== '无' && !line.startsWith('<!--'));
}

const markdown = fs.readFileSync(inputPath, 'utf8');
const { frontmatter } = splitFrontmatter(markdown);
const forbidden = [
  'total_hours',
  'school_year',
  'semester',
  'daily_hours',
  'hour_unit',
  'date_display_format',
  'date_locale',
  'calendar_source',
  'holidays',
  'makeup_days',
  'source_of_truth',
  'outputs',
  'validation',
];
const forbiddenPresent = forbidden.filter((key) => new RegExp(`^${key}:`, 'm').test(frontmatter));
if (forbiddenPresent.length) fail(`package frontmatter must not own derived fields: ${forbiddenPresent.join(', ')}`);

const firstTeachingDay = scalar(frontmatter, 'first_teaching_day');
if (!firstTeachingDay) fail('first_teaching_day is required');
const planText = extractSection(markdown, '授课进度计划', '教学设计方案');
const designText = extractSection(markdown, '教学设计方案');
const tasks = parsePlanRows(planText);
assignDates(tasks, firstTeachingDay);
const teachers = list(frontmatter, 'teachers');
const term = inferTerm(firstTeachingDay);
const totalHours = tasks.reduce((sum, task) => sum + task.total_hours, 0);

const model = {
  model_version: 'phase30.package-owned.v1',
  source_markdown: inputPath,
  metadata: {
    course_name: scalar(frontmatter, 'course_name'),
    major_name: scalar(frontmatter, 'major_name'),
    course_attribute: scalar(frontmatter, 'course_attribute'),
    textbook_name: scalar(frontmatter, 'textbook_name'),
    class_name: scalar(frontmatter, 'class_name'),
    teachers,
    teacher_name: teachers.join('、'),
    first_teaching_day: firstTeachingDay,
  },
  derived: {
    total_hours: totalHours,
    total_hours_label: `${totalHours}H`,
    daily_hours: dailyHours,
    school_year: term.school_year,
    semester: term.semester,
    term_label: `${term.school_year}${term.semester}`,
    start_date: tasks[0].start_date,
    end_date: tasks[tasks.length - 1].end_date,
    date_range: dateRangeLabel(tasks[0].start_date, tasks[tasks.length - 1].end_date),
  },
  schedule: {
    tasks,
  },
  teaching_design: {
    markdown: designText,
    analysis_blocks: (designText.match(/^## 学习任务分析$/gm) || []).length,
    activity_blocks: (designText.match(/^## 教学活动设计/gm) || []).length,
    evaluation_blocks: (designText.match(/^## 学业评价$/gm) || []).length,
  },
  resources: {
    rows: [...designText.matchAll(/^### 五、学习资源\n([\s\S]*?)(?:\n## |\n### |$)/gm)].map((match) => match[1].trim()),
  },
  review_markers: reviewMarkers(markdown),
  output_readiness: {
    markdown_valid: true,
    typst_ready: true,
    pdf_ready: false,
    final_ready: false,
  },
};

console.log(JSON.stringify(model, null, 2));
NODE
}

cmd_example() {
  parse_io_args "$@"
  [[ -n "$OUTPUT" ]] || die "example requires --output"
  need_file "$TEMPLATE_MD"
  ensure_parent_dir "$OUTPUT"
  cp "$TEMPLATE_MD" "$OUTPUT"
}

write_model_file() {
  local input="$1" out_dir="$2" model_path
  model_path="${out_dir}/.teaching-design-package/model.json"
  mkdir -p "${out_dir}/.teaching-design-package"
  package_model_json "$input" > "$model_path"
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

write_placeholder_pdf_typst() {
  local model_path="$1" typ_path="$2" title="$3"
  node - "$model_path" "$typ_path" "$title" <<'NODE'
const fs = require('fs');
const model = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const typPath = process.argv[3];
const title = process.argv[4];
const esc = (value) => String(value ?? '').replace(/\\/g, '\\\\').replace(/"/g, '\\"');
const lines = [
  '// Package-owned Phase 30 PDF surface.',
  '// This file is generated from the unified package model.',
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
  'Phase 30 provides the package-owned rendering path. Full official PDF layout remains scheduled for Phase 32.',
  '',
];
fs.writeFileSync(typPath, lines.join('\n'));
NODE
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
  local status_path="${out_dir}/${MANIFEST_NAME}"
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
  source_markdown: model.source_markdown,
  hidden_model: `${outDir}/.teaching-design-package/model.json`,
  derived: model.derived,
  public_outputs: publicOutputs,
  pdf_requested: pdfRequested,
  pdf_status: {
    full_package_pdf: fullStatus,
    teaching_plan_pdf: planStatus,
    teaching_design_pdf: designStatus,
  },
  review_markers: model.review_markers,
  final_ready: pdfRequested && fullStatus === 'passed' && planStatus === 'passed' && designStatus === 'passed' && model.review_markers.length === 0,
  notes: [
    'Phase 30 uses a package-owned model and rendering path.',
    'Full official PDF layout and clean final delivery enforcement are completed in later planned phases.',
  ],
};
fs.writeFileSync(statusPath, JSON.stringify(status, null, 2));
NODE
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
  write_placeholder_pdf_typst "$model_path" "${OUT_DIR}/.teaching-design-package/teaching-plan.typ" "授课进度计划"
  write_placeholder_pdf_typst "$model_path" "${OUT_DIR}/.teaching-design-package/teaching-design.typ" "教学设计方案"
  if [[ "$RENDER_PDF" == true ]]; then
    if compile_pdf "${OUT_DIR}/teaching-design-package.typ" "${OUT_DIR}/teaching-design-package.pdf" "${OUT_DIR}/.teaching-design-package/full-pdf.stderr.log"; then
      full_status="passed"
    else
      full_status="missing_compiler_or_failed"
    fi
    if compile_pdf "${OUT_DIR}/.teaching-design-package/teaching-plan.typ" "${OUT_DIR}/teaching-plan.pdf" "${OUT_DIR}/.teaching-design-package/plan-pdf.stderr.log"; then
      plan_status="passed"
    else
      plan_status="missing_compiler_or_failed"
    fi
    if compile_pdf "${OUT_DIR}/.teaching-design-package/teaching-design.typ" "${OUT_DIR}/teaching-design.pdf" "${OUT_DIR}/.teaching-design-package/design-pdf.stderr.log"; then
      design_status="passed"
    else
      design_status="missing_compiler_or_failed"
    fi
  fi
  write_status "$model_path" "$OUT_DIR" "$RENDER_PDF" "$full_status" "$plan_status" "$design_status"
}

cmd_manifest() {
  parse_io_args "$@"
  [[ -n "$INPUT" ]] || die "manifest requires --input"
  [[ -n "$OUT_DIR" ]] || die "manifest requires --out-dir"
  mkdir -p "$OUT_DIR"
  local model_path
  model_path="$(write_model_file "$INPUT" "$OUT_DIR")"
  write_status "$model_path" "$OUT_DIR" "false" "not_run" "not_run" "not_run"
  printf '%s/%s\n' "$OUT_DIR" "$MANIFEST_NAME"
}

cmd_compat_render() {
  parse_io_args "$@"
  [[ -n "$INPUT" ]] || die "command requires --input"
  [[ -n "$OUT_DIR" ]] || die "command requires --out-dir"
  cmd_render_package --input "$INPUT" --out-dir "$OUT_DIR"
}

cmd_info() {
  printf 'teaching-design-package: standalone unified Markdown to package-owned model and Typst/PDF status.\n'
  printf 'Package checkpoint: templates/teaching-design-package-full.md\n'
  printf 'Reference: references/format-and-orchestration.md\n'
  printf 'Normal rendering does not require repository sibling skill folders.\n'
}

cmd_version() {
  printf 'teaching-design-package.sh 0.2.0-phase30\n'
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
