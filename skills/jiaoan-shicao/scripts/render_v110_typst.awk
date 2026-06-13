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
  print "  author: \"" meta["teacher_name"] "\","
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
  resource_cols = (i == 1) ? "5.10cm, 6.16cm, 5.08cm" : "5.10cm, 6.34cm, 4.90cm"
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

function table_columns_for_task(i) {
  if (i == 1) return "2.43cm, 4.91cm, 6.24cm, 6.17cm, 3.31cm, 1.98cm"
  if (i == 2) return "2.46cm, 5.01cm, 6.16cm, 6.11cm, 3.31cm, 1.98cm"
  return "2.44cm, 4.92cm, 6.21cm, 6.17cm, 3.32cm, 1.98cm"
}

function emit_activity_group(i, g,    r) {
  print "#block(above: 0pt, below: 0pt)["
  print "  #align(center)["
  print "    #table("
  print "      columns: (" table_columns_for_task(i) "),"
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
    GROUP_COUNT[task_count] = 0
    next
  }

  if (line ~ /^### / && mode == "activity") {
    finish_activity_row()
    group_count++
    GROUP_COUNT[task_count] = group_count
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
