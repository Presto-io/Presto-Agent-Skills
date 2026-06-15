#!/usr/bin/env node
const fs = require('fs');

const modelPath = process.argv[2];
const typPath = process.argv[3];

if (!modelPath || !typPath) {
  console.error('usage: teaching-plan-renderer.js <model.json> <teaching-plan.typ>');
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

function compact(values) {
  const unique = [];
  for (const value of values) {
    if (!unique.includes(value)) unique.push(value);
  }
  return unique.map((value) => String(value)).join(' ');
}

function weekCell(row) {
  const values = (row.hour_consumption || []).map((item) => item.term_week);
  return compact(values);
}

function weekdayCell(row) {
  const values = (row.hour_consumption || []).map((item) => item.weekday_number);
  return compact(values);
}

function titleWeekRange() {
  const values = (model.scheduling.row_consumption_summary || [])
    .flatMap((row) => row.hour_consumption || [])
    .map((item) => item.term_week);
  if (!values.length) return model.scheduling.course.term_week;
  const min = Math.min(...values);
  const max = Math.max(...values);
  return min === max ? String(min) : `${min} - ${max}`;
}

const metadata = model.metadata;
const lines = [
  '// jiaoan-jihua official template',
  '// package-owned teaching-design-package migration; generated from shared scheduling model.',
  `// source_markdown: ${model.source_markdown}`,
  '// total_hours_source: teaching_plan_rows',
  '#import "@preview/cuti:0.2.1": show-cn-fakebold',
  '#show: show-cn-fakebold',
  '',
  '#set page(',
  '  paper: "a4",',
  '  flipped: false,',
  '  margin: (top: 2.54cm, bottom: 2.54cm, left: 2.8cm, right: 2.8cm)',
  ')',
  '',
  '#set text(',
  '  lang: "zh",',
  '  font: "STSong",',
  '  size: 10.5pt,',
  '  hyphenate: false,',
  ')',
  '',
  '#set par(justify: true, leading: 0.52em)',
  '',
  '#let cell-pad = (x: 4.8pt, y: 4.8pt)',
  '#let task-th(body) = table.cell(align: center + horizon, inset: cell-pad)[#text(weight: 700)[#body]]',
  '#let th(body) = table.cell(align: center + horizon, inset: cell-pad)[#body]',
  '#let subth(body) = table.cell(align: center + horizon, inset: cell-pad)[#body]',
  '#let body-cell(body) = table.cell(align: center + horizon, inset: cell-pad)[#body]',
  '#let content-cell(body) = table.cell(align: left + horizon, inset: cell-pad)[#body]',
  '',
  '#set document(',
  `  title: "授课进度计划表 ${typString(metadata.course_name)}",`,
  `  author: "${typString(metadata.teacher_name)}",`,
  '  keywords: "授课计划, 教学计划, 工学一体化",',
  ')',
  '',
  `#align(center)[#text(size: 14pt, weight: "bold")[${content(model.derived.term_label)}第${content(titleWeekRange())}周]]`,
  '#v(0.45em)',
  '#align(center)[#text(size: 14pt, weight: "bold")[工学一体化课程/基本技能课程授课进度计划表]]',
  '#v(0.72em)',
  '',
  '#text(size: 10.5pt)[',
  '  #grid(columns: (1fr, 1fr), row-gutter: 0.75em,',
  `    [专业名称：${content(metadata.major_name)}],`,
  `    [课程名称：${content(metadata.course_name)}],`,
  `    [授课教师：${content(metadata.teacher_name)}],`,
  `    [授课班级：${content(metadata.class_name)}],`,
  '  )',
  ']',
  '',
  '#v(0.9em)',
  '',
  '#align(center)[',
  '  #table(',
  '    columns: (3.15cm, 8.51cm, 1.12cm, 1.29cm, 1.27cm),',
  '    stroke: 0.5pt,',
  '    align: center + horizon,',
];

model.schedule.tasks.forEach((task, taskIndex) => {
  lines.push(
    `    task-th[学习任务${taskIndex + 1}名称：],`,
    `    task-th[${content(task.title)}],`,
    '    table.cell(colspan: 2, align: center + horizon, inset: cell-pad)[学时],',
    `    th[${task.total_hours}H],`,
    '',
  );

  if (taskIndex === 0) {
    lines.push(
      '    subth[],',
      '    subth[教学内容],',
      '    subth[周次],',
      '    subth[星期],',
      '    subth[学时],',
      '',
    );
  }

  task.stages.forEach((stage, stageIndex) => {
    stage.rows.forEach((row, rowIndex) => {
      if (rowIndex === 0) {
        lines.push(`    table.cell(rowspan: ${stage.rows.length}, align: center + horizon, inset: cell-pad)[学习环节${stageIndex + 1}名称：${content(stage.title)}],`);
      }
      lines.push(
        `    content-cell[${content(row.title)}],`,
        `    body-cell[${content(weekCell(row))}],`,
        `    body-cell[${content(weekdayCell(row))}],`,
        `    body-cell[${row.hours}],`,
        '',
      );
    });
  });
});

lines.push(
  '  )',
  ']',
  '',
  '#v(1.1em)',
  '#grid(columns: (1fr, 1fr, 1fr),',
  '  [#align(center)[系主任：]],',
  '  [#align(center)[教研室主任：]],',
  `  [#align(center)[制表：${content(metadata.teacher_name)}]],`,
  ')',
  '',
);

fs.writeFileSync(typPath, lines.join('\n'));
