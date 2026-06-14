# v1.10 fixture-backed Markdown-to-Typst renderer for jiaoan-shicao.
# The script reads the Markdown source only. Reference .typ files are handled
# by the caller's verification path, not by this generator.

function trim(value) {
  sub(/^[[:space:]]+/, "", value)
  sub(/[[:space:]]+$/, "", value)
  return value
}

function strip_quotes(value) {
  value = trim(value)
  if (value ~ /^".*"$/ || value ~ /^'\''.*'\''$/) {
    value = substr(value, 2, length(value) - 2)
  }
  return value
}

function normalize_course_attribute(value) {
  if (value == "工学一体化课程") return "□基本技能课程  ☑工学一体化课程"
  if (value == "基本技能课程") return "☑基本技能课程  □工学一体化课程"
  return value
}

function normalize_total_hours(value) {
  sub(/[Hh]$/, "", value)
  return value
}

function normalize_use_time(value) {
  gsub(/-/, "——", value)
  return value
}

function section_key(title) {
  if (title ~ /^一、/) return "desc"
  if (title ~ /^二、/) return "goals"
  if (title ~ /^三、/) return "content"
  if (title ~ /^四、/) return "students"
  if (title ~ /^五、/) return "resources"
  return ""
}

function append_line(var_name, text) {
  sep = (var_name ~ /students$/) ? "\n\n\n\n" : "\n\n"
  if (text == "") return
  if (DATA[var_name] == "") DATA[var_name] = text
  else DATA[var_name] = DATA[var_name] sep text
}

function parse_eval_line(text, parts) {
  split(text, parts, "；")
  EVAL_ITEM[task_count, eval_count] = parts[1]
  EVAL_DETAIL[task_count, eval_count] = parts[2]
  EVAL_METHOD[task_count, eval_count] = parts[3]
}

function finish_activity_row() {
  if (current_row == 0) return
  ROW_COUNT[task_count, group_count]++
  ACT_TITLE[task_count, group_count, ROW_COUNT[task_count, group_count]] = current_row_title
  ACT_HOURS[task_count, group_count, ROW_COUNT[task_count, group_count]] = current_row_hours
  ACT_LEARN[task_count, group_count, ROW_COUNT[task_count, group_count]] = current_row_learn
  ACT_STUDENT[task_count, group_count, ROW_COUNT[task_count, group_count]] = current_row_student
  ACT_TEACHER[task_count, group_count, ROW_COUNT[task_count, group_count]] = current_row_teacher
  ACT_METHOD[task_count, group_count, ROW_COUNT[task_count, group_count]] = current_row_method
  current_row = 0
  current_row_title = current_row_hours = ""
  current_row_learn = current_row_student = current_row_teacher = current_row_method = ""
  row_block = 0
}

function flush_body_line(line, key) {
  if (mode == "analysis" && current_analysis_key != "") {
    append_line(task_count SUBSEP current_analysis_key, line)
  } else if (mode == "activity" && current_row != 0) {
    key = ""
    if (row_block == 1) key = "current_row_learn"
    else if (row_block == 2) key = "current_row_student"
    else if (row_block == 3) key = "current_row_teacher"
    else if (row_block == 4) key = "current_row_method"
    if (key == "current_row_learn") {
      if (current_row_learn == "") current_row_learn = line
      else current_row_learn = current_row_learn "\n" line
    } else if (key == "current_row_student") {
      if (current_row_student == "") current_row_student = line
      else current_row_student = current_row_student "\n" line
    } else if (key == "current_row_teacher") {
      if (current_row_teacher == "") current_row_teacher = line
      else current_row_teacher = current_row_teacher "\n" line
    } else if (key == "current_row_method") {
      if (current_row_method == "") current_row_method = line
      else current_row_method = current_row_method "\n" line
    }
  }
}

function push_blank() {
  if (mode == "activity" && current_row != 0 && last_activity_was_blank == 0) {
    if (row_block < 4) row_block++
    last_activity_was_blank = 1
  }
}

function format_multiline(text,    out, lines, count, i, line) {
  count = split(text, lines, "\n")
  out = ""
  for (i = 1; i <= count; i++) {
    line = trim(lines[i])
    if (line == "") continue
    if (out != "") out = out "\n"
    out = out i ". " line "；"
  }
  return out
}

function max_int(a, b) {
  return (a > b) ? a : b
}

function ceil_int(value,    whole) {
  whole = int(value)
  return (value > whole) ? whole + 1 : whole
}

function nearly_equal(a, b) {
  return ((a - b < 0 ? b - a : a - b) < 0.000000001)
}

function display_width_line(text,    ascii, non_ascii, non_ascii_count) {
  ascii = text
  gsub(/[^ -~]/, "", ascii)
  non_ascii = text
  gsub(/[ -~]/, "", non_ascii)
  if (ENVIRON["LC_ALL"] == "C" || ENVIRON["LC_CTYPE"] == "C") {
    non_ascii_count = int((length(non_ascii) + 2) / 3)
  } else {
    non_ascii_count = length(non_ascii)
  }
  return length(ascii) + non_ascii_count * 2
}

function display_width(text,    lines, count, i, max_width) {
  count = split(text, lines, "\n")
  max_width = 0
  for (i = 1; i <= count; i++) {
    max_width = max_int(max_width, display_width_line(lines[i]))
  }
  return max_width
}

function content_pressure(text,    lines, count, i, total) {
  if (trim(text) == "") return 0
  count = split(text, lines, "\n")
  total = 0
  for (i = 1; i <= count; i++) {
    total += display_width(lines[i])
  }
  return total
}

function resource_available_units(width_cm,    units) {
  units = int((width_cm - 0.22) / 0.18)
  return (units < 1) ? 1 : units
}

function resource_wrapped_line_count(content, width_cm,    lines, count, units, i, line_width, total) {
  units = resource_available_units(width_cm)
  count = split(content, lines, "\n")
  total = 0
  for (i = 1; i <= count; i++) {
    line_width = max_int(display_width(lines[i]), 1)
    total += int((line_width + units - 1) / units)
  }
  return max_int(total, 1)
}

function resource_wrapped_line_load(content, width_cm,    lines, count, units, i, total) {
  units = resource_available_units(width_cm)
  count = split(content, lines, "\n")
  total = 0
  for (i = 1; i <= count; i++) {
    total += max_int(display_width(lines[i]), 1) / units
  }
  return total
}

function resource_column_spec(resource_text,    contents, min_widths, targets, weights, widths, count, i, total_min, total_weight, extra, step_cm, total_units, min_units, first, second, third, max_lines, total_lines, max_load, distance, delta, lines, load, best_max_load, best_max_lines, best_total_lines, best_distance, best_widths) {
  count = split(resource_text, contents, "\n\n")
  min_widths[1] = 3.2
  min_widths[2] = 2.6
  min_widths[3] = 2.2
  total_min = 0
  total_weight = 0
  for (i = 1; i <= 3; i++) {
    total_min += min_widths[i]
    weights[i] = sqrt(max_int(display_width(contents[i]), 1))
    total_weight += weights[i]
  }

  extra = 16.34 - total_min
  for (i = 1; i <= 3; i++) {
    targets[i] = min_widths[i]
    if (extra > 0 && total_weight != 0) {
      targets[i] += extra * weights[i] / total_weight
    }
    best_widths[i] = targets[i]
  }

  step_cm = 0.02
  total_units = int((16.34 / step_cm) + 0.5)
  for (i = 1; i <= 3; i++) {
    min_units[i] = ceil_int(min_widths[i] / step_cm)
  }

  best_max_load = 1.0e99
  best_max_lines = 2147483647
  best_total_lines = 2147483647
  best_distance = 1.0e99

  for (first = min_units[1]; first <= total_units - min_units[2] - min_units[3]; first++) {
    for (second = min_units[2]; second <= total_units - first - min_units[3]; second++) {
      third = total_units - first - second
      widths[1] = first * step_cm
      widths[2] = second * step_cm
      widths[3] = third * step_cm
      max_lines = 0
      total_lines = 0
      max_load = 0
      for (i = 1; i <= 3; i++) {
        lines = resource_wrapped_line_count(contents[i], widths[i])
        load = resource_wrapped_line_load(contents[i], widths[i])
        max_lines = max_int(max_lines, lines)
        total_lines += lines
        if (load > max_load) max_load = load
      }
      distance = 0
      for (i = 1; i <= 3; i++) {
        delta = widths[i] - targets[i]
        distance += delta * delta
      }
      if (max_load < best_max_load ||
          (nearly_equal(max_load, best_max_load) && max_lines < best_max_lines) ||
          (nearly_equal(max_load, best_max_load) && max_lines == best_max_lines && total_lines < best_total_lines) ||
          (nearly_equal(max_load, best_max_load) && max_lines == best_max_lines && total_lines == best_total_lines && distance < best_distance)) {
        for (i = 1; i <= 3; i++) best_widths[i] = widths[i]
        best_max_load = max_load
        best_max_lines = max_lines
        best_total_lines = total_lines
        best_distance = distance
      }
    }
  }

  return sprintf("%.2fcm, %.2fcm, %.2fcm", best_widths[1], best_widths[2], best_widths[3])
}

function header_min_width_cm(metric, bias) {
  return metric * 0.18 + 0.42 + bias
}

function table_columns_for_chapter(i, chapter,    widths, pressures, base_weights, pressure_scales, remaining_width, total_weight, g, r, col) {
  widths[1] = header_min_width_cm(max_int(display_width("教学活动"), display_width("学习环节")), 0.10)
  widths[2] = header_min_width_cm(display_width("学习内容"), 0.10)
  widths[3] = header_min_width_cm(display_width("学生活动"), 0.10)
  widths[4] = header_min_width_cm(display_width("教师活动"), 0.10)
  widths[5] = header_min_width_cm(display_width("教学方法与手段"), 0.14)
  widths[6] = header_min_width_cm(display_width("课时分配"), 0.10)

  remaining_width = 25.04
  for (col = 1; col <= 6; col++) remaining_width -= widths[col]
  if (remaining_width <= 0) {
    return sprintf("%.2fcm, %.2fcm, %.2fcm, %.2fcm, %.2fcm, %.2fcm", widths[1], widths[2], widths[3], widths[4], widths[5], widths[6])
  }

  pressures[1] = 1
  pressures[2] = 1
  pressures[3] = 1
  pressures[4] = 1
  pressures[5] = 0.5
  pressures[6] = 0.25
  for (g = 1; g <= GROUP_COUNT[i]; g++) {
    if (GROUP_CHAPTER[i, g] != chapter) continue
    pressures[1] += content_pressure(GROUP_STAGE[i, g]) * 0.2
    pressures[2] += content_pressure(GROUP_UNIT[i, g]) * 0.15
    for (r = 1; r <= ROW_COUNT[i, g]; r++) {
      pressures[1] += content_pressure(ACT_TITLE[i, g, r]) * 0.7
      pressures[2] += content_pressure(ACT_LEARN[i, g, r]) + 4
      pressures[3] += content_pressure(ACT_STUDENT[i, g, r]) + 4
      pressures[4] += content_pressure(ACT_TEACHER[i, g, r]) + 4
      pressures[5] += content_pressure(ACT_METHOD[i, g, r]) * 0.45
      pressures[6] += content_pressure(ACT_HOURS[i, g, r]) * 0.25
    }
  }

  base_weights[1] = 0.5
  base_weights[2] = 1.8
  base_weights[3] = 1.6
  base_weights[4] = 1.6
  base_weights[5] = 0.18
  base_weights[6] = 0.06
  pressure_scales[1] = 0.22
  pressure_scales[2] = 1.0
  pressure_scales[3] = 0.95
  pressure_scales[4] = 0.95
  pressure_scales[5] = 0.18
  pressure_scales[6] = 0.05

  total_weight = 0
  for (col = 1; col <= 6; col++) {
    weights[col] = base_weights[col] + pressure_scales[col] * sqrt(pressures[col] + 1)
    total_weight += weights[col]
  }
  if (total_weight == 0) {
    return sprintf("%.2fcm, %.2fcm, %.2fcm, %.2fcm, %.2fcm, %.2fcm", widths[1], widths[2], widths[3], widths[4], widths[5], widths[6])
  }

  for (col = 1; col <= 6; col++) {
    widths[col] += remaining_width * weights[col] / total_weight
  }
  return sprintf("%.2fcm, %.2fcm, %.2fcm, %.2fcm, %.2fcm, %.2fcm", widths[1], widths[2], widths[3], widths[4], widths[5], widths[6])
}

function emit_file(    i) {
  emit_prelude()
  emit_cover()
  for (i = 1; i <= task_count; i++) {
    emit_task_analysis(i)
    emit_activity_design(i)
    emit_evaluation(i)
  }
}

function emit_prelude() {
  author = meta["teacher_name"]
  if (trim(author) == "") author = "Presto"
  print "// 中文字号转换函数"
  print "#import \"@preview/pointless-size:0.1.2\": zh"
  print ""
  print "// 定义常用字体名称"
  print "#let FONT_XBS = (\"FZXiaoBiaoSong-B05\") // 方正小标宋"
  print "#let FONT_HEI = (\"STHeiti\") // 黑体"
  print "#let FONT_FS = (\"STFangsong\") // 仿宋"
  print "#let FONT_KAI = (\"STKaiti\") // 楷体"
  print "#let FONT_SONG = \"STSong\" // 宋体"
  print ""
  print "#set text("
  print "  lang: \"zh\","
  print "  font: FONT_SONG,"
  print "  size: zh(5),"
  print "  hyphenate: false,"
  print "  tracking: -0.3pt,"
  print "  cjk-latin-spacing: auto"
  print ")"
  print ""
  print "#let section-title(body) = block(above: 0pt, below: 0pt, width: 100%)["
  print "  #set text(font: FONT_SONG, size: zh(4))"
  print "  #align(center)[#body]"
  print "]"
  print ""
  print "#set document("
  print "  title: \"" meta["course_name"] "\","
  print "  author: \"" author "\","
  print "  keywords: \"教案, 实操, 教学设计\","
  print ")"
  emit_portrait_page()
  print ""
}

function emit_portrait_page() {
  print "#set page("
  print "  paper: \"a4\","
  print "  flipped: false,"
  print "  margin: (top: 2.54cm, bottom: 2.54cm, left: 2.58cm, right: 2.08cm)"
  print ")"
}

function emit_landscape_page() {
  print "#set page("
  print "  paper: \"a4\","
  print "  flipped: true,"
  print "  margin: (top: 2.54cm, bottom: 2.08cm, left: 2.58cm, right: 2.54cm)"
  print ")"
}

function emit_cover_label(label) {
  if (label == "课程名称：") {
    printf "%s", "      table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-label-width, height: 1.50cm, inset: (bottom: 0.16cm))[#align(bottom)[#box(width: cover-label-width)[#grid(columns: (auto, 1fr, auto, 1fr, auto, 1fr, auto, 1fr, auto), column-gutter: 0pt, [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[课]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[程]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[名]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[称]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[：]])]]]]"
  } else if (label == "课程属性：") {
    printf "%s", "      table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-label-width, height: 1.50cm, inset: (bottom: 0.16cm))[#align(bottom)[#box(width: cover-label-width)[#grid(columns: (auto, 1fr, auto, 1fr, auto, 1fr, auto, 1fr, auto), column-gutter: 0pt, [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[课]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[程]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[属]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[性]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[：]])]]]]"
  } else if (label == "教材名称：") {
    printf "%s", "      table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-label-width, height: 1.50cm, inset: (bottom: 0.16cm))[#align(bottom)[#box(width: cover-label-width)[#grid(columns: (auto, 1fr, auto, 1fr, auto, 1fr, auto, 1fr, auto), column-gutter: 0pt, [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[教]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[材]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[名]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[称]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[：]])]]]]"
  } else if (label == "教学班级：") {
    printf "%s", "      table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-label-width, height: 1.50cm, inset: (bottom: 0.16cm))[#align(bottom)[#box(width: cover-label-width)[#grid(columns: (auto, 1fr, auto, 1fr, auto, 1fr, auto, 1fr, auto), column-gutter: 0pt, [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[教]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[学]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[班]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[级]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[：]])]]]]"
  } else if (label == "计划总课时：") {
    printf "%s", "      table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-label-width, height: 1.50cm, inset: (bottom: 0.16cm))[#align(bottom)[#box(width: cover-label-width)[#grid(columns: (auto, 1fr, auto, 1fr, auto, 1fr, auto, 1fr, auto, 1fr, auto), column-gutter: 0pt, [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[计]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[划]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[总]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[课]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[时]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[：]])]]]]"
  } else if (label == "教师姓名：") {
    printf "%s", "      table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-label-width, height: 1.50cm, inset: (bottom: 0.16cm))[#align(bottom)[#box(width: cover-label-width)[#grid(columns: (auto, 1fr, auto, 1fr, auto, 1fr, auto, 1fr, auto), column-gutter: 0pt, [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[教]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[师]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[姓]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[名]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[：]])]]]]"
  } else if (label == "使用时间：") {
    printf "%s", "      table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-label-width, height: 1.50cm, inset: (bottom: 0.16cm))[#align(bottom)[#box(width: cover-label-width)[#grid(columns: (auto, 1fr, auto, 1fr, auto, 1fr, auto, 1fr, auto), column-gutter: 0pt, [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[使]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[用]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[时]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[间]], [], [#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[：]])]]]]"
  }
}

function emit_cover_row(comment, label, value) {
  print "      // cover-label: " comment
  emit_cover_label(label)
  print ", table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-value-width, height: 1.50cm, stroke: (bottom: 0.5pt), inset: (bottom: 0.16cm))[#align(center + bottom)[#text(font: FONT_SONG, size: zh(4), weight: \"bold\")[" value "]]]],"
}

function emit_cover() {
  print "#v(3.20cm)"
  print "#align(center)[#text(font: FONT_SONG, size: 22pt, weight: \"bold\")[教学设计方案（二）]]"
  print "#v(5.25cm)"
  print "#context {"
  print "  let cover-label-width = calc.max("
  print "    measure(text(font: FONT_SONG, size: zh(4), weight: \"bold\")[课程名称：]).width,"
  print "    measure(text(font: FONT_SONG, size: zh(4), weight: \"bold\")[课程属性：]).width,"
  print "    measure(text(font: FONT_SONG, size: zh(4), weight: \"bold\")[教材名称：]).width,"
  print "    measure(text(font: FONT_SONG, size: zh(4), weight: \"bold\")[教学班级：]).width,"
  print "    measure(text(font: FONT_SONG, size: zh(4), weight: \"bold\")[计划总课时：]).width,"
  print "    measure(text(font: FONT_SONG, size: zh(4), weight: \"bold\")[教师姓名：]).width,"
  print "    measure(text(font: FONT_SONG, size: zh(4), weight: \"bold\")[使用时间：]).width,"
  print "  )"
  print "  let cover-value-width = calc.max("
  print "    measure(text(font: FONT_SONG, size: zh(4), weight: \"bold\")[" meta["course_name"] "]).width,"
  print "    measure(text(font: FONT_SONG, size: zh(4), weight: \"bold\")[" normalize_course_attribute(meta["course_attribute"]) "]).width,"
  print "    measure(text(font: FONT_SONG, size: zh(4), weight: \"bold\")[" meta["textbook_name"] "]).width,"
  print "    measure(text(font: FONT_SONG, size: zh(4), weight: \"bold\")[" meta["class_name"] "]).width,"
  print "    measure(text(font: FONT_SONG, size: zh(4), weight: \"bold\")[" normalize_total_hours(meta["total_hours"]) "]).width,"
  print "    measure(text(font: FONT_SONG, size: zh(4), weight: \"bold\")[" meta["teacher_name"] "]).width,"
  print "    measure(text(font: FONT_SONG, size: zh(4), weight: \"bold\")[" normalize_use_time(meta["use_time"]) "]).width,"
  print "  ) + 0.90cm"
  print ""
  print "  align(center)["
  print "    #table("
  print "      columns: (cover-label-width, cover-value-width),"
  print "      stroke: none,"
  print "      align: bottom,"
  print "      inset: 0pt,"
  emit_cover_row("课程名称", "课程名称：", meta["course_name"])
  emit_cover_row("课程属性", "课程属性：", normalize_course_attribute(meta["course_attribute"]))
  emit_cover_row("教材名称", "教材名称：", meta["textbook_name"])
  emit_cover_row("教学班级", "教学班级：", meta["class_name"])
  emit_cover_row("计划总课时", "计划总课时：", normalize_total_hours(meta["total_hours"]))
  emit_cover_row("教师姓名", "教师姓名：", meta["teacher_name"])
  emit_cover_row("使用时间", "使用时间：", normalize_use_time(meta["use_time"]))
  print "    )"
  print "  ]"
  print "}"
  print ""
  print "#pagebreak()"
  print ""
}

function emit_task_analysis(i,    resource_cols, resources) {
  if (i == 1) emit_portrait_page()
  print ""
  print "#section-title[学习任务分析]"
  print "#v(10pt)"
  print "#align(center)["
  print "  #table("
  print "    columns: (2.2cm, 3.2cm, 2.2cm, 2.4cm, 3.1cm, 3.24cm),"
  print "    stroke: 0.5pt,"
  print "    align: center + horizon,"
  print "    [学习任务], table.cell(colspan: 5)[" TASK_TITLE[i] "],"
  print "    [课时], table.cell(colspan: 2)[" normalize_total_hours(meta["total_hours"]) "], [起止日期], table.cell(colspan: 2)[" TASK_DATE[i] "],"
  print "    table.cell(colspan: 6)[*一、学习任务描述*],"
  print "    table.cell(colspan: 6, align: left + horizon)[" DATA[i SUBSEP "desc"] "],"
  print "    table.cell(colspan: 6)[*二、学习目标*],"
  print "    table.cell(colspan: 6, align: left + horizon)[" DATA[i SUBSEP "goals"] "],"
  print "    table.cell(colspan: 6)[*三、学习内容*],"
  print "    table.cell(colspan: 6, align: left + horizon)[" DATA[i SUBSEP "content"] "],"
  print "    table.cell(colspan: 6)[*四、学生情况分析*],"
  print "    table.cell(colspan: 6, align: left + horizon)[" DATA[i SUBSEP "students"] "],"
  print "    table.cell(colspan: 6)[*五、学习资源*],"
  resource_cols = resource_column_spec(DATA[i SUBSEP "resources"])
  split(DATA[i SUBSEP "resources"], resources, "\n\n")
  print "    table.cell(colspan: 6, inset: 0pt, stroke: none)[#table("
  print "      columns: (" resource_cols "),"
  print "      stroke: 0.5pt,"
  print "      align: left + horizon,"
  print "      inset: 5pt,"
  print "      [" resources[1] "], [" resources[2] "], [" resources[3] "],"
  print "    )],"
  print "  )"
  print "]"
  print ""
  print "#pagebreak()"
  print ""
}

function emit_activity_design(i,    g) {
  emit_landscape_page()
  print ""
  print "#section-title[教学活动设计]"
  print "#v(10pt)"
  for (g = 1; g <= GROUP_COUNT[i]; g++) emit_activity_group(i, g)
  print ""
  print "#pagebreak()"
  print ""
}

function emit_activity_group(i, g,    r) {
  print "#block(above: 0pt, below: 0pt)["
  print "  #align(center)["
  print "    #table("
  print "      columns: (" table_columns_for_chapter(i, GROUP_CHAPTER[i, g]) "),"
  print "      stroke: 0.5pt,"
  print "      align: center + horizon,"
  print "      [*学习环节*], [*" GROUP_STAGE[i, g] "*], [*学习单元*], table.cell(colspan: 3)[*" GROUP_UNIT[i, g] "*],"
  print "      [教学活动], [学习内容], [学生活动], [教师活动], [教学方法与手段], [课时分配],"
  for (r = 1; r <= ROW_COUNT[i, g]; r++) {
    printf "      table.cell(rowspan: 1)[%d.%s],      align(left)[%s],      align(left)[%s],      align(left)[%s],      align(center + horizon)[%s],      [%s],\n", r, ACT_TITLE[i, g, r], format_multiline(ACT_LEARN[i, g, r]), format_multiline(ACT_STUDENT[i, g, r]), format_multiline(ACT_TEACHER[i, g, r]), ACT_METHOD[i, g, r], ACT_HOURS[i, g, r]
  }
  print "    )"
  print "  ]"
  print "]"
}

function emit_evaluation(i,    r) {
  emit_portrait_page()
  print ""
  print "#section-title[学业评价]"
  print "#v(10pt)"
  print "#align(center)["
  print "  #table("
  print "    columns: (1.2cm, 3.2cm, 8.6cm, 3.34cm),"
  print "    stroke: 0.5pt,"
  print "    align: center + horizon,"
  print "    [序号], [考核项目], [考核细则], [考核方式],"
  for (r = 1; r <= EVAL_COUNT[i]; r++) {
    print "    [" r "], align(center + horizon)[" EVAL_ITEM[i, r] "], align(center + horizon)[" EVAL_DETAIL[i, r] "], [" EVAL_METHOD[i, r] "],"
  }
  print "    [小结], table.cell(colspan: 3, align: left + horizon)[" EVAL_SUMMARY[i] "],"
  print "  )"
  print "]"
  if (i < task_count) {
    print ""
    print "#pagebreak()"
    print ""
  }
}

BEGIN {
  in_fm = 0
  mode = ""
  current_analysis_key = ""
  current_row = 0
  group_count = 0
  activity_chapter = 1
  last_activity_was_blank = 0
}

NR == 1 && $0 == "---" {
  in_fm = 1
  next
}

in_fm && $0 == "---" {
  in_fm = 0
  next
}

in_fm {
  if ($0 ~ /^[A-Za-z0-9_-]+:[[:space:]]*/) {
    key = $0
    sub(/:.*/, "", key)
    value = $0
    sub(/^[^:]+:[[:space:]]*/, "", value)
    meta[key] = strip_quotes(value)
  }
  next
}

{
  line = $0
  sub(/\r$/, "", line)

  if (line == "") {
    push_blank()
    next
  }

  if (line == "## 学习任务分析") {
    finish_activity_row()
    mode = "analysis"
    task_count++
    current_analysis_key = ""
    activity_chapter = 1
    next
  }

  if (line ~ /^学习任务：/) {
    TASK_TITLE[task_count] = line
    sub(/^学习任务：/, "", TASK_TITLE[task_count])
    next
  }

  if (line ~ /^课时：/) {
    TASK_HOURS[task_count] = line
    sub(/^课时：/, "", TASK_HOURS[task_count])
    next
  }

  if (line ~ /^起止日期：/) {
    TASK_DATE[task_count] = line
    sub(/^起止日期：/, "", TASK_DATE[task_count])
    next
  }

  if (line ~ /^### / && mode == "analysis") {
    title = line
    sub(/^### /, "", title)
    current_analysis_key = section_key(title)
    next
  }

  if (line ~ /^## 教学活动设计/) {
    finish_activity_row()
    mode = "activity"
    group_count = 0
    activity_chapter = 1
    GROUP_COUNT[task_count] = 0
    next
  }

  if (line == "{pagebreak}" && mode == "activity") {
    finish_activity_row()
    activity_chapter++
    last_activity_was_blank = 0
    next
  }

  if (line ~ /^### / && mode == "activity") {
    finish_activity_row()
    group_count++
    GROUP_COUNT[task_count] = group_count
    GROUP_CHAPTER[task_count, group_count] = activity_chapter
    title = line
    sub(/^### /, "", title)
    split(title, group_parts, "——")
    GROUP_STAGE[task_count, group_count] = group_parts[1]
    GROUP_UNIT[task_count, group_count] = group_parts[2]
    next
  }

  if (line ~ /^#### / && mode == "activity") {
    finish_activity_row()
    current_row = 1
    current_row_title = line
    sub(/^#### /, "", current_row_title)
    row_block = 0
    last_activity_was_blank = 0
    next
  }

  if (line ~ /^##### / && mode == "activity") {
    current_row_hours = line
    sub(/^##### /, "", current_row_hours)
    row_block = 0
    last_activity_was_blank = 0
    next
  }

  if (mode == "activity" && current_row != 0 && row_block == 0) {
    row_block = 1
  }

  if (line == "## 学业评价") {
    finish_activity_row()
    mode = "evaluation"
    eval_count = 0
    EVAL_COUNT[task_count] = 0
    next
  }

  if (mode == "evaluation" && line ~ /^[0-9]+\. /) {
    eval_count++
    EVAL_COUNT[task_count] = eval_count
    text = line
    sub(/^[0-9]+\. /, "", text)
    parse_eval_line(text)
    next
  }

  if (mode == "evaluation" && line ~ /^小结：/) {
    EVAL_SUMMARY[task_count] = line
    sub(/^小结：/, "", EVAL_SUMMARY[task_count])
    next
  }

  flush_body_line(line)
  last_activity_was_blank = 0
}

END {
  finish_activity_row()
  if (task_count != 3) {
    print "render_v110_typst.awk: expected 3 learning tasks, found " task_count > "/dev/stderr"
    exit 2
  }
  emit_file()
}
