#!/usr/bin/env node
const fs = require('fs');

const modelPath = process.argv[2];
const typPath = process.argv[3];

if (!modelPath || !typPath) {
  console.error('usage: teaching-design-renderer.js <model.json> <teaching-design.typ>');
  process.exit(1);
}

const model = JSON.parse(fs.readFileSync(modelPath, 'utf8'));

function typString(value) {
  return String(value ?? '').replace(/\\/g, '\\\\').replace(/"/g, '\\"');
}

function content(value) {
  return String(value ?? '')
    .replace(/\\/g, '\\\\')
    .replace(/\[/g, '\\[')
    .replace(/\]/g, '\\]')
    .replace(/#/g, '\\#')
    .replace(/\$/g, '\\$')
    .replace(/%/g, '\\%')
    .replace(/&/g, '\\&');
}

function normalizeCourseAttribute(value) {
  if (value === '工学一体化课程' || value === '一体化') return '□基本技能课程  ☑工学一体化课程';
  if (value === '基本技能课程') return '☑基本技能课程  □工学一体化课程';
  return value;
}

function hourLabel(value) {
  const text = String(value ?? '').trim();
  if (!text) return '';
  return /[Hh]$/.test(text) ? text.replace(/h$/, 'H') : `${text}H`;
}

function normalizeUseTime(value) {
  return String(value ?? '').replace(/--/g, '——').replace(/-/g, '——');
}

function paragraph(value) {
  return content(String(value ?? '').trim());
}

function resourceCells(text) {
  const parts = String(text ?? '').split(/\n/).map((line) => line.trim()).filter(Boolean);
  return [parts[0] || '', parts[1] || '', parts.slice(2).join('\n') || ''];
}

function lineList(text) {
  const lines = String(text ?? '').split(/\n/).map((line) => line.trim()).filter(Boolean);
  if (!lines.length) return '';
  return lines.map((line, index) => `${index + 1}. ${content(line)}；`).join('\n');
}

function methodLines(text) {
  const lines = String(text ?? '').split(/\n/).map((line) => line.trim()).filter(Boolean);
  return lines.map(content).join(' #linebreak() ');
}

function displayWidth(text) {
  let width = 0;
  for (const char of String(text ?? '')) width += char.charCodeAt(0) <= 0x7f ? 1 : 2;
  return width;
}

function headerMinWidth(text, bias) {
  return displayWidth(text) * 0.18 + 0.42 + bias;
}

function contentPressure(text) {
  const lines = String(text ?? '').split(/\n/).filter((line) => line.trim());
  if (!lines.length) return 0;
  return lines.reduce((sum, line) => sum + displayWidth(line), 0);
}

function tableColumnsForChapter(task, chapter) {
  const widths = [
    headerMinWidth('教学活动', 0.1),
    headerMinWidth('学习内容', 0.1),
    headerMinWidth('学生活动', 0.1),
    headerMinWidth('教师活动', 0.1),
    headerMinWidth('教学方法与手段', 0.14),
    headerMinWidth('课时分配', 0.1),
  ];
  const pressures = [1, 1, 1, 1, 0.5, 0.25];
  for (const stage of task.activity_block.stages) {
    for (const activity of stage.activities) {
      if (activity.chapter !== chapter) continue;
      pressures[0] += contentPressure(activity.title) * 0.7 + contentPressure(stage.title) * 0.2;
      pressures[1] += contentPressure(activity.learning_content) + 4;
      pressures[2] += contentPressure(activity.student_activity) + 4;
      pressures[3] += contentPressure(activity.teacher_activity) + 4;
      pressures[4] += contentPressure(activity.method) * 0.45;
      pressures[5] += contentPressure(activity.hour_label) * 0.25;
    }
  }
  let remaining = 25.04 - widths.reduce((sum, value) => sum + value, 0);
  if (remaining <= 0) return widths.map((value) => `${value.toFixed(2)}cm`).join(', ');
  const baseWeights = [0.5, 1.8, 1.6, 1.6, 0.18, 0.06];
  const pressureScales = [0.22, 1.0, 0.95, 0.95, 0.18, 0.05];
  const weights = pressures.map((pressure, index) => baseWeights[index] + pressureScales[index] * Math.sqrt(pressure + 1));
  const totalWeight = weights.reduce((sum, value) => sum + value, 0);
  for (let index = 0; index < widths.length; index += 1) widths[index] += remaining * weights[index] / totalWeight;
  return widths.map((value) => `${value.toFixed(2)}cm`).join(', ');
}

function emitPrelude(lines) {
  const metadata = model.metadata;
  lines.push(
    '// 中文字号转换函数',
    '#import "@preview/pointless-size:0.1.2": zh',
    '',
    '// Package-owned teaching-design-package migration; generated from shared scheduling model.',
    `// source_markdown: ${model.source_markdown}`,
    '// total_hours_source: teaching_plan_rows',
    '// task_hours_source: schedule.tasks[].total_hours',
    '// activity_hours_source: schedule.tasks[].stages[].rows[].hours',
    '// activity_table_total_width: 25.04cm',
    `// course_attribute: ${metadata.course_attribute}`,
    `// total_hours: ${model.derived.total_hours_label}`,
    `// use_time: ${model.derived.use_time}`,
    '',
    '// 定义常用字体名称',
    '#let FONT_XBS = ("FZXiaoBiaoSong-B05") // 方正小标宋',
    '#let FONT_HEI = ("STHeiti") // 黑体',
    '#let FONT_FS = ("STFangsong") // 仿宋',
    '#let FONT_KAI = ("STKaiti") // 楷体',
    '#let FONT_SONG = "STSong" // 宋体',
    '',
    '#set text(',
    '  lang: "zh",',
    '  font: FONT_SONG,',
    '  size: zh(5),',
    '  hyphenate: false,',
    '  tracking: -0.3pt,',
    '  cjk-latin-spacing: auto',
    ')',
    '',
    '#let section-title(body) = block(above: 0pt, below: 0pt, width: 100%)[',
    '  #set text(font: FONT_SONG, size: zh(4))',
    '  #align(center)[#body]',
    ']',
    '',
    '#set document(',
    `  title: "${typString(metadata.course_name)}",`,
    `  author: "${typString(metadata.teacher_name || 'Presto')}",`,
    '  keywords: "教案, 实操, 教学设计",',
    ')',
  );
  emitPortraitPage(lines);
}

function emitPortraitPage(lines) {
  lines.push(
    '#set page(',
    '  paper: "a4",',
    '  flipped: false,',
    '  margin: (top: 2.54cm, bottom: 2.54cm, left: 2.58cm, right: 2.08cm)',
    ')',
    '',
  );
}

function emitLandscapePage(lines) {
  lines.push(
    '#set page(',
    '  paper: "a4",',
    '  flipped: true,',
    '  margin: (top: 2.54cm, bottom: 2.08cm, left: 2.58cm, right: 2.54cm)',
    ')',
    '',
  );
}

function emitCover(lines) {
  const metadata = model.metadata;
  const totalHours = hourLabel(model.derived.total_hours_label);
  lines.push(
    '#v(3.20cm)',
    '#align(center)[#text(font: FONT_SONG, size: 22pt, weight: "bold")[教学设计方案（二）]]',
    '#v(5.25cm)',
    '#context {',
    '  let cover-label-width = calc.max(',
    '    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[课程名称：]).width,',
    '    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[课程属性：]).width,',
    '    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[教材名称：]).width,',
    '    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[教学班级：]).width,',
    '    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[计划总课时：]).width,',
    '    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[教师姓名：]).width,',
    '    measure(text(font: FONT_SONG, size: zh(4), weight: "bold")[使用时间：]).width,',
    '  )',
    '  let cover-value-width = 10cm',
    '  align(center)[',
    '    #table(',
    '      columns: (cover-label-width, cover-value-width),',
    '      stroke: none,',
    '      align: bottom,',
    '      inset: 0pt,',
  );
  const rows = [
    ['课程名称', metadata.course_name],
    ['课程属性', normalizeCourseAttribute(metadata.course_attribute)],
    ['教材名称', metadata.textbook_name],
    ['教学班级', metadata.class_name],
    ['计划总课时', totalHours],
    ['教师姓名', metadata.teacher_name],
    ['使用时间', normalizeUseTime(model.derived.use_time)],
  ];
  for (const [label, value] of rows) {
    lines.push(
      `      // cover-label: ${label}`,
      `      ${coverLabelCell(label)}, table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-value-width, height: 1.50cm, stroke: (bottom: 0.5pt), inset: (bottom: 0.16cm))[#align(center + bottom)[#text(font: FONT_SONG, size: zh(4), weight: "bold")[${content(value)}]]]],`,
    );
  }
  lines.push('    )', '  ]', '}', '', '#pagebreak()', '');
}

function coverLabelCell(label) {
  const chars = Array.from(`${label}：`);
  const columns = Array(chars.length * 2 - 1).fill(0).map((_, index) => (index % 2 === 0 ? 'auto' : '1fr')).join(', ');
  const cells = chars.flatMap((char, index) => {
    const text = `[#text(font: FONT_SONG, size: zh(4), weight: "bold")[${content(char)}]]`;
    return index === chars.length - 1 ? [text] : [text, '[]'];
  }).join(', ');
  return `table.cell(stroke: (left: 0pt, right: 0pt, top: 0pt, bottom: 0pt))[#box(width: cover-label-width, height: 1.50cm, inset: (bottom: 0.16cm))[#align(bottom)[#box(width: cover-label-width)[#grid(columns: (${columns}), column-gutter: 0pt, ${cells})]]]]`;
}

function emitTaskAnalysis(lines, task, index) {
  if (index === 0) emitPortraitPage(lines);
  const sections = task.analysis_block.sections;
  const resources = resourceCells(sections.resources);
  lines.push(
    '',
    '#section-title[学习任务分析]',
    '#v(10pt)',
    '#align(center)[',
    '  #table(',
    '    columns: (2.2cm, 3.2cm, 2.2cm, 2.4cm, 3.1cm, 3.24cm),',
    '    stroke: 0.5pt,',
    '    align: center + horizon,',
    `    [学习任务], table.cell(colspan: 5)[${content(task.title)}],`,
    `    [课时], table.cell(colspan: 2)[${hourLabel(task.derived_total_hours)}], [起止日期], table.cell(colspan: 2)[${content(task.date_range)}],`,
    '    table.cell(colspan: 6)[*一、学习任务描述*],',
    `    table.cell(colspan: 6, align: left + horizon)[${paragraph(sections.description)}],`,
    '    table.cell(colspan: 6)[*二、学习目标*],',
    `    table.cell(colspan: 6, align: left + horizon)[${paragraph(sections.goals)}],`,
    '    table.cell(colspan: 6)[*三、学习内容*],',
    `    table.cell(colspan: 6, align: left + horizon)[${paragraph(sections.content)}],`,
    '    table.cell(colspan: 6)[*四、学生情况分析*],',
    `    table.cell(colspan: 6, align: left + horizon)[${paragraph(sections.students)}],`,
    '    table.cell(colspan: 6)[*五、学习资源*],',
    '    table.cell(colspan: 6, inset: 0pt, stroke: none)[#table(',
    '      columns: (5.10cm, 6.16cm, 5.08cm),',
    '      stroke: 0.5pt,',
    '      align: left + horizon,',
    '      inset: 5pt,',
    `      [${paragraph(resources[0])}], [${paragraph(resources[1])}], [${paragraph(resources[2])}],`,
    '    )],',
    '  )',
    ']',
    '',
    '#pagebreak()',
    '',
  );
}

function emitActivityDesign(lines, task) {
  emitLandscapePage(lines);
  lines.push('', '#section-title[教学活动设计]', '#v(10pt)');
  for (const stage of task.activity_block.stages) emitActivityStage(lines, task, stage);
  lines.push('', '#pagebreak()', '');
}

function emitActivityStage(lines, task, stage) {
  lines.push(
    '#block(above: 0pt, below: 0pt)[',
    '  #align(center)[',
    '    #table(',
    `      columns: (${tableColumnsForChapter(task, stage.chapter)}),`,
    '      stroke: 0.5pt,',
    '      align: center + horizon,',
    `      [*学习环节*], [*${content(stage.title)}*], [*学习单元*], table.cell(colspan: 3)[*${content(stage.unit || task.title)}*],`,
    '      [教学活动], [学习内容], [学生活动], [教师活动], [教学方法与手段], [课时分配],',
  );
  stage.activities.forEach((activity, index) => {
    lines.push(
      `      table.cell(rowspan: 1)[${index + 1}.${content(activity.title)}],      align(left)[${lineList(activity.learning_content)}],      align(left)[${lineList(activity.student_activity)}],      align(left)[${lineList(activity.teacher_activity)}],      align(center + horizon)[${methodLines(activity.method)}],      [${activity.hour_label}],`,
    );
  });
  lines.push('    )', '  ]', ']');
}

function emitEvaluation(lines, task, index, count) {
  emitPortraitPage(lines);
  lines.push(
    '',
    '#section-title[学业评价]',
    '#v(10pt)',
    '#align(center)[',
    '  #table(',
    '    columns: (1.2cm, 3.2cm, 8.6cm, 3.34cm),',
    '    stroke: 0.5pt,',
    '    align: center + horizon,',
    '    [序号], [考核项目], [考核细则], [考核方式],',
  );
  for (const item of task.evaluation_block.items) {
    lines.push(`    [${item.number}], align(center + horizon)[${content(item.item)}], align(center + horizon)[${content(item.detail)}], [${content(item.method)}],`);
  }
  lines.push(
    `    [小结], table.cell(colspan: 3, align: left + horizon)[${paragraph(task.evaluation_block.summary)}],`,
    '  )',
    ']',
  );
  if (index < count - 1) lines.push('', '#pagebreak()', '');
}

const lines = [];
emitPrelude(lines);
emitCover(lines);
model.teaching_design.tasks.forEach((task, index) => {
  emitTaskAnalysis(lines, task, index);
  emitActivityDesign(lines, task);
  emitEvaluation(lines, task, index, model.teaching_design.tasks.length);
});

fs.writeFileSync(typPath, lines.join('\n'));
