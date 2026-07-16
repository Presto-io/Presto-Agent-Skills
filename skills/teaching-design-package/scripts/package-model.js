#!/usr/bin/env node
const fs = require('fs');
const crypto = require('crypto');

const inputPath = process.argv[2];
const dailyHours = Number(process.argv[3] || 8);
const calendarPath = process.argv[4];

const MODULE_REGISTRY = [
  {
    id: 'teaching-plan',
    display_name: '授课进度计划表',
    order: 1,
    work_markdown: 'evidence/modules/teaching-plan.md',
    work_typst: 'evidence/modules/teaching-plan.typ',
    pdf_filename: 'teaching-plan.pdf',
    public_pdf_suffix: '授课进度计划表',
  },
  {
    id: 'teaching-design',
    display_name: '教学设计方案',
    order: 2,
    work_markdown: 'evidence/modules/teaching-design.md',
    work_typst: 'evidence/modules/teaching-design.typ',
    pdf_filename: 'teaching-design.pdf',
    public_pdf_suffix: '教学设计方案',
  },
];

const ALLOWED_FRONTMATTER = new Set([
  'course_name',
  'major_name',
  'course_attribute',
  'textbook_name',
  'class_name',
  'teachers',
  'first_teaching_day',
]);

const FORBIDDEN_FRONTMATTER = new Set([
  'daily_hours',
  'total_hours',
  'school_year',
  'semester',
  'start_date',
  'end_date',
  'date_range',
  'calendar_policy',
  'calendar_source',
  'outputs',
  'validation',
  'status',
  'manifest',
  'output_readiness',
  'final_ready',
  'pdf_ready',
  'typst_ready',
]);

function fail(code, message, extra = {}) {
  const diagnostic = { code, message, ...extra };
  console.error(`teaching-design-package.sh: ${code}: ${message}`);
  console.error(`TDPKG_DIAGNOSTIC_JSON=${JSON.stringify(diagnostic)}`);
  process.exit(1);
}

function stripQuotes(value) {
  const trimmed = String(value ?? '').trim();
  if ((trimmed.startsWith('"') && trimmed.endsWith('"')) || (trimmed.startsWith("'") && trimmed.endsWith("'"))) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

function safeCourseFilenamePrefix(courseName) {
  const raw = String(courseName ?? '');
  const trimmed = raw.trim();
  const rejected = (code, message, extra = {}) => fail('invalid_course_name_for_filename', message, {
    source_markdown: inputPath,
    rejected_course_name: raw,
    sanitized_course_name: trimmed,
    reason: code,
    ...extra,
  });
  if (!trimmed) rejected('empty_after_trim', 'course_name is required for public delivery filenames');
  if (/[\/\\]/.test(trimmed)) rejected('path_separator', 'course_name must not contain path separators');
  if (/[\u0000-\u001f\u007f]/.test(trimmed)) rejected('control_character', 'course_name must not contain control characters');
  if (trimmed.includes('..')) rejected('path_traversal', 'course_name must not contain path traversal markers');
  if (/[<>:"|?*$`]/.test(trimmed)) rejected('hostile_character', 'course_name contains characters that are unsafe for public filenames');
  if (trimmed === '.' || trimmed === '..') rejected('relative_path_marker', 'course_name must not be a relative path marker');
  return trimmed;
}

function buildPublicDelivery(metadata) {
  const prefix = safeCourseFilenamePrefix(metadata.course_name);
  const modulePdfs = MODULE_REGISTRY.map((entry) => ({
    module_id: entry.id,
    display_name: entry.display_name,
    order: entry.order,
    public_pdf_suffix: entry.public_pdf_suffix || entry.display_name,
    public_pdf_filename: `${prefix}${entry.public_pdf_suffix || entry.display_name}.pdf`,
  }));
  return {
    course_name: metadata.course_name,
    filename_prefix: prefix,
    contract: 'course-name-prefixed-1+1+N',
    current_n: modulePdfs.length,
    public_markdown_filename: `${prefix}教学资料.md`,
    public_package_pdf_filename: `${prefix}教学资料.pdf`,
    module_pdfs: modulePdfs,
    expected_public_filenames: [
      `${prefix}教学资料.md`,
      `${prefix}教学资料.pdf`,
      ...modulePdfs.map((item) => item.public_pdf_filename),
    ],
    work_layout: {
      candidate: 'candidate',
      rollback: 'rollback',
      evidence: 'evidence',
    },
  };
}

function splitFrontmatter(markdown) {
  const match = markdown.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!match) fail('invalid_frontmatter', 'frontmatter is required');
  return { frontmatter: match[1], body: markdown.slice(match[0].length) };
}

function parseFrontmatter(frontmatter) {
  const data = {};
  let currentListKey = '';
  for (const rawLine of frontmatter.split(/\n/)) {
    const line = rawLine.trimEnd();
    if (!line.trim() || line.trim().startsWith('#')) continue;
    const item = line.match(/^\s*-\s*(.*)$/);
    if (item && currentListKey) {
      data[currentListKey].push(stripQuotes(item[1]));
      continue;
    }
    const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!match) fail('invalid_frontmatter', `unsupported frontmatter line: ${line}`);
    const key = match[1];
    const value = match[2];
    if (FORBIDDEN_FRONTMATTER.has(key)) {
      fail('forbidden_derived_frontmatter', `package frontmatter must not own derived field: ${key}`, { key });
    }
    if (!ALLOWED_FRONTMATTER.has(key)) {
      fail('invalid_frontmatter', `unsupported package frontmatter key: ${key}`, { key });
    }
    if (value === '') {
      data[key] = [];
      currentListKey = key;
      continue;
    }
    data[key] = stripQuotes(value);
    currentListKey = '';
  }
  for (const key of ALLOWED_FRONTMATTER) {
    if (!(key in data)) {
      if (key === 'course_name') {
        fail('invalid_course_name_for_filename', 'course_name is required for public delivery filenames', {
          source_markdown: inputPath,
          rejected_course_name: null,
          sanitized_course_name: '',
          reason: 'missing_course_name',
          key,
        });
      }
      fail('invalid_frontmatter', `missing required frontmatter key: ${key}`, { key });
    }
  }
  if (!Array.isArray(data.teachers) || !data.teachers.length) {
    fail('invalid_frontmatter', 'teachers must be a non-empty YAML list');
  }
  return data;
}

function isoDate(value, label = 'date') {
  if (!/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(value)) {
    fail('invalid_date', `${label} must be YYYY-MM-DD: ${value}`, { value });
  }
  const parsed = new Date(`${value}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== value) {
    fail('invalid_date', `${label} is not a valid calendar date: ${value}`, { value });
  }
  return parsed;
}

function labelDate(date) {
  const match = date.match(/^[0-9]{4}-([0-9]{2})-([0-9]{2})$/);
  if (!match) return date;
  return `${Number(match[1])}月${Number(match[2])}日`;
}

function dateRangeLabel(start, end) {
  return `${labelDate(start)}--${labelDate(end)}`;
}

function weekdayNumber(date) {
  const value = isoDate(date).getUTCDay();
  return value === 0 ? 7 : value;
}

function weekdayName(date) {
  return ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][isoDate(date).getUTCDay()];
}

function inferTerm(scheduledStartDate) {
  const match = scheduledStartDate.match(/^([0-9]{4})-([0-9]{2})-[0-9]{2}$/);
  if (!match) fail('invalid_date', `invalid scheduled start date: ${scheduledStartDate}`, { start_date: scheduledStartDate });
  const year = Number(match[1]);
  const month = Number(match[2]);
  if (month >= 9) return { school_year: `${year}-${year + 1}学年`, semester: '第一学期' };
  return { school_year: `${year - 1}-${year}学年`, semester: '第二学期' };
}

function extractSection(markdown, heading, nextHeading) {
  const start = markdown.match(new RegExp(`^# ${heading}$`, 'm'));
  if (!start) fail('missing_section', `missing # ${heading}`, { section: heading });
  const startIndex = start.index + start[0].length;
  const rest = markdown.slice(startIndex);
  const end = nextHeading ? rest.match(new RegExp(`\\n# ${nextHeading}$`, 'm')) : null;
  return (end ? rest.slice(0, end.index) : rest).replace(/^\n+|\n+$/g, '');
}

function parsePlanRows(planText) {
  const tasks = [];
  let currentTask = null;
  let currentStage = null;
  let taskIndex = 0;
  let stageIndex = 0;
  let rowIndex = 0;
  for (const line of planText.split(/\n/)) {
    const taskMatch = line.match(/^##\s+(.+)$/);
    if (taskMatch) {
      const title = taskMatch[1].trim();
      if (!title) fail('malformed_schedule_row', 'learning task title is empty');
      taskIndex += 1;
      stageIndex = 0;
      rowIndex = 0;
      currentTask = { source: `task:${taskIndex}`, title, stages: [], rows: [], total_hours: 0 };
      tasks.push(currentTask);
      currentStage = null;
      continue;
    }
    const stageMatch = line.match(/^###\s+(.+)$/);
    if (stageMatch) {
      if (!currentTask) fail('malformed_schedule_row', `stage appears before any task: ${line}`, { line });
      const title = stageMatch[1].trim();
      if (!title) fail('malformed_schedule_row', 'learning stage title is empty');
      stageIndex += 1;
      rowIndex = 0;
      currentStage = { source: `task:${taskIndex}/stage:${stageIndex}`, title, rows: [], total_hours: 0 };
      currentTask.stages.push(currentStage);
      continue;
    }
    const content = line.trim();
    if (!content) continue;
    if (!currentTask) fail('malformed_schedule_row', `content appears before any task: ${content}`, { line: content });
    if (!currentStage) fail('malformed_schedule_row', `content appears before any stage: ${content}`, { line: content, task: currentTask.title });
    const rowMatch = content.match(/^(.+)-([0-9]+)$/);
    if (!rowMatch) fail('malformed_schedule_row', `malformed row hours, expected text-N: ${content}`, { line: content });
    const title = rowMatch[1].trim();
    const hours = Number(rowMatch[2]);
    if (!title) fail('malformed_schedule_row', `empty content before hour suffix: ${content}`, { line: content });
    if (!Number.isInteger(hours) || hours <= 0) fail('non_positive_hours', `row hours must be a positive integer: ${content}`, { line: content });
    rowIndex += 1;
    const row = {
      source: `task:${taskIndex}/stage:${stageIndex}/row:${rowIndex}`,
      title,
      hours,
      assigned_hours: hours,
      task_title: currentTask.title,
      stage_title: currentStage.title,
    };
    currentStage.rows.push(row);
    currentStage.total_hours += row.hours;
    currentTask.rows.push(row);
    currentTask.total_hours += row.hours;
  }
  if (!tasks.length) fail('missing_section', 'no schedule tasks found', { section: '授课进度计划' });
  for (const task of tasks) {
    if (!task.stages.length) fail('malformed_schedule_row', `schedule task has no stages: ${task.title}`, { task: task.title });
    if (!task.rows.length) fail('malformed_schedule_row', `schedule task has no hour rows: ${task.title}`, { task: task.title });
    for (const stage of task.stages) {
      if (!stage.rows.length) fail('malformed_schedule_row', `schedule stage has no hour rows: ${stage.title}`, { task: task.title, stage: stage.title });
    }
  }
  return tasks;
}

function loadCalendar(calendarFile) {
  let raw = '';
  try {
    raw = fs.readFileSync(calendarFile, 'utf8');
  } catch (error) {
    fail('missing_calendar_resource', `calendar resource missing: ${calendarFile}`, { calendar_path: calendarFile });
  }
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (error) {
    fail('invalid_calendar_json', `calendar is not valid JSON: ${error.message}`, { calendar_path: calendarFile });
  }
  const dates = Array.isArray(parsed) ? parsed : parsed && Array.isArray(parsed.dates) ? parsed.dates : null;
  if (!dates || !dates.length) fail('invalid_calendar_json', 'calendar must be a non-empty array of YYYY-MM-DD strings or expose dates[]', { calendar_path: calendarFile });
  const seen = new Set();
  let previous = '';
  for (const item of dates) {
    if (typeof item !== 'string' || !/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(item)) {
      fail('invalid_calendar_json', `calendar entry is not a YYYY-MM-DD string: ${String(item)}`, { calendar_path: calendarFile, entry: item });
    }
    isoDate(item, 'calendar entry');
    if (seen.has(item)) fail('invalid_calendar_json', `calendar contains duplicate date: ${item}`, { calendar_path: calendarFile, entry: item });
    if (previous && item <= previous) fail('invalid_calendar_json', `calendar dates must be strictly ordered: ${previous} then ${item}`, { calendar_path: calendarFile });
    seen.add(item);
    previous = item;
  }
  return {
    dates,
    sha256: crypto.createHash('sha256').update(raw).digest('hex'),
    schema: Array.isArray(parsed) ? 'array' : 'object.dates',
    path: calendarFile,
  };
}

function weekStartFor(dateText) {
  const parsed = isoDate(dateText);
  const copy = new Date(parsed.getTime());
  copy.setUTCDate(copy.getUTCDate() - (weekdayNumber(dateText) - 1));
  return copy.toISOString().slice(0, 10);
}

function daysBetween(startDate, endDate) {
  return Math.floor((isoDate(endDate).getTime() - isoDate(startDate).getTime()) / 86400000);
}

function termWeekFor(dateText, termWeekStart) {
  return Math.floor(daysBetween(termWeekStart, dateText) / 7) + 1;
}

function compactRange(values) {
  const unique = [];
  for (const value of values) {
    if (!unique.includes(value)) unique.push(value);
  }
  if (unique.length === 1) return unique[0];
  return `${unique[0]}-${unique[unique.length - 1]}`;
}

function applyRangeFromRows(target, rows) {
  const firstRow = rows[0];
  const lastRow = rows[rows.length - 1];
  const weeks = rows.flatMap((row) => row.hour_consumption.map((item) => item.term_week));
  const weekdays = rows.flatMap((row) => row.hour_consumption.map((item) => item.weekday));
  target.start_date = firstRow.start_date;
  target.end_date = lastRow.end_date;
  target.date_range = dateRangeLabel(target.start_date, target.end_date);
  target.use_time = target.date_range;
  target.term_week = compactRange(weeks);
  target.weekday = compactRange(weekdays);
}

function applyRangeFromConsumption(target) {
  const consumption = target.hour_consumption;
  const first = consumption[0];
  const last = consumption[consumption.length - 1];
  target.start_date = first.date;
  target.end_date = last.date;
  target.date_range = dateRangeLabel(target.start_date, target.end_date);
  target.use_time = target.date_range;
  target.term_week = compactRange(consumption.map((item) => item.term_week));
  target.weekday = compactRange(consumption.map((item) => item.weekday));
}

function assignSchedule(tasks, calendar, firstTeachingDay) {
  if (!Number.isInteger(dailyHours) || dailyHours <= 0) fail('non_positive_hours', `daily_hours must be a positive integer: ${dailyHours}`);
  const firstIndex = calendar.dates.indexOf(firstTeachingDay);
  if (firstIndex < 0) {
    fail('first_day_not_found', `first_teaching_day not found in calendar: ${firstTeachingDay}`, { first_teaching_day: firstTeachingDay, calendar_path: calendar.path });
  }
  const termWeekStart = weekStartFor(calendar.dates[0]);
  let currentIndex = firstIndex;
  let remainingDailyCapacity = dailyHours;
  const rowSummaries = [];

  for (const task of tasks) {
    for (const stage of task.stages) {
      for (const row of stage.rows) {
        let left = row.hours;
        row.hour_consumption = [];
        while (left > 0) {
          if (currentIndex >= calendar.dates.length) {
            fail('calendar_exhausted', 'calendar ended before all row hours were assigned', { source: row.source, title: row.title });
          }
          const currentDate = calendar.dates[currentIndex];
          const consumedHours = Math.min(left, remainingDailyCapacity);
          left -= consumedHours;
          remainingDailyCapacity -= consumedHours;
          const evidence = {
            date: currentDate,
            weekday: weekdayName(currentDate),
            weekday_number: weekdayNumber(currentDate),
            term_week: termWeekFor(currentDate, termWeekStart),
            consumed_hours: consumedHours,
            remaining_daily_capacity: remainingDailyCapacity,
            source: row.source,
          };
          row.hour_consumption.push(evidence);
          if (remainingDailyCapacity === 0) {
            currentIndex += 1;
            remainingDailyCapacity = dailyHours;
          }
        }
        applyRangeFromConsumption(row);
        row.assigned_hours = row.hours;
        row.consumption = row.hour_consumption.map((item) => ({
          date: item.date,
          weekday: item.weekday,
          hours: item.consumed_hours,
        }));
        rowSummaries.push({
          source: row.source,
          title: row.title,
          assigned_hours: row.assigned_hours,
          start_date: row.start_date,
          end_date: row.end_date,
          term_week: row.term_week,
          weekday: row.weekday,
          hour_consumption: row.hour_consumption,
        });
      }
      applyRangeFromRows(stage, stage.rows);
      stage.assigned_hours = stage.total_hours;
    }
    applyRangeFromRows(task, task.rows);
    task.assigned_hours = task.total_hours;
  }

  const allRows = tasks.flatMap((task) => task.rows);
  const course = {};
  applyRangeFromRows(course, allRows);
  const term = inferTerm(course.start_date);
  return {
    calendar: {
      path: calendar.path,
      sha256: calendar.sha256,
      schema: calendar.schema,
      policy: 'skill_local_calendar',
      teaching_dates_count: calendar.dates.length,
      first_consumable_date: calendar.dates[0],
      last_consumable_date: calendar.dates[calendar.dates.length - 1],
    },
    first_teaching_day: firstTeachingDay,
    daily_hours: dailyHours,
    daily_hours_source: 'package_default',
    total_hours: allRows.reduce((sum, row) => sum + row.assigned_hours, 0),
    term_week_start: termWeekStart,
    consumed_calendar_range: {
      start_date: course.start_date,
      end_date: course.end_date,
      use_time: course.use_time,
    },
    course: {
      start_date: course.start_date,
      end_date: course.end_date,
      date_range: course.date_range,
      use_time: course.use_time,
      term_week: course.term_week,
      weekday: course.weekday,
      school_year: term.school_year,
      semester: term.semester,
      term_label: `${term.school_year}${term.semester}`,
    },
    tasks: tasks.map((task) => ({
      source: task.source,
      title: task.title,
      assigned_hours: task.assigned_hours,
      total_hours: task.total_hours,
      start_date: task.start_date,
      end_date: task.end_date,
      date_range: task.date_range,
      term_week: task.term_week,
      weekday: task.weekday,
      stage_totals: task.stages.map((stage) => ({
        source: stage.source,
        title: stage.title,
        assigned_hours: stage.assigned_hours,
        total_hours: stage.total_hours,
        start_date: stage.start_date,
        end_date: stage.end_date,
        date_range: stage.date_range,
        term_week: stage.term_week,
        weekday: stage.weekday,
      })),
    })),
    row_consumption_summary: rowSummaries,
  };
}

function buildModuleFrontmatter(metadata, scheduling) {
  const teacherName = metadata.teacher_name;
  return {
    'teaching-plan': {
      major_name: metadata.major_name,
      course_name: metadata.course_name,
      teacher_name: teacherName,
      class_name: metadata.class_name,
      first_teaching_day: metadata.first_teaching_day,
      daily_hours: scheduling.daily_hours,
      template: 'jiaoan-jihua',
    },
    'teaching-design': {
      template: 'jiaoan-shicao',
      course_name: metadata.course_name,
      course_attribute: metadata.course_attribute,
      textbook_name: metadata.textbook_name,
      class_name: metadata.class_name,
      total_hours: scheduling.total_hours,
      teacher_name: teacherName,
      use_time: scheduling.course.use_time,
    },
  };
}

function reviewMarkers(markdown) {
  const match = markdown.match(/^## 复核标记\n([\s\S]*?)(?:\n## |\n# |$)/m);
  if (!match) return [];
  return match[1].split(/\n/).map((line) => line.trim()).filter((line) => line && line !== '无' && !line.startsWith('<!--'));
}

function parseActivityHours(designText) {
  const values = [];
  for (const match of designText.matchAll(/(?:^|\n)\s*(?:活动课时|教学活动课时|lesson_activity_hours)\s*[:：]\s*([0-9]+(?:\.[0-9]+)?)\s*(?:H|h|课时)?\s*(?=\n|$)/g)) {
    values.push(Number(match[1]));
  }
  return values;
}

function normalizeTitle(value) {
  return String(value ?? '')
    .replace(/[\s　]/g, '')
    .replace(/[，,。；;：:（）()《》“”"'、]/g, '');
}

function displayTitleFromHeading(value) {
  return String(value ?? '').replace(/^学习任务[0-9一二三四五六七八九十]+[:：]/, '').replace(/（[0-9]+H）$/, '').trim();
}

function parseHourLabel(value) {
  const text = String(value ?? '').trim();
  if (!text) return null;
  const match = text.match(/^([0-9]+(?:\.[0-9]+)?)\s*(?:H|h|课时)?$/);
  return match ? Number(match[1]) : null;
}

function splitDesignBlocks(designText) {
  const tasks = [];
  let current = null;
  let currentPart = '';
  const pushTask = () => {
    if (current) tasks.push(current);
  };
  for (const rawLine of designText.split(/\n/)) {
    const line = rawLine.replace(/\r$/, '');
    if (line === '## 学习任务分析') {
      pushTask();
      current = { analysis_lines: [], activity_lines: [], evaluation_lines: [] };
      currentPart = 'analysis';
      continue;
    }
    if (!current) continue;
    if (line.startsWith('## 教学活动设计')) {
      current.activity_heading = line.slice(3).trim();
      currentPart = 'activity';
      continue;
    }
    if (line === '## 学业评价') {
      currentPart = 'evaluation';
      continue;
    }
    if (currentPart === 'analysis') current.analysis_lines.push(line);
    else if (currentPart === 'activity') current.activity_lines.push(line);
    else if (currentPart === 'evaluation') current.evaluation_lines.push(line);
  }
  pushTask();
  return tasks;
}

function parseTaskMeta(lines) {
  const meta = { title: '', raw_hours: null, raw_date_range: null };
  for (const line of lines) {
    if (line.startsWith('学习任务：')) meta.title = line.slice('学习任务：'.length).trim();
    else if (line.startsWith('课时：')) meta.raw_hours = line.slice('课时：'.length).trim();
    else if (line.startsWith('起止日期：')) meta.raw_date_range = line.slice('起止日期：'.length).trim();
  }
  return meta;
}

function analysisSectionKey(title) {
  if (title.startsWith('一、')) return 'description';
  if (title.startsWith('二、')) return 'goals';
  if (title.startsWith('三、')) return 'content';
  if (title.startsWith('四、')) return 'students';
  if (title.startsWith('五、')) return 'resources';
  return '';
}

function parseAnalysisSections(lines) {
  const sections = { description: '', goals: '', content: '', students: '', resources: '' };
  let key = '';
  for (const line of lines) {
    if (line.startsWith('### ')) {
      key = analysisSectionKey(line.slice(4).trim());
      continue;
    }
    if (!key) continue;
    if (!line.trim()) {
      if (sections[key]) sections[key] += '\n';
      continue;
    }
    sections[key] += (sections[key] && !sections[key].endsWith('\n') ? '\n' : '') + line;
  }
  for (const name of Object.keys(sections)) sections[name] = sections[name].trim();
  return sections;
}

function splitActivityBlocks(lines) {
  const stages = [];
  let currentStage = null;
  let currentActivity = null;
  let currentChapter = 1;
  const flushActivity = () => {
    if (!currentStage || !currentActivity) return;
    currentActivity.blocks = currentActivity.raw_body.join('\n').split(/\n\s*\n/).map((block) => block.trim()).filter(Boolean);
    currentActivity.learning_content = currentActivity.blocks[0] || '';
    currentActivity.student_activity = currentActivity.blocks[1] || '';
    currentActivity.teacher_activity = currentActivity.blocks[2] || '';
    currentActivity.method = currentActivity.blocks.slice(3).join('\n\n');
    currentActivity.content_title = (currentActivity.learning_content.split(/\n/).find((line) => line.trim()) || '').trim();
    currentActivity.validation_title = currentActivity.title.trim();
    currentStage.activities.push(currentActivity);
    currentActivity = null;
  };
  const flushStage = () => {
    flushActivity();
    if (currentStage) stages.push(currentStage);
    currentStage = null;
  };
  for (const rawLine of lines) {
    const line = rawLine.replace(/\r$/, '');
    if (line.trim() === '{pagebreak}') {
      flushActivity();
      currentChapter += 1;
      continue;
    }
    if (line.startsWith('### ')) {
      flushStage();
      const heading = line.slice(4).trim();
      const parts = heading.split('——');
      currentStage = {
        source: '',
        raw_heading: heading,
        title: (parts[0] || '').trim(),
        unit: (parts.slice(1).join('——') || '').trim(),
        chapter: currentChapter,
        activities: [],
      };
      continue;
    }
    if (line.startsWith('#### ')) {
      if (!currentStage) currentStage = { source: '', raw_heading: '', title: '', unit: '', chapter: currentChapter, activities: [] };
      flushActivity();
      currentActivity = { title: line.slice(5).trim(), raw_hours: null, chapter: currentChapter, raw_body: [] };
      continue;
    }
    if (line.startsWith('##### ') && currentActivity) {
      currentActivity.raw_hours = line.slice(6).trim();
      continue;
    }
    if (currentActivity) currentActivity.raw_body.push(line);
  }
  flushStage();
  return stages;
}

function parseEvaluation(lines) {
  const items = [];
  let summary = '';
  for (const line of lines) {
    const item = line.match(/^([0-9]+)[.]\s*(.+)$/);
    if (item) {
      const parts = item[2].split('；');
      items.push({ number: Number(item[1]), item: (parts[0] || '').trim(), detail: (parts[1] || '').trim(), method: (parts[2] || '').trim(), raw: item[2].trim() });
    } else if (line.startsWith('小结：')) {
      summary = line.slice('小结：'.length).trim();
    }
  }
  return { items, summary, markdown: lines.join('\n').trim() };
}

function crossModuleFail(code, message, scheduling, extra = {}) {
  fail(code, message, {
    code,
    mismatch_class: code,
    module_id: 'teaching-design',
    source_markdown: inputPath,
    calendar: scheduling.calendar,
    model_version: 'phase35.teaching-design-formal-renderer.v1',
    total_hours_source: 'teaching_plan_rows',
    ...extra,
  });
}

function compareTitleOrFail(code, message, scheduling, planTitle, designTitle, extra) {
  const planNormalized = normalizeTitle(planTitle);
  const designNormalized = normalizeTitle(designTitle);
  if (planNormalized !== designNormalized) {
    crossModuleFail(code, message, scheduling, {
      ...extra,
      plan_title: planTitle,
      design_title: designTitle,
      plan_normalized_title: planNormalized,
      design_normalized_title: designNormalized,
      expected: planTitle,
      actual: designTitle,
    });
  }
  return { planNormalized, designNormalized };
}

function buildTeachingDesignModel(designText, scheduleTasks, scheduling) {
  const rawTasks = splitDesignBlocks(designText);
  if (rawTasks.length !== scheduleTasks.length) {
    crossModuleFail('teaching_design_task_count_mismatch', `expected ${scheduleTasks.length} teaching-design tasks, found ${rawTasks.length}`, scheduling, {
      expected: scheduleTasks.length,
      actual: rawTasks.length,
    });
  }

  const designTasks = [];
  const stagesEvidence = [];
  const activitiesEvidence = [];
  for (let taskIndex = 0; taskIndex < scheduleTasks.length; taskIndex += 1) {
    const scheduleTask = scheduleTasks[taskIndex];
    const rawTask = rawTasks[taskIndex];
    const taskPointer = `task:${taskIndex + 1}`;
    if (!rawTask || !rawTask.analysis_lines.length) {
      crossModuleFail('missing_teaching_design_analysis_block', `missing analysis block at ${taskPointer}`, scheduling, { plan_pointer: taskPointer });
    }
    if (!rawTask.activity_lines.length) {
      crossModuleFail('missing_teaching_design_activity_block', `missing activity block at ${taskPointer}`, scheduling, { plan_pointer: taskPointer });
    }
    if (!rawTask.evaluation_lines.length) {
      crossModuleFail('missing_teaching_design_evaluation_block', `missing evaluation block at ${taskPointer}`, scheduling, { plan_pointer: taskPointer });
    }

    const meta = parseTaskMeta(rawTask.analysis_lines);
    const designTaskTitle = meta.title || displayTitleFromHeading(rawTask.activity_heading || '');
    const taskNorm = compareTitleOrFail('teaching_design_task_title_mismatch', `task title mismatch at ${taskPointer}`, scheduling, scheduleTask.title, designTaskTitle, {
      plan_pointer: taskPointer,
      design_pointer: taskPointer,
      plan_hours: scheduleTask.total_hours,
      plan_date_range: scheduleTask.date_range,
      design_date_range: meta.raw_date_range || null,
    });
    const taskHours = parseHourLabel(meta.raw_hours);
    if (taskHours !== null && taskHours !== scheduleTask.total_hours) {
      crossModuleFail('teaching_design_task_hours_mismatch', `task hours mismatch at ${taskPointer}`, scheduling, {
        plan_pointer: taskPointer,
        design_pointer: taskPointer,
        plan_title: scheduleTask.title,
        design_title: designTaskTitle,
        plan_hours: scheduleTask.total_hours,
        design_hours: taskHours,
        expected: scheduleTask.total_hours,
        actual: taskHours,
      });
    }
    if (meta.raw_date_range && meta.raw_date_range !== scheduleTask.date_range) {
      crossModuleFail('teaching_design_task_date_range_mismatch', `task date range mismatch at ${taskPointer}`, scheduling, {
        plan_pointer: taskPointer,
        design_pointer: taskPointer,
        plan_title: scheduleTask.title,
        design_title: designTaskTitle,
        plan_date_range: scheduleTask.date_range,
        design_date_range: meta.raw_date_range,
        expected: scheduleTask.date_range,
        actual: meta.raw_date_range,
      });
    }

    const designStages = splitActivityBlocks(rawTask.activity_lines);
    if (designStages.length !== scheduleTask.stages.length) {
      crossModuleFail('teaching_design_stage_count_mismatch', `stage count mismatch at ${taskPointer}`, scheduling, {
        plan_pointer: taskPointer,
        design_pointer: taskPointer,
        plan_title: scheduleTask.title,
        design_title: designTaskTitle,
        expected: scheduleTask.stages.length,
        actual: designStages.length,
      });
    }

    const mappedStages = [];
    for (let stageIndex = 0; stageIndex < scheduleTask.stages.length; stageIndex += 1) {
      const scheduleStage = scheduleTask.stages[stageIndex];
      const designStage = designStages[stageIndex];
      const stagePointer = `task:${taskIndex + 1}/stage:${stageIndex + 1}`;
      const stageNorm = compareTitleOrFail('teaching_design_stage_title_mismatch', `stage title mismatch at ${stagePointer}`, scheduling, scheduleStage.title, designStage.title, {
        plan_pointer: stagePointer,
        design_pointer: stagePointer,
        plan_title: scheduleStage.title,
        design_title: designStage.title,
        plan_hours: scheduleStage.total_hours,
      });
      if (designStage.activities.length !== scheduleStage.rows.length) {
        crossModuleFail('teaching_design_activity_count_mismatch', `activity count mismatch at ${stagePointer}`, scheduling, {
          plan_pointer: stagePointer,
          design_pointer: stagePointer,
          plan_title: scheduleStage.title,
          design_title: designStage.title,
          expected: scheduleStage.rows.length,
          actual: designStage.activities.length,
        });
      }

      const mappedActivities = [];
      for (let rowIndex = 0; rowIndex < scheduleStage.rows.length; rowIndex += 1) {
        const row = scheduleStage.rows[rowIndex];
        const activity = designStage.activities[rowIndex];
        const designPointer = `task:${taskIndex + 1}/stage:${stageIndex + 1}/activity:${rowIndex + 1}`;
        const activityNorm = compareTitleOrFail('teaching_design_activity_title_mismatch', `activity title mismatch at ${designPointer}`, scheduling, row.title, activity.validation_title, {
          plan_pointer: row.source,
          design_pointer: designPointer,
          plan_title: row.title,
          design_title: activity.validation_title,
          plan_hours: row.hours,
          design_hours: parseHourLabel(activity.raw_hours),
        });
        const activityHours = parseHourLabel(activity.raw_hours);
        if (activityHours !== null && activityHours !== row.hours) {
          crossModuleFail('teaching_design_activity_hours_mismatch', `activity hours mismatch at ${designPointer}`, scheduling, {
            plan_pointer: row.source,
            design_pointer: designPointer,
            plan_title: row.title,
            design_title: activity.validation_title,
            plan_hours: row.hours,
            design_hours: activityHours,
            expected: row.hours,
            actual: activityHours,
          });
        }

        const activityEvidence = {
          schedule_row_source: row.source,
          design_activity_source: designPointer,
          schedule_title: row.title,
          design_title: activity.validation_title,
          display_title: activity.title,
          schedule_normalized_title: activityNorm.planNormalized,
          design_normalized_title: activityNorm.designNormalized,
          schedule_hour: row.hours,
          design_hour: activityHours,
          expected_hour: row.hours,
          actual_hour: activityHours,
          derived_hours: row.hours,
          hour_source: 'schedule.tasks[].stages[].rows[].hours',
          schedule_date_range: row.date_range,
          design_date_range: null,
          expected_title: row.title,
          actual_title: activity.validation_title,
          validation: 'passed',
        };
        activitiesEvidence.push(activityEvidence);
        mappedActivities.push({
          ...activity,
          source: designPointer,
          schedule_row_source: row.source,
          schedule_title: row.title,
          normalized_title: activityNorm.designNormalized,
          schedule_normalized_title: activityNorm.planNormalized,
          derived_hours: row.hours,
          hour_label: `${row.hours}H`,
          date_range: row.date_range,
          expected: { title: row.title, hours: row.hours, date_range: row.date_range },
          actual: { title: activity.validation_title, hours: activityHours, date_range: null },
          validation: 'passed',
        });
      }

      const stageItem = {
        schedule_source: scheduleStage.source,
        design_source: stagePointer,
        title: scheduleStage.title,
        design_title: designStage.title,
        raw_title: designStage.title,
        normalized_title: stageNorm.designNormalized,
        schedule_normalized_title: stageNorm.planNormalized,
        row_count: scheduleStage.rows.length,
        activity_count: designStage.activities.length,
        derived_total_hours: scheduleStage.total_hours,
        chapter: designStage.chapter,
        unit: designStage.unit,
        activities: mappedActivities,
        validation: 'passed',
      };
      stagesEvidence.push(stageItem);
      mappedStages.push(stageItem);
    }

    const taskItem = {
      source: taskPointer,
      schedule_source: scheduleTask.source,
      title: scheduleTask.title,
      raw_title: designTaskTitle,
      normalized_title: taskNorm.designNormalized,
      schedule_normalized_title: taskNorm.planNormalized,
      task_total_hours: scheduleTask.total_hours,
      derived_total_hours: scheduleTask.total_hours,
      raw_hours: meta.raw_hours,
      date_range: scheduleTask.date_range,
      raw_date_range: meta.raw_date_range,
      analysis_block: { source: `${taskPointer}/analysis`, raw: rawTask.analysis_lines.join('\n').trim(), sections: parseAnalysisSections(rawTask.analysis_lines) },
      activity_block: { source: `${taskPointer}/activity`, heading: rawTask.activity_heading || '', stages: mappedStages },
      evaluation_block: { source: `${taskPointer}/evaluation`, ...parseEvaluation(rawTask.evaluation_lines) },
      validation: 'passed',
    };
    designTasks.push(taskItem);
  }

  return {
    markdown: designText,
    scheduling_source: 'shared_scheduling_model',
    tasks: designTasks,
    task_count: designTasks.length,
    analysis_blocks: rawTasks.filter((task) => task.analysis_lines.length).length,
    activity_blocks: rawTasks.filter((task) => task.activity_lines.length).length,
    evaluation_blocks: rawTasks.filter((task) => task.evaluation_lines.length).length,
    mapping: {
      total_hours_source: 'teaching_plan_rows',
      task_hours_source: 'schedule.tasks[].total_hours',
      activity_hours_source: 'schedule.tasks[].stages[].rows[].hours',
      date_range_source: 'shared_scheduling_model',
      mapping_key: 'learning_task + learning_stage + activity_order',
      title_normalization_role: 'diagnostic_equality_only_no_reordering',
    },
    evidence: {
      stages: stagesEvidence,
      activities: activitiesEvidence,
    },
  };
}

const markdown = fs.readFileSync(inputPath, 'utf8');
const { frontmatter } = splitFrontmatter(markdown);
const unified = parseFrontmatter(frontmatter);
const firstTeachingDay = unified.first_teaching_day;
isoDate(firstTeachingDay, 'first_teaching_day');
const planText = extractSection(markdown, '授课进度计划', '教学设计方案');
const designText = extractSection(markdown, '教学设计方案');
if (!designText.trim()) fail('missing_module_source', '教学设计方案 section has no module body', { module: 'teaching-design' });
const tasks = parsePlanRows(planText);
const calendar = loadCalendar(calendarPath);
const scheduling = assignSchedule(tasks, calendar, firstTeachingDay);
const metadata = {
  course_name: unified.course_name,
  major_name: unified.major_name,
  course_attribute: unified.course_attribute,
  textbook_name: unified.textbook_name,
  class_name: unified.class_name,
  teachers: unified.teachers,
  teacher_name: unified.teachers.join('、'),
  first_teaching_day: firstTeachingDay,
};
const publicDelivery = buildPublicDelivery(metadata);
const moduleFrontmatter = buildModuleFrontmatter(metadata, scheduling);
const totalHours = scheduling.total_hours;
const teachingDesign = buildTeachingDesignModel(designText, tasks, scheduling);
const declaredActivityHourValues = parseActivityHours(designText);
const activityHourValues = teachingDesign.evidence.activities.map((item) => item.derived_hours);
const activityHours = activityHourValues.reduce((sum, value) => sum + value, 0);
if (activityHours !== totalHours) {
  fail('teaching_design_hours_inconsistent', `teaching-plan total hours (${totalHours}) and teaching-design mapped activity hours (${activityHours}) mismatch`, {
    teaching_plan_total_hours: totalHours,
    teaching_design_activity_hours: activityHours,
  });
}

const strictSumEvidence = {
  total_hours_source: 'teaching_plan_rows',
  forbidden_sources: [
    'teaching_design_section',
    'yaml_total_hours',
    'yaml_daily_hours',
    'handwritten_dates',
    'renderer_local_calendar',
  ],
  rows: tasks.flatMap((task) => task.stages.flatMap((stage) => stage.rows.map((row) => ({
    source: row.source,
    task_source: task.source,
    stage_source: stage.source,
    task_title: task.title,
    stage_title: stage.title,
    raw_title: row.title,
    raw_hours: row.hours,
    assigned_hours: row.assigned_hours,
    start_date: row.start_date,
    end_date: row.end_date,
    term_week: row.term_week,
    weekday: row.weekday,
    hour_consumption: row.hour_consumption,
  })))),
  stages: tasks.flatMap((task) => task.stages.map((stage) => ({
    source: stage.source,
    task_source: task.source,
    title: stage.title,
    row_sources: stage.rows.map((row) => row.source),
    row_hours: stage.rows.map((row) => row.hours),
    total_hours: stage.total_hours,
    recompute_rule: 'sum(stage.rows[].hours)',
  }))),
  tasks: tasks.map((task) => ({
    source: task.source,
    title: task.title,
    row_sources: task.rows.map((row) => row.source),
    row_hours: task.rows.map((row) => row.hours),
    total_hours: task.total_hours,
    assigned_hours: task.assigned_hours,
    recompute_rule: 'sum(task.stages[].rows[].hours)',
  })),
  course: {
    row_sources: tasks.flatMap((task) => task.rows.map((row) => row.source)),
    row_hours: tasks.flatMap((task) => task.rows.map((row) => row.hours)),
    total_hours: totalHours,
    recompute_rule: 'sum(schedule.tasks[].stages[].rows[].hours)',
  },
  renderer_contract: {
    row_hour_cell: 'row.hours',
    task_total_cell: 'task.total_hours',
    scheduling_cells: 'row.hour_consumption from shared scheduling model',
  },
};

const model = {
  model_version: 'phase35.teaching-design-formal-renderer.v1',
  source_markdown: inputPath,
  metadata,
  modules: {
    registry: MODULE_REGISTRY,
    items: MODULE_REGISTRY.map((entry) => ({
      ...entry,
      public_pdf_filename: publicDelivery.module_pdfs.find((item) => item.module_id === entry.id).public_pdf_filename,
      frontmatter: moduleFrontmatter[entry.id],
      source_section: entry.id === 'teaching-plan' ? '# 授课进度计划' : '# 教学设计方案',
      scheduling_source: 'shared_scheduling_model',
    })),
  },
  public_delivery: publicDelivery,
  scheduling,
  derived: {
    total_hours: totalHours,
    total_hours_label: `${totalHours}H`,
    daily_hours: scheduling.daily_hours,
    calendar_policy: scheduling.calendar.policy,
    school_year: scheduling.course.school_year,
    semester: scheduling.course.semester,
    term_label: scheduling.course.term_label,
    start_date: scheduling.course.start_date,
    end_date: scheduling.course.end_date,
    date_range: scheduling.course.date_range,
    use_time: scheduling.course.use_time,
  },
  schedule: { tasks },
  teaching_design: {
    ...teachingDesign,
    activity_hours: {
      declared: declaredActivityHourValues.length > 0,
      declared_values: declaredActivityHourValues,
      values: activityHourValues,
      total_hours: activityHours,
      matches_teaching_plan: activityHours === totalHours,
      source: 'schedule.tasks[].stages[].rows[].hours',
    },
  },
  resources: {
    rows: [...designText.matchAll(/^### 五、学习资源\n([\s\S]*?)(?:\n## |\n### |$)/gm)].map((match) => match[1].trim()),
  },
  review_markers: reviewMarkers(markdown),
  validation: {
    final_ready: false,
    total_hours_source: 'teaching_plan_rows',
    teaching_design_activity_hours_source: 'schedule.tasks[].stages[].rows[].hours',
    hours_cross_check: 'passed',
    cross_module_evidence: {
      total_hours_source: 'teaching_plan_rows',
      task_hours_source: 'schedule.tasks[].total_hours',
      activity_hours_source: 'schedule.tasks[].stages[].rows[].hours',
      mapping_key: 'learning_task + learning_stage + activity_order',
      tasks: teachingDesign.tasks.map((task) => ({
        source: task.source,
        schedule_source: task.schedule_source,
        title: task.title,
        normalized_title: task.normalized_title,
        task_total_hours: task.task_total_hours,
        derived_total_hours: task.derived_total_hours,
        date_range: task.date_range,
        validation: task.validation,
      })),
      stages: teachingDesign.evidence.stages,
      activities: teachingDesign.evidence.activities,
    },
    calendar_policy: scheduling.calendar.policy,
    shared_scheduling_model: true,
    strict_sum_evidence: strictSumEvidence,
    errors: [],
  },
  output_readiness: {
    markdown_valid: true,
    typst_ready: true,
    pdf_ready: false,
    final_ready: false,
  },
};

console.log(JSON.stringify(model, null, 2));
