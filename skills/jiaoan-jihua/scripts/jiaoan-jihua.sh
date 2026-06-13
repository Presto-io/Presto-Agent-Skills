#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$SCRIPT_DIR" == "${BASH_SOURCE[0]}" ]]; then
  SCRIPT_DIR="."
fi
SKILL_DIR="${SCRIPT_DIR}/.."
TEMPLATE_MD="${SKILL_DIR}/templates/jiaoan-jihua-full.md"
CALENDAR_JSON="${SKILL_DIR}/references/calendar.json"

usage() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'USAGE'
Usage:
  jiaoan-jihua.sh example --output <jiaoan-jihua-full.md>
  jiaoan-jihua.sh render --input <input.md> [--typ <output.typ>]
                         [--expected-typ <reference.typ>]
  jiaoan-jihua.sh manifest
  jiaoan-jihua.sh info
  jiaoan-jihua.sh version

The Markdown-to-Typst conversion is implemented by this Bash script itself.
It does not call external renderers, PDF compilers, or template executables.
USAGE
}

die() {
  printf 'jiaoan-jihua.sh: %s\n' "$*" >&2
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

trim() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "$value"
}

strip_quotes() {
  local value
  value="$(trim "$1")"
  if [[ "$value" == \"*\" && "$value" == *\" ]]; then
    value="${value#\"}"
    value="${value%\"}"
  elif [[ "$value" == \'*\' && "$value" == *\' ]]; then
    value="${value#\'}"
    value="${value%\'}"
  fi
  printf '%s' "$value"
}

escape_string() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  printf '%s' "$value"
}

escape_content() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\[/\\[}"
  value="${value//\]/\\]}"
  value="${value//#/\\#}"
  value="${value//\$/\\$}"
  value="${value//%/\\%}"
  value="${value//&/\\&}"
  printf '%s' "$value"
}

render_plain_segment() {
  local value="$1" part
  while [[ "$value" == *"<br>"* ]]; do
    part="${value%%<br>*}"
    escape_content "$part"
    printf '#linebreak()'
    value="${value#*<br>}"
  done
  escape_content "$value"
}

render_inline() {
  local value="$1" before strong
  while [[ "$value" == *"**"* ]]; do
    before="${value%%\*\**}"
    value="${value#*\*\*}"
    if [[ "$value" != *"**"* ]]; then
      render_plain_segment "$before"
      printf '**'
      render_plain_segment "$value"
      return
    fi
    strong="${value%%\*\**}"
    value="${value#*\*\*}"
    render_plain_segment "$before"
    printf '#strong['
    render_plain_segment "$strong"
    printf ']'
  done
  render_plain_segment "$value"
}

FM_TITLE="教学实施计划"
FM_COURSE=""
FM_MAJOR=""
FM_TEACHER=""
FM_CLASS=""
FM_FIRST_DAY=""
FM_DAILY_HOURS=""
FM_TEMPLATE=""
BODY_LINES=()

set_meta_value() {
  local key="$1" value="$2"
  value="$(strip_quotes "$value")"
  case "$key" in
    major_name) FM_MAJOR="$value" ;;
    course_name) FM_COURSE="$value"; FM_TITLE="$value 教学实施计划" ;;
    teacher_name) FM_TEACHER="$value" ;;
    class_name) FM_CLASS="$value" ;;
    first_teaching_day) FM_FIRST_DAY="$value" ;;
    daily_hours) FM_DAILY_HOURS="$value" ;;
    template) FM_TEMPLATE="$value" ;;
  esac
}

parse_input() {
  local input="$1" line first=true in_fm=false key value
  BODY_LINES=()
  FM_TITLE="教学实施计划"
  FM_COURSE=""
  FM_MAJOR=""
  FM_TEACHER=""
  FM_CLASS=""
  FM_FIRST_DAY=""
  FM_DAILY_HOURS=""
  FM_TEMPLATE=""

  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    if [[ "$first" == true ]]; then
      first=false
      if [[ "$line" == "---" ]]; then
        in_fm=true
        continue
      fi
    fi

    if [[ "$in_fm" == true ]]; then
      if [[ "$line" == "---" ]]; then
        in_fm=false
        continue
      fi
      if [[ "$line" =~ ^([A-Za-z0-9_-]+):[[:space:]]*(.*)$ ]]; then
        key="${BASH_REMATCH[1]}"
        value="${BASH_REMATCH[2]}"
        set_meta_value "$key" "$value"
      fi
    else
      BODY_LINES+=("$line")
    fi
  done < "$input"
}

date_to_serial() {
  local value="$1" year month day era yoe doy doe
  [[ "$value" =~ ^([0-9]{4})-([0-9]{2})-([0-9]{2})$ ]] || die "invalid date: $value"
  year=$((10#${BASH_REMATCH[1]}))
  month=$((10#${BASH_REMATCH[2]}))
  day=$((10#${BASH_REMATCH[3]}))
  if (( month <= 2 )); then
    year=$((year - 1))
  fi
  era=$(( year >= 0 ? year / 400 : (year - 399) / 400 ))
  yoe=$(( year - era * 400 ))
  if (( month > 2 )); then
    month=$((month - 3))
  else
    month=$((month + 9))
  fi
  doy=$(((153 * month + 2) / 5 + day - 1))
  doe=$((yoe * 365 + yoe / 4 - yoe / 100 + doy))
  printf '%s\n' $((era * 146097 + doe - 719468))
}

weekday_for_date() {
  local serial
  serial="$(date_to_serial "$1")"
  printf '%s\n' $((((serial + 3) % 7 + 7) % 7 + 1))
}

load_calendar_dates() {
  local line value
  need_file "$CALENDAR_JSON"
  CALENDAR_DATES=()
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="$(trim "$line")"
    if [[ "$line" =~ \"([0-9]{4}-[0-9]{2}-[0-9]{2})\" ]]; then
      value="${BASH_REMATCH[1]}"
      CALENDAR_DATES+=("$value")
    fi
  done < "$CALENDAR_JSON"
  [[ "${#CALENDAR_DATES[@]}" -gt 0 ]] || die "calendar has no teaching dates: $CALENDAR_JSON"
}

term_week_for_date() {
  local date="$1" first_date first_serial first_weekday term_start serial
  [[ "${#CALENDAR_DATES[@]}" -gt 0 ]] || load_calendar_dates
  first_date="${CALENDAR_DATES[0]}"
  first_serial="$(date_to_serial "$first_date")"
  first_weekday="$(weekday_for_date "$first_date")"
  term_start=$((first_serial - first_weekday + 1))
  serial="$(date_to_serial "$date")"
  printf '%s\n' $(((serial - term_start) / 7 + 1))
}

set_dyn() {
  local name="$1" value="$2"
  printf -v "$name" '%s' "$value"
}

get_dyn() {
  local name="$1"
  printf '%s' "${!name}"
}

append_unique() {
  local var="$1" value="$2" current item
  current="$(get_dyn "$var")"
  for item in $current; do
    [[ "$item" == "$value" ]] && return 0
  done
  if [[ -n "$current" ]]; then
    set_dyn "$var" "$current $value"
  else
    set_dyn "$var" "$value"
  fi
}

parse_official_jihua_body() {
  local line text hours task_count=0 stage_count row_count current_task=0 current_stage=0
  OFFICIAL_TASK_COUNT=0

  for line in "${BODY_LINES[@]}"; do
    line="$(trim "$line")"
    [[ -z "$line" ]] && continue

    if [[ "$line" =~ ^##[[:space:]]+(.+)$ ]]; then
      task_count=$((task_count + 1))
      current_task="$task_count"
      current_stage=0
      set_dyn "TASK_TITLE_${current_task}" "${BASH_REMATCH[1]}"
      set_dyn "TASK_STAGE_COUNT_${current_task}" "0"
      set_dyn "TASK_TOTAL_HOURS_${current_task}" "0"
      OFFICIAL_TASK_COUNT="$task_count"
      continue
    fi

    if [[ "$line" =~ ^###[[:space:]]+(.+)$ ]]; then
      (( current_task > 0 )) || die "stage appears before any task: $line"
      stage_count="$(get_dyn "TASK_STAGE_COUNT_${current_task}")"
      stage_count=$((stage_count + 1))
      current_stage="$stage_count"
      set_dyn "TASK_STAGE_COUNT_${current_task}" "$stage_count"
      set_dyn "STAGE_TITLE_${current_task}_${current_stage}" "${BASH_REMATCH[1]}"
      set_dyn "STAGE_ROW_COUNT_${current_task}_${current_stage}" "0"
      continue
    fi

    (( current_task > 0 )) || die "content appears before any task: $line"
    (( current_stage > 0 )) || die "content appears before any stage: $line"
    if [[ "$line" =~ ^(.+)-([0-9]+)$ ]]; then
      text="$(trim "${BASH_REMATCH[1]}")"
      hours="${BASH_REMATCH[2]}"
      [[ -n "$text" ]] || die "empty content before hour suffix: $line"
      row_count="$(get_dyn "STAGE_ROW_COUNT_${current_task}_${current_stage}")"
      row_count=$((row_count + 1))
      set_dyn "STAGE_ROW_COUNT_${current_task}_${current_stage}" "$row_count"
      set_dyn "ROW_TEXT_${current_task}_${current_stage}_${row_count}" "$text"
      set_dyn "ROW_HOURS_${current_task}_${current_stage}_${row_count}" "$hours"
      set_dyn "ROW_WEEKS_${current_task}_${current_stage}_${row_count}" ""
      set_dyn "ROW_DAYS_${current_task}_${current_stage}_${row_count}" ""
      set_dyn "TASK_TOTAL_HOURS_${current_task}" "$(( $(get_dyn "TASK_TOTAL_HOURS_${current_task}") + 10#$hours ))"
      continue
    fi

    die "malformed stage body line, expected text-N: $line"
  done

  (( OFFICIAL_TASK_COUNT > 0 )) || die "no learning tasks found"
}

assign_schedule_cells() {
  local daily_hours first_index=-1 index remaining t s r stage_count row_count hours_left hours date take week day min_week=999 max_week=0
  [[ -n "$FM_FIRST_DAY" ]] || die "frontmatter first_teaching_day is required"
  [[ -n "$FM_DAILY_HOURS" ]] || die "frontmatter daily_hours is required"
  [[ "$FM_DAILY_HOURS" =~ ^[0-9]+$ ]] || die "daily_hours must be an integer: $FM_DAILY_HOURS"
  daily_hours=$((10#$FM_DAILY_HOURS))
  (( daily_hours > 0 )) || die "daily_hours must be greater than zero"

  load_calendar_dates
  for ((index = 0; index < ${#CALENDAR_DATES[@]}; index++)); do
    if [[ "${CALENDAR_DATES[$index]}" == "$FM_FIRST_DAY" ]]; then
      first_index="$index"
      break
    fi
  done
  (( first_index >= 0 )) || die "first_teaching_day not found in calendar: $FM_FIRST_DAY"

  index="$first_index"
  remaining="$daily_hours"
  for ((t = 1; t <= OFFICIAL_TASK_COUNT; t++)); do
    stage_count="$(get_dyn "TASK_STAGE_COUNT_${t}")"
    for ((s = 1; s <= stage_count; s++)); do
      row_count="$(get_dyn "STAGE_ROW_COUNT_${t}_${s}")"
      (( row_count > 0 )) || die "stage has no content rows: $(get_dyn "STAGE_TITLE_${t}_${s}")"
      for ((r = 1; r <= row_count; r++)); do
        hours="$(get_dyn "ROW_HOURS_${t}_${s}_${r}")"
        hours_left=$((10#$hours))
        (( hours_left > 0 )) || die "row hours must be greater than zero"
        while (( hours_left > 0 )); do
          (( index < ${#CALENDAR_DATES[@]} )) || die "calendar ended before all hours were assigned"
          date="${CALENDAR_DATES[$index]}"
          week="$(term_week_for_date "$date")"
          day="$(weekday_for_date "$date")"
          append_unique "ROW_WEEKS_${t}_${s}_${r}" "$week"
          append_unique "ROW_DAYS_${t}_${s}_${r}" "$day"
          (( week < min_week )) && min_week="$week"
          (( week > max_week )) && max_week="$week"
          if (( hours_left < remaining )); then
            take="$hours_left"
          else
            take="$remaining"
          fi
          hours_left=$((hours_left - take))
          remaining=$((remaining - take))
          if (( remaining == 0 )); then
            index=$((index + 1))
            remaining="$daily_hours"
          fi
        done
      done
    done
  done

  OFFICIAL_MIN_WEEK="$min_week"
  OFFICIAL_MAX_WEEK="$max_week"
}

academic_year_label() {
  local year month
  [[ "$FM_FIRST_DAY" =~ ^([0-9]{4})-([0-9]{2})-[0-9]{2}$ ]] || die "invalid first_teaching_day: $FM_FIRST_DAY"
  year=$((10#${BASH_REMATCH[1]}))
  month=$((10#${BASH_REMATCH[2]}))
  if (( month >= 9 )); then
    printf '%s-%s学年第一学期' "$year" "$((year + 1))"
  else
    printf '%s-%s学年第二学期' "$((year - 1))" "$year"
  fi
}

emit_official_jihua_head() {
  local title
  title="$(academic_year_label)第${OFFICIAL_MIN_WEEK} - ${OFFICIAL_MAX_WEEK}周"
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'TYP'
// jiaoan-jihua official template
#import "@preview/cuti:0.2.1": show-cn-fakebold
#show: show-cn-fakebold

#set page(
  paper: "a4",
  flipped: false,
  margin: (top: 2.54cm, bottom: 2.54cm, left: 2.8cm, right: 2.8cm)
)

#set text(
  lang: "zh",
  font: "STSong",
  size: 10.5pt,
  hyphenate: false,
)

#set par(justify: true, leading: 0.52em)

#let cell-pad = (x: 4.8pt, y: 4.8pt)
#let task-th(body) = table.cell(align: center + horizon, inset: cell-pad)[#text(weight: 700)[#body]]
#let th(body) = table.cell(align: center + horizon, inset: cell-pad)[#body]
#let subth(body) = table.cell(align: center + horizon, inset: cell-pad)[#body]
#let body-cell(body) = table.cell(align: center + horizon, inset: cell-pad)[#body]
#let content-cell(body) = table.cell(align: left + horizon, inset: cell-pad)[#body]

TYP
  printf '#set document(\n'
  printf '  title: "授课进度计划表 %s",\n' "$(escape_string "$FM_COURSE")"
  printf '  author: "%s",\n' "$(escape_string "$FM_TEACHER")"
  printf '  keywords: "授课计划, 教学计划, 工学一体化",\n'
  printf ')\n\n'
  printf '#align(center)[#text(size: 14pt, weight: "bold")[%s]]\n' "$(escape_content "$title")"
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'TYP'
#v(0.45em)
#align(center)[#text(size: 14pt, weight: "bold")[工学一体化课程/基本技能课程授课进度计划表]]
#v(0.72em)

#text(size: 10.5pt)[
  #grid(columns: (1fr, 1fr), row-gutter: 0.75em,
TYP
  printf '    [专业名称：%s],\n' "$(escape_content "$FM_MAJOR")"
  printf '    [课程名称：%s],\n' "$(escape_content "$FM_COURSE")"
  printf '    [授课教师：%s],\n' "$(escape_content "$FM_TEACHER")"
  printf '    [授课班级：%s],\n' "$(escape_content "$FM_CLASS")"
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'TYP'
  )
]

#v(0.9em)

TYP
}

emit_official_content_line() {
  local macro="$1" value="$2"
  printf '    %s[' "$macro"
  render_inline "$value"
  printf '],\n'
}

emit_official_stage_first_cell() {
  local task="$1" stage="$2" rows="$3"
  printf '    table.cell(rowspan: %s, align: center + horizon, inset: cell-pad)[' "$rows"
  render_inline "学习环节${stage}名称：$(get_dyn "STAGE_TITLE_${task}_${stage}")"
  printf '],\n'
}

emit_official_jihua_table() {
  local t s r stage_count row_count total_hours
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'TYP'
#align(center)[
  #table(
    columns: (3.15cm, 8.51cm, 1.12cm, 1.29cm, 1.27cm),
    stroke: 0.5pt,
    align: center + horizon,
TYP

  for ((t = 1; t <= OFFICIAL_TASK_COUNT; t++)); do
    total_hours="$(get_dyn "TASK_TOTAL_HOURS_${t}")"
    printf '    task-th[学习任务%s名称：],\n' "$t"
    printf '    task-th['
    render_inline "$(get_dyn "TASK_TITLE_${t}")"
    printf '],\n'
    printf '    table.cell(colspan: 2, align: center + horizon, inset: cell-pad)[学时],\n'
    printf '    th[%sH],\n\n' "$total_hours"

    if (( t == 1 )); then
      printf '    subth[],\n'
      printf '    subth[教学内容],\n'
      printf '    subth[周次],\n'
      printf '    subth[星期],\n'
      printf '    subth[学时],\n\n'
    fi

    stage_count="$(get_dyn "TASK_STAGE_COUNT_${t}")"
    for ((s = 1; s <= stage_count; s++)); do
      row_count="$(get_dyn "STAGE_ROW_COUNT_${t}_${s}")"
      for ((r = 1; r <= row_count; r++)); do
        if (( r == 1 )); then
          emit_official_stage_first_cell "$t" "$s" "$row_count"
        fi
        emit_official_content_line "content-cell" "$(get_dyn "ROW_TEXT_${t}_${s}_${r}")"
        emit_official_content_line "body-cell" "$(get_dyn "ROW_WEEKS_${t}_${s}_${r}")"
        emit_official_content_line "body-cell" "$(get_dyn "ROW_DAYS_${t}_${s}_${r}")"
        emit_official_content_line "body-cell" "$(get_dyn "ROW_HOURS_${t}_${s}_${r}")"
        printf '\n'
      done
    done
  done

  while IFS= read -r line; do printf '%s\n' "$line"; done <<'TYP'
  )
]

TYP
}

emit_official_signature_grid() {
  printf '#v(1.1em)\n'
  printf '#grid(columns: (1fr, 1fr, 1fr),\n'
  printf '  [#align(center)[系主任：]],\n'
  printf '  [#align(center)[教研室主任：]],\n'
  printf '  [#align(center)[制表：%s]],\n' "$(escape_content "$FM_TEACHER")"
  printf ')\n'
}

emit_official_jihua_typst() {
  parse_official_jihua_body
  assign_schedule_cells
  emit_official_jihua_head
  emit_official_jihua_table
  emit_official_signature_grid
}

emit_head() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'TYP'
// Generated by jiaoan-jihua.sh with Bash builtins only.

#set page(
  paper: "a4",
  margin: (x: 24mm, y: 24mm),
)

#set text(
  lang: "zh",
  font: ("Noto Serif CJK SC", "Songti SC", "STSong"),
  size: 11pt,
)

#set par(
  justify: true,
  leading: 0.65em,
  spacing: 0.75em,
)

#show heading.where(level: 1): it => block(above: 0pt, below: 1.2em)[
  #align(center)[#text(size: 20pt, weight: "bold")[#it.body]]
]

#show heading.where(level: 2): it => block(above: 1.1em, below: 0.55em)[
  #text(size: 15pt, weight: "bold")[#it.body]
]

#show heading.where(level: 3): it => block(above: 0.9em, below: 0.35em)[
  #text(size: 13pt, weight: "bold")[#it.body]
]

#show heading.where(level: 4): it => block(above: 0.7em, below: 0.25em)[
  #text(size: 11pt, weight: "bold")[#it.body]
]

#let meta-row(label, value) = if value != "" [
  #text(weight: "bold")[#label：]#value#linebreak()
]

TYP
}

emit_meta() {
  printf '#set document(title: "%s", author: "%s")\n\n' "$(escape_string "$FM_TITLE")" "$(escape_string "$FM_TEACHER")"
  printf '= %s\n\n' "$(escape_content "$FM_TITLE")"
  printf '#block(stroke: 0.6pt, inset: 8pt, width: 100%%)[\n'
  printf '#meta-row("专业", "%s")\n' "$(escape_string "$FM_MAJOR")"
  printf '#meta-row("课程", "%s")\n' "$(escape_string "$FM_COURSE")"
  printf '#meta-row("任课教师", "%s")\n' "$(escape_string "$FM_TEACHER")"
  printf '#meta-row("授课班级", "%s")\n' "$(escape_string "$FM_CLASS")"
  printf '#meta-row("开课日期", "%s")\n' "$(escape_string "$FM_FIRST_DAY")"
  printf '#meta-row("每日课时", "%s")\n' "$(escape_string "$FM_DAILY_HOURS")"
  printf ']\n\n'
}

emit_heading() {
  local level="$1" text="$2" marker="" i
  for ((i = 0; i < level; i++)); do marker+="="; done
  printf '%s ' "$marker"
  render_inline "$text"
  printf '\n\n'
}

emit_paragraph() {
  render_inline "$1"
  printf '\n\n'
}

split_table_row() {
  local row="$1" cell
  TABLE_CELLS=()
  row="$(trim "$row")"
  row="${row#|}"
  row="${row%|}"
  while [[ "$row" == *"|"* ]]; do
    cell="${row%%|*}"
    TABLE_CELLS+=("$(trim "$cell")")
    row="${row#*|}"
  done
  TABLE_CELLS+=("$(trim "$row")")
}

is_table_delimiter() {
  local row="$1"
  row="${row//|/}"
  row="${row//:/}"
  row="${row//-/}"
  row="${row// /}"
  [[ -z "$row" ]]
}

emit_table() {
  local rows=("$@") max_cols row_idx cell i start=1
  split_table_row "${rows[0]}"
  max_cols="${#TABLE_CELLS[@]}"
  if [[ "${#rows[@]}" -gt 1 ]] && is_table_delimiter "${rows[1]}"; then
    start=2
  fi
  printf '#table(\n'
  printf '  columns: ('
  for ((i = 0; i < max_cols; i++)); do
    (( i > 0 )) && printf ', '
    printf '1fr'
  done
  printf '),\n'
  split_table_row "${rows[0]}"
  for cell in "${TABLE_CELLS[@]}"; do
    printf '  table.cell(fill: luma(235))[#strong['
    render_inline "$cell"
    printf ']],\n'
  done
  for ((row_idx = start; row_idx < ${#rows[@]}; row_idx++)); do
    split_table_row "${rows[$row_idx]}"
    for cell in "${TABLE_CELLS[@]}"; do
      printf '  ['
      render_inline "$cell"
      printf '],\n'
    done
  done
  printf ')\n\n'
}

render_body() {
  local total="${#BODY_LINES[@]}" i=0 line rows
  while (( i < total )); do
    line="${BODY_LINES[$i]}"
    if [[ -z "$(trim "$line")" ]]; then
      ((i++))
      continue
    fi
    if [[ "$line" =~ ^(#{1,5})[[:space:]]+(.*)$ ]]; then
      emit_heading "${#BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"
      ((i++))
      continue
    fi
    if [[ "$line" =~ ^[[:space:]]*\|.*\|[[:space:]]*$ ]]; then
      rows=()
      while (( i < total )) && [[ "${BODY_LINES[$i]}" =~ ^[[:space:]]*\|.*\|[[:space:]]*$ ]]; do
        rows+=("${BODY_LINES[$i]}")
        ((i++))
      done
      emit_table "${rows[@]}"
      continue
    fi
    if [[ "$line" =~ ^[[:space:]]*([0-9]+)\.[[:space:]]+(.*)$ ]]; then
      printf '+ '
      render_inline "${BASH_REMATCH[2]}"
      printf '\n'
      ((i++))
      continue
    fi
    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]+(.*)$ ]]; then
      printf -- '- '
      render_inline "${BASH_REMATCH[1]}"
      printf '\n'
      ((i++))
      continue
    fi
    emit_paragraph "$line"
    ((i++))
  done
}

render_markdown_to_typst() {
  local input="$1" output="$2"
  parse_input "$input"
  ensure_parent_dir "$output"
  : > "$output"
  {
    if [[ "$FM_TEMPLATE" == "jiaoan-jihua" ]]; then
      emit_official_jihua_typst
    else
      emit_head
      emit_meta
      render_body
    fi
  } >> "$output"
}

copy_file_shell() {
  local source="$1" output="$2" line
  ensure_parent_dir "$output"
  : > "$output"
  while IFS= read -r line || [[ -n "$line" ]]; do
    printf '%s\n' "$line" >> "$output"
  done < "$source"
}

same_file_shell() {
  local expected="$1" actual="$2" left right
  exec 3< "$expected"
  exec 4< "$actual"
  while true; do
    IFS= read -r left <&3; local left_status=$?
    IFS= read -r right <&4; local right_status=$?
    if [[ "$left_status" -ne "$right_status" ]]; then exec 3<&-; exec 4<&-; return 1; fi
    if [[ "$left_status" -ne 0 ]]; then exec 3<&-; exec 4<&-; return 0; fi
    if [[ "$left" != "$right" ]]; then exec 3<&-; exec 4<&-; return 1; fi
  done
}

cmd_example() {
  local output=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --output) output="${2:-}"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) die "unknown argument for example: $1" ;;
    esac
  done
  [[ -n "$output" ]] || die "example requires --output"
  need_file "$TEMPLATE_MD"
  copy_file_shell "$TEMPLATE_MD" "$output"
  printf 'wrote %s\n' "$output"
}

cmd_render() {
  local input="" typ="" expected_typ=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --input) input="${2:-}"; shift 2 ;;
      --typ) typ="${2:-}"; shift 2 ;;
      --expected-typ) expected_typ="${2:-}"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) die "unknown argument for render: $1" ;;
    esac
  done
  [[ -n "$input" ]] || die "render requires --input"
  need_file "$input"
  [[ -n "$typ" ]] || typ="${input%.*}.typ"
  render_markdown_to_typst "$input" "$typ"
  printf 'wrote %s\n' "$typ"
  if [[ -n "$expected_typ" ]]; then
    need_file "$expected_typ"
    same_file_shell "$expected_typ" "$typ" || die "Typst differs from expected file: $expected_typ"
    printf 'verified Typst matches %s\n' "$expected_typ"
  fi
}

cmd_manifest() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'JSON'
{
  "name": "jiaoan-jihua",
  "displayName": "教学计划",
  "version": "0.2.0-shell-only",
  "description": "Bash-only Markdown-to-Typst renderer for teaching plans."
}
JSON
}

cmd_info() {
  while IFS= read -r line; do printf '%s\n' "$line"; done <<'INFO'
jiaoan-jihua shell-only renderer
- Markdown-to-Typst conversion is performed inside this Bash script.
- PDF generation and external template execution are intentionally outside this script.
INFO
}

cmd_version() {
  printf 'jiaoan-jihua.sh 0.2.0-shell-only\n'
}

main() {
  local command="${1:-}"
  [[ $# -gt 0 ]] && shift
  case "$command" in
    example) cmd_example "$@" ;;
    render) cmd_render "$@" ;;
    manifest) cmd_manifest "$@" ;;
    info) cmd_info "$@" ;;
    version) cmd_version "$@" ;;
    -h|--help|"") usage ;;
    *) die "unknown command: $command" ;;
  esac
}

main "$@"
